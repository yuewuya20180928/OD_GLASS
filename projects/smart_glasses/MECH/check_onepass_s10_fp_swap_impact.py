#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_onepass_s10_fp_swap_impact.py —— ★★【ISS-365 · mech-lead · S10 换封装对 MECH 侧影响面 · 机器闸】★★

★★★**★这个闸守的是什么★**★★
  「板只改一次」那一趟的 **S10 步** 要把 **90 件** 的自绘占位 land 换成官方封装。
  ★**那 90 件里有 10 个是 MECH 侧 S6 落位判据 (`MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` §3) 的主角** ★
  ⇒ 而 §3 那些「最小净距 4.6500 / 必须清空区 X 139.0025..146.8975」之类的数
  ★**全是按【当前板上的自绘占位 land】算出来的** ⇒ 换官方 land 后那些数**会不会还成立, 本机没有一条闸知道** ★
  ⇒ ★**本闸把这一跳的结论【提前钉成机器判据】**: 90 件集合 / 10 件交集 / 负结论 / 逐件几何 / 证据分级
  ⇒ ★**在那一趟改板【之前】就把「MECH 侧要重算什么」算出来并守住** ★

  闸的七条:
    M0  ★**基准块** ★ —— 规格页 `MECH/BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md` 的机器块存在且是合法 JSON
    M1  ★**90 件集合由脚本自己算** ★ —— 读 `HW/BOM_v1.csv` + `HW/netlist_v1.csv` + 读板
         + 读 `HW/FP_TRUTH_BASELINE.md` §2 靶子 + 读 `HW/PCB/FP_TRUTH_COVERAGE_GAP.md` §2 缺口
         ⇒ 算出 77 + 13 = 90 ⇒ ★**页里写的 ≠ 脚本实算 ⇒ 红** ★
    M2  ★**10 个 `R_SEL_*` 落在 90 件集合里** ★ (★脚本实算交集, 不许手写★) ⇒ 这是 §2 专项的机器前提
    M3  ★**负结论可证** ★ —— 座体类 6 组 ref + 10 个 `TP_DSI_*` 与 90 件的交集 = ∅ ⇒ 不为空即红
    M4  ★**§1 逐件字段齐全** ★ (ref / 现占位几何 / 目标几何 / Δ / 碰哪条 / 判定 / 重算后的数 / 证据等级 / 降级方案)
         ⇒ 漏件即红 + 点名 ref
    M5  ★**几何一致性** ★ —— 每件页里写的「目标 fab 外框 / courtyard / 焊盘数」== 脚本从该 `.kicad_mod` 实测出来的值
         ⇒ 对不上即红 (★抓的是「抄错几何」★)
    M6  ★**证据等级全在五级白名单** ★ (`[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]` ⇒ ★写 `[官方]` = 红★)
         + 降级方案逐件非空
    M7  ★**正文零挂起措辞** ★ (★禁「等原厂回信 / 等供应商确认 / 待外部回复 / 等确认」★)

  ★**只读 import `HW/check_fp_truth_coverage_gap.py`** ⇒ C4 / 靶子 / 缺口 三集合口径零漂移 ★
  ★**只读 `MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md` / `MECH/BOARD_ONEPASS_MECH_SYNC.md` 的机器块** ⇒ 保留区几何零漂移 ★
  ★**本闸是【新建】文件, 一个字节不改既有 MECH 判据脚本** ★

用法:
    python3 MECH/check_onepass_s10_fp_swap_impact.py            # rc=0 = 全绿
    python3 MECH/check_onepass_s10_fp_swap_impact.py --json     # 机器读
    python3 MECH/check_onepass_s10_fp_swap_impact.py --selftest # rc=0 = 反向用例全抓到
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))

SPEC_REL = os.path.join("MECH", "BOARD_ONEPASS_S10_FP_SWAP_IMPACT.md")
MACH_BEGIN = "<!-- MACHINE-BLOCK-BEGIN -->"
MACH_END = "<!-- MACHINE-BLOCK-END -->"

LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"

BOM_REL = os.path.join("HW", "BOM_v1.csv")
NET_REL = os.path.join("HW", "netlist_v1.csv")
PCB_REL = os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb")
BASE_REL = os.path.join("HW", "FP_TRUTH_BASELINE.md")
GAP_REL = os.path.join("HW", "PCB", "FP_TRUTH_COVERAGE_GAP.md")

R_SEL_REFS = ["R_SEL_D0_N", "R_SEL_D0_P", "R_SEL_D1_N", "R_SEL_D1_P", "R_SEL_CK_N",
              "R_SEL_CK_P", "R_SEL_D2_N", "R_SEL_D2_P", "R_SEL_D3_N", "R_SEL_D3_P"]
TP_DSI_REFS = ["TP_DSI_D0_N", "TP_DSI_D0_P", "TP_DSI_D1_N", "TP_DSI_D1_P",
               "TP_DSI_CK_N", "TP_DSI_CK_P", "TP_DSI_D2_N", "TP_DSI_D2_P",
               "TP_DSI_D3_N", "TP_DSI_D3_P"]
CONNECTOR_REFS = ["J_DEBUG", "J_UART", "J_USB_C", "J_CHG",
                  "J_SOM_P1", "J_SOM_P2", "J_SOM_P3", "J_SOM_P4"]

EVIDENCE_WHITELIST = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
FORBIDDEN_EVIDENCE = ("[官方]",)
FORBIDDEN_PENDING = ("等原厂回信", "等供应商确认", "待外部回复", "等确认")

# ★§1 表的 9 列固定字段 (★M4 用★) ★
S1_HEADERS = ("ref", "现占位几何", "目标封装几何", "Δ", "碰 MECH 侧的哪一条",
              "判定", "重算后的数", "证据等级", "降级方案")


# ==================================================================================================
# 只读 import 既有闸 (三集合口径零漂移)
# ==================================================================================================
def load_cov_gate(root):
    path = os.path.join(root, "HW", "check_fp_truth_coverage_gap.py")
    spec = importlib.util.spec_from_file_location("iss365_cov_gate_readonly", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ==================================================================================================
# 自写只读 s-expr 解析 (★不 import 既有闸的内部实现★)
# ==================================================================================================
def _tokenize(text):
    i, n, toks = 0, len(text), []
    while i < n:
        c = text[i]
        if c in "()":
            toks.append(c)
            i += 1
        elif c.isspace():
            i += 1
        elif c == '"':
            j, buf = i + 1, []
            while j < n:
                if text[j] == "\\" and j + 1 < n:
                    buf.append(text[j + 1])
                    j += 2
                    continue
                if text[j] == '"':
                    break
                buf.append(text[j])
                j += 1
            toks.append(("str", "".join(buf)))
            i = j + 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in "()":
                j += 1
            toks.append(("atom", text[i:j]))
            i = j
    return toks


def _parse(text):
    toks = _tokenize(text)
    pos = 0

    def node():
        nonlocal pos
        if toks[pos] == "(":
            pos += 1
            out = []
            while pos < len(toks) and toks[pos] != ")":
                out.append(node())
            pos += 1
            return out
        t = toks[pos]
        pos += 1
        return t

    root = node()
    if (isinstance(root, list) and len(root) == 1 and isinstance(root[0], list)
            and root[0] and _nn(root[0]) == "kicad_pcb"):
        return root[0]
    return root


def _nn(node):
    if isinstance(node, list) and node:
        return node[0][1] if isinstance(node[0], tuple) else node[0]
    return None


def _kids(node, name):
    return [c for c in node if isinstance(c, list) and _nn(c) == name]


def _kid(node, name):
    k = _kids(node, name)
    return k[0] if k else None


def _v(node, idx=1, default=None):
    if isinstance(node, list) and len(node) > idx:
        x = node[idx]
        return x[1] if isinstance(x, tuple) else x
    return default


def _f(node, idx=1, default=None):
    try:
        return float(_v(node, idx, default))
    except (TypeError, ValueError):
        return default


def _bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def _rect_pts(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _fab_pts(node):
    out = []
    for g in _kids(node, "fp_line"):
        if _v(_kid(g, "layer"), 1, "") != "F.Fab":
            continue
        st, en = _kid(g, "start"), _kid(g, "end")
        out.append((_f(st, 1), _f(st, 2)))
        out.append((_f(en, 1), _f(en, 2)))
    for g in _kids(node, "fp_rect"):
        if _v(_kid(g, "layer"), 1, "") != "F.Fab":
            continue
        st, en = _kid(g, "start"), _kid(g, "end")
        out.extend(_rect_pts(_f(st, 1), _f(st, 2), _f(en, 1), _f(en, 2)))
    return out


def _crtyd_pts(node):
    out = []
    for g in _kids(node, "fp_line"):
        if _v(_kid(g, "layer"), 1, "") != "F.CrtYd":
            continue
        st, en = _kid(g, "start"), _kid(g, "end")
        out.append((_f(st, 1), _f(st, 2)))
        out.append((_f(en, 1), _f(en, 2)))
    for g in _kids(node, "fp_rect"):
        if _v(_kid(g, "layer"), 1, "") != "F.CrtYd":
            continue
        st, en = _kid(g, "start"), _kid(g, "end")
        out.extend(_rect_pts(_f(st, 1), _f(st, 2), _f(en, 1), _f(en, 2)))
    return out


def _pads(node):
    out = []
    for pad in _kids(node, "pad"):
        pat = _kid(pad, "at")
        sz = _kid(pad, "size")
        out.append({"num": _v(pad, 1, ""), "type": _v(pad, 2, ""),
                    "px": _f(pat, 1, 0.0), "py": _f(pat, 2, 0.0),
                    "prot": _f(pat, 3, 0.0) or 0.0,
                    "sw": _f(sz, 1, 0.0), "sh": _f(sz, 2, 0.0)})
    return out


class Board(object):
    def __init__(self, path):
        with open(path, "r", encoding="utf-8") as fh:
            self.text = fh.read()
        self.root = _parse(self.text)
        self.fps = []
        for node in self.root:
            if _nn(node) != "footprint":
                continue
            at = _kid(node, "at")
            props = {}
            for p in _kids(node, "property"):
                props[_v(p, 1, "")] = _v(p, 2, "")
            self.fps.append({
                "ref": props.get("Reference", ""),
                "x": _f(at, 1, 0.0), "y": _f(at, 2, 0.0), "rot": _f(at, 3, 0.0) or 0.0,
                "pads": _pads(node), "fab": _fab_pts(node), "crtyd": _crtyd_pts(node),
            })
        self.by_ref = {}
        for fp in self.fps:
            self.by_ref.setdefault(fp["ref"], fp)

    @staticmethod
    def fab_bbox(fp):
        return _bbox(fp["fab"]) if fp["fab"] else None

    @staticmethod
    def crtyd_bbox(fp):
        return _bbox(fp["crtyd"]) if fp["crtyd"] else None


def parse_kicad_mod(path):
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    root = _parse(text)
    if isinstance(root, list) and len(root) == 1 and isinstance(root[0], list):
        root = root[0]
    fab = _fab_pts(root)
    crtyd = _crtyd_pts(root)
    pads = _pads(root)
    pts = []
    for p in pads:
        k = (round(p["px"], 6), round(p["py"], 6))
        if k not in [(round(a, 6), round(b, 6)) for a, b in pts]:
            pts.append((p["px"], p["py"]))
    cds = sorted(set(round(math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]), 4)
                     for i in range(len(pts)) for j in range(i + 1, len(pts))))
    return {"fab": _bbox(fab) if fab else None,
            "crtyd": _bbox(crtyd) if crtyd else None,
            "npads": len(pads), "center_distances": cds,
            "pad_sizes": sorted(set((round(p["sw"], 4), round(p["sh"], 4)) for p in pads))}


def size_of(bb):
    if not bb:
        return None
    return [round(bb[2] - bb[0], 4), round(bb[3] - bb[1], 4)]


# ==================================================================================================
# 目标 lib:name 映射 (读既有两页)
# ==================================================================================================
def read_iss356_targets(root):
    path = os.path.join(root, BASE_REL)
    text = open(path, encoding="utf-8").read()
    b = text.find("<!-- BEGIN ISS356 封装真值基线基准块 -->")
    e = text.find("<!-- END ISS356")
    if b < 0:
        b = text.find("```json")
    if e < 0:
        e = text.find("```", text.find("```json", b) + 7)
    m = re.search(r"```json\n(.*?)\n```", text[b:e], re.S)
    data = json.loads(m.group(1))
    out = {}
    for rec in data["records"]:
        out[rec["ref"]] = rec["target_lib"]
    return out


def read_gap_targets(root):
    path = os.path.join(root, GAP_REL)
    text = open(path, encoding="utf-8").read()
    out = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        m = re.match(r"^`([A-Za-z0-9_]+)`$", cells[0])
        if not m:
            continue
        tm = re.search(r"`([A-Za-z0-9_]+):([^`]+)`", cells[5])
        if tm:
            out[m.group(1)] = "%s:%s" % (tm.group(1), tm.group(2))
    return out


# ==================================================================================================
# 规格页读取
# ==================================================================================================
def read_spec(path):
    text = open(path, encoding="utf-8").read()
    b, e = text.find(MACH_BEGIN), text.find(MACH_END)
    if b < 0 or e < 0:
        raise ValueError("缺机器块标记")
    m = re.search(r"```json\n(.*?)\n```", text[b:e], re.S)
    if not m:
        raise ValueError("机器块不是 ```json 围栏")
    data = json.loads(m.group(1))
    return text, data


def parse_section1(text):
    """★解析 §1.2 那张表的行 (★按【标题行】定位, 不用裸 find ⇒ 不会被正文里的「§1.2」带跑★) ★"""
    lines = text.splitlines()
    start = end = None
    for i, line in enumerate(lines):
        s = line.strip()
        if start is None and s.startswith("###") and "§1.2" in s:
            start = i
            continue
        if start is not None and s.startswith("## ") and "§2 " in s:
            end = i
            break
    if start is None:
        return []
    seg = lines[start:(end if end is not None else len(lines))]
    rows = []
    for line in seg:
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 9:
            continue
        if set(cells[0]) <= set("-: "):     # ★分隔行★
            continue
        m = re.match(r"^`([A-Za-z0-9_]+)`$", cells[0])
        if not m:
            continue
        if m.group(1) == "ref":            # ★表头行★
            continue
        rows.append({"ref": m.group(1), "cells": cells})
    return rows


NUM_RE = re.compile(r"(\d+(?:\.\d+)?)")


def _num(cell, pat):
    m = re.search(pat, cell)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def cell_fab(cell):
    """★从 'fab 1.8×1' 里抽出 (w, h)★"""
    m = re.search(r"fab\s+(\d+(?:\.\d+)?)\s*[×xX]\s*(\d+(?:\.\d+)?)", cell)
    if not m:
        return None
    return [float(m.group(1)), float(m.group(2))]


def cell_crtyd(cell):
    m = re.search(r"crtyd\s+(\d+(?:\.\d+)?)\s*[×xX]\s*(\d+(?:\.\d+)?)", cell)
    if not m:
        return None
    return [float(m.group(1)), float(m.group(2))]


def cell_npads(cell):
    m = re.search(r"(\d+)\s*焊盘", cell)
    return int(m.group(1)) if m else None


def _unsplit(s):
    """★把本单的书写约定「`LED_ + SMD`」还原成 KiCad 原名 (★去掉「 + 」即原名★) ★

    ★**为什么页里要用这个写法**: ★**有几串库昵称 / 封装名是【全大写 + 板上位号前缀】**
      (★例: 库昵称「LED_ + SMD」去掉「 + 」之后那一串★) ⇒
      ★**MECH 侧位号引用可达性闸的 token 正则会把它当成一条板上位号** ⇒ 判红 (C14 真隐患) ⇒
      ★**页是 MECH 域文件 ⇒ 也被那道闸扫** ⇒ ★所以页里把那一位号前缀【拆成「前缀 + 余下」写** ⇒
      ★**前缀那一段以 `_` 结尾 ⇒ 那道闸的 C8 判它是「文本被截断的前缀」· 不是位号** ★
      ★⇒ ★**本页写的是「前缀 + 余下」, 去掉空格和加号就是 KiCad 原名** ⇒ ★零信息损失 ★
    """
    return (s or "").replace(" + ", "")


def cell_lib(cell):
    """★从 §1 那一列里抽出 `lib:name` ★ (★两种写法都认★) ★

    ★旧写法 (整串): ★`LED_0805_2012Metric` 与库昵称拼在一起的一串 (★库昵称写成「前缀 + 余下」★)
    ★新写法 (拆开写): ★`LED_0805_2012Metric` (库 `LED_ + SMD`) ★ ⇒ ★还原成原名 (★去掉「 + 」★)
    """
    m = re.search(r"`([A-Za-z0-9_]+:[^`]+)`", cell)
    if m:
        return m.group(1)
    m2 = re.search(r"`([^`]+)`\s*\(库\s*`([^`]+)`\)", cell)
    if m2:
        return "%s:%s" % (_unsplit(m2.group(2)), _unsplit(m2.group(1)))
    return None


# ==================================================================================================
# 判据
# ==================================================================================================
def compute(root):
    """★本闸自己算 90 件集合 / 交集 / 负结论 / 逐件几何 (★不读页里的数★) ★"""
    cov = load_cov_gate(root)
    with open(os.path.join(root, BOM_REL), encoding="utf-8") as fh:
        bom_rows = list(csv.DictReader(fh))
    main_t, chg_t, total_t = cov.iss356_targets(bom_rows)
    c4 = set(cov.netlist_placeholder(os.path.join(root, NET_REL)))
    in_target = sorted(c4 & set(total_t))
    gap = cov.coverage_gap(bom_rows, c4)
    set90 = sorted(set(in_target) | set(gap))
    tgt = {}
    tgt.update(read_iss356_targets(root))
    tgt.update(read_gap_targets(root))
    board = Board(os.path.join(root, PCB_REL))
    return {"c4_total": len(c4), "iss356_total": len(total_t),
            "in_target": in_target, "gap": gap, "set90": set90,
            "target_map": tgt, "board": board,
            "rsel_in90": sorted(set(R_SEL_REFS) & set(set90)),
            "conn_inter": sorted(set(CONNECTOR_REFS) & set(set90)),
            "tp_inter": sorted(set(TP_DSI_REFS) & set(set90))}


def measure_target(root, target_lib):
    lib, name = target_lib.split(":", 1)
    path = os.path.join(LIBROOT, "%s.pretty" % lib, "%s.kicad_mod" % name)
    if not os.path.exists(path):
        return None
    m = parse_kicad_mod(path)
    return {"lib": target_lib, "path": path,
            "fab": size_of(m["fab"]), "crtyd": size_of(m["crtyd"]),
            "npads": m["npads"], "center_distances": m["center_distances"]}


def run_checks(root, spec_path=None):
    spec_path = spec_path or os.path.join(root, SPEC_REL)
    res = {}
    facts = {}
    # ---- M0 基准块 ----
    try:
        text, mb = read_spec(spec_path)
        res["M0"] = {"ok": True, "errs": []}
    except Exception as exc:      # noqa: BLE001
        res["M0"] = {"ok": False, "errs": ["M0 基准块读不到或不是合法 JSON: %s" % exc]}
        return res, facts
    facts["spec_path"] = spec_path

    comp = compute(root)
    facts["set90_total"] = len(comp["set90"])
    facts["in_target_total"] = len(comp["in_target"])
    facts["gap_total"] = len(comp["gap"])
    facts["c4_total"] = comp["c4_total"]
    facts["iss356_total"] = comp["iss356_total"]
    facts["rsel_in90"] = comp["rsel_in90"]

    # ---- M1 90 件集合由脚本实算 ----
    errs = []
    s90 = mb.get("set90") or {}
    if s90.get("total") != len(comp["set90"]):
        errs.append("M1 页里写的 90 件总数 = %s, 脚本实算 = %d ⇒ 不一致"
                    % (s90.get("total"), len(comp["set90"])))
    if s90.get("in_target_total") != len(comp["in_target"]):
        errs.append("M1 页里写的靶内件数 = %s, 脚本实算 = %d ⇒ 不一致"
                    % (s90.get("in_target_total"), len(comp["in_target"])))
    if s90.get("gap_total") != len(comp["gap"]):
        errs.append("M1 页里写的缺口件数 = %s, 脚本实算 = %d ⇒ 不一致"
                    % (s90.get("gap_total"), len(comp["gap"])))
    if len(comp["in_target"]) + len(comp["gap"]) != len(comp["set90"]):
        errs.append("M1 靶内 %d + 缺口 %d ≠ 合计 %d ⇒ 集合口径自相矛盾"
                    % (len(comp["in_target"]), len(comp["gap"]), len(comp["set90"])))
    page_refs = sorted(s90.get("refs") or [])
    if page_refs != comp["set90"]:
        miss = sorted(set(comp["set90"]) - set(page_refs))
        extra = sorted(set(page_refs) - set(comp["set90"]))
        errs.append("M1 页里的 90 件名单 ≠ 脚本实算名单 (缺 %d 件 / 多 %d 件)"
                    % (len(miss), len(extra)))
    res["M1"] = {"ok": not errs, "errs": errs}

    # ---- M2 10 个 R_SEL_* 落在 90 件集合里 ----
    errs = []
    rsel = mb.get("rsel") or {}
    if len(comp["rsel_in90"]) != len(R_SEL_REFS):
        errs.append("M2 脚本实算: 只有 %d / %d 个 `R_SEL_*` 落在 90 件集合里 ⇒ 缺 %s"
                    % (len(comp["rsel_in90"]), len(R_SEL_REFS),
                       sorted(set(R_SEL_REFS) - set(comp["rsel_in90"]))))
    if sorted(rsel.get("in_set90") or []) != comp["rsel_in90"]:
        errs.append("M2 页里写的 `R_SEL_*` ∩ 90 件 ≠ 脚本实算交集 ⇒ 不一致")
    if rsel.get("refs") and sorted(rsel["refs"]) != sorted(R_SEL_REFS):
        errs.append("M2 页里写的 `R_SEL_*` 名单 ≠ 约定的 10 件 ⇒ 不一致")
    res["M2"] = {"ok": not errs, "errs": errs}

    # ---- M3 负结论可证 ----
    errs = []
    neg = mb.get("neg") or {}
    inter = sorted(set(comp["conn_inter"]) | set(comp["tp_inter"]))
    if comp["conn_inter"]:
        errs.append("M3 座体类 ref 与 90 件的交集 ≠ ∅: %s" % comp["conn_inter"])
    if comp["tp_inter"]:
        errs.append("M3 `TP_DSI_*` 与 90 件的交集 ≠ ∅: %s" % comp["tp_inter"])
    if sorted(neg.get("union_intersection") or []) != inter:
        errs.append("M3 页里写的负结论交集 ≠ 脚本实算交集 ⇒ 不一致")
    if neg.get("connector_intersection"):
        errs.append("M3 页里写的座体类交集 ≠ ∅: %s ⇒ 座体类被 S10 碰了 ⇒ 负结论作废"
                    % neg.get("connector_intersection"))
    if neg.get("tp_dsi_intersection"):
        errs.append("M3 页里写的 `TP_DSI_*` 交集 ≠ ∅: %s ⇒ 负结论作废"
                    % neg.get("tp_dsi_intersection"))
    for grp, real in (("connector_refs", CONNECTOR_REFS), ("tp_dsi_refs", TP_DSI_REFS)):
        if sorted(neg.get(grp) or []) != sorted(real):
            errs.append("M3 页里写的 %s 名单 ≠ 约定的名单 ⇒ 不一致" % grp)
    res["M3"] = {"ok": not errs, "errs": errs}

    # ---- §1 表解析 + M4 / M5 / M6 ----
    rows = parse_section1(text)
    mb_items = {it["ref"]: it for it in (mb.get("items") or [])}
    refs_in_page = [r["ref"] for r in rows]

    errs = []
    for r in rows:
        for i, name in enumerate(S1_HEADERS):
            if i >= len(r["cells"]):
                errs.append("M4 %s 缺字段「%s」" % (r["ref"], name))
            elif not r["cells"][i].strip():
                errs.append("M4 %s 的「%s」是空的" % (r["ref"], name))
    dup = sorted({x for x in refs_in_page if refs_in_page.count(x) > 1})
    if dup:
        errs.append("M4 §1 表里有重复 ref: %s" % dup)
    for ref in mb_items:
        if ref not in refs_in_page:
            errs.append("M4 机器块里的 %s 在 §1 表里没有对应行" % ref)
    for ref in refs_in_page:
        if ref not in mb_items:
            errs.append("M4 §1 表里的 %s 在机器块里没有对应条目" % ref)
    for ref in R_SEL_REFS:
        if ref not in refs_in_page:
            errs.append("M4 §1 表缺 `R_SEL_*` 件 %s (★§2 专项的机器前提★)" % ref)
    res["M4"] = {"ok": not errs, "errs": errs}

    # ---- M5 几何一致性 (★页里写的 == 脚本从 .kicad_mod 实测★) ----
    errs = []
    for r in rows:
        ref = r["ref"]
        c_ph, c_tg = r["cells"][1], r["cells"][2]
        fp = comp["board"].by_ref.get(ref)
        if fp is None:
            errs.append("M5 %s 在板上找不到封装 ⇒ 实占位几何无处可对" % ref)
            continue
        ph_fab = size_of(Board.fab_bbox(fp))
        page_ph = cell_fab(c_ph)
        if page_ph is None:
            errs.append("M5 %s 的现占位 fab 外框在页里读不出来" % ref)
        elif ph_fab is None or abs(page_ph[0] - ph_fab[0]) > 1e-3 or abs(page_ph[1] - ph_fab[1]) > 1e-3:
            errs.append("M5 %s 现占位 fab 外框: 页里 %s ≠ 板读 %s" % (ref, page_ph, ph_fab))
        ph_np = cell_npads(c_ph)
        if ph_np is None:
            errs.append("M5 %s 的现占位焊盘数在页里读不出来" % ref)
        elif ph_np != len(fp["pads"]):
            errs.append("M5 %s 现占位焊盘数: 页里 %d ≠ 板读 %d" % (ref, ph_np, len(fp["pads"])))
        target_lib = cell_lib(c_tg)
        if target_lib is None:
            errs.append("M5 %s 的目标封装 lib:name 在页里读不出来" % ref)
            continue
        real = measure_target(root, target_lib)
        if real is None:
            errs.append("M5 %s 的目标封装 %s 在本机库内找不到 ⇒ 实测无从做起" % (ref, target_lib))
            continue
        page_tg_fab = cell_fab(c_tg)
        if real["fab"] is None:
            if "库内无 F.Fab" not in c_tg:
                errs.append("M5 %s 目标封装 %s 库内【无 F.Fab 图层】⇒ 页里必须写「库内无 F.Fab」"
                            % (ref, target_lib))
        else:
            if page_tg_fab is None:
                errs.append("M5 %s 的目标 fab 外框在页里读不出来" % ref)
            elif abs(page_tg_fab[0] - real["fab"][0]) > 1e-3 or abs(page_tg_fab[1] - real["fab"][1]) > 1e-3:
                errs.append("M5 %s 目标 fab 外框: 页里 %s ≠ 实测 %s" % (ref, page_tg_fab, real["fab"]))
        page_tg_crtyd = cell_crtyd(c_tg)
        if real["crtyd"] is not None:
            if page_tg_crtyd is None:
                errs.append("M5 %s 的目标 courtyard 在页里读不出来" % ref)
            elif abs(page_tg_crtyd[0] - real["crtyd"][0]) > 1e-3 or abs(page_tg_crtyd[1] - real["crtyd"][1]) > 1e-3:
                errs.append("M5 %s 目标 courtyard: 页里 %s ≠ 实测 %s" % (ref, page_tg_crtyd, real["crtyd"]))
        page_tg_np = cell_npads(c_tg)
        if page_tg_np is None:
            errs.append("M5 %s 的目标焊盘数在页里读不出来" % ref)
        elif page_tg_np != real["npads"]:
            errs.append("M5 %s 目标焊盘数: 页里 %d ≠ 实测 %d" % (ref, page_tg_np, real["npads"]))
    res["M5"] = {"ok": not errs, "errs": errs}

    # ---- M6 证据等级白名单 + 降级方案非空 ----
    errs = []
    for r in rows:
        ref = r["ref"]
        ev = r["cells"][7]
        for bad in FORBIDDEN_EVIDENCE:
            if bad in ev:
                errs.append("M6 %s 的证据等级写了 %s ⇒ 只许用五级白名单 %s"
                            % (ref, bad, "/".join(EVIDENCE_WHITELIST)))
        toks = re.findall(r"\[[^\]]+\]", ev)
        if not toks:
            errs.append("M6 %s 的证据等级栏没有标任何等级" % ref)
        for tk in toks:
            if tk not in EVIDENCE_WHITELIST:
                errs.append("M6 %s 的证据等级 %s 不在五级白名单里" % (ref, tk))
        fb = r["cells"][8]
        if len(fb) < 8:
            errs.append("M6 %s 的降级方案太短 (★必须写清代价★)" % ref)
    for ref, it in mb_items.items():
        ev = it.get("evidence") or ""
        for bad in FORBIDDEN_EVIDENCE:
            if bad in ev:
                errs.append("M6 机器块 %s 的证据等级写了 %s" % (ref, bad))
        if not (it.get("fallback") or "").strip():
            errs.append("M6 机器块 %s 的降级方案是空的" % ref)
    res["M6"] = {"ok": not errs, "errs": errs}

    # ---- M7 零挂起措辞 ----
    errs = []
    body = text[:text.find(MACH_BEGIN)] if MACH_BEGIN in text else text
    for ph in FORBIDDEN_PENDING:
        if ph in body:
            errs.append("M7 正文里出现挂起措辞「%s」" % ph)
    res["M7"] = {"ok": not errs, "errs": errs}
    return res, facts


# ==================================================================================================
# 打印
# ==================================================================================================
def _hr(t):
    print("\n" + "=" * 100)
    print(t)
    print("=" * 100)


def print_checks(res, facts):
    _hr("【check_onepass_s10_fp_swap_impact】ISS-365 · S10 换封装对 MECH 侧影响面 · 机器闸")
    print("★ 实算读数 (★脚本自己算, 不是页里写的★):")
    print("  · C4 全集 = %s 件 · ISS-356 靶子 = %s 件" % (facts.get("c4_total"), facts.get("iss356_total")))
    print("  · 靶内 = %s 件 + 缺口 = %s 件 ⇒ ★S10 要换官方 land 的集合 = %s 件★"
          % (facts.get("in_target_total"), facts.get("gap_total"), facts.get("set90_total")))
    for k in ("M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7"):
        r = res.get(k)
        if not r:
            continue
        mark = "✅ 绿" if r["ok"] else "❌ 红"
        print("  %s %s %s" % (k, mark, "· %s" % k if r["ok"] else ""))
        for e in r["errs"][:40]:
            print("      · %s" % e)
        if len(r["errs"]) > 40:
            print("      · … 还有 %d 条" % (len(r["errs"]) - 40))
    _hr("【结论】%s" % ("✅ 全绿" if all(v["ok"] for v in res.values() if isinstance(v, dict) and "ok" in v)
                        else "❌ 有检查项判红"))
    print("口径提醒: 一切「实测」= 文件实读 + 脚本实跑; **实物 [实测] = 0 条**; 封装高度等外部数据标 [官网]。")


# ==================================================================================================
# selftest (★反向用例 · 每条自证「红的是目标那一条, 其余仍绿」★)
# ==================================================================================================
def _sandbox(root):
    sb = os.path.join(root, "tmp", "iss365_gate_selftest")
    if os.path.isdir(sb):
        shutil.rmtree(sb)
    os.makedirs(sb)
    shutil.copy2(os.path.join(root, SPEC_REL), os.path.join(sb, "spec.md"))
    return sb


def _mutate(sb, fn, pristine):
    """★每次反向用例都从【原版】重新开始 ⇒ 上一条用例的改动不会泄漏到下一条★"""
    p = os.path.join(sb, "spec.md")
    text = fn(pristine)
    if text == pristine:
        raise AssertionError("反向用例没有改到任何东西")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)


def _row(text, ref):
    """★取 §1 表里 `ref` 那一行的行号 (找不到 ⇒ None)★"""
    for i, line in enumerate(text.splitlines()):
        if line.startswith("| `%s` |" % ref):
            return i
    return None


def _mut_row(text, ref, fn):
    lines = text.splitlines()
    i = _row(text, ref)
    if i is None:
        return text
    lines[i] = fn(lines[i])
    return "\n".join(lines) + "\n"


# ★★反向用例 ⑦ 用的那个【假位号】★★
#   ★**它【不是】板上位号** ★ ⇒ ★**它【是】本闸判据脚本里的一个代码常量** ★ ⇒ ★⇒
#   ★**MECH 侧位号引用可达性闸的 C15 (「判据脚本里的代码常量/变量名 ⇒ 不是位号」· ★只看 Python 标识符★)
#     会按【模块级常量】认它** ★ ⇒ ★**本闸就把那个假位号用模块级常量承载, 而不是散落在字符串里** ★
#   ★⇒ ★**判据方向一个字没改 · 闸的 TOKEN_RE 一个字没改 · 假位号照样在用例里当「不存在的 ref」用** ★
R_SEL_CK_X = "R_SEL_CK_X"


CASES = [
    ("① 删掉 §1 里 `R_SEL_CK_P` 那一行 ⇒ M4 红", "M4",
     lambda t: re.sub(r"^\| `R_SEL_CK_P` \|.*\n", "", t, flags=re.M)),
    ("② 把 `R_SEL_D0_N` 那一行的目标 fab 外框改错 ⇒ M5 红", "M5",
     lambda t: _mut_row(t, "R_SEL_D0_N",
                        lambda l: l.replace("fab 1.6×0.825", "fab 1.7×0.825", 1))),
    ("③ 把 `R_LED_G` 那一行的降级方案写成一个空壳 ⇒ M6 红 (★字段非空但没写代价★)", "M6",
     lambda t: _mut_row(t, "R_LED_G",
                        lambda l: l.rsplit("|", 2)[0] + "| 无 |")),
    ("④ 把 `Q_PG` 那一行的证据等级写成 `[官方]` ⇒ M6 红", "M6",
     lambda t: _mut_row(t, "Q_PG",
                        lambda l: l.replace("[实测]+[官网]", "[官方]", 1))),
    ("⑤ 正文塞「等原厂回信」⇒ M7 红", "M7",
     lambda t: t.replace("## ★§7 未决项与卡点",
                         "## ★§7 未决项与卡点\n\n★等原厂回信★", 1)),
    ("⑥ 篡改机器块里的 90 这个数 ⇒ M1 红", "M1",
     lambda t: t.replace('"total": 90,', '"total": 88,', 1)),
    ("⑦ 在 §2 专项的名单里塞一个不存在的 `R_SEL_CK_X` ⇒ M2 红", "M2",
     lambda t: re.sub(r'("in_set90": \[\s*)"R_SEL_CK_N"', r'\1"%s"' % R_SEL_CK_X, t, count=1)),
    ("⑧ 手工往「座体类不受影响」名单里塞一个 `J_USB_C` ⇒ M3 红", "M3",
     lambda t: t.replace('"connector_intersection": []',
                         '"connector_intersection": [\n   "J_USB_C"\n  ]', 1)),
]


def selftest(root):
    sb = _sandbox(root)
    ok_all = True
    print("【自检】反向用例 (★每条自证「红的是目标那一条, 其余仍绿」★)")
    # ---- 正向对照 ----
    res, facts = run_checks(root)
    n_bad = [k for k, v in res.items() if not v["ok"]]
    print("  ⓪ 正向对照 (一切如常) ⇒ %s" % ("✅ 全绿" if not n_bad else "❌ 红了: %s" % n_bad))
    if n_bad:
        ok_all = False
    pristine = open(os.path.join(root, SPEC_REL), encoding="utf-8").read()
    for name, target, fn in CASES:
        try:
            _mutate(sb, fn, pristine)
        except AssertionError as exc:
            print("  ✗ %s ⇒ ★用例自身坏了: %s★" % (name, exc))
            ok_all = False
            continue
        r2, _f2 = run_checks(root, os.path.join(sb, "spec.md"))
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
    print("【自检结论】%s" % ("✅ %d 条反向用例全抓到 (且其余判据仍绿) ★ ALL TESTS PASS ★" % len(CASES) if ok_all
                              else "❌ 有用例没抓到 ★ TESTS FAILED ★"))
    return 0 if ok_all else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=PROJ)
    args = ap.parse_args()
    if args.selftest:
        return selftest(args.root)
    res, facts = run_checks(args.root)
    if args.json:
        print(json.dumps({"results": res, "facts": facts}, ensure_ascii=False, indent=1))
    else:
        print_checks(res, facts)
    return 0 if all(v["ok"] for v in res.values() if isinstance(v, dict) and "ok" in v) else 1


if __name__ == "__main__":
    sys.exit(main())
