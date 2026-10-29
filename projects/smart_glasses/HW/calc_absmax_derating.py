#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HW/calc_absmax_derating.py
ISS-068 可靠性证据缺口收口 —— 关键数字唯一出处 (30 秒跑完, 无外部依赖)

复现三组数字:
  (1) 器件级降额占用率 —— 三类判据 (J1 额定直比 / J2 降额 / J3 规范值)
  (2) MTBF 重算: 原模型 (含光学 1,650 FIT) vs 剥离光学子系统后
  (3) R-F4 / R-F5 充电域结温与充电板环境温度可行边界

数据来源等级:
  [官方] = TI datasheet (版本见各行 note) / 厂商公开页
  [推算] = 本文算式 (输入均已在表内标出来源)

用法:  python3 HW/calc_absmax_derating.py
"""
import math

# =====================================================================
# 判据分类 (这是 ISS-068 对 "降额表升级" 的核心: 一刀切的 x0.8/x0.85 会误判)
# =====================================================================
# J1 额定直比  : 器件的"推荐工作上限"本身即硬约束, 降额无意义 (降了就不工作)
#                阈值: <90% OK / 90~100% WARN / >100% FAIL
# J2 降额判据  : 额定值有余量, 可按 x0.8 (V/I) / x0.85 (T) 收紧
#                阈值: <80% OK / 80~100% WARN / >100% FAIL
# J3 规范值判据: 电芯/行业规范值 (如锂电满充 4.2V), 不用通用降额档卡, 回到规格书
#                阈值: 见 note, 本轮该类多为 [0数据]
#
# (器件, 轴, 设计工作值, 官方推荐工作上限, 判据类, 系数, 阈值OK%, 证据/理由)
DERATE = [
    # --- TPS62130A (SLVSAG7F, RGT-16 VQFN 3x3) ---
    ("TPS62130A", "温度Tj", 59.5, 125.0, "J2", 0.85, 80,
     "[官方]REC TJ -40~125C (abs max 150C); Tj=55C+0.1W*45K/W(官方RθJA)=59.5C"),
    ("TPS62130A", "电压VIN", 4.2, 17.0, "J2", 0.80, 80,
     "[官方]REC VIN 3~17C (abs max 20V); SYS 3.0~4.2V"),
    ("TPS62130A", "电流Iout", 1.69, 3.0, "J2", 0.80, 80,
     "[官方]REC 3A; 峰值 1.69A=0.9W/0.8V*1.5"),
    # --- TPS7A20 (SBVS338H, DQN X2SON 4pin, 官方RθJA 166.1) ---
    ("TPS7A20", "温度Tj", 55.0, 125.0, "J2", 0.85, 80,
     "[官方]REC TJ -40~125C (abs max 150C); 5 轨中最大耗散 ~0.175W*166.1=29C"),
    ("TPS7A20", "电压VIN", 4.2, 6.0, "J2", 0.80, 80,
     "[官方]REC VIN 1.6~6.0V (abs max 6.5V); SYS 满电 4.2V"),
    ("TPS7A20", "电流Iout(单轨)", 0.200, 0.300, "J2", 0.80, 80,
     "[官方]REC 300mA/颗; 单颗只带一条轨, 最大轨 VDD_3V3_IO 200mA (ISS-067 后 3.3V 改 buck -> 最大轨 50mA)"),
    # --- BQ25896 (SLUSC76C, RTW WQFN 24pin 4x4) ---
    ("BQ25896", "温度Tj", 55.9, 85.0, "J2", 0.85, 80,
     "[官方]REC TA -40~85C (abs max Tj 150C); Tj=40C+0.5W*31.8K/W(官方RθJA)=55.9C"),
    ("BQ25896", "电压VBUS", 5.0, 14.0, "J2", 0.80, 80,
     "[官方]REC VIN 3.9~14V (abs max VBUS 22V); PD 5V"),
    ("BQ25896", "电压BAT/SYS", 4.2, 4.608, "J1", 1.00, 90,
     "[官方]REC VBAT<=4.608V (abs max BAT/SYS 6V); ★4.2V 是 1S 锂电满充规范值, 不适用 x0.8 降额 (否则任何锂电都超标)"),
    ("BQ25896", "电流Ichg", 1.0, 3.0, "J2", 0.80, 80,
     "[官方]REC 3A (6A continuous); 设计 1.0A"),
    # --- TPS25730 (SLVSGP9, D=WQFN REF 38pin 4.0x6.0 / S=VQFN RSM 32pin 4.0x4.0) ---
    ("TPS25730", "温度Tj", 42.3, 65.0, "J2", 0.85, 80,
     "[官方]REC TA -40~65C @IPP_HV<=6A (官网写 -40~125C 是 TJ 口径); Tj=40+0.04W*57.4=42.3C"),
    ("TPS25730", "电压VBUS", 5.0, 22.0, "J2", 0.80, 80,
     "[官方]REC VBUS 4~22V (abs max 28V)"),
    ("TPS25730", "电流IPP_HV", 2.0, 6.0, "J2", 0.80, 80,
     "[官方]REC IPP_HV<=6A @TA<=65C (abs max 7A cont / 10A pulse <=100us)"),
    # --- BQ2970 (SBVS349, DSE WSON 6pin) ---
    ("BQ2970", "温度TA", 55.0, 85.0, "J2", 0.85, 80,
     "[官方]REC TAmb -40~85C (abs max TFUNC -40~85C); 镜脚内组件环境 <=55C"),
    ("BQ2970", "电压BAT", 4.2, 8.0, "J2", 0.80, 80,
     "[官方]REC BAT<=8V (abs max BAT 12V)"),
    # --- TMP117 (SNOSD82D, YBG DSBGA 6pin, 官方RθJA 133.2) ---
    ("TMP117", "温度TA", 60.0, 150.0, "J2", 0.85, 80,
     "[官方]REC TA -55~150C (abs max TJ 155C)"),
    ("TMP117", "电压V+", 3.3, 5.5, "J2", 0.80, 80,
     "[官方]REC V+ 1.8~5.5C @TA -55~150C / 1.7~5.5C @TA<=70C (abs max 6V)"),
]


def derating_table():
    print("=" * 122)
    print("(1) 器件级降额占用率 —— 三类判据: J1 额定直比 / J2 降额 / J3 规范值")
    print("=" * 122)
    print(f"{'器件':<11}{'轴':<15}{'判据':<5}{'工作值':>9}{'官方上限':>10}{'建议上限':>10}{'占用率':>9}  判定")
    worst = []
    for dev, axis, work, rated, jc, k, thr, note in DERATE:
        limit = rated * k
        util = work / limit * 100.0
        flag = "OK  " if util < thr else ("WARN" if util < 100 else "FAIL")
        print(f"{dev:<11}{axis:<15}{jc:<5}{work:>9.3f}{rated:>10.3f}{limit:>10.3f}{util:>8.1f}%  {flag}")
        if util >= thr:
            worst.append((dev, axis, jc, util, note))
    print()
    print(f"  ⚠️/❌ 项 (占用率 >= 判据阈值): {len(worst)} 条")
    for dev, axis, jc, util, note in worst:
        print(f"    - {dev} / {axis} [{jc}]: {util:.1f}%  {note}")
    print()
    print("  J1/J2 判定阈值: J1 额定直比 <90% OK / 90~100% WARN / >100% FAIL; "
          "J2 降额 <80% OK / 80~100% WARN / >100% FAIL")
    return worst


# =====================================================================
# (2) MTBF 重算: 原模型 vs 剥离光学子系统
# =====================================================================
K_B, E_A, T_REF = 8.617333262e-5, 0.7, 313.15


def af(c):
    return math.exp((E_A / K_B) * (1.0 / T_REF - 1.0 / (c + 273.15)))


COMP = [
    ("SoC", 1, 120, 0.90, 1), ("DC-DC", 1, 35, 0.90, 1), ("LDO", 5, 20, 0.90, 1),
    ("充电IC", 1, 30, 0.90, 1), ("PD", 1, 25, 0.85, 1), ("保护IC", 1, 20, 0.90, 1),
    ("NMOS", 2, 10, 0.85, 1), ("TMP117", 1, 12, 0.70, 1), ("OV04C10", 1, 45, 0.80, 1),
    ("光机", 1, 800, 0.50, 1), ("波导", 2, 300, 0.50, 1), ("分光件", 1, 250, 0.50, 1),
    ("电池", 1, 350, 0.60, 1), ("BTB", 3, 25, 0.70, 1), ("TypeC", 1, 60, 0.60, 1),
    ("Sensor座", 1, 30, 0.70, 1), ("电池座", 2, 25, 0.70, 1), ("FPC", 3, 60, 0.80, 1),
    ("电感", 4, 12, 0.80, 1), ("磁珠", 6, 8, 0.80, 1), ("钽电解", 4, 25, 0.90, 1),
    ("MLCC", 110, 4, 0.90, 1), ("电阻", 95, 4, 0.90, 1), ("ESD", 4, 6, 0.30, 1),
    ("晶振", 2, 15, 0.50, 1), ("LED", 4, 8, 0.70, 1), ("PCB", 1, 150, 0.90, 1),
    ("按键", 3, 30, 0.70, 1), ("骨架", 1, 80, 0.30, 1),
]
OPTICAL = {"光机", "波导", "分光件"}


def mtbf_table():
    print()
    print("=" * 122)
    print("(2) MTBF 重算 —— 光学子系统 (1,650 FIT) 剥离前后对比")
    print("=" * 122)
    n = sum(c[1] for c in COMP)
    fit_all = sum(c[1] * c[2] for c in COMP)
    fit_no = sum(c[1] * c[2] for c in COMP if c[0] not in OPTICAL)
    opt = fit_all - fit_no
    print(f"器件数 = {n}")
    print(f"ΣFIT (含光学)  = {fit_all}   元件级 MTBF = {1e9/fit_all:,.0f} h = {1e9/fit_all/8766:.1f} 年")
    print(f"ΣFIT (剥离光学) = {fit_no}   元件级 MTBF = {1e9/fit_no:,.0f} h = {1e9/fit_no/8766:.1f} 年")
    print(f"光学子系统 = {opt} FIT = 占含光学模型 {opt/fit_all*100:.1f}% / 占剥离后模型 {opt/fit_no*100:.1f}%")
    print()
    print(f"{'工况':<16}{'AF':>8}{'D':>7}{'ΣFIT(含光)':>13}{'MTBF(含光)':>15}{'ΣFIT(剥光)':>13}{'MTBF(剥光)':>16}")
    rows = {}
    for lab, t, d in (("A 满载 55C", 55, 1.0), ("B 按需 40C", 40, 0.19),
                      ("C 按需 55C", 55, 0.19), ("D 按需 35C", 35, 0.19)):
        s_all = sum(c[1] * c[2] * ((1 - c[3]) + c[3] * af(t) * (d if c[4] else 1.0)) for c in COMP)
        s_no = sum(c[1] * c[2] * ((1 - c[3]) + c[3] * af(t) * (d if c[4] else 1.0))
                   for c in COMP if c[0] not in OPTICAL)
        rows[lab] = (s_all, s_no)
        print(f"{lab:<16}{af(t):>8.3f}{d:>7.2f}{s_all:>13,.0f}{1e9/s_all:>14,.0f}h{s_no:>13,.0f}{1e9/s_no:>15,.0f}h")
    b_all, b_no = rows["B 按需 40C"]
    print()
    print(f"  剥离光学后: 元件级 MTBF ×{(1e9/fit_no)/(1e9/fit_all):.2f} ; 主用工况 B (按需 40C) "
          f"×{(1e9/b_no)/(1e9/b_all):.2f} ({1e9/b_all:,.0f}h -> {1e9/b_no:,.0f}h)")
    print("  ★ 结论: 光学件一旦从模型里拿掉, 剩下的 2,574 FIT 全部是通用代表值 —— "
          "MTBF 数字变好看不代表整机更可靠, 只说明**光学件是这个模型里唯一不可预测的部分**。")
    return fit_all, fit_no


# =====================================================================
# (3) R-F4 / R-F5 充电域结温边界
# =====================================================================
def thermal_boundary():
    print()
    print("=" * 122)
    print("(3) 充电域结温边界 (R-F4 BQ25896 / R-F5 TPS25730) —— 全部用官方 RθJA")
    print("=" * 122)
    lim = 85 * 0.85
    print(f"BQ25896: REC TA_max 85C -> 建议上限 {lim:.2f}C; 官方 RθJA(RTW WQFN24) 31.8 C/W; 耗散 0.5W")
    for ta in (35, 40, 45, 50, 55, 60):
        tj = ta + 0.5 * 31.8
        u = tj / lim * 100
        print(f"   TA={ta:>3}C -> Tj={tj:>5.1f}C -> 占用 {u:>5.1f}%  "
              f"{'OK' if u < 80 else ('WARN' if u < 100 else 'FAIL')}")
    print(f"   => 充电板环境温度上限: 占用<=100% 时 TA<={lim - 0.5*31.8:.1f}C ; "
          f"占用<=80% 时 TA<={0.8*lim - 0.5*31.8:.1f}C   ★这是 R-F4 的硬约束")
    lim2 = 65 * 0.85
    print()
    print(f"TPS25730D: REC TA_max 45C(@<=7A)/65C(@<=6A) -> 建议上限 {lim2:.2f}C; "
          f"官方 RθJA(QFN38, sink through PP_HV) 57.4 C/W; 通路损耗 0.04W@2A")
    for ta in (35, 40, 45, 50, 55):
        tj = ta + 0.04 * 57.4
        u = tj / lim2 * 100
        print(f"   TA={ta:>3}C -> Tj={tj:>5.1f}C -> 占用 {u:>5.1f}%  "
              f"{'OK' if u < 80 else ('WARN' if u < 100 else 'FAIL')}")
    print("   ★ 官网产品页 '-40~125C' 是 TJ 口径, 按 TA 用会把余量高估 1.9 倍 (R-F5)")


if __name__ == "__main__":
    derating_table()
    mtbf_table()
    thermal_boundary()
    print()
    print("AF 表: 35C=%.3f 40C=1.000 55C=%.3f 70C=%.3f" % (af(35), af(55), af(70)))
