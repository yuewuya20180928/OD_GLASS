#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_probe_edge.py —— 探针: 找板边净距违规的具体走线 (临时, 用完删)"""
import os
import pcbnew

MM = 1e6
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")

b = pcbnew.LoadBoard(PCB)
bb = b.GetBoardEdgesBoundingBox()
print("board bbox mm: L=%.4f T=%.4f R=%.4f B=%.4f  (w=%.3f h=%.3f)" % (
    bb.GetLeft() / MM, bb.GetTop() / MM, bb.GetRight() / MM, bb.GetBottom() / MM,
    (bb.GetRight() - bb.GetLeft()) / MM, (bb.GetBottom() - bb.GetTop()) / MM))

# 板边线段
segs = []
for d in b.GetDrawings():
    try:
        if d.GetClass() == "PCB_SHAPE" and d.GetShape() == pcbnew.SHAPE_T_SEGMENT:
            segs.append((d.GetStart().x / MM, d.GetStart().y / MM,
                         d.GetEnd().x / MM, d.GetEnd().y / MM,
                         d.GetLayerName()))
    except Exception:
        pass
print("edge segments: %d" % len(segs))
for s in segs[:10]:
    print("   ", s)


def seg_edge_dist(px, py, ax, ay, bx, by):
    """点到线段的距离 (只看垂直距离, 端点也算)"""
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 < 1e-12:
        return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return ((px - (ax + t * dx)) ** 2 + (py - (ay + t * dy)) ** 2) ** 0.5


def track_edge_clear(seg, w):
    """走线段到板边的净距 (铜外缘到板边)"""
    x1, y1, x2, y2 = seg[:4]
    best = 1e9
    n = 8
    for k in range(n + 1):
        t = k / float(n)
        px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        for (ax, ay, bx, by, ln) in segs:
            d = seg_edge_dist(px, py, ax, ay, bx, by)
            if d < best:
                best = d
    return best - w / 2.0


print("\n=== 违规走线 (净距 < 0.5mm) ===")
cnt = 0
for t in b.GetTracks():
    cls = t.GetClass()
    if cls == "PCB_TRACK":
        s = (t.GetStart().x / MM, t.GetStart().y / MM, t.GetEnd().x / MM, t.GetEnd().y / MM)
        w = t.GetWidth() / MM
        c = track_edge_clear(s, w)
        if c < 0.5:
            cnt += 1
            print("  TRACK net=%-22s w=%.3f (%8.3f,%8.3f)->(%8.3f,%8.3f) clearance=%.4f layer=%s" % (
                t.GetNetname(), w, s[0], s[1], s[2], s[3], c, t.GetLayerName()))
    elif cls == "PCB_VIA":
        c = track_edge_clear((t.GetPosition().x / MM, t.GetPosition().y / MM,
                               t.GetPosition().x / MM, t.GetPosition().y / MM),
                              t.GetWidth() / MM)
        if c < 0.5:
            cnt += 1
            print("  VIA  net=%-22s d=%.3f at (%.3f,%.3f) clearance=%.4f" % (
                t.GetNetname(), t.GetWidth() / MM, t.GetPosition().x / MM,
                t.GetPosition().y / MM, c))
print("total <0.5mm: %d" % cnt)

print("\n=== CSI_D0_CK_N 相关焊盘/走线 ===")
for fp in b.GetFootprints():
    for pad in fp.Pads():
        if pad.GetNetname() == "CSI_D0_CK_N":
            r = pad.GetBoundingBox()
            print("  PAD %s.%s rect=(%.3f,%.3f)-(%.3f,%.3f) center=(%.3f,%.3f)" % (
                fp.GetReference(), pad.GetNumber(), r.GetLeft() / MM, r.GetTop() / MM,
                r.GetRight() / MM, r.GetBottom() / MM,
                pad.GetPosition().x / MM, pad.GetPosition().y / MM))
for t in b.GetTracks():
    if t.GetClass() == "PCB_TRACK" and t.GetNetname() == "CSI_D0_CK_N":
        s = (t.GetStart().x / MM, t.GetStart().y / MM, t.GetEnd().x / MM, t.GetEnd().y / MM)
        print("  TRACK w=%.3f (%.3f,%.3f)->(%.3f,%.3f) clr=%.4f" % (
            t.GetWidth() / MM, s[0], s[1], s[2], s[3], track_edge_clear(s, t.GetWidth() / MM)))

# 板边最小净距统计 (全部走线)
print("\n=== 全板走线到板边净距最小 10 条 ===")
res = []
for t in b.GetTracks():
    if t.GetClass() != "PCB_TRACK":
        continue
    s = (t.GetStart().x / MM, t.GetStart().y / MM, t.GetEnd().x / MM, t.GetEnd().y / MM)
    w = t.GetWidth() / MM
    res.append((track_edge_clear(s, w), t.GetNetname(), s, w))
res.sort()
for (c, nn, s, w) in res[:10]:
    print("  clr=%.4f w=%.3f net=%-22s (%.3f,%.3f)->(%.3f,%.3f)" % (c, w, nn, s[0], s[1], s[2], s[3]))
