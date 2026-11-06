#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rip_guard.py -- ★★★**"拆挡路铜"前的承重检查 (2026-11-06 05:5x)**

★★★**为什么必须有这个守卫 (实测事故链)**:
  ① 成品板补丁路线要"拆掉挡路的铜, 再补那一段"
  ② ★**但被拆的铜可能正是别的网的"承重分支"** ⇒ 补段一成功, 那个网就碎了
  ③ 实测: `_reroute2` 把 `RESET_N` 从"1 个孤岛"拆成 **5 个孤岛** (0→5 项),
     差分腿 `USB_D_N_SRC` 也被拖下水 (0→1) ⇒ **总 unc 57→67, 零个网变好**
  ④ ⇒ ★**"补好 1 条 + 拆碎 1 条"总 unc 持平 ⇒ 计数类判据查不出来**
  ⑤ ⇒ ★**所以拆之前必须问一句: 这截铜, 拆了它所属的网会不会散架?**

★★**本脚本做的事 (只读, 不改板)**:
  · 把某个网的铜 (焊盘 + 走线 + 过孔) 建成连通图 (并查集)
  · 算"孤岛数" = 含焊盘的连通分量数
  · ★**对比"拆掉这组铜前/后"的孤岛数** ⇒ 拆后变多 ⇒ ★**这截铜是承重的 ⇒ 不许拆**

★★**用法 (CLI, 给工具作者做预检)**:
  bash state/pcbnew_py.sh state/rip_guard.py <板> --net <网名> [--remove x1,y1,x2,y2 ...]
  ⇒ 打印: 拆前孤岛数 / 拆后孤岛数 / 判定 (承重 ⇒ BLOCK)
  ⇒ 不给 --remove 时只报该网当前的孤岛构成 (诊断用)

★★**导入用 (工具里直接调)**:
  from rip_guard import island_report, is_load_bearing
  ok = is_load_bearing(board, net, [(x1,y1,x2,y2), ...])

★★★**★已知局限 (必须知道, 否则会误判)**: ★**本图不把铜皮填充算进去**
  ⇒ ★**靠铜皮连通的网 (典型: GND) ⇒ 孤岛数会被高估** (实测官方板 GND = 85 个孤岛,
    而实际铜皮把它们连成一片) ⇒ ★**对这类网, "承重" 判定会偏保守 (宁可拦着)**
  ⇒ ★**只加铜的走线/过孔都算在内 ⇒ 对信号网是准的**
  ★**实测校验 (与 KiCad DRC 独立吻合)**: 官方板 `RAIL_DEMO_5V` 孤岛数 = **2**
    (★KiCad DRC 报的那一条 "RAIL_DEMO_5V 未连接" 正是这 2 个孤岛之间)
    · `RESET_N` = 1 (通的) · `USB_D_N_SRC` = 1 (通的)
  ★**实测校验 (守卫本身)**: 拆掉 `RESET_N` 任意一条走线 ⇒ 孤岛 1→2 ⇒ ★**判"承重 ⇒ BLOCK"**
    (★这正是 `_reroute2` 把 RESET_N 拆成 5 块的那个坑)
"""
import sys
import os
import math

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pcbnew  # noqa: E402

MM = 1e6
EPS = 1e-4          # ★1nm 级的点重合判据 (mm)


class DSU(object):
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def _key(x, y):
    return (round(x, 4), round(y, 4))


def _on_seg(px, py, x1, y1, x2, y2):
    """★点是否落在线段上 (含端点)"""
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return abs(px - x1) < EPS and abs(py - y1) < EPS
    t = ((px - x1) * dx + (py - y1) * dy) / L2
    if t < -1e-6 or t > 1 + 1e-6:
        return False
    qx, qy = x1 + t * dx, y1 + t * dy
    return (qx - px) ** 2 + (qy - py) ** 2 < EPS * EPS


def net_graph(board, net):
    """★建某个网的连通图 ⇒ 返回 (dsu, pad_nodes, track_nodes)"""
    dsu = DSU()
    pads = []
    tracks = []
    vias = []
    for f in board.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() != net:
                continue
            pos = p.GetPosition()
            node = ("pad", p.m_Uuid.AsString() if hasattr(p, "m_Uuid") else id(p))
            dsu.find(node)
            pads.append((node, pos.x / MM, pos.y / MM))
    for t in board.GetTracks():
        if t.GetNetname() != net:
            continue
        s, e = t.GetStart(), t.GetEnd()
        a = _key(s.x / MM, s.y / MM)
        b = _key(e.x / MM, e.y / MM)
        if t.Type() == pcbnew.PCB_VIA_T:
            node = ("via", _key(s.x / MM, s.y / MM))
            dsu.find(node)
            vias.append((node, s.x / MM, s.y / MM))
        else:
            node = ("seg", a, b)
            dsu.find(node)
            tracks.append((node, a[0], a[1], b[0], b[1]))
    # ★**走线之间**: 共享端点 ⇒ 同一岛
    by_pt = {}
    for (node, x1, y1, x2, y2) in tracks:
        by_pt.setdefault((x1, y1), []).append(node)
        by_pt.setdefault((x2, y2), []).append(node)
    for pt, lst in by_pt.items():
        for n in lst[1:]:
            dsu.union(lst[0], n)
    # ★**焊盘/过孔落在走线上** ⇒ 同一岛
    for (node, px, py) in pads + vias:
        for (tn, x1, y1, x2, y2) in tracks:
            if _on_seg(px, py, x1, y1, x2, y2):
                dsu.union(node, tn)
        for (vn, vx, vy) in vias:
            if abs(vx - px) < EPS and abs(vy - py) < EPS:
                dsu.union(node, vn)
    # ★**焊盘互相重叠/同点** ⇒ 同一岛 (比如双排同位置的并联焊盘)
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            if abs(pads[i][1] - pads[j][1]) < EPS and abs(pads[i][2] - pads[j][2]) < EPS:
                dsu.union(pads[i][0], pads[j][0])
    return dsu, pads, tracks, vias


def island_count(board, net, remove=()):
    """★算某个网的孤岛数 (含焊盘的连通分量数) —— remove = 要拆掉的走线坐标列表"""
    dsu, pads, tracks, vias = net_graph(board, net)
    rm = []
    for r in remove:
        if len(r) >= 4:
            rm.append((round(r[0], 4), round(r[1], 4), round(r[2], 4), round(r[3], 4)))
    alive = []
    for (node, x1, y1, x2, y2) in tracks:
        if any(abs(x1 - a) < 1e-3 and abs(y1 - b) < 1e-3 and
               abs(x2 - c) < 1e-3 and abs(y2 - d) < 1e-3 for (a, b, c, d) in rm):
            continue
        alive.append((node, x1, y1, x2, y2))
    # ★重算: 共享端点 + 焊盘/过孔落在活着的走线上
    d2 = DSU()
    by_pt = {}
    for (node, x1, y1, x2, y2) in alive:
        d2.find(node)
        by_pt.setdefault((x1, y1), []).append(node)
        by_pt.setdefault((x2, y2), []).append(node)
    for pt, lst in by_pt.items():
        for n in lst[1:]:
            d2.union(lst[0], n)
    pad_nodes = []
    for (node, px, py) in pads:
        d2.find(node)
        pad_nodes.append((node, px, py))
    for (node, px, py) in vias:
        d2.find(node)
    for (node, px, py) in pad_nodes + vias:
        for (tn, x1, y1, x2, y2) in alive:
            if _on_seg(px, py, x1, y1, x2, y2):
                d2.union(node, tn)
    for i in range(len(pad_nodes)):
        for j in range(i + 1, len(pad_nodes)):
            if abs(pad_nodes[i][1] - pad_nodes[j][1]) < EPS and \
               abs(pad_nodes[i][2] - pad_nodes[j][2]) < EPS:
                d2.union(pad_nodes[i][0], pad_nodes[j][0])
    roots = set()
    for (node, px, py) in pad_nodes:
        roots.add(d2.find(node))
    return len(roots)


def island_count_model(net, tracks, vias, pads):
    """★**路由器模型版**孤岛数 (★给"保分支 rip-and-replace"用)
       ★**tracks/vias 用的是路由器内存里的记录格式**:
         tracks = (net, x1, y1, x2, y2, layer, width)
         vias   = (net, x, y, l1, l2)
         pads   = [(node_id, x, y)]
       ⇒ ★**只统计该网的铜** ⇒ 返回"含焊盘的连通分量数" (★孤岛数)"""
    d2 = DSU()
    by_pt = {}
    alive = []
    for rec in tracks:
        if rec[0] != net:
            continue
        node = ("t", id(rec))
        x1, y1, x2, y2 = rec[1], rec[2], rec[3], rec[4]
        alive.append((node, x1, y1, x2, y2))
        d2.find(node)
        by_pt.setdefault((round(x1, 4), round(y1, 4)), []).append(node)
        by_pt.setdefault((round(x2, 4), round(y2, 4)), []).append(node)
    for pt, lst in by_pt.items():
        for n in lst[1:]:
            d2.union(lst[0], n)
    pad_nodes = []
    for (nid, px, py) in pads:
        d2.find(nid)
        pad_nodes.append((nid, px, py))
    via_nodes = []
    for rec in vias:
        if rec[0] != net:
            continue
        node = ("v", id(rec))
        d2.find(node)
        via_nodes.append((node, rec[1], rec[2]))
    for (node, px, py) in pad_nodes + via_nodes:
        for (tn, x1, y1, x2, y2) in alive:
            if _on_seg(px, py, x1, y1, x2, y2):
                d2.union(node, tn)
    for (vn, vx, vy) in via_nodes:
        for (pn, px, py) in pad_nodes:
            if abs(vx - px) < EPS and abs(vy - py) < EPS:
                d2.union(vn, pn)
    for i in range(len(pad_nodes)):
        for j in range(i + 1, len(pad_nodes)):
            if abs(pad_nodes[i][1] - pad_nodes[j][1]) < EPS and \
               abs(pad_nodes[i][2] - pad_nodes[j][2]) < EPS:
                d2.union(pad_nodes[i][0], pad_nodes[j][0])
    roots = set()
    for (node, px, py) in pad_nodes:
        roots.add(d2.find(node))
    return len(roots)


def is_load_bearing(board, net, remove):
    """★拆掉 remove 这组走线后, net 的孤岛数会不会变多 ⇒ 变多 = 承重 = 不许拆"""
    before = island_count(board, net)
    after = island_count(board, net, remove)
    return after > before, before, after


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 2
    boardp = a[0]
    net = None
    remove = []
    i = 1
    while i < len(a):
        if a[i] == "--net":
            net = a[i + 1]
            i += 2
        elif a[i] == "--remove":
            for tok in a[i + 1].split(";"):
                if not tok.strip():
                    continue
                xy = [float(x) for x in tok.split(",")]
                remove.append(xy)
            i += 2
        else:
            i += 1
    board = pcbnew.LoadBoard(boardp)
    if not net:
        print(__doc__)
        return 2
    before = island_count(board, net)
    print("═══ 网 %s: 当前孤岛数(含焊盘的连通分量) = %d" % (net, before))
    if remove:
        load, b, af = is_load_bearing(board, net, remove)
        print("═══ 拆 %d 条铜后: 孤岛数 %d ⇒ %d ⇒ %s"
              % (len(remove), b, af,
                 "★★承重 (拆了就散架) ⇒ BLOCK" if load else "不承重 ⇒ 可以拆"))
        return 1 if load else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
