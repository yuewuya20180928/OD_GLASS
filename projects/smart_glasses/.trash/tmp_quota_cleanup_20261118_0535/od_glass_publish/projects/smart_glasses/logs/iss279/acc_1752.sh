#!/usr/bin/env bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
LOG="$1"; : > "$LOG"
run(){ echo "=== $* ===" >> "$LOG"; timeout 400 python3 "$@" >> "$LOG" 2>&1; echo "rc=$?" >> "$LOG"; }
run SW/tools/check_onepass_sw_sync.py
run SW/tools/check_onepass_sw_sync.py --selftest
run SW/tools/check_demo_panel_spec.py
run SW/tools/check_demo_panel_spec.py --selftest
run SW/tools/check_demo_panel_spec_r6_selftest.py
run SW/tools/timing_check.py
run SW/tools/check_shutdown_semantics.py
run SW/tools/check_brightness_biosafety.py
run SW/tools/check_load_switch_selection.py
run SW/tools/demo_e2e_budget.py
run state/check_pcb_drc.py
echo "=== bash state/pcbnew_py.sh state/check_pcb_nets.py ===" >> "$LOG"
timeout 400 bash state/pcbnew_py.sh state/check_pcb_nets.py >> "$LOG" 2>&1; echo "rc=$?" >> "$LOG"
run state/merge.py
run state/gate_check.py
echo "=== md5 ===" >> "$LOG"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv >> "$LOG" 2>&1
echo "=== DONE ===" >> "$LOG"
