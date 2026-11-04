import os, math, pcbnew
MM=1e6
PROJ=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
b=pcbnew.LoadBoard(os.path.join(PROJ,"HW","PCB","demo_mainboard.kicad_pcb"))
TX,TY=86.70,26.45
print("=== pads within 1.5mm of (%.2f,%.2f) ==="%(TX,TY))
for fp in b.GetFootprints():
    for pad in fp.Pads():
        x,y=pad.GetPosition().x/MM,pad.GetPosition().y/MM
        if math.hypot(x-TX,y-TY)<1.5:
            r=pad.GetBoundingBox()
            print("  %-14s.%-4s net=%-18s c=(%.3f,%.3f) rect=(%.3f,%.3f)-(%.3f,%.3f)"%(
                fp.GetReference(),pad.GetNumber(),pad.GetNetname(),x,y,
                r.GetLeft()/MM,r.GetTop()/MM,r.GetRight()/MM,r.GetBottom()/MM))
print("=== tracks within 1.5mm ===")
for t in b.GetTracks():
    if t.GetClass()!="PCB_TRACK": continue
    x1,y1,x2,y2=t.GetStart().x/MM,t.GetStart().y/MM,t.GetEnd().x/MM,t.GetEnd().y/MM
    if min(math.hypot(x1-TX,y1-TY),math.hypot(x2-TX,y2-TY))<1.5:
        print("  %-18s (%.3f,%.3f)->(%.3f,%.3f) w=%.2f %s"%(t.GetNetname(),x1,y1,x2,y2,t.GetWidth()/MM,t.GetLayerName()))
print("=== vias within 1.5mm ===")
for t in b.GetTracks():
    if t.GetClass()!="PCB_VIA": continue
    x,y=t.GetPosition().x/MM,t.GetPosition().y/MM
    if math.hypot(x-TX,y-TY)<1.5:
        print("  %-18s @(%.3f,%.3f) %s"%(t.GetNetname(),x,y,t.GetLayerName()))
