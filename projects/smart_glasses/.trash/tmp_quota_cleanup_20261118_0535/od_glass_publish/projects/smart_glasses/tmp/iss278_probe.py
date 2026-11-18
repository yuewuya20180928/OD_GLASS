import re, math, json, os
P="HW/PCB/demo_mainboard.kicad_pcb"
text=open(P,encoding="utf-8").read()
lines=text.split("\n")
PAD_RE = re.compile(r'\(pad\s+"([^"]*)"\s+(\S+)\s+(\S+)\s+\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)'
                     r'(?:\s*\(size ([-\d.]+) ([-\d.]+)\))?')
fps={}
i=0
while i < len(lines):
    if lines[i].lstrip().startswith("(footprint"):
        depth,j=0,i
        while j < len(lines):
            depth += lines[j].count("(")-lines[j].count(")")
            if depth==0 and j>i: break
            j+=1
        blk="\n".join(lines[i:j+1])
        m=re.search(r'\(property "Reference" "([^"]+)"',blk)
        if m:
            ref=m.group(1)
            at=re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)',blk)
            ox=float(at.group(1)) if at else 0.0
            oy=float(at.group(2)) if at else 0.0
            pads=[]
            for pm in PAD_RE.finditer(blk):
                num,pt,shape,px,py,_r,sx,sy=pm.groups()
                pads.append(dict(num=num,x=ox+float(px),y=oy+float(py),
                                 sx=float(sx) if sx else 0.0, sy=float(sy) if sy else 0.0))
            fps[ref]=dict(at=(ox,oy),pads=pads)
        i=j+1
    else: i+=1
out={}
for ref in ("J_DEBUG","J_UART","D_LED_G","R_LED_G","J_USB_C","J_BOOT1","J_CHG","SW_RST","U_SOM_RK3572"):
    f=fps.get(ref)
    if not f: out[ref]=None; continue
    out[ref]=dict(at=f["at"],npads=len(f["pads"]),
        pads=[(p["num"],round(p["x"],4),round(p["y"],4),p["sx"],p["sy"]) for p in f["pads"]],
        rel=[(p["num"],round(p["x"]-f["at"][0],4),round(p["y"]-f["at"][1],4)) for p in f["pads"]])
print(json.dumps(out,ensure_ascii=False,indent=1))
# mounting holes / other footprints
mh=[r for r in fps if r.startswith("MH") or r.startswith("Mount") or r.startswith("H_")]
print("MH-ish:",mh)
print("total footprints:",len(fps))
print("all refs:",sorted(fps.keys()))
