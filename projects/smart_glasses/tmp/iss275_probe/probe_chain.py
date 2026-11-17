#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-275 只读探针: 算落表台账里 网表/脚表 的链头 (★不写任何盘上文件★)"""
import os
import re
import sys

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LEDGER_CANON = "HW/SCHEMATIC_LANDING_V1_LANDED.md"
LEDGER_MD_RE = re.compile(r"\b[0-9a-f]{32}\b|\b[0-9a-f]{12}\b")


def ledger_records(text, rel):
    out = []
    ctx_iss = None
    title = "(文首)"
    base = os.path.basename(rel)
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("#"):
            title = s
            hit = re.findall(r"ISS-\d+", s)
            if hit:
                ctx_iss = hit[0]
            continue
        if not s.startswith("|"):
            continue
        if rel not in s and base not in s:
            continue
        tk = LEDGER_MD_RE.findall(s)
        if len(tk) < 2:
            continue
        row_iss = re.findall(r"ISS-\d+", s)
        out.append({"prev": tk[0][:12], "new": tk[-1][:12],
                    "iss": row_iss[0] if row_iss else ctx_iss,
                    "sec": title, "row": s[:140]})
    return out


def ledger_state(rel, text):
    recs = ledger_records(text, rel)
    new_keys = {r["new"] for r in recs}
    prev_keys = {r["prev"] for r in recs}
    heads = sorted(new_keys - prev_keys)
    producer = {}
    for r in recs:
        producer.setdefault(r["new"], set())
        if r["iss"]:
            producer[r["new"]].add(r["iss"])
    why = ""
    head = None
    if not recs:
        why = "台账里一条记录都没有"
    elif not heads:
        why = "没有链头 (每条记录都是别人的前驱 ⇒ 台账不成链)"
    elif len(heads) > 1:
        why = f"链头不唯一 = {heads}"
    else:
        head = heads[0]
    chain = []
    if head:
        by_new = {}
        for r in recs:
            by_new.setdefault(r["new"], []).append(r)
        cur, seen = head, {head}
        chain = [head]
        while True:
            rs = by_new.get(cur) or []
            if not rs:
                break
            prevs = {r["prev"] for r in rs if r["prev"] != r["new"]}
            if len(prevs) != 1:
                why = why or f"链上 {cur} 的前驱不唯一 = {sorted(prevs)}"
                chain = []
                break
            p = prevs.pop()
            if p in seen:
                why = why or f"链成环 ({p})"
                chain = []
                break
            cur = p
            seen.add(cur)
            chain.append(cur)
    return {"records": recs, "head": head, "chain": chain,
            "producer": producer, "why": why,
            "head_iss": sorted(producer.get(head, set())) if head else [],
            "known": new_keys | prev_keys}


def main():
    can = open(os.path.join(ROOT, LEDGER_CANON), encoding="utf-8").read()
    # 锚点登记的落表台账位置
    import yaml
    led = open(os.path.join(ROOT, "SW/SW_MD5_BASELINE_LEDGER.md"), encoding="utf-8").read()
    m = re.search(r"# BEGIN SW_MD5_ANCHORS(.*?)# END SW_MD5_ANCHORS", led, re.S)
    anchors = yaml.safe_load(m.group(1))["anchors"]
    specs = anchors["source_ledger"]["landing_records"]
    print("★锚点登记的落表台账位置:")
    for s in specs:
        print("   ", s, "EXISTS" if os.path.isfile(os.path.join(ROOT, s)) else "(通配)")

    # (a) 只用 canonical
    union = can
    for s in specs:
        if s == LEDGER_CANON:
            continue
        d, b = os.path.dirname(s) or ".", os.path.basename(s)
        import glob
        for hit in sorted(glob.glob(os.path.join(ROOT, d, b))):
            union += "\n" + open(hit, encoding="utf-8").read()

    for rel in ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv"):
        for label, text in (("★(a) canonical only", can), ("★(b) union all landing_records", union)):
            st = ledger_state(rel, text)
            orphan = sorted({r["new"] for r in st["records"]} - set(st["chain"]))
            print("\n=== %s | %s ===" % (rel, label))
            print("  records=%d head=%s head_iss=%s why=%r" % (
                len(st["records"]), st["head"], st["head_iss"], st["why"]))
            print("  chain=%s" % (st["chain"],))
            print("  orphan=%s" % (orphan,))
            for r in st["records"]:
                print("    - prev=%s new=%s iss=%s | %s" % (r["prev"], r["new"], r["iss"], r["row"][:100]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
