#!/usr/bin/env bash
# iss327_run_gates.sh —— ISS-327 · SW 侧 10 道闸在某棵沙盒根上实跑 (★只写 logs/iss327/★)
#
# ★用法★: bash logs/iss327/iss327_run_gates.sh <ROOT> <OUTDIR> <TAG>
#   ROOT   = 闸要读的那棵树 (真树 或 tmp/iss327/ 下的沙盒副本)
#   OUTDIR = 输出目录 (logs/iss327/ 下)
#   TAG    = 标签 (写进 rc 矩阵)
#
# ★纪律 (★ISS-327 任务书 §6⑧★):
#   · ★**所有闸都在 ROOT 目录里 `cd` 进去跑** ⇒ 相对路径默认值 (如 adc_sync 的 --doc "SW/SW_TIMING_REVIEW.md")
#     落到 ROOT 而不是真件
#   · ★**支持 --root 的闸额外显式传 --root "$ROOT"** ⇒ 双重保证读的是沙盒
#   · ★**timing_check.py / check_onepass_sw_sync.py 不支持 --root** ⇒ 只能靠 cd + 脚本本身在 ROOT 内
#     (沙盒里 SW/tools/*.py 是【真副本】不是软链 ⇒ PROJ 由 __file__ 解析 ⇒ 落在 ROOT)
#   · 三道 R6 selftest 闸必须裸跑 (带 --selftest ⇒ rc=2 usage 错误)
#   · --tmpdir 必须指项目内 tmp/ (★本机 /tmp 带 usrquota 且配额已满 ⇒ 不指会 EDQUOT 假红★)
set -u
ROOT="$1"
OUT="$2"
TAG="$3"
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
mkdir -p "$OUT" "$PROJ/tmp/iss327/gates_tmp"

export TMPDIR="$PROJ/tmp/iss327/gates_tmp"
export SW_SYNC_TMPDIR="$PROJ/tmp/iss327/gates_tmp"

# name|params|rootarg
GATES=(
  "check_demo_panel_spec.py||--root"
  "check_demo_panel_spec_r6_chainjudge_selftest.py|--tmpdir $PROJ/tmp/iss327/gates_tmp|--root"
  "check_demo_panel_spec_r6_hardprot_iss315_selftest.py|--tmpdir $PROJ/tmp/iss327/gates_tmp|--root"
  "check_demo_panel_spec_r6_selftest.py|--tmpdir $PROJ/tmp/iss327/gates_tmp|--root"
  "check_landing_trace_obligation.py||--root"
  "check_onepass_sw_sync.py||NONE"
  "check_shutdown_semantics.py||--root"
  "check_sw_ref_reachability.py||--root"
  "check_timing_review_adc_sync.py||NONE"
  "timing_check.py||NONE"
)

run_gate () {   # $1=闸文件 $2=参数 $3=是否支持 --root
  local gate="$1" params="$2" ra="$3"
  local name="${gate%.py}"
  local out="$OUT/${name}.txt"
  local arg=""
  [ "$ra" = "--root" ] && arg="--root $ROOT"
  ( cd "$ROOT" && python3 "SW/tools/$gate" $params $arg ) > "$out" 2>&1
  local rc=$?
  echo "rc=$rc" >> "$out"
  printf '%-48s rc=%-4s %s\n' "$name" "$rc" "$out"
}

echo "=============================================================="
echo "# ISS-327 · 闸链实跑 · TAG=$TAG · ROOT=$ROOT"
echo "# $(date '+%F %T %Z')"
echo "=============================================================="
for spec in "${GATES[@]}"; do
  g="${spec%%|*}"; rest="${spec#*|}"; p="${rest%%|*}"; ra="${rest##*|}"
  run_gate "$g" "$p" "$ra"
done
echo ""
echo "# ---- 追加: --selftest 副跑 (★不计入主表 rc·只作反向用例侧读数★) ----"
for spec in "check_demo_panel_spec.py|--root" "check_onepass_sw_sync.py|NONE" \
            "check_timing_review_adc_sync.py|NONE" "check_shutdown_semantics.py|--root" \
            "check_landing_trace_obligation.py|--root" "check_sw_ref_reachability.py|--root"; do
  g="${spec%%|*}"; ra="${spec##*|}"
  name="${g%.py}"
  out="$OUT/${name}__selftest.txt"
  arg=""; [ "$ra" = "--root" ] && arg="--root $ROOT"
  ( cd "$ROOT" && python3 "SW/tools/$g" --selftest $arg ) > "$out" 2>&1
  rc=$?
  echo "rc=$rc" >> "$out"
  printf '%-48s rc=%-4s %s\n' "${name} --selftest" "$rc" "$out"
done
echo "# ---- 跑完 ----"
