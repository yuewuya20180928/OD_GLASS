#!/usr/bin/env bash
# auto_release_if_ready.sh —— ★布线落盘后自动"自验 + 放行" (2026-11-05 06:00)
# 用法: bash state/auto_release_if_ready.sh
# 行为: 若 v15 日志出现 EXIT= 且尚未放行 ⇒ 跑 verify_and_release.sh ⇒ 写留证 ⇒ 推 GitHub ⇒ 打出摘要
#       若还没落盘 ⇒ 只打印一行"还在跑"
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
# ★★2026-11-05 03:25 修: **原来写死 /tmp/gen_v15.log** ⇒ v15 早就有 EXIT= ⇒ 脚本每轮都拿
#   **旧日志**去对**当前板文件**做自验 ⇒ 一直测的是被 8 层实验覆盖的坏板 (343/13) ⇒ 白费 CPU + 误导老板
#   ⇒ 现在: **指针文件** state/.current_gen_log 指向"当前这一轮"的日志 (启动时写)
LOG="$(cat state/.current_gen_log 2>/dev/null || true)"
if [ -z "$LOG" ] || [ ! -f "$LOG" ]; then
  LOG="$(ls -t /tmp/gen_*.log 2>/dev/null | head -1)"
fi
STAMP=state/.auto_release_done
echo "★盯的日志: ${LOG:-<无>}"
echo "=== 机器读数 (board_progress.py) ==="
python3 state/board_progress.py 2>/dev/null
if ! grep -q "EXIT=" "$LOG" 2>/dev/null; then
  echo "还在跑: $(ps -o etime= -C python3.11 2>/dev/null | tail -1 | tr -d ' ') (v15 日志无 EXIT 行)"
  exit 0
fi
if [ -f "$STAMP" ]; then
  echo "已放行过 (stamp $STAMP): $(cat $STAMP)"
  exit 0
fi
echo "★落盘了 ⇒ 开始自验+放行"
bash state/verify_and_release.sh > /tmp/auto_release.log 2>&1
rc=$?
grep -E "DRC violations|unconnected items|C3 DRC|C4 unconnected|check_pcb_nets rc|check_pcb_drc|chain_gate rc|stage_gate rc|缺失|多余" /tmp/auto_release.log | head -24
echo "--- 差分对审计 (前 12 行) ---"
grep -E "缺:|净距=|Δ" /tmp/auto_release.log | head -14
# ★★2026-11-05 03:15 **修 stamp bug**: 之前**无条件盖章 + 无条件打印"已放行"** ⇒
#   一轮 rc=1 的失败自验会盖上"已放行"章 ⇒ 之后永远不会再自验 ⇒ ★**失败就不许盖章**
if [ "$rc" -eq 0 ]; then
  date "+%Y-%m-%dT%H:%M:%S" > "$STAMP"
  echo "✓ 已放行 (verify rc=0)"
else
  rm -f "$STAMP"
  echo "❌ 未通过 (verify rc=$rc) ⇒ ★**不盖章** ⇒ 下一轮会重跑自验 (可重复)"
fi
