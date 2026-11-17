#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_ledger_reading_same_source.py —— ISS-296 「同源」机器证明 (mech-lead · 2026-11-17)
=========================================================================================
干什么:
  对**同一份落表台账文本** (`HW/SCHEMATIC_LANDING_V1_LANDED.md`, ★只读★),
  分别用【MECH 侧两个闸的台账解析器】与【SW 侧 ISS-284 定版闸的台账解析器】读一遍,
  比对两边读出的【链头 / 链 / 产出单号 / 记录集】⇒ **逐字相同** ⇒ `IDENTICAL: True`
  ⇒ 不相同 ⇒ `IDENTICAL: False` + 逐项 diff (⇒ 判红 ⇒ 本单不成立)。

★为什么必须有这个探针 (★不是形式主义★):
  MECH 侧这两道闸为了接「合法改板」通道, 各自抄了一份 SW 侧 ISS-284 的台账解析器
  (`ledger_cover_rows` / `ledger_change_rows` / `ledger_change_state`)。
  ⇒ ★**抄两份就有「抄歪」的风险** ⇒ ★**同一份台账必须读出同一个链头/链/单号** ★
  ⇒ 否则会出现「SW 侧判绿 · MECH 侧判红」的假红 ⇒ ★**那正是本单要消灭的病** ★

★本脚本只读: 不写任何文件 · 不改任何闸 · 三个被 import 的脚本都只取常量与函数 ★

用法:
  python3 logs/iss296/probe_ledger_reading_same_source.py          ⇒ 打印读数 + IDENTICAL 判定
  python3 logs/iss296/probe_ledger_reading_same_source.py --json   ⇒ 机器可读

退出码: 0 = IDENTICAL: True; 2 = 不相同 (★判红★)
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))

LEDGER = os.path.join("HW", "SCHEMATIC_LANDING_V1_LANDED.md")
BOARD_REL = "HW/PCB/demo_mainboard.kicad_pcb"
PRO_REL = "HW/PCB/demo_mainboard.kicad_pro"

# ★被比对的受管/受保护文件 (★板那一对必须带上: ★合法改板通道读的就是它们★)
RELS = (
    "HW/netlist_v1.csv",
    "HW/netlist_v1_pins.csv",
    "HW/BOM_v1.csv",
    BOARD_REL,
    PRO_REL,
)


def load(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def canonical(state: dict, recs: list, full_row: bool) -> dict:
    """把一次「读台账」的结论压成一个可逐字比对的结构。

    ★**只装【判决用得上的字段】**: 链头 / 链 / 产出单号 / 链头单号 / 取不准的原因 / 链上出现过的 md5 ★
    ★**判据字段一个都不许漏** (★漏了就等于没比★) ★
    ★`full_row=True` 时额外带上变更行的逐字原文 (★两边都是 160 字符截断 ⇒ 应逐字相同★) ★
    """
    rec_keys = ("prev", "new", "iss", "sec") + (("row",) if full_row else ())
    return {
        "head": state.get("head"),
        "chain": list(state.get("chain") or []),
        "head_iss": list(state.get("head_iss") or []),
        "why": state.get("why"),
        "known": sorted(state.get("known") or set()),
        "producer": {k: sorted(v) for k, v in (state.get("producer") or {}).items()},
        "records": [tuple(r.get(k) for k in rec_keys) for r in recs],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    sw = load(os.path.join(PROJ, "SW", "tools", "check_demo_panel_spec.py"), "sw_panel_spec_ro")
    m1 = load(os.path.join(PROJ, "MECH", "check_board_frame_coords.py"), "mech_frame_ro")
    m2 = load(os.path.join(PROJ, "MECH", "check_demo_struct_truth.py"), "mech_truth_ro")

    led_path = os.path.join(PROJ, LEDGER)
    with open(led_path, encoding="utf-8") as f:
        text = f.read()

    # ★同组受保护件的名字别名 (★SW 侧 `check_r6_hard_protected` 里的同一条口径★)
    def aliases_of(rel: str) -> set:
        others = [r for r in RELS if r in (BOARD_REL, PRO_REL) and r != rel]
        out = set()
        for o in others:
            b = os.path.basename(o)
            out |= {o, b, os.path.splitext(b)[1]}
        return out

    results = []
    identical = True
    for rel in RELS:
        excl = aliases_of(rel)
        for tag, sw_state_fn, sw_rec_fn, m_state_fn, m_rec_fn in (
            ("base", sw.sw_ledger_state, sw.sw_ledger_records,
             m1.ledger_state, m1.ledger_records),
            ("change", sw.sw_ledger_change_state, sw.sw_ledger_change_rows,
             m1.ledger_change_state, m1.ledger_change_rows),
            ("change@demo_struct_truth", sw.sw_ledger_change_state, sw.sw_ledger_change_rows,
             m2.ledger_change_state, m2.ledger_change_rows),
        ):
            if tag == "base":
                sw_recs = sw_rec_fn(text, rel)
                m_recs = m_rec_fn(text, rel)
                sw_st = sw_state_fn(rel, text, sw_recs)
                m_st = m_state_fn(rel, text, m_recs)
                full_row = False
            else:
                sw_recs = sw_rec_fn(text, rel, excl)
                m_recs = m_rec_fn(text, rel, excl)
                sw_st = sw_state_fn(rel, text, excl)
                m_st = m_state_fn(rel, text, excl)
                full_row = True
            a = canonical(sw_st, sw_recs, full_row)
            b = canonical(m_st, m_recs, full_row)
            same = (a == b)
            identical = identical and same
            results.append({
                "file": rel, "mode": tag, "identical": same,
                "head": a["head"], "chain_len": len(a["chain"]),
                "head_iss": a["head_iss"], "records": len(a["records"]),
                "sw": a if not same else None,
                "mech": b if not same else None,
            })

    if args.json:
        print(json.dumps({"IDENTICAL": identical, "results": results},
                         ensure_ascii=False, indent=2))
        return 0 if identical else 2

    print("=" * 100)
    print("ISS-296 同源探针 —— MECH 侧台账解析器 vs SW 侧 (ISS-284 定版闸) 台账解析器")
    print("=" * 100)
    print(f"判决源台账: {LEDGER} (★只读★)")
    print("-" * 100)
    print(f"{'文件':<40} {'读法':<26} {'链头':<14} {'链长':>4} {'记录':>4}  {'链头单号':<12} 逐字相同")
    for r in results:
        print(f"{r['file']:<40} {r['mode']:<26} {str(r['head']):<14} {r['chain_len']:>4} "
              f"{r['records']:>4}  {(','.join(r['head_iss']) or '无'):<12} {r['identical']}")
        if not r["identical"]:
            print("   ★★DIFF★★")
            for k in r["sw"]:
                if r["sw"][k] != r["mech"][k]:
                    print(f"     {k}:\n       SW  = {str(r['sw'][k])[:600]}\n"
                          f"       MECH = {str(r['mech'][k])[:600]}")
    print("-" * 100)
    print(f"IDENTICAL: {identical}")
    print("★口径: 比对的字段 = 链头 / 链 / 链头单号 / 取不准原因 / 链上出现过的 md5 / "
          "记录集(prev,new,iss,sec[,row,full]) ★")
    print("★★`base` 读法用两边各自的「全部落表记录」函数 (`ledger_records` vs `sw_ledger_records`) ★")
    print("★★`change` 读法用本单新增的「只认改前≠改后的变更行」函数 (★板那一对要剔歧义行★) ★★")
    return 0 if identical else 2


if __name__ == "__main__":
    sys.exit(main())
