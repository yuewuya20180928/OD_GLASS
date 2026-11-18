#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★**cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-18 23:3x · ① 签收 ISS-333 (mech-lead) ② 派 ISS-328 cont4 纯写型收卷单 (hw-lead)·零写板** ★

★**为什么是这两件 (★全部本机实跑读数·不抄任何 agent 报告★)★**:
  ① `state/advance.py --json` ⇒ `internal: []` (三个总工名下零 open ⇒ A 段真空 ⇒ 本轮全是【收卷/签收】)
  ② 兄弟 job fb67af40 22:55~23:07 那趟 **aborted** (★`stopReason: aborted` @23:07:09★) ⇒ ★**它 22:31 交回的两件 (签 ISS-333 + 重派 ISS-328 纯写型) 没人做** ⇒ 本 job 接手 (★派活前已按铁律确认 hw-lead / mech-lead / sw-lead 三个 agent 名下【零在飞写会话】★)
  ③ ISS-333: ★**盘上产物齐 + main 23:3x 本机独立复核 7 项全绿** ⇒ 具备签字条件 ⇒ 签 `fixing → verified`
  ④ ISS-328: ★**交付页已完成 (占位符 0) · 交卷页只剩 5 处 `<!-- B* -->`** ⇒ ★**3 分钟纯写型活** ⇒ 派 cont4 (★不许重跑链★)

★**ISS-333 签收依据 (★23:3x 本机实跑·不抄 agent 报告★)**:
  - `MECH/tools/check_mech_ref_reachability.py` = 56,550 B / mtime 19:36:31 ✓
  - 真件裸跑 ⇒ **rc=0 绿** (「MECH 侧引用的位号全部可达, 真隐患在基线内」) ✓
  - `--selftest` ⇒ **rc=0 · 反向用例 14/14 通过** ✓
  - 交卷页 `HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md` = 40,812 B @22:11:00 · **占位符 0** ✓
  - `grep -c iss333 state/fragments/mech.yaml` = **11** ✓
  - `logs/iss333/` = 16 件 ✓ · 沙盒 `find tmp/iss333 -type l` = **0 软链** ✓
  - 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` ⇒ 逐字节未动 ✓
  - ★**该闸已在门禁链上** (`state/gate_check.py` 的 EXTRA_GATES 第 8 道 · ★owner=main 的 ISS-330 已挂★) ⇒ 不需要再挂

★**纪律**: 零写板 · 零落表 · 零改闸 · 零改生成器代码 · 零改 agent 的分片 (★只改 issue_log / dispatch_log★) · 零外发
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
NOW = "2026-11-18 23:3x"
STAMP = "20261118_2330_cron775d_verify333_dispatch328_cont4"

BRIEF_328 = open(
    os.path.join(HERE, "dispatch_briefs", "ISS-328_hw_closout_cont4_5blocks.md"),
    encoding="utf-8",
).read()

SUMMARY_328 = (
    "★★**cont4 纯写型收卷单 · 只填交卷页 5 处 + 写 hw.yaml 分片 · 一个字节都不许重新生成** ★ ★"
    "★**为什么派 (★23:3x 本机实跑读数★)**: "
    "★**① 兄弟 job fb67af40 22:55~23:07 那趟 aborted** ⇒ ★**它 22:31 交回的「签 ISS-333 + 重派 ISS-328 纯写型」没人做** ⇒ 本 job 接手 ★ "
    "★**② 派活前已确认三个 agent 名下零在飞写会话** (★hw-lead 最后一条 22:17:15 timeout · mech-lead 最后一条 22:17:14 timeout · sw-lead 21:46:31 done★) ⇒ ★**不违「一个 agent 同时只允许一个写会话」铁律** ★ "
    "★**③ 在盘**: 交付页 `HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md` = 58,493 B @22:13:42 · ★占位符 0★ (★已完成, 一个字不许改★) · "
    "★**④ 缺**: 交卷页 `HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md` (8,156 B @22:13:52) ⇒ ★**只剩 5 处 `<!-- B* -->`** (★L72 B2_ACCEPTANCE · L78 B3_EVIDENCE · L84 B4_INTERFACE · L90 B5_OPEN · L96 B6_REPRO★) · "
    "★**⑤ 读数它自己已经算好了** (`logs/iss328/33_recalc_gate_rc.txt` @22:13 + `logs/iss328/34_cont3_readonly_recalc.txt` @22:13) ⇒ ★**照抄, 不许自己再数一遍** ★ "
    "★**⑥ ★★派活顺序铁律★★**: ★**第 1 步 = write 5 块 → 第 2 步 = 写分片 → 第 3 步 = 才跑必跑项 (`gate_check` 只许跑一次·加 timeout·不许 `--json`)** ★ "
    "★**上一趟 (cont3) 的死因 = 12 分钟全烧在跑必跑项上 ⇒ 交卷页一个字节没写** ★ "
    "★**⑦ ★★不许重跑链★★** (★禁用 `state/gen_pcb_netlist_board.py` / `state/replay_patch_chain.sh` / `state/clrfix_iter.sh` / `state/gen_pcb_routing.py` / `tmp/iss328/run_ru_arm.sh` · ★读数全部从 `logs/iss328/` 引★) ★ "
    "★**任务书全文**: `state/dispatch_briefs/ISS-328_hw_closout_cont4_5blocks.md` (★`check_brief_commands.py --brief-file` rc=0★) ★ "
    "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075 · mtime 必须仍 2026-11-06 07:07:17.362193413) · 零落表 · "
    "零改闸 · 零改生成器代码 · 零改既有文档正文 (★含 ISS-325 的 `HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md`★) · "
    "只写【交卷页 5 处占位符 + `state/fragments/hw.yaml` 的 ISS-328 status/need 值 + `logs/iss328/` 新增件】 · "
    "★**零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信 ⇒ 没有「批一句可以发」这个选项)★** · 不替老板拍板 · 不自签 `state/issue_log.yaml` ★"
)

NOTE_333 = (
    "★2026-11-18 23:3x 项目总工签收 (★本机独立复核 7 项·不抄 agent 报告★): "
    "① `MECH/tools/check_mech_ref_reachability.py` = 56,550 B / mtime 19:36:31 · "
    "② 真件裸跑 rc=0 绿 (「MECH 侧引用的位号全部可达, 真隐患在基线内」) · "
    "③ `--selftest` rc=0 · 反向用例 14/14 通过 · "
    "④ 交卷页 `HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md` = 40,812 B @22:11:00 · 占位符 0 · B0~B6 齐全 · "
    "⑤ `grep -c iss333 state/fragments/mech.yaml` = 11 · `logs/iss333/` = 16 件 · 沙盒 `find tmp/iss333 -type l` = 0 软链 · "
    "⑥ 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 逐字节未动 · "
    "⑦ ★**该闸已在门禁链上** (★`state/gate_check.py` EXTRA_GATES 第 8 道 · owner=main 的 ISS-330 已挂·22:19~22:26 实读 extra_gates 8/8 全绿★) ⇒ 不需再挂★ "
    "★★交卷会话 22:17:15 死在【写完之后】⇒ 交付物没丢 (★铁律: 会话死 ≠ 没交卷 ⇒ 收卷前先看盘上产物·再决定要不要重派★)★"
)

NOTE_328 = (
    "★2026-11-18 23:3x 项目总工续派 cont4 (★纯写型·零写板★): "
    "★**① 兄弟 job fb67af40 22:55~23:07 那趟 aborted ⇒ 它 22:31 交回的这条没人做 ⇒ 本 job 接手** ★ "
    "★**② 派活前已确认 hw-lead 名下零在飞写会话** (★最后一条 22:17:15 timeout·无后台链进程·`ps` 无 gen_pcb_netlist_board / compare_arm_official★) ★ "
    "★**③ 盘上读数**: 交付页 58,493 B @22:13:42 占位符 0 (已完成·不许改) · 交卷页 8,156 B @22:13:52 ⇒ ★**只剩 5 处 `<!-- B* -->` (L72/L78/L84/L90/L96)** ★ · "
    "★**读数已算好在盘** (`logs/iss328/33_recalc_gate_rc.txt` + `34_cont3_readonly_recalc.txt` @22:13) ⇒ 照抄·不许重跑链 ★ "
    "★**④ 判决 (名单制闸)**: 右上臂链终板 vs 官方板 rc=1 (★DRC 12/0 · unc 29/45 · 零铜 13/24 · 差分单边零铜 7/11 · 退铜名单 2 条 `CSI_MCLK_SRC`+`USB_CC1` · 差分死腿 0 · 逐网孤岛变多 7 条·REJECT★) · "
    "★clrfix 终板 vs 官方板 rc=1 (★DRC 0/0·其余同上·REJECT★) ⇒ ★**「挪器件位置」这条处方已被 ISS-325 左上臂 + ISS-328 右上臂两个臂证伪** ★ "
    "★**⑤ ★★新铁律 (本单写进 brief)★★**: ★**段数 3,986 vs 官方终板 18,092 ⇒ 路由器代码已漂移 ⇒ 【同工艺才可比】⇒ 「unc 45→29」一律不算数** ★ "
    "★**⑥ 派活顺序铁律**: ★**先写 5 块 → 再写分片 → 最后才跑 `gate_check` (只许一次·加 timeout·不许 `--json`)** ★ (★上一趟死因 = 12 分钟全烧在跑必跑项上★) ★ "
    "★**⑦ 会话**: runId `8b776126-b460-4f64-bdf0-9df384cacac2` · childSessionKey `agent:hw-lead:subagent:6c152ec4-ffd2-4158-891d-9aea6aa83fbe` · taskName `queue_iss328_closout_cont4` · "
    "brief `state/dispatch_briefs/ISS-328_hw_closout_cont4_5blocks.md` (★`check_brief_commands.py --brief-file` rc=0★) ★"
)


def main() -> int:
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "a+", encoding="utf-8") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)

        # ---- 备份 ----
        for p in (LOG, DLOG):
            shutil.copy2(p, p + ".bak_" + STAMP)

        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]

        hit333 = hit328 = False
        for it in issues:
            if it.get("id") == "ISS-333":
                hit333 = True
                it["status"] = "verified"
                it["verify_result"] = "pass"
                it["verify_date"] = "2026-11-18"
                it["verify_by"] = "main"
                it["note"] = (it.get("note") or "") + "\n" + NOTE_333
            elif it.get("id") == "ISS-328":
                hit328 = True
                it["status"] = "fixing"   # ★保持 fixing: 不许重复派★
                it["dispatched_at"] = NOW
                it["task_brief"] = (it.get("task_brief") or "") + "\n\n" + SUMMARY_328
                it["note"] = (it.get("note") or "") + "\n" + NOTE_328
        assert hit333 and hit328, "ISS-333 / ISS-328 不在 issue_log 里"

        fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".issue_log.", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=10_000)
        os.replace(tmp, LOG)

        with open(DLOG, encoding="utf-8") as f:
            dlog = yaml.safe_load(f)
        dlog["entries"].append(
            {
                "issue": "ISS-333",
                "agent": "mech-lead",
                "at": NOW,
                "brief": (
                    "★★**签收 (main 23:3x 本机独立复核 7 项全绿)** ★ "
                    "① 闸脚本 56,550 B @19:36 · ② 真件裸跑 rc=0 绿 · ③ --selftest rc=0 反向用例 14/14 · "
                    "④ 交卷页 40,812 B @22:11:00 占位符 0 B0~B6 齐全 · ⑤ mech.yaml 命中 iss333 = 11 · logs/iss333 16 件 · 沙盒零软链 · "
                    "⑥ 板 md5 611b869e13518c3c023fb178f91a0075 + mtime 2026-11-06 07:07:17.362193413 逐字节未动 · "
                    "⑦ ★**该闸已在门禁链 EXTRA_GATES 第 8 道 (owner=main 的 ISS-330 已挂) ⇒ 不需再挂** ★ "
                    "★⇒ status: fixing → verified (verify_result=pass) · 零写板 · 零落表 · 零改闸 · 零外发★"
                ),
            }
        )
        dlog["entries"].append(
            {
                "issue": "ISS-328",
                "agent": "hw-lead",
                "at": NOW,
                "brief": SUMMARY_328,
            }
        )

        fd, tmp = tempfile.mkstemp(dir=HERE, prefix=".dispatch_log.", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.safe_dump(dlog, f, allow_unicode=True, sort_keys=False, width=10_000)
        os.replace(tmp, DLOG)

        fcntl.flock(lf, fcntl.LOCK_UN)
    print("APPLY_OK: ISS-333 verified · ISS-328 cont4 dispatched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
