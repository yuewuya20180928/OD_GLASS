#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""conn_esc_stats.py -- ★【逐网出脚失败统计】★

★为什么需要它 (★2026-11-11 00:4x 实测★):
  路由器实测只出 2377 段, 而官方 stage-1 是 17022 段 ⇒ 差一个数量级
  ⇒ 但【没人知道差在哪】⇒ ★**今天所有的臂都是"盲跑"**: 调参数 → 看 unc → 再调
  ⇒ ⇒ 本脚本把"失败"变成【有名有姓的网】+ 【有名有姓的原因】⇒ 才能从盲跑变成定位

★读三类数 (★缺一不可★):
  ① GND 下拉阶段的【失败原因字典】(★`conn_esc` / `free` / `inpad` / `astar` …★)
     ⇒ conn_esc = 【焊盘到过孔的环形铜没连上】⇒ ★**这是 20727 这个大头的来源★**
  ② 逐网线: `[组] 网名 ok=True/False 失败脚=N` ⇒ ★**哪些网布不出来, 差几个脚★**
  ③ 差分对: 单边布通的腿 ⇒ ★**死腿的苗头★**

用法:
  python3 state/conn_esc_stats.py /tmp/v76mv0_R.log [/tmp/v76mv1_R.log ...]
  python3 state/conn_esc_stats.py --cmp A.log B.log     # 逐网差分对比
"""

import ast
import json
import re
import sys
from collections import Counter, defaultdict


def parse_log(path):
    d = dict(reasons={}, nets={}, gnd=None, sum_line=None, groups=defaultdict(Counter))
    for line in open(path, encoding="utf-8", errors="ignore"):
        s = line.strip()
        # ① GND 下拉失败原因字典
        if "失败原因" in s and "conn_esc" in s:
            m = re.search(r"失败原因\s*(\{.*?\})\s*$", s)
            if m:
                try:
                    d["reasons"] = ast.literal_eval(m.group(1))
                except Exception:
                    pass
                m2 = re.search(r"下拉过孔\s*(\d+)\s*成功\s*/\s*(\d+)\s*失败", s)
                if m2:
                    d["gnd"] = (int(m2.group(1)), int(m2.group(2)))
        # ② 逐网线
        m = re.match(r"\[(\w+)\s*\]\s+(\S+)\s+ok=(True|False)\s+失败脚=(\d+)(.*)$", s)
        if m:
            g, net, ok, fails, tail = m.groups()
            mm = re.search(r"L=([\d.]+)mm", tail)
            d["nets"][net] = dict(group=g, ok=(ok == "True"), fails=int(fails),
                                  length=float(mm.group(1)) if mm else None)
            d["groups"][g][ok] += 1
        # ③ SUM
        if s.startswith("[SUM"):
            d["sum_line"] = s
    return d


def show(path, d):
    print("═══ %s ═══" % path)
    if d["gnd"]:
        ok, bad = d["gnd"]
        print("  GND 下拉: %d 成功 / %d 失败" % (ok, bad))
    r = d["reasons"]
    if r:
        tot = sum(r.values()) or 1
        print("  失败原因 Top (★共 %d 次★):" % sum(r.values()))
        for k, v in sorted(r.items(), key=lambda x: -x[1])[:8]:
            print("     %-14s %8d  (%.1f%%)" % (k, v, 100.0 * v / tot))
    if d["sum_line"]:
        print("  %s" % d["sum_line"])
    fail = {n: v for n, v in d["nets"].items() if not v["ok"] or v["fails"]}
    print("  逐网失败/残缺: %d 个网" % len(fail))
    for n, v in sorted(fail.items(), key=lambda x: -x[1]["fails"])[:15]:
        print("     %-24s 组=%-6s ok=%-5s 失败脚=%d" % (n, v["group"], v["ok"], v["fails"]))
    print()


def cmp(a_path, b_path):
    A, B = parse_log(a_path), parse_log(b_path)
    print("═══ 逐网差分: %s  →  %s ═══" % (a_path, b_path))
    ka = sum(1 for v in A["nets"].values() if v["ok"])
    kb = sum(1 for v in B["nets"].values() if v["ok"])
    print("  ok 网数: %d → %d   (Δ %+d)" % (ka, kb, kb - ka))
    diff = []
    for n in sorted(set(A["nets"]) | set(B["nets"])):
        va, vb = A["nets"].get(n), B["nets"].get(n)
        if not va or not vb:
            continue
        if va["ok"] != vb["ok"] or va["fails"] != vb["fails"]:
            diff.append((n, va, vb))
    print("  状态/失败脚不同的网: %d 个" % len(diff))
    for n, va, vb in diff:
        tag = "★赚★" if (va["ok"] and not vb["ok"]) is False and vb["ok"] else "★赔★"
        print("     %-24s %s ok=%-5s 失败脚=%d  →  ok=%-5s 失败脚=%d   %s"
              % (n, tag, va["ok"], va["fails"], vb["ok"], vb["fails"],
                 "改善" if (vb["ok"] and not va["ok"]) else ("退化" if (va["ok"] and not vb["ok"]) else "脚数变化")))
    if A["reasons"] and B["reasons"]:
        print("  失败原因变化 (A→B):")
        for k in sorted(set(A["reasons"]) | set(B["reasons"])):
            va, vb = A["reasons"].get(k, 0), B["reasons"].get(k, 0)
            if va != vb:
                print("     %-14s %8d → %8d  (Δ %+d)" % (k, va, vb, vb - va))


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    if args[0] == "--cmp" and len(args) >= 3:
        cmp(args[1], args[2])
        return 0
    for p in args:
        if p.startswith("--"):
            continue
        show(p, parse_log(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
