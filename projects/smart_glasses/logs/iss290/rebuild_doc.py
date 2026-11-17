#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-290 · 重新回填 MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md 的 §3 表 / §3.1 明细 / §7 JSON 块"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
DOC = os.path.join(ROOT, "MECH", "BOARD_ONEPASS_STRUCT_CROSSCHECK.md")
D = json.load(open(os.path.join(HERE, "compute_iss290.json"), encoding="utf-8"))
tables = open(os.path.join(HERE, "tables.md"), encoding="utf-8").read()
s3 = tables.split("### §3 表行", 1)[1].split("### §3 附", 1)[0].strip()
s3d = tables.split("### §3 附: 目标位 vs 现状 / 净距明细", 1)[1].split("### §4 板读 land pattern 明细", 1)[0].strip()

txt = open(DOC, encoding="utf-8").read()

# ---- §3 表 ----
a = txt.index("| `ref` | `frame` | `target_x` |")
b = txt.index("### ★§3.1 逐条明细")
txt = txt[:a] + s3 + "\n\n" + txt[b:]

# ---- §3.1 明细 ----
a = txt.index("| `ref` | 板上现状原点 |")
b = txt.index("### ★§3.2 结论")
txt = txt[:a] + s3d + "\n\n" + txt[b:]

# ---- §7 JSON 块 (从 compute_iss290.json + 追加的保留区口径重建) ----
block = build_block = None
import importlib.util
spec_ = importlib.util.spec_from_file_location("bd", os.path.join(HERE, "build_doc.py"))
# 直接复用 build_doc 的 zone/connector 构造逻辑 (不重写一遍)
src = open(os.path.join(HERE, "build_doc.py"), encoding="utf-8").read()
src = src.split("txt = open(DOC", 1)[0]
ns = {"D": D, "__name__": "bd", "__file__": os.path.join(HERE, "build_doc.py")}
exec(compile(src.replace('DOC = os.path.join(ROOT, "MECH", "BOARD_ONEPASS_STRUCT_CROSSCHECK.md")', "DOC = None"),
             "build_doc_parts", "exec"), ns)
block = ns["block"]

m = re.search(r"(<!-- MACHINE-BLOCK-BEGIN -->\s*```json\n)(.*?)(\n```\s*<!-- MACHINE-BLOCK-END -->)",
              txt, re.S)
if not m:
    raise SystemExit("机器块定位失败")
txt = txt[:m.start(2)] + json.dumps(block, ensure_ascii=False, indent=1) + txt[m.end(2):]

open(DOC, "w", encoding="utf-8").write(txt)
print("rebuilt:", DOC, os.path.getsize(DOC), "B")
