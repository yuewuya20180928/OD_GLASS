#!/usr/bin/env bash
# sweep_place.sh —— ★排版划分方案扇形搜索 (2026-11-05 07:15)
# 用法: bash state/sweep_place.sh
# 做法: 每组划分跑一次"跳过布线"探针 (≈20 秒) ⇒ 量失败网的平均最长距离 ⇒ 取最优
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
OUT=/tmp/sweep_place.txt
: > "$OUT"

measure() {   # $1=探针板  ⇒ 打印 "平均距离 丢件数"
  timeout 600 bash state/pcbnew_py.sh state/_measure_dist.py "$1" 2>/dev/null | tail -1
}

run_one() {  # $1=名字 $2=BOT $3=TOP $4=RES
  local name="$1" bot="$2" top="$3" res="$4"
  PCB_SKIP_ROUTE=1 PCB_OUT="/tmp/probe_$name.kicad_pcb" \
  PCB_AREA_BOT="$bot" PCB_AREA_TOP="$top" PCB_AREA_RES="$res" \
    timeout 300 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py > "/tmp/probe_$name.log" 2>&1
  local dropped
  dropped=$(grep -c "装不下" "/tmp/probe_$name.log" 2>/dev/null || echo 0)
  local m
  m=$(measure "/tmp/probe_$name.kicad_pcb")
  printf "%-22s BOT=%-18s TOP=%-18s RES=%-18s ⇒ %s (掉件行数 %s)\n" \
      "$name" "$bot" "$top" "$res" "$m" "$dropped" | tee -a "$OUT"
}

run_one "A_base"  "5,58,76,97"        "78,5,157,22"        "78,24,157,97"
run_one "B_tall"  "5,58,76,97"        "78,5,157,32"        "78,34,157,97"
run_one "C_wide"  "5,58,76,97"        "78,5,120,32"        "78,34,157,97"
run_one "D_all"   "5,58,157,97"       "78,5,157,30"        "5,30,157,56"
run_one "E_bot2"  "5,58,76,97"        "78,5,157,26"        "78,28,157,97"
echo "=== 汇总 ==="
cat "$OUT"
