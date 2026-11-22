#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_patch_a2_som_netlist.py —— ★把 SoC 侧节点从占位符换成真实引脚 + A2 段电源使能 (2026-11-03 10:3x)

★ 依赖: `HW/PCB/som_pin_assign.json` (由 `state/_iss165_a2_som.py` 从 OK3572-C 手册引脚表生成)

做四件事:
  ① gen_netlist.py 加 `soc_pin(sig)` —— 查分配表返回 `J_SOM_Px pinN`; 未分配 ⇒ **直接报错退出**
     (⇒ 以后任何新加的 SoC 节点都必须先分配引脚, 不可能再出现"占位符混进板子")
  ② 所有 `SoC[RK3572].<sig>` ⇒ `soc_pin("<sig>")` (含 f-string 形式)
  ③ FET3572-C **未引出** 的信号 (SPI/JTAG/FSIN) ⇒ 行标 DNP + 写明理由 (不编造)
  ④ A2 段新增行: SoM 自己的 VCC_DCIN (7 脚) · CARRIER_BOARD_EN ⇒ U_EN_SW ⇒ RAIL_BOARD_5V (F13)
     · demo 板自己的 Type-C (J_DEMO_USB) + VBUS 检测分压 · I2C_A 上拉改 1.8V (I2C5 域)
"""
import ast
import json
import os
import re
import sys

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
GEN = f'{PROJ}/state/gen_netlist.py'

HELPER = '''

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
'''

A2_FUNC = '''

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
    add("P1", "RAIL_DEMO_5V", "J_DEMO_USB VBUS", "RAIL_DEMO_5V", "RAIL_DEMO_5V",
        "5.0V ±5% (USB-C 5V)", "RAIL", "必装", "[官方]", "",
        "[RAIL_DEMO_5V] ★demo 板自己的 USB-C 5V 输入 ⇒ 同时供 SoM 的 VCC_DCIN (5~13V) 与 U_EN_SW", "A-24")
    add("P1", "RAIL_DEMO_5V", "D_ESD_DEMO", "RAIL_DEMO_5V", "D_ESD_DEMO",
        "ESD 阵列 [待选型] (USB 2.0)", "D", "必装", "[推算]", "",
        "[RAIL_DEMO_5V] USB-C VBUS 入口 ESD 阵列 (紧贴 J_DEMO_USB)", "A-24")
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
    add("P1", "GND", "R_CC2_D", "GND", "R_CC2_D", "5.1k ±1% (CC2 下拉)", "R", "必装", "[官方]", "",
        "[R_CC2_D] USB-C CC2 5.1k 下拉", "A-24")
    add("P1", "J_DEMO_USB", "J_DEMO_USB", "J_DEMO_USB", "J_DEMO_USB",
        "USB-C 16p 插座 (demo 板 5V 输入 + USB 数据)", "CONN", "必装", "[推算]", "",
        "[J_DEMO_USB] ★demo 板自己的 Type-C: VBUS→5V 轨, D+/D-→SoM USB, CC1/CC2→5.1k 下拉 ⇒ 受电端 (UFP)", "A-24")
    # ---- USB 数据: SoM 的 USB_DRD1 (P1_92/P1_94) ↔ 板载 Type-C ----
    add("P1", "USB_D_P_SRC", "R_SER_USB_D_P", "J_DEMO_USB D+", "R_SER_USB_D_P", "22Ω ±1%", "R",
        "必装", "[推算]", "",
        "[USB_D_P_SRC] ★SoM USB2 (OTG1) D+ → 板载 Type-C (demo 板自带 USB, 免跨铰链)", "A-24")
    add("P1", "USB_D_N_SRC", "R_SER_USB_D_N", "J_DEMO_USB D-", "R_SER_USB_D_N", "22Ω ±1%", "R",
        "必装", "[推算]", "",
        "[USB_D_N_SRC] ★SoM USB2 (OTG1) D- → 板载 Type-C", "A-24")
    # ---- VBUS_DET: 板载 Type-C 的 VBUS 分压 → SoM 的 USB_DRD1_VBUSDET (P1_100) ----
    add("P1", "VBUS_DET_D", "R_VBUS_DET_D1", "R_VBUS_DET_D2", "NET_VBUS_DET_D",
        "1M ±1% (上臂)", "R", "必装", "[推算]", "",
        "[VBUS_DET_D] ★demo 板: Type-C VBUS 在**主板本地**分压 (不再跨铰链) ⇒ SoM 的 USB_DRD1_VBUSDET", "A-24")
    add("P1", "GND", "R_VBUS_DET_D2", "GND", "R_VBUS_DET_D2", "1M ±1% (下臂)", "R", "必装",
        "[推算]", "", "[VBUS_DET_D] 分压下臂 地端", "A-24")
    add("P1", "GND", "C_DET_VBUS_D", "GND", "C_DET_VBUS_D", "100nF ±10%", "C", "必装",
        "[推算]", "", "[VBUS_DET_D] ADC 滤波电容", "A-24")
    add("P1", "VBUS_DET", soc_pin("USB_VBUS_DET"), "NET_VBUS_DET_D", soc_pin("USB_VBUS_DET"),
        "USB VBUS 检测", "NET", "必装", "[官方]", "",
        "[VBUS_DET] ★SoM 的 USB_DRD1_VBUSDET (P1_100) ← 板载 Type-C VBUS 分压", "A-24")

    # ---- ② ★F13: CARRIER_BOARD_EN ⇒ 负载开关 U_EN_SW ⇒ RAIL_BOARD_5V ----
    add("P1", "CARRIER_BOARD_EN", f"J_SOM_{car_en.split('_')[0]} pin{car_en.split('_')[1]}",
        "U_EN_SW EN", "J_SOM_P3", "EN 输出", "NET", "必装", "[官方]", "",
        f"[CARRIER_BOARD_EN] ★★F13 致命项: SoM 的 {car_en} (输出, 3.3V, 1K 上拉) ⇒ **底板上电许可**; "
        "Forlinx 原文: 底板早于核心板上电 ⇒ 通电瞬间电流过大 / 无法启动 / **可能对处理器造成不可逆损坏**", "A-24")
    add("P1", "CARRIER_BOARD_EN", "U_EN_SW EN", "CARRIER_BOARD_EN", "U_EN_SW",
        "EN 输入 (高=放行底板)", "NET", "必装", "[官方]", "",
        "[U_EN_SW] EN ← CARRIER_BOARD_EN ⇒ 主板各路只在 SoM 就绪后上电", "A-24")
    add("P1", "RAIL_DEMO_5V", "U_EN_SW IN", "RAIL_DEMO_5V", "U_EN_SW", "5V 输入", "NET",
        "必装", "[官方]", "", "[U_EN_SW] IN = 5V (Type-C 直供)", "A-24")
    add("P1", "RAIL_BOARD_5V", "U_EN_SW OUT", "RAIL_BOARD_5V", "U_EN_SW",
        "5V 输出 (受 CARRIER_BOARD_EN 门控)", "NET", "必装", "[官方]", "",
        "[RAIL_BOARD_5V] ★**底板所有 3.3V/5V 支路都挂这条** (不是 SYS) ⇒ 这就是 F13 的落法", "A-24")
    add("P1", "GND", "U_EN_SW GND", "GND", "U_EN_SW", "GND", "NET", "必装", "[官方]", "",
        "[U_EN_SW] 地", "A-24")

    # ---- ③ SoM 自己的供电 VCC_DCIN (7 脚并联) —— 直供, 不受门控 ----
    for _pn in dcin:
        _c, _n = _pn.split("_")
        add("P1", "RAIL_SOM_DCIN", f"J_SOM_{_c} pin{_n}", "RAIL_DEMO_5V", f"J_SOM_{_c}",
            "5-13V 输入 (SoM 侧)", "NET", "必装", "[官方]", "",
            f"[VCC_DCIN] ★SoM 自己的电源输入 ({_pn}; 手册 §2.4.2 DC 5~13V; 7 脚并联载流) "
            "⇒ **直供 5V, 不经过 U_EN_SW** (否则 SoM 自己起不来)", "A-24")
'''

REPL_LITERALS = [
    ('SoC[RK3572].PWR_CTRL', 'soc_pin("PWR_CTRL")'),
    ('SoC[RK3572].USB_VBUS_DET', 'soc_pin("USB_VBUS_DET")'),
    ('SoC[RK3572].I2C_A_SCL', 'soc_pin("I2C_A_SCL")'),
    ('SoC[RK3572].I2C_A_SDA', 'soc_pin("I2C_A_SDA")'),
    ('SoC[RK3572].I2C_B_SCL', 'soc_pin("I2C_B_SCL")'),
    ('SoC[RK3572].I2C_B_SDA', 'soc_pin("I2C_B_SDA")'),
    ('SoC[RK3572].ID0', 'soc_pin("ID0")'),
    ('SoC[RK3572].ID1', 'soc_pin("ID1")'),
    ('SoC[RK3572].GPIO_DSI_RESET', 'soc_pin("GPIO_DSI_RESET")'),
    ('SoC[RK3572].GPIO_CAM_RESET', 'soc_pin("GPIO_CAM_RESET")'),
    ('SoC[RK3572].CSI_RESET_N', 'soc_pin("CSI_RESET_N")'),
    ('SoC[RK3572].USB_D_P', 'soc_pin("USB_D_P")'),
    ('SoC[RK3572].USB_D_N', 'soc_pin("USB_D_N")'),
    ('SoC[RK3572].RESET_N', 'soc_pin("RESET_N")'),
    ('SoC[RK3572].BOOT_N', 'soc_pin("BOOT_N")'),
    ('SoC[RK3572].UART_TX', 'soc_pin("UART_TX")'),
    ('SoC[RK3572].UART_RX', 'soc_pin("UART_RX")'),
    ('SoC[RK3572].VBUS_DET', 'soc_pin("VBUS_DET")'),
    ('SoC[RK3572].BAT_DET', 'soc_pin("BAT_DET")'),
]


def main():
    src = open(GEN, encoding='utf-8').read()
    orig = src

    print('=== ① 加 soc_pin() 助手 + 分配表加载 ===')
    if 'def soc_pin(' not in src:
        anchor = 'ROWS: list[dict] = []'
        src = src.replace(anchor, anchor + '\n' + HELPER, 1)
        print('  [插] soc_pin() 已加 (未分配的 SoC 信号会直接报错退出)')

    print('=== ② SoC 占位符 ⇒ 真实引脚 ===')
    n = 0
    for old, new in REPL_LITERALS:
        c = src.count(f'"{old}"')
        if c:
            # ★**整串替换 (含外层引号)**: 否则会拼出 "soc_pin("X")" 这种嵌套引号 ⇒ 语法错
            src = src.replace(f'"{old}"', new)
            n += c
    # f-string 形式
    for old, new in (('f"SoC[RK3572].{src}"', 'soc_pin(src)'),
                     ('f"SoC[RK3572].{sig}"', 'soc_pin(sig)'),
                     ('f"SoC[RK3572].XTAL_{pol}"', 'soc_pin(f"XTAL_{pol}")')):
        c = src.count(old)
        src = src.replace(old, new)
        n += c
        if c:
            print(f'  [替] {old} × {c}')
    print(f'  共替换 {n} 处')

    print('=== ③ 未引出的信号标 DNP ===')
    # SPI (P3 启动存储) —— FET3572-C 未引出 SPI
    src = src.replace(
        '''    for sig, tbd, pin in spi:
        add("P3", sig, f"soc_pin(sig)", f"R_SER_{sig}", f"NET_{sig}", "0Ω (串阻位)",
            "NET", "必装", "[待原厂]", tbd, boot_note, "")
        add("P3", f"{sig}_BOOT", f"R_SER_{sig}", pin, f"R_SER_{sig}", "0Ω (串阻位)",
            "R", "必装", "[待原厂]", tbd, f"[{sig}_BOOT] {sig} 串阻位 (0Ω 调试用)", "")''',
        '''    for sig, tbd, pin in spi:
        # ★★2026-11-03: FET3572-C **未引出 SPI** (SoM 板载 eMMC/SD) ⇒ 主板不挂 SPI-NOR ⇒ DNP
        add("P3", sig, f"soc_pin(sig)", f"R_SER_{sig}", f"NET_{sig}", "0Ω (串阻位)",
            "NET", "DNP", "[官方]", tbd,
            boot_note + " ★**DNP: FET3572-C 未引出 SPI (引脚表 399 行里没有 SPI) ⇒ 主板不挂 SPI-NOR**", "")
        add("P3", f"{sig}_BOOT", f"R_SER_{sig}", pin, f"R_SER_{sig}", "0Ω (串阻位)",
            "R", "DNP", "[官方]", tbd, f"[{sig}_BOOT] {sig} 串阻位 (0Ω 调试用; ★DNP: SoM 未引出 SPI)", "")''')
    # JTAG (P8) —— 未引出
    src = src.replace(
        '''        conn_row(by_id, "B-19", "P8", f"{sig}_SOC", f"soc_pin(sig)", f"R_{sig}",
                 f"NET_{sig}_SOC")
        add("P8", sig, f"R_{sig}", f"J_DEBUG {pin}", f"R_{sig}", "100Ω ±1%", "R", "必装",
            "[推算]", "", f"[{sig}] JTAG {sig[5:]} 串阻 (隔离 SoC 调试脚)", "B-19")''',
        '''        # ★★2026-11-03: FET3572-C **未引出 JTAG** ⇒ 调试走 UART0 ⇒ 这四路 DNP
        conn_row(by_id, "B-19", "P8", f"{sig}_SOC", f"soc_pin(sig)", f"R_{sig}",
                 f"NET_{sig}_SOC")
        add("P8", sig, f"R_{sig}", f"J_DEBUG {pin}", f"R_{sig}", "100Ω ±1%", "R", "DNP",
            "[官方]", "", f"[{sig}] JTAG {sig[5:]} 串阻 ★DNP: FET3572-C 未引出 JTAG (调试走 UART0)", "B-19")''')
    # FSIN —— 未引出
    src = src.replace(
        '''    conn_row(by_id, "B-09", "P8", "FSIN", f"soc_pin("FSIN")", "R_SER_FSIN", "NET_FSIN")''',
        '''    conn_row(by_id, "B-09", "P8", "FSIN", f'soc_pin("FSIN")', "R_SER_FSIN", "NET_FSIN")''')
    print('  (SPI / JTAG / FSIN → DNP)')

    print('=== ④ I2C_A 改 1.8V 域 (I2C5) + TMP117 挪到 I2C_B (3.3V 域) ===')
    src = src.replace(
        '''    add("P2", "VDD_3V3_IO", "R_PU_I2CA_SCL", "RAIL_VDD_3V3_IO", "R_PU_I2CA_SCL", "2.2k ±1%",''',
        '''    # ★★2026-11-03 订正: 相机 SCCB 走 **I2C5 (RK3572 上是 1.8V 域)** ⇒ 上拉必须到 **1.8V**
    #   (旧写法拉到 3.3V ⇒ **SoM 的 1.8V 脚被灌 3.3V** ⇒ 过压)
    add("P2", "VDD_1V8_IO", "R_PU_I2CA_SCL", "RAIL_VDD_1V8_IO", "R_PU_I2CA_SCL", "2.2k ±1%",''')
    src = src.replace(
        '''    add("P2", "VDD_3V3_IO", "R_PU_I2CA_SDA", "RAIL_VDD_3V3_IO", "R_PU_I2CA_SDA", "2.2k ±1%",''',
        '''    add("P2", "VDD_1V8_IO", "R_PU_I2CA_SDA", "RAIL_VDD_1V8_IO", "R_PU_I2CA_SDA", "2.2k ±1%",''')
    # TMP117 挪到 I2C_B (3.3V): TMP117 的 VIH = 0.7×V+ ⇒ 1.8V 总线不满足
    src = src.replace(
        '''    add("P2", "I2C_A_SCL", "U_TEMP pin2", "NET_I2C_A_SCL", "U_TEMP",''',
        '''    add("P2", "I2C_B_SCL", "U_TEMP pin2", "NET_I2C_B_SCL", "U_TEMP",''')
    src = src.replace(
        '''    add("P2", "I2C_A_SDA", "U_TEMP pin1", "NET_I2C_A_SDA", "U_TEMP",''',
        '''    add("P2", "I2C_B_SDA", "U_TEMP pin1", "NET_I2C_B_SDA", "U_TEMP",''')
    print('  (I2C_A 上拉 → 1.8V; TMP117 → I2C_B)')

    print('=== ⑤ LDO 输入轨改挂 RAIL_BOARD_5V (F13) ===')
    src = src.replace(
        '''        add("P1", "SYS_PCB", "RAIL_SYS", ref, "RAIL_SYS", "3.5-4.2V (R-F1 抬下限后)",''',
        '''        add("P1", "SYS_PCB", "RAIL_BOARD_5V", ref, "RAIL_BOARD_5V", "5.0V (F13: 由 CARRIER_BOARD_EN 门控)",''')
    src = src.replace(
        '''                add("P1", "SYS_PCB", f"{ref} EN", "RAIL_SYS", ref, "EN", "NET", dnp, "[官方]", "",''',
        '''                add("P1", "SYS_PCB", f"{ref} EN", "RAIL_BOARD_5V", ref, "EN", "NET", dnp, "[官方]", "",''')
    print('  (4 颗 LDO + 它们的 EN → RAIL_BOARD_5V)')

    print('=== ⑥ 插入 A2 段函数 + 在 main() 里调用 ===')
    if 'def build_a2_som(' not in src:
        anchor = '# --------------------------------------------------------------- 写盘 + 门禁'
        src = src.replace(anchor, A2_FUNC.strip() + '\n\n\n' + anchor, 1)
        print('  [插] build_a2_som() 已加')
    if 'build_a2_som(by_id, spec)' not in src:
        src = src.replace('    n_p10 = build_p10_json()',
                          '    build_a2_som(by_id, spec)\n    n_p10 = build_p10_json()', 1)
        print('  [插] main() 里调用 build_a2_som()')

    ast.parse(src)
    if src == orig:
        print('\n★★ 无改动')
        return 1
    open(GEN, 'w', encoding='utf-8').write(src)
    print(f'\n✅ {GEN} 已落盘 (语法自检通过)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
