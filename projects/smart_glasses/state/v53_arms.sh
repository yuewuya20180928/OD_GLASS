#!/usr/bin/env bash
# v53_arms.sh -- ★**v53 概念: 官方 v37 基线原样 + rip-up 机制 (出脚走廊感知)**
#
# ★★**为什么换基线 (2026-11-06 03:2x 实测)**:
#   · v50_R / v51_R 交卷 ⇒ 闸判 REJECT: DRC 0→1, unconnected 57→64, 零铜 26→29, 净救回 -3
#   · ★★**逐位比对 env 找到了元凶**: v50 相对官方 v37 臂脚本 **多了两个开关**
#       PCB_EDGE_STRICT=1  (板边闸)  +  PCB_VIA_HALO_CENTER=1 (via 光环真圆心)
#     ⇒ ★**这两个开关让"干净基线"本身比官方板差** ⇒ 再好的 rip-up 也被基线拖累
#   · ⇒ ★★**要打赢官方板, 基线必须是官方 v37 的 env 逐位相同** ⇒ 本臂就这么干
#
# ★★**本臂相对官方 v37 只多两个开关, 且它们是"一个机制"**:
#   PCB_RIPUP_ALIVE=1 (rip-up 复活: 成功网不再被跳过)
#   PCB_RIPUP_ESC=1   (出脚走廊感知: 拆掉封死 escape_stub 直道的别网铜)
#   ★★**RIPUP_ESC 只在 RIPUP_ALIVE 的第二遍 (普通网之后) 才够得着** ⇒ 两个开关必须同时开
#
# ★★**不动的**: 层数 8 / ABUDGET_MULT=6 / HALO_MARGIN=0.20 / BOARD 160x100
#   ★**三层区划** / PIN_CONN_CAM=1 / SKIP_PAD_CELLS=1 / PAIR_ESCAPE_EXEMPT=1 / PAIR_EXEMPT_R=0.0
#   ★**GND_FIRST=1 / VIA_HALO_MARGIN=0.0 / CONN_GND_ESCAPE=CONN_CAM:4.0 / KEEPOUT=24.0,56.1,35.6,59.6**
#   ⇒ ★★**除那两个 rip-up 开关外, 与官方 v37 逐位相同** ⇒ ★**任何差异都归因到 rip-up**
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

OUT=/tmp/v53_R.kicad_pcb
LOG=/tmp/v53_R.log
if [ -e "$OUT" ] || [ -e "$LOG" ]; then
  echo "  [v53 臂 R] ★已有产物/日志 ⇒ 不覆盖 (铁律: 不删别人的输出) ⇒ 跳过"
  exit 0
fi

(
  cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
  env PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
      PCB_BOARD_W=160 PCB_BOARD_H=100 \
      PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
      PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
      PCB_PAIR_EXEMPT_R=0.0 \
      PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 \
      PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
      PCB_RIPUP_ALIVE=1 PCB_RIPUP_ESC=1 \
      PCB_OUT="$OUT" \
      timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$LOG" 2>&1
  echo "EXIT=$?" >> "$LOG"
) &
echo "=== v53 臂 R (官方 v37 基线原样 + rip-up 出脚走廊感知) ==="
echo "  [v53 臂 R] PID=$! → $OUT"
echo "=== 已起 (官方板不动) ==="
