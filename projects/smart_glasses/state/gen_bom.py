#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOM 生成器 (gen_bom) —— 从 netlist_v1.csv 机械生成 HW/BOM_v1.csv
================================================================================
★为什么要有 (2026-10-27, 项目总工):
  `HW/ERC_DRC_CHECKLIST.md` §0 的投板放行条件第 8 条是 "**BOM 齐**:
  每行有 位号 / 值 / 封装 / 容差 / DNP / 替代料" —— V1 只有 netlist (器件级),
  **没有 BOM 表** → 备料/询价/拼板三件事都没有唯一口径, 每次都要从 392 行 netlist 里人肉挑。

★原则:
  ① BOM 是 **生成物**, 唯一真源是 `state/gen_netlist.py` → 任何人重跑不会漂
  ② 每个位号一行 (netlist 里一个电阻会出现 2-3 行, 这里按 ref 去重)
  ③ **封装/容差/替代料** 本版多数填不出来 (器件没定档) → 写 `待定`, **不许编**
  ④ 采购状态分档: 已定型 / 待选型 / 待原厂 / 待JBD / DNP不装 / 测试点 / 连接器
  ⑤ 板级归属列直接带过来 → 备料时就知道"镜框充电板"和"镜脚主 PCB"各要多少料

用法:  python3 state/gen_bom.py [--out HW/BOM_v1.csv]
退出码: 0=生成成功且自检全过  1=自检不通过
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
CSV_P = os.path.join(PROJ, "HW", "netlist_v1.csv")
OUT_DEFAULT = os.path.join(PROJ, "HW", "BOM_v1.csv")

BOARD_CN = {"CHG_BOARD": "镜框充电板", "MAIN_PCB": "镜脚主 PCB", "HINGE": "跨铰链界面"}


def procurement_status(ref: str, value: str, typ: str, dnp: str, evidence: str) -> tuple[str, str]:
    """返回 (采购状态, 备注)"""
    v = value or ""
    if dnp == "DNP":
        return ("DNP-不装", "方案A/B 二选一或预留位; 板上有位置但首版不贴")
    if "[待选型]" in v:
        return ("待选型", "型号待定: 询价/选型完成后回填")
    if "[待原厂]" in v or evidence == "[待原厂]":
        return ("待原厂", "等原厂回信 (球位/电源域/接口类)")
    if "[待JBD]" in v or evidence == "[待JBD]":
        return ("待JBD", "等 JBD 光机接口定义")
    if ref.startswith("TP_"):
        return ("测试点", "测试焊盘, 免 BOM 但要占板面")
    if typ == "CONN" or ref.startswith("J_") or ref.startswith("CONN_"):
        return ("连接器", "型号/间距/引脚编号待结构与装配复核 (★本版 pin 编号自拟)")
    if typ in ("R", "C", "L"):
        return ("已定型-无源件", "阻容感: 值/容差可定, **封装待板宽/贴装工艺定**")
    if typ == "IC":
        return ("已定型-IC", "型号已定 (官网/官方数据手册), 封装与替代料待采购确认")
    if typ == "SW":
        return ("已定型-开关", "按键/开关: 型号待选型")
    if typ == "LED":
        return ("已定型-LED", "LED: 型号待选型")
    return ("待分类", "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT_DEFAULT)
    args = ap.parse_args()
    if not os.path.exists(CSV_P):
        print(f"❌ 缺 netlist: {CSV_P}", file=sys.stderr)
        return 2
    rows = list(csv.DictReader(open(CSV_P, encoding="utf-8")))

    bom: "OrderedDict[str, dict]" = OrderedDict()
    for r in rows:
        ref = (r.get("ref") or "").strip()
        if not ref:
            continue
        status, memo = procurement_status(ref, r.get("value", ""), r.get("type", ""),
                                           r.get("dnp", ""), r.get("evidence", ""))
        # ★封装 / OPN 从网表行带过来 (2026-10-29 ISS-112) —— 真源是 state/gen_netlist.py 的 PARTS 寄存器,
        #   这里是搬运, 不是手写。网表行没有 ⇒ 待定 (不许编)。
        fp = (r.get("footprint") or "").strip()
        opn = (r.get("opn") or "").strip()
        if ref not in bom:
            bom[ref] = {
                "ref": ref,
                "qty": 1,
                "value": r.get("value", ""),
                "type": r.get("type", ""),
                "dnp": r.get("dnp", ""),
                "board": r.get("board", ""),
                "page": r.get("page", ""),
                "evidence": r.get("evidence", ""),
                "tbd": r.get("tbd", ""),
                "footprint": fp or "待定",
                "opn": opn,
                "tolerance": "待定",
                "alt_part": "待定",
                "procurement": status,
                "memo": memo,
            }
        else:
            # 同一 ref 多行 (netlist 里一个电阻会出现在多段网) → 合并, 不重复计数
            bom[ref]["qty"] = 1
            # ★B-6 修正 (2026-10-27 18:4x, hw-lead ISS-088 复审): DNP 判定必须是 **ref 级** →
            #   一个连接器既有 DNP 预留脚、又有必装脚时, 整颗被判 "DNP-不装" → 备料会漏买!
            #   正确口径: **所有行都是 DNP 才算不装**; 有任一必装行 → 必装 (预留脚不贴而已)。
            if r.get("dnp") == "DNP" and bom[ref]["dnp"] != "必装":
                bom[ref]["dnp"] = "DNP"
                bom[ref]["procurement"] = "DNP-不装"
            if bom[ref]["value"] != r.get("value", "") and not bom[ref]["value"]:
                bom[ref]["value"] = r.get("value", "")

    COLS = ["ref", "qty", "value", "type", "dnp", "board", "page", "evidence", "tbd",
            "footprint", "opn", "tolerance", "alt_part", "procurement", "memo"]
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for ref, b in bom.items():
            b["board"] = BOARD_CN.get(b["board"], b["board"])
            w.writerow({c: b.get(c, "") for c in COLS})

    # ---- 自检 (机械判) ----
    fails = []
    refs_in_net = {r["ref"] for r in rows if r.get("ref")}
    if set(bom) != refs_in_net:
        fails.append(f"位号集合不一致: BOM {len(bom)} vs netlist {len(refs_in_net)}")
    dup = [ref for ref, b in bom.items() if b["qty"] != 1]
    if dup:
        fails.append(f"qty 不等于 1 的位号: {dup[:5]}")
    no_status = [ref for ref, b in bom.items() if not b["procurement"]]
    if no_status:
        fails.append(f"无采购状态的位号: {no_status[:5]}")
    # ★口径与 BOM 侧一致 (2026-10-27 19:5x, P10 子 agent 指出): **所有行都 DNP 才算不装**
    by_ref_dnp: dict[str, set] = {}
    for r in rows:
        ref = (r.get("ref") or "").strip()
        if ref:
            by_ref_dnp.setdefault(ref, set()).add(r.get("dnp") or "")
    dnp_net = sum(1 for v in by_ref_dnp.values() if v == {"DNP"})
    dnp_bom = sum(1 for b in bom.values() if b["dnp"] == "DNP")
    if dnp_net != dnp_bom:
        fails.append(f"DNP 位号数不一致: netlist {dnp_net} vs BOM {dnp_bom}")
    board_missing = [ref for ref, b in bom.items() if not b["board"]]
    if board_missing:
        fails.append(f"无板级归属的位号: {board_missing[:5]}")

    by_status: dict[str, int] = {}
    for b in bom.values():
        by_status[b["procurement"]] = by_status.get(b["procurement"], 0) + 1
    by_board: dict[str, int] = {}
    for b in bom.values():
        by_board[b["board"]] = by_board.get(b["board"], 0) + 1

    # ---- 封装 / OPN 落地率 (ISS-112: C-9 "BOM 封装全部回填" 的进度指标) ----
    fp_done = [r for r, b in bom.items() if b["footprint"] not in ("", "待定")]
    opn_done = [r for r, b in bom.items() if (b.get("opn") or "").strip()]
    fp_todo = sorted(r for r, b in bom.items() if b["footprint"] in ("", "待定"))

    print("=" * 72)
    print("  BOM 生成 · 项目总工机械验收")
    print("=" * 72)
    print(f"  输出: {args.out}  ({os.path.getsize(args.out)} bytes)")
    print(f"  位号总数: {len(bom)}  (netlist 行数 {len(rows)})")
    print(f"  封装已回填: {len(fp_done)}/{len(bom)}   OPN 已回填: {len(opn_done)}/{len(bom)}")
    if fp_done:
        print(f"     封装已定: {', '.join(sorted(fp_done))}")
    print(f"     封装待定 {len(fp_todo)} 条 (C-9 仍 FAIL; 需逐颗查官方 datasheet 后回填 PARTS 寄存器)")
    print("  按采购状态:")
    for k, v in sorted(by_status.items(), key=lambda x: -x[1]):
        print(f"     {k:<18} {v:>4}")
    print("  按板级归属:")
    for k, v in sorted(by_board.items(), key=lambda x: -x[1]):
        print(f"     {k:<18} {v:>4}")
    print()
    if fails:
        for f in fails:
            print(f"  ❌ {f}")
        print("=" * 72)
        return 1
    print("  ✅ 自检全过 (位号集合 / qty / 采购状态 / DNP 数 / 板级归属)")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
