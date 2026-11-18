#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 18:1x · job fb67af40「ARS45 队列自动派活」
★★ISS-292 / ISS-293 复验落 verified + ISS-295 cont1 续做重派★★
=========================================================================================
★**为什么有这一趟 (★main 18:0x~18:1x 本机实查盘面 + 读会话, 不抄任何交卷报告★)**:
  · `python3 state/advance.py --json` ⇒ ★**`internal: []`** (三个 owner 名额全被 `fixing` 占着 ⇒ 一个都派不出去) ★
  · ★**但盘面 ≠ 名单 (★老坑, 第五次了★)** ⇒ ★**本 job 逐个查三个会话的生死 + 逐件查交付物★**:
    - ★`agent:hw-lead:subagent:71c9e8bb` (ISS-292) ★: 16:32:21 → 18:05:36 · runtime 1588s · **status=done** ★
      ⇒ ★**交卷完整** (28110 B · 占位符 0 · 4 件交付物在盘 · 分片 grep=15) ⇒ ★**main 18:1x 独立复验 = 全绿 ⇒ 落 verified** ★
    - ★`agent:sw-lead:subagent:347ae23f` (ISS-293 cont1) ★: 17:48:38 → 18:04:18 · runtime 478s · **status=timeout** ★
      ⇒ ★**交卷单已 40339 B 填满 + 新闸 29/29 rc=0 + selftest 4/4 rc=0 + 分片 grep=11** ⇒ ★**main 18:1x 独立复验 = 全绿 ⇒ 落 verified** ★
    - ★`agent:mech-lead:subagent:885e9633` (ISS-295) ★: 17:48:57 → 18:04:18 · runtime 462s · **status=timeout / abortedLastRun=true** ★
      ⇒ ★**死在「写闸文件」那一刻** ⇒ 交付物 4 件: ① `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` 不存在 ② `MECH/check_mech_verdict_freshness.py` 不存在
        ③ 交卷单 967 B 骨架 (七节全占位) ④ 分片 grep iss295 = 0 ⇒ ★**真僵尸 ⇒ 续做重派 (cont1)** ★
  · ⇒ ★**本趟做三件事**: ①ISS-292 复验落 verified (★hw-lead 名额空出★) ②ISS-293 复验落 verified (★sw-lead 名额空出★)
    ③ISS-295 **cont1 续做重派** (★status 全程保持 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派★)
★**★铁律**: 干活的人不许自签 ⇒ verify_by=main · ★**零写板 · 零落表** ★
★**★零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信, 全靠自己查资料★) ⇒ ★**本 job 不发任何邮件/询价/采购** ★
★**边界**: ★**只写 `state/issue_log.yaml` + `state/dispatch_log.yaml` 两个文件** ⇒ ★**不碰任何 agent 的分片**
  (★`state/fragments/*.yaml` 是三个总工的, main 不写★) · 不碰板 / 网表 / 脚表 / BOM / 决策页 / outbox / 任何闸脚本★
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261117_1810_cronfb67_verify292_293_cont295"
TODAY = "2026-11-17"

BRIEF_295_CONT = os.path.join(HERE, "dispatch_briefs", "ISS-295_mech_claims_and_verdict_freshness_cont1.md")

VERIFY_292 = (
    "★★main 2026-11-17 18:1x 独立复验 (★本机实跑, 不抄交卷报告★) ⇒ ★**PASS** ★: "
    "① ★**硬判据「重跑幂等」main 亲自复现**: 跑前 `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` md5 = `159bf20fe71c36e48292f39dafc46a35` · "
    "`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` md5 = `4d66803c42760fe72f0e64aae252db42` ⇒ 实跑 `python3 state/_iss277_build_preflight.py` "
    "(rc=0 · 步分布 S1~S13 全覆盖 · 缺覆盖的步 []) ⇒ 跑后两个 md5 ★**逐字节相同** ⇒ ★**跑一次生成器不再冲掉订正** ★ "
    "② 八道闸全 rc=0: `HW/check_workpack_state_values.py` rc=0 · `--selftest` rc=0 (反向用例全抓到) · "
    "`HW/check_onepass_preflight_coverage.py` rc=0 · `--selftest` rc=0 · `HW/check_board_frame_caliber.py` rc=0 · "
    "`state/merge.py` rc=0 · `state/gate_check.py` rc=0 (Q1 18/18) · `state/issue_check.py` rc=0 ★ "
    "③ 受保护 5 件逐字节不变: 板 `611b869e13518c3c023fb178f91a0075` (mtime 仍 `2026-11-06 07:07:17.362193413`) · "
    "`.kicad_pro` `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07` · "
    "脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ★ "
    "④ 四件交付物在盘: `state/_iss277_build_preflight.py` 41909 B · `state/_iss277_preflight_README.md` 7876 B · "
    "`state/_iss277_preflight_appendix.md` 27293 B · 交卷单 28110 B (占位符 0) · 分片 `grep -c iss292` = 15 ★"
)

VERIFY_293 = (
    "★★main 2026-11-17 18:1x 独立复验 (★本机实跑, 不抄交卷报告★) ⇒ ★**PASS** ★: "
    "① 新闸 `python3 SW/tools/check_timing_review_adc_sync.py` ⇒ **rc=0 · OK: 29/29 项通过** (★判决对象 = BAT_DET/pin38/SARADC_VIN5 · "
    "满量程 1.8V · lsb 0.439mV · rth 37.5kΩ · tau 3.75ms · settle 33.791ms · leak 2.1%FS · node 1.575V (abs-max 1.98V) · fs_util 87.5% "
    "· P1/P2/P3 旧口径残留行 = 0★) ★ "
    "② `python3 SW/tools/check_timing_review_adc_sync.py --selftest` ⇒ **rc=0 · SELFTEST 4/4 通过** (case1 回退满量程 ⇒ 红 · "
    "case2 回退判决对象 ⇒ 红 · case3 回退 BAT_DET 必装 ⇒ 红 · case4 正向对照 ⇒ 绿 · 真件读回 90918 B 未变) ★ "
    "③ `python3 SW/tools/timing_check.py` ⇒ rc=0 (SELFTEST 85/85) · `python3 SW/tools/check_demo_panel_spec.py` ⇒ rc=0 · "
    "`python3 state/gate_check.py` ⇒ rc=0 (Q1 18/18) ★ "
    "④ 受保护 5 件逐字节不变 (板 `611b869e…` mtime 仍 `2026-11-06 07:07:17` · 网表 `37f62ac3…` · 脚表 `a4270120…` · BOM `5d02bece…`) ★ "
    "⑤ 交卷单 40339 B · 占位符残留 0 (★L350/L355 那 4 处命中经逐行核对 = 脚本原样输出 + 自写说明 + 真命令行省略号, 不是空位★) · "
    "分片 `grep -c iss293` = 11 ★"
)


def main() -> int:
    if not os.path.exists(BRIEF_295_CONT):
        print("⚠ 缺 brief 文件: %s ⇒ 中止" % BRIEF_295_CONT)
        return 1

    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it["id"]: it for it in issues}

        # ---------- ① ISS-292: fixing → verified ----------
        i292 = by_id.get("ISS-292")
        if i292 is None:
            print("⚠ ISS-292 不存在 ⇒ 中止")
            return 1
        if i292.get("status") == "verified":
            print("· ISS-292 已是 verified ⇒ 幂等跳过")
        else:
            i292["status"] = "verified"
            i292["fix_ref"] = "HANDOFF/2026-11-17_hw-lead_ISS292_清单页生成器对齐.md (★28110 B ★)"
            i292["verify_result"] = "pass"
            i292["verify_date"] = TODAY
            i292["note"] = (i292.get("note") or "") + ("\n" + VERIFY_292)
            print("✅ ISS-292 fixing → verified (main 18:1x 独立复验 PASS)")

        # ---------- ② ISS-293: fixing → verified ----------
        i293 = by_id.get("ISS-293")
        if i293 is None:
            print("⚠ ISS-293 不存在 ⇒ 中止")
            return 1
        if i293.get("status") == "verified":
            print("· ISS-293 已是 verified ⇒ 幂等跳过")
        else:
            i293["status"] = "verified"
            i293["fix_ref"] = "HANDOFF/2026-11-17_sw-lead_ISS293_ADC复评文档口径同步.md (★40339 B ★)"
            i293["verify_result"] = "pass"
            i293["verify_date"] = TODAY
            i293["note"] = (i293.get("note") or "") + ("\n" + VERIFY_293)
            print("✅ ISS-293 fixing → verified (main 18:1x 独立复验 PASS)")

        # ---------- ③ ISS-295: 追加 cont1 续做说明 (status 全程 fixing) ----------
        i295 = by_id.get("ISS-295")
        if i295 is None:
            print("⚠ ISS-295 不存在 ⇒ 中止")
            return 1
        with open(BRIEF_295_CONT, encoding="utf-8") as f:
            cont295 = f.read()
        if "⑭ · ISS-295 cont1 续做说明" not in (i295.get("task_brief") or ""):
            i295["task_brief"] = (i295.get("task_brief") or "") + "\n\n---\n\n" + cont295
        i295["status"] = "fixing"
        i295["dispatched_at"] = TODAY
        i295["note"] = (i295.get("note") or "") + (
            "\n★★2026-11-17 18:1x 队列自动派活 job (fb67af40) 【cont1 续做】重派 (★不是从零重做★) ★★: "
            "子会话 `agent:mech-lead:subagent:885e9633` (sessionId f80ec41b) 17:48:57 → 18:04:18 · runtime 462s · "
            "status=timeout/abortedLastRun=true ⇒ transcript 最后两行 = assistant「Now the gate itself:」→ toolResult「Aborted」"
            "⇒ ★**死在写闸文件的那一刻** ★ ⇒ 交付物 4 件实测: ① `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` 不存在 ② "
            "`MECH/check_mech_verdict_freshness.py` 不存在 ③ 交卷单 967 B 骨架 (B0~B6 七节全「(占位 → 交卷时补全)」) ④ "
            "分片 `grep -c iss295` = 0 ⇒ ★**唯一在盘的是 `logs/iss295/gen_coverage_windows.py` (2473 B) + 它跑出来的 7 行漂移清单** ★ "
            "⇒ ★**本趟只补 4 件**: ① 交卷单骨架改成「有内容的骨架」 ② B1 写 `MECH/BOARD_ONEPASS_MECH_CLAIMS.md` ③ B2 写 "
            "`MECH/check_mech_verdict_freshness.py` (★**按逐字短语命中, 不许按行号** ⇒ 行号会漂★) ④ B3 交卷单填满 + 分片 "
            "`state/fragments/mech.yaml` (走 frag_write.py 原子写 · grep -c iss295 ≥ 4) ⇒ ★**续做任务书全文 = "
            "`state/dispatch_briefs/ISS-295_mech_claims_and_verdict_freshness_cont1.md` (★3553 B · "
            "check_brief_commands --brief-file ⇒ rc=0★)** ⇒ ★**status 全程 fixing ⇒ 无 open 窗口 ⇒ "
            "兄弟 job 775d9893 不会重复派** ★")
        print("✅ ISS-295 cont1 续做说明已追加 (status 保持 fixing)")

        shutil.copy2(LOG, BAK)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)

        # ---------- 派活日志 ----------
        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f) or {}
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-295",
            "agent": "mech-lead",
            "at": TODAY,
            "brief": ("★**【cont1 续做】重派 (★不是从零做★)★**: 会话 `agent:mech-lead:subagent:885e9633` 17:48:57 → "
                      "18:04:18 · runtime 462s · status=timeout ⇒ 死在写闸那一刻 ⇒ 4 件交付物: ① CLAIMS.md 不存在 ② "
                      "check_mech_verdict_freshness.py 不存在 ③ 交卷单 967 B 骨架 ④ 分片 grep iss295 = 0 ⇒ "
                      "★**在盘的只有 `logs/iss295/gen_coverage_windows.py` (2473 B) + 它跑出来的 7 行漂移清单** ⇒ "
                      "★**本趟只补 4 件**: 交卷单骨架改成有内容的骨架 · B1 CLAIMS.md · B2 新闸 (★按短语命中不许按行号★) · "
                      "B3 交卷单填满 + 分片 (grep -c iss295 ≥ 4) ★"),
            "job": "★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 18:1x 续做重派 · ★**brief = issue_log 里 "
                   "ISS-295 的 task_brief (★已含本 job 追加的 ⑭ cont1 节★) ⇒ ★完整续做任务书 = "
                   "`state/dispatch_briefs/ISS-295_mech_claims_and_verdict_freshness_cont1.md` (★3553 B · "
                   "check_brief_commands --brief-file ⇒ rc=0★)★ · ★**status 全程保持 fixing ⇒ 无 open 窗口 ⇒ "
                   "兄弟 job 775d9893 不会重复派**★",
        })
        tmp_dl = DL + ".tmp"
        with open(tmp_dl, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp_dl, DL)
        print("✅ dispatch_log 已写 1 条 (ISS-295 cont1)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
