#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-211 / ★ISS-214★ 机器门禁 —— ★**网表自身一致性 4 处 (第 1 轮) + 7 组 (第 2 轮) 缺陷的「现状守卫」** ★
================================================================================
★★**2026-11-16 · ISS-214 第 2 轮扩展** ★★
· 第 1 轮 (ISS-211): d1 I2C_A 上拉 / d2 BAT_DET 全 DNP / d3 U_EN_SW 无本体行 / d4 USB D− 无 ESD
· 第 2 轮 (ISS-214): d5 USB 串阻双值 / d6 CONN_LIGHT 21p vs 22p + P9 堆叠账 /
  d7 SARADC_VIN5 满量程 + 分压比 / d8 BAT_DET 漏电预算 / d9 USB D− ESD 方案与型号判据 /
  d10 CHARGE_BOARD_SPEC ICHG/IIN 方向 / d11 NET-LED board 列
· ★**第 2 轮新读 5 个"根因层"文件** (不是产物层): `state/gen_schematic_pages.py` (P9 页正文) ·
  `HW/CHARGE_BOARD_SPEC.md` (§2.4/§3.4) · `HW/EMC_PRECHECK.md` (USB 2.0 差分 90Ω/480Mbps) ·
  `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` (RK3572 官方 datasheet 抽取文本) ·
  `HW/PCB/FET3572C_PIN_TABLE.csv` (SoM 厂 IO 域表)
★**它不是"检查网表对不对", 是"检查【规格页】跟【现行网表】还对不对得上"** ★

★★**2026-11-16 · ISS-217 第 3 轮扩展 (★落表作业包门禁★)** ★★
· ★**新增第 4 个被检查对象**: `HW/SCHEMATIC_LANDING_WORKPACKET_V1.md` (★落表作业包本体, 28 条作业条目★)
· ★**新增 "作业包完整性" 自检**: ★**作业包里必须逐组出现 (项号 · 真修法文件 · 改法 · 命令 · 翻面判据 id) ⇒ 缺任何一组 ⇒ 红** ★
· ★**新增 "三方对齐" 自检**: ★**作业包项号 ↔ 规格页条号 ↔ 门禁 R# 必须对得上 (对不上 ⇒ 红)** ★
· ★**R9 的翻面阈值从 5.0 收紧到 3.0 mm** (★按 `state/gen_schematic_pages.py` P9 页自引的 ISS-085 规矩; ★**现状断言一条字都不动**★) + ★**新增一条反向用例证明阈值真被读到 3.0 而不是 5.0** ★

★★**它守的是三件事 (★规格页 ⇄ 本脚本 ⇄ 现行文件 三方对齐★)** ★★

  ① **判据 a (规格页 ⇄ 现行文件)**: `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` 里
     ★**逐字引用**的 4 条缺陷现状 (行号 + 关键字段) 必须与现行
     `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` /
     `HW/SCHEMATIC_V1_SPEC.json` / `HW/PCB/demo_mainboard.kicad_pcb` **完全一致**
     ⇒ 对不上 = 网表被静默改过 = **红**
  ② **判据 b (BOM 现状断言)**: `HW/BOM_v1.csv` 里 `U_EN_SW` 行的 `type` 仍是 `NET`
     (★现状断言, 让它别被悄悄"修好"而规格页不跟★)
  ③ **判据 c (不该改错的锚点仍在)**: 4 条各自的"锚"必须还在原位
     (★例: L169 note 里那句"已作废"还在 / L182 的 `dnp=DNP` 还在 / ★
     `U_EN_SW` 在表A/表B 仍然 0 条 `type!=NET` 的器件本体行 / ★
     `D_ESD_USB_D` 仍然只有 2 个焊盘且 D− 那条路仍然 0 个 ESD 位号★)

★★**rc 语义 (★重要: 现在 rc=0 不等于"网表没问题"★)** ★★
  - `rc=0` ⇒ ★**现状与规格页一致** (★即 4 条缺陷**仍在**, 这是预期状态★)
  - `rc=1` ⇒ 不一致, 并**点名**是哪一条 (哪个 key / 哪一行 / 哪个字段对不上)
  - `rc=2` ⇒ 用法/环境错误 (文件缺失等)
  - ★**门禁是【现状守卫】不是【合格证】**: 现在 4 条缺陷仍在 ⇒ 门禁应当是绿的 ⇒
    ★**等它们随"整链重出 第 1 步"那一趟落表后, 用 `--expect-resolved` 翻成
    "缺陷已消失"口径 (★翻面条件写在 `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` §⑤★)★

★★**三条纪律 (★别踩★)** ★★
  - ★**只读**: 本脚本不写任何项目文件 (自检只动临时目录里的副本) ★
  - ★**不改网表 / 不改板 / 不改生成器** ⇒ 本脚本只**看**, 只**判** ★
  - ★**受保护 md5 必须逐字节不变** (网表 `c78f9912…` / 脚表 `4814617e…` / ★
    板 `611b869e…` / `.kicad_pro` `3e504d2b…`) ⇒ 本脚本**一个字节都不碰** ★

用法:
    python3 HW/check_netlist_selfconsistency.py              # 现状守卫 (现在应 rc=0)
    python3 HW/check_netlist_selfconsistency.py --verbose    # 打印逐条锚点明细
    python3 HW/check_netlist_selfconsistency.py --expect-resolved   # 翻面口径 (落表后 rc=0)
    python3 HW/check_netlist_selfconsistency.py --selftest   # 反向用例 (改临时副本 ⇒ 必须变红)
    python3 HW/check_netlist_selfconsistency.py --root DIR   # 指定工程根 (自检/复现用)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.dirname(HERE)  # HW/ 的上一级 = 工程根

REL = {
    "netlist": os.path.join("HW", "netlist_v1.csv"),
    "pins": os.path.join("HW", "netlist_v1_pins.csv"),
    "bom": os.path.join("HW", "BOM_v1.csv"),
    "spec": os.path.join("HW", "SCHEMATIC_V1_SPEC.json"),
    "board": os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb"),
    "specpage": os.path.join("HW", "NETLIST_SELF_CONSISTENCY_SPEC.md"),
    # ── ★ISS-214 第 2 轮新增的 5 条要读的文件 (★全是"根因层"文件, 不是产物层★) ──
    "pages": os.path.join("state", "gen_schematic_pages.py"),        # ★P9 页正文 (堆叠账/铰链通道的源头)
    "chgspec": os.path.join("HW", "CHARGE_BOARD_SPEC.md"),           # ★§2.4/§3.4 ICHG/IIN 系数 (源头)
    "emc": os.path.join("HW", "EMC_PRECHECK.md"),                    # ★USB 2.0 差分 90Ω + 480Mbps (源头)
    "rk": os.path.join("HW", "RK3572_PIN_TABLE", "rk3572_datasheet_V1.1.txt"),  # ★RK3572 官方 datasheet 抽取文本
    "sompins": os.path.join("HW", "PCB", "FET3572C_PIN_TABLE.csv"),   # ★SoM 厂 IO 域表 (SARADC_VIN5 = 1.8V)
    # ── ★ISS-217 第 3 轮新增: 落表作业包本体 (★"作业包漏一条就红" 的被检查对象★) ──
    "workpacket": os.path.join("HW", "SCHEMATIC_LANDING_WORKPACKET_V1.md"),
}

# ★纯文本类文件 (判据写成 'text contains X' / 'text notcontains X')★
TEXT_KINDS = {"pages", "chgspec", "emc", "rk", "specpage"}

# ─────────────────────────────────────────────────────────────────────────────
# ★★ 期望值 (★唯一真源: 规格页的锚点表必须与这里逐字一致★) ★★
# ★格式: (key, file, line, check) ★
#   file : netlist | pins | bom | spec | board | specpage
#   line : 物理行号 (1-based, 表头 = 第 1 行) · 特殊: "?" = 不限行号 (按谓词找)
#   check: ★迷你判据 DSL★ ★
#     "field == value"              CSV 列值逐字相等
#     "field contains value"        CSV 列值包含子串
#     "count(<pred>) == N"          谓词命中行数 (pred 形如 "ref==X&type!=NET")
#     "footprint.<REF>.<attr> == v" 板封装属性 (value | pads | pad1.net | pad2.net | pad3.net)
#     "spec.<path> == value"        SCHEMATIC_V1_SPEC.json 里的字段 (connections[id=B-01].level)
#     "esd_on_net(<netA>,<netB>) == N"  板上带 ESD 的位号里, 焊盘挂在这两条网上的个数
#     "text contains X"             ★★纯文本文件里含子串 X (第 2 轮: pages/chgspec/emc/rk/specpage)★★
#     "text notcontains X"          ★★纯文本文件里不含子串 X ★★
#     "calc(<expr>) <op> <num>"     ★★数值判据 (op ∈ ==/>/>=/</<=), <expr> 见 CALC_EXPRS★★
# ─────────────────────────────────────────────────────────────────────────────

# ★★第 2 轮 (ISS-214) 的数值表达式 (★全部只读现行文件, 不引入外部数据★★)
#   node_v@<V>        BAT_DET 分压链在电池 <V> 时 ADC 节点电压 (V)
#   leak_ua@<V>       BAT_DET 分压链在电池 <V> 时的漏电流 (µA)
#   leak_note_ua@<V>  R_BAT_DET_1 的 note 里**自称**的漏电流 (µA)  (★缺陷: 与上面那个对不上★)
#   esd_dist_usb      板面 D_ESD_USB_D → J_USB_C 距离 (mm)
#   r_ilim            R_ILIM 的阻值 (Ω, 从网表 value 解析)
#   iinmax_max        IINMAX = KILIM_max / R_ILIM (A, KILIM_max = 390 AΩ [官方 BQ25896])
#   ichg_ratio@<Vbat> ICHG/IIN = η·Vbus/Vbat (η=0.90 / Vbus=5.0V, 见规格页 §10 第 (7) 条)
#   ichg_max@<Vbat>   铰链段 ICHG 上限 (A) = iinmax_max × ichg_ratio
#   ichg_pin_max@<Vbat> 铰链段**单 pin** 载流上限 (A) = ichg_max / 2 (J_CHG pin1/pin2 双 pin 并联)
ETA_BUCK = 0.90      # ★BQ25896 充电效率 (datasheet: 92.5% @2A / 90.5% @3A ⇒ 取保守 90%)★
VBUS_CHG = 5.0       # ★VBUS = 5.0V (CHARGE_BOARD_SPEC §3.4 口径)★
KILIM_MAX = 390.0    # ★BQ25896 KILIM max = 390 AΩ (datasheet)★
# ★★ISS-217: ESD 距 J_USB_C 的【翻面】阈值 ★★
#   ★依据: `state/gen_schematic_pages.py` P9 页自引的 ISS-085 结构总工回执
#         「④ **ESD 距连接器 ≤3.0mm** / CMC 距弯折起点 ≥5.0mm, 一律放 PCB 端, 不许上 FPC」
#   ★ISS-211 §5.2 写的「≤ 5 mm」口径【作废】⇒ 取项目自己的规矩 (更严) = 3.0mm
#   ★★现状断言 (`d9_esd_dist` = calc(esd_dist_usb) > 5) 一条字都不许动 ★★
#   ★★现状 47.99mm 无论按 5 还是按 3.0 判都成立 ⇒ 改阈值不动现状断言★★
ESD_MAX_DIST_MM = 3.0

EXPECT: list[tuple[str, str, str, str]] = [
    # ── 第 (1) 条: I2C_A 上拉 —— NET 行说 4.7k/3.3V, 器件行说 2.2k/1.8V ──
    ("d1_a167_value", "netlist", "167", "value == 上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, 灌 0.64mA @VOL=0.4V, t_r=186ns@100pF / 559ns@300pF)"),
    ("d1_a167_ref", "netlist", "167", "ref == NET_I2C_A_SCL"),
    ("d1_a168_value", "netlist", "168", "value == 上拉 2.2k 到 1.8V"),
    ("d1_a168_ref", "netlist", "168", "ref == NET_I2C_A_SDA"),
    ("d1_a169_value", "netlist", "169", "value == 2.2k ±1%"),
    ("d1_a169_net", "netlist", "169", "net == VDD_1V8_IO"),
    ("d1_a169_ref", "netlist", "169", "ref == R_PU_I2CA_SCL"),
    ("d1_a169_note", "netlist", "169", "note contains 已作废"),
    ("d1_a170_value", "netlist", "170", "value == 2.2k ±1%"),
    ("d1_a170_net", "netlist", "170", "net == VDD_1V8_IO"),
    ("d1_a171_value", "netlist", "171", "value contains 上拉 2.2k 到 1.8V"),
    ("d1_b367_net", "pins", "367", "net == I2C_A_SCL"),
    ("d1_b368_net", "pins", "368", "net == VDD_1V8_IO"),
    ("d1_spec_b01_level", "spec", "?", "spec.connections[id=B-01].level == 1.8V"),
    ("d1_spec_b01_imp", "spec", "?", "spec.connections[id=B-01].imp == 上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, 灌 0.64mA @VOL=0.4V, t_r=186ns@100pF / 559ns@300pF)"),
    ("d1_spec_b02_level", "spec", "?", "spec.connections[id=B-02].level == 1.8V"),
    ("d1_spec_b02_imp", "spec", "?", "spec.connections[id=B-02].imp == 上拉 2.2k 到 1.8V"),

    # ── 第 (2) 条: BAT_DET 分压链全 DNP, 但 SoC ADC 输入脚必装 ──
    ("d2_a181_ref", "netlist", "181", "ref == NET_BAT_DET"),
    ("d2_a181_dnp", "netlist", "181", "dnp == 必装"),
    ("d2_a182_ref", "netlist", "182", "ref == R_BAT_DET_1"),
    ("d2_a182_dnp", "netlist", "182", "dnp == DNP"),
    ("d2_a182_value", "netlist", "182", "value == 1M ±1%"),
    ("d2_a182_note", "netlist", "182", "note contains DNP: 同上"),
    ("d2_a183_ref", "netlist", "183", "ref == R_BAT_DET_2"),
    ("d2_a183_dnp", "netlist", "183", "dnp == DNP"),
    ("d2_a184_ref", "netlist", "184", "ref == C_DET_BAT"),
    ("d2_a184_dnp", "netlist", "184", "dnp == DNP"),
    ("d2_a185_ref", "netlist", "185", "ref == C_DET_BAT"),
    ("d2_a185_dnp", "netlist", "185", "dnp == DNP"),
    ("d2_a186_node1", "netlist", "186", "node1 == J_SOM_P1 pin38"),
    ("d2_a186_dnp", "netlist", "186", "dnp == 必装"),
    ("d2_a186_note", "netlist", "186", "note contains [BAT_DET] SoC ADC 输入节点"),
    ("d2_b307_dnp", "pins", "307", "dnp == DNP"),
    ("d2_b309_dnp", "pins", "309", "dnp == DNP"),
    ("d2_b100_dnp", "pins", "100", "dnp == DNP"),
    ("d2_b210_net", "pins", "210", "net == BAT_DET"),

    # ── 第 (3) 条: U_EN_SW 没有器件本体行 ⇒ BOM 把它登记成 NET 行 ──
    ("d3_a441_type", "netlist", "441", "type == NET"),
    ("d3_a441_value", "netlist", "441", "value == EN 输入 (高=放行底板)"),
    ("d3_a442_type", "netlist", "442", "type == IC"),
    ("d3_a443_type", "netlist", "443", "type == NET"),
    ("d3_a444_type", "netlist", "444", "type == NET"),
    ("d3_a_rows", "netlist", "?", "count(ref==U_EN_SW) == 4"),
    ("d3_a_body", "netlist", "?", "count(ref==U_EN_SW&type!=NET) == 1"),
    ("d3_b_rows", "pins", "?", "count(ref==U_EN_SW) == 4"),
    ("d3_b_body", "pins", "?", "count(ref==U_EN_SW&type!=NET) == 1"),
    ("d3_bom208_type", "bom", "208", "type == IC"),
    ("d3_bom208_value", "bom", "208", "value == TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=GND, UQFN-4 RAA 0.85 x 0.75 mm)"),
    ("d3_board_value", "board", "?", "footprint.U_EN_SW.value == EN 输入 (高=放行底板)"),
    ("d3_board_pads", "board", "?", "footprint.U_EN_SW.pads == 4"),
    ("d3_ctrl_a50_type", "netlist", "50", "type == IC"),

    # ── 第 (4) 条: USB D− 全程无 ESD, 而 D_ESD_USB_D 自称"双通道" ──
    # ★★2026-11-16 ISS-257 落表 (★hw-lead·续做第 1 轮★): D_ESD_USB_D 的 value 已随 G1a-7
    #   落成真型号 `TPD1E05U06DPYR (...)` ⇒ ★**这 3 条锚点的【现状值】跟着落表走** ★
    #   (★与 ISS-220 落表时 d1/d6、ISS-223 落表时 d5 的处理同型: 判据本体 (value 必须
    #   等于板上那颗 ESD 的真型号) 一个字没改, 改的只是【断言的现状值】⇒ 锚点条数一条没减★
    #   ★★**板侧 (d4_esd_value) 一条都没动** ★ ⇒ 板封装 Value 属性仍停在旧串 ⇒ ★**PCB 类待办**★
    ("d4_a417_value", "netlist", "417", "value == TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)"),
    ("d4_a417_net", "netlist", "417", "net == USB_D_P_SRC"),
    ("d4_a417_dnp", "netlist", "417", "dnp == 必装"),
    ("d4_a417_note", "netlist", "417", "note contains Forlinx 载板指引要求 ESD 紧贴接口"),
    ("d4_a418_value", "netlist", "418", "value == TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)"),
    ("d4_a432_net", "netlist", "432", "net == NET_USB_D_N_TYPEC"),
    ("d4_a432_ref", "netlist", "432", "ref == R_SER_USB_D_N"),
    ("d4_esd_pads", "board", "?", "footprint.D_ESD_USB_D.pads == 2"),
    ("d4_esd_value", "board", "?", "footprint.D_ESD_USB_D.value == ESD 阵列 [待选型] (USB 2.0 双通道)"),
    ("d4_esd_pad1_net", "board", "?", "footprint.D_ESD_USB_D.pad1.net == USB_D_P_SRC"),
    ("d4_esd_pad2_net", "board", "?", "footprint.D_ESD_USB_D.pad2.net == GND"),
    ("d4_esd_on_dminus", "board", "?", "esd_on_net(USB_D_N_SRC,NET_USB_D_N_TYPEC) == 0"),
    ("d4_bom62_value", "bom", "62", "value == TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)"),
    ("d4_bom62_fp", "bom", "62", "footprint contains 2 焊盘"),

    # ═══════════════════════════════════════════════════════════════════════
    # ★★第 2 轮 (ISS-214) 追加的 7 组锚点 (d5..d11) —— ★ISS-211 的 4 条 (d1..d4) 一条不许删★★
    # ═══════════════════════════════════════════════════════════════════════

    # ── 第 (1) 条 · USB 串阻: 同一颗器件两个阻值 (ISS-211 附带发现 #1) ──
    # ★★2026-11-16 ISS-223 落表第 2 批 (V-1 已由 main 裁 = 22Ω): 这 4 条【现状断言】
    #   跟着落表走 —— `d5_a291_value` / `d5_a292_value` (表A L291/L292 的 NET 行 value)
    #   由 `90Ω ±10%` 改为 `22Ω ±1%`; `d5_spec_b21_imp` / `d5_spec_b22_imp` 改为 `22Ω ±1%`。
    #   ★★【这不是「改判据凑绿」】: 判据本体 (L291/L292 的 NET 行 value 必须 == SPEC.json
    #   B-21/B-22 的 `imp`) 一个字没改, 改的只是【断言的现状值】⇒ ★**锚点条数一条没减
    #   (d5 组仍 16 条) · 判据阈值与 EXPECT 锚点组一条没删**★。
    #   ★**反向用例方向同步翻转 (见 `--selftest` 的 `m_spec_b21_imp`)**: 落表后现状已是
    #   22Ω ⇒ 反向用例改成【退回 90Ω 的旧缺陷】, 与 ISS-220 落表时 d1/d6 的处理同型。
    ('d5_a291_value', 'netlist', '291', 'value == 22Ω ±1%'),
    ('d5_a291_ref', 'netlist', '291', 'ref == NET_USB_D_P_SRC'),
    ('d5_a292_value', 'netlist', '292', 'value == 22Ω ±1%'),
    ('d5_a292_ref', 'netlist', '292', 'ref == NET_USB_D_N_SRC'),
    ('d5_a431_value', 'netlist', '431', 'value == 22Ω ±1%'),
    ('d5_a431_ref', 'netlist', '431', 'ref == R_SER_USB_D_P'),
    ('d5_a432_value', 'netlist', '432', 'value == 22Ω ±1%'),
    ('d5_a432_ref', 'netlist', '432', 'ref == R_SER_USB_D_N'),
    ('d5_a291_rows', 'netlist', '?', 'count(ref==NET_USB_D_P_SRC) == 1'),
    ('d5_a292_rows', 'netlist', '?', 'count(ref==NET_USB_D_N_SRC) == 1'),
    ('d5_spec_b21_imp', 'spec', '?', 'spec.connections[id=B-21].imp == 22Ω ±1%'),
    ('d5_spec_b21_signal', 'spec', '?', 'spec.connections[id=B-21].signal == USB_D+'),
    ('d5_spec_b22_imp', 'spec', '?', 'spec.connections[id=B-22].imp == 22Ω ±1%'),
    ('d5_spec_b22_signal', 'spec', '?', 'spec.connections[id=B-22].signal == USB_D-'),
    ('d5_emc_90_480', 'emc', '?', 'text contains D+/D- 90 Ω 差分, 480 Mbps'),
    ('d5_emc_template', 'emc', '?', 'text contains 不是同一套阻抗模板'),

    # ── 第 (2) 条 · CONN_LIGHT 21p vs 22p + P9 堆叠账 (ISS-213 STK-P9) ──
    ('d6_pages_light_21p', 'pages', '?', 'text notcontains `CONN_LIGHT` (**1×21p@0.5mm**)'),
    ('d6_pages_light_22p', 'pages', '?', 'text contains 1×22p@0.5mm'),
    ('d6_pages_cam_18p', 'pages', '?', 'text notcontains `CONN_CAM` (**18p@0.5mm**)'),
    ('d6_pages_cam_31p', 'pages', '?', 'text contains `CONN_CAM` (**31p@0.3mm'),
    ('d6_pages_usb_4p', 'pages', '?', 'text notcontains `CONN_USB` (**4p@0.5mm**)'),
    ('d6_pages_stack_265', 'pages', '?', 'text notcontains (10+4+18+21)×0.5 = **26.5mm**'),
    ('d6_pages_stack_370', 'pages', '?', 'text notcontains 镜脚根部净高 **37.0mm**'),
    ('d6_pages_stack_380', 'pages', '?', 'text contains 镜脚根部净高 **38.00mm**'),
    ('d6_a237_value', 'netlist', '237', 'value == ★22p@0.5mm (HIROSE FH12-22S-0.5SH(55), 右角/底接触/1固定柱; 官方封装抄 RPi CM5IO)'),
    ('d6_a237_board', 'netlist', '237', 'board == MAIN_PCB'),
    ('d6_a290_value', 'netlist', '290', 'value == ★31p@0.3mm 板内 FPC 座 (Radxa Camera 4K; 座 HIROSE FH35C-31S-0.3SHW(50); 针位见 HW/PCB/FPC_PIN_TABLES.md)'),
    ('d6_a290_board', 'netlist', '290', 'board == MAIN_PCB'),
    ('d6_b_light_pins', 'pins', '?', 'count(ref==CONN_LIGHT) == 22'),
    ('d6_b_cam_pins', 'pins', '?', 'count(ref==CONN_CAM) == 31'),
    ('d6_net_no_conusb', 'netlist', '?', 'count(ref==CONN_USB) == 0'),
    ('d6_bom5_value', 'bom', '5', 'value contains 22p@0.5mm'),
    ('d6_bom5_fp', 'bom', '5', 'footprint contains FH12-22S-0.5SH'),

    # ── 第 (3) 条 · SARADC_VIN5 满量程 + BAT_DET 分压比 (ISS-211 U-2) ──
    ('d7_a181_value', 'netlist', '181', 'value == 1M+1M 分压 + 100nF'),
    ('d7_a182_value', 'netlist', '182', 'value == 1M ±1%'),
    ('d7_a183_value', 'netlist', '183', 'value == 1M ±1%'),
    ('d7_a184_value', 'netlist', '184', 'value == 100nF ±10%'),
    ('d7_a186_node1', 'netlist', '186', 'node1 == J_SOM_P1 pin38'),
    ('d7_a186_dnp', 'netlist', '186', 'dnp == 必装'),
    ('d7_rk_table', 'rk', '?', 'text contains Table 3-16 Electrical Characteristics for SARADC'),
    ('d7_rk_resolution', 'rk', '?', 'text contains Resolution                                                                 NA           12         NA       Bit'),
    ('d7_rk_ain', 'rk', '?', 'text contains Anglog Input Range             AIN                                        AVSS18       NA         AVDD18    V'),
    ('d7_som_p138_signal', 'sompins', '39', 'signal == SARADC_VIN5'),
    ('d7_som_p138_vol', 'sompins', '39', 'vol == 1.8V'),
    ('d7_som_p138_num', 'sompins', '39', 'num == 38'),
    ('d7_node_v', 'netlist', '?', 'calc(node_v@4.2) == 2.1'),
    ('d7_node_over', 'netlist', '?', 'calc(node_v@4.2) > 1.8'),

    # ── 第 (4) 条 · BAT_DET 分压链漏电预算 (ISS-211 U-4) ──
    ('d8_a182_note', 'netlist', '182', 'note contains 漏电流 ~1.65µA @5V'),
    ('d8_bom86_value', 'bom', '86', 'value == 1M ±1%'),
    ('d8_bom86_dnp', 'bom', '86', 'dnp == DNP'),
    ('d8_bom87_value', 'bom', '87', 'value == 1M ±1%'),
    ('d8_bom87_dnp', 'bom', '87', 'dnp == DNP'),
    ('d8_bom27_value', 'bom', '27', 'value == 100nF ±10%'),
    ('d8_leak_now', 'netlist', '?', 'calc(leak_ua@4.2) == 2.1'),
    ('d8_leak_claim', 'netlist', '?', 'calc(leak_note_ua@5) == 1.65'),

    # ── 第 (5) 条 · USB D− 的 ESD 方案 + 型号判据 (ISS-211 U-1) ──
    ('d9_pages_esd_3mm', 'pages', '?', 'text contains ESD 距连接器 ≤3.0mm'),
    ('d9_pages_two_ends', 'pages', '?', 'text contains 两端 ESD'),
    ('d9_emc_480', 'emc', '?', 'text contains 480 Mbps'),
    ('d9_esd_dist', 'netlist', '?', 'calc(esd_dist_usb) > 5'),
    ('d9_esd_pads2', 'board', '?', 'footprint.D_ESD_USB_D.pads == 2'),
    # ★★ISS-257 落表同型 (★上面 d4_a417_value 的注释同样适用★): 网表侧已不写「双通道」自称
    #   ⇒ 这条锚点跟着改钉【落表后的真型号】; ★**板侧的「双通道」自称仍在** ⇒ ★**板待跟 (PCB 类)**★
    ('d9_esd_dual_claim', 'netlist', '417', 'value == TPD1E05U06DPYR (TI 单通道 ESD · X1SON-2 · Cd 0.42pF · VRWM 5.5V)'),
    ('d9_esd_on_dminus', 'board', '?', 'esd_on_net(USB_D_N_SRC,NET_USB_D_N_TYPEC) == 0'),

    # ── 第 (7) 条 · CHARGE_BOARD_SPEC §2.4/§3.4 的 ICHG/IIN 系数方向 (ISS-213 THM-RATIO) ──
    ('d10_spec_0822', 'chgspec', '?', 'text notcontains CC 段电池电流上限 (×Vbat/Vbus/η ≈ 0.822)'),
    ('d10_spec_ratio_1216', 'chgspec', '?', 'text contains ICHG/IIN = η·Vbus/Vbat = **1.216 @3.70V** / **1.071 @4.20V**'),
    ('d10_spec_formula', 'chgspec', '?', 'text notcontains ICHG ≈ IIN × (VBAT / VBUS) / η'),
    ('d10_spec_0822_val', 'chgspec', '?', 'text notcontains ICHG ≈ 0.822 × IIN'),
    ('d10_spec_script', 'chgspec', '?', 'text notcontains lo*0.822'),
    ('d10_spec_script_1216', 'chgspec', '?', 'text contains lo*1.216'),
    ('d10_spec_0411', 'chgspec', '?', 'text notcontains 单 pin 0.411A ≤ 0.5A 触点天花板'),
    ('d10_spec_0608', 'chgspec', '?', 'text contains 单 pin **0.608A**'),
    ('d10_a47_value', 'netlist', '47', 'value == 390Ω ±1% (IINMAX ≈1.00A · ICHG ≈1.22A · 单 pin 0.608A ⇒ 超 0.50A 工作上限 21.6% · 档位待 V-4 裁决)'),
    ('d10_a48_value', 'netlist', '48', 'value == 390Ω ±1% (IINMAX ≈1.00A · ICHG ≈1.22A · 单 pin 0.608A ⇒ 超 0.50A 工作上限 21.6% · 档位待 V-4 裁决)'),
    ('d10_bom97_value', 'bom', '97', 'value == 390Ω ±1% (IINMAX ≈1.00A · ICHG ≈1.22A · 单 pin 0.608A ⇒ 超 0.50A 工作上限 21.6% · 档位待 V-4 裁决)'),
    ('d10_a497_note', 'netlist', '497', 'note contains 工作上限 0.50A'),
    ('d10_ratio_370', 'netlist', '?', 'calc(ichg_ratio@3.7) == 1.216'),
    ('d10_ratio_420', 'netlist', '?', 'calc(ichg_ratio@4.2) == 1.071'),
    ('d10_pin_max_370', 'netlist', '?', 'calc(ichg_pin_max@3.7) == 0.608'),
    ('d10_pin_max_420', 'netlist', '?', 'calc(ichg_pin_max@4.2) == 0.536'),

    # ── 第 (8) 条 · NET-LED / C_VBUS_GND 的 board 列 (ISS-213 NET-LED) ──
    ('d11_a11_ref', 'netlist', '11', 'ref == C_VBUS_OUT'),
    ('d11_a11_board', 'netlist', '11', 'board == CHG_BOARD'),
    ('d11_a12_ref', 'netlist', '12', 'ref == C_VBUS_GND'),
    ('d11_a12_board', 'netlist', '12', 'board == CHG_BOARD'),
    ('d11_a13_ref', 'netlist', '13', 'ref == U_CHG'),
    ('d11_a13_board', 'netlist', '13', 'board == CHG_BOARD'),
    ('d11_a10_ref', 'netlist', '10', 'ref == C_VBUS_GND'),
    ('d11_a10_board', 'netlist', '10', 'board == CHG_BOARD'),
    ('d11_b148_board', 'pins', '148', 'board == CHG_BOARD'),
    ('d11_b149_board', 'pins', '149', 'board == CHG_BOARD'),
    ('d11_b154_board', 'pins', '154', 'board == CHG_BOARD'),
    ('d11_b155_board', 'pins', '155', 'board == CHG_BOARD'),
    ('d11_led508_board', 'netlist', '508', 'board == CHG_BOARD'),
    ('d11_led509_board', 'netlist', '509', 'board == CHG_BOARD'),
    ('d11_led_refs', 'netlist', '?', 'count(ref==R_CHG_LED) == 2'),
    ('d11_board_cvbgnd_pads', 'board', '?', 'footprint.C_VBUS_GND.pads == 2'),
    ('d11_board_cvbgnd_pad2', 'board', '?', 'footprint.C_VBUS_GND.pad2.net == VBUS_5V_CHG'),
    ('d11_board_no_cvbout', 'board', '?', 'count_footprint(C_VBUS_OUT) == 0'),
]


# ═════════════════════════════════════════════════════════════════════════════
# ★★ISS-217: 落表作业包三方对齐表 (★唯一真源 = 本表★) ★★
# ═════════════════════════════════════════════════════════════════════════════
# ★**id**            作业包里的项号 (必须逐个出现, 缺一个就红)
# ★**loc**           作业包 ① 栏必须逐字写出的规格页定位串
# ★**sec / mark**    规格页的哪一节 / 该节里必须存在的标记 (★三方对齐的"规格页那一侧"★)
# ★**head**          mark 是否必须出现在【标题行】(★§1 / §10 的条号是标题; §11 / §13 是正文★)
# ★**anchor**        门禁 EXPECT 里的锚点组前缀 (★三方对齐的"门禁锚点那一侧"★)
# ★**r**             作业包 ⑦ 栏必须声明的翻面判据 R# 集合 (★三方对齐的"翻面判据那一侧"★)
# ★**absorb**        该条目被吸收到哪个主项 (★None = 它自己就是主项★)
WP_MAP: dict[str, dict] = {
    # ── 主项 d1..d11 (★规格页 §1 四条 + §10 七组 = ISS-211 的 4 条 + ISS-214 的 8 条★) ──
    "d1":  {"loc": "§1 第 (1) 条",  "sec": 1,  "mark": "第 (1) 条", "head": True,
            "anchor": "d1",  "r": ("R1",),          "absorb": None},
    "d2":  {"loc": "§1 第 (2) 条",  "sec": 1,  "mark": "第 (2) 条", "head": True,
            "anchor": "d2",  "r": ("R2",),          "absorb": None},
    "d3":  {"loc": "§1 第 (3) 条",  "sec": 1,  "mark": "第 (3) 条", "head": True,
            "anchor": "d3",  "r": ("R3",),          "absorb": None},
    "d4":  {"loc": "§1 第 (4) 条",  "sec": 1,  "mark": "第 (4) 条", "head": True,
            "anchor": "d4",  "r": ("R4", "R9"),     "absorb": None},
    "d5":  {"loc": "§10 第 (1) 条", "sec": 10, "mark": "第 (1) 条", "head": True,
            "anchor": "d5",  "r": ("R5",),          "absorb": None},
    "d6":  {"loc": "§10 第 (2) 条", "sec": 10, "mark": "第 (2) 条", "head": True,
            "anchor": "d6",  "r": ("R6",),          "absorb": None},
    "d7":  {"loc": "§10 第 (3) 条", "sec": 10, "mark": "第 (3) 条", "head": True,
            "anchor": "d7",  "r": ("R2", "R7"),     "absorb": None},
    "d8":  {"loc": "§10 第 (4) 条", "sec": 10, "mark": "第 (4) 条", "head": True,
            "anchor": "d8",  "r": ("R8",),          "absorb": None},
    "d9":  {"loc": "§10 第 (5) 条", "sec": 10, "mark": "第 (5) 条", "head": True,
            "anchor": "d9",  "r": ("R4", "R9"),     "absorb": None},
    "d10": {"loc": "§10 第 (7) 条", "sec": 10, "mark": "第 (7) 条", "head": True,
            "anchor": "d10", "r": ("R10",),         "absorb": None},
    "d11": {"loc": "§10 第 (8) 条", "sec": 10, "mark": "第 (8) 条", "head": True,
            "anchor": "d11", "r": ("R11",),         "absorb": None},
    # ── 规格页 §11 附带发现 #1..#8 (★§11 自己写明每条"已并进第 (N) 条"★) ──
    "#1":  {"loc": "§11 附带发现 #1", "sec": 11, "mark": "#1 ·", "head": False,
            "anchor": "d5",  "r": ("R5",),  "absorb": "d5"},
    "#2":  {"loc": "§11 附带发现 #2", "sec": 11, "mark": "#2 ·", "head": False,
            "anchor": "d8",  "r": ("R8",),  "absorb": "d8"},
    "#3":  {"loc": "§11 附带发现 #3", "sec": 11, "mark": "#3 ·", "head": False,
            "anchor": "d9",  "r": ("R9",),  "absorb": "d9"},
    "#4":  {"loc": "§11 附带发现 #4", "sec": 11, "mark": "#4 ·", "head": False,
            "anchor": "d11", "r": ("R11",), "absorb": "d11"},
    "#5":  {"loc": "§11 附带发现 #5", "sec": 11, "mark": "#5 ·", "head": False,
            "anchor": "d11", "r": ("R11",), "absorb": "d11"},
    "#6":  {"loc": "§11 附带发现 #6", "sec": 11, "mark": "#6 ·", "head": False,
            "anchor": "d11", "r": ("R11",), "absorb": "d11"},
    "#7":  {"loc": "§11 附带发现 #7", "sec": 11, "mark": "#7 ·", "head": False,
            "anchor": "d11", "r": ("R11",), "absorb": "d11"},
    "#8":  {"loc": "§11 附带发现 #8", "sec": 11, "mark": "#8 ·", "head": False,
            "anchor": "d10", "r": ("R10",), "absorb": "d10"},
    # ── ISS-217 的 3 项补差 (★规格页 §11 里还没被规格覆盖的那几条★) ──
    "补差A": {"loc": "§11 附带发现 #1",   "sec": 11, "mark": "#1 ·", "head": False,
              "anchor": "d5",  "r": ("R5",),  "absorb": "d5"},
    "补差B": {"loc": "§11 附带发现 #3",   "sec": 11, "mark": "#3 ·", "head": False,
              "anchor": "d9",  "r": ("R9",),  "absorb": "d9"},
    "补差C": {"loc": "§11 附带发现 #4 / #6", "sec": 11, "mark": "#4 ·", "head": False,
              "anchor": "d11", "r": ("R11",), "absorb": "d11"},
    # ── 6 条待裁确认单 (★规格页 §13 V-1..V-6★) ──
    "待裁V-1": {"loc": "§13 V-1", "sec": 13, "mark": "V-1", "head": False,
                "anchor": "d5",  "r": ("R5",),           "absorb": "d5"},
    "待裁V-2": {"loc": "§13 V-2", "sec": 13, "mark": "V-2", "head": False,
                "anchor": "d9",  "r": ("R4", "R9"),      "absorb": "d9"},
    "待裁V-3": {"loc": "§13 V-3", "sec": 13, "mark": "V-3", "head": False,
                "anchor": "d7",  "r": ("R2", "R7", "R8"), "absorb": "d7"},
    "待裁V-4": {"loc": "§13 V-4", "sec": 13, "mark": "V-4", "head": False,
                "anchor": "d10", "r": ("R10",),          "absorb": "d10"},
    "待裁V-5": {"loc": "§13 V-5", "sec": 13, "mark": "V-5", "head": False,
                "anchor": "d6",  "r": ("R6",),           "absorb": "d6"},
    "待裁V-6": {"loc": "§13 V-6", "sec": 13, "mark": "V-6", "head": False,
                "anchor": "d9",  "r": ("R9",),           "absorb": "d9"},
}

# ★作业包条目的机器可读块 (★格式由本脚本定义, 作业包必须照这个格式写★) ★
WP_ITEM_RE = re.compile(r"<!-- WPITEM:BEGIN id=(.+?) -->\n(.*?)\n<!-- WPITEM:END -->", re.S)
WP_MARKS = "①②③④⑤⑥⑦⑧"
# ★④ 栏里的"真修法文件"必须落在工程里真实存在的文件 (★后缀白名单★) ★
WP_FILE_RE = re.compile(r"[A-Za-z0-9_./-]+\.(?:py|json|md|csv|txt|yaml|yml|net|kicad_pcb|kicad_pro)")

# ★★工程相对路径索引 (★建一次, 缓存在模块级★)
_WP_PATH_INDEX: list[str] | None = None


def _wp_project_paths() -> list[str]:
    """工程里所有文件的相对路径 (★只索引一次★)。"""
    global _WP_PATH_INDEX
    if _WP_PATH_INDEX is None:
        idx: list[str] = []
        base = DEFAULT_ROOT
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames
                           if d not in (".git", "__pycache__", "node_modules", ".openclaw", ".clawhub")]
            for fn in filenames:
                idx.append(os.path.relpath(os.path.join(dirpath, fn), base).replace(os.sep, "/"))
        _WP_PATH_INDEX = idx
    return _WP_PATH_INDEX


def _wp_path_ok(root: str, token: str) -> bool:
    """作业包 ④ 栏里写的路径是不是工程里真实存在的文件。

    ★先在【被检查的 root】下找; 找不到再到【脚本自己所在的工程根】下找
    (★自检时 root 是临时副本, 里面只拷了门禁要读的那几份文件, 而作业包 ④ 栏
    指的是工程里的真源 ⇒ 落到临时副本上会误报"文件不存在"★);
    再不行按【后缀】匹配 (★裸文件名如 SPEC.json → HW/SCHEMATIC_V1_SPEC.json★)。"""
    t = token.replace("\\", "/")
    while t.startswith("./"):
        t = t[2:]
    for base in (root, DEFAULT_ROOT):
        if os.path.isfile(os.path.join(base, t)):
            return True
    for rel in _wp_project_paths():
        if rel == t or rel.endswith("/" + t):
            return True
    return False


class CheckError(Exception):
    """rc=2: 环境/用法错误"""


# ─────────────────────────────────────────────────────────────────────────────
# 读文件
# ─────────────────────────────────────────────────────────────────────────────

def _path(root: str, key: str) -> str:
    return os.path.join(root, REL[key])


def _read_rows(path: str) -> list[dict]:
    """带行号 (CSV 物理行号, 1-based, 表头 = 第 1 行) 的读取。"""
    if not os.path.exists(path):
        raise CheckError(f"★缺文件: {path}")
    with open(path, encoding="utf-8", newline="") as fh:
        raw = fh.read()
    rows = list(csv.reader(raw.split("\n")))
    while rows and rows[-1] == []:
        rows.pop()
    if not rows:
        raise CheckError(f"★空文件: {path}")
    head = rows[0]
    out = []
    for i, r in enumerate(rows[1:]):
        if len(r) != len(head):
            # 列数不齐的行仍然读进来, 缺的补空串 (便于报告)
            r = r + [""] * (len(head) - len(r))
        d = dict(zip(head, r))
        d["_line"] = i + 2
        out.append(d)
    return out


def _read_json(path: str):
    if not os.path.exists(path):
        raise CheckError(f"★缺文件: {path}")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _read_board(path: str) -> dict:
    """解析板文件: {ref: {"value":…, "pads":N, "padN.net":…}}。只读。"""
    if not os.path.exists(path):
        raise CheckError(f"★缺文件: {path}")
    with open(path, encoding="utf-8") as fh:
        s = fh.read()
    out: dict[str, dict] = {}
    for m in re.finditer(r"\(footprint ", s):
        i = m.start()
        depth = 0
        j = i
        while j < len(s):
            if s[j] == "(":
                depth += 1
            elif s[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        blk = s[i:j + 1]
        rm = re.search(r'\(property "Reference" "([^"]*)"', blk)
        if not rm:
            continue
        ref = rm.group(1)
        if ref in out:
            continue
        vm = re.search(r'\(property "Value" "([^"]*)"', blk)
        pads = []
        for pm in re.finditer(r'\(pad "([^"]*)"', blk):
            num = pm.group(1)
            rest = blk[pm.end():pm.end() + 1200]
            nm = re.search(r'\(net "([^"]*)"\)', rest)
            pads.append((num, nm.group(1) if nm else ""))
        info = {"value": vm.group(1) if vm else "", "pads": len(pads), "pads_list": pads}
        for idx, (_num, net) in enumerate(pads, start=1):
            info[f"pad{idx}.net"] = net
        out[ref] = info
    return out


# ─────────────────────────────────────────────────────────────────────────────
# 迷你判据 DSL 求值
# ─────────────────────────────────────────────────────────────────────────────

def _norm(s: str) -> str:
    return (s or "").strip()


def _split_call(check: str, name: str) -> tuple[str, str]:
    """把 'name(<参数>) == <期望>' 拆成 (<参数>, <期望>)。★谓词里可能含 '==', 所以按括号配平拆★"""
    idx = check.index("(")
    depth = 0
    for j in range(idx, len(check)):
        if check[j] == "(":
            depth += 1
        elif check[j] == ")":
            depth -= 1
            if depth == 0:
                break
    else:
        raise CheckError(f"★判据括号不配平: {check!r}")
    pred = check[idx + 1:j]
    rhs = check[j + 1:].strip()
    if not rhs.startswith("=="):
        raise CheckError(f"★判据缺 '==': {check!r}")
    return pred, rhs[2:].strip()


# ─────────────────────────────────────────────────────────────────────────────
# ★★第 2 轮 (ISS-214): 数值判据 calc(<expr>) <op> <num> ★★
# ─────────────────────────────────────────────────────────────────────────────

def _res_ohm(s: str) -> float | None:
    """'390Ω ±1%' / '1M ±1%' / '22Ω' → 欧姆。★M=兆 / m=毫 / k=千, 大小写区分★★"""
    s = (s or "").strip()
    m = re.search(r"([\d.]+)\s*([kKmMrRΩΩ]|ohm)?", s)
    if not m:
        return None
    try:
        v = float(m.group(1))
    except ValueError:
        return None
    unit = m.group(2) or ""
    if unit in ("k", "K"):
        v *= 1e3
    elif unit in ("M",):          # ★兆 (1M = 1e6) ★
        v *= 1e6
    elif unit in ("m",):          # ★毫 ★
        v *= 1e-3
    return v


def _net_rows(ctx: dict) -> list[dict]:
    return ctx.get("rows") or []


def _ref_value(ctx: dict, ref: str) -> str:
    for r in _net_rows(ctx):
        if _norm(r.get("ref")) == ref:
            return r.get("value") or ""
    return ""


def _ref_note(ctx: dict, ref: str) -> str:
    for r in _net_rows(ctx):
        if _norm(r.get("ref")) == ref:
            return r.get("note") or ""
    return ""


def _board_xy(root: str) -> dict:
    return _board_ref_xy(os.path.join(root, REL["board"]))


def _calc_expr(ctx: dict, expr: str) -> float | None:
    """算出一个数值 (★None = 算不出来★)。"""
    expr = expr.strip()

    if expr.startswith("node_v@"):
        v = float(expr.split("@", 1)[1])
        top = _res_ohm(_ref_value(ctx, "R_BAT_DET_1"))
        bot = _res_ohm(_ref_value(ctx, "R_BAT_DET_2"))
        if not top or not bot or top + bot <= 0:
            return None
        return v * bot / (top + bot)

    if expr.startswith("leak_ua@"):
        v = float(expr.split("@", 1)[1])
        top = _res_ohm(_ref_value(ctx, "R_BAT_DET_1"))
        bot = _res_ohm(_ref_value(ctx, "R_BAT_DET_2"))
        if not top or not bot or top + bot <= 0:
            return None
        return v * 1e6 / (top + bot)

    if expr.startswith("leak_note_ua@"):
        note = _ref_note(ctx, "R_BAT_DET_1")
        m = re.search(r"~\s*([\d.]+)\s*[µμ]A", note)
        if not m:
            return None
        return float(m.group(1))

    if expr == "esd_dist_usb":
        xy = _board_xy(ctx["root"])
        a, b = xy.get("J_USB_C"), xy.get("D_ESD_USB_D")
        if not a or not b:
            return None
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    if expr == "r_ilim":
        return _res_ohm(_ref_value(ctx, "R_ILIM"))

    if expr == "iinmax_max":
        r = _res_ohm(_ref_value(ctx, "R_ILIM"))
        if not r:
            return None
        return KILIM_MAX / r

    if expr.startswith("ichg_ratio@"):
        vbat = float(expr.split("@", 1)[1])
        if vbat <= 0:
            return None
        return ETA_BUCK * VBUS_CHG / vbat

    if expr.startswith("ichg_max@"):
        vbat = float(expr.split("@", 1)[1])
        r = _res_ohm(_ref_value(ctx, "R_ILIM"))
        if not r:
            return None
        return (KILIM_MAX / r) * (ETA_BUCK * VBUS_CHG / vbat)

    if expr.startswith("ichg_pin_max@"):
        vbat = float(expr.split("@", 1)[1])
        r = _res_ohm(_ref_value(ctx, "R_ILIM"))
        if not r:
            return None
        return (KILIM_MAX / r) * (ETA_BUCK * VBUS_CHG / vbat) / 2.0

    return None


def _eval_calc(ctx: dict, check: str) -> tuple[bool, str]:
    """calc(<expr>) <op> <num> → (ok, 实际值文本)。"""
    m = re.match(r"^calc\(([^)]*)\)\s*(==|>=|<=|>|<)\s*(-?[\d.]+)\s*$", check)
    if not m:
        return False, f"★calc 判据写法不认识: {check!r}"
    expr, op, rhs = m.group(1), m.group(2), float(m.group(3))
    got = _calc_expr(ctx, expr)
    if got is None:
        return False, f"★calc({expr}) 算不出来 (★现行文件缺数据?)"
    tol = max(1e-3, abs(rhs) * 1e-3)
    if op == "==":
        ok = abs(got - rhs) <= tol
    elif op == ">":
        ok = got > rhs
    elif op == ">=":
        ok = got >= rhs - tol
    elif op == "<":
        ok = got < rhs
    else:  # "<="
        ok = got <= rhs + tol
    return ok, f"calc({expr})={got:.6g} {op} {rhs:g} ⇒ {ok}"


def _eval_check(ctx: dict, check: str) -> tuple[bool, str]:
    """返回 (ok, 实际值文本)。"""
    check = check.strip()

    # ★★第 2 轮 (ISS-214): 'text contains X' / 'text notcontains X' (★必须最先判,
    #    否则会被下面那条通用的 "field contains value" 正则抢走★★)
    if check.startswith("text contains ") or check.startswith("text notcontains "):
        neg = check.startswith("text notcontains ")
        want = check.split(" ", 2)[2].strip()
        body = ctx.get("text", "")
        hit = want in body
        ok = (not hit) if neg else hit
        return ok, f"{'not ' if neg else ''}contains {want!r} ⇒ {hit}"

    # ★★第 2 轮 (ISS-214): 'calc(<expr>) <op> <num>' 数值判据 ★★
    if check.startswith("calc("):
        return _eval_calc(ctx, check)

    # ★"field contains value" (★必须先判, 因为它不含 '==')
    cm = re.match(r"^(\w+)\s+contains\s+(.*)$", check)
    if cm:
        field, want = cm.group(1), cm.group(2).strip()
        got = _norm(ctx.get("row", {}).get(field, ""))
        return want in got, f"{field}={got!r}"

    # ★count(<pred>) == N  (★必须先判: 谓词里含 '==', 不能用朴素的 split★)
    if check.startswith("count("):
        pred, want = _split_call(check, "count")
        rows = ctx["rows"]
        n = 0
        for r in rows:
            ok = True
            for term in pred.split("&"):
                term = term.strip()
                if not term:
                    continue
                if "!=" in term:
                    f, v = term.split("!=", 1)
                    if _norm(r.get(f, "")) == _norm(v):
                        ok = False
                        break
                elif "==" in term:
                    f, v = term.split("==", 1)
                    if _norm(r.get(f, "")) != _norm(v):
                        ok = False
                        break
            if ok:
                n += 1
        return str(n) == want, f"count={n}"

    if "==" not in check:
        return False, f"★判据写法不认识: {check!r}"
    lhs, rhs = check.split("==", 1)
    lhs = lhs.strip()
    rhs = rhs.strip()
    want = rhs

    # count(<pred>) == N  (★已在上头单独处理, 这里不该再到★)
    if lhs.startswith("count("):
        return False, f"★count 判据解析失败: {check!r}"

    # footprint.<REF>.<attr> == v
    if lhs.startswith("footprint."):
        body = lhs[len("footprint."):]
        ref, _, attr = body.partition(".")
        fps = ctx["board"]
        if ref not in fps:
            return False, f"★板文件里没有位号 {ref!r}"
        info = fps[ref]
        if attr == "pads":
            return str(info["pads"]) == want, f"pads={info['pads']}"
        if attr == "value":
            return _norm(info["value"]) == want, f"value={info['value']!r}"
        if attr.endswith(".net"):
            got = info.get(attr, "")
            return _norm(got) == want, f"{attr}={got!r}"
        return False, f"★板属性不认识: {attr!r}"

    # spec.<path> == v
    if lhs.startswith("spec."):
        path = lhs[len("spec."):]
        obj = ctx["spec"]
        m = re.fullmatch(r"connections\[id=([^\]]+)\]\.(\w+)", path)
        if m:
            cid, field = m.group(1), m.group(2)
            hit = [c for c in obj.get("connections", []) if c.get("id") == cid]
            if not hit:
                return False, f"★SPEC.json 里没有 connections id={cid!r}"
            got = hit[0].get(field, "")
            return _norm(got) == want, f"{path}={got!r}"
        # 普通点路径
        cur = obj
        for part in path.split("."):
            if isinstance(cur, dict):
                cur = cur.get(part, "")
            else:
                return False, f"★SPEC 路径走不通: {path}"
        return _norm(cur) == want, f"{path}={cur!r}"

    # esd_on_net(<netA>,<netB>) == N
    if lhs.startswith("esd_on_net("):
        body = lhs[len("esd_on_net("):]
        body = body[:-1] if body.endswith(")") else body
        nets = {n.strip() for n in body.split(",") if n.strip()}
        fps = ctx["board"]
        n = 0
        for ref, info in fps.items():
            if "ESD" not in ref.upper():
                continue
            for _num, net in info.get("pads_list", []):
                if net in nets:
                    n += 1
                    break
        return str(n) == want, f"esd_on_net={n}"

    # count_footprint(<REF>) == N  (★第 2 轮: 板文件里有没有这个位号的封装★)
    if lhs.startswith("count_footprint("):
        body = lhs[len("count_footprint("):]
        body = body[:-1] if body.endswith(")") else body
        ref = body.strip()
        fps = ctx["board"]
        n = sum(1 for r in fps if r == ref)
        return str(n) == want, f"count_footprint({ref})={n}"

    # 普通列比较
    field = lhs
    if field == "count":
        return False, "★count 判据要写成 count(...)"
    got = _norm(ctx.get("row", {}).get(field, ""))
    return got == want, f"{field}={got!r}"


def _parse_contains(check: str) -> tuple[str, str] | None:
    m = re.match(r"^(\w+)\s+contains\s+(.*)$", check)
    if m:
        return m.group(1), m.group(2).strip()
    return None


# ─────────────────────────────────────────────────────────────────────────────
# 规格页锚点表 (判据 a 的另一半: 规格页 ⇄ 本脚本)
# ─────────────────────────────────────────────────────────────────────────────

ANCHOR_ROW_RE = re.compile(r"^\|\s*([a-z0-9_]+)\s*\|\s*([a-z]+)\s*\|\s*(\d+|\?)\s*\|\s*(.+?)\s*\|\s*$")
ANCHOR_BEGIN = "<!-- ANCHORS:BEGIN -->"
ANCHOR_END = "<!-- ANCHORS:END -->"


def parse_spec_anchors(path: str) -> dict[str, tuple[str, str, str]]:
    if not os.path.exists(path):
        raise CheckError(f"★缺文件: {path}")
    with open(path, encoding="utf-8") as fh:
        txt = fh.read()
    if ANCHOR_BEGIN not in txt or ANCHOR_END not in txt:
        raise CheckError(f"★规格页里没有锚点表 (需要 {ANCHOR_BEGIN} … {ANCHOR_END})")
    body = txt.split(ANCHOR_BEGIN, 1)[1].split(ANCHOR_END, 1)[0]
    out: dict[str, tuple[str, str, str]] = {}
    for line in body.split("\n"):
        if not line.strip().startswith("|"):
            continue
        m = ANCHOR_ROW_RE.match(line.strip())
        if not m:
            continue
        key, f, line_no, chk = m.group(1), m.group(2), m.group(3), m.group(4)
        out[key] = (f, line_no, chk)
    return out


def emit_anchor_table() -> str:
    """把 EXPECT 渲染成规格页用的 markdown 锚点表。"""
    lines = ["| key | file | line | check |", "|---|---|---|---|"]
    for key, f, ln, chk in EXPECT:
        lines.append(f"| {key} | {f} | {ln} | {chk} |")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 主检查
# ─────────────────────────────────────────────────────────────────────────────

def _row_at(rows: list[dict], line_no: str) -> dict:
    if line_no == "?":
        return {}
    n = int(line_no)
    for r in rows:
        if r["_line"] == n:
            return r
    raise CheckError(f"★行号 {n} 不在 {len(rows)} 行里 (文件被截断?)")


# ─────────────────────────────────────────────────────────────────────────────
# ★★ISS-217: 作业包完整性 + 三方对齐 (★"作业包漏一条就红"★)
# ─────────────────────────────────────────────────────────────────────────────

def _spec_section(text: str, num: int) -> str | None:
    """取规格页 '## N. …' 那一节的正文 (到下一节 '## M.' 为止)。"""
    m = re.search(rf"^##\s+{num}\.\s.*$", text, re.M)
    if not m:
        return None
    start = m.end()
    m2 = re.search(r"^##\s+\d+\.\s", text[start:], re.M)
    end = start + (m2.start() if m2 else len(text) - start)
    return text[start:end]


def _wp_fields(body: str) -> dict[str, str]:
    """把一条作业条目的 ①..⑧ 栏抽成 {栏位: 内容}。

    ★★栏位可以跨多行 (★本作业包里 d10 / 补差A / 待裁V-2… 的 ⑤ 栏带表格与子列表★):
    一个栏位的内容 = 从它的起始行到【下一个栏位起始行】之间的全部行。★★
    """
    out: dict[str, str] = {}
    cur: str | None = None
    buf: list[str] = []
    for line in body.split("\n"):
        hit = None
        for mark in WP_MARKS:
            if line.startswith(mark):
                hit = mark
                break
        if hit:
            if cur is not None:
                out[cur] = "\n".join(buf).strip()
            cur = hit
            rest = line[len(hit):].lstrip()
            if rest.startswith(":"):
                rest = rest[1:].strip()
            elif rest.startswith("："):
                rest = rest[1:].strip()
            buf = [rest]
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out[cur] = "\n".join(buf).strip()
    return out


def check_workpacket(root: str, verbose: bool = False) -> tuple[int, list[str]]:
    """落表作业包完整性 + 三方对齐 (★作业包 ↔ 规格页 ↔ 门禁 R#★)。"""
    errors: list[str] = []
    report: list[str] = []
    path = _path(root, "workpacket")
    if not os.path.exists(path):
        return 1, [f"★缺文件: {REL['workpacket']} (★ISS-217 落表作业包本体, "
                   f"★没有它, 落表那趟就没有 SOP★)"]
    with open(path, encoding="utf-8") as fh:
        wp = fh.read()
    specpage_path = _path(root, "specpage")
    spec_text = ""
    if os.path.exists(specpage_path):
        with open(specpage_path, encoding="utf-8") as fh:
            spec_text = fh.read()

    # ---- ① 解析作业包条目 (★重复 id 也要红★) ----
    items: dict[str, str] = {}
    for m in WP_ITEM_RE.finditer(wp):
        bid = m.group(1).strip()
        if bid in items:
            errors.append(f"★作业包里项号 {bid!r} 出现了两次 ⇒ 落表那趟会不知道听谁的 ⇒ 红")
        items[bid] = m.group(2)
    extra = sorted(set(items) - set(WP_MAP))
    for bid in extra:
        errors.append(f"★作业包里多出项号 {bid!r} (★门禁的 WP_MAP 里没有 ⇒ 对不上★)")
    for bid in sorted(WP_MAP):
        if bid not in items:
            errors.append(f"★作业包里**缺** {bid!r} 这一组 ⇒ 落表作业包漏一条就红")

    # ---- ② 逐条查 8 栏 + 三方对齐 ----
    exp_anchor_prefixes = {k.split("_", 1)[0] for k, _, _, _ in EXPECT if "_" in k}
    for bid, meta in WP_MAP.items():
        if bid not in items:
            continue
        f = _wp_fields(items[bid])
        missing = [m for m in WP_MARKS if not f.get(m, "").strip()]
        if missing:
            errors.append(f"★作业包 {bid!r} 缺栏位 {''.join(missing)} (★8 栏一字不许少★)")
            continue
        f1 = f["①"].replace("*", "")
        f4 = f["④"]
        f5 = f["⑤"]
        f6 = f["⑥"]
        f7 = f["⑦"].replace("*", "")

        # ① 项号: 必须逐字写出规格页定位串; 有吸收项的必须写"吸收到 X"
        if meta["loc"] not in f1:
            errors.append(f"★作业包 {bid!r} 的 ① 栏没有写规格页定位串 {meta['loc']!r} "
                          f"(★三方对齐: 作业包项号 ↔ 规格页条号★)")
        if meta["absorb"]:
            if "吸收到" not in f1 or meta["absorb"] not in f1:
                errors.append(f"★作业包 {bid!r} 的 ① 栏没有写『吸收到 {meta['absorb']}』 "
                              f"(★规格页 §11 写明每条已并进哪一条★)")

        # ④ 真修法文件: 必须至少指到一个工程里真实存在的文件
        files = [m.group(0) for m in WP_FILE_RE.finditer(f4)]
        real = [p for p in files if _wp_path_ok(root, p)]
        if not real:
            errors.append(f"★作业包 {bid!r} 的 ④ 栏没有指到工程里真实存在的文件 "
                          f"(★找到的路径 = {files or '无'}★) ⇒ 真修法没写清楚")
        elif len(f4.strip()) < 20:
            errors.append(f"★作业包 {bid!r} 的 ④ 栏太短 (★真修法要精确到: 哪个文件的哪一行 / "
                          f"哪个 JSON key / 哪个生成器参数★)")

        # ⑤ 改法: 必须有实质内容 (★长度 + 有反引号字面值 + 不许是占位符★)
        if len(f5.strip()) < 40:
            errors.append(f"★作业包 {bid!r} 的 ⑤ 栏 (改法) 太短 ⇒ 落表那趟没法照做")
        elif "`" not in f5:
            errors.append(f"★作业包 {bid!r} 的 ⑤ 栏 (改法) 没有字面值 (★要写清改成什么字面量★)")
        elif any(t in f5 for t in ("TODO", "待补", "待填", "XXX")):
            errors.append(f"★作业包 {bid!r} 的 ⑤ 栏 (改法) 还是占位符 ⇒ 落表那趟没法照做")

        # ⑥ 命令: 必须是可跑的命令
        if "python3" not in f6 or len(f6.strip()) < 20:
            errors.append(f"★作业包 {bid!r} 的 ⑥ 栏 (命令) 不是一条可跑的命令 ⇒ 落表那趟没法照做")

        # ⑦ 翻面判据: 必须逐个 R# 都写出来, 且与 WP_MAP 完全一致
        got_r = tuple(sorted(set(re.findall(r"R\d+", f7))))
        want_r = tuple(sorted(set(meta["r"])))
        if got_r != want_r:
            errors.append(f"★作业包 {bid!r} 的 ⑦ 栏 (翻面判据) 写的是 {list(got_r)} "
                          f"⇒ 门禁这边是 {list(want_r)} ⇒ 三方对齐失败")

        # 三方对齐 · 规格页那一侧: 该节里必须真的有那个标记
        sec = _spec_section(spec_text, meta["sec"]) if spec_text else None
        if sec is None:
            errors.append(f"★规格页里找不到 §{meta['sec']} 这一节 ⇒ 三方对齐失败 (项号 {bid!r})")
        elif meta["head"]:
            if not any(meta["mark"] in h for h in re.findall(r"^#{2,4}\s.*$", sec, re.M)):
                errors.append(f"★规格页 §{meta['sec']} 里没有标题含 {meta['mark']!r} "
                              f"⇒ 作业包项号 ↔ 规格页条号 对不上 (项号 {bid!r})")
        else:
            if meta["mark"] not in sec:
                errors.append(f"★规格页 §{meta['sec']} 里没有 {meta['mark']!r} "
                              f"⇒ 作业包项号 ↔ 规格页条号 对不上 (项号 {bid!r})")

        # 三方对齐 · 门禁锚点那一侧: EXPECT 里必须有该锚点组的 key
        if meta["anchor"] not in exp_anchor_prefixes:
            errors.append(f"★门禁 EXPECT 里没有锚点组 {meta['anchor']}_* ⇒ "
                          f"作业包项号 ↔ 门禁锚点组 对不上 (项号 {bid!r})")

        if verbose:
            report.append(f"   {'OK  ' if not errors else '    '} 作业包 {bid:<10} "
                          f"规格页={meta['loc']:<18} 锚点={meta['anchor']:<4} "
                          f"R#={','.join(want_r)}")

    if verbose:
        report.append(f"── 作业包: {len(items)} 条 (门禁要求 {len(WP_MAP)} 条) ──")
    return (1 if errors else 0), errors + report


# ═══════════════════════════════════════════════════════════════════════════════
# ★★F-3 遗留的【加强型断言】 (★ISS-230 · 2026-11-16 · hw-lead★)
# ═══════════════════════════════════════════════════════════════════════════════
# ★**判据**: A 组【已迁移过的那 20 条】在 `HW/SCHEMATIC_V1_SPEC.json` 里必须
#   ★**`z_diff` 非空 且 `imp` 为空**★ (差分阻抗只许住在 `z_diff` 字段里)。
# ★**为什么必须有这条断言 (★F-3 的原话★)**:
#   补差A (2026-11-16 ISS-223) 把「差分阻抗」从 `imp` 搬进了 `z_diff`, 而
#   `state/check_netlist.py` 判据 5 的比对源是【`imp` or `z_diff`】⇒
#   ★**谁把差分阻抗塞回 `imp` 并把 `z_diff` 清空, 判据 5 照样全绿 (它先读到了 `imp`)
#   ⇒ 字段分工被静默破坏 ⇒ 这条断言把【字段分工本身】锁死★**。
# ★**为什么【只针对这 20 条】(★两个坑各会造一批假红★)**:
#   ① A 组一共 **22** 条 (A-01~A-22); 另 2 条 (A-11 / A-12) 是★**单端**★连接
#      (`imp` = "单端, 需包地" / "单端", `z_diff` 天然为空) ⇒ 它们本来就该 `imp` 非空、
#      `z_diff` 为空 ⇒ 拖进来 = 造 **2** 条假红。
#   ② ★**更不许把网表里 `conn_id=A-24` 的 15 条 NET 行拖进来★**: 那 15 条是
#      `J_TYPE_C` 16p 母座的功能串 (GND / USB_CC1 / USB_CC2 / CARRIER_BOARD_EN /
#      RAIL_DEMO_5V / RAIL_BOARD_5V 等) ⇒ ★**本来就没有阻抗值**★ ⇒ 拖进来 = 造 **15** 条真红。
#   (★main 2026-11-16 05:5x 实测基线: `state/check_netlist.py` 判据 5 覆盖 **37** 条 A 组 NET 行,
#     其中 want 非空、真正被比对的 **22** 条, 另 **15** 条因 `imp`/`z_diff` 双空而跳过 —— 那 15 条全是 A-24★)
MIGRATED_A_IDS: tuple[str, ...] = (
    "A-01", "A-02", "A-03", "A-04", "A-05", "A-06", "A-07", "A-08", "A-09", "A-10",
    "A-13", "A-14", "A-15", "A-16", "A-17", "A-18", "A-19", "A-20", "A-21", "A-22",
)
# ★单端连接 (★不进断言范围, 但要防着它们被误改成差分★)
SINGLE_ENDED_A_IDS: tuple[str, ...] = ("A-11", "A-12")


def check_a_group_field_discipline(root: str) -> tuple[int, list[str]]:
    """★F-3 加强型断言: A 组已迁移的 20 条必须 `z_diff` 非空 且 `imp` 为空。

    ★**独立于 EXPECT 锚点表** (★所以不会动 `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` 的
    锚点表 ⇒ 规格页 ⇄ 脚本的 160 条锚点一条没增没减★) —— 它是【纪律断言】, 不是【现状断言】。
    ★只进 `check_guard()` (现状守卫) ⇒ **不进 `check_resolved()`** ⇒ ★**`--expect-resolved`
    的「未落表条数」仍然是 21, 一条不多一条不少★**。
    """
    errors: list[str] = []
    report: list[str] = []
    spec = _read_json(_path(root, "spec"))
    by_id = {c.get("id"): c for c in spec.get("connections", [])}

    # ① 断言自身的集合自洽: 20 条必须真的都在 A 组里 (规格页漂移 ⇒ 断言先红)
    a_all = sorted(i for i, c in by_id.items() if c.get("group") == "A")
    not_in_a = [i for i in MIGRATED_A_IDS if by_id.get(i, {}).get("group") != "A"]
    if not_in_a:
        errors.append(
            f"★A组字段分工: {not_in_a} 不在 A 组里 (或 SPEC.json 里没有) ⇒ 断言集合本身漂移了")
    gone = [i for i in MIGRATED_A_IDS if i not in by_id]
    if gone:
        errors.append(f"★A组字段分工: SPEC.json 里缺 {gone} ⇒ 断言集合本身漂移了")

    # ② 逐条: `z_diff` 非空 且 `imp` 为空
    bad_zd: list[str] = []
    bad_imp: list[str] = []
    for cid in MIGRATED_A_IDS:
        c = by_id.get(cid)
        if not c:
            continue
        if not (c.get("z_diff") or "").strip():
            bad_zd.append(cid)
        if (c.get("imp") or "").strip():
            bad_imp.append(cid)
    if bad_zd:
        errors.append(
            f"★A组字段分工: {len(bad_zd)} 条已迁移连接的 `z_diff` 为空 {bad_zd} "
            f"⇒ 差分阻抗被清空了 (★必须住在 `z_diff`, 不许回落进 `imp`★)")
    if bad_imp:
        errors.append(
            f"★A组字段分工: {len(bad_imp)} 条已迁移连接的 `imp` 不为空 {bad_imp} "
            f"⇒ 差分阻抗被塞回【串阻/阻抗】字段了 (★`imp` 已被 `z_diff` 取代★)")

    # ③ 反向保护: 单端连接不许被误改成差分
    bad_single = [cid for cid in SINGLE_ENDED_A_IDS
                  if (by_id.get(cid, {}).get("z_diff") or "").strip()]
    if bad_single:
        errors.append(
            f"★A组字段分工: {bad_single} 是单端连接, `z_diff` 必须为空 "
            f"(★单端不许写差分阻抗★)")

    ok = not (bad_zd or bad_imp or bad_single or not_in_a or gone)
    report.append(
        f"   [加强型断言·F-3] A 组 {len(a_all)} 条 / 已迁移 {len(MIGRATED_A_IDS)} 条: "
        f"`z_diff` 非空 且 `imp` 为空 ⇒ {'✅ 全过' if ok else '★★红★★'} "
        f"(★A-11/A-12 单端与 A-24 那 15 条【不在】断言范围内★)")
    return (1 if errors else 0), errors + report


def check_guard(root: str, verbose: bool) -> tuple[int, list[str]]:
    """现状守卫: 规格页 ⇄ 本脚本 ⇄ 现行文件 三方对齐。"""
    errors: list[str] = []
    report: list[str] = []

    specpage = _path(root, "specpage")
    anchors = parse_spec_anchors(specpage)

    # ---- ① 规格页锚点表 ⇄ 本脚本 EXPECT (不许漂移) ----
    exp_map = {k: (f, ln, chk) for k, f, ln, chk in EXPECT}
    for key, want in exp_map.items():
        if key not in anchors:
            errors.append(f"★规格页锚点表里**缺** {key!r} ⇒ 规格页与门禁脚本漂移了")
    for key, got in anchors.items():
        if key not in exp_map:
            errors.append(f"★规格页锚点表里**多** {key!r} (脚本里没有) ⇒ 规格页与门禁脚本漂移了")
        elif got != exp_map[key]:
            errors.append(
                f"★锚点 {key!r} 规格页={got!r} ≠ 脚本={exp_map[key]!r} ⇒ 规格页与门禁脚本漂移了")

    # ---- ② 现行文件 ⇄ EXPECT ----
    ctx_common: dict = {"spec": _read_json(_path(root, "spec")),
                         "board": _read_board(_path(root, "board")),
                         "root": root}
    cache: dict[str, list[dict]] = {}
    tcache: dict[str, str] = {}

    def rows_of(kind: str) -> list[dict]:
        if kind not in cache:
            cache[kind] = _read_rows(_path(root, kind))
        return cache[kind]

    def text_of(kind: str) -> str:
        if kind not in tcache:
            with open(_path(root, kind), encoding="utf-8") as fh:
                tcache[kind] = fh.read()
        return tcache[kind]

    for key, f, ln, chk in EXPECT:
        ctx = dict(ctx_common)
        if f in ("netlist", "pins", "bom", "sompins"):
            ctx["rows"] = rows_of(f)
            ctx["row"] = _row_at(ctx["rows"], ln)
        if f in TEXT_KINDS:
            ctx["text"] = text_of(f)
        ok, actual = _eval_check(ctx, chk)
        if not ok:
            errors.append(
                f"★[{key}] {REL[f]}:{ln} 判据 {chk!r} 不成立 (实际 {actual}) "
                f"⇒ 现状与规格页不符 (网表被静默改过? 或规格页没跟)")
        if verbose:
            report.append(f"   {'OK  ' if ok else 'FAIL'} {key:<18} {REL[f]}:{ln:<5} {chk}")

    # ---- ③ 报告项 (不判红, 只打印): ESD 到 J_USB_C 的几何距离 ----
    try:
        import math
        fps = ctx_common["board"]
        if "J_USB_C" in fps and "D_ESD_USB_D" in fps:
            # 板文件里 (at x y) 是封装原点; 这里用 ref→原点坐标
            coords = _board_ref_xy(_path(root, "board"))
            if "J_USB_C" in coords and "D_ESD_USB_D" in coords:
                a = coords["J_USB_C"]
                b = coords["D_ESD_USB_D"]
                d = math.hypot(a[0] - b[0], a[1] - b[1])
                report.append(f"   [报告项] D_ESD_USB_D → J_USB_C 板面距离 = {d:.2f} mm "
                              f"(★规格页 §①(4) 引的就是这个数★)")
    except Exception as exc:  # 报告项失败不许影响 rc
        report.append(f"   [报告项] 距离计算跳过: {exc}")

    if verbose:
        report.append("── 判据 b: BOM 里 U_EN_SW 的 type 仍是 NET (现状断言) ──")
        report.append("   (见上方 d3_bom208_type / d3_bom208_value)")

    # ---- ④ ★ISS-217: 落表作业包完整性 + 三方对齐 (★作业包漏一条就红★) ----
    wp_rc, wp_out = check_workpacket(root, verbose)
    errors.extend(x for x in wp_out if x.startswith("★"))
    report.extend(x for x in wp_out if not x.startswith("★"))

    # ---- ⑤ ★★ISS-230 (F-3 遗留): A 组 20 条已迁移连接的【字段分工】加强型断言 ★★
    #   ★★刻意【不进 `check_resolved()`】⇒ `--expect-resolved` 的「未落表条数」仍是 21 ★★
    fd_rc, fd_out = check_a_group_field_discipline(root)
    errors.extend(x for x in fd_out if x.startswith("★"))
    report.extend(x for x in fd_out if not x.startswith("★"))

    return (1 if errors else 0), errors + report


def _board_ref_xy(path: str) -> dict:
    """ref → 封装原点 (x, y)。只读。"""
    with open(path, encoding="utf-8") as fh:
        s = fh.read()
    out: dict[str, tuple[float, float]] = {}
    for m in re.finditer(r"\(footprint ", s):
        i = m.start()
        depth = 0
        j = i
        while j < len(s):
            if s[j] == "(":
                depth += 1
            elif s[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        blk = s[i:j + 1]
        rm = re.search(r'\(property "Reference" "([^"]*)"', blk)
        am = re.search(r"\(at (-?[\d.]+) (-?[\d.]+)", blk)
        if rm and am and rm.group(1) not in out:
            out[rm.group(1)] = (float(am.group(1)), float(am.group(2)))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# 翻面口径 (--expect-resolved): 4 条缺陷必须已经消失
# ─────────────────────────────────────────────────────────────────────────────

def _parse_res(s: str) -> float | None:
    """'1M' / '100k' / '220Ω' → 欧姆。★M=兆 / m=毫 / k=千 (大小写区分)★"""
    s = (s or "").strip()
    m = re.search(r"([\d.]+)\s*([kKMmRrΩ]|ohm)?", s)
    if not m:
        return None
    try:
        v = float(m.group(1))
    except ValueError:
        return None
    unit = m.group(2) or ""
    if unit in ("k", "K", "kohm", "kω"):
        v *= 1e3
    elif unit == "M":
        v *= 1e6
    elif unit == "m":
        v *= 1e-3
    return v


def check_resolved(root: str, verbose: bool) -> tuple[int, list[str]]:
    """翻面口径: 4 条缺陷都已随整链重出落表。"""
    errors: list[str] = []
    report: list[str] = []
    net = _read_rows(_path(root, "netlist"))
    pins = _read_rows(_path(root, "pins"))
    bom = _read_rows(_path(root, "bom"))
    spec = _read_json(_path(root, "spec"))
    board = _read_board(_path(root, "board"))
    netrows = net   # ★R4 里曾用 `net` 当循环变量 (已改名 pnet) ⇒ 这里留一份不受影响的引用★

    # ---- R1: I2C_A 上拉 —— NET 行必须与器件行一致 (2.2k / 1.8V) ----
    stale = [r for r in net if "4.7k 到 3.3V" in (r.get("value") or "")
             or "2.38µs" in (r.get("value") or "")]
    if stale:
        errors.append(
            f"★R1 未落表: 仍有 {len(stale)} 行写着『4.7k 到 3.3V / 2.38µs』 "
            f"(行 {[r['_line'] for r in stale]}) ⇒ L167/L168 的过期注记还在")
    for cid in ("B-01", "B-02"):
        hit = [c for c in spec.get("connections", []) if c.get("id") == cid]
        if not hit:
            errors.append(f"★R1 未落表: SPEC.json 里没有 connections id={cid}")
            continue
        c = hit[0]
        if _norm(c.get("level")) == "3.3V":
            errors.append(f"★R1 未落表: SPEC.json {cid}.level 仍是 3.3V")
        if "4.7k" in (c.get("imp") or ""):
            errors.append(f"★R1 未落表: SPEC.json {cid}.imp 仍含 4.7k")
        if "2.2k" not in (c.get("imp") or ""):
            errors.append(f"★R1 未落表: SPEC.json {cid}.imp 里没有 2.2k")
        if "1.8V" not in (c.get("imp") or "") and "1.8" not in (c.get("imp") or ""):
            errors.append(f"★R1 未落表: SPEC.json {cid}.imp 里没有 1.8V 口径")
    for r in net:
        if _norm(r.get("ref")) in ("NET_I2C_A_SCL", "NET_I2C_A_SDA"):
            v = r.get("value") or ""
            if "2.2k" not in v:
                errors.append(f"★R1 未落表: 表A 行 {r['_line']} 的 NET 行 value 还没改成 2.2k 口径")
    if verbose:
        report.append("   R1 (I2C_A 上拉注记) 检查完毕")

    # ---- R2: BAT_DET 分压链必须实装, 且分压后电压要进得了 1.8V 域 ADC ----
    for ref in ("R_BAT_DET_1", "R_BAT_DET_2", "C_DET_BAT"):
        rows = [r for r in net if _norm(r.get("ref")) == ref]
        if not rows:
            errors.append(f"★R2 未落表: 表A 里没有 {ref}")
            continue
        for r in rows:
            if _norm(r.get("dnp")) == "DNP":
                errors.append(f"★R2 未落表: {ref} 仍是 DNP (表A 行 {r['_line']})")
        rows_b = [r for r in pins if _norm(r.get("ref")) == ref]
        for r in rows_b:
            if _norm(r.get("dnp")) == "DNP":
                errors.append(f"★R2 未落表: {ref} 在脚表里仍是 DNP (行 {r['_line']})")
    top = _parse_res(next((r.get("value") or "" for r in net
                           if _norm(r.get("ref")) == "R_BAT_DET_1"), ""))
    bot = _parse_res(next((r.get("value") or "" for r in net
                           if _norm(r.get("ref")) == "R_BAT_DET_2"), ""))
    if top and bot and top > 0 and bot > 0:
        vbat_max = 4.2   # 1S 锂电满充 (HW/INTERFACE_TABLE.md C-03)
        vnode = vbat_max * bot / (top + bot)
        if vnode > 1.8:
            errors.append(
                f"★R2 未落表: 分压后 {vbat_max}V × {bot:g}/({top:g}+{bot:g}) = {vnode:.3f}V "
                f"> 1.8V 域 ADC 上限 (J_SOM_P1 pin38 = SARADC_VIN5, 1.8V 域) ⇒ 贴上去就是过压")
        if verbose:
            report.append(f"   R2 分压后 ADC 节点电压 @4.2V = {vnode:.3f} V (上限 1.8V)")
    else:
        errors.append("★R2 未落表: 解析不出 R_BAT_DET_1/2 的阻值 ⇒ 无法判定分压后电压, 人工判")
    if verbose:
        report.append("   R2 (BAT_DET 分压链) 检查完毕")

    # ---- R3: U_EN_SW 必须有器件本体行 (type=IC) ----
    body_a = [r for r in net if _norm(r.get("ref")) == "U_EN_SW" and _norm(r.get("type")) != "NET"]
    if not body_a:
        errors.append("★R3 未落表: 表A 里 U_EN_SW 仍然 0 条 type!=NET 的器件本体行")
    body_b = [r for r in pins if _norm(r.get("ref")) == "U_EN_SW" and _norm(r.get("type")) != "NET"]
    if not body_b:
        errors.append("★R3 未落表: 脚表里 U_EN_SW 仍然 0 条 type!=NET 的器件本体行")
    bom_u = [r for r in bom if _norm(r.get("ref")) == "U_EN_SW"]
    if not bom_u:
        errors.append("★R3 未落表: BOM 里没有 U_EN_SW")
    for r in bom_u:
        if _norm(r.get("type")) == "NET":
            errors.append(f"★R3 未落表: BOM 里 U_EN_SW 的 type 仍是 NET (行 {r['_line']})")
    if "U_EN_SW" in board:
        bv = _norm(board["U_EN_SW"].get("value"))
        if bv in ("EN 输入 (高=放行底板)", "5V 输入", "5V 输出 (受 CARRIER_BOARD_EN 门控)", "GND"):
            errors.append(
                f"★R3 未落表: 板封装 U_EN_SW 的 Value 属性还是脚级功能串 {bv!r} ⇒ 板文件也要同趟改")
    if verbose:
        report.append("   R3 (U_EN_SW 器件本体行) 检查完毕")

    # ---- R4: USB D− 必须有 ESD ----
    dminus = {"USB_D_N_SRC", "NET_USB_D_N_TYPEC"}
    hit = []
    for ref, info in board.items():
        if "ESD" not in ref.upper():
            continue
        for _num, pnet in info.get("pads_list", []):
            if pnet in dminus:
                hit.append((ref, pnet))
                break
    if not hit:
        errors.append(
            "★R4 未落表: 板上仍然没有任何 ESD 位号挂在 D− 那条网上 "
            "(USB_D_N_SRC / NET_USB_D_N_TYPEC) ⇒ D− 仍然裸奔")
    if "D_ESD_USB_D" in board:
        info = board["D_ESD_USB_D"]
        if info["pads"] < 3 and not hit:
            errors.append("★R4 未落表: D_ESD_USB_D 仍然只有 2 个焊盘 (D+ + GND) ⇒ 仍不是双通道")
    if verbose:
        report.append(f"   R4 (USB D− ESD) 检查完毕, 命中位号 = {hit}")

    # ═══════════════════════════════════════════════════════════════════════
    # ★★第 2 轮 (ISS-214) 的 R5..R11 —— ★落表后按这几条翻面★★
    # ═══════════════════════════════════════════════════════════════════════

    # ---- R5: USB 串阻必须是 22Ω (不再是 90Ω) ----
    for r in netrows:
        if _norm(r.get("ref")) in ("NET_USB_D_P_SRC", "NET_USB_D_N_SRC"):
            v = r.get("value") or ""
            if "90Ω" in v:
                errors.append(
                    f"★R5 未落表: 表A 行 {r['_line']} 的 NET 行 value 还是 {v!r} "
                    f"⇒ USB 串阻还挂着【差分阻抗】当【串阻】用")
            if "22Ω" not in v:
                errors.append(f"★R5 未落表: 表A 行 {r['_line']} 的 NET 行 value 里没有 22Ω")
    for cid in ("B-21", "B-22"):
        hc = [c for c in spec.get("connections", []) if c.get("id") == cid]
        if not hc:
            errors.append(f"★R5 未落表: SPEC.json 里没有 connections id={cid}")
            continue
        imp = hc[0].get("imp") or ""
        if "90Ω" in imp:
            errors.append(f"★R5 未落表: SPEC.json {cid}.imp 仍含 90Ω (=差分阻抗, 不是串阻)")
        if "22Ω" not in imp:
            errors.append(f"★R5 未落表: SPEC.json {cid}.imp 里没有 22Ω")
    if verbose:
        report.append("   R5 (USB 串阻 22Ω) 检查完毕")

    # ---- R6: P9 页的 CONN_LIGHT 必须写 22p, 且堆叠算式不能再用 21 ----
    with open(_path(root, "pages"), encoding="utf-8") as fh:
        pages_txt = fh.read()
    if "1×21p@0.5mm" in pages_txt:
        errors.append("★R6 未落表: P9 页正文里还有『CONN_LIGHT 1×21p@0.5mm』")
    if "1×22p@0.5mm" not in pages_txt:
        errors.append("★R6 未落表: P9 页正文里没有『CONN_LIGHT 1×22p@0.5mm』")
    if "(10+4+18+21)×0.5" in pages_txt:
        errors.append("★R6 未落表: P9 页的堆叠算式还在用 CONN_LIGHT=21p")
    n_light = sum(1 for r in pins if _norm(r.get("ref")) == "CONN_LIGHT")
    if n_light != 22:
        errors.append(f"★R6 未落表: 脚表里 CONN_LIGHT 的脚行数 = {n_light} (应为 22)")
    if verbose:
        report.append(f"   R6 (P9 页 CONN_LIGHT 22p) 检查完毕, 脚表脚行数 = {n_light}")

    # ---- R7: 分压比必须既进得了 1.8V, 又不能浪费 12bit ----
    top = _parse_res(next((r.get("value") or "" for r in net
                           if _norm(r.get("ref")) == "R_BAT_DET_1"), ""))
    bot = _parse_res(next((r.get("value") or "" for r in net
                           if _norm(r.get("ref")) == "R_BAT_DET_2"), ""))
    if top and bot and top > 0 and bot > 0:
        vnode = 4.2 * bot / (top + bot)
        if vnode > 1.8:
            errors.append(f"★R7 未落表: 分压后 {vnode:.3f}V > 1.8V (SARADC_VIN5 是 1.8V 域)")
        if vnode < 1.2:
            errors.append(
                f"★R7 未落表: 分压后只有 {vnode:.3f}V ⇒ 12bit 量程利用率过低 "
                f"(低于 1.2V = 66.7% 满量程) ⇒ 分压比定得太保守")
    if verbose:
        report.append("   R7 (分压比) 检查完毕")

    # ---- R8: 漏电预算的 note 必须与阻值自洽 ----
    leak_note = next((r.get("note") or "" for r in net
                      if _norm(r.get("ref")) == "R_BAT_DET_1"), "")
    if "~1.65µA @5V" in leak_note:
        errors.append("★R8 未落表: R_BAT_DET_1 的 note 仍写『漏电流 ~1.65µA @5V』(与 1M+1M 对不上)")
    if verbose:
        report.append("   R8 (漏电预算 note) 检查完毕")

    # ---- R9: ESD 必须真的贴到 J_USB_C (★≤3.0mm, 按 ISS-085 规矩; 原 5.0mm 作废★) ----
    import math as _math
    xy = _board_ref_xy(_path(root, "board"))
    if "J_USB_C" in xy and "D_ESD_USB_D" in xy:
        a, b = xy["J_USB_C"], xy["D_ESD_USB_D"]
        d = _math.hypot(a[0] - b[0], a[1] - b[1])
        if d > ESD_MAX_DIST_MM:
            errors.append(
                f"★R9 未落表: D_ESD_USB_D → J_USB_C 板面距离 = {d:.2f} mm > {ESD_MAX_DIST_MM} mm "
                f"⇒ ESD 还是不在接口旁边")
        if verbose:
            report.append(f"   R9 (ESD 位置) 检查完毕, 距离 = {d:.2f} mm "
                          f"(阈值 {ESD_MAX_DIST_MM} mm)")
    else:
        errors.append("★R9 未落表: 板文件里找不到 D_ESD_USB_D 或 J_USB_C 的坐标")

    # ---- R10: ICHG/IIN 系数方向必须倒过来, 且单 pin 载流必须 ≤ 触点额定 ----
    with open(_path(root, "chgspec"), encoding="utf-8") as fh:
        cs_txt = fh.read()
    if "0.822" in cs_txt:
        errors.append("★R10 未落表: CHARGE_BOARD_SPEC 里还有 0.822 (那是倒数, 方向反了)")
    if "1.216" not in cs_txt or "1.071" not in cs_txt:
        errors.append("★R10 未落表: CHARGE_BOARD_SPEC 里没有 1.216 / 1.071 这两个真值")
    for r in netrows:
        if _norm(r.get("ref")) == "R_ILIM":
            v = r.get("value") or ""
            if "0.411A" in v:
                errors.append(f"★R10 未落表: 表A 行 {r['_line']} 的 R_ILIM value 还写着单 pin 0.411A (错值)")
    pin_max = _calc_expr({"rows": netrows, "root": root}, "ichg_pin_max@3.7")
    if pin_max is not None and pin_max > 0.5:
        errors.append(
            f"★R10 未落表: 390Ω 档单 pin 载流上限 = {pin_max:.3f} A > 0.5 A 触点额定 "
            f"⇒ R_ILIM 档位没重新定")
    if verbose:
        report.append(f"   R10 (ICHG/IIN 方向) 检查完毕, 单 pin 上限 = {pin_max}")

    # ---- R11: 充电板本地网的 board 列必须一致 ----
    for netname in ("VBUS_5V_CHG", "VBUS_5V_F1"):
        bad_rows = [(r["_line"], r.get("board")) for r in net
                    if _norm(r.get("net")) == netname and _norm(r.get("board")) != "CHG_BOARD"]
        if bad_rows:
            errors.append(
                f"★R11 未落表: 网 {netname} 上还有 {len(bad_rows)} 行的 board 列不是 CHG_BOARD "
                f"(行/board = {bad_rows})")
    for r in netrows:
        if _norm(r.get("ref")) == "C_VBUS_GND" and _norm(r.get("board")) != "CHG_BOARD":
            errors.append(
                f"★R11 未落表: C_VBUS_GND 的 board 列仍是 {r.get('board')!r} "
                f"(表A 行 {r['_line']}) ⇒ π 滤波对地电容被分到另一块板上")
    if verbose:
        report.append("   R11 (board 列一致性) 检查完毕")

    # ---- ★ISS-217: 作业包完整性 + 三方对齐 (★落表那趟的 SOP 本身也要被门禁守住★) ----
    wp_rc, wp_out = check_workpacket(root, verbose)
    errors.extend(x for x in wp_out if x.startswith("★"))
    report.extend(x for x in wp_out if not x.startswith("★"))

    return (1 if errors else 0), errors + report


# ─────────────────────────────────────────────────────────────────────────────
# 自检 (--selftest): 反向用例 —— 改坏任一锚点 ⇒ 必须变红
# ─────────────────────────────────────────────────────────────────────────────

FIXTURES = ["netlist", "pins", "bom", "spec", "board", "specpage",
            # ★★第 2 轮 (ISS-214) 新增的 5 条要读的文件 (自检要在临时副本里改坏它们)★★
            "pages", "chgspec", "emc", "rk", "sompins",
            # ★★第 3 轮 (ISS-217) 新增: 落表作业包本体 (★自检要在临时副本里删掉一组★)★★
            "workpacket"]


def _copy_fixture(root: str, dst: str) -> str:
    for key in FIXTURES:
        src = os.path.join(root, REL[key])
        if not os.path.exists(src):
            continue
        d = os.path.join(dst, REL[key])
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(src, d)
    return dst


def _run_case(name: str, root: str, mutate, expect_rc: int = 1) -> tuple[str, bool, str]:
    tmp = tempfile.mkdtemp(prefix="iss211_selftest_")
    try:
        _copy_fixture(root, tmp)
        mutate(tmp)
        rc, _ = check_guard(tmp, False)
        if rc != expect_rc:
            return name, False, f"rc={rc} (期望 {expect_rc})"
        return name, True, f"rc={rc} (期望 {expect_rc}) ✔"
    except Exception as exc:
        return name, False, f"异常: {exc}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _mutate_line(path: str, lineno: int, field: str, newval: str) -> None:
    with open(path, encoding="utf-8", newline="") as fh:
        raw = fh.read()
    rows = list(csv.reader(raw.split("\n")))
    while rows and rows[-1] == []:
        rows.pop()
    head = rows[0]
    idx = lineno - 1
    r = rows[idx]
    fi = head.index(field)
    r[fi] = newval
    out = "\n".join(",".join(_csv_escape(x) for x in row) for row in rows) + "\n"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(out)


def _csv_escape(v: str) -> str:
    if any(ch in v for ch in ',"\n'):
        return '"' + v.replace('"', '""') + '"'
    return v


def selftest(root: str) -> int:
    print("╔══ ISS-211/ISS-214 门禁自检 (反向用例: 改坏锚点 ⇒ 必须变红) ══╗")
    print("★ 原 9 个用例 (ISS-211 · d1..d4) **一条不许删**; ★ 第 2 轮 (ISS-214) 追加 7 个 (d5..d11) ★")
    print("★ 第 3 轮 (ISS-217) 追加 3 个 (作业包 ×2 + R9 阈值 ×1) ★ ★ 第 4 轮 (ISS-230 · F-3) 追加 2 个 (A 组字段分工) ★")
    cases: list[tuple[str, bool, str]] = []

    # 用例 0: 基线必须是绿的 —— 否则后面的"抓到"没有意义
    tmp = tempfile.mkdtemp(prefix="iss211_selftest_")
    try:
        _copy_fixture(root, tmp)
        rc, errs = check_guard(tmp, False)
        cases.append((f"用例0 基线干净 (现状=规格页)", rc == 0, f"rc={rc} (期望 0)" + ("" if rc == 0 else f" 错误: {errs[:3]}")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    def m_net_value(tmp):
        # ★★2026-11-16 ISS-220 落表后: L167 的现状已是 2.2k/1.8V ⇒ 反向用例改成【退回 4.7k/3.3V 的旧缺陷】★
        _mutate_line(os.path.join(tmp, REL["netlist"]), 167, "value", "上拉 4.7k 到 3.3V")

    def m_net_dnp(tmp):
        _mutate_line(os.path.join(tmp, REL["netlist"]), 182, "dnp", "必装")

    def m_net_note(tmp):
        _mutate_line(os.path.join(tmp, REL["netlist"]), 169, "note", "[VDD_1V8_IO] I2C_A 上拉 (已订正)")

    def m_bom_type(tmp):
        # ★★2026-11-16 ISS-233 落表后: BOM L208 的 U_EN_SW type 已是 IC ⇒ 反向用例改成【退回 NET 的旧缺陷】
        _mutate_line(os.path.join(tmp, REL["bom"]), 208, "type", "NET")

    def m_spec_level(tmp):
        p = os.path.join(tmp, REL["spec"])
        with open(p, encoding="utf-8") as fh:
            obj = json.load(fh)
        # ★★2026-11-16 ISS-220 落表后: B-01.level 已是 1.8V ⇒ 反向用例改成【退回 3.3V 的旧缺陷】★
        for c in obj.get("connections", []):
            if c.get("id") == "B-01":
                c["level"] = "3.3V"
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=2)

    def m_board_value(tmp):
        p = os.path.join(tmp, REL["board"])
        with open(p, encoding="utf-8") as fh:
            s = fh.read()
        # ★板文件里 property 的 s-表达式在值后面不跟 ')' ⇒ 替换串不能带尾巴★
        s = s.replace('(property "Value" "EN 输入 (高=放行底板)"',
                      '(property "Value" "TPS22991RAA"', 1)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(s)

    def m_specpage_anchor(tmp):
        p = os.path.join(tmp, REL["specpage"])
        with open(p, encoding="utf-8") as fh:
            s = fh.read()
        s = s.replace("| d2_a182_dnp | netlist | 182 | dnp == DNP |",
                      "| d2_a182_dnp | netlist | 182 | dnp == 必装 |", 1)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(s)

    def m_net_delete_esd_note(tmp):
        _mutate_line(os.path.join(tmp, REL["netlist"]), 417, "note", "[D_ESD_USB_D] ESD")

    # ── ★★第 2 轮 (ISS-214) 的 7 个反向用例 (d5..d11) ★★ ──
    def m_spec_b21_imp(tmp):
        p = os.path.join(tmp, REL["spec"])
        with open(p, encoding="utf-8") as fh:
            obj = json.load(fh)
        # ★★2026-11-16 ISS-223 落表后: B-21.imp 已是 22Ω ±1% ⇒ 反向用例改成【退回 90Ω 的旧缺陷】★
        #   ★与 ISS-220 落表时 d1 (m_net_value) / d6 (m_pages_21p_to_22p) 同型处理★
        for c in obj.get("connections", []):
            if c.get("id") == "B-21":
                c["imp"] = "90Ω ±10% (与 MIPI 不同模板!)"
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=2)

    def m_pages_21p_to_22p(tmp):
        p = os.path.join(tmp, REL["pages"])
        with open(p, encoding="utf-8") as fh:
            s = fh.read()
        # ★★2026-11-16 ISS-220 落表后: P9 页已是 22p ⇒ 反向用例改成【退回 21p 的旧缺陷】★
        #   ★只换 pin 数那 4 个字符 (★新页的 pin 数后面还跟着封装与身份说明, 整段带标记的串已不存在★)
        s = s.replace("1×22p@0.5mm", "1×21p@0.5mm", 1)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(s)

    def m_net_rbatdet2_2m(tmp):
        # ★把下臂改成 2M ⇒ calc(node_v@4.2) 从 2.1 变成 2.8 ⇒ d7_node_v / d7_node_over 双双变红
        _mutate_line(os.path.join(tmp, REL["netlist"]), 183, "value", "2M ±1%")

    def m_net_leak_note(tmp):
        # ★把 note 里自称的漏电流从 1.65µA 改成 2.5µA (★与 1M+1M 真值一致了⇒ 缺陷消失⇒ 必须变红★)
        p = os.path.join(tmp, REL["netlist"])
        with open(p, encoding="utf-8") as fh:
            raw = fh.read()
        raw = raw.replace("漏电流 ~1.65µA @5V", "漏电流 ~2.5µA @5V", 1)
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(raw)

    def m_board_move_esd(tmp):
        # ★★calc-only 用例: 把板上的 D_ESD_USB_D 挪到 J_USB_C (140, 5.25) 旁边 ⇒
        #   calc(esd_dist_usb) > 5 不再成立 ⇒ d9_esd_dist 变红, 而 d9 的逐字锚点全都还在
        p = os.path.join(tmp, REL["board"])
        with open(p, encoding="utf-8") as fh:
            s = fh.read()
        s = s.replace("(at 94.95 21.8", "(at 138 5.25", 1)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(s)

    def m_chgspec_0822(tmp):
        p = os.path.join(tmp, REL["chgspec"])
        with open(p, encoding="utf-8") as fh:
            s = fh.read()
        # ★★2026-11-16 ISS-220 落表后: 规格页已是 1.216 ⇒ 反向用例改成【退回旧系数 0.822 的旧缺陷】★
        s = s.replace("ICHG ≈ 1.216 × IIN", "ICHG ≈ 0.822 × IIN", 1)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(s)

    def m_net_cvbgnd_board(tmp):
        # ★★2026-11-16 ISS-220 落表后: L12 的 board 已是 CHG_BOARD ⇒ 反向用例改成【退回 MAIN_PCB 的旧缺陷】★
        _mutate_line(os.path.join(tmp, REL["netlist"]), 12, "board", "MAIN_PCB")

    # ── ★★第 3 轮 (ISS-217) 的 2 个新反向用例 (★作业包门禁 + R9 阈值★) ──
    def m_wp_delete_d11(tmp):
        # ★★删掉作业包里的 d11 一组 ⇒ 作业包完整性检查必须变红 (★"作业包漏一条就红"★)
        p = os.path.join(tmp, REL["workpacket"])
        with open(p, encoding="utf-8") as fh:
            s = fh.read()
        s2 = re.sub(r"<!-- WPITEM:BEGIN id=d11 -->\n.*?\n<!-- WPITEM:END -->\n", "", s, flags=re.S)
        if s2 == s:
            raise RuntimeError("★没找到 d11 那一组 (作业包格式变了?)")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(s2)

    def m_wp_break_r_alignment(tmp):
        # ★★把作业包 d5 的 ⑦ 栏 (翻面判据) 从 R5 改成 R1 ⇒ 三方对齐必须变红
        p = os.path.join(tmp, REL["workpacket"])
        with open(p, encoding="utf-8") as fh:
            s = fh.read()
        s2 = s.replace("⑦ 翻面判据: ★**R5** ★ (★`--expect-resolved` 的 R5 段:",
                       "⑦ 翻面判据: ★**R1** ★ (★`--expect-resolved` 的 R5 段:", 1)
        if s2 == s:
            raise RuntimeError("★没找到 d5 的 ⑦ 栏 (作业包格式变了?)")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(s2)

    # ── ★★第 4 轮 (ISS-230 · F-3 遗留): A 组字段分工加强型断言 的 2 个反向用例 ★─
    def m_spec_a01_zdiff_empty(tmp):
        # ★★F-3 加强型断言的反向用例 (ISS-230): 把 A-01 的 `z_diff` 清空 ⇒ 必须红 ★★
        #   ★为什么【这条必须红】而【判据 5 不会红】: `state/check_netlist.py` 判据 5 的
        #     比对源是【`imp` or `z_diff`】⇒ z_diff 空了它就【跳过】这行 (want 变空)
        #     ⇒ 判据覆盖行数从 22 静默掉到 21 ⇒ ★**只有【字段分工】断言能抓住它**★
        #     ⇒ 这就是 F-3 说的「判据被静默放松」★
        p = os.path.join(tmp, REL["spec"])
        with open(p, encoding="utf-8") as fh:
            obj = json.load(fh)
        for c in obj.get("connections", []):
            if c.get("id") == "A-01":
                c["z_diff"] = ""
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=2)

    def m_spec_a13_imp_refilled(tmp):
        # ★★F-3 加强型断言的第 2 个反向用例 (ISS-230): 把差分阻抗【塞回 `imp` 字段】(★
        #   `z_diff` 同时清空) ⇒ 判据 5 因为先读到 `imp` 仍然全绿 ⇒ 只有字段分工断言能红 ★
        p = os.path.join(tmp, REL["spec"])
        with open(p, encoding="utf-8") as fh:
            obj = json.load(fh)
        for c in obj.get("connections", []):
            if c.get("id") == "A-13":
                c["imp"] = "100Ω ±10%"
                c["z_diff"] = ""
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=2)

    def _esd_threshold_case(root):
        """★反向用例: 证明 R9 的翻面阈值真被读到 3.0 而不是 5.0。★
        做法: 把板上的 D_ESD_USB_D 挪到距 J_USB_C **4.0 mm** 处 (★4.0 落在 3.0 与 5.0 之间,
        正好能区分两个阈值★) ⇒
             ① 真实脚本 (阈值 3.0) 必须报 R9 未落表;
             ② 把脚本副本里的阈值改回 5.0 ⇒ 同一块板【不】报 R9。
        ⇒ 两条断言同时成立 = "阈值真被读到 3.0 而不是 5.0" 被证明;
        ⇒ 谁把常量改回 5.0, 断言① 立刻失败 ⇒ 自检变红。"""
        import importlib.util
        tmp = tempfile.mkdtemp(prefix="iss217_esd_threshold_")
        try:
            _copy_fixture(root, tmp)
            # ---- 把 ESD 挪到 4.0mm 处 (J_USB_C 在 (140.0, 5.25)) ----
            bp = os.path.join(tmp, REL["board"])
            with open(bp, encoding="utf-8") as fh:
                bs = fh.read()
            bs2 = bs.replace("(at 94.95 21.8", "(at 144 5.25", 1)
            if bs2 == bs:
                return "用例18 [R9阈值] 把板上 D_ESD_USB_D 挪到 4.0mm 处", False, "★板文件里找不到 D_ESD_USB_D 的坐标"
            with open(bp, "w", encoding="utf-8") as fh:
                fh.write(bs2)
            # ---- ① 真实脚本 (阈值 3.0) 必须报 R9 ----
            _rc, errs = check_resolved(tmp, False)
            r9_real = [e for e in errs if e.startswith("★R9")]
            if not r9_real:
                return ("用例18 [R9阈值] 把板上 D_ESD_USB_D 挪到 4.0mm 处 (真实阈值 3.0 必须报 R9)",
                        False, "★4.0mm 处没报 R9 ⇒ 阈值不是 3.0 (或没被读到)")
            # ---- ② 脚本副本把阈值改回 5.0 ⇒ 同一块板不报 R9 ----
            with open(os.path.abspath(__file__), encoding="utf-8") as fh:
                src = fh.read()
            src2 = src.replace("ESD_MAX_DIST_MM = 3.0", "ESD_MAX_DIST_MM = 5.0", 1)
            if src2 == src:
                return ("用例18 [R9阈值] 把板上 D_ESD_USB_D 挪到 4.0mm 处 (真实阈值 3.0 必须报 R9)",
                        False, "★脚本里没找到 ESD_MAX_DIST_MM = 3.0 (常量被改名了?)")
            alt_path = os.path.join(tmp, "alt_gate.py")
            with open(alt_path, "w", encoding="utf-8") as fh:
                fh.write(src2)
            spec = importlib.util.spec_from_file_location("iss217_alt_gate", alt_path)
            alt = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(alt)
            _rc2, errs2 = alt.check_resolved(tmp, False)
            r9_alt = [e for e in errs2 if e.startswith("★R9")]
            if r9_alt:
                return ("用例18 [R9阈值] 把板上 D_ESD_USB_D 挪到 4.0mm 处 (真实阈值 3.0 必须报 R9)",
                        False, f"★阈值改成 5.0 后仍然报 R9 ⇒ 常量没被真正读到 ({r9_alt[:1]})")
            return ("用例18 [R9阈值] 把板上 D_ESD_USB_D 挪到 4.0mm 处 (真实阈值 3.0 必须报 R9)",
                    True, "★4.0mm: 阈值 3.0 报红 / 阈值 5.0 不报 ⇒ 阈值真被读到 3.0 ✔")
        except Exception as exc:
            return "用例18 [R9阈值] 阈值反向用例", False, f"异常: {exc}"
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    cases.append(_run_case("用例1 [d1] 改坏 L167 的 value (2.2k/1.8V→4.7k/3.3V) ⇒ 必须红", root, m_net_value))
    cases.append(_run_case("用例2 改坏 L182 的 dnp (DNP→必装) ⇒ 必须红", root, m_net_dnp))
    cases.append(_run_case("用例3 改坏 L169 note (删掉『已作废』) ⇒ 必须红", root, m_net_note))
    cases.append(_run_case("用例4 [d3] 改坏 BOM L208 的 type (IC→NET, 退回旧缺陷) ⇒ 必须红", root, m_bom_type))
    cases.append(_run_case("用例5 [d1] 改坏 SPEC.json B-01.level (1.8V→3.3V) ⇒ 必须红", root, m_spec_level))
    cases.append(_run_case("用例6 改坏板封装 U_EN_SW 的 Value ⇒ 必须红", root, m_board_value))
    cases.append(_run_case("用例7 改坏规格页锚点表 (规格页⇄脚本漂移) ⇒ 必须红", root, m_specpage_anchor))
    cases.append(_run_case("用例8 改坏 L417 的 note (删掉 Forlinx 规矩引用) ⇒ 必须红", root, m_net_delete_esd_note))

    # ★★第 2 轮 (ISS-214) 追加的 7 个反向用例 (★d5..d11 每组 ≥1 个★) ★★
    cases.append(_run_case("用例9 [d5] 改坏 SPEC.json B-21.imp (22Ω→90Ω 退回旧缺陷) ⇒ 必须红", root, m_spec_b21_imp))
    cases.append(_run_case("用例10 [d6] 改坏 P9 页 (22p→21p) ⇒ 必须红", root, m_pages_21p_to_22p))
    cases.append(_run_case("用例11 [d7] 改坏 L183 下臂 (1M→2M, 触发 calc) ⇒ 必须红", root, m_net_rbatdet2_2m))
    cases.append(_run_case("用例12 [d8] 改坏 L182 note 的自称漏电流 (1.65→2.5µA) ⇒ 必须红", root, m_net_leak_note))
    cases.append(_run_case("用例13 [d9] 把板上 D_ESD_USB_D 挪到 J_USB_C 旁 (calc-only) ⇒ 必须红", root, m_board_move_esd))
    cases.append(_run_case("用例14 [d10] 改坏 CHARGE_BOARD_SPEC 的 1.216 ⇒ 必须红", root, m_chgspec_0822))
    cases.append(_run_case("用例15 [d11] 改坏 L12 的 board 列 (CHG_BOARD→MAIN_PCB) ⇒ 必须红", root, m_net_cvbgnd_board))

    # ★★第 3 轮 (ISS-217) 追加的 3 个反向用例 (★作业包门禁 + R9 阈值★) ★★
    cases.append(_run_case("用例16 [ISS-217] 删掉作业包里的 d11 一组 ⇒ 必须红", root, m_wp_delete_d11))
    cases.append(_run_case("用例17 [ISS-217] 改坏作业包 d5 的 ⑦ 栏 (R5→R1, 三方对齐) ⇒ 必须红", root, m_wp_break_r_alignment))
    cases.append(_esd_threshold_case(root))

    # ★★第 4 轮 (ISS-230 · F-3 遗留): A 组 20 条已迁移连接的【字段分工】加强型断言 ★★
    cases.append(_run_case("用例19 [ISS-230/F-3] 清空 A-01 的 z_diff ⇒ 必须红 (字段分工断言)",
                            root, m_spec_a01_zdiff_empty))
    cases.append(_run_case("用例20 [ISS-230/F-3] 把差分阻抗塞回 A-13 的 imp 字段 ⇒ 必须红",
                            root, m_spec_a13_imp_refilled))

    ok = 0
    for name, good, detail in cases:
        print(f"  {'✅' if good else '❌'} {name:<52} {detail}")
        if good:
            ok += 1
    print(f"\n自检结果: {ok}/{len(cases)} 通过")
    if ok != len(cases):
        print("★★ 自检没过 ⇒ 门禁不可信, 不许交卷 ★★")
        return 1
    # 翻面口径: 现在应当是红的 (缺陷还在) ⇒ 期望 rc=1
    rc, errs = check_resolved(root, False)
    print(f"翻面口径 (--expect-resolved) 现状 rc={rc} (期望 1 = 缺陷尚未落表) "
          f"{'✔' if rc == 1 else '★★不符合预期★★'}")
    return 0 if rc == 1 else 1


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", default=DEFAULT_ROOT, help="工程根 (默认 = HW/ 的上一级)")
    ap.add_argument("--verbose", action="store_true", help="打印逐条锚点明细")
    ap.add_argument("--expect-resolved", action="store_true",
                    help="★翻面口径: 4 条缺陷必须已消失 (落表后才 rc=0) ★")
    ap.add_argument("--check-workpacket", action="store_true",
                    help="★只跑作业包完整性 + 三方对齐 (ISS-217) ★")
    ap.add_argument("--selftest", action="store_true", help="跑自检 (反向用例, 只动临时副本)")
    ap.add_argument("--emit-anchors", action="store_true",
                    help="打印规格页用的锚点表 (唯一真源 = 本脚本 EXPECT)")
    args = ap.parse_args(argv)

    if args.emit_anchors:
        print(emit_anchor_table())
        return 0

    root = os.path.abspath(args.root)

    if args.selftest:
        return selftest(root)

    if args.check_workpacket:
        rc, out = check_workpacket(root, args.verbose)
        for line in out:
            print(line)
        if rc == 0:
            print(f"✅ rc=0: ★落表作业包 {len(WP_MAP)} 条齐全, 8 栏齐, 三方对齐 (作业包 ↔ 规格页 ↔ 门禁 R#) 全过★")
        else:
            print(f"★★ rc=1: 落表作业包有 {len([x for x in out if x.startswith('★')])} 条问题 ★★")
        return rc

    try:
        if args.expect_resolved:
            rc, out = check_resolved(root, args.verbose)
            if rc == 0:
                print("✅ rc=0: ★第 1 轮 4 条 + 第 2 轮 7 组缺陷已全部消失★ (翻面口径通过)")
            else:
                print(f"★★ rc=1: 翻面口径未通过 ({len(out)} 条未落表) ★★")
                for line in out:
                    print(f"   {line}")
                print("★**说明**: 现在缺陷仍在 ⇒ 本口径应当是红的; ★"
                      "等它们随『整链重出 第 1 步』落表后本口径才转绿★")
            return rc
        rc, out = check_guard(root, args.verbose)
        errors = [x for x in out if x.startswith("★")]
        report = [x for x in out if not x.startswith("★")]
        for line in report:
            print(line)
        if rc == 0:
            print("✅ rc=0: ★现状与 HW/NETLIST_SELF_CONSISTENCY_SPEC.md 一致★")
            print("★**注意: 门禁是【现状守卫】不是【合格证】** ⇒ ★**第 1 轮 4 条 + 第 2 轮 7 组缺陷★仍在★ ⇒ "
                  "rc=0 是预期状态 ★")
            print("★**落表作业包 (HW/SCHEMATIC_LANDING_WORKPACKET_V1.md) 完整性 + 三方对齐: 全过** "
                  f"(★{len(WP_MAP)} 条作业条目, 8 栏齐★)")
            print("★**翻面条件见规格页 §⑤**; 落表后请改用 `--expect-resolved` ★")
        else:
            print(f"★★ rc=1: 现状与规格页不一致 ({len(errors)} 条) ★★")
            for line in errors:
                print(f"   {line}")
        return rc
    except CheckError as exc:
        print(f"★rc=2: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover
        print(f"★rc=2: 未预期异常: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
