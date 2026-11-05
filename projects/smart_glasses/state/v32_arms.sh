#!/usr/bin/env bash
# v32_arms.sh —— ★**v32 轮: 治"连接器差分脚逃逸走廊被过孔 halo 焊死"** (2026-11-05 18:55)
# ★**根因 (机器读数, 非推测)**:
#   ① `CONN_CAM` 的 GND 下拉孔落在**每个 GND 焊盘正下方 1.2mm**
#      (x=80.4/81.9/83.4/84.9/**86.4**/**87.9**, y=52.60) ⇒ 与 0.5mm pitch 的 CSI 脚**交错成栅栏**
#   ② 过孔 halo 半径 = CLEAR 0.20 + VIA_DIA/2 0.30 + W_CLS/2 0.125 + **HALO_MARGIN 0.20** = **0.825mm**
#      ⇒ 栅栏之间唯一通道 (格 x=87.125, 距孔心 0.775mm) 被 halo 判死 ⇒ **通道焊死**
#   ③ ★**真实 DRC 只需要 0.30 + 0.125 + 0.20 = 0.625mm** ⇒ 0.775 > 0.625 ⇒ **通道本来就合法**
#      ⇒ ★**halo 多算了 HALO_MARGIN (0.20)** ⇒ ★**过孔避让半径比 DRC 实际要求保守 0.20mm**
#   ④ 实算: 通道格放行后净距 = 0.775 - 0.30 - 0.125 = **0.35mm ≥ 0.20 ✔**
# ★**受害网 (v31_Q fail_detail 精确失败段)**: CSI_D0_CK_P (只差 **6.4mm** 都布不通!) ·
#   CSI_D0_D0/D1/D2/D3_P/N · CSI_D0_CK_N ⇒ **10 条 "第二跳" (AC电容→CONN_CAM)**
# ★**单变量**: 只加 `PCB_VIA_HALO_MARGIN=0.0` ⇒ **路由器其余逻辑一行没动**
#   ⇒ 默认值 = HALO_MARGIN ⇒ ★**v31_Q 仍可逐位复现**
# ★**代价预期**: halo 放松 ⇒ 可能蹭出 DRC clearance ⇒ ★**必须 fresh DRC 复查** (不认旧 JSON)
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {   # $1=臂名 $2=层数 $3=额外env
  local name="$1" layers="$2" extra="$3"
  local out="/tmp/v32_${name}.kicad_pcb"
  local log="/tmp/v32_${name}.log"
  if [ -e "$out" ] || [ -e "$log" ]; then
    echo "  [v32 臂 $name] ★已有产物/日志 ⇒ 不覆盖 (铁律: 不删别人的输出) ⇒ 跳过"
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
  echo "  [v32 臂 $name] PID=$! L=$layers env='$extra' → $out"
}

echo "=== v32 (治连接器差分脚逃逸走廊被过孔 halo 焊死) ==="
launch R 8 "PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0"   # ★与 v31_Q 同参, 只多这一刀
echo "=== v32 单臂已起 (官方板不动; 自动晋级守候器随后挂上) ==="
