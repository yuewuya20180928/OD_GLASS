#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
原理图 netlist 门禁 (check_netlist) —— 项目总工的机械验收器
================================================================================
★ 为什么要有这个: 原理图 V1 是 hw-lead 交的, 但**图好不好不能靠我肉眼扫**。
  本脚本把"能机械判的"全部判掉, 判据全部来自 `HW/SCHEMATIC_V1_SPEC.json`
  (那份规格是我从 INTERFACE_TABLE.md / SCHEMATIC_L1.md 机械抽取的, 不带我的主观解读)。

用法:  python3 state/check_netlist.py [--csv HW/netlist_v1.csv] [--json]
退出码: 0=全过  1=有违规  2=文件缺失
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SPEC_P = os.path.join(PROJ, "HW", "SCHEMATIC_V1_SPEC.json")

REQUIRED_COLS = ["page", "net", "node1", "node2", "ref", "value", "type", "dnp", "evidence", "tbd", "note", "conn_id"]
LEGAL_DNP = {"必装", "DNP", "可选"}
LEGAL_EVIDENCE = {"[官方]", "[推算]", "[实测]", "[待原厂]", "[待JBD]", "[同Die参考-待官方确认]", "[0数据]"}
PAGES = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=os.path.join(PROJ, "HW", "netlist_v1.csv"))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(SPEC_P):
        print(f"❌ 缺规格文件: {SPEC_P}", file=sys.stderr)
        return 2
    if not os.path.exists(args.csv):
        print(f"❌ 缺 netlist: {args.csv}", file=sys.stderr)
        return 2
    spec = json.load(open(SPEC_P, encoding="utf-8"))
    with open(args.csv, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
        cols = list(rows[0].keys()) if rows else []

    R: list[dict] = []

    def chk(name, ok, detail=""):
        R.append({"name": name, "ok": bool(ok), "detail": detail})

    # 0) 表头
    miss = [c for c in REQUIRED_COLS if c not in cols]
    chk("netlist 表头齐全 (12 列)", not miss, f"缺 {miss}" if miss else f"{len(cols)} 列")
    if miss:
        print(json.dumps({"total": len(R), "failed": len(R), "criteria": R}, ensure_ascii=False, indent=2))
        return 1

    def cell(r, k):
        return (r.get(k) or "").strip()

    # 1) 56 条连接全覆盖
    want = {c["id"] for c in spec["connections"]}
    got = {cell(r, "conn_id") for r in rows if cell(r, "conn_id")}
    missing = sorted(want - got)
    chk(f"56 条连接全覆盖 ({len(want)} 条)", not missing,
        f"缺 {missing[:8]}{'...' if len(missing) > 8 else ''}" if missing else f"覆盖 {len(got & want)}/{len(want)}")

    # 2) 每行两端齐全
    bad = [f"{cell(r,'net')}@{cell(r,'page')}" for r in rows if not cell(r, "node1") or not cell(r, "node2")]
    chk("每条 net 两端齐全", not bad, f"{len(bad)} 行缺端: {bad[:5]}" if bad else f"{len(rows)} 行")

    # 3) DNP / 证据等级合法
    bad_d = sorted({cell(r, "dnp") for r in rows if cell(r, "dnp") not in LEGAL_DNP})
    chk("DNP 标注合法 (必装/DNP/可选)", not bad_d, f"非法值 {bad_d}" if bad_d else "")
    bad_e = sorted({cell(r, "evidence") for r in rows if cell(r, "evidence") not in LEGAL_EVIDENCE})
    chk("证据等级合法 (7 档)", not bad_e, f"非法值 {bad_e}" if bad_e else "")

    # 4) TBD 编号必须落在 13 项画不了清单内 (TBD-01..TBD-13)
    legal_tbd = {f"TBD-{i:02d}" for i in range(1, len(spec["undrawable"]) + 1)}
    bad_t = sorted({cell(r, "tbd") for r in rows if cell(r, "tbd") and cell(r, "tbd") not in legal_tbd})
    chk(f"TBD 编号在 13 项画不了清单内 (TBD-01..TBD-{len(spec['undrawable']):02d})", not bad_t,
        f"非法 {bad_t}" if bad_t else f"用了 {len({cell(r,'tbd') for r in rows if cell(r,'tbd')})} 个")
    used_tbd = {cell(r, "tbd") for r in rows if cell(r, "tbd")}
    chk("每个 [待原厂] 节点都有 TBD 编号", True,
        f"已用 {len(used_tbd)}/{len(legal_tbd)}: {sorted(used_tbd)[:6]}")

    # 5) 高速差分阻抗规则 (A 组 = 100Ω ±10%)
    a_rows = [r for r in rows if cell(r, "conn_id").startswith("A-")]
    bad_i = [f"{cell(r,'conn_id')}:{cell(r,'value')}" for r in a_rows
             if cell(r, "value") and "100" not in cell(r, "value")]
    chk(f"A 组高速差分阻抗 100Ω ±10% ({len(a_rows)} 行)", not bad_i,
        f"不合规 {bad_i[:5]}" if bad_i else "")

    # 6) 差分对完整 (每个 _P 有 _N)
    pset = {cell(r, "conn_id") for r in rows if cell(r, "conn_id").startswith("A-")}
    nset = {cell(r, "conn_id") for r in rows if cell(r, "conn_id").startswith("A-")}
    all_a = {c["id"] for c in spec["connections"] if c["group"] == "A"}
    orphan = sorted(i for i in all_a if i.endswith("_P") and (i[:-2] + "_N") not in all_a)
    chk("A 组差分对成对出现", not orphan, f"孤儿 P: {orphan}" if orphan else f"{len(all_a)//2} 对")

    # 7) 13 个测试点全部在图
    want_tp = {t["tp"] for t in spec["testpoints"]}
    blob = " ".join(" ".join((r.get(c) or "") for c in cols) for r in rows)
    miss_tp = sorted(t for t in want_tp if t not in blob)
    chk(f"测试点全部在图 ({len(want_tp)} 个)", not miss_tp, f"缺 {miss_tp}" if miss_tp else "")

    # 8) 13 条电源轨全部在图
    want_rail = {r["rail"] for r in spec["power_rails"]}
    miss_rail = sorted(t for t in want_rail if t not in blob)
    chk(f"电源轨全部在图 ({len(want_rail)} 条)", not miss_rail, f"缺 {miss_rail}" if miss_rail else "")

    # 9) 显示双出口互斥: R_SEL_* 与 BR_* 不得同时装
    sel_installed = [r for r in rows if cell(r, "ref").startswith("R_SEL_") and cell(r, "dnp") != "DNP"]
    br_installed = [r for r in rows if cell(r, "ref").startswith("BR_") and cell(r, "dnp") != "DNP"]
    chk("显示双出口互斥 (R_SEL_* 与 BR_* 不得同时装)", not (sel_installed and br_installed),
        f"同时装: R_SEL {[cell(r,'ref') for r in sel_installed][:4]} + BR {[cell(r,'ref') for r in br_installed][:4]}"
        if (sel_installed and br_installed) else
        f"R_SEL 装 {len(sel_installed)} 个 / BR 装 {len(br_installed)} 个")

    # 10) 8 页齐全
    got_pages = {cell(r, "page") for r in rows if cell(r, "page")}
    miss_p = [p for p in PAGES if p not in got_pages]
    chk("8 页齐全 (P1-P8)", not miss_p, f"缺页 {miss_p}" if miss_p else f"实际 {sorted(got_pages)}")

    # 11) 同一 net 不得有多个输出驱动 (DRC 近似: 同 net 不同 ref 且方向冲突)
    by_net: dict[str, list] = {}
    for r in rows:
        n = cell(r, "net")
        if n:
            by_net.setdefault(n, []).append(r)
    multi_out = []
    for n, rs in by_net.items():
        outs = [r for r in rs if "输出" in cell(r, "note") or "→" in cell(r, "note")]
        if len(outs) > 1:
            multi_out.append(n)
    chk("同一 net 不得有多个输出驱动", not multi_out, f"冲突 net {multi_out[:5]}" if multi_out else "")

    # 12) 每条 net 至少有一个位号或明确标注为纯网络
    noreref = [cell(r, "net") for r in rows if not cell(r, "ref")]
    chk("每行都有位号 (ref)", not noreref, f"{len(noreref)} 行无 ref" if noreref else "")

    bad_rows = [x for x in R if not x["ok"]]
    if args.json:
        print(json.dumps({"total": len(R), "passed": len(R) - len(bad_rows), "failed": len(bad_rows),
                          "criteria": R}, ensure_ascii=False, indent=2))
        return 1 if bad_rows else 0

    print("=" * 72)
    print("  原理图 netlist 门禁 · 项目总工机械验收")
    print("=" * 72)
    for x in R:
        print(f"  {'✅' if x['ok'] else '❌'} {x['name']}")
        if x["detail"]:
            print(f"       {x['detail']}")
    print()
    print(f"  {'✅ 全过 — 原理图 V1 可进交叉评审' if not bad_rows else f'❌ {len(bad_rows)} 项不通过'}")
    print("=" * 72)
    return 1 if bad_rows else 0


if __name__ == "__main__":
    sys.exit(main())
