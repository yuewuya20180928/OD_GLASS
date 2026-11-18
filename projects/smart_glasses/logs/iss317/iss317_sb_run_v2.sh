#!/usr/bin/env bash
# ISS-317 沙盒驱动 v2 (★v1 的 乙/丙 两场是崩的 · 本版重跑全部★)
# ★只读项目文件 + 只写 tmp/iss317_sandbox/ 与 logs/iss317/ ★
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
export TMPDIR=$PWD/tmp/iss317_tmp
mkdir -p "$TMPDIR"
SB=tmp/iss317_sandbox
R="bash state/pcbnew_py.sh"

run () {   # $1=tag $2=判据脚本 $3=板 $4=网表(可空) $5=额外参数(可空)
  local tag="$1" sc="$2" brd="$3" net="${4:-}" extra="${5:-}"
  local out="$SB/raw_${tag}.txt"
  local cmd="$R $sc"
  [ -n "$net" ] && cmd="$cmd --net=$net"
  [ -n "$brd" ] && cmd="$cmd --pcb=$brd"
  [ -n "$extra" ] && cmd="$cmd $extra"
  $cmd > "$out" 2>&1
  echo "rc=$?" >> "$out"
  echo "=================== $tag ==================="
  grep -E "C1 焊盘级等价|缺失 |C3 每个器件|C2 针号/针数不符|C3 焊盘数不符|口径:|口径歧义|口径未同步|NC 焊盘落在|❌ 不通过|✅ 全过|自检通过|自检失败|^rc=" "$out" | head -20
}

echo "###############################################################"
echo "# ISS-317 场景矩阵 v2 (★五侧同口径底座 + NC 白名单三选项 + T5/T6 + 丙的前缀陷阱反向用例★)"
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
echo "### A3 丙方案-①(裸前缀): 五侧同口径全改名 · 白名单按 startswith(J_USB_C) 推导"
run A3_bing_prefix $SB/chk_optC1.py $SB/board_ref1.kicad_pcb $SB/netlist_ref1.csv

echo
echo "### A4 丙方案-②(正则锚定): 五侧同口径全改名 · 白名单按 ^J_USB_C(_\d+)?\$ 推导"
run A4_bing_regex $SB/chk_optC2.py $SB/board_ref1.kicad_pcb $SB/netlist_ref1.csv

echo
echo "### A5 反向用例①: 给【非白名单】器件 C_BULK_SENSOR_CORE 造一个 NC 焊盘"
echo "###     ⇒ 期望: 丙方案-①(裸前缀) / 丙方案-②(正则) / 基座 三者都必须仍然抓住 (非法 NC ≥ 1)"
run A5_negcase_CBULK $SB/chk_optC1.py $SB/board_ref1_negNC.kicad_pcb $SB/netlist_ref1.csv
run A5b_negcase_CBULK_regex $SB/chk_optC2.py $SB/board_ref1_negNC.kicad_pcb $SB/netlist_ref1.csv
run A5c_negcase_CBULK_base $SB/chk_base.py $SB/board_ref1_negNC.kicad_pcb $SB/netlist_ref1.csv

echo
echo "### A6 反向用例②(★丙方案-① 的陷阱★): 把 C_BULK_SENSOR_CORE 改名成 J_USB_C_X 并造 NC 焊盘"
echo "###     ⇒ 期望: 裸前缀白名单会【放过】它 (非法 NC 读数比基座少 1) ⇒ 证明丙方案-① 放宽了真错"
run A6_prefixtrap_C1 $SB/chk_optC1.py $SB/board_ref1_prefixtrap.kicad_pcb $SB/netlist_ref1_prefixtrap.csv
run A6b_prefixtrap_C2 $SB/chk_optC2.py $SB/board_ref1_prefixtrap.kicad_pcb $SB/netlist_ref1_prefixtrap.csv
run A6c_prefixtrap_base $SB/chk_base.py $SB/board_ref1_prefixtrap.kicad_pcb $SB/netlist_ref1_prefixtrap.csv

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
echo "### S1 --selftest 自测: 改名后的板 + 未解封的判据 (chk_base) ⇒ 期望 selftest 能抓到脚位对调"
run S1_selftest_base $SB/chk_base.py $SB/board_ref1.kicad_pcb $SB/netlist_ref1.csv "--selftest"

echo
echo "### S2 --selftest 自测: 改名后的板 + 乙方案判据 (chk_optB) ⇒ 期望 selftest 目标已跟着改名"
run S2_selftest_optB $SB/chk_optB.py $SB/board_ref1.kicad_pcb $SB/netlist_ref1.csv "--selftest"

echo
echo "###############################################################"
echo "# 跑完"
echo "###############################################################"
