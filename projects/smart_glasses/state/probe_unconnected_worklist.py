#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_unconnected_worklist.py -- ★**官方板未连接清单 → 逐网逐脚工作表**

★**为什么需要它 (11-06 04:3x)**: G1 要 `unconnected=0`。官方板有 57 项, 但它们**不是同一种病**:
  · 整网无铜 (一根铜都没长)      ⇒ 要整条重新布
  · 三脚网只通局部 (差最后一脚)  ⇒ ★**只补那一段**
  · 端点缝 (差 0.3~5mm 一小段)   ⇒ ★**只补那一小段**
⇒ ★**不分类就开工 ⇒ 会把"补一段"当成"重布整网" ⇒ 白干**

★**网名必须精确解析 (★踩过的坑)**: DRC JSON 里是 `Pad 30 [LIGHT_5V] of CONN_CAM`
  ⇒ ★**必须从方括号里取网名再精确比对** ⇒ ★**不能用子串包含** (`CAM_RESET_N` 含 `RESET_N` ⇒ 子串会误判!)

用法:
  bash state/pcbnew_py.sh state/probe_unconnected_worklist.py <板> <官方DRC.json> [--out 文件]
"""
import sys
import math
import json
import re
import collections
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
    pads, segs, vias = [], [], []
    for f in b.GetFootprints():
        for p in f.Pads():
            q = p.GetPosition()
            sz = p.GetSize()
            pads.append(dict(ref=f.GetReference(), num=str(p.GetNumber()),
                             net=p.GetNetname(), x=q.x / MM, y=q.y / MM,
                             w=sz.x / MM, h=sz.y / MM))
    for t in b.GetTracks():
        s, e = t.GetStart(), t.GetEnd()
        if t.Type() == pcbnew.PCB_VIA_T:
            vias.append(dict(net=t.GetNetname(), x=s.x / MM, y=s.y / MM,
                             w=t.GetWidth(pcbnew.F_Cu) / MM))
        else:
            segs.append(dict(net=t.GetNetname(), layer=t.GetLayerName(),
                              x1=s.x / MM, y1=s.y / MM, x2=e.x / MM, y2=e.y / MM,
                              w=t.GetWidth() / MM))
    return pads, segs, vias


def nets_from_drc(path):
    """★从 DRC JSON 里精确抽网名 (★方括号取值, 不做子串匹配)"""
    d = json.load(open(path, encoding="utf-8"))
    items = d.get("unconnected_items", [])
    out = {}
    for it in items:
        s = json.dumps(it, ensure_ascii=False)
        for m in re.finditer(r"Pad\s+\S+\s+\[([^\]]+)\]", s):
            nm = m.group(1)
            out.setdefault(nm, []).append(s)
    return out, items


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        return 2
    board, drc = a[0], a[1]
    outf = None
    if "--out" in a:
        i = a.index("--out")
        if len(a) > i + 1:
            outf = a[i + 1]
    pads, segs, vias = load(board)
    nets, items = nets_from_drc(drc)
    print("═══ 板: %s ═══" % board)
    print("═══ DRC 未连接条目: %d 条 ⇒ 涉及 %d 个网 ═══" % (len(items), len(nets)))
    lines = []
    cnt = {"整网无铜": 0, "局部未通": 0, "端点缝": 0}
    for nm in sorted(nets):
        np_ = [p for p in pads if p["net"] == nm]
        ns = [s for s in segs if s["net"] == nm]
        nv = [v for v in vias if v["net"] == nm]
        length = sum(math.hypot(s["x2"] - s["x1"], s["y2"] - s["y1"]) for s in ns)
        rows = []
        for p in np_:
            d_same = 1e9
            for s in ns:
                dd = max(0.0, pt_seg_dist(p["x"], p["y"], s["x1"], s["y1"], s["x2"], s["y2"]) - s["w"] / 2.0)
                d_same = min(d_same, dd)
            for v in nv:
                d_same = min(d_same, max(0.0, math.hypot(p["x"] - v["x"], p["y"] - v["y"]) - v["w"] / 2.0))
            d_other, blocker = 1e9, ""
            for s in segs:
                if s["net"] == nm or not s["net"]:
                    continue
                dd = max(0.0, pt_seg_dist(p["x"], p["y"], s["x1"], s["y1"], s["x2"], s["y2"]) - s["w"] / 2.0)
                if dd < d_other:
                    d_other, blocker = dd, "%s[%s]" % (s["net"], s["layer"])
            for v in vias:
                if v["net"] == nm or not v["net"]:
                    continue
                dd = max(0.0, math.hypot(p["x"] - v["x"], p["y"] - v["y"]) - v["w"] / 2.0)
                if dd < d_other:
                    d_other, blocker = dd, "%s[VIA]" % v["net"]
            rows.append((p, d_same, d_other, blocker))
        connected = sum(1 for r in rows if r[1] <= 0.30)
        if len(ns) == 0 and len(nv) == 0:
            kind = "整网无铜"
            cnt["整网无铜"] += 1
        elif connected == len(rows):
            kind = "★铜全在但仍报未连接(★口径差异)"
            cnt["端点缝"] += 1
        elif connected == 0:
            kind = "局部未通"
            cnt["局部未通"] += 1
        else:
            kind = "局部未通"
            cnt["局部未通"] += 1
        miss = [(r[0]["ref"] + "." + r[0]["num"], r[0]["x"], r[0]["y"], r[1], r[2], r[3])
                for r in rows if r[1] > 0.30]
        tag = "%-24s 焊盘%2d 通%2d 段%4d 孔%3d 长%7.2fmm ⇒ %s" % (
            nm, len(rows), connected, len(ns), len(nv), length, kind)
        print("── " + tag)
        lines.append(tag)
        for (pn, x, y, ds, do, bl) in miss:
            sub = "     ★缺 %-22s (%7.2f,%7.2f) 离同网铜 %7.3fmm 别网铜 %6.3fmm %s" % (
                pn, x, y, ds, do, ("[%s]" % bl if do <= 0.45 else ""))
            print(sub)
            lines.append(sub)
    print("── 汇总: 整网无铜 %d · 局部未通 %d · 端点缝 %d (合计 %d 网)" %
          (cnt["整网无铜"], cnt["局部未通"], cnt["端点缝"], len(nets)))
    lines.append("── 汇总: 整网无铜 %d · 局部未通 %d · 端点缝 %d (合计 %d 网)" %
                  (cnt["整网无铜"], cnt["局部未通"], cnt["端点缝"], len(nets)))

    # ══════ ★★★第 2 部分: 按"两两 ratsnest 端点距离"分类 (★★这才是施工单) ══════
    # ★**DRC JSON 里每条未连接都给出了两头的确切焊盘/走线 + 坐标**
    #   ⇒ ★**按两头距离分三类**: <2mm = ★**同网相邻焊盘没互联 (缝合遗漏, 白捡)**
    #   · 2~10mm = ★**差最后一小段 (便宜)** · >10mm = ★**真缺一整条腿 (贵, 多是 DSI/CSI)**
    # ★**★踩过的坑**: 网名必须从 `Pad N [NET] of REF` 的方括号里取 ⇒ ★**不能用子串匹配**
    #   (`CAM_RESET_N` 含 `RESET_N` ⇒ 子串会把 RESET_N 误判成未连接!)
    print("")
    print("═══ 第 2 部分: 57 项按【两头距离】分类 (★施工单) ═══")
    rows = []
    cats = collections.Counter()
    for it in items:
        its = it.get("items", [])
        if len(its) != 2:
            cats["★条目不是两两相连(需单独看)"] += 1
            continue
        a, b = its[0], its[1]
        pa, pb = a.get("pos"), b.get("pos")
        if not pa or not pb:
            cats["★无坐标"] += 1
            continue
        dist = math.hypot(pa["x"] - pb["x"], pa["y"] - pb["y"])
        ma = re.search(r"\[([^\]]+)\]", a.get("description", ""))
        mb = re.search(r"\[([^\]]+)\]", b.get("description", ""))
        na = ma.group(1) if ma else "?"
        nb = mb.group(1) if mb else "?"
        if dist < 2.0:
            tag = "★邻近未互联(<2mm, 白捡)"
        elif dist < 10.0:
            tag = "近距(2~10mm, 便宜)"
        else:
            tag = "远距(>10mm, 真缺腿)"
        cats[tag] += 1
        rows.append((dist, na, nb, a.get("description", ""), b.get("description", ""), tag))
    rows.sort()
    for k, v in cats.most_common():
        print("    · %-26s %d 条" % (k, v))
    lines.append("── 第2部分分类: " + " · ".join("%s=%d" % (k, v) for k, v in cats.most_common()))
    print("  ★最便宜的前 12 条:")
    for dist, na, nb, da, db, tag in rows[:12]:
        print("    ★%7.3fmm %-16s ⇄ %-16s | %s" % (dist, na, nb, da))
        lines.append("    ★%7.3fmm %-16s ⇄ %-16s | %s" % (dist, na, nb, da))
    print("  ★最贵的 10 条:")
    for dist, na, nb, da, db, tag in rows[-10:]:
        print("    ★%8.3fmm %-16s ⇄ %-16s | %s" % (dist, na, nb, da))
        lines.append("    ★%8.3fmm %-16s ⇄ %-16s | %s" % (dist, na, nb, da))
    if outf:
        with open(outf, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print("── 存证: %s" % outf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
