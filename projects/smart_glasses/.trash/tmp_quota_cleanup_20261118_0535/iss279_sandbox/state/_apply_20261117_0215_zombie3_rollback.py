#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
moli (项目总工) 2026-11-17 02:1x · job fb67af40「ARS45 队列自动派活」
★清 3 条僵尸 fixing (ISS-262 / ISS-263 / ISS-264) ⇒ 回滚 open (本 job 立即重派)★
★+ 暂缓 ISS-181 (真动板那一趟) ⇒ deferred (★等老板 6 个字母, 违「板只改一次」纪律★)★
=========================================================================================
★**实测依据 (★本 job 自己查盘 + 读 transcript, 不抄兄弟 job 的报告★)**:
· 子会话 `agent:hw-lead:subagent:e3daa82b` (e9904bce) 00:41:47 → 00:49:54 · runtime 484s
  · status=done · abortedLastRun=true · transcript 末条停在【读一个脚本的源码】⇒ 死在半路
  · ★**盘上交付物 0 件**: `HANDOFF/` 下无 ISS262 文件 · `state/fragments/hw.yaml` 里 0 处 ISS-262
    (hw.yaml mtime 01:34 = ISS-266 那一跳写的) · 板 611b869e… / 网表 e06c1dd6… 逐字节未动
· 子会话 `agent:sw-lead:subagent:edf27358` (9b4c254e) 00:42:00 → 00:55:01 · runtime 779s
  · status=timeout · abortedLastRun=true · 最后一条 = 在新 conda env (`~/miniconda3/envs/rknn3`)
    里装依赖栈, 死在 pip 下载中途 ⇒ 9 分钟全在下载
  · ★**盘上交付物 0 件**: `HANDOFF/` 下无 ISS263 文件 · `state/fragments/sw.yaml` mtime = 11-16 22:09 (早于本会话)
· 子会话 `agent:mech-lead:subagent:de31bc94` (1f3be957) 00:48:53 → 00:49:55 · runtime 462s
  · status=timeout · abortedLastRun=true · ★**半途改了受保护文件**: 最后一条 = "Successfully replaced
    2 block(s) in MECH/service_port_check.py" ⇒ ★**G5b md5 门禁当场变红** (本 job 实跑
    `MECH/check_demo_struct_truth.py` ⇒ 22/23 组通过, FAIL 组 = G5b:
    `MECH/service_port_check.py` e8dac79ec38f67e572956fd02401a9d4 ≠ 9b24bf985764880f0105aee677fba6a8)
  · ⇒ ★**半成品状态**: 常量已迁到 30mm 口径 (p2_y 15.00 / s2_y 20.00 在盘), 但
    ★**H-1 重基线没做 + 片段没写 + 交卷单没有** ⇒ 必须【续做】不是【从头做】
★**处置**: 三条 status fixing → open (留痕) ⇒ 由本 job 重派 (★一个 agent 一个写会话★)
★**ISS-181 暂缓**: 老板 2026-11-17 00:43 主线 = 绘制 PCB 图 ⇒ ISS-181 已由 deferred 激活成 open;
  ★但【真动板那一趟必须一次做完】(位号改名 + 板侧同步 B-1~B-8 + 布局修正 + 布线 45→0 + Gerber 重出)
  ⇒ 按 ISS-266 交卷单, 这一趟里 **S4 (卡 W-1/W-2 USB ESD 换封装+挪位) 与 S8 (卡 P7/A1/W-4/mech)**
  ★**要老板先拍** ⇒ ★**现在派 = 板改两次 = 违铁律** ⇒ ⇒ status open → deferred, 留触发条件
★**兄弟 job 775d9893 (验收签字 + 决策页) 的分工**: 派活 + 僵尸清理 + 重派 = 本 job ⇒ 不撞车
★**铁律**: 干活的人不许自签 ⇒ verify_by=main
★**不碰**: 任何真源文件 / 任何分片 / PROJECT_TRACKER §0 / outbox / 板 / 网表 / 决策页
"""
import fcntl
import os
import shutil

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BAK = LOG + ".bak_20261117_0215_zombie3"
STAMP = "2026-11-17 02:1x 队列自动派活 job (fb67af40)"

NOTES = {
    "ISS-262": (
        "\n\n★" + STAMP + " **僵尸 fixing 清理 + 重派**: 子会话 "
        "`agent:hw-lead:subagent:e3daa82b` (e9904bce) 00:41:47 → 00:49:54 (runtime 484s · "
        "status=done · abortedLastRun=true) ⇒ transcript 末条停在【读脚本源码】, 死在半路 ⇒ "
        "★**盘上交付物 0 件** (HANDOFF 无 ISS262 · fragments/hw.yaml 里 0 处 ISS-262 · "
        "板 611b869e… / 网表 e06c1dd6… 逐字节未动) ⇒ status fixing → open 重派 ★"
    ),
    "ISS-263": (
        "\n\n★" + STAMP + " **僵尸 fixing 清理 + 重派**: 子会话 "
        "`agent:sw-lead:subagent:edf27358` (9b4c254e) 00:42:00 → 00:55:01 (runtime 779s · "
        "status=timeout · abortedLastRun=true) ⇒ 死在新 conda env 里 pip 下载依赖栈的中途 ⇒ "
        "★**盘上交付物 0 件** (HANDOFF 无 ISS263 · fragments/sw.yaml mtime=11-16 22:09 早于本会话) ⇒ "
        "status fixing → open 重派 ★"
    ),
    "ISS-264": (
        "\n\n★" + STAMP + " **僵尸 fixing 清理 + 【续做】重派 (★不是从头做★)**: 子会话 "
        "`agent:mech-lead:subagent:de31bc94` (1f3be957) 00:48:53 → 00:49:55 (runtime 462s · "
        "status=timeout · abortedLastRun=true) ⇒ ★**半途改了受保护文件**: 末条 = "
        "\"Successfully replaced 2 block(s) in MECH/service_port_check.py\" ⇒ "
        "★**G5b md5 门禁当场变红** (本 job 实跑 MECH/check_demo_struct_truth.py ⇒ 22/23 组通过, "
        "FAIL 组 = G5b: service_port_check.py e8dac79ec38f67e572956fd02401a9d4 ≠ "
        "9b24bf985764880f0105aee677fba6a8) ⇒ ★**半成品**: 三处常量已迁到 30mm 口径 (p2_y 15.00 / "
        "s2_y 20.00 在盘), 但 ★**H-1 重基线没做 + 分片没写 + 交卷单没有** ⇒ "
        "status fixing → open, 重派时须【先核已改的 2 处是否对, 再补 H-1 重基线】 ⇒ ★"
        "★**G5b 红灯在交卷前必须自己转绿, 不许留给下一轮★★"
    ),
}

ISS181_NOTE = (
    "\n\n★" + STAMP + " **暂缓 (deferred) · ★等老板的 6 个字母, 现在派 = 违「板只改一次」铁律★**: "
    "本单 = ★**真动板那一趟**★ (位号改名 + 板侧同步 B-1~B-8 + 布局修正 + 布线 45→0 + Gerber/投产包重出) ⇒ "
    "按 ISS-266 交卷单 (HANDOFF/2026-11-17_hw-lead_ISS266_板只改一次作业包v3.md), 这一趟里 "
    "★**S4 (卡 W-1/W-2: USB ESD 换封装+挪位) 与 S8 (卡 P7/A1/W-4/mech) 必须老板先拍**★ ⇒ "
    "★**先改板 = 板改两次 = 白跑两遍 (Gerber/投产包/留证链全作废)**★ ⇒ "
    "★**触发条件 (拍完任一项即可由 main 重新激活成 open 再派)**: ① A1/A2/A3 (落表 6 字母) "
    "② W-1/W-2/W-4 (ESD 封装/差分负线/Q_PG 源漏) ③ P7 D1~D4 (画哪块板: 现役 160×100 台架板 / "
    "60×15 产品板 / 板宽加到 18~20 / 两块都画) ⇒ ★**本轮队列改派 ISS-262 (hw-lead) 不派本单**★"
)


def main():
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f)
        issues = log["issues"]
        by_id = {it.get("id"): it for it in issues}

        for iid in ("ISS-262", "ISS-263", "ISS-264"):
            it = by_id.get(iid)
            if it is None:
                print("⚠ %s 不存在 ⇒ 跳过" % iid)
                continue
            if it.get("status") != "fixing":
                print("⚠ %s status=%s (不是 fixing) ⇒ 幂等跳过" % (iid, it.get("status")))
                continue
            it["status"] = "open"
            it["dispatched_at"] = None
            it["note"] = (it.get("note") or "") + NOTES[iid]
            print(" - %s fixing → open (僵尸回滚, 待本 job 重派)" % iid)

        it181 = by_id.get("ISS-181")
        if it181 is not None:
            if it181.get("status") == "open":
                it181["status"] = "deferred"
                it181["note"] = (it181.get("note") or "") + ISS181_NOTE
                print(" - ISS-181 open → deferred (等老板 6 个字母; 违「板只改一次」的不派)")
            else:
                print("⚠ ISS-181 status=%s (不是 open) ⇒ 幂等跳过" % it181.get("status"))

        shutil.copy2(LOG, BAK)
        tmp = LOG + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)
        fcntl.flock(lk, fcntl.LOCK_UN)
    print("备份: %s" % BAK)


if __name__ == "__main__":
    main()
