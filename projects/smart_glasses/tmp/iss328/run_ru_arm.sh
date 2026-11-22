#!/usr/bin/env bash
# iss328_run_ru_arm.sh -- ★★★【ISS-328 · S8 右上对照臂 · 后台长跑 (nohup)】★★★
#
# ★★★**★这是什么 (★性质★)**★★★ ★★★
#   ★**沙盒预演 · 零写板 · 零落表 · 零改闸 · 零改生成器代码** ★**
#   ★**官方板 HW/PCB/demo_mainboard.kicad_pcb 一个字节都不许动** ★★
#     ⇒ PCB_OUT 指向 tmp/iss328/ · ★**绝不许设 PCB_ALLOW_OFFICIAL=1** ★★
#     ⇒ PCB_REPORT 指向 tmp/iss328/ (★否则会覆盖 HW/PCB/PCB_NETLIST_FILL.txt★) ★★
#
# ★★★★★**★唯一变量 (★单变量的字面证据★)**★★★★** ★★★
#   ★**基线臂 = `state/v76mz_arms.sh` L37~L50 (ISS-325 同日同代码对照臂, 同一份 env)** ★**
#     ⇒ 基线臂的 PCB_PART_POS = 【10 个 R_SEL_* @ 左上 x5.50..38.35 y3.00】★**不含任何 TP_DSI_*** ★**
#   ★**本臂 env 与基线臂逐位相同 ⇒ 唯一差别 = 那 10 个 R_SEL_* 的坐标 (左上 → 右上 §3 方案 A)** ★**
#   ★**本臂【不钉任何 TP_DSI_*】★ ⇒ TP 由生成器「测试点贴伙伴件」规则自动落位 (★基线臂同样不钉★) ★**
#
# ★★★★★**★坐标帧声明 (★ISS-274 · 2026-11-17★)**★★★★** ★★★
#   ★**本臂全部坐标 = 160×100 台架板帧 (帧 id `B160x100` · 板 160.00×100.00mm / 8 铜层 / 186 封装)** ★**
#   ★**不是 60×30 套A 帧 (F30A) · 也不是 60×15 帧** ★
#   ★**坐标来源 = `HW/PCB/LAYOUT_FIX_SPEC.md` §3 方案 A 的右上那组 (★机器读自官方板★) ★**
#
# ★★★★★**★写盘纪律 (★本脚本自己保证★)**★★★★** ★★★
#   ★ 链/clrfix/对照脚本全部在 tmp/iss328/ 里做【路径改写副本】⇒ 不写项目树 ★
#   ★ PCB_DOC_OUT 指向 tmp/iss328/docout ⇒ gen_kicad_project.py 的 4 个产物不落 HW/PCB/ ★
#   ★ 真板 md5 跑前跑后各记一次 ⇒ 交卷页贴出来 ★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

SBX=$PROJ/tmp/iss328
LOGD=$PROJ/logs/iss328
TAG=iss328_s8ru
mkdir -p "$SBX" "$LOGD" "$SBX/docout" "$SBX/cab"

OUT=$SBX/ru_R.kicad_pcb
GENLOG=$SBX/ru_R.gen.log
DRC=$SBX/ru_R.drc.json
REPORT=$SBX/ru_REPORT.txt
RESERVE_FILE="$PROJ/state/.lastgood/v76mg_reserve.txt"
PPFILE=$LOGD/05_RU_PCB_PART_POS.txt

echo "=== ISS-328 S8 右上臂 (后台长跑) 开始 $(date '+%F %T') ==="

# ── 0 · 沙盒副本 (路径改写 ⇒ 只写 tmp/iss328/) ──
cp -f "$PROJ/state/replay_patch_chain.sh" "$SBX/chain_sbx.sh"
sed -i "s#^WORK=/tmp/chain_\${TAG}#WORK=\"\$PROJ/tmp/iss328/chain_\${TAG}\"#" "$SBX/chain_sbx.sh"
sed -i 's#^  OFFDRC="/tmp/_drc45.json"#  OFFDRC="$PROJ/tmp/iss328/_drc45.json"#' "$SBX/chain_sbx.sh"
cp -f "$PROJ/state/clrfix_iter.sh" "$SBX/clrfix_sbx.sh"
sed -i "s#^WORK=/tmp/_clriter_\$TAG.kicad_pcb#WORK=\"\$PROJ/tmp/iss328/_clriter_\$TAG.kicad_pcb\"#" "$SBX/clrfix_sbx.sh"
sed -i "s#^FIN=/tmp/_clrfix_\${TAG}_final.kicad_pcb#FIN=\"\$PROJ/tmp/iss328/_clrfix_\${TAG}_final.kicad_pcb\"#" "$SBX/clrfix_sbx.sh"
sed -i "s#/tmp/_clriter_\${TAG}.BADRULES.drc.json#\$PROJ/tmp/iss328/_clriter_\${TAG}.BADRULES.drc.json#" "$SBX/clrfix_sbx.sh"
cp -f "$PROJ/state/compare_arm_baseline.sh" "$SBX/compare_arm_baseline_sbx.sh"
sed -i 's#"/tmp/_cab_#"'"$SBX"'/cab/_cab_#g' "$SBX/compare_arm_baseline_sbx.sh"
echo "  ✓ 沙盒副本: chain_sbx.sh / clrfix_sbx.sh / compare_arm_baseline_sbx.sh"
grep -n "^WORK=\|^FIN=\|OFFDRC=" "$SBX/chain_sbx.sh" "$SBX/clrfix_sbx.sh" | sed 's/^/    /'

# ── 1 · 守卫 (零写板 / 软链 / 不覆盖) ──
for f in "$OUT" "$GENLOG" "$DRC" "$REPORT" "$PPFILE"; do
  if [ -L "$f" ]; then echo "❌ $f 是软链 ⇒ 收工"; exit 4; fi
done
if [ -e "$OUT" ] || [ -e "$GENLOG" ]; then
  echo "  [${TAG}] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"; exit 0
fi
[ -f "$RESERVE_FILE" ] || { echo "❌ 没有 v76mg 的预留串 ⇒ 收工"; exit 3; }
[ -f "$PPFILE" ] || { echo "❌ 没有 PCB_PART_POS 文件 ⇒ 收工"; exit 3; }
RESERVE=$(cat "$RESERVE_FILE")
PP=$(cat "$PPFILE")
echo "  ✓ 真板 md5 (跑前) = $(md5sum "$PROJ/HW/PCB/demo_mainboard.kicad_pcb" | awk '{print $1}')"
echo "  ✓ 真板 mtime (跑前) = $(stat -c '%y' "$PROJ/HW/PCB/demo_mainboard.kicad_pcb")"
echo "  ✓ 预留串 md5 = $(md5sum "$RESERVE_FILE" | awk '{print $1}') (★只读复用★)"
echo "  ✓ PCB_PART_POS (★机器读·零手抄★) ="
echo "      $PP"
echo "  ✓ 工具指纹 gen_pcb_routing.py sha256 = $(sha256sum state/gen_pcb_routing.py | cut -c1-16)"
echo "  ✓ 工具指纹 gen_pcb_netlist_board.py sha256 = $(sha256sum state/gen_pcb_netlist_board.py | cut -c1-16)"
echo "  ✓ 工具指纹 replay_patch_chain.sh sha256 = $(sha256sum state/replay_patch_chain.sh | cut -c1-16)"

# ── 2 · 路由 (★唯一变量 = 10 个 R_SEL_* 坐标★ · env 与基线臂逐位相同) ──
env PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.0625 \
    PCB_BOARD_W=160 PCB_BOARD_H=100 \
    PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
    PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
    PCB_PAIR_EXEMPT_R=0.0 \
    PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 \
    PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
    PCB_PART_POS="$PP" \
    PCB_PAIR_BEFORE_PWR=1 PCB_PRIORITY_NETS="FSIN_OUT;LIGHT_5V;LIGHT_3V3;I2C_A_SCL;I2C_A_SDA;I2C_B_SCL;I2C_B_SDA;LED_G;LED_G_D;KEY_CAM;JTAG_TDI;SPI_SCLK_BOOT;SPI_MOSI_BOOT;SPI_MISO_BOOT;UART_RX;USB_CC2;BAT_DET;ID_DETECT_0;ID_DETECT_1;JTAG_TDO;JTAG_TMS;UART_TX;LED_B_D" PCB_W_MIN=0.15 \
    PCB_VIA_HALO_CENTER=1 PCB_MERGE_FIX=1 PCB_ESC_ROWNORM=2 \
    PCB_ROUTE_RESERVE="$RESERVE" PCB_PRIO_SPAN_SORT=1 \
    PCB_MEANDER_EDGE=1 \
    PCB_GRID=0.125 \
    PCB_OUT="$OUT" \
    PCB_REPORT="$REPORT" \
    PCB_DOC_OUT="$SBX/docout" \
    timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
    > "$GENLOG" 2>&1
echo "EXIT=$?" >> "$GENLOG"
echo "  [${TAG}] 路由器 EXIT 记录完毕 $(date '+%F %T')"
[ -f "$OUT" ] || { echo "❌ 没出板 ⇒ 收工"; exit 2; }
echo "  ✓ 板 md5 = $(md5sum "$OUT" | awk '{print $1}') · 段数 = $(grep -ac '(segment' "$OUT")"

# ── 3 · 板规则 min track width → 0.15 ──
bash state/pcbnew_py.sh - "$OUT" <<'PY'
import pcbnew, sys
p = sys.argv[1]
b = pcbnew.LoadBoard(p)
if b is None:
    print("  ❌ 板读不出来"); raise SystemExit(1)
b.GetDesignSettings().m_TrackMinWidth = int(0.15 * 1e6)
b.Save(p)
print("  ✓ min track width → 0.15 :", p)
PY

# ── 4 · fresh DRC (裸板) ──
bash state/kicad.sh pcb drc --output "$DRC" --severity-error --severity-warning --format json "$OUT" >/dev/null 2>&1
python3 - "$DRC" <<'PY'
import json, sys, collections
d = json.load(open(sys.argv[1], encoding="utf-8"))
v = d.get("violations") or []
print("  裸板: 违规=%d · unc=%d · %s" % (len(v), len(d.get("unconnected_items") or []),
      dict(collections.Counter(x.get("type") for x in v).most_common(6))))
PY

# ── 5 · 套链 (★loose 步 margin 0.03125 ⇒ 与 v76mz / ISS-325 两臂同配方★) ──
PCB_CHAIN_LOOSE_MARGIN=0.03125 PCB_DOC_OUT="$SBX/docout" bash "$SBX/chain_sbx.sh" "$OUT" "$TAG"
echo "  链 rc=$?"
FINAL=$SBX/chain_${TAG}/final_chain.kicad_pcb

if [ -f "$FINAL" ]; then
  echo "── 边际净距修复 (★把 DRC 违规清零★) ──"
  bash "$SBX/clrfix_sbx.sh" "$FINAL" "${FINAL}.drc.json" --max 5 --tag "$TAG"
  CLR=$SBX/_clrfix_${TAG}_final.kicad_pcb
  echo "── 链终板 vs 官方板 (★名单制闸 compare_arm_official.py★) ──"
  python3 state/compare_arm_official.py "$FINAL" "$PROJ/HW/PCB/demo_mainboard.kicad_pcb" 2>&1 | tail -60
  echo "  ★名单制闸 rc=$?"
  if [ -f "$CLR" ]; then
    echo "── clrfix 终板 vs 官方板 (★名单制闸★) ──"
    python3 state/compare_arm_official.py "$CLR" "$PROJ/HW/PCB/demo_mainboard.kicad_pcb" 2>&1 | tail -60
    echo "  ★名单制闸 rc=$?"
  fi
  echo "── vs 同日同代码基线臂 (ISS-325 对照臂链终板) ──"
  BASE=$SBX/baseline_ctl_chain.kicad_pcb
  if [ -f "$BASE" ]; then
    bash "$SBX/compare_arm_baseline_sbx.sh" "$FINAL" --baseline "$BASE" 2>&1 | tail -80
    echo "  ★对照闸 rc=$?"
  else
    echo "  ⚠️ 基线臂链终板不在盘 ⇒ 跳过臂间对照 (下一趟补)"
  fi
else
  echo "❌ 链没跑完 (终板没生成) ⇒ ★**本轮结果不算数** (看 chain.log 尾部 Traceback)"
fi

echo "  ✓ 真板 md5 (跑后) = $(md5sum "$PROJ/HW/PCB/demo_mainboard.kicad_pcb" | awk '{print $1}')"
echo "  ✓ 真板 mtime (跑后) = $(stat -c '%y' "$PROJ/HW/PCB/demo_mainboard.kicad_pcb")"
echo "=== ISS-328 S8 右上臂 全流程结束 $(date '+%F %T') ==="
