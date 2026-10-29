#!/usr/bin/env bash
# =============================================================================
# s2_board_selftest.sh —— S2 救砖链路 · 板端自检 (CB-04 的 6 项 + CB-03/07/09)
# =============================================================================
#
# 用法:
#   bash SW/tools/s2_board_selftest.sh --config <cfg> --out <json> [--log <log>]
#   bash SW/tools/s2_board_selftest.sh --selftest          # 无板自检 (期望 rc=0)
#
# 它干什么
#   在**板子上**跑 6 项启动自检 + 读版本串 + 扫错误码, 结果落成机器可读 JSON,
#   供 s2_board_judge.py 判 CB-03 / CB-04 / CB-07 / CB-09。
#
#   CB-04 的 6 项 (顺序即判定顺序):
#     1. DDR 自检        2. sensor 枚举     3. 光机 I2C 应答
#     4. NPU 模型加载    5. OD 跑通 1 帧     6. 版本块回显
#
# ★ 6 项的命令全部来自配置文件 (board_test.selftest.*), 没配的项判**未验**,
#   不许跳过、不许假装过 (ISS-080 口径: BR-01 最高只能判 ⚠️未验)。
#
# ★ 怎么在板上跑:
#   方式 A (推荐, ADB 通): adb push 本脚本 /data/local/tmp/ && adb shell sh /data/local/tmp/s2_board_selftest.sh
#   方式 B (串口):         把本脚本喂进串口 (需板端有可用的 shell)
#   方式 C (本机代跑):     bash SW/tools/s2_board_selftest.sh --config ... --out ...
#                          (此时走 adb shell 转发到板子)
#
# ★ 退出码: 0 = 6 项全过; 1 = 有项不通过; 2 = 有项未验 (命令没配/取不到); 3 = 环境错误
set -u

cd "$(dirname "$0")/../.." || exit 2

CFG="SW/tools/s2_rescue_config.json"
OUT=""
LOG=""
SELFTEST=0
REMOTE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --config)   CFG="$2"; shift 2 ;;
    --out)      OUT="$2"; shift 2 ;;
    --log)      LOG="$2"; shift 2 ;;
    --selftest) SELFTEST=1; shift ;;
    --remote)   REMOTE=1; shift ;;
    -h|--help)  sed -n '2,28p' "$0"; exit 0 ;;
    *) echo "❌ 未知参数: $1" >&2; exit 3 ;;
  esac
done

cfg_get() {
  python3 - "$CFG" "$1" <<'PY' 2>/dev/null
import json, sys
try:
    d = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception:
    sys.exit(0)
for k in sys.argv[2].split("."):
    if isinstance(d, dict) and k in d:
        d = d[k]
    else:
        sys.exit(0)
print("" if d is None else (d if isinstance(d, str) else json.dumps(d, ensure_ascii=False)))
PY
}

# ------------------------------------------------------------------ 无板自检
if [ "$SELFTEST" = "1" ]; then
  echo "=============================================================================="
  echo "s2_board_selftest 自检 (纯逻辑, 无需板子)"
  echo "=============================================================================="
  RC=0
  chk() { if [ "$2" = "$3" ]; then echo "  ✅ $1 (rc=$3, 期望 $2)"; else echo "  ❌ $1 (rc=$3, 期望 $2)"; RC=1; fi; }

  TMPD=$(mktemp -d)
  echo ""
  echo "[S1] 配置读取器可用"
  V=$(cfg_get "board_test.selftest.version_file")
  if [ -n "$V" ]; then echo "  ✅ 读到 version_file=$V"; else echo "  ✅ cfg_get 正常 (未配 → 空串, 符合预期)"; fi

  echo ""
  echo "[S2] 未配命令时判未验 (rc=2, 不许假装过)"
  python3 SW/tools/s2_board_selftest.py --config "$CFG" --out "$TMPD/o.json" --log "$TMPD/o.log" >/dev/null 2>&1
  chk "全部未配 → rc=2 (未验)" 2 $?

  echo ""
  echo "[S3] 6 项全过的合成场景 → rc=0"
  python3 SW/tools/s2_board_selftest.py --selftest --out "$TMPD/pass.json" >/dev/null 2>&1
  chk "合成全过 → rc=0" 0 $?

  echo ""
  echo "[S4] 缺一項 → rc=2"
  python3 SW/tools/s2_board_selftest.py --selftest --break sensor --out "$TMPD/break.json" >/dev/null 2>&1
  chk "缺 sensor → rc=2" 2 $?

  echo ""
  echo "[S5] 输出了机器可读 JSON"
  if [ -f "$TMPD/pass.json" ]; then
    python3 -c "
import json,sys
d=json.load(open(sys.argv[1],encoding='utf-8'))
assert 'selftest' in d and 'version_string' in d
print('  ✅ JSON 字段齐全 (selftest / version_string)')
" "$TMPD/pass.json" || { echo "  ❌ JSON 字段不全"; RC=1; }
  else
    echo "  ❌ 没产出 JSON"; RC=1
  fi

  rm -rf "$TMPD"
  echo ""
  echo "------------------------------------------------------------------------------"
  [ "$RC" = "0" ] && echo "结论: PASS (rc=0)" || echo "结论: FAIL"
  echo "证据: [实测] PC 侧自检 (脚本逻辑), 不代表板端 S2 已实测通过"
  echo "=============================================================================="
  exit $RC
fi

# ------------------------------------------------------------------ 板端执行
if [ ! -f "$CFG" ]; then
  echo "❌ 配置不存在: $CFG" >&2
  exit 3
fi
OUT=${OUT:-/tmp/s2_step4_selftest.json}
LOG=${LOG:-/tmp/s2_step4_selftest.log}

# 真正干活的逻辑放在 python 里 (板子上可能没有 bash 之外的工具链)
exec python3 SW/tools/s2_board_selftest.py --config "$CFG" --out "$OUT" --log "$LOG" \
     $( [ "$REMOTE" = "1" ] && echo --remote )
