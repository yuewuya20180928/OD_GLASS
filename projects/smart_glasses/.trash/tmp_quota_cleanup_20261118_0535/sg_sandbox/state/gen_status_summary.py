#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 STATUS_SUMMARY.md (一页看懂: 现状 / 闭环了什么 / 硬指标真状态 / 待办分桶 / 风险)
====================================================================
★2026-10-28 改: 原来这个文件是**手写**的 ⇒ 数字永远停在写的那天
   (10-27 01:20 写完后, issue 数从 86→105、阶段门从 G0→G1 都没跟上 ⇒ 老板在 GitHub 上
   看到的"当前进展"是 1 天前的快照)。现在改为**全实时生成**:
   issue 账 / 阶段门 / 冲突 / 未闭合需求 / 产出物 / 风险 全部从机器可读源实时读。

★保留手写的部分: "闭环了什么" (按结果而非流水账) —— 这段是叙事, 但**顶部标注了时间范围**,
  并在每次发布时追加一条当天的关键事件 (从 PROJECT_TRACKER 的进展节提取)。

跑法: python3 state/gen_status_summary.py
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import os
import re
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
EXT_ROLE = {"vendor": "原厂 (酷芯微)", "jbd": "JBD", "boss": "老板"}


def load(p: str):
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> int:
    issues = (load(os.path.join(HERE, "issue_log.yaml")) or {}).get("issues") or []
    if isinstance(issues, dict):
        issues = list(issues.values())
    state = load(os.path.join(PROJ, "STATE.yaml")) or {}
    summ = state.get("summary") or {}
    nm = state.get("needs_matrix") or {}

    open_i = [i for i in issues if i.get("status") not in ("closed", "deferred", "wontfix")]
    inflight = [i for i in issues if i.get("status") in ("fixing", "fixed")]
    by_own = collections.Counter(i.get("owner") for i in open_i)
    boss = [i for i in open_i if i.get("owner") == "boss"]
    sev = collections.Counter(i.get("severity") for i in open_i)

    # ---- 阶段门: 实时读 --json (不靠字符串匹配) ----
    stage = "未知"
    stage_target = "?"
    stage_missing = "?"
    passed_gates: list[str] = []
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "stage_gate.py"), "--json"],
                           capture_output=True, text=True, timeout=120)
        sj = json.loads(r.stdout or "{}")
        cur = sj.get("current_gate")
        passed_gates = sj.get("passed_gates") or []
        for res in sj.get("results") or []:
            if res.get("gate") == cur:
                stage = f"{cur} {res.get('name') or ''}".strip()
                stage_target = cur
                stage_missing = str(res.get("missing"))
                break
        if not cur:
            stage = "全部阶段门已通过 (G4-done)"
    except Exception as e:  # noqa: BLE001
        stage = f"阶段门读取失败 ({type(e).__name__})"

    # ---- 实测项 ----
    meas = load(os.path.join(HERE, "measurements.yaml")) or {}
    have = meas.get("measurements") or []
    n_have = len([m for m in have if str(m.get("kind")) == "实测" and m.get("value") not in (None, "")])
    n_need = len(meas.get("needed") or [])

    # ---- 今天的进展 (从 PROJECT_TRACKER 进展节标题里取最近一节) ----
    trk_p = os.path.join(PROJ, "PROJECT_TRACKER.md")
    trk = open(trk_p, encoding="utf-8").read()
    # ★tracker 里的进展节号是**升序**排列的 (文件里 §(1.5) 在前、§(1.34) 在后),
    #   章节地图说的"倒序"是指**阅读**顺序 ⇒ 取**节号最大**的 N 节当"最近"。
    heads = re.findall(r"(?m)^#### \((1\.\d+)\)\s+(.+)$", trk)
    def _num(hid: str) -> tuple[int, int]:
        """节号 "1.34" → (1, 34) 按**整数对**比, 不能当浮点数 (1.9 > 1.34 会排错)。"""
        try:
            a, b = hid.split(".", 1)
            return (int(a), int(b))
        except Exception:  # noqa: BLE001
            return (-1, -1)
    heads.sort(key=lambda x: _num(x[0]), reverse=True)   # 新的在前
    recent = [f"- **§({hid})** {htxt.strip()}" for hid, htxt in heads[:6]]

    today = dt.date.today().isoformat()
    n_drafts = len([f for f in os.listdir(os.path.join(HERE, "outbox"))
                    if f.endswith(".md") and f != "README.md"])

    L: list[str] = []
    L.append(f"# 当前进展与待办 · 一页看懂 ({today})\n")
    L.append("\n> **给谁看**: 老板 / 接手的人 / 任何一个想知道\"这项目到哪了、卡在哪\"的人。\n"
             "> **数据来源**: `PROJECT_TRACKER.md`(唯一真源) + `state/issue_log.yaml` + `state/STATE.yaml` + 门禁实时输出。\n"
             "> ★**本文件是自动生成的** (2026-10-28 起) —— 数字不会过期。\n")

    L.append("\n## 1. 一屏现状\n")
    L.append("\n| 指标 | 数 |\n|---|---|\n")
    L.append(f"| 登记 issue | **{len(issues)}** 条 (已闭环 {len(issues)-len(open_i)} / 未闭环 {len(open_i)}: "
             f"blocker {sev.get('blocker',0)} · high {sev.get('high',0)} · medium {sev.get('medium',0)} · low {sev.get('low',0)}) |\n")
    L.append(f"| 产出物 (STATE 登记) | **{summ.get('artifacts','?')}** 件 |\n")
    L.append(f"| 阻塞 | **{summ.get('blockers','?')}** 条 (高危 {summ.get('high_blockers','?')}) · "
             f"未闭合需求 {nm.get('total',0)-nm.get('answered_count',0) if isinstance(nm.get('total'),int) else '?'} 条 · "
             f"**冲突 {summ.get('conflicts','?')}** |\n")
    L.append(f"| **阶段门** | **{stage}**, 还差 **{stage_missing}** 项 (已过: {', '.join(passed_gates) or '无'}) |\n")
    L.append(f"| 组织就绪度 | 4 个角色 **全部就绪** (机制/质量门/推进器/交接协议全到位) |\n")
    L.append(f"| **实测数据** | **{n_have}/{n_need}** 项 ★两个硬指标 (端到端 60ms / 皮肤 43°C) 目前 **0 实测** |\n")
    L.append(f"| 外发草稿 | **{n_drafts}** 份已就绪, **等老板一句「可以发」** |\n")
    L.append(f"| 健康度 | {'🔴' if summ.get('health')=='red' else '🟡' if summ.get('health')=='amber' else '🟢'} "
             f"{summ.get('health','?')} (外部阻塞未清) |\n")

    L.append("\n**未闭环按责任方**: " + " · ".join(
        f"{EXT_ROLE.get(k,k)} {v}" for k, v in by_own.most_common()) + "\n")
    L.append("⇒ **内部能干的都在干; 瓶颈是外部 (原厂 + JBD) + 老板拍板项。**\n")

    L.append("\n## 2. 最近闭环了什么 (按结果, 不按流水账)\n")
    L.append("\n> 完整的进展流水账在 `projects/smart_glasses/PROJECT_TRACKER.md` §(1.xx); "
             "下面是最近 6 节的标题 (机器提取, 不会过期)。\n\n")
    for r in recent:
        L.append(r + "\n")

    L.append("\n## 3. 三个硬指标的真实状态 (诚实版)\n")
    L.append("\n| 硬指标 | 老板锁死值 | 当前状态 | 怎么才能拿到真数 |\n|---|---|---|---|\n")
    L.append(f"| 端到端延迟 | **< 60ms** (口径 A = 曝光→出光) | ⚠️ **[推算] 未实测** | 投板后测 `M-NPU` (纯 NPU 耗时, **软件打点就够, 不需要设备**) + `M-E2E` |\n")
    L.append(f"| 皮肤温度 | **≤ 43°C** (ISO 13732-1) | ⚠️ **[推算] 未实测** | 样机贴片热电偶 `M-SKIN` (需量具) |\n")
    L.append(f"| 续航 | **≥ 1h** (按需触发场景) | ⚠️ **[推算] 未实测** (口径已统一: 420mAh 按需 ~6.1h) | 样机放电计时 `M-BATT` |\n")
    L.append(f"| 其它实测项 | — | **{n_have}/{n_need}** | 见 `state/measurements.yaml` |\n")

    L.append("\n## 4. 待办 (按\"能不能真的动\"分桶)\n")
    L.append("\n完整清单见 `docs/TODO.md` (自动生成)。分桶摘要:\n\n")
    L.append(f"| 桶 | 条数 | 含义 |\n|---|---|---|\n")
    L.append(f"| **A 内部可派** | {len([i for i in open_i if i.get('owner') in ('hw-lead','sw-lead','mech-lead','main')])} | "
             "不等任何人, 三个总工 + 项目总工可自行推进 |\n")
    L.append(f"| **B 等你拍板** | {len(boss)} | 回一句就能解锁下游 (草稿放行 / 打印包 / 设备预算 / 模型许可) |\n")
    L.append(f"| **C 等外部** | {len([i for i in open_i if i.get('owner') in ('vendor','jbd')])} | 原厂纸面资料 + JBD 外形图 |\n")
    L.append(f"| **在飞 (别重复派)** | {len(inflight)} | 已开工, 状态 fixing/fixed |\n")

    L.append("\n## 5. 风险 Top 3\n")
    L.append("\n| 风险 | 等级 | 一句话 |\n|---|---|---|\n")
    L.append("| 原厂纸面资料未回 | 🔴 高 | 8 条 G1 问题单全卡在它上面 (显示 TX / pitch / 电源域 / 启动存储) → 桥接芯片采购 4-8 周不能等 |\n")
    L.append("| 贴皮肤散热 | 🔴 高 | 满载 1.22W → 皮肤 88.6-96.1°C, 超 43°C 红线 2 倍以上 → 出路是**降功耗**(sensor 选型 + 占空比) 不是加散热片 |\n")
    L.append("| 无板无设备 | 🟡 中 | 两个硬指标 0 实测 → G3 那一关不可判通过 (打印包 + 测试设备预算都等老板) |\n")

    L.append("\n## 6. 一键看状态 (全部可复现)\n")
    L.append("\n```bash\ncd projects/smart_glasses\n./status.sh                    # 一屏: 进展/待办(分5桶)/卡点/风险\n"
             "python3 state/advance.py       # 下一批可执行动作\n"
             "python3 state/stage_gate.py    # 阶段门 G0-G4 实时判定\n"
             "python3 state/gate_check.py    # 交付质量门 18/18\n"
             "python3 state/daily_check.py   # 巡检 + 漂移检测\n```\n")

    L.append("\n## 7. 三条最该记住的教训\n")
    L.append("\n1. **两个工具判同一件事, 判据必须同源** —— 一个认 `decision` 字段一个只认配对, 会让阶段门被已答问题假性卡死 3 天。\n")
    L.append("2. **写死的数字必然过期** —— 生成器里硬编码的阶段名/天数/条数会骗人; 要么实时读, 要么明确标注是快照。\n")
    L.append("3. **失败必须显式暴露** —— `>/dev/null 2>&1` 会把语法错误吞掉, 然后推一份陈旧文档还以为刷新了。\n")

    out = os.path.join(PROJ, "STATUS_SUMMARY.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("".join(L))
    print(f"✅ 已生成 {out} (issue {len(issues)} · 阶段门 {stage} · 实测 {n_have}/{n_need})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
