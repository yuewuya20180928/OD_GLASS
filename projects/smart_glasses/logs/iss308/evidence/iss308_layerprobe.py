#!/usr/bin/env python3
"""ISS-308 probe: per-net per-layer copper census on a candidate board."""
import sys, json, collections
import pcbnew

_B=None
def lname(li):
    try:
        n = _B.GetLayerName(li)
        if n: return n
    except Exception:
        pass
    return "L%d" % li

path = sys.argv[1]
b = pcbnew.LoadBoard(path)
if b is None:
    print("LOAD FAIL"); raise SystemExit(2)
_B=b

seg = collections.defaultdict(collections.Counter)
pad = collections.defaultdict(collections.Counter)
vias = collections.Counter()
padlist = collections.defaultdict(list)

for t in b.GetTracks():
    net = t.GetNetname()
    li = t.GetLayer()
    if t.GetClass() == "PCB_VIA":
        vias[net] += 1
    else:
        seg[net][li] += 1

for fp in b.GetFootprints():
    ref = fp.GetReference()
    for p in fp.Pads():
        net = p.GetNetname()
        for li in p.GetLayerSet().Seq():
            pad[net][li] += 1
        padlist[net].append((ref, p.GetPadName(), p.GetPosition(), lname(p.GetLayer())))

out = {}
for n in sorted(set(seg) | set(pad)):
    out[n] = {
        "seg": {lname(k): v for k, v in sorted(seg[n].items())},
        "seg_total": int(sum(seg[n].values())),
        "pad": {lname(k): v for k, v in sorted(pad[n].items())},
        "pad_total": int(sum(pad[n].values())),
        "vias": int(vias[n]),
    }
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
print("nets:", len(out))
lm = {}
for li in range(64):
    try:
        n = b.GetLayerName(li)
        if n: lm[str(li)] = n
    except Exception:
        pass
json.dump(lm, open(sys.argv[2] + ".layermap.json", "w"), ensure_ascii=False, indent=1)
print("layermap:", lm)
