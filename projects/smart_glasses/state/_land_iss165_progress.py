#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""land_iss165_progress.py —— 记录 A2 段进展与最后缺口 (11-03 00:5x)"""
import yaml

IP = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses/state/issue_log.yaml'
d = yaml.safe_load(open(IP, encoding='utf-8'))
for i in d['issues']:
    if i['id'] == 'ISS-165':
        i['note'] += (
            " ★★**2026-11-03 00:5x A2 段进展 (项目总工自办)**: "
            "①网表侧基本做完: **19 个信号映射到 SOM 实际引脚** (17 直接映射 + LED_0/1 分配空闲 GPIO2_B1_d pin80 / GPIO3_D4_d pin19; ★**XTAL_0/1 晶振在 SOM 板上 ⇒ 主板标 DNP 不装**; ★**FSIN 在 SOM 无对应脚 ⇒ DNP 待核**) "
            "②**VCC_DCIN ×7 → RAIL_SOM_DCIN** (USB 5V 直供 SOM) "
            "③★**F13 落地**: pin87 `CARRIER_BOARD_EN` → **U_EN_SW 负载开关 EN** ⇒ **RAIL_SYS → RAIL_BOARD_5V**, ★**主板 3.3V/5V 支路全部改挂 RAIL_BOARD_5V (不再直连 SYS)** ⇒ 底板晚于核心板上电 "
            "④pin88 `PWRON_L` + 开机按键 "
            "⑤分配表落 `HW/PCB/SOM_PIN_ASSIGNMENT.md` + `HW/PCB/som_pin_map.json` ⇒ ★**check_netlist 31 条 / check_kicad_net 5 条全过**。"
            "★★★**但板子还不能下单 —— 剩最后一处**: **板上 SOM 座 400 焊盘的网络绑定有 18 处对不上** (缺失 3: DSI_RESET_N / PWR_ON / VBUS_DET; 多余 15) ⇒ `check_pcb_nets` 判「不等价 ⇒ 板子不能下单」 ⇒ "
            "★**根因方向已锁定**: ★**表里的 `num` 是连接器脚号 (1~400, 分 4 组各 100)**, 而板上是 4×100pin BTB ⇒ ★**组内脚号与表 num 的对应关系必须按 Forlinx 表的组序核对** (我现在的假设是 `组=(num-1)//100, 组内=(num-1)%100`, **未经验证**) ⇒ ★★**引脚对不上 = 板子白打** ⇒ ⇒ **明早第一件事: 逐脚核对前 20 个脚的组序与物理位置**, 再重跑 `gen_pcb_netlist_board.py` + `check_pcb_nets.py` + `check_pcb_drc.py` + 重出 Gerber/钻孔。")
yaml.safe_dump(d, open(IP, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=10**6)
print('[issue_log] ISS-165 进展已记')
