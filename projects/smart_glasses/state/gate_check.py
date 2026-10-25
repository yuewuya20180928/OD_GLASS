#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目总工质量门 (Quality Gate) —— 把控 3 个子模块总工交付的可检查看板
=====================================================================
老板 10-25 09:23: "3 个子模块总工的工作和质量, 你打算如何负责把控?"

把控不能靠"我看过了", 得能**机械判定**。本脚本把"交付质量"拆成 5 个可量化指标:
  Q1 交付齐备率   交接单是否含 6 项必填验收块 (结论/自评/证据分级/接口取值/卡点/复现命令)
  Q2 证据分级率   关键结论是否标了 [实测]/[官方]/[推算]/[0数据]
  Q3 接口声明率   每个总工把自己对跨模块接口的取值写进 interface_claims (冲突才能被检出)
  Q4 需求闭环率   needs_from → answered 的闭环比例 (需求发出去有没有回音)
  Q5 硬指标覆盖   各总工交付里有没有报出硬指标数字 (功耗/皮肤温度/厚度/延迟/球间距)

用法:  python3 state/gate_check.py [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
HANDOFF = os.path.join(PROJ, "HANDOFF")
FRAG_DIR = os.path.join(HERE, "fragments")
TRACKER = os.path.join(PROJ, "PROJECT_TRACKER.md")

AGENTS = ["main", "hw-lead", "sw-lead", "mech-lead"]
FILE_OF = {"main": "pm.yaml", "hw-lead": "hw.yaml", "sw-lead": "sw.yaml", "mech-lead": "mech.yaml"}

# 6 项必填验收块: (代号, 说明, 标题关键词候选)
REQUIRED_BLOCKS = [
    ("B1", "结论摘要", ["结论", "结论摘要", "结论 (给", "一句话"]),
    ("B2", "验收标准自评 (逐条 通过/不通过/未验)", ["验收标准自评", "自评", "验收标准"]),
    ("B3", "证据分级 (实测/官方/推算/0数据)", ["证据分级", "证据等级", "证据"]),
    ("B4", "接口取值声明 (interface_claims)", ["接口取值", "接口声明", "interface_claims", "接口请求"]),
    ("B5", "未决项与卡点 (需要谁回答什么)", ["阻塞", "卡点", "未决", "待办"]),
    ("B6", "自证复现命令", ["复现", "复现命令", "自证"]),
]
EVIDENCE_TAGS = ["实测", "官方", "推算", "0数据", "0 数据"]
HARD_METRICS = {
    "功耗(W)": r"\d+(\.\d+)?\s*W\b|功耗",
    "皮肤温度(°C)": r"\d+(\.\d+)?\s*°C|皮肤侧|ISO 13732",
    "镜腿/镜脚厚度(mm)": r"\d+(\.\d+)?\s*mm|厚度",
    "端到端延迟(ms)": r"\d+(\.\d+)?\s*ms|延迟",
    "FCCSP 球间距(pitch)": r"pitch|球间距|FCCSP",
}


def handoff_files() -> dict:
    """每个 agent 最新一份交接单。"""
    out = {}
    if not os.path.isdir(HANDOFF):
        return out
    for fn in sorted(os.listdir(HANDOFF)):
        if not fn.endswith(".md") or fn == "README.md":
            continue
        for a in AGENTS:
            if f"_{a}_" in fn:
                out[a] = os.path.join(HANDOFF, fn)
    return out


def check_blocks(text: str) -> dict:
    heads = re.findall(r"^#{1,4}\s*(.+)$", text, re.M)
    blob = "\n".join(heads)
    res = {}
    for code, desc, kws in REQUIRED_BLOCKS:
        hit = any(kw in blob for kw in kws)
        res[code] = {"desc": desc, "ok": hit}
    return res


def check_evidence(text: str) -> dict:
    found = [t for t in EVIDENCE_TAGS if t in text]
    return {"tags": found, "n": len(found), "ok": len(found) >= 2}


def check_hard_metrics(text: str) -> dict:
    res = {}
    for name, pat in HARD_METRICS.items():
        res[name] = bool(re.search(pat, text))
    return res


def load_frag(aid: str) -> dict:
    p = os.path.join(FRAG_DIR, FILE_OF[aid])
    if not os.path.exists(p):
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            d = yaml.safe_load(f)
        return d if isinstance(d, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    handoffs = handoff_files()
    report = {"agents": {}, "gaps": []}

    # 全局答案索引: 别人回答给我的 key
    global_answers = {}
    # 全局需求索引: 每个人发出的 needs key (用来判断我的 answers 是否真对上了别人的需求)
    global_needs = {}
    for aid in AGENTS:
        d = load_frag(aid)
        for a in d.get("answers") or []:
            k, to = a.get("key"), a.get("to")
            if k and to:
                global_answers.setdefault(to, set()).add(k)
        for n in d.get("needs_from") or []:
            if n.get("key"):
                global_needs.setdefault(n["key"], {})[aid] = n.get("to")

    for aid in AGENTS:
        d = load_frag(aid)
        hp = handoffs.get(aid)
        text = ""
        if hp and os.path.exists(hp):
            with open(hp, encoding="utf-8", errors="ignore") as f:
                text = f.read()
        blocks = check_blocks(text) if text else {}
        ev = check_evidence(text) if text else {"tags": [], "n": 0, "ok": False}
        hm = check_hard_metrics(text) if text else {}

        needs = d.get("needs_from") or []
        answers = d.get("answers") or []
        answered_keys = {a.get("key") for a in answers if a.get("key")}
        # 【问方视角】我的需求被别人答了没有 (口径与 merge.py 一致: 被问方作答才算)
        globally_answered = global_answers.get(aid, set())
        answered_incoming = sum(1 for n in needs if n.get("key") in globally_answered)
        # 【答方视角】我登记的答复里, 有多少真对上了别人的需求 key
        effective_answers = sum(1 for a in answers
                                if any(owner == a.get("to") and tgt == aid
                                       for owner, tgt in global_needs.get(a.get("key"), {}).items()))
        # ★ 真·可立即闭: 答案写在被问方交接单正文里, 但没登记进 answers
        #   (用 need.item 的中文原文去被问方文档里搜 —— key 是英文, 搜 key 没用)
        closable = 0
        closable_detail = []
        for n in needs:
            if n.get("waiting_on", "agent") != "agent":
                continue
            k = n.get("key")
            if k in globally_answered:
                continue                      # 已被答方登记 → merge 已闭合
            item = (n.get("item") or "").strip()
            probe = item[:8] if len(item) >= 8 else item
            if not probe:
                continue
            for other in AGENTS:
                if other == aid or other not in handoffs:
                    continue
                try:
                    body = open(handoffs[other], encoding="utf-8").read()
                except Exception:
                    continue
                if probe and probe in body:
                    closable += 1
                    closable_detail.append(f"{aid}←{other} {k}")
                    break
        ext = sum(1 for n in needs if n.get("waiting_on", "agent") != "agent")
        # 自闭合: 需求的发起人自己回答了它 (说明 key 双向重用时 to 写错了)
        self_closed = 0
        for n in needs:
            k = n.get("key")
            # 需求发起人自己答了自己 (author==owner 且 to==owner) → 真自闭合
            if any(a.get("key") == k and a.get("to") == aid for a in answers):
                self_closed += 1
        ext_st = sum(1 for n in needs if n.get("state") == "waiting_external")
        claims = d.get("interface_claims") or []

        entry = {
            "handoff": os.path.basename(hp) if hp else None,
            "blocks": blocks,
            "blocks_ok": sum(1 for b in blocks.values() if b["ok"]),
            "blocks_total": len(REQUIRED_BLOCKS),
            "evidence": ev,
            "hard_metrics": hm,
            "hard_metrics_n": sum(1 for v in hm.values() if v),
            "interface_claims": len(claims),
            "needs_total": len(needs),
            "needs_answered_incoming": answered_incoming,
            "answers_registered": len(answers),
            "answers_effective": effective_answers,
            "needs_closable_unregistered": closable,
            "needs_closable_detail": closable_detail,
            "needs_self_closed": self_closed,
            "needs_waiting_external": ext,
            "artifacts": len(d.get("artifacts") or []),
            "blockers": len(d.get("blockers") or []),
        }
        report["agents"][aid] = entry

    # ---- 全局汇总 ----
    subs = [a for a in AGENTS if a != "main"]
    tot_b = sum(report["agents"][a]["blocks_total"] for a in subs)
    ok_b = sum(report["agents"][a]["blocks_ok"] for a in subs)
    tot_n = sum(report["agents"][a]["needs_total"] for a in subs)
    ok_n = sum(report["agents"][a]["needs_answered_incoming"] for a in subs)
    tot_c = sum(report["agents"][a]["interface_claims"] for a in subs)
    ev_ok = sum(1 for a in subs if report["agents"][a]["evidence"]["ok"])
    hm_ok = sum(1 for a in subs if report["agents"][a]["hard_metrics_n"] >= 3)

    tot_closable = sum(report["agents"][a]["needs_closable_unregistered"] for a in subs)
    tot_ext = sum(report["agents"][a]["needs_waiting_external"] for a in subs)
    # ★ 全局口径 (含 main) —— 规则与 merge.py **完全一致**, 两边数字必须对得上
    #   merge.py: ans = [a for a in answers_by_key[k] if a["_by"] == ask_to]
    #   → 需求 (owner,key,to) 被闭合 ⟺ 存在 key 相同且 author == to 的答复
    all_frags = {aid: load_frag(aid) for aid in AGENTS}
    _answers_by_key = {}
    for _aid, _d in all_frags.items():
        for _a in (_d.get("answers") or []):
            if _a.get("key"):
                # ★ 作者 = 分片归属的 agent (merge.py 就是这么记的: {"**a, "_by": aid})
                _answers_by_key.setdefault(_a["key"], []).append(_aid)
    def _answered(n):
        k, to = n.get("key"), n.get("to")
        # 老板决策 (need 带 decision 字段, 由项目总工代录) 同样算闭合
        if n.get("decision"):
            return True
        return bool(to) and to in (_answers_by_key.get(k) or [])
    glob_ext = sum(1 for aid, d in all_frags.items() for n in (d.get("needs_from") or [])
                   if (n.get("waiting_on") or "agent") != "agent" and not _answered(n))
    glob_pending = sum(1 for aid, d in all_frags.items() for n in (d.get("needs_from") or [])
                       if (n.get("waiting_on") or "agent") == "agent" and not _answered(n))
    # ★ 与 merge.py 自对账 (防止两边口径再次漂移)
    _recon = None
    try:
        with open(os.path.join(PROJ, "STATE.yaml"), encoding="utf-8") as f:
            _st = yaml.safe_load(f) or {}
        _ms = (_st.get("summary") or {})
        _recon = {
            "merge_open_needs": _ms.get("open_needs"),
            "gate_global_pending": glob_pending,
            "merge_waiting_external": _ms.get("waiting_external_needs"),
            "gate_global_waiting_external": glob_ext,
            "ok": (_ms.get("open_needs") == glob_pending
                   and _ms.get("waiting_external_needs") == glob_ext),
        }
    except Exception as e:  # noqa: BLE001
        _recon = {"error": str(e), "ok": None}

    report["summary"] = {
        "blocks_ok": ok_b, "blocks_total": tot_b,
        "needs_closable_unregistered": tot_closable,
        "needs_waiting_external": tot_ext,
        "global_waiting_external": glob_ext,
        "global_pending": glob_pending,
        "reconciliation": _recon,
        "evidence_ok_agents": ev_ok, "evidence_total_agents": len(subs),
        "needs_answered_incoming": ok_n, "needs_total": tot_n,
        "answers_effective": sum(report["agents"][a]["answers_effective"] for a in subs),
        "answers_registered": sum(report["agents"][a]["answers_registered"] for a in subs),
        "interface_claims_total": tot_c,
        "hard_metric_agents": hm_ok, "hard_metric_total_agents": len(subs),
    }

    # ---- 缺口清单 (可直接转成派活项) ----
    for a in subs:
        e = report["agents"][a]
        for code, desc, _ in REQUIRED_BLOCKS:
            if not e["blocks"].get(code, {}).get("ok"):
                report["gaps"].append(f"{a}: 交接单缺 [{code}] {desc}")
        if not e["evidence"]["ok"]:
            report["gaps"].append(f"{a}: 关键结论未做证据分级 (实测/官方/推算/0数据)")
        if e["interface_claims"] < 3:
            report["gaps"].append(f"{a}: interface_claims 只有 {e['interface_claims']} 条 → 冲突检测形同虚设 (目标 ≥3 条关键接口)")
        if e["needs_closable_unregistered"]:
            report["gaps"].append(f"{a}: {e['needs_closable_unregistered']} 条需求**对方已答但没登记 answers** → 状态源说\"没人答\", 会导致重复催办 (立即可闭)")
        real_open = e["needs_total"] - e["needs_answered_incoming"] - e["needs_closable_unregistered"] - e["needs_waiting_external"]
        if real_open > 0:
            report["gaps"].append(f"{a}: {real_open} 条需求确实还没人答 (等另一个总工)")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
        return 0

    s = report["summary"]
    print("=" * 74)
    print("项目总工质量门 · 3 个子模块总工交付看板")
    print("=" * 74)
    print(f"\n【Q1 交付齐备率】 {s['blocks_ok']}/{s['blocks_total']} 个必填验收块齐全")
    for a in subs:
        e = report["agents"][a]
        miss = [c for c, b in e["blocks"].items() if not b["ok"]]
        print(f"   {a:<10} {e['blocks_ok']}/{e['blocks_total']}  缺: {miss or '无'}   交接单: {e['handoff']}")
    print(f"\n【Q2 证据分级率】 {s['evidence_ok_agents']}/{s['evidence_total_agents']} 个总工的交付做了证据分级")
    for a in subs:
        print(f"   {a:<10} 标签: {report['agents'][a]['evidence']['tags'] or '无'}")
    print(f"\n【Q3 接口声明率】 全员 interface_claims 共 {s['interface_claims_total']} 条 (目标 ≥3 条/总工 → 冲突才能自动检出)")
    for a in subs:
        print(f"   {a:<10} {report['agents'][a]['interface_claims']} 条")
    print(f"\n【Q4 需求闭环率】")
    print(f"   问方视角 (我的需求被别人答了): {s['needs_answered_incoming']}/{s['needs_total']}  ← 与 merge.py 口径一致")
    print(f"   答方视角 (我登记的答复): {s['answers_registered']} 条, 其中 {s['answers_effective']} 条真对上了别人的需求 key")
    for a in subs:
        e = report["agents"][a]
        print(f"   {a:<10} 被答 {e['needs_answered_incoming']}/{e['needs_total']} | 我答 {e['answers_registered']} 条(有效 {e['answers_effective']})"
              f" | 产出 {e['artifacts']} | 阻塞 {e['blockers']}")
    print(f"   ├─ ⚠️ **疑似漏登记 (答案在对方文档正文里, 但没进 answers)**: {s['needs_closable_unregistered']} 条  ← 需人工判定, 也有可能是 waiting_on 标错")
    print(f"   └─ ⏳ 等外部 (老板/原厂/JBD, 不算谁的锅): 子总工 {s['needs_waiting_external']} 条 | **全局 {s['global_waiting_external']} 条** (含 main)")
    print(f"   └─ 🔵 等另一个总工 (真·内部未闭合): **全局 {s['global_pending']} 条**")
    rc = s.get("reconciliation") or {}
    if rc.get("ok") is True:
        print(f"   ✅ 与 merge.py 自对账一致 (等外部 {rc['merge_waiting_external']} / 等总工 {rc['merge_open_needs']})")
    elif rc.get("ok") is False:
        print(f"   ❌ 与 merge.py **不一致** (merge: 外部 {rc['merge_waiting_external']} / 总工 {rc['merge_open_needs']}"
              f" vs gate: 外部 {rc['gate_global_waiting_external']} / 总工 {rc['gate_global_pending']}) → 先重跑 merge.py")
    else:
        print(f"   ⚠️ 对账未完成: {rc.get('error', 'STATE.yaml 读不到')} → 先跑 merge.py")
    sc = sum(report["agents"][a]["needs_self_closed"] for a in subs)
    print(f"   ⚠️ 自闭合 (自己答自己 = to 写错): {sc} 条")
    overloaded = {k: list(v.keys()) for k, v in global_needs.items() if len(v) > 1}
    if overloaded:
        print(f"   ⚠️ key 双向重用 (配对靠 to 字段区分, 写错就闭错): {len(overloaded)} 个")
        for k, owners in list(overloaded.items())[:5]:
            print(f"      {k}: 发起方 {owners}")
    print(f"\n【Q5 硬指标覆盖】 {s['hard_metric_agents']}/{s['hard_metric_total_agents']} 个总工报出了 ≥3 类硬指标数字")
    for a in subs:
        e = report["agents"][a]
        hit = [k for k, v in e["hard_metrics"].items() if v]
        print(f"   {a:<10} {e['hard_metrics_n']}/5 类: {hit}")
    print(f"\n【缺口清单】(可直接转成下一轮派活项) —— {len(report['gaps'])} 条")
    for g in report["gaps"]:
        print(f"   · {g}")
    print("\n" + "=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
