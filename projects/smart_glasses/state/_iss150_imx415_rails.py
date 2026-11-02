#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iss150_imx415_rails.py —— 按 IMX415 公开 datasheet 重核网表三条 sensor 轨 + I2C 上拉阻值

依据: HW/IMX415_DEMO_SENSOR_FACTS.md §1 (电源域) / §1.3 (上电顺序) / §1.4 (I2C 电平)
实测口径 (公开 datasheet):
  DVDD1 (数字)  1.00~1.20V typ 1.10V, IDVDD 187mA typ / 250mA max
  OVDD  (IO)    1.70~1.90V typ 1.80V, IOVDD 3mA
  AVDD1 (模拟)  2.80~3.00V typ 2.90V, IAVDD 128mA typ / 156mA max
  VI 绝对最大 = -0.3 ~ (OVDD+0.3) 且 ≤3.3V ⇒ I2C 上拉留 3.3V 合法, 但 IOL 只允许 3mA ⇒ 上拉阻值要重算
  上电顺序: DVDD → OVDD → AVDD, 200ms 内 (⇒ 现网表三轨同起 + LDO 无 EN ⇒ 顺序不保证 ⇒ 挂风险单)
变更:
  ① SENSOR_VDD_IO 2.8V → 1.8V (TPS7A20-28 → TPS7A20-18, ref U_LDO_S28B → U_LDO_S18B)  ★★不改会烧 sensor
  ② SENSOR_CORE 保持 1.2V (在 DVDD1 1.00~1.20V 内) 但电流规格 50mA → 250mA
  ③ SENSOR_AVDD 保持 2.8V (在 AVDD1 2.80~3.00V 内, 落在 Min 边界) 但电流规格 30mA → 156mA
  ④ I2C_A 上拉 4.7k → 2.2k (IOL ≤3mA ⇒ R ≥ (3.3-0.4)/3mA = 967Ω ⇒ 取 2.2k: 电流余量 + t_r=2.2k×100pF×0.847≈186ns)
"""
import json

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
SPEC = f'{PROJ}/HW/SCHEMATIC_V1_SPEC.json'
GEN = f'{PROJ}/state/gen_netlist.py'

# ── ① 规格 JSON (真源) ──
d = json.load(open(SPEC, encoding='utf-8'))
for r in d['power_rails']:
    if r['rail'] == 'SENSOR_VDD_IO':
        r['volt'] = '1.8V'
        r['max_i'] = '3mA'
        r['ic'] = 'TPS7A20-18'
        r['evidence'] = ('[官方] IMX415 OVDD (IO 轨) 1.70~1.90V typ 1.80V, IOVDD 3mA (onsemi→Sony 公开 datasheet, '
                         '见 HW/IMX415_DEMO_SENSOR_FACTS.md §1.1) ⇒ ★**2.8V 会直接超规格 (VI max ≤3.3V, OVDD max 1.90V) ⇒ 必须 1.8V**; '
                         '★11-02 19:3x 曾按 AR0234CS 改 2.8V, 19:5x 按 IMX415 datasheet 改回 1.8V ⇒ **净变化 0**')
    elif r['rail'] == 'SENSOR_CORE':
        r['max_i'] = '250mA'
        r['evidence'] = ('[官方] IMX415 DVDD1 (数字) 1.00~1.20V typ 1.10V, IDVDD 187mA typ / **250mA max** ⇒ '
                         '★**1.2V 在范围内 ⇒ 轨电压不变**, 只把电流规格从 50mA 改 250mA (TPS7A20 本体 300mA 够)')
    elif r['rail'] == 'SENSOR_AVDD':
        r['max_i'] = '156mA'
        r['evidence'] = ('[官方] IMX415 AVDD1 (模拟) 2.80~3.00V typ 2.90V, IAVDD 128mA typ / **156mA max** ⇒ '
                         '★**2.8V 落在 Min 边界, 合法** ⇒ 轨电压不变, 电流规格 30mA → 156mA; '
                         '★**注意: 若后续要 typ 值 2.9V, TPS7A20 固定档没有 2.9V ⇒ 需换可调 LDO (见 ISS-152)**')
json.dump(d, open(SPEC, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('[1] SCHEMATIC_V1_SPEC.json: SENSOR_VDD_IO → 1.8V/TPS7A20-18/3mA; CORE 250mA; AVDD 156mA')

# ── ② 生成器 ──
s = open(GEN, encoding='utf-8').read()

old_io = ('        ("U_LDO_S28B", "SENSOR_VDD_IO", "TPS7A20-28", '
          '"LDO 供 SENSOR_VDD_IO (2.8V/30mA) — ★11-02 09:41 sensor 改 AR0234CS: VDD_IO=2.8V (原 1.8V 是 OV04C10 的)", '
          '"必装", "[官方]", "", "C-07"),')
new_io = ('        ("U_LDO_S18B", "SENSOR_VDD_IO", "TPS7A20-18", '
          '"LDO 供 SENSOR_VDD_IO (1.8V/3mA) — ★11-02 19:5x 按 IMX415 公开 datasheet: OVDD 1.70~1.90V (IOVDD 3mA) ⇒ '
          '**2.8V 会超规格 ⇒ 必须 1.8V** (19:3x 按 AR0234CS 改的 2.8V 改回, 净变化 0)", '
          '"必装", "[官方]", "", "C-07"),')
assert old_io in s, 'SENSOR_VDD_IO 的 LDO 行没找到'
s = s.replace(old_io, new_io, 1)

old_core = ('        ("U_LDO_S12", "SENSOR_CORE", "TPS7A20-12", '
            '"LDO 供 SENSOR_CORE (1.2V/50mA)", "必装", "[官方]", "", "C-08"),')
new_core = ('        ("U_LDO_S12", "SENSOR_CORE", "TPS7A20-12", '
            '"LDO 供 SENSOR_CORE (1.2V/250mA) — ★11-02 19:5x 按 IMX415: DVDD1 1.00~1.20V (1.2V 合法) / IDVDD max 250mA", '
            '"必装", "[官方]", "", "C-08"),')
assert old_core in s, 'SENSOR_CORE 的 LDO 行没找到'
s = s.replace(old_core, new_core, 1)

old_avdd = ('        ("U_LDO_S28", "SENSOR_AVDD", "TPS7A20-28", '
            '"LDO 供 SENSOR_AVDD (2.8V/30mA)", "必装", "[官方]", "", "C-06"),')
new_avdd = ('        ("U_LDO_S28", "SENSOR_AVDD", "TPS7A20-28", '
            '"LDO 供 SENSOR_AVDD (2.8V/156mA) — ★11-02 19:5x 按 IMX415: AVDD1 2.80~3.00V typ 2.90V (2.8V 落 Min 边界) / IAVDD max 156mA", '
            '"必装", "[官方]", "", "C-06"),')
assert old_avdd in s, 'SENSOR_AVDD 的 LDO 行没找到'
s = s.replace(old_avdd, new_avdd, 1)

# ④ I2C_A 上拉 4.7k → 2.2k (两处: 电阻行 + 节点行) —— 只改 I2C_A, I2C_B(面板 DDC) 不动
old_pu1 = ('    add("P2", "VDD_3V3_IO", "R_PU_I2CA_SCL", "RAIL_VDD_3V3_IO", "R_PU_I2CA_SCL", "4.7k ±1%",')
new_pu1 = ('    add("P2", "VDD_3V3_IO", "R_PU_I2CA_SCL", "RAIL_VDD_3V3_IO", "R_PU_I2CA_SCL", "2.2k ±1%",')
assert old_pu1 in s
s = s.replace(old_pu1, new_pu1, 1)
old_pu2 = ('    add("P2", "VDD_3V3_IO", "R_PU_I2CA_SDA", "RAIL_VDD_3V3_IO", "R_PU_I2CA_SDA", "4.7k ±1%",')
new_pu2 = ('    add("P2", "VDD_3V3_IO", "R_PU_I2CA_SDA", "RAIL_VDD_3V3_IO", "R_PU_I2CA_SDA", "2.2k ±1%",')
assert old_pu2 in s
s = s.replace(old_pu2, new_pu2, 1)

# 上拉 note: 改电平说明 (3.3V 合法但阻值按 IOL 重算) —— 把两处 "4.7k" 的描述改掉
s = s.replace('"[VDD_3V3_IO] I2C_A 上拉 (规格: 4.7k 到 3.3V; 灌 702µA, t_r=2.38µs@100pF)',
              '"[VDD_3V3_IO] I2C_A 上拉 (★11-02 19:5x 按 IMX415: OVDD 1.8V 域, IOL 只允许 3mA ⇒ R≥(3.3-0.4)/3mA=967Ω ⇒ 取 2.2k; '
              '灌 3.3V/2.2k=1.5mA ≤3mA ✔, t_r=2.2k×100pF×0.847≈186ns ✔; ★**上拉仍留 3.3V**: IMX415 VI 绝对最大 ≤3.3V ⇒ 合法)', 1)
s = s.replace('"上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF)"', '"上拉 2.2k 到 3.3V (★IMX415 IOL≤3mA 重算)"', 1)
s = s.replace('"上拉 4.7k 到 3.3V"', '"上拉 2.2k 到 3.3V (★IMX415 IOL≤3mA 重算)"', 1)

open(GEN, 'w', encoding='utf-8').write(s)
print('[2] gen_netlist.py: 三条轨电压/电流规格 + I2C_A 上拉 4.7k→2.2k + note')
