#!/usr/bin/env bash
# v29_arms.sh —— ★**v29 轮: 差分自短路 + 同点重复过孔 两刀** (2026-11-05 12:30)
# ★**背景 (实测 v28_H, 板已落盘, 机器读数)**:
#   DRC 147 = 65 holes_co_located + 28 clearance + ★21 shorting_items + 19 hole_to_hole + 10 tracks_crossing
#   unconnected 73 · 差分 22 对 / N 未通 12
# ★**21 处短路的物理成因 (用 pcbnew 逐条量出来的, 不是猜)**:
#   · R_SEL_CK_P.1 @ (102.90,5.60) 与 R_SEL_CK_N.1 @ (98.10,5.60) **同一排**
#   · P 侧出脚通道 = **y=6.70 的水平长线 (x 94.95~99.20)**
#   · N 侧出脚 = 从 (98.10,5.60) **往下**走到 y=7.20 的通道
#   ⇒ ★**N 的出脚必然横穿 P 的通道** ⇒ P/N 铜直接叠上 ⇒ KiCad 报 shorting_items
#   ⇒ ★**根因 = 伙伴豁免圈太大**: `build_pair_block(exempt_r=1.20)` 把 N 焊盘周围 1.2mm 全豁免
#     ⇒ ★**N 侧可以从伙伴的铜箔上横穿** ⇒ 修法: `PCB_PAIR_EXEMPT_R` 默认 **0.0**
#       (★只豁免"N 焊盘自己那一格" ⇒ N 能起步, 但不许横穿伙伴铜)
# ★**65 处同点重复过孔的成因**: GND 下拉那一路**直接 board.Add(过孔)**, 同时又塞进 self.vias
#   ⇒ 之后 commit() 又把同一个孔画一遍 ⇒ 板上 453 孔 vs 内存 385 孔 ⇒ 差 68
#   ⇒ 修法: 直接登记进 `_committed` ⇒ commit 跳过
# ★**F8 方向 (下带区 y58→62) 判死**: L 臂 22 对 / N未通 16 (比 H 的 12 还差)
#   ⇒ ★**走廊不是瓶颈**; 且 M 臂直接撞板: CONN_LIGHT.21[GND] ↔ TP_CSI_CK_P.1 间距 0.000mm ⇒ EXIT=1
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {   # $1=臂名 $2=层数 $3=额外env
  local name="$1" layers="$2" extra="$3"
  local out="/tmp/v29_${name}.kicad_pcb"
  rm -f "$out" "/tmp/v29_${name}.log"
  (
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    env PCB_LAYERS="$layers" PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
        PCB_BOARD_W=160 PCB_BOARD_H=100 \
        PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
        PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
        PCB_PAIR_EXEMPT_R=0.0 \
        $extra PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "/tmp/v29_${name}.log" 2>&1
    echo "EXIT=$?" >> "/tmp/v29_${name}.log"
  ) &
  echo "  [v29 臂 $name] PID=$! L=$layers env='$extra' → $out"
}

echo "=== v29 (短路 + 重复孔 两刀) ==="
launch N 8 ""                              # ★**不先布 GND** (H 臂 N未通 12 比 I 的 16 好)
launch O 8 "PCB_GND_FIRST=1"               # ★先布 GND (对照 GND_FIRST 在新修复下的效果)
echo "=== v29 两臂已起 (官方板不动; 自动晋级守候器随后挂上) ==="
