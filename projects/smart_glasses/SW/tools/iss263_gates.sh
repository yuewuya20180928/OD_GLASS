#!/usr/bin/env bash
# ISS-263 · 验收门禁 + 受保护 5 件 md5 交卷后复查
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=/var/tmp/iss263_rknn3/tmp
mkdir -p "$TMPDIR"

echo "=== ISS263 GATE start $(date -Is) ==="
echo
echo "########## G1: python3 SW/tools/check_demo_panel_spec.py ##########"
python3 SW/tools/check_demo_panel_spec.py 2>&1 | tail -25
echo "G1_RC=${PIPESTATUS[0]}"
echo
echo "########## G2: python3 SW/tools/timing_check.py ##########"
python3 SW/tools/timing_check.py 2>&1 | tail -25
echo "G2_RC=${PIPESTATUS[0]}"
echo
echo "########## G3: state/merge.py && state/gate_check.py ##########"
python3 state/merge.py 2>&1 | tail -15
echo "G3_MERGE_RC=${PIPESTATUS[0]}"
python3 state/gate_check.py 2>&1 | tail -25
echo "G3_GATE_RC=${PIPESTATUS[0]}"
echo
echo "########## G4: 受保护 5 件 md5 (交卷后) ##########"
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
echo
echo "########## G5: toolkit2 旧环境 rknn env pip list (交卷后 · 不许变) ##########"
~/miniconda3/envs/rknn/bin/pip list 2>&1
echo
echo "########## G6: rknn3 新环境 pip list (交卷后) ##########"
~/miniconda3/envs/rknn3/bin/pip list 2>&1
echo "=== ISS263 GATE end $(date -Is) ==="
