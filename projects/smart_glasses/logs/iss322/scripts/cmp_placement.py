#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-322 · tmp 沙盒脚本 · ★best_unc23 板 vs 现役板: 布局是否同源★ (pcbnew 直读)"""
import sys
import pcbnew

MM = 1e6


def fps(path):
    b = pcbnew.LoadBoard(path)
    out = {}
    for f in b.GetFootprints():
        p = f.GetPosition()
        out[f.GetReference()] = (round(p.x / MM, 3), round(p.y / MM, 3))
    return out


A = fps("HW/PCB/demo_mainboard.kicad_pcb")
B = fps(sys.argv[1] if len(sys.argv) > 1
        else "state/.lastgood/best_unc23_clrfix.kicad_pcb")
print("current footprints=%d   cmp footprints=%d" % (len(A), len(B)))
common = set(A) & set(B)
same = [k for k in common if abs(A[k][0] - B[k][0]) < 0.01 and abs(A[k][1] - B[k][1]) < 0.01]
mv = [(k, A[k], B[k]) for k in sorted(common) if k not in same]
print("common refs=%d   SAME position=%d (%.1f%%)   moved=%d"
      % (len(common), len(same), 100.0 * len(same) / max(1, len(common)), len(mv)))
for k, a, b in mv[:60]:
    print("   MOVED %-16s cur=(%.2f,%.2f)  cmp=(%.2f,%.2f)" % (k, a[0], a[1], b[0], b[1]))
print("only-in-current:", sorted(set(A) - set(B)))
print("only-in-cmp    :", sorted(set(B) - set(A)))
