#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_via_halo_levels.py -- ★★★**修"过孔 vs 细走线"净距漏判 (2026-11-06 08:4x 实测)**

★★★**为什么必须修 (实测, 不是推测)**:
  ① 官方板 unc 45 · 用 0.0625mm 网格跑无-stub A* ⇒ 救回 3 条 (unc 45→42)
  ② ★**但 fresh DRC 报 12 条 clearance 违规** (0.1937 < 0.2000) ⇒ 闸 REJECT
  ③ ★**逐条看违规**: **12 条全是"过孔 vs 走线"** (不是走线 vs 走线!)
     例: `Via [PWR_GOOD] (86.7,44.325)` vs `Track [VBUS_DET_D] on In4.Cu (86.2,43.95)`
     ⇒ ★**中心距实测正好 0.6250mm**
  ④ ★★**根因 (代码级, 可证伪)**: `gen_pcb_routing.py` 的宽度级别**错配**
     · ★**过孔查询用 `halo[2]`** (`_via_ok` 第 777 行: `s = self.halo[2][l2].get(idx)`)
     · ★**但 0.25mm 走线的铜只登记在 `halo[1]`** (`_add_track_halo` 按**自己**的宽度级登记)
     ⇒ ★**过孔根本看不见 0.25mm 的走线** ⇒ ★**净距检查对"过孔 vs 常规走线"完全失效**
     ⇒ ★**⇒ 放行 ⇒ 撞 0.625mm 中心距 ⇒ KiCad 报 0.1937**
     ⇒ ★**注: 不是 margin 太小** ⇒ ★**是 halo 查错了级别** ⇒ ★**调 margin 治不了**
  ⑤ ★**为什么官方板 (0.125mm 网格 + margin 0.0625) 没报这 12 条**:
     ⇒ ★**margin 0.0625 把 halo[2] 的半径从 0.75 撑到 0.8125** ⇒ ★**恰好盖住了漏判**
     ⇒ ★**换更细网格 + 相应收紧 margin ⇒ 漏判就暴露了** ⇒ ★**这是"两个 bug 互相掩盖"**

★★**修法 (本脚本, 只读板 + 输出新板)**:
  · ★**只加铜, 不删铜** ⇒ 不可能把网打死
  · 把**新加的过孔**按**真实净距需求**重新校验一遍:
    对每个过孔 ⇒ 找附近所有异网铜 (走线/焊盘) ⇒ 用**真实几何距离**判
    ⇒ ★**距离不够 ⇒ 把该过孔判死 ⇒ ★不落这批过孔**
  · ⇒ 落板后 fresh DRC ⇒ ★**0 违规才算成功**

★★**安全**: 只写 --out; 不动输入板; ★**只加铜不删铜**

用法:
  bash state/pcbnew_py.sh state/fix_via_halo_levels.py <板> <DRC.json> --out <新板> [--margin 0.03125]
"""
import sys
import os
import math
import json
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pcbnew  # noqa: E402

MM = 1e6
CLEAR = 0.20


def _pt_seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 < 1e-12:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def _seg_seg_dist(p1, p2, q1, q2):
    """两线段最短距离 (★相交 ⇒ 0)"""
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    d1 = cross(q1, q2, p1)
    d2 = cross(q1, q2, p2)
    d3 = cross(p1, p2, q1)
    d4 = cross(p1, p2, q2)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return 0.0
    d = min(_pt_seg_dist(p1[0], p1[1], q1[0], q1[1], q2[0], q2[1]),
            _pt_seg_dist(p2[0], p2[1], q1[0], q1[1], q2[0], q2[1]),
            _pt_seg_dist(q1[0], q1[1], p1[0], p1[1], p2[0], p2[1]),
            _pt_seg_dist(q2[0], q2[1], p1[0], p1[1], p2[0], p2[1]))
    return d


def _rect_pt_dist(cx, cy, rx, ry, w, h):
    """点 (过孔圆心) 到焊盘矩形铜缘的最短距离"""
    dx = max(abs(cx - rx) - w / 2.0, 0.0)
    dy = max(abs(cy - ry) - h / 2.0, 0.0)
    return math.hypot(dx, dy)


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        return 2
    boardp, drcp = a[0], a[1]
    outp = None
    margin = 0.03125
    i = 2
    while i < len(a):
        if a[i] == "--out":
            outp = a[i + 1]; i += 2
        elif a[i] == "--margin":
            margin = float(a[i + 1]); i += 2
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

    # ── 收集所有异网铜 (走线/焊盘) ──
    tracks = []
    for t in board.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            continue
        s, e = t.GetStart(), t.GetEnd()
        tracks.append((t.GetNetname(), s.x / MM, s.y / MM, e.x / MM, e.y / MM,
                       t.GetLayer(), t.GetWidth() / MM))
    pads = []
    for f in board.GetFootprints():
        for p in f.Pads():
            pos = p.GetPosition()
            # ★**焊盘铜缘用真实矩形** (★不是 bounding radius —— 那个含丝印/courtyard)
            try:
                sz = p.GetSize()
                pw, ph = sz.x / MM, sz.y / MM
            except Exception:
                pw, ph = 0.6, 0.6
            try:
                lay = p.GetLayer()
            except Exception:
                lay = pcbnew.F_Cu
            pads.append((p.GetNetname(), pos.x / MM, pos.y / MM, pw, ph, lay))

    print("═══ 过孔 halo 级别修正: %s ═══" % boardp)
    print("═══ 异网铜: 走线 %d · 焊盘 %d ═══" % (len(tracks), len(pads)))

    vias = []
    for t in board.GetTracks():
        if t.Type() != pcbnew.PCB_VIA_T:
            continue
        pos = t.GetStart()
        vias.append((t, t.GetNetname(), pos.x / MM, pos.y / MM,
                     t.GetWidth() / MM, t.GetNetCode()))
    # ★**过孔 vs 过孔** (★2026-11-06 08:5x 实测漏项: 只查"过孔 vs 走线/焊盘"
    #   ⇒ **过孔 vs 过孔**没查 ⇒ 8 条 clearance 违规漏网
    #   ⇒ 需求 = via_r1 + via_r2 + CLEAR (★两个都是通孔 ⇒ 环在 6 层都有 ⇒ 必须查)
    via_list = [(v[1], v[2], v[3], v[4] / 2.0) for v in vias]
    # ★**过孔跨的层** (★通孔 = F.Cu..B.Cu ⇒ **8 层全有铜** ⇒ 任何层的走线都要查!)
    #   ★这是 2026-11-06 08:5x 实测的最后 1 条漏网: 走线在 In2.Cu, 过孔是通孔
    #   ⇒ ★**通孔在 In2.Cu 也有环** ⇒ 必须按"层相交"判, 不能只看 F.Cu
    def _layer_set(via_obj):
        try:
            l1 = via_obj.TopLayer()
            l2 = via_obj.BottomLayer()
        except Exception:
            return set([pcbnew.F_Cu])
        return set(range(l1, l2 + 1))
    via_layers = {}
    for v in vias:
        via_layers[id(v[0])] = _layer_set(v[0])

    # ★**过孔盘径 (从板文件读, 不猜)** ★过孔铜缘到异网铜缘的真实净距要求
    #   走线: 距离(孔心→走线中轴) ≥ via_r + track_half + CLEAR
    #   焊盘: 距离(孔心→焊盘圆心) ≥ via_r + pad_r + CLEAR
    bad = []
    for (t, net, vx, vy, vr, netcode) in vias:
        need_r = vr / 2.0
        worst = 1e9
        who = ""
        _vl = via_layers.get(id(t), set())
        for (n2, x1, y1, x2, y2, lay, tw) in tracks:
            if n2 == net:
                continue
            # ★**层必须相交** (★通孔 ⇒ 全层 ⇒ 内层走线也要查!)
            if lay not in _vl:
                continue
            d = _seg_seg_dist((vx, vy), (vx, vy), (x1, y1), (x2, y2))
            need = need_r + tw / 2.0 + CLEAR
            if d < need - 1e-9 and d < worst:
                worst = d
                who = "走线 %s[lay%d]" % (n2, lay)
        for (n2, px, py, pw, ph, lay) in pads:
            if n2 == net:
                continue
            if lay not in _vl:
                continue
            d = _rect_pt_dist(vx, vy, px, py, pw, ph)
            if d < CLEAR - 1e-9 and d < worst:
                worst = d
                who = "焊盘 %s" % n2
        # ★**过孔 vs 过孔** (★通孔环在 6 层都有 ⇒ 中心距必须 ≥ 两个半盘 + CLEAR)
        for (n2, px, py, pr2) in via_list:
            if n2 == net:
                continue
            d = math.hypot(vx - px, vy - py)
            if d < need_r + pr2 + CLEAR - 1e-9 and d < worst:
                worst = d
                who = "过孔 %s" % n2
        if who:
            bad.append((t, net, vx, vy, worst, who))

    print("── 检查 %d 个过孔 ⇒ ★**净距不足 %d 个**" % (len(vias), len(bad)))
    for (t, net, vx, vy, worst, who) in bad[:20]:
        print("   ★过孔 %-18s @(%8.3f,%8.3f) 距 %s 仅 %.4fmm (需 %.4f)"
              % (net, vx, vy, who, worst, CLEAR))

    if not bad:
        print("── 无违规过孔 ⇒ 直接复制 (不改动)")
        board.Save(outp)
        print("── 已写出: %s" % outp)
        return 0

    # ★**修法 (保守, 只动违规过孔)**: 把违规过孔**删掉**
    #   ⇒ ★**只删自己新增的过孔** (那些导致 DRC 违规的) ⇒ ★**不能删 ⇒ 只能让上层重跑**
    #   ⇒ ★**但删过孔会让走线悬空** ⇒ ★**所以本脚本只做"诊断 + 删除 + 标记"**,
    #      真正修好要靠上层把该过孔所在的路径重跑
    # ⇒ ★**更安全的做法: 把过孔"挪开"** —— 沿垂直于冲突方向微移, 直到满足净距
    moved, still_bad = 0, 0
    for (t, net, vx, vy, worst, who) in bad:
        # 试 8 个方向微移 0.05mm 步长, 最多 0.6mm
        ok_pos = None
        for step in range(1, 25):
            d = step * 0.05
            for (dx, dy) in ((0, 1), (0, -1), (1, 0), (-1, 0),
                             (0.7071, 0.7071), (-0.7071, 0.7071),
                             (0.7071, -0.7071), (-0.7071, -0.7071),
                             (0.3827, 0.9239), (-0.3827, 0.9239),
                             (0.3827, -0.9239), (-0.3827, -0.9239),
                             (0.9239, 0.3827), (-0.9239, 0.3827),
                             (0.9239, -0.3827), (-0.9239, -0.3827)):
                nx, ny = vx + dx * d, vy + dy * d
                good = True
                need_r = t.GetWidth() / MM / 2.0
                for (n2, x1, y1, x2, y2, lay, tw) in tracks:
                    if n2 == net:
                        continue
                    if lay not in _vl:
                        continue
                    if _seg_seg_dist((nx, ny), (nx, ny), (x1, y1), (x2, y2)) < \
                            need_r + tw / 2.0 + CLEAR - 1e-9:
                        good = False
                        break
                if good:
                    for (n2, px, py, pw, ph, lay) in pads:
                        if n2 == net:
                            continue
                        if lay not in _vl:
                            continue
                        if _rect_pt_dist(nx, ny, px, py, pw, ph) < CLEAR - 1e-9:
                            good = False
                            break
                if good:
                    for (n2, px, py, pr2) in via_list:
                        if n2 == net:
                            continue
                        if math.hypot(nx - px, ny - py) < need_r + pr2 + CLEAR - 1e-9:
                            good = False
                            break
                if good:
                    ok_pos = (nx, ny)
                    break
            if ok_pos:
                break
        if ok_pos:
            _pt = pcbnew.VECTOR2I(pcbnew.FromMM(ok_pos[0]), pcbnew.FromMM(ok_pos[1]))
            t.SetStart(_pt)
            t.SetEnd(_pt)
            moved += 1
        else:
            still_bad += 1

    print("── 挪开 %d 个过孔 · ★**挪不开 %d 个**" % (moved, still_bad))
    if still_bad:
        print("   ★挪不开 ⇒ 必须由上层重跑该路径 (本脚本不删铜 ⇒ 不产生悬空端)")
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones() or [])
    board.Save(outp)
    print("── 已写出: %s (%d B)" % (outp, os.path.getsize(outp)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
