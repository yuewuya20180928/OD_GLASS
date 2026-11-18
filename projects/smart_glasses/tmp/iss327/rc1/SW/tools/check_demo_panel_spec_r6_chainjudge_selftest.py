#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py — ISS-312 · 链头落表单号交叉核对 专项反向用例
=================================================================================================
★★**这个闸防的是什么** ★ (★ISS-309 已 verified · main 05:4x 本机复跑·ISS-312 修完★):

  权威判据 `SW/tools/check_demo_panel_spec.py` 对【落表台账链头的落表单号】**只查「非空」**
  ⇒ ★单号被改坏 (假号 / 多个号 / 与真源不一致) **一律判绿** ⇒ 那是**漏放 (假绿)** ★

  ★**ISS-312 修法 (main 拍板: A + B 都要)** ★
    · **A** 链头产出单号必须【唯一】⇒ 同一个 md5 被两个单号声称产出 = 台账自相矛盾 ⇒ 判红
    · **B** 链头单号必须与【独立信源】对上 ⇒ ★独立信源 = `state/issue_log.yaml`★
      (★main 维护 · 只读 · 与被测对象无关 ⇒ 不是自证★)

★★**本文件装的是【反向用例】, 不是判据** ★
  · 判据在 `SW/tools/check_demo_panel_spec.py` (★本文件只【调用】它, 不复制一份★)
  · ★**每条用例都带「不是巧合」的自证** ★:
      ① 用例改坏的确实是【链头那一条记录的落表单号】 (自证: 链头 md5 没变 · 原单号已不在产出单号里)
      ② ★**同一棵被改坏的树, 修前的判据 (`check_demo_panel_spec.py.bak_iss312`) 判【绿】★
         ⇒ ⇒ 这条红只可能来自新加的 A / B 交叉核对 ⇒ **不是巧合**
      ③ 红项数量 = 1 (⇒ 红的原因唯一 ⇒ 不是别的红项顺带把它带红的)
  · ★**第 4 条是正向对照 (原样不动 ⇒ 必须绿)** ⇒ ★不许把闸修成永远红★

★★**用例清单** ★

  | 用例 | 期望 | 场景 | 抓的是哪道 |
  |---|---|---|---|
  | **CJ-1** | ★红★ | 只改一处 ⇒ 链头产出单号 = {真单号, 假单号} ⇒ **台账自相矛盾** | **A** (不唯一) |
  | **CJ-2** | ★红★ | 每一处都改成一个【**不存在**的】单号 ⇒ 台账自洽但单号是假的 | **B①** (独立信源里查不到) |
  | **CJ-3** | ★红★ | 每一处都改成一个【**真实存在但对不上**】的单号 ⇒ 单号是真的, 事是假的 | **B②** (独立信源里没有这个 md5 的留痕) |
  | **CJ-4** | ★绿★ | 原样不动 ⇒ 必须绿 | (正向对照: 闸没被修成永远红) |

★★**沙盒纪律** ★:
  · 全部用例在临时树上跑, ★**真盘一个字节都不写** ★
  · 临时树里带一份 `state/issue_log.yaml` (★真拷·只读★) ⇒ 独立信源就是真的那一份
  · ★**绝对不许硬链接 (hardlink)** ★ (★有一条用例要改板文件★) ⇒ 全部走真拷贝

用法:
    python3 SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py           # rc=0 = 4 条全过
    python3 SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py --root .  # 指定项目根
    python3 SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py --tmpdir /data/tmp
    ★ISS-309 实测坑★: 系统临时目录 (/tmp) 有【每用户配额】⇒ 配额满时拷贝 4.9 MB 的板会 EDQUOT
      ⇒ 本脚本自动退回 `~/.cache/openclaw-tmp` (或 `ISS312_TMPDIR` / `TMPDIR` / 项目内 tmp/iss312_tmp) ★
"""
from __future__ import annotations

import argparse
import copy
import importlib.machinery
import importlib.util
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))          # .../SW/tools
PROJ = os.path.dirname(os.path.dirname(HERE))              # .../<项目库根>
BAK = os.path.join(HERE, "check_demo_panel_spec.py.bak_iss312")   # ★修前的判据 (★用于「不是巧合」自证★)


# ---------------------------------------------------------------- 判据模块 (★import, 不复制★)
def _load_gate():
    path = os.path.join(HERE, "check_demo_panel_spec.py")
    spec = importlib.util.spec_from_file_location("check_demo_panel_spec_gate", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_gate_bak():
    """★修前的判据 (★ISS-312 留的 `.bak_iss312`★) ⇒ 用来证明「这条红来自新加的交叉核对」★."""
    if not os.path.isfile(BAK):
        return None
    loader = importlib.machinery.SourceFileLoader("check_demo_panel_spec_gate_bak", BAK)
    spec = importlib.util.spec_from_loader("check_demo_panel_spec_gate_bak", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


gate = _load_gate()
gate_bak = _load_gate_bak()

NET = "HW/netlist_v1.csv"
PINS = "HW/netlist_v1_pins.csv"
BOARD = os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb")

# ★临时树要拷的文件 (★全拷贝, 不用硬链接★)
TREE_FILES = (
    gate.DEMO_SPEC,
    gate.TRIAGE,
    gate.PIPELINE,
    gate.LEDGER_DOC,
    os.path.join("HW", "SCHEMATIC_LANDING_V1_LANDED.md"),
    os.path.join("HW", "netlist_v1.csv"),
    os.path.join("HW", "netlist_v1_pins.csv"),
    os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb"),
    os.path.join("HW", "PCB", "demo_mainboard.kicad_pro"),
    gate.ISSUE_LOG_REL,                 # ★独立信源 (★真拷·只读★)
)


# ---------------------------------------------------------------- 沙盒工具
def _make_tmpdir(explicit: str = "") -> str:
    """★建临时树根目录 ⇒ 系统临时目录配额满了就退回下一个候选 (★ISS-309 实测坑★)."""
    cands = []
    if explicit:
        cands.append(explicit)
    for env in ("ISS312_TMPDIR", "TMPDIR"):
        v = os.environ.get(env) or ""
        if v:
            cands.append(v)
    cands.append(tempfile.gettempdir())
    cands.append(os.path.join(os.path.dirname(PROJ), "tmp", "iss312_tmp"))
    cands.append(os.path.join(os.path.expanduser("~"), ".cache", "openclaw-tmp"))
    last = ""
    for root in cands:
        d = ""
        try:
            os.makedirs(root, exist_ok=True)
            d = tempfile.mkdtemp(prefix="iss312_cj_", dir=root)
            probe = os.path.join(d, "_probe.bin")
            with open(probe, "wb") as f:
                f.truncate(12 * 1024 * 1024)     # ★tmpfs 不支持稀疏 ⇒ 这一步真占配额 (板 4.9MB + issue_log 3MB)★
            os.remove(probe)
        except OSError as exc:
            last = "%s: %s" % (root, exc)
            if d:
                shutil.rmtree(d, ignore_errors=True)
            continue
        return d
    raise SystemExit("❌ 临时树根目录建不起来 (系统临时目录配额满?): %s" % last)


def build_tree(tmp: str, root: str, name: str) -> str:
    """在临时目录里搭一棵完整的树 (★全拷贝 ⇒ 改它不会碰真盘★)。"""
    work = os.path.join(tmp, name)
    for rel in TREE_FILES:
        src = os.path.join(root, rel)
        dst = os.path.join(work, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    return work


def fresh_tree(tmp: str, root: str, name: str) -> tuple:
    work = build_tree(tmp, root, name)
    anchors, err = gate.load_sw_anchor(work)
    assert anchors is not None, "临时树读不到锚点 (%s)" % err
    return work, copy.deepcopy(anchors)


def rd(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def wr(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def ledger_path(work: str) -> str:
    return os.path.join(work, gate.LEDGER_CANON)


# ---------------------------------------------------------------- 台账改坏工具 (★口径必须与判据一致★)
def _rec_md5s(line: str) -> list:
    return gate.LEDGER_MD_RE.findall(line.strip())


def break_head_ticket_all(text: str, rel: str, bogus: str, limit: int = 0) -> tuple:
    """把【产出链头的那些记录】的落表单号, 在它【出现的每一处】都改掉 (★`limit` = 最多改几处★)。

    ★口径必须与判据 `sw_ledger_records` 一字不差★:
      · 行内写了 `ISS-xxx` ⇒ 单号 = 行内第一个 (⇒ 改行内那一个★)
      · 行内没写单号 ⇒ 单号继承【最近一个【带单号】的小节标题】(⇒ 改那【标题】那一个★)
    ★只改一处 = 台账自相矛盾 (⇒ 修法 A 治它) · 每一处都改 = 台账自洽但单号是假的 (⇒ 修法 B 治它)★
    返回 (新文本, 改了几处)。
    """
    base = os.path.basename(rel)
    head = gate.sw_ledger_state(rel, text)["head"]
    if not head:
        raise AssertionError("台账里 %s 取不到链头 ⇒ 用例本身坏了" % rel)
    lines = text.splitlines()
    ctx_idx = -1
    todo: list = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("#"):
            if re.search(r"ISS-\d+", s):
                ctx_idx = i
            continue
        if not (s.startswith("|") and (rel in s or base in s)):
            continue
        toks = _rec_md5s(ln)
        if len(toks) < 2 or toks[-1][:12] != head:
            continue              # ★这条记录不产出链头 ⇒ 不动它★
        if re.search(r"ISS-\d+", s):
            todo.append(i)        # ★行内单号★
        elif ctx_idx >= 0:
            todo.append(ctx_idx)  # ★继承来的单号 ⇒ 改【小节标题】那一处★
    out = list(lines)
    seen: set = set()
    for idx in todo:
        if idx in seen:
            continue
        if limit and len(seen) >= limit:
            break
        seen.add(idx)
        out[idx] = re.sub(r"ISS-\d+", bogus, out[idx], count=1)
    return ("\n".join(out) + "\n", len(seen))


# ---------------------------------------------------------------- 独立信源 (issue_log) 读法
def issue_log_blocks(root: str) -> dict:
    """独立信源 issue_log ⇒ {ISS-xxx: 那一整条的原文} (★用判据自己的读法★ ⇒ 口径一字不差★)."""
    return gate.sw_issue_log_entries(root)


def pick_real_but_wrong_iss(root: str, rel: str, head: str, true_iss: str) -> str:
    """挑一个【真实存在但对不上】的单号 (★CJ-3 用★)。

    ★挑选口径★: 该单在 issue_log 里【真实存在】, 且它的留痕里【提到了这个文件】
      但【没有这个链头 md5】⇒ ⇒ 新的交叉核对会红在「独立信源里没有这个 md5 的留痕」
      ⇒ ★⇒ 红的原因唯一 (不是「单号不存在」那条)⇒ 证明抓的是【md5 级】的交叉核对★
    """
    blocks = issue_log_blocks(root)
    base = os.path.basename(rel)
    for iss in sorted(blocks):
        if iss == true_iss:
            continue
        ch = blocks[iss]
        if base not in ch:
            continue
        if head[:12] in ch or head[:8] in ch:
            continue
        return iss
    raise AssertionError("issue_log 里找不到一个「真实存在但对不上」的单号 ⇒ 用例本身坏了")


# ---------------------------------------------------------------- 用例
def run_cases(tmp: str, root: str) -> int:
    base_led = gate.read_text(root, gate.LEDGER_CANON)
    st_net = gate.sw_ledger_state(NET, base_led)
    head_net = st_net["head"]
    true_iss = (st_net.get("head_iss") or [""])[0]
    blocks = issue_log_blocks(root)

    print("=" * 100)
    print("ISS-312 · SW 侧 R6 【链头落表单号交叉核对】 —— 专项反向用例 (修法 A + B)")
    print("=" * 100)
    print("  判决源台账 = %s (★只读★)" % gate.LEDGER_CANON)
    print("  独立信源   = %s (★main 维护 · 只读 · 与被测对象无关★)" % gate.ISSUE_LOG_REL)
    print("  网表链头   = %s · 产出单号 = %s" % (head_net, st_net.get("head_iss")))
    if not true_iss:
        print("  ❌ 台账里取不到网表链头的落表单号 ⇒ 反向自测不成立")
        return 2
    if not blocks:
        print("  ❌ 独立信源 %s 读不到任何条目 ⇒ 反向自测不成立" % gate.ISSUE_LOG_REL)
        return 2
    if gate_bak is None:
        print("  ❌ 找不到修前的判据备份 %s ⇒ 「不是巧合」自证做不了" % BAK)
        return 2
    # ★自证: 真单号在独立信源里【有据可查】(⇒ 绿是挣来的, 不是碰巧) ★
    true_block = blocks.get(true_iss, "")
    print("  ★自证: 真单号 %s 在独立信源里有条目 (status=%s) · 留痕里有文件名 %s: %s · 有链头 md5 %s: %s"
          % (true_iss,
             (re.search(r"^\s*status:\s*(\S+)", true_block, re.M).group(1)
              if re.search(r"^\s*status:\s*(\S+)", true_block, re.M) else "?"),
             os.path.basename(NET), os.path.basename(NET) in true_block,
             head_net[:12], (head_net[:12] in true_block or head_net[:8] in true_block)))
    print("-" * 100)

    # ---- CJ-4 (绿): 原样不动 ⇒ 必须绿 -----------------------------------------------
    def case_cj4():
        """原样不动 ⇒ 必须绿 (★不许把闸修成永远红★)。"""
        work, anchors = fresh_tree(tmp, root, "cj4")
        return work, anchors

    # ---- CJ-1 (红): 只改一处 ⇒ 台账自相矛盾 ⇒ 必须红 (★修法 A★) ---------------------
    def case_cj1():
        work, anchors = fresh_tree(tmp, root, "cj1")
        p = ledger_path(work)
        base = rd(p)
        broken, hit = break_head_ticket_all(base, NET, bogus="ISS-9900", limit=1)
        if hit < 1:
            raise AssertionError("没命中链头的落表单号 ⇒ 用例本身坏了")
        wr(p, broken)
        st = gate.sw_ledger_state(NET, broken)
        prods = sorted((st.get("producer") or {}).get(head_net) or [])
        # ★自证 ①: 链头没变 · 原单号还在 (⇒ 台账自相矛盾) · 假单号进来了 ★
        if st.get("head") != head_net:
            raise AssertionError("改单号把链头也改了 ⇒ 用例本身坏了")
        if true_iss not in prods:
            raise AssertionError("原单号 %s 不在产出单号里了 (%s) ⇒ 改坏没生效" % (true_iss, prods))
        if "ISS-9900" not in prods:
            raise AssertionError("假单号不在产出单号里 (%s) ⇒ 用例本身坏了" % prods)
        print("      ★自证: 只改了 1 处 ⇒ 链头产出单号 = %s ⇒ 台账【自相矛盾】(两个单号抢同一个 md5)"
              % prods)
        return work, anchors

    # ---- CJ-2 (红): 每一处都改成一个【不存在的】单号 ⇒ 必须红 (★修法 B①★) -------------
    def case_cj2():
        work, anchors = fresh_tree(tmp, root, "cj2")
        p = ledger_path(work)
        base = rd(p)
        broken, hit = break_head_ticket_all(base, NET, bogus="ISS-9900")
        if hit < 1:
            raise AssertionError("没命中链头的落表单号 ⇒ 用例本身坏了")
        wr(p, broken)
        st = gate.sw_ledger_state(NET, broken)
        prods = sorted((st.get("producer") or {}).get(head_net) or [])
        if st.get("head") != head_net:
            raise AssertionError("改单号把链头也改了 ⇒ 用例本身坏了")
        if true_iss in prods:
            raise AssertionError("原单号 %s 还在产出单号里 (%s) ⇒ 改坏没生效" % (true_iss, prods))
        if prods != ["ISS-9900"]:
            raise AssertionError("产出单号不是 ['ISS-9900'] (%s) ⇒ 用例本身坏了" % prods)
        # ★自证: 这个单号在独立信源里【不存在】⇒ ⇒ 只可能被「独立信源对账」抓出来 ★
        if "ISS-9900" in blocks:
            raise AssertionError("ISS-9900 在独立信源里居然存在 ⇒ 用例本身坏了")
        print("      ★自证: 每一处都改了 ⇒ 链头产出单号 = %s (★台账自洽, 但这个单号在独立信源里不存在★)"
              % prods)
        return work, anchors

    # ---- CJ-3 (红): 每一处都改成一个【真实存在但对不上】的单号 ⇒ 必须红 (★修法 B②★) -----
    def case_cj3():
        work, anchors = fresh_tree(tmp, root, "cj3")
        wrong = pick_real_but_wrong_iss(work, NET, head_net, true_iss)
        p = ledger_path(work)
        base = rd(p)
        broken, hit = break_head_ticket_all(base, NET, bogus=wrong)
        if hit < 1:
            raise AssertionError("没命中链头的落表单号 ⇒ 用例本身坏了")
        wr(p, broken)
        st = gate.sw_ledger_state(NET, broken)
        prods = sorted((st.get("producer") or {}).get(head_net) or [])
        if st.get("head") != head_net:
            raise AssertionError("改单号把链头也改了 ⇒ 用例本身坏了")
        if prods != [wrong]:
            raise AssertionError("产出单号不是 [%s] (%s) ⇒ 用例本身坏了" % (wrong, prods))
        # ★自证: 这个单号【真实存在】(⇒ 不是「查不到」那条红) ⇒ 只能是被【md5 级】对账抓出来 ★
        wb = blocks.get(wrong, "")
        if not wb:
            raise AssertionError("%s 不在独立信源里 ⇒ 用例本身坏了" % wrong)
        if head_net[:12] in wb or head_net[:8] in wb:
            raise AssertionError("%s 的留痕里居然有链头 md5 ⇒ 用例本身坏了" % wrong)
        print("      ★自证: 换成【真实存在】的单号 %s (★独立信源里有它的条目★) ⇒ "
              "它的留痕里有文件名但没有链头 md5 %s ⇒ 只能被【md5 级】交叉核对抓出来"
              % (wrong, head_net[:12]))
        return work, anchors

    cases = [
        ("CJ-1: 链头单号只改一处 (⇒ 台账自相矛盾) ⇒ 必须红", "red:A", case_cj1),
        ("CJ-2: 链头单号改成【不存在的】单号 ⇒ 必须红", "red:B1", case_cj2),
        ("CJ-3: 链头单号换成【真实存在但对不上】的单号 ⇒ 必须红", "red:B2", case_cj3),
        ("CJ-4: 原样不改动 ⇒ 必须绿 (★不许把闸修成永远红★)", "green", case_cj4),
    ]

    ok, bad = 0, 0
    for name, expect, fn in cases:
        work = None
        try:
            work, anchors = fn()
            fails = gate.run_all(work, skip_md5=False, anchor=anchors)
            bak_fails = gate_bak.run_all(work, skip_md5=False, anchor=copy.deepcopy(anchors))
        except AssertionError as exc:
            print("  ❌ %-62s ⇒ 用例本身坏了: %s" % (name, exc))
            bad += 1
            if work:
                shutil.rmtree(work, ignore_errors=True)
            continue
        if expect == "green":
            hit = (not fails)
            exp_txt = "绿 (不许红)"
            extra = ("      ★自证: 原样不动 ⇒ 链头单号 %s 在独立信源里有据可查 ⇒ 绿是挣来的" % true_iss)
        elif expect == "red:A":
            hit = any("落表单号不唯一" in f for f in fails)
            exp_txt = "R6 点名「落表单号不唯一」 (★修法 A★)"
            extra = ""
        elif expect == "red:B1":
            hit = any("落表单号" in f and "查不到" in f for f in fails)
            exp_txt = "R6 点名「独立信源里查不到」 (★修法 B①★)"
            extra = ""
        else:
            hit = any("落表单号" in f and "留痕" in f for f in fails)
            exp_txt = "R6 点名「独立信源里没有这个 md5 的留痕」 (★修法 B②★)"
            extra = ""
        red_txt = fails[:3] if fails else "无"
        print("  %s %-62s 期望 %-30s 实际红项 %s"
              % ("✅" if hit else "❌", name, exp_txt, red_txt))
        if extra:
            print(extra)
        # ★★「不是巧合」的自证 ①: 同一棵被改坏的树, ★修前的判据判【绿】★★
        if expect != "green":
            print("      ★自证: ★同一棵被改坏的树, 修前的判据 (%s) 判 %s ⇒ "
                  "⇒ 这条红【只可能】来自新加的 A/B 交叉核对 ⇒ 不是巧合"
                  % (os.path.basename(BAK), ("★绿 (无红项)★" if not bak_fails else "★红 %s★" % bak_fails[:1])))
            if bak_fails:
                hit = False
        # ★★「不是巧合」的自证 ②: ★每一条红项都必须是新交叉核对的红 (★含「落表单号」★)★★
        #   ⇒ ⇒ 没有别的红项顺带把它带红 ⇒ 红的原因唯一
        # ★注★: 网表与脚表在台账里【共用同一个 §小节标题】⇒ 改那个标题会同时影响两条链
        #   ⇒ 红项数最多两条 (网表一条 + 脚表一条) ⇒ 这是【如实】的, 不是噪声 ★
        if expect != "green":
            unrelated = [f for f in fails if "落表单号" not in f]
            print("      ★自证: 红项 %d 条, 每条都含「落表单号」(★无关红项 %d 条★) ⇒ 红的原因唯一"
                  % (len(fails), len(unrelated)))
            if unrelated:
                hit = False
        if hit:
            ok += 1
        else:
            bad += 1
            print("[FAIL] %s ⇒ 期望 %s · 实际红项 %s" % (name, exp_txt, red_txt))
        shutil.rmtree(work, ignore_errors=True)
    print("-" * 100)
    print("反向用例: %d/%d 通过" % (ok, ok + bad))
    if bad:
        print("[FAIL] 反向用例: %d/%d 通过 (★红项见上面各条 [FAIL] 行★)" % (ok, ok + bad))
    return 0 if bad == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="ISS-312 SW 侧 R6 链头落表单号交叉核对 专项反向用例")
    ap.add_argument("--root", default=PROJ, help="项目根目录 (默认: 脚本所在项目根)")
    ap.add_argument("--tmpdir", default="", help="★临时树根目录 (默认: TMPDIR → 项目 tmp/iss312_tmp → ~/.cache/openclaw-tmp)")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    if not os.path.isfile(os.path.join(root, gate.LEDGER_CANON)):
        print("❌ 找不到判决源落表台账 %s (root=%s)" % (gate.LEDGER_CANON, root))
        return 2
    tmp = _make_tmpdir(args.tmpdir)
    try:
        return run_cases(tmp, root)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
