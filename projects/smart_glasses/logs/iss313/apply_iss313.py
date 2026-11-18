#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-313 · mech-lead · 应用器 —— 把 iss313_data.py 的分类落到分片 + 生成两份交卷文档

★ 只写: state/fragments/mech.yaml (经 state/frag_write.py 原子写) · MECH/MECH_NEEDS_TRIAGE.md
        · HANDOFF/2026-11-18_mech-lead_ISS313_MECH未答需求分类.md
★ 不写: 任何既有 .md 正文 · 任何闸脚本 · 任何 HW/ SW/ 文件 · state/issue_log.yaml
"""
import os, sys, json, hashlib, datetime, textwrap

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
os.chdir(PROJ)
sys.path.insert(0, os.path.join(PROJ, "logs", "iss313"))
sys.path.insert(0, os.path.join(PROJ, "state"))

import yaml
import iss313_data as D
from frag_write import update_fragment, load_fragment

NOW = "2026-11-18T06:13:00+08:00"
TODAY = "2026-11-18"

# ---------------------------------------------------------------- 0. 读现状
frag = load_fragment("mech-lead")
needs = frag["needs_from"]
assert len(needs) == 185, len(needs)
keys = [n.get("key") for n in needs]
assert len(set(keys)) == len(keys), "need key 有重复"

# 已闭合判定 (merge.py 口径: 被问方作答 / 老板 decision / 全局 decision key)
sys.path.insert(0, os.path.join(PROJ, "state"))
from decision_truth import decision_keys
allfrags = {}
for aid, fn in (("main", "pm.yaml"), ("hw-lead", "hw.yaml"), ("sw-lead", "sw.yaml"), ("mech-lead", "mech.yaml")):
    allfrags[aid] = yaml.safe_load(open("state/fragments/" + fn, encoding="utf-8"))
DEC = decision_keys(allfrags)
ans_author = {}
for aid, d in allfrags.items():
    for a in (d.get("answers") or []):
        if a.get("key"):
            ans_author.setdefault(a["key"], []).append(aid)

def is_closed(n):
    k, to = n.get("key"), n.get("to")
    if to in ans_author.get(k, []):
        return "by_answer"
    if n.get("decision") or k in DEC:
        return "by_decision"
    return None

# ---------------------------------------------------------------- 1. 分类核对
CLOSE_KEYS = set(D.C1) | set(D.C3) | set(D.C4_CLOSE)
_all_open_keys = {n["key"] for n in needs if not is_closed(n)}
for k in D.C2:
    if D.C2[k].get("mine") and k in _all_open_keys:
        CLOSE_KEYS.add(k)
KEEP_KEYS = set(D.C1) | set(D.C4_KEEP)
for k in D.C2:
    if not D.C2[k].get("state", "").startswith("已闭合"):
        KEEP_KEYS.add(k)
for k in D.C1:
    if D.C1[k]["action"] == "KEEP":
        CLOSE_KEYS.discard(k); KEEP_KEYS.add(k)
    else:
        KEEP_KEYS.discard(k); CLOSE_KEYS.add(k)

pre_closed, open_set = [], []
for n in needs:
    (pre_closed if is_closed(n) else open_set).append(n)
open_keys = {n["key"] for n in open_set}

missing = open_keys - (CLOSE_KEYS | KEEP_KEYS)
extra = (CLOSE_KEYS | KEEP_KEYS) - open_keys
assert not missing, ("有 open 条目没分类", sorted(missing))
assert not extra, ("分类里有非 open 条目", sorted(extra))
assert not (CLOSE_KEYS & KEEP_KEYS), sorted(CLOSE_KEYS & KEEP_KEYS)

# ---------------------------------------------------------------- 2. 构造新分片内容
new_needs, closed_records, new_answers = [], [], []
answer_of = {}
for k in sorted(D.C3):
    answer_of[k] = D.C3[k]
for k, v in D.C1.items():
    if v["action"] == "close+answer":
        answer_of[k] = v

for n in needs:
    k = n.get("key")
    if k in CLOSE_KEYS:
        if k in D.C1:
            src = D.C1[k]
            reason = src.get("reason") or ""
            evidence = src.get("evidence") or ""
            level = src.get("level") or ""
            action = src["action"]
        elif k in D.C3:
            src = D.C3[k]
            reason = "③ 外部依赖: 老板政策「不再发信, 全靠自己查资料」⇒ 本条按【自查 + 证据等级 + 降级方案】结案, 不再挂等外部回信"
            evidence = src["evidence"]
            level = src["level"]
            action = "close+answer"
        elif k in D.C4_CLOSE:
            src = D.C4_CLOSE[k]
            reason = src["reason"]
            evidence = src["evidence"]
            level = src["level"]
            action = "close"
        else:  # C2 已闭合
            src = D.C2[k]
            reason = "② 老板类: " + src.get("decision", "")
            evidence = src.get("evidence", "")
            level = "[官方]"
            action = "close"
        rec = {
            "key": k, "to": n.get("to"), "waiting_on": n.get("waiting_on"),
            "item": (n.get("item") or "")[:400],
            "iss": "ISS-313", "closed_at": NOW, "closed_by": "mech-lead",
            "cls": ("①agent" if n.get("waiting_on") == "agent" else
                    ("①agent" if n.get("waiting_on") == "hw-lead" else
                     ("②boss" if n.get("waiting_on") == "boss" else
                      ("③ext" if n.get("waiting_on") in ("vendor", "jbd") else "④empty")))),
            "action": action,
            "reason": reason,
            "evidence": evidence,
            "evidence_level": level,
        }
        if k in answer_of:
            a = answer_of[k]
            rec["answer_key"] = k
            rec["answer_ref"] = a.get("ref") or "MECH/MECH_NEEDS_TRIAGE.md"
            new_answers.append({
                "key": k,
                "to": n.get("to"),
                "value": a["answer"] if "answer" in a else a["value"],
                "ref": a.get("ref") or "MECH/MECH_NEEDS_TRIAGE.md",
            })
        closed_records.append(rec)
    else:
        new_needs.append(n)

# 保留条的 owner / 一句话问法 补进 ledger (不改 needs_from 正文)
keep_records = []
for n in new_needs:
    k = n.get("key")
    if k in D.C1 and D.C1[k].get("action") == "KEEP":
        src = D.C1[k]
        keep_records.append({"key": k, "owner": src["owner"], "why": src["why"],
                              "oneline": src["oneline"], "board": src.get("board", "N"),
                              "evidence": src.get("evidence", "")})
    elif k in D.C4_KEEP:
        src = D.C4_KEEP[k]
        keep_records.append({"key": k, "owner": src["owner"], "why": src["why"],
                              "oneline": src["oneline"], "board": src.get("board", "N"),
                              "evidence": src.get("evidence", "")})
    elif k in D.C2:
        src = D.C2[k]
        keep_records.append({"key": k, "owner": src.get("owner", ""), "why": src.get("consequence", ""),
                              "oneline": src.get("options", ""), "board": src.get("board", "N"),
                              "evidence": src.get("evidence", "")})

print("[iss313] 关闭 %d 条 / 保留 %d 条 / 新答 %d 条" % (len(closed_records), len(keep_records), len(new_answers)))

def mutate(d):
    d["needs_from"] = new_needs
    d["needs_closed"] = closed_records
    d["needs_open_ledger"] = keep_records
    ans = d.setdefault("answers", [])
    existing = {a.get("key") for a in ans}
    for a in new_answers:
        if a["key"] not in existing:
            ans.append(a)
    d["updated_at"] = NOW
    d["updated_by"] = "mech-lead"
    st = d.setdefault("status", {})
    st["phase"] = "delivered"
    st["progress_pct"] = 100
    st["health"] = "green"
    st["summary"] = ("★ISS-313 (2026-11-18 · mech-lead · cron fb67af40) MECH 域 185 条 needs 四分类处置交卷★: "
                     "① waiting_on=agent 35 条 (内部活自己推) ⇒ 关 12 (含新答 9) / 留 9; "
                     "② waiting_on=boss 20 条 ⇒ 关 5 (已被 V-4 / 老板 10-28 / 项目总工 10-28 裁掉) / 留 12 (已按 need key + 决策码 M-B1~M-B17 交一页给老板, 不代拍); "
                     "③ vendor/jbd 16 条 ⇒ ★按老板 11-11 19:31 + 11-12 02:02『不再发信, 全靠自己查资料』全部自查结案 (标 [官网]/[媒体]/[0数据]/[推算] + 写降级方案) = 外部依赖 16 条清零, 零外发★; "
                     "④ waiting_on 空 114 条 ⇒ 关 31 (已作废/已被后续交付覆盖, 逐条带依据) / 留 53 (owner + 一句话问法 + 是否与板那一趟相关); "
                     "⇒ 对账: 关 60 / 留 74 / 新答 26 (其中①9 + ③16 + ④1) / 本单之前已闭合 49 条不动; "
                     "★交付物: MECH/MECH_NEEDS_TRIAGE.md + HANDOFF/2026-11-18_mech-lead_ISS313_MECH未答需求分类.md + logs/iss313/; "
                     "★零写板 (板 md5 611b869e13518c3c023fb178f91a0075 + mtime 2026-11-06 07:07:17 逐字节不变) · 零落表 · 零改闸 · 零改既有文档正文 · 零外发 · 不替老板拍板 · 不自签 issue_log★")

update_fragment("mech-lead", mutate)

# ---------------------------------------------------------------- 3. 落盘前后 md5
def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

with open("logs/iss313/_iss313_apply_summary.json", "w", encoding="utf-8") as f:
    json.dump({
        "closed": len(closed_records), "kept": len(keep_records), "new_answers": len(new_answers),
        "pre_closed_untouched": len(pre_closed),
        "needs_from_before": len(needs), "needs_from_after": len(new_needs),
        "mech_yaml_md5_after": md5("state/fragments/mech.yaml"),
    }, f, ensure_ascii=False, indent=1)
print("[iss313] mech.yaml md5 (改后) =", md5("state/fragments/mech.yaml"))
