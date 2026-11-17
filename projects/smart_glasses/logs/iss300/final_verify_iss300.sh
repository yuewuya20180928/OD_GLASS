#!/usr/bin/env bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
echo "===== [1] 汇总闸主跑 ====="
python3 MECH/check_onepass_mech_release.py ;            echo "rc=$?"
echo "===== [2] 汇总闸 --json ====="
python3 MECH/check_onepass_mech_release.py --json ;     echo "rc=$?"
echo "===== [3] 汇总闸 --selftest ====="
python3 MECH/check_onepass_mech_release.py --selftest ; echo "rc=$?"
echo "===== [4] 6 道闸本体各自 ====="
python3 MECH/check_board_frame_coords.py ;               echo "rc=$?"
python3 MECH/check_demo_struct_truth.py ;               echo "rc=$?"
python3 MECH/check_onepass_mech_sync.py ;               echo "rc=$?"
python3 MECH/check_onepass_struct_crosscheck.py ;       echo "rc=$?"
python3 MECH/board_port_opening_s6_check.py ;           echo "rc=$?"
python3 MECH/check_mech_verdict_freshness.py ;          echo "rc=$?"
echo "===== [5] state 三闸 ====="
python3 state/merge.py ;                                echo "rc=$?"
python3 state/gate_check.py ;                           echo "rc=$?"
python3 state/issue_check.py ;                          echo "rc=$?"
echo "===== [6] 分片 ====="
grep -c iss300 state/fragments/mech.yaml ;              echo "count=$?"
echo "===== [7] 受保护 6 件 md5 + 板 mtime ====="
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
md5sum HW/SCHEMATIC_LANDING_V1_LANDED.md
ls -la --time-style=full-iso HW/PCB/demo_mainboard.kicad_pcb
echo "===== [8] 闸本体字节数 + mtime ====="
ls -la --time-style=full-iso MECH/check_onepass_mech_release.py
echo "===== DONE ====="
