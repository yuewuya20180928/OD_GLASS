#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★【出脚口被谁挡? —— 16 个候选出脚口逐个试算】★ — 2026-11-10 主会话

★**背景**: `v76ml` 唯一被晋级闸卡住的 = `BOOT_N` 的出脚口 (63.60, 11.04) 一寸铜都没有。
★**本脚本**: 在【已布好铜的终板】上, 对 `BOOT_N` 的出脚口枚举
★            4 方向 × `ESC_LENS` 各长度 = 16 个候选直道,
★            逐个算【离最近异网铜/焊盘的距离】并与【净距要求】比较
★            ⇒ ★**指名道姓说出: 哪个方向被谁挡, 差多少毫米** ★★

★**用法**: `probe_escape_block.py <板> [网名]`
"""
import math
import os
import sys

import pcbnew

MM = 1e6
CLEAR = 0.20
W_MIN = 0.15
W_CLS = 0.25
HALO_MARGIN = 0.0625       # ★臂 env 的实测值 (PCB_HALO_MARGIN) ★
ESC_LENS = (1.2, 0.9, 0.6, 0.4)


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


def main():
    board = pcbnew.LoadBoard(sys.argv[1])
    target = sys.argv[2] if len(sys.argv) > 2 else "BOOT_N"
    ref, num = (sys.argv[3], sys.argv[4]) if len(sys.argv) > 4 else ("J_SOM_P1", "28")

    # ★★**找目标焊盘 ★★
    pad = None
    for fp in board.GetFootprints():
        if fp.GetReference() != ref:
            continue
        for p in fp.Pads():
            if str(p.GetNumber()) == num and p.GetNetname() == target:
                r = p.GetBoundingBox()
                pad = ((r.GetLeft() + r.GetRight()) / 2 / MM,
                       (r.GetTop() + r.GetBottom()) / 2 / MM)
    if pad is None:
        print("★ 找不到焊盘 %s.%s [%s]" % (ref, num, target))
        return 1
    cx, cy = pad
    print("═══ %s 焊盘 %s.%s @ (%.2f, %.2f) ═══" % (target, ref, num, cx, cy))

    # ★★**收集异网铜 (走线/孔) 与异网焊盘 ★★**
    copper = []   # (net, kind, x1,y1,x2,y2, layer, w)
    for t in board.GetTracks():
        if t.GetNetname() == target:
            continue
        if t.GetClass() == "PCB_VIA":
            copper.append((t.GetNetname(), "孔", t.GetPosition().x / MM, t.GetPosition().y / MM,
                           t.GetPosition().x / MM, t.GetPosition().y / MM,
                           t.GetLayer(), t.GetWidth() / MM))
        else:
            copper.append((t.GetNetname(), "段", t.GetStart().x / MM, t.GetStart().y / MM,
                           t.GetEnd().x / MM, t.GetEnd().y / MM, t.GetLayer(), t.GetWidth() / MM))
    pads = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == target:
                continue
            r = p.GetBoundingBox()
            pads.append((p.GetNetname(), fp.GetReference(), str(p.GetNumber()),
                         (r.GetLeft() + r.GetRight()) / 2 / MM,
                         (r.GetTop() + r.GetBottom()) / 2 / MM,
                         (r.GetRight() - r.GetLeft()) / MM,
                         (r.GetBottom() - r.GetTop()) / MM))

    lay_name = {board.GetLayerName(i): i for i in range(board.GetCopperLayerCount())}

    print("\n★ 净距要求: 走线-走线 = 0.20 + %.3f/2 + %.3f/2 = %.3fmm (+halo余量 %.4f ⇒ 栅格判死线 %.3f)"
          % (W_MIN, W_CLS, CLEAR + W_MIN / 2 + W_CLS / 2, HALO_MARGIN,
             CLEAR + W_MIN / 2 + W_CLS / 2 + HALO_MARGIN))
    print("★ 走线-焊盘 = 0.20 + %.3f/2 + 焊盘半宽 ⇒ 逐个算\n" % W_MIN)

    for ln in ESC_LENS:
        for (dx, dy) in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            ex, ey = cx + dx * ln, cy + dy * ln
            rows = []
            for (nm, kind, x1, y1, x2, y2, lay, w) in copper:
                if kind == "孔":
                    d = pt_seg_dist(x1, y1, cx, cy, ex, ey) - w / 2 - W_MIN / 2
                    need = CLEAR
                else:
                    d = seg_seg_dist(cx, cy, ex, ey, x1, y1, x2, y2) - w / 2 - W_MIN / 2
                    need = CLEAR
                rows.append((d, need, "铜", nm, lay_name.get(lay, str(lay)),
                             "(%.2f,%.2f)->(%.2f,%.2f) w=%.3f" % (x1, y1, x2, y2, w)))
            for (nm, rf, nu, px, py, pw, ph) in pads:
                # ★★**焊盘到候选直道的距离: 矩形到线段 ★★**
                d = _rect_seg_dist(px, py, pw, ph, cx, cy, ex, ey)
                rows.append((d - W_MIN / 2, CLEAR, "焊盘", nm, "",
                             "%s.%s @(%.2f,%.2f) %.2fx%.2f" % (rf, nu, px, py, pw, ph)))
            rows = [r for r in rows if r[0] < r[1] + 0.60]
            rows.sort(key=lambda t: t[0])
            verdict = "★**判死**" if rows and rows[0][0] < rows[0][1] else ("勉强" if rows and rows[0][0] < rows[0][1] + HALO_MARGIN else "OK")
            head = "  %s 方向(%+d,%+d) 长 %.1f ⇒ %s" % (
                "↓" if dy > 0 else ("↑" if dy < 0 else ("→" if dx > 0 else "←")),
                dx, dy, ln, verdict)
            if not rows:
                print("%s  (附近无铜)" % head)
                continue
            r0 = rows[0]
            print("%s" % head)
            for r in rows[:2]:
                print("        ★ 净距余量 %+.3fmm (需 ≥ %.3f) · %s %-14s L%-8s %s" % (
                    r[0], r[1], r[2], r[3], r[4], r[5]))
    return 0


def _rect_seg_dist(px, py, pw, ph, x1, y1, x2, y2):
    """★矩形(中心px,py,宽pw,高ph) 到线段的距离 (★取矩形四角+边到线的最小★)"""
    hx, hy = pw / 2, ph / 2
    best = 1e9
    # ★★**四角到线段 + 线段两端到矩形(近似) ★★**
    for (cx, cy) in ((px - hx, py - hy), (px + hx, py - hy), (px + hx, py + hy), (px - hx, py + hy)):
        best = min(best, pt_seg_dist(cx, cy, x1, y1, x2, y2))
    # ★★**矩形边到线段: 用矩形中心的法向投影近似 (★够用★) ★★**
    for (ax, ay) in ((x1, y1), (x2, y2)):
        best = min(best, _pt_rect_dist(ax, ay, px, py, hx, hy))
    return best


def _pt_rect_dist(px, py, cx, cy, hx, hy):
    dx = max(abs(px - cx) - hx, 0.0)
    dy = max(abs(py - cy) - hy, 0.0)
    return math.hypot(dx, dy)


if __name__ == "__main__":
    sys.exit(main())
