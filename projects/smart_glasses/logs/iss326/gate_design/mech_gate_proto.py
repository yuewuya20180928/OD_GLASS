#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-326 · ★MECH 侧位号可达性闸 · 设计稿级原型 (★不是闸, 不挂进 state/gate_check.py★)★

★目的: 只为「取 MECH 侧【建闸日基线】」这一个读数 —— ★不许抄 SW 侧的 3★ ★
★口径零漂移做法: ★只读 import SW/tools/check_sw_ref_reachability.py, 直接复用它的
   TOKEN_PREFIXES / read_board_refs / read_netlist_refs / read_net_names / classify ★
   ⇒ MECH 版与 SW 版【同一套判据口径】, 只换【扫描面】与【注册表冻结范围】 ★
★只写 logs/iss326/gate_design/ ★零写板 · 零落表 · 零改闸 (MECH/*.py 一个字不动) ★
"""
from __future__ import annotations

import glob
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT_DIR = os.path.join(ROOT, "logs", "iss326", "gate_design")
SW_GATE = os.path.join(ROOT, "SW", "tools", "check_sw_ref_reachability.py")

# ---------------------------------------------------------------- 只读 import SW 侧那道闸
spec = importlib.util.spec_from_file_location("sw_gate", SW_GATE)
sw = importlib.util.module_from_spec(spec)
sys.modules["sw_gate"] = sw
spec.loader.exec_module(sw)

TOKEN_RE = re.compile(r"\b(?:" + "|".join(re.escape(p) for p in sw.TOKEN_PREFIXES) + r")[A-Za-z0-9_]*")

# ---------------------------------------------------------------- 扫描面: MECH 递归 (py + md)
def mech_files(root: str):
    md = sorted(glob.glob(os.path.join(root, "MECH", "**", "*.md"), recursive=True))
    py = sorted(glob.glob(os.path.join(root, "MECH", "**", "*.py"), recursive=True))
    return md, py

def collect(root: str):
    md, py = mech_files(root)
    if not md and not py:
        raise SystemExit("[mech-gate-proto] MECH 扫描面为空")
    occ = {}
    for path in md + py:
        rel = os.path.relpath(path, root)
        with open(path, encoding="utf-8", errors="replace") as fh:
            for lineno, line in enumerate(fh, 1):
                for m in TOKEN_RE.finditer(line):
                    occ.setdefault(m.group(0), []).append((rel, lineno, line.rstrip("\n")))
    return occ, md, py

def build_mech_aux_index(root: str):
    """★MECH 版辅助索引 (C4/C5/C6): 递归 MECH/**.md + 递归 MECH/**.py ★"""
    md, py = mech_files(root)
    doc_files, anchors, env_keys = set(), set(), set()
    for p in md:
        rel = os.path.relpath(p, root)
        noext = os.path.splitext(rel)[0]
        doc_files.add(noext)
        doc_files.add(os.path.splitext(os.path.basename(rel))[0])
        txt = open(p, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"#\s*(?:BEGIN|END)\s+([A-Za-z0-9_]+)", txt):
            anchors.add(m.group(1))
    env_pat = re.compile(r"os\.environ(?:\.get\(|\.setdefault\(|\.pop\(|\[)\s*[\"']([A-Za-z0-9_]+)[\"']")
    for p in py:
        txt = open(p, encoding="utf-8", errors="replace").read()
        for m in env_pat.finditer(txt):
            env_keys.add(m.group(1))
    return doc_files, anchors, env_keys

def main() -> int:
    root = ROOT
    occ, md, py = collect(root)
    doc_files, anchors, env_keys = build_mech_aux_index(root)

    # ---- live 解析源 (与 SW 侧同源: 板文件 + 3 件网表) ----
    board_path = os.path.join(root, sw.BOARD_REL)
    board_refs = sw.read_board_refs(board_path) if os.path.isfile(board_path) else set()
    net_names = sw.read_net_names(root)
    net_refs = sw.read_netlist_refs({"root": root})
    live = set(board_refs) | set(net_refs)

    idx = {
        "root": root,
        "board_refs": board_refs,
        "netlist_refs": net_refs,
        "live_refs": live,
        "live": live,
        "net_names": net_names,
        "doc_files": doc_files,
        "anchors": anchors,
        "env_keys": env_keys,
        "registry": set(sw.DESIGNATOR_REGISTRY),
        "occ": occ,
    }

    rows = []
    for tok, o in sorted(occ.items()):
        cls, rule, why = sw.classify(tok, idx, o)
        rows.append({"token": tok, "class": cls, "rule": rule, "why": why,
                     "n": len(o), "files": sorted({x[0] for x in o})})

    missing = [r for r in rows if r["class"] == "DESIGNATOR_MISSING"]
    drift = [r for r in rows if r["class"] == "DESIGNATOR_DRIFT"]
    ok = [r for r in rows if r["class"] == "DESIGNATOR_OK"]
    rule_hist = {}
    for r in rows:
        rule_hist[r["rule"]] = rule_hist.get(r["rule"], 0) + 1

    # ---- C14 基线拆分: 只在 .py 里 (判据脚本的常量/变量名 ⇒ 需 C15 命名空间规则)
    #                   vs 也出现在 .md 里 (文档级引用 ⇒ SW 侧同型真隐患) ----
    SELF_DOC = "MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md"
    def split(tok):
        fl = {x[0] for x in occ[tok]}
        py_only = all(f.endswith(".py") for f in fl)
        md_hit = any(f.endswith(".md") for f in fl)
        return py_only, md_hit, fl
    miss_detail = []
    for r in missing:
        py_only, md_hit, fl = split(r["token"])
        miss_detail.append({
            "token": r["token"], "n": r["n"], "py_only": py_only, "md_hit": md_hit,
            "in_self_doc": SELF_DOC in fl,
            "files": sorted(fl)[:4],
        })
    py_only_miss = [m for m in miss_detail if m["py_only"]]
    md_miss = [m for m in miss_detail if m["md_hit"]]
    self_miss = [m for m in miss_detail if m["in_self_doc"]]
    baseline_excl_self = [m for m in miss_detail if not m["in_self_doc"]]

    # ---- 改名真集在 MECH 域的引用面 (预测改名后的 C2 漂移规模) ----
    uni = json.load(open(os.path.join(root, "logs", "iss326", "mech_ref_universe.json"),
                         encoding="utf-8"))["universe"]
    move_refs = {k for k, v in uni.items() if v.get("move") == "改名"}
    keep_refs = {k for k, v in uni.items() if v.get("move") != "改名"}
    referenced = set(occ.keys())
    move_ref = move_refs & referenced
    keep_ref = keep_refs & referenced
    move_ref_live = sorted(t for t in move_ref if t in live)
    move_ref_notlive = sorted(t for t in move_ref if t not in live)

    out = {
        "scan_surface": {
            "md_files": len(md), "py_files": len(py),
            "total_files": len(md) + len(py),
            "glob": "MECH/**/*.md (递归) + MECH/**/*.py (递归)",
        },
        "tokens_unique": len(rows),
        "live_refs": len(live),
        "classification": {
            "DESIGNATOR_OK (C1)": len(ok),
            "DESIGNATOR_DRIFT (C2)": len(drift),
            "DESIGNATOR_MISSING (C14)": len(missing),
            "other_rules": len(rows) - len(ok) - len(drift) - len(missing),
        },
        "baseline_designator_missing": len(missing),
        "baseline_breakdown": {
            "C14_total": len(missing),
            "C14_py_only (判据脚本里的常量/变量名 ⇒ 需 C15 命名空间规则摘出)": len(py_only_miss),
            "C14_md_hit (文档级引用 ⇒ SW 侧同型真隐患)": len(md_miss),
            "C14_from_本单自己产物 (ONETRIP_S1_RENAME_SAFETY_AUDIT.md)": len(self_miss),
            "C14_excluding_本单自己产物": len(baseline_excl_self),
            "C14_excluding_本单产物_and_py_only": len([m for m in baseline_excl_self if not m["py_only"]]),
        },
        "rule_histogram": rule_hist,
        "baseline_tokens": [r["token"] for r in missing],
        "baseline_detail": [{"token": r["token"], "n": r["n"], "files": r["files"][:4]} for r in missing],
        "baseline_detail_split": miss_detail,
        "rename_exposure": {
            "move_refs_total": len(move_refs),
            "move_refs_referenced_in_MECH": len(move_ref),
            "move_refs_referenced_and_live": len(move_ref_live),
            "move_refs_referenced_but_not_live": len(move_ref_notlive),
            "keep_refs_total": len(keep_refs),
            "keep_refs_referenced_in_MECH": len(keep_ref),
            "predicted_C2_drift_after_rename": len(move_ref_live),
        },
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "mech_gate_baseline.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT_DIR, "mech_gate_baseline_raw.txt"), "w", encoding="utf-8") as f:
        f.write(f"扫描面: {out['scan_surface']}\n")
        f.write(f"唯一 token 数: {len(rows)}\n")
        f.write(f"live 位号数: {len(live)}\n")
        f.write(f"分类: {out['classification']}\n")
        f.write(f"★MECH 侧建闸日基线 DESIGNATOR_MISSING = {len(missing)} 条 (★SW 侧是 3, 本单不抄★)\n")
        f.write(f"拆分: {out['baseline_breakdown']}\n")
        f.write(f"规则直方图: {rule_hist}\n")
        for r in missing:
            f.write(f"  - {r['token']}  (出现 {r['n']} 次, 文件 {r['files'][:3]})\n")
        f.write(f"改名暴露面: {out['rename_exposure']}\n")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
