#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-404 · 「板只改一次」板侧闸【挂链覆盖率】机器闸 (G1~G7)
=================================================================================================
派活: state/dispatch_briefs/ISS-404_hw_gate_hook_coverage_audit.md (项目总工 main / moli · 2026-11-25)
执笔: 硬件总工 (hw-lead) · 2026-11-25

★★**本闸守的是什么**★★
  「板那一趟」(S1~S13) 的作业面文件 —— ★**预检清单 / 作业包 / 提交顺序页**★ —— 里【点名】了 19 道闸
  ⇒ ★**其中 13 道不在门禁链 `state/gate_check.py` 上**★ (★含投板前最命门的 `check_pcb_nets.py`
  与 `check_pcb_drc.py`★) ⇒ ★**全仓唯一的 fail-closed 自动链【不跑它们】⇒ 漏跑 = 没有任何机器会响**★
  ⇒ ★**板投出去才发现 ⇒ 板改第二次**★

★★**为什么既有闸盯不到这一格**★★
  `HW/check_onepass_preflight_coverage.py` (★已挂在钉板闸④★) 的 P3 查的是「**脚本在不在盘上**」,
  ★**不是「它在不在 fail-closed 链上」**★ ⇒ ★**本缺口至今零机器闸覆盖**★

★★**七条判据**★★
  G1 清单↔挂链 双向闭环 : ★**页面点名的每一道闸, 必须在【挂链表】或【人工签核台账】里二者其一**★
                          ★(fail-closed: 闸脚本缺失 / 语法跑不起来 ⇒ 一律算红★)
  G2 挂链表引用的脚本真实存在 : 挂链表里每一条的脚本路径必须在本机存在 (★防「幽灵闸」★)
  G3 分类台账自洽       : 仓内每道闸在分类台账里【有且只有一个归属】· ★**本闸脚本自己也要登记**★
                          (★防「自指漏洞」★) · 台账的「真漏挂名单」必须与盘面派生值逐字相同
  G4 板三证不动         : 板 / 网表 / 脚表 / BOM md5 与基线逐字相同
                          (★板 = 写死基线 · 网表/脚表/BOM = 走「落表台账为准」★)
  G5 零挂链 + 零外发自证 : 本闸名在 `state/gate_check.py` 里的行数必须与台账登记的挂链状态一致
                          (★「待 main 挂链」⇒ 期望 0 行 · 「已挂链」⇒ 期望 ≥1 行★) · `state/outbox/` 未动
  G6 证据分级          : 台账里每条结论都带 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`
                          + 每条都要写清「拦什么 / 拦不住会怎样」
  G7 零写板自证         : 板 md5 / mtime / size 三项与基线逐字相同

★★**自指悖论 (★本闸不自拍·交 main 拍★)**★★
  G1 要求「页面点名的闸都要在链上或台账里」⇒ ★**本闸自己也不在链上**★ ⇒ 逻辑上它也该被登记
  ⇒ 而登记它的动作 = 挂链 = ★**main 的机制地界**★ ⇒ ★**台账里「本闸自身」这一行写「待 main 挂链」**★
  ⇒ ★**main 若决定挂本闸: ① 台账 `self.hook_status` 改成「已挂链」 ② 把本闸加进 `state/gate_check.py`
  ⇒ 本闸的 G5 会自动从「期望 grep=0」翻成「期望 grep≥1」★★ (★闸脚本一个字节都不用改★)

退出码: 0 = 全过 · 1 = 有不通过项 (★★红的是现状, 不是闸故障★★) · 2 = 用法错

用法:
  python3 HW/check_onepass_gate_hook_coverage.py              # 主模式 (★今天必然 rc=1★)
  python3 HW/check_onepass_gate_hook_coverage.py --selftest   # 反向用例 (★末行 ALL TESTS PASS★)

★**自检用 env 覆盖** (★只在【沙盒根 ≠ 项目根】时生效 ⇒ 改不了真盘的判据★):
  GATE_HOOK_ROOT · GATE_HOOK_LEDGER · GATE_HOOK_GATE_CHECK · GATE_HOOK_PAGES ·
  GATE_HOOK_MANUAL · GATE_HOOK_OUTBOX · GATE_HOOK_BOARD_MD5
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

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

# ★★板 md5 基线 (★写死·与 HW/check_onepass_preflight_coverage.py 同一条口径★) ★★
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"

CAT_A = "A_已挂链"
CAT_B = "B_必挂但漏挂"
CAT_C = "C_一次性沙盒件"
CAT_D = "D_selftest辅助件"
CAT_E = "E_域内常驻闸"
CAT_SELF = "本闸自身"
VALID_CATS = (CAT_A, CAT_B, CAT_C, CAT_D, CAT_E, CAT_SELF)

EVIDENCE_TAGS = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")

DEFAULT_PAGES = (
    "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md",
    "HW/PCB/BOARD_ONEPASS_WORKPACKET.md",
    "HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md",
)
DEFAULT_LEDGER = "HW/PCB/BOARD_ONEPASS_GATE_HOOK_LEDGER.json"
DEFAULT_MANUAL = "HW/PCB/BOARD_ONEPASS_MANUAL_SIGNOFF_LEDGER.md"
DEFAULT_GATE_CHECK = "state/gate_check.py"
DEFAULT_OUTBOX = "state/outbox"
SELF_GATE = "HW/check_onepass_gate_hook_coverage.py"

_GATE_TOKEN_RE = re.compile(r"[A-Za-z0-9_./-]*check_[A-Za-z0-9_]*\.py")


# ==============================================================================
# 基础工具
# ==============================================================================
def md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def _rel_of(node) -> str:
    """★把 `os.path.join(PROJ, "HW", "x.py")` 这种 AST 节点还原成相对路径★"""
    if not isinstance(node, ast.Call):
        return ""
    parts = []
    for a in node.args:
        if isinstance(a, ast.Constant) and isinstance(a.value, str):
            parts.append(a.value)
        elif isinstance(a, ast.Attribute):
            parts.append(a.attr)
    return "/".join(p for p in parts if p != "PROJ")


def parse_chain(gate_check_path: str) -> dict:
    """★读门禁链 ⇒ {相对路径: [{table,label}, ...]} (★AST 读, 不执行·不 import★) ★

    ★**为什么用 AST 而不是 import**: import 会真的执行 `gate_check.py` 的模块级代码,
    且闸链随时会被 main 改 ⇒ ★**AST 读到的是「此刻盘上的链」, 不会过期**★ ★
    """
    src = read_text(gate_check_path)
    tree = ast.parse(src)
    chain: dict = {}
    for node in tree.body:
        if not (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)):
            continue
        name = node.targets[0].id
        if name in ("EXTRA_GATES", "PINNED_MD5_GATES"):
            for el in node.value.elts:
                rel = _rel_of(el.elts[0])
                if not rel:
                    continue
                try:
                    label = ast.literal_eval(el.elts[1])
                except Exception:  # noqa: BLE001
                    label = "?"
                chain.setdefault(rel, []).append({"table": name, "label": label})
        elif name == "HW_PINOUT_GATE":
            rel = _rel_of(node.value)
            if rel:
                chain.setdefault(rel, []).append(
                    {"table": "HW_PINOUT_GATE", "label": "HW pinout 真源闸"})
    return chain


def scan_gates(root: str, dirs=("HW", "MECH", "SW")) -> list:
    """★仓内闸脚本全量 (★递归·含 HW/tools · MECH/tools · SW/tools★) ★"""
    out = []
    for d in dirs:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for r, dirs_, files in os.walk(base):
            dirs_[:] = [x for x in dirs_ if x not in ("__pycache__", ".git")]
            for fn in files:
                if fn.startswith("check_") and fn.endswith(".py"):
                    out.append(os.path.relpath(os.path.join(r, fn), root))
    return sorted(out)


def _resolve_gate_token(root: str, tok: str):
    tok = tok.strip().lstrip("`").rstrip("`")
    if tok.startswith("./"):
        tok = tok[2:]
    cands = (tok, "HW/" + tok, "MECH/" + tok, "SW/" + tok, "state/" + tok,
             "SW/tools/" + tok, "MECH/tools/" + tok)
    for cand in cands:
        if os.path.exists(os.path.join(root, cand)):
            return cand
    return None


def page_named_gates(root: str, page_rel: str) -> tuple:
    """★从一份作业面文件里抽出它【点名】的闸 ⇒ (能解析到盘上文件的, 解析不到的) ★

    ★**两个都要返回**: ★**解析不到的也要报出来**★ ⇒ ★**页面点名了一个不存在的闸脚本 ⇒ fail-closed 红**
    (★不然「点名一个不存在的脚本」会被静悄悄吞掉 ⇒ 那正是 ISS-136 同款根因★) ★
    """
    p = os.path.join(root, page_rel)
    if not os.path.exists(p):
        return [], []
    found, missing = set(), set()
    for tok in set(_GATE_TOKEN_RE.findall(read_text(p))):
        r = _resolve_gate_token(root, tok)
        if r:
            found.add(r)
        else:
            missing.add(tok.strip().lstrip("`").rstrip("`"))
    return sorted(found), sorted(missing)


def parse_manual_ledger(root: str, manual_rel: str) -> set:
    """★人工签核台账里【已签核】的闸 ⇒ 集合 (★只认表格行·防正文误命中★) ★

    ★**为什么只认表格行**: 台账正文里会写「这些闸还没人跑」⇒ 正文里的闸名【不算签核】
    ⇒ ★**只认以 `|` 开头的表格行**★ ★
    """
    p = os.path.join(root, manual_rel)
    if not os.path.exists(p):
        return set()
    out = set()
    for line in read_text(p).split("\n"):
        if not line.lstrip().startswith("|"):
            continue
        for tok in set(_GATE_TOKEN_RE.findall(line)):
            r = _resolve_gate_token(root, tok)
            if r:
                out.add(r)
    return out


def compile_ok(path: str) -> bool:
    """★「跑不起来」的代理判定: 文件能不能被 Python 解析 (★语法层·不真跑·零副作用★) ★"""
    try:
        compile(read_text(path), path, "exec")
        return True
    except Exception:  # noqa: BLE001
        return False


def classify(gates: list, chain: dict, named_all: set) -> dict:
    """★分类台账的【规则派生】(★优先级不许换★): A > B > C > D > E ★"""
    out = {}
    for g in gates:
        base = os.path.basename(g)
        if g in chain:
            out[g] = CAT_A
        elif g in named_all:
            out[g] = CAT_B
        elif base.endswith("_sbx.py"):
            out[g] = CAT_C
        elif "selftest" in base:
            out[g] = CAT_D
        else:
            out[g] = CAT_E
    return out


# ==============================================================================
# 主判定
# ==============================================================================
def evaluate(root: str, ledger_path: str, gate_check_path: str, page_paths: list,
             manual_path: str, outbox_dir: str) -> tuple:
    """⇒ (全过?, 输出行列表) ★"""
    sandbox = os.path.realpath(root) != os.path.realpath(PROJ)
    blocks = []

    def blk(cid, title, ok, lines):
        nonlocal blocks
        blocks.append((cid, title, ok, lines))

    # ---------- 台账 ----------
    led = {}
    g3_lines = []
    g3_ok = True
    if not os.path.exists(ledger_path):
        g3_ok = False
        g3_lines.append("     ❌ ★分类台账不存在: %s ⇒ fail-closed "
                        "(★不许「查不到就算过」★)" % ledger_path)
    else:
        try:
            with open(ledger_path, encoding="utf-8") as f:
                led = json.load(f)
        except Exception as e:  # noqa: BLE001
            g3_ok = False
            g3_lines.append("     ❌ ★分类台账解析失败: %s ⇒ fail-closed" % e)

    # ---------- 链 / 仓内闸 / 页面点名 ----------
    chain = {}
    if not os.path.exists(gate_check_path):
        g1_bad = ["★门禁链脚本不存在: %s ⇒ fail-closed" % gate_check_path]
        chain = {}
    else:
        try:
            chain = parse_chain(gate_check_path)
            g1_bad = []
        except Exception as e:  # noqa: BLE001
            g1_bad = ["★门禁链解析失败: %s ⇒ fail-closed" % e]
            chain = {}

    gates = scan_gates(root)
    named_by_page = {}
    missing_by_page = {}
    for p in page_paths:
        named_by_page[p], missing_by_page[p] = page_named_gates(root, p)
    named_all = set()
    for v in named_by_page.values():
        named_all |= set(v)
    named_missing = set()
    for v in missing_by_page.values():
        named_missing |= set(v)
    manual_set = parse_manual_ledger(root, manual_path)
    derived = classify(gates, chain, named_all)
    # ★真漏挂 = 【既不在挂链表、也不在人工签核台账】的页面点名闸 (★人工签核过的就不算漏挂★)
    derived_B = set(g for g in named_all if g not in chain and g not in manual_set)

    # ============== G1 ==============
    g1_lines = []
    g1_ok = True
    for g in sorted(named_all):
        if g in chain or g in manual_set:
            continue
        pgs = [p for p in page_paths if g in named_by_page.get(p, [])]
        g1_ok = False
        g1_lines.append("     ❌ ★%s 点名页 %s · 既不在挂链表、也不在人工签核台账 ⇒ "
                        "★漏跑时没有任何机器会响★"
                        % (g, ",".join(os.path.basename(x) for x in pgs)))
    for g in sorted(named_all):
        p = os.path.join(root, g)
        if not os.path.exists(p):
            g1_ok = False
            g1_lines.append("     ❌ ★%s 脚本不存在 ⇒ fail-closed "
                            "(★不许「查不到就算过」★)" % g)
        elif not compile_ok(p):
            g1_ok = False
            g1_lines.append("     ❌ ★%s 脚本语法跑不起来 ⇒ fail-closed" % g)
    for tok in sorted(named_missing):
        g1_ok = False
        g1_lines.append("     ❌ ★页面点名的闸脚本在本机找不到: %s ⇒ fail-closed "
                        "(★不许「查不到就算过」★)" % tok)
    if g1_ok:
        g1_lines.append("     ✔ 页面点名的 %d 道闸全部在挂链表或人工签核台账里" % len(named_all))
    else:
        g1_lines.append("     ❌ ★%d 道页面点名的闸既不在挂链表、也不在人工签核台账 ⇒ "
                        "★「板那一趟」当天漏跑它们 = 没有任何机器会响★"
                        % len([g for g in named_all if g not in chain and g not in manual_set]))
    if manual_set:
        g1_lines.append("     ✔ 人工签核台账已登记 %d 道闸" % len(manual_set))
    else:
        g1_lines.append("     ℹ️ 人工签核台账 %s 不存在 ⇒ 「人工签核」那一路为空 "
                        "(★main 要不要另起页 = Q3★)" % manual_path)
    g1_lines.append("     ℹ️ 链上 %d 道闸 · 其中 %d 道被三页点名 · 三页点名共 %d 道"
                    % (len(chain), len([g for g in chain if g in named_all]), len(named_all)))
    blk("G1", "清单↔挂链 双向闭环 (★页面点名的闸必须在【挂链表】或【人工签核台账】★)",
        g1_ok, g1_lines)

    # ============== G2 ==============
    g2_lines = []
    g2_ok = True
    ghost = sorted(g for g in chain if not os.path.exists(os.path.join(root, g)))
    for g in ghost:
        g2_ok = False
        g2_lines.append("     ❌ ★挂链表引用了不存在的脚本: %s ⇒ 幽灵闸 (★链上那条必红·"
                        "但那是「跑不起来」不是「没挂」★)" % g)
    for g in sorted(chain):
        p = os.path.join(root, g)
        if os.path.exists(p) and not compile_ok(p):
            g2_ok = False
            g2_lines.append("     ❌ ★挂链表引用的脚本语法跑不起来: %s ⇒ fail-closed" % g)
    if g2_ok:
        g2_lines.append("     ✔ 挂链表 %d 条引用的脚本全部在本机存在且语法可跑" % len(chain))
    blk("G2", "挂链表引用的脚本真实存在 (★防「幽灵闸」★)", g2_ok, g2_lines)

    # ============== G3 ==============
    cls = led.get("classification") or {}
    if not cls:
        g3_ok = False
        g3_lines.append("     ❌ ★台账里没有 classification ⇒ fail-closed")
    else:
        lset, gset = set(cls), set(gates)
        if lset != gset:
            g3_ok = False
            g3_lines.append("     ❌ ★台账登记的闸集合 ≠ 仓内实际闸集合 (★差 %d 条·台账要更新★)"
                            % len(lset ^ gset))
            for g in sorted(gset - lset):
                g3_lines.append("        ❌ 仓内有 · 台账无: %s" % g)
            for g in sorted(lset - gset):
                g3_lines.append("        ❌ 台账有 · 仓内无: %s" % g)
        else:
            g3_lines.append("     ✔ 仓内 %d 道闸在台账里【有且只有一个归属】" % len(gset))
        bad_cat = sorted(g for g, e in cls.items()
                         if not isinstance(e, dict) or e.get("cat") not in VALID_CATS)
        for g in bad_cat:
            g3_ok = False
            g3_lines.append("     ❌ ★台账里 %s 的分类不合法 (★合法值: %s★)"
                            % (g, " / ".join(VALID_CATS)))
        fake_a = sorted(g for g, e in cls.items()
                        if isinstance(e, dict) and e.get("cat") == CAT_A and g not in chain)
        for g in fake_a:
            g3_ok = False
            g3_lines.append("     ❌ ★台账声明「已挂链」但链上没有: %s ⇒ 幽灵闸" % g)
        selfe = led.get("self") or {}
        sg = selfe.get("gate")
        if not sg:
            g3_ok = False
            g3_lines.append("     ❌ ★台账里没有「本闸自身」的登记 ⇒ 自指漏洞 "
                            "(★本闸必须登记自己★)")
        elif sg not in cls:
            g3_ok = False
            g3_lines.append("     ❌ ★台账的 self.gate=%s 不在 classification 里 ⇒ 登记不完整" % sg)
        elif cls[sg].get("cat") != CAT_SELF:
            g3_ok = False
            g3_lines.append("     ❌ ★台账里 self.gate=%s 的分类 = %r, 应当是 %r"
                            % (sg, cls[sg].get("cat"), CAT_SELF))
        else:
            g3_lines.append("     ✔ 本闸自身已登记 (hook_status=%s) ⇒ 自指漏洞已封"
                            % selfe.get("hook_status"))
    rows = led.get("must_hook_missing") or []
    mhm = set()
    for r in rows:
        g = (r or {}).get("gate")
        if g in mhm:
            g3_ok = False
            g3_lines.append("     ❌ ★台账真漏挂名单里有重复条目: %s" % g)
        mhm.add(g)
    if mhm != derived_B:
        g3_ok = False
        g3_lines.append("     ❌ ★台账的「真漏挂名单」≠ 盘面派生值 "
                        "(★台账过期 / 有新漏挂没登记★)")
        for g in sorted(derived_B - mhm):
            g3_lines.append("        ❌ 盘面派生有 · 台账无: %s" % g)
        for g in sorted(mhm - derived_B):
            g3_lines.append("        ❌ 台账有 · 盘面派生无 (★已挂链或已不被页面点名·"
                            "请同步台账★): %s" % g)
    else:
        g3_lines.append("     ✔ 真漏挂名单 %d 条与盘面派生值逐字相同" % len(mhm))
    for r in rows:
        g = (r or {}).get("gate")
        if g and not os.path.exists(os.path.join(root, g)):
            g3_ok = False
            g3_lines.append("     ❌ ★台账真漏挂名单里有一条脚本不存在: %s ⇒ fail-closed" % g)
    blk("G3", "分类台账自洽 (★每道闸有且只有一个归属 · 本闸自己也要登记★)", g3_ok, g3_lines)

    # ============== G4 ==============
    g4_lines = []
    g4_ok = True
    board_rel = (led.get("board_baseline") or {}).get("path") or "HW/PCB/demo_mainboard.kicad_pcb"
    board_path = os.path.join(root, board_rel)
    board_want = BOARD_MD5
    if sandbox:
        board_want = os.environ.get("GATE_HOOK_BOARD_MD5") or \
            (led.get("board_baseline") or {}).get("md5") or BOARD_MD5
    if not os.path.exists(board_path):
        g4_ok = False
        g4_lines.append("     ❌ ★板文件不存在: %s ⇒ fail-closed" % board_rel)
    else:
        cur = md5(board_path)
        if cur != board_want:
            g4_ok = False
            g4_lines.append("     ❌ ★板 md5 %s ≠ 基线 %s ⇒ 盘面被改过 (★零写板自证失败★)"
                            % (cur, board_want))
        else:
            g4_lines.append("     ✔ 板 md5 = %s (== 基线)" % cur)
    if not sandbox:
        led_board = (led.get("board_baseline") or {}).get("md5")
        if led_board and led_board != BOARD_MD5:
            g4_ok = False
            g4_lines.append("     ❌ ★台账里的板基线 %s ≠ 闸内写死基线 %s ⇒ "
                            "台账与闸的判决源不一致" % (led_board, BOARD_MD5))
    try:
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        import landing_md5  # noqa: E402
        for rel in ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv"):
            p = os.path.join(root, rel)
            if not os.path.exists(p):
                g4_ok = False
                g4_lines.append("     ❌ %s 不存在 ⇒ fail-closed" % rel)
                continue
            g_ok, msg = landing_md5.check_registered(root, rel, p, md5)
            if g_ok:
                g4_lines.append("     ✔ %s" % msg)
            else:
                g4_ok = False
                g4_lines.append("     ❌ %s" % msg)
    except Exception as e:  # noqa: BLE001
        g4_ok = False
        g4_lines.append("     ❌ ★落表台账口径取不到基线: %s ⇒ fail-closed" % e)
    blk("G4", "板三证不动 (★板 md5 / 网表 / 脚表 / BOM 与基线逐字相同★)", g4_ok, g4_lines)

    # ============== G5 ==============
    g5_lines = []
    g5_ok = True
    status = ((led.get("self") or {}).get("hook_status") or "").strip()
    src = read_text(gate_check_path) if os.path.exists(gate_check_path) else ""
    n_lines = sum(1 for ln in src.split("\n") if "check_onepass_gate_hook_coverage" in ln)
    if status == "待 main 挂链":
        if n_lines == 0:
            g5_lines.append("     ✔ 本闸名在 %s 里的行数 = 0 (★零挂链·台账登记状态 = 待 main 挂链★)"
                            % os.path.basename(gate_check_path))
        else:
            g5_ok = False
            g5_lines.append("     ❌ ★台账登记「待 main 挂链」但 %s 里已有 %d 行提到本闸 ⇒ "
                            "★台账与链不一致·请把台账 self.hook_status 改成「已挂链」★"
                            % (os.path.basename(gate_check_path), n_lines))
    elif status == "已挂链":
        if n_lines >= 1:
            g5_lines.append("     ✔ 本闸已挂链 (%s 里 %d 行) ⇒ 台账登记状态一致"
                            % (os.path.basename(gate_check_path), n_lines))
        else:
            g5_ok = False
            g5_lines.append("     ❌ ★台账登记「已挂链」但 %s 里找不到本闸 ⇒ fail-closed"
                            % os.path.basename(gate_check_path))
    else:
        g5_ok = False
        g5_lines.append("     ❌ ★台账 self.hook_status = %r, 合法值只有「待 main 挂链」/"
                        "「已挂链」⇒ fail-closed" % status)
    ob_base = led.get("outbox_baseline") or {}
    cur_ob = {}
    if os.path.isdir(outbox_dir):
        for r, dirs_, files in os.walk(outbox_dir):
            dirs_[:] = sorted(dirs_)
            for fn in sorted(files):
                p = os.path.join(r, fn)
                cur_ob[os.path.relpath(p, outbox_dir)] = {"md5": md5(p), "size": os.stat(p).st_size}
    if cur_ob != ob_base:
        g5_ok = False
        g5_lines.append("     ❌ ★state/outbox/ 与台账基线不一致 (★零外发自证失败·差 %d 条★)"
                        % len(set(cur_ob) ^ set(ob_base)))
        for k in sorted(set(cur_ob) - set(ob_base)):
            g5_lines.append("        ❌ 新增/多出: %s" % k)
        for k in sorted(set(ob_base) - set(cur_ob)):
            g5_lines.append("        ❌ 消失: %s" % k)
        for k in sorted(set(cur_ob) & set(ob_base)):
            if cur_ob[k] != ob_base[k]:
                g5_lines.append("        ❌ 变了: %s" % k)
    else:
        g5_lines.append("     ✔ state/outbox/ %d 件与台账基线逐字相同 (★零外发★)" % len(cur_ob))
    blk("G5", "零挂链 + 零外发自证", g5_ok, g5_lines)

    # ============== G6 ==============
    g6_lines = []
    g6_ok = True
    for r in rows + [led.get("self") or {}]:
        ev = (r or {}).get("evidence")
        if ev not in EVIDENCE_TAGS:
            g6_ok = False
            g6_lines.append("     ❌ ★%s 没标证据等级 (★合法: %s·evidence=%r★)"
                            % ((r or {}).get("gate") or "(self)",
                               " / ".join(EVIDENCE_TAGS), ev))
    for r in rows:
        if not str((r or {}).get("blocks", "")).strip() \
                or not str((r or {}).get("consequence", "")).strip():
            g6_ok = False
            g6_lines.append("     ❌ ★%s 没写「拦什么 / 拦不住会怎样」"
                            % ((r or {}).get("gate") or "?"))
    if g6_ok:
        g6_lines.append("     ✔ 台账 %d 条结论全部带证据等级标签 + 「拦什么/拦不住会怎样」"
                        % (len(rows) + 1))
    blk("G6", "证据分级 (★每条结论标 [官网]/[实测]/[媒体]/[推算]/[0数据]★)", g6_ok, g6_lines)

    # ============== G7 ==============
    g7_lines = []
    g7_ok = True
    bb = led.get("board_baseline") or {}
    if not os.path.exists(board_path):
        g7_ok = False
        g7_lines.append("     ❌ ★板文件不存在 ⇒ fail-closed")
    else:
        st = os.stat(board_path)
        cur_md5 = md5(board_path)
        want_md5 = bb.get("md5")
        want_size = bb.get("size")
        want_mtime = bb.get("mtime_ns")
        if want_md5 and cur_md5 != want_md5:
            g7_ok = False
            g7_lines.append("     ❌ ★板 md5 %s ≠ 基线 %s" % (cur_md5, want_md5))
        elif want_size is not None and st.st_size != want_size:
            g7_ok = False
            g7_lines.append("     ❌ ★板 size %d ≠ 基线 %d" % (st.st_size, want_size))
        elif want_mtime is not None and st.st_mtime_ns != want_mtime:
            g7_ok = False
            g7_lines.append("     ❌ ★板 mtime_ns %d ≠ 基线 %d" % (st.st_mtime_ns, want_mtime))
        else:
            g7_lines.append("     ✔ 板 md5 / mtime_ns / size 三项与基线逐字相同 "
                            "(md5=%s size=%d)" % (cur_md5, st.st_size))
    blk("G7", "零写板自证 (★md5 / mtime / size 三项与基线逐字相同★)", g7_ok, g7_lines)

    ok_all = all(b[2] for b in blocks)
    out = []
    for cid, title, ok, lines in blocks:
        out.append("  %s  %s %s" % ("OK " if ok else "FAIL", cid, title))
        out.extend(lines)
    return ok_all, out


# ==============================================================================
# 环境解析 (★沙盒覆盖只在 root ≠ PROJ 时生效★)
# ==============================================================================
def resolve_paths(args) -> dict:
    root = os.path.abspath(args.root or os.environ.get("GATE_HOOK_ROOT") or PROJ)
    sandbox = os.path.realpath(root) != os.path.realpath(PROJ)

    def pick(env_name, default_rel, arg=None):
        if arg:
            return arg if os.path.isabs(arg) else os.path.join(root, arg)
        v = os.environ.get(env_name)
        if v and sandbox:
            return v if os.path.isabs(v) else os.path.join(root, v)
        return os.path.join(root, default_rel)

    pages_env = os.environ.get("GATE_HOOK_PAGES") if sandbox else None
    pages = [x for x in pages_env.split(",") if x.strip()] if pages_env else list(DEFAULT_PAGES)
    return {
        "root": root,
        "ledger": pick("GATE_HOOK_LEDGER", DEFAULT_LEDGER, args.ledger),
        "gate_check": pick("GATE_HOOK_GATE_CHECK", DEFAULT_GATE_CHECK, args.gate_check),
        "pages": pages,
        "manual": pick("GATE_HOOK_MANUAL", DEFAULT_MANUAL, args.manual),
        "outbox": pick("GATE_HOOK_OUTBOX", DEFAULT_OUTBOX, args.outbox),
    }


# ==============================================================================
# --selftest (★沙盒在 tmp/iss404/ 下·不写系统 /tmp·不碰真件★)
# ==============================================================================
SANDBOX_GATE = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"ISS-404 沙盒占位闸 (★selftest 用·不是真闸★)\"\"\"
print("sandbox gate stub")
"""


def _w(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def build_sandbox(root: str, hooked=("HW/check_beta.py", "HW/check_gamma.py",
                                     "MECH/check_delta.py")) -> dict:
    """★搭一个自洽的沙盒仓 (★真件一个字节都不碰★) ★

    ★**基线设计**: 页面点名的三道闸 (check_beta / check_gamma / check_delta) 【全部挂在链上】
    ⇒ ★**基线全绿**★ ⇒ ★**反向用例每一条都是「把某处改坏 ⇒ 必须变红」**★ ★
    """
    shutil.rmtree(root, ignore_errors=True)
    gates = {
        "HW/check_alpha.py": SANDBOX_GATE,
        "HW/check_beta.py": SANDBOX_GATE,
        "HW/check_gamma.py": SANDBOX_GATE,
        "MECH/check_delta.py": SANDBOX_GATE,
        "SW/tools/check_epsilon.py": SANDBOX_GATE,
        "HW/check_zeta_sbx.py": SANDBOX_GATE,
        "HW/check_eta_selftest.py": SANDBOX_GATE,
        SELF_GATE: SANDBOX_GATE,
    }
    for rel, body in gates.items():
        _w(os.path.join(root, rel), body)
    # 门禁链 (★AST 读得到的形状★)
    chain = ["EXTRA_GATES = ["]
    for rel in hooked:
        chain.append('    (os.path.join(PROJ, "%s"), "沙盒闸 %s", ()),' % (rel, os.path.basename(rel)))
    chain.append("]")
    chain.append("PINNED_MD5_GATES = []")
    chain.append('HW_PINOUT_GATE = os.path.join(PROJ, "HW", "check_alpha.py")')
    _w(os.path.join(root, "state", "gate_check.py"), "\n".join(chain) + "\n")
    # 页面 (★点名 check_beta / check_gamma / check_delta★)
    _w(os.path.join(root, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md"),
       "# 沙盒预检清单\n判据: `python3 HW/check_beta.py` ⇒ rc=0\n")
    _w(os.path.join(root, "HW", "PCB", "BOARD_ONEPASS_WORKPACKET.md"),
       "# 沙盒作业包\n判据: `python3 HW/check_gamma.py`\n判据: `python3 MECH/check_delta.py`\n")
    _w(os.path.join(root, "HW", "PCB", "BOARD_ONEPASS_COMMIT_ORDER.md"),
       "# 沙盒提交顺序页\n判据: `python3 HW/check_beta.py`\n")
    # 板 + 三张表 + 落表台账
    _w(os.path.join(root, "HW", "PCB", "demo_mainboard.kicad_pcb"), "SANDBOX BOARD\n")
    board_md5 = md5(os.path.join(root, "HW", "PCB", "demo_mainboard.kicad_pcb"))
    for rel in ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv"):
        _w(os.path.join(root, rel), "SANDBOX %s\n" % rel)
    rows = []
    for rel in ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv"):
        rows.append("| `%s` | `%s` | `%s` | no |" % (rel, "0" * 32, md5(os.path.join(root, rel))))
    _w(os.path.join(root, "HW", "SCHEMATIC_LANDING_V1_LANDED.md"),
       "## ISS-999 · V 值拍板即落\n\n### §16.2 · 新旧 md5 前后对照\n\n"
       "| 文件 | 旧 md5 | 新 md5 | 变了? |\n|---|---|---|---|\n" + "\n".join(rows) + "\n")
    # outbox
    _w(os.path.join(root, "state", "outbox", "keep.md"), "sandbox outbox\n")
    ob = {}
    for r, _, files in os.walk(os.path.join(root, "state", "outbox")):
        for fn in files:
            p = os.path.join(r, fn)
            ob[os.path.relpath(p, os.path.join(root, "state", "outbox"))] = {
                "md5": md5(p), "size": os.stat(p).st_size}
    # 台账
    named = set()
    for pg in DEFAULT_PAGES:
        named |= set(page_named_gates(root, pg)[0])
    chain_map = parse_chain(os.path.join(root, "state", "gate_check.py"))
    gates_list = scan_gates(root)
    derived = classify(gates_list, chain_map, named)
    derived_B = sorted(g for g in named if g not in chain_map)
    cls = {}
    for g in gates_list:
        e = {"cat": derived[g]}
        if derived[g] == CAT_A:
            e["hook"] = [x["table"] for x in chain_map[g]]
        cls[g] = e
    cls[SELF_GATE] = {"cat": CAT_SELF, "hook": [], "note": "沙盒自闸"}
    bst = os.stat(os.path.join(root, "HW", "PCB", "demo_mainboard.kicad_pcb"))
    led = {
        "ledger_id": "沙盒台账", "version": "1.0", "issue": "ISS-404",
        "evidence_tags_allowed": list(EVIDENCE_TAGS),
        "self": {"gate": SELF_GATE, "cat": CAT_SELF, "hook_status": "待 main 挂链",
                 "evidence": "[实测]", "note": "沙盒"},
        "board_baseline": {"path": "HW/PCB/demo_mainboard.kicad_pcb", "md5": board_md5,
                           "size": bst.st_size, "mtime_ns": bst.st_mtime_ns,
                           "evidence": "[实测]"},
        "outbox_baseline": ob,
        "classification": cls,
        "must_hook_missing": [
            {"gate": g, "cat": CAT_B, "severity": "沙盒", "named_by": ["sandbox"],
             "blocks": "沙盒", "consequence": "沙盒", "current_reading": "rc=?",
             "evidence": "[实测]", "recommended_batch": "B1"}
            for g in derived_B
        ],
    }
    lp = os.path.join(root, DEFAULT_LEDGER)
    _w(lp, json.dumps(led, ensure_ascii=False, indent=1))
    return {"ledger": lp, "board_md5": board_md5}


def run_selftest() -> int:
    base = os.path.join(PROJ, "tmp", "iss404")
    os.makedirs(base, exist_ok=True)
    sb = os.path.join(base, "selftest_%d" % os.getpid())
    cases = []

    def run(root):
        p = resolve_paths(argparse.Namespace(root=root, ledger=None, gate_check=None,
                                             manual=None, outbox=None))
        return evaluate(p["root"], p["ledger"], p["gate_check"], p["pages"],
                        p["manual"], p["outbox"])

    def failed(lines, cid):
        """★某条判据是否判红 (★看该判据自己的头行 verdict + 它的 ❌ 行★) ★"""
        for l in lines:
            s = l.strip()
            if s.startswith(("OK ", "FAIL")) and s.split()[1] == cid:
                return s.startswith("FAIL")
        return False

    def load_led():
        with open(os.path.join(sb, DEFAULT_LEDGER), encoding="utf-8") as f:
            return json.load(f)

    def save_led(d):
        _w(os.path.join(sb, DEFAULT_LEDGER), json.dumps(d, ensure_ascii=False, indent=1))

    ALL3 = ("HW/check_beta.py", "HW/check_gamma.py", "MECH/check_delta.py")
    try:
        # ---------- 正向 ----------
        build_sandbox(sb, hooked=ALL3)
        ok, lines = run(sb)
        cases.append(("★正向: 沙盒基线 (页面点名的三道闸全在挂链表里) ⇒ 全绿 rc=0", ok is True,
                      "★自证改动★: 沙盒 %s · 三页点名的 check_beta / check_gamma / check_delta 全挂链"
                      % sb))
        if not ok:
            for l in lines:
                print("       ", l)

        # ---------- 反向 1: 把页面点名的一道闸从链里摘掉 ⇒ G1 红 ----------
        build_sandbox(sb, hooked=("HW/check_gamma.py", "MECH/check_delta.py"))
        ok, lines = run(sb)
        cases.append(("① 页面点名的 check_beta.py 不在挂链表 ⇒ G1 红",
                      failed(lines, "G1"),
                      "★自证改动★: 沙盒 gate_check.py 的 EXTRA_GATES 去掉 check_beta.py"))

        # ---------- 反向 2: 挂链表写一个不存在的脚本 ⇒ G2 红 ----------
        build_sandbox(sb, hooked=ALL3)
        gc = os.path.join(sb, "state", "gate_check.py")
        t = read_text(gc).replace('"HW/check_beta.py"), "沙盒闸 check_beta.py"',
                                  '"HW/check_ghost_missing.py"), "幽灵闸"')
        _w(gc, t)
        ok, lines = run(sb)
        cases.append(("② 挂链表里写一个不存在的脚本 ⇒ G2 红 (★幽灵闸★)",
                      failed(lines, "G2"),
                      "★自证改动★: 沙盒 gate_check.py 指向 check_ghost_missing.py (盘上无此文件)"))

        # ---------- 反向 3: 台账漏登记一道闸 ⇒ G3 红 ----------
        build_sandbox(sb, hooked=ALL3)
        d = load_led()
        d["classification"].pop("MECH/check_delta.py")
        save_led(d)
        ok, lines = run(sb)
        cases.append(("③ 台账漏登记一道闸 ⇒ G3 红 (★仓内每道闸必须有且只有一个归属★)",
                      failed(lines, "G3"),
                      "★自证改动★: 台账 classification 删掉 MECH/check_delta.py"))

        # ---------- 反向 4: 台账声明「已挂链」但链上没有 ⇒ G3 红 (幽灵闸) ----------
        build_sandbox(sb, hooked=ALL3)
        d = load_led()
        d["classification"]["HW/check_eta_selftest.py"]["cat"] = CAT_A
        save_led(d)
        ok, lines = run(sb)
        cases.append(("④ 台账把没挂链的闸声明成「已挂链」⇒ G3 红 (★幽灵闸★)",
                      failed(lines, "G3"),
                      "★自证改动★: 台账里 HW/check_eta_selftest.py 的 cat 改成 A_已挂链 (但链上没有)"))

        # ---------- 反向 5: 台账真漏挂名单多一条 ⇒ G3 红 ----------
        build_sandbox(sb, hooked=ALL3)
        d = load_led()
        d["must_hook_missing"].append({"gate": "HW/check_alpha.py", "cat": CAT_B,
                                        "blocks": "沙盒", "consequence": "沙盒",
                                        "evidence": "[实测]", "current_reading": "rc=?"})
        save_led(d)
        ok, lines = run(sb)
        cases.append(("⑤ 台账真漏挂名单多一条 (盘面没有) ⇒ G3 红 (★名单必须与盘面派生值逐字相同★)",
                      failed(lines, "G3"),
                      "★自证改动★: 台账 must_hook_missing 多塞 HW/check_alpha.py"))

        # ---------- 反向 6: 台账删掉自闸登记 ⇒ G3 红 (防自指漏洞) ----------
        build_sandbox(sb, hooked=ALL3)
        d = load_led()
        d["self"] = {}
        save_led(d)
        ok, lines = run(sb)
        cases.append(("⑥ 台账删掉「本闸自身」的登记 ⇒ G3 红 (★防自指漏洞★)",
                      failed(lines, "G3"),
                      "★自证改动★: 台账 self 段清空"))

        # ---------- 反向 7: 板被改一个字节 ⇒ G4 红 + G7 红 ----------
        build_sandbox(sb, hooked=ALL3)
        bp = os.path.join(sb, "HW", "PCB", "demo_mainboard.kicad_pcb")
        _w(bp, read_text(bp) + "; injected\n")
        ok, lines = run(sb)
        cases.append(("⑦ 板被改一个字节 ⇒ G4 红 且 G7 红 (★零写板自证★)",
                      failed(lines, "G4") and failed(lines, "G7"),
                      "★自证改动★: 沙盒板文件尾部加一行"))

        # ---------- 反向 8: 网表被改 ⇒ G4 红 (落表台账口径) ----------
        build_sandbox(sb, hooked=ALL3)
        np_ = os.path.join(sb, "HW", "netlist_v1.csv")
        _w(np_, read_text(np_) + "injected\n")
        ok, lines = run(sb)
        cases.append(("⑧ 网表被改一个字节 ⇒ G4 红 (★走落表台账口径·不是写死基线★)",
                      failed(lines, "G4"),
                      "★自证改动★: 沙盒 HW/netlist_v1.csv 尾部加一行"))

        # ---------- 反向 9: outbox 多一个文件 ⇒ G5 红 (零外发) ----------
        build_sandbox(sb, hooked=ALL3)
        _w(os.path.join(sb, "state", "outbox", "smuggled.md"), "smuggled\n")
        ok, lines = run(sb)
        cases.append(("⑨ state/outbox/ 多一个文件 ⇒ G5 红 (★零外发自证★)",
                      failed(lines, "G5"),
                      "★自证改动★: 沙盒 outbox 里塞 smuggled.md"))

        # ---------- 反向 10: 挂链了但台账仍写「待 main 挂链」⇒ G5 红 (自指悖论的机制) ----------
        build_sandbox(sb, hooked=ALL3)
        gc = os.path.join(sb, "state", "gate_check.py")
        t = read_text(gc).replace("EXTRA_GATES = [",
                                   'EXTRA_GATES = [\n    (os.path.join(PROJ, "HW", '
                                   '"check_onepass_gate_hook_coverage.py"), "本闸自己", ()),')
        _w(gc, t)
        ok, lines = run(sb)
        cases.append(("⑩ 本闸被挂进链但台账仍写「待 main 挂链」⇒ G5 红 (★自指悖论的可翻转机制★)",
                      failed(lines, "G5"),
                      "★自证改动★: 沙盒 gate_check.py 把本闸挂进 EXTRA_GATES, 台账不动"))

        # ---------- 反向 11: 某条结论缺证据等级 ⇒ G6 红 ----------
        build_sandbox(sb, hooked=("HW/check_gamma.py", "MECH/check_delta.py"))
        d = load_led()
        d["must_hook_missing"][0].pop("evidence", None)
        save_led(d)
        ok, lines = run(sb)
        cases.append(("⑪ 台账某条结论缺证据等级标签 ⇒ G6 红",
                      failed(lines, "G6"),
                      "★自证改动★: 台账 must_hook_missing[0] 删掉 evidence"))

        # ---------- 反向 12: 页面点名一个不存在的脚本 ⇒ G1 红 (fail-closed) ----------
        build_sandbox(sb, hooked=ALL3)
        pg = os.path.join(sb, "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")
        _w(pg, "# 沙盒预检清单\n判据: `python3 HW/check_not_exist_zzz.py` ⇒ rc=0\n")
        ok, lines = run(sb)
        cases.append(("⑫ 页面点名一个不存在的脚本 ⇒ G1 红 (★fail-closed·不许「查不到就算过」★)",
                      failed(lines, "G1"),
                      "★自证改动★: 沙盒预检清单点名 HW/check_not_exist_zzz.py"))

        # ---------- 反向 13: 人工签核台账登记 ⇒ G1 转绿 (台账那一路是真的能救的) ----------
        build_sandbox(sb, hooked=("HW/check_gamma.py", "MECH/check_delta.py"))
        _w(os.path.join(sb, DEFAULT_MANUAL),
           "# 沙盒人工签核台账\n\n| 闸 | 谁跑 | 读数 | 日期 |\n|---|---|---|---|\n"
           "| `HW/check_beta.py` | hw-lead | rc=0 | 2026-11-25 |\n")
        ok, lines = run(sb)
        cases.append(("⑬ 人工签核台账登记了 check_beta.py ⇒ G1 转绿 (★台账那一路有效★)",
                      (not failed(lines, "G1")) and failed(lines, "G3"),
                      "★自证改动★: 沙盒新建人工签核台账页并登记 check_beta.py "
                      "(★注意: 台账真漏挂名单没同步 ⇒ G3 仍红·这是设计内的双写纪律★)"))
    finally:
        shutil.rmtree(sb, ignore_errors=True)

    print("=" * 78)
    print("  ISS-404 · 反向用例 (★每条都自证「真的改到了目标」 ★)")
    print("=" * 78)
    bad = 0
    for item in cases:
        name, caught = item[0], item[1]
        proof = item[2] if len(item) > 2 else None
        mark = "✔" if caught else "✘"
        if not caught:
            bad += 1
        print("  %s  %s" % (mark, name))
        if proof:
            print("       %s" % proof)
    print("-" * 78)
    print("  反向用例 %d/%d 通过 (★正向 %d 条 + 反向 %d 条★)"
          % (len(cases) - bad, len(cases), 1, len(cases) - 1))
    if bad:
        print("  ❌ 有反向用例没抓到 ⇒ 闸不是判据 (或用例本身写错了)")
        return 1
    print("  ✅ 反向用例全抓到 ⇒ 判据真在被读 (★不是把红灯调没 ★)")
    print("ALL TESTS PASS")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=None)
    ap.add_argument("--ledger", default=None)
    ap.add_argument("--gate-check", dest="gate_check", default=None)
    ap.add_argument("--manual", default=None)
    ap.add_argument("--outbox", default=None)
    args = ap.parse_args()

    if args.selftest:
        return run_selftest()

    p = resolve_paths(args)
    print("=" * 78)
    print("  ISS-404 · 板侧闸【挂链覆盖率】闸 (★G1 闭环 / G2 幽灵闸 / G3 台账自洽 / "
          "G4 板三证 / G5 零挂链+零外发 / G6 证据分级 / G7 零写板★)")
    print("  ★红的是现状 (★页面点名的闸没挂在链上★), 不是闸故障 ★")
    print("=" * 78)
    ok, lines = evaluate(p["root"], p["ledger"], p["gate_check"], p["pages"],
                         p["manual"], p["outbox"])
    for l in lines:
        print(l)
    print("-" * 78)
    if ok:
        print("  ✅ rc=0: ★★页面点名的闸全在挂链表或人工签核台账里, 台账自洽, 板三证未动 ★★")
        return 0
    print("  ❌ rc=1: ★★有页面点名的闸既不在挂链表、也不在人工签核台账 ★★")
    print("             ⇒ ★「板那一趟」当天, 那几道闸漏跑 = 没有任何机器会响 ★★")
    return 1


if __name__ == "__main__":
    sys.exit(main())
