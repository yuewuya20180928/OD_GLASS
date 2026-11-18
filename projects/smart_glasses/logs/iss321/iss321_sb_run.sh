#!/usr/bin/env bash
# iss321_sb_run.sh —— ISS-321 · SW 侧判据沙盒实跑 (★只写 tmp/iss321_sandbox/ + logs/iss321/★)
#
# ★场景矩阵 ★:
#   S0 = 基线 (全部软链指向真件 · 什么都没改)
#   S1 = 板/网表/脚表/BOM 改名 + SW 文档【没】改
#   S2 = 板/网表/脚表/BOM 改名 + SW 文档【同步】改
#
# ★纪律 ★:
#   · 三道 selftest 闸【必须裸跑】 (带 --selftest ⇒ rc=2 usage 错误 · ISS-318 实测过)
#   · --tmpdir 必须指项目内 tmp/ (本机 /tmp 带 usrquota 且配额已满 ⇒ 不指会 EDQUOT 假红)
#   · 闸脚本一个字节都不改 (软链到真件 · PROJ 由 __file__ 解析 ⇒ 落在沙盒根)
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
SB=tmp/iss321_sandbox
OUT=logs/iss321
mkdir -p "$OUT" tmp/iss321_gates

export TMPDIR="$PWD/tmp/iss321_gates"
export SW_SYNC_TMPDIR="$PWD/tmp/iss321_gates"

# ★闸清单: 闸名 | 额外参数 (★三道 selftest 闸参数留空 ⇒ 裸跑★) ★
GATES=(
  "check_onepass_sw_sync.py|"
  "check_sw_ref_reachability.py|"
  "check_landing_trace_obligation.py|"
  "check_demo_panel_spec.py|"
  "check_demo_panel_spec_r6_selftest.py|--tmpdir $PWD/tmp/iss321_gates"
  "check_demo_panel_spec_r6_chainjudge_selftest.py|--tmpdir $PWD/tmp/iss321_gates"
  "check_demo_panel_spec_r6_hardprot_iss315_selftest.py|--tmpdir $PWD/tmp/iss321_gates"
  "check_shutdown_semantics.py|"
  "check_timing_review_adc_sync.py|"
  "timing_check.py|"
)

run_gate () {   # $1=场景根 $2=闸文件 $3=参数
  local root="$1" gate="$2" params="$3"
  local name="${gate%.py}"
  local out="$OUT/raw_${root##*/}_${name}.txt"
  ( cd "$root" && python3 "SW/tools/$gate" $params ) > "$out" 2>&1
  local rc=$?
  echo "rc=$rc" >> "$out"
  printf '%-46s rc=%-3s %s\n' "$name" "$rc" "$out"
}

for scen in rootS0 rootS1 rootS2; do
  echo ""
  echo "═══════════════════════════════════════════════════════════════════════"
  echo "# 场景 $scen  ($SB/$scen)"
  echo "═══════════════════════════════════════════════════════════════════════"
  for spec in "${GATES[@]}"; do
    g="${spec%%|*}"; p="${spec#*|}"
    run_gate "$SB/$scen" "$g" "$p"
  done
done

echo ""
echo "###############################################################"
echo "# 跑完 · 原始输出在 $OUT/raw_*.txt"
echo "###############################################################"
