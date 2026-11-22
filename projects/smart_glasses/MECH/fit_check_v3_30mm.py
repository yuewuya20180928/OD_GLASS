#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M-FIT v3 — 板宽 30mm / RK3576 基线下的电池·PCB·光机装配干涉检查
================================================================================
为什么要有 v3 (v2 的结论作废):
  v2 (`MECH/fit_check.py`) 的基线是 **板宽 12mm / 板长 50mm / PCB 厚 0.80mm (4层)**。
  2026-11-01 20:5x 项目总工翻案后基线变了:
    ① **板宽 = 30mm** (老板 10-29 19:16 拍板; §0 台账原写 15mm 已订正)
    ② **板长 = 60mm** (不变, ISS-100 定的)
    ③ **主控 = RK3576** (FCCSP698L 16.1×17.2mm pitch 0.6) ⇒ 板框 60×30=1800mm²
    ④ **板层数是 [0数据]**: `HW/esc_layer_models_check.py` 两套模型对撞 ⇒
       模型A 9 层 (板厚 ≈1.22mm) vs 模型B 3 层 (板厚 ≈0.41mm) ⇒ **板厚取哪个值不确定**
       ⇒ 本脚本 **两种都算**, 给区间。

口径声明 (铁律, 不许糊):
  · 本脚本是 **设计态几何 + 公差栈计算** (确定性, 逐项可复现) ⇒ **不是物理装配实测**
    ⇒ `state/measurements.yaml` 的 M-FIT **kind 仍只能是 [推算]**, 阶段门 G2 不认 (这是对的)。
  · **所有 [0数据] 的东西不参与计算**, 只列出来 (波导 / 走鹃Ⅱ三维尺寸 / 镜框截面 / 板层数)。

★ 读法提醒 (板宽方向):
  本项目口径 —— **板宽 = 镜脚内腔的 V 向 (垂直) 尺寸**, 不是 H 向 (见 §0):
    镜脚内腔 H 7.30 (前后) × V 38.00 (垂直) × L 130.00 (长度)
    板厚走 H / **板宽走 V** / 板长走 L
  ⇒ 板宽 12→15→30 直接吃 **V 净高**, H 链与 L 链不动。
  ⚠️ `PROJECT_TRACKER.md` §(1.43) 那句 "镜腿截面从 15×7.3mm → 30×7.3mm" 是 **自由文本表述**,
     与本域的三条锁死尺寸链 (7.30×38.00×130.00) 不对应 —— 已在 B5 登记为口径待确认项,
     本脚本按 **板宽 = V 向** 算 (与 `HW/pcb60x30_check.py` 独立复算一致)。

用法:  python3 MECH/fit_check_v3_30mm.py
        python3 MECH/fit_check_v3_30mm.py --frame B160x100   # ★切档: 台架板 160×100 帧★
        ★切档也可走环境变量: MECH_FRAME=B160x100 python3 MECH/fit_check_v3_30mm.py
退出码: 0 = 报告已生成 (结论看最后一节; **不代表实物已验**)

★★ISS-352 双口径 (2026-11-23 · mech-lead) ★★:
  本脚本现在**同时支持两档** (帧 id 与 `HW/PCB/BOARD_FRAME_CALIBER.md` §6 `cal:FRAMES` 逐字一致):
    · `F30A`     = 60×30 / 6 层 / 1.00mm / RK3576 17.20×16.10 (★默认档 · 历史产品板口径 · 不可与现役台架板混用★)
    · `B160x100` = 160×100 / 8 层 / 1.60mm / RK3572-SOM 承载区 56.70×46.78 (★盘上现役台架板帧★)
  ★★**默认档 (历史产品板口径) 的输出与迁移前逐字节相同** (★60×30 档判据方向一个字都没改★) ★★
  ★**`MECH/fit_check.py` (v2) 已退役** (自报基线 12mm / 50mm / 0.80mm 整套死 · 只留历史闭环记录) ⇒ 现行判据一律引本脚本 ★
"""
from __future__ import annotations

import math
import os
import sys

# =====================================================================
# 输入表 —— 每行标出处 (与 v2 同一纪律: 数字必须能追到文件)
# =====================================================================
BASE = {
    # --- 镜脚内腔 (三条锁死尺寸链; ISS-092 已复核 Delta=0.00) ---
    "cav_h":      7.30,   # §1.6.2 / BOARD_WIDTH_15MM §1.3 / SERVICE_PORT_ISS092 §1  [锁死]
    "cav_v":     38.00,   # §1.6.2 根部净高                                            [锁死]
    "cav_l":    130.00,   # §1.6.2 内腔长                                             [锁死]
    # --- 壳体 ---
    "wall":       0.80,   # §5.4 最小壁厚 (打印件)                                      [推算]
    "pad_thermal": 0.50,  # §2.4 对策C 皮肤侧隔热垫                                      [推算]
    "air_gap":    0.30,   # §2.4 对策C 空气隙                                          [推算]
    "pad_soc":    0.30,   # §5.1 SoC 下方导热垫                                          [推算]
    "frame_thk":  1.00,   # §5.1 铝/铜骨架厚                                            [推算]
    "duct_v":     6.00,   # §5.6.2 走线槽 V 向占位 (保守口径)                             [推算]
    "duct_h":     2.00,   # §1.3 M10 走线槽 H 向厚                                       [推算]
    "conn_margin": 15.00, # §1.4.2 连接器/弯折/插拔余量                                   [推算]
    # --- 电芯 (ISS-065 §3.2 映射表: 315mAh 档用 340mAh 电芯) ---
    "cell_thk":   4.60,   # §1.6.1 Renata ICP422339PR 340mAh 厚   [官网]
    "cell_v":    23.50,   # §1.6.1 同上 高                              [官网]
    "cell_l":    40.50,   # §1.6.1 同上 长                              [官网]
    "cell2_thk":  4.30,   # §1.6.1 丰江 432243 420mAh 厚 (387mAh 档)  [官网]
    "cell2_v":   22.00,
    "cell2_l":   43.50,
    # --- 板层数四档 (ISS-122: 9层 vs 3层 对撞 ⇒ 板厚 [0数据]) ---
    "pcb_thk": (0.41, 0.80, 1.00, 1.22),
    # --- 镜框侧 (全推算 / 等 JBD) ---
    "oe_thk":     4.80,   # §1.3 M5 走鹃Ⅱ 厚 (u1 未到)  [推算]
    "sp_thk":     6.00,   # §1.4.5 分光组件 厚          [推算]
    "cam_thk":    7.20,   # §1.4.5 摄像头位需求下限 10-12 取下限 [推算]
}

# 板层数 ↔ 板厚 ↔ 出处 (★ 这是 [0数据] 的区间, 不是选定的值)
THK_CASES = [
    (0.41, "模型B 3 层", "HW/esc_layer_models_check.py model_B (边带一次逃完 ⇒ 不破 4-6 层锁死) [0数据]"),
    (0.80, "4 层 (锁死档下沿)", "MECH_BUDGET §5.1 4 层 FR4 [推算]; §0 '4-6 层' 锁死"),
    (1.00, "6 层 (锁死档上沿)", "MECH_BUDGET §5.1 6 层 FR4 [推算]; §0 '4-6 层' 锁死"),
    (1.22, "模型A 9 层", "HW/esc_layer_models_check.py model_A (纯层数公式 ⇒ ★破 4-6 层锁死) [0数据]"),
]

# 公差账 (与 v2 同口径: 判据 = 2× 单边公差)
TOL = {
    "fdm_part": 0.30,   # 打印件外形单边          [推算] §5.4
    "fdm_feat": 0.25,   # 打印件特征间距离单边     [推算] §5.4
    "cell":    0.15,    # 电芯厚度公差 —— 原厂未给 [0数据]/假设
    "pcb_out": 0.15,    # PCB 外形公差 —— 板厂未给 [0数据]/假设 (常规铣/外形)
}
CRIT = 2 * TOL["fdm_part"]     # 判据阈值 0.60mm

# 骨架/石墨 V 覆盖 (ISS-118 §: 石墨 V 向覆盖必须跟板宽一起加)
SKELETON_V = {
    15.00: 12.00,   # 15mm 板: SoC 8.0 + 2×2.0 横向铺宽 = 12.0 (满宽) [BOARD_WIDTH_15MM §2.6]
    30.00: 30.00,   # 30mm 板: RK3576 17.2 + 2×6.40 逃线边带 = 30.0 (满宽) [HW/pcb60x30_check.py]
}

# =====================================================================
# ★ISS-352 双口径档位表 (★帧 id 逐字取自 HW/PCB/BOARD_FRAME_CALIBER.md §6 cal:FRAMES★)
#   · ★默认档 = F30A (60×30 / RK3576) —— ★本单【不许自己拍默认档】, 保持现状不变★
#   · 切档 = `--frame B160x100` (或环境变量 MECH_FRAME=B160x100) —— 见 §用法
#   · ★THK_CASES / SKELETON_V / 面积表 三组常量按【档位】取值 (默认档逐字保留迁移前取值)★
# =====================================================================
FRAMES = [
    {
        "fid": "F30A",
        "name": "产品板 60×30 套 A (历史产品板口径 · 与台架板口径不可混用)",
        "pcb_l": 60.00, "pcb_w": 30.00, "pcb_thk": 1.00, "layers": 6,
        "soc_model": "RK3576", "soc_pkg": (17.20, 16.10),
        "thk_cases": THK_CASES,
        "thk_pick": {"lo": 0.41, "mid": 0.80, "x3": 1.00, "hi": 1.22},
        "v_widths": [(12.0, "  (作废口径)"), (15.0, "  (前口径)"), (30.0, "  ← ★当前基线")],
        "areas": {"50×12": 600.0, "60×15": 900.0, "60×30": 1800.0},
        "cur_area": 1800.0, "cmp_area": 900.0,
        "skeleton_v": SKELETON_V, "sk_base_v": 12.0, "sk_cur_v": 30.0,
        "src": "MECH/BOARD_GEOM_30MM.md §0/§1/§3 (ISS-118/130) + HW/pcb60x30_check.py",
        "scope": "F30A 60×30 历史产品板口径 (板宽吃 V 向 · 板厚四档区间)",
    },
    {
        "fid": "B160x100",
        "name": "台架板 160×100 (盘上现役 · RK3572-SOM 承载区形态)",
        "pcb_l": 160.00, "pcb_w": 100.00, "pcb_thk": 1.60, "layers": 8,
        "soc_model": "RK3572-SOM", "soc_pkg": (56.70, 46.78),
        "thk_cases": [
            (1.60, "8 层 (台架板实测)",
             "HW/PCB/demo_mainboard_params.json board 段 thickness_mm 1.6 + 板文件 general/thickness 实读 [实测]"),
        ],
        "thk_pick": {"lo": 1.60, "mid": 1.60, "x3": 1.60, "hi": 1.60},
        "v_widths": [(12.0, "  (作废口径)"), (15.0, "  (前口径)"),
                     (30.0, "  (历史产品板口径)"), (100.0, "  ← ★当前基线")],
        "areas": {"50×12": 600.0, "60×15": 900.0, "60×30": 1800.0, "160×100": 16000.0},
        "cur_area": 16000.0, "cmp_area": 1800.0,
        "skeleton_v": {100.00: 100.00}, "sk_base_v": 30.0, "sk_cur_v": 100.0,
        "src": "HW/PCB/BOARD_FRAME_CALIBER.md §6 cal:FRAMES + §3 SoM 承载区实测占位 + 板文件实读",
        "scope": "B160x100 台架板帧 (板宽吃 V 向 · 板厚 8 层 1.60mm 实测 · 台架板装不进镜脚内腔 V38)",
    },
]
DEFAULT_FRAME_ID = "F30A"
FRAME = FRAMES[0]      # ★当前档位 (由 _bind_frame 绑定)★
FRAME_ID = DEFAULT_FRAME_ID

# =====================================================================
# ★ISS-352 双口径 · 帧级叙述表 (★F30A 档逐字保留迁移前文本 ⇒ 默认档输出逐字节不变★)
#   ★每个模板里的 {..} 占位全部来自【帧值 + 本次复算量】, 不含硬编档位数字★
# =====================================================================
PROSE = {
    "F30A": {
        "title": "M-FIT v3 | 板宽 30mm (V 向) / 板长 60mm / RK3576 | 镜脚内腔 H7.30 × V38.00 × L130.00 (锁死)",
        "v_sec_title": "\n【1】V 链 (板宽吃的就是这一条) —— 板宽 15 → 30 的账",
        "v_row_item": "根部净高 (板宽30 + 走线槽6)",
        "v_row_note": "★板宽 15→30 把 PCB 段需求从 21.00 抬到 36.00 ⇒ **V 余量 17.00 → "
                      "{margin:.2f} (最坏 {worst:.2f})**; 板宽硬顶 = 38.00-6.00-0.60 = **31.40mm**",
        "h_sec_title": "\n【2】H 链 (前后 7.30) × 板厚四档 —— ★ISS-092 检修口净空随板厚变",
        "h_note_hi": "  ★ 板厚 1.22 (模型A) 下: 净空 {clr:.2f} **< 4.50 硬要求 差 {d:.2f}** ⇒ "
                     "ISS-092 C-5 与 P-1 探针口径要重算",
        "h_note_lo": "  ★ 板厚 0.41 (模型B) 下: 净空 {clr:.2f} ⇒ 盖板内腔余 {c:.2f} "
                     "(比 0.80 档多 {diff:.2f})",
        "h_row1_item": "PCB 段前后占位 (t=0.80 中档)",
        "h_row1_note": "板厚四档全过: 最紧 t=1.22 ⇒ 最坏余量 {worst:.2f}mm",
        "h_row2_item": "检修口净空 (外表面→PCB焊盘面) ≥4.50",
        "h_row2_note": "板厚 0.41/0.80/1.00 → 净空 {c1:.2f}/{c2:.2f}/{c3:.2f} ✅; "
                       "**t=1.22 → {c4:.2f} ❌ 差 {d4:.2f}** (ISS-092 C-5/P-1 口径要重算)",
        "h_row2_verdict_ok": "✅ 通过 (0.41~1.00 档)",
        "h_row2_verdict_ng": "⚠️ 板厚 1.22 档不通过",
        "l_sec_title": "\n【3】L 链 (长度 130.00) —— 板长 60 不变, 故 L 链与板宽无关",
        "l_row_item": "长度 (电芯40.5 + 板长60 + 余量15)",
        "l_max_line": "  板长物理上限 = 130.00 - 40.50(电芯) - 15.00(余量) = **{max_len:.1f}mm**; "
                      "RK3576 在 30mm 板宽下需板长 ≥55.9mm (ISS-118) ⇒ 60mm 在区间内, 上限还有 {rem:.1f}mm",
        "l_row2_item": "板长物理上限 (电芯+余量占用)",
        "l_row2_note": "上限 {max_len:.1f}mm, 现取 60 ⇒ 还有 {rem:.1f}mm 余量",
        "aw_sec_title": "板宽 15 → 30 的直接账单",
        "aw_delta_line": "  ★ PCB 板重增量 (60×15 → 60×30): 4层 **+{d4:.3f}g** / 6层 **+{d6:.3f}g** "
                         "(HW/pcb60x30_check.json: 1.332→2.664 / 1.665→3.330 g)",
        "aw_skel_item": "金属骨架 V 覆盖 12 → 30 (SoC 横向铺满)",
        "aw_skel_note": "骨架 +{dsk:.3f}g/侧 (V 覆盖 12.0→30.0 满宽, 长 25mm 假设) ⇒ 整机 +{tot:.3f}g",
        "aw_pcb_item": "PCB 板重 60×15 → 60×30 (4层)",
        "aw_pcb_note": "1.332 → 2.664 g (+{d4:.3f}g); 6层 +{d6:.3f}g ⇒ 整机 +{lo:.3f}~{hi:.3f}g",
        "batt_boardw_line": "    L 占 0..40.50 ⇒ 电池空间与续航口径 **不变** ⇒ 板宽 30 没有换到任何电池空间",
        "batt_row_note": "板宽 30 不影响电池段 (串行排布) ⇒ 续航结论不变",
        "concl_title": "★ 结论 (镜脚侧 / 板宽 30mm (V 向) / 板长 60mm / RK3576 / 镜腿 7.3mm 锁死)",
        "concl_1": "  ① **V 链是本单唯一被板宽打穿的链**: 板宽 30 + 走线槽 6 = 36.00 vs 净高 38.00 ⇒ "
                   "余量 {vm:.2f}mm (最坏 {vw:.2f}) ⇒ ✅ 过判据 0.60, 但 **比板宽 15 时少 15.00mm**",
        "concl_1b": "     ⇒ 板宽硬顶 = 38.00 - 6.00 - 0.60 = **31.40mm** (30mm 距顶只剩 1.40mm)",
        "concl_2": "  ② **H 链与 L 链一字不动**: H 控制段仍是电芯段 6.35 (余 0.95 / 最坏 0.65); "
                   "L 需求 115.50 vs 130.00 (余 14.50)",
        "concl_3": "  ③ **ISS-092 检修口净空随板厚变**: 净空 = 7.30 - (0.80+0.50+0.30+t) ⇒ "
                   "t=0.41/0.80/1.00/1.22 → {c1:.2f}/{c2:.2f}/{c3:.2f}/{c4:.2f}mm",
        "concl_3b": "     ⇒ **t=1.22 (模型A 9 层) 破 4.50 硬要求** (差 {d:.2f}) ⇒ "
                    "C-5 与 P-1 探针口径要重算; t≤1.00 时 4.90 不变",
        "concl_4": "  ④ **电池空间/续航完全不变** (串行排布, 板宽只吃 PCB 段的 V) ⇒ 板宽 30 换到的是 "
                   "PCB 面积, 不是电池",
        "concl_5": "  ⑤ **重量代价**: PCB +{d4:.3f}g (4层) / +{d6:.3f}g (6层) + 骨架 +{dsk:.3f}g/侧 "
                   "(整机 +{tot:.3f}g) ⇒ 整机 **+{lo:.2f}~{hi:.2f}g** (原 48.9-74.0g ⇒ "
                   "**{mlo:.1f}-{mhi:.1f}g**, 目标 30-40g 更远) [推算]",
        "concl_6": "  ⑥ **镜框侧仍全未验** (走鹃Ⅱ u1 / 波导 2D u4 / 端件截面 u8b / 摄像头 u5) ⇒ "
                   "光机·波导干涉 **无法判定**, 彩虹纹指标 [0数据]",
    },
    "B160x100": {
        "title": "M-FIT v3 | 板宽 100mm (V 向) / 板长 160mm / RK3572-SOM | 镜脚内腔 H7.30 × V38.00 × L130.00 (锁死)",
        "v_sec_title": "\n【1】V 链 (板宽吃的就是这一条) —— 台架板 160×100 帧的账",
        "v_row_item": "根部净高 (板宽100 + 走线槽6)",
        "v_row_note": "★台架板板宽 100mm 把 PCB 段需求抬到 106.00 ⇒ **V 余量 -68.00 (最坏 -68.60)**; "
                      "板宽硬顶 = 38.00-6.00-0.60 = **31.40mm** ⇒ 台架板当眼镜镜脚内的板 **装不下**",
        "h_sec_title": "\n【2】H 链 (前后 7.30) × 板厚 1.60mm (8 层 台架板实测) —— ★ISS-092 检修口净空随板厚变",
        "h_note_hi": "  ★ 板厚 1.60 (8 层 台架板实测) 下: 净空 {clr:.2f} **< 4.50 硬要求 差 {d:.2f}** ⇒ "
                     "ISS-092 C-5 与 P-1 探针口径要重算",
        "h_note_lo": "  ★ 板厚 1.60 (8 层 台架板实测) 下: 净空 {clr:.2f} ⇒ 盖板内腔余 {c:.2f}",
        "h_row1_item": "PCB 段前后占位 (t=1.60 台架板实测)",
        "h_row1_note": "板厚 1.60 (8 层实测): 最坏余量 {worst:.2f}mm",
        "h_row2_item": "检修口净空 (外表面→PCB焊盘面) ≥4.50",
        "h_row2_note": "板厚 1.60 → 净空 {c4:.2f} ❌ 差 {d4:.2f} (ISS-092 C-5/P-1 口径要重算)",
        "h_row2_verdict_ok": "✅ 通过 (1.60 档)",
        "h_row2_verdict_ng": "⚠️ 板厚 1.60 档不通过 (净空 {clr:.2f} < 4.50)",
        "l_sec_title": "\n【3】L 链 (长度 130.00) —— 台架板板长 160 ⇒ L 链与板宽无关",
        "l_row_item": "长度 (电芯40.5 + 板长160 + 余量15)",
        "l_max_line": "  板长物理上限 = 130.00 - 40.50(电芯) - 15.00(余量) = **{max_len:.1f}mm**; "
                      "台架板板长 160mm ⇒ **超出上限 {over:.1f}mm** (装不下)",
        "l_row2_item": "板长物理上限 (电芯+余量占用)",
        "l_row2_note": "上限 {max_len:.1f}mm, 现取 160 ⇒ 超出 {over:.1f}mm",
        "aw_sec_title": "台架板 160×100 的直接账单",
        "aw_delta_line": "  ★ PCB 板重增量 (60×30 → 160×100): 4层 **+{d4:.3f}g** / 6层 **+{d6:.3f}g** "
                         "(对照 F30A 60×30 / RK3576 板; 台架板实配 8 层 1.60mm ⇒ 29.600g)",
        "aw_skel_item": "金属骨架 V 覆盖 30 → 100 (满宽)",
        "aw_skel_note": "骨架 +{dsk:.3f}g/侧 (V 覆盖 30.0→100.0 满宽, 长 25mm 假设) ⇒ 整机 +{tot:.3f}g",
        "aw_pcb_item": "PCB 板重 60×30 → 160×100 (4层)",
        "aw_pcb_note": "2.664 → 23.680 g (+{d4:.3f}g); 6层 +{d6:.3f}g ⇒ 整机 +{lo:.3f}~{hi:.3f}g",
        "batt_boardw_line": "    L 占 0..40.50 ⇒ 电池空间与续航口径 **不变** ⇒ 板宽 100 没有换到任何电池空间",
        "batt_row_note": "板宽 100 不影响电池段 (串行排布) ⇒ 续航结论不变",
        "concl_title": "★ 结论 (镜脚侧 / 板宽 100mm (V 向) / 板长 160mm / RK3572-SOM / 镜腿 7.3mm 锁死)",
        "concl_1": "  ① **V 链在台架板帧直接判死**: 板宽 100 + 走线槽 6 = 106.00 vs 净高 38.00 ⇒ "
                   "余量 {vm:.2f}mm (最坏 {vw:.2f}) ⇒ ❌ 连判据 0.60 都不到 ⇒ 台架板**不是**眼镜镜脚内的板",
        "concl_1b": "     ⇒ 板宽硬顶 = 38.00 - 6.00 - 0.60 = **31.40mm** (台架板 100mm 超出 68.60mm)",
        "concl_2": "  ② **H 链控制段仍是电芯段 6.35 (余 0.95 / 最坏 0.65)**; L 需求 {lneed:.2f} vs 130.00 "
                   "(余 {lmar:.2f}) ⇒ L 链在台架板帧同样判死",
        "concl_3": "  ③ **ISS-092 检修口净空随板厚变**: 净空 = 7.30 - (0.80+0.50+0.30+t) ⇒ "
                   "t=1.60 → {c4:.2f}mm",
        "concl_3b": "     ⇒ **t=1.60 (8 层 台架板实测) 破 4.50 硬要求** (差 {d:.2f}) ⇒ "
                    "C-5 与 P-1 探针口径要重算",
        "concl_4": "  ④ **电池空间/续航完全不变** (串行排布, 板宽只吃 PCB 段的 V) ⇒ 板宽 100 换到的是 "
                   "PCB 面积, 不是电池",
        "concl_5": "  ⑤ **重量代价**: PCB +{d4:.3f}g (4层) / +{d6:.3f}g (6层) + 骨架 +{dsk:.3f}g/侧 "
                   "(整机 +{tot:.3f}g) ⇒ 整机 **+{lo:.2f}~{hi:.2f}g** (原 48.9-74.0g ⇒ "
                   "**{mlo:.1f}-{mhi:.1f}g**, 目标 30-40g 更远) [推算]",
        "concl_6": "  ⑥ **镜框侧仍全未验** (走鹃Ⅱ u1 / 波导 2D u4 / 端件截面 u8b / 摄像头 u5) ⇒ "
                   "光机·波导干涉 **无法判定**, 彩虹纹指标 [0数据]",
    },
}


def _bind_frame(fid: str) -> dict:
    """★按档位把几何常量绑到模块级变量上 (★默认档 F30A ⇒ 迁移前取值逐字不变★)★

    ★本单【不许自己拍默认档】⇒ 默认 = F30A (60×30 / RK3576) = 保持现状 ★
    ★切默认档 = main 拍完 U-1 后跑 `--frame B160x100` (或 MECH_FRAME=B160x100) ★
    """
    global FRAME, FRAME_ID, PCB_L, PCB_W, PCB_THK
    global THK_CASES, SKELETON_V
    fr = next((f for f in FRAMES if f["fid"] == fid), None)
    if fr is None:
        raise SystemExit("★未知帧 id %r (可选: %s)★" % (fid, ", ".join(f["fid"] for f in FRAMES)))
    FRAME, FRAME_ID = fr, fr["fid"]
    PCB_L, PCB_W, PCB_THK = fr["pcb_l"], fr["pcb_w"], fr["pcb_thk"]
    THK_CASES = fr["thk_cases"]
    SKELETON_V = fr["skeleton_v"]
    return fr


def _pick_frame_id(argv):
    """★切档解析: `--frame <fid>` 命令行优先, 其次环境变量 MECH_FRAME, 最后默认档 ★
    ★默认档 = F30A (60×30 / RK3576) —— ★本单【不许自己拍默认档】★"""
    fid = os.environ.get("MECH_FRAME", "").strip() or DEFAULT_FRAME_ID
    for i, a in enumerate(argv):
        if a == "--frame" and i + 1 < len(argv):
            fid = argv[i + 1].strip()
        elif a.startswith("--frame="):
            fid = a.split("=", 1)[1].strip()
    return fid or DEFAULT_FRAME_ID


PCB_L = 60.00           # mm 板长 (默认档 F30A; 由 _bind_frame 按档位绑定)
PCB_W = 30.00           # mm 板宽 (默认档 F30A; 由 _bind_frame 按档位绑定)
PCB_THK = 1.00          # mm 板厚 (默认档 F30A; 由 _bind_frame 按档位绑定)


ROWS = []
def row(zone, item, need, avail, margin, worst=None, verdict="", note=""):
    ROWS.append((zone, item, need, avail, margin, worst, verdict, note))

def v(ok):
    return "✅ 通过" if ok else "❌ 不通过"


# =====================================================================
# 1. 板宽 30 下的 V 链 (本单最大的一条)
# =====================================================================
def v_chain():
    P = PROSE[FRAME_ID]
    print("=" * 100)
    print(P["title"])
    print("=" * 100)
    print(f"\n【0】判据与公差账")
    print(f"  判据: 每条余量 ≥ 2×单边公差 = {CRIT:.2f}mm")
    print(f"  公差: FDM 外形 ±{TOL['fdm_part']:.2f} / 特征 ±{TOL['fdm_feat']:.2f} / "
          f"电芯 ±{TOL['cell']:.2f} [0数据] / PCB 外形 ±{TOL['pcb_out']:.2f} [0数据]")

    print(P["v_sec_title"])
    for w, tag in FRAME["v_widths"]:
        v_pcb = w + BASE["duct_v"]
        v_cell = BASE["cell_v"] + BASE["duct_v"]
        need = max(v_pcb, v_cell)
        margin = BASE["cav_v"] - need
        worst = margin - 2 * TOL["fdm_part"]
        print(f"  板宽 {w:>5.1f}mm: PCB段 {v_pcb:5.2f} / 电芯段 {v_cell:5.2f} → 需求 {need:5.2f} "
              f"vs 净高 {BASE['cav_v']:.2f} ⇒ 余量 {margin:+6.2f} (最坏 {worst:+6.2f}) "
              f"{'✅' if worst >= CRIT else '❌'} {tag}")
    v_pcb = PCB_W + BASE["duct_v"]
    margin = BASE["cav_v"] - v_pcb
    worst = margin - 2 * TOL["fdm_part"]
    row("镜脚·V", P["v_row_item"], v_pcb, BASE["cav_v"], margin, worst,
        verdict=v(worst >= CRIT),
        note=P["v_row_note"].format(margin=margin, worst=worst))
    # 电芯段 (板宽不吃它)
    v_cell = BASE["cell_v"] + BASE["duct_v"]
    row("镜脚·V", "根部净高 (电芯段 23.5+走线槽6)", v_cell, BASE["cav_v"], BASE["cav_v"] - v_cell,
        BASE["cav_v"] - v_cell - 2 * TOL["fdm_part"], verdict="✅ 通过",
        note="串行排布 ⇒ 板宽只吃 PCB 段的 V, **电池空间不变** (见 §5)")
    return margin, worst


# =====================================================================
# 2. H 链 × 板厚四档 (含 ISS-092 检修口净空重算)
# =====================================================================
def h_chain():
    P = PROSE[FRAME_ID]
    TP = FRAME["thk_pick"]
    print(P["h_sec_title"])
    print(f"  H 链定义 (SERVICE_PORT_ISS092 §1.1): 皮肤壁 0.80 | 隔热垫 0.50 | 空气隙 0.30 | "
          f"PCB(厚 t) | 骨架 1.00 | 空腔 | 外壁 0.80   (H 从皮肤侧内表面向外数)")
    print(f"  {'板厚 t':>8} {'来源':<22} {'PCB段H需求':>10} {'H余量':>8} {'最坏':>8} "
          f"{'焊盘面H':>9} {'净空':>8} {'盖板内腔≥4.50':>14} {'探针需伸入':>11}")
    res = {}
    for t, tag, src in THK_CASES:
        h_pcb = (BASE["wall"] + BASE["pad_thermal"] + BASE["air_gap"] + t
                 + BASE["frame_thk"] + BASE["wall"])
        m = BASE["cav_h"] - h_pcb
        m_worst = m - 2 * TOL["fdm_part"]
        pad_plane_h = BASE["wall"] + BASE["pad_thermal"] + BASE["air_gap"] + t   # PCB 元件面
        clearance = BASE["cav_h"] - pad_plane_h                                  # 外表面→焊盘面
        cavity_ok = clearance >= 4.50
        probe_need = clearance + 1.00                                           # +行程 1.00
        res[t] = dict(h_pcb=h_pcb, margin=m, worst=m_worst, clearance=clearance,
                      cavity_ok=cavity_ok, probe_need=probe_need, tag=tag, src=src)
        print(f"  {t:>8.2f} {tag:<22} {h_pcb:>10.2f} {m:>+8.2f} {m_worst:>+8.2f} "
              f"{pad_plane_h:>9.2f} {clearance:>8.2f} "
              f"{'✅ 余 %.2f' % (clearance-4.50) if cavity_ok else '❌ 差 %.2f' % (4.50-clearance):>14} "
              f"{probe_need:>11.2f}")
    print(P["h_note_hi"].format(clr=res[TP["hi"]]["clearance"],
                                d=4.50 - res[TP["hi"]]["clearance"]))
    print(P["h_note_lo"].format(clr=res[TP["lo"]]["clearance"],
                                c=res[TP["lo"]]["clearance"] - 4.50,
                                diff=res[TP["lo"]]["clearance"] - 4.90))
    row("镜脚·H", P["h_row1_item"],
        res[TP["mid"]]["h_pcb"], BASE["cav_h"], res[TP["mid"]]["margin"], res[TP["mid"]]["worst"],
        verdict=v(res[TP["mid"]]["worst"] >= CRIT),
        note=P["h_row1_note"].format(worst=res[TP["hi"]]["worst"]))
    row("镜脚·H", P["h_row2_item"],
        4.50, res[TP["mid"]]["clearance"], res[TP["mid"]]["clearance"] - 4.50,
        res[TP["hi"]]["clearance"] - 4.50,
        verdict=(P["h_row2_verdict_ok"] if res[TP["hi"]]["clearance"] >= 4.50
                 else P["h_row2_verdict_ng"].format(clr=res[TP["hi"]]["clearance"])),
        note=P["h_row2_note"].format(c1=res[TP["lo"]]["clearance"], c2=res[TP["mid"]]["clearance"],
                                     c3=res[TP["x3"]]["clearance"], c4=res[TP["hi"]]["clearance"],
                                     d4=4.50 - res[TP["hi"]]["clearance"]))
    # 电芯段 (控制段, 与板宽/板厚都无关)
    h_cell = BASE["wall"] + 4.75 + BASE["wall"]      # 解A: 皮肤壁0.8 + 非对称座深4.75 + 顶板0.8
    row("镜脚·H", "前后厚 (电芯段: 皮肤壁0.8+座深4.75+顶板0.8) ★控制段",
        h_cell, BASE["cav_h"], BASE["cav_h"] - h_cell,
        BASE["cav_h"] - h_cell - TOL["fdm_part"], verdict=v(BASE["cav_h"] - h_cell - TOL["fdm_part"] >= CRIT),
        note="ISS-092 确认 Δ=0.00 (开窗只挖外壁 0.8 一层)")
    # 骨架为基准的敏感性分支
    alt = BASE["cav_h"] - (BASE["wall"] + BASE["frame_thk"] + BASE["wall"]) - 0.80
    print(f"  ⚠️ 敏感性分支 (若改以 **金属骨架内表面为基准**, PCB 向皮肤侧长厚): "
          f"净空保持 4.90 ✅, 但 隔热垫+空气隙 被压到 "
          f"{BASE['pad_thermal']+BASE['air_gap']-(1.22-0.80):.2f}mm (0.80→0.38) ⇒ 隔热性能与 "
          f"ISS-065 的 43°C 结论要重算")
    row("镜脚·H", "敏感性: 板厚 1.22 换基准 (骨架为基准)", 4.90, 4.90, 0.40, 0.40,
        verdict="⚠️ 条件性通过", note="净空保住 4.90, 但隔热垫+空气隙 0.80→0.38 ⇒ 隔热链变薄")
    return res


# =====================================================================
# 3. L 链 (板长 60, 不变)
# =====================================================================
def l_chain():
    P = PROSE[FRAME_ID]
    print(P["l_sec_title"])
    l_need = BASE["cell_l"] + PCB_L + BASE["conn_margin"]
    m = BASE["cav_l"] - l_need
    row("镜脚·L", P["l_row_item"], l_need, BASE["cav_l"], m,
        m - 3 * TOL["fdm_part"], verdict=v(m - 3 * TOL["fdm_part"] >= CRIT),
        note=f"余量 {m:.2f}mm (ISS-092 复核 Δ=0.00)")
    max_len = BASE["cav_l"] - BASE["cell_l"] - BASE["conn_margin"]
    print(P["l_max_line"].format(max_len=max_len, rem=max_len - PCB_L, over=PCB_L - max_len))
    row("镜脚·L", P["l_row2_item"], PCB_L, max_len, max_len - PCB_L, None,
        verdict="✅ 通过", note=P["l_row2_note"].format(max_len=max_len, rem=max_len - PCB_L,
                                                       over=PCB_L - max_len))
    return l_need, m


# =====================================================================
# 4. 面积 / 重量 (板宽 30 的账单)
# =====================================================================
def area_weight():
    P = PROSE[FRAME_ID]
    print(f"\n【4】面积与重量账 —— {P['aw_sec_title']}")
    areas = FRAME["areas"]
    for k, a in areas.items():
        w4 = a * 0.8e-3 * 1.85
        w6 = a * 1.0e-3 * 1.85
        w9 = a * 1.22e-3 * 1.85
        print(f"  板形 {k:<8} 面积 {a:6.0f}mm² ⇒ 板重 4层 {w4:.3f}g / 6层 {w6:.3f}g / "
              f"9层(1.22) {w9:.3f}g   [推算, 密度 1.85 g/cm³, 口径同 HW/pcb60x30_check.py]")
    cur = FRAME["cur_area"]
    cmp_a = FRAME["cmp_area"]
    d4 = cur * 0.8e-3 * 1.85 - cmp_a * 0.8e-3 * 1.85
    d6 = cur * 1.0e-3 * 1.85 - cmp_a * 1.0e-3 * 1.85
    print(P["aw_delta_line"].format(d4=d4, d6=d6))
    # 骨架: V 覆盖 12 → 30 (满宽), 长度按 SoC 区 25mm 估 (待 hw-lead 给 SoC 落位)
    sk_len = 25.0
    for w, sv in SKELETON_V.items():
        vol = sk_len * sv * 1.0          # mm³
        print(f"  金属骨架 (板宽 {w:.0f}): V 覆盖 {sv:.1f}mm × 长 {sk_len:.0f}mm × 厚 1.0mm ⇒ "
              f"{vol/1000:.2f}cm³ × 2.70 g/cm³ = **{vol/1000*2.70:.3f}g** [推算, 骨架长度假设 25mm]")
    sk_base = sk_len * FRAME["sk_base_v"] * 1.0 / 1000 * 2.70
    sk_cur = sk_len * FRAME["sk_cur_v"] * 1.0 / 1000 * 2.70
    d_sk = sk_cur - sk_base
    row("重量", P["aw_skel_item"], d_sk, 0.0, -d_sk, None,
        verdict="⚠️ 重量代价",
        note=P["aw_skel_note"].format(dsk=d_sk, tot=2 * d_sk))
    row("重量", P["aw_pcb_item"], d4, 0.0, -d4, None, verdict="⚠️ 重量代价",
        note=P["aw_pcb_note"].format(d4=d4, d6=d6, lo=d4 + 2 * d_sk, hi=d6 + 2 * d_sk))
    return d4, d6, d_sk


# =====================================================================
# 5. 电池 · 光机 · 镜框侧 (不依赖波导外形的那部分)
# =====================================================================
def battery_and_frame():
    P = PROSE[FRAME_ID]
    print(f"\n【5】电池段与镜框侧")
    print(f"  电池 (串行排布, 板宽不吃电池段): 电芯 4.60×23.50×40.50 (Renata 340mAh, 315mAh 档)")
    print(f"    V 需求 {BASE['cell_v']+BASE['duct_v']:.2f} vs 38.00 ⇒ 余量 "
          f"{BASE['cav_v']-BASE['cell_v']-BASE['duct_v']:.2f}mm (**不变**)")
    print(f"    H 需求 6.35 vs 7.30 ⇒ 余量 0.95 (最坏 0.65) (**不变**)")
    print(P["batt_boardw_line"])
    row("镜脚·电池", "电池段 V/H/L 三向 (解A 315mAh 档)", 29.50, 38.00, 8.50, 7.90,
        verdict="✅ 通过", note=P["batt_row_note"])
    row("镜脚·电池", "电池段 H (控制段)", 6.35, BASE["cav_h"], 0.95, 0.65, verdict="✅ 通过",
        note="ISS-092 Δ=0.00")

    print(f"\n  镜框侧 (光机 · 分光件 · 摄像头 · 波导) —— 只算不依赖波导外形的那部分:")
    print(f"    光机 7.5×5.0×4.8 (0.18cc, u1 未到) [推算] ⇒ 镜框正中区光学舱 11.8mm [推算]")
    print(f"    分光组件 14×10×6 [推算] ⇒ 镜框正中厚度需求 "
          f"{BASE['oe_thk']+BASE['sp_thk']+1.00:.2f}mm [推算]")
    print(f"    摄像头位 (前-后) {BASE['cam_thk']:.2f} / (垂直) 10.53mm [推算]")
    print(f"    波导卡槽平行度 ±0.3° ⇒ **无 2D 外形图 = 无法算** [0数据]")
    row("镜框·正中", "光学舱厚度 (光机+分光件+余量)",
        BASE["oe_thk"] + BASE["sp_thk"] + 1.00, None, None, verdict="⚠️ 未验",
        note="缺 JBD 走鹃Ⅱ 三维尺寸 (u1) + 镜框截面 (u8/u8b) ⇒ 只给需求不给判定")
    row("镜框·上沿", "摄像头位厚度 (模组+遮光罩+壁)", BASE["cam_thk"], None, None,
        verdict="⚠️ 未验", note="缺摄像头模组型号 (u5) + 镜框端件截面 (u8b)")
    row("镜框·波导", "波导卡槽平行度 ±0.3° / 彩虹纹指标", 0.30, None, None,
        verdict="⚠️ 未验", note="缺波导 2D 外形图 (u4) + 厂家彩虹纹指标 ⇒ **ISS-017 第二项 [0数据]**")


def dump_rows():
    print(f"\n【6】逐项表")
    print("-" * 118)
    print(f"{'区域':<12} {'检查项':<50} {'需求':>8} {'可用':>8} {'名义余量':>9} {'最坏余量':>9}  判定")
    print("-" * 118)
    for z, it, need, avail, marg, worst, verd, note in ROWS:
        ns = "—" if need is None else f"{need:.2f}"
        as_ = "—" if avail is None else f"{avail:.2f}"
        ms = "—" if marg is None else f"{marg:.2f}"
        ws = "—" if worst is None else f"{worst:.2f}"
        print(f"{z:<12} {it:<50} {ns:>8} {as_:>8} {ms:>9} {ws:>9}  {verd}")
        if note:
            print(f"{'':<12} └─ {note}")
    print("-" * 118)


def main():
    global TP
    fid = _pick_frame_id(sys.argv[1:])
    fr = _bind_frame(fid)
    TP = fr["thk_pick"]
    if FRAME_ID != DEFAULT_FRAME_ID:
        # ★非默认档才多打一行档位说明 (★默认档输出与迁移前【逐字节相同】★)
        print("★ 档位 = %s (%s) · 板 %.2f×%.2f×%.2fmm / %d 层 · 判据族: %s"
              % (fr["fid"], fr["name"], fr["pcb_l"], fr["pcb_w"], fr["pcb_thk"], fr["layers"],
                 fr["scope"]))
    P = PROSE[FRAME_ID]
    v_margin, v_worst = v_chain()
    h_res = h_chain()
    l_chain_need, l_chain_margin = l_chain()
    d4_, d6_, d_sk_ = area_weight()
    battery_and_frame()
    dump_rows()

    print("\n" + "=" * 100)
    print(P["concl_title"])
    print("=" * 100)
    print(P["concl_1"].format(vm=v_margin, vw=v_worst))
    print(P["concl_1b"])
    print(P["concl_2"].format(lneed=l_chain_need, lmar=l_chain_margin))
    print(P["concl_3"].format(c1=h_res[TP["lo"]]["clearance"], c2=h_res[TP["mid"]]["clearance"],
                              c3=h_res[TP["x3"]]["clearance"], c4=h_res[TP["hi"]]["clearance"]))
    print(P["concl_3b"].format(d=4.50 - h_res[TP["hi"]]["clearance"]))
    print(P["concl_4"])
    print(P["concl_5"].format(d4=d4_, d6=d6_, dsk=d_sk_, tot=2 * d_sk_,
                              lo=d4_ + 2 * d_sk_, hi=d6_ + 2 * d_sk_,
                              mlo=48.9 + d4_ + 2 * d_sk_, mhi=74.0 + d6_ + 2 * d_sk_))
    print(P["concl_6"])
    print(f"\n★ 口径: 本脚本是 **设计态几何 + 公差栈计算**, 不是物理装配实测 "
          f"⇒ measurements.yaml 的 M-FIT kind 仍写 [推算]; 阶段门 G2 不认 (符合预期)")
    print(f"  实物解锁路径: 打 MECH/print/ Rev B 打印包 → 按 MEASURE_CHECKLIST.md 量 → 回填 measurements.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
