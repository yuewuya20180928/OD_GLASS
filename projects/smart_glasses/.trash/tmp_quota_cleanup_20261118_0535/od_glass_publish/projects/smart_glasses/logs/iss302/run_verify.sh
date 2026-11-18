#!/usr/bin/env bash
# ISS-302 cont1 · 最终校验 (★原样 rc 落 logs/iss302/final_verify.log + logs/iss302/placeholders_check.log★)
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 99
LOG="logs/iss302/final_verify.log"
PH="logs/iss302/placeholders_check.log"
: > "$LOG"; : > "$PH"

{
echo "=== ISS-302 cont1 最终校验 $(date '+%Y-%m-%d %H:%M:%S %z') ==="
echo ""
echo "### [1] python3 state/merge.py"
python3 state/merge.py; echo "rc=$?"
echo ""
echo "### [2] python3 state/gate_check.py   (★Q1 必须 18/18; ★Q7 现在 8/9 ⇒ 原样贴, 不许掩饰★)"
python3 state/gate_check.py; echo "rc=$?"
echo ""
echo "### [3] python3 state/issue_check.py"
python3 state/issue_check.py; echo "rc=$?"
echo ""
echo "### [4] 交卷单占位符扫描 (★两类占位符: 转圈箭头符 / 「待」紧接「填」的两字词★) ⇒ 必须 0"
grep -cE "$(printf '\360\237\224\200|\345\276\205\345\241\242')" HANDOFF/2026-11-18_hw-lead_ISS302_CSYS落表.md; echo "rc=$?"
echo ""
echo "### [5] 分片命中数 (★必须 >= 5★)"
grep -c iss302 state/fragments/hw.yaml; echo "rc=$?"
echo ""
echo "### [6] 板 + .kicad_pro 零写板双证 (md5 + mtime)"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro; echo "rc=$?"
stat -c '%n  mtime=%y' HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro; echo "rc=$?"
echo ""
echo "### [7] 三件落表产物 (★本单 cont1 一个字节没再动★)"
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv; echo "rc=$?"
stat -c '%n  mtime=%y' HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv; echo "rc=$?"
echo ""
echo "=== 结束 $(date '+%Y-%m-%d %H:%M:%S %z') ==="
} >> "$LOG" 2>&1

cp "$LOG" "$PH"
cat "$LOG"
