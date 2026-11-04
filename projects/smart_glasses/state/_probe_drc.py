#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_probe_drc.py —— 探针: 归类 DRC 违规 (临时)"""
import os
import json
import math
import collections
import pcbnew

MM = 1e6
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
d = json.load(open("/tmp/_layout_done_drc.json"))
v = d.get("violations") or []

# 板上的走线/过孔
b = pcbnew.LoadBoard(PCB)
tracks, vias = [], []
for t in b.GetTracks():
    if t.GetClass() == "PCB_TRACK":
        tracks.append((t.GetNetname(), t.GetStart().x / MM, t.GetStart().y / MM,
                       t.GetEnd().x / MM, t.GetEnd().y / MM,
                       t.GetWidth() / MM, t.GetLayerName()))
    elif t.GetClass() == "PCB_VIA":
        vias.append((t.GetNetname(), t.GetPosition().x / MM, t.GetPosition().y / MM,
                     t.GetWidth() / MM, t.GetLayerName()))


def pt_seg(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 < 1e-12:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


print("=== 违规按类型 ===")
for k, n in collections.Counter(x.get("type") for x in v).most_common():
    print("  %-24s %d" % (k, n))

print("\n=== 过孔间距检查 (孔心距 < 0.8mm ⇒ 盘会碰) ===")
bad = 0
for i in range(len(vias)):
    for j in range(i + 1, len(vias)):
        if vias[i][0] == vias[j][0]:
            continue
        d0 = math.hypot(vias[i][1] - vias[j][1], vias[i][2] - vias[j][2])
        if d0 < 0.8:
            bad += 1
            if bad <= 8:
                print("  %.3fmm  %s @(%.2f,%.2f)  vs  %s @(%.2f,%.2f)"
                      % (d0, vias[i][0], vias[i][1], vias[i][2],
                         vias[j][0], vias[j][1], vias[j][2]))
print("  过孔对 (<0.8mm): %d" % bad)

print("\n=== 过孔 vs 走线 (中心距) 抽样 ===")
cnt = 0
worst = []
for (vn, vx, vy, vw, vl) in vias:
    for (tn, x1, y1, x2, y2, tw, tl) in tracks:
        if tn == vn:
            continue
        dd = pt_seg(vx, vy, x1, y1, x2, y2)
        need = vw / 2 + tw / 2 + 0.2
        if dd < need:
            worst.append((dd - need, dd, need, vn, vx, vy, tn, x1, y1, x2, y2, tw))
            cnt += 1
worst.sort()
print("  违规对: %d" % cnt)
for w in worst[:12]:
    print("  超 %.3fmm  实际中心距 %.3f (需 %.3f)  via %s@(%.2f,%.2f) vs trk %s (%.2f,%.2f)->(%.2f,%.2f) w=%.2f"
          % (w[0], w[1], w[2], w[3], w[4], w[5], w[6], w[7], w[8], w[9], w[10], w[11]))

print("\n=== 过孔 vs 焊盘 (中心距) 抽样 ===")
pads = []
for fp in b.GetFootprints():
    for pad in fp.Pads():
        pads.append((pad.GetNetname(), pad.GetPosition().x / MM, pad.GetPosition().y / MM,
                     pad.GetSize().x / MM, pad.GetSize().y / MM, fp.GetReference(), pad.GetNumber()))
cnt = 0
for (vn, vx, vy, vw, vl) in vias:
    for (pn, px, py, pw, ph, pr, pnum) in pads:
        if pn == vn:
            continue
        dx = max(abs(px - vx) - (pw / 2 + vw / 2), 0.0)
        dy = max(abs(py - vy) - (ph / 2 + vw / 2), 0.0)
        dd = math.hypot(dx, dy)
        if dd < 0.2:
            cnt += 1
            if cnt <= 10:
                print("  %.3fmm via %s@(%.2f,%.2f) vs pad %s.%s net=%s @(%.2f,%.2f)"
                      % (dd, vn, vx, vy, pr, pnum, pn, px, py))
print("  违规对: %d" % cnt)
