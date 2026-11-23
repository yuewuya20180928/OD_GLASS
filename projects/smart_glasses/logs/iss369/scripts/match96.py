#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 · 为 96 件找库候选 (几何匹配, 只读)
容差 (★写在脚本里·不拍脑袋★):
  PAD_TOL_MM   = 0.05   # 焊盘尺寸
  CENTER_TOL_MM= 0.10   # 焊盘中心距
  FAB_TOL_MM   = 0.20   # fab 外框
"""
import json
import os
import re
from collections import Counter

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
INV = json.load(open(os.path.join(ROOT, "tmp/iss369/board_inventory.json"),
                     encoding="utf-8"))["footprints"]
LIB = json.load(open(os.path.join(ROOT, "tmp/iss369/lib_index.json"),
                     encoding="utf-8"))["mods"]
BUCK = json.load(open(os.path.join(ROOT, "tmp/iss369/buckets.json"), encoding="utf-8"))
RC = json.load(open(os.path.join(ROOT, "tmp/iss369/iss364_recheck.json"), encoding="utf-8"))
t90 = {r["ref"]: r for r in RC}

PAD_TOL = 0.05
CEN_TOL = 0.10
FAB_TOL = 0.20


def sizes_of(f):
    """板面焊盘尺寸集合 (用第一片代表, 单尺寸件取它)"""
    out = set()
    for p in f["pads"]:
        out.add((round(p["w"], 3), round(p["h"], 3)))
    return out


def match(f):
    """找板面该封装的库候选: pad 数相同 + 尺寸/中心距/fab 在容差内"""
    ps = sizes_of(f)
    want_n = f["pad_count"]
    cw = f["centre_dist"]
    bw = f["bbox"][0] if f["bbox"] else None
    bh = f["bbox"][1] if f["bbox"] else None
    cands = []
    for key, m in LIB.items():
        if m["pads_n"] != want_n:
            continue
        ls = set()
        for s in m["pad_sizes"]:
            a, b = s.split("x")
            ls.add((round(float(a), 3), round(float(b), 3)))
        # 尺寸: 集合基数必须相同 (都是同尺寸才可比)
        if len(ls) != len(ps):
            continue
        if not all(any(abs(a[0] - b[0]) <= PAD_TOL and abs(a[1] - b[1]) <= PAD_TOL
                       for b in ps) for a in ls):
            continue
        if abs(m["center"] - cw) > CEN_TOL:
            continue
        if bw is not None and m["fab_w"] > 0 and abs(m["fab_w"] - bw) > FAB_TOL:
            continue
        if bh is not None and m["fab_h"] > 0 and abs(m["fab_h"] - bh) > FAB_TOL:
            continue
        cands.append(key)
    return cands


rest96 = BUCK["rest96_list"]
inv = {f["ref"]: f for f in INV}
res = {}
for ref in rest96:
    f = inv[ref]
    c = match(f)
    res[ref] = {"pad_count": f["pad_count"], "sizes": sorted(sizes_of(f)),
                "bbox": f["bbox"], "center": f["centre_dist"],
                "has_courtyard": f["has_courtyard"],
                "cands": sorted(c), "n_cands": len(c)}

print("=== 96 件库候选 ===")
for ref in rest96:
    r = res[ref]
    libs = Counter(x.split(":")[0] for x in r["cands"])
    print("%-16s pads=%-4d cand=%-4d %s" % (ref, r["pad_count"], r["n_cands"],
                                            dict(sorted(libs.items(), key=lambda z: -z[1]))))
print()
print("候选数分布:", Counter(r["n_cands"] for r in res.values()))
print("零候选的件:", [k for k, v in res.items() if v["n_cands"] == 0])
json.dump(res, open(os.path.join(ROOT, "tmp/iss369/cand96.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("-> tmp/iss369/cand96.json")
