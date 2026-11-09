#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_pair_escape2.py —— ★★验证: N 腿的【相反方向】到底能不能出脚 (★决定 pair-aware 改造的可行性)

★★★**★为什么要有这个 (★2026-11-09 11:3x)★★★**
  ★**上一探针 (`probe_pair_escape.py`) 实测出**:
    · ★**A1 桶 5 对的 P/N 焊盘中心距 = 0.400mm** (★0.4mm pitch 排针上并排)
    · ★**P 腿出脚直道 = 垂直于排针方向** (★(0,+1.2) 三条 / (0,-1.2) 两条) ⇒ ★**P 的直道就贴在 N 焊盘旁**
    · ★★**⇒ 若 N 也同向出脚: 两直道中心距 0.400 ⇒ 净距 = 0.400 - 0.125 - 0.125 = 0.150mm < 0.200mm ⇒ ★★**N 必然被 `_stub_clear` 否掉** ★★
  ★★**⇒ 几何上的唯一解: P 与 N 必须走【相反】的垂直方向** ★★
  · ★★**但代码 `escape_stub` 的注释说 "SoM 0.4mm pitch ⇒ 往往只有一个方向能出脚 ⇒ 硬禁会让 N 没有直道 ⇒ 更糟" ⇒ ★★**这个前提需要验证** ★★
    (★若 N 的【相反方向】其实是通的 ⇒ ★★**那就证明"回落"逻辑才是元凶 ⇒ pair-aware 改造只要"禁止回落"** ★★)

★**本脚本**: ★**在真实板上, 对每条 A1 的 N 焊盘, 检查【与 P 相反】的那个垂直方向, 沿 ESC_LEN 长度是否满足净距** ★★
  ★**只读, 不改板**

用法: bash state/pcbnew_py.sh state/probe_pair_escape2.py [板]
"""
import collections
import math
import os
import sys

import pcbnew

MM = 1000000.0
CLEAR = 0.20
ESC_LEN = 1.2          # ★与 gen_pcb_routing.py 的 ESC_LEN 对齐 (★待核)
W = 0.25               # ★信号线宽

A1 = [
    ("CSI_D0_D0_N_SRC", "CSI_D0_D0_P_SRC"),
    ("CSI_D0_D1_N_SRC", "CSI_D0_D1_P_SRC"),
    ("CSI_D0_D3_N_SRC", "CSI_D0_D3_P_SRC"),
    ("DSI_D0_D2_N_SRC", "DSI_D0_D2_P_SRC"),
    ("DSI_D0_D3_N_SRC", "DSI_D0_D3_P_SRC"),
]


def main():
    boardp = sys.argv[1] if len(sys.argv) > 1 else "HW/PCB/demo_mainboard.kicad_pcb"
    b = pcbnew.LoadBoard(boardp)
    if b is None:
        print("★板读不出来")
        return 2

    pads = collections.defaultdict(list)
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname():
                pads[p.GetNetname()].append(p)
    copper = []   # (net, layer, x1,y1,x2,y2, w, kind)
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            copper.append((t.GetNetname(), None, p.x / MM, p.y / MM, p.x / MM, p.y / MM,
                           0.6, "VIA"))
        else:
            s, e = t.GetStart(), t.GetEnd()
            copper.append((t.GetNetname(), t.GetLayer(), s.x / MM, s.y / MM,
                           e.x / MM, e.y / MM, t.GetWidth() / MM, "TRK"))
    # ★焊盘也当铜 (★矩形近似: 用中心+半宽)
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if not p.GetNetname():
                continue
            pos = p.GetPosition()
            sz = p.GetSize()
            copper.append((p.GetNetname(), p.GetLayer(), pos.x / MM, pos.y / MM,
                           pos.x / MM, pos.y / MM, max(sz.x, sz.y) / MM, "PAD"))

    def seg_dist(px, py, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))

    def lane_clear(net, layer, x0, y0, dx, dy, length):
        """沿 (dx,dy) 方向走 length, 与异网铜的最小净距 (★同层才算)"""
        worst = 99.0
        who = "-"
        for (bn, bl, x1, y1, x2, y2, w, kind) in copper:
            if bn == net:
                continue
            if bl is not None and layer is not None and bl != layer:
                continue
            # ★取该铜沿线段的最近点 (★采样足够密)
            n = 24
            for k in range(n + 1):
                px = x0 + dx * length * k / n
                py = y0 + dy * length * k / n
                dd = seg_dist(px, py, x1, y1, x2, y2) - w / 2.0 - W / 2.0
                if dd < worst:
                    worst = dd
                    who = "%s[%s]" % (bn, kind)
        return worst, who

    print("★A1 桶 5 条: N 腿【与 P 相反】的垂直方向能不能出脚 (★只读实测)")
    print("═" * 84)
    ok_all = 0
    for n_net, p_net in A1:
        npads = pads.get(n_net, [])
        ppads = pads.get(p_net, [])
        if not npads or not ppads:
            continue
        best = None
        for pn in npads:
            for pp in ppads:
                a, c = pn.GetPosition(), pp.GetPosition()
                dd = math.hypot(a.x - c.x, a.y - c.y) / MM
                if best is None or dd < best[0]:
                    best = (dd, pn, pp)
        d, npad, ppad = best
        nx, ny = npad.GetPosition().x / MM, npad.GetPosition().y / MM
        px, py = ppad.GetPosition().x / MM, ppad.GetPosition().y / MM
        layer = npad.GetLayer()

        # ★P 的出脚方向 (取以 P 焊盘中心为端点的走线)
        pdir = None
        for t in b.GetTracks():
            if t.GetNetname() != p_net or t.Type() == pcbnew.PCB_VIA_T:
                continue
            s, e = t.GetStart(), t.GetEnd()
            sx, sy, ex, ey = s.x / MM, s.y / MM, e.x / MM, e.y / MM
            if math.hypot(sx - px, sy - py) < 0.01:
                pdir = (ex - sx, ey - sy)
                break
            if math.hypot(ex - px, ey - py) < 0.01:
                pdir = (sx - px, sy - py)
                break
        if pdir is None:
            print("★ %-18s ★P 腿没找到出脚走线" % n_net)
            continue
        # ★反方向
        odx, ody = -pdir[0], -pdir[1]
        mag = math.hypot(odx, ody)
        odx, ody = odx / mag, ody / mag

        same, who_same = lane_clear(n_net, layer, nx, ny, pdir[0] / mag, pdir[1] / mag, ESC_LEN)
        opp, who_opp = lane_clear(n_net, layer, nx, ny, odx, ody, ESC_LEN)
        verdict = "★可用" if opp >= CLEAR else "★不可用"
        if opp >= CLEAR:
            ok_all += 1
        print("★ %-18s  N 焊盘 (%.3f, %.3f)" % (n_net, nx, ny))
        print("    P 出脚方向 = (%.2f, %.2f)" % (pdir[0] / mag, pdir[1] / mag))
        print("    同向净距 = %+.3fmm (%s)   ⇒ %s" % (same, who_same, "★能走 ⇒ 正是它把 N 堵死" if same >= CLEAR else "★也走不了"))
        print("    反向净距 = %+.3fmm (%s)   ⇒ %s" % (opp, who_opp, verdict))
        print("─" * 84)
    print("★⇒ 反向可用数 = %d / 5" % ok_all)
    print("★⇒ ★★若 = 5 ⇒ ★★\"回落\"就是元凶 ⇒ pair-aware 改造只要【禁止 N 回落同向】★★")
    return 0


if __name__ == "__main__":
    sys.exit(main())
