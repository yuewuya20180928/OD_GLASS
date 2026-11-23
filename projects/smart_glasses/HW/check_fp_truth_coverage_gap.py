#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-361 · hw-lead · 「板那一趟」封装真值覆盖缺口 机器门禁 (G0~G7)
作者: hw-lead · 2026-11-23 · 交卷给 main / 项目总工

用法:
    python3 HW/check_fp_truth_coverage_gap.py               # 正常跑 ⇒ rc=0 = 全过
    python3 HW/check_fp_truth_coverage_gap.py --selftest     # 反向用例自证 ⇒ rc=0 (末行 ALL TESTS PASS)
    python3 HW/check_fp_truth_coverage_gap.py --json         # 机器可读输出
    python3 HW/check_fp_truth_coverage_gap.py --root DIR     # 指定项目根 (默认自动定位)

检查项 (内容级, **不挂 md5** —— 沿用 HW/check_fp_truth_baseline.py 的做法: 文档改一个字就重判):
    G0 基准块存在且是合法 JSON (页内 "BEGIN/END ISS361 封装真值覆盖缺口基准块")
    G1 §1 三集合的件数自洽 —— ★**三个数字 (158 / 100 / 81) 必须由本脚本自己跑出来**★:
       读 HW/BOM_v1.csv (ISS-356 靶子口径) + 读 HW/netlist_v1.csv (C4 占位脚号口径)
       + 读 HW/PCB/demo_mainboard.kicad_pcb (板面 186 封装) ⇒
       页里 §1 写的三个数字 / 三份名单 / 三集合关系 与脚本实算逐项一致
    G2 缺口 13 件逐件齐全 —— 从 BOM 实算「必装 ∩ 非 NET/TP ∩ footprint!='待定' ∩ 在 C4 里」
       ⇒ 算出应当 13 件, 页里 §2 必须逐件都在 (漏一件即红 + 点名 ref)
    G3 每件的目标 lib:name 栏非空 —— ★要么给 lib:name + 实存路径 + md5, 要么写 [0数据] + 非空降级方案★
       ⇒ 两样都没有 ⇒ 红 + 点名 ref
    G4 给得出的那些: .kicad_mod 真在 KiCad 官方库根下**实测存在** + md5 对得上
       (★查文件, 不是只查库目录★)
    G5 证据等级五级白名单 ([官网]/[实测]/[媒体]/[推算]/[0数据]) ⇒ 写 [官方] = 红
    G6 正文无「等原厂回信 / 等供应商确认 / 待外部回复 / 等确认」这类挂起措辞
       (老板 2026-11-12 02:02 政策)
    G7 §3.2 分桶判据里, 四个桶的目标值之和 == 158 (★自己加一遍★) ⇒ 对不上即红

★ 本门禁【不挂 md5】: 判据是内容级 (件数 / 覆盖 / 库文件实存 / md5 / 证据等级 / 降级方案 /
  挂起措辞 / 桶和), 文档改一个字就重判, 不用重锚。

★ **零 pcbnew 依赖**: 本脚本用**纯 python 文本解析**读板面与网表 (口径与 state/check_pcb_nets.py
  的 C4 口径逐条一致, 但独立实现, 不 import 那个需要 pcbnew 的模块) ⇒
  ★**裸 python3 就能跑** (不需要 bash state/pcbnew_py.sh)★

--selftest 反向用例 (每条都自证「真的改到了目标」):
    M1 删掉 §2 表里某一行 (Q_PG)         → 期望 G2 红, 其余仍绿
    M2 把某行 lib:name 改成不存在的      → 期望 G4 红, 其余仍绿
    M3 清空某行目标栏且不给降级方案      → 期望 G3 红, 其余仍绿
    M4 清空某行证据等级                  → 期望 G5 红, 其余仍绿
    M5 正文塞一句「等原厂回信」           → 期望 G6 红, 其余仍绿
    M6 篡改 §1 的三个数字                 → 期望 G1 红, 其余仍绿
    M7 改 §3.2 某桶目标值使四桶和 != 158 → 期望 G7 红, 其余仍绿

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

DOC_REL = os.path.join("HW", "PCB", "FP_TRUTH_COVERAGE_GAP.md")
BLOCK_BEGIN = "<!-- BEGIN ISS361 封装真值覆盖缺口基准块 -->"
BLOCK_END = "<!-- END ISS361 封装真值覆盖缺口基准块 -->"

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

# G6 skip 区 (闸自身的说明文字里会出现这些词)
SKIP_BEGIN = "<!-- G6-SKIP-BEGIN -->"
SKIP_END = "<!-- G6-SKIP-END -->"

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


def split_names(tail):
    return [p.strip() for p in re.split(r"\+(?=\w)", tail) if p.strip()]


def is_pad_name(tail):
    """★真实焊盘号判定: pin<N> 或 USB-IF 物理脚名 (与 state/check_pcb_nets.py 同口径)★"""
    if not tail:
        return False
    if PIN_RE.fullmatch(tail):
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
    """★本单缺口口径: 必装 ∩ 非 NET/TP ∩ footprint!='待定' ∩ 在 C4 里★"""
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


# ---------------------------------------------------------------- helpers


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


def md_tables(text):
    """返回 [(表头 tuple, [行 tuple,...]), ...] —— 只收有 ≥2 列、且表头含 'ref' 的表"""
    out = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i].strip()
        if ln.startswith("|") and ln.count("|") >= 3:
            head = tuple(c.strip() for c in ln.strip("|").split("|"))
            if any("ref" == c.lower() or c.startswith("`ref`") for c in head):
                rows = []
                j = i + 1
                while j < len(lines):
                    r2 = lines[j].strip()
                    if not r2.startswith("|"):
                        break
                    if set(r2.replace("|", "").replace(" ", "")) <= set("-:"):
                        j += 1
                        continue
                    rows.append(tuple(c.strip() for c in r2.strip("|").split("|")))
                    j += 1
                out.append((head, rows))
                i = j
                continue
        i += 1
    return out


def cell(row, head, key):
    for k, c in enumerate(head):
        if c == key or c.replace("`", "") == key:
            return row[k] if k < len(row) else ""
    return ""


def strip_skip(text):
    if SKIP_BEGIN in text and SKIP_END in text:
        pre, rest = text.split(SKIP_BEGIN, 1)
        _, post = rest.split(SKIP_END, 1)
        return pre + post
    return text


def lib_path(libroot, libname):
    lib, name = libname.split(":", 1)
    return os.path.join(libroot, "%s.pretty" % lib, "%s.kicad_mod" % name)


# ---------------------------------------------------------------- 主检查


def check(doc_text, root, libroot=LIBROOT_DEFAULT):
    """返回 (results, facts)"""
    results = {}
    facts = {}

    # ---- 真源实算
    bom_rows = load_bom(os.path.join(root, "HW", "BOM_v1.csv"))
    main_t, chg_t, total_t = iss356_targets(bom_rows)
    ph = netlist_placeholder(os.path.join(root, "HW", "netlist_v1.csv"))
    board = read_board_refs(os.path.join(root, "HW", "PCB", "demo_mainboard.kicad_pcb"))
    c4 = set(ph)
    iss = set(total_t)
    inter = c4 & iss
    diff = c4 - iss
    gap = coverage_gap(bom_rows, c4)

    facts["c4_total"] = len(c4)
    facts["iss356_total"] = len(iss)
    facts["iss356_main"] = len(main_t)
    facts["iss356_chg"] = len(chg_t)
    facts["inter_total"] = len(inter)
    facts["diff_total"] = len(diff)
    facts["gap_total"] = len(gap)
    facts["board_footprints"] = len(board)

    # ---- G0 基准块
    block = parse_block(doc_text)
    results["G0"] = {"ok": block is not None,
                     "detail": "基准块存在且是合法 JSON" if block is not None
                     else "页内缺 BEGIN/END 基准块或 JSON 非法"}
    if block is None:
        for c in ("G1", "G2", "G3", "G4", "G5", "G6", "G7"):
            results[c] = {"ok": False, "detail": "基准块不可用 ⇒ 连带判红"}
        return results, facts

    tables = md_tables(doc_text)

    # ---- G1 三集合件数自洽 (★数字由脚本实算, 不抄文档★)
    g1_bad = []
    counts = block.get("counts", {})
    for key, got in (("c4_total", len(c4)), ("iss356_total", len(iss)),
                     ("diff_total", len(diff)), ("inter_total", len(inter)),
                     ("gap_total", len(gap))):
        if counts.get(key) != got:
            g1_bad.append("基准块 counts.%s: 基准块 %s vs 实算 %d" % (key, counts.get(key), got))
    # 页里 §1.1 / §1.2 / §1.3 三份名单: 逐件与实算集合相等
    def refset_of(head, rows, col):
        return set(cell(r, head, col).strip("`").strip() for r in rows)
    lists = {}
    for head, rows in tables:
        h = [c.replace("`", "") for c in head]
        if "归属桶" in h and "占位脚数" in h:
            lists["c4"] = refset_of(head, rows, "ref")
        elif "板面归属" in h and "在 C4 里?" in h:
            lists["iss"] = refset_of(head, rows, "ref")
        elif "归属桶" in h and "被 ISS-356 口径排除的原因 (逐件归因)" in h:
            lists["diff"] = refset_of(head, rows, "ref")
    for name, want in (("c4", c4), ("iss", iss), ("diff", diff)):
        got = lists.get(name)
        if got is None:
            g1_bad.append("页内缺 §1 名单: %s" % name)
        elif got != want:
            miss = sorted(want - got)
            extra = sorted(got - want)
            g1_bad.append("§1 %s 名单与实算不等 (缺 %d / 多 %d) 例: 缺%s 多%s"
                          % (name, len(miss), len(extra), miss[:3], extra[:3]))
    # 页里 §1 三个小节标题写的三个数字 (★按标题逐个定位, 不用全文扫★)
    for pat, got, label in ((r"###\s*§1\.1\s*`C4-(\d+)`", len(c4), "C4"),
                            (r"###\s*§1\.2\s*`ISS356-(\d+)`", len(iss), "ISS356"),
                            (r"###\s*§1\.3\s*`DIFF-(\d+)`", len(diff), "DIFF")):
        m = re.search(pat, doc_text)
        if not m:
            g1_bad.append("页内缺 §1 标题 (带数字): %s" % label)
        elif int(m.group(1)) != got:
            g1_bad.append("§1 标题 %s 写 %s ⇒ 实算 %d" % (label, m.group(1), got))
    results["G1"] = {"ok": not g1_bad,
                     "detail": "三集合件数自洽 (实算 C4=%d / ISS356=%d / 交集=%d / 差集=%d ⇒ 三份名单逐件相等)"
                     % (len(c4), len(iss), len(inter), len(diff))
                     if not g1_bad else "; ".join(g1_bad[:8])}

    # ---- G2 缺口 13 件逐件齐全
    g2_bad = []
    sec2 = None
    for head, rows in tables:
        h = [c.replace("`", "") for c in head]
        if "目标 `lib:name`" in h or ("目标 lib:name" in h and "库文件实存路径 + md5" in h):
            sec2 = (head, rows)
            break
    if sec2 is None:
        g2_bad.append("页内缺 §2 逐件表")
        sec2_refs = set()
    else:
        head, rows = sec2
        sec2_refs = set(cell(r, head, "ref").strip("`").strip() for r in rows)
        for ref in gap:
            if ref not in sec2_refs:
                g2_bad.append("§2 缺 ref: %s" % ref)
        extra = sorted(sec2_refs - set(gap))
        if extra:
            g2_bad.append("§2 多出实算之外的 ref: %s" % extra[:5])
    facts["gap_refs"] = gap
    results["G2"] = {"ok": not g2_bad,
                     "detail": "缺口 %d 件 §2 逐件齐全 (%d/%d)" % (len(gap), len(gap) - len(g2_bad), len(gap))
                     if not g2_bad else "; ".join(g2_bad[:8])}

    # ---- G3 目标栏非空 + G4 库文件实存/md5
    g3_bad = []
    g4_bad = []
    n_lib = 0
    if sec2 is not None:
        head, rows = sec2
        for r in rows:
            ref = cell(r, head, "ref").strip("`").strip()
            tgt = cell(r, head, "目标 `lib:name`")
            if not tgt:
                tgt = cell(r, head, "目标 lib:name")
            pathmd5 = cell(r, head, "库文件实存路径 + md5")
            fb = cell(r, head, "降级方案")
            tgt = tgt.strip()
            has_lib = ":" in tgt and not tgt.startswith("[0数据]")
            if has_lib:
                if not pathmd5.strip():
                    g3_bad.append("%s: 有目标 lib:name 但库文件实存路径 + md5 栏空" % ref)
                else:
                    n_lib += 1
                    libname = tgt.strip("`")
                    if ":" not in libname:
                        g4_bad.append("%s: lib:name 格式错: %s" % (ref, libname))
                    else:
                        p = lib_path(libroot, libname)
                        if not os.path.isfile(p):
                            g4_bad.append("%s: 文件不在盘: %s" % (ref, libname))
                        else:
                            m = re.search(r"md5\s+`?([0-9a-f]{32})`?", pathmd5)
                            if not m:
                                g4_bad.append("%s: 路径栏里没有 md5" % ref)
                            else:
                                real = hashlib.md5(open(p, "rb").read()).hexdigest()
                                if real != m.group(1):
                                    g4_bad.append("%s: md5 不符 (页写 %s / 实 %s)"
                                                  % (ref, m.group(1)[:8], real[:8]))
            else:
                # [0数据] 档: 必须有非空降级方案
                if "[0数据]" not in tgt:
                    g3_bad.append("%s: 目标栏既不是 lib:name 也不是 [0数据]: %r" % (ref, tgt[:40]))
                if not fb.strip():
                    g3_bad.append("%s: [0数据] 档但降级方案栏空" % ref)
    facts["n_lib_refs"] = n_lib
    results["G3"] = {"ok": not g3_bad,
                     "detail": "%d 件的目标栏非空 (lib:name 档给全 + [0数据] 档都有降级方案)" % len(gap)
                     if not g3_bad else "; ".join(g3_bad[:8])}
    results["G4"] = {"ok": not g4_bad,
                     "detail": "%d 处 lib:name 的 .kicad_mod 全部实测在盘 + md5 一致" % n_lib
                     if not g4_bad else "; ".join(g4_bad[:8])}

    # ---- G5 证据等级五级白名单
    g5_bad = []
    n_ev = 0
    if sec2 is not None:
        head, rows = sec2
        for r in rows:
            ref = cell(r, head, "ref").strip("`").strip()
            ev = cell(r, head, "证据等级")
            n_ev += 1
            if not ev.strip():
                g5_bad.append("证据等级空: %s" % ref)
                continue
            tags = set(re.findall(r"\[[^\[\]]+\]", ev))
            if not tags:
                g5_bad.append("证据等级无标签: %s" % ref)
                continue
            bad = tags - ALLOWED_EVIDENCE
            if bad:
                g5_bad.append("证据等级非法 %s: %s" % (sorted(bad), ref))
    facts["n_evidence_rows"] = n_ev
    results["G5"] = {"ok": not g5_bad,
                     "detail": "%d 行证据等级全 ∈ 五级白名单 (无 [官方])" % n_ev
                     if not g5_bad else "; ".join(g5_bad[:8])}

    # ---- G6 挂起措辞
    body = strip_skip(doc_text)
    g6_bad = []
    for ph_ in FORBIDDEN_PHRASES:
        if ph_ in body:
            g6_bad.append("出现挂起措辞: %s (×%d)" % (ph_, body.count(ph_)))
    results["G6"] = {"ok": not g6_bad,
                     "detail": "正文无「等回复/等原厂回信/待供应商确认/待外部回复/等原厂/等确认」类挂起措辞"
                     if not g6_bad else "; ".join(g6_bad)}

    # ---- G7 四桶目标值之和 == 158
    g7_bad = []
    # ★桶目标值以【页里 §3.2 的表】为准 (那才是给人看的那张表) ⇒ 基准块只做交叉核对★
    tbl = find_bucket_table(doc_text)
    if tbl is None:
        g7_bad.append("页内缺 §3.2 分桶判据表 (桶 / 件数 (= 目标值))")
    else:
        got = []
        for key in ("TP", "DNP", "靶内", "缺口"):
            v = tbl.get(key)
            if v is None:
                g7_bad.append("§3.2 桶表缺桶: %s" % key)
            else:
                got.append(v)
        if len(got) == 4:
            s = sum(got)
            if s != len(c4):
                g7_bad.append("四桶目标值之和 %d != %d (C4 件数) ⇒ 桶表 %s"
                              % (s, len(c4), tbl))
    # ★每桶目标值也要与脚本实算件数相等 (页里写了 42/26/77/13, 不能写别的)★
    tp_n = len([r for r in diff if _bom_row(bom_rows, r)["type"] == "TP"])
    dnp_n = len([r for r in diff
                 if _bom_row(bom_rows, r)["type"] != "TP" and _bom_row(bom_rows, r)["dnp"] == "DNP"])
    want = {"TP": tp_n, "DNP": dnp_n, "靶内": len(inter), "缺口": len(gap)}
    for key, w in want.items():
        if tbl is not None and tbl.get(key) != w:
            g7_bad.append("桶 %s: 页里写 %s ⇒ 实算 %s" % (key, tbl.get(key), w))
    # ★基准块 buckets 与页里桶表必须一致 (两处不能各写各的)★
    blk_b = block.get("buckets", {})
    for key, w in (("tp", tp_n), ("dnp", dnp_n), ("in_target", len(inter)), ("gap", len(gap))):
        if blk_b.get(key) != w:
            g7_bad.append("基准块 buckets.%s: %s ⇒ 实算 %s" % (key, blk_b.get(key), w))
    results["G7"] = {"ok": not g7_bad,
                     "detail": "四桶目标值 %s 之和 = %d == C4 件数 %d" % (tbl, sum(tbl.values()) if tbl else -1, len(c4))
                     if not g7_bad else "; ".join(g7_bad[:8])}
    return results, facts


def find_bucket_table(doc_text):
    """⇒ {桶名: 目标值} —— 从 §3.2 分桶判据表里读 (按表头定位, 不靠猜)"""
    lines = doc_text.splitlines()
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not (s.startswith("|") and "桶" in s and "件数" in s and "目标值" in s):
            continue
        head = [c.strip() for c in s.strip("|").split("|")]
        out = {}
        j = i + 1
        while j < len(lines):
            r2 = lines[j].strip()
            if not r2.startswith("|"):
                break
            cells = [c.strip() for c in r2.strip("|").split("|")]
            if len(cells) < 2:
                break
            name = cells[0].replace("**", "").replace("★", "").strip()
            m = re.search(r"(\d+)", cells[1].replace("**", "").replace("★", ""))
            if name and m and name not in ("合计", "桶"):
                out[name] = int(m.group(1))
            j += 1
        if out:
            return out
    return None


def _bom_row(bom_rows, ref):
    for r in bom_rows:
        if r["ref"] == ref:
            return r
    return {"ref": ref, "type": "", "dnp": ""}


def print_report(results, facts, as_json=False):
    if as_json:
        print(json.dumps({"ok": all(v["ok"] for v in results.values()),
                          "results": results, "facts": facts}, ensure_ascii=False, indent=1))
        return
    print("【ISS-361 封装真值覆盖缺口闸】")
    for cid in ("G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7"):
        r = results[cid]
        print("  [%s] %s :: %s" % ("PASS" if r["ok"] else "FAIL", cid, r["detail"]))
    print("  事实: C4=%s ISS356=%s (main %s / chg %s) 交集=%s 差集=%s | 缺口=%s | 板面封装=%s"
          % (facts.get("c4_total"), facts.get("iss356_total"), facts.get("iss356_main"),
             facts.get("iss356_chg"), facts.get("inter_total"), facts.get("diff_total"),
             facts.get("gap_total"), facts.get("board_footprints")))


# ---------------------------------------------------------------- selftest

def selftest(root):
    doc_path = os.path.join(root, DOC_REL)
    if not os.path.isfile(doc_path):
        print("[FAIL] 找不到 %s" % doc_path)
        return 2
    orig = open(doc_path, encoding="utf-8").read()
    sandbox = os.path.join(root, "tmp", "iss361_selftest")
    if os.path.isdir(sandbox):
        shutil.rmtree(sandbox)
    os.makedirs(sandbox, exist_ok=True)
    cases = []

    # ★先定位 §2 表头 ⇒ 拿到每列的准确下标 (不能猜列位)★
    sec2_head = None
    for ln in orig.splitlines():
        s = ln.strip()
        if s.startswith("|") and "目标" in s and "lib:name" in s and "证据等级" in s:
            sec2_head = [c.strip().replace("`", "") for c in s.strip("|").split("|")]
            break
    if sec2_head is None:
        print("[FAIL] 找不到 §2 表头")
        return 2
    try:
        col_target = next(i for i, c in enumerate(sec2_head) if "目标" in c and "lib:name" in c)
        col_fb = next(i for i, c in enumerate(sec2_head) if "降级方案" in c)
        col_ev = next(i for i, c in enumerate(sec2_head) if c == "证据等级")
    except StopIteration:
        print("[FAIL] §2 表头列定位失败: %s" % sec2_head)
        return 2

    # ---- M1 删掉 §2 表里 Q_PG 那一行
    m1 = re.search(r"^\| `Q_PG` \|.*\n", orig, re.M)
    if not m1:
        print("[FAIL] M1 找不到 §2 Q_PG 行")
        return 2
    # ★探针要选【只在这一行里出现】的串 (否则别处也有 ⇒ 删了也还在 ⇒ 探针失效)★
    m1_probe = None
    for cand in ("Q_PG", "DMP3098L (Diodes Inc SOT23 3-pin", "PWR_ON / pad2=BAT_SW"):
        if orig.count(cand) == 1:
            m1_probe = cand
            break
    if m1_probe is None:
        print("[FAIL] M1 找不到只出现一次的探针串")
        return 2
    cases.append(("M1", "删 §2 一行 (Q_PG) ⇒ G2 红", "G2",
                  m1.group(0), "", m1_probe, "absent"))

    # ---- M2 把某行 lib:name 改成不存在的
    m2 = re.search(r"(`Package_TO_SOT_SMD:SOT-23`)", orig)
    if not m2:
        print("[FAIL] M2 找不到 SOT-23 目标 lib:name")
        return 2
    cases.append(("M2", "改 lib:name 成不存在的 ⇒ G4 红", "G4",
                  m2.group(0), "`Package_TO_SOT_SMD:SOT-23_XX`", "`Package_TO_SOT_SMD:SOT-23_XX`", "present"))

    # ---- M3 清空某行目标栏且不给降级方案 (取 Q_ENVC 行)
    m3 = re.search(r"^\| `Q_ENVC` \|[^\n]*$", orig, re.M)
    if not m3:
        print("[FAIL] M3 找不到 §2 Q_ENVC 行")
        return 2
    # ★行也要用 strip("|").split("|") ⇒ 与表头同一套下标 (否则差一位)★
    p3 = m3.group(0).strip().strip("|").split("|")
    p3m = list(p3)
    p3m[col_target] = "  "
    p3m[col_fb] = "  "
    cases.append(("M3", "清空某行目标栏且不给降级方案 ⇒ G3 红", "G3",
                  m3.group(0), "| " + "|".join(p3m) + " |", "| " + "|".join(p3m) + " |", "present"))

    # ---- M4 清空某行证据等级 (同 Q_ENVC 行)
    m4 = re.search(r"^\| `Q_ENVC` \|[^\n]*$", orig, re.M)
    p4 = m4.group(0).strip().strip("|").split("|")
    if "[实测]" not in p4[col_ev]:
        print("[FAIL] M4 证据等级列值不含 [实测]: %r" % p4[col_ev])
        return 2
    p4m = list(p4)
    p4m[col_ev] = "  "
    cases.append(("M4", "清空某行证据等级 ⇒ G5 红", "G5",
                  m4.group(0), "| " + "|".join(p4m) + " |", "| " + "|".join(p4m) + " |", "present"))

    # ---- M5 正文塞「等原厂回信」
    first_line = orig.split("\n", 1)[0]
    if not first_line.startswith("# "):
        print("[FAIL] M5 首行不是标题: %r" % first_line[:40])
        return 2
    cases.append(("M5", "正文塞「等原厂回信」⇒ G6 红", "G6",
                  first_line, "等原厂回信\n\n" + first_line, "等原厂回信", "present"))

    # ---- M6 篡改 §1 的三个数字 (在 §1.1 标题行里改 C4-158 ⇒ 158 改成 157)
    m6 = re.search(r"### §1\.1 `C4-(\d+)`", orig)
    if not m6:
        print("[FAIL] M6 找不到 §1.1 标题")
        return 2
    old6 = m6.group(0)
    new6 = "### §1.1 `C4-%d`" % (int(m6.group(1)) - 1)
    cases.append(("M6", "篡改 §1 的三个数字之一 ⇒ G1 红", "G1",
                  old6, new6, "### §1.1 `C4-%d`" % (int(m6.group(1)) - 1), "present"))

    # ---- M7 改 §3.2 某桶目标值使四桶和 != 158
    # ★用与闸同一套定位 (§3.2 桶表) ⇒ 改的就是闸真读的那张表★
    tbl = find_bucket_table(orig)
    if not tbl or "靶内" not in tbl:
        print("[FAIL] M7 找不到 §3.2 靶内桶目标值 (读到 %s)" % (tbl,))
        return 2
    old7 = None
    for ln in orig.splitlines():
        s = ln.strip()
        if s.startswith("|") and "靶内" in s and "77" in s and "C4 ∩ ISS-356" in s:
            old7 = s
            break
    if old7 is None:
        print("[FAIL] M7 找不到 §3.2 靶内桶那一行原文")
        return 2
    new7 = old7.replace("77", "78", 1)
    if new7 == old7:
        print("[FAIL] M7 变异串没命中")
        return 2
    cases.append(("M7", "改 §3.2 某桶目标值使四桶和 != 158 ⇒ G7 红", "G7",
                  old7, new7, new7, "present"))

    all_ok = True
    for cid, desc, expect_red, old, new, probe, probe_mode in cases:
        mutated = orig.replace(old, new, 1)
        if mutated == orig:
            print("[FAIL] %s 变异没落到副本上 (串没命中) ⇒ 不能证明红的是目标那一条" % cid)
            all_ok = False
            continue
        # ★探针自证: 变异串必须【在副本里 且 不在原文档里】(或【被删掉】)⇒ 证明"真的改到了目标"★
        if probe_mode == "absent":
            if probe in mutated:
                print("[FAIL] %s 目标串仍留在副本里 ⇒ 删除没生效" % cid)
                all_ok = False
                continue
        else:
            if probe not in mutated:
                print("[FAIL] %s 探针串不在副本里 ⇒ 变异没生效" % cid)
                all_ok = False
                continue
            if probe in orig:
                print("[FAIL] %s 探针串本来就在原文档里 ⇒ 变异无效" % cid)
                all_ok = False
                continue
        cp = os.path.join(sandbox, "FP_TRUTH_COVERAGE_GAP_%s.md" % cid)
        with open(cp, "w", encoding="utf-8") as fh:
            fh.write(mutated)
        res, _ = check(mutated, root)
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
