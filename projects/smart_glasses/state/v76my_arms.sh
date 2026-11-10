#!/usr/bin/env bash
# v76my_arms.sh -- ★★★【★单变量臂: v76mx1 的 env + 只加【窄版直行】(★名单 = 10 条差分 N 腿★)★★★ ★
#
# ★★★★★**★为什么这一臂 (★2026-11-11 04:4x 实测决策)★★★★** ★★★
#   ★**证据 ① (★路由阶段失败明细★ `state/_fail_detail_v76mx1_R.json`★)**: ★**25 个失败网里 10 个全是【差分 N 腿】★★
#     ⇒ `CSI_D0_CK_N`@CONN_CAM.17 · `CSI_D0_D0_N_SRC`@C_AC_CSI_D0_D0_N.1 · `CSI_D0_D0_N`@CONN_CAM.14
#     ⇒ `CSI_D0_D2_N`@C_AC_CSI_D0_D2_N.2 · `CSI_D0_D3_N`@CONN_CAM.2 · `DSI_D0_CK_N_SRC`@R_SEL_CK_N.1
#     ⇒ `DSI_D0_D1_N_SRC`@J_SOM_P3.63 · `DSI_D0_D1_N`@CONN_LIGHT.2 · `DSI_D0_D3_N`@CONN_LIGHT.18 · `DSI_D0_D0_N`@CONN_LIGHT.8
#     ⇒ ★★**⇒ 差分 N 腿 = 路由器阶段最大失败类 = 【零铜】的来源 = unc 的主战场** ★★
#   ★**证据 ② (★机理★)**: ★**`ESC_STRAIGHT` 正是治它的机制** ★★
#     (★实测: P 腿的 45° 首步与 N 腿直道垂距只有 0.255mm, 需要 0.425mm ⇒ N 腿 `L=0.00`★ ⇒ ★**强制直行 ⇒ 两条平行 ⇒ 不撞**★)
#   ★**证据 ③ (★为什么必须"窄版"★)**: ★**全局 `PCB_ESC_STRAIGHT=2` 实测把 unc 从 25 抬到 35 (★伤太大★)** ★★
#     ⇒ ★★**⇒ ⇒ "按网限定" (★`PCB_ESC_STRAIGHT_NETS`★) ⇒ ⇒ 代价收缩到那 10 条腿** ★★★
#     ⇒ ★★**★这与 `v76mx1` (★按网限定的让路闸 ⇒ unc 28 · DRC 0 · 零副作用★) 是同一条已验证的路** ★★★
#
# ★**对照臂 = `v76mx1` (★已交卷·终板在 /tmp/chain_v76mx1/final_chain.kicad_pcb★) ⇒ 不必再花一条臂做对照** ★
# ★**预留串 = 复用 `state/.lastgood/v76mx_reserve.txt` (★必须逐字节一致 ⇒ 否则就不是单变量★)** ★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

OUT=/tmp/v76my_R.kicad_pcb
LOG=/tmp/v76my_R.log
DRC=/tmp/v76my_R.drc.json
RESERVE_FILE="$PROJ/state/.lastgood/v76mx_reserve.txt"

# ★★【★唯一变量 = 窄版直行: 只对这 10 条差分 N 腿生效★】★★
# ★★**为什么只列 N 腿不列 P 腿**: ★**P 腿现在能布出来 ⇒ 动它有【把好网弄坏】的风险; ★且要等读数看【差分Δ超差】会不会涨★ ★★
STRAIGHT_NETS="CSI_D0_CK_N,CSI_D0_D0_N_SRC,CSI_D0_D0_N,CSI_D0_D2_N,CSI_D0_D3_N,DSI_D0_CK_N_SRC,DSI_D0_D1_N_SRC,DSI_D0_D1_N,DSI_D0_D3_N,DSI_D0_D0_N"

if [ -e "$OUT" ] || [ -e "$LOG" ]; then
  echo "  [v76my] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"
  exit 0
fi
if [ ! -f "$RESERVE_FILE" ]; then
  echo "❌ 没有 v76mx 的预留串 ⇒ 收工 (★单变量前提不成立★)"
  exit 3
fi
RESERVE=$(cat "$RESERVE_FILE")
echo "=== v76my 单变量臂: env = v76mx1 逐位相同 · 唯一变量 = 窄版直行 (10 条差分 N 腿) ==="
echo "  ✓ 预留串 (★复用 v76mx 的★) = ${RESERVE:0:110}..."
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
    PCB_GND_ORPHAN_FIX=1 \
    PCB_MEANDER_EDGE=1 \
    PCB_ESC_CLR_FIX=1 \
    PCB_YIELD_STRAIGHT=1 "PCB_YIELD_VICTIMS=BOOT_N,USB_CC1,CARRIER_BOARD_EN" \
    ★★★【★唯一变量★】PCB_ESC_STRAIGHT=2 "PCB_ESC_STRAIGHT_NETS=$STRAIGHT_NETS" \
    PCB_OUT="$OUT" \
    timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
    > "$LOG" 2>&1
echo "EXIT=$?" >> "$LOG"
echo "  [v76my] 路由器 EXIT 记录完毕"

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
bash state/replay_patch_chain.sh "$OUT" v76my
echo "  链 rc=$?"
FINAL=/tmp/chain_v76my/final_chain.kicad_pcb
if [ -f "$FINAL" ]; then
  echo "── vs 对照臂 v76mx1 (★同 env·唯一变量 = 窄版直行★) ──"
  bash state/compare_arm_baseline.sh "$FINAL" --baseline /tmp/chain_v76mx1/final_chain.kicad_pcb
  echo "  ★闸 rc=$?"
  echo "── 权威读数 (fresh DRC) ──"
  bash state/arm_fresh_readings.sh "$FINAL" --baseline /tmp/chain_v76mx1/final_chain.kicad_pcb
  echo "── ★★再上【边际净距修复】(★零风险·把 DRC 违规清零★) ──"
  bash state/clrfix_iter.sh "$FINAL" "${FINAL}.drc.json" --max 4 --tag v76my
fi
echo "=== v76my 全流程结束 $(date '+%F %T') ==="
