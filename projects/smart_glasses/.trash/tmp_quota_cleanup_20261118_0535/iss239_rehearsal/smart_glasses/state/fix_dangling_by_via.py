#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_dangling_by_via.py —— ★给"悬空走线"的悬空端**补过孔**(而不是删段) (2026-11-04 23:5x)

★为什么不能删段 (实测踩过):
  第一版想法是"把 DRC 报的 track_dangling 段删掉" ⇒ 实测 **删了又长出新的**:
  DRC 3 → 6, unconnected 117 → 120, 连跑 3 轮都是同一结果 ⇒ ★**删段是振荡 (删一段 ⇒ 它的邻段变成悬空)**。
  ⇒ 正确做法: ★**那 5~6 条 0.3536mm 的 45° 段本该是"层间过渡段"** (router 打算在这里换层)
    ⇒ 它的另一端本该落在**过孔**上, 但过孔没落 ⇒ ★**在悬空端补一个过孔**就把过渡补齐了 (而不是删掉这段)。

用法: bash state/pcbnew_py.sh state/fix_dangling_by_via.py
"""
import json
import os
import shutil
import subprocess
import sys

import pcbnew

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
KC = os.path.join(PROJ, "state", "kicad.sh")
DRC_JSON = "/tmp/_drc_via_fix.json"
BACKUP = "/tmp/board_before_via_fix.kicad_pcb"
VIA_DIA = pcbnew.FromMM(0.60)
VIA_DRILL = pcbnew.FromMM(0.30)
MAX_VIA = 40


def run_drc():
    subprocess.run(["bash", KC, "pcb", "drc", "--output", DRC_JSON,
                    "--severity-error", "--severity-warning", "--format", "json", PCB],
                   capture_output=True, text=True, timeout=1800, cwd=PROJ)
    with open(DRC_JSON, encoding="utf-8") as f:
        return json.load(f)


def targets(doc):
    out = []
    for v in (doc.get("violations") or []):
        if v.get("type") != "track_dangling":
            continue
        for it in (v.get("items") or []):
            desc = str(it.get("description") or "")
            pos = it.get("pos") or {}
            net = desc.split("[")[1].split("]")[0] if "[" in desc else None
            layer = desc.split(" on ")[1].split(",")[0].strip() if " on " in desc else None
            out.append({"net": net, "layer": layer,
                        "x": float(pos.get("x", 0)), "y": float(pos.get("y", 0))})
    return out


def main():
    shutil.copy2(PCB, BACKUP)
    doc = run_drc()
    tg = targets(doc)
    v0 = len(doc.get("violations") or [])
    u0 = len(doc.get("unconnected_items") or [])
    print(f"★已备份 → {BACKUP}")
    print(f"DRC: violations {v0} · unconnected {u0} · 悬空段 {len(tg)}")
    if not tg:
        print("✅ 无悬空段")
        return 0
    if len(tg) > MAX_VIA:
        print(f"❌ 悬空段 > {MAX_VIA} ⇒ 中止")
        return 1

    board = pcbnew.LoadBoard(PCB)
    tracks = [t for t in board.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T]
    added = 0
    for t in tg:
        # 找同网同层的那个段, 把过孔落在 DRC 指出的悬空端
        cand = None
        for tr in tracks:
            if t["net"] and tr.GetNetname() != t["net"]:
                continue
            a = pcbnew.VECTOR2I(tr.GetStart())
            b = pcbnew.VECTOR2I(tr.GetEnd())
            px = pcbnew.FromMM(t["x"])
            py = pcbnew.FromMM(t["y"])
            if (abs(a.x - px) <= pcbnew.FromMM(0.05) and abs(a.y - py) <= pcbnew.FromMM(0.05)) or \
               (abs(b.x - px) <= pcbnew.FromMM(0.05) and abs(b.y - py) <= pcbnew.FromMM(0.05)):
                cand = tr
                break
        if cand is None:
            continue
        netcode = cand.GetNetCode()
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(t["x"]), pcbnew.FromMM(t["y"])))
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetWidth(VIA_DIA)
        v.SetDrill(VIA_DRILL)
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNetCode(netcode)
        board.Add(v)
        added += 1
    print(f"★补过孔 {added} 个 (落在悬空端, 把层间过渡补齐)")
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)
    print("✓ 已保存")

    doc2 = run_drc()
    v2 = len(doc2.get("violations") or [])
    u2 = len(doc2.get("unconnected_items") or [])
    print(f"★复验: violations {v0} → {v2} · unconnected {u0} → {u2}")
    if v2 > v0:
        print("❌ 违规变多 ⇒ 回滚")
        shutil.copy2(BACKUP, PCB)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
