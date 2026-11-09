#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_probe_pads.py -- ★只读探针: 打印指定网/区域的焊盘 + 预留框覆盖判定 (★不改板)"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("PCB_LAYERS", "8")
import pcbnew  # noqa: E402

MM = 1000000.0
b = pcbnew.LoadBoard("HW/PCB/demo_mainboard.kicad_pcb")
if b is None:
    print("★板读不出来")
    raise SystemExit(2)

BOXES = [
    ("CSI_D0_D0_N_SRC+CSI_D0_D0_P_SRC", 21.550, 50.960, 22.450, 52.360),
    ("CSI_D0_D1_N_SRC+CSI_D0_D1_P_SRC", 20.350, 49.560, 21.250, 50.960),
    ("CSI_D0_D3_N_SRC+CSI_D0_D3_P_SRC", 16.750, 49.560, 17.650, 50.960),
    ("DSI_D0_D2_N_SRC+DSI_D0_D2_P_SRC", 19.550, 7.960, 20.450, 9.360),
    ("DSI_D0_D3_N_SRC+DSI_D0_D3_P_SRC", 18.350, 7.960, 19.250, 9.360),
    ("JTAG_TDO", 143.250, 56.600, 144.150, 58.000),
    ("JTAG_TMS", 142.250, 56.600, 143.150, 58.000),
    ("UART_TX", 18.190, 67.200, 19.090, 68.600),
]


def box_of(x, y):
    hit = []
    for (nm, x0, y0, x1, y1) in BOXES:
        if x0 - 0.3 <= x <= x1 + 0.3 and y0 - 0.3 <= y <= y1 + 0.3:
            hit.append(nm)
    return hit


def ref_of(p):
    try:
        return p.GetParent().GetReference()
    except Exception:
        try:
            return p.GetParentFootprint().GetReference()
        except Exception:
            return "?"


WATCH = {"CSI_D0_D3_P", "CSI_D0_D3_N", "CSI_D0_D3_P_SRC", "CSI_D0_D3_N_SRC",
         "JTAG_TDO", "JTAG_TMS", "UART_TX", "CSI_MCLK"}
rows = []
for p in b.GetPads():
    pos = p.GetPosition()
    x, y = pos.x / MM, pos.y / MM
    net = p.GetNetname()
    ref = ref_of(p)
    if net in WATCH or (ref == "J_SOM" and 15.0 <= x <= 20.0) or ref.startswith("C_AC_CSI_D0_D3"):
        rows.append((ref, p.GetNumber(), net, x, y, box_of(x, y)))

rows.sort(key=lambda r: (r[3], r[4]))
print("★焊盘表 (★watch 网 + J_SOM x15..20 + C_AC_CSI_D0_D3*)")
for (ref, num, net, x, y, hit) in rows:
    tag = ("  ★被预留框覆盖: " + ",".join(hit)) if hit else ""
    print("  %-16s.%-4s %-18s (%8.3f,%8.3f)%s" % (ref, num, net, x, y, tag))
