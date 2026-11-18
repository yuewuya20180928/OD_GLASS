#!/usr/bin/env python3
# ISS-307 · 落位可行性网格扫描 (★只读板, 零写盘★)
# 用法: bash state/pcbnew_py.sh logs/iss307/probe_feasible.py
import math
import pcbnew

BOARD = "HW/PCB/demo_mainboard.kicad_pcb"
b = pcbnew.LoadBoard(BOARD)
MM = 1000000.0
mm = lambda v: v / MM

JX, JY = 140.00, 5.25          # J_USB_C 封装原点 [实测]
R_MAX = 3.00                  # R9 阈值 (ESD_MAX_DIST_MM) [实测 check_netlist_selfconsistency.py L128]
CRTYD_GAP = 0.05              # 余量: 与 J_USB_C courtyard 至少留 0.05mm
CU_CLEAR = 0.25               # 铜间距 (项目 min_clearance 0.0, 取 0.25 保守)
EDGE_CU = 0.50                # copper_edge_clearance (项目规则 0.5) [实测 .kicad_pro]

# ── J_USB_C 的 courtyard (实测自板文件) ──
JC_CR = (135.16, -0.53, 144.84, 6.92)

def rect_of(fp, layer):
    xs, ys = [], []
    for it in fp.GraphicalItems():
        if it.GetLayer() != layer:
            continue
        try:
            bb = it.GetBoundingBox()
        except Exception:
            continue
        xs += [mm(bb.GetLeft()), mm(bb.GetRight())]
        ys += [mm(bb.GetTop()), mm(bb.GetBottom())]
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))

# ── 板上所有焊盘 (绝对矩形) 与所有走线段 ──
PADS = []
for fp in b.GetFootprints():
    for p in fp.Pads():
        pos = p.GetPosition(); sz = p.GetSize()
        PADS.append((fp.GetReference(), p.GetNumber(), p.GetNetname(),
                     mm(pos.x) - mm(sz.x) / 2, mm(pos.y) - mm(sz.y) / 2,
                     mm(pos.x) + mm(sz.x) / 2, mm(pos.y) + mm(sz.y) / 2))
SEGS = []
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        p = t.GetPosition()
        SEGS.append((t.GetNetname(), mm(p.x), mm(p.y), mm(p.x), mm(p.y)))
        continue
    s, e = t.GetStart(), t.GetEnd()
    SEGS.append((t.GetNetname(), mm(s.x), mm(s.y), mm(e.x), mm(e.y)))

def seg_rect_dist(x1, y1, x2, y2, rx1, ry1, rx2, ry2):
    """点到线段的最短距离 (线段在矩形内部时算 0) —— 用采样 + 端点到矩形距离近似."""
    # 端点到矩形距离
    def pt_rect(px, py):
        dx = max(rx1 - px, 0, px - rx2)
        dy = max(ry1 - py, 0, py - ry2)
        return math.hypot(dx, dy)
    d = min(pt_rect(x1, y1), pt_rect(x2, y2))
    if rx1 <= x1 <= rx2 and ry1 <= y1 <= ry2:
        return 0.0
    return d

def rect_overlap(a, c, gap=0.0):
    return not (a[2] + gap <= c[0] or c[2] + gap <= a[0] or a[3] + gap <= c[1] or c[3] + gap <= a[1])

# ── 候选封装模板 (★courtyard = 器件本体 + 0.25mm/边 [推算, IPC 名义值]★) ──
TPL = {
 "TPD2EUSB30DRTR (DRT/SOT-3, 本体 1.00x0.80)": dict(body=(1.00, 0.80), cr=(1.50, 1.30)),
 "TPD2E2U06DCKR  (SC70-3/DCK, 本体 2.00x1.25)": dict(body=(2.00, 1.25), cr=(2.50, 1.75)),
 "ESD752DCKR    (SC70-3/DCK, 本体 2.00x1.25)": dict(body=(2.00, 1.25), cr=(2.50, 1.75)),
 "ESD752DBZR    (SOT-23-3/DBZ, 本体 2.92x1.30)": dict(body=(2.92, 1.30), cr=(3.42, 1.80)),
 "ESD752DXAR    (DFN1110-3/DXA, 本体 1.10x1.00)": dict(body=(1.10, 1.00), cr=(1.60, 1.50)),
 "CM1218-03     (SC70-3, 本体 2.00x1.25)": dict(body=(2.00, 1.25), cr=(2.50, 1.75)),
 "★反向用例 USBLC6-2SC6 (SOT-23-6, 本体 2.90x1.60)": dict(body=(2.90, 1.60), cr=(3.40, 2.10)),
}

def scan(cr_w, cr_h, step=0.05):
    """在 R9 圆内扫描可行原点。返回 (可行点数, 可行区 bbox, 最优点)"""
    ok = []
    half_w, half_h = cr_w / 2, cr_h / 2
    n = int(R_MAX / step) + 2
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x0 = JX + i * step
            y0 = JY + j * step
            d = math.hypot(x0 - JX, y0 - JY)
            if d > R_MAX:
                continue
            r = (x0 - half_w, y0 - half_h, x0 + half_w, y0 + half_h)
            # ① courtyard 不与 J_USB_C 的 courtyard 重叠
            if rect_overlap(r, JC_CR, CRTYD_GAP):
                continue
            # ② 与板上其它封装 courtyard 不重叠
            bad = False
            for fp in b.GetFootprints():
                if fp.GetReference() == "J_USB_C":
                    continue
                c2 = rect_of(fp, pcbnew.F_CrtYd)
                if c2 and rect_overlap(r, c2, CRTYD_GAP):
                    bad = True
                    break
            if bad:
                continue
            # ③ 与所有焊盘 (含 0.25 铜间距) 不重叠
            for (ref, num, net, x1, y1, x2, y2) in PADS:
                if rect_overlap(r, (x1 - CU_CLEAR, y1 - CU_CLEAR, x2 + CU_CLEAR, y2 + CU_CLEAR)):
                    bad = True
                    break
            if bad:
                continue
            # ④ 与所有走线/过孔 (含 0.25 铜间距) 不碰
            for (net, x1, y1, x2, y2) in SEGS:
                if seg_rect_dist(x1, y1, x2, y2, r[0] - CU_CLEAR, r[1] - CU_CLEAR, r[2] + CU_CLEAR, r[3] + CU_CLEAR) < CU_CLEAR:
                    bad = True
                    break
            if bad:
                continue
            # ⑤ 铜到板边 ≥ 0.5mm (courtyard 内缩到本体近似)
            if r[0] < EDGE_CU or r[1] < EDGE_CU or r[2] > 160 - EDGE_CU or r[3] > 100 - EDGE_CU:
                continue
            ok.append((x0, y0, d))
    return ok

print("=" * 96)
print("[判据口径] R9 = 封装原点距 (★不是焊盘中心距★) ⇒ _board_ref_xy() 取 footprint 的 (at x y) 原点")
print(f"           J_USB_C 原点 = ({JX}, {JY}) ; R9 阈值 = {R_MAX} mm ; J_USB_C courtyard = {JC_CR}")
print("=" * 96)
for name, t in TPL.items():
    cw, ch = t["cr"]
    ok = scan(cw, ch)
    if not ok:
        print(f"\n★ {name}")
        print(f"   courtyard = {cw:.2f} x {ch:.2f} mm  ⇒ ★★【放不下】★★ (可行原点数 = 0)")
        # 给出临界高度
        continue
    xs = [p[0] for p in ok]; ys = [p[1] for p in ok]; ds = [p[2] for p in ok]
    best = min(ok, key=lambda p: p[2])
    print(f"\n✔ {name}")
    print(f"   本体 {t['body'][0]:.2f} x {t['body'][1]:.2f} ; courtyard = {cw:.2f} x {ch:.2f} mm")
    print(f"   可行原点数 = {len(ok)}  (步长 0.05mm)")
    print(f"   可行区 bbox : x {min(xs):.2f}..{max(xs):.2f} , y {min(ys):.2f}..{max(ys):.2f}"
          f"   (Δx {max(xs)-min(xs):.2f} , Δy {max(ys)-min(ys):.2f})")
    print(f"   距接口最近可行点 = ({best[0]:.2f}, {best[1]:.2f}) , 距 J_USB_C {best[2]:.3f} mm")
    # x=140 正下方一行
    row = [p for p in ok if abs(p[0] - JX) <= 0.026]
    if row:
        row.sort(key=lambda p: p[1])
        print(f"   x=140.00 那一行的可行 y = {row[0][1]:.2f} .. {row[-1][1]:.2f} "
              f"(距接口 {row[0][2]:.3f} .. {row[-1][2]:.3f} mm)")

print("=" * 96)
print("[临界高度] courtyard 高 hc 的上限 (y0 >= 6.92+hc/2 且 y0 <= 5.25+3.0)")
for hc in (1.30, 1.50, 1.75, 1.80, 2.10, 2.50, 2.66, 2.80):
    y0 = 6.92 + hc / 2
    d = y0 - JY
    print(f"   hc = {hc:.2f} mm ⇒ y0 >= {y0:.3f} , 到 J_USB_C 垂直距 {d:.3f} mm ⇒ {'可行' if d <= R_MAX else '★不可行★'}"
          f" (3.0-该距 = {R_MAX-d:+.3f})")

print("=" * 96)
print("[ISS-306 给的 (137.18, 6.28) 复核]")
d = math.hypot(JX - 137.18, JY - 6.28)
print(f"   hypot = {d:.6f} mm ⇒ ≤3.0 ? {d <= R_MAX}  (★超 {d-R_MAX:.4f} mm★)")
r = (137.18 - 1.25, 6.28 - 0.875, 137.18 + 1.25, 6.28 + 0.875)
print(f"   其 courtyard(SC70-3) = {r} ⇒ 与 J_USB_C courtyard {JC_CR} 重叠 ? {rect_overlap(r, JC_CR)}")

print("=" * 96)
print("[铜箔分布] J_USB_C 12mm 内各网的走线/过孔数量")
cnt = {}
for (net, x1, y1, x2, y2) in SEGS:
    if math.hypot(x1 - JX, y1 - JY) <= 12 or math.hypot(x2 - JX, y2 - JY) <= 12:
        cnt[net] = cnt.get(net, 0) + 1
for k, v in sorted(cnt.items(), key=lambda kv: -kv[1]):
    print(f"   {k!r:26s} {v} 段")
print("[D+/D− 网] NET_USB_D_P_TYPEC / NET_USB_D_N_TYPEC 在 J_USB_C 附近的走线:")
for (net, x1, y1, x2, y2) in SEGS:
    if "USB_D" in net and (math.hypot(x1 - JX, y1 - JY) <= 14 or math.hypot(x2 - JX, y2 - JY) <= 14):
        print(f"   {net!r:24s} ({x1:.2f},{y1:.2f}) -> ({x2:.2f},{y2:.2f})")
