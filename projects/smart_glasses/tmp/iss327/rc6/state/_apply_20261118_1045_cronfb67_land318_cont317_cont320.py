#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★ISS-318 落地 (fixing → verified) + ISS-317 (hw-lead) cont2 续做 + ISS-320 (mech-lead) cont1 续做
   · cron fb67af40 (ARS45 队列自动派活) · 2026-11-18 10:4x★

★**为什么有本脚本** (★main 10:4x 本机实读★):
  · 子会话 `agent:sw-lead:subagent:2973946e-...` 09:17:03 起 · 09:24:28 死 (status=timeout ·
    errorMessage="This operation was aborted") ⇒ **被父 cron run 结束连带 abort** ⇒ 3 条在飞全部变僵尸 fixing
  · main 10:2x 实跑判定:
      - ISS-318 (sw-lead) ⇒ **交卷齐全** (交卷页 52,320 B · B0~B6 齐全 · 分片 09:20:36 已写 · logs/iss318 14 件) ⇒ 可落 verified
      - ISS-317 (hw-lead) ⇒ **半成品** (交卷页 B0~B6 在 · ★交付物 `HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md`
        还是 813 B 骨架七节「(施工中)」 · 交卷页 B2 引用的 7 个日志不存在 · 分片 0 命中 ISS-317) ⇒ cont2
      - ISS-320 (mech-lead) ⇒ **基本没动** (交卷页还是 main 09:1x 落的 1,430 B 骨架 · MECH 域 23 个文件仍含
        `ICP582035PR-01` · 分片 mtime 还是 08:46:20) ⇒ cont1

★**status 处置**: ISS-317 / ISS-320 **保持 fixing** (★不回滚成 open★ ⇒ 下一轮 cron 的 in_flight 规则会跳过这两个
  agent ⇒ 没有重复派活窗口 ⇒ 也避免 10:37 那轮 cron 撞车★) ⇒ **task_brief 追加 cont 说明 (原 brief 全文保留)**
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-18"

CONT317 = open(os.path.join(HERE, "dispatch_briefs",
                            "ISS-317_hw_s1_rename_cont2.md"), encoding="utf-8").read()
CONT320 = open(os.path.join(HERE, "dispatch_briefs",
                            "ISS-320_mech_cell_model_rename_cont1.md"), encoding="utf-8").read()


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
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        # 锁内重读 (★不许用锁外读到的旧内容写回★)
        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}
        applied = []

        # ---------- ① ISS-318 → verified ----------
        i318 = idx.get("ISS-318")
        if i318 and i318.get("status") != "verified":
            i318["status"] = "verified"
            i318["verify_date"] = NOW
            i318["verify_result"] = (
                "✅ verified (★main 2026-11-18 10:2x~10:3x 独立复核·不抄 agent 报告★) ⇒ "
                "★**交卷物在盘**: `HANDOFF/2026-11-18_sw-lead_ISS318_SW位号引用闸与挂链体检.md` (52,320 B · 09:21 · B0~B6 齐全) + "
                "`SW/tools/check_sw_ref_reachability.py` (★**main 本机实跑: 裸跑 rc=0 · `--selftest` rc=0 · 反向用例 7/7 全抓到·含 RC-4/RC-5 fail-closed + RC-6/RC-7 正向对照★)★ + "
                "`logs/iss318/` (14 件: 原始输出 + md5 前后 + 占位符扫描 0) + `state/fragments/sw.yaml` (★09:20:36 已写 status 段换 ISS-318 · artifacts 209 · needs 125★) ★"
                "⇒ ★**零写板双证**: 板 md5 `611b869e13518c3c023fb178f91a0075` + mtime `2026-11-06 07:07:17.362193413` 交卷前后逐字节不变 ★ "
                "⇒ ★**本单自己声明没做完的部分如实留账** (§B5-2): ① 闸【没挂链】(★挂闸是 main 的机制地界·已由 main 在本轮挂入 EXTRA_GATES★) "
                "② 那 3 条真隐患 (CONN_USB / TP_INT / TP_TEMP) 的处置没做 (改文档措辞要动 SW 侧既有文档正文 + 落表那一趟) ③ R3 基线收紧没做 ⇒ ★**三条都转成下一批单, 不装完成** ★"
            )
            i318["note"] = (i318.get("note") or "") + (
                f"\n★**{NOW} 10:4x · cron fb67af40 (ARS45 队列自动派活) 落地 verified** ★ "
                "★**独立复核**: 闸裸跑 rc=0 · `--selftest` 7/7 · 交卷页 B0~B6 齐全 · 分片已写 · 板 md5 逐字节不变 ★ "
                "★**死因归档**: 子会话 09:17:03~09:24:28 被父 cron run 结束连带 abort (★不是 sw-lead 的错★) ★"
            )
            applied.append("ISS-318 fixing → verified (main 独立复核)")

        # ---------- ② ISS-317 cont2 ----------
        i317 = idx.get("ISS-317")
        if i317:
            tb = i317.get("task_brief") or ""
            if "ISS-317 · hw-lead · ★★cont2 续做说明★★" not in tb:
                i317["task_brief"] = tb + "\n\n---\n\n" + CONT317
                applied.append("ISS-317 task_brief += cont2 (★原 brief 全文保留★) · status 保持 fixing")
            i317["dispatched_at"] = NOW
            i317["note"] = (i317.get("note") or "") + (
                f"\n★**{NOW} 10:4x · cron fb67af40 续做重派 cont2** ★ ★**为什么**: 子会话 09:17:03~09:24:28 被父 run 连带 abort ⇒ "
                "★**半成品**: 交卷页 B0~B6 在, ★**但交付物 `HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md` 还是 813 B 骨架七节「(施工中)」 "
                "(★`logs/iss317/rename_list_raw.txt` 58,695 B 的 218 行改名表 + `03b_sb_run_raw.txt` 的 A0~A5 沙盒读数都在盘上·不用重跑★) "
                "+ 交卷页 B2 引用的 7 个日志不存在 + 分片 0 命中 ISS-317★ ⇒ ★**cont2 目标 = 交付物正文写实 + 补齐引用 + 写分片** ★"
            )

        # ---------- ③ ISS-320 cont1 ----------
        i320 = idx.get("ISS-320")
        if i320:
            tb = i320.get("task_brief") or ""
            if "ISS-320 · mech-lead · ★★cont1 续做说明★★" not in tb:
                i320["task_brief"] = tb + "\n\n---\n\n" + CONT320
                applied.append("ISS-320 task_brief += cont1 (★原 brief 全文保留★) · status 保持 fixing")
            i320["dispatched_at"] = NOW
            i320["note"] = (i320.get("note") or "") + (
                f"\n★**{NOW} 10:4x · cron fb67af40 续做重派 cont1** ★ ★**为什么**: 子会话 09:17:03~09:24:27 被父 run 连带 abort ⇒ "
                "★**基本没动**: 交卷页还是 main 09:1x 落的 1,430 B 骨架 · MECH 域 23 个文件仍含 `ICP582035PR-01` · 分片 mtime 仍 08:46:20 ★ "
                "★**main 已先做**: HW 域 3 行 (POWER_BUDGET_V3 L27/L259 + NETLIST_SELF_CONSISTENCY_SPEC L1046) ★ ⇒ ★**MECH 域 33 行 / 19 活文件留给 mech-lead** ★"
            )

        # ---------- ④ dispatch_log ----------
        dl = yaml.safe_load(open(DL, encoding="utf-8")) if os.path.exists(DL) else {"dispatches": [], "entries": []}
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-318", "agent": "sw-lead", "at": NOW,
            "brief": "★**落地 verified** (★main 10:2x 独立复核: 闸裸跑 rc=0 · --selftest 7/7 · 交卷页 52,320 B B0~B6 齐全 · 分片已写 · 板 md5 不变★)"})
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-317", "agent": "hw-lead", "at": NOW,
            "brief": "★**续做重派 cont2** (★子会话被父 run 连带 abort · 半成品: 交付物正文还是骨架·分片没写★ ⇒ 目标 = 交付物写实 + 补齐引用 + 写分片★)"})
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-320", "agent": "mech-lead", "at": NOW,
            "brief": "★**续做重派 cont1** (★子会话被父 run 连带 abort · 基本没动 ⇒ 目标 = MECH 域 33 行 / 19 活文件只换型号名 + 台账逐行落纸 + 写分片★)"})
        applied.append("dispatch_log += 3 条 (ISS-318 落地 / ISS-317 cont2 / ISS-320 cont1)")

        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200))
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=200))

        print("=== apply done ===")
        for a in applied:
            print("  -", a)
        return 0


if __name__ == "__main__":
    sys.exit(main())
