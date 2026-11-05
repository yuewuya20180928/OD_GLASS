#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
netlist 生成器 (gen_netlist) —— **器件级 netlist 的唯一真源**
================================================================================
★为什么器件级内容必须进脚本 (ISS-075 · 2026-10-27):
  上一轮我把 277 行器件级 netlist **手改在 CSV 里**, 而生成器还停在 108 行版 ·
  任何人重跑 `gen_netlist.py` 就会把那 168 行覆盖没了 (生成物漂移 = 静默数据丢失)。
  ⇒ 本版把**全部器件级内容用代码实现**进本脚本: CSV 变成纯生成物, 重跑幂等。

★内容边界:
  ① 只从 `HW/SCHEMATIC_V1_SPEC.json` (56 连接 / 13 电源轨 / 9 选择位 / 13 测试点) 展开
     · **不发明连接**; 器件级 (无源件/保护件/连接器/消抖) 是把规格原文落到器件行, 不改连接关系
  ② SoC 侧球位号一律 `SoC[RK3572].<信号>` 占位 (原厂引脚表/球位图未回) · **0 编造球位号**
  ③ 器件值: 能从规格/官方数据手册拿到的直接引; 拿不到的写 `[待选型]` / `[待原厂]`, 不写死
  ④ 所有 [待原厂] 行都挂 TBD-01..TBD-13 编号 (对应规格 undrawable[] 顺序)

★命名约定 (net 名必须是合法标识符):
  - 规格信号名带 `+` / `-` (KEY_VOL+ / KEY_VOL-) · 净名用 `KEY_VOL_P` / `KEY_VOL_M`
  - 带串阻/AC 耦合的信号: SoC·器件 那段网加 `_SRC` 后缀 (`CSI_D0_CK_P_SRC`),
    器件·连接器 那段用裸名 (`CSI_D0_CK_P`) —— 同一根线上两段网不能同名
  - **出口自检**: 所有 net 名不匹配 `^[A-Za-z0-9_]+$` 直接报错退出

用法:
  python3 state/gen_netlist.py            # 写 HW/netlist_v1.csv
  python3 state/gen_netlist.py --summary  # 顺便打印每页行数 + 器件统计
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SPEC = os.path.join(PROJ, "HW", "SCHEMATIC_V1_SPEC.json")
OUT = os.path.join(PROJ, "HW", "netlist_v1.csv")

COLS = ["page", "net", "node1", "node2", "ref", "value", "type", "dnp", "evidence", "tbd", "note", "conn_id",
        "board", "footprint", "opn"]

# ★★器件封装 / OPN 寄存器 (2026-10-29 ISS-112 · R-F6 新增) ★★
#   为什么要有: BOM_v1.csv 的 **封装列** 之前永远写 "待定" (MECH/cross_review_check.py C-9 判 FAIL:
#   "332/332 条 footprint = 待定 → 板面积/器件高度/连接器外形全部无法核算")。
#   而 netlist 里 **连 footprint 列都没有** ⇒ 光改 BOM CSV 是手改生成物 (ISS-075 明令禁止),
#   必须把封装当 **器件级数据** 落进生成器。
#   本表是 "位号 → (封装, OPN)" 的**唯一真源**; netlist_v1.csv 带出这两列,
#   gen_bom.py 再把它们搬到 BOM_v1.csv (BOM 仍是纯生成物, 重跑幂等)。
#   规则: **没查过官方 datasheet 的器件不许填** —— 宁可留空 (BOM 显示 待定), 不许编。
#
#   字段:
#     footprint —— PCB land pattern (封装尺寸 + pitch + 官方封装图编号)
#     opn       —— 厂商订购型号 (TI 的 "BQ25896RTWR" 这种), 询价/下单直接用
PARTS: dict[str, dict] = {
    # ★★2026-11-05 03:50 补两个 BOM 备料缺口 (footprint/opn 留"待定" ⇒ 备料/询价没有唯一口径)
    #   ① J_USB_C = **自绘 GCT USB4105-16P** (原厂图纸 Rev B3 Sheet 1, 见 HW/PCB/pinout_footprint.json / state/usb_c_footprint.py)
    "J_USB_C": {"footprint": "GCT USB4105-16P 自绘 land pattern (原厂图纸 Rev B3 Sheet 1: 16 焊盘单排 @0.50mm pitch, 焊盘 1.15x0.30mm, 2x Ø0.65mm 壳体固定孔 @±5.78mm, 板边距 8.94mm; 自绘见 state/usb_c_footprint.py)",
                 "opn": "GCT USB4105-16P (USB Type-C 母座 16P, SMT 顶装) —— ★**焊盘宽度按原厂 0.30mm** (登记曾误写 0.20mm)"},
    #   ② U_TEMP = TMP117 官方 WSON-6 (自绘, 见 HW/PCB/pinout_footprint.json / state/tmp117_footprint.py)
    "U_TEMP": {"footprint": "TMP117 WSON-6 2x2mm 自绘 (TI DRV0006B: 6 焊盘 @0.65mm pitch, 焊盘 0.45x0.30mm, 无散热焊盘 EP —— 原厂建议 EP 不焊以保测温精度)",
                 "opn": "TI TMP117 (DRV0006B, I2C 温度计 ±0.1°C, 地址 0x48)"},
    # ★2026-11-03 封装/OPN 落定 (原厂 datasheet, 见 HW/PCB/PINOUT_FOOTPRINT_SPEC.md)
    "J_TYPE_C": {"footprint": "SMT 贴片 USB-C 母座, 8.64 x 6.40 mm 焊盘区, 主体高 3.50 mm, 2x Ø0.50mm 定位孔 + 2x Ø0.65mm 壳体固定孔", "opn": "GCT USB4105 (USB Type C Receptacle for USB 2.0, SMT Type, PCB Top Mount)"},
    # ★2026-11-03 封装/OPN 落定 (原厂 datasheet, 见 HW/PCB/PINOUT_FOOTPRINT_SPEC.md)
    "Q2": {"footprint": "SON-8 Q3, 3.3 x 3.3 mm", "opn": "CSD16406Q3 (同 Q1)"},
    # ★2026-11-03 封装/OPN 落定 (原厂 datasheet, 见 HW/PCB/PINOUT_FOOTPRINT_SPEC.md)
    "U_DCDC_VCORE": {"footprint": "VQFN-16 RGT, 3.00 x 3.00 mm, 带散热焊盘", "opn": "TPS62130ARGTR"},
    # ★2026-11-03 封装/OPN 落定 (原厂 datasheet, 见 HW/PCB/PINOUT_FOOTPRINT_SPEC.md)
    "U_DCDC_VIO": {"footprint": "VQFN-16 RGT, 3.00 x 3.00 mm, 带散热焊盘", "opn": "TPS62130ARGTR"},
    # ★2026-11-03 封装/OPN 落定 (原厂 datasheet, 见 HW/PCB/PINOUT_FOOTPRINT_SPEC.md)
    "U_EN_SW": {"footprint": "UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch", "opn": "TPS22991RAA"},
    # ★2026-11-03 封装/OPN 落定 (原厂 datasheet, 见 HW/PCB/PINOUT_FOOTPRINT_SPEC.md)
    "U_LDO_IO18": {"footprint": "X2SON (DQN) 1.0 x 1.0 mm", "opn": "TPS7A2018DQNR"},
    # ★2026-11-03 封装/OPN 落定 (原厂 datasheet, 见 HW/PCB/PINOUT_FOOTPRINT_SPEC.md)
    "U_LDO_IO33": {"footprint": "X2SON (DQN) 1.0 x 1.0 mm", "opn": "TPS7A2033DQNR"},
    # ★2026-11-03 封装/OPN 落定 (原厂 datasheet, 见 HW/PCB/PINOUT_FOOTPRINT_SPEC.md)
    "U_LDO_L18": {"footprint": "X2SON (DQN) 1.0 x 1.0 mm", "opn": "TPS7A2018DQNR"},
    # ★2026-11-03 封装/OPN 落定 (原厂 datasheet, 见 HW/PCB/PINOUT_FOOTPRINT_SPEC.md)
    "U_LDO_L33": {"footprint": "X2SON (DQN) 1.0 x 1.0 mm, 0.4 mm max height, no-lead", "opn": "TPS7A2033DQNR"},
    # ★2026-11-03 封装/OPN 落定 (原厂 datasheet, 见 HW/PCB/PINOUT_FOOTPRINT_SPEC.md)
    "U_LDO_S12": {"footprint": "X2SON (DQN) 1.0 x 1.0 mm", "opn": "TPS7A2012DQNR"},
    # ★2026-11-03 封装/OPN 落定 (原厂 datasheet, 见 HW/PCB/PINOUT_FOOTPRINT_SPEC.md)
    "U_LDO_S18B": {"footprint": "X2SON (DQN) 1.0 x 1.0 mm", "opn": "TPS7A2018DQNR"},
    # ★2026-11-03 封装/OPN 落定 (原厂 datasheet, 见 HW/PCB/PINOUT_FOOTPRINT_SPEC.md)
    "U_PWR_SW": {"footprint": "UQFN-4 RAA, 0.85 x 0.75 mm, 0.4 mm pitch", "opn": "TPS22991RAA"},
    # ★2026-11-04 显示 FPC 座 (Pi5 22p) 封装/OPN 落定 —— 官方封装抄 Raspberry Pi 官方 CM4IO/CM5IO KiCad
    #   (Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal.kicad_mod); 焊盘 0.3x1.3mm / pitch 0.5 / pad1 在 +x 端
    "CONN_LIGHT": {"footprint": "Hirose FH12-22S-0.5SH, 22P / 0.5mm pitch / 右角(水平) / 底接触 / 1 固定柱, "
                               "焊盘 0.3x1.3mm (RPi 官方 CM5IO 封装: Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal)",
                   "opn": "FH12-22S-0.5SH(55)"},
    # ---- ISS-112: BQ25896 封装从 "VQFN-16 3×3mm (RGT)" 改为官方真实封装 ----
    # 旧写法 (VQFN-16 3×3 = 9mm²) **该封装根本不存在**, 占板面积少算 7mm²。
    # 官方三方一致: 产品页 "WQFN (RTW) / 24 / 16 mm² (4 mm × 4 mm)" +
    #              订购页 "BQ25896RTWR ACTIVE, WQFN (RTW) | 24" +
    #              datasheet 封装附录 "WQFN - 0.8 mm max height / RTW 24 / 4 x 4, 0.5 mm pitch (4224801/A)"
    "U_CHG": {
        "footprint": "WQFN-24 4x4mm P0.5 (RTW 24, 16mm², h<=0.8mm, TI 封装图 4224801/A)",
        "opn": "BQ25896RTWR",
    },
}

# ★板级归属 (2026-10-27 V1.1 新增列 board) —— 充电板在镜框 / 主 PCB 在镜脚, 两者跨铰链
#   CHG_BOARD = 充电板 (镜框): Type-C + 充电链 + 电池
#   MAIN_PCB  = 主 PCB (镜脚): SoC + 全部外设 + 保护/滤波件
#   HINGE     = 跨铰链界面本体 (连接器 / 跨铰链那一段)
BOARD_CHG = "CHG_BOARD"
BOARD_MAIN = "MAIN_PCB"
BOARD_HINGE = "HINGE"
LEGAL_BOARD = {BOARD_CHG, BOARD_MAIN, BOARD_HINGE}

# 跨铰链界面上的 4 个连接器 (全部 HINGE)
# ★★2026-11-02 19:4x demo 板形态 (老板 19:25/19:35): camera/display 改成**板内 FPC 座** ⇒ 不再跨铰链
#   ⇒ HINGE 只剩**充电链**两个连接器 (J_CHG 充电 + CONN_USB) —— 那属整机阶段的镜框充电板
#   ⇒ demo 板阶段: 充电链不装 (直接 USB 供电), camera/display 两个模组用 FPC 连主板
HINGE_REFS = {"J_CHG"}   # ★2026-11-04 19:5x: CONN_USB 跨铰链 USB 座已删 (跨铰链取消)
# 充电板 (镜框) 上的器件 —— ★V1.2: 电池 + 电池保护 IC + 2×MOS 移到**镜脚主 PCB** (MECH 体积硬约束)
CHG_BOARD_REFS = {
    "D_CHG_LED", "Q_CHG_LED", "R_CHG_LED", "C_REGN", "R_ILIM",
    "J_TYPE_C", "D_ESD_TC", "FB_VBUS", "C_VBUS_IN", "C_VBUS_OUT", "U_CHG",
    "TP_VBUS", "R_CC1", "R_CC2", "R_TS_TOP",
    "NET_VBUS_5V_CHG",
    # ★V1.6: P10 充电板页新增的件 (BQ25896 外围) 全在镜框充电板
    "R_PSEL", "R_CE", "R_OTG", "R_PU_SCL", "R_PU_SDA", "R_PU_INT", "R_STAR_PGND",
    "C_VBUS_IC", "C_PMID", "C_BST", "C_BAT", "C_SYS", "L_CHG", "D_TVS_VBUS", "TP_TS",
    # ★它发现的缺陷: VBUS_DET 的 1M+1M 分压物理上必须在**充电板**
    #   (充电板 VBUS 不过铰链到主板 · 分压放在主板 = 采不到电)
    "R_VBUS_DET_1", "R_VBUS_DET_2",
}

PAGES = {
    "P1": "电源树 (13 电源域 + 充电链)",
    "P2": "SoC 主控 (低速控制 / ADC / I2C / FSIN)",
    "P3": "启动存储 (焊盘位 + 串阻位, 不画存储芯片)",
    "P4": "显示双出口 (DSI 原生 / 桥接 互斥 0Ω 位)",
    "P5": "MIPI-CSI 传感器 (CONN_CAM 40p **板内 FPC 座**, demo 阶段 2-lane)",
    "P6": "高速差分与连接器 (DP_TX / USB / Type-C)",
    "P7": "板级接口与测试点 (TP + 按键 + LED + ID 跳线)",
    "P8": "时钟 · 复位 · 调试 (XTAL / RESET / BOOT / JTAG / UART)",
    "P9": "跨铰链界面 (★demo 阶段仅充电链 USB+充电; camera/display 已改板内 FPC)",
    "P10": "充电板 (镜框) 整页: Type-C 16p 物理脚位 + BQ25896 24 脚 + 温度检测三件式 + R_ILIM 硬件限流",
}

# 关键词 · TBD 编号 (对应规格 undrawable[] 顺序: 1 引脚表 2 电源域 3 CSI 规格 4 显示TX
# 5 pitch 6 启动存储 7 帧同步 8 充电状态 9 DDC 独立 10 USB PHY 11 存储挂载 12 时序 13 FSIN)
TBD_RULES = [
    (r"CONN_CAM|CSI_", "TBD-03"),
    (r"CONN_LIGHT|DSI_D0|DSI_DDC|DP_TX|BR_", "TBD-04"),
    (r"V_CORE|V_SOC_IO|SENSOR_|LIGHT_", "TBD-02"),
    (r"USB_", "TBD-10"),
    (r"FSIN", "TBD-13"),
    (r"RESET_N|BOOT_N|XTAL", "TBD-12"),
    (r"JTAG|UART", "TBD-01"),
]

NET_RE = re.compile(r"^[A-Za-z0-9_]+$")


def tbd_for(text: str) -> str:
    for pat, t in TBD_RULES:
        if re.search(pat, text or ""):
            return t
    return ""


def dnp_of(text: str) -> str:
    """规格里的 dnp 原文更丰富 (如 'DNP (无无线)' / '预留, 与 USB 二选一') · 归一化成 3 档, 原文进 note"""
    t = (text or "").strip()
    if t.startswith("必装") or t.startswith("装"):
        return "必装"
    if t.startswith("DNP"):
        return "DNP"
    return "可选"


def ev_of(text: str, default: str = "[推算]") -> str:
    for tag in ("[待原厂]", "[待JBD]", "[同Die参考-待官方确认]", "[官方]", "[实测]", "[推算]", "[0数据]"):
        if tag in (text or ""):
            return tag
    return default


def clean_net(s: str) -> str:
    """net 名归一化: 规格信号名里的 + / - / . 等非法字符 · 合法标识符"""
    s = (s or "").strip()
    s = s.replace("+", "_P").replace("-", "_M")
    s = re.sub(r"[^A-Za-z0-9_]", "_", s)
    return re.sub(r"_+", "_", s).strip("_")


def board_for(r: dict) -> str:
    """板级归属: 充电链器件在充电板 (镜框), SoC 与外设在主 PCB (镜脚), 跨铰链界面本身标 HINGE

    ★为什么要这一列 (2026-10-27): 充电板在镜框 / 主 PCB 在镜脚 · **有两块板**, 必然跨铰链。
      V1 的 netlist 没有板级归属 · 看图的人分不清"这颗器件装哪块板", 而跨铰链的通道数
      (4 组) 与应力点直接决定结构方案与板宽 · 必须画清楚。
    """
    ref = (r.get("ref") or "").strip()
    blob = f"{ref} {r.get('node1', '')} {r.get('node2', '')}"
    if ref in HINGE_REFS:
        return BOARD_HINGE
    if ref in CHG_BOARD_REFS:
        return BOARD_CHG
    if ref.startswith("RAIL_") or ref.startswith("NET_"):
        if re.search(r"J_TYPE_C|U_CHG", blob):
            return BOARD_CHG
        # ★★2026-11-02 19:4x: camera/display 的 FPC 座在**主板** (不再跨铰链) ⇒ 不进 HINGE
        if re.search(r"J_CHG|CONN_USB", blob):
            return BOARD_HINGE
        if ref in ("RAIL_VBUS_5V", "NET_VBUS_5V_CHG"):
            return BOARD_CHG
        # ★V1.5 修正: RAIL_BAT / RAIL_SYS / R_NTC_BAT 都在**镜脚** (电池在镜脚, V1.2 裁决) · MAIN_PCB
        return BOARD_MAIN
    if re.search(r"J_TYPE_C|U_CHG", blob):
        return BOARD_CHG
    return BOARD_MAIN



# ================================================================ ★引脚映射 (真实脚号)
# ★真值源: HW/PCB/pinout_footprint.json (按**原厂 datasheet** 整理, 每条带出处)
#   ⇒ 网表里**不再出现** "U_EN_SW ON" 这种"脚名"写法 ⇒ 一律 "U_EN_SW pin2" ⇒ 板子焊盘号=真实脚号
_PINMAP_PATH = os.path.join(PROJ, "HW", "PCB", "pinout_footprint.json")
try:
    # ★规格 JSON 的 pins 形如 {"1": "VIN", "2": "ON", ...} ⇒ **键=脚号, 值=脚名**
    #   ⇒ 改写时要用的是 **脚名 → 脚号** ⇒ ⇒ 这里把**数字键**的部分反转
    _raw = json.load(open(_PINMAP_PATH, encoding="utf-8")).get("parts") or {}
    _PINMAP = {}
    for _k, _v in _raw.items():
        _pins = _v.get("pins") or {}
        _num = {}
        for _nn, _vv in _pins.items():
            if str(_nn).isdigit():
                _num[str(_vv)] = str(_nn)      # ★脚名 → 脚号
        _PINMAP[_k] = _num if _num else {}    # ★非数字键 (USB-IF 的 A1/B12 之类) 本来就是脚名, 不改写
except Exception:
    _PINMAP = {}


def _apply_pin_maps(rows):
    """把 "<器件> <脚名>" 的节点串改写成 "<器件> pin<真实脚号>" (查不到就原样保留, 由门禁报出来)"""
    changed = unknown = 0
    for r in rows:
        for k in ("node1", "node2"):
            v = (r.get(k) or "").strip()
            mm = re.fullmatch(r"([A-Za-z_0-9]+)\s+(.+)", v)
            if not mm:
                continue
            comp, name = mm.group(1), mm.group(2).strip()
            pm = _PINMAP.get(comp)
            if not pm:
                continue
            if name in pm:
                r[k] = f"{comp} pin{pm[name]}"
                changed += 1
            elif not re.fullmatch(r"pin\d+(\+pin\d+)*", name):
                unknown += 1
    print(f"  [脚号改写] {changed} 处 · 仍无脚号的命名脚 {unknown} 处")
    return rows


# ★★2026-11-03 20:1x: 电源 IC 的引脚一律用**真实脚号** (查 HW/PCB/pinout_footprint.json)
#   ⇒ 起因: 槽位门禁 check_schematic_slots 的 B 项发现 14 个器件"引脚不全"
#   ⇒ 根因: LDO 的 OUT/IN 用的是**裸节点/脚名** ("U_LDO_IO33" / "U_LDO_IO33 VIN") ⇒ 板子上焊盘号是行序占位
_PM_PATH = os.path.join(PROJ, "HW", "PCB", "pinout_footprint.json")
try:
    _PM_RAW = json.load(open(_PM_PATH, encoding="utf-8")).get("parts") or {}
    # ref -> {脚名: 脚号}
    _PIN_NUM = {k: {str(vv): str(nn) for nn, vv in (v.get("pins") or {}).items()}
                for k, v in _PM_RAW.items()}
except Exception:
    _PIN_NUM = {}


def pin_of(ref, name, default=None):
    """ref 的 'name' 引脚的真实脚号 (查不到 ⇒ 返回 default)"""
    m = _PIN_NUM.get(ref) or {}
    return m.get(name, default)

ROWS: list[dict] = []


# ================================================================ ★A2 段: SoM 真实引脚
# ★为什么要有 soc_pin(): 旧写法 "SoC[RK3572].<信号>" 是**占位符** ⇒ 网表里看不出落到哪个脚
#   ⇒ 板子照着画 ⇒ 画出来的板子接不上模块。**现在占位符物理上不可能再进网表**。
#   真值: HW/PCB/som_pin_assign.json (由 state/_iss165_a2_som.py 从 Forlinx OK3572-C 官方手册生成)
_SOM_ASSIGN_PATH = os.path.join(PROJ, "HW", "PCB", "som_pin_assign.json")
_SOM_ASSIGN = json.load(open(_SOM_ASSIGN_PATH, encoding="utf-8"))
SOM_ASSIGN = _SOM_ASSIGN.get("assign", {})
SOM_DNP = _SOM_ASSIGN.get("dnp", {})


def soc_pin(sig: str) -> str:
    """SoC 侧信号名 → 真实引脚节点 (J_SOM_Px pinN); 未引出 ⇒ SoC_NC; 未分配 ⇒ 报错"""
    if sig in SOM_DNP:
        return "SoC_NC"
    m = SOM_ASSIGN.get(sig)
    if not m:
        raise KeyError(f"★SoC 信号没分配引脚: {sig} ⇒ 先去 HW/PCB/som_pin_assign.json 补 "
                       f"(分配表由 state/_iss165_a2_som.py 从手册引脚表生成)")
    return f"J_SOM_{m['conn']} pin{m['num']}"



# ★★2026-11-03 09:54 老板口径: "没有整机, 没有镜脚, demo/主板用 type-c 供电"
#   ⇒ **demo 主板不装电池、不上充电链** ⇒ 电池侧那套 (电池 + 保护 IC + MOS + 分压) 一律 DNP
#   ⇒ 充电 IC (U_CHG 那套) 与跨铰链两个座本来就在 board=CHG_BOARD / HINGE ⇒ 板生成器按板级过滤就不上板
DEMO_DNP = {
    "U_BATPROT": "demo 主板用 Type-C 供电 ⇒ 不装电池 ⇒ 电池保护 IC 不装",
    "Q1": "同上 (电池保护的高边 MOS)",
    "BT_432243": "同上 (不装电池)",
    "R_BAT_DET_1": "同上 (电池电压分压上臂)",
    "R_BAT_DET_2": "同上 (电池电压分压下臂)",
    "C_DET_BAT": "同上 (电池 ADC 滤波)",
    "TP_BAT": "同上 (电池测点)",
    "R_NTC_BAT": "同上 (NTC)",
    "R_TS_PULL": "同上 (NTC 分压下臂)",
    "R_TS_TOP": "同上 (TS 分压上臂)",
    "J_BOOT1": "★SoM 板载 eMMC/SD ⇒ 主板不挂 SPI-NOR 启动存储 (焊盘位可留作扩展)",
    "X1": "★晶振在 SoM 板上 ⇒ 主板不接",
    "U_SUPV": "★SoM 内部 PMIC 已做上电复位 (Forlinx 官方载板复位电路 = 按键+100nF+ESD, 无监督器) ⇒ 主板不装监督器",
    "C_SUPV": "同上 (监督器去耦电容)",
}


def add(page, net, node1, node2, ref, value, typ, dnp, ev, tbd, note, cid=""):
    p = PARTS.get(ref, {})
    if ref in DEMO_DNP:
        dnp = "DNP"
        note = f"[{ref}] ★DNP: {DEMO_DNP[ref]} | " + note
    ROWS.append(dict(page=page, net=net, node1=node1, node2=node2, ref=ref, value=value, type=typ,
                     dnp=dnp, evidence=ev, tbd=tbd, note=note, conn_id=cid,
                     footprint=p.get("footprint", ""), opn=p.get("opn", "")))


# ---------------------------------------------------------------- P1 电源树
def build_p1(by_id, spec):
    """充电链 (充电板侧: Type-C · ESD · π 滤波 · BQ25896 · BQ2970+2×MOS · 电池)
       + 13 条电源域 (2×DC-DC + 7×LDO) + 去耦"""

    # ---- 充电链 ----
    add("P1", "VBUS_5V", "J_TYPE_C A4+A9+B4+B9", "D_ESD_TC", "RAIL_VBUS_5V", "5.0V ±5%", "RAIL", "必装",
        "[推算]", "",
        "电源域: 目标 5.0V ±5% / 最大电流 2.0A (PD 5V/2A); **充电链整条在充电板**, "
        "SYS 经 J_CHG 回主 PCB; SoC 侧球位号 TBD-01", "C-01")
    add("P1", "VBUS_5V", "J_TYPE_C", "USB_VBUS_RAW", "J_TYPE_C", "Type-C 16p 座 (充电板侧, 物理脚位 A/B 编号)", "CONN",
        "必装", "[官方]", "",
        "Type-C 入口连接器 (充电板侧, 在镜框); 本表 pin 编号为**逻辑编号** (pin1=VBUS, pin2=CC1, "
        "pin3=CC2, pin4=D+, pin5=D-, pin6=GND), **非 USB-IF 物理脚位**; 屏蔽壳 · GND", "C-01")
    add("P1", "USB_VBUS_RAW", "USB_VBUS_RAW", "D_ESD_TC", "D_ESD_TC", "ESD 阵列 [待选型]", "D",
        "必装", "[推算]", "",
        "Type-C VBUS 入口 ESD 阵列 (规格 C-01 'Type-C 座 + ESD 阵列'); 通道数/钳位电压随 Type-C 座定",
        "C-01")
    add("P1", "VBUS_5V_ESD", "D_ESD_TC", "FB_VBUS", "FB_VBUS", "π 滤波磁珠 [待选型]", "L",
        "必装", "[推算]", "",
        "[VBUS_5V_ESD] VBUS 入口 π 滤波磁珠位 (阻抗/电流随充电 IC 环路稳定性定)", "C-01")
    add("P1", "VBUS_5V_ESD", "VBUS_5V_ESD", "C_VBUS_IN", "C_VBUS_IN", "[待选型] 10µF", "C",
        "DNP", "[推算]", "",
        "π 滤波输入电容位 (值待充电 IC 定; 内置则改 DNP)", "C-01")
    add("P1", "GND", "C_VBUS_IN", "GND", "C_VBUS_IN", "[待选型] 10µF", "C",
        "DNP", "[推算]", "", "π 滤波输入电容 地端", "C-01")
    add("P1", "VBUS_5V_F1", "FB_VBUS", "C_VBUS_OUT", "FB_VBUS", "π 滤波磁珠 [待选型]", "L",
        "必装", "[推算]", "",
        "[VBUS_5V_F1] π 滤波磁珠 后级侧 (与 FB_VBUS 同一颗)", "C-01")
    add("P1", "VBUS_5V_F1", "VBUS_5V_F1", "C_VBUS_OUT", "C_VBUS_OUT", "[待选型] 100µF", "C",
        "DNP", "[推算]", "",
        "π 滤波后级电容位 (BQ25896 建议 ≥100µF)", "C-01")
    add("P1", "GND", "C_VBUS_GND", "GND", "C_VBUS_GND", "[待选型] 100µF", "C",
        "DNP", "[推算]", "",
        "π 滤波后级**对地**电容 (★V1.6 修正: 原来 C_VBUS_OUT 一颗当两个用 —— 既是 FB·U_CHG 的串联电容, "
        "又是对地电容 · 一颗 2 脚件落进 3 个网 = 导出后一脚悬空); BQ25896 建议 ≥100µF", "C-01")
    add("P1", "VBUS_5V_CHG", "C_VBUS_OUT", "U_CHG pin1", "C_VBUS_OUT", "[待选型] 100µF", "C",
        "DNP", "[推算]", "", "π 滤波电容 (后级, 串联) 位", "C-01")
    add("P1", "VBUS_5V_CHG", "C_VBUS_GND", "C_VBUS_OUT", "C_VBUS_GND", "[待选型] 100µF", "C",
        "DNP", "[推算]", "",
        "π 滤波后级对地电容的信号端 (与 C_VBUS_OUT 同一节点)", "C-01")
    add("P1", "VBUS_5V_CHG", "U_CHG", "NET_VBUS_5V_CHG", "U_CHG", "BQ25896", "IC",
        "必装", "[官方]", "",
        "[VBUS_5V_CHG] 1A 单节锂电充电 IC (TI); 输入接 VBUS_5V_F1, BAT 脚接 BAT 轨, "
        "STAT/PG 脚回主 PCB (见 P2)", "C-01")
    # ---- ★V1.2 (2026-10-27): 电池与电池保护从"充电板"移到**镜脚主 PCB** (MECH 体积硬约束) ----
    #   MECH_BUDGET: 电池 4.12cc **镜框装不下** · 电池在镜脚; 充电板 (Type-C + BQ25896) 按 ISS-014 决策 5 在镜框
    #   ⇒ **跨铰链的大电流是充电电流 (1.0-1.5A), 不是 SYS (0.55A)** · SYS 全程在镜脚产生, 不过铰链 ✅
    #   ⇒ 电池保护 IC (BQ2970) + 2×MOS 与电池同板 (镜脚) · 保护回路短, 更对
    add("P1", "BAT_CHG", "U_CHG pin13+pin14", "RAIL_BAT_CHG", "NET_BAT_PROT", "单端", "NET", "必装",
        "[官方]", "",
        "[BAT_CHG] ★V1.2: 充电电流路径 (1.0-1.5A) 镜框充电板 BQ25896 · 跨铰链 · 镜脚电池; "
        "**铰链段不加 π 滤波** (会破坏充电 IC 的环路稳定性); 靠双 pin 并联 + 载流铜箔 + 压降核算", "C-03")
    add("P1", "BAT_CHG", "RAIL_BAT_CHG", "J_CHG pin1", "RAIL_BAT_CHG", "跨铰链 1.5A (双 pin 并联)",
        "NET", "必装", "[推算]", "",
        "[BAT_CHG] 充电电流跨铰链 (J_CHG pin1/pin2 并联); 载流/压降/发热核算见 P9 页", "C-02")
    add("P1", "BAT_CHG", "J_CHG pin1", "J_CHG pin2", "J_CHG", "跨铰链 1.5A (双 pin 并联)", "NET",
        "必装", "[推算]", "",
        "[BAT_CHG] 双 pin 并联 (每 pin ≈0.75A, 1.27mm 排线); 铰链段压降与发热按结构实际长度核算", "C-02")
    add("P1", "BAT_CHG", "J_CHG pin2", "U_BATPROT", "NET_BAT_PROT", "单端", "NET", "必装",
        "[官方]", "",
        "[BAT_CHG] 充电电流进镜脚侧电池保护 IC (BQ2970) —— **保护 IC 与电池同板 (镜脚)**", "C-03")
    add("P1", "TS_BAT", "R_NTC_BAT", "PGND", "R_NTC_BAT", "103AT NTC ±1% (贴电芯, 另一端接 TS 专用回流)",
        "R", "必装", "[官方]", "",
        "[TS_BAT] ★V1.8 修正 (ISS-091 结构核算): NTC 下端**不接系统地**, 接 **TS 专用回流** —— 1A 充电电流会把 TS "
        "参考地抬高 14-32mV (= 0.44-0.99°C 温度偏差), 而 TS 是**停充安全门限**; 专用回流后偏差 <0.01°C", "C-01")
    add("P1", "TS_BAT", "R_TS_PULL", "PGND", "R_TS_PULL", "30.31k ±1%", "R", "必装", "[官方]", "",
        "[TS_BAT] ★V1.8: RT2 30.31k 下端同样接 **TS 专用回流** (与 NTC 并联构成三件式检测网络)", "C-01")
    for pn in (9, 10):
        add("P1", "HINGE_RSV", f"J_CHG pin{pn}", f"J_CHG pin{pn}", "J_CHG", "预留 (不装)",
            "NET", "DNP", "[推算]", "",
            f"[HINGE_RSV] J_CHG pin{pn} 预留位 (★V1.8: pin10 已改作 **TS 专用回流**, pin9 仍预留; "
            f"充电 IC 的 I2C 本板自闭环不跨铰链, 用不上这脚)", "C-02")
    add("P1", "GND_CHG", "J_CHG pin3", "J_CHG pin4", "J_CHG", "回流 (双 pin)", "NET", "必装",
        "[推算]", "",
        "[GND_CHG] 充电电流回流双 pin (与电源 pin 相邻 · 环路面积最小)", "C-02")
    add("P1", "GND_CHG", "J_CHG pin4", "GND", "J_CHG", "回流 (双 pin)", "NET", "必装",
        "[推算]", "", "[GND_CHG] 回流进镜脚侧数字地", "C-02")
    add("P1", "BAT", "RAIL_BAT", "U_BATPROT", "RAIL_BAT", "4.2V 满 / 3.0V 截止", "RAIL",
        "必装", "[官方]", "",
        "电源域: 目标 4.2V 满 / 3.0V 截止 / 最大电流 1.0-1.5A 充电; 电流路径 电池·Q2·Q1·本轨; "
        "★V1.2: **电池在镜脚主 PCB** (MECH 体积硬约束: 4.12cc 镜框装不下); SoC 侧球位号 TBD-01", "C-03")
    add("P1", "BAT", "U_BATPROT", "RAIL_BAT", "U_BATPROT", "BQ2970", "IC",
        "必装", "[官方]", "",
        "[BAT] 1 节锂电保护 IC (配 2×MOS), **与电池同板 (镜脚)**; 具体型号/封装待选型 "
        "(BQ2970 系列为规格原文所指)", "C-03")
    # ★F2 修正 (2026-10-27 09:1x, hw-lead ISS-088 复审发现): 原来 Q1/Q2 落在**同一个 net** = 两管并联
    #   (并联 MOS 不提供断开功能 = 保护无效), 而且**没有栅极连接**、**电芯负端 (B-) 没画**。
    #   正确拓扑 (BQ2970): 电芯+ · Q1 · Q2 · 保护后 B+ (两管**串联**), 两管栅极由 BQ2970 同驱,
    #   电芯- · BQ2970 的 B- 脚。
    add("P1", "BAT_CELL_P", "BT_432243 B+", "Q1", "BT_432243", "432243 3.7V ≥420mAh", "CONN",
        "必装", "[推算]", "",
        "[BAT_CELL_P] 电芯正极 · 第 1 只保护 MOS (Q1) 漏极; 尺寸 4.3×2.4mm 级, 焊接方式待结构确认", "C-03")
    add("P1", "BAT_PROT_CELL", "Q1", "Q2", "Q1", "[待选型] N-MOS", "SW",
        "必装", "[推算]", "",
        "[BAT_PROT_CELL] ★F2 修正: Q1 与 Q2 **串联** (原来两管同网 = 并联, 保护无效); "
        "V_DS / 栅压 / R_DS(on) / 封装待 BQ2970 数据手册确认", "C-03")
    add("P1", "BAT_PROT_CELL2", "Q2", "U_BATPROT", "Q2", "[待选型] N-MOS", "SW",
        "DNP", "[推算]", "",
        "[BAT_PROT_CELL2] 第 2 只保护 MOS · 电池保护 IC (BQ2970) 的 B+ 脚; 参数同 Q1", "C-03")
    # ★★2026-11-03 按**原厂 datasheet** 拆: BQ2970 **没有单一 GATE 脚** —— 原厂是
    #   **COUT(pin2, 充电管) / DOUT(pin3, 放电管) 两个独立栅驱动** ⇒ ★**两管不可共栅**
    #   (共栅 ⇒ 充电时放电管也导通 ⇒ 电池永远放不出电流 ⇒ 保护逻辑失效)
    add("P1", "BAT_COUT", "U_BATPROT pin2", "Q2", "U_BATPROT", "COUT (充电管栅驱动)", "NET",
        "DNP", "[官方]", "",
        "[BAT_COUT] ★BQ2970 的 COUT (pin2) ⇒ **只**驱动充电管 Q2 的栅极 (原厂要求两管不可共栅)", "")
    add("P1", "BAT_DOUT", "U_BATPROT pin3", "Q1", "U_BATPROT", "DOUT (放电管栅驱动)", "NET",
        "DNP", "[官方]", "",
        "[BAT_DOUT] ★BQ2970 的 DOUT (pin3) ⇒ **只**驱动放电管 Q1 的栅极", "")
    add("P1", "BAT_COUT", "Q2", "GND", "Q2", "[待选型] N-MOS (充电高边开关)", "SW", "DNP", "[推算]", "",
        "[BAT_COUT] Q2 (充电管) 源极接地", "")
    add("P1", "GND", "Q2", "GND", "Q2", "[待选型] N-MOS (充电高边开关)", "SW", "DNP", "[推算]", "",
        "[BAT_COUT] Q2 地脚", "")
    add("P1", "BAT_DOUT", "Q1", "GND", "Q1", "[待选型] N-MOS (放电高边开关)", "SW", "DNP", "[推算]", "",
        "[BAT_DOUT] Q1 (放电管) 源极接地", "")
    add("P1", "GND", "Q1", "GND", "Q1", "[待选型] N-MOS (放电高边开关)", "SW", "DNP", "[推算]", "",
        "[BAT_DOUT] Q1 地脚", "")
    add("P1", "BAT_GATE", "Q1 GATE", "Q2 GATE", "Q1", "[待选型] N-MOS", "SW",
        "必装", "[推算]", "",
        "[BAT_GATE] 两管共栅 (back-to-back 接法, 按 BQ2970 数据手册确认体二极管方向)", "C-03")
    add("P1", "BAT_CELL_N", "BT_432243 B-", "U_BATPROT B-", "BT_432243", "432243 3.7V ≥420mAh",
        "CONN", "必装", "[推算]", "",
        "[BAT_CELL_N] ★F2 修正: **电芯负极 · BQ2970 的 B- 脚** (原来电芯只有一个端子 · 电池回路不闭合)", "C-03")
    add("P1", "SYS", "RAIL_SYS", "U_PWR_SW VOUT", "RAIL_SYS", "3.0-4.2V", "RAIL",
        "必装", "[推算]", "",
        "电源域: 目标 3.0-4.2V / 最大电流 0.55A (330mA×1.5 + 瞬态); **R-F1 裁决: SYS 下限抬到 3.5V**; "
        "★V1.2: **SYS 在镜脚本地产生** (电池在镜脚 · 电池保护后就是 SYS) · **SYS 不过铰链** "
        "(跨铰链的只有充电电流 1.0-1.5A); ★V1.8: SYS 现在**经过负载开关** (老板 10-28 拍板关机=断电) · "
        "开关关时 SYS 全断, 而充电链 (BQ25896 在镜框) 仍在电池侧带电 ⇒ 关机也能充电; SoC 侧球位号 TBD-01", "C-02")
    add("P1", "BAT_CHG", "J_CHG", "J_CHG", "J_CHG", "1×10p@0.5mm 排线座 (充电板↔主 PCB, 跨铰链载流)",
        "CONN", "必装", "[推算]", "",
        "★V1.9 结构侧回执: **J_CHG 实物是一对** (框侧座 + 脚侧座), 采购/备料别只算一只; 单触点额定判据收紧到 **≥0.5A**; 首选 Hirose FH12-10S-0.5SH(55) (未询价, 外发经项目总工)。" "[SYS] ★V1.5 定稿 pin map (1×10p@0.5mm): pin1/pin2=BAT_CHG (充电电流**双 pin 并联**), "
        "pin3/pin4=GND (回流双 pin), pin5=CHG_STAT, pin6=PWR_GOOD, pin7=VBUS_DET, "
        "pin8=**TS** (电池 NTC 在镜脚, TS 跨铰链), pin9/10=预留 (充电 IC I2C 不跨铰链); "
        "★BAT_DET 不跨铰链 (电池在镜脚本地检测); 型号/载流待结构复核 (ISS-091 算压降发热); "
        "★pin 编号为**本版自拟**", "C-02")

    # ---- ★V1.1 补画 1: 电池 NTC 接 BQ25896 的 TS 脚 (硬件停充, 安全项, V1 漏画) ----
    add("P1", "TS_BAT", "U_CHG pin11", "R_NTC_BAT", "NET_TS_BAT", "单端", "NET", "必装",
        "[官方]", "",
        "[TS_BAT] ★电池温度检测: 103AT NTC 接 BQ25896 的 TS 脚 (过温/欠温时**硬件直接停充**; 分压网络按 datasheet 三件式) "
        "(不依赖 SoC, 属安全项); 与 P2 的 SoC 侧数字温度计 U_TEMP 是两回事, 不能互相替代", "C-01")
    add("P1", "TS_BAT", "R_NTC_BAT", "R_TS_PULL", "R_NTC_BAT", "103AT NTC ±1% (贴电芯)",
        "R", "必装", "[官方]", "",
        "[TS_BAT] ★V1.5 修正: NTC **贴电芯 ⇒ 在镜脚** (V1.2 电池搬镜脚后), 而 BQ25896 的 TS 脚在镜框充电板 "
        "· **TS 必须跨铰链** (J_CHG pin8, 高阻无电流); NTC 按 BQ25896 datasheet 取 **103AT** "
        "(与 30.31k 并联构成温度检测网络); ★V1.6 修正: NTC 另一端按 datasheet 三件式接 **GND** (电芯负极侧), 原来接电芯正极 = 与分压公式不符", "C-01")
    add("P1", "PGND", "R_TS_PULL", "PGND", "R_TS_PULL", "30.31k ±1% (RT2)", "R", "必装", "[官方]", "",
        "[TS_BAT] TS 对地下拉 = **RT2 30.31k** (BQ25896 datasheet 温度检测分压); ★V1.6 挪到**镜脚** (NTC 侧) —— "
        "下拉放在连接器远端, FPC 漏电流不进入分压 (FPC 漏电 µA 级, 30k 下拉远大于它)", "C-01")
    add("P1", "TS_BAT", "J_CHG pin8", "R_NTC_BAT", "J_CHG", "跨铰链 (高阻)",
        "NET", "必装", "[推算]", "",
        "[TS_BAT] ★V1.5 补画: **TS 跨铰链这一段** (V1.2 把电池/NTC 搬镜脚时漏了) · 走 J_CHG pin8", "C-01")
    add("P1", "REGN", "U_CHG pin22", "R_TS_TOP", "U_CHG", "BQ25896 内部 5V (REGN)", "NET",
        "必装", "[官方]", "",
        "[REGN] ★V1.6 补: BQ25896 的 **REGN 5V** (内部 LDO 输出, RT1 的参考端) —— 原来 R_TS_TOP 的"
        " REGN 端没有对应节点 · 导出后一脚悬空; 同时补 REGN 去耦电容位", "C-01")
    add("P1", "REGN", "C_REGN", "U_CHG pin22", "C_REGN", "[待选型] 1µF", "C",
        "必装", "[官方]", "", "[REGN] BQ25896 REGN 去耦电容 (datasheet 要求)", "C-01")
    add("P1", "GND", "C_REGN", "GND", "C_REGN", "[待选型] 1µF", "C",
        "必装", "[官方]", "", "[REGN] REGN 去耦电容 地端", "C-01")
    # ★★2026-11-02 02:0x 修一个**真缺陷**: 这里的 node2 原写 "U_CHG pin22" (BQ25896 的 REGN 脚),
    #   正确是 **pin11 (TS 脚)** —— RT1 是 REGN→TS 的上拉, 另一端必须落在 TS。
    #   ★为什么一直没被抓到: `.net` 生成器会**按连通性重排引脚**, 所以 .net 一直是对的,
    #   错的是 **CSV (连接清单)** ⇒ PCB 工程师按 CSV 接线就会把 REGN 短到 NTC 节点 ⇒ 充电链失效。
    #   ⇒ 新增 `state/gen_netlist_pins.py` (pin-centric 表) + check_netlist 判据 31 把这类错变成常驻门禁。
    add("P1", "TS_BAT", "R_TS_TOP", "U_CHG pin11", "R_TS_TOP", "5.24k ±1% (RT1: REGN 到 TS)",
        "R", "必装", "[官方]", "",
        "[TS_BAT] ★V1.5 补画: **RT1 5.24k (REGN 到 TS)** —— BQ25896 温度检测是 RT1/RT2/NTC 三件式, "
        "原来只画了 NTC + 10k 下拉 = 分压比完全不对 (datasheet: 0°C·73.25%, 60°C·34.375%)", "C-01")

    # ---- ★V1.5 补画: R_ILIM 硬件限流 (BQ25896 的 IINLIM **复位默认 2048mA**) ----
    #   不装这颗电阻 · 铰链段可能被灌 ~1.68A (ICHG≈0.822×IIN) · 铰链发热 + 压降失控。
    #   装 300Ω · IINMAX = KILIM/RILIM ≈ 1.07-1.30A · ICHG ≈ 0.88-1.07A (ISS-091 核算输入)
    #   ⇒ 换料不换板: 若结构核算说铰链只吃 1.0A, 改 390Ω · ICHG 0.67-0.82A
    #   ★V1.9 定稿 (2026-10-28): 390Ω (老板 10-28 拍板『边戴边充不允许』⇒ 皮肤温度不再是充电时硬约束)
    add("P1", "IINLIM", "U_CHG pin10", "R_ILIM", "R_ILIM", "390Ω ±1% (IINMAX ≈1.00A · ICHG ≈0.82A · 单 pin 0.411A)",
        "R", "必装", "[官方]", "",
        "[IINLIM] ★★V1.7 按 ISS-091 结构核算定 **470Ω**: BQ25896 的 IINLIM 复位默认 **2048mA** [官方] "
        "(不装 = 铰链吃 ~1.68A); 结构总工核算 (MECH/HINGE_POWER_CALC.md, 可跑): "
        "**300Ω · ICHG 1.07A · 充电时皮肤侧 47.1°C 超 ISO 13732-1 的 43°C 红线** (加厚铜箔到 2oz 也只能到 45.2°C, 救不了); "
        "470Ω · 0.68A · 39.9°C (充电 ~35min); 680Ω · 0.47A · 37.3°C. "
        "★★★**V1.8 改 (老板 10-28 拍板『边戴边充不允许』)**: 充电时眼镜不在皮肤上 ⇒ **皮肤温度不再是充电时的硬约束** ⇒ "
        "充电电流可以提上来 ⇒ **定为 390Ω (ICHG 0.82A, 充电 ~29min)**: 单 pin 0.411A ≤ 常见 0.5A 触点 (ISS-099 待查回规格), "
        "充电板/电芯温升仍在可控范围。★★**ISS-099 结构侧选型回执 (10-28)**: ① **390Ω 档保留**, 但两道保险写死: **(a) 选型判据收紧到 单触点额定 ≥0.5A** (Hirose FH12-10S-0.5SH(55) 满足: 0.5A/触点 · 0.5mm pitch · 座高 2.0mm) **且 (b) 工况写明『只有 pin1/pin2 载流, 其余 ≤1mA』** —— FH12 的 70% 降额条款只针对『全部触点同时导通』, 我们的工况不适用 ⇒ 0.411A/触点 余量 1.22×; ② **300Ω 档正式判死** (单 pin 0.534A > 任何 0.5mm pitch FPC ZIF 的 0.5A 额定天花板, 只能靠 1.0mm pitch 而铰链区装不下); ③ **J_CHG 实物是一对** (框侧座 + 脚侧座), 备料别只算一只; ④ **FPC 固定段 2oz (0.24-0.25mm) 可能超 FH12 可插厚度上限 0.23mm** → 已进 RFQ 硬判据"
        "★真正的热源是**电芯内阻** (0.10Ω · 114mW @1.07A) 而非铰链段 (110.8mW) —— 电芯直接贴皮肤侧; "
        "★★**V1.9 (2026-10-28) 产品语义已定**: 老板 10-28 拍板『**边戴边充不允许**』⇒ 充电时眼镜不在皮肤上 ⇒ "
        "皮肤温度不再是充电时的硬约束 ⇒ **定为 390Ω (ICHG 0.82A / 单 pin 0.411A / 充电 ~29min)**; "
        "300Ω 档正式判死 (单 pin 0.534A > 0.5mm pitch ZIF 的 0.5A 触点天花板); "
        "★注意: 390Ω 档保守口径皮肤侧仍 42.14°C (距 43°C 红线只剩 0.86°C) ⇒ **不能再抬电流**, 余量在电芯侧不在皮肤侧", "C-01")
    add("P1", "GND", "R_ILIM", "GND", "R_ILIM", "390Ω ±1% (IINMAX ≈1.00A · ICHG ≈0.82A · 单 pin 0.411A)", "R", "必装",
        "[官方]", "",
        "[IINLIM] 限流电阻 另一端接地 (IINLIM 对地设定输入电流上限)")

    # ---- ★V1.8 (2026-10-28): 硬件断电通路 + 复位链闭环 (老板拍板关机=断电; ISS-096/098 项目总工接手) ----
    #   ★网表规范 (V1.8 明确): **一行 = 一根导线 = 两个同网的器件脚** ⇒ 每个 2 脚器件必须出现在 **2 行** (一脚一行),
    #   3 脚器件 (MOS) 出现 3 行 (G/D/S 各一行)。违反这条 = 导出 .net 时该脚悬空 (门禁 "两脚件恰好 2 脚" 就是判这个)。
    #   断电拓扑 (为何不用 SR 锁存): ON 脚 **10k 下拉 = 默认关**; SoC GPIO 拉高 = 保持开机;
    #   SoC 关机时把该 GPIO 配成高阻 · ON 掉回下拉 · 开关关 · SoC 断电 · **状态自动保持** (无需自保持电路)
    #   "插电即开机": BQ25896 的 PG (开漏, LOW=输入源良好) 经 Q_PG 驱动 · **★V1.9 P0 修正: Q_PG 必须是 P-MOS 高边开关**
    #   ⚠️ **原 V1.8 用 N-MOS 低边反相是错的 (2026-10-28 hw-lead 查出, 项目总工独立复核确认)**:
    #      原接法 = 栅极接 PG · 源极接 GND · 漏极接 ON ⇒ PG 低 (电源良好) 时 N-MOS **关** ⇒ ON 只剩 10k 下拉 = 低 = **开关关**
    #      ⇒ ① 插电 (PG 低) 反而**开不了机**; ② SoC 拉高 PWR_CTRL 时若 Q_PG 导通会被**拉到 GND 拉不高** ⇒ **开机路径彻底不通**
    #   正解 (**零新增 pin · 零新增轨**, 2026-10-28 项目总工独立复核后定的):
    #      Q_PG 改 **P-MOS 高边开关** —— 源极接 ON · **漏极接 BAT_SW (电池轨, 关机后仍带电 3.0-4.2V)** · 栅极接 PG
    #      ⇒ PG 低 (良好) → 栅极≈0V → Vgs = 0 - V(BAT_SW) ≈ -4.2V → **P-MOS 导通** → ON = BAT_SW = 高 = **开机** ✔
    #      ⇒ PG 高 (无输入) → 栅极 3.3V → ON 被 10k 下拉到 0 → Vgs = +3.3V → **P-MOS 关** → ON 低 = **关** ✔
    #   ★**为什么漏极接 BAT_SW 而不是 3.3V**: 库内 3.3V 轨全部挂在 SYS 下 (U_LDO_IO33 输入 = RAIL_SYS),
    #      **关机断电后就没电** ⇒ 漏极无电位 ⇒ 插电开机不成立 ⇒ 必须用关机后仍带电的 BAT_SW (或 AON 轨, 待原厂确认)
    #   ★**选型硬判据** (写在 HW/POWER_SHUTDOWN_V3.md §2): 低漏 P-MOS · Vgs(th) 明确 · 栅极最大耐压 ±20V · 关断漏电 nA 级
    add("P1", "BAT_SW", "U_PWR_SW VIN", "U_BATPROT", "U_PWR_SW", "VIN (输入)", "NET", "必装",
        "[推算]", "",
        "[BAT_SW] 电池保护 (BQ2970 + 2×MOS) 引脚 · **负载开关输入**; ★V1.8: 开关装镜脚 (与电池/保护板同板); "
        "关机时充电链仍在电池侧带电 ⇒ 关机也能充电", "C-02")
    add("P1", "SYS", "U_PWR_SW VOUT", "RAIL_SYS", "U_PWR_SW",
        "[待选型] 负载开关 (≥2A, R_on ≤40mΩ@3.7V, IQ ≤5µA, 带反向阻断)", "IC", "必装",
        "[推算]", "",
        "[SYS] ★V1.8 硬件断电通路的主器件: VOUT · 镜脚系统轨 SYS (SoC + 2×DC-DC + 7×LDO + sensor + 光机 全在其下游); "
        "**反向阻断必查** (关机插 USB 时防 5V 经 SoC IO 反灌电池); 选型判据 8 条见 HW/POWER_SHUTDOWN_V3.md §2 (型号待选型, 询价经项目总工)", "C-02")
    add("P1", "GND", "U_PWR_SW GND", "GND", "U_PWR_SW", "地脚", "NET", "必装",
        "[推算]", "", "[SYS] 负载开关 地脚")
    add("P1", "BAT_SW", "C_SW_IN", "U_PWR_SW VIN", "C_SW_IN", "10µF ±20%", "C", "必装", "[推算]", "",
        "[BAT_SW] 开关输入端去耦 (紧贴 VIN; 另一端接地)", "C-02")
    add("P1", "GND", "C_SW_IN", "GND", "C_SW_IN", "10µF ±20%", "C", "必装", "[推算]", "",
        "[BAT_SW] 开关输入端去耦 的地端", "C-02")
    add("P1", "SYS", "C_SW_OUT", "U_PWR_SW VOUT", "C_SW_OUT", "10µF ±20%", "C", "必装", "[推算]", "",
        "[SYS] 开关引脚端去耦 (紧贴 VOUT, 承 SoC 上电冲击; 另一端接地)", "C-02")
    add("P1", "GND", "C_SW_OUT", "GND", "C_SW_OUT", "10µF ±20%", "C", "必装", "[推算]", "",
        "[SYS] 开关引脚端去耦 的地端", "C-02")
    add("P1", "PWR_ON", "R_PD_ON", "U_PWR_SW ON", "R_PD_ON", "10k ±1%", "R", "必装", "[推算]", "",
        "[PWR_ON] ★V1.8: ON 脚 **10k 下拉 = 默认关** (关机态就是默认态); SoC GPIO 拉高即保持开机; "
        "SoC 关机时把该 GPIO 配成高阻 · ON 掉回下拉 · 开关关 · SoC 断电 · 状态自动保持 (无需锁存电路)", "C-02")
    add("P1", "GND", "R_PD_ON", "GND", "R_PD_ON", "10k ±1%", "R", "必装", "[推算]", "",
        "[PWR_ON] ON 脚下拉的接地端", "C-02")
    add("P1", "PWR_ON", "U_PWR_SW ON", soc_pin("PWR_CTRL"), "U_PWR_SW", "ON 输入 (高电平 = 导通 = 开机)",
        "NET", "必装", "[推算]", "",
        "[PWR_ON] 负载开关 ON 节点 (高电平 = 开机); ★SoC 用这个 GPIO 保持开机 (推挽高) 或触发关机 (高阻), "
        "脚号与是否可配开漏**待原厂**", "C-02")
    add("P1", "PWR_ON", "Q_PG", "U_PWR_SW ON", "Q_PG", "[待选型] **P-MOS 高边开关** (低漏, Vgs(th) 明确)", "SW",
        "必装", "[推算]", "",
        "[PWR_ON] ★★**V1.9 P0 修正 (2026-10-28)**: Q_PG 由 N-MOS 改 **P-MOS 高边开关** —— "
        "原 N-MOS 低边接法是**错的**: 栅极接 PG(LOW=电源良好) · 源极接 GND · 漏极接 ON ⇒ "
        "PG 低时 MOS 关 ⇒ ON 只剩 10k 下拉 = 低 = **开关关** ⇒ ①插电反而开不了机 ②SoC 拉高 PWR_CTRL 会被 Q_PG 拉到 GND 拉不高 ⇒ **开机路径彻底不通**。"
        "★**正解 (零新增 pin · 零新增轨)**: 源极接 ON · **漏极接 BAT_SW (电池轨, 关机后仍带电)** · 栅极接 PG ⇒ "
        "PG 低(良好)→Vgs≈-4.2V→P-MOS 导通→ON=BAT_SW=高=**开机**; PG 高(无输入)→Vgs=+3.3V→P-MOS 关→ON 落下拉=低=**关** (关机态仍能充电)。"
        "★选型硬判据: 低漏 P-MOS · Vgs(th) 明确 · 栅极最大耐压 ±20V · 关断漏电 nA 级",
        "C-02")
    add("P1", "BAT_SW", "Q_PG", "NET_BAT_SW", "Q_PG", "[待选型] **P-MOS 高边开关** (低漏, Vgs(th) 明确)", "SW",
        "必装", "[推算]", "",
        "[PWR_ON] ★V1.9: Q_PG **漏极**接 **BAT_SW (电池轨 3.0-4.2V)** —— ★**不能用 3.3V 轨**: 库内 3.3V 全挂在 SYS 下 "
        "(U_LDO_IO33 输入 = RAIL_SYS), 关机断电后即灭 ⇒ 漏极无电位 ⇒ 插电开不了机。BAT_SW 在关机态仍带电 ✔",
        "C-02")
    add("P1", "PWR_GOOD", "Q_PG", "J_CHG pin6", "Q_PG", "[待选型] **P-MOS 高边开关** (低漏, Vgs(th) 明确)", "SW",
        "必装", "[推算]", "",
        "[PWR_GOOD] Q_PG **栅极** = 充电板 PG (经 J_CHG pin6 跨铰链, 框侧开漏信号; 主板侧 R_PU_PG 10k 上拉 3.3V)。"
        "★V1.9: PG 低(电源良好) → 栅极≈0 → P-MOS 导通 → ON 拉高 = 开机", "C-06")

    # ---- ★V1.8 复位链闭环 (ISS-096 接手: hw-lead 连续两轮 0 产出) ----
    #   ① 两路 DC-DC 的 PG 开漏并联 · PG_AND (任一路坏 · 高)
    #   ② Q_AND (N-MOS): 栅极 = PG_AND, 漏极 = RESET_N · **两路都好才允许释放复位** (硬件 AND, 不等原厂)
    #   ③ DC-DC 的 EN 脚补上: V_SOC_IO 由 PWR_ON 直接使能 (第一路); V_CORE 由 V_SOC_IO 的 PG 经 Q_ENVC 反相使能 (顺序链)
    #   ④ V_CORE **不单独监督** —— 它是 SoC 内部 DVFS 轨 (0.65-1.0V, 电压本来就变), 监督它没意义;
    #      该监督的是固定电压的 V_SOC_IO (U_SUPV 已在做) · 我原先"要监督 V_CORE"的担心不成立
    add("P8", "PG_AND", "R_PG_PULL", "U_DCDC_VCORE PG", "R_PG_PULL", "10k ±1%", "R", "必装",
        "[推算]", "TBD-12",
        "[PG_AND] ★V1.8 复位链 ①: 两路 DC-DC 的 **PG 开漏信号直接并联** (任一路不 ok · 本网被上拉拉高); "
        "PG 极性 (ok=低/高) **待原厂核** (TPS62130A) —— 画法按最通用的『开漏 + 上拉』, 极性反了只需改 Q_AND 接法", "B-10")
    add("P8", "VDD_1V8_IO", "R_PG_PULL", "RAIL_VDD_1V8_IO", "R_PG_PULL", "10k ±1%", "R", "必装",
        "[推算]", "TBD-12",
        "[PG_AND] ★V1.8 复位链 ①: 并联后的上拉 (10k 挂常供电轨); 阻值偏大则 PG 上升沿慢 (跨铰链还要算分布电容)", "B-10")
    add("P8", "PG_AND", "U_DCDC_VIO PG", "U_DCDC_VCORE PG", "NET_PG_AND", "PG 开漏并联 (两路 DC-DC)",
        "NET", "必装", "[官方]", "TBD-12",
        "[PG_AND] ★V1.8 复位链 ①: 两路 DC-DC 的 PG 脚并到同一网 (开漏信号可以直接并联)", "B-10")
    add("P8", "RESET_N", "Q_AND", "NET_RESET_N", "Q_AND", "[待选型] N-MOS (硬件 AND)", "SW",
        "必装", "[推算]", "TBD-12",
        "[RESET_N] ★V1.8 复位链 ②: **Q_AND 把『两路 PG 都好』变成硬件许可** —— 漏极 = RESET_N; "
        "任一路 PG 坏 · PG_AND 高 · Q_AND 导通 · 拉住复位; 两路都好 · PG_AND 低 · Q_AND 关 · 允许释放 "
        "(与 U_SUPV 的开漏信号并联, 两路都放行才算复位释放) ⇒ **不依赖 TBD-12 也能定住上电时序**", "B-10")
    add("P8", "GND", "Q_AND", "GND", "Q_AND", "[待选型] N-MOS (硬件 AND)", "SW", "必装", "[推算]",
        "TBD-12", "[RESET_N] Q_AND 源极接地", "B-10")
    add("P8", "PG_AND", "Q_AND", "U_DCDC_VIO PG", "Q_AND", "[待选型] N-MOS (硬件 AND)", "SW",
        "必装", "[推算]", "TBD-12", "[PG_AND] Q_AND 栅极 = PG_AND (两路 PG 都好时为低 · Q_AND 关)", "B-10")
    add("P8", "EN_VCORE", "R_EN_VCORE", "RAIL_VDD_1V8_IO", "R_EN_VCORE", "10k ±1%", "R", "必装",
        "[推算]", "TBD-12",
        "[EN_VCORE] ★V1.8 复位链 ③: V_CORE 的 DC-DC **EN 脚上拉** (默认关) —— 由 V_SOC_IO 的 PG 经 Q_ENVC 反相驱动 "
        "⇒ 上电顺序 = V_SOC_IO 先起 · V_CORE 后起 (DVFS 轨最后)", "B-10")
    add("P8", "VDD_1V8_IO", "R_EN_VCORE", "RAIL_VDD_1V8_IO", "R_EN_VCORE", "10k ±1%", "R", "必装",
        "[推算]", "TBD-12", "[EN_VCORE] EN 上拉的另一端 (常供电轨)", "B-10")
    add("P8", "EN_VCORE", "U_DCDC_VCORE EN", "R_EN_VCORE", "U_DCDC_VCORE", "EN 输入 (高 = 使能)",
        "NET", "必装", "[待原厂]", "TBD-12",
        "[EN_VCORE] ★V1.8: V_CORE buck 的 EN 节点 (由 V_SOC_IO 的 PG 经 Q_ENVC 反相驱动)", "B-10")
    # ★★2026-11-03 订正: 两路 DC-DC 的 PG 已并联在 PG_AND (wired-AND) ⇒ Q_ENVC 的栅极也挂 PG_AND
    #   (原来挂 PG_VIO ⇒ **同一个物理脚 (U_DCDC_VIO PG) 挂两个网** ⇒ 板子上短路)
    add("P8", "PG_AND", "Q_ENVC", "U_DCDC_VIO PG", "Q_ENVC", "[待选型] N-MOS (反相)", "SW",
        "DNP", "[推算]", "TBD-12",
        "[PG_VIO] ★V1.8: V_SOC_IO 的 PG 有效 (低) · Q_ENVC 关 · EN_VCORE 被上拉为高 · V_CORE 使能 ⇒ **顺序链**; "
        "PG 极性**待原厂核** (TPS62130A PG 为开漏信号)", "B-10")
    add("P8", "GND", "Q_ENVC", "GND", "Q_ENVC", "[待选型] N-MOS (反相)", "SW", "必装", "[推算]",
        "TBD-12", "[PG_VIO] Q_ENVC 源极接地", "B-10")
    add("P8", "EN_VCORE", "Q_ENVC", "R_EN_VCORE", "Q_ENVC", "[待选型] N-MOS (反相)", "SW", "必装",
        "[推算]", "TBD-12", "[EN_VCORE] Q_ENVC 漏极 = EN_VCORE (把 EN 拉低 = 不使能)", "B-10")
    add("P8", "EN_VIO", "U_DCDC_VIO EN", "NET_PWR_ON", "U_DCDC_VIO", "EN 输入 (高 = 使能)",
        "NET", "必装", "[待原厂]", "TBD-12",
        "[EN_VIO] ★V1.8: V_SOC_IO buck 的 EN **直接由 PWR_ON 开机节点驱动** (它是上电第一路; "
        "PG 极性/EN 极性待原厂核)", "B-10")
    add("P8", "SUPV_CT", "U_SUPV CT", "RAIL_VDD_1V8_IO", "U_SUPV", "CT 脚 (阈值/延时选择)",
        "NET", "必装", "[待原厂]", "TBD-12",
        "[SUPV_CT] ★V1.8: 监督器 CT 脚原来**悬空** (网表里没有) · 补上 (阈值/延时选择, 脚号与接法待原厂核)", "B-10")

    # ---- ★V1.8 SoC 侧 USB VBUS 检测 (ISS-098 接手): VBUS_DET 分压在充电板, 经 J_CHG pin7 跨铰链 ----
    # ★★2026-11-04 19:5x 删: 跨铰链的 VBUS_DET (SoC ← J_CHG pin7) —— 与 demo 板本地分压重复
    #   (同一条 VBUS_DET 到 SoM 有两条路 ⇒ 冲突); demo 板的分压在 P1。
    #   (原行整条删除 —— 跨铰链 VBUS_DET 与 demo 板本地分压重复)
    # add("P6", "VBUS_DET", soc_pin("USB_VBUS_DET"), "J_CHG pin7", "SoC[RK3572]",
    #     "SoC USB VBUS 检测脚 (脚号待原厂)", "NET", "必装", "[待原厂]", "TBD-10",
    #     "[VBUS_DET] ★V1.8 补上 sw-lead 指出的缺件: **SoC 侧没有任何 USB VBUS 连接**", "B-07")

    # ---- ★V1.2 改: 原 V1.1 加的 "SYS 过铰链 π 滤波" **删掉** (SYS 已不过铰链) ----
    #   跨铰链的是**充电电流** · 充电路径上**不能加 π 滤波** (会破坏 BQ25896 环路稳定性)
    #   · 改为: 双 pin 并联载流 + 铰链段压降测点 + 载流核算 (见 P9 页)
    add("P1", "BAT_CHG", "J_CHG pin1", "TP_BAT_CHG", "TP_BAT_CHG", "跨铰链段压降测点", "TP",
        "必装", "[推算]", "",
        "[BAT_CHG] ★跨铰链充电电流段压降测点 (1.5A 下压降 = 接触电阻×1.5A); "
        "铰链段发热与压降按结构实际长度核算 (结构总工)", "C-02")

    # ---- 13 条电源轨 + 供电器件 + 去耦 ----
    rails = {r["rail"]: r for r in spec["power_rails"]}
    power_ics = [
        # ★★2026-11-03: **DNP** —— FET3572-C 是 SoM, **自带 PMIC** (P3_10 = PMIC_VDC) ⇒ V_CORE/V_SOC_IO
        #   由 SoM 内部产生 ⇒ 主板**不产** SoC 的核心/IO 轨 (这两路 DC-DC 是分立 SoC 时代的遗产)
        ("U_DCDC_VCORE", "V_CORE", "TPS62130A", "★**DNP** — SoM 自带 PMIC ⇒ 主板不产 SoC 核心轨", "DNP", "[官方]", "TBD-02", "C-04"),
        ("U_DCDC_VIO", "V_SOC_IO", "TPS62130A", "★**DNP** — SoM 自带 PMIC ⇒ 主板不产 SoC IO 轨", "DNP", "[官方]", "TBD-02", "C-05"),
        ("U_LDO_S28", "SENSOR_AVDD", "TPS7A20-28", "★**DNP** — camera 模组自带稳压 (pin28/29=3.3V, pin30/31=5V) ⇒ 主板不供 sensor 芯片级模拟轨", "DNP", "[官方]", "", "C-06"),
        ("U_LDO_S18B", "SENSOR_VDD_IO", "TPS7A20-18", "★**DNP** — camera 模组自带稳压 ⇒ 主板不供 sensor 芯片级 IO 轨", "DNP", "[官方]", "", "C-07"),
        ("U_LDO_S12", "SENSOR_CORE", "TPS7A20-12", "★**DNP** — camera 模组自带稳压 ⇒ 主板不供 sensor 芯片级数字轨", "DNP", "[官方]", "", "C-08"),
        ("U_LDO_L33", "LIGHT_3V3", "TPS7A20-33", "LDO 供 LIGHT_3V3 (3.3V/150mA)", "必装", "[推算]", "TBD-02", "C-09"),
        ("U_LDO_L18", "LIGHT_1V8", "TPS7A20-18", "LDO 供 LIGHT_1V8 (1.8V/50mA)", "DNP", "[推算]", "TBD-02", "C-10"),
        ("U_LDO_IO33", "VDD_3V3_IO", "TPS7A20-33", "LDO 供 VDD_3V3_IO (3.3V/200mA)", "必装", "[推算]", "", ""),
        ("U_LDO_IO18", "VDD_1V8_IO", "TPS7A20-18", "LDO 供 VDD_1V8_IO (1.8V/100mA)", "必装", "[推算]", "", ""),
    ]
    for ref, rail, part, desc, dnp, ev, tbd, cid in power_ics:
        r = rails.get(rail, {})
        _out_pin = pin_of(ref, "OUT") or pin_of(ref, "VOUT")
        add("P1", rail, f"RAIL_{rail}", f"{ref} pin{_out_pin}" if _out_pin else ref,
            f"RAIL_{rail}", r.get("volt", ""), "RAIL", dnp,
            ev, tbd,
            f"电源域: 目标 {r.get('volt','')} / 最大电流 {r.get('max_i','')}; IC {part}; "
            f"SoC 侧球位号 TBD-01", cid)
        # ★V1.1 补画 3: 输入侧连接 (V1 只画了供电器件与去耦, **没画 IC 输入脚接哪条轨** · ERC B1 "来源" 缺失)
        _in_pin = pin_of(ref, "IN") or pin_of(ref, "VIN")
        add("P1", "SYS_PCB", "RAIL_BOARD_5V", f"{ref} pin{_in_pin}" if _in_pin else f"{ref} VIN",
            "RAIL_BOARD_5V", "5.0V (F13: 由 CARRIER_BOARD_EN 门控)",
            "NET", dnp, "[推算]", "",
            f"[{rail}] {ref} 输入脚供电 (SYS 镜脚本地产生, 电池保护后); "
            f"LDO 输入下限 1.6V / DC-DC 输入 3-17V [官方]",
            cid)
        # ★★2026-11-02 20:3x ★★P0 修复: EN 脚必须显式画!
        #   依据: TPS7A20 datasheet —— EN 内部 500kΩ 下拉, 悬空 = LDO 关断 ("keeps the LDO disabled even
        #   when the EN pin is left floating"); VEN(LOW)≤0.3V 关断 / VEN(HIGH)≥0.9V 使能 (绝对值)。
        #   ★TPS62130A (DC-DC) 同样有 EN。⇒ 原网表 7 路 LDO + 2 路 DC-DC **全都没有 EN 网络**
        #   ⇒ 投板后 9 路全灭 = 整板不上电 = 2~4 周返工 ⇒ 现在改成本≈0 (BOM footprint 还全是"待定")。
        #   修法: **EN 直连 RAIL_SYS** (3.5-4.2V ≫ 0.9V ⇒ 永远使能, 零新增器件)
        #   ★★2026-11-02 20:3x 追加: **SENSOR_AVDD 也 DNP 了** (camera 模组自带稳压) ⇒ 三条 sensor 轨的 LDO 全不装
        #   ⇒ **现在在用的 TPS7A20 只剩 LIGHT_3V3 / LIGHT_1V8 / VDD_3V3_IO / VDD_1V8_IO 四颗** ⇒ 它们的 EN 全部显式接 RAIL_SYS
        #   ⇒ ★**CARRIER_BOARD_EN (SOM pin87) 的底板主电源使能属 A2 段 (SOM 座) 未接 ⇒ 段 B 处理
        if part.startswith("TPS7A20"):
            # ★★2026-11-03 按**原厂 datasheet** 重画 (TPS7A20 = X2SON / DQN0004A, **4 脚 + 散热焊盘**):
            #   ★真脚号: **1=OUT · 2=GND · 3=EN · 4=IN · 5=散热焊盘(接 GND)**
            #   ⇒ ★**之前只画了 IN/EN/OUT ⇒ GND 脚与散热焊盘整个是悬空的** ⇒ 现在补齐
            #   ⇒ EN 仍直连 RAIL_BOARD_5V (永远使能) —— 门限 VEN(LOW)≤0.3V 关断 / VEN(HIGH)≥0.9V 使能
            if ref != "U_LDO_S28":
                add("P1", "SYS_PCB", f"{ref} pin3", "RAIL_BOARD_5V", ref, "EN (pin3)", "NET", dnp,
                    "[官方]", "",
                    f"[{rail}] ★{ref} 的 EN 脚 (pin3) **直连 RAIL_BOARD_5V** ⇒ 永远使能 — "
                    "★★**P0: EN 内部 500kΩ 下拉, 悬空 = 关断 ⇒ 不画 EN = 投板后整板不上电**; "
                    "datasheet 门限 VEN(LOW)≤0.3V 关断 / VEN(HIGH)≥0.9V 使能", cid)
            # GND 脚 (pin2) + 散热焊盘 (pin5) ⇒ 原厂要求散热焊盘接 GND (散热 + 电气)
            add("P1", "GND", f"{ref} pin2", "GND", ref, "GND (pin2)", "NET", dnp, "[官方]", "",
                f"[{rail}] ★{ref} 的 GND 脚 (pin2) —— ★**之前网表里根本没画 GND ⇒ 悬空**", cid)
            add("P1", "GND", f"{ref} pin5", "GND", ref, "散热焊盘 (pin5, EP)", "NET", dnp, "[官方]", "",
                f"[{rail}] ★{ref} 的散热焊盘 (pin5, exposed pad) **必须接 GND** (原厂 X2SON 要求: "
                "既是散热通路也是 GND 回路)", cid)

        # ★V1.1 补画 4: 电压不确定性的吸收方式写进图纸 (ISS-082 前提修正)
        extra = ""
        if part.startswith("TPS7A20"):
            extra = ("; ★电压不确定性吸收: TPS7A20 **全部固定档共用 X2SON 封装** "
                     "[官方 ti.com/product/TPS7A20, 30 档覆盖 0.8-5.5V] · 原厂/JBD 回信后**换料不换板** "
                     "(7µVrms / PSRR 60dB 留给 sensor 轨, 噪声优先)")
        elif part.startswith("TPS62130A"):
            extra = ("; ★电压不确定性吸收: TPS62130A **引脚可选 (标称 ±5%)** [官方] · "
                     "原厂电压落在档内则**换料不换板** (VQFN-16 RGT); 落在档外则换同封装可调型号 "
                     "(改两颗反馈电阻), 仍不改板")
        add("P1", rail, f"RAIL_{rail}", ref, ref, part, "IC", dnp, ev, tbd,
            f"[{rail}] {desc}; 电压 {r.get('volt','—')} / 最大电流 {r.get('max_i','—')}; "
            f"选型依据 规格 power_rails[{rail}]{extra}", cid)
        # 去耦: 每条轨 1×10µF 体电容 + 1×100nF 高频电容 (标准 PDN 做法, 值最终随负载核)
        add("P1", rail, f"RAIL_{rail}", f"C_BULK_{rail}", f"C_BULK_{rail}", "10µF", "C", dnp,
            "[推算]", "",
            f"[{rail}] 体电容 (值随负载瞬态/原厂电源域表核, TBD-02)", cid)
        add("P1", "GND", f"C_BULK_{rail}", "GND", f"C_BULK_{rail}", "10µF", "C", dnp,
            "[推算]", "", f"[{rail}] 体电容 地端", cid)
        add("P1", rail, f"RAIL_{rail}", f"C_HF_{rail}", f"C_HF_{rail}", "100nF", "C", dnp,
            "[推算]", "", f"[{rail}] 高频去耦电容位 (紧贴 IC 引脚)", cid)
        add("P1", "GND", f"C_HF_{rail}", "GND", f"C_HF_{rail}", "100nF", "C", dnp,
            "[推算]", "", f"[{rail}] 高频去耦电容 地端", cid)

    # LIGHT_5V: 无独立 IC, 直接取 VBUS (规格 C-10 'VBUS 直供')
    add("P1", "LIGHT_5V", "RAIL_LIGHT_5V", "D_ESD_LIGHT", "D_ESD_LIGHT", "ESD 阵列 [待选型]", "D",
        "DNP", "[推算]", "",
        "[LIGHT_5V] 光机 5V 供电口 ESD 阵列位 (跨铰链, 随光机接口确认后定)", "C-10")
    add("P1", "GND", "D_ESD_LIGHT", "GND", "D_ESD_LIGHT", "ESD 阵列 [待选型]", "D",
        "DNP", "[推算]", "", "[LIGHT_5V] 光机侧 ESD 地端", "C-10")
    # ★V1.4: ESD 阵列的**地脚**补齐 (原来只有 I/O 脚, 阵列没接地 · 保护不生效)
    # ★2026-11-04 19:5x: D_ESD_USB (跨铰链 USB ESD) 已随跨铰链 USB 一起删除 ⇒ 不再补地脚
    for dref, note in (("D_ESD_TC", "Type-C 入口 ESD 阵列 地脚"),
                       ("D_ESD_CAM", "跨铰链 CSI ESD 阵列 地脚")):
        add("P9", "GND", dref, "GND", dref, "ESD 阵列 [待选型]", "D", "必装", "[推算]", "",
            f"[GND] ★V1.4 补: {note} (原来只有 I/O 脚, 阵列没接地 · ESD 不工作)")
    # GND 轨 (机壳地 / 数字地, 单点汇流)
    add("P1", "GND", "RAIL_GND", "GND", "RAIL_GND", "机壳地 / 数字地 (单点汇流)", "RAIL",
        "必装", "[推算]", "",
        "电源域: 目标 — / 最大电流 —; 单点汇流位置由结构总工定 (ISS-065); SoC 侧球位号 TBD-01",
        "C-11")
    add("P1", "GND", "RAIL_GND", "CHG_GND_STAR", "CHG_GND_STAR", "单点汇流位", "CONN",
        "必装", "[推算]", "",
        "[GND] 充电板↔主 PCB 的地单点汇流位 (结构总工定位置, ISS-065)", "C-11")
    add("P1", "GND", "CHG_GND_STAR", "GND", "CHG_GND_STAR", "单点汇流位", "CONN",
        "必装", "[推算]", "", "[GND] 汇流位 接主板数字地 (与机壳地分开)", "C-11")


# ------------------------------------------------- 规格连接 · NET 行 (共用)
def conn_row(by_id, cid, page, net, n1, n2, ref, value=None, note_extra=""):
    """把规格里的一条连接展开成 netlist 的 NET 行。
    value 默认取规格 imp (A 组阻抗必须与规格逐字一致 · check_netlist 判据 5)。"""
    c = by_id[cid]
    v = value if value is not None else (c.get("imp") or c.get("level") or "")
    ev = ev_of(c.get("level") or c.get("volt") or "", "[推算]")
    tbd = tbd_for((c.get("signal") or "") + " " + (c.get("conn") or ""))
    note = (f"方向 {c.get('dir','')}; 电平 {c.get('level','')}; 阻抗 {c.get('imp','')}; "
            f"连接 {c.get('conn','')}; 测试点 {c.get('tp','')}")
    if note_extra:
        note = f"[{net}] {note_extra}; " + note
    add(page, net, n1, n2, ref, v, "NET", dnp_of(c.get("dnp", "")), ev, tbd, note, cid)


# ---------------------------------------------------------------- P2 SoC 主控
def build_p2(by_id, spec):
    # ---- I2C_A (总线 A: sensor / NTC / 桥接 / 充电 IC) ----
    conn_row(by_id, "B-01", "P2", "I2C_A_SCL", soc_pin("I2C_A_SCL"), "R_PU_I2CA_SCL",
             "NET_I2C_A_SCL")
    conn_row(by_id, "B-02", "P2", "I2C_A_SDA", soc_pin("I2C_A_SDA"), "R_PU_I2CA_SDA",
             "NET_I2C_A_SDA")
    # ★★2026-11-03 订正: 相机 SCCB 走 **I2C5 (RK3572 上是 1.8V 域)** ⇒ 上拉必须到 **1.8V**
    #   (旧写法拉到 3.3V ⇒ **SoM 的 1.8V 脚被灌 3.3V** ⇒ 过压)
    add("P2", "VDD_1V8_IO", "R_PU_I2CA_SCL", "RAIL_VDD_1V8_IO", "R_PU_I2CA_SCL", "2.2k ±1%",
        "R", "必装", "[推算]", "",
        "[VDD_1V8_IO] I2C_A 上拉 (★★11-04 ISS-153 订正: **实际 net = RAIL_VDD_1V8_IO (1.8V 域)**; ★**旧注释写的『[VDD_3V3_IO] / 3.3V 上拉』与网表相反, 已作废**; 依据 ①: RK3572 的 I2C5 = J_SOM_P2 pin31/pin33 属**1.8V 域** (HW/PCB/FET3572C_PIN_TABLE.csv P2_31/P2_33 电压域列 = 1.8V) ⇒ 3.3V 上拉会把 SoM 的 1.8V 脚灌 3.3V = 过压; 依据 ②: camera 模组的 I2C 挂 OVDD **1.8V 域** (IMX415: VI ≤ OVDD+0.3V); 阻值 2.2k 仍成立 (1.8V 域复算: VOL(max)=0.4V, IOL(max)=3mA ⇒ R≥(1.8-0.4)/3mA=467Ω ⇒ 取 2.2k; 灌流 (1.8-0.4)/2.2k=0.64mA ≤3mA ✔; t_r=2.2k×100pF×0.847≈186ns ✔) — ★[TBD-05] 整机阶段若换 AR0234CS (VDD_IO=2.8V ⇒ VIH=0.7×2.8=1.96V > 1.8V 上拉 ⇒ **上拉轨必须一起改**, 并逐个核同总线从设备电平兼容 (TMP117 1.7-5.5V ✔ / 光机), **待 onsemi 回信 (ISS-142)**)", "B-01")
    add("P2", "VDD_1V8_IO", "R_PU_I2CA_SDA", "RAIL_VDD_1V8_IO", "R_PU_I2CA_SDA", "2.2k ±1%",
        "R", "必装", "[推算]", "",
        "[VDD_1V8_IO] I2C_A 上拉 (★同 SCL: 实际 net = RAIL_VDD_1V8_IO, **1.8V 域** —— RK3572 I2C5 1.8V 域 + camera 模组 OVDD 1.8V 域)", "B-02")
    add("P2", "I2C_A_SCL", "CONN_CAM pin24", "NET_I2C_A_SCL", "NET_I2C_A_SCL",
        "上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, ★camera FPC 标 I2C5 = 1.8V 域)", "NET", "必装", "[推算]", "",
        "[I2C_A_SCL] 附加节点 (同 net) · ★**camera 模组 (IMX415) I2C 地址 0x1a** (Sony IMX415-AAQR-C datasheet p.26 SLAVE Address 表: SLAMODE1/0 = Low/Low ⇒ 0x1A; 全表见 HW/I2C_ADDR_TABLE.md)", "B-01")
    add("P2", "I2C_A_SDA", "CONN_CAM pin25", "NET_I2C_A_SDA", "NET_I2C_A_SDA",
        "上拉 2.2k 到 1.8V (RAIL_VDD_1V8_IO, ★camera FPC 标 I2C5 = 1.8V 域)", "NET", "必装", "[推算]", "",
        "[I2C_A_SDA] 附加节点 (同 net) · ★**camera 模组 (IMX415) I2C 地址 0x1a** (Sony IMX415-AAQR-C datasheet p.26 SLAVE Address 表: SLAMODE1/0 = Low/Low ⇒ 0x1A; 全表见 HW/I2C_ADDR_TABLE.md)", "B-02")
    # NTC / 温度检测位: 规格 B-01 把 "NTC" 挂在 I2C_A 上, 但没说是裸 NTC 分压还是数字温度计
    # ★V1.1 定型 (ISS-086): 规格 B-01 的 "NTC 挂 I2C" 只能是**数字温度计** (裸 NTC 是分压不是 I2C)
    # ★★2026-11-04 04:0x: U_TEMP 改成**官方 6 脚 WSON-6 (DRV0006B)** —— TI TMP117 datasheet §5 Table 5-1:
    #   1=SCL  2=GND  3=ALERT  4=ADD0  5=V+  6=SDA   (★原来的 4 脚写法与原厂脚号完全对不上)
    add("P2", "I2C_B_SCL", "U_TEMP pin1", "NET_I2C_B_SCL", "U_TEMP",
        "TMP117 数字温度计 (I2C 地址 0x48, ±0.1°C max, 16bit)", "IC", "必装", "[官方]", "",
        "[I2C_B_SCL] ★TMP117 **pin1 = SCL** (TI SNOSD82D **Table 5-1 'Pin Functions' (p.4)**: 1=SCL 2=GND 3=ALERT 4=ADD0 5=V+ 6=SDA); "
        "★V1.1 定型: TI TMP117 [官方 ti.com/product/TMP117] (1.7-5.5V 供电, 5µA max, WSON-6 2×2mm); "
        "★**I2C 地址 0x48** (TI SNOSD82D **§7.5.3.1.2 + Table 7-2 'Address Pin and Slave Addresses' (p.21)**: 地址字节 1001000x = 0x48 ⇔ **ADD0 接 GND**; 本板 ADD0(pin4) 接地 ⇒ 地址锁死 0x48), "
        "★**11-04 ISS-153 订正**: sensor 地址随换料变 —— IMX415 = **0x1a** (Sony IMX415-AAQR-C datasheet p.26 'SLAVE Address' 表: SLAMODE1/0=Low/Low ⇒ 0x1A) / AR0234CS = **0x10** (onsemi AR0234CS datasheet p.10: 默认写 0x20/读 0x21 ⇒ 7-bit 0x10; SADDR 拉高 ⇒ 0x18) / "
        "桥接 —— **已删除** (随 RK3572 无 DP TX 整条删除, 不在本板) / 充电 IC = **0x6b** (TI BQ25896 datasheet §9.4 'I2C Slave Address: 6BH'; ★但它在 CHG_BOARD 本地自闭环 I2C_CHG_SCL/SDA, **不在本板任何 I2C 总线上** —— 跨铰链的只有 STAT/PG 两根 GPIO) / 光机 0x72 (0数据, 待 JBD 确认; A/B 两条都预留) —— ★**地址全表见 HW/I2C_ADDR_TABLE.md**", "B-01")
    add("P2", "I2C_B_SDA", "U_TEMP pin6", "NET_I2C_B_SDA", "U_TEMP",
        "TMP117 数字温度计", "IC", "必装", "[官方]", "", "[I2C_B_SDA] TMP117 **pin6 = SDA**", "B-01")
    add("P2", "VDD_3V3_IO", "U_TEMP pin5", "RAIL_VDD_3V3_IO", "U_TEMP",
        "TMP117 数字温度计", "IC", "必装", "[官方]", "", "[VDD_3V3_IO] TMP117 **pin5 = V+** (1.7-5.5V)",
        "B-01")
    add("P2", "GND", "U_TEMP pin2", "GND", "U_TEMP", "TMP117 数字温度计", "IC", "必装",
        "[官方]", "", "[GND] TMP117 **pin2 = GND**", "B-01")
    # ★ADD0 (pin4) = 地址选择脚 ⇒ 必须接死 ⇒ 接 GND ⇒ 地址 0x48 (与上面口径一致)
    add("P2", "GND", "U_TEMP pin4", "GND", "U_TEMP", "TMP117 ADD0 (地址选择)", "IC", "必装",
        "[官方]", "", "[GND] TMP117 **pin4 = ADD0** ⇒ 地址选择脚, 原厂: 接 GND/V+/SDA/SCL 之一; "
        "★本设计接 **GND ⇒ 地址 0x48** (与网表/软件口径一致)", "B-01")
    # ★ALERT (pin3) = 开漏输出 (过温/数据就绪告警) ⇒ demo 不接 (原厂允许悬空; 需告警再占一个 SoM 脚)
    add("P2", "NC_U_TEMP_ALERT", "U_TEMP pin3", "NC_U_TEMP_ALERT", "U_TEMP", "TMP117 ALERT (开漏输出, 未接)",
        "IC", "必装", "[官方]", "", "[NC_U_TEMP_ALERT] TMP117 **pin3 = ALERT** (开漏输出, 需上拉) "
        "⇒ ★demo 悬空 (原厂: 可接 GND 或悬空); ★若要过温告警上报 ⇒ 需另占一个 SoM GPIO + 4.7k 上拉", "B-01")
    add("P2", "VDD_3V3_IO", "C_TEMP", "RAIL_VDD_3V3_IO", "C_TEMP", "100nF ±10%", "C", "必装",
        "[推算]", "", "[I2C_A_SCL] TMP117 就近去耦", "B-01")
    add("P2", "GND", "C_TEMP", "GND", "C_TEMP", "100nF ±10%", "C", "必装", "[推算]", "",
        "[I2C_A_SCL] TMP117 去耦 地端", "B-01")

    # ---- BAT_DET (分压 + RC 到 ADC) · VBUS_DET 已改走 A2 段的板载分压 → USB_DRD1_VBUSDET ----
    #   ★★2026-11-03: VBUS_DET (B-07) 不再走"跨铰链 → ADC"那条路 —— demo 板自带 Type-C,
    #   VBUS 检测在**主板本地**分压后直接进 SoM 的 **USB_DRD1_VBUSDET (P1_100)** (专用数字输入)
    for cid, src, srcnode, tp, cap in (
            ("B-08", "BAT_DET", "RAIL_BAT", "TP_BAT", "C_DET_BAT"),):
        r1 = f"R_{src}_1"
        r2 = f"R_{src}_2"
        conn_row(by_id, cid, "P2", src, r1, r2, f"NET_{src}")
        add("P2", f"{src}_RAW", srcnode, r1, r1, "1M ±1%", "R", "必装", "[推算]", "",
            f"[{src}_RAW] 分压上臂 (1M); 上臂阻值大 · 漏电流 ~1.65µA @5V", cid)
        add("P2", src, r2, "GND", r2, "1M ±1%", "R", "必装", "[推算]", "",
            f"[{src}] 分压下臂 地端", cid)
        add("P2", src, cap, "J_CHG pin7" if cid == "B-07" else "R_BAT_DET_2", cap, "100nF ±10%",
            "C", "必装", "[推算]", "",
            f"[{src}] ADC 滤波电容 ({'跨铰链侧 (充电板测 VBUS, 高阻分压)' if cid == 'B-07' else '★V1.2: 电池在镜脚, 本地检测, 不跨铰链'})",
            cid)
        add("P2", "GND", cap, "GND", cap, "100nF ±10%", "C", "必装", "[推算]", "",
            f"[{src}] ADC 滤波电容 地端", cid)
        add("P2", src, soc_pin(src), f"NET_{src}", f"NET_{src}",
            by_id[cid].get("imp", ""), "NET", "必装", "[推算]", "",
            f"[{src}] SoC ADC 输入节点 (跨板那一侧)", cid)

    # ---- 充电状态回读 (BQ25896 STAT / PG, 开漏) ----
    for cid, sig, pin, rpu in (("B-05", "CHG_STAT", "J_CHG pin5", "R_PU_CHG_STAT"),
                               ("B-06", "PWR_GOOD", "J_CHG pin6", "R_PU_PG")):
        conn_row(by_id, cid, "P2", sig, "U_CHG", rpu, f"NET_{sig}")
        add("P2", "VDD_3V3_IO", rpu, "RAIL_VDD_3V3_IO", rpu, "10k ±1%",
            "R", "必装", "[推算]", "",
            f"[VDD_3V3_IO] {sig} 开漏上拉 (BQ25896 状态脚)", cid)
        add("P2", sig, pin, f"NET_{sig}", f"NET_{sig}", "单端", "NET", "必装", "[推算]", "",
            f"[{sig}] 附加节点 (同 net, 经 J_CHG 到主 PCB)", cid)

    # ---- ID_DETECT (2 位板级编码, 焊盘跳线) ----
    for bit, cid in (("0", "B-24"), ("1", "B-24")):
        conn_row(by_id, cid, "P7", f"ID_DETECT_{bit}", soc_pin(f"ID{bit}"),
                 f"R_PU_ID{bit}", f"NET_ID_DETECT_{bit}")
        add("P7", f"ID_DETECT_{bit}", f"R_ID_JMP{bit}", f"NET_ID_DETECT_{bit}", f"R_ID_JMP{bit}",
            "0Ω (跳线位)", "R", "DNP", "[推算]", "",
            f"[ID_DETECT_{bit}] 板级 ID 位 {bit} 跳线位 (焊盘跳线编码 2 位)", cid)
        add("P7", "VDD_3V3_IO", f"R_PU_ID{bit}", "RAIL_VDD_3V3_IO", f"R_PU_ID{bit}", "10k ±1%",
            "R", "必装", "[推算]", "",
            f"[VDD_3V3_IO] 板级 ID 位 {bit} 上拉", cid)
        add("P7", "GND", f"R_ID_JMP{bit}", "GND", f"R_ID_JMP{bit}", "0Ω (跳线位)", "R",
            "DNP", "[推算]", "", f"ID 跳线位 {bit} -> GND (装上 = 该位 0)", cid)


# ------------------------------------------------------------ P3 启动存储
def build_p3(by_id, spec):
    """只留焊盘位 + 串阻位, **不画存储芯片** (内置 DRAM 已确认, 但启动介质形态待原厂 Q19)"""
    spi = (("SPI_SCLK", "TBD-06", "J_BOOT1 pin1"), ("SPI_CSn", "TBD-06", "J_BOOT1 pin2"),
           ("SPI_MOSI", "TBD-11", "J_BOOT1 pin3"), ("SPI_MISO", "TBD-11", "J_BOOT1 pin4"))
    boot_note = ("启动存储: **只留焊盘位 + 串阻位, 不画存储芯片** (内置 boot storage 还是外挂 "
                 "SPI-NOR/eMMC 未确认; 外挂 eMMC 方案 PCB 面积 +25% 且板宽 12->15mm)")
    for sig, tbd, pin in spi:
        add("P3", sig, soc_pin(sig), f"R_SER_{sig}", f"NET_{sig}", "0Ω (串阻位)",
            "NET", "必装", "[待原厂]", tbd, boot_note, "")
        add("P3", f"{sig}_BOOT", f"R_SER_{sig}", pin, f"R_SER_{sig}", "0Ω (串阻位)",
            "R", "必装", "[待原厂]", tbd, f"[{sig}_BOOT] {sig} 串阻位 (0Ω 调试用)", "")
    add("P3", "VDD_3V3_IO", "J_BOOT1 pin5", "RAIL_VDD_3V3_IO", "J_BOOT1",
        "启动存储焊盘位 (4p 信号 + 2p 电源/GND 预留)", "CONN", "必装", "[待原厂]", "TBD-06",
        "[VDD_3V3_IO] ★内置 boot storage 还是外挂 SPI-NOR/eMMC 未确认 (Q19) -> 只留焊盘位; "
        "pin5/pin6 预留外挂 SPI-NOR 的 3V3/GND; ★V1.1: 容量下限已由 SW 总工锁死 (ISS-080): "
        "rootfs ≤30MB · **flash ≥128MB** (64MB SPI-NOR 装不下) · 回原厂答复后选 ≥128MB 的 SPI-NOR "
        "或 eMMC; 供电走 VDD_3V3_IO (200mA 够写入电流)", "")
    add("P3", "GND", "J_BOOT1 pin6", "GND", "J_BOOT1",
        "启动存储焊盘位 (4p 信号 + 2p 电源/GND 预留)", "CONN", "必装", "[待原厂]", "TBD-06",
        "焊盘位 GND 预留 (外挂 SPI-NOR 用)", "")


# ------------------------------------------------------- P4 显示双出口
# ★规格的 display_select 每条 lane 只给了**一颗** 0Ω (R_SEL_CK / R_SEL_D0 / ...) ——
#   那是**逻辑位**; 物理上一颗 0Ω 串在差分对上会把 P/N 短接 · 必须拆成 _P / _N 两颗。
DSI_LANES = [
    # lane, net_P, net_N, cid_P, cid_N, src_P, src_N, pin_P, pin_N, sel_dnp, 有对地端接
    # ★★2026-11-04: 板侧座 = **Pi5 22p/0.5mm DISPLAY 座** (针序照 Pi5 官方原理图 J4, 逐针)
    #   CK = pin5/6 · D0 = pin8/9 · D1 = pin2/3 · D2 = pin16/17 · D3 = pin18/19
    #   ★16..19 在 Pi5 上是 NC ⇒ 本板自用 (承载 lane2/lane3 ⇒ 主板→屏段 4-lane)
    #   依据: HW/PCB/PI5_DSI_22P_PINOUT.md
    ("CK", "DSI_D0_CK_P", "DSI_D0_CK_N", "A-13", "A-14",
     "DSI_TX_CK_P", "DSI_TX_CK_N", 6, 5, "必装", False),        # Pi5 DISPLAY: pin6=DSI1_CP / pin5=DSI1_CN
    ("D0", "DSI_D0_D0_P", "DSI_D0_D0_N", "A-15", "A-16",
     "DSI_TX_D0_P", "DSI_TX_D0_N", 9, 8, "必装", False),        # Pi5 DISPLAY: pin9=DSI1_DP0 / pin8=DSI1_DN0
    ("D1", "DSI_D0_D1_P", "DSI_D0_D1_N", "A-17", "A-18",
     "DSI_TX_D1_P", "DSI_TX_D1_N", 3, 2, "必装", False),        # Pi5 DISPLAY: pin3=DSI1_DP1 / pin2=DSI1_DN1
    ("D2", "DSI_D0_D2_P", "DSI_D0_D2_N", "A-19", "A-20",
     "DSI_TX_D2_P", "DSI_TX_D2_N", 17, 16, "必装", False),      # ★自用脚 (Pi5 侧 NC): lane2
    ("D3", "DSI_D0_D3_P", "DSI_D0_D3_N", "A-21", "A-22",
     "DSI_TX_D3_P", "DSI_TX_D3_N", 19, 18, "必装", False),      # ★自用脚 (Pi5 侧 NC): lane3
]
# ★★2026-11-02 01:0x 老板换主控 RK3572 ⇒ **RK3572 无 DP TX** ⇒ 方案B (DP→DSI 桥接) **不可能成立**
#   ⇒ BR_LANES 常量与全部方案B 器件行 (U_BRIDGE + 12 颗 0Ω 桥接位 + 8 颗 DP 串阻 + 8 颗对地电容)
#   **整条删除** ⇒ 板面积/BOM/位号同时受益 (约 29 个位号消失)。
#   ⇒ 显示链从此只有一条路: SoC 原生 MIPI-DSI → CONN_LIGHT → 光机/面板 (无桥接芯片)。


def build_p4(by_id, spec):
    for lane, netP, netN, cidP, cidN, srcP, srcN, pinP, pinN, sel_dnp, term in DSI_LANES:
        for pol, net, cid, src, pin in (("P", netP, cidP, srcP, pinP), ("N", netN, cidN, srcN, pinN)):
            rsel = f"R_SEL_{lane}_{pol}"
            conn_row(by_id, cid, "P4", f"{net}_SRC", soc_pin(src), rsel, f"NET_{net}_SRC")
            add("P4", net, rsel, f"CONN_LIGHT pin{pin}", rsel, "0Ω", "R", sel_dnp, "[官方]",
                "TBD-04",
                (f"[{net}] DSI 直通位 (SoC 原生 DSI → 光机; ★方案B 已随 RK3572 删除, 此位是**唯一通路**) — ★规格位 R_SEL_* 必须拆 "
                 f"P/N 两颗, 单颗 0Ω 会把差分对短接") if sel_dnp == "必装" else
                (f"[{net}] ★★4-lane 常开 (老板 11-04 01:42 拍板: 主板→屏段走 4-lane) — ★规格位 R_SEL_* 必须拆 P/N 两颗, "
                 f"单颗 0Ω 会把差分对短接"))
            if term:
                rt = f"R_TERM_{net}"
                add("P4", f"{net}_SRC", rt, f"NET_{net}_SRC", rt, "100Ω ±1%", "R", "DNP",
                    "[推算]", "",
                    f"[{net}_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装)")
                add("P4", "GND", rt, "GND", rt, "100Ω ±1%", "R", "DNP", "[推算]", "",
                    f"未用差分对 100Ω 对地端接 ({lane}_{pol} 才装)")
    # ★★方案B 桥接位已整条删除 (RK3572 无 DP TX) —— 见上面 BR_LANES 处的说明。
    # ⇒ R_SEL_* 现在是**唯一通路** (不再是"方案A/方案B 二选一") ⇒ note 已同步改写。
    # ---- DSI DDC (I2C_B) ----
    conn_row(by_id, "B-03", "P4", "I2C_B_SCL", soc_pin("I2C_B_SCL"), "R_PU_I2CB_SCL",
             "NET_I2C_B_SCL")
    conn_row(by_id, "B-04", "P4", "I2C_B_SDA", soc_pin("I2C_B_SDA"), "R_PU_I2CB_SDA",
             "NET_I2C_B_SDA")
    add("P4", "I2C_B_SCL", "R_PU_I2CB_SCL", "NET_I2C_B_SCL", "NET_I2C_B_SCL",
        "上拉 4.7k, 放主板侧", "NET", "必装", "[推算]", "TBD-04",
        "[I2C_B_SCL] ★★2026-11-04 订正: I2C_B **不是触控线**, 而是**屏的控制总线** (模组内 MCU @0x45; 树莓派驱动实测 probe 0xC0/0xC2/0xAC · enable 0xAD=0x01 · 背光 0xAB/0xAA) ⇒ ★**必须接**, 否则屏点不亮且无法调光", "B-03")
    add("P4", "I2C_B_SDA", "R_PU_I2CB_SDA", "NET_I2C_B_SDA", "NET_I2C_B_SDA",
        "上拉 4.7k, 放主板侧", "NET", "必装", "[推算]", "TBD-04",
        "[I2C_B_SDA] ★★2026-11-04 订正: 屏的控制总线 (模组内 MCU @0x45) ⇒ **必须接** (它不是触控线)", "B-04")
    add("P4", "VDD_3V3_IO", "R_PU_I2CB_SCL", "RAIL_VDD_3V3_IO", "R_PU_I2CB_SCL", "4.7k ±1%",
        "R", "必装", "[推算]", "", "[VDD_3V3_IO] DSI DDC 上拉 (放主板侧)", "B-03")
    add("P4", "VDD_3V3_IO", "R_PU_I2CB_SDA", "RAIL_VDD_3V3_IO", "R_PU_I2CB_SDA", "4.7k ±1%",
        "R", "必装", "[推算]", "", "[VDD_3V3_IO] DSI DDC 上拉", "B-04")
    # ---- 显示 FPC 座 (板内, 屏幕模组 ↔ 主板) ----
    # ★★2026-11-04 定稿: **Pi5 22p/0.5mm (HIROSE FH12-22S-0.5SH(55))**
    #   依据链: ① Raspberry Pi 官方 Pi 5 原理图 J4 (DISPLAY 座) 逐脚网名
    #           ② Waveshare 官方 wiki 『2.8inch DSI LCD』屏侧 15p 表 (逐脚与 ① 一致)
    #           ③ Raspberry Pi 官方 CM4IO/CM5IO KiCad 里的 FH12-22S 封装 (机械/land pattern)
    #   ★★**针序必须照 Pi5 DISPLAY 座抄** —— CM5IO 那套 22p (2/3=D0, 5/6=D1, 8/9=CLK, 20/21=I2C) 与之**不同**
    add("P4", "CONN_LIGHT", "CONN_LIGHT", "CONN_LIGHT", "CONN_LIGHT",
        "★22p@0.5mm (HIROSE FH12-22S-0.5SH(55), 右角/底接触/1固定柱; 官方封装抄 RPi CM5IO)",
        "CONN", "必装", "[官方]", "",
        "[CONN_LIGHT] ★2026-11-04 定稿: 板内 FPC 座 22p/0.5mm, 针序照 **Raspberry Pi 5 官方 DISPLAY 座 (J4)**: "
        "1=GND 2=DSI1_DN1 3=DSI1_DP1 4=GND 5=DSI1_CN 6=DSI1_CP 7=GND 8=DSI1_DN0 9=DSI1_DP0 10=GND "
        "11=SCL0 12=SDA0 13=GND 14=3V3 15=3V3; ★16..22 在 Pi5 上是 NC ⇒ 本板自用 (lane2/lane3 + 预留地). "
        "★配套线: Waveshare 『DSI Cable-12cm』22p↔15p; ★详见 HW/PCB/PI5_DSI_22P_PINOUT.md")

    # --- 22p 座逐脚 (Pi5 DISPLAY 座口径) ---
    _light_gnd = [1, 4, 7, 10, 13, 20, 21, 22]
    for _pn in _light_gnd:
        add("P4", "GND", f"CONN_LIGHT pin{_pn}", "GND", "CONN_LIGHT", "GND", "NET", "必装", "[官方]", "",
            f"[CONN_LIGHT] Pi5 DISPLAY 座 pin{_pn} = GND"
            + (" (★16..22 在 Pi5 上是 NC ⇒ 本板自用, 这里当预留地)" if _pn >= 20 else ""), "")
    for _pn in (14, 15):
        add("P4", "LIGHT_3V3", f"CONN_LIGHT pin{_pn}", "RAIL_LIGHT_3V3", "CONN_LIGHT", "3.3V", "NET",
            "必装", "[官方]", "",
            f"[CONN_LIGHT] Pi5 DISPLAY 座 pin{_pn} = 3V3 (★屏侧 15p 的 14/15 都是 3V3)", "")
    # ★★屏控制 I2C (不是触控!) —— Pi5 DISPLAY 座 pin11 = SCL0 / pin12 = SDA0
    #   ★I2C_B 上拉已在 VDD_3V3_IO (3.3V) ⇒ 与屏内 MCU 的 3.3V I2C 同域 ⇒ 不需要电平转换
    add("P4", "I2C_B_SCL", "CONN_LIGHT pin11", "NET_I2C_B_SCL", "NET_I2C_B_SCL",
        "I2C_B_SCL", "NET", "必装", "[官方]", "",
        "[I2C_B_SCL] ★Pi5 DISPLAY 座 pin11 = SCL0 ⇒ **屏控制 I2C** (屏内 MCU @0x45; 树莓派驱动实测 probe 0xC0/0xC2/0xAC · enable 0xAD=0x01 · 背光 0xAB/0xAA) ⇒ **必须接**, 否则屏不亮也无法调光; "
        "★**屏模组内 MCU I2C 地址 0x45** (Raspberry Pi 官方 firmware overlay `vc4-kms-dsi-waveshare-panel.dtbo` 内 `panel_disp1@45`; ★地址全表见 HW/I2C_ADDR_TABLE.md); "
        "★上拉在 VDD_3V3_IO (3.3V) ⇒ 与屏 3.3V 同域, 无需电平转换", "B-03")
    add("P4", "I2C_B_SDA", "CONN_LIGHT pin12", "NET_I2C_B_SDA", "NET_I2C_B_SDA",
        "I2C_B_SDA", "NET", "必装", "[官方]", "",
        "[I2C_B_SDA] ★Pi5 DISPLAY 座 pin12 = SDA0 ⇒ 屏控制 I2C (与 TMP117@0x48 同总线, 地址不冲突); "
        "★**屏模组内 MCU I2C 地址 0x45** (同 SCL 行出处)", "B-04")


# ------------------------------------------------------- P5 MIPI-CSI 传感器
CSI_LANES = [
    # lane, sig_P, sig_N, cid_P, cid_N, CONN_CAM pin P/N, dnp, 对地端接
    # ★★2026-11-02 19:5x 按 Radxa Camera 4K 31 针表 (0.3mm): MDP=正脚 / MDN=负脚
    ("CK", "CSI_D0_CK_P", "CSI_D0_CK_N", "A-01", "A-02", 18, 17, "必装", False),   # MCP18 / MCN17
    ("D0", "CSI_D0_D0_P", "CSI_D0_D0_N", "A-03", "A-04", 15, 14, "必装", False),   # MDP1 15 / MDN1 14
    ("D1", "CSI_D0_D1_P", "CSI_D0_D1_N", "A-05", "A-06", 12, 11, "必装", False),   # MDP2 12 / MDN2 11
    ("D2", "CSI_D0_D2_P", "CSI_D0_D2_N", "A-07", "A-08", 6, 5, "必装", False),      # MDP3 6 / MDN3 5
    ("D3", "CSI_D0_D3_P", "CSI_D0_D3_N", "A-09", "A-10", 3, 2, "必装", False),      # MDP4 3 / MDN4 2
]


def build_p5(by_id, spec):
    for lane, sigP, sigN, cidP, cidN, pinP, pinN, dnp, term in CSI_LANES:
        for pol, sig, cid, pin in (("P", sigP, cidP, pinP), ("N", sigN, cidN, pinN)):
            cac = f"C_AC_{sig}"
            conn_row(by_id, cid, "P5", f"{sig}_SRC", soc_pin(sig), cac, f"NET_{sig}_SRC")
            add("P5", sig, cac, f"CONN_CAM pin{pin}", cac, "100nF ±10%", "C", dnp, "[推算]",
                "TBD-03",
                f"[{sig}] AC 耦合电容位 (MIPI 标准 100nF) — 原厂是否内置 AC 耦合未回 (TBD-03); "
                f"内置则本位改 DNP, 未内置必须装")
            if term:
                rt = f"R_TERM_{sig}"
                add("P5", f"{sig}_SRC", rt, f"NET_{sig}_SRC", rt, "100Ω ±1%", "R", "DNP",
                    "[推算]", "",
                    f"[{sig}_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装)")
                add("P5", "GND", rt, "GND", rt, "100Ω ±1%", "R", "DNP", "[推算]", "",
                    f"未用差分对 100Ω 对地端接 ({lane}_{pol} 才装)")
    # ---- MCLK (单端, 单独包地) ----
    conn_row(by_id, "A-11", "P5", "CSI_MCLK_SRC", soc_pin("CSI_MCLK"), "R_SER_CSI_MCLK",
             "NET_CSI_MCLK_SRC")
    add("P5", "CSI_MCLK", "R_SER_CSI_MCLK", "CONN_CAM pin20", "R_SER_CSI_MCLK", "[待原厂]",
        "R", "必装", "[待原厂]", "TBD-03",
        "[CSI_MCLK] ★11-02 19:5x 按 Radxa Camera 4K 31 针表: MCLK = **pin20** (原 pin11) ; MCLK 串阻位 (**位必留**: MCLK 是时钟输出, 串阻兼做源端匹配/阻尼); "
        "值随 TBD-03 的 MCLK 电平与速率定, 不写死")

    # ---- ★★2026-11-02 20:5x A1 段: camera FPC 座 (31p/0.3mm) 未被主链引用的针全部补齐 ----
    #   依据: Radxa Camera 4K 31 针表 (HW/PCB/FPC_PIN_TABLES.md)
    _cam_gnd = [1, 4, 7, 10, 13, 16, 19, 21]
    for _pn in _cam_gnd:
        add("P5", "GND", f"CONN_CAM pin{_pn}", "GND", "CONN_CAM", "GND", "NET", "必装", "[官方]", "",
            "[CONN_CAM] ★Radxa Camera 4K 31 针表: pin{_pn} = GND", "")
    _cam_nc = [8, 9, 22, 23, 26]
    for _pn in _cam_nc:
        # ★★2026-11-05 03:00 修 (实测 8 个 unconnected 的根因): 这几脚**每个自己一根网**
        #   ⇒ 板上就是 5 个独立焊盘 (无铜) ⇒ KiCad **不会**把它们算成"未连接"
        #   ★**原来 5~8 个 NC 脚共用一根 NC_CONN_CAM 网** ⇒ KiCad 认为"这 5 个焊盘该互相连通" ⇒
        #   ⇒ 实测 DRC 报 8 条 unconnected (假未连接) ⇒ ★**同一个"网"里的 NC 脚不是"不接", 是"该接却没接"**
        add("P5", f"NC_CONN_CAM_{_pn}", f"CONN_CAM pin{_pn}", f"NC_CONN_CAM_{_pn}", "CONN_CAM", "NC", "NET", "必装",
            "[官方]", "",
            f"[CONN_CAM] ★Radxa Camera 4K 31 针表: pin{_pn} = NC (模组内部不接); "
            "★**每个 NC 脚独立成网** (共用一根网会被 DRC 判成'未连接' ⇒ 假告警)", "")
    add("P5", "CAM_RESET_N", "CONN_CAM pin27", soc_pin("GPIO_CAM_RESET"), "CONN_CAM", "单端", "NET",
        "必装", "[官方]", "",
        "[CAM_RESET_N] ★camera 模组 RESET (pin27, 低有效) ⇒ 接 SoC GPIO (★球位号 TBD-01); "
        "参考 Radxa CM5 overlay dts 的 reset-gpios (gpio1 RK_PB3, 低有效) ⇒ ★**主板必须能拉它**", "A-12")
    add("P5", "LIGHT_3V3", "CONN_CAM pin28", "RAIL_LIGHT_3V3", "CONN_CAM", "3.3V", "NET", "必装", "[官方]", "",
        "[CONN_CAM] ★camera 模组 VCC3.3V (pin28) ⇒ 主板 3.3V 轨", "")
    add("P5", "LIGHT_3V3", "CONN_CAM pin29", "RAIL_LIGHT_3V3", "CONN_CAM", "3.3V", "NET", "必装", "[官方]", "",
        "[CONN_CAM] ★camera 模组 VCC3.3V (pin29) ⇒ 主板 3.3V 轨 (两针并联载流)", "")
    add("P5", "LIGHT_5V", "CONN_CAM pin30", "RAIL_LIGHT_5V", "CONN_CAM", "5.0V", "NET", "必装", "[官方]", "",
        "[CONN_CAM] ★camera 模组 VCC5V (pin30) ⇒ 主板 5V 轨 (VBUS 直供 + 限流)", "")
    add("P5", "LIGHT_5V", "CONN_CAM pin31", "RAIL_LIGHT_5V", "CONN_CAM", "5.0V", "NET", "必装", "[官方]", "",
        "[CONN_CAM] ★camera 模组 VCC5V (pin31) ⇒ 主板 5V 轨 (两针并联载流)", "")

    # ---- CSI_RESET_N (10k 上拉到 1.8V 域) ----
    # ---- sensor 三条电源轨 · 连接器 ----
    # ---- 传感器连接器 ----
    add("P5", "CONN_CAM", "CONN_CAM", "CONN_CAM", "CONN_CAM",
        "★31p@0.3mm 板内 FPC 座 (Radxa Camera 4K; 座 HIROSE FH35C-31S-0.3SHW(50); 针位见 HW/PCB/FPC_PIN_TABLES.md)", "CONN", "必装", "[推算]", "TBD-03",
        "[CONN_CAM] ★**2026-11-03 09:3x 订正**: 本行**不再占用任何针脚** (原占 pin1 ⇒ 与 31 针表 pin1=GND 撞车); "
        "11=MCLK, 12=CSI_RESET_N, 13/14=I2C_A, 15/16/17=sensor 3V3/1V8/2V8; "
        "pin 数/pitch/翻盖方式待结构总工 (ISS-065); ★pin 编号为**本版自拟**, 非规格给定")


def by_id_cid_rail(spec, rail):
    for c in spec["connections"]:
        if c.get("rail") == rail:
            return c.get("volt", "")
    for r in spec["power_rails"]:
        if r["rail"] == rail:
            return r.get("volt", "")
    return ""


# -------------------------------------------------- P6 高速差分与连接器
def build_p6(by_id, spec):
    # ★★DP_TX 4 lane 整块已删除 (RK3572 无 DP TX ⇒ 无桥接芯片 ⇒ 8 串阻 + 8 对地电容 + 桥接位全无)
    #   ⇒ P6 现在只剩 USB 2.0 / Type-C CC / 跨铰链预留。
    # ---- USB 2.0 (Type-C · 主 PCB) ----
    conn_row(by_id, "B-21", "P6", "USB_D_P_SRC", soc_pin("USB_D_P"), "R_SER_USB_D_P",
             "NET_USB_D_P_SRC")
    conn_row(by_id, "B-22", "P6", "USB_D_N_SRC", soc_pin("USB_D_N"), "R_SER_USB_D_N",
             "NET_USB_D_N_SRC")
    # ★★2026-11-04 19:5x 删 (跨铰链 USB 在 demo 板不做 — 老板 11-02 19:25「跨铰链取消」):
    #   原先 R_SER_USB_D_P 同时出现在 {USB_D_P_SRC, USB_D_P, NET_USB_D_P_ESD} 三个网
    #   ⇒ ★**22Ω 串阻被短接掉** (Type-C D+ 与 SoM D+ 同网) + ESD 双失效 + 门禁脚数报红。
    #   ⇒ demo 板只保留**板载 Type-C 一条 USB 数据路径** (跨铰链 USB 属整机阶段)。
    # ---- Type-C CC (Rd 下拉; 接 PD 控制器时由控制器接管) ----
    conn_row(by_id, "B-23", "P6", "USB_CC1", "J_TYPE_C A5", "R_CC1", "NET_USB_CC1")
    add("P6", "USB_CC2", "J_TYPE_C B5", "R_CC2", "R_CC2", "5.1k ±1%", "R", "必装", "[推算]",
        "", "[USB_CC2] Type-C Rd (非 PD 时下拉; 接 PD 控制器时由控制器接管)")
    add("P6", "GND", "R_CC1", "GND", "R_CC1", "5.1k ±1%", "R", "必装", "[推算]", "",
        "Type-C Rd 下拉端")
    add("P6", "GND", "R_CC2", "GND", "R_CC2", "5.1k ±1%", "R", "必装", "[推算]", "",
        "Type-C Rd 下拉端")
    add("P6", "USB_CC2", "USB_CC2", "J_TYPE_C B5", "NET_USB_CC2", "单端", "NET", "必装",
        "[推算]", "", "[USB_CC2] CC2 网节点 (同 net)", "B-23")
    # ---- Type-C 座 GND / 屏蔽 + 跨铰链预留 ----
    add("P6", "GND", "J_TYPE_C A1+A12+B1+B12", "GND", "J_TYPE_C", "Type-C 16p 座 (物理脚位 A/B 编号)", "CONN", "必装",
        "[官方]", "", "Type-C GND 脚 (★V1.5 修正: USB-IF 16p 的 GND 是 **A1/A12/B1/B12 四个脚**, "
        "原来只接 A1+A12 · B1/B12 悬空 = 回流路径减半)")
    add("P6", "GND", "J_TYPE_C shield", "GND", "J_TYPE_C", "Type-C 16p 座 (物理脚位 A/B 编号)", "CONN", "必装",
        "[官方]", "", "Type-C 屏蔽壳 接 GND (单点, 与机壳地的接法待结构定)")
    # ★★2026-11-04 19:5x 删: 跨铰链 USB 连接器 (老板 11-02 19:25「跨铰链取消」⇒ demo 板不装)


# ------------------------------------------------------- P7 板级接口与测试点
LEDS = [("R", "B-12", "必装"), ("G", "B-13", "必装"), ("B", "B-14", "DNP")]
KEYS = [
    # 规格信号, 净名 (无 +), 记号, conn_id, dnp, 描述
    ("KEY_PWR", "KEY_PWR", "PWR", "B-15", "必装", "电源键"),
    ("KEY_VOL+", "KEY_VOL_P", "VP", "B-16", "必装", "音量+ 键"),
    ("KEY_VOL-", "KEY_VOL_M", "VM", "B-17", "必装", "音量- 键"),
    ("KEY_CAM", "KEY_CAM", "CAM", "B-18", "DNP", "CAM 键 (焊盘必留, 不装)"),
]
# 全部测试点 (规格 13 个逻辑 TP · 展开成 40 个物理测点)
TPS = [
    ("TP_VBUS", "VBUS_5V", "J_TYPE_C A4+A9+B4+B9", "Type-C 入口 5V", "Type-C 出口侧 ≤3mm", "必装"),
    ("TP_SYS", "SYS", "RAIL_SYS", "系统 3.7V 主轨", "电池保护后 (镜脚本地)", "必装"),
    ("TP_BAT", "BAT", "U_BATPROT", "电池电压", "BQ25896 BAT 脚", "必装"),
    ("TP_VCORE", "V_CORE", "U_DCDC_VCORE", "SoC 核心轨", "DC-DC 输出", "必装"),
    ("TP_VIO", "V_SOC_IO", "U_DCDC_VIO", "SoC IO 轨", "DC-DC/LDO 输出", "必装"),
    ("TP_LIGHT_3V3", "LIGHT_3V3", "CONN_LIGHT pin14", "屏轨 3.3V (Pi5 DISPLAY 座 pin14=3V3)", "LDO 输出", "必装"),
    ("TP_CSI_CK_P", "CSI_D0_CK_P", "CONN_CAM pin18", "CSI 时钟差分 (示波器测眼图/摆幅)",
     "连接器出口 (规格合并名 TP_CSI_D0_CK_P / _N)", "必装"),
    ("TP_CSI_CK_N", "CSI_D0_CK_N", "CONN_CAM pin17", "CSI 时钟差分 (规格合并名 TP_CSI_D0_CK_P / _N)",
     "连接器出口", "必装"),
    ("TP_CSI_D0_P", "CSI_D0_D0_P", "CONN_CAM pin15", "CSI D0 数据差分", "连接器出口", "必装"),
    ("TP_CSI_D0_N", "CSI_D0_D0_N", "CONN_CAM pin14", "CSI D0 数据差分", "连接器出口", "必装"),
    ("TP_MCLK", "CSI_MCLK", "CONN_CAM pin20", "MCLK (包地走线)", "连接器出口", "必装"),
    ("TP_DSI_CK_P", "DSI_D0_CK_P", "CONN_LIGHT pin6", "DSI 时钟差分 (Pi5 DISPLAY pin6=DSI1_CP)",
     "连接器出口 (规格合并名 TP_DSI_D0_CK_P / _N)", "必装"),
    ("TP_DSI_CK_N", "DSI_D0_CK_N", "CONN_LIGHT pin5", "DSI 时钟差分 (Pi5 DISPLAY pin5=DSI1_CN; 规格合并名 TP_DSI_D0_CK_P / _N)",
     "连接器出口", "必装"),
    ("TP_DSI_D0_P", "DSI_D0_D0_P", "CONN_LIGHT pin9", "DSI D0 数据差分 (Pi5 DISPLAY pin9=DSI1_DP0)", "连接器出口", "必装"),
    ("TP_DSI_D0_N", "DSI_D0_D0_N", "CONN_LIGHT pin8", "DSI D0 数据差分 (Pi5 DISPLAY pin8=DSI1_DN0)", "连接器出口", "必装"),
    # ★2026-11-04: DSI lane1/2/3 的差分测点 (22p 座口径: D1=pin2/3 · D2=pin16/17 · D3=pin18/19)
    ("TP_DSI_D1_P", "DSI_D0_D1_P", "CONN_LIGHT pin3", "DSI D1 数据差分 (Pi5 DISPLAY pin3=DSI1_DP1)", "连接器出口", "必装"),
    ("TP_DSI_D1_N", "DSI_D0_D1_N", "CONN_LIGHT pin2", "DSI D1 数据差分 (Pi5 DISPLAY pin2=DSI1_DN1)", "连接器出口", "必装"),
    ("TP_DSI_D2_P", "DSI_D0_D2_P", "CONN_LIGHT pin17", "DSI D2 数据差分 (自用脚)", "连接器出口", "必装"),
    ("TP_DSI_D2_N", "DSI_D0_D2_N", "CONN_LIGHT pin16", "DSI D2 数据差分 (自用脚)", "连接器出口", "必装"),
    ("TP_DSI_D3_P", "DSI_D0_D3_P", "CONN_LIGHT pin19", "DSI D3 数据差分 (自用脚)", "连接器出口", "必装"),
    ("TP_DSI_D3_N", "DSI_D0_D3_N", "CONN_LIGHT pin18", "DSI D3 数据差分 (自用脚)", "连接器出口", "必装"),
    ("TP_I2CB_SCL", "I2C_B_SCL", "CONN_LIGHT pin11", "屏控制 I2C 时钟 (Pi5 DISPLAY pin11=SCL0)", "连接器出口", "必装"),
    ("TP_I2CB_SDA", "I2C_B_SDA", "CONN_LIGHT pin12", "屏控制 I2C 数据 (Pi5 DISPLAY pin12=SDA0)", "连接器出口", "必装"),
    ("TP_I2CA_SCL", "I2C_A_SCL", "CONN_CAM pin24", "I2C_A 时钟", "连接器出口", "必装"),
    ("TP_I2CA_SDA", "I2C_A_SDA", "CONN_CAM pin25", "I2C_A 数据", "连接器出口", "必装"),
    # ★★2026-11-03 19:29 老板拍板 demo 不需要触控 ⇒ 屏侧触控 I2C 测试点已删 (原行在此)
    # ★★2026-11-03 19:29 老板拍板 demo 不需要触控 ⇒ 屏侧触控 I2C 测试点已删 (原行在此)
    # ★2026-11-04 19:5x 改: 测试点挂在 **Type-C 侧网** (J_USB_C A6/B6 只能落一个网 ⇒
    #   之前挂在 SoM 侧网 ⇒ 同一物理脚落两个网 ⇒ "同名脚多网" 提示)
    ("TP_USB_D_P", "NET_USB_D_P_TYPEC", "J_USB_C A6+B6", "USB 2.0 差分",
     "★板载 Type-C 出口 (串阻的 Type-C 侧; 规格合并名 TP_USB_D+ / D-)", "必装"),
    ("TP_USB_D_N", "NET_USB_D_N_TYPEC", "J_USB_C A7+B7", "USB 2.0 差分 (规格合并名 TP_USB_D+ / D-)",
     "★板载 Type-C 出口 (串阻的 Type-C 侧)", "必装"),
    ("TP_FSIN", "FSIN_OUT", "R_SER_FSIN", "帧同步 (FSIN/VSYNC) 引出",
     "SoC 侧 -> 回答原厂问询 Q4b.3", "必装"),
    ("TP_CHG_STAT", "CHG_STAT", "R_PU_CHG_STAT", "充电状态",
     "BQ25896 STAT 脚 -> 回答 Q4b.4", "必装"),
    ("TP_PG", "PWR_GOOD", "R_PU_PG", "电源好 (BQ25896 PG 脚)", "充电板 -> 主 PCB 跨板点", "必装"),
    ("TP_ID", "ID_DETECT_0", "R_PU_ID0", "板级版本识别 (I2C EEPROM 或 GPIO 编码)",
     "主 PCB", "必装"),
    ("TP_LED_R", "LED_R", "R_LED_R", "LED 红", "主 PCB", "必装"),
    ("TP_LED_G", "LED_G", "R_LED_G", "LED 绿", "主 PCB", "必装"),
    ("TP_LED_B", "LED_B", "R_LED_B", "LED 蓝 (无无线 -> DNP)", "主 PCB", "DNP"),
    ("TP_KEY_PWR", "KEY_PWR", "R_KEY_PWR", "电源键", "主 PCB", "必装"),
    ("TP_KEY_VP", "KEY_VOL_P", "R_KEY_VP", "音量+ 键", "主 PCB", "必装"),
    ("TP_KEY_VM", "KEY_VOL_M", "R_KEY_VM", "音量- 键", "主 PCB", "必装"),
    ("TP_RESET", "RESET_N", "R_PU_RESET_N", "复位网", "主 PCB", "必装"),
    ("TP_BOOT", "BOOT_N", "R_PU_BOOT_N", "BOOT 网", "主 PCB", "必装"),
    ("TP_JTAG", "JTAG_TCK", "J_DEBUG pin1", "JTAG 时钟", "调试排针", "必装"),
    ("TP_UART", "UART_TX", "J_UART pin1", "UART TX (与 USB 二选一)", "调试排针", "可选"),
]


def build_p7(by_id, spec):
    for col, cid, dnp in LEDS:
        conn_row(by_id, cid, "P7", f"LED_{col}", soc_pin(f"LED_{col}"), f"R_LED_{col}",
                 f"NET_LED_{col}")
        add("P7", f"LED_{col}_D", f"R_LED_{col}", f"D_LED_{col}", f"R_LED_{col}", "1k ±1%",
            "R", dnp, "[推算]", "",
            f"[LED_{col}_D] LED_{col} 串阻 (3.3V 驱动; 实际值随 LED Vf 与目标亮度定)")
        add("P7", "GND", f"D_LED_{col}", "GND", f"D_LED_{col}", "LED (待选型)", "LED", dnp,
            "[推算]", "", f"LED_{col} 阴极 -> GND")
    for sig, net, tag, cid, dnp, desc in KEYS:
        conn_row(by_id, cid, "P7", net, soc_pin(net), f"R_KEY_{tag}", f"NET_KEY_{tag}")
        add("P7", net, f"SW_KEY_{tag}", f"NET_KEY_{tag}", f"SW_KEY_{tag}", "按键 (待选型)",
            "SW", dnp, "[推算]", "", f"[{net}] {desc} 按键")
        add("P7", "VDD_3V3_IO", f"R_KEY_{tag}", "RAIL_VDD_3V3_IO", f"R_KEY_{tag}", "10k ±1%",
            "R", "必装", "[推算]", "",
            f"[VDD_3V3_IO] {desc} 上拉 (按下到 GND, 支持长按)")
        add("P7", "GND", f"SW_KEY_{tag}", "GND", f"SW_KEY_{tag}", "按键 (待选型)", "SW", dnp,
            "[推算]", "", f"{desc} 另一端 -> GND")
        add("P7", net, f"C_KEY_{tag}", "GND", f"C_KEY_{tag}", "100nF ±10%", "C", dnp,
            "[推算]", "",
            f"[{net}] 按键 RC 消抖电容 (10k 上拉 + 100nF, τ≈1ms); 是否需要消抖取决于 SoC 驱动方式 "
            f"(等 SW 总工确认, 不影响本版布线)")
    for tp, net, node2, what, where, dnp in TPS:
        add("P7", net, tp, node2, tp, "测试点", "TP", dnp, "[推算]", "",
            f"测什么: {what}; 位置: {where}")


# ------------------------------------------- P8 时钟 · 复位 · 调试
def build_p8(by_id, spec):
    # ---- XTAL: 内部 RC 不装 / 外部晶振焊盘位不装 (原厂一句话定生死) ----
    for pol in ("IN", "OUT"):
        add("P8", f"XTAL_{pol}", soc_pin(f"XTAL_{pol}"), "X1", f"NET_XTAL_{pol}", "12pF",
            "NET", "DNP", "[同Die参考-待官方确认]", "TBD-12",
            f"时钟: 外部晶振位 (XTAL_{pol}); 参考版**同时**给 内部RC(不装) 与 外部晶振(焊盘位+2×12pF, 不装) 两套")
        add("P8", f"XTAL_{pol}", f"C_XTAL_{pol}", f"NET_XTAL_{pol}", f"C_XTAL_{pol}",
            "12pF ±10%", "C", "DNP", "[同Die参考-待官方确认]", "TBD-12",
            f"[XTAL_{pol}] 晶振负载电容 (XTAL_{pol} 侧)")
        add("P8", "GND", f"C_XTAL_{pol}", "GND", f"C_XTAL_{pol}", "12pF ±10%", "C", "DNP",
            "[同Die参考-待官方确认]", "TBD-12", "晶振负载电容 地端")
    add("P8", "XTAL", "X1", "NET_XTAL_IN", "X1", "晶振焊盘位 (不装)", "CONN", "DNP",
        "[同Die参考-待官方确认]", "TBD-12",
        "[XTAL] 外部晶振**焊盘位** (不装): 频率/负载/封装待原厂确认 (TBD-12); "
        "AR9481 同 Die 也不能确定 · 先留位")
    # ---- RESET_N (上拉 + RC + 按键) ----
    conn_row(by_id, "B-10", "P8", "RESET_N", "R_PU_RESET_N", "R_SER_RESET_N", "NET_RESET_N")
    add("P8", "VDD_1V8_IO", "R_PU_RESET_N", "RAIL_VDD_1V8_IO", "R_PU_RESET_N", "10k ±1%",
        "R", "必装", "[推算]", "", "[VDD_1V8_IO] RESET_N 上拉 (1.8V 域)", "B-10")
    add("P8", "RESET_N_SOC", "R_SER_RESET_N", soc_pin("RESET_N"), "R_SER_RESET_N", "1k ±1%",
        "R", "必装", "[推算]", "", "[RESET_N_SOC] RESET_N RC 串联 (与 C_RST 构成 RC 复位)", "B-10")
    add("P8", "RESET_N_SOC", "C_RST", "NET_RESET_N_SOC", "C_RST", "100nF ±10%", "C", "必装",
        "[推算]", "", "[RESET_N_SOC] RESET_N 对地 RC 电容 (τ=100ms; **释放时期待原厂 TBD-12**)",
        "B-10")
    add("P8", "GND", "C_RST", "GND", "C_RST", "100nF ±10%", "C", "必装", "[推算]", "",
        "RESET RC 电容 地端", "B-10")
    add("P8", "RESET_N", "SW_RST", "NET_RESET_N", "SW_RST", "复位按键 (待选型)", "SW", "必装",
        "[推算]", "", "[RESET_N] 复位键 -> GND (软上电 / 进下载模式)", "B-10")
    add("P8", "GND", "SW_RST", "GND", "SW_RST", "复位按键 (待选型)", "SW", "必装", "[推算]", "",
        "复位键 -> GND", "B-10")
    # ---- BOOT_N ----
    conn_row(by_id, "B-11", "P8", "BOOT_N", soc_pin("BOOT_N"), "R_PU_BOOT_N", "NET_BOOT_N")
    add("P8", "VDD_1V8_IO", "R_PU_BOOT_N", "RAIL_VDD_1V8_IO", "R_PU_BOOT_N", "10k ±1%", "R",
        "必装", "[推算]", "", "[VDD_1V8_IO] BOOT_N 上拉 (1.8V 域)", "B-11")
    add("P8", "BOOT_N", "SW_BOOT", "NET_BOOT_N", "SW_BOOT", "BOOT 按键 (待选型)", "SW", "必装",
        "[推算]", "", "[BOOT_N] BOOT 键 -> GND (进下载模式)", "B-11")
    add("P8", "GND", "SW_BOOT", "GND", "SW_BOOT", "BOOT 按键 (待选型)", "SW", "必装", "[推算]",
        "", "BOOT 键 -> GND", "B-11")
    # ---- JTAG 4 线 ----
    for sig, pin in (("JTAG_TCK", "pin1"), ("JTAG_TMS", "pin2"), ("JTAG_TDI", "pin3"),
                     ("JTAG_TDO", "pin4")):
        conn_row(by_id, "B-19", "P8", f"{sig}_SOC", soc_pin(sig), f"R_{sig}",
                 f"NET_{sig}_SOC")
        add("P8", sig, f"R_{sig}", f"J_DEBUG {pin}", f"R_{sig}", "100Ω ±1%", "R", "必装",
            "[推算]", "", f"[{sig}] JTAG {sig[5:]} 串阻 (隔离 SoC 调试脚)", "B-19")
    add("P8", "J_DEBUG", "J_DEBUG", "J_DEBUG", "J_DEBUG", "1×4 1.27mm 排针 (JTAG)",
        "CONN", "必装", "[推算]", "",
        "[J_DEBUG] JTAG 调试排针 (不装贴片, 手工可焊); pin1=TCK, 2=TMS, 3=TDI, 4=TDO")
    # ---- UART 2 线 (与 USB 二选一) ----
    conn_row(by_id, "B-20", "P8", "UART_TX", soc_pin("UART_TX"), "J_UART pin1", "NET_UART_TX")
    conn_row(by_id, "B-20", "P8", "UART_RX", soc_pin("UART_RX"), "J_UART pin2", "NET_UART_RX")
    add("P8", "UART_RX", "J_UART", "J_UART pin2", "J_UART", "1×2 1.27mm 排针 (UART)", "CONN",
        "可选", "[推算]", "",
        "[UART_RX] 规格: UART 与 JTAG 复用同一排针 -> 本版拆成 1×2 独立排针 (原厂要求复用则再合并)")
    # ---- FSIN (帧同步引出) ----
    conn_row(by_id, "B-09", "P8", "FSIN", soc_pin("FSIN"), "R_SER_FSIN", "NET_FSIN")
    add("P8", "FSIN_OUT", "R_SER_FSIN", "TP_FSIN", "R_SER_FSIN", "50Ω ±1%", "R", "必装",
        "[推算]", "TBD-13", "[FSIN_OUT] FSIN 引出串阻 (50Ω 源端匹配)")

    # ---- ★V1.1 补画: 上电时序链 (DC-DC PG 状态 + 电压监控 · RESET 链式释放) ----
    # ★★2026-11-03 订正: 两路 DC-DC 的 PG 是**开漏输出并联** (wired-AND ⇒ 同网 PG_AND, 公共上拉 R_PG_PULL)
    #   ⇒ 两个 PG 脚**本来就在同一个网上** ⇒ 测试点也必须挂在 PG_AND, 不能各自再挂一个网
    #   (原来 TP_PG_VCORE 挂 PG_VCORE / TP_PG_VIO 挂 PG_VIO ⇒ **同一个物理脚挂两个网** ⇒ 短路)
    add("P8", "PG_AND", "U_DCDC_VCORE PG", "TP_PG_VCORE", "TP_PG_VCORE",
        "PG (开漏, 需上拉)", "TP", "必装", "[官方]", "TBD-12",
        "[PG_AND] V_CORE 轨 PG 状态引出 (开漏; ★两路 PG 并联成一个 wired-AND 节点 ⇒ 测试点挂公共网)")
    add("P8", "PG_AND", "U_DCDC_VIO PG", "TP_PG_VIO", "TP_PG_VIO",
        "PG (开漏, 需上拉)", "TP", "必装", "[官方]", "TBD-12",
        "[PG_AND] V_SOC_IO 轨 PG 状态引出 (开漏; 同上, 与 V_CORE 的 PG 并联)")
    # 电压监控 · RESET 链式释放 (分压比随原厂电压定, 只改电阻不改板)
    add("P8", "V_SOC_IO", "RAIL_V_SOC_IO", "R_SUPV_DIV1", "R_SUPV_DIV1",
        "[待选型] 分压上臂 (0Ω 跳线位)", "R", "必装", "[推算]", "TBD-02",
        "[SUPV_SENSE] ★V1.1: 电压监控分压 (把 V_SOC_IO 的实际电压映射到监控芯片窗口) · "
        "**原厂电压定了只改两颗电阻, 不改板** (ISS-082 的正确解法: 换料 + 换阻值, 不用可编程器件)")
    add("P8", "SUPV_SENSE", "R_SUPV_DIV1", "R_SUPV_DIV2", "R_SUPV_DIV2",
        "[待选型] 分压下臂 (0Ω 跳线位)", "R", "必装", "[推算]", "TBD-02",
        "[SUPV_SENSE] 分压下臂 (到地)")
    add("P8", "GND", "R_SUPV_DIV2", "GND", "R_SUPV_DIV2", "[待选型] 分压下臂 (0Ω 跳线位)",
        "R", "必装", "[推算]", "TBD-02", "[SUPV_SENSE] 分压下臂 地端")
    add("P8", "VDD_1V8_IO", "U_SUPV VDD", "RAIL_VDD_1V8_IO", "U_SUPV",
        "[待选型] 电压监控 + 复位 (TPS3808G01 类)", "IC", "必装", "[推算]", "TBD-12",
        "[VDD_1V8_IO] 上电监督器 (挂常供电轨); 监控窗口电压待原厂电源域表定 (TBD-02)")
    add("P8", "SUPV_SENSE", "U_SUPV SENSE", "U_SUPV", "U_SUPV",
        "[待选型] 电压监控 + 复位 (TPS3808G01 类)",
        "IC", "必装", "[推算]", "TBD-02", "[SUPV_SENSE] 监督器采样脚 (经分压)")
    add("P8", "RESET_N", "U_SUPV RESET", "NET_RESET_N", "U_SUPV", "开漏释放",
        "IC", "必装", "[推算]", "TBD-12",
        "[RESET_N] ★V1.1: RESET_N 增加一路监督器开漏释放 (与已有 10k 上拉 + RC + 复位键共存: "
        "任一路拉低都生效)")
    add("P8", "VDD_1V8_IO", "C_SUPV", "RAIL_VDD_1V8_IO", "C_SUPV", "100nF ±10%", "C", "必装",
        "[推算]", "", "[VDD_1V8_IO] 监督器 就近去耦", "B-10")
    add("P8", "GND", "C_SUPV", "GND", "C_SUPV", "100nF ±10%", "C", "必装", "[推算]", "",
        "[VDD_1V8_IO] 监督器 去耦 地端", "B-10")


# ------------------------------------------------- P9 跨铰链界面 (V1.1 新增页)
def build_p9(by_id, spec):
    """跨铰链界面页 —— 充电板 (镜框) 与主 PCB (镜脚) 之间的 4 组通道 + 保护/滤波件

    ★为什么要单独一页 (2026-10-27 V1.1):
      V1 把跨铰链的东西散在 P1/P5/P6 里 · 看图的人**数不出到底有几组跨铰链、走多少 pin** ·
      结构总工拿不到明确的接口请求, 跨铰链方案 (柔性段长度 / 应力 / 连接器) 只能靠猜。
      本页把 4 组通道 + 保护件 + 板级归属一次列清, 并把"是否合并成一个跨铰链连接器"列为待评估项。
    """
    # ---- 4 个跨铰链连接器 (本体标 HINGE) ----
    add("P9", "HINGE_CHG", "J_CHG", "J_CHG", "J_CHG",
        "1×10p@0.5mm 排线座 (充电板↔主 PCB, 跨铰链载流)", "CONN", "必装", "[推算]", "",
        "[HINGE_CHG] 通道 1/4 **充电电流 + 状态回读** (★V1.2 改: 电池在镜脚 ⇒ 跨铰链的是**充电电流 "
        "1.0-1.5A**, **SYS 0.55A 不过铰链**): pin1/pin2=BAT_CHG (双 pin 并联载流), pin3/pin4=GND "
        "(回流双 pin), pin5=CHG_STAT, pin6=PWR_GOOD, pin7=VBUS_DET, pin8-10=预留; ★pin 编号为本版自拟 "
        "(型号/间距/载流待结构确认, ISS-085)")
    # ★★2026-11-04 19:5x 删: 跨铰链 USB 座 + 它的 ESD 阵列 + 双回流地 (demo 板不做跨铰链, 老板 11-02 19:25)
    add("P9", "CSI_D0_CK_P", "CONN_CAM pin18", "D_ESD_CAM", "D_ESD_CAM",
        "ESD 阵列 [待选型] (多通道 CSI)", "D", "必装", "[推算]", "TBD-03",
        "[CSI_D0_CK_P] ★跨铰链 CSI 主板侧 ESD 阵列位 (紧贴 CONN_CAM); 通道数随 lane 数定")
    add("P9", "GND", "D_ESD_CAM", "GND", "D_ESD_CAM", "ESD 阵列 [待选型]", "D", "必装",
        "[推算]", "TBD-03", "[CSI_D0_CK_P] CSI ESD 地端")
    # ---- 充电板侧: USB 差分从跨铰链连接器接到 Type-C (V1 漏画这一段) ----
    # ★★2026-11-04 19:5x 删: 充电板侧的跨铰链 USB 走线 (依赖已删的 CONN_USB; 整机阶段再画)
    # ---- 跨铰链回流/地要求 (画成位号行, 便于结构总工提要求) ----
    add("P9", "GND", "CHG_GND_STAR", "GND", "CHG_GND_STAR", "单点汇流位", "CONN", "必装",
        "[推算]", "",
        "[GND] ★跨铰链回流要求: 柔性段的 GND 必须走**连续参考面**(不能细线), 两端各留 ≥2 个 GND pin; "
        "单点汇流位置由结构总工定 (ISS-065)")
    add("P9", "BAT_CHG", "J_CHG pin1", "TP_BAT_CHG", "TP_BAT_CHG", "跨铰链段压降测点", "TP",
        "必装", "[推算]", "",
        "[BAT_CHG] ★跨铰链充电电流段: 双 pin 并联载流 + 压降/发热核算 (1.5A × 接触电阻); "
        "**充电路径上不装 π 滤波** (会破坏 BQ25896 环路稳定性)")


# ------------------------------------------- P10 充电板页 (V1.5): 数据来自 state/p10_rows.json
def build_p10_json() -> int:
    """充电板整页的行数据由 `state/p10_rows.json` 提供 (子 agent 按 HW/CHARGE_BOARD_SPEC.md 产出,
    我只做加载 + 门禁) —— 遵循"规格先行、机械转换我来做"的分工铁律。"""
    p = os.path.join(HERE, "p10_rows.json")
    if not os.path.exists(p):
        return 0
    data = json.load(open(p, encoding="utf-8"))
    for r in data:
        add(r.get("page", "P10"), r["net"], r["node1"], r["node2"], r["ref"], r["value"],
            r.get("type", ""), r.get("dnp", "必装"), r.get("evidence", "[推算]"),
            r.get("tbd", ""), r.get("note", ""), r.get("conn_id", ""))
    return len(data)


# ------------------------------------------------------- ★A2 段: SoM 座接入 + F13 电源使能
def build_a2_som(by_id, spec):
    """★★2026-11-03 A2 段 (ISS-165): SoM (Forlinx FET3572-C) 的 4×100pin BTB 座接入主板

    ★三条致命项级别的结论 (全部出自 Forlinx 官方手册, 可复算):
      ① **SoM 自己的供电 VCC_DCIN = P3_91/93/95/97/98/99/100 (7 脚并联, 5~13V)**
         ⇒ **直供 5V, 不经过 U_EN_SW 门控** (否则 SoM 自己永远起不来)
      ② **F13: CARRIER_BOARD_EN = P3_87 (SoM 输出, 3.3V)** —— 手册原文: 底板早于核心板上电 ⇒
         "通电瞬间电流过大, 设备无法启动, **甚至对处理器造成不可逆损坏**"
         ⇒ ★**主板各路必须由它放行** ⇒ 负载开关 U_EN_SW: IN=5V, OUT=RAIL_BOARD_5V, EN=CARRIER_BOARD_EN
      ③ **camera MCLK 由 SoM 出 (CAM_CLK0_OUT_M0)** ⇒ 上一版"主板自己产 MCLK"的结论作废
    """
    F = _SOM_ASSIGN.get("fixed", {})
    dcin = F.get("VCC_DCIN", [])
    car_en = F.get("CARRIER_BOARD_EN", "P3_87")

    # ---- ① demo 板自己的 Type-C (5V 输入 + USB 数据) ----
    #   ★demo 形态 (老板 11-02 19:25): "demo 直接 USB-C 5V 供电, 不装电池、不上充电链"
    #   ⇒ 主板自己带一个 Type-C; 整机阶段这块是 DNP (整机走跨铰链 USB + 充电板)
    # ---- ★demo 板 USB-C 入口的 ESD 阵列 (Forlinx 载板指引: ESD 阵列紧贴接口) ----
    # ★2026-11-04 19:5x 改: ESD 阵列直接跨在 **SoM 侧 D+ 节点 (USB_D_P_SRC)** 与地之间
    #   (原来挂在独立的 NET_USB_D_P_ESD 网上 ⇒ 那根网是**幽灵分裂网**, 且串阻被拉进第三个网)
    add("P1", "USB_D_P_SRC", "D_ESD_USB_D", "USB_D_P_SRC", "D_ESD_USB_D",
        "ESD 阵列 [待选型] (USB 2.0 双通道)", "D", "必装", "[推算]", "",
        "[D_ESD_USB_D] ★USB-C 入口 ESD 阵列 (紧贴 J_USB_C, 跨 D+ 与地) —— ★**Forlinx 载板指引要求 ESD 紧贴接口**", "A-24")
    add("P1", "GND", "D_ESD_USB_D", "GND", "D_ESD_USB_D", "ESD 阵列 [待选型]", "D", "必装",
        "[推算]", "", "[D_ESD_USB_D] ESD 地端", "A-24")
    # ★★2026-11-05 03:45 修 (BOM 备料错): 这一行的 ref 是 J_USB_C, 但 value/type 写的是**网**的
    #   ("5.0V ±5% (USB-C 5V)" / RAIL) ⇒ BOM 生成器按"每个 ref 取第一行" ⇒ ★**BOM 里 USB-C 座的值变成
    #   "5.0V ±5% (USB-C 5V) / RAIL"** ⇒ 备料的人会以为那是条 5V 轨, 而不是座
    #   ⇒ ★**改法**: 这一行(ref=J_USB_C)的 value/type 写成**器件自己的** ⇒ 网的语义由 net 列承担
    #   (net=RAIL_DEMO_5V 不变 ⇒ 电气不变; BOM 里 USB-C 座就显示成座)
    add("P1", "RAIL_DEMO_5V", "J_USB_C A4+A9+B4+B9", "RAIL_DEMO_5V", "J_USB_C",
        "Type-C 16p 座 (demo 板 5V 输入 + USB 数据)", "CONN", "必装", "[官方]", "",
        "[RAIL_DEMO_5V] ★demo 板自己的 USB-C 5V 输入 ⇒ 同时供 SoM 的 VCC_DCIN (5~13V) 与 U_EN_SW", "A-24")
    add("P1", "RAIL_DEMO_5V", "D_ESD_DEMO", "RAIL_DEMO_5V", "D_ESD_DEMO",
        "ESD 阵列 [待选型] (USB 2.0)", "D", "必装", "[推算]", "",
        "[RAIL_DEMO_5V] USB-C VBUS 入口 ESD 阵列 (紧贴 J_USB_C)", "A-24")
    add("P1", "GND", "D_ESD_DEMO", "GND", "D_ESD_DEMO", "ESD 阵列 [待选型]", "D", "必装",
        "[推算]", "", "[RAIL_DEMO_5V] USB ESD 阵列 地端", "A-24")
    add("P1", "RAIL_DEMO_5V", "FB_DEMO", "RAIL_DEMO_5V", "FB_DEMO", "π 滤波磁珠 [待选型]", "L",
        "必装", "[推算]", "", "[RAIL_DEMO_5V] VBUS π 滤波 (磁珠+体电容)", "A-24")
    add("P1", "GND", "FB_DEMO", "GND", "FB_DEMO", "π 滤波磁珠 [待选型]", "L", "必装",
        "[推算]", "", "[RAIL_DEMO_5V] π 滤波 地端", "A-24")
    add("P1", "RAIL_DEMO_5V", "C_VBUS_DEMO", "RAIL_DEMO_5V", "C_VBUS_DEMO", "10µF ±20%", "C",
        "必装", "[推算]", "", "[RAIL_DEMO_5V] VBUS 体电容", "A-24")
    add("P1", "GND", "C_VBUS_DEMO", "GND", "C_VBUS_DEMO", "10µF ±20%", "C", "必装",
        "[推算]", "", "[RAIL_DEMO_5V] VBUS 体电容 地端", "A-24")
    add("P1", "GND", "R_CC1_D", "GND", "R_CC1_D", "5.1k ±1% (CC1 下拉)", "R", "必装", "[官方]", "",
        "[R_CC1_D] USB-C CC1 5.1k 下拉 (⇒ UFP 受电端)", "A-24")
    # ★★2026-11-03: USB-C 的 CC/地脚用**真实 USB-IF 物理脚** (CC1=A5 · CC2=B5 · GND=A1/A12/B1/B12 + shell)
    add("P1", "GND", "J_USB_C A1+A12+B1+B12", "GND", "J_USB_C", "GND (4 脚 + shell)", "NET",
        "必装", "[官方]", "",
        "[J_USB_C] USB-C 的 4 个 GND 脚 + 外壳 ⇒ 主板地", "A-24")
    add("P1", "USB_CC1", "J_USB_C A5", "R_CC1_D", "J_USB_C", "CC1 (5.1k 下拉 ⇒ 受电端 UFP)", "NET",
        "必装", "[官方]", "", "[J_USB_C] CC1 → 5.1k 下拉 ⇒ 本板做受电端", "A-24")
    add("P1", "USB_CC2", "J_USB_C B5", "R_CC2_D", "J_USB_C", "CC2 (5.1k 下拉)", "NET",
        "必装", "[官方]", "", "[J_USB_C] CC2 → 5.1k 下拉", "A-24")
    add("P1", "GND", "R_CC2_D", "GND", "R_CC2_D", "5.1k ±1% (CC2 下拉)", "R", "必装", "[官方]", "",
        "[R_CC2_D] USB-C CC2 5.1k 下拉", "A-24")
    # ★★2026-11-05 02:45 删 (实测 板↔网表 parity 14 缺失 / 12 多余 的根因):
    #   这一行是"**器件自环**"写法 (net 名 = 器件名, 两侧都是它) ⇒ 导出器会把它当成
    #   **一个叫 J_USB_C 的网**, 并给 J_USB_C **分配 1..14 的占位脚号** ⇒
    #   ⇒ 而真正的 USB-IF 物理脚名 (A1/A4/A6/B12…) 走的是"合并脚名"路径 ⇒ 两套脚号对不上
    #   ⇒ ★**J_USB_C 的每一个物理脚都已经被真实网覆盖** (VBUS/GND/CC1/CC2/D±) ⇒ 这一行多余 ⇒ 删
    # add("P1", "J_USB_C", "J_USB_C", "J_USB_C", "J_USB_C",
    #     "USB-C 16p 插座 (demo 板 5V 输入 + USB 数据)", "CONN", "必装", "[推算]", "",
    #     "[J_USB_C] ★**demo 主板的 Type-C 电源入口** (老板 11-03 09:54: 没有整机, 没有镜脚, demo/主板用 Type-C 供电)", "A-24")
    # ---- USB 数据: SoM 的 USB_DRD1 (P1_92/P1_94) ↔ 板载 Type-C ----
    # ★★2026-11-04 19:5x 改 (串阻真串在中间): 原来这两行与 SoM 侧**同网** ⇒ ★**22Ω 被短接掉**
    #   ⇒ 改: Type-C 侧独立成网 NET_USB_D_P_TYPEC / NET_USB_D_N_TYPEC ⇒ 串阻跨两个网
    add("P1", "NET_USB_D_P_TYPEC", "R_SER_USB_D_P", "J_USB_C A6+B6", "R_SER_USB_D_P", "22Ω ±1%", "R",
        "必装", "[推算]", "",
        "[NET_USB_D_P_TYPEC] ★SoM USB2 (OTG1) D+ → 板载 Type-C: 串阻的 Type-C 侧 (★串阻必须真串在中间, 不能与 SoM 侧同网)", "A-24")
    add("P1", "NET_USB_D_N_TYPEC", "R_SER_USB_D_N", "J_USB_C A7+B7", "R_SER_USB_D_N", "22Ω ±1%", "R",
        "必装", "[推算]", "",
        "[NET_USB_D_N_TYPEC] ★SoM USB2 (OTG1) D- → 板载 Type-C: 串阻的 Type-C 侧", "A-24")
    # ★★2026-11-04 19:5x 补: J_CHG 的 pin7 (原跨铰链 VBUS_DET) 现在 demo 板不用了,
    #   但**座本身仍是 10p** ⇒ 必须把它声明成"预留/NC"行, 否则门禁会报"声明 10p / 实际 9p 断链"
    add("P9", "NC", "J_CHG pin7", "NC", "J_CHG", "预留 (NC)", "NET", "DNP", "[推算]", "",
        "[NC] ★2026-11-04: J_CHG pin7 原走跨铰链 VBUS_DET ⇒ demo 板改本地分压 ⇒ 本脚预留不接")

    # ---- VBUS_DET: 板载 Type-C 的 VBUS 分压 → SoM 的 USB_DRD1_VBUSDET (P1_100) ----
    # ★★2026-11-04 19:5x 修 (分压原本是坏的): 原来只有一行 (net=VBUS_DET_D, n1=R_VBUS_DET_D1, n2=R_VBUS_DET_D2)
    #   ⇒ ★**上臂与下臂被并联在同一个网** ⇒ 分压比恒为 1 ⇒ ★**VBUS 检测读 0V**;
    #   且 C_DET_VBUS_D 只挂 GND (1 条腿) ⇒ 滤波电容也缺一腿。
    #   ⇒ 正确: 上臂 R_VBUS_DET_D1 从 RAIL_DEMO_5V 到中点 VBUS_DET_D, 下臂 R_VBUS_DET_D2 从中点到 GND,
    #     电容 C_DET_VBUS_D 跨中点与地, SoM 的 USB_DRD1_VBUSDET (P1_100) 接中点。
    add("P1", "RAIL_DEMO_5V", "R_VBUS_DET_D1", "RAIL_DEMO_5V", "R_VBUS_DET_D1",
        "1M ±1% (上臂)", "R", "必装", "[推算]", "",
        "[VBUS_DET_D] ★demo 板: Type-C VBUS 在**主板本地**分压 (不再跨铰链) ⇒ 上臂 5V 侧", "A-24")
    add("P1", "VBUS_DET_D", "R_VBUS_DET_D1", "R_VBUS_DET_D2", "NET_VBUS_DET_D",
        "1M ±1% (上臂/下臂中点)", "R", "必装", "[推算]", "",
        "[VBUS_DET_D] ★分压中点 (上臂下臂相连 + 滤波电容 + SoM 检测脚)", "A-24")
    add("P1", "GND", "R_VBUS_DET_D2", "GND", "R_VBUS_DET_D2", "1M ±1% (下臂)", "R", "必装",
        "[推算]", "", "[VBUS_DET_D] 分压下臂 地端", "A-24")
    add("P1", "GND", "C_DET_VBUS_D", "GND", "C_DET_VBUS_D", "100nF ±10%", "C", "必装",
        "[推算]", "", "[VBUS_DET_D] ADC 滤波电容 地端", "A-24")
    add("P1", "VBUS_DET_D", "C_DET_VBUS_D", "VBUS_DET_D", "C_DET_VBUS_D", "100nF ±10%", "C", "必装",
        "[推算]", "", "[VBUS_DET_D] ADC 滤波电容 中点侧 (★原来缺这一腿 ⇒ 器件只有 1 个脚)", "A-24")
    # ★★2026-11-03 修: **ref 必须是器件名 "J_SOM_P1", 不能写节点串** ("J_SOM_P1 pin100" 会被
    #   生成器当成一个叫 "J_SOM_P1 pin100" 的器件 ⇒ 板上多出幽灵封装 + 一个假脚)
    add("P1", "VBUS_DET", soc_pin("USB_VBUS_DET"), "VBUS_DET_D", "J_SOM_P1",
        "1M+1M 分压 + 100nF", "NET", "必装", "[官方]", "",
        "[VBUS_DET] ★SoM 的 USB_DRD1_VBUSDET (P1_100) ← 板载 Type-C VBUS 分压 (demo 版: 检测在主板本地, 不跨铰链)",
        "B-07")

    # ---- ② ★F13: CARRIER_BOARD_EN ⇒ 负载开关 U_EN_SW ⇒ RAIL_BOARD_5V ----
    add("P1", "CARRIER_BOARD_EN", f"J_SOM_{car_en.split('_')[0]} pin{car_en.split('_')[1]}",
        "U_EN_SW ON", "J_SOM_P3", "EN 输出", "NET", "必装", "[官方]", "",
        f"[CARRIER_BOARD_EN] ★★F13 致命项: SoM 的 {car_en} (输出, 3.3V, 1K 上拉) ⇒ **底板上电许可**; "
        "Forlinx 原文: 底板早于核心板上电 ⇒ 通电瞬间电流过大 / 无法启动 / **可能对处理器造成不可逆损坏**", "A-24")
    add("P1", "CARRIER_BOARD_EN", "U_EN_SW ON", "CARRIER_BOARD_EN", "U_EN_SW",
        "EN 输入 (高=放行底板)", "NET", "必装", "[官方]", "",
        "[U_EN_SW] EN ← CARRIER_BOARD_EN ⇒ 主板各路只在 SoM 就绪后上电", "A-24")
    add("P1", "RAIL_DEMO_5V", "U_EN_SW VIN", "RAIL_DEMO_5V", "U_EN_SW", "5V 输入", "NET",
        "必装", "[官方]", "", "[U_EN_SW] IN = 5V (Type-C 直供)", "A-24")
    add("P1", "RAIL_BOARD_5V", "U_EN_SW VOUT", "RAIL_BOARD_5V", "U_EN_SW",
        "5V 输出 (受 CARRIER_BOARD_EN 门控)", "NET", "必装", "[官方]", "",
        "[RAIL_BOARD_5V] ★**底板所有 3.3V/5V 支路都挂这条** (不是 SYS) ⇒ 这就是 F13 的落法", "A-24")
    add("P1", "GND", "U_EN_SW GND", "GND", "U_EN_SW", "GND", "NET", "必装", "[官方]", "",
        "[U_EN_SW] 地", "A-24")

    # ---- ③ SoM 自己的供电 VCC_DCIN (7 脚并联) —— 直供, 不受门控 ----
    # ★★★2026-11-05 11:10 **修 BUG: 这 7 个脚原来落在**独立网** `RAIL_SOM_DCIN` 上**
    #   ★**实测后果 (布线分析发现的, 不是猜的)**: 官方板 DRC 里 `RAIL_SOM_DCIN` 7 个 BTB 脚**全部未连接**
    #     ⇒ ★**SoM 的电源输入在板上是孤岛** ⇒ ★**即使布线全部完成, SoM 也上不了电!**
    #   ★**根因**: 这行的 net 字段写的是 `RAIL_SOM_DCIN`, 而 node2 写的是 `RAIL_DEMO_5V`
    #     ⇒ ★**两个字段自相矛盾** ⇒ 生成器按 net 字段建网 ⇒ 就多出一个孤岛网
    #   ★**正确**: 备注写的是"直供 5V, 不经过 U_EN_SW" ⇒ ⇒ **这 7 个脚就是 RAIL_DEMO_5V 的一部分**
    #   ⇒ ⇒ ★**net 字段改成 RAIL_DEMO_5V** (与 node2 和设计意图一致) ⇒ 网表/原理图/PCB 全链自动跟着对
    for _pn in dcin:
        _c, _n = _pn.split("_")
        add("P1", "RAIL_DEMO_5V", f"J_SOM_{_c} pin{_n}", "RAIL_DEMO_5V", f"J_SOM_{_c}",
            "5-13V 输入 (SoM 侧)", "NET", "必装", "[官方]", "",
            f"[VCC_DCIN] ★SoM 自己的电源输入 ({_pn}; 手册 §2.4.2 DC 5~13V; 7 脚并联载流) "
            "⇒ **直供 5V (与 USB-C 5V 同网), 不经过 U_EN_SW** (否则 SoM 自己起不来)", "A-24")


# --------------------------------------------------------------- 写盘 + 门禁
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()
    if not os.path.exists(SPEC):
        print(f"❌ 缺规格: {SPEC}", file=sys.stderr)
        return 2
    spec = json.load(open(SPEC, encoding="utf-8"))
    by_id = {c["id"]: c for c in spec["connections"]}

    build_p1(by_id, spec)
    build_p2(by_id, spec)
    build_p3(by_id, spec)
    build_p4(by_id, spec)
    build_p5(by_id, spec)
    build_p6(by_id, spec)
    build_p7(by_id, spec)
    build_p8(by_id, spec)
    build_p9(by_id, spec)
    # ★★A2 段: SoM 的 4 组 100pin BTB 座 + F13 电源使能 + SoM 自己的 VCC_DCIN + demo 板 Type-C
    build_a2_som(by_id, spec)
    n_p10 = build_p10_json()

    # ★2026-11-03: 命名脚 → 真实脚号 (查 HW/PCB/pinout_footprint.json)
    _apply_pin_maps(ROWS)

    # ---- 板级归属 (2026-10-27 V1.1 新增): 充电板 / 主 PCB / 跨铰链 ----
    for r in ROWS:
        r["board"] = board_for(r)

    # ---- ★V1.4 (2026-10-27 09:2x): 标出**器件清单行** (net == ref 或 HINGE_* 开头) ----
    #   这些行是"器件登记"而不是一根连接 (例: net=CONN_CAM, node=CONN_CAM) ·
    #   混进 .net 导出会让同一物理脚出现在多个 net · KiCad 判 pin 冲突。
    for r in ROWS:
        if r["net"] == r["ref"] or r["net"].startswith("HINGE_"):
            r["note"] = "[INVENTORY] " + (r["note"] or "")

    # ---- ★V1.4 (2026-10-27 09:2x): 跨铰链连接器的**同一物理脚**在两侧是同一个节点 · 网名必须一致 ----
    #   ① USB_D_P_CHG / USB_D_N_CHG · 合并进 USB_D_P / USB_D_N (穿铰链连接器的一根线是**一个**节点)
    #   ② GND_CHG · 合并进 GND (充电回流脚本来就是地, 单独成网会让同一物理脚落两个网)
    for r in ROWS:
        if r["net"] == "USB_D_P_CHG":
            r["net"] = "USB_D_P"
        elif r["net"] == "USB_D_N_CHG":
            r["net"] = "USB_D_N"
        elif r["net"] == "GND_CHG":
            r["net"] = "GND"

    # ---- ★F6 修正 (2026-10-27 09:1x, hw-lead ISS-088 复审发现): ----
    #   原来"信号网"里混进了 GND 端 (例: net=VBUS_DET 的一行是 R_VBUS_DET_2 · GND)。
    #   一行 = 一根连接, net 名必须是**这根连接所连的那个电气节点**; 一端是 GND ⇒ 这行属于 GND 网。
    #   否则 KiCad 导出时 VBUS_DET 会和 GND 并成一个网 · **分压电阻被短接, ADC 永远读 0V**。
    # ★V1.6 撤掉 F6 的"见 GND 就改网名"规则: 那条规则把**器件信号侧**的行也改成了 GND 网
    #   (例: TS_BAT 的 R_TS_PULL 一行) · 器件一脚同网一脚悬空 · 导出后分压链断。
    #   正确做法: 保持行的网名 = 这根线的网, 由导出器按"器件跨的两个网"来定脚 (见 gen_kicad_net.py)。
    # ★V1.6 新增: **把"临时线名"归一到它的源节点** (行里有 RAIL_*/NET_* 别名端时, 行网名就是那根线的别名)
    for r in ROWS:
        alias_end = None
        for nd in (r["node1"], r["node2"]):
            if nd.startswith("RAIL_") or nd.startswith("NET_"):
                alias_end = nd
        if alias_end and r["net"].endswith("_RAW"):
            r["net"] = alias_end[5:] if alias_end.startswith("RAIL_") else alias_end[4:]
            r["note"] = (r["note"] or "") + f" [V1.6: 临时线名 {r['net']} 已归一到源节点]"

    # ---- 出口自检 1: net 名必须是合法标识符 (无 + - 空格等) ----
    bad_nets = sorted({r["net"] for r in ROWS if not NET_RE.match(r["net"] or "")})
    if bad_nets:
        print(f"❌ net 名不合法 (含非标识符字符): {bad_nets}", file=sys.stderr)
        return 3
    # ---- 出口自检 2: 每行两端齐全 + 每行有位号 ----
    bad_rows = [r for r in ROWS if not r["node1"] or not r["node2"] or not r["ref"]]
    if bad_rows:
        print(f"❌ {len(bad_rows)} 行缺 node/ref: {bad_rows[:3]}", file=sys.stderr)
        return 3
    # ---- 出口自检 3: 所有 TBD 编号落在 TBD-01..TBD-13 ----
    legal = {f"TBD-{i:02d}" for i in range(1, len(spec["undrawable"]) + 1)}
    bad_tbd = sorted({r["tbd"] for r in ROWS if r["tbd"] and r["tbd"] not in legal})
    if bad_tbd:
        print(f"❌ 非法 TBD 编号: {bad_tbd}", file=sys.stderr)
        return 3

    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in ROWS:
            w.writerow(r)

    per_page: dict[str, int] = {}
    for r in ROWS:
        per_page[r["page"]] = per_page.get(r["page"], 0) + 1
    covered = len({r["conn_id"] for r in ROWS if r["conn_id"]})
    print(f"✅ 已生成 {OUT}: {len(ROWS)} 行, 覆盖 {covered} 条连接"
          + (f" (含 P10 充电板页 {n_p10} 行)" if n_p10 else " (★P10 充电板页数据未到, 该页为空)"))
    for p in PAGES:
        print(f"   {p} {PAGES[p]:<42} {per_page.get(p, 0):>4} 行")
    if args.summary:
        types: dict[str, int] = {}
        for r in ROWS:
            types[r["type"]] = types.get(r["type"], 0) + 1
        print(f"   器件类型: {dict(sorted(types.items(), key=lambda x: -x[1]))}")
        print(f"   必装 {sum(1 for r in ROWS if r['dnp'] == '必装')} / "
              f"DNP {sum(1 for r in ROWS if r['dnp'] == 'DNP')} / "
              f"可选 {sum(1 for r in ROWS if r['dnp'] == '可选')}")
        tbd_used = sorted({r["tbd"] for r in ROWS if r["tbd"]})
        print(f"   TBD 使用: {len(tbd_used)} 个 · {tbd_used}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
