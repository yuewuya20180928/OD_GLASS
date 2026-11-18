#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""analyze_escape_dirs.py —— ★★★【★★官方板 45 条未连接的【出脚方向分配】分析器 (只读)★★★】★★★

★★★**★为什么要有这个 (★2026-11-10 03:2x 主会话点名要的东西★)★★★** ★★★
  ★**要的东西**: ★★**"哪个端点最优出脚方向 + 最优长度"表 ⇒ ⇒ 出脚方向冲突图 ⇒ ⇒ 据此做【出脚方向分配】机制**★★ ★★★
  ★★**★`probe_escape_feasibility.py` 只给【每个端点的最优 1 个方向】⇒ ⇒ 只知道"能往哪走"
    ⇒ ★**不知道"两个端点会不会抢同一条道"** ⇒ ★**不知道"能不能给所有端点同时分配出脚方向"**★★ ★★★
  ★★**⇒ 本工具补三件事**: ★★
    ① **每端点 × 4 方向 × 4 长度的完整余量矩阵** (★不是只给最优★) ⇒ ⇒ **可行方向集合** ★★
    ② **出脚方向冲突图**: ★**两个端点若各按某方向出脚, 它们的出脚直道净距 < 0.20mm ⇒ 边** ⇒ ⇒ **图结构** ★★
    ③ **可满足性 (★CSP: 域=4 方向, 约束=两两直道净距, ★前向检查 + MRV 回溯★)**
    ⇒ ★**这直接决定"出脚方向分配"机制能不能救 A* (★方向都分配不出来 ⇒ 这条路也死★)** ★★★

★★★**★口径 (★与 `probe_escape_feasibility.py` / `geom_clear.py` 完全一致, ★不自造几何★)★★★** ★★★
  · 焊盘 → 矩形 (★按旋转角交换长宽★) · 走线 → 矩形 · 过孔 → 矩形(全层)
  · 净距 = `geom_clear.rect_rect_dist` (★真几何★) · ★**只算异网铜 + 只算同层(通孔全层)★**
  · CLEAR = 0.20mm (★板规则★) · ESC_LENS = 1.20/0.90/0.60/0.40mm (★与探针同★)
  · 线宽对照: W=0.20 (旧) / W=0.15 (★老板 11-09 批的设计线宽★)
  · ★**冲突判定**: 两条出脚直道 (★矩形, ★已含线宽★) 的**边缘间距 < CLEAR** ⇒ 冲突 ★★

用法:
  bash state/pcbnew_py.sh state/analyze_escape_dirs.py <板> <DRC.json> [--out <txt>] [--json <json>]
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
DIR_NAME = {(0, 1): "↑", (0, -1): "↓", (1, 0): "→", (-1, 0): "←"}
DIR_FULL = {(0, 1): "↑(0,+1)", (0, -1): "↓(0,-1)",
            (1, 0): "→(+1,0)", (-1, 0): "←(-1,0)"}
WIDTHS = (0.20, 0.15)
W_MAIN = 0.15          # ★设计线宽 (★老板批的★)
EPS = 1e-9


def pad_rect(p):
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


def bbox(r):
    xs = [p[0] for p in r]
    ys = [p[1] for p in r]
    return (min(xs), min(ys), max(xs), max(ys))


def bbox_gap(b1, b2):
    dx = max(0.0, b1[0] - b2[2], b2[0] - b1[2])
    dy = max(0.0, b1[1] - b2[3], b2[1] - b1[3])
    return math.hypot(dx, dy)


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        return 2
    boardp, drcp = a[0], a[1]
    outf = joutf = None
    if "--out" in a:
        i = a.index("--out")
        if i + 1 < len(a):
            outf = a[i + 1]
    if "--json" in a:
        i = a.index("--json")
        if i + 1 < len(a):
            joutf = a[i + 1]

    b = pcbnew.LoadBoard(boardp)

    ALL_CU = set()
    for nm in ["F.Cu", "In1.Cu", "In2.Cu", "In3.Cu", "In4.Cu", "In5.Cu",
               "In6.Cu", "B.Cu"]:
        ALL_CU.add(nm)

    segs, vias, pads = [], [], []
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
    for f in b.GetFootprints():
        for p in f.Pads():
            r, lays = pad_rect(p)
            pads.append((p.GetNetname(), "%s.%s" % (f.GetReference(), p.GetNumber()),
                         r, lays))

    segs_b = [(bbox(r), n, r, lay) for (n, r, lay) in segs]
    vias_b = [(bbox(r), n, r) for (n, r) in vias]
    pads_b = [(bbox(r), n, nm, r, lays) for (n, nm, r, lays) in pads]

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

    L = []
    def out(s=""):
        L.append(s)

    out("═══ 官方板出脚方向分配分析 (只读) ═══")
    out("板 = %s" % boardp)
    out("DRC json = %s" % drcp)
    out("未连接条目 = %d · 净距 CLEAR = %.2fmm · 出脚长度候选 = %s mm"
        % (len(items), CLEAR, "/".join("%.2f" % x for x in ESC_LENS)))
    out("线宽 = W0.20(旧) / W0.15(设计) · ★冲突判定 = 两条出脚直道边缘间距 < %.2fmm ★" % CLEAR)
    out("")

    # ── 解析端点 ──
    eps = []
    skipped = []
    for it in items:
        its = it.get("items") or []
        if len(its) != 2:
            skipped.append(("items!=2", str(it.get("description"))[:60], ""))
            continue
        m0 = re.search(r"\[([^\]]+)\]", its[0].get("description") or "")
        m1 = re.search(r"\[([^\]]+)\]", its[1].get("description") or "")
        net = m0.group(1) if m0 else "?"
        net1 = m1.group(1) if m1 else ""
        if net != net1:
            skipped.append(("net mismatch", "%s vs %s" % (net, net1),
                            (its[0].get("description") or "")[:70]))
            continue
        for sub in its:
            o = byu.get(sub.get("uuid"))
            if o is None:
                skipped.append(("uuid not found", net, (sub.get("description") or "")[:70]))
                continue
            kind, obj = o
            if kind == "p":
                r, lays = pad_rect(obj)
                nm = "%s.%s" % (obj.GetParentFootprint().GetReference(), obj.GetNumber())
                lays_set = set(lays)
            elif obj.Type() == pcbnew.PCB_VIA_T:
                w = obj.GetWidth(pcbnew.F_Cu) / MM
                h = w / 2.0
                cx, cy = obj.GetPosition().x / MM, obj.GetPosition().y / MM
                r = [(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)]
                nm = "过孔"
                lays_set = set(ALL_CU)
            else:
                s, e = obj.GetStart(), obj.GetEnd()
                r = GC.rect_from_seg((s.x / MM, s.y / MM), (e.x / MM, e.y / MM),
                                      obj.GetWidth() / MM)
                if not r:
                    skipped.append(("no rect", net, (sub.get("description") or "")[:70]))
                    continue
                nm = "走线端"
                lays_set = {obj.GetLayerName()}
            cx, cy = rect_center(r)
            eps.append({"net": net, "name": nm, "cx": cx, "cy": cy,
                        "layers": lays_set, "rect": r, "sub": sub})

    # ★★**去重**: ★同一个网的同一个焊盘可能出现在多条未连接条目里 (★例如 3 焊盘的网 ⇒ 2 条未连接★)
    #   ⇒ ★物理上是【同一个铜块】⇒ 只算一个端点 ★★
    dedup = []
    idx_of = {}
    for e in eps:
        k = (e["net"], e["name"], round(e["cx"], 3), round(e["cy"], 3))
        if k in idx_of:
            dedup[idx_of[k]]["refs"] += 1
        else:
            e["refs"] = 1
            idx_of[k] = len(dedup)
            dedup.append(e)
    out("── 端点解析: %d 条记录 ⇒ ★去重后 %d 个物理端点 (★同一网同一焊盘出现在多条未连接里 ⇒ 合并★)"
        % (len(eps), len(dedup)))
    eps = dedup
    if skipped:
        out("   ★★解析跳过 %d 条 (★口径缺口, ★必须知道★★):" % len(skipped))
        for why, a1, a2 in skipped:
            out("     · %s | %s | %s" % (why, a1, a2))
    out("")

    # ── 每端点 × 方向 × 长度 × 线宽 的余量 ──
    for ep in eps:
        cx, cy = ep["cx"], ep["cy"]
        for w in WIDTHS:
            table = {}
            for (dx, dy) in DIRS:
                for ln in ESC_LENS:
                    ex, ey = cx + dx * ln, cy + dy * ln
                    sr = GC.rect_from_seg((cx, cy), (ex, ey), w)
                    if not sr:
                        continue
                    mind, blocker = 1e9, ""
                    sb = bbox(sr)
                    for (bb2, n2, r2, lay2) in segs_b:
                        if n2 == ep["net"]:
                            continue
                        if lay2 not in ep["layers"]:
                            continue
                        if bbox_gap(sb, bb2) >= mind:
                            continue
                        dd = GC.rect_rect_dist(sr, r2)
                        if dd < mind:
                            mind, blocker = dd, "%s[%s]" % (n2, lay2)
                    for (bb2, n2, r2) in vias_b:
                        if n2 == ep["net"]:
                            continue
                        if bbox_gap(sb, bb2) >= mind:
                            continue
                        dd = GC.rect_rect_dist(sr, r2)
                        if dd < mind:
                            mind, blocker = dd, "%s[通孔]" % n2
                    for (bb2, n2, nm2, r2, lays2) in pads_b:
                        if n2 == ep["net"]:
                            continue
                        if not (ep["layers"] & lays2):
                            continue
                        if bbox_gap(sb, bb2) >= mind:
                            continue
                        dd = GC.rect_rect_dist(sr, r2)
                        if dd < mind:
                            mind, blocker = dd, "%s[%s]" % (n2, nm2)
                    table[(dx, dy, ln)] = (mind - CLEAR, blocker, sr)
            ep["tbl%s" % w] = table

    # ── 表①: 每端点最优方向 + 最优长度 ──
    out("═══════ 表① 端点 × 最优出脚方向/长度 (★W=%.2f 设计线宽★) ═══════" % W_MAIN)
    out("%-16s %-18s %-15s %-11s %-4s %-4s %-6s %-7s %-6s %s"
        % ("NET", "端点", "坐标", "层", "向", "长", "余量", "可行向", "可行数", "各向最优(向:长,余量)"))
    for ep in eps:
        t = ep["tbl%s" % W_MAIN]
        best = None
        for k, (mg, blk, sr) in t.items():
            if mg < -EPS:
                continue
            if best is None or mg > best[0] + EPS:
                best = (mg, k, blk)
        feas = sorted([(k[2], k[0], k[1], mg) for k, (mg, blk, sr) in t.items()
                       if mg >= -EPS])
        ep["feas"] = feas
        dirs_feas = sorted(set((k[0], k[1]) for k in t if t[k][0] >= -EPS))
        lay_s = "/".join(sorted(ep["layers"]))
        if len(lay_s) > 11:
            lay_s = lay_s[:11]
        if best is None:
            out("%-16s %-18s (%7.3f,%7.3f) %-11s ★无任何可行方向★"
                % (ep["net"], ep["name"], ep["cx"], ep["cy"], lay_s))
            ep["best"] = None
            continue
        mg, (dx, dy, ln), blk = best
        ep["best"] = (dx, dy, ln, mg, blk)
        # 每个方向的最短可行长 + 该方向最大余量
        per_dir = {}
        for (ln2, dx2, dy2, mg2) in feas:
            k = (dx2, dy2)
            if k not in per_dir:
                per_dir[k] = [ln2, mg2]
            else:
                per_dir[k][0] = min(per_dir[k][0], ln2)
                per_dir[k][1] = max(per_dir[k][1], mg2)
        ep["per_dir"] = per_dir
        out("%-16s %-18s (%7.3f,%7.3f) %-11s %-4s %-6.2f %+6.3f %-7s %-6d %s"
            % (ep["net"], ep["name"], ep["cx"], ep["cy"], lay_s,
               DIR_NAME[(dx, dy)], ln, mg,
               "".join(DIR_NAME[d] for d in dirs_feas), len(dirs_feas),
               " ".join("%s:%.2f(%+.3f)" % (DIR_NAME[k], per_dir[k][0], per_dir[k][1])
                        for k in sorted(per_dir))))
    out("")

    # ── 方向负载直方图 (最优) ──
    hist = {d: 0 for d in DIRS}
    for ep in eps:
        if ep.get("best"):
            hist[(ep["best"][0], ep["best"][1])] += 1
    out("── 表② 方向负载 (★按各端点【最优】方向统计★)")
    for d in DIRS:
        out("   %s (%d,%d): %d 个端点" % (DIR_FULL[d], d[0], d[1], hist[d]))
    out("")

    # ── 硬约束端点 (只有一个可行方向) ──
    hard = [ep for ep in eps if ep.get("feas") and
            len(set((f[1], f[2]) for f in ep["feas"])) == 1]
    out("── 表③ 硬约束端点 (★只有一个可行方向 ⇒ 方向分配机制必须给它这个方向★): %d 个" % len(hard))
    for ep in hard:
        d = (ep["feas"][0][0], ep["feas"][0][1])
        out("   %-16s %-18s (%7.3f,%7.3f) ⇒ %s  可行长 %s"
            % (ep["net"], ep["name"], ep["cx"], ep["cy"], DIR_FULL[d],
               ",".join("%.2f" % f[2] for f in ep["feas"])))
    out("")

    # ── 候选 (每端点每方向: 最短可行长) ──
    # 候选索引: cand[i][dir_index] = {"d":.., "ln":.., "mg":.., "rect":..}
    cand = []
    for ep in eps:
        pd = ep.get("per_dir") or {}
        row = []
        for d in DIRS:
            if d in pd:
                ln, mg = pd[d][0], pd[d][1]
                sr = ep["tbl%s" % W_MAIN][(d[0], d[1], ln)][2]
                row.append({"d": d, "ln": ln, "mg": mg, "rect": sr})
            else:
                row.append(None)
        cand.append(row)

    def stub_conflict(ra, rb):
        if bbox_gap(bbox(ra), bbox(rb)) >= CLEAR:
            return False
        return GC.rect_rect_dist(ra, rb) < CLEAR - EPS

    # ── 冲突图 (★同网铜不需要净距 ⇒ 同网端点之间一律跳过★) ──
    # conf[i][di] = set(j): ★若 i 取方向 di, 则 j 的【所有】方向都与 i 打架 ⇒ j 必须换方向★
    conf = []
    for i in range(len(eps)):
        row = []
        for di in DIRS:
            s = set()
            ci = cand[i][DIRS.index(di)]
            if ci is None:
                row.append(s)
                continue
            for j in range(len(eps)):
                if j == i:
                    continue
                if eps[j]["net"] == eps[i]["net"]:
                    continue        # ★同网 ⇒ 同铜 ⇒ 不需要净距★
                for dj in DIRS:
                    cj = cand[j][DIRS.index(dj)]
                    if cj is None:
                        continue
                    if stub_conflict(ci["rect"], cj["rect"]):
                        s.add(j)
                        break
            row.append(s)
        conf.append(row)

    pair_set = set()
    for i in range(len(eps)):
        for di in DIRS:
            for j in conf[i][DIRS.index(di)]:
                if j > i:
                    pair_set.add((i, j))
    edge_count = len(pair_set)
    out("── 表④ 出脚方向冲突边 (★端点对: 存在某组方向使两条出脚直道净距 < %.2fmm★): %d 条"
        % (CLEAR, edge_count))
    for (i, j) in sorted(pair_set):
        out("   %-16s %-18s (%7.3f,%7.3f)  ✘冲突✘  %-16s %-18s (%7.3f,%7.3f)"
            % (eps[i]["net"], eps[i]["name"], eps[i]["cx"], eps[i]["cy"],
               eps[j]["net"], eps[j]["name"], eps[j]["cx"], eps[j]["cy"]))
    out("")

    # ── 表⑤ CSP 可满足性 (域=4 方向, 前向检查 + MRV) ──
    n = len(eps)
    dom0 = []
    for i in range(n):
        m = 0
        for di, d in enumerate(DIRS):
            if cand[i][di] is not None:
                m |= (1 << di)
        dom0.append(m)
    dom = list(dom0)
    assign = [None] * n
    nodes = [0]
    LIMIT = 200000

    def solve():
        nodes[0] = 0

        def rec(dom_l, asg):
            nodes[0] += 1
            if nodes[0] > LIMIT:
                return None
            pick, pc = -1, 99
            for i in range(n):
                if asg[i] is None:
                    c = bin(dom_l[i]).count("1")
                    if c == 0:
                        return None
                    if c < pc:
                        pc, pick = c, i
            if pick < 0:
                return list(asg)
            for di, d in enumerate(DIRS):
                if not (dom_l[pick] >> di) & 1:
                    continue
                asg[pick] = d
                nd = list(dom_l)
                ok = True
                for j in range(n):
                    if j == pick or asg[j] is not None:
                        continue
                    if j in conf[pick][di]:
                        nd[j] &= ~(1 << di)
                        if nd[j] == 0:
                            ok = False
                            break
                if ok:
                    r = rec(nd, asg)
                    if r is not None:
                        return r
                asg[pick] = None
            return None

        return rec(list(dom0), [None] * n)

    sol = solve()
    sat = sol is not None
    out("── 表⑤ 出脚方向分配可满足性 (★W=%.2f, ★每端点 1 个方向, ★两两直道净距 ≥ %.2fmm★)"
        % (W_MAIN, CLEAR))
    out("   端点 %d · 搜索节点 %d%s" % (n, nodes[0],
        (" · ★★已撞节点上限 ⇒ 只能判【疑似不可行】, 不能判死★★" if nodes[0] > LIMIT else "")))
    if sat:
        out("   ★★✔【可满足】⇒ 全部 %d 个端点能同时分配到互不打架的出脚方向/长度 ★★" % n)
        out("      ⇒ ⇒ 【出脚方向分配】机制在几何上可行 ⇒ ⇒ A* 只要拿到这个【起点方向】就能出发 ★★")
        out("")
        out("   ★分配结果 (★网 / 端点 / 坐标 / 方向 / 长度 / 余量 / 冲突对端★):")
        hist2 = {d: 0 for d in DIRS}
        for i, ep in enumerate(eps):
            d = sol[i]
            di = DIRS.index(d)
            ci = cand[i][di]
            hist2[d] += 1
            out("   %-16s %-18s (%7.3f,%7.3f) %-7s %.2f  %+7.3f  ★冲突对 %d"
                % (ep["net"], ep["name"], ep["cx"], ep["cy"],
                   DIR_FULL[d], ci["ln"], ci["mg"], len(conf[i][di])))
        out("")
        out("   ★分配后方向负载: " + " · ".join(
            "%s=%d" % (DIR_FULL[d], hist2[d]) for d in DIRS))
        out("   ★★注意: ★分配用【每方向最短可行长】(★最不挡人★) ⇒ 实际路由可按需加长, ★但加长会引入新冲突★")
    else:
        out("   ★★✘【不可满足】⇒ ⇒ 【出脚方向分配】也救不了 ⇒ ⇒ 瓶颈比想的更深 ★★")
    out("")

    # ── 表⑨ 最坏 fan-out 冲突图 (★每方向取【最长】可行长 ⇒ 大家尽量往外走时的冲突★) ──
    cand_max = []
    for ep in eps:
        pd = ep.get("per_dir") or {}
        row = []
        for d in DIRS:
            bl = None
            for (ln2, dx2, dy2, mg2) in ep["feas"]:
                if (dx2, dy2) == d and (bl is None or ln2 > bl[0]):
                    bl = (ln2, mg2)
            if bl is None:
                row.append(None)
            else:
                sr = ep["tbl%s" % W_MAIN][(d[0], d[1], bl[0])][2]
                row.append({"d": d, "ln": bl[0], "mg": bl[1], "rect": sr})
        cand_max.append(row)
    pair_set2 = set()
    for i in range(len(eps)):
        for di, d in enumerate(DIRS):
            ci = cand_max[i][di]
            if ci is None:
                continue
            for j in range(len(eps)):
                if j == i or eps[j]["net"] == eps[i]["net"]:
                    continue
                hit = False
                for dj in DIRS:
                    cj = cand_max[j][DIRS.index(dj)]
                    if cj is None:
                        continue
                    if stub_conflict(ci["rect"], cj["rect"]):
                        hit = True
                        break
                if hit:
                    pair_set2.add((i, j))
    out("── 表⑨ 最坏 fan-out 冲突图 (★每端点每方向都取【最长】可行长 ⇒ 全员尽量往外走★): %d 条边"
        % len(pair_set2))
    for (i, j) in sorted(pair_set2):
        out("   %-16s %-18s (%7.3f,%7.3f)  ✘✘  %-16s %-18s (%7.3f,%7.3f)"
            % (eps[i]["net"], eps[i]["name"], eps[i]["cx"], eps[i]["cy"],
               eps[j]["net"], eps[j]["name"], eps[j]["cx"], eps[j]["cy"]))
    out("")

    # ── 表⑥ 差分对腿体检 ──
    out("── 表⑥ 差分对腿的出脚方向体检 (★P/N 两腿能否各走各的★)")
    bynet = {}
    for i, ep in enumerate(eps):
        bynet.setdefault(ep["net"], []).append(i)
    pairnets = []
    for n2, idxs in bynet.items():
        if n2.endswith("_P") or n2.endswith("_N"):
            base = n2[:-2]
            if base + "_P" in bynet and base + "_N" in bynet:
                pairnets.append(base)
    for base in sorted(pairnets):
        pl = bynet[base + "_P"]
        nl = bynet[base + "_N"]
        out("   ★%s (★P 腿 %d 个 · N 腿 %d 个★)" % (base, len(pl), len(nl)))
        for tag, lst in (("P", pl), ("N", nl)):
            for i in lst:
                ep = eps[i]
                da = ep.get("best")
                dirs_feas = sorted(set((f[1], f[2]) for f in ep["feas"]))
                comp = ep["name"].split(".")[0]
                out("      %s@%-18s %-14s (%7.3f,%7.3f) 最优 %-7s 长%.2f 余量%+.3f · 可行方向 %s"
                    % (tag, ep["name"], comp, ep["cx"], ep["cy"],
                       DIR_FULL[(da[0], da[1])] if da else "无",
                       da[2] if da else 0, da[3] if da else 0,
                       "".join(DIR_NAME[d] for d in dirs_feas) or "无"))
        # ★同器件 (或 2mm 内) 的 P/N 两腿 ⇒ ★必须给不同方向 (★否则差分腿挤同一条道★)
        for a_ in pl:
            for b_ in nl:
                pa, pb = eps[a_], eps[b_]
                compa = pa["name"].split(".")[0]
                compb = pb["name"].split(".")[0]
                near = (compa == compb) or (math.hypot(pa["cx"] - pb["cx"],
                                                       pa["cy"] - pb["cy"]) < 2.0)
                if not near:
                    continue
                fa = set((f[1], f[2]) for f in pa["feas"])
                fb = set((f[1], f[2]) for f in pb["feas"])
                overlap = fa & fb
                da = pa.get("best")
                db = pb.get("best")
                same = (da and db and da[0:2] == db[0:2])
                out("      ★近邻两腿: %s@%s ↔ %s@%s ⇒ 可行方向交集 %s · 最优 %s%s ⇒ %s"
                    % ("P", pa["name"], "N", pb["name"],
                       "".join(DIR_NAME[d] for d in sorted(overlap)) or "空(★天然分开★)",
                       DIR_FULL[(da[0], da[1])] if da else "无",
                       DIR_FULL[(db[0], db[1])] if db else "无",
                       "★同向(两腿挤同一条道)★" if same else "反向/异向 ✔"))
                if sat:
                    out("      ★分配后: P %s / N %s ⇒ %s"
                        % (DIR_FULL[sol[a_]], DIR_FULL[sol[b_]],
                           "★同向★" if sol[a_] == sol[b_] else "反向/异向 ✔"))
    out("")

    out("═══════ 汇总 ═══════")
    nfeas = sum(1 for e in eps if e.get("feas"))
    out("端点总数 = %d · 有可行方向的 = %d · 无可行方向的 = %d"
        % (len(eps), nfeas, len(eps) - nfeas))
    out("硬约束端点 (单一方向) = %d" % len(hard))
    out("冲突边 (端点对) = %d" % edge_count)
    out("方向分配可满足 = %s" % ("是" if sat else "否"))
    out("")

    # ── 表⑦ 按网的紧凑表 (★45 条未连接, ★一行一条★) ──
    out("═══════ 表⑦ 按网紧凑表 (★一条未连接一行, ★★主会话要的就是这张★★) ═══════")
    out("%-16s %-20s %-16s %-16s %-8s %s"
        % ("NET", "端点1 (最优向/长/余量)", "端点2 (最优向/长/余量)", "", "可行数", "备注"))
    net_eps = {}
    for i, ep in enumerate(eps):
        net_eps.setdefault(ep["net"], []).append(i)
    for net, idxs in net_eps.items():
        cells = []
        notes = []
        for i in idxs:
            ep = eps[i]
            da = ep.get("best")
            dirs_feas = sorted(set((f[1], f[2]) for f in ep["feas"]))
            cells.append("%s %s/%.2f/%+.3f" % (
                ep["name"],
                DIR_NAME[(da[0], da[1])] if da else "无",
                da[2] if da else 0,
                da[3] if da else 0))
            notes.append("%s:%d向%s" % (ep["name"], len(dirs_feas),
                                       "".join(DIR_NAME[d] for d in dirs_feas)))
            if len(dirs_feas) <= 2:
                notes.append("★%s 受限(仅 %d 向)★" % (ep["name"], len(dirs_feas)))
        out("%-16s %-34s %-34s %-16s %-8s %s"
            % (net, cells[0] if len(cells) > 0 else "",
               cells[1] if len(cells) > 1 else "",
               cells[2] if len(cells) > 2 else "",
               "+".join(notes), " / ".join(notes)))
    out("")

    # ── 表⑧ 受限端点 (★只剩 ≤2 个方向 ⇒ 方向分配机制真正起作用的地方★) ──
    lim = [ep for ep in eps if ep.get("feas") and
           len(set((f[1], f[2]) for f in ep["feas"])) <= 2]
    out("── 表⑧ 受限端点 (★可行方向 ≤2 ⇒ 出脚方向分配的真正战场★): %d 个" % len(lim))
    for ep in lim:
        dirs_feas = sorted(set((f[1], f[2]) for f in ep["feas"]))
        da = ep.get("best")
        out("   %-16s %-18s (%7.3f,%7.3f) 方向 %s · 最优 %s 长%.2f 余量%+.3f"
            % (ep["net"], ep["name"], ep["cx"], ep["cy"],
               "".join(DIR_NAME[d] for d in dirs_feas),
               DIR_NAME[(da[0], da[1])] if da else "无",
               da[2] if da else 0, da[3] if da else 0))
    out("")
    out("★★⇒ 【结论】: ★【出脚方向分配】机制几何可行性 = %s ★" % ("可行" if sat else "不可行"))

    text = "\n".join(L)
    if outf:
        open(outf, "w", encoding="utf-8").write(text)
    if joutf:
        js = {"board": boardp, "drc": drcp, "width": W_MAIN,
              "n_endpoints": len(eps), "skipped": skipped,
              "endpoints": [{"net": e["net"], "name": e["name"],
                             "x": e["cx"], "y": e["cy"],
                             "layers": sorted(e["layers"]),
                             "best": (list(e["best"][0:2]) + [e["best"][2], e["best"][3]])
                             if e.get("best") else None,
                             "feas": [[f[0], f[1], f[2], f[3]] for f in e.get("feas", [])]}
                            for e in eps],
              "assign": ({"%s@%s" % (e["net"], e["name"]):
                           {"dir": list(sol[i]),
                            "len": cand[i][DIRS.index(sol[i])]["ln"],
                            "margin": cand[i][DIRS.index(sol[i])]["mg"]}
                           for i, e in enumerate(eps)} if sat else None),
              "satisfiable": sat,
              "conflict_pairs": edge_count}
        open(joutf, "w", encoding="utf-8").write(json.dumps(js, ensure_ascii=False, indent=1))
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
