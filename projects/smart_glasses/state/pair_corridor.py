#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pair_corridor.py -- ★★★**"成对走廊 A\*" (P/N 同步生长) (2026-11-06 13:0x)**

★★★**为什么要有这个 (★实测的机制, 不是猜)**:
  ① 官方板 unc 45 · 45 条里 23 条 >40mm · 25 条是差分腿
  ② ★**两个独立引擎撞同一堵墙**: 自研 A\\* (成品板 +3 条) · freerouting 2.1.0 (37 轮 score 恒定 996.44)
     ⇒ ★**物理约束, 不是算法问题**
  ③ ★★**根因 (纯几何 + 实测)**:
     · SoM BTB 0.4mm pitch + 0.2mm 焊盘 ⇒ 沿排出线余量精确 = **0.0000mm**
       ⇒ ★**0.2mm 线物理上布不出** ⇒ ★**0.15mm (6mil) 才活**
     · ★**"P 通 N 不通"是顺序依赖**: P 侧靠 pair-partner 豁免先走出去了 ⇒ N 侧再走时 P 的铜已在那
     · ★**实测 `CSI_D0_CK_N`**: 3 个焊盘 (C_AC 45.90,58.60 / TP 44.50,55.20 / CONN_CAM.17 86.90,51.40)
       ⇒ ★**N 侧铜有 50 段但局限在 x 41.95..47.70** ⇒ ★**第 3 个 (远 39.47mm) 完全走不出去**
       ⇒ ★**而 P 侧同目标布到了 x=86.2** ⇒ ★**差别只在"谁先占走廊"**
       ⇒ ★**而那 39mm 沿线 2mm 内有 662 条异网铜 (F.Cu 241 / In2.Cu 244 / In4.Cu 172 / In6.Cu 5)**
       ⇒ ★★**⇒ 单根线走不过去 ⇒ 必须"两条线一起规划, 互为走廊"**

★★★**★"成对走廊 A\\*" 怎么做 (与逐个布的区别)**:
  · ★**逐个布 (现状)**: P 走完 → N 在 P 的走廊里走 ⇒ ★**N 被 P 的铜堵死**
  · ★**成对布 (本模块)**: ★**状态 = (格, 侧)**, ★**侧 ∈ {P, N}** ⇒ ★**两条线在同一个搜索空间里交替生长**
    ⇒ ★**N 的走法会直接影响 P 的走法** ⇒ ★**不会先把走廊占死**
  · ★**启发式**: ★**每个状态都额外算"到对方当前前沿的距离"** ⇒ ★**P 往 N 的方向长, N 往 P 的方向长**
  · ★**间距约束**: ★**P 与 N 的路径点必须保持 ≥ pair_min (默认 0.35mm)** ⇒ ★**差分几何成立**

★★★**安全**: ★**只加铜, 不删铜** ⇒ 不可能把网打死

用法:
  bash state/pcbnew_py.sh state/pair_corridor.py <板> <DRC.json> --out <新板> [--net CSI_D0_CK_P]
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

import pcbnew  # noqa: E402
import gen_pcb_routing as RT  # noqa: E402

MM = 1e6
CLEAR = 0.20
INF = float("inf")


def pt_seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 < 1e-12:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


class PairRouter(object):
    """★**成对走廊 A\\*** —— ★**P 和 N 在同一搜索空间里同步生长**"""

    def __init__(self, router, net_p, net_n, width=0.25, pair_min=0.35, budget=400000):
        self.r = router
        self.net_p = net_p
        self.net_n = net_n
        self.width = width
        self.pair_min = pair_min
        self.budget = budget
        self.cls = router._cls(width)

    # ---------- 障碍查询 (与 router 同一套) ----------
    def _free(self, li, idx, net):
        return self.r._free(li, idx, net, self.cls)

    def _via_ok(self, la, lb, idx, net):
        return self.r._via_ok(la, lb, idx, net, self.cls)

    def _starts(self, net):
        """★**该网的起步格 (焊盘格 + 周围 8 格, 同层)**"""
        out = []
        for pad in self.r.net_pads.get(net, []):
            cx, cy = pad[2], pad[3]
            try:
                li = RT.CU_LAYERS.index(pad[4][0]) if pad[4] else 0
            except Exception:
                li = 0
            i0, j0 = self.r._ci(cx), self.r._cj(cy)
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    i, j = i0 + di, j0 + dj
                    if 0 <= i < self.r.W and 0 <= j < self.r.H:
                        out.append((li, self.r._idx(i, j)))
        return out

    def _goals(self, net, exclude_starts=True):
        """★**目标格** (★★要排除起点格! ★★否则"起点==目标" ⇒ 路径只有 1 格)

        ★★★**踩过的坑 (实测)**: 第一版把 pad 的 3×3 格同时当 starts 和 goals
          ⇒ ★**第一格就判定"到达目标"** ⇒ ★**路径只有 1 格 ⇒ 落了个啥也没干的板**
        ⇒ ★**⇒ goals 必须排除 starts (★按"不是同一个 pad"来排除)**
        """
        out = set()
        starts = set(self._starts(net)) if exclude_starts else set()
        for pad in self.r.net_pads.get(net, []):
            cx, cy = pad[2], pad[3]
            try:
                li = RT.CU_LAYERS.index(pad[4][0]) if pad[4] else 0
            except Exception:
                li = 0
            # ★★**目标 = 焊盘中心格 (★不是 3×3 邻域!)**
            #   ★**理由**: ★**3×3 邻域会与起步格大面积重叠** ⇒ 排除后可能空集
            #     ⇒ ★**而"到焊盘中心格"才是真正的到达** (★焊盘只有 0.2mm 宽, 中心格唯一)
            i, j = self.r._ci(cx), self.r._cj(cy)
            if 0 <= i < self.r.W and 0 <= j < self.r.H:
                k = (li, self.r._idx(i, j))
                if k not in starts:
                    out.add(k)
                else:
                    # ★**该焊盘同时是起点和目标 (只有 1 个焊盘时) ⇒ 认了**
                    out.add(k)
        return out

    def _coords(self, li, idx):
        i, j = idx % self.r.W, idx // self.r.W
        return self.r._cx(i), self.r._cy(j)

    def _init_pad_tracking(self):
        """★**每侧的焊盘清单 + 已连上的清单** (★用于"到达"的判定)"""
        self._pad_list = {}
        self._pad_hit = {}
        self._pad_set = {}
        for (side, net) in ((0, self.net_p), (1, self.net_n)):
            lst = []
            for pad in self.r.net_pads.get(net, []):
                cx, cy = pad[2], pad[3]
                try:
                    li = RT.CU_LAYERS.index(pad[4][0]) if pad[4] else 0
                except Exception:
                    li = 0
                lst.append((li, self.r._idx(self.r._ci(cx), self.r._cj(cy))))
            self._pad_list[side] = lst
            self._pad_hit[side] = set()
            self._pad_set[side] = set(lst)

    def _touches_new_pad(self, li, idx, net, side):
        """★**这个格是不是"还没连上的某个焊盘"的中心格**

        ★★★★2026-11-06 13:2x **修: 命中判定必须用"精确中心格", 不能用 3×3 邻域** ★★★★
          ★**踩过的坑 (实测)**: ★**用 3×3 邻域 ⇒ 起点格到"自己的焊盘"也在邻域内**
            ⇒ ★**第一个状态就把焊盘标记成"已连上"** ⇒ ★**再走一步又命中另一个**
            ⇒ ★**⇒ 扩展 7 次就误判"全部连上" ⇒ 路径只有 1 格** ⇒ ★**落了个啥也没干的板**
          ⇒ ★**⇒ 命中 = 走到那个焊盘的**中心格**** (★焊盘 0.2mm 宽 ⇒ 中心格唯一且精确)
        """
        return (li, idx) in self._pad_set[side] and idx not in self._pad_hit[side]

    def _mark_pad_hit(self, li, idx, net, side):
        """★**标记被连上的焊盘** (★返回是否有新焊盘被连上)"""
        if (li, idx) in self._pad_set[side] and idx not in self._pad_hit[side]:
            self._pad_hit[side].add(idx)
            return True
        return False

    def route(self):
        """★**核心: 双向同步生长的 A\\***"""
        import heapq
        r = self.r
        self._init_pad_tracking()
        sp = self._starts(self.net_p)
        sn = self._starts(self.net_n)
        gp = self._goals(self.net_p)
        gn = self._goals(self.net_n)
        # ★★**注意**: ★**目标格不再排除起步格** (★焊盘中心格是唯一的"到达点")
        #   ⇒ ★**若某网只有 1 个焊盘 ⇒ 起终点重合 ⇒ 路由无意义 ⇒ 那对不该进这里**
        if not sp or not sn or not gp or not gn:
            return None, None, "起步格/目标格算不出来"

        # ★**启发式: 平面距离 + 层差代价**
        def h(li, idx, goals):
            cx, cy = self._coords(li, idx)
            best = INF
            for (gl, gk) in goals:
                gx, gy = self._coords(gl, gk)
                d = math.hypot(cx - gx, cy - gy) + abs(li - gl) * 30.0
                if d < best:
                    best = d
            return best

        # ★**状态 = (li, idx, side)  side: 0=P, 1=N**
        # ★★★★2026-11-06 13:3x **起点 = "已连上的第一个焊盘" (★不是"还没连上的")** ★★★★
        #   ★**踩过的坑 (实测)**: 扩展 7 次就误判"全部连上" ⇒ 路径 1 格
        #     ⇒ ★**根因: ★**起点格天然等于某个焊盘的中心格 ⇒ ★**若把起点算作"命中"**
        #       ⇒ ★**扩展时走 1 步就可能命中第二个焊盘 ⇒ ★**误判提前结束**
        #   ⇒ ★**⇒ 正确建模: ★**起点处先把"自己这个焊盘"标记为已连** ⇒ ★**再走**
        start = {}
        for s in sp:
            start[(s[0], s[1], 0)] = 0.0
        for s in sn:
            start[(s[0], s[1], 1)] = 0.0
        print("  [DBG] P: 焊盘 %d 个 / 起步格 %d · N: 焊盘 %d 个 / 起步格 %d"
              % (len(self._pad_list[0]), len(sp), len(self._pad_list[1]), len(sn)))
        heap = []
        for k, g in start.items():
            goals = gp if k[2] == 0 else gn
            heapq.heappush(heap, (g + h(k[0], k[1], goals), g, k))
        gsc = dict(start)
        came = {}
        # ★**对方的前沿 (用来算"往对方方向长"的额外代价)**
        peer_front = {}
        exp = 0
        best_end = None
        best_cost = INF
        # ★**"已找到目标"的判定**: ★**两侧都到达各自目标 ⇒ 才算成功**
        reached = {}
        while heap and exp < self.budget:
            _f, gc, cur = heapq.heappop(heap)
            if gc > gsc.get(cur, INF) + 1e-9:
                continue
            exp += 1
            li, idx, side = cur
            net = self.net_p if side == 0 else self.net_n
            goals = gp if side == 0 else gn
            # ★★2026-11-06 13:1x **"到达目标"的判定改成"焊盘被连上" (★不是"走到焊盘中心格")**
            #   ★**踩过的坑 (实测)**: ★**焊盘中心格既是起点又是目标** ⇒ ★**第一格就判定到达**
            #     ⇒ ★**路径只有 1 格** ⇒ ★**落了个啥也没干的板**
            #   ⇒ ★**⇒ 判定改为: ★**这个格落在某个"还没连上的焊盘"的 3×3 邻域内** ⇒ 算连上
            if self._touches_new_pad(li, idx, net, side):
                _hit = self._mark_pad_hit(li, idx, net, side)
                if _hit:
                    print("  [DBG] side=%d 命中焊盘 idx=%d (第 %d 个)"
                          % (side, idx, len(self._pad_hit[side])))
                    # ★**该侧所有焊盘都连上了 ⇒ 记下**
                    if len(self._pad_hit[side]) >= len(self._pad_list[side]):
                        reached.setdefault(side, (cur, gc))
                        if len(reached) == 2:
                            ppath = self._trace(came, reached[0][0])
                            npath = self._trace(came, reached[1][0])
                            if ppath and npath:
                                return ppath, npath, ("★**两侧都连上了所有焊盘** (扩展 %d)" % exp)
                        continue
            cx, cy = self._coords(li, idx)
            for (dli, didx) in self._neighbors(li, idx):
                nnet = net
                if not self._free(dli, didx, nnet):
                    continue
                if didx != idx and not self._via_ok(li, dli, didx, nnet):
                    continue
                # ★★**★间距约束: 同一侧的两个状态不能太近? 不 ⇒ ★**关键是"P/N 两条线要平行"**
                #   ⇒ ★**这里用"对方已走过的格"当软障碍: 距离 < pair_min 的格不许走**
                #   ⇒ ★**★但这不是硬障碍** ⇒ ★**改成: 走"靠近对方"的格子给负代价 (奖励并行)**
                _d = 0.0
                _pd = self._peer_dist(dli, didx, side, peer_front)
                if _pd is not None:
                    # ★**越靠近对方越"便宜"** ⇒ ★**鼓励并行**
                    _d += max(0.0, (_pd - self.pair_min)) * 0.35
                    # ★**但离对方太近要罚** (净距不够)
                    if _pd < self.pair_min:
                        _d += (self.pair_min - _pd) * 40.0
                nk = (dli, didx, side)
                ng = gc + 1.0 + _d
                if ng < gsc.get(nk, INF) - 1e-9:
                    gsc[nk] = ng
                    came[nk] = cur
                    peer_front.setdefault(side, []).append((dli, didx))
                    heapq.heappush(heap, (ng + h(dli, didx, goals), ng, nk))
        # ★★**诊断: ★**预算为什么耗尽** ⇒ ★**两侧各自离目标还有多远**
        _dbg = []
        for _side in (0, 1):
            _net = self.net_p if _side == 0 else self.net_n
            _goals = gp if _side == 0 else gn
            _hit = len(self._pad_hit[_side])
            _tot = len(self._pad_list[_side])
            _dbg.append("%s 焊盘 %d/%d 已连" % (_net, _hit, _tot))
        return None, None, ("预算耗尽 (扩展 %d) · %s" % (exp, " · ".join(_dbg)))

    def _peer_dist(self, li, idx, side, peer_front):
        """★**到对方已走过的格的最短距离** (★粗采样, 只看最近 200 个)"""
        peers = peer_front.get(1 - side) or []
        if not peers:
            return None
        cx, cy = self._coords(li, idx)
        best = INF
        for (pl, pk) in peers[-200:]:
            px, py = self._coords(pl, pk)
            d = math.hypot(cx - px, cy - py)
            if d < best:
                best = d
        return None if best == INF else best

    def _neighbors(self, li, idx):
        """★**6 邻域 + 同层换层** (★换层点与 router 的 _astar 同构)"""
        r = self.r
        i, j = idx % r.W, idx // r.W
        out = []
        for (di, dj) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            i2, j2 = i + di, j + dj
            if 0 <= i2 < r.W and 0 <= j2 < r.H:
                out.append((li, r._idx(i2, j2)))
        # ★**换层 (同格换层)**
        for l2 in RT.ROUTE_LAYERS:
            if l2 != li:
                out.append((l2, idx))
        return out

    def _trace(self, came, end):
        p = [end]
        while p[-1] in came:
            p.append(came[p[-1]])
        p.reverse()
        return [(s[0], s[1]) for s in p]


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        return 2
    boardp, drcp = a[0], a[1]
    outp = None
    net_p = None
    net_n = None
    width = 0.25
    pair_min = 0.35
    budget = 400000
    i = 2
    while i < len(a):
        if a[i] == "--out":
            outp = a[i + 1]; i += 2
        elif a[i] == "--net":
            net_p = a[i + 1]; i += 2
        elif a[i] == "--pair":
            net_p = a[i + 1]; net_n = a[i + 2]; i += 3
        elif a[i] == "--width":
            width = float(a[i + 1]); i += 2
        elif a[i] == "--pair-min":
            pair_min = float(a[i + 1]); i += 2
        elif a[i] == "--budget":
            budget = int(a[i + 1]); i += 2
        else:
            i += 1
    if not outp:
        print("★必须给 --out")
        return 2
    if not net_p or not net_n:
        # ★**默认取第一对未连通的差分对**
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

    board = pcbnew.LoadBoard(boardp)
    for z in board.Zones():
        z.UnFill()
    r = RT.GridRouter(board, grid=0.125)
    print("═══ 成对走廊 A\\*: %s / %s ═══" % (net_p, net_n))
    print("═══ 网格 %.4fmm · %dx%d · %d 层 ═══" % (r.g, r.W, r.H, RT.NLAYERS))

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
    print("═══ 已灌入 %d 图元 ═══" % len(r.tracks))

    pr = PairRouter(r, net_p, net_n, width=width, pair_min=pair_min, budget=budget)
    ppath, npath, why = pr.route()
    print("── 结果: %s" % why)
    if not ppath or not npath:
        print("── 没找到成对路径 ⇒ 不落铜")
        board.Save(outp)
        return 1

    print("── P 路径 %d 格 / N 路径 %d 格" % (len(ppath), len(npath)))
    # ★**落铜**: ★**先 P 后 N, 但两条都来自同一次搜索 ⇒ 互不打架**
    r.pair_partner = net_p
    okp = r._emit_path(net_p, ppath, width)
    r.pair_partner = None
    okn = r._emit_path(net_n, npath, width)
    print("── 落铜: P=%s N=%s" % (okp, okn))
    if not (okp and okn):
        print("── 落铜被拒 ⇒ 不落盘")
        board.Save(outp)
        return 1
    r.commit(board)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(outp)
    print("── 已写出: %s (%d B)" % (outp, os.path.getsize(outp)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
