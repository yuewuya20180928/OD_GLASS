#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-361 侦察 2: 板面 13 件的封装几何 (pcbnew) —— 只读"""
import sys, os
sys.path.insert(0, "/home/yuewuya/kicad/squashfs-root/usr/lib/python3/dist-packages")
sys.path.insert(0, "/home/yuewuya/kicad/squashfs-root/usr/lib")
import pcbnew

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
PCB = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")
REFS = ["CHG_GND_STAR", "D_ESD_CAM", "D_ESD_DEMO", "D_ESD_USB_D", "FB_DEMO",
        "Q_AND", "Q_ENVC", "Q_PG", "SW_BOOT", "SW_KEY_PWR", "SW_KEY_VM",
        "SW_KEY_VP", "SW_RST"]

b = pcbnew.LoadBoard(PCB)
print("=== 板面 13 件封装几何 ===")
for fp in b.GetFootprints():
    r = fp.GetReference()
    if r not in REFS:
        continue
    lib = fp.GetFPIDAsString()
    print("\n-- %s :: libid=%r  value=%r" % (r, lib, fp.GetValue()))
    try:
        bb = fp.GetBoundingBox()
        print("   bbox = %.3f x %.3f mm" % (pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight())))
    except Exception as e:
        print("   bbox err", e)
    for pad in fp.Pads():
        p = pad.GetPosition()
        sz = pad.GetSize()
        print("   pad %-4s net=%-16s pos=(%.3f,%.3f) size=(%.3f,%.3f) shape=%d" % (
            pad.GetNumber(), pad.GetNetname(), pcbnew.ToMM(p.x), pcbnew.ToMM(p.y),
            pcbnew.ToMM(sz.x), pcbnew.ToMM(sz.y), pad.GetShape()))

# === 全板封装统计 ===
fps = list(b.GetFootprints())
print("\n=== 全板 ===")
print("  footprint total =", len(fps))
libs = set()
for fp in fps:
    libs.add(fp.GetFPIDAsString())
print("  GetFPIDAsString() 唯一值 =", sorted(repr(x) for x in libs))
print("  有 libid 的件数 =", len([f for f in fps if f.GetFPIDAsString()]))
# 每件的 pad 数分布
from collections import Counter
c = Counter(len(list(f.Pads())) for f in fps)
print("  pad 数分布 =", dict(sorted(c.items())))
