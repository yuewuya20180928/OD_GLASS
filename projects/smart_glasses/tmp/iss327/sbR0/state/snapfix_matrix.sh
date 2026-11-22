#!/usr/bin/env bash
# ★★★★★★2026-11-11 05:6x 【★端点吸附 (PCB_PATCH_SNAP) 的 2x2 对照实验★】★★★★★★
#   ★**问题**: ★链日志的"补上 N 条"是不是假阳性? ⇒ **A* 终点停在【最近格心】⇒ 离焊盘中心差 0.15~0.19mm ⇒ 没搭上**
#   ★**修法**: ★`PCB_PATCH_SNAP=1` ⇒ 路径首/末端点换成【端点真实坐标】⇒ 铜真正压在焊盘上
#   ★★**矩阵**:
#     ① 我的链 s2_combo (2741段) × margin {0.20, 0.03125} × SNAP {0,1}
#     ② ★官方链 combo 输出 (17585段, md5 3267a6df) × margin 0.0625 × SNAP {0,1}
#        ⇒ ★★**官方链第③步的配方** ⇒ SNAP=0 必须逐位复现官方板 (18092段 / md5 611b869e)
#        ⇒ ★★**SNAP=1 ⇒ 官方板的 45 条未连接会不会掉?!** ★★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1
W=/tmp/snapfix
mkdir -p "$W"

fresh_drc () {  # $1=板 $2=输出json
  bash state/kicad.sh pcb drc --output "$2" --severity-error --severity-warning --format json "$1" >/dev/null 2>&1
}

run_one () {  # $1=标签 $2=输入板 $3=margin $4=snap
  local tag="$1" in="$2" margin="$3" snap="$4"
  local out="$W/out_${tag}.kicad_pcb"
  local drc="$W/in_${tag}.drc.json"
  if [ ! -f "$drc" ]; then fresh_drc "$in" "$drc"; fi
  echo "──────── $tag (margin=$margin snap=$snap) ────────"
  env PCB_HALO_MARGIN="$margin" PCB_PATCH_SNAP="$snap" \
      bash state/pcbnew_py.sh state/patch_astar_nostub.py "$in" "$drc" \
      --out "$out" --grid 0.125 > "$W/log_${tag}.log" 2>&1
  echo "  rc=$?  段数=$(grep -ac '(segment' "$out" 2>/dev/null)  md5=$(md5sum "$out" 2>/dev/null | cut -c1-12)"
  grep -E "^  ★补上|^── 补上" "$W/log_${tag}.log" | head -10
}

# ---- ① 我的链 ----
run_one mine_m020_s0 /tmp/snapfix/in_s2_combo.kicad_pcb 0.20 0
run_one mine_m020_s1 /tmp/snapfix/in_s2_combo.kicad_pcb 0.20 1
run_one mine_m031_s0 /tmp/snapfix/in_s2_combo.kicad_pcb 0.03125 0
run_one mine_m031_s1 /tmp/snapfix/in_s2_combo.kicad_pcb 0.03125 1

# ---- ② 官方链 (★combo 输出 = 官方链第②步的产物★) ----
OFFICIAL_COMBO="$PROJ/state/.lastgood/board_combo_unc48_20261106_0629.kicad_pcb"
if [ -f "$OFFICIAL_COMBO" ]; then
  cp -a "$OFFICIAL_COMBO" "$W/off_combo.kicad_pcb"
  run_one off_m0625_s0 "$W/off_combo.kicad_pcb" 0.0625 0
  run_one off_m0625_s1 "$W/off_combo.kicad_pcb" 0.0625 1
else
  echo "❌ 官方 combo 找不到"
fi
echo "=== 全矩阵跑完 $(date '+%F %T') ==="
