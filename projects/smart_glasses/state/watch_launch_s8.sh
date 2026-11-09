#!/usr/bin/env bash
# ★watch_launch_s8.sh —— 等 v76s3 / v76s4 的路由器进程退出 ⇒ 自动发 v76s8
# (★为什么用看门狗而不是轮询: ★长 exec 会卡住工具通道★)
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
LOG=/tmp/_watch_s8.log
echo "[watch] 起 $(date +%H:%M:%S) · 等 PIDs 39845 / 39939 退出" > "$LOG"
while kill -0 39845 2>/dev/null || kill -0 39939 2>/dev/null; do
  sleep 20
done
echo "[watch] s3/s4 已退出 $(date +%H:%M:%S) ⇒ 发 v76s8" >> "$LOG"
(nohup bash state/v76s8_arms.sh > /tmp/_v76s8.out 2>&1 &) 
sleep 45
echo "[watch] v76s8 已起 $(date +%H:%M:%S)" >> "$LOG"
ps -eo pid,etime,args | grep gen_pcb_netlist_board | grep -v grep | awk '{print $1,$2}' | tr '\n' ' ' >> "$LOG"
echo "" >> "$LOG"
