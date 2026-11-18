#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW_TIMING_REVIEW 的机械复核器 (ISS-090 软件侧交叉评审)
=====================================================================
用途: 本文所有"可算的数"必须能从网表/器件表的原始值重新算一遍,
      任何人一条命令就能复现 (交接单 B6)。

跑法:
    python3 SW/tools/timing_check.py            # 打印全部推算 + 自检
    python3 SW/tools/timing_check.py --json     # 机读
退出码: 0 = 自检全过 (不等于结论成立, 只等于"算术与文档一致")

铁律: 本脚本只做**算术复核**, 不做"设计对不对"的判断。
      器件级常数一律注明来源 (官方 datasheet / 网表原值), 查不到就写 0数据。
"""
from __future__ import annotations

import argparse
import json
import math
import sys

# ----------------------------------------------------------------------------
# 0. 原始输入 —— 全部来自 HW/netlist_v1.csv (V1.6) 与器件 datasheet
# ----------------------------------------------------------------------------
NET = {
    # P8 复位链
    "R_PU_RESET_N": 10_000,      # Ω  网表 P8: 上拉到 VDD_1V8_IO
    "R_SER_RESET_N": 1_000,      # Ω  网表 P8: 串到 SoC RESET_N
    "C_RST": 100e-9,             # F  网表 P8: 100nF
    "V_RESET_PULL": 1.8,         # V  网表 P8: RESET_N 上拉轨电平 [待原厂]
    # P8 监督器
    "U_SUPV_VIT_REF": 0.405,     # V  TPS3808G01: VIT = 0.405 x (1 + R1/R2)  [官方 ti.com/lit/ds/symlink/tps3808.pdf]
    "U_SUPV_DELAY_CT_OPEN": 20e-3,   # s  TPS3808: CT 悬空 → 复位延时 20ms  [官方]
    "U_SUPV_DELAY_CT_VDD": 300e-3,   # s  TPS3808: CT 经电阻接 VDD → 300ms  [官方]
    # P2 I2C_A / P4 I2C_B
    "R_I2C_PULL": 4_700,         # Ω  网表 P2/P4: 4.7k 上拉到 3.3V
    "C_I2C_ASSUMED": 100e-12,    # F  网表注释按 100pF 标注 (t_r 注记本身有误, 见 F1)
    # P2 ADC 检测通道
    "R_DET_TOP": 1_000_000,      # Ω  网表 P2: VBUS_DET/BAT_DET 上臂
    "R_DET_BOT": 1_000_000,      # Ω  网表 P2: 下臂
    "C_DET": 100e-9,             # F  网表 P2: 滤波电容
    "V_DET_FS": 3.3,             # V  SoC ADC 满量程 (3.3V 域)
    "ADC_BITS": 12,              # bit [待原厂] SoC ADC 分辨率未确认, 按 12bit 算
    "I_ADC_LEAK_MAX": 1e-6,      # A  典型 SoC ADC 输入漏电流上限 (量级) [0数据: 具体型号未确认]
    # P2 TMP117
    "TMP117_LSB_C": 0.0078125,   # °C [官方 ti.com/lit/gpn/TMP117]
    "TMP117_IV_SUPPLY": 5e-6,    # A  [官方] 5µA max
    "TMP117_V_SUPPLY": 3.3,      # V  网表 P2: 3.3V 供电
    "TMP117_RESET_READ": -256.0, # °C [官方] 复位后首读 = −256°C 直到首次转换完成
    "TMP117_CONV_PERIOD": 1.0,   # s  [官方] 8 averages / 1-Hz conversion cycle
    # P9 / P6 跨铰链 USB
    "CONN_USB_PINS": 4,          # pin  网表 P9: D+/D-/GND/预留
    "CONN_USB_GND_PINS": 1,      # pin  网表 P9: 只有 pin3 一个地
    "ISS085_MIN_GND_PINS": 2,    # pin  ISS-085 (mech-lead) 跨铰链规则: 两端各留 ≥2 个 GND pin
    "USB_FS_MBPS": 12.0,         # Mbit/s [官方 USB 2.0]
    "USB_HS_MBPS": 480.0,        # Mbit/s [官方 USB 2.0]
    "FLASH_IMAGE_MB": 90,        # MB SW/FLASH_AND_VERSION.md §4.1 分区表总量 (boot1+kern8+rootfs30+app16+model30+isp1)
    "USB_RESET_RESP_S": 5e-3,    # s  [官方 USB 2.0 §7.1.7.3] 设备须在总线复位结束后 5ms 内驱动复位握手
    # 热模型 (MECH/MECH_BUDGET.md §2.3)
    "T_SKIN_A": 35.0,            # °C  T_skin = 35.0 + 50.13 x P
    "T_SKIN_B": 50.13,           # °C/W
    "T_SKIN_REDLINE": 43.0,      # °C  ISO 13732-1 红线
    "P_REDLINE": 0.16,           # W  贴皮肤镜腿持续发热量上限 (对应 43.0°C)
}

# 判定用的容差
TOL = 1e-9


def r(x: float, n: int = 3) -> float:
    return round(x + 0.0, n)


def compute() -> dict:
    o: dict = {}

    # ---------------------------------------------------------------- F1 复位 RC
    # 上电释放: 监督器放开 (高阻) + 按键松开 → 戴维宁源 = 1.8V 经 (10k + 1k)
    tau_rel = (NET["R_PU_RESET_N"] + NET["R_SER_RESET_N"]) * NET["C_RST"]
    # 断言 (按键按下): SoC 侧经 1k 对 100nF 放电
    tau_asr = NET["R_SER_RESET_N"] * NET["C_RST"]
    # 上升到 VIH (取 0.7 x VDD 为典型 VIH 下限 [0数据: SoC 手册未到])
    vih = 0.7 * NET["V_RESET_PULL"]
    t_vih = tau_rel * math.log(1.0 / (1.0 - 0.7))
    o["F1_reset_rc"] = {
        "tau_release_ms": r(tau_rel * 1e3),
        "tau_assert_us": r(tau_asr * 1e6),
        "t_reach_0p7vdd_ms": r(t_vih * 1e3),
        "netlist_annotation_ms": 100.0,
        "annotation_error_ratio": r(100e-3 / tau_rel, 1),
        "verdict": "网表注记 'τ=100ms' 与 R/C 原值不符: 实为释放 τ=1.1ms / 断言 τ=100µs",
    }

    # ---------------------------------------------------------------- F2 监督器
    # VIT = 0.405 x (1 + R1/R2); 监督 V_SOC_IO 时反解所需的 R1/R2
    def ratio_for(vit: float) -> float:
        return vit / NET["U_SUPV_VIT_REF"] - 1.0
    o["F2_supervisor"] = {
        "vit_ref_v": NET["U_SUPV_VIT_REF"],
        "ratio_for_vit_3v0": r(ratio_for(3.0), 3),
        "ratio_for_vit_2v7": r(ratio_for(2.7), 3),
        "delay_ct_open_ms": r(NET["U_SUPV_DELAY_CT_OPEN"] * 1e3),
        "delay_ct_vdd_ms": r(NET["U_SUPV_DELAY_CT_VDD"] * 1e3),
        "ct_pin_in_netlist": False,
        "min_reset_release_ms": r(NET["U_SUPV_DELAY_CT_OPEN"] * 1e3 + tau_rel * 1e3 * 1.204),
        "note": "两臂都填 0Ω => R2=0 => SENSE=GND => V_SOC_IO 对地短路 (装配级灾难); "
                "两臂都 DNP => SENSE 悬空 => 释放时刻未定义",
        "divider_zero_risk": True,
    }

    # ---------------------------------------------------------------- F3 I2C 上升沿
    tr_100p = 0.8473 * NET["R_I2C_PULL"] * NET["C_I2C_ASSUMED"]
    trs = {f"{c}pF": r(0.8473 * NET["R_I2C_PULL"] * (c * 1e-12) * 1e9) for c in (100, 200, 300, 500)}
    o["F3_i2c_rise"] = {
        "tr_ns_at_100pF": r(tr_100p * 1e9, 1),
        "netlist_annotation_ns": 2380.0,
        "annotation_error_ratio": r(2380e-9 / tr_100p, 2),
        "tr_ns_vs_cable_cap": trs,
        "spec_std_mode_max_ns": 1000.0,
        "spec_fast_mode_max_ns": 300.0,
        "verdict": "4.7k@100pF 实算 %.0fns (网表注记 2380ns 差 %.1f 倍); "
                   "跨铰链线缆电容 300pF 时 %.0fns > 标准模式 1000ns 上限 => I2C_A 必须锁 100kHz"
                   % (tr_100p * 1e9, 2380e-9 / tr_100p, trs["300pF"]),
    }

    # ---------------------------------------------------------------- F4 ADC 检测通道
    rth = (NET["R_DET_TOP"] * NET["R_DET_BOT"]) / (NET["R_DET_TOP"] + NET["R_DET_BOT"])
    tau_adc = rth * NET["C_DET"]
    lsb_v = NET["V_DET_FS"] / (2 ** NET["ADC_BITS"])
    n_settle = math.log(1.0 / (0.5 * lsb_v / NET["V_DET_FS"]))
    t_settle = n_settle * tau_adc
    leak_err = NET["I_ADC_LEAK_MAX"] * rth
    o["F4_adc_det"] = {
        "rth_ohm": r(rth, 0),
        "tau_ms": r(tau_adc * 1e3),
        "t_settle_to_half_lsb_ms": r(t_settle * 1e3),
        "leak_offset_v": r(leak_err, 4),
        "leak_offset_pct_fs": r(leak_err / NET["V_DET_FS"] * 100, 1),
        "standby_ua": r(NET["V_DET_FS"] / (NET["R_DET_TOP"] + NET["R_DET_BOT"]) * 1e6, 2),
        "verdict": "1M+1M+100nF => 源阻抗 500kΩ / τ=50ms; 12bit 精度需 %.0fms 建立; "
                   "1µA 漏电流 => %.2fV 偏移 (%.0f%% 满量程) => 该分压值对 ADC 不可用"
                   % (t_settle * 1e3, leak_err, leak_err / NET["V_DET_FS"] * 100),
    }

    # ---------------------------------------------------------------- F5 TMP117
    self_heat_uw = NET["TMP117_IV_SUPPLY"] * NET["TMP117_V_SUPPLY"] * 1e6
    o["F5_tmp117"] = {
        "lsb_c": NET["TMP117_LSB_C"],
        "first_read_after_reset_c": NET["TMP117_RESET_READ"],
        "conv_period_s": NET["TMP117_CONV_PERIOD"],
        "self_heat_uw": r(self_heat_uw, 2),
        "self_heat_verdict": "自热 %.1fµW << 测点热阻主导项 => 自热可忽略, 误差由**热耦合路径**主导" % self_heat_uw,
        "accuracy_bands_c": {"-20..50": 0.1, "-40..70": 0.15, "-40..100": 0.2},
        "sw_rule": "复位后首读 = -256°C 必须丢弃; 转换 1Hz => 首次有效读数最坏 ~1s",
    }

    # ---------------------------------------------------------------- F6 跨铰链 USB
    fs_mb_s = NET["USB_FS_MBPS"] / 8.0 * 0.8      # bulk 实测效率按 80% [推算]
    hs_mb_s = NET["USB_HS_MBPS"] / 8.0 * 0.8
    o["F6_usb_hinge"] = {
        "conn_usb_pins": NET["CONN_USB_PINS"],
        "conn_usb_gnd_pins": NET["CONN_USB_GND_PINS"],
        "iss085_min_gnd_pins": NET["ISS085_MIN_GND_PINS"],
        "gnd_rule_ok": NET["CONN_USB_GND_PINS"] >= NET["ISS085_MIN_GND_PINS"],
        "fs_bulk_MBps": r(fs_mb_s, 2),
        "hs_bulk_MBps": r(hs_mb_s, 2),
        "flash_s_at_FS": r(NET["FLASH_IMAGE_MB"] / fs_mb_s, 1),
        "flash_s_at_HS": r(NET["FLASH_IMAGE_MB"] / hs_mb_s, 1),
        "reset_resp_budget_ms": r(NET["USB_RESET_RESP_S"] * 1e3),
        "verdict": "CONN_USB 只有 1 个 GND pin, 违反 ISS-085 自己定的 '≥2 个 GND pin' 规则; "
                   "pin4 现为预留(DNP) => 改成 GND 零成本",
    }

    # ---------------------------------------------------------------- F7 皮肤温度阈值换算
    tiers = {}
    for p in (0.05, 0.10, 0.16, 0.21):
        tiers["%.2fW" % p] = r(NET["T_SKIN_A"] + NET["T_SKIN_B"] * p, 1)
    o["F7_skin_tiers"] = {
        "model": "T_skin = %.1f + %.2f x P_W" % (NET["T_SKIN_A"], NET["T_SKIN_B"]),
        "p_to_tskin": tiers,
        "redline_c": NET["T_SKIN_REDLINE"],
        "p_redline_w": NET["P_REDLINE"],
        "legacy_sw_tiers_c": [70, 85, 95],
        "legacy_verdict": "SW 分片里已登记的 4 档温控 (<70/70-85/85-95/>95°C) 是**结温口径**, "
                          "与 43°C 皮肤红线不同源 => TMP117 定点后必须重定档",
        "tmp117_conservatism": "TMP117 装在镜脚 PCB 上 => T_PCB >= T_skin (皮肤是热沉) "
                               "=> 用 PCB 温度当皮肤代理是**保守方向** (不会漏判超温)",
    }

    # ---------------------------------------------------------------- F8 关机语义
    o["F8_power_off"] = {
        "load_switch_in_netlist": False,
        "rail_switching_devices": 0,
        "verdict": "网表里没有负载开关/电源开关/EN 断开路径 => 电池经 BQ2970 保护管后直连 SYS, "
                   "关机只能靠软件深睡, 轨全部带电",
    }

    return o


# ----------------------------------------------------------------------------
# 自检: 文档里写的关键数字必须与本脚本算出来的一致
# ----------------------------------------------------------------------------
SELF_TESTS = [
    ("复位释放 tau = 1.1ms", lambda o: abs(o["F1_reset_rc"]["tau_release_ms"] - 1.1) < 0.01),
    ("复位断言 tau = 100us", lambda o: abs(o["F1_reset_rc"]["tau_assert_us"] - 100.0) < 0.5),
    ("复位到 VIH = 1.32ms", lambda o: abs(o["F1_reset_rc"]["t_reach_0p7vdd_ms"] - 1.32) < 0.02),
    ("网表注记误差 >= 50 倍", lambda o: o["F1_reset_rc"]["annotation_error_ratio"] >= 50),
    ("监督器 CT 悬空延时 = 20ms", lambda o: abs(o["F2_supervisor"]["delay_ct_open_ms"] - 20.0) < 0.01),
    ("两臂 0Ω 短路风险已标注", lambda o: o["F2_supervisor"]["divider_zero_risk"] is True),
    ("I2C t_r@100pF = 398ns", lambda o: abs(o["F3_i2c_rise"]["tr_ns_at_100pF"] - 398.0) < 1.0),
    ("I2C 注记误差 >= 5 倍", lambda o: o["F3_i2c_rise"]["annotation_error_ratio"] >= 5.0),
    ("I2C 300pF 超标准模式上限", lambda o: o["F3_i2c_rise"]["tr_ns_vs_cable_cap"]["300pF"] > 1000.0),
    ("ADC 源阻抗 500k", lambda o: abs(o["F4_adc_det"]["rth_ohm"] - 500000.0) < 1.0),
    ("ADC tau = 50ms", lambda o: abs(o["F4_adc_det"]["tau_ms"] - 50.0) < 0.5),
    ("ADC 12bit 建立 > 300ms", lambda o: o["F4_adc_det"]["t_settle_to_half_lsb_ms"] > 300.0),
    ("ADC 漏电偏移 > 0.4V", lambda o: o["F4_adc_det"]["leak_offset_v"] > 0.4),
    ("TMP117 首读 -256C", lambda o: o["F5_tmp117"]["first_read_after_reset_c"] == -256.0),
    ("TMP117 自热 < 0.1mW", lambda o: o["F5_tmp117"]["self_heat_uw"] < 100.0),
    ("CONN_USB 地脚数不合规", lambda o: o["F6_usb_hinge"]["gnd_rule_ok"] is False),
    ("FS 刷 90MB < 120s", lambda o: o["F6_usb_hinge"]["flash_s_at_FS"] < 120.0),
    ("HS 刷 90MB < 8s", lambda o: o["F6_usb_hinge"]["flash_s_at_HS"] < 8.0),
    ("0.05W -> 37.5C", lambda o: abs(o["F7_skin_tiers"]["p_to_tskin"]["0.05W"] - 37.5) < 0.1),
    ("0.16W -> 43.0C (红线)", lambda o: abs(o["F7_skin_tiers"]["p_to_tskin"]["0.16W"] - 43.0) < 0.1),
    ("无硬件断电路径", lambda o: o["F8_power_off"]["load_switch_in_netlist"] is False),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    o = compute()
    if args.json:
        print(json.dumps(o, ensure_ascii=False, indent=2))
        return 0

    for k, v in o.items():
        print("=== %s ===" % k)
        for kk, vv in v.items():
            print("   %-34s : %s" % (kk, vv))
        print()

    print("=== SELF-TEST (%d 项) ===" % len(SELF_TESTS))
    fails = 0
    for name, fn in SELF_TESTS:
        try:
            ok = bool(fn(o))
        except Exception as e:  # noqa: BLE001
            ok = False
            name += "  [EXC %s]" % e
        print("  [%s] %s" % ("PASS" if ok else "FAIL", name))
        if not ok:
            fails += 1
    print("\nSELFTEST %d/%d 通过, rc=%d" % (len(SELF_TESTS) - fails, len(SELF_TESTS), 1 if fails else 0))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
