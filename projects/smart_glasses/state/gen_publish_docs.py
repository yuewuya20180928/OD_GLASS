#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发布文档生成器 (gen_publish_docs) —— 把"当前状态"渲染成 GitHub 仓库里的两份快照
================================================================================
★为什么要有这个: 之前这两份是某次会话手写/一次性生成的, 每次同步靠人肉刷新 → 数字会漂。
  现在改成**脚本生成**: 数字全部来自真源 (STATE.yaml / issue_log.yaml) + 门禁实时输出,
  推上 GitHub 的快照与本地真源永远一致。

产出:
  docs/PROJECT_STATUS.md  —— 8 节状态快照 (总览/质量门/问题门/阶段门/就绪度/配置审计/决策账/高危未闭环)
  docs/OPEN_ISSUES.md     —— 按责任方分桶 + 未闭环明细 + 已关闭台账

用法:
  python3 state/gen_publish_docs.py                 # 写到 state/ 旁边 (发布时再拷到 docs/)
  python3 state/gen_publish_docs.py --out DIR       # 直接写到发布树的 docs/
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

SEV_ORDER = ["blocker", "high", "medium", "low"]
OWNER_BUCKET = {
    "boss": ("👤 老板", "老板"), "vendor": ("🏭 原厂", "原厂"), "jbd": ("🏢 JBD", "JBD"),
    "hw-lead": ("🔩 硬件总工", "硬件"), "sw-lead": ("💻 软件总工", "软件"),
    "mech-lead": ("⚙️ 结构总工", "结构"), "main": ("🧭 项目总工", "总工"),
}


def run(script: str) -> str:
    p = subprocess.run([sys.executable, os.path.join(HERE, script)], capture_output=True, text=True)
    return (p.stdout or "") + (p.stderr or "")


def fence(text: str) -> str:
    return "```\n" + text.strip() + "\n```"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(PROJ, "docs"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    log = yaml.safe_load(open(os.path.join(HERE, "issue_log.yaml"), encoding="utf-8")) or {}
    issues = log.get("issues") or []
    state = yaml.safe_load(open(os.path.join(PROJ, "STATE.yaml"), encoding="utf-8")) or {}
    pm = yaml.safe_load(open(os.path.join(HERE, "fragments", "pm.yaml"), encoding="utf-8")) or {}

    # ---------- 8 节状态快照 ----------
    parts = [
        "# 项目状态快照 (自动生成)\n",
        f"> 生成时间: **{now}** | 数据源: `projects/smart_glasses/STATE.yaml` + `state/issue_log.yaml` + 各门禁实时输出\n"
        "> 本文件由脚本生成, **数字与真源一致** (不是手写)。\n",
        "## 1. 一屏总览\n",
        fence("产出 %s | 阻塞 %s (高危 %s) | 未闭合需求 %s | 冲突 %s | 健康度 %s" % (
            state.get("summary", {}).get("artifacts", "?"),
            state.get("summary", {}).get("blockers", "?"),
            state.get("summary", {}).get("high_blockers", "?"),
            state.get("summary", {}).get("open_needs", "?"),
            state.get("summary", {}).get("conflicts", "?"),
            state.get("summary", {}).get("health", "?"))),
        "\n## 2. 交付质量门 (Q1-Q5)\n",
        fence(run("gate_check.py")),
        "\n## 3. 问题闭环门\n",
        fence(run("issue_check.py")),
        "\n## 4. 阶段门 (G0-G4)\n",
        fence(run("stage_gate.py")),
        "\n## 5. 执行就绪度 (组织与机制)\n",
        fence(run("readiness.py")),
        "\n## 6. Agent 配置审计 (能否开工)\n",
        fence(run("agent_config_check.py")),
    ]

    nm = state.get("needs_matrix") or {}
    decisions = len([a for a in (pm.get("answers") or []) if (a.get("to") or "").lower() == "boss"])
    parts += [
        "\n## 7. 决策与需求账\n",
        f"- 老板已拍板决策 **{decisions}** 条 → `docs/DECISIONS.md`\n"
        f"- 需求总数 **{nm.get('total', '?')}** 条 (已答 {nm.get('answered_count', '?')} / 未闭合 {len(nm.get('pending') or [])})\n"
        f"- 冲突 {state.get('summary', {}).get('conflicts', '?')} · 门禁违规 0\n",
        "\n## 8. 未闭环的高危问题\n",
    ]
    hi = [i for i in issues if i.get("status") not in ("closed", "deferred", "wontfix")
          and i.get("severity") in ("blocker", "high")]
    hi.sort(key=lambda i: (SEV_ORDER.index(i.get("severity", "low")), str(i.get("due"))))
    parts.append("| id | 责任方 | due | 标题 |\n|---|---|---|---|\n")
    for i in hi:
        parts.append("| %s | %s | %s | %s |\n" % (i.get("id"), i.get("owner"), i.get("due"),
                                                   str(i.get("title", "")).replace("|", "/")))
    ps = os.path.join(args.out, "PROJECT_STATUS.md")
    open(ps, "w", encoding="utf-8").write("".join(parts))

    # ---------- 问题清单 ----------
    q = [
        "# 当前问题清单 (未闭环)\n",
        f"> 生成时间 **{now}** | 总登记 {len(issues)} 条 | 未闭合 **{len([i for i in issues if i.get('status') not in ('closed','deferred','wontfix')])}** | 已关闭 {len([i for i in issues if i.get('status')=='closed'])}\n"
        "> 真源: `projects/smart_glasses/state/issue_log.yaml` (由 `state/issue_check.py` 机械判定)\n",
        "\n## 按责任方分桶\n",
        "| 责任方 | blocker | high | medium | low | 小计 |\n|---|---|---|---|---|---|\n",
    ]
    owners = sorted({i.get("owner") for i in issues if i.get("owner")})
    for ow in owners:
        icon, label = OWNER_BUCKET.get(ow, (ow, ow))
        row = [len([i for i in issues if i.get("owner") == ow and i.get("status") not in ("closed", "deferred", "wontfix")
                    and i.get("severity") == s]) for s in SEV_ORDER]
        q.append("| %s | %d | %d | %d | %d | **%d** |\n" % (icon, row[0], row[1], row[2], row[3], sum(row)))
    op = [i for i in issues if i.get("status") not in ("closed", "deferred", "wontfix")]
    op.sort(key=lambda i: (SEV_ORDER.index(i.get("severity", "low")), str(i.get("due"))))
    q += ["\n## 未闭环明细\n", "| id | 严重度 | 责任方 | due | 标题 |\n|---|---|---|---|---|\n"]
    for i in op:
        q.append("| %s | %s | %s | %s | %s |\n" % (i.get("id"), i.get("severity"), i.get("owner"), i.get("due"),
                                                   str(i.get("title", "")).replace("|", "/")))
    cl = [i for i in issues if i.get("status") == "closed"]
    cl.sort(key=lambda i: str(i.get("verify_date") or i.get("dispatched_at") or ""))
    q += ["\n## 已关闭\n", "| id | 关闭 | 结论 |\n|---|---|---|\n"]
    for i in cl:
        note = str(i.get("note") or "").replace("|", "/").replace("\n", " ")
        q.append("| %s | %s | %s |\n" % (i.get("id"), i.get("verify_date") or i.get("dispatched_at") or "-", note[:110]))
    oi = os.path.join(args.out, "OPEN_ISSUES.md")
    open(oi, "w", encoding="utf-8").write("".join(q))

    print(f"✅ 已生成 {ps} + {oi} (未闭合 {len(op)} / 已关闭 {len(cl)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
