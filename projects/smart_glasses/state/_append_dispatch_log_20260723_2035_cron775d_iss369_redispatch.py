#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-23 20:3x · job 775d9893「ARS45 继续执行后继计划」
★dispatch_log 追加一条: ISS-369 的【僵尸 fixing 重派】★
=========================================================================================
★**为什么需要这个脚本 (★不是走 advance.py --apply★)**:
  · `advance.py --apply --only ISS-369` 只处理 `internal` 段 ⇒ ★**只有 status=open 的单进得来** ★
  · ISS-369 现状 status=`fixing` (★20:10 那轮两个 job 撞车时落的★) ⇒ --apply 会跳过它 ⇒ 派活日志写不进去
  · ⇒ 本脚本只做一件事: ★**原子追加一条 dispatch_log 条目** ★ (不动 issue_log · 不动 status · 不碰板)
★**为什么可以安全重派 (★本轮 main 实查★)**:
  · 20:10 本 job 派的那条 `b4ed5a3e` = ★**53 秒被 kill·零产出** ★
  · 20:10 兄弟 job fb67af40 派的那条 `1ee3c278` = ★**17.8 秒 aborted·零产出** ★
  · ★**三件交付物实测一个都不在盘** (`HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` · `HW/check_fp_libid_truth.py` · `HANDOFF/2026-11-23_hw-lead_ISS369_*.md` 全缺) ★
  · ★**logs/iss369/ 只有 2 件** (00_baseline_md5.txt + 99_INFLIGHT_20260723_2011.md) ⇒ 交卷页/一页/闸全未产出 ★
  · ⇒ ⇒ ★**没有活着的在飞会话 ⇒ 这不是「重复派」, 是「僵尸 fixing 复活」** ★
★**防撞车 (★本轮的做法★)**:
  · ★**status 保持 `fixing` 不动** ⇒ 兄弟 job fb67af40 读的是同一个字段 ⇒ 它看到 fixing 就不会再派 ⇒ ★**零撞车窗口** ★
  · ★**dispatch_log 里本条用 `redispatch_zombie` 标记** ⇒ 事后查得清「这一趟是复活, 不是重复」
★**边界**: ★**只追加 dispatch_log.yaml 一个文件** ⇒ 不碰 issue_log / 分片 / 板 / 网表 / 脚表 / BOM / outbox / 决策页 ★
"""
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
DL = os.path.join(HERE, "dispatch_log.yaml")
BAK = DL + ".bak_20260723_2035_cron775d_iss369_redispatch"

TS = "2026-11-23 20:35"
SESSION_KEY = "agent:hw-lead:subagent:269e0c97-9e67-4ae5-a36f-14a67fa65daf"
RUN_ID = "dd4ce17b-31cc-4575-b8df-df3d8e0ad37f"
TASK_NAME = "advance_iss369"

ENTRY = {
    "issue": "ISS-369",
    "agent": "hw-lead",
    "at": TS,
    "job": "cron 775d9893 (ARS45 继续执行后继计划)",
    "brief": (
        "★2026-11-23 20:3x cron 775d9893 【ISS-369 僵尸 fixing 复活重派】★"
        "★**本轮 advance.py --json 的 internal 段 = [] (0 条) ⇒ 但 main 实查发现 ISS-369 是【僵尸 fixing】★**"
        "⇒ ★**上一轮 (20:10~20:11) 两个 cron job 撞车各派了一条 hw-lead 写会话: 本 job 的 `b4ed5a3e` (53 秒被 kill·零产出) + 兄弟 job fb67af40 的 `1ee3c278` (17.8 秒 aborted·零产出) ⇒ 两条都死了** ★"
        "⇒ ★**main 本机实测三件交付物一个都不在盘** (`HW/PCB/FP_LIBID_TRUTH_WORKPACKET.md` 缺 · `HW/check_fp_libid_truth.py` 缺 · `HANDOFF/2026-11-23_hw-lead_ISS369_板面库封装名写盘作业包.md` 缺) + `logs/iss369/` 只有 2 件 (00_baseline_md5.txt + 99_INFLIGHT_20260723_2011.md) ⇒ 一页/闸/交卷页 全未产出** ★"
        "⇒ ★**⇒ 这不是「重复派」, 是「僵尸 fixing 复活」⇒ 本轮重派一次 (唯一一次在飞)** ★"
        "★**防撞车做法 (★按上一轮 dispatch_log 里自己写的正解执行★)**: ★**status 保持 `fixing` 不动** ⇒ 兄弟 job fb67af40 读同一个字段 ⇒ 它跳过 ⇒ 零撞车窗口 ★"
        "★**任务书逐字照派未改一字** (★brief 取自 issue_log 的 task_brief 原文·只在前面加了一段【执行须知: 项目根路径 + 重派来龙去脉 + 独占写会话 + 板 md5 基线 + 交卷格式】★) ★"
        "★★**本单 PCB 类 = 纯作业包 + 沙盒 + 新建闸 ⇒ 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零挂链 · 零外发 · 不代老板拍板** ★"
        "★★**主线口径**: 板只改一次 ⇒ 本单【不动板】★"
    ),
    "session_key": SESSION_KEY,
    "run_id": RUN_ID,
    "task_name": TASK_NAME,
    "dispatched_at": "2026-11-23 20:34",
    "prev_session_key": "agent:hw-lead:subagent:1ee3c278-4dbb-43fa-a04c-178969c11f34",
    "redispatch_zombie": True,
    "death_cause": (
        "★两条前序会话都死了: `b4ed5a3e` (本 job 20:10 派·53 秒被 kill·重复派撞车) "
        "+ `1ee3c278` (兄弟 job fb67af40 20:10 派·17.8 秒 aborted) ⇒ 零产出★"
    ),
    "zero_delivery": True,
    "partial_delivery": "0/3",
}


def main() -> int:
    raw = yaml.safe_load(open(DL, encoding="utf-8"))
    if isinstance(raw, list):
        entries = raw
        shape = "list"
    elif isinstance(raw, dict):
        entries = raw.setdefault("dispatches", [])
        shape = "dict"
    else:
        entries = []
        shape = "list"

    # ★幂等: 同 (issue, session_key) 已在盘 ⇒ 不重复追加
    for e in entries:
        if (isinstance(e, dict) and e.get("issue") == ENTRY["issue"]
                and e.get("session_key") == ENTRY["session_key"]):
            print("★已存在同 session_key 条目 ⇒ 不重复追加 (rc=0)")
            return 0

    shutil.copy2(DL, BAK)
    entries.append(ENTRY)

    d = os.path.dirname(DL)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".dispatch_log.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if shape == "dict":
                raw["dispatches"] = entries
                yaml.safe_dump(raw, f, allow_unicode=True, sort_keys=False)
            else:
                yaml.safe_dump(entries, f, allow_unicode=True, sort_keys=False)
        os.replace(tmp, DL)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

    after = yaml.safe_load(open(DL, encoding="utf-8"))
    n_after = len(after) if isinstance(after, list) else len(after.get("dispatches", []))
    print(f"✅ dispatch_log 追加成功 (shape={shape}) · 条目数 {len(entries)} → {n_after}")
    print(f"   备份: {os.path.basename(BAK)}")
    print(f"   新条目: {ENTRY['issue']} → {ENTRY['agent']} · {ENTRY['session_key']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
