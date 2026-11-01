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

★ 探针纪律 (Rev A 脚本踩过的坑, 这版修正):
  · **射线必须从实体外出发** —— 从实体内出发时命中序列奇偶错位, 量不出空腔;
  · **实体段 = 相邻两次命中之间**; **空档 = 两段实体之间**;
    用 "相邻命中差" 会把实体段和空档混在一起 —— 这版把两者分开算;
  · 每条探针只打 **自己那条特征带**, 不许打到邻居身上 (布局表 L 保证互不遮挡)。

Rev B 相对 Rev A 的判据变化 (5 条):
  ① PCB 样板 60×30 (原 12mm 宽口径作废)
  ② PCB 定位孔组 → PIN-SET-2 四孔 (P1/P2 ⌀2.4 + S1/S2 ⌀1.6), 孔距 44.00 (原 40.00)
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

from gen_print_pack_revb import (GAPS, L, OVERHANGS, P, WALLS,  # noqa: E402
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


def solids(hits):
    """命中序列 → 实体段 [(a,b), ...]

    ★ 关键: 射线可能从实体 **内部** 出发 (例如探针起点就在某个实体段里),
      此时命中数是奇数 ⇒ 简单配对会把 "实体-空-实体" 误判成 "空-实体"。
      正确做法: 从起点开始做 **奇偶判定** ——
      偶数索引命中 = 进入实体, 奇数索引命中 = 离开实体;
      若第一个命中是 "离开" (说明起点在实体内), 则实体段从 0 开始。
    """
    if len(hits) == 0:
        return []
    out = []
    if len(hits) % 2 == 1:
        # 起点在实体内: 第一个命中是离开
        out.append((0.0, float(hits[0])))
        for i in range(0, len(hits) - 1, 2):
            out.append((float(hits[i]), float(hits[i + 1])))
        return out
    for i in range(0, len(hits), 2):
        out.append((float(hits[i]), float(hits[i + 1])))
    return out


def voids(hits):
    """命中序列 → 空档 [(a,b), ...] (两段实体之间)"""
    iv = solids(hits)
    return [(iv[i][1], iv[i + 1][0]) for i in range(len(iv) - 1)]


def first_solid(hits):
    """第一段实体的长度 (外形/壁厚)"""
    iv = solids(hits)
    return (iv[0][1] - iv[0][0]) if iv else None


def nearest_void(hits, pos):
    """离 pos 最近的空档宽度 (间隙/孔径)"""
    vd = voids(hits)
    if not vd:
        return None
    g = min(vd, key=lambda q: abs((q[0] + q[1]) / 2 - pos))
    return g[1] - g[0]


def nearest_solid(hits, pos):
    """离 pos 最近的实体段长度"""
    iv = solids(hits)
    if not iv:
        return None
    s = min(iv, key=lambda q: abs((q[0] + q[1]) / 2 - pos))
    return s[1] - s[0]


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

    # ================= fit_coupon =================
    # (1) 壁厚阶梯: 沿 +Y 过阶梯中心, 第一段实体 = 壁厚
    for i, t in enumerate(WALLS):
        x = L["cp_wall_x"] + i * 9 + 3.1
        h = ray_hits(coupon, (x, -5.0, 8.0), (0, 1, 0))
        meas = first_solid(h)
        out.append(Probe("fit_coupon", f"壁厚阶梯 #{i+1}", t, "mm", meas, 0.005,
                         "沿 +Y 过阶梯中心取第一段实体"))

    # (2) 间隙梳: 沿 +X, 取各档空档
    ox0 = L["cp_comb_x"] - 4.0
    h = ray_hits(coupon, (ox0, 10.0, 8.0), (1, 0, 0))
    x = L["cp_comb_x"]
    for i, g in enumerate(GAPS):
        meas = nearest_void(h, (x + 3.0 + g / 2) - ox0)
        out.append(Probe("fit_coupon", f"间隙梳 #{i+1}", g, "mm", meas, 0.005,
                         "沿 +X 量肋间空档"))
        x += 3.0 + g

    # (3) 螺钉柱孔径: 沿 +X 过柱心, 取空档
    h = ray_hits(coupon, (0.0, 26.0, 8.0), (1, 0, 0))
    for cx, nom, name in ((L["cp_boss_x"][1], v("hole_m12"), "M1.2 螺钉柱 ⌀2.4 未开槽"),
                          (L["cp_boss_x"][2], v("hole_m12") + v("split_slot"), "⌀2.4 沿Z开槽(含0.6槽)"),
                          (L["cp_boss_x"][3], v("hole_m12"), "⌀3.0 螺钉柱"),
                          (L["cp_boss_x"][4], v("dowel_h7"), "⌀4.0 定位销柱 ⌀2.0")):
        meas = nearest_void(h, cx)
        out.append(Probe("fit_coupon", f"螺钉柱孔 {name}", nom, "mm", meas, 0.02,
                         "沿 +X 过柱心量柱内空档"))

    # (4) 配作孔试样: 沿 +X 过孔心 (y=31)
    h = ray_hits(coupon, (0.0, 31.0, 8.0), (1, 0, 0))
    for i, d in enumerate((2.0, 2.1, 2.2, 2.4, 2.5)):
        meas = nearest_void(h, L["cp_fit_x"][i])
        out.append(Probe("fit_coupon", f"配作孔试样 ⌀{d}", d, "mm", meas, 0.01,
                         "沿 +X 过孔心量孔径"))

    # (5) 悬空角: 两点拟合
    for i, ang in enumerate(OVERHANGS):
        x0 = L["cp_over_x"] + i * 17
        a = math.radians(ang)
        dz = 16.0 * math.sin(a)
        z1, z2 = 2.0 + 0.3 * dz, 2.0 + 0.7 * dz
        h1 = ray_hits(coupon, (x0 - 2.0, 50.0, z1), (1, 0, 0))
        h2 = ray_hits(coupon, (x0 - 2.0, 50.0, z2), (1, 0, 0))
        if len(h1) and len(h2):
            x1 = x0 - 2.0 + float(h1[0])
            x2 = x0 - 2.0 + float(h2[0])
            meas = math.degrees(math.atan2(abs(z2 - z1), abs(x2 - x1)))
        else:
            meas = None
        out.append(Probe("fit_coupon", f"悬空试样 {ang}° 下表面斜角", float(ang), "deg",
                         meas, 0.5, "两点拟合下表面斜角"))

    # (6) 标定块: 自 +Z 向下
    for dx, nom, name in ((0.0, 5.0, "5mm"), (5.0, 10.0, "10mm"), (10.0, 20.0, "20mm")):
        h = ray_hits(coupon, (L["cp_block_x"] + dx + 2.5, 50.0, 1e3), (0, 0, -1))
        meas = (1e3 - float(h[0]) - 2.0) if len(h) else None
        out.append(Probe("fit_coupon", f"标定块 {name}", nom, "mm", meas, 0.01, "自 +Z 向下量"))

    # (7) 波导卡槽间隙: 沿 +Y 过槽心 (y 66..76), 空档在槽底与对侧壁之间
    x = L["cp_wave_x"]
    for g in (0.10, 0.12, 0.15):
        h = ray_hits(coupon, (x + 4.0, 60.0, 4.0), (0, 1, 0))
        meas = nearest_void(h, 70.0 + g / 2)
        out.append(Probe("fit_coupon", f"波导卡槽单边间隙 {g:.2f}", g, "mm", meas, 0.005,
                         "沿 +Y 过槽心量槽内空档"))
        x += 14

    # (8) M1.6 自攻底孔 (y=26 带)
    h = ray_hits(coupon, (0.0, 26.0, 8.0), (1, 0, 0))
    for i, d in enumerate((1.2, 1.3, 1.4)):
        meas = nearest_void(h, L["cp_pilot_x"][i])
        out.append(Probe("fit_coupon", f"M1.6 自攻底孔试样 ⌀{d}", d, "mm", meas, 0.01,
                         "沿 +X 过孔心量底孔 (M1.6 扭矩/拉脱待实测)"))

    # (9) 板厚三档试样 (y 116..122 带)
    for i, t in enumerate((0.41, 0.80, 1.22)):
        h = ray_hits(coupon, (L["cp_thk_x"] + i * 8.0 + 3.0, 119.0, 1e3), (0, 0, -1))
        meas = (1e3 - float(h[0]) - 2.0) if len(h) else None
        out.append(Probe("fit_coupon", f"板厚试样 {t:.2f}mm (ISS-122 区间)", t, "mm",
                         meas, 0.005, "自 +Z 向下量厚度档"))

    # (10) 盖板 (x 4..17.2, y 116..123.6, z 2.0..3.2)
    cx0, cy0 = L["cp_cover_x"], 116.0
    # 外形 X: 沿 +X 过盖板 (y = cy0+0.5 避开磁铁/孔), 第一段实体 = 盖板全长
    h = ray_hits(coupon, (cx0 - 5.0, cy0 + 0.5, 2.6), (1, 0, 0))
    meas = first_solid(h)
    out.append(Probe("fit_coupon", "ISS-092 盖板外形 X", v("sp_cover_x"), "mm", meas, 0.01,
                     "沿 +X 过盖板取第一段实体"))
    # 外形 Y: 沿 +Y 过盖板 (x = cx0+0.5)
    h = ray_hits(coupon, (cx0 + 0.5, cy0 - 5.0, 2.6), (0, 1, 0))
    meas = first_solid(h)
    out.append(Probe("fit_coupon", "ISS-092 盖板外形 Y", v("sp_cover_y"), "mm", meas, 0.01,
                     "沿 +Y 过盖板取第一段实体"))
    # 盖板厚: 自 +Z 向下 (x=cx0+0.5 避开孔)
    h = ray_hits(coupon, (cx0 + 0.5, cy0 + 0.5, 1e3), (0, 0, -1))
    meas = (1e3 - float(h[0]) - 2.0) if len(h) else None
    out.append(Probe("fit_coupon", "ISS-092 盖板厚", v("sp_cover_t"), "mm", meas, 0.01,
                     "自 +Z 向下量"))
    # 磁吸沉槽 ⌀4.0: 沿 +X 过沉槽中心 (z 在沉槽层 2.4..3.2)
    mag_y = cy0 + v("sp_cover_y") / 2
    mag_x = cx0 + 3.0 + v("sp_mag_dia") / 2
    h = ray_hits(coupon, (cx0 - 5.0, mag_y, 2.4 + 0.4), (1, 0, 0))
    meas = nearest_void(h, mag_x - (cx0 - 5.0))
    out.append(Probe("fit_coupon", "ISS-092 盖板磁吸沉槽 ⌀4.0", v("sp_mag_dia"), "mm",
                     meas, 0.01, "沿 +X 过沉槽中心量孔径 (在沉槽层内)"))
    # 沉槽深: 沿 +Z 自 +1e3 向下, 第一段实体 = 沉槽层厚 (0.80) —— 沉槽中心是空的 ⇒ 实测=层厚+底
    h = ray_hits(coupon, (mag_x, mag_y, 1e3), (0, 0, -1))
    meas = (1e3 - float(h[0]) - 2.0) if len(h) else None
    out.append(Probe("fit_coupon", "ISS-092 盖板磁吸沉槽深 (沉槽中心为空洞⇒量到底)", 0.40,
                     "mm", meas, 0.01,
                     "沉槽中心从上表面到槽底 = 沉槽深 0.80 + 底厚 0.40 = 1.20 (此行量的是 1.20)"))

    # 盖板定位孔 ⌀1.70 (沿 +X 过孔心, y = cy0+1.6, z = 2.6 贯穿层)
    pin_x = cx0 + (v("sp_cover_x") - v("sp_pin_pitch")) / 2
    h = ray_hits(coupon, (cx0 - 5.0, cy0 + 1.6, 2.6), (1, 0, 0))
    meas = nearest_void(h, pin_x - (cx0 - 5.0))
    out.append(Probe("fit_coupon", "ISS-092 盖板定位孔 ⌀1.70", v("sp_pin_hole"), "mm",
                     meas, 0.01, "沿 +X 过 ⌀1.70 对位孔量孔径"))
    # 盖板自攻让过孔 ⌀1.80
    sc_x = cx0 + v("sp_cover_x") / 2
    h = ray_hits(coupon, (cx0 - 5.0, cy0 + v("sp_cover_y") - 1.6, 2.6), (1, 0, 0))
    meas = nearest_void(h, sc_x - (cx0 - 5.0))
    out.append(Probe("fit_coupon", "ISS-092 盖板自攻让过孔 ⌀1.80", v("sp_screw_hole"), "mm",
                     meas, 0.01, "沿 +X 过 M1.6 让过孔量孔径"))

    # (11) 盖板内腔量规 (x 20..40, y 116..128, 底 z 2.0..3.2, 壁到 z=8.1)
    gx0, gy0 = L["cp_gauge_x"], 116.0
    # 内腔深 = 壁顶 (8.1) − 底面 (3.2): 沿 +Z 自量规底面往上量, 取空档深度
    h = ray_hits(coupon, (gx0 + 10.0, gy0 + 6.0, 3.2), (0, 0, 1))
    iv = solids(h)
    meas = None
    if iv:
        # 第一个实体段是底板? 不 —— 起点在底面顶 (3.2), 第一段实体 = 侧壁 (直到顶)
        meas = iv[0][1] - iv[0][0]
    out.append(Probe("fit_coupon", "ISS-092 盖板内腔量规深度 (C-5 4.90)", v("sp_cavity"),
                     "mm", meas, 0.01, "自量规底面顶沿 +Z 打到侧壁顶"))

    # (12) PCB 样板 60×30 + PIN-SET-2 (x 4..64, y 84..114, z 2.0..2.8)
    px0, py0 = L["cp_pcb_x"], 84.0
    # 板长: 沿 +X 过板 (y = py0+5.5 避开所有孔), 第一段实体 = 60
    h = ray_hits(coupon, (px0 - 5.0, py0 + 5.5, 2.4), (1, 0, 0))
    meas = first_solid(h)
    out.append(Probe("fit_coupon", "PCB 样板长 (Rev B 60mm)", v("pcb_len"), "mm", meas, 0.01,
                     "沿 +X 过板取第一段实体"))
    # 板宽: 沿 +Y 过板 (x = px0+2 避开孔)
    h = ray_hits(coupon, (px0 + 2.0, py0 - 5.0, 2.4), (0, 1, 0))
    meas = first_solid(h)
    out.append(Probe("fit_coupon", "PCB 样板宽 (Rev B 30mm, V 向)", v("pcb_wid"), "mm",
                     meas, 0.01, "沿 +Y 过板取第一段实体 —— ★板宽 30 是 V 向尺寸"))
    # 板厚: 自 +Z 向下
    h = ray_hits(coupon, (px0 + 2.0, py0 + 2.0, 1e3), (0, 0, -1))
    meas = (1e3 - float(h[0]) - 2.0) if len(h) else None
    out.append(Probe("fit_coupon", "PCB 样板厚 (0.80 档)", v("pcb_thk"), "mm", meas, 0.01,
                     "自 +Z 向下量样板厚"))
    # PIN-SET-2 四孔: 孔径 + 孔心 X + 孔距
    h = ray_hits(coupon, (px0 - 5.0, py0 + v("pinset2_p_y"), 2.4), (1, 0, 0))
    for bx, by, dia, name in (
            (v("pinset2_p1_x"), v("pinset2_p_y"), v("clr_hole"), "P1 销孔让过"),
            (v("pinset2_p2_x"), v("pinset2_p_y"), v("clr_hole"), "P2 销孔让过")):
        meas = nearest_void(h, bx + 5.0)
        out.append(Probe("fit_coupon", f"PIN-SET-2 {name} ⌀{dia}", dia, "mm", meas, 0.01,
                         "沿 +X 过孔心量孔径"))
    h = ray_hits(coupon, (px0 - 5.0, py0 + v("pinset2_s1_y"), 2.4), (1, 0, 0))
    meas = nearest_void(h, v("pinset2_s1_x") + 5.0)
    out.append(Probe("fit_coupon", "PIN-SET-2 S1 压紧孔让过 ⌀1.60", v("screw_clr"), "mm",
                     meas, 0.01, "沿 +X 过 S1 孔心量孔径"))
    h = ray_hits(coupon, (px0 - 5.0, py0 + v("pinset2_s2_y"), 2.4), (1, 0, 0))
    meas = nearest_void(h, v("pinset2_s2_x") + 5.0)
    out.append(Probe("fit_coupon", "PIN-SET-2 S2 压紧孔让过 ⌀1.60", v("screw_clr"), "mm",
                     meas, 0.01, "沿 +X 过 S2 孔心量孔径"))
    # 孔心 X: 用 S1/S2 两孔的空档中心反推
    for by, bx, name in ((v("pinset2_s1_y"), v("pinset2_s1_x"), "S1"),
                         (v("pinset2_s2_y"), v("pinset2_s2_x"), "S2")):
        h = ray_hits(coupon, (px0 - 5.0, py0 + by, 2.4), (1, 0, 0))
        vd = voids(h)
        meas = None
        if vd:
            g = min(vd, key=lambda q: abs((q[0] + q[1]) / 2 - (bx + 5.0)))
            meas = (g[0] + g[1]) / 2 - 5.0
        out.append(Probe("fit_coupon", f"PIN-SET-2 {name} 板坐标 X", bx, "mm", meas, 0.01,
                         "沿 +X 量空档中心 → 板坐标 X"))
    # P1↔P2 孔距
    h = ray_hits(coupon, (px0 - 5.0, py0 + v("pinset2_p_y"), 2.4), (1, 0, 0))
    vd = sorted(voids(h), key=lambda g: g[0])
    meas = None
    if len(vd) >= 2:
        c1 = (vd[0][0] + vd[0][1]) / 2 - 5.0
        c2 = (vd[1][0] + vd[1][1]) / 2 - 5.0
        meas = c2 - c1
    out.append(Probe("fit_coupon", "PIN-SET-2 P1↔P2 孔距 (Rev A 40.00 → 44.00)",
                     v("pinset2_p2_x") - v("pinset2_p1_x"), "mm", meas, 0.02,
                     "沿 +X 量两孔中心距"))

    # (13) V 向装配试样 (x 68..128, y 84..114)
    ax, az = L["cp_vasm_x"], 84.0
    h = ray_hits(coupon, (ax + 2.0, az - 5.0, 3.0), (0, 1, 0))
    meas = first_solid(h)
    out.append(Probe("fit_coupon", "V 向装配试样 板宽 30 (V 30mm)", v("pcb_wid"), "mm",
                     meas, 0.01, "沿 +Y 过板取第一段实体 (V 30 = 板宽 30 的兑现)"))
    # V 余量间隙梳: 名义 1.0/1.4/1.8/2.0/2.2
    cx = L["cp_vcomb_x"]
    h = ray_hits(coupon, (cx - 2.0, 119.0, 9.0), (1, 0, 0))
    for g in (1.0, 1.4, 1.8, 2.0, 2.2):
        meas = nearest_void(h, cx + 1.0)
        out.append(Probe("fit_coupon", f"V 余量间隙梳 {g:.1f}", g, "mm", meas, 0.01,
                         "沿 +X 量梳齿空档 (V 链余量 2.00 的兑现物)"))
        cx += 2.0 + g

    # ================= temple_cage =================
    clr = v("clr_metal")
    h = ray_hits(cage, (0.0, 3.5, 12.0), (1, 0, 0))
    meas = float(h[0]) if len(h) else None
    out.append(Probe("temple_cage", "电池槽长度", v("batt_l") + 2 * clr, "mm", meas, 0.01,
                     "沿 +X 自槽口打到端挡"))
    h = ray_hits(cage, (20.0, 3.5, -5.0), (0, 0, 1))
    meas = (float(h[2]) - float(h[1])) if len(h) >= 3 else None
    out.append(Probe("temple_cage", "电池槽高度", v("batt_v") + 2 * clr, "mm", meas, 0.01,
                     "沿 +Z 量槽底到侧挡底"))
    # 电池座净厚 (沿 +Y @ Z=24.0, 避开压垫槽)
    h = ray_hits(cage, (20.0, -5.0, 24.0), (0, 1, 0))
    meas = nearest_void(h, 3.0)
    out.append(Probe("temple_cage", "电池座净厚 (Rev A 非对称 4.75)", v("batt_seat"), "mm",
                     meas, 0.005, "沿 +Y @ Z=24.0 量座深"))
    # 压垫槽深
    h_in = ray_hits(cage, (20.0, -5.0, 12.0), (0, 1, 0))
    inner = nearest_void(h_in, 3.0)
    h_out = ray_hits(cage, (20.0, -5.0, 24.0), (0, 1, 0))
    outer = nearest_void(h_out, 3.0)
    groove = None if (inner is None or outer is None) else (inner - outer)
    out.append(Probe("temple_cage", "顶板压垫槽深 (Rev A 0.40)", v("pad_groove"), "mm",
                     groove, 0.005, "槽内净厚 − 槽外净厚"))
    # 顶板厚: 自空腔内 (y=5.0) 沿 +Y
    h = ray_hits(cage, (20.0, 5.0, 24.0), (0, 1, 0))
    meas = first_solid(h)
    out.append(Probe("temple_cage", "电池段顶板厚 (Rev A 0.80)", v("top_plate"), "mm",
                     meas, 0.005, "自空腔内取第一段实体 = 顶板厚"))
    # PCB 定位板: 板长 60 (沿 +X, y = by0+1 避开孔)
    by0 = L["tc_by0"]
    h = ray_hits(cage, (-5.0, by0 + 1.0, 1.0), (1, 0, 0))
    meas = first_solid(h)
    out.append(Probe("temple_cage", "PCB 定位板长 (Rev B 60mm)", v("pcb_len"), "mm", meas, 0.01,
                     "沿 +X 过板取第一段实体"))
    # 板宽 30 (沿 +Y, x = 1)
    h = ray_hits(cage, (1.0, by0 - 5.0, 1.0), (0, 1, 0))
    meas = first_solid(h)
    out.append(Probe("temple_cage", "PCB 定位板宽 (Rev B 30mm)", v("pcb_wid"), "mm", meas, 0.01,
                     "沿 +Y 过板取第一段实体"))
    # PIN-SET-2 四孔
    for bx, by, dia, name in (
            (v("pinset2_p1_x"), v("pinset2_p_y"), v("clr_hole"), "P1 销孔让过 ⌀2.4"),
            (v("pinset2_p2_x"), v("pinset2_p_y"), v("clr_hole"), "P2 销孔让过 ⌀2.4"),
            (v("pinset2_s1_x"), v("pinset2_s1_y"), v("screw_clr"), "S1 压紧孔让过 ⌀1.6"),
            (v("pinset2_s2_x"), v("pinset2_s2_y"), v("screw_clr"), "S2 压紧孔让过 ⌀1.6")):
        h = ray_hits(cage, (-5.0, by0 + by, 1.0), (1, 0, 0))
        meas = nearest_void(h, bx + 5.0)
        out.append(Probe("temple_cage", f"PIN-SET-2 {name}", dia, "mm", meas, 0.01,
                         "沿 +X 过孔心量孔径"))
    # 板厚三档 (Y 92..98)
    for i, t in enumerate((0.41, 0.80, 1.22)):
        h = ray_hits(cage, (4.0 + i * 8.0, L["tc_thk_y"] + 3.0, 1e3), (0, 0, -1))
        meas = (1e3 - float(h[0]) - 2.0) if len(h) else None
        out.append(Probe("temple_cage", f"板厚试样 {t:.2f}mm (ISS-122 区间)", t, "mm",
                         meas, 0.005, "自 +Z 向下量厚度档"))
    # 走线槽 6×2
    dy = L["tc_duct_y"]
    h = ray_hits(cage, (30.0, dy - 5.0, 3.0), (0, 1, 0))
    meas = nearest_void(h, dy + 4.0)
    out.append(Probe("temple_cage", "走线槽宽", v("duct_w"), "mm", meas, 0.01, "沿 +Y 量两壁净宽"))
    h_wall = ray_hits(cage, (30.0, dy + 0.5, -5.0), (0, 0, 1))
    h_floor = ray_hits(cage, (30.0, dy + 4.0, -5.0), (0, 0, 1))
    meas = None
    if len(h_wall) >= 2 and len(h_floor) >= 2:
        meas = (float(h_wall[-1]) - float(h_floor[-1]))
    out.append(Probe("temple_cage", "走线槽高", v("duct_h"), "mm", meas, 0.01, "槽壁总高−槽底厚"))
    # ISS-092 检修口壁 (Y 120.., 壁厚 0.8, 通窗 x 6..16.2 / z 8..12.6)
    wx = L["tc_wall_y"]
    wall_t = L["tc_wall_t"]
    win_x0, win_z0 = L["tc_win_x0"], L["tc_win_z0"]
    ox, oy = v("sp_open_x"), v("sp_open_y")
    bcx, bcz = win_x0 + ox / 2, win_z0 + oy / 2
    # 通窗开口 X: 沿 +X 过通窗中心 (Z=bcz, Y=壁厚中段)
    h = ray_hits(cage, (-5.0, wx + wall_t / 2, bcz), (1, 0, 0))
    meas = nearest_void(h, win_x0 + ox / 2 + 5.0)
    out.append(Probe("temple_cage", "ISS-092 通窗开口 X", v("sp_open_x"), "mm", meas, 0.01,
                     "沿 +X 过通窗中心量开口"))
    # 通窗开口高: 沿 +Z 过通窗中心
    h = ray_hits(cage, (bcx, wx + wall_t / 2, -5.0), (0, 0, 1))
    meas = nearest_void(h, win_z0 + oy / 2 + 5.0)
    out.append(Probe("temple_cage", "ISS-092 通窗开口 Y (高)", v("sp_open_y"), "mm", meas, 0.01,
                     "沿 +Z 过通窗中心量开口"))
    # 螺钉凸台外径 ⌀3.20: 沿 +X 过凸台心 (Y 在凸台段)
    h = ray_hits(cage, (-5.0, wx + wall_t + v("sp_boss_len") / 2, bcz), (1, 0, 0))
    meas = nearest_solid(h, win_x0 + ox / 2 + 5.0)
    out.append(Probe("temple_cage", "ISS-092 螺钉凸台外径 ⌀3.20", v("sp_boss_dia"), "mm",
                     meas, 0.01, "沿 +X 过凸台心量实体段 = 凸台外径"))
    # 凸台自攻底孔 ⌀1.30: 同一射线上的空档
    h = ray_hits(cage, (-5.0, wx + wall_t + v("sp_boss_len") / 2, bcz), (1, 0, 0))
    meas = nearest_void(h, win_x0 + ox / 2 + 5.0)
    out.append(Probe("temple_cage", "ISS-092 螺钉凸台自攻底孔 ⌀1.30", v("sp_pilot"), "mm",
                     meas, 0.01, "沿 +X 过凸台心量底孔空档"))
    # 定位凸台 ⌀1.60 (沿 +X 过凸台心, Y 在凸台高度段)
    h = ray_hits(cage, (-5.0, wx + wall_t + 0.3, bcz), (1, 0, 0))
    iv = solids(h)
    meas = None
    if iv:
        s = min(iv, key=lambda q: abs((q[0] + q[1]) / 2 - (9.0 + 5.0)))
        meas = s[1] - s[0]
    out.append(Probe("temple_cage", "ISS-092 定位凸台 ⌀1.60", v("sp_pin_dia"), "mm", meas, 0.01,
                     "沿 +X 过定位凸台心量实体段"))
    # 定位凸台间距 6.00
    h = ray_hits(cage, (-5.0, wx + wall_t + 0.3, bcz), (1, 0, 0))
    iv = solids(h)
    meas = None
    if len(iv) >= 2:
        c1 = (iv[0][0] + iv[0][1]) / 2
        c2 = (iv[1][0] + iv[1][1]) / 2
        meas = c2 - c1
    out.append(Probe("temple_cage", "ISS-092 定位凸台间距", v("sp_pin_pitch"), "mm", meas, 0.02,
                     "沿 +X 量两凸台中心距"))
    # 磁铁沉槽 ⌀4.0 (沿 +X 过沉槽心, Y 在沉槽段)
    h = ray_hits(cage, (-5.0, wx + wall_t + 1.0, bcz), (1, 0, 0))
    meas = nearest_void(h, 2.0 + v("sp_mag_dia") / 2 + 5.0)
    out.append(Probe("temple_cage", "ISS-092 镜脚侧磁铁沉槽 ⌀4.0", v("sp_mag_dia"), "mm",
                     meas, 0.01, "沿 +X 过沉槽心量孔径"))

    # ================= frame_typec =================
    for (x0, ow, oh, name) in ((0.0, v("tc_open_w"), v("tc_open_h"), "现口径"),
                               (20.0, v("tc_open_w2"), v("tc_open_h2"), "ISS-089 建议口径")):
        t = v("tc_plate_t")
        w = v("tc_wall_min")
        # 开口宽: 沿 +X 过开口中心 (Z = w + oh/2)
        h = ray_hits(ftc, (x0 - 5.0, t / 2, w + oh / 2), (1, 0, 0))
        meas = nearest_void(h, x0 + ow / 2 + 5.0)
        out.append(Probe("frame_typec", f"Type-C 开口宽 ({name})", ow, "mm", meas, 0.01,
                         "沿 +X 过开口中心量宽"))
        # 开口高: 沿 +Z 过开口中心
        h = ray_hits(ftc, (x0 + w + ow / 2, t / 2, -5.0), (0, 0, 1))
        meas = nearest_void(h, w + oh / 2 + 5.0)
        out.append(Probe("frame_typec", f"Type-C 开口高 ({name})", oh, "mm", meas, 0.01,
                         "沿 +Z 过开口中心量高"))
        # 左承力壁厚: 沿 +X 过上壁高度 (Z = oh + w + w/2), 取第一段实体
        h = ray_hits(ftc, (x0 - 5.0, t / 2, oh + w + w / 2), (1, 0, 0))
        meas = first_solid(h)
        out.append(Probe("frame_typec", f"Type-C 左承力壁厚 ({name})", w, "mm", meas, 0.01,
                         "沿 +X 取第一段实体 = 左壁厚"))
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
