#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-369 · hw-lead · 「板那一趟」板面 186 封装库封装名写盘 机器门禁 (L0~L8 + 板面模式 B0~B5)
作者: hw-lead · 2026-11-23 · 交卷给 main / 项目总工

用法:
    python3 HW/check_fp_libid_truth.py                    # 正常跑 (计划模式) ⇒ rc=0 = 全过
    python3 HW/check_fp_libid_truth.py --selftest         # 反向用例自证 ⇒ rc=0 (末行 ALL TESTS PASS)
    python3 HW/check_fp_libid_truth.py --json              # 机器可读输出
    python3 HW/check_fp_libid_truth.py --root DIR          # 指定项目根 (默认自动定位)
    python3 HW/check_fp_libid_truth.py --libroot DIR       # 指定 KiCad 官方库根
    python3 HW/check_fp_libid_truth.py --mode board --board <板文件>
                                                         # ★板面模式: 对【已换 land + 已写库名】的板逐封装判定★

★ 本闸判据 (内容级, **不挂 md5** —— 沿用本项目既有闸的做法: 文档改一个字就重判):
    L0 基准块存在且是合法 JSON (页内 "BEGIN/END ISS369 库封装名写盘基准块")
    L1 ★**件数由脚本自己算出来**★:
       读 HW/PCB/demo_mainboard.kicad_pcb (纯文本) + HW/BOM_v1.csv (ISS-356 靶子口径)
       + HW/netlist_v1.csv (C4 占位脚号口径)
       ⇒ 算出「板面 186 · C4 158 · 靶内 77 + 缺口 13 = 90 · 186 − 90 = 96」
       ⇒ 与基准块 counts、与 §3.1 (90 行) / §3.2 (96 行) 两张表逐项/逐件相等
    L2 §3.1 表 90 件 + §3.2 表 96 件 逐件齐全 —— 漏一件即红 + 多一件也红
    L3 每件字段非空 (★目标 lib:name / .kicad_mod 路径 + md5 / 目标几何 / 几何 Δ /
       pad↔net / 具名脚清单 / 降级方案 / 理由 / 证据等级 一项不许空★)
    L4 ★**每个要写库名的 lib:name, 逐个 `test -f` 验【封装文件】在盘 + md5 对得上**★
       (★查的是 .kicad_mod 文件, 不是只查库目录★)
    L5 ★**几何一致性 + 容差**★:
       ① 90 件 + 4 件的「目标焊盘数 / fab 外框 / 中心距」== 脚本从 .kicad_mod 实测出来的值
       ② 「Δ焊盘数 / Δ中心距」== 脚本实算
       ③ 4 件「只写库名、零几何改动」的件: 板面逐焊盘几何 vs 官方件几何 在容差内
          (★容差写死在脚本里, 且沿用本项目既有口径, 不拍脑袋★)
    L6 证据等级五级白名单 ([官网]/[实测]/[媒体]/[推算]/[0数据]) ⇒ 写 [官方] = 红
    L7 正文无「等原厂回信 / 待供应商确认 / 待外部回复 / 等回复 / 等确认」这类挂起措辞
    L8 ★**「写库名对 C1/C2/C3/C4 的贡献 = 0」这条机制在本单里被机器钉住**★:
       读留证 logs/iss369/10_sandbox_readings.json (五轮 C1~C4) + 12_sandbox_bytediff.json
       + 页内 §4.1 表 ⇒ 五轮 C4 全 = 158 且 S0/S1/S2/S3/S4 的 C1/C2/C3 读数成对相同
       ⇒ ⇒ ★**写库名这一腿对 C4 的贡献 = 0** ★
    ── 板面模式 (--mode board) ──
    B1 板面每个【要写库名的】封装 lib_id 非空 (94 件)
    B2 每个非空 lib_id 指向的 .kicad_mod 在盘 + md5 对得上
    B3 该 .kicad_mod 的焊盘数 == 板上该封装的焊盘数
    B4 几何 Δ 在容差内 (焊盘级位置/尺寸/中心距 + fab 外框)
    B5 ★**不该写库名的 92 件, lib_id 仍为空**★ (防误写)

★ 本门禁【零 pcbnew 依赖】: 纯 python 文本解析 ⇒ ★裸 `python3` 就能跑★

--selftest 反向用例 (每条都自证「真的改到了目标」+「红的是目标那一条, 其余仍绿」):
    M1 删掉 §3.1 表里某一行 (R_PU_BOOT_N)         → 期望 L2 红, 其余仍绿
    M2 把某行 .kicad_mod md5 改错                   → 期望 L4 红, 其余仍绿
    M3 把某行目标焊盘数改成错的                     → 期望 L5 红, 其余仍绿
    M4 清空某行降级方案                             → 期望 L3 红, 其余仍绿
    M5 把某行证据等级写成 [官方]                     → 期望 L6 红, 其余仍绿
    M6 正文塞一句「等原厂回信」                      → 期望 L7 红, 其余仍绿
    M7 篡改基准块 counts.target_total (90→89)       → 期望 L1 红, 其余仍绿
    M8 把页内 §4.1 表的 C4 数字改成 68              → 期望 L8 红, 其余仍绿
    M9 把 §3.2 表里某一件的「不写」改成「写」        → 期望 L2 红, 其余仍绿
    B1 板面模式: 把沙盒板副本里某件的 lib_id 清空    → 期望 B1 红, 其余仍绿
    B2 板面模式: 把沙盒板副本里某件的 lib_id 改成
       一个本机不存在的库                            → 期望 B2 红, 其余仍绿

★ 反向用例的「真的改到了目标」自证 = 三件事同时成立:
    ① 变异确实落到盘上副本里 (变异串在副本里 count>=1, 变异前原串消失)
    ② 期望变红的那一条 check 真的红了
    ③ 其余 check 仍然绿 (证明红的是目标那一条, 不是随便塌一条)
★ 沙盒: 副本落**项目盘 tmp/iss369/selftest/** (不落 /tmp, ★2026-11-23 04:4x 实测系统 /tmp 配额已满★
  ⇒ 写 /tmp 会让闸拿到假读数★)
"""

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sys

DOC_REL = os.path.join("HW", "PCB", "FP_LIBID_TRUTH_WORKPACKET.md")
BLOCK_BEGIN = "<!-- BEGIN ISS369 库封装名写盘基准块 -->"
BLOCK_END = "<!-- END ISS369 库封装名写盘基准块 -->"
SANDBOX_READINGS = os.path.join("logs", "iss369", "10_sandbox_readings.json")
SANDBOX_BYTEDIFF = os.path.join("logs", "iss369", "12_sandbox_bytediff.json")
SANDBOX_DIR = os.path.join("tmp", "iss369", "sbx")
BOARD_REL = os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb")
BOARD_MD5_BASELINE = "611b869e13518c3c023fb178f91a0075"

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

# ★几何容差 (★写在脚本里·不许拍脑袋★)★
#   PAD_POS_TOL / PAD_SIZE_TOL / CEN_TOL: ★沿用本项目既有口径★
#     (tmp/iss369/tools/padeq_rot.py 与 tmp/iss369/tools/padeq_rot_np.py 的同一组值,
#      ISS-364 的换封装作业包也用同一组) ⇒ 不另立标准
#   FAB_TOL: F.Fab 是画图层 (不参与电气), 只用来抓量级错误
#     ⇒ 取本单 4 件「只写库名、零几何改动」的实测最大 fab Δ (0.32 mm) + 0.03 mm 余量
PAD_POS_TOL = 0.05
PAD_SIZE_TOL = 0.05
CEN_TOL = 0.10
FAB_TOL = 0.35

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
    if not tail:
        return False
    if re.fullmatch(r"pin\d+(\+pin\d+)*", tail):
        return True
    if USBIF_RE.match(tail):
        return True
    toks = [t.strip() for t in tail.split("+") if t.strip()]
    return len(toks) >= 2 and all(USBIF_RE.match(t) for t in toks)


def netlist_placeholder(path):
    """★C4 占位脚号口径 (与 state/check_pcb_nets.py 同口径, 独立实现)★ ⇒ placeholder {ref: 焊盘数}"""
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    rows = [r for r in rows if (r.get("board") or BOARD_FILTER).strip() == BOARD_FILTER]
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
        if any(k[0] == "P" for k, v in d.items()):
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


def fp_blocks(text):
    """★板面 186 个封装块 (纯文本·括号配平)★"""
    out = []
    for m in re.finditer(r"^\t\(footprint ", text, re.M):
        s = m.start()
        cands = [text.find("\n\t(footprint ", s + 1), text.find("\n\t(net ", s + 1)]
        cands = [c for c in cands if c != -1]
        e = min(cands) if cands else len(text)
        blk = text[s:e]
        rm = re.search(r'\(property "Reference" "([^"]*)"', blk)
        if not rm:
            continue
        head = re.search(r'^\t\(footprint "([^"]*)"', blk, re.M)
        out.append({"ref": rm.group(1),
                    "lib_id": head.group(1) if head else "",
                    "block": blk})
    return out


def pad_geom(pb):
    at = re.search(r"\(at ([^)]*)\)", pb)
    a = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", at.group(1))] if at else [0.0, 0.0]
    sm = re.search(r"\(size ([-\d\.]+) ([-\d\.]+)\)", pb)
    w = float(sm.group(1)) if sm else 0.0
    h = float(sm.group(2)) if sm else 0.0
    nm = re.search(r'\(pad\s+"([^"]*)"', pb)
    nt = re.search(r'\(net\s+"([^"]*)"', pb)
    return {"num": nm.group(1) if nm else "", "net": nt.group(1) if nt else "",
            "x": a[0], "y": a[1], "w": w, "h": h}


def board_geom(path):
    """★板面每个封装的 (lib_id / 焊盘 / fab 外框 / 中心距) 纯文本实测★"""
    return board_geom_from_text(open(path, encoding="utf-8").read())


def board_geom_from_text(text):
    """★板面每个封装的 (lib_id / 焊盘 / fab 外框 / 中心距) 纯文本实测 (从文本直接算)★"""
    out = {}
    for f in fp_blocks(text):
        blk = f["block"]
        pads = [pad_geom(pb) for pb in _blocks(blk, "pad")]
        xs, ys = [], []
        for tag in ("fp_line", "fp_rect"):
            for b in _blocks(blk, tag):
                lm = re.search(r'\(layer "([^"]*)"\)', b)
                if not lm or lm.group(1) != "F.Fab":
                    continue
                for grp in ("start", "end"):
                    m = re.search(r"\(%s ([-\d\.]+) ([-\d\.]+)\)" % grp, b)
                    if m:
                        xs.append(float(m.group(1)))
                        ys.append(float(m.group(2)))
        fab = (round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3)) if xs else (0.0, 0.0)
        d = 0.0
        for i in range(len(pads)):
            for j in range(i + 1, len(pads)):
                d = max(d, ((pads[i]["x"] - pads[j]["x"]) ** 2
                            + (pads[i]["y"] - pads[j]["y"]) ** 2) ** 0.5)
        out[f["ref"]] = {"lib_id": f["lib_id"], "pads": pads,
                         "pads_n": len(pads), "fab_w": fab[0], "fab_h": fab[1],
                         "center": round(d, 3)}
    return out


def mod_geom(libroot, libname):
    """★从 .kicad_mod 实测: 焊盘 / fab 外框 / 中心距 / md5 / 路径★ ⇒ None 或 dict"""
    if ":" not in libname:
        return None
    lib, nm = libname.split(":", 1)
    rel = "%s.pretty/%s.kicad_mod" % (lib, nm)
    p = os.path.join(libroot, rel)
    if not os.path.isfile(p):
        return None
    text = open(p, encoding="utf-8").read()
    pads = [pad_geom(pb) for pb in _blocks(text, "pad")]
    xs, ys = [], []
    for tag in ("fp_line", "fp_rect"):
        for b in _blocks(text, tag):
            lm = re.search(r'\(layer "([^"]*)"\)', b)
            if not lm or lm.group(1) != "F.Fab":
                continue
            for grp in ("start", "end"):
                m = re.search(r"\(%s ([-\d\.]+) ([-\d\.]+)\)" % grp, b)
                if m:
                    xs.append(float(m.group(1)))
                    ys.append(float(m.group(2)))
    fab = (round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3)) if xs else (0.0, 0.0)
    d = 0.0
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            d = max(d, ((pads[i]["x"] - pads[j]["x"]) ** 2
                        + (pads[i]["y"] - pads[j]["y"]) ** 2) ** 0.5)
    return {"pads_n": len(pads), "pads": pads,
            "fab_w": fab[0], "fab_h": fab[1], "center": round(d, 3),
            "md5": hashlib.md5(open(p, "rb").read()).hexdigest(),
            "path": rel, "ab": p}


def pad_equiv(board_pads, mod_pads):
    """★逐焊盘几何等价 (允许旋转 0/90/180/270) ⇒ (是否等价, 旋转角, 最大位置Δ, 最大尺寸Δ, 中心距Δ)★"""
    if len(board_pads) != len(mod_pads):
        return (False, None, None, None, None)

    def rot(p, deg):
        x, y = p["x"], p["y"]
        if deg == 0:
            return x, y, p["w"], p["h"]
        if deg == 90:
            return -y, x, p["h"], p["w"]
        if deg == 180:
            return -x, -y, p["w"], p["h"]
        return y, -x, p["h"], p["w"]

    def key(p):
        d = "".join(ch for ch in p["num"] if ch.isdigit())
        return (0, int(d), p["num"]) if d else (1, 0, p["num"])

    def maxdist(ps):
        d = 0.0
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                d = max(d, ((ps[i][0] - ps[j][0]) ** 2 + (ps[i][1] - ps[j][1]) ** 2) ** 0.5)
        return d

    bp = sorted(board_pads, key=key)
    for deg in (0, 90, 180, 270):
        mp = sorted([{"num": p["num"], "x": rot(p, deg)[0], "y": rot(p, deg)[1],
                      "w": rot(p, deg)[2], "h": rot(p, deg)[3]} for p in mod_pads], key=key)
        dpos = dsize = 0.0
        ok = True
        for a, b in zip(bp, mp):
            dpos = max(dpos, abs(a["x"] - b["x"]), abs(a["y"] - b["y"]))
            dsize = max(dsize, abs(a["w"] - b["w"]), abs(a["h"] - b["h"]))
        if dpos > PAD_POS_TOL or dsize > PAD_SIZE_TOL:
            continue
        dc = abs(maxdist([(p["x"], p["y"]) for p in bp]) - maxdist([(p["x"], p["y"]) for p in mp]))
        if dc > CEN_TOL:
            continue
        return (True, deg, round(dpos, 4), round(dsize, 4), round(dc, 4))
    return (False, None, None, None, None)


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
    """★按表头内容定位一张表 ⇒ (head, rows, 首行号, 末行号, 行号表)★"""
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s.startswith("|"):
            continue
        if not all(m in s for m in must_have):
            continue
        head = [c.strip() for c in s.strip("|").split("|")]
        rows, idxs = [], []
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


def unq(s):
    return (s or "").strip().strip("`").strip()


def parse_libname(s):
    s = unq(s)
    if ":" not in s:
        return None, None
    lib, nm = s.split(":", 1)
    return lib, nm


def parse_md5(s):
    m = re.search(r"md5\s+`?([0-9a-f]{32})`?", s or "")
    return m.group(1) if m else ""


def parse_path(s):
    m = re.search(r"([A-Za-z0-9_]+\.pretty/[A-Za-z0-9_.+-]+\.kicad_mod)", s or "")
    return m.group(1) if m else ""


# ---------------------------------------------------------------- 主检查 (计划模式)

def check(doc_text, root, libroot=LIBROOT_DEFAULT):
    results = {}
    facts = {}

    board_path = os.path.join(root, BOARD_REL)
    bg = board_geom(board_path)
    bom_rows = load_bom(os.path.join(root, "HW", "BOM_v1.csv"))
    main_t, chg_t, total_t = iss356_targets(bom_rows)
    ph = netlist_placeholder(os.path.join(root, "HW", "netlist_v1.csv"))
    c4 = set(ph)
    iss = set(total_t)
    inter = c4 & iss
    gap = set(coverage_gap(bom_rows, c4))
    target90 = sorted(inter) + sorted(gap)
    rest96 = sorted(set(bg) - set(target90))

    facts["board_footprints"] = len(bg)
    facts["c4_total"] = len(c4)
    facts["iss356_total"] = len(iss)
    facts["iss356_main"] = len(main_t)
    facts["iss356_chg"] = len(chg_t)
    facts["inter_total"] = len(inter)
    facts["gap_total"] = len(gap)
    facts["target_total"] = len(target90)
    facts["rest_total"] = len(rest96)
    facts["board_md5"] = hashlib.md5(open(board_path, "rb").read()).hexdigest()

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
    counts = block.get("counts", {})

    # ---- L1 件数由脚本自己算出来
    l1_bad = []
    want = {"board_footprints": len(bg), "c4_total": len(c4),
            "inter_total": len(inter), "gap_total": len(gap),
            "target_total": len(target90), "rest_total": len(rest96),
            "libid_named": 0, "libid_empty": len(bg)}
    for k, v in want.items():
        if counts.get(k) != v:
            l1_bad.append("基准块 counts.%s: 基准块 %s vs 脚本实算 %s" % (k, counts.get(k), v))
    if len(inter) + len(gap) != len(target90):
        l1_bad.append("脚本自算不自洽: 靶内 %d + 缺口 %d != %d"
                      % (len(inter), len(gap), len(target90)))
    if len(bg) - len(target90) != len(rest96):
        l1_bad.append("脚本自算不自洽: 板面 %d − 90 != %d" % (len(bg), len(rest96)))
    if set(rest96) & set(target90):
        l1_bad.append("90 与 96 有交集: %s" % sorted(set(rest96) & set(target90))[:5])
    if len(target90) + len(rest96) != len(bg):
        l1_bad.append("90 + 96 != 板面封装数 (%d + %d != %d)"
                      % (len(target90), len(rest96), len(bg)))
    fb = counts.get("four_buckets")
    if fb is not None:
        for k, v in (("TP", 42), ("DNP", 26), ("靶内", len(inter)), ("缺口", len(gap))):
            if fb.get(k) != v:
                l1_bad.append("基准块 four_buckets.%s: %s vs 实算 %s" % (k, fb.get(k), v))
    results["L1"] = {"ok": not l1_bad,
                     "detail": "板面 %d · C4 %d · 靶内 %d + 缺口 %d = %d · 其余 %d (★脚本实算·页里写的与实算一致★)"
                     % (len(bg), len(c4), len(inter), len(gap), len(target90), len(rest96))
                     if not l1_bad else "; ".join(l1_bad[:8])}

    # ---- L2 / L3 / L4 / L5 / L6: 两张表
    l2_bad, l3_bad, l4_bad, l5_bad, l6_bad = [], [], [], [], []
    head1, rows1 = find_table(lines, ["现占位几何", "目标几何", "降级方案"])
    head2, rows2 = find_table(lines, ["动作", "理由", "证据等级", "不需要写"])
    head4, rows4 = find_table(lines, ["轮次", "库名非空"])
    head3, rows3 = find_table(lines, ["库封装名", "焊盘数", "形态"])

    if head1 is None or head2 is None:
        results["L2"] = {"ok": False, "detail": "页内找不到 §3.1 / §3.2 两张表"}
        for c in ("L3", "L4", "L5", "L6"):
            results[c] = {"ok": False, "detail": "表不可用 ⇒ 连带判红"}
    else:
        refs1 = [unq(r[0]) for r in rows1]
        refs2 = [unq(r[0]) for r in rows2]
        if len(rows1) != len(target90) or set(refs1) != set(target90):
            l2_bad.append("§3.1 表: %d 行 vs 脚本实算 %d 件; 差 %s / %s"
                          % (len(rows1), len(target90),
                             sorted(set(refs1) - set(target90))[:5],
                             sorted(set(target90) - set(refs1))[:5]))
        if len(rows2) != len(rest96) or set(refs2) != set(rest96):
            l2_bad.append("§3.2 表: %d 行 vs 脚本实算 %d 件; 差 %s / %s"
                          % (len(rows2), len(rest96),
                             sorted(set(refs2) - set(rest96))[:5],
                             sorted(set(rest96) - set(refs2))[:5]))
        if set(refs1) & set(refs2):
            l2_bad.append("§3.1 与 §3.2 有重复 ref: %s" % sorted(set(refs1) & set(refs2))[:5])
        # §1.3 逐个实测表: 186 行, ref 集合 == 板面, 库封装名全空
        if head3 is None:
            l2_bad.append("页内找不到 §1.3 逐个实测表")
        else:
            refs3 = [unq(r[0]) for r in rows3]
            if len(rows3) != len(bg) or set(refs3) != set(bg):
                l2_bad.append("§1.3 表: %d 行 vs 板面 %d 件; 差 %s / %s"
                              % (len(rows3), len(bg),
                                 sorted(set(refs3) - set(bg))[:5],
                                 sorted(set(bg) - set(refs3))[:5]))
            for r in rows3:
                if not (cell(r, head3, "库封装名") or "").strip():
                    l2_bad.append("%s: §1.3 表的库封装名栏空" % unq(r[0]))
                pn = cell(r, head3, "焊盘数")
                ref = unq(r[0])
                if pn.strip().isdigit() and ref in bg and int(pn) != bg[ref]["pads_n"]:
                    l2_bad.append("%s: §1.3 表焊盘数 %s vs 脚本实算 %d"
                                  % (ref, pn, bg[ref]["pads_n"]))

        wt = block.get("write_targets", {}) or {}
        nw = block.get("nowrite_refs", {}) or {}
        n_lib = 0
        for r in rows1:
            ref = unq(r[0])
            libname = unq(cell(r, head1, "目标 `lib:name`") or cell(r, head1, "lib:name"))
            pathcell = cell(r, head1, ".kicad_mod") or ""
            md5cell = parse_md5(pathcell)
            rel = parse_path(pathcell)
            geom = cell(r, head1, "目标几何")
            delta = cell(r, head1, "几何 Δ")
            padnet = cell(r, head1, "pad↔net")
            nets = cell(r, head1, "要重接的 net")
            legb = cell(r, head1, "腿 B 具名脚")
            down = cell(r, head1, "降级方案")
            ev = cell(r, head1, "证据等级")
            # L3 字段非空
            for nm, v in (("目标 lib:name", libname), ("目标几何", geom), ("几何 Δ", delta),
                          ("pad↔net 序", padnet), ("要重接的 net 名单", nets),
                          ("腿 B 具名脚清单", legb), ("降级方案", down), ("证据等级", ev)):
                if not v.strip():
                    l3_bad.append("%s: %s 空" % (ref, nm))
            if not md5cell:
                l3_bad.append("%s: .kicad_mod md5 空" % ref)
            if not rel:
                l3_bad.append("%s: .kicad_mod 路径空" % ref)
            # L6 证据等级
            tags = set(re.findall(r"\[[^\[\]]+\]", ev))
            if not tags:
                l6_bad.append("%s: 证据等级无标签" % ref)
            else:
                bad = tags - ALLOWED_EVIDENCE
                if bad:
                    l6_bad.append("%s: 证据等级非法 %s" % (ref, sorted(bad)))
            # L4 逐个 test -f + md5
            g = mod_geom(libroot, libname)
            if g is None:
                l4_bad.append("%s: %s 的 .kicad_mod 不在盘 (%s)" % (ref, libname, rel))
            else:
                n_lib += 1
                if g["md5"] != md5cell:
                    l4_bad.append("%s: md5 页写 %s vs 盘上实测 %s" % (ref, md5cell, g["md5"]))
                if rel and g["path"] != rel:
                    l4_bad.append("%s: 路径 页写 %s vs 盘上实测 %s" % (ref, rel, g["path"]))
            # L5 几何
            mg = re.search(r"焊盘数\s*(\d+)\s*·\s*fab 外框\s*([-\d\.]+)×([-\d\.]+)\s*mm\s*·\s*中心距\s*([-\d\.]+)\s*mm", geom)
            if not mg:
                l5_bad.append("%s: 目标几何栏解析不出来: %r" % (ref, geom[:60]))
            elif g is not None:
                if int(mg.group(1)) != g["pads_n"]:
                    l5_bad.append("%s: 目标焊盘数 页写 %s vs 实测 %d"
                                  % (ref, mg.group(1), g["pads_n"]))
                if (abs(float(mg.group(2)) - g["fab_w"]) > 0.005
                        or abs(float(mg.group(3)) - g["fab_h"]) > 0.005):
                    l5_bad.append("%s: 目标 fab 外框 页写 %s×%s vs 实测 %.3f×%.3f"
                                  % (ref, mg.group(2), mg.group(3), g["fab_w"], g["fab_h"]))
                if abs(float(mg.group(4)) - g["center"]) > 1e-6:
                    l5_bad.append("%s: 目标中心距 页写 %s vs 实测 %.3f"
                                  % (ref, mg.group(4), g["center"]))
            md = re.search(r"Δ焊盘数\s*([+-]?\d+)", delta)
            if md and g is not None:
                bp = bg.get(ref)
                if bp:
                    want_d = g["pads_n"] - bp["pads_n"]
                    if int(md.group(1)) != want_d:
                        l5_bad.append("%s: Δ焊盘数 页写 %s vs 实算 %+d"
                                      % (ref, md.group(1), want_d))
        # §3.2 表: 写 / 不写 + 理由 + 证据 + (写的那几件) 库文件
        for r in rows2:
            ref = unq(r[0])
            act = (cell(r, head2, "动作") or "").strip()
            reason = cell(r, head2, "理由")
            ev = cell(r, head2, "证据等级")
            libname = unq(cell(r, head2, "目标 `lib:name`") or cell(r, head2, "lib:name"))
            if "不需要写" in libname:
                libname = ""
            pathcell = cell(r, head2, ".kicad_mod") or ""
            md5cell = parse_md5(pathcell)
            rel = parse_path(pathcell)
            if act.replace("*", "") == "写":
                if ref not in wt:
                    l2_bad.append("%s: 基准块 write_targets 里没有它" % ref)
                if not libname:
                    l3_bad.append("%s: 目标 lib:name 空" % ref)
                g = mod_geom(libroot, libname)
                if g is None:
                    l4_bad.append("%s: %s 的 .kicad_mod 不在盘 (%s)" % (ref, libname, rel))
                else:
                    n_lib += 1
                    if md5cell and g["md5"] != md5cell:
                        l4_bad.append("%s: md5 页写 %s vs 盘上实测 %s" % (ref, md5cell, g["md5"]))
                    if rel and g["path"] != rel:
                        l4_bad.append("%s: 路径 页写 %s vs 盘上实测 %s" % (ref, rel, g["path"]))
                # ★L5-③ 只写库名、零几何改动的件: 板面逐焊盘几何 vs 官方件 ⇒ 必须在容差内★
                if ref not in target90 and g is not None:
                    bp = bg.get(ref)
                    if bp:
                        eq, deg, dpos, dsize, dc = pad_equiv(bp["pads"], g["pads"])
                        if not eq:
                            l5_bad.append("%s: 只写库名但板面与 %s 逐焊盘几何不等价"
                                          % (ref, libname))
                        dfab = (round(abs(g["fab_w"] - bp["fab_w"]) + abs(g["fab_h"] - bp["fab_h"]), 3))
                        if dfab > FAB_TOL:
                            l5_bad.append("%s: fab 外框 Δ %.3f mm > 容差 %.2f mm"
                                          % (ref, dfab, FAB_TOL))
            elif act.replace("*", "") == "不写":
                if ref not in nw:
                    l2_bad.append("%s: 基准块 nowrite_refs 里没有它" % ref)
                if libname:
                    l3_bad.append("%s: 动作 = 不写 但给了目标 lib:name %r" % (ref, libname))
            else:
                l3_bad.append("%s: 动作栏 = %r (应为 写 / 不写)" % (ref, act))
            if not reason.strip():
                l3_bad.append("%s: 理由空" % ref)
            tags = set(re.findall(r"\[[^\[\]]+\]", ev))
            if not tags:
                l6_bad.append("%s: 证据等级无标签" % ref)
            else:
                bad = tags - ALLOWED_EVIDENCE
                if bad:
                    l6_bad.append("%s: 证据等级非法 %s" % (ref, sorted(bad)))
        # 基准块 write_targets / nowrite_refs 与两张表一致
        if set(wt) != (set(refs1) | {unq(r[0]) for r in rows2
                                      if (cell(r, head2, "动作") or "").strip().replace("*", "") == "写"}):
            l2_bad.append("基准块 write_targets 的件数与两张表的「写」行数不一致")
        if set(nw) != {unq(r[0]) for r in rows2
                        if (cell(r, head2, "动作") or "").strip().replace("*", "") != "写"}:
            l2_bad.append("基准块 nowrite_refs 的件数与两张表的「不写」行数不一致")
        facts["n_lib_checked"] = n_lib
        facts["n_write"] = len(wt)
        facts["n_nowrite"] = len(nw)
        results["L2"] = {"ok": not l2_bad,
                         "detail": "§1.3 逐个实测表 %d 件 + §3.1 表 %d 件 + §3.2 表 %d 件 == 板面 %d 件 (★不多不少·逐件相等★)"
                         % (len(rows3) if head3 else 0, len(rows1), len(rows2), len(bg))
                         if not l2_bad else "; ".join(l2_bad[:8])}
        results["L3"] = {"ok": not l3_bad,
                         "detail": "%d + %d 行字段全非空 (★几何 Δ / 具名脚清单 / 降级方案 / 理由 一项不许空★)"
                         % (len(rows1), len(rows2)) if not l3_bad else "; ".join(l3_bad[:8])}
        results["L4"] = {"ok": not l4_bad,
                         "detail": "%d 处 lib:name 的 .kicad_mod 全部实测在盘 + md5 一致 (★查的是封装文件, 不是只查库目录★)"
                         % n_lib if not l4_bad else "; ".join(l4_bad[:8])}
        results["L5"] = {"ok": not l5_bad,
                         "detail": "%d 件要写库名的件: 目标焊盘数 / fab 外框 / 中心距 == 脚本从 .kicad_mod 实测; 4 件「只写库名·零几何改动」的逐焊盘等价在容差内 (pos≤%.2f size≤%.2f cen≤%.2f fab≤%.2f mm)"
                         % (len(wt), PAD_POS_TOL, PAD_SIZE_TOL, CEN_TOL, FAB_TOL)
                         if not l5_bad else "; ".join(l5_bad[:8])}
        results["L6"] = {"ok": not l6_bad,
                         "detail": "%d + %d 行证据等级全 ∈ 五级白名单 (无 [官方])"
                         % (len(rows1), len(rows2)) if not l6_bad else "; ".join(l6_bad[:8])}

    # ---- L7 挂起措辞
    l7_bad = []
    for ph_ in FORBIDDEN_PHRASES:
        if ph_ in doc_text:
            l7_bad.append("出现挂起措辞: %s (×%d)" % (ph_, doc_text.count(ph_)))
    results["L7"] = {"ok": not l7_bad,
                     "detail": "正文无「等回复/等原厂回信/待供应商确认/待外部回复/等原厂/等确认」类挂起措辞"
                     if not l7_bad else "; ".join(l7_bad)}

    # ---- L8 沙盒可达性证明 (写库名对 C4 贡献 = 0)
    l8_bad = []
    rp = os.path.join(root, SANDBOX_READINGS)
    bp_ = os.path.join(root, SANDBOX_BYTEDIFF)
    if not os.path.isfile(rp):
        l8_bad.append("缺留证 %s" % SANDBOX_READINGS)
    if not os.path.isfile(bp_):
        l8_bad.append("缺留证 %s" % SANDBOX_BYTEDIFF)
    if not l8_bad:
        sb = json.load(open(rp, encoding="utf-8"))
        bd = json.load(open(bp_, encoding="utf-8"))
        meta = sb.get("_meta", {})
        if not meta.get("real_board_untouched"):
            l8_bad.append("沙盒元数据: 真板被改过")
        if meta.get("real_board_md5_pre") != BOARD_MD5_BASELINE or \
                meta.get("real_board_md5_post") != BOARD_MD5_BASELINE:
            l8_bad.append("沙盒元数据: 真板 md5 前 %s / 后 %s != 基线 %s"
                          % (meta.get("real_board_md5_pre"), meta.get("real_board_md5_post"),
                             BOARD_MD5_BASELINE))
        rounds = ["S0_基线_真板真表", "S1_换land不写库名", "S2_换land加写库名",
                  "S3_只写库名零几何改动", "S4_反向对照_90件写库名不换land"]
        for k in rounds:
            if k not in sb:
                l8_bad.append("沙盒读数缺 %s" % k)
                continue
            if sb[k].get("c4") != 158:
                l8_bad.append("%s: C4 = %s (应为 158)" % (k, sb[k].get("c4")))
        pairs = [("S1_换land不写库名", "S2_换land加写库名"),
                 ("S0_基线_真板真表", "S3_只写库名零几何改动"),
                 ("S0_基线_真板真台" if False else "S0_基线_真板真表",
                  "S4_反向对照_90件写库名不换land")]
        for a, b in pairs:
            if a not in sb or b not in sb:
                continue
            for fld in ("c1", "c2", "c3", "c4"):
                if sb[a].get(fld) != sb[b].get(fld):
                    l8_bad.append("%s vs %s 的 %s 读数不同 ⇒ 写库名影响了它" % (a, b, fld))
        for k, v in bd.items():
            if k.startswith("_"):
                continue
            if not v.get("only_footprint_node_lines"):
                l8_bad.append("字节差分 %s: 差分行不只是封装节点名行" % k)
        for f in ("board_legA_only.kicad_pcb", "board_legA_plus_libid.kicad_pcb",
                  "board_libid_only.kicad_pcb", "board_libid_no_landswap.kicad_pcb"):
            if not os.path.isfile(os.path.join(root, SANDBOX_DIR, f)):
                l8_bad.append("沙盒板副本缺 %s" % f)
        # ★页内 §4.1 表的 C4 数字必须也是 158★
        if head4 is not None:
            k4 = None
            for i, c in enumerate(head4):
                if "C4" in c.replace("`", ""):
                    k4 = i
                    break
            if k4 is None:
                l8_bad.append("§4.1 表没有 C4 列")
            else:
                for r in rows4:
                    if "158" not in (r[k4] if k4 < len(r) else ""):
                        l8_bad.append("§4.1 表某行的 C4 不是 158: %s" % (r[k4] if k4 < len(r) else ""))
        else:
            l8_bad.append("页内找不到 §4.1 沙盒五轮表")
        facts["sandbox_c4"] = {k: sb.get(k, {}).get("c4") for k in rounds}
    results["L8"] = {"ok": not l8_bad,
                     "detail": "沙盒五轮 C4 全 = 158 且 S0/S1/S2/S3/S4 的 C1/C2/C3/C4 成对相同 ⇒ ★写库名这一腿对 C4 的贡献 = 0★"
                     if not l8_bad else "; ".join(l8_bad[:8])}

    return results, facts


# ---------------------------------------------------------------- 板面模式

def check_board(board_path, root, libroot=LIBROOT_DEFAULT):
    """★对【已换 land + 已写库名】的板逐封装判定 (B0~B5)★"""
    results = {}
    facts = {}
    bg = board_geom(board_path)
    doc = open(os.path.join(root, DOC_REL), encoding="utf-8").read()
    block = parse_block(doc) or {}
    wt = block.get("write_targets", {}) or {}
    nw = block.get("nowrite_refs", {}) or {}
    facts["board_footprints"] = len(bg)
    facts["write_expected"] = len(wt)
    facts["nowrite_expected"] = len(nw)

    b1, b2, b3, b4, b5 = [], [], [], [], []
    for ref, t in sorted(wt.items()):
        b = bg.get(ref)
        if b is None:
            b1.append("%s: 板面没有这个封装" % ref)
            continue
        if not b["lib_id"]:
            b1.append("%s: lib_id 仍为空" % ref)
            continue
        if b["lib_id"] != t.get("libname"):
            b2.append("%s: lib_id = %s vs 计划 %s" % (ref, b["lib_id"], t.get("libname")))
            continue
        g = mod_geom(libroot, b["lib_id"])
        if g is None:
            b2.append("%s: %s 的 .kicad_mod 不在盘" % (ref, b["lib_id"]))
            continue
        if t.get("md5") and g["md5"] != t["md5"]:
            b2.append("%s: .kicad_mod md5 %s != 计划 %s" % (ref, g["md5"], t["md5"]))
        if g["pads_n"] != b["pads_n"]:
            b3.append("%s: 板上焊盘数 %d != %s 的 %d"
                       % (ref, b["pads_n"], b["lib_id"], g["pads_n"]))
        eq, deg, dpos, dsize, dc = pad_equiv(b["pads"], g["pads"])
        if not eq:
            b4.append("%s: 板面几何与 %s 不等价 (posΔ>%.2f / sizeΔ>%.2f / cenΔ>%.2f)"
                       % (ref, b["lib_id"], PAD_POS_TOL, PAD_SIZE_TOL, CEN_TOL))
        dfab = round(abs(g["fab_w"] - b["fab_w"]) + abs(g["fab_h"] - b["fab_h"]), 3)
        if dfab > FAB_TOL:
            b4.append("%s: fab 外框 Δ %.3f mm > 容差 %.2f mm" % (ref, dfab, FAB_TOL))
    for ref in sorted(nw):
        b = bg.get(ref)
        if b is None:
            continue
        if b["lib_id"]:
            b5.append("%s: 不该写库名却有 lib_id = %s" % (ref, b["lib_id"]))
    results["B1"] = {"ok": not b1, "detail": "%d 件要写库名的封装 lib_id 全非空"
                      % len(wt) if not b1 else "; ".join(b1[:8])}
    results["B2"] = {"ok": not b2, "detail": "%d 件的 lib_id == 计划且 .kicad_mod 全在盘 + md5 对得上"
                      % len(wt) if not b2 else "; ".join(b2[:8])}
    results["B3"] = {"ok": not b3, "detail": "%d 件的板上焊盘数 == 官方件焊盘数"
                      % len(wt) if not b3 else "; ".join(b3[:8])}
    results["B4"] = {"ok": not b4,
                     "detail": "%d 件的板面几何与官方件在容差内 (pos≤%.2f size≤%.2f cen≤%.2f fab≤%.2f mm)"
                     % (len(wt), PAD_POS_TOL, PAD_SIZE_TOL, CEN_TOL, FAB_TOL)
                     if not b4 else "; ".join(b4[:8])}
    results["B5"] = {"ok": not b5, "detail": "%d 件不该写库名的封装 lib_id 全为空"
                      % len(nw) if not b5 else "; ".join(b5[:8])}
    return results, facts


# ---------------------------------------------------------------- 输出

def print_report(results, facts, as_json=False, title="【ISS-369 板面库封装名写盘闸】"):
    if as_json:
        print(json.dumps({"ok": all(v["ok"] for v in results.values()),
                          "results": results, "facts": facts}, ensure_ascii=False, indent=1))
        return
    print(title)
    for cid in sorted(results.keys()):
        r = results[cid]
        print("  [%s] %s :: %s" % ("PASS" if r["ok"] else "FAIL", cid, r["detail"]))
    print("  事实: 板面封装=%s · C4=%s · 靶内=%s + 缺口=%s = %s · 其余=%s · 板 md5=%s"
          % (facts.get("board_footprints"), facts.get("c4_total"),
             facts.get("inter_total"), facts.get("gap_total"), facts.get("target_total"),
             facts.get("rest_total"), facts.get("board_md5")))
    print("  容差: pos≤%.2f mm · size≤%.2f mm · cen≤%.2f mm · fab≤%.2f mm"
          % (PAD_POS_TOL, PAD_SIZE_TOL, CEN_TOL, FAB_TOL))


# ---------------------------------------------------------------- selftest

def _mutate_row(text, ref, table_must, colmut=None, drop=False):
    """在【指定表内】定位 ref 那一行并做一次变异 ⇒ (新文本, 原行, 新行)"""
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


def _mutate_cell(text, header_must, col_key, newvalue, table_idx=0):
    """★在指定表的指定列上改值 (不定位 ref) ⇒ (新文本, 原值, 新值)★"""
    lines = text.splitlines()
    head, rows, _i, _j, idxs = find_table_span(lines, header_must)
    if head is None or not idxs:
        return None, None, None
    k = None
    for i, c in enumerate(head):
        if c.replace("`", "") == col_key.replace("`", ""):
            k = i
            break
    if k is None:
        return None, None, None
    li = idxs[0]
    cells = [c.strip() for c in lines[li].strip("|").split("|")]
    old = cells[k]
    cells[k] = newvalue
    lines[li] = "| " + " | ".join(cells) + " |"
    return "\n".join(lines), old, newvalue


def probe_ok(probe, n, o):
    """★变异「真的改到了目标」的自证探针★
    普通串   : 该串【在副本里 且 不在原文档里】
    !row;表头;ref      : 该表里这一行已经不在了
    !empty;表头;ref;列 : 该表里这一行的该列已经空了
    !emptylib;ref      : 板副本里该封装的 lib_id 已经空了
    !newlib;ref;值     : 板副本里该封装的 lib_id 已经变成该值
    """
    if not probe:
        return True
    if probe.startswith("!row;"):
        _, must, ref = probe.split(";")
        head, rows = find_table(n.splitlines(), [must])
        if head is None:
            return False
        return not any(r and r[0].strip("`").strip() == ref for r in rows)
    if probe.startswith("!empty;"):
        _, must, ref, col = probe.split(";")
        head, rows = find_table(n.splitlines(), [must])
        if head is None:
            return False
        for r in rows:
            if r and r[0].strip("`").strip() == ref:
                return not cell(r, head, col).strip()
        return False
    if probe.startswith("!emptylib;"):
        ref = probe.split(";")[1]
        bg = board_geom_from_text(n)
        return bool(bg.get(ref)) and bg[ref]["lib_id"] == ""
    if probe.startswith("!newlib;"):
        _, ref, val = probe.split(";")
        bg = board_geom_from_text(n)
        return bool(bg.get(ref)) and bg[ref]["lib_id"] == val
    return (probe in n) and (probe not in o)


def selftest(root):
    doc_path = os.path.join(root, DOC_REL)
    if not os.path.isfile(doc_path):
        print("[FAIL] 找不到 %s" % doc_path)
        return 2
    orig = open(doc_path, encoding="utf-8").read()
    sandbox = os.path.join(root, "tmp", "iss369", "selftest")
    if os.path.isdir(sandbox):
        shutil.rmtree(sandbox)
    os.makedirs(sandbox, exist_ok=True)
    cases = []
    T1 = ["现占位几何", "目标几何", "降级方案"]
    T2 = ["动作", "理由", "证据等级", "不需要写"]
    T4 = ["轮次", "库名非空"]

    # ---- M1 删 §3.1 表里 R_PU_BOOT_N 那一行 ⇒ L2 红
    t, old, _ = _mutate_row(orig, "R_PU_BOOT_N", T1, drop=True)
    if t is None:
        print("[FAIL] M1 找不到 §3.1 R_PU_BOOT_N 行")
        return 2
    cases.append(("M1", "删 §3.1 一行 (R_PU_BOOT_N) ⇒ L2 红", "L2", orig, t,
                  "!row;现占位几何;R_PU_BOOT_N"))

    # ---- M2 把某行 .kicad_mod md5 改错 ⇒ L4 红
    def mut_md5(head, cells):
        for k, c in enumerate(head):
            if ".kicad_mod" in c.replace("`", ""):
                cells[k] = re.sub(r"md5\s+`[0-9a-f]{32}`",
                                  "md5 `deadbeefdeadbeefdeadbeefdeadbeef`", cells[k])
        return cells
    t, old, new = _mutate_row(orig, "R_PU_BOOT_N", T1, mut_md5)
    if t is None or old == new:
        print("[FAIL] M2 变异没命中")
        return 2
    cases.append(("M2", "改 .kicad_mod md5 ⇒ L4 红", "L4", orig, t, "deadbeefdeadbeefdeadbeefdeadbeef"))

    # ---- M3 把某行目标焊盘数改错 ⇒ L5 红
    def mut_pads(head, cells):
        for k, c in enumerate(head):
            if "目标几何" in c.replace("`", ""):
                cells[k] = re.sub(r"焊盘数\s*\d+", "焊盘数 9", cells[k])
        return cells
    t, old, new = _mutate_row(orig, "R_PU_BOOT_N", T1, mut_pads)
    if t is None or old == new:
        print("[FAIL] M3 变异没命中")
        return 2
    cases.append(("M3", "改目标焊盘数 ⇒ L5 红", "L5", orig, t, "焊盘数 9"))

    # ---- M4 清空某行降级方案 ⇒ L3 红
    def mut_down(head, cells):
        for k, c in enumerate(head):
            if c.replace("`", "") == "降级方案":
                cells[k] = " "
        return cells
    t, old, new = _mutate_row(orig, "R_PU_BOOT_N", T1, mut_down)
    if t is None or old == new:
        print("[FAIL] M4 变异没命中")
        return 2
    cases.append(("M4", "清空降级方案 ⇒ L3 红", "L3", orig, t,
                  "!empty;现占位几何;R_PU_BOOT_N;降级方案"))

    # ---- M5 证据等级写成 [官方] ⇒ L6 红
    def mut_ev(head, cells):
        for k, c in enumerate(head):
            if c.replace("`", "") == "证据等级":
                cells[k] = "[官方]"
        return cells
    t, old, new = _mutate_row(orig, "R_PU_BOOT_N", T1, mut_ev)
    if t is None or old == new:
        print("[FAIL] M5 变异没命中")
        return 2
    cases.append(("M5", "证据等级写成 [官方] ⇒ L6 红", "L6", orig, t, "[官方]"))

    # ---- M6 正文塞「等原厂回信」⇒ L7 红
    t = "等原厂回信\n\n" + orig
    cases.append(("M6", "正文塞「等原厂回信」⇒ L7 红", "L7", orig, t, "等原厂回信"))

    # ---- M7 篡改基准块 counts.target_total (90→89) ⇒ L1 红
    if '"target_total": 90,' not in orig:
        print("[FAIL] M7 没找到 target_total: 90")
        return 2
    t = orig.replace('"target_total": 90,', '"target_total": 89,', 1)
    cases.append(("M7", "篡改基准块 counts.target_total ⇒ L1 红", "L1", orig, t, '"target_total": 89,'))

    # ---- M8 把页内 §4.1 表的 C4 数字改成 68 ⇒ L8 红
    lines = orig.splitlines()
    head4, rows4, _i, _j, idxs = find_table_span(lines, T4)
    if head4 is None or not idxs:
        print("[FAIL] M8 找不到 §4.1 表")
        return 2
    k = None
    for i, c in enumerate(head4):
        if "C4" in c.replace("`", ""):
            k = i
            break
    if k is None:
        print("[FAIL] M8 §4.1 表没有 C4 列")
        return 2
    li = idxs[0]
    cells = [c.strip() for c in lines[li].strip("|").split("|")]
    cells[k] = "**68**"
    lines[li] = "| " + " | ".join(cells) + " |"
    t = "\n".join(lines)
    cases.append(("M8", "把 §4.1 的 C4 改成 68 ⇒ L8 红", "L8", orig, t, "**68**"))

    # ---- M9 把 §3.2 表里某一件的 ref 改成板面不存在的 ref ⇒ L2 红
    lines = orig.splitlines()
    head2, rows2, _i, _j, idxs = find_table_span(lines, T2)
    if head2 is None or not idxs:
        print("[FAIL] M9 找不到 §3.2 表")
        return 2
    li = None
    for i, r in enumerate(rows2):
        if r and r[0].strip("`").strip() == "CONN_CAM":
            li = idxs[i]
            break
    if li is None:
        print("[FAIL] M9 找不到 §3.2 CONN_CAM 行")
        return 2
    cells = [c.strip() for c in lines[li].strip("|").split("|")]
    cells[0] = "`CONN_CAM_X`"
    lines[li] = "| " + " | ".join(cells) + " |"
    t = "\n".join(lines)
    cases.append(("M9", "把 §3.2 一件的 ref 改成板面没有的 ref ⇒ L2 红", "L2", orig, t, "CONN_CAM_X"))

    all_ok = True
    for cid, desc, expect_red, o, n, probe in cases:
        if n == o:
            print("[FAIL] %s 变异没落到副本上 (串没命中) ⇒ 不能证明红的是目标那一条" % cid)
            all_ok = False
            continue
        # ★探针自证: 变异串必须【在副本里 且 不在原文档里】★
        if not probe_ok(probe, n, o):
            print("[FAIL] %s 探针自证失败 ⇒ 变异没生效" % cid)
            all_ok = False
            continue
        cp = os.path.join(sandbox, "FP_LIBID_TRUTH_%s.md" % cid)
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

    # ---- 板面模式反向用例 (B1 / B2)
    sbx_board = os.path.join(root, SANDBOX_DIR, "board_legA_plus_libid.kicad_pcb")
    if not os.path.isfile(sbx_board):
        print("[FAIL] 找不到沙盒板副本 %s ⇒ 板面模式反向用例跑不了" % sbx_board)
        all_ok = False
    else:
        btxt = open(sbx_board, encoding="utf-8").read()
        b_cases = []

        def _first_named(t):
            for m2 in re.finditer(r'^\t\(footprint "([^"]+)"', t, re.M):
                if not m2.group(1):
                    continue
                s = m2.start()
                cands = [t.find("\n\t(footprint ", s + 1), t.find("\n\t(net ", s + 1)]
                cands = [c for c in cands if c != -1]
                e = min(cands) if cands else len(t)
                blk = t[s:e]
                rm = re.search(r'\(property "Reference" "([^"]*)"', blk)
                return m2.group(1), (rm.group(1) if rm else None), s, e
            return None, None, None, None

        lib0, ref0, s0, e0 = _first_named(btxt)
        if lib0 is None or ref0 is None:
            print("[FAIL] 沙盒板副本里没有具名封装")
            all_ok = False
        else:
            # B1: 把某件的 lib_id 清空
            n1 = btxt[:s0] + btxt[s0:e0].replace('\t(footprint "%s"' % lib0,
                                                 '\t(footprint ""', 1) + btxt[e0:]
            if n1 == btxt:
                print("[FAIL] B1 变异没命中")
                all_ok = False
            else:
                b_cases.append(("B1", "把沙盒板里 %s 的 lib_id 清空 ⇒ B1 红" % ref0,
                                "B1", btxt, n1, "!emptylib;%s" % ref0))
            # B2: 把某件的 lib_id 改成一个本机不存在的库
            n2 = btxt[:s0] + btxt[s0:e0].replace(
                '\t(footprint "%s"' % lib0,
                '\t(footprint "NoSuchLib_XYZ:NoSuchFootprint_XYZ"', 1) + btxt[e0:]
            if n2 == btxt:
                print("[FAIL] B2 变异没命中")
                all_ok = False
            else:
                b_cases.append(("B2", "把沙盒板里 %s 的 lib_id 改成不存在的库 ⇒ B2 红" % ref0,
                                "B2", btxt, n2,
                                "!newlib;%s;NoSuchLib_XYZ:NoSuchFootprint_XYZ" % ref0))
        for cid, desc, expect_red, o, n, probe in b_cases:
            if not probe_ok(probe, n, o):
                print("[FAIL] %s 探针没生效" % cid)
                all_ok = False
                continue
            cp = os.path.join(sandbox, "board_%s.kicad_pcb" % cid)
            with open(cp, "w", encoding="utf-8") as fh:
                fh.write(n)
            res, _ = check_board(cp, root)
            reds = sorted(k for k, v in res.items() if not v["ok"])
            ok = (reds == [expect_red])
            print("  [%s] %s :: 期望红 %s ⇒ 实得红 %s :: %s"
                  % ("PASS" if ok else "FAIL", cid, expect_red, reds or "无",
                     res.get(expect_red, {}).get("detail", "")[:110]))
            if not ok:
                all_ok = False
        # ★基准: 沙盒板原样跑板面模式 ⇒ 必须全绿 (否则上面两条不算「只红目标那一条」)★
        res, _ = check_board(sbx_board, root)
        reds = sorted(k for k, v in res.items() if not v["ok"])
        ok = (reds == [])
        print("  [%s] B0 :: 沙盒板原样 ⇒ 期望全绿 ⇒ 实得红 %s :: %s"
              % ("PASS" if ok else "FAIL", reds or "无",
                 "; ".join(res[k]["detail"] for k in reds)[:160]))
        if not ok:
            all_ok = False

    shutil.rmtree(sandbox, ignore_errors=True)
    n_cases = len(cases) + 2
    if all_ok:
        print("SELFTEST %d/%d 全过 (每条都自证「红的是目标那一条, 其余仍绿」)" % (n_cases, n_cases))
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
    ap.add_argument("--mode", default="plan", choices=["plan", "board"])
    ap.add_argument("--board", default=None)
    args = ap.parse_args()

    root = args.root or find_root()
    if args.selftest:
        return selftest(root)

    if args.mode == "board":
        bp = args.board or os.path.join(root, SANDBOX_DIR, "board_legA_plus_libid.kicad_pcb")
        if not os.path.isfile(bp):
            print("[FAIL] 找不到板文件 %s" % bp)
            return 1
        res, facts = check_board(bp, root, args.libroot)
        print_report(res, facts, as_json=args.json,
                     title="【ISS-369 板面库封装名写盘闸 · 板面模式】%s" % os.path.basename(bp))
        bad = [k for k, v in res.items() if not v["ok"]]
        if bad:
            print("RED: %s" % ",".join(bad))
            return 1
        print("ALL CHECKS PASS")
        return 0

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
