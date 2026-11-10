#!/usr/bin/env bash
# v76mw_arms.sh -- ★★★【单变量臂: v76mj1 的 env + 只加 PCB_ESC_ROWNORM2=1】★★★ ★
#
# ★★★★★**★为什么这一臂 (★2026-11-11 00:5x 实测决策)★★★★** ★★★
#   ★**现状 (★全部 fresh DRC 实测★)** ★★:
#     · `v76mg1` (v76s8 + MEANDER_EDGE)                    ⇒ ★**DRC 6 · unc 25 条 / 23 网** ★★
#     · `v76mj1` (v76mg1 + GND_ORPHAN_FIX)                  ⇒ ★**DRC 1 · unc 28 条 / 23 网** ★★
#     · `v76ml`  (v76mj1 + ESC_CLR_FIX)                     ⇒ ★**DRC 0 · unc 29 条 / 24 网** ★★
#     · `v76mv1` (v76ml + YIELD_STRAIGHT)                   ⇒ ★**DRC 6 · unc 32 条 / 24 网** ⇒ REJECT
#   ★★★**★`v76mj1` 那唯一一条违规 = clearance 0.1813mm = `ID_DETECT_0`↔`BOOT_N`★★** ★★
#   ★**而 `state/gen_pcb_routing.py` L335-342 的 `PCB_ESC_ROWNORM2` 就是为这条违规写的★**
#     (★源码注释逐字点名: "ID_DETECT_0 / BOOT_N (J_SOM_P1 同排 y=11.040)" + "净距 0.1813 < 0.2000"★)
#   ★★★**★⇒ 本臂 = 【唯一变量 = ROWNORM2】⇒ 若它的作用是真的 ⇒ 终板应是 unc ≤28 且 DRC 0★★** ★★★
#   ★**⇒ 这将是【全项目第一块 unc ≤28 且 DRC=0 的板】⇒ 之前最好的 DRC=0 板是 v76ml 的 unc 29/24** ★★
#
# ★**为什么不用成对臂**: ★`v76mj1` 已经跑完并归档 ⇒ 它就是本臂的【同 env 对照】★
#   ⇒ ★本臂只需与 `/tmp/chain_v76mj1/final_chain.kicad_pcb` 比 ⇒ ★不必再花一条臂做对照★
#
# ★**为什么复用 v76mj 的预留串 (★不重算★)**: ★**预留串是 env 的一部分 ⇒ 必须逐字节相同⇒ 否则就不是单变量★**
#   ⇒ ★直接读 `state/.lastgood/v76mj_reserve.txt` ★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

OUT=/tmp/v76mw_R.kicad_pcb
LOG=/tmp/v76mw_R.log
DRC=/tmp/v76mw_R.drc.json
RESERVE_FILE="$PROJ/state/.lastgood/v76mj_reserve.txt"

if [ -e "$OUT" ] || [ -e "$LOG" ]; then
  echo "  [v76mw] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"
  exit 0
fi
if [ ! -f "$RESERVE_FILE" ]; then
  echo "❌ 没有 v76mj 的预留串 ⇒ 收工 (★单变量前提不成立★)"
  exit 3
fi
RESERVE=$(cat "$RESERVE_FILE")
echo "=== v76mw 单变量臂: env = v76mj1 逐位相同 · 唯一变量 = PCB_ESC_ROWNORM2=1 ==="
echo "  ✓ 预留串 (★复用 v76mj 的★) = ${RESERVE:0:120}..."
echo "  ✓ 工具指纹 gen_pcb_routing.py sha256 = $(sha256sum state/gen_pcb_routing.py | cut -c1-16)"

env PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.0625 \
    PCB_BOARD_W=160 PCB_BOARD_H=100 \
    PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
    PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
    PCB_PAIR_EXEMPT_R=0.0 \
    PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 \
    PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
    PCB_PART_POS="R_SEL_D3_P:5.50,3.0;R_SEL_D3_N:7.95,3.0;R_SEL_D2_P:13.10,3.0;R_SEL_D2_N:15.55,3.0;R_SEL_CK_P:20.70,3.0;R_SEL_CK_N:23.15,3.0;R_SEL_D1_P:28.30,3.0;R_SEL_D1_N:30.75,3.0;R_SEL_D0_P:35.90,3.0;R_SEL_D0_N:38.35,3.0" \
    PCB_PAIR_BEFORE_PWR=1 PCB_PRIORITY_NETS="FSIN_OUT;LIGHT_5V;LIGHT_3V3;I2C_A_SCL;I2C_A_SDA;I2C_B_SCL;I2C_B_SDA;LED_G;LED_G_D;KEY_CAM;JTAG_TDI;SPI_SCLK_BOOT;SPI_MOSI_BOOT;SPI_MISO_BOOT;UART_RX;USB_CC2;BAT_DET;ID_DETECT_0;ID_DETECT_1;JTAG_TDO;JTAG_TMS;UART_TX;LED_B_D" PCB_W_MIN=0.15 \
    PCB_VIA_HALO_CENTER=1 PCB_MERGE_FIX=1 PCB_ESC_ROWNORM=2 \
    PCB_ROUTE_RESERVE="$RESERVE" PCB_PRIO_SPAN_SORT=1 \
    PCB_GND_ORPHAN_FIX=1 PCB_MEANDER_EDGE=1 \
    PCB_ESC_ROWNORM2=1 \
    PCB_OUT="$OUT" \
    timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
    > "$LOG" 2>&1
echo "EXIT=$?" >> "$LOG"
echo "  [v76mw] 路由器 EXIT 记录完毕"

if [ ! -f "$OUT" ]; then echo "❌ 没出板 ⇒ 收工"; exit 2; fi

echo "── 板规则 min track width → 0.15 (★保持与其它臂一致★) ──"
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

echo "── 套已校准的官方补丁链 ──"
bash state/replay_patch_chain.sh "$OUT" v76mw
echo "  链 rc=$?"
FINAL=/tmp/chain_v76mw/final_chain.kicad_pcb
if [ -f "$FINAL" ]; then
  echo "── vs 对照臂 v76mj1 (★同 env·唯一变量 = ROWNORM2★) ──"
  bash state/compare_arm_baseline.sh "$FINAL" --baseline /tmp/chain_v76mj1/final_chain.kicad_pcb
  echo "  ★闸 rc=$?"
  echo "── 权威读数 (fresh DRC) ──"
  bash state/arm_fresh_readings.sh "$FINAL" --baseline /tmp/chain_v76mj1/final_chain.kicad_pcb
fi
echo "=== v76mw 全流程结束 $(date '+%F %T') ==="
