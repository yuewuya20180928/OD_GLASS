#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 · 「自绘占位」vs「已落 land」分类 + 已落 land 件的库等价件穷举 (只读)"""
import json
import os
import re
from collections import Counter, defaultdict

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
INV = json.load(open(os.path.join(ROOT, "tmp/iss369/board_inventory.json"),
                     encoding="utf-8"))["footprints"]
LIB = json.load(open(os.path.join(ROOT, "tmp/iss369/lib_index.json"),
                     encoding="utf-8"))["mods"]
BUCK = json.load(open(os.path.join(ROOT, "tmp/iss369/buckets.json"), encoding="utf-8"))
t90 = set(BUCK["target90_list"])
inv = {f["ref"]: f for f in INV}

print("=== J_SOM_P1 焊盘排布 (是 1 排还是 2 排?) ===")
f = inv["J_SOM_P1"]
xs = sorted({p["x"] for p in f["pads"]})
ys = sorted({p["y"] for p in f["pads"]})
print("  unique x =", len(xs), " unique y =", len(ys), ys[:6])
print("  first 8 (x,y):", [(p["x"], p["y"], p["num"]) for p in f["pads"][:8]])
print("  x 间距样本:", [round(xs[i + 1] - xs[i], 3) for i in range(min(6, len(xs) - 1))])

print()
print("=== 已落 land 的候选件 (有 courtyard 或 silk 或 非单一焊盘尺寸) ===")
def classify(f):
    sizes = {(round(p["w"], 3), round(p["h"], 3)) for p in f["pads"]}
    generic = (f["fp_lines"] == 4 and not f["has_courtyard"]
               and not any("Silk" in x for x in f["layers_used"])
               and len(sizes) == 1)
    return "自绘通用占位" if generic else "已落 land"


cat = Counter()
by_cat = defaultdict(list)
for f in INV:
    c = classify(f)
    cat[c] += 1
    by_cat[c].append(f["ref"])
print("  分类计数:", dict(cat))
print("  已落 land 的件:", by_cat["已落 land"])

print()
print("=== 「已落 land」件 → 库里几何最接近的候选 (打分) ===")


def score(f, m):
    """越小越像"""
    bs = {(round(p["w"], 3), round(p["h"], 3)) for p in f["pads"]}
    ls = {(round(float(a), 3), round(float(b), 3))
          for a, b in (s.split("x") for s in m["pad_sizes"])}
    if len(bs) != len(ls):
        return None
    pd = max(max(abs(a[0] - b[0]), abs(a[1] - b[1])) for a in ls for b in bs)
    cd = abs(m["center"] - f["centre_dist"])
    fd = (abs(m["fab_w"] - f["bbox"][0]) + abs(m["fab_h"] - f["bbox"][1])
          if f["bbox"] else 0.0)
    return pd + cd + fd, pd, cd, fd


for ref in by_cat["已落 land"]:
    f = inv[ref]
    scored = []
    for mk, m in LIB.items():
        if m["pads_n"] != f["pad_count"]:
            continue
        s = score(f, m)
        if s:
            scored.append((s[0], mk, s[1], s[2], s[3], m))
    scored.sort()
    print()
    print("### %s : pad=%d sizes=%s fab=%s cdist=%s"
          % (ref, f["pad_count"], sorted({(round(p["w"], 3), round(p["h"], 3))
                                          for p in f["pads"]}),
             f["bbox"], f["centre_dist"]))
    for tot, mk, pd, cd, fd, m in scored[:5]:
        print("    %-58s tot=%.3f padΔ=%.3f cenΔ=%.3f fabΔ=%.3f  libpad=%s fab=%sx%s"
              % (mk, tot, pd, cd, fd, m["pad_sizes"][:2], m["fab_w"], m["fab_h"]))
