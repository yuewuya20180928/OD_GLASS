#!/usr/bin/env bash
# v59_arms.sh -- ★★**v59 概念: BTB 出脚线宽 0.15mm + ★已修 `_stub_clear` 的 need** (2026-11-06 10:5x)
#
# ★★★★**为什么要有这个臂 (★纯几何推导 + 机器实测双重支持)**:
#   ① 官方板 unc 45 ⇒ G1 要求 unc=0
#   ② ★**两个独立引擎 (自研 A\* / freerouting 2.1.0) 撞同一堵墙** ⇒ 物理约束
#   ③ ★★**根因算出来了 (不是猜)**:
#      SoM BTB = **0.4mm pitch · 0.2mm 宽焊盘** ⇒ 相邻焊盘**中心距 0.4mm**
#      ⇒ 沿排方向出线的需求 = CLEAR 0.20 + 自身半宽 + 对方半宽 0.10
#         · 线宽 **0.20 ⇒ 需 0.4000mm ⇒ ★余量 0.0000mm (卡在临界, 一个纳米都不剩)** ⇒ 实际布不出
#         · 线宽 **0.15 ⇒ 需 0.3750mm ⇒ 余量 0.0250mm** ⇒ ★**可行**
#         · 线宽 0.10 ⇒ 需 0.3500mm ⇒ 余量 0.0500mm ⇒ 可行
#      ★★**0.15mm = 6mil = 行业标准最小线宽** ⇒ ★**板厂几乎都能做**
#      (★FAB_ORDER_NOTES.md 现在写 0.20mm ⇒ 改 0.15mm 只需跟板厂说一声)
#   ④ ★**为什么 P 通 N 不通 (机制, 顺序依赖)**:
#      ★**P 侧靠 "pair-partner 豁免" (`_free` 里 `others == {self.pair_partner}`) 走出去了**
#      ⇒ ★**N 侧再想走时, P 的铜已经在那里 ⇒ 真的堵死** ⇒ ★**不是对称的**
#
# ★★**本臂 = v57 + ★★`_stub_clear` 的 need 修正 (0.299 → 0.275)**
#   ★**v57 是用旧代码跑的 (need 还是硬编码 0.299) ⇒ 成绩偏保守**
#   ★**实测症状**: v57 把官方能通的 `CSI_D0_CK_P/N` 跑成了 N 未通
#   ★**修正后 (need=0.275) ⇒ 0.15mm 直道的真实需求 ⇒ ★**CSI_D0_CK 有望也通**
# ★★**其余 env 与官方 v37_R 逐位相同**
#   ★**⇒ A/B 干净** ⇒ ★**能直接归因到"线宽"这一个量**
# ★**注意**: ★**改了板规则才能落 0.15mm 的线** ⇒ ★**本臂出来的板 DRC 可能因 min_width 规则红**
#   ⇒ ★**量的时候按"实际几何净距"判, 而不是按板规则的 min_width**
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

OUT=/tmp/v59_R.kicad_pcb
LOG=/tmp/v59_R.log
if [ -e "$OUT" ] || [ -e "$LOG" ]; then
  echo "  [v59 臂 R] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"
  exit 0
fi

echo "=== v59 臂 R (BTB 出脚线宽 0.15mm + _stub_clear need 修正) ==="
(
  cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
  env PCB_W_MIN=0.15 \
      PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
      PCB_BOARD_W=160 PCB_BOARD_H=100 \
      PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
      PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
      PCB_PAIR_EXEMPT_R=0.0 \
      PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 \
      PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
      PCB_OUT="$OUT" \
      timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$LOG" 2>&1
  echo "EXIT=$?" >> "$LOG"
) &
echo "  [v59 臂 R] PID=$! → $OUT"
echo "=== 已起 (官方板不动) ==="
