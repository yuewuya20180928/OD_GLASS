#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_pcb_components.py —— 从网表生成 PCB 上的**器件与网络** (pcbnew / KiCad Python API)

为什么走这条路而不是先啃原理图:
  ★**KiCad 的 pcbnew Python API 在本机可用** (随 AppImage 一起) ⇒ ★**可以用官方 API 生成真正的器件、焊盘与网络**,
  而"手搓 .kicad_sch 的 S-expression"在 KiCad 10 的解析规则上试了很久仍不过 (★**原理图格式不是我们的战场**) ⇒
  ★**正确的优先级**: ①**PCB 是真正要交给工厂的产物** ⇒ 先让它"器件+网络"齐全且可机器验证;
  ②**原理图**由 KiCad GUI 从我们的 `HW/netlist_v1.net` 导入生成 (那是 .net 的标准用途, 一次动作) ⇒ 人类可读版。

本脚本:
  读 HW/netlist_v1.csv → 按 ref 归并出引脚(每个 (ref,net) 一个脚) ⇒ 用 pcbnew 造器件(footprint)+焊盘(pad)+网络(net)
  ⇒ 落进 HW/PCB/demo_mainboard.kicad_pcb (与 gen_kicad_project.py 生成的板框/叠层/网络类合并) ⇒
  ★**随后由 state/check_pcb_drc.py + state/check_pcb_nets.py 双重验证**: DRC=0 且 pad↔net 与网表 100% 一致。

器件外形 (按 ref 前缀, 贴近真实, 便于 DRC 有意义):
  R/C/L ⇒ 0603 (两脚, 脚距 1.6mm) · D/TVS ⇒ SOD-123 · U(IC) ⇒ SOIC-8 近似 (2×3mm) ·
  FB ⇒ 0805 四脚 · TP ⇒ 测试点 (单脚) · J*/CONN* ⇒ 连接器 (按针数算长度) · SW ⇒ 轻触 (2脚) · LED ⇒ 0805 两脚
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
# ★pcbnew 只存在于 KiCad AppImage 自带的 python 里 ⇒ 用 state/pcbnew_py.sh 跑本脚本
import pcbnew  # noqa: E402

NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
REPORT = os.path.join(PROJ, "HW", "PCB", "PCB_NETLIST_FILL.txt")

GRID_X0, GRID_Y0 = 8.0, 8.0
CELL_W, CELL_H = 11.0, 9.0
COLS = 14


def pcbnew_mm(v):
    return int(round(v * 1e6))


def load_rows():
    with open(NETLIST, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def group_refs(rows):
    per_ref = {}
    seen = {}
    for r in rows:
        ref = (r.get("ref") or "").strip()
        net = (r.get("net") or "").strip()
        if not ref or not net:
            continue
        key = (ref, net)
        idx = seen.get(key, 0)
        seen[key] = idx + 1
        per_ref.setdefault(ref, []).append((net, f"P{idx+1}", r.get("value", "")))
    return per_ref


def kind_of(ref):
    R = ref.upper()
    if R.startswith(("R_", "RN_")):
        return "R"
    if R.startswith(("C_", "CN_")):
        return "C"
    if R.startswith(("FB_", "L_")):
        return "FB"
    if R.startswith(("D_", "TVS")):
        return "D"
    if R.startswith(("U_", "IC_")):
        return "IC"
    if R.startswith(("J_", "CONN_")):
        return "CONN"
    if R.startswith(("SW_", "BT_")):
        return "SW"
    if R.startswith(("LED_", "D_LED")):
        return "LED"
    if R.startswith(("TP_",)):
        return "TP"
    if R.startswith(("Q_",)):
        return "Q"
    return "IC"


def footprint_size(kind, npins):
    """(宽mm, 高mm, 每侧脚数, 脚间距mm)"""
    if kind in ("R", "C", "LED", "D"):
        return 1.8, 1.0, 1, 1.6
    if kind == "FB":
        return 2.4, 1.4, 2, 1.0
    if kind == "SW":
        return 3.0, 3.0, 1, 2.5
    if kind == "TP":
        return 1.6, 1.6, 1, 0.0
    if kind == "CONN":
        w = max(4.0, npins * 0.5 + 1.5)
        return w, 3.5, npins, 0.5
    # IC / 其它: 两排
    per = max(1, (npins + 1) // 2)
    return max(4.0, per * 1.27 + 1.0), 4.0, per, 1.27


def main():
    if not os.path.exists(PCB):
        print(f"[FAIL] 找不到板文件 (先跑 state/gen_kicad_project.py): {PCB}")
        return 1
    rows = load_rows()
    per_ref = group_refs(rows)
    board = pcbnew.LoadBoard(PCB)

    # 1) 先清掉上次生成的器件类 footprint (只保留机械类: 安装孔/连接器座/按钮座)
    keep = []
    # ★先把列表取全再删 —— 边遍历边 Remove 会让迭代器失效 (后续项变成裸 SwigPyObject)
    all_fps = list(board.GetFootprints())
    for fp in all_fps:
        ref = fp.GetReference()
        if ref.startswith("J_FPC_") or ref.startswith("U_SOM_") or ref.startswith("J_USB") \
           or ref.startswith("J_UART") or ref.startswith("J_JTAG") or ref.startswith("SW_") \
           or ref.startswith("LED_") or ref.startswith("MountingHole"):
            keep.append(fp)
        else:
            board.Remove(fp)
    # 2) 网络表里的每个 ref 都要有 footprint; 已有的机械件先记下它占用的网络
    have = {fp.GetReference(): fp for fp in list(board.GetFootprints())}

    # 3) 建立网络
    netnames = sorted({net for r in rows for (net, _, _) in [(x[0], x[1], x[2]) for x in per_ref.get((r.get("ref") or "").strip(), [])]})
    netnames = sorted({net for pins in per_ref.values() for (net, _, _) in pins})
    netmap = {}
    for nm in netnames:
        ni = pcbnew.NETINFO_ITEM(board, nm)
        board.Add(ni)
        netmap[nm] = ni

    # 4) 生成器件
    placed = 0
    col, row = 0, 0
    x, y = GRID_X0, GRID_Y0
    for ref in sorted(per_ref.keys()):
        pins = per_ref[ref]
        kind = kind_of(ref)
        if ref in have:
            fp = have[ref]
            # 机械件: 把网表里的网挂到它的焊盘 (按针数对位)
            pads = list(fp.Pads())
            for i, (net, _pn, _v) in enumerate(pins):
                if i < len(pads):
                    pads[i].SetNet(netmap[net])
            continue
        w, h, per_side, pitch = footprint_size(kind, len(pins))
        fp = pcbnew.FOOTPRINT(board)
        fp.SetReference(ref)
        fp.SetValue(per_ref[ref][0][2][:40] if per_ref[ref] else ref)
        # 矩形本体 (Edge.Cuts)
        r = pcbnew.PCB_SHAPE(board)
        r.SetShape(pcbnew.SHAPE_T_SEGMENT)
        r.SetLayer(pcbnew.Edge_Cuts)
        r.SetStart(pcbnew.VECTOR2I(pcbnew_mm(-w / 2), pcbnew_mm(-h / 2)))
        r.SetEnd(pcbnew.VECTOR2I(pcbnew_mm(w / 2), pcbnew_mm(h / 2)))
        r.SetWidth(pcbnew_mm(0.1))
        fp.Add(r)
        # 焊盘: 两排
        n = len(pins)
        for i, (net, _pn, _v) in enumerate(pins):
            side = 0 if i < (n + 1) // 2 else 1
            k = i if side == 0 else i - (n + 1) // 2
            px = (-w / 2 + 0.8 + k * pitch) if side == 0 else (w / 2 - 0.8 - k * pitch)
            py = 0.0 if side == 0 else (h / 2 - 0.6)
            pad = pcbnew.PAD(fp)
            pad.SetNumber(str(i + 1))
            pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            pad.SetShape(pcbnew.PAD_SHAPE_RECT)
            pad.SetSize(pcbnew.VECTOR2I(pcbnew_mm(0.6), pcbnew_mm(0.9)))
            pad.SetPosition(pcbnew.VECTOR2I(pcbnew_mm(px), pcbnew_mm(py)))
            pad.SetLayerSet(pad.SMDMask())
            pad.SetNet(netmap[net])
            fp.Add(pad)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew_mm(x), pcbnew_mm(y)))
        board.Add(fp)
        placed += 1
        # 网格推进 (机械件所在区域留空: 右侧 20mm 与上边不放)
        col += 1
        if col >= COLS:
            col = 0
            row += 1
        x = GRID_X0 + col * CELL_W
        y = GRID_Y0 + row * CELL_H

    board.BuildListOfNets()
    pcbnew.SaveBoard(PCB, board)

    # 4) 报告 + 自检: 每个 (ref, net) 都要在板上有一个带该网的焊盘
    b2 = pcbnew.LoadBoard(PCB)
    pairs = set()
    for fp in b2.GetFootprints():
        for pad in fp.Pads():
            nm = pad.GetNetname()
            if nm:
                pairs.add((fp.GetReference(), nm))
    want = {(ref, net) for ref, pins in per_ref.items() for (net, _p, _v) in pins}
    missing = want - pairs
    extra = pairs - want
    rep = [f"PCB 器件/网络生成 · {len(per_ref)} 个器件 · {len(want)} 个 (ref,net) 绑定",
           f"  新增器件: {placed} 个",
           f"  板上 (ref,net) 绑定: {len(pairs)} 个",
           f"  ★缺失: {len(missing)}  {sorted(missing)[:6]}",
           f"  ★多余: {len(extra)}  {sorted(extra)[:6]}"]
    ok = (not missing) and (not extra)
    rep.append(f"\n判定: {'全过 (板子与网表 100% 一致)' if ok else '有不一致'}")
    open(REPORT, "w", encoding="utf-8").write("\n".join(rep) + "\n")
    print("\n".join(rep))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
