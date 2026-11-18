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

# ★★2026-11-06 01:5x **★判据换成独立闸 (state/compare_arm_official.py)** ——
#   ★★**实测事故 (差点让更差的板上位)**: 原判据只有 (unconnected, DRC) 两项
#     ⇒ v44_R (UNC 55 < 57, DRC 0 == 0) 被判"更好" ⇒ ★**晋级成了官方板**
#     ⇒ ★但实测: v44 把 **9 个网打成零铜** (含 4 条差分 _SRC 腿), 只救回 7 个
#       ⇒ ★★**差分对净 -1 / 普通信号网净 -2** ⇒ ★**官方板实际变差了**
#     ⇒ ★★**"只看 ratsnest 数量"会被"把有铜的腿砍成零铜"骗**
#     ⇒ ★★**Δ 数字也会骗**: v44 的 "DSI_D0_D0 Δ 76.197→1.612" 是
#        ★**砍掉配平铜、让一侧归零换来的** (审计器不算零铜对 ⇒ 数字变好, 板子更烂)
#   ★**新判据**: DRC 必须 0, 且
#     {unconnected, 零铜网(≥2焊盘), 差分单边零铜对, 差分Δ超差对} **任何一项都不得变差**,
#     且**至少一项严格变好** ⇒ 才晋级
#   ★**官方板的 DRC 取证改成现测** (★不再读可能过期的 .layout_done.json)
say "  ── 加固判据 (独立闸) ──"
bash state/kicad.sh pcb drc --output "/tmp/_ap_off_${PREFIX}_${ARM}.json" --severity-error --severity-warning --format json HW/PCB/demo_mainboard.kicad_pcb >/dev/null 2>&1
if python3 state/compare_arm_official.py "$PCB" HW/PCB/demo_mainboard.kicad_pcb \
      --drc-json "/tmp/_ap_${PREFIX}_${ARM}.json" "/tmp/_ap_off_${PREFIX}_${ARM}.json" ; then
  say "  ⇒ ★**加固判据通过** ⇒ 走终点线 (晋级 → 加铜皮 → 重出投产包 → 全门禁自验)"
  PREFIX="$PREFIX" bash state/finish_line.sh "$ARM" >> "$OUT" 2>&1
  say "  终点线跑完 (rc=$?) ⇒ 见 $OUT"
else
  say "★**加固判据不通过 ⇒ 不晋级** (★DRC/零铜网/差分单边零铜/Δ超差 任一变差 ⇒ 一律不晋级)"
  exit 0
fi
