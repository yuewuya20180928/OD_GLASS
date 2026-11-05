#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_unconnected_astar.py -- ★★★**用路由器自己的 A* 给成品板补最后一段** (11-06 05:0x)

★★★**为什么这是关键一步 (机器实测链)**:
  ① 官方板 57 项未连接按两头距离分类: <2mm 2 条 · 2~10mm 10 条 · >10mm 45 条 (主体 DSI/CSI)
  ② 直线/L 形/U 形绕排都试过 (state/fix_short_unconnected.py) ⇒ ★**只能补 3 条**
     ⇒ 因为被**别的网的长走线横挡** ⇒ ★**几何模板解不了 ⇒ 得用搜索**
  ③ ★★★**关键发现**: `GridRouter(board)` 的构造函数 ★**把板上已有铜读成障碍图**
     ⇒ ★**可以在成品板上直接跑 A*** ⇒ ★**含换层 (过孔) + 精确净距 + 板边 + 焊盘格**
  ④ ⇒ ★★**这块板从此有了"补最后一段"的能力** ⇒ 不必为了补 3mm 而重跑整轮布线

★★**用法**: `bash state/pcbnew_py.sh state/fix_unconnected_astar.py <板> <DRC.json> --out <新板> [--max-dist 12]`
★**安全**: 只写 --out 路径; ★**只补同网未连接** (差分/跨网天然不匹配 ⇒ 不碰差分几何)
"""
import sys
import os
import math
import json

# ★**必须在 import gen_pcb_routing 之前设好环境** (NLAYERS 等在 import 时读)
os.environ.setdefault("PCB_LAYERS", "8")
os.environ.setdefault("PCB_HALO_MARGIN", "0.20")      # ★官方 v37 的 env
os.environ.setdefault("PCB_VIA_HALO_MARGIN", "0.0")    # ★官方 v37 的 env
os.environ.setdefault("PCB_SKIP_PAD_CELLS", "1")
os.environ.setdefault("PCB_PAIR_EXEMPT_R", "0.0")

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pcbnew  # noqa: E402
import gen_pcb_routing as RT  # noqa: E402

MM = 1e6


def find_item(board, uuid):
    """★按 uuid 在板上找回那一个图元"""
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


def endpoint_cells(r, kind, item, other_xy, net):
    """★算出这个端点可用的起始/目标格集合 (★取端点周围几格 ⇒ 容错)
       同时返回**精确坐标** (★用来做 stub 吸附 ⇒ 避免 track_dangling)"""
    cells = []
    exact = None
    if kind == "pad":
        pos = item.GetPosition()
        cx, cy = pos.x / MM, pos.y / MM
        exact = (cx, cy)
        lays = [0]
        try:
            ls = item.GetLayerSet().Seq()
            lays = [p for p in ls]
        except Exception:
            pass
        i0, j0 = r._ci(cx), r._cj(cy)
        # ★★★2026-11-06 05:2x **只许信号层**: ★**In1/In3/In5/B.Cu 是 GND 平面层**
        #   ⇒ ★**铺了"全部 8 层" ⇒ A* 直接跑到平面上 ⇒ 19 条 track_dangling (实测)**
        # ★★★2026-11-06 05:4x **更严: 只许"焊盘自己有的层"**
        #   ⇒ ★**SMD 焊盘只有 F.Cu ⇒ 起点只能在 F.Cu** ⇒ ★**否则 stub 会落在没有铜的层 ⇒ 悬空**
        _lays = []
        try:
            _ls = item.GetLayerSet().Seq()
            for _l in _ls:
                if _l in RT.CU_LAYERS:
                    _lays.append(RT.CU_LAYERS.index(_l))
        except Exception:
            _lays = [0]
        _lays = [x for x in _lays if x in RT.ROUTE_LAYERS] or [0]
        cand = []
        for li in _lays:
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    i, j = i0 + di, j0 + dj
                    if not (0 <= i < r.W and 0 <= j < r.H):
                        continue
                    gx, gy = r._cx(i), r._cy(j)
                    cand.append((math.hypot(gx - cx, gy - cy), (li, r._idx(i, j))))
        # ★★★2026-11-06 05:6x **按距离排序**: ★**A* 从集合里随便挑一个起点 ⇒ 可能挑最远的**
        #   ⇒ ★**stub 从远处格心斜插到焊盘 ⇒ 必然压到别网 ⇒ 全被拦下 (v6 实测: 一段没落)**
        #   ⇒ ⇒ **按"离端点由近到远"排序** ⇒ 优先用最近的格 ⇒ stub 最短 ⇒ 净距最可能过
        cand.sort(key=lambda t: t[0])
        cells = [c[1] for c in cand]
        return cells, exact
    # track: 取离对方更近的那一头
    s, e = item.GetStart(), item.GetEnd()
    p1 = (s.x / MM, s.y / MM)
    p2 = (e.x / MM, e.y / MM)
    pt = p1 if math.hypot(p1[0] - other_xy[0], p1[1] - other_xy[1]) <= \
        math.hypot(p2[0] - other_xy[0], p2[1] - other_xy[1]) else p2
    exact = pt
    li = item.GetLayer()
    try:
        li = RT.CU_LAYERS.index(li)
    except Exception:
        li = 0
    i0, j0 = r._ci(pt[0]), r._cj(pt[1])
    cand = []
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            i, j = i0 + di, j0 + dj
            if not (0 <= i < r.W and 0 <= j < r.H):
                continue
            gx, gy = r._cx(i), r._cy(j)
            cand.append((math.hypot(gx - pt[0], gy - pt[1]), (li, r._idx(i, j))))
    cand.sort(key=lambda t: t[0])
    cells = [c[1] for c in cand]
    return cells, exact


def main():
    args = sys.argv[1:]
    if len(args) < 4:
        print(__doc__)
        return 2
    boardp, drcp = args[0], args[1]
    outp = None
    max_dist = 12.0
    width = RT.W_SIG
    budget = 300000
    unfill = True
    refill = True
    i = 2
    while i < len(args):
        if args[i] == "--out":
            outp = args[i + 1]
            i += 2
        elif args[i] == "--max-dist":
            max_dist = float(args[i + 1])
            i += 2
        elif args[i] == "--width":
            width = float(args[i + 1])
            i += 2
        elif args[i] == "--budget":
            budget = int(args[i + 1])
            i += 2
        elif args[i] == "--no-unfill":
            unfill = False
            i += 1
        elif args[i] == "--no-refill":
            refill = False
            i += 1
        else:
            i += 1
    if not outp:
        print("★必须给 --out")
        return 2

    board = pcbnew.LoadBoard(boardp)
    d = json.load(open(drcp, encoding="utf-8"))
    items = d.get("unconnected_items", [])
    print("═══ A* 补未连接: %s ═══" % boardp)
    # ★★★2026-11-06 05:1x **先清铜皮填充**: ★**A* 看不见已填充的铜皮**
    #   ⇒ ★**实测: 不清 ⇒ 新线穿过铜皮 ⇒ 147 条 zone clearance 违规**
    #   ⇒ ⇒ 清掉 ⇒ 补铜 ⇒ ★**最后重填** (重填会自己绕开新线 ⇒ 不违规)
    if unfill:
        for z in board.Zones():
            z.UnFill()
        print("═══ 已清 %d 个铜皮填充 (★补完再重填) ═══" % len(list(board.Zones())))
    r = RT.GridRouter(board)
    # ★★★2026-11-06 05:0x **关键**: GridRouter **只把焊盘/板边塞进障碍图, 自己布的线只进 halo 图**
    #   ⇒ ★**成品板上已有铜必须自己灌进去** ⇒ ★**用路由器同一套 API**:
    #   · self.tracks / self.vias  ⇒ 供 _geom_clear 精确净距 + commit 记账
    #   · _add_track_halo / _add_via_halo ⇒ 供 A* 的占位 (净距禁区)
    #   · ★**已灌进去的铜要登记进 _committed ⇒ commit() 不会把它们重写一遍**
    _committed = {}
    n_ing = 0
    for t in board.GetTracks():
        s, e = t.GetStart(), t.GetEnd()
        if t.Type() == pcbnew.PCB_VIA_T:
            try:
                l1 = RT.CU_LAYERS.index(t.TopLayer())
                l2 = RT.CU_LAYERS.index(t.BottomLayer())
            except Exception:
                l1, l2 = 0, RT.NLAYERS - 1
            rec = (t.GetNetname(), s.x / MM, s.y / MM, l1, l2)
            r.vias.append(rec)
            _committed[id(rec)] = rec
            r._add_via_halo(t.GetNetname(), s.x / MM, s.y / MM, l1, l2)
            # ★★★2026-11-06 05:5x **已有过孔必须登记 via_hash**
            #   ⇒ 不登记 ⇒ A* 不知道板上有 408 个孔 ⇒ 新孔贴旧孔 ⇒ DRC hole_to_hole (实测)
            r._add_via_hash(s.x / MM, s.y / MM, t.GetNetname())
            n_ing += 1
        else:
            try:
                li = RT.CU_LAYERS.index(t.GetLayer())
            except Exception:
                li = 0
            w = t.GetWidth() / MM
            rec = (t.GetNetname(), s.x / MM, s.y / MM, e.x / MM, e.y / MM, li, w)
            r.tracks.append(rec)
            _committed[id(rec)] = rec
            r._add_track_halo(t.GetNetname(), s.x / MM, s.y / MM, e.x / MM, e.y / MM, li, w)
            n_ing += 1
    r._committed = _committed
    print("═══ 障碍图: %d 层 · %dx%d 格 (%.2fmm) · ★已灌入成品板铜 %d 图元 ═══" %
          (RT.NLAYERS, r.W, r.H, r.g, n_ing))
    cls = r._cls(width)
    print("═══ 只补两头距离 ≤ %.1fmm 的同网未连接 (预算 %d) ═══" % (max_dist, budget))

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
            failed.append(("两头发的是不同网 ⇒ 不碰", "%s ⇄ %s" % (net_a, net_b)))
            continue
        if dist > max_dist:
            failed.append(("距离 %.1fmm > 阈值 ⇒ 交给路由器" % dist, net_a))
            continue
        k0 = find_item(board, d0.get("uuid"))
        k1 = find_item(board, d1.get("uuid"))
        if k0 is None or k1 is None:
            failed.append(("uuid 找不到板上图元", net_a))
            continue
        c0, e0 = endpoint_cells(r, k0[0], k0[1], (p1.get("x", 0), p1.get("y", 0)), net_a)
        c1, e1 = endpoint_cells(r, k1[0], k1[1], (p0.get("x", 0), p0.get("y", 0)), net_a)
        if not c0 or not c1:
            failed.append(("端点算不出格子", net_a))
            continue
        # ★★★2026-11-06 05:7x **全集合 A* + stub 不过就剔格重试**
        #   ★**教训**: 单独一个起点格 ⇒ A* 直接卡死 (v7 实测 0 条) ⇒ 起点必须是集合
        #   ★**但**: A* 可能挑到"最远"的格 ⇒ stub 斜插 ⇒ 压别网 ⇒ 净距不通过
        #   ⇒ ⇒ **策略: 用全集合跑 A* ⇒ 若 stub 不过 ⇒ 把"这次用的那个格"剔掉 ⇒ 重跑 (最多 4 轮)**
        _c0set = list(c0)
        _c1set = list(c1)
        path = None
        for _try in range(4):
            _p = r._astar(list(_c0set), set(_c1set), net_a, cls=cls, limit=budget)
            if _p is None:
                break
            _g0 = (r._cx(_p[0][1] % r.W), r._cy(_p[0][1] // r.W))
            _g1 = (r._cx(_p[-1][1] % r.W), r._cy(_p[-1][1] // r.W))
            _bad0 = bool(e1) and (abs(e1[0] - _g0[0]) > 1e-6 or abs(e1[1] - _g0[1]) > 1e-6) \
                and not r._geom_clear(net_a, [(e1[0], e1[1], _g0[0], _g0[1])], _p[0][0], width)
            _bad1 = bool(e0) and (abs(e0[0] - _g1[0]) > 1e-6 or abs(e0[1] - _g1[1]) > 1e-6) \
                and not r._geom_clear(net_a, [(e0[0], e0[1], _g1[0], _g1[1])], _p[-1][0], width)
            if not _bad0 and not _bad1:
                path = _p
                break
            # ★剔掉这次用的格 ⇒ 让 A* 换一个
            if _bad0:
                _c0set = [c for c in _c0set if c != _p[0]]
            if _bad1:
                _c1set = [c for c in _c1set if c != _p[-1]]
            if not _c0set or not _c1set:
                break
        if path is None:
            failed.append(("A* 找不到路 / stub 净距不过", net_a))
            continue
        # ★★2026-11-06 05:1x **端点吸附**: ★**不吸附 ⇒ 新线端点落在格心 ⇒ track_dangling**
        #   ⇒ ★**stub_start/stub_end 传精确坐标** (焊盘中心 / 原走线端点)
        # ★★★2026-11-06 05:3x ★★**方向陷阱 (实测 18 条悬空的真凶)**:
        #   路由器里的调用是 `self._astar(sb, set(sa), net, ...)` ⇒ ★**第一个参数是"目标"、第二个是"源"**
        #   ⇒ ★**返回路径的顺序是 [目标 ... 源]** ⇒ ★**所以 stub_start 要给"目标端"(e1)、stub_end 给"源端"(e0)**
        #   ⇒ ★**我先前给反了 ⇒ 首尾接错 ⇒ 18 条 track_dangling**
        ok = r._emit_path(net_a, path, width,
                          stub_start=(e1[0], e1[1], e1[0], e1[1]) if e1 else None,
                          stub_end=(e0[0], e0[1], e0[0], e0[1]) if e0 else None)
        if not ok:
            failed.append(("_emit_path 放弃(净距/板边/过孔)", net_a))
            continue
        fixed.append((net_a, dist, len(path)))
        print("  ★补上 %-16s 间距 %6.3fmm  A* 路径 %d 格" % (net_a, dist, len(path)))

    print("── 补上 %d 条 / 未成 %d 条" % (len(fixed), len(failed)))
    for w_, n_ in failed[:25]:
        print("    · 未成: %s %s" % (w_, n_))
    r.commit(board)
    if refill:
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        print("═══ 已重填 %d 个铜皮 ═══" % len(list(board.Zones())))
    board.Save(outp)
    print("── 已写出: %s (%d B)" % (outp, os.path.getsize(outp)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
