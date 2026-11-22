#!/usr/bin/env bash
# v29_budget.sh —— ★**v29 轮: A* 预算加倍** (2026-11-05 10:30)
# ★**为什么**: v26 实测 "布不动 66 脚" 里 **22 个是"A* 预算耗尽"** (不是真被堵死)
#   ⇒ ★**预算才是剩下的主要瓶颈之一** ⇒ v29 直接把预算 ×2 试一次
# ★其它全部沿用 v27 赢家配置 (F7 排版 + 出脚修复 + 精确落孔判据)
# 用法: bash state/v29_budget.sh [层数] [预算倍数]
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
L="${1:-8}"
MULT="${2:-12}"

launch() {   # $1=臂名 $2=层数 $3=预算倍数 $4=额外env
  local name="$1" layers="$2" mult="$3" extra="$4"
  local out="/tmp/v29_${name}.kicad_pcb"
  rm -f "$out" "/tmp/v29_${name}.log"
  (
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    env PCB_LAYERS="$layers" PCB_ABUDGET_MULT="$mult" PCB_HALO_MARGIN=0.20 \
        PCB_BOARD_W=160 PCB_BOARD_H=100 \
        PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
        PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
        $extra PCB_OUT="$out" \
        timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "/tmp/v29_${name}.log" 2>&1
    echo "EXIT=$?" >> "/tmp/v29_${name}.log"
  ) &
  echo "  [v29 臂 $name] PID=$! L=$layers 预算×${mult} env='$extra' → $out"
}

echo "=== v29 (预算加倍) ==="
launch J "$L" "$MULT" ""
echo "=== v29 已起 (官方板不动) ==="
