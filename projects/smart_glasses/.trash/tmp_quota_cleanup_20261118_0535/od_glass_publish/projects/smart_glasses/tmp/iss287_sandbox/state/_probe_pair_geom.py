#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查差分对 P/N 焊盘位置 + 旁边 P 侧铜箔宽度 (★查"差分自短路"的物理成因)
用法: bash state/pcbnew_py.sh state/_probe_pair_geom.py <板文件>
"""
import sys
import pcbnew

path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/v28_H.kicad_pcb"
b = pcbnew.LoadBoard(path)

nets = {}
for code, name in b.GetNetsByNetcode().items():
    nets[code] = name

want = sys.argv[2:] or ["DSI_D0_CK_P_SRC", "DSI_D0_CK_N_SRC"]

for w in want:
    code = b.GetNetcodeFromNetname(w)
    print("=== %s (netcode=%d) ===" % (w, code))
    pads = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetCode() == code:
                pos = p.GetPosition()
                pads.append((fp.GetReference(), p.GetNumber(),
                             pos.x / 1e6, pos.y / 1e6,
                             p.GetSize().x / 1e6, p.GetSize().y / 1e6))
    for t in pads:
        print("   焊盘 %s.%s @ (%.2f, %.2f) 尺寸 %.2f×%.2f" % t)
    # 该网的走线宽度分布
    widths = {}
    for t in b.GetTracks():
        if t.GetNetCode() != code:
            continue
        if t.Type() != pcbnew.PCB_TRACE_T:
            continue
        w = round(t.GetWidth() / 1e6, 3)
        widths[w] = widths.get(w, 0) + 1
    print("   走线宽度分布:", widths)
    # 焊盘附近 1.5mm 内的走线 (别的网也列, 用来看"旁边是谁")
    if pads:
        px, py = pads[0][2], pads[0][3]
        near = []
        for t in b.GetTracks():
            if t.Type() != pcbnew.PCB_TRACE_T:
                continue
            s = t.GetStart()
            e = t.GetEnd()
            for (qx, qy) in ((s.x / 1e6, s.y / 1e6), (e.x / 1e6, e.y / 1e6)):
                if abs(qx - px) < 1.5 and abs(qy - py) < 1.5:
                    near.append((nets.get(t.GetNetCode(), "?"),
                                 round(t.GetWidth() / 1e6, 3),
                                 b.GetLayerName(t.GetLayer()),
                                 round(s.x / 1e6, 2), round(s.y / 1e6, 2),
                                 round(e.x / 1e6, 2), round(e.y / 1e6, 2)))
                    break
        print("   焊盘附近 1.5mm 内的走线 (%d 条):" % len(near))
        for n in near[:14]:
            print("      ", n)
