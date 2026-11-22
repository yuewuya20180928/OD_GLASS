#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""parse_escape_blockers.py (ISS-334 沙盒·只读) —— 从出脚可行性读数里抽出
【零铜网每个端点的最近异网阻挡物】⇒ 给死因归桶用。

用法: python3 tmp/iss334/parse_escape_blockers.py <escape_feasibility.txt> <zero_copper.json> [--out md]
"""
import sys
import json
import re

txt = open(sys.argv[1], encoding="utf-8").read()
d = json.load(open(sys.argv[2], encoding="utf-8"))
zero = [z["net"] for z in d["zero_nets"] if z["net"]]
outf = None
if "--out" in sys.argv:
    outf = sys.argv[sys.argv.index("--out") + 1]

out = {}
cur = None
ep = ""
for raw in txt.split("\n"):
    m = re.search(r"([A-Za-z0-9_]+) @ ([\w.]+) \(([-\d.]+), ([-\d.]+)\)", raw)
    if m and "W=0." not in raw:
        cur = m.group(1)
        ep = m.group(2)
        continue
    mm = re.search(r"W=0\.15.*?([\u4e00-\u9fff]{2,6})\s+(\S+)\s+([\d.]+).*?余量\s+([+\-][\d.]+)mm"
                   r".*?\[([^\]]+)\]\s+([\d.]+)", raw)
    if mm and cur:
        out.setdefault(cur, []).append(dict(ep=ep, dirn=mm.group(2), length=mm.group(3),
                                            margin=mm.group(4), blocker=mm.group(5),
                                            dist=float(mm.group(6))))

lines = []
for n in sorted(zero):
    eps = out.get(n)
    if not eps:
        lines.append("| `%s` | (无端点读数) | | | | |" % n)
        print("| `%s` | (无端点读数) | | | | |" % n)
        continue
    for e in eps:
        row = "| `%s` | %s | %s | %s | %s | `%s` @ %smm |" % (
            n, e["ep"], e["dirn"], e["length"], e["margin"], e["blocker"], e["dist"])
        lines.append(row)
        print(row)

if outf:
    with open(outf, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("存证: %s" % outf)
