#!/usr/bin/env bash
# ★arm_ledger.sh —— 【臂总账汇总】★ 把所有臂的同口径读数排成一张表
#
# ★★**为什么要有 (★2026-11-10 04:5x)★★
#   ★**臂一多, 读数散在各处, 口径还容易混 (★"unconnected 条目数" vs "网名签名数"★)**
#   ★**⇒ 一张表, 同一口径, 全部 fresh DRC ★★
#
# 用法:
#   bash state/arm_ledger.sh [基线板]
#   ⇒ 默认基线 = state/.lastgood/baseline_v76_chain.kicad_pcb
#   ⇒ 扫 /tmp/chain_v76*/final_chain.kicad_pcb
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
BASE="${1:-state/.lastgood/baseline_v76_chain.kicad_pcb}"

printf '%-14s %7s %7s %6s %6s %6s %6s %6s %6s %6s\n' \
  "臂" "段数" "DRC" "unc条" "unc网" "零铜" "差单" "退铜" "孤岛" "闸"
printf '%.0s─' {1..84}; echo

# ★**基线自己先算一遍**
BASE_ROW=$(python3 - "$BASE" <<'PY'
import json, os, sys
sys.path.insert(0, "state")
p = sys.argv[1]
if not os.path.exists(p):
    print("  (基线缺失)"); raise SystemExit
d = json.load(open(p, encoding="utf-8", errors="ignore")) if p.endswith(".json") else None
segs = sum(1 for l in open(p, encoding="utf-8", errors="ignore") if l.lstrip().startswith("(segment"))
print("BASE\t%d\t-\t-\t-\t-\t-\t-\t-\t-" % segs)
PY
)
echo "$BASE_ROW" | awk -F'\t' '{printf "%-14s %7s %7s %6s %6s %6s %6s %6s %6s %6s\n", "★基线", $2,$3,$4,$5,$6,$7,$8,$9,$10}'

for d in $(ls -d /tmp/chain_v76* 2>/dev/null | sort); do
  B="$d/final_chain.kicad_pcb"
  [ -f "$B" ] || continue
  TAG=$(basename "$d" | sed 's/^chain_//')
  SEG=$(grep -ac '(segment' "$B")
  OUT=$(timeout 900 bash state/arm_fresh_readings.sh "$B" --baseline "$BASE" 2>/dev/null)
  DRC=$(echo "$OUT" | grep -oE "DRC违规: [0-9]+" | head -1 | grep -oE "[0-9]+")
  UNC=$(echo "$OUT" | grep -oE "unc   : [0-9]+ 条 / [0-9]+ 个网名" | grep -oE "[0-9]+" | head -1)
  UNCN=$(echo "$OUT" | grep -oE "unc   : [0-9]+ 条 / [0-9]+ 个网名" | grep -oE "[0-9]+" | tail -1)
  ZC=$(echo "$OUT" | grep -E "零铜" | grep -oE "[0-9]+" | head -1)
  DP=$(echo "$OUT" | grep -E "差分单边" | grep -oE "[0-9]+" | head -1)
  RC=$(echo "$OUT" | grep -A1 "退铜名单" | grep -oE "[0-9]+" | head -1)
  ISL=$(echo "$OUT" | grep -E "逐网孤岛变多" | grep -oE "[0-9]+" | head -1)
  GATE=$(echo "$OUT" | grep -oE "闸 rc=[0-9]+" | tail -1 | grep -oE "[0-9]+$")
  printf '%-14s %7s %7s %6s %6s %6s %6s %6s %6s %6s\n' \
    "$TAG" "$SEG" "${DRC:-?}" "${UNC:-?}" "${UNCN:-?}" "${ZC:-?}" "${DP:-?}" "${RC:-?}" "${ISL:-?}" "${GATE:-?}"
done
echo
echo "★口径: unc条 = unconnected_items 条目数 · unc网 = 网名签名数 · 闸 = 名单制闸 rc (0=ACCEPT)"
echo "★全部读数来自 fresh DRC (★不用 chain 目录里的同名 json★)"
