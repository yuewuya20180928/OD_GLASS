#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-362 · SW 侧「S10 换封装真值」影响面 · 只读探针 (★零写板·零落表·零写真件★)

★本探针只读 ⇒ 只往 stdout 打 ⇒ 留证由调用方重定向到 logs/iss362/★

口径来源 (全部照抄既有权威件, 不自己另发明):
  · 链头 = SW/tools/check_demo_panel_spec.py 的 sw_ledger_state()  (ISS-275 判决源换源机制)
  · 判决源台账 = HW/SCHEMATIC_LANDING_V1_LANDED.md (LEDGER_CANON)
  · 待办 need = STATE.yaml needs_matrix.pending 里 to=sw-lead 的条目
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "SW", "tools"))

import check_demo_panel_spec as dps          # noqa: E402  (只读 import, 不改它)

LEDGER = dps.LEDGER_CANON
MANAGED = ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv")


def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def main() -> int:
    print("=" * 78)
    print("ISS-362 只读探针 · %s" % PROJ)
    print("=" * 78)

    # ---------- ① 三份真源: 盘上现值 + footprint 栏实测 ----------
    print("\n[1] 三份受管真源 · 盘上现值 + footprint 栏")
    ledger_text = read_text(os.path.join(PROJ, LEDGER))
    heads = {}
    for rel in MANAGED:
        p = os.path.join(PROJ, rel)
        on_disk = md5_of(p)
        st = dps.sw_ledger_state(rel, ledger_text)
        heads[rel] = st
        print("  %-26s 盘上 md5 = %s" % (rel, on_disk))
        print("  %-26s 台账链头  = %s   链头产出单号 = %s" % ("", st["head"], st["head_iss"]))
        print("  %-26s 链长 = %d  取不准原因 = %r" % ("", len(st["chain"]), st["why"]))
        print("  %-26s 链(新→旧) = %s" % ("", " ← ".join(st["chain"][:8]) + (" …" if len(st["chain"]) > 8 else "")))
        print("  %-26s 盘上==链头? %s" % ("", (on_disk[:12] == (st["head"] or ""))))

    # ---------- ② footprint 栏实测 (三份真源) ----------
    print("\n[2] footprint 栏实测 (三份真源)")
    fp_stats = {}
    for rel, col in (("HW/netlist_v1.csv", 14), ("HW/netlist_v1_pins.csv", 11), ("HW/BOM_v1.csv", 10)):
        rows = list(csv.reader(read_text(os.path.join(PROJ, rel)).splitlines()))
        hdr = rows[0]
        name = hdr[col - 1] if col - 1 < len(hdr) else "(缺)"
        vals = {}
        for r in rows[1:]:
            if len(r) < col:
                continue
            v = (r[col - 1] or "").strip()
            vals[v] = vals.get(v, 0) + 1
        pending = sum(c for v, c in vals.items() if "待定" in v or "待选" in v)
        star = sum(c for v, c in vals.items() if "★" in v)
        fp_stats[rel] = (name, len(rows) - 1, pending, star, dict(sorted(vals.items(), key=lambda kv: -kv[1])[:6]))
        print("  %-26s 第 %d 栏 = %r  数据行 = %d  含『待定/待选』行 = %d  含★行 = %d"
              % (rel, col, name, len(rows) - 1, pending, star))
        for v, c in list(fp_stats[rel][4].items()):
            print("      %-42s × %d" % (repr(v)[:42], c))

    # ---------- ③ SW 侧现在有谁读 footprint 栏 ----------
    print("\n[3] SW 侧读 footprint 栏的地方 (SW/tools/*.py + SW/*.md)")
    hits = []
    sw_tools = os.path.join(PROJ, "SW", "tools")
    for fn in sorted(os.listdir(sw_tools)):
        if not fn.endswith(".py"):
            continue
        p = os.path.join(sw_tools, fn)
        txt = read_text(p)
        n = txt.count("footprint")
        if n:
            hits.append(("SW/tools/" + fn, n))
    sw_dir = os.path.join(PROJ, "SW")
    md_hits = []
    for fn in sorted(os.listdir(sw_dir)):
        if not fn.endswith(".md"):
            continue
        p = os.path.join(sw_dir, fn)
        txt = read_text(p)
        n = txt.count("footprint")
        if n:
            md_hits.append(("SW/" + fn, n))
    print("  SW/tools/*.py 命中文件 = %d 个" % len(hits))
    for k, v in hits:
        print("      %-56s × %d" % (k, v))
    print("  SW/*.md 命中文件 = %d 个" % len(md_hits))
    for k, v in md_hits:
        print("      %-56s × %d" % (k, v))
    print("  ⇒ SW/tools/*.py 里读 footprint 栏的文件数 = %d (★注意: 命中『footprint』字面量≠读那一栏★)" % len(hits))

    # ---------- ④ 8 条板侧输入清单: 有没有一条讲 footprint ----------
    print("\n[4] SW/BOARD_ONEPASS_SW_SYNC.md 的 8 条清单 · footprint 命中")
    sync_md = read_text(os.path.join(PROJ, "SW", "BOARD_ONEPASS_SW_SYNC.md"))
    m = re.search(r"```json\s*(\{.*?\})\s*```", sync_md, re.S)
    items = []
    if m:
        data = json.loads(m.group(1))
        items = data.get("items", [])
    print("  JSON 块 items 条数 = %d" % len(items))
    fp_items = []
    for it in items:
        blob = " ".join(str(it.get(k, "")) for k in ("title", "current_state", "action", "criterion", "blocked_by"))
        has = ("footprint" in blob.lower()) or ("封装" in blob)
        if has:
            fp_items.append(it["id"])
        print("    %-22s step=%-4s 含 footprint/封装 字样 = %s" % (it.get("id"), it.get("step"), has))
    print("  ⇒ 8 条里提到 footprint/封装的条目 = %s" % (fp_items or "无"))

    # ---------- ⑤ to=sw-lead 的待办 need 与 md5 逐条比对 ----------
    print("\n[5] STATE.yaml needs_matrix.pending 里 to=sw-lead 的条目 · md5 逐条比对")
    import yaml
    st8 = yaml.safe_load(read_text(os.path.join(PROJ, "STATE.yaml")))
    pend = st8["needs_matrix"]["pending"]
    sw = [n for n in pend if n.get("to") == "sw-lead"]
    on_disk_set = {md5_of(os.path.join(PROJ, r)): r for r in MANAGED}
    head_set = {}
    for r in MANAGED:
        h = heads[r]["head"]
        if h:
            head_set[h] = r
    print("  pending 总数 = %d ; to=sw-lead = %d" % (len(pend), len(sw)))
    stale_rows = []
    for n in sw:
        item = n.get("item", "") or ""
        ms = re.findall(r"\b[0-9a-f]{32}\b", item)
        if not ms:
            print("    %-46s md5 = (无)   ← 这条一个 32 位 md5 都没引" % n.get("key"))
            continue
        for m32 in ms:
            p12 = m32[:12]
            where = []
            if m32 in on_disk_set:
                where.append("盘上现值(%s)" % on_disk_set[m32])
            if p12 in head_set:
                where.append("台账链头(%s)" % head_set[p12])
            if not where:
                stale_rows.append((n.get("key"), m32, n.get("since")))
            print("    %-46s %s  %s" % (n.get("key"), m32, ("= " + " / ".join(where)) if where else "★ 陈旧 (既不等于盘上现值, 也不等于台账链头)"))
    print("  ⇒ 陈旧 md5 条数 = %d (涉及 need %d 条)" % (len(stale_rows), len({r[0] for r in stale_rows})))
    for k, v, s in stale_rows:
        print("      %-46s %s  (since %s)" % (k, v, s))

    # ---------- ⑥ SW 台账锚点 §1 entries[] 现状 ----------
    print("\n[6] SW/SW_MD5_BASELINE_LEDGER.md §1 source_ledger.entries[] 现状")
    led = read_text(os.path.join(PROJ, "SW", "SW_MD5_BASELINE_LEDGER.md"))
    m = re.search(r"entries:(.*?)\n\s*hard_protected:", led, re.S)
    if m:
        blk = m.group(1)
        for mm in re.finditer(r"file:\s*(\S+).*?by:\s*(\S+).*?prev_md5:\s*(\w+).*?md5:\s*(\w+)", blk, re.S):
            f, by, prev, cur = mm.groups()
            print("    %-26s by=%-10s prev=%s  登记 md5=%s" % (f, by, prev[:12], cur[:12]))
            print("    %-26s 盘上现值=%s  台账链头=%s  ⇒ 锚点副本落后 %d 跳"
                  % ("", md5_of(os.path.join(PROJ, f))[:12], (heads.get(f, {}).get("head") or "n/a"),
                     1 if md5_of(os.path.join(PROJ, f))[:12] != cur[:12] else 0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
