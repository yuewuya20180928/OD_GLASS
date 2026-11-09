#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_pair_escape.py —— ★★量清"A1 桶 5 条"为什么出不来: ★P 腿的出脚方向 vs N 腿需要的方向

★★★**★为什么要有这个 (★2026-11-09 11:2x)★★★**
  ★**A1 桶 (5 条)**: ★**端点是真墙, 堵的是【自己差分伙伴腿】(净距恰好 0.200mm)**
  ⇒ ★**怀疑**: ★**P 腿的出脚直道 (escape_stub) 占了 N 腿唯一能出的方向**
    ⇒ ★**机制 (从代码读到的)**: ★**`escape_stub` 里 N 侧"优先走与伙伴不同的方向", 但★不行就【回落】到伙伴用过的方向**
      ⇒ ★★**回落那一支 = N 的出脚直道与 P 的直道同向 ⇒ ⇒ 净距不够 ⇒ ⇒ N 出不来** ★★
  ★**本脚本**: ★**在真实板上量【P 腿出脚方向】vs【N 腿焊盘到最近异网铜的方向】⇒ ⇒ 验证或推翻这个假设** ★★
  ★**只读, 不改板**

用法: bash state/pcbnew_py.sh state/probe_pair_escape.py [板]
"""
import collections
import math
import os
import sys

import pcbnew

MM = 1000000.0

# ★A1 桶: (N 腿网名, P 腿网名)
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

    # ★按网收集焊盘与走线
    pads = collections.defaultdict(list)
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname():
                pads[p.GetNetname()].append(p)
    tracks = collections.defaultdict(list)
    for t in b.GetTracks():
        tracks[t.GetNetname()].append(t)

    def seg_dist(px, py, s, e):
        x1, y1 = s
        x2, y2 = e
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        tt = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        return math.hypot(px - (x1 + tt * dx), py - (y1 + tt * dy))

    print("★A1 桶 5 条的出脚方向分析 (★真实板实测)")
    print("═" * 78)
    for n_net, p_net in A1:
        npads = pads.get(n_net, [])
        ppads = pads.get(p_net, [])
        if not npads or not ppads:
            print("★ %-18s 缺焊盘 (N:%d P:%d)" % (n_net, len(npads), len(ppads)))
            continue
        # ★取 N 与 P 最近的焊盘对
        best = None
        for pn in npads:
            for pp in ppads:
                a, c = pn.GetPosition(), pp.GetPosition()
                d = math.hypot(a.x - c.x, a.y - c.y) / MM
                if best is None or d < best[0]:
                    best = (d, pn, pp)
        d, npad, ppad = best
        nx, ny = npad.GetPosition().x / MM, npad.GetPosition().y / MM
        px, py = ppad.GetPosition().x / MM, ppad.GetPosition().y / MM

        # ★P 腿从自己焊盘出去的方向 (取第一条以焊盘中心为端点的走线)
        pdirs = []
        for t in tracks.get(p_net, []):
            if t.Type() == pcbnew.PCB_VIA_T:
                continue
            s, e = t.GetStart(), t.GetEnd()
            sx, sy = s.x / MM, s.y / MM
            ex, ey = e.x / MM, e.y / MM
            if math.hypot(sx - px, sy - py) < 0.01:
                pdirs.append((round(ex - sx, 3), round(ey - sy, 3)))
            elif math.hypot(ex - px, ey - py) < 0.01:
                pdirs.append((round(sx - px, 3), round(sy - py, 3)))
        # ★P 腿铜到 N 焊盘中心的距离
        nearest = None
        for t in tracks.get(p_net, []):
            if t.Type() == pcbnew.PCB_VIA_T:
                continue
            s, e = t.GetStart(), t.GetEnd()
            dd = seg_dist(nx, ny, (s.x / MM, s.y / MM), (e.x / MM, e.y / MM))
            if nearest is None or dd < nearest:
                nearest = dd
        print("★ %s / %s" % (n_net, p_net))
        print("    N 焊盘 (%.3f, %.3f)   P 焊盘 (%.3f, %.3f)   中心距 %.3fmm" % (nx, ny, px, py, d))
        print("    P 腿出脚方向: %s" % (pdirs[:3] if pdirs else "★无 (P 也零铜?)"))
        print("    P 腿铜到 N 焊盘中心最近: %.3fmm" % (nearest if nearest is not None else -1))
        print("─" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
