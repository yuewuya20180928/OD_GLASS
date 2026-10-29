#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-067 (hw-lead) R-F1 3.3V 轨拓扑 / UVP 裁决 —— 数字自证脚本
================================================================
本脚本是 HW/POWER_TOPOLOGY_RF1_3V3V_UVP.md 里所有数字的唯一出处。
跑法:  python3 HW/calc_rf1_3v3v_uvp.py

证据分级
--------
[实测] 本脚本输出 (由下面的 [官方] 参数 + [推算] 模型跑出)
[官方] TPS7A20 dropout 110mV typ · TPS62130A Vin 3-17V / Vout 0.9-6V / 3A / 100% 占空比 /
       VQFN-16 3x3mm · BQ2970 OVP 4.275V (1S 保护, UVP 阈值本仓库未核 -> [0数据])
[推算] 1S 锂电放电曲线: 3.41V->3.0V 区间占总容量 12-15% (RELIABILITY_DESIGN R-F1) 取中值 13.5%;
       3.41->3.50V 窄带 = 3% 标称容量; DoD 0.9 (放电窗口 4.2V->3.0V);
       TPS62130A 效率 88-93% (POWER_BUDGET_V3 §10-3, 效率曲线本身 [0数据]);
       buck-boost 效率 85-90% [推算]; 皮肤侧模型 39.25 / 50.13 K/W (MECH_BUDGET §2.3.1)
"""
from __future__ import annotations

# ---------------- 参数 ----------------
CELL_MAH   = 420.0    # 丰江 432243 >=420mAh, 4.3x22.0x43.5mm (库内网表 BT_432243) [官方]
DOD        = 0.90     # 放电窗口 4.2->3.0V 占标称容量的比例 [官方/口径]
V_NOM      = 3.7      # 标称电压 (口径 A 写死) [官方]
ETA_CHG    = 0.83     # 充电效率 (只用于口径 B 选电芯) [推算]
I33        = 0.350    # 3.3V 轨总负载 = LIGHT_3V3 150mA + VDD_3V3_IO 200mA [推算/库内电源域表]
V33        = 3.30
P33_OUT    = V33 * I33                    # 1.155 W
LDO_DROP   = 0.110    # TPS7A20 dropout 110mV typ [官方]
R_BUCK_TOT = 0.10     # buck 高边 R_on + 电感 DCR 合计假设 100mΩ [0数据 待原厂核]
BUCK_FLOOR = V33 + I33 * R_BUCK_TOT      # buck 自身可维持 3.3V 的最低 SYS

FRAC_BELOW_341 = 0.135   # 3.41->3.0V 占标称容量 (12-15% 取中) [推算]
BAND_341_350   = 0.030   # 3.41->3.50V 窄带占标称容量 [推算]


def usable(v: float) -> float:
    """把放电截止电压 v 换成'可用容量占标称容量的比例' (含 DoD 0.9)。

    归一化 (都以标称容量为分母):
      3.0V 以下 = 10% (DoD 0.9 的含义: 放电窗口 4.2->3.0V 占标称 90%)
      3.0->3.41V 这条带 = 13.5% 标称 (R-F1 原文"3.41->3.0 区间占 12-15%")
      => 3.41V 以上 = 76.5% 标称
    """
    if v >= 4.2:
        return 1.0
    if v >= 3.41:      # 3.41->4.2: 76.5% 全部在上面, 再扣 3.41->v 的窄带
        band = BAND_341_350 * (v - 3.41) / 0.09 if v > 3.41 else 0.0
        return 0.765 - band
    if v >= 3.0:       # 3.0->3.41: 线性插值
        return 0.765 + FRAC_BELOW_341 * (3.41 - v) / 0.41
    return 0.0


def v_avg(v_lo: float) -> float:
    """放电窗口 [v_lo, 4.2] 的平均电压 [推算]"""
    return 3.80 if v_lo <= 3.41 else (4.2 + v_lo) / 2 - 0.05


def loss_mw(kind: str, v_sys_avg: float, eta: float) -> float:
    if kind == "LDO":
        return max(0.0, v_sys_avg - V33) * I33 * 1000
    return P33_OUT * (1 / eta - 1) * 1000


SCEN = [
    ("S0", "现状: 3.3V 用 LDO, SYS<3.41V 时 3.3V 轨已失效 (突然黑屏)", 3.41, "LDO", 0.82),
    ("A",  "方案A: UVP 3.50V + 3.3V 由 TPS62130A buck 供 (PM 裁决基线)", 3.50, "BUCK", 0.82),
    ("A2", "方案A': UVP 3.35V + 3.3V 由 buck 供 (UVP 压到 buck 自身地板)", 3.35, "BUCK", 0.82),
    ("B",  "方案B: UVP 3.00V + 3.3V 由 buck-boost 供 (第三条路)", 3.00, "BB", 0.82),
]
ETA_BUCK = (0.88, 0.92, 0.93)
ETA_BB = (0.85, 0.90)

P_LOADS = [("满载 无桥 中位", 0.82), ("满载 无桥 上界", 1.01),
           ("满载 有桥 中位", 1.02), ("按需 待机-A", 0.217)]

print("=" * 100)
print("§1  可用容量窗口 (电芯 = 丰江 432243 >=420mAh, 4.3mm)")
print("=" * 100)
print(f"{'截止电压':<12}{'可用比例':<12}{'可用容量(mAh)':<18}说明")
for v, note in ((3.41, "LDO 轨失效点 (R-F1 现状)"), (3.50, "方案A UVP"),
                (3.35, "方案A' UVP = buck 自身地板"), (3.30, "3.3V 标称"),
                (3.00, "BQ2970 保护下限 = DoD 窗口底")):
    u = usable(v)
    print(f"{v:<12.2f}{u:<12.3f}{CELL_MAH*u:<18.1f}{note}")
print(f"\n★ 3.3V 轨地板电压: LDO 需 SYS >= {3.3+LDO_DROP:.3f}V (110mV dropout [官方])"
      f"  |  buck 需 SYS >= {BUCK_FLOOR:.3f}V (100mΩ 合计串联 [0数据 待核])")

print()
print("=" * 100)
print("§2  口径A 续航读数  t[h] = Capacity[mAh] x DoD x V / P[W]   (V=3.7 写死, DoD 有效 = usable)")
print("=" * 100)
print(f"{'场景':<5}{'SYS地板':<9}{'usable':<9}{'eta':<7}{'损耗mW':<9}{'P_SYS(W)':<11}"
      f"{'t_A(h)':<10}{'相对S0':<9}{'t_ref(Vavg)':<12}")
base_t = None
res = {}
for key, name, floor, kind, p_load in SCEN:
    u = usable(floor)
    va = v_avg(floor)
    etas = ETA_BUCK if kind == "BUCK" else (ETA_BB if kind == "BB" else (1.0,))
    for eta in etas:
        lm = loss_mw(kind, va, eta)
        p_sys = p_load + lm / 1000
        t_a = CELL_MAH * u * V_NOM / p_sys
        t_r = CELL_MAH * u * va / p_sys
        res[(key, eta)] = (u, p_sys, t_a, lm)
        etal = "LDO" if kind == "LDO" else f"{eta:.2f}"
        if key == "S0":
            base_t = t_a
        rel = "" if key == "S0" else f"{(t_a/base_t-1)*100:+.1f}%"
        print(f"{key:<5}{floor:<9.2f}{u:<9.3f}{etal:<7}{lm:<9.0f}{p_sys:<11.3f}"
              f"{t_a:<10.3f}{rel:<9}{t_r:<12.3f}")
    print()

print("=" * 100)
print("§3  口径B 选电芯 (1h): mAh_required = P x 1000 / 3.7 / 0.83 / usable")
print("=" * 100)
print(f"{'工况':<18}{'P_load':<9}{'场景':<5}{'usable':<9}{'按P_load(mAh)':<17}{'按P_SYS(mAh)':<16}{'420mAh够?'}")
for label, p_load in P_LOADS:
    for key, name, floor, kind, _ in SCEN:
        if key not in ("A", "A2", "B", "S0"):
            continue
        if key != "A" and label != "满载 无桥 中位":
            continue
        etak = 0.92 if key in ("A", "A2") else (0.90 if key == "B" else 1.0)
        u = usable(floor)
        kind = {k: kd for k, _, fl, kd, _ in SCEN}[key]
        p_sys = p_load + loss_mw(kind, v_avg(floor), etak) / 1000
        n_load = p_load * 1000 / V_NOM / ETA_CHG / u
        n_sys = p_sys * 1000 / V_NOM / ETA_CHG / u
        ok = (f"够 (余 {(CELL_MAH/n_sys-1)*100:.0f}%)" if n_sys <= CELL_MAH
              else f"不够 (差 {n_sys-CELL_MAH:.0f}mAh -> 需 650mAh/8.5mm ❌形态)")
        print(f"{label:<18}{p_load:<9.2f}{key:<5}{u:<9.3f}{n_load:<17.0f}{n_sys:<16.0f}{ok}")
    print()

print("=" * 100)
print("§4  3.3V 轨转换损耗 -> 镜腿内发热 -> 皮肤侧温度 (MECH 模型 39.25 / 50.13 K/W)")
print("=" * 100)
for key, name, floor, kind, p_load in SCEN:
    u = usable(floor)
    va = v_avg(floor)
    etas = ETA_BUCK if kind == "BUCK" else (ETA_BB if kind == "BB" else (1.0,))
    for eta in etas:
        lm = loss_mw(kind, va, eta)
        etal = "LDO" if kind == "LDO" else f"{eta:.2f}"
        print(f"{key:<5}({kind:<5} eta={etal:<5}) 镜腿内 +{lm:>4.0f} mW -> 皮肤侧 "
              f"+{lm/1000*39.25:.2f} ~ +{lm/1000*50.13:.2f} °C")
print("\n★ 方案A 相对现状(S0): 100mW - 175mW = -75 mW -> 皮肤侧 -2.94 ~ -3.76 °C   [推算]")
print("★ 但 V3/MECH 现论文值 (镜腿内发热量 0.90W 口径) 未含 LDO/buck 损耗 ->")
print("  方案A 需在热模型里补 +100mW -> 皮肤侧 +3.93 ~ +5.01 °C               [推算]")

print()
print("=" * 100)
print("§5  SYS 电流 (I = P_SYS / 3.7V, 选型余量 x1.5, 库内 SYS 上限 0.55A)")
print("=" * 100)
for key, name, floor, kind, p_load in SCEN:
    u = usable(floor)
    va = v_avg(floor)
    etas = ETA_BUCK if kind == "BUCK" else (ETA_BB if kind == "BB" else (1.0,))
    for eta in etas:
        lm = loss_mw(kind, va, eta)
        p_sys = p_load + lm / 1000
        i = p_sys / V_NOM
        etal = "LDO" if kind == "LDO" else f"{eta:.2f}"
        print(f"{key:<5} P_SYS={p_sys:.3f}W -> I_SYS={i:.3f}A (x1.5={i*1.5:.3f}A) "
              f"{'OK' if i*1.5 <= 0.55 else '超!'}   eta={etal}")

print()
print("=" * 100)
print("§6  第三条路对比 (同一 P_load=0.82W 满载中位, 满载无桥)")
print("=" * 100)
print(f"{'路径':<26}{'SYS地板':<9}{'usable':<9}{'t_A(h) eta中':<14}{'相对S0':<9}{'新增IC':<8}{'相对S0容量'}")
for key, name, floor, kind, p_load in SCEN:
    u = usable(floor)
    va = v_avg(floor)
    eta = 0.92 if kind == "BUCK" else (0.90 if kind == "BB" else 1.0)
    lm = loss_mw(kind, va, eta)
    p_sys = p_load + lm / 1000
    t_a = CELL_MAH * u * V_NOM / p_sys
    add = {"S0": "0 (现状)", "A": "+1 buck", "A2": "+1 buck", "B": "+1 buck-boost"}[key]
    caprel = "" if key == "S0" else f"{(u/usable(3.41)-1)*100:+.1f}%"
    print(f"{name[:24]:<26}{floor:<9.2f}{u:<9.3f}{t_a:<14.3f}{(t_a/base_t-1)*100:+8.1f}%{add:<8}{caprel}")
