#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""geom_clear.py -- ★★★**真几何净距校验器 (可复用) (2026-11-06 18:2x)**

★★★**为什么必须有它 (★实测事故链)**:
  ① 官方板 (unc 45) 上做"保分支 rip-and-replace" ⇒ 能修好 4 个网 (含 2 条差分腿) ⇒ unc 45→40
  ② ★**但 fresh DRC = 678~772 条违规** ⇒ 板子不可用
  ③ ★★**根因**: `gen_pcb_routing.py` 第 3043 行 `_add_track_halo`:
     `rr = CLEAR + w/2.0 + W_CLS[cls]/2.0 + HALO_MARGIN`
     ⇒ ★**halo 半径里的半宽是"对方线"的宽度, 不是"候选线自己"的宽度**
     ⇒ ★**且 `_mark(..., skip_pad_cells=True)` ⇒ halo 不盖别网焊盘格**
     ⇒ ★★**⇒ 路由器自认为合格的铜, 真板 DRC 会报 0.0152mm 这种**
  ④ ⇒ ★**必须有一把"用真实几何说话"的尺子**, 落铜前逐条量, 不合格的整条路径回退
     ⇒ ★**兄弟的 `state/patch_astar_gated.py` 查的是"换层点(过孔)", 本模块查的是"走线"** ⇒ **两半合起来才完整**

★★★**本模块的三条硬规矩 (★每条都是踩过的坑)**:
  ① ★**KiCad 走线端点是圆头** (半径 = 线宽/2) ⇒ ★**净距要按"胶囊形"算**
     ⇒ ★**矩形模型会白算 0.125mm** (实测: 矩形算余量 0.300mm, DRC 实测报 0.1750mm)
  ② ★**焊盘是矩形不是圆** (SoM BTB 焊盘 0.2×0.7mm) ⇒ ★**当圆算会白扣 0.25mm**
  ③ ★**必须分层**: ★**不同层的铜不冲突** (In2.Cu 的铜压在 F.Cu 焊盘下面完全合法)
     ⇒ ★**二维度量会把"内层铜压在焊盘下面"当障碍 ⇒ 白拦一堆**

用法:
  from geom_clear import BoardCopper, check_track, check_via
  bc = BoardCopper(board)                     # ★建索引 (1mm 空间哈希)
  ok, worst, who = check_track(bc, net, (x1,y1), (x2,y2), width, layer)
  ok, worst, who = check_via(bc, net, (x,y))
"""
import math

MM = 1e6
CLEAR = 0.20
EPS = 1e-6

_CU = None


def cu_layers():
    """★铜层表 (F.Cu / In1..In6 / B.Cu)"""
    global _CU
    if _CU is None:
        import pcbnew
        _CU = [pcbnew.F_Cu]
        for i in range(1, 7):
            _CU.append(getattr(pcbnew, "In%d_Cu" % i))
        _CU.append(pcbnew.B_Cu)
    return _CU


def layer_idx(layer):
    try:
        return cu_layers().index(layer)
    except ValueError:
        return -1


def rect_from_seg(a, b, w):
    """★线段 → 矩形四角 (走线本身就是矩形 ⇒ 净距要算矩形对矩形)"""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    if L == 0:
        return None
    nx, ny = -dy / L * w / 2.0, dx / L * w / 2.0
    return [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
            (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]


def rect_bbox(r):
    xs = [p[0] for p in r]
    ys = [p[1] for p in r]
    return (min(xs), min(ys), max(xs), max(ys))


def _pt_seg(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(p[0] - ax, p[1] - ay)
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))


def _ccw(a, b, c):
    return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])


def seg_seg_dist(p1, p2, q1, q2):
    """★两线段最短距离 (重叠 ⇒ 0)"""
    if (_ccw(p1, p2, q1) != _ccw(p1, p2, q2)) and (_ccw(q1, q2, p1) != _ccw(q1, q2, p2)):
        return 0.0
    return min(_pt_seg(p1, q1, q2), _pt_seg(p2, q1, q2),
               _pt_seg(q1, p1, p2), _pt_seg(q2, p1, p2))


def rect_rect_dist(r1, r2):
    """★两矩形最短距离"""
    for i in range(4):
        a1, a2 = r1[i], r1[(i + 1) % 4]
        for j in range(4):
            b1, b2 = r2[j], r2[(j + 1) % 4]
            if seg_seg_dist(a1, a2, b1, b2) <= 0:
                return 0.0
    d = 1e9
    for i in range(4):
        a1, a2 = r1[i], r1[(i + 1) % 4]
        for j in range(4):
            b1, b2 = r2[j], r2[(j + 1) % 4]
            d = min(d, seg_seg_dist(a1, a2, b1, b2))
    return d


class BoardCopper(object):
    """★板上所有铜的矩形索引 (★按层判定 + 1mm 空间哈希)"""

    CELL = 1.0

    def __init__(self, board, via_dia=0.60, extra=()):
        self.index = {}
        self.via_dia = via_dia
        import pcbnew
        for t in board.GetTracks():
            if t.Type() == pcbnew.PCB_VIA_T:
                p = t.GetPosition()
                h = via_dia / 2.0
                cx, cy = p.x / MM, p.y / MM
                rect = [(cx - h, cy - h), (cx + h, cy - h),
                        (cx + h, cy + h), (cx - h, cy + h)]
                lays = set(range(len(cu_layers())))
                self._add(t.GetNetname(), rect, lays, "孔")
            else:
                s, e = t.GetStart(), t.GetEnd()
                r = rect_from_seg((s.x / MM, s.y / MM), (e.x / MM, e.y / MM),
                                   t.GetWidth() / MM)
                if not r:
                    continue
                li = layer_idx(t.GetLayer())
                self._add(t.GetNetname(), r, set([li]) if li >= 0 else set(range(len(cu_layers()))), "走线")
        for f in board.GetFootprints():
            for p in f.Pads():
                pos = p.GetPosition()
                sz = p.GetSize()
                hx, hy = sz.x / MM / 2.0, sz.y / MM / 2.0
                try:
                    rot = p.GetOrientationDegrees() % 180
                except Exception:
                    rot = 0
                if 45 <= rot <= 135:
                    hx, hy = hy, hx
                cx, cy = pos.x / MM, pos.y / MM
                lays = set()
                try:
                    for l in p.GetLayerSet().Seq():
                        li = layer_idx(l)
                        if li >= 0:
                            lays.add(li)
                except Exception:
                    lays = set([0])
                if not lays:
                    lays = set([0])
                rect = [(cx - hx, cy - hy), (cx + hx, cy - hy),
                        (cx + hx, cy + hy), (cx - hx, cy + hy)]
                self._add(p.GetNetname(), rect, lays,
                          "焊盘[%s.%s]" % (f.GetReference(), p.GetNumber()))
        # ★额外加入的铜 (★例如"这一轮新加的铜" ⇒ 用来查新铜之间是否打架)
        for (net, rect, lays, kind) in extra:
            self._add(net, rect, lays, kind)

    def _add(self, net, rect, lays, kind):
        bb = rect_bbox(rect)
        cx0 = int(math.floor(bb[0] / self.CELL))
        cy0 = int(math.floor(bb[1] / self.CELL))
        cx1 = int(math.floor(bb[2] / self.CELL))
        cy1 = int(math.floor(bb[3] / self.CELL))
        for cx in range(cx0, cx1 + 1):
            for cy in range(cy0, cy1 + 1):
                self.index.setdefault((cx, cy), []).append((net, rect, lays, kind))

    def near(self, a1, a2):
        """★取线段附近的铜 (★只取附近的 ⇒ O(局部))"""
        seen = set()
        out = []
        L = math.hypot(a2[0] - a1[0], a2[1] - a1[1])
        steps = max(2, int(L / 0.25) + 2)
        for k in range(steps + 1):
            t = k / steps
            px = a1[0] + (a2[0] - a1[0]) * t
            py = a1[1] + (a2[1] - a1[1]) * t
            cx = int(math.floor(px / self.CELL))
            cy = int(math.floor(py / self.CELL))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for it in self.index.get((cx + dx, cy + dy), ()):
                        key = id(it[1])
                        if key in seen:
                            continue
                        seen.add(key)
                        out.append(it)
        return out


def check_track(bc, net, a1, a2, width, layer):
    """★候选走线的真几何净距 ⇒ (ok, 最差净距, 是谁)"""
    dx, dy = a2[0] - a1[0], a2[1] - a1[1]
    L = math.hypot(dx, dy)
    if L == 0:
        return True, 1e9, ""
    ux, uy = dx / L, dy / L
    # ★圆头: 两端各延长 w/2 (胶囊形的保守近似)
    e1 = (a1[0] - ux * width / 2.0, a1[1] - uy * width / 2.0)
    e2 = (a2[0] + ux * width / 2.0, a2[1] + uy * width / 2.0)
    cand = rect_from_seg(e1, e2, width)
    if cand is None:
        return True, 1e9, ""
    worst = (1e9, "")
    for (n, rect, lays, kind) in bc.near(e1, e2):
        if n == net:
            continue
        if layer not in lays:
            continue
        d = rect_rect_dist(cand, rect)
        if d < worst[0]:
            worst = (d, "%s[%s]" % (kind, n))
    return (worst[0] >= CLEAR - EPS), worst[0], worst[1]


def check_via(bc, net, pos, via_dia=0.60):
    """★候选过孔的真几何净距 (★通孔 ⇒ 全层)"""
    h = via_dia / 2.0
    cx, cy = pos
    rect = [(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)]
    worst = (1e9, "")
    for (n, orect, lays, kind) in bc.near(pos, pos):
        if n == net:
            continue
        if not (lays & set(range(len(cu_layers())))):
            continue
        d = rect_rect_dist(rect, orect)
        if d < worst[0]:
            worst = (d, "%s[%s]" % (kind, n))
    return (worst[0] >= CLEAR - EPS), worst[0], worst[1]
