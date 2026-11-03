#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_netlist_pins.py —— ★网表"针脚级"门禁 (2026-11-03 新增)

★★ 为什么必须新加这条门禁 (实测):
  旧门禁 `check_netlist.py` 只查**连接关系**, 不查**针脚归属** ⇒ 出现了
  ★**同一个连接器脚上挂着 2~4 个不同网** (CONN_CAM 12 个脚 / CONN_LIGHT 9 个脚) ——
  例如 `CSI_D0_CK_P` 同时出现在 CONN_CAM pin1 与 pin18、`CSI_MCLK` 同时在 pin11 与 pin20
  ⇒ **板子上就是短路** ⇒ 而旧的"板子↔网表等价性"门禁是**按 (ref,net) 集合**比对的 ⇒ **假绿**
  ⇒ ⇒ 本门禁把"针脚归属"变成可机械判定的红线。

判据:
  C1 ★**一个针脚只能属于一个网** (处理 "REF pinN+pinM" 复合节点)
  C2 ★**连接器针数 == 规格针数** (真值表见 SPEC_PINS)
  C3 ★**连接器针号连续无缺号**
  C4 ★**同一器件的所有行必须同属一块板** (防止一个件被画到两块板上)
  C5 ★**SoC 侧节点可解析**: `SoC[RK3572].<信号>` 必须在 RK3572 引脚表 (HW/PCB/FET3572C_PIN_TABLE.csv) 里找得到
     —— 找得到的还必须**被分配表选中** (即真实落在某个 J_SOM_Px pinN 上)

退出码: 0 = 全过; 1 = 有不通过项
"""
import collections
import csv
import os
import re
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NET = os.path.join(PROJ, 'HW', 'netlist_v1.csv')
PINTBL = os.path.join(PROJ, 'HW', 'PCB', 'FET3572C_PIN_TABLE.csv')
ASSIGN = os.path.join(PROJ, 'HW', 'PCB', 'som_pin_assign.json')

# ★真值: 连接器的针数 (来自 HW/PCB/FPC_PIN_TABLES.md / 规格书)
SPEC_PINS = {
    'CONN_CAM': 31,     # Radxa Camera 4K (IMX415) 31p/0.3mm
        'CONN_LIGHT': 22,   # ★2026-11-04 定稿: Pi5 22p/0.5mm DISPLAY 座 (针序见 HW/PCB/PI5_DSI_22P_PINOUT.md)
    'CONN_USB': 4,      # 跨铰链 USB (整机阶段)
    'J_CHG': 10,        # 跨铰链充电 (整机阶段)
    'J_DEBUG': 4,       # JTAG 排针
    'J_UART': 2,        # UART 排针
    'J_BOOT1': 6,       # 启动存储焊盘位
    'U_TEMP': 4,        # TMP117
    'U_CHG': 24,        # BQ25896 WQFN-24
}

# ★**部分用到**的 100 脚座 (SoM 的 4 组 BTB): 只查"针号在范围内 + 不重号", 不查针数齐不齐
PARTIAL_PINS = {
    'J_SOM_P1': 100, 'J_SOM_P2': 100, 'J_SOM_P3': 100, 'J_SOM_P4': 100,
}

# ★IC 引脚**有名字**的器件 ⇒ 焊盘号无法从网表自动得出 (封装未落定)
NAMED_PIN_IC = {'U_LDO_L33', 'U_LDO_L18', 'U_LDO_IO33', 'U_LDO_IO18', 'U_LDO_S18B',
                'U_LDO_S12', 'U_DCDC_VCORE', 'U_DCDC_VIO', 'U_SUPV', 'U_PWR_SW',
                'U_BATPROT', 'BT_432243', 'J_TYPE_C', 'Q1'}


def pin_nodes(node, ref):
    """★节点串里的针脚归属**以节点串里的器件名为准**, 不以行的 ref 为准
    —— 例如 "CONN_CAM pin18" 出现在 ref=C_AC_CSI_D0_CK_P 的行里, 它占的是 **CONN_CAM 的 18 脚**。
    支持 "REF pin3" / "REF pin13+pin14" / "REF pin17+pin18"。"""
    out = []
    if not node:
        return out
    m = re.match(r'^([A-Za-z_0-9]+)\s+(.*)$', node)
    if not m:
        return out
    comp, tail = m.group(1), m.group(2).strip()
    if not tail.startswith('pin'):
        return out
    for tok in tail.split('+'):
        mm = re.fullmatch(r'pin(\d+)', tok.strip())
        if mm:
            out.append((comp, int(mm.group(1))))
    return out


def main():
    rows = list(csv.DictReader(open(NET, encoding='utf-8')))
    fails = []
    lines = []

    # ---- C1 一个针脚只能属于一个网 ----
    pin_nets = collections.defaultdict(set)
    pin_rows = collections.defaultdict(list)
    for r in rows:
        ref = (r.get('ref') or '').strip()
        net = (r.get('net') or '').strip()
        if not ref or not net:
            continue
        for k in ('node1', 'node2'):
            for comp, p in pin_nodes((r.get(k) or '').strip(), ref):
                pin_nets[(comp, p)].add(net)
                pin_rows[(comp, p)].append((r.get('page'), ref, net))
    multi = {k: sorted(v) for k, v in pin_nets.items() if len(v) > 1}
    lines.append(f"  {'✅' if not multi else '❌'} C1 一个针脚只能属于一个网 — 冲突 {len(multi)} 处")
    for (ref, p), ns in sorted(multi.items())[:12]:
        lines.append(f"       ★ {ref} pin{p}: {ns}")
    if multi:
        fails.append(f'C1 {len(multi)} 处针脚多网')

    # ---- C2/C3 连接器针数与连续性 ----
    conns = collections.defaultdict(set)
    for (ref, p) in pin_nets:
        conns[ref].add(p)
    for ref, want in sorted(SPEC_PINS.items()):
        got = conns.get(ref, set())
        ok_n = len(got) == want
        gaps = [i for i in range(1, want + 1) if i not in got] if got else list(range(1, want + 1))

        ok_g = not gaps
        lines.append(f"  {'✅' if ok_n and ok_g else '❌'} C2/C3 {ref}: 针数 {len(got)}/{want}"
                     + (f" · 缺号 {gaps[:10]}" if gaps else ""))
        if not ok_n:
            fails.append(f'C2 {ref} 针数 {len(got)}≠{want}')
        if gaps and got:
            fails.append(f'C3 {ref} 缺号 {gaps[:6]}')
    unknown = sorted(set(c for (c, _) in pin_nets) - set(SPEC_PINS))
    if unknown:
        lines.append(f"       (其余带脚号的器件: {unknown})")

    # ---- C2b 部分用到的 100 脚座 (SoM 的 4 组 BTB): 针号必须在范围内 ----
    for ref, n in sorted(PARTIAL_PINS.items()):
        got = conns.get(ref, set())
        bad = sorted(p for p in got if not (1 <= p <= n))
        lines.append(f"  {'✅' if not bad else '❌'} C2b {ref}: 用到 {len(got)} 脚 "
                     f"(座共 {n} 脚) · 越界 {bad[:5]}")
        if bad:
            fails.append(f'C2b {ref} 针号越界 {bad[:5]}')

    # ---- C4 同一器件必须同属一块板 (只查**真实器件**, 网别名 pseudo 件跨板是正常的) ----
    boards = collections.defaultdict(set)
    for r in rows:
        ref = (r.get('ref') or '').strip()
        bd = (r.get('board') or '').strip()
        if not ref or not bd:
            continue
        if ref.startswith(('NET_', 'RAIL_')):
            continue
        boards[ref].add(bd)
    mixed = {k: sorted(v) for k, v in boards.items() if len(v) > 1}
    lines.append(f"  {'✅' if not mixed else '❌'} C4 同一器件只能属于一块板 — 跨板 {len(mixed)} 个")
    for k, v in sorted(mixed.items())[:8]:
        lines.append(f"       ★ {k}: {v}")
    if mixed:
        fails.append(f'C4 {len(mixed)} 个器件跨板')

    # ---- C5 SoC 侧节点可解析到 RK3572 引脚表 ----
    if os.path.exists(PINTBL) and os.path.exists(ASSIGN):
        tbl = list(csv.DictReader(open(PINTBL, encoding='utf-8')))
        sig2pins = collections.defaultdict(list)
        for r in tbl:
            sig2pins[r['signal']].append(f"{r['conn']}_{int(r['num'])}")
        asg = {}
        if os.path.exists(ASSIGN):
            import json
            asg = json.load(open(ASSIGN, encoding='utf-8')).get('assign', {})
        used = set()
        for ours, m in asg.items():
            used.add(m.get('somsig', ''))
        soc_nodes = set()
        for r in rows:
            for k in ('node1', 'node2'):
                v = (r.get(k) or '').strip()
                m = re.match(r'^SoC\[RK3572\]\.(\w+)$', v)
                if m:
                    soc_nodes.add(m.group(1))
        unknown_sig = sorted(s for s in soc_nodes if s not in sig2pins)
        lines.append(f"  {'✅' if not unknown_sig else '❌'} C5 SoC 侧信号在 RK3572 引脚表里存在 — "
                     f"未知 {len(unknown_sig)} 个")
        for s in unknown_sig[:12]:
            lines.append(f"       ★ SoC[RK3572].{s} —— RK3572 引脚表里没有这个信号名")
        if unknown_sig:
            fails.append(f'C5 {len(unknown_sig)} 个 SoC 信号在 RK3572 引脚表里不存在')
        # 分配表覆盖: SoC 节点用到的信号必须在分配表里被选中 (含 *_SRC 之类的源名)
        picked = set()
        for r in rows:
            for k in ('node1', 'node2'):
                v = (r.get(k) or '').strip()
                m = re.match(r'^SoC\[RK3572\]\.(\w+)$', v)
                if m:
                    picked.add(m.group(1))
        unassigned = sorted(s for s in picked if s not in used)
        lines.append(f"  {'✅' if not unassigned else '❌'} C5b SoC 侧节点都已被引脚分配表选中 — "
                     f"未分配 {len(unassigned)} 个")
        for s in unassigned[:12]:
            lines.append(f"       ★ SoC[RK3572].{s} 还没分配到具体引脚 (⇒ 网表里还是占位符)")
        if unassigned:
            fails.append(f'C5b {len(unassigned)} 个 SoC 节点未分配引脚')
    else:
        lines.append("  ⏭ C5 跳过 (引脚表或分配表不存在)")

    # ---- C6/C7 ★**内容存在性**门禁 (★不能只查"自洽", 还要查"该有的东西在不在") ----
    #   ★背景: 2026-11-03 实测 —— `build_a2_som()` 定义了但**忘了在 main() 里调用** ⇒
    #   网表里**根本没有** SoM 的 VCC_DCIN / CARRIER_BOARD_EN / demo Type-C 三组行
    #   ⇒ ★**所有"自洽型"门禁全绿** (针脚唯一/针数/板子等价) ⇒ **这才是真·假绿的第四种形态**
    #   ⇒ ⇒ 这条门禁按**内容**查: SoM 的供电脚在不在、使能脚在不在、每个座用没用
    som_dcin = sorted(p for (r, p) in pin_nets if r == 'J_SOM_P3' and p in (91, 93, 95, 97, 98, 99, 100))
    car_en_rows = [r for r in rows if 'J_SOM_P3 pin87' in ((r.get('node1') or '') + ' ' + (r.get('node2') or ''))]
    used_soms = sorted({r for (r, p) in pin_nets if r.startswith('J_SOM_')})
    ok6 = len(som_dcin) == 7
    lines.append(f"  {'✅' if ok6 else '❌'} C6 SoM 的 VCC_DCIN 7 脚都接上了 — {len(som_dcin)}/7 "
                 f"{'(' + ','.join(map(str, som_dcin)) + ')' if som_dcin else ''}")
    if not ok6:
        fails.append(f'C6 SoM 的 VCC_DCIN 只接了 {len(som_dcin)}/7 脚')
    ok7 = bool(car_en_rows)
    lines.append(f"  {'✅' if ok7 else '❌'} C7 F13 底板使能 CARRIER_BOARD_EN (J_SOM_P3 pin87) 已接 — "
                 f"{len(car_en_rows)} 行")
    if not ok7:
        fails.append('C7 CARRIER_BOARD_EN 没接 (F13: 底板早于核心板上电 ⇒ 可能损坏处理器)')
    ok8 = len(used_soms) == 4
    lines.append(f"  {'✅' if ok8 else '❌'} C8 4 组 SOM 座都用上了 — {used_soms}")
    if not ok8:
        fails.append(f'C8 只有 {len(used_soms)}/4 组 SOM 座在用')

    print("=" * 72)
    print("  网表针脚级门禁 · check_netlist_pins (★一个针脚只能属于一个网)")
    print("=" * 72)
    print("\n".join(lines))
    print("-" * 72)
    if fails:
        print(f"❌ 不通过 {len(fails)} 项: {'; '.join(fails)}")
        return 1
    print("✅ 全过 —— 每个针脚归属唯一, 连接器针数与针号齐, SoC 节点全部落到真实引脚")
    return 0


if __name__ == '__main__':
    sys.exit(main())
