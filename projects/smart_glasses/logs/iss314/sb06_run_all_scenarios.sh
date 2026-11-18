#!/usr/bin/env bash
# ISS-314 沙盒驱动: 跑全部场景 ⇒ 原始读数落盘
# ★只读项目文件 + 只写 tmp/iss314_sandbox/ ★
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss314_tmp
mkdir -p "$TMPDIR"
SB=tmp/iss314_sandbox
R="bash state/pcbnew_py.sh"

run () {   # $1=tag $2=判据脚本 $3=板 $4=网表(可空)
  local tag="$1" sc="$2" brd="$3" net="${4:-}"
  local out="$SB/raw_${tag}.txt"
  if [ -n "$net" ]; then
    $R "$sc" "$brd" "--net=$net" > "$out" 2>&1
  else
    $R "$sc" "$brd" > "$out" 2>&1
  fi
  echo "rc=$?" >> "$out"
  echo "=================== $tag ==================="
  grep -E "C1 焊盘级等价|缺失 |C3 每个器件|C2 针号/针数不符|C3 焊盘数不符|口径:|口径歧义|口径未同步|❌ 不通过|✅ 全过|^rc=" "$out" | head -14
}

echo "### S0 基线: 现役板 + 正本网表 (★项目正本判据★)"
run S0_baseline_official state/check_pcb_nets.py HW/PCB/demo_mainboard.kicad_pcb ""

echo
echo "### S1 只改板侧不改网表 (★沙盒判据 · 无反查层★)"
run S1_boardonly_noref $SB/check_pcb_nets_sandbox.py $SB/board_ref1.kicad_pcb ""

echo
echo "### S2 只改板侧不改网表 + 反查层 (★沙盒判据 · 带反查层★)"
run S2_boardonly_reflookup $SB/check_pcb_nets_reflookup.py $SB/board_ref1.kicad_pcb ""

echo
echo "### S3 只改网表不改板侧 (★沙盒判据 · 无反查层★)"
run S3_netonly_noref $SB/check_pcb_nets_sandbox.py HW/PCB/demo_mainboard.kicad_pcb $SB/netlist_ref1.csv

echo
echo "### S4 三侧同口径改名 (★沙盒判据 · 无反查层★)"
run S4_both_noref $SB/check_pcb_nets_sandbox.py $SB/board_ref1.kicad_pcb $SB/netlist_ref1.csv

echo
echo "### S5 三侧同口径改名 + 反查层 (★沙盒判据 · 带反查层★)"
run S5_both_reflookup $SB/check_pcb_nets_reflookup.py $SB/board_ref1.kicad_pcb $SB/netlist_ref1.csv

echo
echo "### S6 映射表被改坏: 板改名 + 网表缺 3 个 ref (★沙盒判据 · 带反查层★)"
run S6_broken_reflookup $SB/check_pcb_nets_reflookup.py $SB/board_ref1.kicad_pcb $SB/netlist_broken.csv

echo
echo "### S7 映射表被改坏: 板改名 + 网表缺 3 个 ref (★沙盒判据 · 无反查层★)"
run S7_broken_noref $SB/check_pcb_nets_sandbox.py $SB/board_ref1.kicad_pcb $SB/netlist_broken.csv
