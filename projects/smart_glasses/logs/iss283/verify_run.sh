#!/usr/bin/env bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=/home/yuewuya/.openclaw/workspace/projects/smart_glasses/logs/iss283/tmp
LOG="$1"
: > "$LOG"
run() {
  echo "=== $* ===" >> "$LOG"
  timeout 400 python3 "$@" >> "$LOG" 2>&1
  echo "rc=$?" >> "$LOG"
}
run HW/check_land_row_anchors.py
run HW/check_land_row_anchors.py --selftest
run HW/check_netlist_selfconsistency.py
run HW/check_netlist_selfconsistency.py --expect-resolved
run HW/check_onepass_preflight_coverage.py
run HW/check_onepass_preflight_coverage.py --selftest
run HW/check_onepass_commit_order.py
run HW/check_onepass_commit_order.py --selftest
run HW/check_board_frame_caliber.py
run HW/check_board_frame_caliber.py --selftest
run state/land_v_values.py --selftest
run state/check_netlist.py
run state/check_netlist_pins.py
run state/check_sch_erc.py
run state/check_sch_pinfull.py
run state/merge.py
run state/gate_check.py
echo "=== md5 ===" >> "$LOG"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv >> "$LOG" 2>&1
stat -c '%y %n' HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro >> "$LOG" 2>&1
echo "=== DONE ===" >> "$LOG"
