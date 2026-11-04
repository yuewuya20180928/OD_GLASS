#!/usr/bin/env bash
# v26_arms.sh —— ★**v25 之后的并行实验臂** (2026-11-05 07:45)
# 目的: 一次跑 3 个臂, 用**隔离的 PCB_OUT** (★绝不动官方板), 比"布不动的脚"个数
# ★**纪律**: 一个臂一个写者 (各自 PCB_OUT) ⇒ 官方板只由"赢家轮"落盘
# 用法: bash state/v26_arms.sh
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
RUN=state/v26_runs
mkdir -p "$RUN"

launch() {   # $1=臂名 $2=层数 $3=halo $4=预算倍数 $5=额外env
  local name="$1" L="$2" halo="$3" mult="$4" extra="$5"
  local out="/tmp/v26_${name}.kicad_pcb"
  rm -f "$out" /tmp/v26_${name}.log
  ( cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses && \
    env PCB_LAYERS="$L" PCB_HALO_MARGIN="$halo" PCB_ABUDGET_MULT="$mult" $extra \
        PCB_OUT="$out" timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "/tmp/v26_${name}.log" 2>&1 ; echo "EXIT=$?" >> "/tmp/v26_${name}.log" ) &
  echo "  [臂 $name] PID=$! L=$L halo=$halo mult=$mult out=$out log=/tmp/v26_${name}.log"
}

echo "=== v26 并行实验臂 (07:45) ==="
launch A 8  0.20 6 ""          # ★基线: v25 修复 + 长网先走 (新顺序)
launch B 8  0.15 6 ""          # ★单变量: halo 半径 0.20→0.15 (阻面积 -18%)
launch C 10 0.20 6 ""          # ★单变量: 8层→10层 (信号层 4→5, ★官方载板本来就是 10 层)
echo "=== 三个臂已起 (官方板不动) ==="
