#!/usr/bin/env bash
# v41_arms.sh —— ★**v41 概念: 通孔净距禁区按真实孔心算 (修 DRC 漏网)**
# ★**根因 (2026-11-05 23:2x 机器读 + 数值复现)**:
#   `_add_via_halo` 的禁区圆心 = "含孔心那一格"的**格心**, 不是**真实孔心**
#   ⇒ 孔偏格心 δ 时禁区整体偏 δ
#   ⇒ 实测 (v36_S 的 3 条 DRC): 孔 (85.35,9.60) 偏格心 (0.10,0.10)=0.141mm
#     · `Track [DSI_D0_D0_P] on In2.Cu` 端点 (84.95,9.20):
#         离**真实孔心** **0.5657mm** (需 ≥0.625 ⇒ **违规**) 却按格心判 = 0.7071mm ⇒ **放行**
#     · A* 走 8 邻域 ⇒ **对角步 (0.25√2=0.3536mm) 擦过孔盘**
#   ⇒ 修法: 圆心改真实孔心 + 判据 = 格心距 < rr + g*sqrt(2)/2 (★可证安全: 穿格段上任一点到两端点中较近者 ≤ 0.1768mm)
#   ⇒ 单测 `state/_test_halo.py` 全通过 (新判据下最坏对角段 0.8485mm ≥ 0.625)
# ★**单变量 (vs 官方板 v37_R)**: env 逐位相同, 只多一个 `PCB_VIA_HALO_EXACT=1`
# ★**默认关** ⇒ 与 v31/v36/v37/v39/v40 逐位一致
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {
  local name="$1"
  local out="/tmp/v41_${name}.kicad_pcb"
  local log="/tmp/v41_${name}.log"
  if [ -e "$out" ] || [ -e "$log" ]; then
    echo "  [v41 臂 $name] ★已有产物/日志 ⇒ 不覆盖 ⇒ 跳过"
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
        PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
        PCB_VIA_HALO_EXACT=1 \
        PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "$log" 2>&1
    echo "EXIT=$?" >> "$log"
  ) &
  echo "  [v41 臂 $name] PID=$! → $out"
}

echo "=== v41 臂 R (通孔禁区按真实孔心; 基线=官方板 v37_R env) ==="
launch R
echo "=== 已起 (官方板不动) ==="
