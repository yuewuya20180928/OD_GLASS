#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
board_width_15mm_check.py —— ISS-100 板宽 12→15mm 结构侧连带复核 (mech-lead)
=====================================================================
为什么有这个脚本:
  老板 2026-10-27 拍板 **板宽 = 15mm** (不再评估 12mm)。本脚本把这条决定
  落成**可复算的结构数字**, 回答 4 个问题:
    Q1 镜脚腔体 (H 前后 / V 垂直 / L 长度) 在 15mm 板宽下还过不过?
    Q2 J_CHG 座体能不能装进 15mm 板宽? (ISS-085/ISS-091 遗留的 [FAIL])
    Q3 面积缺口 300mm² 被 15mm 吸收了多少? 剩多少? 加长补得了吗?
    Q4 PCB 定位孔位 (ISS-049) 在 15mm 板宽下的可达性?

口径声明 (★所有结论都受这三条约束):
  ① **排布 = 沿长度串行** (电池与 PCB 沿长度排, 镜脚 7.3mm 内叠放物理不成立,
     已被 MECH/fit_check.py 用 H/V/L 三重证明裁决作废)。板宽 12→15 是**垂直向 (V)**
     尺寸, **不进前后 (H) 尺寸链**。
  ② **公差判据**: 每条余量 ≥ 2 × 单边公差 = 2 × 0.30 = **0.60mm** (FDM 外形)。
  ③ 面积模型沿用 HW/PCB_FORM_FACTOR_RECHECK.md §5.3 的口径 (land 542 + 逃线 113,
     利用率双面贴 0.72 / 单面贴 0.60), 该模型自身标 [推算] 误差带 ±25%。

证据等级: 本脚本全部输出是 **[推算]** (设计态几何 + 公差栈, 非物理实测)。
用法: python3 MECH/board_width_15mm_check.py [--json]
退出码: 0 = 报告生成 (结论看最后一节, 不代表实物已验)
"""
from __future__ import annotations

import json
import sys

# =====================================================================
# 输入 —— 全部标来源
# =====================================================================
BASE = {
    # 镜脚内腔 (MECH_BUDGET §1.6.2, 解 A 口径)
    "cav_h":        7.30,    # 镜脚外厚 (前后) —— 老板 19:16 锁死 340mAh/7.3mm
    "cav_v":       38.00,    # 根部净高 (垂直)
    "cav_l":      130.00,    # 内腔长
    "wall":         0.80,   # 打印件单壁 (MECH_BUDGET §5.4, FDM 最小可靠壁)
    "pad_thermal":  0.50,   # 皮肤侧隔热垫 (解 A, 只在 PCB/SoC 段)
    "air_gap":      0.30,   # 皮肤侧空气隙 (解 A)
    "pad_soc":      0.30,   # SoC 下方导热垫
    "frame_thk":    1.00,   # 铝/铜骨架厚 (MECH_BUDGET §5.1)
    "pcb_thk":      0.80,   # PCB 厚 (4 层); 6 层 = 1.00
    # 电芯 (解 A: Renata ICP582035PR-01 340mAh 4.60 厚)
    "cell_thk":     4.60,
    "cell_v":      23.50,
    "cell_l":      40.50,
    # 走线槽 (MECH_BUDGET §5.6.2 口径: V 向 6.00 / H 向 2.00)
    "duct_v":       6.00,
    "duct_h":       2.00,
    # 连接器/弯折余量
    "conn_margin": 15.00,   # MECH_BUDGET §1.4.2
    # 铰链区 (MECH/USB_HINGE_STRUCTURE.md §3.2)
    "hinge_zone":  15.00,   # 铰链区轴向占位
    "fpc_t":        0.20,   # 4 层 FPC 成品厚 (1oz 全铜)
    "fpc_gap":      0.15,   # FPC 嵌套间隙
    "bend_R":       3.00,   # 弯折半径
    "socket_wall":  1.00,   # ZIF 座体两侧壁 (hinge_usb_check.py SOCKET_WALL_MM)
}

TOL = {"fdm_part": 0.30, "fdm_feat": 0.25, "cell": 0.15}
CRIT = 2 * TOL["fdm_part"]          # 0.60mm 判据

# PCB 候选板形 (板长 × 板宽)
BOARDS = [
    ("12mm (现状·待作废)", 50.0, 12.0),
    ("15mm (老板拍板)",    50.0, 15.0),
    ("15×60 (本单建议)",   60.0, 15.0),
]

# 跨铰链 4 条链路 (ISS-085 收敛版 / V1.6 网表实测)
LINKS = [("CONN_CAM", 18, 0.50), ("CONN_LIGHT", 22, 0.50),
         ("CONN_USB", 4, 0.50), ("J_CHG", 10, 0.50)]

# J_CHG 座体 (ISS-091 §5.1: 触点区 = 必装脚数 × pitch, 座体 = 触点区 + 2×壁)
JCHG_MUST = 9          # V1.8 网表: J_CHG 必装 9 pin (pin9 预留 DNP)
JCHG_SEAT_H = 2.00     # ZIF 座体高 (Hirose FH12 标准 flip-lock 2.0mm, [官方])
JCHG_PITCH_NOW = 1.27  # hinge_usb_check.py 现用值 (旧口径)
JCHG_PITCH_NET = 0.50  # 网表 V1.5 定稿 "1×10p@0.5mm"

# 面积模型 (HW/PCB_FORM_FACTOR_RECHECK.md §5.3)
AREA = {
    "land_mm2":      542.0,   # 器件 land 面积
    "escape_mm2":    113.0,   # SoC 逃线框
    "util_2side":    0.72,    # 双面贴利用率
    "util_1side":    0.60,    # 单面贴利用率
}
SOC_W = 8.0          # ARS45 封装宽 (官网 "宽度≤8mm")
ESCAPE_BAND = 0.80   # 逃线带宽 (每侧)

OUT = []
def emit(s=""):
    OUT.append(s)
    print(s)


def v(ok):
    return "✅ 通过" if ok else "❌ 不通过"


def section(t):
    emit()
    emit("=" * 96)
    emit(t)
    emit("=" * 96)


def main() -> int:
    res = {}
    section("【0】口径与输入 (全部 [推算], 源 MECH_BUDGET v1.1 / fit_check.py / USB_HINGE_STRUCTURE.md)")
    emit(f"  镜脚内腔: H {BASE['cav_h']:.2f} × V {BASE['cav_v']:.2f} × L {BASE['cav_l']:.2f} mm")
    emit(f"  公差判据: 每条余量 ≥ 2×{TOL['fdm_part']:.2f} = {CRIT:.2f} mm")
    emit("  排布口径: **沿长度串行** (叠放分支已由 fit_check.py 证伪作废) ⇒ 板宽是 V 向尺寸, 不进 H 链")

    # ------------------------------------------------------------------
    # Q1 镜脚腔体三方向复核
    # ------------------------------------------------------------------
    section("【1】Q1 镜脚腔体复核 (H 前后 / V 垂直 / L 长度)")
    q1 = {}
    for label, pl, pw in BOARDS:
        # H 向: 解 A 口径 (fit_check.py §2 解 A)
        #   电池段 H 链 = 皮肤壁 0.8 + 电池座深 4.75 + 顶板 0.8 = 6.35 (隔热垫/空隙只留 PCB 段)
        #   PCB  段 H 链 = 外壁 0.8 + 骨架 1.0 + PCB 0.8 + 空隙 0.3 + 隔热垫 0.5 + 皮肤壁 0.8
        #   铰链端 PCB 段 (J_CHG 座体 2.0 高, 装在皮肤侧): 座体顶替隔热垫+空隙
        seat = BASE["cell_thk"] + 0.15          # 非对称座深 4.75 (解 A)
        h_cell = BASE["wall"] + seat + BASE["wall"]
        h_pcb = BASE["wall"] + BASE["frame_thk"] + BASE["pcb_thk"] + BASE["air_gap"] \
                + BASE["pad_thermal"] + BASE["wall"]
        h_hinge = BASE["wall"] + BASE["frame_thk"] + BASE["pcb_thk"] + JCHG_SEAT_H + BASE["wall"]
        h_need = max(h_pcb, h_cell, h_hinge)
        h_margin = BASE["cav_h"] - h_need
        h_worst = h_need + TOL["fdm_part"]      # 对抗性最坏: 外形公差 +0.30
        h_margin_w = BASE["cav_h"] - h_worst
        # V 向: 电芯段 / PCB 段 (充电板已挪镜框, 段内只有 PCB + 走线槽)
        v_cell = BASE["cell_v"] + BASE["duct_v"]
        v_pcb = pw + BASE["duct_v"]
        v_need = max(v_cell, v_pcb)
        v_margin = BASE["cav_v"] - v_need
        # L 向
        l_need = BASE["cell_l"] + pl + BASE["conn_margin"]
        l_margin = BASE["cav_l"] - l_need
        ok = min(h_margin, v_margin, l_margin) >= CRIT
        emit(f"\n  ▸ {label}:  板 {pl:.0f} × {pw:.0f} mm")
        emit(f"      H 前后 : 需求 {h_need:.2f} (电芯段 {h_cell:.2f} / PCB 段 {h_pcb:.2f} / 铰链端+J_CHG座 {h_hinge:.2f})  vs {BASE['cav_h']:.2f} → 余 {h_margin:+.2f} mm (最坏 {h_margin_w:+.2f})  {v(h_margin_w>=CRIT)}")
        emit(f"             ★ **板宽是 V 向尺寸, 完全不进 H 链** → H 余量与 12mm 板宽时一字不差")
        emit(f"      V 垂直 : 需求 {v_need:.2f} (电芯段 {v_cell:.2f} / PCB 段 {v_pcb:.2f})  vs {BASE['cav_v']:.2f} → 余 {v_margin:+.2f} mm  {v(v_margin>=CRIT)}")
        emit(f"             ★ 板宽 12→15 只吃 **PCB 段**: {12+BASE['duct_v']:.2f} → {v_pcb:.2f} (该段余量 {BASE['cav_v']-v_pcb:+.2f} mm); 电芯段 {v_cell:.2f} 不变 → 整体余量 {v_margin:+.2f} mm **一字不差**")
        emit(f"      L 长度 : 需求 {l_need:.2f} (电芯 {BASE['cell_l']:.1f} + 板 {pl:.0f} + 余量 {BASE['conn_margin']:.0f}) vs {BASE['cav_l']:.2f} → 余 {l_margin:+.2f} mm  {v(l_margin>=CRIT)}")
        q1[label] = dict(pcb_l=pl, pcb_w=pw, h_need=h_need, h_margin=h_margin,
                         h_margin_worst=h_margin_w, h_pcb=h_pcb, h_hinge=h_hinge, h_cell=h_cell,
                         v_need=v_need, v_cell=v_cell, v_pcb=v_pcb, v_margin=v_margin,
                         l_need=l_need, l_margin=l_margin, ok=ok)
        res[label] = q1[label]

    # ------------------------------------------------------------------
    # Q2 J_CHG 座体 vs 板宽
    # ------------------------------------------------------------------
    section("【2】Q2 J_CHG 座体 vs 板宽 (ISS-085 hinge_usb_check.py 的 [FAIL] 复核)")
    emit(f"  必装脚数 = {JCHG_MUST} (V1.8 网表: pin9 预留 DNP)")
    emit(f"  座体宽 = 必装脚数 × pitch + 2×{BASE['socket_wall']:.2f} (socket_wall 与 hinge_usb_check.py 同口径)")
    emit()
    for pitch, tag in ((JCHG_PITCH_NOW, "脚本现用 1.27mm (旧口径)"),
                       (JCHG_PITCH_NET, "网表 V1.5 定稿 0.5mm")):
        zone = JCHG_MUST * pitch
        sock = zone + 2 * BASE["socket_wall"]
        emit(f"  ▸ pitch {pitch:.2f}mm [{tag}]")
        emit(f"      触点区 {zone:.2f} mm → 座体宽 {sock:.2f} mm")
        for label, pl, pw in BOARDS:
            emit(f"      vs 板宽 {pw:.0f}mm ({label}): 余 {pw - sock:+.2f} mm  {v(pw - sock >= CRIT)}")
        emit()

    # 铰链区垂直堆叠
    stack = sum(n * p for _, n, p in LINKS)
    emit(f"  铰链区垂直堆叠 (4 条 FPC 触点区宽度之和, 全 0.5mm pitch) = {stack:.2f} mm "
         f"vs 镜脚根部净高 {BASE['cav_h']*0+37.0:.1f} mm → 余 {37.0-stack:.2f} mm")
    # 铰链区径向
    radial = BASE["bend_R"] + len(LINKS) * (BASE["fpc_t"] + BASE["fpc_gap"])
    radial_avail = BASE["cav_h"] - 2 * BASE["wall"]
    emit(f"  铰链区径向占位 = R{BASE['bend_R']:.1f} + {len(LINKS)}×({BASE['fpc_t']:.2f}+{BASE['fpc_gap']:.2f}) = {radial:.2f} mm "
         f"vs 前后内净空 {radial_avail:.2f} → 余 {radial_avail-radial:.2f} mm")
    res["j_chg"] = dict(stack_v=stack, stack_v_margin=37.0 - stack,
                        radial=radial, radial_margin=radial_avail - radial,
                        seat_127=JCHG_MUST * JCHG_PITCH_NOW + 2 * BASE["socket_wall"],
                        seat_050=JCHG_MUST * JCHG_PITCH_NET + 2 * BASE["socket_wall"])

    # ------------------------------------------------------------------
    # Q3 面积缺口
    # ------------------------------------------------------------------
    section("【3】Q3 面积缺口账 (源 HW/PCB_FORM_FACTOR_RECHECK.md §5.3, 该模型自身标 [推算] ±25%)")
    raw = AREA["land_mm2"] + AREA["escape_mm2"]
    need2 = raw / AREA["util_2side"]
    need1 = raw / AREA["util_1side"]
    emit(f"  land {AREA['land_mm2']:.0f} + 逃线 {AREA['escape_mm2']:.0f} = {raw:.0f} mm²")
    emit(f"  所需板面积: 双面贴 {raw:.0f}/{AREA['util_2side']:.2f} = {need2:.0f} mm² | 单面贴 {raw:.0f}/{AREA['util_1side']:.2f} = {need1:.0f} mm²")
    emit(f"  真断电电路 (负载开关 + ON 下拉 + 周边) = 8-12 mm²  [项目总工 ISS-100 锚点]")
    emit()
    for label, pl, pw in BOARDS:
        a = pl * pw
        emit(f"  ▸ {label}: 板面积 {pl:.0f}×{pw:.0f} = {a:.0f} mm²")
        emit(f"      双面贴口径: 缺口 {need2-a:+.0f} mm²  (扣真断电 8-12 → {need2-a-12:+.0f} ~ {need2-a-8:+.0f})")
        emit(f"      单面贴口径: 缺口 {need1-a:+.0f} mm²")
    base_a = 50 * 12
    emit()
    emit(f"  ★ 15mm 板宽 (板长仍 50) 的吸收量 = {50*15-base_a:+.0f} mm² "
         f"(双面贴缺口 {need2-base_a:.0f} → {need2-50*15:.0f} mm², 吸收 {100*(need2-base_a-(need2-50*15))/(need2-base_a):.0f}%)")
    emit(f"  ★ 15×60 板: 面积 {60*15:.0f} mm² → 双面贴缺口 {need2-900:+.0f} mm² → **基本闭合**")
    res["area"] = dict(need_2side=need2, need_1side=need1,
                       gap_12=need2 - base_a, gap_15x50=need2 - 750, gap_15x60=need2 - 900)

    # ------------------------------------------------------------------
    # Q4 定位孔位可达性
    # ------------------------------------------------------------------
    section("【4】Q4 PCB 定位孔位可达性 (ISS-049)")
    emit(f"  SoC 封装宽 {SOC_W:.0f} mm (官网 '宽度≤8mm') 居中 + 逃线带 {ESCAPE_BAND:.2f} mm/侧")
    emit(f"  M1.2 螺钉孔: ⌀1.4, 孔心到板边 2.50 mm → 孔占板边 1.80-3.20 mm")
    emit(f"  器件距板边 ≥0.80 mm (MECH_BUDGET §5.1)")
    for label, pl, pw in BOARDS:
        comp = (pw - (SOC_W + 2 * ESCAPE_BAND)) / 2.0     # 器件带宽 (每侧)
        esc0 = (pw - (SOC_W + 2 * ESCAPE_BAND)) / 2.0      # 逃线带起点 (距板边)
        overlap = max(0.0, 3.20 - esc0)                    # 螺钉孔压逃线带的量
        emit(f"\n  ▸ {label}: 板宽 {pw:.0f} mm")
        emit(f"      SoC+逃线占 {esc0:.2f} → {pw-esc0:.2f} mm | 器件带 {comp:.2f} mm/边")
        emit(f"      M1.2 孔 (占 1.80-3.20) 与逃线带起点 {esc0:.2f} 的冲突量 = **{overlap:.2f} mm** "
             f"{'❌ 完全落在逃线带里' if overlap >= 1.40 else ('⚠️ 压逃线带' if overlap > 0 else '✅ 不冲突')}")
        emit(f"      SoC 边缘 → 板边净距 (横向热扩散通道) = {(pw-SOC_W)/2:.2f} mm")
    emit()
    emit("  ⇒ 处置 (建议): 2×M1.2 螺钉孔 **沿板长方向移到 SoC 逃线区之外**, 孔心到板边仍 2.50mm,")
    emit("     ⌀2.0 H7 定位销孔放在板中心线、SoC 前缘外 ≥4mm (负责长向定位, 靠近电池段)")
    res["mount"] = {}

    # ------------------------------------------------------------------
    section("【5】结论")
    ok_all = all(q1[k]["ok"] for k in q1)
    emit(f"  Q1 镜脚腔体: 15mm 板宽下 H/V/L 三方向余量 = "
         f"{q1['15mm (老板拍板)']['h_margin']:.2f}(最坏 {q1['15mm (老板拍板)']['h_margin_worst']:.2f}) / "
         f"{q1['15mm (老板拍板)']['v_margin']:.2f} / "
         f"{q1['15mm (老板拍板)']['l_margin']:.2f} mm  → {v(ok_all)} (判据 ≥{CRIT:.2f})")
    emit(f"  Q2 J_CHG: pitch 0.5mm 口径下座体 {res['j_chg']['seat_050']:.2f} mm → 15mm 板余 {15-res['j_chg']['seat_050']:.2f} mm ✅")
    emit(f"     (hinge_usb_check.py 现在报的 [FAIL] 用的是 1.27mm 旧口径 → 座体 {res['j_chg']['seat_127']:.2f} mm; **那是脚本口径过期, 不是板宽问题**)")
    emit(f"  Q3 面积: 15mm 吸收 {50*15-base_a:.0f} mm²; 15×60 → 双面贴缺口 {need2-900:+.0f} mm², 长度余量 "
         f"{BASE['cav_l']-(BASE['cell_l']+60+BASE['conn_margin']):.2f} mm ✅")
    emit(f"  Q4 定位孔: M1.2 孔必须沿板长错开出 SoC 逃线区 (15mm 下仍压 {max(0.0,3.20-(pw if False else (15-(SOC_W+2*ESCAPE_BAND))/2)):.2f} mm)")
    emit()
    emit("  结论: **15mm 板宽在镜脚腔体上装得下** (三方向余量全部 ≥ 判据);")
    emit("        **面积缺口靠 15×60 板基本闭合** (长度余量仍有 14.50mm);")
    emit("        **J_CHG 装不下的根因是 pitch 口径 (1.27 vs 0.5), 不是板宽** —— 修脚本比改板宽更直接。")
    emit()
    emit("  证据等级: 本脚本全部输出 = [推算] (设计态几何 + 公差栈)。")
    emit("  ★ 本脚本**不是**物理装配实测; state/measurements.yaml 的 M-FIT 仍是 [推算]。")

    if "--json" in sys.argv:
        with open("MECH/board_width_15mm.json", "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        print("\n[已写 MECH/board_width_15mm.json]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
