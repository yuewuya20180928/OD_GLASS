#!/usr/bin/env bash
# iss323_sb_run_all.sh —— ISS-323 · SW 侧判据沙盒实跑 (★8 场景 × 10 道闸 = 80 次★)
#
# ★口径与 logs/iss321/iss321_sb_run.sh 逐字同源 (★只写 tmp/iss321_sandbox/ + logs/iss323/★) ★
#   · 三道 selftest 闸【必须裸跑】 (带 --selftest ⇒ rc=2 usage 错误)
#   · --tmpdir 必须指项目内 tmp/ (★本机 /tmp 带 usrquota 且配额已满 ⇒ 不指会 EDQUOT 假红★)
#   · 闸脚本一个字节都不改 (软链到真件 ⇒ PROJ 由 __file__ 解析 ⇒ 落在沙盒根)
#
# ★与 ISS-321 的差别 ★: 输出落 logs/iss323/ (★不覆盖 ISS-321 的留档★)
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
SB=tmp/iss321_sandbox
OUT=logs/iss323
mkdir -p "$OUT" tmp/iss323_gates

export TMPDIR="$PWD/tmp/iss323_gates"
export SW_SYNC_TMPDIR="$PWD/tmp/iss323_gates"

GATES=(
  "check_onepass_sw_sync.py|"
  "check_sw_ref_reachability.py|"
  "check_landing_trace_obligation.py|"
  "check_demo_panel_spec.py|"
  "check_demo_panel_spec_r6_selftest.py|--tmpdir $PWD/tmp/iss323_gates"
  "check_demo_panel_spec_r6_chainjudge_selftest.py|--tmpdir $PWD/tmp/iss323_gates"
  "check_demo_panel_spec_r6_hardprot_iss315_selftest.py|--tmpdir $PWD/tmp/iss323_gates"
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

echo "ISS-323 · SW 侧判据沙盒实跑 (★8 场景 × 10 道闸 = 80 次·2026-11-18 本机实跑★)"
for scen in rootS0 rootS1 rootS2 rootS3 rootS4 rootS5 rootS7 rootS8; do
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
