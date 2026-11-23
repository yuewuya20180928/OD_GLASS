#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-358 cont1 · 反事实核对: 把我的 answers 改动【还原】后重算未闭合需求数
   ⇒ 证明 +6 是别的分片并发写进来的, 不是我改 key 造成的"""
import os, sys, json, yaml
from collections import defaultdict

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJ, "state"))
FRAGS = {"main": "pm.yaml", "hw-lead": "hw.yaml", "sw-lead": "sw.yaml", "mech-lead": "mech.yaml"}

def load(a):
    with open(os.path.join(PROJ, "state", "fragments", FRAGS[a]), "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def count(frags):
    from decision_truth import decision_keys
    dec = decision_keys(frags)
    abk = defaultdict(list)
    for aid, fr in frags.items():
        for a in (fr.get("answers") or []):
            if isinstance(a, dict) and a.get("key"):
                abk[a["key"]].append(aid)
    def ok(n):
        k, to = n.get("key"), n.get("to")
        if n.get("decision"):
            return True
        if k and k in dec:
            return True
        return bool(to) and to in abk.get(k, [])
    pend = ext = ans = tot = 0
    rows = []
    for aid, fr in frags.items():
        for n in (fr.get("needs_from") or []):
            if not isinstance(n, dict):
                continue
            tot += 1
            a = ok(n)
            if a:
                ans += 1
            else:
                if (n.get("waiting_on") or "agent") == "agent":
                    pend += 1
                else:
                    ext += 1
                rows.append((aid, n.get("key"), n.get("to")))
    return dict(total= tot, answered= ans, pending= pend, ext= ext, unclosed= rows)

frags_now = {a: load(a) for a in FRAGS}
# 反事实: 把我的 8 条改 key 还原 (renames.json 里有 old_key/new_key)
ren = json.load(open(os.path.join(PROJ, "logs", "iss358", "renames.json"), encoding="utf-8"))
revert = {r["new_key"]: r["old_key"] for r in ren}
mech_orig = dict(frags_now["mech-lead"])
orig_answers = []
hit = 0
for a in frags_now["mech-lead"]["answers"]:
    b = dict(a)
    if b.get("key") in revert:
        b["key"] = revert[b["key"]]
        hit += 1
    orig_answers.append(b)
mech_orig["answers"] = orig_answers
frags_revert = dict(frags_now)
frags_revert["mech-lead"] = mech_orig

a_cnt = count(frags_now)
b_cnt = count(frags_revert)
print("还原条数(应=8):", hit)
print("【反事实·我的改动前】总需求=%d 已答=%d 未闭合(pending)=%d 等外部=%d" % (
    b_cnt["total"], b_cnt["answered"], b_cnt["pending"], b_cnt["ext"]))
print("【现状·我的改动后】总需求=%d 已答=%d 未闭合(pending)=%d 等外部=%d" % (
    a_cnt["total"], a_cnt["answered"], a_cnt["pending"], a_cnt["ext"]))
print("⇒ 我的改动对未闭合需求数的净影响 = %+d" % (a_cnt["pending"] - b_cnt["pending"]))
print("⇒ 我的改动对已答数的净影响 = %+d" % (a_cnt["answered"] - b_cnt["answered"]))
sa = set(b_cnt["unclosed"]); sb = set(a_cnt["unclosed"])
print("⇒ 状态翻转的 need 条数 (我的改动引起) =", len(sb ^ sa))
for x in sorted(sb ^ sa)[:20]:
    print("    ", x)
# hw-lead 本轮并发新增的 need
hw_keys = {n.get("key") for n in frags_now["hw-lead"].get("needs_from") or [] if isinstance(n, dict)}
print("⇒ hw.yaml 当前 needs_from 条数 =", len(hw_keys))
iss356 = sorted(k for k in hw_keys if isinstance(k, str) and k.startswith("iss356_"))
print("⇒ 其中 iss356_* 新增 =", len(iss356), iss356)
