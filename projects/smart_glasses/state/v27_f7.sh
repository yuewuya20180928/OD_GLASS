#!/usr/bin/env bash
# v27_f7.sh —— ★★v27 轮: **F7 排版 (CONN_CAM 钉回 86.8,52.8) × v26 赢家配置** (2026-11-05 09:30)
#
# ★★为什么要有这一轮: v26 四臂量的是 **F5 排版** (CONN_CAM 在"其余"区 (104.8, 59.0))
#   ⇒ 而 v21/v23 参照板里 CONN_CAM 在 (86.8, 52.8) ⇒ 贴近 SoM 下排 P2 ⇒ 差分对走廊短
#   ⇒ placement-only 探针实测: **平均最长距离 60.2 → 57.6mm · >60mm 26 → 23**
#   ⇒ ★**F7 与层数/面积是正交的 ⇒ 必须在赢家配置上再测一次**
#
# ★纪律: 一板一写者 · 每个臂独立 PCB_OUT · 官方板只由"赢家轮"落盘 · 不删别的臂的产物
# 用法:
#   bash state/v27_f7.sh <层数> [板宽 板高 BOT TOP RES]
#   例: bash state/v27_f7.sh 8
#       bash state/v27_f7.sh 8 180 120 "5,58,70,117" "78,5,120,36" "78,38,177,117"
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

L="${1:-8}"
BW="${2:-160}"
BH="${3:-100}"
BOT="${4:-5,58,70,97}"
TOP="${5:-78,5,120,36}"
RES="${6:-78,38,157,97}"

launch() {   # $1=臂名 $2=层数 $3=额外env
  local name="$1" layers="$2" extra="$3"
  local out="/tmp/v27_${name}.kicad_pcb"
  rm -f "$out" "/tmp/v27_${name}.log"
  (
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    env PCB_LAYERS="$layers" PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
        PCB_BOARD_W="$BW" PCB_BOARD_H="$BH" \
        PCB_AREA_BOT="$BOT" PCB_AREA_TOP="$TOP" PCB_AREA_RES="$RES" \
        $extra PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "/tmp/v27_${name}.log" 2>&1
    echo "EXIT=$?" >> "/tmp/v27_${name}.log"
  ) &
  echo "  [v27 臂 $name] PID=$! L=$layers 板=${BW}x${BH} env='$extra' → $out"
}

echo "=== v27 (F7 排版轮) ==="
# ★E = F7 + 赢家层数 + 赢家板型 (主臂) ★F = F7 + 10 层 (若赢家不是 10 层, 顺便再测一次)
# ★★PCB_PAIR_ESCAPE_EXEMPT=1 = ★**差分对 N 侧出脚修复** (09:55 实测根因):
#   SoM BTB 0.4mm pitch ⇒ P/N 出脚直道中心距 0.400mm ⇒ ★**N 侧起点被"伙伴禁入格 + 邻居 halo"封死**
#   ⇒ 22 对里 17~18 对 N 侧 0 段铜 ("N 未通") ⇒ 实测修法: ① N 自己焊盘格豁免 halo
#   ② N 侧出脚改走**反方向** (不与 P 并行) ③ N 侧出脚区豁免伙伴禁入格
launch E "$L" "PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1"
launch F 10  "PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1"
echo "=== v27 两臂已起 (官方板不动) ==="
