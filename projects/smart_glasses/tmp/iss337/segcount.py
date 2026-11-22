#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""段/过孔/网名/图元 计数 (只读)"""
import sys, re, os

def count(path):
    seg = via = arc = 0
    nets = set()
    for ln in open(path, encoding="utf-8", errors="ignore"):
        s = ln.strip()
        if s.startswith("(net "):
            m = re.search(r'\(net\s+(?:\d+\s+)?"([^"]*)"', s)
            if m and m.group(1):
                nets.add(m.group(1))
        if s == "(segment":
            seg += 1
        elif s == "(via":
            via += 1
        elif s == "(arc":
            arc += 1
    return seg, via, len(nets), arc, os.path.getsize(path)

if __name__ == "__main__":
    print("%-62s %8s %6s %6s %6s %12s" % ("FILE","SEG","VIA","NETS","ARC","BYTES"))
    for p in sys.argv[1:]:
        if not os.path.isfile(p):
            print("%-62s  MISSING" % p); continue
        s,v,n,a,b = count(p)
        print("%-62s %8d %6d %6d %6d %12d" % (p, s,v,n,a,b))
