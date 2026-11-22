#!/usr/bin/env bash
# iss328 probe · 【排版阶段】落位对照 (零布线 · 秒级)
#   A = 基线臂 (v76mz env 逐字 · R_SEL_* 钉左上 x5.50..38.35 y3.00)
#   B = 右上臂 (同 env · 只把 10 条 R_SEL_* 改到 方案 A 右上组 x78.90..122.30 y5.50)
#   C = 右上臂 + 钉 10 条 TP_DSI_* (方案 A 全 20 串)
#   产出: A/B/C 三块【裸板】(PCB_SKIP_ROUTE=1) + 全板封装落位清单 + 三组 diff
# ★写盘只落 tmp/iss328/ (PCB_OUT / PCB_REPORT / .layout_landed.json 都指到沙盒)
# ★真板 HW/PCB/demo_mainboard.kicad_pcb 一个字节都不碰
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1
SBX=$PROJ/tmp/iss328
LOGD=$PROJ/logs/iss328
RESERVE_FILE="$PROJ/state/.lastgood/v76mg_reserve.txt"
[ -f "$RESERVE_FILE" ] || { echo "❌ 没有 v76mg 的预留串 ⇒ 收工"; exit 3; }
RESERVE=$(cat "$RESERVE_FILE")

# ★基线臂 PCB_PART_POS (照抄 state/v76mz_arms.sh L44 · 10 条 R_SEL_* 钉左上)
PP_BASE="R_SEL_D3_P:5.50,3.0;R_SEL_D3_N:7.95,3.0;R_SEL_D2_P:13.10,3.0;R_SEL_D2_N:15.55,3.0;R_SEL_CK_P:20.70,3.0;R_SEL_CK_N:23.15,3.0;R_SEL_D1_P:28.30,3.0;R_SEL_D1_N:30.75,3.0;R_SEL_D0_P:35.90,3.0;R_SEL_D0_N:38.35,3.0"
# ★右上臂 PCB_PART_POS (★唯一变量 = 10 条 R_SEL_* 坐标换成 方案 A 右上组★)
PP_RU="R_SEL_D0_N:78.90,5.50;R_SEL_D0_P:83.70,5.50;R_SEL_D1_N:88.50,5.50;R_SEL_D1_P:93.30,5.50;R_SEL_CK_N:98.10,5.50;R_SEL_CK_P:102.90,5.50;R_SEL_D2_N:107.70,5.50;R_SEL_D2_P:112.50,5.50;R_SEL_D3_N:117.30,5.50;R_SEL_D3_P:122.30,5.50"
# ★右上臂 + 10 条 TP_DSI_* (方案 A 全 20 串 · 逐字抄 LAYOUT_FIX_SPEC §3 方案 A)
PP_RUTP="R_SEL_D0_N:78.90,5.50;R_SEL_D0_P:83.70,5.50;R_SEL_D1_N:88.50,5.50;R_SEL_D1_P:93.30,5.50;R_SEL_CK_N:98.10,5.50;R_SEL_CK_P:102.90,5.50;R_SEL_D2_N:107.70,5.50;R_SEL_D2_P:112.50,5.50;R_SEL_D3_N:117.30,5.50;R_SEL_D3_P:122.30,5.50;TP_DSI_D0_N:75.70,5.50;TP_DSI_D0_P:87.50,79.70;TP_DSI_D1_N:91.90,79.70;TP_DSI_D1_P:96.30,79.70;TP_DSI_CK_N:78.70,79.70;TP_DSI_CK_P:83.10,79.70;TP_DSI_D2_N:100.70,79.70;TP_DSI_D2_P:105.10,79.70;TP_DSI_D3_N:120.50,5.50;TP_DSI_D3_P:75.70,9.50"

run_arm () { # $1=tag $2=partpos
  local tag="$1" pp="$2"
  local out="$SBX/bare_${tag}.kicad_pcb"
  local log="$SBX/bare_${tag}.gen.log"
  local rep="$SBX/bare_${tag}.report.txt"
  if [ -e "$out" ]; then
    echo "  [${tag}] ★已有产物 ⇒ 不覆盖 (铁律) ⇒ 跳过"
    return 0
  fi
  echo "── 生成裸板 ${tag} (PCB_SKIP_ROUTE=1 · 只排版不布线) $(date '+%F %T') ──"
  env PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.0625 \
      PCB_BOARD_W=160 PCB_BOARD_H=100 \
      PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
      PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
      PCB_PAIR_EXEMPT_R=0.0 \
      PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 \
      PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
      PCB_PART_POS="$pp" \
      PCB_PAIR_BEFORE_PWR=1 PCB_PRIORITY_NETS="FSIN_OUT;LIGHT_5V;LIGHT_3V3;I2C_A_SCL;I2C_A_SDA;I2C_B_SCL;I2C_B_SDA;LED_G;LED_G_D;KEY_CAM;JTAG_TDI;SPI_SCLK_BOOT;SPI_MOSI_BOOT;SPI_MISO_BOOT;UART_RX;USB_CC2;BAT_DET;ID_DETECT_0;ID_DETECT_1;JTAG_TDO;JTAG_TMS;UART_TX;LED_B_D" PCB_W_MIN=0.15 \
      PCB_VIA_HALO_CENTER=1 PCB_MERGE_FIX=1 PCB_ESC_ROWNORM=2 \
      PCB_ROUTE_RESERVE="$RESERVE" PCB_PRIO_SPAN_SORT=1 \
      PCB_MEANDER_EDGE=1 \
      PCB_GRID=0.125 \
      PCB_SKIP_ROUTE=1 \
      PCB_OUT="$out" \
      PCB_REPORT="$rep" \
      timeout 1800 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$log" 2>&1
  local rc=$?
  echo "EXIT=$rc" >> "$log"
  echo "  [${tag}] 生成 rc=$rc · 板 $out"
  [ -f "$out" ] || return 2
  bash state/pcbnew_py.sh "$SBX/dump_fp_pos.py" "$out" > "$SBX/pos_${tag}.tsv" 2>&1
  md5sum "$out" > "$SBX/md5_${tag}.txt"
  grep -E "精确钉位|未匹配|最终没落板|排版" "$log" | head -12 | sed "s/^/    [${tag}] /"
  return 0
}

echo "=== ISS-328 排版阶段落位对照探针 (零布线) ==="
echo "  ✓ 工具指纹 gen_pcb_netlist_board.py sha256 = $(sha256sum state/gen_pcb_netlist_board.py | cut -c1-16)"
echo "  ✓ 预留串 md5 = $(md5sum "$RESERVE_FILE" | cut -d' ' -f1)"
run_arm base "$PP_BASE"
run_arm ru   "$PP_RU"
run_arm rutp "$PP_RUTP"

echo "── 落位清单与 md5 ──"
for t in base ru rutp; do
  echo "  $t: md5=$(cut -d' ' -f1 "$SBX/md5_${t}.txt" 2>/dev/null) · 封装数=$(grep -c '^[A-Za-z]' "$SBX/pos_${t}.tsv" 2>/dev/null) · 落位清单 $SBX/pos_${t}.tsv"
done

# ── diff 1: 右上臂 vs 基线臂 (★起链硬前置: 必须 ≠ 0★) ──
echo "── diff1: 右上臂 vs 基线臂 (全板封装落位) ──"
diff <(grep -v '^#' "$SBX/pos_base.tsv") <(grep -v '^#' "$SBX/pos_ru.tsv") > "$SBX/diff1_ru_vs_base.tsv"
D1=$(grep -c '^[<>]' "$SBX/diff1_ru_vs_base.tsv")
echo "  ★差异行数 = $D1"
[ "$D1" -ne 0 ] && echo "  ✅ 落位有差异 ⇒ 有对照可做 (允许起链)" || echo "  ❌ 落位完全相同 ⇒ 本单无对照可做 (不许起链)"

# ── diff 2: 右上臂(钉TP) vs 右上臂(不钉TP) ⇒ TP 是不是 no-op ──
echo "── diff2: 右上臂+钉10条TP vs 右上臂不钉TP (全板封装落位) ──"
diff <(grep -v '^#' "$SBX/pos_ru.tsv") <(grep -v '^#' "$SBX/pos_rutp.tsv") > "$SBX/diff2_tp_vs_notp.tsv"
D2=$(grep -c '^[<>]' "$SBX/diff2_tp_vs_notp.tsv")
echo "  ★差异行数 = $D2"
grep '^[<>]' "$SBX/diff2_tp_vs_notp.tsv" | head -60

# ── 落盘判定文件 ──
OUTF=$LOGD/06_tp_noop_placement_diff.txt
{
  echo "★★ISS-328 · ③-1 【TP_DSI_* 显式钉位 · 排版阶段是不是 no-op】实测★★"
  echo ""
  echo "  方法: 同一配方 (v76mz env 逐字 · 只改 10 条 R_SEL_* 到方案 A 右上组) · 两次生成"
  echo "        一次【不钉 TP_DSI_*】· 一次【钉 10 条 TP_DSI_* (方案 A 全 20 串)】"
  echo "        ★用 PCB_SKIP_ROUTE=1 只出【排版】不布线 (生成器排版阶段 ~10 秒)"
  echo ""
  echo "  两次生成的板:"
  echo "    [不钉TP]  md5=$(cut -d' ' -f1 "$SBX/md5_ru.txt")   板 tmp/iss328/bare_ru.kicad_pcb"
  echo "    [钉 10TP] md5=$(cut -d' ' -f1 "$SBX/md5_rutp.txt") 板 tmp/iss328/bare_rutp.kicad_pcb"
  echo ""
  echo "  全板封装落位 diff (ref\tx\ty\trot 逐行比):"
  echo "    ★★差异行数 = $D2 ★★"
  echo ""
  echo "  差异明细 (前 60 行, 完整见 tmp/iss328/diff2_tp_vs_notp.tsv):"
  grep '^[<>]' "$SBX/diff2_tp_vs_notp.tsv" | head -60 | sed 's/^/    /'
  echo ""
  if [ "$D2" -eq 0 ]; then
    echo "  ⇒ ★★[实测] 结论: 【钉 vs 不钉 10 条 TP_DSI_*】在【排版阶段】逐个完全相同 (差异行数 = 0)"
    echo "        ⇒ ⇒ 显式钉 TP_DSI_* 是 no-op ⇒ ★**main 下一轮可把 P-1 改判成「删回 10 条」**"
  else
    echo "  ⇒ ★★[实测] 结论: 【钉 vs 不钉 10 条 TP_DSI_*】在【排版阶段】落位【不一样】 (差异行数 = $D2)"
    echo "        ⇒ ⇒ 显式钉 TP_DSI_* 【不是】 no-op ⇒ ★**P-1 的 20 条串不能删回 10 条**"
  fi
  echo ""
  echo "  ── 附: 起链硬前置 (右上臂 vs 基线臂 全板封装落位 diff) = $D1 (必须 ≠ 0) ──"
  echo "  ── 附: 本板帧 = B160x100 (160.00×100.00mm / 8 铜层 / 1.60mm) · 帧声明照 ISS-274 ──"
} > "$OUTF"
echo ""
echo "=== 判定落盘: $OUTF ==="
cat "$OUTF"
echo "=== 探针结束 $(date '+%F %T') ==="
