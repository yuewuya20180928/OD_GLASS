#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iss165_som_map2.py —— A2 段补尾 (安全版: 只分配 LED 的空闲 GPIO, 不删任何代码)

★三条发现 (来自 FET3576-C 公开逐针表):
  ① **XTAL_0/1 (晶振) 在核心板上** ⇒ ★**主板不接晶振** ⇒ 主板侧的晶体/负载电容行 **标 DNP 不装**
     ⇒ ★**用 DNP 标记, 不用删代码** (删多行 add() 会破坏语法 ⇒ 已踩过坑)
  ② **LED_0/LED_1 是动态名** ⇒ 需前缀匹配 + 从表里分配空闲 GPIO
  ③ **FSIN 在 SOM 上无对应引脚** ⇒ 功能在 SOM 内部 ⇒ 主板不接 ⇒ **DNP / 待核**
"""
import csv
import json
import os
import re

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
GEN = f'{PROJ}/state/gen_netlist.py'

rows = list(csv.DictReader(open(f'{PROJ}/HW/PCB/FET3576C_PIN_TABLE.csv', encoding='utf-8')))
bypin, gpios = {}, []
for r in rows:
    num = (r.get('num') or '').strip()
    if not num.isdigit():
        continue
    bypin[num] = r
    sig = (r.get('signal') or '').strip()
    if re.match(r'^GPIO\d+_[A-Z]\d+_d$', sig):
        gpios.append((num, sig))

MAPJ = json.load(open(f'{PROJ}/HW/PCB/som_pin_map.json', encoding='utf-8'))
mapping = MAPJ['mapping']
used = {m['num'] for m in mapping.values()}
free = [(n, sg) for (n, sg) in gpios if n not in used]

src = open(GEN, encoding='utf-8').read()
led = {}
for i, col in enumerate(('0', '1')):
    if i < len(free):
        n, sg = free[i]
        used.add(n)
        led[col] = {'somsig': sg, 'num': n, 'ball': bypin[n].get('ball', ''), 'vol': bypin[n].get('vol', '')}
        src = src.replace(f'SoC[RK3572].LED_{col}', f'J_SOM pin{n}')
        mapping[f'LED_{col}'] = led[col]

# XTAL / FSIN: ★用 DNP 标记 (不删代码)
src = src.replace('conn_row(by_id, cid, "P8", f"XTAL_{pol}", f"SoC[RK3572].XTAL_{pol}", "X1", f"NET_XTAL_{pol}")',
                  'conn_row(by_id, cid, "P8", f"XTAL_{pol}", f"SoC[RK3572].XTAL_{pol}", "X1", f"NET_XTAL_{pol}")  # ★DNP: 晶振在 SOM 上, 主板不装')
src = src.replace('conn_row(by_id, "B-09", "P8", "FSIN", "SoC[RK3572].FSIN", "R_SER_FSIN", "NET_FSIN")',
                  'conn_row(by_id, "B-09", "P8", "FSIN", "SoC[RK3572].FSIN", "R_SER_FSIN", "NET_FSIN")  # ★DNP: SOM 上无对应脚, 主板不接 (待核)')

open(GEN, 'w', encoding='utf-8').write(src)
import ast
ast.parse(src)

MAPJ['mapping'] = mapping
MAPJ['unmapped'] = []
MAPJ['notes'] = [
    "★XTAL_0/1 晶振: **在 SOM 板上** ⇒ 主板不装 (晶体与负载电容都在核心板上) ⇒ 主板侧 XTAL 相关器件 DNP",
    "★FSIN: SOM 逐针表里无对应脚 ⇒ 功能在 SOM 内部 ⇒ 主板不接 ⇒ DNP / 待核",
    f"★LED_0/LED_1 → 分配空闲 GPIO: {led}",
]
json.dump(MAPJ, open(f'{PROJ}/HW/PCB/som_pin_map.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
with open(f'{PROJ}/HW/PCB/SOM_PIN_ASSIGNMENT.md', 'a', encoding='utf-8') as f:
    f.write("\n## ★A2 段补尾\n\n| 我们的信号 | SOM 脚名 | 座脚号 | CPU 球号 | 电平 |\n|---|---|---|---|---|\n")
    for col, m in led.items():
        f.write(f"| LED_{col} | {m['somsig']} | pin{m['num']} | {m['ball']} | {m['vol']} |\n")
    f.write("\n")
    for n in MAPJ['notes']:
        f.write(f"- {n}\n")
print(f"[1] LED 分配: {led} · XTAL/FSIN 标 DNP")
print(f"[2] 映射总数 {len(mapping)}")
