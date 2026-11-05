#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_conn_by_rip.py -- ★★★**成品板"补一段"= 拆必要挡路 + 只补那一段连接** (11-06 07:0x)

★★★**为什么是这套 (11-06 06:5x~07:0x 实测链, 三个坑都踩过)**:
  ① 纯几何模板 (直/L/U) ⇒ 只能补 3 条 (被别网长走线横挡)
  ② 纯 A* (不拆挡路) ⇒ 能补 13 条, 但扣净距后只剩 1 条
  ③ ★**"把网整网重布" (ripup_and_reroute) ⇒ 救回 2 个网, 但产出 245 条 DRC 违规**
     ⇒ ⇒ ★**根因: 整网重布会让路由器重做"出脚 stub"** ⇒ ★**出脚 stub 的前提是空板**
       ⇒ ★**成品板上 ⇒ 几百条 0.25mm stub 撞成一堆 ⇒ 99×GND + 98×VDD_1V8_IO 短路**
     ⇒ ⇒ ★**⇒ 成品板绝不能整网重布**

★**⇒ 本脚本的做法 (★成品板正确打法)**:
  1. 灌入成品板铜 (tracks/vias + halo + via_hash) ⇒ A* 才看得见真实障碍
  2. 清铜皮填充 (A* 看不见已填充铜皮 ⇒ 会穿皮)
  3. 对每条未连接: ★**用路由器自己的 `_escape_blockers()` 找出"出脚走廊"上的挡路铜**
  4. ★**只拆那些挡路** ⇒ A* 补那一段连接 ⇒ ★**不重布整网 ⇒ 不产生出脚 stub 群**
  5. 补不上 ⇒ ★**把挡路原样还回去** (不丢铜)
  6. 差异写回板 + 重填铜皮 ⇒ ★**必须 fresh DRC**

用法:
  bash state/pcbnew_py.sh state/fix_conn_by_rip.py <板> <DRC.json> --out <新板> [--max-dist 12] [--max-rip 8]
"""
import sys
import os
import math
import json
import re

os.environ.setdefault("PCB_LAYERS", "8")
os.environ.setdefault("PCB_HALO_MARGIN", "0.20")
os.environ.setdefault("PCB_VIA_HALO_MARGIN", "0.0")
os.environ.setdefault("PCB_SKIP_PAD_CELLS", "1")
os.environ.setdefault("PCB_PAIR_EXEMPT_R", "0.0")
os.environ.setdefault("PCB_RIPUP_ESC", "1")

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pcbnew  # noqa: E402
import gen_pcb_routing as RT  # noqa: E402

MM = 1e6


def find_item(board, uuid):
    if not uuid:
        return None
    for t in board.GetTracks():
        try:
            if t.m_Uuid.AsString() == uuid:
                return ("track", t)
        except Exception:
            pass
    for f in board.GetFootprints():
        for p in f.Pads():
            try:
                if p.m_Uuid.AsString() == uuid:
                    return ("pad", p)
            except Exception:
                pass
    return None


def endpoint_info(r, kind, item, other_xy):
    """★返回 (候选格列表(按距离排序), 精确坐标)"""
    cand = []
    exact = None
    if kind == "pad":
        pos = item.GetPosition()
        cx, cy = pos.x / MM, pos.y / MM
        exact = (cx, cy)
        lays = []
        try:
            for _l in item.GetLayerSet().Seq():
                if _l in RT.CU_LAYERS:
                    lays.append(RT.CU_LAYERS.index(_l))
        except Exception:
            lays = [0]
        lays = [x for x in lays if x in RT.ROUTE_LAYERS] or [0]
        i0, j0 = r._ci(cx), r._cj(cy)
        for li in lays:
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    i, j = i0 + di, j0 + dj
                    if not (0 <= i < r.W and 0 <= j < r.H):
                        continue
                    gx, gy = r._cx(i), r._cy(j)
                    cand.append((math.hypot(gx - cx, gy - cy), (li, r._idx(i, j))))
    else:
        s, e = item.GetStart(), item.GetEnd()
        p1 = (s.x / MM, s.y / MM)
        p2 = (e.x / MM, e.y / MM)
        pt = p1 if math.hypot(p1[0] - other_xy[0], p1[1] - other_xy[1]) <= \
            math.hypot(p2[0] - other_xy[0], p2[1] - other_xy[1]) else p2
        exact = pt
        try:
            li = RT.CU_LAYERS.index(item.GetLayer())
        except Exception:
            li = 0
        i0, j0 = r._ci(pt[0]), r._cj(pt[1])
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                i, j = i0 + di, j0 + dj
                if not (0 <= i < r.W and 0 <= j < r.H):
                    continue
                gx, gy = r._cx(i), r._cy(j)
                cand.append((math.hypot(gx - pt[0], gy - pt[1]), (li, r._idx(i, j))))
    cand.sort(key=lambda t: t[0])
    return [c[1] for c in cand], exact



def _stub_ok(r, net, exact, grid, layer, width):
    """★stub 段 (精确端点 → 格心) 是否净距通过
    ★**候选**: 直连 / 4 种 L 形 (★直连常斜插压到别网 ⇒ 绕一下就过)"""
    if not exact:
        return True
    if abs(exact[0] - grid[0]) < 1e-6 and abs(exact[1] - grid[1]) < 1e-6:
        return True
    if r._geom_clear(net, [(exact[0], exact[1], grid[0], grid[1])], layer, width):
        return True
    mx, my = (exact[0] + grid[0]) / 2.0, (exact[1] + grid[1]) / 2.0
    for c in ((mx, exact[1]), (exact[0], my), (mx, grid[1]), (grid[0], my)):
        segs = [(exact[0], exact[1], c[0], c[1]), (c[0], c[1], grid[0], grid[1])]
        if r._geom_clear(net, segs, layer, width):
            return True
    return False


def main():
    args = sys.argv[1:]
    if len(args) < 4:
        print(__doc__)
        return 2
    boardp, drcp = args[0], args[1]
    outp = None
    max_dist = 12.0
    width = RT.W_SIG
    max_rip = 8
    budget = 400000
    i = 2
    while i < len(args):
        if args[i] == "--out":
            outp = args[i + 1]
            i += 2
        elif args[i] == "--max-dist":
            max_dist = float(args[i + 1])
            i += 2
        elif args[i] == "--max-rip":
            max_rip = int(args[i + 1])
            i += 2
        elif args[i] == "--budget":
            budget = int(args[i + 1])
            i += 2
        else:
            i += 1
    if not outp:
        print("★必须给 --out")
        return 2

    board = pcbnew.LoadBoard(boardp)
    for z in board.Zones():
        z.UnFill()
    r = RT.GridRouter(board)
    print("═══ 补一段(拆挡路版): %s ═══" % boardp)

    # ── 灌入成品板铜 ──
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
            r._add_via_hash(s.x / MM, s.y / MM, t.GetNetname())
        else:
            try:
                li = RT.CU_LAYERS.index(t.GetLayer())
            except Exception:
                li = 0
            rec = (t.GetNetname(), s.x / MM, s.y / MM, e.x / MM, e.y / MM, li, t.GetWidth() / MM)
            r.tracks.append(rec)
        ingested[id(rec)] = (t, rec)
    r.rebuild_halo()
    print("═══ 已灌入 %d 段 / %d 孔 (halo 已重建) · 已清铜皮填充 ═══" % (len(r.tracks), len(r.vias)))

    d = json.load(open(drcp, encoding="utf-8"))
    items = d.get("unconnected_items", [])
    cls = r._cls(width)
    fixed, failed = [], []
    for it in items:
        its = it.get("items", [])
        if len(its) != 2:
            failed.append(("条目不是两两相连", ""))
            continue
        d0, d1 = its[0], its[1]
        p0, p1 = d0.get("pos") or {}, d1.get("pos") or {}
        dist = math.hypot(p0.get("x", 0) - p1.get("x", 0), p0.get("y", 0) - p1.get("y", 0))
        na = d0.get("description", "").split("[")
        nb = d1.get("description", "").split("[")
        net_a = na[1].split("]")[0] if len(na) > 1 else ""
        net_b = nb[1].split("]")[0] if len(nb) > 1 else ""
        if not net_a or net_a != net_b:
            continue
        if dist > max_dist:
            continue
        k0 = find_item(board, d0.get("uuid"))
        k1 = find_item(board, d1.get("uuid"))
        if k0 is None or k1 is None:
            failed.append(("uuid 找不到板上图元", net_a))
            continue
        c0, e0 = endpoint_info(r, k0[0], k0[1], (p1.get("x", 0), p1.get("y", 0)))
        c1, e1 = endpoint_info(r, k1[0], k1[1], (p0.get("x", 0), p0.get("y", 0)))
        if not c0 or not c1:
            failed.append(("端点算不出格子", net_a))
            continue

        # ★★★**拆挡路**: ★**用路由器自己的 `_escape_blockers` (出脚走廊感知)**
        bl = r._escape_blockers(net_a, max_rip) if hasattr(r, "_escape_blockers") else []
        bl = bl or r._blockers_for(net_a, r._net_start_cells(net_a), max_rip)
        ripped = []
        if bl:
            keep = []
            for s in r.tracks:
                hit = None
                for b in bl:
                    # b = (net, x1, y1, x2, y2, layer, width)
                    if b[0] != s[0]:
                        continue
                    if abs(b[1] - s[1]) < 1e-6 and abs(b[2] - s[2]) < 1e-6 \
                            and abs(b[3] - s[3]) < 1e-6 and abs(b[4] - s[4]) < 1e-6:
                        hit = s
                        break
                if hit is not None:
                    ripped.append(hit)
                else:
                    keep.append(s)
            r.tracks = keep
            r.rebuild_halo()

        # ★A* 补那一段
        path = None
        _c0set = list(c0)
        _c1set = list(c1)
        for _try in range(4):
            _p = r._astar(list(_c0set), set(_c1set), net_a, cls=cls, limit=budget)
            if _p is None:
                break
            _g0 = (r._cx(_p[0][1] % r.W), r._cy(_p[0][1] // r.W))
            _g1 = (r._cx(_p[-1][1] % r.W), r._cy(_p[-1][1] // r.W))
            _bad0 = not _stub_ok(r, net_a, e1, _g0, _p[0][0], width)
            _bad1 = not _stub_ok(r, net_a, e0, _g1, _p[-1][0], width)
            if not _bad0 and not _bad1:
                path = _p
                break
            if _bad0:
                _c0set = [c for c in _c0set if c != _p[0]]
            if _bad1:
                _c1set = [c for c in _c1set if c != _p[-1]]
            if not _c0set or not _c1set:
                break

        n_before = len(r.tracks)
        why = "A* 找不到路"
        if path is not None:
            ok = r._emit_path(net_a, path, width,
                              stub_start=(e1[0], e1[1], e1[0], e1[1]) if e1 else None,
                              stub_end=(e0[0], e0[1], e0[0], e0[1]) if e0 else None)
            if not ok:
                why = "_emit_path 拒绝(过孔/板边/净距)"
                path = None
                r.tracks = r.tracks[:n_before]
        if path is None:
            # ★失败 ⇒ 把挡路原样还回去 (不丢铜)
            if ripped:
                r.tracks = r.tracks + ripped
                r.rebuild_halo()
            failed.append(("%s (拆 %d 挡路已还原)" % (why, len(ripped)), net_a))
            continue
        fixed.append((net_a, dist, len(ripped)))
        print("  ★补上 %-16s 间距 %6.3fmm  拆挡路 %d 条  路径 %d 格" %
              (net_a, dist, len(ripped), len(path)))

    print("── 补上 %d 条 / 未成 %d 条" % (len(fixed), len(failed)))
    for w_, n_ in failed[:20]:
        print("    · 未成: %s %s" % (w_, n_))

    # ── 差异写回 ──
    alive = set(id(s) for s in r.tracks) | set(id(v) for v in r.vias)
    n_del = n_add = 0
    for oid, (obj, rec) in list(ingested.items()):
        if oid not in alive:
            board.Remove(obj)
            del ingested[oid]
            n_del += 1
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
        ingested[id(s)] = (t, s)
        n_add += 1
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
        ingested[id(v)] = (vi, v)
        n_add += 1
    print("── 差异: 删 %d 个旧图元 / 加 %d 个新图元 (净 %+d)" % (n_del, n_add, n_add - n_del))

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(outp)
    print("── 已写出: %s (%d B)" % (outp, os.path.getsize(outp)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
