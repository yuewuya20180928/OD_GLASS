#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★补派 ISS-353 / ISS-354 cont1 (cron 775d9893 · 2026-11-23 04:55)★
★**为什么补派**: 兄弟 job fb67af40 那一趟 cron 自己超时 (cron: job execution timed out)
   ⇒ 它派出的 sw-lead / hw-lead 两个子会话在同一瞬间被连带 abort ⇒ 两条都成了【僵尸 fixing】
   (status=fixing 但无 HANDOFF 页 + 分片命中 0) ⇒ 队列断线。
★**处置**: 沿用本仓既有惯例 (ISS-345 cont1/cont1b / ISS-349 cont1 都是这么救的):
   status 保持 fixing (不落 open ⇒ 兄弟 job 的 advance.py --json 看不见 ⇒ 不会重复派)
   + 写 dispatch_log + 派 cont1 brief + spawn。
★**边界**: 零写板 · 零落表(issue_log 本单不改 status, 只在 dispatch_log 追加) · 零外发
"""
import os, yaml, shutil, datetime as dt

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DL = os.path.join(PROJ, "state", "dispatch_log.yaml")

JOBS = [
    ("ISS-353", "sw-lead", "ISS-353_sw_rk3572_target_caliber_cleanup_cont1.md"),
    ("ISS-354", "hw-lead", "ISS-354_hw_demo_board_manufacturability_closure_cont1.md"),
]
JOB_NOTE = ("cron 775d9893 (ARS45 继续执行后继计划) · ★补派 cont1 时刻 2026-11-23 04:5x·"
            "★status 保持 fixing ⇒ 兄弟 job fb67af40 的 advance.py --json 看不见本单 ⇒ 不会重复派★"
            " ★★**死因 = 兄弟 job fb67af40 那一趟 cron 超时 (cron: job execution timed out)"
            " ⇒ 连带 abort 了它的两个子会话 (endedAt 相差 114ms) ⇒ 本单成僵尸 fixing"
            " (无 HANDOFF 页 + 分片命中 0)**★ ★本 job 04:4x 已本机实读确认: "
            "iss353 已在盘 7 件 logs (含全仓扫描名单 1984 文件/355 命中/86 结论矛盾) · "
            "iss354 已在盘 4 份官方 datasheet PDF ⇒ 两单都从已完成位置续做, 不是从零★")

raw = yaml.safe_load(open(DL, encoding="utf-8"))
assert isinstance(raw, list), "dispatch_log.yaml 顶层不是 list ⇒ 拒绝写"
before = len(raw)

for issue, agent, brief in JOBS:
    bp = os.path.join(PROJ, "state", "dispatch_briefs", brief)
    assert os.path.exists(bp), "brief 不存在: " + bp
    btxt = open(bp, encoding="utf-8").read()
    raw.append({"issue": issue, "agent": agent, "at": dt.date.today().isoformat(),
                "brief": btxt[:300], "job": JOB_NOTE})

# 追加式写回 (保留历史字节不动)
old = open(DL, encoding="utf-8").read()
chunk = yaml.safe_dump(raw[before:], allow_unicode=True, sort_keys=False, width=200)
if old and not old.endswith("\n"):
    chunk = "\n" + chunk
with open(DL, "a", encoding="utf-8") as f:
    f.write(chunk)

# 自检
chk = yaml.safe_load(open(DL, encoding="utf-8"))
assert len(chk) == before + len(JOBS), "条目数不符: %d != %d" % (len(chk), before + len(JOBS))
assert chk[-1]["issue"] == "ISS-354" and chk[-2]["issue"] == "ISS-353", "末两条不对"
print("DISPATCH_LOG_OK before=%d after=%d" % (before, len(chk)))
print("TAIL:", chk[-2]["issue"], "|", chk[-1]["issue"])
