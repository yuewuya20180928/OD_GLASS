#!/usr/bin/env bash
# =============================================================================
# run_iss344.sh —— ISS-344 一条命令复现全部读数 (★sw-lead · 2026-11-23★)
# =============================================================================
# ★**用法**: cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
#            bash logs/iss344/run_iss344.sh
# ★**产出**: logs/iss344/*.txt (★机器生成的命令输出·一条命令能复现★)
# ★**纪律**: ★零写板 · 零落表 · 零改固件本体 · 零改板侧判据 · 零外发 ★
set -u
cd "$(dirname "$0")/../.." || exit 2
P=$(pwd)
export TMPDIR="$P/tmp"
L=logs/iss344

echo "═══ ISS-344 全量读数 (生成于 $(date '+%Y-%m-%d %H:%M:%S %Z') ) ═══" | tee "$L/00_run_header.txt"

# ── ① 新闸 (真件) ───────────────────────────────────────────────────────────
{ echo "═══ ① 新闸跑真件: SW/tools/check_sw_zero_copper_grade_consistency.py ═══"
  python3 SW/tools/check_sw_zero_copper_grade_consistency.py; echo "GATE344_RC=$?"; } \
  > "$L/01_gate_green.txt" 2>&1

# ── ② 反向用例 (★只在 tmp/ 副本上做★) ─────────────────────────────────────
{ echo "═══ ② 反向用例: §3 表某条必需网改回 NC ⇒ 必须判红并点名 ═══"
  python3 logs/iss344/reverse_case.py JTAG_TDI; echo "REVCASE_RC=$?"; } \
  > "$L/02_reverse_case_red.txt" 2>&1

# ── ③ 只增不删自证 ────────────────────────────────────────────────────────
{ echo "═══ ③ 追加式订正 · 只增不删自证 ═══"
  python3 logs/iss344/check_only_additions.py \
    tmp/iss344/orig_ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md \
    SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md; echo "ONLYADD_RC=$?"; } \
  > "$L/03_only_additions_proof.txt" 2>&1

# ── ④ 人工可读的完整 diff ─────────────────────────────────────────────────
{ echo "═══ ④ 完整 diff (老件 → 新件) ═══"
  echo "★老 md5: $(md5sum tmp/iss344/orig_ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md | cut -d' ' -f1)"
  echo "★新 md5: $(md5sum SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md | cut -d' ' -f1)"
  echo '★说明: 下面以 "<" 开头的行 = 14 个【被行内插入】的表格行 (老字符一个没少) ⇒ 见 03 的字符级子序列自证'
  diff -u tmp/iss344/orig_ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md \
          SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md; } \
  > "$L/04_diff_only_additions.txt" 2>&1

# ── ⑤ 必跑命令 (★任务书 §3·逐字★) ─────────────────────────────────────────
{ echo "═══ ⑤ 必跑命令 (任务书 §3 逐字) ═══"
  TMPDIR=$PWD/tmp python3 HW/check_s8_target_list.py HW/PCB/demo_mainboard.kicad_pcb --baseline state/.lastgood/best_v76mg1_clrfix.kicad_pcb ; echo "S8_RC=$?"
  TMPDIR=$PWD/tmp python3 SW/tools/check_sw_ref_reachability.py ; echo "REF_RC=$?"
  TMPDIR=$PWD/tmp python3 SW/tools/check_onepass_sw_release.py ; echo "SWREL_RC=$?"
  TMPDIR=$PWD/tmp python3 state/merge.py ; echo "MERGE_RC=$?"
  TMPDIR=$PWD/tmp python3 state/gate_check.py ; echo "GATE_RC=$?"
  md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb ; } \
  > "$L/05_mandatory_commands.txt" 2>&1

# ── ⑥ 边界自证 (★零写板/零落表/零改固件本体/零改板侧判据★) ────────────────
{ echo "═══ ⑥ 边界自证 (md5 逐字节) ═══"
  echo "--- 板 (★必须仍 = 611b869e13518c3c023fb178f91a0075·mtime 2026-11-06 07:07:17.362193413★)"
  md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro ; stat -c '%n %y' HW/PCB/demo_mainboard.kicad_pcb
  echo "--- 落表三真源 (★必须逐字节不变★)"
  md5sum HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
  echo "--- 板侧判据 (★必须逐字节不变·只读★)"
  md5sum HW/check_s8_target_list.py
  echo "--- 固件本体 (★必须逐字节不变★)"
  md5sum SW/tools/s2_board_run.sh SW/tools/s2_rescue_config.json SW/tools/check_sw_ref_reachability.py \
         SW/tools/check_sw_ref_reachability_v2.py SW/FLASH_AND_VERSION.md SW/EVT_TEMPLATE.md \
         SW/S2_BOARD_TEST_CHECKLIST.md SW/INTEGRATION_PLAN.md SW/SW_REQUIREMENTS.md \
         SW/S2_VENDOR_QUESTION_LIST.md SW/ONETRIP_SW_RENAME_SAFETY.md SW/SW_TIMING_REVIEW.md
  echo "--- 本单允许动的三个件 (★只有 SW 页变了·另两个是新建★)"
  md5sum SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md SW/tools/check_sw_zero_copper_grade_consistency.py \
         HANDOFF/2026-11-23_sw-lead_ISS344_零铜网分级口径对账.md ; } \
  > "$L/06_boundary_md5.txt" 2>&1

# ── ⑦ 引用零假引用自检 ────────────────────────────────────────────────────
{ echo "═══ ⑦ 交卷页引用的每个文件是否都在盘 (★§2⑩ 引用零假引用★) ═══"
  for f in SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md SW/tools/check_sw_zero_copper_grade_consistency.py \
           HW/check_s8_target_list.py state/fragments/pm.yaml state/fragments/sw.yaml \
           logs/iss344/apply_iss344_corrections.py logs/iss344/check_only_additions.py \
           logs/iss344/reverse_case.py logs/iss344/iss344_sec7.md \
           logs/iss344/01_gate_green.txt logs/iss344/02_reverse_case_red.txt \
           logs/iss344/03_only_additions_proof.txt logs/iss344/04_diff_only_additions.txt \
           logs/iss344/05_mandatory_commands.txt logs/iss344/06_boundary_md5.txt \
           HANDOFF/2026-11-23_sw-lead_ISS344_零铜网分级口径对账.md \
           HANDOFF/2026-11-19_sw-lead_ISS338_9条单端脚固件引用.md \
           SW/FLASH_AND_VERSION.md SW/EVT_TEMPLATE.md SW/S2_BOARD_TEST_CHECKLIST.md \
           SW/INTEGRATION_PLAN.md SW/SW_REQUIREMENTS.md SW/S2_VENDOR_QUESTION_LIST.md \
           SW/ONETRIP_SW_RENAME_SAFETY.md SW/SW_TIMING_REVIEW.md \
           SW/tools/s2_board_run.sh SW/tools/s2_rescue_config.json SW/tools/check_sw_ref_reachability.py \
           HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv ; do
    if [ -f "$f" ]; then echo "OK   $f"; else echo "MISS $f"; fi
  done ; } > "$L/07_refs_exist.txt" 2>&1

# ── ⑧ 关键行号核对 (★§4 的 3 个问题用★) ──────────────────────────────────
{ echo "═══ ⑧ 旧分级陈述的逐处行号 (★订正前/订正后★) ═══"
  echo "--- 订正后 (真件) 的分级陈述位置"
  grep -n "真必需 4 条\|可悬空候选 4 条\|必需 2 (\|可悬空候选 6 (\|待定 1 (\|最终分级 (以 §5 表为准)\|待定** ★ | \*\*1\*\*" \
       SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md | cut -c1-220
  echo "--- 订正标记 (【ISS344-CORR】) 出现次数"
  grep -c "ISS344-CORR" SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md ; } \
  > "$L/08_grade_lines.txt" 2>&1

# ── ⑨ 引用 file:line 逐个在盘核对 (★§2⑩ 引用零假引用★) ────────────────────
{ echo "═══ ⑨ 交卷页/SW 页引用的 file:line 逐个在盘核对 (★§2⑩ 引用零假引用★) ═══"
  check() { if [ -f "$1" ]; then c=$(sed -n "${2}p" "$1" | cut -c1-150);
      if [ -n "$c" ]; then echo "OK   $1:$2"; echo "       └─ $c"; else echo "EMPTY $1:$2"; fi
    else echo "MISS $1:$2"; fi; }
  check SW/FLASH_AND_VERSION.md 336;      check SW/FLASH_AND_VERSION.md 44
  check SW/FLASH_AND_VERSION.md 359;      check SW/FLASH_AND_VERSION.md 46
  check SW/FLASH_AND_VERSION.md 527;      check SW/EVT_TEMPLATE.md 503
  check SW/EVT_TEMPLATE.md 250;           check SW/S2_BOARD_TEST_CHECKLIST.md 393
  check SW/S2_BOARD_TEST_CHECKLIST.md 94; check SW/S2_VENDOR_QUESTION_LIST.md 315
  check SW/INTEGRATION_PLAN.md 717;       check SW/INTEGRATION_PLAN.md 844
  check SW/SW_REQUIREMENTS.md 684;        check SW/ONETRIP_SW_RENAME_SAFETY.md 31
  check SW/SW_TIMING_REVIEW.md 274;       check SW/tools/s2_board_run.sh 248
  check SW/tools/s2_rescue_config.json 230; check SW/tools/check_sw_ref_reachability.py 185
  check HW/netlist_v1.csv 285;            check HW/netlist_v1.csv 293
  check HW/netlist_v1.csv 294;            check HW/netlist_v1.csv 356
  check HW/netlist_v1.csv 392;            check HW/netlist_v1.csv 397
  check HW/netlist_v1.csv 399;            check HW/netlist_v1.csv 201
  check HW/netlist_v1.csv 205;            check HW/netlist_v1.csv 207
  check HW/netlist_v1.csv 304 ; } > "$L/09_ref_lines.txt" 2>&1

echo "═══ 全部读数已写入 logs/iss344/ ═══"
grep -E "^(GATE344_RC|REVCASE_RC|ONLYADD_RC|S8_RC|REF_RC|SWREL_RC|MERGE_RC|GATE_RC)=" "$L"/0*.txt 2>/dev/null | sed 's/^/  /'
md5sum HW/PCB/demo_mainboard.kicad_pcb
exit 0
