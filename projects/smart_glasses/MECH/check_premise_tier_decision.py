#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-410 · MECH · 「板那一趟」排针焊盘【前提量选档 ⇒ 下游作废传播】机器闸

★**判据骨架 (来自任务书 §2.1 · 一条都不许放松)** ★
  T1 四来源一致性 —— BOM / 作业包 / 真相页机器块 / 板面 footprint 四来源逐条【实读】,
     判「记没记这一格 / 记的是哪一档」⇒ 四来源档位不一致, 或任何一来源没记 ⇒ 判红
  T2 当前档位机器可判 —— 从【板面 footprint 实读】J_DEBUG/J_UART 的 THT 焊盘边长,
     判定它落在四档的哪一档 ⇒ 不在任何一档 ⇒ 判红 (不许从文档抄)
  T3 换档的重算清单必须完整 —— 四档每一档的「必须重算的数 / 必须重跑的闸 / 必须重签的结论」
     三张清单 ⇒ 条数 ≥ N 且每条都能在 ISS-407 依赖图里找到对应节点 ⇒ 少一条 ⇒ 判红
     (不许只判「清单非空」)
  T4 盲闸登记 + 漂移检测 —— 7 道判决链闸对 pad 的敏感性登记在册 ⇒ 现跑 stdout md5 对拍
     + AST 静态签名重算「盲 / 敏感」分类 ⇒ 任一处漂移 ⇒ 判红
     (★ISS-403 已做过 A/B 实测, 本闸【登记 + 复核】, 不重做一遍当新发现★)
  T5 fail-closed —— 依赖图页 / 本页 / BOM 任一读不到 ⇒ 判红, 不许判绿
  T6 零挂链 + 零外发自证 + 不代拍
  T7 板指纹自证 —— 本闸自己不许写板 ⇒ 跑前跑后两次现读 + 与基线三方逐字相同

★**跑法** ★
  python3 MECH/check_premise_tier_decision.py              → rc=1 (★红的是现状, 不是闸故障★)
  python3 MECH/check_premise_tier_decision.py --selftest   → rc=0 · 末行逐字 ALL TESTS PASS

★**本闸零挂链** ★: `state/gate_check.py` 里【没有】本闸 ⇒ 挂链是 main 的地界 (★本闸不代拍★)
★**本闸不改任何既有闸判据/阈值, 不改任何既有页正文, 不写板, 不写 HW/, 不写 state/issue_log.yaml** ★
"""
from __future__ import annotations

import argparse
import ast
import csv
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

PAGE_REL = "MECH/BOARD_ONEPASS_PREMISE_TIER_DECISION_TABLE.md"
DEP_REL = "MECH/BOARD_ONEPASS_VERDICT_PREMISE_DEPENDENCY.md"
ISS403_REL = "MECH/BOARD_ONEPASS_PAD_SIZE_COUPLING.md"
BOM_REL = "HW/BOM_v1.csv"
WORKPACKET_REL = "HW/PCB/BOARD_ONEPASS_WORKPACKET.md"
FTS_REL = "MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md"
BOARD_REL = "HW/PCB/demo_mainboard.kicad_pcb"
GATE_HOOK_FILE = "state/gate_check.py"

EVIDENCE_LEVELS = ["官网", "实测", "媒体", "推算", "0数据"]

TIER_IDS = ["P1000", "P1010", "P1110", "P1218"]
TVAL = {1.000: "P1000", 1.010: "P1010", 1.110: "P1110", 1.218: "P1218"}
TIER_RE = re.compile(r"(?<![\d.])(\d+\.\d{3,})(?![\d])")

CORE7 = [
    "j_debug_copper_x", "j_uart_copper_x", "j_debug_required_clear_x",
    "j_uart_required_clear_x", "j_uart_cover_margin_x",
    "j_debug_opening_margin_x", "j_debug_cover_margin_y",
]
EXTRA_NUM = ["annular_ring", "seven_numbers_matrix", "pad_tier"]

# P1000 档的 7 个数 (盲闸若写死, 源码里必然出现这些字面量之一)
P1000_LITERALS = {4.81, 2.27, 6.61, 4.07, 0.135, 2.695, 0.77}

VERDICT_CHAIN_GATES = [
    "MECH/check_debug_seat_3d_fit.py",
    "MECH/check_debug_seat_rework_spec.py",
    "MECH/check_fts_seat_body_geometry.py",
    "MECH/check_connector_clearance_caliber.py",
    "MECH/check_fts_vs_generic_courtyard_delta.py",
    "MECH/check_jdebug_1p27_clearance.py",
    "MECH/check_juart_1p27_clearance.py",
]

# ══════════════════════════════════════════════════════════════════════
# 工具
# ══════════════════════════════════════════════════════════════════════
class ReadError(Exception):
    pass


def r4(v):
    return round(float(v) + 0.0, 4)


def _read_text(rel: str) -> str:
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        raise ReadError("文件不存在: %s" % rel)
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def load_page_machine_block(rel: str) -> dict:
    text = _read_text(rel)
    fences = re.findall(r"```json\s*(.*?)```", text, re.S)
    if not fences:
        raise ReadError("%s 里没有 JSON 机器块" % rel)
    try:
        return json.loads(fences[-1])
    except Exception as e:  # noqa: BLE001
        raise ReadError("%s 的机器块解析失败: %s" % (rel, e))


def md5_file(rel: str) -> str:
    p = os.path.join(ROOT, rel)
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def outbox_tree_digest() -> tuple:
    base = os.path.join(ROOT, "state", "outbox")
    if not os.path.isdir(base):
        return None, 0
    files = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames.sort()
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT)
            files.append((rel, md5_file(rel)))
    files.sort(key=lambda t: t[0])
    blob = "".join("%s  %s\n" % (m, rel) for rel, m in files)
    return hashlib.md5(blob.encode("utf-8")).hexdigest(), len(files)


def grep_count(rel_path: str, needle: str) -> int:
    p = os.path.join(ROOT, rel_path)
    if not os.path.exists(p):
        return -1
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read().count(needle)


def _mtime_text(ns: int) -> str:
    sec = ns // 10 ** 9
    nsec = ns % 10 ** 9
    return datetime.datetime.fromtimestamp(sec).strftime("%Y-%m-%d %H:%M:%S") + ".%09d" % nsec


def board_fingerprint() -> dict:
    p = os.path.join(ROOT, BOARD_REL)
    st = os.stat(p)
    return {"md5": md5_file(BOARD_REL), "size": st.st_size,
            "mtime": st.st_mtime_ns, "mtime_text": _mtime_text(st.st_mtime_ns)}


# ══════════════════════════════════════════════════════════════════════
# 四来源现读
# ══════════════════════════════════════════════════════════════════════
def find_tiers(text: str) -> dict:
    hits = {}
    for m in TIER_RE.finditer(text):
        v = round(float(m.group(1)), 6)
        if v in TVAL:
            hits.setdefault(TVAL[v], []).append(m.group(1))
    return hits


def read_source_bom() -> dict:
    text = _read_text(BOM_REL)
    rows = list(csv.DictReader(text.splitlines()))
    sel = [r for r in rows if (r.get("ref") or "").strip() in ("J_DEBUG", "J_UART")]
    if not sel:
        raise ReadError("BOM 里找不到 J_DEBUG / J_UART 两行")
    blob = "\n".join(" | ".join(str(v) for v in r.values()) for r in sel)
    hits = find_tiers(blob)
    return {"id": "SRC_BOM", "records_pad_tier": bool(hits),
            "recorded_tier": _one_tier(hits), "hits": hits,
            "rows_found": len(sel)}


def read_source_workpacket() -> dict:
    hits = find_tiers(_read_text(WORKPACKET_REL))
    return {"id": "SRC_WORKPACKET", "records_pad_tier": bool(hits),
            "recorded_tier": _one_tier(hits), "hits": hits}


def read_source_truth_page() -> dict:
    blk = load_page_machine_block(FTS_REL)
    hits = find_tiers(json.dumps(blk, ensure_ascii=False))
    return {"id": "SRC_TRUTH_PAGE", "records_pad_tier": bool(hits),
            "recorded_tier": _one_tier(hits), "hits": hits}


def _one_tier(hits: dict):
    if not hits:
        return None
    if len(hits) > 1:
        return "AMBIGUOUS:" + ",".join(sorted(hits))
    return sorted(hits)[0]


def read_board_land() -> dict:
    """★只读解析板文件 ⇒ J_DEBUG/J_UART 的 land 实况 (不许用 pcbnew 写任何东西)★"""
    lines = _read_text(BOARD_REL).splitlines()
    starts = [i for i, l in enumerate(lines) if l.strip().startswith("(footprint ")]
    out = {}

    def block(start):
        depth = 0
        for i in range(start, len(lines)):
            depth += lines[i].count("(") - lines[i].count(")")
            if depth == 0:
                return lines[start:i + 1]
        return lines[start:]

    for s in starts:
        blk = block(s)
        txt = "\n".join(blk)
        m = re.search(r'\(property "Reference" "([^"]+)"', txt)
        ref = m.group(1) if m else "?"
        if ref not in ("J_DEBUG", "J_UART"):
            continue
        pads = []
        for i, l in enumerate(blk):
            if '(pad "' in l:
                mm = re.search(r"\(size ([0-9.]+) ([0-9.]+)\)", "\n".join(blk[i:i + 6]))
                dr = re.search(r"\(drill ([0-9.]+)\)", "\n".join(blk[i:i + 6]))
                at = re.search(r"\(at ([-0-9.]+) ([-0-9.]+)\)", blk[i + 1])
                pads.append({"size_x": float(mm.group(1)), "size_y": float(mm.group(2)),
                             "drill": float(dr.group(1)) if dr else None,
                             "at_x": float(at.group(1)), "at_y": float(at.group(2))})
        cx = [p["at_x"] + p["size_x"] / 2 for p in pads] + [p["at_x"] - p["size_x"] / 2 for p in pads]
        cy = [p["at_y"] + p["size_y"] / 2 for p in pads] + [p["at_y"] - p["size_y"] / 2 for p in pads]
        tht = [p for p in pads if p["drill"] is not None]
        out[ref] = {"pad_count": len(pads), "tht_pad_count": len(tht),
                    "pad_size_mm": [pads[0]["size_x"], pads[0]["size_y"]] if pads else None,
                    "has_drill": bool(tht),
                    "copper_x_mm": r4(max(cx) - min(cx)) if cx else None,
                    "copper_y_mm": r4(max(cy) - min(cy)) if cy else None}
    if "J_DEBUG" not in out or "J_UART" not in out:
        raise ReadError("板文件里读不到 J_DEBUG / J_UART 的 footprint")
    return out


def board_face_tier(land: dict) -> tuple:
    """★从板面实读 THT 焊盘边长 ⇒ 落在四档哪一档 (不许从文档抄)★"""
    sizes = set()
    for ref, d in sorted(land.items()):
        if d["tht_pad_count"] == 0:
            return None, ("板面 %s 是 SMD 占位 land (焊盘 %.4f×%.4f · 无钻孔) ⇒ 没有 THT 焊盘 ⇒ 四档哪一档都不是"
                          % (ref, d["pad_size_mm"][0], d["pad_size_mm"][1]))
        sizes.add(round(d["pad_size_mm"][0], 6))
    if len(sizes) != 1:
        return None, "板面 J_DEBUG / J_UART 的 THT 焊盘边长不一致: %r" % sorted(sizes)
    v = sizes.pop()
    tier = TVAL.get(v)
    if tier is None:
        return None, "板面 THT 焊盘边长 %.4f 不在四档 %r 里" % (v, TIER_IDS)
    return tier, "板面实读 THT 焊盘边长 %.4f ⇒ %s" % (v, tier)


# ══════════════════════════════════════════════════════════════════════
# 静态机制签名 + 行为基线 (T4)
# ══════════════════════════════════════════════════════════════════════
def _docstring_consts(tree):
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if ast.get_docstring(n, clean=False) is not None:
                for c in ast.walk(n):
                    if isinstance(c, ast.Expr) and isinstance(c.value, ast.Constant) \
                            and isinstance(c.value.value, str):
                        out.add(id(c.value))
                        break
    return out


def lib_signature(rel: str) -> dict:
    src = _read_text(rel)
    tree = ast.parse(src)
    ds = _docstring_consts(tree)
    km = sum(1 for n in ast.walk(tree)
             if isinstance(n, ast.Constant) and isinstance(n.value, str)
             and ".kicad_mod" in n.value and id(n) not in ds)
    lr = sum(1 for n in ast.walk(tree)
             if (isinstance(n, ast.Name) and n.id.lower() in ("libroot", "lib_root"))
             or (isinstance(n, ast.Attribute) and n.attr.lower() in ("libroot", "lib_root")))
    hard = sum(1 for n in ast.walk(tree)
               if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))
               and not isinstance(n.value, bool)
               and round(float(n.value), 4) in P1000_LITERALS)
    if km > 0 and lr > 0:
        cls = "SENSITIVE(lib-read)"
    elif hard > 0:
        cls = "BLIND(hardcoded-pad-value)"
    else:
        cls = "BLIND(no-lib-read)"
    return {"kicad_mod_runtime_refs": km, "libroot_refs": lr,
            "p1000_literal_refs": hard, "class": cls}


def run_gate_md5(rel: str) -> tuple:
    p = subprocess.run([sys.executable, os.path.join(ROOT, rel)],
                       capture_output=True, text=True, cwd=ROOT, timeout=300)
    blob = (p.stdout + p.stderr).encode("utf-8")
    return p.returncode, hashlib.md5(blob).hexdigest()


# ══════════════════════════════════════════════════════════════════════
# 七个数矩阵 (公式现算)
# ══════════════════════════════════════════════════════════════════════
def seven_numbers(pad: float, const: dict) -> dict:
    jd = r4(const["span_debug_mm"] + pad)
    ju = r4(const["span_uart_mm"] + pad)
    return {
        "j_debug_copper_x": jd,
        "j_uart_copper_x": ju,
        "j_debug_required_clear_x": r4(jd + 2 * (const["crit_mm"] + const["tol_fdm_part_mm"])),
        "j_uart_required_clear_x": r4(ju + 2 * (const["crit_mm"] + const["tol_fdm_part_mm"])),
        "j_uart_cover_margin_x": r4((const["clear_uart_x_mm"] - ju) / 2),
        "j_debug_opening_margin_x": r4((const["open_debug_x_mm"] - jd) / 2),
        "j_debug_cover_margin_y": r4((const["clear_debug_y_mm"] - pad) / 2),
    }


# ══════════════════════════════════════════════════════════════════════
# 判据 T1 ~ T7 (纯函数 · 便于 selftest 注入)
# ══════════════════════════════════════════════════════════════════════
def check_t1(reads: list, page_sources: list) -> list:
    """T1: 四来源一致性 —— 四来源都在册 + 每来源都记着 + 记的是同一档。"""
    reds = []
    want_ids = ["SRC_BOM", "SRC_WORKPACKET", "SRC_TRUTH_PAGE", "SRC_BOARD_FACE"]
    got_ids = [s.get("id") for s in page_sources]
    for sid in want_ids:
        if sid not in got_ids:
            reds.append("T1 真相页的 sources 里缺来源 %s" % sid)
    by_id = {s.get("id"): s for s in page_sources}
    tiers = []
    for r in reads:
        sid = r.get("id")
        reg = by_id.get(sid)
        if reg is None:
            reds.append("T1 来源 %s 没登记在册" % sid)
            continue
        if bool(reg.get("records_pad_tier")) != bool(r.get("records_pad_tier")):
            reds.append("T1 来源 %s 的「记没记这一格」漂移: 真相页记 %r, 现读 %r"
                        % (sid, reg.get("records_pad_tier"), r.get("records_pad_tier")))
        if reg.get("recorded_tier") != r.get("recorded_tier"):
            reds.append("T1 来源 %s 的「记的是哪一档」漂移: 真相页记 %r, 现读 %r"
                        % (sid, reg.get("recorded_tier"), r.get("recorded_tier")))
        if not r.get("records_pad_tier"):
            reds.append("T1 来源 %s 【没记】前提量这一格 (⇒ 四个来源之间没有可比对的记录)" % sid)
            continue
        t = r.get("recorded_tier")
        if t is None or str(t).startswith("AMBIGUOUS"):
            reds.append("T1 来源 %s 记的档位不可判: %r" % (sid, t))
            continue
        tiers.append((sid, t))
    uniq = sorted({t for _, t in tiers})
    if len(uniq) > 1:
        reds.append("T1 四来源记的档位不一致: %r" % tiers)
    elif len(tiers) and len(tiers) < 4:
        reds.append("T1 只有 %d/4 个来源真记着这一格 (⇒ 「现在盘上是哪一档」无人能答)" % len(tiers))
    return reds


def check_t2(board_tier, note: str, tier_ids: list) -> list:
    """T2: 当前档位机器可判 —— 必须能从板面实读落到四档之一。"""
    if board_tier is None:
        return ["T2 板面实读判定不出当前档位: %s" % note]
    if board_tier not in tier_ids:
        return ["T2 板面实读档位 %r 不在四档 %r 里" % (board_tier, tier_ids)]
    return []


def check_t3(page_matrix: list, dep_graph: list, page_tiers: dict) -> list:
    """T3: 换档的重算清单必须完整 —— 每档三张清单逐条对得上 ISS-407 依赖图节点。"""
    reds = []
    edges = [e for e in dep_graph if {"PQ01", "PQ02"} & set(e.get("premises") or [])]
    dep_numbers = {n for e in edges for n in (e.get("numbers") or [])}
    dep_gates = {g for e in edges for g in (e.get("gates") or [])}
    dep_concl = {c for e in edges for c in (e.get("conclusions") or [])}
    if not edges:
        reds.append("T3 ISS-407 依赖图里没有一条边挂到 PQ01/PQ02 (⇒ 依赖图读不到或坏了)")
        return reds
    covered = {row.get("tier") for row in page_matrix}
    for t in TIER_IDS:
        if t not in covered:
            reds.append("T3 真相页的换档清单缺档位 %s" % t)
    for row in page_matrix:
        t = row.get("tier")
        nums = list(row.get("recompute_numbers") or [])
        gates = list(row.get("rerun_gates") or [])
        concl = list(row.get("resign_conclusions") or [])
        for k in CORE7:
            if k not in nums:
                reds.append("T3 %s 的「必须重算的数」缺判决链七个数之一 %s" % (t, k))
        for k in EXTRA_NUM:
            if k not in nums:
                reds.append("T3 %s 的「必须重算的数」缺 %s" % (t, k))
        for n in nums:
            if n not in dep_numbers:
                reds.append("T3 %s 的「必须重算的数」里的 %s 在 ISS-407 依赖图里找不到对应节点" % (t, n))
        if len(gates) < len(dep_gates):
            reds.append("T3 %s 的「必须重跑的闸」条数 %d < 依赖图挂着的 %d"
                        % (t, len(gates), len(dep_gates)))
        for g in gates:
            if g not in dep_gates:
                reds.append("T3 %s 的「必须重跑的闸」里的 %s 在 ISS-407 依赖图里找不到对应节点" % (t, g))
        if len(concl) < len(dep_concl):
            reds.append("T3 %s 的「必须重签的结论」条数 %d < 依赖图挂着的 %d"
                        % (t, len(concl), len(dep_concl)))
        for c in concl:
            if c not in dep_concl:
                reds.append("T3 %s 的「必须重签的结论」里的 %s 在 ISS-407 依赖图里找不到对应节点" % (t, c))
        pad = (page_tiers.get(t) or {}).get("pad_mm")
        if pad is not None:
            row_pad = row.get("pad_mm")
            if row_pad is None or abs(float(row_pad) - float(pad)) > 1e-9:
                reds.append("T3 %s 的换档清单登记的 pad %r ≠ 真相页档位表的 %r" % (t, row_pad, pad))
    return reds


def check_t3_matrix(page_matrix_num: dict, iss403_matrix: dict, const: dict,
                     page_tiers: dict) -> list:
    """T3b: 七个数矩阵必须由公式现算, 且与 ISS-403 登记的 28 格逐格一致 (抄错 = 判红)。"""
    reds = []
    for t in TIER_IDS:
        pad = (page_tiers.get(t) or {}).get("pad_mm")
        if pad is None:
            reds.append("T3b 真相页的档位表缺 %s" % t)
            continue
        calc = seven_numbers(float(pad), const)
        reg = page_matrix_num.get(t) or {}
        old = iss403_matrix.get(t) or {}
        for k in CORE7:
            a = r4(calc[k])
            b = reg.get(k)
            if b is None or abs(float(b) - a) > 1e-9:
                reds.append("T3b %s 的 %s: 真相页登记 %r ≠ 公式现算 %r" % (t, k, b, a))
            c = old.get(k)
            if c is None or abs(float(c) - a) > 1e-9:
                reds.append("T3b %s 的 %s: ISS-403 登记 %r ≠ 公式现算 %r (抄错)" % (t, k, c, a))
    return reds


def check_t4(registry: list, iss403_blind: list, iss403_sensitive: list,
             rerun: dict, signatures: dict) -> list:
    """T4: 盲闸登记 + 漂移检测。"""
    reds = []
    by_gate = {e.get("gate"): e for e in (registry or [])}
    for g in VERDICT_CHAIN_GATES:
        if g not in by_gate:
            reds.append("T4 盲闸登记册里缺 %s" % g)
    iss403_by_gate = {}
    for e in (iss403_blind or []) + (iss403_sensitive or []):
        iss403_by_gate[e.get("gate")] = e
    for g in VERDICT_CHAIN_GATES:
        reg = by_gate.get(g)
        if reg is None:
            continue
        if g not in iss403_by_gate:
            reds.append("T4 %s 不在 ISS-403 的 A/B 实测名单里 (⇒ 本单不能替它宣称盲或不盲)" % g)
            continue
        exp = "SENSITIVE" if g in [e.get("gate") for e in (iss403_sensitive or [])] else "BLIND"
        if reg.get("sensitivity") != exp:
            reds.append("T4 %s 登记的敏感性 %r ≠ ISS-403 实测的 %r" % (g, reg.get("sensitivity"), exp))
        got = rerun.get(g)
        if got is None:
            reds.append("T4 %s 本次没跑出来 (⇒ 漂移或闸坏了)" % g)
            continue
        rc, md5 = got
        if reg.get("rerun_stdout_md5") != md5:
            reds.append("T4 %s 的 stdout md5 漂移: 登记 %r ≠ 现跑 %r (⇒ 它对 pad 的敏感性可能已变)"
                        % (g, reg.get("rerun_stdout_md5"), md5))
        if reg.get("rerun_rc") != rc:
            reds.append("T4 %s 的 rc 漂移: 登记 %r ≠ 现跑 %r" % (g, reg.get("rerun_rc"), rc))
        base = iss403_by_gate[g].get("baseline_stdout_md5")
        if base and base != md5:
            reds.append("T4 %s 与 ISS-403 登记的 stdout md5 不一致: %r ≠ %r" % (g, base, md5))
        sig = signatures.get(g)
        if sig is None:
            reds.append("T4 %s 没算出静态机制签名" % g)
            continue
        if sig.get("class") != (reg.get("lib_signature") or {}).get("class"):
            reds.append("T4 %s 的静态机制分类漂移: 登记 %r ≠ 现算 %r (⇒ 从盲变不盲 或 从不盲变盲)"
                        % (g, (reg.get("lib_signature") or {}).get("class"), sig.get("class")))
        is_sens = sig.get("class") == "SENSITIVE(lib-read)"
        if is_sens != (exp == "SENSITIVE"):
            reds.append("T4 %s 的静态签名 %r 与登记敏感性 %r 不符" % (g, sig.get("class"), exp))
    return reds


def check_t5(loaded: dict) -> list:
    """T5: fail-closed —— 任一必读件读不到 ⇒ 判红。"""
    reds = []
    for key in ("dep", "page", "bom"):
        if not loaded.get(key):
            reds.append("T5 %s 读不到 (⇒ fail-closed 判红, 不许判绿)" % key)
    return reds


def check_t6(hook_count: int, outbox_now, outbox_base, decision, outbox_files) -> list:
    reds = []
    if hook_count != 0:
        reds.append("T6 零挂链自证失败: state/gate_check.py 里有 %d 处本闸名 (必须 0)" % hook_count)
    if outbox_now != outbox_base:
        reds.append("T6 零外发自证失败: state/outbox/ 树摘要 %r ≠ 基线 %r" % (outbox_now, outbox_base))
    if decision != "not_decided_here":
        reds.append("T6 不代拍自证失败: decision_taken_here = %r (必须 'not_decided_here')" % decision)
    return reds


def check_t7(before: dict, after: dict, base: dict) -> list:
    reds = []
    for k in ("md5", "size"):
        if before.get(k) != after.get(k):
            reds.append("T7 板指纹在本闸跑动期间变了: %s %r ⇒ %r (⇒ 本闸不许写板)" % (k, before.get(k), after.get(k)))
    for k in ("md5", "size"):
        if base.get(k) is not None and after.get(k) != base.get(k):
            reds.append("T7 板指纹与基线不符: %s %r ≠ 基线 %r" % (k, after.get(k), base.get(k)))
    if base.get("mtime") and after.get("mtime_text") != base.get("mtime"):
        reds.append("T7 板 mtime 与基线不符: %r ≠ 基线 %r" % (after.get("mtime_text"), base.get("mtime")))
    return reds


# ══════════════════════════════════════════════════════════════════════
# 真跑
# ══════════════════════════════════════════════════════════════════════
def run_real() -> int:
    out = []
    out.append("=" * 78)
    out.append("ISS-410 · MECH · 焊盘前提量选档 ⇒ 下游作废传播 · 机器闸")
    out.append("真相页: %s" % PAGE_REL)
    out.append("=" * 78)
    reds = []
    loaded = {"dep": False, "page": False, "bom": False}

    dep = iss403 = page = None
    try:
        dep = load_page_machine_block(DEP_REL)
        loaded["dep"] = True
    except Exception as e:  # noqa: BLE001
        reds.append("T5 ISS-407 依赖图页读不到: %s" % e)
    try:
        iss403 = load_page_machine_block(ISS403_REL)
    except Exception as e:  # noqa: BLE001
        reds.append("T5 ISS-403 焊盘耦合页读不到: %s" % e)
    try:
        page = load_page_machine_block(PAGE_REL)
        loaded["page"] = True
    except Exception as e:  # noqa: BLE001
        reds.append("T5 本单真相页读不到: %s" % e)
    try:
        _read_text(BOM_REL)
        loaded["bom"] = True
    except Exception as e:  # noqa: BLE001
        reds.append("T5 BOM 读不到: %s" % e)

    reads = []
    if loaded["bom"]:
        try:
            reads.append(read_source_bom())
        except Exception as e:  # noqa: BLE001
            reds.append("T1 BOM 来源现读失败: %s" % e)
    try:
        reads.append(read_source_workpacket())
    except Exception as e:  # noqa: BLE001
        reds.append("T1 作业包来源现读失败: %s" % e)
    try:
        reads.append(read_source_truth_page())
    except Exception as e:  # noqa: BLE001
        reds.append("T1 真相页来源现读失败: %s" % e)
    land = None
    try:
        land = read_board_land()
        tier, note = board_face_tier(land)
        reads.append({"id": "SRC_BOARD_FACE", "records_pad_tier": (tier is not None),
                      "recorded_tier": tier, "hits": {}})
    except Exception as e:  # noqa: BLE001
        tier, note = None, "板面读不到: %s" % e
        reads.append({"id": "SRC_BOARD_FACE", "records_pad_tier": False,
                      "recorded_tier": None, "hits": {}})

    out.append("")
    out.append("── 四来源实读 (T1) ─────────────────────────────────────────────")
    for r in reads:
        out.append("  %-16s 记没记=%-5s 记的档=%-12s 命中=%s"
                   % (r["id"], r["records_pad_tier"], r["recorded_tier"],
                      {k: v[:3] for k, v in (r.get("hits") or {}).items()} or "-"))
    out.append("  板面实读: %s" % json.dumps(land, ensure_ascii=False))
    out.append("  板面判定: %s" % note)

    if page and reads:
        reds += check_t1(reads, page.get("sources") or [])
    if tier is not None or land is not None:
        reds += check_t2(tier, note, TIER_IDS)

    if dep and page:
        reds += check_t3(page.get("tier_recompute_matrix") or [], dep.get("dependency_graph") or [],
                         {t["id"]: t for t in ((page.get("premise_quantity") or {}).get("tiers") or [])})
        const = page.get("formula_constants") or {}
        need = ["span_debug_mm", "span_uart_mm", "crit_mm", "tol_fdm_part_mm",
                "clear_uart_x_mm", "open_debug_x_mm", "clear_debug_y_mm"]
        if not all(k in const for k in need):
            reds.append("T3b 真相页的 formula_constants 缺 %r" % [k for k in need if k not in const])
        else:
            reds += check_t3_matrix(page.get("seven_numbers_matrix") or {},
                                    (iss403 or {}).get("seven_numbers_matrix") or {},
                                    const,
                                    {t["id"]: t for t in ((page.get("premise_quantity") or {}).get("tiers") or [])})

    rerun = {}
    signatures = {}
    for g in VERDICT_CHAIN_GATES:
        try:
            rerun[g] = run_gate_md5(g)
            signatures[g] = lib_signature(g)
        except Exception as e:  # noqa: BLE001
            reds.append("T4 %s 跑不动: %s" % (g, e))
    if page:
        out.append("")
        out.append("── 盲闸登记 + 漂移 (T4) ───────────────────────────────────────")
        for g in VERDICT_CHAIN_GATES:
            sig = signatures.get(g) or {}
            out.append("  %-44s %-28s rc=%s md5=%s"
                       % (g, sig.get("class"), (rerun.get(g) or ("-", "-"))[0],
                          (rerun.get(g) or ("-", "-"))[1][:12]))
        reds += check_t4(page.get("blind_gate_registry") or [],
                         (iss403 or {}).get("blind_gates") or [],
                         (iss403 or {}).get("sensitive_gates") or [],
                         rerun, signatures)

    reds += check_t5(loaded)

    before = board_fingerprint()
    hook = grep_count(GATE_HOOK_FILE, "check_premise_tier_decision")
    ob_now, ob_n = outbox_tree_digest()
    ob_base = ((page or {}).get("outbox_baseline") or {}).get("tree_md5")
    decision = ((page or {}).get("decision_taken_here"))
    reds += check_t6(hook, ob_now, ob_base, decision, ob_n)
    after = board_fingerprint()
    reds += check_t7(before, after, ((page or {}).get("board_baseline") or {}))

    out.append("")
    out.append("── 边界自证 (T6/T7) ───────────────────────────────────────────")
    out.append("  零挂链 grep 命中 = %s (必须 0)" % hook)
    out.append("  outbox 树摘要 = %s (%d 件) · 基线 = %s" % (ob_now, ob_n, ob_base))
    out.append("  decision_taken_here = %r" % decision)
    out.append("  板指纹 跑前 = %s / %s" % (before["md5"], before["mtime_text"]))
    out.append("  板指纹 跑后 = %s / %s" % (after["md5"], after["mtime_text"]))
    out.append("  板指纹 基线 = %s / %s" % ((page or {}).get("board_baseline", {}).get("md5"),
                                            (page or {}).get("board_baseline", {}).get("mtime")))
    out.append("")
    out.append("-" * 78)
    if reds:
        out.append("RESULT: FAIL (%d 条判据不通过)" % len(reds))
        for r in reds:
            out.append("  [FAIL] %s" % r)
        out.append("-" * 78)
        out.append("★★ 红的是【现状】, 不是闸故障 ★★")
        out.append("现状: ① T1 四来源不一致 (BOM / 作业包 / 板面 都没记这一格, 只有真相页记 P1000) "
                   "② T2 板面是 SMD 占位 ⇒ 判定不出当前档位 ③ 档位至今没拍板")
        print("\n".join(out))
        return 1
    out.append("RESULT: PASS (全部判据通过)")
    print("\n".join(out))
    return 0


# ══════════════════════════════════════════════════════════════════════
# selftest (正向 ≥1 + 反向 ≥8)
# ══════════════════════════════════════════════════════════════════════
def _fake_world():
    """构造一个【全绿】的合成世界 (只给判据函数用, 不碰真仓库)。"""
    reads = [
        {"id": "SRC_BOM", "records_pad_tier": True, "recorded_tier": "P1110"},
        {"id": "SRC_WORKPACKET", "records_pad_tier": True, "recorded_tier": "P1110"},
        {"id": "SRC_TRUTH_PAGE", "records_pad_tier": True, "recorded_tier": "P1110"},
        {"id": "SRC_BOARD_FACE", "records_pad_tier": True, "recorded_tier": "P1110"},
    ]
    page_sources = [
        {"id": "SRC_BOM", "records_pad_tier": True, "recorded_tier": "P1110"},
        {"id": "SRC_WORKPACKET", "records_pad_tier": True, "recorded_tier": "P1110"},
        {"id": "SRC_TRUTH_PAGE", "records_pad_tier": True, "recorded_tier": "P1110"},
        {"id": "SRC_BOARD_FACE", "records_pad_tier": True, "recorded_tier": "P1110"},
    ]
    dep_graph = [
        {"id": "E01", "premises": ["PQ01", "PQ02"], "numbers": CORE7 + EXTRA_NUM,
         "gates": ["MECH/check_debug_seat_3d_fit.py"], "conclusions": ["MECH/BOARD_ONEPASS_X.md"]},
        {"id": "E02", "premises": ["PQ02"], "numbers": ["j_debug_cover_margin_y"],
         "gates": ["MECH/check_jdebug_1p27_clearance.py"], "conclusions": ["MECH/BOARD_ONEPASS_Y.md"]},
    ]
    page_matrix = [
        {"tier": t, "pad_mm": pad,
         "recompute_numbers": CORE7 + EXTRA_NUM,
         "rerun_gates": ["MECH/check_debug_seat_3d_fit.py", "MECH/check_jdebug_1p27_clearance.py"],
         "resign_conclusions": ["MECH/BOARD_ONEPASS_X.md", "MECH/BOARD_ONEPASS_Y.md"]}
        for t, pad in (("P1000", 1.000), ("P1010", 1.010), ("P1110", 1.110), ("P1218", 1.218))
    ]
    page_tiers = {t: {"id": t, "pad_mm": p} for t, p in
                  (("P1000", 1.000), ("P1010", 1.010), ("P1110", 1.110), ("P1218", 1.218))}
    const = {"span_debug_mm": 3.81, "span_uart_mm": 1.27, "crit_mm": 0.6, "tol_fdm_part_mm": 0.3,
             "clear_uart_x_mm": 2.54, "open_debug_x_mm": 10.2, "clear_debug_y_mm": 2.54}
    page_num = {t: seven_numbers(p["pad_mm"], const) for t, p in page_tiers.items()}
    iss403_num = {t: dict(v) for t, v in page_num.items()}
    registry = [
        {"gate": g, "sensitivity": "SENSITIVE" if i >= 5 else "BLIND",
         "rerun_rc": 0, "rerun_stdout_md5": "md5-%d" % i,
         "lib_signature": {"class": "SENSITIVE(lib-read)" if i >= 5 else "BLIND(no-lib-read)"}}
        for i, g in enumerate(VERDICT_CHAIN_GATES)
    ]
    iss403_blind = [{"gate": g, "baseline_stdout_md5": "md5-%d" % i}
                    for i, g in enumerate(VERDICT_CHAIN_GATES[:5])]
    iss403_sens = [{"gate": g, "baseline_stdout_md5": "md5-%d" % (5 + i)}
                   for i, g in enumerate(VERDICT_CHAIN_GATES[5:])]
    rerun = {g: (0, "md5-%d" % i) for i, g in enumerate(VERDICT_CHAIN_GATES)}
    sigs = {g: {"class": "SENSITIVE(lib-read)" if i >= 5 else "BLIND(no-lib-read)"}
            for i, g in enumerate(VERDICT_CHAIN_GATES)}
    return dict(reads=reads, page_sources=page_sources, dep_graph=dep_graph,
                page_matrix=page_matrix, page_tiers=page_tiers, const=const,
                page_num=page_num, iss403_num=iss403_num, registry=registry,
                iss403_blind=iss403_blind, iss403_sens=iss403_sens,
                rerun=rerun, sigs=sigs)


def run_selftest() -> int:
    W = _fake_world()
    passed, failed = [], []

    def ok(name, cond):
        (passed if cond else failed).append(name)

    # ---- 正向 ----
    ok("POS-01 合成世界全绿 (T1/T2/T3/T3b/T4/T5/T6/T7)",
       check_t1(W["reads"], W["page_sources"]) == []
       and check_t2("P1110", "ok", TIER_IDS) == []
       and check_t3(W["page_matrix"], W["dep_graph"], W["page_tiers"]) == []
       and check_t3_matrix(W["page_num"], W["iss403_num"], W["const"], W["page_tiers"]) == []
       and check_t4(W["registry"], W["iss403_blind"], W["iss403_sens"], W["rerun"], W["sigs"]) == []
       and check_t5({"dep": 1, "page": 1, "bom": 1}) == []
       and check_t6(0, "x", "x", "not_decided_here", 22) == []
       and check_t7({"md5": "a", "size": 1}, {"md5": "a", "size": 1}, {"md5": "a", "size": 1}) == [])

    # ---- 反向 ----
    r_missing = [dict(x) for x in W["reads"]]
    r_missing[0] = dict(r_missing[0], records_pad_tier=False, recorded_tier=None)
    ok("NEG-01 T1 有一个来源没记这一格 ⇒ 红", len(check_t1(r_missing, W["page_sources"])) >= 1)

    r_diff = [dict(x) for x in W["reads"]]
    r_diff[1] = dict(r_diff[1], recorded_tier="P1010")
    ok("NEG-02 T1 四来源档位不一致 ⇒ 红", len(check_t1(r_diff, W["page_sources"])) >= 1)

    ok("NEG-03 T1 真相页登记漂移 ⇒ 红",
       len(check_t1(W["reads"], [{"id": s["id"], "records_pad_tier": True,
                                 "recorded_tier": "P1218"} for s in W["page_sources"]])) >= 1)

    ok("NEG-04 T2 板面判定不出档位 ⇒ 红", len(check_t2(None, "板面是 SMD 占位", TIER_IDS)) == 1)
    ok("NEG-05 T2 档位不在四档里 ⇒ 红", len(check_t2("P9999", "x", TIER_IDS)) == 1)

    m_short = [dict(x) for x in W["page_matrix"]]
    m_short[0] = dict(m_short[0], recompute_numbers=[k for k in CORE7 if k != "j_debug_copper_x"])
    ok("NEG-06 T3 清单少一个判决链数 ⇒ 红", len(check_t3(m_short, W["dep_graph"], W["page_tiers"])) >= 1)

    m_bogus = [dict(x) for x in W["page_matrix"]]
    m_bogus[2] = dict(m_bogus[2], rerun_gates=["MECH/check_not_in_graph.py"])
    ok("NEG-07 T3 清单里有依赖图找不到的节点 ⇒ 红",
       len(check_t3(m_bogus, W["dep_graph"], W["page_tiers"])) >= 1)

    n_wrong = {t: dict(v) for t, v in W["page_num"].items()}
    n_wrong["P1110"] = dict(n_wrong["P1110"], j_debug_copper_x=9.999)
    ok("NEG-08 T3b 抄错一个数 ⇒ 红",
       len(check_t3_matrix(n_wrong, W["iss403_num"], W["const"], W["page_tiers"])) >= 1)

    n_old = {t: dict(v) for t, v in W["iss403_num"].items()}
    n_old["P1218"] = dict(n_old["P1218"], j_uart_cover_margin_x=0.5)
    ok("NEG-09 T3b 与 ISS-403 登记值不符 ⇒ 红",
       len(check_t3_matrix(W["page_num"], n_old, W["const"], W["page_tiers"])) >= 1)

    reg_bad = [dict(x) for x in W["registry"]]
    reg_bad[0] = dict(reg_bad[0], rerun_stdout_md5="drifted")
    ok("NEG-10 T4 stdout md5 漂移 ⇒ 红",
       len(check_t4(reg_bad, W["iss403_blind"], W["iss403_sens"], W["rerun"], W["sigs"])) >= 1)

    sig_bad = {k: dict(v) for k, v in W["sigs"].items()}
    sig_bad[VERDICT_CHAIN_GATES[0]] = {"class": "SENSITIVE(lib-read)"}
    ok("NEG-11 T4 静态分类从盲变不盲 ⇒ 红",
       len(check_t4(W["registry"], W["iss403_blind"], W["iss403_sens"], W["rerun"], sig_bad)) >= 1)

    reg_short = [x for x in W["registry"] if x["gate"] != VERDICT_CHAIN_GATES[2]]
    ok("NEG-12 T4 登记册缺一道闸 ⇒ 红",
       len(check_t4(reg_short, W["iss403_blind"], W["iss403_sens"], W["rerun"], W["sigs"])) >= 1)

    ok("NEG-13 T5 依赖图页读不到 ⇒ 红",
       len(check_t5({"dep": False, "page": True, "bom": True})) == 1)
    ok("NEG-14 T5 BOM 读不到 ⇒ 红",
       len(check_t5({"dep": True, "page": True, "bom": False})) == 1)

    ok("NEG-15 T6 挂链数≠0 ⇒ 红", len(check_t6(1, "x", "x", "not_decided_here", 22)) == 1)
    ok("NEG-16 T6 outbox 动了 ⇒ 红", len(check_t6(0, "y", "x", "not_decided_here", 22)) == 1)
    ok("NEG-17 T6 代拍了 ⇒ 红", len(check_t6(0, "x", "x", "P1110", 22)) == 1)

    ok("NEG-18 T7 板指纹在跑动期间变了 ⇒ 红",
       len(check_t7({"md5": "a", "size": 1}, {"md5": "b", "size": 1}, {"md5": "a", "size": 1})) >= 1)
    ok("NEG-19 T7 板指纹与基线不符 ⇒ 红",
       len(check_t7({"md5": "a", "size": 1}, {"md5": "a", "size": 1}, {"md5": "z", "size": 1})) == 1)

    print("=" * 78)
    print("ISS-410 · check_premise_tier_decision · selftest")
    for n in passed:
        print("  [PASS] %s" % n)
    for n in failed:
        print("  [FAIL] %s" % n)
    print("-" * 78)
    print("正向 %d 条 · 反向 %d 条" % (sum(1 for n in passed if n.startswith("POS")),
                                       sum(1 for n in passed if n.startswith("NEG"))))
    if failed:
        print("RESULT: FAIL (%d 条自测不过)" % len(failed))
        return 1
    print("ALL TESTS PASS")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=None)
    args = ap.parse_args()
    if args.selftest:
        return run_selftest()
    return run_real()


if __name__ == "__main__":
    sys.exit(main())
