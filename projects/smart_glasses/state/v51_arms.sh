#!/usr/bin/env bash
# v51_arms.sh -- ★**v51 概念: 干净基线 + rip-up 复活**
#
# ★★★★**为什么要有这个臂 (2026-11-06 02:1x 实测, 四个臂打死同一批差分对)**:
#   v44 / v46 / v47 / v48 **全部**打死 `DSI_D0_CK` · `DSI_D0_CK_SRC` · `DSI_D0_D1`
#   ⇒ ★**这不是随机打地鼠, 是同一个坏布局**
#   实测证据 (fail_detail 里的 start/goal):
#     DSI_D0_CK_P : CONN_LIGHT.6 [32.7,60.7] -> [20.95,6.2]   ★**目标在左上角**
#     DSI_D0_D1_P : CONN_LIGHT.3 [34.2,59.45] -> [28.45,6.2]
#     DSI_D0_CK_N : CONN_LIGHT.5 [33.2,60.7] -> [23.45,6.2]
#     DSI_D0_D1_N : CONN_LIGHT.2 [34.7,60.7] -> [30.95,6.2]
#   ⇒ ★**而官方板 v37 里 R_SEL_* 在右上** (x 78.9..117.3, y 5.5..9.5)
#     ★官方板的 DSI 铜也全在右上 (DSI_D0_CK_P x 82.5..104.5; _SRC 走板顶 y 5.6..8.0)
#   ⇒ ★**v39/v40 引入的 `PCB_PART_POS` 把 R_SEL 挪到了左上 (x 5.5..38.35, y 3.0)**
#     ⇒ 那条纵向走廊 **x 21..35, y 6..60 正好穿过 SoM 主体 (SOM_AREA 8..68, 6..50)**
#     ⇒ ★**必布不通** ⇒ ★**v44/v46/v47/v48 全中**
#   ⇒ ★★**本臂 = 把 R_SEL 挪回右上 (删掉 PCB_PART_POS) + 板边闸**
#
# ★★**为什么还要 `PCB_EDGE_STRICT=1`**:
#   v47 板 DRC=12, 其中 **10 条是 `DSI_D0_D1_N` 跑出板框** (实测 y=-0.046mm)
#   ⇒ 根因: 缝合路径不查板边 + `_emit_path` 只查首尾 + commit 只数不拦
#   ⇒ 补丁: `PCB_EDGE_STRICT=1` (默认关, 老行为可复现)
#   ⇒ 交叉验证已过: ★**路由器判据在真板上抓到的 10 条铜 = KiCad DRC 报的 10 条, 零漏报**
#
# ★**单变量说明**: 相对 v44 = ① 删 PCB_PART_POS (R_SEL 回右上) ② 加 PCB_EDGE_STRICT=1
#   ★两项都有机器可读的实测依据 (见上), 不是猜的
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {
  local name="$1"
  local out="/tmp/v51_${name}.kicad_pcb"
  local log="/tmp/v51_${name}.log"
  if [ -e "$out" ] || [ -e "$log" ]; then
    echo "  [v51 臂 $name] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"; return 0
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
        PCB_VIA_HALO_CENTER=1 \
        PCB_EDGE_STRICT=1 \
        PCB_RIPUP_ALIVE=1 \
        PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "$log" 2>&1
    echo "EXIT=$?" >> "$log"
  ) &
  echo "  [v51 臂 $name] PID=$! → $out"
}
echo "=== v51 臂 R (干净基线: R_SEL 回右上 + 板边闸) ==="
launch R
echo "=== 已起 (官方板不动) ==="
