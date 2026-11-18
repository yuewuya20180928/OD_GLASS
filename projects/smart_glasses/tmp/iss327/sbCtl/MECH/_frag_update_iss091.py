#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-091 第2轮: 把铰链充电电流核算的产出登记进 mech-lead 分片 (原子写, 走 frag_write 模块 API)"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment  # noqa: E402

ARTIFACTS = [
    dict(path="MECH/HINGE_POWER_CALC.md", kind="calc", version="v1.0", updated_at="2026-10-28",
         summary="ISS-091 第2轮 跨铰链充电电流 1.0A 载流/压降/发热核算: 铰链段 R_path 37-111mΩ -> ΔV 37-111mV @1.0A (保守110.8mV), "
                "发热 15-127mW -> 皮肤 +0.8~+6.4C (MECH_BUDGET §2.3 口径 k_eff=50.13K/W); 对 SYS 的影响 = 上限被压低30-120mV, 下限3.5V不受影响; "
                "★R_ILIM 档位表 300/390/470/680Ω ↔ IINMAX ↔ ICHG ↔ 压降 ↔ 发热 (12行 min/typ/max, 皮肤 47.1/42.1/39.9/37.3C); "
                "机械: J_CHG 1x10p@0.5 触点区5.0mm/FPC宽>=6.0mm, 承力余量22-75x, 加宽高度影响0.00mm; 自发现8条问题 (M-1 加厚铜箔救不了热/M-2 铜厚与弯折寿命冲突/M-3 电芯内阻是主项且贴皮/M-4 TS参考地被1A回流抬高0.44-0.99C/M-5 地平面分流回流/M-6 触点额定才是瓶颈/M-7 压降方向与不要补偿/M-8 BQ25896提前判满)"),
    dict(path="MECH/hinge_power_calc.py", kind="tool", version="v1.0", updated_at="2026-10-28",
         summary="铰链充电电流核算脚本 (rc=0): 算 FPC 铜箔电阻 rho*L/(w*t) / 铰链段总压降发热 (口径A保守+口径B乐观双口径) / "
                "R_ILIM 4档 x min-typ-max 全表 / '加厚铜箔能否替代降R_ILIM档' 对比表 / 机械 (EI 弯折力矩 触点电流密度 堆叠高度影响) / "
                "SYS 与电芯端电压影响 + TS 参考地偏移; --json 另存 MECH/hinge_power_calc.json"),
]

CLAIMS = [
    ("mech_hinge_chg_path_resistance_mohm", "37-111",
     "铰链段总电阻 (框侧界面 + FPC31mm载流铜箔 + 脚侧界面, 双pin并联)。口径A保守110.8 / 口径B乐观37.0 mΩ [推算]",
     "MECH/HINGE_POWER_CALC.md#2.2"),
    ("mech_hinge_chg_drop_mv_at_1a", "37-111",
     "@1.0A 铰链段压降 (mV), 保守基准 110.8mV; 接触电阻 5-30mΩ/pin/界面 [0数据] [推算]",
     "MECH/HINGE_POWER_CALC.md#2.2"),
    ("mech_hinge_chg_power_mw_at_1a", "15-127",
     "@1.0A 铰链段发热 (mW), 对应皮肤侧 +0.8~+6.4C [推算]",
     "MECH/HINGE_POWER_CALC.md#3.2"),
    ("mech_hinge_chg_skin_rise_c_at_1a", "0.8-6.4",
     "铰链段发热引起的贴皮肤处温度增量 (C), 用 MECH_BUDGET §2.3 口径 k_eff=50.13 K/W, 基准35C [推算]",
     "MECH/HINGE_POWER_CALC.md#3.2"),
    ("mech_rilim_recommended_ohm", "470",
     "建议值(非拍板): 换料不换板 (ILIM脚稳在0.8V, P=0.8^2/470=1.36mW, 0402足够); ICHG max 0.682A / 单pin 0.341A / 皮肤39.9C / 充电~35min [推算]",
     "MECH/HINGE_POWER_CALC.md#4.3"),
    ("mech_rilim_charge_skin_temp_c", "300:47.1/390:42.1/470:39.9/680:37.3",
     "各档 ICHG=max 的贴皮肤侧温度 (C), 口径A保守 (回流走GND双pin铜箔, 接触30mΩ/界面, FPC 1oz/0.3mm/31mm, R_cell=0.10Ω); 300Ω档超 ISO13732-1 的 43C 红线 [推算]",
     "MECH/HINGE_POWER_CALC.md#4.1"),
    ("mech_rilim_charging_minutes", "300:22/390:29/470:35/680:51",
     "各档满充时间 (min, 仅CC段估算, 未计CV拐点, 实际再加10-20%) [推算]",
     "MECH/HINGE_POWER_CALC.md#4"),
    ("mech_j_chg_min_contact_rating_a", "0.5",
     "J_CHG 单触点最小额定电流 (A) = 选型硬判据; 0.5mm pitch FPC ZIF 座典型 0.3-0.5A [0数据 型号未选]; 若只有0.3A型号则 R_ILIM 只能选680Ω",
     "MECH/HINGE_POWER_CALC.md#6-M6"),
    ("mech_fpc_cu_thickness_bend_segment_oz", "1",
     "弯折段铜厚必须保持 1oz (35um, 应变0.583%); 2oz 应变1.167% -> 疲劳寿命按幂律m=4~6 降到1/16~1/32 [推算]",
     "MECH/HINGE_POWER_CALC.md#6-M2"),
    ("mech_fpc_cu_thickness_fixed_segment_oz", "2",
     "固定段铜厚建议 2oz (加厚减压降); 成品厚 0.20->0.25mm, 铰链区径向 +0.16~0.20mm (余量1.00->0.80mm), 垂直堆叠影响 0.00mm [推算]",
     "MECH/HINGE_POWER_CALC.md#5.3"),
    ("mech_fpc_current_trace_width_mm", "0.4",
     "载流铜箔建议加宽到 0.4mm (0.3mm为0.5mm pitch标准导体); 需厂商确认最小间隙0.1mm [0数据]; 高度影响0.00mm [推算]",
     "MECH/HINGE_POWER_CALC.md#5.3"),
    ("mech_hinge_stack_vertical_mm", "27.0",
     "铰链区垂直堆叠 (mm); 本轮全部建议对其影响 = 0.00mm (J_CHG是既有FPC链路端头不是新增层). 注意 DECISIONS.md 记的是26.5, 两值待PM统一",
     "MECH/HINGE_POWER_CALC.md#5.3"),
    ("mech_chg_cell_ir_ohm", "0.10",
     "电芯内阻 (Ω), 区间0.08-0.15 [0数据 丰江432243规格书未查到]; 充电发热主项 = I^2*R (1.069A时114mW, 电芯直接贴镜脚皮肤侧) [推算]",
     "MECH/HINGE_POWER_CALC.md#6-M3"),
    ("mech_ts_ref_offset_c", "0.44-0.99",
     "TS跨铰链参考地被1A回流抬高14-32mV 造成的等效温度偏差 (C), TS斜率32.4mV/C [推算]; 减害方案=pin9/pin10改NTC专用回流 (待PM裁决)",
     "MECH/HINGE_POWER_CALC.md#6-M4"),
    ("mech_bat_det_location", "temple_local",
     "SoC的BAT_DET在镜脚本地(不在J_CHG 10p pin map) -> 读到真实电芯电压, 不会被铰链压降虚高 [推算]",
     "MECH/HINGE_POWER_CALC.md#2.3"),
]

NEEDS = [
    dict(key="iss091_rilim_decision", to="main", since="2026-10-28", due="2026-10-30", waiting_on="boss",
         item="R_ILIM 档位裁决: 我建议 300->470Ω (换料不换板, 皮肤 47.1C->39.9C, 充电 22->35min)。300Ω 档在'边戴边充'下贴皮肤侧 47.1C "
              "超 ISO13732-1 的 43C 红线; 390Ω 为42.1C(逼近红线)。请老板/PM 拍板 300/390/470/680。依据 MECH/HINGE_POWER_CALC.md §4"),
    dict(key="iss091_worn_while_charging", to="main", since="2026-10-28", due="2026-10-30", waiting_on="boss",
         item="'边戴边充'产品行为是否保留: 这直接等价于 'R_ILIM <= 470Ω' (因为充电发热主项是电芯内阻 I^2R 而非铰链段, "
              "电芯 3M背胶直接贴镜脚皮肤侧, 300Ω档 47.1C / 乐观口径也 44.2C)。若维持'充电时摘下'(现有结论)则 390~470Ω 皆可"),
    dict(key="iss091_contact_res_def", to="hw-lead", since="2026-10-28", due="2026-10-30",
         item="接触电阻 5-30mΩ/pin 的口径澄清: 是【单个连接器界面】还是【整条 pin 路径含两端界面]? 我按保守的单界面算(路径内2界面=10-60mΩ/pin), "
              "口径B(整条路径)下压降 111->40-87mV, 两个口径结论方向一致(300Ω FAIL / 470Ω PASS)。需查连接器厂商规格书原文"),
    dict(key="iss091_jchg_contact_rating", to="hw-lead", since="2026-10-28", due="2026-10-31",
         item="J_CHG 1x10p@0.5mm 具体型号 + 【单触点额定电流]: 0.5mm pitch FPC ZIF 座典型0.3-0.5A [0数据]。300Ω档 ICHG max 1.069A -> "
              "单pin 0.534A 已超0.5A; 若只能拿到0.3A型号, 双pin并联仍不够, R_ILIM 只能选680Ω。请在选型时给出单触点额定 >=0.5A 的型号"),
    dict(key="iss091_fpc_vendor_caps", to="hw-lead", since="2026-10-28", due="2026-11-02",
         item="FPC 厂商三项能力: (1)【分段铜厚】固定段2oz/弯折段1oz (弯折段加厚->应变翻倍->疲劳寿命降到1/16~1/32) "
              "(2)载流铜箔加宽到0.4mm (需最小间隙0.1mm) (3)L2/L3地在pin1-pin4区域做 keep-out 挖空 (强制1A走外层加宽铜箔, 否则阻抗与温升都不可控)。"
              "三项都零成本但必须写进FPC加工图, 请选型时向厂商确认 [0数据]"),
    dict(key="iss091_cell_ir", to="main", since="2026-10-28", due="2026-10-31", waiting_on="vendor",
         item="丰江 432243 软包锂电的【内阻]: 现按 0.10Ω (区间0.08-0.15) 算。充电发热主项=I^2*R, 该值直接决定'边戴边充'的皮肤温度。"
              "敏感性: 0.08Ω->470Ω档39.5C / 0.15Ω->40.7C, 均<43C, 结论稳健。请代向电池供应商索取规格书 (外发经PM)"),
    dict(key="iss091_stack_value_conflict", to="main", since="2026-10-28", due="2026-10-29",
         item="铰链区垂直堆叠数值冲突: 任务锚点写 27.0mm (镜脚根部净高37.0, 余10.0), DECISIONS.md 2026-10-27 写 26.5mm (余10.5)。"
              "我按 27.0 保守取; 本轮全部建议的高度影响=0.00mm, 两个取值都不影响结论, 但请统一以免后续引用出错"),
    dict(key="iss091_pin9_10_ntc_return", to="main", since="2026-10-28", due="2026-11-02",
         item="裁决: J_CHG 的 pin9/pin10 (预留) 是否改一个作【NTC 专用回流】? TS (pin8) 跨铰链, 而NTC在镜脚、其回流必须经铰链GND(pin3/pin4), "
              "1A回流在铰链GND上产生14-32mV偏移 = 等效0.44-0.99C温度偏差 (TS斜率32.4mV/C), 而TS是BQ25896的停充安全门限。"
              "改成NTC专用回流后偏差<0.01C。DECISIONS 已定'充电IC的I2C不跨铰链' -> 占用预留脚不冲突"),
    dict(key="iss091_chargeboard_bat_note", to="hw-lead", since="2026-10-28", due="2026-10-30",
         item="充电板规格加一条注记: BQ25896 的 BAT 监测点在【框侧】, 跨铰链压降(37-111mV)使真实电芯欠充 ΔV -> BQ25896 会提前判满并终止。"
              "方向是欠充(永不过充), 容量损失<1%, 建议【不做补偿】(上调终止电压会把真实电芯推过4.2V, 过充方向危险)。"
              "请在 HW/CHARGE_BOARD_SPEC.md §2.x 落这条注记 (我不改 HW/)"),
]

BLOCKERS = [
    dict(id="MECH-B8", severity="high", waiting_since="2026-10-28",
         desc="ISS-091: 跨铰链充电电流核算已交 (MECH/HINGE_POWER_CALC.md), 但两个前置未裁: "
              "(1) J_CHG 单触点额定电流未知 [0数据] -> 直接锁死 R_ILIM 档位 (若只有0.3A型号则只能选680Ω); "
              "(2) FPC 厂商三项能力未知 [0数据] (分段铜厚/0.4mm加宽/地平面keep-out) -> 固定段能否加厚不确定, "
              "影响压降 111->65mV 区间。未裁之前: R_ILIM 最终档位定不了、FPC 加工图定不了、铰链段 FPC 不能下单。",
         needs_from=["main", "hw-lead"]),
]

STATUS = dict(
    phase="P2(ISS-091 第2轮 跨铰链充电电流 1.0A 载流/压降/发热核算已交; 待 R_ILIM 档位裁决 + J_CHG 型号 + FPC 厂商能力)",
    progress_pct=84,
    health="yellow",
    summary="第7轮 ISS-091 (第2轮, 上一轮随网关重启1012死亡0产出, 本轮重派): 新增 MECH/HINGE_POWER_CALC.md + "
            "MECH/hinge_power_calc.py (rc=0, 全部数字可复现, --json 另存) + HANDOFF/2026-10-27_mech-lead_铰链充电电流核算.md "
            "(B1-B6六块齐)。核心结论: (1) 铰链段 R_path 37-111mΩ -> ΔV 37-111mV @1.0A (保守110.8mV), 发热15-127mW -> "
            "皮肤+0.8~+6.4C (MECH_BUDGET §2.3 口径); (2) SYS 不过铰链 -> 下限3.5V不受影响, 只是上限被压低30-120mV, 方向是欠充, "
            "建议不补偿; (3) ★R_ILIM档位表 300/390/470/680Ω -> 皮肤 47.1/42.1/39.9/37.3C, 300Ω档超43C红线, 建议470Ω(换料不换板); "
            "(4) ★自发现8条: 加厚铜箔救不了(300Ω+2oz仍45.2C FAIL)/铜厚与弯折寿命冲突(弯折段必须留1oz)/"
            "电芯内阻才是充电发热主项(114mW, 电芯直接贴皮肤侧)/TS参考地被1A回流抬高0.44-0.99C/FPC地平面会分流回流(需keep-out)/"
            "触点额定0.5A才是真瓶颈/压降方向不要补偿/BQ25896会提前判满; (5) 机械: J_CHG 触点区5.0mm, FPC宽>=6.0mm, "
            "承力余量22-75x, 本轮所有建议对垂直堆叠影响=0.00mm (径向+0.16~0.20mm, 余量1.00->0.80mm); "
            "新增9条 needs_from + 新增 blocker MECH-B8 + 新增 interface_claims 15条。★ 本单只交方案与核算: 实物类[实测]=0, "
            "接触电阻/座体尺寸/触点额定/电芯内阻/FPC厂商能力/疲劳幂律m 全部标[0数据]并给可查证清单; 未联系任何供应商(外发经PM)。",
)


def main():
    def mutate(d):
        d.setdefault("artifacts", [])
        existing_paths = {a.get("path") for a in d["artifacts"]}
        for a in ARTIFACTS:
            if a["path"] not in existing_paths:
                d["artifacts"].append(a)
        d.setdefault("interface_claims", [])
        existing_keys = {c.get("key") for c in d["interface_claims"]}
        for k, v, n, r in CLAIMS:
            if k not in existing_keys:
                d["interface_claims"].append(dict(key=k, value=v, note=n, ref=r))
        d.setdefault("needs_from", [])
        existing_needs = {n.get("key") for n in d["needs_from"]}
        for n in NEEDS:
            if n["key"] not in existing_needs:
                d["needs_from"].append(n)
        d.setdefault("blockers", [])
        existing_ids = {b.get("id") for b in d["blockers"]}
        for b in BLOCKERS:
            if b["id"] not in existing_ids:
                d["blockers"].append(b)
        d["status"] = STATUS

    d = update_fragment("mech-lead", mutate)
    print(f"[frag_write] ✅ mech.yaml 已原子更新: artifacts={len(d['artifacts'])} "
          f"claims={len(d['interface_claims'])} needs={len(d['needs_from'])} blockers={len(d['blockers'])}")


if __name__ == "__main__":
    main()
