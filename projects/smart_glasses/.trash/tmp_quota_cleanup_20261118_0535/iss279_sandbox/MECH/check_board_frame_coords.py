#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_board_frame_coords.py —— ISS-276 「板只改一次」那一趟的【坐标系闸】 (mech-lead)
=================================================================================================
干什么:
  ① **C1 帧标签**: 本单/工作包里出现的每个坐标组都必须带帧标签 ⇒ **漏标一条即红**
  ② **C2 归一后窗口不压 SoM 座**: 读板 ⇒ §3/§4 给的开口矩形与 LED 窗口 ⇒ **压住
     `J_SOM_P1..P4` 焊盘数必须 = 0**
  ③ **C3 两套坐标不可代入 (负向断言)**: 把 60×30 套A 口径的旧矩形喂进现役板坐标
     ⇒ **必须报出「压住了 N 个 SoM 焊盘」而不是静默通过**
  ④ **C4 受保护 5 件 md5 前后逐字节不变** (板 / `.kicad_pro` / 网表 / 脚表 / BOM)

★口径纪律 (硬):
  ① **判据阈值一个字节都不许自己写** ⇒ 本脚本把 `MECH/board_port_opening_s6_check.py`
     **当只读模块 import**, 直接取它的 `BASE` / `TOL` / `CRIT` / `OPEN_X` / `OPEN_Y`
     ⇒ 阈值零漂移 ★
  ② **不改任何既有 MECH/HW 文件** (★`board_port_opening_s6_check.py` / `service_port_check.py` /
     `check_demo_struct_truth.py` / `jd_y0_feasibility.py` / 板 / 网表 / 脚表 / BOM 一个字节不许动★)
     —— 本文件是**新增的独立脚本** ★
  ③ **不拍板**: 开口 / LED 的**最终坐标**一律「列条件 + 可放行空间 + 谁拍」 ★
  ④ 证据级: 盘上板读数 = `[实测]` (读得到才写); 设计态几何 = `[推算]`; **实物 [实测] = 0 条** ★

★为什么要这个闸 (ISS-276 的病灶):
  ISS-271 交的两个窗口 (`D_LED_G` 首选窗口 X 33.00..47.71 · 检修口开口 X 47.00..60.00) 是
  **60×30 套A 坐标**; 现役板是 **160×100 台架板** ⇒ 照字面抄进 §3-S6 = 开口压住 `J_SOM_P1`
  56 个焊盘 / LED 窗口压住 `J_SOM_P3` 10 个焊盘 ⇒ 本闸把这两种坐标**机器化隔开** ★

用法:
  python3 MECH/check_board_frame_coords.py             ⇒ 跑 C1~C4, 打印表
  python3 MECH/check_board_frame_coords.py --compute    ⇒ 打印现役板坐标系下的全部实算数
  python3 MECH/check_board_frame_coords.py --json       ⇒ 机器可读
  python3 MECH/check_board_frame_coords.py --selftest   ⇒ 反向用例 (★五条, 一条不许删★)

退出码: 0 = 全部通过; 2 = 有检查项不通过 (与既有 MECH 闸脚本 rc 语义一致)
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

S6_PATH = os.path.join(HERE, "board_port_opening_s6_check.py")
CALIB_REL = os.path.join("MECH", "BOARD_PORT_OPENING_S6_FRAME_CALIBER.md")
WP_REL = os.path.join("MECH", "BOARD_PORT_OPENING_S6_WORKPACKET.md")
PCB_REL = os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb")

APPEND_MARK = "<!-- ISS276-FRAME-CALIBER-APPEND -->"
MACH_BEGIN = "<!-- MACHINE-BLOCK-BEGIN -->"
MACH_END = "<!-- MACHINE-BLOCK-END -->"

SOM_REFS = ("J_SOM_P1", "J_SOM_P2", "J_SOM_P3", "J_SOM_P4")

# ★帧 id 的唯一权威 = `HW/PCB/BOARD_FRAME_CALIBER.md` §2 的 JSON 块 `cal:FRAMES` (ISS-274 · hw-lead)★
# ★本页与那个权威表【逐字对齐】⇒ 两边不得各用一套 (ISS-276 §5 的对齐要求)★
BENCH_FRAME = "B160x100"      # 帧: B160x100 = 160×100 台架板帧 (现役板)
LEGACY_FRAME = "F30A"         # 帧: F30A = 60×30 套A 帧 (MECH/BOARD_GEOM_30MM.md)
LEGACY_60x15_FRAME = "P60x15"  # 帧: P60x15 = 60×15 帧

# ★受保护 5 件 (ISS-276 派单 §③ 基线 · 2026-11-17 06:1x main 实测) ⇒ 跑前跑后必须逐字节不变 ★
PROTECTED = {
    os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb"): "611b869e13518c3c023fb178f91a0075",
    os.path.join("HW", "PCB", "demo_mainboard.kicad_pro"): "3e504d2be83152e337949723e909be1b",
    os.path.join("HW", "netlist_v1.csv"): "e06c1dd633566aa44732762c2ff99d1c",
    os.path.join("HW", "netlist_v1_pins.csv"): "287e7861a0d1007748d92d9fbecdd490",
    os.path.join("HW", "BOM_v1.csv"): "94642d07a69e8d60dd2af57f69b93607",
}

# ★帧标签词表 (C1 用) ⇒ 坐标行必须挂其中之一 ★
# ★★注意: 词表里只收【能指名道姓说出是哪一套坐标】的词; ★「帧:」这种光有标签没有名字的不算★ ★
FRAME_TOKENS = (
    "B160x100", "160x100-bench", "160x100", "160×100", "台架板",
    "F30A", "60x30-setA", "60x30", "60×30", "套 A", "套A",
    "P60x15", "60x15-setB", "60x15", "60×15",
    "帧无关", "两帧通用", "两套通用",
)

EDGE_KEEPOUT = 0.80          # 器件距板边 (MECH_BUDGET.md §5.1)
LED_REF = "D_LED_G"
RES_REF = "R_LED_G"
BODY_H = 2.54                # 座体高假设 (★F-8 [0数据]★, 与 BASE['jd_body_h'] 同值)


# ==================================================================================================
# ★只读 import 既有闸脚本 ⇒ 阈值零漂移 (★不写回、不改它★)
# ==================================================================================================
def load_s6():
    spec = importlib.util.spec_from_file_location("s6_readonly_iss276", S6_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)       # ★只执行模块顶层 (无副作用)★
    return mod


S6 = load_s6()
BASE = dict(S6.BASE)
TOL = dict(S6.TOL)
CRIT = S6.CRIT                          # 0.60 = 2 × TOL['fdm_part']
OPEN_X, OPEN_Y = S6.OPEN_X, S6.OPEN_Y  # 10.20 × 4.60 (检修口开口定档, SERVICE_PORT_ISS092 §4.1)


# ==================================================================================================
# 板文件只读解析 (焊盘带尺寸 ⇒ 铜箔外框; F.Fab 线段 ⇒ 座体外框)
# ==================================================================================================
PAD_RE = re.compile(
    r'\(pad\s+"([^"]*)"\s+(\S+)\s+(\S+)\s+\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)'
    r'(?:\s*\(size ([-\d.]+) ([-\d.]+)\))?')
FPLINE_RE = re.compile(
    r'\(fp_line\s*\n\s*\(start ([-\d.]+) ([-\d.]+)\)\s*\n\s*\(end ([-\d.]+) ([-\d.]+)\)')


def read_board(root: str) -> dict:
    """读 kicad_pcb ⇒ {refs, edge, pads, fab} (★只读, 一个字节不写★)"""
    path = os.path.join(root, PCB_REL)
    text = open(path, "r", encoding="utf-8").read()
    lines = text.split("\n")

    # ---- Edge.Cuts (中心线) ----
    xs, ys = [], []
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("(gr_line"):
            depth, j = 0, i
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
    edge = {"x0": min(xs), "x1": max(xs), "y0": min(ys), "y1": max(ys),
            "w": max(xs) - min(xs), "h": max(ys) - min(ys)} if xs else None

    # ---- footprints ----
    fps = {}
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
            m = re.search(r'\(property "Reference" "([^"]+)"', blk)
            if m:
                ref = m.group(1)
                at = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', blk)
                ox = float(at.group(1)) if at else 0.0
                oy = float(at.group(2)) if at else 0.0
                pads = []
                for pm in PAD_RE.finditer(blk):
                    num, ptype, shape, px, py, _rot, sx, sy = pm.groups()
                    try:
                        sx = float(sx) if sx else 0.0
                        sy = float(sy) if sy else 0.0
                    except (TypeError, ValueError):
                        sx = sy = 0.0
                    pads.append({"num": num, "type": ptype,
                                 "x": ox + float(px), "y": oy + float(py),
                                 "sx": sx, "sy": sy})
                fab = []
                for lm in FPLINE_RE.finditer(blk):
                    x1, y1, x2, y2 = lm.groups()
                    fab.append((ox + float(x1), oy + float(y1),
                                ox + float(x2), oy + float(y2)))
                fps[ref] = {"at": (ox, oy), "pads": pads, "fab": fab}
            i = j + 1
        else:
            i += 1
    return {"edge": edge, "fps": fps}


def copper_bbox(f: dict) -> tuple:
    ps = f["pads"]
    if not ps:
        return None
    return (min(p["x"] - p["sx"] / 2 for p in ps), max(p["x"] + p["sx"] / 2 for p in ps),
            min(p["y"] - p["sy"] / 2 for p in ps), max(p["y"] + p["sy"] / 2 for p in ps))


def fab_bbox(f: dict) -> tuple:
    fb = f["fab"]
    if not fb:
        return None
    xs = [v for t in fb for v in (t[0], t[2])]
    ys = [v for t in fb for v in (t[1], t[3])]
    return (min(xs), max(xs), min(ys), max(ys))


def rect_hits(rect, pad_list) -> int:
    """矩形与焊盘铜箔【逐 pad 相交】计数 (★不是「中心点落入」, 是真压住★)"""
    x0, x1, y0, y1 = rect
    n = 0
    for p in pad_list:
        px0, px1 = p["x"] - p["sx"] / 2, p["x"] + p["sx"] / 2
        py0, py1 = p["y"] - p["sy"] / 2, p["y"] + p["sy"] / 2
        if px0 < x1 and px1 > x0 and py0 < y1 and py1 > y0:
            n += 1
    return n


def rect_hits_per(rect, fps, refs) -> dict:
    out = {}
    for r in refs:
        f = fps.get(r)
        if f:
            out[r] = rect_hits(rect, f["pads"])
    return out


# ==================================================================================================
# 机器块 (MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md 里的 YAML 块)
# ==================================================================================================
def read_calib(root: str) -> dict:
    path = os.path.join(root, CALIB_REL)
    if not os.path.exists(path):
        raise SystemExit(f"[check_board_frame_coords] 找不到归一页: {path}")
    text = open(path, "r", encoding="utf-8").read()
    b = text.find(MACH_BEGIN)
    e = text.find(MACH_END)
    if b < 0 or e < 0:
        raise SystemExit("[check_board_frame_coords] 归一页缺机器块标记 "
                         f"({MACH_BEGIN} / {MACH_END})")
    seg = text[b:e]
    m = re.search(r"```yaml\n(.*?)\n```", seg, re.S)
    if not m:
        raise SystemExit("[check_board_frame_coords] 归一页机器块不是 ```yaml 围栏")
    import yaml
    data = yaml.safe_load(m.group(1))
    if not isinstance(data, dict):
        raise SystemExit("[check_board_frame_coords] 机器块顶层不是 dict")
    data["_text"] = text
    data["_machine_span"] = (text.find(MACH_BEGIN), text.find(MACH_END))
    return data


def read_wp_append(root: str) -> str:
    path = os.path.join(root, WP_REL)
    if not os.path.exists(path):
        return ""
    text = open(path, "r", encoding="utf-8").read()
    idx = text.find(APPEND_MARK)
    if idx < 0:
        return ""
    return text[idx:]


# ==================================================================================================
# C1 · 帧标签
# ==================================================================================================
NUM_RE = re.compile(r"[-+]?\d+\.\d+")


def _coord_lines(text: str, skip_spans=()) -> list:
    """坐标行 = 一行里出现 ≥2 个带小数点的数 (mm 口径) ⇒ 漏标帧标签即红"""
    out = []
    for i, line in enumerate(text.split("\n")):
        if any(s <= i + 1 <= e for s, e in skip_spans):
            continue
        if len(NUM_RE.findall(line)) >= 2:
            out.append((i + 1, line))
    return out


def _has_frame_token(line: str) -> bool:
    return any(tok in line for tok in FRAME_TOKENS)


_TBL_SEP_RE = re.compile(r"^\s*\|[\s:\-|]+\|\s*$")


def _is_context_anchor(lines, i):
    """帧上下文锚点 = 标题行 / 引用块行 / 表头行 (表头 = 以 | 开头且下一行是分隔行)"""
    line = lines[i]
    if line.lstrip().startswith("#"):
        return True
    if line.lstrip().startswith(">"):
        return True
    if line.lstrip().startswith("|"):
        if i + 1 < len(lines) and _TBL_SEP_RE.match(lines[i + 1]):
            return True
    return False


def _frame_source(lines, i):
    """★严口径: 一个坐标行的帧来源只能是【它自己】/【它所在表的表头】/【它上面最近的标题或引用块】★
    ★不允许「整节继承」—— 表头/标题没写帧 = 那张表/那段话里的坐标就是无主坐标 ⇒ 红★
    返回 (是否通过, 来源说明)"""
    line = lines[i]
    if _has_frame_token(line):
        return True, "本行"
    stripped = line.lstrip()
    if stripped.startswith("|"):
        # 表行 ⇒ 只认本表的表头
        j = i - 1
        while j >= 0:
            l = lines[j]
            if l.lstrip().startswith("|"):
                if j + 1 < len(lines) and _TBL_SEP_RE.match(lines[j + 1]):
                    return _has_frame_token(l), f"表头@第{j + 1}行"
            j -= 1
        return False, "无表头"
    if stripped.startswith(">"):
        # 引用块 ⇒ 认整个引用块 (同一段话)
        j = i
        while j >= 0 and lines[j].lstrip().startswith(">"):
            if _has_frame_token(lines[j]):
                return True, f"引用块@第{j + 1}行"
            j -= 1
        return False, "引用块无帧"
    # 普通正文 ⇒ 认上面最近的标题
    j = i - 1
    while j >= 0:
        if lines[j].lstrip().startswith("#"):
            return _has_frame_token(lines[j]), f"标题@第{j + 1}行"
        j -= 1
    return False, "无标题锚"


def check_c1(root: str, calib: dict) -> dict:
    errs = []
    # --- C1a 机器块: 每个 window 必须带 frame 且 frame 必须已声明 ---
    frames = {f["id"]: f for f in (calib.get("frames") or [])}
    for w in (calib.get("windows") or []):
        fid = w.get("frame")
        if not fid:
            errs.append(f"C1a 机器块窗口 '{w.get('key')}' 缺 frame 标签")
        elif fid not in frames:
            errs.append(f"C1a 机器块窗口 '{w.get('key')}' 的 frame='{fid}' 未在 frames[] 声明")
    for fid in frames:
        if not _has_frame_token(fid):
            errs.append(f"C1a frame id '{fid}' 本身不含可识别帧标签")

    # --- C1b 正文行: 坐标行必须挂帧标签 (本行 或 其所属的帧上下文: 标题 / 引用块 / 表头) ---
    text = calib["_text"]
    ms, me = calib["_machine_span"]
    line_s = text[:ms].count("\n") + 1
    line_e = text[:me].count("\n") + 1
    scopes = [("归一页", text, [(line_s, line_e)])]
    wp = read_wp_append(root)
    if wp:
        scopes.append(("工作包追加段", wp, []))
    else:
        errs.append("C1b 工作包里找不到追加段标记 " + APPEND_MARK)
    detail = []
    for name, scope_text, skip in scopes:
        lines = scope_text.split("\n")
        for i, line in enumerate(lines):
            if any(s <= i + 1 <= e for s, e in skip):
                continue
            if len(NUM_RE.findall(line)) < 2:
                continue
            ok, src = _frame_source(lines, i)
            if not ok:
                errs.append(f"C1b {name} 第 {i + 1} 行坐标组漏帧标签 ({src}): {line.strip()[:90]}")
                detail.append({"scope": name, "line": i + 1, "text": line.strip()[:90]})
    return {"ok": not errs, "errs": errs, "detail": detail,
            "frames": sorted(frames.keys()),
            "windows": [(w.get("key"), w.get("frame")) for w in (calib.get("windows") or [])]}


# ==================================================================================================
# C2 / C3 · 窗口 vs SoM 座
# ==================================================================================================
def check_c2(root: str, calib: dict, board: dict) -> dict:
    errs = []
    fps = board["fps"]
    som_pads = []
    for r in SOM_REFS:
        f = fps.get(r)
        if f:
            som_pads += f["pads"]
    rows = []
    for w in (calib.get("windows") or []):
        if w.get("frame") != BENCH_FRAME:
            continue
        r = w["rect"]
        rect = (float(r["x0"]), float(r["x1"]), float(r["y0"]), float(r["y1"]))
        n = rect_hits(rect, som_pads)
        per = rect_hits_per(rect, fps, SOM_REFS)
        rows.append({"key": w.get("key"), "kind": w.get("kind", "opening"),
                     "rect": rect, "som_hits": n, "per_ref": per})
        if n != 0:
            errs.append(f"C2 窗口 '{w.get('key')}' 压住 {n} 个 SoM 焊盘 {per}")
    if not rows:
        errs.append("C2 机器块里没有任何 frame=%s 的窗口" % BENCH_FRAME)
    return {"ok": not errs, "errs": errs, "rows": rows, "som_pads": len(som_pads)}


def check_c3(root: str, calib: dict, board: dict) -> dict:
    """负向断言: 60×30 套A 的旧矩形喂进现役板坐标 ⇒ 必须报出压住 N 个 SoM 焊盘"""
    errs = []
    fps = board["fps"]
    som_pads = []
    for r in SOM_REFS:
        f = fps.get(r)
        if f:
            som_pads += f["pads"]
    rows = []
    legacy = [w for w in (calib.get("windows") or []) if w.get("frame") != BENCH_FRAME]
    if not legacy:
        errs.append("C3 机器块里没有 60×30 套A 口径的旧矩形 ⇒ 负向断言无从喂")
    for w in legacy:
        r = w["rect"]
        rect = (float(r["x0"]), float(r["x1"]), float(r["y0"]), float(r["y1"]))
        n = rect_hits(rect, som_pads)
        per = rect_hits_per(rect, fps, SOM_REFS)
        rows.append({"key": w.get("key"), "frame": w.get("frame"), "rect": rect,
                     "som_hits": n, "per_ref": per})
        if n <= 0:
            errs.append(f"C3 负向断言失效: 旧矩形 '{w.get('key')}' 喂进现役板坐标后 "
                        f"压住 SoM 焊盘数 = {n} (应为 >0) ⇒ 「两套坐标不可代入」没被证明")
    return {"ok": not errs, "errs": errs, "rows": rows}


# ==================================================================================================
# C4 · 受保护 5 件 md5
# ==================================================================================================
def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_c4(root: str) -> dict:
    errs = []
    rows = []
    for rel, base in PROTECTED.items():
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            errs.append(f"C4 受保护件缺失: {rel}")
            continue
        got = md5_of(p)
        rows.append({"path": rel, "baseline": base, "got": got, "same": got == base})
        if got != base:
            errs.append(f"C4 受保护件被改: {rel} 基线 {base} ⇒ 现值 {got}")
    return {"ok": not errs, "errs": errs, "rows": rows}


# ==================================================================================================
# 现役板坐标系下的实算 (--compute)
# ==================================================================================================
def compute(root: str) -> dict:
    board = read_board(root)
    fps = board["fps"]
    edge = board["edge"]
    out = {"edge_cuts": edge}

    # ---- SoM 承载区 (三个口径都算, 免得又被当成一个数) ----
    som = {}
    for r in SOM_REFS:
        f = fps.get(r)
        if f:
            som[r] = {"origin": f["at"], "copper": copper_bbox(f), "fab": fab_bbox(f),
                      "pads": len(f["pads"])}
    cop = [s["copper"] for s in som.values()]
    fab = [s["fab"] for s in som.values()]
    out["som"] = {
        "per_ref": som,
        "copper_union": (min(b[0] for b in cop), max(b[1] for b in cop),
                         min(b[2] for b in cop), max(b[3] for b in cop)),
        "fab_union": (min(b[0] for b in fab), max(b[1] for b in fab),
                      min(b[2] for b in fab), max(b[3] for b in fab)),
    }
    cu = out["som"]["copper_union"]
    fu = out["som"]["fab_union"]
    out["som"]["copper_union_size"] = (cu[1] - cu[0], cu[3] - cu[2])
    out["som"]["fab_union_size"] = (fu[1] - fu[0], fu[3] - fu[2])
    out["som"]["conservative_union"] = (fu[0] - 0.05, fu[1] + 0.05, cu[2], cu[3])
    out["som"]["conservative_union_size"] = (fu[1] - fu[0] + 0.10, cu[3] - cu[2])

    # ---- 连接器实测 ----
    conns = {}
    for ref in ("J_DEBUG", "J_UART", LED_REF, RES_REF):
        f = fps.get(ref)
        if not f:
            continue
        conns[ref] = {"origin": f["at"], "copper": copper_bbox(f),
                      "npads": len(f["pads"]),
                      "pads": [(p["num"], round(p["x"], 3), round(p["y"], 3)) for p in f["pads"]]}
    out["connectors"] = conns
    jd, ju = conns.get("J_DEBUG"), conns.get("J_UART")
    if jd and ju:
        dx = jd["origin"][0] - ju["origin"][0]
        dy = jd["origin"][1] - ju["origin"][1]
        out["debug_uart_separation"] = {
            "dx": dx, "dy": dy, "straight": math.hypot(dx, dy),
            "note": "★ISS-267 F-7 写的 123.6mm = ΔX; 直线距离 = %.3fmm★" % math.hypot(dx, dy)}

    # ---- 开口 (现役板坐标) ----
    def opening(ref, body_w):
        f = fps[ref]
        ps = f["pads"]
        cx = sum(p["x"] for p in ps) / len(ps)
        cy = sum(p["y"] for p in ps) / len(ps)
        bx0, bx1 = cx - body_w / 2, cx + body_w / 2
        by0, by1 = cy - BODY_H / 2, cy + BODY_H / 2
        cl_x = (OPEN_X - body_w) / 2
        cl_y = (OPEN_Y - BODY_H) / 2
        return {
            "ref": ref, "center": (cx, cy), "body_w": body_w,
            "body": (bx0, bx1, by0, by1),
            "open": (bx0 - cl_x, bx1 + cl_x, by0 - cl_y, by1 + cl_y),
            "cl_x": cl_x, "cl_y": cl_y,
            "worst_cl_x": cl_x - TOL["fdm_part"], "worst_cl_y": cl_y - TOL["fdm_part"],
            "x0_range": (max(bx0 - cl_x, bx1 + cl_x - OPEN_X),
                         min(bx0, edge["x1"] - EDGE_KEEPOUT - OPEN_X)),
            "y0_range": (max(by0 - cl_y, by1 + cl_y - OPEN_Y),
                         min(by0, edge["y1"] - EDGE_KEEPOUT - OPEN_Y)),
        }

    jd_body_w = (jd["copper"][1] - jd["copper"][0]) if jd else 0.0
    o_jd = opening("J_DEBUG", jd_body_w)
    o_ju = opening("J_UART", 2.54)
    out["openings"] = {"J_DEBUG": o_jd, "J_UART": o_ju}

    # 合并开口 (MECH 现行模型) 可行性
    content_w = max(o_jd["body"][1], o_ju["body"][1]) - min(o_jd["body"][0], o_ju["body"][0])
    out["merged_opening"] = {
        "content_w": content_w,
        "open_w": OPEN_X,
        "cl_x": (OPEN_X - content_w) / 2,
        "gap": content_w - OPEN_X,
        "feasible": content_w <= OPEN_X,
        "note": "★合并开口 = 一个 10.20mm 开口同时罩 J_DEBUG + J_UART (MECH/BOARD_PORT_OPENING_S6_WORKPACKET.md §5.1 现行模型)★",
    }

    # ---- LED_G_D 走线独立复算 ----
    r = fps.get(RES_REF)
    d = fps.get(LED_REF)
    if r and d:
        rp = {p["num"]: p for p in r["pads"]}
        dp = {p["num"]: p for p in d["pads"]}
        p1, p2 = rp.get("2"), dp.get("1")
        if p1 and p2:
            dx = p2["x"] - p1["x"]
            dy = p2["y"] - p1["y"]
            out["led_gd"] = {
                "r_pad2": (p1["x"], p1["y"]), "d_pad1": (p2["x"], p2["y"]),
                "dx": dx, "dy": dy, "dist": math.hypot(dx, dy),
                "r_origin": r["at"], "d_origin": d["at"],
                "doc_claim": 93.49,
            }

    # ---- D_LED_G 可放行空间 (现役板坐标) ----
    out["led_space"] = led_space(board, out)
    # ★净距敏感度: 器件间铜箔净距 clr 变大 ⇒ 可放行空间变小、LED_G_D 走线变长 ★
    sweep = []
    for clr in (0.0, 0.10, 0.20, 0.50):
        sp = led_space(board, out, clr=clr)
        near = sp["nearest_to_r_led_g"][0] if sp["nearest_to_r_led_g"] else None
        sweep.append({"clearance": clr,
                      "n_placeable_bands": len(sp["placeable"]),
                      "n_full_height": len(sp["full_height_bands"]),
                      "nearest_origin": near["origin"] if near else None,
                      "led_gd_dist": near["dist"] if near else None})
    out["led_space_sweep"] = sweep
    return out


def led_space(board: dict, comp: dict, clr: float = 0.0) -> dict:
    """clr = 器件间最小铜箔净距 (mm)。★0.00 = 硬不重叠 (板 DRC min_clearance=0.0 的硬极限)★"""
    fps = board["fps"]
    edge = board["edge"]
    led = fps[LED_REF]
    lb = copper_bbox(led)
    lox, loy = led["at"]
    rel = (lb[0] - lox, lb[1] - lox, lb[2] - loy, lb[3] - loy)   # 相对封装原点的铜箔外框
    obst = []
    for ref, f in fps.items():
        if ref == LED_REF:
            continue
        b = copper_bbox(f)
        if b:
            obst.append((ref, b))
    for nm, o in (("OPEN_DEBUG", comp["openings"]["J_DEBUG"]),
                  ("OPEN_UART", comp["openings"]["J_UART"])):
        obst.append((nm, o["open"]))

    # 封装原点窗口 (边距带 0.80 ⇒ 铜箔外框不越界)
    ox0 = edge["x0"] + EDGE_KEEPOUT - rel[0]
    ox1 = edge["x1"] - EDGE_KEEPOUT - rel[1]
    oy0 = edge["y0"] + EDGE_KEEPOUT - rel[2]
    oy1 = edge["y1"] - EDGE_KEEPOUT - rel[3]

    # 沿 X 扫, 求每段可用的原点-Y 区间
    # ★器件占位相对封装原点 = rel = (rel[0], rel[1], rel[2], rel[3]) ⇒ 铜箔 = 原点+rel★
    #   ★原点 ox 处与障碍 [bx0,bx1] 相交 ⇔ ox + rel[1] > bx0 且 ox + rel[0] < bx1★
    #     ⇒ 挡住的原点区间 = (bx0 − rel[1], bx1 − rel[0])★
    #   ★Y 同理: 挡住的原点区间 = (by0 − rel[3], by1 − rel[2])★
    cuts = sorted({ox0, ox1}
                  | {b[1][0] - clr - rel[1] for b in obst}
                  | {b[1][1] + clr - rel[0] for b in obst})
    bands = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        if b - a <= 1e-9:
            continue
        xc = (a + b) / 2
        if not (ox0 <= xc <= ox1):
            continue
        ys = [(oy0, oy1)]
        for nm, (bx0, bx1, by0, by1) in obst:
            # 封装原点在 X 上落进被挡区间 ⇒ 该件被压住
            if not (bx0 - clr - rel[1] <= xc <= bx1 + clr - rel[0]):
                continue
            nxt = []
            for (y0, y1) in ys:
                if by1 + clr - rel[2] <= y0 or by0 - clr - rel[3] >= y1:
                    nxt.append((y0, y1))
                    continue
                if by0 - clr - rel[3] > y0:
                    nxt.append((y0, by0 - clr - rel[3]))
                if by1 + clr - rel[2] < y1:
                    nxt.append((by1 + clr - rel[2], y1))
            ys = nxt
        for (y0, y1) in ys:
            if y1 - y0 <= 1e-9:
                continue
            bands.append({"ox0": a, "ox1": b, "oy0": y0, "oy1": y1,
                          "w": b - a, "h": y1 - y0})
    merged = []
    for bd in bands:
        if merged and abs(merged[-1]["ox1"] - bd["ox0"]) < 1e-9 \
                and abs(merged[-1]["oy0"] - bd["oy0"]) < 1e-9 \
                and abs(merged[-1]["oy1"] - bd["oy1"]) < 1e-9:
            merged[-1]["ox1"] = bd["ox1"]
            merged[-1]["w"] = merged[-1]["ox1"] - merged[-1]["ox0"]
        else:
            merged.append(dict(bd))
    # 整高带 (OY 整段都在内)
    full = [b for b in merged
            if abs(b["oy0"] - oy0) < 1e-6 and abs(b["oy1"] - oy1) < 1e-6]
    # 落位点封装原点窗口 (可放行 ⇒ 该带内的原点位置)
    place = []
    for b in merged:
        px0 = max(b["ox0"], ox0)
        px1 = min(b["ox1"], ox1)
        py0 = max(b["oy0"], oy0)
        py1 = min(b["oy1"], oy1)
        if px1 - px0 > 1e-9 and py1 - py0 > 1e-9:
            place.append({"ox0": px0, "ox1": px1, "oy0": py0, "oy1": py1})
    # 距 R_LED_G 最近的落位原点 (⇒ LED_G_D 走线最短)
    rp = {p["num"]: p for p in fps[RES_REF]["pads"]}
    r2 = rp.get("2")
    near = []
    near_band = None
    if r2:
        for b in place:
            for (px, py) in ((b["ox0"], b["oy0"]), (b["ox1"], b["oy0"]),
                             (b["ox0"], b["oy1"]), (b["ox1"], b["oy1"]),
                             ((b["ox0"] + b["ox1"]) / 2, (b["oy0"] + b["oy1"]) / 2)):
                d = math.hypot(px + rel[0] - r2["x"], py + rel[2] - r2["y"])
                near.append((d, px, py, b))
        near.sort(key=lambda z: z[0])
        if near:
            near_band = {"ox0": near[0][3]["ox0"], "ox1": near[0][3]["ox1"],
                         "oy0": near[0][3]["oy0"], "oy1": near[0][3]["oy1"]}
    return {
        "clearance": clr,
        "led_origin": led["at"],
        "led_copper": lb,
        "led_rel_bbox": rel,
        "origin_window": (ox0, ox1, oy0, oy1),
        "bands": merged,
        "full_height_bands": full,
        "placeable": place,
        "nearest_to_r_led_g": [{"dist": round(d, 6), "origin": (px, py)} for d, px, py, _ in near[:5]],
        "nearest_band": near_band,
        "r_led_g_pad2": (r2["x"], r2["y"]) if r2 else None,
    }


# ==================================================================================================
# 自检 (★五条反向用例, 一条不许删★) —— 一律在【沙盒副本】上跑, 不许碰真件
# ==================================================================================================
def sandbox_base(root: str) -> str:
    """沙盒目录 = <workspace>/tmp/... (★不许用 /tmp, 配额紧张★)"""
    env = os.environ.get("MECH_SANDBOX_DIR")
    if env:
        return env
    return os.path.abspath(os.path.join(root, "..", "..", "tmp", "iss276_frame_selftest"))


def make_sandbox(root: str, tag: str) -> str:
    base = sandbox_base(root)
    dst = os.path.join(base, tag)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)
    for rel in (PCB_REL, CALIB_REL, WP_REL):
        src = os.path.join(root, rel)
        if os.path.exists(src):
            d = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(src, d)
    for rel in PROTECTED:
        src = os.path.join(root, rel)
        if os.path.exists(src):
            d = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(src, d)
    return dst


def run_checks(root: str) -> dict:
    calib = read_calib(root)
    board = read_board(root)
    c1 = check_c1(root, calib)
    c2 = check_c2(root, calib, board)
    c3 = check_c3(root, calib, board)
    c4 = check_c4(root)
    return {"C1": c1, "C2": c2, "C3": c3, "C4": c4}


def selftest(root: str) -> int:
    errs = []
    print("=" * 96)
    print("【自检】check_board_frame_coords.py 反向用例 (★沙盒副本上跑, 真件一个字节不碰★)")
    print("=" * 96)
    base = run_checks(root)
    print(f"  [基线] C1={'OK' if base['C1']['ok'] else 'NG'} "
          f"C2={'OK' if base['C2']['ok'] else 'NG'} "
          f"C3={'OK' if base['C3']['ok'] else 'NG'} "
          f"C4={'OK' if base['C4']['ok'] else 'NG'}")
    if not all(base[k]["ok"] for k in ("C1", "C2", "C3", "C4")):
        errs.append("基线就不绿 ⇒ 自检无意义")

    calib_path = os.path.join(root, CALIB_REL)

    # ---- ① 改窗口一个角 ⇒ C2 红 ----
    sb = make_sandbox(root, "case1_move_corner")
    p = os.path.join(sb, CALIB_REL)
    t = open(p, encoding="utf-8").read()
    before = md5_of(p)
    t2 = t.replace("x0: 137.850", "x0: 13.650", 1)
    if t2 == t:
        errs.append("① 没能改到窗口角点 (模式未命中)")
    open(p, "w", encoding="utf-8").write(t2)
    r1 = run_checks(sb)
    c2_red = not r1["C2"]["ok"]
    print(f"  [{'OK ' if c2_red else 'NG '}] ① 改窗口一个角 (x0 137.850 ⇒ 13.650) ⇒ C2 红: "
          f"{'是' if c2_red else '否'} · md5 {before[:8]} ⇒ {md5_of(p)[:8]} · "
          f"C2 命中数={[(x['key'], x['som_hits']) for x in r1['C2']['rows']]}")
    if not c2_red:
        errs.append("① 改窗口角点后 C2 没红")

    # ---- ② 抽帧标签 ⇒ C1 红 ----
    sb = make_sandbox(root, "case2_strip_tag")
    p = os.path.join(sb, CALIB_REL)
    t = open(p, encoding="utf-8").read()
    before = md5_of(p)
    # ★抽掉 §3.3 那张表的表头帧标签 (只改第一处) ⇒ 该表内坐标变成「无主坐标」★
    t2 = t.replace("| 项 | 值 (帧: **160×100 台架板**) |",
                   "| 项 | 值 (档位已抽) |", 1)
    if t2 == t:
        errs.append("② 没能抽掉帧标签")
    open(p, "w", encoding="utf-8").write(t2)
    r2 = run_checks(sb)
    c1_red = not r2["C1"]["ok"]
    print(f"  [{'OK ' if c1_red else 'NG '}] ② 抽掉一张表的表头帧标签 ⇒ C1 红: "
          f"{'是' if c1_red else '否'} · md5 {before[:8]} ⇒ {md5_of(p)[:8]} · "
          f"C1 错误 {len(r2['C1']['errs'])} 条")
    if not c1_red:
        errs.append("② 抽帧标签后 C1 没红")

    # ---- ③ 把窗口挪进 SoM 区 ⇒ C2 红 ----
    sb = make_sandbox(root, "case3_move_into_som")
    p = os.path.join(sb, CALIB_REL)
    t = open(p, encoding="utf-8").read()
    before = md5_of(p)
    t2 = t.replace("x0: 137.850", "x0: 20.000", 1).replace("y0: 54.300", "y0: 8.000", 1)
    if t2 == t:
        errs.append("③ 没能把窗口挪进 SoM 区")
    open(p, "w", encoding="utf-8").write(t2)
    r3 = run_checks(sb)
    c2_red3 = not r3["C2"]["ok"]
    print(f"  [{'OK ' if c2_red3 else 'NG '}] ③ 把窗口挪进 SoM 区 (x0 20.000 / y0 8.000) ⇒ C2 红: "
          f"{'是' if c2_red3 else '否'} · md5 {before[:8]} ⇒ {md5_of(p)[:8]} · "
          f"C2 命中数={[(x['key'], x['som_hits']) for x in r3['C2']['rows']]}")
    if not c2_red3:
        errs.append("③ 窗口挪进 SoM 区后 C2 没红")

    # ---- ④ 把旧 60×30 矩形当新坐标喂 ⇒ C3 必须报出压住焊盘数 ----
    sb = make_sandbox(root, "case4_legacy_as_new")
    p = os.path.join(sb, CALIB_REL)
    t = open(p, encoding="utf-8").read()
    before = md5_of(p)
    # ④a: 把旧的检修口矩形登记成【现役板窗口】⇒ 当成新坐标用 ⇒ 必须被 C2 抓住 (56 个 SoM 焊盘)
    t2 = t.replace('frame: "%s"' % LEGACY_FRAME, 'frame: "%s"' % BENCH_FRAME, 1)
    changed = t2 != t
    open(p, "w", encoding="utf-8").write(t2)
    r4 = run_checks(sb)
    rows4 = [(x["key"], x["som_hits"]) for x in r4["C3"]["rows"]]
    c2_rows = {x["key"]: x["som_hits"] for x in r4["C2"]["rows"]}
    fed = c2_rows.get("legacy_port_open_60x30")
    c3_ok = r4["C3"]["ok"] and all(n > 0 for _, n in rows4)
    caught = (fed is not None and fed > 0) and not r4["C2"]["ok"]
    print(f"  [{'OK ' if (changed and c3_ok and caught) else 'NG '}] ④a 把旧 60×30 矩形当现役板坐标喂 ⇒ "
          f"C3 报出压住焊盘数 {rows4} · C2 抓到旧矩形压住 SoM **{fed}** 个 (C2 红={not r4['C2']['ok']}) · "
          f"改动生效={changed} · md5 {before[:8]} ⇒ {md5_of(p)[:8]}")
    if not (changed and c3_ok and caught):
        errs.append("④a 旧矩形喂进现役坐标后 C3/C2 没报出压住焊盘数")

    # ④b: 把旧矩形挪到不压 SoM 的位置 ⇒ C3 必须红并报出 N=0 ⇒ 证明 C3 的数是从板算的, 不是写死的
    sb = make_sandbox(root, "case4b_legacy_moved_away")
    p = os.path.join(sb, CALIB_REL)
    t = open(p, encoding="utf-8").read()
    before = md5_of(p)
    t2 = t.replace("x0: 47.000, x1: 60.000", "x0: 120.000, x1: 133.000", 1)
    moved = t2 != t
    open(p, "w", encoding="utf-8").write(t2)
    r4b = run_checks(sb)
    rows4b = [(x["key"], x["som_hits"]) for x in r4b["C3"]["rows"]]
    c3_red = not r4b["C3"]["ok"]
    zero_reported = any(k == "legacy_port_open_60x30" and n == 0 for k, n in rows4b)
    print(f"  [{'OK ' if (moved and c3_red and zero_reported) else 'NG '}] ④b 把旧矩形挪到不压 SoM 处 ⇒ "
          f"C3 红={c3_red} · 报出 {rows4b} · 改动生效={moved} · md5 {before[:8]} ⇒ {md5_of(p)[:8]}")
    if not (moved and c3_red and zero_reported):
        errs.append("④b 旧矩形挪开后 C3 没红 / 没报出 N=0 ⇒ C3 的数可能是写死的")

    # ---- ⑤ 改受保护件 ⇒ C4 红 ----
    sb = make_sandbox(root, "case5_touch_protected")
    p = os.path.join(sb, os.path.join("HW", "PCB", "demo_mainboard.kicad_pro"))
    before = md5_of(p)
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n")
    r5 = run_checks(sb)
    c4_red = not r5["C4"]["ok"]
    print(f"  [{'OK ' if c4_red else 'NG '}] ⑤ 改受保护件 (.kicad_pro 追加 1 字节) ⇒ C4 红: "
          f"{'是' if c4_red else '否'} · md5 {before[:8]} ⇒ {md5_of(p)[:8]} · "
          f"C4 错误 {len(r5['C4']['errs'])} 条")
    if not c4_red:
        errs.append("⑤ 改受保护件后 C4 没红")

    # ---- ⑥ 沙盒自证: 真件一个字节没动 ----
    same = all(md5_of(os.path.join(root, rel)) == base_md5 for rel, base_md5 in PROTECTED.items())
    print(f"  [{'OK ' if same else 'NG '}] ⑥ 真件 5 件 md5 跑完自检后仍逐字节不变: "
          f"{'是' if same else '否'}")
    if not same:
        errs.append("⑥ 自检过程把真件改了")

    print("=" * 96)
    print(f"【自检结论】{'✅ 一致' if not errs else '❌ 不一致 —— ' + '; '.join(errs)}")
    return 0 if not errs else 2


# ==================================================================================================
# 打印
# ==================================================================================================
def hr(t):
    print("\n" + "=" * 96)
    print(t)
    print("=" * 96)


def print_checks(res):
    hr("【闸】ISS-276 坐标系闸 (C1 帧标签 / C2 不压 SoM / C3 负向断言 / C4 受保护 5 件)")
    for k in ("C1", "C2", "C3", "C4"):
        c = res[k]
        print(f"\n--- {k} --- {'✅ 过' if c['ok'] else '❌ 判红'}")
        if k == "C1":
            print(f"   已声明帧: {c['frames']}")
            print(f"   窗口→帧: {c['windows']}")
        elif k == "C2":
            print(f"   SoM 焊盘总数 (P1..P4): {c['som_pads']}")
            for r in c["rows"]:
                print(f"   窗口 '{r['key']}' ({r['kind']}) X {r['rect'][0]:.3f}..{r['rect'][1]:.3f} "
                      f"× Y {r['rect'][2]:.3f}..{r['rect'][3]:.3f} ⇒ 压住 SoM 焊盘 = "
                      f"**{r['som_hits']}** {r['per_ref']}")
        elif k == "C3":
            for r in c["rows"]:
                print(f"   旧矩形 '{r['key']}' (帧 {r['frame']}) 喂进现役板坐标 ⇒ 压住 SoM 焊盘 "
                      f"= **{r['som_hits']}** {r['per_ref']}")
            print("   ⇒ ★两套坐标不可代入: 已机器化证明 (旧矩形一旦被当现役坐标用 ⇒ 立刻压 SoM 座)★")
        elif k == "C4":
            for r in c["rows"]:
                print(f"   {'✅' if r['same'] else '❌'} {r['path']} 基线 {r['baseline']} ⇒ 现值 {r['got']}")
        for e in c["errs"]:
            print(f"   ❌ {e}")


def print_compute(comp):
    hr("【实算】现役 160×100 台架板坐标系 (★全部读盘上板文件, 不抄任何文档数★)")
    e = comp["edge_cuts"]
    print(f"   Edge.Cuts 中心线包围盒: X {e['x0']:.2f}..{e['x1']:.2f} × Y {e['y0']:.2f}..{e['y1']:.2f} "
          f"⇒ {e['w']:.2f} × {e['h']:.2f} mm (stroke 0.1 ⇒ 外缘 {e['w'] + 0.1:.2f} × {e['h'] + 0.1:.2f})")
    s = comp["som"]
    print(f"\n   SoM 承载区 (J_SOM_P1..P4, 各 100 焊盘 = 400 焊盘):")
    print(f"      焊盘铜箔并集: X {s['copper_union'][0]:.3f}..{s['copper_union'][1]:.3f} "
          f"({s['copper_union_size'][0]:.2f}) × Y {s['copper_union'][2]:.3f}..{s['copper_union'][3]:.3f} "
          f"({s['copper_union_size'][1]:.2f})")
    print(f"      座体 F.Fab 并集: X {s['fab_union'][0]:.3f}..{s['fab_union'][1]:.3f} "
          f"({s['fab_union_size'][0]:.2f}) × Y {s['fab_union'][2]:.3f}..{s['fab_union'][3]:.3f} "
          f"({s['fab_union_size'][1]:.2f})")
    print(f"      保守包络(座体±0.05): X {s['conservative_union'][0]:.3f}..{s['conservative_union'][1]:.3f} "
          f"({s['conservative_union_size'][0]:.2f}) × Y {s['conservative_union'][2]:.3f}..{s['conservative_union'][3]:.3f} "
          f"({s['conservative_union_size'][1]:.2f})")
    print(f"      ⇒ ★Y 向 {s['copper_union_size'][1]:.2f}mm > 30 (60×30 板宽) 且 > 15 (60×15 板宽) "
          f"⇒ 现役 SoM 承载区【物理上装不进】60×30 / 60×15★")
    print(f"\n   连接器实测:")
    for ref, c in comp["connectors"].items():
        print(f"      {ref:<10} 原点 ({c['origin'][0]:.2f},{c['origin'][1]:.2f}) · {c['npads']} 焊盘 · "
              f"铜箔 X {c['copper'][0]:.3f}..{c['copper'][1]:.3f} × Y {c['copper'][2]:.3f}..{c['copper'][3]:.3f}")
    if "debug_uart_separation" in comp:
        d = comp["debug_uart_separation"]
        print(f"      ★J_DEBUG ↔ J_UART: ΔX {d['dx']:.2f} · ΔY {d['dy']:.2f} · 直线 {d['straight']:.3f} mm")
    print(f"\n   开口 (现役板坐标 · 开口定档 {OPEN_X:.2f} × {OPEN_Y:.2f} · 座体高 {BODY_H:.2f} 假设):")
    for ref, o in comp["openings"].items():
        print(f"      {ref:<9} 必须清空 X {o['body'][0]:.3f}..{o['body'][1]:.3f} × Y {o['body'][2]:.3f}..{o['body'][3]:.3f}")
        print(f"      {'':<9} 开口 X {o['open'][0]:.3f}..{o['open'][1]:.3f} × Y {o['open'][2]:.3f}..{o['open'][3]:.3f} "
              f"· 单边间隙 X {o['cl_x']:.3f}/Y {o['cl_y']:.3f} (最坏 {o['worst_cl_x']:.3f}/{o['worst_cl_y']:.3f} ≥ {CRIT:.2f})")
        print(f"      {'':<9} 开口左下角可放行区间 X0 ∈ [{o['x0_range'][0]:.3f}, {o['x0_range'][1]:.3f}] · "
              f"Y0 ∈ [{o['y0_range'][0]:.3f}, {o['y0_range'][1]:.3f}]")
    m = comp["merged_opening"]
    print(f"\n   ★合并开口 (一个 10.20 开口同时罩 J_DEBUG + J_UART): 必须清空宽 {m['content_w']:.3f} "
          f"⇒ 单边间隙 {m['cl_x']:.3f} ⇒ {'可行' if m['feasible'] else '❌ 不可行 (差 %.3fmm)' % m['gap']}")
    if "led_gd" in comp:
        g = comp["led_gd"]
        print(f"\n   ★LED_G_D 走线独立复算: R_LED_G.2 ({g['r_pad2'][0]:.2f},{g['r_pad2'][1]:.2f}) ↔ "
              f"D_LED_G.1 ({g['d_pad1'][0]:.2f},{g['d_pad1'][1]:.2f}) ⇒ Δx {g['dx']:.2f} / Δy {g['dy']:.2f} "
              f"⇒ 直线 {g['dist']:.6f} mm (文档 93.49 ⇒ 差 {g['dist'] - g['doc_claim']:+.6f})")
    ls = comp["led_space"]
    print(f"\n   ★D_LED_G 可放行空间 (现役板坐标系 · 零重叠判据 · 边距带 {EDGE_KEEPOUT:.2f}):")
    print(f"      落地封装原点 {ls['led_origin']} · 铜箔 X {ls['led_copper'][0]:.3f}..{ls['led_copper'][1]:.3f} "
          f"× Y {ls['led_copper'][2]:.3f}..{ls['led_copper'][3]:.3f} "
          f"(相对原点 {ls['led_rel_bbox'][0]:+.2f}..{ls['led_rel_bbox'][1]:+.2f} / "
          f"{ls['led_rel_bbox'][2]:+.2f}..{ls['led_rel_bbox'][3]:+.2f})")
    print(f"      原点窗口: X {ls['origin_window'][0]:.3f}..{ls['origin_window'][1]:.3f} · "
          f"Y {ls['origin_window'][2]:.3f}..{ls['origin_window'][3]:.3f}")
    print(f"      整高自由带 (X 向, Y 整段都在内): {len(ls['full_height_bands'])} 条")
    for b in ls["full_height_bands"]:
        print(f"         X {b['ox0']:.3f}..{b['ox1']:.3f} (宽 {b['w']:.3f})")
    print(f"      距 R_LED_G.2 ({ls['r_led_g_pad2'][0]:.2f},{ls['r_led_g_pad2'][1]:.2f}) 最近的落位原点:")
    for n in ls["nearest_to_r_led_g"]:
        print(f"         d = {n['dist']:.3f} mm @ 原点 ({n['origin'][0]:.3f},{n['origin'][1]:.3f})")
    if ls.get("nearest_band"):
        nb = ls["nearest_band"]
        print(f"      ★最近落位带 (封装原点可放行窗口): X {nb['ox0']:.3f}..{nb['ox1']:.3f} · "
              f"Y {nb['oy0']:.3f}..{nb['oy1']:.3f}")
    print(f"      ★净距敏感度 (器件间铜箔净距 clr ⇒ 可落位带数 / 最近落位原点 / LED_G_D 直线长):")
    for s in comp.get("led_space_sweep", []):
        no = s["nearest_origin"]
        no_s = "(%.3f, %.3f)" % (no[0], no[1]) if no else "—"
        d_s = ("%.3f mm" % s["led_gd_dist"]) if s["led_gd_dist"] is not None else "无解"
        print(f"         clr {s['clearance']:.2f} ⇒ 可落位带 {s['n_placeable_bands']:>3} 条 · "
              f"整高 {s['n_full_height']} 条 · 最近原点 {no_s} · LED_G_D = {d_s}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT, help="工程根目录 (默认 = 本脚本上两级)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--compute", action="store_true")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.selftest:
        return selftest(root)

    if args.compute:
        comp = compute(root)
        if args.json:
            print(json.dumps(comp, ensure_ascii=False, indent=2, default=float))
        else:
            print_compute(comp)
        return 0

    res = run_checks(root)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2, default=float))
    else:
        print("=" * 96)
        print("BOARD FRAME COORDS CHECK —— ISS-276 (mech-lead)")
        print("=" * 96)
        print(f"★口径: 现役台架板 160×100 (Edge.Cuts 实读) ★")
        print_checks(res)
        allok = all(res[k]["ok"] for k in ("C1", "C2", "C3", "C4"))
        print("\n" + "=" * 96)
        print(f"【结论】{'✅ 四项全过' if allok else '❌ 有检查项判红'}")
        print("口径提醒: 盘上板读数 = [实测] (读得到才写) · 设计态几何 = [推算] · 实物 [实测] = 0 条")
    return 0 if all(res[k]["ok"] for k in ("C1", "C2", "C3", "C4")) else 2


if __name__ == "__main__":
    sys.exit(main())
