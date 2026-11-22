#!/bin/bash
# ISS-335 · 交卷前必跑 (★任务书 J-9 原文 9 条 + 边界复查★)
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

echo "################ §[1] 交卷前必跑 (任务书 J-9 原文) ################"
echo "\$ python3 state/merge.py      ; echo \"MERGE_RC=\$?\""
python3 state/merge.py      ; echo "MERGE_RC=$?"
echo
echo "\$ python3 state/gate_check.py ; echo \"GATE_RC=\$?\""
python3 state/gate_check.py ; echo "GATE_RC=$?"
echo
echo "\$ python3 state/issue_check.py; echo \"ISSUE_RC=\$?\""
python3 state/issue_check.py; echo "ISSUE_RC=$?"
echo
echo "\$ python3 SW/tools/check_onepass_sw_release.py ; echo \"RELEASE_RC=\$?\""
python3 SW/tools/check_onepass_sw_release.py ; echo "RELEASE_RC=$?"
echo
echo "\$ python3 SW/tools/check_onepass_sw_release.py --selftest ; echo \"RELEASE_ST_RC=\$?\""
python3 SW/tools/check_onepass_sw_release.py --selftest ; echo "RELEASE_ST_RC=$?"
echo
echo "\$ md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c \"%y\" HW/PCB/demo_mainboard.kicad_pcb"
md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c "%y" HW/PCB/demo_mainboard.kicad_pcb
echo
echo "\$ grep -cE \"🔄|待填|PLACEHOLDER|施工中\" SW/ONETRIP_SW_RELEASE_GATE_SPEC.md"
grep -cE "🔄|待填|PLACEHOLDER|施工中" SW/ONETRIP_SW_RELEASE_GATE_SPEC.md
echo "\$ grep -cE \"🔄|待填|PLACEHOLDER|施工中\" HANDOFF/2026-11-19_sw-lead_ISS335_SW侧准出汇总闸.md"
grep -cE "🔄|待填|PLACEHOLDER|施工中" HANDOFF/2026-11-19_sw-lead_ISS335_SW侧准出汇总闸.md
echo "\$ grep -c iss335 state/fragments/sw.yaml"
grep -c iss335 state/fragments/sw.yaml
echo

echo "################ §[2] 边界复查 (板 / 网表 / 脚表 / BOM) ################"
{
  echo "# 边界基线 (ISS-335 · 交卷前 $(date '+%Y-%m-%d %H:%M:%S %z'))"
  echo "## 板"
  md5sum HW/PCB/demo_mainboard.kicad_pcb
  stat -c "%y  %s  %n" HW/PCB/demo_mainboard.kicad_pcb
  echo "## 网表/脚表/BOM"
  md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
  stat -c "%y  %s  %n" HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
} > logs/iss335/04_boundary_after.txt
cat logs/iss335/04_boundary_after.txt
echo
echo "################ §[3] 边界 diff (before vs after · 只该差时间戳行) ################"
diff logs/iss335/00_boundary_before.txt logs/iss335/04_boundary_after.txt
echo "DIFF_RC=$?  (★0 = 逐字节相同·1 = 只差 header 行★)"
echo
echo "################ §[4] 零改既有 16 道 SW 闸 + 零改 gate_check.py ################"
md5sum SW/tools/check_sw_ref_reachability.py SW/tools/check_sw_ref_reachability_v2.py state/gate_check.py
grep -c "check_sw_ref_reachability_v2" state/gate_check.py
echo "  ★↑ v2 在 gate_check.py 里的命中数 = 0 ⇒ 本单零改门禁链 (v2 未挂链)★"
echo
echo "################ §[5] 新增件清单 ################"
ls -la SW/tools/check_onepass_sw_release.py SW/ONETRIP_SW_RELEASE_GATE_SPEC.md HANDOFF/2026-11-19_sw-lead_ISS335_SW侧准出汇总闸.md
ls -la logs/iss335/
echo "FINAL_VERIFY_DONE"
