#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (fb67af40 队列自动派活) 2026-11-16 18:4x: ISS-246 第二次僵尸 fixing 复记
=========================================================================================
★**本脚本只做一件事 (不碰任何真源 / 分片 / 板 / 台账 / 交卷单)** ★
  给 ISS-246 的 `note` 追加一段【第二次僵尸 + 断点定位 + 本轮续做范围】的留痕
  (★status 保持 fixing ⇒ 下一轮 cron 的 in_flight 规则会跳过 mech-lead ⇒ 不撞车★)

★**实测依据 (★main 2026-11-16 18:3x~18:4x 自己实跑/实读, 不抄任何交卷报告★)** ★★
★**A) 第二次僵尸会话** ★
· 子会话 `agent:mech-lead:subagent:47d879b5-3766-453c-80c4-035d30c095ac` (session f16f4296)
  18:11:11 → 18:14:12 (579s) ⇒ ★**status=timeout · abortedLastRun=true** ⇒
  transcript 末条 = 「**Aborted**」(★不是 file lock stale★) ⇒ 死在 B2~B6 填充之前
· ⇒ ★**同一单 (ISS-246) 连续两次会话都被 abort (460s / 579s) ⇒ 本轮派活必须【极窄】★
  (★只补交卷单残段 + 分片 + 验收, 不许重跑已完成的落表与沙盒自证★)

★**B) 盘上真实断点 (main 自己逐项复核过)** ★
· ★**已完成①**: `MECH/HW_CROSS_REVIEW_TRIAGE.md` 第 3 跳重锚已落 (mtime **17:43**)
  ⇒ main 18:39 实跑 `python3 MECH/check_demo_struct_truth.py` ⇒ ★**rc=0 · 23/23 · FAIL 0 组** ★
  ⇒ main 18:39 实跑 `--selftest` ⇒ ★**rc=0 · 14/14 抓到了** ★
· ★**已完成②**: 沙盒反向自证 ★**已跑完** ⇒ `/tmp/iss246_mech/stepA.log` (★**23/23 FAIL 0**★)
  / `stepB.log` (★**21/23 FAIL 2** = 锚点回滚后 G5b+C21 真红★) / `stepC.log` (★**23/23 FAIL 0**★)
  ⇒ ★**绿 → 红 → 绿 三步证据在盘上, 不用重跑★**
· ★**已完成③**: 交卷单骨架 + ★**B0 一句话 + B1 结论摘要 (11 行) 已填** ★
  (`HANDOFF/2026-11-16_mech-lead_ISS245_MECH侧H1重锚第3跳.md` · 8816 B · mtime 18:17)
· ★**缺 3 件 (★本轮只干这 3 件★)**: ★**① B2 / B3 / B4 / B5 / B6 / ★附 交卷物清单 6 段全是
  「(★填内容中★)」** ★ · ★**② `state/fragments/mech.yaml` 里 0 处 ISS-246** (mtime 13:06) ★
  · ★**③ 交卷前 `merge.py` + `gate_check.py` 的自证输出没贴进交卷单** ★
  (main 18:39 已代跑: merge rc=0 · gate_check rc=0 · ★**Q1 18/18**★ ⇒ 基准绿, 不许再退)
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261116_1845_iss246_zombie2"

NOTE = """
★2026-11-16 18:4x 队列自动派活 job (fb67af40) **第二次僵尸 fixing 复记 + 极窄续做重派**: ★**上一轮本 job 18:11 spawn 的子会话也 abort 了** ⇒ 子会话 `agent:mech-lead:subagent:47d879b5-3766-453c-80c4-035d30c095ac` (session f16f4296) 18:11:11 → 18:14:12 (579s) · status=timeout · abortedLastRun=true · transcript 末条 = 「Aborted」 ⇒ ★**同一单连续两次被 abort (460s / 579s) ⇒ 本轮派活【极窄】: 只补 3 件, 不许重跑已完成的落表与沙盒自证** ★ ⇒ ★**盘上现状 (main 18:3x~18:4x 自己实跑/实读复核, 不抄交卷报告)**: ★**已完成 3 项**: ① 落表已落 (`MECH/HW_CROSS_REVIEW_TRIAGE.md` mtime 17:43 · main 实跑 `check_demo_struct_truth.py` ⇒ rc=0 · 23/23 · `--selftest` ⇒ rc=0 · 14/14) ② 沙盒反向自证已跑完 (`/tmp/iss246_mech/stepA.log` 23/23 → `stepB.log` 21/23 FAIL 2 → `stepC.log` 23/23) ③ 交卷单骨架 + B0 + B1 (11 行) 已填 (8816 B · mtime 18:17) ⇒ ★**缺 3 件 (本轮只干这 3 件)**: ① 交卷单 B2/B3/B4/B5/B6/★附 交卷物清单 6 段仍是「(★填内容中★)」 ② `state/fragments/mech.yaml` 里 0 处 ISS-246 (mtime 13:06) ③ merge+gate_check 自证输出没贴进交卷单 (main 18:39 代跑: merge rc=0 · gate_check rc=0 · Q1 18/18 ⇒ 基准绿, 不许再退) ⇒ ★**本 job 续做重派 (runTimeout 5400s) ⇒ 续做硬规矩块已写进 brief (★先落交卷单再填内容·分片第 2 步·验收第 3 步·不许再动 §3.1 锚点数字★)** ⇒ ★**status 保持 fixing (下一轮 cron 的 in_flight 规则会跳过这个 agent ⇒ 不撞车)** ★
"""


def main():
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        log = yaml.safe_load(open(LOG, encoding="utf-8"))
        touched = []
        for it in log.get("issues") or []:
            if it.get("id") != "ISS-246":
                continue
            if it.get("status") != "fixing":
                print("⚠ ISS-246 status=%s (不是 fixing) ⇒ 幂等跳过" % it.get("status"))
                fcntl.flock(lk, fcntl.LOCK_UN)
                return
            it["note"] = (it.get("note") or "") + NOTE
            it["dispatched_at"] = "2026-11-16"
            touched.append("ISS-246")
        if not touched:
            print("⚠ 没有可复记的 ⇒ 未写盘")
            fcntl.flock(lk, fcntl.LOCK_UN)
            return
        shutil.copy2(LOG, BAK)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("备份: %s" % BAK)
    for iid in touched:
        print(" - %s note 追加第二次僵尸复记, status 保持 fixing" % iid)


if __name__ == "__main__":
    main()
