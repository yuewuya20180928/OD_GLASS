#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_lane_conflicts.py -- ★★找出【布局冲突清单】: 哪些网的焊盘被排在同一条走廊, 谁横穿, 挪哪个能解

★★★**★为什么要有这个 (★2026-11-09 18:3x)★★★**
  ★**已定位的病根 (★`FSIN_OUT` 的几何真相)**: ★**该网两个焊盘 `R_SER_FSIN`(93.300,46.600) 与
    `TP_FSIN`(93.500,49.600) 几乎同 x ⇒ ★★**两点之间的垂线是【唯一通道】⇒ ★★**而 `VDD_3V3_IO`
    恰在 y=47.7~48.2 横穿那条垂线 ⇒ ⇒ ★★**A\\* 怎么走都躲不开** ★★
  ⇒ ★★**⇒ 这是【布局级冲突】, 不是算法不够强 ⇒ ⇒ 【挪焊盘】是正解, 而不是【更强的 A\\*】** ★★
  ⇒ ★★**⇒ 本脚本把【这一类】问题在全板 45 条未连接上系统性地找出来 ⇒ ★★**给出可执行的工作单** ★★

★**判据 (★全是几何, ★不含猜测)**
  ★**① 走廊 = 两焊盘中心之间的直线** (★该网必须走这条路才能连上)
  ★**② 横穿 = 异网铜段与该走廊【真正相交】(★不是靠近)**
  ★**③ 挪得动吗 = 把第二个焊盘【垂直于走廊】平移 d ⇒ 重测是否还有横穿**
    ⇒ ★**给出"最小可行位移" ⇒ ⇒ 这就是给布局/占道的工作单**

用法: bash state/pcbnew_py.sh state/probe_lane_conflicts.py [板] [DRC.json] [--out <txt>]
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("PCB_LAYERS", "8")
import pcbnew  # noqa: E402

MM = 1000000.0


def cross(a, b, c, d):
    """线段 ab 与 cd 是否真正相交 (★返回 True/False)"""
    def o(p, q, r):
        v = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        return 0 if abs(v) < 1e-12 else (1 if v > 0 else -1)
    o1, o2 = o(a, b, c), o(a, b, d)
    o3, o4 = o(c, d, a), o(c, d, b)
    return o1 != o2 and o3 != o4


def main():
    boardp = sys.argv[1] if len(sys.argv) > 1 else "HW/PCB/demo_mainboard.kicad_pcb"
    drcp = sys.argv[2] if len(sys.argv) > 2 else "/tmp/_drc45.json"
    outp = None
    if "--out" in sys.argv:
        outp = sys.argv[sys.argv.index("--out") + 1]

    b = pcbnew.LoadBoard(boardp)
    d = json.load(open(drcp, encoding="utf-8"))
    unc_nets = set()
    for it in (d.get("unconnected_items") or []):
        for m in re.finditer(r"\[([A-Za-z0-9_]+)\]", json.dumps(it, ensure_ascii=False)):
            unc_nets.add(m.group(1))

    # ★焊盘按网
    pads = {}
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname():
                pads.setdefault(p.GetNetname(), []).append(
                    (fp.GetReference() + "." + p.GetNumber(), p.GetPosition().x / MM, p.GetPosition().y / MM,
                     set(b.GetLayerName(l) for l in [p.GetLayer()])))
    # ★走线 (★按层)
    tracks = []
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            continue
        s, e = t.GetStart(), t.GetEnd()
        tracks.append((t.GetNetname(), b.GetLayerName(t.GetLayer()),
                       (s.x / MM, s.y / MM), (e.x / MM, e.y / MM)))
    lay_of = {}
    for l in b.GetEnabledLayers().Seq():
        lay_of[b.GetLayerName(l)] = l

    rows = []
    for net in sorted(unc_nets):
        pl = pads.get(net) or []
        if len(pl) < 2:
            continue
        for i in range(len(pl)):
            for j in range(i + 1, len(pl)):
                (_, ax, ay, _), (_, bx, by, _) = pl[i], pl[j]
                a, bp = (ax, ay), (bx, by)
                if math.hypot(bx - ax, by - ay) < 1.0:
                    continue
                hit = []
                for (tn, tl, s, e) in tracks:
                    if tn == net:
                        continue
                    if cross(a, bp, s, e):
                        hit.append((tn, tl, s, e))
                if not hit:
                    continue
                # ★最小可行垂直位移: 把 b 点垂直于走廊平移 d, 重测
                vx, vy = bx - ax, by - ay
                L = math.hypot(vx, vy)
                nx, ny = -vy / L, vx / L
                best = None
                for d in (0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 3.0):
                    for sgn in (1, -1):
                        nb = (bx + sgn * d * nx, by + sgn * d * ny)
                        if not any(cross(a, nb, s2, e2) for (_tn, _tl, s2, e2) in hit):
                            best = (d, sgn, nb)
                            break
                    if best:
                        break
                rows.append((net, pl[i][0], pl[j][0], round(L, 2),
                             sorted(set(h[0] for h in hit)),
                             ("%.1fmm %s" % (best[0], "左" if best[1] > 0 else "右")) if best else "★挪 3mm 内无解",
                             best[2] if best else None))

    out = ["★布局冲突清单 (★两焊盘走廊被异网铜横穿 ⇒ A\\* 躲不开 ⇒ 只能挪焊盘)"]
    out.append("★板: %s   ★未连接涉及网: %d" % (boardp, len(unc_nets)))
    out.append("")
    out.append("%-18s %-16s %-16s %-7s %-28s %s" % ("网", "焊盘A", "焊盘B", "走廊长", "横穿它的网", "最小可行挪动"))
    for (net, pa, pb, L, hs, mv, _) in rows:
        out.append("%-18s %-16s %-16s %-7.2f %-28s %s" % (net, pa, pb, L, ",".join(hs[:3]), mv))
    out.append("")
    out.append("★⇒ %d 个网存在【走廊被横穿】的布局冲突 ⇒ ⇒ 【挪焊盘】比【改路由器】便宜且直接" % len(rows))
    text = "\n".join(out)
    if outp:
        open(outp, "w", encoding="utf-8").write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
