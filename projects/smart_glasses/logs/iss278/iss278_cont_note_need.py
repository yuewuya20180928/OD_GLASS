#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★在已合并的 need 里补一句「ISS-290 同族闸也该改链头口径」★ (★走 frag_write 原子写★)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "state"))
from frag_write import update_fragment
KEY = "iss278_mech_demo_struct_truth_selftest_regression"
ADD = ("\n\n★**【续做补一句 · 同族闸的同源脆点】**★ "
       "`MECH/check_onepass_struct_crosscheck.py` (★ISS-290 的闸, 已 verified, ★**不是本单的域, 本单一个字没改★**) "
       "它的 N6 对网表/脚表/BOM 用的是【硬写 md5 基线】而不是台账链头 ⇒ ★**现在绿, 但下一次【合法】授权落表 (链头前移) "
       "就会假红 ⇒ 会把「合法落表」误判成「真源被偷改」**★ ⇒ 本单的新闸 M5b 判的是【链头】⇒ 不会犯这个错 "
       "⇒ ★**请 main 决定要不要另派一个小活把 ISS-290 闸的 N6 也改成链头口径 (★本单不越界改★)**★")
def mutate(d):
    for n in d.get("needs_from") or []:
        if n.get("key") == KEY and "同族闸的同源脆点" not in (n.get("item") or ""):
            n["item"] = (n.get("item") or "") + ADD
update_fragment("mech-lead", mutate)
print("[note] ✅ need 已补同族闸提示")
