#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
state/_apply_20261118_0140_cron775d_iss131_305.py
================================================================================
★**cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-18 01:4x · 本机实跑** ★

本脚本在同一个 flock 内原子完成三件事:

  ① **ISS-131** (`owner=main`): `open` → `fixing`
     ⇒ ★**main 已自办完** (★交付页 + 机器可复核脚本·零写板·零落表·零外发★) ⇒ 等 hw-lead 独立复验 ★

  ② **ISS-305 新开** (`owner=hw-lead`): ★**直接落 fixing** ⇒ 兄弟 job fb67af40 的 advance.py
     看不见 open 窗口 ⇒ 不会重复派同一个 agent ★

  ③ **dispatch_log** 写 ISS-305 一条

★**依据 = main 本机实跑 (★不抄任何 agent 报告★)**:
  · `python3 state/_iss131_crosscheck_rk3572_caliber.py` = **rc=0** (★球位号 11/11 + CSI 口径 6 条 + ISP 口径·全与官方 datasheet 自洽★)
  · 板 `611b869e13518c3c023fb178f91a0075` · mtime 仍 **2026-11-06 07:07:17** ⇒ ★**零写板** ★
  · 网表 `6aee500e…` / 脚表 `9174309d…` / BOM `5b999399…` mtime 全停在 **00:21:08** ⇒ ★**零落表** ★
  · ★**本 job 零外发** (★老板 2026-11-11 19:31 + 2026-11-12 02:02 口径★)

★**边界**: 不改 `PROJECT_TRACKER.md` §0 锁死表 · 不写别的 agent 的分片 · 不替老板拍板
"""
from __future__ import annotations

import fcntl
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
BRIEF = os.path.join(HERE, "dispatch_briefs", "ISS-305_hw_verify_iss131.md")

TODAY = "2026-11-18"

ISS131_NOTE = (
    "★**2026-11-18 01:4x · cron 775d9893 · 项目总工 (main) 自办完 (★老板 2026-11-12 02:02「不再发信, 全靠自己查资料」口径★)** ★\n"
    "⇒ ★**本单不是「等回信」的单, 是「自查口径」的单 ⇒ 已用项目内【官方 datasheet】自查完** ★\n"
    "⇒ ★**交付物 2 件**:\n"
    "  ① `HW/RK3572_INQUIRY_CALIBER_V2.md` (★6,007 B · 真判据 `grep -cE \"🔄 待填\"` = 0★) —— ★**「口径改 RK3572」三件事的逐条结论 + 证据分级 + 降级方案** ★\n"
    "  ② `state/_iss131_crosscheck_rk3572_caliber.py` (★**机器可复核 · rc=0**★) —— ★**读网表 + 读 `HW/PCB/FET3572C_PIN_TABLE.csv` + 读官方 datasheet txt ⇒ 三方对拍** ★\n"
    "⇒ ★**main 本机实跑的原样结论 (★rc=0·不抄任何 agent 报告★)**:\n"
    "  · ★**球位号 11/11 对上官方 datasheet** (★网表 J_SOM_P2/P4 的 10 处 CSI 落位 + 1 处 MCLK 落位·球位逐条命中★) ⇒ ★**其中 A22/B22/A23/B23 四条是「同球双名」"
    "(★官方 datasheet L1789 逐字 `MIPI_DPHY_CSI0_RX_D2P/MIPI_DPHY_CSI1_RX_D0P A22`·⇒ 这正是「一个 4-lane 口可配 2×2」的物理证据★)** ★\n"
    "  · ★**CSI 通道数**: 官方 §1.2.7 逐字 `Support 2 MIPI CSI-2 interfaces` / `Two 4 data lanes of D-PHY v1.2` / `Each interface may be configured as 2x2 data lanes port` ★\n"
    "    ⇒ 物理 = **2 个 4-lane D-PHY·可拆成 4 个 2-lane 口** ⇒ ★**我方网表只用 `CSI_D0` 一路 4 lane ⇒ 「2 接口 vs 4 口」对我方板无约束** ★\n"
    "  · ★**ISP 12M**: 官方 §1.2.8 逐字 `Image Signal Processor V3.5` / `One channel ISP,12M pixels` / `Maximum input:4096x3072` ⇒ ★**4096×3072 = 12.58 Mpixel ⇒ "
    "「12M」是【单帧分辨率上限】不是 MP/s 吞吐** ⇒ ★**我方 1080p60 在分辨率维度不卡 [官方]** ★\n"
    "  · ★**ISP MP/s = [0数据]** ★ ⇒ datasheet 全文检索不到 ISP 的 MP/s 上限 ⇒ ★**换芯到 RK3572 后这条缺口【没变好也没变坏】(★RK3576 侧同样没给·ISS-124 已 verified 但 MP/s 那条仍挂着★)** ⇒ "
    "★**降级方案**: ① 官方 TRM (★本机只留了 datasheet V1.1·无 TRM⇒需联网·标 [官网]★) ② 板端实测 (★ISS-210 已把 60ms 判据链 + ISP 段打点备好★) ③ 在此之前任何 MP/s 数字只能标 [推算] 并写清推算链** ★\n"
    "⇒ ★**★本单带出的一条新硬约束 (★唯一带推算成分的那条·已写进交付页·待复验★)★**: ★**ISP 是 `One channel` ⇒ 同一时刻只有 1 路传感器能进 ISP** ⇒ "
    "★**⇒ 多摄像头方案在 RK3572 上不成立 (无论 CSI 物理上有几个口) ⇒ 这一条要进 demo 选型硬判据 (ISS-156 的 camera 模组选型只能 1 路) [官方+推算]★** ★\n"
    "⇒ ★**球位号问询对象**: ★**项目内已有 `HW/PCB/FET3572C_PIN_TABLE.csv` (399 条 conn/num) ⇒ 11 处落位已自证 ⇒ 只剩「模组底面图 pin1 标号」一条真需要问 ⇒ "
    "草稿已在盘 `state/outbox/som_balltable_inquiry.md` ⇒ ★**不发·等老板放行** (★本 job 零外发★)** ★\n"
    "⇒ ★**★零写板 / 零落表 (md5 + mtime 双证·main 本机实读)★**: 板 `611b869e13518c3c023fb178f91a0075` mtime 仍 `2026-11-06 07:07:17` · "
    "网表 `6aee500e…` / 脚表 `9174309d…` / BOM `5b999399…` mtime 全停在 `2026-11-18 00:21:08` ⇒ ★**本单零写板·零落表** ★\n"
    "⇒ ★**状态 open → fixing**: ★**main 已交卷 ⇒ 交别人验 (铁律: 干活的人不许自签) ⇒ 新开 ISS-305 → hw-lead 独立复验** ★\n"
    "⇒ ★**诚实边界**: ★**实物 [实测] = 0 条** (★本机无板★) · ★**MP/s 那条没解决·只标清了 [0数据] 并指到 ISS-210** ★ · ★**「One channel ISP ⇒ 只能 1 路」是 [官方+推算] 的合成结论·是本单最该被挑错的一条** ★"
)

ISS305 = {
    "id": "ISS-305",
    "title": (
        "★★[主线内·HW 侧·独立复验类·内部活] ★★【ISS-131「问询口径改 RK3572 (ISP 16M→12M / CSI 3×→2×) + 球位号问询对象改 RK3572 模组厂」"
        "已由 main 按老板 2026-11-12 02:02「不再发信·全靠自己查资料」口径自办完 ⇒ 交付页 + 机器可复核脚本 (★rc=0★) ⇒ 但它含一条 [官方+推算] 的合成结论"
        "「One channel ISP ⇒ 同时只能 1 路传感器」⇒ 这条将来会变成 demo 选型硬判据 ⇒ 错了会拿错判据去筛供应商 ⇒ 必须有人真的挑一遍】★★ "
        "⇒ ★**本单 = 独立复验 (★复现 + 挑错 + 签字·不产新结论·不许改任何工程文件·不许改被判据·零外发★)** ★"
    ),
    "severity": "medium",
    "owner": "hw-lead",
    "reporter": "main",
    "raised": TODAY,
    "due": "2026-11-20",
    "status": "fixing",
    "external": False,
    "need_keys": [],
    "fix_ref": None,
    "verify_by": "main",
    "verify_result": None,
    "verify_date": None,
    "dispatched_at": TODAY,
    "note": (
        "★**2026-11-18 01:4x · cron 775d9893 (ARS45 继续执行后继计划) 新开并直接派出 (★status 直接落 fixing ⇒ 兄弟 job fb67af40 的 advance.py "
        "看不见 open 窗口 ⇒ 不会重复派同一个 agent★)** ★ ⇒ ★**依据 = main 01:3x 本机实跑 `state/_iss131_crosscheck_rk3572_caliber.py` rc=0 + 板/网表 md5+mtime 双证** ★ "
        "⇒ ★**待复验物 3 件**: ① `HW/RK3572_INQUIRY_CALIBER_V2.md` (6,007 B) ② `state/_iss131_crosscheck_rk3572_caliber.py` (★**它是本单要复验的对象·不许自己改掉再报绿★**) "
        "③ `HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt` (★只读源★) ★ ⇒ ★**必挑 6 条错 (A~F)·其中 C 条「One channel ISP ⇒ 只能 1 路」是重点** ★ "
        "⇒ ★**不许改任何工程文件 · 不许改被判据 · 不许改闸去消红 · 不许写别的分片 · 零外发 · 不许自签 issue_log · 不许替老板拍板** ★ ⇒ "
        "★**零写板 · 零落表 · 纯读 + 记 + 签** ★"
    ),
    "task_brief": None,
}


def main() -> int:
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        with open(LOG, encoding="utf-8") as f:
            log = yaml.safe_load(f) or {}
        issues = log.get("issues") or []

        # ---- ① ISS-131: open → fixing (★main 已交卷·待 hw-lead 复验★) ----
        for it in issues:
            if it.get("id") != "ISS-131":
                continue
            if it.get("status") == "fixing":
                print("★ISS-131 已是 fixing ⇒ 跳过 (幂等)")
                break
            if it.get("status") != "open":
                print("★ISS-131 status=%s ≠ open ⇒ 不动" % it.get("status"))
                break
            it["status"] = "fixing"
            it["note"] = (it.get("note") or "") + "\n\n" + ISS131_NOTE
            print("✅ ISS-131 open → fixing (main 自办交卷·等 hw-lead 复验)")
            break

        # ---- ② ISS-305 新开 (★只在 id 不存在时才建 ⇒ 幂等★) ----
        if any(it.get("id") == "ISS-305" for it in issues):
            print("★ISS-305 已存在 ⇒ 不重复开 (幂等)")
        else:
            brief = ""
            if os.path.exists(BRIEF):
                brief = open(BRIEF, encoding="utf-8").read()
            ISS305["task_brief"] = brief
            issues.append(ISS305)
            print("✅ ISS-305 新开 (owner=hw-lead · status=fixing · task_brief %d B)" % len(brief))

        tmp = LOG + ".tmp.%d" % os.getpid()
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)
        os.replace(tmp, LOG)
        print("✅ issue_log.yaml 已原子写回")

        # ---- ③ dispatch_log ----
        with open(DL, encoding="utf-8") as f:
            dl = yaml.safe_load(f) or {"dispatches": []}
        if not any(d.get("issue") == "ISS-305" for d in dl.get("dispatches", [])):
            dl.setdefault("dispatches", []).append({
                "issue": "ISS-305",
                "agent": "hw-lead",
                "at": TODAY,
                "brief": "state/dispatch_briefs/ISS-305_hw_verify_iss131.md",
                "job": "cron 775d9893 (ARS45 继续执行后继计划) · 派出 (★独立复验类·纯读+记+签·零写板·零落表·零外发★)",
            })
            tmp2 = DL + ".tmp.%d" % os.getpid()
            with open(tmp2, "w", encoding="utf-8") as f:
                yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
            os.replace(tmp2, DL)
            print("✅ dispatch_log 已写 ISS-305 → hw-lead")

        fcntl.flock(lk, fcntl.LOCK_UN)
    return 0


if __name__ == "__main__":
    sys.exit(main())
