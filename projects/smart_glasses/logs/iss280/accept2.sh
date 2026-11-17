#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
echo "### B1 merge.py"
python3 state/merge.py > /tmp/iss280_merge.log 2>&1; echo ">>> RC=$?"; tail -5 /tmp/iss280_merge.log
echo
echo "### B2 gate_check.py"
python3 state/gate_check.py > /tmp/iss280_gate.log 2>&1; echo ">>> RC=$?"; grep -n "Q1 交付齐备率" /tmp/iss280_gate.log
echo
echo "### B3 check_pcb_nets key lines"
bash state/pcbnew_py.sh state/check_pcb_nets.py > /tmp/iss280_nets.log 2>&1; echo ">>> RC=$?"; grep -n "缺失\|多余\|同号异网" /tmp/iss280_nets.log | head -6
echo
echo "### B4 issue_check.py (after fragment+merge)"
python3 state/issue_check.py > /tmp/iss280_issue.log 2>&1; echo ">>> RC=$?"; tail -3 /tmp/iss280_issue.log
echo
echo "### B5 protected md5 FINAL"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
echo "### B6 DONE"
