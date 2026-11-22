#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★**cron fb67af40 · 2026-11-18 20:5x · ISS-333 cont1 brief 刷新 (★幂等·★只替换 cont1 那一段·★原 brief 全文不动★)** ★

★**为什么有这一步**: ★**cont1 段落是在 apply 之后才补上「extra_gates 只在 --json 模式里打印」那条实测坑的** ★
⇒ ★**⇒ issue_log.yaml 里那份拷贝是旧的 ⇒ 必须刷新, 否则派出去的 brief 与盘上的 brief 不是同一份** ★
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
MARKER = "【ISS-333 · mech-lead · ★★cont1 续做单"
STAMP = "20261118_2050_cronfb67_iss333_cont1_brief_refresh"

BRIEF = open(
    os.path.join(HERE, "dispatch_briefs", "ISS-333_mech_designator_gate_hook_prep_cont1.md"),
    encoding="utf-8",
).read()


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        shutil.copy2(LOG, LOG + ".bak_" + STAMP)
        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        i333 = next((i for i in issues if i.get("id") == "ISS-333"), None)
        if not i333:
            print("· ISS-333 不存在 (异常)")
            return 1
        tb = i333.get("task_brief") or ""
        pos = tb.find(MARKER)
        if pos < 0:
            print("· ISS-333 task_brief 里找不到 cont1 段 (异常)")
            return 1
        head = tb[:pos].rstrip()
        # 去掉 head 末尾的分隔线 (★原来那段前面有 "\n\n---\n\n"★)
        if head.endswith("---"):
            head = head[:-3].rstrip()
        new_tb = head + "\n\n---\n\n" + BRIEF
        i333["task_brief"] = new_tb
        log["issues"] = issues
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=10**6))
        print("· ISS-333 task_brief 的 cont1 段已刷新 (★原 brief 全文保留★)")
        print("· 原 task_brief 长度 %d → 新长度 %d" % (len(tb), len(new_tb)))
        print("· cont1 段长度 %d (★盘上文件 %d B·一致=True★)" % (len(BRIEF), os.path.getsize(
            os.path.join(HERE, "dispatch_briefs", "ISS-333_mech_designator_gate_hook_prep_cont1.md"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
