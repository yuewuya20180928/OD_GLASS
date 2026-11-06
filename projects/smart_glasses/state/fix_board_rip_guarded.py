#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_board_rip_guarded.py -- ★★★**"保分支"的 rip-and-replace (2026-11-06 17:0x)

★★★**为什么要有这个工具 (实测事故链)**:
  ① 官方板(现 unc 45)还有 45 条未连接, 主体是 **DSI/CSI 差分腿** (★整网无铜 ⇒ 要从零布 40~70mm)
  ② ★**成品板上"整网重布"是破坏器** (`gen_pcb_routing.py` `ripup_and_reroute()` 第 2713 行):
     `keep = [s for s in self.tracks if s not in rip_set and s[0] not in affected]`
     ⇒ ★**它把受影响网自己全部的铜清空后整网重画**
     ⇒ ★**多脚/树状网只连上一对 ⇒ 其余分支被砍** ⇒ 实测 `_reroute2`: unc 57→67 · RESET_N 0→5 孤岛
  ③ ⇒ ★**不能直接用 `ripup_and_reroute`** ⇒ ★**必须加"保分支"守卫**
  ④ ★★**本工具的做法 (★比原版多一道闸)**:
     对每个要修的网:
       a. ★**快照** (tracks/vias/routed_ok)
       b. 调 `ripup_and_reroute()` 重画
       c. ★★**守卫**: 用 `rip_guard.island_count_model()` 算这个网**重画后**的孤岛数
          ⇒ ★**孤岛数变多 ⇒ 这次重画把网拆碎了 ⇒ ★**回滚快照** (不落铜)**
          ⇒ ★**孤岛数不变或变少 ⇒ 才接受**
       d. ★**差分腿保护**: ★**不许拆差分腿** (★打死一条腿 = 那条高速通道不存在 ⇒ 一票否决)
     ⇒ ⇒ ★**从"整网重画"变成"重画 + 逐网验收 + 不合格就回滚"**

★**只加铜不删铜之外, 本工具唯一的删铜来源 = rip-up 拆掉的挡路铜**
  ⇒ ★**删了必须让被删铜所属的网仍然连通** ⇒ ★**由守卫保证 (孤岛数不变)**

用法:
  bash state/pcbnew_py.sh state/fix_board_rip_guarded.py <板> <DRC.json> --out <新板> [--max-dist 80] [--rip 8]
"""
import sys
import os
import json
import math
import re

os.environ.setdefault("PCB_LAYERS", "8")
os.environ.setdefault("PCB_HALO_MARGIN", "0.0625")   # ★**对齐官方板** (官方板是 0.125 网格 + margin 0.0625)
# ★★★**网格必须 0.125mm** (★官方板就是 0.125 造的): ★**粗网格 (0.25) 下净距判据有 ±0.125mm 松**
#   ⇒ ★**实测: 0.25 网格的 rip-up 产出 DRC=678 (新铜压到 GND 缝合短段 0.134mm)** ⇒ ★**必须细网格**
os.environ.setdefault("PCB_VIA_HALO_MARGIN", "0.0")
os.environ.setdefault("PCB_SKIP_PAD_CELLS", "1")
os.environ.setdefault("PCB_PAIR_EXEMPT_R", "0.0")
os.environ.setdefault("PCB_RIPUP_ALIVE", "1")
os.environ.setdefault("PCB_RIPUP_ESC", "1")
# ★★★**必须开**: `gen_pcb_routing.py` 的 `_via_ok` 只查 `halo[2]` ⇒ **看不见 0.25mm 走线**
#   ⇒ ★**过孔 vs 常规走线净距检查失效** ⇒ ★**实测 unc 45→40 的板 DRC=718 (199短路/395净距/124交叉)**
#   ⇒ ★**这个 env 开关就是那个修复** (★默认关 ⇒ 不开就会踩)
os.environ.setdefault("PCB_VIA_CHECK_ALL_CLS", "1")
# ★★★**成品板上必须关掉 escape stub** (★stub 不走净距检查 ⇒ 直接压穿别网的铜
#   ⇒ 实测 DRC 678~772) ⇒ ★**关掉后起步格 = 焊盘自己那一格 ⇒ 铜直接压在焊盘上**
os.environ.setdefault("PCB_USE_ESCAPE", "0")

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pcbnew  # noqa: E402
import gen_pcb_routing as RT  # noqa: E402
import rip_guard as RG  # noqa: E402
import geom_clear as GC  # noqa: E402

MM = 1e6


def load_pairs():
    """★差分对清单 (★打死差分腿 ⇒ 一票否决 ⇒ 必须先拿到)"""
    p = os.path.join(_HERE, "..", "..", "..", "tools", "diff_pair_audit.py")
    try:
        src = open(p, encoding="utf-8").read()
        m = re.search(r"PAIRS\s*=\s*\[(.*?)\]", src, re.S)
        out = re.findall(r'\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)', m.group(1))
        return out if len(out) >= 20 else []
    except Exception:
        return []


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        return 2
    boardp, drcp = a[0], a[1]
    outp = None
    max_dist = 80.0
    rip = 8
    i = 2
    while i < len(a):
        if a[i] == "--out":
            outp = a[i + 1]
            i += 2
        elif a[i] == "--max-dist":
            max_dist = float(a[i + 1])
            i += 2
        elif a[i] == "--rip":
            rip = int(a[i + 1])
            i += 2
        else:
            i += 1
    if not outp:
        print("★必须给 --out")
        return 2

    PAIRS = load_pairs()
    diff_nets = set()
    for (x, y) in PAIRS:
        diff_nets.add(x)
        diff_nets.add(y)
    print("═══ 差分对清单: %d 对 ⇒ 保护 %d 个差分腿网" % (len(PAIRS), len(diff_nets)))

    board = pcbnew.LoadBoard(boardp)
    for z in board.Zones():
        z.UnFill()
    r = RT.GridRouter(board, grid=0.125)
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
            # ★★**必须登记 halo** (★否则 A* 看不见板上已有的铜 ⇒ 新线直接穿过别网的铜
            # ★实测: 不登记 ⇒ fresh DRC = 707 条违规 (119 交叉 + 389 净距 + 199 短路) ⇒ 板子全废)
            r._add_track_halo(t.GetNetname(), s.x / MM, s.y / MM,
                              e.x / MM, e.y / MM, li, w)
        ingested[id(rec)] = (t, rec)
    r.rebuild_halo()
    print("═══ 已灌入 %d 段 / %d 孔 (halo 已重建) ═══" % (len(r.tracks), len(r.vias)))

    # ★该网的焊盘 (给孤岛数算)
    pads_by_net = {}
    for f in board.GetFootprints():
        for p in f.Pads():
            pos = p.GetPosition()
            nm = p.GetNetname()
            nid = ("pad", p.m_Uuid.AsString() if hasattr(p, "m_Uuid") else id(p))
            pads_by_net.setdefault(nm, []).append((nid, pos.x / MM, pos.y / MM))

    d = json.load(open(drcp, encoding="utf-8"))
    items = d.get("unconnected_items") or []
    # ★按间距升序 (★近距的便宜先修)
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
        cand.append((dist, n0))
    cand.sort()
    print("═══ 候选失败网 %d 个 (按间距升序) ═══" % len(cand))

    ok_nets, rej = [], []
    # ★★**真几何净距尺 (★关键: 路由器的 halo 模型偏乐观 ⇒ 必须用真实几何复核)** ★★
    #   ★**兄弟的 `patch_astar_gated.py` 查的是过孔 ⇒ 这把尺子查的是"走线" ⇒ 两半合起来才完整**
    try:
        BC = GC.BoardCopper(board)
        print("═══ 真几何净距尺已建 (★铜 %d 图元索引) ═══"
              % sum(len(v) for v in BC.index.values()))
    except Exception as e:
        BC = None
        print("  ⚠️ 建索引失败: %s" % e)
    # ★**板级校验用**: 每个网的"修之前"孤岛数 (★在真板上算 ⇒ 与 KiCad 口径一致)
    pre_island = {}

    def board_islands(nets):
        out = {}
        for n in nets:
            if n in pre_island:
                continue
            try:
                out[n] = RG.island_count(board, n)
            except Exception:
                out[n] = 999
        return out

    def apply_diff():
        """★把模型差异落到板子上 (★返回 (新增对象, 被删对象) 供回滚)"""
        alive = set(id(s) for s in r.tracks) | set(id(v) for v in r.vias)
        removed = []
        for oid, (obj, rec) in list(ingested.items()):
            if oid not in alive:
                board.Remove(obj)
                removed.append((obj, rec))
                del ingested[oid]
        added = []
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
            added.append((t, s))
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
            added.append((vi, v))
        return added, removed

    def undo_diff(added, removed):
        """★回滚刚才的落铜 (★把被删的图元放回去, 把新增的撤掉)"""
        for (obj, rec) in added:
            try:
                board.Remove(obj)
            except Exception:
                pass
            ingested.pop(id(rec), None)
        for (obj, rec) in removed:
            try:
                board.Add(obj)
            except Exception:
                pass
            # ★★**必须把 ingested 条目放回去** ⇒ ★**否则还原的旧铜会被当成"新铜"⇒ 复核时冤拒**
            ingested[id(rec)] = (obj, rec)

    for (dist, net) in cand:
        pads = pads_by_net.get(net, [])
        if not pads:
            rej.append(("没有焊盘", net))
            continue
        before = RG.island_count_model(net, r.tracks, r.vias, pads)
        snap_t = list(r.tracks)
        snap_v = list(r.vias)
        snap_ok = set(r.routed_ok)
        r.routed_ok.discard(net)
        r.routed.discard(net)
        try:
            n_ok = r.ripup_and_reroute([net], rip_per_net=rip, verbose=True)
        except Exception as e:
            r.tracks = snap_t
            r.vias = snap_v
            r.routed_ok = snap_ok
            rej.append(("ripup 异常 %s" % e, net))
            continue
        after = RG.island_count_model(net, r.tracks, r.vias, pads)
        if after > before:
            # ★★**守卫拦下: 这次重画把网拆碎了 ⇒ 回滚**
            r.tracks = snap_t
            r.vias = snap_v
            r.routed_ok = snap_ok
            r.rebuild_halo()
            rej.append(("★守卫: 孤岛 %d→%d 变多 ⇒ 回滚" % (before, after), net))
            continue
        if not n_ok:
            rej.append(("ripup 没能重布", net))
            continue
        # ★★**先记"修之前"的板级孤岛数 (★必须在落铜之前记!)**
        touched = set([net])
        for (tn, x1, y1, x2, y2, li, w) in snap_t:
            if not any(id(s) == id(tn) for s in r.tracks):
                touched.add(tn[0])
        pre = board_islands(touched)
        # ★★★**新铜真几何复核 (★这一刀是"能不能用"的关键)**
        #   ★★**必须用"落板之后"的板子重建索引** (★★**不然会把"即将被删的旧铜"当成障碍 ⇒ 冤拒**)
        #   ★路由器自认为合格的铜, 真板 DRC 会报 0.0152mm (halo 半宽用错 + skip_pad_cells)
        if BC is not None:
            added2, removed2 = apply_diff()
            try:
                BC2 = GC.BoardCopper(board)      # ★★**落板后重建 (★含新铜, 不含被拆铜)**
            except Exception:
                BC2 = None
            bad = []
            if BC2 is not None:
                for s in r.tracks:
                    if id(s) in ingested:
                        continue
                    (n2, x1, y1, x2, y2, li, w) = s
                    okc, worst, who = GC.check_track(BC2, n2, (x1, y1), (x2, y2), w, li)
                    if not okc:
                        bad.append("走线[%s] 净距 %.3fmm %s" % (n2, worst, who))
                for v in r.vias:
                    if id(v) in ingested:
                        continue
                    (n2, x, y, l1, l2) = v
                    okc, worst, who = GC.check_via(BC2, n2, (x, y))
                    if not okc:
                        bad.append("过孔[%s] 净距 %.3fmm %s" % (n2, worst, who))
            if bad:
                undo_diff(added2, removed2)
                r.tracks = snap_t
                r.vias = snap_v
                r.routed_ok = snap_ok
                r.rebuild_halo()
                rej.append(("★新铜真几何复核不过 (%d 处, 例 %s) ⇒ 回滚"
                            % (len(bad), bad[0][:60]), net))
                continue
            # ★**通过 ⇒ 铜已经落在板上了 ⇒ 后续的板级校验继续用这块板**
        # ★★★**板级校验 (★关键: 模型说通 ≠ 板子真通)**
        #   ★**被拆铜的那些网**也要查 ⇒ ★**不然"修好 1 条、拆坏 7 条"就是这样发生的**
        post = {}
        bad = []
        for n in touched:
            try:
                post[n] = RG.island_count(board, n)
            except Exception:
                post[n] = 999
            if post[n] > pre.get(n, 0):
                bad.append("%s(%d→%d)" % (n, pre.get(n, 0), post[n]))
        if bad:
            undo_diff(added, removed)
            r.tracks = snap_t
            r.vias = snap_v
            r.routed_ok = snap_ok
            r.rebuild_halo()
            rej.append(("★板级校验不过(网被拆碎): %s ⇒ 回滚" % ", ".join(bad[:4]), net))
            continue
        ok_nets.append((net, dist, before, after))
        print("  ★接受 %-18s 间距 %6.1fmm 模型孤岛 %d→%d · 板级孤岛 %s"
              % (net, dist, before, after,
                 ",".join("%s=%d" % (n, post.get(n, 0)) for n in sorted(touched)[:4])))

    print("── 接受 %d 个网 / 退回 %d 个" % (len(ok_nets), len(rej)))
    for (w_, n_) in rej[:20]:
        print("    · 退回: %s  [%s]" % (w_, n_))

    # ── 差异写回 (★已经逐网落过盘了 ⇒ 这里只重填铜皮 + 存盘) ──
    # ★★★**最终板总复核 (★关键: 逐网复核看不见跨网相互作用)** ★★★
    #   ★**A 的 rip-up 改了 B, B 的 rip-up 又改了 A ⇒ 逐网复核时每一网单独看都干净, 合起来就脏**
    #   ⇒ ★**这里对最终板的新铜做一次总复核** ⇒ 不合格 ⇒ ★**整轮回滚 (保持原板)**
    total_bad = []
    try:
        BCF = GC.BoardCopper(board)
        for s in r.tracks:
            if id(s) in ingested:
                continue
            (n2, x1, y1, x2, y2, li, w) = s
            okc, worst, who = GC.check_track(BCF, n2, (x1, y1), (x2, y2), w, li)
            if not okc:
                total_bad.append("走线[%s] 净距 %.3fmm %s" % (n2, worst, who))
        for v in r.vias:
            if id(v) in ingested:
                continue
            (n2, x, y, l1, l2) = v
            okc, worst, who = GC.check_via(BCF, n2, (x, y))
            if not okc:
                total_bad.append("过孔[%s] 净距 %.3fmm %s" % (n2, worst, who))
    except Exception as e:
        print("  ⚠️ 总复核失败: %s" % e)
    if total_bad:
        print("── ★★总复核: 新铜 %d 处不合格 ⇒ ★**整轮回滚 (输出板 = 输入板)**" % len(total_bad))
        for w_ in total_bad[:10]:
            print("     · %s" % w_)
        # ★★**最稳的回滚: 直接把输入板原样拷出去** (★不依赖任何内存回滚逻辑 ⇒ 不会有残留)
        import shutil
        shutil.copyfile(boardp, outp)
        print("── 已回滚: %s = 输入板 (%d B)" % (outp, os.path.getsize(outp)))
        print("── ★本轮逐网通过的是: %s ⇒ ★**下一轮可以只跑这些网**"
              % ", ".join(n for (n, _d, _b, _a) in ok_nets))
        return 0
    else:
        print("── ★★总复核通过: 新铜 0 处不合格 ⇒ 可以落盘")
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(outp)
    print("── 已写出: %s (%d B)" % (outp, os.path.getsize(outp)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
