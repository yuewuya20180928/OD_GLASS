#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-406 · 「板只改一次」验收链【牙齿】机器闸 (T1~T7)
=================================================================================================
派活: state/dispatch_briefs/ISS-406_hw_gate_teeth_invocation_audit.md (项目总工 main / moli · 2026-11-25)
执笔: 硬件总工 (hw-lead) · 2026-11-25

★★**本闸守的是什么**★★
  门禁链 `state/gate_check.py` 上的每一道闸, **它被调用时用的是哪一档** —— 而不只是「它在不在线上」。
  ★**既有闸盯的是「闸在不在链上」, 不是「闸被怎么调」**★:
    · `HW/check_onepass_preflight_coverage.py` P3 = 「清单引用的脚本在本机真实存在」⇒ 只查存在
    · `HW/check_onepass_gate_hook_coverage.py` G1 = 「点名的闸有没有在挂链表 / 人工签核台账」⇒ 只查在不在
    · `SW/tools/check_sw_gate_health.py` H1 = 「同一道闸在两个 TMPDIR 深度下读数是否相同」⇒ 环境无关性
  ⇒ ★**「调用档位 ⇒ 判据强度」这一轴, 全仓至今零机器闸覆盖 ⇒ 本闸补这一格**★

★★**最典型的坏结局 (★本机实测·非推算★)**★★
  `state/check_pcb_drc.py` L135-136 逐字:
      strict = "--strict" in sys.argv
      ok4 = (n_unc == 0) if strict else True
  ⇒ 不带 `--strict` ⇒ **C4 unconnected 恒判绿** ⇒ 板 unconnected=45 也判绿
  ⇒ L138-139 照打「✅ C4 unconnected items = 45」· L187 照打「✅ 全过 —— 图纸可下单」
  ⇒ ★**板那一趟若有人拿「DRC 通过」当验收凭据, 而那次调用没带 `--strict` ⇒ 验收是假的 ⇒ 板改第二次**★

★★**七条判据**★★
  T1 链上闸逐道台账自洽 : ★**链上每个挂链槽位, 在台账里有且只有一行**★
                          ★**argv 必须从 `state/gate_check.py` 用 AST 解析出来 (不许手抄)**★
                          解析条数 ≠ 台账条数 / 槽位 id 不匹配 / argv 不一致 ⇒ 判红
  T2 宽松档识别         : 对每道链上闸, 从其源码里找出「会让判据放宽或收窄的开关」
                          (★`--expect-*` / `--allow-*` / `--skip-*` / `--ignore-*` / `--only` / `--no-*` ★)
                          ⇒ ★**链上用宽松档的闸必须被点名 + 写清「宽松档放宽了哪条判据」**★
                          ⇒ ★**且必须被 main 签核 (`已接受(main 签核)`), 否则判红**★
  T3 fail-open 嫌疑自证 : 每道链上闸必须给出「输入缺失时会不会判绿」的判定
                          ⇒ ★**判「可能会」但拿不出行号证据的, 算没查 ⇒ 判红**★
                          ⇒ T3b: ★**投板前必跑闸在作业面页上被写下来的调用方式, 必须带严格档**★
  T4 板三证不动        : 板 / 网表 / 脚表 / BOM md5 与基线逐字相同
  T5 零挂链 + 零外发自证 : 本闸名在 `state/gate_check.py` 里的行数必须与台账登记的挂链状态一致
                          (★「待 main 挂链」⇒ 期望 0 行 · 「已挂链」⇒ 期望 ≥1 行★) · `state/outbox/` 未动
  T6 证据分级          : 台账里每条结论都带 `[官网]` / `[实测]` / `[媒体]` / `[推算]` / `[0数据]`
  T7 零写板自证        : 板 md5 / mtime / size 三项与基线逐字相同

★★**自指悖论 (★本闸不自拍·交 main 拍★)**★★
  T1 要求「链上每个闸在台账里有且只有一行」⇒ ★**本闸自己也不在链上**★ ⇒ 逻辑上它也该被登记
  ⇒ 而登记它的动作 = 挂链 = ★**main 的机制地界**★ ⇒ ★**台账里「本闸自身」这一行写「待 main 挂链」**★
  ⇒ ★**main 若决定挂本闸: ① 台账 `self.hook_status` 改成「已挂链」 ② 把本闸加进 `state/gate_check.py`
  ⇒ 本闸的 T5 会自动从「期望 grep=0」翻成「期望 grep≥1」★★ (★闸脚本一个字节都不用改★)

退出码: 0 = 全过 · 1 = 有不通过项 (★★红的是现状, 不是闸故障★★) · 2 = 用法错

用法:
  python3 HW/check_onepass_gate_teeth.py              # 主模式 (★今天必然 rc=1★)
  python3 HW/check_onepass_gate_teeth.py --selftest   # 反向用例 (★末行 ALL TESTS PASS★)

★**自检用 env 覆盖** (★只在【沙盒根 ≠ 项目根】时生效 ⇒ 改不了真盘的判据★):
  GATE_TEETH_ROOT · GATE_TEETH_PAGE · GATE_TEETH_GATE_CHECK · GATE_TEETH_PAGES · GATE_TEETH_OUTBOX
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

DEFAULT_PAGE = "HW/PCB/BOARD_ONEPASS_GATE_TEETH_AUDIT.md"
DEFAULT_GATE_CHECK = "state/gate_check.py"
DEFAULT_OUTBOX = "state/outbox"
DEFAULT_PAGES = (
    "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md",
    "HW/PCB/BOARD_ONEPASS_WORKPACKET.md",
    "HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md",
)
SELF_GATE = "HW/check_onepass_gate_teeth.py"
SELF_TOKEN = "check_onepass_gate_teeth"

LEDGER_BEGIN = "<!-- GATE_TEETH_LEDGER_BEGIN -->"
LEDGER_END = "<!-- GATE_TEETH_LEDGER_END -->"

EVIDENCE_TAGS = ("[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]")
VERDICTS = ("不会", "可能会")
ACCEPTED = "已接受(main 签核)"

# ★★「宽松档开关」名字判定: 只认这几族前缀 (★宁可漏也不猜★) ★★
LENIENT_NAME_RE = re.compile(r"^--(expect|allow|lenient|skip|ignore|tolerate|only|force|no-)")
FLAG_RE = re.compile(r"['\"](--[a-z0-9][a-z0-9-]*)['\"]")
LINE_REF_RE = re.compile(r"L\d{2,}")
CMD_SPAN_RE = re.compile(r"`([^`]*)`")


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


def _argv_of(node) -> list:
    """★argv 规范化渲染: 字符串原样 · `os.path.join(PROJ,"a","b")` ⇒ "a/b"★"""
    out = []
    if isinstance(node, (ast.Tuple, ast.List)):
        for e in node.elts:
            if isinstance(e, ast.Constant) and isinstance(e.value, str):
                out.append(e.value)
            elif isinstance(e, ast.Call) and isinstance(e.func, ast.Attribute) \
                    and e.func.attr == "join":
                ps = [a.value for a in e.args
                      if isinstance(a, ast.Constant) and isinstance(a.value, str)]
                out.append("/".join(x for x in ps if x != "PROJ"))
            else:
                out.append("<?>")
    return out


def parse_chain(gate_check_path: str) -> list:
    """★读门禁链 ⇒ [{slot_id, table, gate, label, argv}, ...] (★AST 读·不执行·不 import★) ★

    ★**为什么必须 AST 而不是手抄**: argv 是「判据强度」的唯一载体 ⇒ 手抄一次就漂一次
    ⇒ ★**本闸的台账必须能被机器证明「argv 与盘上的链逐字一致」**★ ★
    """
    src = read_text(gate_check_path)
    tree = ast.parse(src)
    slots = []
    for node in tree.body:
        if not (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)):
            continue
        n = node.targets[0].id
        if n in ("EXTRA_GATES", "PINNED_MD5_GATES"):
            for i, el in enumerate(node.value.elts):
                slots.append({
                    "slot_id": "%s[%d]" % (n, i),
                    "table": n,
                    "gate": _rel_of(el.elts[0]),
                    "label": ast.literal_eval(el.elts[1]),
                    "argv": _argv_of(el.elts[2]),
                })
        elif n == "HW_PINOUT_GATE":
            slots.append({
                "slot_id": "HW_PINOUT_GATE",
                "table": "HW_PINOUT_GATE",
                "gate": _rel_of(node.value),
                "label": "HW pinout 真源闸",
                "argv": [],
            })
    return slots


def flags_in(path: str) -> list:
    t = read_text(path)
    return sorted(set(FLAG_RE.findall(t)))


def lenient_flags_in(path: str) -> list:
    return sorted(f for f in flags_in(path) if LENIENT_NAME_RE.match(f))


def compile_ok(path: str) -> bool:
    try:
        compile(read_text(path), path, "exec")
        return True
    except Exception:  # noqa: BLE001
        return False


def _no_dup_pairs(pairs):
    """★JSON 重复 key 检测 (★台账里同一个槽位写两遍 ⇒ T1 判红★) ★"""
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError("★台账里出现重复 key: %s" % k)
        d[k] = v
    return d


def load_ledger(page_path: str) -> tuple:
    """⇒ (台账 dict, 错误串) ★"""
    if not os.path.exists(page_path):
        return {}, "★台账页不存在: %s" % page_path
    txt = read_text(page_path)
    i = txt.find(LEDGER_BEGIN)
    j = txt.find(LEDGER_END)
    if i < 0 or j < 0:
        return {}, "★台账页里找不到机器块标记 (%s / %s)" % (LEDGER_BEGIN, LEDGER_END)
    seg = txt[i + len(LEDGER_BEGIN):j]
    seg = "\n".join(ln for ln in seg.split("\n")
                    if not ln.strip().startswith("```"))
    try:
        return json.loads(seg, object_pairs_hook=_no_dup_pairs), ""
    except Exception as e:  # noqa: BLE001
        return {}, "★台账机器块解析失败: %s" % e


def documented_invocations(root: str, pages: list, gate_rel: str) -> list:
    """★从作业面页里抽出【被写下来的调用方式】⇒ [(page, line_no, span), ...] ★

    ★**只认「看起来像命令」的片段**: 片段里必须同时出现
      (a) 闸脚本名 (全路径或 basename) · (b) 一个解释器 (`python3` / `python` / `bash`)
    ⇒ ★**纯提及 (例如「③ PCB 段 = ... + `check_pcb_drc`」) 不算调用方式**★
    ⇒ ★**这样本页说的「文档化调用方式」就是页面上真正能复制粘贴的那一串**★ ★
    """
    out = []
    base = os.path.basename(gate_rel)
    for pg in pages:
        p = os.path.join(root, pg)
        if not os.path.exists(p):
            continue
        for i, ln in enumerate(read_text(p).split("\n"), 1):
            if base not in ln:
                continue
            spans = CMD_SPAN_RE.findall(ln)
            cands = [s for s in spans
                     if base in s and re.search(r"\b(python3?|bash)\s", s)]
            if cands:
                for s in cands:
                    out.append((pg, i, s.strip()))
            elif not spans and re.search(r"\b(python3?|bash)\s", ln):
                out.append((pg, i, ln.strip()))
    return out


# ==============================================================================
# 主判定
# ==============================================================================
def evaluate(root: str, page_path: str, gate_check_path: str, pages: list,
             outbox_dir: str) -> tuple:
    """⇒ (全过?, 输出行列表) ★"""
    sandbox = os.path.realpath(root) != os.path.realpath(PROJ)
    blocks = []

    def blk(cid, title, ok, lines):
        blocks.append((cid, title, ok, lines))

    # ---------- 台账 ----------
    led, lerr = load_ledger(page_path)
    if lerr:
        led = {}

    # ---------- 链 ----------
    chain = []
    chain_err = ""
    if not os.path.exists(gate_check_path):
        chain_err = "★门禁链脚本不存在: %s ⇒ fail-closed" % gate_check_path
    else:
        try:
            chain = parse_chain(gate_check_path)
        except Exception as e:  # noqa: BLE001
            chain_err = "★门禁链解析失败: %s ⇒ fail-closed" % e

    # ============== T1 ==============
    t1 = []
    t1_ok = True
    if chain_err:
        t1_ok = False
        t1.append("     ❌ %s" % chain_err)
    if lerr:
        t1_ok = False
        t1.append("     ❌ %s ⇒ fail-closed (★不许「查不到就算过」★)" % lerr)
    lchain = (led.get("chain") or {}) if isinstance(led, dict) else {}
    if not t1_ok:
        pass
    else:
        parsed_ids = [s["slot_id"] for s in chain]
        led_ids = list(lchain.keys())
        if len(parsed_ids) != len(led_ids):
            t1_ok = False
            t1.append("     ❌ ★解析条数 %d ≠ 台账条数 %d ⇒ 台账与链不同步"
                      % (len(parsed_ids), len(led_ids)))
        if set(parsed_ids) != set(led_ids):
            t1_ok = False
            for s in sorted(set(parsed_ids) - set(led_ids)):
                t1.append("        ❌ 链上有 · 台账无: %s" % s)
            for s in sorted(set(led_ids) - set(parsed_ids)):
                t1.append("        ❌ 台账有 · 链上无: %s" % s)
        for s in chain:
            e = lchain.get(s["slot_id"])
            if not isinstance(e, dict):
                continue
            if e.get("gate") != s["gate"]:
                t1_ok = False
                t1.append("     ❌ ★%s 的闸路径不一致: 台账 %r ≠ AST 解析 %r"
                          % (s["slot_id"], e.get("gate"), s["gate"]))
            if list(e.get("argv") or []) != list(s["argv"]):
                t1_ok = False
                t1.append("     ❌ ★%s 的 argv 不一致: 台账 %r ≠ AST 解析 %r "
                          "⇒ ★**台账里的档位不是盘上链真正用的档位**★"
                          % (s["slot_id"], e.get("argv"), s["argv"]))
        if t1_ok:
            t1.append("     ✔ 链上 %d 个挂链槽位 (★%d 个不同脚本★) 在台账里【有且只有一行】"
                      % (len(parsed_ids), len(set(s["gate"] for s in chain))))
            t1.append("     ✔ 每行的闸路径 + argv 与 AST 解析值逐字相同 (★argv 不许手抄★)")
    for s in chain:
        p = os.path.join(root, s["gate"])
        if not os.path.exists(p):
            t1_ok = False
            t1.append("     ❌ ★%s 引用的闸脚本不存在: %s ⇒ fail-closed" % (s["slot_id"], s["gate"]))
        elif not compile_ok(p):
            t1_ok = False
            t1.append("     ❌ ★%s 引用的闸脚本语法跑不起来: %s ⇒ fail-closed"
                      % (s["slot_id"], s["gate"]))
    blk("T1", "链上闸逐道台账自洽 (★argv 由 AST 解析·不许手抄★)", t1_ok, t1)

    # ============== T2 ==============
    t2 = []
    t2_ok = True
    for s in chain:
        e = lchain.get(s["slot_id"]) or {}
        p = os.path.join(root, s["gate"])
        src_len = lenient_flags_in(p) if os.path.exists(p) else []
        used = [f for f in s["argv"] if LENIENT_NAME_RE.match(f)]
        if list(e.get("source_lenient_flags") or []) != src_len:
            t2_ok = False
            t2.append("     ❌ ★%s 的「源码里存在的宽松档开关」台账 %r ≠ 实读 %r ⇒ 台账过期"
                      % (s["slot_id"], e.get("source_lenient_flags"), src_len))
        if list(e.get("used_lenient_flags") or []) != used:
            t2_ok = False
            t2.append("     ❌ ★%s 的「链上实际用的宽松档」台账 %r ≠ AST 解析 %r"
                      % (s["slot_id"], e.get("used_lenient_flags"), used))
        if src_len and not used:
            t2.append("     ℹ️ %-22s 源码有宽松档开关 %s · ★链上一个都没用 (跑的是全量档)★"
                      % (s["gate"], src_len))
        if used:
            relax = str(e.get("lenient_relaxes") or "").strip()
            if not relax:
                t2_ok = False
                t2.append("     ❌ ★%s 在宽松档 %s 下跑, 但台账没写「宽松档放宽了哪条判据」⇒ 判红"
                          % (s["slot_id"], used))
            acc = str(e.get("lenient_acceptance") or "").strip()
            if acc != ACCEPTED:
                t2_ok = False
                t2.append("     ❌ ★%s 在宽松档 %s 下跑, 但台账 lenient_acceptance=%r "
                          "(★只有 main 签核写成 %r 才放行·本闸不代拍★)"
                          % (s["slot_id"], used, acc, ACCEPTED))
            else:
                t2.append("     ✔ %-22s 宽松档 %s 已由 main 签核放行 (★放宽了: %s★)"
                          % (s["gate"], used, relax[:70]))
    if t2_ok:
        t2.append("     ✔ 链上没有「未签核的宽松档」⇒ ★每一道闸跑的都是它自己最强的档★")
    blk("T2", "宽松档识别 (★链上用宽松档的闸必须被点名 + 写清放宽了哪条 + main 签核★)",
        t2_ok, t2)

    # ============== T3 ==============
    t3 = []
    t3_ok = True
    for s in chain:
        e = lchain.get(s["slot_id"]) or {}
        v = str(e.get("fail_open_verdict") or "").strip()
        ev = str(e.get("fail_open_evidence") or "").strip()
        if v not in VERDICTS:
            t3_ok = False
            t3.append("     ❌ ★%s 没有 fail_open_verdict (★合法值: %s·拿不出判定 = 算没查★)"
                      % (s["slot_id"], "/".join(VERDICTS)))
            continue
        if not ev:
            t3_ok = False
            t3.append("     ❌ ★%s 判「%s」但拿不出任何依据 ⇒ ★判「可能会」但拿不出行号证据的, "
                      "算没查★" % (s["slot_id"], v))
        elif not LINE_REF_RE.search(ev):
            t3_ok = False
            t3.append("     ❌ ★%s 的 fail-open 证据里没有行号 (★要 L<行号> 级证据★): %s"
                      % (s["slot_id"], ev[:70]))
        else:
            t3.append("     ✔ %-22s fail-open: %s" % (s["gate"], v))
    # ---- T3b: 投板前必跑闸在作业面页上的文档化调用方式, 必须带严格档 ----
    sr = led.get("strict_required") or []
    if not sr:
        t3_ok = False
        t3.append("     ❌ ★台账里没有 strict_required (★投板前必须用严格档跑的闸名单★) ⇒ 判红")
    for r in sr:
        g = (r or {}).get("gate") or ""
        sw = str((r or {}).get("required_switch") or "").strip()
        p = os.path.join(root, g)
        if not g or not os.path.exists(p):
            t3_ok = False
            t3.append("     ❌ ★strict_required 点名的闸不存在: %s ⇒ fail-closed" % g)
            continue
        if sw and not sw.startswith("("):
            if sw not in flags_in(p):
                t3_ok = False
                t3.append("     ❌ ★%s 台账说严格档开关是 %s, 但源码里没这个开关 ⇒ 台账过期"
                          % (g, sw))
        invs = documented_invocations(root, pages, g)
        if not invs:
            t3_ok = False
            t3.append("     ❌ ★%s 在作业面页上找不到任何【文档化调用方式】⇒ "
                      "★投板前必跑闸却没人写怎么跑 = 没人跑★" % g)
            continue
        bad = [(pg, ln, sp) for (pg, ln, sp) in invs if sw and not sw.startswith("(")
               and sw not in sp]
        if bad:
            t3_ok = False
            for pg, ln, sp in bad:
                t3.append("     ❌ ★%s 在 %s L%d 的文档化调用方式【%s】不含严格档 %s "
                          "⇒ ★**这条命令证明不了它自己声明的判据**★"
                          % (g, pg, ln, sp[:70], sw))
        else:
            t3.append("     ✔ %-24s 作业面页上的 %d 处文档化调用方式全部带 %s"
                      % (g, len(invs), sw or "(无严格档开关)"))
    blk("T3", "fail-open 嫌疑自证 (★行号级证据★) + T3b 投板前必跑闸必须带严格档",
        t3_ok, t3)

    # ============== T4 ==============
    t4 = []
    t4_ok = True
    bb = led.get("board_baseline") or {}
    bpath = os.path.join(root, bb.get("path") or "HW/PCB/demo_mainboard.kicad_pcb")
    if not os.path.exists(bpath):
        t4_ok = False
        t4.append("     ❌ ★板文件不存在: %s ⇒ fail-closed" % bpath)
    else:
        cur = md5(bpath)
        want = bb.get("md5") or BOARD_MD5
        if not sandbox and want != BOARD_MD5:
            t4_ok = False
            t4.append("     ❌ ★台账里的板基线 %s ≠ 闸内写死基线 %s ⇒ 台账与闸的判决源不一致"
                      % (want, BOARD_MD5))
        if cur != want:
            t4_ok = False
            t4.append("     ❌ ★板 md5 %s ≠ 基线 %s ⇒ 盘面被改过 (★零写板自证失败★)"
                      % (cur, want))
        else:
            t4.append("     ✔ 板 md5 = %s (== 基线)" % cur)
    tb = led.get("tables_baseline") or {}
    if not tb:
        t4_ok = False
        t4.append("     ❌ ★台账里没有 tables_baseline (★网表/脚表/BOM 三个 md5★) ⇒ 判红")
    for rel, want in tb.items():
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            t4_ok = False
            t4.append("     ❌ %s 不存在 ⇒ fail-closed" % rel)
            continue
        cur = md5(p)
        if cur != want:
            t4_ok = False
            t4.append("     ❌ ★%s md5 %s ≠ 基线 %s ⇒ ★零落表自证失败★" % (rel, cur, want))
        else:
            t4.append("     ✔ %s = %s" % (rel, cur))
    blk("T4", "板三证不动 (★板 / 网表 / 脚表 / BOM md5 与基线逐字相同★)", t4_ok, t4)

    # ============== T5 ==============
    t5 = []
    t5_ok = True
    status = ((led.get("self") or {}).get("hook_status") or "").strip()
    src = read_text(gate_check_path) if os.path.exists(gate_check_path) else ""
    n_lines = sum(1 for ln in src.split("\n") if SELF_TOKEN in ln)
    if status == "待 main 挂链":
        if n_lines == 0:
            t5.append("     ✔ 本闸名在 %s 里的行数 = 0 (★零挂链·台账登记状态 = 待 main 挂链★)"
                      % os.path.basename(gate_check_path))
        else:
            t5_ok = False
            t5.append("     ❌ ★台账登记「待 main 挂链」但 %s 里已有 %d 行提到本闸 ⇒ "
                      "★台账与链不一致·请把台账 self.hook_status 改成「已挂链」★"
                      % (os.path.basename(gate_check_path), n_lines))
    elif status == "已挂链":
        if n_lines >= 1:
            t5.append("     ✔ 本闸已挂链 (%s 里 %d 行) ⇒ 台账登记状态一致"
                      % (os.path.basename(gate_check_path), n_lines))
        else:
            t5_ok = False
            t5.append("     ❌ ★台账登记「已挂链」但 %s 里找不到本闸 ⇒ fail-closed"
                      % os.path.basename(gate_check_path))
    else:
        t5_ok = False
        t5.append("     ❌ ★台账 self.hook_status = %r, 合法值只有「待 main 挂链」/「已挂链」"
                  "⇒ fail-closed" % status)
    ob_base = led.get("outbox_baseline") or {}
    cur_ob = {}
    if os.path.isdir(outbox_dir):
        for r, _d, files in os.walk(outbox_dir):
            for fn in sorted(files):
                p = os.path.join(r, fn)
                cur_ob[os.path.relpath(p, outbox_dir)] = {
                    "md5": md5(p), "size": os.stat(p).st_size}
    if cur_ob != ob_base:
        t5_ok = False
        t5.append("     ❌ ★state/outbox/ 与台账基线不一致 (★零外发自证失败·差 %d 条★)"
                  % len(set(cur_ob) ^ set(ob_base)))
        for k in sorted(set(cur_ob) - set(ob_base)):
            t5.append("        ❌ 新增/多出: %s" % k)
        for k in sorted(set(ob_base) - set(cur_ob)):
            t5.append("        ❌ 消失: %s" % k)
        for k in sorted(set(cur_ob) & set(ob_base)):
            if cur_ob[k] != ob_base[k]:
                t5.append("        ❌ 变了: %s" % k)
    else:
        t5.append("     ✔ state/outbox/ %d 件与台账基线逐字相同 (★零外发★)" % len(cur_ob))
    blk("T5", "零挂链 + 零外发自证", t5_ok, t5)

    # ============== T6 ==============
    t6 = []
    t6_ok = True
    rows = []
    for sid, e in (lchain or {}).items():
        rows.append((sid, (e or {}).get("evidence")))
    for i, r in enumerate(sr):
        rows.append(((r or {}).get("gate") or "(strict_required#%d)" % i,
                     (r or {}).get("evidence")))
    rows.append(("self", (led.get("self") or {}).get("evidence")))
    for name, ev in rows:
        if ev not in EVIDENCE_TAGS:
            t6_ok = False
            t6.append("     ❌ ★%s 没标证据等级 (★合法: %s·evidence=%r★)"
                      % (name, " / ".join(EVIDENCE_TAGS), ev))
    if t6_ok:
        t6.append("     ✔ 台账 %d 条结论全部带证据等级标签" % len(rows))
    blk("T6", "证据分级 (★每条结论标 [官网]/[实测]/[媒体]/[推算]/[0数据]★)", t6_ok, t6)

    # ============== T7 ==============
    t7 = []
    t7_ok = True
    if not os.path.exists(bpath):
        t7_ok = False
        t7.append("     ❌ ★板文件不存在 ⇒ fail-closed")
    else:
        st = os.stat(bpath)
        cur_md5 = md5(bpath)
        want_md5 = bb.get("md5")
        want_size = bb.get("size")
        want_mtime = bb.get("mtime_ns")
        if want_md5 and cur_md5 != want_md5:
            t7_ok = False
            t7.append("     ❌ ★板 md5 %s ≠ 基线 %s" % (cur_md5, want_md5))
        elif want_size is not None and st.st_size != want_size:
            t7_ok = False
            t7.append("     ❌ ★板 size %d ≠ 基线 %d" % (st.st_size, want_size))
        elif want_mtime is not None and st.st_mtime_ns != want_mtime:
            t7_ok = False
            t7.append("     ❌ ★板 mtime_ns %d ≠ 基线 %d" % (st.st_mtime_ns, want_mtime))
        else:
            t7.append("     ✔ 板 md5 / mtime_ns / size 三项与基线逐字相同 "
                      "(md5=%s size=%d)" % (cur_md5, st.st_size))
    blk("T7", "零写板自证 (★md5 / mtime / size 三项与基线逐字相同★)", t7_ok, t7)

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
    root = os.path.abspath(args.root or os.environ.get("GATE_TEETH_ROOT") or PROJ)
    sandbox = os.path.realpath(root) != os.path.realpath(PROJ)

    def pick(env_name, default_rel, arg=None):
        if arg:
            return arg if os.path.isabs(arg) else os.path.join(root, arg)
        v = os.environ.get(env_name)
        if v and sandbox:
            return v if os.path.isabs(v) else os.path.join(root, v)
        return os.path.join(root, default_rel)

    pages_env = os.environ.get("GATE_TEETH_PAGES") if sandbox else None
    pages = [x for x in pages_env.split(",") if x.strip()] if pages_env \
        else list(DEFAULT_PAGES)
    return {
        "root": root,
        "page": pick("GATE_TEETH_PAGE", DEFAULT_PAGE, args.page),
        "gate_check": pick("GATE_TEETH_GATE_CHECK", DEFAULT_GATE_CHECK, args.gate_check),
        "pages": pages,
        "outbox": pick("GATE_TEETH_OUTBOX", DEFAULT_OUTBOX, args.outbox),
    }


# ==============================================================================
# --selftest (★沙盒在 tmp/iss406/ 下·不写系统 /tmp·不碰真件★)
# ==============================================================================
STUB_GATE = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"ISS-406 沙盒占位闸 (★selftest 用·不是真闸★)\"\"\"
print("sandbox gate stub")
"""


def _w(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def build_sandbox(root: str) -> dict:
    """★搭一个自洽的沙盒仓 (★真件一个字节都不碰★) ★

    ★**基线设计**: 沙盒链上 4 个槽位 (3 个不同脚本) · 其中一道闸在宽松档下跑但**已签核**
    ⇒ ★**基线全绿**★ ⇒ ★**反向用例每一条都是「把某处改坏 ⇒ 必须变红」**★ ★
    """
    shutil.rmtree(root, ignore_errors=True)
    # --- 闸脚本 ---
    _w(os.path.join(root, "HW", "check_alpha.py"),
       STUB_GATE + '\nif "--json" in __import__("sys").argv:\n    print("{}")\n')
    _w(os.path.join(root, "HW", "check_beta.py"),
       STUB_GATE + '\nif "--expect-known" in __import__("sys").argv:\n    print("known")\n')
    _w(os.path.join(root, "MECH", "check_gamma.py"),
       STUB_GATE + '\nif "--only" in __import__("sys").argv:\n    print("only")\n')
    _w(os.path.join(root, "state", "check_pcb_drc.py"),
       STUB_GATE + '\nstrict = "--strict" in __import__("sys").argv\nprint(strict)\n')
    _w(os.path.join(root, "state", "check_pcb_nets.py"), STUB_GATE)
    # --- 门禁链 (★AST 读得到的形状★) ---
    chain = [
        "import os",
        'PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))',
        "EXTRA_GATES = [",
        '    (os.path.join(PROJ, "HW", "check_alpha.py"), "沙盒闸 alpha", ()),',
        '    (os.path.join(PROJ, "HW", "check_beta.py"), "沙盒闸 beta", ("--expect-known",)),',
        "]",
        "PINNED_MD5_GATES = [",
        '    (os.path.join(PROJ, "MECH", "check_gamma.py"), "沙盒闸 gamma", ()),',
        "]",
        'HW_PINOUT_GATE = os.path.join(PROJ, "HW", "check_alpha.py")',
    ]
    _w(os.path.join(root, "state", "gate_check.py"), "\n".join(chain) + "\n")
    # --- 作业面页 (★文档化调用方式带 --strict ⇒ 基线绿★) ---
    for pg in DEFAULT_PAGES:
        _w(os.path.join(root, pg),
           "# 沙盒作业面页\n判据: `python3 state/check_pcb_drc.py --strict` ⇒ rc=0\n"
           "判据: `python3 state/check_pcb_nets.py` ⇒ rc=0\n")
    # --- 板 + 三张表 ---
    _w(os.path.join(root, "HW", "PCB", "demo_mainboard.kicad_pcb"), "SANDBOX BOARD\n")
    for rel in ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv"):
        _w(os.path.join(root, rel), "SANDBOX %s\n" % rel)
    # --- outbox ---
    _w(os.path.join(root, "state", "outbox", "keep.md"), "sandbox outbox\n")
    ob = {}
    for r, _d, files in os.walk(os.path.join(root, "state", "outbox")):
        for fn in files:
            p = os.path.join(r, fn)
            ob[os.path.relpath(p, os.path.join(root, "state", "outbox"))] = {
                "md5": md5(p), "size": os.stat(p).st_size}
    # --- 台账 ---
    slots = parse_chain(os.path.join(root, "state", "gate_check.py"))
    chain_map = {}
    for s in slots:
        p = os.path.join(root, s["gate"])
        src_len = lenient_flags_in(p)
        used = [f for f in s["argv"] if LENIENT_NAME_RE.match(f)]
        chain_map[s["slot_id"]] = {
            "gate": s["gate"],
            "label": s["label"],
            "argv": s["argv"],
            "argv_text": " ".join(s["argv"]) if s["argv"] else "(无)",
            "source_flags": flags_in(p),
            "source_lenient_flags": src_len,
            "used_lenient_flags": used,
            "lenient_relaxes": ("沙盒: 该闸把「零缺陷」换成「与快照一致」" if used else ""),
            "lenient_acceptance": (ACCEPTED if used else "不适用"),
            "fail_open_verdict": "不会",
            "fail_open_evidence": "L001 沙盒桩: 缺输入 ⇒ rc=2 ⇒ 判红",
            "evidence": "[实测]",
        }
    bst = os.stat(os.path.join(root, "HW", "PCB", "demo_mainboard.kicad_pcb"))
    led = {
        "ledger_id": "沙盒台账",
        "version": "1.0",
        "issue": "ISS-406",
        "evidence_tags_allowed": list(EVIDENCE_TAGS),
        "self": {"gate": SELF_GATE, "hook_status": "待 main 挂链",
                 "evidence": "[实测]", "note": "沙盒"},
        "board_baseline": {
            "path": "HW/PCB/demo_mainboard.kicad_pcb",
            "md5": md5(os.path.join(root, "HW", "PCB", "demo_mainboard.kicad_pcb")),
            "size": bst.st_size, "mtime_ns": bst.st_mtime_ns,
            "evidence": "[实测]"},
        "tables_baseline": {
            "HW/netlist_v1.csv": md5(os.path.join(root, "HW/netlist_v1.csv")),
            "HW/netlist_v1_pins.csv": md5(os.path.join(root, "HW/netlist_v1_pins.csv")),
            "HW/BOM_v1.csv": md5(os.path.join(root, "HW/BOM_v1.csv")),
        },
        "outbox_baseline": ob,
        "chain": chain_map,
        "strict_required": [
            {"gate": "state/check_pcb_drc.py", "required_switch": "--strict",
             "required_argv": ["--strict"], "why": "沙盒",
             "blocks": "沙盒", "consequence": "沙盒", "evidence": "[实测]"},
            {"gate": "state/check_pcb_nets.py",
             "required_switch": "(无严格档开关 · 本闸没有宽松档)",
             "required_argv": [], "why": "沙盒",
             "blocks": "沙盒", "consequence": "沙盒", "evidence": "[实测]"},
        ],
    }
    page = os.path.join(root, DEFAULT_PAGE)
    _w(page, "# 沙盒真相页\n\n%s\n```json\n%s\n```\n%s\n"
       % (LEDGER_BEGIN, json.dumps(led, ensure_ascii=False, indent=1), LEDGER_END))
    return {"page": page}


def run_selftest() -> int:
    base = os.path.join(PROJ, "tmp", "iss406")
    os.makedirs(base, exist_ok=True)
    sb = os.path.join(base, "selftest_%d" % os.getpid())
    cases = []

    def run(root):
        p = resolve_paths(argparse.Namespace(root=root, page=None, gate_check=None,
                                             outbox=None))
        return evaluate(p["root"], p["page"], p["gate_check"], p["pages"], p["outbox"])

    def failed(lines, cid):
        for l in lines:
            s = l.strip()
            if s.startswith(("OK ", "FAIL")) and s.split()[1] == cid:
                return s.startswith("FAIL")
        return False

    def load_led():
        with open(os.path.join(sb, DEFAULT_PAGE), encoding="utf-8") as f:
            t = f.read()
        i = t.find(LEDGER_BEGIN)
        j = t.find(LEDGER_END)
        seg = "\n".join(ln for ln in t[i + len(LEDGER_BEGIN):j].split("\n")
                        if not ln.strip().startswith("```"))
        return json.loads(seg)

    def save_led(d):
        _w(os.path.join(sb, DEFAULT_PAGE),
           "# 沙盒真相页\n\n%s\n```json\n%s\n```\n%s\n"
           % (LEDGER_BEGIN, json.dumps(d, ensure_ascii=False, indent=1), LEDGER_END))

    try:
        # ---------- 正向 ----------
        build_sandbox(sb)
        ok, lines = run(sb)
        cases.append(("★正向: 沙盒基线 (宽松档已签核 · 文档化调用带 --strict) ⇒ 全绿 rc=0",
                      ok is True,
                      "★自证改动★: 沙盒 %s · 台账 lenient_acceptance=已接受(main 签核) · "
                      "作业面页写 `python3 state/check_pcb_drc.py --strict`" % sb))
        if not ok:
            for l in lines:
                print("       ", l)

        # ---------- 反向 1: 台账漏登记一个链上槽位 ⇒ T1 红 ----------
        build_sandbox(sb)
        d = load_led()
        d["chain"].pop("PINNED_MD5_GATES[0]")
        save_led(d)
        ok, lines = run(sb)
        cases.append(("① 台账漏登记一个链上槽位 ⇒ T1 红 (★每道闸有且只有一行★)",
                      failed(lines, "T1"),
                      "★自证改动★: 沙盒台账 chain 删掉 PINNED_MD5_GATES[0]"))

        # ---------- 反向 2: 台账多一行不存在的闸 ⇒ T1 红 ----------
        build_sandbox(sb)
        d = load_led()
        d["chain"]["PINNED_MD5_GATES[9]"] = dict(d["chain"]["EXTRA_GATES[0]"])
        save_led(d)
        ok, lines = run(sb)
        cases.append(("② 台账多登记一个链上没有的槽位 ⇒ T1 红 (★解析条数 ≠ 台账条数★)",
                      failed(lines, "T1"),
                      "★自证改动★: 沙盒台账 chain 加一个 PINNED_MD5_GATES[9]"))

        # ---------- 反向 3: 台账里的 argv 与 AST 解析值不符 ⇒ T1 红 ----------
        build_sandbox(sb)
        d = load_led()
        d["chain"]["EXTRA_GATES[1]"]["argv"] = []
        save_led(d)
        ok, lines = run(sb)
        cases.append(("③ 台账里的 argv 与盘上链实际用的档位不符 ⇒ T1 红 "
                      "(★argv 不许手抄★)",
                      failed(lines, "T1"),
                      "★自证改动★: 沙盒台账把 EXTRA_GATES[1] 的 argv 从 "
                      "['--expect-known'] 改成 []"))

        # ---------- 反向 4: 链上闸改了档位但台账没跟 ⇒ T1 红 ----------
        build_sandbox(sb)
        gc = os.path.join(sb, "state", "gate_check.py")
        _w(gc, read_text(gc).replace('("--expect-known",)', '("--only",)'))
        ok, lines = run(sb)
        cases.append(("④ 盘上链改了某道闸的档位但台账没跟 ⇒ T1 红",
                      failed(lines, "T1"),
                      "★自证改动★: 沙盒 gate_check.py 把 EXTRA_GATES[1] 的 "
                      "--expect-known 换成 --only"))

        # ---------- 反向 5: 宽松档未签核 ⇒ T2 红 ----------
        build_sandbox(sb)
        d = load_led()
        d["chain"]["EXTRA_GATES[1]"]["lenient_acceptance"] = "未签核"
        save_led(d)
        ok, lines = run(sb)
        cases.append(("⑤ 链上闸跑宽松档但没经 main 签核 ⇒ T2 红 "
                      "(★本闸不代拍★)",
                      failed(lines, "T2"),
                      "★自证改动★: 沙盒台账 lenient_acceptance 改成 未签核"))

        # ---------- 反向 6: 台账没写「宽松档放宽了哪条判据」⇒ T2 红 ----------
        build_sandbox(sb)
        d = load_led()
        d["chain"]["EXTRA_GATES[1]"]["lenient_relaxes"] = ""
        save_led(d)
        ok, lines = run(sb)
        cases.append(("⑥ 台账没写清「宽松档放宽了哪条判据」⇒ T2 红",
                      failed(lines, "T2"),
                      "★自证改动★: 沙盒台账 lenient_relaxes 清空"))

        # ---------- 反向 7: fail-open 判定缺行号证据 ⇒ T3 红 ----------
        build_sandbox(sb)
        d = load_led()
        d["chain"]["EXTRA_GATES[0]"]["fail_open_evidence"] = "缺输入会判绿 (口说无凭)"
        save_led(d)
        ok, lines = run(sb)
        cases.append(("⑦ fail-open 判定拿不出行号级证据 ⇒ T3 红 "
                      "(★判「可能会」但拿不出行号证据的算没查★)",
                      failed(lines, "T3"),
                      "★自证改动★: 沙盒台账 fail_open_evidence 去掉行号"))

        # ---------- 反向 8: fail-open 判定缺失 ⇒ T3 红 ----------
        build_sandbox(sb)
        d = load_led()
        d["chain"]["EXTRA_GATES[0]"].pop("fail_open_verdict")
        save_led(d)
        ok, lines = run(sb)
        cases.append(("⑧ 某道链上闸没有 fail-open 判定 ⇒ T3 红 (★没查=判红★)",
                      failed(lines, "T3"),
                      "★自证改动★: 沙盒台账删掉 EXTRA_GATES[0] 的 fail_open_verdict"))

        # ---------- 反向 9: 作业面页的文档化调用方式丢了严格档 ⇒ T3 红 ----------
        build_sandbox(sb)
        pg = os.path.join(sb, DEFAULT_PAGES[0])
        _w(pg, "# 沙盒作业面页\n判据: `python3 state/check_pcb_drc.py` ⇒ rc=0\n"
                "判据: `python3 state/check_pcb_nets.py` ⇒ rc=0\n")
        ok, lines = run(sb)
        cases.append(("⑨ 作业面页上的文档化调用方式丢了严格档 ⇒ T3 红 "
                      "(★这条命令证明不了它自己声明的判据★)",
                      failed(lines, "T3"),
                      "★自证改动★: 沙盒预检清单页把 `--strict` 删掉"))

        # ---------- 反向 10: 板被改一个字节 ⇒ T4 红 + T7 红 ----------
        build_sandbox(sb)
        bp = os.path.join(sb, "HW", "PCB", "demo_mainboard.kicad_pcb")
        _w(bp, read_text(bp) + "; injected\n")
        ok, lines = run(sb)
        cases.append(("⑩ 板被改一个字节 ⇒ T4 红 且 T7 红 (★零写板自证★)",
                      failed(lines, "T4") and failed(lines, "T7"),
                      "★自证改动★: 沙盒板文件尾部加一行"))

        # ---------- 反向 11: 网表被改 ⇒ T4 红 ----------
        build_sandbox(sb)
        np_ = os.path.join(sb, "HW", "netlist_v1.csv")
        _w(np_, read_text(np_) + "injected\n")
        ok, lines = run(sb)
        cases.append(("⑪ 网表被改一个字节 ⇒ T4 红 (★零落表自证★)",
                      failed(lines, "T4"),
                      "★自证改动★: 沙盒 HW/netlist_v1.csv 尾部加一行"))

        # ---------- 反向 12: outbox 多一个文件 ⇒ T5 红 ----------
        build_sandbox(sb)
        _w(os.path.join(sb, "state", "outbox", "smuggled.md"), "smuggled\n")
        ok, lines = run(sb)
        cases.append(("⑫ state/outbox/ 多一个文件 ⇒ T5 红 (★零外发自证★)",
                      failed(lines, "T5"),
                      "★自证改动★: 沙盒 outbox 里塞 smuggled.md"))

        # ---------- 反向 13: 本闸被挂进链但台账仍写「待 main 挂链」⇒ T5 红 ----------
        build_sandbox(sb)
        gc = os.path.join(sb, "state", "gate_check.py")
        _w(gc, read_text(gc).replace("EXTRA_GATES = [",
                                      'EXTRA_GATES = [\n    (os.path.join(PROJ, "HW", '
                                      '"check_onepass_gate_teeth.py"), "本闸自己", ()),'))
        ok, lines = run(sb)
        cases.append(("⑬ 本闸被挂进链但台账仍写「待 main 挂链」⇒ T5 红 "
                      "(★自指悖论的可翻转机制★)",
                      failed(lines, "T5"),
                      "★自证改动★: 沙盒 gate_check.py 把本闸挂进 EXTRA_GATES, 台账不动"))

        # ---------- 反向 14: 某条结论缺证据等级 ⇒ T6 红 ----------
        build_sandbox(sb)
        d = load_led()
        d["chain"]["EXTRA_GATES[0]"].pop("evidence", None)
        save_led(d)
        ok, lines = run(sb)
        cases.append(("⑭ 台账某条结论缺证据等级标签 ⇒ T6 红",
                      failed(lines, "T6"),
                      "★自证改动★: 沙盒台账 EXTRA_GATES[0] 删掉 evidence"))

        # ---------- 反向 15: 板 mtime 变了 (内容没变) ⇒ T7 红 ----------
        build_sandbox(sb)
        bp = os.path.join(sb, "HW", "PCB", "demo_mainboard.kicad_pcb")
        os.utime(bp, ns=(bst_ns(bp) + 10 ** 9, bst_ns(bp) + 10 ** 9))
        ok, lines = run(sb)
        cases.append(("⑮ 板 mtime 变了 (内容没变) ⇒ T7 红 (★mtime 也算★)",
                      failed(lines, "T7"),
                      "★自证改动★: 沙盒板文件 utime +1s"))
    finally:
        shutil.rmtree(sb, ignore_errors=True)

    print("=" * 78)
    print("  ISS-406 · 反向用例 (★每条都自证「真的改到了目标」 ★)")
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


def bst_ns(path):
    return os.stat(path).st_mtime_ns


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=None)
    ap.add_argument("--page", default=None)
    ap.add_argument("--gate-check", dest="gate_check", default=None)
    ap.add_argument("--outbox", default=None)
    args = ap.parse_args()

    if args.selftest:
        return run_selftest()

    p = resolve_paths(args)
    print("=" * 78)
    print("  ISS-406 · 验收链【牙齿】闸 (★T1 台账自洽 / T2 宽松档 / T3 fail-open+严格档 / "
          "T4 板三证 / T5 零挂链+零外发 / T6 证据分级 / T7 零写板★)")
    print("  ★红的是现状 (★链上有闸跑在宽松档 + 投板前必跑闸的文档化调用丢了严格档★), "
          "不是闸故障 ★")
    print("=" * 78)
    ok, lines = evaluate(p["root"], p["page"], p["gate_check"], p["pages"], p["outbox"])
    for l in lines:
        print(l)
    print("-" * 78)
    if ok:
        print("  ✅ rc=0: ★★链上每一道闸都跑在自己最强的档 + 投板前必跑闸的调用方式都带严格档 ★★")
        return 0
    print("  ❌ rc=1: ★★链上还有闸跑在宽松档 / 投板前必跑闸的文档化调用方式证明不了它自己 "
          "声明的判据 ★★")
    print("             ⇒ ★「板那一趟」当天照着作业面页跑 ⇒ 拿到的绿是假绿 ⇒ 板改第二次 ★★")
    return 1


if __name__ == "__main__":
    sys.exit(main())
