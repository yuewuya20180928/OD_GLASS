#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_patch_netlist_pins2.py —— ★针脚门禁跑出来的第二批修复 (2026-11-03 09:5x)

门禁 `state/check_netlist_pins.py` 跑出 8 处"一个针脚多个网", 逐条定性:
  ① CONN_LIGHT pin13/14/15 —— **测试点挂错脚** + **LIGHT_5V 挂错脚**
     (40 针表: pin13=GND · pin14=MIPI_CKN · pin15=MIPI_CKP; ★**display 模组根本没有 5V 输入脚**)
  ② CONN_USB pin1 / J_CHG pin1 —— 连接器"声明行"又占了 pin1 (第一批只改了 FPC 两家)
  ③ U_CHG pin4 —— BQ25896 的 STAT 是**单个开漏输出**, 却挂了两个网 (CHG_STAT / CHG_STAT_L)
     ⇒ 合并成一个网; ★**并删掉充电板本地那个 5V 上拉** (它会把 5V 送到 SoC 的 3.3V 开漏输入 ⇒ 过压)
  ④ U_CHG pin17/18 (PGND) —— TS 专用回流跨铰链那套是 **V1.2 电池搬到镜脚之前的残留**
     (NTC 已在充电板上 ⇒ 回流根本不需要跨铰链) ⇒ 删掉跨铰链行, NTC 回流直接接 PGND
  ⑤ C4 跨板 4 个件 —— 充电板件没进 CHG_BOARD_REFS ⇒ **按 P10 页 (充电板整页) 的 ref 全集补齐**

用法: python3 state/_patch_netlist_pins2.py
"""
import ast
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _patch_netlist_fpc_pins import delete_stmt, replace  # noqa: E402

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
GEN = f'{PROJ}/state/gen_netlist.py'
P10 = f'{PROJ}/state/p10_rows.json'


def main():
    src = open(GEN, encoding='utf-8').read()
    orig = src

    print('=== 1. TS 专用回流: 删掉跨铰链残留, NTC 回流直接接 PGND ===')
    src, _ = replace(src,
                     'add("P1", "TS_BAT", "R_NTC_BAT", "TS_RTN", "R_NTC_BAT",',
                     'add("P1", "TS_BAT", "R_NTC_BAT", "PGND", "R_NTC_BAT",',
                     'NTC 另一端 → PGND')
    src, _ = replace(src,
                     'add("P1", "TS_BAT", "R_TS_PULL", "TS_RTN", "R_TS_PULL",',
                     'add("P1", "TS_BAT", "R_TS_PULL", "PGND", "R_TS_PULL",',
                     'R_TS_PULL 下端 → PGND')
    src, _ = delete_stmt(src, 'add("P1", "TS_RTN", "R_NTC_BAT", "TS_RTN", "R_NTC_BAT",',
                          'TS_RTN 声明行')
    src, _ = delete_stmt(src, 'add("P1", "TS_RTN", "J_CHG pin10", "J_CHG", "TS_RTN",',
                          'TS_RTN ↔ J_CHG pin10 (跨铰链残留)')
    src, _ = delete_stmt(src, 'add("P1", "TS_RTN", "J_CHG pin10", "U_CHG pin17+pin18",',
                          'TS_RTN ↔ U_CHG PGND (跨铰链残留)')
    src, _ = replace(src,
                     'add("P1", "TS_RTN", "R_TS_PULL", "TS_RTN", "R_TS_PULL",',
                     'add("P1", "PGND", "R_TS_PULL", "PGND", "R_TS_PULL",',
                     'R_TS_PULL 的 TS_RTN 行 → PGND')

    print('=== 2. display 模组没有 5V 输入脚 + 测试点挂错脚 ===')
    src, _ = delete_stmt(src, 'add("P1", "LIGHT_5V", "RAIL_LIGHT_5V", "CONN_LIGHT pin15",',
                          'LIGHT_5V → CONN_LIGHT pin15 (40 针表里 pin15=MIPI_CKP!)')
    src, _ = replace(src,
                     '("TP_LIGHT_3V3", "LIGHT_3V3", "CONN_LIGHT pin13",',
                     '("TP_LIGHT_3V3", "LIGHT_3V3", "CONN_LIGHT pin31",',
                     'TP_LIGHT_3V3 改挂 pin31 (VDD_3V3)')
    src, _ = delete_stmt(src, '("TP_LIGHT_1V8", "LIGHT_1V8", "CONN_LIGHT pin14",',
                          'TP_LIGHT_1V8 (display 无 1.8V 脚, 且 pin14=MIPI_CKN)')

    print('=== 3. 跨铰链连接器声明行不再占 pin1 ===')
    src, _ = replace(src,
                     'add("P9", "HINGE_USB", "CONN_USB", "CONN_USB pin1", "CONN_USB",',
                     'add("P9", "HINGE_USB", "CONN_USB", "CONN_USB", "CONN_USB",',
                     'HINGE_USB 声明行')
    src, _ = replace(src,
                     'add("P9", "HINGE_CHG", "J_CHG", "J_CHG pin1", "J_CHG",',
                     'add("P9", "HINGE_CHG", "J_CHG", "J_CHG", "J_CHG",',
                     'HINGE_CHG 声明行')

    print('=== 4. 充电板件全部归 CHG_BOARD (按 P10 页 ref 全集) ===')
    rows10 = json.load(open(P10, encoding='utf-8'))
    refs10 = sorted({(r.get('ref') or '').strip() for r in rows10} - {''})
    # 已在 CHG_BOARD_REFS 里的不重复加
    import re as _re
    m = _re.search(r'CHG_BOARD_REFS = \{(.*?)\n\}', src, _re.S)
    body = m.group(1)
    have = set(_re.findall(r'"([A-Za-z_0-9]+)"', body))
    add_list = [r for r in refs10 if r not in have and not r.startswith(('NET_', 'RAIL_'))]
    if add_list:
        ins = '    ' + ', '.join(f'"{r}"' for r in add_list) + ',\n'
        src = src.replace('CHG_BOARD_REFS = {\n', 'CHG_BOARD_REFS = {\n' + ins, 1)
    print(f'  [补] CHG_BOARD_REFS += {len(add_list)} 个: {add_list[:14]}')

    ast.parse(src)
    if src == orig:
        print('\n★★ gen_netlist.py 无改动')
    else:
        open(GEN, 'w', encoding='utf-8').write(src)
        print(f'\n✅ {GEN} 已落盘 (语法自检通过)')

    print('\n=== 5. p10_rows.json: STAT 单网 + 删 5V 上拉 ===')
    rows = json.load(open(P10, encoding='utf-8'))
    out, dropped, renamed = [], 0, 0
    for r in rows:
        ref = (r.get('ref') or '').strip()
        if ref == 'R_PU_STAT_L':
            dropped += 1
            continue
        if r.get('net') == 'CHG_STAT_L':
            r['net'] = 'CHG_STAT'
            r['note'] = ('[CHG_STAT] ★2026-11-03 09:5x 订正: BQ25896 的 STAT (pin4) 是**单个开漏输出**, '
                         '不能同时挂两个网 ⇒ 充电板本地 LED 栅极与跨铰链 STAT **合并成一个网**; '
                         '同时删掉充电板本地的 5V 上拉 (它会把 5V 送到 SoC 的 3.3V 开漏输入 ⇒ 过压), '
                         '上拉留在主板侧 R_PU_CHG_STAT (10k 到 3.3V)')
            renamed += 1
        out.append(r)
    json.dump(out, open(P10, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'  [改] CHG_STAT_L → CHG_STAT: {renamed} 行 · [删] R_PU_STAT_L 两行: {dropped}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
