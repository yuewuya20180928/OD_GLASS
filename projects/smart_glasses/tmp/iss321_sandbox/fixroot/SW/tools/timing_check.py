#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW_TIMING_REVIEW 的机械复核器 (ISS-090 原始版 + ISS-190 复评版)
=====================================================================
★★ISS-190 (2026-11-11) 复评版要点 —— 这版脚本**真的在读网表**★★
  原版 (ISS-090) 的病: 全文从不打开 `HW/netlist_v1.csv`, 只在第 25 行注释里
  提了一句文件名; 所有"网表相关数字"全是**手抄常量**:
    · `R_I2C_PULL = 4700` (注释写 "网表 P2/P4: 4.7k 上拉到 3.3V") —— 而现网表
      L169 的 `R_PU_I2CA_SCL` = **2.2k → RAIL_VDD_1V8_IO** (1.8V 域, ISS-153 订正)
    · F8 段直接写死 `"load_switch_in_netlist": False` / `"rail_switching_devices": 0`,
      自测却把 `is False` 当 PASS 条件 ⇒ **网表变了它照样绿** (假绿)
  本版改法:
    ① 用 `csv` 实读 `HW/netlist_v1.csv`; 凡网表可得的量一律**现读现算**
       (R/C 值、τ 注记、I2C 上拉阻值与**所属轨域**、EN/SS/CT/MR 脚是否在网表、
        复位/启动上拉挂在哪条轨、负载开关是否存在 ⇒ 按**器件位号**认, 不再用
        `LOAD|LOADSW|U_LS` 这种**看不见 U_PWR_SW** 的子串 pattern)
    ② 输出**必须打印网表锚点** (md5 + 行数) ⇒ 下次网表漂移一眼可见
    ③ 加**反向用例**: 把网表副本里某一行改坏 ⇒ 对应判据**必须变红** ⇒
       证明它真在读网表, 不是在演常量

跑法:
    python3 SW/tools/timing_check.py                 # 打印锚点 + 全部推算 + 自检
    python3 SW/tools/timing_check.py --json          # 机读
    python3 SW/tools/timing_check.py --netlist PATH  # 指定别处的一份网表 (反向用例用)
    python3 SW/tools/timing_check.py --reverse-demo  # ★当场演示"改坏网表 ⇒ 判据变红"
    python3 SW/tools/timing_check.py --only F1_reset_rc   # ★只打印某一条结论段 (复现命令用)

退出码: 0 = 自检全过 (不等于结论成立, 只等于"算术与文档一致")
        1 = 有自检没过

铁律: 本脚本只做**算术复核**, 不做"设计对不对"的判断。
      器件级常数一律注明来源 (官方 datasheet / 网表原值), 查不到就写 0数据。
      ★**网表是只读的**: 本脚本只读 HW/netlist_v1.csv, 从不写它; 反向用例写的是
      临时目录里的**副本**。
"""
from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import math
import os
import re
import shutil
import sys
import tempfile

# ----------------------------------------------------------------------------
# 0. 器件级常数 —— 不是网表能给的, 一律注明来源 (官方 datasheet / 规范原文)
# ----------------------------------------------------------------------------
DEVICE = {
    # --- TPS3808G01 (电压监控 + 复位) ---
    "U_SUPV_VIT_REF": 0.405,      # V   [官方] ti.com/lit/ds/symlink/tps3808.pdf: VIT = 0.405 x (1 + R1/R2)
    "U_SUPV_DELAY_CT_OPEN": 20e-3,   # s   [官方] TPS3808: CT 悬空 ⇒ 复位延时 20ms
    "U_SUPV_DELAY_CT_VDD": 300e-3,   # s   [官方] TPS3808: CT 经电阻接 VDD ⇒ 300ms
    "U_SUPV_DELAY_CT_CAP_MIN": 1.25e-3,  # s [官方] TPS3808: 外接电容 ⇒ 1.25ms~10s
    "U_SUPV_DELAY_CT_CAP_MAX": 10.0,     # s [官方] TPS3808: 外接电容 ⇒ 1.25ms~10s
    # --- TMP117 ---
    "TMP117_LSB_C": 0.0078125,   # °C  [官方] ti.com/lit/gpn/TMP117 (1 LSB = 7.8125 m°C)
    "TMP117_IV_SUPPLY": 5e-6,    # A   [官方] TMP117 供电电流 5µA max
    "TMP117_RESET_READ": -256.0, # °C  [官方] TMP117: 复位后首读 = −256°C 直到首次转换完成
    "TMP117_CONV_PERIOD": 1.0,   # s   [官方] TMP117: 8 averages / 1-Hz conversion cycle
    "TMP117_ACC_BANDS_C": {"-20..50": 0.1, "-40..70": 0.15, "-40..100": 0.2},  # °C [官方]
    # --- I2C 规范 ---
    "I2C_TR_STD_MAX_NS": 1000.0,   # ns  [官方] I2C 标准模式 (100kHz) 上升沿上限 1.0µs
    "I2C_TR_FAST_MAX_NS": 300.0,   # ns  [官方] I2C 快模式 (400kHz) 上升沿上限 300ns
    "I2C_TR_K": 0.8473,             # -   [推算] 10%→90% 上升时间系数 = ln(9) = 2.1972
    # --- USB 2.0 ---
    "USB_FS_MBPS": 12.0,         # Mbit/s [官方] USB 2.0 全速
    "USB_HS_MBPS": 480.0,        # Mbit/s [官方] USB 2.0 高速
    "USB_RESET_RESP_S": 5e-3,    # s   [官方] USB 2.0 §7.1.7.3 设备须在总线复位结束后 5ms 内响应
    "USB_BULK_EFF": 0.8,         # -   [推算] bulk 有效效率按 80% 估
    # --- SW 侧 ---
    "FLASH_IMAGE_MB": 90,        # MB  SW/FLASH_AND_VERSION.md §4.1 分区表总量 (boot1+kern8+rootfs30+app16+model30+isp1)
    # --- SoC ADC (★ISS-291: 满量程口径按官方 datasheet 钉死, 不再按量级猜★) ---
    "ADC_BITS": 12,              # bit [官网] RK3572 datasheet L2863 "Resolution ... 12 Bit"
    "I_ADC_LEAK_MAX": 1e-6,      # A   [0数据] SoC ADC 输入漏电流上限 (量级); ★与网表 L182 note 同源 (两侧同一 1µA 假设)★
    "V_DET_FS": 1.8,             # V   ★ISS-291: SAR-ADC 满量程 = 1.8V 域 (★不是 3.3V★) [脚表 L39 SARADC_VIN5=1.8V + datasheet L2454/L2864]★
    "ADC_SETTLE_MAX_MS": 300.0,  # ms  ★判据红线 (沿用 ISS-090 原阈值 300ms, ★阈值不许调松★) 12bit 建立时间上限
    "ADC_LEAK_OFFSET_MAX_V": 0.4,# V   ★判据红线 (沿用 ISS-090 原阈值 0.4V, ★阈值不许调松★) ADC 输入漏电偏移上限
    "ADC_NODE_MAX_V": 1.98,      # V   ★SARADC_AVDD1V8 abs-max [官网] datasheet L2454 (1.62 / 1.8 / 1.98)★
    "ADC_NODE_NOM_MAX_V": 1.8,   # V   ★ADC 输入节点 ≤ 标称域 1.8V [官网] datasheet L2864 (AVSS18 ~ AVDD18)★
    "BAT_FULL_V": 4.2,           # V   ★电池满电 [实测] 网表 L24 RAIL 行 "4.2V 满 / 3.0V 截止"★
    "BAT_CUTOFF_V": 3.0,         # V   ★电池截止 [实测] 网表 L24 同上★
    # --- USB2 OTG 插入检测 (VBUS_DET_D → USB_DRD1_VBUSDET, ★数字脚, 不是 SAR-ADC★) ---
    "USB_VBUS_NOM_V": 5.0,       # V   ★USB VBUS 标称 [实测] 网表 L2 RAIL 行 "5.0V ±5%" (⇒ 4.75~5.25V)★
    "USB_VBUS_MIN_V": 4.75,      # V   ★USB VBUS 下限 [官方] USB 2.0 / Type-C VBUS 4.75~5.25 V★
    "USB_VBUS_MAX_V": 5.25,      # V   ★USB VBUS 上限 [官方] 同上★
    "USB_VBUSDET_VIH_MIN_V": 2.3,# V   ★识别高电平阈值 [官方] Forlinx FET3572 手册 "VBUSDET must be high (> 2.3 V)"★
    "USB_VBUSDET_HI_LO_V": 2.7,  # V   ★标称高电平带下沿 [官方] 手册 "A high level indicates DEVICE mode (2.7-3.3 V, typical: 3.0 V)"★
    "USB_VBUSDET_HI_HI_V": 3.3,  # V   ★标称高电平带上沿 [官方] 同上 (⇒ 降级 abs-max 上界)★
    "USB_VBUSDET_INTERNAL_PD_OHM": 40e3,  # Ω ★降级假设 [官方·仅 DRD0] 手册 "internal 40 kΩ pull-down"; ★本板是 DRD1 ⇒ 未记载 ⇒ [0数据]★
    "DET_CHAIN_STATIC_MAX_UA": 26.25,  # µA ★单条检测链常开静态电流上限 [实测] 网表 L182 note "常开静态功耗 26.25µA / 110µW (V-3 裁决的代价)"★
    # --- 热模型 (MECH/MECH_BUDGET.md §2.3) ---
    "T_SKIN_A": 35.0,            # °C  T_skin = 35.0 + 50.13 x P
    "T_SKIN_B": 50.13,           # °C/W
    "T_SKIN_REDLINE": 43.0,      # °C  ISO 13732-1 红线
    "P_REDLINE": 0.16,           # W   贴皮肤镜腿持续发热量上限 (对应 43.0°C)
    # --- 工程约定 ---
    "ISS085_MIN_GND_PINS": 2,    # pin ISS-085 (mech-lead) 跨铰链规则: 两端各留 ≥2 个 GND pin
}

# 器件常数 → 来源标注 (输出里逐条打印, 便于核对"每个数从哪来")
SOURCES = {
    "U_SUPV_VIT_REF": "[官方] TI TPS3808 datasheet: VIT = 0.405 x (1 + R1/R2)",
    "U_SUPV_DELAY_CT_OPEN": "[官方] TI TPS3808 datasheet: CT 悬空 = 20ms",
    "U_SUPV_DELAY_CT_VDD": "[官方] TI TPS3808 datasheet: CT 经电阻接 VDD = 300ms",
    "TMP117_LSB_C": "[官方] TI TMP117 datasheet: 1 LSB = 7.8125 m°C",
    "TMP117_IV_SUPPLY": "[官方] TI TMP117 datasheet: 5µA max",
    "TMP117_RESET_READ": "[官方] TI TMP117 datasheet: 复位后首读 −256°C",
    "I2C_TR_STD_MAX_NS": "[官方] I2C 标准模式上升沿上限 1.0µs",
    "I2C_TR_FAST_MAX_NS": "[官方] I2C 快模式上升沿上限 300ns",
    "I2C_TR_K": "[推算] 10%→90% 上升时间系数 ln(9)=2.1972",
    "USB_FS_MBPS": "[官方] USB 2.0 全速 12 Mbit/s",
    "USB_HS_MBPS": "[官方] USB 2.0 高速 480 Mbit/s",
    "USB_RESET_RESP_S": "[官方] USB 2.0 §7.1.7.3",
    "USB_BULK_EFF": "[推算] bulk 有效效率 80%",
    "FLASH_IMAGE_MB": "[实测] SW/FLASH_AND_VERSION.md §4.1 分区表总量",
    "ADC_BITS": "[官网] RK3572 datasheet V1.1 L2863: Resolution = 12 Bit (★ISS-291 升级: 原为 [0数据]★)",
    "I_ADC_LEAK_MAX": "[0数据] SoC ADC 漏电流按量级 1µA 估 (★与网表 L182 note 同一假设★)",
    "V_DET_FS": "[官网] SAR-ADC 满量程 = 1.8V 域: 脚表 FET3572C_PIN_TABLE.csv L39 (SARADC_VIN5 / 1.8V) + "
                "rk3572_datasheet_V1.1.txt L2454 (SARADC_AVDD1V8 = 1.62/1.8/1.98V) + L2864 (Analog Input Range = AVSS18~AVDD18) "
                "⇒ ★原 3.3V 写死值已按 ISS-291 订正★",
    "ADC_SETTLE_MAX_MS": "[沿用] ISS-090 原判据阈值 300ms (★ISS-291 只改口径, 阈值不许调松★)",
    "ADC_LEAK_OFFSET_MAX_V": "[沿用] ISS-090 原判据阈值 0.4V (★ISS-291 只改口径, 阈值不许调松★)",
    "ADC_NODE_MAX_V": "[官网] rk3572_datasheet_V1.1.txt L2454: SARADC_AVDD1V8 = 1.62 / 1.8 / 1.98 V ⇒ abs-max 1.98V",
    "ADC_NODE_NOM_MAX_V": "[官网] rk3572_datasheet_V1.1.txt L2864: Analog Input Range = AVSS18 ~ AVDD18 ⇒ ≤1.8V 标称",
    "BAT_FULL_V": "[实测] HW/netlist_v1.csv L24 (RAIL BAT 行): '4.2V 满 / 3.0V 截止'",
    "BAT_CUTOFF_V": "[实测] HW/netlist_v1.csv L24 (RAIL BAT 行): '4.2V 满 / 3.0V 截止'",
    "USB_VBUS_NOM_V": "[实测] HW/netlist_v1.csv L2 (RAIL VBUS_5V 行): '5.0V ±5%'",
    "USB_VBUS_MIN_V": "[官方] USB 2.0 / Type-C VBUS 4.75 ~ 5.25 V",
    "USB_VBUS_MAX_V": "[官方] USB 2.0 / Type-C VBUS 4.75 ~ 5.25 V",
    "USB_VBUSDET_VIH_MIN_V": "[官方] Forlinx FET3572 手册 (state/_os_snapshots/fx3572_manual.html): "
                             "'In device mode, VBUSDET must be high (> 2.3 V)'",
    "USB_VBUSDET_HI_LO_V": "[官方] Forlinx FET3572 手册: 'A high level indicates DEVICE mode (2.7-3.3 V, typical: 3.0 V)'",
    "USB_VBUSDET_HI_HI_V": "[官方] Forlinx FET3572 手册: 同上 (⇒ 降级 abs-max 上界)",
    "USB_VBUSDET_INTERNAL_PD_OHM": "[官方·降级] 手册只对 USB_DRD0_VBUSDET 明写 'internal 40 kΩ pull-down'; "
                                   "★本板用的是 USB_DRD1_VBUSDET ⇒ 手册未记载 ⇒ [0数据] ⇒ 按'存在'降级处理并登记 need★",
    "DET_CHAIN_STATIC_MAX_UA": "[实测] HW/netlist_v1.csv L182 note: '常开静态功耗 26.25µA / 110µW (V-3 裁决的代价)' "
                                "⇒ 取作单条检测链常开静态电流上限 (同板同型链已裁决值)",
    "T_SKIN_A": "[实测] MECH/MECH_BUDGET.md §2.3 热模型",
    "T_SKIN_B": "[实测] MECH/MECH_BUDGET.md §2.3 热模型",
    "T_SKIN_REDLINE": "[官方] ISO 13732-1 43°C 红线",
    "ISS085_MIN_GND_PINS": "[官方] ISS-085 (mech-lead) 跨铰链 ≥2 GND pin 规则",
}

# ----------------------------------------------------------------------------
# 0b. ISP 段判据常数 (ISS-210, 2026-11-15) —— 来源 = ISS-124 的反解 (已验证件)
# ----------------------------------------------------------------------------
# ★★口径纪律 (SOUL.md 铁律的 ISP 版, ISS-124 已钉死, 本脚本照抄) ★★:
#   ① ISP 段必须报【纯硬件耗时】与【SDK 总耗时】两个数, 不许合并成一个数;
#   ② ★12M Pixel 是【单帧分辨率上限】, 不是【每秒能力】 ⇒ 不许用它推 MP/s。
# ★★判据出处: SW/ISP_CAPABILITY_RESEARCH.md §② + SW/ISP_CAPABILITY_RESEARCH.json
#      (isp_ms_budget_60ms_line: modeA 15.095 / modeB 17.33 / 现占位 8.00 / 余量 7.095 / 9.33)
# ★★判定线取 ISS-124 的【发布值】 15.10 / 17.33 ms (逐字引用, 不许调松);
#      精确反解值 (同一次反解的未舍入结果) 一并给出: 15.095 ms ⇒ 与发布值差 0.005 ms
#      ⇒ 远小于板端 0.01 ms 级分辨率 ⇒ 不改变任何结论。
ISP_BUDGET = {
    "budget_ms": 60.0,          # ms  老板锁死的端到端硬指标 (不许调松)
    "T_FIXED_ms": 34.00,        # ms  HW/e2e_budget_rk3572.py T_FIXED (五段拆分之和)
    "S3_now_ms": 8.00,          # ms  现行 ISP 段占位 (SW/SW_REQUIREMENTS.md §10.1)
    "POST_MS": 5.6,             # ms  HW/e2e_budget_rk3572.py POST_MS
    "FRAME_MS": 16.67,          # ms  60fps 帧周期
    "S5_ms": 13.305,            # ms  RK3572 + yolov5n@640 纯 NPU [推算] = 8.87*(6/4)
    "min_frames": 300,          # 帧 SW/DEMO_OD_TIMING_SPEC.md §3.1 (n<300 不作结论)
    "limit_mode_a_ms": 15.10,   # ms  ★模式A 生死线 (ISS-124 发布值, 逐字引用, 不许改)
    "limit_mode_b_ms": 17.33,   # ms  ★模式B 上限 (ISS-124 发布值; 前提 age=1)
    "npu_t2_flip_ms": 20.33,    # ms  老板 10-29 T2 翻案条款 (ISS-129): 纯 NPU > 20.33 ⇒ 60ms 不保
}

ISP_BUDGET_SOURCES = {
    "budget_ms": "[锁死项] 老板锁死的端到端 60ms 硬指标 (SW/RKNN_BENCH.md §5.1 / SW/DEMO_OD_TIMING_SPEC.md §3.3.1)",
    "T_FIXED_ms": "[推算] HW/e2e_budget_rk3572.py T_FIXED = 34.00 (五段拆分恒等还原)",
    "S3_now_ms": "[推算·无官方背书] 现行 ISP 段占位 8.00 ms (SW/SW_REQUIREMENTS.md §10.1; ISS-124 D1/D2)",
    "POST_MS": "[推算] HW/e2e_budget_rk3572.py POST_MS = 5.6",
    "FRAME_MS": "[实测口径] 60fps 帧周期 16.67 ms",
    "S5_ms": "[推算] RK3576 8.87 ms × (6 TOPS / 4 TOPS) = 13.305 ms (RKNN_BENCH.md §4.3)",
    "limit_mode_a_ms": "[推算] ISS-124 反解, 发布值 15.10 ms (SW/ISP_CAPABILITY_RESEARCH.md §②; json 精确值 15.095)",
    "limit_mode_b_ms": "[推算] ISS-124 反解, 发布值 17.33 ms (前提 age=1; json 精确值 17.33)",
    "npu_t2_flip_ms": "[锁死项] 老板 2026-10-29 T2 翻案条款 (ISS-129)",
}

# 判定用的容差
TOL = 1e-9

# 默认网表路径 (相对本文件: SW/tools/ → ../../HW/netlist_v1.csv)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_HERE))     # projects/smart_glasses
DEFAULT_NETLIST = os.path.normpath(os.path.join(_HERE, "..", "..", "HW", "netlist_v1.csv"))

# ★★【ISS-225】SW 侧 md5 基线台账 (★锚点住这儿, 不再硬编码 md5★)
#   ★ 机制照抄 MECH/check_demo_struct_truth.py 的 C21 (★只读参照, MECH/ 一个字节没碰★)
#   ★ 锚点 = SW/SW_MD5_BASELINE_LEDGER.md §1 的机器可读 YAML 块
#   ★ 本文件**只读**该台账 + 落表台账 (落表台账由 hw-lead 写) ⇒ SW 侧一个字节都不写
SW_MD5_LEDGER_REL = os.path.join("SW", "SW_MD5_BASELINE_LEDGER.md")
SW_MD5_ANCHOR_BEGIN = "# BEGIN SW_MD5_ANCHORS"
SW_MD5_ANCHOR_END = "# END SW_MD5_ANCHORS"
NETLIST_REL = os.path.join("HW", "netlist_v1.csv")


def _sw_anchor_entries():
    """读 SW 台账 §1 里 `HW/netlist_v1.csv` 的那条锚点 (读不到 ⇒ (None, 原因))。"""
    path = os.path.join(_PROJECT_ROOT, SW_MD5_LEDGER_REL)
    if not os.path.exists(path):
        return None, "SW 侧 md5 基线台账不存在: %s" % SW_MD5_LEDGER_REL
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.search(re.escape(SW_MD5_ANCHOR_BEGIN) + r"(.*?)" + re.escape(SW_MD5_ANCHOR_END),
                  text, re.S)
    if not m:
        return None, "台账里找不到锚点块"
    try:
        import yaml
        data = yaml.safe_load(m.group(1))
    except Exception as exc:                      # ★fail-closed: 读不到 ⇒ 红, 不许当"没锚点就跳过"★
        return None, "锚点块解析失败: %s" % exc
    anchors = (data or {}).get("anchors") or {}
    for e in (anchors.get("source_ledger") or {}).get("entries") or []:
        if str(e.get("file") or "") == NETLIST_REL:
            return (anchors, e), ""
    return None, "锚点里没有 %s 的条目" % NETLIST_REL


def _md5_seen(text: str, value: str) -> bool:
    return bool(value) and (value in text or value[:12] in text)


# ★★【ISS-285 · 2026-11-17 · sw-lead】★★ 网表锚点判据的【判决源同源化】
#   ★★【根因】同一个事实 («网表当前合法 md5 是多少») 原有两个判决源 ⇒ 授权落表后一个绿一个红:
#     ① `SW/tools/check_demo_panel_spec.py` 的 R6 ⇒ 判决源 = 落表台账【链头】 ⇒ 绿 ✅
#     ② 本文件的网表锚点判据 ⇒ 判决源 = SW 台账 §1 锚点块里【冻结的 md5】 ⇒ 红 ❌
#   ★★【修法落在「让两个判据源同源」, 不落在「放宽判据」★★
#   ★★【四条不许破】★★
#     ① 判据方向不许变: 盘上真源 md5 ∉ 台账登记的合法状态集合 ⇒ 仍必须红 (这一条逐字保留)
#     ② 不许把「取不准」放宽成「取最近一条」⇒ fail-closed 三条 (链头不唯一 / 链断 / 链头无单号) 一条都不许动
#     ③ 不许把落表台账当「锚点可写集合」⇒ 落表台账 append-only + 链完整性防线不许松
#     ④ 不许弱化 ISS-275 已跑通的那条链头逻辑 ⇒ 链头实现**直接 import R6 那份**
#        (★同域 SW/tools, 不 import MECH —— 那是别人地界★) ⇒ 链头 / 链 / 产出单号 逐字一致,
#        且 `check_demo_panel_spec.py` 一个字节没被本单碰过 ⇒ 第 ④ 条自动成立

def _dps():
    """→ (R6 那个文件的模块, 错误原因)。读不到 ⇒ (None, 原因) ⇒ 判红 (fail-closed)。"""
    global _DPS
    if _DPS is None:
        import importlib.util
        p = os.path.join(_HERE, "check_demo_panel_spec.py")
        try:
            spec = importlib.util.spec_from_file_location("_sw_dps_iss285", p)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _DPS = mod
        except Exception as exc:                  # ★fail-closed: 读不到判决源实现 ⇒ 红, 不许降级★
            return None, "读不到 R6 判决源实现 %s: %s" % (p, exc)
    return _DPS, ""


_DPS = None


def _device_dnp_rows(nl, ref: str) -> list:
    """该位号的【器件本体行】(type ∉ {NET, TP}) 上的 dnp 列表。

    ★为什么要单独一个读法: `Netlist.dnp_of()` 取的是【该位号第一条行】的 dnp
      ⇒ 同一个位号有多行时可能拿错行 (ISS-190 的老教训) ⇒ 判据要判【器件本体行】。
    ★空列表 = 该位号在网表里没有器件本体行 ⇒ 判据不许当「装上了」 (fail-closed)。
    """
    return [x.get("dnp", "") for x in nl.rows_of(ref) if x.get("type") not in ("NET", "TP")]


def _netlist_baseline_state():
    """→ (状态串, 允许的网表 md5 集合, 详情)。三方对账: 锚点 ↔ 落表台账 ↔ 盘上真源。

    ★★【ISS-285】判决源 = 【落表台账链头】, 与 `check_demo_panel_spec.py` 的 R6 **同源** ★★
      ① 盘上真源的 md5 必须 == 台账链头 (★判据方向不许变★)
      ② 链头取不准 (不唯一 / 链断 / 有记录不在链上 / 链头没单号) ⇒ 一律判红 (★fail-closed 三条一条没动★)
      ③ 域侧锚点副本降级为【历史留痕】: 允许停在历史值, 但不许胡说
         (md5 必须在台账链上 + 落表单号必须与台账产出该 md5 的单号对得上 + 旧 md5 也必须在链上)
    """
    got = _sw_anchor_entries()
    if not isinstance(got, tuple) or got[0] is None:
        why = got[1] if isinstance(got, tuple) else "未知"
        return ("BAD", set(), "读不到 SW 台账锚点: %s" % why)
    (anchors, entry), _ = got
    want = str(entry.get("md5") or "")
    prev = str(entry.get("prev_md5") or "")
    by = str(entry.get("by") or "")
    if not want:
        return ("BAD", set(), "锚点里 %s 没登记 md5" % NETLIST_REL)
    # ★★【ISS-285】判决源 = 落表台账【链头】(★与 R6 同一份实现 ⇒ 真同源★) ★★
    dps, err = _dps()
    if dps is None:
        return ("BAD", set(), err)
    led_text, led_spec = dps.sw_ledger_canonical_text(_PROJECT_ROOT, anchors)
    if not led_text:
        return ("BAD", set(), "判决源落表台账读不到 ⇒ 无从对账 (fail-closed)")
    st = dps.sw_ledger_state(NETLIST_REL, led_text)
    recs = st.get("records") or []
    head = st.get("head")
    known = set(st.get("known") or set())
    if not recs:
        return ("BAD", set(), "落表台账 (%s) 里查不到 %s 的任何落表记录" % (led_spec, NETLIST_REL))
    if not head:
        return ("BAD", set(), "落表台账最新记录取不准 (%s) ⇒ 取错记录可能假绿 ⇒ 判红"
                % (st.get("why")))
    if not st.get("head_iss"):
        return ("BAD", known, "落表台账最新记录 (%s) 缺落表单号 (字段缺失) ⇒ 判红" % head)
    if not st.get("chain"):
        return ("BAD", known, "落表台账链断了 / 不唯一 (%s)" % (st.get("why")))
    orphan = sorted({r["new"] for r in recs} - set(st.get("chain") or []))
    if orphan:
        return ("BAD", known, "落表台账里有记录不在链上 = %s" % orphan)
    # ★★【域侧锚点副本 = 历史留痕】允许停在历史值, 但不许胡说 ★★
    am = want[:12]
    if am not in known:
        return ("BAD", known, "锚点副本 md5 %s 台账链里查不到 (锚点胡说?)" % (am or "(空)"))
    if by and by not in (st.get("producer") or {}).get(am, set()):
        return ("BAD", known, "锚点副本落表单号 %s 与台账对不上 (台账产出该 md5 的单号 = %s)"
                % (by or "(空)", sorted((st.get("producer") or {}).get(am, []))))
    if prev and prev[:12] not in known:
        return ("BAD", known, "锚点副本旧 md5 %s 台账链里查不到 (历史留痕断了?)" % prev[:12])
    # ★★【判据方向不许变】盘上真源 vs 台账链头 ★★
    disk = os.path.join(_PROJECT_ROOT, NETLIST_REL)
    got_md5 = hashlib.md5(open(disk, "rb").read()).hexdigest() if os.path.exists(disk) else ""
    if got_md5[:12] != head:
        return ("BAD", known, "盘上真源 md5 %s ≠ 台账链头 %s (真源被换了或台账没更新)"
                % (got_md5[:12], head))
    return ("OK", known, "判决源 = %s 链头 %s (单号 %s) · 盘上 md5 = %s"
            % (led_spec, head, ",".join(st.get("head_iss") or []), got_md5))


def netlist_baseline_ok() -> bool:
    """三方对账成立? (锚点 ↔ 落表台账 ↔ 盘上真源)"""
    return _netlist_baseline_state()[0] == "OK"


def netlist_md5_allowed(md5: str) -> bool:
    """这个网表 md5 是落表台账登记过的状态之一吗 (落表前 / 落表后)?

    ★★【ISS-285】落表台账里登记的 md5 是【12 位前缀】(★R6 也是按 12 位比★
      ⇒ 这里也按 12 位前缀比, 口径与判决源 (R6) 完全一致
      (★不然拿 32 位去比 12 位前缀 ⇒ 这条恒红 = 判据自毁★)。
    ★**判据方向一个字没变**: 盘上 md5 ∉ 台账登记的状态集合 ⇒ 仍必须红。★
    """
    if not md5:
        return False
    allowed = _netlist_baseline_state()[1]
    return str(md5).strip().lower()[:12] in {str(x).strip().lower()[:12] for x in allowed}


def netlist_baseline_detail() -> str:
    return _netlist_baseline_state()[2]


def r(x: float, n: int = 3) -> float:
    return round(x + 0.0, n)


# ----------------------------------------------------------------------------
# 0c. ISP 段判据 (ISS-210) —— 把 ISS-124 的反解变成可执行判据
# ----------------------------------------------------------------------------
def _pct(vals, q):
    """线性插值分位数 (q ∈ [0,100]); 空表 ⇒ None。"""
    if not vals:
        return None
    s = sorted(float(v) for v in vals)
    if len(s) == 1:
        return s[0]
    pos = (len(s) - 1) * (q / 100.0)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return s[lo]
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def read_isp_csv(path: str) -> dict:
    """读板端 ISP 段 CSV (格式见 SW/DEMO_OD_TIMING_SPEC.md §3.4) ⇒ 判据输入。

    ★需要的列: ts_isp_in / ts_isp_hw_start / ts_isp_out (都是 CLOCK_MONOTONIC 域的 ms)
    ★派生: t_isp_total = ts_isp_out − ts_isp_in (判据用) · t_isp_hw = ts_isp_out − ts_isp_hw_start (归因用)
    ★缺 ts_isp_hw_start 的行 ⇒ 该行的纯硬件数不计入 (报 [0数据]), 不拿 total 顶替。
    """
    totals: list[float] = []
    hws: list[float] = []
    skipped = 0
    with open(path, newline="", encoding="utf-8", errors="ignore") as fh:
        rd = csv.DictReader(fh)
        for row in rd:
            def g(name):
                v = (row.get(name) or "").strip()
                if v == "":
                    return None
                try:
                    return float(v)
                except ValueError:
                    return None
            t_in, t_hw, t_out = g("ts_isp_in"), g("ts_isp_hw_start"), g("ts_isp_out")
            if t_in is None or t_out is None:
                skipped += 1
                continue
            totals.append(t_out - t_in)
            if t_hw is not None:
                hws.append(t_out - t_hw)
    return {
        "avg_total_ms": (sum(totals) / len(totals)) if totals else None,
        "avg_hw_ms": (sum(hws) / len(hws)) if hws else None,
        "p95_total_ms": _pct(totals, 95),
        "n": len(totals),
        "source": path,
        "_skipped_rows": skipped,
    }


def isp_budget_verdict(meas=None) -> dict:
    """★ISS-210: ISP 段判据 —— 从实测输入算出 PASS/FAIL + 数值 + 差多少。

    ★被判定的是【t_isp_total】(管线可见 / SDK 总耗时口径): 它才是占用 60ms 预算的那个数;
      【t_isp_hw】(纯硬件耗时) 必须**另外单独报**, 只用于归因 (谁慢: ISP 硬件 vs 驱动/用户态)
      ⇒ ★两个数不许合并成一个数 (ISS-124 已钉死)★。
    ★无实测输入 ⇒ verdict = INDET + [0数据] (不许假装测过)。

    meas 支持的键:
      avg_total_ms : 管线可见 ISP 段平均值 (★判据用它★)
      avg_hw_ms    : 纯硬件耗时平均值 (归因用)
      p95_total_ms : 管线可见 ISP 段 p95 (模式B 上限 17.33 ms)
      n            : 采样帧数 (<300 ⇒ 不作结论)
      npu_ms       : 纯 NPU 耗时 (可选; 交叉核对 T2 翻案条款 20.33 ms)
      source       : 来源说明 (板端 CSV 路径等)
    """
    m = dict(meas or {})
    B = ISP_BUDGET
    fixed_other = B["T_FIXED_ms"] - B["S3_now_ms"]            # 26.00
    t_od = B["S5_ms"] + B["POST_MS"]                         # 18.905
    limit_a_exact = B["budget_ms"] - fixed_other - t_od       # 15.095 (精确反解)
    limit_a = B["limit_mode_a_ms"]                            # 15.10 (ISS-124 发布值)
    limit_b = B["limit_mode_b_ms"]                            # 17.33
    headroom_exact = limit_a_exact - B["S3_now_ms"]           # 7.095 (精确)

    avg_total = m.get("avg_total_ms")
    avg_hw = m.get("avg_hw_ms")
    p95_total = m.get("p95_total_ms")
    n = m.get("n")
    npu = m.get("npu_ms")

    out = {
        "judged_number": "t_isp_total (管线可见 / SDK 总耗时口径)",
        "criteria": {
            "limit_mode_a_ms": limit_a,
            "limit_mode_a_exact_ms": limit_a_exact,
            "limit_mode_b_p95_ms": limit_b,
            "isp_now_ms": B["S3_now_ms"],
            "headroom_now_mode_a_ms": headroom_exact,
            "headroom_now_mode_a_doc": "7.09",
            "headroom_now_mode_b_ms": limit_b - B["S3_now_ms"],
            "headroom_now_mode_b_doc": "9.33",
            "published_numbers": "ISP 上限: 模式A 15.10 ms / 模式B 17.33 ms; 现占位 8.00 ms 的余量 +7.09 / +9.33 ms",
            "budget_ms": B["budget_ms"],
            "T_FIXED_ms": B["T_FIXED_ms"],
            "T_FIXED_minus_S3_ms": fixed_other,
            "T_od_ms": t_od,
            "age_baseline": 2,
            "min_frames": B["min_frames"],
        },
        "measurement": {
            "avg_total_ms": avg_total,
            "avg_hw_ms": avg_hw,
            "p95_total_ms": p95_total,
            "n": n,
            "npu_ms": npu,
            "source": m.get("source"),
        },
        "sources": dict(ISP_BUDGET_SOURCES),
    }

    # ── 没有实测输入 ⇒ INDET (板不在本机 ⇒ 板端结论一律 [0数据]) ──
    if avg_total is None:
        out.update({
            "verdict": "INDET",
            "verdict_latency": "INDET",
            "reason": "板端 ISP 段未实测 (本机无可达板) ⇒ 板端结论一律 [0数据] ⇒ 不作判定",
            "evidence": "[0数据]",
            "margin_ms": None,
            "e2e_modeA_ms": None,
            "e2e_modeB_ms": None,
            "mode_b_note": "模式B 前提 age=1 (T_od <= 16.67); 现行 yolov5n@640 的 age=2 ⇒ 模式B 本来就不成立, 与 ISP 无关",
        })
        return out

    # ── 延迟线判定 ──
    margin = r(limit_a - avg_total, 3)
    margin_exact = r(limit_a_exact - avg_total, 3)
    latency = "PASS" if avg_total <= limit_a else "FAIL"
    report_complete = avg_hw is not None
    enough_frames = (n is None) or (n >= B["min_frames"])
    reasons = []
    if not report_complete:
        reasons.append("缺【纯硬件耗时 t_isp_hw】⇒ 违反 §3.1『两个数同口径』纪律 (不许合并成一个数)")
    if n is not None and n < B["min_frames"]:
        reasons.append("采样帧数 n=%s < %d ⇒ 不作结论 (§3.1)" % (n, B["min_frames"]))

    if latency == "FAIL":
        overall = "FAIL"
        reasons.insert(0, "ISP 段 avg %.3f ms > 15.10 ms 生死线 ⇒ 模式A 破线 (超 %.3f ms)"
                       % (avg_total, -margin))
    elif not report_complete or not enough_frames:
        overall = "INDET"
    else:
        overall = "PASS"

    # ★把实测 ISP 段代回 60ms 账本 (模式A / 模式B)
    e2e_a = r(fixed_other + avg_total + t_od, 3)
    e2e_b = r(fixed_other + avg_total + 2 * B["FRAME_MS"], 3)   # age=2 (现行锁定基线)

    out.update({
        "verdict": overall,
        "verdict_latency": latency,
        "margin_ms": margin,
        "margin_ms_exact_line": margin_exact,
        "margin_note": ("正数 = 距 15.10 ms 生死线 (ISS-124 发布线) 还差多少 ms; 负数 = 超了多少 ms;"
                        " margin_ms_exact_line = 对精确反解线 15.095 ms 的差值 (两者差 0.005 ms, 不改变结论)"),
        "e2e_modeA_ms": e2e_a,
        "e2e_modeA_verdict": "PASS" if e2e_a <= B["budget_ms"] else "FAIL",
        "e2e_modeB_ms": e2e_b,
        "e2e_modeB_verdict": "PASS" if e2e_b <= B["budget_ms"] else "FAIL",
        "mode_b_note": "模式B 前提 age=1 (T_od <= 16.67); 现行 yolov5n@640 的 age=2 ⇒ 模式B 本来就不成立, 与 ISP 无关",
        "slowdown_vs_now": (r(avg_total / B["S3_now_ms"], 3) if B["S3_now_ms"] else None),
        "slowdown_vs_now_note": "ISP 最多能慢到现占位 8.00 ms 的几倍才破 60ms 硬线 (ISS-124 的 1.89x / 2.17x)",
        "report_complete": report_complete,
        "frames_enough": enough_frames,
        "p95_mode_b_verdict": ("PASS" if p95_total is not None and p95_total <= limit_b
                                else ("FAIL" if p95_total is not None else "INDET")),
        "reason": ("; ".join(reasons) if reasons else
                   "ISP 段两个数都报、样本足够 (n=%s)、模式A 生死线内 (余量 %.3f ms)"
                   % (n, margin)),
        "evidence": "[实测] (板端跑出来的)" if m.get("source") else "[实测] (未注明来源)",
    })
    if avg_total > limit_a_exact and avg_total <= limit_a:
        out["warning"] = ("测值 %.3f ms 距精确反解线 %.3f ms 只差 %.3f ms ⇒ 建议复测一轮 (板端分辨率 0.01 ms 级)"
                          % (avg_total, limit_a_exact, limit_a - avg_total))
    if npu is not None:
        out["t2_flip_check"] = {
            "npu_ms": npu,
            "threshold_ms": B["npu_t2_flip_ms"],
            "verdict": "FAIL(命中 T2 翻案条款: 纯 NPU > 20.33ms ⇒ 60ms 不可保)" if npu > B["npu_t2_flip_ms"] else "PASS",
        }
    return out


# ----------------------------------------------------------------------------
# 1. 网表读取层 —— ★本版的核心: 所有网表相关数字都从这里来★
# ----------------------------------------------------------------------------
# 网表 value 字段的形态: '10k ±1%' / '100nF ±10%' / '0Ω 跳线位' / '90Ω ±10% (…)' / '[待选型] (0Ω 跳线位)'
_OHM_PREFIX_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(k|M|m)\b")          # '10k ±1%' / '1M ±1%'
_OHM_UNIT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:Ω|ohm)", re.I)   # '0Ω' / '90Ω ±10%'
_FAR_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(n|p|u|µ|m)?\s*F\b")      # '100nF ±10%' / '10µF ±20%'
_VOLT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*V\b")
_TAU_RE = re.compile(r"τ\s*=\s*(\d+(?:\.\d+)?)\s*(ms|s|µs|us)")
_TR_RE = re.compile(r"t_r\s*=\s*(\d+(?:\.\d+)?)\s*(ns|µs|us|ms|s)")


def parse_ohm(text: str):
    """'2.2k ±1%' → 2200.0 ; '0Ω 跳线位' → 0.0 ; '[待选型] (0Ω 跳线位)' → 0.0 ; 解析不出 → None"""
    if not text:
        return None
    m = _OHM_PREFIX_RE.search(text)
    if m:
        mul = {"k": 1e3, "m": 1e6, "M": 1e6}[m.group(2)]
        return float(m.group(1)) * mul
    m = _OHM_UNIT_RE.search(text)
    if m:
        return float(m.group(1))
    return None


def parse_farad(text: str):
    """'100nF ±10%' → 1e-7 ; '10µF ±20%' → 1e-5"""
    if not text:
        return None
    m = _FAR_RE.search(text)
    if not m:
        return None
    mul = {"n": 1e-9, "p": 1e-12, "u": 1e-6, "µ": 1e-6, "m": 1e-3, None: 1.0}[
        m.group(2).lower() if m.group(2) else None
    ]
    return float(m.group(1)) * mul


def parse_volt(text: str):
    """'1.8V ±5%' → 1.8"""
    if not text:
        return None
    m = _VOLT_RE.search(text)
    return float(m.group(1)) if m else None


def parse_tau_ms(text: str):
    """'τ=100ms' → 100.0 (ms) ; 解析不出 → None"""
    if not text:
        return None
    m = _TAU_RE.search(text)
    if not m:
        return None
    v = float(m.group(1))
    unit = m.group(2).lower()
    if unit == "ms":
        return v
    if unit == "s":
        return v * 1e3
    if unit in ("µs", "us"):
        return v * 1e-3
    return None


def parse_tr_ns(text: str):
    """'t_r=2.38µs@100pF' → 2380.0 (ns)"""
    if not text:
        return None
    m = _TR_RE.search(text)
    if not m:
        return None
    v = float(m.group(1))
    unit = m.group(2).lower()
    return {"ns": v, "µs": v * 1e3, "us": v * 1e3, "ms": v * 1e6, "s": v * 1e9}[unit]


def _split_csv_line(line: str):
    """引号感知的 CSV 行切分 → (fields, quoted_flags); 保留原引号形态, 便于原地改一个字段。"""
    fields, quoted, cur, inq, q, i, n = [], [], [], False, False, 0, len(line)
    while i < n:
        ch = line[i]
        if inq:
            if ch == '"':
                if i + 1 < n and line[i + 1] == '"':
                    cur.append('""')
                    i += 2
                    continue
                inq = False
                i += 1
                continue
            cur.append(ch)
            i += 1
            continue
        if ch == '"':
            inq = True
            q = True
            i += 1
            continue
        if ch == ",":
            fields.append("".join(cur))
            quoted.append(q)
            cur, q = [], False
            i += 1
            continue
        cur.append(ch)
        i += 1
    fields.append("".join(cur))
    quoted.append(q)
    return fields, quoted


def _join_csv_line(fields, quoted) -> str:
    out = []
    for f, q in zip(fields, quoted):
        out.append('"%s"' % f.replace('""', '"') if q else f)
    return ",".join(out)


class Netlist:
    """`HW/netlist_v1.csv` 的只读封装 + 锚点指纹。"""

    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        with open(self.path, "rb") as fh:
            raw = fh.read()
        self.md5 = hashlib.md5(raw).hexdigest()
        self.bytes = len(raw)
        self.mtime = os.path.getmtime(self.path)
        with open(self.path, "r", encoding="utf-8-sig", newline="") as fh:
            self._raw = fh.read()
        self.lines = self._raw.split("\n")
        if self.lines and self.lines[-1] == "":
            self.lines.pop()
        self.lines_total = len(self.lines)
        # 表头 = 第一行; 数据行 = 其余
        self.header = _split_csv_line(self.lines[0].rstrip("\r"))[0] if self.lines else []
        self.rows = []
        for ln in self.lines[1:]:
            if not ln.strip():
                continue
            fields, _q = _split_csv_line(ln.rstrip("\r"))
            if not fields:
                continue
            row = {}
            for i, name in enumerate(self.header):
                row[name] = fields[i] if i < len(fields) else ""
            row["_line_no"] = len(self.rows) + 2      # CSV 物理行号 (1=表头)
            self.rows.append(row)
        self.data_rows = len(self.rows)
        self._by_ref = {}
        for row in self.rows:
            self._by_ref.setdefault(row.get("ref", ""), []).append(row)
        # ★★★【ISS-321 · SW 侧 · S1 位号改名适配】★★★
        # ★建【逻辑位号 → 盘上真实位号】的别名表 (★原名优先★)
        # ★规则: 盘上是 `<X>_1` 而 `<X>` 自己不在网表里 ⇒ `<X>` 就是它的逻辑名★
        self._ref_alias = {}
        for _r in self._by_ref:
            if _r.endswith("_1") and len(_r) > 2:
                _base = _r[:-2]
                if _base and _base not in self._by_ref:
                    self._ref_alias.setdefault(_base, _r)
        # ★反向表 (盘上真实名 → 逻辑名) ⇒ 输出层归一化 ★
        self._ref_alias_rev = {v: k for k, v in self._ref_alias.items()}

    # ---- 基本查询 ----
    def actual_ref(self, ref: str) -> str:
        """★逻辑位号 → 盘上真实位号 (★ISS-321 · S1 位号改名适配★)

        ★原名优先; 盘上只有 `<X>_1` 而 `<X>` 自己不在网表里 ⇒ 返回 `<X>_1`★
        ★**不是把判据改软**: 查不到就返回原名 ⇒ 调用方拿到的仍是空/None★
        """
        if ref in self._by_ref:
            return ref
        return self._ref_alias.get(ref, ref)

    def logical_ref(self, ref: str) -> str:
        """★盘上真实位号 → 逻辑位号 (★ISS-321 · S1 位号改名适配★)

        ★用于【输出层归一化】: 判据报出来的位号名保持逻辑名 (★Q_ENVC 而不是 Q_ENVC_1★)
        ★⇒ 判据输出格式一条没变 ⇒ 断言与文档不用跟着改★
        """
        return self._ref_alias_rev.get(ref, ref)

    def rows_of(self, ref: str):
        # ★★★【ISS-321 · S1 位号改名适配】★★★ ★走 actual_ref ★
        return list(self._by_ref.get(self.actual_ref(ref), []))

    def has_ref(self, ref: str) -> bool:
        """该位号在网表里出现过 (哪怕只有引脚行、没有器件行)。"""
        # ★★★【ISS-321 · S1 位号改名适配】★★★ ★走 actual_ref ★
        return self.actual_ref(ref) in self._by_ref

    def ic_rows(self, ref: str):
        return [x for x in self.rows_of(ref) if x.get("type") in ("IC", "SW")]

    def populated(self, ref: str) -> bool:
        """该器件是否**装机** (IC/SW 行里出现 dnp=必装)。"""
        for x in self.ic_rows(ref):
            if x.get("dnp") == "必装":
                return True
        return False

    def dnp_of(self, ref: str):
        """器件/元件的 dnp 标记 (优先 IC/SW 行, 否则取该位号的第一行)。

        ⚠️ **★别拿它回答"这个器件装不装"★** —— 本表 dnp 是**行级** (每个连接一行),
        同一位号在不同行上 dnp 可以不同 (例: `Q_ENVC` 在 `PG_AND` 那行 = DNP,
        在 `GND` / `EN_VCORE` 那两行 = 必装) ⇒ ★**要按网取就用 `dnp_of_row(ref, net)`**。
        """
        for x in self.ic_rows(ref):
            return x.get("dnp", "")
        for x in self.rows_of(ref):
            return x.get("dnp", "")
        return ""

    # ---- ★按【网】取行级 dnp (★ISS-190 订正的根因修在这里★) ----
    def rows_on_net(self, net: str):
        """某条网上的全部行 (按 net 列精确匹配)。"""
        return [x for x in self.rows if (x.get("net") or "") == net]

    @staticmethod
    def _node_is_ref(node: str, ref: str) -> bool:
        """节点列是不是指向某位号的引脚 (例: 'U_DCDC_VIO pin4' / 'Q_AND')。"""
        n = (node or "").strip()
        if not n or not ref:
            return False
        if n == ref:
            return True
        return n.startswith(ref + " pin") or n.startswith(ref + ".") or n.startswith(ref + ",")

    def dnp_of_row(self, ref: str, net: str):
        """★按【指定网】取该位号在那一行上的 dnp。

        ★**为什么必须有这个函数 (★ISS-190 打回的根因★)**: 本网的 dnp 是**行级**
        (每个连接一行) ⇒ 同一位号在不同行上 dnp 可以不同:
          · `Q_ENVC`: `PG_AND` 那行 = **DNP**, 而 `GND` / `EN_VCORE` 两行 = 必装
          · `U_DCDC_VCORE`: `PG_AND` 上的连接行 = 必装, 而它自己的 IC 器件行 (V_CORE 轨) = DNP
        ⇒ ★**`dnp_of(ref)` (取该位号第一条 IC/SW 行) 会拿错行** ⇒ 不能用它回答
          "它在这个网上装不装" ⇒ ⇒ **`pg_source_devices` 必须改用本函数 (按 PG_AND 取)**。

        ★候选行 = net 匹配 且 (该行位号就是 ref ∨ 该行 node1/node2 指向 ref 的引脚)
        ★多候选时按【行主体】取优先级 (确定性, 与行号先后无关):
          0 = 行主体就是 ref 本身 · 1 = 虚拟网络行 (type=NET) · 2 = 测试点行 (type=TP)
          · 3 = 其它器件的行 (此时 dnp 是**那个器件**的装机状态, 不是 ref 的)
        """
        cands = []
        # ★ISS-321 · S1 位号改名适配: 候选行匹配用【盘上真实名】★
        _aref = self.actual_ref(ref)
        for x in self.rows:
            if (x.get("net") or "") != net:
                continue
            if (x.get("ref") == _aref
                    or self._node_is_ref(x.get("node1", ""), _aref)
                    or self._node_is_ref(x.get("node2", ""), _aref)):
                cands.append(x)
        if not cands:
            return ""

        def prio(x):
            if x.get("ref") == _aref:
                return 0
            t = (x.get("type") or "").upper()
            if t == "NET":
                return 1
            if t == "TP":
                return 2
            return 3

        cands.sort(key=lambda x: (prio(x), x.get("_line_no", 0)))
        return cands[0].get("dnp", "")

    def row_states_on_net(self, net: str):
        """某条网上每一行的 (ref, type, dnp, 行号) —— 用于逐行核对装机状态。"""
        # ★ISS-321 · S1 位号改名适配: ref 名归一化回逻辑名★
        return [{"ref": self.logical_ref(x.get("ref", "")), "type": x.get("type", ""),
                 "dnp": x.get("dnp", ""), "line_no": x.get("_line_no")}
                for x in self.rows_on_net(net)]

    def comp_value(self, ref: str):
        """器件行 (R/C/L) 的 value 字符串。"""
        for x in self.rows_of(ref):
            if x.get("type") in ("R", "C", "L"):
                return x.get("value", "")
        return ""

    def ohm(self, ref: str):
        return parse_ohm(self.comp_value(ref))

    def farad(self, ref: str):
        return parse_farad(self.comp_value(ref))

    def rail_of(self, ref: str):
        """电阻/电容行挂在哪条 RAIL 轨上 (取 node2/node1 里以 RAIL_ 开头的那个)。"""
        for x in self.rows_of(ref):
            for k in ("node2", "node1", "net"):
                v = x.get(k, "")
                if v.startswith("RAIL_"):
                    return v
        return ""

    def rail_volts(self, rail: str):
        """RAIL 轨的标称电压 (从 RAIL 行的 value 里读, 如 '1.8V ±5%')。

        ★注意: 网表里 RAIL 行的 `net` 列写的是 'VDD_1V8_IO', 而节点列写的是
        'RAIL_VDD_1V8_IO' ⇒ 两边都要认。
        """
        for x in self.rows:
            if x.get("type") != "RAIL":
                continue
            if rail in (x.get("net", ""), x.get("node1", ""), x.get("node2", "")):
                v = parse_volt(x.get("value", ""))
                if v is not None:
                    return v
        return None

    def net_note(self, net: str):
        for x in self.rows:
            if x.get("net") == net:
                return x.get("note", "") or ""
        return ""

    def net_rows(self, net: str):
        return [x for x in self.rows if x.get("net") == net]

    # ---- 指纹 ----
    def anchor(self) -> dict:
        return {
            "netlist_path": os.path.relpath(self.path, _PROJECT_ROOT),
            "netlist_md5": self.md5,
            "netlist_lines_total": self.lines_total,
            "netlist_data_rows": self.data_rows,
            "netlist_bytes": self.bytes,
            "netlist_mtime": __import__("time").strftime("%Y-%m-%d %H:%M:%S",
                                                        __import__("time").localtime(self.mtime)),
            "netlist_header": ",".join(self.header),
        }


def mutated_copy(nl: Netlist, dest: str, edits) -> str:
    """把网表**副本**改坏: edits = [(ref, new_value), ...] 或 [(ref, new_value, "drop"), ...]。

    ★只改指定器件行的 `value` 字段 (逐行引号感知切分, 其余字节原样保留, 含 CRLF 行尾)。
    ★**绝不写原网表** —— dest 必须是临时目录里的路径。
    """
    edits = list(edits)
    by_ref = {}
    for ref, val, mode in [(e[0], e[1], (e[2] if len(e) > 2 else "set")) for e in edits]:
        # ★ISS-321 · S1 位号改名适配: edits 里的旧名 → 盘上真实名★
        by_ref.setdefault(nl.actual_ref(ref), []).append((val, mode))
    out_lines = []
    for idx, ln in enumerate(nl.lines):
        if idx == 0 or not ln.strip():
            out_lines.append(ln)
            continue
        body, term = (ln.rstrip("\r"), "\r") if ln.endswith("\r") else (ln, "")
        fields, quoted = _split_csv_line(body)
        ref = fields[4] if len(fields) > 4 else ""
        if ref in by_ref and len(fields) > 5:
            for val, mode in by_ref[ref]:
                if mode == "drop":
                    continue
                fields[5] = val
            out_lines.append(_join_csv_line(fields, quoted) + term)
            continue
        out_lines.append(ln)
    with open(dest, "w", encoding="utf-8-sig", newline="") as fh:
        fh.write("\n".join(out_lines))
    return dest


def set_dnp_at_lines_copy(nl: Netlist, dest: str, line_nos, dnp: str = "DNP") -> str:
    """把网表**副本**里指定物理行的 `dnp` 列改掉 (★原网表只读, 绝不写原文件★)。

    ★用途: 反向用例要锁死"dnp 是行级、别再拿错行" ⇒ 必须能**只改某一行**的 dnp。
    ★逐行引号感知切分/回拼, 其余字节原样保留 (含 CRLF 行尾)。
    """
    targets = set(int(n) for n in line_nos)
    out_lines = []
    for idx, ln in enumerate(nl.lines):
        line_no = idx + 1                      # 物理行号 (1 = 表头)
        if line_no not in targets or idx == 0 or not ln.strip():
            out_lines.append(ln)
            continue
        body, term = (ln.rstrip("\r"), "\r") if ln.endswith("\r") else (ln, "")
        fields, quoted = _split_csv_line(body)
        if len(fields) > 7:                    # dnp 是第 8 列 (index 7)
            fields[7] = dnp
            out_lines.append(_join_csv_line(fields, quoted) + term)
            continue
        out_lines.append(ln)
    with open(dest, "w", encoding="utf-8-sig", newline="") as fh:
        fh.write("\n".join(out_lines))
    return dest


def drop_device_rows_copy(nl: Netlist, dest: str, ref: str) -> str:
    """★把某个位号的**器件本体行** (type=IC/SW) 从网表副本里删掉 (★引脚行 type=NET 留着★)。

    ★用途 (ISS-235): 模拟「BOM/装配单里那颗开关**只有引脚行、没有器件行**」⇒ BOM 会漏掉它。
      ★与 `drop_refs_copy` 的区别: 后者把该位号的**全部行**删掉 (模拟「这颗器件不在网表里」),
        本函数只删器件本体行 (模拟「器件在网表里、但 BOM 里没有它」) ⇒ ★两者是不同的缺陷, 必须分别有反向用例 ★。
    """
    out_lines = []
    for idx, ln in enumerate(nl.lines):
        if idx == 0 or not ln.strip():
            out_lines.append(ln)
            continue
        body = ln.rstrip("\r")
        fields, _q = _split_csv_line(body)
        fref = fields[4] if len(fields) > 4 else ""
        ftype = (fields[6] if len(fields) > 6 else "").strip().upper()
        if fref == nl.actual_ref(ref) and ftype in ("IC", "SW"):
            # ★ISS-321 · S1 位号改名适配★
            continue
        out_lines.append(ln)
    with open(dest, "w", encoding="utf-8-sig", newline="") as fh:
        fh.write("\n".join(out_lines))
    return dest


def drop_refs_copy(nl: Netlist, dest: str, refs) -> str:
    """把某个位号的**全部行**从网表副本里删掉 (用来模拟"该器件不在网表了")。"""
    refs = set(nl.actual_ref(r) for r in refs)   # ★ISS-321 · S1 位号改名适配★
    out_lines = []
    for idx, ln in enumerate(nl.lines):
        if idx == 0 or not ln.strip():
            out_lines.append(ln)
            continue
        body = ln.rstrip("\r")
        fields, _q = _split_csv_line(body)
        ref = fields[4] if len(fields) > 4 else ""
        if ref in refs:
            continue
        out_lines.append(ln)
    with open(dest, "w", encoding="utf-8-sig", newline="") as fh:
        fh.write("\n".join(out_lines))
    return dest


# ----------------------------------------------------------------------------
# ★★【ISS-291 · 2026-11-17 · sw-lead】★★ 判决源: SoM 脚表 (★"哪些脚是 SAR-ADC" 的真源★)
#   ★**根因**: F4 原先按【元组顺序】取链 (第一条 populated 的链) ⇒ 判的是 VBUS_DET_D,
#     而它的落点是 pin100 = USB_DRD1_VBUSDET = USB OTG 插入检测**数字**脚
#     ⇒ ★【USB 数字脚被当 12bit SAR-ADC 在判】★, 而★【真 ADC 链 BAT_DET (pin38 = SARADC_VIN5,
#     1.8V 域) 一条判据都没有】★
#   ★**修法 (三条, 一条都不许省)**:
#     ① 判决源 = `HW/PCB/FET3572C_PIN_TABLE.csv` (SoM 厂 IO 域表) 的 signal 列 + vol 列
#        · signal 以 SARADC 开头 ⇒ 该脚是 SAR-ADC 输入
#        · vol = 该脚 IO 域 (SARADC_VIN5 = 1.8V; USB_DRD1_VBUSDET = —— ⇒ 域未知 ⇒ [0数据])
#     ② 落点 = 网表实读 (NET 行找中点网 → 找 J_SOM_P1 pinN)
#     ③ 脚表读不到 / 落点不唯一 / 没有链落到 ADC 脚 ⇒ ★fail-closed 红★
#        (★绝不许退回"元组第一条"★ —— 那正是本单要修的错)
# ----------------------------------------------------------------------------
PIN_TABLE_REL = os.path.join("HW", "PCB", "FET3572C_PIN_TABLE.csv")

# ★取链规则开关: "by_landing_pin" = 新口径 (默认); "tuple_order" = ★老错规则★,
#   **只给 ISS-291 反向用例用** (反向用例把它切过去 ⇒ active_chain 判据必须变红)。
CHAIN_SELECT_MODE = "by_landing_pin"

_SOM_PIN_RE = re.compile(r"^(J_SOM_P1)\s+pin(\d+)$")


def load_som_pin_table(path=None):
    """读 SoM 脚表 → ({(conn, num): {...}}, meta)。读不到 ⇒ (None, 原因) ⇒ 判红 (fail-closed)。"""
    p = path or os.path.join(_PROJECT_ROOT, PIN_TABLE_REL)
    if not os.path.exists(p):
        return None, "SoM 脚表不存在: %s" % PIN_TABLE_REL
    try:
        with open(p, "rb") as fh:
            raw = fh.read()
        md5 = hashlib.md5(raw).hexdigest()
        with open(p, "r", encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
    except Exception as exc:                                    # noqa: BLE001
        return None, "SoM 脚表读失败: %s" % exc
    table = {}
    for row in rows:
        conn = (row.get("conn") or "").strip()
        num = (row.get("num") or "").strip()
        sig = (row.get("signal") or "").strip()
        if not conn or not num or not sig:
            continue
        vol_raw = (row.get("vol") or "").strip()
        table[(conn, num)] = {
            "ball": (row.get("ball") or "").strip(),
            "signal": sig,
            "gpio": (row.get("gpio") or "").strip(),
            "vol_raw": vol_raw,
            "vol": parse_volt(vol_raw),
            "desc": (row.get("desc") or "").strip(),
            "default_function": (row.get("default_function") or "").strip(),
        }
    meta = {"path": os.path.relpath(p, _PROJECT_ROOT), "md5": md5, "rows": len(table)}
    return table, meta


def resolve_chain_landing(nl: Netlist, r_top: str, r_bot: str) -> dict:
    """★该分压链落到哪个 SoM 脚★ (网表实读, 不许手抄)。

    ① 中点网 = 节点列同时出现上臂/下臂两个位号的那一行的 net 列
       (BAT_DET ⇒ 网表 L183; VBUS_DET_D ⇒ 网表 L435)
    ② 落点脚 = 中点网上 node1/node2 形如 "J_SOM_P1 pinN" 的行
       (中点网与落点行不同名时 ⇒ 再按 node 列反查: VBUS_DET_D ⇒ 网表 L439)
    """
    out = {"mid_net": "", "som_conn": "", "som_pin": "", "landing_line": 0}
    mid_net = ""
    for x in nl.rows:
        a = (x.get("node1") or "").strip()
        b = (x.get("node2") or "").strip()
        if {a, b} == {r_top, r_bot}:
            net = (x.get("net") or "").strip()
            if net and not net.startswith("RAIL_") and net != "GND":
                mid_net = net
                break
    out["mid_net"] = mid_net
    if not mid_net:
        return out

    def _pin_of(x):
        for k in ("node1", "node2"):
            m = _SOM_PIN_RE.match((x.get(k) or "").strip())
            if m:
                return m.group(1), m.group(2)
        return None, None

    for x in nl.rows_on_net(mid_net):
        conn, pin = _pin_of(x)
        if pin:
            out.update({"som_conn": conn, "som_pin": pin, "landing_line": x.get("_line_no", 0)})
            return out
    # ★落点行的 net 与中点网不同名 (例: 网表 L439 net=VBUS_DET / node2=VBUS_DET_D) ⇒ 按 node 列反查
    for x in nl.rows:
        if mid_net not in ((x.get("node1") or "").strip(), (x.get("node2") or "").strip()):
            continue
        conn, pin = _pin_of(x)
        if pin:
            out.update({"som_conn": conn, "som_pin": pin, "landing_line": x.get("_line_no", 0)})
            return out
    return out


def classify_landing(pin_table, landing: dict):
    """★按【脚表】给落点分类★ → (类别, 脚表条目)。类别 ∈ {"ADC", "DIGITAL", "UNKNOWN"}。

    ★**连接器名映射**: 网表里 SoM 连接器叫 `J_SOM_P1/P2/P3`, 脚表里叫 `P1/P2/P3`
      ⇒ ★不许硬编一张映射表★ ⇒ 直接从连接器名尾部取 "P<n>" 即可 (J_SOM_P1 → P1)。
    """
    if not pin_table or not landing.get("som_pin"):
        return "UNKNOWN", None
    conn = (landing.get("som_conn") or "").strip()
    candidates = [conn]
    m = re.search(r"(P\d+)$", conn)
    if m and m.group(1) not in candidates:
        candidates.append(m.group(1))
    ent = None
    for c in candidates:
        ent = pin_table.get((c, landing.get("som_pin")))
        if ent:
            break
    if not ent or not isinstance(ent, dict):
        return "UNKNOWN", None
    if ent["signal"].upper().startswith("SARADC"):
        return "ADC", ent
    return "DIGITAL", ent


def _det_supply(nl: Netlist, chain: dict):
    """→ (该链上臂所在轨的标称电压, 来源说明)。读不到 ⇒ (None, 原因)。"""
    rail = nl.rail_of(chain["r_top_ref"])
    v = nl.rail_volts(rail) if rail else None
    if v is not None:
        return v, "网表 RAIL 行 %s = %gV" % (rail, v)
    if chain["tag"] == "VBUS_DET_D":
        v2 = nl.rail_volts("VBUS_5V")
        if v2 is not None:
            return v2, "网表 RAIL 行 VBUS_5V = %gV (上臂挂 %s)" % (v2, rail)
        return DEVICE["USB_VBUS_NOM_V"], "DEVICE 常量 USB_VBUS_NOM_V (网表里 RAIL_DEMO_5V 无 RAIL 行)"
    return DEVICE["BAT_FULL_V"], "DEVICE 常量 BAT_FULL_V (网表里 %s 无 RAIL 行)" % rail


# ----------------------------------------------------------------------------
# 2. 逐条结论的计算 —— 全部现读现算
# ----------------------------------------------------------------------------
def compute(nl: Netlist, isp_meas=None) -> dict:
    o: dict = {}
    o["NETLIST_ANCHOR"] = nl.anchor()

    # ---------------------------------------------------------------- F1 复位 RC
    r_pull = nl.ohm("R_PU_RESET_N")
    r_ser = nl.ohm("R_SER_RESET_N")
    c_rst = nl.farad("C_RST")
    pull_rail = nl.rail_of("R_PU_RESET_N")
    v_pull = nl.rail_volts(pull_rail) or 1.8
    # 网表自己的 τ 注记 (从 C_RST 的 note 里读, 不是手抄)
    tau_annot_ms = parse_tau_ms(nl.net_note("RESET_N_SOC")) or parse_tau_ms(
        " ".join(x.get("note", "") for x in nl.rows_of("C_RST")))
    tau_rel = (r_pull + r_ser) * c_rst
    tau_asr = r_ser * c_rst
    t_vih = tau_rel * math.log(1.0 / (1.0 - 0.7))
    # 复位链上的硬件 AND (V1.8 新增)
    q_and = nl.populated("Q_AND")
    pg_pull = nl.ohm("R_PG_PULL")
    # ★★PG 源器件的 dnp 必须**按【PG_AND 这条网】取那一行** ★★
    #   (★不是 dnp_of(ref)★ —— 那是取该位号第一条 IC/SW 行 = **拿错行** ⇒ ISS-190 打回的根因★)
    pg_sources = {}
    for ref in ("U_DCDC_VCORE", "U_DCDC_VIO"):
        dnp_row = nl.dnp_of_row(ref, "PG_AND")
        pg_sources[ref] = {
            "dnp": dnp_row,                                   # ★行级口径 (PG_AND 上的连接行)★
            "populated": (dnp_row == "必装"),
            "dnp_source": "PG_AND 网上的连接行 (行级口径)",
            "device_ic_row_dnp": nl.dnp_of(ref),               # ★器件级 (那颗 IC 本身装不装) —— 与上面**不是一回事**★
        }
    # ★PG_AND 这条网的逐行装机状态 (★dnp 是行级★)
    pg_and_rows = nl.rows_on_net("PG_AND")
    pg_and_state = {
        "net": "PG_AND",
        "row_count": len(pg_and_rows),
        "rows": nl.row_states_on_net("PG_AND"),
        "dnp_rows": sorted({nl.logical_ref(x.get("ref", "")) for x in pg_and_rows if x.get("dnp") != "必装"}),   # ★ISS-321 · 输出归一化★
        "all_rows_populated": all(x.get("dnp") == "必装" for x in pg_and_rows),
        "pullup_ref": "R_PG_PULL",
        "pullup_ohm": pg_pull,
        "pullup_row_dnp": nl.dnp_of_row("R_PG_PULL", "PG_AND"),
        "q_and_gate_row_dnp": nl.dnp_of_row("Q_AND", "PG_AND"),
        "q_envc_row_dnp": nl.dnp_of_row("Q_ENVC", "PG_AND"),
        "pg_source_devices": pg_sources,
        "pg_sources_all_populated": all(v["dnp"] == "必装" for v in pg_sources.values()),
    }
    # ★RESET_N 上到底有谁在拉 (★main 点名: U_SUPV pin1 也是 DNP 且接在 RESET_N 上★)
    reset_n_rows = nl.rows_on_net("RESET_N")
    reset_n_state = {
        "net": "RESET_N",
        "rows": nl.row_states_on_net("RESET_N"),
        "members": sorted({nl.logical_ref(x.get("ref", "")) for x in reset_n_rows}),   # ★ISS-321 · 输出归一化★
        "dnp_rows": sorted({nl.logical_ref(x.get("ref", "")) for x in reset_n_rows if x.get("dnp") != "必装"}),   # ★ISS-321 · 输出归一化★
        "q_and_drain_row_dnp": nl.dnp_of_row("Q_AND", "RESET_N"),
        "sw_rst_row_dnp": nl.dnp_of_row("SW_RST", "RESET_N"),
        "u_supv_pin1_row_dnp": nl.dnp_of_row("U_SUPV", "RESET_N"),
    }
    o["F1_reset_rc"] = {
        "r_pull_ohm": r_pull,
        "r_pull_rail": pull_rail,
        "r_pull_rail_v": v_pull,
        "r_ser_ohm": r_ser,
        "c_rst_f": r(c_rst, 15),
        "tau_release_ms": r(tau_rel * 1e3),
        "tau_assert_us": r(tau_asr * 1e6),
        "t_reach_0p7vdd_ms": r(t_vih * 1e3),
        "netlist_annotation_ms": tau_annot_ms,
        "annotation_error_ratio": r((tau_annot_ms * 1e-3) / tau_rel, 1) if tau_annot_ms else None,
        "q_and_in_netlist": q_and,
        "pg_pullup_ohm": pg_pull,
        "pg_source_devices": pg_sources,
        "pg_and_state": pg_and_state,
        "reset_n_state": reset_n_state,
        "verdict": "网表注记 'τ=%sms' 与 R/C 原值不符: 实为释放 τ=%.1fms / 断言 τ=%.0fµs (差 %.1f 倍); "
                   "★V1.8 新增 Q_AND 硬件 AND + R_PG_PULL 10k 上拉 ⇒ **PG 已进复位链** (旧结论部分推翻); "
                   "★★行级口径 (★逐行读 PG_AND★): 提到两路 PG pin (pin4) 的连接行 (L62/L64/L402/L403) dnp **全是必装** ⇒ "
                   "**「PG 源器件 DNP」不成立**; ★**真正 DNP 的是 Q_ENVC** (它接在 PG_AND 上, L71) ⇒ ⇒ "
                   "PG_AND 有 R_PG_PULL 10k 上拉 ⇒ Q_AND 栅极接在 PG_AND 上 ⇒ **栅极恒高 ⇒ Q_AND 导通 ⇒ "
                   "RESET_N 恒被拉低 ⇒ 首台板可能不启动** (需 hw-lead 定夺); "
                   "★另: U_SUPV pin1 也是 DNP 且接在 RESET_N 上 (它**不参与**拉复位); "
                   "★器件级补注: 两颗 DC-DC **芯片本体** (U_DCDC_VCORE/U_DCDC_VIO 的 IC 行) 是 DNP ⇒ 实物上 PG 脚不在板上 ⇒ "
                   "PG_AND 更没东西能把它拉低 ⇒ 结论方向不变、且更强" % (
                       tau_annot_ms, tau_rel * 1e3, tau_asr * 1e6, (tau_annot_ms * 1e-3) / tau_rel),
    }

    # ---------------------------------------------------------------- F2 监督器
    div1_val = nl.comp_value("R_SUPV_DIV1")
    div2_val = nl.comp_value("R_SUPV_DIV2")
    div_zero = ("0Ω" in div1_val) and ("0Ω" in div2_val)
    ct_rows = [x for x in nl.rows if re.search(r"(?:^|\W)CT(?:\W|$)", x.get("value", "") or "")]
    mr_rows = [x for x in nl.rows if re.search(r"(?:^|\W)MR(?:\W|$)", x.get("value", "") or "")]
    supv_populated = nl.populated("U_SUPV")

    def ratio_for(vit: float) -> float:
        return vit / DEVICE["U_SUPV_VIT_REF"] - 1.0

    o["F2_supervisor"] = {
        "vit_ref_v": DEVICE["U_SUPV_VIT_REF"],
        "ratio_for_vit_3v0": r(ratio_for(3.0), 3),
        "ratio_for_vit_2v7": r(ratio_for(2.7), 3),
        "delay_ct_open_ms": r(DEVICE["U_SUPV_DELAY_CT_OPEN"] * 1e3),
        "delay_ct_vdd_ms": r(DEVICE["U_SUPV_DELAY_CT_VDD"] * 1e3),
        "ct_pin_in_netlist": len(ct_rows) > 0,
        "ct_pin_rows": len(ct_rows),
        "mr_pin_in_netlist": len(mr_rows) > 0,
        "u_supv_populated": supv_populated,
        "u_supv_dnp": nl.dnp_of("U_SUPV"),
        "div1_value": div1_val,
        "div2_value": div2_val,
        "divider_dnp": [nl.dnp_of("R_SUPV_DIV1"), nl.dnp_of("R_SUPV_DIV2")],
        "min_reset_release_ms": r(DEVICE["U_SUPV_DELAY_CT_OPEN"] * 1e3 + tau_rel * 1e3 * 1.204),
        "note": "两臂都填 0Ω => R2=0 => SENSE=GND => V_SOC_IO 对地短路 (装配级灾难); "
                "两臂都 DNP => SENSE 悬空 => 释放时刻未定义",
        "divider_zero_risk": div_zero,
        "verdict": "★U_SUPV 在现网表是 **DNP** (SoM 自带 PMIC 已做上电复位) ⇒ 监督器这条支路**实物不存在**; "
                   "CT 脚在网表里有 %d 行 (但属 DNP 器件), MR 仍 %d 行 ⇒ 旧结论『CT/MR 悬空 = 20ms』**不再适用**; "
                   "★仍成立: R_SUPV_DIV1/DIV2 仍标 0Ω 跳线位且 **dnp=必装** ⇒ 两颗都装 0Ω 会把 RAIL_V_SOC_IO 短路到地"
                   % (len(ct_rows), len(mr_rows)),
    }

    # ---------------------------------------------------------------- F3 I2C 上升沿
    # ★按**网名**分别取上拉电阻值与所属轨域 (不再用一个 R_I2C_PULL 手抄常量)
    k_tr = DEVICE["I2C_TR_K"]
    buses = {}
    pull_refs = sorted({x["ref"] for x in nl.rows
                         if re.match(r"^R_PU_(I2C[AB])_(SCL|SDA)(_1)?$", x.get("ref", "") or "")})   # ★ISS-321 · S1 位号改名适配★
    for ref in pull_refs:
        m = re.match(r"^R_PU_(I2C[AB])_(SCL|SDA)(_1)?$", ref)   # ★ISS-321 · S1 位号改名适配★
        bus = "I2C_" + m.group(1)[-1]
        ohm = nl.ohm(ref)
        rail = nl.rail_of(ref)
        v_rail = nl.rail_volts(rail)
        b = buses.setdefault(bus, {"pullup_refs": [], "pullup_ohm": ohm, "pullup_rail": rail,
                                   "pullup_rail_v": v_rail, "std_mode_ok_at_300pF": None,
                                   "annotation_ns": None, "annotation_stale": None,
                                   "annotation_text": ""})
        b["pullup_refs"].append(ref)
        b["pullup_ohm"] = ohm if b["pullup_ohm"] is None else b["pullup_ohm"]
    for bus, b in buses.items():
        ohm = b["pullup_ohm"]
        b["tr_ns_at_100pF"] = r(k_tr * ohm * 100e-12 * 1e9, 1)
        b["tr_ns_vs_cable_cap"] = {f"{c}pF": r(k_tr * ohm * (c * 1e-12) * 1e9, 1)
                                   for c in (100, 200, 300, 500)}
        b["std_mode_ok_at_300pF"] = b["tr_ns_vs_cable_cap"]["300pF"] <= DEVICE["I2C_TR_STD_MAX_NS"]
        b["fast_mode_ok_at_300pF"] = b["tr_ns_vs_cable_cap"]["300pF"] <= DEVICE["I2C_TR_FAST_MAX_NS"]
        # 网表自己的 t_r 注记 (NET 行) —— 实读
        for net in (bus + "_SCL", bus + "_SDA"):
            for x in nl.net_rows(net):
                tr_ns = parse_tr_ns(x.get("value", "") or "")
                if tr_ns:
                    b["annotation_ns"] = tr_ns
                    b["annotation_text"] = x.get("value", "")
                    break
            if b["annotation_ns"]:
                break
        if b["annotation_ns"]:
            b["annotation_stale"] = abs(b["annotation_ns"] - b["tr_ns_at_100pF"]) > 1.0
            b["annotation_error_ratio"] = r(b["annotation_ns"] / b["tr_ns_at_100pF"], 2)
    # 主判据 = **最差总线** (t_r 最大的一条) —— 速率上限必须按最差总线定
    worst = max(buses.items(), key=lambda kv: kv[1]["tr_ns_at_100pF"]) if buses else ("(none)", {})
    # 注记误差 = 各总线里最大者 (注记是写在 I2C_A 那两行上的旧口径)
    ann_ratios = [b["annotation_error_ratio"] for b in buses.values() if b.get("annotation_error_ratio")]
    o["F3_i2c_rise"] = {
        "tr_ns_at_100pF": worst[1].get("tr_ns_at_100pF"),
        "worst_bus": worst[0],
        "worst_bus_reason": "主判据取所有 I2C 总线里 t_r 最大的一条 (最差总线) ⇒ 速率上限按它定",
        "netlist_annotation_ns": max([b["annotation_ns"] for b in buses.values() if b.get("annotation_ns")],
                                     default=None),
        "annotation_error_ratio": max(ann_ratios) if ann_ratios else None,
        "tr_ns_vs_cable_cap": worst[1].get("tr_ns_vs_cable_cap", {}),
        "spec_std_mode_max_ns": DEVICE["I2C_TR_STD_MAX_NS"],
        "spec_fast_mode_max_ns": DEVICE["I2C_TR_FAST_MAX_NS"],
        "buses": buses,
        "verdict": "★按网名分别读: " + "; ".join(
            "%s = %sk → %s (%.1fV 域): t_r@100pF=%.0fns, @300pF=%.0fns ⇒ 标准模式(≤1000ns) %s"
            % (bus, ("%g" % (b["pullup_ohm"] / 1000.0)), b["pullup_rail"], b["pullup_rail_v"],
               b["tr_ns_at_100pF"], b["tr_ns_vs_cable_cap"]["300pF"],
               "✅" if b["std_mode_ok_at_300pF"] else "❌")
            for bus, b in sorted(buses.items())) +
            " ⇒ 最差总线 = %s ⇒ I2C 速率上限按 %s 定; ★旧文档写的『4.7k@I2C_A ⇒ 398ns / 1195ns 超标』"
            "**对 I2C_A 已不成立** (现为 2.2k/1.8V), 现在超标的是 %s" % (
                worst[0], worst[0], worst[0]),
    }

    # ---------------------------------------------------------------- F4 ADC 检测通道
    # ★★【ISS-291 · 2026-11-17 · sw-lead】★★ 判决对象 + 满量程口径【双错】收口 ★★
    #   ★**错在哪 (两条都错, 互不相关)**:
    #     ① 判决对象错: 取链规则 = 「元组顺序第一条 populated 链」⇒ 判的是 VBUS_DET_D
    #        (落点 = 网表 L439 ⇒ J_SOM_P1 pin100 = USB_DRD1_VBUSDET = USB OTG 插入检测**数字**脚)
    #        ⇒ ★【USB 数字脚被当 12bit SAR-ADC 在判建立时间/漏电偏移/满量程】★
    #        ⇒ ★【真 ADC 链 BAT_DET (落点 = 网表 L186 ⇒ J_SOM_P1 pin38 = SARADC_VIN5, 1.8V 域) 无判据】★
    #     ② 满量程口径错: DEVICE["V_DET_FS"] 写死 3.3V ⇒ 官方是 1.8V 域
    #        ⇒ 同一个 BAT_DET 分压链, 网表 L182 note 写 2.1% FS 而闸算 15% FS (差 7 倍)
    #   ★**新口径 (判决源 = SoM 脚表, 不是元组顺序)**:
    #     ① 判决源 = HW/PCB/FET3572C_PIN_TABLE.csv (signal 列 + vol 列) ⇒ 读不到 ⇒ fail-closed
    #     ② 落点 = 网表实读 ⇒ 按【落点是不是 SAR-ADC 脚】取链 ⇒ ADC 链 = BAT_DET
    #     ③ 满量程 = 1.8V (官方 datasheet) ⇒ 漏电偏移 %FS 必须与网表 L182 note 逐字对上 (2.1%)
    #     ④ 数字链 (VBUS_DET_D) 从 ADC 判据里摘出去, 另按【数字检测输入】口径单判 (F4D 段)
    pin_table, pin_meta = load_som_pin_table()
    det_chains = []
    for top, bot, cap, tag in (("R_VBUS_DET_D1", "R_VBUS_DET_D2", "C_DET_VBUS_D", "VBUS_DET_D"),
                               ("R_BAT_DET_1", "R_BAT_DET_2", "C_DET_BAT", "BAT_DET")):
        rt, rb, cv = nl.ohm(top), nl.ohm(bot), nl.farad(cap)
        dev_dnp = {r: _device_dnp_rows(nl, r) for r in (top, bot, cap)}
        landing = resolve_chain_landing(nl, top, bot)
        klass, pent = classify_landing(pin_table, landing)
        det_chains.append({
            "tag": tag, "r_top_ohm": rt, "r_bot_ohm": rb, "c_f": cv,
            "r_top_ref": top, "r_bot_ref": bot, "cap_ref": cap,
            "r_top_dnp": nl.dnp_of(top) or nl.rows_of(top)[0].get("dnp", "") if nl.rows_of(top) else "",
            "r_bot_dnp": nl.rows_of(bot)[0].get("dnp", "") if nl.rows_of(bot) else "",
            "c_dnp": nl.rows_of(cap)[0].get("dnp", "") if nl.rows_of(cap) else "",
            "populated": bool(nl.rows_of(top)) and nl.rows_of(top)[0].get("dnp") == "必装"
                          and bool(nl.rows_of(bot)) and nl.rows_of(bot)[0].get("dnp") == "必装",
            # ★★【ISS-285】逐颗【器件本体行】的 dnp (★不许拿该位号第一条行★)
            "device_dnp": dev_dnp,
            "device_populated": bool(dev_dnp.get(top)) and all(d == "必装" for d in dev_dnp.get(top))
                                and bool(dev_dnp.get(bot)) and all(d == "必装" for d in dev_dnp.get(bot))
                                and bool(dev_dnp.get(cap)) and all(d == "必装" for d in dev_dnp.get(cap)),
            # ★★【ISS-291】落点 + 落点分类 (判决源 = SoM 脚表 signal/vol 两列)
            "landing_net": landing["mid_net"],
            "landing_line": landing["landing_line"],
            "som_conn": landing["som_conn"],
            "som_pin": landing["som_pin"],
            "pin_class": klass,
            "pin_signal": (pent or {}).get("signal", ""),
            "pin_vol_raw": (pent or {}).get("vol_raw", ""),
            "pin_vol_v": (pent or {}).get("vol"),
            "pin_desc": (pent or {}).get("desc", ""),
        })
    for ch in det_chains:
        if ch["r_top_ohm"] and ch["r_bot_ohm"]:
            ch["rth_ohm"] = r((ch["r_top_ohm"] * ch["r_bot_ohm"]) / (ch["r_top_ohm"] + ch["r_bot_ohm"]), 0)
            ch["tau_ms"] = r(ch["rth_ohm"] * ch["c_f"] * 1e3)
        else:
            ch["rth_ohm"] = None
            ch["tau_ms"] = None

    # ---- ★★【ISS-291】取链: 按【落点是不是 SAR-ADC 脚】★ (★不是元组顺序★) ----
    adc_chains = [c for c in det_chains if c["pin_class"] == "ADC"]
    adc_populated = [c for c in adc_chains if c["device_populated"]]
    dig_chains = [c for c in det_chains if c["pin_class"] == "DIGITAL"]
    if CHAIN_SELECT_MODE == "tuple_order":
        # ★★【ISS-291 反向用例专用】★★ 老错规则 (元组顺序第一条 populated 链)
        _old = [c for c in det_chains if c["populated"]] or det_chains
        adc_act = _old[0]
        select_reason = ("★tuple_order 模式 (★仅供 ISS-291 反向用例: 老错规则「元组第一条」★)")
    elif len(adc_populated) == 1:
        adc_act = adc_populated[0]
        select_reason = ("★唯一一条装机链落在 SAR-ADC 脚上 (判决源 = SoM 脚表 signal 列: %s)★"
                         % adc_act["pin_signal"])
    elif len(adc_populated) > 1:
        adc_act = None
        select_reason = "★有多条链落到 SAR-ADC 脚 ⇒ 判决对象不唯一 ⇒ fail-closed★"
    else:
        adc_act = None
        select_reason = ("★没有任何装机链落到 SAR-ADC 脚 ⇒ ADC 输入悬空 / 无判据 ⇒ fail-closed★")

    # ---- ADC 链的量 (满量程 = 1.8V 域) ----
    fs_v = DEVICE["V_DET_FS"]
    lsb_v = fs_v / (2 ** DEVICE["ADC_BITS"])
    n_settle = math.log(1.0 / (0.5 * lsb_v / fs_v))
    if adc_act is not None:
        rth = adc_act["rth_ohm"]
        tau_adc = rth * adc_act["c_f"]
        t_settle = n_settle * tau_adc
        leak_err = DEVICE["I_ADC_LEAK_MAX"] * rth
        v_supply, v_supply_src = _det_supply(nl, adc_act)
        rt_a, rb_a = adc_act["r_top_ohm"], adc_act["r_bot_ohm"]
        node_v = v_supply * (rb_a / (rt_a + rb_a)) if (rt_a and rb_a) else None
        standby_ua = v_supply / (rt_a + rb_a) * 1e6 if (rt_a and rb_a) else None
    else:
        rth = tau_adc = t_settle = leak_err = node_v = standby_ua = None
        v_supply, v_supply_src = None, "(无 ADC 链)"

    # ---- ★★【ISS-291】口径同源自证: 三个数必须与网表 L182 note 逐字对上 ----
    note_facts = _bat_det_note_facts(nl)
    leak_pct_fs = (leak_err / fs_v * 100) if (leak_err is not None and fs_v) else None
    fs_caliber_ok = bool(
        note_facts.get("pct_fs") is not None
        and abs(fs_v - 1.8) < 1e-9
        and leak_pct_fs is not None
        and abs(leak_pct_fs - note_facts["pct_fs"]) <= 0.06
        and note_facts.get("mv") is not None and leak_err is not None
        and abs(leak_err * 1e3 - note_facts["mv"]) <= 0.6
        and note_facts.get("rth_k") is not None and rth is not None
        and abs(rth / 1e3 - note_facts["rth_k"]) <= 0.6)

    settle_ok = (t_settle is not None and t_settle * 1e3 <= DEVICE["ADC_SETTLE_MAX_MS"])
    leak_ok = (leak_err is not None and leak_err <= DEVICE["ADC_LEAK_OFFSET_MAX_V"])
    node_ok = (node_v is not None and node_v <= DEVICE["ADC_NODE_MAX_V"]
               and node_v <= DEVICE["ADC_NODE_NOM_MAX_V"])
    object_ok = (adc_act is not None and adc_act["tag"] == "BAT_DET"
                 and adc_act["som_pin"] == "38" and adc_act["pin_signal"] == "SARADC_VIN5")
    populated_ok = bool(adc_act is not None and adc_act["device_populated"])
    fs_util_pct = (node_v / fs_v * 100) if (node_v is not None and fs_v) else None

    o["F4_adc_det"] = {
        "active_chain": (adc_act["tag"] if adc_act else "(无: fail-closed)"),
        "active_chain_pin": (adc_act["som_pin"] if adc_act else ""),
        "active_chain_signal": (adc_act["pin_signal"] if adc_act else ""),
        "active_chain_domain": (adc_act["pin_vol_raw"] if adc_act else ""),
        "chain_select_mode": CHAIN_SELECT_MODE,
        "chain_select_reason": select_reason,
        "judgment_source": ("SoM 脚表 %s (md5 %s, %d 行) + 网表落点实读"
                            % (pin_meta.get("path", "?"), (pin_meta.get("md5") or "?")[:12],
                               pin_meta.get("rows", 0))) if pin_table else
                           ("★脚表读不到 ⇒ fail-closed (%s)★" % (pin_meta or "")),
        "pin_table_md5": (pin_meta or {}).get("md5", ""),
        "full_scale_v": fs_v,
        "full_scale_source": SOURCES.get("V_DET_FS", ""),
        "adc_bits": DEVICE["ADC_BITS"],
        "lsb_mv": r(lsb_v * 1e3, 3),
        "chains": det_chains,
        "rth_ohm": rth,
        "tau_ms": r(tau_adc * 1e3) if tau_adc is not None else None,
        "t_settle_to_half_lsb_ms": r(t_settle * 1e3) if t_settle is not None else None,
        "leak_offset_v": r(leak_err, 4) if leak_err is not None else None,
        "leak_offset_pct_fs": r(leak_pct_fs, 1) if leak_pct_fs is not None else None,
        "standby_ua": r(standby_ua, 2) if standby_ua is not None else None,
        "supply_v": v_supply,
        "supply_source": v_supply_src,
        "node_v_at_supply": r(node_v, 4) if node_v is not None else None,
        "node_max_abs_v": DEVICE["ADC_NODE_MAX_V"],
        "node_nominal_max_v": DEVICE["ADC_NODE_NOM_MAX_V"],
        "fs_utilization_pct": r(fs_util_pct, 1) if fs_util_pct is not None else None,
        "netlist_note_facts": note_facts,
        "criteria": {
            "object_ok": object_ok,
            "fs_caliber_ok": fs_caliber_ok,
            "settle_ok": settle_ok,
            "leak_ok": leak_ok,
            "node_ok": node_ok,
            "populated_ok": populated_ok,
            "all_ok": bool(object_ok and fs_caliber_ok and settle_ok and leak_ok
                           and node_ok and populated_ok),
        },
        "verdict": (
            "★判决对象 = %s 链 (网表 L%s ⇒ %s pin%s = %s, %s 域) ⇒ 源阻抗 %sΩ / τ=%sms; "
            "12bit (LSB=%smV, 满量程 %sV) 需 %.1fms 建立 (红线 %sms ⇒ %s); "
            "1µA 漏电 ⇒ %.4fV 偏移 = %s%% 满量程 (红线 %sV ⇒ %s; ★与网表 L182 note 写死的 %s%% FS 逐字对上 ⇒ %s★); "
            "@%sV 节点 %sV ≤ abs-max %sV ⇒ %s (FS 利用率 %s%%); "
            "★老口径 (判 VBUS_DET_D + FS=3.3V) 报的那条红 = **假红** ⇒ 已作废; "
            "★VBUS_DET_D 链改按【数字检测输入】口径单判 (见 F4D 段)★; %s"
            % (adc_act["tag"] if adc_act else "(无)",
               adc_act["landing_line"] if adc_act else "-",
               adc_act["som_conn"] if adc_act else "-",
               adc_act["som_pin"] if adc_act else "-",
               adc_act["pin_signal"] if adc_act else "-",
               adc_act["pin_vol_raw"] if adc_act else "-",
               rth, r(tau_adc * 1e3) if tau_adc is not None else "-",
               r(lsb_v * 1e3, 3), fs_v,
               t_settle * 1e3 if t_settle is not None else float("nan"),
               DEVICE["ADC_SETTLE_MAX_MS"], "✔" if settle_ok else "❌",
               leak_err if leak_err is not None else float("nan"),
               r(leak_pct_fs, 1) if leak_pct_fs is not None else float("nan"),
               DEVICE["ADC_LEAK_OFFSET_MAX_V"], "✔" if leak_ok else "❌",
               note_facts.get("pct_fs", "?"),
               "✔" if fs_caliber_ok else "❌",
               v_supply if v_supply is not None else "-",
               r(node_v, 4) if node_v is not None else "-",
               DEVICE["ADC_NODE_MAX_V"], "✔" if node_ok else "❌",
               r(fs_util_pct, 1) if fs_util_pct is not None else "-",
               _bat_det_verdict(det_chains))),
    }

    # ---------------------------------------------------------------- F4D 数字检测输入 (USB OTG 插入检测)
    # ★★【ISS-291】VBUS_DET_D 链**不是** SAR-ADC 输入 ⇒ 从 ADC 判据里摘出来, 按数字脚口径单判 ★★
    o["F4D_usb_vbus_det"] = _f4d_usb_det(nl, det_chains, dig_chains)

    # ---------------------------------------------------------------- F5 TMP117
    temp_supply_rail = nl.rail_of("U_TEMP")
    v_temp_supply = nl.rail_volts(temp_supply_rail) or 3.3
    # TMP117 挂在哪条 I2C 总线 (从网表实读: U_TEMP pin1 的 net)
    temp_bus = "(未找到)"
    for x in nl.rows_of("U_TEMP"):
        if "pin1" in (x.get("node1", "") or "") or "I2C" in (x.get("net", "") or ""):
            if (x.get("net", "") or "").startswith("I2C"):
                temp_bus = x["net"].split("_")[0] + "_" + x["net"].split("_")[1]
                break
    self_heat_uw = DEVICE["TMP117_IV_SUPPLY"] * v_temp_supply * 1e6
    o["F5_tmp117"] = {
        "lsb_c": DEVICE["TMP117_LSB_C"],
        "first_read_after_reset_c": DEVICE["TMP117_RESET_READ"],
        "conv_period_s": DEVICE["TMP117_CONV_PERIOD"],
        "supply_rail": temp_supply_rail,
        "supply_v": v_temp_supply,
        "i2c_bus": temp_bus,
        "self_heat_uw": r(self_heat_uw, 2),
        "self_heat_verdict": "自热 %.1fµW << 测点热阻主导项 => 自热可忽略, 误差由**热耦合路径**主导" % self_heat_uw,
        "accuracy_bands_c": DEVICE["TMP117_ACC_BANDS_C"],
        "sw_rule": "复位后首读 = -256°C 必须丢弃; 转换 1Hz => 首次有效读数最坏 ~1s",
        "verdict": "TMP117 挂在 **%s** (旧文档写的是 I2C_A) ⇒ ★旧结论『TMP117 与 camera 同总线, camera 拉死 SDA "
                   "一起致盲温度保护』**对现网表不成立** (camera 在 I2C_A, TMP117 在 %s)" % (temp_bus, temp_bus),
    }

    # ---------------------------------------------------------------- F6 跨铰链 USB
    conn_usb_rows = nl.rows_of("CONN_USB")
    usb_gnd_pins = len([x for x in conn_usb_rows if (x.get("net", "") or "").upper() == "GND"])
    usb_pins = len({x.get("node2", "") for x in conn_usb_rows if "pin" in (x.get("node2", "") or "")})
    # 跨铰链 USB 数据路径: J_CHG 有没有带 D+/D−
    j_chg_nets = {x.get("net", "") for x in nl.rows_of("J_CHG")}
    hinge_usb_data = sorted(n for n in j_chg_nets if "USB" in n.upper())
    # 板内 USB 路径: J_USB_C → 串阻 → SoC USB 脚
    onboard_usb = []
    for x in nl.rows:
        blob = " ".join(x.get(k, "") or "" for k in ("net", "node1", "node2", "ref", "value"))
        if "USB_D_P" in blob and ("J_USB_C" in blob or "J_SOM" in blob):
            onboard_usb.append("%s(%s→%s)" % (x.get("ref", ""), x.get("node1", ""), x.get("node2", "")))
    fs_mb_s = DEVICE["USB_FS_MBPS"] / 8.0 * DEVICE["USB_BULK_EFF"]
    hs_mb_s = DEVICE["USB_HS_MBPS"] / 8.0 * DEVICE["USB_BULK_EFF"]
    o["F6_usb_hinge"] = {
        "conn_usb_pins": usb_pins,
        "conn_usb_gnd_pins": usb_gnd_pins,
        "conn_usb_in_netlist": len(conn_usb_rows) > 0,
        "iss085_min_gnd_pins": DEVICE["ISS085_MIN_GND_PINS"],
        "gnd_rule_ok": usb_gnd_pins >= DEVICE["ISS085_MIN_GND_PINS"],
        "hinge_usb_data_nets": hinge_usb_data,
        "cross_hinge_usb_data_path": bool(hinge_usb_data),
        "onboard_usb_rows": onboard_usb,
        "fs_bulk_MBps": r(fs_mb_s, 2),
        "hs_bulk_MBps": r(hs_mb_s, 2),
        "flash_s_at_FS": r(DEVICE["FLASH_IMAGE_MB"] / fs_mb_s, 1),
        "flash_s_at_HS": r(DEVICE["FLASH_IMAGE_MB"] / hs_mb_s, 1),
        "reset_resp_budget_ms": r(DEVICE["USB_RESET_RESP_S"] * 1e3),
        "verdict": "★CONN_USB 在现网表**已不存在** (%d 行) ⇒ 旧『CONN_USB 只有 1 个 GND pin』的复现命令"
                   "在现网表上已无对象; ★J_CHG 跨铰链 10pin 里**不含 USB D+/D−** (%s) ⇒ 跨铰链 USB 救砖链"
                   "**在现网表上不成立**; ★demo 板改成**板内 Type-C**: J_USB_C → 22Ω 串阻 → J_SOM_P1 pin92/94"
                   " ⇒ 刷写口在板内, 不跨铰链" % (len(conn_usb_rows),
                                                ",".join(hinge_usb_data) if hinge_usb_data else "(无)"),
    }

    # ---------------------------------------------------------------- F7 皮肤温度阈值换算
    tiers = {}
    for p in (0.05, 0.10, 0.16, 0.21):
        tiers["%.2fW" % p] = r(DEVICE["T_SKIN_A"] + DEVICE["T_SKIN_B"] * p, 1)
    o["F7_skin_tiers"] = {
        "model": "T_skin = %.1f + %.2f x P_W" % (DEVICE["T_SKIN_A"], DEVICE["T_SKIN_B"]),
        "p_to_tskin": tiers,
        "redline_c": DEVICE["T_SKIN_REDLINE"],
        "p_redline_w": DEVICE["P_REDLINE"],
        "legacy_sw_tiers_c": [70, 85, 95],
        "legacy_verdict": "SW 分片里已登记的 4 档温控 (<70/70-85/85-95/>95°C) 是**结温口径**, "
                          "与 43°C 皮肤红线不同源 => TMP117 定点后必须重定档",
        "tmp117_conservatism": "TMP117 装在镜脚 PCB 上 => T_PCB >= T_skin (皮肤是热沉) "
                               "=> 用 PCB 温度当皮肤代理是**保守方向** (不会漏判超温)",
    }

    # ---------------------------------------------------------------- F8 关机语义
    # ★按**器件位号**认负载开关 (不再用 LOAD|LOADSW|U_LS 这个看不见 U_PWR_SW 的 pattern)
    LOAD_SWITCH_REFS = ("U_PWR_SW", "U_EN_SW")
    load_refs = []
    seen = set()
    for ref in LOAD_SWITCH_REFS:
        if not nl.has_ref(ref) or nl.actual_ref(ref) in seen:
            continue
        # ★ISS-321 · S1 位号改名适配: seen 按【盘上真实名】⇒ 不重复计★
        seen.add(nl.actual_ref(ref))
        dev = nl.ic_rows(ref)
        load_refs.append({
            # ★ISS-321 · S1 位号改名适配: 报【逻辑名】⇒ 断言格式一条没变★
            "ref": nl.logical_ref(ref),
            "value": dev[0].get("value", "") if dev else "(★网表里只有引脚行, 没有器件行 ⇒ BOM 会漏掉它)",
            "dnp": dev[0].get("dnp", "") if dev else "(无器件行)",
            "has_device_row": bool(dev),
            "populated": (dev[0].get("dnp") == "必装") if dev else None,
            "row_count": len(nl.rows_of(ref)),
        })
    # 再兜一层: 值里写明"负载开关/电源开关"的 IC (按**语义**认, 不是按子串猜)
    for x in nl.rows:
        if x.get("type") == "IC" and re.search(r"(负载开关|电源开关|load switch)", x.get("value", "") or "", re.I):
            ref = x.get("ref", "")
            # ★ISS-321 · S1 位号改名适配: seen 按【盘上真实名】★
            if ref in seen or nl.actual_ref(ref) in seen:
                continue
            seen.add(ref)
            # ★ISS-321 · S1 位号改名适配: 报【逻辑名】★
            load_refs.append({"ref": nl.logical_ref(ref), "value": x.get("value", ""), "dnp": x.get("dnp", ""),
                              "has_device_row": True, "populated": x.get("dnp", "") == "必装",
                              "row_count": len(nl.rows_of(ref))})
    # ON 脚的下拉电阻 (默认关)
    on_pulldown = None
    for ref in ("R_PD_ON",):
        for x in nl.rows_of(ref):
            if (x.get("net", "") or "").upper() == "GND":
                on_pulldown = nl.ohm(ref)
    o["F8_power_off"] = {
        "load_switch_in_netlist": len(load_refs) > 0,
        "load_switch_refs": [x["ref"] for x in load_refs],
        "load_switch_detail": load_refs,
        "load_switch_without_device_row": [x["ref"] for x in load_refs if not x["has_device_row"]],
        "rail_switching_devices": len({x["ref"] for x in load_refs if x["populated"] is True}),
        "on_pin_pulldown_ohm": on_pulldown,
        "default_state": "关" if on_pulldown else "(未找到 ON 脚下拉)",
        "verdict": "★**旧结论已推翻**: 现网表里**有**负载开关 (U_PWR_SW = TPS22991RAA, VIN=BAT_SW → VOUT=RAIL_SYS; "
                   "ON pin2 = PWR_ON, 配 R_PD_ON 10k 下拉 ⇒ 默认关) + U_EN_SW (TPS22991RAA, IN=RAIL_DEMO_5V → "
                   "OUT=RAIL_BOARD_5V, EN=CARRIER_BOARD_EN) ⇒ **硬件断电通路存在** ⇒ "
                   "『关机只能靠软件深睡, 轨全部带电』**对现网表是错的**; "
                   "★新语义: SoC 把 PWR_ON GPIO 配高阻 ⇒ ON 掉回 10k 下拉 ⇒ U_PWR_SW 关 ⇒ 镜脚系统轨 SYS 断电 "
                   "(充电链仍在电池侧带电 ⇒ 关机也能充电)"
                   if load_refs else
                   "网表里没有负载开关/电源开关/EN 断开路径 ⇒ 关机只能靠软件深睡, 轨全部带电",
    }

    # ---------------------------------------------------------------- F4' 供电器件控制脚 EN/SS/CT/MR
    ctrl_rows = []
    for x in nl.rows:
        val = x.get("value", "") or ""
        m = re.search(r"(?:^|\W)(EN|SS|CT|MR)(?:\W|$)", val)
        if not m:
            continue
        sig = m.group(1)
        ref = x.get("ref", "")
        dev_pop = nl.populated(ref) if ref else False
        ctrl_rows.append({
            "signal": sig, "ref": ref, "net": x.get("net", ""),
            "node1": x.get("node1", ""), "node2": x.get("node2", ""),
            "row_type": x.get("type", ""), "row_dnp": x.get("dnp", ""),
            "device_populated": dev_pop,
            "line_no": x.get("_line_no"),
        })
    counts = {s: len([c for c in ctrl_rows if c["signal"] == s]) for s in ("EN", "SS", "CT", "MR")}
    o["F4_ctrl_pins"] = {
        "counts": counts,
        "total_rows": len(ctrl_rows),
        "rows": ctrl_rows,
        "en_device_populated": sorted({c["ref"] for c in ctrl_rows
                                       if c["signal"] == "EN" and c["device_populated"]}),
        "en_device_dnp": sorted({c["ref"] for c in ctrl_rows
                                 if c["signal"] == "EN" and not c["device_populated"]}),
        "verdict": "★**旧结论『供电器件的控制脚在网表里根本不存在』对 EN 已不成立**: 现网表 EN %d 行 / SS %d 行 / "
                   "CT %d 行 / MR %d 行; EN 的去向: 2 颗 DC-DC (pin13) + %d 颗 LDO (pin3, 直连 RAIL_BOARD_5V ⇒ 永远使能) "
                   "+ U_EN_SW (pin2, CARRIER_BOARD_EN) + SoM 输出脚; ★SS 仍 %d 行 (DC-DC 软启动脚没有) ⇒ "
                   "『电源什么时候起』在网表层面**仍未完全定义**; ★CT 的 %d 行属 **DNP** 的 U_SUPV ⇒ 实物不存在"
                   % (counts["EN"], counts["SS"], counts["CT"], counts["MR"],
                      len([c for c in ctrl_rows if c["signal"] == "EN" and "LDO" in c["ref"]]),
                      counts["SS"], counts["CT"]),
    }

    # ---------------------------------------------------------------- F5' 复位/启动上拉轨域
    reset_rail = nl.rail_of("R_PU_RESET_N")
    boot_rail = nl.rail_of("R_PU_BOOT_N")
    reset_v = nl.rail_volts(reset_rail)
    boot_v = nl.rail_volts(boot_rail)
    # SoC 的 IO 域在现网表由谁产生 (V_SOC_IO 的 IC 行还在不在 / 是不是 DNP)
    soc_io_rows = [x for x in nl.rows if x.get("net") == "V_SOC_IO" and x.get("type") == "IC"]
    o["F5_pullup_rail"] = {
        "reset_pullup_ref": "R_PU_RESET_N",
        "reset_pullup_ohm": nl.ohm("R_PU_RESET_N"),
        "reset_pullup_rail": reset_rail,
        "reset_pullup_rail_v": reset_v,
        "boot_pullup_ref": "R_PU_BOOT_N",
        "boot_pullup_ohm": nl.ohm("R_PU_BOOT_N"),
        "boot_pullup_rail": boot_rail,
        "boot_pullup_rail_v": boot_v,
        "same_rail": reset_rail == boot_rail,
        "soc_io_rail_producer": [x.get("ref", "") for x in soc_io_rows],
        "soc_io_rail_producer_dnp": [x.get("dnp", "") for x in soc_io_rows],
        "verdict": "★**仍成立**: RESET_N / BOOT_N 的上拉都挂在 **%s (%sV)** 这条**主板 LDO 轨**上, "
                   "而 SoC 的 IO 域 (V_SOC_IO) 在现网表上**不是这条轨** (%s) ⇒ 主板这条 1.8V 掉电时, "
                   "复位/启动脚仍被它撑着 ⇒ 幽灵复位风险不变; ★更强: 现网表 SoC 核心轨/IO 轨的 IC (U_DCDC_VCORE / "
                   "U_DCDC_VIO) 都是 DNP ⇒ SoC 用 SoM 自带 PMIC 的轨 ⇒ 主板这条 1.8V 与 SoC IO 域**完全无关**"
                   % (reset_rail, reset_v, ",".join(x.get("ref", "") for x in soc_io_rows) or "(无)"),
    }

    # ---------------------------------------------------------------- F9 ISP 段判据 (ISS-210)
    # ★板端没实测时 ⇒ meas=None ⇒ verdict = INDET + [0数据] (不许假装测过)
    o["F9_isp_budget"] = isp_budget_verdict(isp_meas)

    return o


# ----------------------------------------------------------------------------
# 3. 自检 —— ★既有 21 条一条不许删; 新增网表实读用例 + 反向用例★
# ----------------------------------------------------------------------------
# --- 既有 21 条 (ISS-090 原版, 断言内容保持等价) ---
SELF_TESTS_LEGACY = [
    ("复位释放 tau = 1.1ms", lambda o: abs(o["F1_reset_rc"]["tau_release_ms"] - 1.1) < 0.01),
    ("复位断言 tau = 100us", lambda o: abs(o["F1_reset_rc"]["tau_assert_us"] - 100.0) < 0.5),
    ("复位到 VIH = 1.32ms", lambda o: abs(o["F1_reset_rc"]["t_reach_0p7vdd_ms"] - 1.32) < 0.02),
    ("网表注记误差 >= 50 倍", lambda o: o["F1_reset_rc"]["annotation_error_ratio"] >= 50),
    ("监督器 CT 悬空延时 = 20ms", lambda o: abs(o["F2_supervisor"]["delay_ct_open_ms"] - 20.0) < 0.01),
    ("两臂 0Ω 短路风险已标注", lambda o: o["F2_supervisor"]["divider_zero_risk"] is True),
    ("I2C t_r@100pF = 398ns", lambda o: abs(o["F3_i2c_rise"]["tr_ns_at_100pF"] - 398.0) < 1.0),
    # ★★【ISS-225 重锚】原断言 = 「I2C 注记误差 >= 5 倍」⇒ 它断言的是【网表侧那条矛盾仍在】⇒
    #   ISS-220 d6 真把网表 I2C_A 改成 2.2k@1.8V (t_r=186ns) ⇒ **矛盾被上游真修好了** ⇒
    #   ★**这不是把红灯调没, 是网表侧那盏灯被真修好了** (留痕: SW/SW_MD5_BASELINE_LEDGER.md §3 R-02)
    #   ⇒ 断言方向反过来: ★**注记必须与实算一致** (不一致才红 ⇒ 那才是真缺陷)
    ("I2C 网表注记与实算一致 (误差 < 1.01 倍 ⇒ 网表侧矛盾已被 ISS-220 d6 消除)",
     lambda o: o["F3_i2c_rise"]["annotation_error_ratio"] is not None
               and o["F3_i2c_rise"]["annotation_error_ratio"] < 1.01),
    ("I2C 300pF 超标准模式上限", lambda o: o["F3_i2c_rise"]["tr_ns_vs_cable_cap"]["300pF"] > 1000.0),
    # ★★【ISS-291 · 2026-11-17 · sw-lead】★★ 下面这四条原断言 = 【老口径的缺陷事实】
    #   (判的是 VBUS_DET_D 链 + FS=3.3V ⇒ 500kΩ / 50ms / 451ms / 0.50V)
    #   ⇒ ★**判据对象与满量程口径双错**★ ⇒ ★按 ISS-225 同型订正: 断言按【正确口径】重写,
    #   ★**阈值一条都不许调松**★ (建立时间红线仍是 300ms, 漏电偏移红线仍是 0.4V) ★
    ("ADC 源阻抗 = 37.5k (★ISS-291: 判决对象 = BAT_DET 链 → pin38 SARADC_VIN5★)",
     lambda o: _num_close(o["F4_adc_det"]["rth_ohm"], 37500.0, 1.0)),
    ("ADC tau = 3.75ms (★ISS-291 口径★)", lambda o: _num_close(o["F4_adc_det"]["tau_ms"], 3.75, 0.05)),
    ("ADC 12bit 建立 33.8ms ≤ 300ms 红线 (★ISS-291 口径: 老口径的 451ms 是**假红**★)",
     lambda o: (o["F4_adc_det"]["t_settle_to_half_lsb_ms"] is not None
                and 0 < o["F4_adc_det"]["t_settle_to_half_lsb_ms"] <= 300.0)),
    ("ADC 漏电偏移 37.5mV ≤ 0.4V 红线 (★ISS-291 口径: 老口径的 0.50V 是**假红**★)",
     lambda o: (o["F4_adc_det"]["leak_offset_v"] is not None
                and 0 < o["F4_adc_det"]["leak_offset_v"] <= 0.4)),
    ("TMP117 首读 -256C", lambda o: o["F5_tmp117"]["first_read_after_reset_c"] == -256.0),
    ("TMP117 自热 < 0.1mW", lambda o: o["F5_tmp117"]["self_heat_uw"] < 100.0),
    ("CONN_USB 地脚数不合规", lambda o: o["F6_usb_hinge"]["gnd_rule_ok"] is False),
    ("FS 刷 90MB < 120s", lambda o: o["F6_usb_hinge"]["flash_s_at_FS"] < 120.0),
    ("HS 刷 90MB < 8s", lambda o: o["F6_usb_hinge"]["flash_s_at_HS"] < 8.0),
    ("0.05W -> 37.5C", lambda o: abs(o["F7_skin_tiers"]["p_to_tskin"]["0.05W"] - 37.5) < 0.1),
    ("0.16W -> 43.0C (红线)", lambda o: abs(o["F7_skin_tiers"]["p_to_tskin"]["0.16W"] - 43.0) < 0.1),
    # ★原版第 21 条写死 `"load_switch_in_netlist": False` 并把 `is False` 当 PASS 条件 ⇒ **假绿的根因**。
    #   现网表里 U_PWR_SW 确实存在 ⇒ 断言按**现网表实况**订正为 True, 并把位号钉死;
    #   它仍然绑在**网表实读值**上 (反向用例 REV-3 证明: 网表里删掉 U_PWR_SW ⇒ 这条立刻变红)。
    ("F8 负载开关按位号实读 (U_PWR_SW 在网表 ⇒ 旧'无硬件断电通路'结论已推翻)",
     lambda o: o["F8_power_off"]["load_switch_in_netlist"] is True
               and any(x in ("U_PWR_SW", "U_PWR_SW_1") for x in o["F8_power_off"]["load_switch_refs"])),
]


# --- 新增: 网表实读 / 锚点 / 反向用例 ---
def _mk_reverse(name, edits=None, drop=(), fn=None):
    """构造一条反向用例: 在**网表副本**上改坏输入 ⇒ 对应判据必须变红。"""
    def runner(o, nl=None):
        if nl is None:
            return False
        tmp = tempfile.mkdtemp(prefix="timing_rev_")
        try:
            if drop:
                path = drop_refs_copy(nl, os.path.join(tmp, "mutated.csv"), drop)
            else:
                path = mutated_copy(nl, os.path.join(tmp, "mutated.csv"), edits or [])
            mut = Netlist(path)
            mo = compute(mut)
            return bool(fn(o, mo))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return (name, runner)


def _mk_reverse_device_row(name, ref, fn):
    """★反向用例 (ISS-235): 在**网表副本**上只删掉某位号的**器件本体行** (引脚行留着)
    ⇒ 对应判据必须变红。

    ★模拟的缺陷 = 「该位号在网表里 (引脚行还在), 但**没有器件行** ⇒ BOM/装配单会漏掉它」。
    ★与 `_mk_reverse(drop=...)` 的区别: 后者把整颗器件删掉 ⇒ 这是另一种缺陷 (器件不在网表里)。
    """
    def runner(o, nl=None):
        if nl is None:
            return False
        tmp = tempfile.mkdtemp(prefix="timing_rev_devrow_")
        try:
            path = drop_device_rows_copy(nl, os.path.join(tmp, "mutated.csv"), ref)
            mut = Netlist(path)
            mo = compute(mut)
            return bool(fn(o, mo))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return (name, runner)


def _mk_reverse_dnp(name, targets, fn):
    """★反向用例 (行级): 把副本里某些行的 `dnp` 列改成 DNP ⇒ 对应判据必须变红。

    targets = [(net, ref), ...] —— 指网表里 (net 列, ref 列) 同时匹配的行。
    ★用途: 锁死【dnp 是行级】⇒ 改一行 ⇒ 只影响那一行, 不许拿错行。
    """
    def runner(o, nl=None):
        if nl is None:
            return False
        tset = set((net, nl.actual_ref(ref)) for net, ref in targets)   # ★ISS-321 · S1 位号改名适配★
        line_nos = [x["_line_no"] for x in nl.rows
                    if ((x.get("net") or ""), x.get("ref") or "") in tset]
        if not line_nos:
            return False
        tmp = tempfile.mkdtemp(prefix="timing_rev_dnp_")
        try:
            path = set_dnp_at_lines_copy(nl, os.path.join(tmp, "mutated.csv"), line_nos)
            mo = compute(Netlist(path))
            return bool(fn(o, mo))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return (name, runner)


def _mk_reverse_fs_3v3(name):
    """★★【ISS-291】反向用例: 把满量程常量 `V_DET_FS` 改回 3.3 (老口径) ⇒ 口径判据必须变红。

    ★**为什么要单独一种 runner**: 满量程不是网表里的量, 是脚本里的常量 ⇒
      改它必须改**常量本身** (而不是改网表副本) ⇒ ⇒ 造一个「临时改常量 → 重算 → 改回」的 runner。
    ★**自证「真改到了目标」**: mutant 的 `full_scale_v` 必须 = 3.3 (⇒ 真的改了),
      且 mutant 的漏电偏移 %FS 必须从 2.1 变成 1.1 (⇒ 真的换了口径),
      ★**同时**基线的那条判据必须是 True (⇒ 红的不是别的条)。
    """
    def runner(o, nl=None):
        if nl is None:
            return False
        old = DEVICE["V_DET_FS"]
        DEVICE["V_DET_FS"] = 3.3
        try:
            mo = compute(nl)
        finally:
            DEVICE["V_DET_FS"] = old
        return bool(
            _num_close(mo["F4_adc_det"]["full_scale_v"], 3.3, 1e-9)
            and _num_close(mo["F4_adc_det"]["lsb_mv"], 0.8057, 0.002)
            and _num_close(mo["F4_adc_det"]["leak_offset_pct_fs"], 1.1, 0.06)
            and _f4_adc_fs_caliber_ok(o) is True
            and _f4_adc_fs_caliber_ok(mo) is False)
    return (name, runner)


def _mk_reverse_chain_mode(name):
    """★★【ISS-291】反向用例: 把取链规则切回「元组第一条」(老错规则) ⇒ 判决对象判据必须变红。

    ★**为什么要单独一种 runner**: 取链规则是**代码里的分支**, 不是网表里的量 ⇒
      必须真的把 `CHAIN_SELECT_MODE` 切回老规则再重算 ⇒ 切完立刻改回 (不许留在老规则上)。
    ★**自证「真改到了目标」**: mutant 的 `active_chain` 必须 = VBUS_DET_D (⇒ 真的换回了错对象),
      ★**同时**基线的判决对象判据必须是 True (⇒ 红的不是别的条)。
    """
    def runner(o, nl=None):
        if nl is None:
            return False
        global CHAIN_SELECT_MODE
        old = CHAIN_SELECT_MODE
        CHAIN_SELECT_MODE = "tuple_order"
        try:
            mo = compute(nl)
        finally:
            CHAIN_SELECT_MODE = old
        return bool(
            mo["F4_adc_det"]["active_chain"] == "VBUS_DET_D"
            and mo["F4_adc_det"]["chain_select_mode"] == "tuple_order"
            and _f4_adc_object_ok(o) is True
            and _f4_adc_object_ok(mo) is False)
    return (name, runner)


def _rev_pg_and_any_row(o, nl=None):
    """★反向用例: 把 PG_AND 网上**任意一行** (当前必装) 改成 DNP ⇒ 对应判据必须变红。

    ★逐行试 (不跳行): 对 PG_AND 上当前 dnp=必装的每一行, 单独把它改成 DNP,
    断言 **该行对应的判据确实变红** (PG_AND 行的行级状态确实变了)。
    ★这条专门用来钉死【别再拿错行的 dnp】。
    """
    if nl is None:
        return False
    rows = [x for x in nl.rows if (x.get("net") or "") == "PG_AND" and x.get("dnp") == "必装"]
    if not rows:
        return False
    base_rows = o["F1_reset_rc"]["pg_and_state"]["rows"]
    tmp = tempfile.mkdtemp(prefix="timing_rev_pgand_")
    try:
        for x in rows:
            path = set_dnp_at_lines_copy(nl, os.path.join(tmp, "m.csv"), [x["_line_no"]])
            mo = compute(Netlist(path))
            if mo["F1_reset_rc"]["pg_and_state"]["rows"] == base_rows:
                return False                       # ★没变 ⇒ 这行根本没被读到 ⇒ 工具口径有问题★
            # ★ISS-321 · S1 位号改名适配: 两边都归一化回逻辑名★
            changed = [q for q in mo["F1_reset_rc"]["pg_and_state"]["rows"]
                       if q["ref"] == nl.logical_ref(x.get("ref", "")) and q["dnp"] == "DNP"]
            if not changed:
                return False
        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ----------------------------------------------------------------------------
# ★★【ISS-235】F8 两条目标判据 —— ★写成**具名函数**, 正向用例与反向用例**共用同一个函数** ★
#   ⇒ ★这样反向自证才敢叫「真的改到了目标」: 同一个判据函数, 在基线上 True、在突变体上 False ★
#   ⇒ ★**不许**把判据写成两套 (正向一套 / 反向另一套) ⇒ 那样「红」可能只是别的条红 (ISS-227 教训) ★
# ----------------------------------------------------------------------------
def _f8_all_load_switches_have_device_row(o: dict) -> bool:
    """F8 目标判据①: **每一颗**负载开关都必须有器件行 ⇒ BOM/装配单不许漏掉任何一颗。

    ★语义: 网表里认出来的每颗负载开关 (U_PWR_SW / U_EN_SW, 以及任何值里写明
      「负载开关/电源开关/load switch」而被兜底认出来的 IC) 都必须有**器件本体行**
      (type=IC/SW) ⇒ 否则 BOM/装配单里那颗开关会凭空消失 (只留引脚行 ⇒ 装配时拿不到器件)。
    ★**ISS-235**: ISS-233 落表 (2026-11-16 06:48:38) 给 U_EN_SW 补了器件本体行 (网表 L442)
      ⇒ 原断言「U_EN_SW 必须**没有**器件行」恒红 ⇒ 方向翻成这条【正面事实】(★判据更强★)。
    """
    f8 = o["F8_power_off"]
    return (f8["load_switch_without_device_row"] == []
            and any(x in ("U_PWR_SW", "U_PWR_SW_1") for x in f8["load_switch_refs"])
            and any(x in ("U_EN_SW", "U_EN_SW_1") for x in f8["load_switch_refs"]))


def _f8_rail_switching_count_is(o: dict, n: int) -> bool:
    """F8 目标判据②: 装机负载开关数 == n (★基线 = 2: U_PWR_SW + U_EN_SW 两颗都必装★)。

    ★**ISS-235**: ISS-233 给 U_EN_SW 补了器件本体行 (dnp=必装) ⇒ 基线由 1 变 2
      ⇒ 反向用例 REV-3 删掉 U_PWR_SW 后必须掉到 **1 (不是 0)**。
    """
    return o["F8_power_off"]["rail_switching_devices"] == n



# ===================================================================== F4' / BAT_DET 口径 (ISS-285)
# ★★【ISS-285 · 2026-11-17 · sw-lead】★★ BAT_DET 三颗的期望值随 V-3=E 落表翻了:
#   ★旧期望 (落表前): 「BAT_DET 三颗全 DNP」⇒ 落表后【过期】⇒ 红 ★
#   ★新期望 (落表后): 「BAT_DET 三颗必装」★ (证据 = HW/netlist_v1.csv L182/L183/L184 + 落表台账 §16 老板凭据)
#   ★**判据强度不许比原来弱**: 原来判「三颗**没有**装机」(一个负面事实),
#     现在判「三颗**逐颗**按【器件本体行】都是必装」(全集正面事实 + 三颗都必须在场) ⇒ **更强** ★
#   ★**逐颗读【器件本体行】的 dnp**, 不读该位号第一条行 (ISS-190 的老教训: dnp 是行级, 拿错行 = 假绿) ★
BAT_DET_REFS = ("R_BAT_DET_1", "R_BAT_DET_2", "C_DET_BAT")


def _bat_det_all_populated(o: dict) -> bool:
    """BAT_DET 三颗 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 逐颗【器件本体行】必装?"""
    chains = [c for c in (o.get("F4_adc_det") or {}).get("chains") or [] if c.get("tag") == "BAT_DET"]
    if len(chains) != 1:
        return False
    dev = chains[0].get("device_dnp") or {}
    if set(dev) != set(BAT_DET_REFS):
        return False
    for ref in BAT_DET_REFS:
        rows = dev.get(ref) or []
        if not rows or not all(d == "必装" for d in rows):
            return False
    return True


def _bat_det_verdict(det_chains: list) -> str:
    """BAT_DET 链的现状一句话 (★数据驱动 ⇒ 网表翻回 DNP 时老话自动回来★)。"""
    bat = [c for c in det_chains or [] if c.get("tag") == "BAT_DET"]
    if not bat:
        return "★BAT_DET 链在网表里查不到"
    c = bat[0]
    if not c.get("device_populated"):
        return ("★BAT_DET 链 (R_BAT_DET_1/2 + C_DET_BAT) 三颗**全是 DNP** ⇒ "
                "**电量检测分压在现网表上不存在**")
    return ("★BAT_DET 链 (R_BAT_DET_1/2 + C_DET_BAT) 三颗**已改成必装** (V-3=E 落表后) ⇒ "
            "**电量检测分压在现网表上存在** (100k+60k+100nF ⇒ R_th=%sΩ / τ=%sms)"
            % (c.get("rth_ohm"), c.get("tau_ms")))


# ----------------------------------------------------------------------------
# ★★【ISS-291 · 2026-11-17 · sw-lead】★★ 口径同源自证 + 数字检测输入口径
# ----------------------------------------------------------------------------
def _bat_det_note_facts(nl) -> dict:
    """★从网表 BAT_DET 链的 note 里抽【官方口径的三个数】⇒ 与闸算出来的数逐字对账。

    ★网表 L182 note 逐字: 「[BAT_DET_RAW] 分压上臂 (100k); ★方案E (ISS-223 §11.4):
      R_th=37.5kΩ ⇒ ADC 输入漏电 ~1µA 只造成 37.5mV 偏移 (2.1% FS, 可软件标定)★」
    ⇒ ★这三个数 (37.5kΩ / 37.5mV / 2.1% FS) 是**网表侧写死的** ⇒ 闸算出来必须对上,
      对上才叫「口径同源」 (★ISS-291: 老闸算的是 500kΩ / 0.50V / 15.2% ⇒ 差 7 倍 ⇒ 两源不一致★)。
    """
    out = {"pct_fs": None, "mv": None, "rth_k": None, "note": "", "line_no": 0}
    for x in (nl.rows_of("R_BAT_DET_1") or []):
        note = x.get("note", "") or ""
        if "%FS" in note or "mV" in note:
            out["note"] = note
            out["line_no"] = x.get("_line_no", 0)
            break
    note = out["note"]
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*%\s*FS", note)
    if m:
        out["pct_fs"] = float(m.group(1))
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*mV", note)
    if m:
        out["mv"] = float(m.group(1))
    m = re.search(r"R_th\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*k", note)
    if m:
        out["rth_k"] = float(m.group(1))
    return out


def _f4d_usb_det(nl, det_chains: list, dig_chains: list) -> dict:
    """★★【ISS-291】数字检测输入口径 (USB2 OTG 插入检测) 的判据 ★★

    ★**为什么必须另立口径**: VBUS_DET_D 链的落点是 pin100 = USB_DRD1_VBUSDET
      = USB OTG 插入检测**数字**脚 (脚表 vol 栏 = —— ⇒ IO 域未知) ⇒ ★**不是 SAR-ADC**★
      ⇒ 拿 SAR-ADC 的「建立时间 / 漏电偏移 / 满量程」去判它 = ★判错了对象★。
    ★**判据三项 (任务书 §B1-3)**:
      ① 常开静态电流 (代价项, 上限取同板 BAT_DET 链 V-3 已裁决的 26.25µA)
      ② 节点电平 (识别高电平阈值 2.3V / 标称高电平带 2.7~3.3V, 官方 = Forlinx 手册)
      ③ 该脚 abs-max (脚表域栏 = —— ⇒ [0数据] ⇒ 降级取手册高电平带上沿 3.3V)
    ★**未决项不许藏**: 手册只对 USB_DRD0_VBUSDET 明写内部 40kΩ 下拉, 本板用的是 DRD1
      ⇒ [0数据] ⇒ 两种情形都算出来报出 (理想 2.5V / 含内部下拉 0.185V) ⇒ 登记 need。
    """
    ch = (dig_chains or [c for c in (det_chains or []) if c.get("tag") == "VBUS_DET_D"])[0] \
        if (dig_chains or [c for c in (det_chains or []) if c.get("tag") == "VBUS_DET_D"]) else None
    if ch is None:
        return {"chain": "(未找到)", "criteria": {"all_ok": False},
                "verdict": "★网表里找不到 VBUS_DET_D 链 ⇒ fail-closed★"}
    rt, rb = ch["r_top_ohm"], ch["r_bot_ohm"]
    v_nom = DEVICE["USB_VBUS_NOM_V"]
    v_min, v_max = DEVICE["USB_VBUS_MIN_V"], DEVICE["USB_VBUS_MAX_V"]
    pd = DEVICE["USB_VBUSDET_INTERNAL_PD_OHM"]
    r_gnd_pd = (rb * pd) / (rb + pd) if (rb and pd) else None
    node_nom = v_nom * (rb / (rt + rb)) if (rt and rb) else None
    node_min = v_min * (rb / (rt + rb)) if (rt and rb) else None
    node_max = v_max * (rb / (rt + rb)) if (rt and rb) else None
    node_pd = v_nom * (r_gnd_pd / (rt + r_gnd_pd)) if (r_gnd_pd and rt) else None
    i_ideal = v_nom / (rt + rb) * 1e6 if (rt and rb) else None
    i_worst = v_nom / (rt + r_gnd_pd) * 1e6 if (r_gnd_pd and rt) else None
    vih = DEVICE["USB_VBUSDET_VIH_MIN_V"]
    hi_lo, hi_hi = DEVICE["USB_VBUSDET_HI_LO_V"], DEVICE["USB_VBUSDET_HI_HI_V"]
    # abs-max: 脚表域栏已知 ⇒ 域电压 +0.3V (datasheet L2489 "DVDD+0.3"); 未知 ⇒ 降级取手册高电平带上沿
    domain_known = bool(ch.get("pin_vol_v"))
    abs_max = (ch["pin_vol_v"] + 0.3) if domain_known else hi_hi
    static_ok = bool(i_worst is not None and i_worst <= DEVICE["DET_CHAIN_STATIC_MAX_UA"])
    level_ok = bool(node_min is not None and node_min > vih and node_max <= abs_max)
    margin_v = (node_min - vih) if node_min is not None else None
    unresolved = [
        {"item": "该脚 (USB_DRD1_VBUSDET) 是否带内部 40kΩ 下拉",
         "evidence": "[0数据] Forlinx FET3572 手册只对 USB_DRD0_VBUSDET 明写 'internal 40 kΩ pull-down'; "
                     "本板落点是 DRD1 ⇒ 手册未记载",
         "impact": ("若带 ⇒ 节点 = %.3fV (含 40kΩ 下拉) < %.1fV 识别阈值 ⇒ **USB 插入检测永不触发**"
                    % (node_pd if node_pd is not None else float("nan"), vih)),
         "degradation": "本闸按【无内部下拉】的理想分压值判定 (并把含下拉的情形一并算出报出); "
                        "★该脚 abs-max / 域 / 内部下拉三件事一律登记 need, 不在本闸里编数★"},
        {"item": "该脚 IO 域 / abs-max (脚表 vol 栏 = ——)",
         "evidence": "[0数据] 脚表 FET3572C_PIN_TABLE.csv L101 vol 栏 = '——' ⇒ 域未知",
         "impact": ("本闸降级取 Forlinx 手册标称高电平带上沿 %.1fV 作 abs-max 上界 ⇒ 节点 %.3fV ≤ %.1fV ⇒ 通过; "
                    "★若该脚域实为 1.8V ⇒ abs-max = 2.1V ⇒ 节点 %.3fV 越限 ⇒ 必须改分压比★"
                    % (hi_hi, node_max if node_max is not None else float("nan"), hi_hi,
                       node_max if node_max is not None else float("nan"))),
         "degradation": "降级上界取手册高电平带上沿; ★域一旦在脚表里填上, 本闸的 abs-max 判据自动按域+0.3V 生效★"},
        {"item": "识别裕量 (VBUS 下限 4.75V 时)",
         "evidence": "[官方] USB 2.0/Type-C VBUS 4.75~5.25V + 手册识别阈值 >2.3V",
         "impact": ("节点 @4.75V = %.3fV, 距阈值 %.1fV 只剩 %.0fmV (%.1f%%) ⇒ 裕量极薄"
                    % (node_min if node_min is not None else float("nan"), vih,
                       (margin_v * 1e3) if margin_v is not None else float("nan"),
                       (margin_v / vih * 100) if margin_v is not None else float("nan"))),
         "degradation": "本闸按最坏 VBUS 下限 4.75V 判 (比标称 5V 更严)"},
    ]
    return {
        "chain": ch["tag"],
        "landing_net": ch["landing_net"],
        "landing_line": ch["landing_line"],
        "som_conn": ch["som_conn"],
        "som_pin": ch["som_pin"],
        "pin_signal": ch["pin_signal"],
        "pin_vol_raw": ch["pin_vol_raw"],
        "pin_class": ch["pin_class"],
        "r_top_ohm": rt, "r_bot_ohm": rb, "c_f": ch["c_f"],
        "rth_ohm": ch["rth_ohm"],
        "v_supply_nom_v": v_nom, "v_supply_min_v": v_min, "v_supply_max_v": v_max,
        "static_current_ua": r(i_worst, 2) if i_worst is not None else None,
        "static_current_ua_ideal": r(i_ideal, 2) if i_ideal is not None else None,
        "static_current_limit_ua": DEVICE["DET_CHAIN_STATIC_MAX_UA"],
        "node_v_nom": r(node_nom, 3) if node_nom is not None else None,
        "node_v_min": r(node_min, 3) if node_min is not None else None,
        "node_v_max": r(node_max, 3) if node_max is not None else None,
        "node_v_with_internal_pd": r(node_pd, 3) if node_pd is not None else None,
        "vih_min_v": vih,
        "high_band_lo_v": hi_lo, "high_band_hi_v": hi_hi,
        "margin_to_vih_mv": r(margin_v * 1e3, 1) if margin_v is not None else None,
        "abs_max_v": abs_max,
        "abs_max_source": ("脚表域 %s +0.3V" % ch["pin_vol_raw"]) if domain_known else
                          "★[0数据] 降级取 Forlinx 手册标称高电平带上沿 %.1fV★" % hi_hi,
        "domain_known": domain_known,
        "criteria": {
            "static_current_ok": static_ok,
            "level_ok": level_ok,
            "all_ok": bool(static_ok and level_ok),
        },
        "unresolved": unresolved,
        "verdict": (
            "★%s 链落点 = %s pin%s = %s (脚表域栏 = %s ⇒ %s) ⇒ 按【数字检测输入】口径判 (★不是 SAR-ADC★): "
            "① 常开静态电流 %sµA (理想分压 %sµA) ≤ 上限 %sµA (同板 BAT_DET 链 V-3 已裁决值) ⇒ %s; "
            "② 节点电平 %sV @5V (VBUS 4.75~5.25V ⇒ %s~%sV) vs 识别阈值 >%sV ⇒ %s (裕量 %smV ⚠; 且低于手册标称高电平带下沿 %sV ⚠); "
            "③ 该脚 abs-max %s ⇒ %s; "
            "★★未决 (已登记 need, 不阻塞本闸但禁止据此判『安全』): 该脚是否带内部 40kΩ 下拉 [0数据] ⇒ 若带则节点 %sV ⇒ **USB 插入检测不工作**★★"
            % (ch["tag"], ch["som_conn"], ch["som_pin"], ch["pin_signal"], ch["pin_vol_raw"] or "——",
               "域已知" if domain_known else "域未知 [0数据]",
               r(i_worst, 2) if i_worst is not None else "-",
               r(i_ideal, 2) if i_ideal is not None else "-",
               DEVICE["DET_CHAIN_STATIC_MAX_UA"], "✔" if static_ok else "❌",
               r(node_nom, 3) if node_nom is not None else "-",
               r(node_min, 3) if node_min is not None else "-",
               r(node_max, 3) if node_max is not None else "-",
               vih, "✔" if (node_min is not None and node_min > vih) else "❌",
               r(margin_v * 1e3, 1) if margin_v is not None else "-",
               hi_lo,
               r(abs_max, 2), ("✔" if (node_max is not None and node_max <= abs_max) else "❌"),
               r(node_pd, 3) if node_pd is not None else "-")),
    }


# ----------------------------------------------------------------------------
# ★★【ISS-291】具名判据函数 (★正向用例与反向用例**共用同一个函数**⇒ 反向自证敢叫「真改到了目标」★)
#   ★同 ISS-235/ISS-285 的写法: 判据不许写两套 (正向一套 / 反向另一套)
#     ⇒ 那样「红」可能只是别的条红 (ISS-227 教训) ★
# ----------------------------------------------------------------------------
def _num_close(v, target, tol=1e-9):
    """None-safe 数值比较 (★测点缺失 ⇒ 判红, 不许抛异常★)。"""
    try:
        if v is None:
            return False
        return abs(float(v) - float(target)) <= tol
    except (TypeError, ValueError):
        return False


def _f4_adc_object_ok(o: dict) -> bool:
    """F4 判决对象判据: active_chain 必须 = 唯一一条落在 SAR-ADC 脚上的装机链 (BAT_DET / pin38)。"""
    f4 = (o.get("F4_adc_det") or {})
    c = f4.get("criteria") or {}
    return bool(c.get("object_ok")) and f4.get("active_chain") == "BAT_DET" \
        and f4.get("active_chain_pin") == "38" \
        and f4.get("active_chain_signal") == "SARADC_VIN5"


def _f4_adc_fs_caliber_ok(o: dict) -> bool:
    """F4 满量程口径判据: FS = 1.8V 且三个数与网表 L182 note 逐字对上 (37.5kΩ / 37.5mV / 2.1% FS)。"""
    return bool(((o.get("F4_adc_det") or {}).get("criteria") or {}).get("fs_caliber_ok"))


def _f4_adc_settle_ok(o: dict) -> bool:
    """F4 建立时间判据: 12bit 到半 LSB 的建立时间 ≤ 300ms (★阈值沿用, 不许调松★)。"""
    return bool(((o.get("F4_adc_det") or {}).get("criteria") or {}).get("settle_ok"))


def _f4_adc_leak_ok(o: dict) -> bool:
    """F4 漏电偏移判据: 输入漏电造成的偏移 ≤ 0.4V (★阈值沿用, 不许调松★)。"""
    return bool(((o.get("F4_adc_det") or {}).get("criteria") or {}).get("leak_ok"))


def _f4_adc_node_ok(o: dict) -> bool:
    """F4 过压判据: ADC 节点 ≤ abs-max 1.98V 且 ≤ 标称域 1.8V (1.8V 域口径)。"""
    return bool(((o.get("F4_adc_det") or {}).get("criteria") or {}).get("node_ok"))


def _f4_adc_populated_ok(o: dict) -> bool:
    """F4 输入不许悬空判据: ADC 链三颗必须装机 (否则 ADC 输入悬空 ⇒ 读数随机)。"""
    return bool(((o.get("F4_adc_det") or {}).get("criteria") or {}).get("populated_ok"))


def _f4d_static_ok(o: dict) -> bool:
    """F4D 数字链静态电流判据: 常开静态电流 ≤ 同板 BAT_DET 链 V-3 已裁决的 26.25µA。"""
    return bool(((o.get("F4D_usb_vbus_det") or {}).get("criteria") or {}).get("static_current_ok"))


def _f4d_level_ok(o: dict) -> bool:
    """F4D 数字链节点电平判据: @VBUS 下限 4.75V 仍 > 识别阈值 2.3V, 且 ≤ abs-max 上界。"""
    return bool(((o.get("F4D_usb_vbus_det") or {}).get("criteria") or {}).get("level_ok"))


NEW_TESTS = [
    ("网表锚点: md5 与行数可复算 (data_rows = lines_total - 1)",
     lambda o: o["NETLIST_ANCHOR"]["netlist_data_rows"] == o["NETLIST_ANCHOR"]["netlist_lines_total"] - 1),
    ("网表锚点: 现行网表 = 513 数据行 (行数不许变)",
     lambda o: o["NETLIST_ANCHOR"]["netlist_data_rows"] == 513),
    # ★★【ISS-225 重锚】原断言 = 「现行网表 md5 == c78f9912…」(硬编码一个落表前的旧值)
    #   ⇒ ISS-220 落表把它改成 13f59a43… ⇒ **这条恒红** ⇒ ★**不许只追一次 md5** ⇒
    #   ★**改成台账驱动**: ① 现行网表的 md5 必须是落表台账登记过的两个状态之一 (落表前/落表后)
    #     ② 锚点 ↔ 落表台账 ↔ 盘上真源三方对账必须成立 (不许悄悄换真源)
    ("网表锚点: 现行网表 md5 ∈ 落表台账登记的状态 (落表前 / 落表后)",
     lambda o: netlist_md5_allowed(o["NETLIST_ANCHOR"]["netlist_md5"])),
    ("网表锚点: 锚点 ↔ 落表台账 ↔ 盘上真源 三方对账成立 (不许悄悄换真源)",
     lambda o: netlist_baseline_ok()),
    ("F1 实读: R_PU_RESET_N=10k / R_SER_RESET_N=1k / C_RST=100nF",
     lambda o: o["F1_reset_rc"]["r_pull_ohm"] == 10000
               and o["F1_reset_rc"]["r_ser_ohm"] == 1000
               and abs(o["F1_reset_rc"]["c_rst_f"] - 1e-7) < 1e-12),
    ("F1 实读: τ 注记是从网表 note 里读出来的 100ms (不是手抄)",
     lambda o: o["F1_reset_rc"]["netlist_annotation_ms"] == 100.0),
    ("F1 复评: PG 已进复位链 (Q_AND + R_PG_PULL 10k)",
     lambda o: o["F1_reset_rc"]["q_and_in_netlist"] is True
               and o["F1_reset_rc"]["pg_pullup_ohm"] == 10000),
    ("★F1 实读: PG 源 dnp 必须按【PG_AND 那一行】取 ⇒ U_DCDC_VCORE / U_DCDC_VIO 都是必装 (★dnp_of(ref) 拿的是器件级 DNP ⇒ 错一格★)",
     lambda o: o["F1_reset_rc"]["pg_source_devices"]["U_DCDC_VCORE"]["dnp"] == "必装"
               and o["F1_reset_rc"]["pg_source_devices"]["U_DCDC_VIO"]["dnp"] == "必装"
               and o["F1_reset_rc"]["pg_source_devices"]["U_DCDC_VCORE"]["populated"] is True
               and o["F1_reset_rc"]["pg_source_devices"]["U_DCDC_VIO"]["populated"] is True),
    ("★F1 实读: PG_AND 上真正 DNP 的是 Q_ENVC (行级) ⇒ 复位链 P0 的真归因 (★不是『PG 源 DNP』★)",
     lambda o: o["F1_reset_rc"]["pg_and_state"]["dnp_rows"] == ["Q_ENVC"]
               and o["F1_reset_rc"]["pg_and_state"]["q_envc_row_dnp"] == "DNP"
               and o["F1_reset_rc"]["pg_and_state"]["pg_sources_all_populated"] is True
               and o["F1_reset_rc"]["pg_and_state"]["pullup_row_dnp"] == "必装"
               and o["F1_reset_rc"]["pg_and_state"]["q_and_gate_row_dnp"] == "必装"),
    ("★F1 实读: RESET_N 上谁在拉 —— Q_AND 必装 / SW_RST 必装 / U_SUPV pin1 DNP (它不参与拉复位)",
     lambda o: o["F1_reset_rc"]["reset_n_state"]["q_and_drain_row_dnp"] == "必装"
               and o["F1_reset_rc"]["reset_n_state"]["sw_rst_row_dnp"] == "必装"
               and o["F1_reset_rc"]["reset_n_state"]["u_supv_pin1_row_dnp"] == "DNP"
               and "U_SUPV" in o["F1_reset_rc"]["reset_n_state"]["dnp_rows"]),
    ("F3 实读: I2C_A 上拉 = 2.2k → 1.8V 域 (ISS-153 订正)",
     lambda o: o["F3_i2c_rise"]["buses"]["I2C_A"]["pullup_ohm"] == 2200
               and o["F3_i2c_rise"]["buses"]["I2C_A"]["pullup_rail_v"] == 1.8),
    ("F3 实读: I2C_B 上拉 = 4.7k → 3.3V 域",
     lambda o: o["F3_i2c_rise"]["buses"]["I2C_B"]["pullup_ohm"] == 4700
               and o["F3_i2c_rise"]["buses"]["I2C_B"]["pullup_rail_v"] == 3.3),
    ("F3 复评: I2C_A @300pF = 559ns ≤ 1000ns ⇒ 标准模式**通过** (旧结论已翻转)",
     lambda o: o["F3_i2c_rise"]["buses"]["I2C_A"]["tr_ns_vs_cable_cap"]["300pF"] <= 1000.0
               and o["F3_i2c_rise"]["buses"]["I2C_A"]["std_mode_ok_at_300pF"] is True),
    ("F3 复评: I2C_B @300pF = 1194ns > 1000ns ⇒ 标准模式**不通过** (最差总线)",
     lambda o: o["F3_i2c_rise"]["buses"]["I2C_B"]["tr_ns_vs_cable_cap"]["300pF"] > 1000.0
               and o["F3_i2c_rise"]["worst_bus"] == "I2C_B"),
    # ★★【ISS-225 重锚】原断言 = 「网表自带的 t_r 注记 2380ns 仍在 (⇒ 网表侧矛盾)」
    #   ⇒ ISS-220 d6 真把注记改成 186ns (与 2.2k 实算一致) ⇒ **那条矛盾不存在了** ⇒
    #   ★**这不是把红灯调没, 是网表侧那盏灯被真修好了** (留痕: SW/SW_MD5_BASELINE_LEDGER.md §3 R-02)
    ("F3 实读: 网表自带的 t_r 注记 186ns (ISS-220 d6 已把 I2C_A 改成 2.2k@1.8V ⇒ 注记与实算一致, 网表侧矛盾已消除)",
     lambda o: o["F3_i2c_rise"]["netlist_annotation_ns"] == 186.0
               and o["F3_i2c_rise"]["buses"]["I2C_A"]["annotation_stale"] is False),
    ("F4 实读: EN/SS/CT/MR 行数 = 10/0/1/0 (合计 11 行, CT 属 DNP 器件)",
     lambda o: o["F4_ctrl_pins"]["counts"] == {"EN": 10, "SS": 0, "CT": 1, "MR": 0}
               and o["F4_ctrl_pins"]["total_rows"] == 11),
    ("F4 实读: LDO 的 EN 直连 RAIL_BOARD_5V (永远使能)",
     lambda o: any(c["signal"] == "EN" and "LDO" in c["ref"] and "RAIL_BOARD_5V" in (c["node2"] or "")
                   for c in o["F4_ctrl_pins"]["rows"])),
    ("F4 实读: U_SUPV 是 DNP ⇒ 监督器支路实物不存在",
     lambda o: o["F2_supervisor"]["u_supv_populated"] is False
               and o["F2_supervisor"]["u_supv_dnp"] == "DNP"),
    ("F5 实读: RESET_N / BOOT_N 上拉都挂 RAIL_VDD_1V8_IO (1.8V)",
     lambda o: o["F5_pullup_rail"]["reset_pullup_rail"] == "RAIL_VDD_1V8_IO"
               and o["F5_pullup_rail"]["boot_pullup_rail"] == "RAIL_VDD_1V8_IO"
               and o["F5_pullup_rail"]["reset_pullup_rail_v"] == 1.8),
    ("F5 实读: TMP117 现在挂在 I2C_B (旧文档写 I2C_A)",
     lambda o: o["F5_tmp117"]["i2c_bus"] == "I2C_B"),
    ("F6 实读: 跨铰链 J_CHG 不带 USB D+/D− ⇒ 跨铰链 USB 链不成立",
     lambda o: o["F6_usb_hinge"]["cross_hinge_usb_data_path"] is False),
    ("F6 实读: demo 板板内 Type-C → SoC USB 路径存在 (J_USB_C → 串阻 → J_SOM)",
     lambda o: len(o["F6_usb_hinge"]["onboard_usb_rows"]) > 0),
    ("F8 实读: 负载开关 = U_PWR_SW / U_EN_SW, 且 ON 脚有 10k 下拉 (默认关)",
     lambda o: any(x in ("U_PWR_SW", "U_PWR_SW_1") for x in o["F8_power_off"]["load_switch_refs"])
               and any(x in ("U_EN_SW", "U_EN_SW_1") for x in o["F8_power_off"]["load_switch_refs"])
               and o["F8_power_off"]["on_pin_pulldown_ohm"] == 10000),
    # ★★【ISS-235 订正 (2026-11-16, sw-lead)】★★
    #   ★**原断言 = 「U_EN_SW 在网表里**没有器件行**」** ⇒ 那是 **ISS-233 落表之前**的旧事实
    #     (2026-11-16 06:48:38, hw-lead 落表第 3 批: 网表 **L442** 一行给 U_EN_SW 补了器件本体行,
    #      type NET→IC ⇒ BOM L208 / 脚表 L531 同步) ⇒ **这条恒红** ★
    #   ⇒ ★**判据方向翻过来**: 现在断言的是【正向事实】=「**每一颗**负载开关都必须有器件行」
    #     ⇒ 语义 = 「BOM/装配单不许漏掉任何一颗负载开关」
    #   ⇒ ★**判据强度不许比原来弱**: 原来判「U_EN_SW 必须**没有**器件行」(一个具体位号的负面事实),
    #     现在判「**一颗都不许没有**器件行」(全集正面事实 + 两个位号都必须在场) ⇒ **更强** ★
    #   ⇒ ★**判据绑在【网表实读值】上** (反向用例 REV-3c 证明: 删掉 U_EN_SW 的器件本体行 ⇒ 这条立刻变红) ★
    ("★F8 实读: 负载开关 U_PWR_SW / U_EN_SW **都必须有器件行** (BOM/装配单不许漏掉任何一颗负载开关)",
     lambda o: _f8_all_load_switches_have_device_row(o)),
    # ★★【ISS-291 · 2026-11-17 · sw-lead】★★ 判决对象改对: ADC 链 = **落在 SAR-ADC 脚上的那条**
    #   = BAT_DET (网表 L186 ⇒ J_SOM_P1 pin38 = SARADC_VIN5, 1.8V 域)
    #   ★老断言「ADC 装机链是 VBUS_DET_D」= **判错了对象** (VBUS_DET_D 落点 pin100 = USB 数字脚) ⇒ 作废 ★
    ("F4' 实读: ADC 判决对象 = BAT_DET 链 (落点 J_SOM_P1 pin38 = SARADC_VIN5, 1.8V 域); BAT_DET 三颗必装",
     lambda o: _f4_adc_object_ok(o) and _bat_det_all_populated(o)),
    # ★★【ISS-291】满量程口径: 1.8V 域 (官方 datasheet) ⇒ LSB = 0.439mV ★
    ("F4 实读: 满量程 = 1.8V 域 (官方) ⇒ 12bit LSB = 0.439mV (★老口径 3.3V ⇒ 0.806mV 已作废★)",
     lambda o: abs(o["F4_adc_det"]["full_scale_v"] - 1.8) < 1e-9
               and abs(o["F4_adc_det"]["lsb_mv"] - 0.4395) < 0.002),
    # ★★【ISS-291】口径同源自证: 三个数与网表 L182 note 逐字对上 (37.5kΩ / 37.5mV / 2.1% FS) ★
    ("F4 实读: 漏电偏移 37.5mV = 2.1% FS ⇒ 与网表 L182 note 写死的数**逐字对上** (口径同源)",
     lambda o: (_num_close(o["F4_adc_det"]["leak_offset_pct_fs"], 2.1, 0.06)
                and _num_close(o["F4_adc_det"]["leak_offset_v"] * 1e3
                                if o["F4_adc_det"]["leak_offset_v"] is not None else None, 37.5, 0.6)
                and _num_close((o["F4_adc_det"]["rth_ohm"] or 0) / 1e3, 37.5, 0.6))),
    # ★★【ISS-291】判决源必须是脚表 (signal 列), 不是元组顺序 ★
    ("F4 实读: 判决源 = SoM 脚表 signal 列 (落点判 SAR-ADC), 取链模式 = by_landing_pin",
     lambda o: o["F4_adc_det"]["judgment_source"].startswith("SoM 脚表")
               and o["F4_adc_det"]["chain_select_mode"] == "by_landing_pin"
               and o["F4_adc_det"]["active_chain_pin"] == "38"),
    # ★★【ISS-291】ADC 链 @4.2V 节点 1.575V ≤ abs-max 1.98V (1.8V 域) ★
    ("F4 实读: ADC 节点 @4.2V = 1.575V ≤ abs-max 1.98V (FS 利用率 87.5%)",
     lambda o: (_num_close(o["F4_adc_det"]["node_v_at_supply"], 1.575, 0.01)
                and o["F4_adc_det"]["node_max_abs_v"] == 1.98
                and _num_close(o["F4_adc_det"]["fs_utilization_pct"], 87.5, 0.2))),
    # ★★【ISS-291】数字链 (VBUS_DET_D) 落点 = pin100 USB_DRD1_VBUSDET = 数字脚 (不是 ADC) ★
    ("F4D 实读: VBUS_DET_D 落点 = J_SOM_P1 pin100 = USB_DRD1_VBUSDET (数字脚 ⇒ 不进 ADC 判据)",
     lambda o: o["F4D_usb_vbus_det"]["som_pin"] == "100"
               and o["F4D_usb_vbus_det"]["pin_signal"] == "USB_DRD1_VBUSDET"
               and o["F4D_usb_vbus_det"]["pin_class"] == "DIGITAL"),
    # ★★【ISS-291】数字链静态电流判据 (上限 = 同板 BAT_DET 链 V-3 已裁决的 26.25µA) ★
    ("F4D 实读: 数字链常开静态电流 4.81µA (含内部 40kΩ 降级) ≤ 26.25µA 上限",
     lambda o: (_num_close(o["F4D_usb_vbus_det"]["static_current_ua"], 4.81, 0.05)
                and _f4d_static_ok(o))),
    # ★★【ISS-291】数字链节点电平判据 + 未决项必须报出来 (不许藏) ★
    ("F4D 实读: 数字链节点 2.5V > 识别阈值 2.3V, 且内部下拉/域/裕量三条未决项都报出",
     lambda o: (_num_close(o["F4D_usb_vbus_det"]["node_v_nom"], 2.5, 0.01)
                and o["F4D_usb_vbus_det"]["vih_min_v"] == 2.3
                and _f4d_level_ok(o)
                and len(o["F4D_usb_vbus_det"]["unresolved"]) >= 3)),
]

# --- 反向用例 (★核心新增: 改坏网表 ⇒ 判据必须变红) ---
REV_TESTS = [
    _mk_reverse(
        "REV-1 反向: 把 I2C_A 上拉改成 10k ⇒ I2C_A @300pF 判据必须变红 (>1000ns)",
        edits=[("R_PU_I2CA_SCL", "10k ±1%"), ("R_PU_I2CA_SDA", "10k ±1%")],
        fn=lambda o, mo: (mo["F3_i2c_rise"]["buses"]["I2C_A"]["tr_ns_vs_cable_cap"]["300pF"] > 1000.0
                          and mo["F3_i2c_rise"]["buses"]["I2C_A"]["std_mode_ok_at_300pF"] is False
                          and mo["F3_i2c_rise"]["buses"]["I2C_A"]["tr_ns_at_100pF"]
                          != o["F3_i2c_rise"]["buses"]["I2C_A"]["tr_ns_at_100pF"])),
    _mk_reverse(
        "REV-2 反向: 把 I2C_A 上拉改成 4.7k ⇒ t_r@100pF 必须回到 398ns (旧文档那个数)",
        edits=[("R_PU_I2CA_SCL", "4.7k ±1%"), ("R_PU_I2CA_SDA", "4.7k ±1%")],
        fn=lambda o, mo: abs(mo["F3_i2c_rise"]["buses"]["I2C_A"]["tr_ns_at_100pF"] - 398.0) < 1.0),
    # ★★【ISS-235 订正 (2026-11-16, sw-lead)】★★
    #   ★**基线 1 → 2**: ISS-233 落表给 U_EN_SW 补了器件本体行 (type=IC · dnp=必装) ⇒
    #     网表里现在 **两颗**负载开关都装机 ⇒ `rail_switching_devices` 基线 = **2** (不是 1) ★
    #   ⇒ 删掉 U_PWR_SW 后开关数必须掉到 **1 (不是 0)** ⇒ ★**REV-3b (两个都删 ⇒ 0) 不受影响** ★
    #   ⇒ ★**反向自证自带「我确实改到了目标」**: 第 1 条 (U_PWR_SW 不在 mutant 的 load_switch_refs 里)
    #     证明突变真的落到了那颗开关上; 第 3/4 条证明【目标判据】在 mutant 上红、在基线上绿 ★
    _mk_reverse(
        "REV-3 反向: 从网表里删掉 U_PWR_SW ⇒ 装机开关数必须从 2 掉到 1 (★不是 0★ · 断电主开关没了)",
        drop=("U_PWR_SW",),
        fn=lambda o, mo: not any(x in ("U_PWR_SW", "U_PWR_SW_1") for x in mo["F8_power_off"]["load_switch_refs"])
                          and mo["F8_power_off"]["rail_switching_devices"] == 1
                          and not _f8_rail_switching_count_is(mo, 2)
                          and _f8_rail_switching_count_is(o, 2)),
    # ★★【ISS-235 新增】F8 那条翻正后的判据的专属反向用例 ★★
    #   ★**突变 = 只删掉 U_EN_SW 的【器件本体行】(type=IC)**, 引脚行 (type=NET) 留着 ★★
    #     ⇒ 模拟的正是「BOM/装配单里那颗开关只有引脚行、没有器件行 ⇒ BOM 会漏掉它」
    #   ⇒ ★**自证「我确实改到了目标」**: mutant 里 `load_switch_without_device_row == ["U_EN_SW"]`
    #     (⇒ 真的只剩引脚行) 且 U_EN_SW **仍在** load_switch_refs 里 (⇒ 位号还在网表上, 不是被整颗删了) ★
    #   ⇒ ★**红的是【目标那条判据】**: `_f8_all_load_switches_have_device_row(mutant) == False`
    #     而基线 `_f8_all_load_switches_have_device_row(base) == True` ⇒ **同一个函数** 判定 ⇒ 不是别的条红 ★
    _mk_reverse_device_row(
        "REV-3c 反向: 把 U_EN_SW 的**器件本体行**删掉 (只留引脚行) ⇒ F8『不许漏掉任何一颗负载开关』必须变红",
        ref="U_EN_SW",
        fn=lambda o, mo: (mo["F8_power_off"]["load_switch_without_device_row"] in (["U_EN_SW"], ["U_EN_SW_1"])
                          and any(x in ("U_EN_SW", "U_EN_SW_1") for x in mo["F8_power_off"]["load_switch_refs"])
                          and not _f8_all_load_switches_have_device_row(mo)
                          and _f8_all_load_switches_have_device_row(o))),
    _mk_reverse(
        "REV-3b 反向: 把 U_PWR_SW 与 U_EN_SW 都删掉 ⇒ F8『硬件断电通路存在』必须变红",
        drop=("U_PWR_SW", "U_EN_SW"),
        fn=lambda o, mo: mo["F8_power_off"]["load_switch_in_netlist"] is False
                          and mo["F8_power_off"]["rail_switching_devices"] == 0
                          and o["F8_power_off"]["load_switch_in_netlist"] is True),
    _mk_reverse(
        "REV-4 反向: 把 R_PU_RESET_N 改成 20k ⇒ 复位释放 tau 必须变成 2.1ms",
        edits=[("R_PU_RESET_N", "20k ±1%")],
        fn=lambda o, mo: abs(mo["F1_reset_rc"]["tau_release_ms"] - 2.1) < 0.01),
    _mk_reverse(
        "REV-5 反向: 把 C_RST 改成 10nF ⇒ 复位释放 tau 必须变成 0.11ms",
        edits=[("C_RST", "10nF ±10%")],
        fn=lambda o, mo: abs(mo["F1_reset_rc"]["tau_release_ms"] - 0.11) < 0.005),
    _mk_reverse(
        "REV-6 反向: 把 R_PU_I2CB_SCL 改成 1k ⇒ I2C_B 必须变成最差总线之外的合格总线 (t_r 掉到 85ns)",
        edits=[("R_PU_I2CB_SCL", "1k ±1%"), ("R_PU_I2CB_SDA", "1k ±1%")],
        fn=lambda o, mo: abs(mo["F3_i2c_rise"]["buses"]["I2C_B"]["tr_ns_at_100pF"] - 84.7) < 1.0
                          and mo["F3_i2c_rise"]["worst_bus"] == "I2C_A"),
    _mk_reverse_dnp(
        "REV-7 反向: 把 PG_AND 上的 NET_PG_AND 汇总行改成 DNP ⇒ PG 源判据必须变红 (★锁死'别再拿错行的 dnp'★)",
        targets=[("PG_AND", "NET_PG_AND")],
        fn=lambda o, mo: (mo["F1_reset_rc"]["pg_source_devices"]["U_DCDC_VCORE"]["dnp"] == "DNP"
                          and mo["F1_reset_rc"]["pg_source_devices"]["U_DCDC_VIO"]["dnp"] == "DNP"
                          and mo["F1_reset_rc"]["pg_and_state"]["pg_sources_all_populated"] is False
                          and o["F1_reset_rc"]["pg_and_state"]["pg_sources_all_populated"] is True
                          and mo["F1_reset_rc"]["pg_and_state"]["dnp_rows"] != o["F1_reset_rc"]["pg_and_state"]["dnp_rows"])),
    _mk_reverse_dnp(
        "REV-8 反向: 把 PG_AND 上 Q_AND 那行改成 DNP ⇒ 栅极接在 PG_AND 上的 Q_AND 判据必须变红",
        targets=[("PG_AND", "Q_AND")],
        fn=lambda o, mo: (mo["F1_reset_rc"]["pg_and_state"]["q_and_gate_row_dnp"] == "DNP"
                          and o["F1_reset_rc"]["pg_and_state"]["q_and_gate_row_dnp"] == "必装")),
    _mk_reverse_dnp(
        "REV-9 反向: 把 PG_AND 上 R_PG_PULL 那行改成 DNP ⇒ 10k 上拉判据必须变红",
        targets=[("PG_AND", "R_PG_PULL")],
        fn=lambda o, mo: (mo["F1_reset_rc"]["pg_and_state"]["pullup_row_dnp"] == "DNP"
                          and o["F1_reset_rc"]["pg_and_state"]["pullup_row_dnp"] == "必装")),
    ("REV-10 反向: 把 PG_AND 网上**任意一行**改成 DNP ⇒ 对应判据必须变红 (逐行试, 不跳行)",
     _rev_pg_and_any_row),
    # ★★【ISS-285】F4' 期望值随落表翻了 ⇒ 必须有反向用例锁死「改回 DNP ⇒ 变红」 ★★
    _mk_reverse_dnp(
        "REV-11 反向: 把 BAT_DET 三颗 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 改回 DNP ⇒ "
        "F4'『BAT_DET 三颗必装』必须变红",
        targets=[("BAT", "R_BAT_DET_1"), ("BAT_DET", "R_BAT_DET_2"),
                 ("BAT_DET", "C_DET_BAT"), ("GND", "C_DET_BAT")],
        fn=lambda o, mo: (_bat_det_all_populated(o) is True
                          and _bat_det_all_populated(mo) is False)),
    # ★★★【ISS-291 · 2026-11-17 · sw-lead】反向用例组 ★★★
    #   ★**背景**: F4 原先同时犯了两个错 (判决对象错 + 满量程口径错) ⇒ 这一组 6 条把两个错各锁死一次 ★
    _mk_reverse_fs_3v3(
        "REV-12 反向: 把满量程 V_DET_FS 改回 3.3 (老口径) ⇒ 满量程/口径同源判据必须变红",
    ),
    _mk_reverse_chain_mode(
        "REV-13 反向: 把取链规则改回「元组第一条」⇒ 判决对象判据必须变红 (不许悄悄换回错对象)",
    ),
    _mk_reverse_dnp(
        "REV-14 反向: 把 BAT_DET 三颗 (R_BAT_DET_1 / R_BAT_DET_2 / C_DET_BAT) 改回 DNP ⇒ "
        "「ADC 输入悬空」判据必须变红",
        targets=[("BAT", "R_BAT_DET_1"), ("BAT_DET", "R_BAT_DET_2"),
                 ("BAT_DET", "C_DET_BAT"), ("GND", "C_DET_BAT")],
        fn=lambda o, mo: (_f4_adc_populated_ok(o) is True
                          and _f4_adc_populated_ok(mo) is False
                          and mo["F4_adc_det"]["active_chain"] == "(无: fail-closed)")),
    _mk_reverse(
        "REV-15 反向: 把 BAT_DET 的下臂 60k 改成 100k ⇒ @4.2V 节点 2.1V > 1.98V abs-max ⇒ "
        "过压判据必须变红",
        edits=[("R_BAT_DET_2", "100k ±1%")],
        fn=lambda o, mo: (_num_close(mo["F4_adc_det"]["node_v_at_supply"], 2.1, 0.01)
                          and _f4_adc_node_ok(o) is True
                          and _f4_adc_node_ok(mo) is False)),
    _mk_reverse(
        "REV-16 反向: 把 VBUS_DET_D 链的两颗电阻改成 10k/10k ⇒ 数字链静态电流判据必须变红 "
        "(★数字脚口径也在判, 不是只判 ADC★)",
        edits=[("R_VBUS_DET_D1", "10k ±1%"), ("R_VBUS_DET_D2", "10k ±1%")],
        fn=lambda o, mo: (_f4d_static_ok(o) is True
                          and _f4d_static_ok(mo) is False
                          and mo["F4D_usb_vbus_det"]["static_current_ua"] > 250.0)),
    _mk_reverse(
        "REV-17 反向: 把 VBUS_DET_D 的上臂 1M 改成 10M ⇒ 节点 0.45V < 2.3V 识别阈值 ⇒ "
        "数字链节点电平判据必须变红",
        edits=[("R_VBUS_DET_D1", "10M ±1%")],
        fn=lambda o, mo: (_f4d_level_ok(o) is True
                          and _f4d_level_ok(mo) is False
                          and mo["F4D_usb_vbus_det"]["node_v_nom"] < 1.0)),
]


# --- ISP 段判据用例 (★ISS-210: 正向 + ★反向: 超 15.10 ms 必被抓★) ---
def _isp(meas):
    return isp_budget_verdict(meas)


ISP_TESTS = [
    ("ISP 模式A 生死线 = 15.10 ms (ISS-124 发布值, 不许调松)",
     lambda o: isp_budget_verdict()["criteria"]["limit_mode_a_ms"] == 15.10),
    ("ISP 模式B 上限 = 17.33 ms (ISS-124 发布值)",
     lambda o: isp_budget_verdict()["criteria"]["limit_mode_b_p95_ms"] == 17.33),
    ("ISP 精确反解线 = 15.095 ms (json 口径, 与发布线差 0.005 ms)",
     lambda o: abs(isp_budget_verdict()["criteria"]["limit_mode_a_exact_ms"] - 15.095) < 0.001),
    ("ISP 现占位 8.00 ms 的余量 = +7.09 ms (精确 7.095) / +9.33 ms",
     lambda o: (abs(isp_budget_verdict()["criteria"]["headroom_now_mode_a_ms"] - 7.095) < 0.001
                and isp_budget_verdict()["criteria"]["headroom_now_mode_a_doc"] == "7.09"
                and abs(isp_budget_verdict()["criteria"]["headroom_now_mode_b_ms"] - 9.33) < 1e-9)),
    ("模型复现: X=8.00 ms 时模式A e2e = 52.91 ms (与 HW/e2e_budget_rk3572.py 同源)",
     lambda o: abs((ISP_BUDGET["T_FIXED_ms"] - ISP_BUDGET["S3_now_ms"]) + ISP_BUDGET["S3_now_ms"]
                   + ISP_BUDGET["S5_ms"] + ISP_BUDGET["POST_MS"] - 52.905) < 0.001),
    ("★反向: ISP avg = 15.11 ms ⇒ 必须 FAIL (超 15.10 必被抓) 且给出差值",
     lambda o: _isp({"avg_total_ms": 15.11, "avg_hw_ms": 12.0, "n": 300})["verdict"] == "FAIL"
               and _isp({"avg_total_ms": 15.11, "avg_hw_ms": 12.0, "n": 300})["margin_ms"] < 0),
    ("ISP avg = 15.10 ms ⇒ PASS (恰好在生死线上)",
     lambda o: _isp({"avg_total_ms": 15.10, "avg_hw_ms": 12.0, "n": 300})["verdict_latency"] == "PASS"),
    ("ISP avg = 8.00 ms (现占位) ⇒ PASS + 余量 +7.09 ms",
     lambda o: _isp({"avg_total_ms": 8.0, "avg_hw_ms": 7.0, "n": 300})["verdict"] == "PASS"
               and abs(_isp({"avg_total_ms": 8.0, "avg_hw_ms": 7.0, "n": 300})["margin_ms"] - 7.10) < 0.001),
    ("★反向: 无实测输入 ⇒ INDET + [0数据] (不许假装测过)",
     lambda o: _isp(None)["verdict"] == "INDET" and _isp(None)["evidence"] == "[0数据]"),
    ("★反向: 只报 SDK 总耗时、缺纯硬件耗时 ⇒ 不许静默 PASS (⇒ INDET + 理由)",
     lambda o: (_isp({"avg_total_ms": 8.0, "n": 300})["report_complete"] is False
                and _isp({"avg_total_ms": 8.0, "n": 300})["verdict"] == "INDET"
                and "纯硬件" in _isp({"avg_total_ms": 8.0, "n": 300})["reason"])),
    ("★反向: 采样帧数 n=120 < 300 ⇒ 不作结论 (INDET)",
     lambda o: _isp({"avg_total_ms": 8.0, "avg_hw_ms": 7.0, "n": 120})["verdict"] == "INDET"),
    ("ISP p95 = 18.00 ms ⇒ 模式B 上限 (17.33) FAIL",
     lambda o: _isp({"avg_total_ms": 8.0, "avg_hw_ms": 7.0, "p95_total_ms": 18.0, "n": 300})
               ["p95_mode_b_verdict"] == "FAIL"),
    ("T2 交叉核对: 纯 NPU 21.00 ms ⇒ 命中老板翻案条款 (20.33 ms)",
     lambda o: _isp({"avg_total_ms": 8.0, "avg_hw_ms": 7.0, "n": 300, "npu_ms": 21.0})
               ["t2_flip_check"]["verdict"].startswith("FAIL")),
]


def run_selftests(o: dict, nl: Netlist):
    """→ (通过数, 总数, 逐条 (名字, ok))"""
    results = []
    for name, fn in SELF_TESTS_LEGACY:
        try:
            ok = bool(fn(o))
        except Exception as e:  # noqa: BLE001
            ok = False
            name += "  [EXC %s]" % e
        results.append((name, ok))
    for name, fn in NEW_TESTS:
        try:
            ok = bool(fn(o))
        except Exception as e:  # noqa: BLE001
            ok = False
            name += "  [EXC %s]" % e
        results.append((name, ok))
    for name, fn in REV_TESTS:
        try:
            ok = bool(fn(o, nl))
        except Exception as e:  # noqa: BLE001
            ok = False
            name += "  [EXC %s]" % e
        results.append((name, ok))
    for name, fn in ISP_TESTS:
        try:
            ok = bool(fn(o))
        except Exception as e:  # noqa: BLE001
            ok = False
            name += "  [EXC %s]" % e
        results.append((name, ok))
    passed = len([1 for _n, ok in results if ok])
    return passed, len(results), results


def reverse_demo(nl: Netlist) -> int:
    """★当场演示: 改坏网表副本 ⇒ 对应判据变红。"""
    base = compute(nl)
    tmp = tempfile.mkdtemp(prefix="timing_demo_")
    try:
        print("=== 反向用例演示 (改坏网表**副本**, 原网表只读不动) ===")
        print("基线: I2C_A 上拉 = %s → %s (%.1fV 域), t_r@100pF = %s ns, @300pF = %s ns, 标准模式 %s"
              % (base["F3_i2c_rise"]["buses"]["I2C_A"]["pullup_ohm"],
                 base["F3_i2c_rise"]["buses"]["I2C_A"]["pullup_rail"],
                 base["F3_i2c_rise"]["buses"]["I2C_A"]["pullup_rail_v"],
                 base["F3_i2c_rise"]["buses"]["I2C_A"]["tr_ns_at_100pF"],
                 base["F3_i2c_rise"]["buses"]["I2C_A"]["tr_ns_vs_cable_cap"]["300pF"],
                 "✅通过" if base["F3_i2c_rise"]["buses"]["I2C_A"]["std_mode_ok_at_300pF"] else "❌不通过"))
        path = mutated_copy(nl, os.path.join(tmp, "mut.csv"),
                            [("R_PU_I2CA_SCL", "10k ±1%"), ("R_PU_I2CA_SDA", "10k ±1%%")])
        mut = compute(Netlist(path))
        m = mut["F3_i2c_rise"]["buses"]["I2C_A"]
        print("改坏: R_PU_I2CA_SCL 2.2k → 10k (副本)")
        print("改后: t_r@100pF = %s ns, @300pF = %s ns, 标准模式 %s"
              % (m["tr_ns_at_100pF"], m["tr_ns_vs_cable_cap"]["300pF"],
                 "✅通过" if m["std_mode_ok_at_300pF"] else "❌不通过 (变红)"))
        path2 = drop_refs_copy(nl, os.path.join(tmp, "mut2.csv"), ("U_PWR_SW",))
        mut2 = compute(Netlist(path2))
        print("改坏: 从副本里删掉 U_PWR_SW 全部行")
        # ★★【ISS-248 订正 (2026-11-16, sw-lead)】★★ 演示段口径对齐 REV-3 (权威判据, L1573~L1576):
        #   基线 = 2 颗负载开关 (U_PWR_SW + U_EN_SW) ⇒ 删掉 U_PWR_SW 后 `rail_switching_devices` 掉到
        #   **1 (不是 0)** ⇒ 本演示的「变红」判红值 = **1** (★REV-3b 两颗都删 ⇒ 0, 不受影响★)
        print("改后: 装机开关数 rail_switching_devices = %s (基线 %s) ⇒ 断电主开关判据 %s; "
              "load_switch_refs = %s"
              % (mut2["F8_power_off"]["rail_switching_devices"],
                 base["F8_power_off"]["rail_switching_devices"],
                 "❌变红" if mut2["F8_power_off"]["rail_switching_devices"] == 1 else "未变红",
                 mut2["F8_power_off"]["load_switch_refs"]))
        path3 = drop_refs_copy(nl, os.path.join(tmp, "mut3.csv"), ("U_PWR_SW", "U_EN_SW"))
        mut3 = compute(Netlist(path3))
        print("改坏: 再把 U_EN_SW 也删掉")
        print("改后: F8 load_switch_in_netlist = %s (基线 %s) ⇒ 『硬件断电通路存在』判据 %s"
              % (mut3["F8_power_off"]["load_switch_in_netlist"],
                 base["F8_power_off"]["load_switch_in_netlist"],
                 "❌变红" if mut3["F8_power_off"]["load_switch_in_netlist"] is False else "未变红"))
        # ★行级 dnp 演示 (ISS-190 订正: dnp 是行级, 改一行只影响那一行)
        pg_line = [x["_line_no"] for x in nl.rows
                   if (x.get("net") or "") == "PG_AND" and (x.get("ref") or "") == "NET_PG_AND"]
        path4 = set_dnp_at_lines_copy(nl, os.path.join(tmp, "mut4.csv"), pg_line)
        mut4 = compute(Netlist(path4))
        print("改坏: 把 PG_AND 上 NET_PG_AND 那一行的 dnp 改成 DNP (副本)")
        print("改后: pg_source_devices = %s (基线 %s) ⇒ PG 源判据 %s"
              % (mut4["F1_reset_rc"]["pg_source_devices"],
                 base["F1_reset_rc"]["pg_source_devices"],
                 "❌变红" if mut4["F1_reset_rc"]["pg_and_state"]["pg_sources_all_populated"] is False else "未变红"))
        # ★★【ISS-248 订正 (2026-11-16, sw-lead)】★★ 同上: 聚合判据与 REV-3 对齐 (掉到 1 才算「变红」)
        ok = (m["std_mode_ok_at_300pF"] is False
              and mut2["F8_power_off"]["rail_switching_devices"] == 1
              and mut3["F8_power_off"]["load_switch_in_netlist"] is False
              and mut4["F1_reset_rc"]["pg_and_state"]["pg_sources_all_populated"] is False)
        print("\n反向演示: %s" % ("✅ 变红 ⇒ 它真在读网表 (不是演常量)" if ok else "❌ 没变红 ⇒ 有问题"))
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--netlist", default=DEFAULT_NETLIST, help="网表路径 (默认 HW/netlist_v1.csv)")
    ap.add_argument("--reverse-demo", action="store_true", help="只跑反向用例演示")
    ap.add_argument("--only", action="append", default=[], metavar="KEY",
                    help="只打印某个结论段 (可重复), 例如 --only F1_reset_rc --only F3_i2c_rise")
    # ★ISS-210: 板端 ISP 段实测输入 (无输入 ⇒ verdict=INDET + [0数据])
    ap.add_argument("--isp-csv", default=None,
                    help="板端 ISP 段 CSV (SW/DEMO_OD_TIMING_SPEC.md §3.4 格式: ts_isp_in/ts_isp_hw_start/ts_isp_out)")
    ap.add_argument("--isp-avg-ms", type=float, default=None,
                    help="板端实测: ISP 段管线可见 (SDK 总耗时) 平均值 ms")
    ap.add_argument("--isp-hw-avg-ms", type=float, default=None,
                    help="板端实测: ISP 段纯硬件耗时平均值 ms (归因用; 必须另外报)")
    ap.add_argument("--isp-p95-ms", type=float, default=None,
                    help="板端实测: ISP 段管线可见 p95 ms (模式B 上限 17.33 ms)")
    ap.add_argument("--isp-frames", type=int, default=None,
                    help="板端实测: 采样帧数 (n < 300 ⇒ 不作结论)")
    ap.add_argument("--npu-ms", type=float, default=None,
                    help="板端实测: 纯 NPU 耗时 ms (交叉核对 T2 翻案条款 20.33 ms)")
    args = ap.parse_args()

    if not os.path.exists(args.netlist):
        print("[FATAL] 网表不存在: %s" % args.netlist, file=sys.stderr)
        return 2
    nl = Netlist(args.netlist)
    if args.reverse_demo:
        return reverse_demo(nl)

    # ★ISS-210: 汇总板端 ISP 段实测输入 (CSV 优先, 命令行可覆盖单值)
    isp_meas = {}
    if args.isp_csv:
        if not os.path.exists(args.isp_csv):
            print("[FATAL] ISP CSV 不存在: %s" % args.isp_csv, file=sys.stderr)
            return 2
        isp_meas.update(read_isp_csv(args.isp_csv))
    if args.isp_avg_ms is not None:
        isp_meas["avg_total_ms"] = args.isp_avg_ms
    if args.isp_hw_avg_ms is not None:
        isp_meas["avg_hw_ms"] = args.isp_hw_avg_ms
    if args.isp_p95_ms is not None:
        isp_meas["p95_total_ms"] = args.isp_p95_ms
    if args.isp_frames is not None:
        isp_meas["n"] = args.isp_frames
    if args.npu_ms is not None:
        isp_meas["npu_ms"] = args.npu_ms
    if not isp_meas:
        isp_meas = None

    o = compute(nl, isp_meas=isp_meas)

    # ★--only: 只打印指定结论段 (★复现命令里最省事的一条, 不需要管道★)
    if args.only:
        unknown = [k for k in args.only if k not in o]
        if unknown:
            print("[FATAL] 未知结论段: %s (可选: %s)" % (", ".join(unknown), ", ".join(o.keys())),
                  file=sys.stderr)
            return 2
        for k in args.only:
            print("=== %s ===" % k)
            for kk, vv in o[k].items():
                print("   %-34s : %s" % (kk, vv))
            print()
        print("=== NETLIST_ANCHOR ===")
        for kk, vv in o["NETLIST_ANCHOR"].items():
            print("   %-34s : %s" % (kk, vv))
        return 0

    passed, total, results = run_selftests(o, nl)

    if args.json:
        o["_selftest"] = {"passed": passed, "total": total,
                          "items": [{"name": n, "ok": ok} for n, ok in results]}
        print(json.dumps(o, ensure_ascii=False, indent=2, default=str))
        return 0 if passed == total else 1

    for k, v in o.items():
        print("=== %s ===" % k)
        for kk, vv in v.items():
            print("   %-34s : %s" % (kk, vv))
        print()

    print("=== 器件级常数与来源 ===")
    for k in sorted(DEVICE):
        print("   %-34s : %-14s  %s" % (k, DEVICE[k], SOURCES.get(k, "(网表实读, 无需器件常数)")))
    print()

    print("=== SELF-TEST (%d 项: 既有 %d + 新增 %d + 反向 %d + ISP %d) ==="
          % (total, len(SELF_TESTS_LEGACY), len(NEW_TESTS), len(REV_TESTS), len(ISP_TESTS)))
    for name, ok in results:
        print("  [%s] %s" % ("PASS" if ok else "FAIL", name))
    print("\nSELFTEST %d/%d 通过, rc=%d" % (passed, total, 1 if passed != total else 0))
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
