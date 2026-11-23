#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 · 96 件按几何组找库候选 (★打分排序·打印 top N·只读★)
容差 (写在脚本里):
  PAD_TOL  = 0.05 mm
  CEN_TOL  = 0.10 mm
  FAB_TOL  = 0.20 mm
"""
import json
import os
from collections import defaultdict

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
INV = json.load(open(os.path.join(ROOT, "tmp/iss369/board_inventory.json"),
                     encoding="utf-8"))["footprints"]
LIB = json.load(open(os.path.join(ROOT, "tmp/iss369/lib_index.json"),
                     encoding="utf-8"))["mods"]
BUCK = json.load(open(os.path.join(ROOT, "tmp/iss369/buckets.json"), encoding="utf-8"))
RC = {r["ref"]: r for r in json.load(
    open(os.path.join(ROOT, "tmp/iss369/iss364_recheck.json"), encoding="utf-8"))}
t90 = set(BUCK["target90_list"])

PAD_TOL = 0.05
CEN_TOL = 0.10
FAB_TOL = 0.20

inv = {f["ref"]: f for f in INV}
groups = defaultdict(list)
for f in INV:
    if f["ref"] in t90:
        continue
    key = (f["pad_count"], tuple(f["pad_sizes"]),
           tuple(f["bbox"]) if f["bbox"] else None, f["centre_dist"])
    groups[key].append(f["ref"])

# 反查: 90 内每组的官方目标 (作为同组的"官方口径参照")
grp90 = {}
for ref, r in RC.items():
    f = inv[ref]
    key = (f["pad_count"], tuple(f["pad_sizes"]),
           tuple(f["bbox"]) if f["bbox"] else None, f["centre_dist"])
    grp90.setdefault(key, []).append((ref, r["target"]))

print("=== 96 件按组找候选 (pad 数相同 + 尺寸/中心距/fab 在容差内) ===")
for key, refs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    f = inv[refs[0]]
    ps = set((round(p["w"], 3), round(p["h"], 3)) for p in f["pads"])
    want_n = key[0]
    cw = key[3]
    bw, bh = (key[2] if key[2] else (None, None))
    cands = []
    for mk, m in LIB.items():
        if m["pads_n"] != want_n:
            continue
        ls = set((round(float(a), 3), round(float(b), 3))
                 for a, b in (s.split("x") for s in m["pad_sizes"]))
        if len(ls) != len(ps):
            continue
        pdiff = max(max(abs(a[0] - b[0]), abs(a[1] - b[1]))
                    for a in ls for b in ps)
        if pdiff > PAD_TOL:
            continue
        cdiff = abs(m["center"] - cw)
        if cdiff > CEN_TOL:
            continue
        if bw is not None and m["fab_w"] > 0 and abs(m["fab_w"] - bw) > FAB_TOL:
            continue
        if bh is not None and m["fab_h"] > 0 and abs(m["fab_h"] - bh) > FAB_TOL:
            continue
        cands.append(mk)
    print()
    print("### 组: pad=%d sizes=%s fab=%s cdist=%s  → %d 件 (96 内)"
          % (want_n, sorted(ps), key[2], cw, len(refs)))
    print("    件:", refs[:14], "..." if len(refs) > 14 else "")
    print("    90 内同几何组的官方目标:", sorted(set(t for _, t in grp90.get(key, []))))
    print("    ★候选 (%d):" % len(cands), cands[:25])
