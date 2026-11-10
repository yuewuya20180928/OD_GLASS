#!/usr/bin/env bash
# state/clrfix_iter.sh -- ★★★【★"边际净距修复"的【迭代版】: 修 → fresh DRC → 再修 ⇒ 直到干净或修不动★★】★★★ ★
#
# ★★★★★**★为什么必须迭代 (★2026-11-11 04:2x 实测踩到★)★★★★** ★★★
#   ★**现象**: 一条违规是 `Via [TS_BAT] ↔ Track [VDD_3V3_IO]` (净距 0.1937mm)
#     ⇒ ★**收窄 `VDD_3V3_IO` 之后, DRC 改报 `Via [TS_BAT] ↔ Track [JTAG_TDO]` (★同样 0.1937mm★)** ★★
#   ★★★**★根因**: ★**一个过孔周围常常有多条【等距】的铜** ⇒ ★**收窄一条, DRC 就把【下一条】报出来**
#     ⇒ ⇒ ★**"收窄 ⇒ 干净"是错的 ⇒ 必须【迭代】到 DRC 真的干净为止** ★★★
#   ★★**⇒ ★收窄的"单调安全"性质仍然成立 (★净距只增不减★) ⇒ ★**迭代必然收敛 (★最多修 N 次★)** ★★
#
# ★**用法**: bash state/clrfix_iter.sh <终板.kicad_pcb> <DRC.json> [--max N] [--tag 名]
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

BOARD="$1"; DRCJ="$2"
MAX=5; TAG=$(basename "$BOARD" .kicad_pcb)
shift 2 2>/dev/null || true
while [ $# -gt 0 ]; do
  case "$1" in
    --max) MAX="$2"; shift 2 ;;
    --tag) TAG="$2"; shift 2 ;;
    *) shift ;;
  esac
done
[ -f "$BOARD" ] || { echo "❌ 没有板: $BOARD"; exit 2; }
[ -f "$DRCJ" ]  || { echo "❌ 没有 DRC json: $DRCJ"; exit 2; }

WORK=/tmp/_clriter_$TAG.kicad_pcb
cp -f "$BOARD" "$WORK"
# ★★★**★工程文件必须【同名】拷过来 (★铁律: 板旁必须有 .kicad_pro⇒ 否则规则回落默认 0.20⇒ 0.15mm 走线全成假违规★)★★★ ★★
# ★★**踩过的坑**: ★旧写法用 `basename "$f"` 当目标名 ⇒ 拷成 `xxx.<原板名>.kicad_pro` ⇒ pcbnew 找不到 ⇒ 93 条假违规★★
[ -f "${BOARD%.kicad_pcb}.kicad_pro" ] && cp -f "${BOARD%.kicad_pcb}.kicad_pro" "${WORK%.kicad_pcb}.kicad_pro" \
  || echo "⚠️ 源板旁没有 .kicad_pro ⇒ ★【读数会失真】★ (请先补工程文件)"
[ -f "${BOARD%.kicad_pcb}.kicad_prl" ] && cp -f "${BOARD%.kicad_pcb}.kicad_prl" "${WORK%.kicad_pcb}.kicad_prl"
# ★第 1 轮的 DRC 种子 (★不然第 1 轮没有 DRC json 可读★)
cp -f "$DRCJ" "${WORK}.drc.json"

i=0
while [ "$i" -lt "$MAX" ]; do
  i=$((i+1))
  echo "── 第 $i 轮: 修 $WORK (DRC: ${WORK}.drc.json)"
  bash state/pcbnew_py.sh state/fix_clearance_width.py "$WORK" "${WORK}.drc.json" \
      --out "${WORK}.n" 2>&1 | grep -v "GetWidth called" | grep -E "clearance :|收窄了|修不了|·" | head -12
  mv -f "${WORK}.n" "$WORK"
  bash state/kicad.sh pcb drc --output "${WORK}.drc.json" --severity-error --severity-warning --format json "$WORK" >/dev/null 2>&1
  N=$(python3 -c "
import json,sys
d=json.load(open('${WORK}.drc.json'))
v=d.get('violations') or []
print(len(v))
" 2>/dev/null)
  # ★★★**★规则自检: ★`track_width` 违规 > 0 ⇒ ★工程文件/规则没跟过来⇒ ⇒ 本轮读数【作废】★★★
  TW=$(python3 -c "
import json
d=json.load(open('${WORK}.drc.json'))
print(sum(1 for x in (d.get('violations') or []) if x.get('type')=='track_width'))
" 2>/dev/null)
  if [ "${TW:-0}" != "0" ]; then
    echo "   ★★❌★ `track_width` 违规 = $TW ⇒ ★【规则没跟过来 (板旁缺 .kicad_pro?)】⇒ ⇒ 本轮读数作废, 收工★"
    cp -f "${WORK}.drc.json" "/tmp/_clriter_${TAG}.BADRULES.drc.json" 2>/dev/null
    break
  fi
  UNC=$(python3 -c "
import json
d=json.load(open('${WORK}.drc.json'))
print(len(d.get('unconnected_items') or []))
" 2>/dev/null)
  echo "   ⇒ fresh DRC: 违规 = ${N:-?} · unc = ${UNC:-?}"
  [ "${N:-1}" = "0" ] && { echo "✅ 干净了 (第 $i 轮)"; break; }
done

FIN=/tmp/_clrfix_${TAG}_final.kicad_pcb
cp -f "$WORK" "$FIN"
cp -f "${WORK}.drc.json" "${FIN}.drc.json"
for f in "${WORK%.kicad_pcb}.kicad_pro" "${WORK%.kicad_pcb}.kicad_prl"; do
  [ -f "$f" ] && cp -f "$f" "${FIN%.kicad_pcb}.${f##*.}" 2>/dev/null
done
[ -f "${WORK%.kicad_pcb}.kicad_pro" ] && cp -f "${WORK%.kicad_pcb}.kicad_pro" "${FIN%.kicad_pcb}.kicad_pro"
[ -f "${WORK%.kicad_pcb}.kicad_prl" ] && cp -f "${WORK%.kicad_pcb}.kicad_prl" "${FIN%.kicad_pcb}.kicad_prl"
echo "★最终板: $FIN (凭据 ${FIN}.clrfix.json)"
echo "★最终 DRC json: ${FIN}.drc.json"
echo "=== clrfix_iter 结束 (板=$BOARD) $(date '+%F %T') ==="
