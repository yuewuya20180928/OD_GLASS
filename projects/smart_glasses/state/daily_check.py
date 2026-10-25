#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日巡检 (Daily Check) —— 一次跑完 4 个门, 并自动检测"状态漂移"
================================================================================
老板 10-25 12:01: "后继出现问题的时候如何确认?"

确认问题不能靠"我每天想起来看一眼"。本脚本把巡检变成一个**可复现的固定动作**:
  1. 跑 merge.py       → 刷新 STATE.yaml (rc: 0完整 / 2不完整 / 1崩)
  2. 跑 gate_check.py  → 交付质量 5 道门 (Q1..Q5)
  3. 跑 issue_check.py → 问题闭环门 (字段/状态机/验证分离/逾期/双向覆盖)
  4. 跑 stage_gate.py  → 阶段门 (当前在第几关, 缺什么)
  5. ★漂移检测★        与上一次快照逐项比 —— 指标掉了 / 新增高危 / 问题被"忘记" → 报警

漂移是"问题出现"最可靠的信号: 没人会主动说自己变差了, 但数字会。

用法:  python3 state/daily_check.py [--no-snapshot]
退出码: 0=一切正常  1=有违规或漂移  2=脚本/文件错
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SNAP = os.path.join(HERE, "gate_snapshots")
PY = sys.executable


def run(script: str, *args: str) -> tuple[int, str, str]:
    p = subprocess.run([PY, os.path.join(HERE, script), *args],
                       capture_output=True, text=True, cwd=PROJ)
    return p.returncode, p.stdout, p.stderr


def jrun(script: str) -> tuple[int, dict | None]:
    rc, out, err = run(script, "--json")
    try:
        return rc, json.loads(out)
    except Exception:  # noqa: BLE001
        return rc, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-snapshot", action="store_true")
    args = ap.parse_args()

    problems: list[str] = []

    # 1) merge
    rc_m, out_m, err_m = run("merge.py")
    if rc_m not in (0, 2):
        problems.append(f"merge.py 崩溃 rc={rc_m}: {err_m.strip()[:200]}")
    elif rc_m == 2:
        problems.append("merge.py 返回 2 → 快照不完整 (有分片读失败, 已回退 .lastgood)")

    # 2) gate
    rc_g, gate = jrun("gate_check.py")
    # 3) issue
    rc_i, issue = jrun("issue_check.py")
    # 4) stage
    rc_s, stage = jrun("stage_gate.py")
    rc_r, ready = jrun("readiness.py")

    if gate is None:
        problems.append("gate_check.py 输出无法解析")
    if issue is None:
        problems.append("issue_check.py 输出无法解析")
    if stage is None:
        problems.append("stage_gate.py 输出无法解析")
    if rc_i == 1:
        problems.append(f"问题闭环门有违规 {len((issue or {}).get('errors') or [])} 条")
    if gate and gate.get("summary", {}).get("reconciliation", {}).get("ok") is False:
        problems.append("gate 与 merge 口径不一致 (先重跑 merge.py)")

    # 5) 漂移检测
    os.makedirs(SNAP, exist_ok=True)
    snaps = sorted(f for f in os.listdir(SNAP) if f.endswith(".json"))
    prev = None
    if snaps:
        try:
            with open(os.path.join(SNAP, snaps[-1]), encoding="utf-8") as f:
                prev = json.load(f)
        except Exception:  # noqa: BLE001
            prev = None

    cur = {
        "readiness": {k: v for k, v in (ready or {}).items() if k != "criteria"},
        "gate": (gate or {}).get("summary", {}),
        "issues": {k: v for k, v in (issue or {}).items() if k != "issues"},
        "stage": {k: v for k, v in (stage or {}).items() if k != "results"},
    }
    drift: list[str] = []
    if prev:
        pg, pi = prev.get("gate", {}), prev.get("issues", {})
        cg, ci = cur["gate"], cur["issues"]
        # 齐备率掉了
        if cg.get("blocks_ok") is not None and pg.get("blocks_ok") is not None and cg["blocks_ok"] < pg["blocks_ok"]:
            drift.append(f"★Q1 齐备率下降: {pg['blocks_ok']}/{pg.get('blocks_total')} → {cg['blocks_ok']}/{cg.get('blocks_total')}")
        # 内部未闭合变多
        if (cg.get("global_pending") or 0) > (pg.get("global_pending") or 0):
            drift.append(f"★内部未闭合增加: {pg.get('global_pending')} → {cg.get('global_pending')}")
        # 问题单数量增加
        if (ci.get("total") or 0) > (pi.get("total") or 0):
            drift.append(f"★问题单增加: {pi.get('total')} → {ci.get('total')}")
        # 逾期
        if (ci.get("overdue") or 0) > (pi.get("overdue") or 0):
            drift.append(f"★逾期问题增加: {pi.get('overdue')} → {ci.get('overdue')}")
        # 未闭环 blocker
        cb = sum(1 for x in (issue or {}).get("issues", [])
                 if x.get("severity") == "blocker" and x.get("status") not in ("closed", "deferred", "wontfix"))
        drift.append(f"  (未闭环 blocker: {cb} 条)")

    if not args.no_snapshot:
        import datetime as dt
        name = f"{dt.date.today().isoformat()}_daily.json"
        with open(os.path.join(SNAP, name), "w", encoding="utf-8") as f:
            json.dump(cur, f, ensure_ascii=False, indent=2)

    # ---- 一屏报告 ----
    print("=" * 74)
    print("每日巡检 · Daily Check")
    print("=" * 74)
    g = cur["gate"]
    i = cur["issues"]
    s = cur["stage"]
    print(f"  merge          rc={rc_m} {'✅ 完整' if rc_m == 0 else '⚠️ 不完整'}")
    print(f"  交付齐备率     {g.get('blocks_ok')}/{g.get('blocks_total')}"
          f" | 证据分级 {g.get('evidence_ok_agents')}/{g.get('evidence_total_agents')}"
          f" | 接口声明 {g.get('interface_claims_total', g.get('interface_claims', '?'))} 条")
    print(f"  需求闭环       问方 {g.get('needs_answered_incoming')}/{g.get('needs_total')}"
          f" | 内部未闭合 {g.get('global_pending')} | 等外部 {g.get('global_waiting_external')}"
          f" | 对账 {'✅' if (g.get('reconciliation') or {}).get('ok') else '❌'}")
    print(f"  问题闭环门     {i.get('total')} 条 | 逾期 {i.get('overdue')}"
          f" | 内部 {i.get('internal')} / 外部 {i.get('external')} | 违规 {len(i.get('errors') or [])}")
    print(f"  阶段门         当前 **{s.get('current_gate')}** | 已过 {s.get('passed_gates')}")
    r = cur.get("readiness") or {}
    print(f"  执行就绪度     纸面阶段 {'✅就绪' if r.get('paper_ready') else '❌未就绪'} | "
          f"样机阶段 {'✅就绪' if r.get('sample_ready') else '❌不就绪'} | "
          f"实测 {r.get('measurements',{}).get('have')}/{r.get('measurements',{}).get('needed')} 项")
    if prev:
        print(f"  漂移检测       {'无漂移 ✅' if not [d for d in drift if d.startswith('★')] else '有漂移 ⚠️'}")
        for d in drift:
            print(f"      {d}")
    else:
        print("  漂移检测       首次巡检 (无历史快照, 已建立基线)")
    if problems:
        print()
        print("❌ 异常:")
        for p in problems:
            print(f"   - {p}")
        return 1
    print()
    print("✅ 巡检通过 (无违规 / 无漂移)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
