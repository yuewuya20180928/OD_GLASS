#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 · 96 件的库等价性穷搜 (只读)
★三种匹配口径★:
  M-A 严格等价: pad 数同 + 焊盘尺寸多重集同 + 中心距同 (⇒ 写库名不动 land, 零走线风险)
  M-B pad 数同 + 中心距同 (尺寸差 ⇒ 需换 land)
  M-C pad 数同 (其余都差 ⇒ 需换 land)
另: 查 BOM footprint 栏点名的那几个封装在库里有没有官方等效件
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
inv = {f["ref"]: f for f in INV}
rest96 = BUCK["rest96_list"]

groups = defaultdict(list)
for ref in rest96:
    f = inv[ref]
    key = (f["pad_count"], tuple(f["pad_sizes"]), f["centre_dist"])
    groups[key].append(ref)

res = {}
for key, refs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    n, sizes, cen = key
    A, B, C = [], [], []
    for mk, m in LIB.items():
        if m["pads_n"] != n:
            continue
        C.append(mk)
        if abs(m["center"] - cen) <= 1e-6:
            B.append(mk)
            if tuple(sorted(m["pad_sizes"])) == tuple(sorted(sizes)):
                A.append(mk)
    res[refs[0]] = {"pad_n": n, "sizes": list(sizes), "center": cen,
                    "n_refs": len(refs), "A": A, "B": B, "C_n": len(C),
                    "C_sample": sorted(C)[:12]}
    print("### pad=%d sizes=%s cdist=%s  (%d 件: %s)"
          % (n, list(sizes), cen, len(refs), refs[:6]))
    print("    M-A 严格等价 (尺寸+中心距全同) : %d %s" % (len(A), A[:10]))
    print("    M-B pad数+中心距同 (尺寸不同)   : %d %s" % (len(B), B[:10]))
    print("    M-C 仅 pad 数同                : %d %s" % (len(C), sorted(C)[:10]))
    print()

# BOM footprint 栏点名封装 → 库里查官方等效件
print("=" * 70)
print("=== BOM footprint 栏点名的封装, 在本机库里有没有官方等效件 ===")
for pref in ("DF40C", "FH12", "USB4105", "TMP117", "X2SON", "VQFN-16", "RGT",
             "UQFN-4", "RAA", "SON-8", "Q3", "BQ2970", "432243", "SOT-23"):
    hits = [k for k in LIB if pref.lower() in k.lower()]
    print("  %-12s : %d  %s" % (pref, len(hits), hits[:6]))
json.dump(res, open(os.path.join(ROOT, "tmp/iss369/equiv96.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("-> tmp/iss369/equiv96.json")
