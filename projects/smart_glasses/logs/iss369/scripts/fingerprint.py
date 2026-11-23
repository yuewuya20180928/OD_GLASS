#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 · 板面 186 件几何指纹分组 (自算, ★用于判「自绘占位」还是「已落 land」★)
指纹 = (pad 数, 焊盘尺寸集合, fab 外框, 中心距, fp_line 数, 有无 courtyard, 有无 silk, 层集合)
"""
import json
import os
from collections import Counter, defaultdict

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
INV = json.load(open(os.path.join(ROOT, "tmp/iss369/board_inventory.json"),
                     encoding="utf-8"))["footprints"]
BUCK = json.load(open(os.path.join(ROOT, "tmp/iss369/buckets.json"), encoding="utf-8"))
t90 = set(BUCK["target90_list"])
RC = json.load(open(os.path.join(ROOT, "tmp/iss369/iss364_recheck.json"), encoding="utf-8"))
t90map = {r["ref"]: r for r in RC}

groups = defaultdict(list)
for f in INV:
    fp = (f["bbox"][0] if f["bbox"] else None, f["bbox"][1] if f["bbox"] else None)
    key = (f["pad_count"], tuple(f["pad_sizes"]), fp, f["centre_dist"],
           f["fp_lines"], f["has_courtyard"],
           tuple(sorted(x for x in f["layers_used"] if "Silk" in x or "CrtYd" in x)),
           tuple(sorted(f["layers_used"])))
    groups[key].append(f["ref"])

print("=== 几何指纹分组 (共 %d 组) ===" % len(groups))
for key, refs in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
    in90 = [r for r in refs if r in t90]
    out96 = [r for r in refs if r not in t90]
    print()
    print("pad=%d sizes=%s fab=%s cdist=%s lines=%d crtyd=%s extra=%s layers=%s"
          % (key[0], key[1], key[2], key[3], key[4], key[5], key[6], key[7]))
    print("   共 %d 件 (90 内 %d / 96 内 %d)" % (len(refs), len(in90), len(out96)))
    print("   90内:", in90[:8])
    print("   96内:", out96[:12])

# 90 件的目标几何指纹 vs 板面指纹对照
print()
print("=== 90 件: 板面指纹 → 目标库指纹 对照 (★看换 land 的几何位移★) ===")
LIB = json.load(open(os.path.join(ROOT, "tmp/iss369/lib_index.json"),
                     encoding="utf-8"))["mods"]
inv = {f["ref"]: f for f in INV}
pairs = Counter()
for ref, r in sorted(t90map.items()):
    f = inv[ref]
    m = LIB.get(r["target"], {})
    bkey = (f["pad_count"], tuple(f["pad_sizes"]),
            tuple(f["bbox"]) if f["bbox"] else None, f["centre_dist"])
    lkey = (m.get("pads_n"), tuple(m.get("pad_sizes", [])),
            (m.get("fab_w"), m.get("fab_h")), m.get("center"))
    pairs[(bkey, lkey)] += 1
for (b, l), n in sorted(pairs.items(), key=lambda kv: -kv[1]):
    print("  n=%-3d 板 %s → 库 %s" % (n, b, l))
