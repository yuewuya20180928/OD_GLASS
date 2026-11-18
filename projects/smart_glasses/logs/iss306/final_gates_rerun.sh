#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
echo "=== [1] check_stage_g1a.py (期望 rc=1) ==="
python3 state/check_stage_g1a.py; echo "rc=$?"
echo "=== [2] check_netlist_selfconsistency.py --expect-resolved (期望 rc=1) ==="
python3 HW/check_netlist_selfconsistency.py --expect-resolved; echo "rc=$?"
echo "=== [3] merge.py (期望 rc=0) ==="
python3 state/merge.py; echo "rc=$?"
echo "=== [4] gate_check.py (期望 rc=0 · Q1 18/18) ==="
python3 state/gate_check.py; echo "rc=$?"
echo "=== [5] issue_check.py (期望 rc=0) ==="
python3 state/issue_check.py; echo "rc=$?"
echo "=== [6] md5 (板/网表/脚表/BOM 必须逐字节不变) ==="
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
