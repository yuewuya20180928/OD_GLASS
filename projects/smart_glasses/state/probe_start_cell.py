#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★【走廊解剖器: 起步格到底被谁的哪几段铜封死?】★ — 2026-11-11 主会话

★★**它要解决什么 (★2026-11-11 00:5x 实测踩到的痛★)** ★★
  · 之前查"某个网为什么布不出去"靠【读源码猜】+ 【手算】⇒ ★**漏过东西**: ★
    ★**`BOOT_N` 起步格 (63.50,12.25) 不只被 `ID_DETECT_0` 的【一段】铜封死, 而是被【三段】封死** ★★
    ★**⇒ 只看一段 ⇒ 会得出"让开这一段就够了"的【错误结论】⇒ ⇒ 改法不对 ⇒ ⇒ 全板扰动** ★★
  · ⇒ ★★**⇒ 本脚本把这件事【一次算全】: 对给定起步格, 列出【所有】进它 halo 的铜段 (按距离排序) ★★**

★**它给出的三个数 (★与闸的判据完全对齐★)**:
  ① ★**中心距** (点到线段的最短距离) —— ★★**注意: 这是【中心到中心】, 不是净距★★** ★★
  ② ★**净距** = 中心距 − 对方铜半宽 − 我方铜半宽 ⇒ ★**才是 KiCad DRC 报的那个数** ★★
  ③ ★**模型半径** = CLEAR + 对方铜半宽 + W_CLS[cls]/2 + HALO_MARGIN ⇒ ★**路由器内部判死用的半径** ★★
  ⇒ ★★**⇒ 关键判据: 【净距合法 (≥0.2)】但【中心距 < 模型半径】⇒ ⇒ 这不是物理堵死, 是【余量+调度】问题** ★★

用法:
  bash state/pcbnew_py.sh state/probe_start_cell.py <板.kicad_pcb> <格心x> <格心y>
      列出所有进该格 halo 的铜段 (★按距离排序★)
  bash state/pcbnew_py.sh state/probe_start_cell.py <板.kicad_pcb> --net <NET> --pad <ref>.<num>
      自动取该焊盘的出脚末端格心 (★用真板的 escape 直道末端 + 网格吸附★)
"""
import math
import os
import sys

import pcbnew

CLEAR = 0.20
W_CLS = (0.15, 0.25, 0.50)   # ★与路由器一致 (★W_MIN 随 env 变·这里用臂上的 0.15★)
HALO_MARGIN = float(os.environ.get("PCB_HALO_MARGIN", "0.0625"))
# ★★**2026-11-11 02:6x 【★HALO_MARGIN 改成读 env (★臂上是 0.0625·但默认值是 0.20★)】★★
#   ★**⇒ 用错默认值 ⇒ 模型半径算错 ⇒ "封死/不封死"的判断会反过来** ⇒ ⇒ 必须跟臂一致★★


def seg_pt_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(px - x1, py - y1), (x1, y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    qx, qy = x1 + t * dx, y1 + t * dy
    return math.hypot(px - qx, py - qy), (qx, qy)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    board = sys.argv[1]
    b = pcbnew.LoadBoard(board)
    if b is None:
        print("❌ 板读不出来: %s" % board)
        return 1

    gx = gy = None
    if "--net" in sys.argv and "--pad" in sys.argv:
        net = sys.argv[sys.argv.index("--net") + 1]
        padref = sys.argv[sys.argv.index("--pad") + 1]
        found = None
        for fp in b.GetFootprints():
            for pad in fp.Pads():
                if pad.GetNetname() != net:
                    continue
                key = "%s.%s" % (fp.GetReference(), pad.GetNumber())
                if key == padref or padref == "ANY":
                    found = pad
                    break
            if found:
                break
        if not found:
            print("❌ 没找到焊盘 %s (net=%s)" % (padref, net))
            return 1
        bb = found.GetBoundingBox()
        cx = (pcbnew.ToMM(bb.GetX()) + pcbnew.ToMM(bb.GetRight())) / 2.0
        cy = (pcbnew.ToMM(bb.GetY()) + pcbnew.ToMM(bb.GetBottom())) / 2.0
        # ★出脚直道向下 (★SoM 排的真实情形★) 走 ESC_LEN=1.20 ⇒ 再吸到最近格心
        # ★★★**★2026-11-11 02:8x 【★口径订正: 网格原点不是 0 (★真板 bb[0] = -0.05★)】★★★★ ★★
        #   ★**⇒ 用 `round(x/0.25)*0.25` (★假设原点=0★) 会算成 (63.50,12.25) ⇒ ★**那是错的**★
        #   ★**⇒ 真值 = (-0.05 + i*0.25) ⇒ (63.70, 12.20) ⇒ 与路由器 `_ci/_cj` 一致** ★★
        _bb = b.GetBoardEdgesBoundingBox()
        _ox = pcbnew.ToMM(_bb.GetLeft())
        _oy = pcbnew.ToMM(_bb.GetTop())
        _g = 0.25
        ex, ey = cx, cy + 1.20
        gx = _ox + round((ex - _ox) / _g) * _g
        gy = _oy + round((ey - _oy) / _g) * _g
        print("★焊盘 %s @ (%.3f,%.3f) ⇒ 推定起步格心 = (%.2f,%.2f)"
              % (padref, cx, cy, gx, gy))
    else:
        gx = float(sys.argv[2])
        gy = float(sys.argv[3])

    print("═══ 起步格 (%.3f, %.3f) 的解剖 (★板: %s★) ═══" % (gx, gy, os.path.basename(board)))
    hits = []
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK":
            continue
        lay = b.GetLayerName(t.GetLayer())
        s, e = t.GetStart(), t.GetEnd()
        x1, y1 = pcbnew.ToMM(s.x), pcbnew.ToMM(s.y)
        x2, y2 = pcbnew.ToMM(e.x), pcbnew.ToMM(e.y)
        w = pcbnew.ToMM(t.GetWidth())
        d, q = seg_pt_dist(gx, gy, x1, y1, x2, y2)
        halo = CLEAR + w / 2.0 + W_CLS[1] / 2.0 + HALO_MARGIN
        if d < halo:
            hits.append((d, w, halo, t.GetNetname(), lay,
                         x1, y1, x2, y2, q))
    if not hits:
        print("  ✔ 没有铜进这个格的 halo (★该格是活的★)")
        return 0
    hits.sort()
    print("  ★有 %d 段铜进这个格的 halo (★按中心距排序★):" % len(hits))
    for (d, w, halo, net, lay, x1, y1, x2, y2, q) in hits:
        print("    %-16s %-8s (%.3f,%.3f)->(%.3f,%.3f) w=%.3f" % (net, lay, x1, y1, x2, y2, w))
        print("        中心距 %.4f · 净距(边到边) %.4f · 模型半径 %.4f ⇒ %s"
              % (d, d - w / 2.0 - 0.125, halo,
                 "★封死(模型)·但净距合法⇒余量/调度问题★" if d - w / 2.0 - 0.125 >= CLEAR else "★物理堵死★"))
    print("\n  ★★**⇒ 结论**: ★**中心距 < 模型半径 ⇒ 路由器判死; 净距 < 0.2 ⇒ 真堵死** ★★")
    return 0


if __name__ == "__main__":
    sys.exit(main())
