#!/usr/bin/env bash
# freeroute_run.sh —— ★**工业级自动布线 (freerouting) 流水线** (2026-11-05 08:10)
# 目的: 自研路由器到顶时的**备选路径** —— 用 KiCad 的 Specctra DSN/SES 接口把板子交给 freerouting
# 用法: bash state/freeroute_run.sh [板路径] [轮数]
#   默认板 = /tmp/fr_place.kicad_pcb (由 PCB_SKIP_ROUTE=1 生成的"只有排版没有走线"的板)
# 流程: ① 导出 DSN ② 跑 freerouting ③ 把 SES 导回板 ④ 打印统计
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
PCB="${1:-/tmp/fr_place.kicad_pcb}"
PASSES="${2:-30}"
DSN=/tmp/fr_board.dsn
SES=/tmp/fr_board.ses
OUT=/tmp/fr_routed.kicad_pcb
JRE=$(ls -d ~/tools/jdk-*/bin/java 2>/dev/null | head -1)
[ -z "$JRE" ] && JRE=$(ls -d ~/tools/jdk-*/jre/bin/java 2>/dev/null | head -1)
JAR=~/tools/freerouting.jar

echo "=== 0) 准备 ==="
echo "  板: $PCB"
echo "  java: ${JRE:-缺失}"
echo "  jar : $(ls -la $JAR 2>/dev/null | awk '{print $5"字节"}')"
[ -x "$JRE" ] || { echo "❌ 没有 JRE"; exit 1; }
[ -f "$JAR" ] || { echo "❌ 没有 freerouting.jar"; exit 1; }

echo "=== 1) 导出 Specctra DSN ==="
cat > /tmp/_export_dsn.py <<'PY'
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1])
ok = pcbnew.ExportSpecctraDSN(b, sys.argv[2])
print("  ExportSpecctraDSN ->", ok)
PY
bash state/pcbnew_py.sh /tmp/_export_dsn.py "$PCB" "$DSN" 2>&1 | tail -2
[ -s "$DSN" ] || { echo "❌ DSN 没导出"; exit 1; }
ls -la "$DSN" | awk '{print "  DSN 大小:", $5, "字节"}'

echo "=== 2) 跑 freerouting (headless, $PASSES 轮) ==="
cp "$PCB" "$OUT"
timeout 7200 "$JRE" -Xmx4g -jar "$JAR" -de "$DSN" -do "$SES" -mp "$PASSES" 2>&1 | tail -25
echo "  freerouting 退出码: $?"
[ -s "$SES" ] || { echo "❌ 没生成 SES"; exit 1; }
ls -la "$SES" | awk '{print "  SES 大小:", $5, "字节"}'

echo "=== 3) 把 SES 导回板 ==="
cat > /tmp/_import_ses.py <<'PY'
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1])
ok = pcbnew.ImportSpecctraSES(b, sys.argv[2])
print("  ImportSpecctraSES ->", ok)
pcbnew.SaveBoard(sys.argv[3], b)
print("  已存:", sys.argv[3])
PY
bash state/pcbnew_py.sh /tmp/_import_ses.py "$PCB" "$SES" "$OUT" 2>&1 | tail -3

echo "=== 4) 统计 ==="
echo "  走线段数: $(grep -c '(segment' "$OUT")"
echo "  过孔数  : $(grep -c '(via' "$OUT")"
