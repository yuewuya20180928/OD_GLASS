#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_escape_feasibility.py —— ★★★【★★每个未连接端点, 按【出脚方向】算余量 ⇒ ★★回答"物理上还剩几条不可能"★★】★★★

★★★**★为什么要有这个 (★2026-11-10 02:5x 实测)★★★**
  ★**起因**: ★**`classify_unc.py` 的 B1 桶判据 = `ep.startswith("J_SOM_P")` (★设备名匹配★)**
    ⇒ ★★**那句"需线宽 0.15mm (要板厂)"是写死的文案, 不是算出来的** ⇒ ★★
    ★★**⇒ 老板 11-09 已批 0.15mm 为设计线宽 ⇒ ⇒ B1 那 14 条【不是"等板厂", 是"路由器没走出来"】★★** ★★
  ★★**⇒ 本工具把判据换成【几何 + 方向 + 当前线宽】: ★★每个端点枚举 4 个方向 × 4 个出脚长度,
    算【出脚直道 vs 异网铜】的净距余量 ⇒ ⇒ 直接给出: ★★哪些端点【物理可行】/【物理不可能】★★** ★★★
  ★★**★关键: 【同一个"最近异网铜距离", 沿排方向是死路, 垂直方向是活路】⇒ ⇒ 只看距离不看方向 ⇒ 结论必错★★** ★★★
  ★★**★⇒ 输出还顺带给一条【能不能只靠 0.15mm 就全通】的答案 ⇒ ⇒ 这决定"要不要做 pair-aware 改造"★★** ★★★

★★★**★口径 (★全部复用 `probe_unconnected_worklist_v2.py` / `geom_clear.py`, ★不自造几何)★★★**
  · 焊盘 → **矩形** (★按旋转角交换长宽★)
  · 走线段 → **矩形** (`geom_clear.rect_from_seg`)
  · 过孔 → **矩形 + 全层** (★通孔 ⇒ 每层都算★)
  · 净距 = `geom_clear.rect_rect_dist` (★真几何, ★不是包围盒近似★)
  · ★**只算异网铜** (★同网铜不算挡路★) · ★**只算同层** (★异层异网铜不是墙★)

用法:
  bash state/pcbnew_py.sh state/probe_escape_feasibility.py <板> <DRC.json> [--out <txt>]
  ★**默认同时算 W=0.20 与 W=0.15 两条线** (★对照: 0.20 = 旧设计线宽 / 0.15 = 现在的设计线宽★)
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
ESC_LENS = (1.20, 0.90, 0.60, 0.40)
DIRS = ((0, 1), (0, -1), (1, 0), (-1, 0))
DIR_NAME = {(0, 1): "↑(0,+1)", (0, -1): "↓(0,-1)",
            (1, 0): "→(+1,0)", (-1, 0): "←(-1,0)"}
WIDTHS = (0.20, 0.15)


def pad_rect(p):
    """★焊盘 → (矩形四角, 层名集合) ★★与 v2 探针同源口径 (★不自造★)"""
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
    if not lays:
        try:
            lays = {pcbnew.BOARD.GetStandardLayerName(p.GetLayer())}
        except Exception:
            lays = {"F.Cu"}
    return ([(cx - hx, cy - hy), (cx + hx, cy - hy),
             (cx + hx, cy + hy), (cx - hx, cy + hy)], lays)


def rect_center(r):
    xs = [p[0] for p in r]
    ys = [p[1] for p in r]
    return (sum(xs) / 4.0, sum(ys) / 4.0)


def _bbox_gap(b1, b2):
    """★两个包围盒之间的【粗略最小距离】(★轴对齐 ⇒ 精确, ★但比多边形距离便宜得多)"""
    dx = max(0.0, b1[0] - b2[2], b2[0] - b1[2])
    dy = max(0.0, b1[1] - b2[3], b2[1] - b1[3])
    return math.hypot(dx, dy)


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

    # ── 收集铜 (★异网 + 同网都收, ★后面按网过滤★) ──
    segs = []      # (net, rect, layer)
    vias = []      # (net, rect) ★通孔 ⇒ 全层
    for t in b.GetTracks():
        s, e = t.GetStart(), t.GetEnd()
        if t.Type() == pcbnew.PCB_VIA_T:
            w = t.GetWidth(pcbnew.F_Cu) / MM
            h = w / 2.0
            cx, cy = s.x / MM, s.y / MM
            vias.append((t.GetNetname(),
                         [(cx - h, cy - h), (cx + h, cy - h),
                          (cx + h, cy + h), (cx - h, cy + h)]))
        else:
            r = GC.rect_from_seg((s.x / MM, s.y / MM), (e.x / MM, e.y / MM),
                                  t.GetWidth() / MM)
            if r:
                segs.append((t.GetNetname(), r, t.GetLayerName()))
    pads = []      # (net, ref.num, rect, layers)
    for f in b.GetFootprints():
        for p in f.Pads():
            r, lays = pad_rect(p)
            pads.append((p.GetNetname(), "%s.%s" % (f.GetReference(),
                                                    p.GetNumber()), r, lays))

    # ── 端点表 (按 uuid 找) ──
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

    # ★★**★预计算包围盒 (★性能: ★每个铜图元只算一次, ★后面只查表★)** ★★
    def _bb(r):
        return (min(p[0] for p in r), min(p[1] for p in r),
                max(p[0] for p in r), max(p[1] for p in r))
    segs_bb = [(_bb(r2),) + (n2, r2, lay2)[0:0] + (n2, r2, lay2) for (n2, r2, lay2) in segs]
    segs_bb = [(bb, n2, r2, lay2) for (n2, r2, lay2), bb in
               zip(segs, [_bb(r2) for (n2, r2, lay2) in segs])]
    vias_bb = [(bb, n2, r2) for (n2, r2), bb in
               zip(vias, [_bb(r2) for (n2, r2) in vias])]
    pads_bb = [(bb, n2, nm2, r2, lays2) for (n2, nm2, r2, lays2), bb in
               zip(pads, [_bb(r2) for (n2, nm2, r2, lays2) in pads])]

    d = json.load(open(drcp, encoding="utf-8"))
    items = d.get("unconnected_items") or []

    lines = []
    def out(s=""):
        lines.append(s)

    out("═══ 出脚可行性 (按方向 × 按线宽) ═══")
    out("板 = %s" % boardp)
    out("未连接条目 = %d" % len(items))
    out("线宽候选 = %s mm · 净距要求 = %.2f mm" % (", ".join("%.2f" % w for w in WIDTHS), CLEAR))
    out("")

    stat = {w: {"ok": 0, "dead": 0} for w in WIDTHS}
    n_end = 0
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
            n_end += 1
            cx, cy = rect_center(r)
            # ★★**本端点所在层** (★多层焊盘 ⇒ 每层各算一遍, ★取最好的★)
            out("── %s @ %s (%.3f, %.3f) 层=%s" % (net, nm, cx, cy,
                                                 "/".join(sorted(lays)) or "?"))
            for w in WIDTHS:
                best = None     # (margin, dir, ln, blocker)
                for (dx, dy) in DIRS:
                    for ln in ESC_LENS:
                        ex, ey = cx + dx * ln, cy + dy * ln
                        sr = GC.rect_from_seg((cx, cy), (ex, ey), w)
                        if not sr:
                            continue
                        mind, blocker = 1e9, ""
                        # ★★**★包围盒预筛 (★性能: ★原版 2800 万次 rect_rect_dist ⇒ 跑不完★)★★**
                        #   ★**先算【包围盒到包围盒】的粗距, ★粗距 > 当前最优值就跳过 ⇒ ⇒ 只对近处的做真几何** ★★
                        sb = (min(p[0] for p in sr), min(p[1] for p in sr),
                              max(p[0] for p in sr), max(p[1] for p in sr))
                        for (bb2, n2, r2, lay2) in segs_bb:
                            if n2 == net:
                                continue
                            if lay2 not in lays:
                                continue
                            if _bbox_gap(sb, bb2) >= mind:
                                continue
                            dd = GC.rect_rect_dist(sr, r2)
                            if dd < mind:
                                mind, blocker = dd, "%s[%s]" % (n2, lay2)
                        for (bb2, n2, r2) in vias_bb:
                            if n2 == net:
                                continue
                            if _bbox_gap(sb, bb2) >= mind:
                                continue
                            dd = GC.rect_rect_dist(sr, r2)
                            if dd < mind:
                                mind, blocker = dd, "%s[通孔]" % n2
                        for (bb2, n2, nm2, r2, lays2) in pads_bb:
                            if n2 == net:
                                continue
                            if not (lays & lays2):
                                continue
                            if _bbox_gap(sb, bb2) >= mind:
                                continue
                            dd = GC.rect_rect_dist(sr, r2)
                            if dd < mind:
                                mind, blocker = dd, "%s[%s]" % (n2, nm2)
                        margin = mind - CLEAR
                        if best is None or margin > best[0]:
                            best = (margin, (dx, dy), ln, blocker)
                if best is None:
                    out("   ★W=%.2f ⇒ 无方向可试" % w)
                    stat[w]["dead"] += 1
                    continue
                mg, (dx, dy), ln, blocker = best
                tag = "✔物理可行" if mg >= -1e-9 else "✘物理不可能"
                out("   ★W=%.2f 最优方向 %s 长 %.2f ⇒ 余量 %+.3fmm (★最近的异网铜 %s 距离 %.3f★) ⇒ %s"
                    % (w, DIR_NAME[(dx, dy)], ln, mg, blocker, mg + CLEAR, tag))
                if mg >= -1e-9:
                    stat[w]["ok"] += 1
                else:
                    stat[w]["dead"] += 1
            out("")

    out("═══════ 汇总 ═══════")
    out("端点数 = %d" % n_end)
    for w in WIDTHS:
        out("★W=%.2f ⇒ 物理可行 %d / 物理不可能 %d" % (w, stat[w]["ok"], stat[w]["dead"]))
    out("")
    out("★★⇒ 【只靠线宽就能救的】= 物理可行端点数; 【物理不可能】= 必须改几何(挪焊盘/改封装/改布局)")
    text = "\n".join(lines)
    if outf:
        open(outf, "w", encoding="utf-8").write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
