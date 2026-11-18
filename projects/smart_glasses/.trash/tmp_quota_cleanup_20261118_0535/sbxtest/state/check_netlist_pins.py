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
    # ★2026-11-04 19:5x: 'CONN_USB' 已从网表删除 —— 老板 11-02 19:25「**跨铰链取消**」⇒
    #   demo 板只有板载 Type-C 一条 USB 数据路径 (J_USB_C → 串阻 → SoM), 跨铰链 USB 座属整机阶段
    #   ⇒ 这里同步删掉期望 (★判据跟着形态走, 不是为了让门禁变绿而放松判据)
    'J_CHG': 10,        # 跨铰链充电 (整机阶段)
    'J_DEBUG': 4,       # JTAG 排针
    'J_UART': 2,        # UART 排针
    'J_BOOT1': 6,       # 启动存储焊盘位
    'U_TEMP': 6,        # ★2026-11-04: TMP117 官方 WSON-6 (1=SCL 2=GND 3=ALERT 4=ADD0 5=V+ 6=SDA)
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


# ★★C9 用 (ISS-153): I2C 地址表 —— HW/I2C_ADDR_TABLE.md 是地址真源, 网表是另一头
I2C_TABLE = os.path.join(PROJ, 'HW', 'I2C_ADDR_TABLE.md')
# ★网表里从设备地址的**唯一写法** —— 改地址时必须同时改表 (门禁按它机械抽取, 不猜)
ADDR_RE = re.compile(r'I2C\s*地址\s*0[xX]([0-9a-fA-F]{2})')
# ★挂在 I2C net 上但**不是从设备**的件: 上拉电阻 / 测试点 / SoM 座 / 网名伪件 / 地
NOT_SLAVE_PREFIX = ('R_PU_', 'TP_', 'J_SOM_', 'NET_', 'RAIL_', 'SoC')
NOT_SLAVE_EXACT = {'GND'}


def node_device(node):
    """节点串 → 器件名 ('CONN_CAM pin24' → 'CONN_CAM'; 'R_PU_I2CA_SCL' → 同名)"""
    node = (node or '').strip()
    if not node:
        return ''
    if ' ' in node:
        return node.split(' ', 1)[0].strip()
    return node


def parse_i2c_table():
    """解析 HW/I2C_ADDR_TABLE.md → [{bus, ref, dev, addr, status, src, pull, vdom}]"""
    out = []
    if not os.path.exists(I2C_TABLE):
        return out
    for ln in open(I2C_TABLE, encoding='utf-8'):
        ln = ln.strip()
        if not ln.startswith('|'):
            continue
        cells = [c.strip() for c in ln.strip('|').split('|')]
        if len(cells) < 9:
            continue
        if not cells[0] or set(cells[0]) <= {'-', ':', ' '} or cells[0] in ('总线', 'Bus'):
            continue
        m = re.search(r'0[xX]([0-9a-fA-F]{2})', cells[3])
        out.append({'bus': cells[0].replace('`', '').strip(), 'ref': cells[1].replace('`', '').strip(),
                    'dev': cells[2].replace('`', '').strip(),
                    'addr': ('0x' + m.group(1).lower()) if m else None,
                    'status': cells[4].replace('`', '').strip(), 'src': cells[5],
                    'pull': cells[6].replace('`', '').strip(), 'vdom': cells[7].replace('`', '').strip()})
    return out


def check_i2c_addr_table(rows):
    """C9: 网表里的 I2C 从设备地址 vs HW/I2C_ADDR_TABLE.md (双向 + 同总线唯一)"""
    lines, fails = [], []
    tbl = parse_i2c_table()
    if not tbl:
        lines.append("  ❌ C9 I2C 地址表 — HW/I2C_ADDR_TABLE.md 不存在或解析不到表行")
        fails.append('C9 缺 HW/I2C_ADDR_TABLE.md (或表里没有可解析的行)')
        return {'lines': lines, 'fails': fails}

    # ---- 网表侧: 每条总线上的从设备 + 它们声明的地址 ----
    bus_slaves = {'I2C_A': {}, 'I2C_B': {}}
    for r in rows:
        net = (r.get('net') or '').strip()
        bus = 'I2C_A' if 'I2C_A' in net else ('I2C_B' if 'I2C_B' in net else None)
        if bus is None:
            continue
        txt = ' '.join([(r.get('value') or ''), (r.get('note') or '')])
        addrs = set('0x' + a.lower() for a in ADDR_RE.findall(txt))
        devs = set()
        for k in ('ref', 'node1', 'node2'):
            d = node_device((r.get(k) or '').strip())
            if not d or d in NOT_SLAVE_EXACT or d.startswith(NOT_SLAVE_PREFIX):
                continue
            devs.add(d)
        for d in devs:
            bus_slaves[bus].setdefault(d, set()).update(addrs)

    # ---- 表侧: 每条总线"本板在挂"的行 ----
    live = {'I2C_A': {}, 'I2C_B': {}}
    for t in tbl:
        if '本板在挂' in t['status'] and t['bus'] in live:
            live[t['bus']][t['ref']] = t

    ok = True
    for bus in ('I2C_A', 'I2C_B'):
        detail = []
        net_set = set(bus_slaves[bus].keys())
        tbl_set = set(live[bus].keys())
        missing = sorted(net_set - tbl_set)          # 网表有 ⇒ 表里没有
        phantom = sorted(tbl_set - net_set)          # 表里有 ⇒ 网表没有
        addrs = []
        for ref in sorted(net_set & tbl_set):
            net_addrs = bus_slaves[bus][ref]
            t = live[bus][ref]
            if len(net_addrs) != 1:
                ok = False
                detail.append(f"       ★ {bus} {ref}: 网表里的地址声明有 {len(net_addrs)} 个 {sorted(net_addrs)} "
                               f"(应恰好 1 个, 写法 = `I2C 地址 0xNN`)")
            elif t['addr'] is None:
                ok = False
                detail.append(f"       ★ {bus} {ref}: 表里没解析出地址")
            elif next(iter(net_addrs)) != t['addr']:
                ok = False
                detail.append(f"       ★ {bus} {ref}: 网表地址 {sorted(net_addrs)[0]} ≠ 表里地址 {t['addr']} ⇒ **改地址忘了改表**")
            else:
                addrs.append((ref, sorted(net_addrs)[0]))
        for ref in missing:
            ok = False
            detail.append(f"       ★ {bus} {ref}: 网表里挂了这个从设备, 但 HW/I2C_ADDR_TABLE.md 里没有它 ⇒ **加了器件忘了加表**")
        for ref in phantom:
            ok = False
            detail.append(f"       ★ {bus} {ref}: 表里标了『本板在挂』, 但网表上没这个从设备 ⇒ **表与网表不同步**")
        # 同总线地址唯一 (本板在挂的 + 表里预留的)
        all_addr = [(ref, a) for ref, a in addrs]
        for t in tbl:
            if t['addr'] and t['status'] != '本板在挂' and (bus in t['bus'] or t['bus'] in bus):
                all_addr.append((t['ref'] or t['dev'], t['addr']))
        seen = {}
        for ref, a in all_addr:
            if a in seen and seen[a] != ref:
                ok = False
                detail.append(f"       ★ {bus}: 地址 {a} 被两个设备占用 ({seen[a]} / {ref}) ⇒ **撞地址**")
            seen.setdefault(a, ref)
        lines.append(f"  {'✅' if ok else '❌'} C9 {bus} 从设备地址与 HW/I2C_ADDR_TABLE.md 一致且唯一 — "
                     f"{len(net_set & tbl_set)} 个在挂: "
                     + (", ".join(f"{r}={a}" for r, a in sorted(addrs)) or "无"))
        lines.extend(detail)
    if ok:
        lines.append("       (C9 判据: 表 ↔ 网表 双向一致 · 同总线地址唯一)")
    else:
        fails.append('C9 I2C 地址与 HW/I2C_ADDR_TABLE.md 不一致 (或同总线撞地址)')
    return {'lines': lines, 'fails': fails}


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

    # ---- C9 ★★I2C 地址表一致性 (ISS-153 · 2026-11-04) ----
    #   ★背景: **换 sensor 时 I2C 地址会变** (IMX415=0x1a / AR0234CS=0x10 / OV04C10=0x36)
    #   ⇒ 旧网表注释里那串地址是"某一次换料时的快照", 过期没人管 ⇒ 两个从设备撞地址 ⇒
    #   上电后总线全哑 ⇒ 要么改板 (2-4 周 + ¥4-8K), 要么等原厂回信。
    #   ⇒ 本判据把 **网表里声明的地址** 与 **HW/I2C_ADDR_TABLE.md (原厂 datasheet 出处表)** 绑死:
    #     ① 表存在且能解析        ② 网表从设备集合 == 表里"本板在挂"的行集合 (双向)
    #     ③ 每个从设备的网表地址 == 表里地址  ④ 同一条总线内地址两两唯一
    #   ★地址声明的**唯一写法** = 行文本里的 `I2C 地址 0xNN` (门禁按它机械抽取, 不猜)。
    c9 = check_i2c_addr_table(rows)
    for ln in c9["lines"]:
        lines.append(ln)
    fails.extend(c9["fails"])

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
