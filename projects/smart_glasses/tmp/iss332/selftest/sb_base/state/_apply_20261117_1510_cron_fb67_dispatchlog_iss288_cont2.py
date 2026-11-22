#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★ISS-288 cont2 派活登记 (cron fb67af40 · 队列自动派活 · 2026-11-17 15:1x)★
只做一件事: 往 state/dispatch_log.yaml 的 `entries` 追加一条续做派活记录。
不动 dispatches (advance.py 的 open→fixing 段写的), 不动 issue_log.yaml, 不碰任何其它文件。
"""
import datetime as dt
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "dispatch_log.yaml")
BAK = LOG + ".bak_20261117_1510_cron_fb67_iss288_cont2"

shutil.copy2(LOG, BAK)

with open(LOG, encoding="utf-8") as f:
    doc = yaml.safe_load(f) or {}

doc.setdefault("entries", [])

already = any(
    isinstance(e, dict)
    and e.get("issue") == "ISS-288"
    and "cont2" in str(e.get("brief", "")) + str(e.get("job", ""))
    for e in doc["entries"]
)
if already:
    print("★已存在 ISS-288 cont2 派活登记 ⇒ 不重复写")
    raise SystemExit(0)

doc["entries"].append({
    "issue": "ISS-288",
    "agent": "sw-lead",
    "at": "2026-11-17",
    "brief": (
        "★★【cont2 · 只干一件事: 把交卷单 §1~§8 的「待写」填完】★★\n"
        "★**前置**: cont1 两条会话 (`agent:sw-lead:subagent:2c3ec2ed` 14:32~14:37 done·aborted / "
        "`agent:sw-lead:subagent:b3f37a1f` 14:32~14:41 timeout) 都中途死掉 ⇒ "
        "★**补丁本体已落盘** (`SW/tools/timing_check.py` md5 `68c4becffe6bcd708e388dba9d18a505` · "
        "本机实跑 `SELFTEST 72/72 通过, rc=0`) ★**分片也已落盘** (`state/fragments/sw.yaml` 里 `iss288` 6 处) "
        "⇒ ★**只剩交卷单 `HANDOFF/2026-11-17_sw-lead_ISS288_timing_check补丁落地.md` = 1787 B · 68 行 · "
        "`grep -c 待写` = 8 条占位符没填** ⇒ ★**本单只补账, 不许重做补丁**★\n"
        "★**任务书全文**: `state/dispatch_briefs/ISS-288_sw_timing_check_patch_land_cont2.md` (8064 B · "
        "`check_brief_commands --brief-file` rc=0)\n"
        "★**边界**: 零写板 · 零落表 · 零改 `SW/tools/timing_check.py` · 零改既有 SW 判据脚本 · "
        "零外发 · 不自签 issue_log · 只写 `HANDOFF/` + 自己的分片"
    ),
    "job": (
        "cron fb67af40 (ARS45 队列自动派活) · ★续做派活 (cont2) · "
        "★派活时刻 2026-11-17 15:1x · session `agent:sw-lead:subagent:b54d24be-b217-4182-90f8-346f4b0ed549` 在飞★ · "
        "★本轮 advance.py 的 internal[] 为空 (三个总工各有在飞单) ⇒ 本条是 main 手动判定「sw-lead 空闲 + ISS-288 半成品」后的续做派活★"
    ),
})

with open(LOG, "w", encoding="utf-8") as f:
    yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=200)

# 回读校验
with open(LOG, encoding="utf-8") as f:
    chk = yaml.safe_load(f)
n = sum(
    1 for e in chk.get("entries", [])
    if isinstance(e, dict) and e.get("issue") == "ISS-288"
)
print("✅ dispatch_log.yaml 已追加 ISS-288 cont2 派活登记 (entries 里 ISS-288 共 %d 条)" % n)
print("   dispatches 段条数 = %d (未动)" % len(chk.get("dispatches", [])))
print("   备份 = %s" % os.path.basename(BAK))
