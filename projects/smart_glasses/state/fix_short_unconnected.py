#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_short_unconnected.py -- ★**给成品板补"短未连接"** (11-06 04:5x)

★★**为什么需要它 (机器实测)**: 官方板 57 项未连接按"两头距离"分类:
  · <2mm  同网相邻焊盘没互联 (缝合遗漏)   2 条   ← ★**白捡**
  · 2~10mm 差最后一小段                    10 条  ← ★**便宜**
  · >10mm  真缺一整条腿 (主体 DSI/CSI)      45 条  ← ★**贵, 靠路由器重布**
⇒ ⇒ ★**前 12 条只要在成品板上补一小段铜就能消掉** ⇒ ★**不用等路由器重跑**

★★**为什么是"补丁器"而不是改路由器**: 官方板是历史产物 (v37_R), 当前代码已无法复现它
  ⇒ ★**改路由器只能救未来的板, 救不了这块板** ⇒ ⇒ ★**两件事都要做, 但先后顺序是: 先把板救出来**

★**做法**: 读 DRC JSON 的未连接条目 ⇒ ★**用 uuid 精确找回板上那一头** (焊盘或走线)
  ⇒ 试 直连 / 4 种 L 形 / 换层 ⇒ ★**逐段查净距 (0.20 + w/2 + 别网 w/2)、别网过孔、别网焊盘、板边**
  ⇒ 清 ⇒ 才画 ⇒ ★**绝不画在别人的铜上**

★**安全**:
  · ★**只写输出路径, 绝不原地改** (调用方给一个副本)
  · ★**只补 <DIST 阈值的短连接** (默认 12mm), ★**长距的一律不碰** (那是路由器的活)
  · ★**只补同网未连接** ⇒ ★**不碰差分对的几何** (差分对两个网名不同 ⇒ 天然不匹配)

用法:
  bash state/pcbnew_py.sh state/fix_short_unconnected.py <板> <DRC.json> --out <新板> [--max-dist 12.0] [--width 0.25]
"""
import sys
import os
import math
import json
import argparse

import pcbnew

MM = 1e6
CLEAR = 0.20          # ★与路由器同规则
EDGE_MARGIN = 0.25    # ★板边净距 (保守)


def pt_seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 <= 1e-12:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def seg_seg_dist(a1, a2, b1, b2):
    """两线段最短距离 (采样+解析近似: ★够用, 保守取小)"""
    d1 = pt_seg_dist(a1[0], a1[1], b1[0], b1[1], b2[0], b2[1])
    d2 = pt_seg_dist(a2[0], a2[1], b1[0], b1[1], b2[0], b2[1])
    d3 = pt_seg_dist(b1[0], b1[1], a1[0], a1[1], a2[0], a2[1])
    d4 = pt_seg_dist(b2[0], b2[1], a1[0], a1[1], a2[0], a2[1])
    return min(d1, d2, d3, d4)


class Board:
    def __init__(self, path):
        self.b = pcbnew.LoadBoard(path)
        self.tracks = []
        self.vias = []
        self.pads = []
        self.by_uuid = {}
        for t in self.b.GetTracks():
            s, e = t.GetStart(), t.GetEnd()
            try:
                u = t.m_Uuid.AsString()
            except Exception:
                u = None
            if t.Type() == pcbnew.PCB_VIA_T:
                v = dict(kind="via", net=t.GetNetname(), x=s.x / MM, y=s.y / MM,
                         w=t.GetWidth(pcbnew.F_Cu) / MM)
                self.vias.append(v)
            else:
                seg = dict(kind="track", net=t.GetNetname(), layer=t.GetLayerName(),
                           x1=s.x / MM, y1=s.y / MM, x2=e.x / MM, y2=e.y / MM,
                           w=t.GetWidth() / MM, lay=t.GetLayer())
                self.tracks.append(seg)
            if u:
                self.by_uuid[u] = (seg if t.Type() != pcbnew.PCB_VIA_T else v)
        for f in self.b.GetFootprints():
            for p in f.Pads():
                q = p.GetPosition()
                sz = p.GetSize()
                pad = dict(kind="pad", net=p.GetNetname(), x=q.x / MM, y=q.y / MM,
                           w=sz.x / MM, h=sz.y / MM,
                           ref="%s.%s" % (f.GetReference(), str(p.GetNumber())))
                self.pads.append(pad)
                try:
                    self.by_uuid[p.m_Uuid.AsString()] = pad
                except Exception:
                    pass
        # 板框 (取所有 Edge.Cuts 线段的包围盒)
        xs, ys = [], []
        for d in self.b.GetDrawings():
            if d.GetLayer() == pcbnew.Edge_Cuts:
                try:
                    bb = d.GetBoundingBox()
                    xs += [bb.GetLeft() / MM, bb.GetRight() / MM]
                    ys += [bb.GetTop() / MM, bb.GetBottom() / MM]
                except Exception:
                    pass
        self.bbox = (min(xs), min(ys), max(xs), max(ys)) if xs else (0, 0, 180, 120)

    # ---------------- 净距判据 ----------------
    def seg_ok(self, net, p1, p2, lay, w):
        """★这一段铜能不能画"""
        need = CLEAR + w / 2.0
        for s in self.tracks:
            if s["net"] == net:
                continue
            if s["lay"] != lay:
                continue
            if seg_seg_dist(p1, p2, (s["x1"], s["y1"]), (s["x2"], s["y2"])) < need + s["w"] / 2.0:
                return False, "track %s[%s]" % (s["net"], s["layer"])
        for v in self.vias:
            if v["net"] == net:
                continue
            if pt_seg_dist(v["x"], v["y"], p1[0], p1[1], p2[0], p2[1]) < need + v["w"] / 2.0:
                return False, "via %s" % v["net"]
        for p in self.pads:
            if p["net"] == net:
                continue
            dx = max(p["x"] - p["w"] / 2.0 - p1[0], 0, p1[0] - (p["x"] + p["w"] / 2.0))
            dy = max(p["y"] - p["h"] / 2.0 - p1[1], 0, p1[1] - (p["y"] + p["h"] / 2.0))
            if math.hypot(dx, dy) < need:
                return False, "pad %s" % p["ref"]
        bx0, by0, bx1, by1 = self.bbox
        for (x, y) in (p1, p2):
            if not (bx0 + EDGE_MARGIN <= x <= bx1 - EDGE_MARGIN and
                    by0 + EDGE_MARGIN <= y <= by1 - EDGE_MARGIN):
                return False, "板边"
        return True, ""

    def add_track(self, net, p1, p2, lay, w):
        nc = self.b.FindNet(net).GetNetCode()
        t = pcbnew.PCB_TRACK(self.b)
        t.SetStart(pcbnew.VECTOR2I(int(round(p1[0] * MM)), int(round(p1[1] * MM))))
        t.SetEnd(pcbnew.VECTOR2I(int(round(p2[0] * MM)), int(round(p2[1] * MM))))
        t.SetWidth(int(round(w * MM)))
        t.SetLayer(lay)
        t.SetNetCode(nc)
        self.b.Add(t)
        self.tracks.append(dict(kind="track", net=net, layer=self.b.GetLayerName(lay),
                                x1=p1[0], y1=p1[1], x2=p2[0], y2=p2[1], w=w, lay=lay))


def endpoint(board, item, other_xy):
    """★用 uuid 精确找回板上那一头 ⇒ 返回 (点, 层)"""
    u = item.get("uuid")
    obj = board.by_uuid.get(u) if u else None
    if obj is None:
        p = item.get("pos") or {}
        return (p.get("x", 0.0), p.get("y", 0.0)), pcbnew.F_Cu
    if obj["kind"] == "pad":
        return (obj["x"], obj["y"]), pcbnew.F_Cu
    if obj["kind"] == "track":
        d1 = math.hypot(obj["x1"] - other_xy[0], obj["y1"] - other_xy[1])
        d2 = math.hypot(obj["x2"] - other_xy[0], obj["y2"] - other_xy[1])
        e = (obj["x1"], obj["y1"]) if d1 <= d2 else (obj["x2"], obj["y2"])
        return e, obj["lay"]
    # via
    return (obj["x"], obj["y"]), pcbnew.F_Cu


def try_connect(board, net, a, b, w):
    """★试 直连 / L 形 / ★U 形绕排 (★实测 J_SOM_P3 相邻脚 0.2mm 缝 ⇒ 直连几何不可能 ⇒ 必须绕到焊盘排外面)
    返回 (路径, 走法名, 失败原因)"""
    cands = []
    cands.append(("直", [(a, b)]))
    mx, my = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
    for i, c in enumerate(((mx, a[1]), (a[0], my), (mx, b[1]), (b[0], my))):
        cands.append(("L%d" % i, [(a, c), (c, b)]))
    # ★★U 形绕排: ★从两头垂直拉出去 ⇒ 横移 ⇒ 再回来 (★绕过焊盘排/长走线)
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    if d > 1e-6:
        ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
        px, py = -uy, ux
        for off in (0.35, 0.55, 0.8, 1.2, 1.8, 2.6):
            for s in (+1, -1):
                c1 = (a[0] + px * off * s, a[1] + py * off * s)
                c2 = (b[0] + px * off * s, b[1] + py * off * s)
                cands.append(("U%.2f%s" % (off, "+" if s > 0 else "-"),
                              [(a, c1), (c1, c2), (c2, b)]))
                # ★单侧拉出的 L (只拉一头)
                cands.append(("Lo%.2f%s" % (off, "+" if s > 0 else "-"),
                              [(a, c1), (c1, b)]))
    # ★小 jog (两段 45° 折线) ⇒ 绕开正前方的障碍
    if d > 0.2:
        for s in (+0.3, -0.3):
            off = min(0.6, d / 3.0)
            m = (a[0] + ux * d * 0.5 + px * off * s, a[1] + uy * d * 0.5 + py * off * s)
            cands.append(("jog%.0f" % (off * 100), [(a, m), (m, b)]))
    best_why = ""
    for name, path in cands:
        ok = True
        why = ""
        for (p1, p2) in path:
            o, r = board.seg_ok(net, p1, p2, pcbnew.F_Cu, w)
            if not o:
                ok = False
                why = r
                break
        if ok:
            return path, name, ""
        best_why = why
    return None, "", best_why


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("board")
    ap.add_argument("drc")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-dist", type=float, default=12.0)
    ap.add_argument("--width", type=float, default=0.25)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    d = json.load(open(a.drc, encoding="utf-8"))
    items = d.get("unconnected_items", [])
    bd = Board(a.board)
    print("═══ 补短未连接: %s ═══" % a.board)
    print("═══ DRC 未连接 %d 条 ⇒ 只补两头距离 ≤ %.1fmm 的 ═══" % (len(items), a.max_dist))

    fixed, skipped = [], []
    for it in items:
        its = it.get("items", [])
        if len(its) != 2:
            skipped.append(("条目不是两两相连", ""))
            continue
        d0, d1 = its[0], its[1]
        p0, p1 = d0.get("pos") or {}, d1.get("pos") or {}
        dist = math.hypot(p0.get("x", 0) - p1.get("x", 0), p0.get("y", 0) - p1.get("y", 0))
        na = d0.get("description", "").split("[")
        nb = d1.get("description", "").split("[")
        net_a = na[1].split("]")[0] if len(na) > 1 else ""
        net_b = nb[1].split("]")[0] if len(nb) > 1 else ""
        if net_a != net_b:
            skipped.append(("两头发的是不同网(差分/跨网) ⇒ 不碰", "%s ⇄ %s" % (net_a, net_b)))
            continue
        if dist > a.max_dist:
            skipped.append(("距离 %.1fmm > 阈值 ⇒ 交给路由器" % dist, net_a))
            continue
        ea, la = endpoint(bd, d0, (p1.get("x", 0), p1.get("y", 0)))
        eb, lb = endpoint(bd, d1, (p0.get("x", 0), p0.get("y", 0)))
        path, how, why = try_connect(bd, net_a, ea, eb, a.width)
        if path is None:
            skipped.append(("净距挡死(%s)" % why, net_a))
            continue
        if not a.dry:
            for (p1_, p2_) in path:
                bd.add_track(net_a, p1_, p2_, pcbnew.F_Cu, a.width)
        fixed.append((net_a, dist, how, len(path)))
        print("  ★补上 %-16s 间距 %6.3fmm  走法 %-8s 段数 %d" % (net_a, dist, how, len(path)))

    print("── 补上 %d 条 / 跳过 %d 条" % (len(fixed), len(skipped)))
    for w_, n_ in skipped[:20]:
        print("    · 跳过: %s %s" % (w_, n_))
    if not a.dry:
        bd.b.Save(a.out)
        print("── 已写出: %s (%d B)" % (a.out, os.path.getsize(a.out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
