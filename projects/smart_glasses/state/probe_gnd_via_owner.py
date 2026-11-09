#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_gnd_via_owner.py —— ★★★【★★卡死端点的 GND 通孔是【谁家的】? ⇒ ★★决定 `PCB_CONN_GND_ESCAPE` 这个旋钮有没有用★★】★★★

★★★**★为什么要有这个 (★2026-11-10 03:0x)★★★**
  ★**实测 (v76ru 终板分类)**: ★**A2 桶 5 条的端点全是"被 GND 通孔卡死 0.162mm"** ⇒ ★★
  ★★**⇒ 那 5 条本来该由 `PCB_CONN_GND_ESCAPE` 解决 (★它管的就是"连接器 GND 下拉孔不许落在差分脚逃逸走廊里"★)**
    ⇒ ★★**⇒ 但那个旋钮当前是 `CONN_CAM:4.0` ⇒ 4.0mm 早该躲开 0.162mm ⇒ ⇒ ★★所以挡路的孔【不是 CONN_CAM 自己的】★★**
  ★★★**★⇒ 结论决定下一步: ★★如果挡路孔属于别的连接器 ⇒ 旋钮该加别的 ref (★零代码风险!)★; ★★
    ⇒ 如果属于 CONN_CAM 自己 ⇒ 旋钮规则对【多行焊盘】没覆盖 ⇒ 要改代码** ★★★

用法:
  bash state/pcbnew_py.sh state/probe_gnd_via_owner.py <板> <DRC.json> [--nets A,B,C]
"""
import sys
import os
import json
import re
import math

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pcbnew  # noqa: E402

MM = 1e6


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        return 2
    boardp, drcp = a[0], a[1]
    only = None
    if "--nets" in a:
        i = a.index("--nets")
        only = set((a[i + 1] or "").split(","))
    b = pcbnew.LoadBoard(boardp)

    # GND 通孔 (★带位置/直径★) + 所有 GND 焊盘 (★用来认"谁家的孔"★)
    gvias = []
    for t in b.GetTracks():
        if t.Type() != pcbnew.PCB_VIA_T:
            continue
        if t.GetNetname() != "GND":
            continue
        s = t.GetStart()
        gvias.append((s.x / MM, s.y / MM, t.GetWidth(pcbnew.F_Cu) / MM))
    gpads = []
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() != "GND":
                continue
            pos = p.GetPosition()
            gpads.append((pos.x / MM, pos.y / MM,
                          "%s.%s" % (f.GetReference(), p.GetNumber())))

    byu = {}
    for t in b.GetTracks():
        try:
            byu[t.m_Uuid.AsString()] = ("t", t)
        except Exception:
            pass
    for f in b.GetFootprints():
        for p in f.Pads():
            try:
                byu[p.m_Uuid.AsString()] = ("p", p)
            except Exception:
                pass

    d = json.load(open(drcp, encoding="utf-8"))
    items = d.get("unconnected_items") or []
    print("═══ GND 通孔归属 (板 = %s) ═══" % boardp)
    print("GND 通孔 %d 个 · GND 焊盘 %d 个" % (len(gvias), len(gpads)))
    print("")
    for it in items:
        its = it.get("items") or []
        if len(its) != 2:
            continue
        m0 = re.search(r"\[([^\]]+)\]", its[0].get("description") or "")
        m1 = re.search(r"\[([^\]]+)\]", its[1].get("description") or "")
        net = m0.group(1) if m0 else "?"
        if net != (m1.group(1) if m1 else ""):
            continue
        if only and net not in only:
            continue
        for sub in its:
            o = byu.get(sub.get("uuid"))
            if o is None:
                continue
            kind, obj = o
            if kind == "p":
                pos = obj.GetPosition()
                nm = "%s.%s" % (obj.GetParentFootprint().GetReference(),
                                obj.GetNumber())
                cx, cy = pos.x / MM, pos.y / MM
            else:
                s = obj.GetStart()
                cx, cy = s.x / MM, s.y / MM
                nm = "走线端"
            # 最近 GND 通孔
            best = None
            for (vx, vy, vd) in gvias:
                dd = math.hypot(vx - cx, vy - cy)
                if best is None or dd < best[0]:
                    best = (dd, vx, vy, vd)
            if best is None:
                continue
            dd, vx, vy, vd = best
            # 那个孔最近的 GND 焊盘 ⇒ 推断"谁家的"
            owner = None
            bd = 1e9
            for (px, py, pnm) in gpads:
                d2 = math.hypot(px - vx, py - vy)
                if d2 < bd:
                    bd, owner = d2, pnm
            print("%-16s @%-12s (%.3f,%.3f) ⇒ 最近 GND 孔 (%.3f,%.3f) 距端点 %.3fmm Ø%.2f ⇒ 孔最近 GND 焊盘 %s (距 %.3fmm)"
                  % (net, nm, cx, cy, vx, vy, dd, vd, owner, bd))
    return 0


if __name__ == "__main__":
    sys.exit(main())
