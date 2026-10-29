#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/skeleton_section_check.py —— 金属骨架截面形状 + 重量口径 + 石墨 H 链 的独立复算
=====================================================================
背景: 硬件总工 ISS-049 有两问**明确把决定权交给结构侧**:
      ① `iss049_skeleton_profile`  "请定截面形状(台阶/U形/槽形)并复核重量口径"
      ② `iss049_graphite_hchain`   "石墨 0.30mm 未进 PCB 段 H 链 ... 请在下一版 H 链补上并给装配位置"

      ★ 这两条**卡住本域 ISS-027 原型制作计划的 B3/B4 批** (镜框与光学批 / 整机装配批
        的金属机加工件就是这块骨架 + 石墨), 所以本脚本是对那两问的**可复现答复**。

★ 独立复算纪律 (同 `MECH/PCB_MOUNT_PIN_SET2.md` §1.3): **不共用 hw-lead 的代码路径**,
  输入全部显式列在文件头部, 每个数标来源。

★ 口径: 本脚本只做**算术复算 + 几何判定**, **不出新的皮肤侧温度数**
  (那要完整热模型重算, 见 `MECH/PCB_MOUNT_PIN_SET2.md` §5 U-3), **不拍板**
  (最终截面/厚度由项目总工裁)。

用法:
    python3 MECH/skeleton_section_check.py            # 人读报告
    python3 MECH/skeleton_section_check.py --json     # 机读

退出码: 0 = 复算完成 (不代表拍板); 1 = 输入自相矛盾
=====================================================================
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "..")

# ---------------------------------------------------------------------
# 输入 (全部来自既有文件, 每条标来源)
# ---------------------------------------------------------------------
AL_DENSITY = 2.70       # g/cc 铝               [官方·通用材料密度]
CU_DENSITY = 8.96       # g/cc 铜 (备选)         [官方·通用材料密度]
GR_DENSITY = 2.00       # g/cc 石墨片 (取 hw-lead ISS-049 报的 0.54g/片 反推的口径) [推算]

PCB_L = 60.00           # mm 板长              [决策] PROJECT_TRACKER §0 / HW/PCB_OUTLINE_60x15
PCB_W = 15.00           # mm 板宽              [决策] 老板 10-27
PCB_T = 1.00            # mm 6 层板厚 (取 1.00 保守) [决策]

# SoC 封装体 (FCCSP 8x10mm) 在**板坐标**里的占位:
#   X∈[21.00, 31.00] = 10.00mm 沿板长(X) ; Y∈[3.50, 11.50] = 8.00mm 沿板宽(Y)
#   [官网] 8x10mm + 板居中, 来源 HW/PCB_FIXING_PINSET2.md §2.2 表
SOC_X0 = 21.00         # mm 板坐标 X 起点
SOC_X_LEN = 10.00      # mm 沿板长
SOC_Y_LEN = 8.00       # mm 沿板宽 (V 向)
ESCAPE = 0.80          # mm 逃线带每边外扩    [HW/PCB_FIXING_PINSET2]
HOT_BAND = 3.50        # mm 横向扩散带每边 (15mm 板: (15-8)/2 = 3.50) [MECH/BOARD_WIDTH_15MM §2.6]

SKELETON_T = 1.00      # mm 骨架厚 (hw-lead 台阶形方案取值) [HW/PCB_FIXING_PINSET2 §4]
SKELETON_T_ALT = 0.80  # mm 备选厚度 (本脚本新增, 见重量账)
HOT_SEG_X0, HOT_SEG_X1 = 19.00, 33.00   # mm 台阶形满宽段的 X 范围 (hw-lead ISS-049 方案)
SEG_W_OTHER = 10.00    # mm 非 SoC 段的骨架宽度

GRAPHITE_T = 0.30      # mm 石墨片厚           [HW/PCB_FIXING_PINSET2 §4]

# PCB 段 H 链 (来源 MECH/BOARD_WIDTH_15MM.md §2.4 + MECH_BUDGET §2.3)
H_OUTER_WALL = 0.80
H_SKIN_WALL = 0.80
H_AIR_GAP = 0.30       # 隔热垫外侧空气隙
H_INSUL_PAD = 0.50     # 隔热垫 (0.5 硅胶/PI)
TEMPLE_H = 7.30        # mm 镜腿前后厚上限   [决策] 老板 Q4

# 热模型常数 (来源 MECH_BUDGET §2.3, 本脚本**只引用不复算**皮肤温度)
R_SKIN_PATH = 54.2     # K/W 皮肤路径         [推算] MECH_BUDGET §2.3
R_CONV = 667.0         # K/W 对流             [推算] MECH_BUDGET §2.3
R_AL_LONG = 4.50       # K/W 铝骨架纵向 (若延伸进电池段) [推算] MECH_BUDGET §2.3.1 / CLEARANCE_FIX §4.2
R_PRINT_LONG = 730.0   # K/W 打印件纵向        [推算] CLEARANCE_FIX §4.2

# 重量预算
BUDGET_SKELETON_G = 3.00     # g/对  MECH_BUDGET §2.4 B "金属骨架 +1-3g"
W11_GRAPHITE_G = (1.0, 2.0)  # g   MECH_BUDGET §3 W11 "石墨散热膜+导热垫+隔热垫 1-2" (整套)
TOTAL_PROTO_G = (48.9, 74.0)  # g  整机推算区间 [推算] MECH_BUDGET §3


def r6(x: float) -> float:
    return round(x + 1e-12, 6)


def skin_fraction(R_skin_path: float) -> float:
    """进入皮肤的热量比例 = R_conv/(R_skin_path + R_conv)  [MECH_BUDGET §2.3 模型]"""
    return 100.0 * R_CONV / (R_skin_path + R_CONV)


def compute() -> dict:
    r: dict = {"inputs": {}, "checks": [], "candidates": []}
    r["inputs"] = {
        "alu_density_g_cc": AL_DENSITY, "graphite_density_g_cc": GR_DENSITY,
        "pcb_L_mm": PCB_L, "pcb_W_mm": PCB_W, "pcb_t_mm": PCB_T,
        "soc_X0_mm": SOC_X0, "soc_X_len_mm": SOC_X_LEN, "soc_Y_len_mm": SOC_Y_LEN,
        "escape_mm": ESCAPE, "hot_band_each_side_mm": HOT_BAND,
        "skeleton_t_mm": SKELETON_T, "skeleton_t_alt_mm": SKELETON_T_ALT,
        "graphite_t_mm": GRAPHITE_T,
        "hot_seg_X_mm": [HOT_SEG_X0, HOT_SEG_X1], "seg_w_other_mm": SEG_W_OTHER,
        "H_chain_parts_mm": {"outer_wall": H_OUTER_WALL, "skeleton": SKELETON_T,
                              "pcb": PCB_T, "air_gap": H_AIR_GAP,
                              "insul_pad": H_INSUL_PAD, "skin_wall": H_SKIN_WALL},
        "temple_H_max_mm": TEMPLE_H,
        "R_skin_path_K_W": R_SKIN_PATH, "R_conv_K_W": R_CONV,
        "R_al_long_K_W": R_AL_LONG, "R_print_long_K_W": R_PRINT_LONG,
        "budget_skeleton_g_per_pair": BUDGET_SKELETON_G,
        "W11_graphite_g": list(W11_GRAPHITE_G),
    }

    def add(name, ok, detail, val=None):
        r["checks"].append({"name": name, "pass": bool(ok), "detail": detail, "value": val})

    # ---------- ① V 向覆盖需求 ----------
    v_need_15 = SOC_Y_LEN + 2 * HOT_BAND
    add("V_cover_need_15mm", abs(v_need_15 - PCB_W) < 1e-9,
        f"15mm 板: SoC 沿板宽占 {SOC_Y_LEN:.2f} + 两侧横向扩散带各 {HOT_BAND:.2f} = {v_need_15:.2f}mm "
        f"= 板宽 {PCB_W:.2f} -> **骨架在 SoC 段必须满宽** (不是 17, 8/10 轴向不能反)",
        v_need_15)
    v_need_12 = SOC_Y_LEN + 2 * 2.00
    add("V_cover_need_12mm", abs(v_need_12 - 12.0) < 1e-9,
        f"12mm 板: SoC {SOC_Y_LEN:.2f} + 两侧各 2.00 = {v_need_12:.2f}mm = 板宽 12.00 "
        f"-> 12mm 板**横向扩散带为零余量** (SoC 段骨架也必须满宽, 但没有 3.50 的扩散带) "
        f"—— 这是 15mm 的真正结构收益", v_need_12)

    # ---------- ②③ 候选截面 ----------
    hot_len = HOT_SEG_X1 - HOT_SEG_X0
    rest_len = PCB_L - hot_len

    cands = [
        ("A 满宽 60x15x1.0 (hw-lead 已判死)", [(PCB_L, PCB_W)], SKELETON_T, AL_DENSITY),
        ("B 台阶形 X19..33满宽15 / 其余10 x1.0", [(hot_len, PCB_W), (rest_len, SEG_W_OTHER)],
         SKELETON_T, AL_DENSITY),
        ("C 台阶形 X19..33满宽15 / 其余10 x0.8", [(hot_len, PCB_W), (rest_len, SEG_W_OTHER)],
         SKELETON_T_ALT, AL_DENSITY),
        ("D 台阶形 x0.8 铜", [(hot_len, PCB_W), (rest_len, SEG_W_OTHER)],
         SKELETON_T_ALT, CU_DENSITY),
    ]
    for name, rects, th, dens in cands:
        vol = sum(w * l * th for (l, w) in rects) / 1000.0
        g_side = vol * dens
        hot_v = PCB_W if any(w == PCB_W for (_, w) in rects) else 0.0
        r["candidates"].append({
            "name": name, "thickness_mm": th, "density_g_cc": dens,
            "volume_cc": r6(vol), "mass_per_side_g": r6(g_side), "mass_per_pair_g": r6(g_side * 2),
            "hot_segment_V_mm": hot_v,
            "v_cover_ok": hot_v >= v_need_15 - 1e-9,
            "vs_skeleton_budget_g": r6(g_side * 2 - BUDGET_SKELETON_G),
        })
    by = {c["name"][0]: c for c in r["candidates"]}
    add("cand_A_full_width_dead", by["A"]["mass_per_pair_g"] > BUDGET_SKELETON_G,
        f"满宽 60x15x1.0 = {by['A']['mass_per_pair_g']:.2f}g/对, 超骨架预算 {by['A']['vs_skeleton_budget_g']:+.2f}g "
        f"-> 判死 (与 hw-lead 一致)", by["A"]["mass_per_pair_g"])
    add("cand_B_step_1mm_reproduces_hwlead",
        abs(by["B"]["mass_per_pair_g"] - 3.62) < 0.05,
        f"台阶形 t=1.0 = {by['B']['mass_per_pair_g']:.2f}g/对 (hw-lead 报 3.62g) -> **独立复算一致**, "
        f"但超骨架预算 {by['B']['vs_skeleton_budget_g']:+.2f}g", by["B"]["mass_per_pair_g"])
    add("cand_C_step_0_8mm_in_budget", by["C"]["vs_skeleton_budget_g"] <= 0,
        f"台阶形 t=0.8 = {by['C']['mass_per_pair_g']:.2f}g/对, 余骨架预算 {by['C']['vs_skeleton_budget_g']:+.2f}g "
        f"-> **骨架本身**落进 '+1-3g'", by["C"]["mass_per_pair_g"])
    add("cand_D_copper_heavy", by["D"]["vs_skeleton_budget_g"] > 0,
        f"铜台阶形 t=0.8 = {by['D']['mass_per_pair_g']:.2f}g/对, 超预算 {by['D']['vs_skeleton_budget_g']:+.2f}g "
        f"(比铝重 {by['D']['mass_per_pair_g'] - by['C']['mass_per_pair_g']:+.2f}g/对) -> 导热好但重量代价大, "
        f"1 台样机阶段不建议", by["D"]["mass_per_pair_g"])

    # ---------- ④ 石墨: 重量归 W11 (不是骨架预算) + H 链位置 ----------
    g_vol = PCB_L * PCB_W * GRAPHITE_T / 1000.0
    g_side = g_vol * GR_DENSITY
    r["graphite"] = {
        "volume_cc": r6(g_vol), "mass_per_side_g": r6(g_side), "mass_per_pair_g": r6(g_side * 2),
        "placement": "PCB 内侧 = 骨架与 PCB 之间 (与板同长同宽 X∈[0,60]×Y∈[0,15])",
        "budget_line": "MECH_BUDGET §3 W11 (石墨散热膜+导热垫+隔热垫 1-2g) —— **不是** §2.4 B 的骨架预算",
        "note": "hw-lead ISS-049 报 0.54g/片; 本脚本按 2.00 g/cc 复算得 "
                f"{g_side:.2f}g/片 -> 一致",
    }
    add("graphite_in_W11", W11_GRAPHITE_G[0] <= g_side * 2 <= W11_GRAPHITE_G[1],
        f"石墨 {g_side:.2f}g/片 = {g_side * 2:.2f}g/对, 落在 W11 的 {W11_GRAPHITE_G[0]}-{W11_GRAPHITE_G[1]}g 区间内 "
        f"-> **不占** §2.4 B 骨架预算 (我第一版脚本在这里算错了, 已更正)", g_side * 2)

    h_base = H_OUTER_WALL + SKELETON_T + PCB_T + H_AIR_GAP + H_INSUL_PAD + H_SKIN_WALL
    h_gr = h_base + GRAPHITE_T
    h_base_t08 = H_OUTER_WALL + SKELETON_T_ALT + PCB_T + H_AIR_GAP + H_INSUL_PAD + H_SKIN_WALL
    h_gr_t08 = h_base_t08 + GRAPHITE_T
    r["H_chain"] = {
        "base_t1.0_mm": r6(h_base), "plus_graphite_t1.0_mm": r6(h_gr),
        "base_t0.8_mm": r6(h_base_t08), "plus_graphite_t0.8_mm": r6(h_gr_t08),
        "temple_H_max_mm": TEMPLE_H, "clearance_rule_mm": 0.60,
        "margin_t1.0_plus_gr_mm": r6(TEMPLE_H - h_gr),
        "margin_t0.8_plus_gr_mm": r6(TEMPLE_H - h_gr_t08),
        "note": "PCB 段 H 链 (来源 MECH/BOARD_WIDTH_15MM.md §2.4): 外壁0.8+骨架+PCB0.8+空隙0.3+隔热垫0.5+皮肤壁0.8; "
                "石墨 0.30 铺在骨架与 PCB 之间 -> 链 +0.30",
    }
    add("H_chain_margin_t1.0", (TEMPLE_H - h_gr) >= 0.60,
        f"骨架 1.0 + 石墨 0.30: PCB 段 H 链 = {h_gr:.2f}mm vs 可用 {TEMPLE_H:.2f} -> 余 {TEMPLE_H - h_gr:.2f}mm "
        f"(≥0.60 规矩 ✅)", TEMPLE_H - h_gr)
    add("H_chain_margin_t0.8", (TEMPLE_H - h_gr_t08) >= 0.60,
        f"骨架 0.8 + 石墨 0.30: PCB 段 H 链 = {h_gr_t08:.2f}mm vs 可用 {TEMPLE_H:.2f} -> 余 "
        f"{TEMPLE_H - h_gr_t08:.2f}mm ✅", TEMPLE_H - h_gr_t08)

    # ---------- ⑤ 并联热路: 骨架延伸进电池段的后果 ----------
    frac_base = skin_fraction(R_SKIN_PATH)
    r["parallel_heat_path"] = {
        "R_skin_path_K_W": R_SKIN_PATH, "R_conv_K_W": R_CONV,
        "skin_fraction_baseline_pct": r6(frac_base),
        "R_print_long_K_W": R_PRINT_LONG, "R_al_long_K_W": R_AL_LONG,
        "note": "骨架若延伸进电池段, 电池段热量的纵向热路由 730 (打印件) 降到 4.50 (铝) K/W "
                "-> 更多热绕到皮肤 [MECH/CLEARANCE_FIX §4.2]. 本脚本只复算**比例**, 不复算皮肤温度.",
    }
    add("skeleton_stops_at_pcb_rear_edge", True,
        f"硬约束: 金属骨架/石墨止于 PCB 段后缘 (板坐标 X={PCB_L:.2f}). 若延伸进电池段: 纵向热阻 "
        f"{R_PRINT_LONG:.0f} -> {R_AL_LONG:.2f} K/W, 皮肤侧热路被旁路 -> 进皮肤热量比例上升 "
        f"(CLEARANCE_FIX §4.2 报 92.5% -> 95.7%). 理由是物理的 (金属绕过隔热层直接灌到皮肤), 不是模型的.")

    # ---------- ⑥ 整机重量影响 ----------
    for tag in ("B", "C"):
        delta = by[tag]["mass_per_pair_g"]
        r.setdefault("total_weight_impact", {})[f"cand_{tag}"] = {
            "skeleton_pair_g": delta,
            "proto_total_range_g": list(TOTAL_PROTO_G),
            "proto_total_with_pair_g": [r6(TOTAL_PROTO_G[0] + delta), r6(TOTAL_PROTO_G[1] + delta)],
            "target_g": [30, 40],
            "still_over_target": (TOTAL_PROTO_G[0] + delta) > 40,
            "note": "整机推算区间加骨架增量; 目标 30-40g. 候选 C 的骨架增量 "
                    f"{delta:.2f}g/对 是**两种候选里较小**的",
        }
    add("weight_still_over_target", True,
        f"整机推算 {TOTAL_PROTO_G[0]}-{TOTAL_PROTO_G[1]}g 已超 30-40g 目标 (MECH_BUDGET §3.1); "
        f"骨架增量候选 B {by['B']['mass_per_pair_g']:.2f}g / 候选 C {by['C']['mass_per_pair_g']:.2f}g "
        f"-> 两候选都救不了整机超重, 只能少加重 (薄壁化/金属件替打印加强件)")
    return r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    r = compute()
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
        return 0

    print("=" * 80)
    print("金属骨架截面形状 + 重量口径 + 石墨 H 链 —— 结构侧独立复算 (ISS-049 两问的答复)")
    print("=" * 80)
    print("\n★ 口径: 只做**算术复算 + 几何判定**; **不出新的皮肤侧温度数** (要完整热模型重算, U-3); **不拍板**。")

    print("\n【1】V 向覆盖需求 (决定截面形状的硬约束)")
    print("-" * 80)
    print("  15mm 板: SoC 沿板宽 8.00 + 两侧横向扩散带各 3.50 = 15.00mm = 板宽 -> SoC 段骨架必须满宽")
    print("  12mm 板: 8.00 + 各 2.00 = 12.00mm = 板宽 -> 无横向扩散余量 (15mm 的真正结构收益)")

    print("\n【2】候选截面 (台阶形满宽段 X19..33)")
    print("-" * 80)
    print(f"{'方案':<40}{'V覆盖':<9}{'体积cc':<10}{'g/侧':<9}{'g/对':<9}{'vs骨架预算3g'}")
    for c in r["candidates"]:
        v = "✅ 满宽" if c["v_cover_ok"] else "❌"
        print(f"{c['name']:<40}{v:<9}{c['volume_cc']:<10.3f}{c['mass_per_side_g']:<9.2f}"
              f"{c['mass_per_pair_g']:<9.2f}{c['vs_skeleton_budget_g']:+.2f}")
    print("  ★ 候选 B 与 hw-lead ISS-049 报的 3.62g/对 独立复算一致 -> 复算链可信")

    print("\n【3】石墨片 (0.30mm, 铺在骨架与 PCB 之间)")
    print("-" * 80)
    g = r["graphite"]
    print(f"  体积 {g['volume_cc']:.3f}cc · {g['mass_per_side_g']:.2f}g/片 · {g['mass_per_pair_g']:.2f}g/对")
    print(f"  重量归账: {g['budget_line']}")
    print(f"  ⚠️ {g['note']}")

    print("\n【4】PCB 段 H 链 (含石墨)")
    print("-" * 80)
    h = r["H_chain"]
    print(f"  骨架 1.0: {h['base_t1.0_mm']:.2f} -> +石墨 {h['plus_graphite_t1.0_mm']:.2f}mm  "
          f"余 {h['margin_t1.0_plus_gr_mm']:.2f}mm")
    print(f"  骨架 0.8: {h['base_t0.8_mm']:.2f} -> +石墨 {h['plus_graphite_t0.8_mm']:.2f}mm  "
          f"余 {h['margin_t0.8_plus_gr_mm']:.2f}mm   (可用 {h['temple_H_max_mm']}, 规矩 ≥{h['clearance_rule_mm']})")

    print("\n【5】整机重量影响")
    print("-" * 80)
    for k, v in r["total_weight_impact"].items():
        print(f"  {k}: 骨架 {v['skeleton_pair_g']:.2f}g/对 -> 整机推算 "
              f"{v['proto_total_range_g'][0]}-{v['proto_total_range_g'][1]}g 变成 "
              f"{v['proto_total_with_pair_g'][0]:.1f}-{v['proto_total_with_pair_g'][1]:.1f}g "
              f"(目标 30-40g, 仍超)")

    print("\n【判定】")
    print("-" * 80)
    for c in r["checks"]:
        print(f"  {'✅' if c['pass'] else '❌'} {c['name']}: {c['detail']}")

    print("\n★ 结论 (建议, 不拍板 —— 最终由项目总工裁):")
    print("  ① 截面形状 = **台阶形** (SoC 段 X19..33 满宽 15.00 / 其余段 10.00) —— 唯一满足横向扩散带")
    print("     覆盖 (V 需 15.00 = 满宽) 又不像满宽那样被判死的方案")
    print("  ② 厚度 = **0.80mm** (不是 1.00) —— 骨架 2.89g/对, 落进 §2.4 B 的 '+1-3g';")
    print("     1.00mm 时骨架 3.62g/对, 超 0.62g (hw-lead 报的同一数)")
    print("  ③ 石墨 0.30 **铺在 PCB 内侧 (骨架与 PCB 之间)**, 与板同长同宽 -> PCB 段 H 链 +0.30,")
    print("     余量仍 ≥0.60 (骨架 0.8 时余 2.80mm)。石墨重量归 W11, **不占**骨架预算")
    print("  ④ 骨架/石墨**止于 PCB 段后缘** (X=60.00) —— 延伸进电池段 = 金属绕过隔热层直灌皮肤")
    print("  ⑤ ⚠️ 换 0.80mm 的**热学代价必须并进 U-3 一起算**: 铝的导热面积/截面都小 → Tj 会升,")
    print("     而 §2.3.1 的 46.5°C (0.23W) 已经超 43°C 红线 —— **只看重量不看热学会翻车**")
    print("  ⑥ 整机超重 (48.9-74.0g vs 目标 30-40g) **两个候选都救不了**, 只能靠减重措施, 不靠骨架选型")
    return 0


if __name__ == "__main__":
    sys.exit(main())
