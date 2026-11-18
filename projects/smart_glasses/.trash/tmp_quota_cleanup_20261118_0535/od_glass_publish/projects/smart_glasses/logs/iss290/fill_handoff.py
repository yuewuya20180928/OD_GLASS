#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-290 · 回填交卷单里的实跑原始输出 (占位符替换 · 只读 rc 留证)"""
import os
import subprocess

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
DOC = os.path.join(ROOT, "HANDOFF", "2026-11-17_mech-lead_ISS289_结构侧最后一道交叉核对.md")
RC = os.path.join(ROOT, "logs", "iss290", "rc")


def read(p):
    return open(p, encoding="utf-8").read().rstrip("\n")


txt = open(DOC, encoding="utf-8").read()

# ---- md5 跑后 ----
out = subprocess.run(["md5sum", "HW/PCB/demo_mainboard.kicad_pcb", "HW/PCB/demo_mainboard.kicad_pro",
                      "HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv"],
                     cwd=ROOT, capture_output=True, text=True).stdout.rstrip("\n")
mtime = subprocess.run(["stat", "-c", "★ 板 mtime: %y (size %s)", "HW/PCB/demo_mainboard.kicad_pcb"],
                       cwd=ROOT, capture_output=True, text=True).stdout.rstrip("\n")
md5_after = "```\n★ 跑后 (★本单收工时实测★)\n" + out + "\n" + mtime + "\n```"

txt = txt.replace("__MD5_AFTER__", md5_after)
txt = txt.replace("__GATE_MAIN__", read(os.path.join(RC, "gate_main.txt")))
txt = txt.replace("__GATE_SELFTEST__", read(os.path.join(RC, "gate_selftest.txt")))
txt = txt.replace("__ALL_RC__", read(os.path.join(RC, "all_rc.txt")))

assert "__MD5_AFTER__" not in txt and "__GATE_MAIN__" not in txt
assert "__GATE_SELFTEST__" not in txt and "__ALL_RC__" not in txt
open(DOC, "w", encoding="utf-8").write(txt)
print("filled:", DOC, os.path.getsize(DOC), "B")
