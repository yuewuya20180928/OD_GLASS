#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_pcb_netlist_board.py —— 用 pcbnew 从零生成 demo 主板 (网表驱动的真板子)

产出: HW/PCB/demo_mainboard.kicad_pcb
  ★**板上的每一个器件都来自网表** ⇒ ★**每个焊盘都带真实网络** ⇒ ⇒
  ★**可以用 pcbnew 机器验证 "板子 ↔ 网表" 100% 一致** (state/check_pcb_nets.py)
  ★**可以用 KiCad DRC 验几何** (state/check_pcb_drc.py)
  ★⇒ ★**"自己画图" 的验收标准不是"画得像", 而是"板子与网表逐点等价 + DRC 干净"**。

布局 (草案, 等 ISS-158 三件规格回填后重跑):
  · 板 145×100mm (结构不做 ⇒ 尺寸优先满足布线)
  · 左侧 = RK3572 核心板 FET3572-C 承载区 (68×50mm) + 它的 4×100pin/0.4mm BTB 座
  · 右侧 = 网表器件网格 (真实 0603/SOIC 尺寸 ⇒ 间距有意义, DRC 才有价值)
  · 板边 = camera FPC 座 (31p/0.3mm) · display FPC 座 (40p/0.5mm) · USB-C · UART/JTAG · 按键/LED · 4 个安装孔
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
import pcbnew  # noqa: E402

NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
REPORT = os.path.join(PROJ, "HW", "PCB", "PCB_NETLIST_FILL.txt")

BOARD_W, BOARD_H = 145.0, 100.0
GRID_X0, GRID_Y0 = 76.0, 8.0
GRID_PITCH_X, GRID_PITCH_Y = 4.2, 4.2
GRID_COLS = 16
SOM_AREA = (8.0, 6.0, 68.0, 50.0)   # SOM 承载区 x,y,w,h
MM = 1e6


def V(x, y):
    return pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM)))


def load_rows():
    with open(NETLIST, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def group_refs(rows):
    per_ref, seen = {}, {}
    for r in rows:
        ref = (r.get("ref") or "").strip()
        net = (r.get("net") or "").strip()
        if not ref or not net:
            continue
        key = (ref, net)
        idx = seen.get(key, 0)
        seen[key] = idx + 1
        per_ref.setdefault(ref, []).append((net, f"P{idx+1}", (r.get("value") or "")[:40]))
    return per_ref


def kind_of(ref):
    R = ref.upper()
    for k, pref in (("R", ("R_", "RN_")), ("C", ("C_", "CN_")), ("FB", ("FB_", "L_")),
                     ("D", ("D_", "TVS")), ("IC", ("U_", "IC_", "Q_")),
                     ("CONN", ("J_", "CONN_")), ("SW", ("SW_", "BT_")),
                     ("LED", ("LED_",)), ("TP", ("TP_",))):
        if R.startswith(pref):
            return k
    return "IC"


def size_of(kind, npins):
    """(w, h, 每侧脚数, 脚距)"""
    if kind in ("R", "C", "LED"):
        return 1.8, 1.0, 1, 1.6
    if kind == "D":
        return 2.7, 1.6, 1, 2.3
    if kind == "FB":
        return 2.0, 1.2, 2, 1.0
    if kind == "SW":
        return 3.0, 3.0, 1, 2.2
    if kind == "TP":
        return 1.4, 1.4, 1, 0.0
    if kind == "CONN":
        return max(6.0, (npins - 1) * 0.5 + 2.6), 4.0, npins, 0.5
    per = max(1, (npins + 1) // 2)
    return max(4.0, (per - 1) * 1.27 + 2.4), 5.0, per, 1.27


def add_outline(board):
    w, h = BOARD_W, BOARD_H
    pts = [(0, 0), (w, 0), (w, h), (0, h), (0, 0)]
    for i in range(len(pts) - 1):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetStart(V(*pts[i]))
        seg.SetEnd(V(*pts[i + 1]))
        seg.SetWidth(int(0.1 * MM))
        board.Add(seg)


def make_footprint(board, ref, value, kind, pins, netmap, x, y, label=True):
    w, h, per_side, pitch = size_of(kind, len(pins))
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetValue(value)
    # ★位号/值文字放 F.Fab 并隐藏 ⇒ 丝印层只留人工加的装配标识 ⇒ 消除 silk_overlap
    try:
        fp.Reference().SetLayer(pcbnew.F_Fab)
        fp.Reference().SetVisible(False)
        fp.Value().SetLayer(pcbnew.F_Fab)
        fp.Value().SetVisible(False)
    except Exception:
        pass
    # 本体矩形 (Edge.Cuts)
    r = pcbnew.PCB_SHAPE(board)
    r.SetShape(pcbnew.SHAPE_T_SEGMENT)
    r.SetLayer(pcbnew.F_Fab)
    r.SetStart(V(-w / 2, -h / 2))
    r.SetEnd(V(w / 2, -h / 2))
    r.SetWidth(int(0.1 * MM))
    fp.Add(r)
    r2 = pcbnew.PCB_SHAPE(board)
    r2.SetShape(pcbnew.SHAPE_T_SEGMENT)
    r2.SetLayer(pcbnew.F_Fab)
    r2.SetStart(V(w / 2, -h / 2))
    r2.SetEnd(V(w / 2, h / 2))
    r2.SetWidth(int(0.1 * MM))
    fp.Add(r2)
    r3 = pcbnew.PCB_SHAPE(board)
    r3.SetShape(pcbnew.SHAPE_T_SEGMENT)
    r3.SetLayer(pcbnew.F_Fab)
    r3.SetStart(V(w / 2, h / 2))
    r3.SetEnd(V(-w / 2, h / 2))
    r3.SetWidth(int(0.1 * MM))
    fp.Add(r3)
    r4 = pcbnew.PCB_SHAPE(board)
    r4.SetShape(pcbnew.SHAPE_T_SEGMENT)
    r4.SetLayer(pcbnew.F_Fab)
    r4.SetStart(V(-w / 2, h / 2))
    r4.SetEnd(V(-w / 2, -h / 2))
    r4.SetWidth(int(0.1 * MM))
    fp.Add(r4)
    # 焊盘
    n = len(pins)
    half = (n + 1) // 2
    for i, (net, _pn, _v) in enumerate(pins):
        side = 0 if i < half else 1
        k = i if side == 0 else i - half
        px = (-w / 2 + 0.9 + k * pitch) if side == 0 else (w / 2 - 0.9 - k * pitch)
        py = (-h / 2 + 0.5) if side == 0 else (h / 2 - 0.5)
        pad = pcbnew.PAD(fp)
        pad.SetNumber(str(i + 1))
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetSize(V(0.6, 0.9))
        pad.SetPosition(V(px, py))
        pad.SetLayerSet(pad.SMDMask())
        pad.SetNet(netmap[net])
        fp.Add(pad)
    fp.SetPosition(V(x, y))
    board.Add(fp)
    return fp


def main():
    rows = load_rows()
    per_ref = group_refs(rows)
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(6)
    add_outline(board)

    # 网络
    netmap = {}
    for nm in sorted({net for pins in per_ref.values() for (net, _p, _v) in pins}):
        ni = pcbnew.NETINFO_ITEM(board, nm)
        board.Add(ni)
        netmap[nm] = ni

    # 网表器件: 行式装箱 (按实际宽高排, 留 2mm 间距 ⇒ 不重叠 ⇒ DRC 有意义)
    PK_AREA = (72.0, 5.0, BOARD_W - 3.0, BOARD_H - 3.0)   # x0,y0,x1,y1
    items = []
    PSEUDO = ("RAIL_", "NET_")
    for ref in sorted(per_ref.keys()):
        if ref.startswith(PSEUDO):
            continue   # ★网别名伪器件 (RAIL_SYS / NET_*) —— 不是元件, 不画封装
        pins = per_ref[ref]
        kind = kind_of(ref)
        w, h, _per, _pitch = size_of(kind, len(pins))
        items.append((ref, pins, kind, w, h))
    items.sort(key=lambda it: (round(it[4], 1), it[3]))
    px, py = PK_AREA[0], PK_AREA[1]
    row_h = 0.0
    placed = 0
    for (ref, pins, kind, w, h) in items:
        if px + w > PK_AREA[2]:
            px = PK_AREA[0]
            py += row_h + 3.0
            row_h = 0.0
        if py + h > PK_AREA[3]:
            print(f"⚠️ 装不下: {ref} (y={py:.1f}) ⇒ 需要更大板或更紧的间距")
            break
        make_footprint(board, ref, pins[0][2], kind, pins, netmap, px + w / 2.0, py + h / 2.0)
        placed += 1
        px += w + 3.0
        row_h = max(row_h, h)
    py += row_h + 3.0
    # SOM 承载区 (FET3572-C 68×50) + 它的 4×100pin/0.4mm BTB 座 (占位: 按 400 脚模型)
    sx, sy, sw, sh = SOM_AREA
    som = pcbnew.FOOTPRINT(board)
    som.SetReference("U_SOM_RK3572")
    som.SetValue("FET3572-C SoM 68x50 (PLACEHOLDER)")
    rr = pcbnew.PCB_SHAPE(board)
    rr.SetShape(pcbnew.SHAPE_T_SEGMENT)
    rr.SetLayer(pcbnew.F_Fab)
    rr.SetStart(V(sx, sy))
    rr.SetEnd(V(sx + sw, sy))
    rr.SetWidth(int(0.1 * MM))
    som.Add(rr)
    rr2 = pcbnew.PCB_SHAPE(board)
    rr2.SetShape(pcbnew.SHAPE_T_SEGMENT)
    rr2.SetLayer(pcbnew.F_Fab)
    rr2.SetStart(V(sx + sw, sy))
    rr2.SetEnd(V(sx + sw, sy + sh))
    rr2.SetWidth(int(0.1 * MM))
    som.Add(rr2)
    rr3 = pcbnew.PCB_SHAPE(board)
    rr3.SetShape(pcbnew.SHAPE_T_SEGMENT)
    rr3.SetLayer(pcbnew.F_Fab)
    rr3.SetStart(V(sx + sw, sy + sh))
    rr3.SetEnd(V(sx, sy + sh))
    rr3.SetWidth(int(0.1 * MM))
    som.Add(rr3)
    rr4 = pcbnew.PCB_SHAPE(board)
    rr4.SetShape(pcbnew.SHAPE_T_SEGMENT)
    rr4.SetLayer(pcbnew.F_Fab)
    rr4.SetStart(V(sx, sy + sh))
    rr4.SetEnd(V(sx, sy))
    rr4.SetWidth(int(0.1 * MM))
    som.Add(rr4)
    # BTB 座 (4 排 × 100 脚 @0.4mm) —— 沿 SOM 下边
    btb_pins = 400
    for i in range(btb_pins):
        side = i // 100
        k = i % 100
        px = sx + 3.0 + k * 0.4
        py = sy + sh - 4.0 + side * 1.2
        pad = pcbnew.PAD(som)
        pad.SetNumber(str(i + 1))
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetSize(V(0.25, 0.6))
        pad.SetPosition(V(px, py))
        pad.SetLayerSet(pad.SMDMask())
        som.Add(pad)
    som.SetPosition(V(0, 0))
    board.Add(som)

    # 安装孔
    mh = pcbnew.FOOTPRINT(board)
    mh.SetReference("MH_1")
    mh.SetValue("M2.2")
    for (mx, my) in ((3, 3), (BOARD_W - 3, 3), (3, BOARD_H - 3), (BOARD_W - 3, BOARD_H - 3)):
        pad = pcbnew.PAD(mh)
        pad.SetNumber("")
        pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
        pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        pad.SetSize(V(2.2, 2.2))
        pad.SetDrillSize(V(2.2, 2.2))
        pad.SetPosition(V(mx, my))
        pad.SetLayerSet(pad.UnplatedHoleMask())
        mh.Add(pad)
    mh.SetPosition(V(0, 0))
    board.Add(mh)

    board.BuildListOfNets()
    pcbnew.SaveBoard(PCB, board)

    # 自检: 重新载入, 比对 (ref,net) 集合
    b2 = pcbnew.LoadBoard(PCB)
    if b2 is None:
        print("❌ 存盘后读不回来 (板文件无效)")
        return 1
    pairs = set()
    for fp in list(b2.GetFootprints()):
        for pad in list(fp.Pads()):
            nm = pad.GetNetname()
            if nm:
                pairs.add((fp.GetReference(), nm))
    PSEUDO = ("RAIL_", "NET_")
    want = {(ref, net) for ref, pins in per_ref.items()
            if not ref.startswith(PSEUDO) for (net, _p, _v) in pins}
    missing, extra = want - pairs, pairs - want
    rep = [f"PCB 网表驱动生成 · {len(per_ref)} 个器件 · {len(want)} 个 (ref,net) 绑定 · 板 {BOARD_W}×{BOARD_H}mm",
           f"  板上 (ref,net) 绑定: {len(pairs)}",
           f"  ★缺失: {len(missing)} {sorted(missing)[:5]}",
           f"  ★多余: {len(extra)} {sorted(extra)[:5]}",
           f"  SOM 占位: 68×50mm + 4×100pin/0.4mm BTB (400 焊盘)"]
    ok = not missing and not extra
    rep.append(f"\n判定: {'全过 (板子与网表 100% 一致)' if ok else '有不一致'}")
    open(REPORT, "w", encoding="utf-8").write("\n".join(rep) + "\n")
    print("\n".join(rep))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
