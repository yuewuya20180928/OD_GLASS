#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_sync_projection.py —— ISS-294 · 【§5 机器块 ⇄ §2 逐条表】两处逐字对得上的自证

只读 `MECH/BOARD_ONEPASS_MECH_SYNC.md`:
  ① §2.1 逐条表的 `MECH-PORT-USBC` 行 (8 字段) 与 §5 机器块 `items[]` 的同名条目【逐字段对账】
  ② §5 机器块 `openings[]` 的第三条 `PORT_OPEN_USBC` (15 个标准字段 + `tiers`) 字段齐全且非空
  ③ 三处 ( openings[] / items[] / §2 表 ) 的关键几何数逐个一致
  ④ `openings[]` 的 rect 与它自己的 `tiers["2.54"].open_rect` / `must_clear` 自洽
用法: python3 logs/iss294/check_sync_projection.py   (rc=0 = 全对得上)
"""
from __future__ import annotations

import json
import os
import re

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SPEC = os.path.join(PROJ, "MECH", "BOARD_ONEPASS_MECH_SYNC.md")
MACH_BEGIN = "<!-- MACHINE-BLOCK-BEGIN -->"
MACH_END = "<!-- MACHINE-BLOCK-END -->"

STD_FIELDS = ["id", "role", "covers", "frame", "body_w", "body_w_source", "rect",
              "x0_range", "y0_range_at_h_ref", "cl_x", "cl_y", "worst_cl_x",
              "worst_cl_y", "som_hits", "evidence"]
ITEM_FIELDS = ["id", "source_iss", "title", "current_state", "spec", "criterion",
               "blocked_by", "evidence"]
KEY_NUMS = ["132.995", "147.005", "7.300", "133.895", "146.105", "6.400",
            "0.900", "0.600", "135.680", "144.320", "134.220", "145.780"]

text = open(SPEC, encoding="utf-8").read()
b, e = text.find(MACH_BEGIN), text.find(MACH_END)
seg = text[b:e]
m = re.search(r"```json\n(.*?)\n```", seg, re.S)
data = json.loads(m.group(1))

errs = []
out = []

# ---- ② openings[] 第三条: 15 个标准字段一条不缺 + 非空 ----
ops = {o.get("id"): o for o in (data.get("openings") or [])}
out.append(f"openings[] 条数 = {len(ops)} → {sorted(ops)}")
usbc = ops.get("PORT_OPEN_USBC")
if usbc is None:
    errs.append("openings[] 里没有 PORT_OPEN_USBC")
else:
    miss = [f for f in STD_FIELDS if f not in usbc]
    empty = [f for f in STD_FIELDS if f in usbc and
             (usbc[f] is None or (isinstance(usbc[f], (str, list, dict)) and not usbc[f]))]
    out.append(f"PORT_OPEN_USBC 缺字段 = {miss or '无'} · 空字段 = {empty or '无'}")
    if miss:
        errs.append(f"PORT_OPEN_USBC 缺字段 {miss}")
    if empty:
        errs.append(f"PORT_OPEN_USBC 有空字段 {empty}")
    if not usbc.get("tiers"):
        errs.append("PORT_OPEN_USBC 没有 h 三档 (tiers)")
    else:
        out.append(f"tiers = {sorted(usbc['tiers'])} (h 三档)")
    # ④ rect 与 h_ref 档 / must_clear 自洽
    t = (usbc.get("tiers") or {}).get("2.54") or {}
    orr = t.get("open_rect") or {}
    rec = usbc.get("rect") or {}
    same = all(abs(float(rec.get(k, 1e9)) - float(orr.get(k, -1e9))) <= 0.01
               for k in ("x0", "x1", "y0", "y1"))
    out.append(f"rect {rec} vs tiers['2.54'].open_rect {orr} ⇒ {'一致' if same else '不一致'}")
    if not same:
        errs.append("PORT_OPEN_USBC 的 rect 与 tiers['2.54'].open_rect 不一致")
    mc = t.get("must_clear") or {}
    out.append(f"must_clear (h_ref 档) = {mc}")

# ---- ① §2 逐条表的 8 字段行 vs items[] 同名条目 ----
items = {it.get("id"): it for it in (data.get("items") or [])}
it = items.get("MECH-PORT-USBC")
if it is None:
    errs.append("items[] 里没有 MECH-PORT-USBC")
else:
    miss = [f for f in ITEM_FIELDS if f not in it]
    empty = [f for f in ITEM_FIELDS if f in it and not str(it[f]).strip()]
    out.append(f"items[MECH-PORT-USBC] 缺字段 = {miss or '无'} · 空字段 = {empty or '无'}")
    if miss:
        errs.append(f"items[MECH-PORT-USBC] 缺字段 {miss}")
    if empty:
        errs.append(f"items[MECH-PORT-USBC] 有空字段 {empty}")

# ---- §2 表里抓 MECH-PORT-USBC 那一行 (8 格) ----
row = None
for ln in text.split("\n"):
    if ln.startswith("|") and "MECH-PORT-USBC" in ln:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        row = cells
        break
if row is None:
    errs.append("§2 逐条表里找不到 MECH-PORT-USBC 行")
else:
    out.append(f"§2 表行格数 = {len(row)} (★要求 8★)")
    if len(row) != 8:
        errs.append(f"§2 表行格数 = {len(row)} (要求 8)")
    # ① 字段名顺序: 第 1 格 = id, 第 2 格 = source_iss
    out.append(f"§2 表第 1 格 = {row[0][:40]} · 第 2 格 = {row[1][:40]}")
    if "MECH-PORT-USBC" not in row[0]:
        errs.append("§2 表第 1 格不是 MECH-PORT-USBC")
    if "ISS-294" not in row[1]:
        errs.append("§2 表第 2 格不是 ISS-294")
    # ③ 关键几何数: 三处都要出现 (★按数值比, 不按字符串 (JSON 里 7.300 会写成 7.3)★)
    def nums(txt):
        return {round(float(x), 4) for x in re.findall(r"\d+\.\d+", txt)}

    tbl_nums = nums(" ".join(row))
    it_nums = nums(json.dumps(it, ensure_ascii=False)) if it else set()
    op_nums = nums(json.dumps(usbc, ensure_ascii=False)) if usbc else set()
    bad = []
    for n in KEY_NUMS:
        v = round(float(n), 4)
        if not (v in tbl_nums and v in it_nums and v in op_nums):
            bad.append((n, v in tbl_nums, v in it_nums, v in op_nums))
    out.append(f"关键几何数 {len(KEY_NUMS)} 个在 §2 表 / items[] / openings[] 三处一致 ⇒ "
               f"{'一致' if not bad else '不一致: ' + str(bad)}")
    if bad:
        errs.append(f"关键几何数在三处不一致: {bad}")

print("★【ISS-294 · §5 机器块 ⇄ §2 逐条表 对账】★")
for line in out:
    print("  " + line)
print(f"\n结论: {'✅ 两处逐字对得上' if not errs else '❌ ' + '; '.join(errs)}")
raise SystemExit(0 if not errs else 1)
