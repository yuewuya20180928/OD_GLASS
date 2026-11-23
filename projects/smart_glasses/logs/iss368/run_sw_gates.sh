#!/usr/bin/env bash
# ★ISS-368 · 10 道 SW 闸逐道 rc 复跑 (★用法: run_sw_gates.sh <根目录> <输出文件>★)
# ★根目录 = 项目根 (真件) 或沙盒副本根 ⇒ 闸的 cwd 必须是那个根 ★
set -u
ROOT="${1:?root}"
OUT="${2:?out}"
cd "$ROOT" || exit 90
export TMPDIR="$ROOT/tmp/iss368_tmp"
mkdir -p "$TMPDIR"

GATES=(
  "SW/tools/check_onepass_sw_sync.py"
  "SW/tools/check_sw_ref_reachability.py"
  "SW/tools/check_landing_trace_obligation.py"
  "SW/tools/check_demo_panel_spec.py"
  "SW/tools/check_demo_panel_spec_r6_selftest.py"
  "SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py"
  "SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py"
  "SW/tools/check_shutdown_semantics.py"
  "SW/tools/check_timing_review_adc_sync.py"
  "SW/tools/timing_check.py"
  "SW/tools/check_onepass_sw_release.py"
)
: > "$OUT"
{
  echo "# ISS-368 · 10 道 SW 闸逐道 rc"
  echo "# root = $ROOT"
  echo "# at   = $(date -Is)"
  echo
} >> "$OUT"

green=0; red=0
for g in "${GATES[@]}"; do
  o="$(timeout 300 python3 "$g" 2>&1)"
  rc=$?
  echo "===== $g => rc=$rc =====" >> "$OUT"
  echo "$o" >> "$OUT"
  echo >> "$OUT"
  if [ "$rc" -eq 0 ]; then green=$((green+1)); else red=$((red+1)); fi
done
# ★附加: 既有汇总闸的 --selftest
o="$(timeout 300 python3 SW/tools/check_onepass_sw_release.py --selftest 2>&1)"; rc=$?
echo "===== SW/tools/check_onepass_sw_release.py --selftest => rc=$rc =====" >> "$OUT"
echo "$o" >> "$OUT"
echo >> "$OUT"
if [ "$rc" -eq 0 ]; then green=$((green+1)); else red=$((red+1)); fi

{
  echo "----- 汇总 -----"
  echo "绿 = $green · 红 = $red"
  echo "----- end -----"
} >> "$OUT"
echo "green=$green red=$red" > "${OUT}.summary"
exit 0
