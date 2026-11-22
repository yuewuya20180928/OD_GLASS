#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261117_1520_dispatchlog_iss289_cont1.py
★main (moli) · cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-17 15:2x★
★★**只往 `state/dispatch_log.yaml` 追加一条 ISS-289 的【续做重派 cont1】记录·不动 issue_log 的 status (已是 fixing)★**

★**为什么不用 `advance.py --apply --only ISS-289`**: ★**它只在 `status == "open"` 时才标 fixing 并写派活日志★ ⇒ ISS-289 早已是 fixing ⇒ 跑它 = no-op (applied 为空) ⇒ ★**派活日志会缺这一趟的续做记录★ ⇒ ⇒ 本脚本补这一条 (★只 append 一条 dispatch, 不改任何既有条目★)★**

★**边界**: ★**零写板 · 零落表 · 不改 issue_log 的 status 字段 · 不改任何既有 dispatch 条目 · 零外发 · 不碰 PROJECT_TRACKER.md §0★**
"""
import fcntl
import os

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".dispatch_log.lock")

BRIEF = (
    "★**ISS-289 · hw-lead 续做 cont1 (★2026-11-17 15:12 原会话被网关掐断 `abortedLastRun=true` ⇒ "
    "闸 + 订正块 + 分片全在盘, 缺的只是交卷单正文★)** ⇒ ★**只补交卷单 B0~B6 (★七段全是「施工中」骨架★) + "
    "跑回归验收贴 rc + 回答两个差异结论★** ⇒ ★**不许重做闸 `HW/check_workpack_state_values.py` (★已 rc=0 · "
    "selftest 10/10★) · 不许重改追加式订正块 (★已由闸 V2/V3 自证在位★) · 若认为有 bug ⇒ 写进 B5 未决项交 main 裁决★** ⇒ "
    "★**两个必须给结论的问题**: ① 封装数 186 (真盘) vs 185 (ISS-287 沙盒) 差 1 件在哪 + 动板那趟按哪个数走 ② "
    "`_1` 后缀位号官方板 1 个 vs 登记 156 这两个数分别什么口径★** ⇒ ★**零写板 · 零落表 · 零改生成器代码 · "
    "不碰 MECH/SW · 零外发 · 不替老板拍板 · 不自签 issue_log★** ⇒ "
    "★**任务书全文 = `state/dispatch_briefs/ISS-289_hw_workpack_state_values_cont1.md` (★已过 "
    "`python3 state/check_brief_commands.py --brief-file` ⇒ rc=0★)★** ⇒ "
    "★**会话 = `agent:hw-lead:subagent:1e68b706` (★由 cron 775d9893 派出★)★**"
)

JOB = (
    "★派活方 = cron 775d9893 (ARS45 继续执行后继计划) 于 15:2x 派出并在飞 "
    "(★session agent:hw-lead:subagent:1e68b706·72ab-4692-bba2-e51cbd5e319b·runId a1a924b8★)★ · "
    "★**续做原因 = 原会话 15:12 超时被掐 (`abortedLastRun=true`), 半成品在盘★** ★"
    "★**本 job 不重复派第二个 hw-lead 会话 (★同一 agent 只允许一个写会话★)★**"
)

ENTRY = {"issue": "ISS-289", "agent": "hw-lead", "at": "2026-11-17", "brief": BRIEF, "job": JOB}


def main() -> int:
    lockf = open(LOCK, "a+")
    fcntl.flock(lockf, fcntl.LOCK_EX)
    try:
        with open(DL, "r", encoding="utf-8") as f:
            dl = yaml.safe_load(f) or {"dispatches": []}
        disp = dl.setdefault("dispatches", [])
        # ★幂等: 同 issue + 同 agent + 同 at 且 brief 已含 cont1 ⇒ 不重复追加★
        for d in disp:
            if isinstance(d, dict) and d.get("issue") == "ISS-289" and "cont1" in str(d.get("brief", "")):
                print("★dispatch_log 已有 ISS-289 cont1 条目 ⇒ 不重复追加")
                return 0
        disp.append(ENTRY)
        with open(DL, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
        print("★dispatch_log.yaml 已追加 ISS-289 cont1 派活记录 (共 %d 条 dispatch)" % len(disp))
        return 0
    finally:
        fcntl.flock(lockf, fcntl.LOCK_UN)
        lockf.close()


if __name__ == "__main__":
    raise SystemExit(main())
