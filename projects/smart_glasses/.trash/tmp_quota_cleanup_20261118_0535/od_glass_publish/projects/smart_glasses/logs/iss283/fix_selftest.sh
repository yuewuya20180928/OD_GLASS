#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
echo "########## C6 selftest"
timeout 900 python3 HW/check_board_frame_caliber.py --selftest 2>&1 | tail -40
echo "########## rc=${PIPESTATUS[0]}"
echo "########## preflight selftest"
timeout 900 python3 HW/check_onepass_preflight_coverage.py --selftest 2>&1 | tail -30
echo "########## rc=${PIPESTATUS[0]}"
