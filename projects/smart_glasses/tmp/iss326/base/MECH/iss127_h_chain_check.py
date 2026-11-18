#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-127 闭环检查 —— 电芯段 H 链量产几何 + 量产件脱模面统计口径
================================================================================
为什么要有这个脚本:
  ISS-025 (结构 DFM 评审) 算出一条**已定的不可能**: 镜脚主腔深 38.00mm, 沿 V 向脱模
  ⇒ 内腔横截面 (H×L) 沿拉出方向**变窄** 2·h·tan(α) ⇒ 电芯段 H 链量产最坏
  **−0.577mm** ⇒ 几何上做不出来。本脚本把「怎么改」固化成可复跑的判据。

★ 口径 (项目里有**两条**都叫「H 链」的链, 本脚本严格分开, 不许混用):
  链① **电芯段 H 链** (ISS-127 的控制链)
        皮肤壁 0.80 + 座深 4.75 + 顶板 0.80 = **6.35** vs 镜脚厚 **7.30**
        ⇒ 名义余量 0.95 / 量产最坏 0.75 (Δ=1×0.20) / 判据 **0.40** (=2×0.20, 注塑公差带)
        ⇒ DFM_REVIEW §2.1.2 的 −0.577 说的就是这条链
  链② **PCB/骨架堆叠 H 链** (BOARD_GEOM_30MM §5.4 / skeleton_section_check §4)
        外壁 0.80 + 骨架 1.00 + PCB t + 空隙 0.30 + 隔热垫 0.50 + 皮肤壁 0.80 = **3.40+t**
        (+石墨 0.30) vs 7.30 ⇒ 名义余量 3.49/3.10/2.90/2.68 (t=0.41/0.80/1.00/1.22)
        ⇒ ★这条链**从来不是** −0.577 的来源, 本脚本不许拿它去说 −0.577, 也不许拿
          −0.577 去否它

★ 脱模斜度的物理 (本脚本的核心, 也是本单最硬的结论):
    拉出方向 P ⇒ **垂直于 P 的截面**沿 P 变窄 ⇒ 损失 Δ = 2·h_P·tan(α)
      P = V (38.00 深) ⇒ 吃掉 **H 链 + L 链**  ⇒ 电芯段死 (Δ=1.327)
      P = H ( 5.70 深) ⇒ 吃掉 **V 链 + L 链**  ⇒ **H 链 Δ=0** ✅ ← 本单的解
      P = L (40.50 深) ⇒ 吃掉 **H 链 + V 链**  ⇒ H 链更死 (Δ=1.413) ⇒ **否决**
    ⇒ **唯一能把 H 链从脱模项里救出来的方向是 H 向分型** (皮肤盖 + 内胆)。
      电芯自身高 23.50 (V) ⇒ 在任何 V 向脱模里都不可能满足 0.40 判据 (脚本 §B 给证明)。

★ 本脚本不量实物 (本机物理上无法打印/量测, 见 MECH/print/ENV_PROBE_20261101.md)
  ⇒ 所有输出都是 **[推算]**, 不是 [实测]。量产公差带与斜度取值为通用工程经验值
  ⇒ 未按牌号/模具厂锁定 (DFM_REVIEW §6 needs_from #1/#3)。

用法:
    python3 MECH/iss127_h_chain_check.py              # 人读报告 (rc=0)
    python3 MECH/iss127_h_chain_check.py --json       # 机读
    python3 MECH/iss127_h_chain_check.py --self-test  # 自检 + 反向用例 (rc=0)
退出码: 0 = 复算完成 (**不代表实物已验**); 1 = 自检失败 / 输入自相矛盾
"""
from __future__ import annotations

import argparse
import json
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# ---------------------------------------------------------------------
# 锁定输入: 一律 import 既有脚本, **不另起一套数**
# ---------------------------------------------------------------------
from fit_check_v3_30mm import BASE, CRIT as CRIT_FDM, TOL           # noqa: E402
from skeleton_section_check import (AL_DENSITY, GR_DENSITY, SKELETON_T,  # noqa: E402
                                    GRAPHITE_T, H_OUTER_WALL, H_SKIN_WALL,
                                    H_AIR_GAP, H_INSUL_PAD, TEMPLE_H,
                                    BUDGET_SKELETON_G, W11_GRAPHITE_G,
                                    SOC_X_LEN, HOT_BAND)

# ---------------------------------------------------------------------
# 参数 (每个都标出处; 与 MECH/dfm_check.py §B/§C 同一口径)
# ---------------------------------------------------------------------
TOL_PROD_INJ = 0.20        # 注塑 PC/ABS 一般公差 (单边) [推算·通用] dfm_check.py TOL_PROD['inj_pcabs']
CRIT_PROD = 2 * TOL_PROD_INJ          # 量产链判据 = 2×单边公差 = 0.40  ★ISS-127 的 0.40 就是它
N_TOL_CELL = 1             # 电芯段链吃公差的界面数 (由 fit_check 最坏值反解) dfm_check.py §B
DRAFT_CASES = (0.5, 1.0, 1.5)   # 皮纹面 0.5° / 通用 1.0° / 光面 1.5°  (mech_dfm_draft_texture 未裁 ⇒ 三档全跑)
DRAFT_CASE_LABEL = {0.5: "皮纹面 α=0.5°", 1.0: "通用 α=1.0°", 1.5: "光面 α=1.5°"}

# 电芯段链的构成 (fit_check_v3_30mm §2: h_cell = wall + 4.75 + wall)
CELL_SEAT_DEPTH = 4.75     # 非对称电池座深 [推算] fit_check_v3_30mm §2
CELL_OFFSET = 0.15         # 座深 4.75 = 电芯 4.60 + 偏置 0.15 [推算]

# 主腔与分型 (现状: V 向脱模, 38.00 深)
CAV_V_MAIN = BASE["cav_v"]  # 38.00 镜脚主腔深 (V) [锁死]
CAV_H_INNER = TEMPLE_H - 2 * H_OUTER_WALL   # 5.70 主腔 H 向净深 (H 向分型时的抽芯行程)
CAV_L_CELL = BASE["cell_l"]                # 40.50 电芯段腔长 (L)

# 方案定义 (见 MECH/ISS127_H_CHAIN_SOLUTION.md §C)
#   pull = "H" ⇒ 垂直于 H 的截面 (V×L) 变窄 ⇒ H 链 Δ = 0
#   pull = "V" ⇒ 垂直于 V 的截面 (H×L) 变窄 ⇒ H 链 Δ = 2·38·tanα
OPTIONS = {
    "P0": dict(
        name="现状基线: 单壳, 主腔沿 V 向脱模 (38.00 深)",
        pull_cell="V", pull_pcb="V",
        metal_delta_g=0.0, graphite_trim=False, parts_per_side=3,
        molds_per_side=1, risk="★几何上做不出来 (ISS-127 原结论)",
    ),
    "P1": dict(
        name="★推荐: H 向分型 (皮肤盖 + 内胆) + 电池座=独立 0.5mm CNC 嵌件 + 石墨裁到 SoC 带",
        pull_cell="H", pull_pcb="H",
        metal_delta_g=None, graphite_trim=True, parts_per_side=4,
        molds_per_side=2, risk="皮肤盖 0.8mm×130mm 跨距刚度; 接缝防汗; 分型面位置",
    ),
    "P2": dict(
        name="备选: 局部 H 向分型 (只在电芯段开盖) + PCB 段维持 V 向单壳 + 电池座=独立 0.5mm CNC 嵌件",
        pull_cell="H", pull_pcb="V",
        metal_delta_g=None, graphite_trim=True, parts_per_side=4,
        molds_per_side=2, risk="改动面最小; 但 PCB 段仍吃 1.327 (链② 余量够, 不影响结论)",
    ),
    "P3": dict(
        name="已否决: 金属电池舱块 (0.5mm 折弯铝五面盒) + 内胆掏空",
        pull_cell="H", pull_pcb="H",
        metal_delta_g=None, graphite_trim=False, parts_per_side=3,
        molds_per_side=1, risk="★几何最稳但重量判死 (见 §C 重量账)",
    ),
}

# 电池座几何 (CNC Al6063, 独立件; ★**不得延伸进电池段与骨架共体** —— 金属直灌皮肤,
# 见 skeleton_section_check.py 硬约束 skeleton_stops_at_pcb_rear_edge)
SEAT_T = 0.50             # 壁厚 mm [推算·本单取值]
SEAT_PLATE_L = BASE["cell_l"]        # 40.50 承力底板长
SEAT_PLATE_H = BASE["cell_thk"]      # 4.60 承力底板宽 (= 电芯厚)
SEAT_RIB_L = BASE["cell_l"]          # 40.50 H 向定位筋长
SEAT_RIB_H = 1.50                   # 1.50 定位筋宽
SEAT_STOP_H = BASE["cell_thk"]       # 4.60 止挡宽
SEAT_STOP_L = 4.00                  # 4.00 止挡长
SEAT_BOSS_N = 2                     # 2 个 M1.2 凸台

# 金属舱块 (P3, 否决项): 0.5mm 壁五面盒
BOX_WALL_T = 0.50
BOX_CLEAR = 0.80                    # 每侧余量


# =====================================================================
# 核心算式 (全部与 MECH/dfm_check.py §B/§C 同口径)
# =====================================================================
def draft_loss(h: float, alpha_deg: float) -> float:
    """内腔横截面沿拉出方向的收窄量 Δ = 2·h·tan(α)  (dfm_check.py §C 同一式)"""
    return 2.0 * h * math.tan(math.radians(alpha_deg))


def h_loss_for_chain(pull: str, alpha_deg: float, h_cav_v: float = CAV_V_MAIN,
                      h_cav_h: float = CAV_H_INNER) -> float:
    """该拉出方向下, **H 链**被吃掉的脱模损失.

    物理: 拉出方向 P ⇒ 垂直于 P 的截面沿 P 变窄 ⇒ H 链被吃 ⇔ H ⟂ P。
      P=V ⇒ H 链吃 2·h_V·tanα (h_V = 38.00) ⇒ 1.327 @1°
      P=H ⇒ H 链不吃 (H ∥ P, 沿拉出方向是精确的) ⇒ 0
    """
    if pull == "H":
        return 0.0
    if pull == "V":
        return draft_loss(h_cav_v, alpha_deg)
    raise ValueError(pull)


def chain_cell(nominal_need: float = None, cav_h: float = None, alpha_deg: float = 0.0,
               pull: str = "V", n_tol: int = N_TOL_CELL, t_prod: float = TOL_PROD_INJ,
               extra_loss: float = 0.0) -> dict:
    """链① **电芯段 H 链** (ISS-127 控制链)."""
    need = (CELL_SEAT_DEPTH + 2 * BASE["wall"]) if nominal_need is None else nominal_need
    avail = BASE["cav_h"] if cav_h is None else cav_h
    margin = avail - need
    worst_tol = margin - n_tol * t_prod
    loss = h_loss_for_chain(pull, alpha_deg) + extra_loss
    worst = worst_tol - loss
    crit = 2 * t_prod
    return dict(need=need, avail=avail, margin=margin, worst_tol=worst_tol,
                loss=loss, worst=worst, crit=crit, ok=worst >= crit)


def chain_pcb(pcb_t: float, alpha_deg: float = 0.0, pull: str = "V",
              graphite: float = 0.0, t_prod: float = TOL_PROD_INJ,
              n_tol: int = 1) -> dict:
    """链② **PCB/骨架堆叠 H 链** (BOARD_GEOM_30MM §5.4 口径)."""
    need = (H_SKIN_WALL + H_INSUL_PAD + H_AIR_GAP + pcb_t +
            SKELETON_T + H_OUTER_WALL + graphite)
    margin = TEMPLE_H - need
    worst_tol = margin - n_tol * t_prod
    loss = h_loss_for_chain(pull, alpha_deg)
    worst = worst_tol - loss
    crit = 2 * t_prod
    return dict(need=need, margin=margin, worst_tol=worst_tol, loss=loss,
                worst=worst, crit=crit, ok=worst >= crit)


def chain_v(alpha_deg: float = 0.0, pull: str = "V", t_prod: float = TOL_PROD_INJ,
            n_tol: int = 2) -> dict:
    """链③ **镜脚·V** (板宽 30 + 走线槽 6.00 vs 净高 38.00); 判据同 0.40."""
    need = 30.0 + BASE["duct_v"]
    margin = BASE["cav_v"] - need
    worst_tol = margin - n_tol * t_prod
    loss = 0.0 if pull == "V" else draft_loss(CAV_H_INNER, alpha_deg)
    worst = worst_tol - loss
    return dict(need=need, margin=margin, worst_tol=worst_tol, loss=loss,
                worst=worst, crit=2 * t_prod, ok=worst >= 2 * t_prod)


def chain_l(alpha_deg: float = 0.0, pull: str = "V", t_prod: float = TOL_PROD_INJ,
            n_tol: int = 3) -> dict:
    """链④ **镜脚·L** (电芯 40.5 + 板长 60 + 余量 15 vs 130.00)."""
    need = BASE["cell_l"] + 60.0 + BASE["conn_margin"]
    margin = BASE["cav_l"] - need
    worst_tol = margin - n_tol * t_prod
    loss = draft_loss(CAV_V_MAIN, alpha_deg) if pull == "V" else draft_loss(CAV_H_INNER, alpha_deg)
    worst = worst_tol - loss
    return dict(need=need, margin=margin, worst_tol=worst_tol, loss=loss,
                worst=worst, crit=2 * t_prod, ok=worst >= 2 * t_prod)


# =====================================================================
# 重量账 (对着 BOARD_GEOM_30MM §5 的 4.08g/对 与 MECH_BUDGET §3 W11 的 2.16g/对 说增量)
# =====================================================================
def skeleton_cand_c_vol() -> float:
    """骨架候选 C 体积 cc (台阶: SoC 段满宽 30×17.20×0.8 + 其余段 10 宽×0.8)."""
    hot = SOC_X_LEN * 30.0 * 0.80
    rest = (60.0 - SOC_X_LEN) * 10.0 * 0.80
    return hot + rest


def graphite_vol(full: bool = True) -> float:
    """石墨片体积 cc. full=True ⇒ 满板 60×30×0.30; False ⇒ 裁到 SoC 段+逃线带."""
    if full:
        return 60.0 * 30.0 * GRAPHITE_T
    return (SOC_X_LEN + 2 * 5.0) * 30.0 * GRAPHITE_T      # 5.00 = X 向逃线带 [推算]


def seat_vol(t: float = SEAT_T) -> float:
    """电池座 (CNC Al6063) 体积 cc."""
    plate = SEAT_PLATE_L * SEAT_PLATE_H * t
    rib = SEAT_RIB_L * SEAT_RIB_H * t
    stop = SEAT_STOP_H * SEAT_STOP_L * t
    boss = SEAT_BOSS_N * 2.56 * 3.0            # ⌀1.6 攻丝凸台近似柱 ⌀2.56×3.0
    return plate + rib + stop + boss


def metal_box_vol(t: float = BOX_WALL_T) -> float:
    """金属电池舱块 (五面盒) 的**金属**体积 cc (只算壁, 不算与电芯之间的空隙)."""
    cl, cv, ct = BASE["cell_l"], BASE["cell_v"], BASE["cell_thk"]
    end_plates = 2 * t * (cv + 2 * t) * (ct + 2 * t)          # L 向两端板
    top_bottom = 2 * cl * t * (ct + 2 * t)                     # V 向上下板
    back = cl * (cv + 2 * t) * t                              # H 向外背板 (顶板)
    return end_plates + top_bottom + back                     # mm³


def weight_ledger(opt: str) -> dict:
    """某方案的金属+石墨总账 (g/对) 与相对基线的增量."""
    base_skel = skeleton_cand_c_vol() / 1000.0 * AL_DENSITY * 2
    base_gr = graphite_vol(True) / 1000.0 * GR_DENSITY * 2
    base_total = base_skel + base_gr

    o = OPTIONS[opt]
    if opt == "P0":
        skel, gr = base_skel, base_gr
        seat = 0.0
    elif opt == "P3":
        skel, gr = base_skel, base_gr
        seat = metal_box_vol() / 1000.0 * AL_DENSITY * 2
    else:
        skel = base_skel
        gr = (graphite_vol(False) if o["graphite_trim"] else base_gr) / 1000.0 * GR_DENSITY * 2
        seat = seat_vol() / 1000.0 * AL_DENSITY * 2
    total = skel + gr + seat
    return dict(skeleton_g=skel, graphite_g=gr, seat_g=seat, total_g=total,
                base_total_g=base_total, delta_g=total - base_total,
                budget_skeleton_g=BUDGET_SKELETON_G, w11_graphite_g=W11_GRAPHITE_G,
                within_budget=(total - base_total) <= 0.0)


# =====================================================================
# 脱模面统计 (量产件口径, 见 §E)
# =====================================================================
BUCKETS = ["FLAT_TOP", "FLAT_BOTTOM", "DRAFTED", "ZERO_DRAFT", "UNDERCUT"]


def classify(nz: float, dmin: float = 1.0):
    """法向 n 的 z 分量 → (桶名, α)。口径与 dfm_check.py 完全一致。"""
    cos_flat = math.cos(math.radians(45.0))
    sin_min = math.sin(math.radians(dmin))
    if nz >= cos_flat:
        return "FLAT_TOP", None
    if nz <= -cos_flat:
        return "FLAT_BOTTOM", None
    alpha = 90.0 - math.degrees(math.acos(max(-1.0, min(1.0, nz))))
    if nz < -sin_min:
        return "UNDERCUT", alpha
    if nz <= sin_min:
        return "ZERO_DRAFT", alpha
    return "DRAFTED", alpha


def stl_face_stats(path: str):
    """纯 python 读二进制 STL, 按三角面法向统计 (★绕向敏感 ⇒ 只作现状基线)."""
    with open(path, "rb") as fh:
        data = fh.read()
    n_tri = struct.unpack("<I", data[80:84])[0]
    count = {b: 0 for b in BUCKETS}
    area = {b: 0.0 for b in BUCKETS}
    undercuts = []
    off = 84
    for _ in range(n_tri):
        vals = struct.unpack("<12fH", data[off:off + 50])
        off += 50
        v = [(vals[3], vals[4], vals[5]), (vals[6], vals[7], vals[8]),
             (vals[9], vals[10], vals[11])]
        u = [v[1][i] - v[0][i] for i in range(3)]
        w = [v[2][i] - v[0][i] for i in range(3)]
        nx = u[1] * w[2] - u[2] * w[1]
        ny = u[2] * w[0] - u[0] * w[2]
        nz = u[0] * w[1] - u[1] * w[0]
        ln = math.sqrt(nx * nx + ny * ny + nz * nz)
        if ln < 1e-12:
            continue
        tri_area = 0.5 * ln
        b, alpha = classify(nz / ln)
        count[b] += 1
        area[b] += tri_area
        if b == "UNDERCUT":
            undercuts.append((alpha, tri_area))
    total = sum(area.values())
    return dict(n_tri=n_tri, count=count, area=area, total_area=total,
                undercuts=sorted(undercuts, key=lambda t: -t[1]))


def revb_face_stats():
    """Rev B 打印包面级统计: 优先走 dfm_check.py 的解析图元表 (需 numpy);
    numpy 不可用时退回 STL 采样 (绕向敏感 ⇒ 仅现状基线)。"""
    out = {"mode": None, "parts": []}
    try:
        import dfm_check as D  # noqa: F401  (它自己 import print_model_revb → numpy)
        import print_model_revb as PM
        from gen_print_pack_revb import build_coupon, build_temple_cage, build_frame_typec
        for name, builder in (("fit_coupon", build_coupon), ("temple_cage", build_temple_cage),
                              ("frame_typec", build_frame_typec)):
            PM.reset()
            builder()
            model = list(PM.MODEL)
            acc = D.Acc()
            D.acc_model(model, acc)
            out["mode"] = "analytic (dfm_check.py §A 解析图元表)"
            out["parts"].append(dict(
                name=name, total_area=acc.total_area,
                area=dict(acc.area), count=dict(acc.count),
                undercuts=[(a, ar) for a, ar, _ in acc.undercuts]))
        return out
    except Exception as exc:                      # noqa: BLE001
        out["mode"] = f"STL 采样 (numpy 不可用: {exc.__class__.__name__})"
        for fn in ("fit_coupon_revb.stl", "temple_cage_revb.stl", "frame_typec_coupon_revb.stl"):
            p = os.path.join(HERE, "print", fn)
            if not os.path.exists(p):
                continue
            st = stl_face_stats(p)
            out["parts"].append(dict(
                name=fn.replace("_revb.stl", ""), total_area=st["total_area"],
                area=st["area"], count=st["count"],
                undercuts=st["undercuts"]))
        return out


# 量产件脱模面判据 (立"尺子"用; Rev B 统计只作现状基线)
PROD_FACE_CRITERIA = [
    ("E1", "倒扣面 (α<0) 数量", "= 0", "注塑/压铸出不来 (FDM 能打是假象) ⇒ 一票否决",
     "Rev B fit_coupon 现状 2 个 (α=−40°/−30°)"),
    ("E2", "ZERO_DRAFT 面积占比", "≤ 30% (参考线, 非主判据)",
     "与拉出方向**平行**的直壁面是合法的 (棱柱件沿轴向拉出不需要斜度) ⇒ 占比只作参考",
     "Rev B 现状 25.0% / 61.9% / 59.8% (检具+试样, 非量产外形件)"),
    ("E3", "承力/定位/配合链上的 ZERO_DRAFT 直壁面数", "= 0 (主判据)",
     "直壁 ⇒ 该链的脱模损失全额计入 ⇒ 直壁落在关键链上就是红线",
     "本单: 电芯段链上的主腔内壁 = 2 个面 ⇒ 必须改 (方案 P1/P2 把它移出该链)"),
    ("E4", "每条链的脱模损失 Δ", "≤ 该链余量预算",
     "电芯段链 Δ≤0.35 (0.75−0.40); 链② Δ≤余量−0.20−0.40; 链③/④ 同理",
     "现状: 链① Δ=1.327 ⇒ 超 0.977 ⇒ ISS-127"),
    ("E5", "每个腔的登记项", "(拉出方向, 腔深, 受影响链, α, Δ) 5 项齐全",
     "没登记 ⇒ 不许开模 (DFM_REVIEW §6 needs_from #6: 量产外形件 0 数据点)",
     "Rev B 无任何腔级登记"),
    ("E6", "量产外形件数据点", "≥ 1 套量产件或图纸的面级统计",
     "现在的 0 数据点状态不得当合格判据 (DFM_REVIEW §3.5)",
     "现状 0 个数据点"),
]


# =====================================================================
# 报告各节
# =====================================================================
def sec_a_and_baseline():
    lines = []
    A = lines.append
    A("=" * 100)
    A("【A】口径钉死 —— 项目里有两条都叫「H 链」的链, 本脚本严格分开")
    A("=" * 100)
    A("  链① **电芯段 H 链** (ISS-127 的控制链; DFM_REVIEW §2.1.2)")
    A(f"        皮肤壁 {BASE['wall']:.2f} + 座深 {CELL_SEAT_DEPTH:.2f} + 顶板 {BASE['wall']:.2f}"
      f" = **{CELL_SEAT_DEPTH + 2 * BASE['wall']:.2f}** vs 镜脚厚 {BASE['cav_h']:.2f}")
    A(f"        ⇒ 名义余量 {BASE['cav_h'] - (CELL_SEAT_DEPTH + 2 * BASE['wall']):.2f} / "
      f"量产最坏 {BASE['cav_h'] - (CELL_SEAT_DEPTH + 2 * BASE['wall']) - N_TOL_CELL * TOL_PROD_INJ:.2f} "
      f"/ 判据 **{CRIT_PROD:.2f}** (=2×注塑单边公差 {TOL_PROD_INJ:.2f})")
    A("  链② **PCB/骨架堆叠 H 链** (BOARD_GEOM_30MM §5.4 / skeleton_section_check §4)")
    A(f"        外壁 {H_OUTER_WALL:.2f} + 骨架 {SKELETON_T:.2f} + PCB t + 空隙 {H_AIR_GAP:.2f} "
      f"+ 隔热垫 {H_INSUL_PAD:.2f} + 皮肤壁 {H_SKIN_WALL:.2f} = 3.40+t vs {TEMPLE_H:.2f}")
    A("        ⇒ 名义余量 3.49/3.10/2.90/2.68 (t=0.41/0.80/1.00/1.22); +石墨 0.30 再减 0.30")
    A("  ★ 两条链**不许混用**: −0.577 说的是链①; 链② 现在是 ✅ (本脚本 §D 逐档给数)")
    A("")
    A("=" * 100)
    A("【A2】现状基线复算 (链①, 主腔沿 V 向脱模 38.00 深) —— 逐条与 dfm_check.py §B 对齐")
    A("=" * 100)
    base_rows = []
    for a in DRAFT_CASES:
        r = chain_cell(alpha_deg=a, pull="V")
        base_rows.append((a, r))
        A(f"  α={a:.1f}°  Δ脱模={r['loss']:.3f} ⇒ 量产最坏 {r['worst']:.3f} "
          f"(判据 ≥{r['crit']:.2f}) {'✅' if r['ok'] else '❌  ← 几何上做不出来'}")
    A(f"  ★ 与 MECH/DFM_REVIEW.md §2.1.2 逐字一致: 0.5°→0.087 / 1.0°→−0.577 (本脚本 1.5°→−1.240)")
    A("")
    return lines, base_rows


def sec_b_proof():
    """为什么「靠公差/斜度」无解 —— 几何证明."""
    lines = []
    A = lines.append
    A("=" * 100)
    A("【B】★ 为什么靠公差/斜度救不回来 (几何证明, 不靠直觉)")
    A("=" * 100)
    A(f"  判据要求: 电芯段链 Δ脱模 ≤ 量产最坏 0.75 − 判据 0.40 = **0.35mm**")
    A(f"  脱模损失 Δ = 2·h·tan(α) (h = 腔在**拉出方向**上的深度)")
    A(f"  ⇒ 允许的等效腔深 h_max = 0.35 / (2·tanα):")
    for a in DRAFT_CASES:
        hmax = 0.35 / (2 * math.tan(math.radians(a)))
        A(f"      α={a:.1f}° ⇒ h_max = **{hmax:.2f}mm**")
    A(f"  ★ 而电芯自身高 **{BASE['cell_v']:.2f}mm** (V 向) ⇒ 在任何 V 向脱模的腔里,")
    A(f"    电芯的**最高面**必然高于 h_max ⇒ 必然落在窄端 ⇒ **无解**")
    A(f"    (例 α=1.0°: 电芯顶面需 ≤ 10.03 ⇒ 电芯底面 ≤ −13.47 ⇒ 跨过分型面, 物理不可能)")
    A("  ⇒ **只有把拉出方向换成 H (电芯厚度方向) 才能让 H 链 Δ=0**;")
    A(f"    V 向分型 (上下分壳) 分型面若落在电芯半高处 (h=±{BASE['cell_v'] / 2:.2f}) ⇒ "
      f"Δ = 2×{BASE['cell_v'] / 2:.2f}·tanα:")
    for a in DRAFT_CASES:
        d = draft_loss(BASE["cell_v"] / 2.0, a)
        w = chain_cell()["worst_tol"] - d
        A(f"      α={a:.1f}° ⇒ Δ={d:.3f} ⇒ 最坏 {w:.3f} {'✅ (勉强)' if w >= CRIT_PROD else '❌'}")
    A("    ⇒ **只有皮纹 0.5° 情形勉强过, 且依赖电芯 V 位置假设** ⇒ 不作推荐 (且它不解决光面 1.5° 档)")
    A(f"  ⇒ L 向脱模更差: Δ = 2·{CAV_L_CELL:.2f}·tan1° = {draft_loss(CAV_L_CELL, 1.0):.3f} "
      f"> {draft_loss(CAV_V_MAIN, 1.0):.3f} (现状) ⇒ **否决**")
    A("")
    return lines


def sec_faces():
    """面级最小改造集 (B 节交付物)."""
    lines = []
    A = lines.append
    A("=" * 100)
    A("【B2】面级最小改造集 (必须改的面) —— 链① 从 −0.577 回到 ≥0.40")
    A("=" * 100)
    A("  面 ID | 面名 | 所属件 | 当前 α | 当前腔深(拉出方向) | 当前截面贡献 | 目标 | 目标截面 | 改后链①最坏")
    rows = [
        ("F1", "主腔·H 向两侧内壁 (电芯段)", "镜脚壳 (V 向脱模)", "1.0 (0.5 皮纹 / 1.5 光面)",
         f"{CAV_V_MAIN:.2f} (V)", f"2·38·tanα = {draft_loss(CAV_V_MAIN, 1.0):.3f} (1°)",
         "改为 H 向分型 ⇒ 该面与拉出方向平行", "Δ_H = 0",
         f"{chain_cell(alpha_deg=1.0, pull='H')['worst']:.3f} (未计 F2)"),
        ("F2", "皮肤盖·外表面 (贴肤面)", "皮肤盖 (H 向脱模)", "0.5 或 1.5 (待裁)",
         f"{BASE['wall']:.2f} (H)", f"2·0.8·tanα = {draft_loss(BASE['wall'], 1.5):.3f} (1.5°)",
         "分型面放在盖的内表面 ⇒ 贴肤面是型腔底 ⇒ **零斜度**", "Δ_H ≤ 0.042",
         f"{chain_cell(alpha_deg=1.5, pull='H', extra_loss=draft_loss(BASE['wall'], 1.5))['worst']:.3f}"),
        ("F3", "电芯座 H 向定位台阶 (槽壁 ∥ 拉出方向)", "内胆 (H 向脱模)", "0 (合法直壁)",
         f"{CAV_H_INNER:.2f} (H)", "0 (H 链 Δ=0)", "保留, 不改", "0", "—"),
        ("F4", "主腔·V 向底面 (承力面)", "内胆", "0 (分型面)", "—", "0", "保留, 不改", "0", "—"),
        ("F5", "主腔·PCB 段·H 向两侧内壁", "内胆", "1.0", f"{CAV_V_MAIN:.2f} (V)",
         f"{draft_loss(CAV_V_MAIN, 1.0):.3f}", "同 F1 一次改掉 (H 向分型)", "Δ_H = 0", "链② 见 §D"),
        ("F6", "隔热垫 0.5 + 空气隙 0.3 台阶", "内胆 / 皮肤盖", "0 (整体台阶)",
         "—", "0", "改为盖内表面上的整体台阶 (不靠装配塞垫)", "0", "链② 不变"),
    ]
    for r in rows:
        A("  " + " | ".join(str(x) for x in r))
    A("")
    A(f"  ★ 需要补回: α=1.0° 情形 **≥0.977** (0.75−0.40+0.577); 改后实际补回 "
      f"**{chain_cell(alpha_deg=1.0, pull='H')['worst'] - chain_cell(alpha_deg=1.0, pull='V')['worst']:+.3f}**")
    A(f"  ★ 两种脱模角情形 (老板 `mech_dfm_draft_texture` due 11-10 已逾期 ⇒ 不许假设已定):")
    for a in DRAFT_CASES:
        r0 = chain_cell(alpha_deg=a, pull="V")
        r1 = chain_cell(alpha_deg=a, pull="H")
        need = CRIT_PROD - r0["worst"]
        A(f"      {DRAFT_CASE_LABEL[a]:<14} 现状最坏 {r0['worst']:+.3f} ⇒ 需补回 {need:+.3f} "
          f"⇒ 方案 P1 后最坏 **{r1['worst']:.3f}** {'✅' if r1['ok'] else '❌'} "
          f"(补回 {r1['worst'] - r0['worst']:+.3f})")
    A("")
    return lines


def sec_options():
    lines = []
    A = lines.append
    A("=" * 100)
    A("【C】量产架构方案 (方向已裁: 打印件造型 + 金属件定位/承力 ⇒ 电池座/PCB 座改 CNC 嵌件)")
    A("=" * 100)
    for key in ("P1", "P2", "P3"):
        o = OPTIONS[key]
        A(f"  ── {key}: {o['name']}")
        A(f"     拉出方向: 电芯段 = {o['pull_cell']} | PCB 段 = {o['pull_pcb']} "
          f"| 零件数/侧 = {o['parts_per_side']} | 模具/侧 = {o['molds_per_side']} 套")
        for a in DRAFT_CASES:
            rc = chain_cell(alpha_deg=a, pull=o["pull_cell"])
            rp = chain_pcb(1.00, alpha_deg=a, pull=o["pull_pcb"])
            A(f"     链① 电芯段 α={a:.1f}°: Δ={rc['loss']:.3f} ⇒ 最坏 {rc['worst']:.3f} "
              f"(判据 ≥{rc['crit']:.2f}) {'✅' if rc['ok'] else '❌'}   |   "
              f"链② t=1.00: Δ={rp['loss']:.3f} ⇒ 最坏 {rp['worst']:.3f} "
              f"{'✅' if rp['ok'] else '❌'}")
        w = weight_ledger(key)
        A(f"     重量账: 骨架 {w['skeleton_g']:.2f} + 石墨 {w['graphite_g']:.2f} + 电池座/舱块 "
          f"{w['seat_g']:.2f} = **{w['total_g']:.2f} g/对** "
          f"(基线 {w['base_total_g']:.2f} ⇒ 增量 **{w['delta_g']:+.2f} g/对**) "
          f"{'✅ 重量账内 (不恶化超账)' if w['within_budget'] else '❌ 超账'}")
        A(f"     风险: {o['risk']}")
        A("")
    A("  ★ **推荐项 = P1** (H 向分型 + 电池座独立 0.5mm CNC 嵌件 + 石墨裁到 SoC 带):")
    A("     ① 几何: 拉出方向改 H ⇒ 链① 的脱模项 **Δ=0** ⇒ 三档 α (0.5/1.0/1.5) **全部**过 0.40,")
    A("        且把 boss 的 `mech_dfm_draft_texture` 决策**从几何链上摘掉** (只剩外观/触感)。")
    A("     ② 重量: 电池座 0.5mm 薄壁 + 石墨按 SoC 带裁剪 ⇒ 相对基线 **净减** (见上表) ⇒ 重量账内。")
    A("     ③ 与已裁方向一致: 电池座仍是 CNC 金属嵌件 (独立件, **不与骨架共体** —— 金属直灌皮肤, "
      "见 skeleton_section_check 硬约束 skeleton_stops_at_pcb_rear_edge)。")
    A("     ④ P2 是 P1 的「改动面最小」变体 (只在电芯段开局部盖); P3 已按重量判死, 数字留在案上。")
    A("")
    return lines


def sec_board_tiers():
    lines = []
    A = lines.append
    A("=" * 100)
    A("【D】板厚四档 (ISS-122 层数未定 ⇒ t = 0.41/0.80/1.00/1.22, ISS-126) —— 链② 逐档")
    A("=" * 100)
    A(f"  {'方案/α':<14}{'板厚':>7}{'链②需求':>10}{'名义余量':>10}{'量产最坏':>10}{'含石墨后':>10}   判定")
    rows = []
    for key in ("P0", "P1", "P2"):
        o = OPTIONS[key]
        for a in DRAFT_CASES:
            for t in BASE["pcb_thk"]:
                r = chain_pcb(t, alpha_deg=a, pull=o["pull_pcb"])
                rg = chain_pcb(t, alpha_deg=a, pull=o["pull_pcb"], graphite=GRAPHITE_T)
                A(f"  {key + '/' + str(a) + '°':<14}{t:>7.2f}{r['need']:>10.2f}{r['margin']:>10.2f}"
                  f"{r['worst']:>10.3f}{rg['worst']:>10.3f}   "
                  f"{'✅' if (r['ok'] and rg['ok']) else ('⚠️ 含石墨破线' if r['ok'] else '❌')}")
                rows.append((key, a, t, r, rg))
    A("")
    A("  ★ 四档**全部**成立 (P1/P2 下 Δ_H=0 ⇒ 与 α 无关); P0 现状在 α=1.5° 且含石墨、t=1.22 时")
    A("    链② = 0.193 < 0.40 ⇒ **破线** ⇒ 这是本单顺带查出的一条**新问题** (DFM 评审从未把链②")
    A("    按 0.40 判据核过); P1/P2 直接把它消掉。")
    A("  ⚠️ **本单不修 ISS-126**: 检修口净空 5.29/4.90/4.70/**4.48** (t=1.22 破 4.50 硬要求, 差 0.02)")
    A("    —— 那条链与本单的脱模项无关, 属 ISS-092/ISS-126, 不许在这里偷偷改口径。")
    A("")
    return lines, rows


def sec_face_criteria():
    lines = []
    A = lines.append
    A("=" * 100)
    A("【E】量产件脱模面统计口径 (现在 0 个数据点 ⇒ 先立尺子)")
    A("=" * 100)
    A("  判据表 (量产外形件用; Rev B 统计**只作现状基线**, 不作合格判据):")
    A(f"    {'ID':<4}{'判据项':<40}{'阈值':<22}说明")
    for cid, item, thr, why, now in PROD_FACE_CRITERIA:
        A(f"    {cid:<4}{item:<40}{thr:<22}{why}")
        A(f"        └ 现状: {now}")
    A("")
    A("  ★ **口径的核心修正 (本单新增)**: 「ZERO_DRAFT 面占比」**不是**主判据 ——")
    A("    与拉出方向**平行**的直壁面 (棱柱侧壁) 是合法的 (沿轴向拉出不需要斜度);")
    A("    真正致命的是「**落在沿拉出方向收缩的截面上的**直壁面」⇒ 判定必须落到**链级 Δ** (E4)。")
    A("    ⇒ 所以尺子 = 「E3 直壁面归属登记 + E4 链级 Δ + E1 倒扣面为 0」, E2 只作参考线。")
    A("")
    st = revb_face_stats()
    A(f"  Rev B 现状基线 (统计模式: {st['mode']}) [推算·**不是**合格判据]:")
    for p in st["parts"]:
        tot = max(p["total_area"], 1e-9)
        zer = 100.0 * p["area"].get("ZERO_DRAFT", 0.0) / tot
        und = 100.0 * p["area"].get("UNDERCUT", 0.0) / tot
        A(f"    {p['name']:<14} 总面积 {p['total_area']:10.2f} mm² | ZERO_DRAFT {zer:5.1f}% "
          f"| UNDERCUT {und:5.1f}% ({len(p['undercuts'])} 面)")
        if p["undercuts"]:
            for a, ar in p["undercuts"][:3]:
                A(f"        倒扣面 α={a:+7.2f}°  面积 {ar:9.2f} mm²")
    A("    (权威现状基线 = DFM_REVIEW §7: 25.0% / 61.9% / 59.8% + fit_coupon 2 个倒扣面 "
      "α=−40°/−30° —— 用解析图元表精确求, 不在 STL 上采样)")
    A("")
    return lines


def sec_weight():
    lines = []
    A = lines.append
    A("=" * 100)
    A("【C2】重量账 (对着 4.08g/对 骨架 与 W11 2.16g/对 石墨 说增量)")
    A("=" * 100)
    base_skel = skeleton_cand_c_vol() / 1000.0 * AL_DENSITY * 2
    base_gr = graphite_vol(True) / 1000.0 * GR_DENSITY * 2
    A(f"  基线: 骨架候选 C {skeleton_cand_c_vol() / 1000.0:.4f}cc × {AL_DENSITY} g/cc × 2 = "
      f"**{base_skel:.2f} g/对** (骨架预算 +1~3g ⇒ 超 {base_skel - BUDGET_SKELETON_G:.2f})")
    A(f"        石墨满板 {graphite_vol(True) / 1000.0:.4f}cc × {GR_DENSITY} g/cc × 2 = **{base_gr:.2f} g/对** "
      f"(W11 1~2g ⇒ 超 {base_gr - W11_GRAPHITE_G[1]:.2f})")
    A(f"        ⇒ 基线金属+石墨合计 **{base_skel + base_gr:.2f} g/对**")
    A(f"  电池座 (0.5mm CNC Al6063, 独立件): {seat_vol():.1f}mm³ → "
      f"{seat_vol() / 1000.0 * AL_DENSITY:.3f} g/侧 → **{seat_vol() / 1000.0 * AL_DENSITY * 2:.2f} g/对**")
    A(f"  金属舱块 (0.5mm 五面盒, P3): {metal_box_vol():.1f}mm³ → "
      f"{metal_box_vol() / 1000.0 * AL_DENSITY:.2f} g/侧 → "
      f"**{metal_box_vol() / 1000.0 * AL_DENSITY * 2:.2f} g/对** ⇒ **判死**")
    A(f"  石墨裁到 SoC 段+逃线带 ({graphite_vol(False) / 1000.0:.4f}cc): "
      f"{graphite_vol(False) / 1000.0 * GR_DENSITY * 2:.2f} g/对 "
      f"(↓ {base_gr - graphite_vol(False) / 1000.0 * GR_DENSITY * 2:.2f} g/对)")
    A("")
    A(f"  {'方案':<6}{'骨架':>8}{'石墨':>8}{'座/舱':>8}{'合计':>9}{'增量':>9}   重量账")
    for key in ("P0", "P1", "P2", "P3"):
        w = weight_ledger(key)
        A(f"  {key:<6}{w['skeleton_g']:>8.2f}{w['graphite_g']:>8.2f}{w['seat_g']:>8.2f}"
          f"{w['total_g']:>9.2f}{w['delta_g']:>+9.2f}   "
          f"{'— (基线本身)' if key == 'P0' else ('✅ 账内 (≤基线)' if w['within_budget'] else '❌ 超基线')}")
    A("")
    A("  ★ 判据 (本单自定, 写进脚本): **方案的「金属+石墨」合计 ≤ 基线 6.24 g/对**")
    A("    ⇒ 已在超账的基础上**不再加钱**; P1/P2 达标, P3 判死。")
    A("")
    return lines


def sec_other_chains():
    """链③ V / 链④ L (拉出方向改变后, 脱模损失落到这两条链上)."""
    lines = []
    A = lines.append
    A("=" * 100)
    A("【D2】链③ 镜脚·V 与 链④ 镜脚·L —— 换拉出方向后, 脱模损失落到这两条链上")
    A("=" * 100)
    A(f"  {'方案/α':<12}{'链③V 最坏':>12}{'链③ Δ':>10}{'链④L 最坏':>12}{'链④ Δ':>10}   判定")
    for key in ("P0", "P1", "P2"):
        o = OPTIONS[key]
        for a in DRAFT_CASES:
            v = chain_v(alpha_deg=a, pull=o["pull_cell"])
            l = chain_l(alpha_deg=a, pull=o["pull_cell"])
            A(f"  {key + '/' + str(a) + '°':<12}{v['worst']:>12.3f}{v['loss']:>10.3f}"
              f"{l['worst']:>12.3f}{l['loss']:>10.3f}   "
              f"{'✅' if (v['ok'] and l['ok']) else '❌'}")
    A("")
    A("  ★ 名义: 链③ V = 2.00 (量产最坏 1.60); 链④ L = 14.50 (量产最坏 13.90); 判据均 0.40")
    A("  ★ P1 下这两条链各只吃 2·5.70·tanα = 0.0995/0.1990/0.2985 ⇒ 全部 ✅;")
    A("    ⇒ **脱模损失被从「最紧的 H 链」迁移到「最松的 V/L 链」** —— 这是本单的核心杠杆。")
    A("")
    return lines


def build_report() -> dict:
    lines, base_rows = sec_a_and_baseline()
    lines += sec_b_proof()
    lines += sec_faces()
    lines += sec_options()
    lines += sec_board_tiers()[0]
    lines += sec_other_chains()
    lines += sec_face_criteria()
    lines += sec_weight()
    lines.append("=" * 100)
    lines.append("★ 结论 (ISS-127: 从「几何上做不出来」推到「有解」)")
    lines.append("=" * 100)
    lines.append("  ① 口径: 链① 电芯段 (控制链, −0.577 就是它) 与 链② PCB/骨架堆叠 (✅ 2.60/2.90) "
                 "严格分开 —— 不拿 2.60 说 −0.577, 也不拿 −0.577 否 2.60。")
    lines.append("  ② 根因: 拉出方向 V ⇒ 垂直于 V 的 H×L 截面沿 V 变窄 ⇒ **H 链被吃**; "
                 "电芯高 23.50 ⇒ V 向脱模下**任何** α 都过不了 0.40 判据 (Δ ≤ 0.35 要求腔深 ≤10.03)。")
    lines.append("  ③ 解: **拉出方向改 H** (镜腿壳 = 皮肤盖 + 内胆, 分型面 ⊥ H) ⇒ 链① 脱模项 **Δ=0** "
                 "⇒ 三档 α 全部过 0.40 (最坏 0.736/0.722/0.708)。")
    lines.append("  ④ 推荐 **P1**: H 向分型 + 电池座=独立 0.5mm CNC 嵌件 (热隔离, 不与骨架共体) "
                 "+ 石墨裁到 SoC 带 ⇒ 金属+石墨 净减, **重量账内**; 零件 4 件/侧, 模具 2 套/侧。")
    lines.append("  ⑤ 板厚四档: P1/P2 下链② 与 α/板厚**无关**全过 (3.29/2.90/2.70/2.48); "
                 f"现状 P0 在 α=1.5°+含石墨+t=1.22 ⇒ "
                 f"{chain_pcb(1.22, alpha_deg=1.5, pull='V', graphite=GRAPHITE_T)['worst']:.3f} 破线 "
                 "(**本单新发现**)。")
    lines.append("  ⑥ 脱模面尺子: 判据 = E1 倒扣面 0 个 + E3 关键链上直壁面 0 个 + E4 链级 Δ ≤ 预算; "
                 "E2 的 ZERO_DRAFT 占比只作参考 (平行于拉出方向的直壁是合法的)。")
    lines.append("  ⑦ 诚实边界: 本机无法打印/量测 ⇒ 全部 [推算]; 量产公差带/斜度/收缩率**未按牌号锁定** "
                 "(DFM §6 needs_from #1/#3); 未联系任何供应商/原厂/模具厂。")
    return {"text": "\n".join(lines), "base_rows": base_rows}


# =====================================================================
# --self-test: 正向断言 + ★反向用例 (改坏一个参数必须变红)
# =====================================================================
def self_test() -> int:
    fails = []

    def ok(cond, msg):
        if not cond:
            fails.append(msg)
        print(f"  [{'PASS' if cond else 'FAIL'}] {msg}")

    print("=" * 100)
    print("【SELF-TEST】正向断言 + 反向用例 (改坏一个参数必须变红)")
    print("=" * 100)

    # ---- 0) 与既有脚本的口径一致 (不许另起一套数) ----
    r = chain_cell(alpha_deg=1.0, pull="V")
    ok(abs(r["worst"] - (-0.577)) < 0.002,
       f"链① α=1.0° 现状最坏 = {r['worst']:.3f} ≈ −0.577 (DFM_REVIEW §2.1.2)")
    r05 = chain_cell(alpha_deg=0.5, pull="V")
    ok(abs(r05["worst"] - 0.087) < 0.002,
       f"链① α=0.5° 现状最坏 = {r05['worst']:.3f} ≈ 0.087 (DFM_REVIEW §2.1.2)")
    ok(abs(CRIT_PROD - 0.40) < 1e-9, f"量产判据 = {CRIT_PROD:.2f} (=2×0.20, 与 dfm_check §B 同口径)")
    ok(abs(chain_cell()["margin"] - 0.95) < 1e-9, "链① 名义余量 = 0.95 (fit_check_v3_30mm 同源)")
    ok(abs(chain_pcb(1.00)["margin"] - 2.90) < 1e-9,
       "链② t=1.00 名义余量 = 2.90 (fit_check_v3_30mm 同源)")
    ok(abs(chain_pcb(1.22)["margin"] - 2.68) < 1e-9, "链② t=1.22 名义余量 = 2.68")
    ok(abs(chain_pcb(1.22, graphite=GRAPHITE_T)["margin"] - 2.38) < 1e-9,
       "链② t=1.22 含石墨 = 2.38 (BOARD_GEOM §5.4 的 2.60 是 t=1.00 口径)")

    # ---- 1) 正向: 推荐方案在三档 α 下全过 ----
    for a in DRAFT_CASES:
        r = chain_cell(alpha_deg=a, pull="H")
        ok(r["ok"], f"P1 链① α={a:.1f}° 最坏 {r['worst']:.3f} ≥ {r['crit']:.2f}")
    for t in BASE["pcb_thk"]:
        r = chain_pcb(t, pull="H")
        rg = chain_pcb(t, pull="H", graphite=GRAPHITE_T)
        ok(r["ok"] and rg["ok"], f"P1 链② t={t:.2f} 量产最坏 {r['worst']:.3f} / 含石墨 {rg['worst']:.3f} ≥ 0.40")

    # ---- 2) 反向用例 R1: 把方案退回现状 (拉出方向 V) ⇒ 必须变红 ----
    r = chain_cell(alpha_deg=1.0, pull="V")
    ok(not r["ok"], f"R1 退回现状拉出方向 V ⇒ 最坏 {r['worst']:.3f} < 0.40 ⇒ 变红 ✅")

    # ---- 3) 反向用例 R2: 判据/公差被放宽到极限 ⇒ 现状**仍红** ⇒ 证明没有口径能救现状 ----
    r = chain_cell(alpha_deg=1.0, pull="V", t_prod=0.0)
    ok(not r["ok"],
       f"R2 公差/判据被放宽到 0 (t_prod=0 ⇒ 判据 0.00) ⇒ 现状最坏 {r['worst']:.3f} 仍红 "
       "⇒ 证明没有公差口径能救, 只能改结构 ✅")
    r = chain_cell(alpha_deg=1.0, pull="H", extra_loss=0.50)
    ok(not r["ok"],
       f"R2b P1 上人为加 0.50 额外损失 ⇒ 最坏 {r['worst']:.3f} 变红 ⇒ 函数对附加项敏感 ✅")

    # ---- 4) 反向用例 R3: 拉出方向改成 L ⇒ 必须比现状更红 ----
    rL = chain_cell(alpha_deg=1.0, pull="V")
    loss_l = draft_loss(CAV_L_CELL, 1.0)
    ok(loss_l > rL["loss"], f"R3 L 向脱模 Δ={loss_l:.3f} > 现状 Δ={rL['loss']:.3f} ⇒ L 向被否决 ✅")

    # ---- 5) 反向用例 R4: 电芯高度被改小 ⇒ 判据应放行 (证明判据不是硬编码) ----
    #      (电芯高 23.50 是锁死输入; 这里改的是**判据余量**, 验证函数对输入敏感)
    r_big = chain_cell(nominal_need=5.0, alpha_deg=1.0, pull="V")
    ok(r_big["ok"], f"R4 需求被改成 5.00 ⇒ 最坏 {r_big['worst']:.3f} 变绿 ⇒ 函数对输入敏感 ✅")

    # ---- 6) 反向用例 R5: 链② 在 α=1.5° + 含石墨 + t=1.22 ⇒ 现状必须变红 (新发现) ----
    r = chain_pcb(1.22, alpha_deg=1.5, pull="V", graphite=GRAPHITE_T)
    ok(not r["ok"], f"R5 现状链② α=1.5°/含石墨/t=1.22 ⇒ {r['worst']:.3f} < 0.40 ⇒ 变红 ✅")

    # ---- 7) 反向用例 R6: 重量账 —— 电池座质量算错 (×3) ⇒ 重量账必须变红 ----
    w = weight_ledger("P1")
    ok(w["within_budget"], f"R6 P1 重量账 合计 {w['total_g']:.2f} g/对, 增量 {w['delta_g']:+.2f} ⇒ 账内 ✅")
    seat3 = seat_vol(SEAT_T * 3) / 1000.0 * AL_DENSITY * 2
    base_skel = skeleton_cand_c_vol() / 1000.0 * AL_DENSITY * 2
    base_gr = graphite_vol(True) / 1000.0 * GR_DENSITY * 2
    gr_trim = graphite_vol(False) / 1000.0 * GR_DENSITY * 2
    bad = base_skel + gr_trim + seat3
    ok(bad - (base_skel + base_gr) > 0.0,
       f"R6b 电池座壁厚被改成 1.50 (质量 ×3 = {seat3:.2f} g/对) ⇒ 增量 {bad - (base_skel + base_gr):+.2f} ⇒ 变红 ✅")

    # ---- 8) 反向用例 R7: 舱块重量判死 ----
    w3 = weight_ledger("P3")
    ok(not w3["within_budget"], f"R7 金属舱块 P3 增量 {w3['delta_g']:+.2f} g/对 ⇒ 判死 ✅")

    # ---- 9) 脱模面判据自洽: 倒扣面 α<0 必须被判 UNDERCUT ----
    ok(classify(-0.2)[0] == "UNDERCUT", "R8a n_z=−0.2 ⇒ UNDERCUT ✅")
    ok(classify(0.0)[0] == "ZERO_DRAFT", "R8b n_z=0 ⇒ ZERO_DRAFT ✅")
    ok(classify(0.9)[0] == "FLAT_TOP", "R8c n_z=0.9 ⇒ FLAT_TOP ✅")

    # ---- 10) 面级统计脚本能跑通 (至少 STL 路径) ----
    st = revb_face_stats()
    ok(bool(st["parts"]) and all(p["total_area"] > 0 for p in st["parts"]),
       f"R9 脱模面统计可跑 ({st['mode']}, {len(st['parts'])} 件) ✅")

    print("-" * 100)
    if fails:
        print(f"★ SELF-TEST **失败**: {len(fails)} 条")
        for f in fails:
            print(f"    - {f}")
        return 1
    print("★ SELF-TEST **全部通过** (含反向用例: 改坏参数 ⇒ 变红)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    rep = build_report()
    if args.json:
        print(json.dumps({
            "crit_prod": CRIT_PROD,
            "chain_cell_baseline": {str(a): chain_cell(alpha_deg=a, pull="V")
                                    for a in DRAFT_CASES},
            "chain_cell_P1": {str(a): chain_cell(alpha_deg=a, pull="H")
                              for a in DRAFT_CASES},
            "chain_pcb_P1": {str(t): chain_pcb(t, pull="H") for t in BASE["pcb_thk"]},
            "weights": {k: weight_ledger(k) for k in OPTIONS},
        }, ensure_ascii=False, indent=2))
        return 0

    print("=" * 100)
    print("ISS-127 闭环检查 | 电芯段 H 链量产几何 | 拉出方向 = 方案变量 | 判据 = 0.40 (=2×注塑公差)")
    print("=" * 100)
    print("★ 口径: 本脚本是 **设计态几何 + 公差栈 + 通用工程经验值** 的确定性计算")
    print("  ⇒ 全部 [推算]; 本机物理上无法打印/量测 ⇒ **无任何 [实测]**")
    print("  ⇒ 量产公差带/脱模斜度/收缩率 **未按牌号锁定** ⇒ 需模具厂书面确认 (DFM_REVIEW §6 #1/#3)")
    print("  ⇒ 既有算式来源: MECH/fit_check_v3_30mm.py (锁死尺寸链) + MECH/dfm_check.py §B/§C "
          "(公差栈/脱模损失) + MECH/skeleton_section_check.py (重量账)")
    print()
    print(rep["text"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
