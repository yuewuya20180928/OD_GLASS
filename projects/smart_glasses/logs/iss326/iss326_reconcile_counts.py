#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iss326_reconcile_counts.py —— 对账: main 的顶层 571 处 是什么口径?"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
MECH = os.path.join(PROJ, "MECH")

uni = json.load(open(os.path.join(HERE, "mech_ref_universe.json"), encoding="utf-8"))["universe"]
refs = sorted(uni.keys(), key=len, reverse=True)
pats = {r: re.compile(r"(?<![A-Za-z0-9_])" + re.escape(r) + r"(?![A-Za-z0-9_])") for r in refs}

SHAPE = re.compile(r"\b[A-Z]{1,5}_[A-Za-z0-9_]*[A-Za-z0-9]\b")

def files(sub=False):
    out = []
    for dirpath, dirnames, filenames in os.walk(MECH):
        dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
        if not sub and os.path.dirname(dirpath) != MECH and dirpath != MECH:
            continue
        for fn in sorted(filenames):
            if fn.endswith(".py") or fn.endswith(".md"):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)

def count(sub):
    res = {}
    tot_occ = tot_line = tot_shape = 0
    for p in files(sub):
        rel = os.path.relpath(p, PROJ)
        txt = open(p, encoding="utf-8", errors="replace").read()
        lines = txt.splitlines()
        occ = 0; ln_set = set()
        for i, line in enumerate(lines, 1):
            for r in refs:
                n = len(pats[r].findall(line))
                if n:
                    occ += n; ln_set.add(i)
        shape = sum(len(SHAPE.findall(l)) for l in lines)
        res[rel] = (occ, len(ln_set), shape)
        tot_occ += occ; tot_line += len(ln_set); tot_shape += shape
    return res, tot_occ, tot_line, tot_shape

for sub, label in ((False, "顶层 (MECH/*.md + MECH/*.py)"), (True, "递归 (MECH/**/*.md + MECH/**/*.py)")):
    res, a, b, c = count(sub)
    print("=" * 78)
    print("扫描面: %s   文件数=%d" % (label, len(res)))
    print("  口径A 精确真集命中【出现次数】   : %d" % a)
    print("  口径B 精确真集命中【命中行数】   : %d" % b)
    print("  口径C 形状像位号 token【次数】   : %d" % c)
    print("  --- TOP 8 (口径A) ---")
    for rel, (o, l, s) in sorted(res.items(), key=lambda kv: -kv[1][0])[:8]:
        if o:
            print("      A=%4d  B=%4d  C=%4d  %s" % (o, l, s, rel))
    print("  --- TOP 8 (口径B) ---")
    for rel, (o, l, s) in sorted(res.items(), key=lambda kv: -kv[1][1])[:8]:
        if l:
            print("      A=%4d  B=%4d  C=%4d  %s" % (o, l, s, rel))
    print("  --- TOP 8 (口径C) ---")
    for rel, (o, l, s) in sorted(res.items(), key=lambda kv: -kv[1][2])[:8]:
        if s:
            print("      A=%4d  B=%4d  C=%4d  %s" % (o, l, s, rel))
