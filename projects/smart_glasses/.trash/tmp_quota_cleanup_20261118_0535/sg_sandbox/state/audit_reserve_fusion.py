#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""audit_reserve_fusion.py -- ★★审计【预留串】的"跨族公共道"并给出【修正版串】★★ ★★★

★★★**★为什么要有它 (★2026-11-10 01:0x 实测)★★★** ★★★
  ★**机制真相** (★读 `gen_pcb_routing.py` 的 `cu_reserved` 落地代码得到 ★):
    ★**`cu_reserved[li][idx]` = 该格【允许的网集合】; ★★多个框落在同一格 ⇒ 集合取【并集】★★**
    ⇒ ★★**⇒ "给每个卡住的焊盘开专属道" 在【框重叠处】会退化成"给这几族开一条【公共道】"** ★★
    ⇒ ★★**⇒ 公共道里的两族会互相挤 ⇒ ★★**正是"修好一个、打碎另一个"的机制** ★★
  ★**⇒ 修法只有一个: ★★【别让两族共用一条走廊】★★ ⇒ ★**各自换一条走廊 (★改选方向 ★)** ★★

★**本脚本做什么 (★纯只读, ★不改板, ★不碰主线工具 ★)**: ★★
  ① 解析预留串 ⇒ ★**把每个框按【族】拆开** (★同族的多网留一格 ★) ⇒ ★**列出跨族冲突对** ★★
  ② 对冲突: ★**给其中一个族重挑一条【不与别的族重叠】的走廊** (★沿用工具同款几何: 焊盘 → 出脚方向 → 走廊矩形 → 净距排序 ★) ★★
  ③ 输出【修正版预留串】(★可直接贴进臂 env ★) + 审计报告 ★★

用法:
  bash state/pcbnew_py.sh state/audit_reserve_fusion.py \
       HW/PCB/demo_mainboard.kicad_pcb \
       --reserve state/.lastgood/v76rs_reserve_final.txt \
       [--out state/.lastgood/<名字>_split.txt]

★**注意**: ★**输出的修正版只是【给主线的改法建议】★ ⇒ ★**绝不自动开臂** ★★
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("PCB_LAYERS", "8")
import pcbnew  # noqa: E402

MM = 1000000.0
ESC_LEN = 1.20
BOX_W = 0.90
FAM_SUFFIX = ("_N_SRC", "_P_SRC", "_N", "_P", "_SRC")


def family_of(net):
    """★网名 → 族 (★差分配对算同族: ★`_N`/`_P`/`_N_SRC`/`_P_SRC` 都归到同一个 base ★)"""
    for suf in FAM_SUFFIX:
        if net.endswith(suf):
            return net[: -len(suf)]
    return net


def parse_box(b):
    """'NET1+NET2:li,x0,y0,x1,y1' → (nets, li, x0, y0, x1, y1)"""
    head, geo = b.split(":", 1)
    parts = geo.split(",")
    li = int(parts[0])
    x0, y0, x1, y1 = (float(v) for v in parts[1:5])
    return head.split("+"), li, x0, y0, x1, y1


def overlap(a, b):
    """两个矩形 (x0,y0,x1,y1) 是否重叠"""
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 <= bx0 or bx1 <= ax0 or ay1 <= by0 or by1 <= ay0)


def main():
    a = sys.argv[1:]
    boardp = "HW/PCB/demo_mainboard.kicad_pcb"
    reservep = None
    outp = None
    i = 0
    while i < len(a):
        if a[i] == "--reserve":
            reservep = a[i + 1]; i += 2; continue
        if a[i] == "--out":
            outp = a[i + 1]; i += 2; continue
        if not a[i].startswith("--"):
            boardp = a[i]
        i += 1
    if not reservep:
        print("★用法: 需要 --reserve <预留串文件>")
        return 2

    b = pcbnew.LoadBoard(boardp)
    if b is None:
        print("★板读不出来: %s" % boardp)
        return 2

    # ---------- 铜图元 (按层) ----------
    copper = []
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            copper.append((t.GetNetname(), None, "VIA", p.x / MM, p.y / MM, 0.0, 0.0, 0.6))
        else:
            s, e = t.GetStart(), t.GetEnd()
            copper.append((t.GetNetname(), b.GetLayerName(t.GetLayer()), "TRK",
                           s.x / MM, s.y / MM, e.x / MM, e.y / MM, t.GetWidth() / MM))

    def worst_clearance(net, x, y, dx, dy):
        worst = 99.0
        who = "-"
        for (bn, lay, kind, cx, cy, ex, ey, w) in copper:
            if bn == net:
                continue
            if kind == "VIA":
                for k in range(25):
                    t = k / 24.0
                    px, py = x + dx * ESC_LEN * t, y + dy * ESC_LEN * t
                    d = math.hypot(px - cx, py - cy) - w / 2.0 - 0.125
                    if d < worst:
                        worst, who = d, "%s[VIA]" % bn
                continue
            dx2, dy2 = ex - cx, ey - cy
            L2 = dx2 * dx2 + dy2 * dy2
            for k in range(25):
                t = k / 24.0
                px, py = x + dx * ESC_LEN * t, y + dy * ESC_LEN * t
                if L2 == 0:
                    d = math.hypot(px - cx, py - cy) - w / 2.0 - 0.125
                else:
                    u = max(0.0, min(1.0, ((px - cx) * dx2 + (py - cy) * dy2) / L2))
                    qx, qy = cx + u * dx2, cy + u * dy2
                    d = math.hypot(px - qx, py - qy) - w / 2.0 - 0.125
                if d < worst:
                    worst, who = d, "%s[%s]" % (bn, lay)
        return worst, who

    def fp_pads(ref):
        out = []
        for p in b.GetPads():
            try:
                r = p.GetParent().GetReference()
            except Exception:
                try:
                    r = p.GetParentFootprint().GetReference()
                except Exception:
                    r = "?"
            if r == ref:
                pos = p.GetPosition()
                out.append((pos.x / MM, pos.y / MM))
        return out

    def escape_dirs(ref, x, y):
        pts = fp_pads(ref)
        if len(pts) >= 2:
            sx = max(q[0] for q in pts) - min(q[0] for q in pts)
            sy = max(q[1] for q in pts) - min(q[1] for q in pts)
            if sx >= sy:
                return [(0.0, 1.0, "+y"), (0.0, -1.0, "-y")]
            return [(1.0, 0.0, "+x"), (-1.0, 0.0, "-x")]
        return [(0.0, 1.0, "+y"), (0.0, -1.0, "-y")]

    def box_of_dir(x, y, dx, dy):
        if dx == 0.0 and dy > 0:
            return (x - BOX_W / 2.0, y, x + BOX_W / 2.0, y + ESC_LEN + 0.2)
        if dx == 0.0:
            return (x - BOX_W / 2.0, y - ESC_LEN - 0.2, x + BOX_W / 2.0, y)
        if dx > 0:
            return (x, y - BOX_W / 2.0, x + ESC_LEN + 0.2, y + BOX_W / 2.0)
        return (x - ESC_LEN - 0.2, y - BOX_W / 2.0, x, y + BOX_W / 2.0)

    # ---------- 读预留串 ----------
    raw = open(reservep, encoding="utf-8").read().strip()
    boxes = [parse_box(x) for x in raw.split(";") if x.strip()]
    print("★预留串: %d 个框 (★%s★)" % (len(boxes), reservep))

    # ---------- ① 按族拆开 ----------
    subs = []      # [fam, nets[], li, geo]
    for (nets, li, x0, y0, x1, y1) in boxes:
        byfam = {}
        for net in nets:
            byfam.setdefault(family_of(net), []).append(net)
        for fam, ns in byfam.items():
            subs.append([fam, sorted(set(ns)), li, (x0, y0, x1, y1)])
    print("★拆成【族】后: %d 格 (★原 %d 框★)" % (len(subs), len(boxes)))

    def conflicts(sub_list):
        out = []
        for i in range(len(sub_list)):
            for j in range(i + 1, len(sub_list)):
                if sub_list[i][0] == sub_list[j][0]:
                    continue
                if sub_list[i][2] != sub_list[j][2]:
                    continue
                if overlap(sub_list[i][3], sub_list[j][3]):
                    out.append((i, j))
        return out

    before = conflicts(subs)
    print("★★跨族冲突对 (★公共道, ★★不是专属道★★): %d 对" % len(before))
    seen = set()
    for (i, j) in before:
        key = tuple(sorted((subs[i][0], subs[j][0])))
        if key in seen:
            continue
        seen.add(key)
        print("   ★%s  ⇄  %s" % ("+".join(subs[i][1]), "+".join(subs[j][1])))

    # ---------- ② 重挑 ----------
    def candidates(nets):
        cands = []
        for net in nets:
            for p in b.GetPads():
                if p.GetNetname() != net:
                    continue
                try:
                    ref = p.GetParent().GetReference()
                except Exception:
                    try:
                        ref = p.GetParentFootprint().GetReference()
                    except Exception:
                        ref = "?"
                pos = p.GetPosition()
                px, py = pos.x / MM, pos.y / MM
                for (dx, dy, tag) in escape_dirs(ref, px, py):
                    g = box_of_dir(px, py, dx, dy)
                    w, who = worst_clearance(net, px, py, dx, dy)
                    cands.append((w, net, ref, px, py, tag, g, who))
        cands.sort(key=lambda t: -t[0])
        return cands

    changed = []
    for (i, j) in before:
        mover = j
        fam_m = subs[mover][0]
        cands = candidates(subs[mover][1])
        pick = None
        for (w, net, ref, px, py, tag, g, who) in cands:
            bad = False
            for k, s in enumerate(subs):
                if k == mover or s[0] == fam_m or s[2] != subs[mover][2]:
                    continue
                if overlap(g, s[3]):
                    bad = True
                    break
            if not bad:
                pick = (w, net, ref, px, py, tag, g, who)
                break
        if pick:
            w, net, ref, px, py, tag, g, who = pick
            changed.append(("+".join(subs[mover][1]),
                            "⇒ 净距 %+.3f (%s@%s %s, 最近 %s)" % (w, net, ref, tag, who),
                            "%.3f,%.3f,%.3f,%.3f" % g))
            subs[mover][3] = g
        else:
            changed.append(("+".join(subs[mover][1]),
                            "★★找不到不重叠的走廊 ⇒ 保持原样 (★公共道留着 ★★)", ""))

    # ---------- ③ 输出 ----------
    merged = {}
    order = []
    for (fam, nets, li, g) in subs:
        key = (fam, li, g)
        if key not in merged:
            merged[key] = []
            order.append(key)
        merged[key].extend(nets)
    lines = []
    for key in order:
        fam, li, g = key
        nets = sorted(set(merged[key]))
        lines.append("%s:%d,%.3f,%.3f,%.3f,%.3f" % ("+".join(nets), li, g[0], g[1], g[2], g[3]))
    outstr = ";".join(lines)

    print("\n★★★重挑结果 (★%d 个族改了走廊 ★)★★★" % len(changed))
    for c in changed:
        print("   ★%s %s %s" % c)
    fb = [parse_box(x) for x in lines]
    after = conflicts([[family_of("+".join(bb[0])), bb[0], bb[1], (bb[2], bb[3], bb[4], bb[5])] for bb in fb])
    print("★修正后【跨族冲突对】= %d (★修正前 %d★)" % (len(after), len(before)))
    print("\n★★★修正版预留串 (%d 个框)★★★" % len(lines))
    print('  PCB_ROUTE_RESERVE="%s"' % outstr)
    if outp:
        open(outp, "w", encoding="utf-8").write(outstr + "\n")
        print("★已写: %s" % outp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
