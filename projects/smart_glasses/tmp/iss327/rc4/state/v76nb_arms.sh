#!/usr/bin/env bash
# v76nb_arms.sh -- ★★★【单变量臂: v76mg1 的 env + 只换【预留串】(★按当前最好板的 23 条 unc 重算★)★★★ ★
#
# ★★★★★**★为什么这一臂 (★2026-11-11 07:4x 实测决策)★★★★** ★★★
#   ★**当前最好板**: ★**unc 23 条 / 21 网 + DRC 0** (★`v76mg1` → 链 loose 步 margin **0.03125** → 迭代收窄★)
#     ⇒ ★**配方**: ★`v76mg1` 路由 → 官方校准链 → ★**loose 步 margin 0.03125**★ → ★**`clrfix_iter` 收窄** ★★
#   ★★★**★为什么还值得开臂 (★而不是继续调链级参数★)★★★ ★★★
#     · ★**margin 杠杆已饱和 (★实测★)**: ★**0.015625 的产物与 0.03125 逐字节相同** ⇒ ⇒ **链级 margin 到头了** ★★
#     · ★**链级 A\* 预算 20× ⇒ 一个字节都不变** ⇒ ⇒ **链级预算也到头了** ★★
#     ⇒ ★★**⇒ 只剩【路由器本体】还能改 ⇒ ⇒ 本臂换【路由器网格】** ★★
#   ★**为什么选 0.125 (★有实测依据★)**: ★**`v76s4` (PCB_GRID=0.125) 实测解开了 `DSI_D0_D2_P/N` · `DSI_D0_D3_P/N` 两对** ★★
#     ⇒ ★★**⇒ 细网格对【差分腿出脚】有效 (★那正是当前 23 条里 10 条差分腿的病根★) ⇒ ⇒ 值得再试** ★★★
#   ★★**⇒ ⇒ 预期: ★【路由器层面】多救回几条差分腿 ⇒ ⇒ 链级再叠 margin 0.03125 + 收窄 ⇒ ⇒ **unc < 23** ★★ ★★
#
# ★**对照臂 = `v76mg1` (已交卷) ⇒ 不必再花一条臂做对照** ★
# ★★**为什么这一臂 (★2026-11-11 08:0x 实测决策★)**: ★★**预留串是【占坑表】⇒ 它必须对着【现在真正打不出来的网】★★
#   ★★**实测 diff (★旧 57 框 → 新 39 框★)**: ★新增 `CSI_D0_D0_N+CSI_D0_D0_P`/`CSI_MCLK_SRC`/`DSI_D0_D0_N+...+KEY_VOL_M`/
#   ★`DSI_D0_D3_N`/`GND`/`I2C_A_SCL`/`I2C_B_SCL`/`ID_DETECT_1`/`KEY_VOL_M`/`SPI_CSn_BOOT` (★正是现在的零铜/断网★)
#   ⇒ ★而【现在已通的 28 项】不再占坑 (★它们的坑位让出来给真正需要的网★) ⇒ ⇒ ★**占坑表终于对准靶心** ★★
# ★**预留串 = 复用 `state/.lastgood/v76mg_reserve.txt` (★必须逐字节一致 ⇒ 否则就不是单变量★)** ★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

OUT=/tmp/v76nb_R.kicad_pcb
LOG=/tmp/v76nb_R.log
DRC=/tmp/v76nb_R.drc.json
RESERVE_FILE="$PROJ/state/.lastgood/v76nb_reserve.txt"

if [ -e "$OUT" ] || [ -e "$LOG" ]; then
  echo "  [v76nb] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"
  exit 0
fi
[ -f "$RESERVE_FILE" ] || { echo "❌ 没有 v76mg 的预留串 ⇒ 收工"; exit 3; }
RESERVE=$(cat "$RESERVE_FILE")
echo "=== v76nb 单变量臂: env = v76mg1 逐位相同 · 唯一变量 = 预留串(按当前最好板重算) ==="
echo "  ✓ 预留串 (★复用 v76mg 的★) = ${RESERVE:0:110}..."
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
    PCB_MEANDER_EDGE=1 \
    PCB_OUT="$OUT" \
    timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
    > "$LOG" 2>&1
echo "EXIT=$?" >> "$LOG"
echo "  [v76nb] 路由器 EXIT 记录完毕"
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

echo "── 套链 (★loose 步 margin 0.03125 ⇒ ★与当前最好板同配方★) ──"
PCB_CHAIN_LOOSE_MARGIN=0.03125 bash state/replay_patch_chain.sh "$OUT" v76nb
echo "  链 rc=$?"
FINAL=/tmp/chain_v76nb/final_chain.kicad_pcb
if [ -f "$FINAL" ]; then
  echo "── vs 对照臂 v76mg1 (★同 env·唯一变量 = GRID★) ──"
  bash state/compare_arm_baseline.sh "$FINAL" --baseline /tmp/chain_v76mg1/final_chain.kicad_pcb
  echo "  ★闸 rc=$?"
  echo "── ★★边际净距修复 (★零风险·把 DRC 违规清零★) ──"
  bash state/clrfix_iter.sh "$FINAL" "${FINAL}.drc.json" --max 5 --tag v76nb
fi
echo "=== v76nb 全流程结束 $(date '+%F %T') ==="
