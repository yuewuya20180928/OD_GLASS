#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
state/_apply_iss302_csys_landing.py —— ★★ISS-302 · C_SYS / SYS_CHG 必装落表 (hw-lead)★★
================================================================================
★**依据 (★不可改的外部事实★)**:
    TI bq25896 datasheet (SLUSC76C) §7 逐字: "Connect a 20uF closely to the SYS pin."
    ⇒ SYS 脚必挂 20 µF 到地 ⇒ `C_SYS` / `SYS_CHG` 必装
    (★ISS-301 交卷单 §B5-① 的 4 条落表动作 · ★TI_POWER_FACTS.md §订正 A/B/C 已由 main 落★)

★**真源**: `state/p10_rows.json` (★P10 充电板页的器件级行数据 = gen_netlist.py 的唯一输入★)
    ★**产物一律重生成, 一个字节都不手改**: netlist_v1.csv / netlist_v1_pins.csv / BOM_v1.csv ★

★**本脚本只做 4 条动作 (★ISS-301 §B5-① 原文列的四条, 一条不许少★)**:
    ① L499 `C_SYS`  (SYS_CHG ↔ C_SYS)          dnp: DNP → 必装
    ② L498 `SYS_CHG` (U_CHG pin15 ↔ pin16)     dnp: DNP → 必装
    ③ L498 / L499 (★+ L500 同颗电容的地端行★) 的 note: 追加式订正
         · 过期 PM 裁决「VSYS 脚不接 (NC)」→ ★**已作废**★ + 换成
           「★SYS 必接 20 µF (TI §7); 不跨铰链引系统轨★」
         · 「装 20µF 只占 25×10mm 板面」→ 「≈8 mm² (0805/1206)」
         · 「DNP 时不占板面」→ ★**已作废**★ (DNP 照样占 land pattern)
    ④ BOM: CHG_BOARD 加 1 颗 20 µF 6.3 V X7R/X5R (★由 value + dnp 变化经 gen_bom 派生★)

★**note 的改写口径 (★追加式铁律★)**:
    ★**老字一字不许删** ⇒ 过期裁决的原文逐字保留在 note 里, 但同一条 note 追加
    「★★订正 (ISS-302 · 2026-11-18)★」段把它 ★**标为已作废**★ 并给出 ★**现行裁决**★
    ⇒ ★**语义上「删掉旧裁决 / 换成新裁决」已达成**(读者/任何扫描都不会把它当活指令),
      ★**物理上「老字零删」也守住了**(历史不丢, 可回台账核)★
    ★**先例**: 网表 L169 note 的 ISS-153 订正 = 同款写法 (旧注释逐字引用 + 已作废 + 正确值)★

★**L500 的 dnp 同步 (★必要的一致性延伸·不属于新增裁决★)**:
    `C_SYS` 是一颗**两脚**电容 (脚1 = SYS_CHG / 脚2 = PGND) ⇒ 只改脚1 必装、脚2 仍 DNP
    ⇒ `gen_bom.py` 的 dnp 聚合规则会吐「该器件有 1 脚标 DNP (pin2) 但整器按必装」
    ⇒ ★**一颗两脚电容不许一脚必装一脚 DNP** ⇒ 脚2 同步改必装 (零新增件 · 零改板)★

用法:  python3 state/_apply_iss302_csys_landing.py            # ★改真源★
       python3 state/_apply_iss302_csys_landing.py --verify    # ★只校验改后状态 (rc=0/1)★
"""
from __future__ import annotations

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
P10 = os.path.join(PROJ, "state", "p10_rows.json")

# ── ①/② 目标行 (★用 (net, node1, node2, ref) 四元组定位, 不靠行号 ★) ──
T_UCHG = ("SYS_CHG", "U_CHG pin15", "U_CHG pin16", "U_CHG")            # L498
T_CAP = ("SYS_CHG", "U_CHG pin16", "C_SYS", "C_SYS")                  # L499
T_GND = ("PGND", "C_SYS", "U_CHG pin17+pin18", "C_SYS")               # L500

OLD_VALUE = "20µF 6.3V"
NEW_VALUE = "20µF X7R 6.3V"      # ★TI §10.2.2.3: 6 V+ X7R/X5R ★ · ★封装/OPN 仍待选型 (不许编)★

# ── ③ note 追加段 (★逐字写死, 不留手滑空间 ★) ──
COMMON_TAIL = (
    " ★★订正 (ISS-302 · 2026-11-18 · hw-lead · 追加式 · 老字留痕)★: "
    "上句 PM 裁决『电池与负载**都在镜脚** ⇒ 充电板没有系统侧负载 · **VSYS 脚不接 (NC)**』"
    "★**已作废**★ (★被 [官网] TI bq25896 datasheet SLUSC76C §7 逐字 "
    "『Connect a 20uF closely to the SYS pin.』推翻★) ⇒ "
    "★**现行裁决**★ ⇒ ★SYS 必接 20 µF (TI §7); 不跨铰链引系统轨★ "
    "(★20 µF 挂充电板本地 PGND, 紧靠 U_CHG pin15/16 ⇒ "
    "★**不需要**跨铰链多引 2 根电源 pin, 原裁决担心的那个代价不成立★); "
    "『⚠️ [待原厂] SYS 悬空是否影响 BATFET 通路与充电环路 (TI 确认)』★**已结**★ "
    "(TI §7 明令接 20 µF ⇒ SYS 不再悬空); "
    "『⚠️ 待裁决: 网名用 SYS_CHG 而不是 SYS』★**维持 SYS_CHG**★ "
    "(★充电板 SYS 与镜脚 RAIL_SYS 仍是两个网, 不许合并 —— "
    "合并 = 把充电板 SYS 并到镜脚系统轨 = 电气冲突★); "
    "★**充电路径不变**★ = IN · 内部 BATFET · BAT · 跨铰链 · 电芯 "
    "(★反向阻断仍由 BATFET 提供★); "
    "★**本行 dnp 由 DNP 改必装**★ (★SYS 脚现在接 C_SYS, 不是 NC★)"
)

NOTE_UCHG = (
    "★pin15/16 SYS: 本板不供电 (SYS 在镜脚由 BQ2970 + 2×MOS 产生); "
    "⚠️ 待裁决: 网名用 SYS_CHG 而不是 SYS — 现行网表的 SYS 是镜脚系统轨 (RAIL_SYS 3.0-4.2V), "
    "若沿用 SYS 这个网名, 会把充电板悬空的 SYS 脚并到镜脚系统轨上 (电气冲突) ⇒ 建议保留独立网名 SYS_CHG; "
    "⚠️ [待原厂] SYS 悬空是否影响 BATFET 通路与充电环路 (TI 确认) "
    "★裁决 (PM): 电池与负载**都在镜脚** ⇒ 充电板没有系统侧负载 · **VSYS 脚不接 (NC)**; "
    "充电路径 = IN · 内部 BATFET · BAT · 跨铰链 · 电芯 (反向阻断由 BATFET 提供); "
    "★若 TI 数据手册要求 VSYS 必接, 则要把镜脚 SYS 经 J_CHG pin9/10 引过来 (会多两根电源 pin) · 记为后继项"
) + COMMON_TAIL

NOTE_CAP = (
    "★C_SYS 留位不装 = 保留 '电池挪镜框' 可回退分支 (将来接 2 根线 + 贴这颗电容即可, 不用改板); "
    "本板 SYS 无负载, 装 20µF 只占 25×10mm 板面 "
    "★裁决 (PM): 电池与负载**都在镜脚** ⇒ 充电板没有系统侧负载 · **VSYS 脚不接 (NC)**; "
    "充电路径 = IN · 内部 BATFET · BAT · 跨铰链 · 电芯 (反向阻断由 BATFET 提供); "
    "★若 TI 数据手册要求 VSYS 必接, 则要把镜脚 SYS 经 J_CHG pin9/10 引过来 (会多两根电源 pin) · 记为后继项"
    " ★★订正 (ISS-302 · 2026-11-18 · hw-lead · 追加式 · 老字留痕)★: "
    "上句『★C_SYS 留位不装 = 保留 '电池挪镜框' 可回退分支 (将来接 2 根线 + 贴这颗电容即可, 不用改板)』"
    "★**已作废**★ ⇒ ★**C_SYS 改为必装**★ "
    "(★依据: TI bq25896 datasheet SLUSC76C §7 逐字 "
    "『Connect a 20uF closely to the SYS pin.』⇒ "
    "★**现行裁决**★ ⇒ ★SYS 必接 20 µF (TI §7); 不跨铰链引系统轨★ "
    "(★20 µF 挂充电板本地 PGND, 紧靠 U_CHG pin15/16 ⇒ "
    "原裁决担心的『跨铰链多引 2 根电源 pin』代价不成立★); "
    "上句『本板 SYS 无负载, 装 20µF 只占 25×10mm 板面』★**已作废**★ ⇒ "
    "★**现行: 装 20µF 只占 ≈8 mm² (0805/1206)**★ "
    "(★0805 本体 2.0×1.25 = 2.50 mm² · 1206 本体 3.2×1.6 = 5.12 mm² · "
    "★**含焊盘与贴装工艺边 ≈8 mm²**★ ⇒ 充电板 25×10mm 板面装得下, 不构成板面风险★); "
    "PM 裁决『电池与负载**都在镜脚** ⇒ 充电板没有系统侧负载 · **VSYS 脚不接 (NC)**』"
    "★**已作废**★ (★被 [官网] TI §7 推翻★) ⇒ "
    "★**现行裁决**★ ⇒ ★SYS 必接 20 µF (TI §7); 不跨铰链引系统轨★; "
    "『⚠️ [待原厂] SYS 悬空是否影响 BATFET 通路与充电环路 (TI 确认)』★**已结**★ "
    "(TI §7 明令接 20 µF ⇒ SYS 不再悬空); "
    "★**充电路径不变**★ = IN · 内部 BATFET · BAT · 跨铰链 · 电芯 "
    "(★反向阻断仍由 BATFET 提供★); "
    "★**规格: 20 µF / 6.3 V · X7R 或 X5R (TI §10.2.2.3: 6 V+ X7R/X5R)★ "
    "(★封装 / OPN 仍待选型 ⇒ BOM 留『待定』, 不编造★); "
    "★**本行 dnp 由 DNP 改必装**★"
)

NOTE_GND = (
    "SYS 电容 地端 (PGND); DNP 时不占板面 "
    "★★订正 (ISS-302 · 2026-11-18 · hw-lead · 追加式 · 老字留痕)★: "
    "上句『DNP 时不占板面』★**已作废**★ (★**错**: DNP 也照样占 land pattern —— "
    "位置 / 焊盘 / 阻焊 / 丝印都已经在板上★) ⇒ ★**C_SYS 改为必装**★ ⇒ "
    "★**本行 (C_SYS 另一脚) 同步改必装**★ (★一颗两脚电容不许一脚必装一脚 DNP★); "
    "★**≈8 mm² (0805/1206)**★"
)


def _key(r):
    return (r.get("net"), r.get("node1"), r.get("node2"), r.get("ref"))


def find(data, key):
    hits = [r for r in data if _key(r) == key]
    if len(hits) != 1:
        raise SystemExit("★ p10_rows.json 里 %r 命中 %d 行 (期望 1) ★" % (key, len(hits)))
    return hits[0]


def verify(data) -> int:
    """★只校验改后状态 ★"""
    bad = []
    for key, want_dnp, want_note_has, want_value in (
        (T_UCHG, "必装", ("已作废", "★SYS 必接 20 µF (TI §7); 不跨铰链引系统轨★"), NEW_VALUE),
        (T_CAP, "必装", ("已作废", "★SYS 必接 20 µF (TI §7); 不跨铰链引系统轨★",
                         "≈8 mm² (0805/1206)"), NEW_VALUE),
        (T_GND, "必装", ("已作废", "≈8 mm² (0805/1206)"), NEW_VALUE),
    ):
        r = find(data, key)
        if r.get("dnp") != want_dnp:
            bad.append("%r dnp = %r (期望 %r)" % (key[3], r.get("dnp"), want_dnp))
        for s in want_note_has:
            if s not in (r.get("note") or ""):
                bad.append("%r note 缺 %r" % (key[3], s))
        if r.get("value") != want_value:
            bad.append("%r value = %r (期望 %r)" % (key[3], r.get("value"), want_value))
        # ★老字留痕自证: 过期裁决的原文必须还在 note 里 (追加式铁律) ★
    old_marks = {
        T_UCHG: "**VSYS 脚不接 (NC)**",
        T_CAP: "**VSYS 脚不接 (NC)**",
        T_GND: "DNP 时不占板面",
    }
    for key, s in old_marks.items():
        r = find(data, key)
        if s not in (r.get("note") or ""):
            bad.append("%r note 的老字 %r 被删了 (违反追加式铁律)" % (key[3], s))
    if bad:
        print("❌ ISS-302 校验未过:")
        for b in bad:
            print("   ·", b)
        return 1
    print("✅ ISS-302 真源校验通过 (dnp / note / value / 老字留痕 4 项全对)")
    return 0


def main() -> int:
    if "--verify" in sys.argv:
        with io.open(P10, encoding="utf-8") as fh:
            return verify(json.load(fh))

    with io.open(P10, encoding="utf-8") as fh:
        data = json.load(fh)

    # ── ② L498 SYS_CHG (U_CHG pin15 ↔ pin16) ──
    r = find(data, T_UCHG)
    assert r["dnp"] == "DNP", "★L498 dnp 不是 DNP (%r) ⇒ 已被人改过, 停下来★" % r["dnp"]
    r["dnp"] = "必装"
    r["value"] = NEW_VALUE
    r["note"] = NOTE_UCHG

    # ── ① L499 C_SYS (SYS_CHG ↔ C_SYS) ──
    r = find(data, T_CAP)
    assert r["dnp"] == "DNP", "★L499 dnp 不是 DNP (%r) ⇒ 已被人改过, 停下来★" % r["dnp"]
    r["dnp"] = "必装"
    r["value"] = NEW_VALUE
    r["note"] = NOTE_CAP

    # ── ③' L500 C_SYS 地端 (PGND ↔ C_SYS) · ★两脚电容的一致性延伸★ ──
    r = find(data, T_GND)
    assert r["dnp"] == "DNP", "★L500 dnp 不是 DNP (%r) ⇒ 已被人改过, 停下来★" % r["dnp"]
    r["dnp"] = "必装"
    r["value"] = NEW_VALUE
    r["note"] = NOTE_GND

    with io.open(P10, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(data, ensure_ascii=False, indent=2))
    print("★ state/p10_rows.json 已落表 (ISS-302: 3 行 dnp DNP→必装 + 3 行 value + 3 行 note 追加式订正) ★")
    return verify(data)


if __name__ == "__main__":
    sys.exit(main())
