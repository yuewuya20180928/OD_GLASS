#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_blocked.py —— ★解剖"布不动的脚"到底卡在哪 (2026-11-05 06:50)

用法: bash state/pcbnew_py.sh state/analyze_blocked.py [板文件]
默认: 官方板 HW/PCB/demo_mainboard.kicad_pcb

输出 (每行都是机器读出的事实):
  · 布不动的网: 每个网有几个焊盘未连 + 焊盘类型 (SoM BTB / 其它) + 坐标 + 周围 1.5mm 内的**别的**焊盘数
  · 差分对 N 侧 vs P 侧: 两侧焊盘数 / 未连数 / 是否同一排
★目的: 分清 "**几何上就没路**"(通道被占) 与 "**路由顺序吃亏**"(被先布的网挤掉)
"""
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PCB = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")

board = pcbnew.LoadBoard(PCB)
print("板: %s" % PCB)

# 焊盘表: (netname) -> [(ref, pad, x, y, layer, is_btb)]
bynet = {}
allpads = []
for fp in board.GetFootprints():
    ref = fp.GetReference()
    is_btb = ref.startswith("J_SOM")
    for pad in fp.Pads():
        try:
            net = pad.GetNetname()
        except Exception:
            net = ""
        pos = pad.GetPosition()
        x = pcbnew.ToMM(pos.x)
        y = pcbnew.ToMM(pos.y)
        lay = board.GetLayerName(pad.GetLayer())
        rec = (ref, pad.GetNumber(), x, y, lay, is_btb)
        allpads.append(rec)
        if net:
            bynet.setdefault(net, []).append(rec)

print("焊盘总数 %d · 有网 %d 个网" % (len(allpads), len(bynet)))


def ratsnest_unconnected():
    """★**未连的网** —— ★2026-11-05 06:50 改从 **DRC json** 读 (同事指出的坑)
       ★原来的 `conn.GetRatsnestForNet(net, 0)` **传了 2 个参**, pcbnew 只收 1 个 (netcode:int)
       ⇒ TypeError 被 `except: n=None` 吞掉 ⇒ ★"未连的网"永远输出 0 (实际 101 项 / 60 网)
       ⇒ 最省事且口径一致的做法: 读 DRC 跑出来的 unconnected_items (与 verify 同一份证据)
    """
    import json as _json
    import re as _re
    drc = "/tmp/_layout_done_drc.json"
    try:
        d = _json.load(open(drc, encoding="utf-8"))
    except Exception:
        return []
    out = []
    seen = set()
    for u in (d.get("unconnected_items") or []):
        nets = set()
        for it in (u.get("items") or []):
            m = _re.search(r"\[([^\]]+)\]", it.get("description", ""))
            if m:
                nets.add(m.group(1))
        for n in nets:
            if n in seen:
                continue
            seen.add(n)
            out.append((n, None, bynet.get(n, [])))
    return out


un = ratsnest_unconnected()
print("\n=== 未连的网 (%d 个, 口径 = DRC json) ===" % len(un))
rows = []
for (net, n, pads) in un:
    if not pads:
        print("  %-26s ★**板上没这个网的焊盘?**" % net)
        continue
    btb = sum(1 for p in pads if p[5])
    cong = []
    for (ref, num, x, y, lay, _) in pads:
        c = 0
        for (r2, n2, x2, y2, l2, _) in allpads:
            if r2 == ref and n2 == num:
                continue
            if (x2 - x) ** 2 + (y2 - y) ** 2 <= 1.5 ** 2:
                c += 1
        cong.append(c)
    rows.append((n, net, len(pads), btb, min(cong) if cong else 0, max(cong) if cong else 0, pads))
rows.sort(key=lambda r: -r[2])
for (n, net, npads, btb, cmin, cmax, pads) in rows[:26]:
    print("  %-26s 焊盘 %-3d (BTB %d)  周围1.5mm焊盘 %d~%d" % (net, npads, btb, cmin, cmax))
    for (ref, num, x, y, lay, isbtb) in pads[:3]:
        print("        %-10s.%-4s (%7.3f,%7.3f) %-8s%s" % (ref, num, x, y, lay, "  ★BTB" if isbtb else ""))

print("\n=== 差分对: P 侧 vs N 侧 (未连的网里成对的) ===")
unmap = {r[1]: r for r in rows}
for (net, n, pads) in un:
    if not (net.endswith("_N") or net.endswith("_N_SRC")):
        continue
    p_net = net[:-2] + "_P" if net.endswith("_N") else net[:-6] + "_P_SRC"
    if p_net not in bynet:
        continue
    pn = unmap.get(p_net)
    ppads = bynet[p_net]
    npads = bynet[net]
    btb_p = sum(1 for p in ppads if p[5])
    btb_n = sum(1 for p in npads if p[5])
    print("  %-24s 未连=%-4s | %-24s 未连=%-4s  焊盘 P:%d(BTB %d) N:%d(BTB %d)"
          % (p_net, (pn[0] if pn else "0"), net, n, len(ppads), btb_p, len(npads), btb_n))
