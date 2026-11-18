#!/usr/bin/env bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=/home/yuewuya/.openclaw/workspace/projects/smart_glasses/tmp/iss299_tmp
echo "===== TMPDIR=$TMPDIR · $(date -Is) ====="
echo "===== A) 5 个 selftest (TMPDIR 指向项目 tmp·绕开 /tmp 用户配额★实测 /tmp 已 EDQUOT★) ====="
python3 HW/check_fsin_rootcause.py --selftest        ; echo "rc=$? fsin selftest"
python3 HW/check_g1a7_selection_landed.py --selftest ; echo "rc=$? g1a7 selftest"
python3 HW/check_onepass_commit_order.py --selftest  ; echo "rc=$? commit_order selftest"
python3 HW/check_onepass_preflight_coverage.py --selftest ; echo "rc=$? preflight selftest"
python3 HW/check_workpack_state_values.py --selftest ; echo "rc=$? workpack selftest"
python3 HW/check_pin_function_labels.py --selftest   ; echo "rc=$? pin_labels selftest"
python3 HW/board_reboard.py --selftest               ; echo "rc=$? board_reboard selftest"
echo
echo "===== B) state 链 ====="
python3 state/merge.py      ; echo "rc=$? merge"
python3 state/gate_check.py ; echo "rc=$? gate_check"
python3 state/issue_check.py; echo "rc=$? issue_check"
echo
echo "===== C) 受保护 5 件 ====="
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
ls -la --time-style=full-iso HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
echo
echo "===== D) 分片 ====="
grep -c iss299 state/fragments/hw.yaml ; echo "grep_rc=$?"
echo "===== DONE $(date -Is) ====="
