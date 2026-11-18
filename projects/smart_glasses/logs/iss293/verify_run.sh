#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
echo "=== [1] check_timing_review_adc_sync.py ==="
python3 SW/tools/check_timing_review_adc_sync.py; echo "rc=$?"
echo "=== [2] check_timing_review_adc_sync.py --selftest ==="
python3 SW/tools/check_timing_review_adc_sync.py --selftest; echo "rc=$?"
