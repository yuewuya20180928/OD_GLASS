#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P2S 打样打印包生成器 (M-PRINT 的载体)
=====================================================================
本机 **无法打印** (打印机 192.168.1.68 与本机 192.168.2.4 不同网段, 不可达;
无切片器; 无卡尺), 所以本脚本把 MECH_BUDGET.md v1.1 里的关键配合尺寸
**变成可直接下片的实体几何** —— 打印出来量出来的就是 M-PRINT 要的实测值。

生成 3 个件 (二进制 STL):
  1. fit_coupon_340.stl         配合尺寸标定件 (壁厚/间隙梳/螺钉柱/配作孔/悬空角/标定块/波导槽)
  2. temple_cage_340.stl        镜脚内腔检具 (电池座 U 槽 + 配作销 + 走线槽 + Type-C 面板)
  3. optical_cage_TEMPLATE.stl  镜框光学舱托架模板 (⚠️ 走鹃Ⅱ 三维尺寸未到, 参数全 [推算])

★ 铁律: 本脚本 **只把已定案的数字实体化, 不改镜框方案**。
  每个尺寸都在 P 表第 3 列标了来源: "v1.1 §x.y" = MECH/MECH_BUDGET.md v1.1 (改了必须同步改 v1.1);
  "RevA §特征表" = MECH/print/GEOM_SPEC_REVA.md (改了必须同步改该文件)。

★ Rev A (2026-10-26, ISS-050 第 2 步): fit_coupon / temple_cage 两个件按
  MECH/print/GEOM_SPEC_REVA.md §2 的参考实现**机械移植** (F1..F7);
  optical_cage_TEMPLATE **不动** (走鹃Ⅱ 尺寸未到 → 字节必须不变)。
  Rev A 契约值见 P 表的 batt_seat_reva / pad_groove_reva / top_plate_reva 三个键,
  由 verify_pack.py 的 check_reva_contract() 自动核对 (1e-9)。

用法:  python3 MECH/print/gen_print_pack.py
自证:  python3 MECH/print/verify_pack.py     (对 STL 做光线投射实测, 与标称值对表)
"""
from __future__ import annotations

import math
import os
import struct

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# =====================================================================
# 尺寸表 —— **两个来源, 每个键在第 3 列自报出处**
#   (标称值, 单位, 来源章节, 证据等级)
#   ① "v1.1 §x.y ..."  → MECH/MECH_BUDGET.md v1.1 的数字
#        改了这里 **必须同步改 v1.1** (同章节号)。
#   ② "RevA §特征表 ..." → MECH/print/GEOM_SPEC_REVA.md §1 特征变更总表 (Rev A 打印件特征 F1..F7)
#        改了这里 **必须同步改 GEOM_SPEC_REVA.md**。
#   ⚠️ P 表是 **单一真源**: 几何代码一律经 v(key) 取值, 不再另写数字。
# =====================================================================
P = {
    "wall_min":      (0.8,  "mm",  "v1.1 §5.4 最小壁厚",           "[推算]"),
    "rib_min":       (1.2,  "mm",  "v1.1 §5.4 受力肋",             "[推算]"),
    "boss_min_dia":  (2.4,  "mm",  "v1.1 §5.4 螺钉柱最小直径",     "[推算]"),
    "hole_m12":      (1.4,  "mm",  "v1.1 §5.1 M1.2 螺钉孔",        "[官方]"),
    "dowel_h7":      (2.0,  "mm",  "v1.1 §5.1 定位销孔 H7",        "[官方]"),
    "clr_print":     (0.30, "mm",  "v1.1 §5.4 打印件↔打印件单边",   "[推算]"),
    "clr_metal":     (0.15, "mm",  "v1.1 §5.4 打印件↔金属件单边",   "[推算]"),
    "split_slot":    (0.6,  "mm",  "v1.1 §5.4 螺钉柱沿 Z 开槽",     "[推算]"),
    "pcb_len":       (50.0, "mm",  "v1.1 §5.1 PCB 长",             "[推算]"),
    "pcb_wid":       (12.0, "mm",  "v1.1 §5.1 PCB 宽",             "[推算]"),
    "pcb_thk":       (0.8,  "mm",  "v1.1 §5.1 PCB 厚 4层",         "[推算]"),
    "pcb_hole_edge": (2.5,  "mm",  "v1.1 §5.1 孔心到板边",         "[推算]"),
    "tc_open_w":     (9.5,  "mm",  "v1.1 §5.1 Type-C 开孔宽",       "[官网]"),
    "tc_open_h":     (3.6,  "mm",  "v1.1 §5.1 Type-C 开孔高",       "[官网]"),
    "tc_wall_min":   (1.5,  "mm",  "v1.1 §5.1 末端承力壁厚",       "[推算]"),
    "temple_h":      (7.3,  "mm",  "v1.1 §1.6.2 340档 前后厚",      "[推算]"),
    "temple_v":      (38.0, "mm",  "v1.1 §1.6.2 340档 根部净高",    "[推算]"),
    "temple_l":      (130.0,"mm",  "v1.1 §1.6.2 内腔长",           "[推算]"),
    "batt_thk":      (4.6,  "mm",  "v1.1 §1.6.1 Renata 340mAh 厚",  "[官网]"),
    "batt_v":        (23.5, "mm",  "v1.1 §1.6.1 Renata 340mAh 高",  "[官网]"),
    "batt_l":        (40.5, "mm",  "v1.1 §1.6.1 Renata 340mAh 长",  "[官网]"),
    "duct_w":        (6.0,  "mm",  "v1.1 §1.3 M10 走线槽宽",        "[推算]"),
    "duct_h":        (2.0,  "mm",  "v1.1 §1.3 M10 走线槽高",        "[推算]"),
    "oe_len":        (7.5,  "mm",  "v1.1 §1.3 M5 走鹃Ⅱ 长",         "[推算] (u1)"),
    "oe_wid":        (5.0,  "mm",  "v1.1 §1.3 M5 走鹃Ⅱ 宽",         "[推算] (u1)"),
    "oe_thk":        (4.8,  "mm",  "v1.1 §1.3 M5 走鹃Ⅱ 厚",         "[推算] (u1)"),
    "sp_len":        (14.0, "mm",  "v1.1 §1.4.5 分光组件 长",       "[推算]"),
    "sp_wid":        (10.0, "mm",  "v1.1 §1.4.5 分光组件 宽",       "[推算]"),
    "sp_thk":        (6.0,  "mm",  "v1.1 §1.4.5 分光组件 厚",       "[推算]"),
    "sp_mtol":       (0.25, "deg", "v1.1 §5.2 分光件角度公差",       "[推算]"),

    # ---- Rev A 专有键 (MECH/print/GEOM_SPEC_REVA.md §1 特征变更总表) ----
    #   verify_pack.py 的 check_reva_contract() 按 P[k][0] 与 REVA 字典比 1e-9
    #   —— 这里必须与 REVA["batt_seat_depth"/"pad_groove_depth"/"top_plate_thk"] 一致
    #   F5/F6 (⌀1.6 让过孔 / ⌀2.4 间隙孔) 同样登记进 P 表 (来源 = §特征表),
    #   不再只藏在下面的模块常量里; 常量改为从 P 表取, 避免两处漂移。
    "batt_seat_reva": (4.75, "mm", "RevA §特征表 F1 电池座净厚(非对称)", "[推算]"),
    "pad_groove_reva": (0.40, "mm", "RevA §特征表 F4 顶板压垫槽深", "[推算]"),
    "top_plate_reva":  (0.80, "mm", "RevA §特征表 F3 电池段顶板厚", "[推算]"),
    "REVA_SCREW_CLR": (1.60, "mm", "RevA §特征表 F6 M1.2 螺钉让过孔 ⌀1.60", "[推算]"),
    "REVA_CLR_HOLE":  (2.40, "mm", "RevA §特征表 F5 PCB 定位间隙孔 ⌀2.40", "[推算]"),
}


def v(key):
    return P[key][0]


# ---------------------------------------------------------------------
# Rev A 专有常量 (F5 / F6) —— **短别名, 唯一真源是上面 P 表的同名键**
#   F5/F6 已登记进 P 表 (来源: GEOM_SPEC_REVA.md §特征表), 这里不再另写数字,
#   改成从 P 表取 —— 免得 "P 表改了 / 常量忘了改" 的两处漂移。
#   ⚠️ F5/F6 与 v1.1 的 hole_m12 (⌀1.4, coupon 用) / dowel_h7 (⌀2.0, coupon 用) 是**不同的值**:
#     F6: 打印件 M1.2 螺钉孔 ⌀1.4 → ⌀1.6 **过孔** (只让过, 不定位)
#     F5: 打印件 PCB 定位销孔 ⌀2.0 → ⌀2.4 **间隙孔** (定位基准移到金属骨架)
#   契约核对: ⌀1.6 / ⌀2.4 由 verify_pack.py 的 REVA["screw_clr"] / REVA["clr_hole"]
#   + 光线投射探针实测核对 (不靠本文件的常量自证)。
# ---------------------------------------------------------------------
REVA_SCREW_CLR = v("REVA_SCREW_CLR")   # = 1.60  F6 M1.2 螺钉过孔 (让过不定位)
REVA_CLR_HOLE = v("REVA_CLR_HOLE")     # = 2.40  F5 PCB 定位间隙孔 (取代 ⌀2.0 H7 销孔)


# =====================================================================
# 网格工具 (纯 numpy —— 本机没有 trimesh / cadquery)
# =====================================================================
class Mesh:
    def __init__(self, name=""):
        self.name = name
        self.tris = []

    def prism(self, profile, axis, a0, a1):
        """profile: [(u,v)...] 逆时针凸多边形; axis 'x'→YZ面 'y'→XZ面 'z'→XY面"""
        n = len(profile)
        if n < 3:
            return

        def mp(u, vv, t):
            if axis == "x":
                return (t, u, vv)
            if axis == "y":
                return (u, t, vv)
            return (u, vv, t)

        cu = sum(p[0] for p in profile) / n
        cv = sum(p[1] for p in profile) / n
        c0 = [mp(cu, cv, a0)] + [mp(p[0], p[1], a0) for p in profile]
        c1 = [mp(cu, cv, a1)] + [mp(p[0], p[1], a1) for p in profile]
        for i in range(n):
            j = (i + 1) % n
            self.tris.append((c0[0], c0[1 + i], c0[1 + j]))
            self.tris.append((c1[0], c1[1 + j], c1[1 + i]))
            p0 = mp(profile[i][0], profile[i][1], a0)
            p1 = mp(profile[j][0], profile[j][1], a0)
            p2 = mp(profile[j][0], profile[j][1], a1)
            p3 = mp(profile[i][0], profile[i][1], a1)
            self.tris.append((p0, p1, p2))
            self.tris.append((p0, p2, p3))

    def box(self, x0, y0, z0, x1, y1, z1):
        self.prism([(y0, z0), (y1, z0), (y1, z1), (y0, z1)], "x", x0, x1)

    def cyl_z(self, cx, cy, z0, z1, r, seg=48):
        prof = [(cx + r * math.cos(2 * math.pi * i / seg),
                 cy + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]
        self.prism(prof, "z", z0, z1)

    def tube_z(self, cx, cy, z0, z1, r_out, r_in, seg=48, a0=0.0, a1=360.0):
        """圆环棱柱 (通孔); a0/a1 角度范围用于半环 (开槽螺钉柱)。
        部分弧的端面 = 径向矩形 (r_in..r_out x z0..z1), 不是扇形封口"""
        full = abs((a1 - a0) - 360.0) < 1e-6
        cnt = seg if full else seg + 1
        out, inn = [], []
        for i in range(cnt):
            a = math.radians(a0 + (a1 - a0) * (i / seg))
            out.append((cx + r_out * math.cos(a), cy + r_out * math.sin(a)))
            inn.append((cx + r_in * math.cos(a), cy + r_in * math.sin(a)))
        for i in range(seg if full else seg):
            j = (i + 1) % cnt if full else i + 1
            oi, oj, ii, ij = out[i], out[j], inn[i], inn[j]
            self.tris.append(((*oi, z0), (*oj, z0), (*oj, z1)))
            self.tris.append(((*oi, z0), (*oj, z1), (*oi, z1)))
            self.tris.append(((*ii, z0), (*ij, z1), (*ij, z0)))
            self.tris.append(((*ii, z0), (*ii, z1), (*ij, z1)))
            if full:
                self.tris.append(((*oi, z1), (*oj, z1), (*ij, z1)))
                self.tris.append(((*oi, z1), (*ij, z1), (*ii, z1)))
                self.tris.append(((*oi, z0), (*ij, z0), (*oj, z0)))
                self.tris.append(((*oi, z0), (*ii, z0), (*ij, z0)))
            else:
                # 端面: 径向矩形 (r_in..r_out) x (z0..z1)
                for (pa, pb) in ((out[0], inn[0]), (inn[-1], out[-1])):
                    p_out = (pa[0], pa[1])
                    p_in = (pb[0], pb[1])
                    self.tris.append(((*p_out, z0), (*p_in, z0), (*p_in, z1)))
                    self.tris.append(((*p_out, z0), (*p_in, z1), (*p_out, z1)))
                # 上下环面 (扇形环带)
                for i in range(seg):
                    oi, oj, ii, ij = out[i], out[i + 1], inn[i], inn[i + 1]
                    self.tris.append(((*oi, z1), (*oj, z1), (*ij, z1)))
                    self.tris.append(((*oi, z1), (*ij, z1), (*ii, z1)))
                    self.tris.append(((*oi, z0), (*ij, z0), (*oj, z0)))
                    self.tris.append(((*oi, z0), (*ii, z0), (*ij, z0)))

    def overhang(self, x0, y0, y1, z0, hyp, angle_deg, top_h=4.0):
        """悬空试样楔: 下表面斜角 = angle_deg (自水平向下), 斜面法向朝下 → 真悬空"""
        a = math.radians(angle_deg)
        dx = hyp * math.cos(a)
        dz = hyp * math.sin(a)
        H = dz + top_h
        prof = [(x0, z0 + dz), (x0 + dx, z0), (x0 + dx, z0 + H), (x0, z0 + H)]
        self.prism(prof, "y", y0, y1)
        return dx, dz

    def bounds(self):
        pts = np.array([t for tri in self.tris for t in tri], dtype=float)
        return pts.min(axis=0), pts.max(axis=0)

    def volume(self):
        tot = 0.0
        for a, b, c in self.tris:
            tot += float(np.dot(np.asarray(a), np.cross(np.asarray(b), np.asarray(c)))) / 6.0
        return tot

    def write_stl(self, path):
        with open(path, "wb") as f:
            f.write(b"\0" * 80)
            f.write(struct.pack("<I", len(self.tris)))
            for a, b, c in self.tris:
                a = np.asarray(a, float)
                b = np.asarray(b, float)
                c = np.asarray(c, float)
                n = np.cross(b - a, c - a)
                ln = float(np.linalg.norm(n))
                n = n / ln if ln > 1e-12 else np.array([0.0, 0.0, 0.0])
                f.write(struct.pack("<3f", *n))
                for p in (a, b, c):
                    f.write(struct.pack("<3f", *p))
                f.write(struct.pack("<H", 0))


# =====================================================================
# 件 1: 配合尺寸标定件 fit_coupon
# =====================================================================
WALLS = [0.4, 0.6, 0.8, 1.0, 1.2]
GAPS = [0.10, 0.15, 0.20, 0.30, 0.40, 0.50]
OVERHANGS = [30, 40, 45, 50, 60]


def build_coupon():
    """Rev A (GEOM_SPEC_REVA.md §2.5): 相对 Rev 0 **只改 F7** —— 配作孔试样加 ⌀2.4 / ⌀2.5,
    原 ⌀2.0 / 2.1 / 2.2 保留 (FDM 孔径收缩表征, 不作废)。其余特征不动。"""
    m = Mesh("fit_coupon_340")
    m.box(0, 0, 0, 150, 90, 2.0)                       # 底板 2mm

    # (1) 壁厚阶梯试样: 0.4/0.6/0.8/1.0/1.2mm, 高 12mm
    for i, t in enumerate(WALLS):
        x0 = 4 + i * 9
        m.box(x0, 4, 2.0, x0 + 8, 4 + t, 14.0)

    # (2) 间隙梳: 名义间隙 0.10/0.15/0.20/0.30/0.40/0.50 (XY 平面内)
    x = 52.0
    for g in GAPS:
        m.box(x, 4, 2.0, x + 3.0, 16, 17.0)           # 肋条 3mm 宽 15mm 高
        x += 3.0 + g
    m.box(x, 4, 2.0, x + 3.0, 16, 17.0)               # 末肋 (封住最后一档间隙)

    # (3) 螺钉柱试样 (沿 Z = FDM 层间结合最不利工况)
    z0, z1 = 2.0, 14.0
    m.cyl_z(10, 26, z0, z1, 1.5)                                        # 实心柱 (拉脱对照)
    m.tube_z(20, 26, z0, z1, 1.2, v("hole_m12") / 2)                    # ⌀2.4 未开槽
    # ⌀2.4 沿 Z 开槽 (§5.4 强制做法): 两个半环沿 X 分离 0.6mm
    m.tube_z(30 - v("split_slot") / 2, 26, z0, z1, 1.2, v("hole_m12") / 2, a0=90.0, a1=270.0)
    m.tube_z(30 + v("split_slot") / 2, 26, z0, z1, 1.2, v("hole_m12") / 2, a0=270.0, a1=450.0)
    m.tube_z(40, 26, z0, z1, 1.5, v("hole_m12") / 2)                    # ⌀3.0 未开槽
    m.tube_z(50, 26, z0, z1, 2.0, v("dowel_h7") / 2)                    # ⌀4.0 定位销柱

    # (4) 配作孔试样 (Rev A / F7): ⌀2.0/2.1/2.2 (原样保留) + ⌀2.4/2.5 (新增间隙孔试样)
    for i, d in enumerate((2.0, 2.1, 2.2, 2.4, 2.5)):
        m.tube_z(10 + i * 8, 40, z0, z1, 3.0, d / 2)

    # (5) 悬空角试样 30/40/45/50/60°
    for i, ang in enumerate(OVERHANGS):
        m.overhang(62 + i * 17, 30, 42, 2.0, 16.0, ang)

    # (6) 标定块: 5 / 10 / 20mm 阶梯
    m.box(120, 60, 2.0, 125, 80, 7.0)
    m.box(125, 60, 2.0, 130, 80, 12.0)
    m.box(130, 60, 2.0, 135, 80, 22.0)

    # (7) 波导卡槽间隙试样: 名义 0.10 / 0.12 / 0.15 单边 (§5.4)
    x = 6.0
    for g in (0.10, 0.12, 0.15):
        m.box(x, 66, 2.0, x + 8, 70, 6.0)           # 槽底 (Y 66..70)
        m.box(x, 70 + g, 2.0, x + 8, 76, 6.0)       # 对侧槽壁 → 中间形成 gap=g
        x += 14
    return m


# =====================================================================
# 件 2: 镜脚内腔检具 temple_cage (340 mAh 档)
# ---------------------------------------------------------------------
# Rev A (MECH/print/GEOM_SPEC_REVA.md §2.3 / §2.4): 严格照参考实现照抄。
#   坐标: X = 电池插入方向 (电芯自 -X 端插入, 端挡在 +X 端)
#         Y = 电池厚度 = 镜脚 H 向  (**Y 负侧 = 皮肤侧 / Y 正侧 = 顶板侧**)
#         Z = 电池高度 = 镜脚 V 向  (Z=0 = 检具底面)
#   变更: F1 座净厚非对称 4.75 · F2 皮肤侧壁 0.80 · F3 整片顶板 0.80
#         F4 压垫槽 0.40 深 (让位凹槽) · F5 PCB 间隙孔 ⌀2.4 · F6 M1.2 过孔 ⌀1.6 ×2
# =====================================================================
def build_temple_cage():
    m = Mesh("temple_cage_340")
    clr = v("clr_metal")                      # 0.15 单边 (v1.1 §5.4)
    px = v("batt_l") + 2 * clr                # 40.80 座净长 (X)
    pz = v("batt_v") + 2 * clr                # 23.80 座净高 (Z)
    w = 2.0                                  # 检具自身壁厚
    skin_w = 0.80                            # F2 皮肤侧壁厚
    plate_t = v("top_plate_reva")             # F3 电池段顶板厚 0.80
    groove = v("pad_groove_reva")             # F4 顶板内侧压垫槽深 0.40
    cell_t = v("batt_thk")                   # 4.60 电芯厚 (Renata 340mAh, v1.1 §1.6.1)

    # ---- 派生坐标 (§2.2, 照抄即可) ----
    y_floor_in = skin_w                      # 0.80 座底面 (皮肤侧内壁面)
    y_cell_top = y_floor_in + cell_t         # 5.40 电芯顶面
    y_plate_in = y_cell_top + 0.15           # 5.55 顶板内侧面 (内侧间隙 0.15, F1 非对称)
    y_plate_out = y_plate_in + plate_t       # 6.35 顶板外侧面
    y_groove_out = y_plate_in + groove       # 5.95 压垫槽底 (板内让位凹槽 → 槽区板厚 0.40)
    gz0, gz1 = 5.75, 21.75                   # 压垫槽 Z 范围 (16.00 居中)

    # --- A. 电池座 (F1..F4) ---
    m.box(0, 0, 0, px + w, y_plate_out, w)                      # A1 槽底板 (Z 0..2.0)
    m.box(0, 0, w, px, skin_w, w + pz)                           # A2 皮肤侧壁 (Y 0..0.80)
    m.box(0, y_groove_out, w, px, y_plate_out, w + pz)           # A3 顶板基体 (Y 5.95..6.35)
    m.box(0, y_plate_in, w, px, y_groove_out, gz0)              # A4 槽下边条 (Z 2.0..5.75)
    m.box(0, y_plate_in, gz1, px, y_groove_out, w + pz)         # A5 槽上边条 (Z 21.75..25.8)
    m.box(px, 0, 0, px + w, y_plate_out, w + pz + w)             # A6 端挡 (X 40.8..42.8)
    m.box(0, 0, w + pz, px + w, y_plate_out, w + pz + w)         # A7 顶盖 (Z 25.8..27.8)

    # --- B. PCB 定位孔组 (F5/F6) ---
    m.box(0, 60, 0, v("pcb_len"), 92, 2.0)                      # B1 底板 (扩到 X=50)
    m.tube_z(6, 68, 2.0, 18.0, 2.5, REVA_SCREW_CLR / 2)         # B2 M1.2 过孔 ⌀1.6 (X=6)
    m.tube_z(46, 68, 2.0, 18.0, 2.5, REVA_SCREW_CLR / 2)        # B2 M1.2 过孔 ⌀1.6 (X=46)
    m.tube_z(16, 68, 2.0, 18.0, 3.0, REVA_CLR_HOLE / 2)         # B3 PCB 定位间隙孔 ⌀2.4
    m.tube_z(26, 68, 2.0, 18.0, 3.0, 2.1 / 2)                  # B4 FDM 孔径试样 ⌀2.1
    m.tube_z(36, 68, 2.0, 18.0, 3.0, 2.2 / 2)                  # B5 FDM 孔径试样 ⌀2.2
    m.box(0, 78, 2.0, v("pcb_len"), 90, 3.0)                   # B6 PCB 定位板

    # --- C. 走线槽试样 (净截面 6 x 2mm, 长 60mm) —— Rev 0 不动 (F8) ---
    m.box(0, 100, 0, 60, 108, 2.0)                        # 槽底 (2mm)
    m.box(0, 100, 0, 60, 101, 4.0)                        # 侧壁 1
    m.box(0, 107, 0, 60, 108, 4.0)                        # 侧壁 2

    # --- D. Type-C 面板开孔试样 (开口 9.5x3.6, 四周承力壁各 1.5) ---
    ow, oh = v("tc_open_w"), v("tc_open_h")
    w = v("tc_wall_min")
    W, H = ow + 2 * w, oh + 2 * w
    m.box(0, 120, 0, w, 123.0, H)                          # 左壁
    m.box(ow + w, 120, 0, W, 123.0, H)                      # 右壁
    m.box(w, 120, 0, ow + w, 123.0, w)                      # 下壁
    m.box(w, 120, oh + w, ow + w, 123.0, H)                  # 上壁
    return m


# =====================================================================
# 件 3: 镜框光学舱托架模板 (⚠️ JBD 尺寸未到, 全推算)
# =====================================================================
def build_optical_cage():
    m = Mesh("optical_cage_TEMPLATE")
    clr = 0.20
    oel, oew, oet = v("oe_len"), v("oe_wid"), v("oe_thk")
    spl, spw, spt = v("sp_len"), v("sp_wid"), v("sp_thk")
    # 基准面 (Y=0..1): 光机与分光件共用一体托架基准
    m.box(0, 0, 0, 40, 1.0, 30)
    # 光机座 (7.5 x 4.8 x 5.0)
    m.box(2, 1.0, 2, 2 + oel + 2 * clr, 1.0 + oet, 2 + oew + 2 * clr)
    # 分光件座 (14 x 6 x 10), 串联在光机之后
    y0 = 1.0 + oet
    m.box(2, y0, 2, 2 + spl + 2 * clr, y0 + spt, 2 + spw + 2 * clr)
    # 3 点定位: 2 平面 (底面 + 侧导轨) + 1 锥 (120° V 形槽, 两块斜板)
    m.box(0, 0, 0, 40, 1.0, 2.0)            # 平面 1
    m.box(0, 0, 0, 2.0, y0 + spt, 30)       # 平面 2
    h = 4 * math.tan(math.radians(30))      # 120° V 槽: 壁与竖直成 30°
    m.prism([(18, 0), (22, 0), (18, h)], "y", 20.0, 22.0)
    m.prism([(22, 0), (26, 0), (26, h)], "y", 20.0, 22.0)
    return m


def main():
    for fn, builder in (("fit_coupon_340.stl", build_coupon),
                        ("temple_cage_340.stl", build_temple_cage),
                        ("optical_cage_TEMPLATE.stl", build_optical_cage)):
        mesh = builder()
        p = os.path.join(HERE, fn)
        mesh.write_stl(p)
        lo, hi = mesh.bounds()
        print(f"✅ {fn:<28} 三角形 {len(mesh.tris):>5}  外形 "
              f"{hi[0]-lo[0]:6.1f}×{hi[1]-lo[1]:5.1f}×{hi[2]-lo[2]:5.1f}mm  "
              f"体积 {mesh.volume()/1000:5.1f}cc  {os.path.getsize(p)/1024:4.0f}KB")
    print("\n尺寸来源 (v1.1 §x.y = MECH/MECH_BUDGET.md v1.1, 改这里必须同步改 v1.1; "
          "RevA §特征表 = MECH/print/GEOM_SPEC_REVA.md, 改这里必须同步改该文件):")
    for k, (val, unit, src, ev) in P.items():
        print(f"  {k:<15} {val:>7} {unit:<4} {src:<30} {ev}")


if __name__ == "__main__":
    main()
