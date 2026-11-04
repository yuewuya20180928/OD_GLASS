#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_gnd_stitch.py —— ★① 清理悬空走线 ② GND 缝合 (2026-11-04 23:5x, 项目总工)

★★第一版踩坑记录 (必须留着, 免得再犯):
  第一版的 `clean_dangling` 只把"端点是否挨着**焊盘/过孔**"当作连接依据 ⇒ **没有把"别的段的端点"算进去**
  ⇒ 结果 22179 段里 **20664 段被误判成悬空而删掉** ⇒ 板子从 117 未连接变成 **499 未连接 + 178 条 dangling** ⇒
  ★**差点把两小时的工作删了** ⇒ 幸好动手前先 `cp` 了备份 ⇒ 10 秒回滚。
  ⇒ ★**新铁律: 清理类脚本必须 (a) 先备份 (b) 带"删太多就中止"的安全闸 (c) 清理完立刻跑 DRC 对比**.

★逻辑 (正确的连接判定):
  一个"端点"算连上, 当且仅当它挨着: ① 焊盘中心 ② 过孔中心 ③ **另一段走线的端点**
  ⇒ 端点只被"自己这一段"碰到 ⇒ 才是真悬空。

用法:
  bash state/pcbnew_py.sh state/fix_gnd_stitch.py --clean-only   # 只清理悬空段 (安全)
  bash state/pcbnew_py.sh state/fix_gnd_stitch.py                  # 清理 + GND 缝合
"""
import os
import math
import shutil
import sys

import pcbnew

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.environ.get("PCB_FILE") or os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
BACKUP = os.environ.get("PCB_BACKUP") or "/tmp/board_before_fix.kicad_pcb"

GND = "GND"
VIA_DIA = pcbnew.FromMM(0.60)
VIA_DRILL = pcbnew.FromMM(0.30)
TRACK_W = pcbnew.FromMM(0.30)
STUB = pcbnew.FromMM(0.35)      # 焊盘外沿 → 过孔中心
TOL_PAD = pcbnew.FromMM(0.12)
TOL_EXACT = pcbnew.FromMM(0.02)
MAX_DEL_RATIO = 0.02            # ★安全闸: 删掉的段超过 2% ⇒ 中止不保存


def netcode_of(board, name):
    try:
        c = board.GetNetcodeFromNetname(name)
        if c and c > 0:
            return c
    except Exception:
        pass
    try:
        ni = board.FindNet(name)
        if ni is not None:
            return ni.GetNetCode()
    except Exception:
        pass
    try:
        for code, net in board.GetNetInfo().GetNetsByNetcode().items():
            if net.GetNetname() == name:
                return code
    except Exception:
        pass
    return 0


def collect(board):
    segs = [t for t in board.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T]
    vias = [t for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
    pads = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            pads.append((pad.GetPosition().x, pad.GetPosition().y))
    return segs, vias, pads


def end_is_connected(p, pad_pts, via_pts, seg_end_count, skip_seg):
    """端点 p 是否连在别的东西上 (焊盘/过孔/**别的段的端点**)"""
    for (px, py) in pad_pts:
        if abs(px - p.x) <= TOL_PAD and abs(py - p.y) <= TOL_PAD:
            return True
    for (px, py) in via_pts:
        if abs(px - p.x) <= TOL_EXACT and abs(py - p.y) <= TOL_EXACT:
            return True
    # ★别的段的端点 (本段自己的端点要排除)
    for (px, py, cnt) in seg_end_count:
        if cnt <= 1:
            continue
        if abs(px - p.x) <= TOL_EXACT and abs(py - p.y) <= TOL_EXACT:
            return True
    return False


def clean_dangling(board):
    segs, vias, pads = collect(board)
    # 统计每个"端点坐标"被多少段端点占用
    cnt = {}
    for s in segs:
        for p in (s.GetStart(), s.GetEnd()):
            cnt[(p.x, p.y)] = cnt.get((p.x, p.y), 0) + 1
    seg_end_count = [(x, y, c) for (x, y), c in cnt.items()]
    via_pts = [(v.GetPosition().x, v.GetPosition().y) for v in vias]

    removed = zero = trimmed = 0
    for s in list(segs):
        a, b = s.GetStart(), s.GetEnd()
        if a.x == b.x and a.y == b.y:                       # 零长段
            board.Remove(s)
            removed += 1
            zero += 1
            continue
        oka = end_is_connected(a, pads, via_pts, seg_end_count, s)
        okb = end_is_connected(b, pads, via_pts, seg_end_count, s)
        if not oka and not okb:                            # 两端都悬空 ⇒ 整段无用
            board.Remove(s)
            removed += 1
        elif not oka or not okb:                           # 一端悬空 ⇒ 整段删 (它连不上任何东西)
            board.Remove(s)
            removed += 1
            trimmed += 1
    return removed, zero, trimmed


def stitch_gnd(board, gnd_net=None):
    gnd = gnd_net if gnd_net else netcode_of(board, GND)
    if gnd <= 0:
        print("⚠️ 找不到 GND 网")
        return 0
    segs, vias, pads = collect(board)
    via_pts = [(v.GetPosition().x, v.GetPosition().y) for v in vias]
    seg_pts = set()
    for s in segs:
        seg_pts.add((s.GetStart().x, s.GetStart().y))
        seg_pts.add((s.GetEnd().x, s.GetEnd().y))
    bbox = board.GetBoardEdgesBoundingBox()
    added = 0
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() != GND:
                continue
            pos = pad.GetPosition()
            if any(abs(px - pos.x) <= TOL_PAD and abs(py - pos.y) <= TOL_PAD for (px, py) in pads + via_pts + list(seg_pts)):
                continue
            size = pad.GetSize()
            placed = False
            for (cx, cy) in ((pos.x + int(size.x / 2 + STUB), pos.y),
                              (pos.x - int(size.x / 2 + STUB), pos.y),
                              (pos.x, pos.y + int(size.y / 2 + STUB)),
                              (pos.x, pos.y - int(size.y / 2 + STUB))):
                if not bbox.Contains(pcbnew.VECTOR2I(cx, cy)):
                    continue
                if any(abs(px - cx) <= pcbnew.FromMM(0.25) and abs(py - cy) <= pcbnew.FromMM(0.25)
                       for (px, py) in via_pts + list(seg_pts)):
                    continue
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(pcbnew.VECTOR2I(cx, cy))
                v.SetViaType(pcbnew.VIATYPE_THROUGH)
                v.SetWidth(VIA_DIA)
                v.SetDrill(VIA_DRILL)
                v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                v.SetNetCode(gnd)
                board.Add(v)
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(pcbnew.VECTOR2I(pos.x, pos.y))
                t.SetEnd(pcbnew.VECTOR2I(cx, cy))
                t.SetWidth(TRACK_W)
                t.SetLayer(pad.GetLayer())
                t.SetNetCode(gnd)
                board.Add(t)
                via_pts.append((cx, cy))
                seg_pts.add((cx, cy))
                added += 1
                placed = True
                break
            if not placed:
                pass
    return added


def main():
    clean_only = "--clean-only" in sys.argv
    shutil.copy2(PCB, BACKUP)
    print(f"★已备份 → {BACKUP}")
    board = pcbnew.LoadBoard(PCB)
    # ★**先取 GND 的 netcode**: 删过段之后 SWIG 对象可能失真, FindNet 会返回 None ⇒ 提前取好
    gnd_net = netcode_of(board, GND)
    print(f"  载入: GND netcode = {gnd_net}")
    segs, vias, _ = collect(board)
    print(f"  载入: 走线 {len(segs)} 段 · 过孔 {len(vias)} 个")

    stitch_only = "--stitch-only" in sys.argv
    removed, zero, trimmed = (0, 0, 0) if stitch_only else clean_dangling(board)
    print(f"★清理: 共删 {removed} 段 (零长 {zero} · 单端悬空 {trimmed})")
    # ★安全闸只算"**单端悬空**"那部分: 零长段**不承载任何连接** ⇒ 删它永远安全
    #   (实测: 板里有 498 段零长段, 占 2.2% ⇒ 若把零长段也算进去, 安全闸会误拦)
    risky = trimmed
    if segs and risky > len(segs) * MAX_DEL_RATIO:
        print(f"❌ 安全闸触发: 单端悬空删除 {risky} 段 ({risky/len(segs):.1%} > {MAX_DEL_RATIO:.0%}) ⇒ 不保存, 请查逻辑")
        return 1
    print(f"★安全闸: 单端悬空删除 {risky} 段 ({risky/len(segs)*100:.2f}%, 上限 {MAX_DEL_RATIO*100:.0f}%) ⇒ 放行")

    if not clean_only:
        n = stitch_gnd_v2(board, gnd_net)
        print(f"★GND 缝合 (v2): 新增 {n} 个过孔 + 短引线")

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)
    try:
        segs2, vias2, _ = collect(board)
        print(f"✓ 已保存: 走线 {len(segs2)} 段 · 过孔 {len(vias2)} 个")
    except Exception as e:   # ★pcbnew 的 SWIG 对象在 SaveBoard 后不可再迭代 ⇒ 只报文件实际计数
        print(f"✓ 已保存 (统计跳过: {e})")
    return 0


# ============================================================
# ★★2026-11-05 02:4x: 缝合 v2 (实测修)
#   旧版 (v1) 加了 **0 个过孔** ⇒ 原因: 跳过条件把 **所有网** 的走线端点/过孔都算进去了
#   ⇒ 一个 GND 焊盘只要挨着**别的网**的某个端点 (0.12mm 容差) 就被跳过 ⇒ 全部跳过
#   ⇒ ★而且实测 DRC: GND 焊盘上挂着 1.2mm 的短引线却**没有过孔下到平面** ⇒ 正是缺"缝合过孔"
#   ⇒ v2 规则:
#     ① 只有**同网 (GND) 的过孔**挨着焊盘才算"已缝合" (别的网一律不管)
#     ② 放缝合过孔时, 净距只跟**别的网**的铜算 (走线/过孔/焊盘), 与路由器同一口径 (CLEAR=0.20mm)
#     ③ 缝合完必须重填铜皮 (ZONE_FILLER) ⇒ 过孔才会真的连到 L2/L6 的 GND 平面
# ============================================================
MM = 1000000
CLEAR_MM = 0.20
VIA_D = 0.60
TRK_W = 0.30


def stitch_gnd_v2(board, gnd_code):
    """给没缝合到 GND 平面的 GND 焊盘补过孔 + 短引线 ⇒ 返回新增数"""
    segs = [t for t in board.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T]
    vias = [t for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
    gnd_via_pts = [(v.GetPosition().x, v.GetPosition().y) for v in vias
                   if v.GetNetCode() == gnd_code]
    # ★别的网的铜 (用于净距检查)
    other_segs = [(t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y, t.GetLayer())
                  for t in segs if t.GetNetCode() != gnd_code]
    other_vias = [(v.GetPosition().x, v.GetPosition().y) for v in vias
                  if v.GetNetCode() != gnd_code]
    other_pads = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetCode() != gnd_code:
                pos = pad.GetPosition(); sz = pad.GetSize()
                other_pads.append((pos.x - sz.x / 2, pos.y - sz.y / 2,
                                    pos.x + sz.x / 2, pos.y + sz.y / 2, pad.GetLayer()))
    bbox = board.GetBoardEdgesBoundingBox()
    added = 0
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetCode() != gnd_code:
                continue
            pos = pad.GetPosition()
            # ① 已缝合? (只看同网过孔)
            if any(abs(px - pos.x) <= TOL_PAD and abs(py - pos.y) <= TOL_PAD
                   for (px, py) in gnd_via_pts):
                continue
            size = pad.GetSize()
            layer = pad.GetLayer()
            placed = False
            for (cx, cy) in ((pos.x + int(size.x / 2 + STUB), pos.y),
                              (pos.x - int(size.x / 2 + STUB), pos.y),
                              (pos.x, pos.y + int(size.y / 2 + STUB)),
                              (pos.x, pos.y - int(size.y / 2 + STUB))):
                if not bbox.Contains(pcbnew.VECTOR2I(cx, cy)):
                    continue
                need_via = CLEAR_MM * MM
                # ② 净距: 别的网走线 (同层) / 过孔 / 焊盘
                bad = False
                for (x1, y1, x2, y2, li) in other_segs:
                    if li != layer:
                        continue
                    if _seg_dist(cx, cy, x1, y1, x2, y2) < need_via:
                        bad = True; break
                if not bad:
                    for (vx, vy) in other_vias:
                        if abs(vx - cx) <= need_via and abs(vy - cy) <= need_via:
                            bad = True; break
                if not bad:
                    for (x0, y0, x1, y1, li) in other_pads:
                        if li != layer:
                            continue
                        if x0 - need_via <= cx <= x1 + need_via and y0 - need_via <= cy <= y1 + need_via:
                            bad = True; break
                if bad:
                    continue
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(pcbnew.VECTOR2I(cx, cy))
                v.SetViaType(pcbnew.VIATYPE_THROUGH)
                v.SetWidth(VIA_DIA)
                v.SetDrill(VIA_DRILL)
                v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                v.SetNetCode(gnd_code)
                board.Add(v)
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(pcbnew.VECTOR2I(pos.x, pos.y))
                t.SetEnd(pcbnew.VECTOR2I(cx, cy))
                t.SetWidth(pcbnew.FromMM(TRK_W))
                t.SetLayer(layer)
                t.SetNetCode(gnd_code)
                board.Add(t)
                gnd_via_pts.append((cx, cy))
                added += 1
                placed = True
                break
    return added


def _seg_dist(px, py, x1, y1, x2, y2):
    """点到线段的距离 (mm)"""
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 <= 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))



if __name__ == "__main__":
    sys.exit(main())
