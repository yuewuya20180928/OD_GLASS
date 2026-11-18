import importlib.util, os, math, json
spec = importlib.util.spec_from_file_location("cbf", "MECH/check_board_frame_coords.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
ROOT=os.getcwd()
b = m.read_board(ROOT); fps=b["fps"]; edge=b["edge"]
S6=m.S6; BASE=m.BASE; TOL=m.TOL; CRIT=m.CRIT; OPEN_X=m.OPEN_X; OPEN_Y=m.OPEN_Y
print("BASE jd_body_h",BASE["jd_body_h"],"CRIT",CRIT,"TOL",TOL,"OPEN",OPEN_X,OPEN_Y)
print("edge",edge)

som_pads=[]
for r in m.SOM_REFS:
    f=fps.get(r)
    if f: som_pads+=f["pads"]
ys=sorted(set(round(p["y"],4) for p in som_pads))
xs=sorted(set(round(p["x"],4) for p in som_pads))
print("SoM pad rows Y:",ys," n X cols:",len(xs))

def cent(ref):
    f=fps[ref]; ps=f["pads"]
    return sum(p["x"] for p in ps)/len(ps), sum(p["y"] for p in ps)/len(ps)
def copper(ref):
    return m.copper_bbox(fps[ref])

# ---- 座体高度参数式 ----
# OPEN_Y(h) = max(OPEN_Y_NOM, h + 2*(CRIT+TOL.fdm_part))
REQ=CRIT+TOL["fdm_part"]
print("\ncl_req per side = CRIT + fdm_part =",REQ, " => OPEN_Y_min(h) = h + 2*%.2f = h+%.2f"%(REQ,2*REQ))
print("h_max for fixed OPEN_Y=%.2f => h <= %.2f"%(OPEN_Y, OPEN_Y-2*REQ))
for h,label in ((0.90,"h_lo 保守下界(焊盘铜箔排高 0.90 实测)"),
                 (2.54,"h_cur 现值(BASE jd_body_h=2.54 假设)"),
                 (4.00,"h_hi 保守上界(板面 CONN F.Fab 座体高 4.00 实测)")):
    oy=max(OPEN_Y,h+2*REQ)
    print(f"  h={h:.2f} ({label}): OPEN_Y_min={h+2*REQ:.2f} -> OPEN_Y_eff={oy:.2f} (slack={oy-(h+2*REQ):.2f})")
    for ref,bw in (("J_DEBUG",None),("J_UART",2.54)):
        cx,cy=cent(ref)
        print(f"     {ref}: cy={cy:.3f} -> opening Y {cy-oy/2:.3f}..{cy+oy/2:.3f}")

# ---- 两条开口 (按 ISS-276 的 body_w 口径) ----
def opening(ref, body_w, h):
    cx,cy=cent(ref)
    bx0,bx1=cx-body_w/2, cx+body_w/2
    by0,by1=cy-h/2, cy+h/2
    cl_x=(OPEN_X-body_w)/2
    oy=max(OPEN_Y,h+2*REQ)
    cl_y=(oy-h)/2
    return dict(ref=ref,cx=cx,cy=cy,body_w=body_w,
                body=(bx0,bx1,by0,by1),
                open=(bx0-cl_x,bx1+cl_x,cy-oy/2,cy+oy/2),
                cl_x=cl_x,cl_y=cl_y,worst_cl_x=cl_x-TOL["fdm_part"],worst_cl_y=cl_y-TOL["fdm_part"])
jd_bw=copper("J_DEBUG")[1]-copper("J_DEBUG")[0]
print("\nJ_DEBUG body_w from copper =",jd_bw)
for h in (0.90,2.54,4.00):
    for ref,bw in (("J_DEBUG",jd_bw),("J_UART",2.54)):
        o=opening(ref,bw,h)
        r=o["open"]
        hits=m.rect_hits(r,som_pads)
        print(f"h={h:.2f} {ref}: open X {r[0]:.3f}..{r[1]:.3f} Y {r[2]:.3f}..{r[3]:.3f} "
              f"SoM_hits={hits} worst_cl_x={o['worst_cl_x']:.3f} worst_cl_y={o['worst_cl_y']:.3f} "
              f"in_frame={(r[0]>=edge['x0'] and r[1]<=edge['x1'] and r[2]>=edge['y0'] and r[3]<=edge['y1'])}")
        # containment of own pads
        cb=copper(ref)
        cont = (r[0]<=cb[0] and r[1]>=cb[1] and r[2]<=cb[2] and r[3]>=cb[3])
        other = "J_UART" if ref=="J_DEBUG" else "J_DEBUG"
        ob=copper(other)
        cross = not (r[1]<ob[0] or r[0]>ob[1] or r[3]<ob[2] or r[2]>ob[3])
        print(f"      contains_own_pads={cont}  overlaps_{other}_pads={cross}")
