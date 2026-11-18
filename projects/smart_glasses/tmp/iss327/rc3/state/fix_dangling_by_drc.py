#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_dangling_by_drc.py —— ★按 DRC 报告精确删除"悬空走线" (2026-11-04 23:5x)

★为什么不用"自己算连接关系"而要用 DRC 报告:
  我自己按"端点是否挨着别的段/焊盘/过孔"来判 ⇒ 判出来的"连着"与 KiCad 的连通性算法不一致
  ⇒ 漏掉了 5 条真悬空 (KiCad 报的 5 条 `track_dangling`, 全是 0.3536mm 的 45° 层间过渡短段:
  I2C_A_SDA ×2 / KEY_PWR ×2 / BOOT_N ×1 —— 它们的另一端本该落在过孔上, 但过孔没落 ⇒ 整段连不上任何东西)。
  ⇒ **直接照 DRC 的清单删**, 删完再跑一次 DRC 验证 ⇒ ★机器说了算, 不猜。

用法: bash state/pcbnew_py.sh state/fix_dangling_by_drc.py
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
BACKUP = "/tmp/board_before_dangling_fix.kicad_pcb"
DRC_JSON = "/tmp/_drc_dangling.json"
MAX_DELETE = 60


def run_drc():
    subprocess.run(["bash", KC, "pcb", "drc", "--output", DRC_JSON,
                    "--severity-error", "--severity-warning", "--format", "json", PCB],
                   capture_output=True, text=True, timeout=1200, cwd=PROJ)
    with open(DRC_JSON, encoding="utf-8") as f:
        return json.load(f)


def dangling_targets(doc):
    """从 DRC 报告里取出要删的段: (net, layer, pos, length)"""
    out = []
    for v in (doc.get("violations") or []):
        if v.get("type") != "track_dangling":
            continue
        for it in (v.get("items") or []):
            desc = str(it.get("description") or "")
            pos = it.get("pos") or {}
            net = layer = length = None
            if "[" in desc and "]" in desc:
                net = desc.split("[")[1].split("]")[0]
            if " on " in desc:
                layer = desc.split(" on ")[1].split(",")[0].strip()
            if "length " in desc:
                try:
                    length = float(desc.split("length ")[1].split(" mm")[0])
                except Exception:
                    length = None
            out.append({"net": net, "layer": layer,
                        "x": float(pos.get("x", 0)), "y": float(pos.get("y", 0)),
                        "length": length})
    return out


def main():
    shutil.copy2(PCB, BACKUP)
    print(f"★已备份 → {BACKUP}")
    doc = run_drc()
    targets = dangling_targets(doc)
    v_all = len(doc.get("violations") or [])
    u_all = len(doc.get("unconnected_items") or [])
    print(f"DRC: violations {v_all} · unconnected {u_all} · 待处理的悬空段 {len(targets)}")
    if not targets:
        print("✅ 没有悬空段 ⇒ 不用改")
        return 0
    if len(targets) > MAX_DELETE:
        print(f"❌ 悬空段超过 {MAX_DELETE} 条 ⇒ 中止 (先查路由器的几何逻辑)")
        return 1

    board = pcbnew.LoadBoard(PCB)
    tracks = [t for t in board.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T]
    layer_name = {pcbnew.F_Cu: "F.Cu", pcbnew.In1_Cu: "In1.Cu", pcbnew.In2_Cu: "In2.Cu",
                  pcbnew.In3_Cu: "In3.Cu", pcbnew.In4_Cu: "In4.Cu", pcbnew.B_Cu: "B.Cu"}
    deleted = 0
    for tg in targets:
        for t in list(tracks):
            if tg["net"] and t.GetNetname() != tg["net"]:
                continue
            if tg["layer"] and layer_name.get(t.GetLayer()) != tg["layer"]:
                continue
            # ★这个 KiCad 构建里 GetStart()/GetEnd() 返回的是通用 SwigPyObject ⇒ 必须显式转成 VECTOR2I
            a = pcbnew.VECTOR2I(t.GetStart())
            b = pcbnew.VECTOR2I(t.GetEnd())
            ln = max(abs(a.x - b.x), abs(a.y - b.y)) / 1e6
            px = pcbnew.FromMM(tg["x"])
            py = pcbnew.FromMM(tg["y"])
            hit = ((abs(a.x - px) <= pcbnew.FromMM(0.05) and abs(a.y - py) <= pcbnew.FromMM(0.05)) or
                   (abs(b.x - px) <= pcbnew.FromMM(0.05) and abs(b.y - py) <= pcbnew.FromMM(0.05)))
            if not hit:
                continue
            if tg["length"] is not None and abs(ln - tg["length"]) > 0.12:
                continue
            board.Remove(t)
            tracks.remove(t)
            deleted += 1
            break
    print(f"★删除 {deleted} / {len(targets)} 条悬空段")
    pcbnew.SaveBoard(PCB, board)
    print("✓ 已保存")

    doc2 = run_drc()
    v2 = len(doc2.get("violations") or [])
    u2 = len(doc2.get("unconnected_items") or [])
    print(f"★复验: violations {v_all} → {v2} · unconnected {u_all} → {u2}")
    if v2 > v_all:
        print("❌ 违规变多 ⇒ 回滚")
        shutil.copy2(BACKUP, PCB)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
