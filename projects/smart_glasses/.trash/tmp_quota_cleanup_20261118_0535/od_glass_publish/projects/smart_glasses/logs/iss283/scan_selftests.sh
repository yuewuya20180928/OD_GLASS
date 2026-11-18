#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
for g in "HW/check_board_frame_caliber.py --selftest" "HW/check_land_row_anchors.py --selftest" "HW/check_netlist_selfconsistency.py --selftest" "HW/check_onepass_preflight_coverage.py --selftest" "HW/check_onepass_commit_order.py --selftest" "state/land_v_values.py --selftest"; do
  echo "########## $g"
  timeout 900 python3 $g 2>&1 | tail -25
  echo "########## rc=${PIPESTATUS[0]} :: $g"
done
