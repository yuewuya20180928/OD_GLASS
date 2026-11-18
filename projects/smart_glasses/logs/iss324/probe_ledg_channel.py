#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-324 · mech-lead · LED_G 通道邻域只读探针 (READ-ONLY)

问题: ISS-322 登记的第二条死因「`LED_G` 被 `LED_B` 掐 0.200mm」与第一条 (`LED_G_D` 93.49mm)
是不是同一件事? 本探针只读盘上板, 把 R_LED_G / TP_LED_G 周围的邻件 + 网名 + 铜箔净距列出来,
供交付页 §1/§6 判「哪一条死因是【挪 D_LED_G】能解的, 哪一条不是」。
★零写板★
用法: bash state/pcbnew_py.sh logs/iss324/probe_ledg_channel.py
"""
import math
import sys

import pcbnew

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
PCB = ROOT + "/HW/PCB/demo_mainboard.kicad_pcb"

FOCUS = ("R_LED_G", "TP_LED_G", "D_LED_G", "D_LED_B", "R_LED_B", "TP_LED_B")


def p2mm(v):
    return float(v) / 1e6


def bbox_of(fp):
    b = None
    for pad in fp.Pads():
        pp = pad.GetPosition()
        s = pad.GetSize()
        x0 = p2mm(pp.x) - p2mm(s.x) / 2
        x1 = p2mm(pp.x) + p2mm(s.x) / 2
        y0 = p2mm(pp.y) - p2mm(s.y) / 2
        y1 = p2mm(pp.y) + p2mm(s.y) / 2
        if b is None:
            b = [x0, x1, y0, y1]
        else:
            b[0] = min(b[0], x0); b[1] = max(b[1], x1)
            b[2] = min(b[2], y0); b[3] = max(b[3], y1)
    return b


def gap(a, b):
    dx = max(a[0] - b[1], b[0] - a[1], 0.0)
    dy = max(a[2] - b[3], b[2] - a[3], 0.0)
    return math.hypot(dx, dy)


def main():
    board = pcbnew.LoadBoard(PCB)
    print("=" * 80)
    print("ISS-324 probe_ledg_channel · READ-ONLY")
    print("=" * 80)

    fps = list(board.GetFootprints())
    info = {}
    for fp in fps:
        ref = fp.GetReference()
        nets = sorted({pad.GetNetname() for pad in fp.Pads() if pad.GetNetname()})
        info[ref] = {"fp": fp, "bbox": bbox_of(fp), "nets": nets,
                     "origin": (p2mm(fp.GetPosition().x), p2mm(fp.GetPosition().y))}

    print("\n[1] 焦点器件")
    for ref in FOCUS:
        if ref not in info:
            print("  %-10s ★盘上无此位号" % ref)
            continue
        i = info[ref]
        b = i["bbox"]
        print("  %-10s origin=(%.2f, %.2f)  nets=%s  copper X %.3f..%.3f Y %.3f..%.3f"
              % (ref, i["origin"][0], i["origin"][1], ",".join(i["nets"]), b[0], b[1], b[2], b[3]))

    print("\n[2] R_LED_G / TP_LED_G 邻域 (铜箔外框间净距 ≤ 3.00 mm) —— 谁在掐谁")
    for focus in ("R_LED_G", "TP_LED_G"):
        if focus not in info:
            continue
        fb = info[focus]["bbox"]
        rows = []
        for ref, i in info.items():
            if ref == focus or not i["bbox"]:
                continue
            g = gap(fb, i["bbox"])
            if g <= 3.0:
                rows.append((g, ref, ",".join(i["nets"])))
        rows.sort()
        print("  --- %s 邻域 ---" % focus)
        if not rows:
            print("      (3.00 mm 内无其它器件铜箔)")
        for g, ref, nets in rows:
            print("      %-12s 净距 %6.3f mm  net=%s" % (ref, g, nets))

    print("\n[3] `LED_G` 网在盘上的全部成员 (网名精确匹配)")
    for fp in fps:
        for pad in fp.Pads():
            if pad.GetNetname() == "LED_G":
                pp = pad.GetPosition()
                print("      %-10s pad%-3s (%.2f, %.2f)  type=%s"
                      % (fp.GetReference(), pad.GetNumber(), p2mm(pp.x), p2mm(pp.y),
                         pad.GetAttribute()))
    print("\n[4] `LED_B` 网在盘上的全部成员")
    for fp in fps:
        for pad in fp.Pads():
            if pad.GetNetname() == "LED_B":
                pp = pad.GetPosition()
                print("      %-10s pad%-3s (%.2f, %.2f)" % (fp.GetReference(), pad.GetNumber(),
                                                           p2mm(pp.x), p2mm(pp.y)))
    print("\n[5] `LED_G_D` 网在盘上的全部成员")
    for fp in fps:
        for pad in fp.Pads():
            if pad.GetNetname() == "LED_G_D":
                pp = pad.GetPosition()
                print("      %-10s pad%-3s (%.2f, %.2f)" % (fp.GetReference(), pad.GetNumber(),
                                                           p2mm(pp.x), p2mm(pp.y)))

    print("\n[6] 铜皮 (zone) 清单: 网名 + 外框 —— 看 R_LED_G 逃线方向有没有铜皮挡路")
    for z in board.Zones():
        bb = z.GetBoundingBox()
        try:
            net = z.GetNetname()
        except Exception:
            net = "?"
        print("      zone net=%-10s X %.3f..%.3f  Y %.3f..%.3f"
              % (net, p2mm(bb.GetLeft()), p2mm(bb.GetRight()),
                 p2mm(bb.GetTop()), p2mm(bb.GetBottom())))

    print("\n[END] 只读探针跑完")


if __name__ == "__main__":
    sys.exit(main())
