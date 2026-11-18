#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sb04_scan_hardcoded_refs.py —— ISS-314 沙盒: 扫【按 ref 硬编码的下游代码点】

★只读项目源码 + 只读网表 ⇒ 零写项目文件 ★
★目的: 量化「板侧位号改名 ⇒ 哪些按精确 ref 查表/查板的代码点会失配」★
★规则 (ISS-205): 末字符是数字 ⇒ 不动; 否则加 `_1` ⇒ 落表侧 ref 变成 X_1
"""
import ast
import csv
import os
import re
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJ)

NET = os.path.join(PROJ, "HW", "netlist_v1.csv")
SRC_DIRS = [os.path.join(PROJ, "state"), os.path.join(PROJ, "HW")]

rows = list(csv.DictReader(open(NET, encoding="utf-8")))
refs = {(r.get("ref") or "").strip() for r in rows}
refs = {x for x in refs if x and not x.startswith(("RAIL_", "NET_"))}

# ★会被改名的 ref (末字符非数字)
renamed = sorted(x for x in refs if not x[-1].isdigit())
print("== 网表真实器件 ref = %d 个 · 其中末字符非数字 (⇒ 改名后 X→X_1) = %d 个 ==" % (len(refs), len(renamed)))

# ★扫源码里的字符串常量, 看哪些是网表里的 ref
hits = {}
for d in SRC_DIRS:
    if not os.path.isdir(d):
        continue
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".py"):
            continue
        p = os.path.join(d, fn)
        try:
            src = open(p, encoding="utf-8").read()
            tree = ast.parse(src)
        except Exception:
            continue
        lines = src.splitlines()
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                s = node.value.strip()
                if s in refs:
                    hits.setdefault(p, {}).setdefault(s, []).append(node.lineno)

print("\n== 源码里硬编码了网表 ref 的文件 (★改名的 ref 用 ★ 标出★) ==")
tot_all = 0
tot_renamed = 0
for p in sorted(hits):
    rl = sorted(hits[p])
    rr = [x for x in rl if x in renamed]
    tot_all += len(rl)
    tot_renamed += len(rr)
    print("\n--- %s ---" % os.path.relpath(p, PROJ))
    for x in rl:
        mark = "★" if x in renamed else " "
        print("   %s %-14s  (行 %s)" % (mark, x, ",".join(str(y) for y in hits[p][x][:8])))
print("\n== 合计: 硬编码 ref 出现点 %d 处 · 其中指向【会改名的 ref】的 %d 处 ==" % (tot_all, tot_renamed))

# ★专门列出被 check_pcb_nets.py / gen_bom.py / gen_pcb_netlist_board.py 硬编码的
print("\n== 关键三件里指向【会改名 ref】的硬编码点 (★改完名就失配=) ==")
for key in ("state/check_pcb_nets.py", "state/gen_bom.py", "state/gen_pcb_netlist_board.py",
            "state/gen_pcb_components.py"):
    p = os.path.join(PROJ, key)
    if not os.path.exists(p):
        continue
    h = hits.get(p, {})
    rr = sorted(x for x in h if x in renamed)
    if rr:
        print("\n--- %s ---" % key)
        for x in rr:
            print("   ★%-14s 行 %s" % (x, ",".join(str(y) for y in h[x][:10])))
    else:
        print("\n--- %s --- (无指向会改名 ref 的硬编码)" % key)
