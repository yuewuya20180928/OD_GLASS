import pcbnew, sys, collections
b = pcbnew.LoadBoard(sys.argv[1])
length = collections.defaultdict(float); nseg = collections.Counter()
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA": continue
    length[t.GetNetname()] += t.GetLength(); nseg[t.GetNetname()] += 1
for n in sorted(length):
    print("%-16s %9.3f mm  segs=%d" % (n, length[n]/1e6, nseg[n]))
