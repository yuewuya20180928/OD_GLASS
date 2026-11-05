#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_power_pour.py —— ★★给大电流网加铜皮 (2026-11-05 10:30)

★**为什么**: 实测 (官方板 = 臂 A):
  · `RAIL_DEMO_5V` = **151.1mm / 455 段在 F.Cu (线宽 0.25mm) + 66 段在 In2.Cu (内层 0.5oz) / 过孔只有 4 个**
  · `RAIL_SOM_DCIN` = SoM 侧 7 脚并联 (J_SOM_P3.91/93/95/97/98/99/100, 0.2×0.7) ⇒ 汇流段只有 0.2~0.3mm
  ⇒ ★**0.25mm 外层 1oz 铜 ≈ 1.1A, 内层 0.5oz ≈ 0.5A** ⇒ ★**SoM 的 5~13V 输入 (手册 §2.4.2) 扛不住**
  ⇒ ★**解法**: 铺一层**同网铜皮** (KiCad zone) ⇒ 铜皮与细线并联 ⇒ 有效截面暴涨
     ⇒ ★**Cu 皮自动避让别的网** (KiCad 按 0.2mm 净距填充) ⇒ 不引入 DRC 违规

★**做法**: 在该网的铜箔**包围盒 + 外扩 margin** 上加一个 F.Cu 的 zone ⇒ 填铜 ⇒ 重新量
★**幂等**: 已经有同网同区域 zone 就跳过
★**只加铜皮, 不改走线** ⇒ 不影响布线结果

用法:
    python3 state/add_power_pour.py [板路径] [网名 ...]
    默认板 = 官方板; 默认网 = RAIL_DEMO_5V
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import pcbnew  # noqa: E402

MARGIN_MM = 2.0
LAYER = pcbnew.F_Cu


def net_bbox(board, net):
    """该网所有铜 (焊盘/走线/过孔) 的包围盒 (mm)"""
    xs, ys = [], []
    for f in board.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() != net:
                continue
            q = p.GetPosition(); sz = p.GetSize()
            xs += [q.x / 1e6 - sz.x / 2e6, q.x / 1e6 + sz.x / 2e6]
            ys += [q.y / 1e6 - sz.y / 2e6, q.y / 1e6 + sz.y / 2e6]
    for t in board.GetTracks():
        if t.GetNetname() != net:
            continue
        for pt in (t.GetStart(), t.GetEnd()):
            xs.append(pt.x / 1e6); ys.append(pt.y / 1e6)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def main():
    pcb = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") \
        else os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
    nets = [a for a in sys.argv[2:] if not a.startswith("-")] or ["RAIL_DEMO_5V"]
    if not os.path.exists(pcb):
        print("✗ 板不存在: %s" % pcb)
        return 1
    board = pcbnew.LoadBoard(pcb)
    board.BuildListOfNets()
    added = 0
    for net in nets:
        bb = net_bbox(board, net)
        if bb is None:
            print("  ⚠️ %s: 板上没有这个网的铜 ⇒ 跳过" % net)
            continue
        x0, y0, x1, y1 = bb
        x0 -= MARGIN_MM; y0 -= MARGIN_MM
        x1 += MARGIN_MM; y1 += MARGIN_MM
        # ★幂等: 已经有同网 zone 就跳过
        for z in board.Zones():
            if z.GetNetname() == net and z.GetLayer() == LAYER:
                print("  ℹ️ %s: 已经有同网铜皮 ⇒ 跳过" % net)
                break
        else:
            code = board.GetNetcodeFromNetname(net)
            if code <= 0:
                print("  ⚠️ %s: 板上没有这个网 ⇒ 跳过" % net)
                continue
            z = pcbnew.ZONE(board)
            z.SetLayer(LAYER)
            z.SetNetCode(code)
            z.SetIsFilled(False)
            z.SetLocalClearance(pcbnew.FromMM(0.20))
            z.SetMinThickness(pcbnew.FromMM(0.20))
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
            z.SetThermalReliefGap(pcbnew.FromMM(0.30))
            z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.40))
            outline = z.Outline()
            outline.NewOutline()
            for (px, py) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
                outline.Append(pcbnew.VECTOR2I(pcbnew.FromMM(px), pcbnew.FromMM(py)))
            board.Add(z)
            print("  ✅ %s: 加铜皮 (%.1f,%.1f)-(%.1f,%.1f) mm · 净距 0.20 · 热焊盘" %
                  (net, x0, y0, x1, y1))
            added += 1
    if not added:
        print("  (没有新增铜皮)")
        return 0
    # ★填铜 (必须重读再填, ★同会话里填会把铜当孤岛删空 ⇒ 已知坑)
    pcbnew.SaveBoard(pcb, board)
    b2 = pcbnew.LoadBoard(pcb)
    b2.BuildConnectivity()
    filler = pcbnew.ZONE_FILLER(b2)
    filler.Fill(b2.Zones())
    pcbnew.SaveBoard(pcb, b2)
    # ★量铜皮面积 (净距裁掉之后还剩多少)
    b3 = pcbnew.LoadBoard(pcb)
    b3.BuildConnectivity()
    tot = 0.0
    for z in b3.Zones():
        if z.GetNetname() not in nets:
            continue
        try:
            tot += z.GetFilledArea() / 1e12
        except Exception:
            pass
    print("  铜皮填充面积合计: %.1f mm²" % tot)
    print("  已写回: %s" % pcb)
    return 0


if __name__ == "__main__":
    sys.exit(main())
