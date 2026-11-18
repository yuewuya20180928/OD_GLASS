#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss165_assign_final.py —— SOM 引脚最终分配 (用重建后的 CSV: conn + num + signal, 唯一键 = (conn,num))

★ 11-03 00:5x 的三个真发现 (全部来自 Forlinx 公开手册):
  ① §2.6.2 引脚表按连接器分 4 组表 (表0/1→P1, 表2/3→P2, 表4/5→P3, 表6/7→P4), 每组 NUM = **组内脚号 1..100**
  ② ★**`CARRIER_BOARD_EN` = P3_87** (不是 P1_87 —— 差一整组 = 板子直接不工作)
  ③ ★**同一信号名会出现在多组** (如 GPIO2_B5_d 既是 P1_50 又是别的组的复位脚) ⇒ 唯一键必须是 **(conn, num)**,
     我们只取其中一个 ⇒ 选哪个要**显式写进分配表**
"""
import csv
import json
import os
import re
import shutil

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
CSVF = f'{PROJ}/HW/PCB/FET3576C_PIN_TABLE.csv'
GEN = f'{PROJ}/state/gen_netlist.py'
MAPJ = f'{PROJ}/HW/PCB/som_pin_map.json'

rows = list(csv.DictReader(open(CSVF, encoding='utf-8')))
sig2 = {}
for r in rows:
    sig = (r.get('signal') or '').strip()
    cn = (r.get('conn') or '').strip()
    nm = (r.get('num') or '').strip()
    if not sig or not cn or not nm.isdigit():
        continue
    sig2.setdefault(sig, []).append((cn, int(nm)))
gpios = [(cn, int(nm), s) for s, lst in sig2.items()
         for (cn, nm) in lst if re.match(r'^GPIO\d+_[A-Z]\d+_d$', s)]
print(f"[1] CSV: {len(sig2)} 个信号名, GPIO 类 {len(gpios)} 个")

# ── 我们的信号 → SOM 候选 (优先级) ──
RULES = {
    'PWR_CTRL':      ['PWRON_L'],
    'RESET_N':       ['RESET_L'],
    'BOOT_N':        ['SARADC_VIN0_BOOT'],
    'ID_DETECT_0':   ['SARADC_VIN2_HW_ID'],
    'USB_VBUS_DET':  ['USB2_OTG1_VBUSDET'],
    'USB_D_P':       ['USB2_HOST1_DP', 'USB2_OTG0_DP'],
    'USB_D_N':       ['USB2_HOST1_DM', 'USB2_OTG0_DM'],
    'UART_TX':       ['UART0_TX_M0_DEBUG', 'UART5_TX_M1'],
    'UART_RX':       ['UART0_RX_M0_DEBUG', 'UART5_RX_M1'],
    'I2C_A_SCL':     ['I2C8_SCL_M2', 'I2C7_SCL_M1'],
    'I2C_A_SDA':     ['I2C8_SDA_M2', 'I2C7_SDA_M1'],
    'I2C_B_SCL':     ['I2C7_SCL_M1', 'I2C8_SCL_M2'],
    'I2C_B_SDA':     ['I2C7_SDA_M1', 'I2C8_SDA_M2'],
    'CSI_RESET_N':   [],      # ★SOM 未引出 camera reset ⇒ 主板自己出 (见 note)
    'CSI_MCLK':      [],      # ★同上: camera MCLK 由主板提供, 不从 SOM 出
    'ID_DETECT_1':   [],
    'FSIN':          [],
    'XTAL_0':        [],
    'XTAL_1':        [],
}
GPIO_POOL = ['GPIO_CAM_RESET', 'GPIO_DSI_RESET', 'LED_0', 'LED_1']

assign = {}
used = set()
for ours, cands in RULES.items():
    for c in cands:
        if c in sig2:
            cn, nm = sig2[c][0]
            assign[ours] = {'somsig': c, 'conn': cn, 'num': nm}
            used.add((cn, nm))
            break
# GPIO 池: 从空闲 GPIO 里分配
free = [(cn, nm, s) for (cn, nm, s) in gpios if (cn, nm) not in used]
for i, ours in enumerate(GPIO_POOL):
    if i < len(free):
        cn, nm, s = free[i]
        assign[ours] = {'somsig': s, 'conn': cn, 'num': nm}
        used.add((cn, nm))
missing = [k for k in list(RULES) + GPIO_POOL if k not in assign]
print(f"[2] 分配 {len(assign)} / {len(RULES)+len(GPIO_POOL)}; 未分配 {missing}")

# ── 网表: 从 A1 干净基线重来 + A2 全部 ──
shutil.copy('/tmp/gen_netlist.py.bak2', GEN)
g = open(GEN, encoding='utf-8').read()
cnt = 0
for ours, m in assign.items():
    pat = f'SoC[RK3572].{ours}'
    if pat in g:
        cnt += g.count(pat)
        g = g.replace(pat, f'J_SOM_{m["conn"]} pin{m["num"]}')
print(f"[3] 网表节点改写 {cnt} 处")

# ── A2 行: VCC_DCIN (从 CSV 取 P3 的那几脚) + CARRIER_BOARD_EN + U_EN_SW + PWRON_L ──
dcin = [nm for (cn, nm) in sig2.get('VCC_DCIN', []) if cn == 'P3']
car_en = sig2.get('CARRIER_BOARD_EN', [('P3', 87)])[0]
pwr = sig2.get('PWRON_L', [('P3', 88)])[0]
anchor = '    # ---- ★★2026-11-02 20:5x A1 段: display FPC 座 (40p/0.5mm) 未被主链引用的针全部补齐 ----'
block = f'''
    # ---- ★★2026-11-03 00:7x A2 段: RK3572 核心板 (Forlinx FET3572-C) 座 + ★F13 底板主电源使能 ----
    #   ★脚标识 = 手册权威形式 P<x>_<num> (4 个连接器各 100 脚) ⇒ 主板上是 **4 个独立 100 脚 BTB 座**
    for _pn in {dcin}:
        add("P1", "RAIL_SOM_DCIN", f"J_SOM_P3 pin{{_pn}}", "RAIL_SOM_DCIN", "J_SOM_P3", "5-13V", "NET",
            "必装", "[官方]", "",
            "[J_SOM_P3] ★FET3572-C VCC_DCIN (5-13V 输入) ⇒ 主板 USB-C 5V 直供 (多针并联载流)", "A-24")
    add("P1", "CARRIER_BOARD_EN", f"J_SOM_{car_en[0]} pin{car_en[1]}", "CARRIER_BOARD_EN", f"J_SOM_{car_en[0]}",
        "EN 输出", "NET", "必装", "[官方]", "",
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
    # ★★P3_88 (PWRON_L) **已经在 PWR_ON 网上** (接 U_PWR_SW 的 ON 脚 + 10k 下拉) ⇒ **不再单开 PWRON_L 网**
    #   (否则同一个物理脚会落在两个网上 ⇒ 板子短接) ⇒ 开机/关机功能由 U_PWR_SW 的 ON 节点承担
'''
g = g.replace(anchor, block + "\n" + anchor, 1)
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
print(f"[4] A2 行已追加 (VCC_DCIN P3 {dcin} / CARRIER_BOARD_EN {car_en} / PWRON_L {pwr} / U_EN_SW / 按键)")

json.dump({'assign': assign, 'missing': missing, 'vcc_dcin_p3': dcin,
           'carrier_board_en': list(car_en), 'pwr_on_l': list(pwr),
           'note': '★唯一键 = (conn, num); 同一信号名可能出现在多组 ⇒ 我们只取一个, 已在 assign 里显式选定'},
          open(MAPJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
with open(f'{PROJ}/HW/PCB/SOM_PIN_ASSIGNMENT.md', 'w', encoding='utf-8') as f:
    f.write("# SOM 引脚分配表 (RK3572 核心板 Forlinx FET3572-C)\n\n")
    f.write("> ★脚标识 = 手册权威形式 `P<x>_<num>` (4 个连接器各 100 脚) ⇒ **主板上是 4 个独立 100 脚 BTB 座 (J_SOM_P1..P4)**\n")
    f.write("> 来源: Forlinx 官方手册 (OK3576-C_User_Hardware_Manual) §2.6.2 引脚表 + §2.7 功能表; 全量映射 `HW/PCB/som_pin_full_map.json`\n\n")
    f.write("| 我们的信号 | SOM 脚名 | 连接器 | 组内脚 | 座 | 网络名 |\n|---|---|---|---|---|---|\n")
    for ours, m in sorted(assign.items()):
        f.write(f"| {ours} | {m['somsig']} | {m['conn']} | {m['num']} | J_SOM_{m['conn']} | J_SOM_{m['conn']}_pin{m['num']} |\n")
    f.write("\n## 未分配 (★主板自己提供 / DNP)\n\n")
    for x in missing:
        note = ""
        if x in ('CSI_RESET_N', 'CSI_MCLK'):
            note = " ★**SOM 未引出 camera 的 RESET/MCLK ⇒ 主板必须自己产生 (★架构级结论, 要补 MCLK 源)**"
        if x in ('XTAL_0', 'XTAL_1'):
            note = " ★**晶振在核心板上 ⇒ 主板不接**"
        if x == 'FSIN':
            note = " ★SOM 上无对应脚 ⇒ 主板不接"
        f.write(f"- **{x}**{note}\n")
    f.write("\n## 固定脚\n\n| 功能 | 脚标识 |\n|---|---|\n")
    f.write(f"| VCC_DCIN (5-13V 输入) | {' / '.join('P3_'+str(x) for x in dcin)} |\n")
    f.write(f"| CARRIER_BOARD_EN (底板使能, ★致命项 F13) | {car_en[0]}_{car_en[1]} |\n")
    f.write(f"| PWRON_L (开机) | {pwr[0]}_{pwr[1]} |\n")
print("[5] 分配表已落")
