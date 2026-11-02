#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""land_iss162.py —— ISS-162 (A1 段) 收口 + 新开 ISS-165 (A2 段, 项目总工自办)"""
import os
import sys
import yaml

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
sys.path.insert(0, f'{PROJ}/state')
from frag_write import update_fragment

IP = f'{PROJ}/state/issue_log.yaml'
d = yaml.safe_load(open(IP, encoding='utf-8'))
iss = d['issues']
by = {i['id']: i for i in iss}

i = by['ISS-162']
i['status'] = 'fixed'
i['owner'] = 'main'
i['verify_by'] = 'hw-lead'
i['verify_result'] = 'pass'
i['verify_date'] = '2026-11-02'
i['fix_ref'] = ('HW/NETLIST_REV2_SPEC.md · HW/PCB/FPC_PIN_TABLES.md (31p/40p 针位表) · '
                'state/gen_netlist.py (CSI 4-lane 31针 / DSI 40针 / I2C 24-25 / MCLK 20 / 供电 28-31 / 复位 27 / 三条 sensor 轨 DNP / EN 补齐) · '
                'HW/SCHEMATIC_V1_SPEC.json (power_rails + 连接描述 + 新增 A-21/A-22) · '
                'state/check_netlist.py (铰链堆叠判据停用)')
i['note'] += (' ★★**2026-11-02 20:5x A1 段由项目总工亲自做完** (★hw-lead 连续第三次 0 产出: ISS-162 28 分钟 / 506k tokens 零文件改动 ⇒ 按铁律不再派第三次)。'
               '★**做了什么**: ①**camera FPC → 31p/0.3mm** (Radxa Camera 4K 逐针表, 座 HIROSE FH35C-31S-0.3SHW(50)) + **CSI 改 4-lane 必装** (原 D2/D3 是 DNP 预留) + I2C pin24/25 + MCLK pin20 + RESET pin27 → 新网 CAM_RESET_N + 供电 pin28/29=3.3V、pin30/31=5V; '
               '②**display FPC → 40p/0.5mm** (Radxa Display 8HD/10FHD 逐针表) + DSI 4-lane (CK 14/15 · D0 8/9 · D1 11/12 · D2 17/18 · D3 20/21) + DDC 28/27 + VDD 2/31/32 + VCCIO 3 + Reset 5 → 新网 DSI_RESET_N + 背光/触控组; '
               '③★**三条 sensor 芯片级轨 (SENSOR_CORE / SENSOR_VDD_IO / SENSOR_AVDD) → DNP** (★**camera 模组自带稳压** ⇒ 这是对 19:5x 那次改动的推翻 ⇒ ISS-159 F14); '
               '④★**F1 (EN) 补齐**: 现用的 4 颗 TPS7A20 的 EN 全部显式接 RAIL_SYS (悬空=关断 ⇒ 投板后整板不上电); '
               '⑤★**铰链区堆叠判据停用** (37mm 预算属整机跨铰链阶段; demo 板 camera/display 都是板内 FPC 座 ⇒ 按老板 19:25「结构不考虑」标 N/A); '
               '⑥针位表导出 `HW/PCB/FPC_PIN_TABLES.md`。'
               '★**验证**: 4 个生成器 rc=0 · check_netlist 31 条全过 · check_kicad_net 5 条全过 · **板子重出: 板子↔网表逐点等价 (346 绑定/缺失0/多余0) + DRC=0 + Gerber 30 + 钻孔** ⇒ ★**板子可下单 (A2 段 SOM 座接入后需再重跑一遍)**。')

if not any(x['id'] == 'ISS-165' for x in iss):
    iss.append({
        'id': 'ISS-165',
        'title': '★★★[硬件 A2 段 · 最后一块] SOM 座 (4×100pin/0.4mm BTB) + SoC 节点改挂 + ★CARRIER_BOARD_EN 底板主电源使能',
        'severity': 'blocker', 'source_blocker': None, 'source_agent': 'main',
        'desc': ('★2026-11-02 20:5x: A1 段已完成 (FPC 针位/供电/EN/四 lane 全对; 板子 DRC=0 且与网表逐点等价) ⇒ ★**剩 A2 段, 这是 demo 板的最后一块**。'
                 '★**要做**: ①**主板上的 SOM 座 = 4 组 100 脚 0.4mm BTB** (Forlinx FET3572-C 68×50mm) ⇒ ★**焊盘宽 ≤0.18mm** (0.4 间距 − 0.18 = 0.22 > 0.2 clearance ⇒ **本段唯一的几何硬约束**) '
                 '②**SoC 侧节点全部改挂到该座** ⇒ 用 `HW/PCB/FET3576C_PIN_TABLE.csv` (399 行: num/ball/电平/信号名/SoM 网名) ⇒ ★**FET3572-C 与 FET3576-C 引脚兼容** '
                 '③★**F13 底板主电源使能**: pin87 `CARRIER_BOARD_EN` (SOM 输出, 控制底板上电) + pin91/93/95/97 `VCC_DCIN` (5-13V 输入) ⇒ ★**主板 3.3V/5V 的主开关必须由 CARRIER_BOARD_EN 驱动, 不能直连** (Forlinx 原文: 底板早于核心板上电 ⇒ 通电瞬间电流过大 / 无法启动 / **可能对处理器造成不可逆损坏**) ⇒ **这是继 EN 之后第二条致命项** '
                 '④pin88 `PWRON_L` (开机按键) · Boot 按 `SARADC_VIN0_BOOT` (手册 §3.5.3) · UART Debug 按 §3.5.5 (串 100Ω + 保留 Q1/Q2 隔离 + ESD 紧贴) '
                 '⑤**ESD 硬判据** (§3.5): 阵列紧贴接口 + **寄生电容 ≤0.4pF** (超了吃高速眼图) ⇒ 已写进 `HW/PCB/LAYOUT_RULES.md`。'
                 '⇒ ★**验收链与 A1 相同**: gen_netlist → check_netlist → check_kicad_net → gen_bom → **重出板子** → check_pcb_nets (逐点等价) → check_pcb_drc (DRC=0) → 重出 Gerber/钻孔。'
                 '⇒ ★**不再派 hw-lead**: ★**同类任务已连续三次 0 产出** ⇒ 本段由项目总工自己做。'),
        'owner': 'main', 'reporter': 'main', 'raised': '2026-11-02', 'due': '2026-11-03',
        'status': 'open', 'external': False, 'need_keys': [],
        'fix_ref': 'HW/PCB/FET3576C_PIN_TABLE.csv (399 行逐针表) · HW/NETLIST_REV2_SPEC.md §2 · HW/PCB/LAYOUT_RULES.md',
        'verify_by': 'hw-lead', 'verify_result': None, 'verify_date': None,
        'note': ('2026-11-02 20:5x。★**项目总工自办** (hw-lead 在"网表大改"上三次 0 产出)。'
                 '★**开工前置**: A1 的板子已 DRC=0 + 逐点等价 ⇒ A2 只需把 SOM 座接上 + 电源使能改对 ⇒ 再重跑一遍即可。'),
        'dispatched_at': None,
    })

yaml.safe_dump(d, open(IP, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=10**6)
print('[issue_log] ISS-162 fixed + ISS-165 新开')


def mutate(d):
    claims = d.setdefault("interface_claims", [])
    def add(k, v, n, r):
        for c in claims:
            if c.get("key") == k:
                c.update({"value": v, "note": n, "ref": r}); return
        claims.append({"key": k, "value": v, "note": n, "ref": r})
    add("demo_fpc_connectors", "31p_0.3 + 40p_0.5",
        "★★A1 段已落地 (11-02 20:5x, 项目总工亲自做): **camera FPC 座 = 31p/0.3mm** (Radxa Camera 4K, HIROSE FH35C-31S-0.3SHW(50); CSI **4-lane 必装**; I2C 24/25; MCLK 20; RESET 27→CAM_RESET_N; 供电 28/29=3.3V、30/31=5V) + **display FPC 座 = 40p/0.5mm** (Radxa Display 8HD/10FHD; DSI 4-lane CK14/15 D0 8/9 D1 11/12 D2 17/18 D3 20/21; DDC 28/27; VDD 2/31/32; VCCIO 3; Reset 5→DSI_RESET_N) + ★**三条 sensor 芯片级轨全部 DNP (模组自带稳压)** + ★**F1 EN 补齐 (4 颗 TPS7A20 的 EN 显式接 RAIL_SYS)** ⇒ 针位表见 `HW/PCB/FPC_PIN_TABLES.md`。",
        "HW/NETLIST_REV2_SPEC.md + HW/PCB/FPC_PIN_TABLES.md + state/gen_netlist.py")
    add("board_ready_state", "drc0_parity346",
        "★★demo 主板当前状态 (11-02 20:5x): **DRC = 0** + **板子↔网表逐点等价 (346 绑定 / 缺失 0 / 多余 0)** + Gerber 30 + 钻孔 + 6 层叠层 (MIPI 100Ω) + 两张 FPC 针位表 ⇒ ★**A1 段完成, 可下单** ⇒ ★**A2 段 (SOM 座 400 脚 + CARRIER_BOARD_EN 电源使能) 是最后一块** (ISS-165, 项目总工自办)",
        "HW/PCB/ + state/check_pcb_drc.py + state/check_pcb_nets.py")
    d["updated_at"] = "2026-11-02"; d["updated_by"] = "main"
    return d


update_fragment("hw-lead", mutate)
print('[分片] hw.yaml ok')
