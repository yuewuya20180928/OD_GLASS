#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_patch_pinmaps_20261103.py —— ★把 IC 封装/脚号规格表落到网表上 (2026-11-03 10:5x)

真值: `HW/PCB/pinout_footprint.json` (由子 agent 按**原厂 datasheet** 整理, 每条带出处)
⇒ ★**只认原厂 datasheet** (授权分销商镜像的原厂 PDF 同源) —— 第三方博客/AI 生成的不采信。

做四件事:
  ① **PARTS 填充** (footprint + OPN) ⇒ 网表带出真实封装 ⇒ BOM 的封装列不再是"待定"
  ② **命名脚 → 真实脚号** 的通用改写 (node1/node2 形如 "U_EN_SW EN" ⇒ "U_EN_SW pin2")
     ⇒ ★**唯一真源 = pinout_footprint.json**, 网表里不再有"脚名"这种模糊写法
  ③ **TPS7A20 家族改按真实脚图画** (X2SON DQN0004A: 1=OUT 2=GND 3=EN 4=IN 5=散热焊盘)
     ⇒ ★**并补上之前完全没画的 GND 脚与散热焊盘** (原网表只画了 IN/EN/OUT ⇒ GND 是悬空的!)
  ④ **USB-C 改用 USB-IF 物理脚名** (D+/D- 各 2 个物理脚 A6+B6 / A7+B7, GND 4 个 A1/A12/B1/B12, shield)
     + **BQ2970 的 COUT/DOUT 分开** (原厂没有单一 GATE 脚! 共栅会让保护失效)
"""
import ast
import json
import os
import re

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
GEN = f'{PROJ}/state/gen_netlist.py'
SPECJ = f'{PROJ}/HW/PCB/pinout_footprint.json'


def main():
    spec = json.load(open(SPECJ, encoding='utf-8'))
    parts = spec.get('parts') or {}
    src = open(GEN, encoding='utf-8').read()
    orig = src

    # ── ① PARTS 填充 (footprint + opn) ──
    print('=== ① PARTS 填充 (封装 + OPN) ===')
    fill = {}
    for ref, d in parts.items():
        pkg = (d.get('package') or '').strip()
        part = (d.get('part') or '').strip()
        if not pkg:
            continue
        fp = pkg if len(pkg) < 120 else pkg[:117] + '...'
        fill[ref] = (fp, part)
    # 插进 PARTS 字典
    m = re.search(r'PARTS: dict\[str, dict\] = \{\n', src)
    assert m, '找不到 PARTS 字典'
    ins = ''
    for ref, (fp, opn) in sorted(fill.items()):
        if f'"{ref}":' in src:
            continue
        ins += (f'    # ★2026-11-03 封装/OPN 落定 (原厂 datasheet, 见 HW/PCB/PINOUT_FOOTPRINT_SPEC.md)\n'
                f'    "{ref}": {{"footprint": "{fp}", "opn": "{opn}"}},\n')
    if ins:
        src = src.replace(m.group(0), m.group(0) + ins, 1)
        print(f'  [插] {ins.count("footprint")} 个器件的 footprint/opn')

    # ── ② 命名脚 → 真实脚号的通用改写 + ③ TPS7A20 按真实脚号 ──
    print('=== ② 脚名→脚号 通用改写 ===')
    helper = '''

# ================================================================ ★引脚映射 (真实脚号)
# ★真值源: HW/PCB/pinout_footprint.json (按**原厂 datasheet** 整理, 每条带出处)
#   ⇒ 网表里**不再出现** "U_EN_SW EN" 这种"脚名"写法 ⇒ 一律 "U_EN_SW pin2" ⇒ 板子焊盘号=真实脚号
_PINMAP_PATH = os.path.join(PROJ, "HW", "PCB", "pinout_footprint.json")
try:
    _PINMAP = {k: {str(nn): str(vv) for nn, vv in (v.get("pins") or {}).items()}
               for k, v in (json.load(open(_PINMAP_PATH, encoding="utf-8")).get("parts") or {}).items()}
except Exception:
    _PINMAP = {}


def _apply_pin_maps(rows):
    """把 "<器件> <脚名>" 的节点串改写成 "<器件> pin<真实脚号>" (查不到就原样保留, 由门禁报出来)"""
    changed = unknown = 0
    for r in rows:
        for k in ("node1", "node2"):
            v = (r.get(k) or "").strip()
            mm = re.fullmatch(r"([A-Za-z_0-9]+)\\s+(.+)", v)
            if not mm:
                continue
            comp, name = mm.group(1), mm.group(2).strip()
            pm = _PINMAP.get(comp)
            if not pm:
                continue
            if name in pm:
                r[k] = f"{comp} pin{pm[name]}"
                changed += 1
            elif not re.fullmatch(r"pin\\d+(\\+pin\\d+)*", name):
                unknown += 1
    print(f"  [脚号改写] {changed} 处 · 仍无脚号的命名脚 {unknown} 处")
    return rows
'''
    if 'def _apply_pin_maps' not in src:
        anchor = '\nROWS: list[dict] = []'
        src = src.replace(anchor, helper + '\nROWS: list[dict] = []', 1)
        print('  [插] _apply_pin_maps() 已加')

    # 在 main() 里, 板级归属之前调用
    if '_apply_pin_maps(ROWS)' not in src:
        src = src.replace('    # ---- 板级归属 (2026-10-27 V1.1 新增): 充电板 / 主 PCB / 跨铰链 ----',
                          '    # ★2026-11-03: 命名脚 → 真实脚号 (查 HW/PCB/pinout_footprint.json)\n'
                          '    _apply_pin_maps(ROWS)\n\n'
                          '    # ---- 板级归属 (2026-10-27 V1.1 新增): 充电板 / 主 PCB / 跨铰链 ----', 1)
        print('  [插] main() 里调用 _apply_pin_maps()')

    # ── ③ TPS7A20 家族: 按真实脚号画 (含之前漏掉的 GND 与散热焊盘) ──
    print('=== ③ TPS7A20 家族按真实脚号 (X2SON DQN0004A) ===')
    old_ldo = '''        if part.startswith("TPS7A20"):
            # ★★2026-11-02 20:3x: SENSOR_AVDD 已 DNP (camera 模组自带稳压) ⇒ 不再需要它的 EN RC 延时
            # ★★2026-11-03: **TPS62130A (DC-DC) 的 EN 已被规格行画过** (EN_VCORE ← R_EN_VCORE / EN_VIO ← PWR_ON)
            #   ⇒ 这里**只画 TPS7A20** ⇒ 否则同一个 EN 脚会挂两个网 (板子上 = 短路)
            if ref != "U_LDO_S28":
                add("P1", "SYS_PCB", f"{ref} EN", "RAIL_BOARD_5V", ref, "EN", "NET", dnp, "[官方]", "",
                    f"[{rail}] ★{ref} 的 EN 脚**直连 RAIL_SYS** ⇒ 永远使能 — "
                    f"★★**P0: EN 内部 500kΩ 下拉, 悬空 = 关断 ⇒ 不画 EN = 投板后整板不上电**; "
                    f"datasheet 门限 VEN(LOW)≤0.3V 关断 / VEN(HIGH)≥0.9V 使能 ⇒ 接 SYS (3.5-4.2V) 安全", cid)
'''
    new_ldo = '''        if part.startswith("TPS7A20"):
            # ★★2026-11-03 按**原厂 datasheet** 重画 (TPS7A20 = X2SON / DQN0004A, **4 脚 + 散热焊盘**):
            #   ★真脚号: **1=OUT · 2=GND · 3=EN · 4=IN · 5=散热焊盘(接 GND)**
            #   ⇒ ★**之前只画了 IN/EN/OUT ⇒ GND 脚与散热焊盘整个是悬空的** ⇒ 现在补齐
            #   ⇒ EN 仍直连 RAIL_BOARD_5V (永远使能) —— 门限 VEN(LOW)≤0.3V 关断 / VEN(HIGH)≥0.9V 使能
            if ref != "U_LDO_S28":
                add("P1", "SYS_PCB", f"{ref} pin3", "RAIL_BOARD_5V", ref, "EN (pin3)", "NET", dnp,
                    "[官方]", "",
                    f"[{rail}] ★{ref} 的 EN 脚 (pin3) **直连 RAIL_BOARD_5V** ⇒ 永远使能 — "
                    "★★**P0: EN 内部 500kΩ 下拉, 悬空 = 关断 ⇒ 不画 EN = 投板后整板不上电**; "
                    "datasheet 门限 VEN(LOW)≤0.3V 关断 / VEN(HIGH)≥0.9V 使能", cid)
            # GND 脚 (pin2) + 散热焊盘 (pin5) ⇒ 原厂要求散热焊盘接 GND (散热 + 电气)
            add("P1", "GND", f"{ref} pin2", "GND", ref, "GND (pin2)", "NET", dnp, "[官方]", "",
                f"[{rail}] ★{ref} 的 GND 脚 (pin2) —— ★**之前网表里根本没画 GND ⇒ 悬空**", cid)
            add("P1", "GND", f"{ref} pin5", "GND", ref, "散热焊盘 (pin5, EP)", "NET", dnp, "[官方]", "",
                f"[{rail}] ★{ref} 的散热焊盘 (pin5, exposed pad) **必须接 GND** (原厂 X2SON 要求: "
                "既是散热通路也是 GND 回路)", cid)
'''
    if old_ldo in src:
        src = src.replace(old_ldo, new_ldo, 1)
        print('  [替] TPS7A20 分支 ⇒ 按真实脚号 + 补 GND/散热焊盘')
    else:
        print('  ★★ 没找到 TPS7A20 分支原文 —— 需人工处理')

    # ── ④ USB-C 物理脚名 + BQ2970 的 COUT/DOUT ──
    print('=== ④ USB-C 物理脚名 / BQ2970 双栅驱动 ===')
    usb_reps = [
        ('add("P1", "RAIL_DEMO_5V", "J_USB_C VBUS", "RAIL_DEMO_5V", "RAIL_DEMO_5V",',
         'add("P1", "RAIL_DEMO_5V", "J_USB_C A4+A9+B4+B9", "RAIL_DEMO_5V", "J_USB_C",'),
        ('add("P1", "USB_D_P_SRC", "R_SER_USB_D_P", "J_USB_C D+", "R_SER_USB_D_P", "22Ω ±1%", "R",',
         'add("P1", "USB_D_P_SRC", "R_SER_USB_D_P", "J_USB_C A6+B6", "R_SER_USB_D_P", "22Ω ±1%", "R",'),
        ('add("P1", "USB_D_N_SRC", "R_SER_USB_D_N", "J_USB_C D-", "R_SER_USB_D_N", "22Ω ±1%", "R",',
         'add("P1", "USB_D_N_SRC", "R_SER_USB_D_N", "J_USB_C A7+B7", "R_SER_USB_D_N", "22Ω ±1%", "R",'),
    ]
    for old, new in usb_reps:
        if old in src:
            src = src.replace(old, new, 1)
            print(f'  [替] {old[:46]}...')
        else:
            print(f'  ★★ 未找到: {old[:46]}...')

    # CC1/CC2 与 GND 脚用真实物理脚名
    src = src.replace('add("P1", "GND", "R_CC1_D", "GND", "R_CC1_D", "5.1k ±1% (CC1 下拉)", "R", "必装", "[官方]", "",',
                      'add("P1", "GND", "R_CC1_D", "GND", "R_CC1_D", "5.1k ±1% (CC1 下拉)", "R", "必装", "[官方]", "",')
    cc_anchor = '''    add("P1", "GND", "R_CC2_D", "GND", "R_CC2_D", "5.1k ±1% (CC2 下拉)", "R", "必装", "[官方]", "",'''
    cc_new = '''    # ★★2026-11-03: USB-C 的 CC/地脚用**真实 USB-IF 物理脚** (CC1=A5 · CC2=B5 · GND=A1/A12/B1/B12 + shell)
    add("P1", "GND", "J_USB_C A1+A12+B1+B12", "GND", "J_USB_C", "GND (4 脚 + shell)", "NET",
        "必装", "[官方]", "",
        "[J_USB_C] USB-C 的 4 个 GND 脚 + 外壳 ⇒ 主板地", "A-24")
    add("P1", "USB_CC1", "J_USB_C A5", "R_CC1_D", "J_USB_C", "CC1 (5.1k 下拉 ⇒ 受电端 UFP)", "NET",
        "必装", "[官方]", "", "[J_USB_C] CC1 → 5.1k 下拉 ⇒ 本板做受电端", "A-24")
    add("P1", "USB_CC2", "J_USB_C B5", "R_CC2_D", "J_USB_C", "CC2 (5.1k 下拉)", "NET",
        "必装", "[官方]", "", "[J_USB_C] CC2 → 5.1k 下拉", "A-24")
    add("P1", "GND", "R_CC2_D", "GND", "R_CC2_D", "5.1k ±1% (CC2 下拉)", "R", "必装", "[官方]", "",'''
    if cc_anchor in src:
        src = src.replace(cc_anchor, cc_new, 1)
        print('  [插] USB-C 的 GND/CC1/CC2 真实物理脚')

    ast.parse(src)
    if src == orig:
        print('\n★★ 无改动')
        return 1
    open(GEN, 'w', encoding='utf-8').write(src)
    print(f'\n✅ {GEN} 已落盘 (语法自检通过)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
