import pcbnew
MM=1000000.0
b=pcbnew.LoadBoard("tmp/fsin_sandbox/fsin_test.kicad_pcb")
A=(93.300,46.600); B=(93.500,49.600)
L_F=b.GetLayerID("F.Cu"); L_I4=b.GetLayerID("In4.Cu")
net=None
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetNetname()=="FSIN_OUT": net=p.GetNet(); break
    if net: break
print("net:",net.GetNetCode(),net.GetNetname())
def V(x,y): return pcbnew.VECTOR2I(int(round(x*MM)),int(round(y*MM)))
def seg(x1,y1,x2,y2,layer):
    t=pcbnew.PCB_TRACK(b)
    t.SetStart(V(x1,y1)); t.SetEnd(V(x2,y2))
    t.SetWidth(int(0.25*MM)); t.SetLayer(layer); t.SetNet(net)
    b.Add(t); print("  seg",(x1,y1),"->",(x2,y2),"layer",layer)
def via(x,y):
    v=pcbnew.PCB_VIA(b)
    v.SetPosition(V(x,y)); v.SetWidth(int(0.6*MM)); v.SetDrill(int(0.3*MM))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(L_F,L_I4); v.SetNet(net)
    b.Add(v); print("  via at",(x,y))
seg(*A,93.55,47.10,L_F); via(93.55,47.10)
seg(93.55,47.10,93.50,49.10,L_I4); via(93.50,49.10)
seg(93.50,49.10,*B,L_F)
b.Save("tmp/fsin_sandbox/fsin_test.kicad_pcb")
print("saved")
