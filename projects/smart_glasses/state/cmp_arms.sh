#!/usr/bin/env bash
# cmp_arms.sh —— ★**实验臂对比** (2026-11-05 07:45, 10:00 扩到四臂 + 差分指标)
# 比什么: 每个臂的"布不动的脚"数 (失败脚) / 差分对 N 侧失败数 / 落板段数 / 用时 / 退出码
# ★口径统一: 都读日志的 [FAIL] 行 (★不读 state/_fail_detail.json —— 那是**全局**单文件, 多臂并行会互相覆盖)
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
ARMS="${ARMS:-A B C D}"
printf "%-4s %-6s %-10s %-10s %-12s %-8s %-8s %-8s\n" 臂 层数 布不动的脚 N未通对 落板段数 缝合条 RIPUP救 用时
for name in $ARMS; do
  L="/tmp/v26_${name}.log"
  [ -f "$L" ] || { printf "%-4s (还没跑)\n" "$name"; continue; }
  layers=$(grep -m1 "铜层数" "$L" 2>/dev/null | grep -oE "[0-9]+" | head -1); [ -z "$layers" ] && layers="?"
  fail=$(grep -oE "布不动的脚 [0-9]+" "$L" 2>/dev/null | tail -1 | grep -oE "[0-9]+"); [ -z "$fail" ] && fail="?"
  nbad=$(grep '\[PAIR\]' "$L" 2>/dev/null | grep -c 'N 未通'); [ -z "$nbad" ] && nbad="-"
  seg=$(grep -oE "\[SUM \] 走线 [0-9]+" "$L" 2>/dev/null | tail -1 | grep -oE "[0-9]+"); [ -z "$seg" ] && seg="-"
  st=$(grep -oE "\[STITCH\].*新增 [0-9]+ 条" "$L" 2>/dev/null | grep -oE "[0-9]+" | tail -1); [ -z "$st" ] && st="-"
  rip=$(grep -oE "重布成功 [0-9]+ 个" "$L" 2>/dev/null | grep -oE "[0-9]+" | tail -1); [ -z "$rip" ] && rip="-"
  sec=$(grep -oE "用时 [0-9]+s" "$L" 2>/dev/null | tail -1 | grep -oE "[0-9]+"); [ -z "$sec" ] && sec="-"
  printf "%-4s %-6s %-10s %-10s %-12s %-8s %-8s %-8s\n" "$name" "$layers" "$fail" "$nbad" "$seg" "$st" "$rip" "$sec"
done
echo
echo "=== 逐臂关键行 ==="
for name in $ARMS; do
  L="/tmp/v26_${name}.log"
  [ -f "$L" ] || continue
  echo "--- 臂 $name ---"
  grep -E "\[FAIL\]|\[SUM \]|\[CLEAN\]|\[STITCH\]|\[RIPUP\]|落板自检|已原子替换|EXIT=" "$L" | tail -6
done
