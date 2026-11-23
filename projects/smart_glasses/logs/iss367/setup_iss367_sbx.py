#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""setup_iss367_sbx.py —— ★★【ISS-367 · mech-lead】建沙盒根 `tmp/iss367_sbx/`★★

★★★**这个沙盒干什么用** ★★★
  ★**只写沙盒板副本** (★真板 `HW/PCB/demo_mainboard.kicad_pcb` 全程一个字节不碰·md5 收工前复核★)
  ⇒ ★**在副本上用 pcbnew 真把 S10 的 25 件 land 换成官方封装** ⇒
  ★**用 `MECH/check_board_frame_coords.py` 自己的 `led_space()` 在这张副本上重算** ⇒
  ★**得到一条【不依赖本单解析式】的独立复算路径** ★
  ⇒ ★**两条路径 (解析式 / pcbnew 副本) 的四组数必须逐字相同** ⇒ ★**同一个数** ★

★**沙盒落在项目盘 `tmp/iss367_sbx/` (★不写 /tmp★)** ★
"""
from __future__ import annotations

import os
import shutil
import sys

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SBX = os.path.join(PROJ, "tmp", "iss367_sbx")

# ★`MECH/` 整个目录复制过去 (★几个闸靠 `HERE/..` 定位项目根⇒ 沙盒根必须自带 `MECH/`★) ★
HW_FILES = [
    "BOM_v1.csv", "netlist_v1.csv", "netlist_v1_pins.csv",
    "SCHEMATIC_LANDING_V1_LANDED.md", "SCHEMATIC_V1.md", "FP_TRUTH_BASELINE.md",
]
HW_PCB_FILES = [
    "demo_mainboard.kicad_pcb", "demo_mainboard.kicad_pro",
    "demo_mainboard_params.json", "BOARD_FRAME_CALIBER.md",
    "FP_TRUTH_COVERAGE_GAP.md", "BOARD_ONEPASS_WORKPACKET.md",
]


def main():
    if os.path.isdir(SBX):
        shutil.rmtree(SBX)
    os.makedirs(os.path.join(SBX, "HW", "PCB"))
    shutil.copytree(os.path.join(PROJ, "MECH"), os.path.join(SBX, "MECH"))
    for rel in HW_FILES:
        src = os.path.join(PROJ, "HW", rel)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(SBX, "HW", rel))
    for rel in HW_PCB_FILES:
        src = os.path.join(PROJ, "HW", "PCB", rel)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(SBX, "HW", "PCB", rel))
    # ★`state/` 用符号链接 (只读用途) ⇒ 零拷贝 ★
    link = os.path.join(SBX, "state")
    if not os.path.exists(link):
        os.symlink(os.path.join(PROJ, "state"), link)
    print("[sbx] 已建: %s" % SBX)
    print("[sbx] 板副本 md5 = %s" % _md5(os.path.join(SBX, "HW", "PCB", "demo_mainboard.kicad_pcb")))
    print("[sbx] 真板   md5 = %s" % _md5(os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")))
    return 0


def _md5(path):
    import hashlib
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


if __name__ == "__main__":
    sys.exit(main())
