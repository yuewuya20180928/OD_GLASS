#!/usr/bin/env bash
# ★ISS-303 全量回归 (★原样 rc 逐条贴进交卷单★)
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 9
echo "### 运行时刻: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo
for cmd in \
  "python3 MECH/check_onepass_struct_crosscheck.py" \
  "python3 MECH/check_onepass_mech_release.py" \
  "python3 MECH/check_onepass_mech_sync.py" \
  "python3 MECH/check_mech_verdict_freshness.py" \
  "python3 MECH/check_demo_struct_truth.py" \
  "python3 MECH/check_board_frame_coords.py" \
  "python3 MECH/board_port_opening_s6_check.py"
do
  echo "================================================================================================"
  echo "\$ $cmd"
  $cmd
  echo "rc=$?"
  echo
done
echo "================================================================================================"
echo "\$ python3 MECH/check_onepass_mech_release.py --json  (只打 rc)"
python3 MECH/check_onepass_mech_release.py --json > /dev/null 2>&1
echo "rc=$?"
echo
echo "================================================================================================"
echo "\$ md5sum (受保护 5 件)"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
echo
echo "### 结束时刻: $(date '+%Y-%m-%d %H:%M:%S %Z')"
