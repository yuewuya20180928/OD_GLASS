#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main: 清僵尸 fixing (ISS-235 / sw-lead  +  ISS-236 / hw-lead) ⇒ 回滚 open (待重派)
=========================================================================================
★**实测依据 (★2026-11-16 08:2x, main 自己查盘 + 实跑 8 条门禁, 不抄任何交卷报告★)**:
★**A) ISS-235 (sw-lead) —— 僵尸 (子会话死在动手改之前, 盘上零产出)** ★
· 子会话 `agent:sw-lead:subagent:e7f0060e` (session 31d009e7) **07:23:29 → 08:07:52 (44 min)**
  ⇒ ★**status=done 但 abortedLastRun=true** ⇒ transcript 末条 = "I now have the full picture.
  Let me make the code changes to `timing_check.py` first." + 一次 Compaction ⇒ ★**死在动手改之前**
· ★**盘上交付物 0 件**: `SW/tools/timing_check.py` mtime 仍 **04:21** · `SW/tools/check_demo_panel_spec.py`
  mtime 仍 **04:21** (两个脚本一个字节没动) · `HANDOFF/2026-11-16_sw-lead_ISS235_*` **不存在**
  · `state/fragments/sw.yaml` mtime **07:41** = 是 ISS-221 那条会话写的 (它的交卷单 §自证 07:41:34),
  ★**不是本单** ⇒ 分片里 grep `iss235` 0 条 artifact ⇒ ★**本单零交付**
· ★**3 条红一条没修 (main 08:1x 实跑)**: `SW/tools/timing_check.py` ⇒ **rc=1 (selftest 68/70)**
  (红 = F8 L1463 + REV-3 L1484) · `check_demo_panel_spec.py` ⇒ rc=0 · `--selftest` ⇒ **rc=1 (15/16)**
  (红 = REV-12) · `check_shutdown_semantics.py --selftest` ⇒ rc=0 (17/17)
· ★**⇒ 典型「session=done ≠ 活干完了」(第 20 次复发) ⇒ status 由 fixing 回滚为 open 并重派** ★

★**B) ISS-236 (hw-lead) —— 僵尸 + 半成品是坏的 (交付物① 落盘了但编译不过)** ★
· 两个子会话**都死了**: `agent:hw-lead:subagent:7b2dea03` (session e7a86064) 07:23:29→07:44:10
  (★status=failed · errorMessage=`rate limit exceeded(TPM) (1039)`★) · `agent:hw-lead:subagent:03b9b072`
  (session f8f9591e) 07:23:42→07:37:50 (★status=timeout★) · 另有 `85841b8c` (15c66ce6) 07:23→07:44 done/aborted
· ★**盘上交付物 1/2 件, 且第 1 件是坏的**: `state/land_v_values.py` 存在 (**83257 B / 1414 行 / mtime 07:43:53**)
  ⇒ ★**`python3 -m py_compile state/land_v_values.py` ⇒ SyntaxError: line 619 (invalid character '★' U+2605)**
  ⇒ ★**实跑 `--decision V-3=E` ⇒ rc=2 起不来** ⇒ ★**交付物① 不算交付** ★
· ★**main 断点定位精确到 5 行 (在 /tmp 副本实测, 真盘零写入)**: ★**L619/620/621/622/623 这 5 行是散落的
  散文 (本该是 `#` 注释) ⇒ 把它改成注释 ⇒ 全文件编译干净 (1414 行其余全部合法)** ★
· ★**交付物② `HW/SCHEMATIC_FINALIZATION_CLOSEOUT.md` 不存在** · `HANDOFF/2026-11-16_hw-lead_ISS236_*` **不存在**
· ★**受保护 md5 5 个逐字节不变 (main 08:1x 实测)**: 网表 `34132f7e…` · 脚表 `b21b743a…` · BOM `c195a117…`
  · 板 `611b869e…` · `.kicad_pro` `3e504d2b…` ⇒ ★**本单没碰任何真源 / 板** ★
· ★**hw-lead 自己 07:3x 已在分片登记 `iss236_zero_output_check` 报同一事实** ⇒ ★**它自己就说了零产出** ★
· ★**⇒ 交付物① 半成品 + 交付物② 零 ⇒ status 由 fixing 回滚为 open 并重派 (★重派时带上断点定位, 别让子 agent 重写 1414 行★)** ★

★**为什么本 job (fb67af40 队列自动派活) 有权动 issue_log** ★
· ★**有 precedent**: `state/_apply_20261116_0155_zombie215.py` (★同一个 job 在 01:5x 干过同一件事★)
  ⇒ ★**僵尸 fixing 清理 = 派活 job 的既有职责** ★
· ★**兄弟 job 775d9893 (继续执行后继计划) 在 07:2x 开单并派了 235/236, 但它自己的派活用完就结束
  ⇒ ★**这 2 条没人再管 ⇒ 落在本 job 头上 (★"让内部待办不断线, 不靠人盯"★)** ★
· ★**本轮不碰 ISS-229 (mech-lead)**: ★**它不是僵尸 —— 交付物齐全 (HANDOFF 63194 B / 7 道闸全 rc=0 / 分片 07:49)
  ⇒ 属【已交卷待 main 复核】, 归兄弟 job 775d9893 的清账职责 ⇒ 本 job 不碰 (★避免双写 issue_log★)** ★

★**铁律**: 干活的人不许自签 ⇒ verify_by=main
★**不碰**: 任何真源文件 / 任何分片 / PROJECT_TRACKER §0 / outbox / 板
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261116_0825_zombie235_236"
TODAY = "2026-11-16"

NOTE_235 = """
★2026-11-16 08:2x 队列自动派活 job (fb67af40) **僵尸 fixing 清理**: 子会话 `agent:sw-lead:subagent:e7f0060e` (session 31d009e7) 07:23:29 → 08:07:52 (44 min) (★status=done 但 abortedLastRun=true★) ⇒ transcript 末条 = 「I now have the full picture. Let me make the code changes to timing_check.py first.」+ 一次 Compaction ⇒ ★**死在动手改之前**★ ⇒ ★**盘上交付物 0 件**: `SW/tools/timing_check.py` mtime 仍 04:21 · `SW/tools/check_demo_panel_spec.py` mtime 仍 04:21 (两个脚本一字节没动) · `HANDOFF/2026-11-16_sw-lead_ISS235_*` 不存在 · 分片里 `key: iss235` = 0 条 artifact (★sw.yaml 07:41 那次写是 ISS-221 那条会话做的, 不是本单★) ⇒ ★**main 08:1x 自己实跑 4 条门禁 ⇒ 3 条红一条没修**: `timing_check.py` rc=1 (★selftest 68/70★, 红 = F8 L1463 + REV-3 L1484) · `check_demo_panel_spec.py` rc=0 · `--selftest` rc=1 (★15/16★, 红 = REV-12) · `check_shutdown_semantics.py --selftest` rc=0 (17/17) ⇒ ★**典型「session=done ≠ 活干完了」(第 20 次复发)**★ ⇒ ★**status 由 fixing 回滚为 open 并重派**★
"""

NOTE_236 = """
★2026-11-16 08:2x 队列自动派活 job (fb67af40) **僵尸 fixing 清理 (★交付物① 落盘了但是坏的★)**: 两个子会话**都死了** —— `agent:hw-lead:subagent:7b2dea03` (session e7a86064) 07:23:29→07:44:10 (★status=failed · errorMessage=`rate limit exceeded(TPM) (1039)`★) · `agent:hw-lead:subagent:03b9b072` (session f8f9591e) 07:23:42→07:37:50 (★status=timeout★) · 另有 `85841b8c` (15c66ce6) 07:23→07:44 done/aborted ⇒ ★**盘上交付物 1/2 件, 且第 1 件是坏的**: `state/land_v_values.py` 存在 (★83257 B / 1414 行 / mtime 07:43:53★) ⇒ ★**`python3 -m py_compile` ⇒ SyntaxError: line 619 (invalid character '★' U+2605)** ⇒ ★**实跑 `--decision V-3=E` ⇒ rc=2 起不来** ⇒ ★**交付物① 不算交付**★ ⇒ ★**交付物② `HW/SCHEMATIC_FINALIZATION_CLOSEOUT.md` 不存在** · `HANDOFF/2026-11-16_hw-lead_ISS236_*` 不存在 ⇒ ★**main 断点定位精确到 5 行 (在 /tmp 副本实测, 真盘零写入)**: ★**L619/620/621/622/623 这 5 行是散落的散文 (本该是 `#` 注释) ⇒ 改成注释 ⇒ 全文件 1414 行其余全部合法**★ ⇒ ★**受保护 md5 5 个逐字节不变 (main 08:1x 实测)**: 网表 `34132f7e…` · 脚表 `b21b743a…` · BOM `c195a117…` · 板 `611b869e…` · `.kicad_pro` `3e504d2b…` ⇒ 本单没碰任何真源/板 ⇒ ★**hw-lead 自己 07:3x 已在分片登记 `iss236_zero_output_check` 报同一事实 (它自己就说了零产出)**★ ⇒ ★**status 由 fixing 回滚为 open 并重派**★ (★重派时带上断点定位 —— 别让子 agent 重写那 1414 行★)
"""

TARGETS = {"ISS-235": NOTE_235, "ISS-236": NOTE_236}


def main():
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        touched = []
        for it in issues:
            iid = it.get("id")
            if iid not in TARGETS:
                continue
            if it.get("status") != "fixing":
                print("⚠ %s status=%s (不是 fixing) ⇒ 幂等跳过" % (iid, it.get("status")))
                continue
            it["status"] = "open"
            it["dispatched_at"] = None
            it["note"] = (it.get("note") or "") + TARGETS[iid]
            touched.append(iid)
        if not touched:
            print("⚠ 没有可回滚的僵尸 fixing ⇒ 未写盘")
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
        print(" - %s fixing → open (僵尸 fixing 回滚, 待重派)" % iid)


if __name__ == "__main__":
    main()
