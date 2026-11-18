#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-322 · tmp 沙盒脚本 · ★v76 链各板: R_SEL/TP_DSI 集群的 x 序 vs unc 数★
★目的: 判 "unc 高低" 到底跟【布局 lane 序】有关, 还是跟【路由器版本】有关 (★去混淆★)"""
import collections
import pcbnew

MM = 1e6
BOARDS = [
    ("state/.lastgood/baseline_v76me0_chain.kicad_pcb", 35),
    ("state/.lastgood/baseline_v76mg0_chain.kicad_pcb", 35),
    ("state/.lastgood/baseline_v76mj0_chain.kicad_pcb", 28),
    ("state/.lastgood/baseline_v76mv0_chain.kicad_pcb", 29),
    ("state/.lastgood/baseline_v76mw0_chain.kicad_pcb", 29),
    ("state/.lastgood/baseline_v76mx0_chain.kicad_pcb", 26),
    ("state/.lastgood/best_unc23_clrfix.kicad_pcb", 23),
    ("HW/PCB/demo_mainboard.kicad_pcb", 45),
]
FAMS = ["D0", "D1", "D2", "D3", "CK"]


def analyze(path):
    b = pcbnew.LoadBoard(path)
    pos = {}
    for f in b.GetFootprints():
        p = f.GetPosition()
        pos[f.GetReference()] = (round(p.x / MM, 2), round(p.y / MM, 2))
    # R_SEL 的 x 序 (决定 lane 序)
    rsel = []
    for fam in FAMS:
        n = "R_SEL_%s_N" % fam
        p = "R_SEL_%s_P" % fam
        if n in pos and p in pos:
            rsel.append((fam, pos[n][0], pos[p][0]))
    rsel.sort(key=lambda t: t[1])
    order = " ".join("%s[N%.1f/P%.1f]" % (f, n, p) for f, n, p in rsel)
    # SoM 侧 P/N 序 (固定): D3_P..D0_N
    som = []
    for fam in FAMS:
        for s in ("_P", "_N"):
            for fp in b.GetFootprints():
                for pd in fp.Pads():
                    if pd.GetNetname() == "DSI_D0_%s%s_SRC" % (fam, s):
                        q = pd.GetPosition()
                        som.append((round(q.x / MM, 2), fam, s))
    som.sort()
    som_order = " ".join("%s%s" % (f, s) for _, f, s in som)
    # 段内翻转计数: R_SEL 侧 P/N x 序 vs SoM 侧
    flip = 0
    sommap = {}
    for x, f, s in som:
        sommap[(f, s)] = x
    for fam in FAMS:
        n, p = "R_SEL_%s_N" % fam, "R_SEL_%s_P" % fam
        if n in pos and p in pos:
            if (fam, "_P") in sommap and (fam, "_N") in sommap:
                a = sommap[(fam, "_P")] - sommap[(fam, "_N")]
                c = pos[p][0] - pos[n][0]
                if a * c < 0:
                    flip += 1
    return order, som_order, flip, len(pos)


print("%-56s %5s %6s  %s" % ("board", "unc", "flip", "R_SEL 集群 x 序"))
for path, unc in BOARDS:
    try:
        order, som, flip, nfp = analyze(path)
    except Exception as e:
        print("%-56s  ERR %s" % (path, e))
        continue
    print("%-56s %5d %6d  %s" % (path.split("/")[-1][:56], unc, flip, order))
print()
print("★SoM 侧 (J_SOM_P3) DSI P/N 的固定 x 序 (★所有板都一样, 布局改不了★):")
print("   ", som)
print()
print("★flip = DSI 5 族里, 【R_SEL 侧 P/N 横向序】与【SoM 侧】相反的族数 (0 = 完全一致·无交叉需求)")
