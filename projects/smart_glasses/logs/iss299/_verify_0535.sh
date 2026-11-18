#!/usr/bin/env bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
echo "===== 0) 时间戳 ====="
date -Is
echo
echo "===== 1) 闸本体读数 ====="
python3 HW/check_pin_function_labels.py ;                echo "rc=$? (期望 1 · 恰好 15 条)"
python3 HW/check_pin_function_labels.py --expect-known ; echo "rc=$? (期望 0)"
python3 HW/check_pin_function_labels.py --selftest ;     echo "rc=$? (期望 0)"
echo
echo "===== 2) 其余 8 道闸 ====="
python3 HW/check_fsin_rootcause.py ;                   echo "rc=$? check_fsin_rootcause"
python3 HW/check_g1a7_selection_landed.py ;            echo "rc=$? check_g1a7_selection_landed"
python3 HW/check_onepass_commit_order.py ;             echo "rc=$? check_onepass_commit_order"
python3 HW/check_onepass_preflight_coverage.py ;       echo "rc=$? check_onepass_preflight_coverage"
python3 HW/check_workpack_state_values.py ;            echo "rc=$? check_workpack_state_values"
python3 HW/board_reboard.py --selftest ;               echo "rc=$? board_reboard --selftest"
python3 MECH/check_board_frame_coords.py ;             echo "rc=$? check_board_frame_coords"
python3 MECH/check_demo_struct_truth.py ;              echo "rc=$? check_demo_struct_truth"
python3 SW/tools/check_onepass_sw_sync.py ;            echo "rc=$? check_onepass_sw_sync"
echo
echo "===== 3) 前 5 道闸 selftest ====="
python3 HW/check_fsin_rootcause.py --selftest ;        echo "rc=$? fsin selftest"
python3 HW/check_g1a7_selection_landed.py --selftest ; echo "rc=$? g1a7 selftest"
python3 HW/check_onepass_commit_order.py --selftest ;  echo "rc=$? commit_order selftest"
python3 HW/check_onepass_preflight_coverage.py --selftest ; echo "rc=$? preflight selftest"
python3 HW/check_workpack_state_values.py --selftest ; echo "rc=$? workpack selftest"
echo
echo "===== 4) state 链 ====="
python3 state/merge.py ;                               echo "rc=$? merge"
python3 state/gate_check.py ;                          echo "rc=$? gate_check"
python3 state/issue_check.py ;                         echo "rc=$? issue_check"
echo
echo "===== 5) 受保护 5 件 md5 + mtime ====="
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
ls -la --time-style=full-iso HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
echo
echo "===== 6) 分片 ====="
grep -c iss299 state/fragments/hw.yaml ; echo "grep_rc=$?"
echo
echo "===== DONE ====="
date -Is
