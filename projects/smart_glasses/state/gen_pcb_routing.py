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
import os
from collections import defaultdict

import pcbnew

MM = 1e6

# ------------------------------------------------------------------ 常量
GRID = 0.25            # mm 网格步长
CLEAR = 0.20           # mm 铜间距 (KiCad 默认)
# ★★2026-11-05 07:45 **做成可调** (实验臂用)
#   ★理论下限: 栅格 0.25mm ⇒ 半格 0.125 ⇒ 0.125 就够 (当前 0.20 偏保守 ⇒ 多阻 ~18% 面积)
#   ★**改小会放松净距保护 ⇒ 必须盯 DRC** ⇒ 只在实验臂里试, 验过 DRC 才准进正式轮
HALO_MARGIN = float(os.environ.get("PCB_HALO_MARGIN", "0.20"))
                        # ★★2026-11-04 22:35 项目总工改: 0.07 → 0.20 —— 上一轮 DRC 实测净距 0.175 < 要求 0.200
                        #   ⇒ ★**半格量化损失没被补回来** ⇒ 余量必须 ≥ 半格 (0.125) + 富余 ⇒ 0.20
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
VIA_DRILL = 0.30       # mm 过孔钻 ★★2026-11-04 22:45 **必须 ≥ 板子设计规则的最小钻孔 (0.300mm)**
# ★★2026-11-05 07:40 **小焊盘用的缩小过孔** (0402/0603 电容电阻的 GND 焊盘只有 0.6mm 宽)
#   ⇒ 焊盘内过孔用 Ø0.60 放不下 (判据 min(w,h)<0.70 把它们全杀了 ⇒ 11 个 GND 焊盘一根铜都没有)
#   ⇒ 改用 Ø0.50/钻0.30 (环宽 0.10mm) ⇒ 0.6mm 宽的焊盘**放得下** (边距 0.05mm/边)
VIA_DIA_S = 0.50
VIA_DRILL_S = 0.30
#   ⇒ 上一轮改成 0.25mm 是错的: 板 setup 的 min hole = 0.3mm ⇒ ★**199 条 drill_out_of_range**
#   ⇒ 回退 0.30mm, 孔到孔 0.25mm 的问题改用"过孔中心间距"来解 (见 _via_too_close)
# ★★2026-11-04 23:50 **过孔中心间距下限** (孔到孔净距 0.25mm ⇒ 0.15+0.25+0.15 = 0.55mm)
#   ⇒ 取 0.58mm (0.03 余量)
#   ★★**这条必须同时管到 A\* (换层点) 和落铜 (过孔实际摆放)** ——
#   上一版只有落铜时查 (_via_too_close) ⇒ ★**A\* 会规划"根本放不下过孔的换层点"**
#   ⇒ 落铜时过孔被跳过 ⇒ ★**层间过渡段两端没落到过孔上** ⇒ 5 条 track_dangling 的根因
MIN_VIA_CENTER = 0.58  # mm 过孔中心距 (同网/异网都算: 孔到孔是制造规则)

# ★差分对走廊圈数 (格) —— ★**2 格 = 0.50mm**
#   ★理由: 差分对的两根线要**平行等距** (100Ω) ⇒ N 必须能贴着 P 走
#   ★但 P 的 halo 半径 0.65mm ⇒ N 至少要离 P 的铜箔 0.65mm
#   ⇒ ★**改用几何精确判断**: 中心距 0.50mm ⇒ 净距 0.25mm ≥ 0.2 ✓ DRC 干净
#   ⇒ ★**2 圈比 3 圈给 N 多 0.25mm 的活动空间** ⇒ 实测能多布出好几对
PAIR_RING = 2

# ★★2026-11-05 06:15 **修: 层数可配 ⇒ CU_LAYERS 必须跟着层数走**
#   原来写死 6 项 ⇒ 8 层时 li=6 (In6.Cu) ⇒ `CU_LAYERS[li]` 越界 IndexError
#   ⇒ ★**8 层那轮的布线结果被整个吞掉** (实测那轮只剩 78 个脚布不动, 比 6 层的 101 好, 但成绩作废)
#   ⇒ 8 层物理叠层: L1 F.Cu 信号 / L2 In1.Cu GND / L3 In2.Cu 信号 / L4 In3.Cu (空)
#                    L5 In4.Cu 信号 / L6 In5.Cu (空) / L7 In6.Cu 信号 / L8 B.Cu GND
NLAYERS = int(os.environ.get("PCB_LAYERS", 6))
# ★★2026-11-05 07:42 **层数通吃** (6/8/10 层) ⇒ 别再手写列表
#   ★10 层: F.Cu + In1..In8 + B.Cu ⇒ 信号层 F.Cu/In2/In4/In6/In8, 平面 In1/In3/In5/In7/B.Cu
_CU = [pcbnew.F_Cu]
for _i in range(1, max(NLAYERS - 1, 2)):
    _CU.append(getattr(pcbnew, "In%d_Cu" % _i))
_CU.append(pcbnew.B_Cu)
CU_LAYERS = _CU[:NLAYERS] if NLAYERS <= len(_CU) else _CU
# ★允许走信号的层: L1 / L3 / L5 (索引 0 / 2 / 4)
# ★★2026-11-05 04:10 层数可配 (环境变量 PCB_LAYERS): ★**6 层布不通 ⇒ 试 8 层**
#   动机 (实测): 186 器件 / 400 个 0.4mm pitch BTB 焊盘 ⇒ 3 个信号层的 escape 面积不够
#   ⇒ 路由器每轮把 unconnected 卡在 ~90 (剩下的都在 SoM BTB 密集区)
#   ⇒ ★Forlinx 官方载板是 **10 层** ⇒ 6 层本来就是低估 ⇒ ★**加层 = 加 escape 面积**
#   ★6 层: 信号 L1/L3/L5 · 平面 L2(GND)/L6(B.Cu=In5? 见 STACKUP: L2/L6 为 GND 平面)
#   ★8 层: 信号 L1/L3/L5/L7(In6.Cu) · GND 平面仍在 L2/L6 ⇒ ★多一整层 escape 面积
NLAYERS = int(os.environ.get("PCB_LAYERS", 6))
NLAYERS = int(os.environ.get("PCB_LAYERS", 6))
# ★★2026-11-05 07:40 **层数通吃** (★官方载板本身就是 10 层 ⇒ 一直只测到 8 层是低估)
#   ★信号层 = 偶数层 (0=F.Cu, 2, 4, ...) 但**不含最后一层** (B.Cu 留给 GND 平面)
#   ★6 层 ⇒ [0,2,4] · 8 层 ⇒ [0,2,4,6] · 10 层 ⇒ [0,2,4,6,8]
ROUTE_LAYERS = [li for li in range(0, NLAYERS, 2) if li != NLAYERS - 1]
# ★**信号层之间的邻接表** (★稀疏层号 ⇒ 不能用 li±1!)
#   L1↔L3 (过孔跨 In1.Cu 平面) · L3↔L5 (过孔跨 In3.Cu 平面) · L5↔L7 (过孔跨 In5.Cu 平面)
RLAY_NBRS = {0: (2,), 2: (0, 4), 4: (2, 6) if NLAYERS >= 8 else (2,)}
if NLAYERS >= 8:
    RLAY_NBRS[6] = (4,)
# ★★2026-11-05 07:42 **邻接表跟着层数走** (10 层 ⇒ 8 号信号层也要接 6 号)
for _li in ROUTE_LAYERS:
    _nb = []
    for _d in (-2, 2):
        _j = _li + _d
        if 0 <= _j < NLAYERS and _j in ROUTE_LAYERS:
            _nb.append(_j)
    RLAY_NBRS[_li] = tuple(_nb)


def _via_span(la, lb):
    """过孔穿过的铜层 (含中间平面层) —— ★只允许相邻信号层 ⇒ 只跨一层平面"""
    lo, hi = (la, lb) if la < lb else (lb, la)
    return tuple(range(lo, hi + 1))

# ★每格的层偏好代价 (0 = 首选); 换层代价 (格)
# ★**本轮调低**: 上一轮 80 个过孔 ⇒ 整板 99% 走线都挤在 F.Cu ⇒ 局部通道堵死
#   ⇒ 跨层几乎不要钱 (8 格 ≈ 2mm 线) ⇒ 3 个信号层一起用 ⇒ 可走面积 ≈ 3 倍
LAYER_COST = {0: 0.0, 2: 0.25, 4: 0.50}
if NLAYERS >= 8:
    LAYER_COST[6] = 0.75
VIA_COST = 8.0

# 层间跳 (相邻信号层): 换层时经过的铜层 (含中间平面层, 孔要穿过去 ⇒ 必须留间距)
VIA_SPAN = {0: (0, 1, 2), 1: (2, 3, 4)}

LNAME = {0: "L1/F.Cu", 1: "L2/In1.Cu", 2: "L3/In2.Cu",
         3: "L4/In3.Cu", 4: "L5/In4.Cu", 5: "L6/B.Cu"}
if NLAYERS >= 8:
    LNAME.update({6: "L7/In6.Cu", 7: "L8/B.Cu"})
# ★★2026-11-05 07:42 **10 层支持** ⇒ 层名表跟层数走 (L9/In8.Cu / L10/B.Cu)
if NLAYERS > 8:
    for _i in range(8, NLAYERS):
        if _i == NLAYERS - 1:
            LNAME[_i] = "L%d/B.Cu" % (_i + 1)
        else:
            LNAME[_i] = "L%d/In%d.Cu" % (_i + 1, _i)


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


def _ring_offsets(rr):
    """★半径 rr (格) 的环上的格偏移 (按距离从近到远)
       —— 用于"从被封死的焊盘往外找能起步的格子\""""
    out = []
    ri = int(math.ceil(rr))
    for dj in range(-ri, ri + 1):
        for di in range(-ri, ri + 1):
            if di == 0 and dj == 0:
                continue
            d = math.hypot(di, dj)
            if d <= rr + 1e-9:
                out.append((d, di, dj))
    out.sort()
    return [(di, dj) for (_d, di, dj) in out]


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
        self.cu = [dict() for _ in range(NLAYERS)]
        # ★halo[cls][li][idx] = 该单元被哪些网的铜"占了净距"
        #   cls0=0.20mm / cls1=0.25mm / cls2=0.50mm 三套规则各存一份
        self.halo = [[dict() for _ in range(NLAYERS)] for _ in range(3)]
        self.net_pads = {}          # net -> [(ref, padnum, cx, cy, layers)]
        self.pad_rects = []         # (net, x0,y0,x1,y1) —— 过孔不许打进焊盘
        self.pad_rects_l = []       # ★(net, x0,y0,x1,y1, layers) —— ★**焊盘只在它实际存在的层上有铜**
        self.pad_cell = {}          # (li,idx) -> (net, true_cx, true_cy)
        self.routed = set()
        # ★诊断计数器: 布不动的网到底是"预算用完"还是"真被堵死"
        self.astar_budget = 0
        self.astar_blocked = 0
        self.fail_reasons = {}
        self.fail_budget = {}
        self.fail_detail = []
        # ★真板边几何 (Edge.Cuts) —— ★**不能用 GetBoardEdgesBoundingBox()**:
        #   它把边线自身的宽度也算进去 (本板 0.1mm ⇒ 每边多 0.05mm)
        #   ⇒ 净距算出来偏大 ⇒ DRC 报"实际 0.325 / 要求 0.500" ★这就是本轮 2 条红的根因
        self.edge_segs = self._load_edge_segs()
        self.edge_d = []            # ★逐格"格心到真板边的距离" (mm) —— _free() 按线宽级别判
        self.tracks = []            # (net, x1,y1,x2,y2,li,width)
        self.vias = []              # (net, x, y, l1, l2)
        self.via_cells = {}         # ★格 → 该格附近的过孔坐标 (同网孔间距检查用)
        # ★★2026-11-05 **过孔邻近的粗粒度空间哈希** (1mm 格)
        #   ★_via_too_close 在 A* 里被调用**几十万次** ⇒ 逐格 (7×7=49) 查太慢
        #   ⇒ 改查 1mm 粗格 (3×3=9 次查) ⇒ 提速 ~5 倍, 结果完全一样
        self.via_hash = {}           # (cx, cy) → [(x, y), ...]
        # ★★2026-11-05 **差分对耦合布线参数** (★P/N 成对走线时临时生效)
        self.pair_partner = None     # ★伙伴网的网名 (差分对耦合时生效)
        self.pair_block = set()      # ★离伙伴铜箔太近的格 (几何精确) ⇒ 不许走
        self.pair_min = 0.50         # ★mm 差分对中心距下限 (0.25mm 线 ⇒ 净距 0.25 ≥ 0.2)
        self.pair_fallback = 0       # ★耦合失败后退化为"无耦合"的次数 (★要写进报告)
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
                    attr = pad.GetAttribute()
                except Exception:
                    attr = pcbnew.PAD_ATTRIB_SMD
                # ★★2026-11-05 06:25 **修: NPTH (无网络安装孔) 必须是**所有层**的障碍**
                #   原来只认 PAD_ATTRIB_PTH ⇒ NPTH 只算 F.Cu 一层 ⇒ ★**In2.Cu 的走线直接从孔里穿过去**
                #   ⇒ 实测: v21 的 25 条 DRC 违规 **全部**是 hole_clearance
                #   (JTAG_TMS / JTAG_TDI 压到 USB-C 的 NPTH 安装孔, 板边 x≈134.2, y≈2.6)
                #   ⇒ 孔是**贯穿所有层**的 ⇒ 每一层都得当障碍
                pth = attr in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
                is_npth = (attr == pcbnew.PAD_ATTRIB_NPTH)
                layers = list(range(NLAYERS)) if pth else [0]   # ★本板 SMD 全在 F.Cu
                if nm != NONET:
                    self.net_pads.setdefault(nm, []).append(
                        (fp.GetReference(), str(pad.GetNumber()), cx, cy, layers))
                self.pad_rects.append((nm, x0, y0, x1, y1))
                self.pad_rects_l.append((nm, x0, y0, x1, y1, tuple(layers)))
                # ★NPTH 孔还要额外让开 **孔净距** (板规则 0.25mm) ⇒ 不然走线贴孔边照样违规
                if is_npth:
                    HOLE_CLR = 0.25
                    x0, y0, x1, y1 = (x0 - HOLE_CLR, y0 - HOLE_CLR,
                                      x1 + HOLE_CLR, y1 + HOLE_CLR)
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
        for li in ROUTE_LAYERS:
            for idx in edge:
                # ★焊盘格不置 EDGE (焊盘本身已过 DRC ⇒ 不许被误杀; 别的网本来也被 cu 挡住)
                if any((l2, idx) in self.pad_cell for l2 in range(NLAYERS)):
                    continue
                self.cu[li][idx] = "\x00EDGE"

    def _cls(self, w):
        """线宽 → 净距级别"""
        if w <= 0.21:
            return 0
        if w <= 0.30:
            return 1
        return 2

    def _mark(self, cls, li, idx, net, skip_pad_cells=False):
        """★**登记净距禁区**
        ★★2026-11-05 07:50 **skip_pad_cells: halo 不许盖住别的网的焊盘格**
          ⇒ 实测 (只读审计): 78 个失败脚里 14 个真被"同层异网铜"封死, 其中 ★**7 个是
            CONN_CAM/CONN_LIGHT 的信号脚, 最近的异网铜是 0.5mm 处的 GND** ⇒ 落在 halo 半径
            0.525mm 内 ⇒ ★**信号脚自己的起步格被封 ⇒ A* 一步都走不出去**
          ⇒ ★**焊盘自己的 halo (焊盘矩形外扩 rr) 已经守住了它的邻域** ⇒ 别的网再盖一层纯属多余
          ⇒ ★而且物理上就该这样: 焊盘是真实铜, 它的净距由它自己的 halo 管
          ⇒ ★**焊盘格在 cu 里已被它自己的网占住** ⇒ 别的网本来就走不进去 ⇒ 不会引入短路
        """
        if skip_pad_cells:
            pc = self.pad_cell.get((li, idx))
            if pc is not None and pc[0] != net:
                return
        # ★★2026-11-05 07:52 **越界层护栏** (★层号越界会让整轮布线炸掉 ⇒ 宁可跳过)
        if li < 0 or li >= len(self.halo[cls]):
            return
        s = self.halo[cls][li].get(idx)
        if s is None:
            s = set()
            self.halo[cls][li][idx] = s
        s.add(net)

    def _halo_pads(self):
        """焊盘净距禁区: 细线 = 焊盘矩形外扩 (0.2+0.125)=0.325mm ; 粗线/过孔 = 0.5mm
           ★**按真实矩形外扩** (不是按单元中心画圆) —— 否则边界误差会吃净距
           ★★**焊盘只在它实际存在的层上占净距** —— SMD 焊盘只在 F.Cu
             ⇒ 上一版把它记到全部 6 层 ⇒ ★L3/L5 整层被焊盘禁区封死
             ⇒ 板子 99% 只能走 F.Cu ⇒ 局部通道堵死 (本轮 179 脚布不通的根因)"""
        for (net, x0, y0, x1, y1, layers) in self.pad_rects_l:
            for li in layers:
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
            others = s - {net}
            # ★★2026-11-05 **差分对耦合**: 伙伴(P)的 halo **不当障碍**
            #   ★**为什么**: 差分对的 N 侧必须**贴着 P 侧平行走** (100Ω 等长/等距)
            #   ⇒ 若把 P 的 halo 当障碍 ⇒ N 永远跑不到 P 旁边 ⇒ ★**P 走了通道, N 无路可走**
            #   ★**怎么豁免才安全**: 用**几何精确距离**判断, 而不是 halo 的保守栅格半径
            #   ⇒ ★`_pair_block` = 离 P 铜箔 < pair_min 的格 (几何精确) ⇒ 只禁真正会短路的
            if not (self.pair_partner and others == {self.pair_partner}
                    and idx not in self.pair_block):
                return False
        # ★★2026-11-05 02:35 修 (实测 12 条 copper_edge_clearance): **板外的格子一律不许走**
        #   ★**根因**: 下面的"自己网的焊盘所在格"豁免了板边检查 ⇒ 靠边的焊盘 (如安装孔 GND 焊盘)
        #   ⇒ 出脚直道可以从那个格起步 ⇒ ★**直接走到板外** (实测: GND 段 (3.700,-0.050)→(3.700,0.200) 在板外!)
        #   ⇒ edge_d < 0 = 格心在板外 ⇒ 直接禁掉 (对任何网都禁, 含自己的焊盘)
        if self.edge_d[idx] < 0:
            return False
        # ★fix A: 板边净距 —— 铜外缘到真板边 ≥ 0.5mm ⇒ 格心距 ≥ 0.5 + w/2
        if self.edge_d[idx] < EDGE_CLEAR + W_CLS[cls] / 2.0 - 1e-6:
            pc = self.pad_cell.get((li, idx))
            if not (pc and pc[0] == net):
                return False
        return True

    def _path_len(self, path):
        """路径总长 (mm) —— ★GND 缝合的长度闸用它
           ★path 元素是 (li, idx) ⇒ 坐标要按 _emit_path 同样的方式换算 (格心坐标)"""
        if not path:
            return 0.0
        pts = []
        for (li, idx) in path:
            i, j = idx % self.W, idx // self.W
            pts.append((self._cx(i), self._cy(j)))
        total = 0.0
        for k in range(1, len(pts)):
            total += math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1])
        return total

    def _via_ok(self, la, lb, idx, net, cls=1):
        """此处能不能打孔 (跨层所有铜层都要有净距)
           ★**用 halo[2] (0.5mm 宽铜的净距级别) 判** —— 过孔盘 0.6mm 比 0.25mm 线粗
             ⇒ 用 cls1 的净距会漏判 ⇒ 过孔挨着别的网的线 ⇒ DRC 报 clearance
           ★★**过孔一律按"通孔"判 (贯穿 6 层)** —— 因为 commit() 里 SetViaType(THROUGH)
             会把层对强制成 (F.Cu,B.Cu) ⇒ 过孔环在 6 层都有铜
             ⇒ 只查 la..lb 两层 ⇒ **过孔会撞上内层别的网的铜 ⇒ DRC 短接**
             ⇒ ★所以这里必须查**全部 6 层** (且 _add_via_halo 也要记 6 层)"""
        # ★板边: 过孔盘 0.6mm ⇒ 盘外缘距板边 ≥ 0.5mm ⇒ 孔心距 ≥ 0.8mm
        if self.edge_d[idx] < EDGE_CLEAR + VIA_DIA / 2.0 - 1e-6:
            return False
        # ★**不许把过孔打在焊盘底下** (via-in-pad) —— 0402/0603 上的过孔 = 吸锡风险
        #   = 投板后必须手工补焊 ⇒ 返工项。★孔要躲开焊盘, 就得先在 F.Cu 上走一段
        if (0, idx) in self.pad_cell:
            return False
        # ★★2026-11-04 23:50 **孔到孔间距 (制造规则) 必须在 A\* 规划时就查**
        #   板 setup: m_HoleToHoleMin = 0.25mm ⇒ 0.3 钻的孔心距 ≥ 0.55mm (取 0.58)
        #   ★★**上一版只有"落铜时"查 (_via_too_close) ⇒ A\* 会规划"根本放不下过孔的换层点"**
        #   ⇒ 落铜时过孔被跳过 ⇒ ★**层间过渡段的两端没落到过孔上** ⇒ 5 条 track_dangling 的根因
        #   ⇒ ★**这里加上 ⇒ A\* 直接绕开非法换层点** (既治 DRC 又提连通率)
        i, j = idx % self.W, idx // self.W
        if self._via_too_close(net, self._cx(i), self._cy(j)):
            return False
        for l2 in range(NLAYERS):
            c = self.cu[l2].get(idx)
            if c is not None and c != net:
                return False
            s = self.halo[2][l2].get(idx)
            if s and (s - {net}):
                return False
        return True

    # ------------------------------------------------ A*
    def _astar(self, start, goals, net, dist_map=None, alpha=0.0,
                max_via=True, cls=1, limit=0, dist_def=0):
        """start: [(li,idx)] ; goals: set((li,idx))
           ★★**预算按"扩展次数"算, 不是按状态数算** —— 状态数是 (格 × 层),
             开了 3 个信号层后同一个物理区域的状态数 ×3 ⇒ 用状态数当预算
             ⇒ 搜索半径被悄悄砍到 1/3 ⇒ 该通的线也布不出来
             ★扩展次数 = 物理覆盖面积 ⇒ 与层数无关 ⇒ 换层后行为稳定

           ★★2026-11-04 **启发式加上"层差代价"** ——
             原来的 h 只算"到目标包围盒的平面距离" ⇒ **完全不知道换层要花钱**
             ⇒ A* 会在 3 个信号层之间反复横跳 ⇒ ★**预算 (15 万次扩展) 很快烧光**
             ⇒ 实测 82 个失败脚里 **52 个是"预算耗尽"** (不是真堵死)
             ⇒ 现在 h 额外加上"最少要换几次层 × VIA_COST" ⇒ ★**搜索方向正确 ⇒ 又快又通**

           ★★2026-11-05 **预算按路径长度自适应** ——
             实测: 失败脚里 **44/81 是"预算耗尽"**, 而这些网的路径长度中位数 **56mm**!
             ⇒ ★**短网 15 万次扩展够, 长网不够** ⇒ 固定预算 ⇒ 长网必失败
             ⇒ 现在: 按"起终点的曼哈顿距离"给预算 (短网省时间, 长网给够)"""
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
        # ★目标可能在哪几层 (层差 ⇒ 至少要换几次层)
        goal_lis = sorted(set(l for (l, k) in goals))
        # ★**预计算每个目标层的"距当前层多远"** (★否则每次 h_of 都重算 min ⇒ 慢)
        lay_tab = {}
        # ★2026-11-05 04:58: 层集合从固定的 (0,2,4) 改成 **ROUTE_LAYERS** (8 层时含 6)
        #   ⇒ lay_tab 与 lay_min 的长度都随层数变 ⇒ ★**原来固定 range(3) ⇒ 8 层时 lay_min[3] 越界**
        #   (实测 8 层实验直接崩: "list index out of range")
        for gl in goal_lis:
            lay_tab[gl] = [abs(li - gl) // 2 for li in ROUTE_LAYERS]
        lay_min = [min(lay_tab[gl][k] for gl in goal_lis) for k in range(len(ROUTE_LAYERS))]

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
            plan = (dx + dy) + (math.sqrt(2.0) - 1.0) * min(dx, dy)
            # ★换层代价 (可采纳: 每次换层至少花 VIA_COST)
            return plan + lay_min[li // 2] * VIA_COST

        cnt = 0
        for s in start:
            gsc[s] = 0.0
            heapq.heappush(heap, (h_of(s[0], s[1]), 0.0, cnt, s))
            cnt += 1
        goalset = set(goals)
        # ★★2026-11-05 **预算按路径长度自适应** (★长网需要更多扩展)
        #   曼哈顿距离 (格) × 系数 + 底数 ⇒ 短网省时间, 长网给够
        if limit is None or limit <= 0:
            dist_cells = 0
            for (sli, sidx) in start:
                si, sj = sidx % self.W, sidx // self.W
                for (gli, gidx) in goals:
                    gi, gj = gidx % self.W, gidx // self.W
                    d = abs(si - gi) + abs(sj - gj)
                    if d > dist_cells:
                        dist_cells = d
            # ★★2026-11-05 05:30 **A* 预算可调** (环境变量 PCB_ABUDGET_MULT, 默认 1)
        #   ★依据 (实测 v12 的失败分类): 80 个布不动的脚里, **39 个是"A* 预算耗尽"**, 只有 41 个是真被堵死
        #   ⇒ ★**预算才是主要瓶颈之一** (不是几何) ⇒ 放大预算能把这 39 个变成"布出来了"
        #   ⇒ 代价: A* 扩展更多 ⇒ 更慢 ⇒ 用环境变量按需调, 不做死
        _mult = float(os.environ.get("PCB_ABUDGET_MULT", "1"))
        limit = int(min(900000 * _mult, max(150000 * _mult, dist_cells * 900 * _mult)))
        best = None
        nexp = 0
        while heap:
            f, gg, _, cur = heapq.heappop(heap)
            if gg > gsc.get(cur, INF) + 1e-12:
                continue
            nexp += 1
            if nexp > limit:
                self.astar_budget += 1
                break        # ★搜索预算用完 ⇒ 判失败 (否则整板卡死)
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
                        # ★★2026-11-05 **走廊外的格不再是"免费"** ——
                        #   原版 `dist_map.get(k, 0)` ⇒ 不在图里的格代价 0
                        #   ⇒ ★**远处反而比走廊便宜** ⇒ N 会逃出走廊
                        #   ⇒ 现在: 用 `dist_def` (走廊外的代价值) ⇒ ★N 留在走廊里
                        c += alpha * dist_map.get(k, dist_def)
                    if c < gsc.get((li, k), INF):
                        gsc[(li, k)] = c
                        came[(li, k)] = cur
                        heapq.heappush(heap, (c + h_of(li, k), c, cnt, (li, k)))
                        cnt += 1
            if max_via:
                # ★**换层只能到相邻信号层** (L1↔L3 / L3↔L5) —— ★**不能用 li±1**
                #   (ROUTE_LAYERS 是稀疏列表 [0,2,4] ⇒ li±1 永远是 1/3/5 ⇒ 根本换不了层
                #    ⇒ 上一轮整板 80 个过孔全部来自 GND 下拉 ⇒ 布线全挤在 F.Cu)
                for nli in RLAY_NBRS.get(li, ()):
                    if not self._via_ok(li, nli, idx, net, cls):
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
            if len(gsc) > 4000000:
                break        # ★内存保险丝 (状态数上限, 与覆盖无关)
        if best is None:
            return None
        path = [best]
        while path[-1] in came:
            path.append(came[path[-1]])
        path.reverse()
        return path

    # ------------------------------------------------ 单网多焊盘
    def route_net(self, net, width=W_SIG, allow_via=True, dist_map=None,
                  alpha=0.0, via_count=1, trunk=None, dist_def=0,
                  profiles=None):
        """布一个多焊盘网 —— 最小生成树顺序逐个并入一棵树
           trunk: ((padA, padB),) —— 先布的"主干"焊盘对 (差分对用它对齐走向)
           profiles: ★[(guide_map, dist_def, ring), ...] —— ★**逐脚渐次放宽的走廊档位**
             (差分对用: 紧的走廊不通就换松的 ⇒ ★**在同一棵树里重试 ⇒ 不重复布线**)
           返回 dict(ok/段数/长度mm/失败焊盘数)"""
        pads = self.net_pads.get(net)
        if not pads or len(pads) < 2:
            return {"ok": True, "segs": 0, "len": 0.0, "fail": 0, "net": net}
        cls = self._cls(width)
        order = self._mst_order(pads)
        connected_pads = []
        stubs = {}
        nfail_trunk = 0
        ring_used = None

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
                                    alpha=alpha, max_via=allow_via, cls=cls,
                                    dist_def=dist_def)
                if path is None and cls != 0:
                    path = self._astar(sb, set(sa), net, dist_map=dist_map,
                                        alpha=alpha, max_via=allow_via, cls=0)
                    if path is not None:
                        width = W_MIN
                if path:
                    # ★★2026-11-04 23:58 **换层点过孔落不下 ⇒ 整条路径放弃** (不留断铜)
                    if not self._emit_path(net, path, width, via_count,
                                           stub_start=stb, stub_end=sta):
                        nfail_trunk = nfail_trunk + 1
                        continue
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
            path = None
            used_ring = None
            if profiles:
                # ★★★2026-11-05 **逐档放宽走廊 (★在同一棵树里重试 ⇒ 不重复布线)**
                #   ★profiles = [(guide_map, dist_def, ring), ...] ⇒ ring 2 → 4 → 6 → 8
                #   ★**为什么**: 差分对要求 N 贴着 P 走 ⇒ 走廊窄 ⇒ 长距离 (100~240mm) 极易被单点堵死
                #   ⇒ ★**不通就放宽一档** ⇒ ★既保住"贴着 P"的大方向, 又给 N 留出活路
                #   ★**放宽过档的要计数** ⇒ 报告里点名哪些对不是最紧的 (不假装是 100Ω)
                for (pguide, pdef, pring) in profiles:
                    path = self._astar(list(cells), goals, net,
                                       dist_map=pguide, alpha=alpha,
                                       max_via=allow_via, cls=cls, dist_def=pdef)
                    if path is not None:
                        used_ring = pring
                        break
                if used_ring is not None and used_ring != profiles[0][2]:
                    self.pair_fallback += 1
                ring_used = used_ring
            else:
                path = self._astar(list(cells), goals, net,
                                    dist_map=dist_map, alpha=alpha,
                                    max_via=allow_via, cls=cls, dist_def=dist_def)
                ring_used = None
            # ★★2026-11-05 **耦合失败 ⇒ 同一个脚再试一次 (不带走廊约束)** ——
            #   ★**为什么**: 差分对要求 N 贴着 P 走 ⇒ 走廊窄 ⇒ 长距离 (100~240mm) 走不通
            #   ⇒ 实测 12 个 MIPI 对里 **N 侧 10 个完全布不出来** ⇒ 每个 = 2 个焊盘未连接
            #   ★**取舍**: N 走不到 P 旁边 ⇒ 几何不是理想差分对, 但**至少是通的**
            #   ⇒ ★**没通的板子比几何不完美的板子更没用**
            #   ★**在同一个 tree 里重试** ⇒ ★不会重复布已有的连接 (不会出重线)
            #   ★**几何不完美的对, 会在 ROUTING_REPORT 里点名** (不假装是 100Ω)
            if path is None and alpha > 0.0:
                path = self._astar(list(cells), goals, net,
                                   max_via=allow_via, cls=cls)
                if path is not None:
                    self.pair_fallback += 1
                    ring_used = None
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
                # ★诊断: 记下"从哪到哪布不通" ⇒ 才知道是局部堵死还是目标不可达
                self.fail_detail.append({
                    "net": net, "pad": "%s.%s" % (pad[0], pad[1]),
                    "start": [round(cells[0][1] % self.W * self.g + self.bb[0], 2),
                              round(cells[0][1] // self.W * self.g + self.bb[1], 2)],
                    "goal": [round(goal_cells[0][1] % self.W * self.g + self.bb[0], 2),
                             round(goal_cells[0][1] // self.W * self.g + self.bb[1], 2)],
                    "stub": bool(stub_s),
                })
                continue
            # ★★2026-11-04 23:58 **换层点过孔落不下 ⇒ 整条路径放弃** (不留断铜)
            if not self._emit_path(net, path, width, via_count,
                                   stub_start=stub_s, stub_end=stub_g):
                nfail += 1
                ok = False
                self.fail_reasons[net] = self.fail_reasons.get(net, 0) + 1
                self.fail_detail.append({
                    "net": net, "pad": "%s.%s" % (pad[0], pad[1]),
                    "reason": "via_conflict",
                })
                continue
            tree |= set(path)
            connected_pads.append(pad)
        length = self.net_length(net)
        self.routed.add(net)
        return {"ok": ok, "segs": len(self.tracks), "len": round(length, 3),
                "fail": nfail + nfail_trunk, "net": net, "ring": ring_used}

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
        """★出脚直道 vs **已布走线/过孔** 的净距 (A* 的障碍图只管新走线, 管不了后出现的直道)
           ★**need 不加额外余量**: 0.4mm pitch 的 SoM BTB (0.2mm 焊盘) ⇒ 相邻两根
             0.2mm 直道的中心线间距就是 0.4mm ⇒ 净距恰好 0.2mm (KiCad 下限)
             ⇒ 加 0.02 余量会把**每一对相邻脚**都判死 ⇒ BTB 全布不出来
           ★先布的那根直道宽 0.2 ⇒ need = 0.1+0.1+0.2 = 0.4 ⇒ 恰好放行"""
        for (n2, ax, ay, bx, by, li, tw) in self.tracks:
            if n2 == net:
                continue
            if li != 0:
                continue
            # ★need 不加额外余量: 0.4mm pitch 的 SoM BTB (0.2mm 焊盘) ⇒ 相邻两根
            #   0.2mm 直道的中心线间距就是 0.4mm ⇒ 净距恰好 0.2mm (KiCad 下限)
            #   ⇒ 加 0.02 余量会把**每一对相邻脚**都判死 ⇒ BTB 全布不出来
            # ★但**对面是 0.25mm 及以上的线时必须留余量** (直道半宽 0.125 > 0.1
            #   ⇒ 0.4mm 间距只剩 0.175mm 净距 ⇒ DRC 红)
            need = w / 2.0 + tw / 2.0 + CLEAR + (0.0 if tw <= 0.21 else 0.025)
            if _seg_seg_dist(x1, y1, x2, y2, ax, ay, bx, by) < need:
                return False
        for (n2, vx, vy, l1, l2) in self.vias:
            if n2 == net or l1 > 0:
                continue
            need = w / 2.0 + VIA_DIA / 2.0 + CLEAR
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
    def route_gnd_drops(self, net="GND", max_r_mm=4.0, via_top=0, via_bot=5):
        """★GND 焊盘 → 短走线 → 通孔 → L2/L6 完整 GND 平面
           (SMD 焊盘在 F.Cu ⇒ 必须靠过孔下到平面; ★通孔一层平面都连得上)

           ★★2026-11-04 **用"出脚直道"出脚** (与 route_net 同一个机制) ——
             上一版直接从**焊盘中心格**起走 ⇒ 密集器件区 (0402/0603 侧边全是别的网焊盘)
             ⇒ 起点周围全被封死 ⇒ ★**31 个 GND 焊盘一根铜都没接上**
             ⇒ 现在: 先沿焊盘中心线**直着出脚** (直线出脚才有机会挤出焊盘阵),
               再从直道末端去找过孔位
           返回 (成功数, 失败数)"""
        pads = list(self.net_pads.get(net, []))
        net_g = net
        ok = 0
        fail = 0
        done_pads = []
        used_vias = []          # ★已用过的过孔位置 (孔间距 ≥0.60mm ⇒ 不叠孔)
        # ★诊断: 失败原因分类 (★不猜 ⇒ 逐个记)
        why = {"free": 0, "inpad": 0, "viafree": 0, "spacing": 0, "astar": 0}
        for pad in pads:
            _ref, _num, cx, cy, _layers = pad
            done = False
            # ★出脚直道 (与 route_net 的 anchor() 同一套逻辑)
            anchor = self.escape_stub(net, pad)
            if anchor:
                ax, ay = anchor
                start_cells = [(0, self._idx(self._ci(ax), self._cj(ay)))]
                stub_start = (cx, cy, ax, ay)
            else:
                start_cells = list(self._pad_cells(net, pad))
                stub_start = None
            for r_mm in (0.8, 1.2, 1.6, 2.0, 2.5, 3.0, 3.5, 4.0):
                if r_mm > max_r_mm:
                    break
                for cand in self._ring_cells(cx, cy, r_mm):
                    i, j = cand
                    if not (0 <= i < self.W and 0 <= j < self.H):
                        continue
                    idx = self._idx(i, j)
                    px, py = self._cx(i), self._cy(j)
                    if not self._free(0, idx, net):
                        why["free"] += 1
                        continue
                    if self._in_pad(px, py):
                        why["inpad"] += 1
                        continue
                    if not self._via_free_all(idx, net):
                        why["viafree"] += 1
                        continue
                    # ★孔间距: 0.3 钻 + 0.25 最小孔间距 ⇒ 孔心距 ≥0.55mm
                    if any(math.hypot(px - ux, py - uy) < 0.60 for (ux, uy) in used_vias):
                        why["spacing"] += 1
                        continue
                    # ★★**路径可以走内层绕过去**, 但**终点必须在 F.Cu**
                    #   ★因为 GND 下拉孔要落在终点 (过孔是通孔 ⇒ F.Cu..B.Cu ⇒ 接到 L2/L6 平面)
                    #   ★上一版 max_via=False ⇒ 只能走 F.Cu ⇒ 密集器件区根本挤不过去
                    # ★★2026-11-05 04:40 **限制 GND 下拉的走线长度** (≤6mm):
                    #   实测 v12: GND 缝合生成了**一根 160.45mm 的 F.Cu 长线** ⇒
                    #   ★**它把整条走廊堵死并短接了 14 个信号脚** (DSI_D0_D0_N_SRC×7 / DSI_D0_D1_P_SRC×3 / CARRIER_BOARD_EN×4)
                    #   + 87 条 clearance 全撞它 ⇒ ⇒ **GND 接地宁可"留几个未连接", 也不许拉长线横穿板子**
                    #   ⇒ 真正的解法是**第三遍的"焊盘内过孔"** (不需要走线空间)
                    path = self._astar(start_cells, {(0, idx)},
                                       net, max_via=True)
                    if path is None:
                        why["astar"] += 1
                        continue
                    # ★★2026-11-05 04:45 **硬闸: GND 下拉的走线只许 ≤6mm**
                    #   ★实测 v12: 一根 **160.45mm** 的 GND 缝合线把整条 F.Cu 走廊堵死,
                    #   并短接了 14 个信号脚 + 87 条 clearance ⇒ ★**长缝合线一律不许落**
                    #   ⇒ 宁可让这个焊盘留"未连接" (由第三遍的焊盘内过孔接管), 也不许横穿板子
                    if self._path_len(path) > 6.0:
                        why["toolong"] = why.get("toolong", 0) + 1
                        continue
                    # ★★★2026-11-04 **过孔必须真落下来** (否则铜从一层跳到另一层却没孔)
                    if not self._emit_path(net, path, W_SIG, 1,
                                           stub_start=stub_start):
                        why["astar"] += 1
                        continue
                    # ★★2026-11-05 **别放重叠的孔** ——
                    #   ★A* 的最后一步若是换层 ⇒ _emit_path **已经在终点格放过孔了**
                    #   ⇒ 再放一个 ⇒ **两个孔同心** ⇒ KiCad 报 hole_to_hole (co-located)
                    #   ⇒ 查一下: 已有同网同位置的孔就不放了
                    dup = False
                    for (vn, vx, vy, vl1, vl2) in self.vias:
                        if vn == net and abs(vx - px) < 1e-6 and abs(vy - py) < 1e-6:
                            dup = True
                            break
                    if not dup:
                        if self._via_too_close(net, px, py):
                            why["spacing"] += 1
                            continue
                        if not self._via_ok(via_top, via_bot, idx, net):
                            why["viafree"] += 1
                            continue
                        self.vias.append((net, px, py, via_top, via_bot))
                        self.via_cells.setdefault(idx, []).append((px, py))
                        self._add_via_hash(px, py)
                        self._add_via_halo(net, px, py, via_top, via_bot)
                    used_vias.append((px, py))
                    ok += 1
                    done_pads.append(pad)
                    done = True
                    break
                if done:
                    break
            if not done:
                fail += 1
        self.gnd_fail_why = why
        # ★★★2026-11-05 **第二遍: 把没接上的 GND 焊盘接到**已存在的 GND 铜**上
        #   ★**为什么**: 上一版每个 GND 焊盘都自己找过孔位 ⇒ 密集器件区找不到空位
        #   ⇒ 实测 **31 个 GND 焊盘一根铜都没接上** (占 117 个未连接的 27%!)
        #   ★**同一网之间不受 halo 限制** ⇒ ★**直接连到邻近的 GND 铜 (走线或过孔) 就行**
        #   ⇒ 第二遍: 把失败焊盘连到**已成功的 GND 焊盘/过孔** (同网 ⇒ 净距不管)
        orphan = [p for p in pads if p not in done_pads]
        if orphan and done_pads:
            # ★**已接上的 GND 铜的锚点** (焊盘中心 + 过孔位置)
            anchor_xy = []
            for p in done_pads:
                anchor_xy.append((p[2], p[3]))
            for (net, x, y, l1, l2) in self.vias:
                if net == net_g:
                    anchor_xy.append((x, y))
            for pad in orphan:
                _ref, _num, cx, cy, _layers = pad
                anchor = self.escape_stub(net_g, pad)
                if anchor:
                    ax, ay = anchor
                    start_cells = [(0, self._idx(self._ci(ax), self._cj(ay)))]
                    stub_start = (cx, cy, ax, ay)
                else:
                    # ★★2026-11-05 **起脚格被封死时的兵底** ——
                    #   实测: 有 GND 焊盘的**自身格子 8 个邻居全被别的网占** (8nb=0/8)
                    #   ⇒ escape_stub 返回 None (它只看"焊盘密度", 不看"走线围堵")
                    #   ⇒ A* 从焊盘格起步**一步都走不出去** ⇒ 必失败
                    #   ⇒ 现在: 往外找一圈**有空位且邻居能走**的格子, 用直道接过去
                    start_cells, stub_start = self._gnd_escape(net_g, pad)
                    if not start_cells:
                        why["chain"] = why.get("chain", 0) + 1
                        continue
                # ★★**只取最近的几个锚点当目标** (★不然目标散在全板 ⇒ 启发式包围盒巨大 ⇒ A* 预算烧光)
                #   实测: 上一版把 144 个锚点全当目标 ⇒ ★**22 个孤儿全失败**
                near = sorted(anchor_xy,
                              key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)[:16]
                # ★★**目标可以在内层** (★过孔是通孔 ⇒ F.Cu..B.Cu ⇒ 接到 L2/L6 平面)
                goals = set()
                for q in near:
                    gi = self._idx(self._ci(q[0]), self._cj(q[1]))
                    for li in ROUTE_LAYERS:
                        goals.add((li, gi))
                # ★★**允许换层** (★原来 max_via=False ⇒ 只能走 F.Cu ⇒ 挤不过去)
                path = self._astar(start_cells, goals, net_g, max_via=True)
                if path is None:
                    why["chain"] = why.get("chain", 0) + 1
                    continue
                # ★★2026-11-05 04:45 同样硬闸: chain 缝合也只许 ≤6mm (同上: 不许拉长线横穿板子)
                if self._path_len(path) > 6.0:
                    why["chain"] = why.get("chain", 0) + 1
                    continue
                if not self._emit_path(net_g, path, W_SIG, 1, stub_start=stub_start):
                    why["chain"] = why.get("chain", 0) + 1
                    continue
                ok += 1
                fail -= 1
                # ★新接上的焊盘也当锚点 (⇒ 后面孤儿可以接着连)
                anchor_xy.append((cx, cy))
        # ★★★2026-11-05 03:0x **第三遍 (新): 还没接上的 GND 焊盘 ⇒ 直接在焊盘下方落过孔 (焊盘内过孔)**
        #   ★**为什么必须这样**: 前两遍都要**在焊盘外面找空间** ⇒ 密集器件区 (0402/0603 旁边
        #   全是别的网焊盘) ⇒ ★**被围死的焊盘永远找不到过孔位** ⇒ 实测 36 个 GND 焊盘一根铜都没接上
        #   ⇒ ★**焊盘内过孔 (via-in-pad) 是唯一解**: 过孔落在焊盘自己的铜里 ⇒
        #     ① 不需要任何走线空间 ② 净距天然满足 (同网) ③ 直接落到 L2/L6 的 GND 平面
        #   ★**焊盘尺寸判据**: 焊盘短边 ≥ 0.70mm 才放得下 Ø0.6 过孔 (+0.05 边距)
        #   ★**孔间距**: 与已有过孔孔心距 ≥0.60mm (0.3 钻 + 0.25 孔间距)
        orphan3 = [p for p in pads if p not in done_pads]
        for pad in orphan3:
            _ref, _num, cx, cy, _layers = pad
            # 找这个焊盘的矩形 (同网)
            rect = None
            for (n2, x0, y0, x1, y1, _ls) in self.pad_rects_l:
                if n2 == net_g and x0 - 0.01 <= cx <= x1 + 0.01 and y0 - 0.01 <= cy <= y1 + 0.01:
                    rect = (x0, y0, x1, y1)
                    break
            if not rect:
                continue
            x0, y0, x1, y1 = rect
            _short = min(x1 - x0, y1 - y0)
            if _short < 0.55:
                why["inpad_small"] = why.get("inpad_small", 0) + 1
                continue
            # ★★2026-11-05 07:40 **小焊盘用缩小过孔** (0.55~0.70 宽的焊盘 ⇒ Ø0.60 放不下)
            if _short >= 0.70:
                _dia, _drill = VIA_DIA, VIA_DRILL
            else:
                _dia, _drill = VIA_DIA_S, VIA_DRILL_S
            # ★孔间距: 已有过孔
            if any(math.hypot(cx - vx, cy - vy) < 0.60 for (vn, vx, vy, _l1, _l2) in self.vias):
                why["inpad_spacing"] = why.get("inpad_spacing", 0) + 1
                continue
            # ★**过孔所在位置的铜净距**: 同网焊盘不算, 但别的网不能挨着
            idx = self._idx(self._ci(cx), self._cj(cy))
            bad = False
            for (n2, ax, ay, bx, by) in self.pad_rects:
                if n2 == net_g:
                    continue
                if x0 - 0.05 <= cx <= x1 + 0.05 and y0 - 0.05 <= cy <= y1 + 0.05:
                    bad = True
                    break
            # ★★2026-11-05 08:22 **改用几何精确判据** (★halo[2] 的 0.95mm 半径太严 ⇒ 密集区放不下)
            if not bad and not self._via_exact_ok(cx, cy, _dia, net_g, _drill):
                bad = True
            if bad:
                why["inpad_busy"] = why.get("inpad_busy", 0) + 1
                continue
            # ★落过孔 (F.Cu..B.Cu ⇒ 穿过 L2/L6 的 GND 平面 ⇒ 直接接地)
            # ★**不加"焊盘→过孔"的短引线**: 过孔就在焊盘中心 ⇒ 那条引线是**零长段** ⇒ DRC 报 dangling
            #   (实测 v12: "删零长段 434") ⇒ ★焊盘与过孔同点 ⇒ **铜直接连通, 不需要引线**
            v = pcbnew.PCB_VIA(self.b)
            v.SetPosition(pcbnew.VECTOR2I(int(cx * MM), int(cy * MM)))
            v.SetViaType(pcbnew.VIATYPE_THROUGH)
            v.SetWidth(pcbnew.FromMM(_dia))
            v.SetDrill(pcbnew.FromMM(_drill))
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            v.SetNetCode(netcode(self.b, net_g))
            self.b.Add(v)
            self.vias.append((net_g, cx, cy, 0, 5))
            self._add_via_halo(net_g, cx, cy, 0, 5)
            # ★**过孔直接落在焊盘里 ⇒ 焊盘自己就接到平面了** (不需要任何走线)
            ok += 1
            fail -= 1

        # ---------- 4) ★★2026-11-05 07:40 **窄焊盘 (连接器排针类) 沿长轴引出去落过孔**
        #   ★**问题形态**: 0.275×0.9 / 0.3×1.3 的连接器 GND 焊盘 ⇒ **短边太窄放不下任何过孔**
        #     ⇒ 前三遍全灭 (escape_stub 返回 None / A* 出不去 / inpad_small)
        #   ★**解法**: 沿焊盘的**长轴** (垂直于排针方向) 往外扫 0.8~2.5mm ⇒
        #     找到一块**有空间放过孔**的地方 ⇒ 焊盘 → 一小段同层走线 → 过孔 → GND 平面
        #   ★**走线沿长轴 ⇒ 天然避开同排的邻脚** ⇒ 再过一遍 `_geom_clear` 确认净距
        orphan4 = [p for p in pads if p not in done_pads]
        for pad in orphan4:
            _ref, _num, cx, cy, _layers = pad
            rect = None
            for (n2, x0, y0, x1, y1, _ls) in self.pad_rects_l:
                if n2 == net_g and x0 - 0.01 <= cx <= x1 + 0.01 and y0 - 0.01 <= cy <= y1 + 0.01:
                    rect = (x0, y0, x1, y1)
                    break
            if not rect:
                continue
            x0, y0, x1, y1 = rect
            _short = min(x1 - x0, y1 - y0)
            if _short >= 0.55:
                continue          # ★第三遍能处理
            _long_y = (y1 - y0) > (x1 - x0)     # ★长轴是 y 还是 x
            placed = False
            for _d in (0.9, 1.3, 1.7, 2.1, 2.5):
                for _s in (1, -1):
                    vx = cx if _long_y else cx + _s * _d
                    vy = cy + _s * _d if _long_y else cy
                    # ① 走线净距 (别的网铜)
                    if not self._geom_clear(net_g, [(cx, cy, vx, vy)], 0, W_SIG):
                        continue
                    # ② 孔间距
                    if any(math.hypot(vx - ox, vy - oy) < 0.60 for (vn, ox, oy, _a, _b) in self.vias):
                        continue
                    # ③ 过孔位真能放 (★改用**几何精确**判据 ★不用 halo[2] 的 0.95mm)
                    idx = self._idx(self._ci(vx), self._cj(vy))
                    if not self._via_exact_ok(vx, vy, VIA_DIA, net_g, VIA_DRILL):
                        continue
                    # ★落: 焊盘 → 短走线 → 过孔
                    self.tracks.append((net_g, cx, cy, vx, vy, 0, W_SIG))
                    v = pcbnew.PCB_VIA(self.b)
                    v.SetPosition(pcbnew.VECTOR2I(int(vx * MM), int(vy * MM)))
                    v.SetViaType(pcbnew.VIATYPE_THROUGH)
                    v.SetWidth(pcbnew.FromMM(VIA_DIA))
                    v.SetDrill(pcbnew.FromMM(VIA_DRILL))
                    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                    v.SetNetCode(netcode(self.b, net_g))
                    self.b.Add(v)
                    self.vias.append((net_g, vx, vy, 0, 5))
                    self.via_cells.setdefault(idx, []).append((vx, vy))
                    self._add_via_hash(vx, vy)
                    self._add_via_halo(net_g, vx, vy, 0, 5)
                    ok += 1
                    fail -= 1
                    placed = True
                    break
                if placed:
                    break
            if not placed:
                why["narrow"] = why.get("narrow", 0) + 1
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

    def _gnd_escape(self, net, pad):
        """★GND 焊盘自身格子被封死时 ⇒ 往外找能起步的格子
           返回 (start_cells, stub_start) —— stub_start = (焊盘x, 焊盘y, 出脚x, 出脚y)"""
        _ref, _num, cx, cy, _layers = pad
        # 1) 焊盘格本身能走吗?
        i0, j0 = self._ci(cx), self._cj(cy)
        idx0 = self._idx(i0, j0)
        nb = 0
        for dj in (-1, 0, 1):
            for di in (-1, 0, 1):
                if di == 0 and dj == 0:
                    continue
                if self._free(0, self._idx(i0 + di, j0 + dj), net, 1):
                    nb += 1
        if nb:
            return list(self._pad_cells(net, pad)), None
        # 2) 往外找: 半径 0.5/1.0/1.5/2.0mm 的环, 找**空位且邻居能走**的格
        for r_mm in (0.5, 1.0, 1.5, 2.0, 2.5):
            rr = r_mm / self.g
            for (di, dj) in _ring_offsets(rr):
                i, j = i0 + di, j0 + dj
                if not (0 <= i < self.W and 0 <= j < self.H):
                    continue
                idx = self._idx(i, j)
                if not self._free(0, idx, net, 1):
                    continue
                # ★这个格子的邻居也得能走 (不然 A* 起步就死)
                ok = False
                for dj2 in (-1, 0, 1):
                    for di2 in (-1, 0, 1):
                        if di2 == 0 and dj2 == 0:
                            continue
                        if self._free(0, self._idx(i + di2, j + dj2), net, 1):
                            ok = True
                            break
                    if ok:
                        break
                if not ok:
                    continue
                ex, ey = self._cx(i), self._cy(j)
                # ★直道本身要干净 (不许穿过别的网)
                if not self._stub_clear(net, cx, cy, ex, ey):
                    continue
                return [(0, idx)], (cx, cy, ex, ey)
        return [], None

    def _via_exact_ok(self, cx, cy, dia, net, drill=VIA_DRILL):
        """★**几何精确的过孔可落性判据** (★2026-11-05 08:22)
        ★**为什么不能用 `_via_free_all`**: 它用 **halo[2]** 判 ⇒ 半径 = CLEAR+VIA_DIA/2+W_CLS[2]/2+MARGIN
          = 0.20+0.30+0.25+0.20 = **0.95mm** ⇒ ★**密集区任何过孔都放不下**
          ⇒ ⇒ 实测: GND 焊盘内过孔 **inpad_busy=10 / narrow=10** ⇒ 20 个 GND 焊盘一根铜都没有
          ⇒ ⇒ ★**而且同样的过严判据也在压制长线的换层 ⇒ 那 52 个"真被堵死"有一部分是这么来的**
        ★**精确判据** (按真实铜算, 不按栅格保守半径):
          ① 孔盘外缘到**别的网焊盘** ≥ 0.20mm
          ② 孔盘外缘到**别的网走线** ≥ 0.20mm
          ③ 孔心到已有过孔 ≥ 0.60mm (孔间距)
          ④ 孔心到别的网焊盘的**孔** ≥ 0.25mm (孔净距)
        """
        _r = dia / 2.0
        # ① 别的网焊盘 (同网不算)
        for (n2, x0, y0, x1, y1, _ls) in self.pad_rects_l:
            if n2 == net:
                continue
            dx = max(x0 - cx, 0.0, cx - x1)
            dy = max(y0 - cy, 0.0, cy - y1)
            if math.hypot(dx, dy) < _r + CLEAR:
                return False
        # ② 别的网走线 (同网不算)
        for s in self.tracks:
            if s[0] == net:
                continue
            d = _pt_seg_dist(cx, cy, s[1], s[2], s[3], s[4])
            if d < _r + CLEAR + s[6] / 2.0:
                return False
        # ③ 孔间距 (同孔心/近孔心)
        for (vn, vx, vy, _l1, _l2) in self.vias:
            if vn == net:
                continue
            if math.hypot(cx - vx, cy - vy) < 0.60:
                return False
        # ④ 孔净距 (别的网的孔)
        for (vn, vx, vy, _l1, _l2) in self.vias:
            if vn == net:
                continue
            if math.hypot(cx - vx, cy - vy) < drill / 2.0 + 0.25:
                return False
        return True

    def _via_free_all(self, idx, net):
        """通孔 (贯穿 6 层) 在所有层都要有净距"""
        # ★板边: 通孔盘 0.6mm ⇒ 盘外缘距真板边 ≥ 0.5mm ⇒ 孔心距 ≥ 0.8mm
        if self.edge_d[idx] < EDGE_CLEAR + VIA_DIA / 2.0 - 1e-6:
            return False
        for li in range(NLAYERS):
            c = self.cu[li].get(idx)
            if c is not None and c != net:
                return False
            s = self.halo[2][li].get(idx)
            if s and (s - {net}):
                return False
        return True

    # ------------------------------------------------ 后处理: 删退化图元
    def cleanup_geometry(self, verbose=True):
        """★★ **布线后处理** (★落盘前最后一道闸) —— ★**目的: DRC 归零**

        ★**为什么必须有这一步 (不是"擦屁股", 是"兜底")**:
          路由器在"出脚直道 → 栅格路径"的衔接处会留下两类退化图元:
            ① **零长段** (start == end) —— ★KiCad 直接报 `track_dangling`
               (实测: 一条 0.0000mm 的 track = 两个端点重合 ⇒ KiCad 认为它没接上)
            ② **接不上的短段** —— ★层间过渡段的两端没有落到过孔上
               (过孔被 `_via_too_close` 跳过 ⇒ 铜从一层"跳"到另一层但中间没孔)
        ★**只改布出来的几何** —— ★**绝不改板子的设计规则** (min hole / clearance 都不许动)

        算法:
          1) 删零长段 (start == end)
          2) 统计每个"点" (焊盘 / 过孔 / 段端点) 被几个图元碰到
             某个端点**只被本段碰到**且**不在任何焊盘/过孔上** ⇒ 悬空 ⇒ 删整段
             ★**同层的 T 型接头算"接上"** (端点落在另一段的中段上 ⇒ 铜是连通的)
          3) 迭代到收敛 (删掉一段 ⇒ 相邻段的端点可能跟着悬空)
        返回 (删掉的段数, 删掉的过孔数)"""
        EPS = 1e-4

        # ---------- 1) 删零长段 ----------
        n0 = len(self.tracks)
        # ★★2026-11-05 07:15 **已提交到板上的零长段也要真删** (否则板上留 ~565 条退化段 ⇒ DRC 红)
        _keep0 = []
        for s in self.tracks:
            if abs(s[1] - s[3]) < EPS and abs(s[2] - s[4]) < EPS:
                self._drop_committed(s)
            else:
                _keep0.append(s)
        self.tracks = _keep0
        n_zero = n0 - len(self.tracks)

        # ---------- 索引 ----------
        # 焊盘 (同网) 的矩形覆盖 —— ★焊盘**面积**内的端点都算接上 (不只中心)
        pad_by_layer = defaultdict(list)
        for (net, x0, y0, x1, y1, layers) in self.pad_rects_l:
            for li in layers:
                pad_by_layer[li].append((net, x0, y0, x1, y1))
        # 过孔点 —— ★过孔是**通孔** (F.Cu..B.Cu) ⇒ 6 层都算接上
        via_pts = set()
        for (net, x, y, l1, l2) in self.vias:
            for li in range(NLAYERS):
                via_pts.add((li, round(x, 4), round(y, 4)))

        def _on_pad(net, li, x, y):
            for (n2, x0, y0, x1, y1) in pad_by_layer.get(li, ()):
                if n2 == net and x0 - EPS <= x <= x1 + EPS and y0 - EPS <= y <= y1 + EPS:
                    return True
            return False

        # 段的空间哈希 (1mm 格) —— 用来判 T 型接头 (端点落在别段中段上)
        CELL = 1.0
        seg_hash = defaultdict(list)
        for i, s in enumerate(self.tracks):
            x1, y1, x2, y2 = s[1], s[2], s[3], s[4]
            for ci in range(int(math.floor(min(x1, x2) / CELL)),
                            int(math.floor(max(x1, x2) / CELL)) + 1):
                for cj in range(int(math.floor(min(y1, y2) / CELL)),
                                int(math.floor(max(y1, y2) / CELL)) + 1):
                    seg_hash[(ci, cj)].append(i)

        def _t_junction(net, li, x, y, self_idx):
            """端点 (x,y) 是否落在**同网同层**另一段的中段上 (⇒ 铜是连通的)"""
            key = (int(math.floor(x / CELL)), int(math.floor(y / CELL)))
            for j in seg_hash.get(key, ()):
                if j == self_idx:
                    continue
                s = self.tracks[j]
                if s[0] != net or s[5] != li:
                    continue
                if _pt_seg_dist(x, y, s[1], s[2], s[3], s[4]) <= s[6] / 2.0 + EPS:
                    return True
            return False

        # ---------- 2) 删悬空端段 (迭代到收敛) ----------
        n_dang = 0
        for _round in range(40):
            # 每个点的"段端点计数" (同层)
            ep_cnt = defaultdict(int)
            for s in self.tracks:
                ep_cnt[(s[5], round(s[1], 4), round(s[2], 4))] += 1
                ep_cnt[(s[5], round(s[3], 4), round(s[4], 4))] += 1
            drop = set()
            for i, s in enumerate(self.tracks):
                net, li = s[0], s[5]
                for (px, py) in ((s[1], s[2]), (s[3], s[4])):
                    if (li, round(px, 4), round(py, 4)) in via_pts:
                        continue                      # 落在过孔上 ⇒ 接上
                    if _on_pad(net, li, px, py):
                        continue                      # 落在焊盘上 ⇒ 接上
                    if ep_cnt[(li, round(px, 4), round(py, 4))] > 1:
                        continue                      # 别的段端点也在 ⇒ 接上
                    if _t_junction(net, li, px, py, i):
                        continue                      # T 型接头 ⇒ 接上
                    drop.add(i)                       # ★悬空
                    break
            if not drop:
                break
            # 删掉悬空段后重建哈希
            keep = [s for i, s in enumerate(self.tracks) if i not in drop]
            n_dang += len(self.tracks) - len(keep)
            # ★★已提交的悬空段也要从板上删掉 (★阶段性 commit 已经画上去了)
            for i in sorted(drop):
                self._drop_committed(self.tracks[i])
            self.tracks = keep
            seg_hash = defaultdict(list)
            for i, s in enumerate(self.tracks):
                x1, y1, x2, y2 = s[1], s[2], s[3], s[4]
                for ci in range(int(math.floor(min(x1, x2) / CELL)),
                                int(math.floor(max(x1, x2) / CELL)) + 1):
                    for cj in range(int(math.floor(min(y1, y2) / CELL)),
                                    int(math.floor(max(y1, y2) / CELL)) + 1):
                        seg_hash[(ci, cj)].append(i)

        # ---------- 3) 删没有走线接上的孤立过孔 (KiCad 报 via_dangling) ----------
        touch = set()
        for s in self.tracks:
            touch.add((s[5], round(s[1], 4), round(s[2], 4)))
            touch.add((s[5], round(s[3], 4), round(s[4], 4)))
        n_via_drop = 0
        keep_v = []
        for v in self.vias:
            net, x, y = v[0], v[1], v[2]
            anchored = False
            for li in range(NLAYERS):
                if (li, round(x, 4), round(y, 4)) in touch:
                    anchored = True
                    break
            if not anchored and not _on_pad(net, 0, x, y):
                n_via_drop += 1
                self._drop_committed(v)     # ★已提交的孤立过孔也要从板上删掉
                continue
            keep_v.append(v)
        self.vias = keep_v

        if verbose and (n_zero or n_dang or n_via_drop):
            print("  [CLEAN] 后处理: 删零长段 %d / 删悬空段 %d / 删孤立过孔 %d"
                  % (n_zero, n_dang, n_via_drop))
        return n_zero, n_dang, n_via_drop

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
            # ★★★2026-11-05 **整条蛇形都要查净距** ——
            #   上一版只查了顶点 (apex) 一个点 ⇒ ★**两条斜边可以横穿别的网的铜**
            #   ⇒ 实测 DRC: "tracks_crossing" + 2 条 "shorting_items"
            #   (LIGHT_1V8 的 In2.Cu 走线 被 CSI_D0_D0_P 的蛇形斜边横穿)
            #   ⇒ 现在: 拼出 4 段完整几何, **逐段** 对**所有别的网的铜**查净距
            d = base / 2.0
            p_in = (mid[0] - ux * d, mid[1] - uy * d)
            p_out = (mid[0] + ux * d, mid[1] + uy * d)
            cand = [
                (s[1], s[2], p_in[0], p_in[1]),
                (p_in[0], p_in[1], apex[0], apex[1]),
                (apex[0], apex[1], p_out[0], p_out[1]),
                (p_out[0], p_out[1], s[3], s[4]),
            ]
            if not self._geom_clear(net, cand, s[5], s[6]):
                continue
            self._insert_meander(net, s, mid, apex, ux, uy, base)
            return extra_mm
        return 0.0

    def add_meander_v2(self, net, extra_mm, max_bumps=16):
        """★给 net 增加 extra_mm 长度 —— **多凸起版** (2026-11-05 03:2x)

        ★**上一版 (v1) 为什么对 MIPI 时钟对没用** (实测: CSI_D0_CK Δ=32.4mm / DSI_D0_CK Δ=16.5mm 配平失败):
          ① 只在**一个"最长且 ≥2.5mm"的直段**上加**一个**三角凸起
             ⇒ 时钟对的直段往往很短 (0.25mm 网格 + 蛇形 ⇒ 被拆成很多小段) ⇒ 常常一个都找不到
          ② 加了之后净距不够 ⇒ 直接返回 0 ⇒ 差值原封不动
        ★**v2**: **多凸起 + 逐个候选段试**
          ⇒ 一个 32mm 的差可以拆成 8 个 ~4mm 的小凸起 (每个凸起都按需要的高度算, 高度 ≤3mm 以免被挡)
          ⇒ 每个凸起都单独过 `_geom_clear` (别的网铜净距) ⇒ 不合格就换段/换方向
        返回: 实际增加的长度 (mm)
        """
        added = 0.0
        for _ in range(max_bumps):
            remain = extra_mm - added
            if remain <= 0.01:
                break
            best = None
            for seg in self.net_tracks(net):
                L = math.hypot(seg[3] - seg[1], seg[4] - seg[2])
                if L < 1.2:
                    continue
                ux, uy = (seg[3] - seg[1]) / L, (seg[4] - seg[2]) / L
                base = min(L * 0.8, 8.0)
                val = ((base + remain) / 2.0) ** 2 - (base / 2.0) ** 2
                if val <= 0:
                    continue
                a = math.sqrt(val)
                if a > 3.0:          # ★凸起太高 ⇒ 几乎一定被别的网挡住 ⇒ 换段
                    continue
                mid = ((seg[1] + seg[3]) / 2.0, (seg[2] + seg[4]) / 2.0)
                for sign in (1, -1):
                    nx, ny = -uy * sign, ux * sign
                    apex = (mid[0] + nx * a, mid[1] + ny * a)
                    d = base / 2.0
                    p_in = (mid[0] - ux * d, mid[1] - uy * d)
                    p_out = (mid[0] + ux * d, mid[1] + uy * d)
                    cand = [
                        (seg[1], seg[2], p_in[0], p_in[1]),
                        (p_in[0], p_in[1], apex[0], apex[1]),
                        (apex[0], apex[1], p_out[0], p_out[1]),
                        (p_out[0], p_out[1], seg[3], seg[4]),
                    ]
                    if not self._geom_clear(net, cand, seg[5], seg[6]):
                        continue
                    if best is None or L > best[0]:
                        best = (L, seg, mid, apex, ux, uy, base)
                    break
            if best is None:
                break
            _L, seg, mid, apex, ux, uy, base = best
            self._insert_meander(net, seg, mid, apex, ux, uy, base)
            added += remain
        return added

    def add_meander_v3(self, net, extra_mm, max_bumps=24, apex_max=3.0, min_len=0.3):
        """★v3 (2026-11-05 07:25, 07:42 改) —— ★**固定凸起高度, 反算每凸起能补多少**
        ★**v2 的死穴 (实测)**: v2 是"用**剩余差值**反算凸起高度" ⇒
          a = sqrt(((base+remain)/2)^2 - (base/2)^2)
          ⇒ 差值一大 (Δ32.4mm) ⇒ a = 16.7mm ⇒ ★**超过 a≤3.0 的上限 ⇒ 一个凸起都加不上 ⇒ return 0**
          ⇒ ★**差越大越加不上** (完全反了)
        ★**v3**: 固定凸起高度 a=apex_max(=3.0mm) ⇒ 每凸起最多能补
          extra_max(base) = 2*sqrt((base/2)^2 + a^2) - base
          (base=0.96 ⇒ **+5.12mm** · base=2.6 ⇒ +3.94mm · base=8 ⇒ +9.89mm)
          ⇒ ★**一个 32.4mm 的差 = 7 个小凸起** ⇒ 每个都单独过净距检查
        ★**min_len**: 候选直段的最短长度 (v2 是 1.2mm ⇒ ★**很多对的最长单段只有 0.35~1.25mm ⇒ 直接被卡死**
          ⇒ 放宽到 **0.3mm** (同事 07:42 复核: ★**凸起补长能力几乎与直段长短无关, 只看 a**
            ⇒ base=0.283/0.369/0.305 时一个 a=3.0 凸起分别补 +5.72/+5.64/+5.70mm
            ⇒ ⇒ **min_len 放宽到 ≤0.35 ⇒ 那 3 对立刻可配平**)
          ⇒ ★**净距检查 `_geom_clear` 仍在** ⇒ 拉不出违规铜
        ★**自适应凸起高度**: 优先 a=3.0; 不行就退 a=2.0 / a=1.2 (补得少但**空间小、更容易找到位置**)
        返回: 实际增加的长度 (mm)
        """
        added = 0.0
        APEXES = (apex_max, 2.0, 1.2)
        for _ in range(max_bumps):
            remain = extra_mm - added
            if remain <= 0.01:
                break
            best = None
            for seg in self.net_tracks(net):
                L = math.hypot(seg[3] - seg[1], seg[4] - seg[2])
                if L < min_len:
                    continue
                ux, uy = (seg[3] - seg[1]) / L, (seg[4] - seg[2]) / L
                base = min(L * 0.8, 8.0)
                mid = ((seg[1] + seg[3]) / 2.0, (seg[2] + seg[4]) / 2.0)
                for a_try in APEXES:
                    if a_try > apex_max + 1e-6:
                        continue
                    # ★固定 a ⇒ 这一个凸起最多能补多少
                    cap = 2.0 * math.sqrt((base / 2.0) ** 2 + a_try ** 2) - base
                    if cap <= 0.01:
                        continue
                    take = min(remain, cap)
                    # ★**按 take 反算实际凸起高度** (≤ a_try) ⇒ 不会超上限
                    val = ((base + take) / 2.0) ** 2 - (base / 2.0) ** 2
                    if val <= 0:
                        continue
                    a = math.sqrt(val)
                    if a > a_try + 1e-6:
                        continue
                    for sign in (1, -1):
                        nx, ny = -uy * sign, ux * sign
                        apex = (mid[0] + nx * a, mid[1] + ny * a)
                        d = base / 2.0
                        p_in = (mid[0] - ux * d, mid[1] - uy * d)
                        p_out = (mid[0] + ux * d, mid[1] + uy * d)
                        cand = [
                            (seg[1], seg[2], p_in[0], p_in[1]),
                            (p_in[0], p_in[1], apex[0], apex[1]),
                            (apex[0], apex[1], p_out[0], p_out[1]),
                            (p_out[0], p_out[1], seg[3], seg[4]),
                        ]
                        if not self._geom_clear(net, cand, seg[5], seg[6]):
                            continue
                        if best is None or take > best[0]:
                            best = (take, seg, mid, apex, ux, uy, base)
                        break
                    if best is not None and best[1] is seg:
                        break
            if best is None:
                break
            _take, seg, mid, apex, ux, uy, base = best
            self._insert_meander(net, seg, mid, apex, ux, uy, base)
            added += _take
        return added

    def _geom_clear(self, net, segs, li, w=W_SIG):
        """★这几段几何 vs **别的网的所有铜** (同层走线 + 所有过孔 + 同层焊盘) 净距够不够?
           ★**蛇形配平必须走这一步** —— 蛇形是**离网格**的斜线 ⇒ 栅格 halo 管不到"""
        for (x1, y1, x2, y2) in segs:
            # --- 同层走线 ---
            for (n2, tx1, ty1, tx2, ty2, tli, tw) in self.tracks:
                if n2 == net or tli != li:
                    continue
                need = w / 2.0 + tw / 2.0 + CLEAR
                if _seg_seg_dist(x1, y1, x2, y2, tx1, ty1, tx2, ty2) < need:
                    return False
            # --- 过孔 (★实际是通孔 F.Cu..B.Cu ⇒ 所有信号层都算) ---
            for (n2, vx, vy, l1, l2) in self.vias:
                if n2 == net:
                    continue
                need = w / 2.0 + VIA_DIA / 2.0 + CLEAR
                if _pt_seg_dist(vx, vy, x1, y1, x2, y2) < need:
                    return False
            # --- 焊盘 (别的网的焊盘 ⇒ 穿过去就是短路) ★只查**本层真有铜**的焊盘
            for (n2, x0, y0, xp1, yp1, layers) in self.pad_rects_l:
                if n2 == net or li not in layers:
                    continue
                need = w / 2.0 + CLEAR
                if self._seg_hits_rect(x1, y1, x2, y2, x0 - need, y0 - need,
                                       xp1 + need, yp1 + need):
                    return False
        return True

    @staticmethod
    def _seg_hits_rect(x1, y1, x2, y2, rx0, ry0, rx1, ry1):
        """线段是否与矩形 (含边界) 相交 / 进入
           ★做法: 沿线取样 + 检查矩形四个角到线段的距离 (两个都做 ⇒ 不漏)"""
        # 1) 矩形四���到线段的距离
        for (px, py) in ((rx0, ry0), (rx1, ry0), (rx1, ry1), (rx0, ry1)):
            if _pt_seg_dist(px, py, x1, y1, x2, y2) <= 1e-9:
                return True
        # 2) 线段端点在矩形内
        for (px, py) in ((x1, y1), (x2, y2)):
            if rx0 <= px <= rx1 and ry0 <= py <= ry1:
                return True
        # 3) 线段与矩形边相交 (粗判: 采样足够密)
        n = max(2, int(math.hypot(x2 - x1, y2 - y1) / 0.05) + 1)
        for k in range(n + 1):
            t = k / float(n)
            px = x1 + (x2 - x1) * t
            py = y1 + (y2 - y1) * t
            if rx0 <= px <= rx1 and ry0 <= py <= ry1:
                return True
        return False

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
    # ------------------------------------------------ rip-up & reroute (收尾杀招)
    def rebuild_halo(self):
        """★**重建净距禁区** (★rip-up 后必须重建 ⇒ 否则被拆的线的 halo 还在 ⇒ 白拆)
        ★**为什么能精确重建**: 实测结构 —— ★**self.cu 只记焊盘与板边**,
          ★**走线/过孔只进 halo** ⇒ ⇒ 所以 halo = f(焊盘, 全部走线, 全部过孔) ⇒ 可重算
        """
        self.halo = [[dict() for _ in range(NLAYERS)] for _ in range(3)]
        self._halo_pads()
        for s in self.tracks:
            self._add_track_halo(s[0], s[1], s[2], s[3], s[4], s[5], s[6])
        for (net, x, y, l1, l2) in self.vias:
            self._add_via_halo(net, x, y, l1, l2)

    def _net_start_cells(self, net):
        """该网各焊盘的**起步格** (有出脚直道则取直道终点, 否则取焊盘中心格)"""
        cells = []
        for pad in self.net_pads.get(net, []):
            try:
                st = self.escape_stub(net, pad)
            except Exception:
                st = None
            if st:
                ax, ay = st
                cells.append((0, self._idx(self._ci(ax), self._cj(ay))))
            else:
                try:
                    cells.extend(self._pad_cells(net, pad))
                except Exception:
                    pass
        return cells

    def _blockers_for(self, net, cells, maxn=6):
        """★找出**挡住这些起步格**的别的网的走线 (按几何距离从近到远)"""
        out = []
        for s in self.tracks:
            if s[0] == net:
                continue
            for (li, idx) in cells:
                if s[5] != li:
                    continue
                i, j = idx % self.W, idx // self.W
                cx, cy = self._cx(i), self._cj(j)
                d = _pt_seg_dist(cx, cy, s[1], s[2], s[3], s[4])
                if d < CLEAR + s[6] / 2.0 + HALO_MARGIN + self.g:
                    out.append((d, s))
                    break
        out.sort(key=lambda t: t[0])
        return out[:maxn]

    def stitch_same_net(self, nets=None, width=0.30, verbose=False):
        """★★**同网缝合** (2026-11-05 08:45) —— ★★把"同一张网的多个焊盘"直接用短铜连起来
        ★★**为什么必须有 (实测 v25: 82 条未连里 31 条集中在 CONN_CAM/CONN_LIGHT, 19 条是 GND)**:
          ★**同一张网的多个焊盘本来就应该直接短铜相连** (PCB 标准做法: net stitching / 同网缝合)
          ⇒ ★**同网铜之间不需要净距** ⇒ ⇒ **一根直线就能连 ⇒ 绕开所有中间障碍**
          ⇒ ⇒ ★★而我的路由器是"逐点独立布线到目标" ⇒ **同网两焊盘之间从没有"直连"的机会**
          ⇒ ⇒ ★★ 于是 5 个 GND 焊盘各自要去接 GND 平面, 中间还被别的网挡 ⇒ ⇒ 19 条未连
          ⇒ ⇒ ★★ 一次同网直连 ⇒ **一批未连直接消失**
        ★**安全**: 唯一的风险是这根短铜**碰到别的网的铜** ⇒ ⇒ 逐段用 `_geom_clear` 查 ⇒ 不清就不连
        ★**已通网的焊盘也参与** (连了不会坏事, 反而降阻抗)
        返回: 新增的短铜条数
        """
        n_stitched = 0
        targets = nets if nets is not None else list(self.net_pads.keys())
        # ★★2026-11-05 08:52 **差分对的网不许缝合** ⇒ 缝合会在差分线中间加一段短铜
        #   ⇒ ★**破坏差分对的几何/耦合** (P 侧多一个分支 ⇒ 等长与间距全乱)
        try:
            _dp = set()
            for (_p, _n, _tp, _tn) in DIFF_PAIRS:
                _dp.add(_p)
                _dp.add(_n)
        except Exception:
            _dp = set()
        targets = [t for t in targets if t not in _dp]
        for net in targets:
            pads = self.net_pads.get(net) or []
            if len(pads) < 2:
                continue
            # ★按几何顺序排 (连接器的一排脚 ⇒ 排完相邻脚相邻 ⇒ 短铜最短)
            ps = sorted(pads, key=lambda p: (round(p[2], 3), round(p[3], 3)))
            for i in range(len(ps) - 1):
                a = ps[i]
                b = ps[i + 1]
                lay = 0
                # ★同网已有铜盖住这段 ⇒ 跳过 (不重复画)
                mx, my = (a[2] + b[2]) / 2.0, (a[3] + b[3]) / 2.0
                dup = False
                for s in self.tracks:
                    if s[0] != net:
                        continue
                    if _pt_seg_dist(mx, my, s[1], s[2], s[3], s[4]) < 0.05:
                        dup = True
                        break
                if dup:
                    continue
                segs = [(a[2], a[3], b[2], b[3])]
                if not self._geom_clear(net, segs, lay, width):
                    # ★★2026-11-05 08:50 **直线被挡 ⇒ 试 L 形绕行 (两个方向)**
                    _cands = []
                    _mx, _my = (a[2] + b[2]) / 2.0, (a[3] + b[3]) / 2.0
                    for _c in ((_mx, a[3]), (a[2], _my), (_mx, b[3]), (b[2], _my)):
                        _cands.append([(a[2], a[3], _c[0], _c[1]),
                                       (_c[0], _c[1], b[2], b[3])])
                    _picked = None
                    for _s2 in _cands:
                        if self._geom_clear(net, _s2, lay, width):
                            _picked = _s2
                            break
                    if _picked is None:
                        continue
                    for (_x1, _y1, _x2, _y2) in _picked:
                        self.tracks.append((net, _x1, _y1, _x2, _y2, lay, width))
                        self._add_track_halo(net, _x1, _y1, _x2, _y2, lay, width)
                    n_stitched += len(_picked)
                    continue
                self.tracks.append((net, a[2], a[3], b[2], b[3], lay, width))
                self._add_track_halo(net, a[2], a[3], b[2], b[3], lay, width)
                n_stitched += 1
        if verbose and n_stitched:
            print("  [STITCH] 同网缝合: 新增 %d 条短铜" % n_stitched)
        return n_stitched

    def ripup_and_reroute(self, nets, rip_per_net=6, verbose=True):
        """★★**收尾杀招: 拆掉挡路的线, 重布失败的网** (标准 rip-up & reroute)
        ★**为什么必须**: 实测 78 个失败脚里 ★**64 个 (82%) 不是被局部封锁, 是"中途被堵死"**
          ⇒ ⇒ 局部封锁的靠 halo/排版修; ★中途堵的**只能拆线重走**
        ★**做法**: 对每个失败网 ⇒ ① 找出**堵住它起步格**的别的网的走线 ⇒
          ② 拆掉最近的几条 (连同附近的同网过孔) ⇒ ③ ★**重建 halo** (★否则白拆) ⇒
          ④ 重布该网 ⇒ ⑤ 成功则把被拆的网重新布一遍; 失败则**原样放回**
        ★**时机很关键**: 必须在**阶段性 commit 之前**跑 ⇒ ⇒ 被拆的线**根本不会落到板上**
          ⇒ 板上不会留下废铜 ⇒ ★也不需要从板上删图元
        返回: 重布成功的网数
        """
        ok = 0
        for net in nets:
            if net in self.routed:
                continue
            cells = self._net_start_cells(net)
            if not cells:
                continue
            bl = self._blockers_for(net, cells, rip_per_net)
            if not bl:
                continue
            ripped = [b[1] for b in bl]
            rip_nets = set(s[0] for s in ripped)
            keep = [s for s in self.tracks if s not in set(ripped)]
            # ★被拆线附近的同网过孔也要拆 (否则它的 halo 照样堵)
            keep_v = []
            ripped_v = []
            for v in self.vias:
                drop = False
                if v[0] in rip_nets:
                    for s in ripped:
                        if _pt_seg_dist(v[1], v[2], s[1], s[2], s[3], s[4]) < 1.5:
                            drop = True
                            break
                (ripped_v if drop else keep_v).append(v)
            self.tracks = keep
            self.vias = keep_v
            self.rebuild_halo()
            # ★重布这个网 (★routed 集合里也要先摘掉它)
            self.routed.discard(net)
            res = self.route_net(net, width=W_SIG)
            if res.get("ok"):
                ok += 1
                # ★把被拆的网重新布一遍 (它们现在有地方了)
                for rn in sorted(rip_nets):
                    self.route_net(rn, width=W_SIG)
                if verbose:
                    print("  [RIPUP] %-22s 拆了 %d 条线 ⇒ 重布成功" % (net, len(ripped)))
            else:
                # ★失败 ⇒ 原样放回 (★板子上本来也没它们 ⇒ 只需还原障碍模型)
                self.tracks = keep + ripped
                self.vias = keep_v + ripped_v
                self.rebuild_halo()
                self.routed.discard(net)
                if verbose:
                    print("  [RIPUP] %-22s 拆了 %d 条线 ⇒ 仍不通 ⇒ 已还原" % (net, len(ripped)))
        return ok

    def _emit_path(self, net, path, width, via_count=1,
                   stub_start=None, stub_end=None):
        """★stub_start/stub_end = (焊盘中心x, 中心y, 直道终点x, 终点y)
           —— 密集焊盘出脚: 先沿中心线直线走, 再进网格

        ★★2026-11-04 23:58 **换层点必须先确认过孔能落下来** ——
          原来的写法: 边走边打孔, 打孔失败 (被 _via_too_close 跳过) 就**继续往下走**
          ⇒ ★**铜从一层"跳"到另一层但中间没孔** ⇒ 两端悬空 ⇒ DRC track_dangling
          ⇒ 现在: 先把本路径所有换层点**一次性预校验** (含路径内部互相间距),
            任何一个落不下 ⇒ ★**整条路径放弃** (不落铜) ⇒ 宁可这个脚不通, 也不留断铜
        返回 True = 已落铜; False = 放弃 (调用方计入失败)"""
        # ---------- 0) 构造路径点 ----------
        pts = []
        for (li, idx) in path:
            i, j = idx % self.W, idx // self.W
            pts.append([li, self._cx(i), self._cy(j)])
        if not pts:
            return True
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

        # ---------- 1) 收集换层点 ----------
        # ★**层间过渡的两端坐标相同** (A* 的换层是同格换层) ⇒ 落铜时会产生**零长段**
        #   ⇒ 零长段是**退化图元** ⇒ 交给 cleanup_geometry 统一清掉
        trans = []
        for k in range(len(pts) - 1):
            la, xa, ya = pts[k]
            lb, xb, yb = pts[k + 1]
            if la != lb:
                trans.append((xa, ya, la, lb))

        # ---------- 2) 预校验所有换层点 (含路径内部互相间距) ----------
        for (x, y, la, lb) in trans:
            l1, l2 = (la, lb) if la < lb else (lb, la)
            if not self._via_ok(l1, l2, self._idx(self._ci(x), self._cj(y)), net):
                return False
            # ★**同一条路径里的两个换层点也不能太近** (否则第二个孔放不下)
            for (x2, y2, _a, _b) in trans:
                if x2 == x and y2 == y:
                    continue
                if math.hypot(x - x2, y - y2) < MIN_VIA_CENTER:
                    return False

        # ---------- 3) 落铜 ----------
        if stub_start:
            sx, sy, ex, ey = stub_start
            self.tracks.append((net, sx, sy, ex, ey, 0, W_MIN))
            self._add_track_halo(net, sx, sy, ex, ey, 0, W_MIN)
        if stub_end:
            gx, gy, ex, ey = stub_end
            self.tracks.append((net, ex, ey, gx, gy, 0, W_MIN))
            self._add_track_halo(net, ex, ey, gx, gy, 0, W_MIN)
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
                # ★★2026-11-04 23:55 **修共线判据的坐标错位**:
                #   段元组是 (net, x1, y1, x2, y2, li, w) ⇒ p[1]=x1 p[2]=y1 p[3]=x2 p[4]=y2
                #   原来写的是 (p[2]-p[1], p[3]-p[1]) = (y1-x1, x2-x1) ⇒ **x 和 y 混了**
                #   ⇒ 共线判据几乎永远不成立 ⇒ ★**每 0.25mm 一段的小碎线全留着**
                #   (实测 22179 段, 板文件 4.9MB) ⇒ 合并后段数大降, 悬空端的机会也大降
                ax, ay = p[3] - p[1], p[4] - p[2]
                bx, by = s[3] - s[1], s[4] - s[1]
                if (p[5] == s[5]) and (abs(ax * by - ay * bx) < 1e-9) \
                        and (ax * bx + ay * by > 0):
                    merged[-1] = (p[0], p[1], p[2], s[3], s[4], p[5], p[6])
                    continue
            merged.append(s)
        for s in merged:
            self.tracks.append(s)
            self._add_track_halo(s[0], s[1], s[2], s[3], s[4], s[5], s[6])
        return True

    def _emit_via(self, net, x, y, la, lb, count=1):
        l1, l2 = (la, lb) if la < lb else (lb, la)
        vs = [(x, y)]
        if count > 1:
            # ★过孔阵列间距 ≥ VIA_DIA + CLEAR = 0.8mm —— ★上一版用 0.6mm
            #   ⇒ 相邻两个 0.6mm 盘的边缘正好相接 ⇒ DRC: 短接 + 孔重合 + 孔间距不足
            vs = [(x + (k - (count - 1) / 2.0) * 0.85, y)
                  for k in range(count)]
        for (vx, vy) in vs:
            # ★**同一个网的两颗孔间距 ≥ 0.58mm** (孔径 0.3 ⇒ 孔到孔 ≥ 0.25mm)
            #   ★同网的过孔**不互斥** (halo 里同网不算冲突) ⇒ 上限没管住
            #   ⇒ 上一版 DRC: holes co-located 64 条 + hole to hole 5 条
            # ★★2026-11-04 23:50 **这条现在也在 A\* 里查了 (见 _via_ok)** ——
            #   ⇒ A\* 不会规划"落不下过孔的换层点" ⇒ ★**层间过渡段不会断**
            if self._via_too_close(net, vx, vy):
                continue
            if not self._via_ok(l1, l2, self._idx(self._ci(vx), self._cj(vy)), net):
                continue
            self.vias.append((net, vx, vy, l1, l2))
            self.via_cells.setdefault(self._idx(self._ci(vx), self._cj(vy)), []).append((vx, vy))
            self._add_via_hash(vx, vy)
            self._add_via_halo(net, vx, vy, l1, l2)

    def _via_too_close(self, net, vx, vy, mind=0.58):
        """同网两颗过孔离得太近 (孔到孔 < 0.25mm ⇒ DRC 红)

        ★★2026-11-04 22:45 修 (真正的根因): 原来只扫 **3×3 邻格** (±0.25mm) ⇒ ★**够不着 0.56mm 内的其它过孔**
        ⇒ 两颗过孔中心距 0.5mm (孔到孔 0.2mm) 竟然没被拦住 ⇒ DRC 出 hole_to_hole。
        ⇒ 现在扫 ±3 格 (±0.75mm) 才覆盖 mind=0.58。

        ★★2026-11-05 **改用 1mm 粗粒度哈希** (★性能: 这个函数在 A* 里被调用几十万次)
           ⇒ 3×3=9 次查表 (而不是 49 次) ⇒ 结果一样, 速度 ~5×
        """
        cx = int(math.floor(vx))
        cy = int(math.floor(vy))
        for dj in (-1, 0, 1):
            for di in (-1, 0, 1):
                for (ux, uy) in self.via_hash.get((cx + di, cy + dj), ()):
                    if math.hypot(vx - ux, vy - uy) < mind:
                        return True
        return False

    def _add_via_hash(self, vx, vy):
        self.via_hash.setdefault((int(math.floor(vx)), int(math.floor(vy))),
                                 []).append((vx, vy))

    def _add_track_halo(self, net, x1, y1, x2, y2, li, w=W_SIG):
        """走线净距禁区: 半径 = 净距 + 本线半宽 + 对方半宽 (按级别分别登记)
           ★★2026-11-05 07:50 **默认不盖别的网的焊盘格** (见 _mark 的 skip_pad_cells 说明)
           ★★2026-11-05 08:00 **做成可开关** (PCB_SKIP_PAD_CELLS=0) ⇒ 便于 A/B:
             ★**风险**: 焊盘格不再被 halo 挡 ⇒ ★**相邻格 (0.25mm) 会被别的网的走线占用**
               ⇒ 铜到铜可能只剩 0.025mm ⇒ ★**DRC 违规/短路风险**
               ⇒ ⇒ ★**必须盯 DRC** ⇒ 试验用开关, 验过才准进正式轮
        """
        _skip = os.environ.get("PCB_SKIP_PAD_CELLS", "1") != "0"
        for cls in range(3):
            rr = CLEAR + w / 2.0 + W_CLS[cls] / 2.0 + HALO_MARGIN
            for (i, j) in _seg_cells(x1, y1, x2, y2, self.g, rr / self.g,
                                     self.bb[0], self.bb[1]):
                if not (0 <= i < self.W and 0 <= j < self.H):
                    continue
                self._mark(cls, li, self._idx(i, j), net, skip_pad_cells=_skip)

    def _add_via_halo(self, net, x, y, l1, l2, skip_pad_cells=True):
        """通孔净距禁区 (★默认**不盖别的网的焊盘格** ⇒ 见 _mark 的说明)"""
        i, j = self._ci(x), self._cj(y)
        for cls in range(3):
            rr = CLEAR + VIA_DIA / 2.0 + W_CLS[cls] / 2.0 + HALO_MARGIN
            ri = int(math.ceil(rr / self.g))
            # ★**通孔 ⇒ 6 层都有铜** ⇒ 净距禁区必须记满 6 层 (否则内层撞铜 ⇒ DRC 短接)
            for li in range(NLAYERS):
                for dj in range(-ri, ri + 1):
                    for di in range(-ri, ri + 1):
                        if di * di + dj * dj > (rr / self.g) ** 2 + 1e-9:
                            continue
                        i2, j2 = i + di, j + dj
                        if not (0 <= i2 < self.W and 0 <= j2 < self.H):
                            continue
                        self._mark(cls, li, self._idx(i2, j2), net,
                                   skip_pad_cells=skip_pad_cells)

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

    def build_pair_block(self, net_p, min_c=0.50):
        """★**差分对的"几何禁入格"** (★用精确距离, 不用保守的 halo)

        ★**为什么要自己算**: halo 半径 = CLEAR + w/2 + W_CLS[cls]/2 + HALO_MARGIN
          ⇒ 对 0.25mm 线是 0.2+0.125+0.125+0.2 = **0.65mm** (★栅格量化还要再加)
          ⇒ ★**P 的 halo 把 P 旁边 0.65mm 全封死** ⇒ N 想贴着 P 平行走就进不去
        ★**但物理上**: 两根 0.25mm 线中心距 0.50mm ⇒ 净距 0.25mm ≥ 0.2 ✓ DRC 干净
          ⇒ ★**真正会短路的只有 <0.50mm 的那些格** ⇒ 精确算出来, 只禁这些

        返回一个 set of idx (禁入格)"""
        block = set()
        r = min_c + 0.30
        ri = int(math.ceil(r / self.g)) + 1
        for s in self.tracks:
            if s[0] != net_p:
                continue
            x1, y1, x2, y2 = s[1], s[2], s[3], s[4]
            for (i, j) in _seg_cells(x1, y1, x2, y2, self.g, ri,
                                     self.bb[0], self.bb[1]):
                if not (0 <= i < self.W and 0 <= j < self.H):
                    continue
                idx = self._idx(i, j)
                px, py = self._cx(i), self._cy(j)
                # ★精确距离: 格心到伙伴线段的距离
                d = _pt_seg_dist(px, py, x1, y1, x2, y2)
                if d - s[6] / 2.0 - W_SIG / 2.0 < 0.2:
                    block.add(idx)
        # ★★2026-11-05 **伙伴的过孔也要算** ——
        #   ★**漏了过孔 ⇒ DRC 直接报 clearance 违规** (实测 3 条)
        #   ★过孔是通孔 (F.Cu..B.Cu) ⇒ **所有 6 层**都算
        for (net, vx, vy, l1, l2) in self.vias:
            if net != net_p:
                continue
            rr = min_c + 0.30
            for (i, j) in _rect_cells(vx - rr, vy - rr, vx + rr, vy + rr, self.g,
                                      self.bb[0], self.bb[1]):
                if 0 <= i < self.W and 0 <= j < self.H:
                    idx = self._idx(i, j)
                    px, py = self._cx(i), self._cy(j)
                    if math.hypot(px - vx, py - vy) - VIA_DIA / 2.0 - W_SIG / 2.0 < 0.2:
                        block.add(idx)
        # ★伙伴的焊盘周围 (同层) 也要禁
        for (net, x0, y0, x1, y1, layers) in self.pad_rects_l:
            if net != net_p:
                continue
            rr = min_c + 0.3
            for li in layers:
                for (i, j) in _rect_cells(x0 - rr, y0 - rr, x1 + rr, y1 + rr, self.g,
                                          self.bb[0], self.bb[1]):
                    if 0 <= i < self.W and 0 <= j < self.H:
                        block.add(self._idx(i, j))
        return block

    def build_pair_guide(self, net_p, ring=3):
        """★★ **差分对的"走廊引导图"** (★N 侧的关键修复)

        ★**问题**: 上一版用 `build_dist_map(P)` + alpha 把 N **往 P 的路径上拉**,
          但 P 的路径**自己就被 P 的 halo 封死** (halo 半径 0.65mm ⇒ 邻格全禁)
          ⇒ ★**N 想贴 P 就必须进禁区** ⇒ A* 在那里反复撞墙 ⇒ ★**预算烧光 (58/82 失败)**
          ⇒ 实测: 12 个 MIPI 对里 **N 侧 6 个完全布不出来 (trk=0)**

        ★**修法**: 把"拉近"的**目标从 P 的路径改成 P 路径外侧的那一圈**
          - ring = 2 格 (0.50mm) ⇒ ★**离 P 铜箔 ≥0.50mm** ⇒ 净距 0.25 ≥ 0.2 ⇒ DRC 干净
          - ★N 被拉到这圈"合法走廊"上 ⇒ 既能贴着 P 平行走 (差分对几何), 又不碰禁区
          - ★**代价函数在走廊上最小** ⇒ 不再往禁区里钻 ⇒ ★**A* 预算省下来**

        ★★2026-11-05 **距离图要覆盖全板** ——
          ★上一版 `build_dist_map` 只算 40 格 (10mm) 的 BFS
          ⇒ ★**MIPI 的 P 路径长达 100~240mm** ⇒ N 的**大部分路程都在图外**
          ⇒ 整段都拿到同一个 dist_def ⇒ ★**没有"拉近"效果** ⇒ N 还是乱跑
          ⇒ 现在: **全板 BFS** ⇒ N 从头到尾都被引导在 P 的走廊里

        返回 (guide_map, default) —— guide_map[cell] = 离走廊的距离 (0 = 在走廊上)
        default = 走廊之外的"无穷远"代价值 (★不设默认 0 ⇒ 否则远处反而免费)
        """
        cells = set()
        for s in self.tracks:
            if s[0] != net_p:
                continue
            for (i, j) in _seg_cells(s[1], s[2], s[3], s[4], self.g, 0,
                                     self.bb[0], self.bb[1]):
                cells.add(self._idx(i, j))
        if not cells:
            return {}, 0
        dist = {c: 0 for c in cells}
        frontier = list(cells)
        d = 0
        # ★★**全板 BFS** (★不设 40 格上限 ⇒ 覆盖整条 P 路径)
        while frontier:
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
        guide = {}
        for (c, dd) in dist.items():
            guide[c] = max(0, dd - ring)
        # ★走廊外的格: 距离 = max 值 (⇒ 同样"远") ⇒ ★远处不会比走廊更便宜
        dmax = max(guide.values()) if guide else 0
        return guide, dmax

    # ------------------------------------------------ 落板
    def commit(self, board):
        """把生成的走线/过孔写进板子 (★不改任何网表绑定)
        ★★2026-11-05 07:05 **支持"部分落盘"** —— ★★中途存盘**必须带上已布的走线**!
           原来中途存盘 (`_save_board_progress`) 在 `commit()` **之前** ⇒ board 上还没有任何走线图元
           ⇒ ★**写出的必然是 0 走线骨架** ⇒ ★**"超时不丢活"这个功能压根没保住任何进度**
             (实测: 06:53:53 官方板被刷成 468951B / 0 段 / 0 过孔)
           ⇒ 现在: commit() 记住已写入的条数 ⇒ 中途存盘前先 commit 一遍 ⇒
             ★**中途存盘的板 = 已经布了一部分的真板** ⇒ 超时也能捡回进度
        """
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
        # ★★2026-11-05 07:15 **部分落盘的记账改用"对象身份"** (同事指出的回归)
        #   ⇒ 原来用**下标** (_done_tracks 计数) ⇒ ★**cleanup_geometry 会重排/过滤 self.tracks**
        #   ⇒ 下标错位 ⇒ ★**最终 commit 会漏写走线** (数据丢失!)
        #   ⇒ 现在: 用 id(段元组) 记账, 并在 dict 里**保留元组本体** ⇒ id 不会被复用
        _committed = getattr(self, "_committed", None)
        if _committed is None:
            _committed = self._committed = {}
        for _t in self.tracks:
            # ★★必须用 self.tracks 里的**元组对象本身**记身份 (新建元组 ⇒ id 每次都变 ⇒ 记账失效)
            (net, x1, y1, x2, y2, li, w) = _t
            if id(_t) in _committed:
                continue
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
            _committed[id(_t)] = (_t, t)
            n += 1
        for _v in self.vias:
            (net, x, y, l1, l2) = _v
            if id(_v) in _committed:
                continue
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
            _committed[id(_v)] = (_v, v)
            n += 1
        self._done_tracks = len(self.tracks)
        self._done_vias = len(self.vias)
        return n

    def _drop_committed(self, item):
        """★把**已提交到板上的**图元删掉 (★cleanup 要能真的删退化段, 不只是改内存列表)
           ★**为什么必须**: 阶段性 commit 已经把零长段/悬空段画进板了 ⇒
             cleanup 只改 self.tracks 的话 ⇒ ★**板上那些退化段删不掉** ⇒ DRC 永远红
           ★没有 board.Remove/Delete ⇒ 已画进 board 的退化图元**删不掉** ⇒ v25 会带 ~565 条零长段"""
        _c = getattr(self, "_committed", None)
        if not _c:
            return False
        rec = _c.pop(id(item), None)
        if not rec:
            return False
        obj = rec[1]
        try:
            self.b.Remove(obj)          # KiCad 8/9: BOARD.Remove
        except Exception:
            try:
                self.b.Delete(obj)       # 老版 API
            except Exception:
                return False
        return True


# ------------------------------------------------------------------ 差分对
def route_diff_pair(router, net_p, net_n, width=W_SIG, allow_via=True,
                    trunk_p=None, trunk_n=None):
    """★差分对成对布 —— 先布 P, 再在 P 的走廊里布 N (软代价拉近 ⇒ 同层同间距)
       trunk_p/trunk_n: ((padA,padB),) —— 主干焊盘对 (让两根线走同一条走廊)
       返回 dict: 长度 / 长度差 / 最小间距

       ★★2026-11-05 **差分对耦合 (关键修复)**:
         上一轮: P 走完后, N 用 `dist_map` 软代价"被拉向" P, 但 ★**P 的 halo 仍是硬障碍**
           ⇒ N 想贴着 P 走, 但 P 周围 0.5mm 全被封死 ⇒ **N 跑不到 P 旁边**
           ⇒ 实测: 12 个 MIPI 对里 **6 个的 N 侧完全没布出来** (trk=0)
         这一轮: ★**布 N 时把 P 的 halo 豁免** (只留"精确距离 ≥ 0.45mm"作约束)
           ⇒ N 能真正贴着 P 平行走 ⇒ ★**100Ω 差分对的几何才成立**
           ⇒ ★实测 N 侧 trk=0 → 有走线"""
    res = {"p": net_p, "n": net_n}
    r1 = router.route_net(net_p, width=width, allow_via=allow_via, trunk=trunk_p)
    res["p_ok"] = r1["ok"]
    if not r1["ok"]:
        res["n_ok"] = False
        return res
    # ★★**走廊引导图 (★渐进放宽 ring)** ——
    #   ★目标: 把 N 拉到 **P 路径外侧 ring 圈** ⇒ 既贴着 P 走 (差分对几何) 又不进 P 的 halo 禁区
    #   ★**渐进放宽**: ring 2 (0.50mm, 最接近 100Ω) → 4 → 6 → 8
    #   ★**为什么**: 走廊窄 + MIPI 路径长达 100~240mm ⇒ 单点堵死就整条不通
    #   ⇒ ★**不通就放宽一档** ⇒ ★既保住"贴着 P"的大方向, 又给 N 留出活路
    #   ⇒ ★**实际用了几档会记录** ⇒ 报告里点名哪些对不是最紧的 (不假装是 100Ω)
    r2 = None
    used_ring = None
    # ★★**渐进放宽 ring** (★在 route_net **内部**逐脚重试 ⇒ ★不会重复布已通的脚)
    #   ★ring 2 (0.50mm, 最接近 100Ω) → 4 → 6 → 8
    #   ★**为什么**: 走廊窄 + MIPI 路径长达 100~240mm ⇒ 单点堵死就整条不通
    #   ⇒ ★**不通就放宽一档** ⇒ ★既保住"贴着 P"的大方向, 又给 N 留出活路
    #   ⇒ ★**实际用了几档会记录** ⇒ 报告里点名哪些对不是最紧的 (不假装是 100Ω)
    router.pair_partner = net_p
    router.pair_block = router.build_pair_block(net_p, min_c=0.50)
    try:
        # ★每个 ring 一份引导图 (★route_net 内部逐脚挑 ⇒ 不重复布线)
        profiles = []
        for ring in (2, 4, 6, 8):
            guide, gdef = router.build_pair_guide(net_p, ring=ring)
            profiles.append((guide, gdef, ring))
        # ★★alpha 必须非 0 ⇒ ★**"耦合失败 ⇒ 不带走廊再试一次"的兵底才会触发**
        #   (上一版传 alpha=0 ⇒ 兵底永不触发 ⇒ N 侧大量不通 ⇒ unconnected 反而涨了 13)
        r2 = router.route_net(net_n, width=width, allow_via=allow_via,
                              trunk=trunk_n, profiles=profiles, alpha=0.45)
    finally:
        router.pair_partner = None
        router.pair_block = set()
    res["n_ok"] = r2["ok"]
    res["ring"] = r2.get("ring")
    # ★★2026-11-05 02:50 **兵底: 耦合布不通 ⇒ N 侧按普通网布 (不耦合)**
    #   ★**为什么加这个**: 实测 (tools/diff_pair_audit.py, 22 对全审计):
    #     15 对是"**N 侧压根没布出来**" (缺铜) ⇒ ★**这不是"长度差"问题, 是"没连"问题**
    #     ⇒ 而耦合走廊 (ring 2~8) 在 100~240mm 长路径上极易被单点堵死
    #   ★**取舍**: 耦合走不通时, 让 N 侧**按普通网走** (可能绕远、Δ 会大)
    #     ⇒ ★**"连上了但不等长" 远好过 "根本没连"** (没连 = DRC unconnected + 板子不工作)
    #   ★**代价会被如实记下**: res["coupled"]=False ⇒ 报告里点名这些对"未耦合/Δ 大"
    if not r2.get("ok"):
        r3 = router.route_net(net_n, width=width, allow_via=allow_via, trunk=trunk_n)
        res["n_ok"] = r3.get("ok", False)
        res["coupled"] = False
        res["fallback_len"] = round(r3.get("len", 0.0), 3)
        r2 = r3
    else:
        res["coupled"] = True
    res["ring"] = r2.get("ring")
    res["lp"] = round(r1["len"], 3)
    res["ln"] = round(r2.get("len", 0.0), 3)
    res["delta"] = round(abs(r1["len"] - r2["len"]), 3)
    # ★长度配平: 短的那根加蛇形
    if res["delta"] > 0.13:
        # ★★2026-11-05 07:25 **改用 v3** (固定凸起高度 + 反算每凸起能补多少)
        #   ⇒ v2 的死穴: 用**剩余差值**反算凸起高度 ⇒ 差越大 a 越大 ⇒ **超过 a≤3 上限 ⇒ 一个凸起都加不上**
        #   ⇒ v3: 固定 a=3.0 ⇒ 每凸起 +5.12mm (base=0.96) ⇒ Δ32.4 ⇒ 7 个凸起
        #   ⇒ 先试 v3, 不够再回退 v2 (v2 在**小差值**时更精确)
        _short = net_p if r1["len"] < r2["len"] else net_n
        got = router.add_meander_v3(_short, res["delta"])
        if got < res["delta"] - 0.05:
            got += router.add_meander_v2(_short, res["delta"] - got)
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
def add_gnd_planes(board, layers=None, net="GND", fill=True):
    # ★★2026-11-05 06:40 **层数可配 ⇒ 平面层跟着走**
    #   ★★6 层: **(1, 3, 5)** = In1.Cu + In3.Cu + B.Cu
    #     ⇒ ★**之前只有 (1,5) 两个 GND 平面** ⇒ In2.Cu/In4.Cu 两个信号层**底下没有回流面**
    #       ⇒ ① 信号回流路径断 ⇒ ② GND 下拉过孔可落的平面少 ⇒ ★**GND 未连接项变多**
    #   ★8 层: (1, 3, 5, 7) = In1.Cu + In3.Cu + In5.Cu + B.Cu
    #     (ROUTE_LAYERS = [0,2,4,6] = F.Cu/In2.Cu/In4.Cu/In6.Cu ⇒ 平面正好夹在信号层之间)
    if layers is None:
        # ★★2026-11-05 07:40 **跟着层数走** ⇒ 10 层 ⇒ (1,3,5,7,9) = In1/In3/In5/In7 + B.Cu
        layers = tuple(li for li in range(1, NLAYERS, 2))
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
    ("RAIL_SOM_DCIN", 0.20, 1),      # SOM 输入 (≥2A) —— 出脚限 0.2mm
    ("RAIL_DEMO_5V", 0.25, 1),       # USB-C 5V 输入链 —— 出脚限 0.25mm
    ("SYS_PCB", W_PWR, 1),           # 主板主供电 (电池开关后) ⇒ 0.5mm
    # ★**过孔阵列 (via_count>1) 暂时关闭**: 阵列里的外围孔没有走线穿过
    #   ⇒ KiCad 报 via_dangling (7 条) ⇒ ★"坏掉的过孔阵列比没有阵列更糟"
    #   ⇒ 大电流过孔阵列要在下一轮**连同铜皮**一起做 (见 ROUTING_REPORT §4)
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


def _save_board_progress(board, tag=""):
    """★中途落盘 (★超时不丢活) —— ★**必须"存盘→重读→填平面→再存"**:
       同会话里填平面会把整片 GND 当孤岛删空 (已知坑) ⇒ 重读后再填才靠谱"""
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        proj = os.path.dirname(here)
        # ★★2026-11-05 05:58 **修: 必须跟 PCB_OUT 同一口径** (与 gen_pcb_netlist_board.py:54 一致)
        #   ⇒ 原来硬编码官方板路径 ⇒ ★**并行实验 (PCB_OUT=…) 的中途落盘把官方板覆盖成骨架**
        #   ⇒ 实测: 05:50:23 官方板被 8 层实验写成 468951B / 0 段走线的骨架
        #   ⇒ ★**实验输出必须隔离** (AGENTS.md 铁律: 模块内部已实现的项母板不重复做 ⇒ 同理: 实验不许碰官方板)
        pcb = os.environ.get("PCB_OUT") or os.path.join(proj, "HW", "PCB", "demo_mainboard.kicad_pcb")
        pcbnew.SaveBoard(pcb, board)
        b3 = pcbnew.LoadBoard(pcb)
        b3.BuildConnectivity()
        filler = pcbnew.ZONE_FILLER(b3)
        filler.Fill(b3.Zones())
        pcbnew.SaveBoard(pcb, b3)
        print("  [SAVE] 阶段性落盘 %s" % (tag or ""))
    except Exception as e:
        print("  ⚠️ 阶段性落盘失败: %s" % e)


def route_board(board, verbose=True):
    """★★ 整板布线 —— 一次跑完, 返回统计
       (调用方: state/gen_pcb_netlist_board.py —— ★布线必须落进生成器)"""
    import time
    t0 = time.time()
    stats = {"pairs": [], "nets": {}, "failed": [], "gnd": {}}
    r = GridRouter(board)

    # ---------- 0) GND 完整平面 (L2 + L6) —— 先建, 后面所有布线绕开
    add_gnd_planes(board, layers=None, fill=False)
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
            stats["pair_fallback"] = stats.get("pair_fallback", 0) + res.get("n_fallback", 0)
            if verbose:
                print("  [PAIR] %-22s / %-22s  ok=%s/%s  L=%.2f/%.2f  Δ=%.3fmm  间距=%s%s"
                      % (p, n, res.get("p_ok"), res.get("n_ok"),
                         res.get("lp", 0), res.get("ln", 0), res.get("delta", 0),
                         res.get("min_gap"),
                         ("" if res.get("n_ok") else "  ★N 未通")
                         + ("  ★走廊ring=%s" % res.get("ring") if res.get("ring") else "")
                         + ("  ★退化:无耦合" if res.get("n_fallback") else "")))

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
    # ---------- 4) ★★2026-11-05 08:45 **同网缝合 (net stitching)** ——
    #   ★**为什么放这儿**: 实测 v25 的 82 条未连里 ★**19 条是 GND + 31 条集中在两个连接器**
    #     ⇒ 全是"**同网多点**" ⇒ ★★ 同网焊盘之间本来就该短铜直连 (PCB 标准做法) ⇒ ★**一根直线就能接上**
    #   ★**必须在 rip-up 之前** ⇒ ⇒ rip-up 也能用上这些短铜
    try:
        _nst = r.stitch_same_net(verbose=verbose)
        stats["stitched"] = _nst
        if verbose:
            print("  [STITCH] 同网缝合: 新增 %d 条短铜 (多脚连接器/GND 优先受益)" % _nst)
    except Exception as e:
        print("  ⚠️ 同网缝合失败: %s" % e)

    # ★★★2026-11-05 07:50 **rip-up & reroute (收尾杀招)** ——
    #   ★**时机**: 必须在**阶段性 commit 之前** ⇒ ⇒ 被拆的线**根本不会落到板上** ⇒ 板上无废铜
    #   ★**目标**: 实测 78 个失败脚里 **64 个 (82%) 是"中途被堵死"** ⇒ 只能拆线重走
    _failed = sorted(set([n for n, v in stats["nets"].items() if not v.get("ok")]
                          + [e["net"] for e in r.fail_detail]))
    # ★★2026-11-05 07:55 **rip-up 可关** (PCB_RIPUP=0) ⇒ 便于单变量对比
    if _failed and os.environ.get("PCB_RIPUP", "1") != "0":
        _nrip = r.ripup_and_reroute(_failed, rip_per_net=6, verbose=verbose)
        stats["ripup_ok"] = _nrip
        if verbose:
            print("  [RIPUP] 收尾: 尝试 %d 个失败网 ⇒ 重布成功 %d 个" % (len(_failed), _nrip))
        # ★重布成功的网要重新统计 (失败列表会变)
        stats["failed"] = [n for n in set(stats["failed"])
                           if not (stats["nets"].get(n) or {}).get("ok")]
    # ★★2026-11-05 07:05 **中途存盘前先把已布的走线 commit 到板子上**
    #   ⇒ 原来直接存 ⇒ board 上还没有走线图元 ⇒ ★**存出来必然是 0 走线骨架** ⇒ "超时不丢活"没保住任何进度
    try:
        _n = r.commit(board)
        print("  [SAVE] 阶段性 commit: %d 个图元 (MIPI 后)" % _n)
    except Exception as e:
        print("  ⚠️ 阶段性 commit 失败: %s" % e)
    _save_board_progress(board, "MIPI 后")

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

    # ---------- 4) 其余网络 (★★2026-11-05 07:35 **改按"跨距"降序** ⇒ 长干道先走)
    #   ★**旧口径 (按焊盘数从多到少) 的问题**: 这批网**最后才布** ⇒ 前面 USB对/电源/MIPI
    #     已经把 F.Cu 占掉 ⇒ ★**长干道网 (实测 60~100mm) 只能捡剩的通道 ⇒ 82% 的失败脚在这批**
    #   ★**新口径**: 按网的"跨距" (各焊盘的曼哈顿跨度) 降序 ⇒ ★**长网先占空白板面, 短网填空隙**
    rest = [n for n in r.net_pads
            if len(r.net_pads[n]) >= 2 and n not in r.routed and n != "GND"]

    def _span(n):
        """该网的跨距估计 (各焊盘两两曼哈顿距离的最大值) ⇒ 越长越先布"""
        ps = r.net_pads[n]
        best = 0.0
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                d = abs(ps[i][2] - ps[j][2]) + abs(ps[i][3] - ps[j][3])
                if d > best:
                    best = d
        return best

    rest.sort(key=lambda n: (-_span(n), -len(r.net_pads[n])))
    for net in rest:
        res = r.route_net(net, width=W_SIG)
        stats["nets"][net] = res
        if not res["ok"]:
            stats["failed"].append(net)
    if verbose:
        print("  [REST] 其余 %d 个网已布" % len(rest))
    # ★★2026-11-05 07:05 **中途存盘前先 commit** (同上: 不 commit ⇒ 存出来是空骨架)
    try:
        _n2 = r.commit(board)
        print("  [SAVE] 阶段性 commit: %d 个图元 (其余网后)" % _n2)
    except Exception as e:
        print("  ⚠️ 阶段性 commit 失败: %s" % e)
    _save_board_progress(board, "其余网后")
    if verbose and r.fail_reasons:
        nf = sum(r.fail_reasons.values())
        nb = sum(r.fail_budget.values())
        print("  [FAIL] 布不动的脚 %d 个 (其中 **A* 预算耗尽** %d 个 / 真被堵死 %d 个)"
              % (nf, nb, nf - nb))
        top = sorted(r.fail_reasons.items(), key=lambda kv: -kv[1])[:10]
        for (nn, cnt) in top:
            print("         %-24s %d 脚 (预算耗尽 %d)"
                  % (nn, cnt, r.fail_budget.get(nn, 0)))
        try:
            import json as _json
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "_fail_detail.json"), "w") as f:
                _json.dump(r.fail_detail, f, ensure_ascii=False, indent=1)
        except Exception:
            pass

    # ---------- 5) GND 下拉过孔 (焊盘 → 短走线 → 通孔 → L2/L6 平面)
    ok, fail = r.route_gnd_drops("GND")
    stats["gnd"] = {"drops": ok, "fail": fail}
    if verbose:
        print("  [GND ] 下拉过孔 %d 成功 / %d 失败  (失败原因 %s)"
              % (ok, fail, getattr(r, "gnd_fail_why", {})))

    # ---------- 6) 落板 + 填平面
    # ★★2026-11-04 23:55 **先做几何后处理, 再落板** ——
    #   路由器的"出脚直道 → 栅格路径"衔接处会留下退化图元 (零长段 / 悬空短段)
    #   ⇒ ★**落盘前清掉** ⇒ DRC 归零 (只改几何, 不改板子的设计规则)
    n_zero, n_dang, n_via_drop = r.cleanup_geometry(verbose=verbose)
    stats["clean_zero"] = n_zero
    stats["clean_dangling"] = n_dang
    stats["clean_via"] = n_via_drop
    n_new = r.commit(board)
    stats["tracks"] = len(r.tracks)
    stats["vias"] = len(r.vias)
    stats["edge_viol"] = getattr(r, "edge_viol", 0)
    stats["new_items"] = n_new
    # ★★2026-11-05 07:20 **落板自检: 板上真实图元数 vs 内存里的数必须一致**
    #   ⇒ 这是"阶段性 commit + cleanup"回归的**直接判据** (同事给的)
    #   ⇒ 旧流程板: 零长段=0 且 板上段数 == [SUM]段数 ⇒ ★**对不上就说明回归了**
    try:
        _bt = sum(1 for t in board.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T)
        _bv = sum(1 for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T)
        stats["board_tracks"] = _bt
        stats["board_vias"] = _bv
        if _bt != len(r.tracks) or _bv != len(r.vias):
            print("  ❌ ★**落板自检不一致**: 板上 %d 段/%d 孔 vs 内存 %d 段/%d 孔 (差 %+d 段) ⇒ 记账/删除有 bug"
                  % (_bt, _bv, len(r.tracks), len(r.vias), _bt - len(r.tracks)))
        else:
            print("  ✅ 落板自检: 板上 %d 段 / %d 孔 (与内存一致)" % (_bt, _bv))
    except Exception as e:
        print("  ⚠️ 落板自检失败: %s" % e)
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
