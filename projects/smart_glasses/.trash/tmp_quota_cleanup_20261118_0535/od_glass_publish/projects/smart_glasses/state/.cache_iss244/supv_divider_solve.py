#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-244 · G-10 (R_SUPV_DIV1/2 最终阻值) — 按 TI 官方公式反推候选分压阻值
==============================================================
作者: sw-lead (软件总工) · 2026-11-16

★依据 (官方, 可复核):
  TI TPS3808 数据手册 SBVS050N (Rev. N, 2026-08) §7.3.1 "SENSE Input" +
  Figure 7-1 "Using the TPS3808G01 to Monitor a User-Defined Threshold Voltage":
      V_IT = (1 + R1/R2) × 0.405 V      ← R1 = 上臂 (被监控轨 → SENSE), R2 = 下臂 (SENSE → GND)
      R1 + R2 = 4 MΩ                    ← 手册功能框图注
      TPS3808G01 = Adjustable 版, V_IT 标称 0.405 V
      阈值精度: VIT ≤ 3.3 V 时 −1.5% ±0.5% (typ); 迟滞 1.5%
  落盘: state/.cache_iss244/ref/tps3808.pdf (36 页, TI 官网原件)

★本脚本只做算术, 不落表, 不替老板拍板:
  ⇒ 输出的是「窗口假设下的候选阻值 + 误差带」, 不是最终值。

用法: python3 supv_divider_solve.py
"""
import json

V_REF = 0.405          # TPS3808G01 内部基准 (V)
R_SUM = 4_000_000.0    # 手册功能框图: R1 + R2 = 4 MΩ
TOL_R = 0.01           # 电阻 1% (项目通用 ±1%)
ACC_TYP = 0.015        # 手册: VIT ≤ 3.3 V 时 typ ±1.5%
ACC_MAX = 0.005 + 0.015  # 手册: VIT ≤ 3.3 V 时 −1.5% ±0.5% ⇒ 偏差最大 2.0%
HYST = 0.015           # 迟滞 1.5% (VIT)

# 被监控轨 V_SOC_IO 的三档候选 (网表 L84 原文: "[待原厂] (3.3V / 1.8V / 1.2V)")
RAIL_CANDIDATES = [3.3, 1.8, 1.2]
# 触发点取「标称值的 90%」(= 轨电压跌到 −10% 时报欠压)
TRIP_RATIO = 0.90


def solve(v_it):
    """给定触发电压, 返回上/下臂阻值"""
    ratio = v_it / V_REF - 1.0        # = R1/R2
    r1 = R_SUM * ratio / (1.0 + ratio)
    r2 = R_SUM - r1
    return r1, r2


def e96(value):
    """取最接近的 E96 1% 标称值"""
    series = [1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
              1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
              1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
              2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
              3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
              4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
              5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
              7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76]
    decades = [1, 10, 100, 1000, 10000, 100000, 1000000]
    best = None
    for d in decades:
        for s in series:
            cand = s * d
            err = abs(cand - value) / value
            if best is None or err < best[0]:
                best = (err, cand)
    return best[1], best[0]


def main():
    out = []
    print("=== ISS-244 G-10 · TPS3808G01 分压候选 (公式: V_IT = (1 + R1/R2) x 0.405V, R1+R2 = 4MΩ) ===")
    print("窗口假设: 触发点 = 轨标称 x %.0f%% (轨电压跌 -10%% 报欠压); 电阻 1%%; 阈值精度 typ ±%.1f%% / max ±%.1f%%; 迟滞 %.1f%%"
          % (TRIP_RATIO * 100, ACC_TYP * 100, (ACC_TYP + ACC_MAX) * 100, HYST * 100))
    print()
    hdr = "%-6s %-8s %-11s %-11s %-9s %-9s %-9s %-9s" % (
        "轨标称", "V_IT", "R1(上)", "R2(下)", "E96 R1", "E96 R2", "E96后V_IT", "误差带")
    print(hdr)
    print("-" * len(hdr))
    for rail in RAIL_CANDIDATES:
        v_it = rail * TRIP_RATIO
        r1, r2 = solve(v_it)
        e1, _ = e96(r1)
        e2, _ = e96(r2)
        v_it_actual = V_REF * (1.0 + e1 / e2)
        # 误差带: 电阻 ±1% 带来的比例误差 + 基准精度
        lo = v_it_actual * (1 - TOL_R * 2) * (1 - (ACC_TYP + ACC_MAX))
        hi = v_it_actual * (1 + TOL_R * 2) * (1 + (ACC_TYP + ACC_MAX))
        print("%-6.1f %-8.3f %-11s %-11s %-9s %-9s %-9.4f %.4f~%.4f V" % (
            rail, v_it, "%.0f" % r1, "%.0f" % r2,
            fmt_e(e1), fmt_e(e2), v_it_actual, lo, hi))
        out.append({
            "rail_nominal_v": rail,
            "trip_target_v": round(v_it, 4),
            "r1_upper_ohm": round(r1),
            "r2_lower_ohm": round(r2),
            "r1_e96_1pct": fmt_e(e1),
            "r2_e96_1pct": fmt_e(e2),
            "v_it_actual_e96_v": round(v_it_actual, 4),
            "error_band_v": [round(lo, 4), round(hi, 4)],
            "hysteresis_v": round(v_it_actual * HYST, 4),
        })
    print()
    print("★ 结论口径 (只出依据, 不代拍):")
    print("  ① 公式与元件约束全部来自 TI 官方手册 (§7.3.1 + Figure 7-1), 可复核;")
    print("  ② 三个候选值对应网表 L84 原文的三个候选轨电压 (3.3 / 1.8 / 1.2 V);")
    print("  ③ ★真正的阻塞不是阻值算不出, 而是【被监控轨的窗口与产生它的 U_DCDC_VIO 都是 DNP】")
    print("     (网表 L84/L86 U_DCDC_VIO dnp=DNP; L407-L409 U_SUPV dnp=DNP) ⇒")
    print("     监控器本体不装 ⇒ 分压两臂装上只会把 RAIL_V_SOC_IO 短路到地 (ISS-190 已判);")
    print("  ④ ⇒ 建议: R_SUPV_DIV1/R_SUPV_DIV2 随 U_SUPV 一并置 DNP;")
    print("     若决定恢复监督器 ⇒ 按上表取 E96 值 + 触发点随轨标称重算, 且需补 1nF SENSE 滤波电容.");
    print()
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def fmt_e(v):
    if v >= 1_000_000:
        return "%.3fM" % (v / 1_000_000)
    if v >= 1000:
        return "%.0fk" % (v / 1000)
    return "%g" % v


if __name__ == "__main__":
    raise SystemExit(main())
