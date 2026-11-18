#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
GATES=(
"HW/check_pin_function_labels.py"
"HW/check_pin_function_labels.py --selftest"
"HW/check_step1_parts_spec.py"
"HW/check_onepass_preflight_coverage.py"
"HW/check_g1a7_selection_landed.py"
"HW/check_onepass_commit_order.py"
"HW/check_workpack_state_values.py"
"HW/check_fsin_rootcause.py"
"HW/check_netlist_selfconsistency.py"
"HW/check_netlist_selfconsistency.py --expect-resolved"
"HW/check_land_row_anchors.py"
"SW/tools/check_demo_panel_spec.py"
"SW/tools/timing_check.py"
"SW/tools/check_onepass_sw_sync.py"
"MECH/check_onepass_mech_release.py"
"MECH/check_mech_verdict_freshness.py"
"MECH/check_onepass_mech_sync.py"
"MECH/check_onepass_struct_crosscheck.py"
"MECH/check_demo_struct_truth.py"
"MECH/check_board_frame_coords.py"
"MECH/board_port_opening_s6_check.py"
)
for g in "${GATES[@]}"; do
  echo "### CMD: python3 $g"
  out=$(python3 $g 2>&1); rc=$?
  echo "$out" | tail -4
  echo "### RC=$rc"
  echo
done
echo "### DONE $(date '+%F %T')"
