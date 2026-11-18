#!/usr/bin/env bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 99
{
echo "### ISS-305 v2 · 终检 (★分片写完后必跑★)"
echo "### 时间: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo
echo "=== ① merge ==="
python3 state/merge.py ; echo "rc=$?"
echo
echo "=== ② gate_check (★Q1 必须 18/18★) ==="
python3 state/gate_check.py ; echo "rc=$?"
echo
echo "=== ③ issue_check ==="
python3 state/issue_check.py ; echo "rc=$?"
echo
echo "=== ④ 被审脚本原样复跑 (★md5 必须仍是 6fff079d…★) ==="
md5sum state/_iss131_crosscheck_rk3572_caliber.py
python3 state/_iss131_crosscheck_rk3572_caliber.py ; echo "rc=$?"
echo
echo "=== ⑤ 真判别式解析器复跑 ==="
python3 state/_iss305_ball_truth_parser.py >/dev/null ; echo "rc=$?"
grep -E "T1 归属通过|T2 排他通过|窗口 判绿|真判别式   判绿" logs/iss305/07_ball_truth_parse.log
echo
echo "=== ⑥ 零写板终检 (★板 611b869e… 必须逐字节不变★) ==="
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y %n' HW/PCB/demo_mainboard.kicad_pcb
echo
echo "=== ⑦ 交卷单真判据 (★期望 0★) ==="
grep -cE "🔄 待填" HANDOFF/2026-11-18_hw-lead_ISS305_独立复验ISS131.md ; echo "rc=$?"
echo
echo "=== ⑧ 分片校验 (★期望 ≥5★) ==="
grep -c iss305 state/fragments/hw.yaml ; echo "rc=$?"
grep -c iss305_v2 state/fragments/hw.yaml ; echo "rc=$?"
echo
echo "=== ⑨ 交付页 / 被审脚本 / datasheet 读数终检 ==="
stat -c '%s B  %y  %n' HW/RK3572_INQUIRY_CALIBER_V2.md state/_iss131_crosscheck_rk3572_caliber.py
md5sum HW/RK3572_INQUIRY_CALIBER_V2.md state/_iss131_crosscheck_rk3572_caliber.py
echo
echo "=== ⑩ 本单 v2 新增文件 (★全是日志·零工程文件★) ==="
ls -la logs/iss305/09_* logs/iss305/10_* logs/iss305/11_* | sed 's/^/  /'
echo
echo "=== ⑪ 交卷单最终读数 ==="
wc -c -l HANDOFF/2026-11-18_hw-lead_ISS305_独立复验ISS131.md
} > logs/iss305/11_final_verify_v2.log 2>&1
echo "DONE rc=$?"
