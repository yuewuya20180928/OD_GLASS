#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""update_progress_block.py —— 更新 MEMORY.md 顶部的 PROGRESS-BLOCK 实时块。

★**为什么要有这个脚本 (11-05 11:50)**: 之前播报员在会话里用 `sed` 改 MEMORY.md ⇒
  11:20 那轮**直接失败** (`search "PROGRESS-BLOCK" ... failed`) ⇒ MEMORY.md 里的实时块
  停在 11:40 的旧快照 ⇒ 老板看到的和实际差 10 分钟。
  ⇒ ★**改成脚本: 读板面事实 → 整体替换标记之间的内容 → 校验标记之外一个字节都不动**

用法:
  python3 state/update_progress_block.py                 # 自己跑 board_progress.py 取事实
  python3 state/update_progress_block.py --facts FILE    # 从已有文件读事实 (播报脚本用)
  python3 state/update_progress_block.py --dry-run       # 只打印, 不改文件
"""
from __future__ import annotations

import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
WS = os.path.dirname(os.path.dirname(PROJ))          # ~/.openclaw/workspace
MEMORY = os.path.join(WS, "MEMORY.md")
# ★**三份 MEMORY.md (★真值源 + 两份副本; ★改真值源必须一起改 ⇒ 否则同步检查分叉)**
COPIES = [
    os.path.join(WS, "config", "agents", "main", "MEMORY.md"),
    os.path.join(PROJ, "config", "agents", "main", "MEMORY.md"),
]
START = "<!-- PROGRESS-BLOCK-START -->"
END = "<!-- PROGRESS-BLOCK-END -->"


def read_facts(path: str | None) -> str:
    if path:
        try:
            return open(path, encoding="utf-8", errors="ignore").read()
        except OSError as e:
            return f"<读不到 {path}: {e}>"
    # ★★★★2026-11-10 23:5x **超时从 600s 提到 2400s (★实测★)**: ★**九个守卫的 `daily_check --self-test`
    #   实测要 ~14 分钟 ⇒ ⇒ 600s 超时 ⇒ ⇒ 每次刷新进展块都【超时失败】⇒ ⇒ 实时块一直是旧的** ★★
    #   ⇒ ★★**⇒ 顺带: `--facts` 收的是【文件路径】⇒ ★【别把脚本本身当事实源传进去】(★脚本源码里有 `<stderr>` 字面量⇒ 闸门会拒★)** ★★
    # ★★**2026-11-07 01:4x 兄弟实测报出的第四点**: ★**默认路径只跑 `board_progress.py` ⇒ 缺 `[守卫]` 行**
    #   ⇒ ★**老板在实时块里看不到守卫状态 (★今晚刚立了"守卫者也要被守卫")**
    #   ⇒ ★**修在产生点: ★**默认事实源改成 `state/bcast_facts.sh` (★它才是播报用的那一份事实: board_progress + `[守卫]` + 板指纹行)**
    #   ⇒ ★**安全: ★**`bcast_facts.sh` 不回调本脚本 (★已实测确认) ⇒ 无递归风险**
    try:
        r = subprocess.run(
            ["bash", os.path.join(HERE, "bcast_facts.sh")],
            cwd=PROJ, capture_output=True, text=True, timeout=2400)
        if r.returncode != 0:
            return f"<board_progress.py 失败: bcast_facts.sh rc={r.returncode}\n{r.stderr}"
        return r.stdout or ""
    except Exception as e:                                    # noqa: BLE001
        return f"<board_progress.py 失败: {e}>"


# ★★**事实闸门 (★2026-11-07 01:4x 兄弟实测报出的洞: ★**坏输入会被静默写进真值源并报"成功")**
#   现象: `--facts` 指不存在的文件 ⇒ read_facts 返回 "<读不到 ...>" ⇒ 块被冲成一句报错文本,
#         但 replace_block 仍判 "✔ 已更新" 且 main() rc=0; ★**空文件更隐蔽 (块被冲成空的, 连报错字样都没有)**
#   根因: ★**"块能写进去" ≠ "事实是真的"** ⇒ 事实本身没有来源标记, 收方无从怀疑它
#   修法 (★改在产生点, 不靠调用方自觉): ★**facts 不合格 ⇒ 拒绝写 + rc=1**
BAD_PREFIXES = ("<读不到 ", "<board_progress.py 失败", "<stderr>", "<Traceback")


def facts_ok(facts: str) -> tuple[bool, str]:
    """返回 (可否写入, 理由)。★**任何一条不满足 ⇒ 拒绝写入**"""
    if not facts or not facts.strip():
        return False, "facts 为空 ⇒ 拒绝写入 (★空事实会把实时块冲成空块)"
    # ★★**前缀检查 (第一版只有这个 ⇒ 尾部坏输入放行)***
    for pre in BAD_PREFIXES:
        if facts.lstrip().startswith(pre):
            return False, f"facts 以错误前缀开头 ({pre!r}) ⇒ 拒绝写入 (★坏输入不能被当成事实写进真值源)"
    # ★★★**全文子串检查 (★方案 A · 兄弟 01:5x 复现的洞: ★**stderr 与 stdout 同流 ⇒ Traceback 落在【尾部】⇒ 前缀干净 ⇒ 闸门放行**)****
    # ★★★**★"<stderr>" 必须在名单里 (★兄弟 01:55 实测出的最后半步)**: ★**上游把标记写在【尾部】, 下游按【前缀】查 ⇒ 两端各对一半 ⇒ 合起来漏**
    #   ⇒ ★**场景 B: ★**stderr 只是 warning (★不含任何异常类型名) ⇒ 前缀闸看不见 ⇒ `facts_ok()` 返回 True ⇒ ★**"事实带警告"的内容以 rc=0 被写进真值源****
    for bad in ("<stderr>", "Traceback (most recent call last)", "RuntimeError", "SyntaxError", "ModuleNotFoundError", "FileNotFoundError", "KeyError", "AssertionError"):
        if bad in facts:
            return False, f"facts 全文含异常标记 {bad!r} ⇒ 拒绝写入 (★★崩掉的事实不许进真值源; ★**注意: ★**缩水闸挡不住本洞 ⇒ 别拿'两道闸都过了'当已堵**)"
    # ★★★**★未展开的 shell 占位符 (★"来源标记是编的"那一族: ★**贴了 [本轮实跑] 标签, 实际是 `$(...)` 字面量)****
    if "$(" in facts:
        return False, "facts 含未展开的 $(...) 占位符 ⇒ 拒绝写入 (★贴了'实跑'标签但值是命令串 ⇒ 比不贴更糟)"
    if len(facts.strip()) < 40:
        return False, "facts 过短 (<40 字符) ⇒ 拒绝写入 (★典型是空/半截文件)"
    return True, "ok"


def build_block(facts: str, extra: str = "") -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = [START, "", f"★**进展播报 {now}** (机器读数 · 脚本自动生成)", "", "```", facts.rstrip(), "```"]
    if extra.strip():
        body += ["", extra.rstrip()]
    body += ["", END]
    return "\n".join(body)


def replace_block(md: str, block: str) -> tuple[str, str]:
    """返回 (新内容, 说明)。标记之外的内容必须逐字节不变。"""
    if START not in md or END not in md:
        return md, "✗ MEMORY.md 里找不到 PROGRESS-BLOCK 标记 ⇒ 未改动"
    i = md.index(START)
    j = md.index(END) + len(END)
    head, old, tail = md[:i], md[i:j], md[j:]
    new_md = head + block + tail
    # 校验: 标记外的内容一个字节都没动
    if new_md[:i] != md[:i] or new_md[len(head) + len(block):] != md[j:]:
        return md, "✗ 校验失败 (标记外内容被改动) ⇒ 未写入"
    return new_md, f"✔ 已更新 (旧块 {len(old)} 字节 → 新块 {len(block)} 字节)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--facts", default=None, help="事实文件 (默认实时跑 board_progress.py)")
    ap.add_argument("--extra", default="", help="附加文字 (进代码块外)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    facts = read_facts(args.facts)

    # ★★**闸门 (★先判事实合不合格, 再谈写不写) ★★**
    ok, why = facts_ok(facts)
    if not ok:
        print(f"✗ 拒绝写入: {why}", file=sys.stderr)
        print(f"✗ 事实来源: {args.facts or '(默认: board_progress.py)'}", file=sys.stderr)
        print("★**⇒ 实时块保持原样, 未改动**", file=sys.stderr)
        return 1

    block = build_block(facts, args.extra)

    if args.dry_run:
        print(block)
        return 0

    if not os.path.exists(MEMORY):
        print(f"✗ 找不到 {MEMORY}", file=sys.stderr)
        return 1
    md = open(MEMORY, encoding="utf-8").read()
    # ★★**缩水闸 (★"突然缩水"是坏输入的典型特征)**: ★**新块比旧块短于一半 ⇒ 拒绝写 + rc=1**
    try:
        _i = md.index(START); _j = md.index(END)
        _old_len = len(md[_i:_j])
        if _old_len > 0 and len(block) * 2 < _old_len:
            print(f"✗ 拒绝写入: 新块 {len(block)} 字节 < 旧块 {_old_len} 字节的一半 ⇒ 突然缩水 (★典型坏输入)", file=sys.stderr)
            print("★**⇒ 实时块保持原样, 未改动**", file=sys.stderr)
            return 1
    except ValueError:
        pass
    new_md, msg = replace_block(md, block)
    if new_md is md and msg.startswith("✗"):
        print(msg, file=sys.stderr)
        return 1
    tmp = MEMORY + ".tmp_progress"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(new_md)
    os.replace(tmp, MEMORY)
    # ★★**2026-11-07 01:3x 修在产生点 (★兄弟 01:29 实测报出的隐患)**
    #   现象: 本脚本★**只写真值源 MEMORY.md**, 两份副本没跟着写 ⇒ ★**每次刷新实时块都立刻分叉**
    #         ⇒ `state/check_memory_sync.py` 马上报 ❌ ⇒ ★**只能靠别人手工 `cp -f` 补 ⇒ 那是"擦产物"不是修源头**
    #   修法: 写完真值源★**立刻把两份副本同步写过去 (同一份内容, 逐字节同)** ⇒ ★**写完即自洽 ⇒ 不再分叉**
    #   注意: ★**只同步文件, 不跑发布脚本, 不推 GitHub** (★与 `state/publish_github.sh:153/159` 同一做法)
    for copy_path in COPIES:
        if os.path.exists(copy_path):
            shutil.copyfile(MEMORY, copy_path)
        else:
            print(f"⚠ 副本不存在, 跳过: {copy_path}", file=sys.stderr)
    print(msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
