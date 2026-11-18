#!/usr/bin/env bash
# ISS-293 · sw-lead · B3 回归 (★别的闸一条不许红★)
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 9
echo "=== ISS-293 回归 (开始 $(date '+%F %T')) ==="

run() {  # $1=标签 $2...=命令
  local tag="$1"; shift
  local out
  out=$("$@" 2>&1); local rc=$?
  echo "--- [$tag] rc=$rc"
  echo "$out" | tail -6
  echo "###RC $tag $rc"
}

run "timing_check_full"      python3 SW/tools/timing_check.py
run "F4_adc_det"             python3 SW/tools/timing_check.py --only F4_adc_det
run "F4D_usb_vbus_det"       python3 SW/tools/timing_check.py --only F4D_usb_vbus_det
run "adc_sync_gate"          python3 SW/tools/check_timing_review_adc_sync.py
run "adc_sync_gate_selftest" python3 SW/tools/check_timing_review_adc_sync.py --selftest
run "demo_panel_spec"        python3 SW/tools/check_demo_panel_spec.py
run "demo_panel_selftest"    python3 SW/tools/check_demo_panel_spec.py --selftest
run "state_merge"            python3 state/merge.py
run "state_gate_check"       python3 state/gate_check.py
run "state_issue_check"      python3 state/issue_check.py

echo "--- 受保护 5 件 md5 + 板 mtime ---"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %n' HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
echo "--- SW 侧本次动过的两个文件 ---"
md5sum SW/SW_TIMING_REVIEW.md SW/tools/check_timing_review_adc_sync.py SW/tools/timing_check.py SW/SW_REQUIREMENTS.md
echo "=== ISS-293 回归 (结束 $(date '+%F %T')) ==="
