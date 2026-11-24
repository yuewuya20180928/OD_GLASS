#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR="$PWD/tmp"
echo "=== BARE run1 ==="; timeout 900 python3 SW/tools/check_sw_gate_health.py 2>&1; echo "RC=$?"
echo "=== SELFTEST ==="; timeout 900 python3 SW/tools/check_sw_gate_health.py --selftest 2>&1 | tail -8; echo "RC=$?"
