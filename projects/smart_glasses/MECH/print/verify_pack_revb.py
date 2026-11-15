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

★ 坑 ⑤ (ISS-218 第三档实测踩到, 补记): **盒端面是三角扇, 扇心会被 4 个三角形同时命中**。
  盒 (x0,x1,y0,y1,z0,z1) 的 ±X 端面由 "扇心 (mid_y, mid_z) + 4 个角点" 的 4 个三角形拼成;
  探针若落在 **扇心 (mid_y, mid_z)** 上, 射线会同时命中这 4 个三角形 ⇒ 命中数由 1 变 4
  (偶数) ⇒ **奇偶判内外直接翻车** (本轮 5 个点真踩到了)。
  ⇒ 纪律: **互验探针的 (y,z) 必须避开每个被穿越盒的 (mid_y, mid_z)**;
    上面的 `frame_typec_tier3` 采样点刻意避开了所有扇心 (如 (6.75, 4.20, 1.5) 而不是
    (6.75, 3.90, 1.5))。

⚠️ 口径 (与 verify_pack.py 一致, 不许误读):
  本脚本证明的是 **模型/规格层的一致性** (STL == 规格数字),
  **不能** 替代 M-PRINT (实物打印件实测尺寸) —— 实物还有 FDM 工艺偏差
  (孔径收缩 / 层纹 / 收缩率 / PA-CF 吸湿 24h 后尺寸变化)。
  ⇒ `state/measurements.yaml` 的 M-PRINT 仍为 [推算]/未测, 阶段门 G2 不认 (符合设计意图)。

用法: python3 MECH/print/verify_pack_revb.py
      python3 MECH/print/verify_pack_revb.py --selftest    # ★反向用例 (ISS-218 加的)
退出码: 0 = 全部一致; 1 = 有偏差
"""
from __future__ import annotations

import os
import re
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import print_model_revb as PM  # noqa: E402
from gen_print_pack_revb import (GAPS, L, OVERHANGS, P, WALLS,  # noqa: E402
                                 build_coupon, build_frame_typec,
                                 build_frame_typec_tier3, build_temple_cage, v)

# =====================================================================
# ★ISS-218: 第三档 (Type-C 面板开孔) 的判据常量与锚点
# ---------------------------------------------------------------------
# 判据出处: MECH/HW_CROSS_REVIEW_TRIAGE.md §1 的 MECH_ANCHORS 块 (ISS-213 写死的口径)
#   thresholds.crit = 0.60          通用判据: 最坏单边间隙 ≥ 0.60
#   typec_panel.body_x/_y = 8.94/3.26  USB Type-C 母座本体 [官方]
#   typec_panel.fdm_tol = 0.30     FDM 外形公差 ±0.30
# 金属·CNC 档公差 ±0.05 (ISS-213 口径)
# ★**本脚本只读这些数, 一个都不许改**; 反向用例专门抓"有人偷偷松判据"。
# =====================================================================
TRIAGE = os.path.abspath(os.path.join(HERE, os.pardir, "HW_CROSS_REVIEW_TRIAGE.md"))

CRIT_SIDE = 0.60          # 判据: 最坏单边间隙 ≥ 0.60 (MECH/service_port_check.py CRIT)
BODY_X = 8.94             # USB Type-C 母座本体宽 [官方]
BODY_Y = 3.26             # USB Type-C 母座本体高 [官方]
FDM_TOL = 0.30            # FDM 外形公差 ±0.30 (MECH/fit_check.py 口径)
CNC_TOL = 0.05            # 金属·CNC 档公差 ±0.05 (ISS-213 口径)
CRIT_EXPECTED = 0.60      # 判据不许松 —— 写死在这里供反向用例抓


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
                          ("frame_typec", build_frame_typec),
                          ("frame_typec_tier3", build_frame_typec_tier3)):
        PM.reset()
        builder()
        parts[name] = list(PM.MODEL)
    return parts


def stl_points(name):
    fn = {"fit_coupon": "fit_coupon_revb.stl",
          "temple_cage": "temple_cage_revb.stl",
          "frame_typec": "frame_typec_coupon_revb.stl",
          "frame_typec_tier3": "frame_typec_coupon_tier3_revb.stl"}[name]
    return load_stl(os.path.join(HERE, fn))


# =====================================================================
# ★ISS-218: 第三档余量对拍 + 锚点对拍
# ---------------------------------------------------------------------
# 最坏单边间隙 (与 ISS-213 §5.1 / MECH/check_demo_struct_truth.py G2.2-G2.4 同式):
#     g_worst = (开口名义 − 工艺公差 − 母座本体) / 2
# 判据 CRIT = 0.60 (单边)。
# =====================================================================
def worst_gap(opening, body, tol):
    return (opening - tol - body) / 2.0


def load_triage_anchors():
    """读 MECH/HW_CROSS_REVIEW_TRIAGE.md 的 MECH_ANCHORS 块 (只读, 唯一真源)"""
    import yaml
    with open(TRIAGE, encoding="utf-8") as f:
        txt = f.read()
    m = re.search(r"# BEGIN MECH_ANCHORS(.*?)# END MECH_ANCHORS", txt, re.S)
    if not m:
        raise SystemExit("[verify] 定性表里找不到 MECH_ANCHORS 块")
    data = yaml.safe_load(m.group(1))
    return data["anchors"]


def tier3_margin_rows():
    """第三档余量对拍 4 行 (第三档 2 行必须过 + 现候选 2 行必须不过)。

    ★ 全局量在 **调用时** 取 (不是 def 时冻住) —— 否则反向用例改不动它 (ISS-216 C-7 同款坑)。
    """
    rows = []
    # 第三档 (ISS-213 出, 本单落成试样) —— 必须 ≥ 判据
    rows.append(("★第三档 FDM 直成型档", P["tc_open_w3"][0], P["tc_open_h3"][0],
                 FDM_TOL, True))
    rows.append(("★第三档 金属·CNC 档", P["tc_open_w4"][0], P["tc_open_h4"][0],
                 CNC_TOL, True))
    # 两档现候选 (打印包现试样) —— 必须 < 判据 (证明"两档并行"是假二选一)
    rows.append(("现口径 (打印包现试样 1)", P["tc_open_w"][0], P["tc_open_h"][0],
                 FDM_TOL, False))
    rows.append(("ISS-089 建议 (打印包现试样 2)", P["tc_open_w2"][0], P["tc_open_h2"][0],
                 FDM_TOL, False))
    out = []
    for (name, ox, oy, tol, must_pass) in rows:
        gx = worst_gap(ox, BODY_X, tol)
        gy = worst_gap(oy, BODY_Y, tol)
        if must_pass:
            ok = (gx >= CRIT_SIDE and gy >= CRIT_SIDE)
            note = f"第三档 ⇒ 必须 ≥ 判据 {CRIT_SIDE:.2f}"
        else:
            ok = (gx < CRIT_SIDE or gy < CRIT_SIDE)
            note = f"现候选 ⇒ 必须 < 判据 {CRIT_SIDE:.2f} (证'两档并行'是假二选一)"
        out.append((name, ox, oy, tol, gx, gy, ok, note))
    return out


def anchor_checks():
    """第三档数字 vs MECH_ANCHORS 真源 的逐条对拍 (任何漂移都必须变红)"""
    A = load_triage_anchors()
    tc = A["typec_panel"]
    out = []
    out.append(("A1", "第三档 FDM 开口宽 == MECH_ANCHORS.new_opening_x",
                abs(P["tc_open_w3"][0] - tc["new_opening_x"]) < 1e-9,
                f"打印包 {P['tc_open_w3'][0]} vs 锚点 {tc['new_opening_x']}"))
    out.append(("A2", "第三档 FDM 开口高 == MECH_ANCHORS.new_opening_y",
                abs(P["tc_open_h3"][0] - tc["new_opening_y"]) < 1e-9,
                f"打印包 {P['tc_open_h3'][0]} vs 锚点 {tc['new_opening_y']}"))
    out.append(("A3", "第三档 金属·CNC 开口宽 == MECH_ANCHORS.metal_opening_x",
                abs(P["tc_open_w4"][0] - tc["metal_opening_x"]) < 1e-9,
                f"打印包 {P['tc_open_w4'][0]} vs 锚点 {tc['metal_opening_x']}"))
    out.append(("A4", "第三档 金属·CNC 开口高 == MECH_ANCHORS.metal_opening_y",
                abs(P["tc_open_h4"][0] - tc["metal_opening_y"]) < 1e-9,
                f"打印包 {P['tc_open_h4'][0]} vs 锚点 {tc['metal_opening_y']}"))
    out.append(("A5", "★判据阈值不许松 (CRIT == 0.60 == MECH_ANCHORS.thresholds.crit)",
                abs(CRIT_SIDE - CRIT_EXPECTED) < 1e-9
                and abs(CRIT_SIDE - A["thresholds"]["crit"]) < 1e-9,
                f"脚本 {CRIT_SIDE} vs 锚点 {A['thresholds']['crit']} vs 写死 {CRIT_EXPECTED}"))
    out.append(("A6", "母座本体 == MECH_ANCHORS.typec_panel.body_x/body_y",
                abs(BODY_X - tc["body_x"]) < 1e-9 and abs(BODY_Y - tc["body_y"]) < 1e-9,
                f"脚本 {BODY_X}×{BODY_Y} vs 锚点 {tc['body_x']}×{tc['body_y']}"))
    out.append(("A7", "FDM 公差 == MECH_ANCHORS.typec_panel.fdm_tol",
                abs(FDM_TOL - tc["fdm_tol"]) < 1e-9,
                f"脚本 {FDM_TOL} vs 锚点 {tc['fdm_tol']}"))
    return out


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


def build_probes(tier3_model=None):
    out = []
    models = build_model()
    if tier3_model is not None:
        models["frame_typec_tier3"] = tier3_model

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

    # ================= frame_typec_tier3 (★ISS-218 第三档试样) =================
    PM.MODEL[:] = models["frame_typec_tier3"]
    t3 = v("tc3_plate_t")
    w3 = v("tc_wall_min")
    for (x0, ow, oh, tag) in ((L["tc3_fdm_x0"], v("tc_open_w3"), v("tc_open_h3"), "FDM 直成型档"),
                              (L["tc3_cnc_x0"], v("tc_open_w4"), v("tc_open_h4"), "金属·CNC 档")):
        xc = x0 + w3 + ow / 2          # 开口中心 X
        yc = w3 + oh / 2               # 开口中心 Y
        # 开口宽 (沿 +X 过开口中心取空档)
        sp = PM.cover_x(yc, t3 / 2)
        meas = nearest_gap(PM.voids(sp), xc)
        out.append(Probe("frame_typec_tier3", f"★第三档 {tag} 开口宽 ({ow:.2f})", ow, "mm",
                         meas, 0.01, "沿 +X 过开口中心取空档 = 开口宽"))
        # 开口高 (沿 +Y 过开口中心取空档)
        sp = PM.cover_y(xc, t3 / 2)
        meas = nearest_gap(PM.voids(sp), yc)
        out.append(Probe("frame_typec_tier3", f"★第三档 {tag} 开口高 ({oh:.2f})", oh, "mm",
                         meas, 0.01, "沿 +Y 过开口中心取空档 = 开口高"))
        # 左承力壁 (沿 +X 取开口中心处的左壁实体段)
        sp = PM.cover_x(yc, t3 / 2)
        meas = nearest_solid(sp, x0 + w3 / 2)
        out.append(Probe("frame_typec_tier3", f"★第三档 {tag} 左承力壁厚", w3, "mm",
                         meas, 0.01, "沿 +X 过开口中心取左壁实体段 = 左承力壁厚"))
        # 下承力壁 (沿 +Y 取开口中心处的下壁实体段)
        sp = PM.cover_y(xc, t3 / 2)
        meas = nearest_solid(sp, w3 / 2)
        out.append(Probe("frame_typec_tier3", f"★第三档 {tag} 下承力壁厚", w3, "mm",
                         meas, 0.01, "沿 +Y 过开口中心取下壁实体段 = 下承力壁厚"))
        # 外形 X (在开口带之外量, 取含本面板的那段实体)
        sp = PM.cover_x(w3 / 2, t3 / 2)
        meas = nearest_solid(sp, x0 + w3 / 2)
        out.append(Probe("frame_typec_tier3", f"★第三档 {tag} 面板外形 X", ow + 2 * w3, "mm",
                         meas, 0.01, "沿 +X 过下壁带取本面板实体段 = 面板外形宽"))
        # 外形 Y (只对本面板成立 ⇒ 取含本面板 X 的那段)
        sp = PM.cover_y(x0 + w3 / 2, t3 / 2)
        meas = nearest_solid(sp, w3 / 2)
        out.append(Probe("frame_typec_tier3", f"★第三档 {tag} 面板外形 Y", oh + 2 * w3, "mm",
                         meas, 0.01, "沿 +Y 过本面板左壁取实体段 = 面板外形高"))
    # 工艺表征段: 收缩率标定方块 (凸起) + 孔径补偿试样 (通孔)
    for i, (sx, sy, s) in enumerate(L["tc3_sq"]):
        sp = PM.cover_x(sy + s / 2, t3 + v("tc3_boss_h") / 2)
        meas = nearest_solid(sp, sx + s / 2)
        out.append(Probe("frame_typec_tier3", f"★第三档 收缩率标定方块 #{i+1} ({s:.2f}) X",
                         s, "mm", meas, 0.01,
                         "沿 +X 过方块中心取实体段 = 收缩率标称 (FDM 收缩比的分母)"))
    sx, sy, s = L["tc3_sq"][2]
    sp = PM.cover_y(sx + s / 2, t3 + v("tc3_boss_h") / 2)
    meas = nearest_solid(sp, sy + s / 2)
    out.append(Probe("frame_typec_tier3", f"★第三档 收缩率标定方块 #3 ({s:.2f}) Y",
                     s, "mm", meas, 0.01,
                     "沿 +Y 过方块中心取实体段 (与 X 对比 ⇒ 看各向异性)"))
    for i, (hx, hy, dia) in enumerate(L["tc3_holes"]):
        sp = PM.cover_x(hy, t3 / 2)
        meas = nearest_gap(PM.voids(sp), hx)
        out.append(Probe("frame_typec_tier3", f"★第三档 孔径补偿试样 #{i+1} ⌀{dia:.2f}",
                         dia, "mm", meas, 0.01,
                         "沿 +X 过孔心取空档 = 孔径 (FDM 孔径收缩的分母)"))
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
        "frame_typec_tier3": [
            # ★ 探针点必须避开 **盒端面三角扇的中心** (mid_y, mid_z) ——
            #   命中扇心会同时打到 4 个扇形三角形 ⇒ 命中数 4 (偶数) ⇒ 奇偶判内外翻车
            #   (见本文件头“坑 ⑤”)。故下列点的 Y 都刻意避开各盒的 mid_y。
            ((6.75, 4.20, 1.5), "第三档 FDM 开口内 (应为空)"),
            ((0.75, 4.20, 1.5), "第三档 FDM 左承力壁内"),
            ((12.75, 4.20, 1.5), "第三档 FDM 右承力壁内"),
            ((6.75, 0.60, 1.5), "第三档 FDM 下承力壁内"),
            ((22.625, 4.10, 1.5), "第三档 金属·CNC 开口内 (应为空)"),
            ((16.75, 4.10, 1.5), "第三档 金属·CNC 左承力壁内"),
            ((35.50, 3.20, 4.0), "第三档 收缩率标定方块 #1 内"),
            ((44.00, 13.50, 4.0), "第三档 收缩率标定方块 #2 内"),
            ((60.00, 11.50, 4.0), "第三档 收缩率标定方块 #3 内"),
            ((35.00, 26.50, 1.5), "第三档 孔径试样 ⌀4 孔内 (应为空)"),
            ((45.00, 26.50, 1.5), "第三档 孔径试样 ⌀6 孔内 (应为空)"),
            ((57.00, 26.50, 1.5), "第三档 孔径试样 ⌀8 孔内 (应为空)"),
            ((50.00, 26.50, 1.5), "第三档 孔试样之间实体内"),
            ((10.00, 20.00, 1.5), "第三档 面板外 (应为空)"),
        ],
    }
    for name, samples in plans.items():
        tris = stl_points(name)
        PM.MODEL[:] = models[name]
        agree, total, bad = cross_check(name, models[name], tris, samples)
        report.append((name, agree, total, bad))
    return report


def evaluate(tier3_model=None, with_stl=False):
    """跑一遍全部检查 ⇒ 返回各组结果 (main 与 --selftest 共用同一个口径)"""
    probes, models = build_probes(tier3_model)
    geo_bad = [(p.part, p.item, p.nominal, p.measured) for p in probes if not p.ok]
    rows = tier3_margin_rows()
    margin_bad = [r for r in rows if not r[6]]
    acks = anchor_checks()
    ack_bad = [a for a in acks if not a[2]]
    stl = cross_check_all(models) if with_stl else None
    return dict(probes=probes, models=models, geo_bad=geo_bad, rows=rows,
                margin_bad=margin_bad, acks=acks, ack_bad=ack_bad, stl=stl)


def main():
    print("=" * 100)
    print("Rev B 打印包自检 (解析模型精确求尺寸 + STL 逐点互验)")
    print("=" * 100)
    r = evaluate(with_stl=True)
    probes = r["probes"]
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

    # ---------------- ★ISS-218: 第三档余量判据对拍 ----------------
    print("\n【★第三档余量判据对拍 (判据 CRIT = 0.60 — 一个不许松)】")
    print(f"  口径: g_worst = (开口名义 − 工艺公差 − 母座本体 {BODY_X}×{BODY_Y}) / 2")
    mok = 0
    for (name, ox, oy, tol, gx, gy, good, note) in r["rows"]:
        if good:
            mok += 1
        print(f"  {'✅' if good else '❌'} {name:<34} {ox:>6.2f}×{oy:<5.2f} "
              f"公差 ±{tol:.2f} ⇒ 最坏单边 X {gx:>5.2f} / Y {gy:>5.2f}  {note}")
    print(f"  合计: {mok}/{len(r['rows'])} 条对拍通过")

    print("\n【★第三档数字 vs MECH_ANCHORS 真源 对拍 (任何漂移必须变红)】")
    aok = 0
    for (aid, aname, good, detail) in r["acks"]:
        if good:
            aok += 1
        print(f"  {'✅' if good else '❌'} {aid} {aname:<56} {detail}")
    print(f"  合计: {aok}/{len(r['acks'])} 条对拍通过")

    print("\n【STL ↔ 解析模型 逐点互验 (射线奇偶判内外)】")
    total_agree = 0
    total_n = 0
    all_bad = []
    for (name, agree, total, bad) in r["stl"]:
        total_agree += agree
        total_n += total
        all_bad += [(name,) + b for b in bad]
        flag = "✅" if agree == total else "❌"
        print(f"  {flag} {name:<20} {agree}/{total} 点一致")
        for (pt, a, s) in bad:
            print(f"       ❌ 点 {tuple(round(c,2) for c in pt)}: 解析={a} STL={s}")
    print(f"  合计: {total_agree}/{total_n} 点一致 "
          f"({'✅ STL 就是这套规格' if total_agree == total_n else '❌ STL 与规格不一致'})")

    print("\n" + "=" * 100)
    good = (ok == len(probes)) and (total_agree == total_n) \
        and (mok == len(r["rows"])) and (aok == len(r["acks"]))
    if good:
        print("★ Rev B 打印包: 尺寸判据 100% 一致 + STL 与规格逐点互验 100% 一致")
        print("  ⇒ **模型层已闭环** (可直接下片) —— 但 **实物 M-PRINT 仍为 0 数据**:")
        print("    必须实物打印 + 卡尺实测, 见 MECH/print/MEASURE_CHECKLIST.md")
        print("★ 第三档 (ISS-218): 10.50×4.80 FDM 直成型 + 10.25×4.55 金属·CNC "
              "已在 MECH/print/PRINT_COUPON_TIER3_SPEC.md 落成可下片试样")
    else:
        print("⚠️ 有偏差 —— 重新生成后再打")
    print("★ optical_cage_TEMPLATE.stl: ★★ISS-222 (2026-11-16) 已解冻重生 —— 走鹃Ⅱ 作废 + C-6/C-8 落地 "
          "⇒ 分光件座 (7.78 × 8.84 × 11.0); md5 6f23c2e2… → 537dc6af… (旧登记值作废, 待 main 更新 PROJECT_TRACKER)")
    return 0 if good else 1


# =====================================================================
# ★ISS-218: 反向用例 (--selftest) —— 改坏第三档 / 松判据 ⇒ 必须变红
#   ★ 写法照 MECH/check_demo_struct_truth.py --selftest。
#   ★ 关键: 基准值必须在 **调用时** 取 (不能 def 时冻住) —— 否则反向用例改不动它
#     ⇒ 自检变成自嗨 (ISS-216 C-7 同款坑, 本单不重蹈)。
# =====================================================================
_MUT_P_KEYS = ("tc_open_w3", "tc_open_h3", "tc_open_w4", "tc_open_h4")


def _snapshot():
    return (dict((k, P[k]) for k in _MUT_P_KEYS),
            (CRIT_SIDE, BODY_X, BODY_Y, FDM_TOL, CNC_TOL))


def _restore(snap):
    for k, val in snap[0].items():
        P[k] = val
    g = globals()
    (g["CRIT_SIDE"], g["BODY_X"], g["BODY_Y"],
     g["FDM_TOL"], g["CNC_TOL"]) = snap[1]


def _mut_p(key, val):
    P[key] = (val,) + P[key][1:]


def _build_tier3_width(width):
    """临时把第三档 FDM 开口宽改成 width 造一个件 (只给反向用例用)"""
    saved = P["tc_open_w3"]
    P["tc_open_w3"] = (width,) + saved[1:]
    PM.reset()
    build_frame_typec_tier3()
    model = list(PM.MODEL)
    P["tc_open_w3"] = saved
    return model


def selftest():
    print("=" * 100)
    print("Rev B 打印包自检 —— ★反向用例 (ISS-218: 改坏第三档 / 松判据 ⇒ 必须变红)")
    print("=" * 100)
    snap = _snapshot()
    results = []
    try:
        # ---------------- 基线必须全绿, 否则自测不成立 ----------------
        base = evaluate(with_stl=True)
        stl_ok = all(a == n for (_nm, a, n, _b) in base["stl"])
        base_ok = (not base["geo_bad"] and not base["margin_bad"]
                   and not base["ack_bad"] and stl_ok)
        if not base_ok:
            print("❌ 基线就不绿 ⇒ 门禁本身有问题, 自测不成立")
            for b in base["geo_bad"]:
                print(f"     几何红: {b}")
            for b in base["margin_bad"]:
                print(f"     余量红: {b[0]}")
            for b in base["ack_bad"]:
                print(f"     锚点红: {b[0]} {b[1]}")
            return 1
        print("  ✅ 基线绿: 几何探针全过 + 余量对拍全过 + 锚点对拍全过 + STL 逐点互验全过")

        def case(name, target, mutate, expect):
            _restore(snap)
            mutate()
            r = evaluate()
            caught = bool(r[target])
            results.append((name, caught))
            print(f"  {'✅' if caught else '❌'} {name:<50} ⇒ {expect} "
                  f"{'抓到了' if caught else '★抓不到★ (自检是自嗨!)'}")

        case("反向1: 第三档 FDM 开口宽 10.50 → 9.50", "margin_bad",
             lambda: _mut_p("tc_open_w3", 9.50), "余量对拍必须变红")
        case("反向2: 第三档 FDM 开口高 4.80 → 3.60", "margin_bad",
             lambda: _mut_p("tc_open_h3", 3.60), "余量对拍必须变红")
        case("反向3: 第三档 金属·CNC 开口宽 10.25 → 9.50", "margin_bad",
             lambda: _mut_p("tc_open_w4", 9.50), "余量对拍必须变红")
        case("反向4: 第三档 金属·CNC 开口高 4.55 → 3.60", "margin_bad",
             lambda: _mut_p("tc_open_h4", 3.60), "余量对拍必须变红")
        case("反向5: ★判据 CRIT 0.60 → 0.30 (松判据)", "ack_bad",
             lambda: globals().__setitem__("CRIT_SIDE", 0.30), "锚点对拍必须变红")
        case("反向6: 母座本体 8.94 → 9.50 (假装母座更大)", "margin_bad",
             lambda: globals().__setitem__("BODY_X", 9.50), "余量对拍必须变红")
        case("反向7: 金属档公差 0.05 → 0.50 (假装 CNC 不准)", "margin_bad",
             lambda: globals().__setitem__("CNC_TOL", 0.50), "余量对拍必须变红")

        # 反向8: 实体按 9.50 造, 标称仍写 10.50 ⇒ 几何对拍 + STL 互验都必须变红
        _restore(snap)
        wrong = _build_tier3_width(9.50)
        r = evaluate(tier3_model=wrong, with_stl=True)
        caught_geo = bool(r["geo_bad"])
        caught_stl = not all(a == n for (_nm, a, n, _b) in r["stl"])
        results.append(("反向8: 实体按 9.50 造 (标称仍 10.50)", caught_geo and caught_stl))
        print(f"  {'✅' if (caught_geo and caught_stl) else '❌'} "
              f"{'反向8: 实体按 9.50 造 (标称仍 10.50)':<50} ⇒ "
              f"几何对拍 + STL 互验必须变红 "
              f"{'抓到了' if (caught_geo and caught_stl) else '★抓不到★ (自检是自嗨!)'}")
        if caught_geo:
            for b in r["geo_bad"][:3]:
                print(f"       (几何红: {b[1]} 标称 {b[2]} 实测 {b[3]})")
    finally:
        _restore(snap)

    caught = sum(1 for (_n, c) in results if c)
    print("\n" + "-" * 100)
    print(f"反向用例: {caught}/{len(results)} 抓到")
    if caught != len(results):
        print("❌ 有反向用例抓不到 ⇒ 自检不可信")
        return 1
    print("✅ 全部反向用例都抓到了 ⇒ 第三档门禁不是假绿")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(main())
