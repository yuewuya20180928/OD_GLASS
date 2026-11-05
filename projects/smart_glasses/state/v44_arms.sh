#!/usr/bin/env bash
# v44_arms.sh -- ★**v44 概念: 通孔净距禁区的圆心改用"真实孔心" (★半径不变)**
#
# ★★**为什么 (2026-11-06 00:3x 机器读)**:
#   · 官方板 v37_R: unconnected 57 / DRC 0
#   · v40_R (只加串阻归位): **55 / DRC 1** ⇒ ★**只差 1 条 DRC** 就能晋级
#   · v41_R (只加 `PCB_VIA_HALO_EXACT=1`): **63 / DRC 0** ⇒ ★**净亏 6 条**!
#   · ★**v41 那个修法多封 11 格/孔 (21 -> 32) ⇒ 走廊被挤 ⇒ 未通暴涨** ⇒ **不是正确方向**
#   · ★**实测违规 (v40_R 唯一一条)**: `Via[GND]@(85.35,13.60)` vs `Track[ID_DETECT_1]`(In6.Cu)
#       端点 (84.95,13.20) 距**真实孔心 0.5657mm < 0.625 违规**
#       ⇒ ★**根因: 禁区圆心用"含孔那格的格心" (85.45,13.70) ⇒ 禁区整体偏 0.1414mm ⇒ 放行擦孔**
#
# ★**本臂的修法**: 圆心 = **真实孔心**, 半径**不变** (★不加 g*sqrt(2)/2 对角余量)
#   ⇒ 单测 (`state/_test_halo_center.py`): 平均封格 **19.6 vs legacy 21.0** (★**反而少 1.4 格**)
#      ⇒ ★**既堵住实测违规, 又不多堵走廊** ⇒ **期望未通 ≤ 55 且 DRC = 0**
#
# ★**单变量 (vs v40_R)**: env 逐位相同, 只多一个 `PCB_VIA_HALO_CENTER=1`
# ★**默认关** ⇒ 与 v40/v37 逐位一致
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {
  local name="$1"
  local out="/tmp/v44_${name}.kicad_pcb"
  local log="/tmp/v44_${name}.log"
  if [ -e "$out" ] || [ -e "$log" ]; then
    echo "  [v44 臂 $name] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"; return 0
  fi
  local pp="R_SEL_D3_P:5.50,3.0;R_SEL_D3_N:7.95,3.0;R_SEL_D2_P:13.10,3.0;R_SEL_D2_N:15.55,3.0"
  pp="$pp;R_SEL_CK_P:20.70,3.0;R_SEL_CK_N:23.15,3.0;R_SEL_D1_P:28.30,3.0;R_SEL_D1_N:30.75,3.0"
  pp="$pp;R_SEL_D0_P:35.90,3.0;R_SEL_D0_N:38.35,3.0"
  (
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    env PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
        PCB_BOARD_W=160 PCB_BOARD_H=100 \
        PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
        PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
        PCB_PAIR_EXEMPT_R=0.0 \
        PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 \
        PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
        PCB_PART_POS="$pp" \
        PCB_VIA_HALO_CENTER=1 \
        PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "$log" 2>&1
    echo "EXIT=$?" >> "$log"
  ) &
  echo "  [v44 臂 $name] PID=$! → $out"
}
echo "=== v44 臂 R (基线=v40 env + PCB_VIA_HALO_CENTER=1) ==="
launch R
echo "=== 已起 (官方板不动) ==="
