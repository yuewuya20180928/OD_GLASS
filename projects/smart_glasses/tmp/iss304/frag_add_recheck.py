#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-304 交卷后复验条目 → 原子写进 state/fragments/hw.yaml (走 frag_write 的原子写)"""
import os
import sys

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
sys.path.insert(0, os.path.join(ROOT, "state"))

from frag_write import update_fragment  # noqa: E402

KEY = "iss304_post_reload_recheck_0556"
VALUE = (
    "交卷后复验 (2026-11-18 05:56, gateway reload 之后; 别的总工在此期间又落了 ISS-305/307/308/310): "
    "① HW/check_workpack_state_values.py rc=0 (V1~V7 全 OK, V4 那 4 条台账口径 fresh 全「实测 == 期望」); "
    "② state/gate_check.py rc=0 (Q7 钉板 md5 闸链 9/9 道绿, 钉板闸⑥ rc=0) ⇒ 板那一趟的闸链在交卷后依旧全绿; "
    "③ 幂等复跑: 真生成器 + 真同步脚本各再跑一次, 三个 md5 跑前跑后逐字节相同 "
    "(清单页 9f9743c8… / 作业包页 0b6fc2f8… / sidecar 1684c0b0…), "
    "同步脚本自报 0 处 fresh 改了 + sidecar 与作业包页的 state_baseline 登记表逐字节一致 (16607 B); "
    "④ 沙盒反向用例 5 条全过 rc=0 (含「台账链头前跳 ⇒ 4 条 fresh 跟上新链」与「链断 ⇒ 生成器拒写 rc=1 且页一个字节没动」); "
    "⑤ 受保护 5 件 md5 逐字不变 (板 611b869e… / .kicad_pro 3e504d2b… / 网表 6aee500e… / 脚表 9174309d… / BOM 5b999399…) "
    "⇒ 零写板零落表依旧成立; HW/check_pin_function_labels.py 仍 rc=1 = 15 条既有缺陷基线 (ISS-239, 落表批次里修), 原样记录, 不是本单的锅"
)
REF = (
    "logs/iss304/14_post_reload_recheck.log + logs/iss304/15_post_reload_idempotent.log + "
    "HANDOFF/2026-11-18_hw-lead_ISS304_作业包现状值重锚.md §附-2"
)


def mutate(d):
    answers = d.setdefault("answers", [])
    for a in answers:
        if isinstance(a, dict) and a.get("key") == KEY:
            a["value"] = VALUE
            a["ref"] = REF
            return
    answers.append({"key": KEY, "to": "main", "value": VALUE, "ref": REF})


update_fragment("hw-lead", mutate)
print("frag_write ok:", KEY)
