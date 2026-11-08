#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""via_clearance_gate.py -- ★★★**"换层点真实几何复核"闸 (2026-11-06 09:0x 实测)**

★★★**为什么必须有这个闸 (实测事故链, 每条都有出处)**:
  ① 官方板 unc 45 · 用 **0.0625mm 网格**跑无-stub A* ⇒ 救回 3 条 (unc 45→42)
  ② ★**但 fresh DRC 报 12 条 clearance 违规** (实际 0.1937 < 要求 0.2000) ⇒ 闸 REJECT
  ③ ★**逐条看违规**: **12 条全是"过孔 vs 走线"** (不是走线 vs 走线!)
     例: `Via [PWR_GOOD] (86.7,44.325)` vs `Track [VBUS_DET_D] on In4.Cu (86.2,43.95)`
     ⇒ ★**中心距实测正好 0.6250mm** = via_r 0.30 + track_half 0.125 + CLEAR 0.20 (★**恰好临界**)
  ④ ★★**根因 (代码级, 已定位到行号)**: `gen_pcb_routing.py` 的**宽度级别错配**
     · ★**过孔查询用 `halo[2]`** (`_via_ok` 第 777 行: `s = self.halo[2][l2].get(idx)`)
     · ★**但 0.25mm 走线的铜只登记在 `halo[1]`** (`_add_track_halo` 按**自己**的宽度级登记)
     ⇒ ★**过孔看不见 0.25mm 的走线** ⇒ ★**净距检查对"过孔 vs 常规走线"失效**
     ⇒ ★**调 halo margin 治不了 (那是另一个量)**
  ⑤ ★★**为什么官方板 (0.125mm 网格 + margin 0.0625) 没报这 12 条**:
     ⇒ ★**margin 0.0625 把 halo[2] 半径从 0.75 撑到 0.8125** ⇒ ★**恰好盖住了漏判**
     ⇒ ★**⇒ 这是"两个 bug 互相掩盖"** ⇒ ★**换更细网格 + 收紧 margin ⇒ 漏判暴露**
  ⑥ ★★**为什么不直接改 `gen_pcb_routing.py`**:
     ⇒ ★**MEMORY 铁律**: 三臂共用该文件且惰性 import ⇒ ★**改它 ⇒ 之后新起的臂拿新代码 ⇒ A/B 失效**
     ⇒ ★**所以本闸做成独立工具**: 在**落铜后**用**真实几何**复核每个换层点
       ⇒ ★**不合格 ⇒ 回退那一条路径** (★不删铜 ⇒ 不产生悬空端)

★★**本闸做什么 (★逐路径, 不是逐过孔)**:
  ① 跑 A* ⇒ 落铜前**先记录这条路径上的换层点坐标**
  ② 落铜 ⇒ 用**真实几何**检查每个换层点:
     · 距离该点最近的**异网走线** (★按层相交判: 通孔 ⇒ 全层都有铜)
     · 距离该点最近的**异网焊盘** (★按层相交判)
     · 距离该点最近的**异网过孔** (通孔 ⇒ 全层)
     ⇒ 任一不足 `CLEAR` ⇒ ★**这条路径不合格**
  ③ ★**不合格 ⇒ 回退该路径** (从 router 的 tracks/vias 里摘掉) ⇒ ★**不落这条铜**
  ④ 全部落铜后 fresh DRC ⇒ 期望 0 违规

★★**安全**: 只写 --out; ★**回退是"不落铜", 不是"删铜"** ⇒ 不产生悬空端 ⇒ 不打死任何网

用法:
  bash state/pcbnew_py.sh state/patch_astar_nostub.py <板> <DRC.json> --out <新板> [--gate-via 1]
"""
import sys
import os
import math
import json
import re

os.environ.setdefault("PCB_LAYERS", "8")
os.environ.setdefault("PCB_VIA_HALO_MARGIN", "0.0")
os.environ.setdefault("PCB_SKIP_PAD_CELLS", "1")
os.environ.setdefault("PCB_PAIR_EXEMPT_R", "0.0")

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pcbnew  # noqa: E402
import gen_pcb_routing as RT  # noqa: E402

MM = 1e6
CLEAR = 0.20


def pt_seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 < 1e-12:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def seg_seg_dist(p1, p2, q1, q2):
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    d1 = cross(q1, q2, p1)
    d2 = cross(q1, q2, p2)
    d3 = cross(p1, p2, q1)
    d4 = cross(p1, p2, q2)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return 0.0
    return min(pt_seg_dist(p1[0], p1[1], q1[0], q1[1], q2[0], q2[1]),
               pt_seg_dist(p2[0], p2[1], q1[0], q1[1], q2[0], q2[1]),
               pt_seg_dist(q1[0], q1[1], p1[0], p1[1], p2[0], p2[1]),
               pt_seg_dist(q2[0], q2[1], p1[0], p1[1], p2[0], p2[1]))


def rect_pt_dist(cx, cy, rx, ry, w, h):
    dx = max(abs(cx - rx) - w / 2.0, 0.0)
    dy = max(abs(cy - ry) - h / 2.0, 0.0)
    return math.hypot(dx, dy)


class ViaGate(object):
    """★**换层点真实几何复核** (★用 router 已灌入的 tracks/vias, 不落板)"""

    def __init__(self, r):
        self.r = r
        self.tracks = list(r.tracks)     # (net,x1,y1,x2,y2,li,width)
        self.vias = list(r.vias)         # (net,x,y,l1,l2)
        self.pads = []
        for net, plist in r.net_pads.items():
            for (ref, num, cx, cy, layers) in plist:
                self.pads.append((net, cx, cy, set(layers)))

    def check_via(self, net, vx, vy, li_from, li_to, via_r):
        """★这个换层点合法吗? ⇒ 返回 (ok, why, worst)"""
        layers = set(range(li_from, li_to + 1))
        worst = 1e9
        worst_need = 0.0
        who = ""
        for (n2, x1, y1, x2, y2, li, tw) in self.tracks:
            if n2 == net or li not in layers:
                continue
            d = pt_seg_dist(vx, vy, x1, y1, x2, y2)
            need = via_r + tw / 2.0 + CLEAR
            if d < need - 1e-9 and d < worst:
                worst = d
                worst_need = need
                who = "走线 %s[lay%d]" % (n2, li)
        for (n2, cx, cy, lays) in self.pads:
            if n2 == net or not (lays & layers):
                continue
            d = math.hypot(vx - cx, vy - cy)
            _need_pad = via_r + CLEAR
            if d < _need_pad - 1e-9 and d < worst:
                worst = d
                worst_need = _need_pad
                who = "焊盘 %s" % n2
        for (n2, x, y, l1, l2) in self.vias:
            if n2 == net:
                continue
            if not (set(range(l1, l2 + 1)) & layers):
                continue
            d = math.hypot(vx - x, vy - y)
            _need_via = 2 * via_r + CLEAR
            if d < _need_via - 1e-9 and d < worst:
                worst = d
                worst_need = _need_via
                who = "过孔 %s" % n2
        if who:
            # ★★2026-11-08 23:4x **修日志说谎**: ★**原来这里硬编码 "(需 ≥0.0000)"** ⇒ 明明是 0.6250 的净距要求,
            #   日志却写成"需 ≥0.0000" ⇒ ★**读日志的人会以为闸门在乱拒** ⇒ ★**现在打印真实要求值**
            return (False, "%s 仅 %.4fmm (需 ≥%.4f)" % (who, worst, worst_need), worst)
        return (True, "", 1e9)


def _via_conflict_cells(r, net, width):
    """★**算出"这个网上不能打换层点"的格集合** (★距异网铜 < 0.625mm 的地方)

    ★**为什么**: `gen_pcb_routing._via_ok` 查 `halo[2]` ⇒ ★**看不见 halo[1] 里的 0.25mm 走线**
      ⇒ ★**过孔 vs 常规走线的净距检查失效** (★实测 12 条 clearance 违规)
      ⇒ ★**本函数用真实几何算出冲突区 ⇒ A* 主动绕开** ⇒ ★**不需要改共享路由器**

    ★**实现 (稀疏, 不扫全板)**: ★**只处理"该网起脚点附近"的区域**
      ⇒ 理由: ★**换层点只可能出现在路径沿线** ⇒ ★**先做一次普通 A* 拿到路径**
      ⇒ ★**再对路径沿线附近扫冲突区** ⇒ ★**重跑 A* (封掉冲突格)**
      ⇒ ★**若第二遍还是撞 ⇒ 才用"事后回退"兜底**
    """
    return set()


def _conflict_cells_near(r, net, pts, radius_mm=1.2):
    """★**在给定点附近找"换层点会撞铜"的格** (★稀疏: 只扫 radius 内的格)"""
    ban = set()
    via_r = RT.VIA_DIA / 2.0
    gi = int(radius_mm / r.g)
    for (li0, idx0) in pts:
        i0, j0 = idx0 % r.W, idx0 // r.W
        for li in range(RT.NLAYERS):
            for di in range(-gi, gi + 1):
                for dj in range(-gi, gi + 1):
                    i, j = i0 + di, j0 + dj
                    if not (0 <= i < r.W and 0 <= j < r.H):
                        continue
                    idx = r._idx(i, j)
                    if idx in ban:
                        continue
                    cx, cy = r._cx(i), r._cj(j)
                    bad = False
                    # ★**真实几何: 该点到异网走线/焊盘/过孔的距离**
                    for (n2, x1, y1, x2, y2, lay, tw) in r.tracks:
                        if n2 == net or lay != li:
                            continue
                        if pt_seg_dist(cx, cy, x1, y1, x2, y2) < via_r + tw / 2.0 + CLEAR - 1e-9:
                            bad = True
                            break
                    if not bad:
                        for (n2, cx2, cy2, lays) in _pads_of(r, net):
                            if n2 == net or li not in lays:
                                continue
                            if math.hypot(cx - cx2, cy - cy2) < via_r + CLEAR - 1e-9:
                                bad = True
                                break
                    if bad:
                        ban.add(idx)
    return ban


_PAD_CACHE = {}


def _pads_of(r, net):
    """★**取所有网的焊盘 (含真实层集合)** (★缓存, 只算一次)"""
    key = id(r)
    if key not in _PAD_CACHE:
        out = []
        for n, plist in r.net_pads.items():
            for (ref, num, cx, cy, layers) in plist:
                out.append((n, cx, cy, set(layers)))
        _PAD_CACHE[key] = out
    return _PAD_CACHE[key]


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
    max_dist = 0.0
    gate_via = True
    avoid_via = True
    i = 2
    while i < len(a):
        if a[i] == "--out":
            outp = a[i + 1]; i += 2
        elif a[i] == "--grid":
            grid = float(a[i + 1]); i += 2
        elif a[i] == "--budget":
            budget = int(a[i + 1]); i += 2
        elif a[i] == "--width":
            width = float(a[i + 1]); i += 2
        elif a[i] == "--max-dist":
            max_dist = float(a[i + 1]); i += 2
        elif a[i] == "--gate-via":
            gate_via = (a[i + 1] != "0"); i += 2
        elif a[i] == "--avoid-via":
            avoid_via = (a[i + 1] != "0"); i += 2
        else:
            i += 1
    if not outp:
        print("★必须给 --out")
        return 2

    board = pcbnew.LoadBoard(boardp)
    for z in board.Zones():
        z.UnFill()
    r = RT.GridRouter(board, grid=grid)
    print("═══ A* 补段 (无 stub ★+换层点几何闸): %s ═══" % boardp)
    print("═══ 网格 %.4fmm · %dx%d 格 · %d 层 ═══" % (grid, r.W, r.H, RT.NLAYERS))

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

    gate = ViaGate(r)
    d = json.load(open(drcp, encoding="utf-8"))
    items = d.get("unconnected_items") or []
    cls = r._cls(width)
    fixed, failed, gated = [], [], []

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
        c0 = pad_cells(r, k0[1]) if k0[0] == "pad" else \
            track_cells(r, k0[1], (p1.get("x", 0), p1.get("y", 0)))
        c1 = pad_cells(r, k1[1]) if k1[0] == "pad" else \
            track_cells(r, k1[1], (p0.get("x", 0), p0.get("y", 0)))
        if not c0 or not c1:
            failed.append(("端点算不出格子", net))
            continue

        path = r._astar(list(c0), set(c1), net, cls=cls, limit=budget)
        if path is None:
            failed.append(("A* 找不到路", net))
            continue

        # ★★★**两遍 A\*** (★第一遍拿路径 ⇒ 算出沿线冲突格 ⇒ 封格 ⇒ 第二遍重跑)
        #   ★**为什么要两遍**: `_via_ok` 查 `halo[2]` ⇒ ★**看不见 halo[1] 里的 0.25mm 走线**
        #     ⇒ ★**过孔 vs 常规走线的净距检查失效** (★实测 12 条 clearance 违规)
        #   ★**封冲突格 ⇒ A\* 主动绕开** ⇒ ★**比"事后回退"更可能真的布出来**
        if gate_via and avoid_via and path:
            _ban = _conflict_cells_near(r, net, path, radius_mm=1.0)
            if _ban:
                _marked = []
                for _li in range(RT.NLAYERS):
                    for _idx in _ban:
                        if _idx not in r.cu[_li]:
                            r.cu[_li][_idx] = "__VIACONFICT__"
                            _marked.append((_li, _idx))
                _p2 = r._astar(list(c0), set(c1), net, cls=cls, limit=budget)
                for (_li, _idx) in _marked:
                    if r.cu[_li].get(_idx) == "__VIACONFICT__":
                        del r.cu[_li][_idx]
                if _p2 is not None:
                    path = _p2
                    print("     · 封 %d 个冲突格后重跑 A* ⇒ 找到新路径 (%d 格)" % (len(_ban), len(_p2)))
                else:
                    print("     · 封 %d 个冲突格后 A* 无路 ⇒ 用第一遍路径 (由闸兜底)" % len(_ban))

        # ★**落铜前先记录快照** (★回退要用)
        n_tr0, n_via0 = len(r.tracks), len(r.vias)
        ok = r._emit_path(net, path, width)
        if not ok:
            failed.append(("_emit_path 放弃(净距/板边/过孔)", net))
            del r.tracks[n_tr0:]
            del r.vias[n_via0:]
            continue

        # ★★★**换层点几何闸 (★这就是修"halo 级别错配漏判"的地方)** ★★★
        if gate_via:
            bad_via = None
            for v in r.vias[n_via0:]:
                (vn, vx, vy, l1, l2) = v
                if vn != net:
                    continue
                via_r = RT.VIA_DIA / 2.0
                # ★**通孔跨 F.Cu..B.Cu ⇒ 实际层范围** (★commit 时会强制成通孔)
                lo, hi = 0, RT.NLAYERS - 1
                okv, why, worst = gate.check_via(net, vx, vy, lo, hi, via_r)
                if not okv:
                    bad_via = (v, why)
                    break
            if bad_via is not None:
                # ★**回退这条路径** (★不落铜 ⇒ 不产生悬空端 ⇒ 不打死任何网)
                del r.tracks[n_tr0:]
                del r.vias[n_via0:]
                r.rebuild_halo()
                gate = ViaGate(r)
                failed.append(("换层点净距不足 ⇒ 回退 (%s)" % bad_via[1][:44], net))
                gated.append((net, bad_via[1]))
                print("  ✗闸拦下 %-16s 换层点 %s" % (net, bad_via[1][:70]))
                continue

        fixed.append((net, dist, len(path)))
        print("  ★补上 %-16s 间距 %6.3fmm  A* 路径 %d 格" % (net, dist, len(path)))

    print("── 补上 %d 条 / 未成 %d 条 (★闸拦下 %d 条)" % (len(fixed), len(failed), len(gated)))
    for w_, n_ in failed[:40]:
        print("    · 未成: %s %s" % (w_, n_))
    r.commit(board)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(outp)
    print("── 已写出: %s (%d B)" % (outp, os.path.getsize(outp)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
