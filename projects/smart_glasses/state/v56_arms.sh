#!/usr/bin/env bash
# v56_arms.sh -- ★**v56 = v52 的重跑 (★v52_R 在 06:43 被误杀, 没出板)**
#
# ★★**为什么原样重跑 v52 (不调参)**: ★**单变量可比**
#   · v52 = ①删 PCB_PART_POS (R_SEL 回右上) ②加 PCB_EDGE_STRICT=1
#   · ★**两个改动都有机器可读的实测依据** (见 state/v52_arms.sh 头部注释):
#     v44/v46/v47/v48 **四个臂全部打死同一批差分对** ⇒ 根因 = v39+ 把 R_SEL 挪左上
#     ⇒ 那条纵向走廊 x21..35,y6..60 正好穿过 SOM_AREA ⇒ **几何上必布不通**
#   · ★**gen_pcb_routing.py 自 02:4x 起未改** ⇒ ★**同代码同 env ⇒ 与 v52_R 逐位可比**
#
# ★★**这一版与 v52_R 的唯一差别**: ★**timeout 14400 → 21600 (4h → 6h)**
#   ⇒ ★★**教训 (2026-11-06 06:4x 实测事故)**: v52_R 跑满 4h 时 `timeout` 触发 SIGTERM,
#      ★**我当时用 `kill -9` 去废包装器 ⇒ 连坐把 python 一起杀了 (EXIT=137) ⇒ 4 小时工作全丢**
#      ⇒ ★**要废一个 `timeout` 包装器, 应该用 `kill -STOP` 让它停摆, 不是 `kill`**
#      ⇒ ★**这一版根本不废它**: 6 小时足够跑完, 跑完就自己退出
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

PREFIX="${PREFIX:-v56}"
OUT="/tmp/${PREFIX}_R.kicad_pcb"
LOG="/tmp/${PREFIX}_R.log"

if [ -e "$OUT" ] || [ -e "$LOG" ]; then
  echo "  [${PREFIX} 臂 R] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"; exit 0
fi

echo "=== ${PREFIX} 臂 R (v52 原样重跑 + 6h timeout) ==="
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
      PCB_RIPUP_ESC=1 \
      PCB_OUT="$OUT" \
      timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$LOG" 2>&1
  echo "EXIT=$?" >> "$LOG"
) &
echo "  [${PREFIX} 臂 R] PID=$! → $OUT  (timeout 21600s = 6h)"
echo "=== 已起 (官方板不动) ==="

# ★守候器: 一落盘就自动量 + 自动过闸晋级 (★官方板现在是 unc 48 ⇒ 基准是 48)
nohup bash state/auto_promote_when_done.sh "$PREFIX" R 21600 >/dev/null 2>&1 &
echo "  [守候器] PID=$! (等 ${PREFIX}_R 落盘 ⇒ 自动量 ⇒ 过闸才晋级)"
