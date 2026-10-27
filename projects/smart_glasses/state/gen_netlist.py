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
  ② SoC 侧球位号一律 `SoC[TBD-01].<信号>` 占位 (原厂引脚表/球位图未回) · **0 编造球位号**
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
        "board"]

# ★板级归属 (2026-10-27 V1.1 新增列 board) —— 充电板在镜框 / 主 PCB 在镜脚, 两者跨铰链
#   CHG_BOARD = 充电板 (镜框): Type-C + 充电链 + 电池
#   MAIN_PCB  = 主 PCB (镜脚): SoC + 全部外设 + 保护/滤波件
#   HINGE     = 跨铰链界面本体 (连接器 / 跨铰链那一段)
BOARD_CHG = "CHG_BOARD"
BOARD_MAIN = "MAIN_PCB"
BOARD_HINGE = "HINGE"
LEGAL_BOARD = {BOARD_CHG, BOARD_MAIN, BOARD_HINGE}

# 跨铰链界面上的 4 个连接器 (全部 HINGE)
HINGE_REFS = {"J_CHG", "CONN_USB", "CONN_CAM", "CONN_LIGHT"}
# 充电板 (镜框) 上的器件 —— ★V1.2: 电池 + 电池保护 IC + 2×MOS 移到**镜脚主 PCB** (MECH 体积硬约束)
CHG_BOARD_REFS = {
    "J_TYPE_C", "D_ESD_TC", "FB_VBUS", "C_VBUS_IN", "C_VBUS_OUT", "U_CHG",
    "TP_VBUS", "R_CC1", "R_CC2", "R_TS_TOP",
    "NET_VBUS_5V_CHG",
    # ★V1.6: P10 充电板页新增的件 (BQ25896 外围) 全在镜框充电板
    "R_PSEL", "R_CE", "R_OTG", "R_PU_SCL", "R_PU_SDA", "R_PU_INT", "R_STAR_PGND",
    "C_VBUS_IC", "C_PMID", "C_BST", "C_BAT", "C_SYS", "L_CHG", "D_TVS_VBUS", "TP_TS",
    # ★它发现的缺陷: VBUS_DET 的 1M+1M 分压物理上必须在**充电板**
    #   (充电板 VBUS 不过铰链到主板 → 分压放在主板 = 采不到电)
    "R_VBUS_DET_1", "R_VBUS_DET_2",
}

PAGES = {
    "P1": "电源树 (13 电源域 + 充电链)",
    "P2": "SoC 主控 (低速控制 / ADC / I2C / FSIN)",
    "P3": "启动存储 (焊盘位 + 串阻位, 不画存储芯片)",
    "P4": "显示双出口 (DSI 原生 / 桥接 互斥 0Ω 位)",
    "P5": "MIPI-CSI 传感器 (CONN_CAM 40p 跨铰链)",
    "P6": "高速差分与连接器 (DP_TX / USB / Type-C)",
    "P7": "板级接口与测试点 (TP + 按键 + LED + ID 跳线)",
    "P8": "时钟 · 复位 · 调试 (XTAL / RESET / BOOT / JTAG / UART)",
    "P9": "跨铰链界面 (4 组跨铰链通道 + 保护/滤波件 + 板级归属)",
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
        if re.search(r"J_CHG|CONN_USB|CONN_CAM|CONN_LIGHT", blob):
            return BOARD_HINGE
        if ref in ("RAIL_VBUS_5V", "NET_VBUS_5V_CHG"):
            return BOARD_CHG
        # ★V1.5 修正: RAIL_BAT / RAIL_SYS / R_NTC_BAT 都在**镜脚** (电池在镜脚, V1.2 裁决) · MAIN_PCB
        return BOARD_MAIN
    if re.search(r"J_TYPE_C|U_CHG", blob):
        return BOARD_CHG
    return BOARD_MAIN


ROWS: list[dict] = []


def add(page, net, node1, node2, ref, value, typ, dnp, ev, tbd, note, cid=""):
    ROWS.append(dict(page=page, net=net, node1=node1, node2=node2, ref=ref, value=value, type=typ,
                     dnp=dnp, evidence=ev, tbd=tbd, note=note, conn_id=cid))


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
    for pn in (9, 10):
        add("P1", "HINGE_RSV", f"J_CHG pin{pn}", f"J_CHG pin{pn}", "J_CHG", "预留 (不装)",
            "NET", "DNP", "[推算]", "",
            f"[HINGE_RSV] J_CHG pin{pn} 预留位 (★V1.5 裁决: 充电 IC 的 I2C **不跨铰链** —— "
            f"充电电流靠 R_ILIM 硬件限流, 状态靠 CHG_STAT/PWR_GOOD GPIO 兜底; 将来若要在线配置 "
            f"充电电流/截止电压, 把这 2 个脚用上即可, 不用改板)", "C-02")
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
        "必装", "[推算]", "",
        "[BAT_PROT_CELL2] 第 2 只保护 MOS · 电池保护 IC (BQ2970) 的 B+ 脚; 参数同 Q1", "C-03")
    add("P1", "BAT_GATE", "U_BATPROT GATE", "Q1 GATE", "U_BATPROT", "BQ2970", "IC",
        "必装", "[官方]", "",
        "[BAT_GATE] ★F2 修正: **两管栅极由 BQ2970 同驱** (原来完全没有栅极连接 · MOS 永远不导通/不受控); "
        "栅极网络按 BQ2970 数据手册确认是否需要上拉", "C-03")
    add("P1", "BAT_GATE", "Q1 GATE", "Q2 GATE", "Q1", "[待选型] N-MOS", "SW",
        "必装", "[推算]", "",
        "[BAT_GATE] 两管共栅 (back-to-back 接法, 按 BQ2970 数据手册确认体二极管方向)", "C-03")
    add("P1", "BAT_CELL_N", "BT_432243 B-", "U_BATPROT B-", "BT_432243", "432243 3.7V ≥420mAh",
        "CONN", "必装", "[推算]", "",
        "[BAT_CELL_N] ★F2 修正: **电芯负极 · BQ2970 的 B- 脚** (原来电芯只有一个端子 · 电池回路不闭合)", "C-03")
    add("P1", "SYS", "RAIL_SYS", "U_BATPROT", "RAIL_SYS", "3.0-4.2V", "RAIL",
        "必装", "[推算]", "",
        "电源域: 目标 3.0-4.2V / 最大电流 0.55A (330mA×1.5 + 瞬态); **R-F1 裁决: SYS 下限抬到 3.5V**; "
        "★V1.2: **SYS 在镜脚本地产生** (电池在镜脚 · 电池保护后就是 SYS) · **SYS 不过铰链** "
        "(跨铰链的只有充电电流 1.0-1.5A); SoC 侧球位号 TBD-01", "C-02")
    add("P1", "BAT_CHG", "J_CHG", "J_CHG pin1", "J_CHG", "1×10p@0.5mm 排线座 (充电板↔主 PCB, 跨铰链载流)",
        "CONN", "必装", "[推算]", "",
        "[SYS] ★V1.5 定稿 pin map (1×10p@0.5mm): pin1/pin2=BAT_CHG (充电电流**双 pin 并联**), "
        "pin3/pin4=GND (回流双 pin), pin5=CHG_STAT, pin6=PWR_GOOD, pin7=VBUS_DET, "
        "pin8=**TS** (电池 NTC 在镜脚, TS 跨铰链), pin9/10=预留 (充电 IC I2C 不跨铰链); "
        "★BAT_DET 不跨铰链 (电池在镜脚本地检测); 型号/载流待结构复核 (ISS-091 算压降发热); "
        "★pin 编号为**本版自拟**", "C-02")

    # ---- ★V1.1 补画 1: 电池 NTC 接 BQ25896 的 TS 脚 (硬件停充, 安全项, V1 漏画) ----
    add("P1", "TS_BAT", "U_CHG pin11", "R_NTC_BAT", "NET_TS_BAT", "单端", "NET", "必装",
        "[官方]", "",
        "[TS_BAT] ★电池温度检测: 103AT NTC 接 BQ25896 的 TS 脚 (过温/欠温时**硬件直接停充**; 分压网络按 datasheet 三件式) "
        "(不依赖 SoC, 属安全项); 与 P2 的 SoC 侧数字温度计 U_TEMP 是两回事, 不能互相替代", "C-01")
    add("P1", "TS_BAT", "R_NTC_BAT", "GND", "R_NTC_BAT", "103AT NTC ±1% (贴电芯, 另一端接电芯负极=系统 GND)",
        "R", "必装", "[官方]", "",
        "[TS_BAT] ★V1.5 修正: NTC **贴电芯 ⇒ 在镜脚** (V1.2 电池搬镜脚后), 而 BQ25896 的 TS 脚在镜框充电板 "
        "· **TS 必须跨铰链** (J_CHG pin8, 高阻无电流); NTC 按 BQ25896 datasheet 取 **103AT** "
        "(与 30.31k 并联构成温度检测网络); ★V1.6 修正: NTC 另一端按 datasheet 三件式接 **GND** (电芯负极侧), 原来接电芯正极 = 与分压公式不符", "C-01")
    add("P1", "TS_BAT", "R_TS_PULL", "GND", "R_TS_PULL", "30.31k ±1%", "R", "必装", "[官方]", "",
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
    add("P1", "TS_BAT", "R_TS_TOP", "U_CHG pin22", "R_TS_TOP", "5.24k ±1% (RT1: REGN 到 TS)",
        "R", "必装", "[官方]", "",
        "[TS_BAT] ★V1.5 补画: **RT1 5.24k (REGN 到 TS)** —— BQ25896 温度检测是 RT1/RT2/NTC 三件式, "
        "原来只画了 NTC + 10k 下拉 = 分压比完全不对 (datasheet: 0°C·73.25%, 60°C·34.375%)", "C-01")

    # ---- ★V1.5 补画: R_ILIM 硬件限流 (BQ25896 的 IINLIM **复位默认 2048mA**) ----
    #   不装这颗电阻 · 铰链段可能被灌 ~1.68A (ICHG≈0.822×IIN) · 铰链发热 + 压降失控。
    #   装 300Ω · IINMAX = KILIM/RILIM ≈ 1.07-1.30A · ICHG ≈ 0.88-1.07A (ISS-091 核算输入)
    #   ⇒ 换料不换板: 若结构核算说铰链只吃 1.0A, 改 390Ω · ICHG 0.67-0.82A
    add("P1", "IINLIM", "U_CHG pin10", "R_ILIM", "R_ILIM", "300Ω ±1% (IINMAX ≈1.07-1.30A)",
        "R", "必装", "[官方]", "",
        "[IINLIM] ★V1.5 补画: **输入限流电阻** —— BQ25896 的 IINLIM 复位默认 **2048mA** [官方], "
        "不装 = 铰链段被灌 ~1.68A (ICHG≈0.822×IIN), 发热/压降失控; 300Ω 给 ICHG≈0.88-1.07A; "
        "按 ISS-091 结构结论可换 390Ω (换料不换板)", "C-01")
    add("P1", "GND", "R_ILIM", "GND", "R_ILIM", "300Ω ±1% (IINMAX ≈1.07-1.30A)", "R", "必装",
        "[官方]", "",
        "[IINLIM] 限流电阻 另一端接地 (IINLIM 对地设定输入电流上限)")

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
        ("U_DCDC_VCORE", "V_CORE", "TPS62130A", "DC-DC (3A) 供 V_CORE", "必装", "[官方]", "TBD-02", "C-04"),
        ("U_DCDC_VIO", "V_SOC_IO", "TPS62130A", "DC-DC (3A) 供 V_SOC_IO", "必装", "[官方]", "TBD-02", "C-05"),
        ("U_LDO_S28", "SENSOR_AVDD", "TPS7A20-28", "LDO 供 SENSOR_AVDD (2.8V/30mA)", "必装", "[官方]", "", "C-06"),
        ("U_LDO_S18", "SENSOR_VDD_IO", "TPS7A20-18", "LDO 供 SENSOR_VDD_IO (1.8V/30mA)", "必装", "[官方]", "", "C-07"),
        ("U_LDO_S12", "SENSOR_CORE", "TPS7A20-12", "LDO 供 SENSOR_CORE (1.2V/50mA)", "必装", "[官方]", "", "C-08"),
        ("U_LDO_L33", "LIGHT_3V3", "TPS7A20-33", "LDO 供 LIGHT_3V3 (3.3V/150mA)", "必装", "[推算]", "TBD-02", "C-09"),
        ("U_LDO_L18", "LIGHT_1V8", "TPS7A20-18", "LDO 供 LIGHT_1V8 (1.8V/50mA)", "DNP", "[推算]", "TBD-02", "C-10"),
        ("U_LDO_IO33", "VDD_3V3_IO", "TPS7A20-33", "LDO 供 VDD_3V3_IO (3.3V/200mA)", "必装", "[推算]", "", ""),
        ("U_LDO_IO18", "VDD_1V8_IO", "TPS7A20-18", "LDO 供 VDD_1V8_IO (1.8V/100mA)", "必装", "[推算]", "", ""),
    ]
    for ref, rail, part, desc, dnp, ev, tbd, cid in power_ics:
        r = rails.get(rail, {})
        add("P1", rail, f"RAIL_{rail}", ref, f"RAIL_{rail}", r.get("volt", ""), "RAIL", dnp,
            ev, tbd,
            f"电源域: 目标 {r.get('volt','')} / 最大电流 {r.get('max_i','')}; IC {part}; "
            f"SoC 侧球位号 TBD-01", cid)
        # ★V1.1 补画 3: 输入侧连接 (V1 只画了供电器件与去耦, **没画 IC 输入脚接哪条轨** · ERC B1 "来源" 缺失)
        add("P1", "SYS_PCB", "RAIL_SYS", ref, "RAIL_SYS", "3.5-4.2V (R-F1 抬下限后)",
            "NET", dnp, "[推算]", "",
            f"[{rail}] {ref} 输入脚供电 (SYS 镜脚本地产生, 电池保护后); "
            f"LDO 输入下限 1.6V / DC-DC 输入 3-17V [官方]",
            cid)
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
    add("P1", "LIGHT_5V", "RAIL_LIGHT_5V", "CONN_LIGHT pin21", "RAIL_LIGHT_5V", "5.0V", "RAIL",
        "DNP", "[推算]", "TBD-02",
        "电源域: 目标 [待 JBD] / 最大电流 50mA; 供电方式 [待 JBD] 确认 (VBUS 直供 或 升压); "
        "SoC 侧球位号 TBD-01", "C-10")
    add("P1", "LIGHT_5V", "RAIL_LIGHT_5V", "D_ESD_LIGHT", "D_ESD_LIGHT", "ESD 阵列 [待选型]", "D",
        "DNP", "[推算]", "",
        "[LIGHT_5V] 光机 5V 供电口 ESD 阵列位 (跨铰链, 随光机接口确认后定)", "C-10")
    add("P1", "GND", "D_ESD_LIGHT", "GND", "D_ESD_LIGHT", "ESD 阵列 [待选型]", "D",
        "DNP", "[推算]", "", "[LIGHT_5V] 光机侧 ESD 地端", "C-10")
    # ★V1.4: ESD 阵列的**地脚**补齐 (原来只有 I/O 脚, 阵列没接地 · 保护不生效)
    for dref, note in (("D_ESD_TC", "Type-C 入口 ESD 阵列 地脚"),
                       ("D_ESD_USB", "跨铰链 USB ESD 阵列 地脚"),
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
    conn_row(by_id, "B-01", "P2", "I2C_A_SCL", "SoC[TBD-01].I2C_A_SCL", "R_PU_I2CA_SCL",
             "NET_I2C_A_SCL")
    conn_row(by_id, "B-02", "P2", "I2C_A_SDA", "SoC[TBD-01].I2C_A_SDA", "R_PU_I2CA_SDA",
             "NET_I2C_A_SDA")
    add("P2", "VDD_3V3_IO", "R_PU_I2CA_SCL", "RAIL_VDD_3V3_IO", "R_PU_I2CA_SCL", "4.7k ±1%",
        "R", "必装", "[推算]", "",
        "[VDD_3V3_IO] I2C_A 上拉 (规格: 4.7k 到 3.3V; 灌 702µA, t_r=2.38µs@100pF)", "B-01")
    add("P2", "VDD_3V3_IO", "R_PU_I2CA_SDA", "RAIL_VDD_3V3_IO", "R_PU_I2CA_SDA", "4.7k ±1%",
        "R", "必装", "[推算]", "",
        "[VDD_3V3_IO] I2C_A 上拉", "B-02")
    add("P2", "I2C_A_SCL", "CONN_CAM pin13", "NET_I2C_A_SCL", "NET_I2C_A_SCL",
        "上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF)", "NET", "必装", "[推算]", "",
        "[I2C_A_SCL] 附加节点 (同 net)", "B-01")
    add("P2", "I2C_A_SDA", "CONN_CAM pin14", "NET_I2C_A_SDA", "NET_I2C_A_SDA",
        "上拉 4.7k 到 3.3V", "NET", "必装", "[推算]", "",
        "[I2C_A_SDA] 附加节点 (同 net)", "B-02")
    # NTC / 温度检测位: 规格 B-01 把 "NTC" 挂在 I2C_A 上, 但没说是裸 NTC 分压还是数字温度计
    # ★V1.1 定型 (ISS-086): 规格 B-01 的 "NTC 挂 I2C" 只能是**数字温度计** (裸 NTC 是分压不是 I2C)
    add("P2", "I2C_A_SCL", "U_TEMP pin2", "NET_I2C_A_SCL", "U_TEMP",
        "TMP117 数字温度计 (I2C 地址 0x48, ±0.1°C max, 16bit)", "IC", "必装", "[官方]", "",
        "[I2C_A_SCL] ★V1.1 定型: 选 TI TMP117 [官方 ti.com/product/TMP117] (1.7-5.5V 供电, 5µA max, "
        "WSON-2 2×2mm); I2C_A 从设备地址 0x48, 与 sensor 0x36 / 桥接 0x50 / 充电 IC 0x12 / "
        "光机 0x72 都不冲突; 若原厂坚持裸 NTC, 改 ADC 分压位 (不换板)", "B-01")
    add("P2", "I2C_A_SDA", "U_TEMP pin1", "NET_I2C_A_SDA", "U_TEMP",
        "TMP117 数字温度计", "IC", "必装", "[官方]", "", "[I2C_A_SDA] TMP117 SDA", "B-01")
    add("P2", "VDD_3V3_IO", "U_TEMP pin3", "RAIL_VDD_3V3_IO", "U_TEMP",
        "TMP117 数字温度计", "IC", "必装", "[官方]", "", "[I2C_A_SCL] TMP117 供电 (3.3V, 5µA max)",
        "B-01")
    add("P2", "GND", "U_TEMP pin4", "GND", "U_TEMP", "TMP117 数字温度计", "IC", "必装",
        "[官方]", "", "[I2C_A_SCL] TMP117 地脚", "B-01")
    add("P2", "VDD_3V3_IO", "C_TEMP", "RAIL_VDD_3V3_IO", "C_TEMP", "100nF ±10%", "C", "必装",
        "[推算]", "", "[I2C_A_SCL] TMP117 就近去耦", "B-01")
    add("P2", "GND", "C_TEMP", "GND", "C_TEMP", "100nF ±10%", "C", "必装", "[推算]", "",
        "[I2C_A_SCL] TMP117 去耦 地端", "B-01")

    # ---- VBUS_DET / BAT_DET (分压 + RC 到 ADC) ----
    for cid, src, srcnode, tp, cap in (
            ("B-07", "VBUS_DET", "RAIL_VBUS_5V", "TP_VBUS", "C_DET_VBUS"),
            ("B-08", "BAT_DET", "RAIL_BAT", "TP_BAT", "C_DET_BAT")):
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
        add("P2", src, f"SoC[TBD-01].{src}", f"NET_{src}", f"NET_{src}",
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
        conn_row(by_id, cid, "P7", f"ID_DETECT_{bit}", f"SoC[TBD-01].ID{bit}",
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
        add("P3", sig, f"SoC[TBD-01].{sig}", f"R_SER_{sig}", f"NET_{sig}", "0Ω (串阻位)",
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
    ("CK", "DSI_D0_CK_P", "DSI_D0_CK_N", "A-13", "A-14",
     "DSI_TX_CK_P", "DSI_TX_CK_N", 1, 2, "必装", False),
    ("D0", "DSI_D0_D0_P", "DSI_D0_D0_N", "A-15", "A-16",
     "DSI_TX_D0_P", "DSI_TX_D0_N", 3, 4, "必装", False),
    ("D1", "DSI_D0_D1_P", "DSI_D0_D1_N", "A-17", "A-18",
     "DSI_TX_D1_P", "DSI_TX_D1_N", 5, 6, "必装", False),
    ("D2", "DSI_D0_D2_P", "DSI_D0_D2_N", "A-19", "A-20",
     "DSI_TX_D2_P", "DSI_TX_D2_N", 7, 8, "DNP", True),
    ("D3", "DSI_D0_D3_P", "DSI_D0_D3_N", "A-20", "A-20",
     "DSI_TX_D3_P", "DSI_TX_D3_N", 9, 10, "DNP", True),
]
BR_LANES = [  # 方案B 桥接位 (只有 2-lane: CK/D0/D1) —— 规格 display_select 只给了这三条
    # lane, CONN_LIGHT pin P/N, U_BRIDGE 输出脚 P/N
    ("CK", 11, 12, 1, 2), ("D0", 13, 14, 3, 4), ("D1", 15, 16, 5, 6),
]


def build_p4(by_id, spec):
    for lane, netP, netN, cidP, cidN, srcP, srcN, pinP, pinN, sel_dnp, term in DSI_LANES:
        for pol, net, cid, src, pin in (("P", netP, cidP, srcP, pinP), ("N", netN, cidN, srcN, pinN)):
            rsel = f"R_SEL_{lane}_{pol}"
            conn_row(by_id, cid, "P4", f"{net}_SRC", f"SoC[TBD-01].{src}", rsel, f"NET_{net}_SRC")
            add("P4", net, rsel, f"CONN_LIGHT pin{pin}", rsel, "0Ω", "R", sel_dnp, "[官方]",
                "TBD-04",
                (f"[{net}] 显示双出口选择位 (方案A 装 0Ω / 方案B DNP) — ★规格位 R_SEL_* 必须拆 "
                 f"P/N 两颗, 单颗 0Ω 会把差分对短接") if sel_dnp == "必装" else
                (f"[{net}] 4-lane 预留位 (2-lane 不够时再装) — ★规格位 R_SEL_* 必须拆 P/N 两颗, "
                 f"单颗 0Ω 会把差分对短接"))
            if term:
                rt = f"R_TERM_{net}"
                add("P4", f"{net}_SRC", rt, f"NET_{net}_SRC", rt, "100Ω ±1%", "R", "DNP",
                    "[推算]", "",
                    f"[{net}_SRC] 未用差分对 100Ω 对地端接 (0402, 手工可补装)")
                add("P4", "GND", rt, "GND", rt, "100Ω ±1%", "R", "DNP", "[推算]", "",
                    f"未用差分对 100Ω 对地端接 ({lane}_{pol} 才装)")
    # ---- 方案B 桥接位 (与 R_SEL_* 互斥) ----
    for lane, pinP, pinN, brP, brN in BR_LANES:
        for pol, pin, brpin in (("P", pinP, brP), ("N", pinN, brN)):
            br = f"BR_{lane}_{pol}"
            add("P4", f"DSI_BR_{lane}_{pol}_SRC", f"U_BRIDGE pin{brpin}", br, br,
                "0Ω", "R", "DNP", "[官方]", "TBD-04",
                f"[DSI_BR_{lane}_{pol}_SRC] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — "
                f"★与 R_SEL_* 互斥, 不得同装")
            add("P4", f"DSI_BR_{lane}_{pol}", br, f"CONN_LIGHT pin{pin}", br, "0Ω", "R", "DNP",
                "[官方]", "TBD-04",
                f"[DSI_BR_{lane}_{pol}] 方案B 桥接位 (方案A DNP / 方案B 装 0Ω) — "
                f"★与 R_SEL_* 互斥, 不得同装")
    add("P4", "DSI_BR", "U_BRIDGE", "DSI_BR_CK_P_SRC", "U_BRIDGE",
        "[待选型] DP1.4 TX · MIPI DSI TX 桥接芯片 (方案B 专用; 与 P6 同一位)", "IC", "DNP",
        "[推算]", "TBD-04",
        "[DSI_BR] 方案B 才需要的桥接芯片位 (接口类型/功耗/封装随原厂 TBD-04 结论定; "
        "本版只留位不选型)")
    # ---- DSI DDC (I2C_B) ----
    conn_row(by_id, "B-03", "P4", "I2C_B_SCL", "SoC[TBD-01].I2C_B_SCL", "R_PU_I2CB_SCL",
             "NET_I2C_B_SCL")
    conn_row(by_id, "B-04", "P4", "I2C_B_SDA", "SoC[TBD-01].I2C_B_SDA", "R_PU_I2CB_SDA",
             "NET_I2C_B_SDA")
    add("P4", "I2C_B_SCL", "CONN_LIGHT pin17", "NET_I2C_B_SCL", "NET_I2C_B_SCL",
        "上拉 4.7k, 放主板侧", "NET", "必装", "[推算]", "TBD-04",
        "[I2C_B_SCL] 附加节点 (同 net)", "B-03")
    add("P4", "I2C_B_SDA", "CONN_LIGHT pin18", "NET_I2C_B_SDA", "NET_I2C_B_SDA",
        "上拉 4.7k, 放主板侧", "NET", "必装", "[推算]", "TBD-04",
        "[I2C_B_SDA] 附加节点 (同 net)", "B-04")
    add("P4", "VDD_3V3_IO", "R_PU_I2CB_SCL", "RAIL_VDD_3V3_IO", "R_PU_I2CB_SCL", "4.7k ±1%",
        "R", "必装", "[推算]", "", "[VDD_3V3_IO] DSI DDC 上拉 (放主板侧)", "B-03")
    add("P4", "VDD_3V3_IO", "R_PU_I2CB_SDA", "RAIL_VDD_3V3_IO", "R_PU_I2CB_SDA", "4.7k ±1%",
        "R", "必装", "[推算]", "", "[VDD_3V3_IO] DSI DDC 上拉", "B-04")
    # ---- 光机连接器 ----
    add("P4", "CONN_LIGHT", "CONN_LIGHT", "CONN_LIGHT pin1", "CONN_LIGHT",
        "1×22p@0.5mm 光机连接器 (板对板/FFC, 待 JBD 确认; 末脚 GND = 差分回流)", "CONN", "必装", "[待JBD]", "TBD-04",
        "[CONN_LIGHT] 光机↔主板连接器; pin3/4=DSI_CK, 5/6=DSI_D0, 7/8=DSI_D1, 9/10=DSI_D2, "
        "11/12=DSI_D3, 13/14=DDC, 21..26=桥接方案 B 差分, 27/28/29=3V3/1V8/5V; "
        "型号/间距/pin 数待 JBD 开发套件接口定义; ★pin 编号为**本版自拟**, 非 JBD 给定")


# ------------------------------------------------------- P5 MIPI-CSI 传感器
CSI_LANES = [
    # lane, sig_P, sig_N, cid_P, cid_N, CONN_CAM pin P/N, dnp, 对地端接
    ("CK", "CSI_D0_CK_P", "CSI_D0_CK_N", "A-01", "A-02", 1, 2, "必装", False),
    ("D0", "CSI_D0_D0_P", "CSI_D0_D0_N", "A-03", "A-04", 3, 4, "必装", False),
    ("D1", "CSI_D0_D1_P", "CSI_D0_D1_N", "A-05", "A-06", 5, 6, "必装", False),
    ("D2", "CSI_D0_D2_P", "CSI_D0_D2_N", "A-07", "A-08", 7, 8, "DNP", True),
    ("D3", "CSI_D0_D3_P", "CSI_D0_D3_N", "A-09", "A-10", 9, 10, "DNP", True),
]


def build_p5(by_id, spec):
    for lane, sigP, sigN, cidP, cidN, pinP, pinN, dnp, term in CSI_LANES:
        for pol, sig, cid, pin in (("P", sigP, cidP, pinP), ("N", sigN, cidN, pinN)):
            cac = f"C_AC_{sig}"
            conn_row(by_id, cid, "P5", f"{sig}_SRC", f"SoC[TBD-01].{sig}", cac, f"NET_{sig}_SRC")
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
    conn_row(by_id, "A-11", "P5", "CSI_MCLK_SRC", "SoC[TBD-01].CSI_MCLK", "R_SER_CSI_MCLK",
             "NET_CSI_MCLK_SRC")
    add("P5", "CSI_MCLK", "R_SER_CSI_MCLK", "CONN_CAM pin11", "R_SER_CSI_MCLK", "[待原厂]",
        "R", "必装", "[待原厂]", "TBD-03",
        "[CSI_MCLK] MCLK 串阻位 (**位必留**: MCLK 是时钟输出, 串阻兼做源端匹配/阻尼); "
        "值随 TBD-03 的 MCLK 电平与速率定, 不写死")
    # ---- CSI_RESET_N (10k 上拉到 1.8V 域) ----
    conn_row(by_id, "A-12", "P5", "CSI_RESET_N", "SoC[TBD-01].CSI_RESET_N", "R_PU_CSI_RST",
             "NET_CSI_RESET_N")
    add("P5", "VDD_1V8_IO", "R_PU_CSI_RST", "RAIL_VDD_1V8_IO", "R_PU_CSI_RST", "10k ±1%",
        "R", "必装", "[推算]", "", "[VDD_1V8_IO] CSI_RESET_N 上拉 (1.8V 域)", "A-12")
    add("P5", "CSI_RESET_N", "CONN_CAM pin12", "NET_CSI_RESET_N", "NET_CSI_RESET_N",
        "单端, 10k 上拉", "NET", "必装", "[待原厂]", "TBD-03",
        "[CSI_RESET_N] 附加节点 (同 net)", "A-12")
    # ---- sensor 三条电源轨 · 连接器 ----
    for rail, pin in (("SENSOR_AVDD", 15), ("SENSOR_VDD_IO", 16), ("SENSOR_CORE", 17)):
        add("P5", rail, f"RAIL_{rail}", f"CONN_CAM pin{pin}", f"NET_{rail}",
            by_id_cid_rail(spec, rail), "NET", "必装", "[官方]", "",
            f"[{rail}] sensor 供电 接 CONN_CAM pin{pin} (跨铰链, 走线与 MCLK 并行 ≤5mm, 间距 ≥3mm)")
    # ---- 传感器连接器 ----
    add("P5", "CONN_CAM", "CONN_CAM", "CONN_CAM pin1", "CONN_CAM",
        "18p@0.5mm 跨铰链连接器 (型号待结构确认; pin1/2=CK, 3-10=D0-D3, 11=MCLK, 12=RESET, 13/14=I2C_A, 15-17=三条电源, 18=GND)", "CONN", "必装", "[推算]", "TBD-03",
        "[CONN_CAM] 主 PCB ↔ sensor 板 40p 跨铰链连接器; pin1/2=CSI_CK, 3..10=CSI_D0..D3, "
        "11=MCLK, 12=CSI_RESET_N, 13/14=I2C_A, 15/16/17=sensor 3V3/1V8/2V8; "
        "pin 数/pitch/翻盖方式待结构总工 (ISS-065); ★pin 编号为**本版自拟**, 非规格给定")
    add("P5", "GND", "CONN_CAM pin18", "GND", "CONN_CAM", "跨铰链回流地 (独立 pin)", "NET",
        "必装", "[推算]", "TBD-03",
        "[GND] ★CONN_CAM 18p 的第 18 脚 = 跨铰链回流地 (不与电源共脚 · 环路面积最小); "
        "17 脚电源 16 脚是 SENSOR_CORE 1.2V", "C-03")


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
    # ---- DP_TX 4 lane (A-21 覆盖全部 8 条 P/N) ----
    dp_pin = 21
    for lane in range(4):
        for pol in ("P", "N"):
            sig = f"DP_TX_A{lane}_{pol}"
            rser = f"R_SER_DP_A{lane}_{pol}"
            net = f"{sig}_SRC"
            conn_row(by_id, "A-21", "P6", net, f"SoC[TBD-01].{sig}", rser, f"NET_{net}")
            add("P6", sig, rser, f"U_BRIDGE pin{dp_pin}", rser, "100Ω ±10%", "R", "必装",
                "[待原厂]", "",
                f"[{sig}] DP TX 串阻位 (规格: 0402 串阻 ×4; 4 lane × P/N -> 实物 8 颗, "
                f"装配按实际 lane 数裁剪)")
            add("P6", net, f"C_AC_DP_A{lane}_{pol}", f"R_SER_DP_A{lane}_{pol}", f"C_AC_DP_A{lane}_{pol}",
                "[待选型]", "C", "DNP", "[待原厂]", "TBD-04",
                f"[{net}] DP TX **对地**电容位 (并联到 GND, 不是 AC 耦合电容; ★V1.6 修正: 原来 P/N 两路"
                f"共用一颗且 N 路错接到 P 路串阻 · 等于把差分对短接)")
            add("P6", "GND", f"C_AC_DP_A{lane}_{pol}", "GND", f"C_AC_DP_A{lane}_{pol}", "[待选型]", "C",
                "DNP", "[待原厂]", "",
                f"[{net}] DP TX 对地电容 另一端接 GND (两脚件必须落在 2 个网上)")
            dp_pin += 1
    add("P6", "DP_TX", "U_BRIDGE", "DP_TX_A0_P_SRC", "U_BRIDGE",
        "[待选型] DP1.4 TX · MIPI DSI TX 桥接芯片 (方案B 专用; 候选 redriver 兼列)", "IC", "DNP",
        "[推算]", "TBD-04",
        "[DP_TX] 方案B 才需要: SoC DP_TX 4 lane 进桥接芯片, DSI 出桥接芯片走 BR_* 到光机; "
        "**方案A (SoC 原生 DSI) 下整条链冗余 · 本行 DNP**; DP TX 是输出脚, 方案A 下悬空不违规")
    # ---- USB 2.0 (Type-C · 主 PCB) ----
    conn_row(by_id, "B-21", "P6", "USB_D_P_SRC", "SoC[TBD-01].USB_D_P", "R_SER_USB_D_P",
             "NET_USB_D_P_SRC")
    conn_row(by_id, "B-22", "P6", "USB_D_N_SRC", "SoC[TBD-01].USB_D_N", "R_SER_USB_D_N",
             "NET_USB_D_N_SRC")
    add("P6", "USB_D_P", "R_SER_USB_D_P", "CONN_USB pin1", "R_SER_USB_D_P", "22Ω ±1%", "R",
        "必装", "[推算]", "TBD-10",
        "[USB_D_P] USB 2.0 源端串阻 (D+, 22Ω 放在**主板侧 SoC 端**); ★V1.1 修: V1 把 D+ 直接接 "
        "J_TYPE_C pin4 = **把跨铰链短接了** · 改为接跨铰链连接器 CONN_USB pin1, 充电板侧再接 Type-C")
    add("P6", "USB_D_N", "R_SER_USB_D_N", "CONN_USB pin2", "R_SER_USB_D_N", "22Ω ±1%", "R",
        "必装", "[推算]", "TBD-10",
        "[USB_D_N] USB 2.0 源端串阻 (D-, 主板侧); ★V1.1 修: 同上, 改接 CONN_USB pin2")
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
    add("P6", "CONN_USB", "CONN_USB", "CONN_USB pin1", "CONN_USB",
        "4p@0.5mm USB 跨铰链连接器 (D+/D-/GND/预留)", "CONN", "必装", "[推算]", "",
        "[CONN_USB] ★USB 差分对**必然跨铰链** (Type-C 在充电板=镜框, SoC 在主 PCB=镜脚) · "
        "本位必留; ⚠️ USB 2.0 (及可能的 USB 3.0 SS) 差分跨铰链是 SI 风险, 建议 Type-C 挪主 PCB 侧 "
        "或调试改走 J_DEBUG/J_UART · 已列 P6 叙述 + 待项目总工/结构总工拍板")


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
    ("TP_SENSOR_2V8", "SENSOR_AVDD", "CONN_CAM pin15", "sensor 三条轨",
     "LDO 输出 (规格合并名 TP_SENSOR_3V3/1V8/2V8)", "必装"),
    ("TP_SENSOR_1V8", "SENSOR_VDD_IO", "CONN_CAM pin16", "sensor 三条轨",
     "LDO 输出 (规格合并名 TP_SENSOR_3V3/1V8/2V8)", "必装"),
    ("TP_SENSOR_1V2", "SENSOR_CORE", "CONN_CAM pin17", "sensor 三条轨",
     "LDO 输出 (规格合并名 TP_SENSOR_3V3/1V8/2V8)", "必装"),
    ("TP_LIGHT_3V3", "LIGHT_3V3", "CONN_LIGHT pin19", "光机轨", "LDO 输出", "必装"),
    ("TP_LIGHT_1V8", "LIGHT_1V8", "CONN_LIGHT pin20", "光机 1.8V 轨 (待 JBD)",
     "LDO 输出 (待 JBD 确认后)", "DNP"),
    ("TP_CSI_CK_P", "CSI_D0_CK_P", "CONN_CAM pin1", "CSI 时钟差分 (示波器测眼图/摆幅)",
     "连接器出口 (规格合并名 TP_CSI_D0_CK_P / _N)", "必装"),
    ("TP_CSI_CK_N", "CSI_D0_CK_N", "CONN_CAM pin2", "CSI 时钟差分 (规格合并名 TP_CSI_D0_CK_P / _N)",
     "连接器出口", "必装"),
    ("TP_CSI_D0_P", "CSI_D0_D0_P", "CONN_CAM pin3", "CSI D0 数据差分", "连接器出口", "必装"),
    ("TP_CSI_D0_N", "CSI_D0_D0_N", "CONN_CAM pin4", "CSI D0 数据差分", "连接器出口", "必装"),
    ("TP_CSI_RST", "CSI_RESET_N", "CONN_CAM pin12", "CSI 复位 (10k 上拉点)", "连接器出口", "必装"),
    ("TP_MCLK", "CSI_MCLK", "CONN_CAM pin11", "MCLK (包地走线)", "连接器出口", "必装"),
    ("TP_DSI_CK_P", "DSI_D0_CK_P", "CONN_LIGHT pin1", "DSI 时钟差分",
     "连接器出口 (规格合并名 TP_DSI_D0_CK_P / _N)", "必装"),
    ("TP_DSI_CK_N", "DSI_D0_CK_N", "CONN_LIGHT pin2", "DSI 时钟差分 (规格合并名 TP_DSI_D0_CK_P / _N)",
     "连接器出口", "必装"),
    ("TP_DSI_D0_P", "DSI_D0_D0_P", "CONN_LIGHT pin3", "DSI D0 数据差分", "连接器出口", "必装"),
    ("TP_DSI_D0_N", "DSI_D0_D0_N", "CONN_LIGHT pin4", "DSI D0 数据差分", "连接器出口", "必装"),
    ("TP_I2CA_SCL", "I2C_A_SCL", "CONN_CAM pin13", "I2C_A 时钟", "连接器出口", "必装"),
    ("TP_I2CA_SDA", "I2C_A_SDA", "CONN_CAM pin14", "I2C_A 数据", "连接器出口", "必装"),
    ("TP_I2CB_SCL", "I2C_B_SCL", "CONN_LIGHT pin17", "DDC 时钟 (I2C_B)", "连接器出口", "必装"),
    ("TP_I2CB_SDA", "I2C_B_SDA", "CONN_LIGHT pin18", "DDC 数据 (I2C_B)", "连接器出口", "必装"),
    ("TP_USB_D_P", "USB_D_P", "CONN_USB pin1", "USB 2.0 差分",
     "Type-C 出口 (规格合并名 TP_USB_D+ / D-)", "必装"),
    ("TP_USB_D_N", "USB_D_N", "CONN_USB pin2", "USB 2.0 差分 (规格合并名 TP_USB_D+ / D-)",
     "Type-C 出口", "必装"),
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
        conn_row(by_id, cid, "P7", f"LED_{col}", f"SoC[TBD-01].LED_{col}", f"R_LED_{col}",
                 f"NET_LED_{col}")
        add("P7", f"LED_{col}_D", f"R_LED_{col}", f"D_LED_{col}", f"R_LED_{col}", "1k ±1%",
            "R", dnp, "[推算]", "",
            f"[LED_{col}_D] LED_{col} 串阻 (3.3V 驱动; 实际值随 LED Vf 与目标亮度定)")
        add("P7", "GND", f"D_LED_{col}", "GND", f"D_LED_{col}", "LED (待选型)", "LED", dnp,
            "[推算]", "", f"LED_{col} 阴极 -> GND")
    for sig, net, tag, cid, dnp, desc in KEYS:
        conn_row(by_id, cid, "P7", net, f"SoC[TBD-01].{net}", f"R_KEY_{tag}", f"NET_KEY_{tag}")
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
        add("P8", f"XTAL_{pol}", f"SoC[TBD-01].XTAL_{pol}", "X1", f"NET_XTAL_{pol}", "12pF",
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
    add("P8", "RESET_N_SOC", "R_SER_RESET_N", "SoC[TBD-01].RESET_N", "R_SER_RESET_N", "1k ±1%",
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
    conn_row(by_id, "B-11", "P8", "BOOT_N", "SoC[TBD-01].BOOT_N", "R_PU_BOOT_N", "NET_BOOT_N")
    add("P8", "VDD_1V8_IO", "R_PU_BOOT_N", "RAIL_VDD_1V8_IO", "R_PU_BOOT_N", "10k ±1%", "R",
        "必装", "[推算]", "", "[VDD_1V8_IO] BOOT_N 上拉 (1.8V 域)", "B-11")
    add("P8", "BOOT_N", "SW_BOOT", "NET_BOOT_N", "SW_BOOT", "BOOT 按键 (待选型)", "SW", "必装",
        "[推算]", "", "[BOOT_N] BOOT 键 -> GND (进下载模式)", "B-11")
    add("P8", "GND", "SW_BOOT", "GND", "SW_BOOT", "BOOT 按键 (待选型)", "SW", "必装", "[推算]",
        "", "BOOT 键 -> GND", "B-11")
    # ---- JTAG 4 线 ----
    for sig, pin in (("JTAG_TCK", "pin1"), ("JTAG_TMS", "pin2"), ("JTAG_TDI", "pin3"),
                     ("JTAG_TDO", "pin4")):
        conn_row(by_id, "B-19", "P8", f"{sig}_SOC", f"SoC[TBD-01].{sig}", f"R_{sig}",
                 f"NET_{sig}_SOC")
        add("P8", sig, f"R_{sig}", f"J_DEBUG {pin}", f"R_{sig}", "100Ω ±1%", "R", "必装",
            "[推算]", "", f"[{sig}] JTAG {sig[5:]} 串阻 (隔离 SoC 调试脚)", "B-19")
    add("P8", "J_DEBUG", "J_DEBUG", "J_DEBUG pin1", "J_DEBUG", "1×4 1.27mm 排针 (JTAG)",
        "CONN", "必装", "[推算]", "",
        "[J_DEBUG] JTAG 调试排针 (不装贴片, 手工可焊); pin1=TCK, 2=TMS, 3=TDI, 4=TDO")
    # ---- UART 2 线 (与 USB 二选一) ----
    conn_row(by_id, "B-20", "P8", "UART_TX", "SoC[TBD-01].UART_TX", "J_UART pin1", "NET_UART_TX")
    conn_row(by_id, "B-20", "P8", "UART_RX", "SoC[TBD-01].UART_RX", "J_UART pin2", "NET_UART_RX")
    add("P8", "UART_RX", "J_UART", "J_UART pin2", "J_UART", "1×2 1.27mm 排针 (UART)", "CONN",
        "可选", "[推算]", "",
        "[UART_RX] 规格: UART 与 JTAG 复用同一排针 -> 本版拆成 1×2 独立排针 (原厂要求复用则再合并)")
    # ---- FSIN (帧同步引出) ----
    conn_row(by_id, "B-09", "P8", "FSIN", "SoC[TBD-01].FSIN", "R_SER_FSIN", "NET_FSIN")
    add("P8", "FSIN_OUT", "R_SER_FSIN", "TP_FSIN", "R_SER_FSIN", "50Ω ±1%", "R", "必装",
        "[推算]", "TBD-13", "[FSIN_OUT] FSIN 引出串阻 (50Ω 源端匹配)")

    # ---- ★V1.1 补画: 上电时序链 (DC-DC PG 状态 + 电压监控 · RESET 链式释放) ----
    add("P8", "PG_VCORE", "U_DCDC_VCORE PG", "TP_PG_VCORE", "TP_PG_VCORE",
        "PG (开漏, 需上拉)", "TP", "必装", "[官方]", "TBD-12",
        "[PG_VCORE] V_CORE 轨 PG 状态引出 (开漏, 需上拉到对应域); 若原厂要求 PG 参与上电时序, "
        "在此补上拉电阻位 (R_PG_VCORE, 待原厂确认 TBD-12)")
    add("P8", "PG_VIO", "U_DCDC_VIO PG", "TP_PG_VIO", "TP_PG_VIO",
        "PG (开漏, 需上拉)", "TP", "必装", "[官方]", "TBD-12",
        "[PG_VIO] V_SOC_IO 轨 PG 状态引出 (开漏, 需上拉); 同上")
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
    add("P8", "SUPV_SENSE", "U_SUPV IN", "U_SUPV", "U_SUPV",
        "[待选型] 电压监控 + 复位 (TPS3808G01 类)",
        "IC", "必装", "[推算]", "TBD-02", "[SUPV_SENSE] 监督器采样脚 (经分压)")
    add("P8", "RESET_N", "U_SUPV RESET (开漏)", "NET_RESET_N", "U_SUPV", "开漏释放",
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
    add("P9", "HINGE_CHG", "J_CHG", "J_CHG pin1", "J_CHG",
        "1×10p@0.5mm 排线座 (充电板↔主 PCB, 跨铰链载流)", "CONN", "必装", "[推算]", "",
        "[HINGE_CHG] 通道 1/4 **充电电流 + 状态回读** (★V1.2 改: 电池在镜脚 ⇒ 跨铰链的是**充电电流 "
        "1.0-1.5A**, **SYS 0.55A 不过铰链**): pin1/pin2=BAT_CHG (双 pin 并联载流), pin3/pin4=GND "
        "(回流双 pin), pin5=CHG_STAT, pin6=PWR_GOOD, pin7=VBUS_DET, pin8-10=预留; ★pin 编号为本版自拟 "
        "(型号/间距/载流待结构确认, ISS-085)")
    add("P9", "HINGE_USB", "CONN_USB", "CONN_USB pin1", "CONN_USB",
        "4p 跨铰链连接器 (D+/D-/GND/预留)", "CONN", "必装", "[推算]", "",
        "[HINGE_USB] 通道 2/4 **USB 2.0 差分**: Type-C 在镜框充电板, SoC 在镜脚主 PCB · "
        "**烧录/调试口必然跨铰链**; 本位必留 (ISS-085 裁决: Type-C 留充电板)")
    add("P9", "HINGE_CSI", "CONN_CAM", "CONN_CAM pin1", "CONN_CAM",
        "18p@0.5mm 跨铰链连接器 (主 PCB ↔ sensor 板; 18 脚 = 独立回流地)", "CONN", "必装", "[推算]", "TBD-03",
        "[HINGE_CSI] 通道 3/4 **MIPI-CSI**: pin1/2=CK, 3-10=D0-D3, 11=MCLK, 12=RESET_N, "
        "13/14=I2C_A, 15-17=sensor 三条电源; ★4 lane 全跨铰链 = 8 根 100Ω 差分 + MCLK 包地")
    add("P4", "GND", "CONN_LIGHT pin22", "GND", "CONN_LIGHT", "跨铰链回流地 (独立脚)", "NET",
        "必装", "[推算]", "TBD-04",
        "[GND] ★V1.6 补: CONN_LIGHT 原来 21 个脚里**一个 GND 都没有** · DSI 差分无回流路径 "
        "(跨铰链 100Ω 差分必须与地成对) · 22p 的末脚接 GND")
    add("P9", "HINGE_DSI", "CONN_LIGHT", "CONN_LIGHT pin1", "CONN_LIGHT",
        "1×22p@0.5mm 光机连接器 (板对板/FFC, 跨铰链到镜框光机; 末脚 GND = 差分回流)", "CONN", "必装", "[待JBD]", "TBD-04",
        "[HINGE_DSI] 通道 4/4 **显示 + 光机供电** (1×22p@0.5mm): pin1/2=CK, 3/4=D0, 5/6=D1, 7-10=D2/D3 预留(DNP), "
        "11-16=桥接位(方案B), 17/18=DDC(I2C_B), 19=LIGHT_3V3, 20=LIGHT_1V8, 21=LIGHT_5V 预留(DNP), **22=GND 回流**; 型号待 JBD 接口定义")
    # ---- 跨铰链段的保护/滤波件 (装主 PCB 侧, 紧贴连接器) ----
    add("P9", "USB_D_P", "CONN_USB pin1", "D_ESD_USB", "D_ESD_USB",
        "ESD 阵列 [待选型] (2 通道 USB)", "D", "必装", "[推算]", "",
        "[USB_D_P] ★跨铰链 USB 主板侧 ESD 阵列 (紧贴 CONN_USB); ★**不装共模扼流圈** "
        "(USB 2.0 眼图对共模转差分极敏感, 扼流圈会恶化眼图) · 靠 FPC 阻抗控制 + 两端 ESD")
    add("P9", "USB_D_N", "CONN_USB pin2", "D_ESD_USB", "D_ESD_USB",
        "ESD 阵列 [待选型] (2 通道 USB)", "D", "必装", "[推算]", "",
        "[USB_D_N] USB 主板侧 ESD 阵列 (同一位, 2 通道)")
    add("P9", "USB_D_N", "CONN_USB pin3", "GND", "NET_USB_GND_H", "单端", "NET", "必装",
        "[推算]", "",
        "[USB_D_N] 跨铰链 USB 回流地 (独立 pin, 不与电源共 pin · 环路面积最小)", "")
    add("P9", "HINGE_RSV", "CONN_USB pin4", "CONN_USB pin4", "CONN_USB", "预留 (不装)",
        "NET", "DNP", "[推算]", "",
        "[HINGE_RSV] CONN_USB pin4 预留位 (不装)", "")
    add("P9", "GND", "D_ESD_USB", "GND", "D_ESD_USB", "ESD 阵列 [待选型]", "D", "必装",
        "[推算]", "", "[USB_D_P] USB ESD 阵列 地端")
    add("P9", "CSI_D0_CK_P", "CONN_CAM pin1", "D_ESD_CAM", "D_ESD_CAM",
        "ESD 阵列 [待选型] (多通道 CSI)", "D", "必装", "[推算]", "TBD-03",
        "[CSI_D0_CK_P] ★跨铰链 CSI 主板侧 ESD 阵列位 (紧贴 CONN_CAM); 通道数随 lane 数定")
    add("P9", "GND", "D_ESD_CAM", "GND", "D_ESD_CAM", "ESD 阵列 [待选型]", "D", "必装",
        "[推算]", "TBD-03", "[CSI_D0_CK_P] CSI ESD 地端")
    # ---- 充电板侧: USB 差分从跨铰链连接器接到 Type-C (V1 漏画这一段) ----
    add("P9", "USB_D_P_CHG", "CONN_USB pin1", "J_TYPE_C A6+B6", "NET_USB_D_P_CHG",
        "板内走线 (充电板侧)", "NET", "必装", "[推算]", "",
        "[USB_D_P_CHG] ★V1.1 补画: 充电板侧 USB 差分从跨铰链连接器到 Type-C D+ (板内走线)")
    add("P9", "USB_D_N_CHG", "CONN_USB pin2", "J_TYPE_C A7+B7", "NET_USB_D_N_CHG",
        "板内走线 (充电板侧)", "NET", "必装", "[推算]", "",
        "[USB_D_N_CHG] 充电板侧 USB 差分从跨铰链连接器到 Type-C D- (板内走线)")
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
    n_p10 = build_p10_json()

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
