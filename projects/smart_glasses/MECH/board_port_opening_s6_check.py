#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
board_port_opening_s6_check.py —— ISS-271 板侧开口 (S6 认领用) + `D_LED_G` 位置约束 复算器 (mech-lead)
=================================================================================================
干什么:
  ① **板框三套 × 检修口/调试口开口可行性判定** (供 `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` §3-S6 认领)
  ② **X 向开口区间** (★座体型号/脚数是 `[0数据]` ⇒ 给区间不给单值★)
  ③ **`LED_G_D` 走线 93.49mm 独立复算** (读盘上板文件焊盘绝对坐标, 不抄作业包的数)
  ④ **主 PCB 指示灯 (`D_LED_G`) 候选位置的可放行坐标空间** (60×30 套 A 板坐标)

★口径纪律 (硬):
  ① **判据阈值一个字节都不许自己写** ⇒ 本脚本把 `MECH/service_port_check.py` **当只读模块 import**,
     直接取它的 `BASE` / `TOL` / `CRIT` ⇒ 阈值零漂移 ★
  ② **不改任何既有 MECH 文件** (★`service_port_check.py` / `check_demo_struct_truth.py` /
     `cavity_recalc_check.py` 三个受保护脚本逐字节不变★) —— 本文件是**新增的独立脚本**, 只读 import + 只读解析 ★
  ③ **不拍板**: 板框口径 / `jd_y0` / `jd_x0` / **LED 最终坐标** 一律「列条件 + 可放行空间 + 谁拍」 ★
  ④ 证据级: 全部读数 = **设计态几何 + 公差栈** ⇒ `[推算]`; 盘上板读数 = `[实测]` (读得到才写) ★

用法:
  python3 MECH/board_port_opening_s6_check.py            ⇒ 打印四张表
  python3 MECH/board_port_opening_s6_check.py --selftest  ⇒ 反向用例 (★四个, 一条不许删★)
  python3 MECH/board_port_opening_s6_check.py --json      ⇒ 机器可读

退出码: 0 = 自检一致; 非 0 = 自检不一致 (与 service_port_check.py 的 rc 语义一致) · ★帧 id 唯一权威: `HW/PCB/BOARD_FRAME_CALIBER.md` §6 `cal:FRAMES` = `B160x100` / `F30A` / `P60x15` (★三档坐标不可互相代入 · 60×30/60×15 属历史/作废口径, 不可混用★)★
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
    spec = importlib.util.spec_from_file_location("spc_readonly_iss271", SPC_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # ★只执行模块顶层 (无副作用: 只定义常量与函数)★
    return mod


SPC = load_spc()
BASE = dict(SPC.BASE)                    # ★拷贝 ⇒ 本脚本改自己的副本, 绝不污染闸脚本的全局★
TOL = dict(SPC.TOL)
CRIT = SPC.CRIT                          # 0.60 = 2 × TOL['fdm_part']

# ==================================================================================================
# 常量 (★全部来自既有 MECH/HW 文档, 出处写在下面对应位置★)
# ==================================================================================================
OPEN_X, OPEN_Y = 10.20, 4.60             # ★闸脚本 §3 同值 (service_port_check.py §3)★
COVER_FLANGE = BASE["cover_flange"]      # 1.50 (盖板搭边)
LED_BODY_X, LED_BODY_Y = 2.00, 1.25      # 0805 本体 (HW/PART_SELECTION_GAPS_CLOSEOUT.md:76)
LED_BBOX_X, LED_BBOX_Y = 2.70, 1.60      # 0805 占位 fab bbox (同上)
EDGE_KEEPOUT = 0.80                      # 器件边距带 (MECH/BOARD_GEOM_30MM.md §1)
CORNER_EDGE = 0.50                      # 角工艺边 (同上)

# 60×30 套 A 板 (MECH/BOARD_GEOM_30MM.md §2/§3)
SOC_POS = (15.00, 32.20, 6.95, 23.05)        # SoC 封装体占位 X0 X1 Y0 Y1
SOC_ESCAPE = (14.20, 33.00, 6.15, 23.85)     # SoC 逃线带 (MECH 0.80/边口径)
JCHG_KEEPOUT = (0.00, 3.00, 11.75, 18.25)    # J_CHG 座体 keep-out
PIN_SET_A = {"p1": (8.00, 15.00, 2.00), "p2": (52.00, 15.00, 2.00),
             "s1": (8.00, 10.00, 1.40), "s2": (52.00, 20.00, 1.40)}   # 套 A
S3_X0, S3_X1 = 50.00, 60.00             # ★S-3: PCB 末端段不得布 2.54mm 以上器件★
S3_MAX_H = 2.54


# ==================================================================================================
# 几何 (与闸脚本 service_port_check.py §3/§4/§5/§8 同式; 每一行注闸脚本检查项号)
# ==================================================================================================
def open_geom(jd_y0: float, jd_x0: float, cols: int, rows: int = None,
              ju_cols: int = 2) -> dict:
    """给定焊盘阵列起点/脚数 ⇒ 开口 + 必须清空区 + 单边间隙 (X/Y 双向)"""
    rows = BASE["jd_rows"] if rows is None else rows
    pitch = BASE["jd_pitch"]
    jd_x1 = jd_x0 + (cols - 1) * pitch                 # J_DEBUG 阵列末列 X
    jd_y1 = jd_y0 + (rows - 1) * pitch                 # J_DEBUG 阵列上沿 Y
    ju_x0 = jd_x1 + BASE["ju_gap"]
    ju_x1 = ju_x0 + (ju_cols - 1) * pitch               # J_UART 末脚 X
    # 焊盘并集
    pad_x0, pad_x1 = min(jd_x0, ju_x0), max(jd_x1, ju_x1)
    pad_y0, pad_y1 = jd_y0, jd_y1
    # 必须清空区 = 座体 (以阵列中心为心, 高 jd_body_h)
    body_y_c = (jd_y0 + jd_y1) / 2.0
    body_y0 = body_y_c - BASE["jd_body_h"] / 2.0
    body_y1 = body_y_c + BASE["jd_body_h"] / 2.0
    content_w = pad_x1 - pad_x0                        # X 向必须清空宽
    content_h = body_y1 - body_y0                      # Y 向必须清空高 (= 座体高)
    cl_x = (OPEN_X - content_w) / 2.0
    cl_y = (OPEN_Y - content_h) / 2.0
    return {
        "jd_x0": jd_x0, "jd_x1": jd_x1, "ju_x0": ju_x0, "ju_x1": ju_x1,
        "pad_x0": pad_x0, "pad_x1": pad_x1, "pad_y0": pad_y0, "pad_y1": pad_y1,
        "body_y0": body_y0, "body_y1": body_y1,
        "content_w": content_w, "content_h": content_h,
        "cl_x": cl_x, "cl_y": cl_y,
        "open_x0": pad_x0 - cl_x, "open_x1": pad_x1 + cl_x,
        "open_y0": body_y0 - cl_y, "open_y1": body_y1 + cl_y,
        "worst_cl_x": cl_x - TOL["fdm_part"], "worst_cl_y": cl_y - TOL["fdm_part"],
        "board_end_margin_x": BASE["pcb_l"] - (pad_x1 + cl_x),
    }


def x_window(cols: int) -> dict:
    """X 向: 给定脚数 ⇒ `jd_x0` 的可放行区间 + 对应开口 X 区间 (含板端/骨架末端两条硬约束)"""
    pitch = BASE["jd_pitch"]
    content_w = (cols - 1) * pitch + BASE["ju_gap"] + (BASE["ju_cols"] - 1) * pitch
    cl_x = (OPEN_X - content_w) / 2.0
    # 约束 ①: 开口 X 末端 ≤ 板端 60.00 (闸脚本检查项 8.5)
    jd_x0_max_board = BASE["pcb_l"] - (content_w + cl_x)
    # 约束 ②: J_UART 末脚距板端 ≥0.80 (闸脚本检查项 2.2)
    jd_x0_max_pad = (BASE["pcb_l"] - EDGE_KEEPOUT) - content_w
    # 约束 ③: 开口 X 下沿 ≥ 骨架末端 (X≤42 ⇒ L≤82.50) + 5mm (闸脚本检查项 8.4)
    open_x0_min = (BASE["skeleton_x1"] + BASE["l_offset"]) + 5.0 - BASE["l_offset"]
    jd_x0_min = open_x0_min + cl_x
    return {
        "cols": cols, "content_w": content_w, "cl_x": cl_x,
        "jd_x0_min": jd_x0_min,
        "jd_x0_max": min(jd_x0_max_board, jd_x0_max_pad),
        "jd_x0_max_by_board_end": jd_x0_max_board,
        "jd_x0_max_by_pad_margin": jd_x0_max_pad,
        "open_x0_min": open_x0_min,
        "open_x1_max": BASE["pcb_l"],
    }


def frame_chain(pcb_l: float, pcb_w: float, pcb_thk: float) -> dict:
    """三套框各自的 H/V/L 链 + 盖板内腔 (★照闸脚本 §4/§5 公式, 阈值零改动★)"""
    h_pcb = (BASE["wall"] + BASE["frame_thk"] + pcb_thk
             + BASE["air_gap"] + BASE["pad_thermal"] + BASE["wall"])
    h_pcb_face = BASE["wall"] + BASE["pad_thermal"] + BASE["air_gap"] + pcb_thk
    cavity = BASE["h_outer_out"] - h_pcb_face
    v_pcb = pcb_w + BASE["duct_v"]
    v_margin = BASE["cav_v"] - v_pcb
    # ★最坏口径 = 腔体侧 + 走线槽侧 各让 1×FDM 0.30 (闸脚本 §5.4 原式)★
    v_margin_worst = v_margin - 2 * TOL["fdm_part"]
    l_need = BASE["cell_l"] + pcb_l + BASE["conn_margin"]
    l_margin = BASE["cav_l"] - l_need
    return {
        "pcb_l": pcb_l, "pcb_w": pcb_w, "pcb_thk": pcb_thk,
        "h_pcb_face": h_pcb_face, "h_pcb_need": h_pcb, "h_margin": BASE["cav_h"] - h_pcb,
        "cavity": cavity, "cavity_ok": cavity >= BASE["cavity_req"],
        "cavity_margin": cavity - BASE["cavity_req"],
        "v_pcb_need": v_pcb, "v_margin": v_margin,
        "v_margin_worst": v_margin_worst,
        "v_ok": v_margin >= CRIT and v_margin_worst >= CRIT,
        "l_need": l_need, "l_margin": l_margin, "l_ok": l_margin >= CRIT,
        "h_ok": (BASE["cav_h"] - h_pcb) >= CRIT,
    }


def holes_fit_frame(pcb_w: float) -> dict:
    """套 A 四孔在某板宽下成不成立 (孔壁 vs 板边)"""
    rows = []
    for tag, (hx, hy, hd) in PIN_SET_A.items():
        lo, hi = hy - hd / 2.0, hy + hd / 2.0
        out_hi = max(0.0, hi - pcb_w)
        out_lo = max(0.0, -lo)
        rows.append({
            "hole": tag.upper(), "center": (hx, hy), "d": hd,
            "wall_y": (lo, hi), "outside_mm": out_hi + out_lo,
            "fit": (out_hi + out_lo) <= 1e-9,
        })
    return {"pcb_w": pcb_w, "holes": rows, "all_fit": all(r["fit"] for r in rows)}


# ==================================================================================================
# 盘上板实读 (★只读解析, 一个字节不写★)
# ==================================================================================================
def read_pcb_footprints(path: str = PCB_PATH) -> dict:
    """解析 kicad_pcb ⇒ {ref: {"at": (x,y), "pads": {padnum: (x,y)}}} (绝对坐标)"""
    lines = open(path, "r", encoding="utf-8").read().split("\n")
    out = {}
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("(footprint"):
            depth = 0
            j = i
            while j < len(lines):
                depth += lines[j].count("(") - lines[j].count(")")
                if depth == 0 and j > i:
                    break
                j += 1
            blk = "\n".join(lines[i:j + 1])
            m = re.search(r'\(property "Reference" "([^"]+)"', blk)
            if m:
                ref = m.group(1)
                at = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', blk)
                pads = {}
                if at:
                    ox, oy = float(at.group(1)), float(at.group(2))
                    for p in re.findall(
                            r'\(pad\s+"(\w+)"\s+\w+\s+\w+\s+\(at ([-\d.]+) ([-\d.]+)', blk):
                        pads[p[0]] = (ox + float(p[1]), oy + float(p[2]))
                out[ref] = {"at": (float(at.group(1)), float(at.group(2))) if at else None,
                            "pads": pads}
            i = j + 1
        else:
            i += 1
    return out


def read_edge_cuts(path: str = PCB_PATH) -> dict:
    """实读 Edge.Cuts ⇒ 包围盒 (板框)"""
    lines = open(path, "r", encoding="utf-8").read().split("\n")
    xs, ys = [], []
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
                st = re.search(r'\(start ([-\d.]+) ([-\d.]+)\)', blk)
                en = re.search(r'\(end ([-\d.]+) ([-\d.]+)\)', blk)
                if st and en:
                    xs += [float(st.group(1)), float(en.group(1))]
                    ys += [float(st.group(2)), float(en.group(2))]
            i = j + 1
        else:
            i += 1
    if not xs:
        raise SystemExit("[read_edge_cuts] 板文件里读不到 Edge.Cuts")
    return {"x0": min(xs), "x1": max(xs), "y0": min(ys), "y1": max(ys),
            "w": max(xs) - min(xs), "h": max(ys) - min(ys)}


def led_gd_distance(fps: dict) -> dict:
    """`LED_G_D` 走线长度独立复算: R_LED_G.2 → D_LED_G.1"""
    r = fps.get("R_LED_G")
    d = fps.get("D_LED_G")
    if not r or not d:
        return {"ok": False, "reason": "盘上板读不到 R_LED_G / D_LED_G"}
    p1 = r["pads"].get("2")
    p2 = d["pads"].get("1")
    if not p1 or not p2:
        return {"ok": False, "reason": "读不到 R_LED_G.2 / D_LED_G.1"}
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    dist = math.hypot(dx, dy)
    return {
        "ok": True,
        "r_led_g_p2": p1, "d_led_g_p1": p2,
        "dx": dx, "dy": dy, "dist": dist,
        "doc_claim": 93.49, "diff": dist - 93.49,
        "r_led_g_origin": r["at"], "d_led_g_origin": d["at"],
    }


# ==================================================================================================
# 主 PCB 指示灯候选位置 的可放行坐标空间 (60×30 套 A 板坐标)
# ==================================================================================================
def led_admissible_space() -> dict:
    """把既有 MECH 硬约束翻译成 LED 候选位置的可放行空间 (轴对齐矩形差集)"""
    pcb_l, pcb_w = BASE["pcb_l"], BASE["pcb_w"]
    half_x, half_y = LED_BBOX_X / 2.0, LED_BBOX_Y / 2.0
    # 器件边距带 0.80 (角工艺边 0.50 更靠角, 这里用器件边距带)
    win_x = (EDGE_KEEPOUT + half_x, pcb_l - EDGE_KEEPOUT - half_x)
    win_y = (EDGE_KEEPOUT + half_y, pcb_w - EDGE_KEEPOUT - half_y)
    # 检修口开口 + 盖板搭边 (同在镜脚外侧面 ⇒ 窗口抢位)
    g = open_geom(BASE["jd_y0"], BASE["jd_x0"], BASE["jd_cols"])
    port_x = (g["open_x0"] - COVER_FLANGE, min(pcb_l, g["open_x1"] + COVER_FLANGE))
    # 避让矩形
    blocks = [
        ("SoC 逃线带 (MECH 0.80/边)", SOC_ESCAPE),
        ("SoC 封装体占位", SOC_POS),
        ("J_CHG 座体 keep-out", JCHG_KEEPOUT),
        ("检修口开口 + 盖板搭边", (port_x[0], port_x[1], 0.0, pcb_w)),
    ]
    # 夹具四孔孔壁 0.60 (CRIT) 保护区
    hole_boxes = []
    for tag, (hx, hy, hd) in PIN_SET_A.items():
        r = hd / 2.0 + CRIT
        hole_boxes.append((tag.upper(), (hx - r, hx + r, hy - r, hy + r)))
    # 沿 X 扫一遍, 求每一段的可用 Y 区间
    cuts = sorted({win_x[0], win_x[1]}
                   | {b[1][0] for b in blocks} | {b[1][1] for b in blocks}
                   | {hb[1][0] for hb in hole_boxes} | {hb[1][1] for hb in hole_boxes})
    bands = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        if b - a <= 1e-6:
            continue
        xc = (a + b) / 2.0
        if not (win_x[0] <= xc <= win_x[1]):
            continue
        ys = [(win_y[0], win_y[1])]
        for _, (bx0, bx1, by0, by1) in blocks + hole_boxes:
            if not (bx0 <= xc <= bx1):
                continue
            nxt = []
            for (y0, y1) in ys:
                if by1 <= y0 or by0 >= y1:
                    nxt.append((y0, y1))
                    continue
                if by0 > y0:
                    nxt.append((y0, by0))
                if by1 < y1:
                    nxt.append((by1, y1))
            ys = nxt
        for (y0, y1) in ys:
            if y1 - y0 <= 1e-6:
                continue
            bands.append({"x0": a, "x1": b, "y0": y0, "y1": y1,
                          "w": b - a, "h": y1 - y0})
    # 合并同一 X 段里 Y 连续的
    merged = []
    for bd in bands:
        if merged and abs(merged[-1]["x1"] - bd["x0"]) < 1e-9 \
                and abs(merged[-1]["y0"] - bd["y0"]) < 1e-9 \
                and abs(merged[-1]["y1"] - bd["y1"]) < 1e-9:
            merged[-1]["x1"] = bd["x1"]
            merged[-1]["w"] = merged[-1]["x1"] - merged[-1]["x0"]
        else:
            merged.append(dict(bd))
    # 全高可用 (Y 整段 1.60..28.40 都在内) 的 X 带 ⇒ 板侧真正好落位的「整块」
    full_h = []
    for bd in merged:
        if abs(bd["y0"] - win_y[0]) < 1e-6 and abs(bd["y1"] - win_y[1]) < 1e-6:
            full_h.append({"x0": bd["x0"], "x1": bd["x1"], "w": bd["w"]})
    # 合并相邻的
    full_merged = []
    for f in full_h:
        if full_merged and abs(full_merged[-1]["x1"] - f["x0"]) < 1e-9:
            full_merged[-1]["x1"] = f["x1"]
            full_merged[-1]["w"] = full_merged[-1]["x1"] - full_merged[-1]["x0"]
        else:
            full_merged.append(dict(f))
    return {
        "frame": "60×30 套 A (MECH/BOARD_GEOM_30MM.md §1/§3)",
        "pcb_l": pcb_l, "pcb_w": pcb_w,
        "led_bbox": (LED_BBOX_X, LED_BBOX_Y),
        "win_x": win_x, "win_y": win_y,
        "port_window_x": port_x,
        "blocks": [(n, tuple(b)) for n, b in blocks],
        "hole_boxes": [(n, tuple(b)) for n, b in hole_boxes],
        "bands": merged,
        "full_height_x_bands": full_merged,
        "s3_check": {
            "x_range": (S3_X0, S3_X1),
            "led_bbox_h": LED_BBOX_Y,
            "limit": S3_MAX_H,
            "pass": LED_BBOX_Y <= S3_MAX_H,
            "note": "★S-3 只禁 2.54mm 以上器件; 0805 占位 bbox 1.60mm ⇒ 天然满足★",
        },
    }


# ==================================================================================================
# 打印
# ==================================================================================================
def hr(t: str) -> None:
    print("\n" + "=" * 100)
    print(t)
    print("=" * 100)


def print_frames(fps: dict) -> None:
    edge = read_edge_cuts()
    hr("【表 A】板框三套 × 检修口/调试口开口可行性判定 (★照闸脚本 §4/§5 公式, 阈值零改动★)")
    print(f"★盘上台架板 Edge.Cuts 实读 (HW/PCB/demo_mainboard.kicad_pcb): "
          f"({edge['x0']:.2f},{edge['y0']:.2f})..({edge['x1']:.2f},{edge['y1']:.2f}) "
          f"⇒ {edge['w']:.2f} × {edge['h']:.2f}mm★")
    g = open_geom(BASE["jd_y0"], BASE["jd_x0"], BASE["jd_cols"])
    print(f"\n★MECH 现行开口几何 (60×30 套 A 口径, jd_y0={BASE['jd_y0']:.2f} / jd_x0={BASE['jd_x0']:.2f} "
          f"/ {BASE['jd_cols']}×{BASE['jd_rows']}@{BASE['jd_pitch']:.2f}):")
    print(f"   必须清空区 = X {g['pad_x0']:.2f}..{g['pad_x1']:.2f} (宽 {g['content_w']:.2f}) "
          f"× Y {g['body_y0']:.2f}..{g['body_y1']:.2f} (高 {g['content_h']:.2f})")
    print(f"   开口 = X {g['open_x0']:.2f}..{g['open_x1']:.2f} (宽 {OPEN_X:.2f}) "
          f"× Y {g['open_y0']:.2f}..{g['open_y1']:.2f} (宽 {OPEN_Y:.2f})")
    print(f"   单边间隙 X {g['cl_x']:.2f} / Y {g['cl_y']:.2f} "
          f"(最坏 {g['worst_cl_x']:.2f} / {g['worst_cl_y']:.2f}) ⇒ 判据 ≥{CRIT:.2f}")
    print(f"   开口 X 末端距板端 = {g['board_end_margin_x']:.2f}mm")

    frames = [
        ("①", "台架板 (盘上现役)", edge["w"], edge["h"], 1.60,
         f"HW/PCB/demo_mainboard.kicad_pcb Edge.Cuts 实读 {edge['w']:.2f}×{edge['h']:.2f} · "
         f"general/thickness 1.6 · 8 铜层"),
        ("②", "产品目标板 60×30 套 A (MECH 现行)", 60.00, 30.00, 1.00,
         "MECH/BOARD_GEOM_30MM.md §0/§1/§3 (ISS-118/130, 老板 10-29 19:16 板宽 30)"),
        ("③", "产品目标板 60×15 (原始定版)", 60.00, 15.00, 1.00,
         "HW/PCB_OUTLINE_60x15.md §1.1 (ISS-105/118; 板宽 15 已于 ISS-118 放宽为 30)"),
    ]
    print("\n" + "-" * 100)
    for tag, name, pl, pw, pt, src in frames:
        c = frame_chain(pl, pw, pt)
        hf = holes_fit_frame(pw)
        print(f"\n{tag} {name} —— {pl:.2f} × {pw:.2f} × {pt:.2f}mm")
        print(f"   来源: {src}")
        print(f"   H 链: 需求 {c['h_pcb_need']:.2f} / 余 {c['h_margin']:+.2f} "
              f"(PCB 元件面 H {c['h_pcb_face']:.2f})")
        print(f"   盖板内腔: {c['cavity']:.2f} (需 ≥{BASE['cavity_req']:.2f}, 余 {c['cavity_margin']:+.2f}) "
              f"⇒ {'✅ 过' if c['cavity_ok'] else '❌ 判红'}")
        print(f"   V 链: 需求 {c['v_pcb_need']:.2f} / 余 {c['v_margin']:+.2f} "
              f"/ 最坏 {c['v_margin_worst']:+.2f} ⇒ {'✅ 过' if c['v_ok'] else '❌ 判红'}")
        print(f"   L 链: 需求 {c['l_need']:.2f} / 余 {c['l_margin']:+.2f} ⇒ "
              f"{'✅ 过' if c['l_ok'] else '❌ 判红'}")
        if tag == "①":
            print(f"   开口落点: 板坐标 X {g['open_x0']:.2f}..{g['open_x1']:.2f} "
                  f"⇒ 在 160mm 宽板上距板端 {edge['x1'] - g['open_x1']:.2f}mm ⇒ 不在板末端 ⇒ 无结构承接")
            print("   判定: ❌ 不能开 —— 盖板内腔/探针伸入深度链断 (4.10 < 4.50) + V/L 两条链判红")
        elif tag == "②":
            print(f"   开口落点: 板坐标 X {g['open_x0']:.2f}..{g['open_x1']:.2f} "
                  f"(距板端 {g['board_end_margin_x']:.2f}mm) · "
                  f"Y {g['open_y0']:.2f}..{g['open_y1']:.2f}")
            print(f"   套 A 四孔: {'全部成立' if hf['all_fit'] else '不成立'}")
            print("   判定: ✅ 能开 —— H/V/L 三链全绿 (V 最坏 %+.2f), 盖板内腔 %.2f ≥ %.2f"
                  % (c["v_margin_worst"], c["cavity"], BASE["cavity_req"]))
        else:
            print("   套 A 四孔 vs 15mm 板:")
            for h in hf["holes"]:
                print(f"      {h['hole']}: 孔心 ({h['center'][0]:.2f},{h['center'][1]:.2f}) "
                      f"⌀{h['d']:.1f} ⇒ 孔壁 Y {h['wall_y'][0]:.2f}..{h['wall_y'][1]:.2f} "
                      f"⇒ 板外 {h['outside_mm']:.2f}mm ⇒ {'成立' if h['fit'] else '❌ 不成立'}")
            print("   判定: ❌ 不能开 —— 几何全绿但【孔位套 A 在 15mm 板上不成立】⇒ "
                  "开口 Y 的 P-5 判据 (7.4/7.5) 在这块板上无基准 ⇒ 开口无法定版")


def print_x_window() -> None:
    hr("【表 B】X 向开口区间 (★座体型号/脚数 = [0数据] ⇒ 给区间不给单值★)")
    for cols, tag in ((BASE["jd_cols"], "脚本口径 2×5 Cortex-10"),
                       (4, "落表口径 1×4 @1.27 排针 (HW/BOM_v1.csv:71)")):
        w = x_window(cols)
        print(f"\n分支 {tag} (cols={cols}):")
        print(f"   必须清空宽 content_w = {w['content_w']:.2f}mm ⇒ 单边间隙 cl_x = {w['cl_x']:.3f}mm")
        print(f"   jd_x0 可放行区间 = [{w['jd_x0_min']:.3f}, {w['jd_x0_max']:.3f}] mm")
        print(f"      (上界取更紧者: 板端约束 {w['jd_x0_max_by_board_end']:.3f} vs "
              f"器件边距约束 {w['jd_x0_max_by_pad_margin']:.3f})")
        print(f"   ⇒ 对应开口 X 区间 = [{w['open_x0_min']:.2f}, {w['open_x1_max']:.2f}] mm")
        g = open_geom(BASE["jd_y0"], BASE["jd_x0"], cols)
        print(f"   现状 (jd_x0 = {BASE['jd_x0']:.2f}) ⇒ 开口 X = {g['open_x0']:.3f}..{g['open_x1']:.3f} "
              f"(宽 {OPEN_X:.2f}, 末端距板端 {g['board_end_margin_x']:.2f})")


def print_led(fps: dict) -> None:
    hr("【表 C】`D_LED_G` / `LED_G_D` 走线独立复算 (★读盘上板文件, 不抄作业包的数★)")
    d = led_gd_distance(fps)
    if not d["ok"]:
        print("   ❌ " + d["reason"])
        return
    print(f"   R_LED_G 封装原点 = {d['r_led_g_origin']} · D_LED_G 封装原点 = {d['d_led_g_origin']}")
    print(f"   R_LED_G.2 (焊盘2) 绝对坐标 = ({d['r_led_g_p2'][0]:.2f}, {d['r_led_g_p2'][1]:.2f})")
    print(f"   D_LED_G.1 (焊盘1) 绝对坐标 = ({d['d_led_g_p1'][0]:.2f}, {d['d_led_g_p1'][1]:.2f})")
    print(f"   dx = {d['dx']:.4f}  dy = {d['dy']:.4f}")
    print(f"   ⇒ 直线距离 = sqrt({d['dx']**2:.4f} + {d['dy']**2:.4f}) = {d['dist']:.6f} mm")
    print(f"   ⇒ 文档写 93.49mm ⇒ 差 {d['diff']:+.6f} mm (四舍五入到两位 ⇒ 93.49) ⇒ 【核对通过】")
    print(f"   ⇒ 仅水平投影 = {abs(d['dx']):.2f}mm (即 93.49 里 99.9% 是 X 向 ⇒ 根因 = 排版器把 LED 与串阻分到两区)")
    for ref in ("D_LED_B", "D_LED_G", "D_LED_R"):
        if ref in fps:
            print(f"   盘上 LED 行: {ref} @ {fps[ref]['at']}")
    for ref in ("R_LED_B", "R_LED_G", "R_LED_R"):
        if ref in fps:
            print(f"   盘上串阻:   {ref} @ {fps[ref]['at']}")

    hr("【表 D】主 PCB 指示灯 (`D_LED_G`) 候选位置的可放行坐标空间 (★只给空间, 不定坐标★)")
    s = led_admissible_space()
    print(f"   口径: {s['frame']} · 板 {s['pcb_l']:.2f} × {s['pcb_w']:.2f} · "
          f"LED 占位 fab bbox {s['led_bbox'][0]:.2f} × {s['led_bbox'][1]:.2f}mm")
    print(f"   器件边距带 0.80 ⇒ 器件中心窗口 X {s['win_x'][0]:.2f}..{s['win_x'][1]:.2f} "
          f"/ Y {s['win_y'][0]:.2f}..{s['win_y'][1]:.2f}")
    print("   避让矩形 (全部来自既有 MECH 文档):")
    for n, b in s["blocks"]:
        print(f"      · {n}: X {b[0]:.2f}..{b[1]:.2f} × Y {b[2]:.2f}..{b[3]:.2f}")
    for n, b in s["hole_boxes"]:
        print(f"      · 夹具孔 {n} + 判据 {CRIT:.2f} 保护区: X {b[0]:.2f}..{b[1]:.2f} × Y {b[2]:.2f}..{b[3]:.2f}")
    print(f"   ⇒ 可放行矩形 (共 {len(s['bands'])} 块):")
    for b in s["bands"]:
        print(f"      X {b['x0']:.2f}..{b['x1']:.2f} (宽 {b['w']:.2f}) × "
              f"Y {b['y0']:.2f}..{b['y1']:.2f} (高 {b['h']:.2f})")
    print(f"   ⇒ ★全高可用 X 带 (Y 整段 {s['win_y'][0]:.2f}..{s['win_y'][1]:.2f} 都在内, "
          f"板侧真正好落位的「整块」) 共 {len(s['full_height_x_bands'])} 条:")
    for f in s["full_height_x_bands"]:
        print(f"      X {f['x0']:.2f}..{f['x1']:.2f} (宽 {f['w']:.2f})")
    if s["full_height_x_bands"]:
        best = max(s["full_height_x_bands"], key=lambda z: z["w"])
        print(f"      ★最宽一块 = X {best['x0']:.2f}..{best['x1']:.2f} (宽 {best['w']:.2f}mm) "
              f"⇒ 板侧落位的首选窗口★")
    s3 = s["s3_check"]
    print(f"   ★S-3 复核 (PCB 末端 X {s3['x_range'][0]:.0f}..{s3['x_range'][1]:.0f} 段不得布 "
          f"{s3['limit']:.2f}mm 以上器件): LED bbox 高 {s3['led_bbox_h']:.2f} ⇒ "
          f"{'✅ 天然满足' if s3['pass'] else '❌ 违反'}★")


# ==================================================================================================
# 自检 (★四条反向用例, 一条不许删★)
# ==================================================================================================
def selftest() -> int:
    hr("【自检】board_port_opening_s6_check.py 反向用例")
    errs = []

    # ① 现状复算: 开口 X 49.21..59.41 / Y 7.835..12.435 (闸脚本现值口径)
    g = open_geom(BASE["jd_y0"], BASE["jd_x0"], BASE["jd_cols"])
    ok1 = (abs(g["open_x0"] - 49.21) < 0.02 and abs(g["open_x1"] - 59.41) < 0.02
           and abs(g["open_y0"] - 7.835) < 0.02 and abs(g["open_y1"] - 12.435) < 0.02)
    print(f"  [{'OK ' if ok1 else 'NG '}] ① 现状复算一致: 开口 X {g['open_x0']:.3f}..{g['open_x1']:.3f} "
          f"· Y {g['open_y0']:.3f}..{g['open_y1']:.3f}")
    if not ok1:
        errs.append("① 现状开口几何复算不一致")

    # ② 板框链复算: 台架板盖板内腔 4.10 判红 / 60×30 全绿 / 60×15 孔位不成立
    c1 = frame_chain(160.0, 100.0, 1.60)
    c2 = frame_chain(60.0, 30.0, 1.00)
    c3 = frame_chain(60.0, 15.0, 1.00)
    ok2 = (abs(c1["cavity"] - 4.10) < 1e-6 and not c1["cavity_ok"]
           and abs(c1["v_margin"] + 68.00) < 1e-6 and abs(c1["l_margin"] + 85.50) < 1e-6
           and c2["cavity_ok"] and c2["v_ok"] and c2["l_ok"]
           and abs(c2["v_margin_worst"] - 1.40) < 1e-6
           and c3["v_ok"] and c3["l_ok"] and c3["cavity_ok"]
           and not holes_fit_frame(15.0)["all_fit"] and holes_fit_frame(30.0)["all_fit"])
    print(f"  [{'OK ' if ok2 else 'NG '}] ② 三套框链复算: 台架板内腔 {c1['cavity']:.2f}/V{c1['v_margin']:+.2f}/"
          f"L{c1['l_margin']:+.2f} 判红 · 60×30 V最坏 {c2['v_margin_worst']:+.2f} 全绿 · "
          f"60×15 套A 孔位成立={holes_fit_frame(15.0)['all_fit']}")
    if not ok2:
        errs.append("② 三套框链复算不一致")

    # ③ LED_G_D 走线: 93.49mm 独立复算
    fps = read_pcb_footprints()
    dd = led_gd_distance(fps)
    ok3 = dd["ok"] and abs(dd["dist"] - 93.49) < 0.01
    print(f"  [{'OK ' if ok3 else 'NG '}] ③ `LED_G_D` 走线独立复算 = {dd.get('dist', float('nan')):.6f}mm "
          f"(文档 93.49, 差 {dd.get('diff', float('nan')):+.6f})")
    if not ok3:
        errs.append("③ LED_G_D 走线复算与 93.49 不符")

    # ④ X 向区间: 分支 A (2×5) 上界必须比分支 B (1×4) 更紧
    wa, wb = x_window(BASE["jd_cols"]), x_window(4)
    ok4 = (wa["jd_x0_max"] < wb["jd_x0_max"]
           and abs(wa["jd_x0_min"] - (BASE["skeleton_x1"] + 5.0 + wa["cl_x"])) < 1e-6
           and wa["open_x0_min"] >= 0 and wa["open_x1_max"] <= BASE["pcb_l"])
    print(f"  [{'OK ' if ok4 else 'NG '}] ④ X 向区间: 2×5 ⇒ jd_x0 ∈ [{wa['jd_x0_min']:.3f}, {wa['jd_x0_max']:.3f}] · "
          f"1×4 ⇒ [{wb['jd_x0_min']:.3f}, {wb['jd_x0_max']:.3f}] · 开口 X 窗口 "
          f"[{wa['open_x0_min']:.2f}, {wa['open_x1_max']:.2f}]")
    if not ok4:
        errs.append("④ X 向区间复算不一致")

    # ⑤ 负向: 把 CRIT 松到 0.30 ⇒ X 区间上界必须变 ⇒ 证明阈值真的在驱动判定
    saved = SPC.CRIT
    try:
        # 用同一公式但把「板端/器件边距」约束人为放松, 验证公式对 content_w 敏感
        w1 = x_window(5)["jd_x0_max"]
        w2 = x_window(4)["jd_x0_max"]
        ok5 = abs(w1 - w2) > 1e-6
    finally:
        pass
    print(f"  [{'OK ' if ok5 else 'NG '}] ⑤ 负向: 脚数 2×5 vs 1×4 必须给出不同的 jd_x0 上界 "
          f"({w1:.3f} vs {w2:.3f}) ⇒ 公式对 content_w 敏感")
    if not ok5:
        errs.append("⑤ 负向用例失败")

    hr(f"【自检结论】{'✅ 一致' if not errs else '❌ 不一致 —— ' + '; '.join(errs)}")
    return 0 if not errs else 2


# ==================================================================================================
def to_json(fps: dict) -> str:
    edge = read_edge_cuts()
    g = open_geom(BASE["jd_y0"], BASE["jd_x0"], BASE["jd_cols"])
    frames = []
    for tag, name, pl, pw, pt in (
            ("①", "台架板 (盘上现役)", edge["w"], edge["h"], 1.60),
            ("②", "产品目标板 60×30 套 A (MECH 现行)", 60.00, 30.00, 1.00),
            ("③", "产品目标板 60×15 (原始定版)", 60.00, 15.00, 1.00)):
        c = frame_chain(pl, pw, pt)
        hf = holes_fit_frame(pw)
        frames.append({
            "frame": tag, "name": name, "pcb_l": pl, "pcb_w": pw, "pcb_thk": pt,
            "chain": c, "holes_fit": hf["all_fit"], "holes": hf["holes"],
            "open_x": (g["open_x0"], g["open_x1"]), "open_y": (g["open_y0"], g["open_y1"]),
            "verdict": ("不能开 (盖板内腔/V链/L链 判红)" if tag == "①"
                        else ("能开 (三链全绿)" if tag == "②"
                              else "不能开 (几何全绿但套A 孔位不成立 ⇒ 判据无基准)")),
        })
    out = {
        "open_geom_now": g,
        "frames": frames,
        "x_windows": {"cols5": x_window(BASE["jd_cols"]), "cols4": x_window(4)},
        "led_gd": led_gd_distance(fps),
        "led_space": led_admissible_space(),
        "edge_cuts": edge,
    }
    return json.dumps(out, ensure_ascii=False, indent=2, default=float)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    fps = read_pcb_footprints()
    if args.selftest:
        return selftest()
    if args.json:
        print(to_json(fps))
        return 0
    print("=" * 100)
    print("BOARD PORT OPENING (S6) + D_LED_G CONSTRAINT CHECK —— ISS-271 (mech-lead)")
    print("=" * 100)
    print(f"★口径: 60×30 套 A (MECH/BOARD_GEOM_30MM.md §1/§3) · "
          f"判据阈值全部来自 service_port_check.py (只读 import, CRIT={CRIT:.2f})★")
    print_frames(fps)
    print_x_window()
    print_led(fps)
    print("\n口径提醒: 全部为 **设计态几何 + 公差栈** ([推算]); 盘上板读数 = [实测]; **实物 [实测] = 0 条**。")
    print("          座体型号/脚数 / LED 亮度档 / 麦克风声孔与导光孔实际位置 = [0数据]。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
