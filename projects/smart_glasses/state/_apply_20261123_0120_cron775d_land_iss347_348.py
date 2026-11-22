#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_apply_20261123_0120_cron775d_land_iss347_348.py
================================================================================
cron 775d9893 (ARS45 继续执行后继计划) · 2026-11-23 01:2x
--------------------------------------------------------------------
把本 job 本轮的两条【main 自有内部活】落台账:

★**ISS-347 (owner=main · status=fixed)**:
  `state/advance.py --apply` 的落盘路径一直是坏的 ⇒ `state/dispatch_log.yaml` 顶层是 **list**
  ⇒ 旧代码 `dl.setdefault("dispatches", [])` ⇒ **AttributeError** ⇒
  ★**两个 cron job 的「派完标 fixing + 写派活日志」从来没自动跑通过** ⇒
  本 job 已修 (state/advance.py) + 已建端到端单测 (5/5 含反向用例) + 真盘空跑三项 md5 不变

★**ISS-348 (owner=main · status=open)**:
  ★**跨 job 基础设施红**: `/tmp` 是带 **userquota** 的 tmpfs (7.5G) 而用户配额已被打满 ⇒
  任何写 /tmp 的作业都在 EDQUOT 上失败 (★实测: 连 14 KB 的 cp 都失败·dd 20M 失败·
  本 job 的 `issue_check.py` 重定向到 /tmp 时拿到 rc=120 + 0 字节 = 假读数★) ⇒
  占用大头 = `/tmp/od_glass_publish` 4.1G (★5 小时 GitHub 同步 job 的发布暂存目录·01:15 还在被写
  ⇒ **那个 job 此刻正在跑** ⇒ **不许此刻动它**★) + `/tmp/adv_sandbox` 680M (子 agent 正在用)
  ⇒ 建议: ①发布暂存改落项目盘或推完即清 ②子 agent 沙盒改落项目盘 (本 job 的单测已改)
  ③门禁输出不许重定向到 /tmp (⇒ 假读数会把「闸红」和「闸崩」混成一团)

★**为什么这两条是 main 自有地界**:
  ① `state/advance.py` = 派活工具 = main 的机制地界 (三个总工的闸不许他们改, 同款)
  ② `/tmp` 配额是机器级基础设施 ⇒ 登记成 main 的内部活, 但**动手要等 GitHub 同步 job 跑完**
     (★那个 job 的暂存目录此刻在被写 ⇒ 此刻动它 = 把别人的活打断★)

★**原子写 + 带 .bak + 幂等** ★
"""
from __future__ import annotations

import os
import shutil
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
BAK = LOG + ".bak_20261123_0120_cron775d_land_iss347_348"
TODAY = "2026-11-23"

T347_TITLE = (
    "★★[★主线·派活/门禁机制侧·内部活·零写板] ★★"
    "【`state/advance.py --apply` 的落盘路径一直是坏的: `state/dispatch_log.yaml` 顶层是 list "
    "⇒ 旧代码 dl.setdefault('dispatches',[]) ⇒ AttributeError ⇒ 两个 cron job 的「派完标 fixing + 写派活日志」"
    "从来没自动跑通过 ⇒ 修 (两种形状都认 + 追加式写回 + 写回后自检) + 端到端单测 5/5 (含反向用例: 旧备份跑同一沙盒必须复现 AttributeError)】★★"
)

T347_DESC = (
    "★**main 本机实读 + 实跑 (不抄任何 agent 报告)★** ⇒ "
    "★**① 病灶**: `state/dispatch_log.yaml` 顶层类型 = **list** (334 条 / 291 KB) ⇒ "
    "`state/advance.py` 的 `dl.setdefault('dispatches', []).append(...)` ⇒ **AttributeError** ⇒ "
    "★**派活落盘这一步从来没自动跑通过** (兄弟 job fb67 只能绕开它、自己原子写 fixing) ★ "
    "★**② 修法 (只改 state/advance.py 一处, 判据/阈值/排序一个字没动)**: "
    "① 两种形状都认 (list ⇒ 直接追加; dict ⇒ dispatches 键), 写回时保持原形状; "
    "② 追加式写回 ⇒ 历史 291 KB 字节零改动 (零 churn); "
    "③ 空跑零写 ⇒ 只有真有新派活或文件不存在才写盘; "
    "④ 写回后自检 (条目数 + 末条一致性) ⇒ 不一致即 sys.exit(2) ★ "
    "★**③ 单测**: 新增 `state/test_advance_apply_dispatch_log.py` (端到端跑真 advance.py): "
    "T1 list 形状落盘 ✅ / T2 dict 形状落盘 ✅ / T3 --only 过滤 ✅ / T4 空跑零 churn ✅ / "
    "T5 反向用例 (修复前备份跑同一沙盒 ⇒ 必须复现 AttributeError) ✅ ⇒ **ALL TESTS PASS (5/5) rc=0** ★ "
    "★**④ 真盘实跑**: `python3 state/advance.py --apply` ⇒ rc=1 (无可执行动作的正常退出码) ⇒ "
    "dispatch_log md5 `4e4e3b87b713e436ad1685481682b8d7` 前后不变 + issue_log md5 `4a75ac43ad05e39dcda3ed73af8e74c9` 前后不变 "
    "+ 板 md5 `611b869e13518c3c023fb178f91a0075` 前后不变 ⇒ ★**旧代码在这一步直接抛 AttributeError** ★ "
    "★**⑤ 详见**: `state/NOTES_20261123_0120_advance_apply_dispatch_log_fix.md` ★"
)

T348_TITLE = (
    "★★[★基础设施·跨 job·内部活·零写板] ★★"
    "【/tmp 是带 userquota 的 tmpfs (7.5G) 而用户配额已被打满 ⇒ 任何写 /tmp 的作业都在 EDQUOT 上失败 "
    "(★实测: 连 14 KB 的 cp 都失败·dd 20M 失败·本 job 把 issue_check 输出重定向到 /tmp 时拿到 rc=120 + 0 字节 = 假读数★) "
    "⇒ 占用大头 = /tmp/od_glass_publish 4.1G (5 小时 GitHub 同步 job 的发布暂存目录·01:15 还在被写 ⇒ 此刻正在跑·不许此刻动) "
    "+ /tmp/adv_sandbox 680M (子 agent 正在用) ⇒ 建议: 发布暂存改落项目盘或推完即清 + 子 agent 沙盒改落项目盘 (本 job 的单测已改) "
    "+ 门禁输出不许重定向到 /tmp】★★"
)

T348_DESC = (
    "★**main 本机实读 + 实跑 (2026-11-23 01:1x)★** ⇒ "
    "★**① 挂载**: `tmpfs on /tmp type tmpfs (rw,nosuid,nodev,nr_inodes=1048576,inode64,userquota)` · 7.5G · "
    "系统层 df 仍显示 1.5G 可用 ⇒ ★**但用户配额已满** (df 看不出来·只有写的时候才炸) ★ "
    "★**② 实测**: `cp` 14 KB 文件 ⇒ `Disk quota exceeded`; `dd bs=1M count=20` ⇒ `IO error: Disk quota exceeded`; "
    "`mkdir` 能建但写不进文件 ⇒ ★**/tmp 现在实际不可用** ★ "
    "★**③ 假读数 (★这条最危险★)**: 本 job 跑 `state/issue_check.py` 时把 stdout 重定向到 /tmp ⇒ "
    "拿到 **rc=120 + 输出 0 字节** ⇒ ★**差点被当成「闸崩了」读** ⇒ 同一时刻直接跑同一条命令 ⇒ rc=1 + 341 条清单正常出 ★ "
    "★**④ 占用大头**: `du -sh /tmp/od_glass_publish` = **4.1G** (★`.git/FETCH_HEAD` 01:15 还在被写 ⇒ 5 小时 GitHub 同步 job 此刻正在跑 ⇒ **不许此刻动它**★) "
    "+ `/tmp/adv_sandbox` = **680M** (00:56 起·子 agent 正在用·同样不许动) ★ "
    "★**⑤ 本 job 已自救**: 新写的单测沙盒从 /tmp 改落项目盘 (`state/.tmp_advselftest/`·用完即删) ⇒ 不再吃 /tmp 配额 ★ "
    "★**⑥ 待办 (★动手要等 GitHub 同步 job 跑完那一趟★)**: ①发布暂存目录改落项目盘或推完即清 ⇒ 否则 5 小时 job 的 rsync 会继续 EDQUOT ⇒ GitHub 推不出去; "
    "②子 agent 沙盒一律落项目盘; ③门禁命令输出不许落 /tmp ★"
)


def atomic_write(path: str, text: str) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def main() -> int:
    doc = yaml.safe_load(open(LOG, encoding="utf-8").read()) or {}
    issues = doc.get("issues") or []
    have = {i.get("id") for i in issues}

    def add(rec):
        if rec["id"] in have:
            print("★%s 已存在 ⇒ 跳过 (幂等)" % rec["id"])
            return
        issues.append(rec)
        have.add(rec["id"])
        print("★新增 %s (owner=%s status=%s)" % (rec["id"], rec["owner"], rec["status"]))

    add({
        "id": "ISS-347",
        "title": T347_TITLE,
        "severity": "high",
        "source_blocker": None,
        "source_agent": "main",
        "desc": T347_DESC,
        "owner": "main",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-30",
        "status": "fixed",
        "external": False,
        "need_keys": [],
        "task_brief": (
            "★**修 `state/advance.py --apply` 的落盘路径 (★修在产生点★)** ★\n"
            "① 病灶: `state/dispatch_log.yaml` 顶层是 list ⇒ `dl.setdefault('dispatches',[])` ⇒ AttributeError ⇒ "
            "派活落盘从来没自动跑通过 ★\n"
            "② 修法: 两种形状都认 + 追加式写回 (历史字节零改动) + 空跑零写 + 写回后自检 (不一致即 exit 2) ★\n"
            "③ 单测: `python3 -B state/test_advance_apply_dispatch_log.py` ⇒ 5/5 (含反向用例) ★\n"
            "④ 真盘: `python3 state/advance.py --apply` ⇒ 不崩 + 三项 md5 不变 ★\n"
            "★**边界**: 零写板 · 零改他 agent 分片 · 零改判据 · 零外发 ★"
        ),
        "dispatched_at": TODAY,
        "verify_by": "hw-lead",
        "verify_result": None,
        "fix_ref": (
            "state/NOTES_20261123_0120_advance_apply_dispatch_log_fix.md + "
            "state/test_advance_apply_dispatch_log.py (5/5 ALL TESTS PASS) + state/advance.py (修在产生点) + "
            "state/.bak_advance_20260723_0120_pre_dispatchlog_fix.py"
        ),
        "note": (
            "★**status=fixed 而不是 verified** ⇒ ★**自己修自己验 = 没验** ⇒ verify_by=hw-lead (另一个总工) ⇒ "
            "★**不许 main 自己把它签成 verified** ★ · ★**本条是本 job (cron 775d9893) 2026-11-23 01:2x 自修自登**★"
        ),
    })

    add({
        "id": "ISS-348",
        "title": T348_TITLE,
        "severity": "high",
        "source_blocker": None,
        "source_agent": "main",
        "desc": T348_DESC,
        "owner": "main",
        "reporter": "main",
        "raised": TODAY,
        "due": "2026-11-25",
        "status": "open",
        "external": False,
        "need_keys": [],
        "task_brief": (
            "★**把 /tmp 的 EDQUOT 打死** (★跨 job 基础设施★) ★\n"
            "① 先确认 GitHub 同步 job 那一趟跑完 (★`.git/FETCH_HEAD` mtime 不再动★) ⇒ ★**它还在跑就不许动它的暂存目录**★ ★\n"
            "② 处置 `/tmp/od_glass_publish` (4.1G) ⇒ 推完即清 或 改落项目盘 ⇒ **别删仓库源** (源在 workspace) ★\n"
            "③ 子 agent 沙盒目录一律落项目盘 (★本 job 的单测已改·口径可抄★) ★\n"
            "④ 门禁命令输出不许落 /tmp ⇒ 假读数 (rc=120/0 字节) 会把「闸红」和「闸崩」混成一团 ★\n"
            "★**边界**: 零写板 · 零外发 · 零代拍 · **不许在 GitHub 同步 job 正在跑的时候动它的暂存目录** ★"
        ),
        "dispatched_at": None,
        "verify_by": "main",
        "verify_result": None,
        "note": (
            "★**status=open** ⇒ ★**本 job 只登记不动手**★ ⇒ 理由 = ★**`/tmp/od_glass_publish` 此刻被 5 小时 GitHub 同步 job 写着 "
            "(`.git/FETCH_HEAD` 01:15) ⇒ 此刻清它 = 把别人的活打断**★ ⇒ ★**等那一趟跑完再动**★ ★ "
            "★**已自救的部分**: 本 job 的新单测沙盒已改落项目盘 ⇒ 不再吃 /tmp 配额**★"
        ),
    })

    doc["issues"] = issues
    out = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100)
    if not os.path.exists(BAK):
        shutil.copy2(LOG, BAK)
        print("★备份 ->", os.path.basename(BAK))
    atomic_write(LOG, out)

    doc2 = yaml.safe_load(open(LOG, encoding="utf-8").read())
    ids = [i.get("id") for i in doc2["issues"]]
    dup = sorted({x for x in ids if ids.count(x) > 1})
    print("★issues 条数 =", len(ids), "· 重复 id =", dup or "无")
    for iid in ("ISS-347", "ISS-348"):
        h = [i for i in doc2["issues"] if i.get("id") == iid]
        if h:
            print("★%s status=%s owner=%s verify_by=%s" %
                  (iid, h[0].get("status"), h[0].get("owner"), h[0].get("verify_by")))
    return 0 if not dup else 1


if __name__ == "__main__":
    sys.exit(main())
