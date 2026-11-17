#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
for g in "HW/check_board_frame_caliber.py" "HW/check_board_frame_caliber.py --selftest" \
         "HW/check_onepass_preflight_coverage.py" "HW/check_onepass_preflight_coverage.py --selftest" \
         "HW/check_onepass_commit_order.py" "HW/check_onepass_commit_order.py --selftest" \
         "HW/check_land_row_anchors.py" "HW/check_land_row_anchors.py --selftest" \
         "state/land_v_values.py --selftest"; do
  timeout 600 python3 $g > /tmp/iss283_fin.txt 2>&1
  echo "rc=$? :: python3 $g"
done
echo "--- md5 ---"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
