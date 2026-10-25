#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推进器 (Advance) —— 把"后继计划"变成可以执行的动作清单
================================================================================
老板 10-25 12:12: "除了实现 当前进展/待办/卡点, 还要能够实现 继续执行后继计划或步骤的功能"

status.py 回答"现在什么样"; 本脚本回答"**那我现在该干什么**", 并且:
  - 按"能不能真的动"给动作排序 (内部可动 > 老板一键 > 纯等待)
  - 每个动作都带**可直接下发的任务书** (目标/输出文件/写入范围/验收标准/边界/自证命令)
  - 对外动作 (邮件/询价) **只起草不发送** —— 外发必须老板批, 草稿落到 state/outbox/
  - --apply 会: 生成草稿 + 把已派 issue 标 fixing + 写 dispatch_log (可追溯)

用法:
  python3 state/advance.py            # 看下一步计划 (只读, 不改任何东西)
  python3 state/advance.py --json     # 机读
  python3 state/advance.py --apply    # 落盘: 生成草稿 + 标记已派 + 写派活日志
退出码: 0=有可执行动作  1=无可执行动作(全在等)  2=文件错
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
OUTBOX = os.path.join(HERE, "outbox")
AGENT_ROLE = {"hw-lead": "硬件总工", "sw-lead": "软件总工", "mech-lead": "结构总工"}


def load_yaml(path: str):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only", help="逗号分隔的 issue id; 只标这些为 fixing (不指定=全部 internal)")
    args = ap.parse_args()

    log = load_yaml(os.path.join(HERE, "issue_log.yaml")) or {}
    issues = log.get("issues") or []
    t = dt.date.today()

    def days_to(due):
        try:
            return (dt.date.fromisoformat(str(due)) - t).days
        except Exception:  # noqa: BLE001
            return None

    # ---------- A. 内部可立即推进 (owner 是三个总工) ----------
    internal = []
    for it in issues:
        if it.get("owner") not in AGENT_ROLE:
            continue
        if it.get("status") in ("closed", "deferred", "wontfix"):
            continue
        dd = days_to(it.get("due"))
        internal.append({
            "issue": it.get("id"), "title": it.get("title"), "agent": it.get("owner"),
            "role": AGENT_ROLE[it.get("owner")], "due": it.get("due"),
            "days_left": dd, "severity": it.get("severity"),
            "brief": it.get("task_brief") or f"闭环 {it.get('id')}: {it.get('title')}",
            "source": it.get("source_blocker"),
            "_raw": it,
        })

    # ---------- B. 需老板一个"是/否"就能动的动作 ----------
    # 这些动作的共同点: 准备成本在我这边, 只差老板点头就能发出去
    approvals = []
    by_draft: dict[str, dict] = {}
    for it in issues:
        if it.get("status") in ("closed", "deferred", "wontfix"):
            continue
        dr = it.get("email_draft")
        if not dr:
            continue
        slot = by_draft.setdefault(dr, {"kind": "email", "draft": dr, "issues": [],
                                        "to": "", "note": "", "owner": it.get("owner")})
        slot["issues"].append(it.get("id"))
    TO = {"vendor_round2_email.md": ("酷芯微 (info@artosyn.cn)",
                                     "第二轮原厂问询 —— 一封信解决 9 条 vendor issue (显示TX/pitch/启动存储/电源域/NPU口径/借板实测)"),
          "jbd_query.md": ("JBD (走鹃Ⅱ / 波导)",
                           "JBD 问询 —— 波导 2D 外形图 / 一拖二模组 / 走鹃Ⅱ 尺寸 + 彩虹纹指标"),
          "bridge_chip_rfq.md": ("桥接芯片供应商 (待老板指定)",
                                 "并行询价 —— 不等原厂回信, 抢 4-8 周采购周期")}
    for dr, slot in by_draft.items():
        to, note = TO.get(dr, ("待老板指定", ""))
        slot["to"], slot["note"] = to, note
        approvals.append(slot)
    # 老板拍板项
    pm = load_yaml(os.path.join(HERE, "fragments", "pm.yaml")) or {}
    ans_keys = {a.get("key") for a in (pm.get("answers") or [])}
    decisions = []
    for n in (pm.get("needs_from") or []):
        if n.get("waiting_on") == "boss" and n.get("key") not in ans_keys:
            dd = days_to(n.get("due"))
            decisions.append({"key": n.get("key"), "item": str(n.get("item"))[:90],
                              "due": n.get("due"), "days_left": dd,
                              "urgency": "已逾期" if (dd is not None and dd < 0)
                                         else (f"剩{dd}天" if dd is not None and dd <= 2 else "")})

    # ---------- C. 纯等待 (不动作, 只监控) ----------
    waiting = []
    for it in issues:
        if it.get("owner") not in ("vendor", "jbd"):
            continue
        if it.get("status") in ("closed", "deferred", "wontfix"):
            continue
        if it.get("email_draft"):
            continue          # 已归入 B (待发), 不重复列
        dd = days_to(it.get("due"))
        waiting.append({"issue": it.get("id"), "owner": it.get("owner"),
                        "title": it.get("title"), "due": it.get("due"),
                        "days_left": dd, "severity": it.get("severity")})

    plan = {"internal": internal, "approvals": approvals, "decisions": decisions, "waiting": waiting}

    # ---------- apply: 落盘 ----------
    applied = []
    if args.apply:
        os.makedirs(OUTBOX, exist_ok=True)
        for ap_ in approvals:
            draft = ap_.get("draft")
            if not draft:
                continue
            fn = draft if draft.endswith(".md") else f"{draft}.md"
            if os.path.exists(os.path.join(OUTBOX, fn)):
                continue
            path = os.path.join(OUTBOX, fn)
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"# 待发草稿 · {ap_['to']} · 关联 {ap_['issue']}\n\n"
                            f"> ⚠️ 本文件是**草稿**, 未经老板批准不得发送。\n\n")
                applied.append(path)
        # 派过的 issue 标 fixing
        dl_p = os.path.join(HERE, "dispatch_log.yaml")
        dl = load_yaml(dl_p) if os.path.exists(dl_p) else {"dispatches": []}
        only = set(x.strip() for x in (args.only or "").split(",") if x.strip())
        for a in internal:
            raw = a.get("_raw") or {}
            if only and raw.get("id") not in only:
                continue
            if raw.get("status") == "open" and a.get("brief"):
                raw["status"] = "fixing"
                raw["dispatched_at"] = dt.date.today().isoformat()
                dl.setdefault("dispatches", []).append({
                    "issue": raw.get("id"), "agent": raw.get("owner"),
                    "at": dt.date.today().isoformat(), "brief": a["brief"][:300]})
                applied.append(f"ISS {raw.get('id')} → {raw.get('owner')} 标 fixing + 写派活日志")
        with open(dl_p, "w", encoding="utf-8") as f:
            yaml.safe_dump(dl, f, allow_unicode=True, sort_keys=False, width=200)
        if applied:
            with open(os.path.join(HERE, "issue_log.yaml"), "w", encoding="utf-8") as f:
                yaml.safe_dump(log, f, allow_unicode=True, sort_keys=False, width=200)

    if args.json:
        print(json.dumps({**plan, "applied": applied}, ensure_ascii=False, indent=2))
        return 0 if (internal or approvals) else 1

    # ---------- 人读输出 ----------
    print("=" * 78)
    print(f"  推进计划 (下一批可执行动作)      {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 78)

    print(f"\n【A】内部可立即推进 — 派给三个总工 ({len(internal)} 条)")
    if not internal:
        print("      (无)")
    for a in internal:
        dl = a.get("days_left")
        if dl is None:
            u = ""
        elif dl < 0:
            u = f"  [逾期{-dl}天]"
        elif dl <= 2:
            u = f"  [剩{dl}天]"
        else:
            u = ""
        print(f"  ▸ {a['issue']} → {a['agent']} ({a['role']})  due {a['due']}{u}")
        for line in str(a["brief"]).splitlines():
            if line.strip():
                print(f"      {line}")

    print(f"\n【B】只差老板一个「是/否」就能动 — 外发草稿已就绪 ({len(approvals)} 条)")
    if not approvals:
        print("      (无)")
    for a in approvals:
        print(f"  ▸ 收件人: {a['to']}")
        print(f"      {a['note']}")
        print(f"      草稿已就绪: state/outbox/{a['draft']}  (覆盖 {len(a['issues'])} 条 issue: "
              + ", ".join(a["issues"]) + ")")
        print(f"      ★只差老板一句「可以发」——外发一律经老板, 子 agent 不得直接联系供应商")

    print(f"\n【C】等你拍板的口径 ({len(decisions)} 条)")
    for d in decisions:
        u = f"  ← {d['urgency']}" if d["urgency"] else ""
        print(f"  ▸ {d['key']:<22} due {d['due']}{u}")
        print(f"      {d['item']}")

    n_pending = sum(1 for it in issues if it.get("owner") in ("vendor", "jbd")
                     and it.get("status") not in ("closed", "deferred", "wontfix"))
    print(f"\n【D】纯等待 (不动作, 到期自动升级) ({len(waiting)} 条)"
          + (f"  —— 另外 {n_pending} 条外部 issue 已在 B 备好草稿, 草稿没被批准前状态不变" if n_pending else ""))
    for w in waiting:
        dd = w.get("days_left")
        u = f"逾期{-dd}天" if (dd is not None and dd < 0) else (f"剩{dd}天" if dd is not None else "")
        print(f"  ▸ {w['issue']} [{w['owner']}] {w['title'][:48]} (due {w['due']} {u})")

    if applied:
        print(f"\n已落盘 ({len(applied)}):")
        for a in applied:
            print(f"   - {a}")
    print()
    print("  手动执行:  python3 state/advance.py --apply   (生成草稿 + 标记已派)")
    print("  完整看板:  ./status.sh")
    print("=" * 78)
    return 0 if (internal or approvals) else 1


if __name__ == "__main__":
    sys.exit(main())
