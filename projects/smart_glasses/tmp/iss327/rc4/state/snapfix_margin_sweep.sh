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

# ★★★★★★2026-11-11 08:4x 【★扫描出口必须自动过晋级闸 (★不许靠人记得看判据★)★】★★★★★★
#   ★**为什么**: 06:24 那轮播报写 "unc 45→42 ⇒ 看着是改善" ⇒ ★**实测是假改善**:
#     ★**差分腿 `CSI_D0_D0_P` 从【已连通】退成【未连通】 + DRC 0→16 (clearance)★**
#     ⇒ ★**"unc 变少 ≠ 板子更好" ⇒ 必须有机器闸拦** ★★
#   ★**闸 = `state/margin_sweep_gate.py`** (★判据的唯一实现仍是 `compare_arm_official.py` 的名单制★)
#   ★**纪律**: ★**官方 lineage 的变体才与官方板可比** ⇒ ★**"mine_*" 族段数只有 3650 (不同工艺) ⇒ 不进闸** ★★
OFFICIAL_BOARD=state/.lastgood/board_nostub_loose_unc45_20261106_0705.kicad_pcb
PRO=state/.lastgood/candidate_official_p41.kicad_pro
GATE_ARGS=()
for tag in off_m0.0625 off_m0.015625 off_m0.0078125 off_m0; do
  [ -f "$W/out_${tag}.kicad_pcb" ] && GATE_ARGS+=(--label "$tag=$W/out_${tag}.kicad_pcb")
done
if [ ${#GATE_ARGS[@]} -gt 0 ] && [ -f "$OFFICIAL_BOARD" ]; then
  echo ""
  echo "── ★★margin 扫描晋级闸 (★官方 lineage 变体 vs 官方板·名单制★) ──"
  python3 state/margin_sweep_gate.py --official "$OFFICIAL_BOARD" --pro "$PRO" \
      --report state/.lastgood/MARGIN_SWEEP_GATE_$(date +%Y-%m-%d).md \
      "${GATE_ARGS[@]}"
  GATE_RC=$?
  echo "  ★★闸 rc=$GATE_RC (0 = 没有变体够格晋级 · 10 = 有变体过闸 ⇒ 要人工接手)"
else
  echo "⚠️ 没有官方 lineage 变体 / 官方板不在 ⇒ 跳过晋级闸 (★不许默认'扫完就算过★)"
  GATE_RC=2
fi
echo "=== margin 扫描 + 晋级闸 全流程结束 $(date '+%F %T') (闸 rc=$GATE_RC) ==="
exit $GATE_RC
