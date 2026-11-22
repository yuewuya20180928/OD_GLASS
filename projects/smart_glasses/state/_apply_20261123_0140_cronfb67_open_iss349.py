#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261123_0140_cronfb67_open_iss349.py
================================================================================
cron fb67af40 (ARS45 队列自动派活) · 2026-11-23 01:4x
--------------------------------------------------------------------
开单 1 条 (ISS-349 · hw-lead)

★**为什么现在才开这一条 (★队列本身是空的★)**:
  ★`state/advance.py --json` ⇒ internal=[] / approvals=[] / waiting=0
  ★⇒ hw-lead / sw-lead / mech-lead 名下 open 全为 0
  ★⇒ sw-lead (ISS-346) 与 mech-lead (ISS-345) 各自有【在飞会话】⇒ 本 job 不碰
  ★⇒ 只有 hw-lead 名额空着 ⇒ 按「开新单」处理

★**开单依据 (★main 本机实读 + 实跑, 不抄任何 agent 报告★)**:
  ★① `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` 的 §2 表 = 32 行 (B01..B32)
  ★   而 §7 JSON = 33 条 (多出来的是 `B33_PIN_LAND_1P27`) ⇒ 页与 JSON 已不同源
  ★② 该页是生成器 `state/_iss277_build_preflight.py` 的产物
  ★   ⇒ 生成器 `ITEMS_RAW` 只有 B01..B32 (grep B33/1.27/排针/PIN_LAND = 0 命中)
  ★③ sidecar `state/_iss277_preflight_appendix.md` 同样 0 命中
  ★   ⇒ 重跑一次生成器 ⇒ B33 蒸发 ⇒ E-1 从「板侧项全集」里消失
  ★④ ISS-292 (2026-11-17) 的交卷页写死「页 md5 = 159bf20f… ⇒ 页回退这条路已经堵死」
  ★   ⇒ 现页 md5 = 8ae70471604dcf447f43477dbada3f13 ⇒ 已被手改 ⇒ 「已堵死」当场失效
  ★⑤ `state/_iss304_sync_state_baseline_md5.py:145` 的「落表后重锚流程 ①」就是跑生成器
  ★   ⇒ 不是「以后有人跑」, 是「流程每次跑都跑」
  ★⑥ 本仓铁律 (ISS-304 任务书 :52 逐字): 「不许手改生成器产物 ⇒ 必须改 sidecar / 生成器, 再重跑生成器」
  ★   ⇒ ISS-343 的派单口径漏了「要落到生成器 + 重跑」这一步 (★main 自认, 不怪 agent★)

★**为什么直接落 `fixing` 而不是 `open`**:
  ★**兄弟 job (cron 775d9893「继续执行后继计划」) 每 30 分钟跑一次, 它也会读
  ★`state/advance.py --json`** ⇒ ★**若本单留一个 `open` 窗口 ⇒ 兄弟 job 会把
  ★同一条当自己的货派给同一个 agent ⇒ 撞车 (★两个 agent 写会话同时写一个分片 ⇒
  ★分片合并丢 12%~38%★)** ⇒ ★**本单直接落 `fixing` ⇒ 兄弟 job 的
  ★`advance.py --json` 看不见本单 ⇒ 不会重复派**
  ★ (★与 2026-11-22 23:30 开 ISS-342 / 2026-11-23 00:1x 开 ISS-343~345 同一手法★)

★**原子写 + 带 .bak + 幂等** ★
"""
from __future__ import annotations

import os
import shutil
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261123_0140_cronfb67_open_iss349"
DL = os.path.join(HERE, "dispatch_log.yaml")
DL_BAK = DL + ".bak_20261123_0140_cronfb67_open_iss349"
BRIEF_DIR = os.path.join(HERE, "dispatch_briefs")

TODAY = "2026-11-23"
IID = "ISS-349"
OWNER = "hw-lead"
BRIEF_NAME = "ISS-349_hw_preflight_b33生成器回归_修复.md"

TITLE = (
    "★★[★新主线·PCB 线·板侧项全集页被手改·生成器重跑会蒸发 E-1·纯脚本改造+新建机器闸·零写板] ★★"
    "【把 `B33_PIN_LAND_1P27` (E-1 排针 land 0.50→1.27) 从「手改产物页」搬回生成器 `state/_iss277_build_preflight.py` "
    "⇒ 重跑生成器 ⇒ §2 表 33 行 + §7 JSON 33 条 + id 集合逐一相等 ⇒ "
    "新建 `HW/check_preflight_regen_idempotent.py` (表/JSON 同源 + 重跑幂等 + source_iss 在 SOURCES 内) + ≥3 条反向用例】★★ "
    "★**main 2026-11-23 01:4x 实读: 页 §2 表 32 行 vs §7 JSON 33 条 (多出 `B33`) ⇒ 页与 JSON 已不同源; "
    "生成器 ITEMS_RAW 只有 B01..B32 + sidecar 0 命中 ⇒ 重跑一次生成器 B33 即蒸发; "
    "ISS-292 交卷页写死的「页回退这条路已经堵死 (页 md5=159bf20f…)」现已失效 (现页 md5=8ae70471…) "
    "⇒ 而 `state/_iss304_sync_state_baseline_md5.py:145` 的「落表后重锚流程 ①」每次都跑生成器 "
    "⇒ E-1 会从「板只改一次」那一趟的板侧项全集里静默消失 ⇒ 实物排针照样装不进 ⇒ 补做 = 板 md5 变第二次**★"
)

DESC = (
    "★**main 本机实读 + 实跑 (不抄任何 agent 报告)★** ⇒ "
    "★**① 页不同源**: `HW/PCB/BOARD_ONEPASS_PREFLIGHT.md` §2 表 = 32 行 (唯一 id B01_REF_SUFFIX..B32_V2_NET_RENAME) "
    "而 §7 JSON = 33 条 (末条 `B33_PIN_LAND_1P27`) ⇒ 全页 grep B33 只 1 命中 (行 543, JSON 块内) ⇒ 表里一处都没有 ★ "
    "★**② 生成器里没有**: `state/_iss277_build_preflight.py` 的 `ITEMS_RAW` (行 260) 只有 B01..B32 ⇒ grep `B33|PIN_LAND|1\\.27|排针` = 0 命中 ★ "
    "★**③ sidecar 里也没有**: `state/_iss277_preflight_appendix.md` (29,471 B) = 0 命中 ★ "
    "★**④ 「已堵死」失效**: ISS-292 交卷页写死「页 md5 = 159bf20fe71c36e48292f39dafc46a35 ⇒ 页回退这条路已经堵死」, "
    "现页 md5 = 8ae70471604dcf447f43477dbada3f13 (mtime 2026-11-23 01:09:04) ⇒ 已被手改 ★ "
    "★**⑤ 重跑是流程内的固定动作**: `state/_iss304_sync_state_baseline_md5.py:145`「落表后重锚流程: ① python3 state/_iss277_build_preflight.py」 ★ "
    "★**⑥ 覆盖度闸给假绿**: `HW/check_onepass_preflight_coverage.py` (40,636 B @ 01:12) 只读页、不读生成器 ⇒ 页里有 B33 就绿 ⇒ 重跑后页里没有它也不会红 ★ "
    "★**⑦ 铁律早已写过**: ISS-304 任务书 :52 逐字「不许手改生成器产物 ⇒ 必须改 sidecar / 生成器, 再重跑生成器」; "
    "ISS-292 任务书 :107 逐字「只许改它允许的地方 = 加 E-1~E-6 那一条的读入 (不许写死六条·从真源读)」⇒ E-1 本来就该长在生成器里 ★ "
    "★**⑧ 病根在派单口径**: ISS-343 任务书 §1-① 写的是「追加一条 item」到页 ⇒ agent 照做 ⇒ main 自认派单口径漏了「落到生成器 + 重跑」这一步 ⇒ 不怪 agent ★ "
    "★**⑨ 不依赖老板拍板**: E-1 = main 2026-11-17 18:45 已拍死 (pm.yaml key `main_e1_e2_board_side_rulings_20261117`) ⇒ 本单是纯技术活 ★"
)

NOTE = (
    "★★%s · cron fb67af40 (ARS45 队列自动派活) 开单并派出 (★项目总工 main★) ★★ "
    "★**开单依据**: advance.py --json 实读 internal=[] / approvals=[] / waiting=0 (★队列排空 ⇒ 三个总工名下 open 全为 0★) "
    "⇒ sw-lead (ISS-346) 与 mech-lead (ISS-345) 各有在飞会话 ⇒ 本 job 不碰 ⇒ 只有 hw-lead 名额空着 ⇒ 按「开新单」处理; "
    "★**来源 = main 2026-11-23 01:4x 本机实读 + 实跑 (不抄任何 agent 报告)★: 页 §2 表 32 行 vs §7 JSON 33 条 + 生成器 ITEMS_RAW 只 B01..B32 + sidecar 0 命中 "
    "⇒ 重跑一次生成器 B33 蒸发 ⇒ ISS-292「页回退已堵死」的结论失效 (现页 md5 8ae70471… ≠ 159bf20f…) ★ "
    "★**★status 直接落 `fixing` (不经过 `open` 窗口) ⇒ 兄弟 job (cron 775d9893) 的 `advance.py --json` 看不见本单 ⇒ 不会重复派同一个 agent** ★★ "
    "★**任务书全文**: `state/dispatch_briefs/%s` (★check_brief_commands.py --brief-file rc=0★) ★"
    % (TODAY, BRIEF_NAME)
)


def atomic_write(path: str, text: str) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def main() -> int:
    brief_path = os.path.join(BRIEF_DIR, BRIEF_NAME)
    brief = open(brief_path, encoding="utf-8").read()

    # ---------- issue_log ----------
    doc = yaml.safe_load(open(LOG, encoding="utf-8").read()) or {}
    issues = doc.get("issues") or []
    existing = {i.get("id") for i in issues}
    if IID in existing:
        print("★%s 已存在 ⇒ 跳过 issue_log 写入" % IID)
    else:
        issues.append({
            "id": IID,
            "title": TITLE,
            "severity": "high",
            "source_blocker": "ISS-343",
            "source_agent": "main",
            "desc": DESC,
            "owner": OWNER,
            "reporter": "main",
            "raised": TODAY,
            "due": "2026-11-25",
            "status": "fixing",
            "external": False,
            "need_keys": ["main_e1_e2_board_side_rulings_20261117"],
            "task_brief": brief,
            "dispatched_at": TODAY,
            "verify_by": "main",
            "verify_result": None,
            "note": NOTE,
        })
        doc["issues"] = issues
        out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100)
        if not os.path.exists(BAK):
            shutil.copy2(LOG, BAK)
            print("★备份 ->", os.path.basename(BAK))
        atomic_write(LOG, out)
        print("★%s 已落 fixing (owner=%s)" % (IID, OWNER))

    # ---------- dispatch_log (顶层是 list ⇒ 追加式写回, 历史字节零改动) ----------
    dl = yaml.safe_load(open(DL, encoding="utf-8").read()) if os.path.exists(DL) else []
    if isinstance(dl, dict):
        dl_list = dl.setdefault("dispatches", [])
        shape = "dict"
    elif isinstance(dl, list):
        dl_list = dl
        shape = "list"
    else:
        dl_list, shape = [], "list"
    if any(e.get("issue") == IID for e in dl_list):
        print("★dispatch_log 已有 %s ⇒ 跳过" % IID)
    else:
        entry = {
            "issue": IID,
            "agent": OWNER,
            "at": TODAY,
            "brief": brief[:300],
            "job": ("cron fb67af40 (ARS45 队列自动派活) · ★派活时刻 2026-11-23 01:4x · "
                    "★**status 直接落 fixing ⇒ 兄弟 job 775d9893 的 advance.py --json 看不见本单 ⇒ 不会重复派**"),
        }
        if not os.path.exists(DL_BAK):
            shutil.copy2(DL, DL_BAK)
        with open(DL, "a", encoding="utf-8") as f:
            if shape == "list":
                f.write(yaml.safe_dump([entry], allow_unicode=True, sort_keys=False, width=200))
            else:
                f.write("")
        if shape == "dict":
            atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=200))
        print("★dispatch_log 已追加 1 条 (%s)" % IID)

    # ---------- 自检 ----------
    doc2 = yaml.safe_load(open(LOG, encoding="utf-8").read())
    ids = [i.get("id") for i in doc2["issues"]]
    dup = sorted({x for x in ids if ids.count(x) > 1})
    print("★issues 条数 =", len(ids), "· 重复 id =", dup or "无")
    hit = [i for i in doc2["issues"] if i.get("id") == IID]
    if hit:
        h = hit[0]
        print("★%s status=%s owner=%s due=%s brief=%d chars verify_by=%s"
              % (IID, h.get("status"), h.get("owner"), h.get("due"),
                 len(h.get("task_brief") or ""), h.get("verify_by")))
    dl2 = yaml.safe_load(open(DL, encoding="utf-8").read())
    dl2_list = dl2 if isinstance(dl2, list) else (dl2 or {}).get("dispatches", [])
    print("★dispatch_log 条数 =", len(dl2_list), "· 末条 =", dl2_list[-1].get("issue"))
    return 0 if not dup else 1


if __name__ == "__main__":
    sys.exit(main())
