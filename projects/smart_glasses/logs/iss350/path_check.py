#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-350 · 交卷页页内引用路径在盘校验 (MISS = 0)"""
import re, os, sys

PAGE = 'HANDOFF/2026-11-23_sw-lead_ISS350_Q3分档口径写回SW侧.md'
page = open(PAGE, encoding='utf-8').read()

cands = set()
for m in re.finditer(r'([A-Za-z0-9_./\u4e00-\u9fff-]+\.(?:md|csv|py|json|yaml|kicad_pcb|kicad_pro|txt|log|bak|yml))(?::\d+)?', page):
    p = m.group(1)
    if '/' not in p:
        continue
    cands.add(p.lstrip('`(').strip('`,`'))
for m in re.finditer(r'\b(logs/iss\d+/|state/fragments/|state/dispatch_briefs/|HANDOFF/|SW/|HW/)', page):
    cands.add(m.group(1))

ok = [p for p in sorted(cands) if os.path.exists(p)]
miss = [p for p in sorted(cands) if not os.path.exists(p)]

print('== ISS-350 交卷页 · 页内引用路径在盘校验 (终版) ==')
print(f'页文件 = {PAGE}  ({len(page)} 字符)')
print(f'候选引用路径 {len(cands)} 条 · 在盘 OK {len(ok)} 条 · MISS {len(miss)} 条')
print()
for p in ok:
    print('  OK   ', p)
for p in miss:
    print('  MISS ', p)
print()
print('★MISS = 0 =', len(miss) == 0)
sys.exit(0 if not miss else 1)
