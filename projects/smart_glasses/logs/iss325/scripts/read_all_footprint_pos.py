#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-325 · read_all_footprint_pos.py -- 读一块板【全部】封装原点 (pcbnew 权威读法)
⇒ 用来判「两臂落位是否逐个完全相同」(★不只是 20 个 TP/R_SEL, 是全板所有封装★)

用法: bash state/pcbnew_py.sh logs/iss325/scripts/read_all_footprint_pos.py <板> <标签>
"""
import sys

import pcbnew

b = pcbnew.LoadBoard(sys.argv[1])
rows = []
for fp in b.GetFootprints():
    p = fp.GetPosition()
    rows.append((fp.GetReference(),
                 round(pcbnew.ToMM(p.x), 4),
                 round(pcbnew.ToMM(p.y), 4),
                 fp.GetOrientationDegrees()))
rows.sort()
print("__FP__ count=%d board=%s" % (len(rows), sys.argv[1]))
for r in rows:
    print("%s\t%s\t%s\t%s" % r)
