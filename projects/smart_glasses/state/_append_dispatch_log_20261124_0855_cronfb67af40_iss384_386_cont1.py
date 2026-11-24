#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-24 08:5x · job fb67af40「ARS45 队列自动派活」
★dispatch_log 追加两条: ISS-384 (hw-lead) 与 ISS-386 (mech-lead) 的【僵尸 fixing 重派 cont1】★
=========================================================================================
★**为什么需要这个脚本 (★不是走 advance.py --apply★)**:
  · `advance.py --apply --only <ISS-ID>` 只处理 `internal` 段 ⇒ ★**只有 status=open 的单进得来** ★
  · ISS-384 / ISS-386 现状 status=`fixing` (★08:3x 那轮派出去的★) ⇒ --apply 会跳过 ⇒ 派活日志写不进去
  · ⇒ 本脚本只做一件事: ★**原子追加两条 dispatch_log 条目** ★ (不动 issue_log · 不动 status · 不碰板)
★**为什么可以安全重派 (★本轮 main 实测·不是抄任何 agent 报告★)**:
  · ISS-384 会话 `agent:hw-lead:subagent:5c3ed7dd` = ★**08:28:42 起 · 08:45:35 止 · runtimeMs 1,010,660 (≈16.8 分钟) · status=timeout + abortedLastRun=true** ★
  · ISS-386 会话 `agent:mech-lead:subagent:c8ed675b` = ★**08:28:50 起 · 08:45:36 止 · runtimeMs 993,331 (≈16.6 分钟) · status=timeout + abortedLastRun=true** ★
  · ★**两条都被 ~16.5 分钟的墙掐死** (★同一时刻 ⇒ 是墙, 不是 agent 自己停★)
  · ★**但不是零产出**: 两条的交付物【全在盘】(main 08:46~08:47 实读 md5/size/mtime) ⇒ ★**这是【收尾趟】, 不是重做★**
  · ★**真正缺的是【交卷消息】** ⇒ transcript 末行 = "Aborted" ⇒ main 拿不到交卷 ⇒ 签收闸无法走
★**防撞车 (★本轮的做法★)**:
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
BAK = DL + ".bak_20261124_0855_cronfb67af40_iss384_386_cont1"

TS = "2026-11-24 08:55"
JOB = "cron fb67af40 (ARS45 队列自动派活)"

ENTRIES = [
    {
        "issue": "ISS-384",
        "agent": "hw-lead",
        "at": TS,
        "brief": (
            "★★[cont1 续派] 「充电电流档位活值口径收口」: 0.822 旧系数从三份 HW 活文档清干净 + 补 R10 闸的判定面盲区 ★★"
            "★★**纯文档口径订正 + 新建机器闸 · 零写板 · 零落表 · 零改既有闸/既有页面正文 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ①★★"
        ),
        "brief_file": "state/dispatch_briefs/ISS-384_hw_charge_current_live_value_caliber_cont1.md",
        "job": (
            JOB + " · ★2026-11-24 08:5x · ★**cont1 续派 (★status 保持 fixing 不动·★死因 = 上一趟 08:28:42~08:45:35 被 ~16.8 分钟墙掐死·"
            "★四件交付物【全在盘】(真相页 22,908 B@08:38:41 / 新闸 21,898 B@08:38:59 / 交卷页 22,304 B@08:39:59 / frag hw.yaml 736,680 B@08:40:28)"
            "·★缺的只是【交卷消息】·★本趟只做独立复核 + 交卷·★不许重做★)** ★ · ★**命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0** ★"
        ),
        "status_note": "★台账 status 保持 fixing (未改) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★",
        "session_key": "agent:hw-lead:subagent:df40732e-72cd-44a8-9f90-c2c1d24b2a10",
        "run_id": "7ab22f57-e8d1-42a6-88b8-4f2e6f47e0d4",
        "task_name": "queue_iss384_cont1",
        "dispatched_at": "2026-11-24 08:5x",
        "prev_session_key": "agent:hw-lead:subagent:5c3ed7dd-3483-49e4-91a4-8f3625fa4212",
        "redispatch_zombie": True,
        "death_cause": (
            "★上一趟会话 08:28:42~08:45:35 · runtimeMs 1,010,660 (≈16.8 分钟) · status=timeout + abortedLastRun=true "
            "⇒ 被 ~16.5 分钟墙掐死 ⇒ 交付物全在盘但零交卷★"
        ),
        "zero_delivery": False,
        "partial_delivery": "4/4 交付物在盘 · 缺交卷消息",
    },
    {
        "issue": "ISS-386",
        "agent": "mech-lead",
        "at": TS,
        "brief": (
            "★★[cont1 续派] 「板只改一次」那一趟的 J_DEBUG + J_UART 两连接器【座体/开口/清空区 三件合到一件答】★★"
            "★★**纯分析 + 新建机器闸 + 沙盒预演 · 零写板 · 零落表 · 零改已签收件 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ①★★"
        ),
        "brief_file": "state/dispatch_briefs/ISS-386_mech_debug_seat_3d_fit_combined_cont1.md",
        "job": (
            JOB + " · ★2026-11-24 08:5x · ★**cont1 续派 (★status 保持 fixing 不动·★死因 = 上一趟 08:28:50~08:45:36 被 ~16.6 分钟墙掐死·"
            "★三件交付物【全在盘】(真相页 51,765 B@08:37:11 / 新闸 60,272 B@08:37:22 / 交卷页 24,733 B@08:38:40 / frag mech.yaml 731,052 B@08:39:18)"
            "·★缺的只是【交卷消息】·★本趟只做独立复核 + 交卷·★不许重做·★selftest 上限 6 分钟·超时就引用 logs/iss386/gate_selftest.txt 并如实写明★)** ★ · "
            "★**命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0** ★"
        ),
        "status_note": "★台账 status 保持 fixing (未改) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★",
        "session_key": "agent:mech-lead:subagent:41b12d57-60a6-4a65-96bf-c89e5ade01da",
        "run_id": "bc38f49f-9b13-42ac-b010-d71d8427185d",
        "task_name": "queue_iss386_cont1",
        "dispatched_at": "2026-11-24 08:5x",
        "prev_session_key": "agent:mech-lead:subagent:c8ed675b-e328-498f-8030-f3c86e846b07",
        "redispatch_zombie": True,
        "death_cause": (
            "★上一趟会话 08:28:50~08:45:36 · runtimeMs 993,331 (≈16.6 分钟) · status=timeout + abortedLastRun=true "
            "⇒ 被 ~16.5 分钟墙掐死 ⇒ 交付物全在盘但零交卷★"
        ),
        "zero_delivery": False,
        "partial_delivery": "3/3 交付物在盘 · 缺交卷消息",
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

    # ★幂等: 同 (issue, session_key) 已在盘 ⇒ 不重复追加
    added = 0
    for entry in ENTRIES:
        dup = any(
            isinstance(e, dict)
            and e.get("issue") == entry["issue"]
            and e.get("session_key") == entry["session_key"]
            for e in entries
        )
        if dup:
            print(f"★已存在同 session_key 条目 ⇒ 不重复追加: {entry['issue']} (rc=0)")
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
    print(f"✅ dispatch_log 追加成功 (shape={shape}) · 新增 {added} 条 · 条目数 → {n_after}")
    print(f"   备份: {os.path.basename(BAK)}")
    for e in ENTRIES:
        print(f"   新条目: {e['issue']} → {e['agent']} · {e['session_key']} · task={e['task_name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
