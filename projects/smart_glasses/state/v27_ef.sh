#!/usr/bin/env bash
# v27_ef.sh —— ★**v27 的 E/F 两臂 (F7 + 出脚修复, 160×100 台架板)** (2026-11-05 09:55)
# ★与 G 臂 (180×120 面积变量) 分开写脚本 ⇒ ★**面积是单变量, 不跟层数混在一起**
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {   # $1=臂名 $2=层数
  local name="$1" layers="$2"
  local out="/tmp/v27_${name}.kicad_pcb"
  rm -f "$out" "/tmp/v27_${name}.log"
  (
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    env PCB_LAYERS="$layers" PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
        PCB_BOARD_W=160 PCB_BOARD_H=100 \
        PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
        PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
        PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "/tmp/v27_${name}.log" 2>&1
    echo "EXIT=$?" >> "/tmp/v27_${name}.log"
  ) &
  echo "  [v27 臂 $name] PID=$! L=$layers 板=160x100 F7+出脚修复 → $out"
}

echo "=== v27 E/F (160×100) ==="
launch E 8
launch F 10
echo "=== E/F 已起 ==="
