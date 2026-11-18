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
退出码: 0 = 报告已生成 (结论看最后一节; **不代表实物已验**)
"""
from __future__ import annotations

import math

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
    "cell_thk":   4.60,   # §1.6.1 Renata ICP582035PR-01 340mAh 厚   [官网]
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

ROWS = []
def row(zone, item, need, avail, margin, worst=None, verdict="", note=""):
    ROWS.append((zone, item, need, avail, margin, worst, verdict, note))

def v(ok):
    return "✅ 通过" if ok else "❌ 不通过"


# =====================================================================
# 1. 板宽 30 下的 V 链 (本单最大的一条)
# =====================================================================
def v_chain():
    print("=" * 100)
    print("M-FIT v3 | 板宽 30mm (V 向) / 板长 60mm / RK3576 | 镜脚内腔 H7.30 × V38.00 × L130.00 (锁死)")
    print("=" * 100)
    print(f"\n【0】判据与公差账")
    print(f"  判据: 每条余量 ≥ 2×单边公差 = {CRIT:.2f}mm")
    print(f"  公差: FDM 外形 ±{TOL['fdm_part']:.2f} / 特征 ±{TOL['fdm_feat']:.2f} / "
          f"电芯 ±{TOL['cell']:.2f} [0数据] / PCB 外形 ±{TOL['pcb_out']:.2f} [0数据]")

    print(f"\n【1】V 链 (板宽吃的就是这一条) —— 板宽 15 → 30 的账")
    for w in (12.0, 15.0, 30.0):
        v_pcb = w + BASE["duct_v"]
        v_cell = BASE["cell_v"] + BASE["duct_v"]
        need = max(v_pcb, v_cell)
        margin = BASE["cav_v"] - need
        worst = margin - 2 * TOL["fdm_part"]
        tag = "  ← ★当前基线" if w == 30.0 else ("  (作废口径)" if w == 12.0 else "  (前口径)")
        print(f"  板宽 {w:>5.1f}mm: PCB段 {v_pcb:5.2f} / 电芯段 {v_cell:5.2f} → 需求 {need:5.2f} "
              f"vs 净高 {BASE['cav_v']:.2f} ⇒ 余量 {margin:+6.2f} (最坏 {worst:+6.2f}) "
              f"{'✅' if worst >= CRIT else '❌'} {tag}")
    v_pcb = 30.0 + BASE["duct_v"]
    margin = BASE["cav_v"] - v_pcb
    worst = margin - 2 * TOL["fdm_part"]
    row("镜脚·V", "根部净高 (板宽30 + 走线槽6)", v_pcb, BASE["cav_v"], margin, worst,
        verdict=v(worst >= CRIT),
        note=f"★板宽 15→30 把 PCB 段需求从 21.00 抬到 36.00 ⇒ **V 余量 17.00 → "
             f"{margin:.2f} (最坏 {worst:.2f})**; 板宽硬顶 = 38.00-6.00-0.60 = **31.40mm**")
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
    print(f"\n【2】H 链 (前后 7.30) × 板厚四档 —— ★ISS-092 检修口净空随板厚变")
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
    print(f"  ★ 板厚 1.22 (模型A) 下: 净空 {res[1.22]['clearance']:.2f} **< 4.50 硬要求 "
          f"差 {4.50-res[1.22]['clearance']:.2f}** ⇒ ISS-092 C-5 与 P-1 探针口径要重算")
    print(f"  ★ 板厚 0.41 (模型B) 下: 净空 {res[0.41]['clearance']:.2f} ⇒ 盖板内腔余 "
          f"{res[0.41]['clearance']-4.50:.2f} (比 0.80 档多 {res[0.41]['clearance']-4.90:.2f})")
    row("镜脚·H", "PCB 段前后占位 (t=0.80 中档)",
        res[0.80]["h_pcb"], BASE["cav_h"], res[0.80]["margin"], res[0.80]["worst"],
        verdict=v(res[0.80]["worst"] >= CRIT), note="板厚四档全过: 最紧 t=1.22 ⇒ 最坏余量 "
        f"{res[1.22]['worst']:.2f}mm")
    row("镜脚·H", "检修口净空 (外表面→PCB焊盘面) ≥4.50",
        4.50, res[0.80]["clearance"], res[0.80]["clearance"] - 4.50,
        res[1.22]["clearance"] - 4.50,
        verdict=("✅ 通过 (0.41~1.00 档)" if res[1.22]["clearance"] >= 4.50
                 else "⚠️ 板厚 1.22 档不通过"),
        note=f"板厚 0.41/0.80/1.00 → 净空 {res[0.41]['clearance']:.2f}/{res[0.80]['clearance']:.2f}/"
             f"{res[1.00]['clearance']:.2f} ✅; **t=1.22 → {res[1.22]['clearance']:.2f} ❌ 差 "
             f"{4.50-res[1.22]['clearance']:.2f}** (ISS-092 C-5/P-1 口径要重算)")
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
    print(f"\n【3】L 链 (长度 130.00) —— 板长 60 不变, 故 L 链与板宽无关")
    l_need = BASE["cell_l"] + 60.0 + BASE["conn_margin"]
    m = BASE["cav_l"] - l_need
    row("镜脚·L", "长度 (电芯40.5 + 板长60 + 余量15)", l_need, BASE["cav_l"], m,
        m - 3 * TOL["fdm_part"], verdict=v(m - 3 * TOL["fdm_part"] >= CRIT),
        note=f"余量 {m:.2f}mm (ISS-092 复核 Δ=0.00)")
    max_len = BASE["cav_l"] - BASE["cell_l"] - BASE["conn_margin"]
    print(f"  板长物理上限 = 130.00 - 40.50(电芯) - 15.00(余量) = **{max_len:.1f}mm**; "
          f"RK3576 在 30mm 板宽下需板长 ≥55.9mm (ISS-118) ⇒ 60mm 在区间内, 上限还有 {max_len-60:.1f}mm")
    row("镜脚·L", "板长物理上限 (电芯+余量占用)", 60.0, max_len, max_len - 60.0, None,
        verdict="✅ 通过", note=f"上限 {max_len:.1f}mm, 现取 60 ⇒ 还有 {max_len-60:.1f}mm 余量")
    return m


# =====================================================================
# 4. 面积 / 重量 (板宽 30 的账单)
# =====================================================================
def area_weight():
    print(f"\n【4】面积与重量账 —— 板宽 15 → 30 的直接账单")
    areas = {"50×12": 600.0, "60×15": 900.0, "60×30": 1800.0}
    for k, a in areas.items():
        w4 = a * 0.0008 * 1.85 * 1000 / 1000 * 1000 / 1000  # 面积mm² × t mm × 1.85 g/cm³
        w4 = a * 0.8e-3 * 1.85
        w6 = a * 1.0e-3 * 1.85
        w9 = a * 1.22e-3 * 1.85
        print(f"  板形 {k:<8} 面积 {a:6.0f}mm² ⇒ 板重 4层 {w4:.3f}g / 6层 {w6:.3f}g / "
              f"9层(1.22) {w9:.3f}g   [推算, 密度 1.85 g/cm³, 口径同 HW/pcb60x30_check.py]")
    d4 = areas["60×30"] * 0.8e-3 * 1.85 - areas["60×15"] * 0.8e-3 * 1.85
    d6 = areas["60×30"] * 1.0e-3 * 1.85 - areas["60×15"] * 1.0e-3 * 1.85
    print(f"  ★ PCB 板重增量 (60×15 → 60×30): 4层 **+{d4:.3f}g** / 6层 **+{d6:.3f}g** "
          f"(HW/pcb60x30_check.json: 1.332→2.664 / 1.665→3.330 g)")
    # 骨架: V 覆盖 12 → 30 (满宽), 长度按 SoC 区 25mm 估 (待 hw-lead 给 SoC 落位)
    sk_len = 25.0
    for w, sv in SKELETON_V.items():
        vol = sk_len * sv * 1.0          # mm³
        print(f"  金属骨架 (板宽 {w:.0f}): V 覆盖 {sv:.1f}mm × 长 {sk_len:.0f}mm × 厚 1.0mm ⇒ "
              f"{vol/1000:.2f}cm³ × 2.70 g/cm³ = **{vol/1000*2.70:.3f}g** [推算, 骨架长度假设 25mm]")
    sk15 = sk_len * 12.0 * 1.0 / 1000 * 2.70
    sk30 = sk_len * 30.0 * 1.0 / 1000 * 2.70
    d_sk = sk30 - sk15
    row("重量", "金属骨架 V 覆盖 12 → 30 (SoC 横向铺满)", d_sk, 0.0, -d_sk, None,
        verdict="⚠️ 重量代价",
        note=f"骨架 +{d_sk:.3f}g/侧 (V 覆盖 12.0→30.0 满宽, 长 25mm 假设) ⇒ 整机 +{2*d_sk:.3f}g")
    row("重量", "PCB 板重 60×15 → 60×30 (4层)", d4, 0.0, -d4, None, verdict="⚠️ 重量代价",
        note=f"1.332 → 2.664 g (+{d4:.3f}g); 6层 +{d6:.3f}g ⇒ 整机 +{d4+2*d_sk:.3f}~{d6+2*d_sk:.3f}g")
    return d4, d6, d_sk


# =====================================================================
# 5. 电池 · 光机 · 镜框侧 (不依赖波导外形的那部分)
# =====================================================================
def battery_and_frame():
    print(f"\n【5】电池段与镜框侧")
    print(f"  电池 (串行排布, 板宽不吃电池段): 电芯 4.60×23.50×40.50 (Renata 340mAh, 315mAh 档)")
    print(f"    V 需求 {BASE['cell_v']+BASE['duct_v']:.2f} vs 38.00 ⇒ 余量 "
          f"{BASE['cav_v']-BASE['cell_v']-BASE['duct_v']:.2f}mm (**不变**)")
    print(f"    H 需求 6.35 vs 7.30 ⇒ 余量 0.95 (最坏 0.65) (**不变**)")
    print(f"    L 占 0..40.50 ⇒ 电池空间与续航口径 **不变** ⇒ 板宽 30 没有换到任何电池空间")
    row("镜脚·电池", "电池段 V/H/L 三向 (解A 315mAh 档)", 29.50, 38.00, 8.50, 7.90,
        verdict="✅ 通过", note="板宽 30 不影响电池段 (串行排布) ⇒ 续航结论不变")
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
    v_margin, v_worst = v_chain()
    h_res = h_chain()
    l_chain()
    d4_, d6_, d_sk_ = area_weight()
    battery_and_frame()
    dump_rows()

    print("\n" + "=" * 100)
    print("★ 结论 (镜脚侧 / 板宽 30mm (V 向) / 板长 60mm / RK3576 / 镜腿 7.3mm 锁死)")
    print("=" * 100)
    print(f"  ① **V 链是本单唯一被板宽打穿的链**: 板宽 30 + 走线槽 6 = 36.00 vs 净高 38.00 ⇒ "
          f"余量 {v_margin:.2f}mm (最坏 {v_worst:.2f}) ⇒ ✅ 过判据 0.60, 但 **比板宽 15 时少 15.00mm**")
    print(f"     ⇒ 板宽硬顶 = 38.00 - 6.00 - 0.60 = **31.40mm** (30mm 距顶只剩 1.40mm)")
    print(f"  ② **H 链与 L 链一字不动**: H 控制段仍是电芯段 6.35 (余 0.95 / 最坏 0.65); "
          f"L 需求 115.50 vs 130.00 (余 14.50)")
    print(f"  ③ **ISS-092 检修口净空随板厚变**: 净空 = 7.30 - (0.80+0.50+0.30+t) ⇒ "
          f"t=0.41/0.80/1.00/1.22 → "
          f"{h_res[0.41]['clearance']:.2f}/{h_res[0.80]['clearance']:.2f}/"
          f"{h_res[1.00]['clearance']:.2f}/{h_res[1.22]['clearance']:.2f}mm")
    print(f"     ⇒ **t=1.22 (模型A 9 层) 破 4.50 硬要求** (差 {4.50-h_res[1.22]['clearance']:.2f}) "
          f"⇒ C-5 与 P-1 探针口径要重算; t≤1.00 时 4.90 不变")
    print(f"  ④ **电池空间/续航完全不变** (串行排布, 板宽只吃 PCB 段的 V) ⇒ 板宽 30 换到的是 "
          f"PCB 面积, 不是电池")
    print(f"  ⑤ **重量代价**: PCB +{d4_:.3f}g (4层) / +{d6_:.3f}g (6层) + 骨架 +{d_sk_:.3f}g/侧 "
          f"(整机 +{2*d_sk_:.3f}g) ⇒ 整机 **+{d4_+2*d_sk_:.2f}~{d6_+2*d_sk_:.2f}g** "
          f"(原 48.9-74.0g ⇒ **{48.9+d4_+2*d_sk_:.1f}-{74.0+d6_+2*d_sk_:.1f}g**, "
          f"目标 30-40g 更远) [推算]")
    print(f"  ⑥ **镜框侧仍全未验** (走鹃Ⅱ u1 / 波导 2D u4 / 端件截面 u8b / 摄像头 u5) ⇒ "
          f"光机·波导干涉 **无法判定**, 彩虹纹指标 [0数据]")
    print(f"\n★ 口径: 本脚本是 **设计态几何 + 公差栈计算**, 不是物理装配实测 "
          f"⇒ measurements.yaml 的 M-FIT kind 仍写 [推算]; 阶段门 G2 不认 (符合预期)")
    print(f"  实物解锁路径: 打 MECH/print/ Rev B 打印包 → 按 MEASURE_CHECKLIST.md 量 → 回填 measurements.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
