#!/usr/bin/env bash
# ==============================================================================
# rk3572_rknn3_board_smoke.sh — ISS-250 · 路线② 板端验证包 (rknn3-toolkit 产物)
#   "官方 rknn3-toolkit 1.2.0 + target_platform='rk3572' 转出来的 .rknn/.weight,
#    能不能在 RK3572 板上跑通" ⇒ 一条命令出 PASS/FAIL/INDET
# ==============================================================================
# 上游 (只读引用, 本脚本不改它们):
#   · SW/RK3572_TARGET_COMPAT_V2.md      (官方口径 + 兼容矩阵)
#   · SW/research/ISS250_rknn_toolkit2_target_查证表.md  (§2 降级方案 / §3 板端清单)
#   · SW/tools/rk3572_target_smoke.sh    (路线① 版: rk3576-target 产物 + toolkit-lite2)
# 本单: ISS-250 · 交卷单 HANDOFF/2026-11-16_sw-lead_ISS250_rknn-toolkit2_RK3572_target查证与降级方案.md
#
# ★★ 为什么要有这个脚本 (路线① 那套不能直接拿来用):
#   ① 路线② 的产物是【两件套】: .rknn + 同名 .weight (官方 RKNN3 README 明文),
#      只拷 .rknn 一定失败;
#   ② 路线② 的板端 runtime 是【RKNN3】: RK3572 用 librknn3_api.so + librknn3_api_native.so,
#      而 RK3576/RK3588 用 librknn3_api.so + librknn3_api_rkcp.so (官方 demo README 原文);
#      ⇒ 路线① 脚本的 P3 (要求板端有 rknn-toolkit-lite2) 对路线② 不适用;
#   ③ 路线① 脚本的评测步依赖 lite2 的 acc 管线, 路线② 板端是 lite3 ⇒ 精度步本脚本【判 INDET】,
#      不假装能测 (要 lite3 评测器 ⇒ 已登记 need)。
#
# ★★ 铁律:
#   · **板端不许重转** —— 本脚本没有任何 convert/build 路径, 只 load + run。
#   · **纯硬件耗时 vs SDK 总耗时分开报** (SOUL.md 铁律): 本脚本默认报的是 SDK/wall 耗时,
#     纯 NPU 时间必须用 C API RKNN_QUERY_PERF_DETAIL 取, 拿不到 ⇒ N3 判 INDET, 不许顶替。
#   · **本机无板** ⇒ --dry-run 只做本地能做的检查 + 打印板端将执行的命令, rc=0。
#
# 用法:
#   bash SW/tools/rk3572_rknn3_board_smoke.sh --dry-run
#   # 板端 (★两条命令形态见 §3.2 交卷单★):
#   bash SW/tools/rk3572_rknn3_board_smoke.sh \
#     --rknn ./yolov5n_heads_int8_rk3572.rknn \
#     --weight ./yolov5n_heads_int8_rk3572.weight \
#     --expect-sha256 "$(cat yolov5n_heads_int8_rk3572.rknn.sha256)" \
#     --expect-weight-sha256 "$(cat yolov5n_heads_int8_rk3572.weight.sha256)" \
#     --power-note "<供电方式>" --out ./evidence/ISS250_rknn3_$(date +%Y%m%d)
#
#   ★ 若板端没有 rknn3_model_test 二进制, 走【官方 lite3 python 路线】:
#     --mode lite3   (需要板端装了 rknn3-toolkit-lite3, 用 from rknn.api import RKNN)
# ==============================================================================
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ="$(cd "$HERE/../.." && pwd)"

DRY=0
MODE=demo              # demo = 官方 rknn3_model_test 二进制; lite3 = 板端 python rknn.api
RKNN=""
WEIGHT=""
EXPECT_SHA=""
EXPECT_W_SHA=""
DEMO_BIN=""            # rknn3_model_test 可执行文件的路径
LIB_DIR=""             # LD_LIBRARY_PATH 指向的目录
POWER_NOTE=""
OUT=""
LOOPS=100
CORE_MASK=0x1
RETRIES=1

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)             DRY=1 ;;
    --mode)                MODE="$2"; shift ;;
    --rknn)                RKNN="$2"; shift ;;
    --weight)              WEIGHT="$2"; shift ;;
    --expect-sha256)       EXPECT_SHA="$2"; shift ;;
    --expect-weight-sha256) EXPECT_W_SHA="$2"; shift ;;
    --demo-bin)            DEMO_BIN="$2"; shift ;;
    --lib-dir)             LIB_DIR="$2"; shift ;;
    --power-note)          POWER_NOTE="$2"; shift ;;
    --out)                 OUT="$2"; shift ;;
    --loops)               LOOPS="$2"; shift ;;
    --core-mask)           CORE_MASK="$2"; shift ;;
    -h|--help)             sed -n '2,50p' "$0"; exit 0 ;;
    *) echo "未知参数: $1" >&2; exit 2 ;;
  esac
  shift
done

RES_NAME=(); RES_STATE=(); RES_DETAIL=()
record() { RES_NAME+=("$1"); RES_STATE+=("$2"); RES_DETAIL+=("$3"); }
hr()  { printf '=%.0s' {1..78}; echo; }
say() { echo "$@"; }
sha() { sha256sum "$1" 2>/dev/null | awk '{print $1}'; }

# 默认路径: 优先取项目库里已落盘的 rk3572 产物
if [ -z "$RKNN" ]; then
  for cand in "$PROJ"/SW/artifacts/models/*rk3572*.rknn; do
    [ -e "$cand" ] && { RKNN="$cand"; WEIGHT="${cand%.rknn}.weight"; break; }
  done
fi
if [ -z "$WEIGHT" ]; then
  if [ -n "$RKNN" ]; then WEIGHT="${RKNN%.rknn}.weight"; else WEIGHT="./model.weight"; fi
fi

if [ -z "$OUT" ]; then OUT="./evidence/ISS250_rknn3_$(date +%Y%m%d_%H%M%S)"; fi

# ---------------------------------------------------------------- 板端命令模板
cmd_demo() {
  echo "export LD_LIBRARY_PATH=${LIB_DIR:-./lib}"
  echo "${DEMO_BIN:-./rknn3_model_test} ${RKNN} ${WEIGHT} ${CORE_MASK} \"\" \"\" \"\" ${LOOPS}"
}
cmd_lite3() {
  cat <<EOF
python3 - <<'PY'
from rknn.api import RKNN
r = RKNN(verbose=True)
ret1 = r.load_rknn("${RKNN}", "${WEIGHT}")
print("LOAD_RKNN_RET =", ret1)
if ret1 != 0:
    raise SystemExit(2)
ret2 = r.init_runtime(target="rk3572")
print("INIT_RUNTIME_RET =", ret2)
raise SystemExit(0 if ret2 == 0 else 3)
PY
EOF
}

hr
say "ISS-250 · 路线② (rknn3-toolkit / target_platform=rk3572) 板端验证"
hr
say "MODE          : $MODE"
say "RKNN          : ${RKNN:-<未指定>}"
say "WEIGHT        : ${WEIGHT:-<未指定>}"
say "EXPECT sha256 : ${EXPECT_SHA:-<未指定 (跳过 P6 校验)>}"
say "EXPECT w-sha  : ${EXPECT_W_SHA:-<未指定>}"
say "OUT           : $OUT"

if [ "$DRY" = "1" ]; then
  hr; say "[DRY-RUN] 本机无板 ⇒ 只做本地检查 + 打印板端将执行的命令 (不假装通过)"
  hr
  say "[P1] device-tree:"
  say "    cat /proc/device-tree/compatible"
  say "[P3'] 板端 RKNN3 runtime (★RK3572 专用 native 库, 不是 rkcp★):"
  say "    ls -l /usr/lib/librknn3_api.so /usr/lib/librknn3_api_native.so"
  say "    # 或: find / -name 'librknn3_api_native.so' 2>/dev/null"
  say "[P4'] 两件套产物 (★.rknn + .weight, 缺一不可★):"
  say "    ls -l ${RKNN} ${WEIGHT}"
  say "[P6'] sha256 校验 (★两件套都要对★):"
  say "    sha256sum ${RKNN} ${WEIGHT}"
  say "[N1] 接受性 (mode=$MODE):"
  if [ "$MODE" = "lite3" ]; then cmd_lite3; else cmd_demo; fi
  say "[N3] 纯 NPU 耗时: 须 C API RKNN_QUERY_PERF_DETAIL 取 ⇒ 本脚本只报 SDK/wall 耗时 ⇒ 缺纯 NPU ⇒ N3 判 INDET"
  hr
  say "DRY-RUN OK ⇒ 板可达时把上面 [N1] 那条命令原样跑, 看返回码判定 N1"
  hr
  exit 0
fi

# ================================================================ 实跑 (在板上)
mkdir -p "$OUT" 2>/dev/null || true

# ---- P1 板型
DT=$(cat /proc/device-tree/compatible 2>/dev/null | tr -d '\0')
case "$DT" in
  *rk3572*) record P1_board_type PASS "device-tree compatible 含 rk3572"; P1_OK=1 ;;
  *)        record P1_board_type FAIL "device-tree compatible 无 rk3572 (读到: ${DT:-空}) ⇒ 不是 RK3572 板 ⇒ 停"; P1_OK=0 ;;
esac

# ---- P3' 板端 RKNN3 runtime
LIB_FOUND=""
for d in "${LIB_DIR}" ./lib /usr/lib /usr/lib/aarch64-linux-gnu /vendor/lib64; do
  [ -n "$d" ] || continue
  if [ -e "$d/librknn3_api_native.so" ]; then LIB_FOUND="$d"; break; fi
done
if [ -n "$LIB_FOUND" ]; then
  record P3_rknn3_runtime PASS "找到 librknn3_api_native.so (RK3572 native 库) @ $LIB_FOUND"; P3_OK=1
else
  record P3_rknn3_runtime FAIL "板端未找到 librknn3_api_native.so ⇒ BSP 不含 RKNN3 runtime ⇒ 路线② 跑不起来 (⇒ 板侧补 runtime, 已登记 need)"; P3_OK=0
fi

# ---- P4' 两件套产物
if [ -f "${RKNN:-/nonexistent}" ] && [ -f "${WEIGHT:-/nonexistent}" ]; then
  record P4_artifact_pair PASS ".rknn $(stat -c%s "$RKNN" 2>/dev/null) B + .weight $(stat -c%s "$WEIGHT" 2>/dev/null) B 两件套在位"; P4_OK=1
else
  record P4_artifact_pair FAIL "两件套不齐 (rknn=$RKNN weight=$WEIGHT) ⇒ RKNN3 必须 .rknn + .weight 同名成对"; P4_OK=0
fi

# ---- P6' sha256 (两件套都要)
if [ -n "$EXPECT_SHA" ] && [ -f "${RKNN:-/nonexistent}" ]; then
  A=$(sha "$RKNN")
  if [ "$A" = "$EXPECT_SHA" ]; then record P6_sha256 PASS ".rknn sha256 与 sidecar 一致 ($A)"
  else record P6_sha256 FAIL ".rknn sha256 不符 (期望 $EXPECT_SHA 实得 ${A:-读不到})"; fi
else
  record P6_sha256 INDET "未提供 --expect-sha256 或产物不在位 ⇒ 跳过 (★板端不许重转★)"
fi
if [ -n "$EXPECT_W_SHA" ] && [ -f "${WEIGHT:-/nonexistent}" ]; then
  B=$(sha "$WEIGHT")
  if [ "$B" = "$EXPECT_W_SHA" ]; then record P6w_sha256 PASS ".weight sha256 与 sidecar 一致 ($B)"
  else record P6w_sha256 FAIL ".weight sha256 不符 (期望 $EXPECT_W_SHA 实得 ${B:-读不到})"; fi
else
  record P6w_sha256 INDET "未提供 --expect-weight-sha256 ⇒ 跳过"
fi

# ---- N1 接受性
N1_STATE=INDET; N1_DETAIL="未执行"
if [ "${P1_OK:-0}" = "1" ] && [ "${P3_OK:-0}" = "1" ] && [ "${P4_OK:-0}" = "1" ]; then
  if [ "$MODE" = "lite3" ]; then
    OUT_LOG="$OUT/n1_lite3.log"
    if command -v python3 >/dev/null 2>&1; then
      cmd_lite3 > "$OUT/_n1_cmd.sh" 2>/dev/null
      bash "$OUT/_n1_cmd.sh" > "$OUT_LOG" 2>&1
      RC=$?
      if [ "$RC" = "0" ]; then N1_STATE=PASS; N1_DETAIL="load_rknn ret=0 且 init_runtime(target=rk3572) ret=0"
      elif [ "$RC" = "2" ]; then N1_STATE=FAIL; N1_DETAIL="load_rknn 失败 ⇒ 板端不接受该 .rknn/.weight (见 $OUT_LOG)"
      else N1_STATE=FAIL; N1_DETAIL="init_runtime 失败 ⇒ 板端不接受或无设备 (见 $OUT_LOG)"; fi
    else N1_DETAIL="板端无 python3 ⇒ 无法跑 lite3 探针"; fi
  else
    BIN="${DEMO_BIN:-./rknn3_model_test}"
    OUT_LOG="$OUT/n1_demo.log"
    if [ -x "$BIN" ]; then
      ( export LD_LIBRARY_PATH="${LIB_DIR:-./lib}"; "$BIN" "$RKNN" "$WEIGHT" "$CORE_MASK" "" "" "" "$LOOPS" ) > "$OUT_LOG" 2>&1
      RC=$?
      if [ "$RC" = "0" ]; then N1_STATE=PASS; N1_DETAIL="rknn3_model_test 返回 0 ⇒ 模型被 RK3572 接受 (loops=$LOOPS)"
      else N1_STATE=FAIL; N1_DETAIL="rknn3_model_test 返回 $RC ⇒ 见 $OUT_LOG"; fi
    else N1_DETAIL="未找到可执行 rknn3_model_test (--demo-bin 或 ./rknn3_model_test) ⇒ 没法判 N1"; fi
  fi
fi
record N1_acceptance "$N1_STATE" "$N1_DETAIL"

# ---- N3 纯 NPU 耗时 (本脚本只有 wall/SKD 耗时 ⇒ 按铁律判 INDET)
record N3_npu_time INDET "本脚本只采集 SDK/wall 耗时 ⇒ 纯 NPU 耗时须 C API RKNN_QUERY_PERF_DETAIL ⇒ INDET (不许拿 wall time 顶)"

# ---- N4 口径 / N5 可比性
record N4_two_numbers INDET "纯 NPU 与 SDK 总耗时须分开报; 本脚本只拿到后者 ⇒ 缺一个 ⇒ INDET"
if [ -n "$POWER_NOTE" ]; then record N5_comparability INDET "已记供电 ($POWER_NOTE); 散热/频率仍须人工记 (thermal_zone0 / cpufreq)"
else record N5_comparability INDET "供电方式未记 (--power-note) ⇒ N3/N5 不可比"; fi

# ---- 汇总
hr
i=0; FAILED=0
for n in "${RES_NAME[@]}"; do
  st="${RES_STATE[$i]}"; dt="${RES_DETAIL[$i]}"
  printf '%-18s %-6s %s\n' "$n" "$st" "$dt"
  [ "$st" = "FAIL" ] && FAILED=1
  i=$((i+1))
done
hr

mkdir -p "$OUT" 2>/dev/null || true
{
  echo "{"
  echo "  \"issue\": \"ISS-250\","
  echo "  \"route\": \"R2/rknn3-toolkit target_platform=rk3572\","
  echo "  \"mode\": \"$MODE\","
  echo "  \"rknn\": \"$RKNN\","
  echo "  \"weight\": \"$WEIGHT\","
  echo "  \"results\": ["
  i=0; first=1
  for n in "${RES_NAME[@]}"; do
    [ $first -eq 0 ] && echo ","
    first=0
    printf '    {"name": "%s", "state": "%s", "detail": "%s"}' "$n" "${RES_STATE[$i]}" "${RES_DETAIL[$i]}"
    i=$((i+1))
  done
  echo ""
  echo "  ]"
  echo "}"
} > "$OUT/summary.json"

say "summary.json → $OUT/summary.json"
if [ "$FAILED" = "1" ]; then
  hr
  say "❌ 有 FAIL ⇒ ★下一步 (不许停在等回信)★:"
  say "   · P1 FAIL      ⇒ 拿错板了 ⇒ 停, 换板"
  say "   · P3' FAIL     ⇒ 板端 BSP 没有 RKNN3 native 库 ⇒ 板侧补 runtime (need 已登记) ⇒ 补不上 ⇒ 路线③"
  say "   · P4'/P6' FAIL ⇒ 产物两件套不齐或 sha256 不符 ⇒ 重拷 (★不许在板上重转★)"
  say "   · N1 FAIL      ⇒ 路线② 板端不接受 ⇒ 转路线③ (换 SoC / 降负载)"
  say "   · N3 INDET     ⇒ 取不到纯 NPU 耗时 ⇒ 用 C API RKNN_QUERY_PERF_DETAIL 补测"
  hr
  exit 1
fi
hr
say "✅ 无 FAIL (INDET 项按判据走: N3/N4 仍需补测才能判 60 ms 硬线)"
hr
exit 0
