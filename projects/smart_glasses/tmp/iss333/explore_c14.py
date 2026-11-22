#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-333 · 探索脚本: 把 ISS-326 的 60 条 C14 逐条打出来, 为 C15 规则定型 (★只读·不写任何真件★)"""
from __future__ import annotations
import glob, importlib.util, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SW_GATE = os.path.join(ROOT, "SW", "tools", "check_sw_ref_reachability.py")
spec = importlib.util.spec_from_file_location("sw_gate", SW_GATE)
sw = importlib.util.module_from_spec(spec); sys.modules["sw_gate"] = sw; spec.loader.exec_module(sw)

TOKEN_RE = re.compile(r"\b(?:" + "|".join(re.escape(p) for p in sw.TOKEN_PREFIXES) + r")[A-Za-z0-9_]*")

md = sorted(glob.glob(os.path.join(ROOT, "MECH", "**", "*.md"), recursive=True))
py = sorted(glob.glob(os.path.join(ROOT, "MECH", "**", "*.py"), recursive=True))
occ = {}
for path in md + py:
    rel = os.path.relpath(path, ROOT)
    with open(path, encoding="utf-8", errors="replace") as fh:
        for lineno, line in enumerate(fh, 1):
            for m in TOKEN_RE.finditer(line):
                occ.setdefault(m.group(0), []).append((rel, lineno, line.rstrip("\n")))

doc_files, anchors, env_keys = set(), set(), set()
for p in md:
    rel = os.path.relpath(p, ROOT)
    doc_files.add(os.path.splitext(rel)[0])
    doc_files.add(os.path.splitext(os.path.basename(rel))[0])
    txt = open(p, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r"#\s*(?:BEGIN|END)\s+([A-Za-z0-9_]+)", txt):
        anchors.add(m.group(1))
env_pat = re.compile(r"os\.environ(?:\.get\(|\.setdefault\(|\.pop\(|\[)\s*[\"']([A-Za-z0-9_]+)[\"']")
for p in py:
    txt = open(p, encoding="utf-8", errors="replace").read()
    for m in env_pat.finditer(txt):
        env_keys.add(m.group(1))

board_refs = sw.read_board_refs(os.path.join(ROOT, sw.BOARD_REL))
net_refs = sw.read_netlist_refs({"root": ROOT})
net_names = sw.read_net_names(ROOT)
live = set(board_refs) | set(net_refs)
idx = {"root": ROOT, "board_refs": board_refs, "netlist_refs": net_refs, "live_refs": live,
       "net_names": net_names, "doc_files": doc_files, "anchors": anchors, "env_keys": env_keys,
       "registry": set(sw.DESIGNATOR_REGISTRY)}

rows = []
for tok, o in sorted(occ.items()):
    cls, rule, why = sw.classify(tok, idx, o)
    rows.append({"token": tok, "cls": cls, "rule": rule, "n": len(o),
                 "files": sorted({x[0] for x in o}), "occ": o})

missing = [r for r in rows if r["cls"] == "DESIGNATOR_MISSING"]
print(f"扫描面: md={len(md)} py={len(py)} total={len(md)+len(py)}  token={len(rows)}")
print(f"C14 total = {len(missing)}")
SELF = "MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md"
for r in missing:
    fl = r["files"]
    py_only = all(f.endswith(".py") for f in fl)
    md_hit = any(f.endswith(".md") for f in fl)
    self_hit = SELF in fl
    print(f"  {r['token']:44s} n={r['n']:3d} py_only={int(py_only)} md_hit={int(md_hit)} self={int(self_hit)}  {fl[:3]}")
