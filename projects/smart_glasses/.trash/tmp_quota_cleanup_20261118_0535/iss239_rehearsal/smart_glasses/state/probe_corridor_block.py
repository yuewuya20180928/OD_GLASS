# -*- coding: utf-8 -*-
"""probe_corridor_block.py -- ★**真归因**: 对每条失败段, 沿 start->goal 直线采样,
   算"谁的铜在几何上真的挡住了这条直路" (实际净距 < 规则净距) ⇒ 不猜, 只报事实
   用法: bash state/pcbnew_py.sh state/probe_corridor_block.py <板> <fail_detail.json>"""
import sys, json, math, collections, pcbnew

BOARD = sys.argv[1]; DET = sys.argv[2]
b = pcbnew.LoadBoard(BOARD); mm = 1e6
CLEAR = 0.20

# ── 收集所有异网铜 (走线 + 过孔) ──
cu = []
for t in b.GetTracks():
    tn = t.GetNetname()
    if t.GetClass() == "PCB_VIA":
        p = t.GetPosition()
        r = t.GetWidth()/2.0/mm if hasattr(t, "GetWidth") else 0.30
        cu.append((tn, "VIA", p.x/mm, p.y/mm, r))
    else:
        s = t.GetStart(); e = t.GetEnd()
        w = (t.GetWidth()/mm) if hasattr(t, "GetWidth") else 0.25
        cu.append((tn, "TRK", s.x/mm, s.y/mm, e.x/mm, e.y/mm, w/2.0))

def seg_pt_dist(px, py, ax, ay, bx, by):
    vx, vy = bx-ax, by-ay; L2 = vx*vx+vy*vy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px-ax)*vx+(py-ay)*vy)/L2))
    return math.hypot(px-(ax+t*vx), py-(ay+t*vy))

d = json.load(open(DET))
rank = collections.Counter(); rank_strict = collections.Counter()
nseg = 0; nblocked = 0
detail = []
for x in d:
    if "start" not in x or "goal" not in x: continue
    net = x["net"]; s = tuple(x["start"]); g = tuple(x["goal"]); nseg += 1
    L = math.hypot(g[0]-s[0], g[1]-s[1])
    N = max(2, int(L/0.15))
    pts = [(s[0]+(g[0]-s[0])*i/N, s[1]+(g[1]-s[1])*i/N) for i in range(N+1)]
    hit = collections.Counter(); minclear = {}
    for c in cu:
        if c[0] == net: continue
        if c[1] == "VIA":
            _, _, cx, cy, r = c
            dist = min(math.hypot(px-cx, py-cy) for (px, py) in pts) - r
        else:
            _, _, ax, ay, bx, by, hw = c
            dist = min(seg_pt_dist(px, py, ax, ay, bx, by) for (px, py) in pts) - hw
        need = CLEAR
        if dist < need:
            hit[c[0]] += 1
            if c[0] not in minclear or dist < minclear[c[0]]:
                minclear[c[0]] = dist
    if hit:
        nblocked += 1
        for k in hit: rank[k] += 1
        for k, v in minclear.items():
            if v < 0.05: rank_strict[k] += 1
        detail.append((net, x.get("pad"), L, hit.most_common(3), min(minclear.values())))

print("失败段 %d 条; ★**几何上被真实铜挡住直路**的 = %d 条 (%.0f%%)" % (nseg, nblocked, 100.0*nblocked/max(1,nseg)))
print()
print("── 谁挡住了多少条失败段的直路 (真净距 < 0.20mm) ──")
for k, v in rank.most_common(18):
    print("   %-28s %3d 条   (其中净距 <0.05mm 的 %d)" % (k, v, rank_strict.get(k,0)))
print()
print("── 逐条 (net, 直线长度, 最主要阻塞者, 最小净距) ──")
for net, pad, L, hit, mc in sorted(detail, key=lambda t: t[4])[:26]:
    print("   %-18s L=%6.1f  min净距=%+.4f  阻塞者=%s" % (net, L, mc, hit))
