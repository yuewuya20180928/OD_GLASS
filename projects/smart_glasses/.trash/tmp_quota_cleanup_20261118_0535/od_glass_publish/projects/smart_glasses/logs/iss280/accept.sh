#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
run() { # $1=label $2...=cmd
  local label="$1"; shift
  echo "### $label"
  echo "\$ $*"
  out=$("$@" 2>&1); rc=$?
  echo "$out" | tail -12
  echo ">>> RC=$rc"
  echo
}
run "A1 check_onepass_commit_order"        python3 HW/check_onepass_commit_order.py
run "A2 check_onepass_commit_order selftest" python3 HW/check_onepass_commit_order.py --selftest
run "A3 preflight_coverage"                python3 HW/check_onepass_preflight_coverage.py
run "A4 preflight_coverage selftest"       python3 HW/check_onepass_preflight_coverage.py --selftest
run "A5 board_frame_caliber"               python3 HW/check_board_frame_caliber.py
run "A6 board_frame_caliber selftest"      python3 HW/check_board_frame_caliber.py --selftest
run "A7 netlist_contradiction_r3"          python3 HW/check_netlist_contradiction_r3.py
run "A8 check_pcb_drc"                     python3 state/check_pcb_drc.py
run "A9 check_pcb_nets"                    bash state/pcbnew_py.sh state/check_pcb_nets.py
run "A10 issue_check"                      python3 state/issue_check.py
echo "### PROTECTED MD5 AFTER"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
echo "### OTHERS MD5 (must be untouched by me)"
md5sum HW/PCB/BOARD_ONEPASS_PREFLIGHT.md HW/check_onepass_preflight_coverage.py HW/PCB/BOARD_FRAME_CALIBER.md HW/check_board_frame_caliber.py HW/check_netlist_contradiction_r3.py state/check_pcb_drc.py state/check_pcb_nets.py state/compare_arm_official.py
echo "### ISSUE LOG / TRACKER untouched?"
stat -c '%y %n' state/issue_log.yaml PROJECT_TRACKER.md
echo "### ACCEPT SUITE DONE"
