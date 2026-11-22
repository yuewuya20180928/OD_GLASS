#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
充电板面积重算 (ISS-112 · R-F6 · 2026-10-29 · hw-lead)
================================================================================
★为什么有这个脚本:
  ISS-112 把 BQ25896 的封装从库里写的 "VQFN-16 3×3mm (RGT)" 改成官方真实的
  **WQFN (RTW) 24pin 4×4mm = 16 mm²** ⇒ **占板面积 +7 mm²** (9 → 16)。
  充电板 (MECH_BUDGET §1.3 M3) 只有 **25 × 10 mm = 250 mm²**, 且 C-13 判据要求
  器件占位率 ≤ 70% ⇒ **必须机械重算, 不许拍脑袋说"应该还行"**。

★口径声明 (与 MECH/cross_review_check.py C-13 对齐, 便于横向比):
  - 板外形: 25 × 10 mm = 250 mm²                [推算] MECH/MECH_BUDGET.md §1.3 M3
  - 扣 Type-C 座体: 8.9 × 7.4 = 65.86 mm²        [推算] MECH_BUDGET §1.3 M4
  - 可用面积 = 250 − 65.86 = **184.14 mm²**
  - 占位率判据 ≤ 70%                            [推算] MECH/cross_review_check.py C-13
  - **器件清单来源 = HW/netlist_v1.csv (board == CHG_BOARD)** —— 这是**投板真源**
    (生成物, 由 state/gen_netlist.py 产出), 不看文档里的手工镜像

★与 C-13 的差异 (本脚本比 C-13 多算了什么):
  ① U_CHG 16 mm² (C-13 写的 3.0×3.0=9mm² —— 那个封装不存在)
  ② C-13 把 **R_/C_ 默认按 0402 = 0.5 mm²** 算, 本脚本**逐颗给封装** (有的 0805/1206)
  ③ C-13 的 "未建模件" 里混进了 **网名伪 ref** (BAT_CHG / CHG_STAT / I2C_CHG_SCL …),
     它们不是器件, 本脚本按 type 过滤掉
  ④ ★**J_CHG 座体单独列** —— netlist 里它的 board=HINGE (跨铰链界面本体),
     但 **框侧那一半座体物理上就焊在充电板上** (J_CHG_SELECTION: FH12-10S 座体宽≈9.1mm 进深≈6.4mm)
     ⇒ 板面账必须单列, 否则充电板面积账少算 ~58 mm²

用法:
  python3 HW/calc_chg_board_area.py            # 打表 + 判定
  python3 HW/calc_chg_board_area.py --json     # 机器可读
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")
SPEC = os.path.join(PROJ, "HW", "CHARGE_BOARD_SPEC.md")

# ---------------------------------------------------------------- 板与判据
BOARD_L, BOARD_W = 25.0, 10.0                 # mm  [推算] MECH_BUDGET §1.3 M3
TYPEC_L, TYPEC_W = 8.9, 7.4                   # mm  [推算] MECH_BUDGET §1.3 M4
BOARD_AREA = BOARD_L * BOARD_W                # 250.0 mm²
TYPEC_AREA = TYPEC_L * TYPEC_W                # 65.86 mm²
USABLE = BOARD_AREA - TYPEC_AREA              # 184.14 mm²
DENS_LIMIT = 0.70                             # C-13 判据

# J_CHG 框侧座体 (焊在充电板上, 但 netlist board=HINGE ⇒ 单列)  [推算] J_CHG_SELECTION §3.2
J_CHG_SEAT = (9.1, 6.4)                       # 座体宽 × 进深 (FH12-10S, 由 28p 实测反推)
J_CHG_AREA = J_CHG_SEAT[0] * J_CHG_SEAT[1]    # 58.24 mm²

# ---------------------------------------------------------------- 逐颗封装表
#   格式: ref → (宽 mm, 长 mm, 证据)
#   ★没查到官方封装的用 [推算] 并写清依据; **不许编 KiCad 库名**
FP: "OrderedDict[str, tuple]" = OrderedDict([
    # ---- 唯一有官方依据的大件 ----
    ("U_CHG",      (4.00, 4.00, "[官方] WQFN (RTW) 24pin 4x4mm 16mm2 P0.5 (ti.com/lit/gpn/BQ25896 封装附录 4224801/A) · ISS-112 修正")),
    ("J_TYPE_C",   (8.90, 7.40, "[推算] 16p Type-C 座体 MECH_BUDGET M4")),
    # ---- 磁珠 / 电感 / TVS / ESD / LED ----
    ("L_CHG",      (3.50, 3.50, "[推算] 2.2uH Isat>=1.5A 功率电感 (1210/1212 级)")),
    ("FB_VBUS",    (1.60, 0.80, "[推算] pi 滤波磁珠 0805")),
    ("D_ESD_TC",   (1.60, 0.80, "[推算] ESD 阵列 0805")),
    ("D_TVS_VBUS", (3.20, 1.60, "[推算] 5V 单向 TVS 1206/SOD-123")),
    ("D_CHG_LED",  (1.60, 0.80, "[推算] 充电指示 LED 0805")),
    ("Q_CHG_LED",  (2.00, 1.25, "[推算] N-MOS SOT-23")),
    # ---- 电容 ----
    ("C_VBUS_BULK", (3.20, 1.60, "[推算] 100uF X7R 10V 1206")),
    ("C_VBUS_IN",   (3.20, 1.60, "[推算] 10uF 1206")),
    ("C_VBUS_OUT",  (3.20, 1.60, "[推算] 100uF 1206 (DNP 预留位)")),
    ("C_SYS",       (3.20, 1.60, "[推算] 20uF 1206 (DNP 不装)")),
    ("C_BAT",       (2.00, 1.25, "[推算] 10uF X7R 6.3V 0805")),
    ("C_PMID",      (2.00, 1.25, "[推算] 10uF X7R 25V 0805")),
    ("C_REGN",      (1.00, 0.50, "[推算] 4.7uF 0402")),
    ("C_VBUS_IC",   (1.00, 0.50, "[推算] 1uF 0402")),
    ("C_BST",       (1.00, 0.50, "[推算] 47nF 0402")),
])

# 默认封装 (逐颗给不出差别时的兜底)
R_DEFAULT = (1.00, 0.50, "[推算] 0402")
TP_DEFAULT = (1.30, 1.30, "[推算] 测试焊盘 dia 1.3mm")
CONN_DEFAULT = (0.0, 0.0, "[0数据] 未建模 (需查型号)")

# ★ISS-112 的对照口径: 库里旧写法 "VQFN-16 3x3mm (RGT)" = 9 mm² —— 该封装不存在
U_CHG_OLD = (3.00, 3.00, "[已作废] 库里旧写法 VQFN-16 3x3mm (RGT) —— 官方无此封装")

# ---------------------------------------------------------------- 腾挪方案 (3 条)
# ★每条都列出"具体动哪些件", 收益由下面的件表 **算出来**, 不许写"大概能省 XX"。
# ★三条 **不叠加** (T-2/T-3 都含 DNP 件); 单选一条即可。

# T-1 扩板: 充电板外形 25x10 -> 25x12 mm (板面 +50 mm²) —— 零 PCB 板费增量
T1_BOARD_DELTA = (25.0 * 12.0) - (25.0 * 10.0)      # +50.0 mm²

# T-2 双面贴: 下列件翻到底面 (其余必须留正面)
#   ★必须留正面的: U_CHG / L_CHG / C_VBUS_IC (datasheet "as close as possible") /
#     C_REGN ("placed close to the IC") / C_BST (SW<->BTST) / C_PMID (PMID->PGND 环路) /
#     C_BAT ("closely to the BAT pin") / D_ESD_TC (ESD 要贴连接器) / D_TVS_VBUS / FB_VBUS
T2_FLIP = [
    "R_TS_TOP", "R_ILIM", "R_VBUS_DET_1", "R_VBUS_DET_2", "R_PU_CHG_STAT",
    "R_CC1", "R_CC2", "R_PU_SCL", "R_PU_SDA", "R_PU_INT", "R_OTG", "R_CE",
    "R_STAR_PGND", "R_CHG_LED", "R_PU_STAT_L",        # 15 颗 0402
    "C_VBUS_IN", "C_VBUS_BULK",                        # 2 颗 1206 体电容 (远离 IC, 可翻)
]

# T-3 纯删件 (零结构改版): 删/改下列件
#   C_SYS       —— 规格已判"本板不用" (PM 裁决: VSYS 脚 NC)
#   C_VBUS_OUT  —— netlist 已标 DNP 预留位
#   R_PU_INT    —— netlist 已标 DNP
#   R_PU_SCL/SDA —— CHARGE_BOARD_SPEC §2.2 明写"跨铰链版本不装 (上拉在主板侧)" · netlist 标必装 ⚠ 不一致
#   R_STAR_PGND —— 规格 §2.2 明写"删掉此位并把 PGND 全并到 GND (铜皮短接)"
#   充电灯链     —— D_CHG_LED+Q_CHG_LED+R_CHG_LED+R_PU_STAT_L 整链移到镜脚侧
#                    (CHG_STAT 本来就跨铰链到镜脚 SoC GPIO ⇒ 镜脚侧可直接点灯)
T3_DELETE = ["C_SYS", "C_VBUS_OUT", "R_PU_INT", "R_PU_SCL", "R_PU_SDA", "R_STAR_PGND"]
T3_MOVE_LED = ["D_CHG_LED", "Q_CHG_LED", "R_CHG_LED", "R_PU_STAT_L"]

TENGNONG: list = []      # 由 main() 填 (需要件表面积)


def t3_refs_in_table(rows: list) -> list:
    """T-3 里"删除"的件: 只算真正会从板上消失的 (R_STAR_PGND 改铜皮 = 焊盘还在, 净省很小)."""
    have = {r["ref"] for r in rows}
    return [r for r in (T3_DELETE + T3_MOVE_LED) if r in have]


def chg_parts() -> "OrderedDict[str, dict]":
    """从网表真源取 board==CHG_BOARD 的位号 (net == ref 的伪 ref 过滤掉)."""
    parts: "OrderedDict[str, dict]" = OrderedDict()
    with open(NETLIST, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if (r.get("board") or "") != "CHG_BOARD":
                continue
            ref = (r.get("ref") or "").strip()
            if not ref:
                continue
            typ = (r.get("type") or "").strip()
            # 网名伪 ref (BAT_CHG / CHG_STAT / I2C_CHG_SCL ...) 不是器件
            if typ in ("NET", "RAIL"):
                continue
            if ref not in parts:
                parts[ref] = {"type": typ, "value": r.get("value", ""),
                              "dnp": r.get("dnp", ""), "page": r.get("page", "")}
            if r.get("dnp") == "必装":
                parts[ref]["dnp"] = "必装"
    return parts


def fp_of(ref: str, typ: str) -> tuple:
    if ref in FP:
        return FP[ref]
    if typ == "R":
        return R_DEFAULT
    if typ == "C":
        return C_DEFAULT
    if typ == "TP":
        return TP_DEFAULT
    if typ == "CONN" or ref.startswith("J_"):
        return CONN_DEFAULT
    return (0.0, 0.0, "[0数据] 未建模")


C_DEFAULT = (1.00, 0.50, "[推算] 0402 (未逐颗区分)")


# ---------------------------------------------------------------- C-13 口径复刻
# ★为什么要复刻 MECH/cross_review_check.py C-13 的模型:
#   只有在 **同一个模型** 下把 U_CHG 从 9mm² 改成 16mm², Δ 才是干净的 (+7mm²)。
#   C-13 的模型比本脚本粗 (见下), 所以要 **两个口径都报**, 不许只报好看的那个。
C13_FOOTPRINT = {          # [推算] 逐字复刻 MECH/cross_review_check.py CHG_FOOTPRINT
    "J_TYPE_C": 8.9 * 7.4,
    "U_CHG": 3.0 * 3.0,     # ★ISS-112 修正点: 应为 4.0*4.0 = 16
    "L_CHG": 3.5 * 3.5,
    "FB_VBUS": 1.6 * 0.8,
    "D_ESD_TC": 1.6 * 0.8,
    "D_ESD_CHG": 1.6 * 0.8,
    "R_ILIM": 1.0 * 0.5,
    "C_VBUS_BULK": 3.2 * 1.6,
    "C_PMID": 2.0 * 1.25,
    "C_VBUS_IN": 1.6 * 0.8,
    "C_VBUS_IC": 1.0 * 0.5,
    "C_REGN": 1.0 * 0.5,
    "C_BST": 1.0 * 0.5,
    "TP_TS": 1.3,
    "TP_VBUS": 1.3,
}
C13_DEFAULT_RC = 1.0 * 0.5  # 0402


def c13_model(u_chg_area: float) -> dict:
    """复刻 C-13: 从 CHARGE_BOARD_SPEC.md 的 P10 csv 块取位号, 按 C-13 的表算。"""
    txt = open(SPEC, encoding="utf-8").read()
    blk = re.search(r"```csv\n(.*?)```", txt, re.S)
    refs, rows = set(), []
    if blk:
        for line in blk.group(1).splitlines():
            if line.startswith("P10,"):
                parts = line.split(",")
                if len(parts) > 4:
                    refs.add(parts[4].strip().strip('"'))
    area, unmodelled = 0.0, []
    table = dict(C13_FOOTPRINT)
    table["U_CHG"] = u_chg_area
    for ref in refs:
        if ref in table:
            area += table[ref]
        elif re.match(r"^(R_|C_)", ref):
            area += C13_DEFAULT_RC
        else:
            unmodelled.append(ref)
    return {"n_refs": len(refs), "area": round(area, 2), "unmodelled": sorted(unmodelled)}


def area_model(parts: "OrderedDict[str, dict]", u_chg_fp: tuple) -> dict:
    rows = []
    total = 0.0
    unmodelled = []
    for ref, p in parts.items():
        fp = u_chg_fp if ref == "U_CHG" else fp_of(ref, p["type"])
        w, h, ev = fp
        a = w * h
        if a == 0.0:
            unmodelled.append(ref)
        rows.append({"ref": ref, "type": p["type"], "dnp": p["dnp"],
                     "fp": f"{w:.2f}x{h:.2f}", "area": round(a, 2), "ev": ev})
        total += a
    return {"rows": rows, "total": round(total, 2), "unmodelled": unmodelled}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    parts = chg_parts()
    old = area_model(parts, U_CHG_OLD)
    new = area_model(parts, FP["U_CHG"])
    c13_old = c13_model(9.0)
    c13_new = c13_model(16.0)

    delta = round(new["total"] - old["total"], 2)
    res = {
        "board_mm": [BOARD_L, BOARD_W],
        "board_area": BOARD_AREA,
        "typec_area": round(TYPEC_AREA, 2),
        "usable": round(USABLE, 2),
        "n_parts": len(parts),
        "area_old_u_chg_9mm2": old["total"],
        "area_new_u_chg_16mm2": new["total"],
        "delta_mm2": delta,
        "dens_vs_board_old": round(old["total"] / BOARD_AREA, 4),
        "dens_vs_board_new": round(new["total"] / BOARD_AREA, 4),
        "dens_vs_usable_old": round(old["total"] / USABLE, 4),
        "dens_vs_usable_new": round(new["total"] / USABLE, 4),
        "limit": DENS_LIMIT,
        "pass_new": new["total"] / USABLE <= DENS_LIMIT,
        "pass_old": old["total"] / USABLE <= DENS_LIMIT,
        "j_chg_seat_area": round(J_CHG_AREA, 2),
        "area_new_plus_jchg": round(new["total"] + J_CHG_AREA, 2),
        "dens_vs_usable_plus_jchg": round((new["total"] + J_CHG_AREA) / USABLE, 4),
        "unmodelled_new": new["unmodelled"],
        "rows_new": new["rows"],
        "c13_old": c13_old,
        "c13_new": c13_new,
    }

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    print("=" * 74)
    print("  充电板面积重算 · ISS-112 (BQ25896 VQFN-16 3x3 -> WQFN RTW 24 4x4mm)")
    print("=" * 74)
    print(f"  板外形            : {BOARD_L:.0f} x {BOARD_W:.0f} mm = {BOARD_AREA:.1f} mm2   [推算] MECH_BUDGET M3")
    print(f"  扣 Type-C 座体    : {TYPEC_L} x {TYPEC_W} = {TYPEC_AREA:.2f} mm2   [推算] MECH_BUDGET M4")
    print(f"  可用面积          : {USABLE:.2f} mm2")
    print(f"  器件位号 (CHG_BOARD): {len(parts)} 个  (来源 HW/netlist_v1.csv, board==CHG_BOARD)")
    print()
    print(f"  {'位号':<14}{'type':<6}{'装':<5}{'封装 mm':<14}{'mm2':>8}  证据")
    print("  " + "-" * 70)
    for r in sorted(new["rows"], key=lambda x: -x["area"]):
        print(f"  {r['ref']:<14}{r['type']:<6}{r['dnp']:<5}{r['fp']:<14}{r['area']:>8.2f}  {r['ev'][:34]}")
    print("  " + "-" * 70)
    print(f"  {'合计':<14}{'':<6}{'':<5}{'':<14}{new['total']:>8.2f}")
    print()
    print("  ── 口径对比 ──")
    print(f"  旧 (U_CHG 9 mm², 该封装不存在) : {old['total']:>7.2f} mm²   占板 {old['total']/BOARD_AREA:>6.1%}   占可用 {old['total']/USABLE:>6.1%}")
    print(f"  新 (U_CHG 16 mm², 官方真实)     : {new['total']:>7.2f} mm²   占板 {new['total']/BOARD_AREA:>6.1%}   占可用 {new['total']/USABLE:>6.1%}")
    print(f"  Δ = +{delta:.2f} mm²   占可用 +{delta/USABLE:.1%}")
    print(f"  判据 (C-13): 占可用 ≤ {DENS_LIMIT:.0%}  ⇒  旧 {'PASS' if res['pass_old'] else 'FAIL'} / 新 {'PASS' if res['pass_new'] else 'FAIL'}")
    print()
    print("  ── ★同一模型下的 Δ 复刻 (MECH/cross_review_check.py C-13 口径) ──")
    print(f"  C-13 原样 (U_CHG 9 mm²)  : {c13_old['area']:>7.2f} mm²  ({c13_old['n_refs']} 个 P10 位号)  占可用 {c13_old['area']/USABLE:>6.1%}  ⇒ {'PASS' if c13_old['area']/USABLE<=DENS_LIMIT else 'FAIL'}")
    print(f"  C-13 修正 (U_CHG 16 mm²) : {c13_new['area']:>7.2f} mm²  ({c13_new['n_refs']} 个 P10 位号)  占可用 {c13_new['area']/USABLE:>6.1%}  ⇒ {'PASS' if c13_new['area']/USABLE<=DENS_LIMIT else 'FAIL'}")
    print(f"  Δ = +{c13_new['area']-c13_old['area']:.2f} mm²  (同模型, 干净可比)")
    print(f"  ★C-13 口径的未建模件 ({len(c13_old['unmodelled'])} 个, 其中多数是网名伪 ref 不是器件):")
    print(f"     {', '.join(c13_old['unmodelled'])}")
    print()
    print("  ── ★J_CHG 框侧座体 (单列, 不在上面那张表里) ──")
    print(f"  J_CHG (FH12-10S 座体) 宽 {J_CHG_SEAT[0]} x 进深 {J_CHG_SEAT[1]} = {J_CHG_AREA:.2f} mm2   [推算] J_CHG_SELECTION §3.2")
    print(f"  netlist 里它的 board=HINGE ⇒ C-13 没算它; 但框侧那一半座体物理上焊在充电板上")
    print(f"  含座体后: {res['area_new_plus_jchg']:.2f} mm²  占可用 {res['dens_vs_usable_plus_jchg']:.1%}  ⇒ {'PASS' if res['dens_vs_usable_plus_jchg']<=DENS_LIMIT else 'FAIL (超判据)'}")
    if new["unmodelled"]:
        print(f"  ★未建模件 (占位面积未知): {new['unmodelled']}")
    print()
    print("  ── 腾挪方案收益 (目标: 补足缺口) ──")
    amap = {r["ref"]: r["area"] for r in new["rows"]}
    gap_c13 = new["total"] - DENS_LIMIT * USABLE
    phys_free = USABLE - J_CHG_AREA
    gap_phys = new["total"] - phys_free
    t2_save = sum(amap.get(r, 0.0) for r in T2_FLIP)
    t3_save = sum(amap.get(r, 0.0) for r in t3_refs_in_table(new["rows"]))
    print(f"  目标A (C-13 判据口径): 需 ≤ {DENS_LIMIT*USABLE:.2f} mm²  ⇒ 缺口 {gap_c13:.2f} mm²")
    print(f"  目标B (物理口径, 扣 J_CHG 座体): 可用只剩 {phys_free:.2f} mm²  ⇒ 缺口 {gap_phys:.2f} mm²")
    print(f"  {'方案':<44}{'腾出mm²':>9}  物理口径结果")
    print(f"  {'T-1 扩板 25x10 -> 25x12 (板面增量)':<44}{T1_BOARD_DELTA:>9.2f}  "
          f"器件 {new['total']:.2f} / 可用 {phys_free+T1_BOARD_DELTA:.2f} = {new['total']/(phys_free+T1_BOARD_DELTA):.1%} "
          f"{'✅ 装得下' if new['total']<=phys_free+T1_BOARD_DELTA else '❌'}")
    print(f"  {'T-2 双面贴 (16 电阻+2 体电容翻底) + 删 DNP':<44}{t2_save:>9.2f}  "
          f"器件 {new['total']-t2_save:.2f} / {phys_free:.2f} = {(new['total']-t2_save)/phys_free:.1%} "
          f"{'✅ 装得下' if new['total']-t2_save<=phys_free else '❌ 仍不够'}")
    print(f"  {'T-3 纯删件 (DNP+铜皮短接+充电灯移镜脚)':<44}{t3_save:>9.2f}  "
          f"器件 {new['total']-t3_save:.2f} / {phys_free:.2f} = {(new['total']-t3_save)/phys_free:.1%} "
          f"{'✅ 装得下' if new['total']-t3_save<=phys_free else '❌ 仍不够'}")
    print(f"  ★T-2/T-3 都含 DNP 件 ⇒ **两条不叠加** (单选一条即可); T-2 与 T-3 叠加收益更大")
    comb = sorted(set(T2_FLIP) | set(t3_refs_in_table(new["rows"])))
    c_save = sum(amap.get(r, 0.0) for r in comb)
    print(f"  {'T-2+T-3 合并 (双面贴 + 全删件)':<44}{c_save:>9.2f}  "
          f"器件 {new['total']-c_save:.2f} / {phys_free:.2f} = {(new['total']-c_save)/phys_free:.1%} "
          f"{'✅ 装得下' if new['total']-c_save<=phys_free else '❌ 仍不够'}")
    print(f"  ★T-1 不删件, 只改外形 ⇒ 与 T-2/T-3 **可叠加**")
    print(f"  ★注: 以上腾挪收益都是 **正面 land 面积**, 不含走线/间距/平面不可用区"
          f" ⇒ 物理上还要再留 10-20% ⇒ **建议按 T-1 或 T-2+T-3 组合走**")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
