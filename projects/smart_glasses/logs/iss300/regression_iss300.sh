#!/usr/bin/env bash
# ISS-300 交卷前全套回归 (★每条都打印 rc, 一条不许将就★)
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 9
echo "##### ISS-300 回归 · $(date '+%F %T') #####"

echo ""
echo "===== 【R1】汇总闸主跑 (★必须 rc=0 且逐条列 6 道各自的 rc★) ====="
python3 MECH/check_onepass_mech_release.py
echo "R1 rc=$?"

echo ""
echo "===== 【R2】汇总闸 --selftest (★必须 rc=0★) ====="
python3 MECH/check_onepass_mech_release.py --selftest > logs/iss300/selftest_rerun.log 2>&1
echo "R2 rc=$?  (完整输出见 logs/iss300/selftest_rerun.log)"
tail -6 logs/iss300/selftest_rerun.log

echo ""
echo "===== 【R3】6 道闸本体各自读数 (★今天全 rc=0·不许变★) ====="
for f in check_board_frame_coords.py check_demo_struct_truth.py check_onepass_mech_sync.py \
         check_onepass_struct_crosscheck.py board_port_opening_s6_check.py check_mech_verdict_freshness.py; do
  python3 "MECH/$f" > "logs/iss300/gate_${f%.py}.log" 2>&1
  echo "  MECH/$f  rc=$?"
done

echo ""
echo "===== 【R4】state/merge.py (★rc=0★) ====="
python3 state/merge.py
echo "R4 rc=$?"

echo ""
echo "===== 【R5】state/gate_check.py (★rc=0 且 Q1 = 18/18★) ====="
python3 state/gate_check.py 2>&1 | tail -60
echo "R5 rc=${PIPESTATUS[0]}"

echo ""
echo "===== 【R6】state/issue_check.py (★rc=0★) ====="
python3 state/issue_check.py 2>&1 | tail -25
echo "R6 rc=${PIPESTATUS[0]}"

echo ""
echo "##### 回归结束 $(date '+%F %T') #####"
