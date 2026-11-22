#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-333 · 冻结数据生成器 v2: 出【基线 / C17 / 已解掉】三段精确分区 (★只读★)"""
from __future__ import annotations
import glob, importlib.util, os, re, sys, tokenize

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("sw_gate", os.path.join(ROOT, "SW", "tools", "check_sw_ref_reachability.py"))
sw = importlib.util.module_from_spec(spec); sys.modules["sw_gate"] = sw; spec.loader.exec_module(sw)
PREFIX_RE = re.compile(r"\b(?:" + "|".join(re.escape(p) for p in sw.TOKEN_PREFIXES) + r")[A-Za-z0-9_]*")
BARE_RE = re.compile(r"\b(?:Q|X)\d+\b")
SELF_GATE_REL = "MECH/tools/check_mech_ref_reachability.py"

md = sorted(glob.glob(os.path.join(ROOT, "MECH", "**", "*.md"), recursive=True))
py = [p for p in sorted(glob.glob(os.path.join(ROOT, "MECH", "**", "*.py"), recursive=True))
      if os.path.relpath(p, ROOT) != SELF_GATE_REL]
py_names = set()
bad = []
for p in py:
    try:
        with open(p, "rb") as fh:
            for t in tokenize.tokenize(fh.readline):
                if t.type == tokenize.NAME:
                    py_names.add(t.string)
    except Exception as e:
        bad.append((os.path.relpath(p, ROOT), repr(e)[:80]))
print("tokenize 失败的 .py:", bad or "无")

occ = {}
for path in md + py:
    rel = os.path.relpath(path, ROOT)
    with open(path, encoding="utf-8", errors="replace") as fh:
        for ln, line in enumerate(fh, 1):
            for m in PREFIX_RE.finditer(line):
                occ.setdefault(m.group(0), []).append((rel, ln, line.rstrip("\n")))
            for m in BARE_RE.finditer(line):
                occ.setdefault(m.group(0), []).append((rel, ln, line.rstrip("\n")))

board_refs = sw.read_board_refs(os.path.join(ROOT, sw.BOARD_REL))
net_refs = sw.read_netlist_refs({"root": ROOT})
live = set(board_refs) | set(net_refs)
registry = sorted(t for t in occ if t in live)

doc_files, anchors, env_keys = set(), set(), set()
for p in md:
    rel = os.path.relpath(p, ROOT)
    doc_files.add(os.path.splitext(rel)[0]); doc_files.add(os.path.splitext(os.path.basename(rel))[0])
    txt = open(p, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r"#\s*(?:BEGIN|END)\s+([A-Za-z0-9_]+)", txt): anchors.add(m.group(1))
env_pat = re.compile(r"os\.environ(?:\.get\(|\.setdefault\(|\.pop\(|\[)\s*[\"']([A-Za-z0-9_]+)[\"']")
for p in py:
    for m in env_pat.finditer(open(p, encoding="utf-8", errors="replace").read()): env_keys.add(m.group(1))

idx = {"root": ROOT, "board_refs": board_refs, "netlist_refs": net_refs, "live_refs": live,
       "net_names": sw.read_net_names(ROOT), "doc_files": doc_files, "anchors": anchors,
       "env_keys": env_keys, "registry": set(registry)}

rows = []
for tok, o in sorted(occ.items()):
    cls, rule, why = sw.classify(tok, idx, o)
    files = {x[0] for x in o}
    rows.append(dict(tok=tok, cls=cls, rule=rule, n=len(o), py_only=all(f.endswith(".py") for f in files),
                     md=any(f.endswith(".md") for f in files), ident=tok in py_names,
                     bare=bool(BARE_RE.fullmatch(tok)), live=tok in live, reg=tok in registry,
                     files=sorted(files), occ=o))

c14 = [r for r in rows if r["cls"] == "DESIGNATOR_MISSING"]
c15 = [r for r in c14 if r["ident"]]
c16 = [r for r in c14 if r["bare"] and not r["live"] and not r["reg"]]
rest = [r for r in c14 if r not in c15 and r not in c16]
print(f"\nC14 原始 = {len(c14)}")
print(f"  C15 摘掉 (Python 标识符) = {len(c15)}: {sorted(r['tok'] for r in c15)}")
print(f"  C16 摘掉 (裸编号·非位号) = {len(c16)}: {sorted(r['tok'] for r in c16)}")
print(f"  剩余 (待定基线/C17) = {len(rest)}")
for r in rest:
    print(f"    {r['tok']:26s} n={r['n']:3d} py_only={int(r['py_only'])} md={int(r['md'])} "
          f"bare={int(r['bare'])} live={int(r['live'])} reg={int(r['reg'])} ident={int(r['ident'])} {r['files'][:2]}")
