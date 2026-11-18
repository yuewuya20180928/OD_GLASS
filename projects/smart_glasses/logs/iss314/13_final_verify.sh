#!/usr/bin/env bash
# ISS-314 交卷前终验 (★只读·★输出原样贴进交卷单★)
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss314_tmp

echo "=============================================================="
echo "ISS-314 · 交卷前终验"
echo "=============================================================="

echo
echo "---- ① 零写板双证 (★跑后实测·与任务书给的基线对★) ----"
md5sum HW/PCB/demo_mainboard.kicad_pcb
stat -c '%n  mtime=%y  size=%s' HW/PCB/demo_mainboard.kicad_pcb
echo "★任务书给的基线: md5=611b869e13518c3c023fb178f91a0075  mtime=2026-11-06 07:07:17"

echo
echo "---- ② 零落表 (★网表/脚表/BOM/落表台账 md5+mtime★) ----"
md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/SCHEMATIC_LANDING_V1_LANDED.md
stat -c '%n  mtime=%y' HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv HW/SCHEMATIC_LANDING_V1_LANDED.md

echo
echo "---- ③ 零改闸 (★受保护判据脚本 md5·作业包 §5 登记值应一致★) ----"
md5sum state/check_pcb_nets.py state/check_pcb_drc.py state/compare_arm_official.py \
       HW/check_netlist_contradiction_r3.py state/gen_bom.py state/gen_pcb_netlist_board.py \
       state/gen_kicad_sch.py state/chain_gate.py state/gate_check.py state/merge.py \
       state/check_chain_content_anchor.py
echo "★作业包 §5 登记: check_pcb_nets.py=c9319f07646159799ff568f39247650d"
echo "★作业包 §5 登记: check_pcb_drc.py=1088fa4f54633d6df366e7d9c8d65006"
echo "★作业包 §5 登记: compare_arm_official.py=1471bce6cd67c4b0f611541d4a4b0dfc"
echo "★作业包 §5 登记: gen_pcb_netlist_board.py=d7ce3adca419f82176065062d33ecafb"

echo
echo "---- ④ 零重生成 (★投产包一个字节没动★) ----"
md5sum HW/PCB/production/MANIFEST.md5
find HW/PCB/production -type f | wc -l | sed 's/^/投产包文件数: /'

echo
echo "---- ⑤ 现状 C1 读数 (★预期 rc=1 · 缺失 0 / 多余 2 / 同号异网 3★) ----"
bash state/pcbnew_py.sh state/check_pcb_nets.py 2>&1 | sed -n '1,12p'
echo "rc=${PIPESTATUS[0]}"

echo
echo "---- ⑥ chain_gate (★预期 rc=1 · ③⑤ 两条红·原样保留★) ----"
python3 state/chain_gate.py 2>&1 | sed -n '1,26p'
echo "rc=${PIPESTATUS[0]}"

echo
echo "---- ⑦ merge + gate_check (★rc 必须 0 · Q1 必须 18/18★) ----"
python3 state/merge.py; echo "merge rc=$?"
python3 state/gate_check.py 2>&1 | sed -n '1,14p'; echo "gate_check rc=${PIPESTATUS[0]}"

echo
echo "---- ⑧ 沙盒目录 (★跑完即删·交卷时这两个目录必须不存在★) ----"
ls -d tmp/iss314_sandbox tmp/iss314_tmp 2>&1 | sed 's/^/  /'

echo
echo "---- ⑨ 本单落点 (★只有这 4 类★) ----"
ls -la HW/PCB/ONETRIP_S1_REF_RENAME_CALIBER.md "HANDOFF/2026-11-18_hw-lead_ISS314_S1位号改名口径收口.md" 2>&1
ls logs/iss314/ | wc -l | sed 's/^/logs\/iss314\/ 文件数: /'
echo "=============================================================="
echo "ISS-314 终验结束"
echo "=============================================================="
