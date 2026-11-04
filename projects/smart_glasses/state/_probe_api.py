#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_probe_api.py —— 探针: 板边几何 API (临时)"""
import os
import pcbnew

MM = 1e6
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
b = pcbnew.LoadBoard(PCB)

print("--- drawings on Edge.Cuts ---")
for d in b.GetDrawings():
    ln = d.GetLayerName()
    if ln != "Edge.Cuts":
        continue
    print("  class=%s shape=%s start=%s end=%s" % (
        d.GetClass(), d.GetShape(), d.GetStart(), d.GetEnd()))
    try:
        print("     arc angle:", d.GetArcAngle().AsDegrees())
    except Exception as e:
        print("     no arc angle:", e)

print("--- GetBoardPolygonOutlines ---")
try:
    poly = b.GetBoardPolygonOutlines()
    print("  ok type:", type(poly))
    n = poly.OutlineCount()
    print("  outline count:", n)
    ch = poly.Outline(0)
    print("  chain type:", type(ch))
    try:
        pts = ch.Points()
        print("  points:", len(pts), [(round(p.x / MM, 3), round(p.y / MM, 3)) for p in pts[:8]])
    except Exception as e:
        print("  Points() fail:", e)
        print("  CPoint(0):", ch.CPoint(0), " PointCount:", ch.PointCount())
except Exception as e:
    print("  GetBoardPolygonOutlines fail:", e)

print("--- board setup edge clearance ---")
try:
    ds = b.GetDesignSettings()
    print("  m_CopperEdgeClearance =", ds.m_CopperEdgeClearance)
except Exception as e:
    print("  fail:", e)
print("--- pcbnew consts ---")
print("  SHAPE_T_SEGMENT", pcbnew.SHAPE_T_SEGMENT, "SHAPE_T_ARC", pcbnew.SHAPE_T_ARC)
