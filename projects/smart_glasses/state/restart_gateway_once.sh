#!/usr/bin/env bash
# ★【一次性·延时】重启网关, 让 `cron.maxConcurrentRuns=3` 生效 (★2026-11-10 11:4x★)
#
# ★★**为什么需要重启** ★★
#   ★`openclaw config set cron.maxConcurrentRuns 3` 已写进配置, 但**网关只在启动时读一次** ⇒ 必须重启一次才生效 ★
#   ★**这条是"cron 三条推进链连挂"的根因修法** (★详见 MEMORY.md 2026-11-10 11:0x 台账★):
#     ★`maxConcurrentRuns` 默认 = 1 ⇒ 播报 job (200~500 秒) 占着唯一那个 runner 槽位 ⇒
#     ★其它 isolated agent job 只能【排队等槽位】⇒ 而排队的看门狗只有 **60 秒** ⇒
#     ★⇒ 等不到槽位就被判 "cron: isolated agent setup timed out before runner start" ⇒
#     ★⇒ 每日巡检 (7 连挂) / 后继计划 (9 连挂) / 状态速报 (实测手动触发也被打掉) 全栽在这 ★
#
# ★**为什么延时 45 秒**: ★**让本轮的最终回复先发出去** (★网关重启会掐断正在跑的会话★) ★
#
# 用法: nohup bash state/restart_gateway_once.sh > /tmp/gw_restart.log 2>&1 &
set -u
LOG=/tmp/gw_restart.log
DELAY=45

echo "=== $(date '+%F %T') 延时 ${DELAY}s 重启网关 (让 cron.maxConcurrentRuns=3 生效) ===" > "$LOG"
sleep "$DELAY"
echo "--- 重启前 ---" >> "$LOG"
systemctl --user is-active openclaw-gateway >> "$LOG" 2>&1

echo "--- 执行 restart ---" >> "$LOG"
timeout 120 openclaw gateway restart >> "$LOG" 2>&1
echo "restart rc=$?" >> "$LOG"

sleep 20
echo "--- 重启后 ---" >> "$LOG"
systemctl --user is-active openclaw-gateway >> "$LOG" 2>&1
timeout 60 openclaw status 2>&1 | grep -iE "Gateway |Tasks |Heartbeat |Sessions " | head -8 >> "$LOG"
echo "--- 配置确认 ---" >> "$LOG"
timeout 30 openclaw config get cron.maxConcurrentRuns >> "$LOG" 2>&1
echo "=== $(date '+%F %T') 完成 ===" >> "$LOG"
