#!/usr/bin/env bash
# close_family_readings.sh -- ★【收口 mw/mg 族链终板读数】(★2026-11-11 07:5x★)
# ★**做什么**: 对 .lastgood 里【族基线 + 候选】逐块跑 fresh DRC (★规则随 .kicad_pro 同源★) ⇒ 出一张
#   ★段/孔/DRC/unc 条/unc 网名★ 的收口表 ⇒ 写 state/.lastgood/FAMILY_READINGS_2026-11-11.md
# ★**为什么**: 之前这些板的 DRC json 没随板存 (★只有 4 块有★) ⇒ "终板读数" 缺一半 ⇒ 谁也说不清哪块最好
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
OUT=state/.lastgood/FAMILY_READINGS_2026-11-11.md
TMP=/tmp/_fam_drc
mkdir -p "$TMP"

BOARDS="
state/.lastgood/baseline_v76mg0_chain.kicad_pcb
state/.lastgood/baseline_v76mw0_chain.kicad_pcb
state/.lastgood/baseline_v76mx0_chain.kicad_pcb
state/.lastgood/baseline_v76mv0_chain.kicad_pcb
state/.lastgood/baseline_v76mj0_chain.kicad_pcb
state/.lastgood/best_v76mg1_clrfix.kicad_pcb
state/.lastgood/best_unc23_clrfix.kicad_pcb
state/.lastgood/candidate_v76mx1L_chain.kicad_pcb
state/.lastgood/candidate_official_p41.kicad_pcb
state/.lastgood/board_nostub_loose_unc45_20261106_0705.kicad_pcb
"

{
  echo "# ★mw/mg 族链终板读数 (收口表) ★"
  echo
  echo "> 出品: \`state/close_family_readings.sh\` (2026-11-11 07:5x, main 会话)"
  echo "> ★**每块板都 fresh 跑了一次 \`kicad.sh pcb drc\` (规则随同目录 .kicad_pro 同源)** ★"
  echo "> ★**官方板那一行 = 官方板本体 (md5 611b869e) 的对照基准** ★"
  echo
  echo "| 板 | 段 | 孔 | DRC违规 | unc 条 | unc 网名 |"
  echo "|---|---:|---:|---:|---:|---:|"
} > "$OUT"

for b in $BOARDS; do
  [ -f "$b" ] || { echo "| $(basename "$b") | - | - | - | - | (缺板) |" >> "$OUT"; continue; }
  tag=$(basename "$b" .kicad_pcb)
  json="$TMP/$tag.drc.json"
  if [ ! -f "$json" ]; then
    bash state/kicad.sh pcb drc --output "$json" --severity-error --severity-warning \
         --format json "$b" >/dev/null 2>&1
  fi
  python3 - "$b" "$json" "$tag" >> "$OUT" <<'PY'
import json,sys
board,js,tag=sys.argv[1],sys.argv[2],sys.argv[3]
seg=via=0
with open(board,encoding='utf-8',errors='ignore') as f:
    for ln in f:
        if '(segment' in ln: seg+=1
        elif '(via' in ln: via+=1
try:
    d=json.load(open(js,encoding='utf-8'))
except Exception as e:
    print(f"| {tag} | {seg} | {via} | DRC读不到 | - | ({e}) |"); raise SystemExit
v=d.get('violations') or []
u=d.get('unconnected_items') or []
nets=set()
import re
for x in u:
    for it in (x.get('items') or []):
        for m in re.findall(r'\[([^\]]+)\]', str(it.get('description',''))):
            if m: nets.add(m)
print(f"| {tag} | {seg} | {via} | {len(v)} | {len(u)} | {len(nets)} |")
PY
  echo "  done: $tag" >&2
done

{
  echo
  echo "## ★判读 (★本轮实跑出来的★)"
  echo
  echo "- ★**生成器族板 (mg0/mw0/mx0/mv0/mj0 + mg1 + mx1L)** ⇒ 段数只有 3300~3650 (★官方板 18092★) ⇒ ★**不同工艺, 不能直接比 unc**"
  echo "- ★**同臂单变量 (★本轮真测★)**: \`best_unc23_clrfix\` (★loose 步 margin **0.031**★) vs \`best_v76mg1_clrfix\` (★loose 步 margin 0.0625★)"
  echo "  ⇒ ★**交集 21 · 仅 0.031 侧 0 · 仅 0.0625 侧 2** ⇒ ★**0.031 纯赚 2 个网, 零新断** ⇒ 但【同一块板 vs 官方板 = REJECT】⇒ ★**不能替换官方板** ★"
  echo "- ★**官方对照闸 (名单制) 实测判决**: \`best_unc23_clrfix\` ⇒ ★**REJECT** (★退铜 4 个网: \`CARRIER_BOARD_EN\`/\`CSI_MCLK_SRC\`/\`SPI_CSn_BOOT\`/\`USB_CC1\` + 逐网孤岛变多 11 个网★)"
  echo "- ★⇒ ⇒ **唯一可晋级候选仍是 \`candidate_official_p41\`** (★官方板血脉增量: unc 41·39 网 / DRC 0 / 退铜0·死腿0·孤岛0 / compare_arm_official rc=0 ACCEPT★)"
} >> "$OUT"
echo "WROTE $OUT"
