#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-338 · 占位符三查
★三类触发 token 用 re.escape 逐个精确匹配 (★不用 '|'.join 拼正则 —— 空片段会匹配一切★)★
"""
import re, sys
# ★三类: ① HTML 注释起始 ② 待填类标记 (逐个精确串) ③ __大写__ 占位
PATS = [
    ("html-comment", [re.escape("<!--")]),
    ("todo-marker",  ["\U0001f504", "待填", "PLACEHOLDER", "施工中"]),
    ("underscore",   [r"__[A-Z_]+__"]),
]
FILES = ["SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md",
         "HANDOFF/2026-11-19_sw-lead_ISS338_9条单端脚固件引用.md"]
rc = 0
for f in FILES:
    t = open(f, encoding="utf-8").read()
    for name, pats in PATS:
        n = sum(len(re.findall(p, t)) for p in pats)
        if n: rc = 1
        print("  %-46s %-13s %s (%d)" % (f.split("/")[-1][:46], name, "OK" if n == 0 else "RED", n))
print("PLACEHOLDER_CHECK_RC=%d  (★全 0 = 过★)" % rc)
sys.exit(rc)
