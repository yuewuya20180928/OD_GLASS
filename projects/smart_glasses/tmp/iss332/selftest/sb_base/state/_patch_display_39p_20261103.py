#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_patch_display_39p_20261103.py —— ★display FPC 座从"40p 屏侧编号"改成"39p 板侧编号" (老板 19:29 定的)

★★ 依据 (Radxa 官方, 三个来源互证, 见 HW/PCB/display_39p_pinout.json):
  · 屏侧 40p/0.5mm (面板原生) ↔ **板侧 39p/0.3mm** (原厂转接线 AC013 的板端)
  · **只省掉屏侧第 1 脚 (NC)** ⇒ 其余 39 脚 1:1 直通 ⇒ 换算式: **屏侧脚号 = 板侧脚号 + 1**
  · 板侧座 = **HIROSE FH35C-39S-0.3SHW(50)** (背夹 + 上下双面触点) ⇒ ★与相机侧 FH35C-31S-0.3SHW(50) **同系列**
  · 背光: 板侧 34/35 = LED−(两阴极并联) · 38/39 = LED+(两阳极并联) ⇒ **1 串 2 颗并联**
  · 触控: 板侧 23=TP-RESET · 24=TP-VCC · 25=TP-INT · 26=TP-SDA · 27=TP-SCL
    ⇒ ★**老板 19:29 拍板: demo 不需要触控** ⇒ 这 5 脚我们**不接** (NC)
"""
import ast
import json
import re

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
GEN = f'{PROJ}/state/gen_netlist.py'
GATE = f'{PROJ}/state/check_netlist_pins.py'
TABLES = f'{PROJ}/HW/PCB/FPC_PIN_TABLES.md'
JSONF = f'{PROJ}/HW/PCB/display_39p_pinout.json'


def main():
    d = json.load(open(JSONF, encoding='utf-8'))
    pins = d['pins']

    def sig(n):
        return (pins.get(str(n), {}) or {}).get('signal', '?')

    src = open(GEN, encoding='utf-8').read()
    orig = src

    # ── ① DSI_LANES: 屏侧脚号 → 板侧脚号 (−1) ──
    lane_fix = [
        ('"DSI_TX_CK_P", "DSI_TX_CK_N", "A-13", "A-14",\n     "DSI_TX_CK_P", "DSI_TX_CK_N", 15, 14,',
         '"DSI_TX_CK_P", "DSI_TX_CK_N", "A-13", "A-14",\n     "DSI_TX_CK_P", "DSI_TX_CK_N", 14, 13,'),
        ('"DSI_TX_D0_P", "DSI_TX_D0_N", "A-15", "A-16",\n     "DSI_TX_D0_P", "DSI_TX_D0_N", 9, 8,',
         '"DSI_TX_D0_P", "DSI_TX_D0_N", "A-15", "A-16",\n     "DSI_TX_D0_P", "DSI_TX_D0_N", 8, 7,'),
        ('"DSI_TX_D1_P", "DSI_TX_D1_N", "A-17", "A-18",\n     "DSI_TX_D1_P", "DSI_TX_D1_N", 12, 11,',
         '"DSI_TX_D1_P", "DSI_TX_D1_N", "A-17", "A-18",\n     "DSI_TX_D1_P", "DSI_TX_D1_N", 11, 10,'),
        ('"DSI_TX_D2_P", "DSI_TX_D2_N", "A-19", "A-20",\n     "DSI_TX_D2_P", "DSI_TX_D2_N", 18, 17,',
         '"DSI_TX_D2_P", "DSI_TX_D2_N", "A-19", "A-20",\n     "DSI_TX_D2_P", "DSI_TX_D2_N", 17, 16,'),
        ('"DSI_TX_D3_P", "DSI_TX_D3_N", "A-21", "A-22",\n     "DSI_TX_D3_P", "DSI_TX_D3_N", 21, 20,',
         '"DSI_TX_D3_P", "DSI_TX_D3_N", "A-21", "A-22",\n     "DSI_TX_D3_P", "DSI_TX_D3_N", 20, 19,'),
    ]
    for old, new in lane_fix:
        if old in src:
            src = src.replace(old, new, 1)
        else:
            print(f'  ★ lane 未匹配: {old[:52]}')
    print('[1] DSI lane 脚号 −1')

    # ── ② GND / NC / 电源 / reset / 背光 / 触控 全部换成板侧脚号 ──
    src = src.replace('    _disp_gnd = [7, 10, 13, 16, 19, 22, 23, 29, 30, 33, 34]',
                      '    # ★★2026-11-03 19:3x: 改**板侧 39p** 编号 (屏侧脚号 − 1); 屏侧 pin1=NC 被原厂线省掉\n'
                      '    _disp_gnd = [6, 9, 12, 15, 18, 21, 22, 28, 29, 32, 33]')
    src = src.replace('    _disp_nc = [1, 4, 6, 37, 38]',
                      '    _disp_nc = [3, 5, 36, 37]   # ★屏侧 1(NC) 被原厂线省掉 ⇒ 板上无此脚')
    src = src.replace('for _pn in [2, 31, 32]:', 'for _pn in [1, 30, 31]:')      # VDD_3V3
    src = src.replace('add("P4", "LIGHT_3V3", "CONN_LIGHT pin3", "RAIL_LIGHT_3V3", "CONN_LIGHT", "3.3V (VCCIO)", "NET",',
                      'add("P4", "LIGHT_3V3", "CONN_LIGHT pin2", "RAIL_LIGHT_3V3", "CONN_LIGHT", "3.3V (VCCIO)", "NET",')
    src = src.replace('add("P4", "DSI_RESET_N", "CONN_LIGHT pin5", soc_pin("GPIO_DSI_RESET"),',
                      'add("P4", "DSI_RESET_N", "CONN_LIGHT pin4", soc_pin("GPIO_DSI_RESET"),')
    print('[2] GND/NC/电源/reset 改板侧脚号')

    # ── ③ 触控: 老板拍板 demo 不需要触控 ⇒ 5 根全 NC (删掉 I2C_B 与屏的连线 + TP 电源/复位/中断) ──
    # ★触控行 (TP_VCC/TP_RESET/TP_INT) 的删除由 _patch_display_touch_nc.py 单独做 (多行语句整段删)
    src = src.replace('add("P4", "I2C_B_SCL", "CONN_LIGHT pin28", "NET_I2C_B_SCL", "NET_I2C_B_SCL",',
                      'add("P4", "I2C_B_SCL", "R_PU_I2CB_SCL", "NET_I2C_B_SCL", "NET_I2C_B_SCL",')
    src = src.replace('add("P4", "I2C_B_SDA", "CONN_LIGHT pin27", "NET_I2C_B_SDA", "NET_I2C_B_SDA",',
                      'add("P4", "I2C_B_SDA", "R_PU_I2CB_SDA", "NET_I2C_B_SDA", "NET_I2C_B_SDA",')
    print('[3] 触控 I2C 从屏侧摘掉 (I2C_B 留给板载 TMP117)')

    # ── ④ 背光: 板侧 34/35 = LED−, 38/39 = LED+ (两阴极/两阳极各自并联) ──
    src = src.replace('add("P4", "NET_LED_N", "CONN_LIGHT pin35", "NET_LED_N", "CONN_LIGHT", "LED- (背光负极, 1)", "NET",',
                      'add("P4", "NET_LED_N", "CONN_LIGHT pin34", "NET_LED_N", "CONN_LIGHT", "LED-1 (背光阴极 1/2)", "NET",')
    src = src.replace('add("P4", "NET_LED_N", "CONN_LIGHT pin36", "NET_LED_N", "CONN_LIGHT", "LED- (背光负极, 2)", "NET",',
                      'add("P4", "NET_LED_N", "CONN_LIGHT pin35", "NET_LED_N", "CONN_LIGHT", "LED- (背光阴极 2/2)", "NET",')
    src = src.replace('add("P4", "NET_LED_P", "CONN_LIGHT pin39", "NET_LED_P", "CONN_LIGHT", "LED+ (背光正极, 1)", "NET",',
                      'add("P4", "NET_LED_P", "CONN_LIGHT pin38", "NET_LED_P", "CONN_LIGHT", "LED+1 (背光阳极 1/2)", "NET",')
    src = src.replace('add("P4", "NET_LED_P", "CONN_LIGHT pin40", "NET_LED_P", "CONN_LIGHT", "LED+ (背光正极, 2)", "NET",',
                      'add("P4", "NET_LED_P", "CONN_LIGHT pin39", "NET_LED_P", "CONN_LIGHT", "LED+ (背光阳极 2/2)", "NET",')
    print('[4] 背光改板侧脚号 (34/35 与 38/39)')

    # ── ⑤ 连接器声明行: 型号/位数/脚号偏移口径 ──
    src = src.replace('"★40p@0.5mm (Radxa Display 8HD/10FHD, 座 FH12-40S-0.5SH 一类))", "CONN", "必装", "[待视涯]", "TBD-04",',
                      '"★39p@0.3mm (HIROSE FH35C-39S-0.3SHW(50), 背夹+上下双面触点, ★与相机侧 FH35C-31S 同系列)",\n'
                      '        "CONN", "必装", "[官方]", "",')
    src = src.replace('"显示/光机↔主板连接器; pin1/2=DSI_CK, 3/4=DSI_D0, 5/6=DSI_D1, "',
                      '"★★2026-11-03 19:3x 改为**板侧 39p/0.3mm** (Radxa 原厂转接线 AC013 的板端; ★屏侧原生是 40p/0.5mm); "\n'
                      '        "★**换算式: 屏侧脚号 = 板侧脚号 + 1** (屏侧 pin1=NC 被原厂线省掉, 其余 1:1 直通); "')
    ast.parse(src)
    if src != orig:
        open(GEN, 'w', encoding='utf-8').write(src)
        print('✅ gen_netlist.py 已落盘')

    # ── ⑥ 门禁: CONN_LIGHT 针数 40 → 39 ──
    g = open(GATE, encoding='utf-8').read()
    g2 = g.replace("'CONN_LIGHT': 40,   # Radxa Display 8HD/10FHD 40p/0.5mm",
                    "'CONN_LIGHT': 39,   # ★板侧 39p/0.3mm (FH35C-39S-0.3SHW(50)); 屏侧原生 40p/0.5mm")
    if g2 != g:
        open(GATE, 'w', encoding='utf-8').write(g2)
        print('✅ 门禁针数 40 → 39')

    # ── ⑦ FPC_PIN_TABLES.md: display 段换成板侧 39p 表 (屏侧 40p 表保留作对照) ──
    t = open(TABLES, encoding='utf-8').read()
    rows = ['| 板侧脚 | 信号 | 屏侧脚 | 说明 |', '|---|---|---|---|']
    for i in range(1, 40):
        s = sig(i)
        note = (pins.get(str(i), {}) or {}).get('note', '')
        rows.append(f'| {i} | {s} | {i+1 if i < 39 else "40"} | {str(note)[:60]} |')
    newsec = ('## display: **Radxa Display 8HD** —— ★**板侧 39p / 0.3mm** (屏侧原生 40p / 0.5mm)\n\n'
              '> ★★**2026-11-03 19:3x 换口径**: 板上画的是**板侧 39p/0.3mm 座** '
              '(HIROSE **FH35C-39S-0.3SHW(50)**, 背夹 + 上下双面触点, ★**与相机侧 FH35C-31S-0.3SHW(50) 同系列**);\n'
              '> 原厂转接线 AC013 一头插屏 (40p/0.5mm) 一头插我们的座 ⇒ **我们不用自制排线**;\n'
              '> ★**换算式: 屏侧脚号 = 板侧脚号 + 1** (屏侧 pin1=NC 被原厂线省掉, 其余 39 脚 1:1 直通, 无交叉);\n'
              '> ★老板 19:29 拍板 **demo 不需要触控** ⇒ 板侧 23~27 (TP-RESET/VCC/INT/SDA/SCL) 我们**不接**;\n'
              '> ★背光 = **1 串 2 颗并联** (阴极 34/35 同网, 阳极 38/39 同网) ⇒ 板侧要自带 BOOST+恒流+PWM (ISS-173);\n'
              '> 屏侧 40p 原文表见 `HW/STEP1_PARTS_SPEC.md` §3.1; 39p 表的三个原厂出处见 `HW/PCB/DISPLAY_39P_PINOUT.md`。\n\n'
              + '\n'.join(rows) + '\n')
    t = re.sub(r'## display: \*\*Radxa Display 8HD\*\*.*?(?=\n## |\Z)', newsec, t, flags=re.S)
    if '## display: **Radxa Display 8HD** —— ★**板侧 39p' not in t:
        t = re.sub(r'## display:.*?(?=\n## |\Z)', newsec, t, flags=re.S)
    open(TABLES, 'w', encoding='utf-8').write(t)
    print('✅ FPC_PIN_TABLES.md display 段已换板侧 39p 表')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
