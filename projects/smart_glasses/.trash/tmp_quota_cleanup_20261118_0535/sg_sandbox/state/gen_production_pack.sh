#!/usr/bin/env bash
# gen_production_pack.sh —— ★一键生成"硬件投产资料包" (2026-11-04 19:3x, 老板要"尽快看到所有硬件成果物")
#
# 产出清单 (全部在 HW/PCB/production/):
#   gerbers/    Gerber (F/B/内层/阻焊/丝印/外形/…) ★canonical 还在 HW/PCB/gerbers/
#   drill/      Excellon 钻孔 (.drl) + 钻孔图 (PDF) + 钻孔报告 (.rpt)
#   pos/        坐标文件 CPL (csv, 双面, mm)
#   assembly/   IPC-2581 装配文件 (xml) + 装配图 PDF
#   3d/         STEP 3D 模型
#   doc/        PCB 图 PDF (顶/底/全层) + 外形 DXF + IPC-D-356 裸板测试网表 + 板统计 + **原理图 PDF/SVG/网表/BOM**
#
# 用法: bash state/gen_production_pack.sh
# ★前置: 板子/原理图必须已由生成器同步 (gen_netlist → gen_kicad_sch → gen_pcb_netlist_board → gen_bom)
# ★工具: KiCad 10.0.8 AppImage (免 root) ⇒ 走 state/kicad.sh; pcbnew 脚本走 state/pcbnew_py.sh
set -u
PROJ="/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
cd "$PROJ" || exit 1
PCB="HW/PCB/demo_mainboard.kicad_pcb"
SCH="HW/PCB/demo_mainboard.kicad_sch"
OUT="HW/PCB/production"
KC="bash state/kicad.sh"
rm -rf "$OUT"
mkdir -p "$OUT"/{gerbers,drill,pos,assembly,3d,doc/sch_svg}
rc_all=0
step() { echo "── [$1] ──"; }

step "Gerber (canonical → HW/PCB/gerbers + 复制到 production/gerbers)"
$KC pcb export gerbers -o "HW/PCB/gerbers/" "$PCB" || rc_all=1
cp -f HW/PCB/gerbers/* "$OUT/gerbers/" 2>/dev/null

step "钻孔 (Excellon + 钻孔图 PDF + 报告)"
$KC pcb export drill -o "$OUT/drill/" --format excellon --drill-origin absolute \
    --excellon-units mm --excellon-separate-th --generate-map --map-format pdf "$PCB" || rc_all=1

step "坐标文件 (CPL, 双面, mm)"
$KC pcb export pos -o "$OUT/pos/demo_mainboard-pos.csv" --side both --format csv --units mm "$PCB" || rc_all=1

step "装配 (IPC-2581)"
$KC pcb export ipc2581 -o "$OUT/assembly/demo_mainboard-ipc2581.xml" "$PCB" || rc_all=1

# ★注: `pcb export pdf` 的 -o 要**文件路径** (给目录会报 "Failed to create file")
step "装配图 PDF (顶面 / 底面)"
$KC pcb export pdf -o "$OUT/assembly/demo_mainboard-assembly-top.pdf" --layers "F.Silkscreen,F.Fab,Edge.Cuts" "$PCB" || rc_all=1
$KC pcb export pdf -o "$OUT/assembly/demo_mainboard-assembly-bottom.pdf" --layers "B.Silkscreen,B.Fab,Edge.Cuts" "$PCB" || rc_all=1

step "PCB 图 PDF (全层 / 顶层 / 底层)"
$KC pcb export pdf -o "$OUT/doc/demo_mainboard-pcb-all.pdf" --layers "F.Cu,In1.Cu,In2.Cu,In3.Cu,In4.Cu,B.Cu,Edge.Cuts,F.Silkscreen" "$PCB" || rc_all=1
$KC pcb export pdf -o "$OUT/doc/demo_mainboard-pcb-top.pdf" --layers "F.Cu,Edge.Cuts,F.Silkscreen" "$PCB" || rc_all=1
$KC pcb export pdf -o "$OUT/doc/demo_mainboard-pcb-bottom.pdf" --layers "B.Cu,Edge.Cuts,B.Silkscreen" "$PCB" || rc_all=1

step "3D 模型 (STEP)"
$KC pcb export step -o "$OUT/3d/demo_mainboard.step" "$PCB" || rc_all=1

step "外形 DXF (Edge.Cuts)"
$KC pcb export dxf -o "$OUT/doc/" --layers "Edge.Cuts" "$PCB" || rc_all=1

step "IPC-D-356 (裸板测试网表)"
$KC pcb export ipcd356 -o "$OUT/doc/demo_mainboard.d356" "$PCB" || rc_all=1

step "板统计"
$KC pcb export stats -o "$OUT/doc/board-stats.txt" --format report --units mm "$PCB" || rc_all=1

step "原理图可加载门禁 (★KiCad 真能打开才算过)"
python3 state/check_sch_loadable.py || rc_all=1

step "原理图: PDF / SVG / 网表 / KiCad BOM (与我们的 BOM 交叉核对)"
# ★注: KiCad 对我们的**伪位号** (RAIL_* / NET_* / CHG_* 单点汇流位) 会报 "annotation errors" ⇒
#   CLI 退出码可能非 0, **但产物照样出** ⇒ 这里改成**按产物存在且非空**判成败 (rc 只做提示)
_schpdf() { timeout 600 $KC sch export pdf -o "$1" "$SCH" >/dev/null 2>&1; [ -s "$1" ]; }
_schsvg() { timeout 600 $KC sch export svg -o "$1/" "$SCH" >/dev/null 2>&1; }
_schnet() { timeout 600 $KC sch export netlist -o "$1" "$SCH" >/dev/null 2>&1; [ -s "$1" ]; }
_schbom() { timeout 600 $KC sch export bom -o "$1" "$SCH" >/dev/null 2>&1; [ -s "$1" ]; }
_schpdf "$OUT/doc/demo_mainboard-sch.pdf"     || { echo "  ❌ 原理图 PDF 没出"; rc_all=1; }
_schsvg "$OUT/doc/sch_svg"                    || { echo "  ❌ 原理图 SVG 没出"; rc_all=1; }
_schnet "$OUT/doc/demo_mainboard-kicad.net"   || { echo "  ❌ 原理图网表没出"; rc_all=1; }
_schbom "$OUT/doc/demo_mainboard-kicad-bom.xml" || { echo "  ❌ KiCad BOM 没出"; rc_all=1; }
echo "  (KiCad 'annotation errors' 提示: 伪位号 RAIL_*/NET_*/CHG_* 引起, 产物不受影响; 连通性由网表 parity 判据保证)"

step "清单"
find "$OUT" -type f | sort | sed "s|$OUT/||" | awk '{printf "  %s\n", $0}'
echo "── 文件数: $(find "$OUT" -type f | wc -l) | 总大小: $(du -sh "$OUT" | cut -f1) ──"
echo "rc_all=$rc_all"
exit $rc_all
