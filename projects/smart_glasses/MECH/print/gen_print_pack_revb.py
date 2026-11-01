#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P2S 打样打印包生成器 —— **Rev B** (板宽 30mm / 板长 60mm / PIN-SET-2 / ISS-092 检修口)
================================================================================
为什么出 Rev B (Rev A 的几何已过期):
  Rev A (2026-10-26, MECH/print/*.stl) 的 P 表锁在 **板宽 12mm / 板长 50mm**,
  而当前基线已改:
    ① **板宽 12 → 30mm** (老板 10-29 19:16 拍板; §0 台账 11-01 20:5x 订正)
       ⇒ 板宽是 **V 向** 尺寸 (MECH/BOARD_WIDTH_15MM.md §1.2) ⇒ 镜脚净高 38.00 的吃紧点变了
    ② **板长 50 → 60mm** (ISS-100, 2026-10-28 项目总工裁)
    ③ **PCB 定位孔组 → PIN-SET-2** (hw-lead ISS-049 定版): 2×⌀2.0 H7 销孔 (P1/P2)
       + 2×⌀1.4 压紧孔 (S1/S2) ⇒ 打印件让过孔 = 2×⌀2.4 + 2×⌀1.6
       ⚠️ **PIN-SET-2 的 Y 坐标是按板宽 15mm 定的 (Y 0..15)** ⇒ 板宽 30 后 **Y 全部作废**,
          本单 X 坐标沿用 (板长 60 未变), Y 暂用 15mm 板口径并标 [待 hw-lead 重定]
    ④ **Type-C 面板试样从镜脚检具移到镜框端件** (ISS-014 决策 5: 充电板挪镜框)
    ⑤ **新增 ISS-092 检修口特征组** (通窗 / 螺钉凸台 / 磁铁沉槽 / 定位凸台 / 盖板 / 内腔量规)
       —— DECISIONS 2026-10-30 已授权排进 ISS-027 B2 批

★ 建模纪律 (本脚本自己踩过的坑, 写下来免得后人重踩):
  · 本机的 Mesh 类 **只能做并集, 没有布尔减** ⇒
      - **盲孔/沉槽必须分层建**: 下层实心 + 上层带通孔 ⇒ 合起来就是盲孔 (深度 = 上层厚)
      - **通孔在方板里** ⇒ 用 **条带法**: 沿一个方向切条带, 每条带按圆的弦宽切出空档
  · **同一件上的特征不能互相遮挡射线** —— 每条特征独占一个带, 否则自检量出来的数就是错的

★ 铁律: 本脚本 **只把已定案的数字实体化, 不改镜框方案**。
  尺寸表第 3 列自报出处; [0数据] 项只做"占位试样"并显式标注, 不当结论。

用法:  python3 MECH/print/gen_print_pack_revb.py
自证:  python3 MECH/print/verify_pack_revb.py
"""
from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from gen_print_pack import Mesh  # noqa: E402  (复用 Rev A 的网格工具, 几何算法不变)

# =====================================================================
# Rev B 尺寸表 —— (标称值, 单位, 出处, 证据等级)
# =====================================================================
P = {
    # --- 通用打印工艺 ---
    "wall_min":      (0.80, "mm", "MECH_BUDGET §5.4 最小壁厚", "[推算]"),
    "clr_print":     (0.30, "mm", "MECH_BUDGET §5.4 打印件单边公差", "[推算]"),
    "clr_metal":     (0.15, "mm", "MECH_BUDGET §5.4 打印件↔金属件单边", "[推算]"),
    "hole_m12":      (1.40, "mm", "MECH_BUDGET §5.1 M1.2 螺钉孔", "[官方]"),
    "split_slot":    (0.60, "mm", "MECH_BUDGET §5.4 螺钉柱沿 Z 开槽", "[推算]"),
    "dowel_h7":      (2.00, "mm", "MECH_BUDGET §5.1 定位销孔 H7", "[官方]"),
    # --- 镜脚内腔 (三条锁死尺寸链; ISS-092 Δ=0.00) ---
    "temple_h":      (7.30, "mm", "MECH_BUDGET §1.6.2 前后厚 (老板 10-27 Q4 锁死)", "[锁死]"),
    "temple_v":      (38.00, "mm", "MECH_BUDGET §1.6.2 根部净高", "[锁死]"),
    "temple_l":    (130.00, "mm", "MECH_BUDGET §1.6.2 内腔长", "[锁死]"),
    # --- PCB (★Rev B 变更点) ---
    "pcb_len":       (60.00, "mm", "★Rev B: 板长 60 (ISS-100 2026-10-28 裁; 原 50)", "[推算]"),
    "pcb_wid":       (30.00, "mm", "★Rev B: 板宽 30 (老板 10-29 19:16; 原 12) V向", "[推算]"),
    "pcb_thk":       (0.80, "mm", "MECH_BUDGET §5.1 4层 (★ISS-122 层数待 PCB 厂 DFM)", "[0数据]"),
    # --- PIN-SET-2 孔位 (hw-lead ISS-049 定版; Y 坐标板宽 30 后待重定) ---
    "pinset2_p1_x":  (8.00, "mm", "HW/PCB_FIXING_PINSET2.md P1 (X)", "[官方-项目内]"),
    "pinset2_p2_x": (52.00, "mm", "HW/PCB_FIXING_PINSET2.md P2 (X)", "[官方-项目内]"),
    "pinset2_s1_x":  (8.00, "mm", "HW/PCB_FIXING_PINSET2.md S1 (X)", "[官方-项目内]"),
    "pinset2_s2_x": (52.00, "mm", "HW/PCB_FIXING_PINSET2.md S2 (X)", "[官方-项目内]"),
    "pinset2_p_y":   (7.50, "mm", "PIN-SET-2 P1/P2 板宽15 口径 Y (★板宽30 后待重定)", "[0数据]"),
    "pinset2_s1_y":  (2.50, "mm", "PIN-SET-2 S1 板宽15 口径 Y (★板宽30 后待重定)", "[0数据]"),
    "pinset2_s2_y": (12.50, "mm", "PIN-SET-2 S2 板宽15 口径 Y (★板宽30 后待重定)", "[0数据]"),
    "clr_hole":      (2.40, "mm", "打印件 PCB 销孔让过 ⌀2.4 (取代 ⌀2.0 H7 销孔)", "[推算]"),
    "screw_clr":     (1.60, "mm", "打印件 M1.2/M1.4 螺钉让过孔 ⌀1.6", "[推算]"),
    # --- 电芯 (315mAh 档 = Renata 340mAh) ---
    "batt_thk":      (4.60, "mm", "MECH_BUDGET §1.6.1 Renata ICP582035PR-01 厚", "[官网]"),
    "batt_v":       (23.50, "mm", "MECH_BUDGET §1.6.1 同上 高", "[官网]"),
    "batt_l":       (40.50, "mm", "MECH_BUDGET §1.6.1 同上 长", "[官网]"),
    "batt_seat":     (4.75, "mm", "RevA §特征表 F1 电池座净厚(非对称)", "[推算]"),
    "pad_groove":    (0.40, "mm", "RevA §特征表 F4 顶板压垫槽深", "[推算]"),
    "top_plate":     (0.80, "mm", "RevA §特征表 F3 电池段顶板厚", "[推算]"),
    # --- 走线槽 ---
    "duct_w":        (6.00, "mm", "MECH_BUDGET §5.6.2 走线槽 V 向", "[推算]"),
    "duct_h":        (2.00, "mm", "MECH_BUDGET §1.3 M10 走线槽 H 向", "[推算]"),
    # --- Type-C (★移到镜框端件) ---
    "tc_open_w":     (9.50, "mm", "MECH_BUDGET §5.1 Type-C 开孔宽 (现口径)", "[官网]"),
    "tc_open_h":     (3.60, "mm", "MECH_BUDGET §5.1 Type-C 开孔高 (现口径)", "[官网]"),
    "tc_open_w2":   (10.00, "mm", "ISS-089 建议开口 10.0 (待 PM 授权, 并行试样)", "[推算]"),
    "tc_open_h2":    (4.20, "mm", "ISS-089 建议开口 4.2 (待 PM 授权, 并行试样)", "[推算]"),
    "tc_wall_min":   (1.50, "mm", "MECH_BUDGET §5.1 末端承力壁厚", "[推算]"),
    "tc_plate_t":    (3.00, "mm", "Type-C 面板试样板厚 (检具自身, 非产品件)", "[推算]"),
    # --- ISS-092 检修口 (C-1..C-15) ---
    "sp_open_x":    (10.20, "mm", "ISS-092 C-1 通窗开口 X", "[推算]"),
    "sp_open_y":     (4.60, "mm", "ISS-092 C-1 通窗开口 Y", "[推算]"),
    "sp_corner_r":   (0.80, "mm", "ISS-092 C-2 开口圆角 R0.80", "[推算]"),
    "sp_cover_x":   (13.20, "mm", "ISS-092 C-3 盖板外形 X", "[推算]"),
    "sp_cover_y":    (7.60, "mm", "ISS-092 C-3 盖板外形 Y", "[推算]"),
    "sp_cover_t":    (1.20, "mm", "ISS-092 C-3 盖板厚", "[推算]"),
    "sp_cavity":     (4.90, "mm", "ISS-092 C-5 盖板内腔深度 (板厚0.80口径)", "[推算]"),
    "sp_boss_dia":   (3.20, "mm", "ISS-092 C-10 螺钉凸台 ⌀", "[推算]"),
    "sp_boss_len":   (1.60, "mm", "ISS-092 C-10 凸台向内加厚", "[推算]"),
    "sp_mag_dia":    (4.00, "mm", "ISS-092 C-3 N35 磁铁 ⌀4.0×1.0", "[官方]"),
    "sp_mag_t":      (1.00, "mm", "ISS-092 C-3 N35 磁铁厚", "[官方]"),
    "sp_mag_depth":  (0.80, "mm", "ISS-092 磁吸沉槽深 (盖板侧, 留 0.4 底)", "[推算]"),
    "sp_pin_dia":    (1.60, "mm", "ISS-092 C-11 定位凸台 ⌀ (镜脚侧)", "[推算]"),
    "sp_pin_hole":   (1.70, "mm", "ISS-092 C-11 盖板对应孔 ⌀", "[推算]"),
    "sp_pin_pitch":  (6.00, "mm", "ISS-092 C-11 定位凸台间距", "[推算]"),
    "sp_screw":      (1.60, "mm", "ISS-092 C-3 M1.6×6 自攻螺钉", "[官方]"),
    "sp_pilot":      (1.30, "mm", "M1.6 自攻底孔 ⌀1.3 (试样, 扭矩待实测)", "[推算]"),
    "sp_screw_hole": (1.80, "mm", "盖板 M1.6 自攻让过孔 ⌀1.8", "[推算]"),
}


def v(key):
    return P[key][0]


def circle_prof(cx, cz, r, seg=64):
    return [(cx + r * math.cos(2 * math.pi * i / seg),
             cz + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]


# =====================================================================
# 条带法: 带圆孔的平板 (Mesh 只能并集, 靠条带拼出空档)
# =====================================================================
def plate_xy(m, x0, x1, y0, y1, z0, z1, holes, strips=64):
    """XY 平面上的板 (厚向 Z), 挖若干 **沿 Z 通孔** (cx, cy, r)。"""
    dy = (y1 - y0) / strips
    for s in range(strips):
        ya = y0 + s * dy
        yb = ya + dy
        cuts = []
        for (cx, cy, r) in holes:
            d = min(cy - ya, yb - cy) if ya <= cy <= yb else min(abs(ya - cy), abs(yb - cy))
            if d >= r:
                continue
            hw = math.sqrt(max(r * r - d * d, 0.0))
            cuts.append((cx - hw, cx + hw))
        cuts.sort()
        cur = x0
        for (a, b) in cuts:
            if a > cur:
                m.box(cur, ya, z0, min(a, x1), yb, z1)
            cur = max(cur, b)
        if cur < x1:
            m.box(cur, ya, z0, x1, yb, z1)


def plate_xz(m, x0, x1, z0, z1, y0, y1, rects=(), holes=(), strips=64):
    """XZ 平面上的板 (厚向 Y), 挖 **矩形通窗** (xa, xb, za, zb) 与 **圆通孔** (cx, cz, r)。"""
    dz = (z1 - z0) / strips
    for s in range(strips):
        za = z0 + s * dz
        zb = za + dz
        cuts = []
        for (xa, xb, rza, rzb) in rects:
            if zb <= rza or za >= rzb:
                continue
            cuts.append((xa, xb))
        for (cx, cz, r) in holes:
            d = min(cz - za, zb - cz) if za <= cz <= zb else min(abs(za - cz), abs(zb - cz))
            if d >= r:
                continue
            hw = math.sqrt(max(r * r - d * d, 0.0))
            cuts.append((cx - hw, cx + hw))
        cuts.sort()
        cur = x0
        for (a, b) in cuts:
            if a > cur:
                m.box(cur, y0, za, min(a, x1), y1, zb)
            cur = max(cur, b)
        if cur < x1:
            m.box(cur, y0, za, x1, y1, zb)


def blind_pocket_xy(m, x0, x1, y0, y1, z0, z1, depth, holes, strips=64):
    """盲沉槽 (沿 Z, 开口朝上): 下层实心 + 上层带通孔。"""
    plate_xy(m, x0, x1, y0, y1, z0, z1 - depth, [], strips)
    plate_xy(m, x0, x1, y0, y1, z1 - depth, z1, holes, strips)


# =====================================================================
# 布局表 —— 生成器与自检脚本共用 (防两边漂移)
#   ★ 每条特征独占一个带, 互不遮挡自检射线
# =====================================================================
L = {
    # ---- fit_coupon (底板 150 × 132) ----
    "cp_base": (150.0, 132.0),
    "cp_wall_x": 4.0,        # A 壁厚阶梯 (y 4..16)
    "cp_comb_x": 54.0,       # B 间隙梳    (y 4..16)
    "cp_boss_x": (14.0, 24.0, 34.0, 44.0, 54.0),    # C 螺钉柱 (y 26)
    "cp_fit_x": (68.0, 76.0, 84.0, 92.0, 100.0),   # D 配作孔试样 (y 31)
    "cp_pilot_col": 104.0,   # E M1.6 拉脱柱 (y 26)
    "cp_pilot_x": (118.0, 128.0, 138.0),           # E M1.6 底孔 (y 26)
    "cp_over_x": 4.0,        # F 悬空角 (y 44..56)
    "cp_block_x": 95.0,      # G 标定块 (y 44..64)
    "cp_thk_x": 44.0,        # H 板厚三档 (y 116..122)
    "cp_wave_x": 4.0,        # I 波导卡槽 (y 66..76)
    "cp_cover_x": 4.0,       # J 盖板 (y 116..123.6)
    "cp_gauge_x": 20.0,      # K 内腔量规 (y 116..128)
    "cp_pcb_x": 4.0,         # L PCB 样板 60×30 (y 84..114)
    "cp_vasm_x": 68.0,       # M V 向装配试样 (y 84..114)
    "cp_vcomb_x": 68.0,      # N V 余量间隙梳 (y 116..126)
    "cp_vcomb_gaps": (1.0, 1.4, 1.8, 2.0, 2.2),   # N 梳齿名义间隙
    # ---- temple_cage ----
    "tc_by0": 60.0,          # B PCB 定位板 (Y 60..90)
    "tc_thk_y": 92.0,        # B' 板厚三档 (Y 92..98)
    "tc_duct_y": 100.0,      # C 走线槽 (Y 100..108)
    "tc_wall_y": 120.0,      # D 检修口壁 (Y 120..)
    "tc_wall_t": 0.80,
    "tc_win_x0": 6.0,        # D 通窗起点 X
    "tc_win_z0": 8.0,        # D 通窗起点 Z
}

# =====================================================================
# 件 1: 配合尺寸标定件
# =====================================================================
WALLS = [0.4, 0.6, 0.8, 1.0, 1.2]
GAPS = [0.10, 0.15, 0.20, 0.30, 0.40, 0.50]
OVERHANGS = [30, 40, 45, 50, 60]


def build_coupon():
    """Rev A 特征 (1)~(7) 原样保留 + Rev B 新增 (8)~(13)。"""
    m = Mesh("fit_coupon_revb")
    m.box(0, 0, 0, L["cp_base"][0], L["cp_base"][1], 2.0)          # 底板 2mm

    # (1) 壁厚阶梯
    for i, t in enumerate(WALLS):
        x0 = L["cp_wall_x"] + i * 9
        m.box(x0, 4, 2.0, x0 + 8, 4 + t, 14.0)

    # (2) 间隙梳
    x = L["cp_comb_x"]
    for g in GAPS:
        m.box(x, 4, 2.0, x + 3.0, 16, 17.0)
        x += 3.0 + g
    m.box(x, 4, 2.0, x + 3.0, 16, 17.0)

    # (3) 螺钉柱试样 (沿 Z = 层间结合最不利)
    z0, z1 = 2.0, 14.0
    m.cyl_z(L["cp_boss_x"][0], 26, z0, z1, 1.5)
    m.tube_z(L["cp_boss_x"][1], 26, z0, z1, 1.2, v("hole_m12") / 2)
    m.tube_z(L["cp_boss_x"][2] - v("split_slot") / 2, 26, z0, z1, 1.2, v("hole_m12") / 2,
             a0=90.0, a1=270.0)
    m.tube_z(L["cp_boss_x"][2] + v("split_slot") / 2, 26, z0, z1, 1.2, v("hole_m12") / 2,
             a0=270.0, a1=450.0)
    m.tube_z(L["cp_boss_x"][3], 26, z0, z1, 1.5, v("hole_m12") / 2)
    m.tube_z(L["cp_boss_x"][4], 26, z0, z1, 2.0, v("dowel_h7") / 2)

    # (4) 配作孔试样 (Rev A F7)
    for i, d in enumerate((2.0, 2.1, 2.2, 2.4, 2.5)):
        m.tube_z(L["cp_fit_x"][i], 31, z0, z1, 3.0, d / 2)

    # (5) 悬空角试样
    for i, ang in enumerate(OVERHANGS):
        m.overhang(L["cp_over_x"] + i * 17, 44, 56, 2.0, 16.0, ang)

    # (6) 标定块
    m.box(L["cp_block_x"], 44, 2.0, L["cp_block_x"] + 5, 64, 7.0)
    m.box(L["cp_block_x"] + 5, 44, 2.0, L["cp_block_x"] + 10, 64, 12.0)
    m.box(L["cp_block_x"] + 10, 44, 2.0, L["cp_block_x"] + 15, 64, 22.0)

    # (7) 波导卡槽间隙试样
    x = L["cp_wave_x"]
    for g in (0.10, 0.12, 0.15):
        m.box(x, 66, 2.0, x + 8, 70, 6.0)
        m.box(x, 70 + g, 2.0, x + 8, 76, 6.0)
        x += 14

    # (8) M1.6 自攻底孔 + 拉脱试样柱
    m.cyl_z(L["cp_pilot_col"], 26, 2.0, 20.0, 2.2)
    for i, d in enumerate((1.2, 1.3, 1.4)):
        m.tube_z(L["cp_pilot_x"][i], 26, 2.0, 14.0, 3.0, d / 2)

    # (9) 板厚三档试样 (ISS-122 板厚区间兑现物)
    for i, t in enumerate((0.41, 0.80, 1.22)):
        m.box(L["cp_thk_x"] + i * 8.0, 116, 2.0, L["cp_thk_x"] + 6.0 + i * 8.0, 122, 2.0 + t)

    # (10) ISS-092 检修口盖板
    #      盖板 13.20 × 7.60 × 1.20, 分两层:
    #        下层 z 2.0..2.4  —— 定位孔 ×2 (⌀1.70, 间距 6.00) + 自攻让过孔 ⌀1.80 (全通)
    #        上层 z 2.4..3.2  —— 同上的通孔 + 磁吸盲沉槽 ×2 (⌀4.00 深 0.80, 开口朝上)
    #      ⇒ 定位孔/自攻孔是 **全通孔** (上下两层都挖), 磁吸槽是 **盲槽** (只有上层挖)
    cx0, cy0 = L["cp_cover_x"], 116.0
    cz0, cz1 = 2.0, 2.0 + v("sp_cover_t")
    thru = [(cx0 + (v("sp_cover_x") - v("sp_pin_pitch")) / 2, cy0 + 1.60, v("sp_pin_hole") / 2),
            (cx0 + (v("sp_cover_x") + v("sp_pin_pitch")) / 2, cy0 + 1.60, v("sp_pin_hole") / 2),
            (cx0 + v("sp_cover_x") / 2, cy0 + 1.60, v("sp_screw_hole") / 2)]
    mag = [(cx0 + 3.30, cy0 + 5.00, v("sp_mag_dia") / 2),
           (cx0 + 9.90, cy0 + 5.00, v("sp_mag_dia") / 2)]
    plate_xy(m, cx0, cx0 + v("sp_cover_x"), cy0, cy0 + v("sp_cover_y"),
             cz0, cz1 - v("sp_mag_depth"), thru)
    plate_xy(m, cx0, cx0 + v("sp_cover_x"), cy0, cy0 + v("sp_cover_y"),
             cz1 - v("sp_mag_depth"), cz1, thru + mag)

    # (11) 盖板内腔量规: 底板 20×12×1.2 + 边框高 4.90 (开口 13.20×7.60 向上通)
    gx0, gy0 = L["cp_gauge_x"], 116.0
    gw, gh = 20.0, 12.0
    m.box(gx0, gy0, 2.0, gx0 + gw, gy0 + gh, 3.2)                    # 底板
    cxL, cxR = gx0 + (gw - v("sp_cover_x")) / 2, gx0 + (gw + v("sp_cover_x")) / 2
    cyB, cyT = gy0 + (gh - v("sp_cover_y")) / 2, gy0 + (gh + v("sp_cover_y")) / 2
    m.box(gx0, gy0, 3.2, cxL, gy0 + gh, 3.2 + v("sp_cavity"))        # 左框
    m.box(cxR, gy0, 3.2, gx0 + gw, gy0 + gh, 3.2 + v("sp_cavity"))   # 右框
    m.box(cxL, gy0, 3.2, cxR, cyB, 3.2 + v("sp_cavity"))             # 下框
    m.box(cxL, cyT, 3.2, cxR, gy0 + gh, 3.2 + v("sp_cavity"))        # 上框

    # (12) PCB 样板 60×30 + PIN-SET-2 让过孔
    px0, py0 = L["cp_pcb_x"], 84.0
    pz0, pz1 = 2.0, 2.0 + v("pcb_thk")
    holes = [(px0 + v("pinset2_p1_x"), py0 + v("pinset2_p_y"), v("clr_hole") / 2),
             (px0 + v("pinset2_p2_x"), py0 + v("pinset2_p_y"), v("clr_hole") / 2),
             (px0 + v("pinset2_s1_x"), py0 + v("pinset2_s1_y"), v("screw_clr") / 2),
             (px0 + v("pinset2_s2_x"), py0 + v("pinset2_s2_y"), v("screw_clr") / 2)]
    plate_xy(m, px0, px0 + v("pcb_len"), py0, py0 + v("pcb_wid"), pz0, pz1, holes)

    # (13) V 向装配试样 (板宽 30 + 走线槽 6 = 36.00 vs 净高 38.00) + V 余量间隙梳
    ax, az = L["cp_vasm_x"], 84.0
    plate_xy(m, ax, ax + 60.0, az, az + v("pcb_wid"), 2.0, 2.0 + v("pcb_thk"), [])
    m.box(ax + 60.0, az, 2.0, ax + 60.6, az + v("duct_w"), 4.0)
    m.box(ax + 60.0, az + v("duct_w"), 2.0, ax + 60.6, az + v("pcb_wid"), 4.0)
    cx = L["cp_vcomb_x"]
    for g in L["cp_vcomb_gaps"]:
        m.box(cx, 116, 2.0, cx + 2.0, 126, 16.0)
        cx += 2.0 + g
    return m


# =====================================================================
# 件 2: 镜脚内腔检具 (Rev B)
# =====================================================================
def build_temple_cage():
    m = Mesh("temple_cage_revb")
    clr = v("clr_metal")
    px = v("batt_l") + 2 * clr
    pz = v("batt_v") + 2 * clr
    w = 2.0
    skin_w = 0.80
    plate_t = v("top_plate")
    groove = v("pad_groove")
    cell_t = v("batt_thk")

    y_floor_in = skin_w
    y_cell_top = y_floor_in + cell_t
    y_plate_in = y_cell_top + 0.15
    y_plate_out = y_plate_in + plate_t
    y_groove_out = y_plate_in + groove
    gz0, gz1 = 5.75, 21.75

    # --- A. 电池座 (与 Rev A 一致: F1..F4) ---
    m.box(0, 0, 0, px + w, y_plate_out, w)
    m.box(0, 0, w, px, skin_w, w + pz)
    m.box(0, y_groove_out, w, px, y_plate_out, w + pz)
    m.box(0, y_plate_in, w, px, y_groove_out, gz0)
    m.box(0, y_plate_in, gz1, px, y_groove_out, w + pz)
    m.box(px, 0, 0, px + w, y_plate_out, w + pz + w)
    m.box(0, 0, w + pz, px + w, y_plate_out, w + pz + w)

    # --- B. PCB 定位板 (★Rev B: 板长 60 × 板宽 30 + PIN-SET-2 四孔) ---
    by0 = L["tc_by0"]
    plate_xy(m, 0, v("pcb_len"), by0, by0 + v("pcb_wid"), 0.0, 2.0,
             [(v("pinset2_p1_x"), by0 + v("pinset2_p_y"), v("clr_hole") / 2),
              (v("pinset2_p2_x"), by0 + v("pinset2_p_y"), v("clr_hole") / 2),
              (v("pinset2_s1_x"), by0 + v("pinset2_s1_y"), v("screw_clr") / 2),
              (v("pinset2_s2_x"), by0 + v("pinset2_s2_y"), v("screw_clr") / 2)])
    # FDM 孔径试样 (Rev A 表征试样, 保留)
    m.tube_z(26.0, by0 + 22.0, 2.0, 18.0, 3.0, 2.1 / 2)
    m.tube_z(36.0, by0 + 22.0, 2.0, 18.0, 3.0, 2.2 / 2)
    # 板厚三档试样 (ISS-122)
    for i, t in enumerate((0.41, 0.80, 1.22)):
        m.box(2.0 + i * 8.0, L["tc_thk_y"], 2.0, 6.0 + i * 8.0, L["tc_thk_y"] + 6.0, 2.0 + t)

    # --- C. 走线槽试样 (净截面 6 × 2) ---
    dy = L["tc_duct_y"]
    m.box(0, dy, 0, 60, dy + 8, 2.0)
    m.box(0, dy, 0, 60, dy + 1, 4.0)
    m.box(0, dy + 7, 0, 60, dy + 8, 4.0)

    # --- D. ISS-092 检修口壁试样 (镜脚外侧面, 壁厚 0.8, 板面在 XZ 平面) ---
    wx = L["tc_wall_y"]
    wall_t = L["tc_wall_t"]
    ox, oy = v("sp_open_x"), v("sp_open_y")
    win_x0, win_z0 = L["tc_win_x0"], L["tc_win_z0"]
    # 壁: 矩形通窗 (10.20 × 4.60) + 磁铁沉槽通孔 ⌀4.00 ×2 (沉槽深度由盖板侧盲槽试样承担)
    mag_x = (2.0 + v("sp_mag_dia") / 2, 6.0 + ox + 2.0 + v("sp_mag_dia") / 2)
    plate_xz(m, 0, 24, 0, 20, wx, wx + wall_t,
             rects=((win_x0, win_x0 + ox, win_z0, win_z0 + oy),),
             holes=((mx, win_z0 + oy / 2, v("sp_mag_dia") / 2) for mx in mag_x))
    # 螺钉凸台 ⌀3.20 (沿 +Y 凸出壁面 1.60) —— 圆柱体
    bcx, bcz = win_x0 + ox / 2, win_z0 + oy / 2
    m.prism(circle_prof(bcx, bcz, v("sp_boss_dia") / 2), "y",
            wx + wall_t, wx + wall_t + v("sp_boss_len"))
    # 定位凸台 2×⌀1.60 高 0.60, 间距 6.00 (沿 +Y 凸出壁面)
    for dx in (9.0, 15.0):
        m.prism(circle_prof(dx, bcz, v("sp_pin_dia") / 2), "y",
                wx + wall_t, wx + wall_t + 0.6)
    return m


# =====================================================================
# 件 3: 镜框端件 Type-C 面板试样 (★Rev A 从镜脚检具移到这里)
# =====================================================================
def build_frame_typec():
    """面板在 X-Z 平面, 厚度沿 Y (3.00 检具板厚)"""
    m = Mesh("frame_typec_coupon_revb")
    w = v("tc_wall_min")
    t = v("tc_plate_t")
    for (x0, ow, oh, _name) in ((0.0, v("tc_open_w"), v("tc_open_h"), "现口径"),
                                (20.0, v("tc_open_w2"), v("tc_open_h2"), "ISS-089 建议口径")):
        W, H = ow + 2 * w, oh + 2 * w
        m.box(x0, 0, 0, x0 + w, t, H)
        m.box(x0 + ow + w, 0, 0, x0 + W, t, H)
        m.box(x0 + w, 0, 0, x0 + ow + w, t, w)
        m.box(x0 + w, 0, oh + w, x0 + ow + w, t, H)
    return m


def main():
    jobs = (("fit_coupon_revb.stl", build_coupon),
            ("temple_cage_revb.stl", build_temple_cage),
            ("frame_typec_coupon_revb.stl", build_frame_typec))
    for fn, builder in jobs:
        mesh = builder()
        p = os.path.join(HERE, fn)
        mesh.write_stl(p)
        lo, hi = mesh.bounds()
        print(f"✅ {fn:<30} 三角形 {len(mesh.tris):>5}  外形 "
              f"{hi[0]-lo[0]:6.1f}×{hi[1]-lo[1]:5.1f}×{hi[2]-lo[2]:5.1f}mm  "
              f"体积 {mesh.volume()/1000:5.1f}cc  {os.path.getsize(p)/1024:4.0f}KB")
    print("\nRev B 尺寸来源:")
    for k, (val, unit, src, ev) in P.items():
        print(f"  {k:<16} {val:>7} {unit:<3} {src:<52} {ev}")
    print("\n★ optical_cage_TEMPLATE.stl **本单不动** (走鹃Ⅱ 三维尺寸 u1 未到 ⇒ 字节必须不变)")


if __name__ == "__main__":
    main()
