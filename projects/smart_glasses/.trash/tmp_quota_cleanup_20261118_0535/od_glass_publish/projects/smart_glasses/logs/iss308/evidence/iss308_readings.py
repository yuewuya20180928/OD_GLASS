#!/usr/bin/env python3
"""Readings extractor: DRC / unc items / unc nets / per-net copper census / zero-copper nets."""
import json, re, sys, collections

def nets_of(it):
    s = json.dumps(it, ensure_ascii=False)
    return sorted(set(re.findall(r"\[([A-Za-z0-9_]+)\]", s)))

def stats(drcpath, laypath=None):
    d = json.load(open(drcpath, encoding="utf-8"))
    v = d.get("violations") or []
    unc = d.get("unconnected_items") or []
    per = collections.Counter()
    for it in unc:
        for n in nets_of(it):
            per[n] += 1
    return {
        "drc": len(v),
        "drc_kinds": dict(collections.Counter((x.get("type") or "?") for x in v).most_common()),
        "unc_items": len(unc),
        "unc_nets": len(per),
        "netlist": dict(per.most_common()),
    }

if __name__ == "__main__":
    for p in sys.argv[1:]:
        print("=" * 100)
        print("FILE:", p)
        try:
            s = stats(p)
        except Exception as e:
            print("  ERR", e); continue
        print("  DRC=%d  unc_items=%d  unc_nets=%d" % (s["drc"], s["unc_items"], s["unc_nets"]))
        print("  DRC kinds:", s["drc_kinds"])
        print("  UNC NETS:", s["netlist"])
