#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 09:1x · job fb67af40「ARS45 队列自动派活」
★清 2 条僵尸 fixing (ISS-278 mech-lead / ISS-281 hw-lead) ⇒ 回滚 open (本 job 立即重派)★
=========================================================================================
★**实测依据 (★本 job 自己查盘 + 读 sessions/transcript, 不抄兄弟 job 的报告★)**:

① ISS-278 (mech-lead) · 子会话 `agent:mech-lead:subagent:3cb93a05-b17d-455c-a632-de6433e42fe1`
   (spawnedBy cron 775d9893 run fff7a878) · 08:05:44 → 08:52:52 (runtime 1622s · status=timeout ·
   abortedLastRun=true) ⇒ transcript 末条停在【沙盒里跑算尺寸脚本】
   · ★**上一趟 (本 job 07:3x 那一派 = `agent:mech-lead:subagent:6f3f1fdc`) 07:34→08:22 也是 timeout
     (abortedLastRun=true) ⇒ 盘上只留交卷单骨架 877 B (08:14) ⇒ 交付物 1/2/3/5 全「★待做★」★**
   · ★**MECH/ 域零交付物**: `find MECH -newermt '2026-11-17 07:00' -type f` ⇒ 只命中
     `MECH/__pycache__/check_board_frame_coords.cpython-314.pyc` ⇒ ★**`BOARD_ONEPASS_MECH_SYNC.md` /
     `check_onepass_mech_sync.py` 两个交付物在盘上不存在** ★
   · ★**分片零写**: `grep -c ISS-278 state/fragments/mech.yaml` = **0** ⇒ claims 没落
   · ★**半成品算例**: `logs/iss278/compute_iss278.py` (10098 B, 08:49) 跑挂了 ⇒
     `compute_iss278.err` = `TypeError: tuple indices must be integers or slices, not str`
     (第 116 行 `rp = {p["num"]: p for p in res["pads"]}` —— `res["pads"]` 元素是 tuple 不是 dict)
     ⇒ ★**json 输出 0 B** ⇒ 算出来的数一个没落盘★

② ISS-281 (hw-lead) · 子会话 `agent:hw-lead:subagent:cb6956a1-6867-401e-ac71-20c2ed89aa99`
   (spawnedBy cron 775d9893 run 40964745) · 08:47:02 → 09:00:53 (runtime 831s · status=timeout ·
   abortedLastRun=true) ⇒ 末条 = "Now writing the final handoff (交付物 4)"
   · ★**盘上已有 4 件里的 3 件半成品 (本 job 本机实测, 不抄它的报告)★**:
     - `HW/PCB/BOARD_ONEPASS_S10_MANIFEST_SPEC.md` (20592 B, 08:48) ★**已完成**★
     - `HW/PCB/check_onepass_s10_manifest.py` (28531 B, 08:53) ★**本 job 实跑 `--selftest` = rc=0
       (用例 10 条 = 判红 9 + 正向对照 1, 全过)** ★ ⇒ ★**闸本体可用**★
     - `HW/PCB/BOARD_ONEPASS_WORKPACKET.md` (66587 B, 08:54) §3-S10 追加式订正 ★**已在盘上**
       (含 `MANIFEST.md5` 路径 / 格式契约引用 / 「规格落地 ≠ 清单已生成」边界 / 一般化教训)★
     - `state/fragments/hw.yaml` (08:56) 已登记 ISS-281 的 claim ×3 + artifact + handoff
   · ★**唯一缺口 = 交卷单没写完**: `HANDOFF/2026-11-17_hw-lead_ISS281_S10投产包清单落地.md`
     (2106 B, 08:47) ⇒ ★B0 表里 1/2/3 仍写「★待写★」(实际已在盘上) + ★**B2/B3/B4/附A/附B/附C
     全是「★待填」** ★ ⇒ ★**⇒ 这一单是【续做】不是【重做】★**

★**处置**: 两条 status fixing → open (留痕) ⇒ 由本 job 重派 (★一个 agent 一个写会话★)
★**纪律**: 干活的人不许自签 ⇒ verify_by=main
★**不碰**: 板 / 网表 / 脚表 / BOM / 任何受保护 md5 / 别人的分片 / outbox / 决策页
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261117_0915_cron_fb67_zombie_278_281"
STAMP = "2026-11-17 09:1x 队列自动派活 job (fb67af40)"

NOTES = {
    "ISS-278": (
        "\n\n★" + STAMP + " **僵尸 fixing 清理 + 【续做】重派 (★不是从头做★)**: 两趟都被网关重载打死 ⇒ "
        "① 本 job 07:3x 那一派 `agent:mech-lead:subagent:6f3f1fdc` (07:34→08:22 · status=timeout · "
        "abortedLastRun=true) ⇒ 只落交卷单骨架 877 B (08:14), 交付物 1/2/3/5 全「★待做★」★ "
        "② cron 775d9893 那一派 `agent:mech-lead:subagent:3cb93a05` (08:05:44→08:52:52 · runtime 1622s · "
        "status=timeout · abortedLastRun=true) ⇒ transcript 末条停在【沙盒算尺寸】★ "
        "★**本 job 本机实测**: `find MECH -newermt '2026-11-17 07:00' -type f` ⇒ 只命中一个 .pyc ⇒ "
        "★**`MECH/BOARD_ONEPASS_MECH_SYNC.md` 与 `MECH/check_onepass_mech_sync.py` 在盘上不存在**★ · "
        "`grep -c ISS-278 state/fragments/mech.yaml` = 0 ⇒ ★**分片零写**★ · "
        "`logs/iss278/compute_iss278.err` = `TypeError: tuple indices must be integers or slices, not str` "
        "(第 116 行 `rp = {p[\"num\"]: p for p in res[\"pads\"]}` ⇒ res['pads'] 元素是 tuple) ⇒ "
        "★**算出来的数一个没落盘 (json 0 B)**★ ⇒ status fixing → open, 重派时须"
        "★**先修那个 TypeError 再重算**★ ⇒ ★"
    ),
    "ISS-281": (
        "\n\n★" + STAMP + " **僵尸 fixing 清理 + 【续做】重派 (★不是从头做★)**: 子会话 "
        "`agent:hw-lead:subagent:cb6956a1` (08:47:02→09:00:53 · runtime 831s · status=timeout · "
        "abortedLastRun=true) ⇒ 末条 = \"Now writing the final handoff (交付物 4)\" ⇒ "
        "★**本 job 本机实测盘面: 4 件交付物里 3 件已在盘上**★ ⇒ "
        "★`HW/PCB/BOARD_ONEPASS_S10_MANIFEST_SPEC.md` (20592 B · 08:48) 已完成★ · "
        "★`HW/check_onepass_s10_manifest.py` (28531 B · 08:53) ★**本 job 实跑 `--selftest` rc=0 "
        "(用例 10 条 = 判红 9 + 正向对照 1 · 全过)**★ ⇒ 闸本体可用★ · "
        "★`HW/PCB/BOARD_ONEPASS_WORKPACKET.md` (08:54) §3-S10 追加式订正已在盘上 (老字零删)★ · "
        "★`state/fragments/hw.yaml` (08:56) 已登记 claim ×3 + artifact + handoff★ "
        "★**唯一缺口 = 交卷单没写完**: `HANDOFF/2026-11-17_hw-lead_ISS281_S10投产包清单落地.md` "
        "(2106 B · 08:47) ⇒ B0 表里 1/2/3 仍写「★待写」(实际已在盘上, 要改成已完成并贴实测 rc) + "
        "★**B2/B3/B4/附A/附B/附C 全是「★待填」**★ ⇒ status fixing → open, 重派时只补交卷单 + "
        "跑 merge/gate_check ⇒ ★**不要重做那 3 件**★ ⇒ ★"
    ),
}


def main():
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it.get("id"): it for it in issues}

        for iid in ("ISS-278", "ISS-281"):
            it = by_id.get(iid)
            if it is None:
                print("⚠ %s 不存在 ⇒ 跳过" % iid)
                continue
            if it.get("status") != "fixing":
                print("⚠ %s status=%s (不是 fixing) ⇒ 幂等跳过" % (iid, it.get("status")))
                continue
            it["status"] = "open"
            it["dispatched_at"] = None
            it["note"] = (it.get("note") or "") + NOTES[iid]
            print(" - %s fixing → open (僵尸回滚, 待本 job 重派)" % iid)

        shutil.copy2(LOG, BAK)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("备份: %s" % BAK)


if __name__ == "__main__":
    main()
