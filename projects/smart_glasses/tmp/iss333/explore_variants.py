#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-333 · 探索脚本 3: 对比几种 C15/C16 口径的基线结果 (★只读★)"""
from __future__ import annotations
import glob, importlib.util, os, re, sys, tokenize

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("sw_gate", os.path.join(ROOT, "SW", "tools", "check_sw_ref_reachability.py"))
sw = importlib.util.module_from_spec(spec); sys.modules["sw_gate"] = sw; spec.loader.exec_module(sw)
PREFIX_RE = re.compile(r"\b(?:" + "|".join(re.escape(p) for p in sw.TOKEN_PREFIXES) + r")[A-Za-z0-9_]*")
BARE_RE = re.compile(r"\b(?:Q|X)\d+\b")
SELF = "MECH/ONETRIP_S1_RENAME_SAFETY_AUDIT.md"

md = sorted(glob.glob(os.path.join(ROOT, "MECH", "**", "*.md"), recursive=True))
py = sorted(glob.glob(os.path.join(ROOT, "MECH", "**", "*.py"), recursive=True))
py_names = set()
for p in py:
    with open(p, "rb") as fh:
        for tok in tokenize.tokenize(fh.readline):
            if tok.type == tokenize.NAME:
                py_names.add(tok.string)

def collect(files, bare):
    occ = {}
    for path in files:
        rel = os.path.relpath(path, ROOT)
        with open(path, encoding="utf-8", errors="replace") as fh:
            for lineno, line in enumerate(fh, 1):
                for m in PREFIX_RE.finditer(line):
                    occ.setdefault(m.group(0), []).append((rel, lineno, line.rstrip("\n")))
                if bare:
                    for m in BARE_RE.finditer(line):
                        occ.setdefault(m.group(0), []).append((rel, lineno, line.rstrip("\n")))
    return occ

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
# MECH 注册表 = MECH 域引用到的 ∩ live (建闸日冻结) + 裸编号 live
occ_all = collect(md + py, bare=True)
occ_pre = collect(md + py, bare=False)
mech_registry = {t for t in occ_pre if t in live} | {t for t in occ_all if BARE_RE.fullmatch(t) and t in live}
print(f"MECH 注册表候选 = {len(mech_registry)} 条 (含裸编号 live: {sorted(t for t in mech_registry if BARE_RE.fullmatch(t))})")

idx = {"root": ROOT, "board_refs": board_refs, "netlist_refs": net_refs, "live_refs": live,
       "net_names": sw.read_net_names(ROOT), "doc_files": doc_files, "anchors": anchors,
       "env_keys": env_keys, "registry": set(sw.DESIGNATOR_REGISTRY)}

def rows_for(occ, registry):
    idx2 = dict(idx); idx2["registry"] = registry
    out = []
    for tok, o in sorted(occ.items()):
        cls, rule, why = sw.classify(tok, idx2, o)
        files = {x[0] for x in o}
        out.append(dict(token=tok, cls=cls, rule=rule, py_only=all(f.endswith(".py") for f in files),
                        md_hit=any(f.endswith(".md") for f in files), ident=tok in py_names,
                        self_hit=SELF in files, files=sorted(files)))
    return out

print("\n########## V1 · ISS-326 口径复现 (coarse py_only + self-doc 剔除) ##########")
r1 = rows_for(occ_pre, sw.DESIGNATOR_REGISTRY)
c14_1 = [r for r in r1 if r["cls"] == "DESIGNATOR_MISSING"]
print(f"原始 C14 = {len(c14_1)}   py_only = {sum(r['py_only'] for r in c14_1)}   md_hit = {sum(r['md_hit'] for r in c14_1)}   self = {sum(r['self_hit'] for r in c14_1)}")
v1 = [r for r in c14_1 if not r["self_hit"] and not r["py_only"]]
print(f"★ V1 复现值 (剔 self + 剔 py_only) = {len(v1)}")
for r in v1: print(f"     {r['token']:28s} {r['files'][:2]}")

print("\n########## V2 · 精修口径 (C15=Python标识符 / C16=live∪registry 限定) ##########")
occ2 = {t: o for t, o in occ_all.items() if not BARE_RE.fullmatch(t) or t in live or t in mech_registry}
r2 = rows_for(occ2, mech_registry)
c14_2 = []
for r in r2:
    if r["cls"] != "DESIGNATOR_MISSING":
        continue
    if r["ident"]:
        continue          # ★C15: 是 Python 标识符 ⇒ 代码常量/变量名 ⇒ DOC_INTERNAL
    c14_2.append(r)
print(f"★ V2 最终 C14 = {len(c14_2)}")
self2 = [r for r in c14_2 if r["self_hit"]]
non2 = [r for r in c14_2 if not r["self_hit"]]
print(f"   其中 self-doc 内 = {len(self2)}   self-doc 外 = {len(non2)}")
for r in c14_2: print(f"     {r['token']:28s} self={int(r['self_hit'])} py_only={int(r['py_only'])} md={int(r['md_hit'])} {r['files'][:2]}")

print("\n########## V3 · 精修口径 + 显式剔 self-doc (== ISS-326 口径在精修规则下的投影) ##########")
v3 = [r for r in c14_2 if not r["self_hit"]]
print(f"★ V3 = {len(v3)}")

print("\n########## V4 · coarse py_only (ISS-326 的 C15 原样) + C16 限定 ##########")
occ4 = {t: o for t, o in occ_all.items() if not BARE_RE.fullmatch(t) or t in live or t in mech_registry}
r4 = rows_for(occ4, mech_registry)
c14_4 = [r for r in r4 if r["cls"] == "DESIGNATOR_MISSING" and not r["py_only"]]
print(f"★ V4 = {len(c14_4)} (self 内 {sum(r['self_hit'] for r in c14_4)} / 外 {sum(not r['self_hit'] for r in c14_4)})")
for r in c14_4: print(f"     {r['token']:28s} self={int(r['self_hit'])} {r['files'][:2]}")
