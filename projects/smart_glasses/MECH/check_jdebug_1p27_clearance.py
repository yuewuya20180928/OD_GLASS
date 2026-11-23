#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/check_jdebug_1p27_clearance.py —— `J_DEBUG` 排针 land 改 1.27mm 后的结构侧净距真相 机器闸
===================================================================================================
★**性质**: 只读机器闸 · ★零写板 / 零落表 / 零改任何既有脚本 / 零外发 / 不代老板拍板** ★
★**派活**: 项目总工 (main / moli) · ISS-371 · 2026-11-23 · 交卷人 = 结构总工 (mech-lead) ★
★**续做**: cont1 (★上一趟 21:31:03 failed ⇒ 本趟从已落那页续做·闸/交卷页/分片上一趟全零★) ★
★**关联**: `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` (★真相页·上一趟已落·本闸只读它★) ·
          `HANDOFF/2026-11-23_mech-lead_ISS371_JDEBUG排针1.27净距真相.md` (交卷页) ·
          板侧项 = `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` (★ISS-343·本闸不重复发明板侧项编号★) ★

────────────────────────────────────────────────────────────────────────────────────────────────────────
【作用】★把「`J_DEBUG` 排针 land 从 pitch 0.50 改到 1.27」这条板侧已拍板的改动所引起的
  【结构侧净距真相】钉成机器闸 ⇒ 以后谁把 4.0850 / 3.0575 / 2.7575 这组【偏乐观 0.3625mm 的旧数】
  写回任何一页 (含机器块) ⇒ 本闸立刻红 ★

  ★**七条判据 (自证型·不许靠注释说绿)** ★:
    G1 官方 THT land 的焊盘几何必须与盘上 `.kicad_mod` 实读一致 (★自己解析·不许写死 4.8100★)
    G2 §1 那一页声明的三档【宽度】必须与 G1 实算逐项一致 (★宽度 = 铜箔宽 + 铜箔高★)
    G3 必须清空区宽 ≥ 铜箔 X 宽 (★不许越界★) + 越界事实必须被显式记账
    G4 单边间隙 X (左/右) 对称且 ≥ `CRIT` (★`CRIT` 从 `MECH/service_port_check.py` 取·不许写死★)
    G5 降级方案 (SMD 变体) 的几何必须也实测一遍并单列 (★不许拿 THT 的数套用★)
    G6 板面零写板自证 (md5 / mtime / size 三项)
    G7 证据等级五级白名单 + 正文零挂起措辞 + 「判据句 / 事实句」两句分开 + `.kicad_mod` md5 台账

────────────────────────────────────────────────────────────────────────────────────────────────────────
【★两条必须分开写的结论 (main 2026-11-23 22:0x 独立复核)★】★

  ★**判据句 (方向)**: 换官方 THT land 后, 调试口单边间隙 X = 2.6950 / 最坏 2.3950 ≥ `CRIT` 0.60
    ⇒ ★**方向仍过阈** (余量 3.99×) ★
  ★**事实句 (铜箔)**: 若结构件仍按现页 4.0850 留 ⇒ ★**最外侧焊盘每边超出清空区 0.3625mm**
    ⇒ ★**铜箔直接进清空区** ★
  ★**两句同时成立; 不许混成一句「OK / 合格」** ★ ⇒ G7 逐行扫描「合格」与「过 CRIT」同现 ⇒ 红 ★
  ★**⇒ 这一条必须并进「板只改一次」那一趟同批改, 不许只改 `J_DEBUG` 一个** ★

────────────────────────────────────────────────────────────────────────────────────────────────────────
【rc 语义】
  0 = 全部通过
  1 = 有断言不通过 (逐条列出 + 点名判据号)
  2 = 参数 / IO 错误

────────────────────────────────────────────────────────────────────────────────────────────────────────
【用法】
  python3 MECH/check_jdebug_1p27_clearance.py             # 扫真件 (只读)
  python3 MECH/check_jdebug_1p27_clearance.py --selftest  # 反向用例 (末行 ALL TESTS PASS)
  python3 MECH/check_jdebug_1p27_clearance.py --root DIR  # 扫指定树 (反向用例在 tmp/iss371/ 副本上做)

★**沙盒纪律**: 反向用例一律落项目盘 `<root>/tmp/iss371/selftest/` (★不许写系统 `/tmp` ——
  2026-11-23 04:4x 实测系统 `/tmp` 配额已满, 写 `/tmp` 会让闸拿到假读数★) ★
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

# --------------------------------------------------------------------------------------------------
# 常量 (★全部相对路径 + 只读来源★)
# --------------------------------------------------------------------------------------------------
PAGE_REL = "MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md"          # ★真相页 (上一趟已落)★
CROSS_REL = "MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md"              # ★开口 X 的权威来源 (只读)★
CRIT_REL = "MECH/service_port_check.py"                            # ★CRIT 真身 (只读)★
PCB_REL = "HW/PCB/demo_mainboard.kicad_pcb"                        # ★板 (只读·零写板)★

# ★旧数四处同源副本 (只读扫描·用来定位「谁还带着旧数」)★
STALE_DOCS = (
    "HW/PCB/BOARD_ONEPASS_WORKPACKET.md",
    "MECH/BOARD_ONEPASS_MECH_SYNC.md",
    "MECH/BOARD_ONEPASS_MECH_CLAIMS.md",
    "MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md",
)
STALE_NUMBERS = ("4.0850", "3.0575", "2.7575")

# ★KiCad 官方库根 (★与 `HW/check_fp_truth_baseline.py` / `HW/check_fp_truth_land_swap.py` 同一个★)★
LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
THT_LIBDIR = "Connector_PinHeader_1.27mm.pretty"
THT_MOD_NAME = "PinHeader_1x04_P1.27mm_Vertical.kicad_mod"
SMD_MOD_NAME = "PinHeader_1x04_P1.27mm_Vertical_SMD_Pin1Left.kicad_mod"

# ★板零写板基线 (★ISS-371 开工前 / 交卷后各打一次双证★)★
BOARD_BASELINE = {
    "md5": "611b869e13518c3c023fb178f91a0075",
    "mtime": "2026-11-06 07:07:17.362193413",
    "size": 4940213,
}

# ★证据等级五级白名单 (★照 `MECH/check_onepass_s10_led_spec_sync.py` 的现成判据形状★)★
EVIDENCE_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
FORBIDDEN_EVIDENCE = ("[官方]", "[推断]", "[推测]", "[估计]", "[大概]", "[可能]", "[大概值]")
# ★正文零挂起措辞 (★不许出现「等原厂回信」这种把活推出去的写法★)★
HEDGING_WORDS = ("可能", "大概", "应该是", "似乎", "貌似", "估摸", "八成", "多半")
FORBIDDEN_PHRASES = ("等原厂回信", "等原厂回复", "等待原厂", "回头再问原厂")

TOL = 1e-6          # ★数值比对容差 (mm)★


# ==================================================================================================
# 通用工具
# ==================================================================================================
def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def near(a: float, b: float, tol: float = TOL) -> bool:
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


BLOCK_RE = re.compile(
    r"<!--\s*MACHINE-BLOCK[A-Z-]*-BEGIN\s*-->\s*```json\s*(.*?)\s*```\s*"
    r"<!--\s*MACHINE-BLOCK[A-Z-]*-END\s*-->", re.S)


def parse_machine_blocks(text: str) -> list:
    out = []
    for m in BLOCK_RE.finditer(text):
        try:
            out.append(json.loads(m.group(1)))
        except Exception as exc:  # noqa: BLE001
            raise AssertionError("机器块 JSON 解析失败: %s" % exc)
    return out


# --------------------------------------------------------------------------------------------------
# 官方 `.kicad_mod` 只读解析
# --------------------------------------------------------------------------------------------------
PAD_RE = re.compile(
    r'\(pad\s+"([^"]*)"\s+(\S+)\s+(\S+)\s*\(at\s+([-\d.]+)\s+([-\d.]+)'
    r'(?:\s+[-\d.]+)?\)'
    r'(?:\s*\(size\s+([-\d.]+)\s+([-\d.]+)\))?'
    r'(?:\s*\(drill\s+([-\d.]+)\))?')
FP_RECT_RE = re.compile(
    r'\(fp_rect\s*\(start\s+([-\d.]+)\s+([-\d.]+)\)\s*\(end\s+([-\d.]+)\s+([-\d.]+)\)'
    r'(.*?)\(layer\s+"([^"]+)"\)', re.S)
FP_LINE_RE = re.compile(
    r'\(fp_line\s*\(start\s+([-\d.]+)\s+([-\d.]+)\)\s*\(end\s+([-\d.]+)\s+([-\d.]+)\)'
    r'(.*?)\(layer\s+"([^"]+)"\)', re.S)


def parse_mod(path: str) -> dict:
    text = read_text(path)
    pads = []
    for m in PAD_RE.finditer(text):
        num, ptype, shape, px, py, sx, sy, drill = m.groups()
        pads.append({"num": num, "type": ptype, "shape": shape,
                     "px": float(px), "py": float(py),
                     "sx": float(sx or 0.0), "sy": float(sy or 0.0),
                     "drill": float(drill) if drill else None})
    crtyd = None
    for m in FP_RECT_RE.finditer(text):
        if "F.CrtYd" in m.group(6):
            crtyd = tuple(float(v) for v in m.groups()[:4])
            break
    fab = []
    for m in FP_LINE_RE.finditer(text):
        if "F.Fab" in m.group(6):
            fab.append(tuple(float(v) for v in m.groups()[:4]))
    return {"pads": pads, "crtyd": crtyd, "fab_lines": fab}


def pin_axis(pads: list) -> str:
    """★判【针排轴】= 焊盘中心分布的那条轴 (x 变 or y 变)★"""
    xs = {round(p["px"], 6) for p in pads}
    ys = {round(p["py"], 6) for p in pads}
    if len(xs) > 1 and len(ys) == 1:
        return "x"
    if len(ys) > 1 and len(xs) == 1:
        return "y"
    return "?"


def local_envelope(pads: list):
    """→ 铜箔外框 (x0,y0,x1,y1) (以焊盘方框并集计)"""
    x0 = min(p["px"] - p["sx"] / 2.0 for p in pads)
    x1 = max(p["px"] + p["sx"] / 2.0 for p in pads)
    y0 = min(p["py"] - p["sy"] / 2.0 for p in pads)
    y1 = max(p["py"] + p["sy"] / 2.0 for p in pads)
    return (x0, y0, x1, y1)


def fab_box(lines):
    xs, ys = [], []
    for (sx, sy, ex, ey) in lines:
        xs += [sx, ex]
        ys += [sy, ey]
    return (min(xs), min(ys), max(xs), max(ys))


def tht_geometry(mod_path: str) -> dict:
    """→ 官方 THT land 几何 (★全部从 `.kicad_mod` 实算·不写死任何常数★)"""
    mod = parse_mod(mod_path)
    pads = mod["pads"]
    if not pads:
        raise AssertionError("`.kicad_mod` 里读不到焊盘: %s" % mod_path)
    axis = pin_axis(pads)
    if axis == "?":
        raise AssertionError("判不出针排轴: %s" % mod_path)
    first = pads[0]
    if axis == "x":
        pitch = abs(pads[1]["px"] - first["px"])
        span = max(abs(p["px"] - first["px"]) for p in pads)
        pad_along, pad_across = first["sx"], first["sy"]
    else:
        pitch = abs(pads[1]["py"] - first["py"])
        span = max(abs(p["py"] - first["py"]) for p in pads)
        pad_along, pad_across = first["sy"], first["sx"]
    env = local_envelope(pads)
    crtyd = mod["crtyd"]
    fabb = fab_box(mod["fab_lines"])
    drill = first["drill"]
    return {
        "npads": len(pads),
        "axis_local": axis,
        "pitch": pitch,
        "span": span,
        "pad_along": pad_along,
        "pad_across": pad_across,
        "drill": drill,
        "annular": ((pad_along - drill) / 2.0) if drill else None,
        "copper_w_along": span + pad_along,          # ★沿针排轴的铜箔宽 (★核心数★)★
        "copper_w_across": pad_across,
        "copper_local": list(env),
        "crtyd_local": list(crtyd) if crtyd else None,
        "crtyd_wh": [crtyd[2] - crtyd[0], crtyd[3] - crtyd[1]] if crtyd else None,
        "fab_local": list(fabb),
        "fab_wh": [fabb[2] - fabb[0], fabb[3] - fabb[1]],
        "pads": pads,
        "mod_path": mod_path,
    }


def smd_geometry(mod_path: str) -> dict:
    """→ 官方 SMD 变体几何 (★降级方案·独立实测·不许套 THT 的数★)"""
    mod = parse_mod(mod_path)
    pads = mod["pads"]
    env = local_envelope(pads)
    crtyd = mod["crtyd"]
    fabb = fab_box(mod["fab_lines"])
    xs = sorted({round(p["px"], 6) for p in pads})
    ys = sorted({round(p["py"], 6) for p in pads})
    # ★交错判定: 焊盘在【针序】上左右两列交替 (⇒ 2 列 × 4 行交错, 不是 1×4 直排)★
    col_seq = []
    for p in pads:
        cx = min(xs, key=lambda v: abs(v - p["px"]))
        if not col_seq or col_seq[-1] != cx:
            col_seq.append(cx)
    staggered = len(xs) == 2 and len(ys) == 4 and col_seq == [xs[0], xs[1], xs[0], xs[1]]
    return {
        "npads": len(pads),
        "pad_size": [pads[0]["sx"], pads[0]["sy"]],
        "col_x": xs,
        "row_y": ys,
        "arrangement": "%dx%d%s" % (len(xs), len(ys), "_staggered" if staggered else ""),
        "staggered": staggered,
        "copper_w": env[2] - env[0],
        "copper_h": env[3] - env[1],
        "copper_local": list(env),
        "crtyd_wh": [crtyd[2] - crtyd[0], crtyd[3] - crtyd[1]],
        "fab_wh": [fabb[2] - fabb[0], fabb[3] - fabb[1]],
        "mod_path": mod_path,
    }


# --------------------------------------------------------------------------------------------------
# 板面占位只读解析
# --------------------------------------------------------------------------------------------------
def rot_point(x: float, y: float, deg: float):
    """★KiCad 封装摆放变换: 板坐标 (Y 向下) 下 局部 (x,y) → 板向偏移★"""
    r = math.radians(deg)
    return (x * math.cos(r) + y * math.sin(r), -x * math.sin(r) + y * math.cos(r))


def board_jdebug(pcb_path: str) -> dict:
    """→ 板面 `J_DEBUG` 封装实读 (★焊盘在封装里是【局部坐标】⇒ 必须加上封装原点才是板向铜箔★)"""
    text = read_text(pcb_path)
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("(footprint"):
            depth, j = 0, i
            while j < len(lines):
                depth += lines[j].count("(") - lines[j].count(")")
                if depth == 0 and j > i:
                    break
                j += 1
            blk = "\n".join(lines[i:j + 1])
            if re.search(r'\(property "Reference" "J_DEBUG"', blk):
                at = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', blk)
                ox, oy = float(at.group(1)), float(at.group(2))
                rot = float(at.group(3)) if at.group(3) else 0.0
                pads = []
                for m in re.finditer(
                        r'\(pad "([^"]*)" (\S+) (\S+)\s*\(at ([-\d.]+) ([-\d.]+)\)\s*'
                        r'\(size ([-\d.]+) ([-\d.]+)\)', blk):
                    pads.append({"num": m.group(1), "type": m.group(2), "shape": m.group(3),
                                 "px": float(m.group(4)), "py": float(m.group(5)),
                                 "sx": float(m.group(6)), "sy": float(m.group(7))})
                libid = re.match(r'\(footprint(?: "([^"]*)")?', blk)
                xs, ys = [], []
                for p in pads:
                    dx, dy = rot_point(p["px"], p["py"], rot)
                    ax = ox + dx
                    ay = oy + dy
                    xs += [ax - p["sx"] / 2.0, ax + p["sx"] / 2.0]
                    ys += [ay - p["sy"] / 2.0, ay + p["sy"] / 2.0]
                return {"origin": (ox, oy), "rot": rot, "pads": pads,
                        "lib_id": (libid.group(1) if libid and libid.group(1) else ""),
                        "copper_x": [min(xs), max(xs)], "copper_y": [min(ys), max(ys)],
                        "copper_w": max(xs) - min(xs), "copper_h": max(ys) - min(ys)}
            i = j + 1
        else:
            i += 1
    raise AssertionError("板面读不到 J_DEBUG")


def board_jdebug_pad_geom(pcb_path: str) -> dict:
    """→ 板面占位焊盘的排布 (pitch / pad 宽高 / 轴)"""
    b = board_jdebug(pcb_path)
    pads = b["pads"]
    if not pads:
        raise AssertionError("板面 J_DEBUG 没读到焊盘")
    xs = sorted({round(p["px"], 6) for p in pads})
    ys = sorted({round(p["py"], 6) for p in pads})
    axis = "x" if len(xs) > 1 else "y"
    pitch = (abs(xs[1] - xs[0]) if axis == "x" else abs(ys[1] - ys[0])) if len(pads) > 1 else 0.0
    p0 = pads[0]
    return {"axis": axis, "pitch": pitch,
            "pad_w": p0["sx"], "pad_h": p0["sy"],
            "npads": len(pads), "pad_type": p0["type"]}


# --------------------------------------------------------------------------------------------------
# 判据常量 (CRIT / 开口 X)
# --------------------------------------------------------------------------------------------------
def parse_crit(crit_py: str):
    """→ (crit, tol) ★从 `MECH/service_port_check.py` 真身取·不许写死 0.60★"""
    txt = read_text(crit_py)
    m_tol = re.search(r'"fdm_part"\s*:\s*([-\d.]+)', txt)
    m_crit = re.search(r'CRIT\s*=\s*2\s*\*\s*TOL\["fdm_part"\]', txt)
    if not m_tol:
        raise AssertionError("判据真身读不到 TOL['fdm_part']")
    if not m_crit:
        raise AssertionError("判据真身形状变了 (CRIT 不再是 2 * TOL['fdm_part']) ⇒ 人工复核")
    tol = float(m_tol.group(1))
    return 2.0 * tol, tol


def parse_open_x(cross_md: str):
    """→ 调试口开口 X (★从 MECH 权威页机器块 `openings[]` 取·不是从本页取★)"""
    blocks = parse_machine_blocks(read_text(cross_md))
    if not blocks:
        raise AssertionError("MECH 交叉核对页读不到机器块")
    for blk in blocks:
        for op in (blk.get("openings") or []):
            if op.get("id") == "PORT_OPEN_DEBUG" or op.get("covers") == "J_DEBUG":
                return [float(op["open_x"][0]), float(op["open_x"][1])]
    raise AssertionError("MECH 交叉核对页机器块里找不到 PORT_OPEN_DEBUG 开口 X")


# ==================================================================================================
# 七条判据
# ==================================================================================================
def _gate(name: str, errs: list) -> dict:
    return {"ok": not errs, "errs": errs, "name": name}


def g1_official_tht_land(ctx) -> dict:
    """G1 · 官方 THT land 的焊盘几何必须与盘上 `.kicad_mod` 实读一致 (★自己解析★)"""
    errs = []
    geo = ctx["tht"]
    blk = ctx["land_tht"]
    if geo["npads"] != 4:
        errs.append("官方 THT 焊盘数实读 %d ≠ 4" % geo["npads"])
    if geo["axis_local"] not in ("x", "y"):
        errs.append("判不出针排轴 (实读 %r)" % geo["axis_local"])
    if not near(geo["pitch"], 1.27):
        errs.append("官方 THT pitch 实读 %.4f ≠ 1.27" % geo["pitch"])
    if not near(geo["span"], 3.81):
        errs.append("官方 THT 跨距实读 %.4f ≠ 3.81" % geo["span"])
    if not near(geo["pad_along"], 1.0) or not near(geo["pad_across"], 1.0):
        errs.append("官方 THT 焊盘尺寸实读 %.4f×%.4f ≠ 1.0×1.0"
                    % (geo["pad_along"], geo["pad_across"]))
    if geo["drill"] is None or not near(geo["drill"], 0.65):
        errs.append("官方 THT 钻孔实读 %r ≠ 0.65" % geo["drill"])
    for p in geo["pads"]:
        if p["type"] != "thru_hole":
            errs.append("官方 THT pad %s 类型实读 %r ≠ thru_hole" % (p["num"], p["type"]))
    # ★页内声明 vs 实算★
    pairs = [
        ("npads", geo["npads"], blk.get("npads")),
        ("pitch_mm", geo["pitch"], blk.get("pitch_mm")),
        ("pin_span_mm", geo["span"], blk.get("pin_span_mm")),
        ("copper_w_along_axis_mm", geo["copper_w_along"], blk.get("copper_w_along_axis_mm")),
        ("copper_w_across_axis_mm", geo["copper_w_across"], blk.get("copper_w_across_axis_mm")),
        ("drill_mm", geo["drill"], blk.get("drill_mm")),
        ("annular_ring_mm", geo["annular"], blk.get("annular_ring_mm")),
    ]
    for nm, got, want in pairs:
        if want is None:
            errs.append("页内机器块 land_tht.%s 缺失" % nm)
        elif not near(got, want):
            errs.append("页内 land_tht.%s 写 %s, 实算 %s" % (nm, want, round(got, 6)))
    if blk.get("pad_type") != "thru_hole":
        errs.append("页内 land_tht.pad_type 写 %r ≠ thru_hole" % blk.get("pad_type"))
    ctx["geo"] = geo
    return _gate("G1 官方 THT land 几何与 .kicad_mod 实读一致", errs)


def g2_declared_widths_match_recompute(ctx) -> dict:
    """G2 · §1 那一页声明的三档【宽度】必须与 G1 实算逐项一致"""
    errs = []
    geo = ctx["geo"]
    calib = ctx["calibers"]
    b = ctx["board"]
    bp = ctx["board_pad"]
    # ★三档铜箔宽 (全部现算)★
    expect = {
        "current": (b["copper_w"], b["copper_h"]),
        # ★现页口径 = 官方跨距 + 板面占位 pad 宽 (★沿用 SMD 占位的 0.275★)★
        "page_0275": (geo["span"] + bp["pad_w"], bp["pad_h"]),
        # ★官方 THT 真值★
        "official_tht": (geo["copper_w_along"], geo["pad_across"]),
    }
    ctx["expect_widths"] = expect
    for name, (w, h) in expect.items():
        c = calib.get(name)
        if not isinstance(c, dict):
            errs.append("页内 calibers.%s 缺失" % name)
            continue
        if not near(c.get("copper_w_mm"), w):
            errs.append("calibers.%s.copper_w_mm 写 %s, 实算 %s"
                        % (name, c.get("copper_w_mm"), round(w, 6)))
        if not near(c.get("copper_h_mm"), h):
            errs.append("calibers.%s.copper_h_mm 写 %s, 实算 %s"
                        % (name, c.get("copper_h_mm"), round(h, 6)))
    # ★板面占位自身也要对得上 (页内 board_placeholder)★
    bp_blk = ctx["board_placeholder"]
    if bp_blk:
        if not near(bp_blk.get("copper_w_mm"), b["copper_w"]):
            errs.append("页内 board_placeholder.copper_w_mm 写 %s, 板读 %s"
                        % (bp_blk.get("copper_w_mm"), round(b["copper_w"], 6)))
        if not near(bp_blk.get("pitch_mm"), bp["pitch"]):
            errs.append("页内 board_placeholder.pitch_mm 写 %s, 板读 %s"
                        % (bp_blk.get("pitch_mm"), bp["pitch"]))
    return _gate("G2 §1 三档宽度与 G1 实算逐项一致", errs)


def g3_must_clear_no_overflow(ctx) -> dict:
    """G3 · 必须清空区宽 ≥ 铜箔 X 宽 (★不许越界★) + 越界事实必须被显式记账"""
    errs = []
    geo = ctx["geo"]
    calib = ctx["calibers"]
    copper = geo["copper_w_along"]
    center = ctx["copper_center"]
    for name in ("current", "page_0275", "official_tht"):
        c = calib.get(name) or {}
        w = c.get("must_clear_w_mm")
        if w is None:
            errs.append("calibers.%s.must_clear_w_mm 缺失" % name)
            continue
        rng = c.get("must_clear_x") or []
        if len(rng) != 2:
            errs.append("calibers.%s.must_clear_x 缺失" % name)
            continue
        if not near(rng[1] - rng[0], w):
            errs.append("calibers.%s.must_clear_x 宽 %s ≠ must_clear_w_mm %s"
                        % (name, round(rng[1] - rng[0], 6), w))
        if not near((rng[0] + rng[1]) / 2.0, center, 1e-4):
            errs.append("calibers.%s.must_clear_x 未对中铜箔中心 %s" % (name, round(center, 4)))
    # ★★核心: 权威口径的清空区不许比铜箔窄 ⇒ 不许越界★★
    off = calib.get("official_tht") or {}
    ow = off.get("must_clear_w_mm")
    if ow is not None:
        if ow < copper - TOL:
            errs.append("★官方 THT 口径下必须清空区宽 %s < 铜箔宽 %s ⇒ 每边越界 %.4f ⇒ "
                        "铜箔直接进清空区★" % (ow, round(copper, 4), (copper - ow) / 2.0))
    # ★旧口径 (4.0850) 仍在页内 ⇒ 越界事实必须被显式记账★
    legacy = calib.get("page_0275") or {}
    lw = legacy.get("must_clear_w_mm")
    ov = ctx["overflow"]
    if lw is not None and lw < copper - TOL:
        per_edge = (copper - lw) / 2.0
        if not ov:
            errs.append("旧口径 %s 仍带在页内 ⇒ 必须清空区缺『越界记账』(overflow 块)" % lw)
        else:
            if not near(ov.get("per_edge_mm"), per_edge):
                errs.append("overflow.per_edge_mm 写 %s, 实算 %s"
                            % (ov.get("per_edge_mm"), round(per_edge, 6)))
            if not near(ov.get("total_mm"), copper - lw):
                errs.append("overflow.total_mm 写 %s, 实算 %s"
                            % (ov.get("total_mm"), round(copper - lw, 6)))
            if not near(ov.get("legacy_must_clear_w_mm"), lw):
                errs.append("overflow.legacy_must_clear_w_mm 写 %s, 页内旧口径 %s"
                            % (ov.get("legacy_must_clear_w_mm"), lw))
            if not near(ov.get("official_copper_w_mm"), copper):
                errs.append("overflow.official_copper_w_mm 写 %s, 实算 %s"
                            % (ov.get("official_copper_w_mm"), round(copper, 6)))
    else:
        # ★旧口径已被清掉 ⇒ 四处旧数也必须同步清掉 (不许只清一处)★
        for rel in STALE_DOCS:
            p = os.path.join(ctx["root"], rel)
            if not os.path.isfile(p):
                continue
            txt = read_text(p)
            hit = [n for n in STALE_NUMBERS if n in txt]
            if hit:
                errs.append("页内旧口径已清掉, 但 %s 仍带旧数 %s ⇒ 只清一处" % (rel, ",".join(hit)))
    return _gate("G3 必须清空区宽 ≥ 铜箔 X 宽 (不许越界) + 越界记账", errs)


def g4_clearance_symmetric_and_crit(ctx) -> dict:
    """G4 · 单边间隙 X (左/右) 对称且 ≥ CRIT (★CRIT 从真身取·不许写死★)"""
    errs = []
    geo = ctx["geo"]
    crit, tol = ctx["crit"], ctx["tol"]
    open_x = ctx["open_x"]
    copper = geo["copper_w_along"]
    center = ctx["copper_center"]
    # ★居中解: 铜箔中心必须 = 开口 X 中心 (否则开口口径要动)★
    open_center = (open_x[0] + open_x[1]) / 2.0
    if not near(center, open_center, 1e-4):
        errs.append("板面铜箔中心 %s ≠ 开口 X 中心 %s ⇒ 居中解前提不成立"
                    % (round(center, 4), round(open_center, 4)))
    x0 = center - copper / 2.0
    x1 = center + copper / 2.0
    left = x0 - open_x[0]
    right = open_x[1] - x1
    worst = min(left, right) - tol
    ctx["recomputed"] = {"clearance_x_left": left, "clearance_x_right": right,
                         "worst_clearance_x": worst, "margin_ratio": worst / crit}
    off = ctx["calibers"].get("official_tht") or {}
    for nm, got in (("clearance_x_left", left), ("clearance_x_right", right),
                    ("worst_clearance_x", worst)):
        if not near(off.get(nm), got):
            errs.append("calibers.official_tht.%s 写 %s, 实算 %s"
                        % (nm, off.get(nm), round(got, 6)))
    if not near(left, right, 1e-9):
        errs.append("单边间隙左右不对称: 左 %.4f / 右 %.4f" % (left, right))
    if left < crit - TOL:
        errs.append("单边间隙 X 左 %.4f < CRIT %.2f" % (left, crit))
    if right < crit - TOL:
        errs.append("单边间隙 X 右 %.4f < CRIT %.2f" % (right, crit))
    if worst < crit - TOL:
        errs.append("最坏单边间隙 X %.4f < CRIT %.2f" % (worst, crit))
    # ★页内 consts.crit 必须 = 真身 (不许写死别的数)★
    consts = ctx["consts"]
    if not near(consts.get("crit"), crit):
        errs.append("页内 consts.crit 写 %s, 真身 %s" % (consts.get("crit"), crit))
    if not near(consts.get("fdm_part_tol"), tol):
        errs.append("页内 consts.fdm_part_tol 写 %s, 真身 %s" % (consts.get("fdm_part_tol"), tol))
    return _gate("G4 单边间隙 X 对称且 ≥ CRIT (CRIT 取自真身)", errs)


def g5_smd_fallback_measured(ctx) -> dict:
    """G5 · 降级方案 (SMD 变体) 的几何必须也实测一遍并单列 (★不许拿 THT 的数套用★)"""
    errs = []
    geo = ctx["geo"]
    smd = ctx["smd"]
    blk = ctx["land_smd"]
    if not blk:
        errs.append("页内机器块缺 land_smd (降级方案必须单列)")
        return _gate("G5 降级方案 (SMD 变体) 几何独立实测并单列", errs)
    if smd["npads"] != 4:
        errs.append("SMD 变体焊盘数实读 %d ≠ 4" % smd["npads"])
    if not smd.get("staggered"):
        errs.append("★SMD 变体排布实读 %s ≠ 2 列 × 4 行交错 (降级方案不是 1×4 直排)★"
                    % smd["arrangement"])
    arr = str(blk.get("arrangement") or "").lower()
    if "staggered" not in arr and "交错" not in arr:
        errs.append("land_smd.arrangement 必须写明是交错排布, 现写 %r" % blk.get("arrangement"))
    if not near(blk.get("copper_w_mm"), smd["copper_w"]):
        errs.append("land_smd.copper_w_mm 写 %s, 实算 %s"
                    % (blk.get("copper_w_mm"), round(smd["copper_w"], 6)))
    if not near(blk.get("copper_h_mm"), smd["copper_h"]):
        errs.append("land_smd.copper_h_mm 写 %s, 实算 %s"
                    % (blk.get("copper_h_mm"), round(smd["copper_h"], 6)))
    if not near((blk.get("crtyd_wh_mm") or [None, None])[0], smd["crtyd_wh"][0]) or \
            not near((blk.get("crtyd_wh_mm") or [None, None])[1], smd["crtyd_wh"][1]):
        errs.append("land_smd.crtyd_wh_mm 写 %s, 实算 %s"
                    % (blk.get("crtyd_wh_mm"), [round(v, 4) for v in smd["crtyd_wh"]]))
    # ★不许拿 THT 的数套用★
    if near(blk.get("copper_w_mm"), geo["copper_w_along"]):
        errs.append("land_smd.copper_w_mm 与 THT 铜箔宽相同 ⇒ 拿 THT 的数套用了")
    # ★降级方案要过的开口 Y 必须现算★
    need_y = smd["copper_h"] + 2.0 * (ctx["crit"] + ctx["tol"])
    if not near(blk.get("required_open_y_mm"), need_y):
        errs.append("land_smd.required_open_y_mm 写 %s, 实算 %s"
                    % (blk.get("required_open_y_mm"), round(need_y, 6)))
    # ★降级方案必须被判红 (三档 Y 全红) 并写出来★
    rot0 = blk.get("centered_rot0") or {}
    py = rot0.get("pass_crit_y_by_tier") or {}
    if not py or any(bool(v) for v in py.values()):
        errs.append("land_smd.centered_rot0.pass_crit_y_by_tier 必须三档全 false (降级方案 Y 全红)")
    verdict = str(blk.get("verdict") or "")
    if "红" not in verdict:
        errs.append("land_smd.verdict 必须写明『三档 Y 全红』, 现写 %r" % verdict)
    return _gate("G5 降级方案 (SMD 变体) 几何独立实测并单列", errs)


def g6_board_zero_write(ctx) -> dict:
    """G6 · 板面零写板自证 (md5 / mtime / size 三项)"""
    errs = []
    p = ctx["pcb_path"]
    if not os.path.isfile(p):
        errs.append("板文件不在盘: %s" % p)
        return _gate("G6 板面零写板自证 (md5/mtime/size)", errs)
    got_md5 = md5_of(p)
    st = os.stat(p)
    ns = st.st_mtime_ns
    sec, nsec = ns // 1_000_000_000, ns % 1_000_000_000
    got_mtime = "%s.%09d" % (datetime.datetime.fromtimestamp(sec).strftime("%Y-%m-%d %H:%M:%S"),
                             nsec)
    if got_md5 != BOARD_BASELINE["md5"]:
        errs.append("★板 md5 漂移: 实读 %s, 基线 %s★" % (got_md5, BOARD_BASELINE["md5"]))
    if got_mtime != BOARD_BASELINE["mtime"]:
        errs.append("★板 mtime 漂移: 实读 %s, 基线 %s★" % (got_mtime, BOARD_BASELINE["mtime"]))
    if st.st_size != BOARD_BASELINE["size"]:
        errs.append("★板 size 漂移: 实读 %d, 基线 %d★" % (st.st_size, BOARD_BASELINE["size"]))
    ctx["board_triple"] = {"md5": got_md5, "mtime": got_mtime, "size": st.st_size}
    return _gate("G6 板面零写板自证 (md5/mtime/size)", errs)


_EVID_TOKEN_RE = re.compile(r"\[([^\]\n]{1,14})\]")
_EVID_LIKE_RE = re.compile(r"^[\u4e00-\u9fff0-9]{1,14}$")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def _evidence_tokens(body: str):
    """★只挑出「像证据等级标签」的方括号 token (★照 led_spec_sync 的形状·不假红★)★"""
    out = []
    for m in _EVID_TOKEN_RE.finditer(body):
        content = m.group(1)
        if not _EVID_LIKE_RE.match(content):
            continue
        if not _CJK_RE.search(content):
            continue
        if body[m.end():m.end() + 1] == "(" and m.group(0) not in EVIDENCE_WHITELIST \
                and m.group(0) not in FORBIDDEN_EVIDENCE:
            continue
        out.append(m.group(0))
    return out


def g7_evidence_and_wording(ctx) -> dict:
    """G7 · 证据等级五级白名单 + 正文零挂起措辞 + 「判据句/事实句」两句分开 + `.kicad_mod` md5 台账"""
    errs = []
    text = ctx["page_text"]
    # ① 五级白名单
    for tk in _evidence_tokens(text):
        if tk in FORBIDDEN_EVIDENCE:
            errs.append("证据等级 %s 在禁用名单 ⇒ 只许用五级白名单 %s" % (tk, "/".join(EVIDENCE_WHITELIST)))
        elif tk not in EVIDENCE_WHITELIST:
            errs.append("证据等级 %s 不在五级白名单 %s" % (tk, "/".join(EVIDENCE_WHITELIST)))
    if not any(tk in EVIDENCE_WHITELIST for tk in _evidence_tokens(text)):
        errs.append("正文一个证据等级标记都没有")
    # ② 正文零挂起措辞
    for w in HEDGING_WORDS:
        if w in text:
            errs.append("正文出现挂起措辞 %r (不许无档措辞)" % w)
    for w in FORBIDDEN_PHRASES:
        if w in text:
            errs.append("正文出现 %r (不许把活推给原厂回信)" % w)
    # ③ ★两句分开★ (判据句 / 事实句) — 逐行扫描: 「合格」与 CRIT 同现 ⇒ 混成一句 ⇒ 红
    #    ★**例外 (不许漏放)**: 本页/本文自己写的【禁止令式】语句 (「不许把…写成…」「≠」「分开」…)
    #    本身就要同时提到这两个词 ⇒ 遇到禁止令标记即放行 (否则闸会把自己的纪律文案判红)★
    PROHIBIT_MARKERS = ("不许", "不得", "禁止", "≠", "不等于", "分开", "混成", "禁 ")
    for ln in text.split("\n"):
        if "合格" not in ln:
            continue
        if not ("过 CRIT" in ln or "过 `CRIT`" in ln or "≥ CRIT" in ln
                or "≥`CRIT`" in ln or "CRIT" in ln):
            continue
        if any(mk in ln for mk in PROHIBIT_MARKERS):
            continue
        errs.append("★同一行里把「方向过 CRIT」和「合格」混成一句 (判据句与事实句必须分开写)★")
    if "判据句" not in text or "事实句" not in text:
        errs.append("★页内必须显式写出「判据句」与「事实句」两句 (方向过阈 ≠ 铜箔不进清空区)★")
    # ④ `.kicad_mod` 逐个 test -f + md5 台账
    # ★只取「像路径」的候选 (★必须带 `/` ⇒ 页正文里 `.kicad_mod` 这种裸词不算★)★
    paths = sorted(set(re.findall(r"(?:/[^\s`*\"'()\[\]]+)+\.kicad_mod", text)))
    if not paths:
        errs.append("页内一个 `.kicad_mod` 引用都没有 ⇒ 官方 land 几何不可核")
    ledger = ctx["mod_md5"]
    for pth in paths:
        if not os.path.isabs(pth):
            pth = os.path.join(LIBROOT, pth)
        if not os.path.isfile(pth):
            errs.append("★页内引用的 `.kicad_mod` 不在盘: %s★" % pth)
            continue
        got = md5_of(pth)
        if pth not in ledger:
            errs.append("★页内引用的 `.kicad_mod` 没有 md5 记账: %s (实读 %s)★" % (pth, got))
        elif ledger[pth] != got:
            errs.append("★`.kicad_mod` md5 对不上: %s 记账 %s / 实读 %s★"
                        % (pth, ledger[pth], got))
    # ⑤ KiCad 官方库清单数 (现算, 不写死)
    inv = ctx["lib_inventory"]
    if inv is not None:
        blk_inv = ctx["lib_inv_blk"] or {}
        if blk_inv:
            if blk_inv.get("pretty_dirs") != inv["pretty_dirs"]:
                errs.append("页内 kicad 库清单 .pretty 目录数写 %s, 实数 %s"
                            % (blk_inv.get("pretty_dirs"), inv["pretty_dirs"]))
            if blk_inv.get("kicad_mod_files") != inv["kicad_mod_files"]:
                errs.append("页内 kicad 库清单 .kicad_mod 文件数写 %s, 实数 %s"
                            % (blk_inv.get("kicad_mod_files"), inv["kicad_mod_files"]))
    # ⑥ 沙盒路径必须落项目盘 (不许写系统 /tmp)
    sbx = str(ctx["page_main"].get("sandbox") or "")
    if sbx:
        if sbx.startswith("/tmp") or not sbx.startswith("tmp/"):
            errs.append("沙盒路径 %r 必须落项目盘 tmp/ (★系统 /tmp 配额已满·会拿到假读数★)" % sbx)
    return _gate("G7 证据等级五级白名单 + 零挂起措辞 + 两句分开 + md5 台账", errs)


# ==================================================================================================
# 主检查
# ==================================================================================================
def run_checks(root: str, page_path=None, cross_path=None, crit_path=None, pcb_path=None) -> dict:
    root = os.path.abspath(root)
    page_path = page_path or os.path.join(root, PAGE_REL)
    cross_path = cross_path or os.path.join(root, CROSS_REL)
    crit_path = crit_path or os.path.join(root, CRIT_REL)
    pcb_path = pcb_path or os.path.join(root, PCB_REL)
    ctx = {"root": root, "page_path": page_path, "cross_path": cross_path,
           "crit_path": crit_path, "pcb_path": pcb_path}
    errs = []
    if not os.path.isfile(page_path):
        return {"__io__": ["真相页不在盘: %s" % page_path]}
    text = read_text(page_path)
    ctx["page_text"] = text
    try:
        blocks = parse_machine_blocks(text)
    except AssertionError as exc:
        return {"__io__": [str(exc)]}
    if not blocks:
        return {"__io__": ["真相页里读不到机器块 JSON"]}
    main_blk = blocks[0]
    add_blk = blocks[-1] if len(blocks) > 1 else {}
    ctx["page_main"] = main_blk
    ctx["consts"] = main_blk.get("consts") or {}
    ctx["land_tht"] = main_blk.get("land_tht") or {}
    ctx["land_smd"] = main_blk.get("land_smd") or {}
    ctx["board_placeholder"] = main_blk.get("board_placeholder") or {}
    ctx["calibers"] = main_blk.get("calibers") or {}
    ctx["overflow"] = main_blk.get("overflow") or {}
    ctx["mod_md5"] = (add_blk.get("mod_md5") or {})
    ctx["lib_inv_blk"] = (add_blk.get("kicad_lib_inventory") or {})

    try:
        ctx["crit"], ctx["tol"] = parse_crit(crit_path)
        ctx["open_x"] = parse_open_x(cross_path)
        ctx["tht"] = tht_geometry(os.path.join(LIBROOT, THT_LIBDIR, THT_MOD_NAME))
        ctx["smd"] = smd_geometry(os.path.join(LIBROOT, THT_LIBDIR, SMD_MOD_NAME))
        ctx["board"] = board_jdebug(pcb_path)
        ctx["board_pad"] = board_jdebug_pad_geom(pcb_path)
    except AssertionError as exc:
        return {"__io__": [str(exc)]}

    b = ctx["board"]
    ctx["copper_center"] = (b["copper_x"][0] + b["copper_x"][1]) / 2.0
    ctx["lib_inventory"] = lib_inventory()

    res = {}
    res["G1"] = g1_official_tht_land(ctx)
    res["G2"] = g2_declared_widths_match_recompute(ctx)
    res["G3"] = g3_must_clear_no_overflow(ctx)
    res["G4"] = g4_clearance_symmetric_and_crit(ctx)
    res["G5"] = g5_smd_fallback_measured(ctx)
    res["G6"] = g6_board_zero_write(ctx)
    res["G7"] = g7_evidence_and_wording(ctx)
    return res


def lib_inventory() -> dict:
    """→ 本机 KiCad 官方库清单数 (★现算·不写死★)"""
    if not os.path.isdir(LIBROOT):
        return None
    pretty = 0
    mods = 0
    for name in os.listdir(LIBROOT):
        p = os.path.join(LIBROOT, name)
        if os.path.isdir(p) and name.endswith(".pretty"):
            pretty += 1
            for f in os.listdir(p):
                if f.endswith(".kicad_mod"):
                    mods += 1
    return {"pretty_dirs": pretty, "kicad_mod_files": mods}


# ==================================================================================================
# 反向用例 (★每条自证「红的集合 == {目标那一条}」★)
# ==================================================================================================
def _sandbox(root: str, name: str) -> str:
    sb = os.path.join(root, "tmp", "iss371", "selftest", name)
    if os.path.isdir(sb):
        shutil.rmtree(sb)
    for rel in (PAGE_REL, CROSS_REL, CRIT_REL, PCB_REL):
        src = os.path.join(root, rel)
        if not os.path.isfile(src):
            continue
        dst = os.path.join(sb, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    return sb


def _mut(text: str, old: str, new: str, count: int = 1) -> str:
    if old not in text:
        raise AssertionError("反向用例没找到要改的串: %r" % old)
    out = text.replace(old, new, count)
    if out == text:
        raise AssertionError("反向用例没改到任何东西")
    return out


def _mut_block(text: str, old: str, new: str, which: int = 0) -> str:
    """★只改第 `which` 个机器块里的串 (★页正文里也有同一串数字·不限定就会改错地方★)★

    ★**实现注**: 不用 `re.split` (★它会把 BEGIN/END 标记吃掉·拼回去就丢标记★) ⇒
      用 `finditer` 拿到第 `which` 个块的 JSON 内容区间, 只在区间内做替换 ★
    """
    matches = list(BLOCK_RE.finditer(text))
    if which >= len(matches):
        raise AssertionError("反向用例找不到第 %d 个机器块 (共 %d 个)" % (which, len(matches)))
    m = matches[which]
    seg = m.group(1)
    new_seg = _mut(seg, old, new)
    return text[:m.start(1)] + new_seg + text[m.end(1):]


CASES = [
    ("① 把 §1 里的必须清空区宽改小 0.001 ⇒ G3 红",
     "G3", 0, lambda t: _mut_block(t, '"must_clear_w_mm": 4.81,', '"must_clear_w_mm": 4.809,')),
    ("② 把单边间隙改到 0.59 ⇒ G4 红",
     "G4", 0, lambda t: _mut_block(t, '"clearance_x_left": 2.695,', '"clearance_x_left": 0.59,')),
    ("③ 把左右间隙改成不等 ⇒ G4 红",
     "G4", 0, lambda t: _mut_block(t, '"clearance_x_right": 2.695,', '"clearance_x_right": 2.6,')),
    ("④ 把 §1 的 4.8100 改成 4.0850 ⇒ G2 红",
     "G2", 0, lambda t: _mut_block(t, '"copper_w_mm": 4.81,', '"copper_w_mm": 4.085,')),
    ("⑤ 把机器块里 land_tht 的 4.81 改成 4.085 ⇒ G1 红",
     "G1", 0, lambda t: _mut_block(t, '"copper_w_along_axis_mm": 4.81,',
                                   '"copper_w_along_axis_mm": 4.085,')),
    ("⑥ 降级方案拿 THT 的数套用 ⇒ G5 红",
     "G5", 0, lambda t: _mut_block(t, '"copper_w_mm": 6.0,', '"copper_w_mm": 4.81,')),
    ("⑦ 把证据等级写成第六级 ⇒ G7 红",
     "G7", 0, lambda t: _mut(t, "[实测]", "[推断]", 1)),
    ("⑧ 把 `.kicad_mod` 的 md5 记账改错 ⇒ G7 红",
     "G7", 1, lambda t: _mut_block(t, '"9d6b0e63e99e6484d2cd3fa0bb28c4a5"',
                                   '"deadbeefdeadbeefdeadbeefdeadbeef"', 1)),
    ("⑨ 把判据句与事实句混成一句「合格」 ⇒ G7 红",
     "G7", 0, lambda t: _mut(
         t, "★**判据句 (方向 · 判据层面)**:",
         "★**结论: 换官方 THT land 后结构侧合格 (单边间隙过 CRIT 0.60)** ★\n\n"
         "★**判据句 (方向 · 判据层面)**:", 1)),
]


def selftest(root: str) -> int:
    print("=" * 88)
    print("【自检】反向用例 (★每条自证「红的是目标那一条, 其余仍绿」★)")
    print("=" * 88)
    ok_all = True
    res0 = run_checks(root)
    if "__io__" in res0:
        print("  ✗ 正向对照直接 IO 失败: %s" % res0["__io__"])
        return 1
    n_bad = [k for k, v in res0.items() if not v["ok"]]
    print("  ⓪ 正向对照 (真件一切如常) ⇒ %s" % ("✅ 全绿" if not n_bad else "❌ 红了: %s" % n_bad))
    if n_bad:
        ok_all = False

    for name, target, which, fn in CASES:
        sb = _sandbox(root, "case_%s" % target)
        target_file = os.path.join(sb, PAGE_REL)
        pristine = read_text(target_file)
        try:
            bad = fn(pristine)
        except AssertionError as exc:
            print("  ✗ %s ⇒ ★用例自身坏了: %s★" % (name, exc))
            ok_all = False
            continue
        with open(target_file, "w", encoding="utf-8") as fh:
            fh.write(bad)
        r2 = run_checks(sb)
        if "__io__" in r2:
            print("  ✗ %s ⇒ ★用例自身坏了: %s★" % (name, r2["__io__"]))
            ok_all = False
            continue
        red = sorted(k for k, v in r2.items() if not v["ok"])
        hit = target in red
        others = [k for k in red if k != target]
        good = hit and not others
        print("  %s %s ⇒ 红组 %s (目标 %s %s)"
              % ("✅" if good else "❌", name, red or "∅", target,
                 "命中" if hit else "★没命中★"))
        if not good:
            ok_all = False
            for k in red:
                for e in r2[k]["errs"][:3]:
                    print("        · %s: %s" % (k, e))
        shutil.rmtree(sb, ignore_errors=True)

    # ---- 用例⑩: 沙盒里把板改一个字节 ⇒ G6 红 ----
    sb = _sandbox(root, "case_G6")
    pcb = os.path.join(sb, PCB_REL)
    with open(pcb, "a", encoding="utf-8") as fh:
        fh.write("\n# ★反向用例: 板改一个字节★\n")
    r3 = run_checks(sb)
    red3 = sorted(k for k, v in r3.items() if not v["ok"]) if "__io__" not in r3 else ["__io__"]
    good3 = (red3 == ["G6"])
    print("  %s ⑩ 沙盒里把板改一个字节 ⇒ G6 红 ⇒ 红组 %s"
          % ("✅" if good3 else "❌", red3 or "∅"))
    if not good3:
        ok_all = False
        for k in red3:
            if k in r3:
                for e in r3[k]["errs"][:3]:
                    print("        · %s: %s" % (k, e))
    shutil.rmtree(sb, ignore_errors=True)

    print("-" * 88)
    n = len(CASES) + 1
    print("【自检结论】%s" % ("✅ %d 条反向用例全抓到 (且其余判据仍绿) ★ ALL TESTS PASS ★" % n
                              if ok_all else "❌ 有用例没抓到 ★ TESTS FAILED ★"))
    return 0 if ok_all else 1


# ==================================================================================================
# main
# ==================================================================================================
def main() -> int:
    ap = argparse.ArgumentParser(description="ISS-371 J_DEBUG 1.27mm land 结构侧净距真相机器闸")
    ap.add_argument("--selftest", action="store_true", help="跑反向用例")
    ap.add_argument("--root", default=PROJ, help="扫指定树 (默认项目根)")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.selftest:
        return selftest(root)

    print("=" * 88)
    print("ISS-371 · `J_DEBUG` 排针 land 改 1.27mm 后的结构侧净距真相 —— 机器闸")
    print("扫: %s" % root)
    print("=" * 88)
    res = run_checks(root)
    if "__io__" in res:
        print("★IO 失败★")
        for e in res["__io__"]:
            print("  · %s" % e)
        return 2
    n_ok = 0
    for code in ("G1", "G2", "G3", "G4", "G5", "G6", "G7"):
        g = res[code]
        print("\n[%s] %s ⇒ %s" % (code, g["name"], "✅ PASS" if g["ok"] else "❌ FAIL"))
        for e in g["errs"]:
            print("    · %s" % e)
        if g["ok"]:
            n_ok += 1
    print("\n" + "-" * 88)
    print("★判据方向 (判据句): 换官方 THT land 后, 调试口单边间隙 X 仍过 `CRIT` ⇒ 方向不变 ★")
    print("★铜箔事实 (事实句): 若结构件仍按旧口径 4.0850 留 ⇒ 每边越界 0.3625 ⇒ 铜箔直接进清空区 ★")
    print("★两句同时成立, 不许混成一句「OK / 合格」; 且必须并进「板只改一次」那一趟同批改 ★")
    print("-" * 88)
    print("合计: %d/%d 条判据通过" % (n_ok, len(res)))
    return 0 if n_ok == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())
