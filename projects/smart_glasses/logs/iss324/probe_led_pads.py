#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-324 · mech-lead · 只读探针 (READ-ONLY)

★零写板★: 本脚本只调 pcbnew.LoadBoard + 只读遍历, 不调用任何 Save/Update/Plot 出盘函数.
读出:
  (1) 目标器件 (LED 族 + TP 族) 的封装原点 / 焊盘绝对坐标 / 焊盘尺寸 / 层 / 器件值
  (2) LED_G_D 直线距离复算 (R_LED_G.2 <-> D_LED_G.1)
  (3) 同族器件两两间距
  (4) Edge.Cuts 板框实读 (确认现役帧 = B160x100)
  (5) 板上三个串阻封装的器件值 (G-5 板面是否已同步)
用法: bash state/pcbnew_py.sh logs/iss324/probe_led_pads.py
"""
import math
import sys

import pcbnew

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
PCB = ROOT + "/HW/PCB/demo_mainboard.kicad_pcb"

TARGETS = [
    "R_LED_G", "R_LED_R", "R_LED_B",
    "D_LED_G", "D_LED_R", "D_LED_B",
    "TP_LED_G", "TP_LED_R", "TP_LED_B",
]


def p2mm(v):
    return float(v) / 1e6


def main():
    board = pcbnew.LoadBoard(PCB)
    print("=" * 78)
    print("ISS-324 probe_led_pads · READ-ONLY · %s" % PCB)
    print("=" * 78)

    # ---------- (4) Edge.Cuts ----------
    bb = board.GetBoardEdgesBoundingBox()
    print("\n[4] Edge.Cuts 板框实读 (mm): X %.4f .. %.4f  ·  Y %.4f .. %.4f  "
          "=> %.2f x %.2f"
          % (p2mm(bb.GetLeft()), p2mm(bb.GetRight()),
             p2mm(bb.GetTop()), p2mm(bb.GetBottom()),
             p2mm(bb.GetRight()) - p2mm(bb.GetLeft()),
             p2mm(bb.GetBottom()) - p2mm(bb.GetTop())))
    try:
        print("    general/thickness = %s mm" % board.GetDesignSettings().GetBoardThickness())
    except Exception as e:  # pragma: no cover
        print("    general/thickness read err: %r" % (e,))

    # ---------- (1) 器件逐个读出 ----------
    info = {}
    print("\n[1] 目标器件读出")
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref not in TARGETS:
            continue
        origin = fp.GetPosition()
        ox, oy = p2mm(origin.x), p2mm(origin.y)
        value = fp.GetValue()
        fpid = fp.GetFPID().GetLibItemName()
        pads = []
        for pad in fp.Pads():
            pp = pad.GetPosition()
            size = pad.GetSize()
            layers = []
            if pad.IsOnLayer(pcbnew.F_Cu):
                layers.append("F.Cu")
            if pad.IsOnLayer(pcbnew.B_Cu):
                layers.append("B.Cu")
            pads.append({
                "name": pad.GetNumber(),
                "x": round(p2mm(pp.x), 4),
                "y": round(p2mm(pp.y), 4),
                "w": round(p2mm(size.x), 4),
                "h": round(p2mm(size.y), 4),
                "layers": "+".join(layers) if layers else "-",
                "net": pad.GetNetname(),
            })
        pads.sort(key=lambda d: (d["name"]))
        info[ref] = {"origin": (ox, oy), "value": value, "fpid": fpid, "pads": pads}
        print("  %-10s origin=(%.2f, %.2f)  value=%-10s footprint=%s" %
              (ref, ox, oy, value, fpid))
        for d in pads:
            print("      pad%-3s abs=(%.2f, %.2f)  size=%.2f x %.2f  layer=%s  net=%s"
                  % (d["name"], d["x"], d["y"], d["w"], d["h"], d["layers"], d["net"]))

    # ---------- (2) LED_G_D 直线距离 ----------
    print("\n[2] LED_G_D 直线距离独立复算")
    rg = info.get("R_LED_G")
    dg = info.get("D_LED_G")
    if rg and dg:
        p_r2 = [p for p in rg["pads"] if p["name"] == "2"][0]
        p_d1 = [p for p in dg["pads"] if p["name"] == "1"][0]
        dx = p_d1["x"] - p_r2["x"]
        dy = p_d1["y"] - p_r2["y"]
        dist = math.hypot(dx, dy)
        print("    R_LED_G.2 = (%.2f, %.2f)   D_LED_G.1 = (%.2f, %.2f)"
              % (p_r2["x"], p_r2["y"], p_d1["x"], p_d1["y"]))
        print("    dx = %.2f   dy = %.2f" % (dx, dy))
        print("    hypot(dx,dy) = %.6f mm" % dist)
        print("    X 向占比 = %.3f%%   Y 向占比 = %.3f%%"
              % (abs(dx) / dist * 100.0, abs(dy) / dist * 100.0))
        print("    期望值 93.492727 · 偏差 = %.6f mm" % (dist - 93.492727))

    # ---------- (3) 同族器件间距 ----------
    print("\n[3] LED 族器件间距 (原点到原点)")
    ds = sorted([r for r in info if r.startswith(("D_LED", "R_LED", "TP_LED"))])
    for i in range(len(ds)):
        for j in range(i + 1, len(ds)):
            a, b = ds[i], ds[j]
            d = math.hypot(info[a]["origin"][0] - info[b]["origin"][0],
                           info[a]["origin"][1] - info[b]["origin"][1])
            print("    %-10s <-> %-10s  %.3f mm" % (a, b, d))

    # ---------- (5) 三个串阻封装值 ----------
    print("\n[5] 串阻封装器件值 (G-5 板面同步状态)")
    for r in ("R_LED_G", "R_LED_R", "R_LED_B"):
        if r in info:
            print("    %-10s value = %-10s  => %s"
                  % (r, info[r]["value"],
                     "已同步 G-5 新值" if info[r]["value"] not in ("1k", "1k ±1%", "1K")
                     else "★仍是旧值 1k ⇒ 板那一趟要同步"))

    print("\n[END] 只读探针跑完 · 未调用任何 Save/Update/Plot 函数")


if __name__ == "__main__":
    sys.exit(main())
