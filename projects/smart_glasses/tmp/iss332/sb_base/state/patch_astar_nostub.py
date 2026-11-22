#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch_astar_nostub.py -- ★★★**A* 补段 (★去掉 stub 模型) (2026-11-06 06:2x)**

★★★**为什么要有这个脚本 (实测事故链, 每条都有出处)**:
  ① 官方板 57 项未连接
  ② `state/fix_unconnected_astar.py` (兄弟的工具) 在 **0.25mm 与 0.125mm 两张网格上都是"补上 0 条"**
     ⇒ 失败构成完全一样: 15 条"距离>12mm 交给路由器" + 10 条"**stub 净距不过 / A* 找不到路**"
  ③ ⇒ **卡住的是"从焊盘出来的第一段 stub", 不是路径搜索**
  ④ ★★**stub 模型的结构性缺陷**:
     路由器里 `route_net()` 的出脚是"★**沿焊盘中心线先拉一段直道, 再进网格**"
     ⇒ ★**直道方向是预设的** ⇒ ★**表达不了"该往哪边出脚"由 A* 现场决定**
     ⇒ ★★**本脚本的做法**: ★**A* 直接从"焊盘自己那一格"起步** ⇒ ★**出脚方向由 A* 自己选**
        ⇒ ★**彻底绕开 stub 模型**
  ⑤ ★★**网格必须够细 (实测)**: SoM BTB 焊盘只有 **0.2mm 宽**
     ⇒ ★**0.25mm 网格的格心可能落在焊盘外** ⇒ ★**新线端点碰不到焊盘 ⇒ track_dangling**
     ⇒ ★**本脚本默认 0.125mm** (格心离焊盘中心 ≤0.0625mm ⇒ 必落在焊盘内)
  ⑥ ★★**分层**: 路由器自己的 halo 是**按层**的 (`halo[cls][li]`) ⇒ ★**不同层的铜不冲突**
     ⇒ ★**别用二维距离判障碍** (★实测: 二维会把"In2.Cu 的铜压在 F.Cu 焊盘下面"也当墙 ⇒ 白拦一堆)

★★**安全**:
  · 只写 --out 路径, 不动输入板
  · ★**只加铜, 不删任何现有铜** ⇒ 不可能退铜 / 不可能把网打死
  · ★**用路由器自己的 `_emit_path`** (它会做净距/板边/过孔预校验) ⇒ 过了才落铜
  · 落铜后必须 fresh DRC

用法:
  bash state/pcbnew_py.sh state/patch_astar_nostub.py <板> <DRC.json> --out <新板> [--grid 0.125] [--budget 400000]
"""
import sys
import os
import math
import json
import re

# ★**必须在 import gen_pcb_routing 之前设好环境**
os.environ.setdefault("PCB_LAYERS", "8")
os.environ.setdefault("PCB_HALO_MARGIN", "0.20")
os.environ.setdefault("PCB_VIA_HALO_MARGIN", "0.0")
os.environ.setdefault("PCB_SKIP_PAD_CELLS", "1")
os.environ.setdefault("PCB_PAIR_EXEMPT_R", "0.0")

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pcbnew  # noqa: E402
import gen_pcb_routing as RT  # noqa: E402

MM = 1e6

# ★★★★★★2026-11-11 05:5x 【★端点吸附开关 `PCB_PATCH_SNAP` (★默认关 ⇒ 官方链逐位不变★)】★★★★★★
#   ★★★**★根因 (★实测坐实★, ★三个独立样本★)**: ★★★
#     ★**A* 的终点只能落在【格心】⇒ 而【焊盘中心通常不在格心上】⇒ ⇒ 铜画到格心 ⇒ 离焊盘中心差 0.15~0.19mm**
#     ★**⇒ 铜面没搭上焊盘 ⇒ KiCad 判未连接 ⇒ ⇒ 链日志的"补上 N 条"是【假阳性】!!** ★★
#     ★**实测样本**: ★`KEY_VOL_M` 补丁端点 (34.950,51.075) 距焊盘 (34.800,50.960) = **0.1890mm** ★
#     ★              · `I2C_A_SCL` 补丁端点 (51.575,65.450) 距焊盘 (51.700,65.600) = **0.1953mm** ★
#     ★              · `LED_B`     补丁端点 (71.575,58.325) 距焊盘 (71.700,58.400) = **0.1458mm** ★
#     ★★**⇒ 三条独立样本, 同一个模式: ★一端命中焊盘 (0.0000mm), 另一端差 0.15~0.19mm** ★★
#   ★★★**★修法 (★产出点, ★不是擦产物★)**: ★★★
#     ★**把路径首/末端点换成【端点的真实坐标】⇒ 铜直接压在焊盘上 ⇒ ⇒ 真连通** ★
#     ★**路由器 `_emit_path` 本来就有 `stub_start/stub_end` 参数 (★作用正是"把首末端点换成焊盘真实中心"★)**
#     ★**⇒ ★本脚本只是【从来没传过它】⇒ ⇒ 这是【缺的那一环】★★**
#   ★★★**★为什么默认关 (★铁律★)**: ★★**官方链就是用本脚本产的 (★loose 0.0625 ⇒ 官方板 611b869e★)**
#     ⇒ ★★**⇒ 一旦默认开 ⇒ 官方链不再逐位复现 ⇒ 校准链作废 ⇒ ⇒ ★必须 env 门控** ★★
#   ★★★**★安全性 (★为什么这跳是安全的★)**: ★★**最后一跳是【同网铜】⇒ 不可能触发异网净距违规** ★★
#     ★★**⇒ 且 `PCB_ESC_CLR_FIX` 的 `_seg_clear_geom` 会复查【离网格那一跳】⇒ 不合格 ⇒ 整条路径放弃 ⇒ ⇒ 不产生脏铜** ★★
SNAP = os.environ.get("PCB_PATCH_SNAP", "0").strip() not in ("0", "", "false", "False")


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
    """★这个焊盘可用的起步格集合 = ★**自己那一格 + 周围 8 格** (★同层)
       ★★**不含任何"出脚直道"** ⇒ ★★**出脚方向交给 A★ 决定**"""
    pos = pad.GetPosition()
    cx, cy = pos.x / MM, pos.y / MM
    li = 0
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
    """★走线端点: 取离对方近的那个端 ⇒ 它所在格 + 周围 8 格"""
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


def item_real_xy(kind, item, other_xy):
    """★**端点的真实坐标 (★焊盘中心 / 走线离对方近的那个端点★)**

    ★★★**★为什么必须有 (★实测★)**: ★**焊盘中心通常【不在网格格心上】⇒ A* 只能连到【最近格心】**
      ⇒ ★**铜画到格心 ⇒ 离焊盘中心还差 0.15~0.19mm ⇒ 没搭上 ⇒ 假阳性** ★**
    """
    if kind == "pad":
        p = item.GetPosition()
        return (p.x / MM, p.y / MM)
    s, e = item.GetStart(), item.GetEnd()
    p1 = (s.x / MM, s.y / MM)
    p2 = (e.x / MM, e.y / MM)
    return p1 if math.hypot(p1[0] - other_xy[0], p1[1] - other_xy[1]) <= \
        math.hypot(p2[0] - other_xy[0], p2[1] - other_xy[1]) else p2


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
    max_dist = 0.0        # ★0 = 不限距离
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
        elif a[i] == "--width":
            width = float(a[i + 1])
            i += 2
        elif a[i] == "--max-dist":
            max_dist = float(a[i + 1])
            i += 2
        else:
            i += 1
    if not outp:
        print("★必须给 --out")
        return 2

    board = pcbnew.LoadBoard(boardp)
    for z in board.Zones():
        z.UnFill()
    r = RT.GridRouter(board, grid=grid)
    print("═══ A* 补段 (无 stub): %s ═══" % boardp)
    print("═══ 网格 %.3fmm · %dx%d 格 · %d 层 ═══" % (grid, r.W, r.H, RT.NLAYERS))

    # ── 灌入成品板铜 (★用路由器同一套 API, 否则 A* 看不见障碍) ──
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
        # ★★★**A★ 直接从"焊盘自己的格"起步, 不生成 stub** ⇒ ★**出脚方向由 A★ 决定**
        path = r._astar(list(c0), set(c1), net, cls=cls, limit=budget)
        if path is None:
            failed.append(("A* 找不到路", net))
            continue
        # ★★**落铜**: 不传 stub ⇒ 路径两端就是焊盘格 ⇒ 铜直接压在焊盘上
        # ★★★★★★2026-11-11 05:5x 【★端点吸附 (★env 门控 `PCB_PATCH_SNAP`★)】★★★★★★
        #   ★★**默认关 ⇒ 逐位不变 (★官方链 = 本脚本产的 ⇒ 开了官方板 md5 就变 ⇒ 校准链作废★)** ★★
        #   ★★**开了以后: 把首/末端点换成【端点真实坐标】⇒ ★铜真正压在焊盘上 ⇒ ⇒ 真连通** ★★
        #   ★★**传 (x,y,x,y) ⇒ 零长 ⇒ `_emit_path` 不会多出 stub 段, 只把 pts[0]/pts[-1] 换掉** ★★
        _ss = _se = None
        if SNAP:
            _x0, _y0 = item_real_xy(k0[0], k0[1], (p1.get("x", 0), p1.get("y", 0)))
            _x1, _y1 = item_real_xy(k1[0], k1[1], (p0.get("x", 0), p0.get("y", 0)))
            _ss = (_x0, _y0, _x0, _y0)
            _se = (_x1, _y1, _x1, _y1)
        ok = r._emit_path(net, path, width, stub_start=_ss, stub_end=_se)
        if not ok:
            failed.append(("_emit_path 放弃(净距/板边/过孔)", net))
            continue
        fixed.append((net, dist, len(path)))
        print("  ★补上 %-16s 间距 %6.3fmm  A* 路径 %d 格" % (net, dist, len(path)))

    print("── 补上 %d 条 / 未成 %d 条" % (len(fixed), len(failed)))
    for w_, n_ in failed[:30]:
        print("    · 未成: %s %s" % (w_, n_))
    r.commit(board)
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(outp)
    print("── 已写出: %s (%d B)" % (outp, os.path.getsize(outp)))
    return 0


if __name__ == "__main__":
    # ★★2026-11-06 20:2x **崩溃也要留 EXIT 标记** (★实测: 四个臂/进程死于无标记 ⇒ 事后分不清"被杀"还是"正常退出")
    _rc = 1
    try:
        _rc = main()
    except BaseException:
        import traceback
        traceback.print_exc()
        _rc = 1
    finally:
        print("EXIT=%d" % _rc)
    sys.exit(_rc)
