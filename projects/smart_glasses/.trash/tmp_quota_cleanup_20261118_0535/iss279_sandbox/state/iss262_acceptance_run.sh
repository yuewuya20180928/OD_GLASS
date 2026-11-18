#!/usr/bin/env bash
# ★ISS-262 · hw-lead 验收跑批 (★本机实跑 · 原样输出 · rc 原样记录★)
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 2
LOG="HW/ISS262_acceptance_rc.log"
: > "$LOG"
run() {
  desc="$1"; shift
  echo "" >> "$LOG"
  echo "=========================================================" >> "$LOG"
  echo "★ $desc" >> "$LOG"
  echo "\$ $*" >> "$LOG"
  out=$("$@" 2>&1); rc=$?
  echo "$out" >> "$LOG"
  echo "--- rc=$rc ---" >> "$LOG"
  echo "$desc ⇒ rc=$rc" >> "$LOG"
  return 0
}
{
echo "###################################################################"
echo "# ISS-262 · hw-lead 验收跑批 (★$(date '+%Y-%m-%d %H:%M:%S %Z')★)"
echo "# 工程根: /home/yuewuya/.openclaw/workspace/projects/smart_glasses"
echo "###################################################################"
} >> "$LOG"

echo "=== 【跑前】受保护 5 件 md5 ===" >> "$LOG"
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
        HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro >> "$LOG"

run "干跑 V-2=1 (零写盘)"       python3 state/land_v_values.py --decision V-2=1
run "干跑 V-3=E (零写盘)"       python3 state/land_v_values.py --decision V-3=E
run "干跑 V-4=680 (零写盘)"     python3 state/land_v_values.py --decision V-4=680
run "落表器自测 (≥11 条)"        python3 state/land_v_values.py --selftest
run "尺子1 网表"                python3 state/check_netlist.py
run "尺子2 脚表"                python3 state/check_netlist_pins.py
run "尺子3 ERC (期望 ERC=0)"    python3 state/check_sch_erc.py
run "尺子4 图=表"               python3 state/check_sch_pinfull.py
run "现状守卫 (期望 rc=0)"      python3 HW/check_netlist_selfconsistency.py
run "翻面口径 (期望 rc=1)"      python3 HW/check_netlist_selfconsistency.py --expect-resolved
run "G1a-7 选型落表"            python3 HW/check_g1a7_selection_landed.py
run "G1a 阶段门 (期望 rc=1)"    python3 state/check_stage_g1a.py
run "★ISS-262 新闸·体检"        python3 HW/check_land_row_anchors.py
run "★ISS-262 新闸·反向用例"    python3 HW/check_land_row_anchors.py --selftest
run "★ISS-262 新闸·机器重锚干跑" python3 HW/check_land_row_anchors.py --reanchor --dry-run
run "merge"                     python3 state/merge.py
run "gate_check (Q1 18/18)"     python3 state/gate_check.py

echo "" >> "$LOG"
echo "=== 【跑后】受保护 5 件 md5 ===" >> "$LOG"
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv \
        HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro >> "$LOG"

echo "" >> "$LOG"
echo "########## ★rc 汇总表★ ##########" >> "$LOG"
# ★★先落到临时文件再贴回 (★直接 `grep ... "$LOG" >> "$LOG"` 会边读边写自己 ⇒ 汇总表被吃空★)
__rc_tmp="$(mktemp)"
grep -E "⇒ rc=" "$LOG" > "$__rc_tmp"
cat "$__rc_tmp" >> "$LOG"
rm -f "$__rc_tmp"
echo "########## ★跑批结束★ ##########" >> "$LOG"
echo "DONE" >> "$LOG"
