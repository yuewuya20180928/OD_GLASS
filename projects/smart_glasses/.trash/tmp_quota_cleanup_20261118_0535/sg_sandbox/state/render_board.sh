#!/usr/bin/env bash
# render_board.sh —— ★把板子渲染成 PNG, 用来"用眼睛验" (2026-11-05 03:4x)
# 用法: bash state/render_board.sh [输出目录] [DPI]
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
OUT="${1:-/tmp/board_render}"
DPI="${2:-110}"
PCB=HW/PCB/demo_mainboard.kicad_pcb
rm -rf "$OUT"; mkdir -p "$OUT"
bash state/kicad.sh pcb export pdf -o "$OUT/top.pdf"    --layers "F.Cu,Edge.Cuts,F.Silkscreen" "$PCB" >/dev/null 2>&1
bash state/kicad.sh pcb export pdf -o "$OUT/bot.pdf"    --layers "B.Cu,Edge.Cuts,B.Silkscreen" "$PCB" >/dev/null 2>&1
bash state/kicad.sh pcb export pdf -o "$OUT/inner.pdf" --layers "In1.Cu,In2.Cu,In3.Cu,In4.Cu,Edge.Cuts" "$PCB" >/dev/null 2>&1
for f in "$OUT"/*.pdf; do
  b=$(basename "$f" .pdf)
  pdftoppm -png -r "$DPI" "$f" "$OUT/$b" 2>/dev/null
done
ls -la "$OUT"/*.png 2>/dev/null | awk '{print $5, $9}'
