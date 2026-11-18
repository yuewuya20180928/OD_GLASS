#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 13:5x · job fb67af40「ARS45 队列自动派活」
★清 1 条僵尸 fixing (ISS-287) ⇒ 回滚 open (本 job 立即续做重派)★
=========================================================================================
★**实测依据 (★本 job 自己查盘 + 读 transcript, 不抄兄弟 job 的报告★)**:
· 子会话 `agent:hw-lead:subagent:95ae65d0` (sessionId e7162f4e) 13:38:51 → 13:41:43
  · runtime 170s · status=done · abortedLastRun=true
  · ★**transcript 末条 = custom `openclaw:prompt-error`: "LLM idle timeout (120s): no response from
    model"** ⇒ ★**死在模型侧空转, 不是活干完** (转录里最后一条 toolResult 是读 `check_pcb_drc.py` 头 45 行)
· ★**盘上交付物 1.5 件 (半成品)**:
  - 交卷单骨架在: `HANDOFF/2026-11-17_hw-lead_ISS287_沙盒干跑可行性探针.md` (1111 B · 13:39
    · 正文写着「状态: 进行中 (骨架已建, 实测中)」+ B0 受保护 5 件 md5/mtime)
  - 沙盒已复制: `tmp/iss287_sandbox/` (325M · HW/state/MECH/SW/config/deploy) ⇒ 但 README.md 未写
  - ★**分片没写**: `state/fragments/hw.yaml` 里 `grep -c iss287` = 0 (mtime 13:26 = ISS-283 那一趟写的)
  - ⇒ ★**4 个答案一个没答 · 6 个读数一个没读**
· ★**受保护 5 件本 job 实测逐字节未变**: 板 611b869e… (mtime 2026-11-06 07:07:17) · .kicad_pro
  3e504d2b… · 网表 37f62ac3… · 脚表 a4270120… · BOM 5d02bece… ⇒ ★**零写板 · 零落表 仍成立**
★**处置**: ISS-287 status fixing → open (留痕) ⇒ 由本 job 续做重派 (★一个 agent 一个写会话★)
★**兄弟 job 775d9893 的分工**: 它只派 `internal` 里 status==open 的 ⇒ ★**本 job 落回 fixing 之后,
  它的 advance.py 会把 hw-lead 判为 in_flight ⇒ 不撞车** ★
★**铁律**: 干活的人不许自签 ⇒ verify_by=main
★**不碰**: 任何真源文件 / 任何分片 / 板 / 网表 / 决策页 / outbox
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261117_1350_zombie_iss287"
STAMP = "2026-11-17 13:5x 队列自动派活 job (fb67af40)"

NOTE = (
    "\n\n★" + STAMP + " **僵尸 fixing 清理 + 【续做】重派 (★不是从头做★)**: 子会话 "
    "`agent:hw-lead:subagent:95ae65d0` (sessionId e7162f4e) 13:38:51 → 13:41:43 (runtime 170s · "
    "status=done · abortedLastRun=true) ⇒ ★**transcript 末条 = `openclaw:prompt-error`: "
    "\"LLM idle timeout (120s): no response from model\"** ⇒ 死在模型侧空转 (不是活干完) ⇒ "
    "★**盘上 1.5 件半成品**: ① 交卷单骨架在 (1111 B · 13:39 · 正文写着「状态: 进行中」+ B0 "
    "受保护 5 件 md5/mtime) ② 沙盒已复制 (`tmp/iss287_sandbox/` 325M · 含 HW/state/MECH/SW/"
    "config/deploy) 但 README.md 未写 ③ ★**分片没写** (`state/fragments/hw.yaml` 里 "
    "`grep -c iss287` = 0) ⇒ ⇒ ★**4 个答案一个没答 · 6 个读数一个没读** ⇒ status fixing → open, "
    "重派时须【从盘上继续: 交卷单直接填 · 沙盒不要重拷 · 补 README · 补分片】 ⇒ ★"
    "★**本 job 实测受保护 5 件逐字节未变** (板 611b869e… mtime 2026-11-06 07:07:17 · .kicad_pro "
    "3e504d2b… · 网表 37f62ac3… · 脚表 a4270120… · BOM 5d02bece…) ⇒ 零写板 · 零落表 仍成立 ★"
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
        it["status"] = "open"
        it["dispatched_at"] = None
        it["note"] = (it.get("note") or "") + NOTE
        print(" - ISS-287 fixing → open (僵尸回滚, 待本 job 续做重派)")

        shutil.copy2(LOG, BAK)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("备份: %s" % BAK)


if __name__ == "__main__":
    main()
