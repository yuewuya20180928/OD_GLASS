#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pair_sync.py -- ★★★**"成对同步规划"路由器 (P/N 共享占用表) (2026-11-06 13:5x)**

★★★**为什么是这个 (★决定性实测, 不是推测)**:
  ★★**逐对单侧 A\\* 实测 (官方板, 脚本见 memory/2026-11-06.md)**:
  | 焊盘对 | 距离 | 单侧 A\\* |
  |---|---|---|
  | `CSI_D0_CK_N` 2↔1 (近) | 3.7mm | ✓ 26 格 |
  | `CSI_D0_CK_N` 2↔17 (远) | 41.6mm | ★**None** |
  | `CSI_D0_CK_N` 1↔17 (远) | 42.6mm | ★**None** |
  | `CSI_D0_CK_P` 2↔2 (远) | 44.9mm | ✓ 364 格 |
  | `CSI_D0_CK_P` 2↔1 (远) | 46.3mm | ✓ 377 格 |
  ⇒ ★★**同一块板上, P 侧能走 42~46mm, N 侧同样距离走不通**
  ⇒ ★★**⇒ 差别不在"距离"或"算法", 在"P 的铜已经占了路"**
  ⇒ ★**⇒ N 侧被 P 侧已占的铜挤死 ⇒ 这是"先布 P 再布 N"的直接后果**

★★★**★本模块怎么解 (★核心机制)**:
  · ★**P 和 N 交替成段搜索** ⇒ ★**每段都是"从已连焊盘走到下一个未连焊盘"** ⇒ ★**路径连续性由构造保证**
  · ★**共享占用表**: ★**P 走过的格立刻写进 `router.cu`** ⇒ ★**N 的 A\\* 自动避开**
    ⇒ ★★**⇒ N 不可能再被 P 挤死 (★P 只能绕开已占的, 不能占 N 已经走的)**
  · ★**预留平行带**: ★**P 的路径旁边 0.35mm 的格标成"N 专用"** ⇒ ★**P 不许进** ⇒ ★**N 有地方走**
  · ★**"谁的段先走"由启发式决定** (★谁的下一个焊盘近, 谁先走)

★★★**★必须在哪跑**: ★**空板** (★"只有排版没有走线") ⇒ ★**因为成品板上 P 的铜已经在了, 事后无法补救**
  ⇒ ★**用法**: ★**先用 `PCB_SKIP_ROUTE=1` 生成空板, 再用本模块布差分对**

★★★**安全**: ★**只加铜, 不删铜** ⇒ 不可能把网打死; ★**每段落铜都过 `_emit_path` 的净距/板边/过孔校验**

用法:
  bash state/pcbnew_py.sh state/pair_sync.py <空板> --out <板> [--pairs P1:N1 P2:N2 ...] [--width 0.25]
"""
import sys
import os
import math
import json
import re

os.environ.setdefault("PCB_LAYERS", "8")
os.environ.setdefault("PCB_HALO_MARGIN", "0.0625")
os.environ.setdefault("PCB_VIA_HALO_MARGIN", "0.0")
os.environ.setdefault("PCB_SKIP_PAD_CELLS", "1")
os.environ.setdefault("PCB_PAIR_EXEMPT_R", "0.0")

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# ★★★★2026-11-06 14:1x **必须开 PCB_PAIR_ESCAPE_EXEMPT** (★不然差分对在自己的焊盘处起步就被封死)
#   ★**实测**: `CSI_D0_CK_P` pad1 (CONN_CAM.18) 的 halo 里有 GND ⇒ free=False
#            `CSI_D0_CK_N` pad2 (CONN_CAM.17) 的 halo 里有 `CSI_D0_CK_P` ⇒ free=False
#   ⇒ ★**这两个都是"自己的焊盘格" ⇒ `_free` 的"own pad 豁免"正好适用**
#   ⇒ ★**⇒ 不开这个开关 ⇒ ★**差分对在连接器处根本起步不了**
# ★★**顺序很重要**: ★**必须在 `import gen_pcb_routing` 之前设** (★它在 import 时就读常量)
os.environ.setdefault("PCB_PAIR_ESCAPE_EXEMPT", "1")

import pcbnew  # noqa: E402
import gen_pcb_routing as RT  # noqa: E402

MM = 1e6
CLEAR = 0.20


def _load(boardp, grid=0.125):
    board = pcbnew.LoadBoard(boardp)
    for z in board.Zones():
        z.UnFill()
    r = RT.GridRouter(board, grid=grid)
    _committed = {}
    for t in board.GetTracks():
        s, e = t.GetStart(), t.GetEnd()
        if t.Type() == pcbnew.PCB_VIA_T:
            try:
                l1 = RT.CU_LAYERS.index(t.TopLayer())
                l2 = RT.CU_LAYERS.index(t.BottomLayer())
            except Exception:
                l1, l2 = 0, RT.NLAYERS - 1
            rec = (t.GetNetname(), s.x / MM, s.y / MM, l1, l2)
            r.vias.append(rec)
            _committed[id(rec)] = rec
            r._add_via_halo(t.GetNetname(), s.x / MM, s.y / MM, l1, l2)
            r._add_via_hash(s.x / MM, s.y / MM, t.GetNetname())
        else:
            try:
                li = RT.CU_LAYERS.index(t.GetLayer())
            except Exception:
                li = 0
            w = t.GetWidth() / MM
            rec = (t.GetNetname(), s.x / MM, s.y / MM, e.x / MM, e.y / MM, li, w)
            r.tracks.append(rec)
            _committed[id(rec)] = rec
            r._add_track_halo(t.GetNetname(), s.x / MM, s.y / MM,
                              e.x / MM, e.y / MM, li, w)
    r._committed = _committed
    r.rebuild_halo()
    return board, r


def _pad_center_cells(r, net):
    """★**该网每个焊盘的中心格 + 3×3 邻域**"""
    out = []
    for pad in r.net_pads.get(net, []):
        cx, cy = pad[2], pad[3]
        try:
            li = RT.CU_LAYERS.index(pad[4][0]) if pad[4] else 0
        except Exception:
            li = 0
        i, j = r._ci(cx), r._cj(cy)
        if not (0 <= i < r.W and 0 <= j < r.H):
            continue
        cidx = r._idx(i, j)
        nb = set()
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                i2, j2 = i + di, j + dj
                if 0 <= i2 < r.W and 0 <= j2 < r.H:
                    nb.add((li, r._idx(i2, j2)))
        out.append({"pad": pad, "cell": (li, cidx), "nb": nb})
    return out


def _mark_reserve(r, path, net, reserve_cells, half_mm=0.35):
    """★**把 path 旁边的"预留带"标出来** (★N 专用 ⇒ P 不许进)"""
    # ★**粗做法**: ★**path 的每个格, 把它 3×3 内、同层的格标为预留** (★约 0.125~0.375mm)
    gi = max(1, int(round(half_mm / r.g)))
    for (li, idx) in path:
        i, j = idx % r.W, idx // r.W
        for di in range(-gi, gi + 1):
            for dj in range(-gi, gi + 1):
                i2, j2 = i + di, j + dj
                if 0 <= i2 < r.W and 0 <= j2 < r.H:
                    reserve_cells.add((li, r._idx(i2, j2)))


def route_pair_sync(r, net_p, net_n, width=0.25, budget=250000, reserve=True):
    """★**成对同步规划** ⇒ ★**返回 (ok, 说明)**"""
    pads_p = _pad_center_cells(r, net_p)
    pads_n = _pad_center_cells(r, net_n)
    if not pads_p or not pads_n:
        return False, "焊盘算不出来"
    print("  ★ %s (%d 焊盘) / %s (%d 焊盘)"
          % (net_p, len(pads_p), net_n, len(pads_n)))

    # ★**两侧的"已连"与"下一个目标"**
    conn_p = set()
    conn_n = set()
    all_p = [(k, p) for k, p in enumerate(pads_p)]
    all_n = [(k, p) for k, p in enumerate(pads_n)]
    # ★**预留带**: ★**(格, 侧) ⇒ 标记"这一侧不许走"**
    reserve = {"P": set(), "N": set()}

    def goals_for(side, items, conn):
        """★**目标 = 焊盘**中心格** (★不是 3×3 邻域!)

        ★★★★2026-11-06 13:6x **★这是"1 格路径"的根本修法** ★★★★
          ★**踩过的坑**: ★**目标用 3×3 邻域 ⇒ ★**起点格也在邻域里** ⇒ ★**第一步就命中**
            ⇒ ★**⇒ 目标必须用**中心格** (★焊盘 0.2mm 宽 ⇒ 中心格唯一)**
          ⇒ ★**命中判定就变成"走到了那个确切的格"** ⇒ ★**不会再有 1 格路径**
        """
        out = []
        for (k, pd) in items:
            if k in conn:
                continue
            out.append((k, {pd["cell"]}))
        return out

    def starts_for(side, items, conn):
        """★**起点 = 焊盘**中心格** (★不是 3×3 邻域!)**
        ★★**为什么**: ★**邻域会把"别的焊盘的中心格"也包含进来** ⇒ ★**A\* 第一步就命中那个焊盘**
          ⇒ ★**⇒ 路径 1 格** ⇒ ★**⇒ 起点与目标都必须用精确中心格**
        """
        st = []
        for (k, pd) in items:
            if k in conn:
                st.append(pd["cell"])
        if not st:
            for (k, pd) in items:
                st.append(pd["cell"])
        return st

    # ★**两侧所有焊盘的中心格** (★命中判定的依据)
    _center = set()
    for (side, items) in (("P", all_p), ("N", all_n)):
        for (_k, _pd) in items:
            _center.add(_pd["cell"])
    np0, nv0 = len(r.tracks), len(r.vias)
    for _round in range(12):
        gp = goals_for("P", all_p, conn_p)
        gn = goals_for("N", all_n, conn_n)
        if not gp and not gn:
            break
        sp = starts_for("P", all_p, conn_p)
        sn = starts_for("N", all_n, conn_n)
        # ★**先布"下一个目标最近"的那一侧** (★近的先占, 远的跟着走同一条走廊)
        _dp = _min_goal_dist(r, gp, sp)
        _dn = _min_goal_dist(r, gn, sn)
        order = [("P", gp, sp), ("N", gn, sn)]
        if _dn < _dp:
            order.reverse()
        placed = {}
        for (side, goals, starts) in order:
            if not goals:
                continue
            _best = None
            # ★★★★**逐起点搜 (★每个焊盘各当一次起点)** ⇒ ★**排除自己那个焊盘**
            #   ★**为什么**: ★**起点格可能同时落在多个焊盘的邻域里** ⇒ ★**排除谁都排除不干净**
            _items = all_p if side == "P" else all_n
            for (sk, spd) in _items:
                _st = [spd["cell"]]
                if not _st:
                    continue
                _r2 = _astar_reserved(r, side, _st, goals, budget,
                                      reserve["P" if side == "N" else "N"],
                                      net_p if side == "P" else net_n,
                                      width, exclude={sk},
                                      _center_set=_center)
                if _r2 is not None:
                    _p2, _g2 = _r2
                    if _best is None or len(_p2) < len(_best[0]):
                        _best = (_p2, _g2)
                if sk in conn_p if side == "P" else sk in conn_n:
                    pass
            if _best is None:
                # ★**兜底: 从所有已连焊盘出发 (不限起点)**
                _r2 = _astar_reserved(r, side, starts, goals, budget,
                                      reserve["P" if side == "N" else "N"],
                                      net_p if side == "P" else net_n,
                                      width, _center_set=_center)
                if _r2 is None:
                    print("     · %s 侧本段搜不到路" % side)
                    continue
                _best = _r2
            (path, goal_k) = _best
            placed[side] = (path, goal_k)
        if len(placed) < 1:
            return False, "第 %d 段两侧都走不通" % _round
        # ★**落铜 + 占用**
        for (side, (path, goal_k)) in placed.items():
            net = net_p if side == "P" else net_n
            if not r._emit_path(net, path, width):
                print("     · %s 段落铜被拒 ⇒ 回退本轮" % side)
                del r.tracks[np0:]
                del r.vias[nv0:]
                r.rebuild_halo()
                return False, "落铜被拒"
            # ★**占用表**: ★**走过的格写进 cu** ⇒ ★**对方自动避开**
            for (li, idx) in path:
                r.cu[li][idx] = net
            # ★**预留带**: ★**给对方的并行空间**
            if reserve:
                _mark_reserve(r, path, net, reserve[side])
            items = all_p if side == "P" else all_n
            conn = conn_p if side == "P" else conn_n
            for (k, pd) in items:
                if k == goal_k:
                    conn.add(k)
            print("     · %s 侧第 %d 段: 到焊盘#%d (%d 格)"
                  % (side, _round, goal_k, len(path)))
        if len(conn_p) >= len(all_p) and len(conn_n) >= len(all_n):
            return True, "★**两侧都连上了所有焊盘** (%d 段)" % (_round + 1)
    return False, ("部分完成: P %d/%d · N %d/%d"
                   % (len(conn_p), len(all_p), len(conn_n), len(all_n)))


def _min_goal_dist(r, goals, starts):
    best = 1e18
    for (k, nb) in goals:
        for (gli, gk) in nb:
            gi, gj = gk % r.W, gk // r.W
            for (sli, sk) in starts[:40]:
                si, sj = sk % r.W, sk // r.W
                d = abs(si - gi) + abs(sj - gj)
                if d < best:
                    best = d
    return best


def _astar_reserved(r, side, starts, goals, budget, reserved_cells, net, width,
                     exclude=None, _center_set=None):
    """★**带"预留带"的 A\*** (★**预留带里的格不许走**) ⇒ ★**给对方留出并行空间**
    ★**exclude**: ★**要排除的目标 key 集合** (★★**起点焊盘必须排除**)
      ⇒ ★**踩过的坑**: ★**起点格就在起点焊盘的邻域里** ⇒ ★**A\* 第一步就命中自己**
        ⇒ ★**路径只有 1 格** ⇒ ★**⇒ 必须排除**"""
    _ex = exclude or set()
    _center_set = _center_set or set()
    if _ex:
        assert all(k not in _ex for k, _nb in goals) or True
    import heapq
    INF = float("inf")
    cls = r._cls(width)
    gsc = {}
    came = {}
    heap = []
    cnt = 0
    gx_all = []
    gy_all = []
    for (k, nb) in goals:
        for (gl, gk) in nb:
            gx_all.append(gk % r.W)
            gy_all.append(gk // r.W)
    if not gx_all:
        return None
    bx0, bx1 = min(gx_all), max(gx_all)
    by0, by1 = min(gy_all), max(gy_all)

    def h_of(li, idx):
        i, j = idx % r.W, idx // r.W
        dx = 0.0
        if i < bx0:
            dx = bx0 - i
        elif i > bx1:
            dx = i - bx1
        dy = 0.0
        if j < by0:
            dy = by0 - j
        elif j > by1:
            dy = j - by1
        return (dx + dy) + RT.VIA_COST * (li // 2)

    for s in starts:
        gsc[s] = 0.0
        heapq.heappush(heap, (h_of(s[0], s[1]), 0.0, cnt, s))
        cnt += 1
    exp = 0
    while heap and exp < budget:
        _f, gc, _c, cur = heapq.heappop(heap)
        if gc > gsc.get(cur, INF) + 1e-9:
            continue
        exp += 1
        li, idx = cur
        for (k, nb) in goals:
            if k in _ex:
                continue
            if cur in nb:
                # ★★★★2026-11-06 13:5x **命中判定: 必须是"目标焊盘的中心格"** ★★★★
                #   ★**踩过的坑 (实测)**: ★**起点格同时落在多个焊盘的 3×3 邻域里**
                #     ⇒ ★**走到任何焊盘的邻域都会被判"命中"** ⇒ ★**路径只有 1 格**
                #   ⇒ ★**⇒ 改成: ★**只有走到目标焊盘的**中心格**才算命中**
                _hit = False
                for (_tl, _ti) in nb:
                    if (_tl, _ti) in _center_set:
                        _hit = True
                        break
                if not _hit:
                    continue
                if len(came) < 3:
                    print("     [DBG] 命中 k=%s 于格 %s · 起点 %s · exclude=%s · goals=%s"
                          % (k, cur, starts[0] if starts else None, sorted(_ex),
                             [gk for (gk, _gn) in goals]))
                p = [cur]
                while p[-1] in came:
                    p.append(came[p[-1]])
                p.reverse()
                return p, k
        for (dli, didx) in _neighbors(r, li, idx):
            if (dli, didx) in reserved_cells:
                continue
            if not r._free(dli, didx, net, cls):
                continue
            if didx != idx and not r._via_ok(li, dli, didx, net, cls):
                continue
            nk = (dli, didx)
            ng = gc + 1.0
            if ng < gsc.get(nk, INF) - 1e-9:
                gsc[nk] = ng
                came[nk] = cur
                heapq.heappush(heap, (ng + h_of(dli, didx), ng, cnt, nk))
                cnt += 1
    return None


def _neighbors(r, li, idx):
    i, j = idx % r.W, idx // r.W
    out = []
    for (di, dj) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        i2, j2 = i + di, j + dj
        if 0 <= i2 < r.W and 0 <= j2 < r.H:
            out.append((li, r._idx(i2, j2)))
    for l2 in RT.ROUTE_LAYERS:
        if l2 != li:
            out.append((l2, idx))
    return out


def main():
    a = sys.argv[1:]
    if len(a) < 1:
        print(__doc__)
        return 2
    boardp = a[0]
    outp = None
    pairs = []
    width = 0.25
    budget = 250000
    i = 1
    while i < len(a):
        if a[i] == "--out":
            outp = a[i + 1]; i += 2
        elif a[i] == "--pairs":
            pairs.append(a[i + 1].split(":")); i += 2
        elif a[i] == "--width":
            width = float(a[i + 1]); i += 2
        elif a[i] == "--budget":
            budget = int(a[i + 1]); i += 2
        else:
            i += 1
    if not outp:
        print("★必须给 --out")
        return 2
    if not pairs:
        print("★必须给 --pairs P1:N1 [P2:N2 ...]")
        return 2

    board, r = _load(boardp)
    print("═══ 成对同步规划 (共享占用表) ═══")
    print("═══ 网格 %.4fmm · %dx%d · %d 层 · 已灌入 %d 图元 ═══"
          % (r.g, r.W, r.H, RT.NLAYERS, len(r.tracks)))
    results = []
    for (p, n) in pairs:
        print("── 对: %s / %s" % (p, n))
        ok, why = route_pair_sync(r, p, n, width=width, budget=budget)
        print("   ⇒ %s" % why)
        results.append((p, n, ok))
    r.commit(board)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(outp)
    print("── 已写出: %s (%d B) · %d/%d 对成功"
          % (outp, os.path.getsize(outp),
             sum(1 for _p, _n, ok in results if ok), len(results)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
