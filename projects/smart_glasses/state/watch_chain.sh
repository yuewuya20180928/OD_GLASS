#!/usr/bin/env bash
# ★watch_chain.sh —— 臂链看门狗
#   用法: bash state/watch_chain.sh <等待的PID...> -- <要发的臂脚本>
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
LOG=/tmp/_watch_chain.log
PIDS=()
ARM=""
for a in "$@"; do
  if [ "$a" = "--" ]; then ARM=1; continue; fi
  if [ "$ARM" = "1" ]; then ARM_SCRIPT="$a"; else PIDS+=("$a"); fi
done
echo "[chain] $(date +%H:%M:%S) 等 ${PIDS[*]} 退出 ⇒ 发 ${ARM_SCRIPT}" >> "$LOG"
for p in "${PIDS[@]}"; do
  while kill -0 "$p" 2>/dev/null; do sleep 20; done
done
echo "[chain] $(date +%H:%M:%S) 已退出 ⇒ 发 ${ARM_SCRIPT}" >> "$LOG"
(nohup bash "$ARM_SCRIPT" > "/tmp/_$(basename "${ARM_SCRIPT}" .sh | sed 's/_arms//')_$(date +%H%M).out" 2>&1 &)
sleep 50
ps -eo pid,etime,args | grep gen_pcb_netlist_board | grep -v grep | awk '{print $1,$2}' | tr '\n' ' ' >> "$LOG"
echo "" >> "$LOG"
