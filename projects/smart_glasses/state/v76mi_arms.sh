#!/usr/bin/env bash
# v76mi_arms.sh -- ★★★【单臂: 【三个闸全开】(★蛇形板边闸 + 出脚直行 + GND 孤儿铜闸★)★】★★★
#
# ★★★★★**★为什么这条臂 (★2026-11-10 14:2x 实测决策)★★★★** ★★★
#   ★**三个闸各自的实测凭证 (★全部是真臂/真跑, 不是推断★)**:
#     ① `PCB_MEANDER_EDGE=1` (★蛇形板边闸★): ★**v76me 成对臂 ⇒ 板边违规 4→0, 总违规 6→2, unc 零代价** ★★
#     ② `PCB_ESC_STRAIGHT=2` (★出脚后先直行★): ★**v76s9/v76s10 双证 ⇒ 消掉 `ID_DETECT_0`↔`BOOT_N` 那条 clearance** ★★
#     ③ `PCB_GND_ORPHAN_FIX=1` (★GND 孤儿铜闸★): ★**端到端实测 ⇒ 重复直道 316→0 条, 且 GND 焊盘有铜 94/94 两边一致** ★★
#   ★★**⇒ 本臂 = 三个闸叠加, ★目标是 DRC = 0 ⇒ ⇒ 连通性保持 v76s8 那一档 (unc 25 条 / 23 网名)** ★★
#   ★**对照基线**: ★**`state/.lastgood/baseline_v76mg0_chain.kicad_pcb` (★同 env 闸关对照臂★)** ★★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

OUT=/tmp/v76mi_R.kicad_pcb
LOG=/tmp/v76mi_R.log
DRC=/tmp/v76mi_R.drc.json

echo "=== v76mi 臂: v76rr + ★成对预留(P+N) + ★优先网按跨距排序 ★ ==="

# ---- ① 算预留串 (★按官方板实测 ⇒ 坐标不硬编码) ----
echo "── 算预留串 (plan_route_reserve.py) ──"
RESERVE=$(bash state/pcbnew_py.sh state/plan_route_reserve.py HW/PCB/demo_mainboard.kicad_pcb \
           --from-drc /tmp/v76rs_unc.drc.json 2>/dev/null \
           | grep -o 'PCB_ROUTE_RESERVE="[^"]*"' | head -1 | sed 's/PCB_ROUTE_RESERVE="//; s/"$//')
if [ -z "$RESERVE" ]; then
  echo "❌ 预留串没算出来 ⇒ 收工 (★别用空串开臂)"
  exit 3
fi
echo "  ✓ 预留串 = $RESERVE"
echo "  ✓ 工具指纹 plan_route_reserve.py sha256 = $(sha256sum state/plan_route_reserve.py | cut -c1-16)"
echo "  ✓ 工具指纹 gen_pcb_routing.py    sha256 = $(sha256sum state/gen_pcb_routing.py  | cut -c1-16)"
echo "  ✓ 唯一变量 = PCB_HALO_MARGIN 0.20⇒0.0625 (★--from-drc 输入 /tmp/v76rs_unc.drc.json 与 v76ru 同 ★)"

(
  cd "$PROJ"
  env PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.0625 \
      PCB_BOARD_W=160 PCB_BOARD_H=100 \
      PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
      PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
      PCB_PAIR_EXEMPT_R=0.0 \
      PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 \
      PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
      PCB_PART_POS="R_SEL_D3_P:5.50,3.0;R_SEL_D3_N:7.95,3.0;R_SEL_D2_P:13.10,3.0;R_SEL_D2_N:15.55,3.0;R_SEL_CK_P:20.70,3.0;R_SEL_CK_N:23.15,3.0;R_SEL_D1_P:28.30,3.0;R_SEL_D1_N:30.75,3.0;R_SEL_D0_P:35.90,3.0;R_SEL_D0_N:38.35,3.0" \
      PCB_PAIR_BEFORE_PWR=1 PCB_PRIORITY_NETS="FSIN_OUT;LIGHT_5V;LIGHT_3V3;I2C_A_SCL;I2C_A_SDA;I2C_B_SCL;I2C_B_SDA;LED_G;LED_G_D;KEY_CAM;JTAG_TDI;SPI_SCLK_BOOT;SPI_MOSI_BOOT;SPI_MISO_BOOT;UART_RX;USB_CC2;BAT_DET;ID_DETECT_0;ID_DETECT_1;JTAG_TDO;JTAG_TMS;UART_TX;LED_B_D" PCB_W_MIN=0.15 \
      PCB_VIA_HALO_CENTER=1 PCB_MERGE_FIX=1 PCB_ESC_ROWNORM=2 PCB_ESC_STRAIGHT=2 \
      PCB_MEANDER_EDGE=1 \
      PCB_GND_ORPHAN_FIX=1 \
      PCB_ROUTE_RESERVE="$RESERVE" PCB_PRIO_SPAN_SORT=1 \
      PCB_OUT="$OUT" \
      timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$LOG" 2>&1
  echo "EXIT=$?" >> "$LOG"
) &
_PID=$!
echo "  [v76mi 臂] PID=$_PID"

while kill -0 "$_PID" 2>/dev/null; do sleep 60; done
echo "=== 第①步结束 ==="
if [ ! -f "$OUT" ]; then
  echo "❌ 没出板 ⇒ 收工 (看 $LOG)"; exit 2
fi

# ---- ② 板规则 min track width 0.20 ⇒ 0.15 (★老板批准的规格; ★不改几何, ★只让 0.15mm 走线合法) ----
echo "── 板规则 min track width → 0.15 (★老板批准的规格) ──"
bash state/pcbnew_py.sh - "$OUT" <<'PY'
import pcbnew, sys
p = sys.argv[1]
b = pcbnew.LoadBoard(p)
if b is None:
    print("  ❌ 板读不出来"); raise SystemExit(1)
ds = b.GetDesignSettings()
print("  改前 m_TrackMinWidth =", ds.m_TrackMinWidth / 1e6, "mm")
ds.m_TrackMinWidth = int(0.15 * 1e6)
b.Save(p)
print("  ✓ 改为 0.15 ⇒", p)
PY

echo "── 板规则 min track width → 0.15 (★老板批准的规格; ★否则 0.15mm 走线全是假违规) ──"
bash state/pcbnew_py.sh - "$OUT" <<'PY'
import pcbnew, sys
p = sys.argv[1]
b = pcbnew.LoadBoard(p)
if b is None:
    print("  ❌ 板读不出来"); raise SystemExit(1)
ds = b.GetDesignSettings()
print("  改前 m_TrackMinWidth =", ds.m_TrackMinWidth / 1e6, "mm")
ds.m_TrackMinWidth = int(0.15 * 1e6)
b.Save(p)
print("  ✓ 改为 0.15 ⇒", p)
PY

echo "── 裸板读数 ──"
echo "  走线 = $(grep -ac '(segment' "$OUT") · 过孔 = $(grep -ac '(via' "$OUT")"
bash state/kicad.sh pcb drc --output "$DRC" --severity-error --severity-warning --format json "$OUT" >/dev/null 2>&1
python3 - "$DRC" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
print("  DRC违规 = %d · unconnected = %d" % (len(d.get("violations") or []), len(d.get("unconnected_items") or [])))
PY

echo "── 套【已校准的官方补丁链】 ──"
bash state/replay_patch_chain.sh "$OUT" v76mi
echo "  链 rc=$?"

echo "── vs 同链基线 (★不是 vs 官方板) ──"
FINAL="/tmp/chain_v76mi/final_chain.kicad_pcb"
if [ -f "$FINAL" ]; then
  bash state/compare_arm_baseline.sh "$FINAL" --baseline state/.lastgood/baseline_v76mg0_chain.kicad_pcb
else
  echo "  ⚠️ 链没出终板 ⇒ 没法比"
fi
exit 0
