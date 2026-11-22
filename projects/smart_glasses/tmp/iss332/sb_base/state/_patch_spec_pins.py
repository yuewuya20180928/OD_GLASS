#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_patch_spec_pins.py —— ★规格 (HW/SCHEMATIC_V1_SPEC.json) 与网表同步订正 (2026-11-03 10:1x)

① A-12 的信号从 `CSI_RESET_N` 改成 `CAM_RESET_N`
   (★CSI_RESET_N 曾把 camera 复位接到 **pin12** —— 而 pin12 在 31 针表里是 **MDP2 (MIPI 数据正脚)**
    ⇒ 真实复位脚只有 **pin27 = RESET** ⇒ 规格与网表统一叫 CAM_RESET_N)
② C-06/C-07/C-08 (sensor 芯片级三条轨 2.8V/1.8V/1.2V) 标 **DNP**
   (★camera **模组**自带稳压, 模组只吃 3.3V(pin28/29) 与 5V(pin30/31) ⇒ 芯片级轨不出主板)
③ 规格里的 "TP_SENSOR_3V3/1V8/2V8" 测试点删掉 (跟着 ② 一起 DNP)
④ 网表: CAM_RESET_N 行补 conn_id=A-12 + 补一个 TP_CAM_RST 测试点 (pin27)
"""
import ast
import json
import os
import sys

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
SPEC = f'{PROJ}/HW/SCHEMATIC_V1_SPEC.json'
GEN = f'{PROJ}/state/gen_netlist.py'


def main():
    s = json.load(open(SPEC, encoding='utf-8'))
    # ---- ① A-12 ----
    for c in s['connections']:
        if c['id'] == 'A-12':
            c['signal'] = 'CAM_RESET_N'
            c['level'] = '3.3V (SoC GPIO 推挽)'
            c['imp'] = '单端'
            c['tp'] = 'TP_CAM_RST'
            c['note'] = ('★2026-11-03 订正: camera 模组的复位脚只有 **pin27 = RESET** '
                         '(旧写 CSI_RESET_N→pin12 撞了 MDP2 数据脚)')
        # ---- ② sensor 三条轨 DNP ----
        if c.get('id') in ('C-06', 'C-07', 'C-08'):
            c['dnp'] = 'DNP'
            c['tp'] = ''
            c['note'] = ('★2026-11-03 订正: camera **模组自带稳压** (模组只吃 VCC3.3V pin28/29 与 '
                         'VCC5V pin30/31) ⇒ 传感器**芯片级**三条轨不出主板 ⇒ DNP')
    # ---- ③ 删 sensor 测试点 ----
    before = len(s['testpoints'])
    s['testpoints'] = [t for t in s['testpoints'] if 'TP_SENSOR' not in json.dumps(t, ensure_ascii=False)]
    print(f'  [规格] testpoints {before} → {len(s["testpoints"])} (删 sensor 三轨测试点)')
    json.dump(s, open(SPEC, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    # ---- ④ 网表 ----
    src = open(GEN, encoding='utf-8').read()
    old = '''    add("P5", "CAM_RESET_N", "CONN_CAM pin27", "SoC[RK3572].GPIO_CAM_RESET", "CONN_CAM", "RESET", "NET",'''
    new = '''    add("P5", "CAM_RESET_N", "CONN_CAM pin27", "SoC[RK3572].GPIO_CAM_RESET", "CONN_CAM", "RESET", "NET",'''
    if old not in src:
        print('  ★★ 找不到 CAM_RESET_N 行')
        return 1
    # 找到该 add(...) 的结尾, 在 conn_id 位置填 "A-12"
    i = src.index(old)
    j = src.index('", "A-12")', i) if '", "A-12")' in src[i:i + 2000] else -1
    # 该行原本以 ... , "TBD-03",\n  "note...") 结尾 ⇒ 找它的最后一个括号
    depth = 0
    k = src.index('(', i)
    in_s = None
    m = k
    while m < len(src):
        ch = src[m]
        if in_s:
            if ch == '\\':
                m += 2
                continue
            if ch == in_s:
                in_s = None
        else:
            if ch in '"\'':
                in_s = ch
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    break
        m += 1
    stmt = src[i:m + 1]
    if '"A-12"' in stmt:
        print('  (CAM_RESET_N 已带 A-12)')
    else:
        # 末尾是  ... "", note)  ⇒ 追加 conn_id
        stmt2 = stmt[:-1].rstrip()
        if stmt2.endswith(','):
            stmt2 += ' "A-12"'
        else:
            stmt2 += ', "A-12"'
        stmt2 += ')'
        src = src[:i] + stmt2 + src[m + 1:]
        print('  [网表] CAM_RESET_N 补 conn_id=A-12')
    # ---- 补 TP_CAM_RST 测试点 ----
    tp_anchor = '    ("TP_CSI_RST"'
    if tp_anchor in src:
        src = src.replace(tp_anchor,
                          '    ("TP_CAM_RST", "CAM_RESET_N", "CONN_CAM pin27", "camera 复位 (SoC GPIO 拉低)",\n'
                          '     "连接器出口", "必装"),\n' + tp_anchor, 1)
        print('  [网表] 补 TP_CAM_RST 测试点')
    ast.parse(src)
    open(GEN, 'w', encoding='utf-8').write(src)
    print(f'✅ {GEN} 与 {SPEC} 已落盘 (语法自检通过)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
