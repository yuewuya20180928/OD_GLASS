#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-358 cont1 闭合台账核对器 (只读·零写盘·只读 fragments + decision_truth)

★口径严格对齐 merge.py:295 / gate_check.py:433-441:
    answered(n) = n.decision  OR  n.key in decision_keys(frags)  OR  (n.to 在【拥有该 key 的答案的分片归属 agent】名单里)
★也就是: 「被问的那个 agent 名下存在【任意一条】该 key 的答案」⇒ 只看存在性, 不看答案内容 ★
"""
import os, sys, json, yaml
from collections import defaultdict

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJ, "state"))
FRAGS = {"main": "pm.yaml", "hw-lead": "hw.yaml", "sw-lead": "sw.yaml", "mech-lead": "mech.yaml"}

def load(agent):
    with open(os.path.join(PROJ, "state", "fragments", FRAGS[agent]), "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def main():
    frags = {a: load(a) for a in FRAGS}
    from decision_truth import decision_keys
    dec = decision_keys(frags)

    answers_by_key = defaultdict(list)      # key -> [owner agent, ...] (每条答案一个 entry)
    for aid, fr in frags.items():
        for a in (fr.get("answers") or []):
            if isinstance(a, dict) and a.get("key"):
                answers_by_key[a["key"]].append(aid)

    def answered(n):
        k, to = n.get("key"), n.get("to")
        if n.get("decision"):
            return True
        if k and k in dec:
            return True
        return bool(to) and to in answers_by_key.get(k, [])

    rows = []
    for aid in FRAGS:
        for n in (frags[aid].get("needs_from") or []):
            if not isinstance(n, dict):
                continue
            rows.append({"owner": aid, "key": n.get("key") or "", "to": n.get("to") or "",
                         "waiting_on": n.get("waiting_on") or "agent",
                         "has_decision": bool(n.get("decision")),
                         "item": str(n.get("item") or "")[:120],
                         "answered": answered(n)})
    tot = len(rows)
    ans_n = sum(1 for r in rows if r["answered"])
    unans = [r for r in rows if not r["answered"]]
    pend = [r for r in unans if r["waiting_on"] == "agent"]
    ext = [r for r in unans if r["waiting_on"] != "agent"]
    out = {"total_needs": tot, "answered": ans_n, "unanswered_total": len(unans),
           "unanswered_pending": len(pend), "unanswered_waiting_external": len(ext),
           "dec_keys_n": len(dec),
           "unanswered_list": unans}
    # 目标 4 组 key 的跨片询问者 + 闭合态
    tgt = ["pcb_outline_confirm", "ntc_placement", "iss219_mech_c7_sink_area_confirm",
           "iss251_mech_service_port_pad_y_migrate"]
    out["target_askers"] = {}
    for k in tgt:
        out["target_askers"][k] = {
            "askers": [{"owner": r["owner"], "to": r["to"], "answered": r["answered"],
                        "has_decision": r["has_decision"], "item": r["item"]}
                       for r in rows if r["key"] == k],
            "answer_owners": answers_by_key.get(k, []),
        }
    # mech.yaml 分片里 4 组 key 的答案明细 (含 to / ref / value 全长)
    mech = frags["mech-lead"]
    out["mech_target_answers"] = {}
    for i, a in enumerate(mech.get("answers") or []):
        if isinstance(a, dict) and a.get("key") in tgt:
            out["mech_target_answers"].setdefault(a["key"], []).append(
                {"idx": i, "to": a.get("to"), "ref": a.get("ref"), "value": a.get("value"),
                 "vlen": len(str(a.get("value") or "")), "extra": {kk: vv for kk, vv in a.items()
                     if kk not in ("key", "to", "value", "ref")}})
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)

main()
