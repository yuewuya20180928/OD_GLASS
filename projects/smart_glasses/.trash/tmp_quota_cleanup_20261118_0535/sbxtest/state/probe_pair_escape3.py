#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_pair_escape3.py —— ★★★判定: A1 桶那 5 条, 到底要【pair-aware 走廊】还是【线宽 0.15】? ★★★

★★★**★为什么要有这个 (★2026-11-09 11:4x)★★★**
  ★**`probe_pair_escape2.py` 的结论**: ★**N 的【同向】与【反向】出脚道【都走不了】(★0/5)** ⇒ ★**"禁止回落"救不了** ⇒ ★★**pair-aware 不是这 5 条的答案** ★★
  · ★★**但那个测量有两处不可靠 (★自查发现的)**: ★★**(a) 焊盘被当成【圆】算 (★尺寸取 max(宽,长)=0.7mm ⇒ 过度保守) ⇒ ★★**(b) 没试【更细的线】** ★★
  ⇒ ★★★**⇒ 本脚本把两处都修掉: 焊盘按【矩形】算 (★与 v2 探针同源口径) + 同时算 W=0.25 与 W=0.15 两条 ★★★**
  ⇒ ★★★**判据: 若 W=0.15 时【同向】出脚道净距 ≥ 0.20 ⇒ ⇒【这 5 条只要 0.15mm, 不要 pair-aware】 ⇒ ★★**结论会改写 45 条的修法分工** ★★★**

★**只读, 不改板**
用法: bash state/pcbnew_py.sh state/probe_pair_escape3.py [板]
"""
import collections
import math
import os
import sys

import pcbnew

MM = 1000000.0
CLEAR = 0.20
ESC_LEN = 1.20

A1 = [
    ("CSI_D0_D0_N_SRC", "CSI_D0_D0_P_SRC"),
    ("CSI_D0_D1_N_SRC", "CSI_D0_D1_P_SRC"),
    ("CSI_D0_D3_N_SRC", "CSI_D0_D3_P_SRC"),
    ("DSI_D0_D2_N_SRC", "DSI_D0_D2_P_SRC"),
    ("DSI_D0_D3_N_SRC", "DSI_D0_D3_P_SRC"),
]


def main():
    boardp = sys.argv[1] if len(sys.argv) > 1 else "HW/PCB/demo_mainboard.kicad_pcb"
    b = pcbnew.LoadBoard(boardp)
    if b is None:
        print("★板读不出来")
        return 2

    # ★铜: 走线(线) / 过孔(圆) / 焊盘(★矩形 ★按真实宽长)
    coppers = []   # (net, layer, kind, geo, w)
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            coppers.append((t.GetNetname(), None, "VIA", (p.x / MM, p.y / MM), 0.6))
        else:
            s, e = t.GetStart(), t.GetEnd()
            coppers.append((t.GetNetname(), t.GetLayer(), "TRK",
                            (s.x / MM, s.y / MM, e.x / MM, e.y / MM), t.GetWidth() / MM))
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if not p.GetNetname():
                continue
            pos = p.GetPosition()
            sz = p.GetSize()
            coppers.append((p.GetNetname(), p.GetLayer(), "PAD",
                            (pos.x / MM, pos.y / MM, sz.x / MM, sz.y / MM), 0.0))

    def seg_pt_dist(px, py, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))

    def rect_dist(px, py, cx, cy, w, h):
        """★点到【矩形焊盘】的净距 (★矩形 = 中心 ± w/2, ± h/2)"""
        dx = max(abs(px - cx) - w / 2.0, 0.0)
        dy = max(abs(py - cy) - h / 2.0, 0.0)
        return math.hypot(dx, dy)

    def lane_worst(net, layer, x0, y0, dx, dy, length, W):
        """沿方向走 length, 与异网铜的最小净距 (★W = 本线宽)"""
        worst = 99.0
        who = "-"
        for (bn, bl, kind, g, w) in coppers:
            if bn == net:
                continue
            if bl is not None and layer is not None and bl != layer:
                continue
            n = 32
            for k in range(n + 1):
                px = x0 + dx * length * k / n
                py = y0 + dy * length * k / n
                if kind == "PAD":
                    dd = rect_dist(px, py, g[0], g[1], g[2], g[3])
                elif kind == "VIA":
                    dd = math.hypot(px - g[0], py - g[1]) - w / 2.0
                else:
                    dd = seg_pt_dist(px, py, g[0], g[1], g[2], g[3]) - w / 2.0
                dd -= W / 2.0
                if dd < worst:
                    worst = dd
                    who = "%s[%s]" % (bn, kind)
        return worst, who

    pads = collections.defaultdict(list)
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname():
                pads[p.GetNetname()].append(p)

    print("★A1 桶 5 条: 出脚道净距 vs 线宽 (★焊盘按矩形算 ★只读实测)")
    print("═" * 88)
    res = {0.25: 0, 0.15: 0}
    for n_net, p_net in A1:
        npads, ppads = pads.get(n_net, []), pads.get(p_net, [])
        if not npads or not ppads:
            continue
        best = None
        for pn in npads:
            for pp in ppads:
                a, c = pn.GetPosition(), pp.GetPosition()
                dd = math.hypot(a.x - c.x, a.y - c.y) / MM
                if best is None or dd < best[0]:
                    best = (dd, pn, pp)
        d, npad, ppad = best
        nx, ny = npad.GetPosition().x / MM, npad.GetPosition().y / MM
        px, py = ppad.GetPosition().x / MM, ppad.GetPosition().y / MM
        layer = npad.GetLayer()

        pdir = None
        for t in b.GetTracks():
            if t.GetNetname() != p_net or t.Type() == pcbnew.PCB_VIA_T:
                continue
            s, e = t.GetStart(), t.GetEnd()
            sx, sy, ex, ey = s.x / MM, s.y / MM, e.x / MM, e.y / MM
            if math.hypot(sx - px, sy - py) < 0.01:
                pdir = (ex - sx, ey - sy); break
            if math.hypot(ex - px, ey - py) < 0.01:
                pdir = (sx - px, sy - sy + (sy - py) * 0 + (sy - py) * 0); pdir = (sx - px, sy - py); break
        if pdir is None:
            continue
        mag = math.hypot(*pdir)
        sdx, sdy = pdir[0] / mag, pdir[1] / mag
        odx, ody = -sdx, -sdy

        line = "★ %-18s" % n_net
        print(line + " N(%.3f,%.3f)  P出脚方向(%.0f,%.0f)" % (nx, ny, sdx, sdy))
        for W in (0.25, 0.15):
            same, ws = lane_worst(n_net, layer, nx, ny, sdx, sdy, ESC_LEN, W)
            opp, wo = lane_worst(n_net, layer, nx, ny, odx, ody, ESC_LEN, W)
            ok = "✔可用" if same >= CLEAR else ("(反向✔)" if opp >= CLEAR else "✘都不行")
            if same >= CLEAR:
                res[W] += 1
            print("    W=%.2f: 同向 %+.3fmm (%s) · 反向 %+.3fmm (%s) ⇒ %s"
                  % (W, same, ws, opp, wo, ok))
        print("─" * 88)
    print("★⇒ W=0.25 时同向可用数 = %d/5   ★★W=0.15 时同向可用数 = %d/5" % (res[0.25], res[0.15]))
    print("★⇒ ★★若 W=0.15 ⇒ 5/5 ⇒ ⇒【这 5 条只要 0.15mm, 不要 pair-aware】★★")
    return 0


if __name__ == "__main__":
    sys.exit(main())
