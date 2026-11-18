import importlib.util, os, math, json
spec = importlib.util.spec_from_file_location("cbf", "MECH/check_board_frame_coords.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
b=m.read_board(os.getcwd()); fps=b["fps"]; edge=b["edge"]
CRIT=m.CRIT; TOL=m.TOL; OPEN_X=m.OPEN_X; OPEN_Y=m.OPEN_Y
som=[]
for r in m.SOM_REFS:
    f=fps.get(r)
    if f: som+=f["pads"]
CLREQ=CRIT+TOL["fdm_part"]

def ctr(ref):
    ps=fps[ref]["pads"]
    return sum(p["x"] for p in ps)/len(ps), sum(p["y"] for p in ps)/len(ps)
def cb(ref): return m.copper_bbox(fps[ref])

print("=== 公式 ===")
print(f"CL_REQ = CRIT + TOL[fdm_part] = {CRIT} + {TOL['fdm_part']} = {CLREQ:.2f}")
print(f"OPEN_Y(h) = max({OPEN_Y:.2f}, h + 2*{CLREQ:.2f}) = max({OPEN_Y:.2f}, h+{2*CLREQ:.2f})")
print(f"临界 h* = {OPEN_Y:.2f} - {2*CLREQ:.2f} = {OPEN_Y-2*CLREQ:.2f}")
print(f"open_x = cx ± {OPEN_X/2:.2f}   (与 body_w 无关; body_w 上限 {OPEN_X-2*CLREQ:.2f})")
print()
for ref in ("J_DEBUG","J_UART"):
    cx,cy=ctr(ref); c=cb(ref)
    print(f"{ref}: cx={cx:.3f} cy={cy:.3f} 铜箔 X {c[0]:.3f}..{c[1]:.3f} Y {c[2]:.3f}..{c[3]:.3f} fab={m.fab_bbox(fps[ref])}")
print()
TIERS=[("h_lo",0.90,"座体Y不得小于自身焊盘排高(板面实测 0.900)"),
       ("h_cur",2.54,"现值 BASE['jd_body_h'] (Cortex-10 模型假设)"),
       ("h_hi",4.00,"板面自身 CONN 封装 F.Fab 座体高 (实测 4.00)")]
for h in (0.90,2.54,4.00):
    oy=max(OPEN_Y,h+2*CLREQ)
    print(f"h={h:.2f}: OPEN_Y={oy:.2f}  单边余量(名义)={oy/2-h/2:.3f}  最坏(扣 fdm 0.30)={oy/2-h/2-TOL['fdm_part']:.3f}  {'过' if oy/2-h/2-TOL['fdm_part']>=CRIT else '红'}")
print()
for h in (0.90,2.54,4.00):
    oy=max(OPEN_Y,h+2*CLREQ)
    for ref in ("J_DEBUG","J_UART"):
        cx,cy=ctr(ref)
        rect=(cx-OPEN_X/2,cx+OPEN_X/2,cy-oy/2,cy+oy/2)
        print(f"h={h:.2f} {ref}: X {rect[0]:.3f}..{rect[1]:.3f} Y {rect[2]:.3f}..{rect[3]:.3f} | SoM={m.rect_hits(rect,som)} | in_frame={rect[0]>=0 and rect[1]<=160 and rect[2]>=0 and rect[3]<=100}")
print()
# merged union
a=(142.95-5.10,142.95+5.10,56.6-2.30,56.6+2.30); c=(18.89-5.10,18.89+5.10,68.6-2.30,68.6+2.30)
u=(min(a[0],c[0]),max(a[1],c[1]),min(a[2],c[2]),max(a[3],c[3]))
print("合并并集 bbox:",tuple(round(v,3) for v in u),"SoM hits =",m.rect_hits(u,som))
print("合并宽 =",round(u[1]-u[0],3),"vs 开口 10.20 ⇒ 差",round(u[1]-u[0]-10.20,3))
print("必清空并集宽 =",round(143.8375-17.620,4),"vs 10.20 ⇒ 差",round(143.8375-17.620-10.20,4))
print()
# 1.27mm pitch 落位影响
for ref,n,cur_pitch in (("J_DEBUG",4,0.50),("J_UART",2,0.50)):
    span_cur=(n-1)*cur_pitch+0.275
    span_new=(n-1)*1.27+0.275
    print(f"{ref}: 若真实件 = 1×{n} @1.27mm ⇒ 铜箔宽 {span_new:.3f} (现落位 {span_cur:.3f}) ⇒ body_w 上限 {OPEN_X-2*CLREQ:.2f} ⇒ {'仍可用 10.20 开口' if span_new<=OPEN_X-2*CLREQ else '★超上限★'}")
print()
# LED
print("=== LED 两假设 ===")
print("整高自由带 X 1.550..3.450 宽 1.900 ; 次整高带 X 72.540..73.660 宽 1.120 ; 最近落位带 X 6.940..8.250 × Y 63.700..67.900")
print("最近落位带内 D_LED_G.1 → R_LED_G.2 最近 = 0.450 mm (净距0.00) ; 整高带内最近 = 4.800 mm")
print("LED_G_D 现状 93.492727 mm")
