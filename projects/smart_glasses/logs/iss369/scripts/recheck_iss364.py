#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 · ISS-364 §1 的 90 件目标清单【独立复核】(★不许照抄★)
读 HW/PCB/FP_TRUTH_LAND_SWAP_WORKPACKET.md 的 §1 表 ⇒ 逐件:
  ① 抽 ref / 目标 lib:name / .kicad_mod 路径 + md5
  ② 用**自己建的 lib_index.json** 查该 .kicad_mod 是否真在盘 + md5 对不对 + 几何
  ③ 用**自己读的板面** 抽该 ref 的现占位几何
  ④ 算几何 Δ
输出 tmp/iss369/iss364_recheck.json
"""
import json
import os
import re

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
DOC = os.path.join(ROOT, "HW", "PCB", "FP_TRUTH_LAND_SWAP_WORKPACKET.md")
INV = json.load(open(os.path.join(ROOT, "tmp", "iss369", "board_inventory.json"),
                     encoding="utf-8"))
LIB = json.load(open(os.path.join(ROOT, "tmp", "iss369", "lib_index.json"),
                     encoding="utf-8"))["mods"]
BUCK = json.load(open(os.path.join(ROOT, "tmp", "iss369", "buckets.json"),
                      encoding="utf-8"))
t90 = set(BUCK["target90_list"])
inv_by_ref = {f["ref"]: f for f in INV["footprints"]}

txt = open(DOC, encoding="utf-8").read()
lines = txt.splitlines()
# 找 §1 表
start = None
for i, ln in enumerate(lines):
    if re.match(r"^##\s*§1\s*逐件", ln):
        start = i
        break
assert start is not None
hdr = None
rows = []
for ln in lines[start:start + 400]:
    s = ln.strip()
    if s.startswith("|") and s.endswith("|"):
        cells = [c.strip() for c in s.strip("|").split("|")]
        if hdr is None:
            hdr = cells
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        if cells[0] in ("ref",):
            continue
        rows.append(cells)
    elif rows and not s.startswith("|"):
        break

print("§1 表头 %d 列: %s" % (len(hdr), hdr))
print("§1 数据行 %d" % len(rows))
COL = {h: i for i, h in enumerate(hdr)}


def col_of(name):
    """按子串找列号 (表头里有反引号, 直接等值匹配会落空)"""
    for h, i in COL.items():
        if name in h:
            return i
    raise KeyError(name)

out = []
for cells in rows:
    ref = cells[COL["ref"]].strip("`").strip()
    if not ref:
        continue
    tgt = cells[col_of("目标")].strip("`").strip()
    pathmd5 = cells[col_of("实存路径")].strip()
    pm = re.search(r"`([^`]+)`\s*md5\s*`([0-9a-f]{32})`", pathmd5)
    stated_path = pm.group(1) if pm else ""
    stated_md5 = pm.group(2) if pm else ""
    rec = {"ref": ref, "target": tgt, "stated_path": stated_path,
           "stated_md5": stated_md5}
    # ★独立复核: 我自己查
    key = tgt
    lm = LIB.get(key)
    rec["in_lib_index"] = lm is not None
    if lm:
        rec["actual_path"] = lm["path"]
        rec["actual_md5"] = lm["md5"]
        rec["md5_match"] = (lm["md5"] == stated_md5)
        rec["path_match"] = (lm["path"] == stated_path)
        rec["lib_pads_n"] = lm["pads_n"]
        rec["lib_fab"] = [lm["fab_w"], lm["fab_h"]]
        rec["lib_center"] = lm["center"]
    else:
        rec["actual_path"] = None
        rec["md5_match"] = False
        rec["path_match"] = False
    f = inv_by_ref.get(ref)
    rec["on_board"] = f is not None
    if f:
        rec["board_pads_n"] = f["pad_count"]
        rec["board_fab"] = f["bbox"]
        rec["board_center"] = f["centre_dist"]
        rec["board_sizes"] = f["pad_sizes"]
    rec["in_target90"] = ref in t90
    out.append(rec)

print()
print("复核 %d 件:" % len(out))
print("  在 §1 表里但不在 target90 名单:", [r["ref"] for r in out if not r["in_target90"]][:10])
print("  target90 名单里但不在 §1 表:", sorted(t90 - {r["ref"] for r in out})[:10])
print("  .kicad_mod 不在盘:", [r["ref"] for r in out if not r["in_lib_index"]])
print("  md5 对不上:", [r["ref"] for r in out if r["in_lib_index"] and not r["md5_match"]])
print("  路径对不上:", [r["ref"] for r in out if r["in_lib_index"] and not r["path_match"]])
print("  pad 数不一致 (板 vs 库):",
      [(r["ref"], r.get("board_pads_n"), r.get("lib_pads_n")) for r in out
       if r["in_lib_index"] and r.get("board_pads_n") != r.get("lib_pads_n")])
print()
print("  目标 lib:name 分布 (复核用):")
from collections import Counter
for k, v in sorted(Counter(r["target"] for r in out).items(), key=lambda x: -x[1]):
    print("    %-45s %d" % (k, v))
json.dump(out, open(os.path.join(ROOT, "tmp", "iss369", "iss364_recheck.json"), "w",
                    encoding="utf-8"), ensure_ascii=False, indent=1)
print("-> tmp/iss369/iss364_recheck.json")
