#!/usr/bin/env python3
# ISS-307 · 落位可行性 (★只读板, 零写盘★) —— DRC 语义修正版
#   courtyard 只跟 courtyard 判重叠 (KiCad rule: courtyards_overlap)
#   铜间距只判 焊盘 vs 铜 ; 走线可以从器件下方穿过 (★不拿 courtyard 去卡走线★)
# 用法: bash state/pcbnew_py.sh logs/iss307/probe_feasible2.py
import math
import pcbnew

b = pcbnew.LoadBoard("HW/PCB/demo_mainboard.kicad_pcb")
mm = lambda v: v / 1000000.0
JX, JY = 140.00, 5.25
R_MAX = 3.00
JC_CR = (135.16, -0.53, 144.84, 6.92)      # J_USB_C courtyard [实测]
GAP = 0.05                                   # 与 J_USB_C courtyard 的余量
EDGE_CU = 0.50                               # copper_edge_clearance [实测 .kicad_pro]

def rect_of(fp, layer):
    xs, ys = [], []
    for it in fp.GraphicalItems():
        if it.GetLayer() != layer:
            continue
        bb = it.GetBoundingBox()
        xs += [mm(bb.GetLeft()), mm(bb.GetRight())]
        ys += [mm(bb.GetTop()), mm(bb.GetBottom())]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None

CRS = {fp.GetReference(): rect_of(fp, pcbnew.F_CrtYd) for fp in b.GetFootprints()}
CRS = {k: v for k, v in CRS.items() if v}
PADS = []
for fp in b.GetFootprints():
    for p in fp.Pads():
        pos, sz = p.GetPosition(), p.GetSize()
        PADS.append((fp.GetReference(), p.GetNumber(), p.GetNetname(),
                     mm(pos.x) - mm(sz.x) / 2, mm(pos.y) - mm(sz.y) / 2,
                     mm(pos.x) + mm(sz.x) / 2, mm(pos.y) + mm(sz.y) / 2))
SEGS = []
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        p = t.GetPosition()
        SEGS.append(("VIA:" + t.GetNetname(), mm(p.x), mm(p.y), mm(p.x), mm(p.y)))
        continue
    s, e = t.GetStart(), t.GetEnd()
    SEGS.append((t.GetNetname(), mm(s.x), mm(s.y), mm(e.x), mm(e.y)))

def ov(a, c, gap=0.0):
    return not (a[2] + gap <= c[0] or c[2] + gap <= a[0] or a[3] + gap <= c[1] or c[3] + gap <= a[1])

def pt_rect(px, py, r):
    dx = max(r[0] - px, 0, px - r[2]); dy = max(r[1] - py, 0, py - r[3])
    return math.hypot(dx, dy)

def seg_dist(x1, y1, x2, y2, r):
    if (r[0] <= x1 <= r[2] and r[1] <= y1 <= r[3]) or (r[0] <= x2 <= r[2] and r[1] <= y2 <= r[3]):
        return 0.0
    return min(pt_rect(x1, y1, r), pt_rect(x2, y2, r))

TPL = {
 "TPD2EUSB30DRTR  DRT/SOT-3  本体1.00x0.80": (1.50, 1.30),
 "TPD2E2U06DCKR   SC70-3/DCK 本体2.00x1.25": (2.50, 1.75),
 "ESD752DCKR      SC70-3/DCK 本体2.00x1.25": (2.50, 1.75),
 "ESD752DBZR      SOT-23-3   本体2.92x1.30": (3.42, 1.80),
 "ESD752DXAR      DFN1110-3  本体1.10x1.00": (1.60, 1.50),
 "CM1218-03       SC70-3     本体2.00x1.25": (2.50, 1.75),
 "★反向用例A USBLC6-2SC6 SOT-23-6 2.90x1.60": (3.40, 2.10),
 "★反向用例B D_SMB (DO-214AA) 本体5.59x3.42": (6.09, 3.92),
}

def scan(cw, ch, step=0.05, check_copper=False):
    ok = []
    hw, hh = cw / 2, ch / 2
    n = int(R_MAX / step) + 2
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x0, y0 = JX + i * step, JY + j * step
            if math.hypot(x0 - JX, y0 - JY) > R_MAX:
                continue
            r = (x0 - hw, y0 - hh, x0 + hw, y0 + hh)
            if ov(r, JC_CR, GAP):
                continue
            bad = False
            for ref, c2 in CRS.items():
                if ref == "J_USB_C":
                    continue
                if ov(r, c2, GAP):
                    bad = True; break
            if bad:
                continue
            if r[0] < EDGE_CU or r[1] < EDGE_CU or r[2] > 160 - EDGE_CU or r[3] > 100 - EDGE_CU:
                continue
            ok.append((x0, y0, math.hypot(x0 - JX, y0 - JY)))
    return ok

def copper_in(r, clearance=0.25):
    """窗口内会被器件焊盘区占住的既有铜 (按网统计) —— 只算『落进窗口内』的, 不含 clearance 外扩"""
    hit = {}
    for (ref, num, net, x1, y1, x2, y2) in PADS:
        if ov(r, (x1, y1, x2, y2)):
            hit.setdefault(net, []).append(f"pad {ref}.{num}")
    for (net, x1, y1, x2, y2) in SEGS:
        if seg_dist(x1, y1, x2, y2, r) <= clearance:
            hit.setdefault(net, []).append(f"track ({x1:.2f},{y1:.2f})->({x2:.2f},{y2:.2f})")
    return hit

print("=" * 100)
print("[判据口径] R9 = ★封装原点距★ (不是焊盘中心距): _board_ref_xy() 取 footprint 的 (at x y) [实测 L1218-1237]")
print(f"          J_USB_C 原点 ({JX}, {JY}) · R9 阈值 {R_MAX} mm · J_USB_C courtyard {JC_CR} [实测]")
print(f"          板面 Edge.Cuts = x 0..160, y 0..100 · copper_edge_clearance {EDGE_CU} mm [实测 .kicad_pro]")
print("=" * 100)
for name, (cw, ch) in TPL.items():
    ok = scan(cw, ch)
    if not ok:
        print(f"\n★★ {name}  courtyard {cw:.2f}x{ch:.2f} ⇒ 【放不下】(可行原点数 0)")
        continue
    xs = [p[0] for p in ok]; ys = [p[1] for p in ok]
    best = min(ok, key=lambda p: p[2])
    print(f"\n✔ {name}  courtyard {cw:.2f}x{ch:.2f}")
    print(f"   可行原点 {len(ok)} 个 · 区域 x {min(xs):.2f}..{max(xs):.2f} , y {min(ys):.2f}..{max(ys):.2f}"
          f" (Δx {max(xs)-min(xs):.2f} / Δy {max(ys)-min(ys):.2f})")
    print(f"   最近可行点 ({best[0]:.2f}, {best[1]:.2f}) 距接口 {best[2]:.3f} mm")
    row = sorted([p for p in ok if abs(p[0] - JX) <= 0.026], key=lambda p: p[1])
    if row:
        print(f"   x=140.00 整列可行 y = {row[0][1]:.2f}..{row[-1][1]:.2f} (距接口 {row[0][2]:.3f}..{row[-1][2]:.3f})")
    # 取 x=140 上离接口最近的一点, 看窗口内既有铜
    if row:
        p0 = row[0]
        r = (p0[0] - cw / 2, p0[1] - ch / 2, p0[0] + cw / 2, p0[1] + ch / 2)
        hit = copper_in(r)
        print(f"   推荐点 ({p0[0]:.2f},{p0[1]:.2f}) 窗口内既有铜 (按网):")
        if not hit:
            print("      (无)")
        for k, v in sorted(hit.items()):
            print(f"      {k!r:26s} {len(v)} 项  e.g. {v[0]}")

print("=" * 100)
print("[窗口外的既有铜 —— 3.0 mm 圆内到底有什么]")
circ = (JX - R_MAX, JY - R_MAX, JX + R_MAX, JY + R_MAX)
hit = copper_in(circ, clearance=0.0)
for k, v in sorted(hit.items(), key=lambda kv: -len(kv[1])):
    print(f"   {k!r:26s} {len(v)} 项   e.g. {v[0]} | {v[1] if len(v)>1 else ''}")
print("   ── 焊盘 (J_USB_C 自己的 18 个) ──")
for (ref, num, net, x1, y1, x2, y2) in PADS:
    if ref == "J_USB_C":
        print(f"      pad {num!r:6s} {net!r:22s} ({x1:.2f},{y1:.2f})..({x2:.2f},{y2:.2f})")

print("=" * 100)
print("[反向用例 ③] 距离 >3.0 mm 必须被否 / ≤3.0 mm 作正向对照")
for p in [(137.18, 6.28), (137.18, 6.60), (140.00, 7.80), (140.00, 7.55), (140.00, 8.30)]:
    d = math.hypot(JX - p[0], JY - p[1])
    print(f"   ({p[0]:7.2f},{p[1]:5.2f}) → {d:.4f} mm  {'PASS ≤3.0' if d <= R_MAX else '★FAIL >3.0★'}")
