#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_rip_roi2.py -- ★★方案Y 的收尾: 把【压在别网铜上】的新铜挑掉 ⇒ 看能不能 DRC0 + unc<45

★★★**★背景 (★2026-11-09 17:0x 实测)★★★**
  ★**方案Y (★原板 + 只保留目标网新铜, ★丢弃整网重画的其他网) ⇒ DRC 8 / unc 44** (★官方 45 ⇒ ★好 1 条)
  ★**那 8 条全是同一处**: ★**目标网新铜与 `VDD_3V3_IO` 的铜短路/净距不足** (★净距 0.0152~0.125mm)
    ⇒ ★**A\\* 把新铜放在了【别网铜的接头点】上 ⇒ ★★**halo 没挡住那一格** ★★
  ★**本脚本**: ★**把【卷入违规的新铜段】挑掉 ⇒ 再量 ⇒ ★★**看能不能不碰路由器就拿到干净板** ★★

用法: bash state/pcbnew_py.sh state/probe_rip_roi2.py <方案Y板> <原板> <目标网>
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("PCB_LAYERS", "8")
import gen_pcb_routing as RT  # noqa: E402
import geom_clear as GC  # noqa: E402


def parse(p):
    t = open(p, encoding="utf-8", errors="ignore").read()
    return [m.groups() for m in re.finditer(
        r"\(segment\s*\n\s*\(start ([-\d.]+) ([-\d.]+)\)\s*\n\s*"
        r"\(end ([-\d.]+) ([-\d.]+)\)\s*\n\s*\(width ([0-9.]+)\)\s*\n\s*"
        r'\(layer "([^"]+)"\)\s*\n\s*\(net "([^"]+)"\)', t)]


def main():
    yp = sys.argv[1]
    origp = sys.argv[2]
    target = sys.argv[3]
    outp = "/tmp/_rip_roi_Z.kicad_pcb"

    orig = set(parse(origp))
    ys = parse(yp)
    new = [g for g in ys if g not in orig]
    print("★方案Y 板: %d 段 · 其中新铜 %d 段 (★%s)" % (len(ys), len(new), target))

    # ── 用项目自己的真几何尺, 逐条筛【卷入违规的新铜】 ──
    b = RT.GridRouter(yp, grid=0.125) if False else None
    # ★**直接用 geom_clear 的板级索引** (★它是本项目的真几何尺)
    import pcbnew
    board = pcbnew.LoadBoard(yp)
    BC = GC.BoardCopper(board)

    bad_segs = []
    for (x1, y1, x2, y2, w, li, net) in new:
        if net != target:
            continue
        okc, worst, who = GC.check_track(BC, net, (float(x1), float(y1)), (float(x2), float(y2)),
                                         float(w), li)
        if not okc:
            bad_segs.append(((x1, y1, x2, y2, w, li, net), worst, who))
    print("★卷入违规的目标网新铜 = %d / %d 段" % (len(bad_segs), len([g for g in new if g[6] == target])))
    for g, worst, who in bad_segs[:8]:
        print("    净距 %.4fmm  %s  %s" % (worst, who, g[:4]))

    # ── 方案Z = 方案Y − 违规新铜 ──
    txt = open(yp, encoding="utf-8", errors="ignore").read()
    drop_keys = set()
    for (g, _w, _who) in bad_segs:
        drop_keys.add(g[:4])
    removed = 0
    lines = txt.split("\n")
    out = []
    i = 0
    while i < len(lines):
        l = lines[i]
        if l.strip() == "(segment":
            blk = "\n".join(lines[i:i + 8])
            m = re.search(r"\(start ([-\d.]+) ([-\d.]+)\)\s*\n\s*\(end ([-\d.]+) ([-\d.]+)\)", blk)
            if m and (m.group(1), m.group(2), m.group(3), m.group(4)) in drop_keys:
                # ★跳过这个 segment 块 (★它到下一个单独的 ")" 行结束)
                j = i
                while j < len(lines) and lines[j].strip() != ")":
                    j += 1
                i = j + 1
                removed += 1
                continue
        out.append(l)
        i += 1
    open(outp, "w", encoding="utf-8").write("\n".join(out))
    print("✓ 方案Z 已写: %s (★去掉 %d 段违规新铜)" % (outp, removed))

    drc = "/tmp/_drc_roiZ.json"
    subprocess.run(["bash", "state/kicad.sh", "pcb", "drc", "--output", drc,
                    "--severity-error", "--severity-warning", "--format", "json", outp],
                   capture_output=True, timeout=1800)
    try:
        d = json.load(open(drc, encoding="utf-8"))
        nv = len(d.get("violations") or [])
        nu = len(d.get("unconnected_items") or [])
        c = {}
        for v in (d.get("violations") or []):
            c[v.get("type") or "?"] = c.get(v.get("type") or "?", 0) + 1
        print("★★★ 方案Z (原板 + 目标网新铜 − 违规段): DRC违规 = %d · unconnected = %d  (★官方 45)" % (nv, nu))
        if c:
            print("    违规类型:", c)
    except Exception as e:
        print("  ★DRC 读取失败:", e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
