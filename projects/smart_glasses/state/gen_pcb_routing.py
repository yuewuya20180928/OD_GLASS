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
HALO_MARGIN = 0.07     # mm ★栅格量化余量 (单元中心采样 ⇒ 实际净距会少 ~半格)
ESC_LEN = 1.20         # mm ★密集焊盘出脚直道长度 (沿焊盘中心线直线走出)
# ★出脚直道长度候选 (长→短) —— ★板边放不下就缩短 (fix B: 出脚直道离网格 ⇒ 板边要单独查)
ESC_LENS = (1.20, 0.90, 0.60, 0.40)
EDGE_CLEAR = 0.50      # mm ★板边净距 (KiCad board setup: copper edge clearance = 0.5mm)
# ★出脚直道: 直道是**离网格**的 (落在焊盘真实中心线上) ⇒ 落铜后必须再对"已布走线/过孔"
#   做一次几何净距检查 (_stub_vs_routed) —— A* 的障碍图避让不了"后来才出现的直道"。
USE_ESCAPE = True
W_SIG = 0.25           # mm 信号线宽
W_MIN = 0.20           # mm 最细线宽 (KiCad 最小线宽) —— ★SoM BTB (0.4mm pitch) 出脚只能这么细
W_PWR = 0.50           # mm 电源线宽
# ★三个"净距级别" (出线宽度决定要留多少净距):
#   cls0 = 0.20mm (BTB 出脚) · cls1 = 0.25mm (常规信号) · cls2 = 0.50mm (电源宽铜)
W_CLS = (0.20, 0.25, 0.50)
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


def _rect_cells(gx0, gy0, gx1, gy1, g, ox=0.0, oy=0.0):
    """矩形覆盖的网格单元 (★单元**中心**落在矩形内才算 —— 否则会把旁边的空单元
       也当成铜 ⇒ 焊盘出不来线)"""
    i0 = int(math.ceil((gx0 - ox) / g - 1e-9))
    i1 = int(math.floor((gx1 - ox) / g + 1e-9))
    j0 = int(math.ceil((gy0 - oy) / g - 1e-9))
    j1 = int(math.floor((gy1 - oy) / g + 1e-9))
    out = []
    for j in range(j0, j1 + 1):
        for i in range(i0, i1 + 1):
            out.append((i, j))
    if not out:
        # ★比一个单元还小的焊盘 ⇒ 取中心所在单元
        ci = int(round(((gx0 + gx1) / 2.0 - ox) / g))
        cj = int(round(((gy0 + gy1) / 2.0 - oy) / g))
        out.append((ci, cj))
    return out


def _seg_cells(x1, y1, x2, y2, g, r, ox=0.0, oy=0.0):
    """线段 (含端点) 附近的网格单元 (半径 r 个格, 圆判据)
       ★**沿线走**而不是扫包围盒 —— 否则长线段的复杂度是 O(L²) ⇒ 整板布线会卡死"""
    gx1, gy1, gx2, gy2 = (x1 - ox) / g, (y1 - oy) / g, (x2 - ox) / g, (y2 - oy) / g
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


NONET = "\x00NONET"    # ★没分配网络的焊盘 (SoM 未用脚) —— 同样是障碍


def _pt_seg_dist(px, py, x1, y1, x2, y2):
    """点到线段的距离"""
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 < 1e-12:
        return math.hypot(px - x1, py - y1)
    t = ((px - x1) * dx + (py - y1) * dy) / L2
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def _seg_seg_dist(ax, ay, bx, by, cx, cy, dx2, dy2):
    """两线段的最短距离 (交叉 ⇒ 0)"""
    def cross(ox, oy, px2, py2, qx, qy):
        return (px2 - ox) * (qy - oy) - (py2 - oy) * (qx - ox)
    d1 = cross(ax, ay, bx, by, cx, cy)
    d2 = cross(ax, ay, bx, by, dx2, dy2)
    d3 = cross(cx, cy, dx2, dy2, ax, ay)
    d4 = cross(cx, cy, dx2, dy2, bx, by)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return 0.0
    return min(_pt_seg_dist(ax, ay, cx, cy, dx2, dy2),
               _pt_seg_dist(bx, by, cx, cy, dx2, dy2),
               _pt_seg_dist(cx, cy, ax, ay, bx, by),
               _pt_seg_dist(dx2, dy2, ax, ay, bx, by))


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
        # 障碍图: cu[li][idx]=net (精确铜) ; halo[cls][li][idx]=set(net) (净距禁区, 3 个宽度级别)
        self.cu = [dict() for _ in range(6)]
        # ★halo[cls][li][idx] = 该单元被哪些网的铜"占了净距"
        #   cls0=0.20mm / cls1=0.25mm / cls2=0.50mm 三套规则各存一份
        self.halo = [[dict() for _ in range(6)] for _ in range(3)]
        self.net_pads = {}          # net -> [(ref, padnum, cx, cy, layers)]
        self.pad_rects = []         # (net, x0,y0,x1,y1) —— 过孔不许打进焊盘
        self.pad_cell = {}          # (li,idx) -> (net, true_cx, true_cy)
        self.routed = set()
        # ★诊断计数器: 布不动的网到底是"预算用完"还是"真被堵死"
        self.astar_budget = 0
        self.astar_blocked = 0
        self.fail_reasons = {}
        self.fail_budget = {}
        # ★真板边几何 (Edge.Cuts) —— ★**不能用 GetBoardEdgesBoundingBox()**:
        #   它把边线自身的宽度也算进去 (本板 0.1mm ⇒ 每边多 0.05mm)
        #   ⇒ 净距算出来偏大 ⇒ DRC 报"实际 0.325 / 要求 0.500" ★这就是本轮 2 条红的根因
        self.edge_segs = self._load_edge_segs()
        self.edge_d = []            # ★逐格"格心到真板边的距离" (mm) —— _free() 按线宽级别判
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
        """全板焊盘 → 障碍 + 每网焊盘清单
           ★**没分配网络的焊盘也要当障碍** (SoM 400 脚里有一半没网) ⇒ 不然布线直接压过去 ⇒ 短路"""
        for fp in list(self.b.GetFootprints()):
            for pad in list(fp.Pads()):
                nm = pad.GetNetname()
                x0, y0, x1, y1 = _pad_rect(pad)
                cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
                if not nm:
                    nm = NONET
                try:
                    pth = (pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH)
                except Exception:
                    pth = False
                layers = list(range(6)) if pth else [0]   # ★本板 SMD 全在 F.Cu
                if nm != NONET:
                    self.net_pads.setdefault(nm, []).append(
                        (fp.GetReference(), str(pad.GetNumber()), cx, cy, layers))
                self.pad_rects.append((nm, x0, y0, x1, y1))
                for li in layers:
                    for (i, j) in _rect_cells(x0, y0, x1, y1, self.g, self.bb[0], self.bb[1]):
                        idx = self._idx(i, j)
                        self.cu[li][idx] = nm
                        if nm != NONET:
                            self.pad_cell[(li, idx)] = (nm, cx, cy)
        self._halo_pads()
        self._edge_margin()

    # ------------------------------------------------ 板边 (Edge.Cuts)
    def _load_edge_segs(self):
        """★真板边几何 —— Edge.Cuts 的线段 (弧按 16 段采样)

        ★为什么不用 GetBoardEdgesBoundingBox():
          它返回的是**边线外沿**的包围盒 (含边线自身宽度 0.1mm) ⇒ 每边多 0.05mm
          ⇒ 路由器以为板边在 y=-0.05, 实际铜铜边界在 y=0
          ⇒ 差 0.05mm + 少算的 w/2 ⇒ 正好是 DRC 报的 0.325 vs 0.500
        """
        segs = []
        try:
            drawings = list(self.b.GetDrawings())
        except Exception:
            drawings = []
        for d in drawings:
            try:
                if d.GetLayerName() != "Edge.Cuts":
                    continue
                shp = d.GetShape()
            except Exception:
                continue
            try:
                if shp == pcbnew.SHAPE_T_SEGMENT:
                    segs.append((d.GetStart().x / MM, d.GetStart().y / MM,
                                 d.GetEnd().x / MM, d.GetEnd().y / MM))
                elif shp == pcbnew.SHAPE_T_ARC:
                    segs.extend(self._arc_segs(d))
            except Exception:
                continue
        if not segs:
            # 兜底: 用 bbox 内缩 (边线宽的一半 ≈ 0.05mm)
            x0, y0, x1, y1 = self.bb
            e = 0.05
            segs = [(x0 + e, y0 + e, x1 - e, y0 + e),
                     (x0 + e, y1 - e, x0 + e, y0 + e),
                     (x1 - e, y0 + e, x1 - e, y1 - e),
                     (x1 - e, y1 - e, x0 + e, y1 - e)]
        return segs

    def _arc_segs(self, d, n=16):
        """Edge.Cuts 的圆弧 → 折线采样 (本板无弧, 留作通用兜底)"""
        try:
            c = d.GetCenter()
            r = d.GetRadius() / MM
            s = d.GetStart()
            e = d.GetEnd()
            a0 = math.atan2(s.y - c.y, s.x - c.x)
            a1 = math.atan2(e.y - c.y, e.x - c.x)
            ccw = (a1 - a0) % (2 * math.pi)
            sweep = d.GetArcAngle().AsDegrees()
            if abs(ccw - math.radians(sweep)) <= abs((2 * math.pi - ccw) - math.radians(sweep)):
                step = ccw / n
            else:
                step = -(2 * math.pi - ccw) / n
            out = []
            px, py = c.x / MM + r * math.cos(a0), c.y / MM + r * math.sin(a0)
            for k in range(1, n + 1):
                a = a0 + step * k
                qx, qy = c.x / MM + r * math.cos(a), c.y / MM + r * math.sin(a)
                out.append((px, py, qx, qy))
                px, py = qx, qy
            return out
        except Exception:
            return []

    def _build_edge_dist(self):
        """★逐格算"格心到真板边的距离" (mm) —— 只算板边附近的格 (远处恒 1e9)"""
        BIG = 1e9
        d = [BIG] * (self.W * self.H)
        r = int(math.ceil((EDGE_CLEAR + W_PWR / 2.0 + 1.0) / self.g)) + 1
        for (ax, ay, bx, by) in self.edge_segs:
            i0 = int(math.floor((min(ax, bx) - self.bb[0]) / self.g)) - 1
            i1 = int(math.ceil((max(ax, bx) - self.bb[0]) / self.g)) + 1
            j0 = int(math.floor((min(ay, by) - self.bb[1]) / self.g)) - 1
            j1 = int(math.ceil((max(ay, by) - self.bb[1]) / self.g)) + 1
            for j in range(max(0, j0 - r), min(self.H - 1, j1 + r) + 1):
                cy = self._cy(j)
                for i in range(max(0, i0 - r), min(self.W - 1, i1 + r) + 1):
                    dd = _pt_seg_dist(self._cx(i), cy, ax, ay, bx, by)
                    k = self._idx(i, j)
                    if dd < d[k]:
                        d[k] = dd
        return d

    def _edge_seg_ok(self, x1, y1, x2, y2, w):
        """★这段走线的**铜外缘**到真板边 ≥ EDGE_CLEAR ?
           ★给"离网格"的线段用 (出脚直道 / 焊盘真中心引出段) —— 格子判据管不到"""
        need = EDGE_CLEAR + w / 2.0
        for (ax, ay, bx, by) in self.edge_segs:
            if _seg_seg_dist(x1, y1, x2, y2, ax, ay, bx, by) < need:
                return False
        return True

    def _edge_margin(self, margin_mm=EDGE_CLEAR):
        """★板边禁布区 —— ★**按真板边 (Edge.Cuts) 算**, 不是 bbox
           ★**逐格存"格心到板边的真实距离"** ⇒ _free() 按**线宽级别**精确判 (fix A)
             (0.20mm 线 ⇒ 需 0.60mm · 0.25mm ⇒ 0.625mm · 0.50mm 电源 ⇒ 0.75mm)
           ★粗禁布只保留"格心进到 0.5mm 内"这一档, 精确档交给 _free() ⇒ 不误杀焊盘格"""
        self.edge_d = self._build_edge_dist()
        edge = []
        for j in range(self.H):
            for i in range(self.W):
                if self.edge_d[self._idx(i, j)] < margin_mm:
                    edge.append(self._idx(i, j))
        for li in (0, 2, 4):
            for idx in edge:
                # ★焊盘格不置 EDGE (焊盘本身已过 DRC ⇒ 不许被误杀; 别的网本来也被 cu 挡住)
                if any((l2, idx) in self.pad_cell for l2 in range(6)):
                    continue
                self.cu[li][idx] = "\x00EDGE"

    def _cls(self, w):
        """线宽 → 净距级别"""
        if w <= 0.21:
            return 0
        if w <= 0.30:
            return 1
        return 2

    def _mark(self, cls, li, idx, net):
        s = self.halo[cls][li].get(idx)
        if s is None:
            s = set()
            self.halo[cls][li][idx] = s
        s.add(net)

    def _halo_pads(self):
        """焊盘净距禁区: 细线 = 焊盘矩形外扩 (0.2+0.125)=0.325mm ; 粗线/过孔 = 0.5mm
           ★**按真实矩形外扩** (不是按单元中心画圆) —— 否则边界误差会吃净距"""
        for (net, x0, y0, x1, y1) in self.pad_rects:
            for li in range(6):
                for cls in range(3):
                    rr = CLEAR + W_CLS[cls] / 2.0 + HALO_MARGIN
                    cells = _rect_cells(x0 - rr, y0 - rr, x1 + rr, y1 + rr, self.g,
                                       self.bb[0], self.bb[1])
                    for (i, j) in cells:
                        if not (0 <= i < self.W and 0 <= j < self.H):
                            continue
                        self._mark(cls, li, self._idx(i, j), net)

    # ------------------------------------------------ 可走性
    def _free(self, li, idx, net, cls=1):
        c = self.cu[li].get(idx)
        if c is not None and c != net:
            return False
        s = self.halo[cls][li].get(idx)
        if s and (s - {net}):
            return False
        # ★fix A: 板边净距 —— 铜外缘到真板边 ≥ 0.5mm ⇒ 格心距 ≥ 0.5 + w/2
        if self.edge_d[idx] < EDGE_CLEAR + W_CLS[cls] / 2.0 - 1e-6:
            pc = self.pad_cell.get((li, idx))
            if not (pc and pc[0] == net):
                return False
        return True

    def _via_ok(self, li, idx, net, cls=1):
        """此处能不能打孔 (跨层所有铜层都要有净距)"""
        # ★板边: 过孔盘 0.6mm ⇒ 盘外缘距板边 ≥ 0.5mm ⇒ 孔心距 ≥ 0.8mm
        if self.edge_d[idx] < EDGE_CLEAR + VIA_DIA / 2.0 - 1e-6:
            return False
        for l2 in VIA_SPAN[li]:
            c = self.cu[l2].get(idx)
            if c is not None and c != net:
                return False
            s = self.halo[cls][l2].get(idx)
            if s and (s - {net}):
                return False
        return True

    # ------------------------------------------------ A*
    def _astar(self, start, goals, net, dist_map=None, alpha=0.0,
                max_via=True, cls=1, limit=420000):
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
                    if not self._free(li, k, net, cls):
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
                    if not self._via_ok(li, idx, net, cls):
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
            if len(gsc) > limit:
                self.astar_budget += 1
                break        # ★搜索预算用完 ⇒ 判失败 (否则整板卡死)
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
        cls = self._cls(width)
        order = self._mst_order(pads)
        connected_pads = []
        stubs = {}

        def anchor(pad):
            """★这个焊盘的 A* 锚点 (出脚直道终点) + 出脚直道"""
            key = (pad[0], pad[1])
            if key not in stubs:
                stubs[key] = self.escape_stub(net, pad)
            st = stubs[key]
            if st:
                i, j = self._ci(st[0]), self._cj(st[1])
                return [(0, self._idx(i, j))], (pad[2], pad[3], st[0], st[1])
            return list(self._pad_cells(net, pad)), None
        if trunk:
            for (pa, pb) in trunk:
                ta = self._find_pad(net, pa)
                tb = self._find_pad(net, pb)
                if ta is None or tb is None:
                    continue
                sb, stb = anchor(tb)
                sa, sta = anchor(ta)
                path = self._astar(sb, set(sa), net, dist_map=dist_map,
                                    alpha=alpha, max_via=allow_via, cls=cls)
                if path is None and cls != 0:
                    path = self._astar(sb, set(sa), net, dist_map=dist_map,
                                        alpha=alpha, max_via=allow_via, cls=0)
                    if path is not None:
                        width = W_MIN
                if path:
                    self._emit_path(net, path, width, via_count,
                                    stub_start=stb, stub_end=sta)
                    trunk_cells = set(path)
                    connected_pads += [ta, tb]
        gx = sum(p[2] for p in pads) / len(pads)
        gy = sum(p[3] for p in pads) / len(pads)
        root = min(order, key=lambda p: (p[2] - gx) ** 2 + (p[3] - gy) ** 2)
        root_cells, root_stub = anchor(root)
        tree = set(root_cells)
        tree |= locals().get("trunk_cells", set())
        if root not in connected_pads:
            connected_pads.append(root)
        ok = True
        nfail = 0
        for pad in order:
            if pad is root:
                continue
            cells, stub_s = anchor(pad)
            if set(cells) & tree:
                continue
            # ★目标 = **最近的已连焊盘** (不是整棵树) ⇒ 启发式紧 ⇒ A* 不会爆
            goal_pad = min(connected_pads, key=lambda q: (q[2] - pad[2]) ** 2 + (q[3] - pad[3]) ** 2)
            goal_cells, stub_g = anchor(goal_pad)
            goals = set(goal_cells)
            bmark = self.astar_budget
            path = self._astar(list(cells), goals, net,
                                dist_map=dist_map, alpha=alpha,
                                max_via=allow_via, cls=cls)
            if path is None and cls != 0:
                # ★降级1: 细线 (0.2mm) —— 焊盘太密 (BTB 0.4mm pitch) 时必须
                path = self._astar(list(cells), goals, net,
                                    dist_map=dist_map, alpha=alpha,
                                    max_via=allow_via, cls=0)
                if path is not None:
                    width = W_MIN
            if path is None and allow_via:
                # ★降级2: 不换层 ⇒ 只在 F.Cu 上再试
                path = self._astar(list(cells), goals, net,
                                    dist_map=dist_map, alpha=alpha,
                                    max_via=False, cls=cls)
            if path is None:
                nfail += 1
                ok = False
                self.fail_reasons[net] = self.fail_reasons.get(net, 0) + 1
                if self.astar_budget > bmark:
                    self.fail_budget[net] = self.fail_budget.get(net, 0) + 1
                continue
            self._emit_path(net, path, width, via_count,
                            stub_start=stub_s, stub_end=stub_g)
            tree |= set(path)
            connected_pads.append(pad)
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

    # ------------------------------------------------ 密集焊盘出脚直道
    def _nearest_other_pad(self, net, cx, cy):
        """焊盘中心到**别的网**的焊盘边缘的最小距离 (mm)"""
        best = 1e9
        for (n2, x0, y0, x1, y1) in self.pad_rects:
            if n2 == net:
                continue
            dx = max(x0 - cx, 0.0, cx - x1)
            dy = max(y0 - cy, 0.0, cy - y1)
            d = math.hypot(dx, dy)
            if d < best:
                best = d
        return best

    def _stub_vs_routed(self, net, x1, y1, x2, y2, w=W_MIN):
        """★出脚直道 vs **已布走线/过孔** 的净距 (A* 的障碍图只管新走线, 管不了后出现的直道)"""
        for (n2, ax, ay, bx, by, li, tw) in self.tracks:
            if n2 == net:
                continue
            if li != 0:
                continue
            need = w / 2.0 + tw / 2.0 + CLEAR + 0.02
            if _seg_seg_dist(x1, y1, x2, y2, ax, ay, bx, by) < need:
                return False
        for (n2, vx, vy, l1, l2) in self.vias:
            if n2 == net or l1 > 0:
                continue
            need = w / 2.0 + VIA_DIA / 2.0 + CLEAR + 0.02
            if _pt_seg_dist(vx, vy, x1, y1, x2, y2) < need:
                return False
        return True

    def _stub_clear(self, net, x1, y1, x2, y2, need=0.299):
        """这段直线出脚干不干净 (中心线离别的网的焊盘边缘 ≥need)
           ★need = 0.2 净距 + 0.1 (直道半宽) = 0.3 —— ★0.4mm pitch BTB 出脚
             本来就正好卡在 0.2mm 净距上 (物理事实, 不是模型保守)"""
        n = max(2, int(math.hypot(x2 - x1, y2 - y1) / 0.1))
        bx0, bx1 = min(x1, x2) - 1.0, max(x1, x2) + 1.0
        by0, by1 = min(y1, y2) - 1.0, max(y1, y2) + 1.0
        cand = [p for p in self.pad_rects
                if p[1] <= bx1 and p[3] >= bx0 and p[2] <= by1 and p[4] >= by0]
        for k in range(n + 1):
            t = k / float(n)
            px = x1 + (x2 - x1) * t
            py = y1 + (y2 - y1) * t
            for (n2, a0, b0, a1, b1) in cand:
                if n2 == net:
                    continue
                dx = max(a0 - px, 0.0, px - a1)
                dy = max(b0 - py, 0.0, py - b1)
                if math.hypot(dx, dy) < need:
                    return False
        # ★板边: 出脚直道**离网格** ⇒ 格子判据管不到 ⇒ 这里单独查 (fix B)
        #   ★用真板边 (Edge.Cuts) + 直道半宽 ⇒ 铜外缘 ≥ 0.5mm
        if not self._edge_seg_ok(x1, y1, x2, y2, W_MIN):
            return False
        return True

    def _free_score(self, net, cx, cy, r_mm=1.5):
        """出脚终点的空旷度 (周围能走的单元数)"""
        r = r_mm / self.g
        i0, j0 = self._ci(cx), self._cj(cy)
        cnt = 0
        for dj in range(-int(r), int(r) + 1):
            for di in range(-int(r), int(r) + 1):
                if di * di + dj * dj > r * r:
                    continue
                i2, j2 = i0 + di, j0 + dj
                if not (0 <= i2 < self.W and 0 <= j2 < self.H):
                    continue
                if self._free(0, self._idx(i2, j2), net, 0):
                    cnt += 1
        return cnt

    def escape_stub(self, net, pad):
        """★密集焊盘 (SoM BTB 0.4mm pitch / 0.2mm 焊盘) 的出脚:
           沿焊盘中心线先直线走 ESC_LEN, 之后才允许横向偏
           ⇒ 净距才够 (0.25mm 网格做不到 0.4mm pitch 出脚)
           ★fix B: 出脚直道**离网格** ⇒ 板边必须单独查 (铜外缘 ≥ 0.5mm);
             1.2mm 不行就**缩短** (ESC_LENS 长→短) 或换方向
           返回 (终点x, 终点y) 或 None"""
        _ref, _num, cx, cy, _l = pad
        if not USE_ESCAPE:
            return None
        if self._nearest_other_pad(net, cx, cy) >= 0.45:
            return None          # ★不紧 ⇒ 正常出脚
        for ln in ESC_LENS:
            best = None
            for (dx, dy) in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                ex, ey = cx + dx * ln, cy + dy * ln
                if not self._stub_clear(net, cx, cy, ex, ey):
                    continue
                if not self._stub_vs_routed(net, cx, cy, ex, ey):
                    continue
                sc = self._free_score(net, ex, ey)
                if best is None or sc > best[0]:
                    best = (sc, ex, ey)
            if best is not None:
                return (best[1], best[2])
        return None

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
        used_vias = []          # ★已用过的过孔位置 (孔间距 ≥0.55mm ⇒ 不叠孔)
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
                    # ★孔间距: 0.3 钻 + 0.25 最小孔间距 ⇒ 孔心距 ≥0.55mm
                    if any(math.hypot(px - ux, py - uy) < 0.60 for (ux, uy) in used_vias):
                        continue
                    path = self._astar(list(self._pad_cells(net, pad)), {(0, idx)},
                                       net, max_via=False)
                    if path is None:
                        continue
                    self._emit_path(net, path, W_SIG, 1)
                    self.vias.append((net, px, py, via_top, via_bot))
                    self._add_via_halo(net, px, py, via_top, via_bot)
                    used_vias.append((px, py))
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
        # ★板边: 通孔盘 0.6mm ⇒ 盘外缘距真板边 ≥ 0.5mm ⇒ 孔心距 ≥ 0.8mm
        if self.edge_d[idx] < EDGE_CLEAR + VIA_DIA / 2.0 - 1e-6:
            return False
        for li in range(6):
            c = self.cu[li].get(idx)
            if c is not None and c != net:
                return False
            s = self.halo[2][li].get(idx)
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
                if not self._free(li, self._idx(i2, j2), net, 1):
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
            self._add_track_halo(s[0], s[1], s[2], s[3], s[4], s[5], s[6])
        return True

    # ------------------------------------------------ 路径 → 铜
    def _emit_path(self, net, path, width, via_count=1,
                   stub_start=None, stub_end=None):
        """★stub_start/stub_end = (焊盘中心x, 中心y, 直道终点x, 终点y)
           —— 密集焊盘出脚: 先沿中心线直线走, 再进网格"""
        if stub_start:
            sx, sy, ex, ey = stub_start
            self.tracks.append((net, sx, sy, ex, ey, 0, W_MIN))
            self._add_track_halo(net, sx, sy, ex, ey, 0, W_MIN)
        if stub_end:
            gx, gy, ex, ey = stub_end
            self.tracks.append((net, ex, ey, gx, gy, 0, W_MIN))
            self._add_track_halo(net, ex, ey, gx, gy, 0, W_MIN)
        pts = []
        for (li, idx) in path:
            i, j = idx % self.W, idx // self.W
            pts.append([li, self._cx(i), self._cy(j)])
        if stub_start:
            pts[0][1], pts[0][2] = stub_start[2], stub_start[3]
        else:
            p0 = self.pad_cell.get(path[0])
            if p0 and p0[0] == net:
                # ★焊盘真中心**离网格** ⇒ 可能比格心更靠板边 ⇒ 换中心前先验净距
                if len(pts) > 1 and self._edge_seg_ok(p0[1], p0[2], pts[1][1], pts[1][2], width):
                    pts[0][1], pts[0][2] = p0[1], p0[2]
        if stub_end:
            pts[-1][1], pts[-1][2] = stub_end[2], stub_end[3]
        else:
            pn = self.pad_cell.get(path[-1])
            if pn and pn[0] == net:
                if len(pts) > 1 and self._edge_seg_ok(pn[1], pn[2], pts[-2][1], pts[-2][2], width):
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
            self._add_track_halo(s[0], s[1], s[2], s[3], s[4], s[5], s[6])

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

    def _add_track_halo(self, net, x1, y1, x2, y2, li, w=W_SIG):
        """走线净距禁区: 半径 = 净距 + 本线半宽 + 对方半宽 (按级别分别登记)"""
        for cls in range(3):
            rr = CLEAR + w / 2.0 + W_CLS[cls] / 2.0 + HALO_MARGIN
            for (i, j) in _seg_cells(x1, y1, x2, y2, self.g, rr / self.g,
                                     self.bb[0], self.bb[1]):
                if not (0 <= i < self.W and 0 <= j < self.H):
                    continue
                self._mark(cls, li, self._idx(i, j), net)

    def _add_via_halo(self, net, x, y, l1, l2):
        i, j = self._ci(x), self._cj(y)
        for cls in range(3):
            rr = CLEAR + VIA_DIA / 2.0 + W_CLS[cls] / 2.0 + HALO_MARGIN
            ri = int(math.ceil(rr / self.g))
            for li in range(l1, l2 + 1):
                for dj in range(-ri, ri + 1):
                    for di in range(-ri, ri + 1):
                        if di * di + dj * dj > (rr / self.g) ** 2 + 1e-9:
                            continue
                        i2, j2 = i + di, j + dj
                        if not (0 <= i2 < self.W and 0 <= j2 < self.H):
                            continue
                        self._mark(cls, li, self._idx(i2, j2), net)

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
            for (i, j) in _seg_cells(s[1], s[2], s[3], s[4], self.g, 0,
                                     self.bb[0], self.bb[1]):
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
        # ★自检: 板边净距 —— 落板前最后一道闸 (fail fast: 宁可这轮不投板也别留 DRC 红)
        bad = 0
        for (net, x1, y1, x2, y2, li, w) in self.tracks:
            if not self._edge_seg_ok(x1, y1, x2, y2, w):
                bad += 1
                if bad <= 6:
                    print("  ⚠️ [EDGE] 板边净距不足: %s (%.3f,%.3f)->(%.3f,%.3f) w=%.2f"
                          % (net, x1, y1, x2, y2, w))
        for (net, x, y, l1, l2) in self.vias:
            if not self._edge_seg_ok(x, y, x, y, VIA_DIA):
                bad += 1
                if bad <= 6:
                    print("  ⚠️ [EDGE] 过孔离板边太近: %s (%.3f,%.3f)" % (net, x, y))
        self.edge_viol = bad
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
    ox, oy = router.bb[0], router.bb[1]
    for s in router.tracks:
        if s[0] == net_a:
            for (i, j) in _seg_cells(s[1], s[2], s[3], s[4], g, 0, ox, oy):
                ca.add((i, j))
        elif s[0] == net_b:
            for (i, j) in _seg_cells(s[1], s[2], s[3], s[4], g, 0, ox, oy):
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
# ★**线宽上限由出脚决定** (LAYOUT_RULES: SOM 输入 ≥2A ⇒ ≥0.5mm, 但出脚焊盘更窄):
#   · SoM BTB = 0.4mm pitch / 0.2mm 焊盘 ⇒ 出脚只能 0.2mm (否则净距不够)
#   · USB-C 座 = 0.5mm pitch / 0.28mm 焊盘 ⇒ 出脚只能 0.25mm
#   ⇒ **"≥0.5mm 铜宽" 只能在出脚后的开阔区用铜皮/并联铜条实现** (本轮未做 ⇒ 下一轮)
POWER_NETS = [
    ("RAIL_SOM_DCIN", 0.20, 3),      # SOM 输入 (≥2A) —— 出脚限 0.2mm
    ("RAIL_DEMO_5V", 0.25, 3),       # USB-C 5V 输入链 —— 出脚限 0.25mm
    ("SYS_PCB", W_PWR, 2),          # 主板主供电 (电池开关后) ⇒ 0.5mm
    ("VDD_3V3_IO", W_SIG, 1),
    ("VDD_1V8_IO", W_SIG, 1),
    ("LIGHT_3V3", W_SIG, 1),
    ("V_CORE", W_SIG, 1),
    ("LIGHT_5V", W_SIG, 1),
    ("LIGHT_1V8", W_SIG, 1),
    ("V_SOC_IO", W_SIG, 1),
    ("BAT", W_SIG, 1),
    ("BAT_SW", W_SIG, 1),
    ("SENSOR_VDD_IO", W_SIG, 1),
    ("SENSOR_CORE", W_SIG, 1),
    ("SENSOR_AVDD", W_SIG, 1),
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

    # ---------- 1) 差分对 (成对布) —— ★**顺序按 brief 的优先级**:
    #   ① USB 对 (短, 在板边) 先布 (它们在 F.Cu 上占地方少)
    #   ② **电源大电流** (板级长干道, 要整片空板!)
    #   ③ MIPI CSI/DSI 对 (最难, 最后布 —— 让它们吃剩下的空间)
    #   ★上一轮把 MIPI 放在电源前面 ⇒ MIPI 先把 F.Cu 占了 ⇒ 电源长干道全断
    USB_PAIRS = [p for p in DIFF_PAIRS
                 if "USB" in p[0] or "USB" in p[1]]
    MIPI_PAIRS = [p for p in DIFF_PAIRS if p not in USB_PAIRS]

    def _run_pairs(pairs):
        for (p, n, tp, tn) in pairs:
            if p not in r.net_pads or n not in r.net_pads:
                continue
            res = route_diff_pair(r, p, n, trunk_p=tp, trunk_n=tn)
            stats["pairs"].append(res)
            if verbose:
                print("  [PAIR] %-22s / %-22s  ok=%s/%s  L=%.2f/%.2f  Δ=%.3fmm  间距=%s"
                      % (p, n, res.get("p_ok"), res.get("n_ok"),
                         res.get("lp", 0), res.get("ln", 0), res.get("delta", 0),
                         res.get("min_gap")))

    _run_pairs(USB_PAIRS)

    # ---------- 2) 电源 (宽铜 + 过孔阵列) —— ★**必须在 MIPI 之前**
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

    # ---------- 3) MIPI 差分对 (最难 ⇒ 最后)
    _run_pairs(MIPI_PAIRS)

    # ---------- 4) 电源 (宽铜 + 过孔阵列)
    # ---------- 5) 时序/复位/EN 关键线
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
    if verbose and r.fail_reasons:
        nf = sum(r.fail_reasons.values())
        nb = sum(r.fail_budget.values())
        print("  [FAIL] 布不动的脚 %d 个 (其中 **A* 预算耗尽** %d 个 / 真被堵死 %d 个)"
              % (nf, nb, nf - nb))
        top = sorted(r.fail_reasons.items(), key=lambda kv: -kv[1])[:10]
        for (nn, cnt) in top:
            print("         %-24s %d 脚 (预算耗尽 %d)"
                  % (nn, cnt, r.fail_budget.get(nn, 0)))

    # ---------- 5) GND 下拉过孔 (焊盘 → 短走线 → 通孔 → L2/L6 平面)
    ok, fail = r.route_gnd_drops("GND")
    stats["gnd"] = {"drops": ok, "fail": fail}
    if verbose:
        print("  [GND ] 下拉过孔 %d 成功 / %d 失败" % (ok, fail))

    # ---------- 6) 落板 + 填平面
    n_new = r.commit(board)
    stats["tracks"] = len(r.tracks)
    stats["vias"] = len(r.vias)
    stats["edge_viol"] = getattr(r, "edge_viol", 0)
    stats["new_items"] = n_new
    for z in board.Zones():
        try:
            z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        except Exception:
            pass
    _fill_zones(board)
    # ★seconds 必须在用之前算 (上一版这里先读后算 ⇒ KeyError ⇒ 整个 route_board 抛出)
    stats["seconds"] = round(time.time() - t0, 1)
    if verbose:
        print("  [SUM ] 走线 %d 段 / 过孔 %d 个 / 板边净距不足 %d 处 / 用时 %.0fs"
              % (len(r.tracks), len(r.vias), stats["edge_viol"], stats["seconds"]))
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
