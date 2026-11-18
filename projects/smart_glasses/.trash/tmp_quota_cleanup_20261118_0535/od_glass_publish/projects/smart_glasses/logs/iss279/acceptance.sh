#!/bin/bash
# ★★ISS-279 · 验收命令全集 (★本机实跑 · rc 原样落盘★) ★★
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
LOG="$PROJ/logs/iss279/acceptance.log"
mkdir -p "$(dirname "$LOG")"
exec > >(tee "$LOG") 2>&1
cd "$PROJ" || exit 9

run() {                      # run <期望rc> <说明> <命令...>
  local want="$1"; shift
  local desc="$1"; shift
  echo "───────────────────────────────────────────────────────────"
  echo "★ 期望 rc=$want | $desc"
  echo "\$ $*"
  "$@" 2>&1 | tail -12
  local rc=${PIPESTATUS[0]}
  echo ">>> rc = $rc   (期望 $want)   $( [ "$rc" = "$want" ] && echo '✅' || echo '❌ 不符')"
  echo ""
}

echo "###############################################################################"
echo "# ISS-279 · 验收命令全集 · $(date '+%F %T %Z')"
echo "###############################################################################"
echo ""

echo "===== ★★新建 (本单)★★ ====="
run 0 "★本单新闸 (W1~W6)"            python3 SW/tools/check_onepass_sw_sync.py
run 0 "★本单新闸 --selftest (反向 ≥6)"  python3 SW/tools/check_onepass_sw_sync.py --selftest

echo "===== ★★不许被改红的既有 SW 门禁★★ ====="
run 0 "ISS-275 成果"                  python3 SW/tools/check_demo_panel_spec.py
run 0 "ISS-275 selftest (16/16)"      python3 SW/tools/check_demo_panel_spec.py --selftest
run 0 "R6 selftest (7/7)"             python3 SW/tools/check_demo_panel_spec_r6_selftest.py
run 0 "时序 (71/71)"                  python3 SW/tools/timing_check.py
run 0 "关机语义 (17/17)"              python3 SW/tools/check_shutdown_semantics.py
run 0 "亮度生物安全"                  python3 SW/tools/check_brightness_biosafety.py
run 0 "负载开关选型"                  python3 SW/tools/check_load_switch_selection.py
run 0 "demo e2e 预算"                 python3 SW/tools/demo_e2e_budget.py

echo "===== ★★板侧只读 (不许写)★★ ====="
run 0 "PCB DRC (DRC 违规 0 · unconnected 45 是既有状态)" python3 state/check_pcb_drc.py
run 1 "★既有状态: 多余 2 焊盘 (本单不负责修)" bash state/pcbnew_py.sh state/check_pcb_nets.py

echo "===== ★★状态层★★ ====="
run 0 "merge"                         python3 state/merge.py
run 0 "gate_check (Q1 18/18)"         python3 state/gate_check.py

echo "===== ★★受保护 5 件 md5 (跑后) ====="
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
echo ""
echo "基线 (2026-11-17 07:4x main 实测 / 08:2x sw-lead 实测):"
echo "  611b869e13518c3c023fb178f91a0075  HW/PCB/demo_mainboard.kicad_pcb"
echo "  3e504d2be83152e337949723e909be1b  HW/PCB/demo_mainboard.kicad_pro"
echo "  e06c1dd633566aa44732762c2ff99d1c  HW/netlist_v1.csv"
echo "  287e7861a0d1007748d92d9fbecdd490  HW/netlist_v1_pins.csv"
echo "  94642d07a69e8d60dd2af57f69b93607  HW/BOM_v1.csv"
echo ""
echo "=== 验收全集跑完 ==="
