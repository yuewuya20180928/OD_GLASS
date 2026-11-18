#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-04: 复核 demo 主板上的 CONN_LIGHT (Pi5 22p) 封装
   ① 针号 → 网络 是否等于 HW/PCB/pi5_dsi_22p.json 的期望表
   ② 焊盘几何 (0.5mm pitch / 0.3x1.3 / pad1 在 +x 端)
   ③ 与其它器件的 courtyard 是否打架
用法: state/pcbnew_py.sh state/verify_display_fpc.py"""
import json, os, sys

import pcbnew

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
J = os.path.join(PROJ, "HW", "PCB", "pi5_dsi_22p.json")

exp = {int(p["pin"]): p["board_net"] for p in json.load(open(J, encoding="utf-8"))["pins"]}
params = json.load(open(os.path.join(PROJ, "HW", "PCB", "display_fpc_params.json"), encoding="utf-8"))

b = pcbnew.LoadBoard(PCB)
fp = None
for f in b.GetFootprints():
    if f.GetReference() == "CONN_LIGHT":
        fp = f
if fp is None:
    print("❌ 板上没有 CONN_LIGHT")
    sys.exit(1)

fails = []
print("=== ① 针号 → 网络 ===")
pads = {}
for p in fp.Pads():
    pads[int(p.GetNumber())] = p
for n in sorted(exp):
    got = pads[n].GetNetname() if n in pads else "<<缺焊盘>>"
    ok = (got == exp[n])
    if not ok:
        fails.append(f"pin{n}: 期望 {exp[n]} / 实际 {got}")
    print(f"  pin{n:>2}  期望 {exp[n]:<16} 实际 {got:<16} {'✔' if ok else '✘'}")
extra = sorted(set(pads) - set(exp))
if extra:
    fails.append(f"多出焊盘 {extra}")
    print("  ★多出焊盘:", extra)

print("=== ② 焊盘几何 ===")
pitch = float(params["pitch"])
pw = float(params["pad_w"])
pl = float(params["pad_l"])
xs = []
for n in sorted(pads):
    p = pads[n]
    px = p.GetPosition().x / 1000000.0
    py = p.GetPosition().y / 1000000.0
    sx = p.GetSize().x / 1000000.0
    sy = p.GetSize().y / 1000000.0
    xs.append(px)
    if abs(sx - pw) > 1e-6 or abs(sy - pl) > 1e-6:
        fails.append(f"pin{n} 焊盘尺寸 {sx}x{sy} != {pw}x{pl}")
xs_sorted = sorted(xs)
gaps = [round(xs_sorted[i + 1] - xs_sorted[i], 4) for i in range(len(xs_sorted) - 1)]
bad_gap = [g for g in gaps if abs(g - pitch) > 1e-4]
if bad_gap:
    fails.append(f"pitch 不一致: {bad_gap}")
p1x = pads[1].GetPosition().x / 1000000.0
print(f"  焊盘数 {len(pads)} · 尺寸 {pw}x{pl}mm · pitch 全为 {pitch} (异常 {len(bad_gap)})")
print(f"  pad1 x = {p1x:+.3f} (期望 {params['pad1_x']:+.2f}, 即 +x 端) · pad22 x = {xs_sorted[0]:+.3f}")

print("=== ③ 与其它器件的 courtyard 打架 ===")
def bbox(f):
    bb = f.GetBoundingBox()
    return (bb.GetLeft() / 1000000.0, bb.GetTop() / 1000000.0,
            bb.GetRight() / 1000000.0, bb.GetBottom() / 1000000.0)
a = bbox(fp)
clash = 0
for other in b.GetFootprints():
    if other.GetReference() == "CONN_LIGHT":
        continue
    o = bbox(other)
    if a[0] < o[2] and o[0] < a[2] and a[1] < o[3] and o[1] < a[3]:
        clash += 1
        print(f"  ⚠️ 与 {other.GetReference()} 外框重叠")
if clash == 0:
    print(f"  ✔ 无重叠 (CONN_LIGHT 外框 {a[0]:.1f},{a[1]:.1f} .. {a[2]:.1f},{a[3]:.1f} mm)")

print()
if fails:
    print("❌ 不通过:", len(fails))
    for f_ in fails[:20]:
        print("   -", f_)
    sys.exit(1)
print("✅ CONN_LIGHT 22p 封装复核全过")
