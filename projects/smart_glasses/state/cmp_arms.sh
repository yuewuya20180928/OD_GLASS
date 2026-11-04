#!/usr/bin/env bash
# cmp_arms.sh —— ★**实验臂对比** (2026-11-05 07:45)
# 比什么: 每个臂的"布不动的脚"数 (失败脚) / 落板段数 / 用时 / 退出码
# ★口径统一: 都读日志的 [FAIL] 行 + state/_fail_detail.json (⚠️ 后者是**全局**单文件 ⇒
#   ⇒ 多个臂并行时会被互相覆盖 ⇒ 所以臂对比**只读日志**, 不读 _fail_detail.json)
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
printf "%-6s %-10s %-10s %-12s %-10s %-8s\n" 臂 层数 布不动的脚 落板段数 用时 EXIT
for name in A B C; do
  L="/tmp/v26_${name}.log"
  [ -f "$L" ] || { printf "%-6s (还没跑)\n" "$name"; continue; }
  layers=$(grep -oE "PCB_LAYERS=[0-9]+" "$L" 2>/dev/null | head -1)
  layers=$(grep -m1 "铜层数" "$L" 2>/dev/null | grep -oE "[0-9]+ 层" | head -1)
  [ -z "$layers" ] && layers="?"
  fail=$(grep -oE "布不动的脚 [0-9]+" "$L" 2>/dev/null | tail -1 | grep -oE "[0-9]+")
  [ -z "$fail" ] && fail="?"
  seg=$(grep -oE "\[SUM \] 走线 [0-9]+" "$L" 2>/dev/null | tail -1 | grep -oE "[0-9]+")
  [ -z "$seg" ] && seg="-"
  sec=$(grep -oE "用时 [0-9]+s" "$L" 2>/dev/null | tail -1 | grep -oE "[0-9]+")
  [ -z "$sec" ] && sec="-"
  ex=$(grep -oE "EXIT=[0-9]+" "$L" 2>/dev/null | tail -1)
  [ -z "$ex" ] && ex="(跑着)"
  printf "%-6s %-10s %-10s %-12s %-10s %-8s\n" "$name" "$layers" "$fail" "$seg" "$sec" "$ex"
done
echo
echo "=== 逐臂关键行 ==="
for name in A B C; do
  L="/tmp/v26_${name}.log"
  [ -f "$L" ] || continue
  echo "--- 臂 $name ---"
  grep -E "\[FAIL\]|\[SUM \]|\[CLEAN\]|落板自检|已原子替换" "$L" | tail -4
done
