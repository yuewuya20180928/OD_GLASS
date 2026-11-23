#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss327_paste_registry.py —— ISS-327 · 「重建冻结注册表」这一步的【贴表器】

★为什么要有这个脚本 (★2026-11-23 续做时实测发现的坑★)★
  · 本 SOP 初版写的是「覆盖 L161~L237」⇒ ★**行号会漂**★:
    `SW/tools/check_sw_ref_reachability.py` 在 2026-11-18 16:21 被别的单改过一次 (夹具补全)
    ⇒ 行号只对【某一版】成立 ⇒ ★当天照抄行号 = 当天贴错表★。
  · ⇒ 本脚本一律【按内容锚点定位】: `DESIGNATOR_REGISTRY = (` … `# ★共 N 条★`
  · ⇒ 并且当场做【条数自洽断言】+【非 live token 断言】+【备份】+【打印新旧 md5】。

★它只改一个文件: 传入的 --gate (★默认 SW/tools/check_sw_ref_reachability.py★)
★它只读一个文件: 传入的 --from  (★`--freeze-registry` 的输出落盘★)
★任何一条断言不过 ⇒ ★报错退出 · 一个字节都不写★

★用法 (★板那一趟当天照抄★)★
  python3 logs/iss327/iss327_paste_registry.py \
      --gate SW/tools/check_sw_ref_reachability.py \
      --from logs/<单号>/step2_freeze_registry.out \
      --backup logs/<单号>/check_sw_ref_reachability.py.pre_paste.bak

★加 --dry-run ⇒ 只打印将要贴的内容与断言结果 · 不写文件 (★默认建议先跑一次 dry-run★)
"""
import argparse
import hashlib
import importlib.util
import os
import re
import shutil
import sys

BLOCK_RE = re.compile(r"^DESIGNATOR_REGISTRY = \(\n.*?^\)\n^# ★共 \d+ 条★.*$", re.S | re.M)
TOKEN_RE = re.compile(r'^\s+"([A-Za-z0-9_]+)",$', re.M)
ANCHOR_START = "DESIGNATOR_REGISTRY = ("
ANCHOR_END_RE = re.compile(r"^# ★共 \d+ 条★.*$", re.M)


def md5(p):
    with open(p, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def die(msg, *extra):
    print("★[FAIL] " + msg, flush=True)
    for e in extra:
        print("        " + str(e), flush=True)
    sys.exit(2)


def load_live_refs(gate_path):
    """★从闸脚本自己的函数里取 live 位号 (板 ∪ 网表) ⇒ 判「新表里有没有非 live token」★"""
    d = os.path.dirname(os.path.abspath(gate_path))
    spec = importlib.util.spec_from_file_location(
        "g_paste", os.path.join(d, "check_sw_ref_reachability.py"))
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    root = os.path.abspath(os.path.join(d, "..", ".."))
    br = g.read_board_refs(os.path.join(root, g.BOARD_REL))
    nr = g.read_netlist_refs({"root": root})
    return br | nr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", default="SW/tools/check_sw_ref_reachability.py")
    ap.add_argument("--from", dest="src", required=True,
                    help="`--freeze-registry` 的输出文件")
    ap.add_argument("--backup", default="", help="贴表前的备份落点")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    gate = os.path.abspath(args.gate)
    src = os.path.abspath(args.src)
    if not os.path.isfile(gate):
        die("闸脚本读不到: %s" % gate)
    if not os.path.isfile(src):
        die("freeze 输出读不到: %s" % src)

    old_txt = open(gate, encoding="utf-8").read()
    src_txt = open(src, encoding="utf-8").read()

    # ── ① 内容锚点定位 (★不许用行号★) ────────────────────────────────────
    m_start = re.search(r"^%s$" % re.escape(ANCHOR_START), old_txt, re.M)
    m_end = ANCHOR_END_RE.search(old_txt)
    n_start = len(re.findall(r"^%s$" % re.escape(ANCHOR_START), old_txt, re.M))
    n_end = len(ANCHOR_END_RE.findall(old_txt))
    if n_start != 1:
        die("★锚点「%s」在闸脚本里出现 %d 次 (期望恰好 1 次) ⇒ 闸脚本被改过 ⇒ "
            "【不许瞎贴】⇒ 先人读闸脚本再决定怎么贴" % (ANCHOR_START, n_start))
    if n_end != 1:
        die("★锚点「# ★共 N 条★」在闸脚本里出现 %d 次 (期望恰好 1 次) ⇒ "
            "【不许瞎贴】" % n_end)
    if m_end.start() < m_start.start():
        die("★两个锚点的先后顺序反了 ⇒ 闸脚本被改过 ⇒ 【不许瞎贴】")

    # ── ② 从 freeze 输出里取新块 (★只取一次·不许贪婪匹配★) ──────────────
    m = BLOCK_RE.search(src_txt)
    if not m:
        die("freeze 输出里找不到完整的注册表块 (★期望: `DESIGNATOR_REGISTRY = (` … `)` … "
            "`# ★共 N 条★`★) ⇒ freeze 那一步是不是没跑成功?")
    new_block = m.group(0)
    toks = TOKEN_RE.findall(new_block)
    n_decl = int(re.search(r"^# ★共 (\d+) 条★", new_block, re.M).group(1))
    if len(toks) != n_decl:
        die("★freeze 输出自相矛盾: 实际 token %d 条, 但注释写「共 %d 条」 ⇒ 不贴"
            % (len(toks), n_decl))
    if len(set(toks)) != len(toks):
        die("★freeze 输出里有重复 token ⇒ 不贴")

    # ── ③ 非 live token 断言 (★重建表 ⊆ live(板∪网表)·否则判据被污染★) ──
    try:
        live = load_live_refs(gate)
    except Exception as exc:                                  # noqa: BLE001
        die("live 位号读不出来 ⇒ 不贴 (★原因: %s★)" % exc)
    non_live = [t for t in toks if t not in live]
    if non_live:
        die("★新表里有 %d 个非 live token ⇒ 判据会被污染 ⇒ 不贴: %s"
            % (len(non_live), non_live[:8]))

    # ── ④ 组装新文件内容 (★只换那一整块★) ──────────────────────────────
    new_txt = old_txt[:m_start.start()] + new_block + old_txt[m_end.end():]
    if len(re.findall(r"^%s$" % re.escape(ANCHOR_START), new_txt, re.M)) != 1:
        die("贴完之后锚点数量不对 ⇒ 不写")
    if len(ANCHOR_END_RE.findall(new_txt)) != 1:
        die("贴完之后末尾锚点数量不对 ⇒ 不写")

    print("★锚点: START=行%s END=行%s (★内容锚点定位·不是硬编码行号★)"
          % (old_txt[:m_start.start()].count("\n") + 1,
             old_txt[:m_end.start()].count("\n") + 1))
    print("★新表 token 数 = %d · 与 freeze 输出里的「共 %d 条」一致 ⇒ 是" % (len(toks), n_decl))
    print("★非 live token 数 = 0 ⇒ 判据没被污染")
    print("★贴前 md5 = %s" % md5(gate))
    if args.dry_run:
        print("★--dry-run ⇒ 不写文件 (★去掉它再跑一次才是真贴★)")
        return 0

    if args.backup:
        os.makedirs(os.path.dirname(os.path.abspath(args.backup)), exist_ok=True)
        shutil.copyfile(gate, args.backup)
        print("★备份已落: %s" % args.backup)
    with open(gate, "w", encoding="utf-8") as fh:
        fh.write(new_txt)
    print("★贴完 md5 = %s" % md5(gate))
    print("★贴表只动了 1 个文件 · 板/网表/脚表/BOM 一个字节都没动")
    return 0


if __name__ == "__main__":
    sys.exit(main())
