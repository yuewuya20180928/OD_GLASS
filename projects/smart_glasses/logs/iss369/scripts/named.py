#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 · 点名候选件几何逐条对照 (只读)
★要回答: 板面已落 land 的件, 与本机官方 .kicad_mod 是否几何等价 (⇒ 可写 lib_id 且零几何改动)★
"""
import json
import os
import re

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
INV = json.load(open(os.path.join(ROOT, "tmp/iss369/board_inventory.json"),
                     encoding="utf-8"))["footprints"]
LIB = json.load(open(os.path.join(ROOT, "tmp/iss369/lib_index.json"),
                     encoding="utf-8"))["mods"]
inv = {f["ref"]: f for f in INV}

# ★点名候选 (来自 BOM footprint 栏 / 型号 / 库族)
NAMED = {
    "J_SOM_P1": ["Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V_2x50_P0.4mm",
                 "Connector_Hirose_DF40:Hirose_DF40C-100DS-0.4V(51)_2x50_P0.4mm",
                 "Connector_Hirose_DF40:Hirose_DF40HC(3.0)-100DS-0.4V_2x50_P0.4mm"],
    "CONN_LIGHT": ["Connector_FFC-FPC:Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal"],
    "J_USB_C": ["Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal"],
    "U_TEMP": ["Package_DFN_QFN:WSON-6-1EP_2x2mm_P0.65mm_EP0.45x1.2mm",
               "Package_DFN_QFN:DFN-6-1EP_2x2mm_P0.65mm_EP0.45x1.2mm",
               "Package_DFN_QFN:WSON-6_2x2mm_P0.65mm",
               "Package_DFN_QFN:DFN-6_2x2mm_P0.65mm"],
    "Q1": ["Package_SON:HVSON-8-1EP_3x3mm_P0.65mm_EP1.6x2.4mm",
           "Package_DFN_QFN:DFN-8-1EP_3x3mm_P0.65mm_EP1.65x1.4mm",
           "Package_TO_SOT_SMD:SOT-23"],
    "U_LDO_IO18": ["Package_SON:Texas_X2SON-5_1x1mm_P0.65mm",
                   "Package_SON:Texas_X2SON-4_1x1mm_P0.65mm",
                   "Package_SON:Texas_X2SON-5_0.8x0.8mm_P0.48mm"],
    "U_DCDC_VCORE": ["Package_DFN_QFN:HVQFN-16-1EP_3x3mm_P0.5mm_EP1.5x1.5mm"],
    "U_EN_SW": ["Package_DFN_QFN:UQFN-4-1EP_1x1mm_P0.5mm_EP0.7x0.4mm"],
    "U_SUPV": ["Package_TO_SOT_SMD:SOT-23-5"],
    "U_BATPROT": ["Package_TO_SOT_SMD:SOT-23-6"],
    "J_DEBUG": ["Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Vertical",
                "Connector_PinHeader_1.27mm:PinHeader_1x04_P1.27mm_Horizontal"],
    "J_BOOT1": ["Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical"],
    "J_UART": ["Connector_PinHeader_1.27mm:PinHeader_1x02_P1.27mm_Vertical"],
    "CONN_CAM": ["Connector_FFC-FPC:Hirose_FH26-29S-0.3SHW_2Rows-29Pins-1MP_P0.60mm_Horizontal"],
    "X1": ["Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm"],
    "TP_PG": ["TestPoint:TestPoint_Pad_D1.0mm"],
    "BT_432243": ["Connector:BatteryHolder_Keystone_3000_1x6.8mm"],
    "SW_KEY_CAM": ["Button_Switch_SMD:SW_SPST_B3U-1000P"],
    "D_LED_B": ["LED_SMD:LED_0603_1608Metric"],
    "D_ESD_LIGHT": ["Diode_SMD:D_SOD-323"],
}

TOL_PAD = 0.05
TOL_CEN = 0.10
TOL_FAB = 0.30

for ref, cands in NAMED.items():
    f = inv.get(ref)
    if f is None:
        print("★ %s 不在板上" % ref)
        continue
    bs = {(round(p["w"], 3), round(p["h"], 3)) for p in f["pads"]}
    print("=" * 76)
    print("### %s : pad=%d sizes=%s fab=%s cdist=%s crtyd=%s"
          % (ref, f["pad_count"], sorted(bs), f["bbox"], f["centre_dist"],
             f["has_courtyard"]))
    for c in cands:
        m = LIB.get(c)
        if not m:
            print("    %-64s ★不在盘" % c)
            continue
        ls = {(round(float(a), 3), round(float(b), 3))
              for a, b in (s.split("x") for s in m["pad_sizes"])}
        pd = max([max(abs(a[0] - b[0]), abs(a[1] - b[1])) for a in ls for b in bs]
                 or [0])
        cd = abs(m["center"] - f["centre_dist"])
        fd = ((abs(m["fab_w"] - f["bbox"][0]) + abs(m["fab_h"] - f["bbox"][1]))
              if f["bbox"] else 0.0)
        ok = (m["pads_n"] == f["pad_count"] and len(ls) == len(bs)
              and pd <= TOL_PAD and cd <= TOL_CEN and fd <= TOL_FAB)
        print("    %-64s pads=%d/%d padΔ=%.3f cenΔ=%.3f fabΔ=%.3f  sizes=%s ⇒ %s"
              % (c, m["pads_n"], f["pad_count"], pd, cd, fd, m["pad_sizes"][:2],
                 "★几何等价 (可写库名·零几何改动)" if ok else "几何不等价"))
