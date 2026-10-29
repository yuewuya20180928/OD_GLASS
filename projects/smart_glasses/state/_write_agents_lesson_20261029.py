#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 2026-10-29 09:1x 的两个新坑写进 AGENTS.md (插在「僵尸 fixing」之后, 「网关会重启」之前)。

★写文件铁律: 先整体读进内存再写 + 原子写 (tmp + fsync + os.replace)。幂等: 已存在就退出。
"""
from __future__ import annotations

import os
import sys
import tempfile

AG = "/home/yuewuya/.openclaw/workspace/AGENTS.md"
ANCHOR = "### ★ 网关会重启 → 所有在跑的 agent 会话一起死 (2026-10-27 20:0x 实测)"

SECTION = """### ★★★ 手动派活会跟队列 cron 撞车 —— 一个 agent 两个写会话 (2026-10-29 09:1x 实测)

- **现象**: 09:11-09:12 我手动派 ISS-112 (hw-lead) + ISS-113 (sw-lead); **同一分钟, 队列 cron (`ARS45 队列自动派活`, 表达式 `7,37 * * * *`) 也派了同一批** ⇒ 结果 **hw-lead 开 2 个写会话 / sw-lead 开 3 个**。两边 brief 内容不同但**写同一批文件** (HW/CHARGE_BOARD_SPEC.md / BOM_v1.csv / SW/tools/rknn_bench.py …) ⇒ 并发写同一文件 = 截断/互相覆盖。
- **根因 (两个都踩了)**:
  1. cron 的并发检查是 "`sessions_list` 查这个 agent 有没有运行中的会话 → 有就跳过" —— **它查的那一瞬间我的会话还没被登记进列表** ⇒ 两边都认为"这个 agent 空闲"。
  2. cron 的 `sessions_spawn` **报了 "file lock stale" 但实际派成功了** → 它以为失败 → 重试 → **同一 agent 两条会话** (它自己最后发现并 kill 了后起的那条)。
- **铁律**:
  1. ★**手动派活必须走 `advance.py --apply --only <ISS-ID>` 先落 `fixing`** —— cron 只派 `status=open` 的, 落了 fixing 它就不会重复派。**"先派后落"正是重复派的根源。**
  2. ★**手动派活尽量避开 cron 的整点窗口** (队列 cron 在每小时 07 分 / 37 分, GitHub 同步在 13/43 分) —— 我在 09:11-09:12 派活, 正撞 09:07 那轮的尾巴。
  3. ★**spawn 返异常 ≠ 没派出去** —— "file lock stale" / 超时之后可能已经派成功了 ⇒ 派完必须 `subagents list` 核对, 看到多出来的**立刻 kill** (kill 前先看 transcript 有没有 tool_use)。
  4. ★**kill 掉一个写会话后必须查有没有半截写入** —— 用 mtime + 语法检查 (`python3 -c "import ast;ast.parse(open(p).read())"`)。★本例被杀的那条 sw-lead 会话**已经写了一版完整的 `rknn_bench.py` 自动补 calib 修复 (56KB, 语法正常)** ⇒ kill 不等于白干, 先查再决定要不要补做。
  5. ★**被 kill 的 brief 增量要写回 `issue_log.task_brief`** —— 否则下一轮队列派活会丢掉那些增量 (本轮用 `state/_patch_briefs_20261029.py` 把 ISS-111/112/113 的增量写回去了)。
- **★配套铁律: 子 agent 派活必须显式钉模型** —— 默认模型 `MiniMax-M3` **会挂 token plan 上限** (cron 自己查出来的: 10-28 17:19 的失败全是 M3 的 token 上限) ⇒ 我手动派的两条正是用了默认 M3, 日志里直接 `LLM request timed out` + AbortError。⇒ ★**`sessions_spawn` 一律带 `model="minimax/MiniMax-M3.1-Flash"`**。
- **★附带的运维坑: 微信主动推送的 context token 会过期** —— `sendMessage ret=-2 errmsg=prepare failed` 连挂 15+ 次, 根因是 `~/.openclaw/openclaw-weixin/accounts/<acct>.context-tokens.json` 停在 2026-07-21 没刷新 ⇒ **老板在微信上给机器人发一句话就会重新写 token, 主动推送立刻恢复**。注意: **job 本身一直在正常跑**, 只是报告送不到 ⇒ 别把"收不到报告"误判成"任务没跑"。

"""


def main() -> int:
    dry = "--dry-run" in sys.argv
    with open(AG, encoding="utf-8") as f:
        text = f.read()
    if "手动派活会跟队列 cron 撞车" in text:
        print("[skip] AGENTS.md 已含本节")
        return 0
    if ANCHOR not in text:
        print(f"❌ 锚点未找到: {ANCHOR!r}")
        return 2
    idx = text.index(ANCHOR)
    new_text = text[:idx] + SECTION + text[idx:]
    if dry:
        print(f"[dry-run] {len(text)} → {len(new_text)} B")
        return 0
    fd, tmp = tempfile.mkstemp(prefix="AGENTS.md.", suffix=".tmp", dir=os.path.dirname(AG))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(new_text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, AG)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    print(f"✅ AGENTS.md 已原子更新 ({len(text)} → {len(new_text)} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
