#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py — ISS-315 · 硬保护路径【修法 B】专项反向用例
=================================================================================================
★★**这个闸防的是什么** ★ (★ISS-312 已 verified · 但它只堵了【一条路径】★):

  权威判据 `SW/tools/check_demo_panel_spec.py` 有【两条】判【链头落表单号】的路径:

  | 路径 | ISS-312 时的修法 A | ISS-312 时的修法 B | ★ISS-315 之后★ |
  |---|---|---|---|
  | `check_r6_three_way()`  (★落表真源那条★) | 有 | 有 | 有 (★不动★) |
  | `check_r6_hard_protected()` (★硬保护那条★) | 有 | ★**没有** ★ | ★**有** ★ ← ★本单落地★ |

  ⇒ ★修法 B 的定义★: 链头落表单号必须与【独立信源 = `state/issue_log.yaml`】交叉核对
    ① 该单号在 issue_log 里【存在】 ⇒ 假单号 (ISS-9900 之类) 当场露馅
    ② 该单在 issue_log 里的留痕必须提到【这个文件】+【这个链头 md5】
       ⇒ 真实存在但对不上的单号 (★换了另一个真 ISS 号★) 也露馅
  ⇒ ★硬保护路径上【板 md5 合法变更时】不堵 B ⇒ 那条路径会漏放假单号 ★
    (★那正是「板只改一次」那一趟要用的判据★)

★★**本文件装的是【反向用例】, 不是判据** ★
  · 判据在 `SW/tools/check_demo_panel_spec.py` (★本文件只【调用】它, 不复制一份★)
  · ★**每条红用例都带「不是巧合」的自证** ★:
      ① 用例改坏的确实是【硬保护路径上链头那一条记录的落表单号】
      ② ★**同一棵被改坏的树, 修前的判据 (`check_demo_panel_spec.py.bak_iss315`) 判【绿】** ★
         ⇒ ⇒ 这条红【只可能】来自新加的 B ⇒ **不是巧合**
      ③ 红项数 = 1 且每条都含「落表单号」⇒ ⇒ 红的原因唯一 (不是别的红项顺带把它带红的)
  · ★**第 3 / 第 4 条是正向对照 (必须绿)** ⇒ ★不许把闸修成永远红★

★★**用例清单** ★

  | 用例 | 期望 | 场景 | 抓的是哪道 |
  |---|---|---|---|
  | **HP-1** | ★红★ | 硬保护路径链头单号 = 【**不存在**的】单号 ⇒ 台账自洽但单号是假的 | **B①** |
  | **HP-2** | ★红★ | 硬保护路径链头单号 = 【**真实存在但对不上**】的单号 | **B②** |
  | **HP-3** | ★绿★ | 原样不动 ⇒ 必须绿 | (正向对照: 闸没被修成永远红) |
  | **HP-4** | ★绿★ | 合法改板 (★真单号 + 真留痕【文件名 + 改后 md5】★) ⇒ 必须绿 | (正向对照: B 不误伤合法改板) |

★★**沙盒纪律** ★:
  · 全部用例在临时树上跑, ★**真盘一个字节都不写** ★
  · 临时树里带一份 `state/issue_log.yaml` (★真拷·只读★) ⇒ 独立信源就是真的那一份
  · ★**绝对不许硬链接 (hardlink)** ★ (★有一条用例要改板文件★) ⇒ 全部走真拷贝

用法:
    python3 SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py           # rc=0 = 4 条全过
    python3 SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py --root .  # 指定项目根
    python3 SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py --tmpdir /data/tmp
    ★ISS-309 实测坑★: 系统临时目录 (/tmp) 有【每用户配额】⇒ 本脚本自动退回项目内 tmp/iss315_tmp
      (或 `ISS315_TMPDIR` / `TMPDIR` / `~/.cache/openclaw-tmp`) ★
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
BAK = os.path.join(HERE, "check_demo_panel_spec.py.bak_iss315")   # ★修前的判据 (★「不是巧合」自证用★)


# ---------------------------------------------------------------- 判据模块 (★import, 不复制★)
def _load(path: str, name: str):
    loader = importlib.machinery.SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


gate = _load(os.path.join(HERE, "check_demo_panel_spec.py"), "cdps_iss315_gate")
gate_bak = _load(BAK, "cdps_iss315_gate_bak") if os.path.isfile(BAK) else None

BOARD = gate.BOARD_REL
PRO = gate.PRO_REL
NET = gate.LEDGER_REQUIRED[0]


# ---------------------------------------------------------------- 沙盒工具
def _make_tmpdir(explicit: str = "") -> str:
    """★建临时树根目录 ⇒ 系统临时目录配额满了就退回下一个候选 (★ISS-309 实测坑★)."""
    cands = []
    if explicit:
        cands.append(explicit)
    for env in ("ISS315_TMPDIR", "TMPDIR"):
        v = os.environ.get(env) or ""
        if v:
            cands.append(v)
    cands.append(tempfile.gettempdir())
    cands.append(os.path.join(os.path.dirname(PROJ), "tmp", "iss315_tmp"))
    cands.append(os.path.join(os.path.expanduser("~"), ".cache", "openclaw-tmp"))
    last = ""
    for root in cands:
        d = ""
        try:
            os.makedirs(root, exist_ok=True)
            d = tempfile.mkdtemp(prefix="iss315_hp_", dir=root)
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
    for rel in gate.R6_TREE_FILES:
        src = os.path.join(root, rel)
        dst = os.path.join(work, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)                 # ★全拷贝 ⇒ 不用硬链接 (★有用例要改板★)
    return work


def copy_issue_log(work: str, root: str) -> str:
    """把【真 issue_log】拷进临时树 (★只读副本★ ⇒ 独立信源就是真的那一份★)。"""
    dst = os.path.join(work, gate.ISSUE_LOG_REL)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(os.path.join(root, gate.ISSUE_LOG_REL), dst)
    return dst


def rows_for(ticket: str):
    """★台账行工厂: 板一行变更 + `.kicad_pro` 一行「逐字节不变」, 同一单号 ★"""
    def fn(root, base, new, _ticket):
        pro = gate._anchor_base(root, PRO)
        return [gate._row(ticket, BOARD, base, new, "★**是 (★合法改板·板只改一次★)** ★"),
                gate._row(ticket, PRO, pro, pro, "★**否 (★逐字节不变★)** ★")]
    return fn


def excl_for(rel: str) -> set:
    """★硬保护件的【名字别名互斥集】(★口径与权威闸 `check_r6_hard_protected()` 一字不差★)。

    ★为什么要它★: 落表台账里有一行同时写了板与 `.kicad_pro` 的两个 md5 ⇒ 那是【歧义行】
      ⇒ 权威闸算【变更行】时把它剔掉 ⇒ ★这里自证链头时必须用同一口径★ ⇒ 否则链头取不准★
    """
    al = {}
    for r in (BOARD, PRO):
        b = os.path.basename(r)
        al[r] = {r, b, os.path.splitext(b)[1]}
    excl = set()
    for other, s in al.items():
        if other != rel:
            excl |= s
    return excl


def pick_real_but_wrong_iss(root: str, head: str, exclude) -> str:
    """挑一个【真实存在但对不上】的单号 (★HP-2 用★)。

    ★挑选口径★: 该单在 issue_log 里【真实存在】, 且它的留痕里【既没有这个文件名, 也没有这个链头 md5】
      ⇒ ⇒ 新的交叉核对会红在「独立信源里没有 <文件名> 的落表留痕」
      ⇒ ★⇒ 红的原因唯一 (不是「单号不存在」那条)⇒ 证明抓的是【md5 级】的交叉核对★
    """
    blocks = gate.sw_issue_log_entries(root)
    base = os.path.basename(BOARD)
    for iss in sorted(blocks):
        if iss in exclude:
            continue
        ch = blocks[iss]
        if base in ch:
            continue
        if head[:12] in ch or head[:8] in ch:
            continue
        return iss
    raise AssertionError("issue_log 里找不到一个「真实存在但对不上」的单号 ⇒ 用例本身坏了")


# ---------------------------------------------------------------- 用例
def run_cases(tmp: str, root: str) -> int:
    print("=" * 100)
    print("ISS-315 · SW 侧 R6 【硬保护路径 · 链头落表单号交叉核对 (修法 B)】 —— 专项反向用例")
    print("=" * 100)
    print("  判决源台账 = %s (★只读★)" % gate.LEDGER_CANON)
    print("  独立信源   = %s (★main 维护 · 只读 · 与被测对象无关★)" % gate.ISSUE_LOG_REL)
    print("  硬保护件   = %s / %s" % (BOARD, PRO))
    if gate_bak is None:
        print("  ❌ 找不到修前的判据备份 %s ⇒ 「不是巧合」自证做不了" % BAK)
        return 2

    fresh_ticket = gate.sw_fresh_hard_ticket(root)
    if not fresh_ticket:
        print("  ❌ 取不到「从没落过硬保护件」的真单号 ⇒ 反向自测不成立")
        return 2
    print("  ★夹具真单号 = %s (★动态取 · 真 issue_log 里查得到 · 对硬保护件来说是新的★)" % fresh_ticket)

    # ---- HP-1 / HP-2 的底座: 做一次合法改板 (真单号) ⇒ 拿到链头 md5 ----
    probe_work = build_tree(tmp, root, "probe")
    base = gate._anchor_base(probe_work, BOARD)
    pro_base = gate._anchor_base(probe_work, PRO)
    gate._reboard_in_tree(probe_work, rows_fn=rows_for(fresh_ticket), ticket=fresh_ticket)
    head = gate.md5_of(probe_work, BOARD)
    shutil.rmtree(probe_work, ignore_errors=True)
    print("  合法改板后的链头 md5 = %s (★改前 %s★)" % (head[:12], base[:12]))
    print("-" * 100)

    def tree_with_reboard(name: str, ticket: str, trace: bool):
        """★搭一棵树 + 做一次合法改板 (单号 = ticket) + 可选给独立信源补留痕行 ★"""
        work = build_tree(tmp, root, name)
        copy_issue_log(work, root)
        gate._reboard_in_tree(work, rows_fn=rows_for(ticket), ticket=ticket)
        newmd5 = gate.md5_of(work, BOARD)
        if trace:
            gate.sw_sandbox_issue_log(os.path.join(work, gate.ISSUE_LOG_REL), ticket,
                                      [(BOARD, base, newmd5), (PRO, pro_base, pro_base)])
        return work, newmd5

    def case_hp1():
        """HP-1: 链头单号 = 【不存在】的单号 ⇒ 必须红 (★修法 B①★)"""
        work, newmd5 = tree_with_reboard("hp1", "ISS-9900", trace=False)
        blocks = gate.sw_issue_log_entries(work)
        if "ISS-9900" in blocks:
            raise AssertionError("ISS-9900 在独立信源里居然存在 ⇒ 用例本身坏了")
        st = gate.sw_ledger_change_state(BOARD, gate.read_text(work, gate.LEDGER_CANON),
                                         excl_for(BOARD))
        if st.get("head") != newmd5[:12]:
            raise AssertionError("链头取不准 (%s) ⇒ 用例本身坏了" % st.get("head"))
        if st.get("head_iss") != ["ISS-9900"]:
            raise AssertionError("链头产出单号不是 ['ISS-9900'] (%s) ⇒ 用例本身坏了" % st.get("head_iss"))
        print("      ★自证: 链头产出单号 = ['ISS-9900'] (★台账自洽, 但这个单号在独立信源里不存在★)")
        return work

    def case_hp2():
        """HP-2: 链头单号 = 【真实存在但对不上】的单号 ⇒ 必须红 (★修法 B②★)"""
        wrong = pick_real_but_wrong_iss(root, head, exclude={fresh_ticket, "ISS-9900"})
        work, newmd5 = tree_with_reboard("hp2", wrong, trace=False)
        blocks = gate.sw_issue_log_entries(work)
        wb = blocks.get(wrong, "")
        if not wb:
            raise AssertionError("%s 不在独立信源里 ⇒ 用例本身坏了" % wrong)
        if os.path.basename(BOARD) in wb:
            raise AssertionError("%s 的留痕里居然有文件名 ⇒ 用例本身坏了" % wrong)
        if newmd5[:12] in wb or newmd5[:8] in wb:
            raise AssertionError("%s 的留痕里居然有链头 md5 ⇒ 用例本身坏了" % wrong)
        st = gate.sw_ledger_change_state(BOARD, gate.read_text(work, gate.LEDGER_CANON),
                                         excl_for(BOARD))
        if st.get("head_iss") != [wrong]:
            raise AssertionError("链头产出单号不是 [%s] (%s) ⇒ 用例本身坏了" % (wrong, st.get("head_iss")))
        print("      ★自证: 换成【真实存在】的单号 %s (★独立信源里有它的条目★) ⇒ "
              "它的留痕里既没有文件名也没有链头 md5 %s ⇒ 只能被【md5 级】交叉核对抓出来"
              % (wrong, newmd5[:12]))
        return work

    def case_hp3():
        """HP-3: 原样不动 ⇒ 必须绿 (★不许把闸修成永远红★)"""
        work = build_tree(tmp, root, "hp3")
        copy_issue_log(work, root)
        return work

    def case_hp4():
        """HP-4: 合法改板 (★真单号 + 真留痕【文件名 + 改后 md5】★) ⇒ 必须绿"""
        work, newmd5 = tree_with_reboard("hp4", fresh_ticket, trace=True)
        blocks = gate.sw_issue_log_entries(work)
        ch = blocks.get(fresh_ticket, "")
        if os.path.basename(BOARD) not in ch:
            raise AssertionError("留痕行没写进去 ⇒ 用例本身坏了")
        if not (newmd5[:12] in ch or newmd5[:8] in ch):
            raise AssertionError("留痕行里没有改后 md5 ⇒ 用例本身坏了")
        print("      ★自证: 真单号 %s 在独立信源里有条目 · 留痕里有文件名 %s + 改后 md5 %s ⇒ 绿是挣来的"
              % (fresh_ticket, os.path.basename(BOARD), newmd5[:12]))
        return work

    cases = [
        ("HP-1: 硬保护路径链头单号改成【不存在的】单号 ⇒ 必须红", "red:B1", case_hp1),
        ("HP-2: 硬保护路径链头单号换成【真实存在但对不上】的单号 ⇒ 必须红", "red:B2", case_hp2),
        ("HP-3: 原样不改动 ⇒ 必须绿 (★不许把闸修成永远红★)", "green", case_hp3),
        ("HP-4: 合法改板 (真单号 + 真留痕) ⇒ 必须绿 (★B 不误伤合法改板★)", "green", case_hp4),
    ]

    ok, bad = 0, 0
    for name, expect, fn in cases:
        work = None
        try:
            work = fn()
            fails = gate.run_all(work, skip_md5=False)
            bak_fails = gate_bak.run_all(work, skip_md5=False)
        except AssertionError as exc:
            print("  ❌ %-62s ⇒ 用例本身坏了: %s" % (name, exc))
            bad += 1
            if work:
                shutil.rmtree(work, ignore_errors=True)
            continue
        if expect == "green":
            hit = (not fails)
            exp_txt = "绿 (不许红)"
        elif expect == "red:B1":
            hit = any("落表单号" in f and "查不到" in f for f in fails)
            exp_txt = "R6 点名「独立信源里查不到」 (★修法 B①★)"
        else:
            hit = any("落表单号" in f and "留痕" in f for f in fails)
            exp_txt = "R6 点名「独立信源里没有 … 的落表留痕」 (★修法 B②★)"
        red_txt = fails[:3] if fails else "无"
        print("  %s %-62s 期望 %-34s 实际红项 %s"
              % ("✅" if hit else "❌", name, exp_txt, red_txt))
        if expect != "green":
            # ★★「不是巧合」的自证 ①: 同一棵被改坏的树, ★修前的判据判【绿】★★
            print("      ★自证: ★同一棵被改坏的树, 修前的判据 (%s) 判 %s ⇒ "
                  "⇒ 这条红【只可能】来自新加的 B ⇒ 不是巧合"
                  % (os.path.basename(BAK), ("★绿 (无红项)★" if not bak_fails else "★红 %s★" % bak_fails[:1])))
            if bak_fails:
                hit = False
            # ★★「不是巧合」的自证 ②: ★每一条红项都必须含「落表单号」★★ ⇒ 红的原因唯一
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
    ap = argparse.ArgumentParser(description="ISS-315 SW 侧 R6 硬保护路径 修法 B 专项反向用例")
    ap.add_argument("--root", default=PROJ, help="项目根目录 (默认: 脚本所在项目根)")
    ap.add_argument("--tmpdir", default="", help="★临时树根目录 (默认: TMPDIR → 项目 tmp/iss315_tmp → ~/.cache/openclaw-tmp)")
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
