#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-11-15 21:3x · main 逐条裁决落账 (本分片 = pm.yaml, 走原子写)
=====================================================================
★背景: 本轮三个总工交卷 (ISS-195/205/206) 各登记了 need 给 main ⇒
  mech.yaml 里 `iss202*`/`iss203*`/`iss206*` 共 **14 条 PENDING** + hw.yaml 的
  `iss195_mic_y_landing_decision` 1 条 ⇒ ★**main 必须在自己的分片里逐条落 answer**
  ⇒ ★**不许把别人的分片当自己的待办挂着** (★那 14 条一直挂着 = 队列看着空, 其实全是等 main★)

★本脚本做 3 件事:
  ① 落 **13 条 answer** (★ISS-202 的 5 条 + ISS-203 的 5 条 + ISS-206 的 3 条★)
  ② 落 **1 条 answer** (★ISS-195 的麦 Y 落位★)
  ③ 升级 **1 条到老板桶** (★裁 6 = SoM 载板 A 直焊 76 / B 载板 69 两套互斥架构 ⇒ 方案取舍 = 老板级★)
     ⇒ ★**main 不替老板决定** ★ ⇒ ★**C 段 36 → 37** ★
★纪律: 只写 main 自己的分片 pm.yaml (走 frag_write 原子写) · 不写别人的分片 ·
  不改 issue_log · 不改 PROJECT_TRACKER §0 · 不发信
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from frag_write import update_fragment  # noqa: E402

# ★key → (to, value, ref) ★
ANSWERS = {
    # ── ISS-202 侧 (结构 J_CHG 旧口径) ───────────────────────────────────
    "iss202_mech_doc_residual_jchg_old_6pin": (
        "mech-lead",
        "★**main 裁决 (2026-11-15 21:3x)**: ★**做** ★ ⇒ ★**`MECH/USB_HINGE_STRUCTURE.md` 里 J_CHG 的老 6 脚拆脚注释 (SYS / VBUS_DET / BAT_DET 跨铰链) 全部删, 改成 10 脚口径** ★ "
        "⇒ ★**口径 = pin1/2=BAT_CHG · pin3/4=GND · pin5=CHG_STAT · pin6=PWR_GOOD · pin7=NC · pin8=TS_BAT · pin9/10=HINGE_RSV** ★ "
        "⇒ ★**真源 = `HW/netlist_v1.csv` 逐脚 net 名 + `HW/CHARGE_BOARD_SPEC.md` §5.2 (ISS-136 已定版)** ★ "
        "⇒ ★**注记**: 同一接口不许再有第 3 套 pin map ★",
        "HW/netlist_v1.csv + HW/CHARGE_BOARD_SPEC.md §5.2",
    ),
    "iss202_mech_c4_stack_arith_pending": (
        "mech-lead",
        "★**main 裁决 (2026-11-15 21:3x)**: ★**做** ★ ⇒ ★**C-4 按裁决写【两套算式 + 注记】, 不许只留一套** ★ "
        "⇒ ★**判据不许放宽**: cav_v 38.00 / duct_v 6.00 / CRIT 0.60 一个字不许动 ★ "
        "⇒ ★**收敛版 = 25.00mm (16p/20p/4p/10p) · [FAIL] 0 项** ★ ⇒ ★**根因是 pin 数本身 (8→10 = +2 脚 × 0.5 = +1.0mm), 不是判据被放宽** ★ "
        "⇒ ★**25.00 < 净高 38.00, 余 12.00 仍装得下** ★",
        "MECH/hinge_usb_check.py rc=0 (25.0mm · FAIL 0)",
    ),
    "iss202_mech_script_recommended_pins_jchg_8": (
        "mech-lead",
        "★**main 裁决 (2026-11-15 21:3x)**: ★**做** ★ ⇒ ★**`MECH/hinge_usb_check.py` 的 `RECOMMENDED_PINS[\"J_CHG\"]` 8 → 10** ★ "
        "⇒ ★**改完必须重跑, 不许留旧 json/旧输出** ★ (★教训: 上次死会话改完脚本就挂, 盘上留的是过期件★) "
        "⇒ ★**反向用例自证**: 副本上把 pin 数改回 8 ⇒ 必须 [FAIL] ⇒ 恢复 ⇒ rc=0 ★",
        "MECH/hinge_usb_check.py",
    ),
    "iss202_mech_other_docs_jchg_old_pinmap": (
        "mech-lead",
        "★**main 裁决 (2026-11-15 21:3x)**: ★**做** ★ ⇒ ★**11 处文档旧口径 + F-3 全部按 10p 改** ★ "
        "⇒ ★**五处数字统一**: 声明版 31.50 / 收敛版 25.00 / 触点区 21.00 / 堆叠 25.00 ★ "
        "⇒ ★**每处改完加一句注记「★已按网表真源订正★」** ⇒ ★**不许让人再以为那是当前口径** ★",
        "MECH/USB_HINGE_STRUCTURE.md",
    ),
    "iss202_mech_frag_old_needs_stale": (
        "mech-lead",
        "★**main 裁决 (2026-11-15 21:3x)**: ★**做** ★ ⇒ ★**本分片里因 pin map 改口径而失效的老 need 一并清掉** ★ "
        "⇒ ★**但只许删【被这次改口径直接证伪】的条目, 不许借机删别的** ★ "
        "⇒ ★**清掉的每条都要在交卷报告里列出来 (key + 为什么证伪)** ⇒ ★**不许静默删** ★",
        "state/fragments/mech.yaml (走 frag_write 原子写)",
    ),
    # ── ISS-203 侧 (检修口 / 几何基准) ───────────────────────────────────
    "iss203_mech_service_port_doc_15mm_margin": (
        "mech-lead",
        "★**main 裁决 (2026-11-15 21:3x)**: ★**做** ★ ⇒ ★**`MECH/SERVICE_PORT_ISS092.md`: V PCB 净空 21.00 → 36.00, 余 +17.00 → +2.00 (最坏 +1.40, 单边 +1.70)** ★ "
        "⇒ ★**三条余量逐条给 = 0.95 / 2.00 / 14.50** ★ ⇒ ★**数字全部取脚本输出, 不许手算** ★",
        "MECH/service_port_check.py rc=0 (54/54 · FAIL 0)",
    ),
    "iss203_mech_service_port_pinset2_baseline_15mm": (
        "mech-lead",
        "★**main 裁决 (2026-11-15 21:3x)**: ★**只加注记, 数字一个字不许动** ★ "
        "⇒ ★**`p2_y=7.50` / `s2_y=12.50` / `jd_y0=9.50` 是几何基准, 不是可调参数** ★ "
        "⇒ ★**只在文档里加一句「基准已作废 (15mm 口径)」, 不许改这三个数** ★",
        "MECH/service_port_check.py",
    ),
    "iss203_mech_service_port_pcb_thk_4layer": (
        "mech-lead",
        "★**main 裁决 (2026-11-15 21:3x)**: ★**做** ★ ⇒ ★**`MECH/service_port_check.py` 的 `pcb_thk` 0.80 → 1.00** ★ "
        "⇒ ★**理由**: 0.80 是 4 层口径 (脚本第 39 行自注 6 层 = 1.00) ⇒ ★**现行板 6 层 ⇒ 1.00** ★ "
        "⇒ ★**结果: H PCB 4.20 → 4.40, 余 +3.10 → +2.90** ★",
        "MECH/service_port_check.py rc=0",
    ),
    "iss203_mech_hw_cross_review_old_escape_and_holes": (
        "mech-lead",
        "★**main 裁决 (2026-11-15 21:3x)**: ★**分两半裁** ★ "
        "⇒ ★**① `hole_x=(5.00,15.00,55.00)` = 孔位坐标 ⇒ 不动** (★它跟着孔位口径走, 与 SoC 逃线无关★) ★ "
        "⇒ ★**② `soc_escape_x=(20.20,31.80)` = 旧 SoC 逃线带 ⇒ 挂 ISS-128 重算, 本轮不改** (★见 `iss206_mech_hw_cross_review_escape_band_rk3572` 的 answer★) ★",
        "MECH/hw_cross_review_check.py (PASS 14 / FAIL 17 / 条件通过 8 / 说明 15 = 54)",
    ),
    # ── ISS-206 侧 ───────────────────────────────────────────────────────
    "iss206_mech_claim_mainboard_len_carrier_direct": (
        "main",
        "★**main 裁决 (2026-11-15 21:3x)**: ★**这一维已升级给老板** (★同题条目 `iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice` 已进 C 段老板桶★) ⇒ ★**你不用再等 main 回答** ★ "
        "⇒ ★**不许自己选 69 或 76** ★ ⇒ ★**分片里两条 claim value (69mm / 76mm) 一个字都不许动** ★ "
        "⇒ ★**两条对应 `SOC_CARRIER_EVAL` §3/§5/§7 的 A 直接焊 76 / B 载板 69 两套互斥架构 = 两条活方案, 不是历史沿革** ★ "
        "⇒ ★**demo 板 (SoM 走 BTB 座) 不受此影响, 只影响整机载板形态** ★",
        "MECH/SOC_CARRIER_EVAL.md §3/§5/§7",
    ),
    "iss206_mech_hw_cross_review_escape_band_rk3572": (
        "mech-lead",
        "★**main 裁决 (2026-11-15 21:3x)**: ★**挂 ISS-128 (板面积账 + 逃线层数全部重算, RK3572 换芯后)** ★ "
        "⇒ ★**本轮不许改 `MECH/hw_cross_review_check.py` 的 `soc_escape_x`** ★ "
        "⇒ ★**理由**: 逃线带只有在【整链重出第 1 步落表】后才有两个确定输入 (落位 + 板厚档位) ⇒ 现在改 = 白改一遍 ★ "
        "⇒ ★**ISS-128 是 PCB 布局类 ⇒ 按老板 2026-11-11 10:07 口径【排队, 等原理图定稿后】⇒ 不在当期派发范围** ★ "
        "⇒ ★**恢复条件 = ISS-128 开跑时一并重算, 不许单开一条散活** ★",
        "state/issue_log.yaml ISS-128",
    ),
    "iss206_mech_frag_claim_hinge_stack_24_vs_doc_25": (
        "mech-lead",
        "★**main 裁决 (2026-11-15 21:3x)**: ★**口径 = 文档 25.00mm 为准** (★`MECH/USB_HINGE_STRUCTURE.md` §5.2 五处已按 10p 收敛 · `MECH/hinge_usb_check.py` rc=0 · 收敛版 25.0mm · FAIL 0★) ⇒ "
        "★**本分片 `interface_claims` 的 `mech_hinge_stack_fixed_mm` = 24.00 是过期值, 必须改成 25.00** ★ "
        "⇒ ★**改法 = 由 mech-lead 自己改自己的分片 (走 `state/frag_write.py` 的 `--add-claim`) ⇒ main 不写别人的分片 (纪律)** ★ "
        "⇒ ★**本轮已在你的会话里下达追加指令, 你在 ISS-134 交卷时一并做掉** ★ "
        "⇒ ★**不许手改 `state/fragments/mech.yaml` 原文 (必须走原子写)** ★",
        "MECH/USB_HINGE_STRUCTURE.md §5.2 + MECH/hinge_usb_check.py rc=0",
    ),
    "iss206_mech_close_iss202_203_needs_via_main_answers": (
        "mech-lead",
        "★**main 裁决 (2026-11-15 21:3x)**: ★**你要的 answer 已逐条落进 `state/fragments/pm.yaml` 的 `answers`** (★main 的分片 = 你的答复落账处★) ⇒ "
        "★**逐条 key (13 条, 覆盖 ISS-202 与 ISS-203 全部该答的条目)**: `iss202_mech_doc_residual_jchg_old_6pin` · `iss202_mech_c4_stack_arith_pending` · `iss202_mech_script_recommended_pins_jchg_8` · `iss202_mech_other_docs_jchg_old_pinmap` · `iss202_mech_frag_old_needs_stale` · `iss203_mech_service_port_doc_15mm_margin` · `iss203_mech_service_port_pinset2_baseline_15mm` · `iss203_mech_service_port_pcb_thk_4layer` · `iss203_mech_hw_cross_review_old_escape_and_holes` · `iss206_mech_claim_mainboard_len_carrier_direct` · `iss206_mech_hw_cross_review_escape_band_rk3572` · `iss206_mech_frag_claim_hinge_stack_24_vs_doc_25` · 本条 ★ "
        "⇒ ★**你去 `state/fragments/pm.yaml` 里按 key 查你那条 answer (grep 即可)** ⇒ ★**本轮你不用再等 main** ★",
        "state/fragments/pm.yaml (answers)",
    ),
    # ── ISS-195 侧 (麦 Y 落位) ───────────────────────────────────────────
    "iss195_mic_y_landing_decision": (
        "hw-lead",
        "★**main 裁决 (2026-11-15 21:3x)**: ★**麦 M1 的 Y 落位维持 Y=12.00** (★**现行值, 本轮一个字都不动**★) ⇒ 该落位下孔壁净空 **1.26mm** (控制孔 S1) · 三条判据 (不重叠>0 / 板规则 0.25 / ISS-092先例 1.00) 全 PASS · **余量 +0.26mm** ★ "
        "★★**唯一禁止值**: 板中线 **Y=15.00** (★30mm 板的几何中线★) ⇒ 该处最差仅 **0.55mm** (P1) ⇒ **破 ISS-092 先例 1.00mm ⇒ 不许取** ★ "
        "★**满足 1.00mm 先例的允许区间**: [0.80..8.50] / [11.50..12.93] / [17.07..29.20] ⇒ **默认取 Y=12.00** (★落在第二段正中, 且是现行已在盘的落位 ⇒ ★**改落位 = 改板, 属整链重出第 1 步, 本单不做**★) ★ "
        "★**证据**: `HW/iss121_mic_magnet_check.py` rc=0 · [F] 段敏感度 · main 2026-11-15 21:2x 独立复核通过 (ISS-195 已签 verified) ★",
        "HW/iss121_mic_magnet_check.py · HW/ISS121_MIC_MAGNET_POSITION.md",
    ),
}

# ★升级到老板桶的 1 条 (★main 不替老板决定★)
ESCALATE = {
    "key": "iss206_mech_claim_mainboard_len_carrier_direct_scheme_choice",
    "to": "boss",
    "waiting_on": "boss",
    "due": "2026-11-18",
    "since": "2026-11-15",
    "item": (
        "★**【2026-11-15 21:3x main 升级给老板 · 方案取舍 = 老板级, main 不代决】** ★\n"
        "★**题**: SoM 载板形态取哪一套? —— `MECH/SOC_CARRIER_EVAL.md` §3/§5/§7 明确 **A = SoM 直接焊 (76mm)** 与 **B = 载板 (69mm)** 是**两套互斥架构**, 本分片 `interface_claims` 两条 claim value (69mm / 76mm) 都还挂着 ⇒ ★**结构侧不敢自己选, 选了就是替架构拍板** ★\n"
        "★**main 的建议默认值 = 维持 B (载板 69mm)**: ① ★**demo 板用的是 BTB 座 (J_SOM_P2/P4), 不是直焊** ⇒ ★**改直焊 = 整链重出第 1 步之外还要再加一次板级改动** ⇒ ★**代价与 demo 主线无关** ★ ② ★**A (直焊) 省一层厚度, 但换芯 (RK3572) 已经把载板彻底换掉了 ⇒ ★**再叠一次载板形态变更 = 两次变更叠加, 风险不可控** ★ ③ ★**69mm 是当前分片与文档里已定版的那个** ⇒ ★**维持 = 零改动** ★\n"
        "★**不拍板的后果**: ★**结构侧两条 claim 继续并存 (冲突 0 但没人敢动)** ⇒ ★**ISS-198/ISS-203/ISS-206 这类【接口契约侧】的单没法彻底收口** ⇒ ★**demo 板不受影响 (它走 BTB 座), 但整机结构方案无法冻结** ★\n"
        "★**依据**: `MECH/SOC_CARRIER_EVAL.md` §3/§5/§7 · `state/fragments/mech.yaml` 的 `mainboard_len_carrier` claim × 2 · ★**证据等级 [实测] (三份文档里就是这个数, main 已逐条核过)** ★\n"
        "★**注**: ★**这是【唯一】因为本轮交卷而新增的老板待拍板项** ⇒ ★**C 段 36 → 37** ★"
    ),
}


def main():
    def mutate(d):
        d.setdefault("answers", [])
        have = {a.get("key") for a in d["answers"]}
        added = []
        for k, (to, value, ref) in ANSWERS.items():
            if k in have:
                continue
            d["answers"].append({"key": k, "to": to, "value": value, "ref": ref})
            added.append(k)
        d.setdefault("needs_from", [])
        if not any(n.get("key") == ESCALATE["key"] for n in d["needs_from"]):
            d["needs_from"].append(dict(ESCALATE))
            added.append(ESCALATE["key"] + " → boss")
        print("落账 %d 条:" % len(added))
        for a in added:
            print("  ", a)

    update_fragment("main", mutate)


if __name__ == "__main__":
    main()
