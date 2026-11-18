#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 22:2x · job fb67af40「ARS45 队列自动派活」
★★ISS-299 (hw-lead) / ISS-300 (mech-lead) 两条【僵尸 fixing 清理 + cont1 续做重派】★★
=========================================================================================
★**本 job 本轮实测依据 (★自己查盘 + 读会话, 不抄兄弟 job 的报告★)**:
· ★**两条的 `fixing` 都是【僵尸 fixing】★ —— 会话已死, 活没干完:
  - ISS-299 · hw-lead: `agent:hw-lead:subagent:008bc381` (sessionId 5b01e341)
    21:46:41 → **21:59:41** · runtime 776s · status=timeout · abortedLastRun=true
    ⇒ ★**死在「闸本体已重锚好、交卷单 B0~B6 + ⑰-1/⑰-3/⑰-4/⑰-5 已填、只差 §⑰-2 那张回归读数表」那一刻** ★
  - ISS-300 · mech-lead: `agent:mech-lead:subagent:e2720689` (sessionId 1765a992)
    21:46:40 → **21:59:40** · runtime 776s · status=timeout · abortedLastRun=true
    ⇒ ★**死在「新闸已写好并跑绿、交卷单还是 1,828 B 骨架 (10 处占位符)」那一刻** ★
  ⇒ ★**★两个子会话 endedAt 相差 81 毫秒 (21:59:41 / 21:59:40) ⇒ 不是各跑各的撞超时,
    是【父 run `aea23265` 整个被掐 ⇒ 子被连带杀掉】★** ⇒ ★**重派必须【先落盘再干活】★ ★
· ★**★盘面 ≠ 名单 (★老坑, 第八次了★)★**: ★**本 job 的 `advance.py --json` 此刻 `internal: []`**
  (★三个 owner 名额全被 `fixing` 占着 ⇒ advance.py 的 in_flight 规则把两条都挡住★)
  ⇒ ★**但盘面上这两条都是僵尸 ⇒ 不重派就永远卡死在 fixing ⇒ 而且它们挡着后面所有单★ ★
· ★**盘面实况 (main 22:1x~22:2x 本机实跑, 不抄任何 agent 报告)**:
  - ISS-299: ★**主体全做完**: `HW/check_pin_function_labels.py` (55,420 B · mtime 21:51:18) 已把
    `PROTECTED_MD5` 三个基线重锚到 ISS-283 落表后真盘值 (37f62ac3 / a4270120 / 5d02bece) +
    `MD5_ANCHOR_CHAIN` 逐跳补齐 (网表 +3 跳 · BOM +2 跳) ⇒ ★**`--expect-known` rc=0 (15/15 一致) ·
    `--selftest` rc=0 (13 + 10) · 默认模式 rc=1 且恰好 15 条缺陷 (既有缺陷基线)** ★
    ⇒ ★**交卷单 20,689 B · B0~B6 六块齐全且非空 · ⑰-1 反向用例 6/6 已填 · ⑰-3/⑰-4/⑰-5 已填**
    ⇒ ★**★只差 §⑰-2 那一行占位符 `★(回归跑完后现场填入)★` (L189)** ★
    ⇒ 分片 `grep -c iss299` = 10 (claims 5 / needs 2 / artifacts 3) · status = {delivered/100/绿} ⇒ **分片已齐**
    ⇒ ISS-297 附带小修 (3 行标准标题行) **已完成** (ISS-297 交卷单 mtime 21:52)
  - ISS-300: ★**闸本体已做完且跑绿**: `MECH/check_onepass_mech_release.py` (21,227 B · mtime 21:53)
    ⇒ ★**主跑 rc=0 (绿 6 / 红 0) · `--selftest` rc=0 (反向用例 ⑥ 真沙盒真篡改 ⇒ 汇总红 1 道并
    点名 `MECH/check_board_frame_coords.py` · 恢复 ⇒ 回绿 · 真件 md5 不变) · `--json` ok=True n_green=6** ★
    ⇒ ★**交卷单 `HANDOFF/2026-11-17_mech-lead_ISS300_结构侧准出汇总闸.md` = 1,828 B 骨架
    · `grep -cE "🔄|待填"` = 10 处占位符 · B1~B6 六块全空** ★ ⇒ ★**★只差 paperwork★ ★
    ⇒ 分片 `grep -c iss300` = 12 (claims 5 / needs 2 / artifacts 3) · status = {delivered/100/绿} ⇒ **分片已齐**
  - ★**日志在盘**: `logs/iss299/` 4 个 (selftest_after 4,718 B · regression 42,579 B · gate_check 2,928 B ·
    reverse_cases 775 B) · `logs/iss300/` 17 个 (含 boundary_before/after · regression 8,163 B ·
    reverse_case 9,017 B · 6 个 gate_check_*.log) ⇒ **交卷单素材全在盘, 一个字不许编** ★
· ★**★一条 main 实测出来的判据坑 (★要写进续做任务书★)★**:
  ★**`python3 state/check_report_placeholders.py < <交卷单>` 对 ISS-300 那份 10 处 `🔄 待填` 判【无占位符】**
  ⇒ ★**因为它只抓 `%(name)s` / `PLACEHOLDER` / 裸 `TODO`·抓不到 `🔄 待填` 与 `★(…填入…)★` 这种形态★**
  ⇒ ★**⇒ 真判据是 `grep -cE "🔄|待填"` 必须 = 0 ⇒ ★两条续做任务书都写明了这一点★ ★
· ★**本 job 实测受保护 5 件仍逐字节未变**: 板 `611b869e13518c3c023fb178f91a0075` (mtime 2026-11-06 07:07:17.362193413)
  · .kicad_pro `3e504d2be83152e337949723e909be1b` · 网表 `37f62ac3f0b81d92ca7d48fdea717f07`
  · 脚表 `a4270120454aedf7a23c92cd8985c8a6` · BOM `5d02bece9477ffce5fbe0193c7d5cce4` ⇒ **零写板 · 零落表 仍成立** ★
★**处置**: fixing → open → fixing ★**同一个锁内原子完成** ⇒ ★**中间不留「open」窗口 ⇒ 兄弟 job 775d9893 不会撞车** ★
★**铁律**: 干活的人不许自签 ⇒ verify_by=main
★**不碰**: 任何真源文件 / 任何分片 / 板 / 网表 / 脚表 / BOM / 决策页 / outbox / 兄弟 job 的任何单
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
TODAY = "2026-11-17"

CONT = [
    ("ISS-299", "hw-lead", "state/dispatch_briefs/ISS-299_hw_h1_reanchor_hop2_cont1.md",
     "★**cont1 续做 (★2026-11-17 22:2x · cron fb67af40 重派僵尸 fixing★)** ★**依据 = main 22:1x~22:2x 本机实跑★** "
     "⇒ ★**上一趟子会话 `agent:hw-lead:subagent:008bc381` (sessionId 5b01e341) 21:46:41 → 21:59:41 · "
     "runtime 776s · status=timeout / abortedLastRun=true ⇒ 死在「交卷单 §⑰-2 那行占位符还没填」那一刻★** "
     "⇒ ★**★两个子会话 endedAt 相差 81 毫秒 ⇒ 【父 run 被掐 ⇒ 子被连带杀】⇒ 本 job 是僵尸 fixing 的唯一重派方★** "
     "⇒ ★**主体【全做完】(闸已重锚: `--expect-known` rc=0 · `--selftest` rc=0 (13+10) · 默认 rc=1 恰好 15 条缺陷 = "
     "既有基线 · 交卷单 20,689 B · B0~B6 齐全非空 · ⑰-1/⑰-3/⑰-4/⑰-5 已填 · 分片 grep -c=10 已齐) ⇒ "
     "本轮只派【最后 1 件 paperwork: 填 §⑰-2 那行 `★(回归跑完后现场填入)★` (素材 = logs/iss299/ 4 个日志)】★** "
     "⇒ ★**附带一条 main 实测坑写进任务书: `check_report_placeholders.py` 抓不到 `🔄 待填` / `★(…填入…)★` "
     "⇒ 真判据是 `grep -cE \"🔄|待填\"` 必须 = 0★** ★ ⇒ ★**闸本体一个字不许再动 · 零写板 · 零落表 · 零外发** ★"),

    ("ISS-300", "mech-lead", "state/dispatch_briefs/ISS-300_mech_onepass_release_gate_cont1.md",
     "★**cont1 续做 (★2026-11-17 22:2x · cron fb67af40 重派僵尸 fixing★)** ★**依据 = main 22:1x~22:2x 本机实跑★** "
     "⇒ ★**上一趟子会话 `agent:mech-lead:subagent:e2720689` (sessionId 1765a992) 21:46:40 → 21:59:40 · "
     "runtime 776s · status=timeout / abortedLastRun=true ⇒ 死在「新闸已跑绿、交卷单还是 1,828 B 骨架」那一刻★** "
     "⇒ ★**★两个子会话 endedAt 相差 81 毫秒 ⇒ 【父 run 被掐 ⇒ 子被连带杀】⇒ 本 job 是僵尸 fixing 的唯一重派方★** "
     "⇒ ★**闸本体【已做完且跑绿】(21,227 B · 主跑 rc=0 绿6/红0 · `--selftest` rc=0 反向用例 ⑥ 真沙盒真篡改 ⇒ "
     "汇总红1道并点名 check_board_frame_coords.py · 恢复回绿 · 真件 md5 不变 · `--json` ok=True n_green=6) ⇒ "
     "本轮只派【最后 1 件 paperwork: 填满交卷单 B0 + B1~B6 六块 (素材 = logs/iss300/ 17 个日志)】★** "
     "⇒ ★**附带一条 main 实测坑写进任务书: `check_report_placeholders.py` 对那 10 处 `🔄 待填` 判【无占位符】"
     "⇒ 真判据是 `grep -cE \"🔄|待填\"` 必须 = 0★** ★ ⇒ ★**闸本体 + 那 6 道闸本体都一个字不许再动 · 零写板 · 零落表 · 零外发** ★"),
]


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it["id"]: it for it in issues}

        for iid, owner, brief_file, note in CONT:
            it = by_id.get(iid)
            if it is None:
                print("⚠ %s 不存在 ⇒ 中止" % iid)
                return 1
            if it.get("owner") != owner:
                print("⚠ %s owner=%s ≠ %s ⇒ 中止" % (iid, it.get("owner"), owner))
                return 1
            if it.get("status") != "fixing":
                print("⚠ %s status=%s (不是 fixing) ⇒ 幂等跳过, 不重复落账" % (iid, it.get("status")))
                continue
            brief_path = os.path.join(PROJ, brief_file)
            if not os.path.exists(brief_path):
                print("⚠ 缺 cont brief 文件: %s ⇒ 中止" % brief_path)
                return 1
            with open(brief_path, encoding="utf-8") as f:
                cont_brief = f.read()

            # ★fixing → open → fixing 同一个锁内原子完成 ⇒ 中间不留 open 窗口★
            it["status"] = "open"
            it["status"] = "fixing"
            it["dispatched_at"] = TODAY
            it["note"] = (it.get("note") or "") + "\n\n★" + note

            # ★任务书 = 原 task_brief (权威全文) + cont1 续做说明 (盘面实况 + 只做什么 + 边界)★
            it["task_brief"] = (it.get("task_brief") or "") + "\n\n\n" + ("=" * 78) + "\n\n" + cont_brief
            print("✅ %s (%s): fixing→open→fixing 原子完成 + cont1 续做说明已并入 task_brief" % (iid, owner))

        shutil.copy2(LOG, LOG + ".bak_20261117_2225_cronfb67_zombie_299_300_cont1")
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)

        # ---------- 派活日志 ----------
        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f) or {}
        for iid, owner, brief_file, note in CONT:
            dl.setdefault("dispatches", []).append({
                "issue": iid,
                "agent": owner,
                "at": TODAY,
                "brief": ("★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 22:2x · ★**僵尸 fixing 重派 = cont1 续做"
                          "(★不是从零重做★)** ★ · ★**依据 = main 22:1x~22:2x 本机实跑 (不抄任何 agent 报告)** ★ · "
                          "★**上一趟子会话被【父 run 掐断】连带杀掉 (两个 endedAt 相差 81 毫秒) ⇒ 本轮任务书加了"
                          "「先落盘再展开」纪律** ★ · ★**零写板 · 零落表 · 零外发** ★ · "
                          "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★ · "
                          "★**brief = issue_log 里 %s 的 task_brief (★= 原任务书全文 + `%s` 全文·"
                          "已过命令存在性闸 `python3 state/check_brief_commands.py --brief-file` ⇒ rc=0★)** ★"
                          % (iid, brief_file)),
                "note": note,
            })
        tmp_dl = DL + ".tmp"
        with open(tmp_dl, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp_dl, DL)
        print("✅ dispatch_log 已写 %d 条 (cont1 重派)" % len(CONT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
