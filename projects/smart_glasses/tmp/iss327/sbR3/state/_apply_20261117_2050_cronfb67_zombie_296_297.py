#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 20:5x · job fb67af40「ARS45 队列自动派活」
★★ISS-296 (mech-lead) / ISS-297 (hw-lead) 两条【僵尸 fixing 清理 + 续做重排】★★
=========================================================================================
★**实测依据 (★本 job 自己查盘 + 读会话, 不抄兄弟 job 的报告★)**:
· ★**两条的 `fixing` 都是【僵尸 fixing】★ —— 会话已死, 活没干完:
  - ISS-296 · mech-lead: `agent:mech-lead:subagent:e8cb142c` (sessionId 5e731ce9)
    20:12:22 → **20:31:38** · runtime 1155s · status=timeout · abortedLastRun=true
    ⇒ ★**死在「闸本体已改好、交卷单还是骨架、分片一个字没写」那一刻** ★
  - ISS-297 · hw-lead: `agent:hw-lead:subagent:b469ae7e` (sessionId 4b106968)
    20:12:21 → **20:31:38** · runtime 1135s · status=timeout · abortedLastRun=true
    ⇒ ★**死在「交卷单已填满、闸已全接上、只差分片 claims 和 status」那一刻** ★
  ⇒ ★**★两个子会话 endedAt 相差 102 毫秒 (1794918698876 vs 1794918698978) ⇒ 不是各跑各的撞超时,
    是【父 run 被整个打断 ⇒ 子被连带杀掉】★** (★本 job 上一轮 run `57f0c72f` 的 transcript 末条 = toolResult「Aborted」★)
    ⇒ ★**⇒ 这是【父死子死】型连带, 不是两个 agent 各自的问题 ⇒ 重派必须【先落盘再干活】★ ★
· ★**★盘面 ≠ 名单 (★老坑, 第七次了★)★**: ★**本 job 的 `advance.py --json` 此刻 `internal: []`**
  (★三个 owner 名额全被 `fixing` 占着 ⇒ advance.py 的 in_flight 规则把两条都挡住★)
  ⇒ ★**但盘面上这两条都是僵尸 ⇒ 不重派就永远卡死在 fixing ⇒ 而且它们挡着后面所有单★ ★
· ★**盘面实况 (main 20:4x~20:5x 本机实跑)**:
  - ISS-296: ★**闸本体 + MECH 收工清单页 + 同源探针 三件【都已经做完】★
    (★`MECH/check_board_frame_coords.py` rc=0 + --selftest rc=0 · `MECH/check_demo_struct_truth.py` rc=0 + --selftest rc=0 (28/28)
    · `MECH/BOARD_ONEPASS_MECH_SYNC.md` §ISS-296-收工清单 mtime 20:27:45 (老字没删, 前副本 logs/iss296/msync_before_iss296.md)
    · `logs/iss296/probe_ledger_reading_same_source.py` 实跑 rc=0 末行 IDENTICAL: True★)
    ⇒ ★**★只剩 paperwork: 交卷单还是 1,197 B 骨架 + `grep -c iss296 state/fragments/mech.yaml` = 0★ ★
  - ISS-297: ★**主体全做完** (★交卷单 22,542 B · B0~B6 齐全 · 无占位符 · 6 道闸全接上通道
    (main 实跑 5 道 rc=0 + 第 5 道 rc=1 是既有 18 条缺陷基线·改前改后都是 18) · `HW/board_reboard.py --selftest` 10/10★)
    ⇒ ★**★只剩收尾: `interface_claims` 一条没有 + `needs_from` 一条没有 + `status` 块还停在 ISS-292 的摘要 (★`grep -c iss297` = 6 但全是 artifacts★)★ ★
· ★**本 job 实测受保护 5 件仍逐字节未变**: 板 `611b869e13518c3c023fb178f91a0075` (mtime 2026-11-06 07:07:17.362193413)
  · .kicad_pro `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07`
  · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5bdeee...` ⇒ ★**零写板 · 零落表 仍成立 ★
★**处置**: fixing → open → fixing ★**同一个锁内原子完成** ⇒ ★**中间不留「open」窗口 ⇒ 兄弟 job 775d9893 不会撞车** ★
★**铁律**: 干活的人不许自签 ⇒ verify_by=main
★**不碰**: 任何真源文件 / 任何分片 / 板 / 网表 / 脚表 / BOM / 决策页 / outbox / 兄弟 job 的任何单
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-17"

CONT = [
    ("ISS-296", "mech-lead", "ISS-296_mech_legal_reboard_mechanism_cont2.md",
     "⑮ · ISS-296 cont2 续做说明",
     "★**上一趟子会话 `agent:mech-lead:subagent:e8cb142c` (sessionId 5e731ce9) 20:12:22 → 20:31:38 · "
     "runtime 1155s · status=timeout / abortedLastRun=true ⇒ ★**死在「闸本体已改好、交卷单还是骨架、"
     "分片一个字没写」那一刻** ★",
     "★**★闸本体 + MECH 收工清单页 + 同源探针【三件都已做完】★ (★main 20:4x~20:5x 实跑★): "
     "`MECH/check_board_frame_coords.py` rc=0 + `--selftest` rc=0 (⑯a/⑯b/⑰ 全抓到) · "
     "`MECH/check_demo_struct_truth.py` rc=0 + `--selftest` rc=0 (28/28) · "
     "`MECH/BOARD_ONEPASS_MECH_SYNC.md` §ISS-296-收工清单 (M0/M1/M2/M3) mtime 20:27:45 老字没删 "
     "(前副本 `logs/iss296/msync_before_iss296.md` 87,062 B) · "
     "`logs/iss296/probe_ledger_reading_same_source.py` 实跑 rc=0 末行 `IDENTICAL: True` · "
     "`check_onepass_mech_sync.py` / `check_onepass_struct_crosscheck.py` / `merge.py` / `gate_check.py` / "
     "`issue_check.py` 全 rc=0★ ⇒ ★**★只剩 paperwork: 交卷单还是 1,197 B 骨架 + "
     "`grep -c iss296 state/fragments/mech.yaml` = 0★ ★",
     "★**【cont2 续做】重派 (★不是从零重做★)★**: ⇒ ★**本趟只做 3 件, 闸本体一个字不许再动★**: "
     "① 填满交卷单 B1~B4 (★素材盘上都有: 两闸的通道段 + 同源探针 IDENTICAL: True + "
     "⑯a/⑯b/⑰ 与 R10/R11a/R11b/R12 反向用例原样 rc + 回归 + 受保护 5 件 md5/mtime 自证★) "
     "② 写分片 (★`frag_write.py --agent mech-lead` 原子写 · `interface_claims` ≥3 条 + "
     "`needs_from` ≥1 条给 main + `status` 块 · ★★照 sw.yaml 里 ISS-298 的形状★★) "
     "③ 交卷前必跑 9 条命令贴现场 rc (★★含 `grep -c iss296` 校验★★) ★"),

    ("ISS-297", "hw-lead", "ISS-297_hw_legal_reboard_channel_cont3.md",
     "⑰ · ISS-297 cont3 续做说明",
     "★**上一趟子会话 `agent:hw-lead:subagent:b469ae7e` (sessionId 4b106968) 20:12:21 → 20:31:38 · "
     "runtime 1135s · status=timeout / abortedLastRun=true ⇒ ★**死在「交卷单已填满、闸已全接上、"
     "只差分片 claims 和 status」那一刻** ★",
     "★**★主体【全做完了】★ (★main 20:4x~20:5x 实跑★): 交卷单 22,542 B (B0~B6 齐全 + 进度日志 + "
     "`check_report_placeholders.py` 全部无占位符) · 6 道闸全接上通道 (★main 实跑: fsin_rootcause / "
     "g1a7 / commit_order / preflight_coverage / workpack_state_values 全 rc=0 且 `--selftest` 全 rc=0 · "
     "★**第 5 闸 `check_pin_function_labels.py` rc=1 = 既有 18 条缺陷基线·改前改后都是 18·0 条新失效★) · "
     "`HW/board_reboard.py --selftest` 10/10★) ⇒ ★**★只剩收尾 2 件: `interface_claims` 一条没有 + "
     "`needs_from` 一条没有 + `status` 块还停在 ISS-292 的摘要 (★`grep -c iss297` = 6 但【全是 artifacts】★)★ ★",
     "★**【cont3 续做】重派 (★不是从零重做★)★**: ⇒ ★**本趟只做 2 件, 闸本体一个字都不许再动★**: "
     "① 分片补齐 (★`frag_write.py --agent hw-lead` 原子写 · `interface_claims` ≥3 条 + `needs_from` ≥1 条 "
     "给 main (★照交卷单 B5 那三条待决事项·只列事实与代价·不替 main/老板拍板★) + `status` 块改成 "
     "ISS-297 的摘要 · ★★照 sw.yaml 里 ISS-298 的形状 (★ISS-298 已 verified·`grep -c iss298` = 4★★)★★) "
     "② 交卷单【末尾追加】一小节 `## ⑰ 交卷后追记` (★★★不许重写 B0~B6, 只许末尾追加★★★): "
     "main 独立复跑的 6 道闸 rc (★含第 5 闸 rc=1 是既有基线这条原样写★) + 分片补齐后的新 grep 数 + "
     "受保护 5 件 md5 与板 mtime 终检读数 ★"),
]


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it["id"]: it for it in issues}

        for iid, owner, fn, heading, why, disk, dl_sum in CONT:
            it = by_id.get(iid)
            if it is None:
                print("⚠ %s 不存在 ⇒ 中止" % iid)
                return 1
            brief_path = os.path.join(HERE, "dispatch_briefs", fn)
            if not os.path.exists(brief_path):
                print("⚠ 缺 brief 文件: %s ⇒ 中止" % brief_path)
                return 1
            with open(brief_path, encoding="utf-8") as f:
                cont_text = f.read()

            # ★★fixing → open → fixing 同一个锁内原子完成 ⇒ 中间不留「open」窗口 ⇒ 兄弟 job 不会撞车★★
            old_status = it.get("status")
            it["status"] = "open"
            it["status"] = "fixing"
            assert old_status == "fixing", "%s 期望 fixing, 实得 %s" % (iid, old_status)

            tb = it.get("task_brief") or ""
            if heading not in tb:
                it["task_brief"] = tb + "\n\n---\n\n" + cont_text
            it["dispatched_at"] = TODAY
            it["note"] = (it.get("note") or "") + (
                "\n\n★" + TODAY + " 20:5x 队列自动派活 job (fb67af40) **僵尸 fixing 清理 + 【续做】重排 "
                "(★不是从头重做★)**: %s ⇒ %s ⇒ ★**本趟只补盘上缺的那几件, 已做好的不许重做** ★ ⇒ "
                "★**续做任务书全文 = `state/dispatch_briefs/%s`** (★已过 "
                "`python3 state/check_brief_commands.py --brief-file` ⇒ rc=0★) ⇒ ★**status 全程 fixing ⇒ "
                "无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★ ⇒ ★**★死因 = 父 run 被中断 ⇒ 两个子会话"
                "同一秒 (20:31:38·相差 102ms) 一起死 ⇒ 本趟纪律 = 【先落盘再干活】★**" % (why, disk, fn)
            )
            print("✅ %s (%s) 僵尸 fixing 清理 + 续做说明已追加 (status 保持 fixing)"
                  % (iid, owner))

        shutil.copy2(LOG, LOG + ".bak_20261117_2050_cronfb67_zombie_296_297")
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)

        # ---------- 派活日志 ----------
        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f) or {}
        for iid, owner, fn, heading, why, disk, dl_sum in CONT:
            dl.setdefault("dispatches", []).append({
                "issue": iid,
                "agent": owner,
                "at": TODAY,
                "brief": dl_sum,
                "job": ("★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 20:5x 续做重派 ★ · ★**两个 agent 的会话 "
                        "在同一秒 (20:31:38 · 相差 102ms) 一起死 ⇒ 父 run 被中断 ⇒ 两条 `fixing` 全是僵尸 fixing "
                        "⇒ 本 job 的 `advance.py --json` 此刻 `internal: []` (名额被僵尸占着) ⇒ 不重派就永远卡死** ★ · "
                        "★**status 全程保持 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★ · "
                        "★**brief = issue_log 里 %s 的 task_brief (★已含本 job 追加的续做节★) ⇒ "
                        "★完整续做任务书 = `state/dispatch_briefs/%s` ★" % (iid, fn)),
            })
        tmp_dl = DL + ".tmp"
        with open(tmp_dl, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp_dl, DL)
        print("✅ dispatch_log 已写 %d 条" % len(CONT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
