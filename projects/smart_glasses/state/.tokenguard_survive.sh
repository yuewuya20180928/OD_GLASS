#!/bin/bash
# token 守护 · 存活补推 (2026-11-22)
# 目的: cron 的 exec 有 900s 上限, 而本网络下 publish 全量传输要 ~40min ⇒ 会被中途掐断。
# 本脚本 detach 运行: 等发布锁空闲后, 完整跑一遍 publish_github.sh, 结果写日志。
# ★不碰项目文件, 只调发布脚本本身。
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
LOCK=/tmp/od_glass_publish.lock
LOG=/tmp/tokenguard_push.log
cd "$PROJ" || exit 1

echo "[$(date -Is)] 存活补推: 等待发布锁空闲 (最多 90 分钟)" >>"$LOG"
for i in $(seq 1 360); do
  if flock -n "$LOCK" -c true 2>/dev/null; then
    echo "[$(date -Is)] 锁已空闲, 开始补推" >>"$LOG"
    break
  fi
  sleep 15
done

echo "[$(date -Is)] === publish_github.sh 开始 ===" >>"$LOG"
bash state/publish_github.sh "token 守护: 限额前推进度快照" >>"$LOG" 2>&1
rc=$?
echo "[$(date -Is)] === publish 结束 rc=$rc ===" >>"$LOG"
echo "[$(date -Is)] last_github_push=$(cat state/.last_github_push 2>/dev/null)" >>"$LOG"
exit $rc
