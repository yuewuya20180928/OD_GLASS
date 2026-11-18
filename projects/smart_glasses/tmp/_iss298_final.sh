#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
L=logs/iss298/FINAL_RERUN.log
{
echo "### ISS-298 最终复跑 (2026-11-18 06:1x · 交卷前最后一趟)"
date '+%F %T %Z'
echo
echo "=== ① SW 侧那道闸 (本单改的) ==="
timeout 300 python3 SW/tools/check_onepass_sw_sync.py; echo "rc=$?"
echo
echo "=== ② 同闸反向用例 (16 条) ==="
timeout 600 python3 SW/tools/check_onepass_sw_sync.py --selftest; echo "rc=$?"
echo
echo "=== ③ 权威闸 (本单一个字节没改) ==="
timeout 300 python3 SW/tools/check_demo_panel_spec.py >/dev/null 2>&1; echo "check_demo_panel_spec.py rc=$?"
timeout 600 python3 SW/tools/check_demo_panel_spec.py --selftest 2>&1 | tail -3; echo "rc=$?"
echo
echo "=== ④ 状态链 ==="
timeout 300 python3 state/merge.py; echo "merge rc=$?"
timeout 900 python3 state/gate_check.py >/tmp/_iss298_gc.txt 2>&1; echo "gate_check rc=$?"
grep -E "Q1 交付齐备率|钉板 md5 闸链|Q7|全部检查项通过" /tmp/_iss298_gc.txt | head -8
timeout 300 python3 state/issue_check.py >/tmp/_iss298_ic.txt 2>&1; echo "issue_check rc=$?"
tail -3 /tmp/_iss298_ic.txt
echo
echo "=== ⑤ 零写板自证 (md5 + mtime) ==="
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%n mtime=%y' HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro
echo
echo "=== ⑥ 分片 + 交卷单 ==="
grep -c iss298 state/fragments/sw.yaml
ls -l HANDOFF/2026-11-17_sw-lead_ISS298_合法改板通道.md
} > "$L" 2>&1
echo "DONE rc=$?"
