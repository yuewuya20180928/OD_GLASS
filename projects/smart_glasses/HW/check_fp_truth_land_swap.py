#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-364 · hw-lead · 「板那一趟」S10 换封装真值 机器门禁 (L0~L8)
作者: hw-lead · 2026-11-23 · 交卷给 main / 项目总工

用法:
    python3 HW/check_fp_truth_land_swap.py               # 正常跑 ⇒ rc=0 = 全过
    python3 HW/check_fp_truth_land_swap.py --selftest     # 反向用例自证 ⇒ rc=0 (末行 ALL TESTS PASS)
    python3 HW/check_fp_truth_land_swap.py --json         # 机器可读输出
    python3 HW/check_fp_truth_land_swap.py --root DIR     # 指定项目根 (默认自动定位)

检查项 (内容级, **不挂 md5** —— 沿用 HW/check_fp_truth_coverage_gap.py 的做法: 文档改一个字就重判):
    L0 基准块存在且是合法 JSON (页内 "BEGIN/END ISS364 换封装作业包基准块")
    L1 ★**90 这个数由脚本自己算出来**★:
       读 HW/BOM_v1.csv (ISS-356 靶子口径) + 读 HW/netlist_v1.csv (C4 占位脚号口径)
       + 读 HW/FP_TRUTH_BASELINE.md §2 表 (靶子名单) + 读 HW/PCB/FP_TRUTH_COVERAGE_GAP.md §2 表 (缺口名单)
       ⇒ 算出「靶内 77 + 缺口 13 = 90」⇒ 页里 §1 标题写的 90 / 基准块 counts.target_total
       与脚本实算不等 ⇒ 红
    L2 §1 表 90 件逐件齐全 —— 漏一件即红 + 点名 ref (★多一件也红★)
    L3 每件 12 字段非空 —— ★**几何 Δ / 腿 B 具名脚清单 / 降级方案 三项不许空**★
    L4 给得出的那些: .kicad_mod 真在 KiCad 官方库根下**实测存在** + md5 对得上 (★查文件, 不是只查库目录★)
    L5 ★**几何一致性 (本闸的核心)**★: §1 每件写的「目标焊盘数 / fab 外框 / 中心距」
       == 脚本从该 .kicad_mod 实测出来的值 ⇒ 对不上即红 (★这一条抓的是「台账抄错几何」★)
    L6 证据等级五级白名单 ([官网]/[实测]/[媒体]/[推算]/[0数据]) ⇒ 写 [官方] = 红
    L7 正文无「等原厂回信 / 等供应商确认 / 待外部回复 / 等确认」这类挂起措辞
       (老板 2026-11-12 02:02 政策)
    L8 ★**「换 land 不动 C4、具名脚才动 C4」这条机制在本单里被机器钉住**★:
       ① 基准块 counts 的 158 / 100 / 77 / 81 / 13 / 90 与脚本实算逐项相等
       ② §2.1 表的具名脚数总和 == 90 件的脚数之和 (★脚表 netlist_v1_pins.csv 的 pin 栏实算★)
       ③ §2.1 表 90 件齐全
       ⇒ ⇒ ★**腿 B 漏写, L8 就红** ★

★ 本门禁【不挂 md5】: 判据是内容级 (件数 / 覆盖 / 库文件实存 / md5 / 几何 / 证据等级 / 降级方案 /
  挂起措辞 / 机制读数), 文档改一个字就重判, 不用重锚。

★ **零 pcbnew 依赖**: 本脚本用**纯 python 文本解析**读板面与网表 (口径与 state/check_pcb_nets.py
  的 C4 口径逐条一致, 但独立实现, 不 import 那个需要 pcbnew 的模块) ⇒
  ★**裸 python3 就能跑** (不需要 bash state/pcbnew_py.sh)★

--selftest 反向用例 (每条都自证「真的改到了目标」):
    M1 删掉 §1 表里某一行 (Q_PG)              → 期望 L2 红, 其余仍绿
    M2 把某行目标焊盘数改成错的              → 期望 L5 红, 其余仍绿
    M3 把某行 .kicad_mod md5 改错             → 期望 L4 红, 其余仍绿
    M4 清空某行降级方案                       → 期望 L3 红, 其余仍绿
    M5 把某行证据等级写成 [官方]              → 期望 L6 红, 其余仍绿
    M6 正文塞一句「等原厂回信」                → 期望 L7 红, 其余仍绿
    M7 篡改 §1 标题里的 90 这个数              → 期望 L1 红, 其余仍绿
    M8 删掉 §2.1 表里某件的具名脚              → 期望 L8 红, 其余仍绿

★ 反向用例的「真的改到了目标」自证 = 三件事同时成立:
    ① 变异确实落到盘上副本里 (变异串在副本里 count>=1, 变异前原串消失)
    ② 期望变红的那一条 check 真的红了
    ③ 其余 check 仍然绿 (证明红的是目标那一条, 不是随便塌一条)
★ 沙盒: 副本落**项目盘 tmp/** (不落 /tmp, ★2026-11-23 04:4x 实测系统 /tmp 配额已满·写 /tmp 会让闸拿到假读数★)
"""

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sys

DOC_REL = os.path.join("HW", "PCB", "FP_TRUTH_LAND_SWAP_WORKPACKET.md")
BLOCK_BEGIN = "<!-- BEGIN ISS364 换封装作业包基准块 -->"
BLOCK_END = "<!-- END ISS364 换封装作业包基准块 -->"

# 证据等级白名单 (五级固定, 写死的) —— ★写 [官方] = 红★
ALLOWED_EVIDENCE = {"[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]"}

# 挂起措辞黑名单 (老板 2026-11-12 02:02 政策)
FORBIDDEN_PHRASES = (
    "等回复",
    "等原厂回信",
    "待供应商确认",
    "待外部回复",
    "等原厂",
    "等确认",
)

LIBROOT_DEFAULT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"

# ---------------------------------------------------------------- 真源口径 (纯 python)

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


def is_pad_name(tail):
    """★真实焊盘号判定: pin<N> 或 USB-IF 物理脚名 (与 state/check_pcb_nets.py 同口径)★"""
    if not tail:
        return False
    if re.fullmatch(r"pin\d+(\+pin\d+)*", tail):
        return True
    if USBIF_RE.match(tail):
        return True
    toks = [t.strip() for t in tail.split("+") if t.strip()]
    return len(toks) >= 2 and all(USBIF_RE.match(t) for t in toks)


def netlist_placeholder(path):
    """★C4 占位脚号口径 (与 state/check_pcb_nets.py 的 netlist_pads 同规则, 独立实现)★
    ⇒ placeholder {ref: 焊盘数}"""
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
                for nm in [p.strip() for p in re.split(r"\+(?=\w)", tail) if p.strip()]:
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
    placeholder = {}
    for comp, d in terms.items():
        if not d:
            continue
        if any(k[0] == "P" for k in d):
            continue
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


def load_bom(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def iss356_targets(bom_rows):
    """ISS-356 靶子口径: 必装 ∩ 非 NET/TP ∩ footprint=='待定'"""
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
    """缺口口径: 必装 ∩ 非 NET/TP ∩ footprint!='待定' ∩ 在 C4 里"""
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


def pins_table_counts(path):
    """★脚表 netlist_v1_pins.csv ⇒ {ref: 脚数} (★按表头名取 'pin' 栏, 不写死列号★)★"""
    with open(path, encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        hdr = rd.fieldnames or []
        if "ref" not in hdr or "pin" not in hdr:
            return {}
        out = {}
        for r in rd:
            ref = (r.get("ref") or "").strip()
            pin = (r.get("pin") or "").strip()
            if ref and pin:
                out.setdefault(ref, set()).add(pin)
    return {k: len(v) for k, v in out.items()}


def read_board_refs(path):
    """★纯文本读板面 ⇒ {ref: [焊盘号...]} (零 pcbnew)★"""
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
        out[rm.group(1)] = re.findall(r'\(pad\s+"([^"]*)"', blk)
    return out


# ---------------------------------------------------------------- .kicad_mod 实测

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


def read_mod_geom(libroot, libname):
    """★从 .kicad_mod 实测: 焊盘数 / fab 外框 / 中心距★ ⇒ None 或 dict"""
    if ":" not in libname:
        return None
    lib, nm = libname.split(":", 1)
    p = os.path.join(libroot, "%s.pretty" % lib, "%s.kicad_mod" % nm)
    if not os.path.isfile(p):
        return None
    text = open(p, encoding="utf-8").read()
    pads = []
    for pb in _blocks(text, "pad"):
        at = re.search(r"\(at ([^)]*)\)", pb)
        a = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", at.group(1))] if at else [0, 0]
        pads.append((a[0], a[1]))
    d = 0.0
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            d = max(d, ((pads[i][0] - pads[j][0]) ** 2 + (pads[i][1] - pads[j][1]) ** 2) ** 0.5)
    fab = _layer_bbox(text, "F.Fab")
    return {"pads_n": len(pads),
            "fab_w": round(fab[0], 2), "fab_h": round(fab[1], 2),
            "center": round(d, 3),
            "md5": hashlib.md5(open(p, "rb").read()).hexdigest(),
            "path": "%s.pretty/%s.kicad_mod" % (lib, nm)}


# ---------------------------------------------------------------- 页面解析 helpers

def find_root():
    here = os.path.dirname(os.path.abspath(__file__))
    cur = here
    for _ in range(6):
        if os.path.isdir(os.path.join(cur, "HW")) and os.path.isdir(os.path.join(cur, "state")):
            return cur
        cur = os.path.dirname(cur)
    return here


def parse_block(text):
    if BLOCK_BEGIN not in text or BLOCK_END not in text:
        return None
    blob = text.split(BLOCK_BEGIN, 1)[1].split(BLOCK_END, 1)[0].strip()
    blob = re.sub(r"^```json\s*", "", blob)
    blob = re.sub(r"```\s*$", "", blob)
    try:
        return json.loads(blob)
    except Exception:
        return None


def find_table_span(lines, must_have):
    """★按表头内容定位一张表 ⇒ (head, rows, 首行号, 末行号)★"""
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s.startswith("|"):
            continue
        if not all(m in s for m in must_have):
            continue
        head = [c.strip() for c in s.strip("|").split("|")]
        rows = []
        idxs = []
        j = i + 1
        while j < len(lines):
            r2 = lines[j].strip()
            if not r2.startswith("|"):
                break
            if set(r2.replace("|", "").replace(" ", "")) <= set("-:"):
                j += 1
                continue
            rows.append([c.strip() for c in r2.strip("|").split("|")])
            idxs.append(j)
            j += 1
        return head, rows, i, (idxs[-1] + 1 if idxs else i + 1), idxs
    return None, None, None, None, None


def find_table(lines, must_have):
    """★按表头内容定位一张表 ⇒ (head, rows)★ —— 表头 must_have 的每个串都要出现在表头行里"""
    head, rows, _i, _j, _idx = find_table_span(lines, must_have)
    return head, rows


def cell(row, head, key):
    kk = key.replace("`", "")
    for k, c in enumerate(head):
        if c.replace("`", "") == kk:
            return row[k] if k < len(row) else ""
    for k, c in enumerate(head):
        if kk and kk in c.replace("`", ""):
            return row[k] if k < len(row) else ""
    return ""


def page_refs_of_section2(root):
    """★读 HW/FP_TRUTH_BASELINE.md §2 表的 ref 名单 (靶子)★"""
    path = os.path.join(root, "HW", "FP_TRUTH_BASELINE.md")
    lines = open(path, encoding="utf-8").read().splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith("## §2 逐 ref 表"))
    j = next(k for k, l in enumerate(lines) if k > i and l.startswith("### §2.1"))
    out = []
    for l in lines[i:j]:
        s = l.strip()
        if not s.startswith("| `"):
            continue
        out.append(s.strip("|").split("|")[0].strip().strip("`"))
    return [r for r in out if r]


def page_refs_of_charge(root):
    """★读 HW/FP_TRUTH_BASELINE.md §4.1 表的 ref 名单 (镜框充电板 22 件)★"""
    path = os.path.join(root, "HW", "FP_TRUTH_BASELINE.md")
    lines = open(path, encoding="utf-8").read().splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith("### §4.1"))
    j = next(k for k, l in enumerate(lines) if k > i and l.startswith("### §4.2"))
    out = []
    for l in lines[i:j]:
        s = l.strip()
        if not s.startswith("| `"):
            continue
        out.append(s.strip("|").split("|")[0].strip().strip("`"))
    return [r for r in out if r]


def page_refs_of_gap(root):
    """★读 HW/PCB/FP_TRUTH_COVERAGE_GAP.md §2 表的 ref 名单 (缺口)★"""
    path = os.path.join(root, "HW", "PCB", "FP_TRUTH_COVERAGE_GAP.md")
    lines = open(path, encoding="utf-8").read().splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith("## §2 "))
    j = next(k for k, l in enumerate(lines) if k > i and l.startswith("## §3 "))
    out = []
    for l in lines[i:j]:
        s = l.strip()
        if not s.startswith("| `"):
            continue
        out.append(s.strip("|").split("|")[0].strip().strip("`"))
    return [r for r in out if r]


# ---------------------------------------------------------------- 主检查

def check(doc_text, root, libroot=LIBROOT_DEFAULT):
    results = {}
    facts = {}

    bom_rows = load_bom(os.path.join(root, "HW", "BOM_v1.csv"))
    main_t, chg_t, total_t = iss356_targets(bom_rows)
    ph = netlist_placeholder(os.path.join(root, "HW", "netlist_v1.csv"))
    board = read_board_refs(os.path.join(root, "HW", "PCB", "demo_mainboard.kicad_pcb"))
    c4 = set(ph)
    iss = set(total_t)
    diff = c4 - iss
    gap = coverage_gap(bom_rows, c4)

    # ★靶子名单: 从【台账页】读 (不只是 BOM) ⇒ 与 BOM 实算交叉核对
    page_target = set(page_refs_of_section2(root))
    page_charge = set(page_refs_of_charge(root))
    page_gap = set(page_refs_of_gap(root))
    inter = c4 & iss
    target_90 = sorted(inter) + sorted(page_gap)

    facts["c4_total"] = len(c4)
    facts["iss356_total"] = len(iss)
    facts["iss356_main"] = len(main_t)
    facts["iss356_chg"] = len(chg_t)
    facts["inter_total"] = len(inter)
    facts["diff_total"] = len(diff)
    facts["gap_total"] = len(gap)
    facts["board_footprints"] = len(board)
    facts["target_total"] = len(target_90)
    facts["page_target_rows"] = len(page_target)
    facts["page_gap_rows"] = len(page_gap)

    # ---- L0 基准块
    block = parse_block(doc_text)
    results["L0"] = {"ok": block is not None,
                     "detail": "基准块存在且是合法 JSON" if block is not None
                     else "页内缺 BEGIN/END 基准块或 JSON 非法"}
    if block is None:
        for c in ("L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8"):
            results[c] = {"ok": False, "detail": "基准块不可用 ⇒ 连带判红"}
        return results, facts

    lines = doc_text.splitlines()

    # ---- L1 90 这个数由脚本自己算出来
    l1_bad = []
    computed = len(target_90)
    counts = block.get("counts", {})
    if counts.get("target_total") != computed:
        l1_bad.append("基准块 counts.target_total: 基准块 %s vs 脚本实算 %d"
                      % (counts.get("target_total"), computed))
    m = re.search(r"##\s*§1\s*逐件\s*(\d+)\s*行表", doc_text)
    if not m:
        l1_bad.append("页内缺 §1 标题 (带件数的)")
    elif int(m.group(1)) != computed:
        l1_bad.append("§1 标题写 %s 件 ⇒ 脚本实算 %d 件 (靶内 %d + 缺口 %d)"
                      % (m.group(1), computed, len(inter), len(page_gap)))
    if len(inter) != computed - len(page_gap):
        l1_bad.append("脚本自算不自洽: 靶内 %d + 缺口 %d != %d" % (len(inter), len(page_gap), computed))
    # ★台账页的名单与 BOM 实算必须逐件相等 (★不然「90」就是两套口径拼出来的数★)
    if page_target and page_target != set(main_t):
        l1_bad.append("台账页 §2 的镜脚主 PCB 靶子名单 (%d 件) 与 BOM 实算 (%d 件) 不相等: 差 %s / %s"
                      % (len(page_target), len(main_t), sorted(page_target - set(main_t))[:3],
                         sorted(set(main_t) - page_target)[:3]))
    if page_charge and page_charge != set(chg_t):
        l1_bad.append("台账页 §4.1 的镜框充电板名单 (%d 件) 与 BOM 实算 (%d 件) 不相等: 差 %s / %s"
                      % (len(page_charge), len(chg_t), sorted(page_charge - set(chg_t))[:3],
                         sorted(set(chg_t) - page_charge)[:3]))
    if page_gap and set(page_gap) != set(gap):
        l1_bad.append("缺口页 §2 的缺口名单 (%d 件) 与 BOM 实算的缺口 (%d 件) 不相等: 差 %s / %s"
                      % (len(page_gap), len(gap), sorted(set(page_gap) - set(gap))[:3],
                         sorted(set(gap) - set(page_gap))[:3]))
    results["L1"] = {"ok": not l1_bad,
                     "detail": "90 = 靶内 %d + 缺口 %d = %d (★脚本实算·页里写的与实算一致★)"
                     % (len(inter), len(page_gap), computed)
                     if not l1_bad else "; ".join(l1_bad[:8])}

    # ---- L2 / L3 / L4 / L5 / L6: §1 表
    head1, rows1 = find_table(lines, ["现占位几何", "目标几何", "几何 Δ", "降级方案"])
    sec1_refs = []
    if head1 is None:
        results["L2"] = {"ok": False, "detail": "页内缺 §1 逐件表"}
        results["L3"] = {"ok": False, "detail": "页内缺 §1 逐件表"}
        results["L4"] = {"ok": False, "detail": "页内缺 §1 逐件表"}
        results["L5"] = {"ok": False, "detail": "页内缺 §1 逐件表"}
        results["L6"] = {"ok": False, "detail": "页内缺 §1 逐件表"}
    else:
        l2_bad = []
        l3_bad = []
        l4_bad = []
        l5_bad = []
        l6_bad = []
        n_lib = 0
        for r in rows1:
            ref = cell(r, head1, "ref").strip("`").strip()
            if not ref:
                continue
            sec1_refs.append(ref)
        want = set(target_90)
        got = set(sec1_refs)
        for ref in sorted(want - got):
            l2_bad.append("§1 缺 ref: %s" % ref)
        for ref in sorted(got - want):
            l2_bad.append("§1 多出实算之外的 ref: %s" % ref)
        if len(sec1_refs) != len(got):
            l2_bad.append("§1 有重复 ref (行数 %d / 去重 %d)" % (len(sec1_refs), len(got)))
        results["L2"] = {"ok": not l2_bad,
                         "detail": "§1 逐件齐全 (%d/%d)" % (len(got & want), len(want))
                         if not l2_bad else "; ".join(l2_bad[:8])}

        for r in rows1:
            ref = cell(r, head1, "ref").strip("`").strip()
            if not ref:
                continue
            vals = {c: cell(r, head1, c) for c in head1}
            empties = [c for c, v in vals.items() if not v.strip()]
            if empties:
                l3_bad.append("%s: 空字段 %s" % (ref, empties))
            for must in ("几何 Δ", "腿 B 具名脚清单", "降级方案"):
                key = [c for c in head1 if must in c.replace("`", "")]
                if key and not vals[key[0]].strip():
                    l3_bad.append("%s: %s 栏空" % (ref, must))
            # L4 库文件 + md5
            tgt = cell(r, head1, "目标 lib:name").strip("`").strip()
            pm = cell(r, head1, ".kicad_mod 实存路径 + md5")
            if ":" in tgt:
                n_lib += 1
                if not pm.strip():
                    l4_bad.append("%s: 库文件实存路径 + md5 栏空" % ref)
                else:
                    g = read_mod_geom(libroot, tgt)
                    if g is None:
                        l4_bad.append("%s: .kicad_mod 不在盘: %s" % (ref, tgt))
                    else:
                        mm = re.search(r"md5\s+`?([0-9a-f]{32})`?", pm)
                        if not mm:
                            l4_bad.append("%s: 路径栏里没有 md5" % ref)
                        elif mm.group(1) != g["md5"]:
                            l4_bad.append("%s: md5 不符 (页写 %s / 实 %s)"
                                          % (ref, mm.group(1)[:8], g["md5"][:8]))
            # L5 几何一致性
            tcell = cell(r, head1, "目标几何")
            g = read_mod_geom(libroot, tgt) if ":" in tgt else None
            if g is None:
                l5_bad.append("%s: 目标几何无法实测 (lib:name=%r)" % (ref, tgt))
            else:
                mn = re.search(r"焊盘数\s*(\d+)", tcell)
                mf = re.search(r"fab 外框\s*([\d.]+)×([\d.]+)", tcell)
                mc = re.search(r"中心距\s*([\d.]+)", tcell)
                if not mn or not mf or not mc:
                    l5_bad.append("%s: 目标几何栏解析不出来: %r" % (ref, tcell[:60]))
                else:
                    if int(mn.group(1)) != g["pads_n"]:
                        l5_bad.append("%s: 目标焊盘数 页写 %s vs 实测 %d"
                                      % (ref, mn.group(1), g["pads_n"]))
                    if (float(mf.group(1)), float(mf.group(2))) != (g["fab_w"], g["fab_h"]):
                        l5_bad.append("%s: 目标 fab 外框 页写 %s×%s vs 实测 %.2f×%.2f"
                                      % (ref, mf.group(1), mf.group(2), g["fab_w"], g["fab_h"]))
                    if abs(float(mc.group(1)) - g["center"]) > 1e-6:
                        l5_bad.append("%s: 目标中心距 页写 %s vs 实测 %.3f"
                                      % (ref, mc.group(1), g["center"]))
            # L6 证据等级
            ev = cell(r, head1, "证据等级")
            if not ev.strip():
                l6_bad.append("证据等级空: %s" % ref)
            else:
                tags = set(re.findall(r"\[[^\[\]]+\]", ev))
                if not tags:
                    l6_bad.append("证据等级无标签: %s" % ref)
                else:
                    bad = tags - ALLOWED_EVIDENCE
                    if bad:
                        l6_bad.append("证据等级非法 %s: %s" % (sorted(bad), ref))
        results["L3"] = {"ok": not l3_bad,
                         "detail": "%d 件 × 12 字段全非空 (几何 Δ / 具名脚清单 / 降级方案 三项不许空)"
                         % len(sec1_refs) if not l3_bad else "; ".join(l3_bad[:8])}
        results["L4"] = {"ok": not l4_bad,
                         "detail": "%d 处 lib:name 的 .kicad_mod 全部实测在盘 + md5 一致" % n_lib
                         if not l4_bad else "; ".join(l4_bad[:8])}
        results["L5"] = {"ok": not l5_bad,
                         "detail": "%d 件的目标焊盘数 / fab 外框 / 中心距 == 脚本从 .kicad_mod 实测"
                         % len(sec1_refs) if not l5_bad else "; ".join(l5_bad[:8])}
        results["L6"] = {"ok": not l6_bad,
                         "detail": "%d 行证据等级全 ∈ 五级白名单 (无 [官方])" % len(sec1_refs)
                         if not l6_bad else "; ".join(l6_bad[:8])}

    # ---- L7 挂起措辞
    l7_bad = []
    for ph_ in FORBIDDEN_PHRASES:
        if ph_ in doc_text:
            l7_bad.append("出现挂起措辞: %s (×%d)" % (ph_, doc_text.count(ph_)))
    results["L7"] = {"ok": not l7_bad,
                     "detail": "正文无「等回复/等原厂回信/待供应商确认/待外部回复/等原厂/等确认」类挂起措辞"
                     if not l7_bad else "; ".join(l7_bad)}

    # ---- L8 机制钉住
    l8_bad = []
    want_counts = {"c4_total": len(c4), "iss356_total": len(iss),
                    "inter_total": len(inter), "diff_total": len(diff),
                    "gap_total": len(gap), "target_total": len(target_90)}
    for kk, vv in want_counts.items():
        if counts.get(kk) != vv:
            l8_bad.append("基准块 counts.%s: %s vs 实算 %d" % (kk, counts.get(kk), vv))
    sb = block.get("sandbox", {})
    for kk, vv in (("legA_delta_c4", 0),):
        if sb.get(kk) != vv:
            l8_bad.append("基准块 sandbox.%s: %s vs 实算 %s (★换 land 不动 C4★)"
                          % (kk, sb.get(kk), vv))
    if sb.get("legB_delta_c4") != -len(target_90):
        l8_bad.append("基准块 sandbox.legB_delta_c4: %s vs 实算 %d (★具名脚才动 C4★)"
                      % (sb.get("legB_delta_c4"), -len(target_90)))
    if sb.get("s4_legA_legB_k3b_c4") != len(c4) - len(target_90):
        l8_bad.append("基准块 sandbox.s4_legA_legB_k3b_c4: %s vs 实算 %d"
                      % (sb.get("s4_legA_legB_k3b_c4"), len(c4) - len(target_90)))
    # §2.1 表: 90 件齐全 + 具名脚数总和
    head2, rows2 = find_table(lines, ["具名脚数 (本件)", "bare 节点串"])
    if head2 is None:
        l8_bad.append("页内缺 §2.1 腿 B 逐件表 (具名脚数 / bare 节点串)")
        sec2_refs = []
        tot = 0
    else:
        sec2_refs = []
        tot = 0
        for r in rows2:
            ref = cell(r, head2, "ref").strip("`").strip()
            if not ref:
                continue
            sec2_refs.append(ref)
            v = cell(r, head2, "具名脚数 (本件)")
            if v.strip().isdigit():
                tot += int(v.strip())
            else:
                l8_bad.append("%s: §2.1 具名脚数栏不是整数: %r" % (ref, v))
        for ref in sorted(set(target_90) - set(sec2_refs)):
            l8_bad.append("§2.1 缺 ref: %s" % ref)
        for ref in sorted(set(sec2_refs) - set(target_90)):
            l8_bad.append("§2.1 多出实算之外的 ref: %s" % ref)
        # 脚表实算的脚数之和
        ptc = pins_table_counts(os.path.join(root, "HW", "netlist_v1_pins.csv"))
        want_sum = sum(ptc.get(ref, 0) for ref in target_90)
        if tot != want_sum:
            l8_bad.append("§2.1 具名脚数总和 %d != 脚表实算 %d (★腿 B 漏写 ⇒ 这里红★)"
                          % (tot, want_sum))
    facts["legb_pin_sum"] = tot
    facts["legb_pin_sum_want"] = sum(pins_table_counts(
        os.path.join(root, "HW", "netlist_v1_pins.csv")).get(ref, 0) for ref in target_90)
    results["L8"] = {"ok": not l8_bad,
                     "detail": "机制钉住: 158/100/77/81/13/90 与脚本实算一致 + 腿A ΔC4=%s + "
                                "腿B ΔC4=%s + §2.1 具名脚数总和 %d == 脚表实算 %d"
                     % (sb.get("legA_delta_c4"), sb.get("legB_delta_c4"), tot,
                        facts["legb_pin_sum_want"])
                     if not l8_bad else "; ".join(l8_bad[:8])}
    return results, facts


def print_report(results, facts, as_json=False):
    if as_json:
        print(json.dumps({"ok": all(v["ok"] for v in results.values()),
                          "results": results, "facts": facts}, ensure_ascii=False, indent=1))
        return
    print("【ISS-364 换封装作业包闸】")
    for cid in ("L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8"):
        r = results[cid]
        print("  [%s] %s :: %s" % ("PASS" if r["ok"] else "FAIL", cid, r["detail"]))
    print("  事实: C4=%s ISS356=%s (main %s / chg %s) 交集=%s 差集=%s 缺口=%s | 板面封装=%s | "
          "本单对象=%s | 具名脚总和=%s (脚表实算 %s)"
          % (facts.get("c4_total"), facts.get("iss356_total"), facts.get("iss356_main"),
             facts.get("iss356_chg"), facts.get("inter_total"), facts.get("diff_total"),
             facts.get("gap_total"), facts.get("board_footprints"),
             facts.get("target_total"), facts.get("legb_pin_sum"),
             facts.get("legb_pin_sum_want")))


# ---------------------------------------------------------------- selftest

def _mutate_row(text, ref, table_must, colmut=None, drop=False):
    """在【指定表内】定位 ref 那一行并做一次变异 ⇒ (新文本, 原行, 新行)
    ★表作用域: 同一个 ref 在文档里可能出现多次 (例 §1 与 §2.1) ⇒ 必须限定在目标表内★
    ★drop=True 时必须真删行 (不能留空行 ⇒ 空行会把表截断, 后续行全丢)★"""
    lines = text.splitlines()
    head, rows, _i, _j, idxs = find_table_span(lines, table_must)
    if head is None or not idxs:
        return None, None, None
    idx = None
    for k, r in enumerate(rows):
        if r and r[0].strip("`").strip() == ref:
            idx = idxs[k]
            break
    if idx is None:
        return None, None, None
    old = lines[idx]
    if drop:
        lines.pop(idx)
        new = ""
    else:
        cells = [c.strip() for c in old.strip("|").split("|")]
        cells = colmut(head, cells)
        new = "| " + " | ".join(cells) + " |"
        lines[idx] = new
    return "\n".join(lines), old, new


def selftest(root):
    doc_path = os.path.join(root, DOC_REL)
    if not os.path.isfile(doc_path):
        print("[FAIL] 找不到 %s" % doc_path)
        return 2
    orig = open(doc_path, encoding="utf-8").read()
    sandbox = os.path.join(root, "tmp", "iss364_selftest")
    if os.path.isdir(sandbox):
        shutil.rmtree(sandbox)
    os.makedirs(sandbox, exist_ok=True)
    cases = []

    # ---- M1 删掉 §1 里 Q_PG 那一行 ⇒ L2 红
    t, old, _ = _mutate_row(orig, "Q_PG", ["现占位几何", "目标几何", "降级方案"], drop=True)
    if t is None:
        print("[FAIL] M1 找不到 §1 Q_PG 行")
        return 2
    cases.append(("M1", "删 §1 一行 (Q_PG) ⇒ L2 红", "L2", orig, t, "§1"))

    # ---- M2 把某行目标焊盘数改成错的 ⇒ L5 红 (取 Q_ENVC 行)
    def mut_pads(head, cells):
        for k, c in enumerate(head):
            if "目标几何" in c.replace("`", ""):
                cells[k] = cells[k].replace("焊盘数 3", "焊盘数 9")
        return cells
    t, old, new = _mutate_row(orig, "Q_ENVC", ["现占位几何", "目标几何", "降级方案"], mut_pads)
    if t is None or old == new:
        print("[FAIL] M2 找不到 §1 Q_ENVC 行或变异没命中")
        return 2
    cases.append(("M2", "改目标焊盘数 ⇒ L5 红", "L5", orig, t, "焊盘数 9"))

    # ---- M3 把某行 .kicad_mod md5 改错 ⇒ L4 红 (Q_ENVC 行, SOT-23 的 md5)
    def mut_md5(head, cells):
        for k, c in enumerate(head):
            if ".kicad_mod" in c.replace("`", ""):
                cells[k] = re.sub(r"md5\s+`[0-9a-f]{32}`",
                                  "md5 `deadbeefdeadbeefdeadbeefdeadbeef`", cells[k])
        return cells
    t, old, new = _mutate_row(orig, "Q_ENVC", ["现占位几何", "目标几何", "降级方案"], mut_md5)
    if t is None or old == new:
        print("[FAIL] M3 找不到 §1 Q_ENVC 行或变异没命中")
        return 2
    cases.append(("M3", "改 md5 ⇒ L4 红", "L4", orig, t, "deadbeefdeadbeefdeadbeefdeadbeef"))

    # ---- M4 清空某行降级方案 ⇒ L3 红
    def mut_fb(head, cells):
        for k, c in enumerate(head):
            if c.replace("`", "") == "降级方案":
                cells[k] = "  "
        return cells
    t, old, new = _mutate_row(orig, "Q_ENVC", ["现占位几何", "目标几何", "降级方案"], mut_fb)
    if t is None or old == new:
        print("[FAIL] M4 找不到 §1 Q_ENVC 行或变异没命中")
        return 2
    cases.append(("M4", "清空降级方案 ⇒ L3 红", "L3", orig, t, None))

    # ---- M5 把某行证据等级写成 [官方] ⇒ L6 红
    def mut_ev(head, cells):
        for k, c in enumerate(head):
            if c.replace("`", "") == "证据等级":
                cells[k] = "[官方]"
        return cells
    t, old, new = _mutate_row(orig, "Q_ENVC", ["现占位几何", "目标几何", "降级方案"], mut_ev)
    if t is None or old == new:
        print("[FAIL] M5 找不到 §1 Q_ENVC 行或变异没命中")
        return 2
    cases.append(("M5", "证据等级写成 [官方] ⇒ L6 红", "L6", orig, t, "[官方]"))

    # ---- M6 正文塞「等原厂回信」⇒ L7 红
    first_line = orig.split("\n", 1)[0]
    if not first_line.startswith("# "):
        print("[FAIL] M6 首行不是标题")
        return 2
    t = "等原厂回信\n\n" + orig
    cases.append(("M6", "正文塞「等原厂回信」⇒ L7 红", "L7", orig, t, "等原厂回信"))

    # ---- M7 篡改 §1 标题里的 90 这个数 ⇒ L1 红
    m7 = re.search(r"##\s*§1\s*逐件\s*(\d+)\s*行表", orig)
    if not m7:
        print("[FAIL] M7 找不到 §1 标题")
        return 2
    old7 = m7.group(0)
    new7 = re.sub(r"(逐件\s*)(\d+)(\s*行表)",
                  lambda mm: "%s%d%s" % (mm.group(1), int(mm.group(2)) - 1, mm.group(3)),
                  old7, count=1)
    t = orig.replace(old7, new7, 1)
    cases.append(("M7", "篡改 §1 的 90 这个数 ⇒ L1 红", "L1", orig, t, new7))

    # ---- M8 删掉 §2.1 里某件的具名脚 ⇒ L8 红
    t, old, _ = _mutate_row(orig, "R_PU_BOOT_N", ["具名脚数 (本件)", "bare 节点串"], drop=True)
    if t is None:
        print("[FAIL] M8 找不到 §2.1 R_PU_BOOT_N 行")
        return 2
    cases.append(("M8", "删 §2.1 某件的具名脚 ⇒ L8 红", "L8", orig, t, "§2.1"))

    all_ok = True
    for cid, desc, expect_red, o, n, probe in cases:
        if n == o:
            print("[FAIL] %s 变异没落到副本上 (串没命中) ⇒ 不能证明红的是目标那一条" % cid)
            all_ok = False
            continue
        # ★探针自证: 变异串必须【在副本里 且 不在原文档里】⇒ 证明"真的改到了目标"★
        if probe is None:
            if n == o:
                print("[FAIL] %s 变异无效" % cid)
                all_ok = False
                continue
        elif probe == "§1" or probe == "§2.1":
            # 表作用域探针: 目标表里该 ref 的行必须消失
            lines = n.splitlines()
            head, rows = find_table(lines, (["现占位几何", "目标几何", "降级方案"]
                                            if probe == "§1"
                                            else ["具名脚数 (本件)", "bare 节点串"]))
            if head is None or any(r[0].strip("`").strip() ==
                                   ("Q_PG" if probe == "§1" else "R_PU_BOOT_N") for r in rows):
                print("[FAIL] %s 目标表里该行仍在 ⇒ 变异没生效" % cid)
                all_ok = False
                continue
        else:
            if probe not in n:
                print("[FAIL] %s 探针串不在副本里 ⇒ 变异没生效" % cid)
                all_ok = False
                continue
            if probe in o:
                print("[FAIL] %s 探针串本来就在原文档里 ⇒ 变异无效" % cid)
                all_ok = False
                continue
        cp = os.path.join(sandbox, "FP_TRUTH_LAND_SWAP_%s.md" % cid)
        with open(cp, "w", encoding="utf-8") as fh:
            fh.write(n)
        res, _ = check(n, root)
        reds = sorted(k for k, v in res.items() if not v["ok"])
        ok = (reds == [expect_red])
        print("  [%s] %s :: 期望红 %s ⇒ 实得红 %s :: %s"
              % ("PASS" if ok else "FAIL", cid, expect_red, reds or "无",
                 res.get(expect_red, {}).get("detail", "")[:110]))
        if not ok:
            all_ok = False
    shutil.rmtree(sandbox, ignore_errors=True)
    if all_ok:
        print("SELFTEST %d/%d 全过 (每条都自证「红的是目标那一条, 其余仍绿」)" % (len(cases), len(cases)))
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST 失败 ⇒ 闸不可信")
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", default=None)
    ap.add_argument("--doc", default=None)
    ap.add_argument("--libroot", default=LIBROOT_DEFAULT)
    args = ap.parse_args()

    root = args.root or find_root()
    if args.selftest:
        return selftest(root)

    doc_path = args.doc or os.path.join(root, DOC_REL)
    if not os.path.isfile(doc_path):
        print("[FAIL] 找不到 %s" % doc_path)
        return 1
    text = open(doc_path, encoding="utf-8").read()
    results, facts = check(text, root, args.libroot)
    print_report(results, facts, as_json=args.json)
    bad = [k for k, v in results.items() if not v["ok"]]
    if bad:
        print("RED: %s" % ",".join(bad))
        return 1
    print("ALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
