#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_unconnected_worklist_v2.py -- ★★★**分层版未连接施工单 (2026-11-06 18:4x)**

★★★**为什么要 v2 (★实测事故)**:
  ① v1 (`state/probe_unconnected_worklist.py`) 的"最近异网铜"是 ★**纯二维距离, 不分层**
  ② ⇒ ★**它把"内层铜压在 F.Cu 焊盘下面"也报成墙** ⇒ ★**假墙**
     实测 v1 的 05:16 那份施工单: 别网铜 **In2.Cu 34 条 · F.Cu 16 · In4.Cu 4 · In6.Cu 1**
     ⇒ ★**55 条里有 39 条是内层铜 ⇒ 根本不是障碍**
  ③ ⇒ ★**照着 v1 的清单去"改封装/改布局"会改错东西** ⇒ ★**必须分层**

★★★**v2 的三条规矩 (★与 `state/geom_clear.py` 同源)**:
  ① ★**分层**: 焊盘只在它实际存在的层上有铜 ⇒ ★**异层铜不是墙**
     (★通孔焊盘 = 全层; ★通孔过孔 = 全层)
  ② ★**焊盘按矩形**: SoM BTB 焊盘 0.2×0.7mm ⇒ ★**当圆算会白扣 0.25mm**
  ③ ★**走线端点是圆头** (半径=线宽/2) ⇒ ★**算净距要按胶囊形**

★★**输出**: 每个未连接端点给三个数:
   ★**同层异网铜 (真墙)**: 最近的、**真的在同一层**的异网铜距离 + 是谁
   · 异层异网铜 (不是墙): 只作参考, ★**明确标注"不同层"**
   · 同网铜距离 (该网自己已有的铜离这个焊盘多远)

用法:
  bash state/pcbnew_py.sh state/probe_unconnected_worklist_v2.py <板> <DRC.json> [--out <txt>]
"""
import sys
import os
import json
import math
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pcbnew  # noqa: E402
import geom_clear as GC  # noqa: E402

MM = 1e6
CLEAR = 0.20


def pad_rect(p):
    """★焊盘 → (矩形四角, 层名集合)"""
    pos = p.GetPosition()
    sz = p.GetSize()
    hx, hy = sz.x / MM / 2.0, sz.y / MM / 2.0
    try:
        rot = p.GetOrientationDegrees() % 180
    except Exception:
        rot = 0
    if 45 <= rot <= 135:
        hx, hy = hy, hx
    cx, cy = pos.x / MM, pos.y / MM
    lays = set()
    try:
        for l in p.GetLayerSet().Seq():
            lays.add(pcbnew.BOARD.GetStandardLayerName(l))
    except Exception:
        lays = set()
    try:
        if not lays:
            lays = {pcbnew.BOARD.GetStandardLayerName(p.GetLayer())}
    except Exception:
        lays = {"F.Cu"}
    return ([(cx - hx, cy - hy), (cx + hx, cy - hy),
             (cx + hx, cy + hy), (cx - hx, cy + hy)], lays)


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        return 2
    boardp, drcp = a[0], a[1]
    outf = None
    if "--out" in a:
        i = a.index("--out")
        if i + 1 < len(a):
            outf = a[i + 1]
    b = pcbnew.LoadBoard(boardp)

    # ── 收集所有铜 (带层) ──
    segs = []      # (net, rect, layer_name)
    vias = []      # (net, rect, "通孔")
    pads = []      # (net, ref.num, rect, layers)
    for t in b.GetTracks():
        s, e = t.GetStart(), t.GetEnd()
        if t.Type() == pcbnew.PCB_VIA_T:
            w = t.GetWidth(pcbnew.F_Cu) / MM
            h = w / 2.0
            p = s
            cx, cy = p.x / MM, p.y / MM
            vias.append((t.GetNetname(),
                         [(cx - h, cy - h), (cx + h, cy - h),
                          (cx + h, cy + h), (cx - h, cy + h)], "通孔"))
        else:
            r = GC.rect_from_seg((s.x / MM, s.y / MM), (e.x / MM, e.y / MM),
                                  t.GetWidth() / MM)
            if r:
                segs.append((t.GetNetname(), r, t.GetLayerName()))
    for f in b.GetFootprints():
        for p in f.Pads():
            r, lays = pad_rect(p)
            pads.append((p.GetNetname(), "%s.%s" % (f.GetReference(),
                                                    p.GetNumber()), r, lays))

    def dist_to_rect(r1, r2):
        return GC.rect_rect_dist(r1, r2)

    d = json.load(open(drcp, encoding="utf-8"))
    items = d.get("unconnected_items") or []
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

    lines = []
    print("═══ 分层版施工单: %s ═══" % boardp)
    print("═══ 未连接条目 %d 条 ═══" % len(items))
    n_wall = 0
    for it in items:
        its = it.get("items") or []
        if len(its) != 2:
            continue
        m0 = re.search(r"\[([^\]]+)\]", its[0].get("description") or "")
        m1 = re.search(r"\[([^\]]+)\]", its[1].get("description") or "")
        net = m0.group(1) if m0 else "?"
        if net != (m1.group(1) if m1 else ""):
            continue
        ends = []
        for sub in its:
            o = byu.get(sub.get("uuid"))
            if o is None:
                continue
            kind, obj = o
            if kind == "p":
                r, lays = pad_rect(obj)
                nm = "%s.%s" % (obj.GetParentFootprint().GetReference(),
                                obj.GetNumber())
                ends.append((obj.GetNetname(), nm, r, lays))
            else:
                s, e = obj.GetStart(), obj.GetEnd()
                r = GC.rect_from_seg((s.x / MM, s.y / MM), (e.x / MM, e.y / MM),
                                      obj.GetWidth() / MM)
                if r:
                    ends.append((obj.GetNetname(), "走线端", r,
                                 {obj.GetLayerName()}))
        for (pnet, nm, r, lays) in ends:
            wall = (1e9, "")
            other = (1e9, "")
            for (n2, r2, l2) in segs:
                if n2 == pnet or not n2:
                    continue
                dd = dist_to_rect(r, r2)
                if l2 in lays:
                    if dd < wall[0]:
                        wall = (dd, "%s[%s]" % (n2, l2))
                else:
                    if dd < other[0]:
                        other = (dd, "%s[%s](异层·不是墙)" % (n2, l2))
            for (n2, r2, l2) in vias:
                if n2 == pnet or not n2:
                    continue
                dd = dist_to_rect(r, r2)
                if dd < wall[0]:
                    wall = (dd, "%s[%s]" % (n2, l2))
                elif dd < other[0]:
                    other = (dd, "%s[%s](异层·不是墙)" % (n2, l2))
            ws = ("%6.3fmm" % wall[0]) if wall[0] < 1e8 else "   无  "
            os_ = ("%6.3fmm" % other[0]) if other[0] < 1e8 else "   无  "
            tag = "★墙" if wall[0] < CLEAR else "  "
            if wall[0] < CLEAR:
                n_wall += 1
            ln = ("  %s %-20s %-12s ⇒ ★同层异网铜 %s %-28s · 异层异网铜 %s"
                  % (tag, pnet, nm, ws, wall[1] or "-", os_))
            lines.append(ln)
            print(ln)
    print("\n── 端点共 %d 个 · 其中★真墙(同层异网铜 < %.2fmm) %d 个 ──"
          % (len(lines), CLEAR, n_wall))
    if outf:
        with open(outf, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        print("── 已写 %s" % outf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
