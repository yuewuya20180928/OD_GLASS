#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""逐网铜长/段数 对照 (只读)"""
import sys, re, math, collections, json

def load(path):
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

def stats(segs):
    cu=collections.Counter(); ns=collections.Counter()
    for x1,y1,x2,y2,w,l,n in segs:
        cu[n]+=math.hypot(x2-x1,y2-y1); ns[n]+=1
    return cu, ns

def split_cu(segs, q):
    c=collections.Counter()
    for x1,y1,x2,y2,w,l,n in segs:
        L=math.hypot(x2-x1,y2-y1)
        k=max(1,int(math.ceil(L/q-1e-9)))
        c[n]+=L
    return c

paths = sys.argv[1:]
data={}
for p in paths:
    segs=load(p); cu,ns=stats(segs)
    data[p]=(cu,ns,sum(cu.values()),len(segs))
    print("%-64s segs=%6d cu_mm=%8.1f nets_cu=%d" % (p, len(segs), sum(cu.values()), len(cu)))

if len(paths)>=2:
    a,b = paths[0], paths[1]
    cuA,nsA,totA,nsegA = data[a]
    cuB,nsB,totB,nsegB = data[b]
    allnets = sorted(set(cuA)|set(cuB))
    print("\n%-34s %10s %10s %8s | %8s %8s" % ("NET","cuA_mm","cuB_mm","d_cu","segA","segB"))
    rows=[]
    for n in allnets:
        d = cuB.get(n,0.0)-cuA.get(n,0.0)
        rows.append((n,cuA.get(n,0.0),cuB.get(n,0.0),d,nsA.get(n,0),nsB.get(n,0)))
    for r in sorted(rows,key=lambda r:-abs(r[3]))[:30]:
        print("%-34s %10.1f %10.1f %8.1f | %8d %8d" % r)
    print("\n=== 总量 ===")
    print("cuA=%.1f cuB=%.1f  ratio=%.3f  segA=%d segB=%d ratio=%.3f" % (totA,totB,totB/totA,nsegA,nsegB,nsegB/nsegA))
    # 每网铜长相符的网数
    ok=sum(1 for n in allnets if abs(cuB.get(n,0)-cuA.get(n,0))<0.05)
    print("铜长相符(<0.05mm)的网: %d / %d" % (ok,len(allnets)))
    zA=set(n for n in allnets if cuA.get(n,0)==0); zB=set(n for n in allnets if cuB.get(n,0)==0)
    print("零铜网 A=%d B=%d  差集=%d" % (len(zA),len(zB),len(zB-zA)))
