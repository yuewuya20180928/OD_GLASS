#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-403 · mech-lead · 「板那一趟」焊盘尺寸 ⇄ MECH 判决链 7 个数 · ★耦合闭包闸★

★**本闸只判一件事**: ★**「焊盘尺寸一旦被放大, MECH 判决链吃的 7 个数会不会被自动发现并重新推导」** ★
★**零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 · 不自签** ★

────────────────────────────────────────────────────────────────────────────────
★★【本闸的预期读数 = rc=0 (绿)】★★
  ★**绿的理由**: ★**现状 pad 仍是 `1.000` ⇒ 7 个数与 `.kicad_mod` 实算【自洽】⇒ 一切判据成立** ★
  ★⇒ 本闸【不替 main 拍焊盘档位】(★机器块 `decision_taken_here` 必须是 `not_decided_here`★) ★
  ★⇒ 本闸【零挂链】⇒ 它【不在门禁链上跑】⇒ ★**红了也要靠人去跑** ⇒ 这是【本单交付的现状】★

────────────────────────────────────────────────────────────────────────────────
判据 (★逐条定义写在真相页 `MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md` §7 机器块 `gate_criteria`★):
  P1 (A1) ★pad 档位必须从 `.kicad_mod` 【现读】(★不许写死 `1.0`★) ⇒ 与机器块 `current_pad` / `pad_tiers` 逐字一致
  P2 (A2) ★7 个数必须从【pad 档位】推导出来 (★不许写死★) ⇒ 闸自算 vs 机器块 `seven_numbers_matrix` 逐格一致
  P3 (A3) ★判决链消费的数 (copper_x / copper_y / 清空区需求 / 罩住余量 / 开口余量)
        必须与 `.kicad_mod` 实算【逐格一致】⇒ vs 机器块 `verdict_chain_current`
  P4 (A4) ★盲闸名单不许凭空 ⇒ 每个名字必须【真在盘上】+【真能实跑出登记的红项集合】
        +【源码里没有库读入口 ⇒ 结构上不可能看见焊盘尺寸】+ 名单【不重不漏】(7 道全覆盖)
  P5 (A5) ★零挂链自证 ⇒ `grep -c check_pad_size_coupling_closed state/gate_check.py` == 0
  P6 (A6) ★证据分级五级白名单 + 零挂起措辞 + 「判据句 / 事实句」分开 + 不代拍
  P7 (A7) ★板面零写板自证 (md5 / mtime / size 三项)
  P8 (A8) ★零外发自证 (★`state/outbox/` 一个字节没动⇒ 树摘要逐字一致★)

用法:
  python3 MECH/check_pad_size_coupling_closed.py              # 裸跑, rc=0 = 现状自洽
  python3 MECH/check_pad_size_coupling_closed.py --selftest   # 正向 ≥1 + 反向 ≥8, 末行 ALL TESTS PASS
  python3 MECH/check_pad_size_coupling_closed.py --root DIR    # 指定树
  python3 MECH/check_pad_size_coupling_closed.py --libroot DIR # 指定 KiCad 官方库根

★【沙盒纪律】反向用例一律落项目盘 `<root>/tmp/iss403_gate/selftest/` (★不许写系统 `/tmp`★)
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

# ── 真源相对路径 ──
PAGE_REL = "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md"
OPENING_REL = "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md"
CRIT_REL = "MECH/service_port_check.py"
CHAIN_REL = "state/gate_check.py"
BOARD_REL = "HW/PCB/demo_mainboard.kicad_pcb"
OUTBOX_REL = "state/outbox"
HANDOFF_REL = "HANDOFF/2026-11-25_mech-lead_ISS403_焊盘尺寸耦合盲区清账与闸.md"

# ── 官方 KiCad 库 (★pad 尺寸的真身在这里★) ──
LIBROOT_DEFAULT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
LIBDIR = "Connector_PinHeader_1.27mm.pretty"
MODS = {"J_DEBUG": "PinHeader_1x04_P1.27mm_Vertical.kicad_mod",
        "J_UART": "PinHeader_1x02_P1.27mm_Vertical.kicad_mod"}

# ── 7 个数名 (★与真相页 §3.1 逐字一致★) ──
SEVEN = ("j_debug_copper_x", "j_uart_copper_x", "j_debug_required_clear_x",
         "j_uart_required_clear_x", "j_uart_cover_margin_x",
         "j_debug_opening_margin_x", "j_debug_cover_margin_y")
# ── 判决链消费的数 (★A3 逐格★) ──
CHAIN_KEYS = ("copper_x_j_debug", "copper_y_j_debug", "copper_x_j_uart", "copper_y_j_uart",
              "required_clear_x_j_debug", "required_clear_x_j_uart",
              "cover_margin_x_j_uart", "opening_margin_x_j_debug", "cover_margin_y_j_debug")

# ── 证据等级五级白名单 (★照 MECH/check_jdebug_1p27_clearance.py L97-L102 的现成形状★) ──
EVIDENCE_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
FORBIDDEN_EVIDENCE = ("[官方]", "[推断]", "[推测]", "[估计]", "[大概]", "[可能]", "[大概值]")
HEDGING_WORDS = ("可能", "大概", "应该是", "似乎", "貌似", "估摸", "八成", "多半")
FORBIDDEN_PHRASES = ("等原厂回信", "等原厂回复", "等待原厂", "回头再问原厂",
                     "等外部回复", "待外部确认", "等确认", "待回复")
# ★★【元引述豁免】★★: ★**只豁免【在描述禁用名单 / 描述反向用例注入】的那几行**★
#   ★★ **不豁免普通的「不许 / 禁止」行** ⇒ ★**真相页里写一句「可能」照样红** ★★
#   ★★ **也不豁免「挂起措辞 / 无档措辞」这类【普通词】** ⇒ ★**否则反向用例 R9 自己就会被豁免掉★ ★★
META_MARKERS = ("正文塞", "禁用名单", "一律不许出现")
_EVID_TOKEN_RE = re.compile(r"\[([^\]\n]{1,14})\]")
_EVID_LIKE_RE = re.compile(r"^[\u4e00-\u9fff0-9]{1,14}$")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")

TOL = 1e-9


# ══════════════════════════════ 通用工具 ══════════════════════════════
def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def r4(x) -> float:
    return round(float(x) + 0.0, 4)


def strip_md(s: str) -> str:
    return s.replace("*", "").replace("`", "").replace("★", "").strip()


def parse_xy(s: str):
    m = re.search(r"X\s*(-?\d+(?:\.\d+)?)\s*\.\.\s*(-?\d+(?:\.\d+)?)", strip_md(s))
    m2 = re.search(r"Y\s*(-?\d+(?:\.\d+)?)\s*\.\.\s*(-?\d+(?:\.\d+)?)", strip_md(s))
    if not m or not m2:
        return None
    return ((float(m.group(1)), float(m.group(2))), (float(m2.group(1)), float(m2.group(2))))


def find_row(text: str, key: str, forbid=()) -> str:
    for ln in text.splitlines():
        s = strip_md(ln)
        if key in s and not any(f in s for f in forbid):
            return s
    return ""


def parse_mtime(s: str) -> float:
    """'2026-11-06 07:07:17.362193413' → epoch 秒 (★纳秒精度★)"""
    date, tm = s.strip().split(" ")
    hh, mm, ss = tm.split(":")
    frac = "0"
    if "." in ss:
        ss, frac = ss.split(".")
    frac = (frac + "000000000")[:9]
    dt = datetime.datetime.strptime("%s %s:%s:%s" % (date, hh, mm, ss), "%Y-%m-%d %H:%M:%S")
    return dt.timestamp() + int(frac) / 1e9


def extract_json_fence(text: str):
    """★从真相页里抽第一个 ```json 机器块★"""
    for m in re.finditer(r"```json\s*\n(.*?)\n```", text, re.S):
        try:
            return json.loads(m.group(1))
        except Exception:
            continue
    return None


def evidence_tokens(body: str):
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


# ══════════════════════════════ `.kicad_mod` 现读 ══════════════════════════════
_PAD_RE = re.compile(
    r'\(pad\s+"([^"]*)"\s+(\S+)\s+(\S+)\s*\(at\s+([-\d.]+)\s+([-\d.]+)'
    r'(?:\s+[-\d.]+)?\)(?:\s*\(size\s+([-\d.]+)\s+([-\d.]+)\))?'
    r'(?:\s*\(drill\s+([-\d.]+)\))?')


def parse_mod(path: str) -> list:
    txt = read_text(path)
    pads = []
    for m in _PAD_RE.finditer(txt):
        num, ptype, shape, px, py, sx, sy, drill = m.groups()
        pads.append({"num": num, "type": ptype, "shape": shape,
                     "px": float(px), "py": float(py),
                     "sx": float(sx or 0.0), "sy": float(sy or 0.0),
                     "drill": float(drill) if drill else None})
    return pads


def tht_geom(path: str) -> dict:
    """★官方 THT land 几何 (★全部从 `.kicad_mod` 实算·不写死任何常数★)★"""
    pads = parse_mod(path)
    if not pads:
        raise AssertionError("`.kicad_mod` 里读不到焊盘: %s" % path)
    xs = sorted({round(p["px"], 6) for p in pads})
    ys = sorted({round(p["py"], 6) for p in pads})
    if len(xs) > 1 and len(ys) == 1:
        axis = "x"
    elif len(ys) > 1 and len(xs) == 1:
        axis = "y"
    else:
        axis = "?"
    first = pads[0]
    if axis == "y":
        pitch = abs(pads[1]["py"] - first["py"])
        span = max(abs(p["py"] - first["py"]) for p in pads)
        pad_along, pad_across = first["sy"], first["sx"]
    else:
        pitch = abs(pads[1]["px"] - first["px"])
        span = max(abs(p["px"] - first["px"]) for p in pads)
        pad_along, pad_across = first["sx"], first["sy"]
    return {"npads": len(pads), "axis_local": axis, "pitch": r4(pitch), "span": r4(span),
            "pad_along": r4(pad_along), "pad_across": r4(pad_across),
            "drill": first["drill"], "mod_path": path}


# ══════════════════════════════ 真源现读 ══════════════════════════════
def read_crit(root: str):
    """★CRIT / TOL 真身 (只读源码·★不许写死·★不许 import·★本机实读)★"""
    src = read_text(os.path.join(root, CRIT_REL))
    mt = re.search(r"TOL\s*=\s*\{[^}]*\}", src)
    if not mt:
        return None, None, "TOL 真身 (MECH/service_port_check.py) 没找到"
    tol = eval(mt.group(0).split("=", 1)[1])
    mc = re.search(r"CRIT\s*=\s*2\s*\*\s*TOL\[\"fdm_part\"\]", src)
    if not mc:
        return None, None, "CRIT 真身 (CRIT = 2 * TOL['fdm_part']) 没找到"
    return 2 * tol["fdm_part"], tol, None


def read_opening(root: str):
    """★从既有真相页 (只读) 现读 开口 / 必须清空区 —— 不许抄自己页里的数★"""
    txt = read_text(os.path.join(root, OPENING_REL))
    out = {}
    for key, ref in (("J_DEBUG", "调试口"), ("J_UART", "检修口")):
        h = find_row(txt, ref + " · 必须清空区", forbid=("可放行",))
        o = find_row(txt, ref + " · 开口", forbid=("可放行", "必须清空区"))
        hxy, oxy = parse_xy(h), parse_xy(o)
        if not hxy or not oxy:
            return None, "既有真相页里找不到 %s 的必须清空区 / 开口行" % key
        out[key] = {
            "housing_w": {"x": r4(hxy[0][1] - hxy[0][0]), "y": r4(hxy[1][1] - hxy[1][0])},
            "opening_w": {"x": r4(oxy[0][1] - oxy[0][0]), "y": r4(oxy[1][1] - oxy[1][0])},
        }
    return out, None


def outbox_digest(root: str):
    """★`state/outbox/` 树摘要 (★逐字·★相对路径排序★)★"""
    base = os.path.join(root, OUTBOX_REL)
    if not os.path.isdir(base):
        return None, 0
    files = []
    for dp, dn, fn in os.walk(base):
        dn.sort()
        for f in fn:
            files.append(os.path.relpath(os.path.join(dp, f), base))
    files.sort()
    h = hashlib.md5()
    for rel in files:
        fh = md5_of(os.path.join(base, rel))
        h.update(("%s  %s\n" % (fh, rel)).encode())
    return h.hexdigest(), len(files)


# ══════════════════════════════ 推导引擎 (★7 个数由 pad 档位推导·不许写死★) ══════════════════════════════
def compute_seven(pad: float, spans: dict, ho: dict, crit: float, tol_fdm: float) -> dict:
    """★7 个数 + 判决链消费的数 ⇒ 全部由 `pad` 推导 (★pad 一改 ⇒ 全变★)★"""
    dj_x = r4(spans["J_DEBUG"] + pad)
    ju_x = r4(spans["J_UART"] + pad)
    cy = r4(pad)
    need = lambda cx: r4(cx + 2.0 * (crit + tol_fdm))
    return {
        "j_debug_copper_x": dj_x,
        "j_uart_copper_x": ju_x,
        "j_debug_required_clear_x": need(dj_x),
        "j_uart_required_clear_x": need(ju_x),
        "j_uart_cover_margin_x": r4((ho["J_UART"]["housing_w"]["x"] - ju_x) / 2.0),
        "j_debug_opening_margin_x": r4((ho["J_DEBUG"]["opening_w"]["x"] - dj_x) / 2.0),
        "j_debug_cover_margin_y": r4((ho["J_DEBUG"]["housing_w"]["y"] - cy) / 2.0),
        # ── 判决链消费的数 (A3 逐格) ──
        "copper_x_j_debug": dj_x,
        "copper_y_j_debug": cy,
        "copper_x_j_uart": ju_x,
        "copper_y_j_uart": cy,
        "required_clear_x_j_debug": need(dj_x),
        "required_clear_x_j_uart": need(ju_x),
        "cover_margin_x_j_uart": r4((ho["J_UART"]["housing_w"]["x"] - ju_x) / 2.0),
        "opening_margin_x_j_debug": r4((ho["J_DEBUG"]["opening_w"]["x"] - dj_x) / 2.0),
        "cover_margin_y_j_debug": r4((ho["J_DEBUG"]["housing_w"]["y"] - cy) / 2.0),
    }


# ══════════════════════════════ 盲闸实跑 + 红项抽取 ══════════════════════════════
_RED_PATTERNS = (
    re.compile(r"^\[FAIL\]\s*([A-Za-z0-9_.]+)"),        # [FAIL] J0
    re.compile(r"^\[([A-Z]\d+)\]\s"),                    # [G1] ...
    re.compile(r"^([A-Za-z]+\d+(?:\.\d+)?)\s+FAIL"),     # K7   FAIL
)


def extract_red_items(text: str) -> list:
    """★把闸输出里的红项抽成【判据编号集合】(★确定性·★与输出细节无关★)★"""
    red = set()
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("[ok]") or s.startswith("[PASS]"):
            continue
        # ★汇总行不算判据红项 (★只抽【判据编号】★)★
        if s.startswith("RESULT:") or s.startswith("合计") or s.startswith("判据 ") \
                or s.startswith("★") or s.startswith("---"):
            continue
        # ★先判「这一行是不是红的」★
        if "❌" not in s and not re.search(r"\bFAIL\b", s):
            continue
        for pat in _RED_PATTERNS:
            m = pat.match(s)
            if m:
                red.add(m.group(1))
                break
        else:
            red.add("__FAIL__")
    return sorted(red)


# ★★【静态盲证】★★ 一个闸到底有没有【通向 KiCad 库的读入口】★★
_LIB_FN_NAMES = ("tht_geometry", "smd_geometry", "parse_mod", "parse_footprint_copper",
                 "local_envelope", "fab_box", "pin_axis")


def has_lib_read_path(src: str) -> bool:
    """★该闸源码里有没有【能读到 pad 尺寸】的入口★

    ★★【判据】★★:
      ① `LIBROOT = ...` 常量赋值 (★库根被钉死在一个可读路径上★)
      ② 任何一个【解析函数的调用】(★`def` 行不算★)
      ③ 直接把 `.kicad_mod` 字面量喂给 `open()` / `read_text()`
    ★★【为什么不是「源码里有没有出现 `kicad_mod` 这个词」】★★:
      ★`MECH/check_debug_seat_3d_fit.py` 里那个【死代码】 `parse_footprint_copper()` 的
      docstring 就写着「从官方 .kicad_mod 解析 pad」⇒ ★**按「词」判会把死代码误判成活入口**★
      ⇒ ★本判据按【调用】判 ⇒ ★**死代码不算入口** ⇒ ★这正是本单要抓的那个区别★★
    """
    if re.search(r"(?m)^\s*LIBROOT\s*=", src):
        return True
    for fn in _LIB_FN_NAMES:
        for m in re.finditer(r"\b%s\s*\(" % fn, src):
            ls = src.rfind("\n", 0, m.start()) + 1
            le = src.find("\n", m.start())
            line = src[ls:le if le >= 0 else len(src)]
            if re.match(r"\s*def\s+%s\s*\(" % fn, line):
                continue          # ★定义行不算调用★
            return True
    if re.search(r"(?:open|read_text)\s*\([^)]*\.kicad_mod", src):
        return True
    return False


def default_gate_runner(root: str, gate_rel: str):
    script = os.path.join(root, gate_rel)
    if not os.path.isfile(script):
        return None, "", "★闸脚本不存在: %s★" % gate_rel
    try:
        pr = subprocess.run([sys.executable, script, "--root", root],
                            capture_output=True, text=True, cwd=root, timeout=120)
    except Exception as exc:  # fail-closed
        return None, "", "★闸跑不起来: %r★" % exc
    return pr.returncode, pr.stdout, pr.stderr


# ══════════════════════════════ 判据 ══════════════════════════════
def _mk(code, name, errs):
    return {"code": code, "name": name, "ok": not errs, "errs": errs}


def p1(ctx):
    """★P1 (A1) · pad 档位必须从 `.kicad_mod` 现读 ⇒ 与机器块逐字一致★"""
    errs = []
    blk = ctx["block"]
    if blk is None:
        return _mk("P1", "pad 档位从 .kicad_mod 现读 + 与机器块逐字一致", ["★机器块没解析出来★"])
    cp = blk.get("current_pad") or {}
    tiers = blk.get("pad_tiers") or []
    geoms = ctx["geoms"]
    if not geoms:
        errs.append("★`.kicad_mod` 没读到 (fail-closed)★")
        return _mk("P1", "pad 档位从 .kicad_mod 现读 + 与机器块逐字一致", errs)

    # ① 现读 pad 逐字 = 机器块 current_pad
    for ref, g in geoms.items():
        if abs(g["pad_along"] - float(cp.get("pad_x_mm", -1))) > TOL:
            errs.append("★%s 现读 pad 宽 %s ≠ 机器块 current_pad.pad_x_mm %s★"
                        % (ref, g["pad_along"], cp.get("pad_x_mm")))
        if abs(g["pad_across"] - float(cp.get("pad_y_mm", -1))) > TOL:
            errs.append("★%s 现读 pad 高 %s ≠ 机器块 current_pad.pad_y_mm %s★"
                        % (ref, g["pad_across"], cp.get("pad_y_mm")))
    # ② 现读 pad 必须【恰好命中】一档
    cur = geoms.get("J_DEBUG") or {}
    pad_now = cur.get("pad_along")
    hits = [t for t in tiers if abs(float(t["pad_mm"]) - pad_now) <= TOL]
    if len(hits) != 1:
        errs.append("★现读 pad %s 在机器块 pad_tiers 里命中 %d 档 (必须恰好 1 档·★不许凭空★)★"
                    % (pad_now, len(hits)))
    else:
        if hits[0].get("id") != cp.get("current_tier_id"):
            errs.append("★命中的档位 id %s ≠ current_pad.current_tier_id %s★"
                        % (hits[0].get("id"), cp.get("current_tier_id")))
    # ③ 档位数 + 每档环宽必须【闸自算】与登记一致
    if len(tiers) < 3:
        errs.append("★机器块 pad_tiers 只有 %d 档 (★至少 3 档·★降级方案要求全列★)★" % len(tiers))
    drill = ctx["planned_drill"]
    for t in tiers:
        if t.get("annular_ring_mm") is None:
            errs.append("★档位 %s 缺 annular_ring_mm★" % t.get("id"))
            continue
        ann = r4((float(t["pad_mm"]) - drill) / 2.0)
        if abs(ann - float(t["annular_ring_mm"])) > TOL:
            errs.append("★档位 %s 环宽登记 %s ≠ 闸自算 %s (pad %s − 规划孔 %s)/2★"
                        % (t.get("id"), t["annular_ring_mm"], ann, t["pad_mm"], drill))
    # ④ 规划钻孔必须被显式登记 (偏离必须留痕)
    if not (blk.get("planned_drill_source") or "").strip():
        errs.append("★机器块没登记 planned_drill_source (★库件默认孔与规划孔的偏离必须留痕★)")
    # ⑤ 【推导必须吃 pad】(★自证不是写死★)
    d1 = compute_seven(1.000, ctx["spans"], ctx["ho"], ctx["crit"], ctx["tol_fdm"])
    d2 = compute_seven(1.110, ctx["spans"], ctx["ho"], ctx["crit"], ctx["tol_fdm"])
    if d1["j_debug_copper_x"] == d2["j_debug_copper_x"]:
        errs.append("★推导结果对 pad 不敏感 ⇒ 7 个数是写死的★")
    # ⑥ 【源码不许有 pad 常量】
    src = read_text(os.path.abspath(__file__))
    if re.search(r"(?mi)^\s*[A-Z_]*PAD[A-Z_]*\s*=\s*[0-9]", src):
        errs.append("★本闸源码里出现 pad 数值常量 (★pad 必须现读·不许写死★)")
    return _mk("P1", "pad 档位从 .kicad_mod 现读 + 与机器块逐字一致", errs)


def p2(ctx):
    """★P2 (A2) · 7 个数必须由 pad 档位推导 ⇒ 与机器块矩阵逐格一致★"""
    errs = []
    blk = ctx["block"]
    if blk is None:
        return _mk("P2", "7 个数由 pad 档位推导 + 与矩阵逐格一致", ["★机器块没解析出来★"])
    tiers = blk.get("pad_tiers") or []
    matrix = blk.get("seven_numbers_matrix") or {}
    if not tiers:
        errs.append("★机器块没有 pad_tiers★")
    if not matrix:
        errs.append("★机器块没有 seven_numbers_matrix★")
    for t in tiers:
        tid = t.get("id")
        row = matrix.get(tid)
        if row is None:
            errs.append("★档位 %s 在 seven_numbers_matrix 里没有对应行★" % tid)
            continue
        got = compute_seven(float(t["pad_mm"]), ctx["spans"], ctx["ho"], ctx["crit"], ctx["tol_fdm"])
        for k in SEVEN:
            if k not in row:
                errs.append("★矩阵 %s 缺 %s★" % (tid, k))
                continue
            if abs(float(row[k]) - got[k]) > TOL:
                errs.append("★矩阵 %s.%s 写 %s ≠ 由 pad %s 推导的 %s★"
                            % (tid, k, row[k], t["pad_mm"], got[k]))
        extra = set(row) - set(SEVEN)
        if extra:
            errs.append("★矩阵 %s 有多余键 %s★" % (tid, sorted(extra)))
    return _mk("P2", "7 个数由 pad 档位推导 + 与矩阵逐格一致", errs)


def p3(ctx):
    """★P3 (A3) · 判决链消费的数必须与 `.kicad_mod` 实算逐格一致★"""
    errs = []
    blk = ctx["block"]
    if blk is None:
        return _mk("P3", "判决链消费的数与 .kicad_mod 实算逐格一致", ["★机器块没解析出来★"])
    vc = blk.get("verdict_chain_current") or {}
    if not vc:
        errs.append("★机器块缺 verdict_chain_current (★判决链消费的数必须被登记·★逐格可核★)")
        return _mk("P3", "判决链消费的数与 .kicad_mod 实算逐格一致", errs)
    # ★从 `.kicad_mod` 实算 (不用机器块里的 pad_tiers)★
    gd = ctx["geoms"].get("J_DEBUG")
    gu = ctx["geoms"].get("J_UART")
    if not gd or not gu:
        errs.append("★`.kicad_mod` 没读到 (fail-closed)★")
        return _mk("P3", "判决链消费的数与 .kicad_mod 实算逐格一致", errs)
    spans = {"J_DEBUG": gd["span"], "J_UART": gu["span"]}
    got = compute_seven(gd["pad_along"], spans, ctx["ho"], ctx["crit"], ctx["tol_fdm"])
    for k in CHAIN_KEYS:
        if k not in vc:
            errs.append("★verdict_chain_current 缺 %s★" % k)
            continue
        if abs(float(vc[k]) - got[k]) > TOL:
            errs.append("★verdict_chain_current.%s 写 %s ≠ `.kicad_mod` 实算 %s★" % (k, vc[k], got[k]))
    # ★实读铜箔宽必须与实算同源 (跨距 + pad)★
    if abs(gd["span"] + gd["pad_along"] - got["copper_x_j_debug"]) > TOL:
        errs.append("★J_DEBUG 实读铜箔宽与「跨距+pad」不符★")
    if abs(gu["span"] + gu["pad_along"] - got["copper_x_j_uart"]) > TOL:
        errs.append("★J_UART 实读铜箔宽与「跨距+pad」不符★")
    return _mk("P3", "判决链消费的数与 .kicad_mod 实算逐格一致", errs)


def p4(ctx):
    """★P4 (A4) · 盲闸名单不许凭空★"""
    errs = []
    blk = ctx["block"]
    if blk is None:
        return _mk("P4", "盲闸名单不许凭空 (在盘 + 实跑 + 静态盲证 + 不重不漏)", ["★机器块没解析出来★"])
    blind = blk.get("blind_gates") or []
    sens = blk.get("sensitive_gates") or []
    allg = blk.get("all_mech_gates") or []
    runner = ctx["gate_runner"]
    for b in blind:
        rel = b.get("gate") or ""
        path = os.path.join(ctx["root"], rel)
        if not os.path.isfile(path):
            errs.append("★盲闸 %s 在盘上找不到 (★名单不许凭空★)★" % rel)
            continue
        src = read_text(path)
        if has_lib_read_path(src):
            errs.append("★盲闸 %s 的源码里【有】通向 KiCad 库的读入口 "
                        "(★LIBROOT 常量 / 解析函数调用 / 直读 .kicad_mod★) "
                        "⇒ 它【不是结构上的盲闸】⇒ 名单登记错了★" % rel)
        rc, out, err = runner(ctx["root"], rel)
        if rc is None:
            errs.append("★盲闸 %s 实跑失败: %s★" % (rel, err))
            continue
        if rc != b.get("baseline_rc"):
            errs.append("★盲闸 %s 实跑 rc=%s ≠ 登记 baseline_rc %s★" % (rel, rc, b.get("baseline_rc")))
        got = extract_red_items(out)
        want = sorted(b.get("baseline_red_items") or [])
        if got != want:
            errs.append("★盲闸 %s 实跑红项集合 %s ≠ 登记 %s★" % (rel, got, want))
        want_md5 = b.get("baseline_stdout_md5")
        if want_md5:
            got_md5 = hashlib.md5(out.encode()).hexdigest()
            if got_md5 != want_md5:
                errs.append("★盲闸 %s 实跑 stdout md5 %s ≠ 登记 %s (★A/B 两臂逐字相同的那一版★)★"
                            % (rel, got_md5, want_md5))
    for s in sens:
        rel = s.get("gate") or ""
        path = os.path.join(ctx["root"], rel)
        if not os.path.isfile(path):
            errs.append("★敏感闸 %s 在盘上找不到★" % rel)
            continue
        src = read_text(path)
        if not has_lib_read_path(src):
            errs.append("★敏感闸 %s 的源码里【没有】通向 KiCad 库的读入口 ⇒ 它抓不到焊盘变化★" % rel)
        rc, out, err = runner(ctx["root"], rel)
        if rc is None:
            errs.append("★敏感闸 %s 实跑失败: %s★" % (rel, err))
            continue
        if rc != s.get("baseline_rc"):
            errs.append("★敏感闸 %s 实跑 rc=%s ≠ 登记 baseline_rc %s★" % (rel, rc, s.get("baseline_rc")))
        got = extract_red_items(out)
        want = sorted(s.get("baseline_red_items") or [])
        if got != want:
            errs.append("★敏感闸 %s 实跑红项集合 %s ≠ 登记 %s★" % (rel, got, want))
    # 不重不漏
    listed = [b.get("gate") for b in blind] + [s.get("gate") for s in sens]
    if len(set(listed)) != len(listed):
        errs.append("★盲闸/敏感闸名单里有重复★")
    missing = [g for g in allg if g not in listed]
    if missing:
        errs.append("★all_mech_gates 里的 %d 道没进名单: %s★" % (len(missing), missing))
    extra = [g for g in listed if g not in allg]
    if extra:
        errs.append("★名单里有 all_mech_gates 之外的闸: %s★" % extra)
    return _mk("P4", "盲闸名单不许凭空 (在盘 + 实跑 + 静态盲证 + 不重不漏)", errs)


def p5(ctx):
    """★P5 (A5) · 零挂链自证★"""
    errs = []
    txt = ctx["chain_text"]
    if txt is None:
        return _mk("P5", "零挂链自证 (gate_check.py 里零命中)", ["★state/gate_check.py 没读到★"])
    n = len(re.findall(r"check_pad_size_coupling_closed", txt))
    if n != 0:
        errs.append("★`state/gate_check.py` 里 `check_pad_size_coupling_closed` 命中 %d 次 "
                    "(★本闸必须零挂链★)★" % n)
    return _mk("P5", "零挂链自证 (gate_check.py 里零命中)", errs)


def p6(ctx):
    """★P6 (A6) · 证据分级五级白名单 + 零挂起措辞 + 两句分开 + 不代拍★"""
    errs = []
    docs = [("真相页", ctx["page_text"])]
    ho = ctx.get("handoff_text")
    if ho:
        docs.append(("交卷页", ho))
    for name, text in docs:
        for ln in text.split("\n"):
            if any(mk in ln for mk in META_MARKERS):
                # ★元引述行: 只豁免【禁用名单 / 反向用例注入】的描述★
                continue
            for tk in evidence_tokens(ln):
                if tk in FORBIDDEN_EVIDENCE:
                    errs.append("★%s 证据等级 %s 在禁用名单 ⇒ 只许用五级白名单 %s★"
                                % (name, tk, "/".join(EVIDENCE_WHITELIST)))
                elif tk not in EVIDENCE_WHITELIST:
                    errs.append("★%s 证据等级 %s 不在五级白名单 %s★"
                                % (name, tk, "/".join(EVIDENCE_WHITELIST)))
        if not any(tk in EVIDENCE_WHITELIST for tk in evidence_tokens(text)):
            errs.append("★%s 一个证据等级标记都没有★" % name)
        for w in HEDGING_WORDS:
            for ln in text.split("\n"):
                if any(mk in ln for mk in META_MARKERS):
                    continue
                if w in ln:
                    errs.append("★%s 出现挂起措辞 %r (不许无档措辞)★" % (name, w))
                    break
        for w in FORBIDDEN_PHRASES:
            for ln in text.split("\n"):
                if any(mk in ln for mk in META_MARKERS):
                    continue
                if w in ln:
                    errs.append("★%s 出现 %r (★不许把活推给原厂/外部★)★" % (name, w))
                    break
    text = ctx["page_text"]
    if "判据句" not in text:
        errs.append("★真相页必须显式写出「判据句」★")
    if "事实句" not in text:
        errs.append("★真相页必须显式写出「事实句」★")
    blk = ctx["block"] or {}
    if blk.get("decision_taken_here") != "not_decided_here":
        errs.append("★机器块 decision_taken_here=%r (★本单不代拍·★必须 not_decided_here★)"
                    % blk.get("decision_taken_here"))
    return _mk("P6", "证据分级五级白名单 + 零挂起措辞 + 两句分开 + 不代拍", errs)


def p7(ctx):
    """★P7 (A7) · 板面零写板自证 (md5 / mtime / size 三项)★"""
    errs = []
    blk = ctx["block"] or {}
    base = blk.get("board_baseline") or {}
    rel = base.get("path") or BOARD_REL
    path = os.path.join(ctx["root"], rel)
    if not os.path.isfile(path):
        return _mk("P7", "板面零写板自证 (md5 / mtime / size 三项)",
                   ["★板文件不在盘: %s★" % rel])
    st = os.stat(path)
    got_md5 = md5_of(path)
    if got_md5 != base.get("md5"):
        errs.append("★板 md5 %s ≠ 基线 %s (★零写板被破坏★)★" % (got_md5, base.get("md5")))
    if st.st_size != base.get("size"):
        errs.append("★板 size %d ≠ 基线 %s★" % (st.st_size, base.get("size")))
    if base.get("mtime"):
        want = parse_mtime(base["mtime"])
        if abs(st.st_mtime - want) > 1e-6:
            errs.append("★板 mtime %s ≠ 基线 %s★"
                        % (datetime.datetime.fromtimestamp(st.st_mtime).isoformat(), base["mtime"]))
    return _mk("P7", "板面零写板自证 (md5 / mtime / size 三项)", errs)


def p8(ctx):
    """★P8 (A8) · 零外发自证 (outbox 一个字节没动)★"""
    errs = []
    blk = ctx["block"] or {}
    got, n = ctx["outbox"]
    want = blk.get("outbox_tree_md5")
    if want is None:
        errs.append("★机器块缺 outbox_tree_md5 基线★")
        return _mk("P8", "零外发自证 (outbox 树摘要逐字一致)", errs)
    if got != want:
        errs.append("★`state/outbox/` 树摘要 %s ≠ 登记基线 %s (★本单零外发·★一个字节都不许动★)★"
                    % (got, want))
    wantn = blk.get("outbox_tree_files")
    if wantn is not None and n != wantn:
        errs.append("★`state/outbox/` 文件数 %d ≠ 登记基线 %s★" % (n, wantn))
    return _mk("P8", "零外发自证 (outbox 树摘要逐字一致)", errs)


# ══════════════════════════════ 上下文 + 评估 ══════════════════════════════
def build_ctx(root: str, libroot: str, **ov):
    ctx = {"root": root, "libroot": libroot}
    page_path = os.path.join(root, PAGE_REL)
    ctx["page_text"] = ov.get("page_text") or (read_text(page_path) if os.path.isfile(page_path) else "")
    ctx["block"] = ov.get("block") if "block" in ov else extract_json_fence(ctx["page_text"])
    # 现读 `.kicad_mod`
    geoms = {}
    for ref, mod in MODS.items():
        p = os.path.join(libroot, LIBDIR, mod)
        if os.path.isfile(p):
            try:
                geoms[ref] = tht_geom(p)
            except Exception:
                pass
    ctx["geoms"] = geoms
    ctx["spans"] = {r: geoms[r]["span"] for r in geoms if "span" in geoms.get(r, {})}
    crit, tol, err = read_crit(root)
    ctx["crit"] = crit if crit is not None else 0.0
    ctx["tol_fdm"] = (tol or {}).get("fdm_part", 0.0)
    ho, oerr = read_opening(root)
    ctx["ho"] = ho or {}
    ctx["planned_drill"] = float(((ctx["block"] or {}).get("planned_drill_mm")) or 0.71)
    chain_path = os.path.join(root, CHAIN_REL)
    ctx["chain_text"] = ov.get("chain_text") if "chain_text" in ov else (
        read_text(chain_path) if os.path.isfile(chain_path) else "")
    ho_path = os.path.join(root, HANDOFF_REL)
    ctx["handoff_text"] = ov.get("handoff_text") if "handoff_text" in ov else (
        read_text(ho_path) if os.path.isfile(ho_path) else "")
    ctx["outbox"] = ov.get("outbox") if "outbox" in ov else outbox_digest(root)
    ctx["gate_runner"] = ov.get("gate_runner") or default_gate_runner
    ctx["board_override"] = ov.get("board")
    return ctx


def evaluate(ctx):
    res = []
    for fn in (p1, p2, p3, p4, p5, p6, p7, p8):
        try:
            res.append(fn(ctx))
        except Exception as exc:  # fail-closed
            res.append(_mk(fn.__name__.upper(), "判据执行异常 (fail-closed)", ["★%r★" % exc]))
    return res


# ══════════════════════════════ 报告 ══════════════════════════════
def report(res, ctx):
    out = []
    out.append("=" * 92)
    out.append("ISS-403 · 「板那一趟」焊盘尺寸 ⇄ MECH 判决链 7 个数 · 耦合闭包闸")
    out.append("真相页: %s" % PAGE_REL)
    out.append("库根: %s" % ctx["libroot"])
    out.append("=" * 92)
    for r in res:
        out.append("\n[%s] %s ⇒ %s" % (r["code"], r["name"], "✅ PASS" if r["ok"] else "❌ FAIL"))
        for e in r["errs"]:
            out.append("    · %s" % e)
    n_ok = sum(1 for r in res if r["ok"])
    out.append("\n" + "-" * 92)
    out.append("★判据方向 (判据句): 焊盘尺寸一旦被放大, 7 个数必须被自动重新推导, "
               "且 5 道盲闸必须不再「看不见」★")
    out.append("★铜箔事实 (事实句): 本机 A/B 实测 (pad 1.000 vs 1.110) ⇒ 7 道 MECH 闸里 5 道红项集合逐条相同 ★")
    out.append("★两句同时成立, 不许混成一句「OK / 合格」★")
    out.append("-" * 92)
    out.append("合计: %d/%d 条判据通过" % (n_ok, len(res)))
    return "\n".join(out), n_ok, len(res)


# ══════════════════════════════ 反向用例 ══════════════════════════════
def _clone(blk):
    return json.loads(json.dumps(blk, ensure_ascii=False))


def selftest(root: str, libroot: str):
    sbx = os.path.join(root, "tmp", "iss403_gate", "selftest")
    if os.path.isdir(sbx):
        shutil.rmtree(sbx)
    os.makedirs(sbx)
    fails = []
    REV_TAGS = []

    def chk(tag, cond, msg=""):
        if tag.startswith("R"):
            REV_TAGS.append(tag)
        if cond:
            print("[ok]   %-14s ✓" % tag)
        else:
            print("[FAIL] %-14s %s" % (tag, msg))
            fails.append(tag)

    def red_codes(res):
        return sorted(r["code"] for r in res if not r["ok"])

    base_ctx = build_ctx(root, libroot)
    base_res = evaluate(base_ctx)
    base_red = red_codes(base_res)
    chk("T0-正向", base_red == [],
        "★真件上本闸不自洽: 红 %s ⇒ %s★" % (base_red, [e for r in base_res for e in r["errs"]]))

    blk0 = base_ctx["block"]
    if blk0 is None:
        print("[FAIL] T0-机器块    ★真相页机器块没解析出来★")
        fails.append("T0-机器块")
        print("ALL TESTS PASS" if not fails else "SELFTEST FAILED")
        return 0 if not fails else 1

    # ── 反向 1 (P1): 把机器块 current_pad.pad_x_mm 改掉 ⇒ 只有 P1 红 ──
    b = _clone(blk0)
    b["current_pad"]["pad_x_mm"] = 1.11
    r = evaluate(build_ctx(root, libroot, block=b))
    chk("R1-P1-档位", red_codes(r) == ["P1"], "★改了 current_pad.pad_x_mm ⇒ 红的是 %s (应只 P1)★" % red_codes(r))

    # ── 反向 2 (P2): 把矩阵某一格改掉 ⇒ 只有 P2 红 ──
    b = _clone(blk0)
    b["seven_numbers_matrix"]["P1110"]["j_debug_copper_x"] = 5.92
    r = evaluate(build_ctx(root, libroot, block=b))
    chk("R2-P2-矩阵", red_codes(r) == ["P2"], "★改了矩阵一格 ⇒ 红的是 %s (应只 P2)★" % red_codes(r))

    # ── 反向 3 (P2): 把某档 pad_mm 改掉 ⇒ 必然双红 (P1 的环宽自检 + P2 的矩阵推导) ★
    #    ★这条是【故意设计的双红】: 改档位值会同时打破「环宽自检」(P1) 与「矩阵推导」(P2) ⇒
    #      期望集合【逐字写死】= ["P1","P2"] ⇒ 闸红多了或红少了都算本用例失败★
    b = _clone(blk0)
    for t in b["pad_tiers"]:
        if t["id"] == "P1110":
            t["pad_mm"] = 1.12
    r = evaluate(build_ctx(root, libroot, block=b))
    chk("R3-P2-档位值", red_codes(r) == ["P1", "P2"],
        "★改了档位 pad_mm ⇒ 红的是 %s (★逐字期望 [P1,P2]·★设计内的双红★)★" % red_codes(r))

    # ── 反向 4 (P3): 把 verdict_chain_current 改掉 ⇒ 只有 P3 红 ──
    b = _clone(blk0)
    b["verdict_chain_current"]["copper_x_j_debug"] = 5.92
    r = evaluate(build_ctx(root, libroot, block=b))
    chk("R4-P3-链值", red_codes(r) == ["P3"], "★改了 verdict_chain_current ⇒ 红的是 %s (应只 P3)★" % red_codes(r))

    # ── 反向 5 (P4): 往盲闸名单塞一个不存在的闸 ⇒ 只有 P4 红 ──
    b = _clone(blk0)
    b["blind_gates"].append({"gate": "MECH/check_no_such_gate_iss403.py",
                              "blind_lines": [], "mechanism": "反例",
                              "baseline_rc": 0, "baseline_red_items": []})
    r = evaluate(build_ctx(root, libroot, block=b))
    chk("R5-P4-凭空", red_codes(r) == ["P4"], "★盲闸名单塞了个不存在的闸 ⇒ 红的是 %s (应只 P4)★" % red_codes(r))

    # ── 反向 6 (P4): 把 all_mech_gates 删一道 ⇒ 只有 P4 红 (不重不漏判据) ──
    b = _clone(blk0)
    b["all_mech_gates"] = [g for g in b["all_mech_gates"] if "juart" not in g]
    r = evaluate(build_ctx(root, libroot, block=b))
    chk("R6-P4-不漏", red_codes(r) == ["P4"], "★all_mech_gates 删一道 ⇒ 红的是 %s (应只 P4)★" % red_codes(r))

    # ── 反向 7 (P5): 把本闸名字塞进 gate_check 文本 ⇒ 只有 P5 红 ──
    chain = base_ctx["chain_text"] + '\n    (os.path.join(PROJ, "MECH", "check_pad_size_coupling_closed.py"), "x", ()),\n'
    r = evaluate(build_ctx(root, libroot, chain_text=chain))
    chk("R7-P5-挂链", red_codes(r) == ["P5"], "★往 gate_check 塞了本闸 ⇒ 红的是 %s (应只 P5)★" % red_codes(r))

    # ── 反向 8 (P6): 往正文塞一个禁用证据等级 ⇒ 只有 P6 红 ──
    page = base_ctx["page_text"] + "\n★本段塞了一个禁用证据等级 [推断] ★\n"
    r = evaluate(build_ctx(root, libroot, page_text=page))
    chk("R8-P6-证据级", red_codes(r) == ["P6"], "★正文塞了 [推断] ⇒ 红的是 %s (应只 P6)★" % red_codes(r))

    # ── 反向 9 (P6): 往正文塞挂起措辞 ⇒ 只有 P6 红 ──
    page = base_ctx["page_text"] + "\n★本段塞了一个挂起措辞 等原厂回信 ★\n"
    r = evaluate(build_ctx(root, libroot, page_text=page))
    chk("R9-P6-挂起", red_codes(r) == ["P6"], "★正文塞了「等原厂回信」⇒ 红的是 %s (应只 P6)★" % red_codes(r))

    # ── 反向 10 (P6): 机器块标成已拍板 ⇒ 只有 P6 红 ──
    b = _clone(blk0)
    b["decision_taken_here"] = "P1110"
    r = evaluate(build_ctx(root, libroot, block=b))
    chk("R10-P6-代拍", red_codes(r) == ["P6"], "★decision_taken_here 改成 P1110 ⇒ 红的是 %s (应只 P6)★" % red_codes(r))

    # ── 反向 11 (P7): 篡改板 md5 基线 ⇒ 只有 P7 红 ──
    b = _clone(blk0)
    b["board_baseline"]["md5"] = "0" * 32
    r = evaluate(build_ctx(root, libroot, block=b))
    chk("R11-P7-零写板", red_codes(r) == ["P7"], "★篡改板 md5 基线 ⇒ 红的是 %s (应只 P7)★" % red_codes(r))

    # ── 反向 12 (P8): 篡改 outbox 树摘要基线 ⇒ 只有 P8 红 ──
    b = _clone(blk0)
    b["outbox_tree_md5"] = "0" * 32
    r = evaluate(build_ctx(root, libroot, block=b))
    chk("R12-P8-零外发", red_codes(r) == ["P8"], "★篡改 outbox 基线 ⇒ 红的是 %s (应只 P8)★" % red_codes(r))

    # ── 反向 13 (P4): 把一道【能看见库】的闸错登记成盲闸 ⇒ 只有 P4 红 ──
    b = _clone(blk0)
    b["blind_gates"] = [g for g in b["blind_gates"] if "jdebug" not in g["gate"]]
    b["blind_gates"].append({"gate": "MECH/check_jdebug_1p27_clearance.py",
                              "blind_lines": [], "mechanism": "反例·它其实能看见库",
                              "baseline_rc": 0, "baseline_red_items": []})
    r = evaluate(build_ctx(root, libroot, block=b))
    chk("R13-P4-误登盲", red_codes(r) == ["P4"], "★把能看见库的闸登记成盲闸 ⇒ 红的是 %s (应只 P4)★" % red_codes(r))

    # ── 反向 14 (P2): 把 7 个数矩阵整行删掉 ⇒ 只有 P2 红 ──
    b = _clone(blk0)
    del b["seven_numbers_matrix"]["P1218"]
    r = evaluate(build_ctx(root, libroot, block=b))
    chk("R14-P2-缺行", red_codes(r) == ["P2"], "★删掉矩阵一行 ⇒ 红的是 %s (应只 P2)★" % red_codes(r))

    n_rev = sum(1 for t in REV_TAGS if t)
    print("")
    print("反向用例: %d 条 (★要求 ≥8★) · 正向: 1 条" % n_rev)
    print("沙盒: %s" % sbx)
    if fails:
        print("SELFTEST FAILED: %s" % fails)
        return 1
    print("ALL TESTS PASS")
    return 0


# ══════════════════════════════ main ══════════════════════════════
def main(argv):
    ap = argparse.ArgumentParser(description="ISS-403 焊盘尺寸 ⇄ MECH 判决链 7 个数 · 耦合闭包闸")
    ap.add_argument("--selftest", action="store_true", help="跑反向用例 (末行 ALL TESTS PASS)")
    ap.add_argument("--root", default=PROJ, help="项目根")
    ap.add_argument("--libroot", default=LIBROOT_DEFAULT, help="KiCad 官方库根")
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)
    libroot = os.path.abspath(args.libroot)
    if not os.path.isdir(root):
        print("root 不存在: %s" % root)
        return 2
    if args.selftest:
        return selftest(root, libroot)
    ctx = build_ctx(root, libroot)
    res = evaluate(ctx)
    txt, n_ok, n = report(res, ctx)
    print(txt)
    return 0 if n_ok == n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
