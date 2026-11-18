#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_footprint_geom.py —— ★自绘封装的独立小验算 (不跑整板, 30 秒)
   用法: bash state/pcbnew_py.sh state/check_footprint_geom.py
   ★为什么: 自绘封装最容易错在"坐标没加封装原点偏移" ⇒ 整板跑 13 分钟才发现太慢
   ⇒ 单独实例化封装到空板, 打印每个焊盘/孔的 x/y/size/net, 人工一眼核对
"""
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from usb_c_footprint import add_usb_c, PAD_ORDER, PITCH, PAD_LEN, W_NARROW  # noqa: E402

X, Y = 140.0, 5.25          # 与生成器里的 USB_C_X / USB_C_Y 一致
PINS = {"A1+A12+B1+B12": "GND", "A4+A9+B4+B9": "RAIL_DEMO_5V",
        "A6+B6": "NET_USB_D_P_TYPEC", "A7+B7": "NET_USB_D_N_TYPEC",
        "A5": "USB_CC1", "B5": "USB_CC2"}


def main():
    b = pcbnew.CreateEmptyBoard()
    netmap = {}
    for nm in set(PINS.values()):
        ni = pcbnew.NETINFO_ITEM(b, nm)
        b.Add(ni)
        netmap[nm] = ni
    fp = add_usb_c(b, netmap, PINS, X, Y)
    rows = []
    for p in fp.Pads():
        pos = p.GetPosition()
        rows.append((p.GetNumber(), pos.x / 1e6, pos.y / 1e6,
                     p.GetSize().x / 1e6, p.GetSize().y / 1e6, p.GetNetname()))
    sig = [r for r in rows if r[0]]
    holes = [r for r in rows if not r[0]]
    print(f"焊盘 {len(sig)} 个 + 壳体孔 {len(holes)} 个")
    for r in sorted(sig, key=lambda t: t[1]):
        print(f"  pad {r[0]:4s} x={r[1]:8.3f} y={r[2]:7.3f} size={r[3]:.2f}x{r[4]:.2f} net={r[5]}")
    for r in holes:
        print(f"  孔  Ø{r[3]:.2f} x={r[1]:8.3f} y={r[2]:7.3f}")
    xs = sorted(r[1] for r in sig)
    ys = sorted(set(r[2] for r in sig))
    ok = True
    if len(sig) != 16:
        print("❌ 焊盘数不对 (应 16)")
        ok = False
    if abs((xs[-1] - xs[0]) - 15 * PITCH) > 1e-6:
        print(f"❌ 焊盘行跨度不对: {xs[-1]-xs[0]:.3f} (应 {15*PITCH:.3f})")
        ok = False
    if abs(ys[0] - Y) > 1e-6:
        print(f"❌ ★焊盘 y 没加原点偏移: {ys[0]:.3f} (应 {Y:.3f})")
        ok = False
    for r in sig:
        if abs(r[3] - W_NARROW) > 1e-6 or abs(r[4] - PAD_LEN) > 1e-6:
            print(f"❌ 焊盘 {r[0]} 尺寸不对: {r[3]}x{r[4]}")
            ok = False
    print("✅ 几何全对" if ok else "❌ 有问题")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
