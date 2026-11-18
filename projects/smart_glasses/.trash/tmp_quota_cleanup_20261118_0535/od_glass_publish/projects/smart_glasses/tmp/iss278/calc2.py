import importlib.util, os, math
spec = importlib.util.spec_from_file_location("cbf", "MECH/check_board_frame_coords.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
ROOT=os.getcwd(); b=m.read_board(ROOT); fps=b["fps"]; edge=b["edge"]
S6=m.S6; BASE=m.BASE; TOL=m.TOL; CRIT=m.CRIT; OPEN_X=m.OPEN_X; OPEN_Y=m.OPEN_Y
comp=m.compute(ROOT)
som_pads=[]
for r in m.SOM_REFS:
    f=fps.get(r)
    if f: som_pads+=f["pads"]

def cent(ref):
    f=fps[ref]; ps=f["pads"]
    return sum(p["x"] for p in ps)/len(ps), sum(p["y"] for p in ps)/len(ps)
def copper(ref): return m.copper_bbox(fps[ref])
REQ=CRIT+TOL["fdm_part"]
def opening(ref, body_w, h):
    cx,cy=cent(ref); bx0,bx1=cx-body_w/2,cx+body_w/2
    oy=max(OPEN_Y,h+2*REQ); cl_y=(oy-h)/2
    cl_x=(OPEN_X-body_w)/2
    return (bx0-cl_x,bx1+cl_x,cy-oy/2,cy+oy/2)

# full board collision (excluding the connector's own footprint)
def collide(rect, skip_refs):
    hits=[]
    for ref,f in fps.items():
        if ref in skip_refs: continue
        cb=m.copper_bbox(f)
        if not cb: continue
        if not (rect[1]<cb[0] or rect[0]>cb[1] or rect[3]<cb[2] or rect[2]>cb[3]):
            n=m.rect_hits(rect,f["pads"])
            hits.append((ref,n))
    return hits

jd_bw=copper("J_DEBUG")[1]-copper("J_DEBUG")[0]
print("=== 开口 vs 全板 (排除自身连接器) ===")
for h in (0.90,2.54,4.00):
    for ref,bw in (("J_DEBUG",jd_bw),("J_UART",2.54)):
        r=opening(ref,bw,h)
        print(f"h={h:.2f} {ref} open X {r[0]:.3f}..{r[1]:.3f} Y {r[2]:.3f}..{r[3]:.3f}")
        print("   SoM hits:",m.rect_hits(r,som_pads),"| other comps:",collide(r,{ref,"J_SOM_P1","J_SOM_P2","J_SOM_P3","J_SOM_P4"}))

print("\n=== LED: 整高自由带 (边缘带) 内离 R_LED_G.2 最近的落位 ===")
led=fps["D_LED_G"]; lb=m.copper_bbox(led); lox,loy=led["at"]
rel=(lb[0]-lox, lb[1]-lox, lb[2]-loy, lb[3]-loy)
rp={p["num"]:p for p in fps["R_LED_G"]["pads"]}; r2=rp["2"]
print("D_LED_G origin",led["at"],"rel bbox",tuple(round(v,3) for v in rel))
print("R_LED_G.2 at",(r2["x"],r2["y"]))
# edge band = 整高自由带 X 1.550..3.450 ; Y 全段
for band_name, bx0,bx1 in (("整高自由带 X 1.550..3.450",1.550,3.450),
                           ("次整高带 X 72.540..73.660",72.540,73.660),
                           ("最近落位带 X 6.940..8.250",6.940,8.250)):
    best=None
    # sample the band origin grid at 0.01 and compute dist R_LED_G.2 -> D_LED_G.1
    ox=bx0
    while ox<=bx1+1e-9:
        oy=1.450
        while oy<=98.950+1e-9:
            p1=(ox+rel[0], oy+rel[2])   # pad1 relative offset
            # actual pad1 offset: D_LED_G pad1 at origin+(-0.45,-0.20)
            d=math.hypot(p1[0]-r2["x"], p1[1]-r2["y"])
            if best is None or d<best[0]: best=(d,ox,oy)
            oy+=0.05
        ox+=0.01
    print(f"  {band_name}: 最近 D_LED_G.1 到 R_LED_G.2 距离 = {best[0]:.3f} mm @ origin ({best[1]:.3f},{best[2]:.3f})")

print("\n=== LED 现状 ===")
print("  LED_G_D 现状 93.492727 mm; 若搬到 R_LED_G 旁(最近落位带) => 0.450..0.965 mm")
