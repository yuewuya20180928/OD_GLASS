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
# ★★2026-11-05 09:05: ★**2.1.0 需要 class v65 = Java 21** (JRE17 只到 v61; 2.5.0 要 v69=Java25)
#   ⇒ ★**优先用 jdk-21** ⇒ 没有才退回 jdk-17 + 1.9.0 (但 1.9.0 是 GUI 版 ⇒ HeadlessException)
JRE=""
for c in ~/tools/jdk-21*/bin/java ~/tools/jdk-21*/jre/bin/java ~/tools/jdk-17*/bin/java ~/tools/jdk-17*/jre/bin/java; do
  [ -x "$c" ] && { JRE="$c"; break; }
done
JAR=""
for c in ~/tools/fr_2.1.0.jar ~/tools/freerouting.jar ~/tools/fr_1.9.0.jar; do
  [ -f "$c" ] && { JAR="$c"; break; }
done

echo "=== 0) 准备 ==="
echo "  板: $PCB"
echo "  java: ${JRE:-缺失}"
echo "  jar : ${JAR:-缺失} $(ls -la $JAR 2>/dev/null | awk '{print $5}')字节"
[ -x "$JRE" ] || { echo "❌ 没有 JRE"; exit 1; }
[ -f "$JAR" ] || { echo "❌ 没有 freerouting.jar"; exit 1; }
"$JRE" -version 2>&1 | head -1 | sed 's/^/  /'

echo "=== 0.5) 若没给板 ⇒ 先生成"只有排版没走线"的当前版板 (PCB_SKIP_ROUTE=1) ==="
if [ ! -f "$PCB" ]; then
  echo "  生成 $PCB ..."
  PCB_SKIP_ROUTE=1 PCB_OUT="$PCB" bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py 2>&1 | tail -3
fi
[ -f "$PCB" ] || { echo "❌ 没有可导出的板"; exit 1; }

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
# ★★2026-11-05 10:01: freerouting 2.x 启动会试图取屏幕分辨率 ⇒ **无头环境必须显式关 GUI**
#   ⇒ 不加 `-Dgui.enabled=false` 时会 WARN + 可能起 GUI ⇒ ★**实测 2.1.0 加了就能纯 CLI 跑**
# ★★2026-11-05 10:35 **堆从 4g 降到 2g** (★实测被 OOM 杀掉一次)
#   机器只有 14GB, 同时跑 4~5 个布线进程 (每个 ~2GB) ⇒ ★JVM 4g 会把内存吃光
#   ⇒ ★**跑 freerouting 时别同时开太多布线臂** (★或者给它 2g 就够)
# ★★2026-11-06 09:2x 改: **输出落盘** (★原来 `| tail -25` ⇒ 缓冲 ⇒ 进程结束才可见 ⇒ 长跑期间看不到进度)
#   ⇒ ★**freerouting 每轮都打 INFO (pass #N ... score ... unrouted)** ⇒ ★**落盘后随时可 tail 看进度**
FR_LOG=/tmp/fr_progress.log
timeout 14400 "$JRE" -Xmx2g -Dgui.enabled=false -jar "$JAR" -de "$DSN" -do "$SES" -mp "$PASSES" > "$FR_LOG" 2>&1
FR_RC=$?
echo "  freerouting 退出码: $FR_RC  (完整日志: $FR_LOG)"
grep -o "pass #[0-9]* .*unrouted)" "$FR_LOG" | tail -5
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
