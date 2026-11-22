#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★用【真生成器的真 _merge_collinear】(import, 不改真件) 跑 merge_fix=False / True
   ⇒ 直接量出「段数差是不是就由这一个开关造成」"""
import sys, os, pickle, importlib.util
sys.path.insert(0, os.path.join(os.getcwd(),"state"))
import pcbnew  # noqa
spec = importlib.util.spec_from_file_location("realRT", os.path.join(os.getcwd(),"state/gen_pcb_routing.py"))
RT = importlib.util.module_from_spec(spec); spec.loader.exec_module(RT)
print("★用的是真生成器的 _merge_collinear (只读 import)")

for pkl in sys.argv[1:]:
    d=pickle.load(open(pkl,"rb"))
    paths=d["paths"]
    # 官方板路径的段元组格式 = (net,x1,y1,x2,y2,li,w) ⇒ 需转成生成器内部格式
    # 生成器 seg 元组 = (net,x1,y1,x2,y2,li,width)  ⇒ 一致
    for mf in (False, True):
        tot=0; tot_cu=0.0
        for path in paths:
            seg=[]
            for (x1,y1,x2,y2,w,l,n) in path:
                li = {"F.Cu":0,"In2.Cu":2,"In4.Cu":4,"In6.Cu":6}.get(l,0)
                seg.append((n,x1,y1,x2,y2,li,w))
            m=RT._merge_collinear(seg, mf)
            tot+=len(m)
            import math
            for s in m: tot_cu+=math.hypot(s[3]-s[1], s[4]-s[2])
        print("  %-52s merge_fix=%-5s ⇒ %6d 段 (原始 %d)  cu=%.1f" % (d["board"], mf, tot, d["raw"], tot_cu))
