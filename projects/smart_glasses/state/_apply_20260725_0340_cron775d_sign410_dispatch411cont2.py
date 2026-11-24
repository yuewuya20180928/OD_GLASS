#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★_apply_20260725_0340_cron775d_sign410_dispatch411cont2.py★

★**job**: cron `775d9893` (ARS45 继续执行后继计划 · 每 20 分钟) · 2026-11-25 03:26~03:4x
★**做什么**:
  ① 签收 ISS-410 (mech-lead) —— main 本机独立复核, 不抄任何 agent 报告
  ② 追加 dispatch_log 一条 (ISS-411 cont2 续派, sw-lead)

★**铁律**:
  - ① 零写板 / 零落表 (只动 issue_log + dispatch_log) / 零改既有闸 / 零改既有页正文 / 零挂链 / 零外发
  - ② CAS 守卫: 除 ISS-410 一条签收外, 其余全部条目逐条 yaml 序列化 md5 必须逐字不变
  - ③ 原子写: 先写 .tmp 再 os.replace
  - ④ 幂等: 已签收 ⇒ 跳过; dispatch_log 已有 ISS-411 cont2 ⇒ 不重复追加
  - ⑤ 台账 ISS-411 status 保持 `fixing` 不动 ⇒ advance.py 的 in_flight 继续挡住任何 job 重复派
"""
import hashlib
import os
import shutil
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")

NOW = "2026-11-25 03:4x"

SIGN = {
    "ISS-410": {
        "verify_result": (
            "✅ verified (★main 2026-11-25 03:3x 本机独立复核 · 不抄任何 agent 报告★) ⇒ "
            "★**新闸 `MECH/check_premise_tier_decision.py` `--selftest` rc=0 · 末行逐字 `ALL TESTS PASS` "
            "(★正向 1 条 + 反向 19 条·main 实跑 tail 末两行逐字为「正向 1 条 · 反向 19 条 / ALL TESTS PASS」★)** ★ ⇒ "
            "★**裸跑 rc=1 = 【红的是现状】(★T1 四来源不一致: BOM/作业包/板面 都没记这一格, 只有真相页记 P1000 · "
            "T2 板面实读判定不出档位: J_DEBUG/J_UART 是自绘 SMD 占位 land 0.2750×0.9000 无钻孔 · T3 档位至今没拍板★)** ★ ⇒ "
            "★**「排针焊盘前提量今天连『现在盘上是哪一档』都答不出来」第一次成了机器可判 (★四来源逐条实读 + 四档×七数 28 格 + 换档的重算/重跑/重签清单 + 板厂工艺能力自查+降级方案★)** ★ ⇒ "
            "★**交卷页在盘 (43,539 B @03:16 · `HANDOFF/2026-11-25_mech-lead_ISS410_前提量选档决策表与闸.md`) + 真相页在盘 "
            "(89,707 B @03:16 · `MECH/BOARD_ONEPASS_PREMISE_TIER_DECISION_TABLE.md`) + 新闸在盘 (40,949 B) + "
            "自有分片 `state/fragments/mech.yaml` 命中 37 (★artifacts 3 / needs_from 6 / answers 1 / interface_claims 5 / needs_open_ledger 2★) + 留证 `logs/iss410/` 7 件** ★ ⇒ "
            "★**板 md5 `611b869e13518c3c023fb178f91a0075` / size 4940213 / mtime 2026-11-06 07:07:17.362193413 三证逐字节未动 (19 天) "
            "+ BOM `5b999399…` 未变 ⇒ 零写板 · 零落表 · 零挂链 · 零外发** ★ ⇒ "
            "★**本轮 `state/gate_check.py` rc=1, 但红项逐条实读【全部来自 ISS-411 真相页的 3 个沙盒合成 token (SW 域)】· 与本单 (MECH 域) 零交集 "
            "⇒ 按 L-26『签收要跑扫描面命中的闸』: 逐条读过, 无 MECH 项 ⇒ 不构成本单扣分项; 该红已单独派给 sw-lead 的 ISS-411 cont2** ★"
        ),
        "fix_ref": (
            "main 2026-11-25 03:4x 独立复核签收 (★零写板·零落表·零改既有闸判据·零改既有页面正文·零挂链·零外发·未代老板拍板★)"
        ),
    },
}

NOTE_ADDENDUM = (
    "★★2026-11-25 03:4x cron 775d9893 (ARS45 继续执行后继计划) · main 独立复核签收 (★追加式·老字一字未删★)★★\n"
    "★本机实跑读数 (★不抄任何 agent 报告★)★: 新闸 `--selftest` rc=0 · 末行逐字 `ALL TESTS PASS` (正向 1 + 反向 19) · "
    "★裸跑 rc=1 (★红的是现状: T1 四来源不一致 / T2 板面是 SMD 占位 land / T3 档位没拍板★) · "
    "★交卷页在盘 43,539 B + 真相页在盘 89,707 B + 新闸在盘 40,949 B + 自有分片 mech.yaml 命中 37 + 留证 logs/iss410/ 7 件 · "
    "★板 md5/mtime/size 三证与基线逐字相同 (19 天未动) ⇒ 零写板 · 零落表 · 零挂链 · 零外发 · 不代拍 · 不自签★\n"
    "★**签收只解「这一条已交卷」, 不解「这道新闸已挂链」** ⇒ ★**挂链是 main 的地界 (三道新闸都写死零挂链·本轮未挂·下一轮要么挂要么写清为什么不挂)** ★"
)

DISPATCH_ENTRY = {
    "issue": "ISS-411",
    "agent": "sw-lead",
    "at": "2026-11-25 03:4x",
    "brief": (
        "★★[cont2 续派 · 只补缺口] ISS-411 · ★**cont1 (03:12:32~03:21:20) 又被【共因掐死】: "
        "runTimeoutSeconds=5400 (90 分钟) 根本没到 · 会话状态 timeout + abortedLastRun=true · "
        "同一秒死的还有 mech-lead 的 cont1 (03:21:20) ⇒ 与 03:03:28.846~03:03:29.972 同型·与 02:07:37~02:07:40 同型★** ★★"
        "**cont1 不是空壳: 真相页 (66,293 B @03:16) + 新闸 (39,727 B @03:17 · selftest ALL TESTS PASS) + logs/iss411/ 已在盘 ⇒ 本趟只补 4 件缺口, 不许推倒重写★** ★★★"
        "纯查证/纯分析类 (零写板·零落表(除自有分片)·零改既有闸判据·零改既有脚本·零改既有页正文·零挂链·零外发·不代拍) ⇒ 合「板只改一次」纪律 ①** ★"
    ),
    "brief_file": "state/dispatch_briefs/ISS-411_sw_mustchange_face_impact_cont2.md",
    "job": (
        "cron 775d9893 (ARS45 继续执行后继计划) · ★2026-11-25 03:4x · ★**cont2 续派 (★台账 status 保持 fixing 不动 ⇒ "
        "advance.py 的 in_flight 规则继续挡住任何 job 再给该 agent 派活 ⇒ 零撞车窗口★) ★· "
        "★**派活前 main 本机实测三与判据**: 已落盘 (真相页 + 新闸 + logs/iss411/ 在盘) + 会话已死 (status=timeout·endedAt 03:21:20·runTimeoutSeconds=5400 未到 ⇒ 共因) + 交卷页不在盘 ⇒ "
        "★**⇒ 续做, 不是重开, 不是僵尸复活** ★· ★**派活前 main 本机实测 sw-lead 槽位空** (★最后一个 sw-lead 会话 endedAt 03:21:21·status=timeout★ ⇒ 零并发写会话★) ★· "
        "★**本轮新加的缺口项**: main 03:28 实跑 `state/gate_check.py` ⇒ rc=1 (★基线是 0 ⇒ 本单带出来的新红★) ⇒ "
        "红项逐字 = 真相页第 119 行的 3 个沙盒合成 token (TP_INT_ISSX / TP_TEMP_ISSX / U_TEMP_1) 被链上的 `SW/tools/check_sw_ref_reachability.py` 判成【新增真隐患】⇒ "
        "「真隐患条数 6 > 基线上限 3」⇒ ★**本趟必须把闸修回 rc=0 (只许改自己真相页的写法·不许放宽基线·不许改既有闸判据)★** ★"
    ),
    "status_note": (
        "★台账 status 保持 fixing (未改) ⇒ advance.py in_flight 规则继续挡住任何 job 再派活 ⇒ 零撞车窗口★ · "
        "★本趟 = 从 cont1 已落的活续做, 不是从零★"
    ),
    "task_name": "queue_iss411_cont2",
    "dispatched_at": "2026-11-25 03:4x",
    "redispatch_zombie": True,
    "death_cause": (
        "★共因中断 (cont1 与 mech-lead cont1 同秒死 03:21:20 · runTimeoutSeconds=5400 未到) ⇒ cont1 非空壳, 已落盘部分产物·只补 4 件缺口★"
    ),
}


def atomic_write(path, content):
    d = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".part")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def entry_md5(it):
    return hashlib.md5(
        yaml.safe_dump(it, allow_unicode=True, sort_keys=True, width=100).encode("utf-8")
    ).hexdigest()


def main():
    if not os.path.exists(LOG):
        print("FATAL: issue_log.yaml 不在", file=sys.stderr)
        return 2

    raw = open(LOG, encoding="utf-8").read()
    log = yaml.safe_load(raw)
    items = log if isinstance(log, list) else log.get("issues", [])
    before = {it.get("id"): entry_md5(it) for it in items if isinstance(it, dict)}

    # ---------- ① 签收 ISS-410 ----------
    signed = []
    for it in items:
        if not isinstance(it, dict):
            continue
        iid = it.get("id")
        if iid not in SIGN:
            continue
        if it.get("status") == "verified":
            print(f"  [skip] {iid} 已是 verified")
            continue
        meta = SIGN[iid]
        it["status"] = "verified"
        it["verify_result"] = meta["verify_result"]
        it["verify_date"] = NOW
        it["fix_ref"] = meta["fix_ref"]
        na = it.get("note_addendum")
        if not isinstance(na, list):
            na = []
        na.append(NOTE_ADDENDUM)
        it["note_addendum"] = na
        signed.append(iid)

    after = {it.get("id"): entry_md5(it) for it in items if isinstance(it, dict)}
    changed = sorted(k for k in before if before.get(k) != after.get(k))
    if changed != sorted(signed):
        print(f"FATAL: CAS 守卫失败 · 预期只动 {sorted(signed)} · 实际动了 {changed}", file=sys.stderr)
        return 3
    if set(before) != set(after):
        print("FATAL: 条目集合变了 (有增有删)", file=sys.stderr)
        return 3

    if signed:
        shutil.copy2(LOG, LOG + ".bak_20260725_0340_cron775d_sign410")
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=True, width=100))
        print(f"★ issue_log.yaml: 签收 {signed} (其余 {len(before)-len(signed)} 条逐条 md5 未变)")
    else:
        print("★ issue_log.yaml: 无需签收 (幂等)")

    # ---------- ② dispatch_log 追加 ----------
    dlog = yaml.safe_load(open(DLOG, encoding="utf-8")) or []
    if not isinstance(dlog, list):
        dlog = []
    if any(e.get("task_name") == DISPATCH_ENTRY["task_name"] for e in dlog if isinstance(e, dict)):
        print("★ dispatch_log.yaml: 已有 queue_iss411_cont2 (幂等·不重复追加)")
    else:
        dlog.append(DISPATCH_ENTRY)
        shutil.copy2(DLOG, DLOG + ".bak_20260725_0340_cron775d_iss411_cont2")
        atomic_write(DLOG, yaml.safe_dump(dlog, allow_unicode=True, sort_keys=False, width=100))
        print(f"★ dispatch_log.yaml: +1 条 (queue_iss411_cont2) · 现共 {len(dlog)} 条")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
