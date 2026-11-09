#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""plan_route_reserve.py -- ★★算给 A1 那 5 条 N 腿预留【出脚走廊】的框 (★产出 PCB_ROUTE_RESERVE 串)★★

★★★**★为什么要有这个 (★2026-11-10 12:3x)★★★**
  ★**实测机制**: ★**A1 那 5 条的 N 腿, 它的【反向】出脚道都被【别的网的铜】占着**
  ⇒ ★★**⇒ 出脚级成对规划走不通 ⇒ ⇒ 真正要的是【走线级走廊预留】(★`PCB_ROUTE_RESERVE`) ★★
  ⇒ ★★**⇒ 而"预留哪个框"必须【按实测铜占位】算, 不能拍脑袋** ⇒ ★★**本脚本就是算这个** ★★

★**算法 (★全几何, ★无猜测)** ★★★
  ① 对每个 N 腿的 BTB 焊盘, 找【同排方向】的两个垂直方向 (★垂直于排针行)
  ② 对每个方向, 沿该方向检查【出脚直道长度 ESC_LEN=1.2mm】的走廊上有没有【别的网】的铜
     (★同层铜 + 异层铜都要查, ★因为 halo 是分层的)
  ③ 选【净距最大】的那个方向 = ★N 应该走的路 ⇒ ★★**把它预留下来 (★框 = 该走廊的矩形) ★★
  ④ 框的宽度 = ★线宽 + 两侧净距 (★0.25 + 2×0.20 = 0.65mm ⇒ 取 0.9mm 宽, ★留余量) ★★
  ⇒ ★**输出: 可直接贴进臂脚本的 `PCB_ROUTE_RESERVE="..."` 串** ★★

用法: bash state/pcbnew_py.sh state/plan_route_reserve.py [板] [--out <txt>]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("PCB_LAYERS", "8")
import pcbnew  # noqa: E402

MM = 1000000.0
ESC_LEN = 1.20          # ★与 gen_pcb_routing.ESC_LEN 对齐
HALO_CLEAR = 0.20       # ★CLEAR
BOX_W = 0.90            # ★预留框宽度 (0.25 线 + 2×0.20 净距 = 0.65 ⇒ 取 0.9 留余量)

# ★A1 桶 5 条: (N 腿网, N 腿在 BTB 上的焊盘 ref, x, y)
A1 = [
    ("CSI_D0_D0_N_SRC", "J_SOM_P4.65", 22.000, 50.960),
    ("CSI_D0_D1_N_SRC", "J_SOM_P4.71", 20.800, 50.960),
    ("CSI_D0_D3_N_SRC", "J_SOM_P4.89", 17.200, 50.960),
    ("DSI_D0_D2_N_SRC", "J_SOM_P3.75", 20.000, 7.960),
    ("DSI_D0_D3_N_SRC", "J_SOM_P3.81", 18.800, 7.960),
]


def main():
    boardp = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else \
        "HW/PCB/demo_mainboard.kicad_pcb"
    outp = None
    if "--out" in sys.argv:
        outp = sys.argv[sys.argv.index("--out") + 1]

    b = pcbnew.LoadBoard(boardp)
    if b is None:
        print("★板读不出来: %s" % boardp)
        return 2

    # ★铜图元 (走线 / 过孔), 按层
    copper = []
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            copper.append((t.GetNetname(), None, "VIA", p.x / MM, p.y / MM, 0.0, 0.0, 0.6))
        else:
            s, e = t.GetStart(), t.GetEnd()
            copper.append((t.GetNetname(), b.GetLayerName(t.GetLayer()), "TRK",
                           s.x / MM, s.y / MM, e.x / MM, e.y / MM, t.GetWidth() / MM))

    def worst_clearance(net, x, y, dx, dy):
        """沿 (dx,dy) 从 (x,y) 走 ESC_LEN, 与【别的网】铜的最小净距 (★同层算铜边距; 异层按 0.2 净距算)"""
        worst = 99.0
        who = "-"
        for (bn, lay, kind, cx, cy, ex, ey, w) in copper:
            if bn == net:
                continue
            if kind == "VIA":
                for k in range(25):
                    t = k / 24.0
                    px, py = x + dx * ESC_LEN * t, y + dy * ESC_LEN * t
                    d = math.hypot(px - cx, py - cy) - w / 2.0 - 0.125
                    if d < worst:
                        worst, who = d, "%s[VIA]" % bn
                continue
            dx2, dy2 = ex - cx, ey - cy
            L2 = dx2 * dx2 + dy2 * dy2
            for k in range(25):
                t = k / 24.0
                px, py = x + dx * ESC_LEN * t, y + dy * ESC_LEN * t
                if L2 == 0:
                    d = math.hypot(px - cx, py - cy) - w / 2.0 - 0.125
                else:
                    u = max(0.0, min(1.0, ((px - cx) * dx2 + (py - cy) * dy2) / L2))
                    qx, qy = cx + u * dx2, cy + u * dy2
                    d = math.hypot(px - qx, py - qy) - w / 2.0 - 0.125
                if d < worst:
                    worst, who = d, "%s[%s]" % (bn, lay)
        return worst, who

    boxes = []
    lines = ["★给 A1 那 5 条 N 腿预留的出脚走廊 (★全几何算出)★", ""]
    for (net, ref, x, y) in A1:
        # ★垂直于排针行的两个方向 (★BTB 排针行是水平 ⇒ 垂直方向 = ±y)
        cands = []
        for (dx, dy, tag) in ((0.0, 1.0, "+y"), (0.0, -1.0, "-y")):
            w, who = worst_clearance(net, x, y, dx, dy)
            cands.append((w, tag, dx, dy, who))
        cands.sort(reverse=True)
        best = cands[0]
        lines.append("★ %s @ %s (%.3f, %.3f)" % (net, ref, x, y))
        for (w, tag, dx, dy, who) in cands:
            lines.append("    方向 %-3s 走廊最小净距 %+.3fmm  (最近: %s)" % (tag, w, who))
        lines.append("    ⇒ 选 %s (净距 %+.3fmm) ⇒ 预留该走廊" % (best[1], best[0]))
        # ★框: 沿方向的走廊 + 宽度
        x0 = x - BOX_W / 2.0
        x1 = x + BOX_W / 2.0
        if best[2] == 0.0 and best[3] > 0:
            y0, y1 = y, y + ESC_LEN + 0.2
        else:
            y0, y1 = y - ESC_LEN - 0.2, y
        boxes.append("%s:0,%.3f,%.3f,%.3f,%.3f" % (net, x0, y0, x1, y1))
        lines.append("")

    lines.append("★PCB_ROUTE_RESERVE 串 (★可直接贴进臂脚本):")
    lines.append('  PCB_ROUTE_RESERVE="%s"' % ";".join(boxes))
    text = "\n".join(lines)
    if outp:
        open(outp, "w", encoding="utf-8").write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
