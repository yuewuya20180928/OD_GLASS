#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★**cron fb67af40 (ARS45 队列自动派活) · 2026-11-18 21:2x · ISS-332 cont1 (sw-lead) + ISS-333 cont2 (mech-lead) 续做重派** ★

★**为什么派这两条 (★逐条都是本机实跑读数·不抄任何 agent 报告★)**:
  ① `state/advance.py --json` ⇒ internal = [] (三个总工名下零 open ⇒ A 段真空 ⇒ 本轮全是【续做】)
  ② 跨 job 查活 (★看 `~/.openclaw/agents/<agent>/sessions/*.jsonl` 的 mtime·★再等 20s 复核是否还在写★):
     - sw-lead   21:05:32 (静止) ⇒ ★**会话最后一条 = assistant `stopReason: error`
       `errorMessage: "invalid params, context window exceeds limit (2013)"`** ⇒ ★**上下文爆掉·真僵尸** ★
     - mech-lead 21:00:46 (静止) ⇒ ★**会话最后一条 = `openclaw:prompt-error` "This operation was aborted"** ⇒ ★**真僵尸** ★
     - hw-lead   19:46:54 (会话死) ⇒ ★**但后台链还活着**:
       PID 1130618 `bash tmp/iss328/run_ru_arm.sh` + PID 1130654 `state/gen_pcb_netlist_board.py` (R 状态, etimes 6571s)
       + `tmp/iss328/ru_R.gen.log` 21:12:37 仍在长 ⇒ ★**不许重派** (活链期间重派 = 两个 agent 抢同一个分片) ★
  ③ 僵尸鉴别 (★不是只看 status=fixing★): 两单成果**部分在盘**
     - ISS-332 在盘: `SW/tools/check_sw_ref_reachability_v2.py` (45,339 B · 21:05:29 · main 21:1x 实跑 rc=0)
                     + `--selftest` 7/7 通过 + `logs/iss332/` 12 件 (4 RT + 3 CTL 真件读数 + repro 脚本)
       缺: ★**`check_sw_ref_reachability_v2_selftest.py` 不存在** ★ + **交卷页不存在** ★ + **分片命中 0** ★ + 挂闸写法三问没写
       ★★**main 21:2x 本机实跑 `python3 logs/iss332/iss332_repro.py --with-v2` ⇒ v2 现在【抓不住】那 4 条洗白面**
          (RT-5~RT-8 实际[v2] 全 rc=0, 期望 rc=1 ⇒ 「不符」; CTL-1~CTL-3 仍 rc=1 ⇒ 没把闸调死)
          ⇒ ★**⇒ v2 只做了一半 ⇒ cont1 的第一个动作 = 把 4 条洗白面抓住** ★
     - ISS-333 在盘: `MECH/tools/check_mech_ref_reachability.py` (56,550 B · 19:36 · main 20:4x 实跑 --selftest rc=0 · 14/14)
                     + `logs/iss333/` 11 件 (含 cont1 补的 3 件 posthook rc)
       缺: ★**交卷页不存在** ★ + **分片命中 0** ★
       ★★**main 20:2x 已把这道闸挂进 `state/gate_check.py` 的 EXTRA_GATES (ISS-330 owner=main·已落 fixed)**
          ⇒ ★**⇒ 闸脚本一个字节都不许改 ⇒ cont2 只补【交卷页 + 分片】** ★

★**纪律**: 零写板 · 零落表 · 零改闸 · 零改 agent 的分片 · 零外发 · 不替老板拍板 · 不自签 agent 的单
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
NOW = "2026-11-18 21:2x"
STAMP = "20261118_2120_cronfb67_iss332_cont1_iss333_cont2"

BRIEF_332_CONT = open(
    os.path.join(HERE, "dispatch_briefs", "ISS-332_sw_ref_reach_launder_reverse_cases_cont1.md"),
    encoding="utf-8",
).read()

BRIEF_333_CONT = open(
    os.path.join(HERE, "dispatch_briefs", "ISS-333_mech_designator_gate_hook_prep_cont2.md"),
    encoding="utf-8",
).read()

BRIEF_332 = (
    "★★**cont1 续做 (★不是从零·是【把上一趟的半成品补完】★) · 2026-11-18 21:2x · cron fb67af40 (ARS45 队列自动派活)** ★ ★"
    "★**为什么派 (★本机实跑读数★)**: "
    "★**① 上一趟会话 21:05:32 死于 `context window exceeds limit (2013)` ⇒ 会话没了, 但成果大部分在盘** ★ "
    "★**② 在盘**: `SW/tools/check_sw_ref_reachability_v2.py` (45,339 B · 21:05:29 · main 21:1x 实跑 rc=0 · `--selftest` 7/7 通过) "
    "+ `logs/iss332/` 12 件 (4 条 RT + 3 条 CTL 的真件读数 + 自带 `--with-v2` 入口的 repro 脚本) + `tmp/iss332/sb_base/` 沙盒 ★ "
    "★**③ 缺**: ★**新建★ `SW/tools/check_sw_ref_reachability_v2_selftest.py` **不存在** + ★**新建★ 交卷页 **不存在** + "
    "`grep -c iss332 state/fragments/sw.yaml` = **0** + 挂闸/切换写法三问没写 ★ "
    "★**④ ★★最要紧的一条★★: main 21:2x 本机实跑 `python3 logs/iss332/iss332_repro.py --with-v2` ⇒ "
    "**v2 现在【抓不住】那 4 条洗白面** (RT-5~RT-8 实际[v2] 全 rc=0 / 期望 rc=1 ⇒ 「不符」; CTL-1~CTL-3 仍 rc=1 ⇒ 没把闸调死) "
    "⇒ ★**⇒ v2 只做了一半 ⇒ cont1 的第一个动作 = 把 4 条洗白面抓住 (判据方向不许变·不许新加豁免规则来合法放过)** ★ "
    "★**⑤ 抗上下文护栏 (★上一趟就是死在这上面★)**: 不许通读 v2 全文 (900 行) ⇒ 用 grep -n 定位 · 不许把大文件整段贴回对话 · "
    "一次 write ≤ 3000 字 ⇒ 先写骨架再 edit · 不许重跑已在盘的复现 · 回复 ≤ ~800 字 ★ "
    "★**任务书全文**: `state/dispatch_briefs/ISS-332_sw_ref_reach_launder_reverse_cases_cont1.md` "
    "(7,910 B · ★`check_brief_commands.py --brief-file` rc=0★) ★ "
    "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075 · mtime 必须仍 2026-11-06 07:07:17.362193413) · 零落表 · "
    "★**零改真件 `SW/tools/check_sw_ref_reachability.py`** (链上那道闸) · 零改 `state/gate_check.py` · 零改 `SW/SW_MD5_BASELINE_LEDGER.md` · "
    "沙盒只写 `tmp/iss332/` + `logs/iss332/` · 只写 `state/fragments/sw.yaml` "
    "★**零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信 ⇒ 没有「批一句可以发」这个选项)★** · 不替老板拍板 · 不自签 `state/issue_log.yaml` ★"
)

BRIEF_333 = (
    "★★**cont2 续做 (★只补【交卷两件套】★) · 2026-11-18 21:2x · cron fb67af40 (ARS45 队列自动派活)** ★ ★"
    "★**为什么派 (★本机实跑读数★)**: "
    "★**① cont1 会话 21:00:45 被掐 (最后一条 = `openclaw:prompt-error`「This operation was aborted」) ⇒ 成果在盘但没人收卷** ★ "
    "★**② 在盘**: `MECH/tools/check_mech_ref_reachability.py` (56,550 B · 19:36 · ★main 20:4x 实跑 `--selftest` ⇒ rc=0 · 反向用例 14/14 (MC-1~MC-14) 通过★) "
    "+ `logs/iss333/` 11 件 (含 cont1 补的 3 件 posthook rc) ★ "
    "★**③ 缺**: ★**新建★ 交卷页 `HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md` **不存在** + "
    "`grep -c iss333 state/fragments/mech.yaml` = **0** (分片一字没写) ★ "
    "★**④ ★★最要紧的一条★★: main 20:2x 已把这道闸挂进 `state/gate_check.py` 的 `EXTRA_GATES` (ISS-330 owner=main · 已落 fixed) "
    "⇒ ★**⇒ 闸脚本一个字节都不许改 (改了链上那道闸就与盘面不一致⇒全项目门禁失真) ⇒ 本单只补【交卷页 + 分片】** ★ "
    "★**⑤ ★★上一趟就是死在【多余探查】上 (21:00 前它还在 dump J_CHG_SELECTION 分类) ⇒ 这一趟不许做任何新的探查/分析, "
    "读数全部从 `logs/iss333/` 引** ★ "
    "★**⑥ 文档纪律**: `MECH/**/*.md` 现在是这道闸的扫描面 ⇒ 交卷页必须放 `HANDOFF/` (不在扫描面里) · MECH 域文档一律写 `logs/iss333/` ★ "
    "★**⑦ 看链上那道闸 ⇒ 跑 `python3 state/gate_check.py --json` (★`extra_gates` 只在 `--json` 里打印·默认 stdout 不打·★别找错地方)★** ★ "
    "★**任务书全文**: `state/dispatch_briefs/ISS-333_mech_designator_gate_hook_prep_cont2.md` "
    "(6,589 B · ★`check_brief_commands.py --brief-file` rc=0★) ★ "
    "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075) · 零落表 · ★**零改 `MECH/tools/check_mech_ref_reachability.py`** · "
    "零改 `state/gate_check.py` · 零改 `SW/tools/check_sw_ref_reachability.py` · 零改既有 `MECH/**/*.md` 正文 · 零改既有 `MECH/**/*.py` · 零改 `logs/iss326/` · "
    "沙盒只写 `tmp/iss333/` + `logs/iss333/` · 只写 `state/fragments/mech.yaml` "
    "★**零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02)★** · 不替老板拍板 · 不自签 `state/issue_log.yaml` ★"
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

        # ── ISS-332 cont1 (★status 保持 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 不会重复派★) ──
        i332 = idx.get("ISS-332")
        if not i332:
            print("· ISS-332 不存在 (异常)")
            return 1
        tb = i332.get("task_brief") or ""
        if "ISS-332 · sw-lead · ★★cont1 续做单" not in tb:
            i332["task_brief"] = tb + "\n\n---\n\n" + BRIEF_332_CONT
            applied.append("ISS-332 task_brief += cont1 (★原 brief 全文保留★) · status 保持 fixing")
        else:
            applied.append("ISS-332 cont1 已在 brief 里 (跳过·幂等)")
        if i332.get("status") != "fixing":
            i332["status"] = "fixing"
            applied.append("ISS-332 status → fixing (★兜底★)")
        i332["dispatched_at"] = NOW
        i332["note"] = (
            str(i332.get("note") or "")
            + " ★★2026-11-18 21:2x · cron fb67af40 重派 cont1★★ "
            "★**上一趟 21:05:32 死于 `context window exceeds limit (2013)` ⇒ 成果在盘但没交卷 "
            "(★v2 脚本在·但 selftest/交卷页/分片都缺★) "
            "⇒ ★**main 21:2x 实跑 `logs/iss332/iss332_repro.py --with-v2` ⇒ v2 现在抓不住那 4 条洗白面 (RT-5~RT-8 实际全 rc=0) "
            "⇒ ★**cont1 第一动作 = 把 4 条洗白面抓住 + 补 selftest/交卷页/分片** ★"
        )
        applied.append("ISS-332 dispatched_at / note 已更新")

        # ── ISS-333 cont2 (★status 保持 fixing ⇒ 无 open 窗口★) ──
        i333 = idx.get("ISS-333")
        if not i333:
            print("· ISS-333 不存在 (异常)")
            return 1
        tb = i333.get("task_brief") or ""
        if "ISS-333 · mech-lead · ★★cont2 续做单" not in tb:
            i333["task_brief"] = tb + "\n\n---\n\n" + BRIEF_333_CONT
            applied.append("ISS-333 task_brief += cont2 (★原 brief 全文保留★) · status 保持 fixing")
        else:
            applied.append("ISS-333 cont2 已在 brief 里 (跳过·幂等)")
        if i333.get("status") != "fixing":
            i333["status"] = "fixing"
            applied.append("ISS-333 status → fixing (★兜底★)")
        i333["dispatched_at"] = NOW
        i333["note"] = (
            str(i333.get("note") or "")
            + " ★★2026-11-18 21:2x · cron fb67af40 重派 cont2★★ "
            "★**cont1 21:00:45 被掐 (prompt-error「aborted」) ⇒ 闸脚本 + 11 件证据在盘, 但交卷页/分片仍缺 "
            "⇒ ★**main 20:2x 已把这道闸挂进 `state/gate_check.py` 的 EXTRA_GATES ⇒ 本单不许再改那道闸 "
            "⇒ ★**cont2 只补【交卷页 + 分片】· 且不许做新的探查 (★上一趟就死在多余探查上★)** ★"
        )
        applied.append("ISS-333 dispatched_at / note 已更新")

        log["issues"] = issues
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=10**6))

        # ── dispatch_log 追加 ──
        dlog = yaml.safe_load(open(DLOG, encoding="utf-8")) or {}
        entries = dlog.get("dispatches") or []
        for issue, agent, brief, mark in (
            ("ISS-332", "sw-lead", BRIEF_332, "cont1"),
            ("ISS-333", "mech-lead", BRIEF_333, "cont2"),
        ):
            if not any(
                e.get("issue") == issue and mark in str(e.get("brief") or "") for e in entries
            ):
                entries.append(
                    {
                        "issue": issue,
                        "agent": agent,
                        "at": "2026-11-18",
                        "brief": brief,
                        "job": (
                            "cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 21:2x · "
                            "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"
                        ),
                    }
                )
                applied.append("dispatch_log.yaml += %s %s 1 条" % (issue, mark))

    for a in applied:
        print("·", a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
