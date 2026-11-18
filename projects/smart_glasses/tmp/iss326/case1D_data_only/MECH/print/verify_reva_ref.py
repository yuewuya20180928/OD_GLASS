#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rev A 参考实现的**离线复核** (辅助脚本, 不属于交付物, 不写任何 STL)
=========================================================================
按 MECH/print/GEOM_SPEC_REVA.md §2 的参考实现在内存里搭出 Rev A 几何,
再用 verify_pack.py 的同一套光线投射去量, 看能不能量出 Rev A 标称值。

目的: 证明"规格里的参考实现"与"verify_pack.py 的判据"是**同一套数字** ——
      项目总工照 §2 实现 → 应转绿 46/46。
⚠️ 本脚本 **不写 .stl / 不改 gen_print_pack.py**, 只在内存里建模 + 量。
用法: python3 MECH/print/verify_reva_ref.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gen_print_pack import Mesh  # noqa: E402
from verify_pack import (REVA, gaps, intervals, nearest, ray_hits)  # noqa: E402


def build_temple_cage_reva():
    """严格照 GEOM_SPEC_REVA.md §2.3 / §2.4 写"""
    m = Mesh("temple_cage_340_REVA")
    clr = 0.15
    px = 40.5 + 2 * clr      # 40.80  座净长 (X)
    pz = 23.5 + 2 * clr      # 23.80  座净高 (Z)
    w = 2.0                  # 检具壁厚
    seat_y = REVA["batt_seat_depth"]      # 4.75
    skin_w = 0.80                          # F2
    plate_t = REVA["top_plate_thk"]        # 0.80
    groove = REVA["pad_groove_depth"]      # 0.40
    # 派生坐标 (§2.2)
    y_floor_in = skin_w                    # 0.80  座底面
    y_cell_top = skin_w + 4.60             # 5.40  电芯顶面
    y_plate_in = y_cell_top + 0.15         # 5.55  顶板内侧面
    y_plate_out = y_plate_in + plate_t     # 6.35  顶板外侧面
    y_groove_out = y_plate_in + groove     # 5.95  槽底 (板内)
    gz0, gz1 = 5.75, 21.75                 # 压垫槽 Z 范围

    # ---- A 段 (电池段) ----
    m.box(0, 0, 0, px + w, y_plate_out, w)                      # A1 槽底板
    m.box(0, 0, w, px, skin_w, w + pz)                           # A2 皮肤侧壁
    m.box(0, y_groove_out, w, px, y_plate_out, w + pz)           # A3 顶板基体
    m.box(0, y_plate_in, w, px, y_groove_out, gz0)              # A4 槽下边条
    m.box(0, y_plate_in, gz1, px, y_groove_out, w + pz)         # A5 槽上边条
    m.box(px, 0, 0, px + w, y_plate_out, w + pz + w)             # A6 端挡
    m.box(0, 0, w + pz, px + w, y_plate_out, w + pz + w)         # A7 顶盖

    # ---- B 段 (PCB 定位孔组) ----
    m.box(0, 60, 0, 50, 92, 2.0)                                # B1 底板 (扩到 X=50)
    m.tube_z(6, 68, 2.0, 18.0, 2.5, REVA["screw_clr"] / 2)     # B2 过孔 ⌀1.6 (X=6)
    m.tube_z(46, 68, 2.0, 18.0, 2.5, REVA["screw_clr"] / 2)    # B2 过孔 ⌀1.6 (X=46)
    m.tube_z(16, 68, 2.0, 18.0, 3.0, REVA["clr_hole"] / 2)      # B3 间隙孔 ⌀2.4
    m.tube_z(26, 68, 2.0, 18.0, 3.0, 2.1 / 2)                  # B4 试样 ⌀2.1
    m.tube_z(36, 68, 2.0, 18.0, 3.0, 2.2 / 2)                  # B5 试样 ⌀2.2
    m.box(0, 78, 2.0, 50.0, 90, 3.0)                           # B6 PCB 定位板

    # ---- C 段 (走线槽试样) — 照 Rev 0 不动 ----
    m.box(0, 100, 0, 60, 108, 2.0)
    m.box(0, 100, 0, 60, 101, 4.0)
    m.box(0, 107, 0, 60, 108, 4.0)
    # ---- D 段 (Type-C 面板试样) — 照 Rev 0 不动 ----
    ow, oh, tw = 9.5, 3.6, 1.5
    W, H = ow + 2 * tw, oh + 2 * tw
    m.box(0, 120, 0, tw, 123.0, H)
    m.box(ow + tw, 120, 0, W, 123.0, H)
    m.box(tw, 120, 0, ow + tw, 123.0, tw)
    m.box(tw, 120, oh + tw, ow + tw, 123.0, H)
    return m


def build_coupon_reva():
    """fit_coupon: 只改 F7 (配作孔试样加 ⌀2.4 / ⌀2.5), 其余照旧"""
    from gen_print_pack import GAPS, OVERHANGS, WALLS
    m = Mesh("fit_coupon_340_REVA")
    m.box(0, 0, 0, 150, 90, 2.0)
    for i, t in enumerate(WALLS):
        x0 = 4 + i * 9
        m.box(x0, 4, 2.0, x0 + 8, 4 + t, 14.0)
    x = 52.0
    for g in GAPS:
        m.box(x, 4, 2.0, x + 3.0, 16, 17.0)
        x += 3.0 + g
    m.box(x, 4, 2.0, x + 3.0, 16, 17.0)
    z0, z1 = 2.0, 14.0
    m.cyl_z(10, 26, z0, z1, 1.5)
    m.tube_z(20, 26, z0, z1, 1.2, 1.4 / 2)
    m.tube_z(30 - 0.3, 26, z0, z1, 1.2, 0.7, a0=90.0, a1=270.0)
    m.tube_z(30 + 0.3, 26, z0, z1, 1.2, 0.7, a0=270.0, a1=450.0)
    m.tube_z(40, 26, z0, z1, 1.5, 0.7)
    m.tube_z(50, 26, z0, z1, 2.0, 1.0)
    for i, d in enumerate((2.0, 2.1, 2.2, 2.4, 2.5)):          # F7
        m.tube_z(10 + i * 8, 40, z0, z1, 3.0, d / 2)
    for i, ang in enumerate(OVERHANGS):
        m.overhang(62 + i * 17, 30, 42, 2.0, 16.0, ang)
    m.box(120, 60, 2.0, 125, 80, 7.0)
    m.box(125, 60, 2.0, 130, 80, 12.0)
    m.box(130, 60, 2.0, 135, 80, 22.0)
    x = 6.0
    for g in (0.10, 0.12, 0.15):
        m.box(x, 66, 2.0, x + 8, 70, 6.0)
        m.box(x, 70 + g, 2.0, x + 8, 76, 6.0)
        x += 14
    return m


def tris_of(mesh):
    """转成 verify_pack.ray_hits 期望的 (n, 4, 3) 布局: [0]=法线占位, [1:4]=三个顶点"""
    import numpy as np
    arr = np.zeros((len(mesh.tris), 4, 3), dtype=float)
    for i, tri in enumerate(mesh.tris):
        arr[i, 1:, :] = np.asarray(tri, dtype=float)
    return arr


def main():
    cage = tris_of(build_temple_cage_reva())
    coupon = tris_of(build_coupon_reva())
    fails = 0

    def chk(name, meas, nom, tol=0.005):
        nonlocal fails
        ok = meas is not None and abs(meas - nom) <= tol
        if not ok:
            fails += 1
        print(f"  {'✅' if ok else '❌'} {name:<40} 标称 {nom:>7.3f}  实测 "
              f"{'None' if meas is None else f'{meas:.3f}':>8}  "
              f"Δ {'—' if meas is None else f'{meas - nom:+.3f}'}")

    print("【temple_cage_340 — Rev A 参考实现离线复核】")
    # 座净厚 (Z=24.0)
    iv = intervals(ray_hits(cage, (20.0, -5.0, REVA["seat_probe_z_plain"]), (0, 1, 0)))
    gg = gaps(iv)
    seat = (gg[0][1] - gg[0][0]) if gg else None
    chk("电池座净厚 (非对称)", seat, REVA["batt_seat_depth"])
    # 压垫槽深 (Z=12.0, 槽内) —— 槽是让位凹槽 ⇒ 槽内净厚更大
    iv_g = intervals(ray_hits(cage, (20.0, -5.0, REVA["seat_probe_z_groove"]), (0, 1, 0)))
    gg_g = gaps(iv_g)
    inner = (gg_g[0][1] - gg_g[0][0]) if gg_g else None
    chk("顶板压垫槽深", None if (seat is None or inner is None) else inner - seat,
        REVA["pad_groove_depth"])
    # 顶板厚 (从空腔内打首末命中差)
    h_p = ray_hits(cage, (20.0, 5.0, REVA["seat_probe_z_plain"]), (0, 1, 0))
    chk("电池段顶板厚", (float(h_p[-1]) - float(h_p[0])) if len(h_p) >= 2 else None,
        REVA["top_plate_thk"])
    # 座净长 / 净高
    h = ray_hits(cage, (0.0, 3.5, 12.0), (1, 0, 0))
    chk("电池槽长度 (X)", float(h[0]) if len(h) else None, 40.80, 0.01)
    h = ray_hits(cage, (20.0, 3.5, -5.0), (0, 0, 1))
    chk("电池槽高度 (Z)", (float(h[2]) - float(h[1])) if len(h) >= 3 else None, 23.80, 0.01)
    # PCB 孔组
    iv = intervals(ray_hits(cage, (0.0, 68.0, 10.0), (1, 0, 0)))
    g_all = gaps(iv)
    for cx, nom, name in ((6.0, 1.60, "M1.2 过孔 ⌀1.6 (X=6)"),
                          (16.0, 2.40, "定位间隙孔 ⌀2.4 (X=16)"),
                          (26.0, 2.10, "试样 ⌀2.1 (X=26)"),
                          (36.0, 2.20, "试样 ⌀2.2 (X=36)"),
                          (46.0, 1.60, "M1.2 过孔 ⌀1.6 (X=46)")):
        g = nearest(g_all, cx)
        chk(name, (g[1] - g[0]) if g else None, nom, 0.01)

    print("\n【fit_coupon_340 — Rev A 参考实现离线复核】")
    hits = ray_hits(coupon, (0.0, 40.0, 8.0), (1, 0, 0))
    g_all = gaps(intervals(hits))
    for cx, nom in ((10.0, 2.0), (18.0, 2.1), (26.0, 2.2), (34.0, 2.4), (42.0, 2.5)):
        g = nearest(g_all, cx)
        chk(f"配作孔试样 ⌀{nom}", (g[1] - g[0]) if g else None, nom, 0.01)

    lo_c, hi_c = build_coupon_reva().bounds()
    lo_t, hi_t = build_temple_cage_reva().bounds()
    print(f"\n包围盒  fit_coupon {hi_c[0]-lo_c[0]:.2f}×{hi_c[1]-lo_c[1]:.2f}×{hi_c[2]-lo_c[2]:.2f}  "
          f"(规格期望 150.00×90.00×22.00)")
    print(f"包围盒  temple_cage {hi_t[0]-lo_t[0]:.2f}×{hi_t[1]-lo_t[1]:.2f}×{hi_t[2]-lo_t[2]:.2f}  "
          f"(规格期望 60.00×123.00×27.80)")
    print(f"\n离线复核: {'全部一致 ✅' if fails == 0 else f'{fails} 项不一致 ❌'}")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
