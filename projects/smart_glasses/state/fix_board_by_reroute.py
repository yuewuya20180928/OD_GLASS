#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_board_by_reroute.py -- ★★★**把成品板交给路由器, 用整套 rip-up 机器重布失败网** (11-06 06:0x)

★★★**为什么这是正解 (11-06 05:0x~06:0x 实测链)**:
  ① 官方板 57 项未连接 ⇒ 2 条 <2mm + 10 条 2~10mm + 45 条 >10mm (主体 DSI/CSI)
  ② 单点 A* 补段 (state/fix_unconnected_astar.py) ⇒ **只能干净补 1 条** ⇒ **板子太挤, 搜不动**
  ③ ★★★**但路由器本来就有整套 rip-up 机器** (`ripup_and_reroute`):
       找挡路铜 (`_blockers_for` + ★v52 的 `_escape_blockers`) ⇒ 拆 ⇒ 重布 ⇒ 失败就还原
     ⇒ ⇒ **v52 已实测救回 5 条 DSI/CSI 网** ⇒ ⇒ **方向是对的**
  ④ ⇒⇒ **本脚本 = 把官方板灌进路由器, 让它对失败网跑 rip-up, 再把差异写回板**
     ⇒ ⇒ **这是"官方板也能用 rip-up"的唯一路径** (官方板是历史产物, 路由器重跑复现不了它)

★★**与 commit() 的区别 (★关键)**:
  · commit() 会把 `self.tracks` 全部写进板 ⇒ ⇒ **已被 rip-up 拆掉的铜也会被写回去 ⇒ 重复铜**
  ⇒ ⇒ **本脚本自己做差异**: 被拆的 ⇒ 从板上删; 新增的 ⇒ 往板上加; 没动的 ⇒ 不碰

★**安全**:
  · 只写 --out 路径, 绝不原地改
  · ★**被拆的铜如果重布失败, 路由器自己会还原** ⇒ 铜量不会净减少
  · 跑完必须 fresh DRC ⇒ 违规不为 0 就废弃

用法:
  bash state/pcbnew_py.sh state/fix_board_by_reroute.py <板> <DRC.json> --out <新板> [--passes 2] [--rip 8]
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
os.environ.setdefault("PCB_RIPUP_ALIVE", "1")     # ★**必须开** ⇒ 失败网才进 rip-up
os.environ.setdefault("PCB_RIPUP_ESC", "1")       # ★**必须开** ⇒ 出脚走廊感知

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pcbnew  # noqa: E402
import gen_pcb_routing as RT  # noqa: E402

MM = 1e6


def failing_nets(drc_path):
    """★从 DRC JSON 精确抽"未连接"的网名 (★方括号取值, 不做子串匹配)"""
    d = json.load(open(drc_path, encoding="utf-8"))
    out = {}
    for it in d.get("unconnected_items", []):
        s = json.dumps(it, ensure_ascii=False)
        for m in re.finditer(r"Pad\s+\S+\s+\[([^\]]+)\]", s):
            out.setdefault(m.group(1), 0)
            out[m.group(1)] += 1
    return out


def main():
    args = sys.argv[1:]
    if len(args) < 4:
        print(__doc__)
        return 2
    boardp, drcp = args[0], args[1]
    outp = None
    passes = 2
    rip = 8
    batch = 5
    statef = None
    only = None
    i = 2
    while i < len(args):
        if args[i] == "--out":
            outp = args[i + 1]
            i += 2
        elif args[i] == "--passes":
            passes = int(args[i + 1])
            i += 2
        elif args[i] == "--rip":
            rip = int(args[i + 1])
            i += 2
        elif args[i] == "--batch":
            batch = int(args[i + 1])
            i += 2
        elif args[i] == "--state":
            statef = args[i + 1]
            i += 2
        elif args[i] == "--only":
            only = [x.strip() for x in args[i + 1].split(",") if x.strip()]
            i += 2
        else:
            i += 1
    if not outp:
        print("★必须给 --out")
        return 2

    done = set()
    src_board = boardp
    if statef and os.path.exists(statef):
        try:
            st = json.load(open(statef, encoding="utf-8"))
            done = set(st.get("done", []))
            if st.get("out") and os.path.exists(st["out"]):
                src_board = st["out"]
                print("═══ 续跑: 已处理 %d 个网, 从 %s 继续 ═══" % (len(done), src_board))
        except Exception as e:
            print("  ⚠️ state 读不了: %s" % e)
    board = pcbnew.LoadBoard(src_board)
    for z in board.Zones():
        z.UnFill()
    r = RT.GridRouter(board)
    print("═══ 成品板重布: %s ═══" % boardp)
    print("═══ 环境: RIPUP_ALIVE=%s RIPUP_ESC=%s · %d 层 · 网格 %.2fmm ═══" %
          (os.environ.get("PCB_RIPUP_ALIVE"), os.environ.get("PCB_RIPUP_ESC"),
           RT.NLAYERS, r.g))

    # ── 灌入板上已有的铜 (★路由器自己的 tracks/vias 记法) ──
    ingested = {}          # id(记录元组) → 板上的图元对象 (★拆的时候要删它)
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
    print("═══ 已灌入: %d 条走线 / %d 个过孔 (halo 已重建) ═══" %
          (len(r.tracks), len(r.vias)))

    nets = failing_nets(drcp)
    print("═══ 失败网 %d 个 ⇒ 逐轮 rip-up (每轮拆 %d 条) ═══" % (len(nets), rip))
    # ★**短距优先**: ★**越近的越容易救回来** ⇒ ★**先修便宜的**
    order = sorted(nets.keys(), key=lambda n: nets[n])
    ok_total = 0
    _order = order
    if only:
        _order = [n for n in order if n in only]
        print("═══ ★只处理指定网 (%d 个): %s ═══" % (len(_order), " ".join(_order)))
    todo = [n for n in _order if n not in done]
    print("═══ 待处理 %d 个网 (每 %d 个落一次盘) ═══" % (len(todo), batch))

    def save_state():
        if not statef:
            return
        try:
            json.dump({"done": sorted(done), "out": outp}, open(statef, "w", encoding="utf-8"))
        except Exception:
            pass

    # ★★分批: ★**每批跑完就落盘 + 记 state** ⇒ ★**被杀也不丢进度 (★原版只在最后写盘 ⇒ 一被杀全丢)**
    _todo = list(todo)
    while _todo:
        chunk = _todo[:batch]
        _todo = _todo[batch:]
        r.routed_ok = set()
        r.routed = set()
        ok = r.ripup_and_reroute(chunk, rip_per_net=rip, verbose=True)
        ok_total += ok
        for n in chunk:
            done.add(n)
        print("── 本批 %d 个网: 重布成功 %d (累计 %d) ⇒ 落盘" % (len(chunk), ok, ok_total))
        # ★差异写回 (每批都写一次) ★
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
            ingested[id(s)] = (t, s)
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
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        board.Save(outp)
        save_state()
        print("── 已落盘: %s (%d B) · 已处理 %d 个网" % (outp, os.path.getsize(outp), len(done)))

    # ── 差异写回: 被拆的删掉, 新增的加上去 ──
    alive = set(id(s) for s in r.tracks) | set(id(v) for v in r.vias)
    n_del = 0
    for oid, (obj, rec) in list(ingested.items()):
        if oid not in alive:
            board.Remove(obj)
            n_del += 1
    n_add = 0
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
        n_add += 1
    print("── 差异: 删 %d 个旧图元 / 加 %d 个新图元 (净 %+d)" % (n_del, n_add, n_add - n_del))

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    board.Save(outp)
    print("── 已写出: %s (%d B)" % (outp, os.path.getsize(outp)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
