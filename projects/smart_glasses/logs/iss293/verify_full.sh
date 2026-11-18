#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
echo "=== [A] timing_check.py --only F4_adc_det ==="
python3 SW/tools/timing_check.py --only F4_adc_det; echo "rc=$?"
echo "=== [B] timing_check.py --only F4D_usb_vbus_det ==="
python3 SW/tools/timing_check.py --only F4D_usb_vbus_det; echo "rc=$?"
echo "=== [C] check_demo_panel_spec.py ==="
python3 SW/tools/check_demo_panel_spec.py; echo "rc=$?"
echo "=== [D] check_demo_panel_spec.py --selftest ==="
python3 SW/tools/check_demo_panel_spec.py --selftest; echo "rc=$?"
