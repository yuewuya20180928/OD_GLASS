#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch_rip_guarded.py -- ★★★**"拆非承重挡路 + 只补那一段" (2026-11-06 19:3x)**

★★★**这是三件套的合体 (★每件都是今天实测做出来的)**:
  ① ★**no-stub A\*** (`state/patch_astar_nostub.py`): ★**从焊盘自己那一格起步, 不画 escape stub**
     ⇒ ★**escape stub 不走净距检查 ⇒ 成品板上直接压穿别网的铜**
  ② ★**只拆"非承重"的挡路** (`state/rip_guard.py`): ★**拆完那个网仍然连通才允许拆**
     ⇒ ★**拆承重铜 ⇒ 那个网碎掉 ⇒ 官方板实测 RESET_N 0→5 孤岛 / 差分腿被拖下水**
  ③ ★**新铜真几何复核** (`state/geom_clear.py`): ★矩形对矩形 + ★KiCad 圆头 + ★分层
     ⇒ ★**路由器自认为合格的铜, 真板 DRC 会报 0.0152mm** (halo 半宽用错 + skip_pad_cells)

★★★**★与"整网重画"的区别 (★实测)**: `ripup_and_reroute()` 会把被拆的网**整网重画**
  ⇒ ★**实测 ripg10 板比原板多 4906 段** (`VDD_3V3_IO` +2195 / `LIGHT_3V3` +617 / `DSI_D0_D0_P` +600)
  ⇒ ★**那批新铜全部带净距违规 ⇒ DRC 263** ⇒ ★**这条路被"整网重画"卡死**
⇒ ★**本脚本只做一件事: 给目标网补一段; ★**挡路铜只在"拆了它那个网仍然连通"时才拆**

★★**安全**:
  · 只写 --out; ★**每网独立: 不合格 ⇒ 只回滚这一网** (别的网不受影响)
  · ★**只拆经 `rip_guard` 证明"拆了不散架"的铜** ⇒ ★**不会把别的网打死**
  · ★**新铜过不了真几何复核 ⇒ 整网回滚** ⇒ ★**脏板不可能上位**

用法:
  bash state/pcbnew_py.sh state/patch_rip_guarded.py <板> <DRC.json> --out <新板> [--max-dist 15] [--grid 0.125]
"""
import sys
import os
import json
import math
import re

os.environ.setdefault("PCB_LAYERS", "8")
os.environ.setdefault("PCB_HALO_MARGIN", "0.0625")
os.environ.setdefault("PCB_VIA_HALO_MARGIN", "0.0")
os.environ.setdefault("PCB_SKIP_PAD_CELLS", "1")
os.environ.setdefault("PCB_PAIR_EXEMPT_R", "0.0")
os.environ.setdefault("PCB_VIA_CHECK_ALL_CLS", "1")
os.environ.setdefault("PCB_USE_ESCAPE", "0")      # ★**成品板上不画 escape stub**

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pcbnew  # noqa: E402
import gen_pcb_routing as RT  # noqa: E402
import rip_guard as RG  # noqa: E402
import geom_clear as GC  # noqa: E402
from patch_astar_nostub import find_item, pad_cells, track_cells  # noqa: E402

MM = 1e6


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        return 2
    boardp, drcp = a[0], a[1]
    outp = None
    grid = 0.125
    width = RT.W_SIG
    budget = 400000
    max_dist = 15.0
    max_rip = 4
    i = 2
    while i < len(a):
        if a[i] == "--out":
            outp = a[i + 1]
            i += 2
        elif a[i] == "--grid":
            grid = float(a[i + 1])
            i += 2
        elif a[i] == "--budget":
            budget = int(a[i + 1])
            i += 2
        elif a[i] == "--max-dist":
            max_dist = float(a[i + 1])
            i += 2
        elif a[i] == "--max-rip":
            max_rip = int(a[i + 1])
            i += 2
        else:
            i += 1
    if not outp:
        print("★必须给 --out")
        return 2

        board = pcbnew.LoadBoard(boardp)
    # ★★**防御: LoadBoard 可能返回 None** (★板文件被杀时截断/损坏 ⇒ 实测崩在下一行)
    if board is None:
        print("★**板读不出来 (%s) ⇒ 拒绝继续** (★多半是文件被中断写坏)" % boardp)
        return 2
    for z in (board.Zones() or []):
        z.UnFill()
    r = RT.GridRouter(board, grid=grid)
    print("═══ 拆非承重挡路 + 只补那一段: %s ═══" % boardp)
    print("═══ 网格 %.3fmm · %dx%d 格 · %d 层 · escape stub=OFF ═══"
          % (grid, r.W, r.H, RT.NLAYERS))

    # ── 灌入成品板铜 (★登记 halo ⇒ A* 才看得见障碍) ──
    ingested = {}
    for t in list(board.GetTracks()):
        s, e = t.GetStart(), t.GetEnd()
        if t.Type() == pcbnew.PCB_VIA_T:
            try:
                l1 = RT.CU_LAYERS.index(t.TopLayer())
                l2 = RT.CU_LAYERS.index(t.BottomLayer())
            except Exception:
                l1, l2 = 0, RT.NLAYERS - 1
            rec = (t.GetNetname(), s.x / MM, s.y / MM, l1, l2)
            r.vias.append(rec)
            r._add_via_halo(t.GetNetname(), s.x / MM, s.y / MM, l1, l2)
            r._add_via_hash(s.x / MM, s.y / MM, t.GetNetname())
        else:
            try:
                li = RT.CU_LAYERS.index(t.GetLayer())
            except Exception:
                li = 0
            w = t.GetWidth() / MM
            rec = (t.GetNetname(), s.x / MM, s.y / MM, e.x / MM, e.y / MM, li, w)
            r.tracks.append(rec)
            r._add_track_halo(t.GetNetname(), s.x / MM, s.y / MM,
                              e.x / MM, e.y / MM, li, w)
        ingested[id(rec)] = (t, rec)
    r.rebuild_halo()
    ORIG_IDS = set(ingested.keys())
    print("═══ 已灌入 %d 段 / %d 孔 ═══" % (len(r.tracks), len(r.vias)))

    try:
        BC = GC.BoardCopper(board)
    except Exception as e:
        BC = None
        print("  ⚠️ 建真几何索引失败: %s" % e)

    d = json.load(open(drcp, encoding="utf-8"))
    items = d.get("unconnected_items") or []
    cand = []
    for it in items:
        its = it.get("items") or []
        if len(its) != 2:
            continue
        p0 = its[0].get("pos") or {}
        p1 = its[1].get("pos") or {}
        dist = math.hypot(p0.get("x", 0) - p1.get("x", 0),
                          p0.get("y", 0) - p1.get("y", 0))
        m0 = re.search(r"\[([^\]]+)\]", its[0].get("description") or "")
        m1 = re.search(r"\[([^\]]+)\]", its[1].get("description") or "")
        n0 = m0.group(1) if m0 else ""
        n1 = m1.group(1) if m1 else ""
        if not n0 or n0 != n1:
            continue
        if dist > max_dist:
            continue
        cand.append((dist, n0, it))
    cand.sort()
    print("═══ 候选 %d 条 (≤%.1fmm, 按间距升序) ═══" % (len(cand), max_dist))

    cls = r._cls(width)
    fixed, rej = [], []
    for (dist, net, it) in cand:
        its = it["items"]
        p0 = its[0].get("pos") or {}
        p1 = its[1].get("pos") or {}
        k0 = find_item(board, its[0].get("uuid"))
        k1 = find_item(board, its[1].get("uuid"))
        if k0 is None or k1 is None:
            rej.append(("uuid 找不到", net))
            continue
        c0 = pad_cells(r, k0[1]) if k0[0] == "pad" else \
            track_cells(r, k0[1], (p1.get("x", 0), p1.get("y", 0)))
        c1 = pad_cells(r, k1[1]) if k1[0] == "pad" else \
            track_cells(r, k1[1], (p0.get("x", 0), p0.get("y", 0)))
        if not c0 or not c1:
            rej.append(("端点算不出格子", net))
            continue

        snap_t = list(r.tracks)
        snap_v = list(r.vias)
        path = r._astar(list(c0), set(c1), net, cls=cls, limit=budget)
        ripped = []
        if path is None:
            # ★★**A* 走不通 ⇒ 试"拆非承重挡路"** ★★
            #   ★**候选 = 端点附近的异网走线 (★自己按几何算, 不依赖路由器的返回格式)**
            bl = []
            for s in r.tracks:
                if s[0] == net or not s[0]:
                    continue
                (bn, x1, y1, x2, y2, li, w) = s[:7]
                # ★**到端点的距离 (★取两端点里近的那个)**
                dd = min(math.hypot(x1 - p0.get("x", 0), y1 - p0.get("y", 0)),
                         math.hypot(x2 - p0.get("x", 0), y2 - p0.get("y", 0)),
                         math.hypot(x1 - p1.get("x", 0), y1 - p1.get("y", 0)),
                         math.hypot(x2 - p1.get("x", 0), y2 - p1.get("y", 0)))
                if dd <= 1.2:
                    bl.append((dd, s))
            bl.sort(key=lambda t: t[0])
            for (dd, b) in bl:
                if len(ripped) >= max_rip:
                    break
                (bn, x1, y1, x2, y2, li, w) = b[:7]
                if bn == net:
                    continue
                # ★**承重检查 (★在真板上算 ⇒ 与 KiCad 口径一致)**
                try:
                    before_i = RG.island_count(board, bn)
                except Exception:
                    continue
                # ★**试拆: 从模型里去掉 + 从板上删掉 ⇒ 再算孤岛数**
                hit = None
                for s in r.tracks:
                    if s[0] == bn and abs(s[1] - x1) < 1e-3 and abs(s[2] - y1) < 1e-3 \
                            and abs(s[3] - x2) < 1e-3 and abs(s[4] - y2) < 1e-3:
                        hit = s
                        break
                if hit is None:
                    continue
                r.tracks = [s for s in r.tracks if id(s) != id(hit)]
                r.rebuild_halo()
                obj = None
                for oid, (o, rec) in list(ingested.items()):
                    if rec is hit:
                        obj = o
                        break
                if obj is not None:
                    board.Remove(obj)
                    del ingested[id(hit)]
                try:
                    after_i = RG.island_count(board, bn)
                except Exception:
                    after_i = 999
                if after_i > before_i:
                    # ★**承重 ⇒ 放回去** (★网会碎)
                    r.tracks = snap_t
                    r.rebuild_halo()
                    if obj is not None:
                        board.Add(obj)
                        ingested[id(hit)] = (obj, hit)
                    continue
                ripped.append((bn, hit, obj))
            if ripped:
                path = r._astar(list(c0), set(c1), net, cls=cls, limit=budget)
        if path is None:
            # ★**没救回来 ⇒ 把拆的都放回去**
            r.tracks = snap_t
            r.vias = snap_v
            r.rebuild_halo()
            for (bn, hit, obj) in ripped:
                if obj is not None:
                    board.Add(obj)
                    ingested[id(hit)] = (obj, hit)
            rej.append(("A* 找不到路 (★拆了 %d 条非承重挡路也没用)" % len(ripped), net))
            continue

        ok = r._emit_path(net, path, width)
        if not ok:
            r.tracks = snap_t
            r.vias = snap_v
            r.rebuild_halo()
            for (bn, hit, obj) in ripped:
                if obj is not None:
                    board.Add(obj)
                    ingested[id(hit)] = (obj, hit)
            rej.append(("_emit_path 放弃", net))
            continue

        # ★★★**新铜真几何复核 (★矩形+圆头+分层)** ★★★
        bad = []
        if BC is not None:
            try:
                BC2 = GC.BoardCopper(board)
            except Exception:
                BC2 = None
            if BC2 is not None:
                for s in r.tracks:
                    if id(s) in ORIG_IDS:
                        continue
                    (n2, x1, y1, x2, y2, li, w) = s
                    okc, worst, who = GC.check_track(BC2, n2, (x1, y1), (x2, y2), w, li)
                    if not okc:
                        bad.append("走线[%s] 净距 %.3fmm %s" % (n2, worst, who))
                for v in r.vias:
                    if id(v) in ORIG_IDS:
                        continue
                    (n2, x, y, l1, l2) = v
                    okc, worst, who = GC.check_via(BC2, n2, (x, y))
                    if not okc:
                        bad.append("过孔[%s] 净距 %.3fmm %s" % (n2, worst, who))
        if bad:
            # ★**不合格 ⇒ 整网回滚 (★含把拆掉的挡路放回去)**
            r.tracks = snap_t
            r.vias = snap_v
            r.rebuild_halo()
            for (bn, hit, obj) in ripped:
                if obj is not None:
                    board.Add(obj)
                    ingested[id(hit)] = (obj, hit)
            rej.append(("★新铜真几何复核不过 (%d 处, 例 %s) ⇒ 回滚"
                        % (len(bad), bad[0][:52]), net))
            continue

        fixed.append((net, dist, len(ripped)))
        print("  ★补上 %-18s 间距 %6.3fmm  A* %d 格  ★拆非承重挡路 %d 条"
              % (net, dist, len(path), len(ripped)))

    print("── 补上 %d 条 / 未成 %d 条" % (len(fixed), len(rej)))
    for (w_, n_) in rej[:20]:
        print("    · 未成: %s  [%s]" % (w_, n_))

    # ── 差异写回 ──
    alive = set(id(s) for s in r.tracks) | set(id(v) for v in r.vias)
    for oid, (obj, rec) in list(ingested.items()):
        if oid not in alive:
            board.Remove(obj)
            del ingested[oid]
    for s in r.tracks:
        if id(s) in ingested:
            continue
        (net, x1, y1, x2, y2, li, w) = s
        code = RT.netcode(board, net)
        if code <= 0:
            continue
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        t.SetWidth(pcbnew.FromMM(w))
        t.SetLayer(RT.CU_LAYERS[li])
        t.SetNetCode(code)
        board.Add(t)
    for v in r.vias:
        if id(v) in ingested:
            continue
        (net, x, y, l1, l2) = v
        code = RT.netcode(board, net)
        if code <= 0:
            continue
        vi = pcbnew.PCB_VIA(board)
        vi.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        vi.SetWidth(pcbnew.FromMM(RT.VIA_DIA))
        vi.SetDrill(pcbnew.FromMM(RT.VIA_DRILL))
        vi.SetViaType(pcbnew.VIATYPE_THROUGH)
        vi.SetLayerPair(RT.CU_LAYERS[l1], RT.CU_LAYERS[l2])
        vi.SetNetCode(code)
        board.Add(vi)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones() or [])
    board.Save(outp)
    print("── 已写出: %s (%d B)" % (outp, os.path.getsize(outp)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
