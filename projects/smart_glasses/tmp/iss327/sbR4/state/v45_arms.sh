#!/usr/bin/env bash
# v45_arms.sh -- ★**v45 概念: CONN_LIGHT 的 GND 下拉孔也要躲开差分脚逃逸走廊**
#
# ★★**为什么 (2026-11-06 00:5x 机器读)**:
#   · v40_R 的 62 条失败段 **100%** 落在 "CONN_LIGHT 的 GND 下拉孔栅栏" 1.2mm 内
#   · ★**栅栏实测**: 13 个 GND 孔, 排在 (x=27.70…33.95, y=58.70 与 61.70), x 间距 0.75mm
#       ⇒ **正好卡在 CONN_LIGHT 焊盘行 (y=60.15) 与 AC 电容行 (y=58.60) 之间那 1.55mm 的缝里**
#       ⇒ 把逃逸走廊切成 0.75mm 的条 ⇒ ★**62/62 条失败段全部被它封死**
#   · ★**归属实测**: 这些孔**不是下拉孔**(附近 1.2mm 无 GND 焊盘), 是**缝合孔**
#       —— 但根因是同一件事: **GND 孔落在连接器差分脚的逃逸走廊里**
#   · ★**同一机制 CONN_CAM 已经修过** (`PCB_CONN_GND_ESCAPE=CONN_CAM:4.0`) ⇒ ★**CONN_LIGHT 漏了**
#
# ★**本臂的修法 (纯 env, 零代码改动)**: `PCB_CONN_GND_ESCAPE="CONN_CAM:4.0;CONN_LIGHT:2.0"`
#   ⇒ 规则: 该连接器 GND 焊盘的下拉孔心到**焊盘行**的垂直距离 ≥ MIN ⇒ 孔必须往上/下远躲
#   ⇒ MIN=2.0 ⇒ 孔心距 y=60.15 至少 2.0mm ⇒ **y ≤ 58.15 或 y ≥ 62.15** ⇒ **逃逸走廊整条让开**
#
# ★**单变量 (vs v44 臂)**: env 逐位相同, 只多 `PCB_CONN_GND_ESCAPE` 的第二组
# ★**默认关** ⇒ 与 v44 逐位一致 (机制在 gen_pcb_routing.py, 早已存在, env 门控)
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {
  local name="$1"
  local out="/tmp/v45_${name}.kicad_pcb"
  local log="/tmp/v45_${name}.log"
  if [ -e "$out" ] || [ -e "$log" ]; then
    echo "  [v45 臂 $name] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"; return 0
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
        PCB_CONN_GND_ESCAPE="CONN_CAM:4.0;CONN_LIGHT:2.0" \
        PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
        PCB_PART_POS="$pp" \
        PCB_VIA_HALO_CENTER=1 \
        PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "$log" 2>&1
    echo "EXIT=$?" >> "$log"
  ) &
  echo "  [v45 臂 $name] PID=$! → $out"
}
echo "=== v45 臂 R (v44 env + CONN_LIGHT GND 孔逃逸走廊) ==="
launch R
echo "=== 已起 (官方板不动) ==="
