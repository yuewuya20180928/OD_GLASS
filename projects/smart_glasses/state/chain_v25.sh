#!/usr/bin/env bash
# chain_v25.sh —— ★等 A/B 出数 ⇒ 自动起下一轮 (2026-11-05 06:35)
# 用法: bash state/chain_v25.sh
# 1) 等 /tmp/gen_v23_8l.log 与 /tmp/gen_v24_6l.log 都出现 EXIT=
# 2) 从两份日志抽 "布不动的脚" 数字 ⇒ **层数多的一方赢**
# 3) 起 v25: 赢的层数 + A\*预算×6 + ★新排版(F5+TP贴伙伴) + NPTH 障碍 + In3.Cu 平面 + USB-C 丝印修正
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
LOG8=/tmp/gen_v23_8l.log
LOG6=/tmp/gen_v24_6l.log
OUT=/tmp/chain_v25.log
: > "$OUT"

fail_of() {   # $1=日志 ⇒ 抽 "布不动的脚 N 个"; 没有就回 9999
  local n
  n=$(grep -oE "布不动的脚 [0-9]+" "$1" 2>/dev/null | head -1 | grep -oE "[0-9]+" | head -1)
  echo "${n:-9999}"
}

echo "[$(date '+%H:%M:%S')] 等 A/B 两轮落盘 (8层=$LOG8 / 6层=$LOG6)..." | tee -a "$OUT"
for i in $(seq 1 240); do
  a=$(grep -c "EXIT=" "$LOG8" 2>/dev/null || echo 0)
  b=$(grep -c "EXIT=" "$LOG6" 2>/dev/null || echo 0)
  [ "$a" -ge 1 ] && [ "$b" -ge 1 ] && break
  sleep 30
done
F8=$(fail_of "$LOG8"); F6=$(fail_of "$LOG6")
echo "[$(date '+%H:%M:%S')] A/B 出数: 8层×3 布不动脚=$F8 · 6层×3 布不动脚=$F6" | tee -a "$OUT"
grep -hE "\[SUM \]|布不动的脚|判定|EXIT=" "$LOG8" "$LOG6" 2>/dev/null | tee -a "$OUT"

LAYERS=8
if [ "$F6" != "9999" ] && [ "$F8" = "9999" ]; then LAYERS=6; fi
if [ "$F6" != "9999" ] && [ "$F8" != "9999" ] && [ "$F6" -lt "$F8" ]; then LAYERS=6; fi
echo "[$(date '+%H:%M:%S')] ⇒ 下一轮层数 = $LAYERS (预算×6, 写官方板)" | tee -a "$OUT"

# ★v25: 新排版 + NPTH 障碍 + In3.Cu 平面 + USB-C 丝印修正 + 预算×6
setsid nohup bash -c "cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses && \
  PCB_LAYERS=$LAYERS PCB_ABUDGET_MULT=6 timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
  > /tmp/gen_v25.log 2>&1; echo \"EXIT=\$?\" >> /tmp/gen_v25.log" >/dev/null 2>&1 &
sleep 3
ps -eo pid,etime,args | grep gen_pcb_netlist_board | grep -v grep | tail -2 | tee -a "$OUT"
echo "[$(date '+%H:%M:%S')] v25 已起 (日志 /tmp/gen_v25.log)" | tee -a "$OUT"
