#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★全图共线合并 (正确版): 证明【段数是可分解的粒度指标, 不是布线能力的指标】"""
import sys, re, math, collections

def segs_of(path):
    out=[]; cur={}; x1=y1=x2=y2=w=None; layer=None; net=None
    for ln in open(path, encoding="utf-8", errors="ignore"):
        s=ln.strip()
        if s=="(segment": cur={"k":"seg"}; x1=y1=x2=y2=w=layer=net=None
        elif s.startswith("(start "):
            m=re.match(r'\(start\s+([-\d.]+)\s+([-\d.]+)\)',s); x1,y1=float(m.group(1)),float(m.group(2))
        elif s.startswith("(end "):
            m=re.match(r'\(end\s+([-\d.]+)\s+([-\d.]+)\)',s); x2,y2=float(m.group(1)),float(m.group(2))
        elif s.startswith("(width "): w=float(re.match(r'\(width\s+([-\d.]+)\)',s).group(1))
        elif s.startswith("(layer "): layer=s.split('"')[1] if '"' in s else None
        elif s.startswith("(net "):
            m=re.search(r'\(net\s+(?:\d+\s+)?"([^"]*)"',s); net=m.group(1) if m else None
        elif s==")":
            if cur.get("k")=="seg" and None not in (x1,y1,x2,y2): out.append((x1,y1,x2,y2,w or 0.25,layer,net))
            cur={}
    return out

def full_merge(segs, tol=1e-6):
    """同(net,layer,width) 图内: 反复合并【共线且首尾相接】的两段 (无向)"""
    by = collections.defaultdict(list)
    for i,(x1,y1,x2,y2,w,l,n) in enumerate(segs):
        by[(l,n,round(w,4))].append(i)
    alive = [True]*len(segs)
    total = len(segs)
    # 端点 -> 该组内的段索引
    changed = True
    rounds = 0
    while changed:
        changed = False; rounds += 1
        for key, idxs in by.items():
            # 建端点表
            ep = collections.defaultdict(list)   # point -> list of (seg_idx, other_point)
            for i in idxs:
                if not alive[i]: continue
                x1,y1,x2,y2,w,l,n = segs[i]
                ep[(round(x1,4),round(y1,4))].append((i,(x2,y2)))
                ep[(round(x2,4),round(y2,4))].append((i,(x1,y1)))
            for pt, lst in ep.items():
                if len(lst) != 2: continue
                (i,a),(j,b) = lst
                if i==j or not alive[i] or not alive[j]: continue
                x1,y1,x2,y2,w,l,n = segs[i]
                x3,y3,x4,y4,w2,l2,n2 = segs[j]
                d1 = (x2-x1, y2-y1); d2 = (x4-x3, y4-y3)
                nd1 = math.hypot(*d1); nd2 = math.hypot(*d2)
                if nd1 < tol or nd2 < tol: continue
                cr = abs(d1[0]*d2[1]-d1[1]*d2[0])/(nd1*nd2)
                if cr > 1e-6: continue
                dot = (d1[0]*d2[0]+d1[1]*d2[1])/(nd1*nd2)
                if abs(dot) < 1.0-1e-9: continue   # 必须平行(同向或反向)
                # 合并 i+j: 用最外两端
                pts = [(x1,y1),(x2,y2),(x3,y3),(x4,y4)]
                ends = []
                for p in pts:
                    if p not in ends: ends.append(p)
                # 去掉那个被包在中间的端点: 保留两点
                if len(ends) == 3:
                    # 哪个端点是两条段的公共点
                    common = [p for p in ends if p in ((x1,y1),(x2,y2)) and p in ((x3,y3),(x4,y4))]
                    if len(common)!=1: continue
                    c = common[0]
                    o1 = (x2,y2) if (x1,y1)==c else (x1,y1)
                    o2 = (x4,y4) if (x3,y3)==c else (x3,y3)
                    ends = [o1,o2]
                if len(ends)!=2: continue
                segs[i] = (ends[0][0],ends[0][1],ends[1][0],ends[1][1],w,l,n)
                alive[j]=False
                total -= 1
                changed = True
                break
            if changed: break
    return [segs[i] for i in range(len(segs)) if alive[i]], total, rounds

for p in sys.argv[1:]:
    segs = segs_of(p)
    cu0 = sum(math.hypot(s[2]-s[0], s[3]-s[1]) for s in segs)
    m, total, rounds = full_merge(list(segs))
    cu1 = sum(math.hypot(s[2]-s[0], s[3]-s[1]) for s in m)
    print("%-58s raw=%6d  merged=%6d  (rounds=%d)  cu_raw=%.1f cu_merged=%.1f  delta=%.4f"
          % (p, len(segs), len(m), rounds, cu0, cu1, abs(cu1-cu0)))
