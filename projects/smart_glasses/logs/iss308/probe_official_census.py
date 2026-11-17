import pcbnew, sys, collections, json
b = pcbnew.LoadBoard(sys.argv[1])
seg = collections.defaultdict(collections.Counter); vias = collections.Counter(); pad = collections.Counter()
for t in b.GetTracks():
    n = t.GetNetname()
    if t.GetClass() == "PCB_VIA": vias[n]+=1
    else: seg[n][b.GetLayerName(t.GetLayer())]+=1
for fp in b.GetFootprints():
    for p in fp.Pads():
        pad[p.GetNetname()]+=1
out={}
for n in sorted(set(seg)|set(vias)|set(pad)):
    out[n]={"seg":dict(seg[n]),"seg_total":int(sum(seg[n].values())),"pads":int(pad[n]),"vias":int(vias[n])}
json.dump(out, open(sys.argv[2],"w"), ensure_ascii=False, indent=1)
print("nets:",len(out))
