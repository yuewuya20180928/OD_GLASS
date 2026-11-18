#!/usr/bin/env bash
# run_grid_ladder.sh -- ★**网格阶梯实验 (2026-11-06 08:1x)**
#
# ★**为什么要有这个脚本 (机器实测链)**:
#   ① 官方板 unc 45 (18092段/433孔 · DRC 0 · md5 611b869e)
#   ② `patch_astar_nostub.py` 在 0.125mm 网格 + halo margin 0.0625 ⇒ 救回 3 条
#   ③ ★**剩下 45 条里 23 条 >40mm + 25 条是差分腿** ⇒ **全是 SoM BTB 出脚问题**
#   ④ ★★**最深的根因 (量化)**: SoM BTB **0.4mm pitch** · 焊盘 0.2mm 宽
#      ⇒ 相邻焊盘格心距 = 0.4mm ⇒ ★**在 0.25mm 网格上 = 1.6 格 (非整数!)**
#      ⇒ 焊盘周围 3×3 起步格全是别网焊盘 ⇒ ★**A\* 连起步格都拿不到**
#      ⇒ ★**0.25mm 网格对 0.4mm pitch BTB 结构性无解** (不是算法不够好)
#   ⑤ ⇒ ★**解法 = 更细网格 + 相应收紧 halo margin**
#      ★**margin 下限 = 网格半格** (★量化损失无人承担 ⇒ DRC 撞线 ⇒ 07:0x 实测:
#        margin=0 于 0.125mm 网格 ⇒ **11 条 clearance 违规 0.1937 < 0.2**)
#
# ★**网格阶梯 (每一级都独立成板, 后一级以官方板为基线)**:
#   0.1250mm ⇒ margin 0.0625 (★当前已用, 救回 3 条)
#   0.0625mm ⇒ margin 0.03125 (★**0.4mm pitch = 6.4 格** ⇒ 起步格终于能落在焊盘之间)
#
# ★**每个网格跑完都必做**:
#   ① fresh DRC (★margin 是算出来的下限, 但仍必须实测)
#   ② 名单制闸 `compare_arm_official.py` (★退铜名单空 + 差分死腿空 + 逐网孤岛不变多)
#   ③ 只有 ACCEPT 才谈晋级
#
# 用法: bash state/run_grid_ladder.sh <板> <DRC.json> [网格]
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
PCB="${1:?用法: run_grid_ladder.sh <板> <DRC.json> [网格]}"
DRC="${2:?}"
GRID="${3:-0.0625}"

# ★**margin = 网格半格** (★量化损失下限) ⇒ 向上取到 4 位小数
MARGIN=$(python3 -c "print(round($GRID/2.0, 6))")
OUT="/tmp/_ladder_${GRID}.kicad_pcb"
LOG="/tmp/_ladder_${GRID}.log"

echo "═══ 网格阶梯: grid=${GRID}mm · margin=${MARGIN}mm (半格) ═══"
env PCB_HALO_MARGIN="$MARGIN" bash state/pcbnew_py.sh state/patch_astar_nostub.py \
    "$PCB" "$DRC" --out "$OUT" --grid "$GRID" --width 0.25 --budget 900000 \
    > "$LOG" 2>&1
echo "  跑完 rc=$? ⇒ $OUT"

echo "── fresh DRC ──"
bash state/pcbnew_py.sh state/check_pcb_drc.py "$OUT" 2>&1 | grep -E "C3 |C4 |C7 "
echo "── 名单制闸 ──"
python3 state/compare_arm_official.py "$OUT" "$PCB" 2>&1 | tail -16
