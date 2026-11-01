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
    "sp_pin_dia":    (1.60, "mm", "ISS-092 C-11 定位凸台 ⌀ (镜脚侧)", "[推算]"),
    "sp_pin_hole":   (1.70, "mm", "ISS-092 C-11 盖板对应孔 ⌀", "[推算]"),
    "sp_pin_pitch":  (6.00, "mm", "ISS-092 C-11 定位凸台间距", "[推算]"),
    "sp_screw":      (1.60, "mm", "ISS-092 C-3 M1.6×6 自攻螺钉", "[官方]"),
    "sp_pilot":      (1.30, "mm", "M1.6 自攻底孔 ⌀1.3 (试样, 扭矩待实测)", "[推算]"),
}


def v(key):
    return P[key][0]


def circle_prof(cx, cz, r, seg=48):
    return [(cx + r * math.cos(2 * math.pi * i / seg),
             cz + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]


# =====================================================================
# 件 1: 配合尺寸标定件 (Rev A 特征全留 + Rev B 新增)
# =====================================================================
WALLS = [0.4, 0.6, 0.8, 1.0, 1.2]
GAPS = [0.10, 0.15, 0.20, 0.30, 0.40, 0.50]
OVERHANGS = [30, 40, 45, 50, 60]


def build_coupon():
    """Rev A 全部特征 (1~7) 原样保留 + Rev B 新增 (8~11):
       8) PCB 60×30 样板 + PIN-SET-2 让过孔组  9) 检修口盖板 + 内腔量规
       10) M1.6 自攻底孔试样  11) 板宽 30 的 V 向装配试样 (V 余量 2.00 的兑现物)"""
    m = Mesh("fit_coupon_revb")
    m.box(0, 0, 0, 150, 90, 2.0)                       # 底板 2mm (Rev A 同)

    # (1) 壁厚阶梯
    for i, t in enumerate(WALLS):
        x0 = 4 + i * 9
        m.box(x0, 4, 2.0, x0 + 8, 4 + t, 14.0)

    # (2) 间隙梳
    x = 52.0
    for g in GAPS:
        m.box(x, 4, 2.0, x + 3.0, 16, 17.0)
        x += 3.0 + g
    m.box(x, 4, 2.0, x + 3.0, 16, 17.0)

    # (3) 螺钉柱试样 (沿 Z = 层间结合最不利)
    z0, z1 = 2.0, 14.0
    m.cyl_z(10, 26, z0, z1, 1.5)
    m.tube_z(20, 26, z0, z1, 1.2, v("hole_m12") / 2)
    m.tube_z(30 - v("split_slot") / 2, 26, z0, z1, 1.2, v("hole_m12") / 2, a0=90.0, a1=270.0)
    m.tube_z(30 + v("split_slot") / 2, 26, z0, z1, 1.2, v("hole_m12") / 2, a0=270.0, a1=450.0)
    m.tube_z(40, 26, z0, z1, 1.5, v("hole_m12") / 2)
    m.tube_z(50, 26, z0, z1, 2.0, v("dowel_h7") / 2)

    # (4) 配作孔试样 (Rev A F7: ⌀2.0/2.1/2.2 + ⌀2.4/2.5)
    for i, d in enumerate((2.0, 2.1, 2.2, 2.4, 2.5)):
        m.tube_z(10 + i * 8, 40, z0, z1, 3.0, d / 2)

    # (5) 悬空角试样
    for i, ang in enumerate(OVERHANGS):
        m.overhang(62 + i * 17, 30, 42, 2.0, 16.0, ang)

    # (6) 标定块
    m.box(120, 60, 2.0, 125, 80, 7.0)
    m.box(125, 60, 2.0, 130, 80, 12.0)
    m.box(130, 60, 2.0, 135, 80, 22.0)

    # (7) 波导卡槽间隙试样
    x = 6.0
    for g in (0.10, 0.12, 0.15):
        m.box(x, 66, 2.0, x + 8, 70, 6.0)
        m.box(x, 70 + g, 2.0, x + 8, 76, 6.0)
        x += 14

    # ===== Rev B 新增 =====
    # (8) PCB 60×30 样板 + PIN-SET-2 让过孔组 (X 沿板坐标, Y = 板宽方向)
    #     位置: 样板占 X 4..64 / Y 4..34, 板坐标 X = 样板X-4, 板Y = 样板Y-4
    px0, py0 = 4.0, 4.0
    m.box(px0, py0, 2.0, px0 + v("pcb_len"), py0 + v("pcb_wid"), 2.0 + v("pcb_thk"))
    for bx, by, dia, name in (
            (v("pinset2_p1_x"), v("pinset2_p_y"), v("clr_hole"), "P1 销孔让过 ⌀2.4"),
            (v("pinset2_p2_x"), v("pinset2_p_y"), v("clr_hole"), "P2 销孔让过 ⌀2.4"),
            (v("pinset2_s1_x"), v("pinset2_s1_y"), v("screw_clr"), "S1 压紧孔让过 ⌀1.6"),
            (v("pinset2_s2_x"), v("pinset2_s2_y"), v("screw_clr"), "S2 压紧孔让过 ⌀1.6")):
        m.tube_z(px0 + bx, py0 + by, 2.0, 2.0 + v("pcb_thk"), 3.2, dia / 2)
    # (8b) 板边 4 角工艺边 0.50 试样 (板框规则)
    m.box(px0 + 0.5, py0 + 0.5, 2.0 + v("pcb_thk"), px0 + 1.0, py0 + 1.0, 2.0 + v("pcb_thk") + 0.4)

    # (9) ISS-092 检修口盖板 + 内腔量规
    cx0, cy0 = 70.0, 4.0
    m.box(cx0, cy0, 2.0, cx0 + v("sp_cover_x"), cy0 + v("sp_cover_y"), 2.0 + v("sp_cover_t"))
    # 盖板磁吸沉槽 (N35 ⌀4.0 深 1.0 → 沉 0.8 留 0.4 底)
    for dx in (3.0, v("sp_cover_x") - 3.0 - v("sp_mag_dia")):
        m.tube_z(cx0 + dx + v("sp_mag_dia") / 2, cy0 + v("sp_cover_y") / 2,
                 2.0 + v("sp_cover_t") - 0.8, 2.0 + v("sp_cover_t"),
                 v("sp_mag_dia") / 2, v("sp_mag_dia") / 2 - 0.001)
    # 盖板定位孔 ⌀1.70 ×2, 间距 6.00
    for dx in ((v("sp_cover_x") - v("sp_pin_pitch")) / 2,
               (v("sp_cover_x") + v("sp_pin_pitch")) / 2):
        m.tube_z(cx0 + dx, cy0 + 1.6, 2.0, 2.0 + v("sp_cover_t"), 2.4, v("sp_pin_hole") / 2)
    # 盖板螺钉过孔 ⌀1.8 (M1.6 自攻)
    m.tube_z(cx0 + v("sp_cover_x") / 2, cy0 + v("sp_cover_y") - 1.6, 2.0, 2.0 + v("sp_cover_t"),
             2.4, 0.9)
    # (9b) 盖板内腔量规: 13.20×7.60 开口, 深 4.90 (量"盖板坐在外表面后到 PCB 焊盘面"的距离)
    gx0, gy0 = 86.0, 4.0
    m.box(gx0, gy0, 2.0, gx0 + 20.0, gy0 + 12.0, 2.0 + 1.2)                    # 量规底
    for (x0, x1, y0, y1) in (
            (gx0, gx0 + (20.0 - v("sp_cover_x")) / 2, gy0, gy0 + 12.0),
            (gx0 + (20.0 + v("sp_cover_x")) / 2, gx0 + 20.0, gy0, gy0 + 12.0)):
        m.box(x0, y0, 2.0 + 1.2, x1, y1, 2.0 + 1.2 + v("sp_cavity"))           # 侧壁
    for (y0b, y1b) in ((gy0, gy0 + (12.0 - v("sp_cover_y")) / 2),
                       (gy0 + (12.0 + v("sp_cover_y")) / 2, gy0 + 12.0)):
        m.box(gx0 + (20.0 - v("sp_cover_x")) / 2, y0b, 2.0 + 1.2,
              gx0 + (20.0 + v("sp_cover_x")) / 2, y1b, 2.0 + 1.2 + v("sp_cavity"))

    # (10) M1.6 自攻底孔试样 (M1.6 旋入塑料的底孔实测 + 拉脱力试样柱)
    m.cyl_z(115, 8, 2.0, 20.0, 2.2)                    # 柱 (拉脱试样)
    for i, d in enumerate((1.2, 1.3, 1.4)):             # 底孔 ⌀1.2/1.3/1.4
        m.tube_z(122 + i * 8, 8, 2.0, 14.0, 3.0, d / 2)

    # (11) 板宽 30 的 V 向装配试样: 板宽 30 + 走线槽 6 = 36.00 vs 净高 38.00
    #      ⇒ 做 2.00mm 名义间隙的梳 (量 V 余量到底能不能装进)
    ax, az = 4.0, 40.0
    m.box(ax, az, 2.0, ax + 60.0, az + v("pcb_wid"), 2.0 + v("pcb_thk"))       # 板 (V 30)
    m.box(ax + 60.0, az, 2.0, ax + 60.0 + 0.6, az + v("duct_w"), 2.0 + 2.0)    # 走线槽壁
    m.box(ax + 60.0, az + v("duct_w"), 2.0, ax + 60.0 + 0.6, az + v("pcb_wid"), 2.0 + 2.0)
    for i, g in enumerate((1.0, 1.4, 1.8, 2.0, 2.2)):                        # V 余量间隙梳
        m.box(ax + 62.0 + i * 6.0, az, 2.0, ax + 64.0 + i * 6.0, az + 4.0, 2.0 + 12.0)
        if i:
            pass
    return m


# =====================================================================
# 件 2: 镜脚内腔检具 (Rev B) —— 电池座 + PCB 定位组 (PIN-SET-2) + 检修口壁试样
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

    # --- A. 电池座 (与 Rev A 逐字节一致: F1..F4) ---
    m.box(0, 0, 0, px + w, y_plate_out, w)
    m.box(0, 0, w, px, skin_w, w + pz)
    m.box(0, y_groove_out, w, px, y_plate_out, w + pz)
    m.box(0, y_plate_in, w, px, y_groove_out, gz0)
    m.box(0, y_plate_in, gz1, px, y_groove_out, w + pz)
    m.box(px, 0, 0, px + w, y_plate_out, w + pz + w)
    m.box(0, 0, w + pz, px + w, y_plate_out, w + pz + w)

    # --- B. PCB 定位组 (★Rev B: 板长 60 + PIN-SET-2 四孔) ---
    #  板坐标 X → 检具 X (板长 60); 板宽 Y → 检具 Y (板宽 30, 起点 Y=60)
    by0 = 60.0
    m.box(0, by0, 0, v("pcb_len"), by0 + v("pcb_wid"), 2.0)                 # B1 底板
    for bx, by, dia in (
            (v("pinset2_p1_x"), v("pinset2_p_y"), v("clr_hole")),
            (v("pinset2_p2_x"), v("pinset2_p_y"), v("clr_hole")),
            (v("pinset2_s1_x"), v("pinset2_s1_y"), v("screw_clr")),
            (v("pinset2_s2_x"), v("pinset2_s2_y"), v("screw_clr"))):
        m.tube_z(bx, by0 + by, 2.0, 18.0, 3.2, dia / 2)
    # FDM 孔径试样 (保留 Rev A 的表征试样)
    m.tube_z(26.0, by0 + 8.0, 2.0, 18.0, 3.0, 2.1 / 2)
    m.tube_z(36.0, by0 + 8.0, 2.0, 18.0, 3.0, 2.2 / 2)
    # B6 PCB 定位板 (板厚试样: 0.41 / 0.80 / 1.22 三档, ★ISS-122 板厚区间兑现)
    for i, t in enumerate((0.41, 0.80, 1.22)):
        m.box(0, by0 + 20.0 + i * 6.0, 2.0, v("pcb_len"), by0 + 24.0 + i * 6.0, 2.0 + t)

    # --- C. 走线槽试样 (净截面 6 × 2) ---
    m.box(0, 100, 0, 60, 108, 2.0)
    m.box(0, 100, 0, 60, 101, 4.0)
    m.box(0, 107, 0, 60, 108, 4.0)

    # --- D. ISS-092 检修口壁试样 (镜脚外侧面) ---
    #  布局: 壁厚 0.8 (Y 向), 通窗 10.20(X) × 4.60(Z), 螺钉凸台 ⌀3.20 向内加厚 1.60,
    #  磁铁沉槽 (⌀4.0), 定位凸台 2×⌀1.60 间距 6.00
    dx0, dy0, dz0 = 0.0, 110.0, 0.0
    wall_t = 0.8
    ox, oy = v("sp_open_x"), v("sp_open_y")
    # 壁 (绕开孔的 4 块)
    m.box(dx0, dy0, dz0, dx0 + 6.0, dy0 + wall_t, dz0 + 20.0)
    m.box(dx0 + 6.0 + ox, dy0, dz0, dx0 + 24.0, dy0 + wall_t, dz0 + 20.0)
    m.box(dx0 + 6.0, dy0, dz0, dx0 + 6.0 + ox, dy0 + wall_t, dz0 + 8.0)
    m.box(dx0 + 6.0, dy0, dz0 + 8.0 + oy, dx0 + 6.0 + ox, dy0 + wall_t, dz0 + 20.0)
    # 螺钉凸台 (⌀3.20, 向内 = +Y, 加厚 1.60)
    m.prism(circle_prof(dx0 + 6.0 + ox / 2, dz0 + 8.0 + oy / 2, v("sp_boss_dia") / 2),
            "y", dy0 + wall_t, dy0 + wall_t + v("sp_boss_len"))
    # 自攻底孔 ⌀1.3 (M1.6)
    m.prism(circle_prof(dx0 + 6.0 + ox / 2, dz0 + 8.0 + oy / 2, v("sp_pilot") / 2),
            "y", dy0 + wall_t, dy0 + wall_t + v("sp_boss_len"))
    # 磁铁沉槽 (⌀4.0 深 1.0, 座在镜脚侧壁上 —— 沉槽做 1.0 深 ⇒ 壁厚 0.8 需局部加厚 1.2)
    for dx in (2.0, 6.0 + ox + 2.0):
        m.prism(circle_prof(dx0 + dx + v("sp_mag_dia") / 2, dz0 + 8.0 + oy / 2,
                            v("sp_mag_dia") / 2),
                "y", dy0 + wall_t + 1.2, dy0 + wall_t + 1.2 + v("sp_mag_t"))
        m.prism(circle_prof(dx0 + dx + v("sp_mag_dia") / 2, dz0 + 8.0 + oy / 2,
                            v("sp_mag_dia") / 2),
                "y", dy0 + wall_t, dy0 + wall_t + 1.2)
    # 定位凸台 2×⌀1.60 高 0.60, 间距 6.00
    for dx in (dx0 + 10.0, dx0 + 16.0):
        m.prism(circle_prof(dx, dz0 + 8.0 + oy / 2, v("sp_pin_dia") / 2),
                "y", dy0 + wall_t, dy0 + wall_t + 0.6)
    return m


# =====================================================================
# 件 3: 镜框端件 Type-C 面板试样 (★Rev A 从镜脚检具移到这里)
# =====================================================================
def build_frame_typec():
    m = Mesh("frame_typec_coupon_revb")
    w = v("tc_wall_min")
    # (a) 现口径 9.5 × 3.6
    ow, oh = v("tc_open_w"), v("tc_open_h")
    W, H = ow + 2 * w, oh + 2 * w
    m.box(0, 0, 0, w, W, H)
    m.box(ow + w, 0, 0, W, W, H)
    m.box(w, 0, 0, ow + w, W, w)
    m.box(w, 0, oh + w, ow + w, W, H)
    # (b) ISS-089 建议口径 10.0 × 4.2 (并行试样, 待 PM 授权后二选一)
    ox0 = 20.0
    ow2, oh2 = v("tc_open_w2"), v("tc_open_h2")
    W2, H2 = ow2 + 2 * w, oh2 + 2 * w
    m.box(ox0, 0, 0, ox0 + w, W2, H2)
    m.box(ox0 + ow2 + w, 0, 0, ox0 + W2, W2, H2)
    m.box(ox0 + w, 0, 0, ox0 + ow2 + w, W2, w)
    m.box(ox0 + w, 0, oh2 + w, ox0 + ow2 + w, W2, H2)
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
