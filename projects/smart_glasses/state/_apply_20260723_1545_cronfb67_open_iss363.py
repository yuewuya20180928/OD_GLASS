#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★**cron fb67af40 (ARS45 队列自动派活) · 2026-11-23 15:4x · 新开 ISS-363 (sw-lead) 并直接派出** ★

★**为什么新开 (★逐条本机实读·不抄任何 agent 报告★)**:
  ① `python3 state/advance.py --json` ⇒ ★**`internal: []`** ⇒ 三个总工名下**零 `open` 可派** ⇒ 队列真空 ⇒ 不开单就断线 ★
  ② hw-lead 名下 ISS-361 是 `fixing` 且会话**活着** (★transcript 在盘 + 15:43:07 刚交卷 + `logs/iss361/` 54 件在盘★)
     ⇒ ★**本轮不碰 hw-lead** ★
  ③ sw-lead 名下 ISS-362 **本 job 刚签收 (verified)** ⇒ ★**槽位空出来** ⇒ 可派 ★
  ④ mech-lead 名下**零 open 零 fixing** ⇒ 本轮无单可派 ⇒ 不凑数
  ⑤ ★**派活前置闸**: `python3 state/check_brief_commands.py --brief-file state/dispatch_briefs/ISS-363_sw_fp_truth_read_entry.md` ⇒ ★**rc=0** ★

★**main 对 ISS-362 交卷页 B5 四问的裁决 (★本 job 代落·逐条★)**:
  ★**B5-1 (要不要往 `SW/BOARD_ONEPASS_SW_SYNC.md` 的 8 条清单加第 9 条)** ⇒ ★**加** ★
    ⇒ ★**但必须【三处同批落地】**: ① 清单 `.md` (§2 表 + §2.1 分布表 + §6 JSON 块加 SW09) ② ISS-362 页 §H4-REG 三个数字 (8→9 / 0→1 / 4→新值) ③ 新闸 (H1 从「登记」变「有闸」) ★
    ⇒ ★**本机实读发现的三条硬事实**: ★清单闸 `REQUIRED_IDS` 只判「8 条一条不许漏」⇒ **多出来的条目不判红**; ★`SOURCES` 白名单 14 个 id 里**没有 ISS-362/363** ⇒ ★**SW09 的 `source_iss` 必须用 `ISS-241+ISS-244`** (★真来源=落表残项 8 行的 footprint 选型归 ISS-241/244★) ⇒ **不必改既有闸**; ★ISS-362 闸 H4 判据是**动态**的 (判「页里登记数 == 本机实测」) ⇒ **加第 9 条后 H4 会红但不需要改闸脚本**, 只要同步页里三个数字 ★
    ⇒ ★**⇒ 真件落地 = main 的一键动作 ⇒ 本单只出补丁 + 沙盒证明 ⇒ 真件零改** ★
  ★**B5-2 (要不要给三份真源加一道【读封装栏】的新闸)** ⇒ ★**加** ★ ⇒ ★**交新脚本、不挂链** (★挂不挂 `gate_check.py` / 准出汇总闸 = main 的机制地界·ISS-330/333 同款★) ★
  ★**B5-3 (那 9 条过期 need 的正文要不要真被改写)** ⇒ ★**不改** ★ ⇒ ★**改用机器闸判「仍 open 的 need 引着的 md5 == 落表台账链头」⇒ 把人工清洗任务变成机器判据 (F3)★**
  ★**B5-4 (`SW/SW_MD5_BASELINE_LEDGER.md` §1 锚点副本要不要跟到链头 ISS-302)** ⇒ ★**跟, 但走合法换源通道 (落 decision + 留痕)** ★ ⇒ ★**本单零改该文件** ⇒ ★**登记一条 need 给 main** ★

★**纪律**: ★**status 直接落 `fixing` ⇒ 无 `open` 窗口 ⇒ 下一轮 in_flight 规则会跳过 sw-lead ⇒ 兄弟 job 775d9893 不会重复派** ★
★**零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零改 agent 分片 · 零外发 (★老板 2026-11-11 19:31 + 2026-11-12 02:02: 不再发信·本 job 自己也不发★)**
"""
from __future__ import annotations

import fcntl
import os
import shutil
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DLOG = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
STAMP = "20261123_1545_cronfb67_open_iss363"
BRIEF_FILE = "ISS-363_sw_fp_truth_read_entry.md"

BRIEF = open(os.path.join(HERE, "dispatch_briefs", BRIEF_FILE), encoding="utf-8").read()

TITLE = (
    "★★[★新主线·PCB 线·SW 侧「S10 换封装真值」收口·纯分析+新建闸+沙盒预演·零写板] ★★"
    "【ISS-362 (sw-lead) 已把「S10 换封装真值」这一跳对 SW 侧的影响面交卷 (H1/H3/H4 三条是【登记式绿】"
    "⇒ 它把三个缺口【登记】上了, 但没有任何闸去判) ⇒ 而「板只改一次」那一趟 S10 会【合法地】把三份真源 "
    "(网表/脚表/BOM) 的 md5 一起换掉 ⇒ 若清单里没有这一条 ⇒ 那一趟当天 SW 侧没人认领这一跳 ⇒ 红了没人解释 ⇒ "
    "最坏的结果是有人为让闸绿去改锚点/改判据 ⇒ 那正是 ISS-273/275/284 三单花大力气堵掉的「悄悄换真源」漏洞】★★ "
    "⇒ ★**本单 = ① SW09 (清单第 9 条) 的 9 字段草案 + 「三处同批落地」的补丁清单 (★真件零改★) "
    "② 新建 `SW/tools/check_fp_truth_read.py` (★把 H1 从「登记」变成「有闸」· 双态判据·不挂链★) "
    "③ 沙盒预演: 三处同批落地 ⇒ 10 道 SW 闸全绿 + 反证「只改一处 ⇒ H4 红 + F4 红」 "
    "④ 一页 + 交卷页 + 分片 + 留证** "
    "★【纯分析 + 新建闸类 · 零写板 · 零落表 · 零改既有闸 · 零改既有页面 · 零外发 · 不代老板拍板】★★"
)

DESC = (
    "★**main 2026-11-23 15:4x 本机实读 (不抄任何 agent 报告)★** ⇒ "
    "★**① 病灶**: ISS-362 交卷页 §H1-REG 实测 `H1-READERS=0` ⇒ SW 全域**零道闸读 `footprint` 栏**; "
    "§H4-REG 实测 `H4-COVER=0` ⇒ 8 条板侧输入清单里**没有「S10 换封装真值」这一条** ⇒ "
    "「板只改一次」那一趟 S10 换封装真值落表时, SW 侧【没有任何机器判据】知道它该不该红 ⇒ "
    "★★后果★: 红了没人解释 ⇒ 现场最容易误读成「板改坏了」→ 去改锚点/改判据/改真源凑绿 → 板 md5 变第二次 → 整趟白跑 ★★ "
    "★**② 三份真源的封装栏在哪 (main 实测)★**: 网表 `HW/netlist_v1.csv` 第 14 栏 `footprint` (513 行·非空 90) · "
    "脚表 `HW/netlist_v1_pins.csv` 第 **11** 栏 `footprint` (584 行·非空 162) · BOM `HW/BOM_v1.csv` 第 10 栏 `footprint` "
    "(218 行·非空 218) ⇒ ★**★须按表头名定位, 不许写死列号** (★ISS-362 派活书写的「脚表第 12 栏」实为 `opn`·已在页里更正★)★ ★ "
    "★**③ 清单闸的实读事实 (决定「加第 9 条要不要改既有闸」)★**: `SW/tools/check_onepass_sw_sync.py` 的 "
    "`REQUIRED_IDS` 只判「8 条一条不许漏」⇒ ★**多出来的条目不判红**; `SOURCES` 白名单 = 14 个 id (ISS-225/234/241/244/266/269/"
    "271/273/274/275/276/277/278/279) ⇒ ★**没有 ISS-362/ISS-363** ⇒ SW09 的 `source_iss` 必须落在白名单里 (★建议 "
    "`ISS-241+ISS-244`·真来源 = 落表残项 8 行的 footprint 选型归 ISS-241/244·见清单 SW03 那行的 current_state★) ⇒ "
    "★**不必改既有闸** ★ "
    "★**④ ISS-362 闸 H4 是动态判据 (main 实读闸源码)★**: 它判「页里登记的 `H4-ITEMS`/`H4-COVER`/`H4-GENERIC` == 本机实测」 ⇒ "
    "★**加第 9 条后 H4 会红, 但不需要改闸脚本, 只要同步页里 §H4-REG 三个数字** (现值 8 / 0 / 4) ⇒ ⇒ "
    "★**⇒ 「三处同批落地」= 清单 .md + ISS-362 页 H4-REG 三数字 + 新闸** ★ "
    "★**⑤ 落表台账链头** = `HW/SCHEMATIC_LANDING_V1_LANDED.md` (判决源) ⇒ 新闸 F2 必须复用 "
    "`check_demo_panel_spec.sw_ledger_state()` 口径, 不许自己另写一套链头算法 ★ "
    "★**⑥ 本单不许落真件的两条硬理由★**: ① `SW/BOARD_ONEPASS_SW_SYNC.md` 是 **ISS-362 签收闸的 PROTECTED 件** "
    "(md5 `b8f935db333c16fa1051f0b06ae3e6ec`) ⇒ 改了它, ISS-362 的签收脚本重跑会红; ② 三处必须同批, 中间任何一刻不同步链就红 ⇒ "
    "★**⇒ 真件落地 = main 的一键动作 ⇒ 本单只出补丁 + 沙盒证明** ★ "
    "★**⑦ 双态判据是本单最关键的设计★**: 新闸 F4 只判「页里登记的条数 == 本机实测」, ★**不判「必须 0 条」也不判「必须 1 条」** ⇒ "
    "⇒ 第 9 条落地那天新闸不红, 而 ISS-362 的 H4 会红 ⇒ ⇒ 本单交付的补丁正好是那天的落地方案, 而不是一颗哑弹 ★ "
    "★**⇒ 本单只出【纯分析 + 新建闸 + 沙盒预演】, 一个字节都不许写板** ★"
)

NOTE = (
    "★2026-11-23 15:45 cron fb67af40 新开并直接派出 (status 落 fixing ⇒ 下一轮 in_flight 规则会跳过 sw-lead ⇒ "
    "窗口消失 ⇒ 不与兄弟 job 775d9893 撞车)★ "
    "★**开单依据**: ① `state/advance.py --json` ⇒ internal=[] (三个总工名下零 open 可派) "
    "② hw-lead 名下 ISS-361 会话活着 (15:43:07 刚交卷) ⇒ 本轮不碰 "
    "③ sw-lead 名下 ISS-362 本 job 刚签收 verified ⇒ 槽位空出来 ⇒ 可派 "
    "④ mech-lead 名下零 open 零 fixing ⇒ 本轮无单可派 ⇒ 不凑数 "
    "⑤ 派活前置闸 `state/check_brief_commands.py --brief-file` ⇒ rc=0 ★ "
    "★**main 对 ISS-362 交卷页 B5 四问的裁决**: B5-1 加第 9 条 (★但三处同批落地·真件落地归 main 一键动作·本单只出补丁+沙盒证明★) · "
    "B5-2 加闸 (★交新脚本不挂链·挂链归 main★) · B5-3 不改 need 正文 (★改用机器闸 F3 判「open need 引的 md5 == 链头」★) · "
    "B5-4 锚点副本跟到链头 (★但走合法换源通道·本单零改该文件·登记 need 给 main★) ★ "
    "★**任务书全文**: `state/dispatch_briefs/%s` (10,295 B · `check_brief_commands.py --brief-file` rc=0)★ "
    "★**边界**: 零写板 (md5 必须仍 611b869e13518c3c023fb178f91a0075 · mtime 必须仍 2026-11-06 07:07:17.362193413) · "
    "零落表 (网表/脚表/BOM/落表台账/issue_log 一字不改) · 零改既有闸 (check_onepass_sw_sync.py / check_sw_fp_truth_impact.py / "
    "gate_check.py / merge.py / frag_write.py 一字不改) · 零改既有页面 (SW/BOARD_ONEPASS_SW_SYNC.md / "
    "SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md / SW/SW_MD5_BASELINE_LEDGER.md 老字零改动) · 零挂链 · "
    "只写自己的分片 state/fragments/sw.yaml (只走 frag_write.py) · 沙盒只落 tmp/iss363_sbx/ + logs/iss363/ · "
    "不替老板拍板 · 零外发 (老板 2026-11-11 19:31 + 2026-11-12 02:02) · 不自签 issue_log★"
) % BRIEF_FILE


def atomic_write(path: str, text: str) -> None:
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp_", suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main() -> int:
    applied = []
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)

        shutil.copy2(LOG, LOG + ".bak_" + STAMP)
        shutil.copy2(DLOG, DLOG + ".bak_" + STAMP)
        applied.append("备份: issue_log.yaml + dispatch_log.yaml")

        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        idx = {i.get("id"): i for i in issues}

        iid = "ISS-363"
        if iid in idx:
            it = idx[iid]
            if it.get("status") != "fixing":
                it["status"] = "fixing"
                applied.append("%s status → fixing (★兜底·幂等★)" % iid)
            if it.get("task_brief") != BRIEF:
                it["task_brief"] = BRIEF
                applied.append("%s task_brief 刷新" % iid)
        else:
            issues.append({
                "id": iid,
                "title": TITLE,
                "severity": "high",
                "source_blocker": "ISS-362",
                "source_agent": "main",
                "desc": DESC,
                "owner": "sw-lead",
                "reporter": "main",
                "raised": "2026-11-23",
                "due": "2026-11-25",
                "status": "fixing",
                "external": False,
                "need_keys": [],
                "task_brief": BRIEF,
                "note": NOTE,
                "dispatched_at": "2026-11-23",
            })
            applied.append("新开 %s (sw-lead) · status 直接落 fixing" % iid)

        log["issues"] = issues
        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=10**6))

        # ★★dispatch_log.yaml 顶层是【list】(★不是 dict★ ⇒ 2026-11-23 15:4x 实测★)
        dlog = yaml.safe_load(open(DLOG, encoding="utf-8")) or []
        if isinstance(dlog, dict):          # ★兼容老结构★
            entries = dlog.get("dispatches") or []
            dlog_is_dict = True
        else:
            entries = dlog
            dlog_is_dict = False
        if not any(e.get("issue") == iid for e in entries):
            entries.append({
                "issue": iid,
                "agent": "sw-lead",
                "at": "2026-11-23",
                "brief": NOTE,
                "job": (
                    "cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-23 15:45 · "
                    "★**status 全程 fixing ⇒ 无 open 窗口 ⇒ 兄弟 job 775d9893 不会重复派** ★"
                ),
            })
            applied.append("dispatch_log.yaml += %s sw-lead 1 条" % iid)
        out = dlog
        if dlog_is_dict:
            out["dispatches"] = entries
        else:
            out = entries
        atomic_write(DLOG, yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=10**6))

    for a in applied:
        print("·", a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
