#!/usr/bin/env bash
# ★ISS-304 · 沙盒搭建脚本 (★真盘零写★) ★
# 用法: bash tmp/iss304/mk_sandbox.sh <沙盒根>
set -euo pipefail
REAL=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
SB="${1:?用法: mk_sandbox.sh <沙盒根>}"
rm -rf "$SB"
mkdir -p "$SB/state" "$SB/HW/PCB"
FILES=(
  state/_iss277_build_preflight.py
  state/_iss277_preflight_appendix.md
  state/_iss304_ledger_fresh.py
  state/_iss304_sync_state_baseline_md5.py
  HW/BOM_v1.csv
  HW/netlist_v1.csv
  HW/netlist_v1_pins.csv
  HW/SCHEMATIC_LANDING_V1_LANDED.md
  HW/landing_md5.py
  HW/board_reboard.py
  HW/check_netlist_contradiction_r3.py
  HW/check_pin_function_labels.py
  HW/CORE_MODULE_SELECTION.md
  HW/POWER_RAIL_SPEC.md
  HW/PCB/demo_mainboard.kicad_pcb
  HW/PCB/demo_mainboard.kicad_pro
  HW/PCB/BOARD_ONEPASS_MD5_LEDGER.md
  HW/PCB/BOARD_ONEPASS_PREFLIGHT.md
  HW/PCB/BOARD_ONEPASS_WORKPACKET.md
  HW/check_workpack_state_values.py
  HW/check_board_frame_caliber.py
  state/pcbnew_py.sh
  state/check_pcb_nets.py
)
for f in "${FILES[@]}"; do
  cp "$REAL/$f" "$SB/$f"
done
echo "★沙盒已建: $SB ($(find "$SB" -type f | wc -l) 个文件)"
