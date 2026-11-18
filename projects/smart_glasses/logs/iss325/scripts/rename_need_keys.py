#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-325 · rename_need_keys.py -- 把本单两条新 need 的 key 改成【任务书 §③-5 逐字给的名字】

★**为什么要改名**: 任务书 §③-5 逐字给了两个 need key:
    · `iss325_s8_tp_pin_noop_proven`
    · `iss325_s8_no_valid_control`
★ 上一趟 (并行实例) 用的是同义但不同的 key (`iss325_s8_tp_dsi_pin_is_noop` / `iss325_s8_arm_pair_not_a_control`)
★ ⇒ main 拿着任务书来查会查不到 ⇒ ⇒ 本脚本把 key 改成【任务书逐字给的那两个】, 内容一字不改

★**纪律**: 走 `state/frag_write.py` 的 `update_fragment()` (★原子写 tmp+fsync+os.replace★) ⇒ ★**禁 open(p,"w")★**
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment  # noqa: E402

RENAME = {
    "iss325_s8_tp_dsi_pin_is_noop": "iss325_s8_tp_pin_noop_proven",
    "iss325_s8_arm_pair_not_a_control": "iss325_s8_no_valid_control",
}

changed = []


def mutate(d):
    for n in d.get("needs_from", []):
        k = n.get("key")
        if k in RENAME:
            n["key"] = RENAME[k]
            changed.append("%s → %s" % (k, RENAME[k]))
    # 顺手给两条 need 的 item 末尾补一句「key 已按任务书 §③-5 逐字对齐」⇒ main 查得到
    for n in d.get("needs_from", []):
        if n.get("key") in RENAME.values():
            n["item"] = n.get("item", "") + " ★(本 need key 已按 ISS-325 cont2 任务书 §③-5 逐字对齐★)"


update_fragment("hw-lead", mutate)
print("✅ 改名 %d 条:" % len(changed))
for c in changed:
    print("   " + c)
