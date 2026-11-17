cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=/home/yuewuya/.openclaw/workspace/projects/smart_glasses/tmp/iss283
LOG=logs/iss283/final_check_1750.log
: > $LOG
for c in "HW/check_land_row_anchors.py" "HW/check_land_row_anchors.py --selftest" \
         "HW/check_onepass_preflight_coverage.py" "HW/check_onepass_preflight_coverage.py --selftest" \
         "HW/check_onepass_commit_order.py" "HW/check_onepass_commit_order.py --selftest" \
         "HW/check_board_frame_caliber.py" "HW/check_board_frame_caliber.py --selftest" \
         "HW/check_netlist_selfconsistency.py" "HW/check_netlist_selfconsistency.py --selftest" \
         "HW/check_netlist_selfconsistency.py --expect-resolved" \
         "state/land_v_values.py --selftest" "state/merge.py" "state/gate_check.py" "state/issue_check.py"; do
  timeout 300 python3 $c > /tmp/iss283_fc.txt 2>&1
  echo "rc=$? :: python3 $c" >> $LOG
done
echo "--- md5 ---" >> $LOG
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv \
       HW/netlist_v1_pins.csv HW/BOM_v1.csv >> $LOG
echo "=== DONE ===" >> $LOG
