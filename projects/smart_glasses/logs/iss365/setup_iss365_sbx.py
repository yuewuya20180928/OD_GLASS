#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""setup_iss365_sbx.py —— ★★【ISS-365 · mech-lead】建沙盒根 `tmp/iss365_sbx/`★★

★★**沙盒怎么造 (★照 main 实读过的源码口径·不踩坑★)** ★★
  ★`MECH/check_onepass_struct_crosscheck.py` **没有** `--root` ⇒ 它靠 `PROJ = HERE/..` ★
  ⇒ 沙盒根必须是【一个里面有 `MECH/` 的目录】⇒ 把 `MECH/` 整个目录 + 它要读的表复制进去 ★
  ⇒ 跑 `tmp/iss365_sbx/MECH/check_onepass_struct_crosscheck.py` ⇒ PROJ 自动指向沙盒根 ★

  ★`MECH/check_onepass_mech_sync.py` 有 `--root` ⇒ 两种都行, 本沙盒统一用「目录法」, 三道闸同口径 ★

★★**只复制要读的东西; `state/` 用符号链接 (只读用途) ⇒ 零拷贝 908 MB★ ★★
"""
from __future__ import annotations

import os
import shutil
import sys

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SBX = os.path.join(PROJ, "tmp", "iss365_sbx")

MECH_FILES = [
    "check_onepass_struct_crosscheck.py",
    "check_onepass_mech_sync.py",
    "check_board_frame_coords.py",
    "check_demo_struct_truth.py",
    "service_port_check.py",
    "hw_cross_review_check.py",
    "BOARD_ONEPASS_STRUCT_CROSSCHECK.md",
    "BOARD_ONEPASS_MECH_SYNC.md",
    "BOARD_GEOM_30MM.md",
    "BOARD_PORT_OPENING_S6_WORKPACKET.md",
    "BOARD_PORT_OPENING_S6_FRAME_CALIBER.md",
    "HW_CROSS_REVIEW_TRIAGE.md",
    "pinset2_mech_check.py",
    "board_port_opening_s6_check.py",
]

HW_FILES = [
    "BOM_v1.csv",
    "netlist_v1.csv",
    "netlist_v1_pins.csv",
    "SCHEMATIC_LANDING_V1_LANDED.md",
    "SCHEMATIC_V1.md",
    "FP_TRUTH_BASELINE.md",
]

HW_PCB_FILES = [
    "demo_mainboard.kicad_pcb",
    "demo_mainboard.kicad_pro",
    "demo_mainboard_params.json",
    "BOARD_FRAME_CALIBER.md",
    "FP_TRUTH_COVERAGE_GAP.md",
    "BOARD_ONEPASS_WORKPACKET.md",
]


def main():
    if os.path.isdir(SBX):
        shutil.rmtree(SBX)
    os.makedirs(os.path.join(SBX, "MECH"), exist_ok=True)
    os.makedirs(os.path.join(SBX, "HW", "PCB"), exist_ok=True)
    n = 0
    # ---- MECH/ 整个目录 (★闸脚本 + 它 import/读的全部件; 一个字节都不改, 只复制★) ----
    for name in sorted(os.listdir(os.path.join(PROJ, "MECH"))):
        src = os.path.join(PROJ, "MECH", name)
        if os.path.isdir(src):
            if name in ("__pycache__", "print", "tools"):
                continue
            shutil.copytree(src, os.path.join(SBX, "MECH", name))
            n += 1
            continue
        if name.endswith(".pyc"):
            continue
        shutil.copy2(src, os.path.join(SBX, "MECH", name))
        n += 1
    for f in HW_FILES:
        src = os.path.join(PROJ, "HW", f)
        if not os.path.exists(src):
            print("[sbx] 缺 HW 文件 (跳过): %s" % f)
            continue
        shutil.copy2(src, os.path.join(SBX, "HW", f))
        n += 1
    # ---- HW/PCB/ 全部 (★含板 + 校准页 + 作业包 + params★) ----
    for name in sorted(os.listdir(os.path.join(PROJ, "HW", "PCB"))):
        src = os.path.join(PROJ, "HW", "PCB", name)
        if os.path.isdir(src) or ".bak" in name:
            continue
        shutil.copy2(src, os.path.join(SBX, "HW", "PCB", name))
        n += 1
    # state/ 只读 ⇒ 符号链接
    st = os.path.join(SBX, "state")
    if not os.path.exists(st):
        os.symlink(os.path.join(PROJ, "state"), st)
    print("[sbx] 沙盒根: %s  (复制 %d 件 + state 符号链接)" % (SBX, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
