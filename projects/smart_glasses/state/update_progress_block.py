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
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
WS = os.path.dirname(os.path.dirname(PROJ))          # ~/.openclaw/workspace
MEMORY = os.path.join(WS, "MEMORY.md")
START = "<!-- PROGRESS-BLOCK-START -->"
END = "<!-- PROGRESS-BLOCK-END -->"


def read_facts(path: str | None) -> str:
    if path:
        try:
            return open(path, encoding="utf-8", errors="ignore").read()
        except OSError as e:
            return f"<读不到 {path}: {e}>"
    try:
        r = subprocess.run(
            [sys.executable, os.path.join(HERE, "board_progress.py")],
            cwd=PROJ, capture_output=True, text=True, timeout=300)
        return (r.stdout or "") + (("\n<stderr>\n" + r.stderr) if r.stderr else "")
    except Exception as e:                                    # noqa: BLE001
        return f"<board_progress.py 失败: {e}>"


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
    block = build_block(facts, args.extra)

    if args.dry_run:
        print(block)
        return 0

    if not os.path.exists(MEMORY):
        print(f"✗ 找不到 {MEMORY}", file=sys.stderr)
        return 1
    md = open(MEMORY, encoding="utf-8").read()
    new_md, msg = replace_block(md, block)
    if new_md is md and msg.startswith("✗"):
        print(msg, file=sys.stderr)
        return 1
    tmp = MEMORY + ".tmp_progress"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(new_md)
    os.replace(tmp, MEMORY)
    print(msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
