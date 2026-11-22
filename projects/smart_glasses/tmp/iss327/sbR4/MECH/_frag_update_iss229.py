#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-229 分片原子写脚本 —— 充电皮肤温度按改正系数 1.216 重算 + MECH 闸 G5b/C21 重锚

走 state/frag_write.py 的 update_fragment (tmp + fsync + os.replace), 全程零 open(p,"w").

纪律:
  * 只写自己 (mech-lead) 的分片
  * 一个别人的条目都不删不改 (别人的分片一个字节都不碰)
  * issue 状态 / owner 是 main 的活, 本脚本不碰 state/issue_log.yaml
  * 本单改值只限【本域可算的派生数】(皮肤侧表 / 充电时间 / TS 偏移 / 铰链段发热 / 皮肤增量)
    —— 旧值一律在 note 里留痕 (★ISS-229 订正), 不删历史
  * 老板拍板值 (R_ILIM 现行 390Ω / 网表现值) 一字未动, 只补 note 订正
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "state"))

from frag_write import update_fragment  # noqa: E402

AGENT = "mech-lead"
SINCE = "2026-11-16"

# ============================================================== artifacts
ARTIFACTS = [
    {
        "path": "MECH/hinge_power_calc.py",
        "kind": "script",
        "version": "v2.0",
        "updated_at": SINCE,
        "summary": (
            "ISS-229 充电电流换算系数改正: ICHG_FACTOR 0.822 → **1.216 @Vbat 3.70V** / **1.071 @4.20V** "
            "(buck 功率守恒 ICHG/IIN = η·Vbus/Vbat; 旧 0.822 = (Vbat/Vbus)/η = 1.216 的【精确倒数】⇒ 方向反了 ⇒ "
            "只留痕不参与计算, 常量 ICHG_FACTOR_VOID_LEGACY 保留) + RILIM_VALUES 增 **1.2kΩ** 候选档 "
            "+ 皮肤侧温度 / 单 pin 载流 / TS 偏移 / 充电时间 全部按新系数重算。--json 出 "
            "rilim_table(15 行) / copper_vs_rilim(10 行) / rilim_full_grid(30 行)。★口径一个没动 "
            "(k_eff 50.13 K/W · R_path 口径A保守 110.78 mΩ · 基准 35 °C · R_cell 0.10 Ω · 铜厚 1oz/2oz · "
            "KILIM 320/355/390 AΩ · 红线 43 °C)。★[实测] = 脚本实跑 (rc=0), **板端 [实测] = 0 条**, "
            "温度/发热全为 [推算]。"
        ),
    },
    {
        "path": "MECH/hinge_power_calc.json",
        "kind": "data",
        "version": "v2.0",
        "updated_at": SINCE,
        "summary": (
            "ISS-229 活口径表唯一真源: ichg_factor (1.216 @3.70V / 1.071 @4.20V / legacy_void 0.822 留痕) "
            "+ rilim_table 15 行 (5 档 × min/typ/max) + copper_vs_rilim 10 行 + rilim_full_grid 30 行 "
            "(5 档 × min/typ/max × 1oz/2oz), 每行带 evidence (ICHG=[推算] / board_measured=0)。"
            "★**下游 (热路 / 整机重量账 / 充电板规格 / 决策页) 只能引用这里的现行值** ⇒ 旧数 (47.1/42.1/39.9/37.3 °C "
            "等, 按作废系数 0.822 算) 一律带「已作废」标记。"
        ),
    },
    {
        "path": "MECH/HINGE_POWER_CALC.md",
        "kind": "calc",
        "version": "v2.0",
        "updated_at": SINCE,
        "summary": (
            "ISS-229 口径订正留痕 + 全表重出: §0-A (一句话说明旧表整体作废 + 新系数推导 + 复现命令) + "
            "§0-A.1 旧值→新值对照表 22 行 (旧数不删) + 正文 M-1/M-3/M-4/M-6/M-7/M-8 与 "
            "§4.1/§4.2/§4.3/§5.3/§7-N8 逐处标「旧值已作废」。★**新数**: max 档 1oz 皮肤侧 "
            "300Ω 61.4 ❌ / 390Ω 50.6 ❌ (超 43 °C 红线 7.6 °C) / 470Ω 45.8 ❌ / **680Ω 40.1 ✅** (余 2.9 °C) / "
            "**1.2kΩ 36.7 ✅**; 单 pin max 0.790/0.608/0.505/0.349/0.198 A; TS 偏移 1.46/1.13/0.93/0.65/0.37 °C; "
            "充电时间 (400 mAh 仅 CC 段) 15/20/24/34/61 min。★**旧 42.14 °C / 47.07 °C (按 0.822 算) 判为"
            "「无有效数字」** ⇒ 活档 = 680Ω / 1.2kΩ (V-4 待 main/老板拍, 本单不代拍)。"
        ),
    },
    {
        "path": "MECH/FPC_FAB_NOTES.md",
        "kind": "note",
        "version": "v2.0",
        "updated_at": SINCE,
        "summary": (
            "ISS-229 同型旧数清理: §0-A 口径订正留痕 + §0-A.1 对照表 (系数 / 390Ω 档 ICHG 0.822→1.216 A / "
            "单 pin 0.411→0.608 A / 铰链段发热 15-127 → **8.3-276.8 mW** / 300Ω 档皮肤 47.1→**61.4 °C** ❌ / "
            "2oz 57.4 °C ❌) + §载流表 / P-4 / X-2 / 证据表逐处标旧数作废。★结论 (加厚铜箔救不了充电发热) "
            "在改正系数下**更强**: 300Ω 档 2oz 仍超红线 14.4 °C ⇒ 唯一有效杠杆仍是 R_ILIM 换料不换板。"
        ),
    },
    {
        "path": "MECH/HW_CROSS_REVIEW_TRIAGE.md",
        "kind": "spec",
        "version": "v2.0",
        "updated_at": SINCE,
        "summary": (
            "ISS-229 MECH 闸重锚: §1 `source_ledger.entries` 网表那条 md5 **13f59a43… → 3215020b…** "
            "(by=ISS-223 / prev_md5 + landed_at 2026-11-16 05:18:41 四项齐全) + §3.1 新增 **R-02** 留痕行 "
            "(谁改的 / 哪个单号 / 新旧 md5 / 复现命令) + §0 Q-10。★脚表锚点 (by=ISS-220 / a600afae…) 本轮 md5 "
            "未变 ⇒ 一字不动。★门禁 G5b + C21 由 FAIL 回到 [OK]: **rc=2 (21/23) → rc=0 (23/23)**, "
            "`--selftest` **14/14** 反向用例一条没删 (门禁脚本 md5 fa9b59e5… 逐字节不变 ⇒ 判据没被改软)。"
        ),
    },
    {
        "path": "HANDOFF/2026-11-16_mech-lead_ISS229_充电皮肤温度重算与MECH闸重锚.md",
        "kind": "handoff",
        "version": "v1.0",
        "updated_at": SINCE,
        "summary": (
            "ISS-229 交接单 (B1 结论 12 条 / B2 逐条自评 21 条 + 未验 3 条 / B3 证据分级四档 / "
            "B4 接口取值 4 条 + V-4 30 行全网格 / B5 未决 6 条 / B6 七条复现命令 + 与 main 独立推算逐条对拍一致 + "
            "受保护 md5 实测) + **B7 本轮补交** (三道门禁 + 两条 selftest 实跑输出 + 两条逐字确认 + 分片落地记录)。"
            "★板端 [实测] = 0 条, 零外发, 不自签 issue_log, 不代拍 V-4。"
        ),
    },
    {
        "path": "MECH/_frag_update_iss229.py",
        "kind": "script",
        "version": "v1.0",
        "updated_at": SINCE,
        "summary": (
            "ISS-229 分片原子写脚本 (走 state/frag_write.py 的 update_fragment: tmp + fsync + os.replace, "
            "零 open(p,\"w\")): 新增 artifact 6 条 / interface_claim 4 条 (系数 1.216 + 1.071 / 活口径表指针 / "
            "网表 md5 锚点 ISS-223) + 同型旧值收口 6 条 (皮肤侧表 / 充电时间 / TS 偏移 / 铰链段发热 / 皮肤增量 / "
            "两条老板/网表现值只补 note) + answers 2 条 (iss223 / iss230) + needs 3 条 (main 整机阶段判据 / "
            "hw-lead PCB_OUTLINE 旧数 / sw-lead EVT PWR-05 充电电流判据) + 旧 need 订正追加 2 条 (只加不改)。"
        ),
    },
]

# ============================================================== 新增 claims (4 条, 与交接单 B4 §4.1 同 key)
NEW_CLAIMS = [
    {
        "key": "mech_ichg_factor_vbat_370",
        "value": "1.216",
        "note": (
            "★改正后的活口径: ICHG/IIN = η·Vbus/Vbat @Vbat=3.70V (η=0.90, Vbus=5.0V) ⇒ 0.90×5.0/3.70 = 1.216216 "
            "⇒ **1.216** (Vbat 最低 ⇒ 系数最大 ⇒ 温度最高 ⇒ 取最坏档)。★**旧值 0.822 = (Vbat/Vbus)/η = 1.216 的"
            "精确倒数 ⇒ 方向反了 ⇒ 已作废 (只留痕, 不参与计算)** ⇒ 下游凡引用充电电流的数 (皮肤温度 / 铰链发热 / "
            "电芯发热 / 单 pin 载流 / TS 偏移 / 充电时间) 一律按 1.216 重算。★[推算] (系数源 "
            "HW/CHARGE_BOARD_SPEC.md §2.4 + §3.4 方向修正, ISS-214 d10 · ISS-220 第 1 批落表已改正)。"
        ),
        "ref": "MECH/HINGE_POWER_CALC.md §0-A + MECH/hinge_power_calc.py L44~L49",
    },
    {
        "key": "mech_ichg_factor_vbat_420",
        "value": "1.071",
        "note": (
            "CV 段末端口径: ICHG/IIN = η·Vbus/Vbat @Vbat=4.20V ⇒ 0.90×5.0/4.20 = 1.071429 ⇒ **1.071**。★本表主口径取"
            "最坏的 **1.216** (@3.70V), 1.071 也在输出里列出。★旧值 0.933 同属倒数方向, 已作废留痕。★[推算]"
            " (系数源同 §2.4/§3.4)。"
        ),
        "ref": "MECH/hinge_power_calc.py L47 + MECH/hinge_power_calc.json#ichg_factor",
    },
    {
        "key": "mech_charge_skin_temp_live_table",
        "value": "MECH/hinge_power_calc.json#rilim_table",
        "note": (
            "★**充电皮肤侧温度的活口径表 = `MECH/hinge_power_calc.json` 的 `rilim_table` (15 行) / "
            "`copper_vs_rilim` (10 行) / `rilim_full_grid` (30 行)** ⇒ 下游 (热路 / 整机重量账 / 充电板规格 / "
            "决策页 §9) **只能引用 JSON 里的现行值** ⇒ 文档里的旧数一律带「已作废」标记。★max 档 1oz 皮肤侧: "
            "300Ω **61.4** ❌ / 390Ω **50.6** ❌ (超 43 °C 红线 7.6 °C) / 470Ω **45.8** ❌ / 680Ω **40.1** ✅ / "
            "1.2kΩ **36.7** ✅ °C ⇒ 活档 = 680Ω / 1.2kΩ。★**旧值 (作废, 按 0.822 系数算): 47.1 / 42.1 / 39.9 / 37.3 "
            "/ 35.8 °C** ⇒ 旧 42.14 °C / 47.07 °C **无有效数字**。★[推算] 板端 [实测] = 0 条。"
        ),
        "ref": "MECH/hinge_power_calc.json + MECH/HINGE_POWER_CALC.md §0-A.1",
    },
    {
        "key": "mech_netlist_md5_anchor_iss223",
        "value": "3215020b6d4120e1b7728227effdc6d3",
        "note": (
            "★**MECH 闸 §1 `source_ledger` 网表锚点的现行真值** = 落表单 **ISS-223** / 落表时刻 2026-11-16 05:18:41 "
            "/ 旧值 `13f59a43dbd35dc6cb16e897c8c891ab` (ISS-220) ⇒ 已在 `MECH/HW_CROSS_REVIEW_TRIAGE.md` §3.1 **R-02** "
            "留痕 (谁改的 / 哪个单号 / 新旧 md5 / 复现命令)。★脚表 `HW/netlist_v1_pins.csv` = "
            "`a600afae493f5a7a6c55f46ad35ac89c` 本轮 md5 未变 ⇒ 锚点一字不动。★门禁 **G5b + C21 由 FAIL 回到 [OK]** "
            "(rc=2 21/23 → rc=0 23/23; `--selftest` 14/14)。★[实测] (本机 md5sum + 门禁实跑)。"
        ),
        "ref": "MECH/HW_CROSS_REVIEW_TRIAGE.md §1 source_ledger + §3.1 R-02",
    },
]

# ============================================================== 同型旧值收口 (本域可算的派生数)
# ★value 改的是【按作废系数 0.822 算出来的派生数】; 旧值在 note 里逐字留痕 (不删历史)
VALUE_FIXES = {
    "mech_rilim_charge_skin_temp_c": {
        "value": "300:61.4/390:50.6/470:45.8/680:40.1",
        "note": (
            "各档 ICHG=max 的贴皮肤侧温度 (C), 口径A保守 (回流走GND双pin铜箔, 接触30mΩ/界面, FPC 1oz/0.3mm/31mm, "
            "R_cell=0.10Ω), **系数 1.216 @Vbat3.70V 最坏档**。★**ISS-229 订正 (2026-11-16)**: 原值 "
            "`300:47.1/390:42.1/470:39.9/680:37.3` 是按**作废系数 0.822** 算的 ⇒ **已作废 (逐字留痕在此, 不删)**; "
            "★新值 = 300Ω **61.4** ❌ / 390Ω **50.6** ❌ (超 43 °C 红线 7.6 °C) / 470Ω **45.8** ❌ / 680Ω **40.1** ✅ "
            "(余 2.9 °C) / **1.2kΩ 36.7 ✅** (本轮新增候选档) ⇒ 活档 = 680Ω / 1.2kΩ。2oz 版: 300Ω 57.4 / 390Ω 48.3 / "
            "470Ω 44.1 / 680Ω 39.4 / 1.2kΩ 36.4 °C。★[推算] 板端 [实测] = 0 条。"
        ),
        "ref": "MECH/HINGE_POWER_CALC.md §0-A.1 + MECH/hinge_power_calc.json#rilim_table",
    },
    "mech_rilim_charging_minutes": {
        "value": "300:15/390:20/470:24/680:34",
        "note": (
            "各档满充时间 (min, 400mAh, 仅CC段估算, 未计CV拐点, 实际再加10-20%), ICHG=max 档。★**ISS-229 订正 "
            "(2026-11-16)**: 原值 `300:22/390:29/470:35/680:51` 按**作废系数 0.822** 算 ⇒ **已作废 (留痕, 不删)**; "
            "★新值 = 300Ω **15** / 390Ω **20** / 470Ω **24** / 680Ω **34** / **1.2kΩ 61** min (电流↑ ⇒ 时间↓)。"
            "★[推算]"
        ),
        "ref": "MECH/HINGE_POWER_CALC.md §0-A.1 + MECH/hinge_power_calc.json#rilim_table",
    },
    "mech_ts_ref_offset_c": {
        "value": "0.37-1.46",
        "note": (
            "TS 跨铰链参考地被充电回流抬高造成的等效温度偏差 (C), TS 斜率 32.4 mV/C, 偏移 = ICHG×30mΩ。★**ISS-229 订正 "
            "(2026-11-16)**: 原值 `0.44-0.99` 是按**作废系数 0.822** 算的 ⇒ **已作废 (留痕, 不删)**; ★新值逐档 (max 档) = "
            "300Ω **1.46** / 390Ω **1.13** / 470Ω **0.93** / 680Ω **0.65** ✅ / 1.2kΩ **0.37** ✅ °C ⇒ ★**「留 1 °C 门限"
            "裕量」只在 680Ω / 1.2kΩ 成立** (390Ω 档已超)。⇒ 这是一条**指向 680Ω/1.2kΩ 的独立约束** (与皮肤温度 / "
            "单 pin 触点额定同向)。★减害方案 pin9/pin10 改 NTC 专用回流 已被 ISS-206 作废 (pin10 现为 HINGE_RSV "
            "预留不装) ⇒ 偏差靠选档解决, 不改 pin map。★[推算]"
        ),
        "ref": "MECH/HINGE_POWER_CALC.md §0-A.1 + M-4 + MECH/hinge_power_calc.json#rail_impact",
    },
    "mech_hinge_chg_power_mw_at_1a": {
        "value": "8.3-276.8",
        "note": (
            "铰链段发热 (mW) —— 全候选网格 (5 档 × min/typ/max × 1oz/2oz), 口径A保守; 下限 = 1.2kΩ min 档 2oz, "
            "上限 = 300Ω max 档 1oz; 现行 390Ω 档 = **78.7-163.8 mW**。★**ISS-229 订正 (2026-11-16)**: 原值 `15-127` "
            "按**作废系数 0.822** 算 (上界 127 mW = 300Ω 档 max 旧 ICHG 1.069 A × R_path 110.78 mΩ) ⇒ **已作废 (留痕, "
            "不删)**; ★新值 **8.3-276.8 mW** (上界 ×2.19, 电流² 律) ⇒ 皮肤侧增量见 "
            "`mech_hinge_chg_skin_rise_c_at_1a`。★结论 (铜箔轴向导热极强 ⇒ 铜箔自身温升 <0.1 °C ⇒ 不做额外散热铜箔) "
            "在新系数下不变。★[推算]"
        ),
        "ref": "MECH/FPC_FAB_NOTES.md §0-A.1 + MECH/hinge_power_calc.json#rilim_full_grid",
    },
    "mech_hinge_chg_skin_rise_c_at_1a": {
        "value": "0.42-13.88",
        "note": (
            "铰链段发热引起的贴皮肤处温度增量 (C), 用 MECH_BUDGET §2.3 口径 k_eff=50.13 K/W, 基准 35 °C; 全候选网格 "
            "(下限 = 1.2kΩ min 档 2oz, 上限 = 300Ω max 档 1oz)。★**ISS-229 订正 (2026-11-16)**: 原值 `0.8-6.4` "
            "按**作废系数 0.822** 算 ⇒ **已作废 (留痕, 不删)**; ★新值 **0.42-13.88 °C**。★[推算]"
        ),
        "ref": "MECH/FPC_FAB_NOTES.md §0-A.1 + MECH/hinge_power_calc.json#rilim_full_grid",
    },
}

# ★老板/网表现值: value 一字未动, 只在 note 里追加订正 (不动拍板结论)
NOTE_APPEND = {
    "mech_rilim_recommended_ohm": (
        " | ★**ISS-229 订正 (2026-11-16)**: 本条 value 仍是**现行网表/老板 10-28 拍板值 390Ω** (一字未动); "
        "但 note 里 0.682A / 0.341A / 皮肤 39.9°C / 充电 ~35min 是按**作废系数 0.822** 算的 ⇒ **已作废 (留痕)** ⇒ "
        "按 1.216: 390Ω max = ICHG **1.216A** / 单 pin **0.608A** (>0.5A 触点天花板 21.6%) / 皮肤侧 **50.6 °C ❌** "
        "(超 43 °C 红线 7.6 °C) / TS 偏移 **1.13 °C** ⇒ ★**390Ω 档在改正口径下判 FAIL**; 活档 = **680Ω** "
        "(皮肤 40.1 °C / 单 pin 0.349A / 余量 1.43× / 充 ~34min) 或 **1.2kΩ** (36.7 °C / 0.198A / ~61min, 若电芯 ≤1C) "
        "⇒ ★**V-4 建议默认值待 main/老板拍, 本单不代拍**。"
    ),
    "r_ilim_set": (
        " | ★**ISS-229 订正 (2026-11-16)**: 本条 value 仍是**网表现值 / 老板 10-28 拍板值 390Ω** (一字未动); "
        "但 note 里「ICHG 0.822A (max), 单 pin 0.411A」按**作废系数 0.822** 算 ⇒ **已作废 (留痕)** ⇒ 按 1.216: "
        "390Ω max = ICHG **1.216A** / 单 pin **0.608A** ⇒ 300Ω 档单 pin **0.790A** (旧 0.534A) ⇒ 300Ω 档正式判死、"
        "390Ω 档在皮肤 43 °C + 0.5A 触点 + TS 1 °C 三条上全破 ⇒ 活档 680Ω / 1.2kΩ (V-4 待拍, 本单不代拍)。"
    ),
}

# ============================================================== answers (回掉本单对应的未闭合 need)
ANSWERS = [
    {
        "key": "iss223_skin_temp_recompute",
        "to": "hw-lead",
        "value": (
            "已按改正后的系数重算并落盘 (ISS-229): **ICHG/IIN = η·Vbus/Vbat = 0.90×5.0/3.70 = 1.216216 ⇒ 1.216** "
            "(@Vbat 4.20V ⇒ 1.071; 主口径取最坏 1.216), 旧 0.822 = 1.216 的精确倒数 ⇒ 作废留痕。★max 档 1oz 皮肤侧 = "
            "300Ω **61.4** / 390Ω **50.6** / 470Ω **45.8** / 680Ω **40.1** / 1.2kΩ **36.7** °C ⇒ **活档 = 680Ω / "
            "1.2kΩ**; 单 pin max = 0.790 / 0.608 / 0.505 / 0.349 / 0.198 A ⇒ **390Ω 与 470Ω 档超 0.5 A 触点额定**; "
            "TS 偏移 = 1.46 / 1.13 / 0.93 / 0.65 / 0.37 °C ⇒ **留 1 °C 裕量只在 680Ω / 1.2kΩ 成立**; 充电时间 "
            "(400 mAh 仅 CC 段) = 15 / 20 / 24 / 34 / 61 min ⇒ **原 42.14 °C (按 0.822 算) 已作废 ⇒ 无有效数字**。"
            "★[推算] 板端 [实测] = 0 条。复现: python3 MECH/hinge_power_calc.py (rc=0)"
        ),
        "ref": "HANDOFF/2026-11-16_mech-lead_ISS229_充电皮肤温度重算与MECH闸重锚.md §B4.2 + "
               "MECH/HINGE_POWER_CALC.md §0-A.1",
    },
    {
        "key": "iss230_skin_temp_void_marked",
        "to": "hw-lead",
        "value": (
            "你标的作废成立, 且 ISS-229 已交叉核对并给出新数: 42.14 °C / 47.07 °C **无有效数字** (按作废系数 0.822 算) ⇒ "
            "现行 = **390Ω max 皮肤侧 50.6 °C ❌** (超 43 °C 红线 7.6 °C) + **单 pin 0.608A ❌** (超 0.5 A 触点额定 "
            "21.6%) ⇒ 390Ω 档在改正口径下判 FAIL; 同句的充电时间 ~29.20min / 典型 32.08min 同样出自作废表 ⇒ 新值 "
            "**~19.7min / ~21.7min** (400 mAh 仅 CC 段); O-4 行 TS 偏移 0.44-0.99 °C ⇒ 新值 390Ω max **36.5 mV = "
            "1.13 °C** (留 1 °C 裕量只在 680Ω/1.2kΩ 成立)。★**680Ω 复核**: max 1oz 皮肤 **40.1 °C ✅** (余 2.9 °C) + "
            "单 pin **0.349A ✅** (余量 1.43×) + TS **0.65 °C ✅** ⇒ 与你 11-01 的 `chg_rilim_recommended`=680Ω 一致 ⇒ "
            "建议默认值仍 680Ω (电芯若 ≤1C 则退 1.2kΩ); ★**V-4 由 main/老板拍, 本单不代拍**; 另建议把 "
            "`HW/PCB_OUTLINE_60x15.md` §3.4 表 / L149 充电时间 / §4.2 O-4 行这三处旧数按新表订正 (已登记 need)。"
        ),
        "ref": "HANDOFF/2026-11-16_mech-lead_ISS229_充电皮肤温度重算与MECH闸重锚.md §B4.2 §U-2 + "
               "MECH/HINGE_POWER_CALC.md §0-A.1",
    },
]

# ============================================================== 新增 needs (本单新登记)
NEEDS = [
    {
        "key": "iss229_mech_charge_skin_temp_scope_to_main",
        "to": "main",
        "since": SINCE,
        "due": "2026-11-19",
        "item": (
            "★ISS-229 出数 (改正系数 1.216) 后, 请裁【整机阶段】口径要不要跟: ①**充电时皮肤侧 43 °C 红线** —— 老板 "
            "10-28 已拍「边戴边充不允许」⇒ 充电时眼镜不在皮肤上 ⇒ 皮肤侧这条在充电场景**不是硬约束**; 但**与佩戴无关**的"
            "三条仍成立 (铰链段温升 / **TS 停充门限偏差** 390Ω max 1.13 °C / **单 pin 触点额定** 390Ω max 0.608A) ⇒ "
            "问 main: 整机阶段的『充电链』判据要不要按 680Ω / 1.2kΩ 重写? ★**本单只登记, 不改别人的件** (PROJECT_TRACKER "
            "§0 / DECISION_PENDING / issue_log 一个字节都没碰); ②**V-4 建议默认值** (680Ω 或 1.2kΩ) 仍**待老板拍** ⇒ "
            "DECISION_PENDING_2026-11-16.md §A2 的 V-4 行可直接引用本单 §B4.2 的 **30 行全网格** (含 1.2kΩ 新候选档); "
            "③本域既有 need `iss091_rilim_decision` 里的 47.1 °C / 42.1 °C 是按**作废系数 0.822** 算的 ⇒ 本单**只加订正"
            "说明、没删历史条目** ⇒ 以 §B4.2 为准。"
        ),
    },
    {
        "key": "iss229_mech_hw_pcb_outline_old_charge_numbers",
        "to": "hw-lead",
        "since": SINCE,
        "due": "2026-11-19",
        "item": (
            "ISS-229 已出改正系数下的权威表 ⇒ `HW/PCB_OUTLINE_60x15.md` 里还有三处带 **0.822 旧口径**的数 "
            "(★**只报不改, HW 地界由 hw-lead 自己改**): ①§3.4 表 (L142~L147) 的 ICHG / 单 pin / 余量列 —— "
            "390Ω 现写 0.82A / 0.411A / ✅余量 1.22× ⇒ 新值 **1.216A / 0.608A / ❌超 0.5A 天花板 21.6%**; 470Ω 现写 "
            "0.68A / 0.341A / ✅ ⇒ 新值 **1.009A / 0.505A / ❌超 1.0%**; 680Ω 现写 0.47A / 0.236A ⇒ 新值 **0.697A / "
            "0.349A / ✅余量 1.43×**; 300Ω 现写 0.534A ⇒ 新值 **0.790A**; ②L149 那句「390Ω max 档充电 ~29.20min / 典型 "
            "32.08min」⇒ 新值 **~19.7min / ~21.7min** (400 mAh 仅 CC 段, 实际再加 10-20%); ③§4.2 O-4 行「TS 参考地被 "
            "1A 回流抬高 14-32mV = 0.44-0.99 °C」⇒ 新值 390Ω max **36.5 mV = 1.13 °C** (留 1 °C 裕量只在 680Ω / 1.2kΩ "
            "成立)。★出处: `MECH/HINGE_POWER_CALC.md` §0-A.1 + `MECH/hinge_power_calc.json` (rilim_table / "
            "copper_vs_rilim / rilim_full_grid); 复现: `python3 MECH/hinge_power_calc.py` (rc=0)。"
        ),
    },
    {
        "key": "iss229_mech_sw_evt_pwr05_charge_current_criterion",
        "to": "sw-lead",
        "since": SINCE,
        "due": "2026-11-19",
        "item": (
            "ISS-229 重算后, `SW/EVT_TEMPLATE.md` **PWR-05**「充电电流 ≥ 1.5A @5V/2A 适配器」与现行 R_ILIM 体系不相容 "
            "(★**只报不改, SW 地界由 sw-lead 自己改**): 改正系数 1.216 下 max 档**电池侧**充电电流 = 390Ω 1.216A / "
            "680Ω 0.697A / 1.2kΩ 0.395A ⇒ 连现行 V-4 候选 (680Ω) 也只有 0.697A, **1.5A 达不到**; 若该判据量的是"
            "**输入电流 IIN**, 390Ω 档 IINMAX max = 1.00A (680Ω 档 0.574A) ⇒ 同样达不到 ⇒ ★请 sw-lead 复核它到底量哪个量 "
            "(输入电流 vs 电池侧电流), 并给改法 (降阈值 / 改判据对象 / 或注明 demo 板不装充电链故本项不适用 —— "
            "charge IC 在 demo 板是 DNP 位)。★该不兼容**在旧 0.822 系数下就已存在** (390Ω max = 0.822A) ⇒ 属既存判据, "
            "不是 ISS-229 造成, 本单只把新系数下的准确数摆出来。★出处: `MECH/HINGE_POWER_CALC.md` §0-A.1 + "
            "`MECH/hinge_power_calc.json`; 复现: `python3 MECH/hinge_power_calc.py` (rc=0)。"
        ),
    },
]

# ★既有 need 的订正: 只在 item 末尾追加, 历史条目一个字不删
NEED_NOTE_APPEND = {
    "iss091_rilim_decision": (
        " | ★**ISS-229 订正 (2026-11-16, 只加不改)**: 本条里的『皮肤 47.1C → 39.9C / 390Ω 42.1C / 充电 22→35min』"
        "全部按**作废系数 0.822** 算 ⇒ **已作废, 无有效数字** ⇒ 现行口径: max 档 1oz 皮肤侧 300Ω **61.4** ❌ / 390Ω "
        "**50.6** ❌ / 470Ω **45.8** ❌ / **680Ω 40.1** ✅ / **1.2kΩ 36.7** ✅ °C; 单 pin max 0.790 / 0.608 / 0.505 / "
        "0.349 / 0.198 A; 充电时间 15 / 20 / 24 / 34 / 61 min ⇒ 活档 = **680Ω / 1.2kΩ** ⇒ **裁决入口仍是 V-4** "
        "(`DECISION_PENDING_2026-11-16.md` §A2), 详见 HANDOFF/2026-11-16_mech-lead_ISS229_*.md §B4.2。★本单不代拍。"
    ),
    "iss091_worn_while_charging": (
        " | ★**ISS-229 订正 (2026-11-16, 只加不改)**: 本条里的『300Ω 档 47.1C / 乐观口径也 44.2C』按**作废系数 "
        "0.822** 算 ⇒ **已作废** ⇒ 现行: 300Ω max 皮肤侧 **61.4 °C** ❌ / 乐观 55.1 °C ❌; 390Ω max **50.6 °C** ❌ / "
        "乐观 46.9 °C ❌; 470Ω max **45.8 °C** ❌ / 乐观 43.2 °C; 680Ω max **40.1 °C** ✅; 1.2kΩ max **36.7 °C** ✅ ⇒ "
        "『边戴边充不允许』这条产品语义**仍然有效** (充电时眼镜不在皮肤上), 但**活档只剩 680Ω / 1.2kΩ** (V-4 待拍)。"
    ),
}

STATUS = {
    "phase": "P3",
    "progress_pct": 99,
    "health": "yellow",
    "summary": (
        "2026-11-16 ISS-229 (充电皮肤温度按改正系数 1.216 重算 + MECH 闸 G5b/C21 重锚): ★**根因 = 换算系数方向反了** —— "
        "buck 功率守恒 ICHG/IIN = η·Vbus/Vbat = 0.90×5.0/3.70 = **1.216** (@4.20V ⇒ 1.071), 旧 **0.822** = "
        "(Vbat/Vbus)/η = 1.216 的**精确倒数** ⇒ 系数偏小 ⇒ 电流偏小 ⇒ 温度偏乐观 ⇒ 旧表 rilim_table / "
        "copper_vs_rilim / rilim_full_grid **全部作废 (逐字留痕, 不删)** ⇒ 新数 (max 档 1oz): 皮肤侧 300Ω **61.4** ❌ / "
        "390Ω **50.6** ❌ (超 43 °C 红线 7.6 °C) / 470Ω **45.8** ❌ / **680Ω 40.1** ✅ (余 2.9 °C) / **1.2kΩ 36.7** ✅; "
        "单 pin max 0.790 / **0.608** ❌ / 0.505 / 0.349 / 0.198 A; TS 偏移 1.46 / **1.13** / 0.93 / **0.65** ✅ / 0.37 °C "
        "(留 1 °C 裕量只在 680Ω/1.2kΩ 成立); 充电时间 15/20/24/34/61 min ⇒ **活档 = 680Ω / 1.2kΩ** (V-4 待 main/老板拍, "
        "**本单不代拍**); 原 42.14 °C / 47.07 °C **无有效数字**。★**MECH 闸重锚**: §1 source_ledger 网表 md5 "
        "13f59a43→**3215020b** (by=ISS-223, landed_at 05:18:41) + §3.1 **R-02** 留痕 + §0 Q-10 ⇒ 门禁 **G5b + C21 由 "
        "FAIL 回到 [OK] (rc=2 21/23 → rc=0 23/23)**, `--selftest` **14/14** 反向用例一条没删 (门禁脚本 md5 未变 ⇒ 判据没被"
        "改软); 脚表锚点未动。★**三道门禁实跑全绿**: check_demo_struct_truth **23/23** + cavity_recalc **22/22** + "
        "verify_budget **53/53 + 12/12** (selftest 14/14 / 24/24 / 11/11)。★**分片本轮真落盘** (走 state/frag_write.py "
        "原子写: 新增 artifact 6 条 / claim 4 条 / answer 2 条 / need 3 条 + 同型旧值收口 6 条, 老板/网表现值只补 note)。"
        "★阈值一个不许动 (皮肤 43 °C / 端件 60 °C / cavity_req 4.50 / CRIT 0.60 / cav_v 38.00 / duct_v 6.00) · 零外发 · "
        "板端 [实测] = 0 条 · **不自签 issue_log** (status 留给 main 落 verified) · 未碰 HW/ SW/ PROJECT_TRACKER §0。"
    ),
}


FIXED_LOG = []
NOTE_APPENDED = []
NEED_APPENDED = []


def mutate(d: dict) -> None:
    # ---- artifacts: 只追加 (同 path 多版本是本仓既有惯例)
    arts = d.setdefault("artifacts", [])
    have = {(a.get("path"), a.get("version")) for a in arts}
    for a in ARTIFACTS:
        if (a["path"], a["version"]) not in have:
            arts.append(a)

    # ---- interface_claims: 新增 4 条 (key 不重复)
    claims = d.setdefault("interface_claims", [])
    have_c = {c.get("key") for c in claims}
    for c in NEW_CLAIMS:
        if c["key"] not in have_c:
            claims.append(dict(c))
            have_c.add(c["key"])

    # ---- interface_claims: 同型旧值收口 (value 改 + note 留痕旧值)
    fixed = []
    for c in claims:
        fx = VALUE_FIXES.get(c.get("key"))
        if fx and c.get("value") != fx["value"]:
            fixed.append((c.get("key"), c.get("value"), fx["value"]))
            FIXED_LOG.append((c.get("key"), c.get("value"), fx["value"]))
            c["value"] = fx["value"]
            c["note"] = fx["note"]
            c["ref"] = fx["ref"]

    # ---- interface_claims: 老板/网表现值 —— value 一字未动, 只追加 note
    appended = []
    for c in claims:
        add = NOTE_APPEND.get(c.get("key"))
        if add and add not in (c.get("note") or ""):
            c["note"] = (c.get("note") or "") + add
            appended.append(c.get("key"))
            NOTE_APPENDED.append(c.get("key"))

    # ---- answers: 回掉本单对应的未闭合 need
    answers = d.setdefault("answers", [])
    have_a = {a.get("key") for a in answers}
    for a in ANSWERS:
        if a["key"] not in have_a:
            answers.append(dict(a))

    # ---- needs_from: 新增 3 条
    needs = d.setdefault("needs_from", [])
    have_n = {n.get("key") for n in needs}
    for n in NEEDS:
        if n["key"] not in have_n:
            needs.append(dict(n))

    # ---- needs_from: 既有 need 只追加订正说明 (不删不改历史条目)
    need_appended = []
    for n in needs:
        add = NEED_NOTE_APPEND.get(n.get("key"))
        if add and add not in (n.get("item") or ""):
            n["item"] = (n.get("item") or "") + add
            need_appended.append(n.get("key"))
            NEED_APPENDED.append(n.get("key"))

    d.setdefault("status", {}).update(STATUS)


def main() -> int:
    before = None
    try:
        import yaml
        with open(os.path.join(REPO, "state", "fragments", "mech.yaml"), encoding="utf-8") as f:
            before = yaml.safe_load(f)
    except Exception as e:  # noqa: BLE001
        print(f"[frag_update_iss229] ⚠️ 读基线失败 (不影响写): {e}")

    d = update_fragment(AGENT, mutate)

    print(f"[frag_update_iss229] ✅ {AGENT} 分片已原子更新 "
          f"(artifact {len(d.get('artifacts') or [])} / claim {len(d.get('interface_claims') or [])} / "
          f"answer {len(d.get('answers') or [])} / need {len(d.get('needs_from') or [])}) "
          f"⇒ 再跑 python3 state/merge.py")
    print(f"[frag_update_iss229] ★同型旧值收口 (改值 + note 留痕旧值): {len(FIXED_LOG)} 条")
    for k, old, new in FIXED_LOG:
        print(f"    - {k}: {old} → {new}")
    print(f"[frag_update_iss229] ★只补 note (value 一字未动): {NOTE_APPENDED}")
    print(f"[frag_update_iss229] ★既有 need 只追加订正 (历史条目不删): {NEED_APPENDED}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
