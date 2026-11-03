#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_iss165_som_footprint_apply.py —— 把 4 组 100pin BTB 座接进板生成器 (A2 段最后一步)

★做什么:
  ① 从网表 (`HW/netlist_v1.csv`) 解析出每个 J_SOM_Px 的 **脚号 → 网络** 映射
  ② 在 `state/gen_pcb_netlist_board.py` 里加一行调用:
        from som_btb_footprint import add_som_connectors
        add_som_connectors(board, netmap, SOM_PARAMS, pin_net)
     (调用点放在 `board.BuildListOfNets()` **之前**)
  ③ 重跑生成器 + 三个门禁 (等价性 / DRC / 针脚级)

★几何真值: `HW/PCB/som_btb_params.json` (Hirose DF40C-100DS-0.4V(51))
★座在板上的位置: SoM 承载区原点 (8,6) + SoM 上的座中心 (2×2, 中心距 34×43mm)
"""
import csv
import os
import re
import sys

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
GEN = f'{PROJ}/state/gen_pcb_netlist_board.py'
NET = f'{PROJ}/HW/netlist_v1.csv'
PARAMS = f'{PROJ}/HW/PCB/som_btb_params.json'


def parse_pin_net():
    rows = list(csv.DictReader(open(NET, encoding='utf-8')))
    pin_net = {}
    for r in rows:
        net = (r.get('net') or '').strip()
        if not net:
            continue
        for k in ('node1', 'node2'):
            v = (r.get(k) or '').strip()
            m = re.fullmatch(r'J_SOM_(P\d) pin(\d+)', v)
            if m:
                pin_net.setdefault(m.group(1), {})[int(m.group(2))] = net
    return pin_net


def main():
    pin_net = parse_pin_net()
    tot = sum(len(v) for v in pin_net.values())
    print(f'[1] 网表里的 SOM 脚: ' + ', '.join(f'{k}={len(v)}' for k, v in sorted(pin_net.items()))
          + f' (合计 {tot})')
    for k in sorted(pin_net):
        miss = [i for i in range(1, 101) if i not in pin_net[k]]
        print(f'    {k}: 用到 {sorted(pin_net[k])}')

    src = open(GEN, encoding='utf-8').read()
    if 'add_som_connectors' in src:
        print('[2] 生成器里已有 add_som_connectors 调用 ⇒ 跳过注入')
    else:
        # ① 加 import + 参数常量
        imp_anchor = 'import pcbnew  # noqa: E402'
        if imp_anchor not in src:
            imp_anchor = 'import pcbnew'
        add = (imp_anchor + '\nimport sys as _sys\n'
               '_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n'
               'from som_btb_footprint import add_som_connectors  # noqa: E402\n'
               'SOM_PARAMS = os.path.join(PROJ, "HW", "PCB", "som_btb_params.json")')
        src = src.replace(imp_anchor, add, 1)
        # ② 在 BuildListOfNets 之前插调用
        call_anchor = '    board.BuildListOfNets()'
        if call_anchor not in src:
            print('★★ 找不到 board.BuildListOfNets() ⇒ 需人工接入')
            return 1
        call = ('    # ★★A2 段: SoM 的 4 组 100pin BTB 座 (Hirose DF40C-100DS-0.4V(51))\n'
                '    #   脚号编排: **奇数脚 = 一排 / 偶数脚 = 另一排** ⇒ 我们的焊盘 n 正好对插 SoM 的 n 脚\n'
                '    _som_pins = _pin_net_from_netlist()\n'
                '    add_som_connectors(board, netmap, SOM_PARAMS, _som_pins)\n\n')
        src = src.replace(call_anchor, call + call_anchor, 1)
        # ③ 辅助函数: 从网表解析脚→网
        helper = '''

def _pin_net_from_netlist():
    """从 HW/netlist_v1.csv 解析每个 J_SOM_Px 的 {脚号: 网络} (网表是唯一真源)"""
    import csv as _csv
    import re as _re
    _out = {}
    with open(NETLIST, encoding="utf-8") as _f:
        for _r in _csv.DictReader(_f):
            _net = (_r.get("net") or "").strip()
            if not _net:
                continue
            for _k in ("node1", "node2"):
                _m = _re.fullmatch(r"J_SOM_(P\\d) pin(\\d+)", (_r.get(_k) or "").strip())
                if _m:
                    _out.setdefault(_m.group(1), {})[int(_m.group(2))] = _net
    return _out
'''
        src = src.replace('\ndef main():', helper + '\n\ndef main():', 1)
        open(GEN, 'w', encoding='utf-8').write(src)
        print('[2] 已把 add_som_connectors 注入生成器')

    import ast
    ast.parse(open(GEN, encoding='utf-8').read())
    print('[3] 语法自检通过 ⇒ 重跑生成器 + 门禁')
    return 0


if __name__ == '__main__':
    sys.exit(main())
