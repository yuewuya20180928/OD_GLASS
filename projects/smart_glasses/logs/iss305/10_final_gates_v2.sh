#!/usr/bin/env bash
# ISS-305 v2 · 交卷前全闸回归 (★原样 rc + 原样输出★ · 对「已签收后的现版」再跑一遍★)
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 99

{
echo "### ISS-305 · v2 交卷前全闸回归 (★原样 rc + 原样输出★)"
echo "### 时间: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "### 本轮身份: v2 复核 (★main 04:2x 已签收 ISS-305 verified/pass·交付页 04:1x 被追加 §5 ⇒ 本轮只补『现版读数 + 下游传播闭环核对』★)"

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
echo "=== ⑥ python3 state/_iss305_ball_truth_parser.py (★本单自证: 真判别式 11/11 + 排他 11/11★) ==="
md5sum state/_iss305_ball_truth_parser.py
python3 state/_iss305_ball_truth_parser.py ; echo "rc=$?"
echo "--- 关键三行 ---"
grep -E "T1 归属通过|T2 排他通过|±3 行窗口 判绿|真判别式   判绿" logs/iss305/07_ball_truth_parse.log

echo
echo "=== ⑦ 零写板 md5 (闸跑之后) ==="
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
echo "rc=$?"
stat -c '%y %n' HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
echo "rc=$?"

echo
echo "=== ⑧ 交卷单真判据 (★grep -cE 「🔄 待填」· 期望 0★) ==="
grep -cE "🔄 待填" HANDOFF/2026-11-18_hw-lead_ISS305_独立复验ISS131.md ; echo "rc=$?"

echo
echo "=== ⑨ 分片校验 (★grep -c iss305 state/fragments/hw.yaml·期望 ≥5★) ==="
grep -c iss305 state/fragments/hw.yaml ; echo "rc=$?"

echo
echo "=== ⑩ 交付页 / datasheet 三代读数 (★只读源·不许改★) ==="
stat -c '%s B  %y  %n' HW/RK3572_INQUIRY_CALIBER_V2.md HW/RK3572_INQUIRY_CALIBER_V2.md.bak_20261118_0410_overclaim_narrow
md5sum HW/RK3572_INQUIRY_CALIBER_V2.md HW/RK3572_INQUIRY_CALIBER_V2.md.bak_20261118_0410_overclaim_narrow
wc -c HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt HW/RK3572_PIN_TABLE/RK3572_datasheet_V1.1.pdf HW/RK3572_PIN_TABLE/rk3572_pins.csv
md5sum HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.txt HW/RK3572_PIN_TABLE/rk3572_datasheet_V1.1.pdf HW/RK3572_PIN_TABLE/rk3572_pins.csv

echo
echo "=== ⑪ 本单新增文件清单 (★全是新增复验工具/日志·零工程文件★) ==="
ls -la state/_iss305_ball_truth_parser.py logs/iss305/ | sed 's/^/  /'
echo "rc=$?"

echo
echo "=== ⑫ 板 md5 前后对照 (★空 = 零写板★) ==="
echo "板 611b869e13518c3c023fb178f91a0075 必须逐字节不变 (mtime 2026-11-06 07:07:17)"
} > logs/iss305/10_final_gates_v2.log 2>&1
echo "DONE rc=$?"
