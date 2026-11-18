#!/usr/bin/env python3
# ISS-307 · 落位可行性探针 (★只读板, 零写盘★)
# 用法: bash state/pcbnew_py.sh logs/iss307/probe_placement.py
import math, sys
import pcbnew

BOARD = "HW/PCB/demo_mainboard.kicad_pcb"
b = pcbnew.LoadBoard(BOARD)
MM = 1000000.0

def mm(v):  # pcbnew internal unit -> mm
    return v / MM

def fp_bbox(fp, layer):
    """返回 fp 在指定层上所有 fp_line/fp_rect/fp_poly 的绝对 bbox (mm)。"""
    xs, ys = [], []
    for it in fp.GraphicalItems():
        if it.GetClass() not in ("MGRAPHIC", "PCB_SHAPE"):
            continue
        if it.GetLayer() != layer:
            continue
        try:
            bb = it.GetBoundingBox()
        except Exception:
            continue
        if bb.GetWidth() == 0 and bb.GetHeight() == 0:
            continue
        xs += [mm(bb.GetLeft()), mm(bb.GetRight())]
        ys += [mm(bb.GetTop()), mm(bb.GetBottom())]
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))

def pads_abs(fp):
    out = []
    for p in fp.Pads():
        pos = p.GetPosition()
        sz = p.GetSize()
        out.append({
            "num": p.GetNumber(),
            "net": p.GetNetname(),
            "x": mm(pos.x), "y": mm(pos.y),
            "w": mm(sz.x), "h": mm(sz.y),
            "shape": p.GetShape(),
            "type": p.GetAttribute(),
        })
    return out

def all_fp():
    out = {}
    for fp in b.GetFootprints():
        out[fp.GetReference()] = fp
    return out

fps = all_fp()
print("=" * 90)
print("[探针 1] 板面概况")
bb = b.GetBoardEdgesBoundingBox()
print(f"  Edge.Cuts bbox (mm) = x {mm(bb.GetLeft()):.2f}..{mm(bb.GetRight()):.2f} , y {mm(bb.GetTop()):.2f}..{mm(bb.GetBottom()):.2f}")
print(f"  封装总数 = {len(fps)}")

print("=" * 90)
print("[探针 2] 每个封装的 courtyard / fab 存在情况 (统计)")
has_crtyd = []
for ref, fp in sorted(fps.items()):
    cr = fp_bbox(fp, pcbnew.F_CrtYd)
    fb = fp_bbox(fp, pcbnew.F_Fab)
    if cr:
        has_crtyd.append(ref)
print(f"  有 F.CrtYd (courtyard) 的封装 = {len(has_crtyd)} 个: {has_crtyd}")
nofab = [r for r, f in fps.items() if not fp_bbox(f, pcbnew.F_Fab)]
print(f"  无 F.Fab 的封装 = {len(nofab)} 个: {nofab[:10]}")

print("=" * 90)
print("[探针 3] J_USB_C 与 D_ESD_USB_D 实测")
for ref in ("J_USB_C", "D_ESD_USB_D"):
    fp = fps[ref]
    pos = fp.GetPosition()
    print(f"  {ref}: 原点 = ({mm(pos.x):.2f}, {mm(pos.y):.2f}) mm, 焊盘数 = {len(fp.Pads())}")
    cr = fp_bbox(fp, pcbnew.F_CrtYd)
    fb = fp_bbox(fp, pcbnew.F_Fab)
    if cr: print(f"      courtyard bbox = x {cr[0]:.2f}..{cr[2]:.2f} , y {cr[1]:.2f}..{cr[3]:.2f}  (W {cr[2]-cr[0]:.2f} x H {cr[3]-cr[1]:.2f})")
    if fb: print(f"      F.Fab bbox     = x {fb[0]:.2f}..{fb[2]:.2f} , y {fb[1]:.2f}..{fb[3]:.2f}  (W {fb[2]-fb[0]:.2f} x H {fb[3]-fb[1]:.2f})")
    for p in pads_abs(fp):
        print(f"      pad {p['num']!r:6s} net={p['net']!r:24s} abs=({p['x']:.3f},{p['y']:.3f}) size=({p['w']:.3f},{p['h']:.3f}) type={p['type']}")

print("=" * 90)
print("[探针 4] J_USB_C 原点 8 mm / 12 mm 半径内的其他封装")
for R in (8.0, 12.0):
    near = []
    jx, jy = mm(fps["J_USB_C"].GetPosition().x), mm(fps["J_USB_C"].GetPosition().y)
    for ref, fp in fps.items():
        if ref == "J_USB_C":
            continue
        p = fp.GetPosition()
        d = math.hypot(mm(p.x) - jx, mm(p.y) - jy)
        if d <= R:
            near.append((round(d, 2), ref, round(mm(p.x), 2), round(mm(p.y), 2)))
    near.sort()
    print(f"  ≤ {R} mm: {near}")

print("=" * 90)
print("[探针 5] J_USB_C 附近的铜箔 (track / via / pad)")
jx, jy = 140.0, 5.25
trk = []
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        p = t.GetPosition()
        d = math.hypot(mm(p.x) - jx, mm(p.y) - jy)
        if d <= 12:
            trk.append(("VIA", round(d, 2), round(mm(p.x), 2), round(mm(p.y), 2), t.GetNetname()))
        continue
    s, e = t.GetStart(), t.GetEnd()
    for pt in (s, e):
        d = math.hypot(mm(pt.x) - jx, mm(pt.y) - jy)
        if d <= 12:
            trk.append((t.GetNetname(), round(d, 2), round(mm(s.x), 2), round(mm(s.y), 2),
                        round(mm(e.x), 2), round(mm(e.y), 2), mm(t.GetWidth())))
            break
print(f"  ≤12 mm 内的 track/via 段 = {len(trk)}")
for t in trk[:40]:
    print("   ", t)
