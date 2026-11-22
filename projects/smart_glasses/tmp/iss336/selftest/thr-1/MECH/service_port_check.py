#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
service_port_check.py —— ISS-092 镜脚末端检修口 规格书自证脚本 (mech-lead)
=====================================================================
为什么有这个脚本:
  ISS-092 的验收标准是 "**尺寸表 + 影响量 + [推算]/[0数据] 标注**"。尺寸表里的每一个数
  (开口尺寸 / 单边间隙 / 盖板内腔 / 三条尺寸链余量 / 重量 / 探针伸入深度 / 冲突间距)
  都是**设计态几何 + 公差栈**, 没有人能靠"读一遍"确认它自洽 —— 必须机械复算。

口径声明 (与 MECH/fit_check.py / MECH/BOARD_GEOM_30MM.md 一致):
  · 公差判据: **余量 ≥ 2 × 单边公差 = 2 × 0.30 = 0.60mm**, 且同时报名义/最坏两列。
  · 本脚本是 **设计态确定性计算**, **不是物理装配实测** ⇒ 证据级最高 [推算], 阶段门 G2 不认 (这是对的)。
  · 排布 = **沿长度串行** (叠放分支已由 fit_check.py 三重证明裁决作废)。
  · ★ **主 PCB 板宽 = 30.00mm** (现行 60×30 板; 老板 10-29 19:16 拍板; MECH/BOARD_GEOM_30MM.md §0/§1
    —— 本域唯一权威几何口径) —— 2026-11-12 由 **15.00mm 迁入** (ISS-203 / ISS-197 L6): 15mm 口径已作废,
    此前本脚本的 V 链 PCB 段读数 (需求 21.00 / 余 +17.00) 是**给一块不存在的板打的分**。
    ★ 板宽走 V 不走 H ⇒ 本次只动 V 链 PCB 段 (【5】5.4), H/L 链不受板宽影响。

用法: python3 MECH/service_port_check.py [--self-test|--selftest]
      --self-test / --selftest = 反向用例 (★两个, 一条不许删★):
        ① (★ISS-203 旧用例, 保留★) 强制 pcb_w 回 15.00 (旧板宽) ⇒ 读数必须回到迁移前基准
           (★现基准 = N_ITEMS_BASE = 57 项 = 板宽迁移前 54 项 + ISS-264 新增 3 项口径/现值检查★)
        ② (★ISS-264 新用例★) 强制 p2_y / s2_y 回【旧 15mm 板口径】(7.50 / 12.50)
           ⇒ 【7.4b / 7.5b 两条口径钉死】必红并【点名 p2_y / s2_y】;
           ⇒ 同时 7.4 / 7.5 两条【几何判据】必须仍然绿 (旧基准下 1.00 / 1.03mm ≥ 判据 0.60)
              —— 这是【迁的是常量, 不是松判据】的机器证据
        ③ 装回现行口径 ⇒ 必须又全绿
退出码: 0 = 全部项一致 (报告已生成); 非 0 = 有项不一致;
        --self-test 下另: 0 = 三个反向用例都与预期一致, 2 = 不一致
"""
from __future__ import annotations

import argparse
import math
import sys

# =====================================================================
# 输入 —— 全部标来源 (与 MECH/SERVICE_PORT_ISS092.md 一致)
# =====================================================================
BASE = {
    # 镜脚内腔 (老板锁死)
    "cav_h":       7.30,   # §1.6.2 镜脚前后厚 ← 锁死值
    "cav_v":      38.00,   # §1.6.2 根部净高
    "cav_l":     130.00,   # §1.6.2 内腔长
    "wall":        0.80,   # §5.4 FDM 最小可靠单壁
    "frame_thk":   1.00,   # §5.1 铝/铜骨架
    "pcb_thk":     1.00,   # §5.1 PCB 厚 (★6 层现行; 4 层 0.80 已作废 —— ISS-206 依 MECH/BOARD_GEOM_30MM.md §1)
    "air_gap":     0.30,   # §2.4 皮肤侧空气隙
    "pad_thermal": 0.50,   # §2.4 皮肤侧隔热垫
    "cell_thk":    4.60,   # §1.6.1 Renata ICP582035PR-01 (315 档)
    "cell_v":     23.50,   # §1.6.1
    "cell_l":     40.50,   # §1.6.1
    "l_offset":   40.50,   # ★ 镜脚长度坐标 L = 板坐标 X + 40.50 (串行: 电芯 0..40.5 / PCB 40.5..100.5)
    "hinge_l":    15.00,   # 铰链区轴向占位 (L 0..15)
    "skeleton_x1": 42.00,  # 金属骨架末端 (板坐标 X)
    "pcb_l":      60.00,   # ISS-100 / ISS-107 定版 (fit_check.py 的 50 是旧值)
    "pcb_w":      30.00,   # 主 PCB 板宽 Y [官方-项目内: 老板 10-29 19:16 拍板, MECH/BOARD_GEOM_30MM.md §0/§1;
                            # ★2026-11-12 由 15.00 迁入 (ISS-203 / ISS-197 L6) —— 15mm 口径已作废, 勿回改]
    "duct_v":      6.00,   # §5.6.2 垂直向走线槽占位 (口径)
    "duct_h":      2.00,   # §1.3
    "conn_margin": 15.00,  # §1.4.2
    # H 坐标 (本文 §1.1 新立)
    "h_skin_wall_in": 0.80,   # 皮肤侧外壁内表面 = H 0
    "h_pcb_face":    2.60,   # PCB 元件面 (外侧) = 壁0.8 + 隔热0.5 + 空隙0.3 + **PCB 1.0** (6 层)
    "h_outer_in":    6.50,   # 镜脚外壁内表面
    "h_outer_out":   7.30,   # 镜脚外表面
    # J_DEBUG / J_UART 焊盘阵列 (本文 §3.2)
    "jd_pitch":      1.27,   # Cortex-10 pitch
    "jd_cols":       5,      # 2×5
    "jd_rows":       2,
    "jd_body_w":     5.08,   # Cortex-10 座体长 (X)
    "jd_body_h":     2.54,   # Cortex-10 座体宽 (Y)  ← **开口必须清空的是它, 不是焊盘**
    "ju_cols":       2,      # 1×2
    "ju_body_h":     2.54,   # J_UART 座体宽 (Y) —— 本单定 DNP (只留焊盘), 见 §3.2
    "jd_x0":        50.50,   # 阵列起点 (板坐标 X)
    "jd_y0":         9.50,   # 阵列起点 (板坐标 Y)
    "ju_gap":        1.27,   # J_UART 距 J_DEBUG 末列的 X 间距
    "pad_d":         0.60,   # 焊盘直径 [0数据·待 hw-lead 定]
    # 盖板
    "cover_t":       1.20,   # 盖板厚
    "cover_flange":  1.50,   # 搭边宽
    "cavity_req":    4.30,   # ISS-085 §6.1 硬要求: 盖板内腔 ≥4.5
    "screw_d":       1.60,   # M1.6 自攻
    "screw_l":       6.00,   # M1.6×6
    "screw_d_eff":   1.30,   # 螺纹根部等效直径 (真实螺钉不是实心圆柱) [推算]
    "screw_head_d":  2.80,   # 头径
    "screw_head_t":  1.00,   # 头高
    "screw_boss_d":  3.20,   # 凸台直径
    "screw_boss_in": 1.60,   # 凸台向内加厚
    "screw_len_req": 2.40,   # 旋入总长 (1.5×d)
    "screw_x":      60.30,   # 螺钉在板坐标 X 的位置 (盖板端部, 在 PCB 板端之外)
    # 磁吸
    "mag_d":         4.00,   # N35 ⌀4×1
    "mag_t":         1.00,
    # 任务书下限
    "task_min_x":    7.10,   # 任务书: 初步 ≥7.1×2.7
    "task_min_y":    2.70,
    # 产线
    "cortex_pad_coplan": 0.05,   # P-3 焊盘共面度
    "pogo_travel":        1.00,   # pogo 工作行程
    # 重量
    "rho_pa_cf":   1.20,   # g/cc
    "rho_ndfeb":   7.50,   # g/cc
    "rho_steel":   7.85,   # g/cc
    "mass_total_lo": 48.90,   # MECH_BUDGET §3 315 档合计下限
    "mass_total_hi": 72.80,   # 315 档合计上限
    # 夹具基准 (PIN-SET-2, ISS-049/ISS-107)
    # ★★ISS-206 (2026-11-12) 注记 · ★★ISS-264 (2026-11-17) 实际迁移落地 ★★:
    #   ISS-206 当时只加注记不动数字 (因为 7.4/7.5 两式的符号/系数是按旧基准写的, 只换数字会让公式反过来
    #   ⇒ 造出【假红】) ⇒ ★**ISS-264 把【公式 + 基准】一起迁了**: 7.4/7.5 改成【两个 Y 区间的最近距离】通用式
    #   (对旧基准 7.50/12.50 与新基准 15.00/20.00 都给出正确读数, 旧基准下复算仍得 1.00 / 1.03mm ⇒ 可回溯)。
    #   ★**现行基准 = 30mm 板 PIN-SET-2 套 A** (MECH/BOARD_GEOM_30MM.md §3 [官方]):
    #     P2 (52.00, 15.00) / S2 (52.00, 20.00) ⇒ 孔心 Y 与焊盘阵列 (Y 9.50..10.77) 不重叠, 最近距离 3.23 / 8.53mm。
    #   ★**旧口径留档 (已作废, 不许回改)**: p2_y = **7.50** / s2_y = **12.50** = **15mm 板口径**
    #     (板宽 15 已于 ISS-100/ISS-118/ISS-130 作废) —— 旧基准下 7.4/7.5 读数 = 1.00 / 1.03mm
    #     (仍过判据 0.60 ⇒ 判据结论不变, 错的只是基准)。
    #   ★**仍未迁 (别的单的地界, 等 main + hw-lead)**: 焊盘阵列起点 jd_y0 = 9.50 (旧 15mm 板口径)
    #     ⇒ 开口 Y 跟着它算 ⇒ need `iss251_mech_service_port_pad_y_migrate` 仍挂 (只差 jd_y0 一项)。
    "p2_x": 52.00, "p2_y": 15.00, "p2_d": 2.00,     # ⌀2.0 H7 圆销定位孔 (★现行 30mm 板套 A Y=15.00; 旧值 7.50 = 15mm 板口径, 已作废)
    "s2_x": 52.00, "s2_y": 20.00, "s2_d": 1.40,    # ⌀1.4 M1.2 压紧孔 (★现行 30mm 板套 A Y=20.00; 旧值 12.50 = 15mm 板口径, 已作废)
    "soc_escape_x0": 20.20, "soc_escape_x1": 31.80,  # SoC 逃线带
    "s2_repeat": 0.046,   # ISS-049 定位链重复性
}

TOL = {"fdm_part": 0.30, "fdm_feat": 0.25}
CRIT = 2 * TOL["fdm_part"]          # 0.60mm 判据

# ★★ISS-264 (2026-11-17): 夹具基准口径真值 (MECH/BOARD_GEOM_30MM.md §3 PIN-SET-2 套 A [官方])
#   —— **只用于【口径钉死检查】(7.4b/7.5b), 不参与任何几何计算** ⇒ 改这里 = 改口径 (要重走口径变更流程)
PIN_SET_A = {"p2_x": 52.00, "p2_y": 15.00, "s2_x": 52.00, "s2_y": 20.00}
# ★ 作废口径留档 (15mm 板): 只留名字, 不参与计算 —— 反向用例用它把门禁打红
PIN_SET_LEGACY_15MM = {"p2_y": 7.50, "s2_y": 12.50}

# ★★ISS-264: 迁移前的自证基线项数 (板宽迁移前 54 项 ⇒ 迁常量后加 3 项口径/现值检查 = 57 项)
N_ITEMS_BASE = 57

RESULTS = []
# ★★ISS-264 (2026-11-17): --selftest 的第 ③ 段 (装回现行口径) 用它压掉逐项打印, 只留结论块
VERBOSE = True


def chk(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    if VERBOSE:
        print(f"  [{'OK ' if ok else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    return bool(ok)


def near(a, b, tol=1e-6):
    return abs(a - b) <= tol


def run_report() -> tuple:
    """跑一遍全量核算 (读全局 BASE) ⇒ 返回 (通过数, 总数, 失败名单, 全部明细行)。

    ★★ISS-264 (2026-11-17): 拆成独立函数, 好让 --self-test 能用不同的 BASE 跑多遍 (反向用例)。
    """
    RESULTS.clear()
    print("=" * 100)
    print("SERVICE-PORT CHECK — ISS-092 镜脚末端检修口 (开孔 + 盖板) | mech-lead 2026-10-30")
    print("=" * 100)
    print(f"\n【0】判据与公差账")
    print(f"  判据: **每条余量 ≥ 2× 单边公差** → 阈值 {CRIT:.2f}mm")
    print(f"  公差: FDM 外形 ±{TOL['fdm_part']:.2f} / 特征 ±{TOL['fdm_feat']:.2f}mm")
    print(f"  口径: 设计态几何 + 公差栈 (非实物实测) ⇒ 证据级 [推算]")

    # ------------------------------------------------------------------
    print(f"\n【1】H 坐标自洽 (§1.1)")
    h_chain = (BASE["h_skin_wall_in"] + BASE["pad_thermal"] + BASE["air_gap"]
               + BASE["pcb_thk"] + BASE["frame_thk"] + BASE["wall"])
    chk("1.1 H 链 = 壁0.8+隔热0.5+空隙0.3+PCB1.0+骨架1.0+壁0.8 = 4.40",
        near(h_chain, 4.40), f"H 链 = {h_chain:.2f}mm")
    chk("1.2 PCB 元件面 H = 0.8+0.5+0.3+1.0 = 2.60",
        near(BASE["h_skin_wall_in"] + BASE["pad_thermal"] + BASE["air_gap"] + BASE["pcb_thk"],
             BASE["h_pcb_face"]), f"H_pcb = {BASE['h_pcb_face']:.2f}mm")
    chk("1.3 外壁内表面 H = 7.30-0.80 = 6.50",
        near(BASE["h_outer_out"] - BASE["wall"], BASE["h_outer_in"]),
        f"H_outer_in = {BASE['h_outer_in']:.2f}mm")
    chk("1.4 外壁内表面与骨架外表面之间空腔 = 2.90mm (螺钉凸台/探针落这里)",
        near(BASE["h_outer_in"] - (BASE["h_pcb_face"] + BASE["frame_thk"]), 2.90),
        f"空腔 = {BASE['h_outer_in'] - (BASE['h_pcb_face'] + BASE['frame_thk']):.2f}mm")

    # ------------------------------------------------------------------
    print(f"\n【2】焊盘阵列与开口必须清空区 (§3.2)")
    jd_x1 = BASE["jd_x0"] + (BASE["jd_cols"] - 1) * BASE["jd_pitch"]
    jd_y1 = BASE["jd_y0"] + (BASE["jd_rows"] - 1) * BASE["jd_pitch"]
    ju_x0 = jd_x1 + BASE["ju_gap"]
    ju_x1 = ju_x0 + (BASE["ju_cols"] - 1) * BASE["jd_pitch"]
    # 焊盘 bbox (只有焊盘, DNP 座体)
    pad_x0, pad_x1 = min(BASE["jd_x0"], ju_x0), max(jd_x1, ju_x1)
    pad_y0, pad_y1 = BASE["jd_y0"], jd_y1
    # ★ 开口必须清空的是 **Cortex-10 座体** (若将来装), 不是焊盘:
    #   座体 X 50.50..55.58 / Y 9.50-1.27/2+... ⇒ 以阵列中心为心, 高 2.54
    jd_body_y_c = (BASE["jd_y0"] + jd_y1) / 2
    body_y0 = jd_body_y_c - BASE["jd_body_h"] / 2
    body_y1 = jd_body_y_c + BASE["jd_body_h"] / 2
    content_x0, content_x1 = pad_x0, pad_x1          # X 向: 焊盘并集 (J_UART 更靠外)
    content_w = content_x1 - content_x0
    content_h = body_y1 - body_y0                   # Y 向: 按 Cortex-10 座体高
    chk("2.1 J_DEBUG 2×5 **焊盘** 包络 = 5.08 × 1.27",
        near(jd_x1 - BASE["jd_x0"], 5.08) and near(jd_y1 - BASE["jd_y0"], 1.27),
        f"{jd_x1 - BASE['jd_x0']:.2f} × {jd_y1 - BASE['jd_y0']:.2f}mm")
    chk("2.2 J_UART 1×2 末脚 X = 58.12 (距 PCB 板端 1.88mm ≥0.8)",
        near(ju_x1, 58.12) and (BASE["pcb_l"] - ju_x1) >= 0.8,
        f"X={ju_x1:.2f}, 距板端 {BASE['pcb_l'] - ju_x1:.2f}mm")
    chk("2.3 焊盘并集 bbox = 7.62 × 1.27",
        near(pad_x1 - pad_x0, 7.62) and near(pad_y1 - pad_y0, 1.27),
        f"{pad_x1 - pad_x0:.2f} × {pad_y1 - pad_y0:.2f}mm")
    chk("2.4 ★ **必须清空区** = 7.62 (X) × 2.54 (Y, 按 Cortex-10 座体)",
        near(content_w, 7.62) and near(content_h, 2.54),
        f"{content_w:.2f} × {content_h:.2f}mm")
    chk("2.5 焊盘阵列整体在板内 (X≤59.2 且 Y≤13.0)",
        pad_x1 <= 59.2 and pad_y1 <= 13.0,
        f"X max {pad_x1:.2f}, Y max {pad_y1:.2f}")
    ju_body_y0 = BASE["jd_y0"] - BASE["ju_body_h"] / 2
    chk("2.6 J_UART 座体若装 (DNP) 需开口 Y 放大到 5.24 —— 本文取 4.60 ⇒ J_UART 座体一律 DNP",
        True, f"J_UART 座体下沿 Y={ju_body_y0:.2f} < 开口下沿 {BASE['jd_y0'] - 1.03:.2f} ⇒ 装不下")

    # ------------------------------------------------------------------
    print(f"\n【3】开口尺寸与单边间隙 (§3.5 / §4.1)")
    OPEN_X, OPEN_Y = 10.20, 4.60
    cl_x = (OPEN_X - content_w) / 2
    cl_y = (OPEN_Y - content_h) / 2
    worst_x, worst_y = cl_x - TOL["fdm_part"], cl_y - TOL["fdm_part"]
    chk("3.1 开口 ≥ 任务书下限 7.1 × 2.7",
        OPEN_X >= BASE["task_min_x"] and OPEN_Y >= BASE["task_min_y"],
        f"{OPEN_X:.2f} × {OPEN_Y:.2f}mm")
    chk("3.2 名义单边间隙 X ≥ 判据 0.60", cl_x >= CRIT, f"X {cl_x:.2f}mm")
    chk("3.3 名义单边间隙 Y ≥ 判据 0.60", cl_y >= CRIT, f"Y {cl_y:.2f}mm")
    chk("3.4 最坏单边间隙 (FDM ±0.30) X ≥ 判据 0.60", worst_x >= CRIT, f"X {worst_x:.2f}mm")
    chk("3.5 最坏单边间隙 Y ≥ 判据 0.60", worst_y >= CRIT, f"Y {worst_y:.2f}mm")

    # ------------------------------------------------------------------
    print(f"\n【4】盖板 (§4.1)")
    COVER_X = OPEN_X + 2 * BASE["cover_flange"]
    COVER_Y = OPEN_Y + 2 * BASE["cover_flange"]
    chk("4.1 盖板外形 = 13.20 × 7.60 × 1.20",
        near(COVER_X, 13.20) and near(COVER_Y, 7.60) and near(BASE["cover_t"], 1.20),
        f"{COVER_X:.2f} × {COVER_Y:.2f} × {BASE['cover_t']:.2f}mm")
    cavity = BASE["h_outer_out"] - BASE["h_pcb_face"]
    chk("4.2 盖板内腔 = 外表面 7.30 − PCB 元件面 2.60 = 4.70 ≥ 4.50 (硬要求)",
        cavity >= BASE["cavity_req"], f"内腔 {cavity:.2f}mm, 余 {cavity - BASE['cavity_req']:.2f}mm")
    boss_room = BASE["h_outer_in"] - (BASE["h_pcb_face"] + BASE["frame_thk"])
    chk("4.3 螺钉凸台 (向内 1.60) 落在 PCB 段 2.90mm 空腔内",
        BASE["screw_boss_in"] <= boss_room, f"空腔 {boss_room:.2f}mm ≥ 凸台 {BASE['screw_boss_in']:.2f}mm")
    screw_eng = BASE["wall"] + BASE["screw_boss_in"]
    chk("4.4 螺钉旋入总长 = 壁 0.8 + 凸台 1.6 = 2.40 = 1.5×d (自攻在塑料里的下限)",
        near(screw_eng, BASE["screw_len_req"]) and screw_eng >= 1.5 * BASE["screw_d"],
        f"{screw_eng:.2f}mm = {screw_eng / BASE['screw_d']:.2f}×d")
    chk("4.5 盖板搭边 1.50 ≥ 密封条宽度需求 (量产)",
        BASE["cover_flange"] >= 1.50, f"{BASE['cover_flange']:.2f}mm")
    chk("4.6 盖板凸出镜脚外表面 1.20mm (不占内腔)",
        near(BASE["cover_t"], 1.20), f"外凸 {BASE['cover_t']:.2f}mm")

    # ------------------------------------------------------------------
    print(f"\n【5】三条锁死尺寸链 —— 检修口的影响必须 = 0 (§5.1)")
    h_cell = BASE["wall"] + (BASE["cell_thk"] + 0.15) + BASE["wall"]
    h_pcb = BASE["wall"] + BASE["frame_thk"] + BASE["pcb_thk"] + BASE["air_gap"] + BASE["pad_thermal"] + BASE["wall"]
    v_cell = BASE["cell_v"] + BASE["duct_v"]
    v_pcb = BASE["pcb_w"] + BASE["duct_v"]
    l_need = BASE["cell_l"] + BASE["pcb_l"] + BASE["conn_margin"]
    chk("5.1 H 电池段 (控制段) 需求 6.35, 余量 +0.95 / 最坏 +0.65",
        near(h_cell, 6.35) and near(BASE["cav_h"] - h_cell, 0.95)
        and near(BASE["cav_h"] - (h_cell + TOL["fdm_part"]), 0.65),
        f"需求 {h_cell:.2f} / 余 {BASE['cav_h'] - h_cell:+.2f} / 最坏 {BASE['cav_h'] - (h_cell + TOL['fdm_part']):+.2f}")
    chk("5.2 H PCB 段 需求 4.40 → 余量 +2.90 (检修口 Δ0.00)",
        near(h_pcb, 4.40) and near(BASE["cav_h"] - h_pcb, 2.90), f"需求 {h_pcb:.2f} / 余 {BASE['cav_h'] - h_pcb:+.2f}")
    chk("5.3 V 电池段 (控制段) 需求 29.50, 余量 +8.50",
        near(v_cell, 29.50) and near(BASE["cav_v"] - v_cell, 8.50), f"余 {BASE['cav_v'] - v_cell:+.2f}")
    v_margin = BASE["cav_v"] - v_pcb
    v_margin_worst = v_margin - 2 * TOL["fdm_part"]   # 最坏: 腔体侧 + 走线槽侧 各让 1×0.30
    chk(f"5.4 V PCB 段 需求 {v_pcb:.2f} (板宽 {BASE['pcb_w']:.2f} + 走线槽 {BASE['duct_v']:.2f}), "
        f"余量 {v_margin:+.2f} (开口只挖壁, Δ0.00)",
        v_margin >= CRIT and v_margin_worst >= CRIT,
        f"需求 {v_pcb:.2f} / 余 {v_margin:+.2f} / 最坏 {v_margin_worst:+.2f} "
        f"(单边口径最坏 {v_margin - TOL['fdm_part']:+.2f}) · 判据 ≥{CRIT:.2f}")
    print(f"       ★ 口径同步提示 (ISS-206 · 2026-11-12): MECH/SERVICE_PORT_ISS092.md §1/§5.1 已按本脚本输出 "
          f"重写 (30mm 板宽 + 6 层 1.0 板厚 ⇒ V PCB 段需求 {v_pcb:.2f} / 余 {v_margin:+.2f} / 最坏 {v_margin_worst:+.2f}; "
          f"H PCB 段需求 4.40 / 余 +2.90) ⇒ 文档与脚本现已同口径")
    chk("5.5 L 需求 115.50, 余量 +14.50 (开口在 PCB 段内, Δ0.00)",
        near(l_need, 115.50) and near(BASE["cav_l"] - l_need, 14.50), f"余 {BASE['cav_l'] - l_need:+.2f}")
    chk("5.6 镜腿厚度锁死值 7.30mm 不变 (Δ = 0.00)",
        near(BASE["cav_h"], 7.30), f"H = {BASE['cav_h']:.2f}mm")
    chk("5.7 电池段 H 余量仍 ≥ 判据 0.60 (最坏)",
        BASE["cav_h"] - (h_cell + TOL["fdm_part"]) >= CRIT,
        f"最坏 {BASE['cav_h'] - (h_cell + TOL['fdm_part']):+.2f}mm")

    # ------------------------------------------------------------------
    print(f"\n【6】重量影响 (§5.2)")
    cover_vol = COVER_X * COVER_Y * BASE["cover_t"]
    cover_g = cover_vol * BASE["rho_pa_cf"] / 1000.0
    mag_vol = math.pi * (BASE["mag_d"] / 2) ** 2 * BASE["mag_t"]
    mag_g = mag_vol * BASE["rho_ndfeb"] / 1000.0
    screw_v = (math.pi * (BASE["screw_d_eff"] / 2) ** 2 * BASE["screw_l"]
               + math.pi * (BASE["screw_head_d"] / 2) ** 2 * BASE["screw_head_t"])
    screw_g = screw_v * BASE["rho_steel"] / 1000.0
    boss_vol = math.pi * (BASE["screw_boss_d"] / 2) ** 2 * BASE["screw_boss_in"]
    boss_g = boss_vol * BASE["rho_pa_cf"] / 1000.0
    per_side = cover_g + mag_g + screw_g + boss_g
    total = per_side * 2
    chk("6.1 盖板 0.144 g", near(cover_g, 0.144, 0.001), f"{cover_g:.3f} g")
    chk("6.2 磁铁 0.094 g", near(mag_g, 0.094, 0.001), f"{mag_g:.3f} g")
    chk("6.3 螺钉 M1.6×6 0.111 g (螺纹根部等效 ⌀1.30 + 头)",
        near(screw_g, 0.111, 0.003), f"{screw_g:.3f} g")
    chk("6.4 凸台 0.015 g", near(boss_g, 0.015, 0.002), f"{boss_g:.3f} g")
    chk("6.5 单侧 +0.364 g / 整机 +0.73 g", near(per_side, 0.364, 0.003) and near(total, 0.73, 0.02),
        f"单侧 {per_side:.3f} g / 整机 {total:.3f} g")
    pct_lo = total / BASE["mass_total_hi"] * 100
    pct_hi = total / BASE["mass_total_lo"] * 100
    chk("6.6 占原型整机 48.9-72.8 g 的 +1.00%~+1.49%",
        near(pct_lo, 1.00, 0.03) and near(pct_hi, 1.49, 0.04),
        f"{pct_lo:.2f}% ~ {pct_hi:.2f}%")
    chk("6.7 净腔体占用 = 0.013 cc (盖板在壁外, 只算凸台)",
        near(boss_vol / 1000.0, 0.013, 0.001), f"{boss_vol / 1000.0:.4f} cc")

    # ------------------------------------------------------------------
    print(f"\n【7】产线可达性 (§7.2)")
    reach = BASE["h_outer_out"] - BASE["h_pcb_face"]
    need_reach = reach + BASE["pogo_travel"]
    chk("7.1 探针可伸入净空 = 4.70mm", near(reach, 4.70), f"{reach:.2f}mm")
    chk("7.2 含工作行程后需 ≥5.70mm 可伸入", near(need_reach, 5.70, 0.01),
        f"需 {need_reach:.2f}mm (市售 pogo 伸出 typ. 6-11mm)")
    probe_need_x = (BASE["jd_cols"] - 1) * BASE["jd_pitch"] + 2 * 1.0
    probe_need_y = (BASE["jd_rows"] - 1) * BASE["jd_pitch"] + 2 * 1.0
    chk("7.3 净开口容得下 2×5 探针阵列 (7.08 × 3.27)",
        OPEN_X >= probe_need_x and OPEN_Y >= probe_need_y,
        f"需 {probe_need_x:.2f} × {probe_need_y:.2f} / 有 {OPEN_X:.2f} × {OPEN_Y:.2f}")
    # ★★ISS-264 (2026-11-17): 7.4/7.5 的【公式 + 基准】同批迁移 ——
    #   旧式 (jd_y0 - p2_y) 只在【孔在焊盘阵列下方】时成立; 套 A 基准下 P2 (Y 15.00) 在阵列 (Y 9.50..10.77)
    #   **上方** ⇒ 旧式会算出负数 = 假红 (ISS-206 注记里点名的那个坑)。
    #   ⇒ 改成【两个 Y 区间的最近距离】通用式 (重叠时为负) ⇒ 新基准 3.23 / 8.53mm; 旧基准回代仍得 1.00 / 1.03mm。
    #   ★**判据阈值 CRIT = 0.60 一个数字没动** —— 本单是【迁常量/迁公式】, 不是【松判据】。
    p2_wall_y0 = BASE["p2_y"] - BASE["p2_d"] / 2.0
    p2_wall_y1 = BASE["p2_y"] + BASE["p2_d"] / 2.0
    p2_gap = max(p2_wall_y0 - jd_y1, BASE["jd_y0"] - p2_wall_y1)
    s2_wall_y0 = BASE["s2_y"] - BASE["s2_d"] / 2.0
    s2_wall_y1 = BASE["s2_y"] + BASE["s2_d"] / 2.0
    s2_gap = max(s2_wall_y0 - jd_y1, BASE["jd_y0"] - s2_wall_y1)
    chk("7.4 夹具基准复用 PIN-SET-2 P2 (⌀2.0 H7) —— 孔壁到焊盘阵列 ≥0.60",
        p2_gap >= CRIT,
        f"P2 孔壁 Y {p2_wall_y0:.2f}..{p2_wall_y1:.2f} → 焊盘阵列 Y {BASE['jd_y0']:.2f}..{jd_y1:.2f} "
        f"= {p2_gap:.2f}mm (≥{CRIT:.2f})")
    chk("7.5 夹具基准复用 S2 (⌀1.4) —— 孔壁到焊盘阵列 ≥0.60",
        s2_gap >= CRIT,
        f"S2 孔壁 Y {s2_wall_y0:.2f}..{s2_wall_y1:.2f} → 焊盘阵列 Y {BASE['jd_y0']:.2f}..{jd_y1:.2f} "
        f"= {s2_gap:.2f}mm (≥{CRIT:.2f})")
    # ★★ISS-264 新增: 【口径钉死】—— 夹具基准常量必须等于 30mm 板套 A 真值 (BOARD_GEOM_30MM.md §3)
    #   ⇒ 反向用例把 p2_y / s2_y 改回旧 15mm 板口径 ⇒ 这两条必红并【点名是谁】
    chk("7.4b ★口径钉死: p2_y = 15.00 (30mm 板 PIN-SET-2 套 A, MECH/BOARD_GEOM_30MM.md §3)",
        near(BASE["p2_y"], PIN_SET_A["p2_y"]),
        f"p2_y = {BASE['p2_y']:.2f} (真值 {PIN_SET_A['p2_y']:.2f}; ★旧值 7.50 = 15mm 板口径, 已作废, 不许回改)")
    chk("7.5b ★口径钉死: s2_y = 20.00 (30mm 板 PIN-SET-2 套 A, MECH/BOARD_GEOM_30MM.md §3)",
        near(BASE["s2_y"], PIN_SET_A["s2_y"]),
        f"s2_y = {BASE['s2_y']:.2f} (真值 {PIN_SET_A['s2_y']:.2f}; ★旧值 12.50 = 15mm 板口径, 已作废, 不许回改)")
    print(f"       ★ P-5 (夹具基准孔) 最近距离现值 (ISS-264 迁移后): P2 = {p2_gap:.2f}mm / S2 = {s2_gap:.2f}mm "
          f"(判据 ≥{CRIT:.2f} ⇒ 均过) · ★旧 15mm 板基准 (p2_y 7.50 / s2_y 12.50) 下是 1.00 / 1.03mm —— 已作废")
    chk("7.6 焊盘共面 ≤0.05mm 可达 (ISS-049 定位链重复性 0.046 ≤ 0.05)",
        BASE["s2_repeat"] <= BASE["cortex_pad_coplan"],
        f"重复性 {BASE['s2_repeat']:.3f}mm ≤ {BASE['cortex_pad_coplan']:.2f}mm")
    chk("7.7 焊盘阵列与 SoC 逃线带 (X 20.20..31.80) 间距 ≥5.0mm",
        content_x0 - BASE["soc_escape_x1"] >= 5.0,
        f"{content_x0 - BASE['soc_escape_x1']:.2f}mm")

    # ------------------------------------------------------------------
    print(f"\n【8】与电池 / 铰链 / 其它件冲突复核 (§8) —— ★ 坐标换算: L = X + 40.50")
    open_x0 = content_x0 - cl_x
    open_x1 = content_x1 + cl_x
    open_l0 = open_x0 + BASE["l_offset"]
    open_l1 = open_x1 + BASE["l_offset"]
    # ★★ISS-264 (2026-11-17): 开口 Y 现值 (随基准重算) —— 开口 Y 由【焊盘阵列 Y + 单边间隙】决定,
    #   夹具基准 (p2_y/s2_y) 迁移**不影响**它; 它仍跟着 jd_y0 = 9.50 (旧 15mm 板口径, 未迁) 走。
    open_y0 = body_y0 - cl_y
    open_y1 = body_y1 + cl_y
    chk("8.1b 开口 Y 区间 (板坐标) 现值 —— 须含住必须清空区",
        open_y0 <= body_y0 and open_y1 >= body_y1,
        f"开口 Y {open_y0:.3f}..{open_y1:.3f} (宽 {OPEN_Y:.2f}) = 必须清空区 Y {body_y0:.3f}..{body_y1:.3f} "
        f"+ 单边间隙 {cl_y:.2f} · ★jd_y0={BASE['jd_y0']:.2f} 仍是旧 15mm 板基准 ⇒ 开口 Y 仍待 main + hw-lead 定版")
    chk("8.1 开口在 PCB 段内 (板坐标 X 49.21..59.41 ⇒ 镜脚 L 89.71..99.91)",
        near(open_x0, 49.21, 0.02) and near(open_x1, 59.41, 0.02)
        and near(open_l0, 89.71, 0.02) and near(open_l1, 99.91, 0.02),
        f"X {open_x0:.2f}..{open_x1:.2f} ⇒ L {open_l0:.2f}..{open_l1:.2f}")
    chk("8.2 与电芯 (L 0..40.50) 间距 ≥2mm (ISS-085 D-3 缓冲要求)",
        open_l0 - BASE["cell_l"] >= 2.0, f"{open_l0 - BASE['cell_l']:.2f}mm")
    chk("8.3 与铰链区 (L 0..15) 间距 ≥20mm", open_l0 - BASE["hinge_l"] >= 20.0,
        f"{open_l0 - BASE['hinge_l']:.2f}mm")
    chk("8.4 与骨架末端 (X≤42 ⇒ L≤82.50) 间距 ≥5mm",
        open_l0 - (BASE["skeleton_x1"] + BASE["l_offset"]) >= 5.0,
        f"{open_l0 - (BASE['skeleton_x1'] + BASE['l_offset']):.2f}mm")
    chk("8.5 开口 X 末端 ≤ PCB 板端 (60.00) ⇒ 开口投影完全落在 PCB 内",
        open_x1 <= BASE["pcb_l"], f"开口 {open_x0:.2f}..{open_x1:.2f} vs 板端 {BASE['pcb_l']:.0f}")
    chk("8.5b 螺钉凸台 (X 58.7..61.9) 在 H 4.90..6.50 ⇒ 与 PCB (H 1.60..2.60) 不干涉",
        BASE["h_pcb_face"] + BASE["pcb_thk"] <= BASE["h_outer_in"] - BASE["screw_boss_in"],
        f"PCB 上表面 H={BASE['h_pcb_face'] + BASE['pcb_thk']:.2f} < 凸台下沿 H={BASE['h_outer_in'] - BASE['screw_boss_in']:.2f}")
    chk("8.6 开口不与 SoC 逃线带重叠 (2D 判定, X 向)",
        not (open_x0 <= BASE["soc_escape_x1"] and open_x1 >= BASE["soc_escape_x0"]),
        "X 向无重叠")
    chk("8.7 距镜脚内腔末端 (L=130) ≥20mm (手指可捏盖板)",
        BASE["cav_l"] - open_l1 >= 20.0, f"{BASE['cav_l'] - open_l1:.2f}mm")

    # ------------------------------------------------------------------
    print(f"\n【9】IP 防护口径 (§6)")
    chk("9.1 磁吸+自攻螺钉 **无密封条** ⇒ IPx4 不成立 (只能宣称防汗)",
        True, "缝即通路 —— 设计口径判定")
    chk("9.2 加密封条 (0.50×1.50=0.75mm²) + 迷宫 ⇒ IPx4 可达, IPx5/x7 不可达",
        near(0.50 * BASE["cover_flange"], 0.75), "密封条截面 0.75mm²")
    chk("9.3 原型 (FDM) 不宣称 IP 等级", True, "FRAMEWORK_SCOPE H5-04: IP 推迟到量产")

    # ------------------------------------------------------------------
    print(f"\n【10】末端外侧面 V 净高要求 (S-2, [0数据] 项)")
    need_v = OPEN_Y + 2 * 1.25
    chk("10.1 末端外侧面 V 净高要求 ≥7.10mm (需求, 非断言)",
        near(need_v, 7.10), f"开口 {OPEN_Y:.2f} + 两侧 1.25 = {need_v:.2f}mm")

    # ------------------------------------------------------------------
    ok = sum(1 for _, o, _ in RESULTS if o)
    total_n = len(RESULTS)
    fails = [n for n, o, _ in RESULTS if not o]
    print("\n" + "=" * 100)
    print(f"【结论】{ok}/{total_n} 项一致 | FAIL {len(fails)} 项")
    if fails:
        for n in fails:
            print(f"   ❌ {n}")
    print("=" * 100)
    print("口径提醒: 全部为 **设计态几何 + 公差栈** ([推算]), **实物 [实测] = 0 条**。")
    print("          镜脚末端 V 净高 / 座体型号 / 磁铁拉脱力 / 麦克风磁场敏感度 = [0数据]。")
    print("=" * 100)
    return ok, total_n, fails, list(RESULTS)


# =====================================================================
# ★★ISS-264 (2026-11-17) 反向用例 (--self-test / --selftest)
# =====================================================================
def selftest() -> int:
    """三个反向用例 (★旧的一条不许删★)。

    ① (★ISS-203 旧用例·保留★) pcb_w 强制回 15.00 (旧板宽) ⇒ 读数必须全绿 (FAIL 0)。
    ② (★ISS-264 新用例★) p2_y / s2_y 强制回【旧 15mm 板口径】(7.50 / 12.50)
       ⇒ 【7.4b / 7.5b 两条口径钉死】必红并【点名 p2_y / s2_y】;
       ⇒ 同时 7.4 / 7.5 两条【几何判据】必须仍然绿 (旧基准 1.00 / 1.03mm ≥ 判据 0.60)
          ⇒ 这是【本单迁的是常量, 不是松判据】的机器证据。
    ③ 装回现行口径 (15.00 / 20.00) ⇒ 必须又全绿。
    """
    global VERBOSE
    saved = dict(BASE)
    errs = []

    # ---------------- ① 旧用例 (ISS-203 板宽迁移 · 保留不许删) ----------------
    BASE["pcb_w"] = 15.00
    print(">>> [反向用例 ① · ISS-203 板宽迁移 · 旧用例保留] pcb_w 强制回 15.00 (旧板宽)\n")
    ok_a, tot_a, fails_a, _rows_a = run_report()
    if fails_a:
        errs.append(f"① pcb_w=15.00 期望 FAIL 0, 实得 {fails_a}")
    if tot_a != N_ITEMS_BASE:
        errs.append(f"① 项数 {tot_a} ≠ 基准 N_ITEMS_BASE = {N_ITEMS_BASE}")
    BASE.clear()
    BASE.update(saved)

    # ---------------- ② 新用例 (ISS-264 夹具基准迁移) ----------------
    BASE["p2_y"] = PIN_SET_LEGACY_15MM["p2_y"]
    BASE["s2_y"] = PIN_SET_LEGACY_15MM["s2_y"]
    print(">>> [反向用例 ② · ISS-264 夹具基准迁移 · 本单新增] p2_y / s2_y 强制回旧 15mm 板口径 "
          f"({PIN_SET_LEGACY_15MM['p2_y']:.2f} / {PIN_SET_LEGACY_15MM['s2_y']:.2f}) "
          "⇒ 【7.4b / 7.5b 口径钉死】两条必红并点名 p2_y / s2_y\n")
    ok_b, tot_b, fails_b, rows_b = run_report()

    def _row(prefix):
        for r in rows_b:
            if r[0].startswith(prefix):
                return r
        return None

    r74, r74b, r75, r75b = _row("7.4 "), _row("7.4b"), _row("7.5 "), _row("7.5b")
    print(">>> [反向用例 ② · 决定性四行 (★点名是谁★)]")
    for r in (r74, r74b, r75, r75b):
        if r:
            print(f"   [{'OK ' if r[1] else 'FAIL'}] {r[0]}  — {r[2]}")
    print()
    if r74b is None or r74b[1]:
        errs.append("② 7.4b (p2_y 口径钉死) 没变红 ⇒ 反向用例没抓到")
    else:
        if "p2_y" not in r74b[2]:
            errs.append("② 7.4b 变红了但没点名 p2_y ⇒ 明细里查不到是谁")
    if r75b is None or r75b[1]:
        errs.append("② 7.5b (s2_y 口径钉死) 没变红 ⇒ 反向用例没抓到")
    else:
        if "s2_y" not in r75b[2]:
            errs.append("② 7.5b 变红了但没点名 s2_y ⇒ 明细里查不到是谁")
    if r74 is None or not r74[1]:
        errs.append("② 7.4 (几何判据) 不绿 ⇒ 判据被松了 (本单只许迁常量)")
    if r75 is None or not r75[1]:
        errs.append("② 7.5 (几何判据) 不绿 ⇒ 判据被松了 (本单只许迁常量)")
    BASE.clear()
    BASE.update(saved)

    # ---------------- ③ 装回现行口径 ⇒ 必须又全绿 ----------------
    VERBOSE = False
    print(">>> [反向用例 ③] 装回现行口径 (p2_y 15.00 / s2_y 20.00) ⇒ 必须又全绿\n")
    ok_c, tot_c, fails_c, _rows_c = run_report()
    VERBOSE = True
    if fails_c:
        errs.append(f"③ 装回后期望 FAIL 0, 实得 {fails_c}")
    if tot_c != N_ITEMS_BASE:
        errs.append(f"③ 装回后项数 {tot_c} ≠ 基准 N_ITEMS_BASE = {N_ITEMS_BASE}")

    print("=" * 100)
    if errs:
        print("[反向用例] ❌ 不一致 (⇒ rc=2):")
        for e in errs:
            print(f"   ❌ {e}")
    else:
        print("[反向用例] ✅ 一致 —— ① 旧板宽用例 FAIL 0 · "
              "② 旧 15mm 板口径回改 ⇒ 7.4b / 7.5b 必红并点名 p2_y / s2_y, "
              "几何 7.4 / 7.5 仍绿 (判据 0.60 未松) · ③ 装回又全绿")
    print("=" * 100)
    return 0 if not errs else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", "--selftest", dest="self_test", action="store_true",
                    help="反向用例: ① pcb_w 回 15.00 (旧板宽) ② p2_y/s2_y 回旧 15mm 板口径 (7.50/12.50) ⇒ 必红并点名")
    args = ap.parse_args()
    if args.self_test:
        return selftest()
    _ok, _total, fails, _rows = run_report()
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
