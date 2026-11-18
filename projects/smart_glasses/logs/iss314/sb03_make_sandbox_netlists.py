#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sb03_make_sandbox_netlists.py —— ISS-314 沙盒: 造【网表侧改名】的沙盒网表

★只写沙盒目录 (tmp/iss314_sandbox/) ⇒ 项目网表一个字节不许动 ★
★规则 = ISS-205: 末字符是数字 ⇒ 不动; 否则加 `_1`
★产出:
   netlist_ref1.csv   = 项目网表 + 表侧 ref 全部按 ISS-205 改名 (⇒ 三侧同口径)
   netlist_broken.csv = netlist_ref1.csv 再故意删掉 3 个 ref 的行 (⇒ 模拟"映射表被改坏")
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(PROJ, "HW", "netlist_v1.csv")

NODE_RE = re.compile(r"^([A-Za-z_0-9]+)(\s+.*)?$")


def kicad_ref(ref):
    """★ISS-205 规则 (与 state/gen_kicad_sch.py::kicad_ref() 同口径)"""
    ref = (ref or "").strip()
    if not ref:
        return ref
    if ref.startswith(("RAIL_", "NET_")):
        return ref
    if ref[-1].isdigit():
        return ref
    return ref + "_1"


def rename_node(node):
    node = (node or "").strip()
    if not node:
        return node
    m = NODE_RE.match(node)
    if not m:
        return node
    comp = m.group(1)
    tail = m.group(2) or ""
    if comp.startswith(("RAIL_", "NET_")):
        return node
    return kicad_ref(comp) + tail


rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
flds = list(rows[0].keys())

out1 = os.path.join(HERE, "netlist_ref1.csv")
with open(out1, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=flds)
    w.writeheader()
    for r in rows:
        r2 = dict(r)
        r2["ref"] = kicad_ref(r.get("ref"))
        r2["node1"] = rename_node(r.get("node1"))
        r2["node2"] = rename_node(r.get("node2"))
        w.writerow(r2)
print("★已生成沙盒网表 (表侧同口径改名): %s" % out1)

# ---- 故意改坏: 删掉 3 个 ref 的全部行 (★模拟"落表只改了一半"★)
BROKEN = {"Q_PG", "U_EN_SW", "SW_BOOT"}
out2 = os.path.join(HERE, "netlist_broken.csv")
n = 0
with open(out2, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=flds)
    w.writeheader()
    for r in rows:
        r2 = dict(r)
        ref = (r.get("ref") or "").strip()
        nodes = " ".join([r.get("node1") or "", r.get("node2") or ""])
        if ref in BROKEN or any(re.search(r"\b%s\b" % re.escape(b), nodes) for b in BROKEN):
            n += 1
            continue
        r2["ref"] = kicad_ref(r.get("ref"))
        r2["node1"] = rename_node(r.get("node1"))
        r2["node2"] = rename_node(r.get("node2"))
        w.writerow(r2)
print("★已生成沙盒网表 (故意删掉 %d 行 / 3 个 ref): %s" % (n, out2))

# ---- 报表
for tag, p in (("项目正本", SRC), ("同口径改名", out1), ("故意改坏", out2)):
    rs = list(csv.DictReader(open(p, encoding="utf-8")))
    refs = {(x.get("ref") or "").strip() for x in rs}
    refs = {x for x in refs if x}
    print("★ %-12s 行 %4d · ref 去重 %3d · 带 _1 的 %3d"
          % (tag, len(rs), len(refs), len([x for x in refs if x.endswith("_1")])))
