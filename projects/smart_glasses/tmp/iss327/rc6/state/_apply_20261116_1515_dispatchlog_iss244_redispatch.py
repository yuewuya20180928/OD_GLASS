#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261116_1515_dispatchlog_iss244_redispatch.py
★main (moli) 2026-11-16 15:15 (cron fb67af40 ARS45 队列自动派活)★
★**只往 `state/dispatch_log.yaml` 补一条 ISS-244 的【续做重派】记录** ★
★(ISS-243 那条已由 `state/advance.py --apply --only ISS-243` 写入 ⇒ 本脚本不重复写★)
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

BRIEF_244_HEAD = (
    "★**续做派活 (★main 2026-11-16 15:1x 实测: 上一轮会话 14:43:10~14:52:04 撞 timeout (runtime 484s · abortedLastRun=true · status=timeout) "
    "⇒ ISS-244 是【零产出僵尸】★) ⇒ ★**本轮重派 · runTimeout 5400s** ★** "
    "★**盘上零产出 (收口页/门禁/交卷单/分片 四件一件没落) ⇒ 上一轮 9 分钟全花在内存里 (APH1608SURCK 的 Iv-vs-If 数字化) ⇒ "
    "本轮要求: 先落盘骨架再填内容 · PDF 与数字化脚本落盘 · 四条重点缺口优先于 22 件 OPN 清单** ★"
)


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
    shutil.copy2(DL, DL + ".bak_20261116_1515_cron_iss244_redispatch")
    lf = open(LOCK, "a+")
    try:
        fcntl.flock(lf, fcntl.LOCK_EX)
        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {"dispatches": []}
        disp = dl.setdefault("dispatches", [])
        last = disp[-1] if disp else {}
        if last.get("issue") == "ISS-244" and last.get("redispatch"):
            print("   - dispatch_log 里已有 ISS-244 重派记录 ⇒ 不重复写")
            return 0
        disp.append({
            "issue": "ISS-244",
            "agent": "sw-lead",
            "at": TODAY,
            "brief": BRIEF_244_HEAD,
            "redispatch": True,
            "reason": (
                "★上一轮 status=timeout/aborted (runtime 484s · abortedLastRun=true · session c2315fc7) ⇒ 零产出僵尸: "
                "HW/PART_SELECTION_GAPS_CLOSEOUT.md / HW/check_part_selection_gaps*.py / HANDOFF/2026-11-16_sw-lead_ISS244_*.md "
                "四件交付物一件没落 ⇒ 仍无交卷 ★"
            ),
            "session_key": "agent:sw-lead:subagent:4270cb11-51d5-4aac-9c77-1c7ef270e476",
            "run_id": "f5acafad-291a-4628-b1a7-912300afd1c6",
        })
        _atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=100000))
    finally:
        fcntl.flock(lf, fcntl.LOCK_UN)
        lf.close()
    print("   - dispatch_log 补记 ISS-244 续做重派 (session 4270cb11 / run f5acafad)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
