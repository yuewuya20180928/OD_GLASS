#!/usr/bin/env bash
# ISS-281 验收脚本 (★本机实跑 · rc 原样落日志★)
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
LOG=logs/iss281/acceptance.log
: > "$LOG"
run() {
  echo "########## \$ $* ##########" >> "$LOG"
  "$@" >> "$LOG" 2>&1
  local rc=$?
  echo "########## rc=$rc  ★($1)##########" >> "$LOG"
  echo "" >> "$LOG"
}

run python3 HW/check_onepass_s10_manifest.py
run python3 HW/check_onepass_s10_manifest.py --selftest
run python3 HW/check_onepass_s10_manifest.py --demo-sandbox
run python3 HW/check_onepass_commit_order.py
run python3 HW/check_onepass_commit_order.py --selftest
run python3 HW/check_onepass_preflight_coverage.py
run python3 HW/check_onepass_preflight_coverage.py --selftest
run python3 state/check_pcb_drc.py
run bash state/pcbnew_py.sh state/check_pcb_nets.py
run python3 state/merge.py
run python3 state/gate_check.py
run python3 state/issue_check.py
run md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
echo "########## DONE ##########" >> "$LOG"
