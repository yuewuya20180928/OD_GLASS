#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main (fb67af40 队列自动派活) 2026-11-16 18:4x: ISS-246 第二次续做重派 · dispatch_log 记账
=========================================================================================
★**只往 state/dispatch_log.yaml 追加一条重派记录 (不碰 issue_log / 真源 / 分片 / 板 / 台账)** ★
"""
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DLOG = os.path.join(HERE, "dispatch_log.yaml")
BAK = DLOG + ".bak_20261116_1845_iss246_cont2"

ENTRY = {
    "issue": "ISS-246",
    "agent": "mech-lead",
    "at": "2026-11-16",
    "redispatch": True,
    "reason": (
        "★**第二次僵尸** (★main 2026-11-16 18:3x~18:4x 自己实跑/实读核出来, 不抄交卷报告★): "
        "上一轮本 job 18:11 spawn 的子会话 `agent:mech-lead:subagent:47d879b5-3766-453c-80c4-035d30c095ac` "
        "(session f16f4296) 18:11:11 → 18:14:12 (579s) ⇒ status=timeout · abortedLastRun=true · "
        "transcript 末条 = 「Aborted」 ⇒ 死在 B2~B6 填充之前 ⇒ "
        "★**同一单连续两次被 abort (460s / 579s) ⇒ 本轮派活必须【极窄】** ★\n"
        "★**盘上断点 (main 自己复核)**: ✅落表已落 (`MECH/HW_CROSS_REVIEW_TRIAGE.md` mtime 17:43 · "
        "main 实跑 `check_demo_struct_truth.py` ⇒ rc=0 · 23/23 · `--selftest` ⇒ rc=0 · 14/14) "
        "✅沙盒反向自证已跑完 (`/tmp/iss246_mech/stepA.log` 23/23 → `stepB.log` 21/23 FAIL 2 → "
        "`stepC.log` 23/23) ✅交卷单骨架 + B0 + B1 (11 行) 已填 (8816 B · mtime 18:17) ⇒ "
        "★**缺 3 件 (本轮只干这 3 件)**: ① 交卷单 B2/B3/B4/B5/B6/★附 6 段仍是「(★填内容中★)」 "
        "② `state/fragments/mech.yaml` 里 0 处 ISS-246 (mtime 13:06) "
        "③ merge+gate_check 自证输出没贴进交卷单 (main 18:39 代跑: merge rc=0 · gate_check rc=0 · Q1 18/18) ★"
    ),
    "brief": (
        "★**极窄续做 (★只补 3 件, 严禁重跑已完成的活★)**: "
        "① 填完交卷单 `HANDOFF/2026-11-16_mech-lead_ISS245_MECH侧H1重锚第3跳.md` 的 6 段 "
        "(B2 自评 / B3 证据分级 / B4 接口取值声明 / B5 验收原样输出 / B6 边界审计 / ★附 交卷物清单) "
        "—— 沙盒三步直接引用 stepA/B/C.log 原样输出, 不许重跑 ⇒ "
        "② `state/fragments/mech.yaml` 走 `python3 state/frag_write.py --agent mech-lead` 原子写 "
        "(artifact ×2 + interface_claim + 给 main 的复核 need) ⇒ "
        "③ 交卷前 merge.py (rc=0) && gate_check.py (Q1 18/18) 贴进 B5 ④ + 把三份沙盒 log 拷进 HANDOFF/ 留档 + 删 /tmp/iss246_mech/sandbox/ ⇒ "
        "★**三条硬禁止**: 不许再动 §3.1 锚点数字 (main 18:39 已绿, 再动 C21 会红) / 不许碰 `check_demo_struct_truth.py` "
        "(md5 `fa9b59e5…` 前后不变) / 不许碰 HW/ 与别人分片 ⇒ ★**时间纪律**: 骨架先落盘 → 逐段填 → 分片 → 验收贴盘 → 交卷 ★"
    ),
    "session_key": "agent:mech-lead:subagent:844a5b10-9c4b-4945-966d-3239cad54b29",
    "run_id": "90f8fefc-9448-4b1c-a0ec-f00e4b6abf6b",
    "task_name": "queue_iss246_cont2",
    "run_timeout_s": 5400,
    "spawned_by": "fb67af40(本 job)",
    "status_at_spawn": "fixing (保持 ⇒ 下一轮 cron 的 in_flight 规则跳过 mech-lead ⇒ 不撞车)",
}


def main():
    d = yaml.safe_load(open(DLOG, encoding="utf-8")) or {}
    disp = d.setdefault("dispatches", [])
    if any(e.get("run_id") == ENTRY["run_id"] for e in disp if isinstance(e, dict)):
        print("⚠ 该 run_id 已在 dispatch_log ⇒ 幂等跳过")
        return
    shutil.copy2(DLOG, BAK)
    disp.append(ENTRY)
    tmp = DLOG + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(d, f, allow_unicode=True, sort_keys=False, width=200)
    os.replace(tmp, DLOG)
    print("备份: %s" % BAK)
    print(" - ISS-246 → mech-lead 第 2 次续做重派已记账 (run_id %s)" % ENTRY["run_id"])


if __name__ == "__main__":
    main()
