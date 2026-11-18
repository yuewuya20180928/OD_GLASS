#!/usr/bin/env bash
# run_board_gen.sh —— ★启动一轮整板生成+布线 (统一入口, 2026-11-05 03:28)
# 用法:
#   bash state/run_board_gen.sh <日志名> [额外环境变量...]
# 例:
#   bash state/run_board_gen.sh v16 PCB_ABUDGET_MULT=3            # 官方板
#   bash state/run_board_gen.sh 180 PCB_ABUDGET_MULT=3 PCB_BOARD_W=180 PCB_BOARD_H=120 PCB_OUT=/tmp/board_180.kicad_pcb
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
NAME="$1"; shift
LOG="/tmp/gen_${NAME}.log"
: > "$LOG"
# ★指针: auto_release_if_ready.sh 盯这个文件 (★别再盯旧日志 ⇒ 之前白测了好几轮坏板)
if [ "${PCB_OUT:-}" = "" ]; then
  echo "$LOG" > state/.current_gen_log
fi
env "$@" timeout 4000 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py > "$LOG" 2>&1
echo "EXIT=$?" >> "$LOG"
echo "✓ 跑完: $LOG"
grep -E "\[SUM |layout_done|\[FAIL" "$LOG" | tail -4
