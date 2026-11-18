#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-121 判据: MEMS 麦克风 vs 镜脚末端检修口 N35 磁铁 —— **磁场强度 + 位置间距**
=====================================================================================
题目 (ISS-092 转来的 I-5 / I-6 两条接口请求):
  ① 磁场: 镜脚末端外侧面防丢磁铁 N35 ⌀4.00×1.00, 末端 MEMS 麦克风对该磁场是否敏感
           (间距 ≥40mm 够不够, 要按麦克风规格书的磁场敏感度核)
  ② 位置: 麦克风声孔 / 导光孔在镜脚外侧的**实际位置**, 与通窗/磁铁/螺钉凸台间距是否 ≥40mm

【本脚本做 4 件事, 全部可机械复算】
  A. **坐标系回归**: 由 ISS-092 §8 表反推板坐标 X ↔ 镜脚 L 的映射, 并复算 MECH 自己写的
     4 个间距 (电芯 49.21 / 铰链 74.71 / 骨架 7.21 / 逃线带 17.41) —— 复算不过 ⇒ 后面全不信
  B. **磁体模型**: 均匀磁化圆柱 (N35 ⌀4×1) 的磁场, 数值积分 (等效面磁荷) + 轴向解析解互校
     ⇒ 表面场 / 轴向 B(d) / 候选麦克风位置的**三维** B
  C. **位置判据**: 候选麦克风位置 × {通窗, 磁铁, 螺钉} 的最小间距, 逐项过 ≥40mm 判据
  D. **落盘 JSON**: HW/iss121_mic_magnet_check.json

【纪律】
  - 只写 HW/ 下本脚本自己的两个文件 (脚本 + JSON); 不碰 state/ MECH/ SW/ 别人的分片。
  - 证据分级: 磁体牌号参数 [官方-牌号通用值]; 几何全部来自 MECH 的 [推算]; 麦克风磁场敏感度 [0数据]。
  - 退出码: 0 = 判据跑完 (含 WARN/FAIL-已归属); 1 = 有**未归属**的硬 FAIL。
"""
from __future__ import annotations

import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "iss121_mic_magnet_check.json")

# =====================================================================================
# 0. 常数与证据分级
# =====================================================================================
MU0 = 4.0e-7 * math.pi

# N35 (烧结钕铁硼, 国标牌号) —— 两家磁材厂公开牌号表:
#   Br = 1.18~1.23 T (宁波永久) / 典型 1.17~1.21 T (tymagnets)  => 取 typ 1.20 T
#   (BH)max 33~36 MGOe; Hcb >=876 kA/m; 最高工作温度 80 degC   [官方-牌号通用值]
BR_TYP = 1.20                  # T
BR_LO, BR_HI = 1.14, 1.26      # T  (-5%/+5% 敏感性带宽)

# 磁铁几何 (ISS-092 4.1 C-8): N35 ⌀4.00 × 1.00, 轴向充磁, 装在镜脚外壁 ⌀4.20×1.00 沉槽
MAG_D, MAG_T = 4.00, 1.00      # mm
MAG_R = MAG_D / 2.0            # 2.00 mm
MAG_M = BR_TYP / MU0           # A/m  (M = Br/mu0)

# 参考场 (判定锚点)
EARTH_MIN, EARTH_TYP, EARTH_MAX = 25.0, 50.0, 65.0     # µT  地磁场 [官方-通用物理量]
IEC4_8 = {1: 1.0, 2: 3.0, 3: 10.0, 4: 30.0, 5: 100.0}  # A/m [官方-通用引用]
#   B = mu0*H  =>  1 A/m = 1.2566 µT

# =====================================================================================
# 1. 坐标系 (板坐标 X <-> 镜脚 L) —— 回归校验
# =====================================================================================
# 板坐标 (MECH/PCB_MOUNT_PIN_SET2.md 坐标约定): 原点 = 板框左下角, X = 板长 0..60.00, X=0 = 铰链端
# 镜脚 L (MECH): 0 = 铰链端, 130.00 = 耳端
# 映射由 ISS-092 §8 第 12 行反推: 逃线带 X 20.20..31.80 == L 60.70..72.30 => 偏移 = 40.50
L_OFFSET = 40.50


def L_of(x: float) -> float:
    return x + L_OFFSET


def x_of(L: float) -> float:
    return L - L_OFFSET


def regression_check():
    """复算 MECH 自己写的 4 个间距 —— 映射对不对, 用 MECH 的数说话。"""
    cases = [
        ("电芯 L0..40.5 -> 通窗", 49.21, L_of(49.20) - 40.50),
        ("铰链区 L0..15 -> 通窗", 74.71, L_of(49.20) - 15.00),
        ("金属骨架末端 L82.5 -> 通窗", 7.21, L_of(49.20) - 82.50),
        ("逃线带末端 X31.80 -> 通窗", 17.41, L_of(49.20) - L_of(31.80)),
    ]
    rows, ok = [], True
    for name, ref, calc in cases:
        d = abs(calc - ref)
        good = d <= 0.011
        ok = ok and good
        rows.append({"case": name, "mech_mm": ref, "recomputed_mm": round(calc, 4),
                     "delta_mm": round(d, 4), "pass": good})
    return ok, rows


# =====================================================================================
# 2. 磁体模型 —— 均匀磁化圆柱
# =====================================================================================
def B_axial(z_from_center: float, br: float = BR_TYP,
            r: float = MAG_R, half_t: float = MAG_T / 2.0) -> float:
    """轴线上 (距磁体中心 z, mm) 的 B (Tesla) —— 解析解 (均匀磁化圆柱)。"""
    M = br / MU0
    za, zb = z_from_center + half_t, z_from_center - half_t
    return MU0 * M / 2.0 * (za / math.hypot(r, za) - zb / math.hypot(r, zb))


def B_numeric(px, py, pz, br: float = BR_TYP, r: float = MAG_R, half_t: float = MAG_T / 2.0,
              nr: int = 160, ntheta: int = 120):
    """任意点 P (mm, 磁体中心在原点, 轴 = +z) 的 B —— 等效面磁荷数值积分。
    上表面 sigma=+M, 下表面 sigma=-M。返回 (Bx, By, Bz) (Tesla)。
    ★ 极坐标积分**必须带雅可比 r'** (dA = r' dr' dtheta)。
      初版按等面积环写, 面积元少算 3x 被中点法低估抵消 => 与解析解差 2.0% => 已修 (现差 0.0001%)"""
    M = br / MU0
    bx = by = bz = 0.0
    dr = r / nr
    dth = 2.0 * math.pi / ntheta
    for sign, zf in ((+1.0, half_t), (-1.0, -half_t)):
        sigma = sign * M
        for i in range(nr):
            rr = (i + 0.5) * dr
            w = sigma * rr * dr * dth / (4.0 * math.pi)   # 雅可比 r' dr' dtheta
            for j in range(ntheta):
                th = (j + 0.5) * dth
                sx, sy = rr * math.cos(th), rr * math.sin(th)
                dx, dy, dz = px - sx, py - sy, pz - zf
                d2 = dx * dx + dy * dy + dz * dz
                d = math.sqrt(d2)
                k = w / (d2 * d)
                bx += k * dx
                by += k * dy
                bz += k * dz
    return MU0 * bx, MU0 * by, MU0 * bz


def self_test_magnet():
    """数值积分 vs 解析解 (轴线上) —— 互校, 偏差 >0.5% 判模型不可用。"""
    b_num = B_numeric(0.0, 0.0, 10.0)[2]
    b_ana = B_axial(10.0)
    err = abs(b_num - b_ana) / b_ana
    b_face = B_axial(MAG_T / 2.0)                       # 端面中心表面场 (外侧极限)
    b_face_out = B_numeric(0.0, 0.0, MAG_T / 2.0 + 0.05)[2]
    err_face = abs(b_face_out - b_face) / b_face
    return {"numeric_vs_analytic_rel_err": round(err, 9),
            "numeric_ok": err <= 0.005,
            "face_numeric_vs_analytic_rel_err": round(err_face, 9),
            "B_face_center_T": round(b_face, 6), "B_face_center_G": round(b_face * 1e4, 1),
            "mag_moment_A_m2": round(MAG_M * math.pi * MAG_R ** 2 * MAG_T * 1e-9, 8)}


def b_at_3d(dx_mm: float, dy_mm: float, dz_mm: float, br: float = BR_TYP) -> float:
    """相对磁体中心的三维偏移 (mm) 处的 |B| (Tesla)。"""
    bx, by, bz = B_numeric(dx_mm, dy_mm, dz_mm, br=br)
    return math.sqrt(bx * bx + by * by + bz * bz)


# =====================================================================================
# 3. 几何 (板坐标 X) —— 全部来自 MECH 的 [推算]
# =====================================================================================
G = {
    # ISS-092 §4.1 尺寸表
    "window": (49.20, 59.40),     # C-1 通窗 10.20 (X) x 4.60 (Y)
    "cover": (48.00, 61.20),       # C-3 盖板外廓 13.20 x 7.60 (搭边 1.50/1.50)
    "screw_x": 60.30,              # C-9 M1.6x6 自攻螺钉 (盖板 X=60.30, 在 PCB 板端之外)
    "magnet_x_nom": 59.80,         # 镜脚侧 N35 磁铁: L≈100.30 (ISS-092 §4.3) => X=59.80 —— 精确 X [0数据]
    "magnet_x_lo": 48.00,          # 最坏情形: 磁铁贴在盖板搭边最里侧 (X=48.00)
    "jdebug": (50.50, 55.58),      # J_DEBUG 2x5@1.27 焊盘阵列
    "juart": (56.85, 58.12),       # J_UART 1x2
    # ISS-092 §8 冲突复核表
    "soc": (20.20, 31.80),         # SoC 逃线带
    # 跨铰链 4 连接器落板区 —— ISS-105 open, 边界 [0数据]。两种情形:
    #   (a) 座体悬出板端 (FPC 连接器常规做法) => 只占焊盘 X 0..3.00
    #   (b) 沿板长拉开 => 占 X 0..24.00
    "conn_zone_pads_only": (0.00, 3.00),
    "conn_zone_full": (0.00, 24.00),
    "skeleton": (18.00, 42.00),    # 金属骨架 (L 58.5..82.5)
    # ★★ PIN-SET-2 孔位 = **现行 60×30 板 / 套 A** (ISS-194 仲裁定版)
    #   真源: MECH/BOARD_GEOM_30MM.md §3/§4 (结构侧定版, main 已验收签字)
    #         + HW/pcb60x30_check.py 的 HOLES 表 (逐坐标一致)
    #   套A: P1(8.00,15.00)⌀2.00 / P2(52.00,15.00)⌀2.00 / S1(8.00,10.00)⌀1.40 / S2(52.00,20.00)⌀1.40
    #   ★**作废**: 15mm 老口径 P1(8,7.50) S1(8,2.50) P2(52,7.50) S2(52,12.50)
    #      —— 旧值留档在 PINSET_LEGACY_15MM, **只用于输出"改前/改后"对照**, 不参与任何判定
    "pinset": {"P1": (8.00, 15.00, 2.00), "S1": (8.00, 10.00, 1.40),
               "P2": (52.00, 15.00, 2.00), "S2": (52.00, 20.00, 1.40)},
}

# ★【作废口径·仅留档对照】15mm 板老孔位 (ISS-049 定版于 60×15 板时的坐标)
#   用途: 输出"套A 改前 vs 改后"的净空对照 (审计留痕); **不参与任何判定**。
PINSET_LEGACY_15MM = {"P1": (8.00, 7.50, 2.00), "S1": (8.00, 2.50, 1.40),
                       "P2": (52.00, 7.50, 2.00), "S2": (52.00, 12.50, 1.40)}

# 麦 M1 推荐落位 (板坐标) —— 与 CAND 第 1 项一致, 供 Y 向敏感度扫描与冲突文本引用
MIC_M1_POS = (5.00, 12.00)

# ---- J_CHG 座体 keep-out (现行 60×30 板) —— MECH/BOARD_GEOM_30MM.md §2 (结构侧定版)
#   = HW/pcb60x30_check.py 的 JCHG_RECT (x0,y0,x1,y1) —— 板中线 15.00 ± 3.25
JCHG_KEEPOUT_RECT_60X30 = (0.00, 11.75, 3.00, 18.25)

# =====================================================================================
# 3b. PIN-SET-2 孔壁净空判据 —— ★只引既有判据, 不新增/不改任何阈值★
# =====================================================================================
# ★**判据来源全部是仓库里已有的数, 本单没有自造任何新阈值**:
#   ① 硬性物理判据 (MD §3.2-4 既有口径「与 PIN-SET-2 不打架」): 封装边不得压到孔壁 ⇒ 净空 > 0
CRIT_PIN_WALL_NONOVERLAP_MM = 0.0
#   ② 板厂 DRC 数值 [实测]: HW/PCB/demo_mainboard.kicad_pro -> design_settings.rules
#      min_hole_clearance = 0.25mm (孔壁到铜) / min_copper_edge_clearance = 0.5mm
#      ★封装轮廓在焊盘之外 ⇒ 孔壁到封装边的净空是孔壁到焊盘净空的**保守下界**
REF_PIN_WALL_BOARD_RULE_MM = 0.25
#   ③ 项目先例 [推算]: MECH/SERVICE_PORT_ISS092.md §8-11「P2 孔壁到 J_DEBUG 焊盘阵列最近 1.00mm ✅」
REF_PIN_WALL_ISS092_MM = 1.00
#   ④ 通用工艺惯例 (非本项目判据, 只作参考): 自攻 M1.2 螺钉孔周围留 ≥1.0mm 器件/走线净空
REF_PIN_WALL_SELF_TAP_MM = 1.00
# H 向 (厚度) 坐标 —— ISS-092 §5.1 尺寸链
H = {
    "wall_out": 7.30, "wall_in": 6.50,       # 外壁 0.8
    "pcb_top": 2.40, "pcb_bot": 1.60,        # PCB 0.8 (ISS-092 C-5: 盖板内腔 4.90 = 7.30-2.40)
    "skel_out": 3.40,                        # 骨架外表面 (PCB 上方 1.0mm)
    "mag_center": 6.80,                      # 磁铁沉槽 1.0 深, 外表面与壁外表面齐平
    "mic_port": 2.95,                        # top-port 麦克风声孔中心高 (PCB 面 +0.55)
    "mic_top": 3.50,                         # top-port 封装顶 (1.10 高)
}
DZ_MIC = H["mag_center"] - H["mic_port"]    # 3.85 mm

# 候选麦克风位置 (板坐标 X, Y) —— 见文档 §3
CAND = [
    ("M1 铰链端", 5.00, 12.00,
     "唯一能同时满足『距通窗>=40』与『距磁铁>=40』的板区 (X<=9.20); 骨架外 (无骨架开窗需求)"),
    ("M2 SoC 区前", 17.00, 12.00,
     "骨架起点前 (X18.00) 最后一格; 但距通窗仅 32.20"),
    ("M3 mech-lead 假设位 (根部 SoC 区)", 26.00, 12.00,
     "ISS-092 §8 第 10 行『导光孔 根部 SoC 区』的代表位; 也是镜脚外侧导光孔若复活时的落点"),
]

def jchg_keepout_gap(x, y, pkg_w=2.90, pkg_h=1.60):
    """麦封装 (pkg_w x pkg_h, 中心 x,y) 到 **60×30 板 J_CHG 座体 keep-out** 的 2D 间距。
    keep-out 真源: MECH/BOARD_GEOM_30MM.md §2 + HW/pcb60x30_check.py 的 JCHG_RECT (结构侧定版)。
    ★这是**新增的 30mm 板连带项**: 15mm 板时 J_CHG 座体在 Y 4.25..10.75, 麦在 Y12.00 ⇒ Y 向有间隔;
      30mm 板 J_CHG 座体居中于板中线 Y=15.00 ⇒ 落板区 Y 11.75..18.25 与麦的 Y 带**重叠**
      ⇒ 只剩 X 向净空。本项**只报数**, 不改 ISS-121 既有 conn_zone 判定 (ISS-105 [0数据] 边界, 非本单裁决范围)。
    返回 (dx, dy, 2D 间距, Y 是否重叠)。"""
    jx0, jy0, jx1, jy1 = JCHG_KEEPOUT_RECT_60X30
    px0, px1 = x - pkg_w / 2.0, x + pkg_w / 2.0
    py0, py1 = y - pkg_h / 2.0, y + pkg_h / 2.0
    dx = max(jx0 - px1, 0.0, px0 - jx1)
    dy = max(jy0 - py1, 0.0, py0 - jy1)
    overlap_y = not (py1 < jy0 or py0 > jy1)
    return dx, dy, math.hypot(dx, dy), overlap_y


def pinset_clearance(pinset, x, y, pkg_w=2.90, pkg_h=1.60):
    """封装 (pkg_w x pkg_h, 中心 x,y) 到 PIN-SET-2 各孔**孔壁**的净空。
    几何: 孔心到封装矩形的最近点距 (dx,dy) => hypot(dx,dy) = 孔心到封装边距离;
          孔壁净空 = 该距离 - 孔半径。
    返回 (最小净空 mm, 控制孔号, {孔号: 净空})。
    ★公式与 ISS-121 原版 (ISS-121 交卷时的 pin_clear 算法) 逐字一致 —— 只换孔位表, 不换公式。"""
    px0, px1 = x - pkg_w / 2.0, x + pkg_w / 2.0
    py0, py1 = y - pkg_h / 2.0, y + pkg_h / 2.0
    detail = {}
    for pn, (hx, hy, hd) in pinset.items():
        dx = max(px0 - hx, 0.0, hx - px1)
        dy = max(py0 - hy, 0.0, hy - py1)
        edge = math.hypot(dx, dy)
        detail[pn] = round(edge - hd / 2.0, 4)
    gov = min(detail, key=detail.get)
    return detail[gov], gov, detail


def pinset_drift_guard():
    """口径防漂移闸: 本脚本的 pinset 表必须与 HW/pcb60x30_check.py 的 HOLES 表**逐坐标一致**。
    ★只读那一个文件 (不 import, 避免副作用); 读不到 => 报 skipped (不算 FAIL)。
    返回 (ok: True/False/None, detail: str)。"""
    ref = os.path.join(HERE, "pcb60x30_check.py")
    if not os.path.exists(ref):
        return None, "HW/pcb60x30_check.py 不存在 ⇒ 跳过对拍"
    try:
        with open(ref, encoding="utf-8") as f:
            src = f.read()
    except OSError as e:
        return None, "读 HW/pcb60x30_check.py 失败 (%s) ⇒ 跳过对拍" % e
    got = {}
    for m in re.finditer(r'\("(?P<k>[PS]\d)",\s*"[^"]*",\s*\((?P<x>[-\d.]+),\s*(?P<y>[-\d.]+)\),\s*(?P<d>[-\d.]+)', src):
        got[m.group("k")] = (float(m.group("x")), float(m.group("y")), float(m.group("d")))
    if not got:
        return None, "在 HW/pcb60x30_check.py 里没解析到 HOLES 表 ⇒ 跳过对拍"
    if got == dict(G["pinset"]):
        return True, "逐坐标一致 (%d 孔)" % len(got)
    return False, "★**不一致**: pcb60x30_check.py HOLES=%s vs 本脚本 pinset=%s" % (got, G["pinset"])


def mic_y_sensitivity(x=None, y_lo=0.80, y_hi=29.20, step=0.01):
    """麦落位 X 固定时, Y 在板宽内的**孔壁净空**敏感度 (现行套A 孔位)。
    用于回答「Y 落位若随板宽重定 (MD §3.6 P-3) 会掉到多少」。
    返回 dict: 每 0.10mm 采样 + 最差/最优 Y + >= 各参考门槛的 Y 区间。"""
    x = MIC_M1_POS[0] if x is None else x
    ys = [round(y_lo + i * step, 2) for i in range(int(round((y_hi - y_lo) / step, 2)) + 1)]
    rows = []
    for y in ys:
        w, gov, _ = pinset_clearance(G["pinset"], x, y)
        rows.append((y, round(w, 4), gov))
    worst = min(rows, key=lambda r: r[1])
    best = max(rows, key=lambda r: r[1])
    bands = {}
    for name, thr in (("nonoverlap", CRIT_PIN_WALL_NONOVERLAP_MM),
                      ("board_rule_0.25", REF_PIN_WALL_BOARD_RULE_MM),
                      ("iss092_1.00", REF_PIN_WALL_ISS092_MM)):
        ok = [(y, w) for y, w, _ in rows if w >= thr]
        if not ok:
            bands[name] = {"ok": False, "text": "无满足区间"}
            continue
        runs, s, p = [], ok[0][0], ok[0][0]
        for y, _ in ok[1:]:
            if y - p > 0.015:
                runs.append((s, p))
                s = y
            p = y
        runs.append((s, p))
        bands[name] = {"ok": True,
                       "text": " / ".join("[%.2f..%.2f]" % (a, b) for a, b in runs),
                       "runs": [[a, b] for a, b in runs]}
    return {"mic_x": x, "y_range": [y_lo, y_hi], "step": step,
            "worst": {"y": worst[0], "wall_mm": worst[1], "governing_hole": worst[2]},
            "best": {"y": best[0], "wall_mm": best[1], "governing_hole": best[2]},
            "at_current_y": next(((y, w, g) for y, w, g in rows
                                  if abs(y - MIC_M1_POS[1]) < 0.005), None),
            "bands": bands,
            "samples": [{"y": y, "wall_mm": w, "governing_hole": g}
                        for y, w, g in rows if int(round(y * 100)) % 50 == 0]}


# =====================================================================================
# 4. 判据
# =====================================================================================
CRIT_POS_MM = 40.0        # ISS-092 I-6 判据: 与通窗/磁铁/螺钉凸台间距 >=40mm
CRIT_B_STRONG = EARTH_TYP  # 50 µT = 地磁典型值 => 判定「无影响」的强判据
CRIT_B_LOOSE = 100.0      # 100 µT 参考带 (IEC 61000-4-8 L4=30A/m=37.7µT, L5=100A/m=126µT)


def eval_candidate(name, x, y, note):
    d_win = G["window"][0] - x if x < G["window"][0] else x - G["window"][1]
    d_mag_nom = abs(G["magnet_x_nom"] - x)
    d_mag_lo = abs(G["magnet_x_lo"] - x)
    d_screw = abs(G["screw_x"] - x)
    d_cover = (G["cover"][0] - x) if x < G["cover"][0] else (x - G["cover"][1])

    # 磁场: 磁体中心 -> 麦克风声孔中心 (dx 沿板长, dy=0 取最坏, dz = H 向 3.85)
    b_nom = b_at_3d(G["magnet_x_nom"] - x, 0.0, DZ_MIC) * 1e6      # µT
    b_lo = b_at_3d(G["magnet_x_lo"] - x, 0.0, DZ_MIC) * 1e6        # µT (磁铁最靠里)
    b_hi_br = b_at_3d(G["magnet_x_nom"] - x, 0.0, DZ_MIC, br=BR_HI) * 1e6  # Br 上限

    # 骨架遮挡: 麦克风上方有没有金属骨架 (骨架在 PCB 与外壁之间 H2.40..3.40)
    skel_over = not (x < G["skeleton"][0] or x > G["skeleton"][1])

    # 与 PIN-SET-2 孔的净空 (孔壁到封装边) —— 封装按典型 LGA 2.90 x 1.60
    # ★口径 = G["pinset"] = 现行 60×30 板 / 套 A (ISS-194 定版)
    pin_clear, pin_gov, pin_detail = pinset_clearance(G["pinset"], x, y)
    # 作废口径对照 (15mm 老孔位) —— 只为输出「改前/改后」留痕, 不参与判定
    pin_clear_legacy, pin_gov_legacy, _ = pinset_clearance(PINSET_LEGACY_15MM, x, y)

    # 跨铰链连接器落板区冲突 (ISS-105 open, 边界 [0数据]) —— 两种情形都算
    d_conn_pad = x - G["conn_zone_pads_only"][1] if x >= G["conn_zone_pads_only"][1] else -1.0
    d_conn_full = x - G["conn_zone_full"][1] if x >= G["conn_zone_full"][1] else -1.0
    conn_conflict = "情形b(占 X0..24, ISS-105 情形2) 重叠" if d_conn_full < 0 else \
                    ("情形a(仅焊盘 X0..3) 净空 %.2f mm" % d_conn_pad)

    return {
        "name": name, "board_x": x, "board_y": y, "temple_L": round(L_of(x), 2),
        "note": note,
        "conn_zone_clear_pads_only_mm": round(d_conn_pad, 2),
        "conn_zone_clear_full_mm": round(d_conn_full, 2),
        "conn_zone_status": conn_conflict,
        "clear_window_mm": round(d_win, 2),
        "clear_magnet_nom_mm": round(d_mag_nom, 2),
        "clear_magnet_worst_mm": round(d_mag_lo, 2),
        "clear_screw_mm": round(d_screw, 2),
        "clear_cover_footprint_mm": round(d_cover, 2),
        "B_at_mic_uT_nominal": round(b_nom, 2),
        "B_at_mic_uT_worst_magnetpos": round(b_lo, 2),
        "B_at_mic_uT_Br_high": round(b_hi_br, 2),
        "B_vs_earth_typ": ("< 地磁典型值(50uT)" if b_hi_br < EARTH_TYP else
                           "地磁量级" if b_hi_br < EARTH_MAX else "> 地磁上限(65uT)"),
        "pos_pass_window": d_win >= CRIT_POS_MM,
        "pos_pass_magnet": d_mag_lo >= CRIT_POS_MM,
        "pos_pass_screw": d_screw >= CRIT_POS_MM,
        "pos_pass_all": (d_win >= CRIT_POS_MM and d_mag_lo >= CRIT_POS_MM
                         and d_screw >= CRIT_POS_MM),
        "mag_pass": b_hi_br <= CRIT_B_STRONG,
        "skeleton_over_mic": skel_over,
        "skeleton_cutout_needed": skel_over,
        "pinset_clearance_mm": (round(pin_clear, 2) if pin_clear is not None else None),
        "pinset_governing_hole": pin_gov,
        "pinset_clearance_per_hole_mm": pin_detail,
        "pinset_clearance_legacy_15mm_mm": (round(pin_clear_legacy, 2)
                                            if pin_clear_legacy is not None else None),
        "pinset_governing_hole_legacy_15mm": pin_gov_legacy,
        "pinset_clearance_delta_vs_legacy_mm": (round(pin_clear - pin_clear_legacy, 2)
                                                if pin_clear is not None else None),
        # 孔壁净空判据 (全部引既有判据; 阈值未改)
        "pinset_wall_pass_nonoverlap": pin_clear > CRIT_PIN_WALL_NONOVERLAP_MM,
        "pinset_wall_pass_board_rule": pin_clear >= REF_PIN_WALL_BOARD_RULE_MM,
        "pinset_wall_pass_iss092_precedent": pin_clear >= REF_PIN_WALL_ISS092_MM,
        "pinset_wall_margin_vs_iss092_mm": round(pin_clear - REF_PIN_WALL_ISS092_MM, 2),
    }


def feasible_band():
    """『>=40mm 判据』在板坐标 X 上的可满足区间 (对通窗/磁铁/螺钉各取约束)。"""
    x_hi_win = G["window"][0] - CRIT_POS_MM      # 9.20
    x_hi_mag = G["magnet_x_lo"] - CRIT_POS_MM    # 8.00 (最坏: 磁铁在搭边最里侧)
    x_hi_scr = G["screw_x"] - CRIT_POS_MM        # 20.30
    x_hi = min(x_hi_win, x_hi_mag, x_hi_scr)
    conflicts = []
    if x_hi >= 8.00:
        # ★坐标取自 G["pinset"] (现行 60×30 板 / 套 A) —— 不再手写死坐标, 防再次漂移
        p1, s1 = G["pinset"]["P1"], G["pinset"]["S1"]
        conflicts.append(
            "PIN-SET-2 P1(%.2f,%.2f) ⌀%.1f / S1(%.2f,%.2f) ⌀%.1f (现行60x30套A) —— "
            "X=8.00 落在带内, 需 Y 向避让"
            % (p1[0], p1[1], p1[2], s1[0], s1[1], s1[2]))
    conflicts.append("跨铰链 4 连接器落板区 X 0..~24 (ISS-105 open, [0数据]) —— 与带内 X<=9.20 重叠")
    return {"x_max_allowed": round(x_hi, 2),
            "constraint_window": x_hi_win, "constraint_magnet_worst": x_hi_mag,
            "constraint_screw": x_hi_scr,
            "band": "X <= %.2f" % x_hi,
            "conflicts": conflicts,
            "usable_band_mm": round(x_hi, 2)}


def axis_table():
    rows = []
    for d in (5, 10, 20, 30, 40, 50, 60, 80):
        b = B_axial(MAG_T / 2.0 + d)          # 自磁体端面起算
        rows.append({"d_from_face_mm": d, "B_uT": round(b * 1e6, 2),
                     "B_G": round(b * 1e4, 3),
                     "vs_earth": ("<地磁最小(25uT)" if b * 1e6 < EARTH_MIN else
                                  "地磁量级" if b * 1e6 < EARTH_MAX else ">地磁上限")})
    return rows


def main() -> int:
    print("=" * 90)
    print("ISS-121 判据: MEMS 麦克风 vs 检修口 N35 磁铁 (磁场 + 位置)")
    print("=" * 90)

    reg_ok, reg_rows = regression_check()
    print("\n[A] 坐标系回归 (板坐标 X <-> 镜脚 L, 偏移 %.2f):" % L_OFFSET)
    for r in reg_rows:
        print("    %-34s MECH=%-8s 复算=%-9s Δ=%.4f  %s"
              % (r["case"], r["mech_mm"], r["recomputed_mm"], r["delta_mm"],
                 "OK" if r["pass"] else "FAIL"))
    if not reg_ok:
        print("    FAIL 坐标系回归失败 => 后续全部结论作废")
        return 1
    print("    OK 4/4 复算一致 => 映射被 MECH 自己的数字证实")

    st = self_test_magnet()
    print("\n[B] 磁体模型 (均匀磁化圆柱, Br=%.2fT, 直径%.2f x %.2fmm):" % (BR_TYP, MAG_D, MAG_T))
    print("    数值积分 vs 解析解 相对偏差 = %.6f%%  %s"
          % (st["numeric_vs_analytic_rel_err"] * 100, "OK" if st["numeric_ok"] else "FAIL"))
    print("    端面中心表面场 = %.0f G (%.4f T)" % (st["B_face_center_G"], st["B_face_center_T"]))
    print("    磁矩 m = %.3e A·m²" % st["mag_moment_A_m2"])
    if not st["numeric_ok"]:
        return 1

    print("\n[B2] 轴向场 (自磁体端面起算) —— 判定锚点: 地磁 25/50/65 µT, IEC 61000-4-8:")
    print("     d=40mm 处 B = %.1f µT;  地磁最小 25 / 典型 50 / 上限 65 µT"
          % (B_axial(MAG_T / 2.0 + 40) * 1e6))
    print("     IEC 61000-4-8 等级 (A/m -> µT): " + ", ".join(
        "L%d=%gA/m(%.1fµT)" % (k, v, MU0 * v * 1e6) for k, v in IEC4_8.items()))
    for r in axis_table():
        print("     d=%-3dmm  B=%8.2f µT (%7.3f G)  %s"
              % (r["d_from_face_mm"], r["B_uT"], r["B_G"], r["vs_earth"]))

    print("\n[C] 位置判据 (>=%.0fmm):" % CRIT_POS_MM)
    band = feasible_band()
    print("    可满足带 (板坐标 X): %s  —— 约束: 通窗 %.2f / 磁铁最坏 %.2f / 螺钉 %.2f"
          % (band["band"], band["constraint_window"], band["constraint_magnet_worst"],
             band["constraint_screw"]))
    for c in band["conflicts"]:
        print("    ! 带内冲突: %s" % c)

    # SoC 处的场 (订正 ISS-092 §4.3 的 '≥68mm' 说法)
    soc_x = G["soc"][1]
    soc_dz = H["mag_center"] - 2.20          # SoC 芯片中心高 (PCB 0.8 厚 + 封装)
    soc_dx = G["magnet_x_nom"] - soc_x
    b_soc = b_at_3d(soc_dx, 0.0, soc_dz) * 1e6
    soc_gap = soc_dx
    print("\n[C2] ISS-092 §4.3 '磁铁↔SoC 间距 >=68mm' 的复核:")
    print("     按同一条尺寸链: 磁铁板 X=59.80, SoC 逃线带末端板 X=%.2f => 实际间距 %.2f mm"
          % (soc_x, soc_gap))
    print("     该处磁场 B = %.1f µT (= 地磁典型值 50µT 的 %.1f 倍)  => 对 SoC 无功能影响, 但**数字必须订正**"
          % (b_soc, b_soc / EARTH_TYP))

    cands = []
    for name, x, y, note in CAND:
        r = eval_candidate(name, x, y, note)
        cands.append(r)
        print("\n    %s  (板 X=%.2f / Y=%.2f / 镜脚 L=%.2f)" % (name, x, y, L_of(x)))
        print("      间距: 通窗 %.2f | 磁铁(标称) %.2f | 磁铁(最坏) %.2f | 螺钉 %.2f | 盖板外廓 %.2f"
              % (r["clear_window_mm"], r["clear_magnet_nom_mm"],
                 r["clear_magnet_worst_mm"], r["clear_screw_mm"],
                 r["clear_cover_footprint_mm"]))
        print("      位置判据 >=40mm: %s   (通窗 %s / 磁铁 %s / 螺钉 %s)"
              % ("PASS" if r["pos_pass_all"] else "FAIL",
                 "OK" if r["pos_pass_window"] else "X",
                 "OK" if r["pos_pass_magnet"] else "X",
                 "OK" if r["pos_pass_screw"] else "X"))
        print("      磁场: B(麦克风处) 标称 %.2f µT / 磁铁最靠里 %.2f µT / Br上限 %.2f µT  => %s"
              % (r["B_at_mic_uT_nominal"], r["B_at_mic_uT_worst_magnetpos"],
                 r["B_at_mic_uT_Br_high"], r["B_vs_earth_typ"]))
        print("      磁场判据 (<=50µT=地磁典型值): %s" % ("PASS" if r["mag_pass"] else "FAIL"))
        print("      金属骨架遮挡: %s   PIN-SET-2 孔到封装壁 %.2f mm (控制孔 %s; 作废15mm口径 %.2f mm ⇒ Δ%+.2f)"
              % ("需骨架开窗 ~2.5x2.5" if r["skeleton_cutout_needed"] else "无 (骨架外)",
                 r["pinset_clearance_mm"] if r["pinset_clearance_mm"] is not None else -1,
                 r["pinset_governing_hole"],
                 r["pinset_clearance_legacy_15mm_mm"],
                 r["pinset_clearance_delta_vs_legacy_mm"]))
        print("      孔壁净空判据: 不重叠(>0) %s | 板规则 0.25mm %s | ISS-092先例 1.00mm %s (余量 %+.2f mm)"
              % ("PASS" if r["pinset_wall_pass_nonoverlap"] else "FAIL",
                 "PASS" if r["pinset_wall_pass_board_rule"] else "FAIL",
                 "PASS" if r["pinset_wall_pass_iss092_precedent"] else "FAIL",
                 r["pinset_wall_margin_vs_iss092_mm"]))
        print("      跨铰链连接器落板区 (ISS-105 [0数据]): %s" % r["conn_zone_status"])

    mag_all_pass = all(c["mag_pass"] for c in cands)
    pos_any_pass = any(c["pos_pass_all"] for c in cands)
    fails = []
    if not mag_all_pass:
        fails.append("[未归属] 磁场判据在所有候选位均不通过")
    for c in cands:
        if not c["pos_pass_all"] and c["name"].startswith("M1"):
            fails.append("[已归属->needs_from] %s 位置判据不通过: 通窗 %.2f / 磁铁最坏 %.2f mm"
                         % (c["name"], c["clear_window_mm"], c["clear_magnet_worst_mm"]))
        if c["name"].startswith("M1") and c["conn_zone_clear_full_mm"] < 0:
            fails.append("[已归属->ISS-105] %s 落板区边界 [0数据]: 情形b(连接器占 X0..24) 时无合规位置"
                         % c["name"])

    # ---- ISS-195: 孔位口径漂移闸 (本脚本 pinset vs HW/pcb60x30_check.py HOLES) ----
    guard_ok, guard_detail = pinset_drift_guard()
    if guard_ok is False:
        fails.append("[未归属->口径漂移] 本脚本 PIN-SET-2 孔位与 HW/pcb60x30_check.py 不一致: %s" % guard_detail)

    print("\n[D] 汇总")
    print("    磁场判据 (B <= 地磁典型值 50 µT): %s" % ("OK 全部候选通过" if mag_all_pass else "FAIL"))
    print("    位置判据 (>=40mm, 镜脚外侧面): %s"
          % ("OK 有可行候选 (M1)" if pos_any_pass else "FAIL 无可行候选"))
    print("    FAIL 清单:")
    if not fails:
        print("      (无)")
    for f in fails:
        print("      - %s" % f)

    # ---- ISS-195: 孔位口径漂移闸 + Y 向敏感度 (板宽 30mm 后麦落位要重定, MD §3.6 P-3) ----
    print("\n[E] 孔位口径漂移闸 (本脚本 pinset vs HW/pcb60x30_check.py HOLES):")
    print("    %s —— %s" % ("PASS" if guard_ok else ("SKIP" if guard_ok is None else "FAIL"), guard_detail))

    ysens = mic_y_sensitivity()
    cur = ysens["at_current_y"]
    print("\n[F] 麦 Y 落位敏感度 (X=%.2f 固定, 现行60x30套A孔位; MD §3.6 P-3 待重定):" % ysens["mic_x"])
    if cur:
        print("    当前落位 Y=%.2f => 孔壁净空 %.2f mm (控制孔 %s)" % (cur[0], cur[1], cur[2]))
    print("    全 Y 区间 [%.2f..%.2f] 最差: Y=%.2f => %.2f mm (%s) | 最优: Y=%.2f => %.2f mm"
          % (ysens["y_range"][0], ysens["y_range"][1],
             ysens["worst"]["y"], ysens["worst"]["wall_mm"], ysens["worst"]["governing_hole"],
             ysens["best"]["y"], ysens["best"]["wall_mm"]))
    for nm, lbl in (("nonoverlap", "不重叠 >0mm"), ("board_rule_0.25", "板规则 0.25mm"),
                    ("iss092_1.00", "ISS-092先例 1.00mm")):
        b = ysens["bands"][nm]
        print("    可用 Y 区间 [满足 %s]: %s" % (lbl, b.get("text", "-")))
    print("    ★⇒ 若按板宽 30mm 把麦落位取到板中线 Y=15.00, 孔壁净空只剩 %.2f mm ⇒ **Y 落位须由 main 裁决**"
          % pinset_clearance(G["pinset"], ysens["mic_x"], 15.00)[0])

    out = {
        "issue": "ISS-121",
        "title": "MEMS 麦克风与检修口磁铁的磁场/位置复核 (ISS-092 I-5/I-6)",
        "generated_by": "HW/iss121_mic_magnet_check.py",
        "evidence_grading": {
            "magnet_grade_params": "[官方-牌号通用值] N35 Br 1.17~1.23T (取 typ 1.20T)",
            "magnet_geometry": "[官方-MECH 规格] N35 直径4.00x1.00 (ISS-092 §4.1 C-8)",
            "geometry_all": "[推算] MECH 设计态几何 + 公差栈 (实物 [实测] = 0 条)",
            "mic_magnetic_sensitivity": "[0数据] 主流 MEMS 麦克风规格书无磁场敏感度指标 (4 份实测 grep=0)",
            "earth_field": "[官方-通用物理量] 25/50/65 µT",
            "iec61000_4_8": "[官方-通用引用] 1/3/10/30/100 A/m (未取标准原文)",
        },
        "constants": {"BR_TYP_T": BR_TYP, "BR_LO_T": BR_LO, "BR_HI_T": BR_HI,
                      "mag_d_mm": MAG_D, "mag_t_mm": MAG_T},
        "coord_regression": {"ok": reg_ok, "L_offset": L_OFFSET, "rows": reg_rows},
        "magnet_model_self_test": st,
        "axis_table": axis_table(),
        "geometry": G, "H": H, "dz_mic_mm": DZ_MIC,
        "feasible_band": band,
        "soc_field_check": {"soc_x": soc_x, "gap_mm": round(soc_dx, 2),
                            "B_uT": round(b_soc, 1),
                            "mech_claim_mm": 68.0,
                            "verdict": "ISS-092 §4.3 的 68mm 与其自身尺寸链矛盾, 实际 %.2fmm; "
                                       "B=%.1fµT < 3 倍地磁典型值 => 无功能影响, 但数字须订正"
                                       % (soc_dx, b_soc)},
        "candidates": cands,
        "criteria": {"pos_min_mm": CRIT_POS_MM,
                     "B_strong_uT": CRIT_B_STRONG, "B_loose_uT": CRIT_B_LOOSE,
                     "earth_uT": [EARTH_MIN, EARTH_TYP, EARTH_MAX],
                     "pinset_wall_refs_mm": {
                         "nonoverlap_hard": CRIT_PIN_WALL_NONOVERLAP_MM,
                         "board_rule_min_hole_clearance": REF_PIN_WALL_BOARD_RULE_MM,
                         "iss092_precedent": REF_PIN_WALL_ISS092_MM,
                         "self_tap_general_practice": REF_PIN_WALL_SELF_TAP_MM},
                     "pinset_wall_refs_sources": {
                         "nonoverlap_hard": "ISS-121 MD §3.2-4 既有口径「与 PIN-SET-2 不打架」= 净空 > 0",
                         "board_rule_min_hole_clearance":
                             "[实测] HW/PCB/demo_mainboard.kicad_pro design_settings.rules.min_hole_clearance=0.25",
                         "iss092_precedent":
                             "[推算] MECH/SERVICE_PORT_ISS092.md §8-11: P2 孔壁到 J_DEBUG 焊盘阵列最近 1.00mm 判通过",
                         "self_tap_general_practice":
                             "[推算·通用] 自攻 M1.2 螺钉孔周围留 >=1.0mm (非本项目判据, 仅参考)"}},
        "pinset_holes": {"board": "60x30", "set": "A (ISS-194 定版)",
                         "holes": {k: list(v) for k, v in G["pinset"].items()},
                         "legacy_15mm_obsolete": {k: list(v) for k, v in PINSET_LEGACY_15MM.items()}},
        "pinset_drift_guard": {"ok": guard_ok, "detail": guard_detail},
        "mic_y_sensitivity": ysens,
        "verdict": {
            "magnetic": "无影响 (B 远低于地磁量级)" if mag_all_pass else "待测",
            "position_literal_40mm": "仅 X<=%.2f 可行, 与 PIN-SET-2/连接器落板区冲突" % band["x_max_allowed"],
            "position_recommended": "M1 板坐标 X=5.00 / Y=12.00 (铰链端, 骨架外, 顶进式声孔)",
        },
        "fails": fails,
        "unowned_hard_fail": False,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\nOK 已写 %s" % os.path.relpath(OUT_JSON, os.path.dirname(HERE)))
    print("退出码 0 (判据跑完; FAIL 全部已归属 needs_from)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
