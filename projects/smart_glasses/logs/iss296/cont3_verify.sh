#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
echo "===== ISS-296 cont3 FINAL VERIFICATION $(date '+%F %T %z') ====="
echo "--- 1 frame main"; python3 MECH/check_board_frame_coords.py >/dev/null 2>&1; echo "rc=$?"
echo "--- 2 frame selftest"; python3 MECH/check_board_frame_coords.py --selftest >/dev/null 2>&1; echo "rc=$?"
echo "--- 3 struct main"; python3 MECH/check_demo_struct_truth.py >/dev/null 2>&1; echo "rc=$?"
echo "--- 4 struct selftest"; python3 MECH/check_demo_struct_truth.py --selftest >/dev/null 2>&1; echo "rc=$?"
echo "--- 5 onepass mech"; python3 MECH/check_onepass_mech_sync.py >/dev/null 2>&1; echo "rc=$?"
echo "--- 6 onepass struct"; python3 MECH/check_onepass_struct_crosscheck.py >/dev/null 2>&1; echo "rc=$?"
echo "--- 7 probe same source"; python3 logs/iss296/probe_ledger_reading_same_source.py >/dev/null 2>&1; echo "rc=$?"
echo "--- 8 merge"; python3 state/merge.py >/dev/null 2>&1; echo "rc=$?"
echo "--- 9 gate_check"; python3 state/gate_check.py >/dev/null 2>&1; echo "rc=$?"
echo "--- 10 issue_check"; python3 state/issue_check.py >/dev/null 2>&1; echo "rc=$?"
echo "--- grep count"; grep -c iss296 state/fragments/mech.yaml; echo "count_rc=$?"
echo "--- md5 protected"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
ls -la --time-style=full-iso HW/PCB/demo_mainboard.kicad_pcb
ls -la --time-style=full-iso HW/SCHEMATIC_LANDING_V1_LANDED.md
echo "===== DONE ====="
