#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-361 侦察 8: (a) TestPoint_Pad_D1.0mm 官方封装真实焊盘数 (b) 13 件板面 fab 外框/中心距"""
import sys, os
sys.path.insert(0, "/home/yuewuya/kicad/squashfs-root/usr/lib/python3/dist-packages")
sys.path.insert(0, "/home/yuewuya/kicad/squashfs-root/usr/lib")
import pcbnew

LR = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"

# ---------- (a) 官方 TestPoint_Pad_D1.0mm 实测焊盘数 ----------
print("=== (a) 官方 TestPoint:TestPoint_Pad_D1.0mm 实测 ===")
import io
_fp_txt = open(os.path.join(LR, "TestPoint.pretty", "TestPoint_Pad_D1.0mm.kicad_mod"),
               encoding="utf-8").read()
fpr = pcbnew.FootprintLoad
try:
    fpr = pcbnew.FootprintLoad(io.StringIO(_fp_txt))
except Exception as e:
    print("  FootprintLoad(StringIO) 失败: %s" % e)
    fpr = None
if fpr is None:
    print("  ⇒ 改走纯文本计焊盘")
    import re as _re
    _pads = _re.findall(r'\(pad\s+"([^"]*)"', _fp_txt)
    print("  焊盘数 = %d · 焊盘号 = %s" % (len(_pads), _pads))
    for _m in _re.finditer(r'\(pad\s+"([^"]*)"\s+(\w+)\s+(\w+)\s*\(at ([^)]*)\)\s*\(size ([^)]*)\)', _fp_txt):
        print("    pad %-3s %-6s %-9s at=(%s) size=(%s)"
              % (_m.group(1), _m.group(2), _m.group(3), _m.group(4), _m.group(5)))
else:
    pads = list(fpr.Pads())
    print("  焊盘数 = %d" % len(pads))
    for p in pads:
        print("    pad %-3s shape=%d size=(%.3f,%.3f) at=(%.3f,%.3f)"
              % (p.GetNumber(), p.GetShape(),
                 pcbnew.ToMM(p.GetSize().x), pcbnew.ToMM(p.GetSize().y),
                 pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)))
    print("  F.Fab 图形数 = %d" % len(list(fpr.GraphicalItems())))
    print("  attr exclude_from_pos_files = %s" % fpr.GetAttributes())

# ---------- (b) 13 件板面几何 ----------
print("\n=== (b) 13 件板面 fab 外框 / 焊盘中心距 ===")
b = pcbnew.LoadBoard(os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb"))
G13 = ["CHG_GND_STAR", "D_ESD_CAM", "D_ESD_DEMO", "D_ESD_USB_D", "FB_DEMO", "Q_AND",
       "Q_ENVC", "Q_PG", "SW_BOOT", "SW_KEY_PWR", "SW_KEY_VM", "SW_KEY_VP", "SW_RST"]
for fp in b.GetFootprints():
    r = fp.GetReference()
    if r not in G13:
        continue
    # fab 外框: 取 F.Fab 层图形 bbox
    xs, ys = [], []
    for gi in fp.GraphicalItems():
        if gi.GetLayer() != pcbnew.F_Fab:
            continue
        bb = gi.GetBoundingBox()
        xs += [pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetRight())]
        ys += [pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetBottom())]
    fab = (max(xs) - min(xs), max(ys) - min(ys)) if xs else (0, 0)
    pads = sorted(list(fp.Pads()), key=lambda p: int(p.GetNumber()))
    pos = [(pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)) for p in pads]
    sizes = [(pcbnew.ToMM(p.GetSize().x), pcbnew.ToMM(p.GetSize().y)) for p in pads]
    # 中心距: 相邻焊盘间最大距离
    import math
    d = 0.0
    for i in range(len(pos)):
        for j in range(i + 1, len(pos)):
            dd = math.hypot(pos[i][0] - pos[j][0], pos[i][1] - pos[j][1])
            d = max(d, dd)
    print("  %-14s pads=%d · fab外框 %.2f x %.2f mm · 焊盘尺寸 %s · 最大中心距 %.3f mm"
          % (r, len(pads), fab[0], fab[1],
             "x".join("%.3fx%.3f" % s for s in sizes), d))
    print("                 焊盘中心 = %s" % ["(%.3f,%.3f)" % p for p in pos])
