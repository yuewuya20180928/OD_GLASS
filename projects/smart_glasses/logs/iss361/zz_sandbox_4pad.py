#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-361 沙盒实验: 4 焊盘 gullwing 封装落到按键位 ⇒ C3 会不会红?
★ 副本落项目盘 tmp/iss361/ ⇒ 真板零改动
"""
import sys, os, shutil
sys.path.insert(0, "/home/yuewuya/kicad/squashfs-root/usr/lib/python3/dist-packages")
sys.path.insert(0, "/home/yuewuya/kicad/squashfs-root/usr/lib")
import pcbnew

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
SRC = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")
DST = os.path.join(ROOT, "tmp", "iss361", "sandbox_4pad_button.kicad_pcb")
os.makedirs(os.path.dirname(DST), exist_ok=True)
shutil.copy2(SRC, DST)

b = pcbnew.LoadBoard(DST)
target = None
for fp in b.GetFootprints():
    if fp.GetReference() == "SW_BOOT":
        target = fp
        break
assert target is not None, "找不到 SW_BOOT"
pads = list(target.Pads())
print("SW_BOOT 原 pad 数 = %d" % len(pads))
for p in pads:
    print("   pad %s net=%s at=%s" % (p.GetNumber(), p.GetNetname(), p.GetPosition()))

# 仿 Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2 (4 焊盘, 焊盘号 1,1,2,2)
# ⇒ 复制现有 pad1/pad2 各一份, 焊盘号保持 1 / 2, 位置按 KMR2 间距 (±2.05, ±0.8)
lay = b.GetLayerName
for num, dx, dy in (("1", -2.050, -0.800), ("2", -2.050, 0.800)):
    src = [p for p in pads if p.GetNumber() == num][0]
    new = pcbnew.PAD(target)
    new.SetNumber(num)
    new.SetShape(pcbnew.PAD_SHAPE_RECT)
    new.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    new.SetSize(pcbnew.VECTOR2I_MM(0.9, 1.0))
    new.SetLayerSet(src.GetLayerSet())
    new.SetPosition(pcbnew.VECTOR2I_MM(src.GetPosition().x / 1e6 + dx,
                                       src.GetPosition().y / 1e6 + dy))
    new.SetNet(src.GetNet())
    target.Add(new)
print("加焊盘后 pad 数 = %d" % len(list(target.Pads())))
pcbnew.SaveBoard(DST, b)
print("副本已落: %s" % DST)
