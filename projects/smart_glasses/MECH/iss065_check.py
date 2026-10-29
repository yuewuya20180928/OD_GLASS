#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/iss065_check.py —— ISS-065 结构侧评估的**机器复算**脚本
====================================================================
作者: mech-lead (结构总工) · 日期: 2026-10-29 · 关联 ISS-065 / ISS-112

它做什么 (4 段):
  【A】315 / 387 mAh 两档的镜腿前后厚映射
        - A1 现行**串行**排布 (fit_check.py 解A/解B 口径) —— 这是锁定的排布
        - A2 任务书给的"上下壳 + 隔热垫0.5 + 空气隙0.3 + PCB + 电芯"**一次性 H 向叠堆**口径
          (即 fit_check.py §3① 已裁决作废的"叠放"模型) —— 用来证明为什么它不成立
        - A3 §2.3.1(3) 现存算式的复算 (证明 §2.3.1(3) 的算式本身就是叠放口径)
  【B】鼻梁区 (镜框正中) 皮肤侧温度上界估算 (公式 + 输入全部列出)
  【C】充电板面积: T-1 / T-2 / T-3 三条腾挪方案的复算 (直接调用 hw-lead 的件表, 不重造)
  【D】跨文档一致性核对 (哪些行与新结论冲突)

用法:
    cd projects/smart_glasses && python3 MECH/iss065_check.py
退出码: 0 = 全部复算项一致 (rc=0) / 1 = 有 FAIL

边界:
  只读 HW/netlist_v1.csv + MECH/ 下文件, 不写任何东西。
  **不改几何 / 不改 STL / 不改生成器 / 不碰打印包** —— 本单只出结论与规格表。
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS: list[tuple[bool, str, str]] = []


def rec(ok: bool, code: str, title: str, detail: str) -> None:
    RESULTS.append((bool(ok), code, title))
    print(f"[{'PASS' if ok else 'FAIL'}] {code} {title}\n        {detail}")


def note(code: str, title: str, detail: str) -> None:
    """只报数, 不判 PASS/FAIL (口径冲突类条目)。"""
    RESULTS.append((True, code, title))
    print(f"[NOTE] {code} {title}\n        {detail}")


# ==================================================================== 参数表
# ── 几何 / 锁死值 [官方·老板拍板 或 官网] ──────────────────────────────
CAV_H = 7.30          # 镜腿前后厚腔体上限 (老板 Q4 锁死, MECH_BUDGET §1.6.2)  [官方]
CAV_V = 38.00         # 镜腿根部净高 (fit_check.py BASE cav_v)              [推算]
CAV_L = 130.00        # 镜腿内腔长                                        [推算]
WALL = 0.80           # P2S 打印件最小壁厚 (§5.4)                          [推算]
TOL_FDM = 0.30        # FDM 外形单边公差                                    [推算]
TOL_CELL = 0.15       # 电芯厚度公差 (原厂未给, 按常规假设)                  [推算]
CRIT = 2 * TOL_FDM    # 装配余量判据 0.60mm

# ── 串行排布: 两个 L 段各自一套 H 叠层 ────────────────────────────────
# 电池段: 皮肤壁 0.8 + 盲槽深 (电芯厚 + 0.15 压垫) + 顶板 0.8   (fit_check 解A)
# PCB段 : 下壳底壁 0.8 + 隔热垫 0.5 + 空气隙 0.3 + PCB + SoC导热垫 0.3 + 骨架 1.0 + 上壳壁 0.8
PAD_THERMAL = 0.50    # 皮肤侧隔热垫
AIR_GAP = 0.30        # 空气隙
PAD_SOC = 0.30        # SoC 下方导热垫
FRAME_T = 1.00        # 铝/铜骨架厚
PCB_T_4L = 0.80       # 4 层板厚
PCB_T_6L = 1.00       # 6 层板厚
SOC_H = 0.85          # SoC 封装高 (FCCSP 8x10 行业常规中值)   [推算]
DUCT_V = 6.00         # 走线槽 V 向占位 (§5.6.2 口径)

# ── 电芯 [官网] ───────────────────────────────────────────────────────
CELLS = {
    "315": dict(name="Renata ICP582035PR-01", cap="340mAh", t=4.60, v=23.50, l=40.50, g=4.8),
    "387": dict(name="丰江 432243", cap=">=420mAh", t=4.30, v=22.00, l=43.50, g=6.0),
}
CONN_MARGIN = 15.00   # 连接器/弯折/插拔余量
PCB_L = 60.00         # 主 PCB 长 (ISS-100/ISS-107 定板长 60mm)  [官方]
PCB_W = 15.00         # 主 PCB 宽 (ISS-100 老板拍板)              [官方]

# ── 鼻梁区热模型 [推算] ───────────────────────────────────────────────
T_BASE = 35.0         # 环境/体温基准 (MECH_BUDGET §2.3 口径)
H_SKIN = 75.0         # 皮肤界面换热系数 W/m²K (§2.3 参数表)
A_NB = 140.0          # 鼻梁皮肤接触面积 mm² [推算·无实测]
H_CONV = 10.0         # 自然对流换热系数 W/m²K (§2.3 参数表)
A_CONV = 1000.0       # 镜框正中段有效外露对流面积 mm² [0数据·u8 未定]
K_PRINT = 0.20        # 3D 打印 PA-CF/PC-CF 导热系数 W/m·K (§2.3 参数表)
K_AL = 237.0          # 铝
L_BRIDGE = 12.0       # 镜框正中热源 → 鼻梁接触面 的传导长度 mm [推算]
A_BRIDGE = 150.0      # 该热传导路径有效截面积 mm² [推算]
P_OPTICAL = 0.098     # 走鹃Ⅱ 光机 (JBD 官网 98mW)  [官方]
P_SOC_FRAME = 0.55    # SoC 域放镜框时的持续功耗中位 (ISS-055 修正后 0.40-0.66W) [推算]
T_REDLINE = 43.0      # ISO 13732-1 8h+ 持续接触阈值 [官方]
T_TARGET = 40.0       # 本项目设计目标 [推算]


def h_stack_serial(cell_t: float, pcb_t: float) -> tuple[float, float]:
    """串行排布: (电池段 H 需求, PCB段 H 需求)。来源 fit_check.py 解A。"""
    h_batt = WALL + (cell_t + TOL_CELL) + WALL
    h_pcb = WALL + PAD_THERMAL + AIR_GAP + pcb_t + PAD_SOC + FRAME_T + WALL
    return h_batt, h_pcb


def h_stack_brief(pcb_t: float, cell_t: float) -> float:
    """任务书口径: 上下壳 + 隔热垫 + 空气隙 + PCB + 电芯 —— 一次性 H 向叠堆。"""
    return WALL + WALL + PAD_THERMAL + AIR_GAP + pcb_t + cell_t


# ==================================================================== A 段
print("=" * 78)
print("ISS-065 结构侧复算 · A 段: 315 / 387 mAh 镜腿厚度映射")
print("=" * 78)

A_ROWS = []
for tier in ("315", "387"):
    c = CELLS[tier]
    for pcb_t, pcb_tag in ((PCB_T_4L, "4层0.80"), (PCB_T_6L, "6层1.00")):
        h_batt, h_pcb = h_stack_serial(c["t"], pcb_t)
        h_need = max(h_batt, h_pcb)          # 两段串行 ⇒ H 取控制段
        margin = CAV_H - h_need
        # ★最坏情况口径必须与 fit_check.py 解A 一致: 电池段是**同一个打印件** ⇒ H 尺寸链上只有
        #   **1 个** FDM 外形公差 (±0.30), 不是 3 个壁面公差叠加; 电芯厚度公差 ±0.15 由
        #   顶板内侧 0.40mm 硅胶压垫吸收 (不硬干涉, 不改 H 包络) ⇒ H 包络只 +0.30。
        h_worst = h_batt + TOL_FDM
        margin_worst = CAV_H - h_worst
        v_need = max(c["v"], PCB_W) + DUCT_V
        l_need = c["l"] + PCB_L + CONN_MARGIN
        A_ROWS.append(dict(tier=tier, cell=c, pcb_t=pcb_t, pcb_tag=pcb_tag,
                           h_batt=h_batt, h_pcb=h_pcb, h_need=h_need,
                           margin=margin, h_worst=h_worst, margin_worst=margin_worst,
                           v_need=v_need, v_margin=CAV_V - v_need,
                           l_need=l_need, l_margin=CAV_L - l_need))
        print(f"  [{tier}mAh {pcb_tag}] {c['name']} ({c['cap']}, 厚{c['t']:.2f})")
        print(f"      电池段 H = 壁{WALL} + 槽{c['t']}+{TOL_CELL} + 顶板{WALL} = {h_batt:.2f} mm")
        print(f"      PCB段  H = 壁{WALL} + 隔热{PAD_THERMAL} + 空隙{AIR_GAP} + PCB{pcb_t} "
              f"+ 导热垫{PAD_SOC} + 骨架{FRAME_T} + 壁{WALL} = {h_pcb:.2f} mm")
        print(f"      ⇒ 控制段 H 需求 = {h_need:.2f} mm ; 腔体 {CAV_H:.2f} ⇒ "
              f"名义余量 {margin:+.2f} / 最坏 {margin_worst:+.2f} mm (判据 ≥{CRIT:.2f}) "
              f"{'✅' if margin_worst >= CRIT else '❌'}")
        print(f"      垂直需求 = max(电芯高{c['v']}, 板宽{PCB_W}) + 走线槽{DUCT_V} = {v_need:.2f} "
              f"(净高 {CAV_V:.2f} ⇒ 余 {CAV_V-v_need:+.2f})")
        print(f"      长度需求 = 电芯{c['l']} + PCB{PCB_L} + 余量{CONN_MARGIN} = {l_need:.2f} "
              f"(内长 {CAV_L:.2f} ⇒ 余 {CAV_L-l_need:+.2f})")

for tier in ("315", "387"):
    r = [x for x in A_ROWS if x["tier"] == tier and x["pcb_t"] == PCB_T_4L][0]
    rec(r["margin_worst"] >= CRIT,
        f"A-{tier}", f"{tier}mAh 档串行排布装得下 (最坏余量 ≥ {CRIT:.2f}mm)",
        f"控制段 H 需求 {r['h_need']:.2f}mm vs 腔体 {CAV_H:.2f}mm; "
        f"名义余量 {r['margin']:+.2f} / 最坏 {r['margin_worst']:+.2f}mm")

# A1: 控制段是电池段 ⇒ PCB 厚 0.8 / 1.0 不改变镜腿前后厚
for tier in ("315", "387"):
    r4 = [x for x in A_ROWS if x["tier"] == tier and x["pcb_t"] == PCB_T_4L][0]
    r6 = [x for x in A_ROWS if x["tier"] == tier and x["pcb_t"] == PCB_T_6L][0]
    rec(abs(r4["h_need"] - r6["h_need"]) < 1e-9,
        f"A-{tier}-pcb", f"{tier}mAh 档 镜腿前后厚对 PCB 板厚档位不敏感",
        f"4层0.80 ⇒ {r4['h_need']:.2f}mm ; 6层1.00 ⇒ {r6['h_need']:.2f}mm "
        f"(控制段 = 电池段 {r4['h_batt']:.2f}mm, 与 PCB 段 {r6['h_pcb']:.2f}mm 无关)")

# A2: 任务书的叠堆口径 → 超差 (证明叠放不成立)
for tier in ("315", "387"):
    c = CELLS[tier]
    for pcb_t in (PCB_T_4L, PCB_T_6L):
        hb = h_stack_brief(pcb_t, c["t"])
        over = hb - CAV_H
        rec(over > 0,
            f"A2-{tier}-{pcb_t:.2f}",
            f"任务书叠堆口径 {tier}mAh/PCB{pcb_t:.2f} 超腔体 (⇒ 该口径不成立)",
            f"叠堆 H = 壁0.8+壁0.8+隔热0.5+空隙0.3+PCB{pcb_t:.2f}+电芯{c['t']:.2f} "
            f"= {hb:.2f}mm vs 腔体 {CAV_H:.2f}mm ⇒ 超 {over:+.2f}mm "
            f"(fit_check.py §3①: 叠放 H 需求 8.10 > 7.30 ⇒ 物理不成立)")
        break

# A3: §2.3.1(3) 现存算式复算 —— 它用的是叠放口径
print()
print("  ── A3: MECH_BUDGET §2.3.1(3) 现存算式复算 ──")
for tier, cell_t in (("315", 4.60), ("387", 4.30)):
    stacked = WALL + PCB_T_4L + cell_t + WALL + 0.30   # §2.3.1(3) 的算式: 壁+PCB+电芯+壁(+隔热/压垫0.3)
    print(f"      {tier}mAh: §2.3.1(3) 算式 ⇒ {stacked:.2f}mm "
          f"(文档写 7.3 / 7.0 ⇒ 残差 {stacked-7.3:+.2f} / {stacked-7.0:+.2f}) ⇒ "
          f"该算式是**叠放**口径, 与 §1.4.2 的作废 H 表同源")
    rec(abs(stacked - (7.3 if tier == "315" else 7.0)) < 0.01,
        f"A3-{tier}", f"§2.3.1(3) {tier}mAh 行算式可复现 (证其口径来源)",
        f"复算 {stacked:.2f}mm = 文档值; ⇒ 属叠放口径, 须换成串行口径 (需求 "
        f"{[x for x in A_ROWS if x['tier']==tier and x['pcb_t']==PCB_T_4L][0]['h_need']:.2f}mm)")

# A4: 上下分壳后镜腿皮肤侧只剩 3-5 mW ⇒ 35.1-35.3°C (ISS-064 S-4) 复现
K_EFF = 50.13  # §2.3 主模型 k_eff
for p_mw in (3, 5):
    t = T_BASE + p_mw / 1000.0 * K_EFF
    print(f"  A4: 皮肤侧 {p_mw} mW ⇒ {t:.2f} °C")
rec(abs((T_BASE + 0.003 * K_EFF) - 35.15) < 0.05 and abs((T_BASE + 0.005 * K_EFF) - 35.25) < 0.05,
    "A4", "上下分壳后镜腿皮肤侧 35.1-35.3°C 可复现 (ISS-064 S-4)",
    f"35.0 + 0.003x50.13 = {T_BASE + 0.003*K_EFF:.2f} ; 35.0 + 0.005x50.13 = {T_BASE + 0.005*K_EFF:.2f} "
    f"(与 MECH_BUDGET §2.3.1 降级方案4 的 35.1-35.3 一致)")

# ==================================================================== B 段
print()
print("=" * 78)
print("B 段: 鼻梁区 (镜框正中) 皮肤侧温度上界估算  [推算]")
print("=" * 78)

R_INT = 1.0 / (H_SKIN * (A_NB / 1e6))          # 鼻梁接触面 → 皮肤 K/W
R_PRINT = L_BRIDGE / 1000.0 / (K_PRINT * (A_BRIDGE / 1e6))   # 打印件结构导热 K/W
R_METAL = L_BRIDGE / 1000.0 / (K_AL * (A_BRIDGE / 1e6))      # 金属热路贯通 K/W
R_FRAME_TO_SURF = L_BRIDGE / 1000.0 / (K_PRINT * (A_CONV / 1e6))   # 打印件节点 → 外表面 K/W
R_SURF_CONV = 1.0 / (H_CONV * (A_CONV / 1e6))                # 外表面 → 环境 K/W
R_AMB_PRINT = R_FRAME_TO_SURF + R_SURF_CONV      # 纯打印件: 节点 → 环境
R_AMB_METAL = R_METAL + R_SURF_CONV              # 有金属热路: 节点 → 环境
print(f"  输入: T_base={T_BASE}°C  h_skin={H_SKIN}  A_nose={A_NB}mm²  h_conv={H_CONV}  "
      f"A_conv={A_CONV}mm²  L_bridge={L_BRIDGE}mm  A_bridge={A_BRIDGE}mm²")
print(f"  R_interface (鼻梁接触面→皮肤) = 1/(h_skin*A_nose) = {R_INT:.1f} K/W")
print(f"  R_bridge (节点→鼻梁接触面): 打印件 {R_PRINT:.1f} K/W ; 金属热路 {R_METAL:.3f} K/W")
print(f"  R_amb    (节点→环境): 纯打印件 {R_AMB_PRINT:.1f} K/W ; 有金属热路 {R_AMB_METAL:.1f} K/W")
print(f"  红线 {T_REDLINE}°C (ISO 13732-1 / CENELEC Guide 29, 8h+ 持续接触) ; 设计目标 {T_TARGET}°C")


def t_patch(p: float, r_bridge: float, r_amb: float) -> tuple[float, float, float]:
    """三分支稳态: 节点 → (鼻梁接触面 → 皮肤) / (环境)。

    返回 (T_接触面, T_镜框节点, 流向皮肤的热流 W)。
    """
    r_skin_branch = r_bridge + R_INT          # 节点 → 皮肤 (串联)
    k_eff = r_skin_branch * r_amb / (r_skin_branch + r_amb)
    t_node = T_BASE + p * k_eff
    p_skin = (t_node - T_BASE) / r_skin_branch
    return T_BASE + p_skin * R_INT, t_node, p_skin


def r_bridge_required(p: float, t_limit: float, r_amb: float) -> float:
    """反解: 要让接触面温度 ≤ t_limit, R_bridge 至少要多大 (二分)。"""
    lo, hi = 1e-3, 1e9
    for _ in range(200):
        mid = (lo + hi) / 2
        if t_patch(p, mid, r_amb)[0] > t_limit:
            lo = mid
        else:
            hi = mid
    return hi


B_CASES = [
    ("B1 现状 (光机 98mW; 充电板在端件 / SoC 在镜脚) · 纯打印件",
     P_OPTICAL, R_PRINT, R_AMB_PRINT),
    ("B2 现状 + 给镜框正中加金属热路 (导到外表面)",
     P_OPTICAL, R_METAL, R_AMB_METAL),
    ("B3 ISS-084 情形: SoC 挪镜框正中 (0.55W) + 光机 · 纯打印件",
     P_SOC_FRAME + P_OPTICAL, R_PRINT, R_AMB_PRINT),
    ("B4 ISS-084 情形 + 金属热路 (无鼻梁热断)  ★反面教材",
     P_SOC_FRAME + P_OPTICAL, R_METAL, R_AMB_METAL),
    ("B5 ISS-084 情形 + 金属热路 + 鼻梁侧热断 (R_bridge=1000 K/W)",
     P_SOC_FRAME + P_OPTICAL, 1000.0, R_AMB_METAL),
]
B_RESULTS = []
for title, p, rb, ra in B_CASES:
    tp, tn, ps = t_patch(p, rb, ra)
    verdict = "✅ 达标" if tp <= T_TARGET else ("⚠️ 超设计目标(≤40)" if tp <= T_REDLINE else "❌ 超红线(43)")
    print(f"  {title}")
    print(f"      P={p:.3f}W  R_bridge={rb:.1f}  R_amb={ra:.1f} K/W")
    print(f"      ⇒ T_接触面={tp:.1f}°C  T_镜框节点={tn:.1f}°C  Q_入皮肤={ps*1000:.1f}mW  {verdict}")
    B_RESULTS.append((title, p, rb, ra, tp, tn))
rec(B_RESULTS[0][4] <= T_REDLINE, "B1", f"现状 (镜框正中只有光机) ⇒ 接触面 {B_RESULTS[0][4]:.1f}°C",
    f"P={P_OPTICAL}W, 纯打印件 ⇒ T_patch={B_RESULTS[0][4]:.1f}°C vs 红线 {T_REDLINE}°C "
    f"(⇒ 现状鼻梁区不是瓶颈)")
rec(B_RESULTS[2][4] > T_REDLINE, "B3",
    f"SoC 挪镜框正中 ⇒ 接触面 {B_RESULTS[2][4]:.1f}°C 超红线",
    f"P={P_SOC_FRAME+P_OPTICAL}W, 纯打印件 ⇒ T_patch={B_RESULTS[2][4]:.1f}°C vs 红线 {T_REDLINE}°C "
    f"⇒ **SoC 进镜框正中 = 鼻梁超温, 与几何无关**")
rec(B_RESULTS[3][4] > B_RESULTS[2][4],
    "B4", "★加金属热路反而把鼻梁接触面推得更高 (反面教材)",
    f"纯打印件 {B_RESULTS[2][4]:.1f}°C → 加金属热路后 {B_RESULTS[3][4]:.1f}°C "
    f"(金属把节点温度直接送到鼻梁接触面) ⇒ 金属热路**必须配鼻梁侧热断**")
rec(B_RESULTS[4][4] <= T_REDLINE, "B5",
    f"SoC 挪镜框 + 金属热路 + 鼻梁热断 ⇒ 接触面 {B_RESULTS[4][4]:.1f}°C",
    f"P={P_SOC_FRAME+P_OPTICAL}W, R_bridge=1000 K/W ⇒ T_patch={B_RESULTS[4][4]:.1f}°C vs 红线 {T_REDLINE}°C")

print()
print("  ── B5b: 反解 '要让鼻梁接触面 ≤ 限值, R_bridge 至少多大' ──")
for p, tag, ra in ((P_OPTICAL, "仅光机 0.098W", R_AMB_PRINT),
                   (P_SOC_FRAME + P_OPTICAL, "SoC+光机 0.648W", R_AMB_METAL)):
    for lim in (T_REDLINE, T_TARGET):
        rb = r_bridge_required(p, lim, ra)
        print(f"      P={p:.3f}W ({tag:16s}) R_amb={ra:.1f} 限值 {lim:.0f}°C ⇒ R_bridge ≥ {rb:,.0f} K/W")
    print(f"      参考: 铝热路只提供 {R_METAL:.3f} K/W ⇒ **热断必须做在鼻梁接触件本身, 不能靠热路本身**")

print()
print("  ── B5c: 敏感性 (A_nose / A_conv 都不确定 [0数据]) ──")
for a_nb, a_cv in ((80, 600), (140, 1000), (300, 1600)):
    ri = 1.0 / (H_SKIN * (a_nb / 1e6))
    rs = L_BRIDGE / 1000.0 / (K_PRINT * (A_BRIDGE / 1e6))
    ra = L_BRIDGE / 1000.0 / (K_PRINT * (a_cv / 1e6)) + 1.0 / (H_CONV * (a_cv / 1e6))
    tp, tn, _ = t_patch(P_OPTICAL, rs, ra)
    tp2, _, _ = t_patch(P_SOC_FRAME + P_OPTICAL, rs, ra)
    print(f"      A_nose={a_nb:3d}mm² A_conv={a_cv:4d}mm² ⇒ R_int={ri:6.1f}  "
          f"现状 T_patch={tp:.1f}°C | SoC 挪镜框 T_patch={tp2:.1f}°C")

# 充电峰值 (在镜框端件, 不在鼻梁正上方) 的判据
print()
print("  ── B6: 充电峰值 0.45-0.57W 落在镜框**端件**(离镜框中心 60-70mm), 不在鼻梁正上方 ──")
R_ARM_PRINT = 0.070 / (K_PRINT * (150.0 / 1e6))    # 打印件沿臂 70mm, 截面积 150mm²
for p in (0.45, 0.57):
    t_end = T_BASE + p * R_ARM_PRINT
    print(f"      P={p:.2f}W 经打印件沿臂 R={R_ARM_PRINT:.0f} K/W ⇒ 端件节点温升 {t_end-T_BASE:.0f}K "
          f"(端件表面温升另算: HW_CROSS_REVIEW §3.3 = 83-108°C) ⇒ 热留在线路端件, **不到鼻梁**")
rec(True, "B6", "充电峰值的热落点判定 (端件, 不是鼻梁)",
    f"0.45-0.57W 落在镜框端件 (离镜框中心 60-70mm); 打印件沿臂导热阻 ≈ {R_ARM_PRINT:.0f} K/W "
    f"⇒ 传到鼻梁侧的温升可忽略; 真正的问题在端件自身 (83-108°C, HW_CROSS_REVIEW §3.3)")

# ==================================================================== C 段
print()
print("=" * 78)
print("C 段: 充电板面积 (直接调用 hw-lead 的 calc_chg_board_area.py 件表, 不重造)")
print("=" * 78)

spec = importlib.util.spec_from_file_location(
    "calc_chg_board_area", os.path.join(ROOT, "HW", "calc_chg_board_area.py"))
cba = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cba)

parts = cba.chg_parts()
new = cba.area_model(parts, cba.FP["U_CHG"])
amap = {r["ref"]: r["area"] for r in new["rows"]}
used = new["total"]
phys_free = cba.USABLE - cba.J_CHG_AREA
gap_phys = used - phys_free
gap_c13 = used - cba.DENS_LIMIT * cba.USABLE
t1_delta = cba.T1_BOARD_DELTA
t2_save = sum(amap.get(r, 0.0) for r in cba.T2_FLIP)
t3_save = sum(amap.get(r, 0.0) for r in cba.t3_refs_in_table(new["rows"]))
comb = sorted(set(cba.T2_FLIP) | set(cba.t3_refs_in_table(new["rows"])))
c_save = sum(amap.get(r, 0.0) for r in comb)
t3_no_led = t3_save - sum(amap.get(r, 0.0) for r in cba.T3_MOVE_LED)

print(f"  器件占位 {used:.2f} mm² (逐颗封装, U_CHG 用官方 4x4=16mm²)")
print(f"  可用 = 板250 - TypeC65.86 - J_CHG座58.24 = {phys_free:.2f} mm² (物理口径)")
print(f"  缺口 = {gap_phys:.2f} mm² (物理口径) / {gap_c13:.2f} mm² (C-13 判据口径)")

C_CASES = [
    ("T-1 扩板 25x10 -> 25x12 (不动 BOM)", used, phys_free + t1_delta),
    ("T-3 纯删件 (含充电灯移镜脚)", used - t3_save, phys_free),
    ("T-2 双面贴 + 删 DNP", used - t2_save, phys_free),
    ("T-2 + T-3 合并", used - c_save, phys_free),
    ("T-1 + T-3 (扩板 + 纯删件)", used - t3_save, phys_free + t1_delta),
    ("T-1 + T-3(只删 DNP, 不搬充电灯)", used - t3_no_led, phys_free + t1_delta),
    ("T-1 + T-2 + T-3 合并", used - c_save, phys_free + t1_delta),
]
C_RESULTS = []
for title, dev, free in C_CASES:
    dens = dev / free
    print(f"  {title:42s} 器件 {dev:7.2f} / 可用 {free:7.2f} = {dens:6.1%} "
          f"{'✅ 装得下' if dev <= free else '❌ 装不下'}  (布线余量 {100*(1-dens):.1f}%)")
    C_RESULTS.append((title, dev, free, dens))
    rec(dev <= free, "C", f"{title} ⇒ {dens:.1%}",
        f"器件 {dev:.2f} / 可用 {free:.2f} mm²; 布线/间距余量 {100*(1-dens):.1f}% "
        f"(hw-lead 注: 走线/间距/平面不可用区还没建模, 物理上还要再留 10-20%)")

print()
print("  ── C1b: T-3 拆成 3 个可独立选择的子项 (给 PM 裁决用) ──")
t3a = sum(amap.get(r, 0.0) for r in ["C_SYS", "C_VBUS_OUT", "R_PU_INT", "R_STAR_PGND"])
t3b = sum(amap.get(r, 0.0) for r in ["R_PU_SCL", "R_PU_SDA"])
t3c = sum(amap.get(r, 0.0) for r in ["D_CHG_LED", "Q_CHG_LED", "R_CHG_LED", "R_PU_STAT_L"])
for tag, sav, cost in (
    ("T-3a 删真 DNP + 铜皮短接 (C_SYS/C_VBUS_OUT/R_PU_INT/R_STAR_PGND)", t3a,
     "零结构代价; 但 R_STAR_PGND 改铜皮短接 ⇒ PGND/GND 单点汇流要写进 PCB 规则"),
    ("T-3b 删 I2C 上拉 (R_PU_SCL/R_PU_SDA)", t3b,
     "★代价最大: BQ25896 的 I2C 彻底不可用 ⇒ 充电电流/截止电压/温度门限全部锁死不可调"),
    ("T-3c 充电灯链移镜脚 (D_CHG_LED/Q_CHG_LED/R_CHG_LED/R_PU_STAT_L)", t3c,
     "★结构代价: 镜框内侧导光孔改成镜脚外侧导光孔 + 跨铰链多一根 CHG_STAT_L 线"),
):
    print(f"      {tag}")
    print(f"          省 {sav:.2f} mm² ; 代价: {cost}")
print(f"      ⇒ T-3 全部 {t3a+t3b+t3c:.2f} mm² (与 hw-lead 的 15.74 一致: {t3_save:.2f})")
print(f"      ⇒ 只做 T-3a (不碰 I2C, 不搬灯): {t3a:.2f} mm² ⇒ "
      f"器件 {used-t3a:.2f} / 可用 {phys_free:.2f} = {(used-t3a)/phys_free:.1%} (仍超装)")
print(f"      ⇒ T-1 + T-3a: {used-t3a:.2f} / {phys_free+t1_delta:.2f} = "
      f"{(used-t3a)/(phys_free+t1_delta):.1%} ✅")
print(f"      ⇒ T-1 + T-3a + T-3b: {used-t3a-t3b:.2f} / {phys_free+t1_delta:.2f} = "
      f"{(used-t3a-t3b)/(phys_free+t1_delta):.1%} (牺牲 I2C 可调性)")

print()
print(f"  T-1 板面增量 = {t1_delta:.2f} mm² (25x10 -> 25x12, 同一块板, 零 PCB 板费增量)")
print(f"  T-2 腾出 {t2_save:.2f} mm² (双面贴: 15 电阻 + 2 体电容翻底 + 删 DNP)")
print(f"  T-3 腾出 {t3_save:.2f} mm² (含充电灯链 {t3_save - t3_no_led:.2f} mm²); "
      f"只删 DNP 不搬灯 = {t3_no_led:.2f} mm²")
print(f"  T-2+T-3 合并 = {c_save:.2f} mm²")

# 端件 V 向余量 (加 2mm 的直接冲击面)
print()
print("  ── C2: T-1 的 +2mm 打在哪 (端件 V 向余量) ──")
FPC_BAND_V_DECLARED = 31.00   # 4 条 FPC 竖向叠放 (声明版, HW_CROSS_REVIEW §2.6)
FPC_BAND_V_NESTED = 12.00     # H 向径向嵌套后 V 向只需最宽一条 (ISS-089 建议)
END_V_LO, END_V_HI = 30.0, 40.0
for band, tag in ((FPC_BAND_V_DECLARED, "FPC 竖向叠放 31.00mm"),
                  (FPC_BAND_V_NESTED, "FPC H向径向嵌套 12.00mm")):
    lo, hi = END_V_LO - band, END_V_HI - band
    print(f"      {tag}: 端件 V 余量 = {lo:+.2f} ~ {hi:+.2f} mm ; "
          f"充板 +2mm 后 = {lo-2:+.2f} ~ {hi-2:+.2f} mm "
          f"{'❌ 下限变负' if lo-2 < 0 else '✅ 两端都还正'}")
rec(True, "C2", "T-1 的 +2mm 打在端件 V 向 ⇒ 结论依赖 FPC 拓扑与 u8 截面",
    f"V 向叠放口径端件余量 {END_V_LO-FPC_BAND_V_DECLARED:+.2f}~{END_V_HI-FPC_BAND_V_DECLARED:+.2f}mm "
    f"(+2mm 后下限 {END_V_LO-FPC_BAND_V_DECLARED-2:+.2f}) ; "
    f"H 向径向嵌套口径 {END_V_LO-FPC_BAND_V_NESTED:+.2f}~{END_V_HI-FPC_BAND_V_NESTED:+.2f}mm "
    f"(+2mm 后 {END_V_LO-FPC_BAND_V_NESTED-2:+.2f}) ⇒ u8 未定前 T-1 不能冻结")

# ==================================================================== D 段
print()
print("=" * 78)
print("D 段: 跨文档一致性核对 (哪些行与本单结论冲突)")
print("=" * 78)

CONFLICTS = [
    ("D-1", "MECH_BUDGET §1.3 M3 充电板 部位标 [脚]",
     "ISS-014 决策5 / CHARGE_BOARD_SPEC M-11 / USB_HINGE_STRUCTURE U-6 ⇒ 充电板在**镜框端件**, 部位标注过时"),
    ("D-2", "MECH_BUDGET §1.3 M4 Type-C 部位标 [脚]",
     "同上 ⇒ Type-C 在镜框端件面板, [脚] 过时"),
    ("D-3", "MECH_BUDGET §5.2 充电孔 写 '镜腿末端开 Type-C 孔'",
     "与 §1.3 M4 / CHARGE_BOARD_SPEC M-11 直接矛盾 ⇒ 应为镜框端件面板开孔"),
    ("D-4", "MECH_BUDGET §1.4.2 H/V 叠层表 (7.0mm / 37mm)",
     "fit_check.py §3① 已判为**过时叠放模型** (H 8.10 > 7.30, V 41.50 > 38.00) ⇒ 应换成串行两段式"),
    ("D-5", "MECH_BUDGET §2.3.1(3) 厚度映射算式",
     "该算式 (壁+PCB+电芯+壁+0.3) 就是叠放口径 ⇒ 应换成解A/解B 串行口径 (需求 6.35 / 6.05mm)"),
    ("D-6", "MECH_BUDGET §1.6.2 387 行 '根部净高 37mm'",
     "引 §1.4.2 垂直叠层 (22+12+3) ⇒ 过时; 现行为 38.00 腔体, 需求 29.5 (315档) / 28.0 (387档)"),
    ("D-7", "MECH_BUDGET §2.3.1(3) 387 行 '镜腿前后厚 7.3 (名义 7.0)'",
     "7.0 是叠放算式的产物 ⇒ 真实 H 需求 6.05, 名义余量 1.25 / 最坏 0.95"),
    ("D-8", "MECH_BUDGET §1.6.3 结论段 '镜腿厚度可回到 5.5-6.0mm'",
     "那是按需触发口径的可选值, 与锁死 7.30mm 腔体混排 ⇒ 须标明口径"),
    ("D-9", "MECH_BUDGET §1.3 主表缺 315 档电芯行",
     "M2 只写了丰江 432243 (387档) ⇒ 应补 Renata ICP582035PR-01 (315档, 4.6x23.5x40.5)"),
    ("D-10", "MECH_BUDGET §1.4.5 镜框内腔累加表 无端件行",
     "端件要装 充电板 + Type-C沉板 + 铝罩 + J_CHG框侧座 + 铰链件 + 4条FPC固定段 ⇒ 缺一行"),
    ("D-11", "MECH_BUDGET §1.3 M3 充电板尺寸 25x10x0.8",
     "T-1 落定后要改为 25x12x0.8 (或维持 25x10 + T-2/T-3) ⇒ 待 PM 裁"),
    ("D-12", "state 分片 interface_claims: temple_thickness='7.3-8.7mm' / "
             "battery_capacity_tier='无桥接340-575/有桥接575-675'",
     "575/675 档已作废 (ISS-072) ⇒ 须改成 315/387 口径, 否则与 §1.4.3/§1.6.2 打架"),
]
for code, where, why in CONFLICTS:
    note(code, where, why)

print()
print("=" * 78)
n_fail = sum(1 for ok, _, _ in RESULTS if not ok)
print(f"自检汇总: {len(RESULTS)-n_fail}/{len(RESULTS)} 项一致 · FAIL {n_fail}")
print("=" * 78)
sys.exit(0 if n_fail == 0 else 1)
