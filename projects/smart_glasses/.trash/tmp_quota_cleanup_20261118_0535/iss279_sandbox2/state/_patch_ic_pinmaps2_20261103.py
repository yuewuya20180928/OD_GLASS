#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_patch_ic_pinmaps2_20261103.py —— ★把 IC 规格表的第二轮订正落到网表 (2026-11-03 11:0x)

依据: `HW/PCB/pinout_footprint.json` (原厂 datasheet) + 子 agent 的三条"我的假设被原厂推翻":
  ① **BQ2970 没有单一 GATE 脚** —— 原厂是 **COUT(pin2, 充电管) / DOUT(pin3, 放电管) 两个独立栅驱动**
     ⇒ ★原网表"BAT_GATE 一根线接 Q1+Q2 共栅"**与原厂不符 ⇒ 保护会失效** ⇒ 必须拆开 + 补 Q2
  ② **TPS3808 的采样脚叫 SENSE(pin5)** (不是 IN), 且网表缺 GND(pin2) 与 MR(pin3)
  ③ **U_EN_SW / U_PWR_SW 的原厂脚名是 VIN / ON / VOUT / GND** (TPS22991RAA) ⇒ 网表里的
     "IN / EN / OUT" 是自拟名 ⇒ 改成原厂名才能自动对到脚号
  ④ **USB-IF 物理脚名 (A1/A4/A5/B12/shield) 就是真实焊盘号** ⇒ 板生成器与门禁都要认它
"""
import ast
import os
import re

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
GEN = f'{PROJ}/state/gen_netlist.py'
BRD = f'{PROJ}/state/gen_pcb_netlist_board.py'
GATE = f'{PROJ}/state/check_pcb_nets.py'

USBIF = r'(?:[AB](?:1|4|5|6|7|8|9|12)|shield)'


def main():
    # ── ① 网表: U_EN_SW / U_PWR_SW / U_SUPV 的脚名改成原厂名 ──
    src = open(GEN, encoding='utf-8').read()
    n = 0
    for ref, ren in (('U_EN_SW', {'IN': 'VIN', 'EN': 'ON', 'OUT': 'VOUT'}),
                     ('U_PWR_SW', {'IN': 'VIN', 'EN': 'ON', 'OUT': 'VOUT'}),
                     ('U_SUPV', {'IN': 'SENSE', 'RESET (开漏)': 'RESET'})):
        for old, new in ren.items():
            o = f'"{ref} {old}"'
            if o in src:
                src = src.replace(o, f'"{ref} {new}"')
                n += 1
    print(f'[1] 脚名改原厂名: {n} 处')

    # ── ② BQ2970: 拆 COUT/DOUT + 补 Q2 ──
    old_gate = '''    add("P1", "BAT_GATE", "Q1", "GND", "Q1", "[待选型] N-MOS (高边开关)", "SW", "必装", "[推算]", "",'''
    # 先看实际文本
    m = re.search(r'add\("P1", "BAT_GATE".*?\n', src)
    print('[2] BAT_GATE 现状:', (m.group(0)[:150] if m else '未找到'))
    if m:
        rows_bat = '''    # ★★2026-11-03 按**原厂 datasheet** 拆: BQ2970 **没有单一 GATE 脚** —— 原厂是
    #   **COUT(pin2, 充电管) / DOUT(pin3, 放电管) 两个独立栅驱动** ⇒ ★**两管不可共栅**
    #   (共栅会让保护逻辑失效: 充电时放电管也导通 ⇒ 电池永远放不出电流)
    add("P1", "BAT_COUT", "U_BATPROT pin2", "Q2", "U_BATPROT", "COUT (充电管栅驱动)", "NET",
        dnp, "[官方]", "",
        "[BAT_COUT] ★BQ2970 的 COUT (pin2) ⇒ **只**驱动充电管 Q2 的栅极 (原厂要求两管不可共栅)", cid)
    add("P1", "BAT_DOUT", "U_BATPROT pin3", "Q1", "U_BATPROT", "DOUT (放电管栅驱动)", "NET",
        dnp, "[官方]", "",
        "[BAT_DOUT] ★BQ2970 的 DOUT (pin3) ⇒ **只**驱动放电管 Q1 的栅极", cid)
    add("P1", "BAT_COUT", "Q2", "GND", "Q2", "[待选型] N-MOS (充电高边开关)", "SW", dnp, "[推算]", "",
        "[BAT_COUT] Q2 (充电管) 源极接地", cid)
    add("P1", "GND", "Q2", "GND", "Q2", "[待选型] N-MOS (充电高边开关)", "SW", dnp, "[推算]", "",
        "[BAT_COUT] Q2 地脚", cid)
    add("P1", "BAT_DOUT", "Q1", "GND", "Q1", "[待选型] N-MOS (放电高边开关)", "SW", dnp, "[推算]", "",
        "[BAT_DOUT] Q1 (放电管) 源极接地", cid)
    add("P1", "GND", "Q1", "GND", "Q1", "[待选型] N-MOS (放电高边开关)", "SW", dnp, "[推算]", "",
        "[BAT_DOUT] Q1 地脚", cid)
'''
        src = src.replace(m.group(0), rows_bat, 1)
        print('  [替] BAT_GATE → BAT_COUT/BAT_DOUT (两管分开) + 补 Q2')

    ast.parse(src)
    open(GEN, 'w', encoding='utf-8').write(src)
    print('✅ gen_netlist.py 已落盘')

    # ── ③ 板生成器 + 门禁: 认 USB-IF 物理脚名当真实焊盘号 ──
    for path, label in ((BRD, '生成器'), (GATE, '门禁')):
        s = open(path, encoding='utf-8').read()
        if 'USBIF' in s:
            print(f'[3] {label}: 已有 USBIF 规则 ⇒ 跳过')
            continue
        # 加常量
        anchor = 'PSEUDO = ("RAIL_", "NET_")'
        add = (anchor + '\n# ★USB-IF 物理脚名 (A1/A4/A5/A6/A7/A8/A9/A12 · B 同 · shield) 就是**真实焊盘号**\n'
               '#   (USB-C 座如 GCT USB4105 的 KiCad 封装正是用这组名字当 pad number)\n'
               f'USBIF_RE = re.compile(r"^{USBIF}$")')
        s = s.replace(anchor, add, 1)
        # 把 "编号脚" 的判定从 pin\\d+ 扩展成 pin\\d+ | USB-IF
        s2 = s.replace('re.fullmatch(r"pin\\d+(\\+pin\\d+)*", tail)',
                       '_is_pad_name(tail)')
        s2 = s2.replace('re.fullmatch(r"pin\\d+(\\+pin\\d+)*", name)',
                        '_is_pad_name(name)')
        # 加 _is_pad_name 助手
        helper = ('''

def _is_pad_name(tail):
    """★真实焊盘号判定: "pin<N>" (网表针号) 或 USB-IF 物理脚名 (A1/A4/.../shield)"""
    if not tail:
        return False
    return bool(re.fullmatch(r"pin\\d+(\\+pin\\d+)*", tail)) or bool(USBIF_RE.match(tail))
''')
        m2 = re.search(r'\ndef [a-z_]+\(', s2)
        s2 = s2[:m2.start()] + helper + s2[m2.start():]
        open(path, 'w', encoding='utf-8').write(s2)
        print(f'[3] {label}: USB-IF 焊盘号规则已加')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
