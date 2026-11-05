#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_csi_order.py —— ★判定: CSI/DSI 到底需不需要 P/N 自交 (机器读官方板)

★**为什么必须先测这个**:
  cron 播报说 "CSI 侧 5 对缺铜 ⇒ v38 crossover" ⇒ ★**但缺铜 ≠ 需要交叉**
  ⇒ 审计实测规律: **P 侧基本通了 / N 侧基本没通** ⇒ ★**也可能是纯拥塞**
  ⇒ ★**交叉 = 拓扑问题; 拥塞 = 几何问题** ⇒ 搞错就白造一个臂

★**改用 pcbnew 直读** (自绘解析器被 KiCad 7 格式坑了: `(footprint ""` + property Reference + pad 号与 size 分行)
"""
import sys, re, collections

PCB = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/yuewuya/.openclaw/workspace/projects/smart_glasses/HW/PCB/demo_mainboard.kicad_pcb"

import pcbnew
b = pcbnew.LoadBoard(PCB)
print("═══ 板: %s ═══" % PCB)

pads = []
for f in b.GetFootprints():
    ref = f.GetReference()
    for p in f.Pads():
        pos = p.GetPosition()
        net = p.GetNetname()
        pads.append(dict(ref=ref, pad=p.GetNumber(), net=net,
                         x=pos.x / 1e6, y=pos.y / 1e6,
                         w=p.GetSize().x / 1e6, h=p.GetSize().y / 1e6))
print("═══ 焊盘总数: %d ═══" % len(pads))

def lane_nets(kind):
    out = collections.defaultdict(dict)
    for p in pads:
        nm = p["net"]
        m = re.match(r'^(CSI|DSI)_D0_(D\d|CK)_(P|N)(_SRC)?$', nm)
        if not m or m.group(1) != kind:
            continue
        _, lane, pol, src = m.groups()
        out[lane][(pol, bool(src))] = p
    return out

for kind in ("CSI", "DSI"):
    print("\n" + "=" * 78)
    print("═══ %s 各 lane 的 P/N 位置 (官方板, 机器读) ═══" % kind)
    print("=" * 78)
    lanes = lane_nets(kind)
    for lane in sorted(lanes):
        d = lanes[lane]
        print("\n── %s_%s ──" % (kind, lane))
        for src in (True, False):
            P = d.get(("P", src)); N = d.get(("N", src))
            tag = "_SRC" if src else "    "
            ps = ("%s.%s @(%.2f,%.2f)" % (P["ref"], P["pad"], P["x"], P["y"])) if P else "★缺"
            ns = ("%s.%s @(%.2f,%.2f)" % (N["ref"], N["pad"], N["x"], N["y"])) if N else "★缺"
            if P and N:
                order = "P在左" if P["x"] < N["x"] else ("N在左" if N["x"] < P["x"] else "同点")
                order = ("★P在左" if P["x"] < N["x"] else "★N在左") + "  dx=%.2fmm" % abs(P["x"] - N["x"])
            else:
                order = "★有一侧无焊盘"
            print("  %-4s P=%-34s N=%-34s %s" % (tag, ps, ns, order))

print("\n" + "=" * 78)
print("═══ 结论辅助: 各中途器件的两脚 P/N 端位置 ═══")
print("=" * 78)
for f in b.GetFootprints():
    ref = f.GetReference()
    if not (ref.startswith("C_AC_CSI") or ref.startswith("R_SEL")):
        continue
    items = []
    for p in f.Pads():
        pos = p.GetPosition()
        items.append((p.GetNumber(), p.GetNetname(), pos.x / 1e6, pos.y / 1e6))
    items.sort(key=lambda t: t[2])
    if len(items) == 2:
        a, bb = items
        ord_ = "P在左" if a[1].endswith("_P") or "_P" in a[1] else "?"
        print("  %-16s %-22s @(%.2f,%.2f)   %-22s @(%.2f,%.2f)" %
              (ref, a[1], a[2], a[3], bb[1], bb[2], bb[3]))
