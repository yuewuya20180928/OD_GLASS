import os, math, pcbnew
MM=1e6
PROJ=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
b=pcbnew.LoadBoard(os.path.join(PROJ,"HW","PCB","demo_mainboard.kicad_pcb"))
segs=[]
for d in b.GetDrawings():
    if d.GetLayerName()=="Edge.Cuts" and d.GetShape()==pcbnew.SHAPE_T_SEGMENT:
        segs.append((d.GetStart().x/MM,d.GetStart().y/MM,d.GetEnd().x/MM,d.GetEnd().y/MM))
def psd(px,py,ax,ay,bx,by):
    dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy
    if L2<1e-12: return math.hypot(px-ax,py-ay)
    t=max(0.0,min(1.0,((px-ax)*dx+(py-ay)*dy)/L2))
    return math.hypot(px-(ax+t*dx),py-(ay+t*dy))
near=[]
for fp in b.GetFootprints():
    for pad in fp.Pads():
        r=pad.GetBoundingBox()
        cx,cy=(r.GetLeft()+r.GetRight())/2/MM,(r.GetTop()+r.GetBottom())/2/MM
        dmin=min(psd(cx,cy,*s) for s in segs)
        # pad edge clearance: rect edge to board
        corners=[(r.GetLeft()/MM,r.GetTop()/MM),(r.GetRight()/MM,r.GetTop()/MM),
                 (r.GetLeft()/MM,r.GetBottom()/MM),(r.GetRight()/MM,r.GetBottom()/MM)]
        de=min(min(psd(px,py,*s) for s in segs) for (px,py) in corners)
        if de<0.75:
            near.append((de,fp.GetReference(),pad.GetNumber(),pad.GetNetname(),round(cx,3),round(cy,3)))
near.sort()
print("pads with pad-edge-to-board < 0.75mm:",len(near))
for n in near[:40]: print("  ",n)
