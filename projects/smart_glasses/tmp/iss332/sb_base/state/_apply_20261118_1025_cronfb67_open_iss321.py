#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★新开 ISS-321 (sw-lead) = 「板只改一次」那一趟的 SW 侧: S1 位号改名【会不会把 SW 判据炸掉】(★status 直接落 fixing = 立即派出★)
   · cron fb67af40 (ARS45 队列自动派活) · 2026-11-18 10:2x★

★**为什么开这一单 (★main 10:2x 本机实读★)**:
  · 主板那一趟 = 位号改名 + 板侧同步 + 布局修正 + 布线 45→0 + Gerber/投产包重出 (★板只改一次★)
  · HW 侧: ISS-314/ISS-317 已实测 ⇒ 改名会炸 `state/check_pcb_nets.py` (NC 白名单 + --selftest 自崩)
  · SW 侧: ISS-318 只做了【文档侧】(40 份 SW/*.md 的位号引用) + 建了改名漂移闸 (自己 rename-safe)
    ⇒ ★**SW 侧 12 道脚本闸会不会被改名炸掉, 没人查过** ★
  · main 粗扫: `SW/tools/*.py` 里 13 个文件命中位号形状的 token ⇒ 值得逐条核
★**为什么 status 直接落 fixing (而不是 open)**: ★**本轮就派 ⇒ 直接落 fixing ⇒ 下一轮 cron 的 in_flight 规则会跳过 sw-lead ⇒ 没有重复派活窗口★**
"""
from __future__ import annotations

import fcntl
import os
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "issue_log.yaml")
DL = os.path.join(HERE, "dispatch_log.yaml")
LOCK = os.path.join(HERE, ".issue_log.lock")
NOW = "2026-11-18"

BRIEF = open(os.path.join(HERE, "dispatch_briefs",
                          "ISS-321_sw_rename_safety_audit.md"), encoding="utf-8").read()

TITLE = ("★★[主线内·SW 侧·纯分析 / 作业包 / 判据设计类·内部活] ★★【「板只改一次」那一趟的 SW 侧: "
         "S1 位号改名 (五侧同口径 · 186 个要改) 到底会不会把 SW 侧的 12 道判据脚本炸掉 —— 逐条实测 + 逐条逐字改法 + 执行顺序表】★★ ⇒ "
         "★**纯分析 / 作业包 / 判据设计类 · 零写板 · 零落表 · 零改闸 · 沙盒只写 tmp/ + logs/iss321/** ★")


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
    with open(LOCK, "a+") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        log = yaml.safe_load(open(LOG, encoding="utf-8")) or {}
        issues = log.get("issues") or []
        if any(i.get("id") == "ISS-321" for i in issues):
            print("=== ISS-321 已存在, 不重复开 ===")
            for i in issues:
                if i.get("id") == "ISS-321":
                    print("  status =", i.get("status"))
            return 0

        issues.append({
            "id": "ISS-321",
            "title": TITLE,
            "owner": "sw-lead",
            "status": "fixing",
            "severity": "high",
            "due": "2026-11-19",
            "created_at": NOW,
            "dispatched_at": NOW,
            "source_blocker": "board-onepass-S1-rename",
            "task_brief": BRIEF,
            "note": ("★**2026-11-18 10:2x · cron fb67af40 (ARS45 队列自动派活) 新开并直接派出 (status 直接落 fixing "
                     "⇒ 下一轮 in_flight 规则会跳过 sw-lead ⇒ 窗口消失 ⇒ 不与兄弟 job 775d9893 撞车)** ★ ★**开单依据 (★main 10:2x 本机实读★)**: "
                     "★**① 板那一趟要做 S1 位号改名 (五侧同口径 · 186 个要改)** ⇒ ★**② HW 侧已实测: 改名会炸 `state/check_pcb_nets.py` "
                     "(NC 白名单 `J_USB_C` 撞死 + `--selftest` 自己崩)** ⇒ ★**③ SW 侧只做过【文档侧】(ISS-318: 40 份 SW/*.md 的位号引用) "
                     "+ 自建了改名漂移闸 (它自己 rename-safe·RC-6 证明)** ⇒ ★**④ SW 侧另外 12 道判据脚本会不会被改名炸掉 = 没人查过** ★ "
                     "★**⑤ main 粗扫: `grep -rhoE \"\\b(R|C|U|L|D|Q|TP|CONN|J|SW|K|F|B|T|JP)_[A-Z0-9_]{1,14}\\b\" SW/tools/*.py` ⇒ 13 个文件命中** "
                     "⇒ ★**本单 = 逐条核真集 + 沙盒实跑 + 逐字改法 + 执行顺序表 (★零写板·零落表·零改闸★)** ★")
        })

        dl = yaml.safe_load(open(DL, encoding="utf-8")) if os.path.exists(DL) else {"dispatches": [], "entries": []}
        dl.setdefault("dispatches", []).append({
            "issue": "ISS-321", "agent": "sw-lead", "at": NOW,
            "brief": "★**新开单 + 直接派出 (status 直接落 fixing)** ★ ★**「板只改一次」那一趟的 SW 侧: S1 位号改名"
                     "(五侧同口径·186 个要改) 会不会炸掉 SW 侧 12 道判据脚本 —— 逐条实测 + 逐条逐字改法 + 执行顺序表** ★"})
        dl.setdefault("entries", []).append({
            "issue": "ISS-321", "agent": "sw-lead", "at": NOW,
            "brief": "★**新开单 + 直接派出 (status 直接落 fixing)** ★ ★**S1 位号改名对 SW 判据脚本的安全性体检 (★零写板·零落表·零改闸★)** ★"})

        atomic_write(LOG, yaml.safe_dump(log, allow_unicode=True, sort_keys=False, width=200))
        atomic_write(DL, yaml.safe_dump(dl, allow_unicode=True, sort_keys=False, width=200))
        print("=== apply done ===")
        print("  - ISS-321 新开 (sw-lead · status=fixing · 直接派出)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
