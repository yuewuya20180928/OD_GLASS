#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-322 · tmp 沙盒脚本 · ★★每条高速腿的【已有铜量】(P vs N) ★★
★回答: N 腿是不是"单边零铜"(P 腿有铜 / N 腿一根铜都没有)"""
import sys, collections
import pcbnew

MM = 1e6
b = pcbnew.LoadBoard("HW/PCB/demo_mainboard.kicad_pcb")

seg_len = collections.defaultdict(float)
seg_cnt = collections.Counter()
via_cnt = collections.Counter()
layers = collections.defaultdict(collections.Counter)
for t in b.GetTracks():
    n = t.GetNetname()
    if t.Type() == pcbnew.PCB_VIA_T:
        via_cnt[n] += 1
        continue
    s, e = t.GetStart(), t.GetEnd()
    L = ((s.x - e.x) ** 2 + (s.y - e.y) ** 2) ** 0.5 / MM
    seg_len[n] += L
    seg_cnt[n] += 1
    layers[n][b.GetLayerName(t.GetLayer())] += 1

NETS = sorted([n for n in set(list(seg_len.keys()) + list(via_cnt.keys()))
                if n.startswith(("DSI_", "CSI_"))])
print("★现役板高速腿铜量 (★总走线长 mm / 段数 / 过孔数 / 分层段数★)")
print("%-18s %9s %6s %5s  %s" % ("net", "len_mm", "segs", "vias", "per-layer segs"))
tot_p = tot_n = 0.0
for n in NETS:
    lay = " ".join("%s:%d" % (k, v) for k, v in sorted(layers[n].items()))
    print("%-18s %9.2f %6d %5d  %s" % (n, seg_len[n], seg_cnt[n], via_cnt[n], lay))
print()
# 差分对 P/N 对照
print("── 差分族 P/N 铜量对照 (★N 为 0 ⇒ 单边零铜★)")
fams = collections.defaultdict(dict)
for n in NETS:
    for suf in ("_P_SRC", "_N_SRC", "_P", "_N"):
        if n.endswith(suf):
            fams[n[:-len(suf)]][suf] = n
            break
for fam, d in sorted(fams.items()):
    for seg in ("_SRC", ""):
        p = d.get("_P" + seg)
        q = d.get("_N" + seg)
        lp = seg_len.get(p, 0.0) if p else None
        lq = seg_len.get(q, 0.0) if q else None
        flag = ""
        if p and q:
            if lp == 0 and lq > 0:
                flag = "  ★★ P 腿零铜 / N 腿有铜"
            elif lq == 0 and lp > 0:
                flag = "  ★★★ N 腿单边零铜 (P 腿有 %.1fmm)" % lp
            elif lp == 0 and lq == 0:
                flag = "  ★ 整对零铜"
        print("  %-14s%-5s P=%-18s %8.2fmm   N=%-18s %8.2fmm%s"
              % (fam, seg or "(远端)", p or "-", lp or 0.0, q or "-", lq or 0.0, flag))
