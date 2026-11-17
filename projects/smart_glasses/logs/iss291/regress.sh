#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
echo "=== ① timing_check.py ==="
python3 SW/tools/timing_check.py >/tmp/iss291_tc.txt 2>&1; echo "rc=$?"; tail -2 /tmp/iss291_tc.txt
echo "=== ② check_demo_panel_spec.py ==="
python3 SW/tools/check_demo_panel_spec.py >/tmp/iss291_dps.txt 2>&1; echo "rc=$?"; tail -3 /tmp/iss291_dps.txt
echo "=== ③ check_demo_panel_spec.py --selftest ==="
python3 SW/tools/check_demo_panel_spec.py --selftest >/tmp/iss291_dpss.txt 2>&1; echo "rc=$?"; tail -3 /tmp/iss291_dpss.txt
echo "=== ④ HW/check_step1_parts_spec.py ==="
python3 HW/check_step1_parts_spec.py >/tmp/iss291_s1.txt 2>&1; echo "rc=$?"; tail -3 /tmp/iss291_s1.txt
echo "=== ⑤ state/merge.py ==="
python3 state/merge.py >/tmp/iss291_merge.txt 2>&1; echo "rc=$?"; tail -3 /tmp/iss291_merge.txt
echo "=== ⑥ state/gate_check.py ==="
python3 state/gate_check.py >/tmp/iss291_gate.txt 2>&1; echo "rc=$?"; tail -3 /tmp/iss291_gate.txt
echo "=== ⑦ state/issue_check.py ==="
python3 state/issue_check.py >/tmp/iss291_iss.txt 2>&1; echo "rc=$?"; tail -3 /tmp/iss291_iss.txt
echo "=== ⑧ md5 protected ==="
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
echo "=== ⑨ timing_check.py md5 + 行数 ==="
md5sum SW/tools/timing_check.py; wc -l SW/tools/timing_check.py
