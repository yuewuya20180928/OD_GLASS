#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_debug_header_fw_impact.py -- ISS-378 · sw-lead
============================================================================
J_DEBUG / J_UART 排针换 land 后的【固件影响面】+ JTAG 口径冲突收敛的机器判据。

用法:
  python3 SW/tools/check_debug_header_fw_impact.py             # 跑 W0~W8
  python3 SW/tools/check_debug_header_fw_impact.py --selftest  # 反向用例自测
  python3 SW/tools/check_debug_header_fw_impact.py --json      # 机器可读输出

退出码: 0 = W0~W8 全绿 · 1 = 有判据红 · 2 = 用法/环境错

★**本闸只读**: 不写板 · 不写网表 · 不改既有闸 · 不改已签收页 · 不改既有口径页正文 ·
不挂链 · 不外发 · 不签台账。沙盒只落 tmp/iss378_sbx/ 与 logs/iss378/。

★**设计原则 (★每条判据都必须 fail-closed★)**:
  ① 本闸自己从 `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` **重新读**,
     **不许抄页上的表** ⇒ 页面漂了当场红。
  ② SoC / SoM 两侧的 JTAG 事实**由本闸自己跑 grep 实测出来**, 不许抄页上的数。
  ③ 「需改代码」的行必须给出 **文件 + 行号 + 函数名**, 且本闸**核实那个文件
     确实存在、那行确实存在、那个函数确实在那行或它之前定义过**。
  ④ 零挂起措辞: 页面里不许出现任何「等外部答复」形态的挂账。
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # .../SW/tools
SWROOT = os.path.dirname(HERE)                            # .../SW
PROJ = os.path.dirname(SWROOT)                            # .../smart_glasses
PAGE_REL = os.path.join("SW", "BOARD_ONEPASS_DEBUG_HEADER_FW_IMPACT.md")

# ---------------------------------------------------------------- 判据常量
NATURES = ("无", "仅物理针序", "需改代码")
EVIDENCE_WHITELIST = ("官网", "实测", "媒体", "推算", "0数据")
REQUIRED_NETS = (
    "JTAG_TCK", "JTAG_TMS", "JTAG_TDI", "JTAG_TDO",
    "JTAG_TCK_SOC", "JTAG_TMS_SOC", "JTAG_TDI_SOC", "JTAG_TDO_SOC",
    "UART_TX", "UART_RX",
    "BOOT_N", "KEY_PWR", "KEY_VOL_P", "KEY_VOL_M", "KEY_CAM",
    "RESET_N", "RESET_N_SOC", "USB_CC1", "USB_CC2",
)
ROUTE_NUMBERS = ("①", "②", "③")
ROUTE_KEYWORDS = (("①", "改口径"), ("②", "改网表"), ("③", "换 SoM"))
CHAIN_KEYS = ("USB", "UART", "JTAG")

# ★**零挂起措辞白名单 (★源码里用拼接造, 避免自匹配★)** ★
FORBIDDEN_HANGING = (
    "等" + "原厂回信",
    "待" + "外部确认",
    "等" + "外部回复",
    "等待" + "外部",
    "待" + "外部回复",
    "等" + "外部确认",
    "等" + "原厂答复",
    "挂" + "外部待回复",
)
# ★**证据等级白名单外的标签 (★拼接造, 避免自匹配★)** ★
BAD_EVIDENCE_TAG = "[" + "猜" + "测]"

RELS = {
    "page": PAGE_REL,
    "netlist": os.path.join("HW", "netlist_v1.csv"),
    "pins": os.path.join("HW", "netlist_v1_pins.csv"),
    "bom": os.path.join("HW", "BOM_v1.csv"),
    "board": os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb"),
    "som_pin_table": os.path.join("HW", "PCB", "FET3572C_PIN_TABLE.csv"),
    "soc_pins_csv": os.path.join("HW", "RK3572_PIN_TABLE", "rk3572_pins.csv"),
    "soc_datasheet_txt": os.path.join("HW", "RK3572_PIN_TABLE", "rk3572_datasheet_V1.1.txt"),
    "gate_check": os.path.join("state", "gate_check.py"),
}


# ---------------------------------------------------------------- 小工具
def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def section(text, start_pat, end_pat):
    """取一节正文 (★start_pat 不匹配 ⇒ 返回空串 ⇒ 判据红★)."""
    m = re.search(start_pat, text, re.M)
    if not m:
        return ""
    rest = text[m.end():]
    e = re.search(end_pat, rest, re.M)
    return rest[:e.start()] if e else rest


def strip_md(s):
    s = s.strip()
    s = s.replace("**", "").replace("★", "")
    s = s.replace("`", "").replace("　", " ")
    return s.strip()


def split_block(text):
    """返回 (start, end, json_str) —— ```json iss378_contract ... ``` 块。"""
    m = re.search(r"```json\s+iss378_contract\s*(\{.*?\})\s*```", text, re.S)
    if not m:
        return None
    return m.start(), m.end(), m.group(1)


def parse_contract(page_text):
    b = split_block(page_text)
    if not b:
        raise RuntimeError("页里找不到 ```json iss378_contract 块")
    return json.loads(b[2])


def replace_block(text, obj):
    b = split_block(text)
    if not b:
        raise RuntimeError("页里找不到 ```json iss378_contract 块")
    return text[:b[0]] + "```json iss378_contract\n" + json.dumps(
        obj, ensure_ascii=False, indent=2) + "\n```" + text[b[1]:]


ROW_RE = re.compile(r"^\|\s*`([A-Za-z0-9_\*]+)`\s*\|")


def parse_net_rows(page_text):
    """★从 §1-1 逐网表里抽出每一行 (★不许抄机器块★)."""
    sec = section(page_text, r"^###\s+§1-1", r"^###\s+§1-2")
    rows = []
    for line in sec.split("\n"):
        if not line.startswith("|"):
            continue
        if not ROW_RE.match(line.strip()):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 9:
            rows.append({"_bad_cells": len(cells), "_raw": line, "net": None})
            continue
        rows.append({
            "net": cells[0].strip("`"),
            "nodes": cells[1],
            "pads_cell": cells[2],
            "fw_use": cells[3],
            "changed": cells[4],
            "nature": strip_md(cells[5]),
            "change_cell": cells[6],
            "evidence": cells[7],
            "source": cells[8],
        })
    return rows


def load_netlist(root):
    """net -> [(node1, node2, ref), ...]"""
    out = {}
    path = os.path.join(root, RELS["netlist"])
    with open(path, encoding="utf-8", errors="ignore", newline="") as f:
        for r in csv.reader(f):
            if len(r) < 5:
                continue
            net = r[1].strip()
            if not net:
                continue
            out.setdefault(net, []).append((r[2].strip(), r[3].strip(), r[4].strip()))
    return out


def load_pins(root):
    """pin_id -> net"""
    out = {}
    path = os.path.join(root, RELS["pins"])
    with open(path, encoding="utf-8", errors="ignore", newline="") as f:
        rd = csv.DictReader(f)
        for r in rd:
            pid = (r.get("pin_id") or "").strip()
            if pid:
                out[pid] = (r.get("net") or "").strip()
    return out


# ---------------------------------------------------------------- 闸自己跑的实测
def measure_soc_side(root):
    """★自己 grep SoC 侧官方引脚表 (★不许抄页上的数★)."""
    path = os.path.join(root, RELS["soc_pins_csv"])
    hits, names = 0, set()
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "jtag" in line.lower():
                hits += 1
                for m in re.finditer(r"JTAG_[A-Z0-9_]+", line):
                    names.add(m.group(0))
    txt = ""
    dpath = os.path.join(root, RELS["soc_datasheet_txt"])
    if os.path.exists(dpath):
        txt = read_text(dpath)
    return {
        "jtag_hit_lines": hits,
        "mux_names": sorted(names),
        "has_tck": any(n.startswith("JTAG_TCK") for n in names),
        "has_tms": any(n.startswith("JTAG_TMS") for n in names),
        "has_tdi": any(n.startswith("JTAG_TDI") for n in names),
        "has_tdo": any(n.startswith("JTAG_TDO") for n in names),
        "datasheet_tdi_tdo_hits": len(re.findall(r"JTAG_TDI|JTAG_TDO", txt)),
        "datasheet_has_jtag_iface": ("JTAG interface for debug" in txt),
    }


def measure_som_side(root):
    """★自己 grep SoM 侧逐针表 (★不许抄页上的数★)."""
    path = os.path.join(root, RELS["som_pin_table"])
    hits = 0
    data_rows = 0
    with open(path, encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            data_rows += 1
            if "jtag" in line.lower():
                hits += 1
    return {"jtag_hits": hits, "data_rows": data_rows}


def measure_netlist_soc_endpoints(root):
    nl = load_netlist(root)
    out = {}
    for n in ("JTAG_TCK_SOC", "JTAG_TMS_SOC", "JTAG_TDI_SOC", "JTAG_TDO_SOC"):
        eps = set()
        for n1, n2, _ in nl.get(n, []):
            eps.add(n1)
            eps.add(n2)
        out[n] = sorted(eps)
    return out


def board_fingerprint(root):
    p = os.path.join(root, RELS["board"])
    st = os.stat(p)
    return {
        "board_md5": md5(p),
        "board_mtime_ns": st.st_mtime_ns,
        "board_size": st.st_size,
    }


# ---------------------------------------------------------------- 判据
def w0_table_matches_reality(root, page_text, contract, netlist, pins):
    """★W0: §1 逐网表逐行与网表/脚表实读一致 (自己重读, 不许抄表)."""
    rows = parse_net_rows(page_text)
    errs = []
    if not rows:
        return False, "§1-1 逐网表解析出 0 行 (页结构变了?)"
    bad = [r for r in rows if r.get("net") is None]
    if bad:
        errs.append("有 %d 行的列数不是 9" % len(bad))
    got = [r["net"] for r in rows if r.get("net")]
    if len(got) != len(set(got)):
        errs.append("逐网表里有重复网名")
    missing = [n for n in REQUIRED_NETS if n not in got]
    if missing:
        errs.append("逐网表缺这些必需网: %s" % ",".join(missing))
    # 逐行核对: 网名在网表里存在 / 两端节点与网表逐字对得上 / pad 与脚表对得上
    for r in rows:
        net = r.get("net")
        if not net:
            continue
        if net not in netlist:
            errs.append("%s: 网表里没有这条网" % net)
            continue
        node_blob = " | ".join("%s|%s" % (a, b) for a, b, _ in netlist[net])
        for tok in [t.strip() for t in re.split(r"[/、,，]", r["nodes"]) if t.strip()]:
            tok = strip_md(tok)
            if not tok:
                continue
            if tok not in node_blob:
                errs.append("%s: 端点 `%s` 在网表该网的节点里查不到" % (net, tok))
        for pid in re.findall(r"(?:J_DEBUG|J_UART)\.pin\d+", r["pads_cell"]):
            if pid not in pins:
                errs.append("%s: 脚表里没有 %s" % (net, pid))
            elif pins[pid] != net:
                errs.append("%s: 脚表 %s 的网是 %s, 与本页写的 %s 不符"
                             % (net, pid, pins[pid], net))
    # 页面表 与 机器块 必须一一对应
    blk = {x.get("net"): x for x in contract.get("net_rows", [])}
    for net, b in blk.items():
        if net not in got:
            errs.append("机器块有 %s 但页面表没有" % net)
    for r in rows:
        net = r.get("net")
        if not net or net not in blk:
            continue
        b = blk[net]
        if strip_md(b.get("nature", "")) != r["nature"]:
            errs.append("%s: 页面表变化性质(%s) 与机器块(%s) 不符"
                        % (net, r["nature"], b.get("nature")))
        pads = sorted(set(re.findall(r"(?:J_DEBUG|J_UART)\.pin\d+", r["pads_cell"])))
        bpads = sorted(b.get("pads", []) or [])
        if pads != bpads:
            errs.append("%s: 页面表 pad(%s) 与机器块(%s) 不符" % (net, pads, bpads))
    for net in blk:
        if net not in got:
            errs.append("机器块有 %s 但页面表没有" % net)
    if errs:
        return False, "; ".join(errs[:8]) + (" ... (共 %d 条)" % len(errs))
    return True, "§1 逐网表 %d 行与网表/脚表实读一致" % len(rows)


def w1_nature_present(page_text, contract):
    rows = parse_net_rows(page_text)
    errs = []
    for r in rows:
        if r.get("net") is None:
            continue
        n = r["nature"]
        if not n:
            errs.append("%s: 变化性质留空" % r["net"])
        elif n not in NATURES:
            errs.append("%s: 变化性质=%s 不在三分类里 %s" % (r["net"], n, NATURES))
    for x in contract.get("net_rows", []):
        n = strip_md(x.get("nature", ""))
        if not n:
            errs.append("机器块 %s: 变化性质留空" % x.get("net"))
        elif n not in NATURES:
            errs.append("机器块 %s: 变化性质=%s 不在三分类里" % (x.get("net"), n))
    if errs:
        return False, "; ".join(errs[:8])
    return True, "全部 %d 行的变化性质都在三分类里且非空" % len(rows)


def w2_code_change_locations(root, page_text, contract):
    """★W2: 「需改代码」的行必须给出 文件 + 行号 + 函数名, 且文件/行/函数都要存在."""
    errs = []
    rows = {r["net"]: r for r in parse_net_rows(page_text) if r.get("net")}
    n_checked = 0
    for x in contract.get("net_rows", []):
        if strip_md(x.get("nature", "")) != "需改代码":
            continue
        n_checked += 1
        net = x.get("net")
        f = x.get("change_file") or ""
        ln = x.get("change_line")
        fn = x.get("change_func") or ""
        if not f or not isinstance(ln, int) or not fn:
            errs.append("%s: 需改代码行缺 文件/行号/函数名" % net)
            continue
        path = os.path.join(root, f)
        if not os.path.isfile(path):
            errs.append("%s: change_file `%s` 不存在" % (net, f))
            continue
        lines = read_text(path).split("\n")
        if ln < 1 or ln > len(lines):
            errs.append("%s: change_line %s 不在 `%s` 的行范围内 (1..%d)"
                        % (net, ln, f, len(lines)))
            continue
        defpat = re.compile(r"^\s*def\s+%s\s*\(" % re.escape(fn))
        defline = None
        for i, l in enumerate(lines[:ln], start=1):
            if defpat.match(l):
                defline = i
                break
        if defline is None:
            errs.append("%s: 函数 `%s` 在 `%s` 的第 %s 行或之前没有定义"
                        % (net, fn, f, ln))
            continue
        # 页面表那一行的「若需改」单元格必须写出同一个文件 + 行号
        r = rows.get(net)
        if r is None:
            errs.append("%s: 页面表没有这一行" % net)
            continue
        cell = r["change_cell"]
        if f not in cell:
            errs.append("%s: 页面表『若需改』列没写文件 `%s`" % (net, f))
        if ("L%d" % ln) not in cell and (str(ln) not in cell):
            errs.append("%s: 页面表『若需改』列没写行号 %s" % (net, ln))
        if fn not in cell:
            errs.append("%s: 页面表『若改』列没写函数名 `%s`" % (net, fn))
    if n_checked == 0:
        return False, "没有任何一行标了「需改代码」⇒ 判据自毁 (本单至少应有 JTAG/UART 行的机器件改动登记)"
    if errs:
        return False, "; ".join(errs[:8])
    return True, "%d 条「需改代码」行的 文件/行号/函数名 全部核实存在" % n_checked


def w3_rescue_chains(page_text, contract):
    sec = section(page_text, r"^##\s+§2\b", r"^##\s+§3\b")
    errs = []
    if not sec:
        return False, "页里找不到 §2"
    for k in CHAIN_KEYS:
        if ("%s 链" % k) not in sec:
            errs.append("§2 里没有 %s 链" % k)
    wc = contract.get("worst_case_chain")
    if wc not in CHAIN_KEYS:
        errs.append("机器块 worst_case_chain=%r 不在 USB/UART/JTAG 里" % wc)
    worst_line = None
    for line in sec.split("\n"):
        if "最坏情况下只剩" in line:
            worst_line = line
            break
    if worst_line is None:
        errs.append("§2 里没有「最坏情况下只剩…」的结论句")
    elif wc and wc not in worst_line:
        errs.append("§2 的「最坏情况下只剩」结论句里没有点名最坏链 %s" % wc)
    chains = contract.get("rescue_chains") or []
    if sorted(chains) != sorted(CHAIN_KEYS):
        errs.append("机器块 rescue_chains=%r 不是 USB/UART/JTAG 三条" % chains)
    if errs:
        return False, "; ".join(errs[:8])
    return True, "§2 三条链 + 最坏结论句齐全 (最坏只剩 %s)" % wc


def w4_three_routes(page_text, contract):
    sec = section(page_text, r"^##\s+§3\b", r"^##\s+§4\b")
    errs = []
    if not sec:
        return False, "页里找不到 §3"
    found = {}
    for m in re.finditer(r"^####\s*★?路线\s*([①②③])(.*)$", sec, re.M):
        num = m.group(1)
        tail = m.group(2)
        rest = sec[m.end():]
        nxt = re.search(r"^#{2,4}\s", rest, re.M)
        body = rest[:nxt.start()] if nxt else rest
        found[num] = (tail, body)
    for num, kw in ROUTE_KEYWORDS:
        if num not in found:
            errs.append("§3 里没有「路线 %s」小节" % num)
            continue
        tail, body = found[num]
        if kw not in tail and kw not in body:
            errs.append("§3 的路线 %s 小节里没有写清它是什么 (%s)" % (num, kw))
        if "代价" not in body:
            errs.append("§3 的路线 %s 小节里没有『代价』" % num)
    routes = contract.get("resolution_routes") or []
    if len(routes) != 3:
        errs.append("机器块 resolution_routes 只有 %d 条 (必须 3 条)" % len(routes))
    else:
        for (num, kw), r in zip(ROUTE_KEYWORDS, routes):
            if kw.replace(" ", "") not in str(r).replace(" ", ""):
                errs.append("机器块第 %s 条路线 (%r) 与关键词 %s 不符" % (num, r, kw))
    if errs:
        return False, "; ".join(errs[:8])
    return True, "§3 三条路线 (①改口径/②改网表/③换 SoM) 齐全且各有代价"


def w5_jtag_facts_measured(root, page_text, contract):
    """★W5: SoC / SoM 两侧 JTAG 的事实必须由闸自己跑 grep 实测出来, 且结论不许含糊."""
    soc = measure_soc_side(root)
    som = measure_som_side(root)
    eps = measure_netlist_soc_endpoints(root)
    errs = []
    cs = contract.get("soc_side") or {}
    ss = contract.get("som_side") or {}
    # ---- SoC 侧
    if cs.get("jtag_hit_lines") != soc["jtag_hit_lines"]:
        errs.append("SoC 侧: 页写 %r 行 JTAG 命中, 闸实测 %d"
                    % (cs.get("jtag_hit_lines"), soc["jtag_hit_lines"]))
    for k in ("has_tck", "has_tms", "has_tdi", "has_tdo"):
        if bool(cs.get(k)) != bool(soc[k]):
            errs.append("SoC 侧: 页写 %s=%r, 闸实测 %r" % (k, cs.get(k), soc[k]))
    if not soc["has_tck"] or not soc["has_tms"]:
        errs.append("SoC 侧: 实测没有 TCK/TMS mux 名")
    if soc["has_tdi"] or soc["has_tdo"]:
        errs.append("SoC 侧: 实测竟然有 TDI/TDO mux 名 ⇒ 结论必须重写")
    # ---- SoM 侧
    if ss.get("jtag_hits") != som["jtag_hits"]:
        errs.append("SoM 侧: 页写 %r 处 JTAG 命中, 闸实测 %d"
                    % (ss.get("jtag_hits"), som["jtag_hits"]))
    concl = str(ss.get("conclusion") or "")
    if som["jtag_hits"] == 0:
        if "无 JTAG 引出" not in concl:
            errs.append("SoM 侧实测 JTAG 命中 0, 机器块结论却不是「无 JTAG 引出」: %r" % concl)
        if "SoM 侧有 JTAG 引出" in concl:
            errs.append("SoM 侧实测 JTAG 命中 0, 机器块结论却说有引出")
    else:
        if "有 JTAG 引出" not in concl:
            errs.append("SoM 侧实测 JTAG 命中 %d, 机器块结论没说有引出: %r"
                        % (som["jtag_hits"], concl))
    # ---- §3 正文里的 SoM 侧结论必须与实测一致 (不许含糊 / 不许反转)
    sec3 = section(page_text, r"^##\s+§3\b", r"^##\s+§4\b")
    if concl and concl not in sec3:
        errs.append("§3 正文里找不到机器块写的 SoM 侧结论句「%s」" % concl)
    if som["jtag_hits"] == 0 and "SoM 侧有 JTAG 引出" in sec3:
        errs.append("§3 正文把 SoM 侧结论写成「有 JTAG 引出」, 与实测 (命中 0) 反了")
    # ---- 网表侧 SoM 端点
    ce = contract.get("netlist_soc_endpoints") or {}
    for n in ("JTAG_TCK_SOC", "JTAG_TMS_SOC", "JTAG_TDI_SOC", "JTAG_TDO_SOC"):
        if ce.get(n) != "SoC_NC":
            errs.append("网表 %s: 机器块写 %r, 期望 SoC_NC" % (n, ce.get(n)))
        if set(eps.get(n) or []) != {"SoC_NC", "R_JTAG_%s" % n.split("_")[1]}:
            errs.append("网表 %s: 闸实测端点 = %r, 与 SoC_NC + 串阻 不符" % (n, eps.get(n)))
    # ---- §4 必须同时出现 TCK/TMS 与 TDI/TDO 两个方向
    sec4 = section(page_text, r"^##\s+§4\b", r"^##\s+§5\b")
    for tok in ("TCK", "TMS", "TDI", "TDO"):
        if tok not in sec4:
            errs.append("§4 里没有 %s 这个方向" % tok)
    if errs:
        return False, "; ".join(errs[:8])
    return True, ("SoC 实测 %d 行 JTAG (TCK/TMS 有 · TDI/TDO 无) + SoM 实测 %d 命中 + 网表四条 SoC_NC ⇒ 结论一致"
                   % (soc["jtag_hit_lines"], som["jtag_hits"]))


def w6_evidence_hygiene(page_text):
    errs = []
    tags = {}
    for m in re.finditer(r"\[([^\]\n]{1,12})\]", page_text):
        s = m.group(1)
        tags[s] = tags.get(s, 0) + 1
    for s, n in sorted(tags.items()):
        if s not in EVIDENCE_WHITELIST:
            errs.append("证据等级标签 [%s] 不在五级白名单里 (%d 处)" % (s, n))
    for bad in FORBIDDEN_HANGING:
        if bad in page_text:
            errs.append("页面出现零挂起措辞「%s」" % bad)
    if BAD_EVIDENCE_TAG in page_text:
        errs.append("页面出现白名单外证据等级 %s" % BAD_EVIDENCE_TAG)
    # [0数据] 处必须同时给出降级方案
    sec44 = section(page_text, r"^###\s+§4-4", r"^##\s+§5\b")
    if "[0数据]" in page_text:
        if not sec44:
            errs.append("页面有 [0数据] 但没有 §4-4 降级方案小节")
        else:
            bad_rows = [l for l in sec44.split("\n")
                        if "[0数据]" in l and "降级" not in l]
            if bad_rows:
                errs.append("§4-4 有 %d 行写了 [0数据] 但同一行没有降级方案" % len(bad_rows))
    if errs:
        return False, "; ".join(errs[:8])
    return True, "证据等级五级白名单 + 零挂起措辞 + [0数据] 处都有降级方案"


def w7_zero_write(root, contract):
    errs = []
    fp = board_fingerprint(root)
    bl = contract.get("baseline") or {}
    for key, live in (("board_md5", fp["board_md5"]),
                      ("board_size", str(fp["board_size"]))):
        want = bl.get(key)
        if want is None:
            errs.append("机器块 baseline 缺 %s" % key)
            continue
        if str(want) != str(live):
            errs.append("板指纹 %s: 基线 %r vs 实测 %r" % (key, want, live))
    # mtime 精确到纳秒 (9 位), 与基线常量逐字比
    import time as _time
    ns = fp["board_mtime_ns"]
    mtime = _time.strftime("%Y-%m-%d %H:%M:%S", _time.localtime(ns // 10 ** 9)) \
        + "." + ("%09d" % (ns % 10 ** 9))
    if str(bl.get("board_mtime")) != mtime:
        errs.append("板 mtime: 基线 %r vs 实测 %r" % (bl.get("board_mtime"), mtime))
    for rel, key in (("netlist", "netlist_md5"), ("pins", "pins_md5"), ("bom", "bom_md5")):
        live = md5(os.path.join(root, RELS[rel]))
        want = bl.get(key)
        if want != live:
            errs.append("%s: 基线 %r vs 实测 %r" % (key, want, live))
    if errs:
        return False, "; ".join(errs[:8])
    return True, "板 md5/mtime/size 三项 + 网表/脚表/BOM 三件 md5 全部与基线一致"


def w8_zero_hook(root):
    p = os.path.join(root, RELS["gate_check"])
    if not os.path.isfile(p):
        return False, "找不到 state/gate_check.py"
    txt = read_text(p)
    n = txt.count("check_debug_header_fw_impact")
    if n != 0:
        return False, "state/gate_check.py 里出现了 %d 处 check_debug_header_fw_impact ⇒ 新闸被挂链了" % n
    return True, "state/gate_check.py 里 check_debug_header_fw_impact 命中 0 ⇒ 零挂链"


# ---------------------------------------------------------------- 总跑
def run_all(root=PROJ, page_path=None):
    page_path = page_path or os.path.join(root, RELS["page"])
    page_text = read_text(page_path)
    contract = parse_contract(page_text)
    netlist = load_netlist(root)
    pins = load_pins(root)
    res = {}
    res["W0"] = w0_table_matches_reality(root, page_text, contract, netlist, pins)
    res["W1"] = w1_nature_present(page_text, contract)
    res["W2"] = w2_code_change_locations(root, page_text, contract)
    res["W3"] = w3_rescue_chains(page_text, contract)
    res["W4"] = w4_three_routes(page_text, contract)
    res["W5"] = w5_jtag_facts_measured(root, page_text, contract)
    res["W6"] = w6_evidence_hygiene(page_text)
    res["W7"] = w7_zero_write(root, contract)
    res["W8"] = w8_zero_hook(root)
    return res


# ---------------------------------------------------------------- 反向用例
SBX = os.path.join(PROJ, "tmp", "iss378_sbx", "selftest")

SHARED_FILES = ("board", "netlist", "pins", "bom", "som_pin_table",
                "soc_pins_csv", "soc_datasheet_txt", "gate_check")
# ★**「需改代码」列指向的那个被签收闸也要进沙盒 (★W2 要核实它存在★)** ★
EXTRA_FILES = (os.path.join("SW", "tools", "check_debug_pin_order_contract.py"),)


def build_sandbox():
    """建一个沙盒根: 共享副本 (只读) + 每案目录。"""
    if os.path.isdir(SBX):
        shutil.rmtree(SBX)
    shared = os.path.join(SBX, "shared")
    os.makedirs(shared)
    for key in SHARED_FILES:
        src = os.path.join(PROJ, RELS[key])
        dst = os.path.join(shared, key)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    for rel in EXTRA_FILES:
        dst = os.path.join(shared, "extra__" + rel.replace(os.sep, "__"))
        shutil.copy2(os.path.join(PROJ, rel), dst)
    return shared


def _link(shared, case_dir, key):
    """把共享副本 hardlink 到 case_dir 的同构相对路径上。"""
    src = os.path.join(shared, key)
    dst = os.path.join(case_dir, RELS[key])
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        os.remove(dst)
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)
    return dst


def make_case(shared, name, mutate_page=None, mutate_block=None,
              mutate_netlist=None, mutate_gate=None, post=None):
    d = os.path.join(SBX, name)
    os.makedirs(d, exist_ok=True)
    for key in SHARED_FILES:
        _link(shared, d, key)
    for rel in EXTRA_FILES:
        src = os.path.join(shared, "extra__" + rel.replace(os.sep, "__"))
        dst = os.path.join(d, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst):
            os.remove(dst)
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)
    # 网表
    if mutate_netlist is not None:
        p = os.path.join(d, RELS["netlist"])
        txt = mutate_netlist(read_text(p))
        os.remove(p)
        with open(p, "w", encoding="utf-8") as f:
            f.write(txt)
    # gate_check
    if mutate_gate is not None:
        p = os.path.join(d, RELS["gate_check"])
        txt = mutate_gate(read_text(p))
        os.remove(p)
        with open(p, "w", encoding="utf-8") as f:
            f.write(txt)
    # 页
    page = read_text(os.path.join(PROJ, RELS["page"]))
    if mutate_block is not None:
        blk = parse_contract(page)
        mutate_block(blk)
        page = replace_block(page, blk)
    if mutate_page is not None:
        page = mutate_page(page)
    if post is not None:
        page = post(d, page)
    page_path = os.path.join(d, "page.md")
    with open(page_path, "w", encoding="utf-8") as f:
        f.write(page)
    return d, page_path


def drop_row(page, net):
    """从逐网表里删掉一行 (页面表 + 机器块同时删)."""
    out = []
    for line in page.split("\n"):
        if line.strip().startswith("| `%s`" % net):
            continue
        out.append(line)
    page = "\n".join(out)
    blk = parse_contract(page)
    blk["net_rows"] = [x for x in blk.get("net_rows", []) if x.get("net") != net]
    return replace_block(page, blk)


def rename_net(page, old, new):
    out = []
    for line in page.split("\n"):
        if line.strip().startswith("| `%s`" % old):
            line = line.replace("`%s`" % old, "`%s`" % new, 1)
        out.append(line)
    page = "\n".join(out)
    blk = parse_contract(page)
    for x in blk.get("net_rows", []):
        if x.get("net") == old:
            x["net"] = new
    return replace_block(page, blk)


def blank_nature(page, net):
    out = []
    for line in page.split("\n"):
        if line.strip().startswith("| `%s`" % net):
            cells = line.split("|")
            # 列序: 0='' 1=网名 2=两端 3=pad 4=固件 5=变化 6=性质 7=若需改 8=证据 9=来源
            cells[6] = "  "
            line = "|".join(cells)
        out.append(line)
    page = "\n".join(out)
    blk = parse_contract(page)
    for x in blk.get("net_rows", []):
        if x.get("net") == net:
            x["nature"] = ""
    return replace_block(page, blk)


def bad_change_file(page, net, bad_file):
    out = []
    for line in page.split("\n"):
        if line.strip().startswith("| `%s`" % net):
            line = line.replace("SW/tools/check_debug_pin_order_contract.py", bad_file)
        out.append(line)
    page = "\n".join(out)
    blk = parse_contract(page)
    for x in blk.get("net_rows", []):
        if x.get("net") == net:
            x["change_file"] = bad_file
    return replace_block(page, blk)


def flip_som_conclusion(page):
    """★把 §3 里的 SoM 侧结论从「无 JTAG 引出」改成「有 JTAG 引出」. ★"""
    m = re.search(r"^##\s+§3\b", page, re.M)
    assert m, "找不到 §3"
    head = page[:m.end()]
    rest = page[m.end():]
    old = "SoM 侧无 JTAG 引出"
    assert old in rest, "§3 里找不到原结论句"
    rest = rest.replace(old, "SoM 侧有 JTAG 引出", 1)
    return head + rest


def drop_route_iii(page):
    """★把 §3 的「路线 ③」整节删掉 (证明 W4 真在数三条路). ★"""
    m = re.search(r"^####\s*★?路线\s*③.*$", page, re.M)
    assert m, "找不到 路线 ③ 小节"
    start = m.start()
    nxt = re.search(r"^#{2,4}\s", page[m.end():], re.M)
    end = m.end() + (nxt.start() if nxt else 0)
    return page[:start] + page[end:]


def drop_uart_chain(page):
    sec = re.search(r"^\|\s*★\*\*UART 链\*\*.*$", page, re.M)
    assert sec, "找不到 UART 链 那一行"
    page = page[:sec.start()] + page[sec.end():]
    blk = parse_contract(page)
    blk["rescue_chains"] = ["USB", "JTAG"]
    return replace_block(page, blk)


def drop_worst_case_sentence(page):
    m = re.search(r"^> ★\*\*最坏情况下只剩 USB（S2）这一条链\*\*.*$", page, re.M)
    assert m, "找不到最坏结论句"
    return page[:m.start()] + page[m.end():]


def inject_bad_evidence(page):
    return page + "\n\n★本段注入的白名单外证据等级：" + BAD_EVIDENCE_TAG + "★\n"


def inject_hanging(page):
    return page + "\n\n★本段注入的零挂起措辞：" + FORBIDDEN_HANGING[0] + "★\n"


def fake_board_baseline(blk):
    blk.setdefault("baseline", {})["board_md5"] = "0" * 32


def _post_netlist_faked(case_dir, page):
    """★网表被改后, 把基线 md5 与逐网表那一行同步改掉 ⇒ 只让 W5 独红 (证明 W5 真在读网表)."""
    nl = os.path.join(case_dir, RELS["netlist"])
    blk = parse_contract(page)
    blk.setdefault("baseline", {})["netlist_md5"] = md5(nl)
    page = replace_block(page, blk)
    out = []
    for line in page.split("\n"):
        if line.strip().startswith("| `JTAG_TDI_SOC`"):
            line = line.replace("`SoC_NC`", "`J_SOM_P1 pin99`")
        out.append(line)
    return "\n".join(out)


def hook_gate(txt):
    return txt + "\n# check_debug_header_fw_impact\n"


def break_netlist_soc_endpoint(txt):
    return txt.replace("JTAG_TDI_SOC,SoC_NC", "JTAG_TDI_SOC,J_SOM_P1 pin99")


CASES = [
    # (名字, 目标判据, 构造函数)
    ("REV1_route3_deleted", "W4",
     lambda shared: make_case(shared, "REV1_route3_deleted",
                               mutate_page=drop_route_iii)),
    ("REV2_som_conclusion_flipped", "W5",
     lambda shared: make_case(shared, "REV2_som_conclusion_flipped",
                               mutate_page=flip_som_conclusion)),
    ("REV3_change_file_not_exist", "W2",
     lambda shared: make_case(shared, "REV3_change_file_not_exist",
                               mutate_page=lambda p: bad_change_file(
                                   p, "JTAG_TDI", "SW/tools/NO_SUCH_FILE_ISS378.py"))),
    ("REV4_net_row_deleted", "W0",
     lambda shared: make_case(shared, "REV4_net_row_deleted",
                               mutate_page=lambda p: drop_row(p, "KEY_CAM"))),
    ("REV5_nature_blank", "W1",
     lambda shared: make_case(shared, "REV5_nature_blank",
                               mutate_page=lambda p: blank_nature(p, "JTAG_TMS"))),
    ("REV6_uart_chain_dropped", "W3",
     lambda shared: make_case(shared, "REV6_uart_chain_dropped",
                               mutate_page=drop_uart_chain)),
    ("REV7_worst_case_sentence_dropped", "W3",
     lambda shared: make_case(shared, "REV7_worst_case_sentence_dropped",
                               mutate_page=drop_worst_case_sentence)),
    ("REV8_bad_evidence_tag", "W6",
     lambda shared: make_case(shared, "REV8_bad_evidence_tag",
                               mutate_page=inject_bad_evidence)),
    ("REV9_hanging_wording", "W6",
     lambda shared: make_case(shared, "REV9_hanging_wording",
                               mutate_page=inject_hanging)),
    ("REV10_board_baseline_faked", "W7",
     lambda shared: make_case(shared, "REV10_board_baseline_faked",
                               mutate_block=fake_board_baseline)),
    ("REV11_gate_hooked", "W8",
     lambda shared: make_case(shared, "REV11_gate_hooked",
                               mutate_gate=hook_gate)),
    ("REV12_netlist_soc_endpoint_broken", "W5",
     lambda shared: make_case(shared, "REV12_netlist_soc_endpoint_broken",
                               mutate_netlist=break_netlist_soc_endpoint,
                               post=_post_netlist_faked)),
    ("REV13_net_name_not_in_netlist", "W0",
     lambda shared: make_case(shared, "REV13_net_name_not_in_netlist",
                               mutate_page=lambda p: rename_net(p, "KEY_CAM", "KEY_NOT_EXIST"))),
]


def run_selftest():
    shared = build_sandbox()
    ok = 0
    fail = []
    print("=== ISS-378 · check_debug_header_fw_impact --selftest ===")
    for name, target, builder in CASES:
        d, page_path = builder(shared)
        try:
            res = run_all(root=d, page_path=page_path)
        except Exception as e:  # fail-closed: 异常 = 全红
            res = {k: (False, "exception: %s" % e) for k in
                   ("W0", "W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8")}
        reds = sorted([k for k, v in res.items() if not v[0]])
        if reds == [target]:
            ok += 1
            print("  ✔ %-38s 目标判据 %s 独红 · 其余全绿" % (name, target))
        else:
            fail.append((name, target, reds))
            print("  ✘ %-38s 期望独红 %s · 实际红 %s" % (name, target, reds or "无"))
    # 正向: 不动的沙盒必须全绿
    d, page_path = make_case(shared, "REV0_control")
    res = run_all(root=d, page_path=page_path)
    ctrl_red = sorted([k for k, v in res.items() if not v[0]])
    if ctrl_red:
        fail.append(("REV0_control", "无红", ctrl_red))
        print("  ✘ %-38s 期望全绿 · 实际红 %s" % ("REV0_control", ctrl_red))
    else:
        ok += 1
        print("  ✔ %-38s 对照组全绿 (证明不是把灯调没了)" % "REV0_control")
    total = len(CASES) + 1
    print("SELFTEST %d/%d" % (ok, total))
    if ok != total:
        print("❌ 反向用例有 %d 条不一致" % (total - ok))
        return 1
    print("ALL TESTS PASS")
    return 0


# ---------------------------------------------------------------- main
def fmt(res):
    lines = []
    for k in sorted(res):
        ok, msg = res[k]
        lines.append("  %s %s : %s" % ("✔" if ok else "✘", k, msg))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", default=PROJ)
    args = ap.parse_args()
    if args.selftest:
        return run_selftest()
    try:
        res = run_all(root=args.root)
    except Exception as e:
        print("❌ 判据运行异常 (fail-closed): %s" % e)
        return 1
    nred = sum(1 for v in res.values() if not v[0])
    if args.json:
        print(json.dumps({k: {"ok": v[0], "msg": v[1]} for k, v in res.items()},
                         ensure_ascii=False, indent=2))
    else:
        print("=== ISS-378 · check_debug_header_fw_impact ===")
        print(fmt(res))
        print("--- %d/%d 绿 ---" % (len(res) - nred, len(res)))
    return 1 if nred else 0


if __name__ == "__main__":
    sys.exit(main())
