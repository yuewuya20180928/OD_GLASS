#!/usr/bin/env bash
# promote_arm.sh —— ★**把赢家臂的板晋级到官方板** (2026-11-05 08:25)
# 用法: bash state/promote_arm.sh <A|B|C|D>
# 流程: ① 校验收工闸 (段数>0 且 与落盘印一致) ② 备份官方板 ③ 复制 + 写落盘印 ④ 跑全量取证
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

# ① 备份官方板
BK="/tmp/board_prev_before_promote_$(date +%H%M%S).kicad_pcb"
cp -p "$PCB" "$BK"; echo "  旧官方板已备份: $BK ($(grep -c '(segment' "$BK") 段)"
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
