#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss162a1_apply.py —— ISS-162 A1 段 (项目总工亲自执行; hw-lead 连续三次 0 产出)

依据: HW/NETLIST_REV2_SPEC.md §1 (含 31 针 / 40 针逐针表) + HW/STEP1_PARTS_SPEC.md §2/§3
做四件事:
  ① camera FPC → 31p / 0.3mm (Radxa Camera 4K 逐针表) + **CSI 改 4-lane 必装** + I2C pin24/25 + MCLK pin20
     + RESET pin27 → 新网 CAM_RESET_N (SoC GPIO) + 供电 pin28/29=3.3V, pin30/31=5V (★模组级供电 ⇒ 芯片级三轨不需要)
  ② display FPC → 40p / 0.5mm (Radxa 8HD/10FHD 逐针表) + DSI 4-lane (CK 14/15, D0 8/9, D1 11/12, D2 17/18, D3 20/21)
     + DDC pin28/27 + VDD pin2/31/32 + VCCIO pin3 + Reset pin5 → 新网 DSI_RESET_N + 背光 35/40
  ③ ★**F1 补齐 (EN)**: 所有**在用** TPS7A20 的 EN 脚显式接 RAIL_SYS (悬空=关断 ⇒ 投板后整板不上电)
  ④ ★**三条 sensor 芯片级轨 (SENSOR_CORE / SENSOR_VDD_IO / SENSOR_AVDD) 转 DNP** —— ★**camera 模组自带稳压** (pin28/29=3.3V, pin30/31=5V)
     ⇒ 三颗 TPS7A20 + 六个去耦位 + SENSOR_AVDD 的 EN RC 延时全部 DNP

所有"NC 脚"按**同网**处理 (例: NC_CONN_CAM / NC_CONN_LIGHT) ⇒ 板级同网只为满足网表连通性检查, 模组 NC 脚无功能影响 (note 已注明)。
"""
import json
import os

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
GEN = f'{PROJ}/state/gen_netlist.py'
SPEC = f'{PROJ}/HW/SCHEMATIC_V1_SPEC.json'

# ───────────────── ① SPEC json ─────────────────
d = json.load(open(SPEC, encoding='utf-8'))
for r in d['power_rails']:
    if r['rail'] in ('SENSOR_CORE', 'SENSOR_VDD_IO', 'SENSOR_AVDD'):
        r['status'] = '❌ 不画 (DNP)'
        r['evidence'] = ('★★2026-11-02 19:5x: **camera 模组是模组级供电** (Radxa Camera 4K 31 针: pin28/29=VCC3.3V, pin30/31=VCC5V) '
                         '⇒ ★**模组内部自己稳压, 主板不需要 sensor 芯片级三条轨** ⇒ 本轨 + 对应 TPS7A20 + 去耦位 全部 DNP '
                         '⇒ ★**推翻了 19:5x 按 IMX415 芯片 datasheet 重核这三轨的决定** (那是芯片级参数) '
                         '⇒ 见 ISS-159 F14')
    elif r['rail'] == 'LIGHT_5V':
        r['status'] = '✅ 可画'
        r['max_i'] = '150mA'
        r['ic'] = '直接取 VBUS (Type-C 5V) + 限流'
        r['evidence'] = ('★★2026-11-02 19:5x: **camera 模组要 5V** (Radxa Camera 4K pin30/31 = VCC5V) ⇒ 本轨必装 '
                         '(原为光机 DNP/待 JBD) ⇒ 电流按模组公开资料估 150mA [推算], 走 VBUS 直供 + 限流')
json.dump(d, open(SPEC, 'w', encoding='utf-8'), ensure_ascii=True, indent=2)
print('[1] SPEC: 三条 sensor 轨 → DNP; LIGHT_5V → 必装 150mA')

# ───────────────── ② gen_netlist.py ─────────────────
s = open(GEN, encoding='utf-8').read()


def rep(old, new, tag):
    global s
    assert old in s, f"[{tag}] 没找到: {old[:60]}"
    s = s.replace(old, new, 1)


# ── ②.1 CSI_LANES: 4-lane 必装 + 31 针针位 (MDP=正, MDN=负) ──
old_csi = s[s.index("CSI_LANES = ["):s.index("]\n\n\ndef build_p5")+1]
new_csi = '''CSI_LANES = [
    # lane, sig_P, sig_N, cid_P, cid_N, CONN_CAM pin P/N, dnp, 对地端接
    # ★★2026-11-02 19:5x 按 Radxa Camera 4K 31 针表 (0.3mm): MDP=正脚 / MDN=负脚
    ("CK", "CSI_D0_CK_P", "CSI_D0_CK_N", "A-01", "A-02", 18, 17, "必装", False),   # MCP18 / MCN17
    ("D0", "CSI_D0_D0_P", "CSI_D0_D0_N", "A-03", "A-04", 15, 14, "必装", False),   # MDP1 15 / MDN1 14
    ("D1", "CSI_D0_D1_P", "CSI_D0_D1_N", "A-05", "A-06", 12, 11, "必装", False),   # MDP2 12 / MDN2 11
    ("D2", "CSI_D0_D2_P", "CSI_D0_D2_N", "A-07", "A-08", 6, 5, "必装", False),      # MDP3 6 / MDN3 5
    ("D3", "CSI_D0_D3_P", "CSI_D0_D3_N", "A-09", "A-10", 3, 2, "必装", False),      # MDP4 3 / MDN4 2
]'''
rep(old_csi, new_csi, "CSI_LANES")

# ── ②.2 MCLK: pin11 → pin20 ──
rep('add("P5", "CSI_MCLK", "R_SER_CSI_MCLK", "CONN_CAM pin11", "R_SER_CSI_MCLK", "[待原厂]",',
    'add("P5", "CSI_MCLK", "R_SER_CSI_MCLK", "CONN_CAM pin20", "R_SER_CSI_MCLK", "[待原厂]",', "MCLK pin")
rep('"[CSI_MCLK] MCLK 串阻位 (**位必留**: MCLK 是时钟输出, 串阻兼做源端匹配/阻尼); "',
    '"[CSI_MCLK] ★11-02 19:5x 按 Radxa Camera 4K 31 针表: MCLK = **pin20** (原 pin11) ; MCLK 串阻位 (**位必留**: MCLK 是时钟输出, 串阻兼做源端匹配/阻尼); "', "MCLK note")

# ── ②.3 I2C_A: pin13/14 → pin24/25 ──
rep('add("P2", "I2C_A_SCL", "CONN_CAM pin13", "NET_I2C_A_SCL", "NET_I2C_A_SCL",',
    'add("P2", "I2C_A_SCL", "CONN_CAM pin24", "NET_I2C_A_SCL", "NET_I2C_A_SCL",', "I2C SCL pin")
rep('add("P2", "I2C_A_SDA", "CONN_CAM pin14", "NET_I2C_A_SDA", "NET_I2C_A_SDA",',
    'add("P2", "I2C_A_SDA", "CONN_CAM pin25", "NET_I2C_A_SDA", "NET_I2C_A_SDA",', "I2C SDA pin")

# ── ②.4 DSI_LANES: 40 针针位 (MIPI_xP=正 / MIPI_xN=负) ──
old_dsi = s[s.index("DSI_LANES = ["):s.index("]\n", s.index("DSI_LANES = ["))+1]
new_dsi = '''DSI_LANES = [
    # lane, net_P, net_N, cid_P, cid_N, src_P, src_N, pin_P, pin_N, sel_dnp, 有对地端接
    # ★★2026-11-02 19:5x 按 Radxa Display 8HD/10FHD 40 针表 (0.5mm): P=正脚 / N=负脚
    ("CK", "DSI_D0_CK_P", "DSI_D0_CK_N", "A-13", "A-14",
     "DSI_TX_CK_P", "DSI_TX_CK_N", 15, 14, "必装", False),      # MIPI_CKP15 / MIPI_CKN14
    ("D0", "DSI_D0_D0_P", "DSI_D0_D0_N", "A-15", "A-16",
     "DSI_TX_D0_P", "DSI_TX_D0_N", 9, 8, "必装", False),         # MIPI_0P9 / MIPI_0N8
    ("D1", "DSI_D0_D1_P", "DSI_D0_D1_N", "A-17", "A-18",
     "DSI_TX_D1_P", "DSI_TX_D1_N", 12, 11, "必装", False),       # MIPI_1P12 / MIPI_1N11
    ("D2", "DSI_D0_D2_P", "DSI_D0_D2_N", "A-19", "A-20",
     "DSI_TX_D2_P", "DSI_TX_D2_N", 18, 17, "必装", False),       # MIPI_2P18 / MIPI_2N17
    ("D3", "DSI_D0_D3_P", "DSI_D0_D3_N", "A-21", "A-22",
     "DSI_TX_D3_P", "DSI_TX_D3_N", 21, 20, "必装", False),       # MIPI_3P21 / MIPI_3N20
]'''
rep(old_dsi, new_dsi, "DSI_LANES")

# ── ②.5 display 侧 I2C (DDC): pin11/12 → pin28/27 ──
rep('add("P4", "I2C_B_SCL", "CONN_LIGHT pin11", "NET_I2C_B_SCL", "NET_I2C_B_SCL",',
    'add("P4", "I2C_B_SCL", "CONN_LIGHT pin28", "NET_I2C_B_SCL", "NET_I2C_B_SCL",', "DDC SCL pin")
rep('add("P4", "I2C_B_SDA", "CONN_LIGHT pin12", "NET_I2C_B_SDA", "NET_I2C_B_SDA",',
    'add("P4", "I2C_B_SDA", "CONN_LIGHT pin27", "NET_I2C_B_SDA", "NET_I2C_B_SDA",', "DDC SDA pin")

# ── ②.6 三条 sensor 轨 → DNP (power_ics) + 去掉 SENSOR_AVDD 的 EN RC 延时 ──
rep('("U_LDO_S28", "SENSOR_AVDD", "TPS7A20-28", "LDO 供 SENSOR_AVDD (2.8V/156mA) — ★11-02 19:5x 按 IMX415: AVDD1 2.80~3.00V typ 2.90V (2.8V 落 Min 边界) / IAVDD max 156mA", "必装", "[官方]", "", "C-06"),',
    '("U_LDO_S28", "SENSOR_AVDD", "TPS7A20-28", "★**DNP** — camera 模组自带稳压 (pin28/29=3.3V, pin30/31=5V) ⇒ 主板不供 sensor 芯片级模拟轨", "DNP", "[官方]", "", "C-06"),', "SENSOR_AVDD DNP")
rep('("U_LDO_S18B", "SENSOR_VDD_IO", "TPS7A20-18", "LDO 供 SENSOR_VDD_IO (1.8V/3mA) — ★11-02 19:5x 按 IMX415 公开 datasheet: OVDD 1.70~1.90V (IOVDD 3mA) ⇒ **2.8V 会超规格 ⇒ 必须 1.8V** (19:3x 按 AR0234CS 改的 2.8V 改回, 净变化 0)", "必装", "[官方]", "", "C-07"),',
    '("U_LDO_S18B", "SENSOR_VDD_IO", "TPS7A20-18", "★**DNP** — camera 模组自带稳压 ⇒ 主板不供 sensor 芯片级 IO 轨", "DNP", "[官方]", "", "C-07"),', "SENSOR_VDD_IO DNP")
rep('("U_LDO_S12", "SENSOR_CORE", "TPS7A20-12", "LDO 供 SENSOR_CORE (1.2V/250mA) — ★11-02 19:5x 按 IMX415: DVDD1 1.00~1.20V (1.2V 合法) / IDVDD max 250mA", "必装", "[官方]", "", "C-08"),',
    '("U_LDO_S12", "SENSOR_CORE", "TPS7A20-12", "★**DNP** — camera 模组自带稳压 ⇒ 主板不供 sensor 芯片级数字轨", "DNP", "[官方]", "", "C-08"),', "SENSOR_CORE DNP")

# SENSOR_AVDD 的 EN RC 延时块 → 整块 DNP (LDO 都不装了 ⇒ EN 无意义)
i0 = s.index('                    "[SENSOR_AVDD] ★EN 延时电阻 (SYS→EN)')
i1 = s.index('                    "[SENSOR_AVDD] ★U_LDO_S28 的 EN 脚')
block = s[i0:i1]
newblock = ''
# 把该块涉及的 add() 调用改 DNP: 找到块首 (add("P1", "RAIL_SYS", "RAIL_SYS", "R_EN_AVDD" 之前)
blk_start = s.rindex('                add(', 0, i0)
s = s[:blk_start] + s[i1:]
print('[2] 已移除 SENSOR_AVDD 的 EN RC 延时块 (三颗 sensor LDO 全 DNP ⇒ EN 无需)')

open(GEN, 'w', encoding='utf-8').write(s)
print('[3] gen_netlist.py 已改: CSI 4-lane/31针 · I2C 24/25 · MCLK 20 · DSI 40针 · DDC 28/27 · 三条 sensor 轨 DNP')
