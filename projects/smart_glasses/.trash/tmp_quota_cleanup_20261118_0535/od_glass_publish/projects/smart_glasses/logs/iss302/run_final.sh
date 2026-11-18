#!/usr/bin/env bash
# ISS-302 cont1 · 收尾三道 (分片写完后跑) · ★原样 rc 落 logs/iss302/final_gates.log★
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 99
LOG="logs/iss302/final_gates.log"
: > "$LOG"

run() {
  local label="$1"; shift
  echo "==================================================" >> "$LOG"
  echo "### GATE: $label" >> "$LOG"
  echo "### CMD : $*" >> "$LOG"
  echo "--- output begin ---" >> "$LOG"
  "$@" >> "$LOG" 2>&1
  local rc=$?
  echo "--- output end ---" >> "$LOG"
  echo "### RC  : $rc" >> "$LOG"
  echo "### VERDICT: $label => rc=$rc" >> "$LOG"
  echo "" >> "$LOG"
  echo "$label rc=$rc"
}

echo "=== ISS-302 收尾三道 开始 $(date '+%Y-%m-%d %H:%M:%S %z') ===" | tee -a "$LOG"
run "state/merge.py"       python3 state/merge.py
run "state/gate_check.py"  python3 state/gate_check.py
run "state/issue_check.py" python3 state/issue_check.py
echo "=== 收尾三道 结束 $(date '+%Y-%m-%d %H:%M:%S %z') ===" | tee -a "$LOG"
