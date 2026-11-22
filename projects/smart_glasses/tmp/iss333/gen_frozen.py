#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-333 · 冻结数据生成器: 算 MECH 注册表 / 基线 / 非位号注册表 / 盘面指纹 (★只读·不写真件★)"""
from __future__ import annotations
import glob, hashlib, importlib.util, json, os, re, sys, tokenize

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
for p in py:
    with open(p, "rb") as fh:
        for t in tokenize.tokenize(fh.readline):
            if t.type == tokenize.NAME:
                py_names.add(t.string)

def collect(files, bare):
    occ = {}
    for path in files:
        rel = os.path.relpath(path, ROOT)
        with open(path, encoding="utf-8", errors="replace") as fh:
            for ln, line in enumerate(fh, 1):
                for m in PREFIX_RE.finditer(line):
                    occ.setdefault(m.group(0), []).append((rel, ln, line.rstrip("\n")))
                if bare:
                    for m in BARE_RE.finditer(line):
                        occ.setdefault(m.group(0), []).append((rel, ln, line.rstrip("\n")))
    return occ

occ = collect(md + py, bare=True)
board_refs = sw.read_board_refs(os.path.join(ROOT, sw.BOARD_REL))
net_refs = sw.read_netlist_refs({"root": ROOT})
live = set(board_refs) | set(net_refs)
registry = sorted(t for t in occ if t in live)
print(f"# 扫描面 md={len(md)} py={len(py)} (闸自身已排除)")
print(f"# live 位号 = {len(live)}  ·  MECH 引用到的 live = {len(registry)}")
print("MECH_DESIGNATOR_REGISTRY = (")
for t in registry: print(f'    "{t}",')
print(")")
fp = hashlib.sha256(("\n".join(sorted(live))).encode()).hexdigest()
print(f"\n# REGISTRY_BOARD_FINGERPRINT = {fp}")
print(f"# 盘面 live 位号集合 sha256 · 建闸日 2026-11-18 实测")
