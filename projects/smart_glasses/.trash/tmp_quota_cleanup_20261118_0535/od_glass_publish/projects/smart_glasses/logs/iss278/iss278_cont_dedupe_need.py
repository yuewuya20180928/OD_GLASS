#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iss278_cont_dedupe_need.py —— ★合并 mech.yaml 里同 key 的重复 need (★用 frag_write 的原子写, 禁止裸 open(p,"w")★)★

★为什么需要这一步★:
  ★**ISS-278 的同一件事 (check_demo_struct_truth --selftest rc=1 的升级) 被本 agent 的两次续做各写了一条同 key 的 need** ★
  ⇒ `state/merge.py` 按 key 配对 ⇒ ★**needs_matrix/pending 里出现两条同 key** ⇒ main 会看到同一件事被挂两次 ⇒
  ★**⇒ 合并成一条 (内容取两条的并集, 一条信息都不丢) ⇒ main 只看到一件, 但两轮的证据都在★**

★纪律: ★**只走 `state/frag_write.py` 的 `update_fragment` (原子 tmp+os.replace) ⇒ 不裸写分片★** ★
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "state"))

from frag_write import update_fragment          # ★只用它的原子写★

KEY = "iss278_mech_demo_struct_truth_selftest_regression"


def main() -> int:
    seen = []

    def mutate(d):
        needs = d.get("needs_from") or []
        hits = [n for n in needs if n.get("key") == KEY]
        if len(hits) < 2:
            print(f"[dedupe] 无需合并 (同 key 条数 = {len(hits)})")
            return
        # ★取两条的 item 并集 (★中间用分隔标, 一条信息都不丢★)★
        merged_item = "\n\n".join(
            f"★**—— 合并自本 agent 两次续做 (★内容为并集, 一条信息都不丢★) ——**\n\n{n.get('item','')}"
            for n in hits)
        keep = {
            "key": KEY,
            "to": hits[0].get("to", "main"),
            "item": merged_item,
            "since": hits[-1].get("since", "2026-11-17"),
        }
        out = []
        placed = False
        for n in needs:
            if n.get("key") == KEY:
                if not placed:
                    out.append(keep)
                    placed = True
                continue
            out.append(n)
        d["needs_from"] = out
        seen.append((len(hits), len(merged_item)))

    update_fragment("mech-lead", mutate)
    if seen:
        print(f"[dedupe] ✅ 合并 {seen[0][0]} 条同 key need ⇒ 1 条 (item {seen[0][1]} 字符)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
