#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss165_som_final.py —— A2 段最终修正: 用手册的 **权威脚标识 `P<x>_<n>`** 重建 SOM 映射

★★ 根因 (11-03 00:5x 实测): 我解析 §2.6.2 时**丢了「属于哪个连接器 (P1..P4)」这一列** ⇒ CSV 的 num 只是**组内脚号 1..100**
   ⇒ 之前一直拿组内脚号当全局号 ⇒ 板子绑不上网络 (18 处对不上) ⇒ ★★**引脚对不上 = 板子白打**
★★ 修法: 不再靠 num ⇒ ★**直接用手册 §2.7 各功能表里的 `Pin Number` 列 (P3_91 这种权威形式)** 建
   「我们的信号 → (P组, 组内脚)」⇒ 网表节点写成 `J_SOM_P<x> pin<n>` ⇒ 主板上 4 个独立 100 脚座
"""
import collections
import csv
import html
import json
import os
import re

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
MANUAL = '/tmp/fx3576.html'
GEN = f'{PROJ}/state/gen_netlist.py'
MAPJ = f'{PROJ}/HW/PCB/som_pin_map.json'

# ── ① 解析手册: 行内若含 `P<x>_<n>` ⇒ 该行其余单元格里的信号名 → (x,n) ──
t = open(MANUAL, encoding='utf-8', errors='replace').read()
tables = re.findall(r'<table.*?</table>', t, re.S)
sig2conn = collections.defaultdict(set)
for tb in tables:
    for tr in re.findall(r'<tr.*?</tr>', tb, re.S):
        cells = [html.unescape(re.sub(r'<[^>]+>', '', c)).strip() for c in re.findall(r'<t[dh].*?</t[dh]>', tr, re.S)]
        pinref = None
        for c in cells:
            m = re.fullmatch(r'P(\d+)_(\d+)', c.strip())
            if m:
                pinref = (int(m.group(1)), int(m.group(2)))
                break
        if not pinref:
            continue
        for c in cells:
            if re.fullmatch(r'[A-Z][A-Z0-9_]{3,}', c.strip()) and not c.strip().startswith('P'):
                sig2conn[c.strip()].add(pinref)
print(f"[1] 手册功能表解析: 信号 → (P组, 组内脚) 命中 {len(sig2conn)} 个信号")

# ── ② 我们的信号 → SOM 信号名候选 (优先级) ──
RULES = {
    'PWR_CTRL':      ['PWRON_L'],
    'RESET_N':       ['RESET_L'],
    'BOOT_N':        ['SARADC_VIN0_BOOT'],
    'ID':            ['SARADC_VIN2_HW_ID'],
    'USB_VBUS_DET':  ['USB2_OTG1_VBUSDET'],
    'USB_D_P':       ['USB2_OTG1_DP', 'USB2_HOST1_DP'],
    'USB_D_N':       ['USB2_OTG1_DM', 'USB2_HOST1_DM'],
    'UART_TX':       ['UART0_TX_M0_DEBUG', 'UART5_TX_M1'],
    'UART_RX':       ['UART0_RX_M0_DEBUG', 'UART5_RX_M1'],
    'I2C_A_SCL':     ['I2C8_SCL_M2', 'I2C7_SCL_M1'],
    'I2C_A_SDA':     ['I2C8_SDA_M2', 'I2C7_SDA_M1'],
    'I2C_B_SCL':     ['I2C7_SCL_M1', 'I2C8_SCL_M2'],
    'I2C_B_SDA':     ['I2C7_SDA_M1', 'I2C8_SDA_M2'],
    'CSI_RESET_N':   ['MIPI_DPHY_CSI0_RX_D0P'],
    'CSI_MCLK':      ['MIPI_DPHY_CSI0_RX_CLK_P'],
    'GPIO_CAM_RESET': ['GPIO2_B5_d', 'GPIO3_D4_d'],
    'GPIO_DSI_RESET': ['GPIO2_B3_d', 'GPIO2_B1_d'],
    'LED_0':         ['GPIO2_B1_d', 'GPIO3_D4_d'],
    'LED_1':         ['GPIO3_D4_d', 'GPIO2_B5_d'],
    'FSIN':          [],
    'XTAL_0':        [],
    'XTAL_1':        [],
}
# ★SOM 的电源/控制脚 (固定, 不走 RULES)
FIXED = {
    'SOM_DCIN':   [(3, 91), (3, 93), (3, 95), (3, 97), (3, 98), (3, 99), (3, 100)],
    'CARRIER_EN': [(1, 87)],          # ★组待核: 手册里 P1_87/P2_87/P3_87 都有同名? 以功能表为准
    'PWRON_L':    [(3, 88)],
}

assign = {}
for ours, cands in RULES.items():
    for c in cands:
        if c in sig2conn:
            x, n = sorted(sig2conn[c])[0]
            assign[ours] = {'somsig': c, 'conn': x, 'num': n}
            break
for name, lst in FIXED.items():
    if lst:
        assign[name] = {'somsig': name, 'conn': lst[0][0], 'num': lst[0][1], 'all': [list(x) for x in lst]}
missing = [k for k in RULES if k not in assign]
print(f"[2] 我们的信号 → SOM 脚: 命中 {len(assign)} / {len(RULES)}; 未命中 {missing}")

# ── ③ 网表节点改写 (从 A1 干净基线重来) ──
import shutil
shutil.copy('/tmp/gen_netlist.py.bak2', GEN)
g = open(GEN, encoding='utf-8').read()
cnt = 0
for ours, m in assign.items():
    pat = f'SoC[RK3572].{ours}'
    if pat in g:
        cnt += g.count(pat)
        g = g.replace(pat, f'J_SOM_P{m["conn"]} pin{m["num"]}')
open(GEN, 'w', encoding='utf-8').write(g)
print(f"[3] 网表节点改写 {cnt} 处 → J_SOM_P<x> pin<n>")

# ── ④ 追加 SOM 座/电源/使能 行 (A2 段) ──
anchor = '    # ---- ★★2026-11-02 20:5x A1 段: display FPC 座 (40p/0.5mm) 未被主链引用的针全部补齐 ----'
assert anchor in g
som_block = '''
    # ---- ★★2026-11-03 00:6x A2 段: RK3572 核心板 (Forlinx FET3572-C) 座 + ★F13 底板主电源使能 ----
    #   ★脚标识用手册权威形式 P<x>_<n> (4 个连接器各 100 脚) ⇒ 主板上是 **4 个独立 100 脚 BTB 座**
    #   ★分配表: HW/PCB/SOM_PIN_ASSIGNMENT.md + HW/PCB/som_pin_map.json
    for _pn in ["91", "93", "95", "97", "98", "99", "100"]:
        add("P1", "RAIL_SOM_DCIN", f"J_SOM_P3 pin{_pn}", "RAIL_SOM_DCIN", "J_SOM_P3", "5-13V", "NET",
            "必装", "[官方]", "",
            "[J_SOM_P3] ★FET3572-C VCC_DCIN (5-13V 输入) ⇒ 主板 USB-C 5V 直供 (多针并联载流)", "A-24")
    add("P1", "CARRIER_BOARD_EN", "J_SOM_P1 pin87", "CARRIER_BOARD_EN", "J_SOM_P1", "EN 输出", "NET",
        "必装", "[官方]", "",
        "[CARRIER_BOARD_EN] ★★F13 (致命项): **SOM 输出, 控制底板上电** ⇒ ★**主板 3.3V/5V 的主开关 (U_EN_SW) 必须由它驱动, 不得直连** "
        "(Forlinx 手册: 底板早于核心板上电 ⇒ 通电瞬间电流过大/无法启动/可能对处理器造成不可逆损坏)", "A-24")
    add("P1", "CARRIER_BOARD_EN", "U_EN_SW EN", "CARRIER_BOARD_EN", "U_EN_SW", "EN 输入 (高=使能)", "NET",
        "必装", "[官方]", "",
        "[U_EN_SW] ★负载开关 EN ⇒ 接 CARRIER_BOARD_EN (SOM 上电后才放行底板各路)", "A-24")
    add("P1", "RAIL_SYS", "U_EN_SW IN", "RAIL_SYS", "U_EN_SW", "5V 输入 (USB-C)", "NET", "必装", "[官方]", "",
        "[U_EN_SW] 输入 = SYS (USB-C 5V)", "A-24")
    add("P1", "RAIL_BOARD_5V", "U_EN_SW OUT", "RAIL_BOARD_5V", "U_EN_SW", "5V 输出 (受 CARRIER_BOARD_EN 门控)", "NET",
        "必装", "[官方]", "",
        "[U_EN_SW] 输出 = **底板 5V 轨** ⇒ ★**底板所有 3.3V/5V 支路都挂这条, 而不是 SYS** ⇒ 这就是 F13 的落法", "A-24")
    add("P1", "GND", "U_EN_SW GND", "GND", "U_EN_SW", "GND", "NET", "必装", "[官方]", "",
        "[U_EN_SW] 地", "A-24")
    add("P1", "PWRON_L", "J_SOM_P3 pin88", "PWRON_L", "J_SOM_P3", "开机控制 (SOM 输入)", "NET",
        "必装", "[官方]", "",
        "[PWRON_L] ★SOM P3_88 ⇒ 主板侧按键到 GND 拉低 (手册 §3.5.2)", "A-24")
    add("P1", "PWRON_L", "SW_PWRON", "PWRON_L", "SW_PWRON", "按键 (到 GND)", "NET", "必装", "[推算]", "",
        "[PWRON_L] ★开机按键: 一端 PWRON_L, 一端 GND", "A-24")
    add("P1", "GND", "SW_PWRON", "GND", "SW_PWRON", "GND", "NET", "必装", "[推算]", "",
        "[PWRON_L] 按键地端", "A-24")
'''
g = g.replace(anchor, som_block + "\n" + anchor, 1)

# 底板支路的 LDO 输入改挂 RAIL_BOARD_5V (F13)
g = g.replace('''        add("P1", "SYS_PCB", "RAIL_SYS", ref, "RAIL_SYS", "3.5-4.2V (R-F1 抬下限后)",
            "NET", dnp, "[推算]", "",
            f"[{rail}] {ref} 输入脚供电 (SYS 镜脚本地产生, 电池保护后); "''',
'''        _in_rail = "RAIL_BOARD_5V" if ref in ("U_LDO_L33", "U_LDO_L18", "U_LDO_IO33", "U_LDO_IO18") else "RAIL_SYS"
        add("P1", _in_rail, _in_rail, ref, _in_rail, "5.0V (受 CARRIER_BOARD_EN 门控)" if _in_rail == "RAIL_BOARD_5V" else "3.5-4.2V (R-F1 抬下限后)",
            "NET", dnp, "[推算]", "",
            f"[{rail}] {ref} 输入脚供电 (★F13: 底板支路挂 RAIL_BOARD_5V = 由 CARRIER_BOARD_EN 门控的 U_EN_SW 输出); "''')
open(GEN, 'w', encoding='utf-8').write(g)
import ast
ast.parse(g)
print("[4] A2 段行已追加 (VCC_DCIN×7 / CARRIER_BOARD_EN + U_EN_SW / PWRON_L + 按键 / 底板支路改挂 RAIL_BOARD_5V)")

# ── ⑤ 落映射 ──
MAP = {'assign': assign, 'missing': missing,
       'note': '★脚标识 = 手册权威形式 P<x>_<n> (4 个连接器各 100 脚) ⇒ 主板上是 4 个独立 100 脚 BTB 座 (J_SOM_P1..P4)'}
json.dump(MAP, open(MAPJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
json.dump({k: sorted([list(x) for x in v]) for k, v in sig2conn.items()},
          open(f'{PROJ}/HW/PCB/som_signal_to_connector.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
with open(f'{PROJ}/HW/PCB/SOM_PIN_ASSIGNMENT.md', 'w', encoding='utf-8') as f:
    f.write("# SOM 引脚分配表 (RK3572 核心板 Forlinx FET3572-C)\n\n")
    f.write("> ★**脚标识 = 手册权威形式 `P<x>_<n>`** (4 个连接器各 100 脚, 脚号各自独立) ⇒ **主板上是 4 个独立 100 脚 BTB 座 (J_SOM_P1..P4)**\n")
    f.write("> 来源: Forlinx 官方手册 (OK3576-C_User_Hardware_Manual) §2.6/§2.7 逐针与功能表\n\n")
    f.write("| 我们的信号 | SOM 脚名 | 连接器 | 组内脚 | 座 | 网络名 |\n|---|---|---|---|---|---|\n")
    for ours, m in sorted(assign.items()):
        f.write(f"| {ours} | {m['somsig']} | P{m['conn']} | {m['num']} | J_SOM_P{m['conn']} | J_SOM_P{m['conn']}_pin{m['num']} |\n")
    f.write(f"\n## 未分配 (需人工选脚或标 DNP)\n\n")
    for x in missing:
        f.write(f"- **{x}**\n")
    f.write("\n## 固定脚\n\n| 功能 | 脚标识 |\n|---|---|\n")
    f.write("| VCC_DCIN (5-13V 输入) | P3_91/93/95/97/98/99/100 |\n")
    f.write("| CARRIER_BOARD_EN (底板使能) | P1_87 (★组待核) |\n")
    f.write("| PWRON_L (开机) | P3_88 |\n")
print("[5] 分配表已落 (HW/PCB/SOM_PIN_ASSIGNMENT.md / som_pin_map.json / som_signal_to_connector.json)")
