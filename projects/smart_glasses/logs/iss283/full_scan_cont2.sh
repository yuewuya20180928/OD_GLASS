#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
OUT=logs/iss283/full_scan_cont2_1345.log
: > $OUT
run () {
  echo "### CMD: $*" | tee -a $OUT
  timeout 900 "$@" > /tmp/iss283_scan_one.txt 2>&1
  rc=$?
  echo "### rc=$rc :: $*" | tee -a $OUT
  tail -6 /tmp/iss283_scan_one.txt | sed 's/^/    /' | tee -a $OUT
  echo "" | tee -a $OUT
}
run python3 state/land_v_values.py --selftest
run python3 HW/check_land_row_anchors.py
run python3 HW/check_land_row_anchors.py --selftest
run python3 HW/check_netlist_selfconsistency.py
run python3 HW/check_netlist_selfconsistency.py --selftest
run python3 HW/check_netlist_selfconsistency.py --expect-resolved
run python3 HW/check_netlist_contradiction_r3.py
run python3 HW/check_part_selection_landed_crosscheck.py
run python3 HW/check_onepass_preflight_coverage.py
run python3 HW/check_onepass_preflight_coverage.py --selftest
run python3 HW/check_onepass_commit_order.py
run python3 HW/check_onepass_commit_order.py --selftest
run python3 HW/check_board_frame_caliber.py
run python3 HW/check_board_frame_caliber.py --selftest
run python3 state/check_netlist.py
run python3 state/check_netlist_pins.py
run python3 state/check_sch_erc.py
run python3 state/check_sch_pinfull.py
run python3 state/issue_check.py
run python3 state/check_chain_content_anchor.py
run python3 state/chain_gate.py
run python3 MECH/check_board_frame_coords.py
run python3 SW/tools/timing_check.py
echo "=== SCAN DONE ===" | tee -a $OUT
