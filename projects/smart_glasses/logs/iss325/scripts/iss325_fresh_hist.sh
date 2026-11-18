#!/usr/bin/env bash
# iss325_fresh_hist.sh -- ★★把 ISS-322 §3-6 那张表的 unc 列【全部 fresh 重测一遍】★★
# ★为什么: 那张表的 unc 列是【硬编码在脚本里的历史记录】(★probe_lane_order_vs_unc.py 的 BOARDS 列表★)
#   ⇒ main 已实测发现其中一块对不上 ⇒ ⇒ 本单自己 fresh 测每一块, 不抄那张表
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1
EV=logs/iss325
mkdir -p "$EV/hist"
BOARDS="state/.lastgood/baseline_v76me0_chain.kicad_pcb
state/.lastgood/baseline_v76mg0_chain.kicad_pcb
state/.lastgood/baseline_v76mj0_chain.kicad_pcb
state/.lastgood/baseline_v76mv0_chain.kicad_pcb
state/.lastgood/baseline_v76mw0_chain.kicad_pcb
state/.lastgood/baseline_v76mx0_chain.kicad_pcb
state/.lastgood/best_unc23_clrfix.kicad_pcb
HW/PCB/demo_mainboard.kicad_pcb"
OUT="$EV/09b_hist_boards_fresh_drc.txt"
: > "$OUT"
while read -r bd; do
  [ -f "$bd" ] || { echo "$bd  MISSING" >> "$OUT"; continue; }
  base=$(basename "$bd" .kicad_pcb)
  json="$EV/hist/${base}.drc.json"
  bash state/kicad.sh pcb drc --output "$json" --severity-error --severity-warning --format json "$bd" >/dev/null 2>&1
  python3 - "$json" "$bd" "$base" >> "$OUT" <<'PY'
import json, sys, hashlib, re, collections
p, bd, base = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    d = json.load(open(p, encoding="utf-8"))
except Exception as e:
    print("%-42s DRC_READ_FAIL %s" % (base, e)); raise SystemExit(0)
v = d.get("violations") or []
u = d.get("unconnected_items") or []
nets = set()
for it in u:
    nets.update(re.findall(r"\[([A-Za-z0-9_]+)\]", json.dumps(it, ensure_ascii=False)))
md5 = hashlib.md5(open(bd, "rb").read()).hexdigest()
print("%-42s md5=%s  viol=%d  unc=%d  unc网名=%d" % (base, md5, len(v), len(u), len(nets)))
PY
done <<< "$BOARDS"
echo "=== hist fresh DRC 完成 $(date '+%F %T') ===" >> "$OUT"
cat "$OUT"
