# -*- coding: utf-8 -*-
"""F3 候选口径实测 (★只读★ · agent id 用 merge.py 的真 id ★)"""
import os, re, sys, time, yaml
PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "state"))
import decision_truth as dt
FD = os.path.join(PROJ, "state", "fragments")
FILES = {"main": "pm.yaml", "hw-lead": "hw.yaml", "mech-lead": "mech.yaml", "sw-lead": "sw.yaml"}
t0 = time.time()
frags = {}
for aid, fn in FILES.items():
    frags[aid] = yaml.safe_load(open(os.path.join(FD, fn), encoding="utf-8")) or {}
print("load 4 fragments: %.2fs" % (time.time() - t0))
dec = dt.decision_keys(frags)
answers_by_key = {}
for aid, fr in frags.items():
    for a in fr.get("answers") or []:
        k = a.get("key")
        if k:
            answers_by_key.setdefault(k, []).append({**a, "_by": aid})
HEX32 = re.compile(r"\b[0-9a-f]{32}\b")
rows = []
for aid, fr in frags.items():
    for n in fr.get("needs_from") or []:
        if n.get("to") != "sw-lead":
            continue
        k = n.get("key")
        ans = [a for a in answers_by_key.get(k, []) if a["_by"] == "sw-lead"]
        closed = bool(ans) or bool(n.get("decision")) or (k in dec)
        item = n.get("item") or ""
        mds = sorted(set(HEX32.findall(item)))
        rows.append({"by": aid, "key": k, "closed": closed, "md5": mds,
                     "waiting_on": n.get("waiting_on") or "agent", "since": n.get("since")})
print("to=sw-lead needs total = %d" % len(rows))
openn = [r for r in rows if not r["closed"]]
print("★仍 open = %d" % len(openn))
for r in sorted(openn, key=lambda x: (x["by"], x["key"] or "")):
    print("   open %-9s %-52s md5=%s waiting_on=%s since=%s" % (r["by"], r["key"], r["md5"], r["waiting_on"], r["since"]))
print("★仍 open 且引着 md5 的 need 条数 = %d" % sum(1 for r in openn if r["md5"]))
print("★仍 open 且引着 md5 的 md5 总条数 = %d" % sum(len(r["md5"]) for r in openn if r["md5"]))
print("已闭合且引着 md5 = %d" % sum(1 for r in rows if r["closed"] and r["md5"]))
print("--- sw-lead 分片自己 needs_from 里 to=sw-lead 的 ---")
for r in rows:
    if r["by"] == "sw-lead":
        print("   ", r["key"], "closed=", r["closed"], "md5=", r["md5"])
