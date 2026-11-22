#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_apply_20261117_1145_cron_fb67_redisp_iss285.py
moli (项目总工) 2026-11-17 11:4x · job fb67af40「ARS45 队列自动派活」
★ISS-285 (sw-lead) 僵尸 fixing ⇒ 【续做】重派落账 (★不改 status · 只补留痕 + 派活日志★)

★★**本 job 自己查盘 + 读 transcript, 不抄任何兄弟 job 的报告★★:
· `python3 state/advance.py --json` ⇒ internal = [] (★hw-lead 名额被 ISS-282 (fixing) 占着 ·
  sw-lead 名额被 ISS-285 (fixing) 占着 ⇒ 两个名额都被占★)
· ★**ISS-285 的会话是僵尸**: `agent:sw-lead:subagent:b15754e1` (11:05:28 → 11:35:47 ·
  status=timeout · abortedLastRun=true) ⇒ transcript 末条 = "Now I'll write the patch
  (as an idempotent applier) — to SW/patches/, not touching any real file yet." ⇒ ★写完就断了★
· ★**盘上实况 (本 job 实测)**: 交卷单 1362 B 骨架 (§0 情形判定已填 / §1~§6 全「施工中·待填」) ·
  补丁套用器 24640 B (11:33) ★**一次都没跑过** (logs/iss285/ 不存在)★ · `grep -c ISS-285
  state/fragments/sw.yaml` = 0 ⇒ ★**分片零写**★
· ★**ISS-282 (hw-lead) 不是僵尸**: `agent:hw-lead:subagent:e1153379` (11:03 起 · status=running ·
  11:37 仍在写) ⇒ ★**hw-lead 名额继续被占 ⇒ ISS-283 (open) 本轮不派**★

★★**本脚本做的事 (边界写死)★★:
· ★**只写 `state/issue_log.yaml` + `state/dispatch_log.yaml` (flock + 锁内重读 + tmp/os.replace 原子写)★★
· ISS-285: ★**status 保持 fixing** (★续做重派不是新单★) + note 追加僵尸实况 + dispatched_at 刷新
· dispatch_log: 追加一条 ISS-285 / sw-lead 的【续做重派】条目 (★brief 指向 cont1 任务书★)
· ★**不碰板 / 网表 / 脚表 / BOM / 任何 agent 的分片 / 决策页 / outbox / 别人的 issue****
· ★**零外发 · 零采购 · 不替老板拍板****
"""
import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
IL = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-17"

NOTE = (
    "\n\n★**2026-11-17 11:4x (cron fb67af40 队列自动派活) 僵尸 fixing ⇒ 【续做】重派 (★不是新单·status 保持 fixing★)** ★\n"
    "· ★**僵尸实况 (本 job 自己查盘 + 读 transcript)**: 子会话 `agent:sw-lead:subagent:b15754e1` "
    "(11:05:28 → 11:35:47 · status=timeout · abortedLastRun=true) ⇒ transcript 末条 = "
    "\"Now I'll write the patch (as an idempotent applier) — to SW/patches/, not touching any real file yet.\" "
    "⇒ ★**补丁写完就断了**★\n"
    "· ★**盘面半成品 (本 job 实测)**: 交卷单 `HANDOFF/2026-11-17_sw-lead_ISS285_落表后SW判据口径收口.md` "
    "= **1362 B 骨架** (§0 情形判定已填 = 情形一 / §1~§6 全「施工中·待填」) · "
    "补丁套用器 `SW/patches/ISS-285_sw_judgment_alignment/apply_iss285_sw_judgment_alignment.py` = "
    "**24640 B (11:33) · 一次都没跑过** (★`logs/iss285/` 目录不存在★) · "
    "`grep -c ISS-285 state/fragments/sw.yaml` = **0** ⇒ ★**分片零写**★\n"
    "· ★**情形判定不变**: `state/issue_log.yaml` 里 ISS-283 仍是 open ⇒ ★**本单仍是情形一** ⇒ "
    "★**不许改 `SW/SW_MD5_BASELINE_LEDGER.md` 锚点 / 不许改 `SW/tools/timing_check.py` 判据 / 不许改期望值**★ ⇒ "
    "★**真盘上 `timing_check.py` 交卷时必须还是 rc=1 · 68/71 (只有沙盒里才 71/71)**★\n"
    "· ★**续做任务书** = `state/dispatch_briefs/ISS-285_sw_landing_after_judgment_alignment_cont1.md` "
    "(5372 B · ★派活前已过 `python3 state/check_brief_commands.py --brief-file …` ⇒ rc=0 零告警★) ⇒ "
    "★**第一件事 cat 全文 (含原任务书全文路径)****\n"
    "· ★**本 job 同轮还查到**: ISS-282 (hw-lead) 会话 `agent:hw-lead:subagent:e1153379` "
    "(11:03 起 · status=running · 11:37 仍在写) ⇒ ★**不是僵尸 ⇒ hw-lead 名额继续被占 ⇒ "
    "ISS-283 (open·hw-lead) 本轮不派**★ ⇒ ★**一个 agent 同时只派 1 条的纪律不变**★\n"
)

BRIEF_HEAD = (
    "★**续做重派 (★11:05~11:35 那一趟会话被掐 ⇒ 盘上已有半成品: 交卷单骨架 1362 B + 补丁套用器 24640 B(没跑过)"
    " ⇒ 从盘上现状继续, 不要从零重做★)** ⇒ ★**完整任务书全文 = "
    "`state/dispatch_briefs/ISS-285_sw_landing_after_judgment_alignment_cont1.md` (5372 B) ⇒ 第一件事先 cat 全文**★\n"
    "★**原任务书全文** = `state/dispatch_briefs/ISS-285_sw_landing_after_judgment_alignment.md` (9607 B) ⇒ 也 cat 一遍★\n"
    "★**情形判定不变 (情形一)**: ISS-283 仍 open ⇒ 只读分析 + 方案页 + 自测设计 ⇒ "
    "★**不许改 SW/SW_MD5_BASELINE_LEDGER.md 锚点 / 不许改 SW/tools/timing_check.py 判据 / 不许改期望值**★ ⇒ "
    "★**真盘 timing_check.py 交卷时必须还是 rc=1 · 68/71**★\n"
)


def atomic_write(path: str, data) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix="." + os.path.basename(path) + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        il = yaml.safe_load(open(IL, encoding="utf-8")) or {}
        dl = yaml.safe_load(open(DL, encoding="utf-8")) or {}
        shutil.copy2(IL, IL + ".bak_20261117_1145_cron_fb67_redisp_iss285")
        shutil.copy2(DL, DL + ".bak_20261117_1145_cron_fb67_redisp_iss285")

        hit = 0
        for it in il.get("issues") or []:
            if it.get("id") != "ISS-285":
                continue
            hit += 1
            if it.get("status") != "fixing":
                raise SystemExit("★ISS-285 status 不是 fixing (=%s) ⇒ 拒绝落账" % it.get("status"))
            it["note"] = (it.get("note") or "") + NOTE
            it["dispatched_at"] = TODAY
            it["task_brief"] = BRIEF_HEAD + (it.get("task_brief") or "")
        if hit != 1:
            raise SystemExit("★ISS-285 不唯一 (命中 %d 条) ⇒ 拒绝落账" % hit)

        dl.setdefault("dispatches", []).append({
            "issue": "ISS-285",
            "agent": "sw-lead",
            "at": TODAY,
            "brief": BRIEF_HEAD.strip(),
        })

        atomic_write(IL, il)
        atomic_write(DL, dl)
    print("★落账 OK: ISS-285 保持 fixing + note 追加 + dispatch_log 追加 1 条 (续做重派)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
