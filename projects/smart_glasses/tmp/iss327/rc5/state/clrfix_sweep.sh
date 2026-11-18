#!/usr/bin/env bash
# state/clrfix_sweep.sh -- ★把"边际净距修复"批量套到若干臂的终板上, 给出【每臂 DRC=0 等价读数】★
# ★**只读臂产物 ⇒ 不改任何臂 ⇒ 不污染臂历史** ★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

for tag in "$@"; do
  DIR=/tmp/chain_v76$tag
  BOARD=$DIR/final_chain.kicad_pcb
  DRCJ=$DIR/final_board.drc.json
  OUT=/tmp/_clr_v76$tag.kicad_pcb
  if [ ! -f "$BOARD" ] || [ ! -f "$DRCJ" ]; then echo "★跳过 v76$tag (没有终板/DRC)"; continue; fi
  if [ -e "$OUT" ]; then echo "★跳过 v76$tag (已有产物 $OUT)"; continue; fi
  echo "═══ v76$tag ═══"
  cp -f "${BOARD%.kicad_pcb}.kicad_pro" "${OUT%.kicad_pcb}.kicad_pro" 2>/dev/null
  cp -f "${BOARD%.kicad_pcb}.kicad_prl" "${OUT%.kicad_pcb}.kicad_prl" 2>/dev/null
  bash state/pcbnew_py.sh state/fix_clearance_width.py "$BOARD" "$DRCJ" --out "$OUT" 2>&1 \
    | grep -v "GetWidth called" | grep -E "净距修复|收窄了|修不了|·|凭据|已写出"
  bash state/kicad.sh pcb drc --output "${OUT}.drc.json" --severity-error --severity-warning --format json "$OUT" >/dev/null 2>&1
  python3 - "${OUT}.drc.json" "$tag" <<'PY'
import json, sys, collections
d = json.load(open(sys.argv[1], encoding="utf-8"))
v = d.get("violations") or []
print("  ⇒ v76%s: fresh DRC 违规=%d · unc=%d 条 · %s"
      % (sys.argv[2], len(v), len(d.get("unconnected_items") or []),
         dict(collections.Counter(x.get("type") for x in v).most_common(5))))
for x in v[:5]:
    print("     -", x.get("type"), "|", x.get("description", "")[:100])
PY
done
echo "=== clrfix_sweep 结束 $(date '+%F %T') ==="
