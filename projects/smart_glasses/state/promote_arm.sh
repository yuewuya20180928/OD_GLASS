#!/usr/bin/env bash
# promote_arm.sh —— ★**把赢家臂的板晋级到官方板** (2026-11-05 08:25)
# 用法: bash state/promote_arm.sh <A|B|C|D>
# 流程: ① 校验收工闸 (段数>0 且 与落盘印一致) ② ★**先跑 DRC/parity 预检** ③ 备份官方板 (内存 + 持久)
#       ④ 复制 + 写落盘印 ⑤ 跑全量取证
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
ARM="${1:?用法: promote_arm.sh <A|B|C|D>}"
SRC="/tmp/v26_${ARM}.kicad_pcb"
PCB=HW/PCB/demo_mainboard.kicad_pcb
LOG="/tmp/v26_${ARM}.log"

echo "══════ 晋级 臂 $ARM ══════"
[ -f "$SRC" ] || { echo "❌ 没有 $SRC"; exit 1; }
SEG=$(grep -c '(segment' "$SRC"); VIA=$(grep -c '(via' "$SRC")
echo "  臂板: $SEG 段 / $VIA 孔  ($(ls -la --time-style=+%H:%M:%S "$SRC" | awk '{print $6,$7}'))"
[ "$SEG" -gt 1000 ] || { echo "❌ 段数太少 ⇒ 不晋级"; exit 1; }
echo "  日志收工标记:"; grep -E "\[FAIL\]|\[SUM \]|落板自检|EXIT=" "$LOG" | tail -4

# ★★2026-11-05 09:35 **晋级前预检**: ★parity 不过 ⇒ 板与网表不一致 ⇒ 绝不能当官方板
echo "  ── 预检 (臂板) ──"
bash state/kicad.sh pcb drc --output /tmp/_promote_drc.json --severity-error --severity-warning --format json "$SRC" >/dev/null 2>&1
python3 - <<'PY'
import json
try:
    d = json.load(open('/tmp/_promote_drc.json'))
    v = len(d.get('violations') or []); u = len(d.get('unconnected_items') or [])
    print("  臂板 DRC=%d  unconnected=%d" % (v, u))
except Exception as e:
    print("  ⚠️ DRC 取证失败: %s" % e)
PY
bash state/pcbnew_py.sh state/check_pcb_nets.py "$SRC" >/tmp/_promote_parity.log 2>&1
PRC=$?
echo "  臂板 parity rc=$PRC"
if [ "$PRC" -ne 0 ]; then
  echo "❌ ★**臂板与网表不一致 (parity 红) ⇒ 拒绝晋级**"; tail -6 /tmp/_promote_parity.log; exit 1
fi

# ① 备份官方板 (内存 + ★持久位置, /tmp 重启即失)
STAMP=$(date +%Y%m%d_%H%M%S)
BK="/tmp/board_prev_before_promote_${STAMP}.kicad_pcb"
cp -p "$PCB" "$BK"; echo "  旧官方板已备份: $BK ($(grep -c '(segment' "$BK") 段)"
mkdir -p state/.lastgood ~/board_backups
cp -p "$PCB" "state/.lastgood/board_prev_promote_${STAMP}.kicad_pcb"
cp -p "$PCB" "$HOME/board_backups/board_prev_promote_${STAMP}.kicad_pcb"
echo "  ★持久备份: state/.lastgood/ + ~/board_backups/"
# ② 复制
cp "$SRC" "$PCB"
# ③ 写落盘印 (★at = 板自己的 mtime ⇒ 闸门只对"真被改过的板"报警)
python3 - "$PCB" <<'PY'
import json, os, sys, time
p = sys.argv[1]
seg = via = 0
for l in open(p, encoding="utf-8", errors="ignore"):
    s = l.lstrip()
    if s.startswith("(segment"): seg += 1
    elif s.startswith("(via"): via += 1
land = {"at": int(os.stat(p).st_mtime), "tracks": seg, "vias": via,
        "pcb": os.path.basename(p), "landed_at": int(time.time())}
json.dump(land, open(os.path.join(os.path.dirname(p), ".layout_landed.json"), "w",
                     encoding="utf-8"), ensure_ascii=False)
print("  落盘印:", json.dumps(land, ensure_ascii=False))
PY
# ④ 全量取证
bash state/board_report.sh "$PCB" "$LOG" 2>&1 | tail -40
