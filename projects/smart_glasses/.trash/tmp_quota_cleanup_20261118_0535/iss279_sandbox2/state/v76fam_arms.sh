#!/usr/bin/env bash
# v76fam_arms.sh -- ★★★【优先网臂】: v76 基线 + ★把未连通的信号网提到【电源之前】布 ★★★
#
# ★★★**★为什么是这条 (★2026-11-09 21:4x 实测机制推导)★★★** ★★★
#   ★**实测①**: ★**挪 12 个焊盘 (0.3mm) ⇒ 走线段 13407→15867 (+2460) ⇒ ★★**但空间被供电网拿走了**
#       (★14 条供电网铜长合计 +266.2mm, ★而它们的失败脚数一个没动) ⇒ ★★**让出空间 ≠ 空间被用在需要的地方** ★★★
#   ★**实测②**: ★**路由器本来就排队: ①差分对 ②电源 ③MIPI ④其余网络(最后) ⇒ ★★**最后那批只能捡剩的通道**
#       (★★**源码原注释: [82% 的失败脚在这批]** ⇒ ★★**路由器早就知道这个问题**) ★★★
#   ★**实测③**: ★**挪焊盘这条路是【混沌景观上抽奖】⇒ 连续两轮 (0.15mm / v76m1) 都是净收益为负**
#       ⇒ ★★**⇒ 换一条【效果可预测】的路: ★把指定网【提前】布 ⇒ 它们先挑走廊** ★★★
#   ★**⇒ 本臂 = v76 基线 env 逐位相同 + 只多一个 PCB_PRIORITY_NETS** ⇒ ★★**干净 A/B** ★★
#   ★★★**★网从哪来 (★不是随手挑)★★★**: ★**官方板 45 条未连接里【属于"其余网络"批】的那些** ⇒
#       ★★**它们就是被排到最后、只能捡剩通道的那批** ⇒ ★★**优先给它们, 正是机制指向的动作** ★★★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

OUT=/tmp/v76fam_R.kicad_pcb
LOG=/tmp/v76fam_R.log
DRC=/tmp/v76fam_R.drc.json

echo "=== v76fam 臂: v76 基线 + ★优先网 (提到电源之前) ★ ==="
(
  cd "$PROJ"
  # ★★★**★唯一变量: PCB_PRIORITY_NETS 把这些网提到【电源之前】布 ⇒ ★★**它们先挑走廊** ★★★**
  env PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
      PCB_BOARD_W=160 PCB_BOARD_H=100 \
      PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
      PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
      PCB_PAIR_EXEMPT_R=0.0 \
      PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 \
      PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
      PCB_PART_POS="R_SEL_D3_P:5.50,3.0;R_SEL_D3_N:7.95,3.0;R_SEL_D2_P:13.10,3.0;R_SEL_D2_N:15.55,3.0;R_SEL_CK_P:20.70,3.0;R_SEL_CK_N:23.15,3.0;R_SEL_D1_P:28.30,3.0;R_SEL_D1_N:30.75,3.0;R_SEL_D0_P:35.90,3.0;R_SEL_D0_N:38.35,3.0" \
      PCB_PAIR_BEFORE_PWR=1 PCB_PRIORITY_NETS="FSIN_OUT;LIGHT_5V;LIGHT_3V3;I2C_A_SCL;I2C_A_SDA;I2C_B_SCL;I2C_B_SDA;LED_G;LED_G_D;KEY_CAM;JTAG_TDI;SPI_SCLK_BOOT;SPI_MOSI_BOOT;SPI_MISO_BOOT;UART_RX;USB_CC2;BAT_DET;ID_DETECT_0;ID_DETECT_1;JTAG_TDO;JTAG_TMS;UART_TX;LED_B_D" PCB_W_MIN=0.15 \
      PCB_VIA_HALO_CENTER=1 \
      PCB_OUT="$OUT" \
      timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$LOG" 2>&1
  echo "EXIT=$?" >> "$LOG"
) &
_PID=$!
echo "  [v76fam 臂] PID=$_PID"
while kill -0 "$_PID" 2>/dev/null; do sleep 60; done
echo "=== 第①步结束 ==="
[ -f "$OUT" ] || { echo "❌ 没出板 ⇒ 收工 (看 $LOG)"; exit 2; }
echo "── 板面读数 (★与 v76_R 同口径) ──"
echo "  走线 = $(grep -ac '(segment' "$OUT") · 过孔 = $(grep -ac '(via' "$OUT")"
bash state/kicad.sh pcb drc --output "$DRC" --severity-error --severity-warning --format json "$OUT" >/dev/null 2>&1
python3 - "$DRC" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
print("  DRC违规 = %d · unconnected = %d" % (len(d.get("violations") or []), len(d.get("unconnected_items") or [])))
PY
echo "── 套【已校准的官方补丁链】 ──"
bash state/replay_patch_chain.sh "$OUT" v76fam
FINAL="/tmp/chain_v76fam/final_chain.kicad_pcb"
if [ -f "$FINAL" ]; then
  echo "── ★vs 同链基线 (★不是 vs 官方板) ──"
  bash state/compare_arm_baseline.sh "$FINAL"
fi
exit 0
