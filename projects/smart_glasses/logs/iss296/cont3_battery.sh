#!/bin/bash
# ★ISS-296 cont3 · 交卷前必跑 · 最终复核轮 (★全部本机实跑·一条一条贴★)
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
LOG=logs/iss296/cont3_final_verification.log
: > "$LOG"
run() {   # run <序号> <说明> <命令...>
  local n="$1"; shift
  local desc="$1"; shift
  echo "════════ [$n] $desc" >> "$LOG"
  echo "\$ $*" >> "$LOG"
  "$@" >> "$LOG" 2>&1
  local rc=$?
  echo "--- rc=$rc" >> "$LOG"
  echo "" >> "$LOG"
  echo "[$n] rc=$rc"
  return 0
}

echo "===== ISS-296 cont3 · 交卷前必跑 · 最终复核轮 · $(date '+%F %T %z') ====="

run 1  "闸1 主跑 (MECH/check_board_frame_coords.py)"                    python3 MECH/check_board_frame_coords.py
run 2  "闸1 自检 (--selftest · ⑯a/⑯b/⑰ + ⑩c)"                          python3 MECH/check_board_frame_coords.py --selftest
run 3  "闸2 主跑 (MECH/check_demo_struct_truth.py)"                      python3 MECH/check_demo_struct_truth.py
run 4  "闸2 自检 (--selftest · R10/R11a/R11b/R12 · 28/28)"               python3 MECH/check_demo_struct_truth.py --selftest
run 5  "回归 闸3 (MECH/check_onepass_mech_sync.py)"                      python3 MECH/check_onepass_mech_sync.py
run 6  "回归 闸4 (MECH/check_onepass_struct_crosscheck.py)"              python3 MECH/check_onepass_struct_crosscheck.py
run 7  "回归 闸5 (MECH/board_port_opening_s6_check.py)"                  python3 MECH/board_port_opening_s6_check.py
run 8  "回归 闸6 (MECH/check_mech_verdict_freshness.py)"                 python3 MECH/check_mech_verdict_freshness.py
run 9  "同源探针 (MECH 解析器 vs SW 解析器 · 15 组读数)"                   python3 logs/iss296/probe_ledger_reading_same_source.py
run 10 "门禁链 ① (state/merge.py)"                                      python3 state/merge.py
run 11 "门禁链 ② (state/gate_check.py · Q1 必须 18/18)"                   python3 state/gate_check.py
run 12 "门禁链 ③ (state/issue_check.py)"                                python3 state/issue_check.py

echo "════════ [13] 分片计数 (grep -c iss296 state/fragments/mech.yaml)"
grep -c iss296 state/fragments/mech.yaml >> "$LOG" 2>&1
echo "--- count above (grep 退出码 = 0 表示找到了)" >> "$LOG"
echo "" >> "$LOG"
echo "[13] count=$(grep -c iss296 state/fragments/mech.yaml)"

echo "════════ [14] 受保护 5 件 md5 (双重自证)"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv >> "$LOG" 2>&1
ls -la --time-style=full-iso HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv >> "$LOG" 2>&1
echo "--- 落表台账 (本单零写入 · mtime 应 = ISS-302 那次落表 2026-11-18 00:22:44)" >> "$LOG"
ls -la --time-style=full-iso HW/SCHEMATIC_LANDING_V1_LANDED.md >> "$LOG" 2>&1
echo "--- 闸1 md5 (改前 051967adde31be65888de056c6fbf478 → 改后应为 5b38bf4e552b8699e8bc811b34529922)" >> "$LOG"
md5sum MECH/check_board_frame_coords.py >> "$LOG" 2>&1
echo "" >> "$LOG"
echo "[14] md5 block written"

echo "════════ [15] 本单改过的东西 (★清单·便于 main 复核★)"
echo "HANDOFF/2026-11-17_mech-lead_ISS296_合法改板机制与收工重锚.md  (追加 §8 · 老字没删)" >> "$LOG"
ls -la --time-style=full-iso "HANDOFF/2026-11-17_mech-lead_ISS296_合法改板机制与收工重锚.md" >> "$LOG" 2>&1
ls -la --time-style=full-iso state/fragments/mech.yaml >> "$LOG" 2>&1
echo "--- 别人的分片 (必须一个字节没碰)" >> "$LOG"
md5sum state/fragments/hw.yaml state/fragments/sw.yaml state/fragments/pm.yaml >> "$LOG" 2>&1
ls -la --time-style=full-iso state/fragments/hw.yaml state/fragments/sw.yaml state/fragments/pm.yaml >> "$LOG" 2>&1
echo "" >> "$LOG"

echo "===== DONE $(date '+%F %T %z') =====" >> "$LOG"
echo "===== cont3 battery finished ====="
