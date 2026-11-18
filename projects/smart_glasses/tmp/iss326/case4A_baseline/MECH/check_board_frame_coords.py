#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_board_frame_coords.py —— ISS-276 「板只改一次」那一趟的【坐标系闸】 (mech-lead)
=================================================================================================
干什么:
  ① **C1 帧标签**: 本单/工作包里出现的每个坐标组都必须带帧标签 ⇒ **漏标一条即红**
  ② **C2 归一后窗口不压 SoM 座**: 读板 ⇒ §3/§4 给的开口矩形与 LED 窗口 ⇒ **压住
     `ZZ_COMMENT_PROBE_1..P4` 焊盘数必须 = 0**
  ③ **C3 两套坐标不可代入 (负向断言)**: 把 60×30 套A 口径的旧矩形喂进现役板坐标
     ⇒ **必须报出「压住了 N 个 SoM 焊盘」而不是静默通过**
  ④ **C4 受保护件 md5 前后逐字节不变** (★ISS-286 改判据口径★):
     - 网表 / 脚表 / BOM 3 件 ⇒ ★**判决源 = 落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md`
       里该文件的最新落表记录 (链头)**★ ⇒ 合法落表 ⇒ 链头自动前移 ⇒ 绿
       (★病根 = 判决源选错了, 不是真源被改了 ⇒ 修法落在【取值来源】上★)
     - 板 / `.kicad_pro` 2 件 ⇒ ★★【ISS-296】走【合法改板】通道★★ (★不是「基线写死一票否决」★)
       ⇒ 板那一趟合法改板一次 ⇒ 台账落一行 ⇒ 链头前移 ⇒ 绿 ⇒ ★**假红被消掉, 板白改第二遍这条路被堵死**★

★★【ISS-296 · 2026-11-17 · mech-lead】★★ 板 / `.kicad_pro` 的「合法改板」通道 (★照 SW 侧 ISS-284 已 verified 的形状★)
  ① 背景: 「板只改一次」那一趟**授权**板合法改一次 ⇒ 板 md5 会合法地变 ⇒ 而 C4 把板 md5
     写死成「硬保护基线」⇒ 那一趟改完板 C4 **必假红** ⇒ ⇒ 假红在收工验收时会被读成
     「板改坏了」⇒ ⇒ 有人去「改板凑绿」⇒ ⇒ **板白改第二遍** (最坏 = 把 `C_VBUS_GND`
     装回板上, ISS-289 点名的 2-4 周 + ¥4-8K) ★
  ② ★**所以不能只是「把基线改个数」** ⇒ 那是「悄悄换真源」(ISS-273/275 花大力气堵掉的洞)
     ⇒ 必须做成【一个由单号背书的显式动作】★
  ③ ★**MECH 侧不新造第二个可手改的 md5 字段** ⇒ ★**判决源 = 落表台账链头** ⇒
     ★**一条合法改板记录 = 落表台账【一行】(单号 by | 文件名 file | 改前 md5 prev_md5 |
     改后 md5 md5) 四项捆在同一个原子行里** ★ ⇒ 追加一次 = 原子一次 ⇒
     ★**不存在两个可各自独立编辑的字段** ⇒ 比 SW 侧少一个可被挖的坑 = 更严 ★
  ④ 判据 (照 SW 侧 ISS-284 的四条, **一条都不许放宽**):
     - ① **保护基线自证**: 闸里写死的保护基线 md5 必须能在落表台账里与该文件【同行】查到
       ⇒ ★**只改闸里的基线而台账没记 ⇒ 判红** ★
     - ② **台账里没有变更行** ⇒ 不许有合法改板记录; 且 **盘上 md5 必须 == 基线**
       (★纯 md5 硬保护, 一条不许放松★)
     - ③ **台账里有变更行** ⇒ **链头唯一 / 链不断 / 链头有单号** (★fail-closed 三条一条不许动★)
       + 链头那一行的**四项**必须齐全且与链头**逐字对上** + **保护基线必须留在链尾**
       (★不许把基线偷偷前移★) + **盘上 md5 必须 == 台账链头** (★判据方向不许变★)
     - ④ **同组受保护件成对覆盖**: 一次合法改板必须覆盖同组全部件 (板 + `.kicad_pro`
       只来一条 ⇒ 判红)
  ⑤ ★**同源机器证明**: MECH 侧台账解析器与 SW 侧解析器对同一份台账读出的【链头 / 链 /
     产出单号】必须**逐字相同** ⇒ `logs/iss296/probe_ledger_reading_same_source.py`
     (★照 ISS-288 先例 `logs/iss288/probe_netlist_reading.py`★) ⇒ 不相同 ⇒ 判红 ★

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
  python3 MECH/check_board_frame_coords.py --selftest   ⇒ 反向用例 (★原有 5 条一条不许少
                                                  + ISS-286 新增 ⑦~⑪ 5 条台账口径用例
                                                  + ISS-296 新增 ⑫~⑰ 6 条合法改板用例★)

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

# ★受保护 2 件 (★真·不许变 ⇒ 基线写死★ · ISS-276 派单 §③ 基线 · 2026-11-17 06:1x main 实测)
#   ⇒ 跑前跑后必须逐字节不变 ★
#   ★★【ISS-286 · 2026-11-17】★★ 原先这里是 5 件 (板 / `.kicad_pro` + 网表 / 脚表 / BOM 三件写死 md5)
#   ★★⇒ 网表 / 脚表 / BOM 三件【移出】写死基线, 改走【落表台账链头】(见下面 PROTECTED_LEDGER)★★
#   ★★【ISS-296 · 2026-11-17】★★ 板 / `.kicad_pro` 这两件的**基线值一个字都没改** (★基线永远不许改★)
#   ★★⇒ 改的是【判决源】: 不再是「盘上 == 写死基线 一票否决」, 而是
#   ★★【落表台账链头 + 合法改板通道】(见下面 check_hard_protected_legal_reboard) ★★
#   ★★⇒ 「只改闸里的基线而台账没记」仍然判红 (★基线自证★) ⇒ 悄悄换真源这条路照样堵死 ★★
PROTECTED = {
    os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb"): "611b869e13518c3c023fb178f91a0075",
    os.path.join("HW", "PCB", "demo_mainboard.kicad_pro"): "3e504d2be83152e337949723e909be1b",
}

# ★★【ISS-286 · 2026-11-17】★★ 台账管理的 3 件真源 (网表 / 脚表 / BOM)
#   ★病根 = 【判决源选错了】(不是真源被改了) ⇒ 修法必须落在【取值来源】上, 不许只改【取值】★
#   ★先例 = ISS-273 (MECH 侧同构 · 已 verified) / ISS-275 (SW 侧同构 · 已 verified)★
#   ★口径照抄 MECH/check_demo_struct_truth.py 的 ledger_records / ledger_state
#     (★只读参照 · 本单一个字不改那个脚本★)★
LEDGER_CANON = "HW/SCHEMATIC_LANDING_V1_LANDED.md"
LEDGER_MD_RE = re.compile(r"\b[0-9a-f]{32}\b|\b[0-9a-f]{12}\b")
PROTECTED_LEDGER = (
    os.path.join("HW", "netlist_v1.csv"),
    os.path.join("HW", "netlist_v1_pins.csv"),
    os.path.join("HW", "BOM_v1.csv"),
)

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
# ★★落表台账判决源 (ISS-286) ★★ —— ★口径照抄 ISS-273 先例 (MECH/check_demo_struct_truth.py)★
#   ★★那个脚本本单一个字不改 (只读参照) · 这里只把它的两个函数搬过来, 行为一致★★
#   链头 = 「不是任何记录的前驱」的那个改后 md5 ⇒ ★判最新靠【图】不靠【行序】★
#     ⇒ 台账行序被打乱也不影响判定 ⇒ 「取错记录造成假绿」这条路被堵死 ★
# ==================================================================================================
def ledger_records(text: str, rel: str) -> list:
    """从落表台账文本里抽出 rel 的落表记录 ⇒ [{'prev','new','iss','sec','row'}] (★行序无关★)。"""
    out = []
    ctx_iss = None          # ★最近的带单号标题 ⇒ 批次单号 (行里没写单号时继承它)
    title = "(文首)"
    base = os.path.basename(rel)
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("#"):
            title = s
            hit = re.findall(r"ISS-\d+", s)
            if hit:
                ctx_iss = hit[0]
            continue
        if not s.startswith("|"):
            continue
        if rel not in s and base not in s:
            continue
        tk = LEDGER_MD_RE.findall(s)
        if len(tk) < 2:
            continue            # ★只有一个 md5 ⇒ 不是「改前→改后」记录行
        row_iss = re.findall(r"ISS-\d+", s)
        out.append({"prev": tk[0][:12], "new": tk[-1][:12],
                    "iss": row_iss[0] if row_iss else ctx_iss,
                    "sec": title, "row": s[:140]})
    return out


def ledger_state(rel: str, text: str, recs=None) -> dict:
    """算该受管真源在台账里的链头 / 链 / 产出单号表 (★取不准就返回 head=None ⇒ 判红★)。

    ★★【ISS-296】`recs` 可外传 ⇒ 合法改板通道用【只含改前≠改后的变更行】算链
      (★受管真源那条链的读数一字未变★) ★
    """
    if recs is None:
        recs = ledger_records(text, rel)
    new_keys = {r["new"] for r in recs}
    prev_keys = {r["prev"] for r in recs}
    heads = sorted(new_keys - prev_keys)
    producer = {}
    for r in recs:
        producer.setdefault(r["new"], set())
        if r["iss"]:
            producer[r["new"]].add(r["iss"])
    why = ""
    head = None
    if not recs:
        why = "台账里一条记录都没有"
    elif not heads:
        why = "没有链头 (每条记录都是别人的前驱 ⇒ 台账不成链)"
    elif len(heads) > 1:
        why = f"链头不唯一 = {heads} (取不准 ⇒ 不许判绿)"
    else:
        head = heads[0]
    chain = []
    if head:
        by_new = {}
        for r in recs:
            by_new.setdefault(r["new"], []).append(r)
        cur, seen = head, {head}
        chain = [head]
        while True:
            rs = by_new.get(cur) or []
            if not rs:
                break                       # 链尾 (起源值, 没有产出记录)
            prevs = {r["prev"] for r in rs if r["prev"] != r["new"]}
            if len(prevs) != 1:
                why = why or f"链上 {cur} 的前驱不唯一 = {sorted(prevs)}"
                chain = []
                break
            p = prevs.pop()
            if p in seen:
                why = why or f"链成环 ({p})"
                chain = []
                break
            cur = p
            seen.add(cur)
            chain.append(cur)
    return {"records": recs, "head": head, "chain": chain,
            "producer": producer, "why": why,
            "head_iss": sorted(producer.get(head, set())) if head else [],
            "known": new_keys | prev_keys}


# ==================================================================================================
# ★★【ISS-296 · 2026-11-17 · mech-lead】★★ 合法改板通道 (★照 SW 侧 ISS-284 已 verified 的形状★)
#   ★★口径来源: `SW/tools/check_demo_panel_spec.py` 的 `sw_ledger_cover_rows` /
#     `sw_ledger_change_rows` / `sw_ledger_change_state` / `check_r6_hard_protected`
#     (★那个脚本是 ISS-284 的定版闸 · 本单只【读它的形状】+ 在自己的探针里读它的解析器★
#      · 一个字不许改它★) ★★
#   ★★同源机器证明: `logs/iss296/probe_ledger_reading_same_source.py`
#     (★MECH 解析器 vs SW 解析器 对同一份台账读出的链头/链/产出单号必须逐字相同★) ★★
# ==================================================================================================
# ★★一条合法改板记录 = 【单号 by + 文件名 file + 改前 md5 prev_md5 + 改后 md5 md5】★★
#   ★★MECH 侧这四项**捆在落表台账的一行里** (追加一次 = 原子一次) ⇒
#   ★★**不新造第二个可手改的 md5 字段** ⇒ 少一个可被挖的坑 = 更严 ★★
REBOARD_FIELDS = ("by", "file", "prev_md5", "md5")


def m12(value) -> str:
    """md5 归一到 12 位小写前缀 (★落表台账里落表记录用的就是前缀★)。"""
    return str(value or "").strip().lower()[:12]


def ledger_cover_rows(text: str, rel: str) -> list:
    """落表台账里提到 rel 的【覆盖行】(表格行 + 至少一个 md5) ⇒ [{'md5s','iss','sec','row','full'}]。

    ★口径与 `ledger_records` 同源 (只认表格行 · 文件名同行 · 单号取行内 ISS-xxx 或最近带单号小节)★
    ★与 `ledger_records` 的差别: 允许【只有一个 md5】的行 (★「逐字节不变」声明行就是这么写的★)★
    """
    out = []
    ctx_iss = None
    sec = "(文首)"
    base = os.path.basename(rel)
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("#"):
            sec = s
            hit = re.findall(r"ISS-\d+", s)
            if hit:
                ctx_iss = hit[0]
            continue
        if not s.startswith("|"):
            continue
        if rel not in s and base not in s:
            continue
        tk = LEDGER_MD_RE.findall(s)
        if not tk:
            continue
        row_iss = re.findall(r"ISS-\d+", s)
        out.append({"md5s": [m12(t) for t in tk],
                    "iss": row_iss[0] if row_iss else ctx_iss,
                    "sec": sec, "row": s[:160], "full": s})
    return out


def ledger_change_rows(text: str, rel: str, exclude_aliases=()) -> list:
    """落表台账里 rel 的【变更行】(★改前 md5 ≠ 改后 md5★) ⇒ 合法改板只认这种行。

    ★`exclude_aliases` = 同组其它受保护件的名字别名 ⇒ ★一行两件两值 = 歧义行 ⇒ 不算变更行★
      (★例: 台账 L114 那一行同时写了板与 `.kicad_pro` 的两个 md5 ⇒ 那不是「板改过」的记录★)
    """
    out = []
    for r in ledger_cover_rows(text, rel):
        tk = r["md5s"]
        if len(tk) < 2:
            continue
        prev, new = tk[0], tk[-1]
        if prev == new:
            continue
        if any(a and a in r["full"] for a in exclude_aliases):
            continue
        out.append({"prev": prev, "new": new, "iss": r["iss"],
                    "sec": r["sec"], "row": r["row"], "full": r["full"]})
    return out


def ledger_change_state(rel: str, text: str, exclude_aliases=()) -> dict:
    """变更行上的链头 / 链 / 产出单号表 (★只认改前≠改后的行★; 取不准 ⇒ head=None ⇒ 判红★)。"""
    return ledger_state(rel, text,
                        recs=ledger_change_rows(text, rel, exclude_aliases))


def check_hard_protected_legal_reboard(root: str, group: dict, led_text: str,
                                       led_spec: str, md5_map: dict = None) -> tuple:
    """★【ISS-296】受保护件 (板 / `.kicad_pro`) 的【合法改板】通道 ★ (★判据只许变严★)。

    ★★判据 (照 SW 侧 ISS-284 的四条, ★一条都不许放宽★)★★
      ① ★保护基线自证★: 闸里写死的保护基线 md5 必须能在落表台账里与该文件【同行】查到
         ⇒ ★**只改闸里的 md5 而台账没记 ⇒ 判红** ★ (★悄悄换真源这条路被堵死★)
      ② ★台账里该文件没有变更行★ ⇒ 不许有合法改板记录; 且 **盘上 md5 必须 == 基线**
         (★纯 md5 硬保护, 与 ISS-286 之前一模一样, 一条不许放松★)
      ③ ★台账里有变更行★ ⇒ ★链头唯一 / 链不断 / 链头有单号★ (★fail-closed 三条一条不许动★)
         + ★链头那一行的四项 (by / file / prev_md5 / md5) 必须齐全且与链头逐字对上★
         + ★保护基线必须留在链尾★ (★不许把基线偷偷前移★)
         + ★盘上 md5 必须 == 台账链头★ (★判据方向不许变: 合法改板只是让链头前移★)
      ④ ★同组受保护件成对覆盖★: 一次合法改板必须覆盖同组全部件 (★只来一条 ⇒ 判红★)

    ★★返回 (rows, errs) ★★
    """
    errs = []
    rows = []
    covers_of = {}
    if not led_text:
        return rows, ["C4 合法改板: 判决源落表台账读不到 (%s) ⇒ 无从对账 (fail-closed 判红)" % led_spec]
    # ---- 同组受保护件的「名字别名」⇒ 用于剔「一行两件两值」的歧义行 ----
    aliases = {}
    for rel in group:
        b0 = os.path.basename(rel)
        aliases[rel] = {rel, b0, os.path.splitext(b0)[1]}
    heads = {}
    trip_iss = set()
    for rel, base in group.items():
        base12 = m12(base)
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            errs.append("C4 合法改板: 受保护文件不存在: %s" % rel)
            continue
        got = (md5_map or {}).get(rel) or md5_of(p)
        excl = set()
        for other, al in aliases.items():
            if other != rel:
                excl |= al
        covers = ledger_cover_rows(led_text, rel)
        covers_of[rel] = covers
        chg = ledger_change_rows(led_text, rel, excl)
        # ① 保护基线自证 (★只改闸里的基线而台账没记 ⇒ 判红★)
        if not any(base12 in r["md5s"] for r in covers):
            errs.append("C4 合法改板: %s 的保护基线 md5 %s 在落表台账 (%s) 里与该文件同行查不到 ⇒ "
                         "★闸里的基线被单独改了 (只改基线不落表 = 悄悄换真源 = 判红)★"
                         % (rel, base12, led_spec))
            continue
        if not chg:
            # ② 台账里没有变更行 ⇒ 不许有合法改板记录; 盘上必须还是基线 (★纯 md5 硬保护★)
            rows.append({"path": rel, "baseline": base, "got": got,
                         "same": got[:12] == base12, "mode": "纯 md5 硬保护 (台账无变更行)",
                         "covers": len(covers)})
            if got[:12] != base12:
                errs.append("C4 合法改板: 受保护文件 md5 变了: %s (%s ≠ 基线 %s) ★台账里没有变更行 ⇒ "
                             "不是合法改板 ⇒ 判红★" % (rel, got[:12], base12))
            continue
        # ③ 台账里有变更行 ⇒ 走【合法改板】路径
        st = ledger_change_state(rel, led_text, excl)
        head = st.get("head")
        chain = st.get("chain") or []
        for r in chg:
            if r["iss"]:
                trip_iss.add(r["iss"])
        rows.append({"path": rel, "baseline": base, "got": got,
                     "same": bool(head) and got[:12] == head,
                     "mode": "合法改板 (落表台账链头)",
                     "head": head, "iss": st.get("head_iss") or [],
                     "chain_len": len(chain), "covers": len(covers),
                     "change_rows": len(chg)})
        if not head:
            errs.append("C4 合法改板: %s 台账最新记录取不准 (%s) ⇒ 取错记录可能假绿 ⇒ 判红"
                         % (rel, st.get("why")))
            continue
        heads[rel] = head
        if not st.get("head_iss"):
            errs.append("C4 合法改板: %s 台账最新记录 (%s) 缺落表单号 (★四项不齐 ⇒ 判红★)"
                         % (rel, head))
        if not chain:
            errs.append("C4 合法改板: %s 台账链断了 / 不唯一 (%s) ⇒ 判红" % (rel, st.get("why")))
        else:
            orphan = sorted({r["new"] for r in chg} - set(chain))
            if orphan:
                errs.append("C4 合法改板: %s 台账里有记录不在链上 = %s ⇒ 判红" % (rel, orphan))
        # ③-1 链头那一行的【四项】必须齐全且与链头逐字对上
        head_rows = [r for r in chg if r["new"] == head]
        if not head_rows:
            errs.append("C4 合法改板: %s 台账链头 (%s) 找不到产出它的那一行 ⇒ 判红" % (rel, head))
            continue
        head_prevs = sorted({r["prev"] for r in head_rows})
        if len(head_prevs) != 1:
            errs.append("C4 合法改板: %s 链头那一行的改前 md5 不唯一 = %s ⇒ 取不准 ⇒ 判红"
                         % (rel, head_prevs))
            continue
        r_prev = head_prevs[0]
        r_by = (head_rows[0]["iss"] or "").strip()
        r_full = head_rows[0]["full"]
        missing = []
        if not r_by:
            missing.append("by (落表单号)")
        if not (rel in r_full or os.path.basename(rel) in r_full):
            missing.append("file (文件名)")
        if not r_prev:
            missing.append("prev_md5 (改前 md5)")
        if not head:
            missing.append("md5 (改后 md5)")
        if missing:
            errs.append("C4 合法改板: %s 台账链头那一行的四项不齐: 缺 %s ⇒ 判红"
                         % (rel, ", ".join(missing)))
            continue
        # 链上该链头的前驱必须 == 那一行的改前 md5 (★链不断★)
        if len(chain) >= 2 and chain[1] != r_prev:
            errs.append("C4 合法改板: %s 链头那一行的改前 md5 %s 与链上的 %s 对不上 (链断) ⇒ 判红"
                         % (rel, r_prev, chain[1]))
            continue
        # 保护基线必须留在链尾 (★不许把基线偷偷前移★)
        if chain and chain[-1] != base12:
            errs.append("C4 合法改板: %s 的保护基线 %s 不在台账链尾 (链尾 = %s) ⇒ "
                         "★基线被偷偷前移 = 判红★" % (rel, base12, chain[-1]))
            continue
        # 盘上 md5 必须 == 台账链头 (★判据方向不许变★)
        if got[:12] != head:
            errs.append("C4 合法改板: %s 盘上 md5 %s ≠ 台账链头 %s (真源被换了或台账没更新) ⇒ 判红"
                         % (rel, got[:12], head))
    # ④ 同组受保护件: 一次合法改板必须覆盖同组全部件 (★只来一条 ⇒ 判红★)
    if trip_iss:
        for rel, base in group.items():
            expect = heads.get(rel, m12(base))
            covered = [r for r in covers_of.get(rel) or []
                       if r["iss"] in trip_iss and expect in r["md5s"]]
            if not covered:
                errs.append("C4 合法改板: %s 没有被同一次合法改板 (%s) 覆盖 (记录只来一条 ⇒ 判红)"
                             % (rel, "/".join(sorted(trip_iss))))
    return rows, errs


# ==================================================================================================
# C4 · 受保护件 md5 (★ISS-286: 2 件写死基线 + 3 件走落表台账链头★)
# ==================================================================================================
def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_c4(root: str, baseline_override: dict = None) -> dict:
    errs = []
    rows = []
    # ---- 判决源台账 (只读) ----
    led_path = os.path.join(root, LEDGER_CANON)
    led_text = ""
    if os.path.isfile(led_path):
        with open(led_path, encoding="utf-8") as f:
            led_text = f.read()
    else:
        errs.append(f"C4 落表台账读不到: {LEDGER_CANON} (★判决源缺失 ⇒ fail-closed 判红★)")

    # ---- ① 受保护 2 件 (板 / `.kicad_pro`): ★★【ISS-296】合法改板通道★★
    #   ★★基线值一个字没改 (基线永远不许改) ★★ 改的是【判决源】: 写死基线一票否决
    #   ⇒ 【落表台账链头 + 合法改板通道】 ⇒ 板那一趟合法改一次 ⇒ 链头前移 ⇒ 绿 ★★
    #   ★★而「只改闸里的基线而台账没记」仍然判红 (基线自证) ⇒ 悄悄换真源照样堵死 ★★
    group = dict(PROTECTED)
    if baseline_override:
        group.update({k: v for k, v in baseline_override.items() if k in group})
    hp_rows, hp_errs = check_hard_protected_legal_reboard(root, group, led_text, LEDGER_CANON)
    rows.extend(hp_rows)
    errs.extend(hp_errs)

    # ---- ② 台账管理 3 件 (网表 / 脚表 / BOM): 判决源 = 落表台账最新记录 (链头) ----
    #   ★合法落表 ⇒ 链头自动前移 ⇒ 绿 ★ · ★盘上 md5 在台账里查不到任何登记 ⇒ 红 ★
    for rel in PROTECTED_LEDGER:
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            errs.append(f"C4 受保护件缺失: {rel}")
            continue
        got = md5_of(p)
        if led_text:
            st = ledger_state(rel, led_text)
        else:
            st = {"records": [], "head": None, "chain": [], "why": "落表台账读不到",
                  "head_iss": [], "known": set(), "producer": {}}
        recs = st.get("records") or []
        head = st.get("head")
        why = st.get("why")
        iss = st.get("head_iss") or []
        chain = st.get("chain") or []
        rows.append({"path": rel, "baseline": f"落表台账链头 ({LEDGER_CANON})", "got": got,
                     "same": bool(head) and got[:12] == head, "mode": "落表台账链头",
                     "head": head, "iss": iss, "chain_len": len(chain),
                     "records": len(recs)})
        # ---- fail-closed 五条 (★一条不许放宽★) ----
        if not led_text:
            errs.append(f"C4 台账管理件判决失败: {rel} 落表台账读不到 ({LEDGER_CANON}) ⇒ fail-closed 判红")
            continue
        if not recs:
            errs.append(f"C4 台账管理件判决失败: {rel} 落表台账里查不到任何登记 "
                        f"(★台账查不到 ⇒ 判红★)")
            continue
        if not head:
            errs.append(f"C4 台账管理件判决失败: {rel} 台账链头取不准 ({why}) ⇒ 取不准不许判绿")
            continue
        if not iss:
            errs.append(f"C4 台账管理件判决失败: {rel} 台账链头 ({head}) 无落表单号 "
                        f"(★单号/文件名/前后 md5 四项不齐 ⇒ 判红★)")
            continue
        if not chain:
            errs.append(f"C4 台账管理件判决失败: {rel} 落表链断了 / 不唯一 ({why}) ⇒ 判红")
            continue
        orphan = sorted({r["new"] for r in recs} - set(chain))
        if orphan:
            errs.append(f"C4 台账管理件判决失败: {rel} 台账里有记录不在链上 = {orphan} "
                        f"(★前后 md5 不齐 ⇒ 链断了 ⇒ 判红★)")
            continue
        if got[:12] != head:
            errs.append(f"C4 台账管理件判决失败: {rel} 盘上 md5 {got[:12]}… ≠ 台账链头 {head}… "
                        f"(★真源被换了? 或台账没更新★)")
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
    for rel in list(PROTECTED.keys()) + list(PROTECTED_LEDGER) + [LEDGER_CANON]:
        src = os.path.join(root, rel)
        if os.path.exists(src):
            d = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(src, d)
    return dst


def run_checks(root: str, baseline_override: dict = None) -> dict:
    calib = read_calib(root)
    board = read_board(root)
    c1 = check_c1(root, calib)
    c2 = check_c2(root, calib, board)
    c3 = check_c3(root, calib, board)
    c4 = check_c4(root, baseline_override=baseline_override)
    return {"C1": c1, "C2": c2, "C3": c3, "C4": c4}


def selftest(root: str) -> int:
    errs = []
    print("=" * 96)
    print("【自检】check_board_frame_coords.py 反向用例 (★沙盒副本上跑, 真件一个字节不碰★)")
    print("=" * 96)
    # ★真件指纹 (跑自检前先取一遍 ⇒ 跑完再比 ⇒ 自证「自检过程没碰真件」· ISS-286 加固★)
    pre_fp = {}
    for _rel in list(PROTECTED.keys()) + list(PROTECTED_LEDGER) + [LEDGER_CANON]:
        _p = os.path.join(root, _rel)
        if os.path.exists(_p):
            pre_fp[_rel] = md5_of(_p)
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

    # ================== ★★【ISS-286 新增 · 台账判决源】★★ ==================
    #   ★原 5 条反向用例一条不许少 (上面 ①~⑤ 全在) · 下面 ⑦~⑪ 是台账口径的新用例 ★
    def sb_ledger_read(sb):
        with open(os.path.join(sb, LEDGER_CANON), encoding="utf-8") as f:
            return f.read()

    def sb_ledger_write(sb, text):
        with open(os.path.join(sb, LEDGER_CANON), "w", encoding="utf-8") as f:
            f.write(text)

    def sb_drop_rel(text, rel):
        """把台账里该文件的全部落表记录行删掉 (⇒ 台账里查不到这个文件)。"""
        b = os.path.basename(rel)
        out = []
        for ln in text.splitlines():
            t = ln.strip()
            if t.startswith("|") and (rel in t or b in t) and len(LEDGER_MD_RE.findall(t)) >= 2:
                continue
            out.append(ln)
        return "\n".join(out) + "\n"

    def c4_reason(res):
        """取 C4 第一条错误 (★反向用例要贴出「红在哪一条」, 不是只贴一个红★)"""
        e = res["C4"]["errs"]
        return e[0] if e else ""

    def c4_red_files(res):
        out = []
        for e in res["C4"]["errs"]:
            if "台账管理件判决失败" in e:
                out.append(e.split(":")[1].split()[0])
        return out

    NET_REL = os.path.join("HW", "netlist_v1.csv")

    # ---- ⑦ 合法落表 ⇒ 链头自动前移 ⇒ C4 必须绿 (★本单效果证明★) ----
    sb = make_sandbox(root, "case7_legal_landing")
    p = os.path.join(sb, NET_REL)
    before = md5_of(p)
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n")                       # ★模拟一次合法落表 (盘上产物变了) ★
    after = md5_of(p)
    lt = sb_ledger_read(sb)
    head0 = ledger_state(NET_REL, lt)["head"]
    lt2 = lt + ("\n### ★★ISS-286 自检 · 合法落表 (★仅沙盒副本·真台账一个字没动★)★★\n\n"
                "| 文件 | 前 | 后 | 变了? |\n|---|---|---|---|\n"
                f"| ★**`{NET_REL}`** ★ | `{head0}` | `{after[:12]}` | ★**是**★ |\n")
    sb_ledger_write(sb, lt2)
    r7 = run_checks(sb)
    c4_green = r7["C4"]["ok"]
    print(f"  [{'OK ' if c4_green else 'NG '}] ⑦ 合法落表 (台账链头 {head0} ⇒ {after[:12]}) ⇒ C4 绿: "
          f"{'是' if c4_green else '否'} · 盘上 md5 {before[:8]} ⇒ {after[:8]} · "
          f"C4 错误 {len(r7['C4']['errs'])} 条" + (f" · {c4_reason(r7)}" if not c4_green else ""))
    if not c4_green:
        errs.append("⑦ 合法落表后 C4 还是红 ⇒ 判决源没换成落表台账")

    # ---- ⑧ 台账里查不到该文件的任何登记 ⇒ C4 红 ----
    sb = make_sandbox(root, "case8_ledger_no_record")
    lt = sb_ledger_read(sb)
    sb_ledger_write(sb, sb_drop_rel(lt, NET_REL))
    r8 = run_checks(sb)
    c4_red8 = not r8["C4"]["ok"]
    print(f"  [{'OK ' if c4_red8 else 'NG '}] ⑧ 台账里查不到网表的任何登记 ⇒ C4 红: "
          f"{'是' if c4_red8 else '否'} · 红件 {c4_red_files(r8)} · {c4_reason(r8)}")
    if not c4_red8:
        errs.append("⑧ 台账里查不到网表登记后 C4 没红")

    # ---- ⑨ 台账里有登记, 但盘上 ≠ 台账登记值 ⇒ C4 红 ----
    sb = make_sandbox(root, "case9_disk_not_in_ledger")
    p = os.path.join(sb, NET_REL)
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n")
    r9 = run_checks(sb)
    c4_red9 = not r9["C4"]["ok"]
    print(f"  [{'OK ' if c4_red9 else 'NG '}] ⑨ 台账没更新而盘上网表被改 ⇒ C4 红: "
          f"{'是' if c4_red9 else '否'} · 盘上 md5 {md5_of(p)[:8]} · 红件 {c4_red_files(r9)} · "
          f"{c4_reason(r9)}")
    if not c4_red9:
        errs.append("⑨ 盘上真源被偷改后 C4 没红")

    # ---- ⑩a 台账被手改 · 单号不齐 (伪造行无所属章节 ⇒ 无落表单号) ⇒ C4 红 ----
    sb = make_sandbox(root, "case10a_forged_no_ticket")
    p = os.path.join(sb, NET_REL)
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n")
    tampered = md5_of(p)[:12]
    lt = sb_ledger_read(sb)
    head0 = ledger_state(NET_REL, lt)["head"]
    forged = f"| ★**伪造** ★ | ★**`{NET_REL}`** ★ | `{head0}` | `{tampered}` | ★**手改**★ |\n"
    sb_ledger_write(sb, forged + lt)     # ★伪造行插到台账最前面 (无所属章节 ⇒ 无单号) ★
    r10a = run_checks(sb)
    c4_red10a = not r10a["C4"]["ok"]
    print(f"  [{'OK ' if c4_red10a else 'NG '}] ⑩a 台账被手改 (登记值凑成与盘上一致, 但单号不齐) ⇒ C4 红: "
          f"{'是' if c4_red10a else '否'} · 盘上 {tampered} / 台账登记 {tampered} (值一样!) · "
          f"红件 {c4_red_files(r10a)} · {c4_reason(r10a)}")
    if not c4_red10a:
        errs.append("⑩a 台账单号不齐 (手改) 后 C4 没红")

    # ---- ⑩b 台账被手改 · 文件名不齐 (登记到了别的文件名下) ⇒ C4 红 ----
    sb = make_sandbox(root, "case10b_forged_wrong_filename")
    p = os.path.join(sb, NET_REL)
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n")
    tampered = md5_of(p)[:12]
    lt = sb_ledger_read(sb)
    head0 = ledger_state(NET_REL, lt)["head"]
    forged = (f"| ★**伪造** ★ | ★**`HW/netlist_v1_old.csv`** ★ | `{head0}` | `{tampered}` | "
              f"★**手改**★ |\n")
    sb_ledger_write(sb, forged + lt)
    r10b = run_checks(sb)
    c4_red10b = not r10b["C4"]["ok"]
    print(f"  [{'OK ' if c4_red10b else 'NG '}] ⑩b 台账被手改 (登记值凑成与盘上一致, 但文件名不对) ⇒ C4 红: "
          f"{'是' if c4_red10b else '否'} · 红件 {c4_red_files(r10b)} · {c4_reason(r10b)}")
    if not c4_red10b:
        errs.append("⑩b 台账文件名不对 (手改) 后 C4 没红")

    # ---- ⑩c 台账被手改 · 前后 md5 不齐 (前驱是假值 ⇒ 链断) ⇒ C4 红 ----
    sb = make_sandbox(root, "case10c_forged_broken_prev")
    p = os.path.join(sb, NET_REL)
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n")
    tampered = md5_of(p)[:12]
    lt = sb_ledger_read(sb)
    st = ledger_state(NET_REL, lt)
    head0 = st["head"]
    rec = next((r for r in st["records"] if r["new"] == head0), None)
    prev0 = rec["prev"] if rec else "000000000000"     # ★链头那一行的真前驱 ★
    lines = lt.splitlines()
    hit = ndel = 0
    for i, ln in enumerate(lines):
        t = ln.strip()
        if not t.startswith("|"):
            continue
        tk = LEDGER_MD_RE.findall(t)
        if len(tk) < 2:
            continue
        if tk[-1][:12] == head0:
            # ★链头那一行: 前 md5 换成假值, 后 md5 凑成盘上值 (★登记值 == 盘上值★) ★
            lines[i] = re.sub(re.escape(tk[0]), "000000000000", t, count=1)
            lines[i] = re.sub(re.escape(tk[-1]), tampered, lines[i], count=1)
            hit += 1
        elif tk[-1][:12] == prev0:
            # ★把「产出前驱的那一行」改成自环 (前 == 后) ⇒ 前驱不再是链上的改后值
            #   (★不能删行: 删了它自己的前驱就会顶上来变成第二个链头 ⇒ 测的就不是「链断了」★) ★
            lines[i] = re.sub(re.escape(tk[-1]), tk[0], t, count=1)
            ndel += 1
    sb_ledger_write(sb, "\n".join(lines) + "\n")
    r10c = run_checks(sb)
    c4_red10c = not r10c["C4"]["ok"]
    # ★★★ ISS-296 cont3 (★2026-11-18 05:5x · mech-lead · 追加式订正·老字留痕★) ★★★
    #   ★**旧值 = `hit == 1`** (★假设: 链头 md5 在台账里只出现 1 次★) ⇒ ★**新值 = `hit >= 1`** ★
    #   ★**为什么必须改 (★不是「为了让闸绿而改闸」·是【台账数据形状】变了★)**:
    #     ★**ISS-302 (hw-lead · 2026-11-18 00:3x 落表)** 往 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §19 追加了【两张表】★
    #       ⇒ 同一个链头 md5 `6aee500e60ba…` 现在落在【2 行】上 (§19.2 前后对照表 L1451 + §19.3 登记表 L1466)
    #       ⇒ `hit == 1` 这个【台账形状假设】被一次【合法落表】打破 ⇒ 自检误报红 (★2026-11-18 05:45 实测 rc=2★) ★
    #   ★**为什么这不是放宽判据 (★三条都在★)**:
    #     ① ★**判据方向一个字没动** ★ (★盘上 md5 ≠ 基线 ⇒ 仍红; 盘上 md5 ≠ 台账链头 ⇒ 仍红★)
    #     ② ★**fail-closed 三条没动** ★ (★链头不唯一⇒红 · 链断⇒红 · 链头无单号⇒红★)
    #     ③ ★**本条用例的【真正断言】是 `c4_red10c`** (★链头那一行被改坏 ⇒ C4 必须红★) ⇒ ★**它一直是红的** ★
    #   ⇒ ★**只把【计数型 sanity 断言】从「恰好 1 行」放宽成「至少 1 行」⇒ 判据只可能变严 (★多改一行 ⇒ 链断得更彻底★)·不可能变松** ★
    #   ★**改前副本**: `logs/iss296/check_board_frame_coords_before_iss296_cont3.py` (★md5 `051967adde31be65888de056c6fbf478`★) ★
    print(f"  [{'OK ' if (hit >= 1 and ndel == 1 and c4_red10c) else 'NG '}] ⑩c 台账被手改 (登记值凑成与盘上一致, "
          f"但前 md5 是假值 ⇒ 链断) ⇒ C4 红: {'是' if c4_red10c else '否'} · 改坏行 {hit} / 改自环行 {ndel} · "
          f"红件 {c4_red_files(r10c)} · {c4_reason(r10c)}")
    if not (hit >= 1 and ndel == 1 and c4_red10c):     # ★ISS-296 cont3: `hit == 1` ⇒ `hit >= 1` (★见上方留痕★) ★
        errs.append("⑩c 台账前后 md5 不齐 (手改) 后 C4 没红")

    # ---- ⑪ 链头不唯一 (台账里造第二条指向同一文件的链头) ⇒ C4 红 (fail-closed) ----
    sb = make_sandbox(root, "case11_two_heads")
    lt = sb_ledger_read(sb)
    st = ledger_state(NET_REL, lt)
    head0 = st["head"]
    rec = next((r for r in st["records"] if r["new"] == head0), None)
    prev0 = rec["prev"] if rec else "000000000000"
    forged = (f"\n| ★**伪造** ★ | ★**`{NET_REL}`** ★ | `{prev0}` | `deadbeefdead` | "
              f"★**手改**★ |\n")
    sb_ledger_write(sb, lt + forged)
    r11 = run_checks(sb)
    c4_red11 = not r11["C4"]["ok"]
    print(f"  [{'OK ' if c4_red11 else 'NG '}] ⑪ 台账里造出第二条链头 (链头不唯一) ⇒ C4 红: "
          f"{'是' if c4_red11 else '否'} · 红件 {c4_red_files(r11)} · {c4_reason(r11)}")
    if not c4_red11:
        errs.append("⑪ 链头不唯一后 C4 没红")

    # ================== ★★【ISS-296 新增 · 合法改板通道】★★ ==================
    #   ★★判据只许变严, 不许放松 ★★ · 全部在【沙盒副本】上做, 真件一个字节不许碰 ★★
    #   ★★ISS-999 = 沙盒里的假单号 (真台账里不存在) ⇒ 只在沙盒副本里出现 ★★
    BOARD_REL = os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb")
    PRO_REL = os.path.join("HW", "PCB", "demo_mainboard.kicad_pro")

    def hp_reason(res):
        """取 C4 第一条【合法改板】错误 (★反向用例要贴出「红在哪一条」, 不是只贴一个红★)"""
        for e in res["C4"]["errs"]:
            if "合法改板" in e:
                return e
        return res["C4"]["errs"][0] if res["C4"]["errs"] else ""

    def sb_board_append_byte(sb):
        """在沙盒里的板上追加 1 字节 (★模拟「手改板」/ 模拟「合法改板后的新板」★)"""
        p = os.path.join(sb, BOARD_REL)
        with open(p, "a", encoding="utf-8") as f:
            f.write("\n")
        return md5_of(p)

    def sb_ledger_append(sb, rows):
        lt = sb_ledger_read(sb)
        sb_ledger_write(sb, lt + "\n" + rows)

    # ---- ⑫ ① 把闸里的板基线 md5 改掉 (★悄悄换真源★) 而落表台账不动 ⇒ 必须红 ----
    sb = make_sandbox(root, "case12_baseline_swapped")
    r12 = run_checks(sb, baseline_override={BOARD_REL: "deadbeefdeadbeefdeadbeefdeadbeef"})
    c4_red12 = not r12["C4"]["ok"]
    print(f"  [{'OK ' if c4_red12 else 'NG '}] ⑫ 闸里的板基线被单独改 (611b869e… ⇒ deadbeef…) 而台账不动 "
          f"⇒ C4 红: {'是' if c4_red12 else '否'} · {hp_reason(r12)}")
    if not c4_red12:
        errs.append("⑫ 闸里的基线被单独改后 C4 没红")

    # ---- ⑬ ② 盘上板被手改 (★台账里没有变更行★) ⇒ 必须红 (纯 md5 硬保护不许被放松) ----
    sb = make_sandbox(root, "case13_disk_handedit")
    newmd5_13 = sb_board_append_byte(sb)
    r13 = run_checks(sb)
    c4_red13 = not r13["C4"]["ok"]
    print(f"  [{'OK ' if c4_red13 else 'NG '}] ⑬ 盘上板被手改 (md5 ⇒ {newmd5_13[:8]}…) 而台账无变更行 "
          f"⇒ C4 红: {'是' if c4_red13 else '否'} · {hp_reason(r13)}")
    if not c4_red13:
        errs.append("⑬ 盘上板被手改后 C4 没红")

    # ---- ⑭ ③ 台账补一条【变更行】(改前→改后) 但四项不齐 (★无落表单号★) ⇒ 必须红 ----
    sb = make_sandbox(root, "case14_forged_no_ticket")
    forged14 = (f"| ★**伪造** ★ | ★**`{BOARD_REL}`** ★ | `611b869e1351` | `777777777777` | "
                f"★**手改**★ |\n")
    lt14 = sb_ledger_read(sb)
    sb_ledger_write(sb, forged14 + lt14)   # ★伪造行插到台账最前面 (无所属章节 ⇒ 无单号) ★
    r14 = run_checks(sb)
    c4_red14 = not r14["C4"]["ok"]
    print(f"  [{'OK ' if c4_red14 else 'NG '}] ⑭ 台账补了一条变更行但四项不齐 (无落表单号) ⇒ C4 红: "
          f"{'是' if c4_red14 else '否'} · {hp_reason(r14)}")
    if not c4_red14:
        errs.append("⑭ 台账变更行四项不齐后 C4 没红")

    # ---- ⑮ ④ 只让板有变更行, `.kicad_pro` 没有 (★同组覆盖★) ⇒ 必须红 ----
    sb = make_sandbox(root, "case15_board_only")
    newmd5_15 = sb_board_append_byte(sb)
    sb_ledger_append(sb, f"| ★**ISS-999** ★ | ★**`{BOARD_REL}`** ★ | `611b869e1351` | "
                         f"`{newmd5_15[:12]}` | ★**是 (合法改板·板只改一次)** ★ |\n")
    r15 = run_checks(sb)
    c4_red15 = not r15["C4"]["ok"]
    print(f"  [{'OK ' if c4_red15 else 'NG '}] ⑮ 只让板有变更行 (`.kicad_pro` 没有同一次覆盖) ⇒ C4 红: "
          f"{'是' if c4_red15 else '否'} · {hp_reason(r15)}")
    if not c4_red15:
        errs.append("⑮ 同组覆盖不成对后 C4 没红")

    # ---- ⑯a 链头不唯一 (★fail-closed 一★) ⇒ 必须红 ----
    sb = make_sandbox(root, "case16a_two_heads")
    sb_ledger_append(sb,
                     f"| ★**ISS-999** ★ | ★**`{BOARD_REL}`** ★ | `111111111111` | `222222222222` | ★**手改**★ |\n"
                     f"| ★**ISS-999** ★ | ★**`{BOARD_REL}`** ★ | `333333333333` | `444444444444` | ★**手改**★ |\n")
    r16a = run_checks(sb)
    c4_red16a = not r16a["C4"]["ok"]
    print(f"  [{'OK ' if c4_red16a else 'NG '}] ⑯a 台账里造出第二条链头 (链头不唯一) ⇒ C4 红: "
          f"{'是' if c4_red16a else '否'} · {hp_reason(r16a)}")
    if not c4_red16a:
        errs.append("⑯a 链头不唯一后 C4 没红")

    # ---- ⑯b 链断 / 保护基线不在链尾 (★fail-closed 二★) ⇒ 必须红 ----
    sb = make_sandbox(root, "case16b_broken_chain")
    sb_ledger_append(sb, f"| ★**ISS-999** ★ | ★**`{BOARD_REL}`** ★ | `555555555555` | `666666666666` | "
                         f"★**手改**★ |\n")
    r16b = run_checks(sb)
    c4_red16b = not r16b["C4"]["ok"]
    print(f"  [{'OK ' if c4_red16b else 'NG '}] ⑯b 链断 (改前 md5 对不上保护基线 ⇒ 基线不在链尾) ⇒ C4 红: "
          f"{'是' if c4_red16b else '否'} · {hp_reason(r16b)}")
    if not c4_red16b:
        errs.append("⑯b 链断后 C4 没红")

    # ---- ⑰ ⑥ 正向对照: 合法改板一次 (板 + `.kicad_pro` 成对) ⇒ 必须绿 (证明闸不是恒红) ----
    sb = make_sandbox(root, "case17_legal_reboard")
    newmd5_17 = sb_board_append_byte(sb)
    sb_ledger_append(sb,
                     f"| ★**ISS-999** ★ | ★**`{BOARD_REL}`** ★ | `611b869e1351` | `{newmd5_17[:12]}` | "
                     f"★**是 (合法改板·板只改一次)** ★ |\n"
                     f"| ★**ISS-999** ★ | ★**`{PRO_REL}`** ★ | `3e504d2be831` | `3e504d2be831` | "
                     f"★**否 (逐字节不变)** ★ |\n")
    r17 = run_checks(sb)
    c4_green17 = r17["C4"]["ok"]
    others17 = [k for k in ("C1", "C2", "C3") if not r17[k]["ok"]]
    print(f"  [{'OK ' if (c4_green17 and not others17) else 'NG '}] ⑰ 正向对照: 合法改板一次 "
          f"(板 611b869e… ⇒ {newmd5_17[:8]}… + `.kicad_pro` 同一次成对登记) ⇒ C4 绿: "
          f"{'是' if c4_green17 else '否'} · C1/C2/C3 = "
          f"{'全绿' if not others17 else others17} · C4 错误 {len(r17['C4']['errs'])} 条"
          + (f" · {hp_reason(r17)}" if not c4_green17 else ""))
    if not (c4_green17 and not others17):
        errs.append("⑰ 合法改板后 C4 还是红 ⇒ 合法改板通道没走通")

    # ---- ⑱ ★★【cont3 · 2026-11-18 · mech-lead · 新增】★★ main 【真实落表形状】: 同一个 md5 登记在【两张表】里
    #   (★§16.2「新旧 md5 前后对照」链头行 + §19.3「逐条登记」行 · ISS-302 2026-11-18 00:22 那次落表就是这个形状★)
    #   ⇒ ⑰ 只覆盖了【单行】形状 ⇒ ★**真实落表形状从来就没被验过** ⇒ 本条补上 ⇒ C4 必须【绿】★
    #   ⇒ ★**为什么这一条要紧**: 「板只改一次」那一趟落表时, main 会按 ISS-302 的形状写【两张表】
    #   ⇒ 若两张表让 C4 假红 ⇒ 收工验收时又会被读成「板改坏了」⇒ 板白改第二遍 (★ISS-296 立项病灶★) ★
    sb = make_sandbox(root, "case18_real_landing_two_tables")
    newmd5_18 = sb_board_append_byte(sb)
    r18a = f"| ★**`{BOARD_REL}`** ★ | `611b869e1351` | `{newmd5_18[:12]}` | ★**是**★ |\n"
    r18b = (f"| L9999 | {BOARD_REL} | `611b869e1351` | `{newmd5_18[:12]}` | "
            f"★**2026-11-18 05:5x** ★ | ★**ISS-999** ★ |\n")
    sb_ledger_append(sb, r18a + r18b +
                     f"| ★**`{PRO_REL}`** ★ | `3e504d2be831` | `3e504d2be831` | "
                     f"★**否 (逐字节不变)** ★ |\n")
    r18 = run_checks(sb)
    c4_green18 = r18["C4"]["ok"]
    others18 = [k for k in ("C1", "C2", "C3") if not r18[k]["ok"]]
    print(f"  [{'OK ' if (c4_green18 and not others18) else 'NG '}] ⑱ 正向对照: 合法改板一次 "
          f"+ 【两张表都写】(main 真实落表形状: §16.2 链头行 + §19.3 登记行) ⇒ C4 绿: "
          f"{'是' if c4_green18 else '否'} · C1/C2/C3 = "
          f"{'全绿' if not others18 else others18} · C4 错误 {len(r18['C4']['errs'])} 条"
          + (f" · {hp_reason(r18)}" if not c4_green18 else ""))
    if not (c4_green18 and not others18):
        errs.append("⑱ 真实落表形状 (两张表) 下合法改板后 C4 还是红 ⇒ 那一趟收工验收会假红")

    # ---- ⑲ 同样两张表, 但两行的【改前 md5 互相不一致】⇒ C4 必须红 (★fail-closed 在真实形状上不许松★) ----
    sb = make_sandbox(root, "case19_two_tables_inconsistent_prev")
    newmd5_19 = sb_board_append_byte(sb)
    r19a = f"| ★**`{BOARD_REL}`** ★ | `611b869e1351` | `{newmd5_19[:12]}` | ★**是**★ |\n"
    r19b = (f"| L9999 | {BOARD_REL} | `deadbeefdead` | `{newmd5_19[:12]}` | "
            f"★**2026-11-18 05:5x** ★ | ★**ISS-999** ★ |\n")
    sb_ledger_append(sb, r19a + r19b +
                     f"| ★**`{PRO_REL}`** ★ | `3e504d2be831` | `3e504d2be831` | "
                     f"★**否 (逐字节不变)** ★ |\n")
    r19 = run_checks(sb)
    c4_red19 = not r19["C4"]["ok"]
    print(f"  [{'OK ' if c4_red19 else 'NG '}] ⑲ 两张表都写但【改前 md5 互相不一致】⇒ C4 红: "
          f"{'是' if c4_red19 else '否'} · {hp_reason(r19)}")
    if not c4_red19:
        errs.append("⑲ 两张表改前 md5 不一致后 C4 没红 ⇒ fail-closed 被放松")

    # ---- ⑥ 沙盒自证: 真件一个字节没动 ----
    same = all(md5_of(os.path.join(root, rel)) == base_md5 for rel, base_md5 in PROTECTED.items())
    same2 = all(md5_of(os.path.join(root, rel)) == fp for rel, fp in pre_fp.items())
    print(f"  [{'OK ' if (same and same2) else 'NG '}] ⑥ 真件 6 件 (板 / `.kicad_pro` 写死基线 2 件 + "
          f"台账管理 3 件 + 落表台账本体 1 件) md5 跑完自检后仍逐字节不变: "
          f"{'是' if (same and same2) else '否'}")
    if not (same and same2):
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
    hr("【闸】ISS-276 坐标系闸 (C1 帧标签 / C2 不压 SoM / C3 负向断言 / C4 受保护件: 2 件合法改板通道 (ISS-296) + 3 件台账链头)")
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
                mode = r.get("mode", "")
                if mode.startswith("合法改板"):
                    print(f"   {'✅' if r['same'] else '❌'} {r['path']} ★合法改板通道★ "
                          f"判决源 = 落表台账链头 {r.get('head') or '取不准'} "
                          f"(by {','.join(r.get('iss') or []) or '无单号'}) ⇒ 盘上 {r['got'][:12]}… "
                          f"(台账变更行 {r.get('change_rows')} 条 · 链长 {r.get('chain_len')})")
                elif mode.startswith("纯 md5"):
                    print(f"   {'✅' if r['same'] else '❌'} {r['path']} ★纯 md5 硬保护★ "
                          f"(台账无变更行) 基线 {r['baseline']} ⇒ 现值 {r['got']}")
                else:
                    print(f"   {'✅' if r['same'] else '❌'} {r['path']} 判决源 = 落表台账链头 "
                          f"{r.get('head') or '取不准'} (by {','.join(r.get('iss') or []) or '无单号'}) "
                          f"⇒ 盘上 {r['got'][:12]}… (台账记录 {r.get('records')} 条 · 链长 "
                          f"{r.get('chain_len')})")
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
