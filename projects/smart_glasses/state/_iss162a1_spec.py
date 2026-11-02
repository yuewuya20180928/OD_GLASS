#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iss162a1_spec.py —— A1 段第二步: 规格里的连接描述改成新针位 (31p/40p) + 补 DSI D3 通道 + 连接器脚数"""
import json
import re

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
SPEC = f'{PROJ}/HW/SCHEMATIC_V1_SPEC.json'
GEN = f'{PROJ}/state/gen_netlist.py'

# ── Radxa Camera 4K 31 针 (0.3mm) ──
CAM = {1: "GND", 2: "MDN4", 3: "MDP4", 4: "GND", 5: "MDN3", 6: "MDP3", 7: "GND", 8: "NC",
       9: "NC", 10: "GND", 11: "MDN2", 12: "MDP2", 13: "GND", 14: "MDN1", 15: "MDP1", 16: "GND",
       17: "MCN", 18: "MCP", 19: "GND", 20: "MCLK", 21: "GND", 22: "NC", 23: "NC", 24: "SCL",
       25: "SDA", 26: "NC", 27: "RESET", 28: "VCC3.3V", 29: "VCC3.3V", 30: "VCC5V", 31: "VCC5V"}
# ── Radxa Display 8HD/10FHD 40 针 (0.5mm) ──
DISP = {1: "NC", 2: "VDD_3V3", 3: "VCCIO", 4: "NC", 5: "RESET", 6: "NC", 7: "GND",
        8: "MIPI_0N", 9: "MIPI_0P", 10: "GND", 11: "MIPI_1N", 12: "MIPI_1P", 13: "GND",
        14: "MIPI_CKN", 15: "MIPI_CKP", 16: "GND", 17: "MIPI_2N", 18: "MIPI_2P", 19: "GND",
        20: "MIPI_3N", 21: "MIPI_3P", 22: "GND", 23: "GND", 24: "TP_RESET", 25: "TP_VCC",
        26: "TP_INT", 27: "TP_SDA", 28: "TP_SCL", 29: "GND", 30: "GND", 31: "VDD_3V3", 32: "VDD_3V3",
        33: "GND", 34: "GND", 35: "LED_N", 36: "GND", 37: "NC", 38: "NC", 39: "GND", 40: "LED_P"}

d = json.load(open(SPEC, encoding='utf-8'))
conns = d['connections']

# ── 1) CSI 通道 (A-01..A-10): 改成 31 针针位 ──
CSI_MAP = {"A-01": "CONN_CAM pin18 (MCP) + 100Ω 串阻", "A-02": "CONN_CAM pin17 (MCN) + 100Ω 串阻",
           "A-03": "CONN_CAM pin15 (MDP1) + 100Ω 串阻", "A-04": "CONN_CAM pin14 (MDN1) + 100Ω 串阻",
           "A-05": "CONN_CAM pin12 (MDP2) + 100Ω 串阻", "A-06": "CONN_CAM pin11 (MDN2) + 100Ω 串阻",
           "A-07": "CONN_CAM pin6 (MDP3) + 100Ω 串阻", "A-08": "CONN_CAM pin5 (MDN3) + 100Ω 串阻",
           "A-09": "CONN_CAM pin3 (MDP4) + 100Ω 串阻", "A-10": "CONN_CAM pin2 (MDN4) + 100Ω 串阻"}
for c in conns:
    if c['id'] in CSI_MAP:
        c['conn'] = CSI_MAP[c['id']]
        c['dnp'] = '必装'
        c['note'] = '★★11-02 19:5x 按 Radxa Camera 4K 31 针表 (0.3mm): **CSI 改 4-lane 必装** (原 D2/D3 是 DNP 预留)'

# ── 2) DSI 通道 (A-13..A-22): 改成 40 针针位 + 补 A-21/A-22 ──
DSI_MAP = {"A-13": "CONN_LIGHT pin15 (MIPI_CKP) + R_SEL_CK 0Ω", "A-14": "CONN_LIGHT pin14 (MIPI_CKN) + 100Ω 对地端接",
           "A-15": "CONN_LIGHT pin9 (MIPI_0P) + R_SEL_D0 0Ω", "A-16": "CONN_LIGHT pin8 (MIPI_0N) + 100Ω 对地端接",
           "A-17": "CONN_LIGHT pin12 (MIPI_1P) + R_SEL_D1 0Ω", "A-18": "CONN_LIGHT pin11 (MIPI_1N) + 100Ω 对地端接",
           "A-19": "CONN_LIGHT pin18 (MIPI_2P) + R_SEL_D2 0Ω", "A-20": "CONN_LIGHT pin17 (MIPI_2N) + 100Ω 对地端接"}
for c in conns:
    if c['id'] in DSI_MAP:
        c['conn'] = DSI_MAP[c['id']]
        c['dnp'] = '必装'
        c['note'] = '★★11-02 19:5x 按 Radxa Display 8HD/10FHD 40 针表 (0.5mm)'
have = {c['id'] for c in conns}
if 'A-21' not in have:
    base = [c for c in conns if c['id'] == 'A-19'][0]
    for cid, sig, pin_p, pin_n in (('A-21', 'DSI_D0_D3_P', 'CONN_LIGHT pin21 (MIPI_3P) + R_SEL_D3 0Ω', None),
                                  ('A-22', 'DSI_D0_D3_N', 'CONN_LIGHT pin20 (MIPI_3N) + 100Ω 对地端接', None)):
        c = dict(base)
        c['id'] = cid
        c['signal'] = sig
        c['conn'] = pin_p
        c['tp'] = '—'
        c['dnp'] = '必装'
        c['note'] = '★★11-02 19:5x 新增 (DSI 第 4 通道, 按 40 针表: MIPI_3P=21 / MIPI_3N=20)'
        conns.append(c)

json.dump(d, open(SPEC, 'w', encoding='utf-8'), ensure_ascii=True, indent=2)
print('[1] SPEC: CSI/DSI 连接描述改新针位 + 新增 A-21/A-22 (DSI D3)')

# ── 3) 生成器: 连接器脚数描述 18p/16p → 31p/40p + 新增未引出的针脚 ──
g = open(GEN, encoding='utf-8').read()
g2 = re.sub(r'1×18p@0\.5mm[^"]{0,40}', '★31p@0.3mm (Radxa Camera 4K, 座 HIROSE FH35C-31S-0.3SHW(50))', g)
g2 = re.sub(r'1×16p@0\.5mm[^"]{0,40}', '★40p@0.5mm (Radxa Display 8HD/10FHD, 座 FH12-40S-0.5SH 一类)', g2)
open(GEN, 'w', encoding='utf-8').write(g2)
print('[2] 生成器: 连接器脚数描述 18p→31p/0.3mm, 16p→40p/0.5mm')

# ── 4) 针位表导出 (供画图/人核) ──
with open(f'{PROJ}/HW/PCB/FPC_PIN_TABLES.md', 'w', encoding='utf-8') as f:
    f.write("# FPC 针位表 (按真实在售模组)\n\n")
    f.write("## camera: Radxa Camera 4K (IMX415) —— 31p / 0.3mm, 座 HIROSE FH35C-31S-0.3SHW(50)\n\n")
    f.write("| 针 | 定义 | 针 | 定义 |\n|---|---|---|---|\n")
    for i in range(1, 31, 2):
        f.write(f"| {i} | {CAM[i]} | {i+1} | {CAM[i+1]} |\n")
    f.write("\n## display: Radxa Display 8HD/10FHD —— 40p / 0.5mm\n\n")
    f.write("| 针 | 定义 | 针 | 定义 |\n|---|---|---|---|\n")
    for i in range(1, 41, 2):
        f.write(f"| {i} | {DISP[i]} | {i+1} | {DISP.get(i+1,'—')} |\n")
print('[3] 针位表已导出 HW/PCB/FPC_PIN_TABLES.md')
