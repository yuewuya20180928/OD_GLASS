#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/hinge_power_calc.py —— ISS-091 第2轮: 跨铰链充电电流 1.0A 载流/压降/发热核算

用法:
    cd projects/smart_glasses && python3 MECH/hinge_power_calc.py
    cd projects/smart_glasses && python3 MECH/hinge_power_calc.py --json   # 机器可读

口径来源:
  - 铰链段柔性材料/接口定义: 项目总工 ISS-091 第2轮派活锚点 + DECISIONS 2026-10-27 (J_CHG 1x10p@0.5)
  - 热模型: MECH/MECH_BUDGET.md §2.2/§2.3 (k_eff 主模型 50.13 K/W, 剥离口径 39.25 K/W, 基准 35C)
  - R_ILIM 公式: HW/CHARGE_BOARD_SPEC.md §2.4 (IINMAX = KILIM/RILIM, KILIM=320/355/390 AΩ)
  - 铰链段几何: MECH/USB_HINGE_STRUCTURE.md §4.1/§4.2 (弯折弧长 4.71mm @R3.0; 固定段每端>=8mm)

证据等级: [实测] 我算的 / [官方] 厂商规格 / [推算] 由前两者推导 / [0数据] 查不到
"""
import json
import math
import sys

# ----------------------------------------------------------------------------
# 0. 常数与模型参数
# ----------------------------------------------------------------------------
RHO_CU = 1.72e-8          # Ω·m 退火铜 [官方] 标准值
K_EFF_MAIN = 50.13        # K/W 主模型 皮肤侧有效热阻 (MECH_BUDGET §2.3)
K_EFF_STRIP = 39.25       # K/W 剥离口径 (壳壁不算皮肤侧)
T_SKIN_BASE = 35.0        # °C 环境/体温基准 (MECH_BUDGET §2.3)
T_REDLINE = 43.0          # °C ISO 13732-1 烧伤阈值 (MECH_BUDGET §2.2)
T_TARGET = 40.0           # °C 设计目标上沿

KILIM_MIN, KILIM_TYP, KILIM_MAX = 320.0, 355.0, 390.0   # AΩ [官方] BQ25896
ICHG_FACTOR = 0.822        # Vbat/Vbus/η  (CHARGE_BOARD_SPEC §2.4 口径)
RILIM_VALUES = [300, 390, 470, 680]

# --- 铰链段 FPC 载流铜箔 ---
# 长度: 铰链段 7-9mm + 两端固定段 >=8mm -> >=23mm; ISS-085 §4.2 总长 >=31mm
FPC_LEN_CASES = {
    "短 (23mm, 铰链段7.9+固定段8×2)": 0.023,
    "标称 (31mm, ISS-085 §4.2)": 0.031,
    "长 (40mm, 框内/脚内段加长)": 0.040,
}
# 铜箔: 0.5mm pitch 标准导体 0.3mm (间隙0.2); 加宽 0.4mm 需厂商允许 (最小间隙0.1mm) [0数据]
TRACE_WIDTH_CASES = {
    "0.3mm (标准导体)": 0.30e-3,
    "0.4mm (加宽, 需厂商确认最小间隙0.1mm)": 0.40e-3,
}
# 铜厚: 1oz=35um / 2oz=70um
FOIL_THICK_CASES = {
    "1oz (35um)": 35e-6,
    "2oz (70um)": 70e-6,
}

# --- 接触电阻 (每 pin, 单侧界面) ---
# 任务锚点: 0.5mm pitch FPC 典型 5-30 mΩ —— 通用工程值, 未核厂商规格书 -> [0数据]+区间
R_CONTACT_PER_PIN_PER_INTERFACE = (5e-3, 30e-3)
N_CONTACT_INTERFACES = 2   # 框侧界面 + 脚侧界面

# --- 电芯 ---
R_CELL_INTERNAL = 0.10     # Ω 软包锂电内阻标称 [0数据] 丰江432243规格书未查到, 按0.08-0.15取
R_CELL_RANGE = (0.08, 0.15)
CELL_CAPACITY_MAH = 400

# --- 机械 ---
K_TEMP_FPC = 400.0         # W/m·K 铜 [官方] 标准值
E_PI = 2.5e9               # Pa 聚酰亚胺 E [推算] 通用值
FPC_T = 0.20e-3            # m 成品厚 (4层 0.5pitch)
FPC_W = 6.0e-3             # m FPC 宽度 (10p@0.5 -> 5.0mm触点区 + 两侧0.5走线边距)
BEND_R = 3.0e-3            # m 弯折半径

# 铰链区堆叠 (任务锚点 27.0mm / DECISIONS 26.5mm)
HINGE_STACK_MM = 27.0
TEMPLE_ROOT_NET_HEIGHT_MM = 37.0
HINGE_RADIAL_CLEARANCE_MM = 5.40   # 前后内净空 (USB_HINGE_STRUCTURE C-4)
HINGE_RADIAL_USED_MM = 4.40        # R3.0 + 4x(0.20+0.15)


def r_trace(length_m, width_m, thick_m):
    """单条 FPC 铜箔导体的直流电阻"""
    return RHO_CU * length_m / (width_m * thick_m)


def r_path(r_c_iface, r_trace_b_plus, r_trace_gnd, r_plane, use_plane_return):
    """
    铰链段总电阻 (电源回路: 框侧界面 -> B+ 铜箔 -> FPC -> GND 铜箔/平面 -> 脚侧界面)
    口径 A (保守): 回流只走 GND 双 pin 的铜箔
    口径 B (乐观): 回流主要走 FPC 内层地平面 (截面大得多)
    """
    b_plus = (N_CONTACT_INTERFACES * r_c_iface + r_trace_b_plus) / 2.0   # pin1+pin2 并联
    if use_plane_return:
        gnd = (N_CONTACT_INTERFACES * r_c_iface + (r_trace_gnd * r_plane) / (r_trace_gnd + r_plane)) / 2.0
    else:
        gnd = (N_CONTACT_INTERFACES * r_c_iface + r_trace_gnd) / 2.0
    return b_plus + gnd


def r_plane(length_m, width_m=4.5e-3, thick_m=35e-6):
    """FPC 内层地平面当回流导体时的直流电阻 (跨整个宽度)"""
    return RHO_CU * length_m / (width_m * thick_m)


def skin_rise(p_w, k_eff=K_EFF_MAIN):
    """皮肤侧温升 (°C) —— 用 MECH_BUDGET §2.3 口径, 不另起炉灶。p_w 单位 W"""
    return p_w * k_eff


def fmt(x, n=3):
    return f"{x:.{n}f}"


def main():
    out = {}

    # ------------------------------------------------------------------
    # 1. FPC 载流铜箔电阻表
    # ------------------------------------------------------------------
    print("=" * 100)
    print("[1] 铰链段 FPC 载流铜箔电阻 R_trace = rho*L/(w*t)   [推算, rho_Cu=1.72e-8 ohm*m]")
    print("=" * 100)
    print(f"{'长度':<34} {'线宽':<30} {'铜厚':<16} {'R/pin':>10}")
    trace_tab = {}
    for lname, L in FPC_LEN_CASES.items():
        for wname, w in TRACE_WIDTH_CASES.items():
            for tname, t in FOIL_THICK_CASES.items():
                r = r_trace(L, w, t)
                trace_tab[(lname, wname, tname)] = r
                print(f"{lname:<34} {wname:<30} {tname:<16} {fmt(r*1000,2)} mohm")
    out["trace_table_mohm"] = {f"{k[0]}|{k[1]}|{k[2]}": v * 1000 for k, v in trace_tab.items()}

    # ------------------------------------------------------------------
    # 2. 压降 (3 个工况)
    # ------------------------------------------------------------------
    # 基准工况: 标称长度 31mm, 线宽 0.3mm, 铜厚 1oz (最小改动), 平面回流 = 口径A保守
    BASE = dict(len_key="标称 (31mm, ISS-085 §4.2)", wid_key="0.3mm (标准导体)",
                thick_key="1oz (35um)")
    L = FPC_LEN_CASES[BASE["len_key"]]
    w = TRACE_WIDTH_CASES[BASE["wid_key"]]
    t = FOIL_THICK_CASES[BASE["thick_key"]]
    rt = r_trace(L, w, t)
    rp = r_plane(L)

    scenarios = []
    for cname, r_c in (("乐观 (5 mohm/界面)", 5e-3), ("标称 (17.5 mohm/界面)", 17.5e-3),
                        ("保守 (30 mohm/界面)", 30e-3)):
        for planame, use_plane in (("口径A 回流走GND双pin铜箔(保守)", False),
                                   ("口径B 回流走FPC地平面(乐观)", True)):
            for tagn, tt, tw in (("1oz 0.3mm (最小改动)", t, w),
                                 ("2oz 0.4mm (加宽加厚)", 70e-6, 0.40e-3)):
                r_tt = r_trace(L, tw, tt)
                r_p = r_plane(L) if tt == 35e-6 else r_plane(L, 4.5e-3, 70e-6)
                R = r_path(r_c, r_tt, r_tt, r_p, use_plane)
                for i in (0.5, 1.0):
                    dv = i * R
                    p = i * i * R
                    scenarios.append(dict(
                        contact=cname, plane=planame, build=tagn, I=i,
                        R_mohm=R * 1000, dV_mV=dv * 1000, P_mW=p * 1000,
                        dT_skin=skin_rise(p)))

    print()
    print("=" * 100)
    print("[2] 铰链段压降 / 发热  (R_path 含 框侧界面 + B+铜箔 + 回流 + 脚侧界面)")
    print("=" * 100)
    print(f"{'接触电阻口径':<24} {'回流模型':<30} {'FPC 工艺':<22} {'I(A)':>6} "
          f"{'R_path(mohm)':>14} {'dV(mV)':>9} {'P(mW)':>9} {'皮肤+degC':>11}")
    for s in scenarios:
        print(f"{s['contact']:<24} {s['plane']:<30} {s['build']:<22} {s['I']:>6.2f} "
              f"{s['R_mohm']:>14.1f} {s['dV_mV']:>9.1f} {s['P_mW']:>9.1f} {s['dT_skin']:>11.2f}")
    out["scenarios"] = scenarios

    # ------------------------------------------------------------------
    # 3. R_ILIM 档位表  ★老板要看的
    # ------------------------------------------------------------------
    print()
    print("=" * 100)
    print("[3] ★ R_ILIM 档位表   IINMAX = KILIM/R_ILIM  [官方: KILIM=320/355/390 AΩ]")
    print("    ICHG = IINMAX x 0.822 (Vbat/Vbus/eta)  [推算, CHARGE_BOARD_SPEC §2.4 口径]")
    print("=" * 100)
    rilim_tab = []
    for R_ILIM in RILIM_VALUES:
        iin = [KILIM_MIN / R_ILIM, KILIM_TYP / R_ILIM, KILIM_MAX / R_ILIM]
        ichg = [x * ICHG_FACTOR for x in iin]
        for idx, tag in enumerate(("min", "typ", "max")):
            I = ichg[idx]
            # 口径A保守 + 基准 FPC 工艺(1oz/0.3mm/31mm)
            R_cons = r_path(R_CONTACT_PER_PIN_PER_INTERFACE[1], rt, rt, rp, False)
            R_opt = r_path(R_CONTACT_PER_PIN_PER_INTERFACE[0], rt, rt, rp, True)
            dv_c, p_c = I * R_cons, I * I * R_cons
            dv_o, p_o = I * R_opt, I * I * R_opt
            p_cell = I * I * R_CELL_INTERNAL
            dt_hinge_c = skin_rise(p_c)
            # 电芯内阻发热: 电芯在镜脚、3M背胶贴皮肤侧 -> 保守取 100% 进皮肤路径;
            # 乐观取 50% (电芯偏上/外侧, 部分由镜腿外表面带走)
            dt_cell_cons = skin_rise(p_cell, K_EFF_MAIN) * 1.0
            dt_cell_opt = skin_rise(p_cell, K_EFF_MAIN) * 0.5
            dt_total = dt_hinge_c + dt_cell_cons          # 保守合计
            dt_total_opt = dt_hinge_c + dt_cell_opt       # 乐观合计
            row = dict(
                R_ILIM=R_ILIM, tag=tag,
                IINMAX_A=iin[idx], ICHG_A=I,
                per_pin_A=I / 2.0,
                dV_mV_cons=dv_c * 1000, dV_mV_opt=dv_o * 1000,
                P_mW_cons=p_c * 1000, P_mW_opt=p_o * 1000,
                P_cell_mW=p_cell * 1000,
                dT_hinge_c=dt_hinge_c, dT_cell_cons=dt_cell_cons, dT_cell_opt=dt_cell_opt,
                dT_total=dt_total, dT_total_opt=dt_total_opt,
                T_skin=T_SKIN_BASE + dt_total,
                T_skin_opt=T_SKIN_BASE + dt_total_opt,
                t_charge_min=CELL_CAPACITY_MAH / (I * 1000.0) * 60.0,
            )
            rilim_tab.append(row)
            print(f"R_ILIM={R_ILIM:>4}ohm {tag:>3} | IINMAX={iin[idx]:.3f}A | ICHG={I:.3f}A "
                  f"| 单pin={I/2:.3f}A | dV(A口径)={dv_c*1000:5.1f}mV (B口径 {dv_o*1000:4.1f}mV) "
                  f"| P铰链(A)={p_c*1000:5.1f}mW | P电芯={p_cell*1000:5.1f}mW "
                  f"| 皮肤+{dt_total:.2f}C -> {T_SKIN_BASE+dt_total:.1f}C "
                  f"(乐观 {T_SKIN_BASE+dt_total_opt:.1f}C) "
                  f"| 充电~{row['t_charge_min']:.0f}min")
    out["rilim_table"] = rilim_tab

    # 判定表
    print()
    print("-" * 100)
    print("判定 (以 ICHG=max 档 + 口径A保守 + 电芯内阻 0.10ohm 为准):")
    print("  验收判据: C1 单pin<=0.5A (连接器单触点额定, 待选型) | C2 压降<=100mV | "
          "C3 皮肤<43C红线 | C4 皮肤<40C设计目标 | C5 铰链段发热<=50mW")
    for R_ILIM in RILIM_VALUES:
        row = [r for r in rilim_tab if r["R_ILIM"] == R_ILIM and r["tag"] == "max"][0]
        c1 = "OK " if row["per_pin_A"] <= 0.5 else "FAIL"
        c2 = "OK " if row["dV_mV_cons"] <= 100 else "FAIL"
        c3 = "OK " if row["T_skin"] <= T_REDLINE else "FAIL"
        c4 = "OK " if row["T_skin"] <= T_TARGET else "FAIL"
        c5 = "OK " if row["P_mW_cons"] <= 50 else "FAIL"
        print(f"  R_ILIM={R_ILIM:>4}ohm: C1[{c1}] C2[{c2}] C3[{c3}] C4[{c4}] C5[{c5}]  "
              f"皮肤 {row['T_skin']:.1f}C (乐观 {row['T_skin_opt']:.1f}C)  "
              f"充电 {row['t_charge_min']:.0f}min")
    print("-" * 100)

    # ------------------------------------------------------------------
    # 3b. "加厚铜箔" 能不能代替 "降 R_ILIM 档"?
    # ------------------------------------------------------------------
    print()
    print("=" * 100)
    print("[3b] 能否用加宽/加厚铜箔代替降 R_ILIM 档?  (口径A保守, ICHG=max 档)")
    print("=" * 100)
    print(f"{'R_ILIM':>8} {'FPC 工艺':<24} {'ICHG(A)':>8} {'dV(mV)':>8} {'P铰链(mW)':>11} "
          f"{'皮肤(C)':>9} {'判定':>8}")
    cmp_rows = []
    for R_ILIM in RILIM_VALUES:
        I = [r for r in rilim_tab if r["R_ILIM"] == R_ILIM and r["tag"] == "max"][0]["ICHG_A"]
        for bname, tw, tt in (("1oz 0.3mm (基线)", w, t),
                              ("2oz 0.4mm (加宽加厚)", 0.40e-3, 70e-6)):
            r_tt = r_trace(L, tw, tt)
            r_p = r_plane(L, 4.5e-3, tt)
            R = r_path(R_CONTACT_PER_PIN_PER_INTERFACE[1], r_tt, r_tt, r_p, False)
            dv, p = I * R, I * I * R
            dt = skin_rise(p) + skin_rise(I * I * R_CELL_INTERNAL)
            T = T_SKIN_BASE + dt
            print(f"{R_ILIM:>7}ohm {bname:<24} {I:>8.3f} {dv*1000:>8.1f} {p*1000:>11.1f} "
                  f"{T:>9.1f} {'PASS' if T <= T_REDLINE else 'FAIL':>8}")
            cmp_rows.append(dict(R_ILIM=R_ILIM, build=bname, ICHG=I, dV_mV=dv*1000,
                                  P_mW=p*1000, T_skin=T, pass_43=T <= T_REDLINE))
    out["copper_vs_rilim"] = cmp_rows

    # ------------------------------------------------------------------
    # 4. 机械
    # ------------------------------------------------------------------
    print()
    print("=" * 100)
    print("[4] 机械")
    print("=" * 100)
    I_sec = FPC_W * FPC_T ** 3 / 12.0
    EI = E_PI * I_sec
    M_bend = EI / BEND_R
    F_lever = M_bend / 0.025
    print(f"  FPC 弯曲刚度 EI = {EI:.3e} N*m^2   弯折力矩 @R3.0 = {M_bend*1000:.3f} mN*m"
          f"   25mm 力臂等效力 = {F_lever:.3f} N")
    print(f"  -> 铰链开合时 FPC 对连接器的拉力 ~{F_lever:.3f} N (25mm 力臂), "
          f"vs ZIF 保持力 3-10 N -> 余量 {3.0/F_lever:.0f}-{10.0/F_lever:.0f}x  [推算]")
    # 铜箔弯折应变
    for tname, tt in FOIL_THICK_CASES.items():
        eps = tt / (2 * BEND_R)
        print(f"  弯折段铜箔应变 eps = t/(2R) @R3.0: {tname:<16} eps={eps*100:.3f}%  "
              f"(1oz->2oz 应变 x{ (70e-6)/(35e-6):.1f}, 疲劳寿命按 m=4~6 幂律 -> x{(1/2)**5:.3f}~{(1/2)**4:.3f})")
    # 电流密度
    for cw, cl, tag in ((0.30e-3, 1.20e-3, "触点 0.30x1.20mm"),):
        print(f"  触点电流密度 @{tag}: 单pin 0.5A -> {0.5/(cw*cl*1e6):.2f} A/mm^2 ; "
              f"单pin 0.53A -> {0.53/(cw*cl*1e6):.2f} A/mm^2")
    # 高度影响
    print(f"  铰链区垂直堆叠 {HINGE_STACK_MM}mm / 镜脚根部净高 {TEMPLE_ROOT_NET_HEIGHT_MM}mm "
          f"(余 {TEMPLE_ROOT_NET_HEIGHT_MM-HINGE_STACK_MM:.1f}mm)")
    print(f"  -> 加宽铜箔(外层L1/L4): 成品厚不变 -> 高度影响 0.00mm")
    print(f"  -> 固定段 1oz->2oz: 成品厚 +0.04~0.05mm/层 x 4 层 -> 径向 +0.16~0.20mm "
          f"(径向余量 {HINGE_RADIAL_CLEARANCE_MM-HINGE_RADIAL_USED_MM:.2f}mm -> "
          f"{HINGE_RADIAL_CLEARANCE_MM-HINGE_RADIAL_USED_MM-0.20:.2f}mm), 高度影响 0.00mm")
    out["mech"] = dict(EI=EI, M_bend_Nm=M_bend, F_lever_N=F_lever,
                       eps_1oz=35e-6/(2*BEND_R), eps_2oz=70e-6/(2*BEND_R),
                       radial_remaining_after_2oz=0.80)

    # ------------------------------------------------------------------
    # 5. 压降对 SYS / 电芯端电压的影响
    # ------------------------------------------------------------------
    print()
    print("=" * 100)
    print("[5] 压降对 SYS 轨 与 电芯端电压的影响  (基准: 口径A保守 1oz/0.3mm/31mm)")
    print("=" * 100)
    R_cons = r_path(R_CONTACT_PER_PIN_PER_INTERFACE[1], rt, rt, rp, False)
    R_opt = r_path(R_CONTACT_PER_PIN_PER_INTERFACE[0], rt, rt, rp, True)
    for R_ILIM in RILIM_VALUES:
        row = [r for r in rilim_tab if r["R_ILIM"] == R_ILIM and r["tag"] == "max"][0]
        I = row["ICHG_A"]
        print(f"  R_ILIM={R_ILIM}ohm ICHG={I:.3f}A: dV(A)={I*R_cons*1000:.1f}mV (B) {I*R_opt*1000:.1f}mV")
        print(f"      -> CV 段电芯稳定电压 = 4.200 - dV = {4.200 - I*R_cons:.3f}V (口径A) "
              f"/ {4.200 - I*R_opt:.3f}V (口径B)   [欠充方向, 不会过充]")
        print(f"      -> SYS 轨上限 = 同上 (SYS 在镜脚本地由电芯产生, 不跨铰链, 压降只压低上限)")
        print(f"      -> SYS 下限 3.5V (R-F1 UVP) 不受影响")
        # TS 偏移
        dV_ts = I * R_CONTACT_PER_PIN_PER_INTERFACE[1]
        ts_sens = 5.0 * (0.7325 - 0.34375) / 60.0   # V/degC (0->60C, 73.25%->34.375% of REGN)
        print(f"      -> TS 参考地偏移 {dV_ts*1000:.1f}mV (回流经铰链GND) = 等效 {dV_ts/ts_sens:.2f}degC 温度偏差")
    out["rail_impact"] = dict(R_cons_mohm=R_cons * 1000, R_opt_mohm=R_opt * 1000)

    if "--json" in sys.argv:
        with open("MECH/hinge_power_calc.json", "w") as f:
            json.dump(out, f, ensure_ascii=False, indent=2, default=str)
        print("\n[json] 已写 MECH/hinge_power_calc.json")

    print("\n[完成] rc=0")


if __name__ == "__main__":
    main()
