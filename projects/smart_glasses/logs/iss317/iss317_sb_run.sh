#!/usr/bin/env bash
# ISS-317 沙盒驱动: 跑全部场景 ⇒ 原始读数落盘
# ★只读项目文件 + 只写 tmp/iss317_sandbox/ 与 logs/iss317/ ★
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss317_tmp
mkdir -p "$TMPDIR"
SB=tmp/iss317_sandbox
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
  grep -E "C1 焊盘级等价|缺失 |C3 每个器件|C2 针号/针数不符|C3 焊盘数不符|口径:|口径歧义|口径未同步|NC 焊盘落在|❌ 不通过|✅ 全过|^rc=" "$out" | head -16
}

echo "###############################################################"
echo "# ISS-317 场景矩阵 (★五侧同口径底座 + NC 白名单三选项 + T5/T6★)"
echo "###############################################################"

echo
echo "### A0 底座: 五侧同口径改名 (板改名 + 网表改名) · 判据不动 (★复现 ISS-314 S5★)"
run A0_base_5side $SB/chk_base.py $SB/board_ref1.kicad_pcb $SB/netlist_ref1.csv

echo
echo "### A1 甲方案: 豁免 J_USB_C 改名 (板+网表都保持 J_USB_C) · 判据不动"
run A1_jia_exempt $SB/chk_base.py $SB/board_ref1_exJUSBC.kicad_pcb $SB/netlist_ref1_exJUSBC.csv

echo
echo "### A2 乙方案: 五侧同口径全改名 · 解封判据两行 (NC_ALLOWED + --selftest 目标)"
run A2_yi_unseal $SB/chk_optB.py $SB/board_ref1.kicad_pcb $SB/netlist_ref1.csv

echo
echo "### A3 丙方案: 五侧同口径全改名 · 白名单按位号形状推导 (前缀匹配)"
run A3_bing_shape $SB/chk_optC.py $SB/board_ref1.kicad_pcb $SB/netlist_ref1.csv

echo
echo "### A4 丙方案的反向用例: 给【非白名单】器件 C_BULK_SENSOR_CORE 造一个 NC 焊盘"
echo "###     ⇒ 期望: 前缀白名单【必须】仍然把它抓住 (非法 NC ≥ 1) ⇒ 证明丙没有放宽真错"
run A4_bing_negcase $SB/chk_optC.py $SB/board_ref1_negNC.kicad_pcb $SB/netlist_ref1.csv

echo
echo "### A5 A4 的对照组: 同一个板 (带非法 NC) 跑【未改的】判据 ⇒ 非法 NC 读数应一致"
run A5_base_negcase_ctrl $SB/chk_base.py $SB/board_ref1_negNC.kicad_pcb $SB/netlist_ref1.csv

echo
echo "### T5-b 映射歧义: 板侧同名封装出现两份 + 网表不改 (原表) ⇒ 期望 ③ 红「口径歧义」"
run T5b_ambig $SB/chk_base.py $SB/board_t5b_dup.kicad_pcb ""

echo
echo "### T6-a 板侧 ref ⇒ <原名>_2 (表侧从来没有的名字) ⇒ 期望 ③ 红「口径未同步」"
run T6a_x2 $SB/chk_base.py $SB/board_t6a_x2.kicad_pcb $SB/netlist_ref1.csv

echo
echo "### T6-b 板侧 ref ⇒ <原名>_Z_1 (反查不命中) ⇒ 期望 ③ 红「口径未同步」"
run T6b_xz1 $SB/chk_base.py $SB/board_t6b_xz1.kicad_pcb $SB/netlist_ref1.csv

echo
echo "###############################################################"
echo "# 跑完"
echo "###############################################################"
