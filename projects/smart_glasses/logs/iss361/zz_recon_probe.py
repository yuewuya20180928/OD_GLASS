#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-361 侦察脚本 (只读 · 不改任何真源) —— 三集合对账 + 13 件缺口实算。
★ 这是探测用的一次性脚本, 正式判据在 HW/check_fp_truth_coverage_gap.py。
"""
import csv, os, re, sys, json

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
sys.path.insert(0, os.path.join(ROOT, "state"))

# ---- 口径 A: ISS-356 靶子 (照抄 check_fp_truth_baseline.py 的 load_targets 口径)
def load_targets():
    with open(os.path.join(ROOT, "HW", "BOM_v1.csv"), encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    main, chg, total = [], [], []
    for r in rows:
        if r["dnp"] != "必装":
            continue
        if r["type"] in ("NET", "TP"):
            continue
        if r["footprint"] != "待定":
            continue
        total.append(r["ref"])
        if r["board"] == "镜脚主 PCB":
            main.append(r["ref"])
        elif r["board"] == "镜框充电板":
            chg.append(r["ref"])
    return main, chg, total, rows

main_t, chg_t, total_t, bom_rows = load_targets()
bom_by_ref = {r["ref"]: r for r in bom_rows}

# ---- 口径 B: C4 占位脚号 158 (从 state/check_pcb_nets.py 的 netlist_pads 独立复算)
def netlist_placeholder():
    """★独立复算 state/check_pcb_nets.py 的 C4 口径 (同规则, 不共用代码)★"""
    PSEUDO = ("RAIL_", "NET_")
    BOARD_FILTER = "MAIN_PCB"
    PIN_RE = re.compile(r"pin\d+(\+pin\d+)*")
    USBIF_RE = re.compile(r"^(?:[AB](?:1|4|5|6|7|8|9|12)|shield)$")

    def split_node(node):
        node = (node or "").strip()
        if not node:
            return None, None
        m = re.match(r"^([A-Za-z_0-9]+)\s+(.*)$", node)
        if not m:
            return node, None
        return m.group(1), m.group(2).strip()

    def split_names(tail):
        return [p.strip() for p in re.split(r"\+(?=\w)", tail) if p.strip()]

    def is_pad_name(tail):
        if not tail:
            return False
        if PIN_RE.fullmatch(tail):
            return True
        if USBIF_RE.match(tail):
            return True
        toks = [t.strip() for t in tail.split("+") if t.strip()]
        if len(toks) >= 2 and all(USBIF_RE.match(t) for t in toks):
            return True
        return False

    with open(os.path.join(ROOT, "HW", "netlist_v1.csv"), encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    rows = [r for r in rows if (r.get("board") or "MAIN_PCB").strip() == BOARD_FILTER]

    refs = set()
    for r in rows:
        ref = (r.get("ref") or "").strip()
        if ref:
            refs.add(ref)
    real = {x for x in refs if not x.startswith(PSEUDO)}
    for r in rows:
        for k in ("node1", "node2"):
            comp, tail = split_node(r.get(k))
            if not comp or comp in real or comp.startswith(PSEUDO):
                continue
            if tail and PIN_RE.fullmatch(tail):
                real.add(comp)

    terms = {}
    for r in rows:
        net = (r.get("net") or "").strip()
        ref = (r.get("ref") or "").strip()
        if not net:
            continue
        parsed = [split_node(r.get(k)) for k in ("node1", "node2")]
        if (parsed[0][0] == parsed[1][0]
                and parsed[0][1] is None and parsed[1][1] is None):
            continue
        seen = set()
        for comp, tail in parsed:
            if comp is None or comp not in real:
                continue
            d = terms.setdefault(comp, {})
            if tail and is_pad_name(tail):
                for tok in tail.split("+"):
                    tok = tok.strip()
                    key = ("P", int(tok[3:])) if tok.startswith("pin") else ("P", tok)
                    d.setdefault(key, (net, "P"))
                    seen.add(comp)
            elif tail:
                for nm in split_names(tail):
                    d.setdefault(("N", nm, net), (net, "N"))
                    seen.add(comp)
            else:
                d.setdefault(("B", net), (net, "B"))
                seen.add(comp)
        if ref and ref in real and ref not in seen:
            terms.setdefault(ref, {}).setdefault(("B", net), (net, "B"))

    placeholder = {}
    for comp, d in terms.items():
        if not d:
            continue
        if any(k[0] == "P" for k in d):
            continue          # 有真实 pin<N> 脚号 ⇒ 不是占位
        pins = []
        for i, (_k, v) in enumerate(d.items(), start=1):
            if isinstance(_k, str) and "+" in _k:
                parts = [q.strip() for q in _k.split("+") if q.strip()]
                if parts and all(USBIF_RE.match(q) for q in parts):
                    for q in parts:
                        pins.append((q, v[0]))
                    continue
            if isinstance(_k, str) and USBIF_RE.match(_k):
                pins.append((_k, v[0]))
            else:
                pins.append((i, v[0]))
        placeholder[comp] = len([1 for k, _v in pins if isinstance(k, int)])
    return placeholder

ph = netlist_placeholder()
c4 = set(ph)
print("C4 口径实算 =", len(c4))
# 交叉核对: 与 check_pcb_nets.py 实际输出比对
listed = set(x.strip() for x in open(os.path.join(ROOT, "logs/iss361/03_c4_158_refs.txt")) if x.strip())
print("  check_pcb_nets.py 输出 =", len(listed))
print("  两边集合相同?", c4 == listed)
if c4 != listed:
    print("  只在实算:", sorted(c4 - listed)[:10])
    print("  只在输出:", sorted(listed - c4)[:10])

iss356 = set(total_t)
print("ISS-356 靶子 =", len(iss356), "(main %d / chg %d)" % (len(main_t), len(chg_t)))
inter = c4 & iss356
diff = c4 - iss356
print("交集 C4∩ISS356 =", len(inter))
print("差集 C4\\ISS356 =", len(diff))

# ---- 81 件成分归因
tp, dnp, gap = [], [], []
for ref in sorted(diff):
    r = bom_by_ref.get(ref)
    if r is None:
        gap.append((ref, "★不在 BOM★", None))
        continue
    if r["type"] == "TP":
        tp.append(ref)
    elif r["dnp"] == "DNP":
        dnp.append(ref)
    else:
        gap.append((ref, r["type"], r))
print("  TP %d + DNP %d + 缺口 %d = %d" % (len(tp), len(dnp), len(gap), len(tp)+len(dnp)+len(gap)))

# ---- 缺口 13 件: 全字段
print("\n=== 缺口 13 件逐件 ===")
for ref, typ, r in gap:
    r = r or bom_by_ref.get(ref)
    print("%-14s dnp=%-4s type=%-4s board=%-10s fp=%s" % (
        ref, r["dnp"], r["type"], r["board"], r["footprint"]))
    print("               value=%s" % r["value"])
    print("               memo=%s" % (r["memo"][:150] if r["memo"] else ""))

# ---- 脚数 (netlist_v1_pins.csv)
with open(os.path.join(ROOT, "HW", "netlist_v1_pins.csv"), encoding="utf-8") as fh:
    pins = list(csv.DictReader(fh))
cnt = {}
for p in pins:
    cnt[p["ref"]] = cnt.get(p["ref"], 0) + 1
print("\n=== 缺口件脚数 (pins csv) ===")
for ref, typ, r in gap:
    print("  %-14s pins=%s" % (ref, cnt.get(ref, "?")))

# ---- FP_TRUTH 页里有目标 lib:name 的?
fp_text = open(os.path.join(ROOT, "HW", "FP_TRUTH_BASELINE.md"), encoding="utf-8").read()
print("\n=== 缺口件在 FP_TRUTH 页的 lib:name 命中 ===")
for ref, typ, r in gap:
    hits = re.findall(r"`([A-Za-z_0-9]+:[A-Za-z0-9_]+)`", fp_text)
    found = set()
    for line in fp_text.splitlines():
        if ref in line:
            for h in re.findall(r"`([A-Za-z_0-9]+:[A-Za-z0-9_]+)`", line):
                found.add(h)
    print("  %-14s 同名行内 lib:name = %s" % (ref, sorted(found) or "无"))

json.dump({
    "c4": sorted(c4), "iss356": sorted(iss356), "inter": sorted(inter),
    "diff": sorted(diff), "tp": tp, "dnp": dnp,
    "gap": [g[0] for g in gap],
    "gap_detail": {g[0]: {"dnp": g[2]["dnp"], "type": g[2]["type"],
                           "board": g[2]["board"], "fp": g[2]["footprint"],
                           "value": g[2]["value"], "pins": cnt.get(g[0], 0)}
                   for g in gap if g[2]},
    "ph_pins": {k: v for k, v in ph.items()},
}, open(os.path.join(ROOT, "logs/iss361/04_recon.json"), "w", encoding="utf-8"),
   ensure_ascii=False, indent=1)
print("\n[写出] logs/iss361/04_recon.json")
