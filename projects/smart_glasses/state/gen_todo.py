#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 docs/TODO.md —— "接下来干什么"的可执行聚合视图
================================================================================
老板 10-25 20:00: "接下来的待办有没有推到 github 上?"
→ 待办本来就在 issue_log 里, 但那是**流水账**; 这份是**按"能不能动"分桶的行动清单**。

四桶:
  A 立刻可派   内部可自行推进 (owner 是三个总工) —— 不等任何人, 随时能派
  B 等你拍板   需老板一句话 (含建议默认值) —— 回了就能解锁下游
  C 等外部     等原厂/JBD (含 due 与到期升级点) —— 不是谁的锅
  D 依赖关系   谁解锁谁 (哪些事不做就永远卡着)

用法:  python3 state/gen_todo.py
"""
from __future__ import annotations

import collections
import datetime as dt
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
ROLE = {"hw-lead": "🔩 硬件总工", "sw-lead": "💻 软件总工", "mech-lead": "⚙️ 结构总工",
        "main": "🔧 项目总工"}
EXT_ROLE = {"boss": "👤 老板", "vendor": "🏭 酷芯微原厂", "jbd": "🏢 JBD"}

log = yaml.safe_load(open(os.path.join(HERE, "issue_log.yaml"), encoding="utf-8")) or {}
pm = yaml.safe_load(open(os.path.join(HERE, "fragments", "pm.yaml"), encoding="utf-8")) or {}
issues = log.get("issues") or []
open_iss = [i for i in issues if i.get("status") not in ("closed", "deferred", "wontfix")]
t = dt.date.today()


def dleft(due):
    try:
        return (dt.date.fromisoformat(str(due)) - t).days
    except Exception:  # noqa: BLE001
        return None


def due_tag(due):
    d = dleft(due)
    if d is None:
        return ""
    if d < 0:
        return f"⚠️逾期{-d}天"
    if d <= 2:
        return f"⏰剩{d}天"
    return f"剩{d}天"


A = [i for i in open_iss if i.get("owner") in ("hw-lead", "sw-lead", "mech-lead", "main")]
B = [i for i in open_iss if i.get("owner") == "boss"]
C = [i for i in open_iss if i.get("owner") in ("vendor", "jbd")]
Cext = [i for i in open_iss if i.get("owner") in ("boss", "vendor", "jbd")]

md = [
    "# 下一步行动清单 (TODO)",
    "",
    f"> 生成 **{dt.datetime.now().strftime('%Y-%m-%d %H:%M')}** | 自动生成 (源: `state/issue_log.yaml` + `state/fragments/pm.yaml`)",
    "> 分桶依据 = **能不能真的动** (内部 / 等你 / 等外部), 不是按严重度排",
    f"> 总量: 登记 **{len(issues)}** 条 | 未闭环 **{len(open_iss)}** | 已关闭 **{len(issues)-len(open_iss)}**",
    "",
    "## 0. 一句话现状",
    "",
    f"**A 桶 (内部可派) {len(A)} 条** · **B 桶 (等你) {len(B)} 条** · **C 桶 (等外部) {len(C)} 条**",
    "",
    "> 内部能干的都干了 → 现在推项目的**唯一瓶颈是外部** (原厂纸面资料 + JBD 外形图 + 3 份草稿未发)。",
    "",
    "## A. 立刻可派 —— 内部可自行推进 (不等任何人)",
    "",
]
by_agent = collections.defaultdict(list)
for i in A:
    by_agent[i["owner"]].append(i)
if not A:
    md.append("(无)")
for ag in ("main", "hw-lead", "sw-lead", "mech-lead"):
    rows = by_agent.get(ag)
    if not rows:
        continue
    md.append(f"### {ROLE[ag]} —— {len(rows)} 条")
    md.append("")
    md.append("| id | 严重度 | due | 事项 | 做什么 |")
    md.append("|---|---|---|---|---|")
    for i in sorted(rows, key=lambda x: ({"blocker": 0, "high": 1, "medium": 2, "low": 3}.get(x.get("severity"), 9), str(x.get("due")))):
        brief = str(i.get("task_brief") or "").splitlines()
        what = brief[0].replace("目标:", "").replace("目标: ", "") if brief else ""
        md.append(f"| {i.get('id')} | {i.get('severity')} | {i.get('due')} {due_tag(i.get('due'))} | {str(i.get('title'))[:48]} | {what[:70]} |")
    md.append("")

md += [
    "## B. 等你拍板 —— 回一句就能解锁下游",
    "",
    "| id | due | 事项 | 我的建议 | 不定的后果 |",
    "|---|---|---|---|---|",
]
SUGGEST = {
    "q16_display_iface": "先发原厂第二轮 (P0 第一问)",
    "q1_latency_scope": "口径 A (已拍板)",
    "q17_display_fps": "60fps 优先 (已拍板)",
    "q4_battery_scope": "按需触发 (已拍板)",
    "q18_highspeed_cam": "改主观眩晕验收 (已拍板, 数字部分待设备)",
    "test_equipment_budget": "高速相机+示波器: 自有 / 租 / 外委",
    "bridge_chip_quote": "不阻塞 (双出口已留); 但并行询价能抢 2 个月",
}
for i in sorted(B, key=lambda x: str(x.get("due"))):
    md.append(f"| {i.get('id')} | {i.get('due')} {due_tag(i.get('due'))} | {str(i.get('title'))[:56]} | "
              f"{SUGGEST.get(i.get('source_blocker') or '', '—')} | 卡住下游 |")
md += [
    "",
    "> 已拍板的 12 条决策 → `docs/DECISIONS.md`; 未拍的 → `state/fragments/pm.yaml` 的 `needs_from` (waiting_on=boss)",
    "",
    "## C. 等外部 —— 等原厂 / JBD (不是谁的锅, 但有 due 与升级点)",
    "",
    "| id | 外部方 | due | 升级点 | 事项 |",
    "|---|---|---|---|---|",
]
for i in sorted(C, key=lambda x: str(x.get("due"))):
    md.append(f"| {i.get('id')} | {EXT_ROLE.get(i.get('owner'), i.get('owner'))} | {i.get('due')} {due_tag(i.get('due'))} | "
              f"到期未回自动升级项目总工 | {str(i.get('title'))[:50]} |")
md += [
    "",
    "### ★ 草稿状态 (外发一律经老板)",
    "",
    "| 草稿 | 覆盖 issue | 状态 |",
    "|---|---|---|",
    "| `state/outbox/vendor_round2_email.md` | 9 条 | 🟡 已就绪, **老板决定保留不发** |",
    "| `state/outbox/jbd_query.md` | 3 条 | 🟡 已就绪, **老板决定保留不发** |",
    "| `state/outbox/bridge_chip_rfq.md` | 1 条 | 🟡 已就绪, **老板决定保留不发** |",
    "",
    "## D. 依赖关系 —— 谁解锁谁",
    "",
    "```",
    "① 3 份草稿发出 ──► 12 条外部 issue 解锁 ──► G1 原理图/PCB 定稿",
    "                    └─► JBD 的 2D 外形图 ──► 镜框开模 ──► G2",
    "                    └─► 光机 LED 波长/亮度/光通量 ──► 光生物安全评估",
    "",
    "② 打印环境 (打印机跨网段 + 量具) ──► M-PRINT ──► G2 少一项",
    "",
    "③ 测试设备 (高速相机/示波器/热电偶) ──► M-E2E 口径A + M-OPTIC ──► G3",
    "",
    "④ 内部 22 条 ──► 纸面滴水不漏 (不直接解锁 G0, 但让外部一解锁就能直接进 G1)",
    "```",
    "",
    "**结论**: ①②③ 全是**一次性的外部动作**; ④ 是**我们自己能做的**。所以接下来只有两类活: 等老板一句话, 以及把 ④ 推完。",
    "",
    "## E. 复现命令",
    "",
    "```bash",
    "cd projects/smart_glasses",
    "./status.sh                    # 一屏: 进展/待办/卡点/风险",
    "python3 state/advance.py       # 下一批可执行动作 (A 桶)",
    "python3 state/issue_check.py   # 问题闭环门",
    "python3 state/stage_gate.py    # 阶段门缺口",
    "python3 state/gen_todo.py      # 重新生成本文件",
    "```",
    "",
]
out = os.path.join(PROJ, "TODO.md")   # 与 CERT_CHECKLIST.md 同级 (发布时拷到 docs/)
open(out, "w", encoding="utf-8").write("\n".join(md))
print(f"✅ docs/TODO.md 已生成 (A={len(A)} B={len(B)} C={len(C)})")
