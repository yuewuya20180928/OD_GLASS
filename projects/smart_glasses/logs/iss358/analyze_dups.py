#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-358 cont1 只读分析器 (零写盘) —— 只读 state/fragments/*.yaml, 绝不碰 STATE.yaml"""
import os, sys, json, yaml
from collections import Counter, defaultdict

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRAGS = {"main": "pm.yaml", "hw-lead": "hw.yaml", "sw-lead": "sw.yaml", "mech-lead": "mech.yaml"}
HIGH = ("answers", "needs_from")
LOW = ("artifacts", "interface_claims", "risks", "blockers")

def load(agent):
    p = os.path.join(PROJ, "state", "fragments", FRAGS[agent])
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def effkey(e):
    return str(e.get("key") or e.get("id") or e.get("path") or "")

def main():
    D = {a: load(a) for a in FRAGS}
    out = {}
    # ---- 高危 answers 重名 (mech-lead) ----
    ans = [e for e in (D["mech-lead"].get("answers") or []) if isinstance(e, dict)]
    dupans = defaultdict(list)
    for i, e in enumerate(ans):
        dupans[str(e.get("key") or "")].append((i, e))
    out["mech_high_ans"] = {k: [(i, e.get("_by"), str(e.get("value"))[:120], len(str(e.get("value") or ""))) for i, e in v]
                            for k, v in dupans.items() if len(v) > 1}
    out["mech_ans_total"] = len(ans)
    # ---- 低危 mech artifacts 同 path 重复 ----
    arts = [e for e in (D["mech-lead"].get("artifacts") or []) if isinstance(e, dict)]
    bypath = defaultdict(list)
    for i, e in enumerate(arts):
        bypath[str(e.get("path") or "")].append((i, e))
    out["mech_art_total"] = len(arts)
    out["mech_art_dup_path"] = {
        p: [(i, e.get("key"), len(str(e.get("summary") or e.get("value") or "")), str(e.get("summary") or "")[:80]) for i, e in v]
        for p, v in bypath.items() if len(v) > 1 and p}
    # 其它低危段
    for sect in LOW[1:]:
        ents = [e for e in (D["mech-lead"].get(sect) or []) if isinstance(e, dict)]
        c = Counter(effkey(e) for e in ents if effkey(e))
        out[f"mech_{sect}_dups"] = {k: n for k, n in c.items() if n > 1}
        out[f"mech_{sect}_total"] = len(ents)
    # ---- 四片 needs_from 全表 + 闭合统计 ----
    needs = []
    for agent in FRAGS:
        for e in (D[agent].get("needs_from") or []):
            if not isinstance(e, dict):
                continue
            needs.append({"owner": agent, "key": str(e.get("key") or ""),
                          "to": str(e.get("to") or ""), "item": str(e.get("item") or e.get("question") or "")[:110],
                          "section": str(e.get("section") or "")})
    out["needs_total"] = len(needs)
    # 答案索引: (by, key) -> n
    ansidx = defaultdict(list)
    for agent in FRAGS:
        for e in (D[agent].get("answers") or []):
            if not isinstance(e, dict):
                continue
            ansidx[(str(e.get("_by") or ""), str(e.get("key") or ""))].append(e)
    def closed(nd):
        to = nd["to"]
        if not to:
            return False
        return bool(ansidx.get((to, nd["key"])))
    unclosed = [n for n in needs if not closed(n)]
    out["unclosed_before"] = [{"owner": n["owner"], "key": n["key"], "to": n["to"], "item": n["item"]} for n in unclosed]
    out["unclosed_before_n"] = len(unclosed)
    out["unclosed_total_need_n"] = len(needs)
    # 目标 4 组 key 的跨片询问者
    tgt = ["pcb_outline_confirm", "ntc_placement", "iss219_mech_c7_sink_area_confirm", "iss251_mech_service_port_pad_y_migrate"]
    out["askers"] = {k: [{"owner": n["owner"], "to": n["to"], "item": n["item"], "closed": closed(n)}
                          for n in needs if n["key"] == k] for k in tgt}
    # 各片 answers 计数
    out["answers_per_agent"] = {a: len([e for e in (D[a].get("answers") or []) if isinstance(e, dict)]) for a in FRAGS}
    out["needs_per_agent"] = {a: len([e for e in (D[a].get("needs_from") or []) if isinstance(e, dict)]) for a in FRAGS}
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)

main()
