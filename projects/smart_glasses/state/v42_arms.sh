#!/usr/bin/env bash
# v42_arms.sh —— ★**v42 概念: 串阻阵归位 (PCB_PART_POS) + 通孔禁区按真实孔心 (PCB_VIA_HALO_EXACT)**
#
# ★★**这是"组合臂"**: 两个机制各自已单独验证过, 这里叠在一起取冠军板
#   ① PCB_PART_POS 串阻阵归位  ⇒ 治 DSI "R_SEL 摆在反方向(右上角)" ⇒ 单变量臂 v39_R 已证:
#      ★**unconnected 57 → 55** (比官方板好) ★**但 DRC 4 ⇒ 被 Pareto 挡住**
#   ② PCB_VIA_HALO_EXACT=1      ⇒ 治 v39_R 那 4 条 DRC 的**根因**:
#      ★**`_add_via_halo` 禁区圆心用了"格心"而非"真实孔心"** ⇒ 孔偏格心 0.141mm 时判松
#      ⇒ A* 对角步 (0.25√2) 可擦过孔盘 (实测离真实孔心 0.5657mm < 0.625 需求)
#      ⇒ ★**单变量臂 v41_R 正在验证这个机制**
# ★**相对 v40_R 只多一个变量** (PCB_VIA_HALO_EXACT=1) ⇒ 可解释
# ★**默认关 ⇒ 与 v31/v36/v37/v39/v40 逐位一致**
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {
  local name="$1"
  local out="/tmp/v42_${name}.kicad_pcb"
  local log="/tmp/v42_${name}.log"
  if [ -e "$out" ] || [ -e "$log" ]; then
    echo "  [v42 臂 $name] ★已有产物/日志 ⇒ 不覆盖 ⇒ 跳过"
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
        PCB_PART_POS="R_SEL_D3_P:5.50,3.0;R_SEL_D3_N:7.95,3.0;R_SEL_D2_P:13.10,3.0;R_SEL_D2_N:15.55,3.0;R_SEL_CK_P:20.70,3.0;R_SEL_CK_N:23.15,3.0;R_SEL_D1_P:28.30,3.0;R_SEL_D1_N:30.75,3.0;R_SEL_D0_P:35.90,3.0;R_SEL_D0_N:38.35,3.0" \
        PCB_VIA_HALO_EXACT=1 \
        PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "$log" 2>&1
    echo "EXIT=$?" >> "$log"
  ) &
  echo "  [v42 臂 $name] PID=$! → $out"
}

echo "=== v42 臂 R (串阻归位 + 真实孔心禁区; 基线=官方板 env + keepout) ==="
launch R
echo "=== 已起 (官方板不动) ==="
