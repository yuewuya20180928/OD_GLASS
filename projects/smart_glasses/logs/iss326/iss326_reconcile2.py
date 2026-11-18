#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iss326_reconcile2.py —— 口径矩阵: 找出 main 那个 571 / 174 / 129 / 120 / 116 / 74 是什么口径"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
MECH = os.path.join(PROJ, "MECH")

uni = json.load(open(os.path.join(HERE, "mech_ref_universe.json"), encoding="utf-8"))["universe"]
refs = sorted(uni.keys(), key=len, reverse=True)
pats = {r: re.compile(r"(?<![A-Za-z0-9_])" + re.escape(r) + r"(?![A-Za-z0-9_])") for r in refs}
SHAPE = re.compile(r"\b[A-Za-z]{1,5}_[A-Za-z0-9_]*\b")
PREFIXES = ("R_", "C_", "U_", "J_", "D_", "L_", "Q_", "TP_", "LED_", "FB_", "BT_", "CONN_", "CHG_", "SW_")
SHAPE2 = re.compile(r"\b(?:" + "|".join(PREFIXES) + r")[A-Za-z0-9_]*")


def walk(sub):
    out = []
    for dirpath, dirnames, filenames in os.walk(MECH):
        dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
        if not sub and dirpath != MECH:
            continue
        for fn in sorted(filenames):
            if fn.endswith(".py") or fn.endswith(".md"):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def metrics(path):
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    exact_occ = 0; exact_ln = set(); uniq_per_line = 0
    shape_occ = 0; shape_ln = set(); shape2_occ = 0; shape2_ln = set()
    for i, line in enumerate(lines, 1):
        c = 0
        for r in refs:
            n = len(pats[r].findall(line))
            if n:
                c += n
        if c:
            exact_occ += c; exact_ln.add(i)
            uniq_per_line += len({r for r in refs if pats[r].search(line)})
        s = len(SHAPE.findall(line))
        if s:
            shape_occ += s; shape_ln.add(i)
        s2 = len(SHAPE2.findall(line))
        if s2:
            shape2_occ += s2; shape2_ln.add(i)
    return {"A_occ": exact_occ, "B_ln": len(exact_ln), "C_uniqpl": uniq_per_line,
            "D_shape_occ": shape_occ, "E_shape_ln": len(shape_ln),
            "F_prefix_occ": shape2_occ, "G_prefix_ln": len(shape2_ln)}


KEYS = ["A_occ", "B_ln", "C_uniqpl", "D_shape_occ", "E_shape_ln", "F_prefix_occ", "G_prefix_ln"]

for sub, label in ((False, "顶层"), (True, "递归")):
    for extset, elabel in (((".py", ".md"), "md+py"), ((".md",), "md-only"), ((".py",), "py-only")):
        rows = []
        for p in walk(sub):
            if not p.endswith(extset):
                continue
            rel = os.path.relpath(p, PROJ)
            rows.append((rel, metrics(p)))
        print("=" * 90)
        print("扫描面 %s / %s   文件数=%d" % (label, elabel, len(rows)))
        for k in KEYS:
            tot = sum(m[k] for _, m in rows)
            top5 = [r for r, _ in sorted(rows, key=lambda kv: -kv[1][k])[:5]]
            tops = [dict((rel, m) for rel, m in rows)[t][k] for t in top5]
            print("  %-13s 合计=%6d   TOP5=%s  (%s)" % (k, tot, tops, " / ".join(os.path.basename(t) for t in top5)))
