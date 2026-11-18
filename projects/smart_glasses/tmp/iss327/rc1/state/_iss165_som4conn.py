#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss165_som4conn.py —— A2 段收口: SOM 座改成 **4 个独立 100 脚座 (P1..P4)**

★★ 根因 (11-03 00:4x 实测): Forlinx 手册里脚标识是 **`P3_91` 这种「连接器_脚号」形式**
   (4 个 BTB 各 100 脚, 脚号各自独立) ⇒ ★**主板上应该是 4 个 100 脚座, 不是一个 400 脚座**
   ⇒ 我之前的 CSV 丢了 "P<x>_" 前缀 ⇒ 全局 num 与物理脚对应错 ⇒ 板子绑不上网络 (18 处对不上)。

做法:
  ① 从手册全文抽 `P<x>_<n>` 标识 + 邻近信号名 ⇒ 得 signal → [(x,n)]
  ② 用 §2.6.2 表的 (num, ball, signal) 作桥 ⇒ 得 全局 num → (x, n)
  ③ 网表节点 `J_SOM pin<全局num>` → `J_SOM_P<x> pin<n>` (脚标识带连接器号 ⇒ 不可能撞脚)
  ④ 板生成器: 画 **4 个 100 脚座** (J_SOM_P1..P4), 焊盘编号 = 组内脚号, 网络按 (组, 组内脚) 绑定
"""
import collections
import csv
import html
import json
import os
import re

PROJ = '/home/yuewuya/.openclaw/workspace/projects/smart_glasses'
MANUAL = '/tmp/fx3576.html'
CSVF = f'{PROJ}/HW/PCB/FET3576C_PIN_TABLE.csv'
GEN = f'{PROJ}/state/gen_netlist.py'
PCBGEN = f'{PROJ}/state/gen_pcb_netlist_board.py'

# ── ① 手册全文: P<x>_<n> + 邻近信号名 ──
t = open(MANUAL, encoding='utf-8', errors='replace').read()
plain = html.unescape(re.sub(r'<[^>]+>', '\n', re.sub(r'<script.*?</script>', '', t, flags=re.S)))
lines = [l.strip() for l in plain.split('\n') if l.strip()]
SKIP = {'PIN', 'NUM', 'BALL', 'GPIO', 'VOL', 'SIGNAL', 'NAME', 'FUNCTION', 'POWER', 'INPUT', 'OUTPUT',
        'DEFAULT', 'NOTE', 'GND', 'TABLE', 'ROW', 'AND', 'THE', 'FOR', 'WITH', 'THIS', 'THAT', 'TYPE',
        'LEVEL', 'CARRIER', 'BOARD', 'CONNECTOR', 'SUPERSCRIPT', 'MEANING', 'NUMBER', 'CONFIGURABLE'}
sig2conn = collections.defaultdict(set)
pat = re.compile(r'P(\d+)_(\d+)')
for i, l in enumerate(lines):
    for m in pat.finditer(l):
        g, n = int(m.group(1)), int(m.group(2))
        ctx = ' '.join(lines[max(0, i - 6):i + 7])
        for cand in re.findall(r'\b([A-Z][A-Z0-9_]{4,})\b', ctx):
            if cand in SKIP or cand.startswith('P') and '_' in cand:
                continue
            sig2conn[cand].add((g, n))

# ── ② §2.6.2 表: (num, signal) ⇒ 桥到 (x,n) ──
num2conn = {}
with open(CSVF, encoding='utf-8') as f:
    for r in csv.DictReader(f):
        num = (r.get('num') or '').strip()
        sig = (r.get('signal') or '').strip()
        if not num.isdigit() or not sig:
            continue
        cands = sig2conn.get(sig)
        if cands:
            num2conn[num] = sorted(cands)[0]
print(f"[1] 桥接完成: 全局 num → (连接器, 组内脚) 命中 {len(num2conn)} / 399")

# ── ③ 网表节点改写: J_SOM pin<全局num> → J_SOM_P<x> pin<n> ──
g = open(GEN, encoding='utf-8').read()
cnt, miss = 0, []
def repl(m):
    global cnt
    num = m.group(1)
    if num in num2conn:
        x, n = num2conn[num]
        cnt += 1
        return f'J_SOM_P{x} pin{n}'
    miss.append(num)
    return m.group(0)
g2 = re.sub(r'J_SOM pin(\d+)', repl, g)
open(GEN, 'w', encoding='utf-8').write(g2)
print(f"[2] 网表节点改写 {cnt} 处; 未桥接 {len(set(miss))} 个: {sorted(set(miss))[:12]}")

# ── ④ 板生成器: 4 个 100 脚座 ──
p = open(PCBGEN, encoding='utf-8').read()
old_som_start = p.index('    # ★2026-11-03 00:6x: 把网表里 "J_SOM pin<N>" 的网络绑到 BTB 焊盘')
old_som_end = p.index('    board.BuildListOfNets()')
new_block = '''    # ★★2026-11-03 00:5x: SOM 座 = **4 个独立 100 脚 BTB (P1..P4)** (Forlinx 脚标识是 P<x>_<num> 形式, 4 个连接器脚号各自独立)
    #   依据: HW/PCB/som_pin_map.json (全局 num ↔ (连接器, 组内脚)) + HW/PCB/FET3576C_PIN_TABLE.csv
    #   网络来源: 网表里 "J_SOM_P<x> pin<n>" 节点所在的网
    import csv as _csv
    som_net = {}
    _np = os.path.join(PROJ, "HW", "netlist_v1.csv")
    if os.path.exists(_np):
        for _r in _csv.DictReader(open(_np, encoding="utf-8")):
            _net = (_r.get("net") or "").strip()
            for _nd in ((_r.get("node1") or ""), (_r.get("node2") or "")):
                if _nd.startswith("J_SOM_P") and _net:
                    _pn = _nd.split("pin", 1)[1].strip()
                    som_net.setdefault(_nd.split()[0], {}).setdefault(_pn, set()).add(_net)
    _SOM_ORIGIN = {"J_SOM_P1": (sx + 4.0, sy + 6.0), "J_SOM_P2": (sx + 44.0, sy + 6.0),
                    "J_SOM_P3": (sx + 4.0, sy + 10.0), "J_SOM_P4": (sx + 44.0, sy + 10.0)}
    for _ref, (_ox, _oy) in _SOM_ORIGIN.items():
        _fp = pcbnew.FOOTPRINT(board)
        _fp.SetReference(_ref)
        _fp.SetValue("Forlinx FET3572-C SoM 100pin BTB 0.4mm")
        _rr = pcbnew.PCB_SHAPE(board)
        _rr.SetShape(pcbnew.SHAPE_T_SEGMENT)
        _rr.SetLayer(pcbnew.F_Fab)
        _rr.SetStart(V(_ox - 20.0, _oy - 0.8))
        _rr.SetEnd(V(_ox + 20.0, _oy - 0.8))
        _rr.SetWidth(int(0.1 * MM))
        _fp.Add(_rr)
        for _k in range(1, 101):
            _px = _ox - 19.8 + (_k - 1) * 0.4
            _pad = pcbnew.PAD(_fp)
            _pad.SetNumber(str(_k))
            _pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            _pad.SetShape(pcbnew.PAD_SHAPE_RECT)
            _pad.SetSize(V(0.18, 0.6))
            _pad.SetPosition(V(_px, _oy))
            _pad.SetLayerSet(_pad.SMDMask())
            _nets = sorted(som_net.get(_ref, {}).get(str(_k), ()))
            if _nets:
                _ni = netmap.get(_nets[0])
                if _ni is not None:
                    _pad.SetNet(_ni)
            _fp.Add(_pad)
        _fp.SetPosition(V(0, 0))
        board.Add(_fp)
    # SOM 承载区外形 (68×50mm) —— 只作装配参考, 不是铜
    _so = pcbnew.PCB_SHAPE(board)
    _so.SetShape(pcbnew.SHAPE_T_SEGMENT)
    _so.SetLayer(pcbnew.F_Fab)
    _so.SetStart(V(sx, sy))
    _so.SetEnd(V(sx + sw, sy))
    _so.SetWidth(int(0.1 * MM))
    board.Add(_so)

'''
p2 = p[:old_som_start] + new_block + p[old_som_end:]
open(PCBGEN, 'w', encoding='utf-8').write(p2)
import ast
ast.parse(p2)
print("[3] 板生成器: SOM 座改为 4 个独立 100 脚座 (J_SOM_P1..P4)")

# ── 落映射表 ──
json.dump({k: [list(x) for x in v] for k, v in sorted(sig2conn.items())},
          open(f'{PROJ}/HW/PCB/som_signal_to_connector.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
with open(f'{PROJ}/HW/PCB/SOM_PIN_ASSIGNMENT.md', 'a', encoding='utf-8') as f:
    f.write("\n## ★★11-03 00:5x 修正: 脚标识是 `P<x>_<num>` 形式 ⇒ **主板上是 4 个独立 100 脚座 (P1..P4)**, 不是 400 脚单座\n\n")
    f.write("| 全局 num | 连接器 | 组内脚 |\n|---|---|---|\n")
    for num in sorted(num2conn, key=lambda x: int(x)):
        x, n = num2conn[num]
        f.write(f"| {num} | P{x} | {n} |\n")
print("[4] 映射表已落 HW/PCB/som_signal_to_connector.json + SOM_PIN_ASSIGNMENT.md 追加")
