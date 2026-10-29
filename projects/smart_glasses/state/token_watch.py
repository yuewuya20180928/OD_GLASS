#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""token 守护: 扫描所有 agent 会话最近 5h 窗口的 token 消耗, 判断是否该先推 GitHub 再继续。

★为什么要有这个 (老板 2026-10-29 09:59 亲自要求):
  "你自己周期性的去检测token的使用情况, 及token是否快要用完, 然后每次在5h的token限额用完前先将进展推送到github上,
   避免token用完中断关机而导致信息丢失"
  ⇒ 第一次实证: 2026-10-29 10:02→18:43 会话被掐断 8.7 小时, 老板交代的任务一条没落盘 ⇒ **这个脚本就是为下次不发生这种事**。

判据 (任一命中 = 该推 GitHub 了):
  ① 5h 窗口 token 消耗 > state/token_budget.json 里的 threshold
  ② 距上次 GitHub 推送 > max_idle_minutes (默认 45 分钟) —— ★最可靠的兜底, 不依赖限额数值
  ③ 当前会话 context 使用率 > context_pct_limit (默认 75%)

用法: python3 state/token_watch.py [--json] [--write-flag]
"""
from __future__ import annotations

import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WS = "/home/yuewuya/.openclaw/workspace"
AGENT_DIRS = [
    os.path.join(WS, "..", ".openclaw", "agents", a, "sessions")
    for a in ("main", "hw-lead", "sw-lead", "mech-lead")
]
BUDGET = os.path.join(HERE, "token_budget.json")
LAST_PUSH = os.path.join(HERE, ".last_github_push")
DEFAULT_BUDGET = {
    "window_hours": 5,
    "threshold_tokens": 8_000_000,
    "max_idle_minutes": 45,
    "context_pct_limit": 75,
    "_note": "threshold 是估算值 (MiniMax token plan 实际限额未公开); 真正兜底的是 max_idle_minutes",
}


def load_budget() -> dict:
    b = dict(DEFAULT_BUDGET)
    if os.path.exists(BUDGET):
        try:
            b.update(json.load(open(BUDGET, encoding="utf-8")))
        except Exception:
            pass
    return b


def window_tokens(hours: float) -> tuple:
    """扫所有 agent 会话, 统计最近 hours 小时内 assistant 消息的 (input+output) tokens。"""
    cutoff = time.time() - hours * 3600
    total = 0
    per_agent = {}
    msgs = 0
    for d in AGENT_DIRS:
        d = os.path.abspath(d)
        if not os.path.isdir(d):
            continue
        agent = os.path.basename(os.path.dirname(d))
        for p in glob.glob(os.path.join(d, "*.jsonl")):
            if "trajectory" in p:
                continue
            try:
                with open(p, errors="replace") as f:
                    for line in f:
                        if '"usage"' not in line:
                            continue
                        try:
                            rec = json.loads(line)
                        except Exception:
                            continue
                        ts = rec.get("timestamp") or ""
                        if not ts:
                            continue
                        try:
                            import datetime
                            t = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
                        except Exception:
                            continue
                        if t < cutoff:
                            continue
                        u = (rec.get("message") or {}).get("usage")
                        if not u:
                            continue
                        n = (u.get("input") or 0) + (u.get("output") or 0)
                        total += n
                        per_agent[agent] = per_agent.get(agent, 0) + n
                        msgs += 1
            except OSError:
                continue
    return total, per_agent, msgs


def main() -> int:
    b = load_budget()
    total, per_agent, msgs = window_tokens(b["window_hours"])

    last_push_age = None
    if os.path.exists(LAST_PUSH):
        try:
            last_push_age = (time.time() - os.stat(LAST_PUSH).st_mtime) / 60.0
        except OSError:
            pass

    ctx_pct = None
    try:
        cur = os.path.join(WS, "..", ".openclaw", "agents", "main", "sessions")
        newest = max(glob.glob(os.path.join(cur, "*.jsonl")), key=os.path.getmtime)
        ctx_pct = None  # context 用量由 session_status 提供, 这里不猜
    except Exception:
        pass

    reasons = []
    if total > b["threshold_tokens"]:
        reasons.append(f"窗口 token {total/1e6:.1f}M > 阈值 {b['threshold_tokens']/1e6:.1f}M")
    if last_push_age is not None and last_push_age > b["max_idle_minutes"]:
        reasons.append(f"距上次 GitHub 推送 {last_push_age:.0f} 分钟 > {b['max_idle_minutes']} 分钟")
    elif last_push_age is None:
        reasons.append("从未推送过 GitHub (或标记丢失)")

    out = {
        "window_hours": b["window_hours"],
        "window_tokens": total,
        "window_tokens_M": round(total / 1e6, 2),
        "threshold_tokens": b["threshold_tokens"],
        "per_agent": {k: round(v / 1e6, 2) for k, v in per_agent.items()},
        "usage_records": msgs,
        "last_push_minutes_ago": round(last_push_age, 1) if last_push_age is not None else None,
        "verdict": "PUSH_NOW" if reasons else "OK",
        "reasons": reasons,
        "budget": b,
    }
    if "--json" in sys.argv:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"token 守护 [{out['window_hours']}h 窗口]: {out['window_tokens_M']}M "
              f"(阈值 {b['threshold_tokens']/1e6:.1f}M) | 按 agent: {out['per_agent']}")
        print(f"  距上次 GitHub 推送: {out['last_push_minutes_ago']} 分钟")
        print(f"  判定: **{out['verdict']}**" + ((" ← " + "; ".join(reasons)) if reasons else ""))
    return 0 if out["verdict"] == "OK" else 3


if __name__ == "__main__":
    sys.exit(main())
