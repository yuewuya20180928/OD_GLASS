#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_net_rootcause.py -- ★**逐网根因探针 (对比两块板)**

★**为什么需要它 (11-06 04:1x)**: 名单制闸能告诉我"退铜了哪几个网", 但**不告诉我为什么退**
  ⇒ ★**"缺整条腿" 和 "出脚被封" 是两种根因, 修法完全不同** (前者要走廊/拓扑, 后者要 escape/rip-up)

★**分类判据 (按焊盘到最近同网铜的距离 d)**:
  · d <= 0.30mm            ⇒ ★**已接上**
  · 0.30 < d <= 5.0mm      ⇒ ★**端点缝 (差最后一小段)**
  · d > 5.0mm              ⇒ ★**整腿缺失 (这根铜压根没长出来)**
★**外加**: 每个焊盘到最近别网铜的距离 d2 ⇒ d2 小 ⇒ ★**出脚被封 (F2)**

用法:
  bash state/pcbnew_py.sh state/probe_net_rootcause.py <板1> [--nets A,B] [--compare <板2>]
"""
import sys
import math
import pcbnew

MM = 1e6


def pt_seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 <= 1e-12:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def load(path):
    b = pcbnew.LoadBoard(path)
    pads = []
    for f in b.GetFootprints():
        for p in f.Pads():
            q = p.GetPosition()
            sz = p.GetSize()
            pads.append(dict(ref=f.GetReference(), num=str(p.GetNumber()),
                             net=p.GetNetname(), x=q.x / MM, y=q.y / MM,
                             w=sz.x / MM, h=sz.y / MM))
    segs, vias = [], []
    for t in b.GetTracks():
        s, e = t.GetStart(), t.GetEnd()
        d = dict(net=t.GetNetname(), layer=t.GetLayerName(),
                 x1=s.x / MM, y1=s.y / MM, x2=e.x / MM, y2=e.y / MM,
                 w=(t.GetWidth(pcbnew.F_Cu) if t.Type() == pcbnew.PCB_VIA_T else t.GetWidth()) / MM)
        if t.Type() == pcbnew.PCB_VIA_T:
            d["x"], d["y"] = s.x / MM, s.y / MM
            vias.append(d)
        else:
            segs.append(d)
    return pads, segs, vias


def net_report(path, nets):
    pads, segs, vias = load(path)
    out = {}
    for n in nets:
        np_ = [p for p in pads if p["net"] == n]
        ns = [s for s in segs if s["net"] == n]
        nv = [v for v in vias if v["net"] == n]
        length = sum(math.hypot(s["x2"] - s["x1"], s["y2"] - s["y1"]) for s in ns)
        # ★每焊盘: 最近同网铜距离 / 最近别网铜距离
        items = []
        for p in np_:
            d_same = 1e9
            for s in ns:
                dd = pt_seg_dist(p["x"], p["y"], s["x1"], s["y1"], s["x2"], s["y2"])
                dd = max(0.0, dd - s["w"] / 2.0)
                if dd < d_same:
                    d_same = dd
            for v in nv:
                dd = max(0.0, math.hypot(p["x"] - v["x"], p["y"] - v["y"]) - v["w"] / 2.0)
                d_same = min(d_same, dd)
            d_other = 1e9
            blocker = None
            for s in segs:
                if s["net"] == n or not s["net"]:
                    continue
                dd = pt_seg_dist(p["x"], p["y"], s["x1"], s["y1"], s["x2"], s["y2"])
                dd = max(0.0, dd - s["w"] / 2.0)
                if dd < d_other:
                    d_other, blocker = dd, "%s[%s]" % (s["net"], s["layer"])
            for v in vias:
                if v["net"] == n or not v["net"]:
                    continue
                dd = max(0.0, math.hypot(p["x"] - v["x"], p["y"] - v["y"]) - v["w"] / 2.0)
                if dd < d_other:
                    d_other, blocker = dd, "%s[VIA]" % v["net"]
            items.append(dict(pad="%s.%s" % (p["ref"], p["num"]), x=p["x"], y=p["y"],
                              d_same=d_same, d_other=d_other, blocker=blocker))
        out[n] = dict(npads=len(np_), nseg=len(ns), nvia=len(nv),
                      length=length, items=items)
    return out


def verdict(it, zero=False):
    d = it["d_same"]
    if zero:
        tag = "★★整网无铜(一根都没长出来)"
    elif d <= 0.30:
        tag = "已接上"
    elif d <= 5.0:
        tag = "★端点缝(差最后一小段)"
    else:
        tag = "★★整腿缺失(铜没长出来)"
    if it["d_other"] <= 0.45:
        tag += " +出脚被封(%s @%.3fmm)" % (it["blocker"], it["d_other"])
    return tag


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 2
    board1 = a[0]
    nets = []
    board2 = None
    for i, tok in enumerate(a):
        if tok == "--nets" and i + 1 < len(a):
            nets = [x for x in a[i + 1].split(",") if x]
        if tok == "--compare" and i + 1 < len(a):
            board2 = a[i + 1]
    if not nets:
        print("★必须给 --nets")
        return 2
    r1 = net_report(board1, nets)
    r2 = net_report(board2, nets) if board2 else None
    print("═══ 板1: %s ═══" % board1)
    if r2:
        print("═══ 板2(对比): %s ═══" % board2)
    for n in nets:
        v = r1[n]
        print("── %s: 焊盘 %d · 段 %d · 孔 %d · 总长 %.2fmm" %
              (n, v["npads"], v["nseg"], v["nvia"], v["length"]))
        for it in v["items"]:
            print("     %-22s (%7.2f,%7.2f) 同网铜 %6.3fmm  别网铜 %6.3fmm ⇒ %s" %
                  (it["pad"], it["x"], it["y"], it["d_same"], it["d_other"],
                   verdict(it, zero=(v["nseg"] == 0 and v["nvia"] == 0))))
        if r2:
            w = r2[n]
            print("     [对比板2] 焊盘 %d · 段 %d · 孔 %d · 总长 %.2fmm" %
                  (w["npads"], w["nseg"], w["nvia"], w["length"]))
            for it in w["items"]:
                print("        %-22s 同网铜 %6.3fmm ⇒ %s" %
                      (it["pad"], it["d_same"], verdict(it)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
