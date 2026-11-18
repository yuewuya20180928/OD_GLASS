#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_stub_wall.py -- ★★★**量清"成品板补段"到底被什么挡住 (2026-11-06 05:3x 实测)**

★★★**为什么要有这个脚本 (机器实测链)**:
  ① 官方板 57 项未连接
  ② 纯 A* 补段 (`state/fix_unconnected_astar.py`) ⇒ **0.25mm 网格补上 0 条 · 0.125mm 网格也补上 0 条**
     ⇒ ⇒ ★**网格分辨率不是瓶颈** (★0.125mm 两轮失败构成完全一样)
  ③ 失败构成: 15 条"距离超阈值(>12mm)" + 10 条"**stub 净距不过**"
     ⇒ ⇒ ★**卡住的是"从焊盘出来的第一段" (escape stub), 不是路径搜索**
  ④ ⇒ ★**必须逐端点量: 这个焊盘到最近的异网铜有多远?** ⇒ 才知道是"能挤过去但方向不对" 还是"物理无解"

★★**输出 (每条未连接项一行)**:
    net · 两头间距 · 端A(器件.脚号 @x,y, 焊盘尺寸, 层) · 端B(...) ·
    端A到最近异网铜的距离 + 是谁(网名/类型) · 端B同理
  ⇒ ★**"最近的异网铜 < 0.2+半宽" ⇒ 这就是墙** ⇒ 改 footprint / 改布局, 改路由算法没用

用法: bash state/pcbnew_py.sh state/diag_stub_wall.py <板> <DRC.json> [--out <json>]
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

MM = 1e6


def seg_point_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        return 2
    boardp, drcp = a[0], a[1]
    outp = None
    if "--out" in a:
        outp = a[a.index("--out") + 1]

    board = pcbnew.LoadBoard(boardp)
    byu = {}
    for t in board.GetTracks():
        try:
            byu[t.m_Uuid.AsString()] = ("track", t)
        except Exception:
            pass
    for f in board.GetFootprints():
        for p in f.Pads():
            try:
                byu[p.m_Uuid.AsString()] = ("pad", p)
            except Exception:
                pass

    # ── 收齐所有铜 (异网) 的粗表, 供最近距离查询 ──
    tracks = []   # (net, x1,y1,x2,y2, width, layer)
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            continue
        s, e = t.GetStart(), t.GetEnd()
        tracks.append((t.GetNetname(), s.x / MM, s.y / MM, e.x / MM, e.y / MM,
                       t.GetWidth() / MM, t.GetLayer()))
    pads = []     # (net, cx,cy, halfw, halfh, ref)
    for f in board.GetFootprints():
        for p in f.Pads():
            pos = p.GetPosition()
            sz = p.GetSize()
            pads.append((p.GetNetname(), pos.x / MM, pos.y / MM,
                         sz.x / MM / 2.0, sz.y / MM / 2.0,
                         "%s.%s" % (f.GetReference(), p.GetNumber())))

    def nearest_other(net, cx, cy, halfw=0.125):
        """★最近的异网铜 (返回 (距离, 说明))"""
        best = (1e9, "")
        for (n, x1, y1, x2, y2, w, ly) in tracks:
            if n == net:
                continue
            d = seg_point_dist(cx, cy, x1, y1, x2, y2) - w / 2.0
            if d < best[0]:
                best = (d, "走线[%s]" % n)
        for (n, px, py, hw, hh, ref) in pads:
            if n == net:
                continue
            dx = max(abs(cx - px) - hw, 0.0)
            dy = max(abs(cy - py) - hh, 0.0)
            d = math.hypot(dx, dy)
            if d < best[0]:
                best = (d, "焊盘[%s %s]" % (ref, n))
        return best

    d = json.load(open(drcp, encoding="utf-8"))
    rows = []
    for it in (d.get("unconnected_items") or []):
        its = it.get("items") or []
        if len(its) != 2:
            rows.append({"net": "?", "note": "条目不是两两相连", "n_items": len(its)})
            continue
        p0 = its[0].get("pos") or {}
        p1 = its[1].get("pos") or {}
        dist = math.hypot(p0.get("x", 0) - p1.get("x", 0),
                          p0.get("y", 0) - p1.get("y", 0))
        m0 = re.search(r"\[([^\]]+)\]", its[0].get("description") or "")
        m1 = re.search(r"\[([^\]]+)\]", its[1].get("description") or "")
        net = m0.group(1) if m0 else "?"
        net2 = m1.group(1) if m1 else "?"
        ends = []
        for it2 in (its[0], its[1]):
            o = byu.get(it2.get("uuid"))
            if o is None:
                ends.append({"desc": (it2.get("description") or "")[:60],
                             "pos": [p0.get("x"), p0.get("y")]})
                continue
            kind, obj = o
            if kind == "pad":
                pos = obj.GetPosition()
                sz = obj.GetSize()
                fp = obj.GetParentFootprint()
                ref = "%s.%s" % (fp.GetReference(), obj.GetNumber())
                cx, cy = pos.x / MM, pos.y / MM
                hw, hh = sz.x / MM / 2.0, sz.y / MM / 2.0
            else:
                s, e = obj.GetStart(), obj.GetEnd()
                cx, cy = s.x / MM, s.y / MM
                hw = hh = 0.0
                ref = "走线"
            dd, who = nearest_other(net, cx, cy)
            ends.append({"desc": ref, "pos": [round(cx, 3), round(cy, 3)],
                         "size": [round(hw * 2, 3), round(hh * 2, 3)],
                         "near_other_mm": round(dd, 3), "near_other": who,
                         "wall": bool(dd < 0.2 + max(hw, hh))})
        rows.append({"net": net, "net2": net2, "dist": round(dist, 3),
                     "ends": ends,
                     "wall": any(e.get("wall") for e in ends)})

    wall = [r for r in rows if r.get("wall")]
    print("═══ 未连接 %d 条 · 其中端点被异网铜挡住(<0.2+半宽)的 %d 条 ═══"
          % (len(rows), len(wall)))
    for r in sorted(rows, key=lambda x: (not x.get("wall"), x.get("dist", 999))):
        if "ends" not in r:
            print("  ★%-16s %s" % (r.get("net"), r.get("note")))
            continue
        e = r["ends"]
        print("  %s %-16s 间距 %7.3fmm" % ("◆墙" if r.get("wall") else "  ",
                                          r["net"], r["dist"]))
        for x in e:
            print("        %-14s @(%8.3f,%8.3f) 尺寸%s ⇒ 最近异网铜 %6.3fmm %s"
                  % (x.get("desc"), x["pos"][0], x["pos"][1], x.get("size"),
                     x.get("near_other_mm", -1), x.get("near_other", "")))
    if outp:
        json.dump(rows, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("── 已写 %s" % outp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
