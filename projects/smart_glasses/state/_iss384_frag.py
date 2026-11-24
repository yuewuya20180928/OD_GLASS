#!/usr/bin/env python3
"""ISS-384 (hw-lead) · 分片落盘 · 2026-11-24
纪律: 分片必须走 state/frag_write.py 的原子写 (禁 open(p,'w'))
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from frag_write import update_fragment  # noqa: E402

ARTIFACTS = [
    {"path": "HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md", "kind": "note", "version": "v1.0",
     "updated_at": "2026-11-24",
     "summary": "ISS-384 充电电流活值口径真相页 §0~§5 + 机器块 charge_current_live_value: (coef_main 1.216 / coef_cv 1.071 / 680Ω ichg_max 0.697 / per_pin_max 0.349 / margin 1.43×); 逐处订正表 35 行 (34 处活值 + 1 处数值不变说明行); 历史留痕 vs 活值分账表 (活值 34 / ISS-230 作废标记 2 / 网表合法历史说明 2 / 订正块留痕 35); 根因 = 0.822 是 1.216 的倒数 (方向反); 证据分级 [实测]/[推算]/[官方]/[0数据] 逐条标注; 未决 0 条硬阻塞 (4 条 [0数据] 均带降级方案)。零落表零写板零改既有闸零外发不代拍。"},
    {"path": "HW/check_charge_current_live_value.py", "kind": "gate", "version": "v1.0",
     "updated_at": "2026-11-24",
     "summary": "ISS-384 新建闸 (零挂链, 未改任何既有闸): 扫 HW/PCB_OUTLINE_60x15.md + HW/J_CHG_SELECTION.md + HW/POWER_BUDGET_V3.md, 按【语境】判旧系数 0.822 / 0.411A / 1.22× / 旧充电时间 / 旧 TS 偏移是否为活值 ⇒ 判红并点名 文件:行号; 两条命门各有反向用例: ① 删 L151/L193 的 ISS-230 作废标记 ⇒ 变红 (不按子串判) ② 把网表/脚表/BOM/板文件加进扫描范围 ⇒ 变红 (落表真源不许被文档闸碰); 裸跑 rc=0, --selftest 14/14 末行 ALL TESTS PASS。"},
    {"path": "HANDOFF/2026-11-24_hw-lead_ISS384_充电电流活值口径收口与R10判定面盲区.md",
     "kind": "handoff", "version": "v1.0", "updated_at": "2026-11-24",
     "summary": "ISS-384 交卷页 B1~B6 齐全 (B1 结论摘要 8 条 / B2 验收标准自评 15 条逐条通过·未验·依据 + B2-1 逐处订正表 35 行 / B3 证据分级 / B4 接口取值声明 12 条 / B5 未决项与卡点 5 条零外部挂起 / B6 自证复现命令); 含零落表·零写板·零改既有闸·零挂链·零外发·不代拍 全部实测读数。"},
]

CLAIMS = [
    {"key": "charge_current_coef_main", "value": "1.216",
     "note": "★ISS-384 追平: ICHG/IIN = η·(Vbus/Vbat) @ VBAT=3.70V (最坏档)。★旧值 0.822 = (Vbat/Vbus)/η = 1.216 的精确倒数 ⇒ 方向反了 ⇒ 已作废 (MECH/HINGE_POWER_CALC.md §0-A)。",
     "ref": "HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md#机器块 + MECH/HINGE_POWER_CALC.md §0-A"},
    {"key": "charge_current_coef_cv", "value": "1.071",
     "note": "★ISS-384 追平: @ VBAT=4.20V (CV 段末端)。来源 HW/CHARGE_BOARD_SPEC.md §2.4 (ISS-220 第 1 批已改正)。",
     "ref": "HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md#机器块"},
    {"key": "charge_current_rilim_landed", "value": "680Ω",
     "note": "★ISS-384 只报事实不代拍: 网表 L47/L48 自 2026-11-16 (V-4 裁定) 起已落 680Ω ⇒ 本单把三份文档追平到该真值, 网表一个字节没动。是否维持/改档 = 老板·PM 域。",
     "ref": "HW/netlist_v1.csv L47/L48 + HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md §0"},
    {"key": "charge_current_ichg_max_680", "value": "0.697A",
     "note": "★ISS-384 追平: 680Ω 档 max (KILIM_max 390 AΩ) ⇒ ICHG = IINMAX × 1.216。已写进三份文档的追加订正块与真相页机器块。",
     "ref": "MECH/hinge_power_calc.json rilim_table (680Ω max)"},
    {"key": "charge_current_per_pin_max_680", "value": "0.349A",
     "note": "★ISS-384 追平: pin1/pin2 双 pin 并联 ⇒ ÷2 ⇒ 0.349A ≤ 0.50A 触点工作上限 ⇒ 唯一成立档。",
     "ref": "MECH/hinge_power_calc.json rilim_table (680Ω max)"},
    {"key": "charge_current_margin_680", "value": "1.43×",
     "note": "★ISS-384 追平: 0.50A ÷ 0.349A = 1.43× (旧值 1.22× 是 390Ω 档在错系数下的数, 已作废)。",
     "ref": "MECH/HINGE_POWER_CALC.md §0-A.1 对照表"},
    {"key": "charge_current_per_pin_max_390", "value": "0.608A",
     "note": "★ISS-384 追平: 390Ω 档 max ⇒ 单 pin 0.608A ⇒ 超 0.50A 触点上限 21.6% ⇒ 该档判死 (旧值 0.411A/余量 1.22× 作废)。",
     "ref": "MECH/HINGE_POWER_CALC.md §0-A.1 对照表"},
    {"key": "charge_current_per_pin_max_470", "value": "0.505A",
     "note": "★ISS-384 追平: 470Ω 档 max ⇒ 单 pin 0.505A ⇒ 超上限 1.0% ⇒ 该档判死 (旧值 0.341A/有 0.16A 余量 作废)。",
     "ref": "MECH/hinge_POWER_CALC.md §0-A.1 对照表"},
    {"key": "charge_current_per_pin_max_300", "value": "0.790A",
     "note": "★ISS-384 追平: 300Ω 档 max ⇒ 单 pin 0.790A ⇒ 超上限 58% ⇒ 该档判死 (旧值 0.534A 作废)。",
     "ref": "MECH/hinge_power_calc.json rilim_table (300Ω max)"},
    {"key": "ts_ref_ground_offset_680", "value": "20.9mV / 0.65°C",
     "note": "★ISS-384 追平: O-4 行「TS 参考地被 1A 回流抬高 14-32mV = 0.44-0.99°C」⇒ 按 680Ω 档 0.697A 改为 20.9mV = 0.65°C (旧值作废)。",
     "ref": "MECH/HINGE_POWER_CALC.md §M-4 表 (680Ω 行)"},
    {"key": "charge_time_max_680", "value": "34.41min",
     "note": "★ISS-384 追平: 680Ω 档 max 充电时间 (400mAh 口径); 旧值 51min 是错系数下的数。",
     "ref": "MECH/hinge_power_calc.json rilim_table t_charge_min"},
    {"key": "charge_current_doc_green", "value": "HW/check_charge_current_live_value.py rc=0",
     "note": "★ISS-384 新闸 (零挂链): 扫三份 HW 活文档, 按语境判旧系数活值 ⇒ 判红点名 文件:行号; 历史留痕 (ISS-230 L151/L193) 与落表真源 (网表/脚表/BOM) 均不误伤, 且各有反向用例。",
     "ref": "HW/check_charge_current_live_value.py"},
]

NEEDS = [
    {"key": "iss384_gate_hook_decision", "to": "main",
     "item": "是否把新闸 HW/check_charge_current_live_value.py 挂进 state/gate_check.py。★本单按先例零挂链 (挂链 = main 的地界) ⇒ 请 main 决定; 新闸已可裸跑 rc=0 + --selftest 14/14 随时可挂。",
     "since": "2026-11-24", "due": "2026-11-25",
     "status": "open", "evidence": "[实测] grep -c check_charge_current_live_value state/gate_check.py = 0"},
    {"key": "iss384_rilim_档位确认", "to": "main",
     "item": "R_ILIM 是否维持 680Ω (V-4 已裁且已落表 2026-11-16)。★本单不代拍, 只报『文档与已落表真值不一致已修完』。若要改档 ⇒ 走板只改一次那一趟 (换料不换板, ILIM 脚稳 0.8V)。",
     "since": "2026-11-24", "due": "2026-11-25",
     "status": "open", "evidence": "[实测] HW/netlist_v1.csv L47/L48 = 680Ω; MECH §0-A.1: 390/470/300 档在 1.216 系数下全判死"},
    {"key": "iss384_jchg_触点额定", "to": "main",
     "item": "J_CHG 座体单触点额定 ≥0.5A 的厂商书面确认 (RFQ 硬判据)。★[0数据] (规格页未核) ⇒ 降级方案: 若只拿得到 0.3A 型号, 则 680Ω 档单 pin 0.349A 也不合格 ⇒ 需 R_ILIM ≥790Ω 或 1.0mm pitch (MECH §M-6 已量化)。★本单零外发, 只把后果量化给 PM。",
     "since": "2026-11-24", "due": "2026-11-26",
     "status": "open_degraded", "evidence": "[0数据] + MECH/HINGE_POWER_CALC.md §M-6"},
    {"key": "iss384_evt_板端实测", "to": "main",
     "item": "板端 ICHG / 触点温升实测 (EVT 阶段)。★[0数据] (板端 0 条实测) ⇒ 降级方案: EVT 按 HW/EVT_RELIABILITY_TEST_ITEMS.md 实测复核; 在此之前所有 ICHG 数一律标 [推算]/[实测](脚本), 不冒充实测。",
     "since": "2026-11-24", "due": "EVT 阶段",
     "status": "open_degraded", "evidence": "[0数据] MECH/HINGE_POWER_CALC.md §8 证据分级汇总"},
]

SUMMARY = ("ISS-384 交卷 (2026-11-24 08:2x-09:xx): 充电电流活值口径收口 = 真相页 HW/CHARGE_CURRENT_LIVE_VALUE_CALIBER.md "
           "(§0~§5 + 机器块) + 新闸 HW/check_charge_current_live_value.py (零挂链, 裸跑 rc=0, --selftest 14/14 ALL TESTS PASS) "
           "+ 交卷页 B1~B6 + 三份 HW 活文档【追加式订正块】(PCB_OUTLINE 14 行 / J_CHG 16 行 / POWER_BUDGET 5 行 = 34 处活值逐处追平到 680Ω 落表真值 "
           "ICHG 0.697A / 单 pin 0.349A / 余量 1.43× / 系数 1.216@3.70V 与 1.071@4.20V)。关键事实: 网表 2026-11-16 (V-4) 已落 680Ω ⇒ 网表早对, 错的是文档; "
           "既有闸 R10 只扫 CHARGE_BOARD_SPEC.md (已清零 ⇒ 绿) ⇒ 判定面有洞 = 机器事实, 本单另写新闸不碰既有闸。零落表 (网表/脚表/BOM md5 逐字同, "
           "网表那 2 处 0.822 合法历史说明一字未动) 零写板 (板三项指纹逐字同) 零改既有闸 零挂链 (grep=0) 零外发 不代拍 (R_ILIM 档位归老板/PM 域)。")


def main():
    def mutate(d):
        d.setdefault("artifacts", []).extend(ARTIFACTS)
        d.setdefault("interface_claims", []).extend(CLAIMS)
        d.setdefault("needs_from", []).extend(NEEDS)
        st = d.setdefault("status", {})
        st["phase"] = "fixing"
        st["progress_pct"] = 100
        st["health"] = "green"
        st["summary"] = SUMMARY
        st["updated_at"] = "2026-11-24"
        d["updated_at"] = "2026-11-24"
        d["updated_by"] = "hw-lead"

    update_fragment("hw-lead", mutate)
    print("frag_write OK: artifacts +%d, interface_claims +%d, needs_from +%d"
          % (len(ARTIFACTS), len(CLAIMS), len(NEEDS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
