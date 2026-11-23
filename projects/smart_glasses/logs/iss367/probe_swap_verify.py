#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_swap_verify.py —— ★★【ISS-367】自写 25 件换 land 的【解析式重算】 vs
ISS-365 用 pcbnew 做的沙盒板 —— 逐件逐焊盘对账 ★★

★★★**为什么必须对账** ★★★
  ISS-365 的 AFTER 数 (2183 / 2.225..3.250 / 73.215..74.385 / sweep) 是
  ★**用 pcbnew 在沙盒里真换 25 件 land** 算出来的 ★ ⇒ ★**那条数没有一条
  「不依赖 pcbnew」的复跑路径** ★ ⇒ ★**本单要自己把那条数算出来, 就必须证明
  「解析式换 land」与「pcbnew 换 land」在【焊盘几何】上逐件逐焊盘一致** ★
  ⇒ ★**一致 ⇒ 本单的数 = ISS-365 的数 = main 复核过的数 (同一件事)** ★
  ⇒ ★**不一致 ⇒ 本单必须改口径并在交卷页写明** ★

用法:
    python3 logs/iss367/probe_swap_verify.py
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
SBX = os.path.join(PROJ, "tmp", "iss365_sbx")
LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"

SWAP_LOG = os.path.join(PROJ, "logs", "iss365", "sbx_swap_log.json")


# ==================================================================================================
# 板文件: 一次扫描 ⇒ 记每个 footprint 的行区间 (★不做 O(n^2) 的 join★)
# ==================================================================================================
def footprint_spans(path):
    lines = open(path, "r", encoding="utf-8").read().split("\n")
    spans = []
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("(footprint"):
            depth, j = 0, i
            while j < len(lines):
                depth += lines[j].count("(") - lines[j].count(")")
                if depth == 0 and j > i:
                    break
                j += 1
            blk = "\n".join(lines[i:j + 1])
            m = re.search(r'\(property "Reference" "([^"]+)"', blk)
            spans.append((m.group(1) if m else "", i, j))
            i = j + 1
        else:
            i += 1
    return lines, spans


PAD_RE = re.compile(
    r'\(pad\s+"([^"]*)"\s+(\S+)\s+(\S+)\s+\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)'
    r'(?:\s*\(size ([-\d.]+) ([-\d.]+)\))?')


def fp_local_pads(lines, i, j):
    """★取一个 footprint 的【局部】焊盘 (x, y, size_x, size_y, pad_rot)★"""
    blk = "\n".join(lines[i:j + 1])
    out = []
    for m in PAD_RE.finditer(blk):
        num, ptype, shape, px, py, prot, sx, sy = m.groups()
        try:
            sx = float(sx) if sx else 0.0
            sy = float(sy) if sy else 0.0
        except (TypeError, ValueError):
            sx = sy = 0.0
        out.append({"num": num, "px": float(px), "py": float(py),
                    "sx": sx, "sy": sy,
                    "prot": float(prot) if prot else 0.0})
    return out


def fp_at(lines, i, j):
    blk = "\n".join(lines[i:j + 1])
    at = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', blk)
    if not at:
        return (0.0, 0.0, 0.0)
    return (float(at.group(1)), float(at.group(2)),
            float(at.group(3)) if at.group(3) else 0.0)


def mod_pads(path):
    text = open(path, "r", encoding="utf-8").read()
    out = []
    for m in PAD_RE.finditer(text):
        num, ptype, shape, px, py, prot, sx, sy = m.groups()
        try:
            sx = float(sx) if sx else 0.0
            sy = float(sy) if sy else 0.0
        except (TypeError, ValueError):
            sx = sy = 0.0
        out.append({"num": num, "px": float(px), "py": float(py),
                    "sx": sx, "sy": sy, "prot": float(prot) if prot else 0.0})
    return out


def main():
    log = json.load(open(SWAP_LOG, encoding="utf-8"))["log"]
    orig_p = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
    sbx_p = os.path.join(SBX, "HW", "PCB", "demo_mainboard.kicad_pcb")
    olines, ospans = footprint_spans(orig_p)
    slines, sspans = footprint_spans(sbx_p)
    omap = {r: (i, j) for r, i, j in ospans}
    smap = {r: (i, j) for r, i, j in sspans}

    bad = 0
    for rec in log:
        ref = rec["ref"]
        target = rec["target"]
        lib, name = target.split(":", 1)
        mp = os.path.join(LIBROOT, "%s.pretty" % lib, "%s.kicad_mod" % name)
        if not os.path.exists(mp):
            print("!! %s 目标库件找不到: %s" % (ref, mp))
            bad += 1
            continue
        want = mod_pads(mp)
        got = fp_local_pads(slines, *smap[ref])
        _, _, rot = fp_at(slines, *smap[ref])
        oo = fp_at(olines, *omap[ref])
        ok = (len(want) == len(got))
        detail = []
        if ok:
            for w, g in zip(sorted(want, key=lambda z: z["num"]),
                            sorted(got, key=lambda z: z["num"])):
                same = (abs(w["px"] - g["px"]) < 1e-6 and abs(w["py"] - g["py"]) < 1e-6
                        and abs(w["sx"] - g["sx"]) < 1e-6 and abs(w["sy"] - g["sy"]) < 1e-6)
                if not same:
                    ok = False
                    detail.append("pad%s mod(%.4f,%.4f,%.4f,%.4f) sbx(%.4f,%.4f,%.4f,%.4f)"
                                  % (w["num"], w["px"], w["py"], w["sx"], w["sy"],
                                     g["px"], g["py"], g["sx"], g["sy"]))
        print("%s %-16s rot(orig %.1f / sbx %.1f) npad %d/%d %s"
              % ("OK " if ok else "BAD", ref, oo[2], rot, len(want), len(got),
                 "" if ok else "⇒ " + " | ".join(detail)))
        if not ok:
            bad += 1
    print("\n★对账结论: %d / %d 件一致 · 不一致 %d 件" % (len(log) - bad, len(log), bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
