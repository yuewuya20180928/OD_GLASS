#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M-FIT v2 — 镜脚侧装配余量闭环检查 (闭环 ISS-042)
=====================================================================
为什么有 v2:
  ISS-017 交卷时 v1 只报了 "前后余量 0.30mm" —— 与 FDM 单边公差 ±0.2~0.3mm
  **同量级**, 我自己判"临界 = 不通过"。老板 19:16 拍板 Q4 = 按需触发
  (电池按 340mAh 档起算, 镜腿 7.3mm) → 这条变成当前最严重的内部问题。

v2 加了 4 件事 (全部可复算):
  ① **公差判据**: 每条余量必须 ≥ 2× 单边公差 (FDM 0.30 → 0.60mm),
     并且同时报 **最坏情况 (对抗性) 余量** —— "名义余量" 单看会骗人。
  ② **候选解 ×4** 的前后/垂直/长度余量 (不再只给结论)。
  ③ **3 项条件性不通过** 的逐条解法 (叠放模型 / 充电板不移出 / ⌀2.0 H7)。
  ④ **对散热路径的影响**: 量化"金属骨架不得延伸进电池段"这条硬约束。

口径声明:
  · 本脚本是 **设计态几何 + 公差栈计算** (确定性, 逐项可复现) —— 它**不是物理装配实测**,
    所以 measurements.yaml 里 M-FIT 的 kind 仍只能写 [推算] (阶段门不认, 这是对的)。
  · 尺寸全部来自 MECH_BUDGET.md v1.1, 每条标了章节号; 本脚本**不改方案**, 只算余量。
  · **v1 → v2 的唯一口径修正**: 走线槽在垂直方向的占位取 **6.00mm**
    (MECH_BUDGET §5.6.2 表: 电池 23.5 + 走线槽 6 = 29.5; §1.4.2 正文写的 "3" 是笔误,
     §5.6.2 的表才是对外口径)。取 6.00 = 取保守值。

用法: python3 MECH/fit_check.py
退出码: 0 = 报告已生成 (结论看最后一节; 不代表实物已验)
"""
from __future__ import annotations

import math

# =====================================================================
# 输入表 —— 全部来自 MECH_BUDGET.md v1.1 (章节号 = 来源)
# =====================================================================
BASE = {
    # 镜脚内腔 (老板 19:16 Q4 锁死: 340mAh 档 / 镜腿 7.3mm)
    "cav_h":      7.30,     # §1.6.2 340档 镜脚前后厚  ← ** 镜腿外厚上限 (设计限) **
    "cav_v":     38.00,     # §1.6.2 340档 根部净高
    "cav_l":    130.00,     # §1.6.2 内腔长
    # 壳体
    "wall":       0.80,     # §5.4 最小壁厚 (0.4 喷嘴 × 2 圈 = 0.8 双向)
    "pad_thermal": 0.50,    # §2.4 对策 C 皮肤侧隔热垫
    "air_gap":    0.30,     # §2.4 对策 C 空气隙
    "seam":       0.20,     # 上下分壳合缝 (v1.1 未给 → 本脚本假设, 标 [推算])
    # 电芯
    "cell_thk":   4.60,     # §1.6.1 Renata ICP582035PR-01 340mAh 厚  [官网]
    "cell_v":    23.50,     # §1.6.1 同上 高
    "cell_l":    40.50,     # §1.6.1 同上 长
    "cell2_thk":  4.30,     # §1.6.1 丰江 432243 420mAh 厚 (解B 用)  [官网]
    "cell2_v":   22.00,     # §1.6.1 同上 高
    "cell2_l":   43.50,     # §1.6.1 同上 长
    # PCB (§5.1)
    "pcb_l":     50.00,     # §5.1 PCB 长
    "pcb_w":     12.00,     # §5.1 PCB 宽
    "pcb_thk":    0.80,     # §5.1 PCB 厚 (4 层 FR4; 6 层 = 1.0)
    "pad_soc":    0.30,     # §5.1 SoC 下方导热垫
    "frame_thk":  1.00,     # §5.1 铝/铜骨架 (v1.1 未给厚 → 假设 1.0, [推算])
    # 走线 / 充电板
    "duct_v":     6.00,     # §5.6.2 口径: 垂直向走线槽占位 (6×2 槽, 竖放)
    "duct_h":     2.00,     # §1.3 M10 走线槽厚 (H 向)
    "chg_l":     25.00,     # §1.3 M3 充电板长
    "chg_w":     10.00,     # §1.3 M3 充电板宽
    "conn_margin": 15.00,   # §1.4.2 连接器/弯折/插拔余量
    # Type-C (§5.1)
    "tc_h":       3.60,     # §5.1 面板开孔高
    "tc_w":       9.50,     # §5.1 面板开孔宽
    "tc_wall":    1.50,     # §5.1 末端承力壁厚
    # 镜框侧 (全推算, 维持 v1 口径)
    "oe_thk":     4.80,     # §1.3 M5 走鹃Ⅱ 厚 (u1 未查到)
    "sp_thk":     6.00,     # §1.4.5 分光组件 厚
    "oe_margin":  1.00,     # §1.4.5 装配余量
    "cam_thk":    7.20,     # §1.4.5 摄像头位实际需求 10-12 (取下限)
}

# =====================================================================
# 公差账 (证据: MECH_BUDGET §5.4 "装配间隙" 行 + §5.3 "打印精度风险")
# =====================================================================
TOL = {
    "fdm_part": 0.30,   # 打印件 **外形尺寸** 单边 (FDM 收缩+层纹)      [推算] §5.4
    "fdm_feat": 0.25,   # 打印件 **特征间距离** 单边 (盲槽深度/壁厚位置)  [推算] §5.4
    "cell":    0.15,    # 电芯厚度公差 —— ⚠️ [0数据] 原厂未给, 按常规假设  [推算]
    "seam":    0.10,    # 合缝/装配间隙 波动                            [推算]
}
CRIT = 2 * TOL["fdm_part"]          # 判据阈值 = 2 × 0.30 = **0.60mm**
TOL_TEXT = "FDM 单边 ±0.30mm (外形) / ±0.25mm (特征) / 电芯 ±0.15mm [假设]"

ROWS = []


def row(zone, item, need, avail, margin, worst=None, verdict="", note=""):
    ROWS.append((zone, item, need, avail, margin, worst, verdict, note))
    return margin


def v(ok):
    return "✅ 通过" if ok else "❌ 不通过"


# =====================================================================
# 1. 基线复现 (ISS-017 交卷的数, v1.1 原模型)
# =====================================================================
def baseline():
    print("=" * 100)
    print("M-FIT v2 — 镜脚侧装配余量闭环 (ISS-042) | 基线 MECH_BUDGET.md v1.1 | Q4=按需触发/340mAh/镜腿7.3mm")
    print("=" * 100)
    print(f"\n【0】判据与公差账")
    print(f"  判据: **每条余量 ≥ 2× 单边公差** → 阈值 {CRIT:.2f}mm")
    print(f"  公差: {TOL_TEXT}")
    print(f"  口径修正: 走线槽垂直占位取 6.00mm (MECH_BUDGET §5.6.2 表口径; §1.4.2 正文的 '3' 是笔误) → 取保守值")

    print(f"\n【1】基线复现 (v1.1 原模型 = ISS-017 交卷的数)")
    # H 串行 (壁 + 电池 + 隔热 + 空隙 + 壁)
    h_ser = BASE["wall"] + BASE["cell_thk"] + BASE["pad_thermal"] + BASE["air_gap"] + BASE["wall"]
    m = BASE["cav_h"] - h_ser
    row("基线·H", "前后厚 (串行: 壁0.8+电芯4.6+隔热0.5+空隙0.3+壁0.8)", h_ser, BASE["cav_h"], m,
        verdict=v(m >= CRIT),
        note=f"名义余量 {m:.2f}mm < 2×公差 {CRIT:.2f}mm → **临界 = 不通过** (ISS-017 自判)")
    # H 叠放 (§1.4.2 原表)
    h_stk = (BASE["wall"] + BASE["pad_soc"] + BASE["pcb_thk"] + BASE["cell_thk"]
             + BASE["wall"] + BASE["pad_thermal"] + BASE["air_gap"])
    m = BASE["cav_h"] - h_stk
    row("基线·H", "前后厚 (§1.4.2 叠放模型)", h_stk, BASE["cav_h"], m,
        verdict=v(m >= CRIT), note=f"干涉 {-m:+.2f}mm → 条件性不通过 ①")
    # V 串行 / 叠放
    v_ser = BASE["cell_v"] + BASE["duct_v"]
    m = BASE["cav_v"] - v_ser
    row("基线·V", "根部净高 (串行: 电芯高23.5+走线槽6)", v_ser, BASE["cav_v"], m,
        verdict=v(m >= CRIT), note=f"名义余量 {m:.2f}mm")
    v_stk = BASE["cell_v"] + BASE["pcb_w"] + BASE["duct_v"]
    m = BASE["cav_v"] - v_stk
    row("基线·V", "根部净高 (§1.4.2 叠放模型)", v_stk, BASE["cav_v"], m,
        verdict=v(m >= CRIT), note=f"干涉 {-m:+.2f}mm → 条件性不通过 ①")
    # L 充电板挪出 / 不挪出
    l_out = BASE["cell_l"] + BASE["pcb_l"] + BASE["conn_margin"]
    m = BASE["cav_l"] - l_out
    row("基线·L", "长度 (电芯40.5+PCB50+连接余量15, 充电板已挪出)", l_out, BASE["cav_l"], m,
        verdict=v(m >= CRIT), note=f"名义余量 {m:.2f}mm")
    l_keep = l_out + BASE["chg_l"]
    m = BASE["cav_l"] - l_keep
    row("基线·L", "长度 (充电板 **不** 挪出镜脚)", l_keep, BASE["cav_l"], m,
        verdict=v(m >= CRIT), note=f"干涉 {-m:+.2f}mm → 条件性不通过 ②")
    # H7 销孔
    row("基线·PCB", "定位销孔 ⌀2.0 H7 (FDM 打不出)", 2.00, 2.00, 0.0,
        verdict="❌ 打印件做不到",
        note=f"FDM ±{TOL['fdm_part']:.2f} vs H7 ±0.010 → 条件性不通过 ③ (v1.1 §5.3/§5.5 已规定用金属件)")
    # 尾端
    tail = BASE["tc_h"] + 2 * BASE["tc_wall"]
    m = BASE["cav_h"] - tail
    row("基线·尾端", "尾端截面高 (开口3.6+两侧承力壁1.5)", tail, BASE["cav_h"], m,
        verdict=v(m >= CRIT), note=f"名义余量 {m:.2f}mm (充电板/Type-C 挪到镜框后此段空出)")
    # PCB/SoC 段 (H 余量最大的一段 —— 关键资源)
    h_pcb = (BASE["wall"] + BASE["pad_thermal"] + BASE["air_gap"] + BASE["pcb_thk"]
             + BASE["pad_soc"] + BASE["frame_thk"] + BASE["wall"])
    m = BASE["cav_h"] - h_pcb
    row("基线·散热", "PCB/SoC 段前后占位 (含骨架1.0)", h_pcb, BASE["cav_h"], m,
        verdict="✅ 通过", note=f"余量 {m:.2f}mm ← **这条是解A 的资源** (隔热层挪到这里放得下)")
    return h_ser, h_stk, v_ser, v_stk, l_out, l_keep


# =====================================================================
# 2. 候选解 ×4
# =====================================================================
def candidates():
    print(f"\n【2】候选解 ×4 —— 每个都给 改什么 / 代价 / 修完后的余量数字")

    # ---------- 解 A (推荐): 隔热层局部化 + 电池段单件箱形 ----------
    # 改动 1: 0.5 隔热垫 + 0.3 空气隙 只保留在 PCB/SoC 段 (那里 H 余量 2.80)
    # 改动 2: 电池段做成 **下壳一体的盲槽 + 自带 0.8 顶板** (单件闭环, 取消该段合缝)
    # 改动 3: 电池座改为 **非对称座**: 深 4.75 (电芯 4.60 + 0.15), 定位面在段前端壁
    seat_A = BASE["cell_thk"] + 0.15          # 4.75
    h_A = BASE["wall"] + seat_A + BASE["wall"]  # 皮肤壁 + 座深 + 顶板
    # 最坏情况: 下壳外形尺寸 ±0.30 (FDM), 内部特征 ±0.25
    h_A_worst = h_A + TOL["fdm_part"]          # 6.65
    mA = BASE["cav_h"] - h_A
    mA_w = BASE["cav_h"] - h_A_worst
    vA = BASE["cell_v"] + BASE["duct_v"]
    lA = BASE["cell_l"] + BASE["pcb_l"] + BASE["conn_margin"]
    print(f"\n  ── 解 A 【隔热层局部化 + 电池段单件箱形】 ★推荐")
    print(f"     改: ①0.5隔热垫+0.3空隙只留 PCB/SoC 段 ②电池段=下壳一体盲槽(深4.75)+自带0.8顶板, 取消该段合缝")
    print(f"         ③顶板内侧 0.4 硅胶压垫 (吸收电芯厚度公差, 不产生硬干涉)")
    print(f"     前后: 需求 {h_A:.2f} → 余量 **{mA:.2f}mm** (最坏 {h_A_worst:.2f} → 余量 {mA_w:.2f}mm)  "
          f"{'✅ ≥2×公差' if mA_w >= CRIT else '❌'}")
    print(f"     垂直: 需求 {vA:.2f} → 余量 **{BASE['cav_v']-vA:.2f}mm**   长度: 需求 {lA:.2f} → 余量 **{BASE['cav_l']-lA:.2f}mm**")
    print(f"     代价: 隔热垫位置迁移 (数量不变) + 压垫 {0.4*BASE['cell_v']*BASE['cell_l']*0.3/1000:.2f}g/条 → 整机 +0.2g; "
          f"上壳缩短 (电池段由下壳封口, 净材料 ≈ 0); 装配顺序: 电芯先装下壳 → 再合上壳")
    print(f"     公差性质: 电池段是 **同一个打印件**, H 尺寸链上只有 **1 个** FDM 外形公差 (±0.30), "
          f"不是 v1 的 3 个壁面公差叠加")
    row("解A·H", "前后厚 (皮肤壁0.8 + 座深4.75 + 顶板0.8)", h_A, BASE["cav_h"], mA, mA_w,
        verdict=v(mA_w >= CRIT), note=f"名义余量 {mA:.2f}mm; 最坏情况 {h_A_worst:.2f}mm → 余量 {mA_w:.2f}mm")
    # 座深 vs 电芯: 短座情形由 0.4mm 硅胶压垫吸收, 不产生硬干涉, 也不改变 H 包络
    seat_min = (h_A - TOL["fdm_part"]) - BASE["wall"] - BASE["wall"]     # 座深最短情形 (下壳最矮)
    crush = (BASE["cell_thk"] + TOL["cell"]) - seat_min                     # 需被压垫吸收的量
    print(f"     座深/电芯配合: 座深名义 {seat_A:.2f} → 最短情形 {seat_min:.2f}mm; "
          f"电芯最厚 {BASE['cell_thk']+TOL['cell']:.2f}mm → 需压缩 {crush:.2f}mm, "
          f"由 0.40mm 硅胶压垫吸收 ({'✅ 无硬干涉' if crush <= 0.40 else '❌ 压不动'}), H 包络不变")
    row("解A·配合", "电池座深 vs 电芯厚 (压垫吸收)", BASE["cell_thk"] + TOL["cell"], seat_min, -crush,
        verdict="✅ 通过" if crush <= 0.40 else "❌ 不通过",
        note=f"最厚电芯比最短座深多 {crush:.2f}mm → 0.40mm 硅胶压垫压缩吸收")
    row("解A·V", "根部净高 (电芯高 + 走线槽6)", vA, BASE["cav_v"], BASE["cav_v"] - vA,
        BASE["cav_v"] - vA - TOL["fdm_feat"] - TOL["cell"],
        verdict="✅ 通过")
    row("解A·L", "长度 (电芯 + PCB + 连接余量)", lA, BASE["cav_l"], BASE["cav_l"] - lA,
        BASE["cav_l"] - lA - 3 * TOL["fdm_part"], verdict="✅ 通过")

    # ---------- 解 A-1 (最小改动版): 上壳覆盖全长 ----------
    h_A1 = BASE["wall"] + seat_A + BASE["seam"] + BASE["wall"]
    h_A1_worst = (h_A1 + TOL["fdm_part"] * 2 + TOL["seam"])
    mA1 = BASE["cav_h"] - h_A1
    mA1_w = BASE["cav_h"] - h_A1_worst
    print(f"\n  ── 解 A-1 【只取消电池段隔热层, 上壳仍覆盖全长】 (最小改动, 但**最坏情况不过**)")
    print(f"     改: 只做解A 的改动①, 电池段仍由上壳盖板封口 (中间留 0.2 合缝)")
    print(f"     前后: 需求 {h_A1:.2f} → 名义余量 **{mA1:.2f}mm** (≥{CRIT:.2f} ✓); "
          f"**最坏情况 {h_A1_worst:.2f} → 余量 {mA1_w:.2f}mm ❌** (两个打印件的高度公差 ±0.30 各自叠加)")
    print(f"     结论: 名义能过, 最坏情况**过不了** → 只能当 A 的降级版, 不能当主选")
    row("解A1·H", "前后厚 (壁0.8+座4.75+合缝0.2+壁0.8) 最坏情况", h_A1_worst, BASE["cav_h"], mA1_w,
        verdict="❌ 最坏情况不通过", note=f"名义余量 {mA1:.2f}mm 通过, 但对抗栈余量 {mA1_w:.2f}mm")

    # ---------- 解 B: 解 A + 换薄电芯 (丰江 432243, 4.30 厚 / 420mAh) ----------
    seat_B = BASE["cell2_thk"] + 0.15
    h_B = BASE["wall"] + seat_B + BASE["wall"]
    h_B_worst = h_B + TOL["fdm_part"]
    vB = BASE["cell2_v"] + BASE["duct_v"]
    lB = BASE["cell2_l"] + BASE["pcb_l"] + BASE["conn_margin"]
    w_cell340 = 3.7 * 340 / 1000 / 260 * 1000
    w_cell420 = 3.7 * 420 / 1000 / 260 * 1000
    print(f"\n  ── 解 B 【解 A + 换薄电芯: 丰江 432243, 4.30mm 厚 / 420mAh】")
    print(f"     改: 电芯 Renata ICP582035PR-01 (4.60 厚) → 丰江 432243 (4.30 厚, 420mAh ≥ 340 需求)")
    print(f"     前后: 需求 {h_B:.2f} → 名义余量 **{BASE['cav_h']-h_B:.2f}mm** (最坏 {h_B_worst:.2f} → 余量 {BASE['cav_h']-h_B_worst:.2f}mm) ✅")
    print(f"     垂直: {vB:.2f} → 余量 **{BASE['cav_v']-vB:.2f}mm**   长度: {lB:.2f} → 余量 **{BASE['cav_l']-lB:.2f}mm**")
    print(f"     代价: **整机 +{2*(w_cell420-w_cell340):.2f}g** (420mAh 5.98g vs 340mAh 4.84g @260Wh/kg, §3 W7 同口径) —— "
          f"重量表已经 50.1-74.0g 超标, 不建议为空间买重量")
    print(f"     好处: 容量 340→420mAh (按需触发口径下续航余量更足), 垂直省 1.5mm, 体积密度 78→102 mAh/cc")
    row("解B·H", "前后厚 (壁0.8 + 座4.45 + 顶板0.8)", h_B, BASE["cav_h"], BASE["cav_h"] - h_B,
        BASE["cav_h"] - h_B_worst, verdict="✅ 通过", note=f"代价 +{2*(w_cell420-w_cell340):.2f}g 整机")

    # ---------- 解 C: 电池分置左右镜脚 (2×170mAh) ----------
    seat_C = 4.00 + 0.15
    h_C = BASE["wall"] + seat_C + BASE["wall"]
    print(f"\n  ── 解 C 【电池分置左右镜脚 (各 170mAh)】")
    print(f"     改: 340mAh 拆成 2×170mAh, 每侧用 ≤4.00mm 厚的电芯 (⚠️ 具体型号 [0数据], 需采购确认)")
    print(f"     前后: 需求 {h_C:.2f} → 名义余量 **{BASE['cav_h']-h_C:.2f}mm** (最坏 {h_C+TOL['fdm_part']:.2f} → 余量 {BASE['cav_h']-h_C-TOL['fdm_part']:.2f}mm) ✅")
    print(f"     垂直/长度: 每侧 ≤25mm (电池40+PCB50+余量15) → 长度余量 ≥{BASE['cav_l']-105:.2f}mm ✅")
    print(f"     代价: **跨铰链 1-2A 充电电流** (铰链滑环或加粗 FPC, 屈寿命 = 最大新风险) + 电池座×2 + 焊点×2 + 整机 +0.5~1.0g (体积效率 -35%)")
    print(f"     额外收益: 镜脚皮肤侧只剩电池 → 皮肤温度 37.5°C (§2.3.1 降级方案4), 但 SoC 仍在镜脚 → 收益有限")
    print(f"     判定: **不推荐** —— 可靠性新风险 > 空间收益 (解A 已能把余量做到 {mA:.2f}mm)")
    row("解C·H", "前后厚 (壁0.8 + 座4.15 + 顶板0.8)", h_C, BASE["cav_h"], BASE["cav_h"] - h_C,
        BASE["cav_h"] - h_C - TOL["fdm_part"], verdict="✅ 通过", note="⚠️ 电芯型号 [0数据]; 跨铰链大电流为新风险")

    # ---------- 解 D: PCB/SoC 挪到镜框 (变更请求) ----------
    print(f"\n  ── 解 D 【SoC + PCB 全部挪到镜框, 镜脚只留电池】 (散热最优, 但**撞已锁前提**)")
    print(f"     前后: 镜脚侧同解A → 余量 **{mA:.2f}mm** ✅; 皮肤侧温度 37.5°C ✅ (§2.3.1 降级方案4, 唯一同时解掉空间+散热的方案)")
    print(f"     ❌ 但镜框没有位置: 正中区 11.8mm 光学舱已锁 (§1.4.5) / 上沿 10-12mm 被摄像头占 / 镜片位 1.3mm")
    print(f"     → 镜框要再塞 50×12 PCB + 骨架 + 石墨, 厚度必然突破 11.8mm → **必须走变更流程**; "
          f"本轮判定: **不可行 (是没位置, 不是没时间)**")
    row("解D·H", "前后厚 (镜脚只留电池) — 撞锁死前提", h_A, BASE["cav_h"], mA, mA_w,
        verdict="❌ 前提冲突", note="镜框无位置放 PCB/骨架; 需变更流程")

    return dict(A=(mA, mA_w, BASE["cav_v"] - vA, BASE["cav_l"] - lA),
                A1=(mA1, mA1_w, None, None),
                B=(BASE["cav_h"] - h_B, BASE["cav_h"] - h_B_worst, BASE["cav_v"] - vB, BASE["cav_l"] - lB),
                C=(BASE["cav_h"] - h_C, BASE["cav_h"] - h_C - TOL["fdm_part"], None, None))


# =====================================================================
# 3. 三项条件性不通过的逐条解法
# =====================================================================
def conditional_fixes():
    print(f"\n【3】三项条件性不通过 —— 逐条解法 (含计算)")

    # ① 叠放模型
    h_stk = (BASE["wall"] + BASE["pad_soc"] + BASE["pcb_thk"] + BASE["cell_thk"]
             + BASE["wall"] + BASE["pad_thermal"] + BASE["air_gap"])
    v_stk = BASE["cell_v"] + BASE["pcb_w"] + BASE["duct_v"]
    l_ser = BASE["cell_l"] + BASE["pcb_l"]
    print(f"\n  ① 叠放模型 (前后 +0.80mm / 垂直 +3.50mm) —— **裁决: 锁「沿长度串行」, 叠放物理不成立**")
    print(f"     证明 A (H): 叠放要求 {h_stk:.2f}mm > 镜腿上限 {BASE['cav_h']:.2f}mm, 超 {h_stk-BASE['cav_h']:.2f}mm → 在 7.3mm 镜腿里**根本装不下**")
    print(f"     证明 B (V): 叠放要求 {v_stk:.2f}mm > 根部净高 {BASE['cav_v']:.2f}mm, 超 {v_stk-BASE['cav_v']:.2f}mm → 同样装不下")
    print(f"     证明 C (L): 串行只需 {l_ser:.1f}mm ≤ 内长 {BASE['cav_l']:.1f}mm (余 {BASE['cav_l']-l_ser:.1f}mm) → **串行是唯一可行排布**")
    print(f"     处置: §1.4.2 的 H/V 表是 **过时模型** (它按 420mAh/22mm 电芯算), §1.3/§1.4.3/§1.6.2/§1.6.3/§5.6.2 全用串行 → 以串行为准, 叠放分支作废")
    print(f"     若老板坚持叠放: 镜腿厚必须 ≥ {h_stk:.2f} + 2×{TOL['fdm_part']:.2f} = **{h_stk + 2*TOL['fdm_part']:.2f}mm**")
    print(f"             = 比 7.3mm 厚 {(h_stk + 2*TOL['fdm_part'])/BASE['cav_h']-1:+.0%} (华为 AI 眼镜 6.25mm 的 {(h_stk + 2*TOL['fdm_part'])/6.25:.2f} 倍) → **走变更流程**")
    print(f"     ⟹ 本轮: ①按「串行 + 解A」闭环, 不需要变更")

    # ② 充电板不移出
    l_keep = BASE["cell_l"] + BASE["pcb_l"] + BASE["conn_margin"] + BASE["chg_l"]
    v_par = max(BASE["pcb_w"], BASE["chg_w"]) + BASE["duct_v"]
    print(f"\n  ② 充电板不移出镜脚 (长度 +0.50mm) —— **解法: 充电板与主 PCB 沿垂直方向并排 (不占长度)**")
    print(f"     前提方案 (已定): 充电板挪到镜框 (§1.6.3) → 长度需求 {BASE['cell_l']+BASE['pcb_l']+BASE['conn_margin']:.1f}mm, 余 {BASE['cav_l']-(BASE['cell_l']+BASE['pcb_l']+BASE['conn_margin']):.1f}mm ✅")
    print(f"     若坚持留在镜脚且必须沿长度串行: 需求 {l_keep:.2f} > {BASE['cav_l']:.2f} → 干涉 {l_keep-BASE['cav_l']:.2f}mm ❌")
    print(f"     ⟹ 改排布: 充电板 (25×10×0.8) 放到 **PCB 段的垂直空当** (与 PCB 同 L 段, 沿 V 并排):")
    print(f"        长度需求不变 = {BASE['cell_l']+BASE['pcb_l']+BASE['conn_margin']:.1f}mm → 余量 **{BASE['cav_l']-(BASE['cell_l']+BASE['pcb_l']+BASE['conn_margin']):.1f}mm** ✅")
    print(f"        该段垂直需求 = max(PCB宽12, 充电板宽10) + 走线槽6 = {v_par:.1f}mm ≤ 净高 {BASE['cav_v']:.1f} → 余量 **{BASE['cav_v']-v_par:.1f}mm** ✅")
    print(f"        (Type-C 仍在尾端; 充电板→尾端的线走 **电芯上方的走线槽**, 该槽在 V 向占 6mm, 在 H 向占 2mm, 位于电芯上方而非侧面)")
    print(f"     兜底: PCB 50→45mm (需 hw-lead 确认 12×12 逃线区 + MIPI + SPI-NOR 68mm² 能否放下) → 长度需求 {BASE['cell_l']+45+BASE['conn_margin']+BASE['chg_l']:.1f} → 余 {BASE['cav_l']-(BASE['cell_l']+45+BASE['conn_margin']+BASE['chg_l']):.1f}mm ✅")

    # ③ H7 销孔
    print(f"\n  ③ ⌀2.0 H7 定位销孔 FDM 做不到 —— **解法: 定位基准整体移到金属骨架, 打印件只让过不定位**")
    print(f"     金属骨架 (机加工 Al/Cu, §5.5 已有件, **不增加零件数**):")
    print(f"        · PCB 安装面: 铣削平面, 平面度 ≤5µm (§1.4.5/§5.5 同款要求)")
    print(f"        · 2× M1.2 螺纹孔 (攻丝) → PCB 用 2 颗 M1.2 螺钉压紧 (★PIN-SET-2: 板坐标 S1 (8.00,2.50) / S2 (52.00,12.50), 纯压紧零定位)")
    print(f"        · 2× ⌀2.0 H7 定位销孔 (⌀2.0 销装在骨架上, 销孔 H7) → 负责 **全部定位**, 防电池充放电微动 (★PIN-SET-2: P1 (8.00,7.50) 配圆销=全基准 / P2 (52.00,7.50) 配菱形销对边1.94=只定Y ⇒ 消过定位)")
    print(f"     打印件侧: 1× **⌀2.4 间隙孔** (打印公差 ±0.30 完全可接受 —— 它只让过, 不定位) + 2× ⌀1.6 螺钉过孔")
    print(f"     ⟹ 打印公差 **不进定位链**: 定位链 = 骨架铣削面 (≤5µm) + H7 销 (≤0.01) → PCB 板面平行度 ≤0.05°")
    print(f"     代价: 骨架多 2 个 M1.2 攻丝孔 + 2 个 H7 销孔 (机加工, 件数不变, 单件 +0.2g 估算); PCB 孔位已由 hw-lead ISS-049 定版 PIN-SET-2 (2×⌀2.0H7 销孔 + 2×⌀1.4 压紧孔, 板坐标 P1(8.00,7.50)/P2(52.00,7.50)/S1(8.00,2.50)/S2(52.00,12.50))")
    print(f"     ⚠️ 打印包要改一处: temple_cage_340.stl 的 ⌀2.0 配作孔 → ⌀2.4 间隙孔 (已列入 §6 打印件影响)")
    print(f"     ⚠️ 打印包**尚未跟改 PIN-SET-2** (改版授权在 PM 手上): M1.2 让过孔仍是老口径 (孔距 40.00, X=6/X=46); PIN-SET-2 要求孔距 44.00 (S1 X=8.00 → S2 X=52.00)")
    return l_keep


# =====================================================================
# 4. 散热路径影响 (硬约束的量化)
# =====================================================================
def thermal():
    k_print, k_al = 0.20, 237.0          # §2.3 打印件 k=0.2 (PA-CF/PC-CF), §5.1 铝骨架 k=237
    L_len, W_v = 40.5e-3, 38.0e-3        # 电池段长度 / 镜脚根部净高 (传导截面积 = 高 × 厚)
    H_cav = BASE["cav_h"] * 1e-3
    R_print = L_len / (k_print * W_v * H_cav)          # 打印上壳纵向热阻
    R_al = L_len / (k_al * 1.0e-3 * W_v)                # 1.0mm 铝骨架若延伸进电池段
    R_skin, R_conv = 54.2, 667.0                        # §2.3 皮肤路径 / 对流
    R_cell, R_wall = 50.0, 12.5                        # 电芯 + 皮肤侧壁 (§2.3 R_壳壁)
    print(f"\n【4】对散热路径的影响 (解 A)")
    print(f"  热路 ①  主散热路 (不变): SoC → 0.3 导热垫 → 铝骨架 → 石墨 → 上壳外壁 → 对流")
    print(f"  热路 ②  隔热路 (不变):   SoC → 0.5 隔热垫 + 0.3 空气隙 (在 PCB/SoC 段) → 皮肤侧下壳 → 皮肤")
    print(f"  ⟹ 解 A 只把 0.5 垫 + 0.3 空隙从「全长」缩到「PCB/SoC 段」, **热路 ② 的隔热层原封不动留在 SoC 与皮肤之间** → 皮肤侧温度不变 (§2.3.1: 0.23W → 46.5°C ❌ 仍超 43°C, 但**不是我这条改的**)")
    print(f"  电池段没有热源 (电芯自身发热 mW 级) → 取消该段隔热层 **不切断任何热路**")
    print(f"\n  ⚠️ 新增硬约束 (量化): **金属骨架 / 石墨不得延伸进电池段**")
    print(f"     若骨架(铝 1.0mm)延伸进电池段 → 新增并联热路 R = {R_al:.2f} K/W")
    print(f"        并联后 R_skin_path: {R_skin:.1f} → {1/(1/R_skin + 1/(R_al+R_cell+R_wall)):.1f} K/W, "
          f"进入皮肤的热量比例: {R_conv/(R_skin+R_conv)*100:.1f}% → {R_conv/(1/(1/R_skin+1/(R_al+R_cell+R_wall))+R_conv)*100:.1f}%")
    print(f"        (按 §2.3.1 的 ±14°C 模型不确定性, 这条只能当「禁止」的依据, 不能当「允许」的依据)")
    print(f"     若维持打印件(PA-CF k=0.2)纵向导热 → R = {R_print:.0f} K/W, 与皮肤路径 {R_skin:.1f} K/W 并联后几乎无影响 ✅")
    print(f"     ⟹ 解 A 的散热结论: **热路不断**; 附带代价 0 (隔热垫数量不变); 但必须写进加工图: 骨架止于 PCB 段后缘")
    print(f"  充电峰值 (0.8W): 充电板挪到镜框 (已定前提) → 镜脚不受影响; 若按解 ② 留在镜脚, 必须铝屏蔽罩 + 与皮肤隔断 (§2.4 E), "
          f"镜脚皮肤侧净高余量 {BASE['cav_v']-(BASE['cell_v']+BASE['duct_v']):.1f}mm 放得下屏蔽罩 ✅")
    return R_al, R_print


# =====================================================================
# 5. 镜框侧 (维持 v1 口径: 数据不足, 只能列条件)
# =====================================================================
def frame_side():
    frame_mid = BASE["oe_thk"] + BASE["sp_thk"] + BASE["oe_margin"]
    row("镜框·正中", "光学舱厚度 (光机+分光件+余量)", frame_mid, None, None,
        verdict="⚠️ 未验", note="镜框正中厚度未定义 + 走鹃Ⅱ 三维尺寸未查到 (u1) → 需 JBD")
    row("镜框·上沿", "摄像头位厚度 (模组+遮光罩+壁)", BASE["cam_thk"], None, None,
        verdict="⚠️ 未验", note="镜框上沿厚度未定义 + 模组型号未选 (u5) → 需模组厂")
    row("镜框·镜片位", "波导卡槽平行度 ±0.3°", 0.3, None, None,
        verdict="⚠️ 未验", note="波导 2D 外形图/耦入区未到 (u4) → 需 JBD + 波导厂")


def dump_rows():
    print(f"\n【5】逐项表 (余量 + 最坏情况余量)")
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
    baseline()
    cand = candidates()
    conditional_fixes()
    thermal()
    frame_side()
    dump_rows()

    mA, mAw, vA, lA = cand["A"]
    print("\n" + "=" * 100)
    print("★ 结论 (镜脚侧 / 340mAh 档 / 充电板挪出镜脚 / 沿长度串行 / Q4 锁死镜腿 7.3mm)")
    print("=" * 100)
    print(f"  基线 (v1.1 原模型): 前后名义余量 0.30mm < 2×公差 0.60mm → **临界 = 不通过** (ISS-017 自判, 已闭环)")
    print(f"  推荐解 A: 前后 **余量 {mA:.2f}mm** (最坏情况 {mAw:.2f}mm) / 垂直 **余量 {vA:.2f}mm** / 长度 **余量 {lA:.2f}mm**")
    print(f"          判据: 前后 {mAw:.2f}mm ≥ 2×{TOL['fdm_part']:.2f} = {CRIT:.2f}mm → **是**")
    print(f"  三项条件性不通过: ① 裁决为串行 (叠放在 7.3mm 内物理不可能, 已给 H/V/L 三重证明) "
          f"② 充电板沿 V 与 PCB 并排, 长度余量 {lA:.2f}mm 不变 ③ 定位基准移到金属骨架, 打印件只做 ⌀2.4 间隙孔")
    print(f"  散热: 热路不断 (隔热层仍在 SoC 段); 新增硬约束 = 金属骨架/石墨不得延伸进电池段 (否则并联热路 4.50 K/W)")
    print(f"  镜框侧: 仍 **未验** (缺 JBD 走鹃Ⅱ 三维尺寸 u1 + 波导 2D 外形图 u4 + 镜框截面 u8)")
    print(f"\n★ 口径: 本脚本是 **设计态几何 + 公差栈计算**, 不是物理装配实测 → measurements.yaml 里 M-FIT 的 kind 仍写 [推算]")
    print(f"  实物解锁路径不变: 打 MECH/print/ 打印包 → 按 MECH/print/MEASURE_CHECKLIST.md 量 → 回填 measurements.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
