#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os
PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(PROJ, "logs", "iss358")
ml = json.load(open(os.path.join(OUT, "merge_log.json"), encoding="utf-8"))
rn = json.load(open(os.path.join(OUT, "renames.json"), encoding="utf-8"))
cl = json.load(open(os.path.join(OUT, "claim_log.json"), encoding="utf-8"))
BT = chr(96)
L = []
L.append("# ISS-358 · 已并入 / 已去重登记清单 (可逐条追回)")
L.append("")
L.append("## A. answers 改 key 8 条 (★value/to/ref 一字未改, 只换 key 名★)")
L.append("")
L.append("| 原 idx | 原 key | 新 key | to | value 字数 | ref |")
L.append("|---|---|---|---|---|---|")
for r in rn:
    L.append("| %d | %s%s%s | %s%s%s | %s | %d | %s |" % (
        r["idx"], BT, r["old_key"], BT, BT, r["new_key"], BT, r["to"], r["vlen"], r["ref"]))
L.append("")
L.append("★逐条原文见 logs/iss358/renames.json (含 value 全文)★")
L.append("")
L.append("## B. artifacts 同 path 合并 31 组 (★被并入的 summary 逐字保留在 base 条目的 summary 里, 可按 #序号 追回★)")
L.append("")
for m in ml:
    L.append("### %s%s%s  (原 %d 条 → 1 条)" % (BT, m["path"], BT, 1 + len(m["absorbed"])))
    L.append("- **保留主登记**: 原 #%d · kind=%s · version=%s · updated_at=%s" % (
        m["base_idx"], m["base_kind"], m["base_version"], m["base_updated_at"]))
    L.append("  - summary 原文: %s" % m["base_summary"])
    for a in m["absorbed"]:
        L.append("- **并入**: 原 #%d · kind=%s · version=%s · updated_at=%s" % (
            a["idx"], a["kind"], a["version"], a["updated_at"]))
        L.append("  - summary 原文: %s" % a["summary"])
    L.append("")
L.append("## C. interface_claims 逐字重名 1 组")
L.append("")
for c in cl:
    L.append("- 保留 原 #%d, 删 原 #%d · key=%s%s%s (★两条目逐字相同 ⇒ 合并后 interface_claims 取值不变★)" % (
        c["kept_idx"], c["dropped_idx"], BT, c["key"], BT))
    L.append("  - 原文: %s" % json.dumps(c["entry"], ensure_ascii=False))
L.append("")
open(os.path.join(OUT, "dedup_list.md"), "w", encoding="utf-8").write("\n".join(L))
print("dedup_list.md 写好, 行数", len(L))
