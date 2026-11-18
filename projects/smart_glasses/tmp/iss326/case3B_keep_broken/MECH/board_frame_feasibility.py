#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
board_frame_feasibility.py —— ISS-310 「板框口径代价对照 (MECH 侧)」机器复算器 (mech-lead)
=================================================================================================
干什么:
  给 main / 老板一张【机器可判的板框可行域表】, 让「板只改一次」那一趟画在哪个框上这件事
  能被【逐档复算】, 而不是靠两页 MECH 文档互相打架。

  逐档矩阵: ★三套框 × 板厚档 {0.80 / 1.00 / 1.22 / 1.60} × 层数 {4 / 6 / 8} = 36 档★
  每一档出: ★H 链 需求/余 · 盖板内腔 (判据 4.50) · V 链 需求/余/最坏 · L 链 需求/余 ·
  套 A 孔位成立性 (P1/P2/S1/S2 各判) · P-5 净空 · 板重 · 层数档原生性 · 开口能不能开 (是/否 + 判红原因)★

★口径纪律 (硬) ★
  ① **判据阈值一个字节都不许自己写** ⇒ 本脚本把 `MECH/service_port_check.py` **当只读模块 import**,
     直接取它的 `BASE` / `TOL` / `CRIT` ⇒ 阈值零漂移 (与 `MECH/board_port_opening_s6_check.py` 同法)。
  ② **每个判据都标出处** (脚本内 `SOURCES` 表 + 打印时的表 0) ⇒ 不存在「写死在脚本里当事实」的数。
  ③ **不改任何既有文件** (★`service_port_check.py` / `check_onepass_mech_sync.py` /
     `check_onepass_struct_crosscheck.py` / `check_board_frame_coords.py` / `board_port_opening_s6_check.py` /
     `state/gate_check.py` 一个字节没动★) —— 本文件是**新增的独立脚本**。
  ④ **不拍板**: 板框口径 / 层数 / 板厚 只「列档 + 判红原因 + 谁拍」, 不代拍。
  ⑤ 证据级: 全部几何读数 = **设计态几何 + 公差栈** ⇒ `[推算]`; 盘上板读数 (Edge.Cuts / 板厚) = `[实测]`。
  ⑥ **零写盘**: 本脚本只读既有文件 + 只打印 + 只写自己的输出 (不写任何既有文件)。

用法:
  python3 MECH/board_frame_feasibility.py            ⇒ 打印 表0~表4
  python3 MECH/board_frame_feasibility.py --selftest  ⇒ 反向用例 (★7 条, 一条不许删★) ⇒ rc=0
  python3 MECH/board_frame_feasibility.py --json      ⇒ 机器可读

退出码: 0 = 复算完成 (★不代表实物已验★); `--selftest` 下 2 = 反向用例不一致。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPC_PATH = os.path.join(HERE, "service_port_check.py")
PCB_PATH = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")


# ==================================================================================================
# ★只读 import 既有闸脚本 ⇒ 阈值零漂移 (★不写回、不改它★)
# ==================================================================================================
def load_spc():
    spec = importlib.util.spec_from_file_location("spc_readonly_iss310", SPC_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # ★只执行模块顶层 (无副作用: 只定义常量与函数)★
    return mod


SPC = load_spc()
BASE = dict(SPC.BASE)                    # ★拷贝 ⇒ 本脚本改自己的副本, 绝不污染闸脚本的全局★
TOL = dict(SPC.TOL)
CRIT = SPC.CRIT                          # 0.60 = 2 × TOL['fdm_part']


# ==================================================================================================
# ★判据出处表 (★每个阈值都能追到一行出处★) —— 打印成表 0
# ==================================================================================================
SOURCES = {
    "cav_h":    "MECH/service_port_check.py BASE['cav_h'] = 7.30 (镜脚内腔厚, 老板锁死; ISS-092 §1.6.2)",
    "cav_v":    "MECH/service_port_check.py BASE['cav_v'] = 38.00 (根部净高; ISS-092 §1.6.2)",
    "cav_l":    "MECH/service_port_check.py BASE['cav_l'] = 130.00 (内腔长; ISS-092 §1.6.2)",
    "wall":     "MECH/service_port_check.py BASE['wall'] = 0.80 (FDM 最小可靠单壁; §5.4)",
    "frame_thk": "MECH/service_port_check.py BASE['frame_thk'] = 1.00 (铝/铜骨架; §5.1)",
    "air_gap":  "MECH/service_port_check.py BASE['air_gap'] = 0.30 (皮肤侧空气隙; §2.4)",
    "pad_thermal": "MECH/service_port_check.py BASE['pad_thermal'] = 0.50 (皮肤侧隔热垫; §2.4)",
    "duct_v":   "MECH/service_port_check.py BASE['duct_v'] = 6.00 (垂直走线槽占位; §5.6.2)",
    "cell_l":   "MECH/service_port_check.py BASE['cell_l'] = 40.50 (电芯长; §1.6.1)",
    "conn_margin": "MECH/service_port_check.py BASE['conn_margin'] = 15.00 (连接器弯折/插拔余量; §1.4.2)",
    "cavity_req": "MECH/service_port_check.py BASE['cavity_req'] = 4.50 (ISS-085 §6.1 硬要求)",
    "CRIT":     "MECH/service_port_check.py CRIT = 2 × TOL['fdm_part'] = 0.60 (FDM 外形 ±0.30 ⇒ 2×0.30)",
    "h_pcb_face": "MECH/service_port_check.py BASE['h_pcb_face'] = 壁0.8+隔热0.5+空隙0.3+PCB厚 (脚本 §1.2)",
    "h_chain":  "MECH/BOARD_GEOM_30MM.md §5.4 第 4 条 (= 3.40 + t; 本脚本同式) + MECH/iss127_h_chain_check.py:168",
    "v_chain":  "MECH/service_port_check.py §5.4 (V PCB 段 = pcb_w + duct_v vs cav_v)",
    "l_chain":  "MECH/service_port_check.py §5.5 (L 需求 = cell_l + pcb_l + conn_margin vs cav_l)",
    "cover_cavity": "MECH/service_port_check.py §4.2 (盖板内腔 = h_outer_out − h_pcb_face)",
    "pinset_a": "MECH/BOARD_GEOM_30MM.md §3 (PIN-SET-2 套 A: P1(8,15) P2(52,15) S1(8,10) S2(52,20))",
    "hole_fit": "MECH/board_port_opening_s6_check.py holes_fit_frame() (孔壁 vs 板边, 板 Y 区间 [0, pcb_w])",
    "p5_gap":   "MECH/service_port_check.py 检查项 7.4 / 7.5 (孔壁→焊盘阵列 最近距离, 判据 ≥ CRIT)",
    "jd_geom":  "MECH/service_port_check.py §2/§3 (jd_x0=50.50 / jd_y0=9.50 / 2×5 @1.27 / 开口 10.20×4.60)",
    "weight":   "MECH/BOARD_GEOM_30MM.md §1 (板重 = 面积 × 板厚 × 1.85 g/cc; 60×30×1.0 ⇒ 3.33g)",
    "mass_tot": "MECH/service_port_check.py BASE['mass_total_lo'/'mass_total_hi'] = 48.90 / 72.80 (整机)",
    "frames":   "HW/PCB/BOARD_FRAME_CALIBER.md §2 cal:FRAMES (帧 id 唯一权威: B160x100 / F30A / P60x15)",
    "board_read": "HW/PCB/demo_mainboard.kicad_pcb Edge.Cuts + general/thickness (本脚本只读实读)",
}

# ==================================================================================================
# ★三套框 (★帧 id 用 `HW/PCB/BOARD_FRAME_CALIBER.md` §2 `cal:FRAMES` 的权威写法★)
#   · pcb_l = 板 X 向长 (MECH 口径 pcb_l) · pcb_w = 板 Y 向宽 (MECH 口径 pcb_w)
#   · 台架板 X=160 / Y=100 ⇒ pcb_l=160 / pcb_w=100 (★与 MECH/DEBUG_PORT_LAYOUT_CONSTRAINTS.md 表 2 同: V 链需求 106 = 100+6★)
# ==================================================================================================
FRAMES = [
    {
        "fid": "B160x100",
        "name": "① 台架板 160×100 (盘上现役)",
        "pcb_l": 160.00,
        "pcb_w": 100.00,
        "native_layers": 8,
        "native_thk": 1.60,
        "pinset_applicable": False,   # ★套 A 是 F30A 帧的坐标, 套到台架板帧 = 口径不适用★
        "src": "HW/PCB/demo_mainboard.kicad_pcb Edge.Cuts 实读 + HW/PCB/BOARD_FRAME_CALIBER.md §2 cal:FRAMES",
    },
    {
        "fid": "F30A",
        "name": "② 产品板 60×30 套 A (MECH 现行)",
        "pcb_l": 60.00,
        "pcb_w": 30.00,
        "native_layers": 6,
        "native_thk": 1.00,
        "pinset_applicable": True,
        "src": "MECH/BOARD_GEOM_30MM.md §0/§1/§3 (ISS-118/130, 老板 10-29 19:16 板宽 30)",
    },
    {
        "fid": "P60x15",
        "name": "③ 产品板 60×15 (原始定版 · 板宽已作废)",
        "pcb_l": 60.00,
        "pcb_w": 15.00,
        "native_layers": 6,
        "native_thk": 1.00,
        "pinset_applicable": True,
        "src": "HW/PCB_OUTLINE_60x15.md §1.1 (ISS-105/118; 板宽 15 已于 ISS-118 放宽为 30 ⇒ 现为作废口径)",
    },
]

# ★板厚四档 (★出处: ISS-122/ISS-126 的板厚四档 + 盘上板实测 1.60★)
THICKNESS_TIERS = [
    (0.80, "4 层旧口径 (ISS-206 依 MECH/BOARD_GEOM_30MM.md §1 已标作废)"),
    (1.00, "6 层现行 (MECH/BOARD_GEOM_30MM.md §1 · service_port_check BASE['pcb_thk'])"),
    (1.22, "ISS-122/ISS-126 板厚四档之一 (MECH/iss127_h_chain_check.py:521) — ★项目内无现役板用此档★"),
    (1.60, "盘上台架板实测 (HW/PCB/demo_mainboard.kicad_pcb general/thickness 1.6, 8 铜层)"),
]
LAYER_TIERS = [4, 6, 8]

# ★PIN-SET-2 套 A 四孔 (MECH/BOARD_GEOM_30MM.md §3)
PIN_SET_A = {
    "P1": (8.00, 15.00, 2.00),
    "P2": (52.00, 15.00, 2.00),
    "S1": (8.00, 10.00, 1.40),
    "S2": (52.00, 20.00, 1.40),
}

# ★J_DEBUG 焊盘阵列 + 开口 (MECH/service_port_check.py §2/§3; MECH/board_port_opening_s6_check.py 同式)
JD_X0, JD_Y0 = 50.50, 9.50
OPEN_X, OPEN_Y = 10.20, 4.60
GRAPHITE_T = 0.30          # MECH/BOARD_GEOM_30MM.md §5.4 第 4 条 (+石墨 0.30 的口径)
RHO_PCB = 1.85            # g/cc, MECH/BOARD_GEOM_30MM.md §1 (板重口径)


# ==================================================================================================
# 盘上板只读实读 (★零写盘★)
# ==================================================================================================
def read_board_edge_cuts(path: str = PCB_PATH) -> dict:
    """只读解析 Edge.Cuts ⇒ 包围盒 (板框) + general/thickness

    ★KiCad 6/7 风格: `(gr_line` 是多行块 ⇒ 按括号配平取块 (同 MECH/board_port_opening_s6_check.py 的做法)★
    ★本函数只读, 一个字节不写★"""
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    xs, ys = [], []
    thk = None
    for ln in lines:
        m = re.search(r"\(thickness ([0-9.]+)\)", ln)
        if m and thk is None:
            thk = float(m.group(1))
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("(gr_line"):
            depth = 0
            j = i
            while j < len(lines):
                depth += lines[j].count("(") - lines[j].count(")")
                if depth == 0 and j > i:
                    break
                j += 1
            blk = "\n".join(lines[i:j + 1])
            if "Edge.Cuts" in blk:
                st = re.search(r"\(start ([-\d.]+) ([-\d.]+)\)", blk)
                en = re.search(r"\(end ([-\d.]+) ([-\d.]+)\)", blk)
                if st and en:
                    xs += [float(st.group(1)), float(en.group(1))]
                    ys += [float(st.group(2)), float(en.group(2))]
            i = j + 1
        else:
            i += 1
    if not xs:
        return {"ok": False, "thickness": thk}
    return {"ok": True, "x0": min(xs), "x1": max(xs), "y0": min(ys), "y1": max(ys),
            "w": max(xs) - min(xs), "h": max(ys) - min(ys), "thickness": thk}


# ==================================================================================================
# 几何 (★照闸脚本 §2/§3/§4/§5/§7/§8 同式, 每行注出处★)
# ==================================================================================================
def open_geometry(jd_x0: float = JD_X0, jd_y0: float = JD_Y0) -> dict:
    """开口 + 必须清空区 + 单边间隙 (X/Y) —— 同 MECH/board_port_opening_s6_check.py open_geom()"""
    pitch = BASE["jd_pitch"]
    jd_x1 = jd_x0 + (BASE["jd_cols"] - 1) * pitch
    jd_y1 = jd_y0 + (BASE["jd_rows"] - 1) * pitch
    ju_x0 = jd_x1 + BASE["ju_gap"]
    ju_x1 = ju_x0 + (BASE["ju_cols"] - 1) * pitch
    pad_x0, pad_x1 = min(jd_x0, ju_x0), max(jd_x1, ju_x1)
    body_y_c = (jd_y0 + jd_y1) / 2.0
    body_y0 = body_y_c - BASE["jd_body_h"] / 2.0
    body_y1 = body_y_c + BASE["jd_body_h"] / 2.0
    content_w = pad_x1 - pad_x0
    content_h = body_y1 - body_y0
    cl_x = (OPEN_X - content_w) / 2.0
    cl_y = (OPEN_Y - content_h) / 2.0
    return {
        "content_w": content_w, "content_h": content_h,
        "cl_x": cl_x, "cl_y": cl_y,
        "worst_cl_x": cl_x - TOL["fdm_part"], "worst_cl_y": cl_y - TOL["fdm_part"],
        "open_x0": pad_x0 - cl_x, "open_x1": pad_x1 + cl_x,
        "open_y0": body_y0 - cl_y, "open_y1": body_y1 + cl_y,
        "pad_y0": jd_y0, "pad_y1": jd_y1,
    }


def holes_fit(pcb_l: float, pcb_w: float, pinset: dict = None) -> dict:
    """套 A 四孔在某板框下成不成立 (孔壁 vs 板边) —— 同 MECH/board_port_opening_s6_check.py holes_fit_frame()"""
    pinset = pinset or PIN_SET_A
    rows = []
    for tag, (hx, hy, hd) in pinset.items():
        y0, y1 = hy - hd / 2.0, hy + hd / 2.0
        x0, x1 = hx - hd / 2.0, hx + hd / 2.0
        out_y = max(0.0, y1 - pcb_w) + max(0.0, -y0)
        out_x = max(0.0, x1 - pcb_l) + max(0.0, -x0)
        rows.append({"hole": tag, "center": (hx, hy), "d": hd,
                     "wall_y": (y0, y1), "wall_x": (x0, x1),
                     "outside_mm": round(out_y + out_x, 4),
                     "fit": (out_y + out_x) <= 1e-9})
    return {"holes": rows, "all_fit": all(r["fit"] for r in rows)}


def p5_clearance(jd_y0: float = JD_Y0, pinset: dict = None) -> dict:
    """P-5: 夹具基准孔壁 → 焊盘阵列 最近距离 (闸脚本 7.4 / 7.5 通用式)"""
    pinset = pinset or PIN_SET_A
    jd_y1 = jd_y0 + (BASE["jd_rows"] - 1) * BASE["jd_pitch"]
    out = {}
    for tag in ("P2", "S2"):
        hx, hy, hd = pinset[tag]
        y0, y1 = hy - hd / 2.0, hy + hd / 2.0
        gap = max(y0 - jd_y1, jd_y0 - y1)
        out[tag.lower() + "_gap"] = round(gap, 4)
        out[tag.lower() + "_ok"] = gap >= CRIT
    return out


def chains(pcb_l: float, pcb_w: float, pcb_thk: float, graphite: float = 0.0) -> dict:
    """H / 盖板内腔 / V / L 四条判据 (★照 service_port_check.py §1.2/§4.2/§5.2/§5.4/§5.5 同式★)"""
    # H 链 (PCB/骨架堆叠) = 壁0.8 + 骨架1.0 + PCB t + 空隙0.3 + 隔热0.5 + 壁0.8 = 3.40 + t
    h_need = (BASE["wall"] + BASE["frame_thk"] + pcb_thk
              + BASE["air_gap"] + BASE["pad_thermal"] + BASE["wall"])
    h_margin = BASE["cav_h"] - h_need
    h_margin_g = BASE["cav_h"] - (h_need + graphite)
    # 盖板内腔 = 外表面 7.30 − PCB 元件面 (壁0.8+隔热0.5+空隙0.3+PCB厚)
    h_pcb_face = BASE["wall"] + BASE["pad_thermal"] + BASE["air_gap"] + pcb_thk
    cavity = BASE["h_outer_out"] - h_pcb_face
    # V 链 = pcb_w + duct_v vs cav_v (最坏 = 名义 − 2×FDM 0.30)
    v_need = pcb_w + BASE["duct_v"]
    v_margin = BASE["cav_v"] - v_need
    v_worst = v_margin - 2 * TOL["fdm_part"]
    # L 链 = cell_l + pcb_l + conn_margin vs cav_l
    l_need = BASE["cell_l"] + pcb_l + BASE["conn_margin"]
    l_margin = BASE["cav_l"] - l_need
    return {
        "h_need": h_need, "h_margin": h_margin,
        "h_margin_worst_obs": h_margin - 2 * TOL["fdm_part"],
        "h_margin_graphite": h_margin_g,
        "h_ok": h_margin >= CRIT,
        "h_pcb_face": h_pcb_face,
        "cavity": cavity, "cavity_margin": cavity - BASE["cavity_req"],
        "cavity_ok": cavity >= BASE["cavity_req"],
        "v_need": v_need, "v_margin": v_margin, "v_worst": v_worst,
        "v_ok": (v_margin >= CRIT) and (v_worst >= CRIT),
        "l_need": l_need, "l_margin": l_margin, "l_ok": l_margin >= CRIT,
    }


def board_weight_g(pcb_l: float, pcb_w: float, pcb_thk: float) -> float:
    """板重 (g) = 面积 × 板厚 × 1.85 g/cc (MECH/BOARD_GEOM_30MM.md §1)"""
    return pcb_l * pcb_w * pcb_thk / 1000.0 * RHO_PCB


def evaluate(frame: dict, layers: int, thk: float, *,
             pcb_l: float = None, pcb_w: float = None,
             cavity_override: float = None,
             pinset: dict = None) -> dict:
    """算一档 (frame × layers × thk) ⇒ 全部判据 + 开口能不能开 + 判红原因"""
    pcb_l = frame["pcb_l"] if pcb_l is None else pcb_l
    pcb_w = frame["pcb_w"] if pcb_w is None else pcb_w
    c = chains(pcb_l, pcb_w, thk)
    if cavity_override is not None:
        c["cavity"] = cavity_override
        c["cavity_margin"] = cavity_override - BASE["cavity_req"]
        c["cavity_ok"] = cavity_override >= BASE["cavity_req"]
    pinset = pinset or PIN_SET_A
    holes = holes_fit(pcb_l, pcb_w, pinset)
    p5 = p5_clearance(JD_Y0, pinset)
    og = open_geometry()
    weight = board_weight_g(pcb_l, pcb_w, thk)
    native = (layers == frame["native_layers"] and abs(thk - frame["native_thk"]) < 1e-9)

    reds = []
    if not c["h_ok"]:
        reds.append(f"H 链余 {c['h_margin']:+.2f} < {CRIT:.2f}")
    if not c["cavity_ok"]:
        reds.append(f"盖板内腔 {c['cavity']:.2f} < {BASE['cavity_req']:.2f} "
                    f"(余 {c['cavity_margin']:+.2f})")
    if not c["v_ok"]:
        reds.append(f"V 链 余 {c['v_margin']:+.2f} / 最坏 {c['v_worst']:+.2f} < {CRIT:.2f}")
    if not c["l_ok"]:
        reds.append(f"L 链 余 {c['l_margin']:+.2f} < {CRIT:.2f}")
    if frame["pinset_applicable"] and not holes["all_fit"]:
        bad = [f"{h['hole']} 板外 {h['outside_mm']:.2f}" for h in holes["holes"] if not h["fit"]]
        reds.append("套 A 孔位不成立 (" + " · ".join(bad) + ") ⇒ 开口 Y 的 P-5 判据无基准")
    if frame["pinset_applicable"]:
        for tag in ("p2", "s2"):
            if not p5[tag + "_ok"]:
                reds.append(f"P-5 {tag.upper()} 净空 {p5[tag + '_gap']:.2f} < {CRIT:.2f}")

    # 开口末端是否落在板末端 (镜脚末端承接) —— 【观察项】, 判红与否见 ISS-271 §3.1 原文
    end_margin = pcb_l - og["open_x1"]
    at_end = end_margin <= 2.0     # ★2.0 = 观察阈 (F30A 现状 0.59 / P60x15 0.59 / 台架板 100.59)★

    return {
        "frame_id": frame["fid"], "frame_name": frame["name"],
        "pcb_l": pcb_l, "pcb_w": pcb_w, "layers": layers, "thk": thk,
        "native": native,
        "h_need": c["h_need"], "h_margin": c["h_margin"],
        "h_margin_graphite": c["h_margin_graphite"],
        "cavity": c["cavity"], "cavity_margin": c["cavity_margin"], "cavity_ok": c["cavity_ok"],
        "v_need": c["v_need"], "v_margin": c["v_margin"], "v_worst": c["v_worst"], "v_ok": c["v_ok"],
        "l_need": c["l_need"], "l_margin": c["l_margin"], "l_ok": c["l_ok"],
        "holes": holes, "p5": p5,
        "open_x": (og["open_x0"], og["open_x1"]), "open_y": (og["open_y0"], og["open_y1"]),
        "open_end_margin_x": end_margin, "open_at_board_end": at_end,
        "weight_g": weight,
        "weight_pct_lo": weight / BASE["mass_total_hi"] * 100.0,
        "weight_pct_hi": weight / BASE["mass_total_lo"] * 100.0,
        "can_open": (len(reds) == 0),
        "red_reasons": reds,
    }


def all_rows() -> list:
    rows = []
    for fr in FRAMES:
        for layers in LAYER_TIERS:
            for thk, _why in THICKNESS_TIERS:
                rows.append(evaluate(fr, layers, thk))
    return rows


# ==================================================================================================
# 打印
# ==================================================================================================
def print_table0() -> None:
    print("=" * 108)
    print("【表 0】判据出处表 (★每个阈值都能追到一行出处; 本脚本阈值零自造 = 只读 import service_port_check.py★)")
    print("=" * 108)
    for k, v in SOURCES.items():
        print(f"  {k:<16} = {v}")
    print()


def print_table1(rows: list) -> None:
    print("=" * 108)
    print("【表 1】主表 —— 三套框 × 板厚四档 × 层数三档 (36 档)  ★机器可判★")
    print("=" * 108)
    hdr = (f"{'帧':<10}{'层':>4}{'板厚':>7}{'原生':>5} | {'H需求':>7}{'H余':>8} | "
           f"{'内腔':>7}{'余':>7} | {'V需求':>8}{'V余':>8}{'最坏':>8} | {'L需求':>8}{'L余':>8} | "
           f"{'套A孔位':>10}{'P2/S2净空':>12} | {'板重g':>8} | 开口")
    print(hdr)
    print("-" * 108)
    for r in rows:
        if r["frame_id"] == "B160x100":
            # ★套 A 四孔是 F30A 帧的坐标 ⇒ 套到台架板帧 = 口径不适用 (不是「孔位不成立」)★
            holes = "口径不适用"
        else:
            holes = ("全部成立" if r["holes"]["all_fit"]
                     else "不成立(" + ",".join(h["hole"] for h in r["holes"]["holes"] if not h["fit"]) + ")")
        p5s = f"{r['p5']['p2_gap']:.2f}/{r['p5']['s2_gap']:.2f}" if r["frame_id"] != "B160x100" else "口径不适用"
        mark = "✅ 能开" if r["can_open"] else "❌ 不能开"
        print(f"{r['frame_id']:<10}{r['layers']:>4}{r['thk']:>7.2f}{'★' if r['native'] else ' ':>5} | "
              f"{r['h_need']:>7.2f}{r['h_margin']:>+8.2f} | "
              f"{r['cavity']:>7.2f}{r['cavity_margin']:>+7.2f} | "
              f"{r['v_need']:>8.2f}{r['v_margin']:>+8.2f}{r['v_worst']:>+8.2f} | "
              f"{r['l_need']:>8.2f}{r['l_margin']:>+8.2f} | "
              f"{holes:>10}{p5s:>12} | {r['weight_g']:>8.3f} | {mark}")
    print("-" * 108)
    print("  ★原生 = 该 (层数, 板厚) 与 `HW/PCB/BOARD_FRAME_CALIBER.md` §2 cal:FRAMES 里该帧声明的 (layers, thickness) 一致;")
    print("    非原生档 = 必须先重声明 cal:FRAMES + 重算叠层/阻抗文档 (⇒ 那是【连带成本】, 不是几何判红)。")
    print("  ★层数**不进入**本表任何几何判据 (H/V/L/内腔/孔位都是纯几何) ⇒ 层数只改变【原生档标记】与【连带成本】。")
    print()


def print_table2(rows: list) -> None:
    print("=" * 108)
    print("【表 2】三套框 × 板厚四档 (各框取其原生层数) —— 开口能不能开 + 判红原因")
    print("=" * 108)
    for fr in FRAMES:
        print(f"\n  {fr['name']}  (帧 id `{fr['fid']}` · 原生 {fr['native_layers']} 层 / {fr['native_thk']:.2f}mm "
              f"· {fr['pcb_l']:.2f}×{fr['pcb_w']:.2f} · 出处: {fr['src']})")
        for thk, why in THICKNESS_TIERS:
            r = evaluate(fr, fr["native_layers"], thk)
            mark = "✅ 能开" if r["can_open"] else "❌ 不能开"
            print(f"    · 板厚 {thk:.2f}mm  {mark}"
                  + ("" if r["can_open"] else "  ⇒ " + " ; ".join(r["red_reasons"])))
            print(f"        (内腔 {r['cavity']:.2f} 余 {r['cavity_margin']:+.2f} | V 余 {r['v_margin']:+.2f}/最坏 {r['v_worst']:+.2f} "
                  f"| L 余 {r['l_margin']:+.2f} | H 余 {r['h_margin']:+.2f} | 板重 {r['weight_g']:.2f}g "
                  f"= 整机 {r['weight_pct_lo']:.1f}~{r['weight_pct_hi']:.1f}%)")
            print(f"        板厚出处: {why}")
    print()


def print_table3(rows: list) -> None:
    print("=" * 108)
    print("【表 3】开口落点与承接 (观察项) —— 开口 X/Y 是 60×30 套 A 帧的模型坐标")
    print("=" * 108)
    og = open_geometry()
    print(f"  开口 = X {og['open_x0']:.2f}..{og['open_x1']:.2f} (宽 {OPEN_X:.2f}) × "
          f"Y {og['open_y0']:.3f}..{og['open_y1']:.3f} (宽 {OPEN_Y:.2f})")
    print(f"  必须清空区 = X 宽 {og['content_w']:.2f} × Y 高 {og['content_h']:.2f} "
          f"(Cortex-10 座体高 2.54 = 假设, [0数据])")
    print(f"  单边间隙 X {og['cl_x']:.2f} / Y {og['cl_y']:.2f} (最坏 {og['worst_cl_x']:.2f} / {og['worst_cl_y']:.2f}) "
          f"⇒ 判据 ≥{CRIT:.2f}")
    print()
    for fr in FRAMES:
        r = evaluate(fr, fr["native_layers"], fr["native_thk"])
        print(f"  · {fr['fid']:<10} 开口末端距板端 = {r['open_end_margin_x']:.2f}mm "
              f"⇒ {'在板末端 (镜脚末端有结构承接)' if r['open_at_board_end'] else '★不在板末端 ⇒ 镜脚末端无结构承接 (ISS-271 §3.1 原文)'}")
    print()


def print_table4(rows: list) -> None:
    print("=" * 108)
    print("【表 4】板重账 (面积 × 板厚 × 1.85 g/cc) vs 整机质量预算 48.90 / 72.80 g")
    print("=" * 108)
    print(f"  {'帧':<10}{'层':>4}{'板厚':>7}{'面积mm²':>10}{'板重g':>9}{'占整机下限':>12}{'占整机上限':>12}  说明")
    for r in rows:
        if not r["native"]:
            continue
        print(f"  {r['frame_id']:<10}{r['layers']:>4}{r['thk']:>7.2f}"
              f"{r['pcb_l'] * r['pcb_w']:>10.1f}{r['weight_g']:>9.3f}"
              f"{r['weight_pct_hi']:>11.1f}%{r['weight_pct_lo']:>11.1f}%"
              + ("  ★板本身已吃掉整机质量预算的大头" if r["weight_pct_hi"] > 50 else ""))
    print("  ★占整机比例: 下限列 = 板重 / 整机上限 72.80g; 上限列 = 板重 / 整机下限 48.90g。")
    print()


def print_table5(rows: list) -> None:
    print("=" * 108)
    print("【表 5】结论 (★只列判定 + 谁拍, 不代拍★)")
    print("=" * 108)
    for fr in FRAMES:
        native_rows = [evaluate(fr, fr["native_layers"], t) for t, _ in THICKNESS_TIERS]
        green = [r for r in native_rows if r["can_open"]]
        red = [r for r in native_rows if not r["can_open"]]
        print(f"  · 帧 `{fr['fid']}` ({fr['name']})")
        print(f"      原生层数下【能开】的板厚档: "
              + (", ".join(f"{r['thk']:.2f}mm" for r in green) if green else "★无 (该框全部板厚档判红)★"))
        print(f"      原生层数下【判红】的板厚档: "
              + (", ".join(f"{r['thk']:.2f}mm ({r['red_reasons'][0]})" for r in red) if red else "无"))
    print()
    print("  ★「能开」= 本域几何判据 (H/V/L 三链 + 盖板内腔 + 套 A 孔位 + P-5) 全绿。")
    print("  ★它**不**回答「这一趟画它划不划算」⇒ 那在 `MECH/BOARD_FRAME_DECISION_INPUT.md` §C/§D (两条路线代价)。")
    print("  ★它**不**回答「P7 的 23 条跨 SoM 主体腿能不能在 30mm 宽内布通」⇒ 那是 HW 域的活。")
    print()


# ==================================================================================================
# ★反向用例 (--selftest) —— 一条不许删 ★
# ==================================================================================================
def selftest() -> int:
    errs = []
    print("=" * 108)
    print("[反向用例] ISS-310 board_frame_feasibility.py —— ★目标: 抓住「改了参数还判绿」的假闸★")
    print("=" * 108)

    def ok(cond, msg):
        if cond:
            print(f"  [OK ] {msg}")
        else:
            print(f"  [NG ] {msg}")
            errs.append(msg)
        return bool(cond)

    F_B = FRAMES[0]
    F_A = FRAMES[1]
    F_C = FRAMES[2]

    # ---------------- ① 盖板内腔改到 4.00 ⇒ 必须判红 (任务书 (a)) ----------------
    print("\n>>> ① 盖板内腔人为改到 4.00 (F30A / 6 层 / 1.00mm) ⇒ 必须判红")
    base = evaluate(F_A, 6, 1.00)
    ok(base["can_open"], f"①a 基线 F30A/6层/1.00mm = 能开 (内腔 {base['cavity']:.2f})")
    bad = evaluate(F_A, 6, 1.00, cavity_override=4.00)
    ok(not bad["can_open"], "①b 内腔改 4.00 ⇒ 整档判红")
    ok(any("盖板内腔 4.00" in s for s in bad["red_reasons"]),
       f"①c 判红原因点名盖板内腔: {bad['red_reasons']}")

    # ---------------- ② 套 A 孔位搬到 15mm 板 ⇒ 必须判「孔位不成立」 (任务书 (b)) ----------------
    print("\n>>> ② 套 A 孔位搬到 15mm 板 (P2 孔心 Y=15.00) ⇒ 必须判「孔位不成立」")
    r15 = evaluate(F_C, 6, 1.00)
    p2_15 = [h for h in r15["holes"]["holes"] if h["hole"] == "P2"][0]
    ok(not p2_15["fit"],
       f"②a P2 (52.00,15.00) ⌀2.0 在 15mm 板上孔壁 Y {p2_15['wall_y'][0]:.2f}..{p2_15['wall_y'][1]:.2f} "
       f"⇒ 板外 {p2_15['outside_mm']:.2f}mm ⇒ 不成立")
    ok(not r15["can_open"], "②b 60×15 整档判红")
    ok(any("孔位不成立" in s for s in r15["red_reasons"]),
       f"②c 判红原因点名孔位: {r15['red_reasons']}")
    # ★反向对照: 同一套孔位在 30mm 板上必须全部成立 (证明判据对板宽敏感, 不是恒真)
    r30 = evaluate(F_A, 6, 1.00)
    ok(r30["holes"]["all_fit"], "②d 对照: 同一套孔位在 30mm 板上全部成立 (⇒ 孔位判据对板宽敏感)")

    # ---------------- ③ pcb_thk 1.60 → 1.00 ⇒ 内腔 4.10 → 4.70 且判定 ❌ → ✅ (任务书 (c)) ----------------
    print("\n>>> ③ 台架板 pcb_thk 1.60 → 1.00 ⇒ 盖板内腔必须 4.10 → 4.70, 内腔判定 ❌ → ✅")
    b16 = evaluate(F_B, 8, 1.60)
    b10 = evaluate(F_B, 8, 1.00)
    ok(abs(b16["cavity"] - 4.10) < 1e-9, f"③a 台架板 t=1.60 内腔 = {b16['cavity']:.2f} (判红)")
    ok(not b16["cavity_ok"], "③b t=1.60 内腔判定 = ❌")
    ok(abs(b10["cavity"] - 4.70) < 1e-9, f"③c 台架板 t=1.00 内腔 = {b10['cavity']:.2f}")
    ok(b10["cavity_ok"], "③d t=1.00 内腔判定 = ✅ (❌ → ✅ 翻转)")
    ok(any("盖板内腔" in s for s in b16["red_reasons"]) and
       not any("盖板内腔" in s for s in b10["red_reasons"]),
       "③e 判红原因里的内腔条目随板厚消失")
    print(f"      ★注: 台架板 t=1.00 的【整档】仍判红 (V 链 {b10['v_margin']:+.2f} / L 链 {b10['l_margin']:+.2f} "
          f"是板长板宽带来的, 换板厚救不了) ⇒ 这是本表最重要的一条结论之一")

    # ---------------- ④ V 链对板宽敏感 (改 pcb_w ⇒ 必须判红) ----------------
    print("\n>>> ④ 把 F30A 的板宽从 30 改到 100 ⇒ V 链必须判红")
    v_bad = evaluate(F_A, 6, 1.00, pcb_w=100.00)
    ok(abs(v_bad["v_need"] - 106.00) < 1e-9, f"④a V 需求 = {v_bad['v_need']:.2f} (100 + 6)")
    ok(abs(v_bad["v_margin"] + 68.00) < 1e-9, f"④b V 余 = {v_bad['v_margin']:+.2f} (台架板口径)")
    ok(not v_bad["v_ok"] and not v_bad["can_open"], "④c V 链判红 ⇒ 整档判红")
    ok(any("V 链" in s for s in v_bad["red_reasons"]), "④d 判红原因点名 V 链")

    # ---------------- ⑤ L 链对板长敏感 (改 pcb_l ⇒ 必须判红) ----------------
    print("\n>>> ⑤ 把 F30A 的板长从 60 改到 160 ⇒ L 链必须判红")
    l_bad = evaluate(F_A, 6, 1.00, pcb_l=160.00)
    ok(abs(l_bad["l_need"] - 215.50) < 1e-9, f"⑤a L 需求 = {l_bad['l_need']:.2f}")
    ok(abs(l_bad["l_margin"] + 85.50) < 1e-9, f"⑤b L 余 = {l_bad['l_margin']:+.2f}")
    ok(not l_bad["l_ok"] and not l_bad["can_open"], "⑤c L 链判红 ⇒ 整档判红")

    # ---------------- ⑥ 4.50 阈值的 0.01 分辨率 (t=1.22 ⇒ 内腔 4.48 < 4.50) ----------------
    print("\n>>> ⑥ t=1.22 ⇒ 内腔 4.48 (离 4.50 只差 0.02) ⇒ 必须判红 (证明 4.50 阈值真被用到 0.01 级)")
    r122 = evaluate(F_A, 6, 1.22)
    ok(abs(r122["cavity"] - 4.48) < 1e-9, f"⑥a F30A t=1.22 内腔 = {r122['cavity']:.2f}")
    ok(not r122["cavity_ok"] and not r122["can_open"], "⑥b 内腔判红 ⇒ 整档判红")

    # ---------------- ⑦ 板重随参数变 (不是常量) ----------------
    print("\n>>> ⑦ 板重必须随 (板框, 板厚) 变 (改参数 ⇒ 重量必须跟着变)")
    w08 = board_weight_g(60.0, 30.0, 0.80)
    w10 = board_weight_g(60.0, 30.0, 1.00)
    w22 = board_weight_g(60.0, 30.0, 1.22)
    w16 = board_weight_g(60.0, 30.0, 1.60)
    wb = board_weight_g(160.0, 100.0, 1.60)
    ok(abs(w10 - 3.33) < 0.005, f"⑦a 60×30×1.00 = {w10:.3f}g (MECH/BOARD_GEOM_30MM.md §1 = 3.33g)")
    ok(abs(board_weight_g(60.0, 15.0, 1.00) - 1.665) < 0.005,
       f"⑦b 60×15×1.00 = {board_weight_g(60.0, 15.0, 1.00):.3f}g (MECH/DEBUG_PORT_LAYOUT_CONSTRAINTS.md 表 2 = 1.67g)")
    ok(len({round(x, 4) for x in (w08, w10, w22, w16)}) == 4, "⑦c 四档板厚 ⇒ 四个不同板重")
    ok(abs(wb - 47.36) < 0.005, f"⑦d 台架板 160×100×1.60 = {wb:.3f}g")

    print()
    print("=" * 108)
    if errs:
        print("[反向用例] ❌ 不一致 (⇒ rc=2):")
        for e in errs:
            print(f"   ❌ {e}")
    else:
        print("[反向用例] ✅ 一致 —— ① 内腔改 4.00 ⇒ 判红 · ② 孔位搬到 15mm 板 ⇒ 不成立 · "
              "③ 板厚 1.60→1.00 ⇒ 内腔 4.10→4.70 且 ❌→✅ · ④ V 链对板宽敏感 · "
              "⑤ L 链对板长敏感 · ⑥ 4.50 阈值 0.01 分辨率 (t=1.22 ⇒ 4.48 判红) · ⑦ 板重随参数变")
        print("[反向用例] ★⇒ 没有任何一档是「改了参数还判绿」的假闸★")
    print("=" * 108)
    return 0 if not errs else 2


# ==================================================================================================
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", "--self-test", dest="selftest", action="store_true",
                    help="反向用例 (7 条) ⇒ rc=0")
    ap.add_argument("--json", dest="as_json", action="store_true", help="机器可读")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    rows = all_rows()
    if args.as_json:
        print(json.dumps({"sources": SOURCES, "frames": FRAMES,
                          "thickness_tiers": THICKNESS_TIERS, "layer_tiers": LAYER_TIERS,
                          "rows": rows}, ensure_ascii=False, indent=2, default=str))
        return 0

    edge = read_board_edge_cuts()
    print("=" * 108)
    print("BOARD-FRAME FEASIBILITY — ISS-310 板框口径代价对照 (MECH 侧) | mech-lead 2026-11-18")
    print("=" * 108)
    print(f"\n★盘上台架板只读实读 (HW/PCB/demo_mainboard.kicad_pcb): Edge.Cuts 中心线 "
          f"({edge.get('x0', 0):.2f},{edge.get('y0', 0):.2f})..({edge.get('x1', 0):.2f},{edge.get('y1', 0):.2f}) "
          f"⇒ {edge.get('w', 0):.2f} × {edge.get('h', 0):.2f}mm · general/thickness = {edge.get('thickness')} "
          f"[实测·板文件] ★本脚本只读, 一个字节没写★")
    print(f"★判据来源: 只读 import MECH/service_port_check.py ⇒ BASE/TOL/CRIT (CRIT = {CRIT:.2f}) 阈值零自造★")
    print("★口径: 全部几何读数 = 设计态几何 + 公差栈 ⇒ [推算]; 实物 [实测] = 0 条★")
    print()
    print_table0()
    print_table1(rows)
    print_table2(rows)
    print_table3(rows)
    print_table4(rows)
    print_table5(rows)
    print("★本脚本不拍板框 / 不拍层数 / 不拍板厚 —— 只出可行域表 + 判红原因 + 出处。")
    print("=" * 108)
    return 0


if __name__ == "__main__":
    sys.exit(main())
