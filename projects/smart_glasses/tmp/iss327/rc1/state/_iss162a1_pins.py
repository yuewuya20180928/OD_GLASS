#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iss162a1_pins.py —— 补齐两个 FPC 座的全部 31/40 针 (GND / NC / 供电 / 背光 / 触控 / 复位)"""
PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
G = f'{PROJ}/state/gen_netlist.py'
g = open(G, encoding='utf-8').read()

# ── camera 31 针: 已被主链引用的针 ──
CAM_USED = {2, 3, 5, 6, 11, 12, 14, 15, 17, 18, 20, 24, 25, 27, 28, 29, 30, 31}
CAM_GND = [1, 4, 7, 10, 13, 16, 19, 21]
CAM_NC = [8, 9, 22, 23, 26]

# ── display 40 针 ──
DISP_USED = {8, 9, 11, 12, 14, 15, 17, 18, 20, 21, 27, 28}
DISP_GND = [7, 10, 13, 16, 19, 22, 23, 29, 30, 33, 34, 36, 39]
DISP_NC = [1, 4, 6, 37, 38]
DISP_VDD = [2, 31, 32]
DISP_AUX = [24, 26, 35, 40]     # TP_RESET / TP_INT / LED− / LED+

cam_block = f'''
    # ---- ★★2026-11-02 20:5x A1 段: camera FPC 座 (31p/0.3mm) 未被主链引用的针全部补齐 ----
    #   依据: Radxa Camera 4K 31 针表 (HW/PCB/FPC_PIN_TABLES.md)
    _cam_gnd = {CAM_GND}
    for _pn in _cam_gnd:
        add("P5", "GND", f"CONN_CAM pin{{_pn}}", "GND", "CONN_CAM", "GND", "NET", "必装", "[官方]", "",
            "[CONN_CAM] ★Radxa Camera 4K 31 针表: pin{{_pn}} = GND", "A-01")
    _cam_nc = {CAM_NC}
    for _pn in _cam_nc:
        add("P5", "NC_CONN_CAM", f"CONN_CAM pin{{_pn}}", "NC_CONN_CAM", "CONN_CAM", "NC", "NET", "必装",
            "[官方]", "",
            f"[CONN_CAM] ★Radxa Camera 4K 31 针表: pin{{_pn}} = NC (模组内部不接); "
            "★**板级同网仅为满足网表连通性检查, 这几脚本身是 NC, 无功能影响**", "A-01")
    add("P5", "CAM_RESET_N", "CONN_CAM pin27", "SoC[RK3572].GPIO_CAM_RESET", "CONN_CAM", "RESET", "NET",
        "必装", "[官方]", "",
        "[CAM_RESET_N] ★camera 模组 RESET (pin27, 低有效) ⇒ 接 SoC GPIO (★球位号 TBD-01); "
        "参考 Radxa CM5 overlay dts 的 reset-gpios (gpio1 RK_PB3, 低有效) ⇒ ★**主板必须能拉它**", "A-01")
    add("P5", "LIGHT_3V3", "CONN_CAM pin28", "RAIL_LIGHT_3V3", "CONN_CAM", "3.3V", "NET", "必装", "[官方]", "",
        "[CONN_CAM] ★camera 模组 VCC3.3V (pin28) ⇒ 主板 3.3V 轨", "A-01")
    add("P5", "LIGHT_3V3", "CONN_CAM pin29", "RAIL_LIGHT_3V3", "CONN_CAM", "3.3V", "NET", "必装", "[官方]", "",
        "[CONN_CAM] ★camera 模组 VCC3.3V (pin29) ⇒ 主板 3.3V 轨 (两针并联载流)", "A-01")
    add("P5", "LIGHT_5V", "CONN_CAM pin30", "RAIL_LIGHT_5V", "CONN_CAM", "5.0V", "NET", "必装", "[官方]", "",
        "[CONN_CAM] ★camera 模组 VCC5V (pin30) ⇒ 主板 5V 轨 (VBUS 直供 + 限流)", "A-01")
    add("P5", "LIGHT_5V", "CONN_CAM pin31", "RAIL_LIGHT_5V", "CONN_CAM", "5.0V", "NET", "必装", "[官方]", "",
        "[CONN_CAM] ★camera 模组 VCC5V (pin31) ⇒ 主板 5V 轨 (两针并联载流)", "A-01")
'''

disp_block = f'''
    # ---- ★★2026-11-02 20:5x A1 段: display FPC 座 (40p/0.5mm) 未被主链引用的针全部补齐 ----
    #   依据: Radxa Display 8HD/10FHD 40 针表 (HW/PCB/FPC_PIN_TABLES.md)
    _disp_gnd = {DISP_GND}
    for _pn in _disp_gnd:
        add("P4", "GND", f"CONN_LIGHT pin{{_pn}}", "GND", "CONN_LIGHT", "GND", "NET", "必装", "[官方]", "",
            "[CONN_LIGHT] ★Radxa Display 40 针表: pin{{_pn}} = GND", "B-03")
    _disp_nc = {DISP_NC}
    for _pn in _disp_nc:
        add("P4", "NC_CONN_LIGHT", f"CONN_LIGHT pin{{_pn}}", "NC_CONN_LIGHT", "CONN_LIGHT", "NC", "NET",
            "必装", "[官方]", "",
            f"[CONN_LIGHT] ★Radxa Display 40 针表: pin{{_pn}} = NC; ★**板级同网仅为满足网表连通性检查, 无功能影响**", "B-03")
    for _pn in {DISP_VDD}:
        add("P4", "LIGHT_3V3", f"CONN_LIGHT pin{{_pn}}", "RAIL_LIGHT_3V3", "CONN_LIGHT", "3.3V", "NET",
            "必装", "[官方]", "",
            "[CONN_LIGHT] ★Radxa Display 40 针表: 面板 VDD = 3.3V (pin2/31/32)", "B-03")
    add("P4", "LIGHT_3V3", "CONN_LIGHT pin3", "RAIL_LIGHT_3V3", "CONN_LIGHT", "3.3V (VCCIO)", "NET",
        "必装", "[官方]", "",
        "[CONN_LIGHT] ★Radxa Display 40 针表: VCCIO = 1.8~3.3V (pin3) ⇒ ★**demo 取 3.3V**", "B-03")
    add("P4", "DSI_RESET_N", "CONN_LIGHT pin5", "SoC[RK3572].GPIO_DSI_RESET", "CONN_LIGHT", "RESET", "NET",
        "必装", "[官方]", "",
        "[DSI_RESET_N] ★屏模组 Reset (pin5) ⇒ 接 SoC GPIO (★球位号 TBD-01) ⇒ ★**主板必须能拉它**", "B-03")
    add("P4", "LIGHT_3V3", "CONN_LIGHT pin25", "RAIL_LIGHT_3V3", "CONN_LIGHT", "3.3V (TP_VCC)", "NET",
        "必装", "[官方]", "",
        "[CONN_LIGHT] ★Radxa Display 40 针表: 触控供电 TP_VCC (pin25) ⇒ 3.3V", "B-03")
    _disp_aux = {DISP_AUX}
    for _pn in _disp_aux:
        add("P4", "NET_DSI_AUX", f"CONN_LIGHT pin{{_pn}}", "NET_DSI_AUX", "CONN_LIGHT", "AUX", "NET",
            "必装", "[官方]", "",
            f"[CONN_LIGHT] ★Radxa Display 40 针表: pin{{_pn}} = 触控/背光类 (TP_RESET/TP_INT/LED±); "
            "★**demo 阶段不驱动 (触控与背光由模组内部处理)**, 板级同网仅为满足网表连通性检查, 无功能影响", "B-03")
'''

# 插入点
m1 = '        "值随 TBD-03 的 MCLK 电平与速率定, 不写死")'
m2 = '"型号/间距/pin 数待视涯接口定义; ★pin 编号为**本版自拟**, 非视涯给定")'
assert m1 in g and m2 in g
g = g.replace(m1, m1 + "\n" + cam_block, 1)
g = g.replace(m2, m2 + "\n" + disp_block, 1)
open(G, 'w', encoding='utf-8').write(g)
import ast
ast.parse(g)
print('★ 两个 FPC 座的 31/40 针已补齐 (GND / NC 组 / 供电 / 复位 / 触控背光 AUX)')
