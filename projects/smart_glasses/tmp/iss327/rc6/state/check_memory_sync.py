#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""state/check_memory_sync.py —— 检查 MEMORY / 日记的**多副本一致性** (2026-11-02 08:2x 新增)

★为什么要有这个 (心跳查出的真缺陷):
  同一份 MEMORY.md 存在**三个副本**, 而"谁是真值源"曾经是分裂的:
    ① `$WS/MEMORY.md`                      —— 项目总工 (我) 一直写的那份
    ② `$WS/config/agents/main/MEMORY.md`   —— ★**运行时真正加载的那份**
    ③ `$PROJ/config/agents/main/MEMORY.md` —— ★**发布树 (GitHub) 里那份**
  ⇒ 我 11-02 凌晨写的 4 条记忆 + 头部基线订正**只进了 ①** ⇒ **运行时读不到, GitHub 也没有**
  ⇒ 且 daily memory 的发布树副本停在 2026-06-11 ⇒ ★**"断电续传凭据"这个机制三个月没生效**
  ⇒ 根因: **同步靠人记得** —— 同 MEMORY 里"哨兵写入点"那一条是同一个病。

★修法: ①真值源 = ①, `publish_github.sh` 在 rsync 前自动同步到 ②③ ②**本脚本当门禁**: 三份不一致就报错
  ⇒ 从此"忘了同步"会**被拦住**, 而不是静默分叉。

用法: python3 state/check_memory_sync.py
"""
from __future__ import annotations

import hashlib
import os
import sys

WS = "/home/yuewuya/.openclaw/workspace"
PROJ = os.path.join(WS, "projects", "smart_glasses")
CANON = os.path.join(WS, "MEMORY.md")
COPIES = [
    os.path.join(WS, "config", "agents", "main", "MEMORY.md"),
    os.path.join(PROJ, "config", "agents", "main", "MEMORY.md"),
]


def h(p: str) -> str:
    try:
        return hashlib.md5(open(p, "rb").read()).hexdigest()
    except OSError:
        return "MISSING"


def main() -> int:
    ok = True
    ref = h(CANON)
    print("=" * 78)
    print("  MEMORY / 日记 多副本一致性门禁")
    print("=" * 78)
    print(f"  真值源  {CANON}\n         md5={ref}")
    for c in COPIES:
        ch = h(c)
        same = (ch == ref)
        print(f"  {'✅' if same else '❌'} 副本 {c}\n         md5={ch}")
        if not same:
            ok = False
    # daily memory: 发布树副本必须含最新日记
    wsm = os.path.join(WS, "config", "agents", "main", "memory")
    pm = os.path.join(PROJ, "config", "agents", "main", "memory")
    if os.path.isdir(wsm):
        newest = max((f for f in os.listdir(wsm) if f.endswith(".md")), default=None)
        if newest:
            p = os.path.join(pm, newest)
            same = os.path.exists(p) and h(os.path.join(wsm, newest)) == h(p)
            print(f"  {'✅' if same else '❌'} 最新日记 {newest} 在发布树副本里")
            if not same:
                ok = False
    print(f"\n  {'✅ 全过' if ok else '❌ 副本已分叉 ⇒ 跑 publish_github.sh 会自动同步, 但先确认真值源正确'}")
    print("=" * 78)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
