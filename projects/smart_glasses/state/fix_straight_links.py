#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_straight_links.py -- ★★★**"直线优先"补连接 (2026-11-06 05:4x 实测)**

★★★**为什么要有这个脚本 (机器实测链, 每条都有出处)**:
  ① 官方板 57 项未连接
  ② `state/fix_unconnected_astar.py` 在 **0.25mm 与 0.125mm 两张网格上都是 "补上 0 条"**
     ⇒ ⇒ ★**网格分辨率不是瓶颈** (两轮失败构成完全一样)
  ③ 失败构成: 15 条"距离>12mm 交给路由器" + 10 条"**stub 净距不过 / A* 找不到路**"
     ⇒ ⇒ ★**卡住的是"从焊盘出来的第一段 stub"**, 不是路径搜索
  ④ ★★**stub 模型的表达力缺陷** (本脚本要补的洞):
     A* 的起点 = "焊盘中心 → 最近格" 的一段 stub ⇒ **stub 必然垂直或斜向**
     ⇒ ★**表达不了"沿着一排焊盘直连"** (★这正是同网相邻焊盘唯一可行的走法)
  ⑤ ★★**SoM BTB 精确几何 (实测)**:
       0.4mm pitch · 焊盘 0.2mm 宽 ⇒ **焊盘边缘净空只有 0.200mm**
       ⇒ ★**在两排焊盘之间穿 0.25mm 走线 + 两侧 0.2mm 净距 = 需要 0.650mm ⇒ 物理放不下**
       ⇒ ★**但同一排内、相邻的同网焊盘 (间距 0.4mm) 可以连**: 沿排方向拉直线即可
       (例: `RAIL_DEMO_5V` = J_SOM_P3.91 @ (16.8,7.96) ↔ J_SOM_P3.93 @ (16.4,7.96))
  ⑥ ⇒ ★**本脚本 = 先试"最朴素的直连"**, 用**精确几何净距**验算, 过了就落铜
     ⇒ 不走 A* ⇒ 不产生 stub ⇒ ★**专门吃"同排相邻焊盘"这一类**

★★**净距验算 (本脚本自己算, 不信 DRC)**:
  · 候选走线 = 两端点之间的直线段 (两端点可以是焊盘中心或走线端点)
  · 对板上**每一条异网铜** (走线/过孔/焊盘) 算"线段到它"的净距
  · ★**要求 ≥ 0.2mm** (板规则) ⇒ ★**不满足就不落铜** ⇒ ★**落铜后 DRC 不该新增违规**

★★**安全**: 只写 --out; 只加铜, 不删任何现有铜 ⇒ ★**不可能"退铜" ⇒ 不可能把网打死**

用法:
  bash state/pcbnew_py.sh state/fix_straight_links.py <板> <DRC.json> --out <新板> [--width 0.25]
"""
import sys
import os
import json
import math
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pcbnew  # noqa: E402

MM = 1e6
CLEAR = 0.20          # ★板规则净距 (mm)
EPS = 1e-6           # ★1nm 容差 (★对齐 KiCad 的 nm 整数比较: 实际==要求 ⇒ 不算违规)
VIA_DIA = 0.60        # 过孔外径
VIA_DRILL = 0.30

# ★★**铜层表** (★8 层叠层: F / In1..In6 / B)
_CU = [pcbnew.F_Cu]
for _i in range(1, 7):
    _CU.append(getattr(pcbnew, "In%d_Cu" % _i))
_CU.append(pcbnew.B_Cu)


def _layer_idx(layer):
    try:
        return _CU.index(layer)
    except ValueError:
        return -1


def seg_seg_dist(p1, p2, q1, q2):
    """★两线段之间的最短距离 (2D, 端点也算)"""
    def pt_seg(p, a, b):
        ax, ay = a
        bx, by = b
        dx, dy = bx - ax, by - ay
        if dx == 0 and dy == 0:
            return math.hypot(p[0] - ax, p[1] - ay)
        t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
        return math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))

    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

    if (ccw(p1, p2, q1) != ccw(p1, p2, q2)) and (ccw(q1, q2, p1) != ccw(q1, q2, p2)):
        return 0.0
    return min(pt_seg(p1, q1, q2), pt_seg(p2, q1, q2),
               pt_seg(q1, p1, p2), pt_seg(q2, p1, p2))


def seg_point_dist(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(p[0] - ax, p[1] - ay)
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))


def rect_from_seg(a, b, w):
    """★线段 → 矩形四角 (★走线本身就是矩形 ⇒ 净距要算矩形对矩形)"""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    if L == 0:
        return None
    nx, ny = -dy / L * w / 2.0, dx / L * w / 2.0
    return [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
            (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]


def rect_rect_dist(r1, r2):
    """★两矩形的最短距离 (重叠 ⇒ 0)"""
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


def rect_bbox(r):
    xs = [p[0] for p in r]
    ys = [p[1] for p in r]
    return (min(xs), min(ys), max(xs), max(ys))


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        return 2
    boardp, drcp = a[0], a[1]
    outp = None
    width = 0.25
    # ★**线宽扫描表** (★优先宽线; 下限 = 板规则最小线宽 0.200mm)
    widths = [0.25, 0.20]
    detour = True
    detour_ext = 3.0
    detour_step = 0.25
    detour_max_dist = 15.0
    PATH_LAYER = 0        # ★★候选走线所在层 (0 = F.Cu)
    i = 2
    while i < len(a):
        if a[i] == "--out":
            outp = a[i + 1]
            i += 2
        elif a[i] == "--width":
            width = float(a[i + 1])
            widths = [width]
            i += 2
        elif a[i] == "--widths":
            widths = [float(x) for x in a[i + 1].split(",") if x.strip()]
            i += 2
        elif a[i] == "--no-detour":
            detour = False
            i += 1
        elif a[i] == "--detour-ext":
            detour_ext = float(a[i + 1])
            i += 2
        else:
            i += 1
    if not outp:
        print("★必须给 --out")
        return 2

    board = pcbnew.LoadBoard(boardp)
    d = json.load(open(drcp, encoding="utf-8"))

    # ── 收齐异网铜 (用于净距验算) —— ★一律用"矩形"表示 ★
    #   ★★★**每块铜必须带"层集合"** (★★★不同层的铜**互不冲突**)
    #     ★★**这是个大坑**: 之前按二维算 ⇒ 把"内层铜正压在 F.Cu 焊盘下面"也当冲突
    #        ⇒ ★**白拦了一大片** (实测施工单里一堆 "别网铜 0.000mm [X[In2.Cu]]" 就是这种)
    ALL_LAYERS = set(range(len(_CU)))
    copper = []       # (net, 矩形四角, 参考名, 层集合)
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            h = VIA_DIA / 2.0
            cx, cy = p.x / MM, p.y / MM
            copper.append((t.GetNetname(),
                           [(cx - h, cy - h), (cx + h, cy - h),
                            (cx + h, cy + h), (cx - h, cy + h)], "孔",
                           ALL_LAYERS))
        else:
            s, e = t.GetStart(), t.GetEnd()
            r = rect_from_seg((s.x / MM, s.y / MM), (e.x / MM, e.y / MM),
                               t.GetWidth() / MM)
            if r:
                li = _layer_idx(t.GetLayer())
                copper.append((t.GetNetname(), r, "走线",
                               set([li]) if li >= 0 else ALL_LAYERS))
    pads = []
    for f in board.GetFootprints():
        for p in f.Pads():
            pos = p.GetPosition()
            sz = p.GetSize()
            # ★**焊盘按矩形算, 不能当圆** (★SoM BTB 焊盘 0.2x0.7mm ⇒ 圆会白扣 0.25mm)
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
                    li = _layer_idx(l)
                    if li >= 0:
                        lays.add(li)
            except Exception:
                lays = set([0])
            if not lays:
                lays = set([0])
            pads.append((p.GetNetname(),
                         [(cx - hx, cy - hy), (cx + hx, cy - hy),
                          (cx + hx, cy + hy), (cx - hx, cy + hy)],
                         "%s.%s" % (f.GetReference(), p.GetNumber()),
                         lays))

    byu = {}
    for t in board.GetTracks():
        try:
            byu[t.m_Uuid.AsString()] = ("track", t)
        except Exception:
            pass
    for f in board.GetFootprints():
        for p in f.Pads():
            try:
                byu[p.m_Uuid.AsString()] = ("pad", p)
            except Exception:
                pass

    def endpoint(it):
        """★取这个 DRC 条目端点的 (类型, 几何, 描述)"""
        o = byu.get(it.get("uuid"))
        if o is None:
            pos = it.get("pos") or {}
            return ("pt", (pos.get("x", 0), pos.get("y", 0)),
                    (it.get("description") or "")[:40])
        kind, obj = o
        if kind == "pad":
            pos = obj.GetPosition()
            return ("pad", (pos.x / MM, pos.y / MM), "焊盘 %s.%s" % (
                obj.GetParentFootprint().GetReference(), obj.GetNumber()))
        s, e = obj.GetStart(), obj.GetEnd()
        return ("seg", ((s.x / MM, s.y / MM), (e.x / MM, e.y / MM)), "走线端")

    # ★★★**空间哈希 (1mm 粗格)**: ★**净距验算只看路径附近的铜** ⇒ 绕行搜索才跑得动
    #   (★不加这个: 每次验算扫全板 17k 铜 ⇒ 绕行候选几万条 ⇒ 跑一小时也不出结果)
    HASH_CELL = 1.0
    index = {}

    def _idx_add(net, rect, kind, lays):
        cx0 = int(math.floor(min(p[0] for p in rect) / HASH_CELL))
        cy0 = int(math.floor(min(p[1] for p in rect) / HASH_CELL))
        cx1 = int(math.floor(max(p[0] for p in rect) / HASH_CELL))
        cy1 = int(math.floor(max(p[1] for p in rect) / HASH_CELL))
        for cx in range(cx0, cx1 + 1):
            for cy in range(cy0, cy1 + 1):
                index.setdefault((cx, cy), []).append((net, rect, kind, lays))

    for (n, rect, kind, lays) in copper:
        _idx_add(n, rect, kind, lays)
    for (n, rect, ref, lays) in pads:
        _idx_add(n, rect, "焊盘[%s %s]" % (ref, n), lays)

    def _path_items(a1, a2, w):
        """★取路径附近的铜 (★只取附近的 ⇒ O(局部))"""
        L = math.hypot(a2[0] - a1[0], a2[1] - a1[1])
        seen = set()
        out = []
        steps = max(2, int(L / 0.25) + 2)
        for k in range(steps + 1):
            t = k / steps
            px = a1[0] + (a2[0] - a1[0]) * t
            py = a1[1] + (a2[1] - a1[1]) * t
            cx = int(math.floor(px / HASH_CELL))
            cy = int(math.floor(py / HASH_CELL))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for it in index.get((cx + dx, cy + dy), ()):
                        key = id(it[1])
                        if key in seen:
                            continue
                        seen.add(key)
                        out.append(it)
        return out

    def clearance_ok(net, a1, a2, w=None):
        """★候选线段 a1→a2 对所有异网铜的净距 (≥0.2) ⇒ 过了才落铜

        ★★**圆头修正 (实测依据)**: KiCad 的走线端点是**圆头** (半径 = 线宽/2)
        ⇒ ★**净距要按"胶囊形"算**, 不是矩形 ⇒
          实测: `RAIL_DEMO_5V` 直连 · 矩形算法算得余量 0.300mm ⇒ 实际 DRC 报
          "actual 0.1750mm" (= 0.300 − 0.125) ⇒ ★**矩形模型漏掉了圆头的 0.125mm**
        ⇒ ★**这里把线段两端各延长 w/2** (胶囊形的保守近似)"""
        ww = width if w is None else w
        dx, dy = a2[0] - a1[0], a2[1] - a1[1]
        L = math.hypot(dx, dy)
        if L == 0:
            return (-1e9, "零长")
        ux, uy = dx / L, dy / L
        e1 = (a1[0] - ux * ww / 2.0, a1[1] - uy * ww / 2.0)
        e2 = (a2[0] + ux * ww / 2.0, a2[1] + uy * ww / 2.0)
        cand = rect_from_seg(e1, e2, ww)
        if cand is None:
            return (-1e9, "零长")
        cb = rect_bbox(cand)
        worst = (1e9, "")
        for (n, rect, kind, lays) in _path_items(e1, e2, ww):
            if n == net:
                continue
            # ★★**分层判定**: 不同层的铜**不冲突** (★内层铜压在 F.Cu 焊盘下面完全合法)
            if PATH_LAYER not in lays:
                continue
            d = rect_rect_dist(cand, rect)
            if d < worst[0]:
                worst = (d, "%s[%s]" % (kind, n))
        return worst

    items = d.get("unconnected_items") or []
    added = []
    skipped = []
    # ★**绕行候选拐点**: 以两端点的包围盒为中心, 向外扩 detour_ext mm, 步长 0.25mm
    #   ⇒ ★**L 形 (2 段) 与 U 形 (3 段)** 各试一遍 ⇒ ★**全部用精确净距验算**, 过了才落铜
    def detour_corners(a1, a2):
        x0, x1_ = sorted((a1[0], a2[0]))
        y0, y1_ = sorted((a1[1], a2[1]))
        xs = []
        ys = []
        v = x0 - detour_ext
        while v <= x1_ + detour_ext + 1e-9:
            xs.append(round(v, 4))
            v += detour_step
        v = y0 - detour_ext
        while v <= y1_ + detour_ext + 1e-9:
            ys.append(round(v, 4))
            v += detour_step
        # ★**候选太多会指数爆炸** (★长距项尤其) ⇒ ★**每维限 40 个点**
        if len(xs) > 40:
            st = len(xs) // 40
            xs = xs[::st][:41]
        if len(ys) > 40:
            st = len(ys) // 40
            ys = ys[::st][:41]
        return xs, ys
    for it in items:
        its = it.get("items") or []
        if len(its) != 2:
            continue
        m0 = re.search(r"\[([^\]]+)\]", its[0].get("description") or "")
        m1 = re.search(r"\[([^\]]+)\]", its[1].get("description") or "")
        net = m0.group(1) if m0 else ""
        if not net or net != (m1.group(1) if m1 else ""):
            skipped.append(("两头不同网", net))
            continue
        (k0, p0, desc0) = endpoint(its[0])
        (k1, p1, desc1) = endpoint(its[1])
        cand = []
        if k0 == "seg" and k1 == "seg":      # ★两个端点都是走线 ⇒ 四种接法都试
            cand = [(p0[0], p1[0]), (p0[1], p1[1]), (p0[0], p1[1]), (p0[1], p1[0])]
        else:                                 # ★至少一个端点是焊盘 ⇒ 点到点
            q0 = p0[0] if k0 == "seg" else p0
            q1 = p1[0] if k1 == "seg" else p1
            cand = [(q0, q1)]
        # ★**两头间距** (★绕行只在近距项上试 ⇒ 长距项是"长距离布线能力"问题)
        dist = math.hypot(cand[0][1][0] - cand[0][0][0],
                          cand[0][1][1] - cand[0][0][1])
        best = None
        for (a1, a2) in cand:
            if a1 == a2:
                continue
            # ★**线宽扫描**: 优先用最宽的线 (★电流能力/工艺友好) ⇒ 从宽到窄试
            for w in widths:
                wres, who = clearance_ok(net, a1, a2, w)
                if wres >= CLEAR - EPS:
                    best = ((a1, a2), wres, who, w)
                    break
        # ★**直连不行 ⇒ 试 L 形 / U 形绕行** (★只对近距项 ⇒ 长距项是"长距离布线能力"问题, 不是绕行问题)
        is_detour = False
        if best is None and detour and dist <= detour_max_dist:
            xs, ys = detour_corners(cand[0][0], cand[0][1])
            paths = []
            for (a1, a2) in cand:
                for cx in xs:
                    paths.append([(a1, (cx, a1[1])), ((cx, a1[1]), a2)])
                for cy in ys:
                    paths.append([(a1, (a1[0], cy)), ((a1[0], cy), a2)])
                # ★U 形 (上下绕)
                for cy in ys:
                    for cx in xs:
                        paths.append([(a1, (a1[0], cy)), ((a1[0], cy), (cx, cy)),
                                      ((cx, cy), (a2[0], cy)), ((a2[0], cy), a2)])
            for p in paths:
                segs = [s for s in p if s[0] != s[1]]
                if not segs:
                    continue
                ok = True
                worstw = 1e9
                who = ""
                wuse = None
                for w in widths:
                    worstw = 1e9
                    who = ""
                    ok = True
                    for (s1, s2) in segs:
                        r, wh = clearance_ok(net, s1, s2, w)
                        if r < worstw:
                            worstw, who = r, wh
                        if r < CLEAR - EPS:
                            ok = False
                            break
                    if ok:
                        wuse = w
                        break
                if ok and wuse is not None:
                    best = (segs, worstw, who, wuse)
                    break
            if best is not None:
                is_detour = True
                segs = best[0]
                a1, a2 = segs[0][0], segs[-1][1]
            else:
                segs = None
        else:
            segs = None
        if best is None:
            # 记最接近的一次, 便于看差多少
            worst = None
            for (a1, a2) in cand:
                if a1 == a2:
                    continue
                for w in widths:
                    wres, who = clearance_ok(net, a1, a2, w)
                    if worst is None or wres > worst[1]:
                        worst = ((a1, a2), wres, who, w)
            skipped.append(("直连净距不足 %.3fmm (需 %.2f) %s"
                            % (worst[1] if worst else -1, CLEAR,
                               worst[2] if worst else ""), net))
            continue
        if is_detour:
            segs = best[0]
            w, who, use_w = best[1], best[2], best[3]
            a1, a2 = segs[0][0], segs[-1][1]
        else:
            (a1, a2), w, who, use_w = best
            segs = [(a1, a2)]
        code = board.GetNetcodeFromNetname(net)
        if code <= 0:
            skipped.append(("网名找不到", net))
            continue
        for (s1, s2) in segs:
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(s1[0]), pcbnew.FromMM(s1[1])))
            t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(s2[0]), pcbnew.FromMM(s2[1])))
            t.SetWidth(pcbnew.FromMM(use_w))
            t.SetLayer(_CU[PATH_LAYER])
            t.SetNetCode(code)
            board.Add(t)
        added.append((net, math.hypot(a2[0] - a1[0], a2[1] - a1[1]),
                      desc0, desc1, w))
        print("  ★直连补上 %-16s %6.3fmm  (%s ↔ %s) 线宽 %.3f 净距余量 %.3fmm"
              % (net, math.hypot(a2[0] - a1[0], a2[1] - a1[1]), desc0, desc1,
                 use_w, w))

    print("── 直连补上 %d 条 / 放弃 %d 条" % (len(added), len(skipped)))
    for (why, n) in skipped[:25]:
        print("    · 未成: %s  [%s]" % (why, n))

    for z in board.Zones():
        z.UnFill()
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(outp)
    print("── 已写出: %s (%d B)" % (outp, os.path.getsize(outp)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
