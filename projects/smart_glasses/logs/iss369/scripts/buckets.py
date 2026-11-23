#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 · 四桶口径实算 (★借 HW/check_fp_truth_land_swap.py 的纯 python 口径函数·不改那个脚本★)"""
import importlib.util
import json
import os
import sys

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
spec = importlib.util.spec_from_file_location(
    "ls", os.path.join(ROOT, "HW", "check_fp_truth_land_swap.py"))
ls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ls)

bom = ls.load_bom(os.path.join(ROOT, "HW", "BOM_v1.csv"))
main_t, chg_t, total_t = ls.iss356_targets(bom)
ph = ls.netlist_placeholder(os.path.join(ROOT, "HW", "netlist_v1.csv"))
board = ls.read_board_refs(os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb"))
c4 = set(ph)
iss = set(total_t)
gap = ls.coverage_gap(bom, c4)
inter = c4 & iss
target90 = sorted(inter) + sorted(gap)

# BOM 里每件的类型/dnp/footprint/board
bom_by_ref = {}
for r in bom:
    ref = (r.get("ref") or "").strip()
    if ref:
        bom_by_ref.setdefault(ref, r)

board_refs = set(board)
print("board footprints      :", len(board_refs))
print("C4 placeholder set    :", len(c4))
print("ISS-356 targets total :", len(iss), " main", len(main_t), " chg", len(chg_t))
print("inter (靶内 = C4∩ISS) :", len(inter))
print("gap   (缺口)          :", len(gap))
print("target_90             :", len(target90))
print("C4 - ISS (C4 里不在靶子名单):", len(c4 - iss))
print("board refs not in C4  :", len(board_refs - c4))

rest96 = sorted(board_refs - set(target90))
print("rest (board - 90)     :", len(rest96))

# 给 rest96 分类
buckets = {"TP": [], "DNP": [], "靶内-非C4": [], "缺口-非C4": [], "其它": []}
for ref in rest96:
    r = bom_by_ref.get(ref, {})
    typ = (r.get("type") or "").strip()
    dnp = (r.get("dnp") or "").strip()
    fp = (r.get("footprint") or "").strip()
    if typ == "TP":
        buckets["TP"].append(ref)
    elif dnp != "必装":
        buckets["DNP"].append(ref)
    elif fp == "待定" and ref in iss:
        buckets["靶内-非C4"].append(ref)
    elif fp != "待定":
        buckets["缺口-非C4"].append(ref)
    else:
        buckets["其它"].append(ref)
for k, v in buckets.items():
    print("  bucket %-12s %d" % (k, len(v)))
print("  sum =", sum(len(v) for v in buckets.values()))
for k, v in buckets.items():
    if v:
        print("   ", k, v[:200])

# BOM 里有没有板面没有的 ref
print("BOM refs not on board :", len(set(bom_by_ref) - board_refs))
missing = sorted(set(bom_by_ref) - board_refs)
print("   sample:", missing[:20])

json.dump({
    "board": len(board_refs), "c4": len(c4), "iss_total": len(iss),
    "iss_main": len(main_t), "iss_chg": len(chg_t),
    "inter": len(inter), "gap": len(gap), "target90": len(target90),
    "rest96": len(rest96),
    "buckets": {k: v for k, v in buckets.items()},
    "bom_not_on_board": missing,
    "target90_list": target90,
    "rest96_list": rest96,
}, open(os.path.join(ROOT, "tmp", "iss369", "buckets.json"), "w", encoding="utf-8"),
    ensure_ascii=False, indent=1)
print("-> tmp/iss369/buckets.json")
