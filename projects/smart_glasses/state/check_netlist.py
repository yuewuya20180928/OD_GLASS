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

REQUIRED_COLS = ["page", "net", "node1", "node2", "ref", "value", "type", "dnp", "evidence", "tbd", "note", "conn_id",
                 "board"]
LEGAL_DNP = {"必装", "DNP", "可选"}
LEGAL_EVIDENCE = {"[官方]", "[推算]", "[实测]", "[待原厂]", "[待JBD]", "[同Die参考-待官方确认]", "[0数据]"}
LEGAL_BOARD = {"CHG_BOARD", "MAIN_PCB", "HINGE"}
PAGES = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10"]


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
    chk("netlist 表头齐全 (13 列)", not miss, f"缺 {miss}" if miss else f"{len(cols)} 列")
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
    spec_imp = {c["id"]: (c.get("imp") or "") for c in spec["connections"]}
    bad_i = []
    for r in rows:
        cid = cell(r, "conn_id")
        want = spec_imp.get(cid, "")
        if not want or not cid.startswith("A-"):
            continue
        if cell(r, "type") != "NET":
            continue
        got = cell(r, "value")
        if got != want:
            bad_i.append(f"{cid}: 规格 {want!r} vs netlist {got!r}")
    a_nets = [r for r in rows if cell(r, "conn_id").startswith("A-") and cell(r, "type") == "NET"]
    chk(f"A 组阻抗逐条对照规格 ({len(a_nets)} 条 net)", not bad_i,
        f"不一致 {bad_i[:4]}" if bad_i else "全部一致")

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
    chk("10 页齐全 (P1-P10)", not miss_p, f"缺页 {miss_p}" if miss_p else f"实际 {sorted(got_pages)}")

    # 11) 同一 net 不得有多个输出驱动 (DRC 近似: 同 net 不同 ref 且方向冲突)
    # ★2026-10-28 修判据 (假阳性): 旧实现用 `"输出" in note or "→" in note` 扫全文 ——
    #   ⇒ note 正文里任何**说明性箭头** (如 "PG 低 → 栅极≈0 → P-MOS 导通") 都被当成信号方向,
    #     一行就误判成"输出驱动" ⇒ 改一行 note 就让门禁变红 (V1.9 Q_PG 改 P-MOS 时踩中)。
    # ★新判据: 只认 note **开头**的结构化方向声明 ("方向 A→B" / "输出: ..." / "A 输出 → B"),
    #   不认正文中间的箭头 ⇒ 注释怎么写都不会误报。
    def _is_output_driver(r) -> bool:
        n = (cell(r, "note") or "").strip()
        if not n:
            return False
        head = n[:24]          # 只看开头 (方向声明都写在开头)
        return ("方向" in head) or ("输出" in head)
    by_net: dict[str, list] = {}
    for r in rows:
        n = cell(r, "net")
        if n:
            by_net.setdefault(n, []).append(r)
    multi_out = []
    for n, rs in by_net.items():
        if n == "GND":
            continue   # GND 是单电气节点, "多驱动"判据不适用
        outs = [r for r in rs if _is_output_driver(r)]
        if len(outs) > 1:
            multi_out.append(n)
    chk("同一 net 不得有多个输出驱动", not multi_out, f"冲突 net {multi_out[:5]}" if multi_out else "")

    # 12) 每条 net 至少有一个位号或明确标注为纯网络
    noreref = [cell(r, "net") for r in rows if not cell(r, "ref")]
    chk("每行都有位号 (ref)", not noreref, f"{len(noreref)} 行无 ref" if noreref else "")

    # ---- ★V1.1 (2026-10-27) 新增判据: 板级归属 / 跨铰链 / 安全项 / 回归判据 ----

    # 13) 板级归属列存在且取值合法
    bad_b = sorted({cell(r, "board") for r in rows if cell(r, "board") not in LEGAL_BOARD})
    cnt_b: dict[str, int] = {}
    for r in rows:
        cnt_b[cell(r, "board")] = cnt_b.get(cell(r, "board"), 0) + 1
    chk("板级归属合法 (CHG_BOARD/MAIN_PCB/HINGE)", not bad_b,
        f"非法 {bad_b}" if bad_b else f"{cnt_b}")

    # 14) 跨铰链 4 个连接器必须标 HINGE
    hinge_conn = {"J_CHG", "CONN_USB", "CONN_CAM", "CONN_LIGHT"}
    bad_h = sorted({cell(r, "ref") for r in rows
                    if cell(r, "ref") in hinge_conn and cell(r, "board") != "HINGE"})
    chk("跨铰链 4 个连接器标 HINGE", not bad_h,
        f"错标 {bad_h}" if bad_h else "J_CHG / CONN_USB / CONN_CAM / CONN_LIGHT")

    # 15) SoC 侧节点必须在主 PCB (镜脚), 不许在充电板
    bad_s = sorted({cell(r, "ref") for r in rows
                    if "SoC[TBD-01]." in (cell(r, "node1") + cell(r, "node2"))
                    and cell(r, "board") != "MAIN_PCB"})
    chk("SoC 侧节点全在主 PCB (MAIN_PCB)", not bad_s, f"错标 {bad_s}" if bad_s else "")

    # 16) 充电链器件必须在充电板 (镜框) —— ★V1.2: 电池与电池保护移到镜脚, 所以拆成两半判
    chg_must = {"J_TYPE_C", "U_CHG", "D_ESD_TC", "FB_VBUS"}
    bad_c = sorted({cell(r, "ref") for r in rows
                    if cell(r, "ref") in chg_must and cell(r, "board") != "CHG_BOARD"})
    chk("充电板器件在充电板 (CHG_BOARD)", not bad_c, f"错标 {bad_c}" if bad_c else "")
    bat_must = {"BT_432243", "U_BATPROT", "Q1", "Q2"}
    bad_bat = sorted({cell(r, "ref") for r in rows
                      if cell(r, "ref") in bat_must and cell(r, "board") != "MAIN_PCB"})
    chk("电池与电池保护在主 PCB (MECH 体积硬约束)", not bad_bat,
        f"错标 {bad_bat}" if bad_bat else "BT/U_BATPROT/Q1/Q2 全在 MAIN_PCB")

    # 17) P9 跨铰链界面页存在且行数足够
    p9 = [r for r in rows if cell(r, "page") == "P9"]
    chk("P9 跨铰链界面页存在 (≥10 行)", len(p9) >= 10, f"{len(p9)} 行")

    # 18) 电池 NTC → BQ25896 TS 脚 (硬件停充, 安全项) 必须在图
    has_ntc = (any(cell(r, "ref") == "R_NTC_BAT" for r in rows)
               and any(cell(r, "net") == "TS_BAT" for r in rows))
    chk("电池 NTC → BQ25896 TS 脚 (硬件停充) 在图", has_ntc, "R_NTC_BAT + TS_BAT 已在图" if has_ntc else "缺 R_NTC_BAT / TS_BAT")

    # 19) 回归判据: USB 差分**必经跨铰链连接器** (V1 把铰链短接了: 网里没有 CONN_USB 的脚)
    #     ★V1.4 口径更新: V1.4 起跨铰链连接器的同一物理脚在两侧是同一节点 → 网名合并,
    #     所以"USB_D_P 网里同时有 CONN_USB 脚与 Type-C 脚"是**正确**的 (线确实穿铰链)。
    miss_usb = []
    for netn in ("USB_D_P", "USB_D_N"):
        nodelist = []
        for r in rows:
            if cell(r, "net") == netn:
                nodelist += [cell(r, "node1"), cell(r, "node2")]
        if not any(x.startswith("CONN_USB pin") for x in nodelist):
            miss_usb.append(netn)
    chk("USB 差分必经跨铰链连接器 (网里有 CONN_USB 脚)", not miss_usb,
        f"缺铰链连接器 {miss_usb}" if miss_usb else "USB_D_P/USB_D_N 都经 CONN_USB")

    # 19b) P10 充电板页必须有行 (数据来自 state/p10_rows.json; 未到就红 —— 诚实反映"还没画完")
    p10 = [r for r in rows if cell(r, "page") == "P10"]
    chk("P10 充电板页有内容 (≥30 行)", len(p10) >= 30, f"{len(p10)} 行")

    # 20) U_BRIDGE 定位统一 (DP1.4 TX → MIPI DSI TX 桥接) 且方案A 下 DNP
    ub = [r for r in rows if cell(r, "ref") == "U_BRIDGE"]
    bad_ub = [f"{cell(r,'page')}:{cell(r,'value')[:28]}" for r in ub
              if cell(r, "dnp") != "DNP" or "DSI" not in cell(r, "value")]
    chk("U_BRIDGE 定位统一 (DP→DSI 桥接) 且方案A 下 DNP", not bad_ub,
        f"{bad_ub}" if bad_ub else f"{len(ub)} 行 (P4+P6 同一颗)")

    # 21) U_TEMP 已定型为数字温度计 TMP117 (I2C 0x48)
    ut = [r for r in rows if cell(r, "ref") == "U_TEMP"]
    bad_t = [cell(r, "value")[:28] for r in ut if "TMP117" not in cell(r, "value")]
    chk("U_TEMP 已定型 TMP117 (I2C 0x48)", not bad_t, f"{bad_t}" if bad_t else f"{len(ut)} 行")

    # 22) 回归判据: SYS 轨不得跨铰链 (V1.2 起 SYS 在镜脚本地产生)
    sys_cross = [f"{cell(r,'net')}@{cell(r,'page')}" for r in rows
                 if cell(r, "net") in ("SYS", "SYS_PCB", "RAIL_SYS")
                 and "J_CHG" in (cell(r, "node1") + cell(r, "node2"))]
    chk("SYS 轨不得跨铰链 (电池在镜脚, SYS 本地产生)", not sys_cross,
        f"跨铰链 {sys_cross[:4]}" if sys_cross else "")

    # 23) ★跨铰链连接器: **声明 pin 数 == 网表实际引用 pin 数** (mech-lead ISS-085 F-1/F-2: 断链)
    hinge_pins = {}
    for ref in ("J_CHG", "CONN_USB", "CONN_CAM", "CONN_LIGHT"):
        decl = 0
        for r in rows:
            if cell(r, "ref") == ref:
                m = re.search(r"(\d+)\s*[×x]?\s*(\d*)\s*p\b", cell(r, "value"))
                if m:
                    decl = max(decl, int(m.group(1)) * (int(m.group(2)) if m.group(2) else 1))
        used = set()
        for r in rows:
            for node in (cell(r, "node1"), cell(r, "node2")):
                m = re.match(rf"^{re.escape(ref)} (.+)$", node)
                if m:
                    used.add(m.group(1))
        hinge_pins[ref] = (decl, len(used))
    bad_link = [f"{k}: 声明 {v[0]}p / 实际 {v[1]}p" for k, v in hinge_pins.items() if v[0] != v[1]]
    chk("跨铰链连接器无断链 (声明 pin 数 == 实际引用)", not bad_link,
        f"{bad_link}" if bad_link else "J_CHG10/CONN_USB4/CONN_CAM18/CONN_LIGHT21 全对")

    # 24) ★铰链区高度预算: 4 条链路触点区堆叠 ≤ 镜脚根部净高 37.0mm (mech-lead ISS-085 F-3)
    stack = sum(v[0] for v in hinge_pins.values()) * 0.5
    chk("铰链区堆叠高度 ≤ 镜脚根部净高 37.0mm", stack <= 37.0,
        f"{stack:.1f}mm (余 {37.0 - stack:.1f}mm)")

    # 23) 跨铰链大电流必须双 pin 并联 (J_CHG pin1/pin2 同网)
    bat_net = {cell(r, "net") for r in rows if cell(r, "ref") == "J_CHG"
               and "BAT_CHG" in (cell(r, "note") or "")}
    pins = {cell(r, "node1") for r in rows if cell(r, "net") in bat_net} | \
           {cell(r, "node2") for r in rows if cell(r, "net") in bat_net}
    need = {"J_CHG pin1", "J_CHG pin2"}
    chk("跨铰链充电电流双 pin 并联 (pin1/pin2)", need.issubset(pins),
        f"缺 {sorted(need - pins)}" if not need.issubset(pins) else "pin1/pin2 同网")

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
    print(f"  {'✅ 全过 — 原理图 V1.1 可进交叉评审' if not bad_rows else f'❌ {len(bad_rows)} 项不通过'}")
    print("=" * 72)
    return 1 if bad_rows else 0


if __name__ == "__main__":
    sys.exit(main())
