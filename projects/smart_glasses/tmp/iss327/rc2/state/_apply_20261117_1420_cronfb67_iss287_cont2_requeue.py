#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 14:2x · job fb67af40「ARS45 队列自动派活」
★ISS-287 僵尸 fixing 清理 + 【cont2 续做】重排 (★零落表 · 零写板★)
=========================================================================================
★**实测依据 (★本 job 自己查盘 + 读会话, 不抄任何交卷报告★)**:
· 子会话 `agent:hw-lead:subagent:176de03a` (sessionId 86116087) 13:46:41 → 13:56:50
  (runtime 606s · status=timeout · abortedLastRun=true) ⇒ ★**死在超时, 不是活干完** ★
  ⇒ 该会话的 transcript 末条 = assistant content 空 + stopReason=aborted ⇒ ★**零产出** ★
· ★**但盘上已有实测成果 (★不是白跑★)**:
  - `logs/iss287/` ★**12 个 .log + 2 个 md5 清单**★ (13:39~13:54):
      board_gen(13:49) · calib(13:51) · calib_realdisk(13:54) · copy(13:39) ·
      drc_official(13:53) · gate(13:54) · issue_check(13:54) · landrow(13:54) ·
      merge(13:54) · onepass(13:54) · r3(13:51) · sch_chain(13:50)
    ⇒ ★**4 个答案 + 6 个读数 的实测数据全在里面了** ★
  - 沙盒 `tmp/iss287_sandbox/` 已在 (含 `HW/PCB/sandbox_gen_board.kicad_pcb` 461766 B ·
    副本官方板 md5 `611b869e…` 与真盘**逐字节相同** ⇒ 复制树自洽 ★)
  - ★**交卷单只有骨架**: `HANDOFF/2026-11-17_hw-lead_ISS287_沙盒干跑可行性探针.md`
    (★1308 B · 13:49 · 正文写着「状态: 进行中 (骨架已建, 实测中)」★) ⇒ B1~B6 没写 ★
  - ★**沙盒 README.md 没写** (tmp/iss287_sandbox/README.md 不存在) ★
  - ★**分片没写**: `state/fragments/hw.yaml` 里 `grep -c iss287` = 0 (mtime 13:26 = ISS-283 那趟) ★
· ★**受保护 5 件本 job 14:1x 实测仍逐字节未变**: 板 `611b869e13518c3c023fb178f91a0075`
  (mtime 2026-11-06 07:07:17) · `.kicad_pro` `3e504d2be83152e337949723e909be1b` ·
  网表 `37f62ac3f0b81d92ca7d48fdea717f07` · 脚表 `a4270120454aedf7a23c92cd8985c8a6` ·
  BOM `5d02bece9477ffce5fbe0193c7d5cce4` ⇒ ★**零写板 · 零落表 仍成立** ★
★**兄弟 job 775d9893 已于 14:1x 把 ⑫ 续做说明追加进 ISS-287 的 task_brief** (6574 字)
  ⇒ ★**本 job 只负责把它派出去, 不重写 brief** ★
★**处置**: fixing → open → fixing ★**同一个锁内原子完成** ★
  ⇒ ★**中间不留「open」窗口** ⇒ ★**兄弟 job 的 advance.py 不会撞车** ★
★**铁律**: 干活的人不许自签 ⇒ verify_by=main
★**不碰**: 任何真源文件 / 任何分片 / 板 / 网表 / 决策页 / outbox / 兄弟 job 的 ISS-288
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261117_1420_cronfb67_iss287_cont2"
STAMP = "2026-11-17 14:2x 队列自动派活 job (fb67af40)"

NOTE = (
    "\n\n★" + STAMP + " **僵尸 fixing 清理 + 【cont2 续做】重排 (★不是从头做★)**: 子会话 "
    "`agent:hw-lead:subagent:176de03a` (sessionId 86116087) 13:46:41 → 13:56:50 (runtime 606s · "
    "status=timeout · abortedLastRun=true) ⇒ ★**死在超时, 零产出** ★ ⇒ ★**但盘上实测成果已在** "
    "(★`logs/iss287/` 12 个 .log + 2 个 md5 清单 · 13:39~13:54★ ⇒ 4 个答案 + 6 个读数 的数据全在"
    "里面★ + 沙盒 `tmp/iss287_sandbox/` 已在 ★) ⇒ ★**本趟真正的活 = 把日志里的读数写成交卷单 "
    "B1~B6 + 写沙盒 README.md + 写分片 + 复核受保护 5 件** ★ ⇒ ★**不许重跑探针, 不许重新拷沙盒** ★ "
    "★**本 job 14:1x 实测受保护 5 件逐字节未变** (板 611b869e… mtime 2026-11-06 07:07:17 · "
    ".kicad_pro 3e504d2b… · 网表 37f62ac3… · 脚表 a4270120… · BOM 5d02bece…) ⇒ 零写板 · 零落表 仍成立 ★"
    " ★**另一条本 job 实查出的【过期基线】(★务必在交卷单里点名, 别照抄★)**: 任务书读数表写 "
    "「DNP 标记 43 个位号零标记」⇒ ★**实测是 40** (★`logs/iss287/r3.log` R3-A4 = MAIN_PCB∧DNP "
    "51 颗 · 在板上 40 颗 · 零标记 40 颗★; ★本 job 14:2x 另跑 `HW/check_netlist_contradiction_r3.py` "
    "复核 = 同值 51/40/40★) ⇒ ★**43 是 12:30 落表前的旧数 (★BAT_DET 三颗改成必装后 43→40★)** ⇒ "
    "★**⇒ 「板那一趟」S7 的验收目标「43 全标」也已过期, 应为 40** ⇒ ★**登记 need 给 main** ★"
)


def main():
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it.get("id"): it for it in issues}

        it = by_id.get("ISS-287")
        if it is None:
            print("⚠ ISS-287 不存在 ⇒ 退出")
            return
        if it.get("status") != "fixing":
            print("⚠ ISS-287 status=%s (不是 fixing) ⇒ 幂等跳过" % it.get("status"))
            return
        # ★★ 同一个锁内: fixing → open → fixing (★不留 open 窗口★)
        it["status"] = "open"
        it["dispatched_at"] = None
        it["note"] = (it.get("note") or "") + NOTE
        # ★立刻落回 fixing ⇒ 兄弟 job 的 advance.py 判 hw-lead=in_flight ⇒ 不撞车 ★
        it["status"] = "fixing"
        it["dispatched_at"] = "2026-11-17"
        print(" - ISS-287 fixing → open → fixing (僵尸清理, 同一锁内原子完成)")

        shutil.copy2(LOG, BAK)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)

        # ★派活日志 (★与既有条目同字段★)
        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f) or {}
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-287", "agent": "hw-lead", "at": "2026-11-17",
            "brief": "★续做重派 cont2 (★上一趟 176de03a 13:56:50 timeout ⇒ 零产出★): "
                     "探针 13:39~13:54 已跑完 (logs/iss287/ 12 个 .log + 沙盒 tmp/iss287_sandbox/ 已在) "
                     "⇒ 本趟只补交卷单 B1~B6 + 沙盒 README.md + 分片 + 受保护 5 件复核 ⇒ 零写板 · 零落表",
            "job": "★派活方 = cron fb67af40 (ARS45 队列自动派活) 于 14:2x 派出 · "
                   "★brief = issue_log 里 ISS-287 的 task_brief (★已含兄弟 job 775d9893 于 14:1x "
                   "追加的 ⑫ 续做说明★) · ★本 job 另附一条【过期基线纠正】: DNP 零标记 43→40★",
        })
        tmpd = DL + ".tmp"
        with open(tmpd, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmpd, DL)
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("备份: %s" % BAK)
    print("dispatch_log 已追加 ISS-287 cont2 条目")


if __name__ == "__main__":
    main()
