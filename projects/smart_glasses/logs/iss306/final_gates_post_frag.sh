#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
echo "=== [1] check_stage_g1a.py ==="; python3 state/check_stage_g1a.py; echo "rc=$?"
echo "=== [2] check_netlist_selfconsistency.py --expect-resolved ==="; python3 HW/check_netlist_selfconsistency.py --expect-resolved; echo "rc=$?"
echo "=== [3] merge.py ==="; python3 state/merge.py; echo "rc=$?"
echo "=== [4] gate_check.py ==="; python3 state/gate_check.py 2>&1 | grep -E "Q1 交付齐备率|钉板闸链|rc=" | head -15; echo "rc(pipeline)=${PIPESTATUS[0]}"
echo "=== [5] issue_check.py ==="; python3 state/issue_check.py > /dev/null 2>&1; echo "rc=$?"
echo "=== [6] md5 ==="; md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
echo "=== [7] placeholder grep (期望 0) ==="; grep -cE "🔄|待填" "HANDOFF/2026-11-18_sw-lead_ISS306_G1a两条红溯源.md"; echo "rc=$?"
echo "=== [8] frag grep (期望 ≥5) ==="; grep -c iss306 state/fragments/sw.yaml
