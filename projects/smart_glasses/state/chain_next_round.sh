#!/usr/bin/env bash
# chain_next_round.sh —— ★等当前这一轮落盘后**立刻**起下一轮 (不等 5 分钟 cron 的空档)
# 用法: bash state/chain_next_round.sh <本轮日志> <下一轮日志> <A*预算倍数>
#
# ★★2026-11-05 04:30 加的 **A 闸 (自验不掐掉)**:
#   问题: 上一轮一落盘就起下一轮 ⇒ auto_release 的 detect_live_log() 扫 /proc 只能看到**下一轮**的日志
#         ⇒ 上一轮那块板**永远不会被 DRC/unconnected/门禁量一遍** ⇒ 真数一个都出不来
#   修法: 三道闸全过之后、起下一轮**之前**, 先跑一次 state/verify_and_release.sh
#         (此时官方板 100% 是刚落盘的那一轮 ⇒ 量到的数就是这一轮的) ⇒ 再起下一轮
#   ⇒ ★**先量后跑** ⇒ 上一轮的真数先落袋, 下一轮再接着跑
#
# 三道闸 (全过才起下一轮):
#   ① 官方板有走线 (>0 segment)      ⇒ 本轮真的落盘了
#   ② 本轮日志有 "已原子替换正式板"   ⇒ 落盘标记 (不是"被杀前的半成品")
#   ③ 本轮日志有 "判定: 全过"         ⇒ ★**网表 parity 全过** ⇒ 若 parity 还红 ⇒
#      起下一轮等于拿同一份有 bug 的代码再烧 40 分钟 ⇒ **不起, 留给人修**
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
CUR_LOG="${1:-/tmp/gen_v20.log}"
NEXT_LOG="${2:-/tmp/gen_v21.log}"
MULT="${3:-6}"
PIDFILE=state/.chain_round.pid
BOARD=HW/PCB/demo_mainboard.kicad_pcb
TIMEOUT=$(( 900 * MULT )); [ "$TIMEOUT" -lt 4000 ] && TIMEOUT=4000

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE" 2>/dev/null)" 2>/dev/null; then
  echo "已有链条在跑 (PID $(cat "$PIDFILE")) ⇒ 退出"
  exit 0
fi
echo $$ > "$PIDFILE"

echo "[chain] 等待 $CUR_LOG 出现 EXIT= … (下一轮预算×$MULT, timeout ${TIMEOUT}s)"
while true; do
  if grep -q "EXIT=" "$CUR_LOG" 2>/dev/null; then break; fi
  sleep 15
done
RC="$(grep -oE 'EXIT=[0-9]+' "$CUR_LOG" | tail -1)"
SEG="$(grep -c '(segment' "$BOARD" 2>/dev/null | head -1)"; SEG="${SEG:-0}"
LAND="$(grep -c '已原子替换正式板' "$CUR_LOG" 2>/dev/null | head -1)"; LAND="${LAND:-0}"
PAR="$(grep -c '判定: 全过' "$CUR_LOG" 2>/dev/null | head -1)"; PAR="${PAR:-0}"
echo "[chain] $CUR_LOG 结束 ($RC) · 官方板 $SEG 段走线 · 落盘标记 $LAND · parity全过 $PAR"

if [ "${SEG:-0}" -lt 1 ] || [ "${LAND:-0}" -lt 1 ]; then
  echo "[chain] ★本轮没真落盘 (走线 $SEG / 落盘标记 $LAND) ⇒ **不起下一轮** (留给人查 bug)"
  rm -f "$PIDFILE"
  exit 0
fi
if [ "${PAR:-0}" -lt 1 ]; then
  echo "[chain] ★parity 没过 (日志里没有 '判定: 全过') ⇒ **不起下一轮**"
  echo "[chain]   ⇒ 同一份代码再烧一轮只会再红一次 ⇒ 留给人先修 parity"
  grep -E "★缺失|★多余|判定" "$CUR_LOG" | tail -4
  rm -f "$PIDFILE"
  exit 0
fi

# ★★A 闸: 先把刚落盘这一轮量一遍 (官方板此刻 100% 是这一轮的) ⇒ 真数先落袋
echo "[chain] ★先自验刚落盘的板 (verify_and_release.sh) ⇒ 把这一轮的真数量出来"
bash state/verify_and_release.sh > /tmp/chain_verify.log 2>&1
VRC=$?
echo "[chain] verify rc=$VRC · 关键行:"
grep -E "DRC violations|unconnected items|C3 DRC|C4 unconnected|check_pcb_nets rc|check_pcb_drc|chain_gate rc|stage_gate rc|★缺失|★多余|判定" /tmp/chain_verify.log | head -24
{
  echo ""
  echo "===== [chain] $(date '+%Y-%m-%d %H:%M:%S') 自验本轮落盘板 (verify rc=$VRC) ====="
  grep -E "DRC violations|unconnected items|check_pcb_nets rc|check_pcb_drc|chain_gate rc|stage_gate rc|★缺失|★多余" /tmp/chain_verify.log | head -24
} >> "$CUR_LOG"

echo "[chain] 本轮已落盘且已自验 ⇒ 起下一轮: 预算×$MULT ⇒ 日志 $NEXT_LOG"
setsid nohup bash -c "cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses && PCB_LAYERS=6 PCB_ABUDGET_MULT=$MULT timeout $TIMEOUT bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py > $NEXT_LOG 2>&1; echo \"EXIT=\$?\" >> $NEXT_LOG" > /dev/null 2>&1 &
sleep 4
echo "[chain] 下一轮 PID: $(pgrep -f 'gen_pcb_netlist_board.py' | tr '\n' ' ')"
rm -f "$PIDFILE"
exit 0
