#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iss303 probe —— 只读探针: 用 MECH/check_board_frame_coords.py 的现成台账解析器
读出三个台账管理件 (网表 / 脚表 / BOM) 的【链头 / 链 / 登记 md5 全集】。
★只读 · 不改任何文件 · 用来定 N6 新判决源的合法集合形状★"""
import importlib.util
import os
import sys

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CFC = load("cfc_probe", os.path.join(PROJ, "MECH", "check_board_frame_coords.py"))

led_path = os.path.join(PROJ, CFC.LEDGER_CANON)
text = open(led_path, encoding="utf-8").read()
print(f"台账 = {CFC.LEDGER_CANON} · {len(text.splitlines())} 行")

for rel in CFC.PROTECTED_LEDGER:
    st = CFC.ledger_state(rel, text)
    cov = CFC.ledger_cover_rows(text, rel)
    reg = sorted({m for r in cov for m in r["md5s"]})
    print("=" * 100)
    print(f"★ {rel}")
    print(f"  链头 head   = {st['head']}  (产出单号 {st['head_iss']})")
    print(f"  链长        = {len(st['chain'])} · 记录条数 = {len(st['records'])}")
    print(f"  why         = {st['why']!r}")
    print(f"  覆盖行数    = {len(cov)}")
    print(f"  登记 md5 全集 ({len(reg)}) = {reg}")
    orphan = sorted({r['new'] for r in st['records']} - set(st['chain']))
    print(f"  不在链上的记录 new 值 = {orphan}")
    print(f"  chain = {st['chain']}")
