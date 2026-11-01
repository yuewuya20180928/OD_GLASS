#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-122 判据: BGA 逃线层数 —— **两套模型对撞, 看 4-6 层到底破没破**
=====================================================================
题目: ISS-118 判定 "RK3576 需 9 层 (破 4-6 层锁死)"。这个 9 层是怎么来的?
      ★**hq-lead 的模型只用了纯层数公式, 完全没算"边带一次能排多少排过孔"** ⇒
      两套模型结论相反 (9 层 vs 6 层可能) ⇒ **必须当面对撞, 不能只听一套**。

【模型 A (ISS-118 原模型, hw-lead 写的)】
  rows_deep = (max(arr_x, arr_y)+1)//2        # 中心到边的球圈数
  sig_layers = ceil(rows_deep / 2)             # "每增加 1 个布线层, 多逃 2 圈球" [推算/媒体]
  total = sig_layers + 2                       # + 2 参考面
  ⇒ RK3576: rows_deep=14 ⇒ sig=7 ⇒ total=**9 层**
  ★**缺陷**: 这个公式假设"每层只逃 2 圈", **完全没看边带 (SoC 到板边那段) 能排多少排**。

【模型 B (本脚本, 边带优先 + 每排过孔接 2 球圈)】
  物理事实:
    ① 一排逃线过孔 (via) 落在一个 x 位置上, 该 x 上的**上下两个球圈**都可以接到 ⇒ **1 排 = 2 球圈**
    ② 边带半宽 = (板宽 - 封装宽)/2 ⇒ 能排多少排 = max_rows_in_band()
    ③ 逃线总需求 = 中心到最远球的球圈数 (长边决定)
  ⇒ 边带一次能逃 = 边带排数 × 2 球圈
  ⇒ 若 边带排数×2 ≥ 逃线需求 ⇒ **单层 (L1) 就够** ⇒ 6 层板绰绰有余

【还有第三个数: "每排过孔能接几圈"是不是真的是 2?】
  ★这是**两种模型的分歧根源**, 也是**必须交给 PCB 厂 DFM 报告定案**的那一点:
    - 模型 A 隐含: 1 排 = 1 球圈 (因为"每 2 圈要 1 层" ⇒ 每层只加 2 圈 = 2 排)
    - 模型 B 用: 1 排 = 2 球圈 (via 上下各接一个球)
  ⇒ 实际是 **1 排过孔到底能接 2 个球圈还是 1 个**? 这取决于 **via 尺寸 vs 球间距** 与
    **是否允许同一 x 上的球用同一个 via 引出** (业界标准 BGA 逃线: 一排 via 可接 2 行球)

退出码: 0 = 判据跑完 (含 WARN) / 1 = 有硬 FAIL
输出: HW/esc_layer_models_check.json

纪律: 只写 HW/ 下本脚本自己的两个文件; 不碰 state/ MECH/ SW/ 别人的分片。
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "esc_layer_models_check.json")

# ---- 几何参数 (全部来自 ISS-118 的 HW/pcb60x30_check.py, 口径一致) ----
ESCAPE = {
    0.65: dict(ball_pad=0.30, trace=0.30, via_pad=0.40, via_drill=0.20),
    0.60: dict(ball_pad=0.30, trace=0.30, via_pad=0.40, via_drill=0.20),
}
ROW_CLEAR = 0.05
PCB_W_NEW = 30.00
PCB_THK_1L = 0.1          # 单层芯板厚 (mm)
CU_THK = 0.035            # 单层铜厚 (mm)

SOCS = {
    "RK3576": dict(name="RK3576", pkg_w=17.20, pkg_h=16.10, pitch=0.60,
                   n_balls=698, arr_x=28, arr_y=26),
    "RK3588": dict(name="RK3588", pkg_w=23.00, pkg_h=23.00, pitch=0.65,
                   n_balls=1088, arr_x=32, arr_y=34),
}

results = []
warns = 0
fails = 0


def chk(name, ok, detail, note="", level="INFO"):
    global warns, fails
    results.append({"check": name, "status": ("PASS" if ok else ("WARN" if level == "WARN" else "FAIL")),
                    "detail": detail, "note": note})
    if not ok:
        if level == "WARN":
            warns += 1
        else:
            fails += 1
    icon = "✅" if ok else ("⚠️" if level == "WARN" else "❌")
    print(f"  {icon} {name}: {detail}" + (f" ⇒ {note}" if note else ""))


def band(p, rows):
    """逃线带/边 (抄 ISS-118 的 band())"""
    e = ESCAPE[p]
    row_pitch = e["via_pad"] + ROW_CLEAR
    return (p / 2 + 0.05 + e["trace"] + (rows - 1) * row_pitch + e["via_pad"] / 2)


def max_rows_in_band(p, half_space):
    n = 0
    while band(p, n + 1) <= half_space:
        n += 1
    return n


def main() -> int:
    print("=" * 100)
    print("ISS-122 判据 | BGA 逃线层数: 模型 A (ISS-118 原模型) vs 模型 B (边带优先) 对撞")
    print("=" * 100)

    out = {}

    for key, soc in SOCS.items():
        p = soc["pitch"]
        arr = max(soc["arr_x"], soc["arr_y"])
        rows_deep = (arr + 1) // 2
        half_space = (PCB_W_NEW - soc["pkg_w"]) / 2
        n_edge = max_rows_in_band(p, half_space)

        print(f"\n【{soc['name']}】封装 {soc['pkg_w']}×{soc['pkg_h']}mm · pitch {p} · "
              f"阵列 {soc['arr_x']}×{soc['arr_y']} ({soc['n_balls']} 球)")

        # ---------- 模型 A (ISS-118 原模型) ----------
        sig_a = -(-rows_deep // 2)
        total_a = sig_a + 2
        print(f"\n  ── 模型 A (ISS-118 原模型: 纯层数公式, 不算边带) ──")
        print(f"     逃线深度 rows_deep = {rows_deep} 圈 ⇒ 布线层 ceil({rows_deep}/2) = {sig_a} ⇒ "
              f"总 {total_a} 层 {'❌ 破 4-6 层锁死' if total_a > 6 else '✅ 不破'}")
        chk(f"{soc['name']} 模型A 层数", total_a > 6,
            f"{total_a} 层 (布线 {sig_a} + 参考面 2)",
            f"破 4-6 层锁死; ★但这个模型**没算边带**", level="WARN")

        # ---------- 模型 B (边带优先) ----------
        # 边带排数 × 每排球圈数(2) = 边带一次能逃多少球圈
        edge_capacity_rows = n_edge * 2          # 1 排过孔 = 上下 2 个球圈
        need_rows = rows_deep
        # 若边带排数足够, 需要的过孔排数 = ceil(逃线需求球圈 / 2)
        via_rows_needed = math.ceil(rows_deep / 2)   # 逃 rows_deep 圈 ⇒ 需要 rows_deep/2 排过孔
        edge_ok = n_edge >= via_rows_needed
        sig_b = 1 if edge_ok else math.ceil((via_rows_needed - n_edge) / 2) + 1
        total_b = sig_b + 2
        print(f"\n  ── 模型 B (边带优先: 1 排过孔接上下 2 个球圈) ──")
        print(f"     边带半宽 {half_space:.2f}mm ⇒ 能排 {n_edge} 排过孔 (占 {band(p, n_edge):.2f}mm/边)")
        print(f"     逃 {rows_deep} 圈 ⇒ 需要 {via_rows_needed} 排过孔")
        print(f"     ⇒ {'✅ 边带够排 (单层 L1 即可)' if edge_ok else '❌ 边带不够, 需内层接力'}")
        print(f"     ⇒ 布线层 {sig_b} + 参考面 2 = **{total_b} 层** "
              f"{'✅ 不破 4-6 层锁死' if total_b <= 6 else '❌ 仍破'}")
        chk(f"{soc['name']} 模型B 层数", total_b <= 6,
            f"{total_b} 层 (边带 {n_edge} 排 {'够' if edge_ok else '不够'})",
            f"★与模型 A 的 {total_a} 层**结论相反** ⇒ 必须 PCB 厂 DFM 报告定案",
            level="WARN" if total_b <= 6 else "FAIL")

        # ---------- 分歧根源 ----------
        via_geom_ok = p - ESCAPE[p]["via_pad"] >= 0.075
        print(f"\n  ── 分歧根源: 1 排过孔能不能接 2 个球圈? ──")
        print(f"     模型 A 隐含 1 排 = 1 球圈 (每层只加 2 圈 = 2 排)")
        print(f"     模型 B 用   1 排 = 2 球圈 (via 上下各接一个球)")
        print(f"     几何前提: 同排过孔净间隙 = pitch - via_pad = {p - ESCAPE[p]['via_pad']:.3f}mm "
              f"{'✅ ≥0.075' if via_geom_ok else '❌'} ⇒ 过孔本身排得下")
        chk(f"{soc['name']} 过孔几何前提", via_geom_ok,
            f"同排过孔净间隙 {p - ESCAPE[p]['via_pad']:.3f}mm (判据 ≥0.075)",
            "★这只证明'过孔排得下', **不证明'1 排能接 2 球圈'** ⇒ 那要 DFM 报告")

        # ---------- 板厚代价 ----------
        print(f"\n  ── 板厚代价 (若采用各模型层数) ──")
        for tag, tot in (("模型A", total_a), ("模型B", total_b)):
            thk = tot * PCB_THK_1L + tot * CU_THK
            print(f"     {tag} {tot} 层 ⇒ 板厚 ≈ {thk:.2f}mm (芯板 {tot}×{PCB_THK_1L} + 铜 {tot}×{CU_THK})")
        print(f"     ★对照: PCB 段镜脚 V 净高余量 (ISS-118 §1) —— 板厚占镜脚 7.3mm 厚度的一部分")

        out[key] = {
            "pkg": [soc["pkg_w"], soc["pkg_h"]], "pitch": p,
            "arr": [soc["arr_x"], soc["arr_y"]], "n_balls": soc["n_balls"],
            "rows_deep": rows_deep,
            "edge_half_space": round(half_space, 2),
            "edge_rows": n_edge,
            "via_rows_needed": via_rows_needed,
            "model_A": {"sig_layers": sig_a, "total_layers": total_a,
                        "thickness_est_mm": round(total_a * (PCB_THK_1L + CU_THK), 2)},
            "model_B": {"sig_layers": sig_b, "total_layers": total_b,
                        "thickness_est_mm": round(total_b * (PCB_THK_1L + CU_THK), 2),
                        "edge_sufficient": edge_ok},
            "via_clear_same_row": round(p - ESCAPE[p]["via_pad"], 3),
        }

    print("\n" + "=" * 100)
    print(f"【汇总】 判据 {len(results)-fails-warns} PASS · {warns} WARN · {fails} FAIL")
    print("  ★★ 结论: 两套模型对同一块板给出**相反的层数结论** ⇒")
    print("     模型 A (ISS-118 原模型) = 纯层数公式, **没算边带**")
    print("     模型 B (本脚本) = 边带优先, 1 排过孔接 2 球圈")
    print("     ⇒ **'4-6 层破没破'这个结论本身不确定** ⇒ 必须 PCB 厂 DFM 报告定案 (ISS-122 的核心)")
    print("     ⇒ ★**但方向是好消息**: 若模型 B 成立, 4-6 层不需要破锁 ⇒ 加层/HDI 这两条代价都省了")
    print("=" * 100)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"issue": "ISS-122", "socs": out, "checks": results,
                   "warn": warns, "fail": fails, "total": len(results)},
                  f, ensure_ascii=False, indent=2)
    print(f"JSON -> {OUT_JSON}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
