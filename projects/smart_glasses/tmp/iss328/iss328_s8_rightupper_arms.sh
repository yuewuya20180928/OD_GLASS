#!/usr/bin/env bash
# iss328_s8_rightupper_arms.sh -- ★★★【ISS-328 · S8 右上布局对照臂 (零写板 · 沙盒预演)】★★★
#
# ★★★★★**★这是什么 (★性质★)**★★★★** ★★★
#   ★**这是 ISS-322/ISS-265 处方「10 个 R_SEL_* 挪到右上 (§3 方案 A 那组坐标)」的第一条
#     【真能构成对照】的臂** ★** (★ISS-325 那两条臂全板 185 封装落位逐个相同 ⇒ 对照无效★) ★**
#   ★**主交付物**: HW/PCB/ONETRIP_S8_RIGHTUPPER_CONTROL_ARM.md ★**
#   ★**性质**: ★**沙盒预演 · 零写板 · 零落表 · 零改闸 · 零改生成器代码** ★**
#   ★**官方板 HW/PCB/demo_mainboard.kicad_pcb 一个字节都不许动** ★**
#     ⇒ PCB_OUT = /tmp/iss328_s8ru_R.kicad_pcb ★**绝不许设 PCB_ALLOW_OFFICIAL=1** ★**
#     ⇒ PCB_REPORT = /tmp/iss328_s8ru_REPORT.txt ★**否则会覆盖 HW/PCB/PCB_NETLIST_FILL.txt** ★**
#
# ★★★★★**★唯一变量 (★单变量的字面证据★)**★★★★** ★★★
#   ★**基线臂 = `state/iss325_s8_control_v76mz_arms.sh` (ISS-325 同日同代码对照臂, 已在盘上) ★**
#     ⇒ 该臂的 PCB_PART_POS = 【10 个 R_SEL_* @ 左上】★**没有 TP_DSI_* 条目** ★
#   ★**本臂 env 与 v76mz 逐字节相同 ⇒ 唯一差别 = 那 10 个 R_SEL_* 的坐标 (左上 → 右上) ★**
#   ★**本臂【不钉任何 TP_DSI_*】★ ⇒ TP 由生成器「测试点贴伙伴件」规则自动落位
#     (★基线臂同样不钉 ⇒ 两条臂的 TP 处置【完全一致】★) ★
#   ★**⇒ ⇒ 两臂之间【全板封装落位必然不同】⇒ ⇒ 对照【有效】★★
#
# ★**坐标帧声明 (★ISS-274 · 2026-11-17 ★)**: ★**本臂全部坐标 = 160×100 台架板帧
#   (帧 id `B160x100` · 板 160.00×100.00mm / 8 铜层 / 186 封装)★** ⇒ ★**不是 60×30 套A 帧
#   (F30A) · 也不是 60×15 帧** ★ ★**坐标来源 = `HW/PCB/LAYOUT_FIX_SPEC.md` §3 方案 A
#   的右上那组 (★机器读自官方板 HW/PCB/demo_mainboard.kicad_pcb, 见
#   logs/iss328/01_official_RSEL_TP_pos.tsv + logs/iss328/05_RU_PCB_PART_POS.txt★) ★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

TAG=iss328_s8ru
OUT=/tmp/${TAG}_R.kicad_pcb
LOG=/tmp/${TAG}_R.log
DRC=/tmp/${TAG}_R.drc.json
REPORT=/tmp/${TAG}_REPORT.txt
RESERVE_FILE="$PROJ/state/.lastgood/v76mg_reserve.txt"
PPFILE="$PROJ/logs/iss328/05_RU_PCB_PART_POS.txt"
EVDIR="$PROJ/logs/iss328"
mkdir -p "$EVDIR"

# ★★软链守卫 (★sw-lead 11-18 14:39 踩过的坑: 软链写穿真件★) ★★
for f in "$OUT" "$LOG" "$DRC" "$REPORT" "$PPFILE"; do
  if [ -L "$f" ]; then echo "❌ $f 是软链 ⇒ 收工"; exit 4; fi
done

# ★**不许覆盖历史产物** ★
if [ -e "$OUT" ] || [ -e "$LOG" ]; then
  echo "  [${TAG}] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"
  exit 0
fi
[ -f "$RESERVE_FILE" ] || { echo "❌ 没有 v76mg 的预留串 ⇒ 收工"; exit 3; }
[ -f "$PPFILE" ] || { echo "❌ 没有 PCB_PART_POS 文件 ⇒ 收工"; exit 3; }
RESERVE=$(cat "$RESERVE_FILE")
PP=$(cat "$PPFILE")

echo "=== ISS-328 S8 右上臂: env = v76mz 逐位相同 · 唯一变量 = 10 个 R_SEL_* 坐标 (左上 → 右上 §3 方案 A) ==="
echo "  ✓ 预留串 md5 = $(md5sum "$RESERVE_FILE" | awk '{print $1}') (★只读复用·不许覆盖★)"
echo "  ✓ PCB_PART_POS (★机器读·零手抄★) ="
echo "      $PP"
echo "  ✓ 工具指纹 gen_pcb_routing.py sha256 = $(sha256sum state/gen_pcb_routing.py | cut -c1-16)"
echo "  ✓ 工具指纹 gen_pcb_netlist_board.py sha256 = $(sha256sum state/gen_pcb_netlist_board.py | cut -c1-16)"

# ★★env 快照落盘 (交卷要用) ★★
{
  echo "# ISS-328 右上臂 env 快照 (★生成时刻 $(date '+%F %T')★)"
  echo "# 基线臂 = state/iss325_s8_control_v76mz_arms.sh (ISS-325 同日同代码 · 10 个 R_SEL_* @ 左上 · 不钉 TP)"
  echo "# 唯一变量 = PCB_PART_POS 的 10 个 R_SEL_* 坐标 (左上 → 右上 §3 方案 A 那组)"
  echo "# 坐标帧 = B160x100 (★ISS-274 帧声明★ · 160.00×100.00mm / 8 铜层 / 186 封装)"
  echo "PCB_LAYERS=8"
  echo "PCB_ABUDGET_MULT=6"
  echo "PCB_HALO_MARGIN=0.0625"
  echo "PCB_BOARD_W=160"
  echo "PCB_BOARD_H=100"
  echo "PCB_AREA_BOT=5,58,70,97"
  echo "PCB_AREA_TOP=78,5,120,36"
  echo "PCB_AREA_RES=78,38,157,97"
  echo "PCB_PIN_CONN_CAM=1"
  echo "PCB_SKIP_PAD_CELLS=1"
  echo "PCB_PAIR_ESCAPE_EXEMPT=1"
  echo "PCB_PAIR_EXEMPT_R=0.0"
  echo "PCB_GND_FIRST=1"
  echo "PCB_VIA_HALO_MARGIN=0.0"
  echo "PCB_CONN_GND_ESCAPE=CONN_CAM:4.0"
  echo "PCB_KEEPOUT=24.0,56.1,35.6,59.6"
  echo "PCB_PART_POS=$PP"
  echo "PCB_PAIR_BEFORE_PWR=1"
  echo "PCB_PRIORITY_NETS=FSIN_OUT;LIGHT_5V;LIGHT_3V3;I2C_A_SCL;I2C_A_SDA;I2C_B_SCL;I2C_B_SDA;LED_G;LED_G_D;KEY_CAM;JTAG_TDI;SPI_SCLK_BOOT;SPI_MOSI_BOOT;SPI_MISO_BOOT;UART_RX;USB_CC2;BAT_DET;ID_DETECT_0;ID_DETECT_1;JTAG_TDO;JTAG_TMS;UART_TX;LED_B_D"
  echo "PCB_W_MIN=0.15"
  echo "PCB_VIA_HALO_CENTER=1"
  echo "PCB_MERGE_FIX=1"
  echo "PCB_ESC_ROWNORM=2"
  echo "PCB_ROUTE_RESERVE=<state/.lastgood/v76mg_reserve.txt 整串·md5 1950683f8f2981eb6e1141c3559c02a6>"
  echo "PCB_PRIO_SPAN_SORT=1"
  echo "PCB_MEANDER_EDGE=1"
  echo "PCB_GRID=0.125"
  echo "PCB_OUT=$OUT"
  echo "PCB_REPORT=$REPORT"
  echo "# ★链级: PCB_CHAIN_LOOSE_MARGIN=0.03125 (★与 v76mz / ISS-325 两臂同配方★)"
} > "$EVDIR/10_arm_env_snapshot_RU.txt"

# ★★【★唯一变量 = PCB_PART_POS 的 10 个 R_SEL_* 坐标★】★★
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
    timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
    > "$LOG" 2>&1
echo "EXIT=$?" >> "$LOG"
echo "  [${TAG}] 路由器 EXIT 记录完毕"
[ -f "$OUT" ] || { echo "❌ 没出板 ⇒ 收工"; exit 2; }

echo "── 板规则 min track width → 0.15 ──"
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

echo "── fresh DRC (裸板) ──"
bash state/kicad.sh pcb drc --output "$DRC" --severity-error --severity-warning --format json "$OUT" >/dev/null 2>&1
python3 - "$DRC" <<'PY'
import json, sys, collections
d = json.load(open(sys.argv[1], encoding="utf-8"))
v = d.get("violations") or []
print("  裸板: 违规=%d · unc=%d · %s" % (len(v), len(d.get("unconnected_items") or []),
      dict(collections.Counter(x.get("type") for x in v).most_common(6))))
PY

echo "── 套链 (★loose 步 margin 0.03125 ⇒ ★与 v76mz / ISS-325 两臂同配方★) ──"
PCB_CHAIN_LOOSE_MARGIN=0.03125 bash state/replay_patch_chain.sh "$OUT" "$TAG"
echo "  链 rc=$?"
FINAL=/tmp/chain_${TAG}/final_chain.kicad_pcb
if [ -f "$FINAL" ]; then
  echo "── ★★边际净距修复 (★零风险·把 DRC 违规清零★) ──"
  bash state/clrfix_iter.sh "$FINAL" "${FINAL}.drc.json" --max 5 --tag "$TAG"
fi
echo "=== ISS-328 S8 右上臂 全流程结束 $(date '+%F %T') ==="
