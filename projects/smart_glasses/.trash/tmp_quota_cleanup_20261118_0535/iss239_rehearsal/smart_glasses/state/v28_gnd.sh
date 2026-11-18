#!/usr/bin/env bash
# v28_gnd.sh —— ★**v28 轮: GND 两刀** (2026-11-05 10:27)
# ★**背景 (实测)**: unconnected 83 里 **GND 占 50** ⇒ 25 个 GND 焊盘一根铜都没有
#   ① **落孔判据太保守**: GND 下拉用 halo[2] (0.95mm 半径) 判"能不能放孔"
#      ⇒ 密集器件区一个孔都放不下 ⇒ 已加 `_via_site_ok` (几何精确, 规则没放松)
#   ② **顺序太晚**: GND 下拉排在所有信号/电源之后 ⇒ 焊盘周围的好位置被占光
#      ⇒ 已加 `PCB_GND_FIRST=1` (先落 GND 孔, 信号线绕开)
# ★两臂都带: F7 排版 + 差分对 N 侧出脚修复 + 浮点容差 + 过孔查重
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {   # $1=臂名 $2=层数 $3=额外env
  local name="$1" layers="$2" extra="$3"
  local out="/tmp/v28_${name}.kicad_pcb"
  rm -f "$out" "/tmp/v28_${name}.log"
  (
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    env PCB_LAYERS="$layers" PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
        PCB_BOARD_W=160 PCB_BOARD_H=100 \
        PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
        PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
        $extra PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "/tmp/v28_${name}.log" 2>&1
    echo "EXIT=$?" >> "/tmp/v28_${name}.log"
  ) &
  echo "  [v28 臂 $name] PID=$! L=$layers env='$extra' → $out"
}

echo "=== v28 (GND 两刀) ==="
launch H 8 ""                              # ★只加"精确落孔判据"
launch I 8 "PCB_GND_FIRST=1"               # ★再加"GND 先布"
echo "=== v28 两臂已起 (官方板不动) ==="
