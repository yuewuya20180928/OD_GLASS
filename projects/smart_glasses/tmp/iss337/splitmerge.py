#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★段数归一化检验: 把段按 0.25mm 切碎 / 把共线相邻段合并 ⇒ 看段数是否收敛到同一口径"""
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

def split_seg(sg, q):
    x1,y1,x2,y2,w,l,n = sg
    L = math.hypot(x2-x1, y2-y1)
    if L <= q*1.001: return 1
    # axis-aligned only (all official segs are 45/90)
    k = max(1, int(math.ceil(L/q - 1e-9)))
    return k

def count_split(segs, q):
    return sum(split_seg(s,q) for s in segs)

def merge_collinear(segs, tol=1e-6):
    """合并同层同网同宽、共线、端点相接的段 (贪心)"""
    by = collections.defaultdict(list)
    for i,s in enumerate(segs):
        x1,y1,x2,y2,w,l,n = s
        # 用规范化方向
        if (x1,y1) <= (x2,y2): a,b=(x1,y1),(x2,y2)
        else: a,b=(x2,y2),(x1,y1)
        key=(l,n,round(w,4))
        by[key].append((a,b,i))
    merged = 0
    for key, items in by.items():
        # 端点字典
        adj = collections.defaultdict(list)
        for a,b,i in items:
            adj[a].append((b,i)); adj[b].append((a,i))
        visited=set()
        for i,(a,b,_) in enumerate(items):
            if i in visited: continue
            # 走链
            chain=[a,b]; visited.add(i)
            changed=True
            while changed:
                changed=False
                for e in chain[-1:]:
                    for (o,j) in adj.get(e,[]):
                        if j not in visited:
                            # 检查共线
                            d1=(b[0]-a[0], b[1]-a[1]); d2=(o[0]-e[0], o[1]-e[1])
                            cr = d1[0]*d2[1]-d1[1]*d2[0]
                            nd1=math.hypot(*d1); nd2=math.hypot(*d2)
                            if nd1>0 and nd2>0 and abs(cr)/(nd1*nd2) < 1e-6:
                                chain.append(o); visited.add(j); changed=True; break
                    if changed: break
            merged += 1
    return merged

for p in sys.argv[1:]:
    try:
        segs = segs_of(p)
    except FileNotFoundError:
        print("%s MISSING"%p); continue
    cu = sum(math.hypot(s[2]-s[0], s[3]-s[1]) for s in segs)
    lens = collections.Counter(round(math.hypot(s[2]-s[0], s[3]-s[1]),3) for s in segs)
    print("="*96)
    print("FILE: %s" % p)
    print("  raw_segs=%d  copper_mm=%.1f  avg_len=%.4f" % (len(segs), cu, cu/max(1,len(segs))))
    for q in (0.25, 0.125):
        print("  split@%.3fmm ⇒ %d segs" % (q, count_split(segs, q)))
    print("  merge_collinear ⇒ %d segs" % merge_collinear(segs))
    print("  top_len_hist: %s" % lens.most_common(10))
