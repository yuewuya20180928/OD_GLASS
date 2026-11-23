#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/check_juart_1p27_clearance.py —— `J_UART` 排针 land 改 1.27mm 后的结构侧净距真相 机器闸
===================================================================================================
★**性质**: 只读机器闸 · ★零写板 / 零落表 / 零改任何既有脚本 / 零外发 / 不代老板拍板** ★
★**派活**: 项目总工 (main) · ISS-374 · 2026-11-23 派 / 2026-11-24 01:1x 做 · 交卷人 = 结构总工 (mech-lead) ★
★**续做**: cont1 (★上一趟 2026-11-23 23:16:37 派 · 23:23:13 被掐 · runtimeMs 394,308 ≈ 6.6 分钟 ·
  status=timeout + abortedLastRun=true + promptError="This operation was aborted" · externalAbort=false
  ⇒ 非上下文溢出·不是逻辑错★ ⇒ 三件交付物零落地) ★
★**关联**: `MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md` (★真相页·本单产出★) ·
          `HANDOFF/2026-11-23_mech-lead_ISS374_JUART排针1.27净距真相.md` (交卷页) ·
          板侧项 = `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 `B33_PIN_LAND_1P27` (★不重复发明板侧项编号★) ★
★**姊妹件 (ISS-371 · 已签收 · 本闸只读不改)**: `MECH/BOARD_ONEPASS_JDEBUG_1P27_CLEARANCE.md` ·
          `MECH/check_jdebug_1p27_clearance.py` ★

────────────────────────────────────────────────────────────────────────────────────────────────────────
【作用】★把「`J_UART` 排针 land 从 pitch 0.50 改到 1.27」这条板侧已拍板的改动所引起的
  【结构侧净距真相】钉成机器闸 ⇒ 以后谁把 `2.2700` / `0.1350` / `0.4650` 这组数写错、
  或者拿姊妹件 `J_DEBUG` 的 `4.8100` / `2.6950` 套过来 ⇒ 本闸立刻红 ★

────────────────────────────────────────────────────────────────────────────────────────────────────────
【★★本单最关键的一条: 两颗件的推导链【不同源】★★】

  ★**`J_DEBUG` 的必须清空区 X 宽 = 铜箔 X 宽 (铜箔支配) ⇒ 换 land ⇒ 清空区跟着变宽 ⇒ 方向绿** ★
  ★**`J_UART` 的必须清空区 X 宽 = 座体模型 `2.5400` (座体支配·固定值) ⇒ 换 land ⇒ 铜箔顶到座体 ⇒ 方向红** ★
  ★**⇒ 【不许】把 `J_DEBUG` 的推导链套到 `J_UART` 上** ★ ⇒ ★**J5 就是专门防这一条的** ★

────────────────────────────────────────────────────────────────────────────────────────────────────────
【九条判据 (★自证型·每条 fail-closed★)】
    J0 官方 1×2 THT land 几何必须与盘上 `.kicad_mod` 实读一致 (★自己解析·不许写死 `2.2700`★)
    J1 §2 三档量差表逐格与 J0 实算一致 (现状 / THT / SMD 变体 ★不许拿 THT 的数套 SMD 变体★)
    J2 座体必须清空区 X 宽 ≥ 铜箔 X 宽 (不许越界) + 越界/不足事实必须被显式记账
    J3 每边余量对称且 ≥ `CRIT` (★`CRIT` 从 `MECH/service_port_check.py` 取·不许写死★) + 最坏余量 (±0.30) 也要判
    J4 SMD 降级变体几何独立实测并单列 (★`Pin1Left` 与 `Pin1Right` 两个变体各自算★)
    J5 `J_DEBUG` / `J_UART` 两件方向结论必须并排出现在页里 + 方向必须相反 + 口径必须不同源
       ⇒ ★**只写一颗 ⇒ 红** ★ ⇒ ★**专防「拿一颗件的结论套另一颗」★ ★
    J6 板面零写板自证 (md5 / mtime / size 三项)
    J7 证据等级五级白名单 + 正文零挂起措辞 + 「判据句 / 事实句」两句分开 + `.kicad_mod` md5 台账
    J8 零挂链 ⇒ 自证 `grep -c check_juart_1p27_clearance state/gate_check.py` == 0

【★判据句与事实句必须分开 (ISS-371 立下的口径纪律·本闸继承★)】
  ★**判据句**: 换官方 THT 后 `J_UART` 每边余量 `0.1350` < `CRIT` `0.60` ⇒ **不过阈** ★
  ★**事实句**: 铜箔 X 宽 `2.2700` > 座体必须清空区宽 `2.5400` 减去两倍 `CRIT` ⇒ **铜箔进座体必须清空区** ⇒ **结构件装不上** ★
  ★**两句同时成立; 不许混成一句含混的「过」** ★ ⇒ J3 逐行扫描 ⇒ 红 ★

────────────────────────────────────────────────────────────────────────────────────────────────────────
【rc 语义】
  0 = 全部通过
  1 = 有断言不通过 (逐条列出 + 点名判据号)
  2 = 参数 / IO 错误

【用法】
  python3 MECH/check_juart_1p27_clearance.py             # 扫真件 (只读)
  python3 MECH/check_juart_1p27_clearance.py --selftest  # 反向用例 (末行 ALL TESTS PASS)
  python3 MECH/check_juart_1p27_clearance.py --root DIR  # 扫指定树 (反向用例在 tmp/iss374_sbx/selftest/ 上做)

【★SKIP 口径 (★为什么 J5 独占「页存在性」★)】
  ★**页缺失时, 依赖页的判据 (J1/J2/J3/J4/J7) 标 SKIP 并计绿; 页存在性 + 两件并排 + 方向相反
  全部由 J5 独占 ⇒ ①「页被删/改名」这类反向用例能定位到唯一病灶 (J5 红, 其余绿)
  ②整闸仍然是 fail-closed (J5 红 ⇒ rc=1) ★**

【沙盒纪律】反向用例一律落项目盘 `<root>/tmp/iss374_sbx/selftest/` (★不许写系统 `/tmp`★)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

PAGE_REL = "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE.md"
CRIT_REL = "MECH/service_port_check.py"
CALIBER_REL = "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md"
PCB_REL = "HW/PCB/demo_mainboard.kicad_pcb"
GATE_REL = "state/gate_check.py"

LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
FPLIB_DIR = "Connector_PinHeader_1.27mm.pretty"
MOD_NAMES = {
    "tht_1x02": "PinHeader_1x02_P1.27mm_Vertical.kicad_mod",
    "smd_pin1left": "PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Left.kicad_mod",
    "smd_pin1right": "PinHeader_1x02_P1.27mm_Vertical_SMD_Pin1Right.kicad_mod",
    "tht_1x04": "PinHeader_1x04_P1.27mm_Vertical.kicad_mod",
}

BOARD_BASELINE = {
    "md5": "611b869e13518c3c023fb178f91a0075",
    "mtime": "2026-11-06 07:07:17.362193413",
    "size": 4940213,
}

EVIDENCE_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
FORBIDDEN_EVIDENCE = ("[官方]", "[推断]", "[推测]", "[估计]", "[大概值]")
HEDGING_WORDS = ("可能", "大概", "应该是", "似乎", "貌似", "估摸", "八成", "多半")
FORBIDDEN_PHRASES = ("等原厂回信", "等原厂回复", "等待原厂", "回头再问原厂")
# ★结论类禁词: 不许用含混的「合格 / OK」当判决 (ISS-371 口径·本闸继承)★
FORBIDDEN_VERDICT_WORDS = ("合格", "OK")

TOL = 1e-6


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
    return abs(float(a) - float(b)) <= tol


def strip_fences(text: str) -> str:
    """去掉 ```...``` 围栏块 (机器块与命令块) ⇒ 只在正文散文里扫证据标记与措辞"""
    return re.sub(r"```.*?```", "\n", text, flags=re.S)


def mtime_ns_of(dt_str: str) -> int:
    """'2026-11-06 07:07:17.362193413' -> epoch ns (本地时区·与 `stat -c '%y'` 同口径)"""
    import datetime
    d, t = dt_str.split(" ")
    hms, frac = t.split(".")
    base = datetime.datetime.strptime(d + " " + hms, "%Y-%m-%d %H:%M:%S")
    return int(base.timestamp()) * 10 ** 9 + int(frac[:9].ljust(9, "0"))


def parse_machine_block(text: str) -> dict:
    """取 ```MECH-JUART-CLEARANCE-JSON ... ``` 里的 JSON"""
    m = re.search(r"```MECH-JUART-CLEARANCE-JSON\s*(\{.*\})\s*```", text, re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except Exception:
        return {}


# --------------------------------------------------------------------------------------------------
# 官方 `.kicad_mod` 解析 (★自己解析·不许写死★)
# --------------------------------------------------------------------------------------------------

def _fab_pts(txt: str):
    """★只取 F.Fab 层上的 fp_line/fp_rect 端点★
    (★2026-11-24 踩坑: 用 `.*?` 跨块匹配会把 F.SilkS 线误当成 F.Fab ⇒ 必须按块切★)"""
    pts = []
    idx = 0
    while True:
        i = txt.find("(fp_line", idx)
        if i < 0:
            i2 = txt.find("(fp_rect", idx)
            if i2 < 0:
                break
            i = i2
        j = len(txt)
        for marker in ("(fp_line", "(fp_rect", "(fp_text", "(pad ", "(property"):
            k = txt.find(marker, i + 1)
            if 0 < k < j:
                j = k
        chunk = txt[i:j]
        if '(layer "F.Fab")' in chunk:
            m = re.search(r"\(start\s+([-\d.]+)\s+([-\d.]+)\)\s*\n\s*\(end\s+([-\d.]+)\s+([-\d.]+)\)", chunk)
            if m:
                pts.append([float(m.group(1)), float(m.group(2))])
                pts.append([float(m.group(3)), float(m.group(4))])
        idx = j if j > i else i + 1
    return pts


def parse_mod(path: str) -> dict:
    """返回 {pads:[{num,type,shape,at,size,drill}], crtyd:[[x0,y0],[x1,y1]], fab:[[..],[..]]}"""
    txt = read_text(path)
    pads = []
    for m in re.finditer(
        r'\(pad\s+"([^"]+)"\s+(\S+)\s+(\S+)\s*\n\s*\(at\s+([-\d.]+)\s+([-\d.]+)\)\s*\n\s*\(size\s+([-\d.]+)\s+([-\d.]+)\)',
        txt,
    ):
        num, ptype, shape, ax, ay, sx, sy = m.groups()
        d = 0.0
        dm = re.search(r"\(drill\s+([-\d.]+)\)", txt[m.end():m.end() + 400])
        if dm:
            d = float(dm.group(1))
        pads.append({
            "num": num, "type": ptype, "shape": shape,
            "at": [float(ax), float(ay)],
            "size": [float(sx), float(sy)],
            "drill": d,
        })
    crtyd = None
    cm = re.search(r"\(fp_rect\s*\n\s*\(start\s+([-\d.]+)\s+([-\d.]+)\)\s*\n\s*\(end\s+([-\d.]+)\s+([-\d.]+)\)", txt)
    if cm:
        crtyd = [[float(cm.group(1)), float(cm.group(2))], [float(cm.group(3)), float(cm.group(4))]]
    fab = None
    fab_pts = _fab_pts(txt)
    if fab_pts:
        fab = [[min(p[0] for p in fab_pts), min(p[1] for p in fab_pts)],
               [max(p[0] for p in fab_pts), max(p[1] for p in fab_pts)]]
    return {"pads": pads, "crtyd": crtyd, "fab": fab}


def rot90(p):
    """KiCad footprint rot +90°: 局部 (x,y) -> (y, -x)  (★S1/S2 沙盒实测校准过★)"""
    return [p[1], -p[0]]


def mod_copper_box(mod: dict, rot: int = 90):
    """把 mod 的焊盘按旋转摆到板上, 返回铜箔 X/Y 包络 (局部系)"""
    xs0 = ys0 = 1e18
    xs1 = ys1 = -1e18
    for p in mod["pads"]:
        at = rot90(p["at"]) if rot == 90 else p["at"]
        # ★pad 的长轴随封装一起转: size (w,h) -> rot90 => (h,w)★
        sz = [p["size"][1], p["size"][0]] if rot == 90 else p["size"]
        x0 = at[0] - sz[0] / 2.0
        x1 = at[0] + sz[0] / 2.0
        y0 = at[1] - sz[1] / 2.0
        y1 = at[1] + sz[1] / 2.0
        xs0 = min(xs0, x0)
        xs1 = max(xs1, x1)
        ys0 = min(ys0, y0)
        ys1 = max(ys1, y1)
    if xs0 > xs1:
        return None
    return [round(xs0, 6), round(ys0, 6), round(xs1, 6), round(ys1, 6)]


def mod_pitch(mod: dict, rot: int = 90):
    """焊盘排距 (旋转后)"""
    pts = []
    for p in mod["pads"]:
        at = rot90(p["at"]) if rot == 90 else p["at"]
        pts.append(at)
    if len(pts) < 2:
        return None
    # ★排距轴 = 焊盘中心连线方向上的投影差 (1×N 直排 ⇒ 取最大跨度方向)★
    xs = sorted({round(q[0], 6) for q in pts})
    ys = sorted({round(q[1], 6) for q in pts})
    if len(xs) > 1:
        return round((xs[-1] - xs[0]) / (len(xs) - 1), 6)
    if len(ys) > 1:
        return round((ys[-1] - ys[0]) / (len(ys) - 1), 6)
    return None


def mod_annular_ring(mod: dict):
    vals = []
    for p in mod["pads"]:
        if p["drill"] > 0:
            vals.append((min(p["size"]) - p["drill"]) / 2.0)
    if not vals:
        return None
    return round(min(vals), 6)


# --------------------------------------------------------------------------------------------------
# 板面读数 (★纯文本解析 .kicad_pcb·不依赖 pcbnew★)
# --------------------------------------------------------------------------------------------------
def board_fp_block(pcb_text: str, ref: str) -> str:
    """取含 (property "Reference" "<ref>" 的 footprint 块"""
    key = '(property "Reference" "%s"' % ref
    pos = pcb_text.find(key)
    if pos < 0:
        return ""
    start = pcb_text.rfind("(footprint", 0, pos)
    if start < 0:
        return ""
    depth = 0
    i = start
    n = len(pcb_text)
    while i < n:
        if pcb_text[i] == "(":
            depth += 1
        elif pcb_text[i] == ")":
            depth -= 1
            if depth == 0:
                return pcb_text[start:i + 1]
        i += 1
    return ""


def board_fp_geom(pcb_text: str, ref: str) -> dict:
    blk = board_fp_block(pcb_text, ref)
    if not blk:
        return {}
    om = re.search(r"\n\s*\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)", blk)
    origin = [float(om.group(1)), float(om.group(2))] if om else [0.0, 0.0]
    rot = float(om.group(3)) if (om and om.group(3)) else 0.0
    pads = []
    for m in re.finditer(
        r'\(pad\s+"([^"]+)"\s+(\S+)\s+(\S+)\s*\n\s*\(at\s+([-\d.]+)\s+([-\d.]+)\)\s*\n\s*\(size\s+([-\d.]+)\s+([-\d.]+)\)',
        blk,
    ):
        num, ptype, shape, ax, ay, sx, sy = m.groups()
        pads.append({"num": num, "type": ptype, "shape": shape,
                     "at": [float(ax), float(ay)],
                     "size": [float(sx), float(sy)]})
    xs = []
    ys = []
    for p in pads:
        cx = origin[0] + p["at"][0]
        cy = origin[1] + p["at"][1]
        xs += [cx - p["size"][0] / 2.0, cx + p["size"][0] / 2.0]
        ys += [cy - p["size"][1] / 2.0, cy + p["size"][1] / 2.0]
    fab = []
    for gx, gy in _fab_pts(blk):
        fab.append([origin[0] + gx, origin[1] + gy])
    out = {"origin": origin, "rot": rot, "pads": pads}
    if xs:
        out["copper_x"] = [round(min(xs), 6), round(max(xs), 6)]
        out["copper_x_width"] = round(max(xs) - min(xs), 6)
        out["copper_y"] = [round(min(ys), 6), round(max(ys), 6)]
        out["copper_y_width"] = round(max(ys) - min(ys), 6)
    if fab:
        out["fab_x_width"] = round(max(p[0] for p in fab) - min(p[0] for p in fab), 6)
        out["fab_y_width"] = round(max(p[1] for p in fab) - min(p[1] for p in fab), 6)
    return out


# --------------------------------------------------------------------------------------------------
# 判据常量 / 座体清空区 解析 (★从真身取·不许写死★)
# --------------------------------------------------------------------------------------------------
def parse_crit(crit_py: str) -> dict:
    """CRIT = 2 * TOL["fdm_part"] ; TOL["fdm_part"] = 0.30"""
    out = {}
    tm = re.search(r'"fdm_part"\s*:\s*([-\d.]+)', crit_py)
    if not tm:
        tm = re.search(r"'fdm_part'\s*:\s*([-\d.]+)", crit_py)
    if tm:
        out["fdm_part"] = float(tm.group(1))
    cm = re.search(r"CRIT\s*=\s*2\s*\*\s*TOL\[\"fdm_part\"\]", crit_py)
    if cm:
        out["formula"] = 'CRIT = 2 * TOL["fdm_part"]'
    if "fdm_part" in out:
        out["crit"] = round(2 * out["fdm_part"], 6)
    return out


PAIR_RE = re.compile(r"X\s+([\d.]+)\.\.([\d.]+)\s*[×x]\s*Y\s+([\d.]+)\.\.([\d.]+)")
OPEN_RE = re.compile(r"开口\s*X\s*([\d.]+)\.\.([\d.]+)\s*[×x]\s*Y\s+([\d.]+)\.\.([\d.]+)")


def parse_caliber(cal: str) -> dict:
    """从 `MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md` 解析两件的必须清空区与开口
    ★逐行扫: 只认【写着「必须清空区」的行】与【写着「开口」的行】⇒ 不吃板框尺寸★
    ★按 X 排序取最小 = J_UART 侧 (UART 检修口), 取最大 = J_DEBUG 侧 (调试口)★
    ★两个口径不同源, 各自独立取, 不许互相套用★"""
    out = {"must_clear_pairs": [], "opening_pairs": []}
    for line in cal.splitlines():
        for m in PAIR_RE.finditer(line):
            head = line[:m.start()]
            mi = head.rfind("必须清空区")
            oi = head.rfind("开口")
            pair = [[float(m.group(1)), float(m.group(2))],
                    [float(m.group(3)), float(m.group(4))]]
            if mi > oi:
                out["must_clear_pairs"].append(pair)
            elif oi >= 0:
                out["opening_pairs"].append(pair)
    mc = sorted(out["must_clear_pairs"], key=lambda p: p[0][0])
    op = sorted(out["opening_pairs"], key=lambda p: p[0][0])
    if mc:
        out["juart_must_clear"] = mc[0]
        out["jdebug_must_clear"] = mc[-1]
    if op:
        out["juart_opening"] = op[0]
        out["jdebug_opening"] = op[-1]
    return out


# ==================================================================================================
# 闸实现
# ==================================================================================================
def _gate(name: str, errs: list, notes: list, skipped: bool = False) -> dict:
    return {"gate": name, "ok": (not errs), "errors": errs, "notes": notes, "skipped": skipped}


def load_page(root: str):
    p = os.path.join(root, PAGE_REL)
    if not os.path.exists(p):
        return None, ""
    t = read_text(p)
    return parse_machine_block(t), t


def j0_official_land(ctx) -> dict:
    """官方 1×2 THT land 几何必须与盘上 `.kicad_mod` 实读一致 (★自己解析·不许写死 2.2700★)"""
    errs, notes = [], []
    mods = ctx["mods"]
    tht = mods.get("tht_1x02")
    if not tht:
        return _gate("J0", ["读不到官方 1×2 THT `.kicad_mod`"], notes)
    m = tht
    if len(m["pads"]) != 2:
        errs.append("THT 1×2 pad 数应为 2, 实读 %d" % len(m["pads"]))
    pitch = mod_pitch(m)
    box = mod_copper_box(m)
    if box is None:
        errs.append("THT 1×2 铜箔包络算不出来")
        return _gate("J0", errs, notes)
    cx_w = round(box[2] - box[0], 6)
    notes.append("实读 pitch=%s 铜箔 X 宽=%.4f (包络 %s)" % (pitch, cx_w, box))
    if not near(pitch, 1.27):
        errs.append("THT 1×2 pitch 实读 %s ≠ 1.27" % pitch)
    for i, p in enumerate(m["pads"]):
        if p["drill"] <= 0:
            errs.append("THT pad %s 没有 drill" % p["num"])
        if p["type"] != "thru_hole":
            errs.append("THT pad %s type=%s ≠ thru_hole" % (p["num"], p["type"]))
    if m["crtyd"] is None:
        errs.append("THT 1×2 读不到 `fp_rect`")
    ar = mod_annular_ring(m)
    if ar is None:
        errs.append("THT 1×2 算不出环宽")
    else:
        notes.append("实读环宽=%.4f" % ar)
    # ★页里声明的官方 land 真值必须与盘上 `.kicad_mod` 逐项一致★
    land = ((ctx["mb"] or {}).get("official_land") or {}).get("tht_1x02") or {}
    if land:
        if not near(land.get("pitch"), pitch):
            errs.append("页里 THT 1×2 pitch %r ≠ 实读 %r" % (land.get("pitch"), pitch))
        if land.get("crtyd") != m["crtyd"]:
            errs.append("页里 THT 1×2 `fp_rect` %r ≠ 实读 %r" % (land.get("crtyd"), m["crtyd"]))
        if land.get("fab") != m["fab"]:
            errs.append("页里 THT 1×2 `F.Fab` %r ≠ 实读 %r" % (land.get("fab"), m["fab"]))
        if not near(land.get("annular_ring"), ar):
            errs.append("页里 THT 1×2 环宽 %r ≠ 实算 %r" % (land.get("annular_ring"), ar))
        for i, key in ((0, "pad1"), (1, "pad2")):
            lp = land.get(key) or {}
            if not near(lp.get("at", [9, 9])[0], m["pads"][i]["at"][0]) or \
               not near(lp.get("at", [9, 9])[1], m["pads"][i]["at"][1]):
                errs.append("页里 THT 1×2 %s 坐标 %r ≠ 实读 %r" % (key, lp.get("at"), m["pads"][i]["at"]))
            if not near(lp.get("size", [9, 9])[0], m["pads"][i]["size"][0]):
                errs.append("页里 THT 1×2 %s 尺寸 %r ≠ 实读 %r" % (key, lp.get("size"), m["pads"][i]["size"]))
            if not near(lp.get("drill"), m["pads"][i]["drill"]):
                errs.append("页里 THT 1×2 %s 钻孔 %r ≠ 实读 %r" % (key, lp.get("drill"), m["pads"][i]["drill"]))
    ctx["tht_copper_x_width"] = cx_w
    ctx["tht_pitch"] = pitch
    ctx["tht_annular_ring"] = ar
    ctx["tht_mod"] = m
    return _gate("J0", errs, notes)


def j1_tiers_match_recompute(ctx) -> dict:
    """§2 三档量差表逐格与实算一致 (★不许拿 THT 的数套 SMD 变体★)"""
    errs, notes = [], []
    mb = ctx["mb"]
    if not mb:
        return _gate("J1", [], ["页机器块缺失 ⇒ SKIP (页存在性归 J5)"], skipped=True)
    tiers = {t.get("tier"): t for t in mb.get("tiers", [])}
    if not tiers:
        errs.append("页机器块里没有 tiers")
        return _gate("J1", errs, notes)

    # 现状
    cur = ctx["board"].get("J_UART", {})
    cur_w = cur.get("copper_x_width")
    t0 = tiers.get("status_quo")
    if t0 is None:
        errs.append("页里缺 status_quo 档")
    elif cur_w is None:
        errs.append("板面读不出 J_UART 现状铜箔 X 宽")
    else:
        notes.append("现状 板读=%.4f 页写=%.4f" % (cur_w, t0.get("copper_x_width")))
        if not near(cur_w, t0.get("copper_x_width", -1)):
            errs.append("现状档 铜箔 X 宽 页写 %.4f ≠ 板读 %.4f" % (t0.get("copper_x_width"), cur_w))

    # 官方 THT
    t1 = tiers.get("official_tht")
    if t1 is None:
        errs.append("页里缺 official_tht 档")
    else:
        if not near(t1.get("copper_x_width"), ctx.get("tht_copper_x_width")):
            errs.append("THT 档 铜箔 X 宽 页写 %.4f ≠ `.kicad_mod` 实算 %.4f"
                        % (t1.get("copper_x_width", -1), ctx.get("tht_copper_x_width", -1)))

    # 官方 SMD 两个变体 —— 各自用自己的 mod 算, 逐格比
    for key, tier_name in (("smd_pin1left", "official_smd_pin1left"),
                           ("smd_pin1right", "official_smd_pin1right")):
        t = tiers.get(tier_name)
        if t is None:
            errs.append("页里缺 %s 档" % tier_name)
            continue
        mm = ctx["mods"].get(key)
        if not mm:
            errs.append("读不到 %s 的 `.kicad_mod`" % key)
            continue
        box = mod_copper_box(mm)
        if box is None:
            errs.append("%s 铜箔包络算不出来" % key)
            continue
        sx_w = round(box[2] - box[0], 6)
        sy_w = round(box[3] - box[1], 6)
        notes.append("%s 实算 铜箔 X=%.4f Y=%.4f" % (key, sx_w, sy_w))
        if not near(t.get("copper_x_width"), sx_w):
            errs.append("%s 档 铜箔 X 宽 页写 %.4f ≠ 实算 %.4f"
                        % (tier_name, t.get("copper_x_width", -1), sx_w))
        if not near(t.get("copper_y_width"), sy_w):
            errs.append("%s 档 铜箔 Y 宽 页写 %.4f ≠ 实算 %.4f"
                        % (tier_name, t.get("copper_y_width", -1), sy_w))
        if near(t.get("copper_x_width"), ctx.get("tht_copper_x_width")):
            errs.append("%s 档 铜箔 X 宽 与 THT 档相同 ⇒ 疑似套用了 THT 的数" % tier_name)

    # 方向与 verdict 自洽
    for t in tiers.values():
        w = t.get("copper_x_width")
        mg = t.get("margin_nominal")
        if w is None or mg is None:
            continue
        exp = round((ctx["juart_mc_w"] - w) / 2.0, 6)
        if not near(mg, exp):
            errs.append("%s 档 每边余量 页写 %.4f ≠ 由铜箔宽实算 %.4f" % (t.get("tier"), mg, exp))
    return _gate("J1", errs, notes)


def j2_must_clear_and_bookkeeping(ctx) -> dict:
    """座体必须清空区 X 宽必须 ≥ 铜箔 X 宽 (不许越界) + 越界/不足事实必须被显式记账"""
    errs, notes = [], []
    mb = ctx["mb"]
    if not mb:
        return _gate("J2", [], ["页机器块缺失 ⇒ SKIP (页存在性归 J5)"], skipped=True)
    crit = ctx["crit"]
    mc_w = ctx["juart_mc_w"]
    notes.append("座体必须清空区 X 宽 (从 %s 实读)=%.4f  CRIT=%.4f" % (CALIBER_REL, mc_w, crit))
    tiers = {t.get("tier"): t for t in mb.get("tiers", [])}
    # ★现状档必须留得住: 铜箔 X 宽 ≤ 座体必须清空区 X 宽 − 2×CRIT (否则现状就装不下)★
    t0 = tiers.get("status_quo")
    if t0 is not None and t0.get("copper_x_width") is not None:
        limit = round(mc_w - 2 * crit, 6)
        if t0["copper_x_width"] > limit + TOL:
            errs.append("现状档 铜箔 X 宽 %.4f > 座体清空区 %.4f − 2×CRIT %.4f = %.4f ⇒ 现状就装不下"
                        % (t0["copper_x_width"], mc_w, crit, limit))
        notes.append("现状 铜箔 X 宽 %.4f ≤ 上限 %.4f (%.4f − 2×%.2f)"
                     % (t0["copper_x_width"], limit, mc_w, crit))
    for name, t in tiers.items():
        w = t.get("copper_x_width")
        if w is None:
            continue
        mg = t.get("margin_nominal")
        # ★每边余量必须由铜箔 X 宽实算得出 (不许手写一个数)★
        exp_mg = round((mc_w - w) / 2.0, 6)
        if mg is None:
            errs.append("%s 档 没写每边余量 ⇒ 不足事实没被记账" % name)
            continue
        if not near(mg, exp_mg):
            errs.append("%s 档 每边余量 页写 %.4f ≠ 由铜箔 X 宽 %.4f 实算 %.4f"
                        % (name, mg, w, exp_mg))
        if mg < crit and t.get("pass_nominal") is not False:
            errs.append("%s 档 每边余量 %.4f < CRIT %.4f 但页面写 pass_nominal=%r ⇒ 不足事实被掩盖"
                        % (name, mg, crit, t.get("pass_nominal")))
        if mg < crit:
            v = (t.get("verdict") or "")
            if "FAIL" not in v.upper():
                errs.append("%s 档 判决串缺 FAIL ⇒ 不足事实没被显式记账 (%r)" % (name, v))
            notes.append("%s 档 余量 %.4f < CRIT ⇒ 差 %.4f (已记账)" % (name, mg, crit - mg))
        if w > mc_w and not (t.get("verdict") or "").upper().startswith("FAIL"):
            errs.append("%s 档 铜箔 X 宽 %.4f > 必须清空区 %.4f ⇒ 越界事实没被记账"
                        % (name, w, mc_w))
    return _gate("J2", errs, notes)


def j3_margin_symmetric_and_crit(ctx) -> dict:
    """每边余量对称且 ≥ CRIT (从真身取 CRIT·不许写死) + 最坏余量 (±fdm_part) 也要判"""
    errs, notes = [], []
    mb = ctx["mb"]
    if not mb:
        return _gate("J3", [], ["页机器块缺失 ⇒ SKIP (页存在性归 J5)"], skipped=True)
    crit = ctx["crit"]
    tol = ctx["fdm_part"]
    for t in mb.get("tiers", []):
        mg = t.get("margin_nominal")
        w = t.get("copper_x_width")
        if mg is None or w is None:
            continue
        mc = ctx["juart_mc_w"]
        left = (ctx["juart_mc_x0"] + (mc - w) / 2.0) - ctx["juart_mc_x0"]
        right = ctx["juart_mc_x1"] - (ctx["juart_mc_x1"] - (mc - w) / 2.0)
        if not near(left, right):
            errs.append("%s 档 左右余量不对称: %.4f / %.4f" % (t.get("tier"), left, right))
        exp_worst = round(mg - tol, 6)
        if not near(t.get("margin_worst"), exp_worst):
            errs.append("%s 档 最坏余量 页写 %.4f ≠ %.4f (每边余量 − fdm_part %.2f)"
                        % (t.get("tier"), t.get("margin_worst", -1), exp_worst, tol))
        exp_pass = exp_worst >= crit
        if bool(t.get("pass_worst")) != exp_pass:
            errs.append("%s 档 pass_worst 页写 %r ≠ 实算 %r"
                        % (t.get("tier"), t.get("pass_worst"), exp_pass))
        notes.append("%s 档 每边 %.4f (最坏 %.4f) %s CRIT %.4f"
                     % (t.get("tier"), mg, exp_worst, "过" if mg >= crit else "不过", crit))
    return _gate("J3", errs, notes)


def j4_smd_variants_separate(ctx) -> dict:
    """SMD 降级变体几何独立实测并单列 (Pin1Left 与 Pin1Right 两个变体各自算)"""
    errs, notes = [], []
    mb = ctx["mb"]
    if not mb:
        return _gate("J4", [], ["页机器块缺失 ⇒ SKIP (页存在性归 J5)"], skipped=True)
    tiers = {t.get("tier"): t for t in mb.get("tiers", [])}
    for tier_name, key in (("official_smd_pin1left", "smd_pin1left"),
                           ("official_smd_pin1right", "smd_pin1right")):
        t = tiers.get(tier_name)
        if t is None:
            errs.append("页里缺 %s 档 ⇒ SMD 变体没有单列" % tier_name)
            continue
        mm = ctx["mods"].get(key)
        if not mm:
            errs.append("读不到 %s 的 `.kicad_mod`" % key)
            continue
        # md5 台账必须与盘上文件一致
        want = ctx["mod_md5"].get(key)
        decl = ((mb.get("official_land") or {}).get(key) or {}).get("md5")
        if decl != want:
            errs.append("%s 的 md5 台账 页写 %r ≠ 盘上 %r" % (key, decl, want))
        # 两个变体必须各自带自己的 pad 真值, 且 pad 位置互不为同
        land = (mb.get("official_land") or {}).get(key) or {}
        p1 = land.get("pad1") or {}
        p2 = land.get("pad2") or {}
        if not p1 or not p2:
            errs.append("%s 的 pad 真值没写全" % key)
            continue
        if not near(p1.get("at", [9, 9])[0], mm["pads"][0]["at"][0]) or \
           not near(p1.get("at", [9, 9])[1], mm["pads"][0]["at"][1]):
            errs.append("%s pad1 坐标 页写 %r ≠ `.kicad_mod` 实读 %r" % (key, p1.get("at"), mm["pads"][0]["at"]))
        if not near(p2.get("at", [9, 9])[0], mm["pads"][1]["at"][0]) or \
           not near(p2.get("at", [9, 9])[1], mm["pads"][1]["at"][1]):
            errs.append("%s pad2 坐标 页写 %r ≠ `.kicad_mod` 实读 %r" % (key, p2.get("at"), mm["pads"][1]["at"]))
        notes.append("%s md5=%s pad1@%s pad2@%s" % (key, want, mm["pads"][0]["at"], mm["pads"][1]["at"]))
    # 两个变体必须真的不同 (pad 序左右互换) ⇒ 不许只写一个
    a = ctx["mods"].get("smd_pin1left")
    b = ctx["mods"].get("smd_pin1right")
    if a and b:
        if a["pads"][0]["at"] == b["pads"][0]["at"]:
            errs.append("Pin1Left 与 Pin1Right 的 pad1 坐标相同 ⇒ 两个变体没各自算")
        notes.append("Pin1Left pad1@%s vs Pin1Right pad1@%s" % (a["pads"][0]["at"], b["pads"][0]["at"]))
    return _gate("J4", errs, notes)


def j5_two_parts_side_by_side(ctx) -> dict:
    """`J_DEBUG` / `J_UART` 两件方向结论必须并排出现在页里 ⇒ 只写一颗 ⇒ 红
    ★★专防「拿一颗件的结论套另一颗」★★"""
    errs, notes = [], []
    mb = ctx["mb"]
    page_text = ctx["page_text"]
    if not mb:
        return _gate("J5", ["★真相页缺失或机器块缺失 ⇒ J_UART 与 J_DEBUG 无法并排★"], notes)
    if not page_text:
        return _gate("J5", ["★真相页缺失 ⇒ 两件方向结论无法并排★"], notes)
    for ref in ("J_UART", "J_DEBUG"):
        if ref not in page_text:
            errs.append("页里找不到 %s ⇒ 两件没有并排" % ref)
    direction = mb.get("direction") or {}
    ju = direction.get("J_UART")
    jd = direction.get("J_DEBUG")
    if not ju or not jd:
        errs.append("页机器块里 direction 缺 J_UART 或 J_DEBUG ⇒ 两件没有并排")
        return _gate("J5", errs, notes)
    notes.append("direction: J_UART=%r / J_DEBUG=%r" % (ju, jd))
    if ju == jd:
        errs.append("两件方向结论相同 (%r) ⇒ 口径不同源的方向相反结论没写出来" % ju)
    # ★方向必须【语义相反】(一红一绿) ⇒ 就算两串字不同、但都写绿, 也红★
    ju_red = str(ju).upper().startswith("RED")
    jd_red = str(jd).upper().startswith("RED")
    if ju_red == jd_red:
        errs.append("两件方向不是一红一绿 (J_UART=%r / J_DEBUG=%r) ⇒ 方向相反的结论没写出来"
                    % (ju, jd))
    reg = mb.get("must_clear_regime") or {}
    if reg.get("J_UART") == reg.get("J_DEBUG"):
        errs.append("两件清空区口径相同 (%r) ⇒ 口径不同源没写出来" % reg.get("J_UART"))
    notes.append("口径: J_UART=%r / J_DEBUG=%r" % (reg.get("J_UART"), reg.get("J_DEBUG")))
    if reg.get("J_UART") != "body_driven" or reg.get("J_DEBUG") != "copper_driven":
        errs.append("清空区口径不是 (J_UART=body_driven / J_DEBUG=copper_driven) ⇒ 根因没钉住")

    # 姊妹件 J_DEBUG 的数必须由它自己的来源重算 (1×4 mod + 它自己的必须清空区 + 它自己的开口)
    sib = mb.get("sibling") or {}
    m4 = ctx["mods"].get("tht_1x04")
    if not m4:
        errs.append("读不到官方 1×4 THT `.kicad_mod` ⇒ 姊妹件无法独立复算")
    else:
        box = mod_copper_box(m4)
        if box:
            w4 = round(box[2] - box[0], 6)
            if not near(sib.get("copper_x_width"), w4):
                errs.append("J_DEBUG 铜箔 X 宽 页写 %r ≠ 1×4 `.kicad_mod` 实算 %.4f"
                            % (sib.get("copper_x_width"), w4))
            else:
                notes.append("J_DEBUG 实算铜箔 X 宽=%.4f (1×4 mod 独立复算)" % w4)
        mcj = ctx.get("jdebug_mc")
        opj = ctx.get("jdebug_opening")
        if mcj and opj:
            # ★J_DEBUG = 铜箔支配口径 ⇒ 居中参考取【板读铜箔中心】(不是座体清空区显示值)★
            jd = ctx["board"].get("J_DEBUG") or {}
            copper = jd.get("copper_x")
            mc_c = ((copper[0] + copper[1]) / 2.0) if copper else (mcj[0][0] + mcj[0][1]) / 2.0
            # J_DEBUG = 铜箔支配 ⇒ 铜箔落在必须清空区内 ⇒ 真判据是 开口 vs 铜箔
            exp_margin = None
            try:
                # 居中解: 铜箔中心 = 板读铜箔中心
                cx0 = mc_c - (sib.get("copper_x_width") or 0) / 2.0
                cx1 = mc_c + (sib.get("copper_x_width") or 0) / 2.0
                exp_margin = round(min(cx0 - opj[0][0], opj[0][1] - cx1), 6)
            except Exception:
                exp_margin = None
            if exp_margin is not None:
                if not near(sib.get("opening_margin_left"), exp_margin):
                    errs.append("J_DEBUG 开口单边余量 页写 %r ≠ 实算 %.4f"
                                % (sib.get("opening_margin_left"), exp_margin))
                else:
                    notes.append("J_DEBUG 开口单边余量 实算=%.4f (独立复算)" % exp_margin)
            # 两件方向必须相反 ⇒ 用实算再验一次
            ju_w = None
            for t in mb.get("tiers", []):
                if t.get("tier") == "official_tht":
                    ju_w = t.get("copper_x_width")
            if ju_w is not None and exp_margin is not None:
                ju_mg = (ctx["juart_mc_w"] - ju_w) / 2.0
                if (exp_margin >= ctx["crit"]) == (ju_mg >= ctx["crit"]):
                    errs.append("实算两件同向 (J_UART 余量 %.4f / J_DEBUG 余量 %.4f) ⇒ 口径链算错了"
                                % (ju_mg, exp_margin))
    return _gate("J5", errs, notes)


def j6_board_zero_write(ctx) -> dict:
    """板面零写板自证 (md5 / mtime / size 三项)"""
    errs, notes = [], []
    pcb = ctx["pcb_path"]
    if not os.path.exists(pcb):
        return _gate("J6", ["板文件不存在"], notes)
    md5 = md5_of(pcb)
    st = os.stat(pcb)
    import datetime
    ns = st.st_mtime_ns
    mtime = datetime.datetime.fromtimestamp(ns / 1e9).strftime("%Y-%m-%d %H:%M:%S.%f")
    notes.append("md5=%s" % md5)
    notes.append("mtime=%s (ns=%d)" % (mtime, ns))
    notes.append("size=%d" % st.st_size)
    if md5 != BOARD_BASELINE["md5"]:
        errs.append("板 md5 %s ≠ 基线 %s" % (md5, BOARD_BASELINE["md5"]))
    base_ns = mtime_ns_of(BOARD_BASELINE["mtime"])
    if ns != base_ns:
        errs.append("板 mtime %s (ns=%d) ≠ 基线 %s (ns=%d)"
                    % (mtime, ns, BOARD_BASELINE["mtime"], base_ns))
    if st.st_size != BOARD_BASELINE["size"]:
        errs.append("板 size %d ≠ 基线 %d" % (st.st_size, BOARD_BASELINE["size"]))
    return _gate("J6", errs, notes)


def _evidence_tokens(body: str):
    # ★只认形如 [实测] 的证据标记 ⇒ 带引号的 (如 TOL["fdm_part"]) 不算证据标记★
    return set("[%s]" % t for t in re.findall(r"\[([^\[\]\"']{1,12})\]", body))


def j7_evidence_and_wording(ctx) -> dict:
    """证据等级五级白名单 + 正文零挂起措辞 + 判据句/事实句分开 + `.kicad_mod` md5 台账"""
    errs, notes = [], []
    mb = ctx["mb"]
    text = ctx["page_text"]
    if not text:
        return _gate("J7", [], ["页缺失 ⇒ SKIP (页存在性归 J5)"], skipped=True)
    prose = strip_fences(text)
    toks = _evidence_tokens(prose)
    bad = sorted(t for t in toks if t not in EVIDENCE_WHITELIST)
    if bad:
        errs.append("证据等级白名单外: %s" % ", ".join(bad))
    notes.append("证据标记 %d 种" % len(toks))
    for w in HEDGING_WORDS:
        if w in prose:
            errs.append("正文含挂起/含糊措辞 %r" % w)
    for p in FORBIDDEN_PHRASES:
        if p in prose:
            errs.append("正文含外推挂起措辞 %r" % p)
    for w in FORBIDDEN_VERDICT_WORDS:
        if w in prose:
            errs.append("正文含含混判决词 %r (判据句与事实句必须分开写)" % w)
    # 判据句 / 事实句 必须分开 (★不许写在同一行★)
    if "判据句" not in text:
        errs.append("页里没有「判据句」标记")
    if "事实句" not in text:
        errs.append("页里没有「事实句」标记")
    for line in text.splitlines():
        if "判据句" in line and "事实句" in line:
            errs.append("判据句与事实句写在同一行 ⇒ 没分开")
            break
    # md5 台账 (正文表格里必须有; 机器块里的台账由 J4 查)
    for key, want in ctx["mod_md5"].items():
        if want not in text:
            errs.append("页里缺 `.kicad_mod` md5 台账: %s = %s" % (MOD_NAMES[key], want))
    return _gate("J7", errs, notes)


def j8_zero_chaining(ctx) -> dict:
    """零挂链 ⇒ 自证 `grep -c check_juart_1p27_clearance state/gate_check.py` == 0"""
    errs, notes = [], []
    gp = ctx["gate_path"]
    if not os.path.exists(gp):
        return _gate("J8", ["state/gate_check.py 不存在"], notes)
    txt = read_text(gp)
    n = txt.count("check_juart_1p27_clearance")
    notes.append("state/gate_check.py 里 `check_juart_1p27_clearance` 命中 %d 次 (必须 0)" % n)
    if n != 0:
        errs.append("新闸被挂进 state/gate_check.py (%d 次) ⇒ 违反零挂链" % n)
    return _gate("J8", errs, notes)


# ==================================================================================================
# 主跑
# ==================================================================================================
def build_ctx(root: str, libroot: str = None) -> dict:
    libroot = libroot or LIBROOT
    ctx = {
        "root": root,
        "page_path": os.path.join(root, PAGE_REL),
        "crit_path": os.path.join(root, CRIT_REL),
        "caliber_path": os.path.join(root, CALIBER_REL),
        "pcb_path": os.path.join(root, PCB_REL),
        "gate_path": os.path.join(root, GATE_REL),
        "libroot": libroot,
    }
    mb, text = load_page(root)
    ctx["mb"] = mb
    ctx["page_text"] = text
    crit = parse_crit(read_text(ctx["crit_path"])) if os.path.exists(ctx["crit_path"]) else {}
    ctx["crit"] = crit.get("crit", 0.60)
    ctx["fdm_part"] = crit.get("fdm_part", 0.30)
    if "crit" not in crit:
        ctx.setdefault("_notes", []).append("★CRIT 真身读不到 ⇒ 按 0.60 处理★")
    cal = parse_caliber(read_text(ctx["caliber_path"])) if os.path.exists(ctx["caliber_path"]) else {}
    ctx["caliber"] = cal
    jm = cal.get("juart_must_clear")
    ctx["juart_mc_x0"] = jm[0][0] if jm else 0.0
    ctx["juart_mc_x1"] = jm[0][1] if jm else 0.0
    ctx["juart_mc_w"] = round(jm[0][1] - jm[0][0], 6) if jm else 0.0
    ctx["jdebug_mc"] = cal.get("jdebug_must_clear")
    ctx["jdebug_opening"] = cal.get("jdebug_opening")
    ctx["juart_opening"] = cal.get("juart_opening")
    pcb_text = read_text(ctx["pcb_path"]) if os.path.exists(ctx["pcb_path"]) else ""
    ctx["pcb_text"] = pcb_text
    ctx["board"] = {
        "J_UART": board_fp_geom(pcb_text, "J_UART"),
        "J_DEBUG": board_fp_geom(pcb_text, "J_DEBUG"),
    }
    mods = {}
    md5s = {}
    for key, name in MOD_NAMES.items():
        p = os.path.join(libroot, FPLIB_DIR, name)
        if os.path.exists(p):
            mods[key] = parse_mod(p)
            md5s[key] = md5_of(p)
    ctx["mods"] = mods
    ctx["mod_md5"] = md5s
    return ctx


def run_checks(root: str, libroot: str = None) -> dict:
    ctx = build_ctx(root, libroot)
    gates = []
    gates.append(j0_official_land(ctx))
    gates.append(j1_tiers_match_recompute(ctx))
    gates.append(j2_must_clear_and_bookkeeping(ctx))
    gates.append(j3_margin_symmetric_and_crit(ctx))
    gates.append(j4_smd_variants_separate(ctx))
    gates.append(j5_two_parts_side_by_side(ctx))
    gates.append(j6_board_zero_write(ctx))
    gates.append(j7_evidence_and_wording(ctx))
    gates.append(j8_zero_chaining(ctx))
    return {"gates": gates, "ctx": ctx}


def print_report(res: dict) -> int:
    bad = 0
    print("=== MECH/check_juart_1p27_clearance.py · ISS-374 · J_UART 排针 1.27mm 净距真相 ===")
    for g in res["gates"]:
        tag = "PASS" if g["ok"] else "FAIL"
        if g.get("skipped") and g["ok"]:
            tag = "SKIP"
        if not g["ok"]:
            bad += 1
        print("[%s] %s" % (tag, g["gate"]))
        for n in g["notes"]:
            print("       · %s" % n)
        for e in g["errors"]:
            print("       ✗ %s" % e)
    print("---")
    if bad:
        print("RESULT: FAIL (%d 条判据不通过)" % bad)
    else:
        print("RESULT: PASS (9/9 判据通过)")
    return 1 if bad else 0


# ==================================================================================================
# 反向用例自测
# ==================================================================================================
def _sandbox(root: str, name: str) -> str:
    d = os.path.join(root, "tmp/iss374_sbx/selftest", name)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d, exist_ok=True)
    return d


def _mirror(src: str, dst: str, link: bool = False) -> None:
    """★永远做真副本·绝不建符号链接 ★
    (★2026-11-24 实测踩坑: 用符号链接时, 沙盒里的写操作会【穿透】写到真板/真页/真 CRIT 源上
      ⇒ 板 md5 变成 3dd88de4… ⇒ 已当场回滚 (md5 / mtime ns / size 三项复原)★)"""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def _case(root: str, name: str, mutate=None, lib_mutate=None) -> dict:
    """造一个沙盒副本树, 跑一遍, 返回 {gate: ok}"""
    d = _sandbox(root, name)
    _mirror(os.path.join(root, PAGE_REL), os.path.join(d, PAGE_REL))
    _mirror(os.path.join(root, CRIT_REL), os.path.join(d, CRIT_REL))
    _mirror(os.path.join(root, CALIBER_REL), os.path.join(d, CALIBER_REL))
    _mirror(os.path.join(root, PCB_REL), os.path.join(d, PCB_REL))
    _mirror(os.path.join(root, GATE_REL), os.path.join(d, GATE_REL))
    libroot = os.path.join(d, "_lib")
    os.makedirs(os.path.join(libroot, FPLIB_DIR), exist_ok=True)
    for key, nm in MOD_NAMES.items():
        src = os.path.join(LIBROOT, FPLIB_DIR, nm)
        shutil.copy2(src, os.path.join(libroot, FPLIB_DIR, nm))
    if mutate:
        mutate(d)
    if lib_mutate:
        lib_mutate(libroot, d)
    res = run_checks(d, libroot=libroot)
    out = {}
    for g in res["gates"]:
        out[g["gate"]] = g["ok"]
    # ★沙盒跑完立刻删大文件 (板副本 4.9MB × N 用例) ⇒ 只留页副本做留证★
    try:
        os.remove(os.path.join(d, PCB_REL))
    except OSError:
        pass
    return out


def _mut_page(d: str, old: str, new: str) -> None:
    p = os.path.join(d, PAGE_REL)
    t = read_text(p)
    if old not in t:
        raise AssertionError("沙盒变异锚点找不到: %r" % old[:60])
    t = t.replace(old, new, 1)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(t)


def _mut_all(d: str, old: str, new: str) -> None:
    p = os.path.join(d, PAGE_REL)
    t = read_text(p)
    assert old in t, "沙盒变异锚点找不到: %r" % old[:60]
    t = t.replace(old, new)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(t)


def selftest(root: str) -> int:
    print("=== --selftest · ISS-374 反向用例 ===")
    # ★★护栏: 自测不得改动真件 (★2026-11-24 踩坑后加的: 沙盒必须用真副本, 不得用符号链接★)★★
    guard = {}
    for rel in (PAGE_REL, CRIT_REL, PCB_REL):
        p = os.path.join(root, rel)
        st = os.stat(p)
        guard[rel] = (md5_of(p), st.st_mtime_ns, st.st_size)
    cases = []

    def add(case_id, desc, expect_red, mutate=None, lib_mutate=None):
        cases.append((case_id, desc, expect_red, mutate, lib_mutate))

    # ①★病根: 把 J_UART 那一页删掉/改名 ⇒ J5 红、其余仍绿★
    add("T1", "★病根①: J_UART 那一页改名 ⇒ J5 红, 其余仍绿", ["J5"],
        mutate=lambda d: os.rename(os.path.join(d, PAGE_REL),
                                   os.path.join(d, "MECH/BOARD_ONEPASS_JUART_1P27_CLEARANCE_RENAMED.md")))

    # ②★病根: 把 J_UART 的 THT 铜箔宽改成 J_DEBUG 的 4.8100 ⇒ J1/J2 红★
    add("T2", "★病根②: J_UART 的 THT 铜箔宽改成 J_DEBUG 的 4.8100 ⇒ J1/J2 红", ["J1", "J2"],
        mutate=lambda d: _mut_page(d, '"copper_x_width": 2.2700', '"copper_x_width": 4.8100'))

    # ③★病根: 把 J_UART 的方向结论改成跟 J_DEBUG 一样 ⇒ J5 红★
    add("T3", "★病根③: J_UART 方向结论改成与 J_DEBUG 同向 ⇒ J5 红", ["J5"],
        mutate=lambda d: _mut_page(d, '"J_UART": "RED_structure_part_does_not_fit"',
                                   '"J_UART": "PASS_margin_3.99x"'))

    # ④★病根: 把 J_UART 的清空区口径改成 J_DEBUG 的铜箔支配 ⇒ J5 红★
    add("T4", "★病根④: J_UART 清空区口径改成 copper_driven (套 J_DEBUG 的口径) ⇒ J5 红", ["J5"],
        mutate=lambda d: _mut_page(d, '"J_UART": "body_driven"', '"J_UART": "copper_driven"'))

    # ⑤ 官方 THT `.kicad_mod` 被改 ⇒ J0 红 (自己解析, 不写死)
    def lib_mut(libroot, d):
        p = os.path.join(libroot, FPLIB_DIR, MOD_NAMES["tht_1x02"])
        t = read_text(p).replace("(start -1.55 -1.14)", "(start -1.60 -1.14)", 1)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(t)
        _mut_page(d, "47bcbf6d0f267d543e50d4b2a8dfabf5", md5_of(p))
    add("T5", "官方 1×2 THT `.kicad_mod` 的 `fp_rect` 被改 (台账同步改) ⇒ J0 红", ["J0"], lib_mutate=lib_mut)

    # ⑥ SMD 变体 md5 台账错 ⇒ J4 红
    add("T6", "SMD `Pin1Left` 的 md5 台账写错 ⇒ J4 红", ["J4"],
        mutate=lambda d: _mut_page(d, '"md5": "7f15e4a1a32059c2b8eea027edfdbd84"',
                                   '"md5": "00000000000000000000000000000000"'))

    # ⑦ 正文塞挂起措辞 ⇒ J7 红
    add("T7", "正文塞入挂起措辞「等原厂回信」⇒ J7 红", ["J7"],
        mutate=lambda d: _mut_page(d, "## §4 未决项", "## §4 未决项\n等原厂回信再说。"))

    # ⑧ 板被改 ⇒ J6 红
    def board_mut(d):
        p = os.path.join(d, PCB_REL)
        with open(p, "ab") as fh:
            fh.write(b"\n; tampered by selftest\n")
    add("T8", "板文件被追加字节 ⇒ J6 红 (零写板自证)", ["J6"], mutate=board_mut)

    # ⑨ 把 THT 档的不足事实掩盖成 pass ⇒ J2/J3 红
    add("T9", "THT 档 `pass_nominal` 被改成 true (掩盖不足) ⇒ J2 红", ["J2"],
        mutate=lambda d: _mut_page(d, '"pass_nominal": false, "pass_worst": false,\n     "fab_body_x": 2.6400',
                                   '"pass_nominal": true, "pass_worst": false,\n     "fab_body_x": 2.6400'))

    # ⑩ 把「事实句」标记整段删掉 ⇒ J7 红 (判据句/事实句 必须两句分开在)
    add("T10", "「事实句」标记被删掉 ⇒ J7 红 (判据句/事实句 两句分开的要求被破坏)", ["J7"],
        mutate=lambda d: _mut_all(d, "事实句", "观感"))

    # ⑪ 把 SMD 变体的铜箔宽换成 THT 的数 ⇒ J1 红 (不许拿 THT 的数套 SMD 变体)
    add("T11", "SMD 变体档的铜箔宽换成 THT 的 2.2700 ⇒ J1/J2 红", ["J1", "J2"],
        mutate=lambda d: _mut_page(d, '"copper_x_width": 1.9200', '"copper_x_width": 2.2700'))

    # ⑫ CRIT 真身被松 ⇒ J3 红 (判据不许被偷偷松)
    def crit_mut(d):
        p = os.path.join(d, CRIT_REL)
        t = read_text(p).replace('"fdm_part": 0.30', '"fdm_part": 0.10')
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(t)
    add("T12", "CRIT 真身被松 (fdm_part 0.30 → 0.10) ⇒ J3 红", ["J3"], mutate=crit_mut)

    ok_all = True
    for cid, desc, expect_red, mutate, lib_mutate in cases:
        got = _case(root, cid, mutate=mutate, lib_mutate=lib_mutate)
        reds = sorted([k for k, v in got.items() if not v])
        expect = sorted(expect_red)
        good = (reds == expect)
        ok_all = ok_all and good
        print("  [%s] %-4s %s" % ("OK" if good else "XX", cid, desc))
        print("        红: %s (期望 %s)" % (",".join(reds) or "无", ",".join(expect) or "无"))
        if not good:
            for k in sorted(set(reds) | set(expect)):
                if (k in reds) != (k in expect):
                    print("        ✗ %s 状态不符" % k)
    print("---")
    # ★★护栏收尾: 真件必须逐字节未变 (md5 / mtime ns / size) ★★
    for rel, (h0, m0, s0) in guard.items():
        p = os.path.join(root, rel)
        st = os.stat(p)
        h1 = md5_of(p)
        if (h1, st.st_mtime_ns, st.st_size) != (h0, m0, s0):
            ok_all = False
            print("  [XX] ★★护栏触发: %s 在自测过程中被改了 ⇒ 沙盒写法有穿透★★" % rel)
            print("        md5 %s → %s / mtime_ns %d → %d / size %d → %d" % (h0, h1, m0, st.st_mtime_ns, s0, st.st_size))
        else:
            print("  [OK] 护栏: %s 逐字节未变 (md5 %s)" % (rel, h1))
    if ok_all:
        print("ALL TESTS PASS (%d/%d)" % (len(cases), len(cases)))
        return 0
    print("SELFTEST FAIL")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=None)
    ap.add_argument("--libroot", default=None)
    args = ap.parse_args()
    root = os.path.abspath(args.root) if args.root else PROJ
    if not os.path.isdir(root):
        print("root 不存在: %s" % root)
        return 2
    if args.selftest:
        return selftest(root)
    res = run_checks(root, libroot=args.libroot)
    return print_report(res)


if __name__ == "__main__":
    sys.exit(main())
