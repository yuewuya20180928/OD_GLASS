#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★**cron fb67af40 (ARS45 队列自动派活) · 2026-11-18 20:4x · ISS-333 cont1 重派 (mech-lead)** ★

★**为什么派这一条 (★逐条都是本机实跑读数·不抄任何 agent 报告★)**:
  ① `state/advance.py --json` ⇒ internal = [] (三个总工名下零 open ⇒ A 段真空)
  ② 跨 job 查活 (★看 `~/.openclaw/agents/<agent>/sessions/*.jsonl` 的 mtime★):
     - sw-lead  20:41:42 (0 min)  ⇒ 在飞 ⇒ 不碰 (ISS-332)
     - hw-lead  19:46:54 (55 min) ⇒ 会话被掐, 但★后台链还活着★
       (PID 1130618 `bash tmp/iss328/run_ru_arm.sh` / PID 1130654 `gen_pcb_netlist_board.py` 活,
        `tmp/iss328/ru_R.gen.log` 20:38 仍在长) ⇒ ★**不许重派** (活链期间重派 = 两个 agent 抢同一个分片)
     - mech-lead 19:40:47 (1h01m) ⇒ 会话最后一条是 toolResult「Aborted」⇒ ★**真僵尸** ★
  ③ 僵尸鉴别 (★不是只看 status=fixing★): ISS-333 的成果**部分在盘**
     - 在盘: `MECH/tools/check_mech_ref_reachability.py` (56,550 B · 19:36)
             + `logs/iss333/` 8 件
             ★**main 20:4x 本机实跑 `--selftest` ⇒ rc=0 · 反向用例 14/14 通过** ★
     - 缺: 交卷页 `HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md` **不存在**
           + `grep -c iss333 state/fragments/mech.yaml` = **0** (分片一字没写)
  ④ ★**main 20:2x 已把这道闸挂进 `state/gate_check.py` 的 EXTRA_GATES (ISS-330 owner=main · 已落 fixed)**
     ⇒ ★**⇒ 这道闸已经在链上 ⇒ 【不许 agent 再改它】·改了链上那道闸就与盘面不一致**
     ⇒ ★**⇒ 收卷口径 = 【交卷页填实 + 分片写 + 挂闸后闸复跑 rc 落盘】** (MEMORY 铁律③) ★
  ⑤ 兄弟 job 775d9893 20:2x 明确不抢队列, 并把处置指令写在 DECISION_INDEX_2026-11-18.md §P-2 第 1 条
     ⇒ ★**本 job (持队列者) 执行该处置指令** ★

★**纪律**: 零写板 · 零落表 · 零改闸 · 零改 agent 的分片 · 零外发 · 不替老板拍板
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-18 20:4x"
STAMP = "20261118_2045_cronfb67_iss333_cont1"

BRIEF_333_CONT = open(
    os.path.join(HERE, "dispatch_briefs", "ISS-333_mech_designator_gate_hook_prep_cont1.md"),
    encoding="utf-8",
).read()

DISPATCH_BRIEF = (
    "★★**cont1 重派 (★不是从零·是【收卷】★) · 2026-11-18 20:4x · cron fb67af40 (ARS45 队列自动派活)** ★ ★"
    "★**为什么派 (★本机实跑读数★)**: "
    "★**① 上一趟会话 19:40:47 被掐 (最后一条 toolResult = 「Aborted」) ⇒ 会话没了, 但成果大部分在盘** ★ "
    "★**② 成果在盘**: `MECH/tools/check_mech_ref_reachability.py` (56,550 B · 19:36) + `logs/iss333/` 8 件 "
    "(baseline_repro.json / baseline_repro_raw.txt / freeze_guard.txt / freeze_registry_output.txt / gate_dump_classification.txt / gate_main_run.txt / repro_baseline.py / repro_iss326_caliber.py) "
    "⇒ ★**main 20:4x 本机实跑 `--selftest` ⇒ rc=0 · 反向用例 14/14 通过 (MC-1~MC-14)** ★ "
    "★**③ 成果缺**: 交卷页 `HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md` **不存在** + "
    "`grep -c iss333 state/fragments/mech.yaml` = **0** (分片一字没写) ⇒ ★**真僵尸 (成果在盘但没人收卷)** ★ "
    "★**④ ★★最要紧的一条★★: main 20:2x 已把这道闸挂进 `state/gate_check.py` 的 EXTRA_GATES (ISS-330 owner=main · 已落 fixed·挂完五门 rc 全绿) "
    "⇒ ★**⇒ 这道闸已经在链上 ⇒ 【不许 agent 再改它】·改了链上那道闸就与盘面不一致 ⇒ 本单只补【交卷页 + 分片 + 挂闸后 rc 落盘】** ★ "
    "★**⑤ 兄弟 job 775d9893 20:2x 明确不抢队列, 处置指令写在 DECISION_INDEX_2026-11-18.md §P-2 第 1 条 ⇒ 本 job (持队列者) 执行** ★ "
    "★**任务书全文**: `state/dispatch_briefs/ISS-333_mech_designator_gate_hook_prep_cont1.md` "
    "(8,255 B · ★`check_brief_commands.py --brief-file` rc=0★ · ★该闸自测 --self-test 10/10 通过 ⇒ 不是摆设★) ★ "
    "★**边界**: 零写板 · 零落表 · 零改 `state/gate_check.py` · ★**零改 `MECH/tools/check_mech_ref_reachability.py` (★已在链上·★改了就失真)★** · "
    "零改 `SW/tools/check_sw_ref_reachability.py` (★已在链上·只读 import★) · 零改既有 `MECH/**/*.md` 正文 (★闸的扫描面就是它·写了位号 = 全项目门禁变红★) · "
    "零改既有 `MECH/**/*.py` · 零改 `logs/iss326/` · 沙盒只写 `tmp/iss333/` + `logs/iss333/` · 只写 `state/fragments/mech.yaml` "
    "★**零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信 ⇒ 没有「批一句可以发」这个选项)★** · 不替老板拍板 · 不自签 `state/issue_log.yaml` ★"
)


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
    applied = []
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        # ── 备份 (★改前必备份·★出事能回滚★) ──
        shutil.copy2(LOG, LOG + ".bak_" + STAMP)
        shutil.copy2(DLOG, DLOG + ".bak_" + STAMP)
        applied.append("备份: issue_log.yaml + dispatch_log.yaml")

        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}

        # ── ISS-333 cont1 (★status 保持 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 不会重复派★) ──
        i333 = idx.get("ISS-333")
        if not i333:
            print("· ISS-333 不存在 (异常)")
            return 1
        tb = i333.get("task_brief") or ""
        if "ISS-333 · mech-lead · ★★cont1 续做单" not in tb:
            i333["task_brief"] = tb + "\n\n---\n\n" + BRIEF_333_CONT
            applied.append("ISS-333 task_brief += cont1 (★原 brief 全文保留★) · status 保持 fixing")
        else:
            applied.append("ISS-333 cont1 已在 brief 里 (跳过·幂等)")
        if i333.get("status") != "fixing":
            i333["status"] = "fixing"
            applied.append("ISS-333 status → fixing (★它本来就是 fixing·此处只作兜底★)")
        i333["dispatched_at"] = NOW
        i333["note"] = (
            str(i333.get("note") or "")
            + " ★★2026-11-18 20:4x · cron fb67af40 重派 cont1★★ "
            "★**上一趟 19:40:47 被掐 ⇒ 成果在盘但没人收卷 (★交卷页不存在·分片命中 0★) "
            "⇒ ★**main 20:2x 已把这道闸挂进 `state/gate_check.py` 的 EXTRA_GATES (ISS-330) ⇒ 本单不许再改那道闸 "
            "⇒ ★**收卷口径 = 交卷页填实 + 分片写 + 挂闸后闸复跑 rc 落盘** ★"
        )
        applied.append("ISS-333 dispatched_at / note 已更新")

        log["issues"] = issues
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=10**6))

        # ── dispatch_log 追加 ──
        dlog = yaml.safe_load(open(DLOG, encoding="utf-8")) or {}
        entries = dlog.get("dispatches") or []
        if not any(e.get("issue") == "ISS-333" and "cont1" in str(e.get("brief") or "") for e in entries):
            entries.append(
                {
                    "issue": "ISS-333",
                    "agent": "mech-lead",
                    "at": "2026-11-18",
                    "brief": DISPATCH_BRIEF,
                    "job": (
                        "cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 20:4x · "
                        "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"
                    ),
                }
            )
            dlog["dispatches"] = entries
            atomic_write(DLOG, yaml.safe_dump(dlog, allow_unicode=True, sort_keys=False, width=10**6))
            applied.append("dispatch_log.yaml += ISS-333 cont1 1 条")

    for a in applied:
        print("·", a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
