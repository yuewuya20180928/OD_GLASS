#!/usr/bin/env bash
# ★★★★★★2026-11-11 06:1x 【★margin 扫描: ★官方链的 45 条到底能降多少★】★★★★★★
#   ★**依据 (★今晚实测★)**: ★★**halo margin 越小 ⇒ halo 越紧 ⇒ 可走空间越多 ⇒ A* 能找到的路越多** ★★
#     ★**实测: margin 0.20 ⇒ 补上 0 条 · margin 0.0625 ⇒ 补上 3 条 (官方) · margin 0.03125 ⇒ 补上 6 条 (我的链)** ★★
#   ★★**⇒ ⇒ 往下扫 ⇒ 看官方链 lineage 的 45 条能降到多少** ★★
#   ★★**纪律**: ★★**只读官方板, 只写 /tmp ⇒ 官方板 md5 611b869e 一字不动** ★★
#   ★★**⇒ 同时扫 SNAP=0 (默认, 与官方链逐位一致)** ★★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1
W=/tmp/snapfix
mkdir -p "$W"

fresh_drc () {
  [ -f "$2" ] && return 0
  bash state/kicad.sh pcb drc --output "$2" --severity-error --severity-warning --format json "$1" >/dev/null 2>&1
}

run_one () {  # $1=标签 $2=输入板 $3=margin
  local tag="$1" in="$2" margin="$3"
  local out="$W/out_${tag}.kicad_pcb"
  local drc="$W/in_${tag%%_*}.drc.json"
  fresh_drc "$in" "$drc"
  echo "──────── $tag (margin=$margin) ────────"
  env PCB_HALO_MARGIN="$margin" \
      bash state/pcbnew_py.sh state/patch_astar_nostub.py "$in" "$drc" \
      --out "$out" --grid 0.125 > "$W/log_${tag}.log" 2>&1
  echo "  rc=$?  段数=$(grep -ac '(segment' "$out" 2>/dev/null)"
  grep -E "^  ★补上|^── 补上" "$W/log_${tag}.log" | head -12
}

OFFICIAL_COMBO="$W/off_combo.kicad_pcb"
for m in 0.015625 0.0078125 0; do
  run_one "off_m${m}_s0" "$OFFICIAL_COMBO" "$m"
done
for m in 0.015625 0.0078125 0; do
  run_one "mine_m${m}_s0" "$W/in_s2_combo.kicad_pcb" "$m"
done
echo "=== margin 扫描跑完 $(date '+%F %T') ==="
