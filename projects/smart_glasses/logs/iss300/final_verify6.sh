#!/usr/bin/env bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
H="HANDOFF/2026-11-17_mech-lead_ISS300_结构侧准出汇总闸.md"
echo "===== [A] 交卷单占位符自检 ====="
PAT=$'\xf0\x9f\x94\x84|\xe5\xbe\x85\xe5\xa1\xab'
grep -cE "$PAT" "$H" ; echo "★上面必须是 0★ (grep rc=$?)"
python3 state/check_report_placeholders.py < "$H" ; echo "rc=$?"
echo "===== [B] 交卷单自身字节数 + mtime ====="
ls -la --time-style=full-iso "$H"
echo "===== [C] merge ====="
python3 state/merge.py ; echo "rc=$?"
echo "===== [D] 汇总闸主跑 ====="
python3 MECH/check_onepass_mech_release.py ; echo "rc=$?"
echo "===== [E] 汇总闸 --json ====="
python3 MECH/check_onepass_mech_release.py --json ; echo "rc=$?"
echo "===== [F] 汇总闸 --selftest ====="
python3 MECH/check_onepass_mech_release.py --selftest ; echo "rc=$?"
echo "===== [G] 6 道闸本体各自 ====="
python3 MECH/check_board_frame_coords.py ; echo "rc=$?"
python3 MECH/check_demo_struct_truth.py ; echo "rc=$?"
python3 MECH/check_onepass_mech_sync.py ; echo "rc=$?"
python3 MECH/check_onepass_struct_crosscheck.py ; echo "rc=$?"
python3 MECH/board_port_opening_s6_check.py ; echo "rc=$?"
python3 MECH/check_mech_verdict_freshness.py ; echo "rc=$?"
echo "===== [H] gate_check + issue_check ====="
python3 state/gate_check.py ; echo "rc=$?"
python3 state/issue_check.py ; echo "rc=$?"
echo "===== [I] 分片 ====="
grep -c iss300 state/fragments/mech.yaml ; echo "grep_rc=$?"
echo "===== [J] 受保护 6 件 md5 + 板 mtime ====="
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv \
       HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/SCHEMATIC_LANDING_V1_LANDED.md
ls -la --time-style=full-iso HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
echo "===== [K] 闸本体 + 6 道闸本体 md5 ====="
md5sum MECH/check_onepass_mech_release.py MECH/check_board_frame_coords.py MECH/check_demo_struct_truth.py \
       MECH/check_onepass_mech_sync.py MECH/check_onepass_struct_crosscheck.py MECH/board_port_opening_s6_check.py \
       MECH/check_mech_verdict_freshness.py
echo "===== DONE ====="
