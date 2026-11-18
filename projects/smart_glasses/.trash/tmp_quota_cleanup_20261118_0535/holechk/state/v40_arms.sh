#!/usr/bin/env bash
# v40_arms.sh —— ★**v40 概念: 以"新官方板 v37_R"为基线 + DSI 中途串阻阵 `R_SEL_D*` 归位**
#
# ★**为什么要有 (2026-11-05 23:1x 机器读数)**:
#   · 官方板已换成 **v37_R** (23:00:15 落盘): 17018 段 / 408 孔 / **unconnected 57** / DRC 0 / parity 全过
#     ⇒ ★**首次把 unconnected 从 64 打到 57** (v37_R 的 keepout 24.0,56.1,35.6,59.6 起作用)
#   · ★**DSI 仍是最大缺口**: 新官方板 57 条未通里 **13 条是 DSI**
#     (A腿 SoM→串阻 与 B腿 串阻→CONN_LIGHT 都断)
#   · ★**根因 = 串阻阵摆在反方向** (机器读):
#       `R_SEL_*` 全阵在 **x=78.90…118.90** (右上角) ⇒ 两条端点全在左边
#       (SoM `J_SOM_P3` DSI 脚 x=18.40…23.60,y=7.96 / `CONN_LIGHT` DSI 脚 x=26.25…34.75,y=60.15)
#       ⇒ 单 lane 168mm 斜穿全板 ⇒ 官方板实测 A 腿失败段长 **55–98mm**
#       (`DSI_D0_D3_N_SRC`: (18.8,7.96)→(117.3,5.6) = **98mm**)
#   · ⇒ 本臂把 10 个 `R_SEL_*` 钉到**顶带 y=3.0**, **按 SoM 侧 lane x 序** (D3,D2,CK,D1,D0)
#       ⇒ 腿 A (SoM→串阻) 零交叉, 腿 B (串阻→CONN_LIGHT) 承担 lane 3-cycle 交叉 (长走廊有换层空间)
#
# ★**单变量 (vs 官方板 v37_R)**: env 与 v37_R **逐位相同**, 只多一个 `PCB_PART_POS`
# ★**默认关**: `PCB_PART_POS` 空 ⇒ 行为与 v37_R 逐位一致 (机制在 gen_pcb_netlist_board.py, env 门控)
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {   # $1=臂名
  local name="$1"
  local out="/tmp/v40_${name}.kicad_pcb"
  local log="/tmp/v40_${name}.log"
  if [ -e "$out" ] || [ -e "$log" ]; then
    echo "  [v40 臂 $name] ★已有产物/日志 ⇒ 不覆盖 (铁律: 不删别人的输出) ⇒ 跳过"
    return 0
  fi
  # ★R_SEL_D* 顶带坐标 (SoM lane 序): 同 lane P/N 间距 2.45mm (铜间隙 0.25), lane 间 5.15mm (铜间隙 2.95)
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
        PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "$log" 2>&1
    echo "EXIT=$?" >> "$log"
  ) &
  echo "  [v40 臂 $name] PID=$! → $out"
}

echo "=== v40 臂 R (基线=新官方板 v37_R + DSI 串阻阵归位) ==="
launch R
echo "=== 已起 (官方板不动) ==="
