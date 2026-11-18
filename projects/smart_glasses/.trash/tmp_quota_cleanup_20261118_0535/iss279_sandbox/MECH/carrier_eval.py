#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CARRIER_EVAL v2 — SoC 载板化 / 模组化 的结构代价评估 (ISS-084)
=====================================================================
任务 (ISS-084 task_brief):
  "评估 SoC 载板化 (或模组化) 的结构代价: 在镜框主板位置加一层载板对
   板宽/厚度/堆叠/热/重量/装配 的影响 (给 3 档方案: 直接焊 / BTB 载板 / FPC 载板),
   并给出 是否值得 (结论可以是 不值得, 但要有数)。同时给 兜底路线 的可行性初判:
   用现成 AR9481/ARS45 模组做 EVT 样机来验证 ISP+显示+OD 全链路的可行性
   (要解决什么/差在哪)。不许拍板"

v2 相对 v1 的修正 (v1 的三个实算错误, 已在本文件顶部记录):
  ① **SoC 封装高度漏计**: fit_check.py 的 PCB/SoC 段 H 叠层 (4.50mm) 没有 SoC 封装
     (0.85mm) 的位置 —— SoC 必须在 PCB 与骨架之间 → 该段真实需求 **5.35mm**,
     余量 **1.95mm** (原报 2.80mm)。v1 用 2.80 算载板增量 → 结论偏松, 已改。
  ② **镜框上沿平面预算算错**: v1 用了"单侧 96mm", 实际镜框前框总宽 140mm, 扣两侧
     铰链区 15mm + 正中区占用 → 单侧连续段只有 **43mm**。v1 的"76/110mm"是错的。
  ③ **热扩散公式单位错**: v1 把铜箔厚度 35µm 当成 35e-3 m 代进 Carslaw 公式, 算出
     R_扩散 = 0.2 K/W (虚低 17 倍) → v2 修正后 **R_扩散 = 3.39 K/W**, 装法 2 结温抬升
     **+3.5°C** (不是 v1 的 +0.5°C)。

本脚本只做一件事: **把"载板化"的每一条结构代价变成可复算的数字**, 并给出
**结构侧的方向性判据**。**拍板权在项目总工 + 老板, 本脚本不拍板。**

口径声明 (与本项目其它脚本一致):
  · 设计态几何 + 面积/重量/热阻计算, **不是物理装配实测**
    → measurements.yaml 相关项 kind 仍写 [推算], 阶段门 G2 不认 (这是对的, 别改)。
  · 证据分级四档: [实测] / [官方] / [推算] / [0数据]
    —— 本脚本**没有任何一条 [实测]** (无实物), 全部 [推算] 或转引 [官方]/[0数据]。
  · 所有输入显式列在 SRC 表里, 每条带来源 + 证据等级, 可逐项复核。

用法: python3 MECH/carrier_eval.py
退出码: 0 = 报告已生成 (结论看最后一节; 不代表实物已验)
"""
from __future__ import annotations

import math

# =====================================================================
# 输入表 —— 每项: (值, 来源, 证据等级)
# =====================================================================
SRC = {
    # ---------- 镜脚侧 (MECH_BUDGET v1.1 / CLEARANCE_FIX) ----------
    "temple_cav_h":   (7.30,  "MECH_BUDGET §1.6.2 340mAh 档 镜脚外厚上限 (老板 19:16 Q4 锁死)", "[推算]"),
    "temple_cav_v":  (38.00,  "MECH_BUDGET §1.6.2 根部净高", "[推算]"),
    "temple_cav_l": (130.00,  "MECH_BUDGET §1.6.2 镜脚内腔长", "[推算]"),
    "wall":          (0.80,  "MECH_BUDGET §5.4 最小壁厚 (0.4 喷嘴 × 2 圈)", "[推算]"),
    "pad_thermal":   (0.50,  "MECH_BUDGET §2.4 对策 C 皮肤侧隔热垫", "[推算]"),
    "air_gap":       (0.30,  "MECH_BUDGET §2.4 对策 C 空气隙", "[推算]"),
    "pcb_thk_4L":    (0.80,  "MECH_BUDGET §5.1 PCB 厚 4 层", "[推算]"),
    "pcb_thk_6L":    (1.00,  "HW/PCB_FORM_FACTOR_RECHECK §6.4 6 层 → 1.0mm", "[推算]"),
    "pad_soc":       (0.30,  "MECH_BUDGET §5.1 SoC 下方导热垫", "[推算]"),
    "skeleton":      (1.00,  "MECH_BUDGET §5.1 铝/铜骨架厚 (v1.1 未给厚 → 假设 1.0)", "[推算]"),
    "cell_l":       (40.50,  "Renata ICP582035PR-01 340mAh 长", "[官网]"),
    "cell_thk":      (4.60,  "同电芯 厚", "[官网]"),
    "conn_margin":  (15.00,  "MECH_BUDGET §1.4.2 连接器/弯折/插拔余量", "[推算]"),
    # ---------- 镜框侧 (MECH_BUDGET §1.4.5 / CLEARANCE_FIX) ----------
    "frame_opt_h":  (11.80,  "MECH_BUDGET §1.4.5 镜框正中 光学舱 前后累加 (已锁前提)", "[推算]"),
    "frame_cam_h":  (10.00,  "MECH_BUDGET §1.4.5 镜框上沿 摄像头位 实际需求 10-12mm (取下限)", "[推算]"),
    "frame_cam_mod_h": (4.50, "MECH_BUDGET §1.4.5 摄像头模组厚 (镜头筒+AA+遮光罩 另计)", "[推算]"),
    "frame_cam_shade_h": (1.50, "MECH_BUDGET §1.4.5 遮光罩", "[推算]"),
    "frame_outer_len": (140.0, "MECH_BUDGET §3 W9 镜框外形 ~140×40×40mm", "[推算]"),
    "frame_outer_h":  (40.0,  "MECH_BUDGET §3 W9 镜框外形 高", "[推算]"),
    "lens_h":         (35.0,  "镜片高 (常规全框比例) → 上沿带高 = 40-35", "[推算]"),
    "hinge_zone":    (15.0,  "MECH_BUDGET §1.4.2 铰链区 ~15mm/侧", "[推算]"),
    "splitter_len":  (14.0,  "MECH_BUDGET §1.2 一拖二分光组件 ~14×10×6mm", "[推算]"),
    "cam_mod_len":   (10.0,  "MECH_BUDGET §1.3 M8 摄像头模组 ~10×10×4.5", "[推算]"),
    "chg_l":         (25.0,  "MECH_BUDGET §1.3 M3 充电板 25×10×0.8", "[推算]"),
    # ---------- SoC 封装 ----------
    "soc_w":          (8.0,  "ARS45 FCCSP 8×10mm (官网: 封装尺寸优化至 8*10mm)", "[官网]"),
    "soc_l":         (10.0,  "同上", "[官网]"),
    "soc_h":         (0.85,  "FCCSP 8×10 级别 封装高度 (行业常规 0.75-0.90 取中) —— ARS45 实际值 [0数据]", "[推算]"),
    "soc_escape":   (113.0,  "SoC 封装 + 逃线框 (p=0.5 → 9.6×11.6)", "[推算]"),
    # ---------- 面积模型 (HW/PCB_FORM_FACTOR_RECHECK §5.3) ----------
    "land_total":   (542.0,  "146 画入 + 42 外推 器件 land 合计", "[推算]"),
    "land_soc_decap":(30.0,  "SoC 就近去耦 ~30 颗 (必须与 SoC 同板)", "[推算]"),
    "util_2s":      (0.72,   "双面贴 land 占比 (布板利用率)", "[推算]"),
    # ---------- 连接器 (官网 / 原厂目录) ----------
    "btb_stack":    (1.50,   "Hirose DF40 0.4mm 叠高 1.5mm (DF40C-xxxDS-0.4V(51)); 系列 1.5-4.0mm", "[官方]"),
    "btb_pitch":    (0.40,   "DF40 0.4mm 触点节距", "[官方]"),
    "btb_len":      (13.60,  "DF40 60 位双排 长度 ≈ 0.4×(60/2)+~1.6 (据官网 A 尺寸表推)", "[推算]"),
    "btb_depth":    (3.38,   "DF40 系列 深 3.38mm", "[官方]"),
    "btb_pos":      (60,     "DF40 位数 10-100; 本项目按 ISS-081 最小引脚集 ~50 信号 + 电源地", "[官方]"),
    "fpc_conn_h":   (1.50,   "Hirose FH55 0.4mm 高 1.5mm (深 4.2) / FH52 0.5mm 高 2.0mm (深 5.7)", "[官方]"),
    "fpc_thk":      (0.30,   "FPC 触点区厚度 0.30±0.05mm", "[官方]"),
    "fpc_stiff":    (0.30,   "FPC SoC 区局部玻纤板补强 (FCCSP 焊点需刚性)", "[推算]"),
    # ---------- 材料 (通用值) ----------
    "k_cu":        (400.0,   "铜导热系数", "[官方]"),
    "t_cu":         (0.035,  "1oz 铜厚 35µm", "[官方]"),
    "fr4_cc":        (1.85,   "FR4 密度 g/cc", "[官方]"),
    "al_cc":         (2.70,   "铝密度 g/cc", "[官方]"),
    "pi_cc":         (1.40,   "聚酰亚胺+铜 FPC 复合密度 g/cc", "[推算]"),
    # ---------- 器件 (官方) ----------
    "soc_module_w": (45.0,   "机器人 SoM 级 核心板 (SOM3559C_A1 45×55mm 规格书)", "[官网]"),
    "soc_module_l": (55.0,   "同上", "[官网]"),
    # ---------- 整机重量 (MECH_BUDGET §3) ----------
    "wt_total_lo":  (48.9,   "315mAh 配置 整机重量下限", "[推算]"),
    "wt_total_hi":  (74.0,   "387mAh 配置 整机重量上限", "[推算]"),
    "wt_target_hi": (40.0,   "消费 AR 对标上限", "[推算]"),
    # ---------- 功耗 (HW/POWER_BUDGET_V2 §4.1) ----------
    "p_temple_full": (0.90,  "镜腿内满载发热量 (口径 a)", "[推算]"),
    "skin_limit":    (43.0,  "ISO 13732-1 烧伤阈值 43°C (持续接触)", "[官网]"),
    "skin_now":      (80.1,  "镜腿内满载 皮肤侧温度 (主口径)", "[推算]"),
    "skin_idle":     (37.5,  "镜腿只留电池时 皮肤侧温度", "[推算]"),
}
V = {k: v[0] for k, v in SRC.items()}

OUT = []
def say(s=""):
    OUT.append(s)
    print(s)


# =====================================================================
# 0. 口径 + v1 修正记录
# =====================================================================
def header():
    say("=" * 100)
    say("CARRIER_EVAL v2 — SoC 载板化/模组化 结构代价 (ISS-084) | 结构侧评估, **不拍板**")
    say("=" * 100)
    say("\n【0】口径")
    say("  · 设计态几何 + 面积/重量/热阻计算, **不是物理装配实测** → measurements.yaml kind 仍写 [推算]")
    say("  · 证据分级 [实测]/[官方]/[推算]/[0数据]; 本脚本 **[实测] 条数 = 0**")
    say("  · 拍板权在项目总工 + 老板; 本脚本末尾只给 **结构侧判据 + 方向**, 不给「应采用 X 方案」")

    say("\n【0-bis】★ v1 的三处实算错误 (本版已修正, 修正会改变结论方向)")
    h_old = (V["wall"] + V["pad_thermal"] + V["air_gap"] + V["pcb_thk_4L"]
             + V["pad_soc"] + V["skeleton"] + V["wall"])
    say(f"  ① **SoC 封装高度漏计**: fit_check.py 的 'PCB/SoC 段' H 叠层 = {h_old:.2f}mm, 余量 "
        f"{V['temple_cav_h']-h_old:.2f}mm")
    say(f"     → 但叠层顺序是 壁{V['wall']}+隔热{V['pad_thermal']}+空隙{V['air_gap']}+PCB{V['pcb_thk_4L']}"
        f"+**[SoC {V['soc_h']}]**+导热垫{V['pad_soc']}+骨架{V['skeleton']}+壁{V['wall']} —— **SoC 封装没有位置**")
    say(f"     → 该段真实需求 **{h_old+V['soc_h']:.2f}mm**, 余量 **{V['temple_cav_h']-h_old-V['soc_h']:.2f}mm**")
    say(f"     → **影响: 载板增量 (+2.1~2.3mm) 是拿 {V['temple_cav_h']-h_old-V['soc_h']:.2f}mm 余量去顶, "
        f"不是拿 2.80mm**。载板化的厚度账因此**收紧**。")
    say(f"  ② **镜框上沿平面预算算错**: v1 用 '单侧 96mm' → 实际: 前框总宽 {V['frame_outer_len']:.0f}mm, "
        f"扣两侧铰链区 {V['hinge_zone']:.0f}mm + 正中区 (分光 {V['splitter_len']:.0f} / 摄像头 {V['cam_mod_len']:.0f}) "
        f"→ **单侧连续段仅 43mm**")
    say("     → **影响: 载板化省下的主板长度 (76→69mm) 在镜框侧依然塞不下, 但在镜脚侧是决定性的** (见【2】)")
    say("  ③ **热扩散公式单位错**: v1 把铜箔厚 35µm 当成 35e-3 m 代进 Carslaw 公式 → 算出 R_扩散 = 0.2 K/W")
    say("     (虚低 17 倍) → v2 修正后 **R_扩散 = 3.39 K/W**, 装法 2 结温抬升 **+3.5°C** (不是 v1 的 +0.5°C)")


# =====================================================================
# 1. 三档方案定义 + SoC 位叠层
# =====================================================================
def tiers():
    say("\n【1】三档方案的物理定义")
    rows = [
        ("A 直接焊 (现状)", "SoC 直接回流在主板上; 球位图错 → **整块主板重投**"),
        ("B BTB 载板", "SoC + 逃线 + 就近去耦 放独立载板 (4 层); 载板用 60 位 0.4mm BTB **叠在**主板上"),
        ("C FPC 载板", "SoC 放载板/刚岛, 经 FPC 引出; FPC 可弯折 → **载板可与主板不在同一处**"),
        ("D 供应商模组 (兜底路线)", "买现成模组, 模组自带 SoC+DDR+PMIC+连接器; 主板只留接口"),
    ]
    for a, b in rows:
        say(f"    {a:<26} {b}")

    A = dict(name="A 直接焊", conn=0.0, brd=0.0, fpc=0.0, stiff=0.0, steps=1, new_parts=0)
    B = dict(name="B BTB 载板", conn=V["btb_stack"], brd=V["pcb_thk_4L"], fpc=0.0, stiff=0.0, steps=3, new_parts=2)
    C = dict(name="C FPC 载板", conn=V["fpc_conn_h"], brd=0.0, fpc=V["fpc_thk"], stiff=V["fpc_stiff"], steps=4, new_parts=3)
    D = dict(name="D 供应商模组", conn=V["btb_stack"], brd=1.00, fpc=0.0, stiff=0.0, steps=3, new_parts=2)

    say("\n  ★ SoC 位**前后叠层** (不含外壳壁/隔热/骨架 —— 那些是与载板无关的公共项)")
    say(f"    叠层顺序 (皮肤侧→外侧): 壁 {V['wall']} + 隔热 {V['pad_thermal']} + 空隙 {V['air_gap']} "
        f"+ 主板 {V['pcb_thk_4L']} + **[SoC {V['soc_h']}]** + 导热垫 {V['pad_soc']} + 骨架 {V['skeleton']} + 壁 {V['wall']}")
    base_h = (V["wall"] + V["pad_thermal"] + V["air_gap"] + V["pcb_thk_4L"] + V["soc_h"]
               + V["pad_soc"] + V["skeleton"] + V["wall"])
    say(f"    基线 (A, 4 层板): **{base_h:.2f}mm** vs 镜脚上限 {V['temple_cav_h']:.2f} → 余量 "
        f"**{V['temple_cav_h']-base_h:.2f}mm**")
    say(f"    (若按 6 层板 1.0mm: {base_h+0.2:.2f}mm → 余量 {V['temple_cav_h']-base_h-0.2:.2f}mm)")

    say("\n  ★ 载板化在 SoC 位**增加的厚度** (相对 A):")
    for t in (B, C, D):
        add = t["conn"] + t["brd"] + t["fpc"] + t["stiff"]
        t["add"] = add
        t["h"] = base_h + add
        say(f"    {t['name']:<26} +{add:.2f}mm  →  该段总需求 {t['h']:.2f}mm vs 镜脚 {V['temple_cav_h']:.2f} → "
            f"{'❌ 超 %.2fmm' % (t['h']-V['temple_cav_h']) if t['h'] > V['temple_cav_h'] else '✅ 余 %.2fmm' % (V['temple_cav_h']-t['h'])}")
    say(f"\n    ⚠️ **关键结论 1**: B/C 两档在**镜脚里都装不下** (分别超 {B['h']-V['temple_cav_h']:.2f} / "
        f"{C['h']-V['temple_cav_h']:.2f}mm)")
    say(f"       → 载板化**强制 SoC 必须在镜框** → 主板也必须跟着去镜框 (BTB 是叠装, FPC 才可分家)")
    say(f"    ⚠️ **关键结论 2**: 对照镜框 —— 上沿摄像头位 {V['frame_cam_h']:.0f}mm 里已占 "
        f"摄像头 {V['frame_cam_mod_h']:.1f} + 遮光罩 {V['frame_cam_shade_h']:.1f} = "
        f"{V['frame_cam_mod_h']+V['frame_cam_shade_h']:.1f}mm → 余 "
        f"{V['frame_cam_h']-V['frame_cam_mod_h']-V['frame_cam_shade_h']:.1f}mm")
    say(f"       载板位还要 壁{V['wall']}+载板{V['pcb_thk_4L']}+SoC{V['soc_h']}+导热垫{V['pad_soc']}+壁{V['wall']} "
        f"= {V['wall']*2+V['pcb_thk_4L']+V['soc_h']+V['pad_soc']:.2f}mm (载板直接压金属骨架, 不再加背板) → "
        f"**{'✅ 塞得下' if V['frame_cam_h']-V['frame_cam_mod_h']-V['frame_cam_shade_h'] >= V['wall']*2+V['pcb_thk_4L']+V['soc_h']+V['pad_soc'] else '❌ 塞不下'}**")
    say(f"       → **载板位在镜框上沿是'刚好'级 (余量 "
        f"{V['frame_cam_h']-V['frame_cam_mod_h']-V['frame_cam_shade_h']-(V['wall']*2+V['pcb_thk_4L']+V['soc_h']+V['pad_soc']):.2f}mm)**, "
        f"**没有决策余量** → 必须等 u8 镜框截面才能判")
    return A, B, C, D, base_h


# =====================================================================
# 2. 面积账
# =====================================================================
def areas(B, C):
    say("\n【2】面积账 (板宽 / 板长 / 总 PCB 面积)")
    say(f"  模型 (HW/PCB_FORM_FACTOR_RECHECK §5.3): land {V['land_total']:.0f} + SoC 逃线框 {V['soc_escape']:.0f} "
        f"= {V['land_total']+V['soc_escape']:.0f}mm² 占用 → /利用率 {V['util_2s']} = 所需板面积")

    conn_land = V["btb_len"] * V["btb_depth"]                 # 连接器本体占位 (两侧各一份)
    fanout = V["btb_len"] * (V["btb_depth"] + 3.0)            # 逃线扇出区 (估 3mm/侧)
    say(f"\n  连接器占位 (60 位 0.4mm BTB): 本体 {V['btb_len']:.1f}×{V['btb_depth']:.2f} = {conn_land:.0f}mm²; "
        f"含逃线扇出 ≈ {fanout:.0f}mm²/侧 [推算]")

    # --- A 直接焊 ---
    occ_A = V["land_total"] + V["soc_escape"]
    need_A = occ_A / V["util_2s"]
    len_A = need_A / 12.0
    say(f"\n  ── A 直接焊")
    say(f"     主板占用 {occ_A:.0f}mm² → 需板面积 **{need_A:.0f}mm²** → 板宽 12mm → 板长 **{len_A:.0f}mm**")
    say(f"     (与 hw-lead §8.2 一致: 76×12 = 912mm² 是唯一 ≥911 的 12mm 宽方案; MECH §5.1 写的 50mm **已过时**)")

    # --- B BTB 载板 ---
    occ_main_B = V["land_total"] - V["land_soc_decap"] + fanout
    occ_car_B = V["soc_escape"] + V["land_soc_decap"] + conn_land + fanout
    need_main_B = occ_main_B / V["util_2s"]
    need_car_B = occ_car_B / V["util_2s"]
    len_B = need_main_B / 12.0
    say(f"\n  ── B BTB 载板 (SoC + 逃线 + 去耦 + 连接器 全上载板)")
    say(f"     主板占用 {occ_main_B:.0f} (原 {occ_A:.0f} − 去耦 {V['land_soc_decap']:.0f} + 连接器扇出 {fanout:.0f}) "
        f"→ 需 **{need_main_B:.0f}mm²** → 板宽 12 → 板长 **{len_B:.0f}mm**")
    say(f"     载板占用 {occ_car_B:.0f} → 需 **{need_car_B:.0f}mm²** → 载板 ~16×16mm")
    say(f"     ★ 主板长度 **{len_A:.0f} → {len_B:.0f}mm (−{len_A-len_B:.0f}mm)**")
    say(f"     ★ 总 PCB 面积 {need_A:.0f} → {need_main_B+need_car_B:.0f}mm² "
        f"(**{need_main_B+need_car_B-need_A:+.0f}mm² / {(need_main_B+need_car_B)/need_A*100-100:+.0f}%**)")
    say(f"     ★ 载板化让主板**变短** (SoC 逃线区从主板搬走了) —— 这是它唯一真正的面积收益")

    # --- C FPC 载板 ---
    occ_main_C = V["land_total"] - V["land_soc_decap"] + fanout * 0.7
    occ_car_C = V["soc_escape"] + V["land_soc_decap"] + conn_land + fanout * 0.7 + V["stiff_area"] if False else \
                V["soc_escape"] + V["land_soc_decap"] + conn_land + fanout * 0.7
    need_main_C = occ_main_C / V["util_2s"]
    need_car_C = occ_car_C / V["util_2s"]
    len_C = need_main_C / 12.0
    say(f"\n  ── C FPC 载板 (连接器换成 FPC 座, 扇出略省; 载板面积与 B 同量级)")
    say(f"     主板需 **{need_main_C:.0f}mm²** → 板长 **{len_C:.0f}mm**; 载板需 **{need_car_C:.0f}mm²**")
    say(f"     ★ 总 PCB 面积 **{need_main_C+need_car_C:.0f}mm²** ({need_main_C+need_car_C-need_A:+.0f} vs A) "
        f"→ **与 B 同量级, 无本质优势**")
    say(f"     ★ C 相对 B 的唯一差异 = **载板可以不在主板旁边** (FPC 可弯折) → 见【5】架构决策树")

    # --- 镜脚长度账 (载板化在这里是不是真收益) ---
    say("\n  ── ★ 镜脚长度账 (这才是载板化真正的结构收益所在)")
    for name, L in (("A 直接焊", len_A), ("B BTB 载板", len_B), ("C FPC 载板", len_C)):
        need = V["cell_l"] + L + V["conn_margin"]
        marg = V["temple_cav_l"] - need
        say(f"     {name:<14} 电池{V['cell_l']:.1f} + 主板{L:.0f} + 余量{V['conn_margin']:.0f} = "
            f"**{need:.0f}mm** vs 镜脚内腔 {V['temple_cav_l']:.0f} → "
            f"{'❌ 超 %.1fmm' % (-marg) if marg < 0 else '✅ 余 %.1fmm' % marg}")
    say(f"     ★ **A 直接焊在镜脚里超长 {V['cell_l']+len_A+V['conn_margin']-V['temple_cav_l']:.1f}mm** "
        f"(这是 hw-lead §7.2 ME-2 已标的问题)")
    say(f"     ★ **B/C 载板化把它修好了** (余 {V['temple_cav_l']-(V['cell_l']+len_B+V['conn_margin']):.1f}mm) "
        f"→ **载板化最硬的收益是这条, 不是风险隔离**")
    return dict(need_A=need_A, len_A=len_A, need_B=need_main_B + need_car_B, len_B=len_B,
                len_C=len_C, need_main_B=need_main_B, need_car_B=need_car_B,
                occ_main_B=occ_main_B, occ_car_B=occ_car_B)


# =====================================================================
# 3. 厚度堆叠 + 架构决策树 (载板到底该放哪)
# =====================================================================
def arch_tree(B, C, D, base_h, ar):
    say("\n【3】堆叠与架构决策树 —— 载板到底放在哪一端")
    say("  前置事实 (三条互相独立, 但共同决定架构):")
    say("   ① ISS-014 决策 5 (老板 10-25 19:23 拍板): **SoC + 充电板挪镜框**, 镜脚只留电池")
    say("   ② MECH/CLEARANCE_FIX §3.5 解 D: 'SoC+PCB 全部挪镜框' → **镜框没位置, 不可行** (需变更流程)")
    say("   ③ HW/SCHEMATIC_V1 (hw-lead 10-27): SoC 在**镜脚主 PCB**, 充电板在镜框 → 与 ① 不一致")
    say("  → **镜框主板位本身还没定**。所以载板化的结构代价必须分'主板在镜框/在镜脚'两种情形给。")

    say("\n  ── 情形 α: 主板 + 载板 **都在镜框** (BTB 叠装)")
    say(f"     镜脚只剩电池 → 皮肤侧 {V['skin_idle']:.1f}°C ✅ (MECH §2.3.1 降级方案 4)")
    say(f"     镜框要同时装: 主板({ar_len_B():.0f}×12) + 载板(16×16) + 充电板(25×10) + 摄像头(10×10) + 分光组件(14×10×6)")
    say(f"     ✗ **解 D 判定镜框没位置** —— 载板化不改变这个判定 (主板还是那块大板)")
    say(f"     → **α 档不值得**: 付出 +{B['add']:.2f}mm 厚度 +{(ar['need_B']/ar['need_A']-1)*100:.0f}% 面积, 换来的主板位置仍然不存在")

    say("\n  ── 情形 β: 主板留**镜脚**, 载板 (FPC) 挪**镜框** (只有 C 档能做)")
    say(f"     镜脚: 主板 {ar_len_C():.0f}×12 + 电池 → 长度 ✅, 厚度 ✅ (SoC 不在镜脚)")
    say(f"     镜框: 载板(16×16) + 充电板(25×10) + 摄像头 + 分光 → 载板是小件, **空间上可行** ✅")
    say(f"     ✗ **但 FPC 跨铰链要带 1-2A 供电** (SoC 域 550mW/0.8V×1.5 = 1.03A, HW/POWER_BUDGET_V2 §10)")
    say(f"        → 这正是 **MECH 解 C 被否掉的那条可靠性风险** ('跨铰链 1-2A 充电电流 = 屈寿命 = 最大新风险')")
    say(f"     → β 档 = 用一条**已判不可行的可靠性路线**换空间 → 结构侧不推荐, 需老板拍板")

    say("\n  ── 情形 γ: 主板 + 载板 **都在镜脚**")
    say(f"     厚度: {B['h']:.2f}mm (B) / {C['h']:.2f}mm (C) vs 镜脚 {V['temple_cav_h']:.2f} → "
        f"{'❌ 超 %.2f' % (B['h']-V['temple_cav_h']) if B['h']>V['temple_cav_h'] else '✅'}"
        f" / {'❌ 超 %.2f' % (C['h']-V['temple_cav_h']) if C['h']>V['temple_cav_h'] else '✅'}")
    say(f"     → **γ 档直接出局** (镜脚里根本放不下 SoC + 载板)")
    return dict(alpha_bad=True, beta_hinge_amps=1.03, gamma_impossible=True)


def ar_len_B():
    return (V["land_total"] - V["land_soc_decap"] + V["btb_len"]*(V["btb_depth"]+3.0)) / V["util_2s"] / 12.0


def ar_len_C():
    return (V["land_total"] - V["land_soc_decap"] + V["btb_len"]*(V["btb_depth"]+3.0)*0.7) / V["util_2s"] / 12.0


# =====================================================================
# 4. 热
# =====================================================================
def thermal(B):
    say("\n【4】热 —— 载板化**不产生散热收益**, 只决定热从哪走 + 引入多少新热阻")
    say(f"  现状 (MECH §2.6): 镜腿内满载 {V['p_temple_full']:.2f}W → 皮肤侧 **{V['skin_now']:.1f}°C** "
        f"vs 43°C 红线 → 差 5-6 倍; 待机 {0.05:.2f}W → 37.5°C")
    say(f"  ★ 载板化**不改变**这三个数字: 发热功率不变 / 皮肤侧面积不变 / 43°C 红线不变")
    say(f"  ★ 载板化只做一件事: **把发热件挪到哪个皮肤区** —— 镜框侧同样适用 43°C "
        f"(ISO 13732-1 持续接触), 所以 '挪镜框' ≠ '解决散热'")

    say("\n  ── 载板位的两种装法 (决定 SoC 的热能不能走到金属件)")
    say("    装法 1 【载板背面压金属衬板/骨架】(推荐):")
    say("             热路: SoC → 载板过孔 → 背面铜面/金属衬板 → 骨架 → 石墨 → 对流")
    say("             ⇒ BTB 连接器**不在热路上** → 对结温**零惩罚**")
    say("             ⇒ 代价: 新增 1 件金属衬板 (机加工件, 违反 '打印件负责容纳' 需说明)")
    say("    装法 2 【热必须穿过 BTB 连接器】:")
    say("             热路: SoC → 载板内横向扩散 → 连接器触点 → 主板 → 骨架")

    # 装法 2 定量: 载板内横向扩散 (薄膜环形扩散, Carslaw)
    #   t 用米; r1 = SoC 散热焊盘等效半径, r2 = 连接器触点区等效半径
    t_m = V["t_cu"] / 1000.0                              # 0.035mm → 3.5e-5 m
    r1 = math.sqrt(V["soc_w"] * V["soc_l"] / math.pi) / 1000.0   # 等效半径 (m)
    r2 = (V["btb_len"] / 2.0) / 1000.0                   # 连接器触点区等效半径 (m)
    R_spread = (1.0/(2*math.pi*V["k_cu"]*t_m)) * math.log(r2/r1)
    R_conn = 0.5
    R_tot = R_spread + R_conn
    say(f"\n    装法 2 定量 (薄膜环形扩散, Carslaw):")
    say(f"      SoC 散热焊盘等效半径 r1 = {r1*1e3:.2f}mm (8×10mm 焊盘); "
        f"连接器触点区等效半径 r2 = {r2*1e3:.1f}mm ({V['btb_len']:.1f}mm 长)")
    say(f"      R_扩散 = (1/(2π·k·t))·ln(r2/r1) = (1/(2π·{V['k_cu']:.0f}·{t_m*1e6:.0f}e-6))·"
        f"ln({r2*1e3:.1f}/{r1*1e3:.2f}) = **{R_spread:.2f} K/W**   [t = {V['t_cu']*1e3:.0f}µm 铜箔]")
    say(f"      R_连接器界面 ≈ **{R_conn:.1f} K/W** [推算, 无实测]")
    say(f"      装法 2 新增总热阻 ≈ **{R_tot:.1f} K/W**")
    say(f"      → 镜腿内 {V['p_temple_full']:.2f}W 时结温抬升 **+{V['p_temple_full']*R_tot:.1f} °C** "
        f"(对照基线 R(结→皮肤) ≈ 54.5 K/W, Tj ≈ 84°C)")
    say(f"      ⇒ **装法 2 不是致命的, 但它是白给的** —— 镜框侧本来就得配金属件 (打印件 k=0.2, "
        f"加塑料隔断 +94 K/W, MECH §5.1)")
    say(f"      ⇒ 两条装法的差别不是 '热行不行', 是 **'镜框要不要多一个金属件'** (装法 1 要, 装法 2 不要)")
    return dict(R_spread=R_spread, R_conn=R_conn, R_tot=R_tot, dT=V["p_temple_full"]*R_tot)


# =====================================================================
# 5. 重量
# =====================================================================
def mass(B, C, D, ar):
    say("\n【5】重量增量")
    # B: 载板 16×16×0.8 FR4 + BTB (一侧装在载板上, 主板侧算在主板里) + 金属衬板 16×14×0.8 Al
    m_car_B = 16.0*16.0*V["pcb_thk_4L"]/1000.0*V["fr4_cc"]
    m_btb = 0.20
    m_plate_B = 16.0*14.0*0.80/1000.0*V["al_cc"]
    mB = m_car_B + m_btb + m_plate_B
    # C: FPC 30×20×0.3 + 刚岛 16×14×0.3 FR4 + FPC 座 + 金属衬板
    m_fpc = 30.0*20.0*V["fpc_thk"]/1000.0*V["pi_cc"]
    m_stiff = 16.0*14.0*V["fpc_stiff"]/1000.0*V["fr4_cc"]
    m_conn_f = 0.25
    mC = m_fpc + m_stiff + m_conn_f + m_plate_B
    # D: 模组级
    mD = 11.0
    for t, m, desc in ((B, mB, "载板 16×16×0.8 FR4 + BTB 0.20 + 金属衬板 16×14×0.8 Al"),
                       (C, mC, "FPC 30×20×0.3 + 刚岛 16×14×0.3 + FPC座 0.25 + 金属衬板"),
                       (D, mD, "机器人核心板级模组 + 散热片 (估)")):
        t["mass"] = m
        t["mass_desc"] = desc
    say(f"    A 直接焊     : +0.00 g")
    say(f"    B BTB 载板   : +{mB:.2f} g  ({m_car_B:.2f} 载板 + {m_btb:.2f} BTB + {m_plate_B:.2f} 金属衬板)")
    say(f"    C FPC 载板   : +{mC:.2f} g  ({m_fpc:.2f} FPC + {m_stiff:.2f} 刚岛 + {m_conn_f:.2f} 座 + {m_plate_B:.2f} 衬板)")
    say(f"    D 供应商模组 : +{mD:.2f} g  ({mD:.1f} 模组级 + 散热片估)  ← **单项就 +{mD/V['wt_total_lo']*100:.0f}% 整机**")
    say(f"\n    整机基线 {V['wt_total_lo']:.1f}-{V['wt_total_hi']:.1f} g vs 对标 ≤{V['wt_target_hi']:.0f} g "
        f"(已超 +{(V['wt_total_lo']/V['wt_target_hi']-1)*100:.0f}% ~ +{(V['wt_total_hi']/V['wt_target_hi']-1)*100:.0f}%)")
    say(f"    → B 档 +{mB:.2f}g = 再 +{mB/V['wt_total_lo']*100:.1f}% (可忽略) | "
        f"D 档 +{mD:.1f}g = 再 +{mD/V['wt_total_lo']*100:.0f}% (**形态否决级**)")
    return dict(mB=mB, mC=mC, mD=mD)


# =====================================================================
# 6. 装配 / 零件 / 失效模式
# =====================================================================
def assembly(B, C, D, ar):
    say("\n【6】装配代价 / 新增零件 / 新增失效模式")
    rows = [
        ("A 直接焊", "1 次 SMT (主板)", "0", "0",
         "球位图/引脚映射错 → 整块主板重投 (6 层 ~910mm² 板)",
         "无新增"),
        ("B BTB 载板", "2 次 SMT (主板 + 载板) + 1 次对插", "1 块载板 + 1 颗 BTB + 1 件金属衬板", "3",
         f"球位图错 → 只重投载板 (4 层 ~{ar['need_car_B']:.0f}mm² 板, 面积 1/{ar['need_A']/ar['need_car_B']:.1f}) "
         f"✅ 风险从项目级降到载板级",
         "连接器对插不良 / 载板翘曲 (16×16 薄板 + SoC 集中载荷) / 上下分壳合缝方向限制装配顺序"),
        ("C FPC 载板", "2 次 SMT + 1 次 FPC 折弯 + 1 次对插", "1 块 FPC + 1 颗座 + 刚岛 + 金属衬板", "4",
         "同 B, 但 FPC 也要重投 (FPC 打样周期比 PCB 长, 且需折弯治具)",
         "同 B + FPC 弯折半径 ≥3mm 占空间 + 弯折疲劳 + FCCSP 焊在 FPC/刚岛上的工艺先例 [0数据]"),
        ("D 供应商模组", "1 次 SMT (主板) + 模组对插", "1 颗模组 (+ 散热片)", "3",
         "主板完全不动, 换模组即可换 SoC ✅ 风险隔离最彻底",
         "模组是黑盒: 引脚定义/电源时序/ISP 参数全靠模组厂; 采购与版本锁定风险; 体积/重量不可控"),
    ]
    for r in rows:
        say(f"    {r[0]}")
        say(f"      工序: {r[1]}   |  新增件: {r[2]}  (工序数 {r[3]})")
        say(f"      风险隔离收益: {r[4]}")
        say(f"      新增失效模式: {r[5]}")

    say("\n  ★ **装配顺序硬冲突 (B/C/D 都撞)**: 镜框/镜腿是 3D 打印**分体壳** (MECH §5.2 上下分壳),")
    say("    主板+载板必须在**合壳之前**装进去 → 载板/连接器的装配方向必须与合壳方向一致。")
    say("    载板若挂在主板**上方** (SoC 朝上) → 合壳时会被压到, 对插空间不足 →")
    say("    **SoC 必须朝内 (朝皮肤侧) 或主板朝下贴骨架** → 直接翻转现有 'SoC 远离皮肤侧' 的散热布局要求")
    say("    → 这条是 B/C/D 三档共同的**结构级冲突**, 且与 MECH §2.4 对策 A (上下分壳 + SoC 不贴皮肤) 直接矛盾。")
    say("    → **这是本单最硬的一条装配结论**: 载板化不是'多一颗连接器', 是'改 SoC 的朝向', 而朝向已经被散热定死了。")


# =====================================================================
# 7. 三条判据 + 方向性结论
# =====================================================================
def verdict(ar, th, ms, arch, A, B, C, D, base_h):
    say("\n【7】结构侧判据 (三条) + 方向性结论 (**拍板留给项目总工 + 老板**)")
    say("  判据 A 【载板化解决的是哪个风险?】")
    say("    A-1 ISS-081 已自证: 球数/封装**不是风险** (45-80 脚够, 8×10 FCCSP 放得下);")
    say("        真正卡住的只有**引脚→功能映射**。→ 载板化的目标应该是这个, 不是球位图。")
    say("    A-2 ★ **载板化不解除对原厂的依赖**: 载板自己也要球位图才能画 → 球位图永远不来, 载板一样做不出来。")
    say("        载板化只买到: '球位图来了但我们把功能映射搞错了' 这一种情形下, 重投的是 260mm² 小板不是 910mm² 大板。")
    say("    A-3 ⇒ 所以载板化的**真实价值 = 一次小板的成本**, 而不是'项目可以不等原厂'。")
    say("    A-4 唯一真正解开依赖的是 **D 档 (供应商模组)**: 模组厂自己出版引脚定义表 (ISS-083 正在做的事)。")

    say("\n  判据 B 【结构代价打在真约束上了吗?】")
    say(f"    B-1 厚度: B +{B['add']:.2f}mm / C +{C['add']:.2f}mm, 打在镜脚 SoC 位 "
        f"(余量只剩 {V['temple_cav_h']-base_h:.2f}mm) → **B/C 在镜脚里直接装不下**")
    say(f"    B-2 镜脚长度: A 直接焊 **超长 {V['cell_l']+ar['len_A']+V['conn_margin']-V['temple_cav_l']:.1f}mm** "
        f"(hw-lead ME-2 已标) → **载板化把它修成余 {V['temple_cav_l']-(V['cell_l']+ar['len_B']+V['conn_margin']):.1f}mm** ✅")
    say(f"        ⇒ **这是载板化唯一硬收益, 且是可量化的**")
    say(f"    B-3 镜框平面: 上沿单侧连续段只有 **43mm** (本单新算) → 主板 {ar['len_B']:.0f}mm 仍塞不下")
    say(f"    B-4 总 PCB 面积: A {ar['need_A']:.0f} → B {ar['need_B']:.0f}mm² "
        f"({ar['need_B']-ar['need_A']:+.0f} / {ar['need_B']/ar['need_A']*100-100:+.0f}%) → **面积没省, 只是搬家**")
    say(f"    B-5 重量: B +{ms['mB']:.2f}g (可忽略) | D +{ms['mD']:.1f}g (**形态否决级**)")
    say(f"    B-6 镜框上沿厚度: 载板位需求 {V['wall']*2+V['pcb_thk_4L']+V['soc_h']+V['pad_soc']:.2f}mm vs "
        f"上沿摄像头位剩 {V['frame_cam_h']-V['frame_cam_mod_h']-V['frame_cam_shade_h']:.1f}mm → **刚好级, 无决策余量**")

    say("\n  判据 C 【热与装配有没有被顺手解决?】")
    say(f"    C-1 载板化**不改变任何散热数字** ({V['skin_now']:.1f}°C / 43°C 红线 / 0.16-0.21W 上限 全部不变)")
    m_plate = 16.0*14.0*0.80/1000.0*V["al_cc"]
    say(f"    C-2 载板位要走到金属件 → 镜框现在是 3D 打印 (k=0.2) → **必须新增 1 件金属衬板** "
        f"({m_plate:.2f}g, 且是机加工件 → 违反「打印件负责容纳, 关键件机加工」需在 §5.5 登记)")
    say(f"    C-3 装法 2 (热穿连接器) 结温 +{th['dT']:.1f}°C; 装法 1 (金属衬板) ≈ 0 → "
        f"**代价落在'镜框多一个金属件', 不是落在温度**")
    say(f"    C-4 ★ **装配顺序冲突 (见【6】)**: 载板化 = 改 SoC 朝向, 与上下分壳 + SoC 不贴皮肤的既定布局矛盾")

    say("\n  ── 结构侧方向性判据 (**不是拍板**)")
    say("    ① **在「镜框主板位」这个字面提法下 (情形 α): 不值得** —— 因为解 D 已判镜框没位置,")
    say(f"       载板化不改变这个判定, 却要付 +{B['add']:.2f}mm 厚度 +{(ar['need_B']/ar['need_A']-1)*100:.0f}% 面积 "
        f"+{B['new_parts']} 件新增零件 +{B['steps']-1} 道工序。")
    say("    ② **在'镜脚主板位'这个提法下 (情形 γ): 不可能** —— B/C 在镜脚里厚度超差 "
        f"({B['h']-V['temple_cav_h']:.2f}/{C['h']-V['temple_cav_h']:.2f}mm)。")
    say("    ③ **真正有价值的是第三条**: 载板化把主板长度从 "
        f"{ar['len_A']:.0f}mm 压到 {ar['len_B']:.0f}mm, **修掉镜脚长度超差 "
        f"{V['cell_l']+ar['len_A']+V['conn_margin']-V['temple_cav_l']:.1f}mm** —— 这条收益跟「载板放哪」无关。")
    say("    ④ **所以结构侧的方向是: 值得做的不是'把 SoC 搬到镜框', 而是'把 SoC 从主板上拆下来做成载板',")
    say("       用来解决主板面积/长度; 至于载板装在镜框还是镜脚, 是被厚度和可靠性逼出来的结果, 不是目的。**")
    say("    ⑤ **但这件事的性价比取决于两个现在都是 [0数据] 的数**: 原厂球位图能不能来 (决定 A-2),")
    say("       以及 ISS-081 的引脚预算能不能缩到 50 脚以内 (决定连接器是 60 位还是 40 位, 决定载板 16×16 还是 12×12)。")
    say("    ⑥ **给项目总工的建议动作 (不是拍板)**: 先做 D 档台架 (ISS-083 已在做), 同时在主板上")
    say("       **预留 60 位 BTB 载板接口** (成本≈0: 只多一块 16×16 空板位 + 一颗连接器焊盘),")
    say("       这样 ISS-083 一旦拿到模组引脚表, **主板不用重投**。")
    say("    ⑦ **本条不替项目总工/老板拍板** —— 请裁: (a) 主板位到底定镜脚还是镜框 (解 D 走不走变更流程)")
    say("       (b) ISS-083 模组线是否升主线 (它是 A-1 的唯一现成解) (c) u8 镜框截面口径")


# =====================================================================
# 8. 兜底路线: 供应商 AR9481/ARS45 模组做 EVT
# =====================================================================
def fallback():
    say("\n【8】兜底路线初判 —— 用现成 AR9481/ARS45 模组做 EVT 样机, 验证 ISP+显示+OD 全链路")
    say("  ★ 先拆两件被混在一起的事:")
    say("    (i)  **台架 EVT** (桌面台架, 模组不戴在脸上) —— 验的是**软件/协议链**")
    say("    (ii) **眼镜形态 EVT** (模组进眼镜) —— 验的是**整机形态**")
    say(f"    ⇒ (ii) **几何否决**: 模组级参考 {V['soc_module_w']:.0f}×{V['soc_module_l']:.0f}mm "
        f"(SOM3559C_A1 规格书 [官网])")
    say(f"       镜脚内腔 {V['temple_cav_l']:.0f}×{V['temple_cav_v']:.0f}×{V['temple_cav_h']:.2f} → "
        f"模组高 {V['soc_module_l']:.0f} > 净高 {V['temple_cav_v']:.0f}, **超 {V['soc_module_l']-V['temple_cav_v']:.0f}mm**")
    say(f"       镜框上沿单侧连续段 43mm < 模组 {V['soc_module_w']:.0f}mm → 也否决")
    say(f"       ⇒ **模组只能上台架, 不能进眼镜**。'用模组做 EVT 样机' 这句话必须拆成两问。")

    say("\n  ── (i) 台架 EVT: **可行, 且是现成路径** ✅")
    can = [
        ("ISP 链路", "模组自带 ISP + 驱动 → 曝光/增益/帧率/中断/DMA 全链可跑", "✅"),
        ("OD 链路", "模组自带 NPU runtime → yolov5s INT8 640×640 可跑, 出框 + NMS", "✅"),
        ("显示链路", "若模组带 MIPI-DSI TX → 可直连走鹃Ⅱ; 若只有 DP/HDMI → **仍需桥接芯片, 这条验不到**", "⚠️ 看接口"),
        ("★显示 TX 判定", "模组规格书会写明视频输出接口类型 → **ISS-083 (DSI TX 到底是哪一种) 的最直接公开证据**", "✅✅"),
        ("★引脚→功能映射", "模组厂出版引脚定义表 + 原理图 → **直接绕开 ISS-081 的卡点**", "✅✅"),
        ("功耗构成", "分别关 ISP/NPU/显示测差值 → 给 sw-lead 一个**分项**功耗表 (比整机 1.22W 有用)", "✅"),
        ("端到端延迟", "台架可测 ISP→OD→合成→出光 段; 口径 A (曝光→出光) 需高速相机 + 光电探头", "⚠️ 需设备"),
    ]
    for a, b, c in can:
        say(f"    [{c}] {a:<14} {b}")

    say("\n  ── (i) 台架 EVT **要解决什么** (做之前必须先解决的)")
    must = [
        "① 模组选型: 必须能买到**引脚定义表公开**的 AR9481/ARS45 模组 (ISS-083 正在找, 我不外联)",
        "② 显示输出口必须是 MIPI-DSI 才能接走鹃Ⅱ; 若只有 HDMI/DP → 台架也得加桥接板, 验证价值打折",
        "③ CSI 摄像头输入: 模组的 CSI 口是否引出 + 能否驱动我们的 OV04C10/AR0234CS (可能得换模组自带 sensor)",
        "④ ISP 调参: 模组 ISP 是给机器人/扫地机 sensor 调的; 我们用鱼眼 120° → **LDC + 数字 shift 参数要在模组 SDK 上重做**",
        "⑤ 存储/启动: 模组自带 eMMC → 启动链/rootfs 分区/OTA 要按模组重做 (SW/FLASH_AND_VERSION)",
        "⑥ 供电: 机器人模组是 5V/12V 输入, 不是电池直供 → 台架要额外电源板; 且测不出眼镜形态的电池账",
        "⑦ 散热: 模组必须配散热片 (台架风冷) → **测出的满载功耗不能外推眼镜形态**",
    ]
    for m in must:
        say(f"    {m}")

    say("\n  ── (i) 台架 EVT **差在哪** (验不了什么)")
    gaps = [
        f"形态: 尺寸 / 佩戴 / 配重 —— 全验不了 (模组 {V['soc_module_w']:.0f}×{V['soc_module_l']:.0f}mm 进不去眼镜)",
        "重量: 模组级 +11g vs 整机 30-40g 目标 → 没有可比性",
        f"散热: 台架风冷 → 验不了镜腿 0.16-0.21W 上限 / 43°C 红线 (现状皮肤侧 {V['skin_now']:.1f}°C)",
        "续航: AR9481 ~1W (机器人预算) vs ARS45 <300mW → **台架功耗不能倒推电池档位**",
        "OD 延迟: AR9481 8TOPS vs ARS45 6TOPS (tracker §2.1: 640×640@60 ~11ms vs ~15ms) → **台架值偏乐观, 不能当 60ms 达标证据**",
        "ISP 画质: 模组 ISP 是机器人相机调的 → 我们的鱼眼 120° 畸变/LDC 要重调, 调不动就证不了",
        "引脚映射: 模组引脚 ≠ SoC 球位 → **模组证不了 ARS45 的球位图** (只证平台可行)",
        "光学链: 走鹃Ⅱ / 一拖二分光 / 波导 与 SoC 无关, 台架里挂不上 → 光学件仍全部 [0数据]",
    ]
    for g in gaps:
        say(f"    · {g}")

    say("\n  ── 兜底路线的**真正价值** (与 ISS-084 的关系)")
    say("    ★ 载板化 (B/C) 与 模组化 (D) **是同一个风险隔离机制的两端**:")
    say("      B/C = 我们自己造那块'引脚图隔离板' → 但**我们得有球位图才能造** → 死锁")
    say("      D   = 别人造那块板, 并附引脚表 → **死锁解开**")
    say("    ⇒ **先走 D (台架 EVT + 模组引脚表), 再决定要不要为 D 做一块适配主板**;")
    say("      **不要**在球位图 0 数据时先做 B/C 载板 —— 那是在赌原厂会回信。")
    say("    ⇒ 若最终确实要用模组进眼镜 (D 档), 几何已否决 → 那时唯一可行的是")
    say("      **主板预留载板/模组接口** (B 档接口的主板), 而不是把模组塞进眼镜。")
    return dict(mod_w=V["soc_module_w"], mod_l=V["soc_module_l"], can=len(can), gaps=len(gaps))


# =====================================================================
# 9. 自检
# =====================================================================
def selfcheck(ar, th, ms, arch, fbk, base_h):
    say("\n【9】自检 (断言)")
    checks = [
        ("B 档厚度增量 = 连接器 1.50 + 载板 0.80 = 2.30mm", abs(B_ADD - 2.30) < 1e-9),
        ("C 档厚度增量 = 连接器 1.50 + FPC 0.30 + 刚岛 0.30 = 2.10mm", abs(C_ADD - 2.10) < 1e-9),
        ("SoC 封装高度已计入 H 叠层 (v1 修正 ①)", abs(base_h - (V["wall"]+V["pad_thermal"]+V["air_gap"]+V["pcb_thk_4L"]+V["soc_h"]+V["pad_soc"]+V["skeleton"]+V["wall"])) < 1e-9),
        ("A 直接焊在镜脚里长度超差 > 0 (v1 修正 ② 的关联结论)", V["cell_l"]+ar["len_A"]+V["conn_margin"] > V["temple_cav_l"]),
        ("B 载板化把镜脚长度修成有余量", V["cell_l"]+ar["len_B"]+V["conn_margin"] <= V["temple_cav_l"]),
        ("B/C 两档在镜脚 SoC 位厚度超差 (装不下)", B_H > V["temple_cav_h"] and C_H > V["temple_cav_h"]),
        ("载板化不减总 PCB 面积 (只是搬家)", ar["need_B"] > ar["need_A"]),
        ("镜框上沿单侧连续段 = 43mm (v1 修正 ②)", abs(FRAME_SIDE - 43.0) < 1e-9),
        ("模组高 > 镜脚净高 → 眼镜形态几何否决", fbk["mod_l"] > V["temple_cav_v"]),
        ("D 档重量增量 > 整机重量的 10% (形态否决级)", ms["mD"]/V["wt_total_lo"] > 0.10),
        ("装法 2 结温抬升 < 10°C (不致命但白给)", th["dT"] < 10.0),
        ("本脚本 [实测] 条数 = 0 (无实物)", True),
    ]
    ok = True
    for name, res in checks:
        say(f"    {'✅' if res else '❌'} {name}")
        ok = ok and res
    say(f"\n  自检: {sum(1 for _, r in checks if r)}/{len(checks)} 通过")
    return ok


# 全局: 供自检引用的模块级常量 (由 tiers() 填)
B_ADD = C_ADD = B_H = C_H = FRAME_SIDE = 0.0


def main() -> int:
    global B_ADD, C_ADD, B_H, C_H, FRAME_SIDE
    header()
    A, B, C, D, base_h = tiers()
    B_ADD, C_ADD, B_H, C_H = B["add"], C["add"], B["h"], C["h"]
    ar = areas(B, C)
    FRAME_SIDE = (V["frame_outer_len"]/2 - V["hinge_zone"]) - 12.0   # 12 = 正中区半占
    arch = arch_tree(B, C, D, base_h, ar)
    th = thermal(B)
    ms = mass(B, C, D, ar)
    assembly(B, C, D, ar)
    verdict(ar, th, ms, arch, A, B, C, D, base_h)
    fbk = fallback()
    ok = selfcheck(ar, th, ms, arch, fbk, base_h)

    say("\n" + "=" * 100)
    say("结构侧方向性结论 (拍板权在项目总工 + 老板):")
    say(f"  · 字面提法'镜框主板位加一层载板' → **不值得** (解 D 已判镜框没位置, 载板化不改变判定)")
    say(f"  · '镜脚主板位加一层载板' → **不可能** (B/C 厚度超差 {B_H-V['temple_cav_h']:.2f}/{C_H-V['temple_cav_h']:.2f}mm)")
    say(f"  · 真正有价值的是: 载板化把主板长度 {ar['len_A']:.0f}→{ar['len_B']:.0f}mm, **修掉镜脚长度超差 "
        f"{V['cell_l']+ar['len_A']+V['conn_margin']-V['temple_cav_l']:.1f}mm** (这条与载板装哪无关)")
    say(f"  · 但载板化**不解除对原厂的依赖** (载板自己也要球位图) → 唯一现成解是 D 档 (模组引脚表, ISS-083)")
    say(f"  · D 档: 台架 EVT ✅ 可行 / 眼镜形态 ❌ 几何否决 (模组 {V['soc_module_w']:.0f}×{V['soc_module_l']:.0f}mm "
        f"vs 镜脚净高 {V['temple_cav_v']:.0f}mm)")
    say(f"  · 结构侧建议动作 (**建议, 非拍板**): ISS-083 模组线升主线 + 主板预留 60 位 BTB 载板接口 (成本≈0)")
    say("=" * 100)
    say("\n★ 口径: 本脚本是**设计态计算**, 不是物理装配实测 → measurements.yaml kind 仍写 [推算]; 阶段门 G2 不认 (这是对的)。")
    say("★ 本单 [实测] 条数 = 0。")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
