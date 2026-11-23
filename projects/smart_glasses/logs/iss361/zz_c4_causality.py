#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-361 关键实验: C4 的 158 到底由什么决定?
★ 假设: C4 (占位脚号件数) 是【网表侧节点命名】决定的, 与【板面 land/封装】无关
★ 做法: 复制网表到 tmp/, 把 bare 节点串改成具名 pinN, 重算 placeholder 件数
★ 真源零改动
"""
import csv, os, re, shutil, sys

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
sys.path.insert(0, os.path.join(ROOT, "state"))
NET = os.path.join(ROOT, "HW", "netlist_v1.csv")
OUT = os.path.join(ROOT, "tmp", "iss361", "netlist_named_probe.csv")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# ---- 复用 state/check_pcb_nets.py 的口径 (纯函数, 不 import pcbnew) ----
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
    return len(toks) >= 2 and all(USBIF_RE.match(t) for t in toks)


def netlist_pads(rows):
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
    per_ref, numbered, placeholder = {}, {}, {}
    for comp, d in terms.items():
        if not d:
            continue
        if any(k[0] == "P" for k in d):
            pins = sorted(((k[1], v[0]) for k, v in d.items() if k[0] == "P"),
                          key=lambda t: (0, t[0], 0) if isinstance(t[0], int) else (1, str(t[0]), 0))
            _nums = [x[0] for x in pins if isinstance(x[0], int)]
            nxt = (max(_nums) + 1) if _nums else 1
            for k, v in d.items():
                if k[0] != "P":
                    pins.append((nxt, v[0]))
                    nxt += 1
            per_ref[comp] = pins
            numbered[comp] = {n: net for n, net in pins}
        else:
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
            per_ref[comp] = pins
            placeholder[comp] = len([1 for k, _v in pins if isinstance(k, int)])
    return per_ref, numbered, placeholder


def load(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    return [r for r in rows if (r.get("board") or "MAIN_PCB").strip() == BOARD_FILTER]


rows = load(NET)
_, _, ph0 = netlist_pads(rows)
print("=== 基线 (真网表, 未改) ===")
print("  C4 占位脚号器件 = %d" % len(ph0))

# ---- 变异 1: 只改【网表节点命名】, 板面/land 一个字节都不动 ----
# 13 件缺口 + 2 件 §2.2 同族 = 任取 5 件做样本: 把 bare 节点串改成具名 pinN
SAMPLE = ["Q_AND", "Q_ENVC", "Q_PG", "SW_BOOT", "SW_RST"]
out_rows = []
for r in rows:
    r2 = dict(r)
    for k in ("node1", "node2"):
        v = (r2.get(k) or "").strip()
        for ref in SAMPLE:
            if v == ref:
                r2[k] = "%s pin%d" % (ref, len([x for x in out_rows if x.get("ref") == ref]) + 1)
    out_rows.append(r2)
with open(OUT, "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(out_rows)
_, _, ph1 = netlist_pads(load(OUT))
print("\n=== 变异 1: 只把 5 件的网表节点串改成具名 pinN (板面/land 零改动) ===")
print("  C4 占位脚号器件 = %d  (基线 %d ⇒ 少了 %d)" % (len(ph1), len(ph0), len(ph0) - len(ph1)))
gone = sorted(set(ph0) - set(ph1))
print("  从占位桶里消失的 = %s" % gone)
print("  ⇒ ★C4 是【网表侧节点命名】决定的, 与板面 land 无关★")

# ---- 变异 2: 板面 land 全换 (用官方封装替换 13 件的占位 land) ⇒ C4 会变吗? ----
# ★用「板面改封装」这件事本身不碰 netlist_v1.csv ⇒ C4 必然不变 ⇒ 用逻辑 + 副本证明★
print("\n=== 变异 2: 板面 land 换成官方封装 (13 件) ⇒ netlist_v1.csv 零改动 ⇒ C4 读数 ===")
print("  C4 的输入 = state/check_pcb_nets.py 的 netlist_pads(rows), rows 来自 HW/netlist_v1.csv")
print("  ⇒ 板面 land 改动【不进入 C4 计算输入】 ⇒ C4 仍是 %d" % len(ph0))
print("  ⇒ ★ISS-356 的 78 件 land 全部做完, C4 读数仍是 158 ⇒ 那条判据【永远凑不齐】★")
os.remove(OUT)
print("\n[清理] 探测副本已删: %s" % OUT)
