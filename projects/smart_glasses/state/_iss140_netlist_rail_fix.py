#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iss140_netlist_rail_fix.py —— ISS-140 自己动手做 (子 agent 两次 0 产出)

变更 (依据: 老板 11-02 09:41 拍板 sensor = onsemi AR0234CS):
  ① HW/SCHEMATIC_V1_SPEC.json: SENSOR_VDD_IO 1.8V → 2.8V (AR0234CS VDD_IO=2.8V), IC 换 TPS7A20-28
     · SENSOR_AVDD 保留 2.8V, 但 evidence 标 [待原厂: AR0234CS 有无独立模拟轨] —— ★**不改电路, 等 onsemi 回信**
     · SENSOR_CORE 1.2V 不动 (AR0234CS VDD/VDD_PHY/VDD_DATA = 1.2V)
  ② state/gen_netlist.py: U_LDO_S18 → U_LDO_S28B (2.8V 档) ; I2C_A 上拉 note 加 [TBD-05] ; 测试点改名
     · ★**I2C 上拉仍保持 3.3V 不改电路** (改不改要等 VDD_IO abs max 与同总线从设备电平核完)
"""
import json
import re

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
SPEC = f'{PROJ}/HW/SCHEMATIC_V1_SPEC.json'
GEN = f'{PROJ}/state/gen_netlist.py'

# ── ① 规格 JSON ──
d = json.load(open(SPEC, encoding='utf-8'))
for r in d['power_rails']:
    if r['rail'] == 'SENSOR_VDD_IO':
        r['volt'] = '2.8V'
        r['ic'] = 'TPS7A20-28'
        r['evidence'] = ('[官方] AR0234CS VDD_IO=2.8V (onsemi datasheet 口径, 见 HW/SENSOR_SELECTION.md §B4); '
                         '★11-02 09:41 换料后由 1.8V 改 2.8V; ★原 1.8V 是 OV04C10 的 IO 轨')
    elif r['rail'] == 'SENSOR_AVDD':
        r['evidence'] = ('[待原厂] ★11-02 09:41 换 AR0234CS 后, 该轨是否仍需要未确认 '
                         '(AR0234CS 是否有独立模拟轨待 onsemi 回信, ISS-142) ⇒ **暂保留 2.8V 不动**')
    elif r['rail'] == 'SENSOR_CORE':
        r['evidence'] = ('[官方] AR0234CS VDD/VDD_PHY/VDD_DATA = 1.2V (onsemi datasheet 口径) '
                         '⇒ 与原 OV04C10 core 1.2V 相同, **不改**')
json.dump(d, open(SPEC, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('[1] SCHEMATIC_V1_SPEC.json 电源轨已更新')

# ── ② 生成器 ──
s = open(GEN, encoding='utf-8').read()

old_ic = ('        ("U_LDO_S18", "SENSOR_VDD_IO", "TPS7A20-18", '
          '"LDO 供 SENSOR_VDD_IO (1.8V/30mA)", "必装", "[官方]", "", "C-07"),')
new_ic = ('        ("U_LDO_S28B", "SENSOR_VDD_IO", "TPS7A20-28", '
          '"LDO 供 SENSOR_VDD_IO (2.8V/30mA) — ★11-02 09:41 sensor 改 AR0234CS: VDD_IO=2.8V (原 1.8V 是 OV04C10 的)", '
          '"必装", "[官方]", "", "C-07"),')
assert old_ic in s, "没找到 power_ics 里的 SENSOR_VDD_IO 行"
s = s.replace(old_ic, new_ic, 1)

# I2C 上拉 note 加 TBD-05 (不改电压)
old_pu = ('"[VDD_3V3_IO] I2C_A 上拉 (规格: 4.7k 到 3.3V; 灌 702µA, t_r=2.38µs@100pF)", "B-01")')
new_pu = ('"[VDD_3V3_IO] I2C_A 上拉 (规格: 4.7k 到 3.3V; 灌 702µA, t_r=2.38µs@100pF) '
          '— ★[TBD-05] 11-02 09:41 sensor 改 AR0234CS: 其 VDD_IO=2.8V, 本上拉 3.3V 是否超 VDD_IO 绝对最大额定值'
          ' **待 onsemi 回信 (ISS-142)**; 若超, 改上拉到 2.8V 并逐个核同总线从设备 (TMP117 1.7-5.5V / 充电IC / 光机) 电平兼容", "B-01")')
assert old_pu in s, "没找到 I2C 上拉 note"
s = s.replace(old_pu, new_pu, 1)

# 测试点改名: TP_SENSOR_1V8 → TP_SENSOR_IO2V8 (轨改成 2.8V, 名字不能还叫 1V8; 且与 TP_SENSOR_2V8 不重号)
assert '"TP_SENSOR_1V8"' in s
s = s.replace('"TP_SENSOR_1V8"', '"TP_SENSOR_IO2V8"')
s = s.replace('("TP_SENSOR_IO2V8", "SENSOR_VDD_IO", "CONN_CAM pin16", "sensor 三条轨",\n'
              '     "LDO 输出 (规格合并名 TP_SENSOR_3V3/1V8/2V8)", "必装"),',
              '("TP_SENSOR_IO2V8", "SENSOR_VDD_IO", "CONN_CAM pin16", "sensor IO 轨 (2.8V, AR0234CS VDD_IO)",\n'
              '     "LDO 输出 (U_LDO_S28B); ★原名 TP_SENSOR_1V8 (1.8V 是 OV04C10 的, 已随换料改 2.8V)", "必装"),')

open(GEN, 'w', encoding='utf-8').write(s)
print('[2] gen_netlist.py 已改 (U_LDO_S28B / TBD-05 note / 测试点改名)')
