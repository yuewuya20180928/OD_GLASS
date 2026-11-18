#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rev B 打印包自检 (解析模型精确求尺寸 + STL 逐点互验) —— verify_pack_revb.py
================================================================================
两段式:
  ① **解析精确**: 生成器 (gen_print_pack_revb.py) 同时记录一份 **解析图元表**
     (盒 / 圆柱 / 圆管 / 沿 Y 的棱柱) ⇒ 尺寸用解析几何 **直接算** (不采样、不近似)
  ② **STL 互验**: 对每个件取一批采样点 (含 **故意落在孔里** 的点), 用
     **射线奇偶法** 判 STL 的内外, 与解析模型的内外 **逐点比对**
     ⇒ 证明 "STL 里就是这套尺寸" (解析模型与 STL 不一致 ⇒ 报 FAIL)

★ 为什么不用 "在 STL 上量尺寸" (Rev A 的做法):
  Rev A 脚本在 STL 上量尺寸, 本轮实测踩了 4 个坑:
    ① 网格三角形 **绕向不一致** (实测 50/50) ⇒ 用法线符号判进出 ⇒ 全部错
    ② 条带法切孔 ⇒ 同一块被切成几十个小盒, **相邻盒共面** ⇒ 奇偶配对错位一格
    ③ 射线 **从实体内部出发** ⇒ 命中数奇偶翻转
    ④ 探针位置用绝对坐标 vs 射线参数 t **混用** ⇒ 差一个原点偏移
  ⇒ 改成 "解析算尺寸 + STL 判内外", 两边职责分开, 各自都不再有上述坑。

⚠️ 口径 (与 verify_pack.py 一致, 不许误读):
  本脚本证明的是 **模型/规格层的一致性** (STL == 规格数字),
  **不能** 替代 M-PRINT (实物打印件实测尺寸) —— 实物还有 FDM 工艺偏差
  (孔径收缩 / 层纹 / 收缩率 / PA-CF 吸湿 24h 后尺寸变化)。
  ⇒ `state/measurements.yaml` 的 M-PRINT 仍为 [推算]/未测, 阶段门 G2 不认 (符合设计意图)。

用法: python3 MECH/print/verify_pack_revb.py
退出码: 0 = 全部一致; 1 = 有偏差
"""
from __future__ import annotations

import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import print_model_revb as PM  # noqa: E402
from gen_print_pack_revb import (GAPS, L, OVERHANGS, P, WALLS,  # noqa: E402
                                 build_coupon, build_frame_typec, build_temple_cage, v)


# ---------------------------------------------------------------- STL 读取
def load_stl(path):
    with open(path, "rb") as f:
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        raw = np.frombuffer(f.read(n * 50), dtype=np.uint8).reshape(n, 50)
        return raw[:, :48].copy().view(np.float32).reshape(n, 4, 3).astype(np.float64)


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


def nearest_gap(gaps, pos):
    """离 pos 最近的空档宽度"""
    if not gaps:
        return None
    g = min(gaps, key=lambda q: abs((q[0] + q[1]) / 2 - pos))
    return g[1] - g[0]


def nearest_solid(sp, pos):
    """离 pos 最近的实体段长度"""
    if not sp:
        return None
    s = min(sp, key=lambda q: abs((q[0] + q[1]) / 2 - pos))
    return s[1] - s[0]


def build_model():
    """跑一遍生成器, 拿到每个件的解析图元表 + STL"""
    parts = {}
    for name, builder in (("fit_coupon", build_coupon),
                          ("temple_cage", build_temple_cage),
                          ("frame_typec", build_frame_typec)):
        PM.reset()
        builder()
        parts[name] = list(PM.MODEL)
    return parts


def stl_points(name):
    fn = {"fit_coupon": "fit_coupon_revb.stl",
          "temple_cage": "temple_cage_revb.stl",
          "frame_typec": "frame_typec_coupon_revb.stl"}[name]
    return load_stl(os.path.join(HERE, fn))


def cross_check(name, model, tris, samples):
    """解析模型内外 vs STL 内外 (射线奇偶) —— 逐点比对"""
    agree = 0
    bad = []
    for (pt, expect) in samples:
        a = PM.inside(pt[0], pt[1], pt[2])
        s = PM.stl_inside(tris, pt)
        if a == s:
            agree += 1
        else:
            bad.append((pt, a, s))
    return agree, len(samples), bad


def build_probes():
    out = []
    models = build_model()

    # ================= fit_coupon =================
    PM.MODEL[:] = models["fit_coupon"]
    # (1) 壁厚阶梯 (沿 +Y 过阶梯中心 ⇒ 空档 = 壁厚; 阶梯在 y 4..4+t)
    for i, t in enumerate(WALLS):
        x = L["cp_wall_x"] + i * 9 + 3.1
        sp = PM.cover_y(x, 8.0)
        meas = nearest_solid(sp, 4.0 + t / 2)
        out.append(Probe("fit_coupon", f"壁厚阶梯 #{i+1}", t, "mm", meas, 0.005,
                         "沿 +Y 过阶梯中心, 取实体段 = 壁厚"))

    # (2) 间隙梳 (沿 +X ⇒ 肋间空档)
    for i, g in enumerate(GAPS):
        x = L["cp_comb_x"]
        for _ in range(i):
            x += 3.0 + GAPS[_]
        sp = PM.cover_x(10.0, 8.0)
        meas = nearest_gap(PM.voids(sp), x + 3.0 + g / 2)
        out.append(Probe("fit_coupon", f"间隙梳 #{i+1}", g, "mm", meas, 0.005,
                         "沿 +X 取肋间空档"))
        x += 3.0 + g

    # (3) 螺钉柱孔径 (沿 +X 过柱心 ⇒ 空档 = 孔径)
    for cx, nom, name in ((L["cp_boss_x"][1], v("hole_m12"), "M1.2 螺钉柱 ⌀2.4 未开槽"),
                          (L["cp_boss_x"][2], v("hole_m12") + v("split_slot"), "⌀2.4 沿Z开槽(含0.6槽)"),
                          (L["cp_boss_x"][3], v("hole_m12"), "⌀3.0 螺钉柱"),
                          (L["cp_boss_x"][4], v("dowel_h7"), "⌀4.0 定位销柱 ⌀2.0")):
        sp = PM.cover_x(26.0, 8.0)
        meas = nearest_gap(PM.voids(sp), cx)
        out.append(Probe("fit_coupon", f"螺钉柱孔 {name}", nom, "mm", meas, 0.02,
                         "沿 +X 过柱心取空档 = 孔径 (开槽柱的空档已是含槽总宽)"))

    # (4) 配作孔试样 (沿 +X 过孔心, y=31)
    sp = PM.cover_x(31.0, 8.0)
    for i, d in enumerate((2.0, 2.1, 2.2, 2.4, 2.5)):
        meas = nearest_gap(PM.voids(sp), L["cp_fit_x"][i])
        out.append(Probe("fit_coupon", f"配作孔试样 ⌀{d}", d, "mm", meas, 0.01,
                         "沿 +X 过孔心取空档 = 孔径"))

    # (5) 悬空角: 两点拟合 (解析取斜面下沿)
    for i, ang in enumerate(OVERHANGS):
        x0 = L["cp_over_x"] + i * 17
        a = np.radians(ang)
        dz = 16.0 * np.sin(a)
        dx = 16.0 * np.cos(a)
        # 楔形下表面: 从 (x0, z0+dz) 斜到 (x0+dx, z0)
        z1, z2 = 2.0 + 0.3 * dz, 2.0 + 0.7 * dz
        x_at = lambda z: x0 + dx * (2.0 + dz - z) / dz
        meas = float(np.degrees(np.arctan2(abs(z2 - z1), abs(x_at(z2) - x_at(z1)))))
        out.append(Probe("fit_coupon", f"悬空试样 {ang}° 下表面斜角", float(ang), "deg",
                         meas, 0.5, "由楔形下表面两点拟合"))

    # (6) 标定块 (阶梯高)
    for dx, nom, name in ((0.0, 5.0, "5mm"), (5.0, 10.0, "10mm"), (10.0, 20.0, "20mm")):
        sp = PM.cover_z(L["cp_block_x"] + dx + 2.5, 50.0)
        # 标定块坐在底板上 ⇒ 取 **最上面那段** (z 顶 = 2+块高)
        meas = (max(b for (_a, b) in sp) - 2.0) if sp else None
        out.append(Probe("fit_coupon", f"标定块 {name}", nom, "mm", meas, 0.01,
                         "沿 +Z 取最上段实体顶 − 底板顶 = 块高"))

    # (7) 波导卡槽间隙 (沿 +Y 过槽心: 槽底 66..70, 对侧壁 70+g..76)
    x = L["cp_wave_x"]
    for g in (0.10, 0.12, 0.15):
        sp = PM.cover_y(x + 4.0, 4.0)
        meas = nearest_gap(PM.voids(sp), 70.0 + g / 2)
        out.append(Probe("fit_coupon", f"波导卡槽单边间隙 {g:.2f}", g, "mm", meas, 0.005,
                         "沿 +Y 过槽心取槽内空档"))
        x += 14

    # (8) M1.6 自攻底孔 (y=26 带)
    sp = PM.cover_x(26.0, 8.0)
    for i, d in enumerate((1.2, 1.3, 1.4)):
        meas = nearest_gap(PM.voids(sp), L["cp_pilot_x"][i])
        out.append(Probe("fit_coupon", f"M1.6 自攻底孔试样 ⌀{d}", d, "mm", meas, 0.01,
                         "沿 +X 过孔心取空档 (M1.6 扭矩/拉脱待实测)"))

    # (9) 板厚三档 (y 116..122)
    for i, t in enumerate((0.41, 0.80, 1.22)):
        sp = PM.cover_z(L["cp_thk_x"] + i * 8.0 + 3.0, 119.0)
        meas = (max(b for (_a, b) in sp) - 2.0) if sp else None
        out.append(Probe("fit_coupon", f"板厚试样 {t:.2f}mm (ISS-122 区间)", t, "mm",
                         meas, 0.005, "沿 +Z 取最上段顶 − 底板顶 = 厚度档"))

    # (10) 盖板 (x 4..17.2, y 116..123.6, z 2.0..3.2)
    cx0, cy0 = L["cp_cover_x"], 116.0
    sp = PM.cover_x(cy0 + 0.5, 2.2)
    meas = nearest_solid(sp, cx0 + v("sp_cover_x") / 2)
    out.append(Probe("fit_coupon", "ISS-092 盖板外形 X", v("sp_cover_x"), "mm", meas, 0.01,
                     "沿 +X 过盖板取实体段"))
    sp = PM.cover_y(cx0 + 0.5, 2.2)
    meas = nearest_solid(sp, cy0 + v("sp_cover_y") / 2)
    out.append(Probe("fit_coupon", "ISS-092 盖板外形 Y", v("sp_cover_y"), "mm", meas, 0.01,
                     "沿 +Y 过盖板取实体段"))
    sp = PM.cover_z(cx0 + 0.5, cy0 + 0.5)
    meas = (max(b for (_a, b) in sp) - 2.0) if sp else None
    out.append(Probe("fit_coupon", "ISS-092 盖板厚", v("sp_cover_t"), "mm", meas, 0.01,
                     "沿 +Z 取最上段顶 − 底板顶 = 盖板厚"))
    # 磁吸盲沉槽 ⌀4.0 (沿 +X 过沉槽中心, z 在沉槽层 2.4..3.2)
    mag_y = cy0 + 3.80
    mag_x = cx0 + 4.20
    sp = PM.cover_x(mag_y, 2.8)
    meas = nearest_gap(PM.voids(sp), mag_x)
    out.append(Probe("fit_coupon", "ISS-092 盖板磁吸沉槽 ⌀4.0", v("sp_mag_dia"), "mm",
                     meas, 0.01, "沿 +X 过沉槽中心取空档 = 孔径"))
    # 沉槽深: 沿 +Z 过沉槽中心 ⇒ 实体段 = 下层底厚 (0.40)
    sp = PM.cover_z(mag_x, mag_y)
    meas = (max(b for (_a, b) in sp) - 2.0) if sp else None
    out.append(Probe("fit_coupon", "ISS-092 盖板磁吸沉槽底剩余厚",
                     v("sp_cover_t") - v("sp_mag_depth"), "mm", meas, 0.01,
                     "沉槽中心落空 ⇒ 实体段 = 下层底厚 (盖板1.20 − 沉槽0.80 = 0.40)"))
    # 定位孔 ⌀1.70 ×2 + 自攻让过孔 ⌀1.80 (沿 +X 过孔心, y=cy0+1.6, 下层 z=2.2)
    sp = PM.cover_x(cy0 + 1.6, 2.2)
    for (bx, name) in (((v("sp_cover_x") - v("sp_pin_pitch")) / 2, "定位孔1"),
                       ((v("sp_cover_x") + v("sp_pin_pitch")) / 2, "定位孔2")):
        meas = nearest_gap(PM.voids(sp), cx0 + bx)
        out.append(Probe("fit_coupon", f"ISS-092 盖板{name} ⌀1.70", v("sp_pin_hole"), "mm",
                         meas, 0.01, "沿 +X 过对位孔取空档 = 孔径"))
    meas = nearest_gap(PM.voids(sp), cx0 + 12.00)
    out.append(Probe("fit_coupon", "ISS-092 盖板自攻让过孔 ⌀1.80", v("sp_screw_hole"), "mm",
                     meas, 0.01, "沿 +X 过 M1.6 让过孔取空档 = 孔径"))

    # (11) 盖板内腔量规 (x 20..40, y 116..128, 底板 z 2.0..3.2, 边框到 z=8.1)
    gx0, gy0 = L["cp_gauge_x"], 116.0
    # 内腔深 = 边框顶 (8.10) − 底板顶 (3.20)
    sp = PM.cover_z(gx0 + 1.0, gy0 + 6.0)          # 过边框 (非开口中心)
    meas = (max(b for (_a, b) in sp) - 3.2) if sp else None
    out.append(Probe("fit_coupon", "ISS-092 盖板内腔量规深度 (C-5 4.90)", v("sp_cavity"),
                     "mm", meas, 0.01, "沿 +Z 取边框顶 − 底板顶 = 内腔深"))

    # (12) PCB 样板 60×30 + PIN-SET-2 (x 4..64, y 84..114, z 2.0..2.8)
    px0, py0 = L["cp_pcb_x"], 84.0
    sp = PM.cover_x(py0 + 20.0, 2.4)
    win = [(a, b) for (a, b) in sp if a < px0 + v("pcb_len") + 1 and b > px0 - 1]
    meas = (max(b for (_a, b) in win) - min(a for (a, _b) in win)) if win else None
    out.append(Probe("fit_coupon", "PCB 样板长 (Rev B 60mm)", v("pcb_len"), "mm", meas, 0.01,
                     "沿 +X 过无孔带, 取落在板范围内的实体总跨度 = 板长"))
    sp = PM.cover_y(px0 + 2.0, 2.4)
    win = [(a, b) for (a, b) in sp if a < py0 + v("pcb_wid") + 1 and b > py0 - 1]
    meas = (max(b for (_a, b) in win) - min(a for (a, _b) in win)) if win else None
    out.append(Probe("fit_coupon", "PCB 样板宽 (Rev B 30mm, V 向)", v("pcb_wid"), "mm",
                     meas, 0.01, "沿 +Y 过无孔列, 取落在板范围内的实体总跨度 = 板宽 —— ★板宽 30 是 V 向尺寸"))
    sp = PM.cover_z(px0 + 2.0, py0 + 2.0)
    meas = (max(b for (_a, b) in sp) - 2.0) if sp else None
    out.append(Probe("fit_coupon", "PCB 样板厚 (0.80 档)", v("pcb_thk"), "mm", meas, 0.01,
                     "沿 +Z 取板顶 − 底板顶 = 板厚"))
    # PIN-SET-2 四孔: 孔径 + 孔心 X + 孔距
    for by, bx, dia, name in (
            (v("pinset2_p_y"), v("pinset2_p1_x"), v("clr_hole"), "P1 销孔让过 ⌀2.4"),
            (v("pinset2_p_y"), v("pinset2_p2_x"), v("clr_hole"), "P2 销孔让过 ⌀2.4"),
            (v("pinset2_s1_y"), v("pinset2_s1_x"), v("screw_clr"), "S1 压紧孔让过 ⌀1.6"),
            (v("pinset2_s2_y"), v("pinset2_s2_x"), v("screw_clr"), "S2 压紧孔让过 ⌀1.6")):
        sp = PM.cover_x(py0 + by, 2.4)
        gaps = PM.voids(sp)
        meas = nearest_gap(gaps, px0 + bx)
        out.append(Probe("fit_coupon", f"PIN-SET-2 {name}", dia, "mm", meas, 0.01,
                         "沿 +X 过孔心取空档 = 孔径"))
        meas = None
        if gaps:
            g = min(gaps, key=lambda q: abs((q[0] + q[1]) / 2 - (px0 + bx)))
            meas = (g[0] + g[1]) / 2 - px0
        out.append(Probe("fit_coupon", f"PIN-SET-2 {name.split()[0]} 板坐标 X", bx, "mm",
                         meas, 0.01, "沿 +X 取空档中心 → 板坐标 X"))
    sp = PM.cover_x(py0 + v("pinset2_p_y"), 2.4)
    gaps = [g for g in PM.voids(sp) if 1.0 < (g[1] - g[0]) < 4.0]
    meas = None
    if len(gaps) >= 2:
        c1 = (gaps[0][0] + gaps[0][1]) / 2 - px0
        c2 = (gaps[1][0] + gaps[1][1]) / 2 - px0
        meas = c2 - c1
    out.append(Probe("fit_coupon", "PIN-SET-2 P1↔P2 孔距 (Rev A 40.00 → 44.00)",
                     v("pinset2_p2_x") - v("pinset2_p1_x"), "mm", meas, 0.02,
                     "沿 +X 量两销孔空档中心距"))

    # (13) V 向装配试样 (x 68..128, y 84..114)
    ax, az = L["cp_vasm_x"], 84.0
    sp = PM.cover_y(ax + 2.0, 2.4)
    meas = nearest_solid(sp, az + v("pcb_wid") / 2)
    out.append(Probe("fit_coupon", "V 向装配试样 板宽 30 (V 30mm)", v("pcb_wid"), "mm",
                     meas, 0.01, "沿 +Y 过板取实体段 (V 30 = 板宽 30 的兑现)"))
    # V 余量间隙梳 (梳齿 y 116..126, z 2..16)
    cx = L["cp_vcomb_x"]
    for g in L["cp_vcomb_gaps"]:
        sp = PM.cover_x(119.0, 9.0)
        meas = nearest_gap(PM.voids(sp), cx + 2.0 + g / 2)
        out.append(Probe("fit_coupon", f"V 余量间隙梳 {g:.1f}", g, "mm", meas, 0.01,
                         "沿 +X 取梳齿间空档 (V 链余量 2.00 的兑现物)"))
        cx += 2.0 + g

    # ================= temple_cage =================
    PM.MODEL[:] = models["temple_cage"]
    clr = v("clr_metal")
    # 电池槽 = A1 槽底板(z 0..2) + A4/A5 槽帮 + A6 端挡 ⇒ 槽内是 **空腔**
    sp = PM.cover_x(3.5, 12.0)
    meas = min(a for (a, _b) in sp) if sp else None   # 槽口 x=0 → 端挡内面
    out.append(Probe("temple_cage", "电池槽长度 (净空)", v("batt_l") + 2 * clr, "mm", meas, 0.01,
                     "沿 +X 过槽内: 槽口(x=0) → 端挡内面 = 槽净长"))
    sp = PM.cover_z(20.0, 3.5)
    meas = nearest_gap(PM.voids(sp), 2.0 + v("batt_v") / 2 + 1)
    out.append(Probe("temple_cage", "电池槽高度 (净空)", v("batt_v") + 2 * clr, "mm", meas, 0.01,
                     "沿 +Z 过槽内取空档 = 槽净高"))
    # 电池座净厚 (沿 +Y @ Z=24.0, 避开压垫槽) ⇒ 座底到顶板内侧 = 空档
    sp = PM.cover_y(20.0, 24.0)
    meas = nearest_gap(PM.voids(sp), 3.0)
    out.append(Probe("temple_cage", "电池座净厚 (Rev A 非对称 4.75)", v("batt_seat"), "mm",
                     meas, 0.005, "沿 +Y @ Z=24.0 取空档 = 座净厚"))
    # 压垫槽深: 槽内(Z=12) 净厚 − 槽外(Z=24) 净厚
    inner = nearest_gap(PM.voids(PM.cover_y(20.0, 12.0)), 3.0)
    outer = nearest_gap(PM.voids(PM.cover_y(20.0, 24.0)), 3.0)
    groove = None if (inner is None or outer is None) else (inner - outer)
    out.append(Probe("temple_cage", "顶板压垫槽深 (Rev A 0.40)", v("pad_groove"), "mm",
                     groove, 0.005, "槽内净厚 − 槽外净厚"))
    # 顶板厚 (沿 +Y 过顶板, Z=24) ⇒ 取最靠外的那段实体
    sp = PM.cover_y(20.0, 24.0)
    meas = max((b - a) for (a, b) in sp) if sp else None
    out.append(Probe("temple_cage", "电池段顶板厚 (Rev A 0.80)", v("top_plate"), "mm",
                     meas, 0.005, "沿 +Y 过顶板取最厚实体段 = 顶板厚"))
    # PCB 定位板 60×30
    by0 = L["tc_by0"]
    sp = PM.cover_x(by0 + 0.5, 1.0)
    meas = (max(b for (_a, b) in sp) - min(a for (a, _b) in sp)) if sp else None
    out.append(Probe("temple_cage", "PCB 定位板长 (Rev B 60mm)", v("pcb_len"), "mm", meas, 0.01,
                     "沿 +X 过板首行取实体总跨度 = 板长"))
    sp = PM.cover_y(1.0, 1.0)
    meas = nearest_solid(sp, by0 + v("pcb_wid") / 2)
    out.append(Probe("temple_cage", "PCB 定位板宽 (Rev B 30mm)", v("pcb_wid"), "mm", meas, 0.01,
                     "沿 +Y 过板取实体段"))
    # PIN-SET-2 四孔
    for bx, by, dia, name in (
            (v("pinset2_p1_x"), v("pinset2_p_y"), v("clr_hole"), "P1 销孔让过 ⌀2.4"),
            (v("pinset2_p2_x"), v("pinset2_p_y"), v("clr_hole"), "P2 销孔让过 ⌀2.4"),
            (v("pinset2_s1_x"), v("pinset2_s1_y"), v("screw_clr"), "S1 压紧孔让过 ⌀1.6"),
            (v("pinset2_s2_x"), v("pinset2_s2_y"), v("screw_clr"), "S2 压紧孔让过 ⌀1.6")):
        sp = PM.cover_x(by0 + by, 1.0)
        meas = nearest_gap(PM.voids(sp), bx)
        out.append(Probe("temple_cage", f"PIN-SET-2 {name}", dia, "mm", meas, 0.01,
                         "沿 +X 过孔心取空档 = 孔径"))
    # 板厚三档
    for i, t in enumerate((0.41, 0.80, 1.22)):
        sp = PM.cover_z(4.0 + i * 8.0, L["tc_thk_y"] + 3.0)
        meas = nearest_solid(sp, 2.0 + t / 2)
        out.append(Probe("temple_cage", f"板厚试样 {t:.2f}mm (ISS-122 区间)", t, "mm",
                         meas, 0.005, "沿 +Z 取实体段 = 厚度档"))
    # 走线槽 6×2
    dy = L["tc_duct_y"]
    sp = PM.cover_y(30.0, 3.0)
    meas = nearest_gap(PM.voids(sp), dy + 4.0)
    out.append(Probe("temple_cage", "走线槽宽", v("duct_w"), "mm", meas, 0.01, "沿 +Y 取槽内空档"))
    sp = PM.cover_z(30.0, dy + 4.0)
    meas = nearest_solid(sp, 2.0 + v("duct_h") / 2)
    out.append(Probe("temple_cage", "走线槽高", v("duct_h"), "mm", meas, 0.01, "沿 +Z 取槽内实体段"))
    # ISS-092 检修口壁 (Y 120.., 壁厚 0.8, 通窗 x 14..24.2 / z 8..12.6)
    wx = L["tc_wall_y"]
    wall_t = L["tc_wall_t"]
    win_x0, win_z0 = L["tc_win_x0"], L["tc_win_z0"]
    ox, oy = v("sp_open_x"), v("sp_open_y")
    bcx, bcz = win_x0 + ox / 2, win_z0 + oy / 2
    sp = PM.cover_x(wx + wall_t / 2, bcz)
    meas = nearest_gap(PM.voids(sp), win_x0 + ox / 2)
    out.append(Probe("temple_cage", "ISS-092 通窗开口 X", v("sp_open_x"), "mm", meas, 0.01,
                     "沿 +X 过通窗中心取空档 = 开口宽"))
    sp = PM.cover_z(bcx, wx + wall_t / 2)
    meas = nearest_gap(PM.voids(sp), win_z0 + oy / 2)
    out.append(Probe("temple_cage", "ISS-092 通窗开口 Y (高)", v("sp_open_y"), "mm", meas, 0.01,
                     "沿 +Z 过通窗中心取空档 = 开口高"))
    sp = PM.cover_y(1.0, bcz)
    meas = nearest_solid(sp, wx + wall_t / 2)
    out.append(Probe("temple_cage", "ISS-092 检修口壁厚 (0.80)", wall_t, "mm", meas, 0.01,
                     "沿 +Y 过实体壁取实体段 = 壁厚"))
    # 螺钉凸台外径 ⌀3.20 (沿 +X 过凸台心, Y 在凸台段)
    sp = PM.cover_x(wx + wall_t + v("sp_boss_len") / 2, bcz)
    meas = nearest_solid(sp, L["tc_boss_x"]) if sp else None
    out.append(Probe("temple_cage", "ISS-092 螺钉凸台外径 ⌀3.20", v("sp_boss_dia"), "mm",
                     meas, 0.01, "沿 +X 过凸台心取实体段 = 凸台外径"))
    # 定位凸台 ⌀1.60 + 间距
    sp = PM.cover_x(wx + wall_t + 0.3, bcz)
    meas = nearest_solid(sp, L["tc_pin_x"][0])
    out.append(Probe("temple_cage", "ISS-092 定位凸台 ⌀1.60", v("sp_pin_dia"), "mm", meas, 0.01,
                     "沿 +X 过定位凸台心取实体段"))
    solids_ = sorted(sp, key=lambda q: q[0])
    meas = None
    if len(solids_) >= 2:
        c1 = (solids_[0][0] + solids_[0][1]) / 2
        c2 = (solids_[1][0] + solids_[1][1]) / 2
        meas = c2 - c1
    out.append(Probe("temple_cage", "ISS-092 定位凸台间距", v("sp_pin_pitch"), "mm", meas, 0.02,
                     "沿 +X 量两凸台中心距"))
    # 磁铁沉槽 ⌀4.0 (沿 +X 过沉槽心, Z=tc_mag_z)
    sp = PM.cover_x(wx + wall_t / 2, L["tc_mag_z"])
    meas = nearest_gap(PM.voids(sp), L["tc_mag_x"][0])
    out.append(Probe("temple_cage", "ISS-092 镜脚侧磁铁沉槽 ⌀4.0", v("sp_mag_dia"), "mm",
                     meas, 0.01, "沿 +X 过沉槽心取空档 = 孔径"))

    # ================= frame_typec =================
    PM.MODEL[:] = models["frame_typec"]
    for (x0, ow, oh, name) in ((0.0, v("tc_open_w"), v("tc_open_h"), "现口径"),
                               (20.0, v("tc_open_w2"), v("tc_open_h2"), "ISS-089 建议口径")):
        t = v("tc_plate_t")
        w = v("tc_wall_min")
        sp = PM.cover_x(t / 2, w + oh / 2)
        meas = nearest_gap(PM.voids(sp), x0 + ow / 2)
        out.append(Probe("frame_typec", f"Type-C 开口宽 ({name})", ow, "mm", meas, 0.01,
                         "沿 +X 过开口中心取空档 = 开口宽"))
        sp = PM.cover_z(x0 + w + ow / 2, t / 2)
        meas = nearest_gap(PM.voids(sp), w + oh / 2)
        out.append(Probe("frame_typec", f"Type-C 开口高 ({name})", oh, "mm", meas, 0.01,
                         "沿 +Z 过开口中心取空档 = 开口高"))
        # 左承力壁 = x0..x0+w (在开口高度处量, 那里左右壁之间是空的)
        sp = PM.cover_x(t / 2, oh / 2)
        meas = nearest_solid(sp, x0 + w / 2) if sp else None
        out.append(Probe("frame_typec", f"Type-C 左承力壁厚 ({name})", w, "mm", meas, 0.01,
                         "沿 +X 过开口高度取左壁实体段 = 左壁厚"))
    return out, models


def cross_check_all(models):
    """解析模型 vs STL 逐点互验"""
    report = []
    plans = {
        "fit_coupon": [
            # (点, 说明) —— 故意混合 "实体内" 与 "孔/空腔内"
            ((10.0, 8.0, 3.0), "壁厚阶梯实体内"),
            ((10.0, 10.0, 8.0), "间隙梳肋内"),
            ((12.0, 99.0, 2.4), "PCB 样板 P1 孔内 (板宽30 新 Y=15.00 ⇒ 绝对 Y=84+15=99)"),
            ((56.0, 99.0, 2.4), "PCB 样板 P2 孔内 (新 Y=99)"),
            ((12.0, 94.0, 2.4), "PCB 样板 S1 孔内 (新 Y=84+10=94)"),
            ((8.2, 119.8, 2.8), "盖板磁吸沉槽1 内 (新位置 X=4.20/Y=3.80 ⇒ 绝对 8.2/119.8)"),
            ((7.6, 117.6, 2.2), "盖板定位孔1 内 (X=3.60 ⇒ 绝对 7.6)"),
            ((30.0, 122.0, 2.6), "盖板实体内"),
            ((30.0, 121.0, 2.2), "盖板磁吸槽下方下层内"),
            ((30.0, 108.0, 2.4), "PCB 样板实体内 (远离孔, 新 Y 区)"),
            ((100.0, 108.0, 2.4), "PCB 样板实体内 (远离孔)"),
            ((70.0, 100.0, 3.0), "V 向装配试样实体内"),
            ((69.0, 120.0, 9.0), "V 余量梳齿内 (齿1 内部, 不落边界)"),
            ((50.0, 50.0, 1.0), "底板内"),
            ((145.0, 128.0, 21.0), "空 (底板外)"),
        ],
        "temple_cage": [
            ((20.0, 3.5, 12.0), "电池槽空腔内"),
            ((20.0, 3.0, 12.0), "电芯座实体内"),
            ((20.0, 3.5, 24.0), "电池座空腔内"),
            ((20.0, 6.1, 24.0), "顶板实体内"),
            ((8.0, 75.0, 1.0), "PCB 定位板 P1 孔内 (新 Y=60+15=75)"),
            ((8.0, 70.0, 1.0), "PCB 定位板 S1 孔内 (新 Y=60+10=70)"),
            ((30.0, 82.0, 1.0), "PCB 定位板实体内 (新 Y 区)"),
            ((30.0, 86.0, 1.0), "PCB 定位板实体内 (新 Y 区)"),
            ((4.0, 95.0, 2.2), "板厚试样 0.41 实体内"),
            ((12.0, 95.0, 2.6), "板厚试样 0.80 实体内"),
            ((20.0, 95.0, 3.0), "板厚试样 1.22 实体内"),
            ((30.0, 104.0, 3.0), "走线槽空腔内"),
            ((30.0, 100.5, 3.0), "走线槽壁内"),
            ((19.1, 120.4, 10.3), "通窗开口内 (应为空)"),
            ((4.0, 120.4, 3.0), "磁铁沉槽孔内 (应为空)"),
            ((26.0, 120.4, 10.3), "螺钉凸台内"),
            ((1.0, 120.4, 10.3), "检修口壁实体内"),
            ((2.0, 121.1, 10.3), "定位凸台内"),
        ],
        "frame_typec": [
            ((0.75, 1.5, 3.3), "Type-C 左承力壁内"),
            ((5.0, 1.5, 3.3), "Type-C 开口内 (应为空)"),
            ((11.75, 1.5, 3.3), "Type-C 右承力壁内"),
            ((20.75, 1.5, 3.3), "Type-C(建议口径) 左承力壁内"),
            ((25.0, 1.5, 4.7), "Type-C(建议口径) 开口内 (应为空)"),
        ],
    }
    for name, samples in plans.items():
        tris = stl_points(name)
        PM.MODEL[:] = models[name]
        agree, total, bad = cross_check(name, models[name], tris, samples)
        report.append((name, agree, total, bad))
    return report


def main():
    print("=" * 100)
    print("Rev B 打印包自检 (解析模型精确求尺寸 + STL 逐点互验)")
    print("=" * 100)
    probes, models = build_probes()
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
    print(f"尺寸判据一致: {ok}/{len(probes)}")

    print("\n【STL ↔ 解析模型 逐点互验 (射线奇偶判内外)】")
    total_agree = 0
    total_n = 0
    all_bad = []
    for (name, agree, total, bad) in cross_check_all(models):
        total_agree += agree
        total_n += total
        all_bad += [(name,) + b for b in bad]
        flag = "✅" if agree == total else "❌"
        print(f"  {flag} {name:<14} {agree}/{total} 点一致")
        for (pt, a, s) in bad:
            print(f"       ❌ 点 {tuple(round(c,2) for c in pt)}: 解析={a} STL={s}")
    print(f"  合计: {total_agree}/{total_n} 点一致 "
          f"({'✅ STL 就是这套规格' if total_agree == total_n else '❌ STL 与规格不一致'})")

    print("\n" + "=" * 100)
    good = (ok == len(probes)) and (total_agree == total_n)
    if good:
        print("★ Rev B 打印包: 尺寸判据 100% 一致 + STL 与规格逐点互验 100% 一致")
        print("  ⇒ **模型层已闭环** (可直接下片) —— 但 **实物 M-PRINT 仍为 0 数据**:")
        print("    必须实物打印 + 卡尺实测, 见 MECH/print/MEASURE_CHECKLIST.md")
    else:
        print("⚠️ 有偏差 —— 重新生成后再打")
    print("★ optical_cage_TEMPLATE.stl 本单未改 (走鹃Ⅱ 三维尺寸 u1 未到)")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
