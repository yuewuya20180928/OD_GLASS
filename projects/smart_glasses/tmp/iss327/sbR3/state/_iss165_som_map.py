#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss165_som_map.py —— A2 段: 把网表里的 SoC 占位信号映射到 SOM 实际引脚 + 落 J_SOM 座 + CARRIER_BOARD_EN 电源使能

依据: HW/PCB/FET3576C_PIN_TABLE.csv (399 行, Forlinx 官方手册 §2.6 解析) —— ★**FET3572-C 与 FET3576-C 引脚兼容**
做法: ①建"我们的信号 → SOM 脚名候选(按优先级)"规则表 ②在表里挑第一个存在的脚 ③把网表里
      `SoC[RK3572].<sig>` 节点改写成 `J_SOM pin<num>` ④加 J_SOM 座相关行 (VCC_DCIN×7 / CARRIER_BOARD_EN / PWRON_L)
      ⑤★**F13: 主板 3.3V/5V 由 CARRIER_BOARD_EN 使能** ⇒ 加 U_EN_SW 负载开关 (RAIL_SYS → RAIL_BOARD_5V)
"""
import csv
import json
import os
import re

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
CSV = f'{PROJ}/HW/PCB/FET3576C_PIN_TABLE.csv'
GEN = f'{PROJ}/state/gen_netlist.py'

rows = list(csv.DictReader(open(CSV, encoding='utf-8')))
bypin = {}
alt2num = {}
for r in rows:
    num = (r.get('num') or '').strip()
    if not num.isdigit():
        continue
    bypin[num] = r
    for a in (r.get('signal') or '').split('/'):
        a = a.strip()
        if a:
            alt2num.setdefault(a, num)

# ★我们的信号 → SOM 脚候选 (按优先级; 第一个在表里存在的胜出)
RULES = {
    # ---- 电源/控制 (板级) ----
    'PWR_CTRL':      ['PWRON_L'],
    'RESET_N':       ['RESET_L'],
    'BOOT_N':        ['SARADC_VIN0_BOOT'],
    'ID':            ['SARADC_VIN2_HW_ID'],
    'USB_VBUS_DET':  ['USB2_OTG1_VBUSDET', 'USB2_OTG1_VBUSDET'],
    'USB_D_P':       ['USB2_OTG1_DP', 'USB2_HOST1_DP'],
    'USB_D_N':       ['USB2_OTG1_DM', 'USB2_HOST1_DM'],
    'UART_TX':       ['UART0_TX_M0_DEBUG', 'UART5_TX_M1'],
    'UART_RX':       ['UART0_RX_M0_DEBUG', 'UART5_RX_M1'],
    # ---- I2C: camera 用 M2 组, display/touch 用 M1 组 (M1/M2 = 模块侧/载板侧, 取公开表) ----
    'I2C_A_SCL':     ['I2C8_SCL_M2', 'I2C7_SCL_M1', 'I2C8_SCL_M1'],
    'I2C_A_SDA':     ['I2C8_SDA_M2', 'I2C7_SDA_M1', 'I2C8_SDA_M1'],
    'I2C_B_SCL':     ['I2C7_SCL_M1', 'I2C8_SCL_M2'],
    'I2C_B_SDA':     ['I2C7_SDA_M1', 'I2C8_SDA_M2'],
    # ---- 复位/时钟 (camera) ----
    'CSI_RESET_N':   ['MIPI_DPHY_CSI0_RX_D0P', 'GPIO2_B5_d'],   # ★具体脚待核 (SOM 是否引出 camera reset)
    'CSI_MCLK':      ['MIPI_DPHY_CSI0_RX_CLK_P', 'GPIO2_B3_d'],  # ★同上
    # ---- 通用 GPIO (给 camera / display 复位) ----
    'GPIO_CAM_RESET': ['GPIO2_B5_d', 'GPIO3_D4_d'],
    'GPIO_DSI_RESET': ['GPIO2_B3_d', 'GPIO2_B1_d'],
    # ---- 其余占位 ----
    'FSIN':          [],
    'XTAL_':         [],
    'LED_':          [],
}

mapping = {}
unmapped = []
for sig, cands in RULES.items():
    hit = None
    for c in cands:
        if c in alt2num:
            hit = c
            break
    if hit:
        mapping[sig] = {'somsig': hit, 'num': alt2num[hit],
                         'ball': bypin[alt2num[hit]].get('ball', ''),
                         'vol': bypin[alt2num[hit]].get('vol', '')}
    else:
        unmapped.append(sig)

# ★网表里实际用到的信号
src = open(GEN, encoding='utf-8').read()
used = sorted(set(re.findall(r'SoC\[RK3572\]\.([A-Za-z0-9_]+)', src)))
todo = [s for s in used if s not in mapping]

# ── 改写网表节点: SoC[RK3572].<sig> → J_SOM pin<num> ──
cnt = 0
for sig, m in mapping.items():
    pat = f'SoC[RK3572].{sig}'
    if pat in src:
        cnt += src.count(pat)
        src = src.replace(pat, f'J_SOM pin{m["num"]}')

# ── 追加: J_SOM 座相关行 + F13 电源使能 ──
anchor = '    # ---- ★★2026-11-02 20:5x A1 段: display FPC 座 (40p/0.5mm) 未被主链引用的针全部补齐 ----'
assert anchor in src
som_block = '''
    # ---- ★★2026-11-03 00:3x A2 段: RK3572 核心板 (Forlinx FET3572-C) 座 + ★F13 底板主电源使能 ----
    #   逐针表: HW/PCB/FET3576C_PIN_TABLE.csv (399 行) + HW/PCB/SOM_PIN_ASSIGNMENT.md (本单生成的分配表)
    #   电源: pin91/93/95/97 = VCC_DCIN (5-13V) ⇒ 主板 USB 5V 直接供 SOM; pin87 = CARRIER_BOARD_EN (SOM 输出)
    #   ★F13: **主板的 3.3V/5V 主开关由 CARRIER_BOARD_EN 驱动** —— 否则底板早于核心板上电
    #        (Forlinx 原文: 通电瞬间电流过大 / 无法启动 / 可能对处理器造成不可逆损坏)
    _som_dcin = ["91", "93", "95", "97"]
    for _pn in _som_dcin:
        add("P1", "RAIL_SOM_DCIN", f"J_SOM pin{_pn}", "RAIL_SOM_DCIN", "J_SOM", "5-13V", "NET",
            "必装", "[官方]", "",
            "[J_SOM] ★FET3572-C VCC_DCIN (5-13V 输入) ⇒ 主板 USB-C 5V 直供 (★4 针并联载流)", "A-24")
    add("P1", "CARRIER_BOARD_EN", "J_SOM pin87", "CARRIER_BOARD_EN", "J_SOM", "EN 输出", "NET",
        "必装", "[官方]", "",
        "[CARRIER_BOARD_EN] ★★F13 (致命项): **SOM 输出, 控制底板上电** ⇒ ★**主板 3.3V/5V 的主开关 (U_EN_SW) 必须由它驱动, 不得直连** "
        "(Forlinx 手册: 底板早于核心板上电 ⇒ 通电瞬间电流过大/无法启动/可能对处理器造成不可逆损坏) ⇒ 详见 HW/PCB/LAYOUT_RULES.md", "A-24")
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
    add("P1", "PWRON_L", "J_SOM pin88", "PWRON_L", "J_SOM", "开机控制 (SOM 输入)", "NET",
        "必装", "[官方]", "",
        "[PWRON_L] ★SOM pin88 ⇒ 主板侧按键到 GND 拉低 (手册 §3.5.2)", "A-24")
    add("P1", "PWRON_L", "SW_PWRON", "PWRON_L", "SW_PWRON", "按键 (到 GND)", "NET", "必装", "[推算]", "",
        "[PWRON_L] ★开机按键: 一端 PWRON_L, 一端 GND", "A-24")
    add("P1", "GND", "SW_PWRON", "GND", "SW_PWRON", "GND", "NET", "必装", "[推算]", "",
        "[PWRON_L] 按键地端", "A-24")
'''
src = src.replace(anchor, som_block + "\n" + anchor, 1)

# ★底板各路 LDO 的输入改挂 RAIL_BOARD_5V (F13): 把 LDO 输入行的 SYS 改成 BOARD_5V
src = src.replace('''        add("P1", "SYS_PCB", "RAIL_SYS", ref, "RAIL_SYS", "3.5-4.2V (R-F1 抬下限后)",
            "NET", dnp, "[推算]", "",
            f"[{rail}] {ref} 输入脚供电 (SYS 镜脚本地产生, 电池保护后); "''',
'''        _in_rail = "RAIL_BOARD_5V" if ref in ("U_LDO_L33", "U_LDO_L18", "U_LDO_IO33", "U_LDO_IO18") else "RAIL_SYS"
        add("P1", _in_rail, _in_rail, ref, _in_rail, "5.0V (受 CARRIER_BOARD_EN 门控)" if _in_rail == "RAIL_BOARD_5V" else "3.5-4.2V (R-F1 抬下限后)",
            "NET", dnp, "[推算]", "",
            f"[{rail}] {ref} 输入脚供电 (★F13: 底板支路挂 RAIL_BOARD_5V = 由 CARRIER_BOARD_EN 门控的 U_EN_SW 输出); "''')

open(GEN, 'w', encoding='utf-8').write(src)
import ast
ast.parse(src)
print(f"[1] 网表节点改写: {cnt} 处 SoC 占位 → J_SOM pinN; 映射 {len(mapping)} 个信号")

# ── 落分配表 ──
with open(f'{PROJ}/HW/PCB/SOM_PIN_ASSIGNMENT.md', 'w', encoding='utf-8') as f:
    f.write("# SOM 引脚分配表 (RK3572 核心板 Forlinx FET3572-C)\n\n")
    f.write("> 来源: Forlinx 官方手册 §2.6 逐针表 (解析后 `HW/PCB/FET3576C_PIN_TABLE.csv`, 399 行) + 我们的网表信号\n")
    f.write("> ★**FET3572-C 与 FET3576-C 引脚兼容** ⇒ 用这张表分配\n\n")
    f.write("| 我们的信号 | SOM 脚名 | 座脚号 | CPU 球号 | 电平 |\n|---|---|---|---|---|\n")
    for s, m in sorted(mapping.items()):
        f.write(f"| {s} | {m['somsig']} | pin{m['num']} | {m['ball']} | {m['vol']} |\n")
    f.write(f"\n## ★未分配 (需人工选脚或标待核)\n\n")
    for s in (todo or unmapped):
        f.write(f"- **{s}**\n")
    f.write("\n## 电源与控制 (固定)\n\n")
    f.write("| 功能 | 座脚号 |\n|---|---|\n| VCC_DCIN (5-13V 输入) | pin91/93/95/97 |\n")
    f.write("| CARRIER_BOARD_EN (SOM 输出, 底板使能) | pin87 |\n| PWRON_L (开机) | pin88 |\n")
json.dump({"mapping": mapping, "unmapped": todo or unmapped},
          open(f'{PROJ}/HW/PCB/som_pin_map.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"[2] 分配表已落: HW/PCB/SOM_PIN_ASSIGNMENT.md (映射 {len(mapping)} / 未分配 {len(todo or unmapped)})")
print("    未分配:", ", ".join(todo or unmapped))
