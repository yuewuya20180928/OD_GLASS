#!/usr/bin/env bash
# ISS-302 cont1 · 闸复跑 runner (hw-lead · 2026-11-18)
# ★只读复跑: 不改任何判据 / 不改任何基线常量 ★
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 99

LOG="logs/iss302/gates_rerun.log"
: > "$LOG"

run() {
  local label="$1"; shift
  echo "==================================================" >> "$LOG"
  echo "### GATE: $label" >> "$LOG"
  echo "### CMD : $*" >> "$LOG"
  echo "--- output begin ---" >> "$LOG"
  "$@" >> "$LOG" 2>&1
  local rc=$?
  echo "--- output end ---" >> "$LOG"
  echo "### RC  : $rc" >> "$LOG"
  echo "### VERDICT: $label => rc=$rc" >> "$LOG"
  echo "" >> "$LOG"
  echo "$label rc=$rc"
}

echo "=== ISS-302 闸复跑 开始 $(date '+%Y-%m-%d %H:%M:%S %z') ===" | tee -a "$LOG"

run "HW/check_pin_function_labels.py"          python3 HW/check_pin_function_labels.py
run "HW/check_pin_function_labels.py --selftest" python3 HW/check_pin_function_labels.py --selftest
run "HW/check_step1_parts_spec.py"             python3 HW/check_step1_parts_spec.py
run "HW/check_onepass_preflight_coverage.py"   python3 HW/check_onepass_preflight_coverage.py
run "HW/check_g1a7_selection_landed.py"        python3 HW/check_g1a7_selection_landed.py
run "HW/check_onepass_commit_order.py"         python3 HW/check_onepass_commit_order.py
run "HW/check_workpack_state_values.py"        python3 HW/check_workpack_state_values.py
run "HW/check_fsin_rootcause.py"               python3 HW/check_fsin_rootcause.py
run "HW/check_netlist_selfconsistency.py"      python3 HW/check_netlist_selfconsistency.py
run "HW/check_netlist_selfconsistency.py --expect-resolved" python3 HW/check_netlist_selfconsistency.py --expect-resolved
run "HW/check_land_row_anchors.py"             python3 HW/check_land_row_anchors.py
run "SW/tools/check_demo_panel_spec.py"        python3 SW/tools/check_demo_panel_spec.py
run "SW/tools/timing_check.py"                 python3 SW/tools/timing_check.py
run "SW/tools/check_onepass_sw_sync.py"        python3 SW/tools/check_onepass_sw_sync.py
run "MECH/check_onepass_mech_release.py"       python3 MECH/check_onepass_mech_release.py
run "MECH/check_mech_verdict_freshness.py"     python3 MECH/check_mech_verdict_freshness.py
run "MECH/check_onepass_mech_sync.py"          python3 MECH/check_onepass_mech_sync.py
run "MECH/check_onepass_struct_crosscheck.py"  python3 MECH/check_onepass_struct_crosscheck.py
run "MECH/check_demo_struct_truth.py"          python3 MECH/check_demo_struct_truth.py
run "MECH/check_board_frame_coords.py"         python3 MECH/check_board_frame_coords.py

echo "=== 闸复跑 结束 $(date '+%Y-%m-%d %H:%M:%S %z') ===" | tee -a "$LOG"
