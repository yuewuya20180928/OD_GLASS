#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★**cron fb67af40 (ARS45 队列自动派活) · 2026-11-18 21:5x · ① 签收 ISS-332 (sw-lead) ② 重派 ISS-328 收卷单 (hw-lead) ③ 重派 ISS-333 cont3 (mech-lead)** ★

★**为什么派这两条 (★逐条都是本机实跑读数·不抄任何 agent 报告★)**:
  ① `state/advance.py --json` ⇒ internal = [] (三个总工名下零 open ⇒ A 段真空 ⇒ 本轮全是【续做/收卷】)
  ② 兄弟 job 775d9893 21:36~21:47 那轮明确把三条交回本 job (★它自己写的「本 job【不抢队列】·请 fb67af40 接手」★)
  ③ 本机实读的存活判定:
     - sw-lead  21:46:31 会话 status=done ⇒ ★**已交卷** ⇒ 本轮做【独立复核 + 签收】
     - mech-lead 21:34:29 会话 status=timeout/aborted ⇒ ★**真僵尸** ⇒ 交卷页 + 分片仍缺 ⇒ 重派 cont3
     - hw-lead  19:46:56 会话死 ⇒ ★**但后台链 21:37:23 全流程结束 (本机 `ps` 实读: 无 gen_pcb_netlist_board / compare_arm_official 进程)**
       ⇒ ★**上一轮那条「活链期间不许重派」的约束已解除** ⇒ 派【收卷单】

★**ISS-332 的签收依据 (★21:5x 本机独立实跑·不抄任何 agent 报告★)**:
  - `python3 SW/tools/check_sw_ref_reachability_v2_selftest.py --selftest` ⇒ ★**15/15 通过 · rc=0** ★
  - `python3 logs/iss332/iss332_repro.py --with-v2` ⇒ ★**RT-5/6/7/8 实际[v2] 全 rc=1 且 点名=是 · CTL-1/2/3 仍 rc=1 (闸没调死) · rc=0** ★
    (★上一趟 21:2x 实跑是 RT-5~RT-8 全 rc=0 ⇒ v2 只做了一半 ⇒ 本轮 21:5x 复跑已修好★)
  - `python3 SW/tools/check_sw_ref_reachability_v2.py` ⇒ ★**rc=0 绿** ★
  - 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` ⇒ 逐字节未动
  - `grep -c iss332 state/fragments/sw.yaml` = 4 ⇒ ≥1 ★
  - merge 0 / gate_check 0 (Q1 18/18 · Q2 3/3 · Q7 9/9) / issue_check 0

★**纪律**: 零写板 · 零落表 (★本 job 只签 status, 不改任何真源·闸/生成器/网表/脚表/BOM 一个字节没动★) · 零改 agent 的分片 · 零外发
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
NOW = "2026-11-18 21:5x"
STAMP = "20261118_2150_cronfb67_verify332_dispatch328_333"

BRIEF_328 = open(
    os.path.join(HERE, "dispatch_briefs", "ISS-328_hw_rightupper_arm_closout.md"),
    encoding="utf-8",
).read()

BRIEF_333 = open(
    os.path.join(HERE, "dispatch_briefs", "ISS-333_mech_designator_gate_hook_prep_cont3.md"),
    encoding="utf-8",
).read()

SUMMARY_328 = (
    "★★**收卷单 (cont3) · 只做【收割 + 填实】· 一个字节都不许重新生成** ★ ★"
    "★**为什么派 (★21:5x 本机实跑读数★)**: "
    "★**① 后台链 21:37:23 全流程结束** (`logs/iss328/08_rightupper_arm.log` L209) ⇒ ★**21:5x `ps` 实读: 无 `state/gen_pcb_netlist_board.py` / 无 `compare_arm_official` 进程 ⇒ 全退** "
    "⇒ ★**⇒ 上一轮那条「活链期间不许重派」的约束【已解除】·现在重派安全 (不再是并发写分片)** ★ "
    "★**② 在盘**: 链的读数全在盘 (`logs/iss328/` 15 件 + `tmp/iss328/` 沙盒产物) · "
    "★**③ 缺**: 交付页 `HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md` (14,973 B) ⇒ **12 处占位符** "
    "(`SEC2_READINGS`/`SEC2_BARE_VS_CHAIN`/`SEC2_FP_DIFF`/`SEC2_GEOM`/`SEC2_PN`/`SEC3_OFFICIAL`/`SEC3_BASELINE`/`SEC3_VERDICT`/`SEC5_CONCLUSION`/`SEC6_EVIDENCE`/`SEC6_INTEGRITY`/`SEC7_FILES`) + "
    "交卷页 `HANDOFF/2026-11-18_hw-lead_ISS328_右上对照臂与TP_noop复测.md` (3,667 B) ⇒ **7 处占位符** (B0_ONE~B6_REPRO) + "
    "`state/fragments/hw.yaml` 的 status 段还停在 cont1 中途口径 ★ "
    "★**④ 判决已经出来了**: 三个名单制闸块 **全是 REJECT** (★L91 / L122 / L191★) ⇒ ★**「挪器件位置」这条处方被 ISS-325 左上臂 + ISS-328 右上臂【两个臂】证伪** ★ "
    "★**⑤ 最值钱的一条 (★日志 L41~L45★)**: 自校准闸 档② ⇒ ★**官方链 stage-1 是 17022 段, 当前路由器只出 3471 段 ⇒ 路由器代码已漂移 ⇒ 两臂不同工艺** "
    "⇒ ★**「同工艺才可比」新铁律 ⇒ 「unc 45→29」在追平段数之前一律不算数** ★ "
    "★**⑥ ★★本单最要紧的一条纪律★★**: ★**不许重跑链** (★不许跑 `state/gen_pcb_netlist_board.py` / `state/replay_patch_chain.sh` / `state/clrfix_iter.sh` / `tmp/iss328/run_ru_arm.sh`·★读数全部从 `logs/iss328/` 引★) ★ "
    "★**任务书全文**: `state/dispatch_briefs/ISS-328_hw_rightupper_arm_closout.md` "
    "(★`check_brief_commands.py --brief-file` rc=0★) ★ "
    "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075 · mtime 必须仍 2026-11-06 07:07:17.362193413) · 零落表 · "
    "零改闸 · 零改生成器代码 · 零改既有文档正文 (★含 ISS-325 的 `HW/PCB/ONETRIP_S8_LEFTUPPER_REHEARSAL.md`★) · "
    "只写【交付页占位符 + 交卷页占位符 + `state/fragments/hw.yaml` + `logs/iss328/` 新增件】 · "
    "★**零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信 ⇒ 没有「批一句可以发」这个选项)★** · 不替老板拍板 · 不自签 `state/issue_log.yaml` ★"
)

SUMMARY_333 = (
    "★★**cont3 续做单 · ★★只补【交卷两件套】· ★★先写文件 · 后跑闸★★** ★ ★"
    "★**为什么派 (★21:5x 本机实跑读数★)**: "
    "★**① cont2 会话 21:34:29 死** (最后一条 = assistant text「Aborted」· `stopReason: aborted`) ★ "
    "★**② ★★死因已定位 (★main 21:5x 读它的 transcript 尾部逐条对·★不是「活没干完」而是【顺序错了】★★)**: "
    "★**13:27:59 还在 poll 后台进程 → 13:28:02 在 dump 判据脚本片段 → 13:28:15 跑第一次 `state/gate_check.py` → 13:28:35 又起一个后台进程 → 13:31:17 跑第二次 `gate_check --json` → 13:34:27 被掐** "
    "⇒ ★**它把整个 9 分钟全烧在【跑必跑项】上 ⇒ 交卷页一个字节没写 + 分片一个字节没写** ★ "
    "⇒ ★**⇒ cont3 的第一条纪律 = 【先写两个文件, 最后才跑必跑项】· ★gate_check 只许跑一次★** ★ "
    "★**③ 在盘**: `MECH/tools/check_mech_ref_reachability.py` (56,550 B · 19:36 · ★main 20:4x 实跑 `--selftest` ⇒ rc=0 · 14/14★) + `logs/iss333/` 14 件 (★含 cont2 死前写的 cont2_verify_run1/2/3.txt·★那三件就是它【跑完必跑项就没时间写文件】的证据★) ★ "
    "★**④ 缺**: ★**`HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md` 不存在** + ★**`grep -c iss333 state/fragments/mech.yaml` = 0** ★ "
    "★**⑤ ★★最要紧的一条★★**: ★**main 20:2x 已把这道闸挂进 `state/gate_check.py` 的 `EXTRA_GATES` (★owner=main 的 ISS-330·★21:4x 实读 extra_gates 条数 = 8★) ⇒ 闸脚本一个字节都不许改 (改了链上那道闸就与盘面不一致⇒全项目门禁失真) ⇒ 本单只补【交卷页 + 分片】** ★ "
    "★**任务书全文**: `state/dispatch_briefs/ISS-333_mech_designator_gate_hook_prep_cont3.md` "
    "(★`check_brief_commands.py --brief-file` rc=0★) · ★**上一趟那份仍然有效**: `state/dispatch_briefs/ISS-333_mech_designator_gate_hook_prep_cont2.md`★ ★ "
    "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075) · 零落表 · ★**零改 `MECH/tools/check_mech_ref_reachability.py`** · "
    "零改 `state/gate_check.py` · 零改 `state/check_*.py` · 零改既有 `MECH/` 域文档正文与脚本 · 零改 `logs/iss326/` · "
    "沙盒只写 `tmp/iss333/` + `logs/iss333/` 新增件 · 只写 `state/fragments/mech.yaml` · "
    "★**零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02)★** · 不替老板拍板 · 不自签 `state/issue_log.yaml` ★"
)

VERIFY_332 = (
    "★★**2026-11-18 21:5x · cron fb67af40 (ARS45 队列自动派活) · main 独立复核 ⇒ fixing → verified** ★ ★"
    "★**交付物**: `HANDOFF/2026-11-18_sw-lead_ISS332_SW位号可达性闸4条洗白面收紧.md` (19,194 B · 21:45:22) + "
    "`SW/tools/check_sw_ref_reachability_v2.py` (59,025 B · 21:37:24) + "
    "`SW/tools/check_sw_ref_reachability_v2_selftest.py` (15,018 B · 21:39:00) + `logs/iss332/` 24 项 raw + `state/fragments/sw.yaml` ★ ★"
    "★**本机独立复核 (★21:5x 本机实跑·不抄 agent 报告★)**: "
    "★**① `python3 SW/tools/check_sw_ref_reachability_v2_selftest.py --selftest` ⇒ 15/15 通过 · rc=0** ★ · "
    "★**② `python3 logs/iss332/iss332_repro.py --with-v2` ⇒ 判决表: RT-5 (TP_TEMP→U_TEMP_1) rc=1 点名=是 / RT-6 (→TP_temp) rc=1 点名=是 / "
    "RT-7 (→SW_TEMP_ISSX) rc=1 点名=是 / RT-8 (→TP_TEMP_) rc=1 点名=是 · CTL-1/CTL-2/CTL-3 仍 rc=1 (★闸没被调死★) · rc=0** ★ "
    "★**③ `python3 SW/tools/check_sw_ref_reachability_v2.py` ⇒ rc=0 绿** ★ · "
    "★**④ 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` ⇒ 逐字节未动** ★ · "
    "★**⑤ `grep -c iss332 state/fragments/sw.yaml` = 4 ⇒ ≥1** ★ · "
    "★**⑥ merge rc=0 · gate_check rc=0 (Q1 18/18 · Q2 3/3 · Q7 9/9) · issue_check rc=0** ★ ★"
    "★**⇒ 上一趟 (21:2x) 实跑时 v2 还抓不住那 4 条洗白面 (RT-5~RT-8 全 rc=0) ⇒ 本轮复跑已全红 ⇒ 缺口补齐 ⇒ 签 verified** ★ ★"
    "★**两条交 main 拍的结论 (agent 自己写明的·不代拍)★**: "
    "★**① 两本台账不是同一本·交集=0** (`BASELINE_TOKENS` 3 条 = 允许它【对不上】的已登记真患 · `EXEMPT_LEDGER` 15 条 = 允许它【不算位号】的形状豁免·★切闸时两本都要认★) ★ · "
    "★**② 怎么挂**: `state/gate_check.py` 的 `EXTRA_GATES` 第 3 位 (L222-223) · 路径换成 v2 · `args` 传 `()` 裸跑 ⇒ ★**只改 1 行**★ · 旧闸建议不删文件、退出链 (★回滚 = 改回 1 行★) ★ ★"
    "★**已知残留 [推算]**: 「洗白成已登记的合法 token」这条路仍漏 (例 `TP_TEMP`→`TP_BOOT`) ⇒ 堵它要 token 级快照台账 ⇒ 属下一版 ★ "
    "★**零写板 · 零落表 · 零改真件闸 · 零改 `state/gate_check.py` · 零外发** ★"
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

        shutil.copy2(LOG, LOG + ".bak_" + STAMP)
        shutil.copy2(DLOG, DLOG + ".bak_" + STAMP)
        applied.append("备份: issue_log.yaml + dispatch_log.yaml")

        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}

        # ── ① ISS-332 签收 (fixing → verified) ──
        i332 = idx.get("ISS-332")
        if not i332:
            print("· ISS-332 不存在 (异常)")
            return 1
        if i332.get("status") == "verified":
            applied.append("ISS-332 已是 verified ⇒ 幂等跳过")
        else:
            if i332.get("status") != "fixing":
                print("· ISS-332 status=%s ≠ fixing ⇒ 不签" % i332.get("status"))
                return 1
            i332["status"] = "verified"
            i332["verify_result"] = "pass"
            i332["verify_date"] = "2026-11-18"
            i332["note"] = (i332.get("note") or "") + "\n\n" + VERIFY_332
            applied.append("ISS-332 fixing → verified (verify_result=pass · 21:5x 独立复核 6 项全绿)")

        # ── ② ISS-328 收卷单 (status 保持 fixing) ──
        i328 = idx.get("ISS-328")
        if not i328:
            print("· ISS-328 不存在 (异常)")
            return 1
        tb = i328.get("task_brief") or ""
        if "ISS-328 · hw-lead · ★★收卷单 (cont3)" not in tb:
            i328["task_brief"] = tb + "\n\n---\n\n" + BRIEF_328
            applied.append("ISS-328 task_brief += 收卷单 (★原 brief 全文保留★) · status 保持 fixing")
        else:
            applied.append("ISS-328 收卷单已在 brief 里 (跳过·幂等)")
        if i328.get("status") != "fixing":
            i328["status"] = "fixing"
            applied.append("ISS-328 status → fixing (★兜底★)")
        i328["dispatched_at"] = NOW
        i328["note"] = (
            str(i328.get("note") or "")
            + " ★★2026-11-18 21:5x · cron fb67af40 派【收卷单】★★ "
            "★**后台链 21:37:23 全流程结束 + 21:5x `ps` 实读全退 ⇒ 「活链期间不许重派」的约束已解除** "
            "⇒ ★**派收卷单: 填实交付页 12 处 + 交卷页 7 处占位符 + 更新分片 status, 不许重跑链** ★ "
            "★**判决已定: 三个名单制闸块全 REJECT (L91/L122/L191) ⇒ 「挪器件位置」这条处方被 ISS-325 左上臂 + ISS-328 右上臂两个臂证伪** ★"
        )
        applied.append("ISS-328 dispatched_at / note 已更新")

        # ── ③ ISS-333 cont3 (status 保持 fixing) ──
        i333 = idx.get("ISS-333")
        if not i333:
            print("· ISS-333 不存在 (异常)")
            return 1
        tb = i333.get("task_brief") or ""
        if "ISS-333 · mech-lead · ★★cont3 续做单" not in tb:
            i333["task_brief"] = tb + "\n\n---\n\n" + BRIEF_333
            applied.append("ISS-333 task_brief += cont3 (★原 brief 全文保留★) · status 保持 fixing")
        else:
            applied.append("ISS-333 cont3 已在 brief 里 (跳过·幂等)")
        if i333.get("status") != "fixing":
            i333["status"] = "fixing"
            applied.append("ISS-333 status → fixing (★兜底★)")
        i333["dispatched_at"] = NOW
        i333["note"] = (
            str(i333.get("note") or "")
            + " ★★2026-11-18 21:5x · cron fb67af40 重派 cont3★★ "
            "★**cont2 21:34:29 死 ⇒ ★★main 21:5x 读它 transcript 尾部定位死因: 9 分钟全烧在【跑 gate_check 两遍】上 ⇒ 交卷页/分片一个字没写★★ "
            "⇒ ★**cont3 第一纪律 = 【先写两个文件 · 最后才跑必跑项 · gate_check 只跑一次】** ★ "
            "★**闸脚本已被 main 挂进 EXTRA_GATES ⇒ 仍不许改** ★"
        )
        applied.append("ISS-333 dispatched_at / note 已更新")

        log["issues"] = issues
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=10**6))

        # ── dispatch_log 追加 ──
        dlog = yaml.safe_load(open(DLOG, encoding="utf-8")) or {}
        entries = dlog.get("dispatches") or []
        for issue, agent, brief, mark in (
            ("ISS-328", "hw-lead", SUMMARY_328, "收卷单 (cont3)"),
            ("ISS-333", "mech-lead", SUMMARY_333, "cont3 续做单"),
        ):
            if not any(e.get("issue") == issue and mark in str(e.get("brief") or "") for e in entries):
                entries.append(
                    {
                        "issue": issue,
                        "agent": agent,
                        "at": "2026-11-18",
                        "brief": brief,
                        "job": (
                            "cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-18 21:5x · "
                            "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"
                        ),
                    }
                )
                applied.append("dispatch_log.yaml += %s %s 1 条" % (issue, mark))

        atomic_write(DLOG, yaml.safe_dump(dlog, allow_unicode=True, sort_keys=False, width=10**6))

    for a in applied:
        print("·", a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
