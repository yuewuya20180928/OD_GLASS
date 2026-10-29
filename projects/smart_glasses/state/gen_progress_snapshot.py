#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 PROGRESS_SNAPSHOT.md —— token 断电前的"可恢复快照" (老板 09:59 要求: 进展+待办必须先落盘)。

★原则: 所有数字**实时读**, 一个都不写死 (AGENTS.md 铁律: 写死的数字必然过期)。

用法: python3 state/gen_progress_snapshot.py
"""
from __future__ import annotations

import datetime
import os
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
OUT = os.path.join(PROJ, "PROGRESS_SNAPSHOT.md")


def sh(cmd, cwd=PROJ):
    try:
        return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=120).stdout.strip()
    except Exception as e:
        return f"<{e}>"


def main() -> int:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    log = yaml.safe_load(open(os.path.join(HERE, "issue_log.yaml"), encoding="utf-8"))
    items = log["issues"] if isinstance(log.get("issues"), dict) else (log.get("issues") or [])
    by_status = {}
    for it in items:
        by_status[it.get("status")] = by_status.get(it.get("status"), 0) + 1

    fixing = [it for it in items if it.get("status") == "fixing"]
    open_boss = [it for it in items if it.get("owner") == "boss" and it.get("status") not in ("closed", "verified", "deferred", "wontfix")]
    open_main = [it for it in items if it.get("owner") == "main" and it.get("status") in ("open", "fixing")]
    internal = [it for it in items if it.get("owner") in ("hw-lead", "sw-lead", "mech-lead") and it.get("status") == "open"]

    stage = sh("python3 state/stage_gate.py --json 2>/dev/null | head -c 600")
    status_line = sh("./status.sh 2>/dev/null | sed -n '4p'")
    gate = sh("python3 state/gate_check.py 2>/dev/null | grep -E 'Q1' | head -1")
    merge_rc = subprocess.run("python3 state/merge.py >/dev/null 2>&1", shell=True, cwd=PROJ).returncode
    issue_rc = subprocess.run("python3 state/issue_check.py >/dev/null 2>&1", shell=True, cwd=PROJ).returncode
    last_push = ""
    lp = os.path.join(HERE, ".last_github_push")
    if os.path.exists(lp):
        last_push = open(lp, encoding="utf-8").read().strip()

    lines = [
        f"# PROGRESS_SNAPSHOT.md —— 进展快照 (自动生成 {now})",
        "",
        "> ★**这是 token 断电前的续传凭据**。会话被掐断后: 先读本文件 + `TASK_BOARD.md`, 再继续干活。",
        "> ★本文件由 `state/gen_progress_snapshot.py` 生成, **数字全部实时读, 不写死**。",
        "",
        "## 一、当前状态",
        "",
        f"- 阶段门: {status_line or '(见 ./status.sh)'}",
        f"- 交付质量门: {gate or '(未取到)'}",
        f"- 门禁: merge rc={merge_rc} · issue rc={issue_rc}",
        f"- 问题单: 共 {len(items)} 条 · " + " · ".join(f"{k}={v}" for k, v in sorted(by_status.items())),
        f"- GitHub 上次推送: {last_push or '(未知)'}",
        "",
        "## 二、执行中 (谁在干什么)",
        "",
    ]
    if fixing:
        for it in fixing:
            lines.append(f"- **{it['id']}** · {it.get('owner')} · {str(it.get('title'))[:70]} · 派出于 {it.get('dispatched_at') or '?'}")
    else:
        lines.append("- (无)")
    lines += ["", "## 三、待办", "", "### 3.1 等老板拍板 (外部依赖, 不算总工失职)", ""]
    if open_boss:
        for it in open_boss:
            lines.append(f"- {it['id']} · {str(it.get('title'))[:78]}")
    else:
        lines.append("- (无)")
    lines += ["", "### 3.2 等我做 (项目总工)", ""]
    if open_main:
        for it in open_main:
            lines.append(f"- {it['id']} · {str(it.get('title'))[:78]}")
    else:
        lines.append("- (无)")
    lines += ["", "### 3.3 三个总工可自行推进 (队列 cron 每 30 分钟自动派)", ""]
    if internal:
        for it in internal[:12]:
            lines.append(f"- {it['id']} · {it.get('owner')} · {str(it.get('title'))[:70]}")
        if len(internal) > 12:
            lines.append(f"- …另有 {len(internal)-12} 条")
    else:
        lines.append("- (无)")
    lines += [
        "",
        "## 四、恢复步骤 (token 恢复后照此走)",
        "",
        "1. `cd projects/smart_glasses && git pull` (或读本文件 + TASK_BOARD.md)",
        "2. 读 `TASK_BOARD.md` §1 (老板最新任务) / §2 (执行中) / §3 (待办)",
        "3. 读本文件 §2 / §3 确认最新状态",
        "4. **先落盘再干活**: 新任务先登记到 `TASK_BOARD.md` + `state/issue_log.yaml`, 再动手",
        "",
        "## 五、阶段门原始输出",
        "",
        "```",
        stage[:800],
        "```",
        "",
    ]
    text = "\n".join(lines)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, OUT)
    print(f"✅ PROGRESS_SNAPSHOT.md 已生成 ({len(text)} B, {now})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
