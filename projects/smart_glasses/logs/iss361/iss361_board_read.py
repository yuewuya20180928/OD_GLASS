#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-361 · 纯 python 板面读取器 (无 pcbnew 依赖) —— 供机器闸与页面生成器共用。
★ 只读 HW/PCB/demo_mainboard.kicad_pcb, 零写入。
★ 本文件是留证脚本 (logs/iss361/), 不是交付物; 交付物是 HW/check_fp_truth_coverage_gap.py
  (它内含同款读取逻辑, 以便闸自足)。

口径 (与 state/check_pcb_nets.py 的 C4 口径完全一致, 但独立实现, 不 import 那个模块):
  · 网表行按 board 列过滤 ⇒ 只留 MAIN_PCB
  · 节点串 "DEV" (bare) ⇒ 占位脚号 (按行序 1..M)
  · 节点串 "DEV pin<N>" ⇒ 真实脚号
  · USB-IF 物理脚名 (A1/A4/.../shield) ⇒ 真实脚号
"""
import csv
import os
import re

PSEUDO = ("RAIL_", "NET_")
BOARD_FILTER = "MAIN_PCB"
PIN_RE = re.compile(r"pin\d+(\+pin\d+)*")
USBIF_RE = re.compile(r"^(?:[AB](?:1|4|5|6|7|8|9|12)|shield)$")


# ---------------------------------------------------------------- 板面读取

def _blocks(text, name):
    out = []
    i = 0
    while True:
        m = re.search(r"\(%s\b" % re.escape(name), text[i:])
        if not m:
            break
        s = i + m.start()
        depth = 0
        j = s
        while j < len(text):
            if text[j] == "(":
                depth += 1
            elif text[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append(text[s:j + 1])
        i = j + 1
    return out


def read_board(path):
    """⇒ {ref: {"libid":str, "value":str, "pads":[(num, net, x, y, w, h)], "fab":(w,h), "bbox":(w,h)}}"""
    text = open(path, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'^\t\(footprint ', text, re.M):
        s = m.start()
        cands = [text.find("\n\t(footprint ", s + 1), text.find("\n\t(net ", s + 1)]
        cands = [c for c in cands if c != -1]
        e = min(cands) if cands else len(text)
        blk = text[s:e]
        rm = re.search(r'\(property "Reference" "([^"]*)"', blk)
        if not rm:
            continue
        ref = rm.group(1)
        vm = re.search(r'\(property "Value" "([^"]*)"', blk)
        libm = re.match(r'\(footprint "([^"]*)"', blk)
        pads = []
        for pb in _blocks(blk, "pad"):
            num = re.search(r'pad\s+"([^"]*)"', pb).group(1)
            at = re.search(r"\(at ([^)]*)\)", pb)
            sz = re.search(r"\(size ([^)]*)\)", pb)
            net = re.search(r'\(net (?:\d+ )?"([^"]*)"\)', pb)
            a = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", at.group(1))] if at else [0, 0]
            s2 = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", sz.group(1))] if sz else [0, 0]
            pads.append((num, net.group(1) if net else "", a[0], a[1], s2[0], s2[1]))
        fab = _layer_bbox(blk, "F.Fab")
        bbox = _layer_bbox(blk, "F.CrtYd")
        out[ref] = {"libid": libm.group(1) if libm else "",
                    "value": vm.group(1) if vm else "",
                    "pads": pads, "fab": fab, "crtyd": bbox}
    return out


def _layer_bbox(blk, layer):
    xs, ys = [], []
    for tag in ("fp_line", "fp_rect"):
        for b in _blocks(blk, tag):
            lm = re.search(r'\(layer "([^"]*)"\)', b)
            if not lm or lm.group(1) != layer:
                continue
            for grp in ("start", "end"):
                m = re.search(r"\(%s ([-\d\.]+) ([-\d\.]+)\)" % grp, b)
                if m:
                    xs.append(float(m.group(1)))
                    ys.append(float(m.group(2)))
    if not xs:
        return (0.0, 0.0)
    return (max(xs) - min(xs), max(ys) - min(ys))


# ---------------------------------------------------------------- 网表 C4 口径

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


def netlist_placeholder(path):
    """⇒ (placeholder {ref: 脚数}, per_ref {ref: [(焊盘号, 网名)]}, notes)"""
    with open(path, encoding="utf-8") as fh:
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
    notes = []
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
                    if key in d and d[key][0] != net:
                        notes.append("%s %s 同时挂 %s 与 %s" % (comp, key[1], d[key][0], net))
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
    for comp, d in terms.items():
        pinnets = {v[0] for k, v in d.items() if k[0] == "P"}
        for k in [k for k in d if k[0] == "B" and k[1] in pinnets]:
            del d[k]
    per_ref, placeholder = {}, {}
    for comp, d in terms.items():
        if not d:
            continue
        if any(k[0] == "P" for k in d):
            pins = sorted(((k[1], v[0]) for k, v in d.items() if k[0] == "P"),
                          key=lambda t: (0, t[0], 0) if isinstance(t[0], int) else (1, str(t[0]), 0))
            nums = [x[0] for x in pins if isinstance(x[0], int)]
            nxt = (max(nums) + 1) if nums else 1
            for k, v in d.items():
                if k[0] != "P":
                    pins.append((nxt, v[0]))
                    nxt += 1
            per_ref[comp] = pins
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
    return placeholder, per_ref, notes


# ---------------------------------------------------------------- BOM 口径

def load_bom(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def iss356_targets(bom_rows):
    """ISS-356 靶子口径: 必装 ∩ 非 NET/TP ∩ footprint=='待定' ⇒ (main, chg, total)"""
    main, chg, total = [], [], []
    for r in bom_rows:
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
    return main, chg, total


def coverage_gap(bom_rows, c4_set):
    """本单缺口口径: 必装 ∩ 非 NET/TP ∩ footprint != '待定' ∩ 在 C4 里"""
    out = []
    for r in bom_rows:
        if r["dnp"] != "必装":
            continue
        if r["type"] in ("NET", "TP"):
            continue
        if r["footprint"] == "待定":
            continue
        if r["ref"] not in c4_set:
            continue
        out.append(r["ref"])
    return sorted(out)
