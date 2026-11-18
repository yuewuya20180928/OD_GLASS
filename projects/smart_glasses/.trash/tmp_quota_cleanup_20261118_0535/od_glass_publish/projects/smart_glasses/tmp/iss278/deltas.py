import importlib.util, os, math, json
spec = importlib.util.spec_from_file_location("cbf", "MECH/check_board_frame_coords.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
b=m.read_board(os.getcwd()); fps=b["fps"]
P=json.load(open('HW/PCB/demo_mainboard_params.json'))
def at(ref):
    f=fps.get(ref); return f["at"] if f else None
def fab(ref):
    f=fps.get(ref); return m.fab_bbox(f) if f else None
def cop(ref):
    f=fps.get(ref); return m.copper_bbox(f) if f else None

pairs=[
 ("J_UART (检修口)", at("J_UART"), P["connectors"]["uart_position_mm"]),
 ("J_DEBUG (调试口)", at("J_DEBUG"), (P["connectors"]["jtag_position_mm"][0],P["connectors"]["jtag_position_mm"][1])),
 ("USB-C", at("J_USB_C"), tuple(P["connectors"]["usb_c_position_mm"])),
 ("CAM FPC", at("CONN_CAM"), tuple(P["fpc_camera"]["position_mm"])),
 ("DISP FPC", at("CONN_LIGHT"), tuple(P["fpc_display"]["position_mm"])),
]
print("=== params 声明坐标 vs 落表板实测 (帧 B160x100) ===")
for name, actual, decl in pairs:
    dx=actual[0]-decl[0]; dy=actual[1]-decl[1]
    print(f"  {name:20s} params {decl} vs 板 {actual} => dX {dx:+.3f}  dY {dy:+.3f}")
print()
print("=== 位号存在性 ===")
for p,real in [("J_UART","J_UART"),("J_JTAG","J_DEBUG"),("J_USB","J_USB_C"),("J_FPC_CAM","CONN_CAM"),("J_FPC_DISP","CONN_LIGHT"),("U_SOM_RK3572","J_SOM_P1..P4"),("LED_PWR","D_LED_G/D_LED_B/D_LED_R"),("LED_RUN","D_ESD_LIGHT")]:
    print(f"  params {p:14s} -> 板 {real:28s} | params 在板: {'YES' if p in fps else 'NO'}")
print()
print("=== 脚数/间距 ===")
for ref in ("J_DEBUG","J_UART"):
    f=fps[ref]; xs=sorted(p["x"] for p in f["pads"])
    pit=sorted(set(round(xs[i+1]-xs[i],4) for i in range(len(xs)-1)))
    print(f"  {ref}: 焊盘 {len(f['pads'])} 个, 间距 {pit}, 铜箔宽 {cop(ref)[1]-cop(ref)[0]:.3f}, fab {fab(ref)}")
print(f"  BOM 文本: J_DEBUG='1×4 1.27mm 排针 (JTAG)' / J_UART='1×2 1.27mm 排针 (UART)'")
print()
print("=== D_LED_G / R_LED_G ===")
for ref in ("D_LED_G","R_LED_G"):
    f=fps[ref]
    print(f"  {ref}: origin {f['at']} fab {fab(ref)} copper {tuple(round(v,3) for v in cop(ref))}")
    for p in f["pads"]: print("     pad",p["num"],round(p["x"],3),round(p["y"],3))
print()
print("=== 安装孔 ===")
print("  params 声明:",P["misc"]["mounting_holes"],"⌀",P["misc"]["mounting_hole_diameter_mm"])
print("  板实测: 0 个安装孔 (只有 J_USB_C 的 2 个 np_thru_hole 壳体柱)")
print()
print("=== 座体高 h 三档的判据余量 ===")
CRIT=m.CRIT; TOL=m.TOL; OY=m.OPEN_Y
for h in (0.90,2.54,4.00):
    oy=max(OY,h+2*(CRIT+TOL["fdm_part"]))
    print(f"  h={h:.2f}: 用 4.60 定档 最坏余量 = {(OY-h)/2-TOL['fdm_part']:.3f} ({'过' if (OY-h)/2-TOL['fdm_part']>=CRIT-1e-9 else '★红★'}) ; 需 OPEN_Y={oy:.2f} -> 最坏余量 {(oy-h)/2-TOL['fdm_part']:.3f}")
print()
print("=== SoM 承载区 (保守包络) ===")
print("  焊盘铜箔并集 X 15.100..68.900 × Y 7.610..54.390 ; 保守包络 X 13.650..70.350 × Y 7.610..54.390 ; 400 焊盘")
