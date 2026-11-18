#!/usr/bin/env bash
# cmp_all.sh —— ★**把"所有已落盘的臂"排一张总表** (2026-11-05 11:05)
# 每臂量: 段数 / 过孔 / DRC / unconnected / N未通对 / 布不动的脚
# ⇒ ★**口径统一**: 都用 KiCad DRC 的实测 (不读各臂自己的日志数字)
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

printf "%-9s %-9s %-8s %-6s %-13s %-9s %-9s\n" 臂 段数 过孔 DRC unconnected N未通对 布不动的脚
for spec in v26:A,B,C,D v27:E,F,G v28:H,I v29:J; do
  PREFIX="${spec%%:*}"; ARMS="${spec#*:}"
  IFS=',' read -ra LIST <<< "$ARMS"
  for ARM in "${LIST[@]}"; do
    PCB="/tmp/${PREFIX}_${ARM}.kicad_pcb"
    LOG="/tmp/${PREFIX}_${ARM}.log"
    [ -f "$PCB" ] || continue
    SEG=$(grep -c '(segment' "$PCB"); VIA=$(grep -c '(via' "$PCB")
    bash state/kicad.sh pcb drc --output "/tmp/_ca_${PREFIX}_${ARM}.json" --severity-error --severity-warning --format json "$PCB" >/dev/null 2>&1
    read -r DRC UNC <<< "$(python3 - "/tmp/_ca_${PREFIX}_${ARM}.json" <<'PY'
import json,sys
try:
    d=json.load(open(sys.argv[1]))
    print(len(d.get("violations") or []), len(d.get("unconnected_items") or []))
except Exception:
    print("- -")
PY
)"
    NB=$(grep '\[PAIR\]' "$LOG" 2>/dev/null | grep -c 'N 未通')
    [ "$NB" = "0" ] && NB="-"
    FP=$(grep -oE '布不动的脚 [0-9]+' "$LOG" 2>/dev/null | tail -1 | grep -oE '[0-9]+')
    [ -z "$FP" ] && FP="-"
    printf "%-9s %-9s %-8s %-6s %-13s %-9s %-9s\n" "${PREFIX}_${ARM}" "$SEG" "$VIA" "$DRC" "$UNC" "$NB" "$FP"
  done
done
