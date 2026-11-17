import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1])
import collections
L=collections.defaultdict(float); N=collections.Counter()
for t in b.GetTracks():
    if t.GetClass()=="PCB_VIA": continue
    L[t.GetNetname()]+=t.GetLength(); N[t.GetNetname()]+=1
for n in ["LED_B","LED_B_D","LED_G","LED_G_D"]:
    print("%-10s %8.3f mm  segs=%d"%(n,L.get(n,0)/1e6,N.get(n,0)))
