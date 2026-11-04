#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_analyze_unc.py —— 读 DRC json, 按网统计未连接项 (临时工具, 用完删)"""
import json
import sys
from collections import defaultdict

P = sys.argv[1] if len(sys.argv) > 1 else "/tmp/_pcb_drc.json"
d = json.load(open(P))
unc = d.get("unconnected_items") or []
viol = d.get("violations") or []
print("violations: %d   unconnected: %d" % (len(viol), len(unc)))

by = defaultdict(list)
for u in unc:
    by[u.get("net") or "?"].append(u)

print("\n=== 未连接按网 (共 %d 个网) ===" % len(by))
for net, items in sorted(by.items(), key=lambda kv: -len(kv[1])):
    pos = []
    for it in items:
        p = it.get("pos") or {}
        pos.append("(%.2f,%.2f)" % (p.get("x", 0), p.get("y", 0)))
    desc = (items[0].get("description") or "")[:70]
    print("  %-26s n=%-3d %s" % (net, len(items), desc))
    print("       %s" % " ".join(pos[:14]))

if viol:
    print("\n=== 违规 ===")
    for v in viol:
        print("  [%s] %s" % (v.get("type"), str(v.get("description"))[:120]))
        for it in (v.get("items") or []):
            print("      -", str(it.get("description"))[:100], it.get("pos"))
