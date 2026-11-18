#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-324 · mech-lead · J_SOM_P4 针距只读探针 (READ-ONLY)

问题: ISS-322 登记「`LED_G` 被 `LED_B` 掐 0.200mm」—— 这条到底卡在哪?
本探针把 J_SOM_P4 的 pad19 (LED_G) / pad21 (LED_B) 逐个读出来 (坐标 / 尺寸 / 针距),
判断这 0.200mm 是【器件侧】还是【连接器针距侧】。
★零写板★
用法: bash state/pcbnew_py.sh logs/iss324/probe_som_pad_pitch.py
"""
import math
import sys

import pcbnew

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
PCB = ROOT + "/HW/PCB/demo_mainboard.kicad_pcb"


def p2mm(v):
    return float(v) / 1e6


def main():
    board = pcbnew.LoadBoard(PCB)
    print("=" * 80)
    print("ISS-324 probe_som_pad_pitch · READ-ONLY")
    print("=" * 80)

    for fp in board.GetFootprints():
        if fp.GetReference() != "J_SOM_P4":
            continue
        pads = []
        for pad in fp.Pads():
            pp = pad.GetPosition()
            s = pad.GetSize()
            pads.append({
                "num": pad.GetNumber(),
                "x": p2mm(pp.x), "y": p2mm(pp.y),
                "w": p2mm(s.x), "h": p2mm(s.y),
                "net": pad.GetNetname(),
                "type": str(pad.GetAttribute()),
            })
        print("J_SOM_P4 焊盘数 = %d · 封装原点 = (%.2f, %.2f)"
              % (len(pads), p2mm(fp.GetPosition().x), p2mm(fp.GetPosition().y)))
        xs = sorted({p["x"] for p in pads})
        ys = sorted({p["y"] for p in pads})
        print("  X 唯一值 %d 个: %s" % (len(xs), ["%.2f" % v for v in xs[:12]]))
        print("  Y 唯一值 %d 个: %s" % (len(ys), ["%.2f" % v for v in ys[:12]]))

        by_num = {p["num"]: p for p in pads}
        for n in ("19", "21", "20", "18", "22"):
            if n in by_num:
                p = by_num[n]
                print("  pad%-3s abs=(%.2f, %.2f) size=%.3f x %.3f net=%-12s type=%s"
                      % (n, p["x"], p["y"], p["w"], p["h"], p["net"], p["type"]))

        for a, b in (("19", "21"), ("19", "20"), ("18", "19")):
            if a in by_num and b in by_num:
                pa, pb = by_num[a], by_num[b]
                dx = pa["x"] - pb["x"]
                dy = pa["y"] - pb["y"]
                centre = math.hypot(dx, dy)
                # 边缘到边缘净距 (两 pad 同向 ⇒ 中心距 - 半宽 - 半宽)
                edge = centre - pa["w"] / 2 - pb["w"] / 2
                print("  pad%s <-> pad%s : 中心距 %.3f mm · 边缘净距 %.3f mm  (net %s / %s)"
                      % (a, b, centre, edge, pa["net"], pb["net"]))

        # 沿 X 方向的最小相邻针距 (同排)
        row = sorted([p for p in pads if abs(p["y"] - by_num["19"]["y"]) < 1e-6],
                     key=lambda p: p["x"])
        if len(row) > 2:
            d = []
            for i in range(len(row) - 1):
                dd = row[i + 1]["x"] - row[i]["x"]
                d.append((dd, row[i]["num"], row[i + 1]["num"]))
            d.sort()
            print("  同 Y 排 (Y=%.2f) 共 %d 脚 · 最小相邻针距 = %.3f mm (pad%s↔pad%s) · 最大 = %.3f mm"
                  % (row[0]["y"], len(row), d[0][0], d[0][1], d[0][2], d[-1][0]))

    print("\n[END] 只读探针跑完")


if __name__ == "__main__":
    sys.exit(main())
