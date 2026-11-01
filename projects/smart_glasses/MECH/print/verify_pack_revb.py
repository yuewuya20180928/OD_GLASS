#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rev B 打印包模型自检 (光线投射实测 STL 网格) —— verify_pack_revb.py
================================================================================
对 Rev B 的 3 个 STL 做 **光线投射实测**, 与标称值对表。

⚠️ 口径 (与 verify_pack.py 一致, 不许误读):
  本脚本量的是 **模型网格几何真值**, 证明 "Rev B 的数字被正确实体化成几何了";
  它 **不能** 替代 M-PRINT (实物打印件实测尺寸) —— 实物还有 FDM 工艺偏差
  (孔径收缩 / 层纹 / 收缩率 / PA-CF 吸湿 24h 后尺寸变化)。
  ⇒ `state/measurements.yaml` 的 M-PRINT 仍为 [推算]/未测, 阶段门 G2 不认 (符合设计意图)。

Rev B 相对 Rev A 的判据变化 (5 条):
  ① PCB 样板 60×30 (原 12mm 宽口径作废)
  ② PCB 定位孔组 → PIN-SET-2 四孔 (P1/P2 ⌀2.4 让过 + S1/S2 ⌀1.6 让过), 孔距 44.00 (原 40.00)
  ③ 新增 ISS-092 检修口组: 通窗 10.20×4.60 / 螺钉凸台 ⌀3.20 / 磁铁沉槽 ⌀4.0 / 定位凸台 ⌀1.60 / 盖板 13.20×7.60×1.20 / 内腔量规 4.90
  ④ 新增板厚三档试样 0.41 / 0.80 / 1.22 (ISS-122 板厚区间兑现物)
  ⑤ Type-C 面板试样从镜脚检具 **移到镜框端件** (ISS-014 决策 5), 两档开口并行

用法: python3 MECH/print/verify_pack_revb.py
退出码: 0 = 模型与标称一致; 1 = 有偏差
"""
from __future__ import annotations

import math
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from gen_print_pack_revb import (GAPS, OVERHANGS, P, WALLS,  # noqa: E402
                                 build_coupon, build_frame_typec, build_temple_cage, v)


# ---------------------------------------------------------------- STL 读取
def load_stl(path):
    with open(path, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        raw = np.frombuffer(f.read(n * 50), dtype=np.uint8).reshape(n, 50)
        fl = raw[:, :48].copy().view(np.float32).reshape(n, 4, 3).astype(np.float64)
    return fl


# ---------------------------------------------------------------- 光线投射
def ray_hits(tris, origin, direction, tmin=1e-7):
    v0, v1, v2 = tris[:, 1, :], tris[:, 2, :], tris[:, 3, :]
    e1, e2 = v1 - v0, v2 - v0
    d = np.asarray(direction, dtype=float)
    h = np.cross(np.broadcast_to(d, e2.shape), e2)
    a = np.einsum("ij,ij->i", e1, h)
    ok = np.abs(a) > 1e-14
    f = np.zeros_like(a)
    f[ok] = 1.0 / a[ok]
    s = np.asarray(origin, dtype=float) - v0
    u = f * np.einsum("ij,ij->i", s, h)
    q = np.cross(s, e1)
    vv = f * np.einsum("j,ij->i", d, q)
    t = f * np.einsum("ij,ij->i", e2, q)
    hit = ok & (u >= -1e-9) & (vv >= -1e-9) & (u + vv <= 1 + 1e-9) & (t > tmin)
    ts = np.sort(t[hit])
    out = []
    for x in ts:
        if not out or x - out[-1] > 1e-6:
            out.append(float(x))
    return np.array(out)


def intervals(hits):
    return [(float(hits[i]), float(hits[i + 1])) for i in range(0, len(hits) - 1, 2)]


def gaps(iv):
    return [(iv[i][1], iv[i + 1][0]) for i in range(len(iv) - 1)]


def nearest(items, pos):
    if not items:
        return None
    return min(items, key=lambda g: abs((g[0] + g[1]) / 2 - pos))


class Probe:
    def __init__(self, part, item, nominal, unit, measured, tol=0.01, note=""):
        self.part, self.item, self.nominal = part, item, nominal
        self.unit, self.measured, self.tol, self.note = unit, measured, tol, note

    @property
    def ok(self):
        return self.measured is not None and abs(self.measured - self.nominal) <= self.tol

    @property
    def delta(self):
        return None if self.measured is None else self.measured - self.nominal


def build_probes():
    out = []
    coupon = load_stl(os.path.join(HERE, "fit_coupon_revb.stl"))
    cage = load_stl(os.path.join(HERE, "temple_cage_revb.stl"))
    ftc = load_stl(os.path.join(HERE, "frame_typec_coupon_revb.stl"))

    # ================= fit_coupon: Rev A 特征 (1)~(7) 保留 =================
    for i, t in enumerate(WALLS):
        x = 4 + i * 9 + 3.1
        iv = intervals(ray_hits(coupon, (x, 0.0, 8.0), (0, 1, 0)))
        meas = (iv[0][1] - iv[0][0]) if iv else None
        out.append(Probe("fit_coupon", f"壁厚阶梯 #{i+1}", t, "mm", meas, 0.005,
                         "沿 +Y 量实体段"))

    OX = 50.0
    g_all = gaps(intervals(ray_hits(coupon, (OX, 10.0, 8.0), (1, 0, 0))))
    x = 52.0
    for i, g in enumerate(GAPS):
        gg = nearest(g_all, (x + 3.0 + g / 2) - OX)
        meas = (gg[1] - gg[0]) if gg else None
        out.append(Probe("fit_coupon", f"间隙梳 #{i+1}", g, "mm", meas, 0.005, "沿 +X 量空腔"))
        x += 3.0 + g

    hits = ray_hits(coupon, (0.0, 26.0, 8.0), (1, 0, 0))
    g_all = gaps(intervals(hits))
    for cx, nom, name in ((20.0, v("hole_m12"), "M1.2 螺钉柱 ⌀2.4 未开槽"),
                          (30.0, v("hole_m12") + v("split_slot"), "⌀2.4 沿Z开槽 (含0.6槽)"),
                          (40.0, v("hole_m12"), "⌀3.0 螺钉柱"),
                          (50.0, v("dowel_h7"), "⌀4.0 定位销柱 ⌀2.0")):
        gg = nearest(g_all, cx)
        meas = (gg[1] - gg[0]) if gg else None
        out.append(Probe("fit_coupon", f"螺钉柱孔 {name}", nom, "mm", meas, 0.02, "沿 +X 量柱内空腔"))

    hits = ray_hits(coupon, (0.0, 40.0, 8.0), (1, 0, 0))
    g_all = gaps(intervals(hits))
    for cx, d in ((10.0, 2.0), (18.0, 2.1), (26.0, 2.2), (34.0, 2.4), (42.0, 2.5)):
        gg = nearest(g_all, cx)
        meas = (gg[1] - gg[0]) if gg else None
        out.append(Probe("fit_coupon", f"配作孔试样 ⌀{d}", d, "mm", meas, 0.01, "沿 +X 量孔"))

    for i, ang in enumerate(OVERHANGS):
        x0 = 62 + i * 17
        a = math.radians(ang)
        dz = 16.0 * math.sin(a)
        z1, z2 = 2.0 + 0.3 * dz, 2.0 + 0.7 * dz
        h1 = ray_hits(coupon, (x0 - 2.0, 36.0, z1), (1, 0, 0))
        h2 = ray_hits(coupon, (x0 - 2.0, 36.0, z2), (1, 0, 0))
        if len(h1) and len(h2):
            x1 = x0 - 2.0 + float(h1[0])
            x2 = x0 - 2.0 + float(h2[0])
            meas = math.degrees(math.atan2(abs(z2 - z1), abs(x2 - x1)))
        else:
            meas = None
        out.append(Probe("fit_coupon", f"悬空试样 {ang}° 下表面斜角", float(ang), "deg",
                         meas, 0.5, "两点拟合"))

    for x, nom, name in ((122.0, 5.0, "5mm"), (127.0, 10.0, "10mm"), (132.0, 20.0, "20mm")):
        h = ray_hits(coupon, (x, 70.0, 1e3), (0, 0, -1))
        meas = (1e3 - float(h[0]) - 2.0) if len(h) else None
        out.append(Probe("fit_coupon", f"标定块 {name}", nom, "mm", meas, 0.01, "自 +Z 向下量"))

    x = 6.0
    for g in (0.10, 0.12, 0.15):
        gg = gaps(intervals(ray_hits(coupon, (x + 4.0, 60.0, 4.0), (0, 1, 0))))
        meas = (gg[0][1] - gg[0][0]) if gg else None
        out.append(Probe("fit_coupon", f"波导卡槽单边间隙 {g:.2f}", g, "mm", meas, 0.005, "沿 +Y 量槽"))
        x += 14

    # ================= Rev B 新增 (8) PCB 样板 60×30 + PIN-SET-2 =================
    px0, py0 = 4.0, 4.0
    # 板长 (沿 +X, 避开孔)
    h = ray_hits(coupon, (0.0, py0 + 1.0, 2.4), (1, 0, 0))
    meas = None
    if len(h):
        meas = float(h[0]) - px0
    out.append(Probe("fit_coupon", "PCB 样板长 (Rev B 60mm)", v("pcb_len"), "mm", meas, 0.01,
                     "沿 +X 自板边量到板端"))
    # 板宽 (沿 +Y)
    gg = gaps(intervals(ray_hits(coupon, (px0 + 1.0, 0.0, 2.4), (0, 1, 0))))
    meas = (gg[0][1] - gg[0][0]) if gg else None
    out.append(Probe("fit_coupon", "PCB 样板宽 (Rev B 30mm, V 向)", v("pcb_wid"), "mm", meas, 0.01,
                     "沿 +Y 量板宽 —— ★板宽 30 是 V 向尺寸"))
    # 板厚 (沿 +Z)
    h = ray_hits(coupon, (px0 + 1.0, py0 + 1.0, 5.0), (0, 0, -1))
    meas = (float(h[0]) - 2.0) if len(h) else None
    out.append(Probe("fit_coupon", "PCB 样板厚 (0.80 档)", v("pcb_thk"), "mm", meas, 0.01,
                     "沿 +Z 量样板厚"))
    # PIN-SET-2 四孔: 位置 + 孔径
    for bx, by, dia, name in (
            (v("pinset2_p1_x"), v("pinset2_p_y"), v("clr_hole"), "P1 销孔让过"),
            (v("pinset2_p2_x"), v("pinset2_p_y"), v("clr_hole"), "P2 销孔让过"),
            (v("pinset2_s1_x"), v("pinset2_s1_y"), v("screw_clr"), "S1 压紧孔让过"),
            (v("pinset2_s2_x"), v("pinset2_s2_y"), v("screw_clr"), "S2 压紧孔让过")):
        cx, cy = px0 + bx, py0 + by
        # 孔径: 沿 +X 过孔心
        g_all = gaps(intervals(ray_hits(coupon, (0.0, cy, 2.4), (1, 0, 0))))
        gg = nearest(g_all, cx)
        meas = (gg[1] - gg[0]) if gg else None
        out.append(Probe("fit_coupon", f"PIN-SET-2 {name} ⌀{dia}", dia, "mm", meas, 0.01,
                         "沿 +X 过孔心量孔径"))
        # 孔心 X: 沿 +Y 过孔心找空腔中点
        g_all2 = gaps(intervals(ray_hits(coupon, (cx, 0.0, 2.4), (0, 1, 0))))
        gg2 = nearest(g_all2, cy)
        meas_x = ((gg2[0] + gg2[1]) / 2 - px0) if gg2 else None
        out.append(Probe("fit_coupon", f"PIN-SET-2 {name} 板坐标 X", bx, "mm", meas_x, 0.01,
                         "沿 +Y 量空腔中点 → 板坐标 X"))
    # P1↔P2 孔距 (Rev A 40.00 → Rev B 44.00)
    g_all = gaps(intervals(ray_hits(coupon, (0.0, py0 + v("pinset2_p_y"), 2.4), (1, 0, 0))))
    p1 = nearest(g_all, px0 + v("pinset2_p1_x"))
    p2 = nearest(g_all, px0 + v("pinset2_p2_x"))
    meas = (p2[0] - p1[1]) if (p1 and p2) else None
    out.append(Probe("fit_coupon", "PIN-SET-2 P1↔P2 孔距 (Rev A 40.00 → 44.00)",
                     v("pinset2_p2_x") - v("pinset2_p1_x"), "mm", meas, 0.01,
                     "沿 +X 量两孔净距"))

    # ================= Rev B 新增 (9) ISS-092 检修口组 =================
    cx0, cy0 = 70.0, 4.0
    # 盖板外形 X / Y / 厚
    h = ray_hits(coupon, (0.0, cy0 + 1.0, 3.0), (1, 0, 0))
    meas = (float(h[0]) - cx0) if len(h) else None
    out.append(Probe("fit_coupon", "ISS-092 盖板外形 X", v("sp_cover_x"), "mm", meas, 0.01,
                     "沿 +X 量盖板"))
    gg = gaps(intervals(ray_hits(coupon, (cx0 + 1.0, 0.0, 3.0), (0, 1, 0))))
    meas = (gg[0][1] - gg[0][0]) if gg else None
    out.append(Probe("fit_coupon", "ISS-092 盖板外形 Y", v("sp_cover_y"), "mm", meas, 0.01, "沿 +Y"))
    h = ray_hits(coupon, (cx0 + 1.0, cy0 + 1.0, 5.0), (0, 0, -1))
    meas = (float(h[0]) - 2.0) if len(h) else None
    out.append(Probe("fit_coupon", "ISS-092 盖板厚", v("sp_cover_t"), "mm", meas, 0.01, "沿 +Z"))
    # 磁吸沉槽 ⌀4.0
    mcx = cx0 + 3.0 + v("sp_mag_dia") / 2
    g_all = gaps(intervals(ray_hits(coupon, (0.0, cy0 + v("sp_cover_y") / 2, 3.0), (1, 0, 0))))
    gg = nearest(g_all, mcx)
    meas = (gg[1] - gg[0]) if gg else None
    out.append(Probe("fit_coupon", "ISS-092 盖板磁吸沉槽 ⌀4.0", v("sp_mag_dia"), "mm", meas, 0.01,
                     "沿 +X 量 N35 磁铁沉槽"))
    # 盖板定位孔 ⌀1.70
    ph = cx0 + (v("sp_cover_x") - v("sp_pin_pitch")) / 2
    g_all = gaps(intervals(ray_hits(coupon, (0.0, cy0 + 1.6, 3.0), (1, 0, 0))))
    gg = nearest(g_all, ph)
    meas = (gg[1] - gg[0]) if gg else None
    out.append(Probe("fit_coupon", "ISS-092 盖板定位孔 ⌀1.70", v("sp_pin_hole"), "mm", meas, 0.01,
                     "沿 +X 量 ⌀1.70 对位孔"))
    # 内腔量规深度 4.90 (自量规底面往上量)
    gx0, gy0 = 86.0, 4.0
    h = ray_hits(coupon, (gx0 + 10.0, gy0 + 6.0, 20.0), (0, 0, -1))
    meas = None
    if len(h):
        hits_down = h
        # 底面 z=2.0+1.2=3.2, 内腔侧壁顶 = 3.2+4.90
        meas = float(hits_down[0]) - 3.2
    out.append(Probe("fit_coupon", "ISS-092 盖板内腔量规深度 (C-5 4.90)", v("sp_cavity"), "mm",
                     meas, 0.01, "自量规底面量到内腔顶"))

    # ================= Rev B 新增 (10) M1.6 自攻底孔试样 =================
    g_all = gaps(intervals(ray_hits(coupon, (0.0, 8.0, 8.0), (1, 0, 0))))
    for cx, d in ((122.0, 1.2), (130.0, 1.3), (138.0, 1.4)):
        gg = nearest(g_all, cx)
        meas = (gg[1] - gg[0]) if gg else None
        out.append(Probe("fit_coupon", f"M1.6 自攻底孔试样 ⌀{d}", d, "mm", meas, 0.01,
                         "沿 +X 量底孔 (M1.6 扭矩/拉脱待实测)"))

    # ================= Rev B 新增 (11) V 向装配试样 (板宽 30) =================
    ax, az = 4.0, 40.0
    gg = gaps(intervals(ray_hits(coupon, (ax + 2.0, 0.0, 3.0), (0, 1, 0))))
    meas = (gg[0][1] - gg[0][0]) if gg else None
    out.append(Probe("fit_coupon", "V 向装配试样 板宽 30 (V 30mm)",
                     v("pcb_wid"), "mm", meas, 0.01, "沿 +Y 量板 (V 30 = 板宽 30 的兑现)"))

    # ================= temple_cage: 电池座 + PCB 定位组 + 检修口壁 =================
    clr = v("clr_metal")
    h = ray_hits(cage, (0.0, 3.5, 12.0), (1, 0, 0))
    meas = float(h[0]) if len(h) else None
    out.append(Probe("temple_cage", "电池槽长度", v("batt_l") + 2 * clr, "mm", meas, 0.01,
                     "沿 +X 自槽口打到端挡"))
    h = ray_hits(cage, (20.0, 3.5, -5.0), (0, 0, 1))
    meas = (float(h[2]) - float(h[1])) if len(h) >= 3 else None
    out.append(Probe("temple_cage", "电池槽高度", v("batt_v") + 2 * clr, "mm", meas, 0.01, "沿 +Z"))

    # 电池座净厚 (Rev A 口径, 沿 +Y @ Z=24.0)
    gg = gaps(intervals(ray_hits(cage, (20.0, -5.0, 24.0), (0, 1, 0))))
    seat_meas = (gg[0][1] - gg[0][0]) if gg else None
    out.append(Probe("temple_cage", "电池座净厚 (Rev A 非对称 4.75)", v("batt_seat"), "mm",
                     seat_meas, 0.005, "沿 +Y @ Z=24.0 (避开压垫槽)"))
    # 压垫槽深
    gg_g = gaps(intervals(ray_hits(cage, (20.0, -5.0, 12.0), (0, 1, 0))))
    inner = (gg_g[0][1] - gg_g[0][0]) if gg_g else None
    groove = None if (seat_meas is None or inner is None) else (inner - seat_meas)
    out.append(Probe("temple_cage", "顶板压垫槽深 (Rev A 0.40)", v("pad_groove"), "mm",
                     groove, 0.005, "槽内净厚 − 槽外净厚"))
    # 顶板厚
    h_p = ray_hits(cage, (20.0, 5.0, 24.0), (0, 1, 0))
    meas = (float(h_p[-1]) - float(h_p[0])) if len(h_p) >= 2 else None
    out.append(Probe("temple_cage", "电池段顶板厚 (Rev A 0.80)", v("top_plate"), "mm",
                     meas, 0.005, "空腔内首末命中差"))

    # PIN-SET-2 四孔 (检具内)
    by0 = 60.0
    for bx, by, dia, name in (
            (v("pinset2_p1_x"), v("pinset2_p_y"), v("clr_hole"), "P1 销孔让过 ⌀2.4"),
            (v("pinset2_p2_x"), v("pinset2_p_y"), v("clr_hole"), "P2 销孔让过 ⌀2.4"),
            (v("pinset2_s1_x"), v("pinset2_s1_y"), v("screw_clr"), "S1 压紧孔让过 ⌀1.6"),
            (v("pinset2_s2_x"), v("pinset2_s2_y"), v("screw_clr"), "S2 压紧孔让过 ⌀1.6")):
        g_all = gaps(intervals(ray_hits(cage, (0.0, by0 + by, 10.0), (1, 0, 0))))
        gg = nearest(g_all, bx)
        meas = (gg[1] - gg[0]) if gg else None
        out.append(Probe("temple_cage", f"PIN-SET-2 {name}", dia, "mm", meas, 0.01, "沿 +X 量孔"))
    # 板厚三档试样
    for i, t in enumerate((0.41, 0.80, 1.22)):
        y = by0 + 20.0 + i * 6.0 + 2.0
        h = ray_hits(cage, (5.0, y, 10.0), (0, 0, -1))
        meas = (float(h[0]) - 2.0) if len(h) else None
        out.append(Probe("temple_cage", f"板厚试样 {t:.2f}mm (ISS-122 区间)", t, "mm",
                         meas, 0.005, "沿 +Z 量厚度档"))
    # 走线槽 6×2
    gg = gaps(intervals(ray_hits(cage, (30.0, 95.0, 3.0), (0, 1, 0))))
    meas = (gg[0][1] - gg[0][0]) if gg else None
    out.append(Probe("temple_cage", "走线槽宽", v("duct_w"), "mm", meas, 0.01, "沿 +Y"))
    h_wall = ray_hits(cage, (30.0, 100.5, -5.0), (0, 0, 1))
    h_floor = ray_hits(cage, (30.0, 104.0, -5.0), (0, 0, 1))
    meas = None
    if len(h_wall) >= 2 and len(h_floor) >= 2:
        meas = (float(h_wall[-1]) - float(h_floor[-1]))
    out.append(Probe("temple_cage", "走线槽高", v("duct_h"), "mm", meas, 0.01, "槽壁总高−槽底厚"))

    # ISS-092 检修口壁: 通窗 10.20 × 4.60
    dy0 = 110.0
    gg = gaps(intervals(ray_hits(cage, (0.0, dy0 + 0.4, 10.3), (1, 0, 0))))
    meas = (gg[0][1] - gg[0][0]) if gg else None
    out.append(Probe("temple_cage", "ISS-092 通窗开口 X", v("sp_open_x"), "mm", meas, 0.01,
                     "沿 +X 过通窗中心量开口"))
    # 通窗高 (沿 +Z)
    gg = gaps(intervals(ray_hits(cage, (11.1, dy0 + 0.4, 0.0), (0, 0, 1))))
    meas = (gg[0][1] - gg[0][0]) if gg else None
    out.append(Probe("temple_cage", "ISS-092 通窗开口 Y (高)", v("sp_open_y"), "mm", meas, 0.01,
                     "沿 +Z 过通窗中心量开口"))
    # 螺钉凸台 ⌀3.20 (沿 +Z 过心量直径 → 用 +X 侧向量)
    gg = gaps(intervals(ray_hits(cage, (0.0, dy0 + 1.4, 10.3), (1, 0, 0))))
    meas = (gg[0][1] - gg[0][0]) if gg else None
    out.append(Probe("temple_cage", "ISS-092 螺钉凸台 ⌀3.20", v("sp_boss_dia"), "mm", meas, 0.01,
                     "沿 +X 过凸台中心"))
    # 定位凸台 ⌀1.60
    gg = gaps(intervals(ray_hits(cage, (0.0, dy0 + 0.4, 10.3), (1, 0, 0))))
    cands = [(g[0] + g[1]) / 2 for g in gg]
    tgt = 10.0
    gg2 = min(gg, key=lambda g: abs((g[0] + g[1]) / 2 - tgt)) if gg else None
    meas = (gg2[1] - gg2[0]) if gg2 else None
    out.append(Probe("temple_cage", "ISS-092 定位凸台 ⌀1.60", v("sp_pin_dia"), "mm", meas, 0.01,
                     "沿 +X 过定位凸台中心"))
    # 定位凸台间距 6.00
    mids = sorted((g[0] + g[1]) / 2 for g in gg)
    meas = None
    for i in range(len(mids) - 1):
        if abs(mids[i + 1] - mids[i] - v("sp_pin_pitch")) < 0.5:
            meas = mids[i + 1] - mids[i]
            break
    out.append(Probe("temple_cage", "ISS-092 定位凸台间距", v("sp_pin_pitch"), "mm", meas, 0.02,
                     "沿 +X 量两凸台中点距"))

    # ================= frame_typec_coupon =================
    for (ox0, ow, oh, name) in ((0.0, v("tc_open_w"), v("tc_open_h"), "现口径"),
                                (20.0, v("tc_open_w2"), v("tc_open_h2"), "ISS-089 建议口径")):
        gg = gaps(intervals(ray_hits(ftc, (0.0, 1.5, 0.0), (1, 0, 0))))
        # 在 x 方向上量开口: 用沿 +Y 在开口高度中心
        gg = gaps(intervals(ray_hits(ftc, (ox0 - 5.0, 6.5, 1.5), (1, 0, 0))))
        meas = (gg[0][1] - gg[0][0]) if gg else None
        out.append(Probe("frame_typec", f"Type-C 开口宽 ({name})", ow, "mm", meas, 0.01,
                         "沿 +X 量开口宽"))
        gg = gaps(intervals(ray_hits(ftc, (ox0 + ow / 2, 6.5, -5.0), (0, 0, 1))))
        meas = (gg[0][1] - gg[0][0]) if gg else None
        out.append(Probe("frame_typec", f"Type-C 开口高 ({name})", oh, "mm", meas, 0.01,
                         "沿 +Z 量开口高"))
        gg = gaps(intervals(ray_hits(ftc, (ox0 - 5.0, 6.5, 1.5), (1, 0, 0))))
        meas = (gg[0][0] - (ox0 - 5.0)) if gg else None
        out.append(Probe("frame_typec", f"Type-C 承力壁厚 ({name})", v("tc_wall_min"), "mm",
                         meas, 0.01, "沿 +X 量左承力壁"))
    return out


def main():
    print("=" * 100)
    print("Rev B 打印包模型自检 (光线投射实测) —— ⚠️ 模型级, 不等于实物打印实测")
    print("=" * 100)
    probes = build_probes()
    ok = 0
    cur = None
    for p in probes:
        if p.part != cur:
            cur = p.part
            print(f"\n【{cur}】")
        m = "None" if p.measured is None else f"{p.measured:.3f}"
        d = "—" if p.delta is None else f"{p.delta:+.3f}"
        flag = "✅" if p.ok else ("⚠️ " if p.measured is not None else "❌")
        if p.ok:
            ok += 1
        print(f"  {flag} {p.item:<46} 标称 {p.nominal:>7.3f} {p.unit:<3} "
              f"实测 {m:>8} {p.unit:<3} Δ {d:>8}  {p.note}")
    print("\n" + "-" * 100)
    print(f"模型与标称一致: {ok}/{len(probes)}")
    if ok != len(probes):
        print("⚠️ 有偏差 —— STL 与 Rev B 判据不同步, 重新生成后再打")
    print("★ 口径: 上面是 **模型真值**。M-PRINT (实物打印件实测尺寸) 仍为 0 数据 ——")
    print("  必须实物打印 + 卡尺实测, 见 MECH/print/MEASURE_CHECKLIST.md")
    print("★ optical_cage_TEMPLATE.stl 本单未改 (走鹃Ⅱ 三维尺寸 u1 未到)")
    return 0 if ok == len(probes) else 1


if __name__ == "__main__":
    sys.exit(main())
