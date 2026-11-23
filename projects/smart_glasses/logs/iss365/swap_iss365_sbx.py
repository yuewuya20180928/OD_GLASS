#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""swap_iss365_sbx.py —— ★★【ISS-365 · mech-lead】沙盒换 land (★只改沙盒板副本·真板一个字节不碰★)★★

★★**它干什么** ★★
  在 `tmp/iss365_sbx/HW/PCB/demo_mainboard.kicad_pcb` 这张【副本】上, 把 §1 收录的 25 件
  的自绘占位 land 换成 ISS-356 / 覆盖缺口页给的【官方 `.kicad_mod`】⇒
  ★**用来提前算「换封装之后 MECH 三道闸会怎么重判」** ★

★★**三条纪律 (★本脚本自己写死的·不许违反★)** ★★
  ① ★**只写沙盒板副本** ★ (★真板 `HW/PCB/demo_mainboard.kicad_pcb` 的 md5 全程不变·收工前复核★)
  ② ★**pad↔net 按【焊盘号】继承** ★ (★不替老板做 pad 序对调——那是板级决定 (B13/B10/B11)·
     ★**几何判据与 net 无关** ⇒ 不影响任何 MECH 结论★)
  ③ ★**不动落位** ★ (★位置/旋转一律沿用旧封装⇒ 这一跳只测「换 land」的影响, 不夹带「挪位」★)

用法 (★必须带 KiCad python★):
    bash state/pcbnew_py.sh logs/iss365/swap_iss365_sbx.py --sbx <沙盒根> --mode swap|control
"""
from __future__ import annotations

import argparse
import json
import os
import sys

LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"

# ★★§1 收录的 25 件 ⇒ 目标 `lib:name` (★取自 ISS-356 基准块 + 覆盖缺口 §2, 本单实算得出★) ★★
SWAPS = [
    # (ref, target lib:name)
    ("R_SEL_D0_N", "Resistor_SMD:R_0603_1608Metric"),
    ("R_SEL_D0_P", "Resistor_SMD:R_0603_1608Metric"),
    ("R_SEL_D1_N", "Resistor_SMD:R_0603_1608Metric"),
    ("R_SEL_D1_P", "Resistor_SMD:R_0603_1608Metric"),
    ("R_SEL_CK_N", "Resistor_SMD:R_0603_1608Metric"),
    ("R_SEL_CK_P", "Resistor_SMD:R_0603_1608Metric"),
    ("R_SEL_D2_N", "Resistor_SMD:R_0603_1608Metric"),
    ("R_SEL_D2_P", "Resistor_SMD:R_0603_1608Metric"),
    ("R_SEL_D3_N", "Resistor_SMD:R_0603_1608Metric"),
    ("R_SEL_D3_P", "Resistor_SMD:R_0603_1608Metric"),
    ("D_LED_G", "LED_SMD:LED_0805_2012Metric"),
    ("D_ESD_CAM", "Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm"),
    ("D_ESD_DEMO", "Diode_SMD:D_SOD-323"),
    ("D_ESD_USB_D", "Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm"),
    ("SW_BOOT", "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2"),
    ("SW_KEY_PWR", "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2"),
    ("SW_KEY_VM", "Button_Switch_SMD:SW_SPST_B3U-1000P"),
    ("SW_KEY_VP", "Button_Switch_SMD:SW_SPST_B3U-1000P"),
    ("SW_RST", "Button_Switch_SMD:SW_Push_1P1T_NO_CK_KMR2"),
    ("FB_DEMO", "Inductor_SMD:L_0805_2012Metric"),
    ("Q_AND", "Package_TO_SOT_SMD:SOT-23"),
    ("Q_ENVC", "Package_TO_SOT_SMD:SOT-23"),
    ("Q_PG", "Package_TO_SOT_SMD:SOT-23"),
    ("R_LED_G", "Resistor_SMD:R_0603_1608Metric"),
    ("R_PU_I2CB_SCL", "Resistor_SMD:R_0603_1608Metric"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sbx", required=True)
    ap.add_argument("--mode", choices=("swap", "control"), default="swap")
    args = ap.parse_args()
    import pcbnew

    pcb = os.path.join(args.sbx, "HW", "PCB", "demo_mainboard.kicad_pcb")
    board = pcbnew.LoadBoard(pcb)
    log = []
    if args.mode == "swap":
        # ---- 第一遍: 先把每一件的旧几何/网络全部读出来 (★不碰板结构★) ----
        #   ★为什么要两遍★: `board.Remove()` 会释放 C++ 对象 ⇒ 之后 SWIG 代理可能失效
        #   ⇒ ★读在前、改在后★ ⇒ 不依赖「改完还能读到旧对象」
        plan = []
        for ref, target in SWAPS:
            lib, name = target.split(":", 1)
            libdir = os.path.join(LIBROOT, "%s.pretty" % lib)
            old = board.FindFootprintByReference(ref)
            if old is None:
                log.append({"ref": ref, "status": "NOT_FOUND"})
                continue
            pos = old.GetPosition()
            orient = old.GetOrientationDegrees()
            value = old.GetValue()
            nets = {}
            for p in list(old.Pads()):
                nets.setdefault(p.GetNumber(), p.GetNetname())
            old_npads = old.GetPadCount()
            plan.append({"ref": ref, "target": target, "libdir": libdir, "name": name,
                         "pos": pos, "orient": orient, "value": value,
                         "nets": nets, "old_npads": old_npads})
        # ---- 第二遍: 换封装 (★位置/旋转不变·pad↔net 按焊盘号继承·不替老板做 pad 序对调★) ----
        for item in plan:
            ref = item["ref"]
            new = pcbnew.FootprintLoad(item["libdir"], item["name"])
            if new is None:
                log.append({"ref": ref, "status": "LOAD_FAIL", "target": item["target"]})
                continue
            new.SetReference(ref)
            new.SetValue(item["value"])
            new.SetPosition(item["pos"])
            new.SetOrientationDegrees(item["orient"])
            new.SetLayer(pcbnew.F_Cu)
            for p in list(new.Pads()):
                nn = item["nets"].get(p.GetNumber())
                if nn:
                    p.SetNetCode(board.GetNetcodeFromNetname(nn))
            old = board.FindFootprintByReference(ref)
            if old is not None:
                board.Remove(old)
            board.Add(new)
            log.append({"ref": ref, "status": "SWAPPED", "target": item["target"],
                        "pos_mm": [pcbnew.ToMM(item["pos"].x), pcbnew.ToMM(item["pos"].y)],
                        "rot_deg": item["orient"],
                        "old_pads": item["old_npads"],
                        "new_pads": new.GetPadCount()})
        board.BuildListOfNets()
    board.Save(pcb)
    print(json.dumps({"mode": args.mode, "pcb": pcb, "log": log},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
