#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 · 沙盒逐字节差分 (只读)
★证明: 写 lib_id 只改 (footprint "...") 那一行, 其它一个字节都不动★
"""
import difflib
import hashlib
import json
import os
import re

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
SBX = os.path.join(ROOT, "tmp", "iss369", "sbx")
BOARD = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def cmp(a, b, label):
    ta = open(a, encoding="utf-8").read().splitlines()
    tb = open(b, encoding="utf-8").read().splitlines()
    d = list(difflib.unified_diff(ta, tb, "A", "B", lineterm="", n=0))
    added = [x for x in d if x.startswith("+") and not x.startswith("+++")]
    removed = [x for x in d if x.startswith("-") and not x.startswith("---")]
    only_libid = all(re.match(r'^[+-]\t\(footprint "', x) for x in added + removed) \
        if (added or removed) else True
    print("### %s" % label)
    print("   A md5=%s (%d 行)" % (md5(a), len(ta)))
    print("   B md5=%s (%d 行)" % (md5(b), len(tb)))
    print("   差分: +%d 行 / -%d 行 · ★全部是 (footprint \"...\") 节点名行: %s"
          % (len(added), len(removed), only_libid))
    print("   前 6 条差分:")
    for x in d[:12]:
        print("     %s" % x)
    # 逐个 ref 的库名对照
    return {"a_md5": md5(a), "b_md5": md5(b), "added": len(added),
            "removed": len(removed), "only_footprint_node_lines": only_libid}


res = {}
res["S0_vs_S3_只写库名"] = cmp(BOARD, os.path.join(SBX, "board_libid_only.kicad_pcb"),
                               "S0 真板  vs  S3 只写库名 (零几何改动)")
res["S1_vs_S2_换land加库名"] = cmp(os.path.join(SBX, "board_legA_only.kicad_pcb"),
                                  os.path.join(SBX, "board_legA_plus_libid.kicad_pcb"),
                                  "S1 换land  vs  S2 换land+写库名")
res["S0_vs_S4_反向对照"] = cmp(BOARD, os.path.join(SBX, "board_libid_no_landswap.kicad_pcb"),
                               "S0 真板  vs  S4 90件写库名不换land")

# 板面 ref→lib_id 对照 (纯文本)
def libids(path):
    t = open(path, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'^\t\(footprint "([^"]*)"', t, re.M):
        s = m.start()
        cands = [t.find("\n\t(footprint ", s + 1), t.find("\n\t(net ", s + 1)]
        cands = [c for c in cands if c != -1]
        e = min(cands) if cands else len(t)
        blk = t[s:e]
        rm = re.search(r'\(property "Reference" "([^"]*)"', blk)
        if rm:
            out[rm.group(1)] = m.group(1)
    return out


s3 = libids(os.path.join(SBX, "board_libid_only.kicad_pcb"))
named = {k: v for k, v in s3.items() if v}
print()
print("### S3 板面库名非空: %d / %d" % (len(named), len(s3)))
from collections import Counter
print("   目标分布:", dict(Counter(v.split(":")[0] for v in named.values())))
json.dump(res, open(os.path.join(ROOT, "logs", "iss369", "12_sandbox_bytediff.json"),
                    "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("-> logs/iss369/12_sandbox_bytediff.json")
