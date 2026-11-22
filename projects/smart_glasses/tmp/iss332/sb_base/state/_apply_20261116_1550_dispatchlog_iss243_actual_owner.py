#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1550_dispatchlog_iss243_actual_owner.py
★main (moli) 2026-11-16 15:5x (cron 775d9893 ARS45 继续执行后继计划)★
★**只往 `state/dispatch_log.yaml` 补一条 ISS-243 的【实际在跑会话归属】记录** ★
★(为什么要这一条: 上一条 ISS-243 重派记录写的是【已死会话】337705c2 ⇒ 下一轮若只按 session_key 判"有没有在跑会话"会误判成没人跑 ⇒ 补上真会话 key★)
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-16"
REAL_SESSION = "agent:hw-lead:subagent:8f42d87e-22c6-404c-9fd7-81be77ece276"


def _atomic_write(path: str, data: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".tmp_dl.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    shutil.copy2(DL, DL + ".bak_20261116_1550_iss243_actual_owner")
    lf = open(LOCK, "a+")
    try:
        fcntl.flock(lf, fcntl.LOCK_EX)
        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {"dispatches": []}
        disp = dl.setdefault("dispatches", [])
        if any(d.get("session_key") == REAL_SESSION for d in disp):
            print("   - dispatch_log 里已有本会话记录 ⇒ 不重复写")
            return 0
        disp.append({
            "issue": "ISS-243",
            "agent": "hw-lead",
            "at": TODAY,
            "brief": (
                "★**实际在跑会话归属 (★main 2026-11-16 15:5x 补记★)**: ★**本条 IS**S-243 续做派活"
                "= cron 775d9893 (继续执行后继计划) 15:4x spawn 的会话 `8f42d87e` (run 9685960b · taskName advance_iss243 · runTimeout 5400s) ★"
                "⇒ ★**上一条 ISS-243 重派记录里的 session_key 337705c2 是【已死的上一轮会话】, 不是在跑会话** ★ "
                "⇒ ★**判【有没有在跑的写会话】时以本条 session_key 为准** ★ "
                "⇒ ★**去重记录**: 兄弟 job fb67af40 (队列自动派活) 15:4x 同时也在准备重派 ISS-243 ⇒ ★**已用 sessions_send 把它劝停** (它回: 「队列无新动作 · hw-lead 名额已由 8f42d87e 占用」) "
                "⇒ ★**同一 agent 只留一条写会话 (铁律)** ★"
            ),
            "redispatch": True,
            "reason": (
                "★main 实测: 上一轮会话 337705c2 (15:15:03~15:24:10 · runtime 543s · aborted) ⇒ 零产出僵尸 "
                "(MOS_PAD_PIN_MAPPING.md 不存在 / 交卷单不存在 / 网表脚表 BOM 板 4 个 md5 逐字节未变) ⇒ 本轮续做重派 ★"
            ),
            "session_key": REAL_SESSION,
            "run_id": "9685960b-4335-49f7-b860-4eb49d326bd0",
            "task_name": "advance_iss243",
            "run_timeout_s": 5400,
            "dedup": "★已劝停兄弟 job fb67af40 同刻重派 (sessions_send · 它确认不再 spawn)★",
        })
        _atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))
    finally:
        fcntl.flock(lf, fcntl.LOCK_UN)
        lf.close()
    print("   - dispatch_log 补记 ISS-243 实际在跑会话归属 (8f42d87e) + 去重记录")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
