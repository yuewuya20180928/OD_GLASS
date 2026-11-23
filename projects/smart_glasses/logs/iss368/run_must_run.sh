#!/usr/bin/env bash
# ISS-368 · sw-lead · 必跑命令逐条实跑 (★原样 rc 留证★)
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
OUT=logs/iss368/must_run_rc.txt
: > "$OUT"
run() {
  desc="$1"; shift
  echo "### $desc" >> "$OUT"
  echo "\$ $*" >> "$OUT"
  start=$(date +%s.%N)
  "$@" >> "$OUT" 2>&1
  rc=$?
  end=$(date +%s.%N)
  printf 'rc=%s  (%.2fs)\n\n' "$rc" "$(echo "$end - $start" | bc)" >> "$OUT"
  echo "$desc rc=$rc"
}
run "① ISS-363 新闸 (只读)"        python3 SW/tools/check_fp_truth_read.py
run "② ISS-363 新闸 selftest"      python3 SW/tools/check_fp_truth_read.py --selftest
run "③ ISS-362 影响页闸 (只读)"     python3 SW/tools/check_sw_fp_truth_impact.py
run "④ 既有闸 check_onepass_sw_sync" python3 SW/tools/check_onepass_sw_sync.py
run "⑤ 既有汇总闸 sw_release"       python3 SW/tools/check_onepass_sw_release.py
run "⑥ 幂等补丁干跑"                python3 SW/tools/apply_sw09_three_place_patch.py --dry-run
run "⑦ 本单新闸 F1~F7"             python3 SW/tools/check_sw09_patch_dryrun.py
run "⑧ 本单新闸 selftest"           python3 SW/tools/check_sw09_patch_dryrun.py --selftest
run "⑨ merge"                      python3 state/merge.py
run "⑩ gate_check"                 python3 state/gate_check.py
run "⑪ frag_write --show"          python3 state/frag_write.py --agent sw-lead --show
echo "### ⑫ md5 自证" >> "$OUT"
md5sum HW/PCB/demo_mainboard.kicad_pcb SW/BOARD_ONEPASS_SW_SYNC.md SW/BOARD_ONEPASS_FP_TRUTH_IMPACT.md SW/SW_MD5_BASELINE_LEDGER.md >> "$OUT" 2>&1
echo "rc=$?" >> "$OUT"
stat -c '%y %n' HW/PCB/demo_mainboard.kicad_pcb >> "$OUT"
echo "ALL DONE"
