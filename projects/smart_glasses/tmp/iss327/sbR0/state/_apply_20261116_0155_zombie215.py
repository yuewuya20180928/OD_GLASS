#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main: 清僵尸 fixing (ISS-215 / sw-lead) ⇒ 回滚 open (待重派)
=========================================================================================
★**实测依据 (★2026-11-16 01:5x, main 自己查盘 + 读 transcript★)**:
· 子会话 `agent:sw-lead:subagent:580cc849` (db9aa514) 00:42:33 → **01:49:50 结束**
  (★status=done · abortedLastRun=false · ★但整场 74 分钟 / 635k tokens★)
· ★**盘上交付物 0 件**: `SW/` 下 00:40 以后无任何文件被改 (DEMO_OD_TIMING_SPEC.md 停在 11-15 22:28 ·
  timing_check.py 停在 11-15 22:30) · `state/fragments/sw.yaml` mtime = 00:00:40 (早于本会话) ·
  `HANDOFF/2026-11-16_sw-lead_ISS215*` 不存在 ⇒ ★**"session=done" ≠ "活干完了" (第 19 次复发)★**
· transcript 末尾全是 "Now let me check ..." 的分析循环 ⇒ ★**长上下文空转: 读了一堆没动手写★**
· ★**兄弟 job 775d9893 已明确把这条留给本 job** ("I'll flag it, not race it" ⇒ 它不动 ISS-215) ⇒ 不撞车
★**处置**: status fixing → open (★留痕: 上一轮 0 交付 + 空转原因★) ⇒ 由本 job 重派
★**铁律**: 干活的人不许自签 ⇒ verify_by=main
★**不碰**: 任何真源文件 / 任何分片 / PROJECT_TRACKER §0 / outbox
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261116_0155_zombie215"
IID = "ISS-215"

NOTE = (
    "\n\n★2026-11-16 01:5x 队列自动派活 job (fb67af40) **僵尸 fixing 清理**: 子会话 "
    "`agent:sw-lead:subagent:580cc849` (db9aa514) 00:42:33 → 01:49:50 (★status=done · abortedLastRun=false★) "
    "整场 74 分钟 / 635k tokens ⇒ ★**盘上交付物 0 件**: `SW/` 下 00:40 以后零文件改动 "
    "(DEMO_OD_TIMING_SPEC.md 停在 11-15 22:28 · timing_check.py 停在 11-15 22:30) · "
    "`state/fragments/sw.yaml` mtime=00:00:40 (早于本会话) · `HANDOFF/2026-11-16_sw-lead_ISS215*` 不存在 ⇒ "
    "★**「session=done」不等于「活干完了」(第 19 次复发)★** ⇒ transcript 末尾全是分析循环 "
    "(★长上下文空转: 读了一堆没动手写★) ⇒ ★**status 由 fixing 回滚为 open 并重派**, "
    "★重派时已加「先落盘再展开」的执行纪律★ (★兄弟 job 775d9893 已把这条留给本 job, 不撞车★)"
)


def main():
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        hit = None
        for it in issues:
            if it.get("id") == IID:
                hit = it
                break
        if hit is None:
            print("⚠ %s 不存在 ⇒ 跳过" % IID)
            return
        if hit.get("status") != "fixing":
            print("⚠ %s status=%s (不是 fixing) ⇒ 幂等跳过, 不重复落账" % (IID, hit.get("status")))
            return
        hit["status"] = "open"
        hit["dispatched_at"] = None
        hit["note"] = (hit.get("note") or "") + NOTE
        shutil.copy2(LOG, BAK)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("备份: %s" % BAK)
    print(" - %s fixing → open (僵尸 fixing 回滚, 待重派)" % IID)


if __name__ == "__main__":
    main()
