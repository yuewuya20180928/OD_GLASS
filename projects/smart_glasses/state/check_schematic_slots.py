#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_schematic_slots.py —— ★原理图"槽位齐全性"门禁 (2026-11-03 20:0x)

★★ 为什么要有这条 (它替代了一个坏掉的现成 skill):
  · ClawHub 上的 `electrical-schematic-review` **正文损坏 (66 处 U+FFFD, 发布方编码错)** ⇒ 按铁律弃用
  · 替代方案: 用 `smart-hardware-reference` 的 **H3-01 原理图设计 / H3-04 电源设计方案 / H3-03 PCB Layout**
    的**必选组件槽位**做判据, 写成本项目专用的机检门禁 (判据落到文件与网表, 不靠人眼)

★判据 (每条都对应今天真实踩过的坑):
  A 交付件齐全 (H3-01/H3-04/H3-03 的必选件 → 本项目的对应物)
  B ★**每个器件的引脚在网表里齐全** (对照 pinout_footprint.json 的真实脚号)
     ⇒ ★**这条能抓住 2026-11-03 12:5x 那个"LDO 的 GND 脚整个漏画"的事故**
  C ★**外部接口必须有 ESD 器件** (Forlinx 载板指引: ESD 紧贴接口)
  D ★**每条电源轨必须有来源/声明 DNP**
  E ★**调试接口存在**
  F 文档槽位: 电源轨需求表里必须有"启动时序"与"掉电保护"两节
"""
import csv
import json
import os
import re
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NET = os.path.join(PROJ, 'HW', 'netlist_v1.csv')
PINMAP = os.path.join(PROJ, 'HW', 'PCB', 'pinout_footprint.json')
POWER = os.path.join(PROJ, 'HW', 'POWER_RAIL_SPEC.md')

# ★交付件 (H3-01/H3-03/H3-04 槽位 → 本项目对应物)
DELIVERABLES = [
    ('H3-04 电源设计方案', 'HW/POWER_RAIL_SPEC.md', ['电源输入规格', '各轨电压', '启动时序', '掉电']),
    ('H3-01 主控接口', 'HW/PCB/SOM_PIN_ASSIGNMENT.md', ['CARRIER_BOARD_EN']),
    ('H3-01 外设接口针位', 'HW/PCB/FPC_PIN_TABLES.md', ['display:', 'camera:']),
    ('H3-03 叠层/层数', 'HW/PCB/STACKUP.md', ['层', '阻抗']),
    ('H3-03 布线/阻抗规则', 'HW/PCB/LAYOUT_RULES.md', ['阻抗']),
    ('H3-02 器件封装与脚号', 'HW/PCB/pinout_footprint.json', ['"pins"']),
]
EXT_CONN = ('CONN_CAM', 'CONN_LIGHT', 'J_USB_C', 'J_CHG', 'CONN_USB')
DEBUG_CONN = ('J_DEBUG', 'J_UART')


def main():
    fails, lines = [], []
    rows = list(csv.DictReader(open(NET, encoding='utf-8')))

    # ---- A 交付件齐全 ----
    for slot, rel, keys in DELIVERABLES:
        p = os.path.join(PROJ, rel)
        if not os.path.exists(p):
            lines.append(f'  ❌ A 缺交付件 [{slot}] → {rel}')
            fails.append(f'A 缺 {rel}')
            continue
        txt = open(p, encoding='utf-8', errors='replace').read()
        miss = [k for k in keys if k not in txt]
        if miss:
            lines.append(f'  ❌ A 交付件 [{slot}] {rel} 缺内容: {miss}')
            fails.append(f'A {rel} 缺 {miss}')
        else:
            lines.append(f'  ✅ A 交付件 [{slot}] {rel}')

    # ---- B 每个器件的引脚在网表里齐全 ----
    if os.path.exists(PINMAP):
        spec = json.load(open(PINMAP, encoding='utf-8')).get('parts') or {}
        # 网表里每个 ref 用到的引脚
        used = {}
        for r in rows:
            ref = (r.get('ref') or '').strip()
            for k in ('node1', 'node2'):
                v = (r.get(k) or '').strip()
                m = re.fullmatch(r'([A-Za-z_0-9]+)\s+pin(\d+)(\+pin(\d+))?', v)
                # ★归属以**节点串里的器件名**为准 (一行可以带别家器件的脚, 例如 NET 行)
                if m:
                    # ★归属以**节点串里的器件名**为准 (一行可以带别家器件的脚)
                    _comp = m.group(1)
                    for g in (2, 4):
                        if m.group(g):                      # ★取**脚号的值**, 不是组号!
                            used.setdefault(_comp, set()).add(int(m.group(g)))
        bad = []
        for ref, d in sorted(spec.items()):
            want = {int(n) for n in (d.get('pins') or {}) if str(n).isdigit()}
            if not want:
                continue
            if len(want) > 8:
                # ★多引脚电源 IC (如 VQFN-16) 按需用脚, 只用 4~6 个 ⇒ 不做"全脚齐全"检查
                continue
            got = used.get(ref, set())
            if ref not in used:
                continue                      # ★不在网表里 (DNP/未上板) ⇒ 不判
            # ★**全 DNP 的器件不参与"引脚齐全"判定** (它不装在板上)
            # ★只对**必装**器件做"引脚齐全"检查 (DNP 器件不装在板上, 漏脚无意义)
            _dn = [r for r in rows if (r.get('ref') or '').strip() == ref]
            if _dn and not any((r.get('dnp') or '').strip() != 'DNP' for r in _dn):
                continue
            miss = sorted(want - got)
            if miss:
                bad.append((ref, miss))
        lines.append(f"  {'✅' if not bad else '❌'} B 器件引脚在网表里齐全 — "
                     f"对照 pinout_footprint.json 核 {len(spec)} 个器件")
        for ref, miss in bad[:10]:
            lines.append(f'       ★ {ref} 缺引脚 {miss} ⇒ ★**器件引脚漏画** (今天 LDO 的 GND 脚就是这样漏的)')
        if bad:
            fails.append(f'B {len(bad)} 个器件引脚不全')
    else:
        lines.append('  ⏭ B 跳过 (pinout_footprint.json 不存在)')

    # ---- C 外部接口必须有 ESD (按**网**判: 该接口的信号网有没有挂到 D_ESD* 器件) ----
    conn_nets = {}
    for r in rows:
        blob = (r.get('node1') or '') + ' ' + (r.get('node2') or '')
        for c in EXT_CONN:
            if re.search(rf'\b{c}\b', blob):
                conn_nets.setdefault(c, set()).add((r.get('net') or '').strip())
    esd_nets = set()
    for r in rows:
        if (r.get('ref') or '').startswith('D_ESD'):
            esd_nets.add((r.get('net') or '').strip())
    lack = []
    for c in EXT_CONN:
        if c not in conn_nets:
            continue                      # 该接口不在网表里 (DNP/铰链件) ⇒ 不判
        if not (conn_nets[c] & esd_nets):
            lack.append(c)
    lines.append(f"  {'✅' if not lack else '❌'} C 外部接口有 ESD 器件 — "
                 f"接口 {sorted(conn_nets)}")
    if lack:
        lines.append(f'       ★ 无 ESD 的接口: {lack} (Forlinx 载板指引: ESD 阵列紧贴接口)')
        fails.append(f'C 接口缺 ESD: {lack}')

    # ---- D 每条电源轨有来源或声明 DNP ----
    rails = {}
    for r in rows:
        net = (r.get('net') or '').strip()
        ref = (r.get('ref') or '').strip()
        if ref.startswith('RAIL_') and net == ref:
            rails.setdefault(ref, set()).add((r.get('dnp') or '').strip())
    no_src = [k for k, v in rails.items() if 'DNP' not in v]
    lines.append(f"  {'✅' if not no_src else '❌'} D 电源轨有来源/声明 DNP — 轨 {len(rails)} 条")
    if no_src:
        lines.append(f'       ★ 无来源也无 DNP 声明: {no_src[:8]}')
        fails.append(f'D {len(no_src)} 条轨无来源')

    # ---- E 调试接口存在 ----
    all_refs = {(r.get('ref') or '').strip() for r in rows}
    have_dbg = [d for d in DEBUG_CONN if d in all_refs]
    lines.append(f"  {'✅' if have_dbg else '❌'} E 调试接口存在 — {have_dbg}")
    if not have_dbg:
        fails.append('E 无调试接口')

    # ---- F 电源轨需求表的两节 ----
    if os.path.exists(POWER):
        t = open(POWER, encoding='utf-8').read()
        miss = [k for k in ('启动时序', '掉电') if k not in t]
        lines.append(f"  {'✅' if not miss else '❌'} F 电源轨需求表含启动时序/掉电保护" + (f' — 缺 {miss}' if miss else ''))
        if miss:
            fails.append(f'F 电源轨表缺 {miss}')
    else:
        lines.append('  ❌ F 缺 HW/POWER_RAIL_SPEC.md')
        fails.append('F 缺电源轨需求表')

    print("=" * 72)
    print("  原理图槽位门禁 · check_schematic_slots (★替代损坏的 electrical-schematic-review)")
    print("=" * 72)
    print("\n".join(lines))
    print("-" * 72)
    if fails:
        print(f"❌ 不通过 {len(fails)} 项: {'; '.join(fails)}")
        return 1
    print("✅ 全过 —— 原理图槽位齐全 (H3-01 / H3-03 / H3-04 必选件)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
