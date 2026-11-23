#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""xcheck_iss365.py —— ★★【ISS-365】把本单实算的 S6 净距 与 既有闸打印的表 逐条对账 ★★

★**为什么要有这一步**: ★**本单的数不是抄闸的, 也不是抄任何 agent 报告的** ⇒
  ⇒ 必须【本单自己算一遍】+【把既有闸自己的输出抓一遍】+【逐条对账】
  ⇒ 对不上就说明口径漂了, 那一行必须标红 ★
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))

ROW_RE = re.compile(r"^\s+(\S+)\s+(B160x100)\s+\(([\d.]+),\s*([\d.]+)\)\s+"
                     r"X\s+([\d.]+)\.\.([\d.]+)\s+\S+\s+Y\s+([\d.]+)\.\.([\d.]+)\s+"
                     r"\S+.*?([\d.]+)\s+([\d.]+)\s*$")


def parse_gate(path):
    out = {}
    txt = open(path, encoding="utf-8").read()
    for line in txt.splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        out[m.group(1)] = {
            "target": [float(m.group(3)), float(m.group(4))],
            "env": [float(m.group(5)), float(m.group(6)), float(m.group(7)), float(m.group(8))],
            "clr_gate": float(m.group(9)),
            "clr_mc": float(m.group(10)),
        }
    return out


def main():
    res = json.load(open(os.path.join(HERE, "compute_iss365.json"), encoding="utf-8"))
    mine = {r["ref"]: r for r in res["s6_rows"]}
    total_bad = 0
    report = []
    for tag, fn, k_gate, k_mc in (
            ("BEFORE", "sbx_before_check_onepass_struct_crosscheck.txt", "clr_gate", "clr_mc"),
            ("AFTER", "sbx_after_check_onepass_struct_crosscheck.txt",
             "clr_gate_after", "clr_mc_after")):
        p = os.path.join(HERE, fn)
        if not os.path.exists(p):
            print("[xcheck] 缺文件: %s" % p)
            continue
        g = parse_gate(p)
        bad = 0
        for ref in sorted(g):
            m = mine.get(ref)
            if m is None:
                print("  [%s] MISSING %s" % (tag, ref))
                bad += 1
                continue
            if abs(m[k_gate] - g[ref]["clr_gate"]) > 1e-6 or \
               abs(m[k_mc] - g[ref]["clr_mc"]) > 1e-6:
                bad += 1
                print("  [%s] MISMATCH %s: 闸=(%s, %s) 本单=(%s, %s)"
                      % (tag, ref, g[ref]["clr_gate"], g[ref]["clr_mc"], m[k_gate], m[k_mc]))
        total_bad += bad
        print("[xcheck] %s: 闸打印 %d 行 · 与本单实算不一致 %d 条" % (tag, len(g), bad))
        report.append({"phase": tag, "gate_rows": len(g), "mismatch": bad})
    json.dump({"report": report, "total_mismatch": total_bad},
              open(os.path.join(HERE, "xcheck_result.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return 0 if total_bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
