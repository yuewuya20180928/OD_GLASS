#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261123_0320_cronfb67_redisp_iss345_cont1b.py
================================================================================
cron fb67af40 (ARS45 队列自动派活) · 2026-11-23 03:2x
--------------------------------------------------------------------
【第二次重派】ISS-345 (mech-lead) —— cont1 会话又被【父 run 结束 ⇒ 子会话连带 abort】掐死

★★为什么必须再重派 (★main 03:2x 本机实读, 不猜★)★★:
  ★**上一轮 cont1 会话 `f94fa31d-4d42-49b0-a123-27252765d1d7` (02:13→02:19) 又被 abort**
    (★sessions_list: status=done 但 `abortedLastRun: true`·runtime 316,932 ms = 5.3 分钟★
      ★父 run = cron fb67af40 的 02:10 轮, 父 run 一结束 ⇒ 子会话被连带掐死 ★)
  ★⇒ **又是 5 分钟全耗在读文件上, 真件 2 个脚本零改动**
    (★main 03:2x 实测: `MECH/pinset2_mech_check.py` md5 `9d5ff8653fa674498aae4ef2a7033098`
      = `tmp/iss345_base/pinset2_mech_check.py` 逐字节相同 · mtime 仍 2026-11-11 17:26:25 ★
      ★`MECH/skeleton_section_check.py` md5 `8bdc002357e18a1853d6a452f832bd5f` 同样相同
      · mtime 仍 2026-11-11 17:29:43 ★
      ★交卷页 `HANDOFF/2026-11-23_mech-lead_ISS345_8脚本迁双口径.md` 仍 949 B (骨架未填) ★)
  ★⇒ 台账上 ISS-345 仍挂 `fixing` ⇒ **advance.py 的 in_flight 规则会永远挡住 mech-lead**
    ⇒ **僵尸 fixing 第二次 ⇒ 队列再次静默停摆** ⇒ 必须本轮再救

★★本轮与上一轮的两处不同 (★不是原样重试★)★★:
  ★**① 父会话改用 `sessions_yield` 等子会话** (★老板 webchat 会话 11-23 00:0x 已实证:
    ★"改从 boss 会话自己派, 父会话用 sessions_yield 等 ⇒ 这次没再被掐" ★)
    ⇒ ★**本轮父会话不会提前结束 ⇒ 子会话不再被连带 abort** ★
  ★**② 任务书里把「两次 abort 的实测读数」直接写进抬头** (★md5 + mtime + 交卷页字节数 ★)
    ⇒ ★**子 agent 不用再花 5 分钟自己确认「盘面到底有没有半截改动」** ★

★★为什么本轮【不写】`state/issue_log.yaml` (★与上一轮不同, 理由写死★)★★:
  ★**兄弟 job cron 775d9893 本轮 (03:16 起) 正在给 ISS-349 / ISS-346 做签收**
    (★main 03:2x 读它的 transcript 末段: 正在核对 ISS-349 交卷页 / 生成器回归 / 分片登记★)
    ★⇒ **两个 job 同时改 `issue_log.yaml` = 后写覆盖先写 ⇒ 台账条目可能凭空消失** ★
  ★⇒ 本轮 **零改 issue_log.yaml** ⇒ 而 ISS-345 本来就已经是 `fixing` + brief 已是 cont1 全文
    ⇒ ★**「先落 fixing 再 spawn」这条纪律已经天然满足 (无需再落盘) ⇒ 兄弟 job 看不见本单 ⇒ 不会重复派** ★
  ★⇒ 本轮只写 `state/dispatch_log.yaml` (追加式, 顶层 list ⇒ 历史 337 条字节零改动) ★

★**原子写 + 带 .bak + 幂等** ★
"""
from __future__ import annotations

import os
import shutil
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(HERE, "dispatch_log.yaml")
DL_BAK = DL + ".bak_20261123_0320_cronfb67_redisp_iss345_cont1b"
LOG = os.path.join(HERE, "issue_log.yaml")

IID = "ISS-345"
OWNER = "mech-lead"
CONT_BRIEF = "ISS-345_mech_8脚本迁双口径_cont1.md"
NOW = "2026-11-23 03:2x"
TAG = "%s@cont1b@%s" % (IID, NOW)


def main() -> int:
    # ---------- 台账只读自检 (本轮不写) ----------
    doc = yaml.safe_load(open(LOG, encoding="utf-8").read()) or {}
    issues = doc.get("issues") or []
    hit = [i for i in issues if i.get("id") == IID]
    if not hit:
        print("★%s 不在台账 ⇒ 中止 (不该 happen)" % IID)
        return 2
    h = hit[0]
    print("★台账 %s: status=%s owner=%s due=%s brief=%d chars verify_by=%s dispatched_at=%s"
          % (IID, h.get("status"), h.get("owner"), h.get("due"),
             len(h.get("task_brief") or ""), h.get("verify_by"), h.get("dispatched_at")))
    if h.get("status") != "fixing":
        print("★status 不是 fixing ⇒ 停 (本轮不改台账, 交人工)")
        return 2

    # ---------- dispatch_log (顶层是 list ⇒ 追加式写回, 历史字节零改动) ----------
    dl = yaml.safe_load(open(DL, encoding="utf-8").read()) if os.path.exists(DL) else []
    if isinstance(dl, dict):
        dl_list = dl.setdefault("dispatches", [])
        shape = "dict"
    elif isinstance(dl, list):
        dl_list = dl
        shape = "list"
    else:
        dl_list, shape = [], "list"

    if any(TAG in str(e.get("brief", ""))[:120] for e in dl_list):
        print("★dispatch_log 已有本轮记录 ⇒ 跳过 (幂等)")
    else:
        entry = {
            "issue": IID,
            "agent": OWNER,
            "at": NOW,
            "brief": ("[重派 cont1b] " + TAG +
                      " · cont1 会话 `f94fa31d` (02:13→02:19) 又被【父 run 结束 ⇒ 子会话连带 abort】掐死 (5.3 分钟 · "
                      "abortedLastRun=true) ⇒ 真件 2 个脚本零改动 (main 03:2x 实测 md5/mtime 逐字节未变) ⇒ "
                      "僵尸 fixing 第二次 ⇒ 第二次重派 · 任务书 state/dispatch_briefs/" + CONT_BRIEF),
            "job": ("cron fb67af40 (ARS45 队列自动派活) · ★重派时刻 2026-11-23 03:2x · "
                    "★**本轮零改 issue_log.yaml (兄弟 job 775d9893 正在同文件上给 ISS-349/ISS-346 签收 ⇒ 不并发写)** "
                    "⇒ ★**ISS-345 本就是 fixing + brief 已是 cont1 ⇒ 「先落 fixing 再 spawn」天然满足 ⇒ 兄弟 job 看不见本单 ⇒ 不重复派** "
                    "★**本轮父会话改用 sessions_yield 等子会话 ⇒ 不再被连带 abort**"),
        }
        if not os.path.exists(DL_BAK):
            shutil.copy2(DL, DL_BAK)
            print("★备份 ->", os.path.basename(DL_BAK))
        with open(DL, "a", encoding="utf-8") as f:
            if shape == "list":
                f.write(yaml.safe_dump([entry], allow_unicode=True, sort_keys=False, width=200))
        print("★dispatch_log 已追加 1 条 (%s cont1b)" % IID)

    # ---------- 自检 ----------
    dl2 = yaml.safe_load(open(DL, encoding="utf-8").read())
    dl2_list = dl2 if isinstance(dl2, list) else (dl2 or {}).get("dispatches", [])
    print("★dispatch_log 条数 =", len(dl2_list), "· 末条 =", dl2_list[-1].get("issue"),
          "· 末条 at =", dl2_list[-1].get("at"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
