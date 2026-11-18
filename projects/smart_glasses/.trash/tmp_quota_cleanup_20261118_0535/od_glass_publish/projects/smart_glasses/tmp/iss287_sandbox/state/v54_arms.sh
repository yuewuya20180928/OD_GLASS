#!/usr/bin/env bash
# v54_arms.sh -- ★**v54 概念: 代码惰性对照臂 (control)**
#
# ★★**为什么需要这一臂 (2026-11-06 03:5x 兄弟会话独立核验后提的缺口)**:
#   · v53 = 新代码 + 官方 v37 env + rip-up 开 ⇒ ★**若 v53 与官方板有差异, 归因给 rip-up 需要"跑法铁证"**
#   · ★★**只做代码层 diff 不够**: 代码 diff 533 行, 且历史上出现过
#     ★**"开关默认关 ⇒ 惰性" 但实际跑起来不一样** 的坑 (v50/v51: 两个默认关的开关开了 ⇒ 基线变差)
#   · ⇒ ★★**本臂 = 新代码 + 官方 v37 env + rip-up 全关** ⇒ ★**若逐位复现官方板**
#     ⇒ 证明 ★**新代码在官方 env 下跑法惰性** ⇒ ⇒ v53 的任何差异都只能归因到 rip-up
#     ⇒ 若不能复现 ⇒ 还有没门控的改动 ⇒ **归因链断** ⇒ v53 的成绩一律不可采信
#
# ★★**env 与官方 v37 臂脚本逐位相同 (19 条 PCB_* 一个不多一个不少)**
# ★★**代码与 v53 同一份快照 (state/.router_src_v53.py == 当前 state/gen_pcb_routing.py)**
# ★★**只差一个变量: 不开 rip-up (RIPUP_ALIVE / RIPUP_ESC 都不设 ⇒ 默认关)**
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

OUT=/tmp/v54_R.kicad_pcb
LOG=/tmp/v54_R.log
if [ -e "$OUT" ] || [ -e "$LOG" ]; then
  echo "  [v54 臂 R] ★已有产物/日志 ⇒ 不覆盖 (铁律: 不删别人的输出) ⇒ 跳过"
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
      PCB_OUT="$OUT" \
      timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$LOG" 2>&1
  echo "EXIT=$?" >> "$LOG"
) &
echo "=== v54 臂 R (代码惰性对照: 新代码 + 官方 v37 env + 不开 rip-up) ==="
echo "  [v54 臂 R] PID=$! → $OUT"
echo "=== 已起 (官方板不动) ==="
