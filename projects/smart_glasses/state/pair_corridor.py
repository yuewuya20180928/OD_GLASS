#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pair_corridor.py -- ★★★**"逐段成对扩展" (P/N 同步规划一条走廊) (2026-11-06 13:3x)**

★★★**为什么是这个形态 (★前三版的实测教训, 一版比一版接近真相)**:
  ① 第一版 (状态 = (格, 侧), 一次性同步生长):
     ★**坑**: ★**"到达目标"的判定错了** ⇒ 起点格 = 焊盘中心格 ⇒ 扩展 1 次就判"到达" ⇒ 路径 1 格
  ② 第二版 (改用 3×3 邻域命中):
     ★**坑**: ★**起点到"自己的焊盘"也在邻域内** ⇒ 第一个状态就把所有焊盘标成已连 ⇒ 扩展 7 次误判"全连"
  ③ 第三版 (精确中心格命中):
     ★**命中判定对了** (实测 P 命中 4 个 / N 命中 3 个) ⇒ ★**但扩展只有 7 次**
     ★**真正的缺陷**: ★**状态里没有"这是哪条路径"的信息**
     ⇒ ★**"命中某个焊盘"不构成"从另一个焊盘连续走到它"** ⇒ ★**A\* 可以在任意格之间跳**
  ④ ★★**本版 (逐段成对扩展)**: ★**每次 P 和 N 各走一段**
     · ★**每段的起点 = 上一个已连的焊盘 (或任意已连铜的格)** ⇒ ★**路径连续性由构造保证**
     · ★**每段的终点 = 下一个"还没连上"的焊盘** ⇒ ★**必须真正走到才算连上**
     · ★**两段必须都成功才前进** ⇒ ★**失败就回退这一段** ⇒ ★**不会留下半截铜**
     ⇒ ★★**⇒ 这才是差分对该有的样子: 两条线在同一走廊里, 一段一段同步长**

★★★**★为什么这条路的收益可期 (★实测依据)**:
  · 官方板 `CSI_D0_CK_N` 的铜局限 x41.95..47.70 ⇒ ★**第 3 个焊盘 (远 39.47mm) 走不出去**
  · ★**而 P 侧同目标布到了 x=86.2** ⇒ ★**差别只在"谁先占走廊"**
  · ★**本版让 P 和 N 同时规划 ⇒ ★**N 的走法会直接影响 P 的走法 ⇒ ★**不会先把走廊占死**

★★★**安全**: ★**只加铜, 不删铜** ⇒ 不可能把网打死; ★**每段都验净距/板边/过孔** ⇒ 落铜安全

用法:
  bash state/pcbnew_py.sh state/pair_corridor.py <板> <DRC.json> --out <新板> [--pair P N]
"""
import sys
import os
import math
import json
import re
import heapq

os.environ.setdefault("PCB_LAYERS", "8")
os.environ.setdefault("PCB_HALO_MARGIN", "0.0625")
os.environ.setdefault("PCB_VIA_HALO_MARGIN", "0.0")
os.environ.setdefault("PCB_SKIP_PAD_CELLS", "1")
os.environ.setdefault("PCB_PAIR_EXEMPT_R", "0.0")

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pcbnew  # noqa: E402
import gen_pcb_routing as RT  # noqa: E402

MM = 1e6
CLEAR = 0.20
INF = float("inf")
VIA_COST = 30.0


def pt_seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 < 1e-12:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


class SegRouter(object):
    """★**单侧的一小段路由** (★从一个起点搜到一组候选目标焊盘)"""

    def __init__(self, router, net, width=0.25, budget=120000):
        self.r = router
        self.net = net
        self.width = width
        self.budget = budget
        self.cls = router._cls(width)

    def pad_cells(self):
        """★**该网每个焊盘的"中心格"** (★精确, 不用邻域)"""
        out = []
        for pad in self.r.net_pads.get(self.net, []):
            cx, cy = pad[2], pad[3]
            try:
                li = RT.CU_LAYERS.index(pad[4][0]) if pad[4] else 0
            except Exception:
                li = 0
            i, j = self.r._ci(cx), self.r._cj(cy)
            if 0 <= i < self.r.W and 0 <= j < self.r.H:
                out.append((li, self.r._idx(i, j), pad))
        return out

    def pad_neighborhood(self, li, idx):
        """★**焊盘的 3×3 邻域** (★当"到达"的判定区: 走到中心格或邻域都算连上)"""
        i, j = idx % self.r.W, idx // self.r.W
        out = set()
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                i2, j2 = i + di, j + dj
                if 0 <= i2 < self.r.W and 0 <= j2 < self.r.H:
                    out.add((li, self.r._idx(i2, j2)))
        return out

    def astar_to(self, starts, goal_sets, avoid_paths=None, exclude=None):
        """★**从一个起点搜到"某个目标邻域"**

        goal_sets: [(名字, set(格))] —— 命中任一即可
        avoid_paths: [ [(li,idx), ...] ] —— ★**对方已走的路径** ⇒ ★**用来做"并行奖励"**
        exclude: set(名字) —— ★**要排除的目标** (★★**起点自己那个焊盘必须排除**)
        ★★**踩过的坑 (实测)**: ★**起点格就在起点焊盘的 3×3 邻域里** ⇒ ★**A\* 第一步就命中**
          ⇒ ★**路径只有 1 格** ⇒ ★**⇒ 必须排除起点焊盘**
        """
        _ex = exclude or set()
        r = self.r
        INF_ = INF
        gsc = {}
        came = {}
        heap = []
        cnt = 0
        # ★**启发式: 到最近目标集合的平面距离 + 层差**
        gx_all = []
        gy_all = []
        for _nm, gs in goal_sets:
            for (gl, gk) in gs:
                gx_all.append(gk % r.W)
                gy_all.append(gk // r.W)
        if not gx_all:
            return None, None, "目标集合空"
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
            return (dx + dy) + VIA_COST * (abs(li) // 2)

        for s in starts:
            gsc[s] = 0.0
            heapq.heappush(heap, (h_of(s[0], s[1]), 0.0, cnt, s))
            cnt += 1
        exp = 0
        while heap and exp < self.budget:
            _f, gc, _c, cur = heapq.heappop(heap)
            if gc > gsc.get(cur, INF_) + 1e-9:
                continue
            exp += 1
            li, idx = cur
            for (nm, gs) in goal_sets:
                if nm in _ex:
                    continue
                if cur in gs:
                    path = self._trace(came, cur)
                    return path, nm, "★**命中 %s** (扩展 %d)" % (nm, exp)
            for (dli, didx) in self._neighbors(li, idx):
                if not r._free(dli, didx, self.net, self.cls):
                    continue
                if didx != idx and not r._via_ok(li, dli, didx, self.net, self.cls):
                    continue
                _d = 0.0
                if avoid_paths:
                    _pd = self._peer_dist(dli, didx, avoid_paths)
                    if _pd is not None:
                        _d += max(0.0, _pd - 0.45) * 0.30
                nk = (dli, didx)
                ng = gc + 1.0 + _d
                if ng < gsc.get(nk, INF_) - 1e-9:
                    gsc[nk] = ng
                    came[nk] = cur
                    heapq.heappush(heap, (ng + h_of(dli, didx), ng, cnt, nk))
                    cnt += 1
        return None, None, "预算耗尽 (扩展 %d)" % exp

    def _peer_dist(self, li, idx, avoid_paths):
        cx, cy = self.r._cx(idx % self.r.W), self.r._cy(idx // self.r.W)
        best = INF
        for path in avoid_paths:
            for (pl, pk) in path[-120:]:
                px, py = self.r._cx(pk % self.r.W), self.r._cy(pk // self.r.W)
                d = math.hypot(cx - px, cy - py)
                if d < best:
                    best = d
        return None if best == INF else best

    def _neighbors(self, li, idx):
        r = self.r
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

    def _trace(self, came, end):
        p = [end]
        while p[-1] in came:
            p.append(came[p[-1]])
        p.reverse()
        return p


class PairPlanner(object):
    """★**逐段成对扩展**: ★**P 和 N 轮流走一段, 两段都成才前进**"""

    def __init__(self, router, net_p, net_n, width=0.25, budget=120000):
        self.r = router
        self.sp = SegRouter(router, net_p, width, budget)
        self.sn = SegRouter(router, net_n, width, budget)
        self.net_p = net_p
        self.net_n = net_n
        self.width = width

    def run(self):
        r = self.r
        pads_p = self.sp.pad_cells()
        pads_n = self.sn.pad_cells()
        if not pads_p or not pads_n:
            return None, None, "焊盘算不出来"
        # ★**目标邻域 (每个焊盘一个)**
        nb_p = [(("P_pad%d" % k), self.sp.pad_neighborhood(pl, pk))
                for k, (pl, pk, _pd) in enumerate(pads_p)]
        nb_n = [(("N_pad%d" % k), self.sn.pad_neighborhood(pl, pk))
                for k, (pl, pk, _pd) in enumerate(pads_n)]
        # ★**起点 = 每个焊盘的 3×3 (★从任一焊盘都能出发)**
        st_p = []
        for (pl, pk, _pd) in pads_p:
            st_p.extend(sorted(self.sp.pad_neighborhood(pl, pk)))
        st_n = []
        for (pl, pk, _pd) in pads_n:
            st_n.extend(sorted(self.sn.pad_neighborhood(pl, pk)))
        # ★★★**已连集合: ★**初始为空** (★第一段就是"从一个焊盘走到另一个焊盘") ★★★
        #   ★**踩过的坑 (实测)**: ★**初始把"所有焊盘"都算已连** ⇒ ★**目标集合永远为空**
        #     ⇒ ★**第一段就"完成"** ⇒ ★**结果 "P 1/4 · N 1/3"** ⇒ ★**啥也没布**
        conn_p = set()
        conn_n = set()
        path_p = []
        path_n = []
        hit_p = set()
        hit_n = set()
        print("  P 焊盘 %d 个 · N 焊盘 %d 个" % (len(pads_p), len(pads_n)))
        # ★**起点焊盘名** (★第一段: 从任意焊盘出发 ⇒ 不知道起点是哪个 ⇒ ★**用"命中的目标"反推**)
        #   ⇒ ★**做法**: ★**每次 A\* 返回后, ★**把"命中的目标"作为下一次的起点**
        #   ⇒ ★**第一段的起点 = 任意焊盘 ⇒ ★**但要排除所有可能的起点焊盘? 不 ⇒ ★**只排除"上一个命中的"**
        start_pad_p = None
        start_pad_n = None
        for _round in range(8):
            # ★**P 侧走一段**
            goals_p = []
            for k, (pl, pk, _pd) in enumerate(pads_p):
                if pl in conn_p:
                    continue
                goals_p.append((("P_pad%d" % k), self.sp.pad_neighborhood(pl, pk)))
            if not goals_p:
                break
            # ★★**排除起点焊盘** (★起点格就在它的邻域里 ⇒ 不排除就 1 格命中)
            _ex_p = set()
            if start_pad_p is not None:
                _ex_p.add(start_pad_p)
            # ★★★★**第一段: ★**从每个焊盘分别出发搜一次** (★**否则起点格会同时落在
            #   多个焊盘的邻域里 ⇒ ★**排除谁都排除不干净** ⇒ ★**路径只有 1 格**)
            ppath = None
            pname = None
            why = ""
            _cands = []
            if start_pad_p is None:
                # ★**第一段: 每个焊盘各当一次起点**
                for k0, (pl0, pk0, _pd0) in enumerate(pads_p):
                    _st = sorted(self.sp.pad_neighborhood(pl0, pk0))
                    _pp, _pn, _ww = self.sp.astar_to(_st, goals_p,
                                                     avoid_paths=[path_n],
                                                     exclude={"P_pad%d" % k0})
                    if _pp is not None:
                        _cands.append((len(_pp), _pp, _pn, _ww))
                if _cands:
                    _cands.sort(key=lambda t: t[0])
                    _l, ppath, pname, why = _cands[0]
                    print("     · 第一段 P: 从 %s 出发 (%d 格, 共 %d 个可行起点)"
                          % (pname, _l, len(_cands)))
            if ppath is None:
                ppath, pname, why = self.sp.astar_to(st_p, goals_p, avoid_paths=[path_n],
                                                    exclude=_ex_p)
            if ppath is None:
                return None, None, "P 侧第 %d 段失败: %s" % (_round, why)
            # ★**P 命中了哪个焊盘?**
            for k, (pl, pk, _pd) in enumerate(pads_p):
                if ("P_pad%d" % k) == pname:
                    conn_p.add(pl)
                    hit_p.add((pl, pk))
                    start_pad_p = pname
                    break
            # ★**N 侧走一段 (★用 P 刚走的路径当"并行引导")**
            goals_n = []
            for k, (pl, pk, _pd) in enumerate(pads_n):
                if pl in conn_n:
                    continue
                goals_n.append((("N_pad%d" % k), self.sn.pad_neighborhood(pl, pk)))
            if not goals_n:
                break
            _ex_n = set()
            if start_pad_n is not None:
                _ex_n.add(start_pad_n)
            # ★★**N 侧同理** (★第一段从每个焊盘各搜一次)
            npath = None
            nname = None
            why2 = ""
            _cands2 = []
            if start_pad_n is None:
                for k0, (pl0, pk0, _pd0) in enumerate(pads_n):
                    _st = sorted(self.sn.pad_neighborhood(pl0, pk0))
                    _pp, _pn, _ww = self.sn.astar_to(_st, goals_n,
                                                     avoid_paths=[path_p],
                                                     exclude={"N_pad%d" % k0})
                    if _pp is not None:
                        _cands2.append((len(_pp), _pp, _pn, _ww))
                if _cands2:
                    _cands2.sort(key=lambda t: t[0])
                    _l, npath, nname, why2 = _cands2[0]
                    print("     · 第一段 N: 从 %s 出发 (%d 格, 共 %d 个可行起点)"
                          % (nname, _l, len(_cands2)))
            if npath is None:
                npath, nname, why2 = self.sn.astar_to(st_n, goals_n, avoid_paths=[path_p],
                                                      exclude=_ex_n)
            if npath is None:
                return None, None, "N 侧第 %d 段失败: %s" % (_round, why2)
            for k, (pl, pk, _pd) in enumerate(pads_n):
                if ("N_pad%d" % k) == nname:
                    conn_n.add(pl)
                    hit_n.add((pl, pk))
                    start_pad_n = nname
                    break
            path_p.append(ppath)
            path_n.append(npath)
            print("  第 %d 段: P %s (%d 格) · N %s (%d 格)"
                  % (_round, pname, len(ppath), nname, len(npath)))
            # ★**下一段的起点 = 刚走到的焊盘附近**
            st_p = []
            for (pl, pk) in hit_p:
                st_p.extend(sorted(self.sp.pad_neighborhood(pl, pk)))
            st_n = []
            for (pl, pk) in hit_n:
                st_n.extend(sorted(self.sn.pad_neighborhood(pl, pk)))
            if len(conn_p) >= len(pads_p) and len(conn_n) >= len(pads_n):
                return path_p, path_n, "★**两侧都连上了所有焊盘** (%d 段)" % (_round + 1)
        return (path_p, path_n,
                "★**部分完成**: P %d/%d · N %d/%d"
                % (len(conn_p), len(pads_p), len(conn_n), len(pads_n)))


def _load_board(boardp):
    board = pcbnew.LoadBoard(boardp)
    for z in board.Zones():
        z.UnFill()
    r = RT.GridRouter(board, grid=0.125)
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


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        return 2
    boardp, drcp = a[0], a[1]
    outp = None
    net_p = net_n = None
    width = 0.25
    budget = 120000
    i = 2
    while i < len(a):
        if a[i] == "--out":
            outp = a[i + 1]; i += 2
        elif a[i] == "--pair":
            net_p = a[i + 1]; net_n = a[i + 2]; i += 3
        elif a[i] == "--width":
            width = float(a[i + 1]); i += 2
        elif a[i] == "--budget":
            budget = int(a[i + 1]); i += 2
        else:
            i += 1
    if not outp:
        print("★必须给 --out")
        return 2
    if not net_p or not net_n:
        d = json.load(open(drcp, encoding="utf-8"))
        nets = set()
        for it in (d.get("unconnected_items") or []):
            for s in (it.get("items") or []):
                m = re.search(r"\[([^\]]+)\]", str(s.get("description") or ""))
                if m:
                    nets.add(m.group(1))
        cands = [n for n in sorted(nets) if n.endswith("_P") and (n[:-2] + "_N") in nets]
        if not cands:
            print("★没找到候选差分对")
            return 2
        net_p, net_n = cands[0], cands[0][:-2] + "_N"
        print("★自动选差分对: %s / %s" % (net_p, net_n))

    board, r = _load_board(boardp)
    print("═══ 逐段成对扩展: %s / %s ═══" % (net_p, net_n))
    print("═══ 网格 %.4fmm · %dx%d · %d 层 ═══" % (r.g, r.W, r.H, RT.NLAYERS))
    print("═══ 已灌入 %d 图元 ═══" % len(r.tracks))

    pl = PairPlanner(r, net_p, net_n, width=width, budget=budget)
    ppaths, npaths, why = pl.run()
    print("── 结果: %s" % why)
    if not ppaths or not npaths:
        board.Save(outp)
        print("── 没找到成对路径 ⇒ 不落铜")
        return 1

    # ★**落铜: ★**逐段落, ★**每段都验净距; 失败就停并回退前面的**
    np0, nv0 = len(r.tracks), len(r.vias)
    ok = True
    for k, pp in enumerate(ppaths):
        if not r._emit_path(net_p, pp, width):
            print("── P 第 %d 段落铜被拒 ⇒ 全部回退" % k)
            ok = False
            break
    if ok:
        for k, nn in enumerate(npaths):
            if not r._emit_path(net_n, nn, width):
                print("── N 第 %d 段落铜被拒 ⇒ 全部回退" % k)
                ok = False
                break
    if not ok:
        del r.tracks[np0:]
        del r.vias[nv0:]
        r.rebuild_halo()
        board.Save(outp)
        print("── 已回退 ⇒ 不落铜")
        return 1
    print("── 落铜成功: P %d 段 / N %d 段" % (len(ppaths), len(npaths)))
    r.commit(board)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(outp)
    print("── 已写出: %s (%d B)" % (outp, os.path.getsize(outp)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
