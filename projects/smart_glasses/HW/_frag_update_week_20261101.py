#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_frag_update_week_20261101.py —— 2026-11-01 周更新窗口的分片原子写

--------------------------------------------------------------------------------
为什么用 Python API 而不是纯 CLI:
  CLI 的 --add-*/--set 只支持**追加**与**整段替换**, 本单还需要两件 CLI 做不到的事:
    ① **清重复 key 的过期条目** (interface_claims 里 battery_capacity_tier 有 2 条:
       旧值 无桥接340-575mAh/有桥接575-675mAh 与 新值 315/387 —— merge.py 取最后一条,
       但旧条目留在文件里就是"过期值", 别人 grep 到会当真的)
    ② **给 23 条没有 due 的 needs_from 补 due** (窗口纪律: 新加的需求 due 必填 ⇒ 历史欠账也补齐)
  原子写仍由 state/frag_write.py 的 update_fragment() 负责 (tmp + fsync + os.replace),
  与 CLI 走**同一条路径** —— 照抄 MECH/_frag_update_iss092.py 的写法。

边界: 只改**自己的**分片 state/fragments/hw.yaml。不碰别人的分片 / STATE.yaml /
      PROJECT_TRACKER.md / issue_log.yaml (issue_log 走 state/_hw_week_iss.py 单独原子写)。

用法: python3 HW/_frag_update_week_20261101.py [--dry-run]
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment  # noqa: E402

# ================================================================= 1. claims 订正
# ★ 全部写清 旧值 → 新值 (合并器不会替我纠错)
CLAIM_FIX = {
    "pcb_outline": (
        "60x30mm",
        "★2026-11-01 订正: 旧值 60x15mm → 新值 60x30mm。依据 老板 10-29 19:16 拍板『板宽可以放到 30mm 以内』"
        " (PROJECT_TRACKER §0 板宽行, 11-01 20:5x 台账订正) ⇒ 60x30=1800mm²。"
        "★ISS-118 机械判定: RK3588 在 60x30 下缺 497.3mm² 装不下, RK3576 余 122.3mm² 装得下。"
        "★板长 60mm 不变; 骨架/石墨上限仍 = PCB 段后缘 X=60.00。",
        "HW/PCB_FIXING_PINSET2.md#1 + PROJECT_TRACKER.md#0",
    ),
    "pcb_width_recommend": (
        "30mm",
        "★2026-11-01 订正: 旧值 15mm → 新值 30mm (老板 10-29 19:16 拍板)。"
        "★注意: 板宽 30 只指镜脚主 PCB, 充电板在镜框 (ISS-014 决策 5) ⇒ 放宽板宽**不解**充电板 14.60mm² 面积缺口。",
        "PROJECT_TRACKER.md#0 (板宽行) + HW/pcb60x30_check.json",
    ),
    "pcb_mount_holes_xy": (
        "P1(8,15)P2(52,15)S1(8,10)S2(52,20)",
        "★2026-11-01 订正: 旧值 P1(8,7.5)P2(52,7.5)S1(8,2.5)S2(52,12.5) → 新值按 **60x30mm 板宽**把 Y 向平移 "
        "(旧中心 7.50 → 新中心 15.00, S 孔 ±5.00 不变)。X 向与孔位窗口 X[4,12]+X[46,56] 不变。"
        "★与 SoC 逃线带 X[20.20,31.80] 的 2D 重叠 = 0.000mm² (复算: python3 HW/hw_week_20261101_check.py §1)。",
        "HW/hw_week_20261101_check.py#sec1",
    ),
    "chg_input_limit": (
        "0.82-1.00A",
        "★2026-11-01 二次订正: 旧值 1.00A/0.82A/0.411A (300Ω→390Ω 换算时用了**反向**公式) → 新值 **0.82-1.00A** "
        "(R_ILIM=390Ω 的 IINMAX, 三档 KILIM=320/355/390 AΩ)。★**ICHG 不是 IIN**: buck 功率守恒 ICHG=η·Vbus/Vbat·IIN "
        "= **1.2162×IIN** (旧式 0.8222× 是它的倒数) ⇒ 电池侧电流见 chg_ichg_at_rilim, 单 pin 见 chg_single_pin_a。",
        "HW/CHARGE_CURRENT_RECHECK_2026-11-01.md#2",
    ),
    "chg_single_pin_a": (
        "0.50-0.61A",
        "★2026-11-01 二次订正: 旧值 0.411A → 新值 **0.50-0.61A** (390Ω 档 ICHG 1.00-1.22A ÷ 双 pin)。"
        "⇒ **390Ω 档判 FAIL**: 0.608A > 0.5mm pitch ZIF 触点 0.5A 额定 (余量 0.82×)。"
        "★建议 R_ILIM 退 **680Ω** (单 pin 0.349A / 余量 1.43×, 换料不换板) —— 裁决权在 boss, 见 chg_rilim_recommended。",
        "HW/calc_chg_ichg.py + HW/CHARGE_CURRENT_RECHECK_2026-11-01.md#2",
    ),
}

CLAIM_NEW = [
    {
        "key": "chg_ichg_at_rilim",
        "value": "1.00-1.22A",
        "note": "★新增 (2026-11-01): R_ILIM=390Ω 时的**电池充电电流** ICHG = η·(Vbus/Vbat)·IIN = 1.2162×IIN ⇒ "
                "0.998-1.216A。★铰链里流的是 ICHG 不是 IIN ⇒ 铰链载流核算必须用这个数。",
        "ref": "HW/calc_chg_ichg.py §ratio",
    },
    {
        "key": "chg_rilim_recommended",
        "value": "680Ω",
        "note": "★新增 (2026-11-01) 建议值: 现行 390Ω 档单 pin 0.608A 超 0.5A 触点天花板 ⇒ 建议退到 680Ω "
                "(IINMAX 0.471-0.574A / ICHG 0.572-0.698A / 单 pin 0.349A / 触点余量 1.43× / 铰链余量 2.15× / "
                "充电 420mAh CC≈36min)。★若电芯规格书确认 ≤1C 则须退到 1.2kΩ (0.94C)。★**裁决权在 boss**, "
                "网表/BOM 未改 (不在本单边界)。",
        "ref": "HW/CHARGE_CURRENT_RECHECK_2026-11-01.md#2.3",
    },
    {
        "key": "chg_status_readback",
        "value": "CHG_STAT+VBUS_DET",
        "note": "★新增 (2026-11-01, ISS-043): 充电状态读取 = 双通路 —— ① CHG_STAT (BQ25896 STAT 开漏, 10k 上拉到 "
                "VDD_3V3_IO, → J_CHG pin5 → SoC GPIO, 低=充电中) ② VBUS_DET (1M+1M 分压 + 100nF → J_CHG pin7 → "
                "SoC ADC)。两路都在网表里 ⇒ ISS-043『未确认』前提不成立 ⇒ M-CHRG 门禁硬件上可实现。",
        "ref": "HW/CHARGE_STATUS_READBACK.md#B1 + HW/netlist_v1.csv P2 行 159-173",
    },
    {
        "key": "chg_status_gate_logic",
        "value": "OR(CHG_STAT_low,VBUS>thr)",
        "note": "★新增 (2026-11-01): 门禁判据必须是 **OR** 而不是单看 CHG_STAT —— 开漏线断线会读到『高=未充电』, "
                "单用一条通路会在断线时放开禁 OD (皮肤侧 75.1°C 风险)。两条都断 ⇒ 开机自检判『未知态』 ⇒ 默认禁 OD "
                "(fail-closed)。★I2C 跨铰链是 DNP ⇒ 读不到充电 IC 寄存器 ⇒ 门禁不依赖 I2C。",
        "ref": "HW/CHARGE_STATUS_READBACK.md#3.1",
    },
    {
        "key": "chg_vbus_det_rc",
        "value": "50ms(1M)/3.2ms(100k47k)",
        "note": "★新增 (2026-11-01): VBUS_DET 分压 RC —— 现状 1M‖1M=500kΩ ×100nF ⇒ τ=50ms (95%≈150ms), "
                "慢; 建议改 100k/47k (Rth=32.0kΩ ⇒ τ=3.2ms, 5V→1.60V) ⇒ 换料不换板。★与 sw-lead 9 项请求 P1-8 同向。",
        "ref": "HW/CHARGE_STATUS_READBACK.md#B6 + HW/netlist_v1.csv P2 行 159-164",
    },
    {
        "key": "evt_reliability_test_items",
        "value": "37项/6类",
        "note": "★新增 (2026-11-01, ISS-111): EVT 可靠性实测项清单 37 项 (跌落 9 / 振动 5 / 弯折 6 / 热 5 / 焊点 6 / "
                "连接器寿命 6), 每项含 测什么/怎么测/量化判据/不过回退/状态 五字段。★全部状态 = [未验] (无样机)。",
        "ref": "HW/EVT_RELIABILITY_TEST_ITEMS.md#B4",
    },
    {
        "key": "evt_xray_sampling",
        "value": "1块板/3位置+1切片",
        "note": "★新增 (2026-11-01): 跌落后 X-ray 抽样口径订正 —— 旧口径『抽检 3 块板』不成立 (1 台样机只有 1 块主板), "
                "改为**同一块板 3 个位置 (FCCSP/BTB/电感) + 1 处切片**, 抽样量按**位置**计; 判据 空洞率≤25% 不变。",
        "ref": "HW/EVT_RELIABILITY_TEST_ITEMS.md#4.1 R-D-06",
    },
    {
        "key": "soic_pkg_notes_20261101",
        "value": "ARS45已停/RK3576基线",
        "note": "★新增 (2026-11-01) 口径声明: 11-01 20:5x 基线已换 **瑞芯微 RK3576** (ARS45/酷芯微路线 10-29 19:20 起作废)。"
                "⇒ 所有 ARS45 专属 claim (fccsp_pitch_min / soc_pkg_balls_* / soc_pin_budget_* / mipi_csi_lanes / "
                "bridge_chip_spec / vendor_* 系列) **仅作历史口径保留**, 换芯重画时全部要换。"
                "★同时暴露新硬冲突: RK3576 逃线需 9 层 ⇒ 破 §0 『4-6 层』锁死 (ISS-122), 比选型更靠前。",
        "ref": "PROJECT_TRACKER.md#0 (主控基线行, 11-01 20:5x)",
    },
]

# ================================================================= 2. answers
ANSWERS = [
    # ---- to sw-lead ----
    {
        "key": "fw_boot_storage_bom",
        "to": "sw-lead",
        "value": "64MB SPI-NOR 装不下 (分区表 90MB) ⇒ 必须 ≥128MB, 路线选 **eMMC 5.1 / ePoP** (不是 NOR)。"
                "★量产眼镜印证: 小米 AI 眼镜用 Kingston **ePoP** 存储 (52audio 拆解) ⇒ 方向一致。"
                "ARS45 侧仍按『无内置 boot storage』设计 (外挂), 脚号 TBD-06/11。"
                "★板宽已放宽到 30mm ⇒ 挂 eMMC 的面积压力解除 (旧账: 12→15mm 要 +25%)。",
        "ref": "HW/ONLINE_INTEL_2026-10-26.md#B3-2 + HW/netlist_v1.csv P3 行 185-190",
    },
    {
        "key": "fw_boot_mode_hw",
        "to": "sw-lead",
        "value": "BOOT 走**独立通路** (J_BOOT1 焊盘 + R_SER_SPI_* 0Ω 串阻位, P3 行 186-190), **不复用侧键** (售后长按3s=版本号/"
                "长按10s=关机, 复用会误触进 BOOT 变砖) —— 采纳你的建议。"
                "HW-22 预留位数: 至少 2 个按键焊盘 + 1-2 个 LED 焊盘 + 各电源轨/关键信号测试点 (HARDWARE_BREAKDOWN §1.5)。"
                "★BOOT/RESET 测试点已留 (TP_BOOT)。",
        "ref": "HW/HARDWARE_BREAKDOWN.md#1.5(HW-21/HW-22) + HW/netlist_v1.csv P3 行 186-190",
    },
    {
        "key": "sw_reset_hw_changes",
        "to": "sw-lead",
        "value": "9 项逐条现状 (按网表 grep 口径): **P0-1 已做** (Q_AND N-MOS 硬件 AND, P8 行 62) · "
                "**P0-3 已做** (U_SUPV CT 补上, 行 72) · **P1-4 未做** (CONN_USB 仍 4p D+/D-/GND/预留 ⇒ 要 pin4 改 GND) · "
                "**P1-5 部分** (充电板侧有 D_ESD_TC, 主板侧有 D_ESD_USB 行 442-443; Type-C 侧位置按 ≤3mm 落) · "
                "**P1-7 已做** (J_BOOT1 + 0Ω 位) · **P1-8 未做** (VBUS_DET 仍 1M+1M ⇒ 本周已出同向建议 100k/47k, 见 "
                "HW/CHARGE_STATUS_READBACK.md) · **P0-2/P1-6/P1-9 待排期** (U_SUPV 分压仍 [待选型]/TBD-12; USB pogo 未加; "
                "U_TEMP TMP117 有器件但缺物理测点 note)。★改网表要动 state/gen_netlist.py ⇒ 不在硬件总工本单边界, 已列 needs 给项目总工。",
        "ref": "HW/netlist_v1.csv P8 行 62/72 + HW/CHARGE_STATUS_READBACK.md#B1-4",
    },
    {
        "key": "sw_poweroff_gpio_pin",
        "to": "sw-lead",
        "value": "① 脚号: 网表仍是 **TBD-01** (SoC 未定脚) ⇒ 11-01 基线换 RK3576 后随换芯一次性重映射, 不单独投板费。"
                "② 关机瞬间动作: SoC 把 PWR_CTRL GPIO 写**高阻** → 负载开关 ON 脚掉回 **10k 下拉** → 开关关 → SoC 断电 ⇒ "
                "**状态自动保持** (不用 SR 锁存)。关机时**充电板仍有电** (电池在镜脚, SYS 未接) ⇒ 关机也能充电。"
                "③ 通知充电板的通路: **无** ⇒ SW 不做该动作, 充电灯是充电板本地硬件行为 (NMOS 读 STAT)。"
                "★关机 = 负载开关断 SYS, 不是 SoC 自己睡。",
        "ref": "HW/POWER_SHUTDOWN_V3.md#3 (§3 表格 关机动作行)",
    },
    # ---- to mech-lead ----
    {
        "key": "mech_reltest_xray_sampling",
        "to": "mech-lead",
        "value": "★**采纳你的口径**: 旧『抽检 3 块板』在 1 台样机上不成立 ⇒ 改为 **同一块板 3 个位置 (FCCSP/BTB/电感) "
                "+ 1 处切片**, 抽样量按**位置**计而非按板计; 判据不变 (空洞率 ≤25%, IPC-A-610 Class 2 条款未核)。"
                "★你 T-01 那组判据 (接触电阻 ΔR≤+10mΩ / 阻抗 ±10% / MTF 衰减 ≤10% / 电池 ΔR≤+20% / 电感 ΔL≤±10%) "
                "我全部确认采用, 已写进 HW/EVT_RELIABILITY_TEST_ITEMS.md §B3 工况基准表。",
        "ref": "HW/EVT_RELIABILITY_TEST_ITEMS.md#4.1 R-D-06 + #B3",
    },
    {
        "key": "iss085_esd_cmc_placement",
        "to": "mech-lead",
        "value": "你的 5 条结构位置要求**全部采纳**并写进 EVT 清单与 EMC 判据: ① 两端各 1 组 ESD 距连接器 ≤3.0mm, 共面接地 "
                "(回路 ≤1 过孔), 结电容 ≤0.5pF, 封装 ≤0.5mm ② 两端各 1 个 CMC 距弯折起点 ≥5.0mm 且距连接器 ≤10.0mm, 260°C 回流焊耐受, ≤0805 "
                "③ **一律装 PCB 端, 不许装跨铰链 FPC** (弯折区只允许连续铜箔) ④ 顺序 连接器→ESD→CMC→串阻/端接, 两端对称 "
                "⑤ BAT_DET/VBUS_DET 高阻检测线跨铰链必须被 GND 夹持, 与 USB 差分对间距 ≥3mm。"
                "★**一处分歧 (按我的口径, 你可反驳)**: USB 2.0 差分对**不装 CMC** —— 网表 P9 行 442 已写明 "
                "(USB 2.0 眼图对共模转差分极敏感, 扼流圈会恶化眼图); CMC 只给 CSI/显示差分用。",
        "ref": "HW/EVT_RELIABILITY_TEST_ITEMS.md#4.6 + HW/netlist_v1.csv P9 行 442",
    },
    {
        "key": "iss085_emc_grounding_definition",
        "to": "mech-lead",
        "value": "『外露金属件』定义: **用户可触及 或 佩戴中与皮肤/人体形成导电路径的金属件** (骨架外露面 / Type-C 屏蔽壳 / "
                "铝框 / 充电板铝屏蔽罩 / 铰链销 / PCB 定位销) —— 判据不是『外露』, 是『人体能否触到并泄放』。"
                "★**活动铰链不做全单点接地** (活动接地路径要断, 否则铰链转动时电势差会放电打火) ⇒ 铰链两半**各接机壳地一次**, "
                "铰链本体靠导电垫/铰链销做**搭接 (不是接地)**; 你给的间距 (骨架≥3.0mm / Type-C 壳≥3.0mm / 铰链销与 FPC≥0.5mm / "
                "PCB 销≥0.5mm) 我全部采纳。★R-04/R-07 收敛的前提仍是『外露金属面清单』, 请结构侧给一份带坐标的面清单。",
        "ref": "HW/EMC_PRECHECK.md#R-04/R-07",
    },
    {
        "key": "iss085_usb_crc_threshold",
        "to": "mech-lead",
        "value": "确认你的口径: **『通信中断』= 0 次总线复位 / 0 次掉线 / 0 次枚举丢失**, CRC 错误阈值 **≤1 次/分钟**连续传输 —— "
                "USB 2.0 的 CRC 重传是协议自带机制, 写 0 错误会把正常重传误判成失败 ⇒ **可作为量产抽检项**。"
                "★口径统一为: 枚举丢失 0 次 + 总线复位 0 次 + CRC 错误 ≤1 次/分钟 ⇒ 判通过。",
        "ref": "HW/EMC_PRECHECK.md#R-03 + HW/EVT_RELIABILITY_TEST_ITEMS.md#4.2 R-V-04",
    },
    {
        "key": "iss091_chargeboard_bat_note",
        "to": "mech-lead",
        "value": "★**采纳『不做补偿』**并写进 HW/CHARGE_BOARD_SPEC 的同口径注记 (HW/CHARGE_CURRENT_RECHECK_2026-11-01.md "
                "§2.4 同源): BQ25896 的 BAT 监测点在**框侧**, 跨铰链压降 37-111mV ⇒ 真实电芯欠充 ΔV ⇒ BQ25896 会**提前判满**并终止。 "
                "方向是**欠充 (永不过充)**, 容量损失 <1% ⇒ 不上调终止电压 (会把真实电芯推过 4.2V, 过充方向危险)。"
                "★同一条链上的新数字: 充电电流换算方向已订正 (ICHG=1.216×IIN), 390Ω 档单 pin 0.608A 超触点 0.5A ⇒ 建议 R_ILIM 退 680Ω —— "
                "你按 1.5A 设计点算的铰链压降/发热**不受影响** (仍保守 1.23-2.15×)。",
        "ref": "HW/CHARGE_CURRENT_RECHECK_2026-11-01.md#2.4/#2.5",
    },
    {
        "key": "iss089_ichg_ratio_datasheet",
        "to": "mech-lead",
        "value": "★**确认你判对了**: buck 降压功率守恒 Pout=η·Pin ⇒ **ICHG = η·Vbus·IIN/Vbat = 0.9×5/3.7 = 1.2162×IIN**; "
                "旧的 0.8222 是它的倒数 (乘积=1.000000000, 脚本自校)。★后果: 390Ω 档实际 ICHG = **1.00-1.22A** (不是 0.67-0.82A), "
                "单 pin = **0.608A** ⇒ 超 0.5mm pitch ZIF 触点 0.5A 额定 ⇒ **390Ω 档要重判, 你的假设成立**。"
                "★我的建议取 **680Ω** (单 pin 0.349A / 触点余量 1.43× / 铰链余量 2.15× / 420mAh CC≈36min) 而非 680Ω 直判, "
                "理由: 680Ω 已满足触点与铰链两条硬判据; **若电芯规格书确认 ≤1C 则须退到 1.2kΩ** (0.94C)。裁决权在 boss。",
        "ref": "HW/calc_chg_ichg.py + HW/CHARGE_CURRENT_RECHECK_2026-11-01.md#2.2",
    },
    {
        "key": "iss089_p9_topology_and_stack",
        "to": "mech-lead",
        "value": "★两处都改: ① **CONN_LIGHT 统一 22p** (器件表与网表都是 22p ⇒ 物理带宽 27.00mm + 4 条×2×0.50mm 走线边距 = "
                "**31.00mm**, 不是 26.5mm; §功能块里的 21p 与 (10+4+18+21) 自算作废)。② **P9 页补走线拓扑定义** —— 采不采你的 "
                "H 向径向嵌套, 要先看板宽: ★**板宽已从 15mm 放宽到 30mm** (老板 10-29 19:16), 4 条 FPC 带宽合计 31.00mm 在 30mm 板宽下"
                "只差 1.00mm ⇒ **V 向叠放不再需要 16mm 面内扇开** ⇒ 你的『V 向叠放必须扇开』结论是 15mm 板宽下的, **已过期**。"
                "★我的建议: 按 **V 向叠放 4 条 (31.00mm ≤ 30mm 板宽余 1.00mm 仍偏紧) + H 向径向嵌套** 两条一起核, 但**不再拍板** "
                "(板宽 30 后 4 条跨铰链连接器 (54 触点 = 27mm 焊盘排) 的落板区仍未定 ⇒ ISS-105 F-2 还开着)。",
        "ref": "HW/netlist_v1.csv P9 行 437-441 + needs iss118_pcb_outline_sync_60x30",
    },
    {
        "key": "iss089_chg_led_board_column",
        "to": "mech-lead",
        "value": "★**你判对了, 我方改正**: D_CHG_LED/Q_CHG_LED/R_CHG_LED 三行的 board 列必须 **MAIN_PCB → CHG_BOARD** "
                "(充电灯装充电板/镜框, 老板 10-27 拍板『关机时充电灯要亮』+ VBUS_5V_CHG 只存在于充电板 ⇒ 物理上只能在框侧); "
                "★现状: BOM_v1.csv 里 R_CHG_LED 已是『镜框充电板』而 D/Q_CHG_LED 仍是『镜脚主 PCB』 ⇒ **同一条链三行不一致**。"
                "★我已把 HW/BOM_v1.csv 的 J_CHG 行备注同步, 但**网表改 board 列要动 state/gen_netlist.py (不属硬件总工本单边界)** ⇒ "
                "已列 needs 给项目总工排期, 请项目总工转告。★打印包 MECH/print/temple_cage_340.stl 的 Type-C 面板试样"
                "(Y120-123) 移到镜框端件, 我同意, 但那是结构侧的活。",
        "ref": "HW/BOM_v1.csv (行 330-332) + HW/netlist_v1.csv P10",
    },
    {
        "key": "proto_pcb_thickness_tier",
        "to": "mech-lead",
        "value": "★**你的假设已过期, 别按 4 层 0.80mm 做 mock 板**: 板框已定 **60×30mm** (老板 10-29 19:16), 层数目标 **6 层 1.00mm** "
                "(4 层在 4 组高速 + 62 net + 190 器件下无解) ⇒ **板重 3.33g** (60×30×1.0), 不是 1.33g/1.67g。"
                "★H 链余量按 6 层 1.00mm 重算 (旧 4 层口径已作废); 你的 B2 mock 板请按 **60×30×1.00mm** 做。"
                "★屏蔽罩: 第一台样机**不做**金属屏蔽罩 (只做石墨 + 骨架) ⇒ mock 板的高度上限只需留骨架+石墨+上壳。"
                "★另: PCB 面上需要结构开孔 = 4 个固定孔 (P1/P2 ⌀2.0 H7 + S1/S2 ⌀1.4) + SoC 散热焊盘投影区, 其余不要求开孔。",
        "ref": "HW/pcb60x30_check.json (板重 3.33g) + HW/PCB_FIXING_PINSET2.md",
    },
    {
        "key": "iss065_battery_tier_claim_sync",
        "to": "mech-lead",
        "value": "★**已改**: 我方 interface_claims.battery_capacity_tier = **315mAh无桥/387mAh有桥** (与 mech-lead 同值); "
                "★并且本次窗口把**文件里重复的旧值条目 (无桥接340-575mAh/有桥接575-675mAh) 一并删掉** —— 留着就是过期值, "
                "别人 grep 到会当真 (合并器只取最后一条, 不代表文件里没有错的)。"
                "★其余按你说的: POWER_BUDGET_V2.md §10 S-5 的 315/387 口径是对的, 文档正文不动。",
        "ref": "state/fragments/hw.yaml (interface_claims.battery_capacity_tier) + HW/_frag_update_week_20261101.py",
    },
    {
        "key": "iss092_jdebug_cortex10_netlist",
        "to": "mech-lead",
        "value": "★**接受 2x5@1.27 Cortex-10 焊盘阵列 (座体 DNP)**: 现状网表 J_DEBUG 是 1x4 1.27mm JTAG 排针 (SCHEMATIC_V1 P7 行 585) ⇒ "
                "要改成 2×5 焊盘阵列 + 座体 DNP + J_UART 1x2 **并入同一阵列** (省一条连接器)。"
                "★焊盘尺寸/间距/引脚序 = Cortex-10 标准 (1.27mm 网格, 2×5) —— 需结构侧给**座体外形**或按标准封装出 footprint。"
                "★改网表要动 state/gen_netlist.py (不属硬件总工本单边界) ⇒ 已列 needs 给项目总工排期。",
        "ref": "HW/netlist_v1.csv P7 行 585 + needs iss092_jdebug_cortex10_netlist_fix",
    },
    # ---- to main ----
    {
        "key": "emc_hw_interface_ask",
        "to": "main",
        "value": "EMC 需要的 4 项硬件数据: ① **充电状态读取 = 已有, 双通路** CHG_STAT (BQ25896 STAT 开漏 +10k 上拉 → J_CHG pin5 → SoC GPIO, "
                "低=充电中) + VBUS_DET (1M+1M 分压+100nF → J_CHG pin7 → SoC ADC) ⇒ M-CHRG 门禁**硬件上可实现** (ISS-043 可关)。"
                "② **电源域标称电压**: SYS 3.0-4.2V / 3.3V 轨 (LIGHT_3V3 150mA + VDD_3V3_IO 200mA) / 1.8V IO / 2.8V SENSOR_AVDD / "
                "1.8V SENSOR_VDD_IO / 1.2V SENSOR_CORE / V_CORE 0.65-1.0V —— ★但 **11-01 基线换 RK3576 后全部作废**, 随换芯重出。"
                "③ **帧同步信号能引出**: 现在没有独立帧同步脚 (走 MIPI CSI 内的 FS/EL 或走 USB 侧事件), 需要引出的话要加 pin ⇒ 换芯时一并定。"
                "④ **测流点**: TP_BAT_CHG (跨铰链压降) / TP_VBUS / TP_CHG_STAT / TP_USB_D_P/N 已有; **贴片测温点位** U_TEMP (TMP117) 有器件、"
                "缺物理测点 note ⇒ 已列 needs。",
        "ref": "HW/CHARGE_STATUS_READBACK.md + HW/netlist_v1.csv (P7 测试点页)",
    },
]

# ================================================================= 3. needs (本周新增)
NEEDS_NEW = [
    {
        "key": "iss105_rilim_decision",
        "to": "main",
        "item": "★ISS-105 衍生 (本周新发现, 请老板拍板): R_ILIM 390Ω 档的**充电电流换算方向反了** —— buck 降压 ICHG=η·Vbus/Vbat·IIN="
                "**1.2162×IIN** (旧式 0.8222× 是它的倒数) ⇒ 390Ω 档实际 ICHG 1.00-1.22A, **单 pin 0.608A > 0.5mm ZIF 触点 0.5A 额定** "
                "⇒ 390Ω 档判 FAIL。★建议 **R_ILIM 退 680Ω** (单 pin 0.349A / 触点余量 1.43× / 铰链余量 2.15× / 420mAh CC≈36min); "
                "若电芯规格书确认 ≤1C 则须退 **1.2kΩ** (0.94C)。★**换料不换板** (0402 ±1%), 零板费, 但**网表/BOM/门禁值都要跟着改** ⇒ "
                "请裁定 680Ω 还是 1.2kΩ (due 11-03)。★我的默认假设: 若 11-03 前无回复, 按 **680Ω** 出 RFQ 问价口径, 标注『待电芯规格书确认可退 1.2kΩ』。",
        "since": "2026-11-01",
        "waiting_on": "boss",
        "due": "2026-11-03",
    },
    {
        "key": "iss079_phip_manual_fetch",
        "to": "main",
        "item": "ISS-079 遗留 (需人工一步): 酷芯微**港交所申请版本招股书 (PHIP) 直链检索不到** —— hkexnews 的 AP&PHIP 入口 "
                "(www1.hkexnews.hk/app/appindex.html?lang=zh) 要点 Warning Statement + JS 交互, 非交互抓取拿不到申请人列表 (已试 5 条路径, 见 "
                "HW/ONLINE_INTEL_2026-10-26.md §2.3)。★请人工打开该页 → ACCEPT → 年份 2026 → 检索『合肥酷芯微电子股份有限公司』或"
                "『Artosyn』→ 下载申请版本 PDF, 放 `state/outbox/` ⇒ 我再补 §业务/供应链/交付页的原文级证据。"
                "★当前招股书数字全部是**媒体转述级**, 不能当芯片级规格用 (due 11-05)。",
        "since": "2026-11-01",
        "waiting_on": "boss",
        "due": "2026-11-05",
    },
    {
        "key": "iss043_vbus_det_divider_change",
        "to": "main",
        "item": "ISS-043 衍生 (与 sw-lead 9 项请求 P1-8 同向): 网表 `R_VBUS_DET_1/2` 现状 **1M+1M** ⇒ 源阻抗 500kΩ, τ=**50ms** "
                "(95%≈150ms), ADC 漏电误差 ~15.2%FS。★建议改 **100k/47k** (Rth=32.0kΩ ⇒ τ=**3.2ms**, 5V→**1.60V**, 漏电误差降 10 倍) ⇒ "
                "**换料不换板**。★改网表要动 `state/gen_netlist.py` (不属硬件总工本单边界) ⇒ 请排期重生成; 并请转 sw-lead 核对 ADC 量程与门禁阈值"
                " (我方建议: VBUS_PRESENT_TH=3.0V 对应输入 ≥4.4V)。★另: 充电状态门禁判据必须是 **OR(CHG_STAT 低, VBUS>阈值)** ⇒ "
                "断线 fail-safe, 详见 HW/CHARGE_STATUS_READBACK.md §3.1 (due 11-04)。",
        "since": "2026-11-01",
        "due": "2026-11-04",
    },
    {
        "key": "iss089_chg_led_board_column_fix",
        "to": "main",
        "item": "ISS-089 交叉评审 #4 (mech-lead 判对, 我方认账): 充电灯链 **D_CHG_LED/Q_CHG_LED/R_CHG_LED 的 board 列标 MAIN_PCB 是错的** —— "
                "老板 10-27 拍板『关机时充电灯要亮』+ VBUS_5V_CHG 只存在于充电板 ⇒ 这条链物理上只能在**镜框充电板**。"
                "★现状 HW/BOM_v1.csv 里 R_CHG_LED 已是『镜框充电板』而 D/Q_CHG_LED 仍是『镜脚主 PCB』 ⇒ 同一条链三行不一致。"
                "★改 board 列要动 `state/gen_netlist.py` (不属硬件总工本单边界) ⇒ 请排期重生成网表+BOM; 改完 ISS-103 的镜框导光孔位置才能定 "
                "(否则会开在镜脚上) (due 11-04)。",
        "since": "2026-11-01",
        "due": "2026-11-04",
    },
    {
        "key": "iss092_jdebug_cortex10_netlist_fix",
        "to": "main",
        "item": "ISS-092 衍生: J_DEBUG 现状是 1x4 1.27mm JTAG 排针 (SCHEMATIC_V1 P7 行 585) ⇒ 按 mech-lead (ISS-092) 要求改成 "
                "**2x5@1.27 Cortex-10 焊盘阵列 (座体 DNP)**, 并把 **J_UART 1x2 并入同一阵列**。★改网表要动 `state/gen_netlist.py` ⇒ "
                "请排期; 焊盘阵列按 Cortex-10 标准 1.27mm 网格, footprint 我方出 (due 11-05)。",
        "since": "2026-11-01",
        "due": "2026-11-05",
    },
    {
        "key": "iss105_bom_generator_qty_override",
        "to": "main",
        "item": "ISS-105 衍生 (工具缺口): `HW/BOM_v1.csv` 的 J_CHG 备料口径『**实物一对 (框侧座 + 脚侧座), 备料按 2 只**』我已写进 memo 列 "
                "(第 12 行), ★但 `state/gen_bom.py` 的自检**强制所有 ref 的 qty==1** 且 memo 由 `procurement_status()` 生成 ⇒ "
                "**下次重生成网表/BOM 时这行备注会被覆盖掉**。★请在生成器里加一张『备料倍数/实物件数』覆盖表 (至少 J_CHG=2) 或改自检口径; "
                "否则我们的备料口径随时蒸发 (due 11-06)。",
        "since": "2026-11-01",
        "due": "2026-11-06",
    },
    {
        "key": "iss118_pcb_outline_sync_60x30",
        "to": "mech-lead",
        "item": "★台账订正 (重要): 老板 10-29 19:16 拍板『板宽可以放到 30mm 以内』 ⇒ **板框已定 60×30mm** (PROJECT_TRACKER §0 板宽行, "
                "11-01 20:5x 已订正)。★我方分片的 `pcb_outline` 已从 60x15mm 改成 **60x30mm** ⇒ 合并器现在会报 "
                "`pcb_outline` 冲突 (60x30mm vs 你的 60x15mm) ⇒ **请把 mech.yaml 的 pcb_outline 同步成 60x30mm** (或改用 "
                "pcb_board_width=30mm + pcb_length=60mm 两个细分 key)。★附带: 60×30 ⇒ 板重 **3.33g** (6层1.0mm), 你的 H 链与 mock 板"
                " (B2) 请按 30mm 板宽重算 —— 你 10-31 的假设『4层0.80mm / 1.33g』已作废 (due 11-04)。",
        "since": "2026-11-01",
        "due": "2026-11-04",
    },
    {
        "key": "iss118_pcb_holes_30mm_y",
        "to": "mech-lead",
        "item": "★孔位 Y 向重算 (板宽 15→30 后): 4 个固定/压紧孔的 X 不变, **Y 按中心线平移** (旧中心 7.50 → 新中心 15.00, S 孔 ±5.00 不变) ⇒ "
                "新坐标 **P1(8.00,15.00) / P2(52.00,15.00) / S1(8.00,10.00) / S2(52.00,20.00)** (板 60×30, 原点左下角)。"
                "★复算已过: 4 孔在板内且边距 ≥2.0mm; 与 SoC 逃线带 X[20.20,31.80] 的 2D 重叠 = **0.000mm²**; 全部落在 X[4,12]+X[46,56] 窗口; "
                "P1-P2 基准跨距 44.00mm 不变 (`python3 HW/hw_week_20261101_check.py` §1)。★请结构侧确认: 骨架 ⌀2.0 h6 压装销孔位置 + "
                "打印件 ⌀2.4 间隙孔 + 螺钉柱避让是否随 Y 平移 (骨架石墨覆盖范围也要重核, 30mm 板宽下 SoC 横向扩散通道从 2.00mm 变 3.50mm) (due 11-04)。",
        "since": "2026-11-01",
        "due": "2026-11-04",
    },
]

# ================================================================= 4. artifacts
ARTIFACTS = [
    {
        "path": "HW/EVT_RELIABILITY_TEST_ITEMS.md",
        "kind": "spec",
        "version": "1.0",
        "updated_at": "2026-11-01",
        "summary": "ISS-111 交付: EVT 可靠性实测项清单 37 项 (跌落 9 / 振动 5 / 弯折 6 / 热 5 / 焊点 6 / 连接器寿命 6), "
                   "每项含 测什么/怎么测(设备+工装+样品数+次数)/量化判据/不过回退哪一版/状态 五字段; "
                   "工况直接引用 RELIABILITY_DESIGN §2.2 不重写; X-ray 抽样按位置计 (1 块板 3 位置 + 1 切片); 全部 [未验]",
    },
    {
        "path": "HW/CHARGE_STATUS_READBACK.md",
        "kind": "spec",
        "version": "1.0",
        "updated_at": "2026-11-01",
        "summary": "ISS-043 交付: 充电状态读取 = CHG_STAT (BQ25896 STAT 开漏 + 10k 上拉 → J_CHG pin5) + VBUS_DET (1M+1M+100nF → "
                   "J_CHG pin7 → ADC) 双通路; 门禁判据 OR(...) fail-safe; RC 复算 τ=50ms (建议改 100k/47k ⇒ 3.2ms); M-CHRG 硬件上可实现",
    },
    {
        "path": "HW/CHARGE_CURRENT_RECHECK_2026-11-01.md",
        "kind": "review",
        "version": "1.0",
        "updated_at": "2026-11-01",
        "summary": "ISS-089 交叉评审 #3 确认 + ISS-105 收口: ICHG/IIN 换算方向反了 (0.8222× → 1.2162×); 390Ω 档单 pin 0.608A > "
                   "0.5A 触点天花板 ⇒ 判 FAIL, 建议 680Ω (单 pin 0.349A/余量 1.43×); J_CHG 实物一对备料口径 + 机械防呆 C-4 已闭环",
    },
    {
        "path": "HW/calc_chg_ichg.py",
        "kind": "script",
        "version": "1.0",
        "updated_at": "2026-11-01",
        "summary": "充电电流换算自证脚本 rc=0: 系数自校 (1.2162×0.8222=1.000000000) + 5 档 R_ILIM 扫描 + 三条硬判据 (触点/电芯倍率/铰链) + "
                   "R_ILIM 不装 ⇒ 铰链过 1.365×",
    },
    {
        "path": "HW/calc_chg_ichg.json",
        "kind": "data",
        "version": "1.0",
        "updated_at": "2026-11-01",
        "summary": "充电电流换算机读结果 (5 档 × IINMAX/ICHG/单pin/余量/倍率/判定)",
    },
    {
        "path": "HW/ONLINE_INTEL_2026-10-26.md",
        "kind": "intel",
        "version": "1.0",
        "updated_at": "2026-11-01",
        "summary": "ISS-079 交付: ①采用 ARS45 的 AI 翻译眼镜 = 科大讯飞『讯飞AI眼镜』(2026-05-28 BEYOND Expo 发布 / 40g / 122 语言 / "
                   "唇动识别降噪), 公开拆解 [0数据]; ②酷芯微招股书: fabless + 智能可穿戴仅占营收 9.8% + 供应商集中 61-65% + "
                   "分销收入塌 1.09 亿 ⇒ 支持跳过酷芯微; PHIP 直链 [0数据] (5 条路径已试)",
    },
    {
        "path": "HW/hw_week_20261101_check.py",
        "kind": "script",
        "version": "1.0",
        "updated_at": "2026-11-01",
        "summary": "本周自证入口 rc=0: 43 项检查 (孔位 60x30 重算 / 充电电流 / 充电状态通路 / EVT 清单齐套性 / BOM 备料口径 / "
                   "分片过期值与重复键 / 分片登记计数) 一次复算交接单里每个数字",
    },
    {
        "path": "HW/_frag_update_week_20261101.py",
        "kind": "script",
        "version": "1.0",
        "updated_at": "2026-11-01",
        "summary": "2026-11-01 周更新分片原子写脚本 (走 state/frag_write.py 的 update_fragment, 同一条 tmp+fsync+os.replace 路径): "
                   "claims 订正 6 条 + 新增 8 条 + answers 16 条 + needs 8 条 + 补 due 23 条 + 状态/产出",
    },
    {
        "path": "HANDOFF/2026-11-01_hw-lead_周更新.md",
        "kind": "handoff",
        "version": "1.0",
        "updated_at": "2026-11-01",
        "summary": "2026-11-01 周更新交接单 (B1-B6 六块齐): ISS-043/079/105/111 四条闭环 + ISS-121 登记 + 16 条补登记 answers + "
                   "8 条新 needs + 14 条 claims 订正/新增 + 自证命令",
    },
    {
        "path": "HANDOFF/2026-11-01_hw-lead_ISS111_EVT可靠性实测项清单.md",
        "kind": "handoff",
        "version": "1.0",
        "updated_at": "2026-11-01",
        "summary": "ISS-111 专项交接单 (B1-B6 六块齐): EVT 37 项清单交付说明 + 对 mech-lead 的 X-ray 抽样口径答复",
    },
]

# ================================================================= 5. 补 due (历史欠账)
DUE_FIX = {
    "pcb_outline_confirm": "2026-11-05",
    "debug_port_form": "2026-11-05",
    "iss081_pm_decisions": "2026-11-05",
    "iss081_vendor_ball_count": "2026-11-05",
    "iss105_pcb_outline_sync_60x15": "2026-11-05",
    "iss049_skeleton_profile": "2026-11-05",
    "iss049_graphite_hchain": "2026-11-05",
    "iss049_mount_screw": "2026-11-05",
    "iss049_hole_windows": "2026-11-05",
    "iss049_segment_order": "2026-11-05",
    "iss049_budget_version": "2026-11-05",
    "iss062_rgeo2_vendor_send": "2026-11-05",
    "iss062_rgeo2_sw_q4_correction": "2026-11-05",
    "iss062_rgeo2_roi_fallback_decision": "2026-11-05",
    "iss067_uvp_landing_to_main": "2026-11-05",
    "iss067_mech_transmit_m1_m8": "2026-11-05",
    "iss067_caliber_b_converter_loss": "2026-11-05",
    "iss121_magnet_xy_define": "2026-11-04",
    "iss121_mag_soc_gap_correction": "2026-11-04",
    "iss121_skeleton_extent_confirm": "2026-11-04",
    "iss121_mic_count_spec": "2026-11-04",
    "iss121_conn_zone_dependency": "2026-11-04",
}

STATUS = {
    "phase": "P2(原理图/BOM)+结构接口",
    "progress_pct": 68,
    "health": "yellow",
    "summary": "2026-11-01 周更新 (项目总工派, 本周唯一写会话窗口): 四条 issue 闭环 + 16 条补登记 answers + 14 条 claims 订正/新增。"
               "① ISS-111 (EVT 可靠性实测项清单) **fixed**: 出 HW/EVT_RELIABILITY_TEST_ITEMS.md —— 6 类 37 项 (跌落 9/振动 5/弯折 6/热 5/"
               "焊点 6/连接器寿命 6), 每项含 测什么/怎么测(设备+工装+样品数+次数)/量化判据/不过回退哪一版/状态 五字段, 工况直接引用 "
               "RELIABILITY_DESIGN §2.2 不重写; 顺带闭合 mech-lead 的 X-ray 抽样口径 (1 台只有 1 块主板 ⇒ 抽样按**位置**计: 同板 3 位置 + 1 切片)。"
               "② ISS-043 (充电状态读取) **fixed**: HW/CHARGE_STATUS_READBACK.md —— 硬件上本来就是**双通路**: CHG_STAT (BQ25896 STAT 开漏 + "
               "10k 上拉 → J_CHG pin5 → SoC GPIO, 低=充电中) + VBUS_DET (1M+1M+100nF → J_CHG pin7 → ADC) ⇒ M-CHRG 门禁**可实现**; "
               "★判据必须 OR(...) 才 fail-safe (单看 CHG_STAT 断线会放开禁 OD); RC 复算 τ=50ms (建议 100k/47k ⇒ 3.2ms)。"
               "③ ISS-079 (情报检索) **fixed**: HW/ONLINE_INTEL_2026-10-26.md —— 采用 ARS45 的 AI 翻译眼镜 = **科大讯飞『讯飞AI眼镜』** "
               "(2026-05-28 BEYOND Expo 发布, 40g, 122 语言, 唇动识别降噪), 但**公开拆解 [0数据]**; 招股书侧 (媒体转述级) 拿到硬情报: "
               "**fabless + 智能可穿戴仅占营收 9.8% + 供应商集中 61.2-65.5% + 分销收入 1.71亿→4350万 (-1.09亿)** ⇒ 量化支持『跳过酷芯微』; "
               "PHIP 直链仍 [0数据] (5 条路径已试, 需人工点 hkexnews)。④ ISS-105 **fixed**: 分片过期值订正 (pcb_outline 60x15→**60x30mm** / "
               "pcb_width_recommend 15→30mm / pcb_mount_holes_xy 的 Y 按 30mm 板宽重算 = P1(8,15)P2(52,15)S1(8,10)S2(52,20)) + "
               "battery_capacity_tier 重复旧值条目已清 + J_CHG『实物一对』写进 BOM 备料栏 + 机械防呆已是 RFQ C-4 硬判据。"
               "⑤ ★**本周新发现 (总工的盲区)**: ISS-089 交叉评审 #3 命中 —— CHARGE_BOARD_SPEC §3.4 的 ICHG=IIN×(VBAT/VBUS)/η **方向反了** "
               "(buck 降压应是 ICHG=η·Vbus/Vbat·IIN=**1.2162×IIN**, 旧式 0.8222× 是它的倒数, 乘积=1.000000000 自校) ⇒ **390Ω 档实际 "
               "ICHG 1.00-1.22A, 单 pin 0.608A > 0.5A 触点天花板 ⇒ 390Ω 档判 FAIL**, 建议 R_ILIM 退 **680Ω** (单 pin 0.349A/余量 1.43×); "
               "mech 按 1.5A 设计点算的铰链压降不受影响 (仍保守 1.23-2.15×)。⑥ ★补登记 **16 条 answers** (窗口开始时 13 条) —— 覆盖 sw-lead 的 "
               "fw_boot_storage_bom / fw_boot_mode_hw / sw_reset_hw_changes / sw_poweroff_gpio_pin, mech-lead 的 13 条 (含 X-ray 抽样/ESD-CMC/"
               "接地定义/CRC 阈值/BAT 监测点/ICHG 方向/P9 堆叠/充电灯 board 列/mock 板档位/电池档位/Cortex-10), main 的 emc_hw_interface_ask。"
               "⑦ ★新增 8 条 needs (含 R_ILIM 退档裁决 due 11-03 / PHIP 人工下载 / VBUS_DET 改阻值 / 充电灯 board 列 / J_DEBUG Cortex-10 / "
               "BOM 生成器备料倍数 / mech 侧 60x30 同步 / 孔位 Y 重算), 并给 23 条历史 needs 补 due (零僵尸)。⑧ 边界: 未发任何邮件/未联系供应商/"
               "未改 PROJECT_TRACKER/STATE.yaml/别人的分片/别人的 issue; 网表与 BOM 生成器 (state/gen_netlist.py, gen_bom.py) 不在本单边界 ⇒ 走 needs。"
               "自证: python3 HW/hw_week_20261101_check.py (rc=0) + state/merge.py (rc=0) + state/gate_check.py。",
}


def main() -> int:
    dry = "--dry-run" in sys.argv

    def mutate(d: dict) -> None:
        # --- 1. claims: 去重复 key (保留最后一条) + 订正 + 新增 ---
        claims = d.get("interface_claims") or []
        seen = {}
        for c in claims:
            k = c.get("key")
            if k:
                seen[k] = c          # 后出现的覆盖先出现的 (与 merge.py 口径一致)
        out = []
        for c in claims:
            k = c.get("key")
            if k is None:
                continue
            if seen.get(k) is not c:
                continue            # 旧的重复条目直接丢掉 (过期值不留在文件里)
            if k in CLAIM_FIX:
                val, note, ref = CLAIM_FIX[k]
                c["value"] = val
                c["note"] = note
                c["ref"] = ref
            out.append(c)
        have = {c.get("key") for c in out}
        for nc in CLAIM_NEW:
            if nc["key"] in have:
                continue
            out.append(dict(nc))
        d["interface_claims"] = out

        # --- 2. answers ---
        ans = d.setdefault("answers", [])
        have_ans = {(a.get("key"), a.get("to")) for a in ans}
        for a in ANSWERS:
            if (a["key"], a["to"]) in have_ans:
                continue
            ans.append({"key": a["key"], "to": a["to"], "value": a["value"], "ref": a["ref"]})

        # --- 3. needs: 补 due + 新增 ---
        needs = d.setdefault("needs_from", [])
        for n in needs:
            k = n.get("key")
            if k in DUE_FIX and not n.get("due"):
                n["due"] = DUE_FIX[k]
        have_need = {n.get("key") for n in needs}
        for n in NEEDS_NEW:
            if n["key"] in have_need:
                continue
            needs.append({"key": n["key"], "to": n["to"], "item": n["item"],
                           "since": n.get("since", "2026-11-01"),
                           "waiting_on": n.get("waiting_on", "agent"),
                           "due": n.get("due")})

        # --- 4. artifacts ---
        arts = d.setdefault("artifacts", [])
        have_art = {a.get("path") for a in arts}
        for a in ARTIFACTS:
            if a["path"] in have_art:
                continue
            arts.append(dict(a))

        # --- 5. status ---
        st = d.setdefault("status", {})
        st.update(STATUS)
        d["updated_at"] = "2026-11-01"
        d["updated_by"] = "hw-lead"

    if dry:
        from frag_write import load_fragment
        import copy
        d = copy.deepcopy(load_fragment("hw-lead"))
        mutate(d)
        print("[dry-run] 将要写入的统计:")
        print(f"  interface_claims: {len(d.get('interface_claims') or [])}")
        print(f"  answers: {len(d.get('answers') or [])}")
        print(f"  needs_from: {len(d.get('needs_from') or [])}")
        print(f"  artifacts: {len(d.get('artifacts') or [])}")
        return 0

    update_fragment("hw-lead", mutate)
    print("[frag_write] ✅ hw.yaml 已原子更新 (claims/answers/needs/artifacts/status)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
