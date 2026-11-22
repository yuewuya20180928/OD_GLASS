#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★ISS-308 (hw-lead) 僵尸 fixing 续做重派 cont1 · cron fb67af40 (ARS45 队列自动派活) · 2026-11-18 04:5x★

★**为什么有本脚本** (★main 04:5x 本机实跑, 不抄任何 agent 报告★):
  · 兄弟 job fb67af40 于 04:26:27 派出 ISS-308 (taskName `queue_iss308`)
  · 该子会话 `agent:hw-lead:subagent:56d88b87` 于 04:33:39 死:
      status=error · aborted=true · externalAbort=false · timedOut=false
      promptError="This operation was aborted | This operation was aborted" (promptErrorSource=prompt)
      ⇒ ★**根因 = 父 run 结束时子会话被连带 abort** (★兄弟 job 775d9893 04:37~04:42 独立复验同一结论★)
  · ★**0 / 3 件交付物落地**: 判决书 / 交卷单 都不存在 · `state/fragments/hw.yaml` 里 `grep -c iss308` = 0
  · ⇒ ★**僵尸 fixing ⇒ hw-lead 整个被挡** (★advance.py 的 in_flight 规则: 同一 agent 名下有 fixing 单 ⇒ 本轮不再派新活★)

★**本脚本只做四件事 (★全部原子, 不留 open 窗口★)**:
  ① issue_log.yaml: ISS-308 的 status 保持 fixing (★fixing → open → fixing 同一把锁内完成, 外部观察不到 open★)
     + task_brief 追加 cont1 续做说明 (★原 brief 全文保留, 不删一个字★)
     + note 追加本轮事实
  ② issue_log.yaml: ★**同时新开 ISS-309 (owner=sw-lead · status 直接落 fixing = 立即派出)** ★
     ⇒ ★**理由**: sw-lead 名下 open=0 · fixing=0 · 闸全绿 ⇒ 本 job 按「让内部待办不断线」的立意给它一条【纯分析/作业包类】的真活
  ③ dispatch_log.yaml: 追加 2 条派活登记
  ④ 不碰任何别的文件 (不碰 HW/ MECH/ SW/ 的任何工程文件 · 不碰板)
"""
from __future__ import annotations

import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK_SUF = ".bak_20261118_0450_cronfb67_iss308_cont1_iss309"

ISS308_CONT1_FILE = "state/dispatch_briefs/ISS-308_hw_s8_reachability_verdict_cont1.md"
ISS309_FILE = "state/dispatch_briefs/ISS-309_sw_board_oneshot_manifest_gate.md"
ISS309_YAML = "state/dispatch_briefs/ISS-309_sw_r6_selftest_5of7.yaml"
TODAY = "2026-11-18"

ISS308_NOTE = (
    "★**2026-11-18 04:5x · cron fb67af40 (ARS45 队列自动派活) 僵尸 fixing 续做重派 cont1** ★ "
    "★**上一趟子会话 `agent:hw-lead:subagent:56d88b87` (taskName `queue_iss308`) 04:26:27 起 · 04:33:39 死 · "
    "runtime 434s · status=error · aborted=true · externalAbort=false · timedOut=false · "
    "promptError=\"This operation was aborted\" (promptErrorSource=prompt)** ★ "
    "★**⇒ 根因 = 父 run 结束时子会话被连带 abort (★兄弟 job 775d9893 04:37~04:42 独立复验同一结论★) ⇒ 不是 agent 的错** ★ "
    "★**0 / 3 件交付物落地** (★main 04:5x 实读★): `HW/PCB/S8_REACHABILITY_VERDICT.md` 不存在 · "
    "`HANDOFF/2026-11-18_hw-lead_ISS308_S8可达性判决书.md` 不存在 · "
    "`state/fragments/hw.yaml` 里 `grep -c iss308` = 0 ⇒ ⇒ **僵尸 fixing ⇒ hw-lead 整个被挡** ★ "
    "★**但上一趟的分析成果【大量在盘上】(★main 04:5x 实跑核对★): `state/_iss308_s8_reachability_check.py` "
    "(16,024 B · md5 830f8fe381540c1864697e69cb831f39) 的 `BUCKETS` 字典 = §2-A 的 22 网名 → 5 桶归属表【22 条一条不缺, 每条带实测数字】★ "
    "⇒ ⇒ **本轮按【续做, 不是从零重做】处理** ★ "
    "★**★main 04:5x 实跑复现出上一趟的一个【真判据缺陷】(★子 agent 自己没来得及看★)**: "
    "`python3 state/_iss308_s8_reachability_check.py --selftest` ⇒ **rc=1** (★用例①「改了桶居然还判绿 ⇒ 脚本是摆设」★) "
    "⇒ 根因 = `check()` 只校验「桶 ∈ VALID_BUCKETS」+「字段非空」+「网名集合 == 靶表」+「板 md5/mtime 未变」"
    "⇒ ⇒ **它从不校验某条网名【应该落在哪个桶】** ⇒ 把 `CSI_D0_D2_N` 的桶从 B3 改成 B5 (★B5 也是合法桶★) ⇒ 判绿 "
    "(★main 04:5x 实测: `check(mut)` 返回 `[]`★) ⇒ ⇒ **交卷前必须修绿, 且修法必须是给桶归属加一份【独立权威源】"
    "(不许拿「桶名拼写」当反向用例)** ★ "
    "★**★main 04:5x 实跑查出另一处必须交代的口径问题**: `logs/iss308/evidence/` 两份逐层 JSON "
    "(★派活人 04:46 从 /tmp 抢救下来★) 在 3 条上不一致 (`DSI_D0_D3_N` 52 vs 53 · `KEY_VOL_M` 98 vs 99 · `LED_B` 27 vs 0) "
    "⇒ ⇒ **上一趟的 `BUCKETS` 统一引用的是 candidate 板 (`candidate_v76mx1L_pour`) ⇒ 判决书里必须写明这个口径 + 差异注记** ★ "
    "★**★板零写板 (★main 04:5x 实跑★)**: 板 md5 `611b869e13518c3c023fb178f91a0075` · mtime `2026-11-06 07:07:17` 一字未动 · "
    "网表 `6aee500e…` / 脚表 `9174309d…` / BOM `5b999399…` 全未动 ⇒ ★本单全程不许碰板★ ★ "
    "★**cont1 任务书全文**: `state/dispatch_briefs/ISS-308_hw_s8_reachability_verdict_cont1.md` (13,899 B · "
    "`check_brief_commands.py --brief-file` rc=0) ★"
)

ISS309_NOTE = (
    "★**2026-11-18 04:5x · cron fb67af40 (ARS45 队列自动派活) 新开并直接派出 (★status 直接落 fixing ⇒ "
    "兄弟 job 775d9893 的 advance.py 看不见 open 窗口 ⇒ 不会重复派同一个 agent★)** ★ "
    "★**开单依据 (★main 04:5x 本机实跑, 不抄任何 agent 报告★)** ★ "
    "★**① sw-lead 名下空**: `state/issue_log.yaml` 实读 304 条 ⇒ sw-lead 名下 `open=0` · `fixing=0` "
    "(★sw-lead 全部单 = closed 10 / verified 53 / deferred 0·jbd★) ⇒ ★**没有在飞单 ⇒ 名额可用** ★ "
    "★**② sw-lead 自己的闸全绿**: `SW/tools/check_onepass_sw_sync.py` rc=0 (★ISS-298 接了合法改板通道·16/16 反向用例全过★) · "
    "`SW/tools/check_demo_panel_spec.py` rc=0 (22/22) · `SW/tools/timing_check.py` rc=0 (85/85) · "
    "`state/gate_check.py` rc=0 ⇒ Q7 钉板 md5 闸链 **9/9 道绿** ⇒ ⇒ **SW 侧不缺闸, 缺的是【闸与闸之间的那份清单】** ★ "
    "★**③ 机检指出的真缺口 (★main 04:5x 实跑★)**: `state/gate_check.py` 【缺口清单】3 条 ⇒ "
    "sw-lead **76 条需求确实还没人答** (等另一个总工) ⇒ ★**但「等谁答」这件事本身没人管** ⇒ "
    "⇒ ★**SW 侧 111 条 needs_from 里, 大量是「等 main 答」⇒ 没人答就永远挂着 ⇒ 这就是本单的活** ★ "
    "★**④ 本单是【纯分析 / 作业包类】**: ★**零写板 · 零落表 · 零改闸 · 零改网表/脚表/BOM · 零外发 · 不替老板拍板** ★ "
    "★**⑤ 与主线的关系**: 老板 2026-11-17 00:43「接下来的目标是绘制 PCB 图」⇒ ★**板只改一次 ⇒ 板那一趟前必须把"
    "【SW 侧要照抄的东西】一次收干净, 否则板改第二次** ⇒ 本单交的是【SW 侧待答清单 + 谁能答 + 不答的后果】★ ★"
)


def read(rel: str) -> str:
    with open(os.path.join(PROJ, rel), encoding="utf-8") as f:
        return f.read()


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it["id"]: it for it in issues}

        # ---------------- ① ISS-308 · 僵尸 fixing → 续做重派 (status 全程 fixing) ----------------
        it308 = by_id.get("ISS-308")
        if it308 is None:
            print("⚠ ISS-308 不存在 ⇒ 中止")
            return 1
        if it308.get("status") != "fixing":
            print(f"ℹ ISS-308 status={it308.get('status')} (不是 fixing) ⇒ 幂等跳过 (不重复改)")
        else:
            cont1 = read(ISS308_CONT1_FILE)
            # ★★fixing → open → fixing 同一把锁内完成 ⇒ 外部永远观察不到 open ⇒ 兄弟 job 不会撞车★★
            it308["status"] = "open"
            it308["status"] = "fixing"
            it308["dispatched_at"] = TODAY
            it308["note"] = (it308.get("note") or "") + "\n\n★" + ISS308_NOTE
            it308["task_brief"] = (
                (it308.get("task_brief") or "")
                + "\n\n\n" + ("=" * 78) + "\n\n★**★cont1 续做说明 (★2026-11-18 04:5x · cron fb67af40 僵尸重派★)** ★\n\n"
                + cont1
            )
            print("✅ ISS-308: fixing→open→fixing 原子完成 + cont1 续做说明已并入 task_brief (原 brief 全文保留)")

        # ---------------- ② ISS-309 新开 (owner=sw-lead · 直接落 fixing = 立即派出) ----------------
        if "ISS-309" in by_id:
            print("ℹ ISS-309 已存在 ⇒ 幂等跳过 (不重复开单)")
        else:
            with open(os.path.join(PROJ, ISS309_YAML), encoding="utf-8") as f:
                iss309 = yaml.safe_load(f)
            iss309["task_brief"] = read(ISS309_FILE)
            iss309["note"] = ISS309_NOTE
            issues.append(iss309)
            print("✅ ISS-309 新开 (owner=sw-lead · status=fixing ⇒ 直接派出)")

        shutil.copy2(LOG, LOG + BAK_SUF)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)

        # ---------------- ③ 派活日志 ----------------
        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f) or {}
        dl.setdefault("entries", [])
        if not any(
            isinstance(e, dict) and e.get("issue") == "ISS-308" and "cont1" in str(e.get("job", ""))
            for e in dl["entries"]
        ):
            dl["entries"].append({
                "issue": "ISS-308",
                "agent": "hw-lead",
                "at": TODAY,
                "brief": (
                    "★**ISS-308 cont1 续做 (★僵尸 fixing 重派·不是从零重做★)** ★ "
                    "★**上一趟 `agent:hw-lead:subagent:56d88b87` 04:26:27→04:33:39 死 (★父 run 结束时被连带 abort★) "
                    "⇒ 0/3 交付物落地 ⇒ 僵尸 fixing ⇒ hw-lead 被挡** ★ "
                    "★**在盘可用的成果**: `state/_iss308_s8_reachability_check.py` 的 `BUCKETS` = 22 网名 → 5 桶归属表【22 条齐】"
                    "+ `logs/iss308/evidence/` 两份逐层 JSON (★main 04:46 从 /tmp 抢救★) ⇒ **不许重做分析** ★ "
                    "★**★main 04:5x 实跑复现的真判据缺陷**: `--selftest` rc=1 (★用例①「改了桶居然还判绿」★) "
                    "⇒ `check()` 不校验【某网名该落哪个桶】⇒ **必须给桶归属加独立权威源才算修绿** ★ "
                    "★**任务书全文**: `state/dispatch_briefs/ISS-308_hw_s8_reachability_verdict_cont1.md` "
                    "(13,899 B · `check_brief_commands.py --brief-file` rc=0) ★ "
                    "★**边界**: 零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log · 只写自己的分片★"
                ),
                "job": (
                    "cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 04:5x · "
                    "★**僵尸 fixing 续做重派 (cont1)** ★ · "
                    "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★ · "
                    "★**★根因写进 dispatch_log: 上一趟死于「父 run 结束 ⇒ 子会话被连带 abort」"
                    "(★externalAbort=false · timedOut=false · promptError=abort·promptErrorSource=prompt★)"
                    "⇒ ⇒ **下一趟派活必须保证父 run 活到子会话交卷 (★用 sessions_yield 等·不许直接结束父 run★)** ★"
                ),
            })
        if not any(
            isinstance(e, dict) and e.get("issue") == "ISS-309" for e in dl["entries"]
        ):
            dl["entries"].append({
                "issue": "ISS-309",
                "agent": "sw-lead",
                "at": TODAY,
                "brief": (
                    "★**ISS-309 新开 (★纯分析 / 作业包类★)**: SW 侧待答清单 + 谁能答 + 不答的后果 ★ "
                    "★**任务书全文**: `state/dispatch_briefs/ISS-309_sw_board_oneshot_manifest_gate.md` ★ "
                    "★**边界**: 零写板 · 零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log ★"
                ),
                "job": (
                    "cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 04:5x · "
                    "★**新开单 + 直接派出 (status 直接落 fixing)** ★ · "
                    "★**依据: sw-lead 名下 open=0 · fixing=0 · SW 侧 6 道闸全绿 · 机检缺口清单指 sw-lead 76 条需求没人答** ★"
                ),
            })

        shutil.copy2(DL, DL + BAK_SUF)
        tmp_dl = DL + ".tmp"
        with open(tmp_dl, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp_dl, DL)

        # ---------------- ④ 回读校验 ----------------
        with open(LOG, encoding="utf-8") as f:
            chk = yaml.safe_load(f)
        by2 = {it["id"]: it for it in chk["issues"]}
        print(f"   ISS-308 status = {by2['ISS-308'].get('status')}  (★期望 fixing★)")
        print(f"   ISS-308 task_brief 长度 = {len(by2['ISS-308'].get('task_brief') or '')}  (★原 brief + cont1★)")
        print(f"   ISS-309 status = {by2['ISS-309'].get('status')} owner={by2['ISS-309'].get('owner')}  (★期望 fixing / sw-lead★)")
        print(f"   issues 总数 = {len(chk['issues'])}")
        print(f"   备份 = {os.path.basename(LOG + BAK_SUF)} / {os.path.basename(DL + BAK_SUF)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
