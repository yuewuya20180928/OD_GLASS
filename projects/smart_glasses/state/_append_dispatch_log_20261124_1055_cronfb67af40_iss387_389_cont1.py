#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-24 10:5x · job fb67af40「ARS45 队列自动派活」
★dispatch_log 追加三条: ISS-387 (hw-lead) · ISS-388 (sw-lead) · ISS-389 (mech-lead) 的【僵尸 fixing 重派 cont1】★
=========================================================================================
★**为什么需要这个脚本 (★不是走 advance.py --apply★)**:
  · `advance.py --apply --only <ISS-ID>` 只处理 `internal` 段 ⇒ ★**只有 status=open 的单进得来** ★
  · ISS-387 / ISS-389 现状 status=`fixing` (★09:45 那轮派出去的★) ⇒ --apply 会跳过 ⇒ 派活日志写不进去
  · ⇒ 本脚本只做一件事: ★**原子追加两条 dispatch_log 条目** ★ (不动 issue_log · 不动 status · 不碰板)
★**为什么可以安全重派 (★本轮 main 实测·不是抄任何 agent 报告★)**:
  · ISS-387 会话 `agent:hw-lead:subagent:5170b697` = ★**09:45:20 起 · 10:10:23 止 · 墙钟 25.05 分钟** ★
  · ISS-389 会话 `agent:mech-lead:subagent:c6a0fb40` = ★**09:45:58 起 · 10:11:09 止 · 墙钟 25.18 分钟** ★
  · ★**两条都是 25 分钟整** ⇒ ★**死因 = spawn 时给的 `runTimeoutSeconds=1500` 到点被掐** ★
    (★main 本机实算: 09:45:20 + 1500s = 10:10:20 ≈ 实测 10:10:23 止 ⇒ 逐字对齐⇒ 不是墙, 是本 job 自己给的上限★)
  · ★**但不是零产出**:
    - ISS-387 ⇒ 真相页 `HW/PCB/BOARD_ONEPASS_FTS_SINGLE_ROW_LAND_TRUTH.md` 44,122 B @10:10:03 ✔ (★机器块 json.loads rc=0★)
                    ★**但新闸 `HW/check_fts_single_row_land_truth.py` 一次都没开写** ★ (★掐死在写闸之前★)
    - ISS-389 ⇒ 要求单 `MECH/BOARD_ONEPASS_DEBUG_SEAT_REWORK_SPEC.md` 65,851 B @10:08:14 ✔
                    + 新闸 `MECH/check_debug_seat_rework_spec.py` 47,102 B @10:08:25 ✔ (★main 本机实测裸跑 rc=0 判据 472 条 · selftest rc=0 17/17★)
                    ★**但交卷页没落盘** ★ (★最后一趟 toolCall = 写交卷页, 被掐在半路, 无 toolResult★)
  · ⇒ ISS-387 = 【续做趟】(闸还没写) · ISS-389 = 【收尾趟】(只剩交卷页 + 分片)
★**本轮已做的修正 (★真病灶, 不是猜★)**:
  · ★**runTimeoutSeconds: 1500 → 2400** (★40 分钟·本轮已按此 spawn★) ⇒ 同一死因不会再发生第二次
  · ★**cont1 brief 里把 `python3 state/check_footprint_geom.py` 改成真命令 `bash state/pcbnew_py.sh state/check_footprint_geom.py`**
    (★main 本机实测: 裸 python3 ⇒ `ModuleNotFoundError: No module named 'pcbnew'` rc=1; 带包装器 ⇒ rc=0 末行「✅ 几何全对」★)
★**防撞车 (★本轮的做法·照 08:55 cont1 先例★)**:
  · ★**status 保持 `fixing` 不动** ⇒ 兄弟 job 775d9893 与下一轮 fb67af40 读的是同一个字段 ⇒ 它们看到 fixing 就不会再派 ⇒ ★**零撞车窗口** ★
  · ★**dispatch_log 里本条用 `redispatch_zombie` 标记** ⇒ 事后查得清「这一趟是复活, 不是重复」 ★
★**边界**: ★**只追加 dispatch_log.yaml 一个文件** ⇒ 不碰 issue_log / 分片 / 板 / 网表 / 脚表 / BOM / outbox / 决策页 ★
"""
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(HERE, "dispatch_log.yaml")
BAK = DL + ".bak_20261124_1055_cronfb67af40_iss387_389_cont1"

TS = "2026-11-24 10:55"
JOB = "cron fb67af40 (ARS45 队列自动派活)"

ENTRIES = [
    {
        "issue": "ISS-388",
        "agent": "sw-lead",
        "at": TS,
        "brief": (
            "★★[cont1 续派] 「两道已签收 SW 闸今天真的坏了」: 诊断已做完, ★**本趟只做【诊断页 + 新闸 + 交卷页 + 分片 + 交卷】** ★★"
            "★★**纯分析 + 新建闸 + 诊断 · 零写板 · 零落表 · 零改既有闸的判据/阈值 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ①★★"
        ),
        "brief_file": "state/dispatch_briefs/ISS-388_sw_gate_failure_diagnosis_cont1.md",
        "job": (
            JOB + " · ★2026-11-24 11:0x · ★**cont1 续派 (★status 保持 fixing 不动·★死因 = 上一趟 09:45:40~10:55:12 墙钟 69.5 分钟"
            "·★掐死在【写新闸 SW/tools/check_sw_gate_health.py 的那一刻】(transcript 末行 = write 的参数里已有新闸源码开头, 但无 toolResult ⇒ 没落盘)"
            "·★三件交付物【零】在盘 (诊断页/新闸/交卷页) · 分片登记 0 条"
            "·★但两道闸的失效已【实测复现】(闸1: 默认 TMPDIR 10/11 FAIL vs TMPDIR=\$PWD/tmp 11/11 PASS ⇒ 环境耦合; 闸2: 裸跑 5/7 rc=1 + selftest 0/10 ⇒ 账本漂移)"
            "·★SW 域 13 道闸的 roster 画像已由 main 从 /tmp 抢救到 logs/iss388/roster_profile_20261124_1049.jsonl (★直接用, 勿重跑)"
            "·★本轮 runTimeoutSeconds 2400 (40 分钟)·★本趟是【续做趟】不是重做)** ★ · "
            "★**命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0** ★"
        ),
        "status_note": "★台账 status 保持 fixing (未改) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★",
        "session_key": "agent:sw-lead:subagent:queue_iss388_cont1",
        "task_name": "queue_iss388_cont1",
        "dispatched_at": TS,
        "prev_session_key": "agent:sw-lead:subagent:54b0b1d5-02b2-4f5f-898a-119e633f0448",
        "redispatch_zombie": True,
        "death_cause": (
            "★上一趟会话 09:45:40~10:55:12 · 墙钟 69.5 分钟 · transcript 141 行 (77 toolCall) · status=done+abortedLastRun=true "
            "⇒ 掐死在【写新闸 SW/tools/check_sw_gate_health.py 的 write 调用】上 (参数里已有源码开头, 无 toolResult ⇒ 没落盘) "
            "⇒ 三件交付物零在盘 + 分片零登记★"
        ),
        "zero_delivery": True,
        "partial_delivery": "0/3 交付物在盘 · 但两道病闸的失效已实测复现 + SW 域 13 闸 roster 画像已抢救到 logs/iss388/",
    },
    {
        "issue": "ISS-387",
        "agent": "hw-lead",
        "at": TS,
        "brief": (
            "★★[cont1 续派] 「FTS 单排直插原厂 land 几何查证」: 真相页已在盘, ★**本趟只做【新建闸 + 交卷页 + 分片 + 交卷】** ★★"
            "★★**纯查证 + 纯分析 + 新建文档/闸 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ①★★"
        ),
        "brief_file": "state/dispatch_briefs/ISS-387_hw_fts_single_row_land_truth_cont1.md",
        "job": (
            JOB + " · ★2026-11-24 10:5x · ★**cont1 续派 (★status 保持 fixing 不动·★死因 = 上一趟 09:45:20~10:10:23 墙钟 25.05 分钟"
            "= spawn 的 runTimeoutSeconds=1500 到点被掐·★真相页已在盘 44,122 B@10:10:03 但★**新闸一次都没开写**★·"
            "★本轮 runTimeoutSeconds 1500→2400 (40 分钟)·★本趟是【续做趟】不是重做)** ★ · "
            "★**命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0** ★"
        ),
        "status_note": "★台账 status 保持 fixing (未改) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★",
        "session_key": "agent:hw-lead:subagent:queue_iss387_cont1",
        "task_name": "queue_iss387_cont1",
        "dispatched_at": TS,
        "prev_session_key": "agent:hw-lead:subagent:5170b697-022d-4c45-bce0-c87355c7bd3e",
        "redispatch_zombie": True,
        "death_cause": (
            "★上一趟会话 09:45:20~10:10:23 · 墙钟 25.05 分钟 · status=done (transcript 末行 = 编辑真相页机器块) "
            "⇒ 死因 = spawn 的 runTimeoutSeconds=1500 到点被掐 (★main 本机实算 09:45:20+1500s=10:10:20 ≈ 实测 10:10:23 止·逐字对齐·不是墙★) "
            "⇒ 真相页已成但新闸一次都没开写★"
        ),
        "zero_delivery": False,
        "partial_delivery": "1/3 交付物在盘 (真相页) · 缺新闸 + 交卷页 + 分片",
    },
    {
        "issue": "ISS-389",
        "agent": "mech-lead",
        "at": TS,
        "brief": (
            "★★[cont1 续派] 「J_DEBUG / J_UART 两连接器 座体/开口/清空区 三件合到一件」: 要求单+新闸已在盘, ★**本趟只做【交卷页 + 分片 + 交卷】** ★★"
            "★★**纯分析 + 作业包 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改已签收件 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ①★★"
        ),
        "brief_file": "state/dispatch_briefs/ISS-389_mech_debug_seat_rework_spec_cont1.md",
        "job": (
            JOB + " · ★2026-11-24 10:5x · ★**cont1 续派 (★status 保持 fixing 不动·★死因 = 上一趟 09:45:58~10:11:09 墙钟 25.18 分钟"
            "= spawn 的 runTimeoutSeconds=1500 到点被掐·★要求单 65,851 B@10:08:14 + 新闸 47,102 B@10:08:25 都在盘且已跑通 (裸跑 rc=0 判据 472 条·selftest rc=0 17/17)"
            "·★但交卷页没落盘 (最后一趟 toolCall = 写交卷页·被掐在半路)·★本轮 runTimeoutSeconds 1500→2400 (40 分钟)·★本趟是【收尾趟】不许重做)** ★ · "
            "★**命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0** ★"
        ),
        "status_note": "★台账 status 保持 fixing (未改) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★",
        "session_key": "agent:mech-lead:subagent:queue_iss389_cont1",
        "task_name": "queue_iss389_cont1",
        "dispatched_at": TS,
        "prev_session_key": "agent:mech-lead:subagent:c6a0fb40-e81f-41ee-b628-4b811d5970e3",
        "redispatch_zombie": True,
        "death_cause": (
            "★上一趟会话 09:45:58~10:11:09 · 墙钟 25.18 分钟 · status=done (transcript 末行 = 写交卷页的 write 工具调用, 无 toolResult) "
            "⇒ 死因 = spawn 的 runTimeoutSeconds=1500 到点被掐 (★main 本机实算 09:45:58+1500s=10:10:58 ≈ 实测 10:11:09 止·逐字对齐·不是墙★) "
            "⇒ 要求单+新闸在盘但交卷页没落盘★"
        ),
        "zero_delivery": False,
        "partial_delivery": "2/3 交付物在盘 (要求单 + 新闸) · 缺交卷页 + 分片",
    },
]


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

    # ★幂等: 同 (issue, task_name) 已在盘 ⇒ 不重复追加
    added = 0
    for entry in ENTRIES:
        dup = any(
            isinstance(e, dict)
            and e.get("issue") == entry["issue"]
            and e.get("task_name") == entry["task_name"]
            for e in entries
        )
        if dup:
            print(f"★已存在同 task_name 条目 ⇒ 不重复追加: {entry['issue']} (rc=0)")
            continue
        entries.append(entry)
        added += 1

    if added == 0:
        print("★零新增 ⇒ 未写盘 (rc=0)")
        return 0

    shutil.copy2(DL, BAK)
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
    print(f"✅ dispatch_log 追加成功 (shape={shape}) · 新增 {added} 条 · 条目数 {len(entries)} → {n_after}")
    print(f"   备份: {os.path.basename(BAK)}")
    for e in ENTRIES:
        print(f"   新条目: {e['issue']} → {e['agent']} · {e['task_name']} · redispatch_zombie={e['redispatch_zombie']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
