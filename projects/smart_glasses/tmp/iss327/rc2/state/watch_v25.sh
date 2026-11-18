#!/usr/bin/env bash
# watch_v25.sh —— ★v25 收工看门狗 (2026-11-05 07:20)
# 用法: bash state/watch_v25.sh
# 1) 等 /tmp/gen_v25.log 出 EXIT=
# 2) ★**收工闸**: 板上段数 必须 == 落盘印 (.layout_landed.json) 里的 tracks
#    · 相等 ⇒ 板上就是刚落的那块 ⇒ 收
#    · 不等 ⇒ ★**板被中途存盘改过 / 崩在半路** ⇒ 从好板备份回滚
#    (同事建议: 别只判 "段数<1" —— 新码下崩了会留"几千段半成品", 那个判据不会触发)
# 3) 回滚后 / 收工后都跑一次 verify_and_release.sh ⇒ 出 8 道门禁 + 差分对审计的数字
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
LOG=/tmp/gen_v25.log
PCB=HW/PCB/demo_mainboard.kicad_pcb
STAMP=HW/PCB/.layout_landed.json
OUT=/tmp/watch_v25.log
: > "$OUT"

say() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$OUT"; }

say "等 v25 收工 (日志 $LOG)..."
for i in $(seq 1 480); do
  grep -q "EXIT=" "$LOG" 2>/dev/null && break
  sleep 30
done
say "v25 收工: $(grep -oE 'EXIT=[0-9]+' "$LOG" 2>/dev/null | tail -1)"

SEG_BOARD="$(grep -c '(segment' "$PCB" 2>/dev/null | head -1)"; SEG_BOARD="${SEG_BOARD:-0}"
SEG_STAMP="?"
if [ -f "$STAMP" ]; then
  SEG_STAMP="$(python3 -c "import json;print(int(json.load(open('$STAMP')).get('tracks',-1)))" 2>/dev/null || echo '?')"
fi
say "板上段数=$SEG_BOARD · 落盘印 tracks=$SEG_STAMP"

ROLLBACK=0
if [ "$SEG_STAMP" = "?" ] || [ "$SEG_BOARD" != "$SEG_STAMP" ]; then
  ROLLBACK=1
fi
if [ "$SEG_BOARD" -lt 1 ]; then ROLLBACK=1; fi

if [ "$ROLLBACK" = "1" ]; then
  for BAK in /tmp/board_last_good.kicad_pcb state/.lastgood/board_last_good_kicad_pcb \
             state/.lastgood/board_last_good_kicad_pcb ~/board_backups/board_last_good.kicad_pcb; do
    if [ -f "$BAK" ] && [ "$(grep -c '(segment' "$BAK" 2>/dev/null | head -1)" -gt 100 ]; then
      cp -p "$BAK" "$PCB"
      say "★**收工闸拦下** (板上 $SEG_BOARD 段 vs 落盘印 $SEG_STAMP) ⇒ 已从备份回滚: $BAK ⇒ 恢复 $(grep -c '(segment' "$PCB") 段"
      break
    fi
  done
else
  say "✅ 收工闸通过: 板上段数与落盘印一致 ($SEG_BOARD)"
fi

say "跑自验 (verify_and_release.sh) 出门禁数字..."
timeout 3600 bash state/verify_and_release.sh > /tmp/verify_v25.log 2>&1
RC=$?
say "verify rc=$RC"
grep -E "unconnected items|DRC violations|check_pcb_nets rc|check_pcb_drc|chain_gate rc|stage_gate rc|单边零铜|Δ>0.13|布不动的脚" /tmp/verify_v25.log | head -20 | tee -a "$OUT"
say "完成 (详见 /tmp/verify_v25.log)"
