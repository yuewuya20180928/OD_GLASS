import importlib.util, os, math
spec = importlib.util.spec_from_file_location("cbf", "MECH/check_board_frame_coords.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
b=m.read_board(os.getcwd()); fps=b["fps"]
CRIT=m.CRIT; TOL=m.TOL; OPEN_X=m.OPEN_X; OPEN_Y=m.OPEN_Y
print("=== 验证: open_x = cx ± OPEN_X/2 (与 body_w 无关) ===")
for ref in ("J_DEBUG","J_UART"):
    f=fps[ref]; ps=f["pads"]
    cx=sum(p["x"] for p in ps)/len(ps); cy=sum(p["y"] for p in ps)/len(ps)
    print(f"  {ref}: cx={cx:.4f} -> open_x {cx-OPEN_X/2:.3f}..{cx+OPEN_X/2:.3f}   cy={cy:.4f}")
print("\n=== 验证: body_w <= OPEN_X - 2*(CRIT+TOL) 才可能过 ===")
lim=OPEN_X-2*(CRIT+TOL["fdm_part"])
print(f"  body_w 上限 = {lim:.2f} mm;  J_DEBUG 用铜箔宽 {m.copper_bbox(fps['J_DEBUG'])[1]-m.copper_bbox(fps['J_DEBUG'])[0]:.3f} -> 过")
print(f"  若 body_w = 板面 F.Fab 宽 6.00: cl_x=(10.20-6.00)/2={((OPEN_X-6.0)/2):.3f} worst={((OPEN_X-6.0)/2-TOL['fdm_part']):.3f} -> {'过' if ((OPEN_X-6.0)/2-TOL['fdm_part'])>=CRIT else '红'}")
print("\n=== 验证: ISS-276 已发布矩形 == 本单公式@h_cur=2.54 输出 ===")
for ref,bw in (("J_DEBUG",None),("J_UART",2.54)):
    f=fps[ref]; ps=f["pads"]
    cx=sum(p["x"] for p in ps)/len(ps); cy=sum(p["y"] for p in ps)/len(ps)
    eff=max(OPEN_Y, 2.54+2*(CRIT+TOL["fdm_part"]))
    print(f"  {ref}: 公式 -> X {cx-OPEN_X/2:.3f}..{cx+OPEN_X/2:.3f} Y {cy-eff/2:.3f}..{cy+eff/2:.3f}")
