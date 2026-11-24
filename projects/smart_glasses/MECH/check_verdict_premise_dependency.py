#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-407 · MECH · 「板那一趟」MECH 判决链【前提依赖图 + 作废传播矩阵】机器闸

★**判据骨架 (来自任务书 §2.1 · 一条都不许放松)** ★
  D1 前提量清单可机器重建 —— 每个前提量的「当前值 + 真值读取点」必须能被脚本重新读出来
     (不许手抄数值) ⇒ 读不出来 ⇒ 判红 (这本身就是「前提没有真值来源」的病)
  D2 依赖图自洽 —— 每个前提量至少挂到 1 个数 / 闸 / 结论上 ⇒ 孤立的前提量 ⇒ 判红
  D3 写死常量点必须进依赖图 —— 判决链闸源码里的几何字面量 (AST 实扫, 不许手抄)
     必须逐条出现在依赖图的「写死常量点」栏里 ⇒ 漏一条 ⇒ 判红
  D4 作废传播矩阵与依赖图一致 —— 矩阵里每一格都必须能在依赖图里找到对应边 ⇒ 多/少一格 ⇒ 判红
  D5 板三证不动 —— 板 / 网表 / 脚表 / BOM md5 与基线逐字相同
  D6 零挂链 + 零外发自证 + 证据分级

★**跑法** ★
  python3 MECH/check_verdict_premise_dependency.py              → rc=1 (★红的是现状, 不是闸故障★)
  python3 MECH/check_verdict_premise_dependency.py --selftest   → rc=0 · 末行逐字 ALL TESTS PASS

★**本闸零挂链** ★: `state/gate_check.py` 里【没有】本闸 ⇒ 挂链是 main 的地界 (★本闸不代拍★)
★**本闸不改任何既有闸判据/阈值, 不改任何既有页正文** ★
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

PAGE_REL = "MECH/BOARD_ONEPASS_VERDICT_PREMISE_DEPENDENCY.md"
GATE_REL = "MECH/check_verdict_premise_dependency.py"

EVIDENCE_LEVELS = ["官网", "实测", "媒体", "推算", "0数据"]

# ══════════════════════════════════════════════════════════════════════
# 写死常量扫描 · 规则 HC-SCAN-v2 (单一事实源: 真相页与本闸都从这里取)
# ══════════════════════════════════════════════════════════════════════
VERDICT_CHAIN_GATES = [
    "MECH/check_debug_seat_3d_fit.py",
    "MECH/check_debug_seat_rework_spec.py",
    "MECH/check_fts_seat_body_geometry.py",
    "MECH/check_fts_vs_generic_courtyard_delta.py",
    "MECH/check_fts_seat_sample_plan.py",
    "MECH/check_jdebug_1p27_clearance.py",
    "MECH/check_juart_1p27_clearance.py",
    "MECH/check_connector_clearance_caliber.py",
    "MECH/check_pad_size_coupling_closed.py",
]

GEOM_TOKEN = re.compile(
    r"(COPPER|COUPLER|CLR|CLEAR|CLEARANCE|OPEN|OPENING|HOUSING|SEAT|BODY|"
    r"WIDTH|HEIGHT|DEPTH|THICK|THICKNESS|PAD|PITCH|SPAN|MARGIN|OFFSET|GAP|"
    r"HOLE|DRILL|SIZE|LENGTH|POSITION|FAB|CRTYD|COURTYARD|FOOTPRINT|"
    r"ANNULAR|RING|CRIT|TOL|ZONE|KEEPOUT|DATUM|ORIGIN|X_MM|Y_MM|Z_MM)",
    re.IGNORECASE,
)

GEOMETRY_VALUE_SET = {
    0.65, 0.71, 1.01, 1.11, 1.218,
    1.27, 3.81, 4.81, 2.27, 6.61, 4.07,
    0.135, 2.695, 0.77, 0.08, 0.715, 0.026, 0.661,
    0.6, 0.3, 0.25, 0.15, 0.2, 0.145,
    1.775, 4.085, 2.54, 10.2, 17.62, 20.16, 67.33, 69.87,
    55.33, 57.87, 137.85, 148.05, 13.79, 23.99, 66.3, 70.9,
    0.52, 1.8, 0.86, 2.16, 5.08, 1.6, 0.085, 0.765, 0.775, 0.9,
}

MIN_ABS = 0.001
MAX_ABS = 1000.0
COMPARE_FN = re.compile(r"^(near|eq|almost|approx|equal|close|within|tol|nearish)$", re.IGNORECASE)


def _is_num(node) -> bool:
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, (int, float))
        and not isinstance(node.value, bool)
    )


def _f(v) -> float:
    return round(float(v), 9)


def _dict_paths(node, path, out):
    for k, v in zip(node.keys, node.values):
        kn = k.value if isinstance(k, ast.Constant) else None
        kp = "%s.%s" % (path, kn if kn is not None else "?")
        if _is_num(k):
            out.append((kp, "dict_key", _f(k.value), k.lineno))
        if _is_num(v):
            out.append((kp, "dict_value", _f(v.value), v.lineno))
        elif isinstance(v, ast.Dict):
            _dict_paths(v, kp, out)
        elif isinstance(v, (ast.List, ast.Tuple)):
            for i, e in enumerate(v.elts):
                if _is_num(e):
                    out.append(("%s[%d]" % (kp, i), "list_value", _f(e.value), e.lineno))
                elif isinstance(e, ast.Dict):
                    _dict_paths(e, "%s[%d]" % (kp, i), out)


def scan_gate_constants(rel_path: str, root: str = None) -> list[dict]:
    root = root or ROOT
    path = os.path.join(root, rel_path)
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    lines = src.splitlines()
    tree = ast.parse(src)
    hits: dict[tuple, dict] = {}

    def add(lineno, value, rule, ctx):
        key = (rel_path, lineno, value)
        if key in hits:
            hits[key]["rules"].add(rule)
            return
        hits[key] = {"gate": rel_path, "line": lineno, "value": value, "rules": {rule}, "ctx": ctx}

    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            val = node.value
            for t in targets:
                if not isinstance(t, ast.Name):
                    continue
                nm = t.id
                if _is_num(val):
                    if GEOM_TOKEN.search(nm):
                        add(node.lineno, _f(val.value), "R1", nm)
                elif isinstance(val, ast.Dict):
                    sub = []
                    _dict_paths(val, nm, sub)
                    for p, kind, v, ln in sub:
                        if GEOM_TOKEN.search(p):
                            add(ln, v, "R2", p)
                elif isinstance(val, (ast.List, ast.Tuple)):
                    for i, e in enumerate(val.elts):
                        if _is_num(e) and GEOM_TOKEN.search(nm):
                            add(e.lineno, _f(e.value), "R2", "%s[%d]" % (nm, i))

    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            sub = []
            _dict_paths(node, "<dict>", sub)
            for p, kind, v, ln in sub:
                if GEOM_TOKEN.search(p):
                    add(ln, v, "R2", p)

    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for side in list(node.comparators) + [node.left]:
                if _is_num(side):
                    v = _f(side.value)
                    if v in GEOMETRY_VALUE_SET:
                        add(side.lineno, v, "R3", "compare")
                elif isinstance(side, ast.Call):
                    for a in list(side.args) + [k.value for k in side.keywords]:
                        if _is_num(a):
                            v = _f(a.value)
                            if v in GEOMETRY_VALUE_SET:
                                add(a.lineno, v, "R3", "compare-arg")

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else "")
            if not COMPARE_FN.match(name or ""):
                continue
            for a in list(node.args) + [k.value for k in node.keywords]:
                if _is_num(a):
                    v = _f(a.value)
                    if v in GEOMETRY_VALUE_SET:
                        add(a.lineno, v, "R3'", "%s(...)" % name)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get":
            for a in list(node.args)[1:]:
                if _is_num(a):
                    v = _f(a.value)
                    if v in GEOMETRY_VALUE_SET:
                        add(a.lineno, v, "R4", "get-default")

    out = []
    for (g, ln, v), d in hits.items():
        if not (MIN_ABS <= abs(d["value"]) <= MAX_ABS):
            continue
        d["rules"] = sorted(d["rules"])
        d["text"] = lines[ln - 1].strip()[:150]
        out.append(d)
    out.sort(key=lambda d: (d["gate"], d["line"], d["value"]))
    return out


def scan_all_constants(root: str = None) -> list[dict]:
    out = []
    for g in VERDICT_CHAIN_GATES:
        out.extend(scan_gate_constants(g, root=root))
    return out


# ══════════════════════════════════════════════════════════════════════
# 前提量读点实现 (每种 kind 一个读取器)
# ══════════════════════════════════════════════════════════════════════
class ReadError(Exception):
    pass


def _read_text(path: str) -> str:
    if not os.path.exists(path):
        raise ReadError("文件不存在: %s" % path)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


_PAD_BLOCK = re.compile(r"\(pad\b")
_PAD_AT = re.compile(r"\(at\s+([-\d.]+)\s+([-\d.]+)\)")


def _kicad_pad_blocks(text: str) -> list[str]:
    idxs = [m.start() for m in _PAD_BLOCK.finditer(text)]
    out = []
    for i, s in enumerate(idxs):
        e = idxs[i + 1] if i + 1 < len(idxs) else len(text)
        out.append(text[s:e])
    return out


def read_kicad_mod_pad(text: str, axis: str) -> float:
    sizes = re.findall(r"\(size\s+([-\d.]+)\s+([-\d.]+)\)", text)
    if not sizes:
        raise ReadError("找不到 (size X Y)")
    sx, sy = float(sizes[0][0]), float(sizes[0][1])
    return sx if axis == "x" else sy


def read_kicad_mod_drill(text: str) -> float:
    m = re.search(r"\(drill\s+([-\d.]+)\)", text)
    if not m:
        raise ReadError("找不到 (drill N)")
    return float(m.group(1))


def read_kicad_mod_span_y(text: str) -> float:
    ys = []
    for blk in _kicad_pad_blocks(text):
        for m in _PAD_AT.finditer(blk):
            ys.append(float(m.group(2)))
    if len(ys) < 2:
        raise ReadError("pad 少于 2 个, 算不出跨距")
    return round(max(ys) - min(ys), 9)


def read_md_range_width(text: str, line_pattern: str, range_pattern: str) -> float:
    """在【所有】匹配行里取区间宽度; 若各行宽度不一致 ⇒ 读点歧义 ⇒ 报错 (宁可红, 不许静默取错)。"""
    lp = re.compile(line_pattern)
    rp = re.compile(range_pattern)
    widths = []
    for line in text.splitlines():
        if not lp.search(line):
            continue
        m = rp.search(line)
        if not m:
            continue
        widths.append((round(abs(float(m.group(2)) - float(m.group(1))), 9), line.strip()[:120]))
    if not widths:
        raise ReadError("没找到匹配行 %r + 区间 %r" % (line_pattern, range_pattern))
    vals = sorted(set(w for w, _ in widths))
    if len(vals) > 1:
        raise ReadError("读点歧义: %r 命中多个不同宽度 %r" % (line_pattern, vals))
    return vals[0]


def read_md_first_number(text: str, pattern: str) -> float:
    m = re.search(pattern, text)
    if not m:
        raise ReadError("没找到 %r" % pattern)
    g = m.groups()
    if g:
        return float(g[0])
    return float(m.group(0))


def read_py_dict_value(text: str, var: str, key: str) -> float:
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == var and isinstance(node.value, ast.Dict):
                    for k, v in zip(node.value.keys, node.value.values):
                        if isinstance(k, ast.Constant) and k.value == key and _is_num(v):
                            return _f(v.value)
    raise ReadError("找不到 %s[%r]" % (var, key))


def read_py_crit(text: str) -> float:
    """CRIT = 2 * TOL["fdm_part"] ⇒ 按式实算 (不许抄常量)。"""
    tol = read_py_dict_value(text, "TOL", "fdm_part")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "CRIT":
                    src = ast.dump(node.value)
                    if "fdm_part" in src:
                        return round(2 * tol, 9)
    raise ReadError("找不到 CRIT = 2 * TOL[\"fdm_part\"]")


def read_json_block_value(text: str, pointer: list) -> float:
    fences = re.findall(r"```json\s*(.*?)```", text, re.S)
    if not fences:
        raise ReadError("没有 ```json 机器块")
    data = json.loads(fences[-1])
    cur = data
    for p in pointer:
        if not isinstance(cur, dict) or p not in cur:
            raise ReadError("机器块里没有 %r" % (pointer,))
        cur = cur[p]
    if not isinstance(cur, (int, float)):
        raise ReadError("机器块里 %r 不是数" % (pointer,))
    return _f(cur)


READER_KINDS = {
    "kicad_mod_pad_x": lambda t, rp: read_kicad_mod_pad(t, "x"),
    "kicad_mod_pad_y": lambda t, rp: read_kicad_mod_pad(t, "y"),
    "kicad_mod_drill": lambda t, rp: read_kicad_mod_drill(t),
    "kicad_mod_span_y": lambda t, rp: read_kicad_mod_span_y(t),
    "md_range_width": lambda t, rp: read_md_range_width(t, rp["line_pattern"], rp["range_pattern"]),
    "md_first_number": lambda t, rp: read_md_first_number(t, rp["pattern"]),
    "py_dict_value": lambda t, rp: read_py_dict_value(t, rp["var"], rp["key"]),
    "py_crit": lambda t, rp: read_py_crit(t),
    "json_block_value": lambda t, rp: read_json_block_value(t, rp["pointer"]),
}


def read_premise(premise: dict, root: str = None) -> tuple:
    """⇒ (value, error) —— error 为 None 表示读成功。"""
    root = root or ROOT
    rp = premise.get("read_point") or {}
    kind = rp.get("kind")
    if kind == "missing":
        return None, "无真值读取点 (kind=missing)"
    fn = READER_KINDS.get(kind)
    if fn is None:
        return None, "未知读取器 kind=%r" % kind
    path = rp.get("path")
    full = path if os.path.isabs(path) else os.path.join(root, path)
    try:
        text = _read_text(full)
    except ReadError as e:
        return None, str(e)
    try:
        return float(fn(text, rp)), None
    except ReadError as e:
        return None, str(e)
    except Exception as e:  # noqa: BLE001
        return None, "读取异常 %s: %s" % (type(e).__name__, e)


# ══════════════════════════════════════════════════════════════════════
# 页面 / 基线工具
# ══════════════════════════════════════════════════════════════════════
def load_page_machine_block(page_path: str) -> dict:
    text = _read_text(page_path)
    fences = re.findall(r"```json\s*(.*?)```", text, re.S)
    if not fences:
        raise ReadError("页面里没有 ```json 机器块")
    return json.loads(fences[-1])


def md5_file(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def outbox_tree_digest(root: str = None) -> tuple:
    root = root or ROOT
    base = os.path.join(root, "state", "outbox")
    if not os.path.isdir(base):
        return None, 0
    files = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames.sort()
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root)
            files.append((rel, md5_file(full)))
    files.sort(key=lambda t: t[0])
    blob = "".join("%s  %s\n" % (m, rel) for rel, m in files)
    return hashlib.md5(blob.encode("utf-8")).hexdigest(), len(files)


def grep_count(rel_path: str, needle: str, root: str = None) -> int:
    root = root or ROOT
    p = os.path.join(root, rel_path)
    if not os.path.exists(p):
        return -1
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read().count(needle)


# ══════════════════════════════════════════════════════════════════════
# 判据 D1 ~ D6 (纯函数 · 便于 selftest 注入)
# ══════════════════════════════════════════════════════════════════════
def check_d1(premises: list, reader) -> list:
    """D1: 每个前提量的「当前值 + 真值读取点」必须能被脚本重新读出来。"""
    reds = []
    for p in premises:
        pid = p.get("id")
        reg = p.get("current_value")
        val, err = reader(p)
        if err:
            reds.append("D1 %s 读不出真值: %s" % (pid, err))
            continue
        if not isinstance(reg, (int, float)):
            reds.append("D1 %s 页面登记的 current_value 不是数: %r" % (pid, reg))
            continue
        if abs(float(val) - float(reg)) > 1e-9:
            reds.append("D1 %s 页面登记 %r ≠ 现读 %r" % (pid, reg, val))
    return reds


def check_d2(premises: list, edges: list) -> list:
    """D2: 每个前提量至少挂到 1 条依赖边。"""
    used = set()
    for e in edges:
        for pid in e.get("premises", []):
            used.add(pid)
    return ["D2 前提量 %s 在依赖图里没有挂到任何一条边 (孤立前提量)" % p.get("id")
            for p in premises if p.get("id") not in used]


def check_d3(scanned: list, registered: list, edges: list) -> list:
    """D3: 实扫到的写死常量点必须逐条登记, 且每条都被依赖图引用。"""
    reds = []
    sset = {(c["gate"], int(c["line"]), round(float(c["value"]), 9)) for c in scanned}
    rset = {(c["gate"], int(c["line"]), round(float(c["value"]), 9)) for c in registered}
    for miss in sorted(sset - rset):
        reds.append("D3 实扫到但没登记的写死常量点: %s L%d = %r" % miss)
    for extra in sorted(rset - sset):
        reds.append("D3 登记了但实扫不到的写死常量点: %s L%d = %r" % extra)
    referenced = set()
    for e in edges:
        for hid in e.get("hardcoded_constant_ids", []):
            referenced.add(hid)
    rids = {c.get("id") for c in registered}
    for hid in sorted(rids - referenced):
        reds.append("D3 写死常量点 %s 登记了但没出现在依赖图的「写死常量点」栏里" % hid)
    return reds


def check_d4(matrix: list, edges: list) -> list:
    """D4: 矩阵里每一格都必须能在依赖图里找到对应边。

    「对应边」 = 该格的目标出现在某条边里, 且那条边与该矩阵行【至少共享一个前提量】
    (允许间接路径: 例如 PQ09 清空区宽 → 罩住余量 → 某闸)。
    """
    reds = []
    for row in matrix:
        rid = row.get("id")
        pset = set(row.get("premise_change", {}).get("premises", []))
        for cell in row.get("cells", []):
            kind = cell.get("kind")
            target = cell.get("target")
            ok = False
            for e in edges:
                if not (pset & set(e.get("premises", []))):
                    continue
                if kind == "number" and target in e.get("numbers", []):
                    ok = True
                elif kind == "gate" and target in e.get("gates", []):
                    ok = True
                elif kind == "conclusion" and target in e.get("conclusions", []):
                    ok = True
                if ok:
                    break
            if not ok:
                reds.append("D4 矩阵 %s 的格子 (%s/%s) 在依赖图里找不到对应边" % (rid, kind, target))
    return reds


def check_d5(actual: dict, baseline: dict) -> list:
    """D5: 板 / 网表 / 脚表 / BOM md5 与基线逐字相同。"""
    reds = []
    for k, want in (baseline or {}).items():
        got = actual.get(k)
        if got is None:
            reds.append("D5 %s 实读不到 (文件缺失?)" % k)
        elif got != want:
            reds.append("D5 %s md5 %r ≠ 基线 %r" % (k, got, want))
    return reds


def check_d6(hook_count: int, outbox_now: str, outbox_base: str,
             premises: list, evidence_levels: list) -> list:
    """D6: 零挂链 + 零外发自证 + 证据分级。"""
    reds = []
    if hook_count != 0:
        reds.append("D6 零挂链自证失败: state/gate_check.py 里有 %d 处本闸名 (必须 0)" % hook_count)
    if outbox_now != outbox_base:
        reds.append("D6 零外发自证失败: state/outbox/ 树摘要 %r ≠ 基线 %r" % (outbox_now, outbox_base))
    for p in premises:
        ev = p.get("evidence")
        if ev not in evidence_levels:
            reds.append("D6 %s 证据等级 %r 不在白名单 %r 里" % (p.get("id"), ev, evidence_levels))
    return reds


# ══════════════════════════════════════════════════════════════════════
# 真跑
# ══════════════════════════════════════════════════════════════════════
def run_real(root: str = None) -> int:
    root = root or ROOT
    page = os.path.join(root, PAGE_REL)
    out = []
    out.append("=" * 78)
    out.append("ISS-407 · MECH 判决链前提依赖 + 作废传播 · 机器闸")
    out.append("真相页: %s" % PAGE_REL)
    out.append("=" * 78)
    reds = []
    try:
        blk = load_page_machine_block(page)
    except Exception as e:  # noqa: BLE001
        print("[FAIL] D0 机器块解析失败: %s" % e)
        print("\nRESULT: FAIL (机器块都读不出来)")
        return 1

    premises = blk.get("premise_quantities", [])
    edges = blk.get("dependency_graph", [])
    matrix = blk.get("invalidation_matrix", [])
    registered = blk.get("hardcoded_constants", [])

    # ---- D1 ----
    d1 = check_d1(premises, lambda p: read_premise(p, root=root))
    out.append("\n--- D1 前提量清单可机器重建 ---")
    for p in premises:
        val, err = read_premise(p, root=root)
        mark = "OK " if err is None else "RED"
        out.append("  [%s] %-6s %-28s 现读=%-12s 登记=%-12s %s"
                   % (mark, p.get("id"), (p.get("name") or "")[:28],
                      ("%.4f" % val) if val is not None else "—",
                      p.get("current_value"), err or ""))
    out.append("  ⇒ D1 红项 %d 条" % len(d1))
    reds += d1

    # ---- D2 ----
    d2 = check_d2(premises, edges)
    out.append("\n--- D2 依赖图自洽 ---")
    out.append("  前提量 %d 个 · 依赖边 %d 条" % (len(premises), len(edges)))
    for r in d2:
        out.append("  [RED] %s" % r)
    out.append("  ⇒ D2 红项 %d 条" % len(d2))
    reds += d2

    # ---- D3 ----
    scanned = scan_all_constants(root=root)
    d3 = check_d3(scanned, registered, edges)
    out.append("\n--- D3 写死常量点必须进依赖图 (规则 HC-SCAN-v2 · AST 实扫) ---")
    out.append("  扫描闸 %d 道 · 实扫到写死常量点 %d 个 · 页面登记 %d 个"
               % (len(VERDICT_CHAIN_GATES), len(scanned), len(registered)))
    for r in d3:
        out.append("  [RED] %s" % r)
    out.append("  ⇒ D3 红项 %d 条" % len(d3))
    reds += d3

    # ---- D4 ----
    d4 = check_d4(matrix, edges)
    out.append("\n--- D4 作废传播矩阵与依赖图一致 ---")
    out.append("  矩阵 %d 行 · 依赖边 %d 条" % (len(matrix), len(edges)))
    for r in d4:
        out.append("  [RED] %s" % r)
    out.append("  ⇒ D4 红项 %d 条" % len(d4))
    reds += d4

    # ---- D5 ----
    bl = blk.get("table_baselines", {})
    actual = {}
    for k, rel in (blk.get("baseline_files", {}) or {}).items():
        p = os.path.join(root, rel)
        actual[k] = md5_file(p) if os.path.exists(p) else None
    d5 = check_d5(actual, bl)
    out.append("\n--- D5 板三证不动 ---")
    for k in sorted(set(list(bl.keys()) + list(actual.keys()))):
        out.append("  %-10s 实读=%-34s 基线=%s"
                   % (k, actual.get(k), bl.get(k, "(无)")))
    for r in d5:
        out.append("  [RED] %s" % r)
    out.append("  ⇒ D5 红项 %d 条" % len(d5))
    reds += d5

    # ---- D6 ----
    hook = grep_count("state/gate_check.py", "check_verdict_premise_dependency", root=root)
    now, nfiles = outbox_tree_digest(root)
    ob = blk.get("outbox_baseline", {})
    d6 = check_d6(hook, now, ob.get("tree_md5"), premises, blk.get("evidence_levels", EVIDENCE_LEVELS))
    out.append("\n--- D6 零挂链 + 零外发 + 证据分级 ---")
    out.append("  零挂链: state/gate_check.py 里本闸名出现 %d 次 (必须 0)" % hook)
    out.append("  零外发: state/outbox/ %d 个文件 · 树摘要 %s (基线 %s)"
               % (nfiles, now, ob.get("tree_md5")))
    for r in d6:
        out.append("  [RED] %s" % r)
    out.append("  ⇒ D6 红项 %d 条" % len(d6))
    reds += d6

    out.append("\n" + "=" * 78)
    if reds:
        out.append("RESULT: FAIL (%d 条判据不通过)" % len(reds))
        out.append("★红的是【现状】, 不是闸故障: 前提量 PQ13/PQ14/PQ15/PQ16 没有真值读取点")
        out.append("  (座体外形三量 + 板厚至今 [0数据] ⇒ 「前提改了没人知道」就是现状本身)")
        out.append("=" * 78)
        print("\n".join(out))
        return 1
    out.append("RESULT: PASS (6 条判据全绿)")
    out.append("=" * 78)
    print("\n".join(out))
    return 0


# ══════════════════════════════════════════════════════════════════════
# selftest (正向 ≥1 + 反向 ≥8)
# ══════════════════════════════════════════════════════════════════════
def _fake_world():
    """构造一个【全绿】的合成世界 (只给判据函数用, 不碰真仓库)。"""
    premises = [
        {"id": "PQ01", "current_value": 1.0, "evidence": "实测"},
        {"id": "PQ02", "current_value": 1.0, "evidence": "实测"},
        {"id": "PQ03", "current_value": 0.65, "evidence": "实测"},
    ]
    edges = [
        {"id": "E01", "premises": ["PQ01", "PQ02", "PQ03"], "numbers": ["n1"],
         "gates": ["MECH/g.py"], "conclusions": ["c1"], "hardcoded_constant_ids": ["HC-001"]},
    ]
    scanned = [{"gate": "MECH/g.py", "line": 10, "value": 4.81}]
    registered = [{"id": "HC-001", "gate": "MECH/g.py", "line": 10, "value": 4.81}]
    matrix = [
        {"id": "M1", "premise_change": {"premises": ["PQ01"]},
         "cells": [{"kind": "number", "target": "n1", "status": "invalid"}]},
    ]
    actual = {"board": "aaa", "netlist": "bbb"}
    baseline = {"board": "aaa", "netlist": "bbb"}
    return premises, edges, scanned, registered, matrix, actual, baseline


def run_selftest() -> int:
    p, e, sc, rg, mx, ac, bl = _fake_world()
    passed = []
    failed = []

    def ok(name, cond):
        (passed if cond else failed).append(name)

    # ---- 正向 ----
    good_reader = lambda pr: (float(pr["current_value"]), None)
    ok("POS-01 合成世界全绿 (D1~D4)",
       check_d1(p, good_reader) == [] and check_d2(p, e) == []
       and check_d3(sc, rg, e) == [] and check_d4(mx, e) == [])
    ok("POS-02 D5/D6 全绿",
       check_d5(ac, bl) == [] and check_d6(0, "x", "x", p, EVIDENCE_LEVELS) == [])

    # ---- 反向 ----
    def reader_raises(pr):
        return None, "无真值读取点"

    def reader_wrong(pr):
        return 99.0, None

    ok("NEG-01 D1 读不出来 ⇒ 红", len(check_d1(p, reader_raises)) == len(p))
    ok("NEG-02 D1 登记值≠现读 ⇒ 红", len(check_d1(p, reader_wrong)) == len(p))
    ok("NEG-03 D2 孤立前提量 ⇒ 红", len(check_d2(p + [{"id": "PQ99", "current_value": 1.0}], e)) == 1)
    ok("NEG-04 D3 实扫到但没登记 ⇒ 红",
       len(check_d3(sc + [{"gate": "MECH/g.py", "line": 11, "value": 2.27}], rg, e)) == 1)
    ok("NEG-05 D3 登记了但没人引用 ⇒ 红",
       len(check_d3(sc, rg, [{**e[0], "hardcoded_constant_ids": []}])) == 1)
    ok("NEG-06 D4 矩阵多一格 ⇒ 红",
       len(check_d4(mx + [{"id": "M2", "premise_change": {"premises": ["PQ01"]},
                           "cells": [{"kind": "number", "target": "nX", "status": "invalid"}]}], e)) == 1)
    ok("NEG-07 D5 md5 不符 ⇒ 红", len(check_d5({"board": "zzz", "netlist": "bbb"}, bl)) == 1)
    ok("NEG-12 D5 实读缺件 ⇒ 红", len(check_d5({"board": "aaa"}, bl)) == 1)
    ok("NEG-08 D6 挂链数≠0 ⇒ 红", len(check_d6(1, "x", "x", p, EVIDENCE_LEVELS)) == 1)
    ok("NEG-09 D6 outbox 动了 ⇒ 红", len(check_d6(0, "y", "x", p, EVIDENCE_LEVELS)) == 1)
    ok("NEG-10 D6 证据等级不在白名单 ⇒ 红",
       len(check_d6(0, "x", "x", [{"id": "P", "current_value": 1.0, "evidence": "官方"}], EVIDENCE_LEVELS)) == 1)
    ok("NEG-11 D3 登记了但实扫不到 ⇒ 红",
       len(check_d3([], rg, e)) == 1)

    print("=" * 78)
    print("ISS-407 · check_verdict_premise_dependency · selftest")
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
    return run_real(root=args.root)


if __name__ == "__main__":
    sys.exit(main())
