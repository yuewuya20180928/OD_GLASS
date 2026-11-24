#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR="$PWD/tmp"
for g in SW/tools/check_sw_gate_health.py MECH/check_fts_seat_body_geometry.py HW/check_fts_land_drill_same_batch.py; do
  s=$(date +%s); timeout 900 python3 "$g" >/dev/null 2>&1; rc=$?; e=$(date +%s)
  echo "BARE $g rc=$rc $((e-s))s"
  s=$(date +%s); timeout 900 python3 "$g" --selftest >/dev/null 2>&1; rc=$?; e=$(date +%s)
  echo "SELF $g rc=$rc $((e-s))s"
done
echo DONE
