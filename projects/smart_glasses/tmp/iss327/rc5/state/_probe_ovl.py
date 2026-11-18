import os, math, pcbnew
MM=1e6
PROJ=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
b=pcbnew.LoadBoard(os.path.join(PROJ,"HW","PCB","demo_mainboard.kicad_pcb"))
for want in ("C_HF_VDD_3V3_IO","C_AC_CSI_D0_D2_P","C_HF_LIGHT_3V3"):
    fp=b.FindFootprintByReference(want)
    if not fp: print(want,"NOT FOUND"); continue
    p=fp.GetPosition()
    print("%s fp@ (%.3f,%.3f) orient=%.1f"%(want,p.x/MM,p.y/MM,fp.GetOrientation().AsDegrees()))
    for pad in fp.Pads():
        r=pad.GetBoundingBox(); sz=pad.GetSize()
        print("   pad %-4s net=%-16s c=(%.3f,%.3f) size=%.3fx%.3f bbox=(%.3f,%.3f)-(%.3f,%.3f)"%(
            pad.GetNumber(),pad.GetNetname(),pad.GetPosition().x/MM,pad.GetPosition().y/MM,
            sz.x/MM,sz.y/MM,r.GetLeft()/MM,r.GetTop()/MM,r.GetRight()/MM,r.GetBottom()/MM))
