#!/usr/bin/env bash
# arm_fresh_readings.sh -- ★★**读一条臂的【权威读数】(★永远 fresh DRC)★★**
#
# ★★★★★★**★为什么必须有这个脚本 (★2026-11-10 01:4x 实测踩到的坑)★★** ★★★★★★
#   ★**坑**: `/tmp/chain_<TAG>/final_chain.kicad_pcb.drc.json` ★**不是终板的 DRC** ★★
#     ⇒ ★**它是【上一步 patch 的输入 DRC】** (★`step_nostub` 把输入板的 DRC 存成了输出板的名字)
#     ⇒ ★**实测**: v76ru 终板 fresh DRC = **unc 35 / DRC 3**,
#        而那个同名文件里是 **unc 43 / DRC 3** ⇒ ★**据此报的[打碎 9 个]是错的, 真值是【打碎 5 个】★★**
#   ★⇒ ★**⇒ 读数必须 fresh DRC 终板自己** ★★ ★★★
#
# ★**用法**:
#   bash state/arm_fresh_readings.sh <终板.kicad_pcb> [--baseline <基线板>]
#   ⇒ ★**只读板 ⇒ 不改板 ⇒ 不污染任何臂** ★★
#   ⇒ ★**会把 fresh DRC 写回 <板>.drc.json (★并把原来那个错位的存成 .drc.json.stale_input★)** ★★
#
# ★**判据纪律 (★来自 MEMORY: [看 Δ 汇总前, 必须先看单边零铜对数] 同一族)★★**:
#   ★**一切读数必须来自 fresh DRC ⇒ 任何"数出来 nicer"的漂亮结论都要先过这一关** ★★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

BOARD="${1:?用法: arm_fresh_readings.sh <终板.kicad_pcb> [--baseline <基线板>]}"
BASE=""
if [ "${2:-}" = "--baseline" ] && [ -n "${3:-}" ]; then BASE="$3"; fi
BASE="${BASE:-state/.lastgood/baseline_v76_chain.kicad_pcb}"

[ -f "$BOARD" ] || { echo "❌ 没有板: $BOARD"; exit 1; }

# ---- ① fresh DRC 终板 (★权威) ----
FRESH="${BOARD}.drc.json.fresh"
bash state/kicad.sh pcb drc --output "$FRESH" --severity-error --severity-warning \
     --format json "$BOARD" >/dev/null 2>&1
[ -f "$FRESH" ] || { echo "❌ fresh DRC 没跑出来"; exit 2; }

# ---- ② 错位文件体检 (★同名 json 是不是终板的? ★) ----
OLD="${BOARD%.kicad_pcb}.kicad_pcb.drc.json"
[ -f "$OLD" ] || OLD="${BOARD}.drc.json"
if [ -f "$OLD" ] && [ "$OLD" != "$FRESH" ]; then
  python3 - "$OLD" "$FRESH" <<'PY'
import json, sys, re
def stat(p):
    d = json.load(open(p, encoding="utf-8"))
    u = d.get("unconnected_items") or []
    nets = set()
    for it in u:
        nets |= set(re.findall(r"\[([A-Za-z0-9_]+)\]", json.dumps(it, ensure_ascii=False)))
    return len(u), len(nets), len(d.get("violations") or [])
o = stat(sys.argv[1]); f = stat(sys.argv[2])
print("  ★体检: 旧同名 json = unc %d 条 / %d 网 / DRC %d   |   fresh = unc %d 条 / %d 网 / DRC %d"
      % (o[0], o[1], o[2], f[0], f[1], f[2]))
if o[:2] != f[:2]:
    print("  ⚠️ ★★【旧同名 json 与终板不一致 ⇒ 它是【上一步的输入 DRC】⇒ 别拿它读数】★★")
PY
  # 把错位的旧文件挪成 .stale_input (留证), 再让同名文件变成真的
  if [ "$OLD" != "$FRESH" ] && [ "$OLD" != "${BOARD}.drc.json" ]; then
    cp -f "$OLD" "${OLD}.stale_input"
  fi
  cp -f "$FRESH" "$OLD"
  echo "  ✓ 已把 fresh DRC 写回 $OLD (旧的存成 *.stale_input)"
fi

echo "── 权威读数 (fresh DRC) ──"
python3 - "$FRESH" "$BOARD" <<'PY'
import json, sys, re
d = json.load(open(sys.argv[1], encoding="utf-8"))
u = d.get("unconnected_items") or []
nets = set()
for it in u:
    nets |= set(re.findall(r"\[([A-Za-z0-9_]+)\]", json.dumps(it, ensure_ascii=False)))
print("  板    : %s" % sys.argv[2])
print("  段数  : %d" % sum(1 for l in open(sys.argv[2], encoding="utf-8", errors="ignore") if "(segment" in l))
print("  DRC违规: %d" % len(d.get("violations") or []))
print("  unc   : %d 条 / %d 个网名" % (len(u), len(nets)))
for x in (d.get("violations") or [])[:8]:
    print("     - [%s] %s" % (x.get("type"), str(x.get("description"))[:110]))
PY

# ---- ③ 同口径对比基线 (★可选) ----
if [ -f "$BASE" ]; then
  echo "── vs 同链基线 (★fresh DRC 双边) ──"
  bash state/compare_arm_baseline.sh "$BOARD" --baseline "$BASE" 2>&1 | sed -n '1,12p;/名单差集/,/闸 rc/p'
fi
exit 0
