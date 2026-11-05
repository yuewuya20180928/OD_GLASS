#!/usr/bin/env bash
# v37_arms.sh —— ★**v37 轮: 治"DSI 侧元件把 CONN_LIGHT 扇出封死"** (2026-11-05 21:50)
# ★**单变量 (vs v36_R)**: 只多一个 `PCB_KEEPOUT="24.0,56.1,35.6,59.6"` ⇒ **env 其余与 v36_R 逐位相同**
# ★**根因 (机器读数)**: v31_Q 的 fail_detail 里 DSI 侧失败脚全是 `stub=true`
#   (CONN_LIGHT.2/5/8/16/18 · J_SOM_P3.63 · R_SEL_D0_N.1 …) ⇒ ★**连起步都出不去**
#   ⇒ 而 DSI 上方/下方被 `TP_CSI_*` / `R_SER_CSI_MCLK` / `R_PU_I2CA_SDA` / AC电容行 占住
# ★**探针已验** (placement-only, 不布线): keepout 24.0,56.1,35.6,59.6
#   ⇒ ★**DSI 上走廊整条空出来** · ★**零掉件** (placement drop = 0) · ★**parity 不变**
# ★**注意**: keep-out 只让**同排**的元件右移, 不会"凭空腾出走廊" ⇒ 所以是"排上带规则"式修复
# ★**代价预期**: 被挪的元件 (TP_CSI_CK_P 等) 位置变了 ⇒ 其逃逸走廊也变了 ⇒ 净效果以实测为准
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {   # $1=臂名 $2=层数 $3=额外env
  local name="$1" layers="$2" extra="$3"
  local out="/tmp/v37_${name}.kicad_pcb"
  local log="/tmp/v37_${name}.log"
  if [ -e "$out" ] || [ -e "$log" ]; then
    echo "  [v37 臂 $name] ★已有产物/日志 ⇒ 不覆盖 (铁律: 不删别人的输出) ⇒ 跳过"
    return 0
  fi
  (
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    env PCB_LAYERS="$layers" PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
        PCB_BOARD_W=160 PCB_BOARD_H=100 \
        PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
        PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
        PCB_PAIR_EXEMPT_R=0.0 \
        $extra PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "$log" 2>&1
    echo "EXIT=$?" >> "$log"
  ) &
  echo "  [v37 臂 $name] PID=$! L=$layers env='$extra' → $out"
}

echo "=== v37 (治 DSI 侧元件封死 CONN_LIGHT 扇出) ==="
launch R 8 "PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 PCB_KEEPOUT=24.0,56.1,35.6,59.6"
echo "=== v37 单臂已起 (官方板不动; 自动晋级守候器随后挂上) ==="
