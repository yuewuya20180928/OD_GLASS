#!/usr/bin/env bash
# ★ISS-283 · 全闸扫描 (★落表前基线 / 落表后复跑同一份·对比用★) ★
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
LOG="$1"
: > "$LOG"
GATES=(
  "HW/check_land_row_anchors.py"
  "HW/check_land_row_anchors.py --selftest"
  "HW/check_netlist_selfconsistency.py"
  "HW/check_netlist_selfconsistency.py --selftest"
  "HW/check_netlist_selfconsistency.py --expect-resolved"
  "HW/check_netlist_contradiction_r3.py"
  "HW/check_part_selection_landed_crosscheck.py"
  "HW/check_onepass_preflight_coverage.py"
  "HW/check_onepass_preflight_coverage.py --selftest"
  "HW/check_onepass_commit_order.py"
  "HW/check_onepass_commit_order.py --selftest"
  "HW/check_board_frame_caliber.py"
  "HW/check_board_frame_caliber.py --selftest"
  "state/check_netlist.py"
  "state/check_netlist_pins.py"
  "state/check_sch_erc.py"
  "state/check_sch_pinfull.py"
  "state/land_v_values.py --selftest"
  "state/merge.py"
  "state/gate_check.py"
  "state/issue_check.py"
  "state/check_chain_content_anchor.py"
  "state/chain_gate.py"
  "MECH/check_board_frame_coords.py"
  "MECH/check_demo_struct_truth.py"
  "SW/tools/timing_check.py"
  "SW/tools/check_demo_panel_spec.py"
)
for g in "${GATES[@]}"; do
  echo "=== $g ===" >> "$LOG"
  timeout 300 python3 $g > /tmp/iss283_g.txt 2>&1
  echo "rc=$?" >> "$LOG"
  tail -6 /tmp/iss283_g.txt >> "$LOG"
  echo "" >> "$LOG"
done
echo "=== DONE ===" >> "$LOG"
