#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-322 · tmp 沙盒脚本 · ★★差分对【段内 P/N 顺序】是否翻转 (真交叉 ⇒ 要改板)★★
★按"段"分组: ①SoM侧 ②AC电容侧 ③连接器侧 ④测试点/串阻侧
★同一段内若 P 与 N 的 x 顺序相反 ⇒ 段内必须交叉 ⇒ 【拓扑级·可能要加 crossover 结构】"""
import collections
import pcbnew

MM = 1e6
b = pcbnew.LoadBoard("HW/PCB/demo_mainboard.kicad_pcb")

nets = collections.defaultdict(list)
for f in b.GetFootprints():
    for p in f.Pads():
        n = p.GetNetname()
        if not n:
            continue
        q = p.GetPosition()
        nets[n].append((f.GetReference(), str(p.GetNumber()), q.x / MM, q.y / MM))

fams = collections.defaultdict(lambda: collections.defaultdict(dict))
for n in nets:
    if not n.startswith(("DSI_", "CSI_")):
        continue
    for suf in ("_P_SRC", "_N_SRC", "_P", "_N"):
        if n.endswith(suf):
            fams[n[:-len(suf)]][suf][n] = nets[n]
            break

STAGE = [
    ("SoM侧", lambda r: r.startswith("J_SOM")),
    ("AC电容侧", lambda r: r.startswith("C_AC_")),
    ("连接器侧", lambda r: r.startswith("CONN_")),
    ("测试点侧", lambda r: r.startswith("TP_")),
    ("串阻侧", lambda r: r.startswith("R_SEL")),
]


def stage_of(ref):
    for nm, f in STAGE:
        if f(ref):
            return nm
    return "其他:" + ref


print("★段内 P/N 横向顺序 (★同段内 x 顺序相反 ⇒ 段内必须交叉★)")
flip = 0
total_seg = 0
for fam in sorted(fams):
    d = fams[fam]
    for seg in ("_SRC", ""):
        P = d.get("_P" + seg)
        N = d.get("_N" + seg)
        if not P or not N:
            continue
        pnet = list(P.keys())[0]
        nnet = list(N.keys())[0]
        # 按段聚合每个 P/N 焊盘的 x
        byst = collections.defaultdict(lambda: {"P": [], "N": []})
        for r, num, x, y in P[pnet]:
            byst[stage_of(r)]["P"].append(x)
        for r, num, x, y in N[nnet]:
            byst[stage_of(r)]["N"].append(x)
        for st in sorted(byst):
            ps = byst[st]["P"]
            ns = byst[st]["N"]
            if not ps or not ns:
                continue
            total_seg += 1
            pm, nm_ = sum(ps) / len(ps), sum(ns) / len(ns)
            if abs(pm - nm_) < 0.01:
                verdict = "★P/N 同位(重合)★"
            elif pm < nm_:
                verdict = "P在左"
            else:
                verdict = "★N在左 ⇒ 段内需交叉★"
                flip += 1
            print("  %-10s %-9s %-10s P:%-14s(x=%7.2f)  N:%-14s(x=%7.2f)  %s"
                  % (fam, seg or "(远端)", st, ",".join(sorted(set(P.keys()))), pm,
                     ",".join(sorted(set(N.keys()))), nm_, verdict))
print()
print("★同段比较总数 = %d · 其中【N在左 ⇒ 段内需交叉】 = %d" % (total_seg, flip))
print("★注: 段内交叉在 8 层板上可用【换层绕开】实现 ⇒ 不必然要加 crossover 结构;")
print("     但【同一层同一走廊】内无法绕 ⇒ 需要成对规划 (pair-aware) 才能绕开。")
