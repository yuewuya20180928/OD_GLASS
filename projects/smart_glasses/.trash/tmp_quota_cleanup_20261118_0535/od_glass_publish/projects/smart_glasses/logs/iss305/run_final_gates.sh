#!/usr/bin/env bash
# ISS-305 cont1 · 交卷前全闸回归 (★原样 rc + 原样输出★)
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 99

{
echo "### ISS-305 · 交卷前全闸回归 (★原样 rc + 原样输出★)"
echo "### 时间: $(date '+%Y-%m-%d %H:%M:%S %Z')"

echo
echo "=== ① 零写板 md5 (闸跑之前) ==="
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
echo "rc=$?"
stat -c '%y %n' HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
echo "rc=$?"

echo
echo "=== ② python3 state/merge.py ==="
python3 state/merge.py ; echo "rc=$?"

echo
echo "=== ③ python3 state/gate_check.py (★Q1 必须 18/18★) ==="
python3 state/gate_check.py ; echo "rc=$?"

echo
echo "=== ④ python3 state/issue_check.py ==="
python3 state/issue_check.py ; echo "rc=$?"

echo
echo "=== ⑤ python3 state/_iss131_crosscheck_rk3572_caliber.py (★原样跑·确认没被我碰过★) ==="
md5sum state/_iss131_crosscheck_rk3572_caliber.py
python3 state/_iss131_crosscheck_rk3572_caliber.py ; echo "rc=$?"

echo
echo "=== ⑥ 零写板 md5 (闸跑之后) ==="
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
echo "rc=$?"
stat -c '%y %n' HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
echo "rc=$?"

echo
echo "=== ⑦ 交卷单真判据 (★grep -cE 「🔄 待填」· 期望 0★) ==="
grep -cE "🔄 待填" HANDOFF/2026-11-18_hw-lead_ISS305_独立复验ISS131.md ; echo "rc=$?"

echo
echo "=== ⑧ 分片校验 (★grep -c iss305 state/fragments/hw.yaml·期望 ≥5★) ==="
grep -c iss305 state/fragments/hw.yaml ; echo "rc=$?"

echo
echo "=== ⑨ 板 md5 前后对照 (★空 = 零写板★) ==="
echo "板 611b869e13518c3c023fb178f91a0075 必须逐字节不变"

echo
echo "=== ⑩ 交付页 / datasheet 读数 (★只读源·不许改★) ==="
wc -c HW/RK3572_INQUIRY_CALIBER_V2.md HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.pdf HW/RK3572_PIN_TABLE/rk3572_pins.csv
md5sum HW/RK3572_INQUIRY_CALIBER_V2.md HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.pdf HW/RK3572_PIN_TABLE/rk3572_pins.csv

echo
echo "=== ⑪ 本单新增文件 (★只新增这 3 个 + 写分片脚本★) ==="
ls -la state/_iss305_ball_truth_parser.py logs/iss305/07_ball_truth_parse.log logs/iss305/08_final_gates.log logs/iss305/write_frag.sh
echo "rc=$?"

echo
echo "### 结束: $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > logs/iss305/08_final_gates.log 2>&1

echo "done rc=$?"
