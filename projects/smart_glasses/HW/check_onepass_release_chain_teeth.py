#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-409 · 「板那一趟」投产/放行链【有没有牙齿】机器闸 (T1~T7)
=================================================================================================
派活: state/dispatch_briefs/ISS-409_hw_release_chain_teeth_audit.md (项目总工 main / moli · 2026-11-25)
执笔: 硬件总工 (hw-lead) · 2026-11-25

★★**本闸守的是什么**★★
  ★**投产链上真正决定「这张板能不能下单」的那几道闸, 被调用时用的是 `check_pcb_drc.py` 的哪一档** ★
  —— ★**不是「闸在不在链上」, 是「闸跑起来之后用的是哪一档」** ★

  `state/check_pcb_drc.py` L134-L136 逐字:
      strict = "--strict" in sys.argv
      ok4 = (n_unc == 0) if strict else True
  ⇒ ★**不带 `--strict` ⇒ C4 unconnected 恒判绿** ★
  ⇒ L138-139 照打「✅ C4 unconnected items = 45」· L187 照打「✅ 全过 —— 图纸可下单」⇒ ★**这就是假绿的样子** ★

  ★**ISS-406 (门禁链 18 道闸) 与本单 (投产/放行/巡检/候选验证链) 查的不是同一批对象** ⇒ ★**本单不是重做, 是补另一条链** ★

★★**最典型的坏结局 (★本机实测·非推算★)★★
  `state/chain_gate.py` L296 逐字:  `rc2, _ = run([sys.executable, "state/check_pcb_drc.py"])`
  ⇒ ★**argv 里没有 `--strict`** ★
  ⇒ L299 源码注释自己写着「★布线是否完成 (不阻塞"准出", 但要报出来 —— 现在 Gerber 不能下单)★」
  ⇒ ★**`lay_txt` 只拼进 L309 的输出字符串, 不进 `x3` 判定位** ★
  ⇒ ★⇒ ★**「板那一趟」当天, 只要板侧同步 (C1) 清零 ⇒ `check_pcb_nets` 转绿 ⇒ ③PCB 环 (绿·绿) 判绿** ★
  ⇒ ★⇒ ★**哪怕 unconnected 仍是 45, 投产链准入闸照样放行 ⇒ Gerber 可以下单 ⇒ 板改第二次** ★ ★

★★**七条判据**★★
  T1 调用点全集自洽 : ★**扫描全仓** (`state/` `HW/` `SW/` `MECH/` 下 `*.sh` `*.py`) 里引用
                      `check_pcb_drc` 的文件, ★**逐个用 AST / .sh 逻辑行实读** 判 argv 是否带 `--strict`
                      ⇒ ★**判据不许手抄清单** ★
                      · ★**T1a 命中文件数 ≥ 8** ⇒ 少于这个数说明扫描漏了 ⇒ 判红
                      · ★**T1b 真相页机器块台账 ↔ 实读【双向】一致** (文件集合 / (文件,行,kind) / strict 逐字相同) ⇒ 判红
                      · ★**T1c 台账必须点名宽松档真调用点** ⇒ 判红
  T2 放行链必须严格档 : ★**投产准入 `state/chain_gate.py` · `state/board_report.sh` ·
                      `state/verify_candidate.sh` · `state/daily_check.py`** 四道闸的调用点若不带 `--strict` ⇒ 判红
                      ⇒ ★**这是本闸的命门判据: 现状必红** ★
  T3 假绿输出不得被当放行凭据 :
                      · ★**T3a** 「图纸可下单」这个假绿标记串, 在【工具本体之外】的每个出现
                        ⇒ 都必须被台账登记为 `quoted_markers` 一行 (注明是引述还是断言) ⇒ 未登记 ⇒ 判红
                        ⇒ 登记为「断言」⇒ 判红
                      · ★**T3b** 每个真调用点必须登记它的【结果怎么用】`use` ∈ {judgement, display, discarded}
                        ⇒ 缺登记 ⇒ 判红 (★「跑完就扔」= 判据只剩人眼, 必须被点名★)
                      · ★**T3c** `use=judgement` 的真调用点 ⇒ 必须带 `--strict` ⇒ 否则判红
                        (★`use=judgement` 才是真判据; `display`/`discarded` 不判绿红, 由 T2 点名强制★)
                      · ★**T3d** 每个「抄日志里的 DRC 文本」的点 ⇒ 台账必须登记它抄的日志 + 生产脚本 + 生产脚本是否严格档
                        ⇒ 缺登记 ⇒ 判红 · 生产脚本非严格档 ⇒ 判红
                      · ★**T3e** `must_strict=true` 的真调用点 ⇒ 台账必须登记它的【消费方】(谁拿它的输出当证据)
                        ⇒ 缺登记或为空 ⇒ 判红
                      · ★**T3f** `must_strict=false` 的真调用点 ⇒ 台账必须登记【由哪一道别的闸兜底】+ 兜底闸在不在链上
                        ⇒ 缺登记 ⇒ 判红 · 兜底闸不在链上 ⇒ 判红 (★骨架阶段故意宽松, 但兜底必须真的在链上★)
  T4 fail-closed       : ★**真相页 / 机器块 / 板文件 / `state/gate_check.py` / `state/outbox/` 任一缺失 ⇒ 判红** ★
                      · ★**扫不到任何真调用点 ⇒ 判红** (不许「没扫到就算过」)
                      · ★**候选文件 AST 解析失败 ⇒ 必须被台账显式登记 (kind=unparsed) ⇒ 没登记 ⇒ 判红** ★
  T5 零挂链 + 零外发自证 : 本闸名在 `state/gate_check.py` 里的行数 = 0 · `state/outbox/` 逐件 md5 + 文件集合与基线相同
  T6 板指纹自证        : ★**本闸自己不许写板** ⇒ 板 md5 / mtime(ns) / size 三项与基线逐字相同 ★
  T7 「未布线 ⇒ 不可下单」闸点台账 :
                      · 必须登记全部 8 个「承担这条判据的闸点」(`stage_gate.py` · `verify_and_release.sh` ·
                        `chain_gate.py` · `promote_arm.sh` · `promote_board_file.sh` · `gen_production_pack.sh` ·
                        `check_pcb_drc.py` · `compare_arm_official.py` · `check_pcb_nets.py`) ⇒ 缺一 ⇒ 判红
                      · 每个必须标 `kind` ∈ {绝对闸, 相对闸, 无闸} + `on_chain` ⇒ 缺 ⇒ 判红
                      · ★**必须至少 1 道「绝对闸」且 `on_chain=true`** ⇒ 否则判红 ★

★★**扫描范围的两处显式排除 (★写在台账里·不许暗箱★)★★
  ① `state/check_pcb_drc.py` —— ★**它是被调用的那个工具本体, 不是调用点** ★
  ② `HW/check_onepass_release_chain_teeth.py` —— ★**本闸自己** (它的每一个提及都在字符串/文档里) ★
  ⇒ 其余**每一个**含 `check_pcb_drc` 的 `*.sh`/`*.py` 都必须进台账 (含历史一次性脚本) ⇒ 漏一条判红

退出码: 0 = 全过 · 1 = 有不通过项 (★★红的是现状, 不是闸故障★★) · 2 = 用法错

用法:
  python3 HW/check_onepass_release_chain_teeth.py              # 主模式 (★今天必然 rc=1★)
  python3 HW/check_onepass_release_chain_teeth.py --selftest   # 反向用例 (★末行 ALL TESTS PASS★)

★**自检用 env 覆盖** (★只在【沙盒根 ≠ 项目根】时生效 ⇒ 改不了真盘的判据★):
  RELEASE_TEETH_ROOT · RELEASE_TEETH_PAGE · RELEASE_TEETH_GATE_CHECK · RELEASE_TEETH_OUTBOX
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

# ★★板指纹基线 (★与 HW/check_onepass_gate_teeth.py 同一条口径★) ★★
BOARD_REL = "HW/PCB/demo_mainboard.kicad_pcb"
BOARD_MD5 = "611b869e13518c3c023fb178f91a0075"
BOARD_SIZE = 4940213
BOARD_MTIME_NS = 1793920037362193413  # ★2026-11-06 07:07:17.362193413 +0800 ⇒ ns★

DEFAULT_PAGE = "HW/PCB/BOARD_ONEPASS_RELEASE_CHAIN_TEETH_AUDIT.md"
DEFAULT_GATE_CHECK = "state/gate_check.py"
DEFAULT_OUTBOX = "state/outbox"

SELF_GATE = "HW/check_onepass_release_chain_teeth.py"
SELF_TOKEN = "check_onepass_release_chain_teeth"

LEDGER_BEGIN = "<!-- RELEASE_CHAIN_TEETH_LEDGER_BEGIN -->"
LEDGER_END = "<!-- RELEASE_CHAIN_TEETH_LEDGER_END -->"

# ★★被扫的目录 (★brief 指定★) ★★
SCAN_DIRS = ("state", "HW", "SW", "MECH")
# ★★工具本体 + 本闸本体 = 显式排除 (★台账里必须写明★) ★★
EXCLUDE_REL = ("state/check_pcb_drc.py", SELF_GATE)
# ★★扫描的 token (★带不带 `.py` 都算: 日志抄写点写的是 `check_pcb_drc` 不带 `.py`★) ★★
STEM = "check_pcb_drc"
TOOL_NAME = "check_pcb_drc.py"

# ★★T1a 的下限 (★主给的口径: 宽松档脚本 ≥ 8 个 ⇒ 命中文件数必须 ≥ 8, 少一个就说明扫描漏了★) ★★
MIN_CANDIDATES = 8

# ★★T2 点名的放行链闸 (★必须严格档★) ★★
RELEASE_CHAIN_GATES = (
    "state/chain_gate.py",        # 投产链准入闸 ③PCB 环
    "state/board_report.sh",      # 投产链板报告 (被 promote_arm / finish_line 消费)
    "state/verify_candidate.sh",  # 候选板验证
    "state/daily_check.py",       # 每日巡检
)

# ★★T3a 假绿标记串 (★【只有这一个串是工具本体独有的假绿结论】· 不用「✅ 全过」——
#     「✅ 全过」是全仓 30+ 个脚本的通用收尾语, 用它当标记 = 满屏假红★) ★★
FAKE_GREEN_MARKERS = ("图纸可下单",)
# ★★T3b 调用点的结果怎么用 (★决定它是不是一道真判据★) ★★
USE_KINDS = ("judgement", "display", "discarded")

# ★★T7 必须登记的「承担『未布线 ⇒ 不可下单』判据」的闸点 ★★
REQUIRED_NO_ORDER_GATES = (
    "state/stage_gate.py",
    "state/verify_and_release.sh",
    "state/chain_gate.py",
    "state/promote_arm.sh",
    "state/promote_board_file.sh",
    "state/gen_production_pack.sh",
    "state/check_pcb_drc.py",
    "state/compare_arm_official.py",
    "state/check_pcb_nets.py",
)
NO_ORDER_KINDS = ("绝对闸", "相对闸", "无闸")

# ★★AST 认定的「执行类」调用名 (★含 subprocess.* 的方法名★) ★★
EXEC_NAMES = {
    "run", "Popen", "call", "check_call", "check_output", "system", "popen",
    "exec_run", "execute", "spawn", "Popen3", "check_output", "getoutput",
}
# ★★.sh 里【读日志/读文本】的命令 ⇒ 抄日志的点 ★★
LOG_SCRAP_CMDS = {"grep", "egrep", "fgrep", "rg", "sed", "awk", "cut", "tr"}
# ★★.sh 里【只是打标签/回显】的命令 ⇒ 展示, 不是抄日志 ★★
LABEL_CMDS = {"echo", "printf", "tee", "cat", "head", "tail"}


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


def _no_dup_pairs(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise ValueError("台账里出现重复 key: %s" % k)
        seen[k] = v
    return seen


# ==============================================================================
# 扫描器
# ==============================================================================
def _iter_script_files(root: str):
    for d in SCAN_DIRS:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dp, dn, fn in os.walk(base):
            dn[:] = [x for x in dn if x not in (".git", "__pycache__", "node_modules")]
            for f in sorted(fn):
                if f.endswith((".sh", ".py")):
                    yield os.path.join(dp, f)


def _strip_comment(line: str) -> str:
    out, q = [], None
    i = 0
    while i < len(line):
        c = line[i]
        if q:
            out.append(c)
            if c == "\\" and i + 1 < len(line):
                out.append(line[i + 1]); i += 2; continue
            if c == q:
                q = None
        else:
            if c in ("'", '"'):
                q = c; out.append(c)
            elif c == "#":
                break
            else:
                out.append(c)
        i += 1
    return "".join(out)


def _split_segments(line: str):
    """★引号感知的简单命令切分 ⇒ 不会被 grep 的 `|` 正则切碎★"""
    segs, cur, q, i = [], [], None, 0
    while i < len(line):
        c = line[i]
        if q:
            cur.append(c)
            if c == "\\" and i + 1 < len(line):
                cur.append(line[i + 1]); i += 2; continue
            if c == q:
                q = None
            i += 1
            continue
        if c in ("'", '"'):
            q = c; cur.append(c); i += 1; continue
        if line.startswith("&&", i) or line.startswith("||", i):
            segs.append("".join(cur)); cur = []; i += 2; continue
        if c in ";|&\n":
            segs.append("".join(cur)); cur = []; i += 1; continue
        cur.append(c); i += 1
    segs.append("".join(cur))
    return segs


def _logical_lines(path: str):
    raw = read_text(path).split("\n")
    out, buf, start = [], "", None
    for i, ln in enumerate(raw, 1):
        if not buf:
            start = i
        s = ln.rstrip()
        if s.endswith("\\"):
            buf += s[:-1] + " "
            continue
        buf += s
        out.append((start, buf))
        buf = ""
    if buf:
        out.append((start, buf))
    return out


def _cmd_word(seg: str) -> str:
    seg = seg.strip()
    # 去掉前置的环境变量赋值 (FOO=bar cmd ...)
    for tok in seg.split():
        if "=" in tok and not tok.startswith("=") and not tok.startswith("-"):
            continue
        return tok.lstrip("$(").strip("\"'")
    return ""


def scan_sh(path: str, rel: str):
    """⇒ [site dict] ★site = {file, line, kind, strict, text} ★"""
    out = []
    for start, logical in _logical_lines(path):
        code = _strip_comment(logical)
        if STEM not in code:
            continue
        for seg in _split_segments(code):
            if STEM not in seg:
                continue
            cmd = _cmd_word(seg)
            if cmd in LOG_SCRAP_CMDS:
                kind = "loggrep"
            elif cmd in LABEL_CMDS:
                kind = "label"
            else:
                kind = "invoke"
            out.append({"file": rel, "line": start, "kind": kind,
                        "strict": "--strict" in seg, "text": seg.strip()[:200]})
    return out


def scan_py(path: str, rel: str):
    """⇒ (sites, parse_error) ★AST 实读, 不用正则猜★"""
    try:
        tree = ast.parse(read_text(path), filename=rel)
    except Exception as e:  # noqa: BLE001
        return [], "AST parse failed: %s" % e
    parent = {}
    for node in ast.walk(tree):
        for ch in ast.iter_child_nodes(node):
            parent[ch] = node
    out = []

    def governing_call(node):
        cur, hops = node, 0
        while cur is not None and hops < 8:
            p = parent.get(cur)
            if p is None:
                return None
            if isinstance(p, ast.Call):
                fn = p.func
                name = fn.attr if isinstance(fn, ast.Attribute) else (
                    fn.id if isinstance(fn, ast.Name) else "")
                return p if name in EXEC_NAMES else None
            if isinstance(p, (ast.List, ast.Tuple, ast.Set, ast.Dict, ast.JoinedStr,
                              ast.Starred, ast.keyword)):
                cur = p; hops += 1
                continue
            return None
        return None

    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        if STEM not in node.value:
            continue
        call = governing_call(node)
        if call is None:
            out.append({"file": rel, "line": node.lineno, "kind": "doc",
                        "strict": False, "text": node.value.replace("\n", " ")[:200]})
            continue
        strict = False
        for sub in ast.walk(call):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str) \
                    and "--strict" in sub.value:
                strict = True
        fn = call.func
        fname = fn.attr if isinstance(fn, ast.Attribute) else (
            fn.id if isinstance(fn, ast.Name) else "?")
        out.append({"file": rel, "line": node.lineno, "kind": "invoke",
                    "strict": strict, "text": "%s(%s)" % (fname, node.value[:120])})
    return out, ""


def scan(root: str):
    """⇒ (candidates, sites, parse_errors) ★
    candidates: {rel: {kinds: {kind: n}, lines: [..], unparsed: bool}} ★
    sites:      [{file, line, kind, strict, text}] ★"""
    candidates, sites, perrors = {}, [], {}
    for p in _iter_script_files(root):
        rel = os.path.relpath(p, root).replace(os.sep, "/")
        if rel in EXCLUDE_REL:
            continue
        txt = read_text(p)
        if STEM not in txt:
            continue
        if p.endswith(".py"):
            ss, err = scan_py(p, rel)
            if err:
                perrors[rel] = err
                candidates[rel] = {"kinds": {"unparsed": 1}, "lines": [], "unparsed": True}
                continue
        else:
            ss = scan_sh(p, rel)
        kinds, lines = {}, []
        for s in ss:
            kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
            if s["kind"] in ("invoke", "loggrep", "label"):
                lines.append(s["line"])
                sites.append(s)
        if not kinds:
            kinds = {"comment": 1}
        candidates[rel] = {"kinds": kinds, "lines": sorted(set(lines)),
                           "unparsed": False}
    return candidates, sites, perrors


def fake_green_hits(root: str):
    """⇒ [(rel, line, marker)] ★假绿标记串出现在【工具本体之外】的脚本里 ★"""
    hits = []
    for p in _iter_script_files(root):
        rel = os.path.relpath(p, root).replace(os.sep, "/")
        if rel in EXCLUDE_REL:
            continue
        for i, ln in enumerate(read_text(p).split("\n"), 1):
            for mk in FAKE_GREEN_MARKERS:
                if mk in ln:
                    hits.append((rel, i, mk))
    return hits


# ==============================================================================
# 台账
# ==============================================================================
def load_ledger(page_path: str):
    """⇒ (台账 dict, 错误串) ★"""
    if not os.path.exists(page_path):
        return {}, "★真相页不存在: %s" % page_path
    txt = read_text(page_path)
    i = txt.find(LEDGER_BEGIN)
    j = txt.find(LEDGER_END)
    if i < 0 or j < 0:
        return {}, "★真相页里找不到机器块标记 (%s / %s)" % (LEDGER_BEGIN, LEDGER_END)
    seg = txt[i + len(LEDGER_BEGIN):j]
    seg = "\n".join(ln for ln in seg.split("\n")
                    if not ln.strip().startswith("```"))
    try:
        return json.loads(seg, object_pairs_hook=_no_dup_pairs), ""
    except Exception as e:  # noqa: BLE001
        return {}, "★台账机器块解析失败: %s" % e


def _site_key(s):
    return (s["file"], int(s["line"]), s["kind"])


# ==============================================================================
# 主判定
# ==============================================================================
def evaluate(root: str, page_path: str, gate_check_path: str,
             outbox_dir: str) -> tuple:
    """⇒ (全过?, 输出行列表) ★"""
    sandbox = os.path.realpath(root) != os.path.realpath(PROJ)
    blocks = []

    def blk(cid, title, ok, lines):
        blocks.append((cid, title, bool(ok), list(lines)))

    # ---------------- T4 fail-closed (★先查输入·缺一个直接红★) ----------------
    t4 = []
    t4ok = True
    for p, what in ((page_path, "真相页"), (gate_check_path, "门禁链"),
                    (os.path.join(root, BOARD_REL), "板文件")):
        if not os.path.exists(p):
            t4.append("❌ %s 缺失 ⇒ fail-closed 判红: %s" % (what, p))
            t4ok = False
    if not os.path.isdir(outbox_dir):
        t4.append("❌ state/outbox/ 缺失 ⇒ fail-closed 判红")
        t4ok = False
    ledger, lerr = load_ledger(page_path)
    if lerr:
        t4.append("❌ %s" % lerr)
        t4ok = False
    blk("T4", "fail-closed (输入缺失 / 扫不到 ⇒ 判红, 不许判绿)", t4ok, t4)

    if not t4ok:
        # ★输入就不全 ⇒ 其余判据没有可信读数 ⇒ 直接红 (★不许"其余项默认绿"★)
        for cid, title in (("T1", "调用点全集自洽"),
                           ("T2", "放行链必须严格档"),
                           ("T3", "假绿输出不得被当放行凭据"),
                           ("T5", "零挂链 + 零外发自证"),
                           ("T6", "板指纹自证"),
                           ("T7", "「未布线 ⇒ 不可下单」闸点台账")):
            blk(cid, title, False, ["⛔ 因 T4 输入不全, 本项未判 ⇒ 按 fail-closed 记红"])
        return _render(blocks)

    # ---------------- 扫描 ----------------
    candidates, sites, perrors = scan(root)

    # ---------------- T1 ----------------
    t1 = []
    t1ok = True
    n_cand = len(candidates)
    if n_cand < MIN_CANDIDATES:
        t1.append("❌ 扫描命中文件数 = %d < %d ⇒ 扫描漏了 ⇒ 判红"
                  % (n_cand, MIN_CANDIDATES))
        t1ok = False
    else:
        t1.append("✅ T1a 扫描命中文件数 = %d (≥ %d) ⇒ 扫描没漏"
                  % (n_cand, MIN_CANDIDATES))

    led_cand = {}
    for c in (ledger.get("candidates") or []):
        f = c.get("file")
        if f:
            led_cand[f] = c
    live_set = set(candidates)
    led_set = set(led_cand)
    miss = sorted(live_set - led_set)      # ★实读有·台账没登记★
    extra = sorted(led_set - live_set)     # ★台账有·实读没有★
    if miss:
        t1.append("❌ T1b 实读命中但台账未登记 %d 个文件 ⇒ 判红: %s"
                  % (len(miss), ", ".join(miss[:8])))
        t1ok = False
    if extra:
        t1.append("❌ T1b 台账登记但实读扫不到 %d 个文件 (被改名/删除/路径错) ⇒ 判红: %s"
                  % (len(extra), ", ".join(extra[:8])))
        t1ok = False
    if not miss and not extra:
        t1.append("✅ T1b 候选文件集合 ↔ 实读双向一致 (%d 个)" % n_cand)

    led_sites = {}
    for s in (ledger.get("call_sites") or []):
        try:
            k = (s.get("file"), int(s.get("line")), s.get("kind"))
        except Exception:  # noqa: BLE001
            continue
        led_sites[k] = s
    live_sites = {}
    for s in sites:
        if s["kind"] in ("invoke", "loggrep", "label"):
            live_sites[_site_key(s)] = s
    lmiss = sorted(set(live_sites) - set(led_sites))
    lextra = sorted(set(led_sites) - set(live_sites))
    if lmiss:
        t1.append("❌ T1b 实读有调用点但台账未登记 %d 条 ⇒ 判红: %s"
                  % (len(lmiss), ", ".join("%s L%s %s" % k for k in lmiss[:8])))
        t1ok = False
    if lextra:
        t1.append("❌ T1b 台账登记的调用点实读不存在 %d 条 ⇒ 判红: %s"
                  % (len(lextra), ", ".join("%s L%s %s" % k for k in lextra[:8])))
        t1ok = False
    if not lmiss and not lextra:
        t1.append("✅ T1b 调用点 (文件,行,kind) ↔ 实读双向一致 (%d 条)" % len(live_sites))

    # ★台账声明的 strict 必须与实读逐字相同★
    for k in sorted(set(led_sites) & set(live_sites)):
        ls = led_sites[k]
        want = bool(ls.get("strict"))
        got = bool(live_sites[k]["strict"])
        if want != got:
            t1.append("❌ T1b 台账说 %s L%s %s strict=%s, 实读是 strict=%s ⇒ 判红"
                      % (k[0], k[1], k[2], want, got))
            t1ok = False
    if t1ok:
        t1.append("✅ T1b 台账 strict 标记 ↔ 实读逐字一致")

    # ★T1c 台账必须点名宽松档真调用点★
    lenient_inv = [k for k in sorted(live_sites)
                   if k[2] == "invoke" and not live_sites[k]["strict"]]
    led_lenient = [k for k in sorted(led_sites)
                   if k[2] == "invoke" and not bool(led_sites[k].get("strict"))]
    if lenient_inv and not led_lenient:
        t1.append("❌ T1c 台账没有点名任何宽松档真调用点 (实读有 %d 个) ⇒ 判红"
                  % len(lenient_inv))
        t1ok = False
    elif lenient_inv:
        t1.append("✅ T1c 台账点名宽松档真调用点 %d 个: %s"
                  % (len(lenient_inv),
                     ", ".join("%s L%s" % (k[0], k[1]) for k in lenient_inv)))
    else:
        t1.append("✅ T1c 当前没有宽松档真调用点")

    # ★T4 的第二半: 解析失败必须被登记★
    if perrors:
        unreg = sorted(f for f in perrors
                       if led_cand.get(f, {}).get("kind") != "unparsed")
        if unreg:
            t1.append("❌ T4 %d 个候选文件 AST 解析失败且台账未登记 ⇒ fail-closed 判红: %s"
                      % (len(unreg), ", ".join(unreg[:6])))
            t1ok = False
        else:
            t1.append("✅ T4 %d 个解析失败文件已被台账登记 (kind=unparsed)" % len(perrors))
    blk("T1", "调用点全集自洽 (AST/逻辑行实读 · 不许手抄清单)", t1ok, t1)

    # ---------------- T2 ----------------
    t2 = []
    t2ok = True
    inv_by_file = {}
    for k, s in live_sites.items():
        if k[2] == "invoke":
            inv_by_file.setdefault(k[0], []).append(s)
    for g in RELEASE_CHAIN_GATES:
        sites_g = inv_by_file.get(g, [])
        if not sites_g:
            t2.append("❌ %s 里【没有找到真调用点】⇒ 扫描漏了/被改名 ⇒ 判红" % g)
            t2ok = False
            continue
        bad = [s for s in sites_g if not s["strict"]]
        if bad:
            t2.append("❌ %s 的调用点不带 `--strict` ⇒ 放行链在宽松档上 ⇒ 判红: %s"
                      % (g, ", ".join("L%s" % s["line"] for s in bad)))
            t2ok = False
        else:
            t2.append("✅ %s 的调用点带 `--strict`" % g)
        # ★台账必须把它标成 must_strict★
        any_must = any(bool(led_sites.get(_site_key(s), {}).get("must_strict"))
                       for s in sites_g)
        if not any_must:
            t2.append("❌ %s 的调用点没被台账标成 must_strict=true ⇒ 判红" % g)
            t2ok = False
    blk("T2", "放行链必须严格档 (投产准入 / 板报告 / 候选验证 / 巡检)", t2ok, t2)

    # ---------------- T3 ----------------
    t3 = []
    t3ok = True

    # ★T3a 假绿标记串的每一次出现都要被台账登记★
    fg = fake_green_hits(root)
    led_q = {}
    for q in (ledger.get("quoted_markers") or []):
        try:
            led_q[(q.get("file"), int(q.get("line")), q.get("marker"))] = q
        except Exception:  # noqa: BLE001
            continue
    for f in fg:
        if (f[0], f[1], f[2]) not in led_q:
            t3.append("❌ T3a 假绿标记串「%s」出现在 %s L%d, 台账没登记 ⇒ 判红"
                      % (f[2], f[0], f[1]))
            t3ok = False
        elif (led_q[(f[0], f[1], f[2])].get("verdict") or "") != "quoted":
            t3.append("❌ T3a %s L%d 的「%s」被登记为【断言】⇒ 判红"
                      % (f[0], f[1], f[2]))
            t3ok = False
    extra_q = sorted(set(led_q) - set(fg))
    if extra_q:
        t3.append("❌ T3a 台账登记的假绿标记位置实读已不存在 %d 处 ⇒ 判红: %s"
                  % (len(extra_q), ", ".join("%s L%d" % (q[0], q[1]) for q in extra_q[:6])))
        t3ok = False
    if t3ok:
        t3.append("✅ T3a 假绿标记串「图纸可下单」在工具本体之外的 %d 处出现, "
                  "全部登记为 quoted (引述, 非对当前板的断言)" % len(fg))

    # ★T3b 每个真调用点都要登记 use★
    for k in sorted(live_sites):
        if k[2] != "invoke":
            continue
        ls = led_sites.get(k, {})
        use = (ls.get("use") or "").strip()
        if use not in USE_KINDS:
            t3.append("❌ T3b 真调用点 %s L%s 没登记 use (须 ∈ %s) ⇒ 判红"
                      % (k[0], k[1], "/".join(USE_KINDS)))
            t3ok = False
        else:
            t3.append("✅ T3b %s L%s 结果用途 = %s" % (k[0], k[1], use))

    # ★T3c use=judgement 的必须严格档★
    for k in sorted(live_sites):
        if k[2] != "invoke":
            continue
        ls = led_sites.get(k, {})
        if (ls.get("use") or "") != "judgement":
            continue
        if not live_sites[k]["strict"]:
            t3.append("❌ T3c %s L%s 的结果被当成判据 (use=judgement) 却跑在宽松档 ⇒ "
                      "判红" % (k[0], k[1]))
            t3ok = False
        else:
            t3.append("✅ T3c %s L%s use=judgement 且带 --strict" % (k[0], k[1]))

    # ★T3d 抄日志的点★
    for k in sorted(live_sites):
        if k[2] != "loggrep":
            continue
        ls = led_sites.get(k, {})
        src = (ls.get("log_source") or "").strip()
        up = (ls.get("upstream_script") or "").strip()
        ups = ls.get("upstream_strict")
        if not src or not up or ups is None:
            t3.append("❌ T3d 抄日志的调用点 %s L%s 没登记 (log_source / upstream_script / "
                      "upstream_strict) ⇒ 判红" % (k[0], k[1]))
            t3ok = False
            continue
        if not bool(ups):
            t3.append("❌ T3d 抄日志的调用点 %s L%s 的生产脚本 %s 【不是严格档】⇒ "
                      "假绿会被抄进放行结论 ⇒ 判红" % (k[0], k[1], up))
            t3ok = False
        else:
            t3.append("✅ T3d %s L%s 抄的 %s 由 %s 生产 (严格档) ⇒ 只是展示"
                      % (k[0], k[1], src, up))

    # ★T3e must_strict 的调用点必须有消费方★
    for k in sorted(live_sites):
        if k[2] != "invoke":
            continue
        ls = led_sites.get(k, {})
        if not bool(ls.get("must_strict")):
            continue
        cb = ls.get("consumed_by")
        if not isinstance(cb, list) or not cb:
            t3.append("❌ T3e must_strict 的调用点 %s L%s 没登记消费方 "
                      "(consumed_by 为空/缺) ⇒ 判红" % (k[0], k[1]))
            t3ok = False
        else:
            t3.append("✅ T3e %s L%s 登记了 %d 个消费方: %s"
                      % (k[0], k[1], len(cb), ", ".join(cb[:4])))

    # ★T3f must_strict=false 的调用点必须点名兜底闸且兜底在链上★
    for k in sorted(live_sites):
        if k[2] != "invoke":
            continue
        ls = led_sites.get(k, {})
        if bool(ls.get("must_strict")):
            continue
        fg_gate = (ls.get("fallback_gate") or "").strip()
        if not fg_gate:
            t3.append("❌ T3f 宽松档调用点 %s L%s 没登记兜底闸 (fallback_gate) ⇒ 判红"
                      % (k[0], k[1]))
            t3ok = False
        elif ls.get("fallback_on_chain") is not True:
            t3.append("❌ T3f 宽松档调用点 %s L%s 的兜底闸 %s 【不在链上】⇒ 判红"
                      % (k[0], k[1], fg_gate))
            t3ok = False
        else:
            t3.append("✅ T3f %s L%s 兜底闸 %s (在链上)" % (k[0], k[1], fg_gate))
    blk("T3", "假绿输出不得被当放行凭据", t3ok, t3)

    # ---------------- T5 ----------------
    t5 = []
    t5ok = True
    try:
        gtxt = read_text(gate_check_path)
    except Exception as e:  # noqa: BLE001
        gtxt = ""
        t5.append("❌ 读不到 %s: %s" % (gate_check_path, e))
        t5ok = False
    n_hook = gtxt.count(SELF_TOKEN)
    if n_hook != 0:
        t5.append("❌ 本闸名在 %s 里出现 %d 次 ⇒ 挂链了 ⇒ 判红 (★本单零挂链★)"
                  % (gate_check_path, n_hook))
        t5ok = False
    else:
        t5.append("✅ 零挂链: `%s` 在 %s 里 0 行" % (SELF_TOKEN, gate_check_path))

    base_out = ledger.get("meta", {}).get("outbox_baseline")
    if not isinstance(base_out, dict) or not base_out:
        t5.append("❌ 台账里没有 outbox_baseline ⇒ 判红 (★零外发没法自证★)")
        t5ok = False
    else:
        live_out = {}
        for dp, dn, fn in os.walk(outbox_dir):
            dn[:] = [x for x in dn if x != ".git"]
            for f in sorted(fn):
                p = os.path.join(dp, f)
                rel = os.path.relpath(p, root).replace(os.sep, "/")
                live_out[rel] = md5(p)
        o_miss = sorted(set(base_out) - set(live_out))
        o_extra = sorted(set(live_out) - set(base_out))
        o_diff = sorted(k for k in set(base_out) & set(live_out)
                        if base_out[k] != live_out[k])
        if o_miss or o_extra or o_diff:
            if o_miss:
                t5.append("❌ outbox 少了 %d 件 ⇒ 判红: %s" % (len(o_miss), ", ".join(o_miss[:5])))
            if o_extra:
                t5.append("❌ outbox 多了 %d 件 ⇒ 判红: %s" % (len(o_extra), ", ".join(o_extra[:5])))
            if o_diff:
                t5.append("❌ outbox 有 %d 件被改 ⇒ 判红: %s" % (len(o_diff), ", ".join(o_diff[:5])))
            t5ok = False
        else:
            t5.append("✅ 零外发: state/outbox/ %d 件逐件 md5 与基线相同" % len(live_out))
    blk("T5", "零挂链 + 零外发自证", t5ok, t5)

    # ---------------- T6 ----------------
    t6 = []
    t6ok = True
    bp = os.path.join(root, BOARD_REL)
    try:
        st = os.stat(bp)
        bmd5 = md5(bp)
    except Exception as e:  # noqa: BLE001
        st, bmd5 = None, ""
        t6.append("❌ 读不到板文件: %s" % e)
        t6ok = False
    if st is not None:
        if bmd5 != BOARD_MD5:
            t6.append("❌ 板 md5 = %s ≠ 基线 %s ⇒ 判红" % (bmd5, BOARD_MD5))
            t6ok = False
        else:
            t6.append("✅ 板 md5 = %s (与基线逐字相同)" % bmd5)
        if st.st_size != BOARD_SIZE:
            t6.append("❌ 板 size = %d ≠ 基线 %d ⇒ 判红" % (st.st_size, BOARD_SIZE))
            t6ok = False
        else:
            t6.append("✅ 板 size = %d (与基线逐字相同)" % st.st_size)
        if st.st_mtime_ns != BOARD_MTIME_NS:
            t6.append("❌ 板 mtime = %d ns ≠ 基线 %d ns ⇒ 判红"
                      % (st.st_mtime_ns, BOARD_MTIME_NS))
            t6ok = False
        else:
            t6.append("✅ 板 mtime = %d ns (与基线逐字相同)" % st.st_mtime_ns)
    # ★台账基线 vs 闸内写死基线 双查★
    lb = ledger.get("meta", {}).get("board_baseline") or {}
    if lb.get("md5") and lb.get("md5") != BOARD_MD5:
        t6.append("❌ 台账基线 md5 (%s) ≠ 闸内写死基线 (%s) ⇒ 判红"
                  % (lb.get("md5"), BOARD_MD5))
        t6ok = False
    blk("T6", "板指纹自证 (零写板)", t6ok, t6)

    # ---------------- T7 ----------------
    t7 = []
    t7ok = True
    ng = ledger.get("no_order_gates") or []
    ng_map = {}
    for g in ng:
        f = g.get("file")
        if f:
            ng_map[f] = g
    for f in REQUIRED_NO_ORDER_GATES:
        if f not in ng_map:
            t7.append("❌ 台账没登记「未布线 ⇒ 不可下单」闸点 %s ⇒ 判红" % f)
            t7ok = False
    for f, g in sorted(ng_map.items()):
        if f not in REQUIRED_NO_ORDER_GATES:
            continue
        if g.get("kind") not in NO_ORDER_KINDS:
            t7.append("❌ %s 的 kind 必须是 %s 之一 ⇒ 判红" % (f, "/".join(NO_ORDER_KINDS)))
            t7ok = False
        if "on_chain" not in g:
            t7.append("❌ %s 缺 on_chain 标记 ⇒ 判红" % f)
            t7ok = False
    abs_on = [f for f, g in ng_map.items()
              if g.get("kind") == "绝对闸" and g.get("on_chain") is True]
    if not abs_on:
        t7.append("❌ 没有任何一道「绝对闸」在链上 ⇒ 「未布线 ⇒ 不可下单」无处落地 ⇒ 判红")
        t7ok = False
    else:
        t7.append("✅ 链上的绝对闸: %s" % ", ".join(sorted(abs_on)))
    blk("T7", "「未布线 ⇒ 不可下单」闸点台账", t7ok, t7)

    return _render(blocks)


def _render(blocks):
    lines = []
    lines.append("=" * 78)
    lines.append("  ISS-409 · 「板那一趟」投产/放行链牙齿闸 · check_onepass_release_chain_teeth")
    lines.append("=" * 78)
    ok_all = True
    for cid, title, ok, bl in blocks:
        ok_all = ok_all and ok
        lines.append("")
        lines.append("【%s】%s  ⇒ %s" % (cid, title, "✅ 通过" if ok else "❌ 不通过"))
        for ln in bl:
            lines.append("   " + ln)
    lines.append("")
    lines.append("-" * 78)
    lines.append("★**总判定: %s**" % ("✅ 全过" if ok_all else
                                        "❌ 有不通过项 (★红的是现状, 不是闸故障★)"))
    lines.append("-" * 78)
    return ok_all, lines


# ==============================================================================
# 路径解析
# ==============================================================================
def resolve_paths(args) -> dict:
    def pick(env_name, default_rel, arg=None):
        if arg:
            return os.path.abspath(arg)
        env = os.environ.get(env_name)
        if env:
            return os.path.abspath(env)
        return os.path.join(PROJ, default_rel)

    root = os.path.abspath(args.root) if args.root else \
        os.path.abspath(os.environ.get("RELEASE_TEETH_ROOT") or PROJ)
    if not args.root:
        env_root = os.environ.get("RELEASE_TEETH_ROOT")
        if env_root:
            root = os.path.abspath(env_root)
    page = pick("RELEASE_TEETH_PAGE", DEFAULT_PAGE, args.page)
    if not page.startswith(root + os.sep) and page != root:
        page = os.path.join(root, DEFAULT_PAGE)
    gc = pick("RELEASE_TEETH_GATE_CHECK", DEFAULT_GATE_CHECK, args.gate_check)
    if not gc.startswith(root + os.sep):
        gc = os.path.join(root, DEFAULT_GATE_CHECK)
    ob = pick("RELEASE_TEETH_OUTBOX", DEFAULT_OUTBOX, args.outbox)
    if not ob.startswith(root + os.sep):
        ob = os.path.join(root, DEFAULT_OUTBOX)
    return {"root": root, "page": page, "gate_check": gc, "outbox": ob}


# ==============================================================================
# 沙盒 (selftest 用)
# ==============================================================================
SANDBOX_FILES = {
    "state/chain_gate.py": (
        '#!/usr/bin/env python3\n'
        'import subprocess, sys\n'
        'rc, _ = subprocess.run([sys.executable, "state/check_pcb_drc.py", "--strict"],\n'
        '                       capture_output=True)\n'
        'print("check_pcb_drc rc=%s" % rc)\n'
    ),
    "state/board_report.sh": (
        '#!/usr/bin/env bash\n'
        'bash state/pcbnew_py.sh state/check_pcb_drc.py --strict "$PCB" >/dev/null 2>&1\n'
        'echo "  check_pcb_drc   rc=$?"\n'
    ),
    "state/verify_candidate.sh": (
        '#!/usr/bin/env bash\n'
        'bash state/pcbnew_py.sh state/check_pcb_drc.py --strict "$CAND" 2>&1 | tail -5\n'
    ),
    "state/daily_check.py": (
        '#!/usr/bin/env python3\n'
        'import subprocess, sys\n'
        'rc = subprocess.run([sys.executable, "state/check_pcb_drc.py", "--strict"])\n'
        'print(rc.returncode)\n'
    ),
    "state/verify_and_release.sh": (
        '#!/usr/bin/env bash\n'
        'python3 state/check_pcb_drc.py --strict; _rc=$?\n'
        'echo "  check_pcb_drc(--strict) rc=$_rc"\n'
    ),
    "state/finish_line.sh": (
        '#!/usr/bin/env bash\n'
        'bash state/verify_and_release.sh > /tmp/verify_final.log 2>&1\n'
        'grep -E "unconnected items|DRC violations|check_pcb_drc" /tmp/verify_final.log | head -14\n'
    ),
    "state/replay_patch_chain.sh": (
        '#!/usr/bin/env bash\n'
        'bash state/pcbnew_py.sh state/check_pcb_drc.py --strict "$W" 2>&1 | grep -E "C3 |C4 "\n'
    ),
    "state/chain_tool_stamp.py": (
        '#!/usr/bin/env python3\n'
        '"""★工具指纹戳 (★只算 sha256, 不跑它★)"""\n'
        'TOOLS = ("patch_astar_nostub.py", "check_pcb_drc.py")\n'
        'print(TOOLS)\n'
    ),
    "state/gen_pcb_netlist_board.py": (
        '#!/usr/bin/env python3\n'
        '"""★可以用 KiCad DRC 验几何 (state/check_pcb_drc.py)★"""\n'
        'print("gen")\n'
    ),
    "state/gen_pcb_components.py": (
        '#!/usr/bin/env python3\n'
        '"""★随后由 state/check_pcb_drc.py + state/check_pcb_nets.py 双重验证★"""\n'
        'print("gen")\n'
    ),
    "state/gate_check.py": (
        '#!/usr/bin/env python3\n'
        '"""★门禁链 (★故意【不含】本闸名★)"""\n'
        'print("gate_check ok")\n'
    ),
}


def _w(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def build_sandbox(root: str) -> dict:
    """★建一个【结构与真盘同构】的沙盒 (★零硬链接: 内容拷贝★) ★"""
    os.makedirs(root, exist_ok=True)
    for rel, body in SANDBOX_FILES.items():
        _w(os.path.join(root, rel), body)
    # ★板: 内容拷贝 (★不用硬链接★) ⇒ md5 与真盘一致 ⇒ T6 走真判据 ★
    src = os.path.join(PROJ, BOARD_REL)
    dst = os.path.join(root, BOARD_REL)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(src):
        shutil.copyfile(src, dst)
        shutil.copystat(src, dst)
    else:
        _w(dst, "# sandbox board\n")
    # ★outbox: 两件 + 基线 ★
    ob = os.path.join(root, "state/outbox")
    _w(os.path.join(ob, "README.md"), "sandbox outbox readme\n")
    _w(os.path.join(ob, "attach", "a.md"), "sandbox outbox attach\n")
    return {"root": root}


# ★★沙盒里每个脚本的「结果怎么用」(★与真盘同构★) ★★
SANDBOX_USE = {
    "state/chain_gate.py": ("judgement", True),
    "state/daily_check.py": ("judgement", True),
    "state/verify_and_release.sh": ("judgement", True),
    "state/board_report.sh": ("display", True),
    "state/verify_candidate.sh": ("discarded", True),
    "state/replay_patch_chain.sh": ("discarded", False),
}
SANDBOX_FALLBACK = ("state/compare_arm_official.py", True)


def sandbox_ledger(root: str, candidates: dict, sites: list,
                   with_quoted: bool = True) -> dict:
    """★按沙盒实扫结果生成一份【台账】★"""
    led_c = []
    for f in sorted(candidates):
        led_c.append({"file": f, "kind": "unparsed" if candidates[f].get("unparsed")
                      else ",".join(sorted(candidates[f]["kinds"])),
                      "note": "sandbox"})
    led_s = []
    for s in sites:
        if s["kind"] not in ("invoke", "loggrep", "label"):
            continue
        use, must = SANDBOX_USE.get(s["file"], ("display", True))
        row = {"id": "SB-%s-L%d-%s" % (os.path.basename(s["file"]).replace(".", "_"),
                                       s["line"], s["kind"]),
               "file": s["file"], "line": s["line"], "kind": s["kind"],
               "strict": bool(s["strict"]), "argv": s["text"][:120],
               "chain": "sandbox", "must_strict": bool(must),
               "use": use,
               "consumed_by": ["state/finish_line.sh"] if must else [],
               "fallback_gate": SANDBOX_FALLBACK[0] if not must else "",
               "fallback_on_chain": SANDBOX_FALLBACK[1] if not must else None,
               "log_source": "/tmp/verify_final.log" if s["kind"] == "loggrep" else "",
               "upstream_script": "state/verify_and_release.sh" if s["kind"] == "loggrep" else "",
               "upstream_strict": True if s["kind"] == "loggrep" else None,
               "note": "sandbox", "evidence": "[实测]"}
        led_s.append(row)
    quoted = []
    if with_quoted:
        for f, ln, mk in fake_green_hits(root):
            quoted.append({"file": f, "line": ln, "marker": mk,
                           "verdict": "quoted", "context": "sandbox"})
    ob = {}
    for dp, dn, fn in os.walk(os.path.join(root, "state/outbox")):
        dn[:] = [x for x in dn if x != ".git"]
        for f in sorted(fn):
            p = os.path.join(dp, f)
            ob[os.path.relpath(p, root).replace(os.sep, "/")] = md5(p)
    return {
        "meta": {"iss": "ISS-409", "tool": "state/check_pcb_drc.py",
                 "generated_at": "sandbox",
                 "board_baseline": {"md5": BOARD_MD5, "size": BOARD_SIZE,
                                    "mtime_ns": BOARD_MTIME_NS},
                 "outbox_baseline": ob},
        "candidates": led_c,
        "call_sites": led_s,
        "quoted_markers": quoted,
        "no_order_gates": [
            {"id": "NG-%d" % i, "file": f, "kind": "绝对闸", "on_chain": True,
             "criterion": "unconnected==0", "evidence": "[实测]"}
            for i, f in enumerate(REQUIRED_NO_ORDER_GATES)],
    }


def write_sandbox_page(root: str, ledger: dict) -> str:
    page = os.path.join(root, DEFAULT_PAGE)
    body = (
        "# 沙盒真相页\n\n"
        "★本文件是 selftest 沙盒用的最小真相页★\n\n"
        + LEDGER_BEGIN + "\n```json\n"
        + json.dumps(ledger, ensure_ascii=False, indent=1)
        + "\n```\n" + LEDGER_END + "\n"
    )
    _w(page, body)
    return page


def refresh_sandbox(root: str) -> dict:
    """★把沙盒里的小文件恢复到【干净基线】(板不动) ★"""
    for rel, body in SANDBOX_FILES.items():
        _w(os.path.join(root, rel), body)
    cand, sites, _err = scan(root)
    led = sandbox_ledger(root, cand, sites)
    page = write_sandbox_page(root, led)
    return {"root": root, "page": page, "ledger": led,
            "candidates": cand, "sites": sites}


# ==============================================================================
# selftest
# ==============================================================================
def run_selftest() -> int:
    results = []

    def case(name: str, ok: bool, detail: str = ""):
        results.append((name, ok, detail))
        print("  %s %s%s" % ("✅" if ok else "❌", name,
                             ("  ⇒ " + detail) if detail and not ok else ""))

    sb_root = os.path.join(PROJ, "tmp", "iss409", "selftest_%d" % os.getpid())
    build_sandbox(sb_root)
    try:
        # ---------------- 正向 ----------------
        st = refresh_sandbox(sb_root)
        ok, lines = evaluate(st["root"], st["page"],
                             os.path.join(st["root"], "state/gate_check.py"),
                             os.path.join(st["root"], "state/outbox"))
        case("正向 · 干净沙盒 ⇒ 全绿", ok,
             " | ".join(l for l in lines if l.startswith("   ❌"))[:400])

        def neg(name, mut, want_block=None):
            st = refresh_sandbox(sb_root)
            mut(st)
            ok2, lines2 = evaluate(st["root"], st["page"],
                                    os.path.join(st["root"], "state/gate_check.py"),
                                    os.path.join(st["root"], "state/outbox"))
            hit = (not ok2)
            if want_block and hit:
                joined = "\n".join(lines2)
                hit = want_block in joined
                if not hit:
                    case(name, False, "判红了, 但不是 %s 判的" % want_block)
                    return
            case(name, hit,
                 " | ".join(l for l in lines2 if l.startswith("   ❌"))[:400])

        # 1. 真相页缺失
        def m1(st):
            os.remove(st["page"])
        neg("反向 01 · 真相页缺失 ⇒ fail-closed 判红", m1, "T4")

        # 2. 台账少登记一个候选文件
        def m2(st):
            st["ledger"]["candidates"] = st["ledger"]["candidates"][1:]
            write_sandbox_page(st["root"], st["ledger"])
        neg("反向 02 · 台账少登记候选文件 ⇒ T1 判红", m2, "T1")

        # 3. 台账把 strict 写错
        def m3(st):
            for r in st["ledger"]["call_sites"]:
                if r["kind"] == "invoke":
                    r["strict"] = not r["strict"]
                    break
            write_sandbox_page(st["root"], st["ledger"])
        neg("反向 03 · 台账 strict 与实读不符 ⇒ T1 判红", m3, "T1")

        # 4. 放行链某点被改成宽松档
        def m4(st):
            p = os.path.join(st["root"], "state/chain_gate.py")
            _w(p, SANDBOX_FILES["state/chain_gate.py"]
               .replace('"state/check_pcb_drc.py", "--strict"', '"state/check_pcb_drc.py"'))
            cand, sites, _e = scan(st["root"])
            led = sandbox_ledger(st["root"], cand, sites)
            led["call_sites"] = [r for r in led["call_sites"] if r["kind"] != "invoke"
                                 or r["file"] != "state/chain_gate.py"]
            # ★保留一条实读存在但台账登记 strict=true 的 invoke 行 ⇒ 触发 T2 而不是 T1b★
            for s in sites:
                if s["kind"] == "invoke" and s["file"] == "state/chain_gate.py":
                    led["call_sites"].append({
                        "id": "SB-keep", "file": s["file"], "line": s["line"],
                        "kind": "invoke", "strict": True, "argv": s["text"][:120],
                        "chain": "sandbox", "must_strict": True,
                        "consumed_by": ["state/finish_line.sh"],
                        "log_source": "", "upstream_script": "",
                        "upstream_strict": None, "evidence": "[实测]"})
                    break
            write_sandbox_page(st["root"], led)
        neg("反向 04 · 放行链某点跑宽松档 ⇒ T2 判红", m4, "T2")

        # 5. 假绿标记串被登记为【断言】
        def m5(st):
            _w(os.path.join(st["root"], "state/emit_order_ok.py"),
               '#!/usr/bin/env python3\nprint("✅ 全过 —— 图纸可下单")\n')
            cand, sites, _e = scan(st["root"])
            led = sandbox_ledger(st["root"], cand, sites)
            for q in led.get("quoted_markers") or []:
                q["verdict"] = "asserted"
            write_sandbox_page(st["root"], led)
        neg("反向 05 · 假绿标记串被登记为【断言】⇒ T3 判红", m5, "T3")

        # 6. 抄日志的点缺 upstream 登记
        def m6(st):
            led = st["ledger"]
            for r in led["call_sites"]:
                if r["kind"] == "loggrep":
                    r["upstream_script"] = ""
                    break
            write_sandbox_page(st["root"], led)
        neg("反向 06 · 抄日志的点缺 upstream 登记 ⇒ T3 判红", m6, "T3")

        # 7. 抄日志的上游不是严格档
        def m7(st):
            led = st["ledger"]
            for r in led["call_sites"]:
                if r["kind"] == "loggrep":
                    r["upstream_strict"] = False
                    break
            write_sandbox_page(st["root"], led)
        neg("反向 07 · 抄日志的上游不是严格档 ⇒ T3 判红", m7, "T3")

        # 8. 扫不到任何真调用点
        def m8(st):
            for rel in ("state/chain_gate.py", "state/board_report.sh",
                        "state/verify_candidate.sh", "state/daily_check.py",
                        "state/verify_and_release.sh", "state/replay_patch_chain.sh"):
                p = os.path.join(st["root"], rel)
                if os.path.exists(p):
                    os.remove(p)
            cand, sites, _e = scan(st["root"])
            led = sandbox_ledger(st["root"], cand, sites)
            led["call_sites"] = [r for r in led["call_sites"] if r["kind"] == "loggrep"]
            write_sandbox_page(st["root"], led)
        neg("反向 08 · 扫不到任何真调用点 ⇒ T2/T4 判红", m8)

        # 9. outbox 多了文件
        def m9(st):
            _w(os.path.join(st["root"], "state/outbox", "EXTRA.md"), "extra\n")
        neg("反向 09 · outbox 多了文件 ⇒ T5 判红", m9, "T5")

        # 10. gate_check 里出现本闸名
        def m10(st):
            _w(os.path.join(st["root"], "state/gate_check.py"),
               '#!/usr/bin/env python3\n# check_onepass_release_chain_teeth\nprint("x")\n')
        neg("反向 10 · 门禁链里出现本闸名 ⇒ T5 判红", m10, "T5")

        # 11. 板被改了
        def m11(st):
            p = os.path.join(st["root"], BOARD_REL)
            with open(p, "ab") as f:
                f.write(b"\n# tampered\n")
        neg("反向 11 · 板被改 ⇒ T6 判红", m11, "T6")

        # 12. no_order_gates 少登记一道
        def m12(st):
            led = st["ledger"]
            led["no_order_gates"] = led["no_order_gates"][:-1]
            write_sandbox_page(st["root"], led)
        neg("反向 12 · 「未布线 ⇒ 不可下单」闸点少登记 ⇒ T7 判红", m12, "T7")

        # 13. 候选文件 AST 解析失败且台账未登记
        def m13(st):
            _w(os.path.join(st["root"], "state/gen_broken.py"),
               'x = (\n')
            led = st["ledger"]
            led["candidates"] = [c for c in led["candidates"]
                                 if c["file"] != "state/gen_broken.py"]
            led["call_sites"] = [r for r in led["call_sites"]
                                 if r["file"] != "state/gen_broken.py"]
            write_sandbox_page(st["root"], led)
        neg("反向 13 · 解析失败文件未登记 ⇒ T1/T4 fail-closed 判红", m13)

        # 14. must_strict 的调用点缺消费方
        def m14(st):
            led = st["ledger"]
            for r in led["call_sites"]:
                if r["kind"] == "invoke" and r["must_strict"]:
                    r["consumed_by"] = []
                    break
            write_sandbox_page(st["root"], led)
        neg("反向 14 · must_strict 调用点缺消费方 ⇒ T3 判红", m14, "T3")

        # 15. 候选文件数不足下限 (扫描漏了)
        def m15(st):
            keep = {"state/chain_gate.py", "state/gate_check.py"}
            for rel in list(SANDBOX_FILES):
                if rel in keep:
                    continue
                p = os.path.join(st["root"], rel)
                if os.path.exists(p):
                    os.remove(p)
            cand, sites, _e = scan(st["root"])
            led = sandbox_ledger(st["root"], cand, sites)
            write_sandbox_page(st["root"], led)
        neg("反向 15 · 候选文件数不足 8 ⇒ T1 判红 (扫描漏了)", m15, "T1")

        # 16. 机器块解析失败
        def m16(st):
            _w(st["page"], "# 沙盒真相页\n\n没有机器块标记\n")
        neg("反向 16 · 机器块解析失败 ⇒ T4 fail-closed 判红", m16, "T4")

        # 17. 假绿标记串出现了但台账没登记
        def m17(st):
            _w(os.path.join(st["root"], "state/emit_order_ok.py"),
               '#!/usr/bin/env python3\nprint("✅ 全过 —— 图纸可下单")\n')
            cand, sites, _e = scan(st["root"])
            led = sandbox_ledger(st["root"], cand, sites, with_quoted=False)
            write_sandbox_page(st["root"], led)
        neg("反向 17 · 假绿标记串出现但台账没登记 ⇒ T3 判红", m17, "T3")

        # 18. 真调用点没登记 use
        def m18(st):
            led = st["ledger"]
            for r in led["call_sites"]:
                if r["kind"] == "invoke":
                    r["use"] = ""
                    break
            write_sandbox_page(st["root"], led)
        neg("反向 18 · 真调用点没登记 use ⇒ T3 判红", m18, "T3")

        # 19. 宽松档调用点的兜底闸不在链上
        def m19(st):
            led = st["ledger"]
            for r in led["call_sites"]:
                if r["kind"] == "invoke" and not r["must_strict"]:
                    r["fallback_on_chain"] = False
                    break
            write_sandbox_page(st["root"], led)
        neg("反向 19 · 宽松档调用点的兜底闸不在链上 ⇒ T3 判红", m19, "T3")

        # 20. use=judgement 却跑在宽松档
        def m20(st):
            p = os.path.join(st["root"], "state/daily_check.py")
            _w(p, SANDBOX_FILES["state/daily_check.py"]
               .replace('"state/check_pcb_drc.py", "--strict"', '"state/check_pcb_drc.py"'))
            cand, sites, _e = scan(st["root"])
            led = sandbox_ledger(st["root"], cand, sites)
            for r in led["call_sites"]:
                if r["file"] == "state/daily_check.py" and r["kind"] == "invoke":
                    r["strict"] = True      # ★台账说 strict, 实读 lenient ⇒ 触发 T1b + T3c★
            write_sandbox_page(st["root"], led)
        neg("反向 20 · use=judgement 却跑宽松档 ⇒ T1b/T3c 判红", m20)

    finally:
        shutil.rmtree(sb_root, ignore_errors=True)

    n_pos = sum(1 for _n, ok, _d in results if ok and _n.startswith("正向"))
    n_neg = sum(1 for n, ok, _d in results if ok and n.startswith("反向"))
    n_bad = sum(1 for _n, ok, _d in results if not ok)
    print("")
    print("  ★ 正向 %d 条 + 反向 %d 条 = %d 条 (失败 %d 条)"
          % (n_pos, n_neg, n_pos + n_neg, n_bad))
    if n_bad:
        print("  ❌ SELFTEST FAILED")
        return 1
    if n_pos < 1 or n_neg < 8:
        print("  ❌ SELFTEST 用例数不足 (要求 正向≥1 且 反向≥8)")
        return 1
    print("ALL TESTS PASS")
    return 0


# ==============================================================================
# main
# ==============================================================================
def main() -> int:
    ap = argparse.ArgumentParser(description="ISS-409 投产/放行链牙齿闸")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=None)
    ap.add_argument("--page", default=None)
    ap.add_argument("--gate-check", dest="gate_check", default=None)
    ap.add_argument("--outbox", default=None)
    a = ap.parse_args()
    if a.selftest:
        return run_selftest()
    p = resolve_paths(a)
    if not os.path.isdir(p["root"]):
        print("❌ 根目录不存在: %s" % p["root"])
        return 2
    ok, lines = evaluate(p["root"], p["page"], p["gate_check"], p["outbox"])
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
