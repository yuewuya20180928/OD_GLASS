#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-333 · 探索脚本 2: 验证 C15 (判据脚本代码标识符) + C16 (裸编号位号) 的口径, 并算最终基线 (★只读★)"""
from __future__ import annotations
import glob, importlib.util, io, os, re, sys, tokenize

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("sw_gate", os.path.join(ROOT, "SW", "tools", "check_sw_ref_reachability.py"))
sw = importlib.util.module_from_spec(spec); sys.modules["sw_gate"] = sw; spec.loader.exec_module(sw)

PREFIX_RE = re.compile(r"\b(?:" + "|".join(re.escape(p) for p in sw.TOKEN_PREFIXES) + r")[A-Za-z0-9_]*")
BARE_RE = re.compile(r"\b(?:Q|X)\d+\b")

md = sorted(glob.glob(os.path.join(ROOT, "MECH", "**", "*.md"), recursive=True))
py = sorted(glob.glob(os.path.join(ROOT, "MECH", "**", "*.py"), recursive=True))

# ---------- C15: 哪些 token 在 .py 里是【Python 标识符】(NAME token) ----------
py_names = set()
for p in py:
    try:
        with open(p, "rb") as fh:
            for tok in tokenize.tokenize(fh.readline):
                if tok.type == tokenize.NAME:
                    py_names.add(tok.string)
    except Exception as e:
        print("tokenize fail", p, e)

def collect(files):
    occ = {}
    for path in files:
        rel = os.path.relpath(path, ROOT)
        with open(path, encoding="utf-8", errors="replace") as fh:
            for lineno, line in enumerate(fh, 1):
                for m in PREFIX_RE.finditer(line):
                    occ.setdefault(m.group(0), []).append((rel, lineno, line.rstrip("\n")))
                for m in BARE_RE.finditer(line):
                    occ.setdefault(m.group(0), []).append((rel, lineno, line.rstrip("\n")))
    return occ

occ = collect(md + py)
print("universe(含裸编号) token =", len(occ))

doc_files, anchors, env_keys = set(), set(), set()
for p in md:
    rel = os.path.relpath(p, ROOT)
    doc_files.add(os.path.splitext(rel)[0]); doc_files.add(os.path.splitext(os.path.basename(rel))[0])
    txt = open(p, encoding="utf-8", errors="replace").read()
    for m in re.finditer(r"#\s*(?:BEGIN|END)\s+([A-Za-z0-9_]+)", txt): anchors.add(m.group(1))
env_pat = re.compile(r"os\.environ(?:\.get\(|\.setdefault\(|\.pop\(|\[)\s*[\"']([A-Za-z0-9_]+)[\"']")
for p in py:
    for m in env_pat.finditer(open(p, encoding="utf-8", errors="replace").read()): env_keys.add(m.group(1))

board_refs = sw.read_board_refs(os.path.join(ROOT, sw.BOARD_REL))
net_refs = sw.read_netlist_refs({"root": ROOT})
live = set(board_refs) | set(net_refs)
registry = set(sw.DESIGNATOR_REGISTRY)
idx = {"root": ROOT, "board_refs": board_refs, "netlist_refs": net_refs, "live_refs": live,
       "net_names": sw.read_net_names(ROOT), "doc_files": doc_files, "anchors": anchors,
       "env_keys": env_keys, "registry": registry}

rows = []
for tok, o in sorted(occ.items()):
    cls, rule, why = sw.classify(tok, idx, o)
    files = {x[0] for x in o}
    py_only = all(f.endswith(".py") for f in files)
    md_hit = any(f.endswith(".md") for f in files)
    ident = tok in py_names
    rows.append(dict(token=tok, cls=cls, rule=rule, n=len(o), py_only=py_only, md_hit=md_hit,
                     ident=ident, files=sorted(files)))

print("\n=== 裸编号 token 现状 ===")
for r in rows:
    if BARE_RE.fullmatch(r["token"]):
        print(f"  {r['token']:6s} cls={r['cls']:20s} live={r['token'] in live} reg={r['token'] in registry} md={r['md_hit']} py={r['py_only']} files={r['files'][:3]}")

# ---------- 应用 C15: py_only 且是 Python 标识符 ⇒ DOC_INTERNAL ----------
def final(r):
    if r["cls"] == "DESIGNATOR_MISSING" and r["py_only"] and r["ident"]:
        return "DOC_INTERNAL", "C15"
    return r["cls"], r["rule"]

print("\n=== 应用 C15 后 C14 剩余 ===")
c14 = []
for r in rows:
    c, rule = final(r)
    r["final_cls"], r["final_rule"] = c, rule
    if c == "DESIGNATOR_MISSING":
        c14.append(r)
print(f"C14 剩余 = {len(c14)}")
for r in c14:
    print(f"  {r['token']:28s} md={int(r['md_hit'])} py={int(r['py_only'])} self={int('MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md' in r['files'])} files={r['files'][:2]}")
