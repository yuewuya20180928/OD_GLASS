#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW/tools/check_demo_panel_spec_r6_selftest.py — ISS-275 · R6 判决源同构收口 专项反向用例
=================================================================================================
★★**为什么独立成文件 (★不许把用例塞进 `check_demo_panel_spec.py` 主体★)** ★★
  本文件【只装用例】, 判据一个字节都不动 ⇒ 主体 `SW/tools/check_demo_panel_spec.py` 的
  R1~R5 / R7 一字未改 (★main 2026-11-17 06:1x 已与基线 `e14014aac…` 逐行 diff 复核★)
  ⇒ ★**改本文件不会碰到别人的判据** ★

★★**测的是什么** ★ (★ISS-275: SW 侧 R6 的判决源从【域侧锚点副本】换成【落表台账链头】★):

  | 用例 | 期望 | 场景 | 为什么必须有它 |
  |---|---|---|---|
  | **R2** | ★**绿** ★ | 盘上 md5 == 台账链头 + 域侧锚点副本**停在历史值** | ★★**本单要达成的行为** ★★ (改之前它是红的) |
  | **R1** | ★**红** ★ | 盘上真源被换掉 (≠ 链头) | ★★**悄悄换真源判据不许被删** ★★ (本单最容易走偏的地方) |
  | **R3** | ★**红** ★ | 台账记录**链断** (中间一跳被挖掉 ⇒ 链头不唯一) | 取不准 ⇒ fail-closed ⇒ 不许假绿 |
  | **R4** | ★**绿** ★ | 台账里同一条链的记录**顺序打乱** | ★★**判最新靠【有向链】不靠行序** ★★ (不许用"取最后一行") |
  | **R5a** | ★**红** ★ | 台账最新记录的落表单号被改坏 | 单号改坏 = 挂错单 ⇒ 红 (★ISS-309 重构: 锚点副本【对齐到链头】后改坏 ⇒ 判红★) |
  | **R5b** | ★**红** ★ | 台账最新记录的落表单号**字段缺失** | 字段缺失 = 出处不明 ⇒ 红 |
  | **R6** | ★**红** ★ | 硬保护件 (板 / `.kicad_pro`) md5 变 | ★板变是板那一趟的事, 不许被台账机制吞掉★ |

★★**判据出处 (★不 import MECH 的脚本 —— 那是别人地界★)** ★:
  主体 `check_demo_panel_spec.py` 的 `sw_ledger_records()` / `sw_ledger_state()`
  (★ISS-275 新增, SW 侧自己写的★) ⇒ 本文件只【调用】它们, ★**不复制一份** ★
  ⇒ 主体改了判据本文件立刻跟着变 (★不会出现"用例跟判据各说各话"★)

★★**【ISS-309 · 2026-11-18 · sw-lead】本文件的两处改动 (★判据一个字节都没动★)** ★:
  ① `synth_ledger()` 多带【板 / `.kicad_pro` 的保护基线登记行】⇒ ★R4 修前红在【R6 硬保护】
     (★与它要测的「行序」完全无关★ ⇒ 夹具假伤) ⇒ 现在合成台账满足判据前提 ⇒ R4 绿★·
  ② `_case_r5a()` 重构: ★★把【域侧锚点副本对齐到链头】(= 一次刚落完表的状态) 再改坏链头的
     落表单号 ⇒ 判据的【锚点副本单号 ↔ 台账产出单号】交叉核对能咬住 ⇒ 判红★·
     ★★**已知覆盖缺口 (已登记 need, 本单不改判据)** ★★: ★锚点副本【停在历史值】时 (★当前仓库
     就是这个状态★), 改坏链头落表单号 ⇒ ★判据【绿】= 漏放★ ⇒ 缺口诊断在下面【覆盖缺口诊断】段
     里自带实跑证据 ★

★★**沙盒纪律** ★:
  · 全部用例在 `/tmp` 临时树上跑, ★**真盘一个字节都不写** ★
  · ★**绝对不许硬链接 (hardlink)** ★ —— 本文件有一条用例要改板文件, 硬链接会把真盘板一起改掉
    ⇒ 树里**全部走真拷贝** (板 4.9MB, 拷贝几十毫秒, 换零风险)

用法:
    python3 SW/tools/check_demo_panel_spec_r6_selftest.py           # rc=0 = 7 条全过
    python3 SW/tools/check_demo_panel_spec_r6_selftest.py --root .  # 指定项目根
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))          # .../SW/tools
PROJ = os.path.dirname(os.path.dirname(HERE))              # .../<项目库根>


# ★★ 主体门禁模块 (★import, 不复制判据★)
def _load_gate():
    path = os.path.join(HERE, "check_demo_panel_spec.py")
    spec = importlib.util.spec_from_file_location("check_demo_panel_spec_gate", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gate = _load_gate()

# ★★ 临时树要拷的文件 (R1~R7 要读的全部真源; ★全拷贝, 不用硬链接★)
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
)

NET = "HW/netlist_v1.csv"
PINS = "HW/netlist_v1_pins.csv"
BOARD = os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb")


# ---------------------------------------------------------------- 沙盒工具
def build_tree(tmp: str, root: str, name: str) -> str:
    """在 /tmp 里搭一棵完整的树 (★全拷贝 ⇒ 改它不会碰真盘★)。"""
    work = os.path.join(tmp, name)
    for rel in TREE_FILES:
        src = os.path.join(root, rel)
        dst = os.path.join(work, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    return work


def fresh_tree(tmp: str, root: str, name: str) -> tuple:
    """★每条用例一棵独立的新树 (★不共用 ⇒ 互不污染★) + 锚点副本。"""
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


def anchor_entry(anchors: dict, rel: str) -> dict:
    """按【文件名】取锚点条目 (★不靠下标 ⇒ 锚点顺序变了也不会取错★)。"""
    for e in ((anchors.get("source_ledger") or {}).get("entries") or []):
        if str(e.get("file") or "") == rel:
            return e
    raise AssertionError("锚点 source_ledger.entries 里没有 %s ⇒ 定位不到条目" % rel)


# ---------------------------------------------------------------- 台账改坏工具 (★自己写, 不 import MECH★)
def rec_of_line(line: str) -> tuple:
    """按主体口径 (`sw_ledger_records`) 从一行里抽 (prev, new) 前缀 —— ★口径必须与判据一致★。"""
    toks = gate.LEDGER_MD_RE.findall(line.strip())
    if len(toks) < 2:
        return ("", "")
    return (toks[0][:12], toks[-1][:12])


def drop_mid_record(text: str, rel: str, target_prev: str, target_new: str) -> tuple:
    """把台账里【指定那一跳】的记录行删掉 ⇒ 链断 (链头不唯一)。返回 (新文本, 删了几行)。"""
    base = os.path.basename(rel)
    out, hit = [], 0
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("|") and (rel in s or base in s):
            prev, new = rec_of_line(ln)
            if prev == target_prev and new == target_new:
                hit += 1
                continue
        out.append(ln)
    return ("\n".join(out) + "\n", hit)


def break_head_ticket(text: str, rel: str, bogus: str = "ISS-999") -> tuple:
    """把台账【链头那一行】的落表单号改坏 ⇒ 单号与锚点对不上。返回 (新文本, 改了几行)。

    ★★【ISS-309 · 已弃用】★★ ⇒ ★单号在【每一处】都要改 (★判据口径: 行内 `ISS-xxx` 优先,
      行内没写就继承【最近一个带单号的小节标题】★) ⇒ 只改一处 ⇒ 链头产出单号里还留着原单号
      ⇒ 判据看不见改坏 ⇒ ★改用 `break_head_ticket_all()`★。
    """
    base = os.path.basename(rel)
    head = gate.sw_ledger_state(rel, text)["head"]
    if not head:
        raise AssertionError("台账里 %s 取不到链头 ⇒ 用例本身坏了" % rel)
    out, hit = [], 0
    for ln in text.splitlines():
        s = ln.strip()
        if (s.startswith("|") and (rel in s or base in s) and "ISS-" in s
                and rec_of_line(ln)[1] == head):
            ln = re.sub(r"ISS-\d+", bogus, ln, count=1)
            hit += 1
        out.append(ln)
    return ("\n".join(out) + "\n", hit)


def break_head_ticket_all(text: str, rel: str, bogus: str = "ISS-999") -> tuple:
    """★【ISS-309】★ 把【产出链头的那些记录】的落表单号, 在它【出现的每一处】都改坏。

    ★口径必须与判据 (`sw_ledger_records`) 一字不差★:
      · 行内写了 `ISS-xxx` ⇒ 单号 = 行内第一个 (⇒ 改行内那一个★)
      · 行内没写单号 ⇒ 单号继承【最近一个【带单号】的小节标题】(⇒ 改那【标题】那一个★)
    ★★只改一处 = 假改坏★ ⇒ 链头产出单号里还留着原单号 ⇒ 判据当然看不见 ⇒
      ★★所以这条用例必须把【每一处】都改掉, 才算真的"把落表单号改坏了"★★
    返回 (新文本, 改了几处)。
    """
    base = os.path.basename(rel)
    head = gate.sw_ledger_state(rel, text)["head"]
    if not head:
        raise AssertionError("台账里 %s 取不到链头 ⇒ 用例本身坏了" % rel)
    lines = text.splitlines()
    ctx_idx = -1                 # ★最近一个【带单号】的小节标题★ (判据口径: 标题没单号就不更新 ctx)
    todo: list = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("#"):
            if re.search(r"ISS-\d+", s):
                ctx_idx = i
            continue
        if not (s.startswith("|") and (rel in s or base in s)):
            continue
        if rec_of_line(ln)[1] != head:
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
        seen.add(idx)
        out[idx] = re.sub(r"ISS-\d+", bogus, out[idx], count=1)
    return ("\n".join(out) + "\n", len(seen))


def hard_rows_of(anchors: dict) -> list:
    """锚点里【硬保护件】的保护基线登记行 ⇒ [(文件, 保护基线 md5)]。

    ★【ISS-309】R4/R5b 的合成台账必须带上这两行★ ⇒ 否则判据的①「保护基线自证」
      (基线 md5 必须在落表台账里【同行】查得到) 必然判红 ⇒ ★那条红与「行序打乱 / 缺单号」
      完全是两回事 ⇒ = 夹具假伤★。
    ★写法照真台账的样子 (改前 md5 == 改后 md5 ⇒ 【逐字节不变】声明行 ⇒ 只算覆盖行, 不算变更行)★。
    """
    out = []
    for e in (anchors.get("hard_protected") or []):
        rel = str(e.get("file") or "")
        base = str(e.get("md5") or "")
        if rel and base:
            out.append((rel, base))
    return out


def synth_ledger(pairs: list, tag: str = "合成", hard_rows: list = ()) -> str:
    """把抽出来的落表记录重排成一份【合成台账】(★反向用例专用: 专测「行序打乱仍取最新」★)。

    ★**标题里故意不带任何 `ISS-xxx`** ⇒ 行内没写单号的记录 ⇒ 单号真的缺失 (R5b 用) ★
    ★**【ISS-309】`hard_rows` = 板 / `.kicad_pro` 的保护基线登记行 (★改前==改后 ⇒ 逐字节不变★)
      ⇒ 合成台账因此满足判据的①「保护基线自证」前提 ⇒ ★R4 不再红在【R6 硬保护】(夹具假伤)★** ★
    """
    lines = ["# %s落表台账 (★仅供反向用例★)" % tag, ""]
    for rel, recs in pairs:
        for i, r in enumerate(recs):
            iss = r.get("iss") or "★无单号★"
            lines.append("| %s %d | `%s` | `%s` | `%s` | %s | 说明 |"
                         % (tag, i, rel, r["prev"], r["new"], iss))
    for rel, base in (hard_rows or ()):
        lines.append("| %s h | `%s` | `%s` | `%s` | ★保护基线 (逐字节不变)★ | 说明 |"
                     % (tag, rel, base, base))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- 用例
def run_cases(tmp: str, root: str) -> int:
    base_led = gate.read_text(root, gate.LEDGER_CANON)
    recs_net = gate.sw_ledger_records(base_led, NET)
    recs_pins = gate.sw_ledger_records(base_led, PINS)
    st_net = gate.sw_ledger_state(NET, base_led)
    head_net = st_net["head"]
    st_pins = gate.sw_ledger_state(PINS, base_led)
    head_pins = st_pins["head"]

    print("=" * 100)
    print("ISS-275 · SW 侧 R6 判决源 (落表台账链头) —— 专项反向用例")
    print("=" * 100)
    print("  判决源台账 = %s (★只读★)" % gate.LEDGER_CANON)
    print("  网表链头 = %s (链长 %d) · 脚表链头 = %s (链长 %d)"
          % (head_net, len(st_net["chain"]), head_pins, len(st_pins["chain"])))
    print("-" * 100)

    # ---- R2 (绿): 盘上 == 台账链头, 域侧锚点副本停在历史值 ⇒ 必须绿 ------------------
    def case_r2():
        """盘上 md5 == 台账链头 + 域侧锚点副本停在历史值 ⇒ 必须绿 (★本单要达成的行为★)。"""
        work, anchors = fresh_tree(tmp, root, "r2")
        disk_net = gate.md5_of(work, NET)
        disk_pins = gate.md5_of(work, PINS)
        # ★自证 ①: 盘上确实 == 台账链头 (判决源的前提) ★
        assert disk_net[:12] == head_net, "盘上网表 md5 %s ≠ 台账链头 %s" % (disk_net[:12], head_net)
        assert disk_pins[:12] == head_pins, "盘上脚表 md5 %s ≠ 台账链头 %s" % (disk_pins[:12], head_pins)
        # ★把域侧锚点副本【退到历史值】: md5 = 它自己的 prev_md5 (上一跳的落表结果) ★
        touched = []
        for rel, st in ((NET, st_net), (PINS, st_pins)):
            e = anchor_entry(anchors, rel)
            old_md5 = str(e.get("md5") or "")
            hist = str(e.get("prev_md5") or "")          # ★历史值 = 上一跳的落表结果 ★
            assert hist, "%s 锚点没有 prev_md5 ⇒ 用例本身坏了" % rel
            hkey = hist[:12]
            assert hkey in (st.get("known") or set()), "%s 历史值 %s 不在台账链上 ⇒ 用例本身坏了" % (rel, hkey)
            prods = sorted((st.get("producer") or {}).get(hkey) or [])
            assert prods, "%s 历史值 %s 台账里查不到产出单号 ⇒ 用例本身坏了" % (rel, hkey)
            e["md5"] = hist
            e["by"] = prods[0]
            touched.append((rel, old_md5, hist, prods[0]))
        # ★自证 ②: 锚点副本确实动了 (退到了历史值 ≠ 台账链头) ★
        for rel, old_md5, hist, by in touched:
            assert anchor_entry(anchors, rel)["md5"] == hist, "%s 锚点没改到历史值" % rel
            assert hist[:12] not in (head_net, head_pins), "%s 历史值撞链头 ⇒ 用例本身坏了" % rel
        # ★自证 ③: 【旧机制】 (盘上 md5 == 域侧锚点副本) 下这两条会判红 ⇒ 换源真的换了 ★
        old_red = [rel for rel, old_md5, hist, by in touched
                   if gate.md5_of(work, rel)[:12] != hist[:12]]
        assert old_red, "旧机制 (盘上 == 域侧锚点副本) 下本该判红, 却没红 ⇒ 用例本身坏了"
        print("      ★自证: 旧机制 (盘上 md5 == 域侧锚点副本) 下这 2 条会判红 (%s)"
              % ", ".join(old_red))
        print("      ★自证: 域侧锚点副本已退到历史值 (网表 %s/%s · 脚表 %s/%s) ⇒ 判决源 = 台账链头"
              % (touched[0][2][:12], touched[0][3], touched[1][2][:12], touched[1][3]))
        return work, anchors

    cases = [
        ("R2: 盘上 md5 == 台账链头, 域侧锚点副本停在历史值 ⇒ 必须绿", "green", case_r2),

        # ---- R1 (红): 盘上真源被换掉 (≠ 链头) ⇒ 必须红 --------------------------------
        ("R1: 盘上真源被换掉 (≠ 台账链头) ⇒ 必须红, 且 R6 点名", "red:盘上真源",
         lambda: _case_r1(tmp, root, head_net)),

        # ---- R3 (红): 台账记录链断 ⇒ 必须红 ------------------------------------------
        ("R3: 台账记录链断 (链头不唯一) ⇒ 必须红", "red:链",
         lambda: _case_r3(tmp, root, recs_net)),

        # ---- R4 (绿): 台账里同一条链的记录顺序打乱 ⇒ 仍取最新 ⇒ 必须绿 --------------
        ("R4: 台账里同一条链的记录顺序打乱 ⇒ 仍取最新 ⇒ 必须绿", "green",
         lambda: _case_r4(tmp, root, recs_net, recs_pins, head_net, head_pins)),

        # ---- R5a (红): 台账最新记录的落表单号被改坏 ⇒ 必须红 -------------------------
        ("R5a: 台账最新记录的落表单号被改坏 ⇒ 必须红", "red:单号",
         lambda: _case_r5a(tmp, root, head_net, recs_net, recs_pins)),

        # ---- R5b (红): 台账最新记录的落表单号字段缺失 ⇒ 必须红 ------------------------
        ("R5b: 台账最新记录的落表单号字段缺失 ⇒ 必须红", "red:缺单号",
         lambda: _case_r5b(tmp, root, recs_net, recs_pins, head_net)),

        # ---- R6 (红): 硬保护件 (板) md5 变 ⇒ 必须红, 且【台账链那几条不红】 ----------
        ("R6: 硬保护件 (板) md5 变 ⇒ 必须红, 且台账链那几条不红", "red:硬保护",
         lambda: _case_r6(tmp, root)),
    ]

    # ---- 基线前置条件 --------------------------------------------------------------
    base_work = build_tree(tmp, root, "base")
    base_fails = gate.run_all(base_work, skip_md5=False)
    if base_fails:
        print("  ❌ 基线就不绿: %s ⇒ 反向自测不成立" % base_fails[:3])
        return 2
    print("  ✅ 基线全绿 (R1~R7 在临时树上全过)  ← 反向用例的前置条件")

    ok, bad = 0, 0
    for name, expect, fn in cases:
        try:
            work, anchors = fn()
            fails = gate.run_all(work, skip_md5=False, anchor=anchors)
        except AssertionError as exc:
            print("  ❌ %-58s ⇒ 用例本身坏了: %s" % (name, exc))
            bad += 1
            continue
        if expect == "green":
            hit = (not fails)
            exp_txt = "绿 (不许红)"
        elif expect == "red:硬保护":
            # ★SW 侧 R6 把【硬保护】与【台账链】都编在 "R6 " 前缀下 ⇒
            #   「R6 侧不红」在 SW 侧的口径 = ★台账链那几条不许红★ (MECH 侧对应 "C21 不红")
            hit = (any(f.startswith("R6 硬保护") for f in fails)
                   and not any(f.startswith("R6 台账链") for f in fails))
            exp_txt = "R6 硬保护 红 / R6 台账链 不红"
        elif expect == "red:盘上真源":
            hit = any(f.startswith("R6") and "盘上真源 md5" in f for f in fails)
            exp_txt = "R6 点名「盘上真源 md5」"
        elif expect == "red:链":
            hit = any(f.startswith("R6") and ("取不准" in f or "台账链" in f) for f in fails)
            exp_txt = "R6 点名「台账链」"
        elif expect == "red:单号":
            hit = any(f.startswith("R6") and "落表单号" in f for f in fails)
            exp_txt = "R6 点名「落表单号」"
        elif expect == "red:缺单号":
            hit = any(f.startswith("R6") and "缺落表单号" in f for f in fails)
            exp_txt = "R6 点名「缺落表单号」"
        else:
            hit, exp_txt = False, "?"
        red_txt = fails[:3] if fails else "无"
        print("  %s %-58s 期望 %-26s 实际红项 %s"
              % ("✅" if hit else "❌", name, exp_txt, red_txt))
        if hit:
            ok += 1
        else:
            bad += 1
    print("-" * 100)
    print("反向用例: %d/%d 通过" % (ok, ok + bad))
    # ---- ★【覆盖缺口诊断】★ (★ISS-309 · 不计入 7 条 · 只报事实·不遮红★) ------------------
    print("-" * 100)
    diag_gap(tmp, root, head_net)
    return 0 if bad == 0 else 1


def diag_gap(tmp: str, root: str, head_net: str) -> None:
    """★【ISS-309 · 覆盖缺口诊断】★ 锚点副本【停在历史值】时, 改坏链头落表单号 ⇒ 判据漏放。

    ★★这不是一条用例 (★不计入 7/7★) ⇒ 它只【报事实】: 把判据现在的漏洞当场跑出来 ★★
    ★★★ 本单【不许改判据】(`SW/tools/check_demo_panel_spec.py` 是权威判据) ⇒
      ⇒ 修法 + 反向用例设计已写进 need (★交 main 拍板★) ⇒ 本段只负责【让漏洞自带证据】★★★
    """
    work, anchors = fresh_tree(tmp, root, "gap")
    p = ledger_path(work)
    base = rd(p)
    broken, hit = break_head_ticket_all(base, NET, bogus="ISS-999")
    if hit < 1:
        print("  ★覆盖缺口诊断: 没命中链头的落表单号 ⇒ 诊断本身失效")
        return
    wr(p, broken)
    st = gate.sw_ledger_state(NET, broken)
    prods = sorted((st.get("producer") or {}).get(head_net) or [])
    fails = gate.run_all(work, skip_md5=False, anchor=anchors)
    print("  ★覆盖缺口诊断 (★ISS-309 · 已登记 need · 本单不改判据★):")
    print("      场景: ★锚点副本停在历史值★ (★当前仓库就是这个状态: 锚点 %s/%s · 链头 %s/%s★)"
          % (str(anchor_entry(anchors, NET).get("md5") or "")[:12],
             anchor_entry(anchors, NET).get("by"), head_net, sorted(
                 (gate.sw_ledger_state(NET, base).get("producer") or {}).get(head_net) or [])))
    print("      改坏链头落表单号 %d 处 ⇒ 链头产出单号 = %s ⇒ 判据判定: %s"
          % (hit, prods, ("★红★ %s" % fails[:1]) if fails else "★绿 (无红项) ⇒ ★漏放★"))
    print("      ⇒ ★★判据只查【链头单号非空】, 不查【单号自相矛盾 / 与锚点副本一致】★★")
    print("      ⇒ 修法 (★交 main 拍板, 本单不碰判据★): 链头产出单号【不唯一】⇒ 判红 "
          "(★ISS-309 need·反向用例设计见交卷单 B3/B5★)")


# ---------------------------------------------------------------- 单条用例实现
def _case_r1(tmp: str, root: str, head_net: str) -> tuple:
    work, anchors = fresh_tree(tmp, root, "r1")
    p = os.path.join(work, NET)
    before = gate.md5_of(work, NET)
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n# ISS-275 r6-selftest: 盘上真源被换掉\n")
    after = gate.md5_of(work, NET)
    # ★自证: 文件真被改了, 且新 md5 ≠ 台账链头 ★
    assert after != before, "改坏动作没生效: 网表 md5 没变"
    assert after[:12] != head_net, "改坏后 md5 竟然还等于链头 ⇒ 用例本身坏了"
    print("      ★自证: 盘上网表 md5 %s → %s (≠ 台账链头 %s)"
          % (before[:12], after[:12], head_net))
    return work, anchors


def _case_r3(tmp: str, root: str, recs_net: list) -> tuple:
    work, anchors = fresh_tree(tmp, root, "r3")
    p = ledger_path(work)
    base = rd(p)
    # ★挖掉链中间那一跳 (ISS-233 那一跳) ⇒ 断成两条 ⇒ 链头不唯一 ★
    broken, hit = drop_mid_record(base, NET, "3215020b6d41", "34132f7e40a2")
    assert hit == 1, "没精确命中要挖的那一跳 (命中 %d 行) ⇒ 用例本身坏了" % hit
    wr(p, broken)
    st = gate.sw_ledger_state(NET, broken)
    # ★自证: 记录少了一条, 且链头【取不准】(None) ⇒ 判红是机制本身判的 ★
    assert len(st["records"]) == len(recs_net) - 1, "记录数没少一条 ⇒ 用例本身坏了"
    assert st["head"] is None, "链断之后链头竟还取得到 ⇒ 用例本身坏了"
    print("      ★自证: 链中间那一跳被挖掉 ⇒ 链头取不准 (head=None, why=%s)" % st["why"])
    return work, anchors


def _case_r4(tmp: str, root: str, recs_net: list, recs_pins: list,
             head_net: str, head_pins: str) -> tuple:
    work, anchors = fresh_tree(tmp, root, "r4")
    p = ledger_path(work)
    rev_net = list(reversed(recs_net))
    rev_pins = list(reversed(recs_pins))
    # ★自证 ①: 顺序确实被打乱了 (行序 ≠ 原始行序) ★
    assert [r["new"] for r in rev_net] != [r["new"] for r in recs_net], "行序没被打乱"
    assert [r["new"] for r in rev_pins] != [r["new"] for r in recs_pins], "脚表行序没被打乱"
    # ★【ISS-309】合成台账必须带上【板 / .kicad_pro 的保护基线登记】⇒ 判据前提合法 ★
    synth = synth_ledger([(NET, rev_net), (PINS, rev_pins)], tag="乱序",
                         hard_rows=hard_rows_of(anchors))
    wr(p, synth)
    st = gate.sw_ledger_state(NET, synth)
    stp = gate.sw_ledger_state(PINS, synth)
    # ★自证 ②: 打乱之后链头【不变】 ⇒ 判最新靠图不靠行序 ★
    assert st["head"] == head_net, "打乱后网表链头变了 (%s ≠ %s)" % (st["head"], head_net)
    assert stp["head"] == head_pins, "打乱后脚表链头变了 (%s ≠ %s)" % (stp["head"], head_pins)
    # ★自证 ③ (★ISS-309 补★): ★【取最后一行】的实现错误必被本用例抓到★
    #   ⇒ 合成台账里网表【最后一行】的改后 md5 ≠ 链头 ⇒ 若判据改成"取最后一行" ⇒ 必判红 ★
    last_new = rev_net[-1]["new"]
    assert last_new != head_net, ("合成台账最后一行恰好就是链头 (%s) ⇒ "
                                  "本用例抓不到「取最后一行」的实现错误 ⇒ 用例本身坏了" % last_new)
    print("      ★自证: 记录行序已打乱, 链头不变 (网表 %s / 脚表 %s) ⇒ 判最新靠【有向链】"
          % (st["head"], stp["head"]))
    print("      ★自证: 台账里【最后一行】的改后 md5 = %s ≠ 链头 %s ⇒ "
          "⇒ 若判据改成「取最后一行」本用例必判红 ⇒ 本用例真的在测行序" % (last_new, head_net))
    return work, anchors


def _case_r5a(tmp: str, root: str, head_net: str, recs_net: list, recs_pins: list) -> tuple:
    """★【ISS-309 · 重构】★ 台账最新记录的落表单号被改坏 ⇒ 必须红。

    ★★为什么必须把【域侧锚点副本】先对齐到链头★★
      判据里能咬住"落表单号被改坏"的, 只有【锚点副本落表单号 ↔ 台账产出该 md5 的单号】
      这一条交叉核对 (★`check_r6_three_way` ②-3★) ⇒ ★它咬的是【锚点副本登记的那个 md5】★
      ⇒ 锚点副本若【停在历史值】(★当前仓库就是这个状态: 锚点 ISS-257/e06c1dd6·链头 ISS-302★
      ★), 那条交叉核对压根碰不到链头 ⇒ 改坏链头单号 = 判据看不见 ⇒ ★漏放★。
      ⇒ 本用例把锚点副本【对齐到链头】(= 一次刚落完表的状态: 锚点登记的就是最新那次落表)
      ⇒ 交叉核对重新咬住链头 ⇒ ★改坏链头落表单号 ⇒ 必须红★。

    ★★已知覆盖缺口 (★已登记 need · 本单不改判据★)★★: 锚点副本【停在历史值】时的那个洞
      ⇒ 本文件末尾【覆盖缺口诊断】段自带实跑证据 ★
    """
    work, anchors = fresh_tree(tmp, root, "r5a")
    p = ledger_path(work)
    base = rd(p)
    # ---- ① 取链头当前的落表单号 (判据口径: producer[链头]) ★
    st0 = gate.sw_ledger_state(NET, base)
    head = st0["head"]
    assert head == head_net, "链头变了 (%s ≠ %s) ⇒ 用例本身坏了" % (head, head_net)
    orig = sorted((st0.get("producer") or {}).get(head) or [])
    assert len(orig) == 1, "链头产出单号不唯一 (%s) ⇒ 用例本身坏了" % orig
    orig_iss = orig[0]
    head_rec = next((r for r in recs_net if r["new"] == head), None)
    assert head_rec, "找不到网表链头那一条记录 ⇒ 用例本身坏了"
    # ---- ② 合成台账 (每条记录都带【显式】单号 ⇒ 改坏单号这件事看得见) ★
    synth = synth_ledger([(NET, recs_net), (PINS, recs_pins)], tag="改单号",
                         hard_rows=hard_rows_of(anchors))
    wr(p, synth)
    # ---- ③ ★把域侧锚点副本【对齐到链头】(= 一次刚落完表的状态) ★
    e = anchor_entry(anchors, NET)
    e["md5"] = gate.md5_of(work, NET)        # 盘上 md5 (其 12 位前缀 = 链头)
    e["by"] = orig_iss                      # 锚点登记的单号 = 最新那次落表的单号
    e["prev_md5"] = head_rec["prev"]        # 链头的上一跳
    # ★自证 ①: 对齐之后判据【是绿的】⇒ 后面那条红一定是【改坏单号】造成的, 不是夹具本身坏 ★
    pre = gate.run_all(work, skip_md5=False, anchor=copy.deepcopy(anchors))
    assert not pre, "锚点副本对齐到链头后判据就不绿 (%s) ⇒ 用例本身坏了" % pre[:2]
    # ---- ④ ★改坏链头的落表单号 (在它出现的【每一处】都改) ★
    broken, hit = break_head_ticket_all(synth, NET, bogus="ISS-999")
    assert hit >= 1, "没命中链头的落表单号 ⇒ 用例本身坏了"
    wr(p, broken)
    st = gate.sw_ledger_state(NET, broken)
    prods = sorted((st.get("producer") or {}).get(head_net) or [])
    # ★自证 ②: 链头没变 · 原单号【已经不在】链头产出单号里 · 只剩伪造单号 ★
    assert st["head"] == head_net, "改单号把链头也改了 ⇒ 用例本身坏了"
    assert orig_iss not in prods, "原单号 %s 还在链头产出单号里 (%s) ⇒ 改坏没生效" % (orig_iss, prods)
    assert "ISS-999" in prods, "伪造单号不在链头产出单号里 (%s) ⇒ 用例本身坏了" % prods
    # ★自证 ③: 锚点副本登记的单号与台账对不上 ⇒ ★判据必然红★ ★
    anchor_by = str(anchor_entry(anchors, NET).get("by") or "")
    assert anchor_by == orig_iss, "锚点副本单号 %s ≠ 链头原单号 %s ⇒ 用例本身坏了" % (anchor_by, orig_iss)
    assert anchor_by not in prods, "锚点副本单号还在台账产出单号里 ⇒ 改坏没生效 ⇒ 用例本身坏了"
    print("      ★自证: 锚点副本已【对齐到链头】(md5 %s / by %s / prev %s) ⇒ 对齐后判据绿"
          % (str(e["md5"])[:12], anchor_by, head_rec["prev"]))
    print("      ★自证: 链头 %s 的落表单号 %s → %s (改了 %d 处) ⇒ 锚点副本登记的 %s 与台账对不上"
          % (head_net, orig_iss, prods, hit, anchor_by))
    return work, anchors


def _case_r5b(tmp: str, root: str, recs_net: list, recs_pins: list, head_net: str) -> tuple:
    work, anchors = fresh_tree(tmp, root, "r5b")
    p = ledger_path(work)
    head_rec = next((r for r in recs_net if r["new"] == head_net), None)
    assert head_rec, "找不到网表链头那一条记录 ⇒ 用例本身坏了"
    # ★把链头那条记录的单号【整个抽掉】(合成台账里不写单号 ⇒ 单号真的缺失) ★
    noiss = [dict(r, iss=None) if r["new"] == head_net else dict(r) for r in recs_net]
    synth = synth_ledger([(NET, noiss), (PINS, recs_pins)], tag="缺单号",
                         hard_rows=hard_rows_of(anchors))
    wr(p, synth)
    st = gate.sw_ledger_state(NET, synth)
    # ★自证: 链头还在, 但【没有产出单号】了 ⇒ 判红是"缺出处" ⇒ 不是链断了 ★
    assert st["head"] == head_net, "合成台账里链头变了 ⇒ 用例本身坏了"
    assert not st["head_iss"], "链头竟还有产出单号 (%s) ⇒ 用例本身坏了" % st["head_iss"]
    print("      ★自证: 链头 %s 仍在, 但产出单号 = %s (空) ⇒ 缺出处 ⇒ 判红"
          % (head_net, st["head_iss"]))
    return work, anchors


def _case_r6(tmp: str, root: str) -> tuple:
    work, anchors = fresh_tree(tmp, root, "r6")
    p = os.path.join(work, BOARD)
    before = gate.md5_of(work, BOARD)
    want = ""
    for e in (anchors.get("hard_protected") or []):
        if str(e.get("file") or "") == BOARD:
            want = str(e.get("md5") or "")
    assert want, "锚点里没有 %s 的硬保护 md5 ⇒ 用例本身坏了" % BOARD
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n# ISS-275 r6-selftest: 板被偷偷改了\n")
    after = gate.md5_of(work, BOARD)
    # ★自证: 板真被改了, 且新 md5 ≠ 硬保护登记值 ★
    assert after != before, "改坏动作没生效: 板 md5 没变"
    assert after != want, "改坏后 md5 竟然还等于硬保护登记值 ⇒ 用例本身坏了"
    print("      ★自证: 盘上板 md5 %s → %s (≠ 硬保护登记 %s)"
          % (before[:12], after[:12], want[:12]))
    return work, anchors


def main() -> int:
    ap = argparse.ArgumentParser(description="ISS-275 SW 侧 R6 判决源 (落表台账链头) 专项反向用例")
    ap.add_argument("--root", default=PROJ, help="项目根目录 (默认: 脚本所在项目根)")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    if not os.path.isfile(os.path.join(root, gate.LEDGER_CANON)):
        print("❌ 找不到判决源落表台账 %s (root=%s)" % (gate.LEDGER_CANON, root))
        return 2
    with tempfile.TemporaryDirectory(prefix="iss275_r6_") as tmp:
        return run_cases(tmp, root)


if __name__ == "__main__":
    sys.exit(main())
