#!/usr/bin/env bash
# ISS-324 · mech-lead · 交卷前门禁链自证 runner
# 每条命令逐个跑, 各自捕获 rc (不靠管道吞 rc) ⇒ 输出原样落盘 logs/iss324/07_gate_chain.log
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
LOG=logs/iss324/07_gate_chain.log
: > "$LOG"

say() { printf '%s\n' "$*" >> "$LOG"; }

run() {
  local desc="$1"; shift
  say ""
  say "================================================================"
  say "\$ $*"
  say "----------------------------------------------------------------"
  "$@" >> "$LOG" 2>&1
  local rc=$?
  say "[rc=$rc] $desc"
  return $rc
}

say "### ISS-324 交卷前门禁链 · 采集时刻 $(date '+%Y-%m-%d %H:%M:%S %Z')"

run "板框可行域 --json"        python3 MECH/board_frame_feasibility.py --json
run "板框可行域 --selftest"     python3 MECH/board_frame_feasibility.py --selftest
run "MECH 侧既有闸 --selftest"  python3 MECH/check_onepass_mech_sync.py --selftest
run "MECH 板框坐标闸"           python3 MECH/check_board_frame_coords.py
run "MECH 结构真值闸"           python3 MECH/check_demo_struct_truth.py
run "分片合并"                  python3 state/merge.py
run "门禁链 (Q1 必须 18/18)"    python3 state/gate_check.py

say ""
say "================================================================"
say "\$ md5sum HW/PCB/demo_mainboard.kicad_pcb   # 期望 611b869e13518c3c023fb178f91a0075"
md5sum HW/PCB/demo_mainboard.kicad_pcb >> "$LOG" 2>&1
say "\$ stat -c \"%y\" HW/PCB/demo_mainboard.kicad_pcb   # 期望 2026-11-06 07:07:17.362193413"
stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb >> "$LOG" 2>&1

say ""
say "================================================================"
say "\$ 占位符扫描 (两份交付文档都必须 0)"
say "\$ grep -cE \"🔄|待填|PLACEHOLDER|施工中\" MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md"
grep -cE "🔄|待填|PLACEHOLDER|施工中" MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md >> "$LOG" 2>&1
say "\$ grep -cE \"🔄|待填|PLACEHOLDER|施工中\" HANDOFF/2026-11-18_mech-lead_ISS324_D_LED_G落位口径.md"
grep -cE "🔄|待填|PLACEHOLDER|施工中" "HANDOFF/2026-11-18_mech-lead_ISS324_D_LED_G落位口径.md" >> "$LOG" 2>&1
say "\$ grep -c \"iss324\" state/fragments/mech.yaml"
grep -c "iss324" state/fragments/mech.yaml >> "$LOG" 2>&1

say ""
say "### 门禁链跑完 · 采集时刻 $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "OK -> $LOG"
