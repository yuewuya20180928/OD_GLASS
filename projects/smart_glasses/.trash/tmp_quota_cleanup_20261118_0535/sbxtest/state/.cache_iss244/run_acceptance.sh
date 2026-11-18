#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
echo "### ① ISS-241 门禁 (上游, 本单不许把它改红)"
python3 HW/check_part_selection_matrix.py; echo "rc=$?"
echo
echo "### ①b ISS-241 门禁 --selftest"
python3 HW/check_part_selection_matrix.py --selftest; echo "rc=$?"
echo
echo "### ② merge + gate_check (Q1)"
python3 state/merge.py >/dev/null; echo "merge rc=$?"
python3 state/gate_check.py | sed -n '1,12p'; echo "gate rc=$?"
echo
echo "### ③ 本单门禁"
python3 HW/check_part_selection_gaps.py; echo "rc=$?"
echo
echo "### ④ 本单门禁 --selftest"
python3 HW/check_part_selection_gaps.py --selftest; echo "rc=$?"
echo
echo "### ⑤ LED 曲线数字化自证 (--selftest)"
python3 state/.cache_iss244/led/extract_ivif.py --selftest; echo "rc=$?"
echo
echo "### ⑥ G-10 分压候选表"
python3 state/.cache_iss244/supv_divider_solve.py | sed -n '1,12p'; echo "rc=$?"
echo
echo "### ⑦ 件数双源统计"
python3 - <<'PYEOF'
import csv, json, re
rows=list(csv.DictReader(open("HW/BOM_v1.csv",encoding="utf-8")))
pend=[r["ref"] for r in rows if "待选型" in r["value"] and r["dnp"]=="必装" and r["ref"] not in ("U_PWR_SW","U_EN_SW")]
t=open("HW/PART_SELECTION_MATRIX_2026-11-16.md",encoding="utf-8").read()
b=t.split("<!-- BEGIN 选型证据基准块 -->")[1].split("<!-- END 选型证据基准块 -->")[0]
scope=json.loads(re.sub(r"```json|```","",b.strip()))["expected_refs"]
print("ISS-241 登记范围 =",len(scope))
print("当前仍待落 =",len(pend))
print("已被并发落表落掉 =",[r for r in scope if r not in pend])
PYEOF
echo
echo "### ⑧ 受保护文件 md5 (交卷前后逐字节未变)"
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/PART_SELECTION_MATRIX_2026-11-16.md HW/check_part_selection_matrix.py
