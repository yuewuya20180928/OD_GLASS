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
    ③ **可满足性**: ★**能不能给全部端点同时分配一个"互不打架"的出脚方向? (★约束求解 + 回溯★)**
    ⇒ ★**这直接决定"出脚方向分配"机制能不能救 A* (★方向都分配不出来 ⇒ 这条路也死★)** ★★★

★★★**★口径 (★与 `probe_escape_feasibility.py` / `geom_clear.py` 完全一致, ★不自造几何★)★★★** ★★★
  · 焊盘 → 矩形 (★按旋转角交换长宽★) · 走线 → 矩形 · 过孔 → 矩形(全层)
  · 净距 = `geom_clear.rect_rect_dist` (★真几何★) · ★**只算异网铜 + 只算同层(通孔全层)★**
  · CLEAR = 0.20mm (★板规则★) · ESC_LENS = 1.20/0.90/0.60/0.40mm (★与探针同★)
  · 线宽对照: W=0.20 (旧) / W=0.15 (★老板 11-09 批的设计线宽★)

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
             (cx + hx, cy + hy), (cx - hy, cy + hy)], lays)


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
    out("线宽 = W0.20(旧) / W0.15(设计) · ★冲突判定 = 两条出脚直道间距 < %.2fmm ★" % CLEAR)
    out("")

    # ── 解析端点 ──
    eps = []          # 每个端点一条记录
    skipped = []
    for it in items:
        its = it.get("items") or []
        if len(its) != 2:
            skipped.append(("items!=2", it.get("description"), str(its)[:120]))
            continue
        m0 = re.search(r"\[([^\]]+)\]", its[0].get("description") or "")
        m1 = re.search(r"\[([^\]]+)\]", its[1].get("description") or "")
        net = m0.group(1) if m0 else "?"
        net1 = m1.group(1) if m1 else ""
        if net != net1:
            skipped.append(("net mismatch", "%s vs %s" % (net, net1),
                            (its[0].get("description") or "")[:80]))
            continue
        for si, sub in enumerate(its):
            o = byu.get(sub.get("uuid"))
            if o is None:
                skipped.append(("uuid not found", net, (sub.get("description") or "")[:80]))
                continue
            kind, obj = o
            if kind == "p":
                r, lays = pad_rect(obj)
                nm = "%s.%s" % (obj.GetParentFootprint().GetReference(), obj.GetNumber())
                lays_set = set(lays)
            else:
                s, e = obj.GetStart(), obj.GetEnd()
                r = GC.rect_from_seg((s.x / MM, s.y / MM), (e.x / MM, e.y / MM),
                                      obj.GetWidth() / MM)
                if not r:
                    skipped.append(("no rect", net, (sub.get("description") or "")[:80]))
                    continue
                nm = "走线端"
                lays_set = {obj.GetLayerName()}
            cx, cy = rect_center(r)
            eps.append({"net": net, "name": nm, "cx": cx, "cy": cy,
                        "layers": lays_set, "rect": r,
                        "is_pad": kind == "p"})

    out("── 端点解析: %d 个 (★条目 %d ⇒ 期望 %d 个端点★)"
        % (len(eps), len(items), 2 * len(items)))
    if skipped:
        out("   ★★解析跳过 %d 条 (★口径缺口, ★必须知道★★):" % len(skipped))
        for why, a1, a2 in skipped:
            out("     · %s | %s | %s" % (why, a1, a2))
    out("")

    # ── 每个端点: 4 方向 × 4 长度 × 2 线宽 的余量 ──
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
    out("═══════ 表① 端点 × 最优出脚方向/长度 (★W=0.15 设计线宽★) ═══════")
    out("%-18s %-16s %-16s %-4s %-6s %-8s %-8s %-7s %s"
        % ("NET", "端点", "坐标", "层", "最优向", "最优长", "余量", "可行向", "可行集合(向:长)"))
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
        dirs_feas = sorted(set((k[0], k[1]) for k in t if t[k][0] >= -EPS))
        if best is None:
            out("%-18s %-16s (%7.3f,%7.3f) %-4s  ★无任何可行方向★"
                % (ep["net"], ep["name"], ep["cx"], ep["cy"],
                   "/".join(sorted(ep["layers"]))))
            ep["best"] = None
            ep["feas"] = []
            continue
        mg, (dx, dy, ln), blk = best
        ep["best"] = (dx, dy, ln, mg, blk)
        ep["feas"] = [(dx2, dy2, ln2, mg2) for (ln2, dx2, dy2, mg2) in feas]
        out("%-18s %-16s (%7.3f,%7.3f) %-4s %-6s %-6.2f %+8.3f %-7s %s"
            % (ep["net"], ep["name"], ep["cx"], ep["cy"],
               "/".join(sorted(ep["layers"])), DIR_NAME[(dx, dy)], ln, mg,
               "".join(DIR_NAME[d] for d in dirs_feas),
               " ".join("%s:%.2f(%+.3f)" % (DIR_NAME[(dx2, dy2)], ln2, mg2)
                        for (ln2, dx2, dy2, mg2) in feas)))
    out("")

    # ── 方向负载直方图 ──
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
            len(set((f[0], f[1]) for f in ep["feas"])) == 1]
    out("── 表③ 硬约束端点 (★只有一个可行方向 ⇒ 方向分配机制必须给它这个方向★): %d 个" % len(hard))
    for ep in hard:
        d = (ep["feas"][0][0], ep["feas"][0][1])
        out("   %-18s %-16s (%7.3f,%7.3f) ⇒ %s  可行长 %s"
            % (ep["net"], ep["name"], ep["cx"], ep["cy"], DIR_FULL[d],
               ",".join("%.2f" % f[2] for f in ep["feas"])))
    out("")

    # ── 表④ 冲突图 ──
    #  候选 = 每个端点的 (dir,len) 可行组合;  冲突 = 两条出脚直道间距 < CLEAR
    cands = []
    for ep in eps:
        cs = []
        for (dx, dy, ln, mg) in ep["feas"]:
            key = "tbl%s" % W_MAIN
            sr = ep[key][(dx, dy, ln)][2]
            cs.append({"d": (dx, dy), "ln": ln, "mg": mg, "rect": sr})
        cands.append(cs)

    def conflict(ei, ci, ej, cj):
        ra, rb = ci["rect"], cj["rect"]
        if bbox_gap(bbox(ra), bbox(rb)) >= CLEAR:
            return False
        return GC.rect_rect_dist(ra, rb) < CLEAR - EPS

    edges = []
    for i in range(len(eps)):
        for j in range(i + 1, len(eps)):
            for ci in cands[i]:
                hit = [cj for cj in cands[j] if conflict(i, ci, j, cj)]
                if hit:
                    edges.append((i, j, ci, hit))
    out("── 表④ 出脚方向冲突边 (★两端点【某组方向】同时出脚 ⇒ 净距 < %.2fmm★): %d 条" % (CLEAR, len(edges)))
    out("   (★冲突是【候选组合级】的 ⇒ 换方向/换长度就能解 ⇒ 不是死冲突★)")
    out("")

    # ── 表⑤ 可满足性: 能不能给全部端点同时分配互不打架的方向 ──
    #  约束: 每端点选 1 个候选; 任意两条所选出脚直道间距 ≥ CLEAR
    order = sorted(range(len(eps)), key=lambda i: (len(cands[i]), i))
    # 同网两端点 (★同一未连接条目的两端) 不算互相冲突 (★是同一条线的两头, 实际是同网铜★)
    same_item = {}
    # 重解析: 记录每个端点属于哪个 item
    # (上面已按 item 顺序 append, 每 item 最多 2 个 ⇒ 这里重建)
    idx = 0
    for it in items:
        its = it.get("items") or []
        if len(its) != 2:
            continue
        m0 = re.search(r"\[([^\]]+)\]", its[0].get("description") or "")
        m1 = re.search(r"\[([^\]]+)\]", its[1].get("description") or "")
        if not m0 or not m1 or m0.group(1) != m1.group(1):
            continue
        ok0 = any(e["net"] == m0.group(1) and e["name"] != "走线端" and
                  abs(e["cx"] - its[0]["pos"]["x"]) < 0.5 and
                  abs(e["cy"] - its[0]["pos"]["y"]) < 0.5 for e in eps)
        # 简化: 按顺序配对 (★条目与端点一一对应, 顺序一致★)
        same_item[idx] = same_item.get(idx + 1, idx)
        idx += 2
    # ★更稳的配对: 按坐标匹配
    pair_of = {}
    k = 0
    for it in items:
        its = it.get("items") or []
        if len(its) != 2:
            continue
        found = []
        for sub in its:
            hit = None
            for ei, e in enumerate(eps):
                if ei in pair_of:
                    continue
                if abs(e["cx"] - sub["pos"]["x"]) < 0.6 and abs(e["cy"] - sub["pos"]["y"]) < 0.6:
                    hit = ei
                    break
            if hit is not None:
                found.append(hit)
                pair_of[hit] = "used"
        if len(found) == 2:
            pair_of[found[0]] = found[1]
            pair_of[found[1]] = found[0]
    pair_of = {k2: v for k2, v in pair_of.items() if isinstance(v, int)}

    assign = [None] * len(eps)
    nodes = [0]
    LIMIT = 200000

    def dfs(pos):
        nodes[0] += 1
        if nodes[0] > LIMIT:
            return False
        if pos >= len(order):
            return True
        i = order[pos]
        for ci in cands[i]:
            ok = True
            for j in range(len(eps)):
                if assign[j] is None:
                    continue
                if j == i:
                    continue
                if pair_of.get(i) == j:
                    continue          # ★同一条未连接的两端 = 同一条线 ⇒ 不算冲突
                if conflict(i, ci, j, assign[j]):
                    ok = False
                    break
            if ok:
                assign[i] = ci
                if dfs(pos + 1):
                    return True
                assign[i] = None
        return False

    sat = dfs(0)
    out("── 表⑤ 出脚方向分配可满足性 (★W=%.2f, ★每端点 1 个方向, ★两两净距 ≥ %.2fmm★)" % (W_MAIN, CLEAR))
    out("   端点 %d · 搜索节点 %d · 上限 %d" % (len(eps), nodes[0], LIMIT))
    if sat:
        out("   ★★✔【可满足】⇒ 全部 %d 个端点能同时分配到互不打架的出脚方向/长度 ★★" % len(eps))
        out("      ⇒ ⇒ 【出脚方向分配】机制在几何上是可行的 ⇒ ⇒ A* 只要给它这个【起点方向】就能出发 ★★")
        out("")
        out("   ★分配结果 (★网名 / 端点 / 坐标 / 方向 / 长度 / 余量 / 冲突对端数★):")
        for i, ep in enumerate(eps):
            ci = assign[i]
            nb = 0
            for j in range(len(eps)):
                if assign[j] is None or j == i or pair_of.get(i) == j:
                    continue
                if conflict(i, ci, j, assign[j]):
                    nb += 1
            out("   %-18s %-16s (%7.3f,%7.3f) %-7s %.2f  %+7.3f  ★冲突对 %d"
                % (ep["net"], ep["name"], ep["cx"], ep["cy"],
                   DIR_FULL[ci["d"]], ci["ln"], ci["mg"], nb))
        hist2 = {d: 0 for d in DIRS}
        for ci in assign:
            if ci:
                hist2[ci["d"]] += 1
        out("")
        out("   ★分配后方向负载: " + " · ".join(
            "%s=%d" % (DIR_FULL[d], hist2[d]) for d in DIRS))
    else:
        out("   ★★✘【不可满足 (★在节点上限内没找到解★)】⇒ ⇒ 出脚方向分配也救不了 ⇒ ⇒ 瓶颈更深 ★★")
        out("      (★注: 节点上限 %d ⇒ 若超限截断, ★只能判"疑似不可行", ★不能判死★)" % LIMIT)
    out("")

    # ── 表⑥ 差分对配对体检 ──
    out("── 表⑥ 差分对腿的出脚方向体检 (★P/N 两腿能否各走各的★)")
    bynet = {}
    for i, ep in enumerate(eps):
        bynet.setdefault(ep["net"], []).append(i)
    pairnets = []
    for n, idxs in bynet.items():
        if n.endswith("_P") or n.endswith("_N"):
            base = n[:-2]
            if base + "_P" in bynet and base + "_N" in bynet:
                pairnets.append(base)
    for base in sorted(pairnets):
        ip = bynet[base + "_P"]
        inn = bynet[base + "_N"]
        for a_ in ip:
            for b_ in inn:
                pa, pb = eps[a_], eps[b_]
                da = pa.get("best")
                db = pb.get("best")
                s = "同向(★两腿挤同一条道⇒差分必炸★)" if (da and db and da[0:2] == db[0:2]) else "反向/异向 ✔"
                out("   %-16s P@%-13s (%7.3f,%7.3f) 最优 %-7s | N@%-13s (%7.3f,%7.3f) 最优 %-7s ⇒ %s"
                    % (base, pa["name"], pa["cx"], pa["cy"],
                       DIR_FULL[(da[0], da[1])] if da else "无",
                       pb["name"], pb["cx"], pb["cy"],
                       DIR_FULL[(db[0], db[1])] if db else "无", s))
                if sat and assign[a_] and assign[b_]:
                    s2 = "同向" if assign[a_]["d"] == assign[b_]["d"] else "反向/异向 ✔"
                    out("   %-16s ★分配后: P %s / N %s ⇒ %s" % ("", DIR_FULL[assign[a_]["d"]],
                       DIR_FULL[assign[b_]["d"]], s2))
    out("")

    out("═══════ 汇总 ═══════")
    nfeas = sum(1 for e in eps if e.get("feas"))
    nhard = len(hard)
    out("端点总数 = %d · 有可行方向的 = %d · 无可行方向的 = %d"
        % (len(eps), nfeas, len(eps) - nfeas))
    out("硬约束端点 (单一方向) = %d" % nhard)
    out("冲突边 = %d" % len(edges))
    out("方向分配可满足 = %s" % ("是" if sat else "否"))
    out("")
    out("★★⇒ 【结论】: ★方向分配机制【几何可行性】= %s ⇒ ⇒ 主会话可据此决定要不要做"出脚方向分配"★"
        % ("可做" if sat else "不可做"))

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
                           {"dir": list(assign[i]["d"]), "len": assign[i]["ln"],
                            "margin": assign[i]["mg"]}
                           for i, e in enumerate(eps)} if sat else None),
              "satisfiable": sat}
        open(joutf, "w", encoding="utf-8").write(json.dumps(js, ensure_ascii=False, indent=1))
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
