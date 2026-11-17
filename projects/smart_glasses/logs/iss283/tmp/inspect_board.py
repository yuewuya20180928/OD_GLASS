#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★ISS-283 · cont2 · 盘面勘察脚本 (★只读·零写板★)"""
import json
import os
import re

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

board = open(os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb"), encoding="utf-8").read()
lines = board.split("\n")


def footprints():
    i = 0
    while i < len(lines):
        if lines[i].startswith("\t(footprint "):
            blk, depth, j = [], 0, i
            while j < len(lines):
                blk.append(lines[j])
                depth += lines[j].count("(") - lines[j].count(")")
                if depth == 0 and j > i:
                    break
                j += 1
            yield i + 1, "\n".join(blk)
            i = j + 1
        else:
            i += 1


for ref in ("D_ESD_USB_D", "Q_PG"):
    print("=" * 62)
    print("板面 footprint:", ref)
    for ln0, blk in footprints():
        if '"Reference" "%s"' % ref in blk:
            print("  (行 %d)" % ln0)
            for ln in blk.split("\n"):
                s = ln.strip()
                if s.startswith("(pad "):
                    num = re.search(r'"(\d+)"', s)
                    net = re.search(r'\(net\s+"([^"]*)"\)', s)
                    print("    pad %s  net=%s" % (num.group(1) if num else "?",
                                                 net.group(1) if net else "(无 net ⇒ 继承默认)"))
            break

print("=" * 62)
print("板上仍挂旧网名 USB_D_P_SRC 的 footprint:")
for ln0, blk in footprints():
    m = re.search(r'\(property "Reference" "([^"]*)"', blk)
    ref = m.group(1) if m else "?"
    nets = re.findall(r'\(net\s+"([^"]*)"\)', blk)
    if "USB_D_P_SRC" in nets:
        print("    L%-6d %-16s nets=%s" % (ln0, ref, nets))

txt = open(os.path.join(PROJ, "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md"), encoding="utf-8").read()
m = re.search(r"```json\s*(\{.*?\})\s*```", txt, re.S)
obj = json.loads(m.group(1))
print("=" * 62)
print("清单 JSON: %d items" % len(obj["items"]))
for it in obj["items"]:
    print("   %-24s step=%-4s src=%-8s title=%s" % (it["id"], it.get("step"), it.get("source_iss"),
                                                    it.get("title", "")[:44]))
hits = [it["id"] for it in obj["items"]
        if "USB_D_P_SRC" in json.dumps(it, ensure_ascii=False)
        or "NET_USB_D_P_TYPEC" in json.dumps(it, ensure_ascii=False)]
print("含 V-2 网名的条目:", hits)

wp = os.path.join(PROJ, "HW/PCB/BOARD_ONEPASS_WORKPACKET.md")
w = open(wp, encoding="utf-8").read()
print("=" * 62)
print("作业包里提到 Q_PG 的行:")
for ln in w.split("\n"):
    if "Q_PG" in ln:
        print("   ", ln[:190])
