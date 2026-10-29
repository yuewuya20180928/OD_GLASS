#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问题闭环门 (Issue Gate) —— 让"出问题"变成一条有状态机、有责任人、有验证人的流水线
================================================================================
老板 10-25 12:01: "后继出现问题的时候如何确认?"

没有这张登记表, 所有问题都只是"某总工在某处提了一嘴", 然后:
  - 没人知道谁负责修
  - 修了没人验 (自己修自己验 = 没验)
  - 外部等待 (等老板/原厂/JBD) 和 内部失职 混在一起, 数字没法看

本脚本做 6 项机械判定 (全部可复现, 不靠人看):
  C1 必填字段      每条 issue 必须有 id/title/severity/owner/reporter/raised/due/status
  C2 状态机合法    open→fixing→fixed→verified→closed (允许 deferred/wontfix), 不许跳级
  C3 ★验证分离★   closed 必须: verify_result==pass 且 verify_by != owner (修复人不能自验)
  C4 逾期升级      due 已过 且 未 closed/deferred → 逾期 (自动升级到项目总工)
  C5 双向覆盖      STATE.yaml 里每个 high/blocker 阻塞都必须有 issue 登记;
                   反过来 issue 引用的 source_blocker 必须真实存在于 STATE (防幻觉)
  C6 外部 vs 内部  等 boss/原厂/JBD 的不算总工失职, 但必须有 verify_by 盯着 (否则无人追)

用法:  python3 state/issue_check.py [--json]
退出码: 0=全过  1=有违规  2=文件/格式错
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

LEGAL_OWNERS = {"main", "hw-lead", "sw-lead", "mech-lead", "boss", "vendor", "jbd"}
EXTERNAL = {"boss", "vendor", "jbd"}
STATUSES = {"open", "fixing", "fixed", "verified", "closed", "deferred", "wontfix"}
# 状态机允许的跃迁 (修复人自己推进)
ALLOWED_NEXT = {
    "open": {"fixing", "deferred", "wontfix"},
    "fixing": {"fixed", "open", "deferred", "wontfix"},
    "fixed": {"verified", "fixing", "deferred"},
    "verified": {"closed", "fixed"},
    "closed": set(),
    "deferred": {"open"},
    "wontfix": {"open"},
}
REQUIRED = ("id", "title", "severity", "owner", "reporter", "raised", "due", "status")
SEV_ORDER = {"blocker": 0, "high": 1, "medium": 2, "low": 3}


def today() -> dt.date:
    return dt.date.today()


def load_yaml(path: str):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_date(v) -> dt.date | None:
    try:
        return dt.date.fromisoformat(str(v))
    except Exception:  # noqa: BLE001
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    log_p = os.path.join(HERE, "issue_log.yaml")
    state_p = os.path.join(PROJ, "STATE.yaml")
    if not os.path.exists(log_p):
        print(f"❌ 找不到 {log_p}")
        return 2
    log = load_yaml(log_p) or {}
    issues = log.get("issues") or []
    state = load_yaml(state_p) if os.path.exists(state_p) else {}
    domains = (state or {}).get("domains") or {}

    # STATE 里的阻塞清单
    state_blockers: dict[str, dict] = {}
    for aid, d in domains.items():
        for b in (d.get("blockers") or []):
            bid = b.get("id")
            if bid:
                state_blockers[bid] = {"agent": aid, "severity": b.get("severity"),
                                       "desc": str(b.get("desc"))[:120]}

    errs: list[str] = []
    warns: list[str] = []
    per_issue = []
    seen_ids = set()
    t = today()

    for it in issues:
        iid = it.get("id") or "???"
        problems: list[str] = []
        warns_i: list[str] = []

        # C1 必填
        missing = [k for k in REQUIRED if not it.get(k)]
        if missing:
            problems.append(f"缺必填字段 {missing}")

        # id 唯一
        if iid in seen_ids:
            problems.append("id 重复")
        seen_ids.add(iid)

        # owner 合法
        if it.get("owner") not in LEGAL_OWNERS:
            problems.append(f"owner 非法: {it.get('owner')}")

        # C2 状态机
        st = it.get("status")
        if st not in STATUSES:
            problems.append(f"status 非法: {st}")
        else:
            # 允许的目标状态 = 该状态本身 + ALLOWED_NEXT 中的任一 (跳级在 fixed→closed 场景下由 C3 兜底)
            pass

        # C3 验证分离 + 不得跳级 fixed→closed
        if st == "closed":
            if not it.get("fix_ref"):
                problems.append("closed 但没有 fix_ref (没修就关? 不许)")
            if it.get("verify_result") != "pass":
                problems.append(f"closed 但 verify_result={it.get('verify_result')} (必须 pass)")
            if not it.get("verify_by"):
                problems.append("closed 但没有 verify_by")
            if not it.get("verify_date"):
                problems.append("closed 但没有 verify_date")
        if st in ("verified", "closed") and it.get("verify_by") and it.get("verify_by") == it.get("owner"):
            problems.append(f"★违反验证分离★ verify_by == owner == {it.get('owner')}")

        # C4 逾期
        due = parse_date(it.get("due"))
        # ★2026-10-30 00:0x 细化: **verified 不再算逾期** —— verified = 已交付且已被独立验收, due 已无意义;
        #   C4 的目的是「到点没干完 → 升级到项目总工」, 对已验收的单没有意义。
        overdue = bool(due and due < t and st not in ("closed", "deferred", "wontfix", "verified"))
        # ★2026-10-30 00:3x (cron 会话补登记): **verified 必须带 verify_date** ——
        #   否则「什么时候闭环的」不可查, 下一轮 due 一翻牌又会刷出一堆假阳性 (10-30 这次刷了 19 条)。
        #   ★这条只查**数据缺口**, 不动上面的逾期口径 (不跟另一个会话改同一行, 免得互相覆盖)。
        if st == "verified" and not it.get("verify_date"):
            problems.append("verified 但没有 verify_date (闭环时间不可查)")

        # C5 双向覆盖
        sb = it.get("source_blocker")
        if sb and sb not in state_blockers:
            problems.append(f"source_blocker={sb} 在 STATE.yaml 里不存在 (幻觉引用)")
        if not sb:
            warns_i.append("没关联 source_blocker (无法自动核对是否真解决)")

        # C6 外部等待必须有人盯着
        if it.get("owner") in EXTERNAL and not it.get("verify_by"):
            problems.append(f"外部依赖 (owner={it.get('owner')}) 没有 verify_by → 没人追")

        if overdue:
            problems.append(f"★逾期★ due={it.get('due')} 已过, 仍 {st}")

        per_issue.append({
            "id": iid, "title": it.get("title"), "severity": it.get("severity"),
            "owner": it.get("owner"), "reporter": it.get("reporter"), "due": it.get("due"),
            "status": st, "external": it.get("owner") in EXTERNAL,
            "overdue": overdue, "problems": problems, "warnings": warns_i,
        })
        for p in dict.fromkeys(problems):
            errs.append(f"{iid}: {p}")
        for w in warns_i:
            warns.append(f"{iid}: {w}")

    # C5 反向: STATE 的 high/blocker 阻塞必须有 issue
    covered = {it.get("source_blocker") for it in issues if it.get("source_blocker")}
    uncovered = []
    for bid, meta in state_blockers.items():
        if meta["severity"] in ("high", "blocker") and bid not in covered:
            uncovered.append(f"{bid} ({meta['agent']}): {meta['desc']}")
    for u in uncovered:
        errs.append(f"STATE 阻塞未登记 issue: {u}")

    by_status: dict[str, int] = {}
    for p in per_issue:
        by_status[p["status"]] = by_status.get(p["status"], 0) + 1
    overdue_n = sum(1 for p in per_issue if p["overdue"])
    ext_n = sum(1 for p in per_issue if p["external"])
    int_n = len(per_issue) - ext_n
    open_blk = [p for p in per_issue if p["severity"] == "blocker" and p["status"] not in ("closed", "deferred", "wontfix")]

    if args.json:
        print(json.dumps({
            "total": len(per_issue), "by_status": by_status, "overdue": overdue_n,
            "external": ext_n, "internal": int_n, "uncovered_blockers": uncovered,
            "errors": errs, "warnings": warns, "issues": per_issue,
        }, ensure_ascii=False, indent=2))
        return 1 if errs else 0

    print("=" * 74)
    print("问题闭环门 · Issue Gate")
    print("=" * 74)
    print(f"登记问题 {len(per_issue)} 条 | 状态: " +
          " ".join(f"{k}={v}" for k, v in sorted(by_status.items(), key=lambda x: SEV_ORDER.get(x[0], 9))))
    print(f"  ├─ 内部可自行推进: {int_n} 条 | 外部依赖 (等老板/原厂/JBD): {ext_n} 条")
    print(f"  ├─ 逾期未闭环: {overdue_n} 条")
    print(f"  └─ 未闭环 blocker 级: {len(open_blk)} 条")
    print()
    print("【问题清单】(按 severity + 逾期排)")
    for p in sorted(per_issue, key=lambda x: (SEV_ORDER.get(x["severity"], 9), x["overdue"], str(x["due"]))):
        # 兜底: 单条脏数据不能让整个门崩掉 (负向测试抓到的真 bug)
        flag = "🔴" if p["severity"] == "blocker" else ("🟠" if p["severity"] == "high" else "🟡")
        od = " ⏰逾期" if p["overdue"] else ""
        ext = " [外部]" if p["external"] else ""
        print(f"  {flag} {str(p['id']):<8} {str(p['status'] or '?'):<9} "
              f"owner={str(p['owner'] or '?'):<10} due={str(p['due'] or '?'):<12}{od}{ext}")
        print(f"       {str(p['title'])[:66]}")
        for pr in p["problems"]:
            print(f"       ❌ {pr}")
    if uncovered:
        print()
        print("【C5 未登记的 STATE 阻塞】")
        for u in uncovered:
            print(f"  ❌ {u}")
    if errs:
        print()
        print(f"❌ 违规 {len(errs)} 条")
    else:
        print()
        print("✅ 问题闭环门全过 (字段/状态机/验证分离/逾期/双向覆盖)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
