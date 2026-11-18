#!/usr/bin/env bash
# v33_arms.sh —— ★**v33 轮: 在 v32 基础上再补一刀 —— 连接器逃逸走廊禁放 GND 下拉孔** (2026-11-05 19:20)
# ★**背景**: v32_R = 过孔 halo 精确几何 (0.825 → 0.625mm) ⇒ 开了栅栏间的 0.75mm 缝
# ★**v33_S = v32_R + `PCB_CONN_GND_ESCAPE="CONN_CAM:4.0"`** ⇒ 单变量 (相对 v32_R)
# ★**为什么这一刀**: `CONN_CAM` 的 GND 下拉孔落在**每个 GND 焊盘正下方 1.2mm**
#   (x=80.4/81.9/83.4/84.9/86.4/87.9, y=52.60) ⇒ ★**把连接器下方 4.3mm 的空带
#   (y 51.85→56.15, x 78..95) 切成一条条 0.75mm 的缝** ⇒ 差分脚逃不出去
#   ⇒ ★**规则**: CONN_CAM 的 GND 下拉孔心到焊盘行的垂直距离 ≥ 4.0mm
#     ⇒ 孔只能往连接器**上方**躲 (y=47.4, 那里是空的) ⇒ ★**逃逸走廊整条让开**
# ★**为什么不对 CONN_LIGHT 用这一刀**: 它上下两侧都被**器件**堵死
#   (电容行 y57.95-59.05 / TP+串阻 y60.95-63.05) ⇒ 挪孔解决不了 ⇒ DSI 侧要另走摆放臂
# ★**风险**: GND 下拉孔改道 ⇒ 可能少几个 GND 孔 ⇒ unconnected 可能 +2~6 ⇒
#   ★**守候器按 Pareto 判 (两项都不许变差 + 至少一项变好) ⇒ 变差就不晋级**
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {   # $1=臂名 $2=层数 $3=额外env
  local name="$1" layers="$2" extra="$3"
  local out="/tmp/v33_${name}.kicad_pcb"
  local log="/tmp/v33_${name}.log"
  if [ -e "$out" ] || [ -e "$log" ]; then
    echo "  [v33 臂 $name] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"
    return 0
  fi
  (
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    env PCB_LAYERS="$layers" PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
        PCB_VIA_HALO_MARGIN=0.0 \
        PCB_BOARD_W=160 PCB_BOARD_H=100 \
        PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
        PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
        PCB_PAIR_EXEMPT_R=0.0 \
        $extra PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "$log" 2>&1
    echo "EXIT=$?" >> "$log"
  ) &
  echo "  [v33 臂 $name] PID=$! L=$layers env='$extra' → $out"
}

echo "=== v33 (v32 + 连接器逃逸走廊禁放 GND 下拉孔) ==="
launch S 8 "PCB_GND_FIRST=1 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0"
echo "=== v33 单臂已起 (官方板不动; 守候器随后挂上) ==="
