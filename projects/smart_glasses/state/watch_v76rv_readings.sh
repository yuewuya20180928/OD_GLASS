#!/usr/bin/env bash
# watch_v76rv_readings.sh -- ★★等 v76rv 出终板 ⇒ 自动出【权威读数】★★
#
# ★**为什么**: ★`/tmp/chain_<TAG>/final_chain.kicad_pcb.drc.json` 不是终板的 DRC (★是上一步的输入★)
#   ⇒ ★**谁手读它谁被骗** ⇒ ★**让机器在终板一出现就 fresh DRC 一次** ★★
# ★**它做什么 (★只读板 ⇒ 不污染任何臂★)**:
#   ① 等 `/tmp/chain_v76rv/final_chain.kicad_pcb` 出现 (★每 60s 探一次★)
#   ② 跑 `state/arm_fresh_readings.sh` (★fresh DRC + 体检错位 json + 名单差集★)
#   ③ 读数写 `/tmp/v76rv_readings.txt` + `state/v76rv_READINGS.md` ⇒ ★**主会话可以直接读文件, 不用等我广播** ★★
# ★**绝不**: ★**不开新臂** ★**不改板** ★**不动正在跑的臂脚本** ★★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

FINAL=/tmp/chain_v76rv/final_chain.kicad_pcb
OUT=/tmp/v76rv_readings.txt
MD="$PROJ/state/v76rv_READINGS.md"
DEADLINE=$(( $(date +%s) + 14400 ))   # ★最多等 4 小时★

echo "[watch] $(date '+%F %T') 开始等 $FINAL"
while [ ! -f "$FINAL" ]; do
  if [ "$(date +%s)" -gt "$DEADLINE" ]; then
    echo "[watch] $(date '+%F %T') 超时 (4h) ⇒ 退出"; exit 3
  fi
  # ★臂还活着吗 (★进程还在 ⇒ 不是卡死★)
  ALIVE=$(pgrep -f "v76rv_arms.sh|chain_v76rv" 2>/dev/null | wc -l)
  if [ "$ALIVE" -eq 0 ] && [ ! -f "$FINAL" ]; then
    # ★★**臂进程没了但终板还没出来 ⇒ 可能链还在跑 (★replay_patch_chain.sh 不含 v76rv_arms.sh 字样★)⇒ 再宽限 20 分钟★**
    GRACE=$(( $(date +%s) + 1200 ))
    while [ ! -f "$FINAL" ] && [ "$(date +%s)" -lt "$GRACE" ]; do sleep 60; done
    [ -f "$FINAL" ] || { echo "[watch] $(date '+%F %T') 臂与终板都不在 ⇒ 退出"; exit 4; }
  fi
  sleep 60
done

echo "[watch] $(date '+%F %T') 终板出现 ⇒ 出权威读数"
sleep 15   # ★等链把终板写完 (★保险★)★
{
  echo "# v76rv 权威读数 (★fresh DRC 同口径 ★生成于 $(date '+%F %T')★)"
  echo
  bash state/arm_fresh_readings.sh "$FINAL" 2>&1
} > "$OUT"

{
  echo "# v76rv 权威读数 (★fresh DRC 同口径 ★生成于 $(date '+%F %T')★)"
  echo
  echo '```'
  cat "$OUT"
  echo '```'
} > "$MD"

echo "[watch] $(date '+%F %T') 读数写好: $OUT · $MD"
exit 0
