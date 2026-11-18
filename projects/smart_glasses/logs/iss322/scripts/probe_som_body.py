#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-322 · tmp 沙盒脚本 · ★★SoM 主体区 (x 8..76, y 6..56) 的【逐层可穿越性】★★
★回答: 23 条 DSI/CSI 腿"必须跨 SoM 主体" ⇒ ★在【内层】上是不是真的过不去?★
"""
import collections
import pcbnew

MM = 1e6
b = pcbnew.LoadBoard("HW/PCB/demo_mainboard.kicad_pcb")
X0, X1, Y0, Y1 = 8.0, 76.0, 6.0, 56.0
CU = ["F.Cu", "In1.Cu", "In2.Cu", "In3.Cu", "In4.Cu", "In5.Cu", "In6.Cu", "B.Cu"]
LI = {n: i for i, n in enumerate(CU)}


def inb(x, y):
    return X0 <= x <= X1 and Y0 <= y <= Y1


print("═══ SoM 主体区 x %.0f..%.0f  y %.0f..%.0f (%.0f x %.0f mm) ═══"
      % (X0, X1, Y0, Y1, X1 - X0, Y1 - Y0))
print()
print("── ① 区内的封装 (★按是否通孔分开★) ──")
inside = []
for f in b.GetFootprints():
    bb = f.GetBoundingBox()
    x0, y0 = bb.GetLeft() / MM, bb.GetTop() / MM
    x1, y1 = bb.GetRight() / MM, bb.GetBottom() / MM
    if x1 < X0 or x0 > X1 or y1 < Y0 or y0 > Y1:
        continue
    tht = 0
    smd = 0
    pads_on = collections.Counter()
    for p in f.Pads():
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
            tht += 1
        else:
            smd += 1
        pads_on[p.GetLayerSet().FmtHex()] += 1
    inside.append((f.GetReference(), x0, y0, x1, y1, tht, smd))
inside.sort(key=lambda t: t[0])
for r, x0, y0, x1, y1, tht, smd in inside:
    print("   %-18s x %6.2f..%6.2f  y %6.2f..%6.2f   PTH焊盘=%-3d SMD焊盘=%-3d"
          % (r, x0, x1, y0, y1, tht, smd))
print("   ⇒ 区内封装总数 = %d" % len(inside))
print()

print("── ② J_SOM_P1..P4 的焊盘落在哪些层 (★决定内层是不是被封★) ──")
for f in b.GetFootprints():
    if not f.GetReference().startswith("J_SOM_P"):
        continue
    lay = collections.Counter()
    for p in f.Pads():
        ls = p.GetLayerSet()
        for nm in CU:
            if ls.Contains(pcbnew.LayerId(LI[nm]) if False else
                           getattr(pcbnew, nm.replace(".Cu", "_Cu"), pcbnew.F_Cu)):
                lay[nm] += 1
    tht = sum(1 for p in f.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH)
    smd = sum(1 for p in f.Pads() if p.GetAttribute() != pcbnew.PAD_ATTRIB_PTH)
    print("   %-10s 焊盘 %d (PTH %d / SMD %d)  层分布: %s"
          % (f.GetReference(), len(f.Pads()), tht, smd, dict(lay)))
print()

print("── ③ 区内逐层铜占布 (★走线段 + 过孔 + 区内焊盘, 每层多少 mm/多少个★) ──")
seg = collections.defaultdict(float)
segn = collections.Counter()
via = collections.Counter()
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        p = t.GetPosition()
        if inb(p.x / MM, p.y / MM):
            via["ALL(通孔)"] += 1
        continue
    s, e = t.GetStart(), t.GetEnd()
    sx, sy, ex, ey = s.x / MM, s.y / MM, e.x / MM, e.y / MM
    if not (inb(sx, sy) or inb(ex, ey)):
        continue
    L = ((s.x - e.x) ** 2 + (s.y - e.y) ** 2) ** 0.5 / MM
    nm = b.GetLayerName(t.GetLayer())
    seg[nm] += L
    segn[nm] += 1
for nm in CU:
    print("   %-7s 走线段 %4d 条 / %8.2f mm" % (nm, segn.get(nm, 0), seg.get(nm, 0.0)))
print("   区内通孔(过孔) = %d 个 (★过孔是全层障碍★)" % via["ALL(通孔)"])
print()

print("── ④ 区内各层的【自由面积占比】粗估 (★走线+过孔扫过的包围盒面积占比★) ──")
for nm in CU:
    cov = 0.0
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            if inb(p.x / MM, p.y / MM):
                r = t.GetWidth(pcbnew.F_Cu) / MM / 2.0
                cov += (2 * r) ** 2
            continue
        if b.GetLayerName(t.GetLayer()) != nm:
            continue
        s, e = t.GetStart(), t.GetEnd()
        if not (inb(s.x / MM, s.y / MM) or inb(e.x / MM, e.y / MM)):
            continue
        w = t.GetWidth() / MM
        L = ((s.x - e.x) ** 2 + (s.y - e.y) ** 2) ** 0.5 / MM
        cov += L * w
    area = (X1 - X0) * (Y1 - Y0)
    print("   %-7s 铜投影面积 ≈ %8.1f mm² / %8.1f mm²  = %.2f%%"
          % (nm, cov, area, 100.0 * cov / area))
