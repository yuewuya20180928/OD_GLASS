#!/usr/bin/env bash
# S2 救砖链路 —— 无板先验一键复现 (L0 + L1)
# ==============================================================================
# 用法: bash SW/tools/s2_selftest.sh
#
# 这条命令是 SW/FLASH_AND_VERSION.md §4.5.9 的 B6 自证命令之一:
#   **没有板子也能跑**, 且每一条都有明确的期望返回码 —— 期望不符 = 退出码非 0。
#
# 覆盖:
#   L0-1 分区表/版本块布局静态检查 (8 项, 期望 rc=0)
#   L0-2 容量算术: 64MB 装不下这套分区 (期望 rc=1 = 真实的约束发现)
#   L1-1 写入 + 回读校验 (15 项, 期望 rc=0)
#   L1-2 断电注入 A: 写到一半掉电 → 期望判"未生效"
#   L1-3 断电注入 B: 版本块 payload 写完、magic 未写 → 期望判"未生效"
#   L0-3 BOOT 探针纯逻辑自测 (10 项, 期望 rc=0)
#   L0-4 BOOT 探针参数齐备性检查 (期望 rc=2 = 4 个 0 数据项仍未填)
#
# ★ 本脚本跑出来的是 [实测](PC 侧), 不代表板端 S2 已通 —— 板端实测见 EVT BR-01。
set -u

cd "$(dirname "$0")/../.." || exit 2
CFG="SW/tools/s2_rescue_config.example.json"
TMP="${TMPDIR:-/tmp}/s2_selftest_$$"
mkdir -p "$TMP"
OUT="$TMP/out.txt"
PASS=0
FAIL=0

expect() {   # expect <描述> <期望rc> <实际rc>
  if [ "$2" = "$3" ]; then
    printf "  ✅ %-58s rc=%s (期望 %s)\n" "$1" "$3" "$2"
    PASS=$((PASS + 1))
  else
    printf "  ❌ %-58s rc=%s (期望 %s)\n" "$1" "$3" "$2"
    FAIL=$((FAIL + 1))
  fi
}

run() {      # run <命令...> ; 保留真实返回码到 RC, 输出进 $OUT
  "$@" > "$OUT" 2>&1
  RC=$?
}

echo "=============================================================================="
echo "ARS45 S2 救砖链路 · 无板先验 (L0 静态 + L1 仿真)"
echo "配置文件: $CFG"
echo "=============================================================================="

echo ""
echo "[L0-1] 分区表 / 版本块布局静态检查 (期望 rc=0, 8/8 通过)"
run python3 SW/tools/flash_layout_check.py --config "$CFG"
tail -6 "$OUT"
expect "L0-1 布局静态检查" 0 $RC

echo ""
echo "[L0-2] 容量算术: 这套分区表装不装得下 64MB (期望 rc=1 = 装不下, 真实约束发现)"
run python3 SW/tools/flash_layout_check.py --config "$CFG" --device-size 64MB
tail -8 "$OUT"
expect "L0-2 64MB 装不下 → FAIL" 1 $RC

echo ""
echo "[L1-1] 写入 + 回读校验 (期望 rc=0, 15/15 通过)"
run python3 SW/tools/flash_writer.py write --config "$CFG" --target "$TMP/flash.img" --synth
expect "L1-1a 写入" 0 $RC
run python3 SW/tools/flash_writer.py verify --config "$CFG" --target "$TMP/flash.img"
tail -3 "$OUT"
expect "L1-1b 回读校验" 0 $RC

echo ""
echo "[L1-2] 断电注入 A: 写到 model_a 掉电 (期望 write rc=5, verify rc=1 → 判未生效)"
run python3 SW/tools/flash_writer.py write --config "$CFG" --target "$TMP/cut.img" --synth --fail-after model_a
expect "L1-2a 断电注入 A 触发" 5 $RC
run python3 SW/tools/flash_writer.py verify --config "$CFG" --target "$TMP/cut.img"
tail -3 "$OUT"
expect "L1-2b 半写状态被判未生效" 1 $RC

echo ""
echo "[L1-3] 断电注入 B: 版本块 payload 写完、magic 未写 (期望 write rc=5, verify rc=1)"
run python3 SW/tools/flash_writer.py write --config "$CFG" --target "$TMP/vbcut.img" --synth --fail-after version_block_payload
expect "L1-3a 断电注入 B 触发" 5 $RC
run python3 SW/tools/flash_writer.py verify --config "$CFG" --target "$TMP/vbcut.img"
tail -3 "$OUT"
expect "L1-3b magic 缺失被判未生效" 1 $RC

echo ""
echo "[L0-3] BOOT 探针纯逻辑自测 (期望 rc=0, 10/10 通过)"
run python3 SW/tools/boot_rescue_probe.py --selftest
tail -4 "$OUT"
expect "L0-3 探针自测" 0 $RC

echo ""
echo "[L0-4] BOOT 探针参数齐备性 (期望 rc=2 = 4 个 0 数据项仍未填)"
run python3 SW/tools/boot_rescue_probe.py --dry-run --config "$CFG"
tail -8 "$OUT"
expect "L0-4 参数不全 → rc=2" 2 $RC

echo ""
echo "=============================================================================="
echo "结果: 通过 $PASS / 失败 $FAIL"
echo "证据: [实测](PC 侧仿真环境, 2026-10-27) —— ★不代表板端 S2 已实测通过"
echo "=============================================================================="
rm -rf "$TMP"
[ "$FAIL" = "0" ] || exit 1
exit 0
