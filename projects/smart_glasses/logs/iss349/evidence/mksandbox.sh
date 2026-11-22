#!/usr/bin/env bash
# ★ISS-349 · 沙盒副本生成器 (★项目盘 tmp/iss349/ · 绝不落 /tmp★)
# 用法: bash tmp/iss349/mksandbox.sh <目标目录>
set -euo pipefail
PROJ="/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
DST="${1:?用法: mksandbox.sh <目标目录>}"
rm -rf "$DST"
mkdir -p "$DST/state/fragments" "$DST/HW/PCB"
# ★state 顶层脚本 + md + sh (★生成器与其依赖都在顶层★)
cp -a "$PROJ"/state/*.py "$PROJ"/state/*.md "$PROJ"/state/*.sh "$DST/state/" 2>/dev/null || true
# ★main 的分片 (★E-1 裁决原文的出处·生成器只读它★)
cp -a "$PROJ"/state/fragments/pm.yaml "$DST/state/fragments/pm.yaml"
# ★HW 全量 (★含板/网表/脚表/BOM/台账/各检查脚本★)
cp -a "$PROJ"/HW/. "$DST/HW/"
# ★砍掉两个大目录 (★生成器不读它们·省 28M·省时间★)
rm -rf "$DST/HW/PCB/production" "$DST/HW/PCB/_tmp_pi5"
echo "★沙盒已建: $DST"
du -sh "$DST"
