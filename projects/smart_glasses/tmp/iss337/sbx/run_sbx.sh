#!/usr/bin/env bash
# ★ISS-337 沙盒: 用【真生成器 + 只改 env 配方】跑两条臂, 零写 HW/PCB
# SBX-A: 官方链口径 (GRID=0.125 + MERGE_FIX=0  ⇒ 不合并 ⇒ 段数应暴涨)
# SBX-B: 现役口径 (GRID=0.125 + MERGE_FIX=1  ⇒ 合并 ⇒ 段数应保持 ~3.3K)
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1
RESERVE=$(cat state/.lastgood/v76mg_reserve.txt)
PP="R_SEL_D3_P:5.50,3.0;R_SEL_D3_N:7.95,3.0;R_SEL_D2_P:13.10,3.0;R_SEL_D2_N:15.55,3.0;R_SEL_CK_P:20.70,3.0;R_SEL_CK_N:23.15,3.0;R_SEL_D1_P:28.30,3.0;R_SEL_D1_N:30.75,3.0;R_SEL_D0_P:35.90,3.0;R_SEL_D0_N:38.35,3.0"

run_arm() {  # $1=tag $2=merge_fix
  local TAG="$1" MF="$2"
  local OUT=/tmp/iss337_sbx_${TAG}.kicad_pcb
  local LOG=/tmp/iss337_sbx_${TAG}.log
  local REP=/tmp/iss337_sbx_${TAG}_REPORT.txt
  [ -e "$OUT" ] && { echo "[$TAG] 已有产物 ⇒ 跳过"; return 0; }
  echo "[$TAG] ★起跑 merge_fix=$MF grid=0.125 $(date '+%F %T')"
  env PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.0625 \
    PCB_BOARD_W=160 PCB_BOARD_H=100 \
    PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
    PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
    PCB_PAIR_EXEMPT_R=0.0 \
    PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 \
    PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
    PCB_PART_POS="$PP" \
    PCB_PAIR_BEFORE_PWR=1 PCB_PRIORITY_NETS="FSIN_OUT;LIGHT_5V;LIGHT_3V3;I2C_A_SCL;I2C_A_SDA;I2C_B_SCL;I2C_B_SDA;LED_G;LED_G_D;KEY_CAM;JTAG_TDI;SPI_SCLK_BOOT;SPI_MOSI_BOOT;SPI_MISO_BOOT;UART_RX;USB_CC2;BAT_DET;ID_DETECT_0;ID_DETECT_1;JTAG_TDO;JTAG_TMS;UART_TX;LED_B_D" PCB_W_MIN=0.15 \
    PCB_VIA_HALO_CENTER=1 PCB_MERGE_FIX="$MF" PCB_ESC_ROWNORM=2 \
    PCB_ROUTE_RESERVE="$RESERVE" PCB_PRIO_SPAN_SORT=1 \
    PCB_MEANDER_EDGE=1 \
    PCB_GRID=0.125 \
    PCB_OUT="$OUT" \
    PCB_REPORT="$REP" \
    timeout 3600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
    > "$LOG" 2>&1
  echo "[$TAG] ★EXIT=$? $(date '+%F %T')"
}

run_arm A 0
run_arm B 1
echo "★两条沙盒臂跑完"
