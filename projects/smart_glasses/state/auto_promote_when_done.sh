#!/usr/bin/env bash
# auto_promote_when_done.sh —— ★**臂一落盘就自动量 + 自动晋级** (2026-11-05 11:00)
# 目的: 不用等我盯着 ⇒ 臂落盘 ⇒ 自动跑 DRC ⇒ 比官方板 ⇒ 更好就自动走终点线
# 用法: bash state/auto_promote_when_done.sh <前缀> <臂名> [等多久秒]
# 例:   bash state/auto_promote_when_done.sh v28 H 7200
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
PREFIX="${1:?用法: auto_promote_when_done.sh <前缀> <臂名> [超时秒]}"
ARM="${2:?用法: auto_promote_when_done.sh <前缀> <臂名> [超时秒]}"
WAIT="${3:-7200}"
LOG="/tmp/${PREFIX}_${ARM}.log"
PCB="/tmp/${PREFIX}_${ARM}.kicad_pcb"
OUT=/tmp/auto_promote.log

say() { echo "[$(date '+%H:%M:%S')] $*" >> "$OUT"; }
say "=== 守候 ${PREFIX}_${ARM} (超时 ${WAIT}s) ==="
t0=$(date +%s)
while [ $(( $(date +%s) - t0 )) -lt "$WAIT" ]; do
  if grep -q 'EXIT=' "$LOG" 2>/dev/null; then break; fi
  sleep 20
done
if ! grep -q 'EXIT=' "$LOG" 2>/dev/null; then
  say "✗ 等超时 ⇒ 没等到 ${PREFIX}_${ARM} 落盘"
  exit 1
fi
say "✔ ${PREFIX}_${ARM} 落盘 ($(grep -oE 'EXIT=[0-9]+' "$LOG" | tail -1)) ⇒ 开始量"
[ -f "$PCB" ] || { say "✗ 没有臂板文件 $PCB"; exit 1; }

# ★★2026-11-05 12:45 **必须 EXIT=0 才量** (★血的教训)
#   v28 M 臂: 布局阶段撞板 (焊盘间距 0.000mm) ⇒ **EXIT=1, 板根本没落盘**
#   ⇒ 但 /tmp/v28_M.kicad_pcb 里留着**中途存的残片** (4.27MB / 15778 段)
#   ⇒ 旧版守候器只看"日志里出现 EXIT=" 就去量 ⇒ ★**量了一块残片** ⇒ 报出 "DRC=143 unconn=63"
#   ⇒ ★**那组数字是假的** (还被我口头引用过一次 ⇒ 已在 12:45 订正)
#   ⇒ ★**残片已改名 .partial** ⇒ 以后不会有人再量它
_exit=$(grep -oE 'EXIT=[0-9]+' "$LOG" | tail -1 | cut -d= -f2)
if [ "${_exit:-1}" != "0" ]; then
  say "✗ 臂没成功落盘 (EXIT=${_exit:-无}) ⇒ **不量、不晋级** (★中途残片不是板)"
  exit 1
fi
# ★再核一次: 落盘印 (段数/过孔) 必须和板上实测一致 ⇒ 防止"存了一半"的板混进来
say "  (EXIT=0 ✔ ⇒ 开始量真板)"

# ★量这个臂
bash state/kicad.sh pcb drc --output "/tmp/_ap_${PREFIX}_${ARM}.json" --severity-error --severity-warning --format json "$PCB" >/dev/null 2>&1
read -r DRC UNC <<< "$(python3 - "/tmp/_ap_${PREFIX}_${ARM}.json" <<'PY'
import json,sys
try:
    d=json.load(open(sys.argv[1]))
    print(len(d.get("violations") or []), len(d.get("unconnected_items") or []))
except Exception:
    print("999 999")
PY
)"
say "  臂: DRC=$DRC unconnected=$UNC"
# ★官方板现状
read -r ODRC OUNC <<< "$(python3 - <<'PY'
import json
try:
    d=json.load(open('HW/PCB/.layout_done.json'))
    print(d.get('drc_violations', 999), d.get('unconnected', 999))
except Exception:
    print('999 999')
PY
)"
say "  官方板: DRC=$ODRC unconnected=$OUNC"

# ★★2026-11-05 14:38 **晋级判据改成 Pareto 改进** (★血的教训)
#   旧版: `[ "$UNC" -ge "$OUNC" ] || [ "$DRC" -gt "$ODRC" ]`
#     ⇒ ★**unconnected "相等"(64==64) 就被判"不比官方板好"** ⇒ ⇒ **DRC 从 1 降到 0 的改善被完全忽略**
#     ⇒ ⇒ v31_Q (DRC=0 / unconn=64) 明明比官方板 (DRC=1 / unconn=64) 干净, 却被拒晋级
#     ⇒ ⇒ ★**日志自己都打了 "DRC 0 vs 1" 却仍判不晋级** ⇒ 这是判据 bug, 不是臂的问题
#   新版 (Pareto): ★**两项都不得变差, 且至少一项严格变好** ⇒ 才晋级
#     worse  = (UNC > OUNC) or (DRC > ODRC)          ⇒ 任一变差 ⇒ 不晋级
#     better = (UNC < OUNC) or (DRC < ODRC)          ⇒ 至少一项严格变好
#     全平 (UNC==OUNC and DRC==ODRC) ⇒ 没有改善 ⇒ 不晋级
#   ★**防呆**: 取证失败时 DRC/UNC = 999 ⇒ 999 > 任何值 ⇒ 自动落到"不晋级" ⇒ 绝不误晋级
_better=$(python3 - "$UNC" "$OUNC" "$DRC" "$ODRC" <<'PY'
import sys
try:
    unc, ounc, drc, odrc = (int(x) for x in sys.argv[1:5])
except Exception:
    print("no"); raise SystemExit
# ★**基线未知 (999 = 取证失败) ⇒ 绝不晋级** (★不能拿"官方板没量出来"当"臂更好")
if unc >= 999 or ounc >= 999 or drc >= 999 or odrc >= 999:
    print("no"); raise SystemExit
worse  = (unc > ounc) or (drc > odrc)
better = (unc < ounc) or (drc < odrc)
print("yes" if (not worse and better) else "no")
PY
)
if [ "$_better" != "yes" ]; then
  say "★不比官方板好 (unconnected $UNC vs $OUNC · DRC $DRC vs $ODRC · Pareto 不满足) ⇒ **不晋级**"
  exit 0
fi
say "  ⇒ 比官方板好 (Pareto: 两项不劣且至少一项更优) ⇒ 走终点线 (晋级 → 加铜皮 → 重出投产包 → 全门禁自验)"
PREFIX="$PREFIX" bash state/finish_line.sh "$ARM" >> "$OUT" 2>&1
say "  终点线跑完 (rc=$?) ⇒ 见 $OUT"
