#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_unc_map.py —— 把 DRC 的 unconnected items 映射到 (ref, pad) + 同网所有焊盘
   用法: bash state/pcbnew_py.sh state/probe_unc_map.py <板> <drc.json>"""
import json
import os
import re
import sys

import pcbnew

PCB = sys.argv[1]
DRC = sys.argv[2]

board = pcbnew.LoadBoard(PCB)
d = json.load(open(DRC))

pads_by_pos = {}
pads_by_net = {}
for fp in board.GetFootprints():
    ref = fp.GetReference()
    for pad in fp.Pads():
        p = pad.GetPosition()
        x = pcbnew.ToMM(p.x)
        y = pcbnew.ToMM(p.y)
        net = pad.GetNetname()
        pads_by_pos[(round(x, 2), round(y, 2))] = (ref, pad.GetNumber(), net, x, y)
        pads_by_net.setdefault(net, []).append((ref, pad.GetNumber(), x, y))


def near(x, y, tol=0.6):
    best = None
    for (px, py), v in pads_by_pos.items():
        if abs(px - x) < tol and abs(py - y) < tol:
            d2 = (px - x) ** 2 + (py - y) ** 2
            if best is None or d2 < best[0]:
                best = (d2, v)
    return best[1] if best else None


u = d.get("unconnected_items") or []
print("unconnected items: %d" % len(u))
rows = []
for x in u:
    its = x.get("items") or []
    if len(its) < 2:
        continue

    def g(i):
        s = str(i.get("description", ""))
        p = i.get("pos") or {}
        m = re.search(r"\[([^\]]+)\]", s)
        return (m.group(1) if m else "?", p.get("x"), p.get("y"))

    a, b = g(its[0]), g(its[1])
    na, nb = near(a[1], a[2]), near(b[1], b[2])
    rows.append((a[0], na, nb, a, b))

print()
print("%-20s %-22s %-22s %-8s" % ("NET", "ENDPOINT A", "ENDPOINT B", "DIST"))
for net, na, nb, a, b in rows:
    sa = "%s.%s" % (na[0], na[1]) if na else "?@%.2f,%.2f" % (a[1], a[2])
    sb = "%s.%s" % (nb[0], nb[1]) if nb else "?@%.2f,%.2f" % (b[1], b[2])
    d = ((a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5
    print("%-20s %-22s %-22s %8.2f" % (net, sa, sb, d))

print()
print("=== 各网全部焊盘 (含已通) ===")
for net in sorted(set(r[0] for r in rows)):
    ps = pads_by_net.get(net, [])
    print("  %-20s %d pads: %s" % (net, len(ps),
          ", ".join("%s.%s(%.1f,%.1f)" % (r, n, x, y) for r, n, x, y in ps)))
