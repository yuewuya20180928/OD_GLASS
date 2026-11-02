#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss165_som_pins_full.py —— SOM 引脚映射**全量**重建 (399 行全覆盖, 含 GPIO)

★★ 关键结构 (11-03 00:5x 实测): 手册 §2.6.2 的引脚表按**连接器分 4 组表**, 每组表的 NUM 列 = **组内脚号 1..100**
   (★所以我之前的 CSV 丢的是"属于哪个连接器"这一维 ⇒ 一直拿组内脚号当全局号 ⇒ 板子绑不上)
★★ 归属怎么定: 用 §2.7 功能表的 "Signal Name → P<x>_<n>" 反查 —— 同一信号在两处出现 ⇒ 可直接配对
   ⇒ ★★ **功能表没有的信号 (纯 GPIO 等) ⇒ 用该表自身的组内 NUM + 推断出的连接器号 ⇒ 同样拿到 (x, n)**
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
OUTJ = f'{PROJ}/HW/PCB/som_pin_full_map.json'

t = open(MANUAL, encoding='utf-8', errors='replace').read()
tables = re.findall(r'<table.*?</table>', t, re.S)


def rows_of(tb):
    out = []
    for tr in re.findall(r'<tr.*?</tr>', tb, re.S):
        cells = [html.unescape(re.sub(r'<[^>]+>', '', c)).strip() for c in re.findall(r'<t[dh].*?</t[dh]>', tr, re.S)]
        if cells:
            out.append(cells)
    return out


# ── ① §2.7 功能表: Signal Name → (x, n) ──
func = collections.defaultdict(set)
pin_tables = []
for tb in tables:
    rs = rows_of(tb)
    if not rs:
        continue
    hdr = [x.upper() for x in rs[0]]
    if 'FUNCTION' in hdr and 'PIN NUMBER' in hdr:
        idx_sig = hdr.index('SIGNAL NAME')
        idx_pin = hdr.index('PIN NUMBER')
        for r in rs[1:]:
            if len(r) <= max(idx_sig, idx_pin):
                continue
            m = re.fullmatch(r'P(\d+)_(\d+)', r[idx_pin].strip())
            if m:
                func[r[idx_sig].strip()].add((int(m.group(1)), int(m.group(2))))
    elif 'NUM' in hdr and 'SIGNAL NAME' in hdr:
        pin_tables.append(rs)

print(f"[1] 功能表: 信号 → (P组, 组内脚) 命中 {len(func)} 个信号; §2.6.2 引脚表 {len(pin_tables)} 张")

# ── ② 每张引脚表 → 归属连接器 (用功能表反查众数) ──
sig2conn = {}
unresolved_tables = []
for ti, rs in enumerate(pin_tables):
    votes = collections.Counter()
    for r in rs[1:]:
        if len(r) < 3:
            continue
        num = r[0].strip()
        sig = r[2].strip()
        if not num.isdigit() or not sig:
            continue
        cands = func.get(sig)
        if cands:
            x, n = sorted(cands)[0]
            votes[x] += 1
            sig2conn.setdefault(sig, (x, n, num))
    if votes:
        x = votes.most_common(1)[0][0]
    else:
        x = None
        unresolved_tables.append(ti)
    # 整表补齐 (无功能表引用的信号 ⇒ 用本表 NUM 作组内脚号)
    for r in rs[1:]:
        if len(r) < 3:
            continue
        num, sig = r[0].strip(), r[2].strip()
        if not num.isdigit() or not sig or sig in sig2conn:
            continue
        if x is not None:
            sig2conn[sig] = (x, int(num), num)
    print(f"    表{ti}: {len(rs)-1} 行 ⇒ 归属 P{x if x else '?'} (票数 {dict(votes) if votes else '无'})")

print(f"[2] 全量映射: {len(sig2conn)} 个信号 (含 GPIO)")
missing_group = [s for s, v in sig2conn.items() if v[0] is None]
print(f"    无归属的信号: {len(missing_group)} {missing_group[:8]}")

# ── ③ 重建 CSV (带连接器列!) ──
with open(CSVF, 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['num', 'conn', 'ball', 'signal', 'gpio', 'vol', 'desc'])
    for rs in pin_tables:
        hdr = [x.upper() for x in rs[0]]
        i_num = hdr.index('NUM')
        i_ball = hdr.index('BALL') if 'BALL' in hdr else 1
        i_sig = hdr.index('SIGNAL NAME')
        i_gpio = hdr.index('GPIO') if 'GPIO' in hdr else None
        i_vol = hdr.index('VOL') if 'VOL' in hdr else None
        i_desc = hdr.index('PIN DESCRIPTION') if 'PIN DESCRIPTION' in hdr else None
        for r in rs[1:]:
            if len(r) <= i_sig:
                continue
            num = r[i_num].strip()
            sig = r[i_sig].strip()
            if not num.isdigit():
                continue
            v = sig2conn.get(sig)
            conn = f"P{v[0]}" if v else ""
            w.writerow([num, conn, r[i_ball].strip() if len(r) > i_ball else '',
                        sig,
                        r[i_gpio].strip() if i_gpio is not None and len(r) > i_gpio else '',
                        r[i_vol].strip() if i_vol is not None and len(r) > i_vol else '',
                        r[i_desc].strip() if i_desc is not None and len(r) > i_desc else ''])
print(f"[3] CSV 已重建 (带 conn 列): {CSVF}")

# ── ④ 落 JSON ──
json.dump({s: {'conn': f"P{v[0]}", 'num': v[1], 'global_num': v[2]} for s, v in sig2conn.items()},
          open(OUTJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"[4] 全量映射已落: {OUTJ}")
