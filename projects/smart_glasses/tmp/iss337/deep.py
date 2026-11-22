#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深层读数: 铜长/层分布/zone/坐标量子/网段分布 (只读)"""
import sys, re, os, collections, math

def analyze(path):
    segs = []   # (x1,y1,x2,y2,w,layer,net)
    vias = 0
    zones = 0
    nets = set()
    cur = {}
    layer = None; net = None; x1=y1=x2=y2=None; w=None
    for ln in open(path, encoding="utf-8", errors="ignore"):
        s = ln.strip()
        if s == "(segment":
            cur = {"k":"seg"}; x1=y1=x2=y2=w=None; layer=None; net=None
        elif s == "(via":
            cur = {"k":"via"}; vias += 1
        elif s == "(zone":
            zones += 1; cur = {"k":"zone"}
        elif s.startswith("(start "):
            m = re.match(r'\(start\s+([-\d.]+)\s+([-\d.]+)\)', s); x1,y1 = float(m.group(1)), float(m.group(2))
        elif s.startswith("(end "):
            m = re.match(r'\(end\s+([-\d.]+)\s+([-\d.]+)\)', s); x2,y2 = float(m.group(1)), float(m.group(2))
        elif s.startswith("(width "):
            w = float(re.match(r'\(width\s+([-\d.]+)\)', s).group(1))
        elif s.startswith("(layer "):
            layer = s.split('"')[1] if '"' in s else None
        elif s.startswith("(net "):
            m = re.search(r'\(net\s+(?:\d+\s+)?"([^"]*)"', s)
            net = m.group(1) if m else None
            if net: nets.add(net)
        elif s == ")":
            if cur.get("k") == "seg" and None not in (x1,y1,x2,y2):
                segs.append((x1,y1,x2,y2,w or 0.25, layer, net))
            cur = {}
    return segs, vias, zones, nets

def q(v, step):
    return round(v/step)

for path in sys.argv[1:]:
    if not os.path.isfile(path):
        print("%s MISSING" % path); continue
    segs, vias, zones, nets = analyze(path)
    cu = sum(math.hypot(x2-x1, y2-y1) for x1,y1,x2,y2,w,l,n in segs)
    layers = collections.Counter(l for *_ ,l,n in segs)
    netseg = collections.Counter(n for *_ , n in segs)
    widths = collections.Counter(round(w,3) for *_ ,w,l,n in segs)
    # coordinate quantum: gcd-ish on differences of coords
    xs = sorted(set(round(s[0],4) for s in segs) | set(round(s[2],4) for s in segs))
    ds = sorted(set(round(xs[i+1]-xs[i],4) for i in range(len(xs)-1)))
    small = [d for d in ds if d > 1e-9 and d < 1.0]
    from math import gcd
    g = 0
    for d in small:
        g = gcd(g, int(round(d*1e6)))
    qstep = (g/1e6) if g else None
    print("="*100)
    print("FILE: %s" % path)
    print("  segs=%d  vias=%d  zones=%d  nets_with_cu=%d" % (len(segs), vias, zones, len(nets)))
    print("  copper_length_mm=%.1f   avg_seg_len_mm=%.4f" % (cu, cu/max(1,len(segs))))
    print("  layers: %s" % dict(layers))
    print("  widths: %s" % dict(widths))
    print("  coord_quantum_mm=%s   (distinct_x=%d)" % (qstep, len(xs)))
    top = netseg.most_common(8)
    print("  top nets by seg: %s" % top)
    z = netseg.most_common()
    print("  nets_with_0_seg=%d" % (len(nets) - len([k for k,v in netseg.items() if v>0])))
