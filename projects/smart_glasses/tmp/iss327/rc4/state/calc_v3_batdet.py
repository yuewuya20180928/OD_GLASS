#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-223 · V-3 (BAT_DET 分压比) 可判化 · 误差预算自算脚本
=====================================================================
★**零外发** (不发邮件 / 询价 / 问询 / 采购) · ★**本单实物 [实测] = 0 条** ★

【口径来源】
· 公式口径 = ★**项目自己的** `SW/tools/timing_check.py` F4「ADC 检测通道」★ (★不是本单另起一套★)
      rth        = R_top || R_bot
      tau        = rth * C_filter
      lsb_v      = V_FS / 2**ADC_BITS
      n_settle   = ln(1 / (0.5 * lsb_v / V_FS))        # = ln(2**ADC_BITS)
      t_settle   = n_settle * tau
      leak_err   = I_ADC_LEAK_MAX * rth
★**V_FS 的订正**: `SW/tools/timing_check.py` 里 `DEVICE["V_DET_FS"] = 3.3` 是 ★**3.3V 域** 的口径;
  ★**`BAT_DET` 走 `J_SOM_P1 pin38 = SARADC_VIN5` = 1.8V 域** ⇒ 本脚本按 ★**1.8V typ / 1.98V max** 算
  (★依据 = RK3572 Datasheet Rev 1.1 §3.10 Table 3-16 + 电气总表 `SARADC_AVDD1V8` = 1.62/1.8/1.98V★)。

【证据分级】
· [官网]  RK3572 Datasheet Rev 1.1 (★项目库内 `HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.txt`★):
          Resolution 12 bit · AIN = AVSS18~AVDD18 · DNL ±1/±3 LSB · INL ±2/±6 LSB
          (Fs=1MS/s, FCLK=20MHz) · Top/Bottom Offset ±10/±20 LSB · Fs up to 1MS/s · 8 单端通道
· [实测]  本脚本输出 (★本机实算★) + 网表/脚表/BOM 本机实读
· [0数据] ★**SARADC_VIN5 的输入漏电流 / 输入电容 / 采样保持时间** ★
          ⇒ datasheet Table 3-16 【没有】漏电/输入电容行;
            datasheet 里那几条 `Input leakage current IPAD -10/NA/10 uA` 属于
            ★**Table 3-4 数字 GPIO**★, 【不是】SARADC (★已逐字核对表头与行归属★);
            输入电容 / t_acq / 内部采样电容 C_in: datasheet 全文无 ⇒ 在 Rockchip TRM (不公开);
            公开的 Linux 主线 `drivers/iio/adc/rockchip_saradc.c` 也【没有 rk3572 的条目】
            ⇒ RK3572 走 BSP 驱动 ⇒ 拿不到
          ⇒ 本脚本把 I_leak / C_in 当【显式未知量】做敏感度分析, ★**不拿量级值冒充实测**★

用法: python3 state/calc_v3_batdet.py
"""
import math

# ── [官网] RK3572 Datasheet Rev 1.1 §3.10 Table 3-16 + 电气总表 ──
ADC_BITS = 12
V_FS_TYP = 1.8      # SARADC_AVDD1V8 typ
V_FS_MAX = 1.98     # SARADC_AVDD1V8 max
V_AVDD_MIN = 1.62   # SARADC_AVDD1V8 min
DNL_TYP, DNL_MAX = 1.0, 3.0        # LSB
INL_TYP, INL_MAX = 2.0, 6.0        # LSB (Fs=1MS/s, FCLK=20MHz)
OFF_TYP, OFF_MAX = 10.0, 20.0      # LSB (EOT / EOB)

# ── [0数据] 未知的两个量 (★只做敏感度扫描, 不当实测★) ──
I_LEAK_SCENARIOS_UA = [0.05, 0.1, 0.2, 0.5, 1.0]   # µA
C_IN_SCENARIOS_PF = [10.0, 20.0, 30.0]             # pF (★通用 SAR 量级, 不是 RK3572 的值★)

# ── 电芯电压 ──
V_BAT_MAX = 4.20      # 满充 (HW/INTERFACE_TABLE.md C-03: 4.2V 满 / 3.0V 截止)
V_BAT_HI = 4.35      # 高镍/快充上界 (★按最坏算余量★)

# ── 候选方案: (名, R_top, R_bot, C_filter) ──
SCHEMES = [
    ("现行 1M+1M (DNP 未装)", 1.0e6, 1.0e6, 100e-9),
    ("V-3 方案A 2.0M+1.2M",   2.0e6, 1.2e6, 100e-9),
    ("V-3 方案D 2.0M+1.0M",   2.0e6, 1.0e6, 100e-9),
    ("★新方案E 100k+60k★",    100e3,  60e3, 100e-9),
    ("★新方案E' 100k+60k+1uF★", 100e3, 60e3, 1.0e-6),
]

RES_TOL = 0.01   # 电阻 ±1%


def r(x, n=3):
    return round(x, n)


def analyse(name, rt, rb, cf):
    ratio = rb / (rt + rb)
    rth = rt * rb / (rt + rb)
    tau = rth * cf
    lsb_typ = V_FS_TYP / 2 ** ADC_BITS
    lsb_max = V_FS_MAX / 2 ** ADC_BITS
    n_settle = math.log(1.0 / (0.5 * lsb_typ / V_FS_TYP))    # = ln(2**ADC_BITS)
    t_settle = n_settle * tau

    out = {"name": name, "ratio": ratio, "rth": rth, "tau": tau,
           "lsb_typ": lsb_typ, "lsb_max": lsb_max,
           "n_settle": n_settle, "t_settle": t_settle}

    # ── ① 满量程/过压判据 ──
    for vbat, tag in ((V_BAT_MAX, "4.20"), (V_BAT_HI, "4.35")):
        v_node = vbat * ratio
        out[f"v_node_{tag}"] = v_node
        out[f"util_{tag}_typ"] = v_node / V_FS_TYP * 100
        out[f"util_{tag}_max"] = v_node / V_FS_MAX * 100
        out[f"overvolt_{tag}"] = v_node > V_FS_MAX

    # ── ② 电阻比容差 (worst-case: 两颗反向取极值) ──
    k_r2 = rt / (rt + rb)     # ∂lnV/∂lnR2
    k_r1 = rb / (rt + rb)     # ∂lnV/∂lnR1 (取绝对值)
    d_ratio_rel = (k_r2 + k_r1) * RES_TOL
    out["ratio_tol_rel"] = d_ratio_rel
    out["ratio_tol_mv_bat"] = V_BAT_MAX * d_ratio_rel * 1000

    # ── ③ ADC 自身误差 (offset + INL + DNL, max) 折算到电池侧 ──
    adc_err_lsb = OFF_MAX + INL_MAX + DNL_MAX
    out["adc_err_lsb_max"] = adc_err_lsb
    out["adc_err_mv_node"] = adc_err_lsb * lsb_max * 1000
    out["adc_err_mv_bat"] = adc_err_lsb * lsb_max * 1000 / ratio

    # ── ④ 漏电误差 (敏感度: I_leak 未知) ──
    out["leak_bat_per_ua"] = 1e-6 * rt * 1000 / ratio   # mV(电池侧) per µA
    out["leak_tbl"] = []
    for il in I_LEAK_SCENARIOS_UA:
        dv_node = il * 1e-6 * rth
        out["leak_tbl"].append((il, r(dv_node * 1000, 2),
                                r(dv_node / V_FS_TYP * 100, 2),
                                r(dv_node / lsb_typ, 1),
                                r(dv_node / V_FS_TYP * 100 / 2 ** ADC_BITS * 100, 2)))
    # ── ⑤ 建立时间 (敏感度: C_in 未知 ⇒ 采样窗口要求) ──
    #    口径: ADC 采样电容 C_in 从【节点】取电荷, 时间常数 τ_in = (R_th + R_sw)·C_in
    #    ⇒ ½LSB 建立所需 t_acq = ln(2**12)·τ_in  (★这是【最坏】口径: 忽略外部滤波电容的缓冲★)
    out["cin_tbl"] = []
    for cin in C_IN_SCENARIOS_PF:
        tau_in = rth * cin * 1e-12
        out["cin_tbl"].append((cin, r(tau_in * 1e6, 3), r(n_settle * tau_in * 1e6, 1),
                                r(n_settle * tau_in * 1e3, 3)))
    # ── ⑥ 静态功耗 ──
    out["i_div_ua"] = V_BAT_MAX / (rt + rb) * 1e6
    out["p_div_uw"] = V_BAT_MAX * V_BAT_MAX / (rt + rb) * 1e6
    return out


def main():
    print("=" * 100)
    print("ISS-223 · V-3 (BAT_DET 分压比) 误差预算 · [官网]+[实测]+[0数据] 分级")
    print("  公式口径 = SW/tools/timing_check.py F4 (项目自己的公式) · V_FS 订正为 1.8V 域 (SARADC_VIN5)")
    print(f"  [官网] ADC_BITS={ADC_BITS} · V_FS typ={V_FS_TYP}V max={V_FS_MAX}V min={V_AVDD_MIN}V "
          f"· DNL max={DNL_MAX}LSB · INL max={INL_MAX}LSB · offset max={OFF_MAX}LSB")
    print("=" * 100)

    res = [analyse(*s) for s in SCHEMES]

    print("\n【表 1】方案总览")
    hdr = (f"{'方案':<28}{'k=R2/(R1+R2)':>13}{'R_th':>11}{'τ(ms)':>9}"
           f"{'t_settle ½LSB(ms)':>19}{'V_node@4.2':>12}{'利用率@1.8':>11}{'过压?':>7}")
    print(hdr)
    print("-" * len(hdr))
    for o in res:
        print(f"{o['name']:<28}{o['ratio']:>13.5f}{o['rth']/1e3:>9.1f}k"
              f"{o['tau']*1e3:>9.2f}{o['t_settle']*1e3:>19.1f}"
              f"{o['v_node_4.20']:>12.4f}{o['util_4.20_typ']:>10.1f}%"
              f"{'★是' if o['overvolt_4.20'] else '否':>7}")

    print("\n【表 2】误差项 (折算到电池侧 4.20V)")
    hdr2 = (f"{'方案':<28}{'比容差 (worst)':>18}{'ADC 自身 (max)':>16}{'漏电 @0.1µA':>16}"
            f"{'漏电 @1µA':>14}{'漏电@1µA 占FS':>15}")
    print(hdr2)
    print("-" * len(hdr2))
    for o in res:
        l01 = 0.1e-6 * o["rth"]
        l10 = 1.0e-6 * o["rth"]
        print(f"{o['name']:<28}{o['ratio_tol_rel']*100:>17.2f}%{o['adc_err_mv_bat']:>13.1f} mV"
              f"{l01*1000:>13.1f} mV{l10*1000:>11.1f} mV{l10/V_FS_TYP*100:>13.1f}%")

    print("\n【表 3】漏电敏感度 (ΔV_node / 占满量程 / LSB 数)  ★[0数据] I_leak 未知⇒只做扫描★")
    print(f"{'方案':<28}" + "".join(f"{'I=' + str(i) + 'µA':>22}" for i in I_LEAK_SCENARIOS_UA))
    for o in res:
        row = f"{o['name']:<28}"
        for (il, mv, pct, lsb, pct_lsb) in o["leak_tbl"]:
            row += f"{mv:>10.1f}mV{pct:>6.1f}%{lsb:>5.0f}"
        print(row)

    print("\n【表 4】建立时间敏感度 (C_in 未知) ★[0数据] ⇒ 反推需要的采样等待窗口★")
    print(f"{'方案':<28}" + "".join(f"{'C_in=' + str(c) + 'pF':>28}" for c in C_IN_SCENARIOS_PF))
    for o in res:
        row = f"{o['name']:<28}"
        for (cin, tau_us, t_us, t_ms) in o["cin_tbl"]:
            row += f"{'τ_in=' + str(tau_us) + 'us':>13}{'t_acq=' + str(t_us) + 'us':>15}"
        print(row)

    print("\n【表 5】静态功耗 (常开代价)")
    print(f"{'方案':<28}{'分压电流@4.2V':>16}{'分压功耗':>14}{'日耗 (24h)':>16}")
    print("-" * 76)
    for o in res:
        print(f"{o['name']:<28}{o['i_div_ua']:>13.2f} µA{o['p_div_uw']:>11.2f} µW"
              f"{o['i_div_ua']*24/1e3:>13.3f} mAh/日")

    print("\n【结论】")
    print("  ① 现行 1M+1M: V_node@4.2V = %.3fV > AVDD18 max %.2fV ⇒ ★过压, 判死★ (与 d2/d7 现状一致)"
          % (res[0]["v_node_4.20"], V_FS_MAX))
    a, d, e = res[1], res[2], res[3]
    print("  ② ★★A(2.0M+1.2M) 与 D(2.0M+1.0M) 的差别只有 R_th 的 12.5%% (750k vs 667k)★★")
    print("     ⇒ ★**两者都差 3 个数量级 (SAR ADC 要的是 kΩ 级源阻抗) ⇒ V-3 现在这个选项集是【伪选择】**★")
    print("  ③ ★**关键恒等式 (决定性)**: ΔV_leak(电池侧) = I_leak × R_th / k = I_leak × **R_top**★")
    print("     ⇒ A 与 D 的 R_top 都是 2.0M ⇒ ★**漏电误差项完全相同** (方案 E 的 R_top=100k ⇒ 小 20 倍)★")
    print("  ④ 电阻比容差项 (worst ±1%%) 也只跟 R_top/R_bot 的比值有关: A 与 D 同为 ±1.00%% ⇒ **相同**")
    print("  ⑤ ⇒ A 相对 D 的优势只有【利用率 87.5%% vs 77.8%%】+【电池侧分辨率 %.3fmV vs %.3fmV】+【静态电流 %.3fµA vs %.3fµA】"
          % (V_FS_TYP / 2 ** ADC_BITS / a["ratio"] * 1000,
             V_FS_TYP / 2 ** ADC_BITS / d["ratio"] * 1000,
             a["i_div_ua"], d["i_div_ua"]))
    print("  ⑥ ⇒ ★**推荐 (供 main/老板拍, 本单不代拍)**: 新增 ★**方案 E = 100k + 60k + 100nF**★")
    print("     · k 与 A 同 (0.375) ⇒ 利用率/分辨率不打折")
    print("     · R_th = %.1fkΩ ⇒ τ = %.2fms ⇒ t_settle(½LSB) = %.0fms ⇒ **软件等 ≥50ms 就能到 ½LSB**"
          % (e["rth"] / 1e3, e["tau"] * 1e3, e["t_settle"] * 1e3))
    print("     · 漏电 @1µA (★[0数据] 占位值★) ⇒ %.1fmV = %.1f%% FS ⇒ **可软件标定** (常数项)"
          % (1e-6 * e["rth"] * 1000, 1e-6 * e["rth"] / V_FS_TYP * 100))
    print("     · 代价: 常开 %.2fµA / %.0fµW ⇒ %.3f mAh/日 ⇒ ★**这是唯一的取舍, 归老板拍**★"
          % (e["i_div_ua"], e["p_div_uw"], e["i_div_ua"] * 24 / 1e3))
    print("  ⑦ ★**降级方案 (I_leak / C_in 拿不到时的兜底)**:")
    print("     · ① BAT_DET 的用途降级口径: 只作【低电量告警粗判 (±100mV 级)】, 不作【电量百分比显示】的精度基准")
    print("       ⇒ 依据: SW/SW_REQUIREMENTS M7-R6 只要求『软件侧确认电量读取正常』 (★不是百分比精度★)")
    print("     · ② 即便 I_leak = 1µA 这个最坏占位值, E 的总误差仍 < %.1f%% FS ⇒ 够用"
          % ((1e-6 * e["rth"] + e["adc_err_mv_node"] / 1000) / V_FS_TYP * 100))
    print("     · ③ SoM 手册 / SoC TRM 到手后只回填 3 个数 (I_leak / C_in / t_acq) ⇒ 可把误差算到 1 LSB 内")
    print("     · ④ ★**本单不落表 V-3 的值 (不许代拍)**: 网表仍是 1M+1M + DNP (诚实的现状)★")
    print("\n" + "=" * 100)


if __name__ == "__main__":
    main()
