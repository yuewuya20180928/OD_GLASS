#!/usr/bin/env bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
echo "=== 1 check_onepass_mech_sync ==="
python3 MECH/check_onepass_mech_sync.py >/dev/null 2>&1; echo "rc=$?"
echo "=== 2 check_onepass_mech_sync --selftest ==="
python3 MECH/check_onepass_mech_sync.py --selftest >/dev/null 2>&1; echo "rc=$?"
echo "=== 3 check_onepass_struct_crosscheck ==="
python3 MECH/check_onepass_struct_crosscheck.py >/dev/null 2>&1; echo "rc=$?"
echo "=== 4 check_onepass_struct_crosscheck --selftest ==="
python3 MECH/check_onepass_struct_crosscheck.py --selftest >/dev/null 2>&1; echo "rc=$?"
echo "=== 5 check_mech_verdict_freshness ==="
python3 MECH/check_mech_verdict_freshness.py >/dev/null 2>&1; echo "rc=$?"
echo "=== 6 check_mech_verdict_freshness --selftest ==="
python3 MECH/check_mech_verdict_freshness.py --selftest >/dev/null 2>&1; echo "rc=$?"
echo "=== 7 merge ==="
python3 state/merge.py >/dev/null 2>&1; echo "rc=$?"
echo "=== 8 gate_check ==="
python3 state/gate_check.py >/dev/null 2>&1; echo "rc=$?"
echo "=== 9 md5 ==="
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
echo "=== 10 board mtime ==="
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
