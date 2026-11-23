#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 · 186 件全量交叉分类 (自算, 不照抄任何人的口径)"""
import importlib.util
import json
import os
import collections

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
gap = set(ls.coverage_gap(bom, c4))
inter = c4 & iss
target90 = set(inter) | gap

bom_by_ref = collections.defaultdict(list)
for r in bom:
    ref = (r.get("ref") or "").strip()
    if ref:
        bom_by_ref[ref].append(r)

board_refs = set(board)
print("=== 交叉表: 186 = f(inC4, inISS356, inGap) ===")
tab = collections.Counter()
for ref in sorted(board_refs):
    tab[(ref in c4, ref in iss, ref in gap)] += 1
for k in sorted(tab, key=lambda x: (-tab[x], x)):
    print("  inC4=%-5s inISS=%-5s inGap=%-5s : %d" % (k[0], k[1], k[2], tab[k]))
print("  total =", sum(tab.values()))

print()
print("=== BOM 属性分布 (板面 186 件) ===")
attr = collections.Counter()
for ref in sorted(board_refs):
    rows = bom_by_ref.get(ref, [])
    if not rows:
        attr["BOM无此件"] += 1
        continue
    r = rows[0]
    attr[(r.get("type") or "").strip(), (r.get("dnp") or "").strip(),
         (r.get("footprint") or "").strip()] += 1
for k, v in sorted(attr.items(), key=lambda x: -x[1]):
    print("  %-40s : %d" % (str(k), v))

print()
print("=== 96 件 (board - 90) 逐件属性 ===")
rest96 = sorted(board_refs - target90)
for ref in rest96:
    rows = bom_by_ref.get(ref, [])
    r = rows[0] if rows else {}
    print("  %-16s inC4=%-5s type=%-8s dnp=%-6s fp=%-10s board=%s"
          % (ref, ref in c4, (r.get("type") or "").strip(),
             (r.get("dnp") or "").strip(), (r.get("footprint") or "").strip(),
             (r.get("board") or "").strip()))

print()
print("=== 找 '靶内 22 / 缺口 1' 的出处 ===")
print("  ISS-356 充电板靶子数 =", len(chg_t))
print("  board refs ∩ chg_t   =", len(board_refs & set(chg_t)), sorted(board_refs & set(chg_t)))
print("  gap ∩ (board-90)     =", len(gap - target90))
print("  iss ∩ (board-90)     =", len(iss - target90), sorted(iss - target90))
print("  board refs ∩ iss    =", len(board_refs & iss))
print("  board refs ∩ gap    =", len(board_refs & gap))
print("  rest96 ∩ c4         =", len(set(rest96) & c4))
print("  rest96 - c4         =", len(set(rest96) - c4))
print("  (board-90) - c4     =", len((board_refs - target90) - c4),
      sorted((board_refs - target90) - c4))
