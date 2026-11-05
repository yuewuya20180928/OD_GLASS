# -*- coding: utf-8 -*-
"""★probe_crossover.py -- 查官方板上两条差分线的铜: 分层统计 + 投影交叉检测
   用法: bash state/pcbnew_py.sh state/probe_crossover.py <板路径> <netA> <netB>
"""
import sys, math, pcbnew

path = sys.argv[1] if len(sys.argv) > 1 else "HW/PCB/demo_mainboard.kicad_pcb"
netA = sys.argv[2] if len(sys.argv) > 2 else "CSI_D0_CK_P"
netB = sys.argv[3] if len(sys.argv) > 3 else "CSI_D0_CK_N"

b = pcbnew.LoadBoard(path)
LNAME = {0:"F.Cu",1:"In1.Cu",2:"In2.Cu",3:"In3.Cu",4:"In4.Cu",5:"In5.Cu",6:"In6.Cu",7:"B.Cu"}

def collect(net):
    segs = []   # (layer, x1,y1,x2,y2)
    vias = []
    for t in b.GetTracks():
        if t.GetNetname() != net: continue
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            vias.append((p.x/1e6, p.y/1e6, LNAME.get(t.TopLayer(),"?"),
                         t.GetLayerSet().Seq(), 0))
        else:
            s = t.GetStart(); e = t.GetEnd()
            segs.append((t.GetLayer(), s.x/1e6, s.y/1e6, e.x/1e6, e.y/1e6))
    return segs, vias

def pads_of(net):
    out = []
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() == net:
                out.append((f.GetReference(), p.GetNumber(), p.GetPosition().x/1e6, p.GetPosition().y/1e6))
    return out

def seg_int(p1,p2,p3,p4):
    """真交叉 (非共线重叠)"""
    d1 = (p2[0]-p1[0], p2[1]-p1[1]); d2 = (p4[0]-p3[0], p4[1]-p3[1])
    den = d1[0]*d2[1] - d1[1]*d2[0]
    if abs(den) < 1e-12: return None
    t = ((p3[0]-p1[0])*d2[1] - (p3[1]-p1[1])*d2[0]) / den
    u = ((p3[0]-p1[0])*d1[1] - (p3[1]-p1[1])*d1[0]) / den
    if 1e-9 < t < 1-1e-9 and 1e-9 < u < 1-1e-9:
        return (p1[0]+t*d1[0], p1[1]+t*d1[1])
    return None

for net in (netA, netB):
    segs, vias = collect(net)
    print("══ %s: %d 段 / %d 孔 / %d 焊盘" % (net, len(segs), len(vias), len(pads_of(net))))
    byl = {}
    for s in segs: byl.setdefault(s[0], []).append(s)
    for ly in sorted(byl):
        ss = byl[ly]
        xs = [v for s in ss for v in (s[1], s[3])]; ys = [v for s in ss for v in (s[2], s[4])]
        print("   %-7s %3d 段  x %.2f..%.2f  y %.2f..%.2f" % (LNAME.get(ly,str(ly)), len(ss), min(xs), max(xs), min(ys), max(ys)))
    for p in pads_of(net):
        print("   焊盘 %-18s pad%-3s @ (%.2f, %.2f)" % p)
    print()

sa,_ = collect(netA); sb,_ = collect(netB)
xa = {(s[0], s[1], s[2], s[3], s[4]) for s in sa}
xb = {(s[0], s[1], s[2], s[3], s[4]) for s in sb}
print("── 同层投影交叉检测 (段段真交叉) ──")
found = 0
for a in sa:
    for bb in sb:
        if a[0] != bb[0]: continue
        r = seg_int((a[1],a[2]),(a[3],a[4]),(bb[1],bb[2]),(bb[3],bb[4]))
        if r:
            found += 1
            if found <= 12:
                print("   ★交叉 @ (%.3f, %.3f)  层=%s  A:(%.2f,%.2f)->(%.2f,%.2f)  B:(%.2f,%.2f)->(%.2f,%.2f)"
                      % (r[0], r[1], LNAME.get(a[0],a[0]), a[1],a[2],a[3],a[4], bb[1],bb[2],bb[3],bb[4]))
print("   同层真交叉总数 = %d" % found)

print("── 不同层 (投影重叠但不同层 ⇒ 合法跨层穿越) ──")
ov = 0
for a in sa:
    for bb in sb:
        if a[0] == bb[0]: continue
        # 粗判: 包围盒有重叠
        if (min(a[1],a[3]) < max(bb[1],bb[3]) and max(a[1],a[3]) > min(bb[1],bb[3])
            and min(a[2],a[4]) < max(bb[2],bb[4]) and max(a[2],a[4]) > min(bb[2],bb[4])):
            ov += 1
print("   跨层包围盒重叠段对 = %d (粗判)" % ov)
