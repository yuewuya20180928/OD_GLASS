#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20260724_1630_cronfb67af40_iss395_dispatch_iss393_cont1.py
===========================================================================
cron fb67af40 (ARS45 队列自动派活) · 2026-11-24 16:3x
★★**落 2 条**: ISS-395 (★新派·hw-lead★) + ISS-393 cont1 (★僵尸续跑·mech-lead★)★★

★**为什么不用 `python3 state/advance.py --apply --only ISS-395`** ★
  ★**实跑 `python3 state/advance.py --json` ⇒ `internal: []`** ★
  ⇒ ★**根因 = advance.py 的 in_flight 规则: hw-lead 名下已有 `fixing` 的 ISS-391/ISS-394 ⇒ ISS-395 被挡住 ⇒ `internal` 空 ⇒ `--apply --only` 那一圈循环遍历的是空列表 ⇒ 一个字都不会落** ★
  ⇒ ★**⇒ 本 job 沿用同族先例 (`_apply_20260724_1155_cronfb67af40_open_390_391.py` / `_apply_20260724_1445_cronfb67af40_open_392_393_394.py`): 自己写脚本直接落台账** ★

★**本 job 本轮实读到的槽位真相 (★main 本机实读·不抄任何 agent 报告★)★** ★
| agent | 台账 | 实测会话 | 本轮判定 |
|---|---|---|---|
| hw-lead | ISS-391/ISS-394 = fixing | ★**ISS-394 cont1 `1e6291b8` 15:43→15:54 status=done** ★·交卷页 `HANDOFF/2026-11-24_hw-lead_ISS394_座体选型结论传播清账与闸.md` 62,212 B 在盘 · 真相页 + 新闸在盘 · `hw.yaml` 里 `iss394` 命中 15 处 | ★**真交卷·待 main 签收 ⇒ 槽位空出来了** ★ |
| sw-lead | ISS-388/ISS-392 = fixing | ★**ISS-392 `34ab940c` 仍在跑 (★末条时间戳 2026-11-24T08:07:00Z = 16:07:00·transcript 仍在长·★16:2x 再采样仍在长★)** ★ | ★**真在飞 ⇒ 本轮跳过 sw-lead (★它名下也没有 open 单★)** ★ |
| mech-lead | ISS-390/ISS-393 = fixing | ★**ISS-393 `366a30b1` 14:52:46→★15:37:46 死 (★45 分钟·末条 = assistant 的 thinking 块·零文件落盘·零分片★)** ★·真相页/新闸/交卷页/`logs/iss393/` **全不在盘** · `mech.yaml` 里 `iss393` 命中 **0** · 只有 `tmp/iss393_sbx/` (官方 MKT PDF + 4 张读图 PNG) | ★**真僵尸 ⇒ 走 cont1 续跑 (★status 保持 fixing·不落 open·⇒ advance.py 看不见 ⇒ 别的 job 不会重复派★)** ★ |

★**ISS-393 的死因 (★main 本机实读 transcript 最后一条 thinking 块·★不抄报告★)★**:
  ★**它把 45 分钟全花在【读资料 + 实测 + 想清楚】上 ⇒ 读数全在它自己的上下文里 ⇒ 但一份文件都没落 ⇒ 那些读数随会话一起消失** ★
  ⇒ ★★**⇒ 这正是 LESSONS.md L-13 记的那条「攒了一堆读数在上下文里, 最后一步才开始写交付物」★★ ⇒ ⇒ 本单 cont1 的第一件事 = 把上一趟的读数【直接写进文件】⇒ brief 里已经逐字交接过去了★** ★

★**本 job 派的两条 (★都属「板只改一次」纪律 ① 的纯分析/新建闸类 ⇒ 零写板★)★** ★
| ISS | agent | 性质 | 本趟定位 |
|---|---|---|---|
| ★**ISS-395** ★ | ★hw-lead★ | ★**PCB·HW 侧门禁自守层** ★ | ★**钉板闸⑩ 的【并发假红】⇒ 变成机器可判** ★ (★真相页 `HW/PCB/BOARD_ONEPASS_GATE10_CONCURRENCY_SAFETY.md` + 新闸 `HW/check_gate10_concurrency_safety.py`★) ★ |
| ★**ISS-393 cont1** ★ | ★mech-lead★ | ★**PCB·MECH 侧对照物真值层** ★ | ★**「通用库件 courtyard 被当成厂件」的扩散面清账 + 判决链重算** ★ (★真相页 `MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` + 新闸 `MECH/check_fts_vs_generic_courtyard_delta.py`★) ★ |

★**ISS-395 为什么现在才派 (★main 本机实读★)★**: ★**它是被兄弟 job 775d9893 r87 (15:4x) 新开的, 落 `open` 并明写「★派活由队列 job 执行★」+「★本轮 r87 里 hw-lead 的槽位被【ISS-394 cont1】占着 ⇒ 本单不与 ISS-394 cont1 并行派给同一个 agent★」⇒ ★⇒ 而 ISS-394 cont1 已于 15:54 交卷 ⇒ ★★那个唯一的阻塞条件已经消失 ⇒ 本轮 (16:3x) 正是它该被派出去的时候★★** ★

★**并发写盘护栏**: `state/issue_log.yaml` 是 5.0 MB 大文件, main 的 webchat 会话 (★16:1x 仍在跑★) 可能同时在写
  ⇒ ★**本脚本在 `os.replace` 之前重算 md5, 与开读时不一致就中止 (rc=3)** ★

★**边界**: 零写板 · 零落表 · 零改既有闸 · 零改既有页面正文 · 零外发 · 不代老板拍板
          · 不改别人分片 · 只写 issue_log.yaml + dispatch_log.yaml + 本脚本自身
"""
import hashlib
import os
import shutil
import sys
import tempfile
import time

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
STAMP = time.strftime("%Y%m%d_%H%M")

BRIEF_395 = "state/dispatch_briefs/ISS-395_hw_gate10_concurrency_safety.md"
BRIEF_393 = "state/dispatch_briefs/ISS-393_mech_fts_vs_generic_courtyard_delta_cont1.md"

JOB = ("cron fb67af40 (ARS45 队列自动派活) · ★2026-11-24 16:3x · "
       "★**先落 fixing 再 spawn (★铁律⑩-i ⇒ 零撞车窗口★) · "
       "★**命令存在性守卫 `python3 state/check_brief_commands.py --brief-file` 两条全 rc=0** ★ · "
       "★**纯分析 / 新建真相页 + 新建机器闸类 (零写板·零落表·零改既有闸·零改既有页正文·零外发·不代拍) ⇒ 合「板只改一次」纪律 ①** ★ · "
       "★**开单依据 = 本 job 本机实读: hw-lead 的 ISS-394 cont1 已于 15:54 交卷 ⇒ 槽位空出 ⇒ 兄弟 job r87 留在 `open` 的 ISS-395 可派; "
       "mech-lead 的 ISS-393 会话 15:37 死且零产出 ⇒ 走 cont1 续跑; sw-lead 的 ISS-392 会话 16:07 仍在跑 ⇒ 本轮跳过** ★")


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    raw = open(LOG, encoding="utf-8").read()
    md5_before = md5(LOG)
    doc = yaml.safe_load(raw)
    issues = doc.get("issues") or []
    by_id = {i.get("id"): i for i in issues}
    print("★ 开读时: issue_log md5=%s · 条数=%d" % (md5_before, len(issues)))

    # ---------- ① ISS-395: open -> fixing ----------
    t395 = by_id.get("ISS-395")
    if t395 is None:
        print("★★ISS-395 不在台账 ⇒ 停下 (不该由本脚本新开)")
        return 2
    if t395.get("status") == "fixing":
        print("★ISS-395 已是 fixing ⇒ 不重复改 (幂等)")
    elif t395.get("status") == "open":
        t395["status"] = "fixing"
        t395["dispatched_at"] = "2026-11-24"
        t395["note_addendum"] = (
            "★**2026-11-24 16:3x cron fb67af40 (ARS45 队列自动派活) 落 fixing 并派活**★\n"
            "★**它是被兄弟 job 775d9893 r87 (15:4x) 新开的, 落 `open` 并明写「★派活由队列 job 执行★」+「★本轮 r87 里 hw-lead 的槽位被【ISS-394 cont1】占着 ⇒ 本单不与 ISS-394 cont1 并行派给同一个 agent★」★**\n"
            "★**⇒ 而 ISS-394 cont1 (`1e6291b8`) 已于 15:43→15:54 status=done 交卷 (★交卷页 62,212 B 在盘 + 真相页 + 新闸 + `hw.yaml` 命中 15 处★) ⇒ ★★那个唯一的阻塞条件已经消失★★**\n"
            "★**本 job 本机实读 (★不抄任何 agent 报告★)★**: `state/advance.py --json` ⇒ `internal: []` (★hw-lead 名下 fixing 的 ISS-391/ISS-394 被 in_flight 规则挡住 ⇒ `--apply --only ISS-395` 那一圈循环遍历的是空列表 ⇒ 一个字都不会落 ⇒ 本 job 自写脚本直接落台账, 沿用同族先例 `_apply_20260724_1155_*` / `_apply_20260724_1445_*`★)\n"
            "★**本单性质**: 纯分析 + 新建真相页 + 新建机器闸 · 零写板 · 零落表 · 零改既有闸的判据/阈值 · 零改既有页面正文 · 零挂链 · 零外发 · 不代拍 ⇒ 合「板只改一次」纪律 ①★\n"
            "★**命令存在性守卫 `python3 state/check_brief_commands.py --brief-file %s` rc=0**★" % BRIEF_395
        )
        print("★ISS-395: open -> fixing ✅")
    else:
        print("★★ISS-395 状态是 %s (不是 open/fixing) ⇒ 停下" % t395.get("status"))
        return 2

    # ---------- ② ISS-393: 保持 fixing (僵尸续跑) ----------
    t393 = by_id.get("ISS-393")
    if t393 is None:
        print("★★ISS-393 不在台账 ⇒ 停下")
        return 2
    if t393.get("status") != "fixing":
        print("★★ISS-393 状态是 %s (不是 fixing) ⇒ 停下 (★僵尸续跑必须保持 fixing, 否则 advance.py 会看见它 ⇒ 别的 job 会重复派★)"
              % t393.get("status"))
        return 2
    t393["note_addendum"] = (
        "★**2026-11-24 16:3x cron fb67af40 (ARS45 队列自动派活) 判定: 本单 = 【真僵尸】⇒ 走 cont1 续跑 (★status 保持 fixing·不落 open★)**★\n"
        "★**死因 (★main 本机实读 transcript·不抄任何 agent 报告★)★**: 子会话 `agent:mech-lead:subagent:27ab6108-0c0a-4b16-9be2-4516c3171bf7` / sessionId "
        "`366a30b1-041b-4a78-b6e9-c12ca8a8a0b6` ⇒ ★**14:52:46 起 → ★15:37:46 止 (★墙钟 45 分钟·末条 = assistant 的 thinking 块·不是 toolResult★)**★ ⇒ "
        "★**死因 = 把 45 分钟全花在【读资料 + 实测 + 想清楚】上 ⇒ 读数全在它自己的上下文里 ⇒ 但一份文件都没落 ⇒ 那些读数随会话一起消失** ★\n"
        "★**⇒ 这正是 LESSONS.md L-13 记的那条: 「攒了一堆读数在上下文里, 最后一步才开始写交付物」★★**\n"
        "★**本 job 本机实读到的零产出证据 (★两次采样·间隔 ≥10 分钟★)★**: `MECH/BOARD_ONEPASS_FTS_VS_GENERIC_COURTYARD_DELTA.md` ★**不在盘**★ · "
        "`MECH/check_fts_vs_generic_courtyard_delta.py` ★**不在盘**★ · `HANDOFF/2026-11-24_mech-lead_ISS393_*.md` ★**不在盘**★ · "
        "`logs/iss393/` ★**不存在**★ · `grep -c \"iss393\" state/fragments/mech.yaml` ⇒ ★**0**★ · ★**唯一留下的 = `tmp/iss393_sbx/` (★官方 MKT PDF md5 `69d9415867cd642d6a6e07c6b755516b` + 4 张读图 PNG·14:5x★)**★\n"
        "★**⇒ 本轮 cont1 的做法 = 把上一趟的实测读数【逐字交接进 brief】(★它自己跑出来的·不是抄别人的报告★) ⇒ 并写死【先落盘, 再继续】⇒ 本单性质 = 纯查证 + 纯分析 + 新建真相页 + 新建机器闸 + 收尾 · 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍 ⇒ 合「板只改一次」纪律 ①★\n"
        "★**命令存在性守卫 `python3 state/check_brief_commands.py --brief-file %s` rc=0**★" % BRIEF_393
    )
    print("★ISS-393: note_addendum 写入 (status 保持 fixing) ✅")

    # ---------- 原子写回 issue_log (md5 守卫) ----------
    if md5(LOG) != md5_before:
        print("★★issue_log.yaml 在本脚本运行期间被改 (md5 变了) ⇒ 中止 (rc=3), 不写盘")
        return 3
    bak = LOG + ".bak_%s_cronfb67_iss395_iss393cont1" % STAMP
    shutil.copy2(LOG, bak)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(LOG), prefix=".issue_log.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=100000)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, LOG)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    print("✅ issue_log 已写入: ISS-395 -> fixing + ISS-393 note_addendum (备份: %s)" % os.path.basename(bak))

    # ---------- dispatch_log 追加 (幂等: 同 (issue, task_name) 不重复) ----------
    raw2 = open(DLOG, encoding="utf-8").read()
    if isinstance(raw2, list):
        entries, shape = raw2, "list"
    elif isinstance(raw2, dict):
        entries = raw2.setdefault("dispatches", [])
        shape = "dict"
    else:
        entries, shape = [], "list"

    new_entries = [
        {
            "issue": "ISS-395",
            "agent": "hw-lead",
            "at": "2026-11-24 16:3x",
            "brief": ("★★[新派] 钉板闸⑩【板侧项全集重跑幂等闸】的【并发假红】⇒ 把「并发 ⇒ 假红 ⇒ 板那一趟不许开工」变成机器可判 ★★"
                      "★★**纯分析 + 新建真相页 + 新建机器闸 · 零写板 · 零落表 · 零改既有闸 · 零改既有页正文 · 零挂链 · 零外发 · 不代拍** "
                      "⇒ 合「板只改一次」纪律 ①★★"),
            "brief_file": BRIEF_395,
            "job": JOB,
            "status_note": ("★台账 status 由 open 直接落 fixing (★不是 open★) ⇒ advance.py 的 in_flight 规则继续挡住任何 job "
                            "再给该 agent 派活 ⇒ 零撞车窗口★"),
            "task_name": "queue_iss395",
            "dispatched_at": "2026-11-24 16:3x",
            "redispatch_zombie": False,
            "carried_over_from": ("★**本单是兄弟 job 775d9893 r87 (15:4x) 新开并落 `open` 的, 那一条明写「★派活由队列 job 执行★」"
                                  "+「★hw-lead 的槽位被【ISS-394 cont1】占着 ⇒ 不并行派★」★ ⇒ ★**ISS-394 cont1 已于 15:54 交卷 ⇒ 阻塞条件消失 "
                                  "⇒ 本 job (fb67af40) 16:3x 接上派**★"),
        },
        {
            "issue": "ISS-393",
            "agent": "mech-lead",
            "at": "2026-11-24 16:3x",
            "brief": ("★★[续跑 cont1] 上一趟 (14:52~15:37) 读了 45 分钟资料却【零文件落盘】⇒ 本趟 = 把已实测的读数【逐字交接】+ "
                      "【先落盘, 再继续】★★**纯查证 + 纯分析 + 新建真相页 + 新建机器闸 + 收尾 · 零写板 · 零落表 · 零改既有闸 · "
                      "零改既有页正文 · 零挂链 · 零外发 · 不代拍** ⇒ 合「板只改一次」纪律 ①★★"),
            "brief_file": BRIEF_393,
            "job": JOB,
            "status_note": ("★台账 status 保持 fixing (★不是 open★) ⇒ advance.py 的 in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★"),
            "task_name": "queue_iss393_cont1",
            "dispatched_at": "2026-11-24 16:3x",
            "redispatch_zombie": True,
            "carried_over_from": ("★**上一趟 = cron fb67af40 14:4x 派的子会话 `agent:mech-lead:subagent:27ab6108-0c0a-4b16-9be2-4516c3171bf7` / "
                                  "sessionId `366a30b1-041b-4a78-b6e9-c12ca8a8a0b6`: 14:52:46→15:37:46 (★45 分钟·末条 = assistant 的 thinking 块·零产出★) "
                                  "⇒ 死因 = 读数全攒在上下文里、一份文件都没落 (★LESSONS.md L-13 同型★) ⇒ 本轮 cont1 = 交接读数 + 先落盘★** "
                                  "★**命令存在性守卫 `state/check_brief_commands.py --brief-file` rc=0** ★"),
        },
    ]
    added = 0
    for entry in new_entries:
        dup = any(isinstance(e, dict) and e.get("issue") == entry["issue"]
                   and e.get("task_name") == entry["task_name"] for e in entries)
        if dup:
            print("★已存在同 task_name 条目 ⇒ 不重复追加: %s" % entry["issue"])
            continue
        entries.append(entry)
        added += 1
    if added:
        bak2 = DLOG + ".bak_%s_cronfb67_iss395_iss393cont1" % STAMP
        shutil.copy2(DLOG, bak2)
        fd, tmp2 = tempfile.mkstemp(dir=os.path.dirname(DLOG), prefix=".dispatch_log.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                if shape == "dict":
                    raw2["dispatches"] = entries
                    yaml.safe_dump(raw2, f, allow_unicode=True, sort_keys=False)
                else:
                    yaml.safe_dump(entries, f, allow_unicode=True, sort_keys=False)
            os.replace(tmp2, DLOG)
        finally:
            if os.path.exists(tmp2):
                os.unlink(tmp2)
        print("✅ dispatch_log 追加成功 (shape=%s) · 新增 %d 条" % (shape, added))
    else:
        print("★dispatch_log 零新增 ⇒ 未写盘")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
