#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_0407_brief_marker_fix.py
★把两条 brief 的"本单产出路径"改成闸认得的写法 ⇒ `state/check_brief_commands.py` 归绿★

★★**为什么改 (★派活前必做那道闸, 不是洁癖★)**:
  ★**闸的豁免口径**: 路径【同一行】前面 30 字内出现【新建/新增/产出/输出文件/交付物…】⇒ 认定它是"本单产出" ⇒ 豁免
  ★**ISS-225 (本轮新开)**: 原来写的是 `交接单 \`HANDOFF/…ISS225….md\` (★新建★)` ⇒ "新建"在路径【后面】⇒ 闸认不出 ⇒ 误报
    ⇒ ★**改成**: `交接单 (★新建★) \`HANDOFF/…ISS225….md\`` ⇒ 闸豁免 ✔
  ★**ISS-223 (hw-lead 已在跑, 04:07 实测会话仍活着)**: 它的交接单路径同样没带"新建"标记 ⇒ 闸一直误报
    ⇒ ★**只加标记, 一字不改它的任务内容** ⇒ ★**不动正在跑的会话, 只把队列里的 brief 文本改成闸认得的写法** ★
"""
import os
import shutil
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")

REPL_225_OLD = "★**交接单 `HANDOFF/2026-11-16_sw-lead_ISS225_SW侧md5基线台账化.md` (★新建★)**"
REPL_225_NEW = "★**交接单 (★新建★) `HANDOFF/2026-11-16_sw-lead_ISS225_SW侧md5基线台账化.md`**"

REPL_223_OLD = "★**交接单 `HANDOFF/2026-11-16_hw-lead_ISS223_落表第2批与分片补落.md`**"
REPL_223_NEW = "★**交接单 (★新建★) `HANDOFF/2026-11-16_hw-lead_ISS223_落表第2批与分片补落.md`**"


def main():
    with open(LOG, "r", encoding="utf-8") as f:
        log = yaml.safe_load(f)
    by_id = {i.get("id"): i for i in log["issues"]}

    n = 0
    b = by_id["ISS-225"]["task_brief"]
    assert REPL_225_OLD in b, "ISS-225 目标串没找到"
    by_id["ISS-225"]["task_brief"] = b.replace(REPL_225_OLD, REPL_225_NEW)
    n += 1

    b = by_id["ISS-223"]["task_brief"]
    assert REPL_223_OLD in b, "ISS-223 目标串没找到"
    by_id["ISS-223"]["task_brief"] = b.replace(REPL_223_OLD, REPL_223_NEW)
    n += 1

    shutil.copy2(LOG, LOG + ".bak_20261116_0407_brief_marker_fix")
    with open(LOG, "w", encoding="utf-8") as f:
        yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
    print(f"OK: {n} 条 brief 的产出路径已加『★新建★』标记 (任务内容一字未改)")


if __name__ == "__main__":
    main()
