#!/usr/bin/env bash
# measure_arm.sh —— ★**量一个实验臂的真实成绩** (2026-11-05 10:30)
# 用法: bash state/measure_arm.sh <前缀> <臂名>   例: bash state/measure_arm.sh v27 E
# 输出: DRC / unconnected / 段数 / 过孔 / 布不动的脚 / N未通对数 (全部机器读出)
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
PREFIX="${1:?用法: measure_arm.sh <前缀> <臂名>}"
ARM="${2:?用法: measure_arm.sh <前缀> <臂名>}"
PCB="/tmp/${PREFIX}_${ARM}.kicad_pcb"
LOG="/tmp/${PREFIX}_${ARM}.log"
[ -f "$PCB" ] || { echo "❌ 没有 $PCB (臂还没落盘?)"; exit 1; }
echo "══════ 量 ${PREFIX}_${ARM} ══════"
echo "  板: $(ls -la --time-style=+%H:%M:%S "$PCB" | awk '{print $6, $5"字节"}')"
echo "  段数 $(grep -c '(segment' "$PCB") / 过孔 $(grep -c '(via' "$PCB")"
grep -E "\[SUM \]|布不动的脚|EXIT=" "$LOG" | tail -3 | sed 's/^/  /'
bash state/kicad.sh pcb drc --output "/tmp/_m_${PREFIX}_${ARM}.json" --severity-error --severity-warning --format json "$PCB" >/dev/null 2>&1
python3 - "/tmp/_m_${PREFIX}_${ARM}.json" <<'PY'
import json, sys, collections, re
try:
    d = json.load(open(sys.argv[1]))
except Exception as e:
    print("  ⚠️ DRC 取证失败:", e); raise SystemExit
v = d.get("violations") or []
u = d.get("unconnected_items") or []
print("  ★ DRC violations = %d   unconnected items = %d" % (len(v), len(u)))
print("  DRC 类型:", collections.Counter([x.get("type") for x in v]).most_common(6))
nets = collections.Counter()
for x in u:
    for it in (x.get("items") or []):
        for m in re.findall(r"\[([^\]]+)\]", str(it.get("description"))):
            nets[m] += 1
print("  未连接 top10:", nets.most_common(10))
PY
nb=$(grep '\[PAIR\]' "$LOG" 2>/dev/null | grep -c 'N 未通')
tot=$(grep -c '\[PAIR\]' "$LOG" 2>/dev/null)
echo "  差分对: 共 $tot 对, N 侧未通 $nb 对"
