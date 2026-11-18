#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_probe_nets.py —— 探针: 未连网的焊盘分布 (临时)"""
import os
import math
import pcbnew

MM = 1e6
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
b = pcbnew.LoadBoard(os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb"))

NETS = ["VDD_3V3_IO", "LIGHT_3V3", "V_CORE", "V_SOC_IO", "BAT", "BAT_SW",
        "SENSOR_CORE", "SENSOR_AVDD", "LIGHT_1V8", "LIGHT_5V", "VDD_1V8_IO",
        "RESET_N", "RESET_N_SOC", "CAM_RESET_N", "PWR_GOOD", "PWR_ON",
        "PG_AND", "BOOT_N", "CARRIER_BOARD_EN", "EN_VCORE", "VBUS_DET_D",
        "SUPV_SENSE", "GND"]

pads = []
for fp in b.GetFootprints():
    for pad in fp.Pads():
        r = pad.GetBoundingBox()
        pads.append((pad.GetNetname(), fp.GetReference(), str(pad.GetNumber()),
                     (r.GetLeft() + r.GetRight()) / 2 / MM, (r.GetTop() + r.GetBottom()) / 2 / MM,
                     (r.GetRight() - r.GetLeft()) / MM, (r.GetBottom() - r.GetTop()) / MM))

for n in NETS:
    ps = [p for p in pads if p[0] == n]
    if not ps:
        continue
    print("=== %s : %d pads ===" % (n, len(ps)))
    for (nn, ref, num, cx, cy, w, h) in ps:
        # 最近的其他网焊盘
        best = (1e9, None)
        for p2 in pads:
            if p2[0] == nn:
                continue
            dx = max(abs(p2[3] - cx) - (p2[5] / 2 + w / 2), 0.0)
            dy = max(abs(p2[4] - cy) - (p2[6] / 2 + h / 2), 0.0)
            d = math.hypot(dx, dy)
            if d < best[0]:
                best = (d, p2)
        print("   %-12s.%-4s (%8.3f,%8.3f) pad %.2fx%.2f  最近异网焊盘 %.3f (%s.%s @%.2f,%.2f)"
              % (ref, num, cx, cy, w, h, best[0],
                 best[1][1] if best[1] else "?", best[1][2] if best[1] else "?",
                 best[1][3] if best[1] else -1, best[1][4] if best[1] else -1))
