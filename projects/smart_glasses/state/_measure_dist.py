#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_measure_dist.py —— ★量"失败网"的平均最长距离 (给 sweep_place.sh 用)

用法: bash state/pcbnew_py.sh state/_measure_dist.py <探针板>
输出: "平均最长距离 XX.Xmm 覆盖 N/M 网"
"""
import collections
import json
import math
import re
import sys

import pcbnew

PATH = sys.argv[1] if len(sys.argv) > 1 else "/tmp/probe.kicad_pcb"
DRC = "/tmp/_layout_done_drc.json"

nets = set()
try:
    d = json.load(open(DRC, encoding="utf-8"))
    for u in (d.get("unconnected_items") or []):
        for it in (u.get("items") or []):
            m = re.search(r"\[([^\]]+)\]", it.get("description", ""))
            if m:
                nets.add(m.group(1))
except Exception:
    pass
nets = {n for n in nets if n and n != "GND"}

b = pcbnew.LoadBoard(PATH)
bynet = collections.defaultdict(list)
for fp in b.GetFootprints():
    for p in fp.Pads():
        n = p.GetNetname()
        if not n:
            continue
        pos = p.GetPosition()
        bynet[n].append((pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)))

tot = 0.0
cnt = 0
for n in sorted(nets):
    ps = bynet.get(n, [])
    if len(ps) < 2:
        continue
    best = 0.0
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            best = max(best, math.hypot(ps[i][0] - ps[j][0], ps[i][1] - ps[j][1]))
    tot += best
    cnt += 1
print("平均最长距离 %.1fmm 覆盖 %d/%d 网" % (tot / max(cnt, 1), cnt, len(nets)))
