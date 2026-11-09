#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_skip_pad_leak.py —— ★★验证【成品板修复】的漏洞: 已有铜的 halo 被跳过 ⇒ 新铜能压在它上面

★★★**★为什么要有这个 (★2026-11-09 09:0x 实测)★★★**
  ★**症状**: ★**rip-and-replace 在官方板上造出的新铜与别网铜【净距 0.000mm (重叠)】**
    ⇒ ★**例**: ★**`走线[ID_DETECT_0] 净距 0.000mm 走线[USB_D_N_SRC]`**
  ★**机制 (★实读代码确认)**: ★**`rebuild_halo()` 里**
    · ★**走线**: ★**`_add_track_halo(...)` ⇒ ★**走 env `PCB_SKIP_PAD_CELLS` ✔**
    · ★★**过孔**: ★★**`_add_via_halo(net,x,y,l1,l2)` ⇒ ★★**`skip_pad_cells` 是【函数默认值 True】⇒ 走 env 也改不了** ★★
  ⇒ ★★**⇒ 已有【过孔】的 halo 在【异网焊盘格】上被跳过 ⇒ ⇒ 新铜可以正好压在那个过孔上** ★★
  ★**本脚本**: ★**统计"已有铜落在异网焊盘格里"的处数 ⇒ 若 >0 ⇒ 机制成立** ★

用法: bash state/pcbnew_py.sh state/probe_skip_pad_leak.py [板]
"""
import math
import os
import sys

import pcbnew

MM = 1000000.0
G = 0.125

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("PCB_LAYERS", "8")
import gen_pcb_routing as RT  # noqa: E402


def main():
    boardp = sys.argv[1] if len(sys.argv) > 1 else "HW/PCB/demo_mainboard.kicad_pcb"
    b = pcbnew.LoadBoard(boardp)
    if b is None:
        print("★板读不出来")
        return 2
    CU = RT.CU_LAYERS
    LAY = {l: i for i, l in enumerate(CU)}
    LN = {l: RT.LayerName(l) if hasattr(RT, "LayerName") else str(l) for l in CU}

    # ① pad_cell: (层索引, 格i, 格j) -> 网集合
    padcell = {}
    for fp in b.GetFootprints():
        for p in fp.Pads():
            nm = p.GetNetname()
            if not nm:
                continue
            pos = p.GetPosition()
            cx, cy = pos.x / MM, pos.y / MM
            ls = p.GetLayerSet()
            for l in CU:
                if ls.Contains(l):
                    i, j = int(math.floor(cx / G)), int(math.floor(cy / G))
                    padcell.setdefault((LAY[l], i, j), set()).add(nm)

    # ② 已有铜落在异网焊盘格里的处数
    leaks = {"VIA": [], "TRK": []}
    for t in b.GetTracks():
        nm = t.GetNetname()
        if not nm:
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            pos = t.GetPosition()
            cx, cy = pos.x / MM, pos.y / MM
            i, j = int(math.floor(cx / G)), int(math.floor(cy / G))
            for l in CU:
                pc = padcell.get((LAY[l], i, j))
                if pc and any(x != nm for x in pc):
                    leaks["VIA"].append((nm, round(cx, 3), round(cy, 3), sorted(pc)))
        else:
            s, e = t.GetStart(), t.GetEnd()
            li = LAY.get(t.GetLayer())
            if li is None:
                continue
            n = int(max(abs(e.x - s.x), abs(e.y - s.y)) / MM / G) + 1
            for k in range(n + 1):
                x = (s.x + (e.x - s.x) * k / max(n, 1)) / MM
                y = (s.y + (e.y - s.y) * k / max(n, 1)) / MM
                i, j = int(math.floor(x / G)), int(math.floor(y / G))
                pc = padcell.get((li, i, j))
                if pc and any(q != nm for q in pc):
                    leaks["TRK"].append((nm, round(x, 3), round(y, 3), sorted(pc)))

    print("★板: %s" % boardp)
    print("★已有【过孔】落在异网焊盘格里的处数 = %d" % len(leaks["VIA"]))
    print("  ⇒ ★★**这些过孔的 halo 会被跳过 (_add_via_halo 默认 skip_pad_cells=True) ⇒ ⇒ 新铜可以压上去** ★★")
    for h in leaks["VIA"][:8]:
        print("    ", h)
    print("★已有【走线】落在异网焊盘格里的处数 = %d" % len(leaks["TRK"]))
    print("  ⇒ ★走线的 halo 走 env 开关 (★PCB_SKIP_PAD_CELLS=0 ⇒ 不跳) ⇒ ★★**不是漏洞源** ★★")
    for h in leaks["TRK"][:8]:
        print("    ", h)
    return 0


if __name__ == "__main__":
    sys.exit(main())
