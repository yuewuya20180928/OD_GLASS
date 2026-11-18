#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW/tools/check_landing_trace_obligation.py — ISS-315 · 「落表留痕义务」闸 (★N-2 落地★)
=================================================================================================
★★**这道闸判的是什么东西** ★ (★ISS-312 的 need N-2 · ISS-315 做成机器可判★):

  ★**义务 (逐字)**★: ★任何落表单 (★含合法改板★) 都必须在 `state/issue_log.yaml` 里
    留下【文件名 + 新 md5】的留痕 ⇒ ★缺痕迹 ⇒ 判红★ ★[ISS-312 交卷单 B3.4 · N-2]★

  ★**为什么这条义务现在【已经生效】** ★:
    ISS-312 把【修法 B】(链头落表单号 ↔ 独立信源 `state/issue_log.yaml` 交叉核对) 铺到了
    【落表真源那条路径】(`check_r6_three_way()`) ⇒ ★那一侧的义务已经生效★
    ⇒ ★主线重出网表 / 脚表 / BOM 那一趟的单号若不留痕 ⇒ 开工前 SW 闸会红★
    ⇒ ★ISS-315 同单把这条义务做成【一道独立的闸】★ (★原来它只是判据里的一个副作用, 现在它自己也有人看★)

★★**「落表单」怎么认 (★机器可判·不许靠嘴说★)** ★:

  ★**定义**★: 一个 issue_log 条目被当作【落表单】 ⇔ 它是【落表台账里某个受管真源的
    【链头产出单号】】★ (★判决源口径 · ISS-275 / ISS-284 同款★)

  | 受管真源 | 链头口径 | 为什么是它 |
  |---|---|---|
  | `HW/netlist_v1.csv` · `HW/netlist_v1_pins.csv` · `HW/BOM_v1.csv` | 三向口径 (`sw_ledger_state`) | ★台账管理的真源 (★落表链侧★) ★ |
  | `HW/PCB/demo_mainboard.kicad_pcb` · `.kicad_pro` | 变更行口径 (`sw_ledger_change_state` + 别名互斥) | ★硬保护件走【合法改板】通道 (★ISS-284 的 P10★) ⇒ 它的「落表」只有真的改过才算★ |

  ★**为什么不用锚点副本里的单号** ★: ★锚点副本是【历史留痕】 (★ISS-275 起降级★)
    ⇒ ★当前锚点记的是 `e06c1dd63356…/ISS-257`, 而链头已是 `6aee500e60ba…/ISS-302`★
    ⇒ ★按锚点副本判 ⇒ 义务会挂在【一个早就落过表的旧单】上 ⇒ 判据会漂★
    ⇒ ★本闸只认【判决源 = 落表台账链头】★ ★[推算 · 口径与 ISS-275/ISS-284 一致]★

★★**纪律** ★:
  · ★**不许拿 issue_log 自己的副本互证** (★那还是自证★) ⇒ ★真单号必须能在
    `state/issue_log.yaml` 的【真条目】里查到 (★就像 ISS-312 的修法 B★) ★
  · ★**不许硬编码任何单号 / md5 / 文件名** ★ ⇒ ★全部动态取自盘上★
  · ★本闸只读盘上两个文件** (★落表台账 + issue_log★) ⇒ ★不写任何东西★
  · ★**判据本体在 `SW/tools/check_demo_panel_spec.py` 里, 本闸只【调用】它, 不复制一份** ★

用法:
    python3 SW/tools/check_landing_trace_obligation.py             # 主模式: rc=0 = 义务都履行了
    python3 SW/tools/check_landing_trace_obligation.py --selftest  # 反向用例 (≥4 条)
    python3 SW/tools/check_landing_trace_obligation.py --root .    # 指定项目根
"""
from __future__ import annotations

import argparse
import importlib.machinery
import importlib.util
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))          # .../SW/tools
PROJ = os.path.dirname(os.path.dirname(HERE))              # .../<项目库根>


# ---------------------------------------------------------------- 判据模块 (★import, 不复制★)
def _load_gate():
    path = os.path.join(HERE, "check_demo_panel_spec.py")
    loader = importlib.machinery.SourceFileLoader("cdps_landing_trace_gate", path)
    spec = importlib.util.spec_from_loader("cdps_landing_trace_gate", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


gate = _load_gate()

# ★**受管真源清单** ★ (★口径来源: `SW/tools/check_onepass_sw_sync.py` 的 CHAIN_FILES 三件 +
#   权威闸锚点 `hard_protected[]` 两件 ★ · ★不许硬编码 md5 / 单号★)
MANAGED_CHAIN = ("HW/netlist_v1.csv", "HW/netlist_v1_pins.csv", "HW/BOM_v1.csv")
MANAGED_HARD = ("HW/PCB/demo_mainboard.kicad_pcb", "HW/PCB/demo_mainboard.kicad_pro")


def hard_alias_excl(rel: str) -> set:
    """★硬保护件的【名字别名互斥集】 (★口径与权威闸 `check_r6_hard_protected()` 一字不差★)。

    ★为什么★: 落表台账里有一行同时写了板与 `.kicad_pro` 的两个 md5 ⇒ 那是【歧义行】
      ⇒ 权威闸算【变更行】时把它剔掉 ⇒ 本闸必须用同一口径, 否则链头会取不准 ★
    """
    al = {}
    for r in MANAGED_HARD:
        b = os.path.basename(r)
        al[r] = {r, b, os.path.splitext(b)[1]}
    excl = set()
    for other, s in al.items():
        if other != rel:
            excl |= s
    return excl


# ---------------------------------------------------------------- 核心 (★主模式与 --selftest 共用同一条路径★)
def collect_obligations(ledger_text: str) -> list:
    """★把落表台账解析成【义务清单】 ⇒ [{rel, head, iss, kind, prev}] ★

    ★每个条目 = 「一个单号必须为某个文件的某个新 md5 留痕」这条义务 ★
    """
    out: list = []
    for rel in MANAGED_CHAIN:
        st = gate.sw_ledger_state(rel, ledger_text)
        head = st.get("head")
        if not head:
            continue
        chain = st.get("chain") or []
        prev = chain[-2] if len(chain) >= 2 else ""
        for iss in st.get("head_iss") or []:
            out.append({"rel": rel, "head": head, "iss": iss, "kind": "落表真源", "prev": prev})
    for rel in MANAGED_HARD:
        st = gate.sw_ledger_change_state(rel, ledger_text, hard_alias_excl(rel))
        head = st.get("head")
        if not head:
            continue
        chain = st.get("chain") or []
        prev = chain[-2] if len(chain) >= 2 else ""
        for iss in st.get("head_iss") or []:
            out.append({"rel": rel, "head": head, "iss": iss, "kind": "硬保护件·合法改板", "prev": prev})
    return out


def check_obligations(ledger_text: str, entries: dict) -> tuple:
    """★判【落表留痕义务】 ⇒ (红项列表, 说明行列表) ★ (★绿 = 空红项★)"""
    fails: list = []
    notes: list = []
    obs = collect_obligations(ledger_text)
    if not entries:
        return (["落表留痕义务: 独立信源 (%s) 读不到任何条目 ⇒ 无从对账 (fail-closed ⇒ 判红)"
                 % gate.ISSUE_LOG_REL], notes)
    for o in obs:
        rel, head, iss = o["rel"], o["head"], o["iss"]
        base = os.path.basename(rel)
        ch = entries.get(iss)
        if not ch:
            fails.append("落表留痕义务: %s (%s) 的落表单号 %s 在独立信源 (%s) 里查不到 "
                         "⇒ 单号是假的 (★判红★)" % (rel, o["kind"], iss, gate.ISSUE_LOG_REL))
            continue
        if base not in ch:
            fails.append("落表留痕义务: 落表单 %s 在独立信源里没有 %s 的留痕 (★缺文件名★) "
                         "⇒ 落表没有留痕 ⇒ 判红" % (iss, base))
            continue
        if not (head[:12] in ch or head[:8] in ch):
            fails.append("落表留痕义务: 落表单 %s 在独立信源里没有 %s 的【新 md5】%s 的留痕 "
                         "(★缺新 md5 / 只写了改前的值★) ⇒ 判红" % (iss, base, head[:12]))
            continue
        notes.append("✅ %s (%s) ← %s · 链头 %s ⇒ 独立信源里留了【%s + %s】"
                     % (rel, o["kind"], iss, head[:12], base, head[:12]))
    return fails, notes


def run_gate(root: str) -> tuple:
    """★闸的完整入口 (★主模式与 --selftest 走的是同一条路径★) ⇒ (红项, 说明, 义务数)★"""
    ledger_text = gate.read_text(root, gate.LEDGER_CANON)
    entries = gate.sw_issue_log_entries(root)
    obs = collect_obligations(ledger_text)
    fails, notes = check_obligations(ledger_text, entries)
    return fails, notes, len(obs)


# ---------------------------------------------------------------- --selftest (★反向用例★)
def _split_blocks(text: str) -> tuple:
    """★把 issue_log 文本切成 (前缀, 块列表) ★ (★口径照抄权威闸 `sw_issue_log_entries()`★)"""
    marker = "\nissues:"
    i = text.find(marker)
    if i < 0:
        raise AssertionError("issue_log 里找不到 issues: 段")
    rest = text[i + len(marker):]
    lines = rest.splitlines(keepends=True)
    pre: list = []
    pos = 0
    for line in lines:
        if line.startswith("- "):
            break
        pre.append(line)
        pos += 1
    blocks: list = []
    cur: list = []
    for line in lines[pos:]:
        if line.startswith("- "):
            if cur:
                blocks.append("".join(cur))
            cur = [line]
        elif cur:
            cur.append(line)
    if cur:
        blocks.append("".join(cur))
    return text[:i] + marker + "".join(pre), blocks


def _rewrite_block(text: str, iss: str, fn) -> tuple:
    """★把 issue_log 文本里【iss 那一条】的块内容按 fn 改一遍 ⇒ 返回 (新文本, 新块) ★"""
    prefix, blocks = _split_blocks(text)
    hit = 0
    new_block = ""
    for idx, ch in enumerate(blocks):
        m = re.search(r"^\s*(?:-\s*)?id:\s*['\"]?(ISS-\d+)['\"]?\s*$", ch, re.M)
        if not (m and m.group(1) == iss):
            continue
        new_block = fn(ch)
        blocks[idx] = new_block
        hit += 1
        break
    if not hit:
        raise AssertionError("issue_log 里找不到单号 %s ⇒ 用例本身坏了" % iss)
    return prefix + "".join(blocks), new_block


def _selftest(root: str) -> int:
    ledger_text = gate.read_text(root, gate.LEDGER_CANON)
    entries = gate.sw_issue_log_entries(root)
    obs = collect_obligations(ledger_text)
    print("=" * 96)
    print("ISS-315 · 【落表留痕义务闸】 —— 反向用例 (★N-2 落地★)")
    print("=" * 96)
    print("  判决源台账 = %s (★只读★)" % gate.LEDGER_CANON)
    print("  独立信源   = %s (★main 维护 · 只读 · 与被测对象无关★)" % gate.ISSUE_LOG_REL)
    if not obs:
        print("  ❌ 台账里一个落表义务都取不到 ⇒ 反向自测不成立")
        return 2
    o = obs[0]
    rel, head, iss = o["rel"], o["head"], o["iss"]
    base = os.path.basename(rel)
    print("  ★拿第一条义务做用例底座: %s ← %s · 链头 %s (★改前 %s★)"
          % (rel, iss, head[:12], (o.get("prev") or "(无)")[:12]))
    print("-" * 96)

    real_text = open(os.path.join(root, gate.ISSUE_LOG_REL), encoding="utf-8").read()
    tmp = tempfile.mkdtemp(prefix="iss315_lt_", dir=os.path.join(PROJ, "tmp"))
    try:
        def make_tree(name: str, issue_text: str) -> str:
            work = os.path.join(tmp, name)
            os.makedirs(os.path.join(work, "HW"), exist_ok=True)
            os.makedirs(os.path.join(work, "state"), exist_ok=True)
            shutil.copy2(os.path.join(root, gate.LEDGER_CANON),
                         os.path.join(work, gate.LEDGER_CANON))
            with open(os.path.join(work, gate.ISSUE_LOG_REL), "w", encoding="utf-8") as f:
                f.write(issue_text)
            return work

        def check_tree(name: str, issue_text: str):
            work = make_tree(name, issue_text)
            fails, _notes, n = run_gate(work)
            shutil.rmtree(work, ignore_errors=True)
            return fails, n

        # ---- LT-4 (绿): 原样不动 ⇒ 必须绿 ----
        ok0, n0 = check_tree("lt4", real_text)
        print("  %s LT-4 原样不动 ⇒ 必须绿 (★不许把闸修成永远红★)  义务 %d 条 · 红项 %s"
              % ("✅" if not ok0 else "❌", n0, ok0[:2] if ok0 else "无"))

        # ---- LT-1 (红): 缺文件名 ⇒ 必须红 ----
        def drop_name(ch):
            return ch.replace(base, base.replace(".", "_X."))
        t1, b1 = _rewrite_block(real_text, iss, drop_name)
        if base in b1:
            print("  ❌ LT-1 缺文件名 ⇒ 必须红 ⇒ 用例本身坏了 (文件名还在)")
            return 1
        f1, _ = check_tree("lt1", t1)
        hit1 = [x for x in f1 if "缺文件名" in x]

        # ---- LT-2 (红): 缺新 md5 ⇒ 必须红 ----
        def drop_md5(ch):
            return ch.replace(head[:8], head[:7] + "f")
        t2, b2 = _rewrite_block(real_text, iss, drop_md5)
        if head[:12] in b2 or head[:8] in b2:
            print("  ❌ LT-2 缺新 md5 ⇒ 必须红 ⇒ 用例本身坏了 (新 md5 还在)")
            return 1
        f2, _ = check_tree("lt2", t2)
        hit2 = [x for x in f2 if "新 md5" in x]

        # ---- LT-3 (红): md5 写的是【改前】的值 ⇒ 必须红 ----
        prev = (o.get("prev") or "")[:8]
        if not prev:
            print("  ❌ LT-3 md5 写的是改前的值 ⇒ 必须红 ⇒ 用例本身坏了 (取不到改前 md5)")
            return 1

        def to_prev(ch):
            return ch.replace(head[:8], prev)
        t3, b3 = _rewrite_block(real_text, iss, to_prev)
        if head[:12] in b3 or head[:8] in b3:
            print("  ❌ LT-3 md5 写的是改前的值 ⇒ 必须红 ⇒ 用例本身坏了 (新 md5 还在)")
            return 1
        if prev not in b3:
            print("  ❌ LT-3 md5 写的是改前的值 ⇒ 必须红 ⇒ 用例本身坏了 (改前的值没写进去)")
            return 1
        f3, _ = check_tree("lt3", t3)
        hit3 = [x for x in f3 if "新 md5" in x]

        print("-" * 96)
        results = [
            ("LT-1 缺文件名 ⇒ 必须红", hit1, f1),
            ("LT-2 缺新 md5 ⇒ 必须红", hit2, f2),
            ("LT-3 md5 写的是改前的值 ⇒ 必须红", hit3, f3),
        ]
        bad = 0 if not ok0 else 1
        for name, hit, fails in results:
            good = bool(hit) and len(fails) == 1
            print("  %s %-34s 红项 %d 条 · %s"
                  % ("✅" if good else "❌", name, len(fails), (fails[0][:88] if fails else "无")))
            if not good:
                bad += 1
            else:
                print("      ★自证: ★同一棵盘面, 只把【%s】那一条的留痕改坏 ⇒ 别的一切都没动★"
                      % ("文件名" if "LT-1" in name else ("新 md5" if "LT-2" in name else "新 md5 (换成改前的值)")))
                print("      ★自证: LT-4 (原样不动) ⇒ 绿 ⇒ ⇒ 这条红【只可能】来自被改坏的那一处 ⇒ 不是巧合")
        print("-" * 96)
        print("反向用例: %d/4 通过" % (4 - bad))
        if bad:
            print("[FAIL] 反向用例: %d/4 通过 (★红项见上面各条 [FAIL] 行★)" % (4 - bad))
            return 1
        print("✅ 反向用例全抓到 ⇒ 判据真在被读 (★不是把红灯调没 ★)")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="ISS-315 落表留痕义务闸")
    ap.add_argument("--selftest", action="store_true", help="只跑反向自检")
    ap.add_argument("--root", default=PROJ, help="项目根目录 (默认: 脚本所在项目根)")
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    if args.selftest:
        return _selftest(root)

    print("=" * 78)
    print("  ISS-315 · 落表留痕义务闸 (★N-2: 落表单必须在 issue_log 里留【文件名 + 新 md5】★)")
    print("=" * 78)
    ledger_path = os.path.join(root, gate.LEDGER_CANON)
    if not os.path.isfile(ledger_path):
        print("❌ 找不到判决源落表台账 %s (root=%s) ⇒ fail-closed" % (gate.LEDGER_CANON, root))
        return 1
    fails, notes, n = run_gate(root)
    print("  判决源台账 = %s (★只读★)" % gate.LEDGER_CANON)
    print("  独立信源   = %s (★main 维护 · 只读·与被测对象无关★)" % gate.ISSUE_LOG_REL)
    print("  义务条目   = %d 条 (★落表台账里各受管真源的链头产出单号★)" % n)
    for line in notes:
        print("  " + line)
    for f in fails:
        print("  ❌ " + f)
    print("-" * 78)
    if not fails:
        print("  ✅ rc=0: ★★每一条落表义务都在 issue_log 里留了【文件名 + 新 md5】★★")
        return 0
    print("  ❌ rc=1: ★★有落表义务没留痕 (★缺文件名 / 缺新 md5 / 只写了改前的值★)★★")
    return 1


if __name__ == "__main__":
    sys.exit(main())
