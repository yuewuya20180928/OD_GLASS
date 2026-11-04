#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_pcb_routing.py —— ★通用网格路由器 (A* / Lee) + 差分对捆绑 + 电源粗铜 + GND 平面

★★ 为什么必须有这个模块 (而不是手拉线):
  板子是**脚本生成**的 (state/gen_pcb_netlist_board.py) ⇒ 手拉的线下次重生成就没了
  ⇒ ★布线必须**落进生成器** ⇒ 本模块就是那个"可复用的布线器"。

★★ 路由器规格 (★来自 HW/PCB/LAYOUT_RULES.md + STACKUP.md):
  · 网格步长        0.25 mm (8 邻域 ⇒ 45°/90° 走线)
  · 信号层          L1 (F.Cu) 优先 → L3 (In2.Cu) → L5 (In4.Cu)
                   ★**L2 (In1.Cu) 与 L6 (B.Cu) 是完整 GND 平面 ⇒ 不许走信号**
                     (STACKUP.md: L1 信号/L2 GND/L3 信号/L4 电源/L5 信号/L6 GND)
  · 换层            只能相邻信号层换 (F.Cu↔In2.Cu / In2.Cu↔In4.Cu)
                   ⇒ 过孔只跨一层平面 (L2 或 L4), **不跨 GND+电源双平面** (回流路径不断)
  · 线宽            信号 0.25mm / 电源 0.5mm (LAYOUT_RULES: SOM 输入 ≥2A ⇒ ≥0.5mm)
  · 间距            KiCad 默认 0.2mm (本路由器按 0.2mm 建 keepout)
  · 过孔            0.6mm 盘 / 0.3mm 钻 (环宽 0.15mm = KiCad 最小环宽)
  · 差分对          先布 P, 再在 P 的走廊里布 N (软代价拉近 ⇒ 同层同间距) + 长度配平

★ 坐标系: 全程用 KiCad 原生坐标 (内部单位 1e-6 mm, **y 向下**) ⇒ 不用做 y 取负
"""

import heapq
import math

import pcbnew

MM = 1e6

# ------------------------------------------------------------------ 常量
GRID = 0.25            # mm 网格步长
CLEAR = 0.20           # mm 铜间距 (KiCad 默认)
W_SIG = 0.25           # mm 信号线宽
W_PWR = 0.50           # mm 电源线宽
VIA_DIA = 0.60         # mm 过孔盘
VIA_DRILL = 0.30       # mm 过孔钻

# 铜层顺序 (物理 L1..L6) —— 索引即 CU_LAYERS 下标
CU_LAYERS = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu,
             pcbnew.In3_Cu, pcbnew.In4_Cu, pcbnew.B_Cu]
# ★允许走信号的层: L1 / L3 / L5 (索引 0 / 2 / 4)
ROUTE_LAYERS = [0, 2, 4]
# ★每格的层偏好代价 (0 = 首选); 换层代价 (格)
LAYER_COST = {0: 0.0, 2: 0.60, 4: 1.80}
VIA_COST = 30.0

# 层间跳 (相邻信号层): 换层时经过的铜层 (含中间平面层, 孔要穿过去 ⇒ 必须留间距)
VIA_SPAN = {0: (0, 1, 2), 1: (2, 3, 4)}

LNAME = {0: "L1/F.Cu", 1: "L2/In1.Cu", 2: "L3/In2.Cu",
         3: "L4/In3.Cu", 4: "L5/In4.Cu", 5: "L6/B.Cu"}


# ------------------------------------------------------------------ 工具
def netcode(board, name):
    try:
        return board.GetNetcodeFromNetname(name)
    except Exception:
        return -1


def _pad_rect(pad):
    """焊盘外接矩形 (mm, 轴对齐) —— 处理封装旋转 (pad 自身 90° 时宽高互换)"""
    p = pad.GetPosition()
    sz = pad.GetSize()
    w = sz.x / MM
    h = sz.y / MM
    try:
        rot = pad.GetOrientationDegrees() % 180
    except Exception:
        rot = 0
    if 45 <= rot <= 135:
        w, h = h, w
    return (p.x / MM - w / 2.0, p.y / MM - h / 2.0,
            p.x / MM + w / 2.0, p.y / MM + h / 2.0)


def _rect_cells(gx0, gy0, gx1, gy1, g):
    i0 = int(math.floor(gx0 / g))
    i1 = int(math.ceil(gx1 / g))
    j0 = int(math.floor(gy0 / g))
    j1 = int(math.ceil(gy1 / g))
    out = []
    for j in range(j0, j1 + 1):
        for i in range(i0, i1 + 1):
            out.append((i, j))
    return out


def _seg_cells(x1, y1, x2, y2, g, r):
    """线段 (含端点) 附近的网格单元 (半径 r 个格, 圆判据)
       ★**沿线走**而不是扫包围盒 —— 否则长线段的复杂度是 O(L²) ⇒ 整板布线会卡死"""
    gx1, gy1, gx2, gy2 = x1 / g, y1 / g, x2 / g, y2 / g
    dx, dy = gx2 - gx1, gy2 - gy1
    length = math.hypot(dx, dy)
    n = max(1, int(math.ceil(length / 0.7)))
    ri = int(math.ceil(r))
    out = set()
    for k in range(n + 1):
        t = k / float(n)
        ci = int(round(gx1 + t * dx))
        cj = int(round(gy1 + t * dy))
        for dj in range(-ri, ri + 1):
            for di in range(-ri, ri + 1):
                if di * di + dj * dj > r * r + 1e-9:
                    continue
                out.add((ci + di, cj + dj))
    return out


class RoutingError(Exception):
    pass


# ------------------------------------------------------------------ 路由器
class GridRouter:
    """★网格路由器 —— 一次可以布一批网 (批量跑, 不是一条一条手写)"""

    def __init__(self, board, grid=GRID):
        self.b = board
        self.g = grid
        bb = board.GetBoardEdgesBoundingBox()
        self.bb = (bb.GetLeft() / MM, bb.GetTop() / MM,
                   bb.GetRight() / MM, bb.GetBottom() / MM)
        self.W = int((self.bb[2] - self.bb[0]) / grid) + 3
        self.H = int((self.bb[3] - self.bb[1]) / grid) + 3
        # 障碍图: cu[li][idx]=net (精确铜) ; halo/haloW[li][idx]=set(net) (净距禁区)
        self.cu = [dict() for _ in range(6)]
        self.halo = [dict() for _ in range(6)]      # 细线规则
        self.haloW = [dict() for _ in range(6)]     # 粗线/过孔规则
        self.net_pads = {}          # net -> [(ref, padnum, cx, cy, layers)]
        self.pad_rects = []         # (net, x0,y0,x1,y1) —— 过孔不许打进焊盘
        self.pad_cell = {}          # (li,idx) -> (net, true_cx, true_cy)
        self.routed = set()
        self.tracks = []            # (net, x1,y1,x2,y2,li,width)
        self.vias = []              # (net, x, y, l1, l2)
        self._build_pads()

    # ------------------------------------------------ 索引
    def _idx(self, i, j):
        return j * self.W + i

    def _cx(self, i):
        return self.bb[0] + i * self.g

    def _cy(self, j):
        return self.bb[1] + j * self.g

    def _ci(self, x):
        return int(round((x - self.bb[0]) / self.g))

    def _cj(self, y):
        return int(round((y - self.bb[1]) / self.g))

    # ------------------------------------------------ 障碍建图
    def _build_pads(self):
        """全板焊盘 → 障碍 + 每网焊盘清单"""
        for fp in list(self.b.GetFootprints()):
            for pad in list(fp.Pads()):
                nm = pad.GetNetname()
                if not nm:
                    continue
                x0, y0, x1, y1 = _pad_rect(pad)
                cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
                try:
                    pth = (pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH)
                except Exception:
                    pth = False
                layers = list(range(6)) if pth else [0]   # ★本板 SMD 全在 F.Cu
                self.net_pads.setdefault(nm, []).append(
                    (fp.GetReference(), str(pad.GetNumber()), cx, cy, layers))
                self.pad_rects.append((nm, x0, y0, x1, y1))
                for li in layers:
                    for (i, j) in _rect_cells(x0, y0, x1, y1, self.g):
                        idx = self._idx(i, j)
                        self.cu[li][idx] = nm
                        self.pad_cell[(li, idx)] = (nm, cx, cy)
        self._halo_pads()

    def _mark(self, li, idx, net, wide):
        m = self.haloW if wide else self.halo
        s = m[li].get(idx)
        if s is None:
            s = set()
            m[li][idx] = s
        s.add(net)

    def _halo_pads(self):
        """焊盘净距禁区: 细线 = 外扩 (0.2+0.125)=0.325mm ; 粗线/过孔 = 0.5mm"""
        for li in range(6):
            for idx, net in list(self.cu[li].items()):
                i, j = idx % self.W, idx // self.W
                # 焊盘中心 (用单元中心近似; 焊盘小 ⇒ 误差可接受)
                px, py = self._cx(i), self._cy(j)
                for wide, rr in ((False, 0.325), (True, 0.50)):
                    for (i2, j2) in _seg_cells(px, py, px, py, self.g, rr / self.g):
                        if not (0 <= i2 < self.W and 0 <= j2 < self.H):
                            continue
                        self._mark(li, self._idx(i2, j2), net, wide)

    # ------------------------------------------------ 可走性
    def _free(self, li, idx, net, wide=False):
        c = self.cu[li].get(idx)
        if c is not None and c != net:
            return False
        if c == net:
            return True        # ★自己的铜 (焊盘) ⇒ 豁免净距 (焊盘间距由 DRC 单独判)
        m = self.haloW if wide else self.halo
        s = m[li].get(idx)
        if s and (s - {net}):
            return False
        return True

    def _via_ok(self, li, idx, net):
        """此处能不能打孔 (跨层所有铜层都要有净距)"""
        for l2 in VIA_SPAN[li]:
            c = self.cu[l2].get(idx)
            if c is not None and c != net:
                return False
            s = self.haloW[l2].get(idx)
            if s and (s - {net}):
                return False
        return True

    # ------------------------------------------------ A*
    def _astar(self, start, goals, net, dist_map=None, alpha=0.0,
                max_via=True, wide=False):
        """start: [(li,idx)] ; goals: set((li,idx))"""
        INF = float("inf")
        gsc = {}
        came = {}
        heap = []
        gx = [k % self.W for (l, k) in goals]
        gy = [k // self.W for (l, k) in goals]
        if not gx:
            return None
        bx0, bx1 = min(gx), max(gx)
        by0, by1 = min(gy), max(gy)

        def h_of(li, idx):
            i, j = idx % self.W, idx // self.W
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
            return (dx + dy) + (math.sqrt(2.0) - 1.0) * min(dx, dy)

        cnt = 0
        for s in start:
            gsc[s] = 0.0
            heapq.heappush(heap, (h_of(s[0], s[1]), 0.0, cnt, s))
            cnt += 1
        goalset = set(goals)
        best = None
        while heap:
            f, gg, _, cur = heapq.heappop(heap)
            if gg > gsc.get(cur, INF) + 1e-12:
                continue
            if cur in goalset:
                best = cur
                break
            li, idx = cur
            i, j = idx % self.W, idx // self.W
            for dj in (-1, 0, 1):
                for di in (-1, 0, 1):
                    if di == 0 and dj == 0:
                        continue
                    i2, j2 = i + di, j + dj
                    if not (0 <= i2 < self.W and 0 <= j2 < self.H):
                        continue
                    k = self._idx(i2, j2)
                    if not self._free(li, k, net, wide):
                        continue
                    step = (math.sqrt(2.0) if (di and dj) else 1.0)
                    c = gg + step + LAYER_COST.get(li, 0.0)
                    if alpha and dist_map is not None:
                        c += alpha * dist_map.get(k, 0)
                    if c < gsc.get((li, k), INF):
                        gsc[(li, k)] = c
                        came[(li, k)] = cur
                        heapq.heappush(heap, (c + h_of(li, k), c, cnt, (li, k)))
                        cnt += 1
            if max_via:
                for nli in (li - 1, li + 1):
                    if nli not in ROUTE_LAYERS or nli not in VIA_SPAN.get(li, ()):
                        continue
                    if not self._via_ok(li, idx, net):
                        continue
                    st = (nli, idx)
                    c = gg + VIA_COST + LAYER_COST.get(nli, 0.0)
                    if alpha and dist_map is not None:
                        c += alpha * dist_map.get(idx, 0)
                    if c < gsc.get(st, INF):
                        gsc[st] = c
                        came[st] = cur
                        heapq.heappush(heap, (c + h_of(nli, idx), c, cnt, st))
                        cnt += 1
        if best is None:
            return None
        path = [best]
        while path[-1] in came:
            path.append(came[path[-1]])
        path.reverse()
        return path

    # ------------------------------------------------ 单网多焊盘
    def route_net(self, net, width=W_SIG, allow_via=True, dist_map=None,
                  alpha=0.0, via_count=1, trunk=None):
        """布一个多焊盘网 —— 最小生成树顺序逐个并入一棵树
           trunk: ((padA, padB),) —— 先布的"主干"焊盘对 (差分对用它对齐走向)
           返回 dict(ok/段数/长度mm/失败焊盘数)"""
        pads = self.net_pads.get(net)
        if not pads or len(pads) < 2:
            return {"ok": True, "segs": 0, "len": 0.0, "fail": 0, "net": net}
        wide = (width >= 0.4)
        order = self._mst_order(pads)
        if trunk:
            for (pa, pb) in trunk:
                ta = self._find_pad(net, pa)
                tb = self._find_pad(net, pb)
                if ta is None or tb is None:
                    continue
                cells = self._pad_cells(net, tb)
                path = self._astar(list(cells), set(self._pad_cells(net, ta)),
                                    net, dist_map=dist_map, alpha=alpha,
                                    max_via=allow_via, wide=wide)
                if path:
                    self._emit_path(net, path, width, via_count)
                    trunk_cells = set(path)
        gx = sum(p[2] for p in pads) / len(pads)
        gy = sum(p[3] for p in pads) / len(pads)
        root = min(order, key=lambda p: (p[2] - gx) ** 2 + (p[3] - gy) ** 2)
        tree = set(self._pad_cells(net, root))
        tree |= locals().get("trunk_cells", set())
        ok = True
        nfail = 0
        for pad in order:
            if pad is root:
                continue
            cells = self._pad_cells(net, pad)
            if cells & tree:
                continue
            # ★主干优先: 已经布过的树干算在树里
            path = self._astar(list(cells), set(tree), net,
                                dist_map=dist_map, alpha=alpha,
                                max_via=allow_via, wide=wide)
            if path is None:
                nfail += 1
                ok = False
                continue
            self._emit_path(net, path, width, via_count)
            tree |= set(path)
        length = self.net_length(net)
        self.routed.add(net)
        return {"ok": ok, "segs": len(self.tracks), "len": round(length, 3),
                "fail": nfail, "net": net}

    def _mst_order(self, pads):
        """Prim 最小生成树 ⇒ 好的布线顺序"""
        n = len(pads)
        if n <= 2:
            return list(pads)
        d = [1e18] * n
        d[0] = 0.0
        order = []
        used = [False] * n
        for _ in range(n):
            u = -1
            for i in range(n):
                if not used[i] and (u < 0 or d[i] < d[u]):
                    u = i
            used[u] = True
            order.append(pads[u])
            for i in range(n):
                if used[i]:
                    continue
                dd = ((pads[u][2] - pads[i][2]) ** 2 + (pads[u][3] - pads[i][3]) ** 2)
                if dd < d[i]:
                    d[i] = dd
        return order

    def _pad_cells(self, net, pad):
        """焊盘的**中心单元** (只取中心, 起点线从焊盘真实中心画出去)"""
        _ref, _num, cx, cy, layers = pad
        i, j = self._ci(cx), self._cj(cy)
        return set((li, self._idx(i, j)) for li in layers)

    def _find_pad(self, net, key):
        """按 (ref, padnum) 或 padnum 找焊盘"""
        for p in self.net_pads.get(net, []):
            if p[1] == str(key):
                return p
            if isinstance(key, (tuple, list)) and len(key) == 2 and p[0] == key[0] and p[1] == str(key[1]):
                return p
        return None

    # ------------------------------------------------ GND 平面下拉过孔
    def route_gnd_drops(self, net="GND", max_r_mm=3.0, via_top=0, via_bot=5):
        """★GND 焊盘 → 短走线 → 通孔 → L2/L6 完整 GND 平面
           (SMD 焊盘在 F.Cu ⇒ 必须靠过孔下到平面; ★通孔一层平面都连得上)
           返回 (成功数, 失败数)"""
        pads = list(self.net_pads.get(net, []))
        ok = 0
        fail = 0
        for pad in pads:
            _ref, _num, cx, cy, _layers = pad
            done = False
            for r_mm in (0.8, 1.2, 1.6, 2.0, 2.5, 3.0):
                if r_mm > max_r_mm:
                    break
                for cand in self._ring_cells(cx, cy, r_mm):
                    i, j = cand
                    if not (0 <= i < self.W and 0 <= j < self.H):
                        continue
                    idx = self._idx(i, j)
                    px, py = self._cx(i), self._cy(j)
                    if not self._free(0, idx, net):
                        continue
                    if self._in_pad(px, py):
                        continue
                    if not self._via_free_all(idx, net):
                        continue
                    path = self._astar(list(self._pad_cells(net, pad)), {(0, idx)},
                                       net, max_via=False)
                    if path is None:
                        continue
                    self._emit_path(net, path, W_SIG, 1)
                    self.vias.append((net, px, py, via_top, via_bot))
                    self._add_via_halo(net, px, py, via_top, via_bot)
                    ok += 1
                    done = True
                    break
                if done:
                    break
            if not done:
                fail += 1
        return (ok, fail)

    def _ring_cells(self, cx, cy, r_mm):
        """以 (cx,cy) 为心、半径 r_mm 的候选单元 (按距离排序)"""
        r = r_mm / self.g
        i0, j0 = self._ci(cx), self._cj(cy)
        out = []
        for dj in range(-int(r) - 1, int(r) + 2):
            for di in range(-int(r) - 1, int(r) + 2):
                d = math.hypot(di, dj)
                if 0.6 <= d <= r:
                    out.append((d, i0 + di, j0 + dj))
        out.sort()
        return [(i, j) for (_d, i, j) in out]

    def _in_pad(self, x, y):
        """这个点是不是落在某个焊盘里 (过孔不许打在焊盘上 = via-in-pad)"""
        for (net, x0, y0, x1, y1) in self.pad_rects:
            if x0 - 0.05 <= x <= x1 + 0.05 and y0 - 0.05 <= y <= y1 + 0.05:
                return True
        return False

    def _via_free_all(self, idx, net):
        """通孔 (贯穿 6 层) 在所有层都要有净距"""
        for li in range(6):
            c = self.cu[li].get(idx)
            if c is not None and c != net:
                return False
            s = self.haloW[li].get(idx)
            if s and (s - {net}):
                return False
        return True

    # ------------------------------------------------ 长度配平 (蛇形)
    def add_meander(self, net, extra_mm):
        """给 net 加一段三角凸起, 走线长度增加 extra_mm (mm)
           ★差分对长度配平用 (把短的那根加长)"""
        if extra_mm <= 0.001:
            return 0.0
        segs = self.net_tracks(net)
        best = None
        for s in segs:
            L = math.hypot(s[3] - s[1], s[4] - s[2])
            if L < 2.5:
                continue
            if best is None or L > best[0]:
                best = (L, s)
        if best is None:
            return 0.0
        L, s = best
        ux, uy = (s[3] - s[1]) / L, (s[4] - s[2]) / L
        base = min(L * 0.8, 8.0)
        # 三角凸起: extra = 2*sqrt((base/2)^2 + a^2) - base  ⇒  解 a
        val = ((base + extra_mm) / 2.0) ** 2 - (base / 2.0) ** 2
        if val <= 0:
            return 0.0
        a = math.sqrt(val)
        for sign in (1, -1):
            nx, ny = -uy * sign, ux * sign
            mid = ((s[1] + s[3]) / 2.0, (s[2] + s[4]) / 2.0)
            apex = (mid[0] + nx * a, mid[1] + ny * a)
            if self._free_line(apex, net, s[5]):
                self._insert_meander(net, s, mid, apex, ux, uy, base)
                return extra_mm
        return 0.0

    def _free_line(self, pt, net, li):
        """凸起顶点附近有没有别的网的铜"""
        i, j = self._ci(pt[0]), self._cj(pt[1])
        for dj in (-1, 0, 1):
            for di in (-1, 0, 1):
                i2, j2 = i + di, j + dj
                if not (0 <= i2 < self.W and 0 <= j2 < self.H):
                    return False
                if not self._free(li, self._idx(i2, j2), net):
                    return False
        return True

    def _insert_meander(self, net, seg, mid, apex, ux, uy, base):
        """把 seg 换成 带三角凸起 的三段"""
        x1, y1 = seg[1], seg[2]
        x2, y2 = seg[3], seg[4]
        li, w = seg[5], seg[6]
        d = (base / 2.0)
        p_in = (mid[0] - ux * d, mid[1] - uy * d)
        p_out = (mid[0] + ux * d, mid[1] + uy * d)
        idx = self.tracks.index(seg)
        new = [
            (net, x1, y1, p_in[0], p_in[1], li, w),
            (net, p_in[0], p_in[1], apex[0], apex[1], li, w),
            (net, apex[0], apex[1], p_out[0], p_out[1], li, w),
            (net, p_out[0], p_out[1], x2, y2, li, w),
        ]
        self.tracks[idx:idx + 1] = new
        for s in new:
            self._add_track_halo(s[0], s[1], s[2], s[3], s[4], s[5])
        return True

    # ------------------------------------------------ 路径 → 铜
    def _emit_path(self, net, path, width, via_count=1):
        pts = []
        for (li, idx) in path:
            i, j = idx % self.W, idx // self.W
            pts.append([li, self._cx(i), self._cy(j)])
        p0 = self.pad_cell.get(path[0])
        if p0 and p0[0] == net:
            pts[0][1], pts[0][2] = p0[1], p0[2]
        pn = self.pad_cell.get(path[-1])
        if pn and pn[0] == net:
            pts[-1][1], pts[-1][2] = pn[1], pn[2]
        seg = []
        for k in range(len(pts) - 1):
            la, xa, ya = pts[k]
            lb, xb, yb = pts[k + 1]
            if la != lb:
                self._emit_via(net, xa, ya, la, lb, via_count)
                seg.append((net, xa, ya, xb, yb, lb, width))
            else:
                seg.append((net, xa, ya, xb, yb, la, width))
        merged = []
        for s in seg:
            if merged:
                p = merged[-1]
                ax, ay = p[2] - p[1], p[3] - p[1]
                bx, by = s[3] - s[1], s[4] - s[1]
                if (p[5] == s[5]) and (abs(ax * by - ay * bx) < 1e-9) \
                        and (ax * bx + ay * by > 0):
                    merged[-1] = (p[0], p[1], p[2], s[3], s[4], p[5], p[6])
                    continue
            merged.append(s)
        for s in merged:
            self.tracks.append(s)
            self._add_track_halo(s[0], s[1], s[2], s[3], s[4], s[5])

    def _emit_via(self, net, x, y, la, lb, count=1):
        l1, l2 = (la, lb) if la < lb else (lb, la)
        vs = [(x, y)]
        if count > 1:
            vs = [(x + (k - (count - 1) / 2.0) * 0.6, y)
                  for k in range(count)]
        for (vx, vy) in vs:
            if not self._via_ok(l1, self._idx(self._ci(vx), self._cj(vy)), net):
                continue
            self.vias.append((net, vx, vy, l1, l2))
            self._add_via_halo(net, vx, vy, l1, l2)

    def _add_track_halo(self, net, x1, y1, x2, y2, li):
        """走线净距禁区: 细线 0.45mm (中心线) ; 粗线/过孔 0.70mm"""
        for wide, rr in ((False, 0.45), (True, 0.70)):
            for (i, j) in _seg_cells(x1, y1, x2, y2, self.g, rr / self.g):
                if not (0 <= i < self.W and 0 <= j < self.H):
                    continue
                self._mark(li, self._idx(i, j), net, wide)

    def _add_via_halo(self, net, x, y, l1, l2):
        i, j = self._ci(x), self._cj(y)
        for wide, rr in ((False, 0.625), (True, 0.80)):
            ri = int(math.ceil(rr / self.g))
            for li in range(l1, l2 + 1):
                for dj in range(-ri, ri + 1):
                    for di in range(-ri, ri + 1):
                        if di * di + dj * dj > (rr / self.g) ** 2 + 1e-9:
                            continue
                        i2, j2 = i + di, j + dj
                        if not (0 <= i2 < self.W and 0 <= j2 < self.H):
                            continue
                        self._mark(li, self._idx(i2, j2), net, wide)

    def net_length(self, net):
        tot = 0.0
        for s in self.tracks:
            if s[0] != net:
                continue
            tot += math.hypot(s[3] - s[1], s[4] - s[2])
        return tot

    def net_tracks(self, net):
        return [s for s in self.tracks if s[0] == net]

    # ------------------------------------------------ 差分对走廊
    def build_dist_map(self, net):
        """到 net 已布路径的距离图 (BFS, 跨层合并) —— 差分对"拉近"用"""
        cells = set()
        for s in self.tracks:
            if s[0] != net:
                continue
            for (i, j) in _seg_cells(s[1], s[2], s[3], s[4], self.g, 0):
                cells.add(self._idx(i, j))
        if not cells:
            return {}
        dist = {c: 0 for c in cells}
        frontier = list(cells)
        d = 0
        while frontier and d < 40:
            d += 1
            nxt = []
            for c in frontier:
                i, j = c % self.W, c // self.W
                for dj in (-1, 0, 1):
                    for di in (-1, 0, 1):
                        i2, j2 = i + di, j + dj
                        if not (0 <= i2 < self.W and 0 <= j2 < self.H):
                            continue
                        k = self._idx(i2, j2)
                        if k in dist:
                            continue
                        dist[k] = d
                        nxt.append(k)
            frontier = nxt
        return dist

    # ------------------------------------------------ 落板
    def commit(self, board):
        """把生成的走线/过孔写进板子 (★不改任何网表绑定)"""
        n = 0
        for (net, x1, y1, x2, y2, li, w) in self.tracks:
            code = netcode(board, net)
            if code <= 0:
                continue
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
            t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
            t.SetWidth(pcbnew.FromMM(w))
            t.SetLayer(CU_LAYERS[li])
            t.SetNetCode(code)
            board.Add(t)
            n += 1
        for (net, x, y, l1, l2) in self.vias:
            code = netcode(board, net)
            if code <= 0:
                continue
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
            try:
                v.SetViaType(pcbnew.VIATYPE_THROUGH)
            except Exception:
                pass
            v.SetWidth(pcbnew.FromMM(VIA_DIA))
            v.SetDrill(pcbnew.FromMM(VIA_DRILL))
            v.SetLayerPair(CU_LAYERS[l1], CU_LAYERS[l2])
            v.SetNetCode(code)
            board.Add(v)
            n += 1
        return n


# ------------------------------------------------------------------ 差分对
def route_diff_pair(router, net_p, net_n, width=W_SIG, allow_via=True,
                    trunk_p=None, trunk_n=None):
    """★差分对成对布 —— 先布 P, 再在 P 的走廊里布 N (软代价拉近 ⇒ 同层同间距)
       trunk_p/trunk_n: ((padA,padB),) —— 主干焊盘对 (让两根线走同一条走廊)
       返回 dict: 长度 / 长度差 / 最小间距"""
    res = {"p": net_p, "n": net_n}
    r1 = router.route_net(net_p, width=width, allow_via=allow_via, trunk=trunk_p)
    res["p_ok"] = r1["ok"]
    if not r1["ok"]:
        res["n_ok"] = False
        return res
    dm = router.build_dist_map(net_p)
    r2 = router.route_net(net_n, width=width, allow_via=allow_via,
                          dist_map=dm, alpha=0.45, trunk=trunk_n)
    res["n_ok"] = r2["ok"]
    res["lp"] = round(r1["len"], 3)
    res["ln"] = round(r2["len"], 3)
    res["delta"] = round(abs(r1["len"] - r2["len"]), 3)
    # ★长度配平: 短的那根加蛇形
    if res["delta"] > 0.13:
        if r1["len"] < r2["len"]:
            got = router.add_meander(net_p, res["delta"])
        else:
            got = router.add_meander(net_n, res["delta"])
        res["meander"] = round(got, 3)
        res["lp"] = round(router.net_length(net_p), 3)
        res["ln"] = round(router.net_length(net_n), 3)
        res["delta"] = round(abs(res["lp"] - res["ln"]), 3)
    res["min_gap"] = _min_gap(router, net_p, net_n)
    return res


def _min_gap(router, net_a, net_b):
    """两条网之间的最小间距 (mm) —— 差分对"同间距"的实测值"""
    g = router.g
    ca, cb = set(), set()
    for s in router.tracks:
        if s[0] == net_a:
            for (i, j) in _seg_cells(s[1], s[2], s[3], s[4], g, 0):
                ca.add((i, j))
        elif s[0] == net_b:
            for (i, j) in _seg_cells(s[1], s[2], s[3], s[4], g, 0):
                cb.add((i, j))
    if not ca or not cb:
        return None
    best = 1e9
    for (i, j) in ca:
        for (di, dj) in ((1, 0), (0, 1), (1, 1), (1, -1)):
            k = (i + di, j + dj)
            if k in cb:
                d = g * math.hypot(di, dj)
                if d < best:
                    best = d
    return round(best, 3) if best < 1e9 else None


# ------------------------------------------------------------------ GND 平面
def add_gnd_planes(board, layers=(1, 5), net="GND", fill=True):
    """★L2 / L6 完整 GND 平面 (STACKUP.md: L2 GND / L6 GND)
       ★**完整平面 = 不分割** ⇒ 满足 LAYOUT_RULES "L2/L6 不得在差分对下方被分割"
       ★平面层不放信号 (路由器只用 L1/L3/L5)"""
    bb = board.GetBoardEdgesBoundingBox()
    pts = [pcbnew.VECTOR2I(bb.GetLeft(), bb.GetTop()),
           pcbnew.VECTOR2I(bb.GetRight(), bb.GetTop()),
           pcbnew.VECTOR2I(bb.GetRight(), bb.GetBottom()),
           pcbnew.VECTOR2I(bb.GetLeft(), bb.GetBottom())]
    made = 0
    code = netcode(board, net)
    for li in layers:
        z = pcbnew.ZONE(board)
        z.SetLayer(CU_LAYERS[li])
        if code > 0:
            z.SetNetCode(code)
        z.SetLocalClearance(pcbnew.FromMM(0.25))
        try:
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        except Exception:
            pass
        try:
            z.SetAssignedPriority(0)
        except Exception:
            pass
        lc = pcbnew.SHAPE_LINE_CHAIN()
        for p in pts:
            lc.Append(p)
        lc.SetClosed(True)
        z.AddPolygon(lc)
        board.Add(z)
        made += 1
    if fill:
        _fill_zones(board)
    return made


def _fill_zones(board):
    try:
        board.BuildConnectivity()
    except Exception:
        pass
    try:
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        return True
    except Exception as e:
        print("  ⚠️ 区域填充失败: %s" % e)
        return False


# ------------------------------------------------------------------ 整板布线计划
# ★差分对清单 (按任务优先级)
DIFF_PAIRS = [
    # (P 网, N 网, P 主干, N 主干)
    ("NET_USB_D_P_TYPEC", "NET_USB_D_N_TYPEC",
     ((("J_USB_C", "2"), ("R_SER_USB_D_P", "2")),),
     ((("J_USB_C", "3"), ("R_SER_USB_D_N", "2")),)),
    ("USB_D_P_SRC", "USB_D_N_SRC",
     ((("R_SER_USB_D_P", "1"), ("J_SOM_P1", "92")),),
     ((("R_SER_USB_D_N", "1"), ("J_SOM_P1", "94")),)),
    ("CSI_D0_CK_P_SRC", "CSI_D0_CK_N_SRC", None, None),
    ("CSI_D0_CK_P", "CSI_D0_CK_N", None, None),
    ("CSI_D0_D0_P_SRC", "CSI_D0_D0_N_SRC", None, None),
    ("CSI_D0_D0_P", "CSI_D0_D0_N", None, None),
    ("CSI_D0_D1_P_SRC", "CSI_D0_D1_N_SRC", None, None),
    ("CSI_D0_D1_P", "CSI_D0_D1_N", None, None),
    ("CSI_D0_D2_P_SRC", "CSI_D0_D2_N_SRC", None, None),
    ("CSI_D0_D2_P", "CSI_D0_D2_N", None, None),
    ("CSI_D0_D3_P_SRC", "CSI_D0_D3_N_SRC", None, None),
    ("CSI_D0_D3_P", "CSI_D0_D3_N", None, None),
    ("DSI_D0_CK_P_SRC", "DSI_D0_CK_N_SRC", None, None),
    ("DSI_D0_CK_P", "DSI_D0_CK_N", None, None),
    ("DSI_D0_D0_P_SRC", "DSI_D0_D0_N_SRC", None, None),
    ("DSI_D0_D0_P", "DSI_D0_D0_N", None, None),
    ("DSI_D0_D1_P_SRC", "DSI_D0_D1_N_SRC", None, None),
    ("DSI_D0_D1_P", "DSI_D0_D1_N", None, None),
    ("DSI_D0_D2_P_SRC", "DSI_D0_D2_N_SRC", None, None),
    ("DSI_D0_D2_P", "DSI_D0_D2_N", None, None),
    ("DSI_D0_D3_P_SRC", "DSI_D0_D3_N_SRC", None, None),
    ("DSI_D0_D3_P", "DSI_D0_D3_N", None, None),
]

# ★电源网 (宽铜) —— 优先级: 大电流链 → 局部电源 → 一般电源
POWER_NETS = [
    ("RAIL_SOM_DCIN", W_PWR, 3),      # SOM 输入 (≥2A) ⇒ ≥0.5mm + 过孔阵列
    ("RAIL_DEMO_5V", W_PWR, 3),       # USB-C 5V 输入链
    ("SYS_PCB", W_PWR, 2),
    ("VDD_3V3_IO", 0.40, 1),
    ("VDD_1V8_IO", 0.40, 1),
    ("LIGHT_3V3", 0.40, 1),
    ("V_CORE", 0.40, 1),
    ("LIGHT_5V", 0.40, 1),
    ("LIGHT_1V8", 0.40, 1),
    ("V_SOC_IO", 0.40, 1),
    ("BAT", 0.40, 1),
    ("BAT_SW", 0.40, 1),
    ("SENSOR_VDD_IO", 0.40, 1),
    ("SENSOR_CORE", 0.40, 1),
    ("SENSOR_AVDD", 0.40, 1),
]

# ★上电/复位/时序关键线 (LAYOUT_RULES §2: 每个电源 IC 的 EN 必须有明确网络)
TIMING_NETS = [
    "RESET_N", "RESET_N_SOC", "CAM_RESET_N", "PWR_GOOD", "PWR_ON",
    "PG_AND", "BOOT_N", "EN_VIO", "CARRIER_BOARD_EN", "EN_VCORE",
    "VBUS_DET", "VBUS_DET_D", "SUPV_SENSE", "SUPV_CT",
]


def route_board(board, verbose=True):
    """★★ 整板布线 —— 一次跑完, 返回统计
       (调用方: state/gen_pcb_netlist_board.py —— ★布线必须落进生成器)"""
    import time
    t0 = time.time()
    stats = {"pairs": [], "nets": {}, "failed": [], "gnd": {}}
    r = GridRouter(board)

    # ---------- 0) GND 完整平面 (L2 + L6) —— 先建, 后面所有布线绕开
    add_gnd_planes(board, layers=(1, 5), fill=False)
    if verbose:
        print("  [GND] L2/L6 完整平面已建 (★不分割 ⇒ 差分对下方参考平面完整)")

    # ---------- 1) 差分对 (成对布) —— USB 先, 再 MIPI
    for (p, n, tp, tn) in DIFF_PAIRS:
        if p not in r.net_pads or n not in r.net_pads:
            continue
        res = route_diff_pair(r, p, n, trunk_p=tp, trunk_n=tn)
        stats["pairs"].append(res)
        if verbose:
            print("  [PAIR] %-22s / %-22s  ok=%s/%s  L=%.2f/%.2f  Δ=%.3fmm  间距=%s"
                  % (p, n, res.get("p_ok"), res.get("n_ok"),
                     res.get("lp", 0), res.get("ln", 0), res.get("delta", 0),
                     res.get("min_gap")))

    # ---------- 2) 电源 (宽铜 + 过孔阵列)
    for (net, w, vc) in POWER_NETS:
        if net not in r.net_pads:
            continue
        res = r.route_net(net, width=w, via_count=vc)
        stats["nets"][net] = res
        if not res["ok"]:
            stats["failed"].append(net)
        if verbose:
            print("  [PWR ] %-16s w=%.2fmm  ok=%s  失败脚=%d  L=%.1fmm"
                  % (net, w, res["ok"], res["fail"], res["len"]))

    # ---------- 3) 时序/复位/EN 关键线
    for net in TIMING_NETS:
        if net not in r.net_pads:
            continue
        res = r.route_net(net, width=W_SIG)
        stats["nets"][net] = res
        if not res["ok"]:
            stats["failed"].append(net)
        if verbose:
            print("  [TIME] %-16s ok=%s  失败脚=%d  L=%.1fmm"
                  % (net, res["ok"], res["fail"], res["len"]))

    # ---------- 4) 其余网络 (按焊盘数从多到少 ⇒ 大网先布)
    rest = [n for n in r.net_pads
            if len(r.net_pads[n]) >= 2 and n not in r.routed and n != "GND"]
    rest.sort(key=lambda n: -len(r.net_pads[n]))
    for net in rest:
        res = r.route_net(net, width=W_SIG)
        stats["nets"][net] = res
        if not res["ok"]:
            stats["failed"].append(net)
    if verbose:
        print("  [REST] 其余 %d 个网已布" % len(rest))

    # ---------- 5) GND 下拉过孔 (焊盘 → 短走线 → 通孔 → L2/L6 平面)
    ok, fail = r.route_gnd_drops("GND")
    stats["gnd"] = {"drops": ok, "fail": fail}
    if verbose:
        print("  [GND ] 下拉过孔 %d 成功 / %d 失败" % (ok, fail))

    # ---------- 6) 落板 + 填平面
    n_new = r.commit(board)
    stats["tracks"] = len(r.tracks)
    stats["vias"] = len(r.vias)
    stats["new_items"] = n_new
    for z in board.Zones():
        try:
            z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        except Exception:
            pass
    _fill_zones(board)
    stats["seconds"] = round(time.time() - t0, 1)
    return stats


# ------------------------------------------------------------------ 自检
def _selftest():
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(6)
    r = GridRouter(b)
    print("  网格: %dx%d 格 @ %.2fmm  信号层=%s" %
          (r.W, r.H, r.g, [LNAME[i] for i in ROUTE_LAYERS]))
    print("  ✅ gen_pcb_routing 自检通过 (模块可加载)")


if __name__ == "__main__":
    _selftest()
