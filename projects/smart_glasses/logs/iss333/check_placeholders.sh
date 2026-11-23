#!/usr/bin/env bash
# ISS-333 · 占位符黑名单自查 (★交卷页里逐字引用这条命令会【自匹配】⇒ 假阳★)
# -----------------------------------------------------------------------------
# ★为什么黑名单字面量放在这个脚本里, 不放在交卷页正文里 ★:
#   交卷页 B6-1 的「⑤ 边界自证」段原本逐字引用了这条 grep 命令
#   ⇒ 于是「黑名单里的词」出现在交卷页自己的正文里
#   ⇒ 再跑同一条 grep 去查交卷页 ⇒ 它【匹配到自己】⇒ 读数变成 2 而不是 0
#   ⇒ 那是【自匹配假阳】, 不是交卷页真有占位符
#   ⇒ 处置: 黑名单字面量只存在本脚本里; 交卷页只引用本脚本 ⇒ 复查命令与被查对象不再同文件
#
# 用法:
#   bash logs/iss333/check_placeholders.sh                      # 查默认交卷页 (ISS-333)
#   bash logs/iss333/check_placeholders.sh <某个 .md 路径>       # 查指定文件
# 期望: 打印 "0 <路径>" (★0 = 该文件无占位符★)
set -u

PATTERN='🔄|待填|PLACEHOLDER|施工中|__[A-Z_]+__'
PROJ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TARGET="${1:-$PROJ/HANDOFF/2026-11-18_mech-lead_ISS333_MECH侧位号可达性闸实现.md}"

n=$(grep -cE "$PATTERN" "$TARGET" || true)
echo "$n $TARGET"
[ "$n" -eq 0 ]
