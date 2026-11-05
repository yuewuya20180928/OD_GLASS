#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_why_blocked.py -- 对 fail_detail 里的失败段, 查它周围 1.2mm 内有什么铜
(回答: 是"被别人的铜堵死" 还是 "周围根本没铜 => 是路由器自己的避让模型/预算问题")"""
import sys, json, math, collections
import pcbnew
BOARD = sys.argv[1]
DET  = sys.argv[2]
b = pcbnew.LoadBoard(BOARD)
mm = 1e6
d = json.load(open(DET))
segs = []
for x in d:
    if "start" not in x or "goal" not in x: continue
    segs.append((x["net"], x["pad"], tuple(x["start"]), tuple(x["goal"])))
print("板: %s" % BOARD)
print("失败段条数: %d\n" % len(segs))
for net, pad, s, g in segs:
    # 线段包围盒
    x0,x1 = sorted((s[0],g[0])); y0,y1 = sorted((s[1],g[1]))
    PAD = 1.2
    def segdist(px,py,ax,ay,bx,by):
        vx,vy = bx-ax, by-ay
        L2 = vx*vx+vy*vy
        t = 0.0 if L2==0 else max(0.0,min(1.0,((px-ax)*vx+(py-ay)*vy)/L2))
        return math.hypot(px-(ax+t*vx), py-(ay+t*vy))
    blockers = collections.Counter()
    mind = 1e9
    for t in b.GetTracks():
        tn = t.GetNetname()
        if tn == net: continue
        if t.GetClass()=="PCB_VIA":
            p=t.GetPosition(); px,py = p.x/mm, p.y/mm
            if x0-PAD<=px<=x1+PAD and y0-PAD<=py<=y1+PAD:
                dd = segdist(px,py,s[0],s[1],g[0],g[1])
                blockers["VIA:"+tn]+=1
                mind=min(mind,dd)
        else:
            for a,bb in ((t.GetStart(),t.GetEnd()),):
                pass
            ax,ay = t.GetStart().x/mm, t.GetStart().y/mm
            bx,by = t.GetEnd().x/mm, t.GetEnd().y/mm
            if max(ax,bx) < x0-PAD or min(ax,bx) > x1+PAD: continue
            if max(ay,by) < y0-PAD or min(ay,by) > y1+PAD: continue
            dd = segdist(ax,ay,s[0],s[1],g[0],g[1])
            if dd<=PAD:
                blockers["TRK:"+tn]+=1
                mind=min(mind,dd)
    # 焊盘
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname()==net: continue
            pp=p.GetPosition(); px,py=pp.x/mm,pp.y/mm
            if x0-PAD<=px<=x1+PAD and y0-PAD<=py<=y1+PAD:
                dd = segdist(px,py,s[0],s[1],g[0],g[1])
                blockers["PAD:%s.%s(%s)"%(f.GetReference(),p.GetNumber(),p.GetNetname())]+=1
                mind=min(mind,dd)
    print("── %-20s pad=%-22s (%.2f,%.2f)->(%.2f,%.2f) len=%.1f" % (
        net,pad,s[0],s[1],g[0],g[1], math.hypot(g[0]-s[0],g[1]-s[1])))
    if not blockers:
        print("     ★★ 周围 1.2mm 内**没有任何异网铜** ⇒ 不是被堵 ⇒ 是路由器避让模型/预算")
    else:
        print("     最近异网铜距 %.3fmm | 阻挡者: %s" % (mind, dict(list(blockers.items())[:8])))
