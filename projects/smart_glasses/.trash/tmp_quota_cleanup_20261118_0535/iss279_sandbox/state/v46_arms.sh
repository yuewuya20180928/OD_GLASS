#!/usr/bin/env bash
# v46_arms.sh -- ★**v46 概念: GND 下拉孔逃逸规则加"方向" (★只许往下躲)**
#
# ★★**为什么 (2026-11-06 01:2x 机器读)**:
#   · v45 (v44 + `PCB_CONN_GND_ESCAPE="CONN_CAM:4.0;CONN_LIGHT:2.0"`) 实测**打地鼠**:
#     `CSI_D0_CK_P` 从 ok=True 变成 ok=False, 而 `CSI_D0_D0_P` 从 False 变 True
#     ⇒ ★**挪孔只是把拥挤从一处赶到另一处**
#   · ★**根因**: 旧规则是对称的 `abs(via_y - pad_y) >= MIN` ⇒ ★**无法表达"只能往某一边躲"**
#   · ★**CONN_LIGHT 的差分脚是往上逃**: TP 行 y=55.20 / AC 电容行 y=58.60 都在其**上方**,
#     而 SoM P4 (y=50.61..54.39) 挡住垂直通路 ⇒ ★**上方的 GND 孔才拦路, 下方的无害**
#   · ★**栅栏实测**: 15 个孔分两排 —— **y=58.70 (9 个, 拦路)** 与 y=61.70 (5 个, 无害)
#
# ★**本臂的修法 (纯 env, 零代码改动)**: `PCB_CONN_GND_ESCAPE="CONN_CAM:4.0;CONN_LIGHT:1.5:DOWN"`
#   ⇒ 语义: CONN_LIGHT 的 GND 下拉孔**只许往 y 增大方向躲**, 且至少 1.5mm
#   ⇒ 实测 (单测 `state/_test_esc_dir.py`): **上排 9 孔全禁 / 下排 5 孔全留**
#   ⇒ ★**只拆掉拦路那排, 不动无害那排** ⇒ 不像 v45 那样"赶走这排、堵住那排"
#
# ★**单变量 (vs v44 臂)**: env 逐位相同, 只多 `CONN_LIGHT:1.5:DOWN` 的方向后缀
# ★**默认 ANY ⇒ 逐位一致** (代码已 patch, env 门控)
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {
  local name="$1"
  local out="/tmp/v46_${name}.kicad_pcb"
  local log="/tmp/v46_${name}.log"
  if [ -e "$out" ] || [ -e "$log" ]; then
    echo "  [v46 臂 $name] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"; return 0
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
        PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 \
        PCB_CONN_GND_ESCAPE="CONN_CAM:4.0;CONN_LIGHT:1.5:DOWN" \
        PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
        PCB_PART_POS="$pp" \
        PCB_VIA_HALO_CENTER=1 \
        PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "$log" 2>&1
    echo "EXIT=$?" >> "$log"
  ) &
  echo "  [v46 臂 $name] PID=$! → $out"
}
echo "=== v46 臂 R (v44 env + CONN_LIGHT GND 孔只许往下躲) ==="
launch R
echo "=== 已起 (官方板不动) ==="
