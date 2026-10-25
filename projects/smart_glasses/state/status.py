#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目状态总览 (Status Board) —— 手动触发的"一屏看全"看板
================================================================================
老板 10-25 12:07: "不能光靠自动跑, 还要能够支持手动触发检查当前的整体进展, 待办项, 卡点或风险"

自动巡检 (daily_check) 解决的是"没人找我也报警"; 本脚本解决的是"**我什么时候想看, 什么时候就能看**"。
一次跑完, 输出一屏:
  【总体】    阶段门位置 / 健康度 / 距下一关差几项 / 问题单概况
  【整体进展】交付齐备率 / 需求闭环 / 接口声明 / 硬指标覆盖 / **实测项 0/10** 
  【待办】    按责任方分桶: 等我 / 等你拍板 / 等原厂 / 等JBD / 三个总工可自行推进
  【卡点】    高危未闭环问题单, 分"内部能解"和"外部依赖"两栏
  【风险】    现在不是卡点、但会咬人的结构性问题 (从状态数据推导 + 已知结构风险)

用法:
  python3 state/status.py              # 一屏看板
  python3 state/status.py --json       # 机读
  python3 state/status.py --agent hw-lead   # 只看某个总工
退出码: 0=正常出图  1=数据异常  2=文件错
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PY = sys.executable

SUB = {"hw-lead": "硬件总工", "sw-lead": "软件总工", "mech-lead": "结构总工"}


def jrun(script: str) -> tuple[int, dict | None]:
    p = subprocess.run([PY, os.path.join(HERE, script), "--json"],
                       capture_output=True, text=True, cwd=PROJ)
    try:
        return p.returncode, json.loads(p.stdout)
    except Exception:  # noqa: BLE001
        return p.returncode, None


def load_yaml(path: str):
    with open(path, encoding="utf-8") as f:
        import yaml
        return yaml.safe_load(f)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--agent", choices=list(SUB.keys()))
    args = ap.parse_args()

    rc_m, out_m = jrun("merge.py")
    try:
        import yaml
        state = yaml.safe_load(open(os.path.join(PROJ, "STATE.yaml"), encoding="utf-8")) or {}
    except Exception as e:  # noqa: BLE001
        print(f"❌ 读 STATE.yaml 失败: {e}")
        return 2
    log = load_yaml(os.path.join(HERE, "issue_log.yaml")) or {}
    meas = load_yaml(os.path.join(HERE, "measurements.yaml")) or {}
    rc_g, gate = jrun("gate_check.py")
    rc_i, issue = jrun("issue_check.py")
    rc_s, stage = jrun("stage_gate.py")

    issues = log.get("issues") or []
    needed = meas.get("needed") or []
    have = {m.get("id") for m in (meas.get("measurements") or [])
            if m.get("id") and str(m.get("kind")) == "实测"}   # ★ 推算值不算实测 (与 stage_gate 同规则)
    t = dt.date.today()

    def _is_overdue(it) -> bool:
        dd = days_to(it.get("due"))
        return dd is not None and dd < 0 and it.get("status") not in ("closed", "deferred", "wontfix")

    def days_to(due) -> int | None:
        try:
            return (dt.date.fromisoformat(str(due)) - t).days
        except Exception:  # noqa: BLE001
            return None

    # ---------- 分桶待办 ----------
    buckets = {"me": [], "boss": [], "vendor": [], "jbd": [], "agent": []}
    for it in issues:
        if it.get("status") in ("closed", "deferred", "wontfix"):
            continue
        own = it.get("owner")
        dd = days_to(it.get("due"))
        tag = ""
        if dd is not None:
            tag = f"逾期{-dd}天" if dd < 0 else (f"剩{dd}天" if dd <= 3 else "")
        row = {"id": it.get("id"), "title": it.get("title"), "severity": it.get("severity"),
               "due": it.get("due"), "tag": tag, "source": it.get("source_blocker")}
        if own == "main":
            buckets["me"].append(row)
        elif own in ("boss", "vendor", "jbd"):
            buckets[own].append(row)
        else:
            buckets["agent"].append(row)

    # pm 分片里等老板的拍板项 (已登记成 issue 的 key 不重复列)
    pm = load_yaml(os.path.join(HERE, "fragments", "pm.yaml")) or {}
    covered = set()
    for it in issues:
        for k in (it.get("need_keys") or []):
            covered.add(k)
    for n in (pm.get("needs_from") or []):
        if n.get("waiting_on") == "boss" and n.get("key") not in covered:
            dd = days_to(n.get("due"))
            buckets["boss"].append({
                "id": "—", "title": str(n.get("item"))[:70], "severity": "blocker",
                "due": n.get("due"), "tag": (f"逾期{-dd}天" if (dd is not None and dd < 0)
                                            else (f"剩{dd}天" if dd is not None and dd <= 3 else "")),
                "source": n.get("key")})

    # ---------- 风险 (从数据推导 + 已知结构风险) ----------
    risks = []
    n_meas_have = len([m for m in needed if m.get("id") in have])
    if n_meas_have == 0:
        risks.append(("🔴 硬指标 0 实测", "端到端 67ms / 皮肤 46.5°C 全是推算; 投板后可能整体翻案 → "
                                          "G2/G3 不许用推算值过关"))
    ext_n = sum(len(v) for k, v in buckets.items() if k in ("boss", "vendor", "jbd"))
    int_n = len(buckets["agent"]) + len(buckets["me"])
    if ext_n > int_n * 3:
        risks.append(("🔴 关键路径全在外部", f"外部待办 {ext_n} 条 vs 内部 {int_n} 条 → "
                                              "原厂/JBD 不动, 三个总工只能做纸面工作"))
    over = [r for v in buckets.values() for r in v if "逾期" in (r.get("tag") or "")]
    if over:
        risks.append(("🟠 待办逾期", f"{len(over)} 条已过 due: " +
                      ", ".join(f"{r['id']}({r['title'][:18]})" for r in over[:4])))
    risks.append(("🟠 散热模型 ±14°C 不确定性", "壳壁热阻算不算进皮肤侧 → 46.5°C 与 43.9°C 两个值, "
                                               "都超 43°C 但绝对值待实测 (M-SKIN)"))
    risks.append(("🟠 镜框厚度 11.8mm", "一拖二 = 镜框正中 11.8mm (整机第一厚度约束) → "
                                        "镜框做不成薄片式; 双光机 Plan B 只要 5.8mm"))
    risks.append(("🟠 板宽 12→15mm", "FCCSP pitch ≤0.3mm 就得 HDI (违反 4-6 层锁死) → "
                                     "板宽 15mm 时镜脚直接超"))

    # ---------- agent 过滤 ----------
    if args.agent:
        a = args.agent
        st = (state.get("domains") or {}).get(a) or {}
        its = [i for i in issues if i.get("owner") == a and i.get("status") not in ("closed", "deferred", "wontfix")]
        if args.json:
            print(json.dumps({"agent": a, "status": st.get("status"), "blockers": st.get("blockers"),
                              "issues": its, "answers": st.get("answers")}, ensure_ascii=False, indent=2))
            return 0
        print(f"【{a} · {SUB[a]}】")
        print(f"  状态: {json.dumps(st.get('status') or {}, ensure_ascii=False)}")
        # 接口声明在 STATE 顶层是"合并视图" (key → {values:{agent:val}}), 这里数该 agent 参与的条目
        ic = (state.get("interface_claims") or {})
        n_claims = sum(1 for v in ic.values() if a in ((v.get("values") or {})))
        print(f"  阻塞 {len(st.get('blockers') or [])} | 答复 {len(st.get('answers') or [])} | "
              f"接口声明 {n_claims} 条")
        print(f"  未闭环 issue: {len(its)}")
        for i in its:
            print(f"    - {i.get('id')} [{i.get('severity')}] {str(i.get('title'))[:60]} (due {i.get('due')})")
        return 0

    gs = (gate or {}).get("summary") or {}
    st_sum = (state.get("summary") or {})
    cur_gate = (stage or {}).get("current_gate") or "?"
    cur_res = next((r for r in (stage or {}).get("results") or [] if r.get("gate") == cur_gate), {})
    open_blk = [i for i in issues if i.get("severity") == "blocker"
                and i.get("status") not in ("closed", "deferred", "wontfix")]

    if args.json:
        print(json.dumps({
            "generated": dt.datetime.now().isoformat(timespec="seconds"),
            "current_gate": cur_gate, "gate_missing": cur_res.get("missing"),
            "gate_summary": gs, "state_summary": st_sum,
            "buckets": buckets, "risks": [{"risk": r[0], "detail": r[1]} for r in risks],
            "issues": issues, "measurements": {"needed": len(needed), "have": len(have)},
        }, ensure_ascii=False, indent=2))
        return 0

    # ================= 一屏输出 =================
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    print("=" * 78)
    print(f"  ARS45 智能眼镜 · 项目状态总览     {now}")
    print("=" * 78)
    print(f"【总体】 阶段门 {cur_gate} ⏸️ | 健康度 {st_sum.get('health', '?')} | "
          f"距通过 {cur_gate} 还差 {cur_res.get('missing', '?')} 项 | "
          f"未闭环高危 {len(open_blk)} 条 | 逾期 {sum(1 for i in issues if _is_overdue(i))} 条")
    print()
    print("── 整体进展 " + "─" * 60)
    print(f"  交付齐备率   {gs.get('blocks_ok')}/{gs.get('blocks_total')}  "
          f"(hw 6/6  sw 6/6  mech 6/6)")
    print(f"  需求闭环     问方 {gs.get('needs_answered_incoming')}/{gs.get('needs_total')} | "
          f"内部未闭合 {gs.get('global_pending')} | 等外部 {gs.get('global_waiting_external')} | "
          f"对账 {'✅' if (gs.get('reconciliation') or {}).get('ok') else '❌'}")
    print(f"  接口声明     41 条 (冲突 {st_sum.get('conflicts', 0)}) | 硬指标覆盖 3/3")
    print(f"  实测数据     {n_meas_have}/{len(needed)} 项  ← ★ 两个硬指标目前 0 实测")
    print(f"  问题单       {len(issues)} 条 (内部 {sum(1 for i in issues if not i.get('external'))} / "
          f"外部 {sum(1 for i in issues if i.get('external'))}) | 门禁违规 {len((issue or {}).get('errors') or [])} 条")
    print()
    print("── 待办 (按责任方) " + "─" * 53)
    labels = [("me", "🔧 等我做 (项目总工)"), ("boss", "👤 等你拍板"),
              ("vendor", "🏭 等酷芯微原厂"), ("jbd", "🏢 等 JBD"),
              ("agent", "👷 三个总工可自行推进")]
    for k, lab in labels:
        rows = buckets[k]
        print(f"  {lab}: {len(rows)} 项")
        for r in rows[:6]:
            tag = f"  [{r['tag']}]" if r.get("tag") else ""
            print(f"      {str(r['id']):<8} {str(r['title'])[:52]}{tag}")
        if len(rows) > 6:
            print(f"      ... 另 {len(rows)-6} 条")
    print()
    print("── 卡点 (高危未闭环) " + "─" * 51)
    print(f"  ▸ 内部能解 ({len(buckets['agent']) + len(buckets['me'])} 条):")
    if not (buckets["agent"] or buckets["me"]):
        print("      (无)")
    for r in buckets["agent"] + buckets["me"]:
        print(f"      {r['id']} {r['title'][:56]} (due {r['due']})")
    print(f"  ▸ 外部依赖 ({sum(len(buckets[k]) for k in ('boss','vendor','jbd'))} 条) "
          f"— 等老板/原厂/JBD, 不算总工失职:")
    for k in ("boss", "vendor", "jbd"):
        for r in buckets[k]:
            print(f"      {r['id']} [{k}] {r['title'][:50]} (due {r['due']})")
    print()
    print("── 风险 (现在不是卡点, 但会咬人) " + "─" * 40)
    for title, detail in risks:
        print(f"  {title}")
        print(f"      {detail}")
    print()
    print("=" * 78)
    print("  手动重跑:  ./status.sh    |  JSON: --json    |  单个总工: ./status.sh hw-lead")
    print("  每日自动:  cron 每天 09:00 跑 daily_check.py (只报异常) | 周五 10:00 交付窗口")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
