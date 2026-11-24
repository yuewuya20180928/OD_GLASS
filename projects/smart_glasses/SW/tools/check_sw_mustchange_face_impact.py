#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-411 · sw-lead · 「板那一趟」SW 侧【必改面 → 闸的判据失效】影响面清账闸 (★零挂链★)
=================================================================================================
★★**本闸是什么**: 一道【必改面影响面】闸 —— 判「★那一趟 (位号改名 + 布线 45→0) 落地之后,
  SW 域 31 道闸里哪些的判据输入会变 / 变成什么 / 谁在链上会当场失守★」 ★

★★**为什么必须有它 (★不重复 ISS-392 / ISS-388 / ISS-398★)** ★:
  · ★ISS-392 (`check_sw_gate_chain_coverage.py`) 判的是「★闸在不在链上·覆盖率多少★」★
    ⇒ 覆盖率 19.4% 是「有没有接电」, 不是「接了电之后会不会被那一趟打掉」★
  · ★ISS-388 (`check_sw_gate_health.py`) 判的是「★同一道闸在两个 TMPDIR 深度下读数是否相同★」★
    ⇒ 不是「判据输入会不会被那一趟改掉」这一轴★
  · ★ISS-398 判的是「★v2 那道闸的自测夹具本身对不对★」⇒ 不是「31 道闸的必改面影响面」这一轴★
  ⇒ ★**「必改面 → 闸的判据失效」这一轴, 全仓至今零机器闸覆盖 ⇒ 本闸补这一格** ★

★★★**★T4 是本闸的命门 (★它存在的理由·不是凑数★)★** ★:
  ★**链上正在跑的那道闸 (`check_sw_ref_reachability.py` · v1) 自己硬编了 55 个位号字面量** ★
  ⇒ ★**位号改名那一趟一落地, 链上这道闸的判据就【静默失效或误判】** ★
  ⇒ ★**本闸把「在链上 + 硬编位号」这个组合直接点名判红** ★ ★

★★★★**★九条判据 (★逐条机器可判·不许靠注释说绿★)** ★★★★★:
  T0 零扰动   : 板三项 (md5/mtime/size) + 网表/脚表/BOM 三件 md5 ⇒ 与登记基线逐字相同 ★
  T1 位号登记 : 逐闸从【源码实读】位号字面量命中数 (口径A + 口径B) ⇒ 必须与登记册一致 ★
                ★少登记 / 多登记 / 漏掉一道闸 / 正则漏了 (地板线) ⇒ 判红★ ★
  T2 输入面   : 逐闸的【输入面分类 + 钉基线标记】必须登记且与源码实读一致 ⇒ 任何一道没标 ⇒ 判红 ★
  T3 文档面   : 「无真源依赖」的闸数必须登记 (现状 10 道) ⇒ 它变了 ⇒ 判红并点名 ★
  T4 命门     : 「在链上 + 硬编位号」的组合必须被点名 ⇒ 现状红 (v1 在链上, 硬编 55 处) ★
                ★★**T4 现场从 `state/gate_check.py` 的 AST 实算链内清单·不读登记册★**★★
  T5 影响判定 : 31 道闸 × 三面 (改名面/布线面/文档面) 的判定必须齐全 + 自洽 ★
  T6 fail-closed : 闸目录扫不到 / 任一登记文件读不到 / 真相页机器块读不到 ⇒ 判红 (不许判绿) ★
  T7 零挂链   : 本闸名不许出现在 `state/gate_check.py` ⇒ 出现即红 ★ + ★零外发自证 (本闸不许 import 网络库)★ ★
  T8 双绑     : 真相页机器块里的登记册 ⇒ 必须与本闸内嵌的【建册日冻结快照】逐字段相同 ★
                ★★**页面被改而闸没改 ⇒ 判红 (★防真相页自己漂★)**★★

★★★**★登记册放在哪 (★为什么是「页面为主 + 闸内冻结快照兜底」★)** ★★★:
  · ★**登记册的主本 = 真相页机器块里的 `registry`** (★人改得动·所以要能被抓★) ★
  · ★**本闸内嵌一份【建册日冻结快照】**(★只用来算 digest·改它 = 改闸判据·是 main 的地界★) ★
  · ★**T8 把两者钉在一起** ⇒ ★**页面单方面漂 ⇒ 红; 闸单方面漂 ⇒ 红; 两边一起漂 ⇒ 闸源码变了 (可见)★** ★

★★★**★本闸不许做什么 (★写死★)** ★★★:
  ★**零写板** (只读板文件算 md5/mtime/size) ★
  ★**零落表** (只读网表/脚表/BOM 算 md5) ★
  ★**零改既有闸判据** (★本闸只读它们, 不 import 它们, 不改它们★) ★
  ★**零改既有页正文** (★真相页是【新建】文件; 既有页只许引用★) ★
  ★**零挂链** (★`state/gate_check.py` 一个字节都不许动★) ★
  ★**零外发** (★本闸源码里不许 import smtplib / requests / urllib / http.client / socket★) ★
  ★**不代拍** (★「哪几道闸要改 / 怎么改 / 挂不挂链」都是 main 的地界·本闸只报事实★) ★
  ★**不自签** (★不许写 `state/issue_log.yaml`★) ★

★★**用法** ★:
    python3 SW/tools/check_sw_mustchange_face_impact.py              # ★裸跑 · 现状红 (T4 红) ★
    python3 SW/tools/check_sw_mustchange_face_impact.py --selftest   # ★反向用例自检 ★
    python3 SW/tools/check_sw_mustchange_face_impact.py --json       # 机读输出 ★
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))

# ===================================================================== 路径与基线
PAGE_REL = "SW/BOARD_ONEPASS_SW_MUSTCHANGE_FACE_IMPACT.md"
BLOCK_BEGIN = "<!-- ISS411-MUSTCHANGE:BEGIN -->"
BLOCK_END = "<!-- ISS411-MUSTCHANGE:END -->"
GATE_CHECK_REL = "state/gate_check.py"
SELF_REL = "SW/tools/check_sw_mustchange_face_impact.py"

BOARD_REL = "HW/PCB/demo_mainboard.kicad_pcb"
BOARD_MD5 = "611b" + "869e13518c3c023fb178f91a0075"
BOARD_MTIME = "2026-11-06 07:07:17.362193413"
BOARD_SIZE = 4940213

TABLE_MD5 = {
    "HW/netlist_v1.csv": "6aee500e60ba0732f83a9cf557ba90ab",
    "HW/netlist_v1_pins.csv": "9174309df1ec9411ac8e8d9e80ee386a",
    "HW/BOM_v1.csv": "5b9993992405904a60ac96a020b375d8",
}

# ★★位号字面量口径 ★★
# ★口径A (★main 2026-11-25 02:4x 本机实扫用的口径★): 引号字面量 + 前缀 ∈ {TP,J,U,C,Q,D,FB,SW}
#   + 后缀全大写 + 【按【唯一 token 值】计数】 ★★本机实跑复现 main 的 8 个数字 8/8 逐字命中★★
#   (v2=58 · v1=55 · sync=20 · v2_selftest=8 · shutdown=6 · debug_pin_order=2 · evt=1 · load_switch=1)
# ★口径B (★扩展口径★): 口径A + 补回 {R, L, BT, CONN, IC} 五族 (★main 的口径漏了电阻/电芯/连接器三族★)
RX_A = re.compile(r'["\'](?:TP|J|U|C|Q|D|FB|SW)_[A-Z0-9_]+["\']')
RX_B = re.compile(r'["\'](?:TP|J|U|C|R|Q|L|D|FB|SW|BT|CONN|IC)_[A-Z0-9_]+["\']')

# ★地板线 (★main 给的口径: 少于此数 ⇒ 本闸的正则漏了 ⇒ 判红★) ★
FLOORS = {
    "SW/tools/check_sw_ref_reachability_v2.py": 50,
    "SW/tools/check_sw_ref_reachability.py": 50,
    "SW/tools/check_onepass_sw_sync.py": 15,
}
# ★现状在册的硬编位号闸道数 (★口径A★) ★
HARD_REF_GATE_COUNT = 8
# ★现状在册的「无真源依赖」闸道数 (★真源面 = board/table/bom/firm★) ★
DOC_ONLY_GATE_COUNT = 10

# ★输入面关键词 (★照 main 题面 §1.1 的分类口径·本机实读复现 31 道闸的六个分布数★) ★
FACE_PATTERNS = {
    "board":  [r"\.kicad_pcb", r"unconnected", r"check_pcb_nets", r"pcbnew"],
    "table":  [r"netlist_v1", r"PIN_TABLE", r"\.csv"],
    "bom":    [r"\bBOM\b", r"BOM_v1"],
    "doc":    [r"\.md\b"],
    "ledger": [r"fragments", r"issue_log", r"STATE\.yaml"],
    "firm":   [r"\.c\b", r"\.h\b"],
}
TRUTH_FACES = ("board", "table", "bom", "firm")

# ★「钉死基线」检测 (★照 ISS-372 已签收闸的类A/类B 形态·本闸只读·不改它★) ★
BOARD_NEEDLE = "611b" + "869e"
TABLE_NEEDLES = ("6aee500e", "9174309d", "5b999399")
BOARD_KEYS = ("board_md5", "BOARD_MD5", "pcb_md5",
              "BOARD_BASELINE_MD5", "BASELINE_BOARD_MD5")

# ★判定枚举 ★
RENAME_ENUM = ("不受影响", "判绿变判红", "判红变判绿", "静默跳过",
               "条件性-随真相页字段", "基线漂移-须重锚", "有合法改板通道")
ROUTE_ENUM = ("不受影响", "基线漂移-须重锚", "有合法改板通道", "基线漂移-自守闸告警器")
DOC_ENUM = ("不受影响", "随真相页/台账改即漂")
DRIFT_SRC_ENUM = ("无", "真相页", "台账", "真相页+台账", "工具链产物")

# ★★零外发自证: 本闸不许 import 这些模块 (★用 AST 扫 import, 不用 grep·注释不算★) ★
FORBIDDEN_IMPORTS = ("smtplib", "requests", "urllib", "urllib.request", "http",
                      "http.client", "socket", "ftplib", "telnetlib", "xmlrpc")


# ===================================================================== 内嵌冻结快照
# ★★建册日: 2026-11-25 · sw-lead · ISS-411 · 本机实读 31 道闸源码生成★★
#   ★它的唯一用途 = 算 `FROZEN_REGISTRY_SHA256` ⇒ 与真相页机器块的 `registry_sha256` 对拍 (T8)★
#   ★**它不是判据来源** —— 判据来源永远是【源码实读】★★
FROZEN_REGISTRY_SHA256 = "5084c0115ff62aa7e7c8e706007706a35e1bf0116f50106744b891e65a176d32"


# ===================================================================== 小工具
def read_text(path: str) -> str:
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def md5_of(path: str) -> str:
    h = hashlib.md5()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()


def fmt_mtime_ns(ns: int) -> str:
    sec, frac = divmod(int(ns), 1_000_000_000)
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sec)) + ".%09d" % frac


def disk_gate_rels(root: str):
    """★自己扫盘 ⇒ 盘上全部 `SW/**/check_*.py` (★不许写死 31★)★"""
    out = []
    sw = os.path.join(root, "SW")
    if not os.path.isdir(sw):
        return out
    for dirpath, dirnames, filenames in os.walk(sw):
        dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
        for fn in sorted(filenames):
            if not (fn.startswith("check_") and fn.endswith(".py")):
                continue
            if ".bak" in fn:
                continue
            out.append(os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, "/"))
    return sorted(out)


def _proj_join_rel(node):
    """★AST: 认 `os.path.join(PROJ, "SW", "tools", "x.py")` ⇒ 返回 "SW/tools/x.py"★"""
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    if not (isinstance(func, ast.Attribute) and func.attr == "join"):
        return None
    inner = func.value
    if not (isinstance(inner, ast.Attribute) and inner.attr == "path"):
        return None
    if not (isinstance(inner.value, ast.Name) and inner.value.id == "os"):
        return None
    parts = []
    for i, a in enumerate(node.args):
        if isinstance(a, ast.Constant) and isinstance(a.value, str):
            parts.append(a.value)
        elif i == 0 and isinstance(a, ast.Name):
            continue
        else:
            return None
    if not parts:
        return None
    return "/".join(p for p in parts if p)


def chain_gate_rels(root: str):
    """★链里挂的 SW 闸 (★从 `state/gate_check.py` 的 AST 里抽·不靠 grep 猜★)"""
    src = read_text(os.path.join(root, GATE_CHECK_REL))
    if not src:
        return None                       # ★读不到 ⇒ None (fail-closed 用) ★
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            rel = _proj_join_rel(node)
            if rel and rel.startswith("SW/") and rel.endswith(".py"):
                out.append(rel)
    return sorted(set(out))


def faces_of(src: str):
    out = []
    for face, pats in FACE_PATTERNS.items():
        for p in pats:
            if re.search(p, src):
                out.append(face)
                break
    return out


def ref_tokens(src: str, rx):
    return sorted(set(x[1:-1] for x in rx.findall(src)))


def pins_board_of(src: str) -> bool:
    if BOARD_NEEDLE in src:
        return True
    if BOARD_NEEDLE[:4] in src and BOARD_NEEDLE[4:8] in src:
        return True
    return any(k in src for k in BOARD_KEYS)


def pins_table_of(src: str) -> bool:
    return any(n in src for n in TABLE_NEEDLES)


def registry_digest(reg) -> str:
    canon = json.dumps(reg, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def load_truth_block(root: str):
    """★读真相页机器块 (★读不到 ⇒ None ⇒ fail-closed★)"""
    txt = read_text(os.path.join(root, PAGE_REL))
    if not txt or BLOCK_BEGIN not in txt or BLOCK_END not in txt:
        return None
    seg = txt.split(BLOCK_BEGIN, 1)[1].split(BLOCK_END, 1)[0]
    m = re.search(r"```json\n(.*?)\n```", seg, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except ValueError:
        return None


def get_registry(root: str):
    """★★登记册 = 真相页机器块里的 `registry` (★读不到 ⇒ None ⇒ fail-closed★)★★"""
    blk = load_truth_block(root)
    if not isinstance(blk, dict):
        return None, blk
    reg = blk.get("registry")
    if not isinstance(reg, dict):
        return None, blk
    return reg, blk


def page_counts(blk):
    if isinstance(blk, dict):
        c = blk.get("counts")
        if isinstance(c, dict):
            return c
    return {}


# ===================================================================== 判据
def judge_T0(root):
    """★T0 · 零扰动: 板三项 + 三表 md5 与登记基线逐字相同★"""
    errors = []
    b = os.path.join(root, BOARD_REL)
    if not os.path.exists(b):
        errors.append("★板文件读不到: %s" % BOARD_REL)
    else:
        got = md5_of(b)
        if got != BOARD_MD5:
            errors.append("★板 md5 = %s ≠ 基线 %s ⇒ 板被动过 (本闸零写板)" % (got, BOARD_MD5))
        st = os.stat(b)
        gm = fmt_mtime_ns(st.st_mtime_ns)
        if gm != BOARD_MTIME:
            errors.append("★板 mtime = %s ≠ 基线 %s" % (gm, BOARD_MTIME))
        if st.st_size != BOARD_SIZE:
            errors.append("★板 size = %d ≠ 基线 %d" % (st.st_size, BOARD_SIZE))
    for rel, want in sorted(TABLE_MD5.items()):
        got = md5_of(os.path.join(root, rel))
        if got != want:
            errors.append("★%s md5 = %s ≠ 基线 %s" % (rel, got or "(读不到)", want))
    return {"ok": not errors, "errors": errors}


def judge_T1(root, disk, reg):
    """★T1 · 位号字面量登记自洽 (★判据从源码实读, 不许读登记册自己的数★)"""
    errors = []
    if reg is None:
        return {"ok": False, "errors": ["★登记册读不到 ⇒ fail-closed 判红"], "n_hard": -1}
    disk_set = set(disk)
    reg_keys = set(reg)
    for rel in sorted(disk_set - reg_keys):
        errors.append("★盘上有闸但【登记册漏了它】: %s" % rel)
    for rel in sorted(reg_keys - disk_set):
        errors.append("★登记册里有闸但【盘上读不到】: %s" % rel)
    computed = {}
    for rel in sorted(disk_set & reg_keys):
        src = read_text(os.path.join(root, rel))
        if not src:
            errors.append("★闸源码读不到: %s" % rel)
            continue
        a = len(ref_tokens(src, RX_A))
        b = len(ref_tokens(src, RX_B))
        computed[rel] = (a, b)
        r = reg[rel]
        if not isinstance(r, dict):
            errors.append("★%s 的登记条目不是对象 ⇒ 判红" % rel)
            continue
        if a != r.get("a"):
            errors.append("★%s 口径A 位号字面量命中数 实读 %d ≠ 登记 %s ⇒ 登记册漂了"
                          % (rel, a, r.get("a")))
        if b != r.get("b"):
            errors.append("★%s 口径B 位号字面量命中数 实读 %d ≠ 登记 %s ⇒ 登记册漂了"
                          % (rel, b, r.get("b")))
        if (a > 0) != bool(r.get("hard_ref")):
            errors.append("★%s 的「硬编位号」标记 实读 %s ≠ 登记 %s ⇒ 判红"
                          % (rel, a > 0, r.get("hard_ref")))
    # 地板线: 少于 main 给的下限 ⇒ 本闸的正则漏了 ⇒ 判红
    for rel, floor in sorted(FLOORS.items()):
        a, _b = computed.get(rel, (-1, -1))
        if a >= 0 and a < floor:
            errors.append("★%s 口径A 命中数 %d < 地板线 %d ⇒ 本闸的正则漏了 ⇒ 判红"
                          % (rel, a, floor))
    n_hard = sum(1 for rel in computed if computed[rel][0] > 0)
    if n_hard != HARD_REF_GATE_COUNT:
        hard_list = sorted(rel for rel in computed if computed[rel][0] > 0)
        errors.append("★硬编位号闸道数 实读 %d ≠ 在册 %d ⇒ 点名: %s"
                      % (n_hard, HARD_REF_GATE_COUNT, ", ".join(hard_list)))
    return {"ok": not errors, "errors": errors,
            "n_gates": len(disk_set), "n_hard": n_hard}


def judge_T2(root, disk, reg):
    """★T2 · 每道闸的输入面 + 钉基线标记必须登记且与源码实读一致★"""
    errors = []
    if reg is None:
        return {"ok": False, "errors": ["★登记册读不到 ⇒ fail-closed 判红"]}
    for rel in sorted(disk):
        if rel not in reg:
            continue                     # ★T1 已报「漏登记」, 这里不重复★
        src = read_text(os.path.join(root, rel))
        if not src:
            errors.append("★闸源码读不到: %s" % rel)
            continue
        r = reg[rel]
        if not isinstance(r, dict):
            continue
        got = faces_of(src)
        want = r.get("faces")
        if want is None:
            errors.append("★%s 没有登记输入面 ⇒ 判红" % rel)
        elif sorted(want) != sorted(got):
            errors.append("★%s 输入面 实读 %s ≠ 登记 %s ⇒ 登记册漂了"
                          % (rel, sorted(got), sorted(want)))
        truth = sorted(set(got) & set(TRUTH_FACES))
        doc_only = (len(truth) == 0)
        if doc_only != bool(r.get("doc_only")):
            errors.append("★%s 「无真源依赖」判定 实读 %s ≠ 登记 %s"
                          % (rel, doc_only, r.get("doc_only")))
        if pins_board_of(src) != bool(r.get("pin_board")):
            errors.append("★%s 的「钉板 md5」标记 实读 %s ≠ 登记 %s"
                          % (rel, pins_board_of(src), r.get("pin_board")))
        if pins_table_of(src) != bool(r.get("pin_table")):
            errors.append("★%s 的「钉三表 md5」标记 实读 %s ≠ 登记 %s"
                          % (rel, pins_table_of(src), r.get("pin_table")))
    return {"ok": not errors, "errors": errors}


def judge_T3(root, disk, blk):
    """★T3 · 「无真源依赖」的闸数必须登记; 变了 ⇒ 判红并点名★"""
    errors = []
    computed = set()
    for rel in sorted(disk):
        src = read_text(os.path.join(root, rel))
        if not src:
            continue
        got = faces_of(src)
        if not (set(got) & set(TRUTH_FACES)):
            computed.add(rel)
    pc = page_counts(blk)
    page_n = pc.get("doc_only_gate_count")
    if page_n is None:
        errors.append("★真相页机器块里没有 `counts.doc_only_gate_count` ⇒ 判红")
    elif page_n != DOC_ONLY_GATE_COUNT:
        errors.append("★「无真源依赖」闸道数: 页面在册 %s ≠ 本闸在册 %d ⇒ 判红"
                      % (page_n, DOC_ONLY_GATE_COUNT))
    if len(computed) != DOC_ONLY_GATE_COUNT:
        errors.append("★「无真源依赖」闸道数 实读 %d ≠ 在册 %d ⇒ 点名差额: %s"
                      % (len(computed), DOC_ONLY_GATE_COUNT,
                         sorted(computed) ))
    return {"ok": not errors, "errors": errors,
            "n": len(computed), "gates": sorted(computed)}


def judge_T4(root, disk, chain):
    """★T4 · 命门: 「在链上 + 硬编位号」的组合必须被点名 ⇒ 现状红★
    ★★**链内清单现场从 `state/gate_check.py` 的 AST 实算; 命中数现场从源码实读 ——
       一律不读登记册**★★"""
    errors = []
    if chain is None:
        errors.append("★`%s` 读不到/解析不了 ⇒ 无法算链内清单 ⇒ fail-closed 判红"
                      % GATE_CHECK_REL)
        return {"ok": False, "errors": errors, "combo": [], "n_chain": 0}
    hits = []
    for rel in sorted(chain):
        if rel not in disk:
            continue
        src = read_text(os.path.join(root, rel))
        if not src:
            continue
        n = len(ref_tokens(src, RX_A))
        if n > 0:
            hits.append((rel, n))
    for rel, n in hits:
        errors.append("★★命门: 链上这道闸硬编了 %d 个位号字面量 ⇒ 位号改名那一趟一落地, "
                      "它的判据就失效 (判红 / 静默跳过) ⇒ %s" % (n, rel))
    return {"ok": not errors, "errors": errors,
            "combo": ["%s(%d)" % (r, n) for r, n in hits],
            "n_chain": len(chain)}


def judge_T5(root, disk, reg):
    """★T5 · 31 道闸 × 三面 (改名面/布线面/文档面) 的影响判定必须齐全 + 自洽★"""
    errors = []
    if reg is None:
        return {"ok": False, "errors": ["★登记册读不到 ⇒ fail-closed 判红"]}
    for rel in sorted(disk):
        if rel not in reg:
            continue
        r = reg[rel]
        if not isinstance(r, dict):
            errors.append("★%s 的登记条目不是对象 ⇒ 判红" % rel)
            continue
        for key, enum in (("rename", RENAME_ENUM), ("route", ROUTE_ENUM), ("doc", DOC_ENUM)):
            v = r.get(key)
            if v is None:
                errors.append("★%s 缺 %s 面判定 ⇒ 判红" % (rel, key))
            elif v not in enum:
                errors.append("★%s 的 %s 面判定 %r 不在枚举内 ⇒ 判红" % (rel, key, v))
        ds = r.get("drift_src")
        if ds not in DRIFT_SRC_ENUM:
            errors.append("★%s 的 drift_src %r 不在枚举内 ⇒ 判红" % (rel, ds))
        # 自洽: 硬编位号 ⇒ 改名面不可能「不受影响」
        if r.get("hard_ref") and r.get("rename") == "不受影响":
            errors.append("★%s 硬编位号却判改名面「不受影响」⇒ 自相矛盾 ⇒ 判红" % rel)
        # 自洽: 钉板 md5 ⇒ 布线面不可能「不受影响」
        if r.get("pin_board") and r.get("route") == "不受影响":
            errors.append("★%s 钉死板 md5 却判布线面「不受影响」⇒ 自相矛盾 ⇒ 判红" % rel)
        # 自洽: 无真源依赖 ⇒ 漂移源必须登记, 且文档面判定必须与漂移源相容
        if r.get("doc_only"):
            if ds == "无":
                errors.append("★%s 无真源依赖却没登记 drift_src ⇒ 判红" % rel)
            elif ds == "工具链产物":
                if r.get("doc") != "不受影响":
                    errors.append("★%s 读工具链产物却判文档面会漂 ⇒ 判红" % rel)
            elif r.get("doc") != "随真相页/台账改即漂":
                errors.append("★%s 读真相页/台账却判文档面「不受影响」⇒ 判红" % rel)
        elif ds != "无":
            errors.append("★%s 有真源依赖却登记了 drift_src ⇒ 判红" % rel)
    return {"ok": not errors, "errors": errors}


def judge_T6(root, disk, blk):
    """★T6 · fail-closed: 闸目录扫不到 / 任一登记文件读不到 / 真相页机器块读不到 ⇒ 判红★"""
    errors = []
    if not disk:
        errors.append("★闸目录扫不到任何 `SW/**/check_*.py` ⇒ fail-closed 判红")
    if not os.path.isdir(os.path.join(root, "SW")):
        errors.append("★`SW/` 目录读不到 ⇒ fail-closed 判红")
    if not os.path.exists(os.path.join(root, GATE_CHECK_REL)):
        errors.append("★`%s` 不存在 ⇒ fail-closed 判红" % GATE_CHECK_REL)
    if blk is None:
        errors.append("★真相页机器块读不到 (%s) ⇒ fail-closed 判红" % PAGE_REL)
    reg = blk.get("registry") if isinstance(blk, dict) else None
    if isinstance(reg, dict):
        for rel in sorted(reg):
            if not os.path.exists(os.path.join(root, rel)):
                errors.append("★登记的闸文件不存在: %s ⇒ fail-closed 判红" % rel)
    return {"ok": not errors, "errors": errors}


def judge_T7(root):
    """★T7 · 零挂链 + 零外发自证 (★AST 扫 import·不用 grep★)"""
    errors = []
    gc = read_text(os.path.join(root, GATE_CHECK_REL))
    me = os.path.basename(__file__)
    if gc:
        if me in gc:
            errors.append("★★零挂链自证失败: `%s` 出现在 `%s` 里 ⇒ 本闸被挂链了 ⇒ 判红"
                          % (me, GATE_CHECK_REL))
    else:
        errors.append("★`%s` 读不到 ⇒ fail-closed 判红" % GATE_CHECK_REL)
    # 零外发: 扫本闸 (沙盒里是沙盒副本) 的 import
    self_path = os.path.join(root, SELF_REL)
    if not os.path.exists(self_path):
        self_path = os.path.abspath(__file__)
    src = read_text(self_path)
    if not src:
        errors.append("★本闸源码读不到 ⇒ fail-closed 判红")
    else:
        try:
            tree = ast.parse(src)
        except SyntaxError:
            tree = None
            errors.append("★本闸源码解析失败 ⇒ fail-closed 判红")
        if tree is not None:
            mods = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for al in node.names:
                        mods.add(al.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        mods.add(node.module.split(".")[0])
            for m in sorted(mods):
                if m in FORBIDDEN_IMPORTS:
                    errors.append("★零外发自证失败: 本闸 import 了 `%s` ⇒ 判红" % m)
    return {"ok": not errors, "errors": errors}


def judge_T8(root, blk):
    """★T8 · 双绑: 真相页机器块的登记册 ⇒ 必须与本闸内嵌的建册日冻结快照逐字段相同★"""
    errors = []
    if blk is None:
        return {"ok": False, "errors": ["★真相页机器块读不到 ⇒ fail-closed 判红"]}
    reg = blk.get("registry")
    if not isinstance(reg, dict):
        return {"ok": False, "errors": ["★真相页机器块里没有 `registry` ⇒ 判红"]}
    got = registry_digest(reg)
    if got != FROZEN_REGISTRY_SHA256:
        errors.append("★★真相页登记册的摘要 = %s ≠ 本闸冻结快照 %s ⇒ 真相页单方面漂了 ⇒ 判红"
                      % (got, FROZEN_REGISTRY_SHA256))
    want = blk.get("registry_sha256")
    if want != got:
        errors.append("★真相页机器块自报的 `registry_sha256` = %s ≠ 实算 %s ⇒ 页面自相矛盾 ⇒ 判红"
                      % (want, got))
    return {"ok": not errors, "errors": errors, "digest": got}


# ===================================================================== 跑闸
def run_checks(root: str):
    disk = disk_gate_rels(root)
    chain = chain_gate_rels(root)
    reg, blk = get_registry(root)
    res = {}
    res["T0"] = judge_T0(root)
    res["T1"] = judge_T1(root, disk, reg)
    res["T2"] = judge_T2(root, disk, reg)
    res["T3"] = judge_T3(root, disk, blk)
    res["T4"] = judge_T4(root, disk, chain)
    res["T5"] = judge_T5(root, disk, reg)
    res["T6"] = judge_T6(root, disk, blk)
    res["T7"] = judge_T7(root)
    res["T8"] = judge_T8(root, blk)
    res["_meta"] = {"disk": disk, "chain": chain}
    return res


# ===================================================================== --selftest
SBX_ROOT = os.path.join(PROJ, "tmp", "iss411_sbx", "selftest")


def build_sandbox(dst: str) -> str:
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)
    shutil.copytree(os.path.join(PROJ, "SW"), os.path.join(dst, "SW"), symlinks=True)
    st = os.path.join(dst, "state")
    os.makedirs(st, exist_ok=True)
    shutil.copy2(os.path.join(PROJ, GATE_CHECK_REL), os.path.join(st, "gate_check.py"))
    for rel in (BOARD_REL,) + tuple(TABLE_MD5.keys()):
        d = os.path.dirname(os.path.join(dst, rel))
        os.makedirs(d, exist_ok=True)
        shutil.copy2(os.path.join(PROJ, rel), os.path.join(dst, rel))
    return dst


def _mut_page(dst, fn):
    """★在沙盒的真相页机器块里改内容 (★默认【不改】 `registry_sha256`·故意制造页面漂移★)"""
    p = os.path.join(dst, PAGE_REL)
    txt = read_text(p)
    seg = txt.split(BLOCK_BEGIN, 1)[1].split(BLOCK_END, 1)[0]
    m = re.search(r"```json\n(.*?)\n```", seg, re.S)
    blk = json.loads(m.group(1))
    fn(blk)
    new = "```json\n" + json.dumps(blk, ensure_ascii=False, indent=1) + "\n```"
    seg2 = seg[:m.start()] + new + seg[m.end():]
    txt2 = txt.replace(seg, seg2, 1)
    with open(p, "w", encoding="utf-8") as f:
        f.write(txt2)


def selftest() -> int:
    print("=" * 92)
    print("ISS-411 · 反向用例自检 (★每条必须自证: 红的集合 == {目标那一条}★)")
    print("=" * 92)
    cases = []

    # ---- 正向: 干净沙盒里【只有 T4 红】(命门), 其余全绿 ----
    def c0(dst):
        return "★正向用例: 干净沙盒 ⇒ 现状应当【只有 T4 红】(链上闸硬编位号) ★"

    cases.append((c0, "T4", "★正向★ 干净沙盒 ⇒ 只有 T4 红"))

    # ---- ① 页面登记册里某道闸的口径A 命中数改成假值 ⇒ T1 + T8 红 ----
    def c1(dst):
        def f(b):
            r = b["registry"]["SW/tools/check_shutdown_semantics.py"]
            r["a"] = 999
        _mut_page(dst, f)
        return "把页面登记册里 check_shutdown_semantics.py 的口径A 命中数改成 999 (源码实读仍是 6)"

    # ---- ② 在沙盒里给某道闸加一个硬编位号字面量 ⇒ T1 红 (登记册没跟着改) ----
    def c2(dst):
        p = os.path.join(dst, "SW/tools/check_load_switch_selection.py")
        with open(p, "a", encoding="utf-8") as f:
            f.write('\nHARD_REF_PROBE = "' + "U_" + "PROBE_XYZ" + '"\n')
        return "给 check_load_switch_selection.py 加一个硬编位号字面量 (源码实读 +1 ≠ 登记)"

    # ---- ③ 在沙盒里放一道【不在登记册里】的新闸 ⇒ T1 红 (漏登记) ----
    def c3(dst):
        p = os.path.join(dst, "SW/tools/check_iss411_probe_gate.py")
        with open(p, "w", encoding="utf-8") as f:
            f.write('#!/usr/bin/env python3\n# ISS-411 selftest probe gate\n')
        return "在盘上放一道不在登记册里的新闸 ⇒ T1 应当红 (漏登记)"

    # ---- ④ 把某道闸的输入面登记改错 ⇒ T2 + T8 红 ----
    def c4(dst):
        def f(b):
            b["registry"]["SW/tools/check_shutdown_semantics.py"]["faces"] = \
                ["board", "table", "doc"]
        _mut_page(dst, f)
        return "把 check_shutdown_semantics.py 的输入面登记改成含 board (源码实读不含)"

    # ---- ⑤ 删掉某道闸的输入面登记 ⇒ T2 + T8 红 ----
    def c5(dst):
        def f(b):
            b["registry"]["SW/tools/check_iss250_rknn_target_gate.py"].pop("faces", None)
        _mut_page(dst, f)
        return "把 check_iss250_rknn_target_gate.py 的输入面登记整条删掉"

    # ---- ⑥ 把「无真源依赖」闸数在册值改成 9 ⇒ T3 + T8 红 ----
    def c6(dst):
        def f(b):
            b["counts"]["doc_only_gate_count"] = 9
        _mut_page(dst, f)
        return "把「无真源依赖」闸数在册值改成 9 (实读 10) ⇒ T3 应当点名"

    # ---- ⑦ 把链上那道硬编位号闸从链里摘掉 ⇒ T4 转绿 (★证明 T4 的红来自「链上+硬编」这个组合★) ----
    def c7(dst):
        p = os.path.join(dst, GATE_CHECK_REL)
        txt = read_text(p)
        # ★★链上【两道】硬编位号闸都要摘掉 (★onepass_sw_sync 在 gate_check.py 里有【两处】挂载★) ★★
        olds = [
            ('(os.path.join(PROJ, "SW", "tools", "check_sw_ref_reachability.py"),\n'
             '     "SW 侧位号引用可达性闸 (ISS-318)", ()),'),
            ('(os.path.join(PROJ, "SW", "tools", "check_onepass_sw_sync.py"), '
             '"SW 侧板侧输入/合法改板闸 (ISS-298)", ()),'),
            ('(os.path.join(PROJ, "SW", "tools", "check_onepass_sw_sync.py"), '
             '"钉板闸⑨ SW 侧合法改板通道闸", ()),'),
        ]
        for old in olds:
            if old not in txt:
                raise AssertionError("链上那行的写法变了 ⇒ 用例本身坏了: %r" % (old[:70],))
            txt = txt.replace(old, "", 1)
        with open(p, "w", encoding="utf-8") as f:
            f.write(txt)
        return ("把链上两道硬编位号闸 (check_sw_ref_reachability.py + check_onepass_sw_sync.py 的两处挂载) "
                "从门禁链里摘掉 ⇒ T4 应当【转绿】(★反向自证: T4 的红确实来自「在链上 + 硬编位号」这个组合★)")

    # ---- ⑧ 把某道闸的改名面判定改成「不受影响」(自相矛盾) ⇒ T5 + T8 红 ----
    def c8(dst):
        def f(b):
            b["registry"]["SW/tools/check_sw_ref_reachability.py"]["rename"] = "不受影响"
        _mut_page(dst, f)
        return "把 v1 的改名面判定改成「不受影响」⇒ 它硬编 55 个位号 ⇒ 自相矛盾 ⇒ T5 红"

    # ---- ⑨ 在沙盒里给板追加一个字节 ⇒ T0 红 ----
    def c9(dst):
        p = os.path.join(dst, BOARD_REL)
        with open(p, "a", encoding="utf-8") as f:
            f.write("\n# ISS-411 selftest: 板改一个字节 (★只在沙盒★)\n")
        return "在沙盒里给板追加一个字节 ⇒ T0 (零扰动) 应当红"

    # ---- ⑩ 真相页机器块被删 ⇒ T5/T6/T8 红 (fail-closed) ----
    def c10(dst):
        p = os.path.join(dst, PAGE_REL)
        txt = read_text(p)
        seg = txt.split(BLOCK_BEGIN, 1)[1].split(BLOCK_END, 1)[0]
        with open(p, "w", encoding="utf-8") as f:
            f.write(txt.replace(seg, "\n(机器块被删了)\n", 1))
        return "把真相页机器块删掉 ⇒ T5/T6/T8 fail-closed 应当红"

    # ---- ⑪ 把一道闸从盘上删掉 ⇒ T1 + T6 红 ----
    def c11(dst):
        os.remove(os.path.join(dst, "SW/tools/check_rk3572_vccio_domain.py"))
        return "把 check_rk3572_vccio_domain.py 从盘上删掉 ⇒ T1(登记了但读不到) + T6 应当红"

    # ---- ⑫ 给沙盒里的本闸加一个网络 import ⇒ T7 红 (零外发自证) ----
    def c12(dst):
        p = os.path.join(dst, SELF_REL)
        with open(p, "a", encoding="utf-8") as f:
            f.write("\nimport smtplib\n")
        return "给沙盒里的本闸加一行 `import smtplib` ⇒ T7 (零外发自证) 应当红"

    # ---- ⑬ 把本闸挂进门禁链 ⇒ T7 红 (零挂链自证) ----
    def c13(dst):
        p = os.path.join(dst, GATE_CHECK_REL)
        txt = read_text(p)
        add = ('\nEXTRA_GATES.append((os.path.join(PROJ, "SW", "tools", '
               '"check_sw_mustchange_face_impact.py"), "ISS-411 probe", ()))\n')
        with open(p, "w", encoding="utf-8") as f:
            f.write(txt + add)
        return "把本闸挂进门禁链 ⇒ T7 (零挂链自证) 应当红"

    # ---- ⑭ 把页面登记册里一道闸整条删掉 ⇒ T1 + T8 红 (漏登记) ----
    def c14(dst):
        def f(b):
            b["registry"].pop("SW/tools/check_rk3572_vccio_domain.py", None)
        _mut_page(dst, f)
        return "把页面登记册里 check_rk3572_vccio_domain.py 整条删掉 ⇒ T1(漏登记) + T8 红"

    # ★★底噪: ★【T4 在任何沙盒里都是红的】(★链上那两道闸硬编位号⇒ 命门★) ★★
    #   ⇒ 每条用例的【预期红集合】必须【含 T4】(★除 c0 本身就是「只有 T4 红」·c7 把两道都摘掉才转绿★)
    cases.append((c1, "T1,T4,T8", None))
    cases.append((c2, "T1,T4", None))
    cases.append((c3, "T1,T3,T4", None))
    cases.append((c4, "T2,T4,T8", None))
    cases.append((c5, "T2,T4,T8", None))
    cases.append((c6, "T3,T4", None))
    cases.append((c7, "NONE", None))
    cases.append((c8, "T4,T5,T8", None))
    cases.append((c9, "T0,T4", None))
    cases.append((c10, "T1,T2,T3,T4,T5,T6,T8", None))
    cases.append((c11, "T1,T4,T6", None))
    cases.append((c12, "T4,T7", None))
    cases.append((c13, "T4,T7", None))
    cases.append((c14, "T1,T4,T8", None))

    npass = 0
    for idx, (fn, tgt, _d) in enumerate(cases, 1):
        dst = os.path.join(SBX_ROOT, "case%d" % idx)
        build_sandbox(dst)
        what = fn(dst)
        res = run_checks(dst)
        failed = sorted(cid for cid, v in res.items()
                        if cid != "_meta" and not v.get("ok"))
        want = [] if tgt == "NONE" else sorted(x for x in tgt.split(",") if x)
        ok = (failed == want)
        npass += 1 if ok else 0
        print("  用例 %d · 目标 %s · 红的集合 = %s · %s"
              % (idx, tgt, failed, "PASS" if ok else "FAIL"))
        print("        手法: %s" % what)
        if not ok:
            for cid, v in res.items():
                if cid == "_meta":
                    continue
                if not v.get("ok"):
                    for e in (v.get("errors") or [])[:4]:
                        print("        ⚠ %s: %s" % (cid, e))
        shutil.rmtree(dst, ignore_errors=True)
    print("-" * 92)
    print("反向用例: %d/%d 通过 (★每条都自证「红的集合 == {目标那一条}」★)" % (npass, len(cases)))
    if npass != len(cases):
        print("★有用例 FAIL ⇒ 本闸不可信 ⇒ rc=1★")
        return 1
    print("ALL TESTS PASS")
    return 0


# ===================================================================== 主流程
ORDER = ["T0", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"]


def main() -> int:
    ap = argparse.ArgumentParser(
        description="ISS-411 「板那一趟」SW 侧必改面影响面清账闸 (★零挂链★)")
    ap.add_argument("--root", default=PROJ, help="项目根 (默认本脚本上两级)")
    ap.add_argument("--selftest", action="store_true", help="跑反向用例")
    ap.add_argument("--json", action="store_true", help="机读输出")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    if args.selftest:
        return selftest()
    res = run_checks(root)
    npass = sum(1 for cid in ORDER if res[cid].get("ok"))
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0 if npass == len(ORDER) else 1
    print("=" * 92)
    print("ISS-411 · 「板那一趟」SW 侧【必改面 → 闸的判据失效】影响面清账闸")
    print("  根 = %s" % root)
    print("  真相页 = %s" % PAGE_REL)
    print("=" * 92)
    for cid in ORDER:
        v = res[cid]
        print("  [%s] %s" % ("PASS" if v.get("ok") else "FAIL", cid))
        for e in (v.get("errors") or []):
            print("        ★%s" % e)
    disk = res["_meta"]["disk"]
    chain = res["_meta"]["chain"]
    print("-" * 92)
    print("★盘上 SW 闸: %d 道 · 链内 %s 道"
          % (len(disk), (len(chain) if chain is not None else "读不到")))
    print("★硬编位号闸道数 (口径A): %s · 「无真源依赖」闸道数: %s"
          % (res["T1"].get("n_hard", "?"), res["T3"].get("n", "?")))
    if res["T4"].get("combo"):
        print("★★命门 (在链上 + 硬编位号): %s" % ", ".join(res["T4"]["combo"]))
    print("-" * 92)
    print("判据结果 %d/%d 通过, rc=%d" % (npass, len(ORDER), 0 if npass == len(ORDER) else 1))
    return 0 if npass == len(ORDER) else 1


if __name__ == "__main__":
    sys.exit(main())
