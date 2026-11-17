#!/usr/bin/env bash
# v36S_arms.sh —— ★**v36 概念第 2 臂: 窄焊盘下拉孔"孔心取焊盘内余量最大的点"**
# ★**概念不变 (v36)**: 窄焊盘的 GND 下拉孔
#   - 臂 R (已跑, 判负): "短边 < 孔径+0.10 ⇒ 禁落孔" ⇒ GND 下拉 176→94 (丢 82 个地) ⇒ 电源支路断
#   - 臂 S (本臂):      ★**窄焊盘照落孔, 只是孔心要正** ⇒ 精确坐标 + 余量分挑点
# ★**单变量 (vs v36_R)**: env 逐位相同, 只有 gen_pcb_routing.py 的代码补丁不同
# ★**补丁依据 (机器读数)**:
#   v35_R 的 DRC 2 (两处违规指同一颗孔 @ (62.700,64.450))
#     ⇒ `U_TEMP.2` 焊盘 0.45x0.30 (短边 0.30 ⇒ Ø0.5 孔**必然**探出铜面 ★**不是错**)
#     ⇒ ★**错在孔心偏心 0.195mm** ⇒ 压住 `U_TEMP.1`(I2C_B_SCL) 逃逸短桩 ⇒ 净距 0.125 ✘
#     ⇒ 焊盘中心 ⇒ 0.2085 ✔ ; ★**吸附 0.25 栅格 (62.95,64.45) ⇒ 0.184 ✘** ⇒ 必须精确坐标
#     ⇒ 候选 (62.895,64.600) ⇒ 净距 **0.3036** ✔ (单测 35/35 PASS)
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {   # $1=臂名
  local name="$1"
  local out="/tmp/v36_${name}.kicad_pcb"
  local log="/tmp/v36_${name}.log"
  if [ -e "$out" ] || [ -e "$log" ]; then
    echo "  [v36 臂 $name] ★已有产物/日志 ⇒ 不覆盖 (铁律: 不删别人的输出) ⇒ 跳过"
    return 0
  fi
  (
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    env PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
        PCB_BOARD_W=160 PCB_BOARD_H=100 \
        PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
        PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
        PCB_PAIR_EXEMPT_R=0.0 \
        PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 \
        PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "$log" 2>&1
    echo "EXIT=$?" >> "$log"
  ) &
  echo "  [v36 臂 $name] PID=$! → $out"
}

echo "=== v36 臂 S (窄焊盘孔心取余量最大的点) ==="
launch S
echo "=== 已起 (官方板不动) ==="
