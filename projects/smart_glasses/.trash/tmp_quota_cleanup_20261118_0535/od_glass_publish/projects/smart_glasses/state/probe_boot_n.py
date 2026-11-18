#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★【`BOOT_N` 到底被谁挡住? —— 用 pcbnew 真几何取证】★ — 2026-11-10 主会话

★**背景**: `v76ml` 是当前最好的臂 (★DRC 0 · unc 29 条/24 网·退铜 0·死腿 0·孤岛 1★),
★**唯一被晋级闸卡住的就是 `BOOT_N` 这一个孤岛** ⇒ ★**这就是剩下全部的工作量**。

★**本脚本**:
   ★ ① 列出 `BOOT_N` / `ID_DETECT_0` / `ID_DETECT_1` 三个网在 SoM 战场区 (x58..72, y8..15) 的**全部铜**
   ★ ② 算 `BOOT_N` 每个焊盘到**最近异网铜**的距离 ⇒ ★**指名道姓说出挡它的是哪一段** ★★
   ★ ③ 打印官方板同一区域作对照 (★官方板靠牺牲 `ID_DETECT_0` 换来 `BOOT_N` 通★)
"""
import math
import os
import sys

import pcbnew

MM = 1e6
AREA = (58.0, 72.0, 8.0, 15.0)      # ★ SoM 战场区 xmin,xmax,ymin,ymax
NETS = ("BOOT_N", "ID_DETECT_0", "ID_DETECT_1")


def pt_seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 < 1e-12:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def seg_seg_dist(x1, y1, x2, y2, x3, y3, x4, y4):
    def pt_seg(px, py, ax, ay, bx, by):
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        if L2 < 1e-12:
            return math.hypot(px - ax, py - ay)
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
        return math.hypot(px - (ax + t * dx), py - (ay + t * dy))
    return min(pt_seg(x1, y1, x3, y3, x4, y4), pt_seg(x2, y2, x3, y3, x4, y4),
               pt_seg(x3, y3, x1, y1, x2, y2), pt_seg(x4, y4, x1, y1, x2, y2))


def in_area(x, y):
    return AREA[0] <= x <= AREA[1] and AREA[2] <= y <= AREA[3]


def collect(board):
    """⇒ (pads[net]=[(x,y,ref,num)], segs[net]=[(x1,y1,x2,y2,layer,w)], vias[net]=[(x,y,layer,size)])"""
    pads = {n: [] for n in NETS}
    segs = {n: [] for n in NETS}
    vias = {n: [] for n in NETS}
    all_segs, all_vias = [], []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            nm = pad.GetNetname()
            if nm not in pads:
                continue
            r = pad.GetBoundingBox()
            cx = (r.GetLeft() + r.GetRight()) / 2 / MM
            cy = (r.GetTop() + r.GetBottom()) / 2 / MM
            pads[nm].append((cx, cy, fp.GetReference(), str(pad.GetNumber())))
    for t in board.GetTracks():
        nm = t.GetNetname()
        if t.GetClass() == "PCB_VIA":
            v = (nm, t.GetPosition().x / MM, t.GetPosition().y / MM, t.GetLayer(),
                 t.GetWidth() / MM)
            if nm in vias:
                vias[nm].append(v[1:])
            all_vias.append(v)
        else:
            s = (nm, t.GetStart().x / MM, t.GetStart().y / MM,
                 t.GetEnd().x / MM, t.GetEnd().y / MM, t.GetLayer(), t.GetWidth() / MM)
            if nm in segs:
                segs[nm].append(s[1:])
            all_segs.append(s)
    return pads, segs, vias, all_segs, all_vias


def report(board, tag):
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║ ★★ %s ══" % tag)
    print("╚══════════════════════════════════════════════════════════════╝")
    pads, segs, vias, all_segs, all_vias = collect(board)
    lay_name = {board.GetLayerName(i): i for i in range(board.GetCopperLayerCount())}

    for net in NETS:
        print("\n────── %s ──────" % net)
        for (x, y, ref, num) in sorted(pads[net]):
            print("  焊盘 %-8s.%-4s @ (%.2f, %.2f)" % (ref, num, x, y))
        ns = [s for s in segs[net] if in_area(s[0], s[1]) or in_area(s[2], s[3])]
        print("  ★ 战场区铜: %d 段 / %d 孔 (全网 %d 段 / %d 孔)" % (
            len(ns), len([v for v in vias[net] if in_area(v[0], v[1])]),
            len(segs[net]), len(vias[net])))
        for s in sorted(ns, key=lambda t: (t[4], t[0], t[1])):
            print("     L%-8s (%.2f,%.2f)->(%.2f,%.2f) w=%.3f" % (
                lay_name.get(s[4], str(s[4])), s[0], s[1], s[2], s[3], s[5]))
        for v in sorted([v for v in vias[net] if in_area(v[0], v[1])], key=lambda t: (t[0], t[1])):
            print("     ★孔 (%.2f,%.2f) L%s size=%.2f" % (
                v[0], v[1], lay_name.get(v[2], str(v[2])), v[3]))
        _b = [s for s in segs[net]]
        print("  ★ 全网铜: %d 段 / %d 孔" % (len(_b), len(vias[net])))

    # ★★**⇒ BOOT_N 的战场: 最近异网铜 ★★**
    print("\n── ★★ BOOT_N 焊盘 → 最近异网铜 (★指名道姓★) ──")
    bsegs = [s for s in segs["BOOT_N"] if in_area(s[0], s[1]) or in_area(s[2], s[3])]
    if not bsegs:
        print("  ★ BOOT_N 在战场区【一寸铜都没有】⇒ ⇒ 它是被【别处的铜】堵在出脚口")
    for (x, y, ref, num) in sorted(pads["BOOT_N"]):
        rows = []
        for (nm, sx1, sy1, sx2, sy2, lay, w) in all_segs:
            if nm == "BOOT_N":
                continue
            if not (in_area(sx1, sy1) or in_area(sx2, sy2)):
                continue
            d = min(seg_seg_dist(x, y, x, y, sx1, sy1, sx2, sy2) for _ in (0,))
            rows.append((d, "段", nm, lay_name.get(lay, str(lay)),
                         "(%.2f,%.2f)->(%.2f,%.2f)" % (sx1, sy1, sx2, sy2)))
        for (nm, vx, vy, lay, sz) in all_vias:
            if nm == "BOOT_N":
                continue
            if not in_area(vx, vy):
                continue
            rows.append((math.hypot(vx - x, vy - y), "孔", nm,
                         lay_name.get(lay, str(lay)), "@(%.2f,%.2f) Ø%.2f" % (vx, vy, sz)))
        rows.sort(key=lambda t: t[0])
        print("  焊盘 %-8s.%-4s @ (%.2f,%.2f):" % (ref, num, x, y))
        for r in rows[:4]:
            print("      ★ %.3fmm  %s %-14s L%-8s %s" % r)
    return pads, segs, vias


def main():
    board_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/chain_v76ml/final_chain.kicad_pcb"
    official = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses/HW/PCB/demo_mainboard.kicad_pcb"
    print("═══ 板: %s ═══" % board_path)
    report(pcbnew.LoadBoard(board_path), "候选臂 v76ml 终板")
    if len(sys.argv) > 2 and sys.argv[2] == "--official":
        report(pcbnew.LoadBoard(official), "官方板 (对照)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
