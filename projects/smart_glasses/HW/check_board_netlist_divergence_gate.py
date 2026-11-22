#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_board_netlist_divergence_gate.py —— ISS-340 · ★板 ↔ 网表 差异归属判别闸 (只读)★

★为什么要有这个闸 (ISS-340 的来由)★:
  `state/check_pcb_nets.py` 只回答 **"板和网表等不等价"** (C1 焊盘级等价 ⇒ 红/绿),
  但**不回答 "这条差异归谁"** ⇒ 板只改一次 (投板后改板 = 2-4 周 + ¥4-8K) 的前提下,
  ★必须先把每条差异拆成三桶★:
    · **A = 网表侧错** ⇒ 改网表就够, ★**板 md5 一个字节都不用动**★
    · **B = 板侧错**   ⇒ 必须动板, 进板那一趟 B-清单 (那一趟一次做完)
    · **C = 等老板拍板** ⇒ 进待拍板页 (★本闸只列 need key + 题, 不代拍★)

★本闸的三条硬纪律★:
  ① ★**自己跑出差异** ★ —— 网表→焊盘映射、板文件解析、C1 三类差异 (多余/同号异网/缺失)
     ★全部在本文件里独立实现一遍★ (★不 import `state/check_pcb_nets.py`, 不照抄任何读数★)
  ② ★**只读** ★ —— 板文件**只按文本解析** (★不 import pcbnew ⇒ 结构上就不可能写板★);
     网表只读; ★唯一写入 = --selftest 在 /tmp 下的临时副本★ (★不碰盘上任何工程文件★)
  ③ ★**归桶是算出来的, 不是写死的** ★ —— 每条差异命中一条**可复算的规则** (R0~R5),
     输出里必须打印**命中了哪条规则 + 该规则的实际取值** ⇒ 规则错了能一眼看见, 不会假绿。

★归桶规则 (按序命中第一条即停)★:
  R0 DECIDE  (→ C) 差异类型=多余(EXTRA) + 该器件命中**未拍板**的 boss need key
                   ⇒ "该不该在这块板上"本身就是待拍事项 ⇒ 拍之前不许动板也不许动网表
  R1 NETROW  (→ A) 差异类型=多余(EXTRA) + 该器件在网表里存在但 **board 列 ≠ MAIN_PCB**
                   ⇒ 网表把器件划给了别的板 ⇒ 改 board 列即对齐 ⇒ **板 md5 不用动**
  R2 PSEUDO  (→ A) 差异类型=缺失(MISSING) + 管辖该焊盘的网表行是**伪器件/清单行**
                   (type ∈ {NET, RAIL}) ⇒ 网表多了一行 ⇒ 删这行即对齐 ⇒ **板 md5 不用动**
  R3 AUTH    (→ B) 差异类型=同号异网(WRONG) + 网表侧该行带**权威标记**
                   (老板拍板/裁决 · [官方] · 载板指引/规格) + 目标网被其它焊盘佐证
                   ⇒ 网表侧是已拍的一侧 ⇒ **板是旧接法** ⇒ 板那一趟重画/挪线
  R4 BOARD   (→ B) 差异类型=缺失(MISSING) + 其它 ⇒ 板少东西 ⇒ 板那一趟补焊盘/加封装
  R5 STALE   (→ B) 差异类型=多余(EXTRA) + 该器件在网表里**完全没有** ⇒ 板上有网表外器件 ⇒ 板删
  R6 UNATTR  (→ 未解释) 上面全不命中 ⇒ ★**强制人工看** ⇒ 闸退 rc=2 (★不许默认绿★)

★rc 语义★: 0 = 无未解释差异 (每条都归了桶) · 2 = 有未解释差异 (R6) · 1 = 运行错误

★用法★:
  python3 HW/check_board_netlist_divergence_gate.py --selftest
  python3 HW/check_board_netlist_divergence_gate.py HW/PCB/demo_mainboard.kicad_pcb --netlist HW/netlist_v1.csv
"""

import csv
import hashlib
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
DEFAULT_BOARD = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
DEFAULT_NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")
DEFAULT_REGISTRY = os.path.join(PROJ, "state", "fragments", "pm.yaml")

BOARD_FILTER = "MAIN_PCB"
PSEUDO = ("RAIL_", "NET_")
# ★NC 焊盘合法的器件: SOM 的 4 组 100 脚座未用脚 + USB-C 的 shield/A8/B8
NC_ALLOWED = {"J_SOM_P1", "J_SOM_P2", "J_SOM_P3", "J_SOM_P4", "J_USB_C"}
USBIF_RE = re.compile(r"^(?:[AB](?:1|4|5|6|7|8|9|12)|shield)$")
PIN_RE = re.compile(r"^pin\d+(\+pin\d+)*$")
# ★受控阻抗 / 高速网的网表标记 (⇒ 该网是差分对成员 / 高速网)
# ★★注意: 不能拿裸「阻抗」当标记 ★ —— ★网表里「阻抗 单端」恰恰是【单端】的意思★
# (★实测踩坑: PWR_GOOD 行 190 的 note 写着「阻抗 单端」⇒ 被裸「阻抗」命中 ⇒ 把电源网误判成差分对成员网★)
DIFF_MARKERS = ("差分阻抗", "受控阻抗", "差分对", "等长", "差分")
SINGLE_ENDED_MARKERS = ("单端",)
# ★高速网名提示 (★粗筛, 只作提示不作判据★): USB 2.0 FS 不算高速 ⇒ 不列 USB/HS
HIGH_SPEED_HINT = ("DSI", "CSI", "MIPI", "PCIE", "SERDES", "LVDS", "ETH")
# ★权威标记: 老板拍板 / 官方规格 —— 命中 ⇒ 网表侧是"已拍的一侧"
BOSS_AUTHORITY = ("拍板", "裁决", "老板", "G-1")
OFFICIAL_AUTHORITY = ("官方", "载板指引", "指引", "规格", "datasheet", "Forlinx", "标准")
PSEUDO_TYPES = ("NET", "RAIL")


# --------------------------------------------------------------------- 通用


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def mtime_of(path):
    st = os.stat(path)
    return "%.9f" % st.st_mtime


def short(s, n=96):
    s = re.sub(r"\s+", " ", (s or "")).strip()
    return s if len(s) <= n else s[: n - 3] + "..."


# ----------------------------------------------------------------- 网表解析


def read_netlist(path):
    """→ [{列: 值, '_line': 行号, '_raw': 原始行}]"""
    with open(path, encoding="utf-8-sig") as f:
        raw = f.read().splitlines()
    rows, header = [], None
    for i, r in enumerate(csv.reader(raw)):
        if i == 0:
            header = r
            continue
        if not r or not any((x or "").strip() for x in r):
            continue
        d = dict(zip(header, r))
        d["_line"] = i + 1
        d["_raw"] = raw[i] if i < len(raw) else ""
        rows.append(d)
    return rows


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
    """★网表里的节点尾串 ⇒ 真实焊盘号? (pin<N> / USB-IF 物理脚名 / 合并写法)"""
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


def netlist_pads(rows):
    """★网表 → 焊盘期望 (独立实现, 不复用 check_pcb_nets.py)★

    规则 (与板生成器同口径):
      · 编号脚 "<器件> pin<N>" ⇒ 焊盘号 = N
      · USB-IF 物理脚名 (A1/A6/B12/shield, 含 "A6+B6" 合并写法) ⇒ 焊盘号 = 该脚名
      · 命名脚 / 裸端 ⇒ 焊盘号 = 占位序 (1..M)
      · 退化行 (node1 与 node2 是同一裸器件) ⇒ 不占引脚
      · 行的 ref 若两个节点都没提到 ⇒ ref 自己占一个裸端
      · 裸端若已被同器件的编号脚占用 ⇒ 是别名, 不占焊盘
    返回 (want, src, placeholder, notes)
      want  : {(ref, pad): net}
      src   : {(ref, pad): [(行号, 原始行, net)]}
    """
    rows = [r for r in rows if (r.get("board") or BOARD_FILTER).strip() == BOARD_FILTER]
    refs = set((r.get("ref") or "").strip() for r in rows if (r.get("ref") or "").strip())
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
        if parsed[0][0] == parsed[1][0] and parsed[0][1] is None and parsed[1][1] is None:
            continue                                  # 退化行
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
                    if key not in d:
                        d[key] = (net, "P", r["_line"], r["_raw"], r)
                    seen.add(comp)
            elif tail:
                for nm in split_names(tail):
                    key = ("N", nm, net)
                    if key not in d:
                        d[key] = (net, "N", r["_line"], r["_raw"], r)
                    seen.add(comp)
            else:
                key = ("B", net)
                if key not in d:
                    d[key] = (net, "B", r["_line"], r["_raw"], r)
                seen.add(comp)
        if ref and ref in real and ref not in seen:
            d = terms.setdefault(ref, {})
            key = ("B", net)
            if key not in d:
                d[key] = (net, "B", r["_line"], r["_raw"], r)
    # 裸端被同器件的编号脚覆盖 ⇒ 别名, 不占焊盘
    for comp, d in terms.items():
        pinnets = set(v[0] for k, v in d.items() if k[0] == "P")
        for k in [k for k in d if k[0] == "B" and k[1] in pinnets]:
            del d[k]
    want, src, placeholder = {}, {}, {}
    for comp, d in terms.items():
        if not d:
            continue
        entries = []
        if any(k[0] == "P" for k in d):
            pins = sorted([(k[1], v[0], k) for k, v in d.items() if k[0] == "P"],
                          key=lambda t: (0, t[0], 0) if isinstance(t[0], int) else (1, str(t[0]), 0))
            nums = [x[0] for x in pins if isinstance(x[0], int)]
            nxt = (max(nums) + 1) if nums else 1
            for num, net, k in pins:
                entries.append((num, net, k))
            for k, v in d.items():
                if k[0] != "P":
                    entries.append((nxt, v[0], k))
                    nxt += 1
        else:
            for i, (k, v) in enumerate(d.items(), start=1):
                entries.append((i, v[0], k))
            placeholder[comp] = len(entries)
        for num, net, k in entries:
            if comp.startswith(PSEUDO):
                continue
            key = (comp, str(num))
            want[key] = net
            v = d[k]
            src.setdefault(key, []).append((v[2], v[3], net, v[4]))
    return want, src, placeholder, notes


# ----------------------------------------------------------------- 板文件解析


class Str(str):
    """★带引号的字符串 (与原子 token 区分)★"""


def sexp_parse(text):
    stack = [[]]
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "(":
            new = []
            stack[-1].append(new)
            stack.append(new)
            i += 1
        elif c == ")":
            if len(stack) > 1:
                stack.pop()
            i += 1
        elif c == '"':
            j, buf = i + 1, []
            while j < n:
                if text[j] == "\\":
                    if j + 1 < n:
                        buf.append(text[j + 1])
                    j += 2
                    continue
                if text[j] == '"':
                    break
                buf.append(text[j])
                j += 1
            stack[-1].append(Str("".join(buf)))
            i = j + 1
        elif c.isspace():
            i += 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in '()"':
                j += 1
            stack[-1].append(text[i:j])
            i = j
    return stack[0]


def _kids(node, name):
    for c in node:
        if isinstance(c, list) and c and c[0] == name:
            yield c


def _f(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def parse_board(path):
    """★板文件 (kicad_pcb 文本) → 焊盘 / 走线 / 过孔 / 铜区 (★只读★)"""
    with open(path, encoding="utf-8") as f:
        root = sexp_parse(f.read())
    # ★sexp_parse 返回的是顶层列表, 真文档是它的第一个元素 (kicad_pcb …)★
    doc = root[0] if (root and isinstance(root[0], list) and root[0]) else root
    netnum2name = {}
    for c in _kids(doc, "net"):
        if len(c) >= 3:
            try:
                netnum2name[int(c[1])] = str(c[2])
            except (TypeError, ValueError):
                pass
    fps, segs, vias, zones = {}, [], [], []
    for blk in _kids(doc, "footprint"):
        ref, at, pads = None, (0.0, 0.0, 0.0), []
        for c in blk:
            if not isinstance(c, list) or not c:
                continue
            if c[0] == "property" and len(c) > 2 and c[1] == "Reference":
                ref = str(c[2])
            elif c[0] == "at":
                at = (_f(c[1]), _f(c[2]), _f(c[3]) if len(c) > 3 else 0.0)
            elif c[0] == "pad":
                num, loc, size, net = str(c[1]), (0.0, 0.0), (0.0, 0.0), ""
                for d in c:
                    if not isinstance(d, list) or not d:
                        continue
                    if d[0] == "at":
                        loc = (_f(d[1]), _f(d[2]))
                    elif d[0] == "size":
                        size = (_f(d[1]), _f(d[2]))
                    elif d[0] == "net":
                        if len(d) >= 3:
                            net = str(d[2])
                        elif isinstance(d[1], Str):
                            net = str(d[1])          # ★KiCad 10: (net "NAME") 只有名字★
                        else:
                            try:
                                net = netnum2name.get(int(d[1]), "")
                            except (TypeError, ValueError):
                                net = ""
                pads.append({"num": num, "loc": loc, "size": size, "net": net})
        if ref:
            fps[ref] = {"at": at, "pads": pads}
    for blk in _kids(doc, "segment"):
        st = en = None
        width, layer, net = 0.0, "", ""
        for d in blk:
            if not isinstance(d, list) or not d:
                continue
            if d[0] == "start":
                st = (_f(d[1]), _f(d[2]))
            elif d[0] == "end":
                en = (_f(d[1]), _f(d[2]))
            elif d[0] == "width":
                width = _f(d[1])
            elif d[0] == "layer":
                layer = str(d[1])
            elif d[0] == "net":
                net = str(d[1])
        if st and en:
            segs.append({"s": st, "e": en, "w": width, "layer": layer, "net": net})
    for blk in _kids(doc, "via"):
        at, net = None, ""
        for d in blk:
            if not isinstance(d, list) or not d:
                continue
            if d[0] == "at":
                at = (_f(d[1]), _f(d[2]))
            elif d[0] == "net":
                net = str(d[1])
        if at:
            vias.append({"at": at, "net": net})
    for blk in _kids(doc, "zone"):
        net, layer = "", ""
        for d in blk:
            if not isinstance(d, list) or not d:
                continue
            if d[0] == "net":
                net = str(d[1])
            elif d[0] == "layer":
                layer = str(d[1])
        if net:
            zones.append({"net": net, "layer": layer})
    return {"fps": fps, "segs": segs, "vias": vias, "zones": zones}


def board_pads(bp):
    have = {}
    for ref, fp in bp["fps"].items():
        for p in fp["pads"]:
            have[(ref, p["num"])] = p["net"]
    return have


def _pad_abs(fp, p):
    x, y, ang = fp["at"]
    px, py = p["loc"]
    r = math.radians(ang)
    return (x + px * math.cos(r) + py * math.sin(r),
            y - px * math.sin(r) + py * math.cos(r))


def _seg_len(s):
    return math.hypot(s["e"][0] - s["s"][0], s["e"][1] - s["s"][1])


def copper_stats(bp, ref, padnum):
    """★某个焊盘的铜: 有没有铜 / 直连铜长 (mm) / 该网总走线长 (mm)★"""
    fp = bp["fps"].get(ref)
    if fp is None:
        return {"net": "", "has_copper": False, "stub_mm": 0.0, "net_total_mm": 0.0,
                "segments": 0, "vias": 0, "zone": False}
    pad = None
    for p in fp["pads"]:
        if p["num"] == padnum:
            pad = p
            break
    if pad is None:
        return {"net": "", "has_copper": False, "stub_mm": 0.0, "net_total_mm": 0.0,
                "segments": 0, "vias": 0, "zone": False}
    net = pad["net"]
    ax, ay = _pad_abs(fp, pad)
    hw, hh = pad["size"][0] / 2.0, pad["size"][1] / 2.0
    tol = 0.06
    stub, cnt = 0.0, 0
    total = 0.0
    vias = 0
    for s in bp["segs"]:
        if s["net"] != net:
            continue
        total += _seg_len(s)
        for pt in (s["s"], s["e"]):
            if abs(pt[0] - ax) <= hw + tol and abs(pt[1] - ay) <= hh + tol:
                stub += _seg_len(s)
                cnt += 1
                break
    for v in bp["vias"]:
        if v["net"] != net:
            continue
        if abs(v["at"][0] - ax) <= hw + tol and abs(v["at"][1] - ay) <= hh + tol:
            vias += 1
    zone = any(z["net"] == net for z in bp["zones"])
    return {"net": net, "has_copper": bool(net), "stub_mm": stub, "net_total_mm": total,
            "segments": cnt, "vias": vias, "zone": zone}


# -------------------------------------------------------------- 决策登记表


def load_registry(path):
    """★未拍板的 boss need key (★只读, 不落表)★ → [(key, 行号, 全文)]"""
    if not path or not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    items, cur = [], None
    for i, ln in enumerate(lines):
        m = re.match(r"^\s*-\s*key:\s*(\S+)\s*$", ln)
        if m:
            if cur:
                items.append(cur)
            cur = {"key": m.group(1), "line": i + 1, "text": [], "decided": False,
                   "to": "", "item": []}
            continue
        if cur is None:
            continue
        m2 = re.match(r"^\s+(\w+):\s*(.*)$", ln)
        if m2:
            k, v = m2.group(1), m2.group(2)
            if k in ("decision", "decided_at", "decided_by"):
                if v.strip().strip("'\"") not in ("",):
                    cur["decided"] = True
                if k == "item":
                    cur["item"].append(v)
                continue
            if k == "to":
                cur["to"] = v.strip().strip("'\"")
            if k == "item":
                cur["item"].append(v)
            continue
        if ln.strip():
            cur["text"].append(ln)
    if cur:
        items.append(cur)
    out = []
    for it in items:
        if it["decided"] or it["to"] != "boss":
            continue
        body = " ".join(it["item"] + it["text"]).strip().strip("'\"")
        out.append((it["key"], it["line"], body))
    return out


def open_keys_for(ref, registry):
    pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(ref) + r"(?![A-Za-z0-9_])")
    return [(k, ln, txt) for (k, ln, txt) in registry if pat.search(txt)]


# ------------------------------------------------------------------- 归桶


def authority_of(row):
    """★网表行的权威标记 ⇒ (命中?, 命中的标记串, evidence 等级)★"""
    note = (row.get("note") or "")
    ev = (row.get("evidence") or "").strip()
    for m in BOSS_AUTHORITY:
        if m in note:
            return True, "老板拍板/裁决标记『%s』" % m, ev
    for m in OFFICIAL_AUTHORITY:
        if m in note:
            return True, "官方规格标记『%s』" % m, ev
    if ev in ("[官方]", "[官网]"):
        return True, "evidence 等级 %s" % ev, ev
    return False, "无", ev


def net_class(net, rows_by_net):
    """★这个网是不是 受控阻抗/差分对成员 或 高速网★"""
    marks = []
    for r in rows_by_net.get(net, []):
        note = (r.get("note") or "")
        for m in DIFF_MARKERS:
            if m in note:
                marks.append("%s (netlist HW/netlist_v1.csv 行 %d: %s)"
                             % (m, r["_line"], short(note, 60)))
                break
    up = (net or "").upper()
    hs = [h for h in HIGH_SPEED_HINT if h in up]
    single = False
    for r in rows_by_net.get(net, []):
        note = (r.get("note") or "")
        if any(m in note for m in SINGLE_ENDED_MARKERS):
            single = True
            break
    return marks, hs, single


def _gov_row(gov_rows):
    """★取管辖该焊盘的网表行 (dict) —— 兼容 4 元组 (行号, 原文, net, row) 与直接给 dict★"""
    if not gov_rows:
        return None
    g = gov_rows[0]
    if isinstance(g, (tuple, list)):
        return g[3] if len(g) > 3 else None
    return g


def classify(rec, ctx):
    """★归桶 (★规则化, 可复算★) → (bucket, rule_id, 理由, 证据 dict)★"""
    ref, kind = rec["ref"], rec["kind"]
    rows_by_ref = ctx["rows_by_ref"]
    my_rows = rows_by_ref.get(ref, [])

    if kind == "extra":
        keys = open_keys_for(ref, ctx["registry"])
        if keys:
            k, ln, txt = keys[0]
            return ("C", "R0 DECIDE",
                    "该器件命中未拍板的 boss need key ⇒ 留/删本身就是待拍事项 ⇒ 本闸不代拍",
                    {"need_key": k, "need_line": ln,
                     "need_item": short(txt, 200), "need_all": [x[0] for x in keys]})
        other_board = [r for r in ctx["all_rows"]
                       if (r.get("ref") or "").strip() == ref
                       and (r.get("board") or BOARD_FILTER).strip() != BOARD_FILTER]
        if other_board:
            r = other_board[0]
            return ("A", "R1 NETROW",
                    "网表把该器件划给了别的板 (board 列 ≠ %s) ⇒ 改网表即对齐 ⇒ 板 md5 不用动"
                    % BOARD_FILTER,
                    {"file": "HW/netlist_v1.csv", "line": r["_line"],
                     "change": "board 列 『%s』 → 『%s』" % ((r.get("board") or "").strip(),
                                                         BOARD_FILTER),
                     "raw": short(r["_raw"])})
        if not my_rows:
            return ("B", "R5 STALE",
                    "网表里根本没有这个器件 ⇒ 板上有网表外的器件 ⇒ 板那一趟拿掉",
                    {"file": "HW/netlist_v1.csv", "line": 0, "change": "板侧删除", "raw": ""})
        return (None, "R6 UNATTR", "多余器件但无 open need key 且网表里有它 ⇒ 无法自动归桶",
                {})

    if kind == "missing":
        gov = _gov_row(rec["gov_rows"])
        on_board = ref in ctx["board_refs"]
        if gov is not None:
            gtype = (gov.get("type") or "").strip().upper()
            if gtype in PSEUDO_TYPES and not on_board:
                return ("A", "R2 PSEUDO",
                        "管辖该焊盘的网表行是伪器件/清单行 (type=%s) ⇒ 网表多了一行 ⇒ 改网表即对齐"
                        " ⇒ 板 md5 不用动" % gtype,
                        {"file": "HW/netlist_v1.csv", "line": gov["_line"],
                         "change": "删掉这行 (type=%s 的伪器件/清单行)" % gtype,
                         "raw": short(gov["_raw"])})
        if on_board:
            return ("B", "R4 BOARD",
                    "器件在板上、缺的是这个焊盘 ⇒ 板那一趟补焊盘 (板 md5 要动)",
                    {"file": "HW/PCB/demo_mainboard.kicad_pcb", "line": 0,
                     "change": "补 %s pad%s (网 %s)" % (ref, rec["pad"], rec["want_net"]),
                     "raw": ""})
        return ("B", "R4 BOARD",
                "器件整体不在板上 ⇒ 板那一趟加封装 (板 md5 要动)",
                {"file": "HW/PCB/demo_mainboard.kicad_pcb", "line": 0,
                 "change": "加 %s 封装 (网 %s)" % (ref, rec["want_net"]), "raw": ""})

    # kind == "wrong" ⇒ 同号异网
    gov = _gov_row(rec["gov_rows"])
    if gov is None:
        return (None, "R6 UNATTR", "同号异网但找不到管辖的网表行", {})
    ok, marker, ev = authority_of(gov)
    n1 = rec["want_net"]
    corrob = [(k[0], k[1]) for k, v in ctx["want"].items()
              if v == n1 and k[0] != ref]
    if ok and corrob:
        return ("B", "R3 AUTH",
                "网表侧带权威标记 ⇒ 已拍的一侧是网表 ⇒ 板是旧接法 ⇒ 板那一趟重画/挪线",
                {"authority": marker, "evidence": ev, "corrob": corrob,
                 "file": "HW/PCB/demo_mainboard.kicad_pcb", "line": 0,
                 "change": ("把 %s pad%s 的网从 %s 改到 %s ⇒ 重画该焊盘的 stub 铜"
                            % (ref, rec["pad"], rec["board_net"], rec["want_net"]))})
    if ok and not corrob:
        return ("B", "R3 AUTH",
                "网表侧带权威标记 ⇒ 板是旧接法 (目标网无其它焊盘佐证 ⇒ ★复核后再动板★)",
                {"authority": marker, "evidence": ev, "corrob": [],
                 "file": "HW/PCB/demo_mainboard.kicad_pcb", "line": 0,
                 "change": ("把 %s pad%s 的网从 %s 改到 %s ⇒ 重画该焊盘的 stub 铜"
                            % (ref, rec["pad"], rec["board_net"], rec["want_net"]))})
    return (None, "R6 UNATTR",
            "同号异网但网表行没有权威标记 ⇒ 不自动归桶 ⇒ 强制人工判", {})


# ------------------------------------------------------------------ 主流程


def run_pipeline(board_path, netlist_path, registry_path):
    rows_all = read_netlist(netlist_path)
    want, src, placeholder, notes = netlist_pads(rows_all)
    bp = parse_board(board_path)
    have = board_pads(bp)

    missing, extra, wrong = [], [], []
    for k, net in want.items():
        if k not in have:
            missing.append((k, net))
        elif have[k] != net:
            wrong.append((k, net, have[k]))
    nc = set(k for k, v in have.items() if not v)
    extra = [e for e in extra if e[0] not in nc]
    for k, net in have.items():
        if k not in want and k not in nc:
            extra.append((k, net))
    bad_nc = sorted(k for k in nc if k[0] not in NC_ALLOWED)

    rows_by_ref = {}
    rows_by_net = {}
    for r in rows_all:
        rr = (r.get("ref") or "").strip()
        if rr:
            rows_by_ref.setdefault(rr, []).append(r)
        nn = (r.get("net") or "").strip()
        if nn:
            rows_by_net.setdefault(nn, []).append(r)

    ctx = {"want": want, "have": have, "src": src, "registry": load_registry(registry_path),
           "rows_by_ref": rows_by_ref, "rows_by_net": rows_by_net, "all_rows": rows_all,
           "board_refs": set(bp["fps"].keys())}

    recs = []
    for (ref, pad), net in sorted(want.items()):
        if (ref, pad) not in have:
            recs.append({"kind": "missing", "ref": ref, "pad": pad, "want_net": net,
                         "board_net": "", "gov_rows": src.get((ref, pad), [])})
    for (ref, pad), bnet in sorted(have.items()):
        if (ref, pad) in want or not bnet:
            continue
        gov = src.get((ref, pad), [])
        if not gov:
            # 网表里没有这个器件 ⇒ 找该器件在别的板上的行
            alt = [r for r in rows_all if (r.get("ref") or "").strip() == ref]
            hit = [r for r in alt if (r.get("net") or "").strip() == bnet] or alt
            gov = [(hit[0]["_line"], hit[0]["_raw"], (hit[0].get("net") or ""), hit[0])] \
                if hit else []
        recs.append({"kind": "extra", "ref": ref, "pad": pad, "want_net": "",
                     "board_net": bnet, "gov_rows": gov})
    for (ref, pad), wnet, bnet in sorted(wrong):
        recs.append({"kind": "wrong", "ref": ref, "pad": pad, "want_net": wnet,
                     "board_net": bnet, "gov_rows": src.get((ref, pad), [])})

    for rec in recs:
        bucket, rule, reason, ev = classify(rec, ctx)
        rec["bucket"] = bucket
        rec["rule"] = rule
        rec["reason"] = reason
        rec["ev"] = ev
        rec["cu"] = copper_stats(bp, rec["ref"], rec["pad"])
        marks, hs, single = net_class(rec["board_net"], rows_by_net)
        marks2, hs2, single2 = net_class(rec["want_net"], rows_by_net)
        rec["diff_marks"] = marks + marks2
        rec["hs"] = sorted(set(hs + hs2))
        rec["single_ended"] = single or single2
    return {"recs": recs, "want": want, "have": have, "missing": missing, "extra": extra,
            "wrong": wrong, "bad_nc": bad_nc, "nc": nc, "notes": notes,
            "placeholder": placeholder, "bp": bp, "ctx": ctx}


KIND_CN = {"missing": "缺失", "extra": "多余", "wrong": "同号异网"}


def bucket_of(rec):
    return rec.get("bucket")


def print_report(res, board_path, netlist_path, registry_path):
    recs = res["recs"]
    print("=" * 78)
    print("  ISS-340 · 板 ↔ 网表 差异归属判别闸 (★自己跑出 C1 三类差异 + 逐条归桶★)")
    print("=" * 78)
    print("  板     : %s" % board_path)
    print("  网表   : %s" % netlist_path)
    print("  登记表 : %s (★只读★)" % registry_path)
    print("  规模   : 网表推出焊盘 %d / 板上焊盘 %d (带网 %d, NC %d)"
          % (len(res["want"]), len(res["have"]), len(res["have"]) - len(res["nc"]),
             len(res["nc"])))
    print("  C1 差异: 缺失 %d · 多余 %d · 同号异网 %d ⇒ 合计 %d"
          % (len(res["missing"]), len(res["extra"]), len(res["wrong"]), len(recs)))
    if res["bad_nc"]:
        print("  ★非法 NC 焊盘: %d 个 ⇒ %s"
              % (len(res["bad_nc"]), ", ".join("%s pad%s" % k for k in res["bad_nc"][:8])))
    print("")
    for i, rec in enumerate(recs, 1):
        ref, pad = rec["ref"], rec["pad"]
        cu = rec["cu"]
        print("─" * 78)
        print("  [%d] %s %s pad%s   归桶 = %s   规则 = %s"
              % (i, KIND_CN[rec["kind"]], ref, pad, rec["bucket"] or "★未解释★", rec["rule"]))
        if rec["kind"] == "wrong":
            print("      网表应 = %s   板实 = %s" % (rec["want_net"], rec["board_net"]))
        elif rec["kind"] == "extra":
            print("      网表应 = (无此焊盘)   板实 = %s" % rec["board_net"])
        else:
            print("      网表应 = %s   板实 = (无此焊盘)" % rec["want_net"])
        # 网表侧证据
        for (ln, raw, net, _row) in rec["gov_rows"][:2]:
            print("      网表证据[实测]: HW/netlist_v1.csv:%d  net=%s" % (ln, net))
            print("                   原文: %s" % short(raw, 150))
        # 板上证据
        print("      板上证据[实测·板文件解析]: %s pad%s 实际网 = %s"
              % (ref, pad, cu["net"] or "(NC 无网)"))
        print("                   焊盘有铜 = %s · 直连铜(走线段)长 = %.3f mm · "
              "该网总走线 = %.3f mm · 直连段数 = %d · 焊盘内过孔 = %d · 该网有铜区 = %s"
              % ("是" if cu["has_copper"] else "否", cu["stub_mm"], cu["net_total_mm"],
                 cu["segments"], cu["vias"], "是" if cu["zone"] else "否"))
        if rec["diff_marks"] or rec["hs"]:
            print("      阻抗/速率[实测·网表原文]: %s%s"
                  % (" ; ".join(rec["diff_marks"][:2]) or "",
                     (" ; 高速网名提示 %s" % rec["hs"]) if rec["hs"] else ""))
        print("      归桶理由: %s" % rec["reason"])
        ev = rec["ev"]
        if rec["bucket"] == "C":
            print("      need key = %s  (state/fragments/pm.yaml:%d)" % (ev.get("need_key"),
                                                                        ev.get("need_line")))
            print("      待拍题  : %s" % ev.get("need_item"))
        elif rec["bucket"] == "A":
            print("      A 桶修法: %s:%s  ⇒ %s" % (ev.get("file"), ev.get("line"),
                                                  ev.get("change")))
            print("                 原文: %s" % short(ev.get("raw", ""), 130))
        elif rec["bucket"] == "B":
            print("      B 桶修法: %s ⇒ %s" % (ev.get("file"), ev.get("change")))
            if ev.get("authority"):
                print("                 权威依据: %s (evidence %s)"
                      % (ev["authority"], ev.get("evidence", "")))
            if ev.get("corrob"):
                print("                 目标网被其它焊盘佐证: %s"
                      % ", ".join("%s pad%s" % c for c in ev["corrob"][:6]))
        print("")
    # ---- 末尾 4 行 ----
    A = [r for r in recs if bucket_of(r) == "A"]
    B = [r for r in recs if bucket_of(r) == "B"]
    C = [r for r in recs if bucket_of(r) == "C"]
    U = [r for r in recs if bucket_of(r) is None]
    print("① A 桶(网表侧错 ⇒ 改网表就够, ★板 md5 不用动★) = %d 条" % len(A))
    for r in A:
        ev = r["ev"]
        print("   · %s pad%s ⇒ 改 %s:%s ⇒ %s"
              % (r["ref"], r["pad"], ev.get("file"), ev.get("line"), ev.get("change")))
    if not A:
        print("   · (无)")
    print("② B 桶(板侧错 ⇒ 必须动板, 进板那一趟一次做完) = %d 条" % len(B))
    for r in B:
        if r["kind"] == "wrong":
            act = ("把 %s pad%s 的网从 %s 改到 %s ⇒ 重画该焊盘的 stub 铜 "
                   "(当前直连铜长 %.3f mm)"
                   % (r["ref"], r["pad"], r["board_net"], r["want_net"], r["cu"]["stub_mm"]))
        elif r["kind"] == "missing":
            act = r["ev"].get("change", "补焊盘")
        else:
            act = r["ev"].get("change", "板侧删除")
        tag = "受控阻抗/差分对成员网 ⇒ 动铜时不许破坏对内匹配" if (r["diff_marks"] or r["hs"]) \
            else ("单端低速/电源域 ⇒ 不触及高速/差分铜"
                  + (" (网表原文写明「单端」)" if r.get("single_ended") else ""))
        print("   · %s pad%s ⇒ %s" % (r["ref"], r["pad"], act))
        print("       铜/速率: %s ; 要不要重跑 DRC + 重出 Gerber: ★要★" % tag)
    if not B:
        print("   · (无)")
    print("③ C 桶(等老板拍板 ⇒ 本闸只列 need key + 题, 不代拍) = %d 条" % len(C))
    for r in C:
        print("   · %s pad%s ⇒ need key = %s (state/fragments/pm.yaml:%d)"
              % (r["ref"], r["pad"], r["ev"].get("need_key"), r["ev"].get("need_line")))
        print("       题: %s" % r["ev"].get("need_item"))
    if not C:
        print("   · (无)")
    keys = []
    for r in C:
        k = r["ev"].get("need_key")
        if k and k not in keys:
            keys.append(k)
    if keys:
        must = ("板那一趟开工前必须先落: %s (★C 桶没拍板之前不许开工: 拍「留位」= 改网表 + "
                "重生成脚表/BOM, 拍「下板」= 板那一趟新增一条板侧动作★)" % "; ".join(keys))
    else:
        must = ("板那一趟开工前必须先落: C 桶为空 ⇒ 无前置待拍项, ★但板那一趟开工前仍须确认 "
                "B 桶每条是否已被 §ISS-283 裁决覆盖★")
    print("④ %s" % must)
    print("-" * 78)
    if U:
        print("❌ 有 %d 条差异无法自动归桶 (R6 UNATTR) ⇒ 需人工判" % len(U))
    else:
        print("✅ 全部 %d 条差异均已归桶 (A=%d / B=%d / C=%d) ⇒ 无未解释差异"
              % (len(recs), len(A), len(B), len(C)))
    return len(U)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    board = os.path.abspath(args[0]) if args else DEFAULT_BOARD
    netlist = DEFAULT_NETLIST
    registry = DEFAULT_REGISTRY
    for a in argv[1:]:
        if a.startswith("--netlist="):
            netlist = os.path.abspath(a.split("=", 1)[1])
        elif a.startswith("--registry="):
            registry = os.path.abspath(a.split("=", 1)[1])
        elif a.startswith("--netlist") or a.startswith("--registry"):
            pass
    if "--selftest" in argv:
        return do_selftest()
    # "--netlist X" 分离写法
    for i, a in enumerate(argv):
        if a == "--netlist" and i + 1 < len(argv):
            netlist = os.path.abspath(argv[i + 1])
        if a == "--registry" and i + 1 < len(argv):
            registry = os.path.abspath(argv[i + 1])
    try:
        res = run_pipeline(board, netlist, registry)
    except Exception as e:                                   # 运行错误 ⇒ rc=1
        sys.stderr.write("运行错误: %r\n" % (e,))
        return 1
    n_unattr = print_report(res, board, netlist, registry)
    return 2 if n_unattr else 0


# ------------------------------------------------------------------ 自检


def _patch_pad_net(board_text, ref, padnum, old_net, new_net):
    """★在板文件文本里把某个器件的某个焊盘的网名换掉 (★只作用于临时副本★)"""
    lines = board_text.splitlines(True)
    out, i = [], 0
    in_fp = False
    fp_ref = None
    while i < len(lines):
        ln = lines[i]
        if not in_fp and ln.lstrip().startswith("(footprint"):
            in_fp = True
            fp_ref = None
            block = []
        if in_fp:
            block.append(ln)
            m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', ln)
            if m:
                fp_ref = m.group(1)
            if ln.rstrip().endswith(")") and ln.startswith("\t)") and fp_ref is not None:
                in_fp = False
                blk = "".join(block)
                if fp_ref == ref:
                    pat = re.compile(r'(\(pad\s+"%s"[\s\S]*?)\(net\s+"%s"\)'
                                     % (re.escape(padnum), re.escape(old_net)))
                    blk2, n = pat.subn(lambda m: m.group(1) + '(net "%s")' % new_net, blk, count=1)
                    if n == 0:
                        raise RuntimeError("没找到 %s pad%s 的 net=%s" % (ref, padnum, old_net))
                    block = [blk2]
                out.append("".join(block))
                block = []
                i += 1
                continue
        else:
            out.append(ln)
        i += 1
    return "".join(out)


def do_selftest():
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        print("  [%s] %s%s" % ("✅" if cond else "❌", name, ("  ← " + detail) if detail else ""))
        if not cond:
            ok = False

    board = DEFAULT_BOARD
    netlist = DEFAULT_NETLIST
    registry = DEFAULT_REGISTRY
    if not (os.path.exists(board) and os.path.exists(netlist)):
        print("❌ 自检失败: 板/网表不在位")
        return 1

    md5_before, mt_before = md5_of(board), mtime_of(board)

    # ---- T1 正向: 当前板 + 当前网表 ⇒ 5 条差异被完整复现且归桶总数 = 5
    print("── T1 正向: 当前板 + 当前网表 ⇒ 5 条差异被完整复现且全部归桶")
    res = run_pipeline(board, netlist, registry)
    n = len(res["recs"])
    A = sum(1 for r in res["recs"] if r["bucket"] == "A")
    B = sum(1 for r in res["recs"] if r["bucket"] == "B")
    C = sum(1 for r in res["recs"] if r["bucket"] == "C")
    U = sum(1 for r in res["recs"] if r["bucket"] is None)
    check("差异条数 = 5", n == 5, "实得 %d (缺失%d/多余%d/同号异网%d)"
          % (n, len(res["missing"]), len(res["extra"]), len(res["wrong"])))
    check("归桶总数 = 5 (无未解释)", A + B + C == 5 and U == 0,
          "A=%d B=%d C=%d 未解释=%d" % (A, B, C, U))
    check("桶分布 = A0/B3/C2", (A, B, C) == (0, 3, 2), "A=%d B=%d C=%d" % (A, B, C))

    # ---- T2 反向: 消掉一条差异 ⇒ 该条从桶里消失且总数减 1 (证明是算出来的)
    print("── T2 反向: 把 Q_PG pad1 的网改对 ⇒ 该条差异消失且总数减 1")
    tmpdir = tempfile.mkdtemp(prefix="iss340_gate_")
    try:
        tmp_board = os.path.join(tmpdir, "board_patched.kicad_pcb")
        with open(board, encoding="utf-8") as f:
            txt = f.read()
        patched = _patch_pad_net(txt, "Q_PG", "1", "PWR_ON", "PWR_GOOD")
        with open(tmp_board, "w", encoding="utf-8") as f:
            f.write(patched)
        res2 = run_pipeline(tmp_board, netlist, registry)
        n2 = len(res2["recs"])
        still = [r for r in res2["recs"] if r["ref"] == "Q_PG" and r["pad"] == "1"]
        B2 = sum(1 for r in res2["recs"] if r["bucket"] == "B")
        check("总数 5 → 4", n2 == 4, "实得 %d" % n2)
        check("Q_PG pad1 从桶里消失", len(still) == 0,
              "仍报 %s" % [("%s pad%s" % (r["ref"], r["pad"])) for r in still])
        check("B 桶 3 → 2", B2 == 2, "实得 %d" % B2)
        check("Q_PG pad3 仍在 (只消掉一条)", any(r["ref"] == "Q_PG" and r["pad"] == "3"
                                                for r in res2["recs"]))
        # ---- T5 三类差异都可产出: 网表多一行 ⇒ MISSING 且归 A
        print("── T5 合成: 网表多一行 (伪器件行) ⇒ 差异类型=缺失 且归 A 桶")
        tmp_nl = os.path.join(tmpdir, "netlist_extra.csv")
        with open(netlist, encoding="utf-8") as f:
            nl = f.read().splitlines()
        nl.append("P1,GND,C_SYNTH_ALIAS,NET_SYNTH_ALIAS,C_SYNTH_ALIAS,别名,NET,DNP,"
                  "[推算],,★合成行: 网表多了一行 (伪器件 type=NET)★,X-SYNTH,MAIN_PCB,,")
        with open(tmp_nl, "w", encoding="utf-8") as f:
            f.write("\n".join(nl) + "\n")
        res3 = run_pipeline(board, tmp_nl, registry)
        miss = [r for r in res3["recs"] if r["kind"] == "missing"]
        check("缺失类差异被检出", len(miss) >= 1, "检出 %d 条" % len(miss))
        check("合成缺失行归 A 桶", any(r["bucket"] == "A" for r in miss),
              "归桶 %s" % [r["bucket"] for r in miss])
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    # ---- T3 归桶逻辑: 3 个合成案例各归各桶
    print("── T3 归桶逻辑: 造 3 个合成案例 (网表多一行 / 板网不同 / 等决策) 各归各桶")
    ctx = {"want": {("R_FAKE", "1"): "GND"}, "have": {}, "src": {},
           "registry": [("boss_synth_decide_20990101", 1, "★合成待拍项★ C_SYNTH_X 留还是不留")],
           "rows_by_ref": {}, "rows_by_net": {}, "all_rows": [],
           "board_refs": set()}
    fake_gov = [(123, "P1,GND,C_SYNTH_ALIAS,NET_SYNTH_ALIAS,C_SYNTH_ALIAS,别名,NET,DNP",
                 "GND",
                 {"_line": 123, "_raw": "P1,GND,C_SYNTH_ALIAS,NET_SYNTH_ALIAS,C_SYNTH_ALIAS,别名,"
                                       "NET,DNP,[推算],,★合成行: 网表多了一行★,X-SYNTH,MAIN_PCB,,",
                  "type": "NET", "net": "GND", "note": "★合成行★", "evidence": "[推算]",
                  "ref": "C_SYNTH_ALIAS"})]
    rec_a = {"kind": "missing", "ref": "C_SYNTH_ALIAS", "pad": "1", "want_net": "GND",
             "board_net": "", "gov_rows": fake_gov}
    b = classify(rec_a, ctx)
    check("合成① 网表多一行 ⇒ A 桶", b[0] == "A", "实得 %s (%s)" % (b[0], b[1]))
    fake_gov2 = [(456, "P1,NET_X,R_FAKE,NET_X,R_FAKE,x,R,必装,[官方],,★老板拍板「写法 A」★",
                  "NET_X",
                  {"_line": 456,
                   "_raw": "P1,NET_X,R_FAKE,NET_X,R_FAKE,x,R,必装,[官方],,★老板拍板「写法 A」★",
                   "type": "R", "net": "NET_X", "note": "★老板拍板「写法 A」★",
                   "evidence": "[官方]", "ref": "R_FAKE"})]
    ctx2 = dict(ctx)
    ctx2["want"] = {("R_FAKE", "1"): "NET_X", ("R_OTHER", "2"): "NET_X"}
    rec_b = {"kind": "wrong", "ref": "R_FAKE", "pad": "1", "want_net": "NET_X",
             "board_net": "NET_Y", "gov_rows": fake_gov2}
    b2 = classify(rec_b, ctx2)
    check("合成② 板网不同 ⇒ B 桶", b2[0] == "B", "实得 %s (%s)" % (b2[0], b2[1]))
    rec_c = {"kind": "extra", "ref": "C_SYNTH_X", "pad": "1", "want_net": "",
             "board_net": "GND", "gov_rows": []}
    b3 = classify(rec_c, ctx)
    check("合成③ 等决策 ⇒ C 桶", b3[0] == "C", "实得 %s (%s)" % (b3[0], b3[1]))

    # ---- T4 板文件零改证明
    print("── T4 板文件零改证明 (selftest 全程板 md5 / mtime 不变)")
    md5_after, mt_after = md5_of(board), mtime_of(board)
    check("板 md5 不变", md5_before == md5_after, "%s → %s" % (md5_before, md5_after))
    check("板 mtime 不变", mt_before == mt_after, "%s → %s" % (mt_before, mt_after))

    print("-" * 78)
    if ok:
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
