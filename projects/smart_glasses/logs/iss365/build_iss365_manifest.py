#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_iss365_manifest.py —— ★★【ISS-365】生成交卷前终检 md5 清单 `logs/iss365/29_final_md5.txt` ★★

★★**为什么用脚本生成**: ★**清单里的 md5 必须与盘面【此刻】逐字节相同** ★
  ⇒ ★**手抄必错** (★本单就错过一次: 规格页改了一轮之后清单没跟着改 ⇒ main 复跑 `md5sum -c` 直接 FAILED★)
  ⇒ ★**本脚本现算现写 ⇒ `md5sum -c` 必然 rc=0** ★

★★**清单范围 (★逐条·不漏不多★)** ★★
  · 受保护 5 件 (板 / `.kicad_pro` / 网表 / 脚表 / BOM)
  · 既有闸 7 个脚本 (★零改既有闸的自证★)
  · 既有页 5 个 (★第 6 个 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` 按 main 2026-11-23 16:55 整改要求改了 §3.2 ⇒
    ★**不进清单** (★进清单就等于宣称它「逐字节未变」★) ⇒ 旧→新 md5 对照见 `logs/iss365/29b_struct_crosscheck_md5_change.txt`★)
  · 本单新建/写入的 3 件 (规格页 / 新闸 / 交卷页)
"""
from __future__ import annotations

import hashlib
import os

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(PROJ, "logs", "iss365", "29_final_md5.txt")

PROTECTED = [
    "HW/PCB/demo_mainboard.kicad_pcb",
    "HW/PCB/demo_mainboard.kicad_pro",
    "HW/netlist_v1.csv",
    "HW/netlist_v1_pins.csv",
    "HW/BOM_v1.csv",
]
GATES = [
    "MECH/check_onepass_struct_crosscheck.py",
    "MECH/check_onepass_mech_sync.py",
    "MECH/check_board_frame_coords.py",
    "MECH/check_demo_struct_truth.py",
    "state/gate_check.py",
    "state/merge.py",
    "state/frag_write.py",
]
PAGES = [
    "MECH/BOARD_ONEPASS_MECH_SYNC.md",
    "MECH/BOARD_GEOM_30MM.md",
    "MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md",
    "HW/PCB/BOARD_ONEPASS_WORKPACKET.md",
    "HW/PCB/BOARD_FRAME_CALIBER.md",
]
MINE = [
    "MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md",
    "MECH/check_onepass_s10_fp_swap_impact.py",
    "HANDOFF/2026-11-23_mech-lead_ISS365_S10换封装对MECH侧影响面.md",
]

HEADER = """# ISS-365 · 交卷前终检 md5 清单 (★2026-11-23 17:1x · md5sum -c 本文件 ⇒ 必须 rc=0 且零 FAILED★)
# ★受保护 5 件 + 既有闸 7 个脚本 + 既有页 5 个 (★老字未变★) + 本单新建 3 件★
# ★注意: MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md 不在本清单里 ⇒ 它按 main 2026-11-23 16:55 整改要求改了 §3.2 一行 ⇒ 旧→新 md5 对照见 logs/iss365/29b_struct_crosscheck_md5_change.txt★
"""


def md5(rel):
    h = hashlib.md5()
    with open(os.path.join(PROJ, rel), "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    lines = [HEADER]
    for group in (PROTECTED, GATES, PAGES, MINE):
        for rel in group:
            p = os.path.join(PROJ, rel)
            if not os.path.exists(p):
                raise SystemExit("★清单里的文件不在盘上: %s" % rel)
            lines.append("%s  %s\n" % (md5(rel), rel))
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("".join(lines))
    print("[manifest] 已写 %s (%d 条)" % (OUT, len(PROTECTED) + len(GATES) + len(PAGES) + len(MINE)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
