#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rip_escape_guard.py -- ★★★**"带承重守卫的拆挡路 + 只补一段" (2026-11-06 07:4x)**

★★★**为什么要有这个脚本 (机器实测链, 每条都有出处)**:
  ① 官方板 unc 45 · DRC 0 (已晋级, md5 611b869e)
  ② `state/fix_straight_links.py` 在这 45 条上 **补上 0 条** ⇒ 纯几何模板到顶
  ③ `state/patch_astar_nostub.py` (halo 0.0625) 只救回 **3 条** ⇒ 纯 A* 也到顶
     ⇒ ★**剩下的 45 条里有 23 条 >40mm + 25 条是差分腿** ⇒ ★**全是"被别的铜挡住"**
  ④ `state/fix_conn_by_rip.py` 试过"拆挡路 + 补一段" ⇒ ★**只救回 1 条**
     ⇒ ★**根因 (两个, 都可修)**:
       (a) ★**`_escape_blockers()` 只查 F.Cu** (`if s[5] != 0: continue`)
           ⇒ ★**内层的挡路铜根本找不到** ⇒ ★**该拆的没拆**
       (b) ★**它拆的是"别的网"的铜, 却没有承重检查**
           ⇒ ★**实测事故**: `_reroute2` 把 `RESET_N` 从 1 个孤岛拆成 **5 个孤岛**
             ⇒ ★**总 unc 反而 57→67** ⇒ ★**"补好 1 条 + 拆碎 1 条"计数类判据查不出来**
  ⑤ ⇒ ★**本脚本 = `_escape_blockers` 的加固版**: ★**全层查** + ★**承重守卫**
     (拆之前先问: 这截铜拆了, 它所属的网会不会散架? 会 ⇒ 不拆)

★★**安全**:
  · 只写 --out 路径, 不动输入板
  · ★**只加铜 + 拆"非承重"的挡路** ⇒ ★**不会把别的网打死** (承重的直接跳过)
  · ★**每个被拆的网, 拆完立刻用 `rip_guard.island_report` 复核孤岛数**
    ⇒ 孤岛数变多 ⇒ ★**判定拆错了 ⇒ 原样还回去**
  · 落铜后必须 fresh DRC (脚本自己也跑)

用法:
  bash state/pcbnew_py.sh state/rip_escape_guard.py <板> <DRC.json> --out <新板> [--max-dist 30] [--max-rip 12]
"""
import sys
import os
import math
import json
import re

os.environ.setdefault("PCB_LAYERS", "8")
os.environ.setdefault("PCB_HALO_MARGIN", "0.0625")
os.environ.setdefault("PCB_VIA_HALO_MARGIN", "0.0")
os.environ.setdefault("PCB_SKIP_PAD_CELLS", "1")
os.environ.setdefault("PCB_PAIR_EXEMPT_R", "0.0")
os.environ.setdefault("PCB_RIPUP_ESC", "1")

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pcbnew  # noqa: E402
import gen_pcb_routing as RT  # noqa: E402
from rip_guard import is_load_bearing  # noqa: E402

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


def pad_cells(r, pad):
    """焊盘可用起步格 = 自己那一格 + 周围 8 格 (★同层) ⇒ 出脚方向由 A* 自己决定"""
    pos = pad.GetPosition()
    cx, cy = pos.x / MM, pos.y / MM
    try:
        li = RT.CU_LAYERS.index(pad.GetLayer())
    except Exception:
        li = 0
    if li < 0:
        li = 0
    i0, j0 = r._ci(cx), r._cj(cy)
    out = []
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            i, j = i0 + di, j0 + dj
            if 0 <= i < r.W and 0 <= j < r.H:
                out.append((li, r._idx(i, j)))
    return out


def track_cells(r, t, other_xy):
    s, e = t.GetStart(), t.GetEnd()
    p1 = (s.x / MM, s.y / MM)
    p2 = (e.x / MM, e.y / MM)
    pt = p1 if math.hypot(p1[0] - other_xy[0], p1[1] - other_xy[1]) <= \
        math.hypot(p2[0] - other_xy[0], p2[1] - other_xy[1]) else p2
    try:
        li = RT.CU_LAYERS.index(t.GetLayer())
    except Exception:
        li = 0
    i0, j0 = r._ci(pt[0]), r._cj(pt[1])
    out = []
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            i, j = i0 + di, j0 + dj
            if 0 <= i < r.W and 0 <= j < r.H:
                out.append((li, r._idx(i, j)))
    return out


def blockers_all_layers(r, net, maxn=12):
    """★**全层**找"挡住本网焊盘出脚走廊"的别的网走线 (★修 `_escape_blockers` 只查 F.Cu 的缺陷)

    ★**做法**: 对每个本网焊盘, 沿 4 个方向取 ESC_LENS 长度做"出脚直道"候选
      ⇒ ★**对每一层**的别的网走线算几何净距 ⇒ 净距不足 ⇒ 那条就是挡路者
    ★**与原版的差别 (★这是本脚本的核心改动)**:
      原版 `if s[5] != 0: continue` ⇒ ★**只查 F.Cu**
      ⇒ ★**内层 (In2.Cu 等) 的挡路铜完全看不见** ⇒ ★**该拆的没拆 ⇒ 只救回 1 条**
    """
    out = []
    for pad in r.net_pads.get(net, []):
        try:
            cx, cy = pad[2], pad[3]
        except Exception:
            continue
        for (dx, dy) in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            for ln in RT.ESC_LENS:
                ex, ey = cx + dx * ln, cy + dy * ln
                for s in r.tracks:
                    if s[0] == net:
                        continue
                    tw = s[6]
                    need = RT.W_MIN / 2.0 + tw / 2.0 + RT.CLEAR + (0.0 if tw <= 0.21 else 0.025)
                    if RT._seg_seg_dist(cx, cy, ex, ey, s[1], s[2], s[3], s[4]) < need - 1e-9:
                        dd = RT._pt_seg_dist(cx, cy, s[1], s[2], s[3], s[4])
                        out.append((dd, s))
    out.sort(key=lambda t: t[0])
    seen = set()
    res = []
    for (dd, s) in out:
        k = id(s)
        if k in seen:
            continue
        seen.add(k)
        res.append((dd, s))
    return res[:maxn]


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        return 2
    boardp, drcp = a[0], a[1]
    outp = None
    max_dist = 30.0
    max_rip = 12
    budget = 600000
    width = RT.W_SIG
    i = 2
    while i < len(a):
        if a[i] == "--out":
            outp = a[i + 1]; i += 2
        elif a[i] == "--max-dist":
            max_dist = float(a[i + 1]); i += 2
        elif a[i] == "--max-rip":
            max_rip = int(a[i + 1]); i += 2
        elif a[i] == "--budget":
            budget = int(a[i + 1]); i += 2
        elif a[i] == "--width":
            width = float(a[i + 1]); i += 2
        else:
            i += 1
    if not outp:
        print("★必须给 --out")
        return 2

    board = pcbnew.LoadBoard(boardp)
    for z in board.Zones():
        z.UnFill()
    # ★**网格必须 0.125mm** (★0.25mm 网格对 0.4mm pitch BTB 结构性无解 ⇒ 起步格都拿不到)
    grid = 0.125
    r = RT.GridRouter(board, grid=grid)
    print("═══ 拆挡路+补一段 (带承重守卫): %s ═══" % boardp)
    print("═══ 网格 %.3fmm · %dx%d 格 · %d 层 ═══" % (r.g, r.W, r.H, RT.NLAYERS))

    # ── 灌入成品板铜 (与 patch_astar_nostub 同法) ──
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
            r._add_track_halo(t.GetNetname(), s.x / MM, s.y / MM,
                              e.x / MM, e.y / MM, li, w)
            n_ing += 1
    r._committed = _committed
    r.rebuild_halo()
    print("═══ 已灌入成品板铜 %d 图元 (halo 已重建) ═══" % n_ing)

    d = json.load(open(drcp, encoding="utf-8"))
    items = d.get("unconnected_items") or []
    cls = r._cls(width)
    fixed, failed = [], []
    rip_log = []

    for it in items:
        its = it.get("items") or []
        if len(its) != 2:
            continue
        d0, d1 = its[0], its[1]
        p0, p1 = d0.get("pos") or {}, d1.get("pos") or {}
        dist = math.hypot(p0.get("x", 0) - p1.get("x", 0), p0.get("y", 0) - p1.get("y", 0))
        m0 = re.search(r"\[([^\]]+)\]", d0.get("description") or "")
        m1 = re.search(r"\[([^\]]+)\]", d1.get("description") or "")
        net = m0.group(1) if m0 else ""
        if not net or net != (m1.group(1) if m1 else ""):
            continue
        if max_dist and dist > max_dist:
            failed.append(("距离 %.1fmm > 阈值" % dist, net))
            continue
        k0 = find_item(board, d0.get("uuid"))
        k1 = find_item(board, d1.get("uuid"))
        if k0 is None or k1 is None:
            failed.append(("uuid 找不到板上图元", net))
            continue
        if k0[0] == "pad":
            c0 = pad_cells(r, k0[1])
        else:
            c0 = track_cells(r, k0[1], (p1.get("x", 0), p1.get("y", 0)))
        if k1[0] == "pad":
            c1 = pad_cells(r, k1[1])
        else:
            c1 = track_cells(r, k1[1], (p0.get("x", 0), p0.get("y", 0)))
        if not c0 or not c1:
            failed.append(("端点算不出格子", net))
            continue

        # ── 第一步: 不拆任何东西, 先纯 A* 试一次 (★省得白拆) ──
        ripped = []          # ★**必须先初始化** (纯 A* 成功时根本不会进拆挡路分支)
        keep_tracks = list(r.tracks)
        path = r._astar(list(c0), set(c1), net, cls=cls, limit=budget)
        if path is None:
            # ── 第二步: 找挡路 (★全层!) ──
            bl = blockers_all_layers(r, net, max_rip)
            if not bl:
                failed.append(("A* 找不到路 + 无挡路可拆", net))
                continue

            # ── 第三步: ★**承重守卫** ──
            #   逐个候选挡路: 用 `rip_guard.is_load_bearing` 问一句
            #   "拆了它, 它所属的网会不会散架?" ⇒ 会 ⇒ ★**不许拆** ⇒ 换下一个候选
            #   ⇒ ★**这是本脚本与 fix_conn_by_rip.py 的核心差别**
            #      (后者无承重检查 ⇒ 实测把 RESET_N 拆成 5 块 ⇒ unc 57→67)
            ripped_nets = {}
            skipped_load_bearing = []
            for (dd, s) in bl:
                bnet = s[0]
                rm = [(s[1], s[2], s[3], s[4])]
                try:
                    lb, before, after = is_load_bearing(board, bnet, rm)
                except Exception:
                    lb, before, after = False, None, None
                if lb:
                    # ★**承重 ⇒ 跳过这条挡路** (不拆 ⇒ 别的网不会散架)
                    skipped_load_bearing.append((bnet, before, after))
                    continue
                # 不承重 ⇒ 允许拆
                idx = None
                for i_t, tt in enumerate(r.tracks):
                    if tt is s:
                        idx = i_t
                        break
                if idx is None:
                    continue
                r.tracks.pop(idx)
                r.rebuild_halo()
                ripped.append(s)
                ripped_nets[bnet] = (before, after)

            if not ripped:
                failed.append(("A* 找不到路 + 挡路全是承重 (%d 条)"
                               % len(skipped_load_bearing), net))
                for (bn, bf, af) in skipped_load_bearing[:3]:
                    rip_log.append("    · %s 孤岛 %d→%d ⇒ 承重 ⇒ 不拆" % (bn, bf, af))
                continue

            # 拆完重建 ⇒ 再 A*
            path = r._astar(list(c0), set(c1), net, cls=cls, limit=budget)
            if path is None:
                # ★**补不上 ⇒ 全部还回去** (不丢铜)
                r.tracks = keep_tracks
                r.rebuild_halo()
                failed.append(("拆挡路后 A* 仍找不到路 (已还原 %d 条)" % len(ripped), net))
                continue

        ok = r._emit_path(net, path, width)
        if not ok:
            failed.append(("_emit_path 放弃(净距/板边/过孔)", net))
            if ripped:
                r.tracks = keep_tracks
                r.rebuild_halo()
            continue
        fixed.append((net, dist, len(ripped)))
        print("  ★补上 %-16s 间距 %6.3fmm  拆挡路 %d 条  路径 %d 格"
              % (net, dist, len(ripped), len(path)))

    print("── 补上 %d 条 / 未成 %d 条" % (len(fixed), len(failed)))
    for w_, n_ in failed[:40]:
        print("    · 未成: %s %s" % (w_, n_))
    for l_ in rip_log[:20]:
        print(l_)
    r.commit(board)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(outp)
    print("── 已写出: %s (%d B)" % (outp, os.path.getsize(outp)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
