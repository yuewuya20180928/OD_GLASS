#!/usr/bin/env bash
# v58_arms.sh -- ★★**v58 概念: W_MIN=0.15 + R_SEL 部分挪位 (含配套 TP 一起钉)** (2026-11-06 10:2x)
#
# ★★★★**为什么是这个组合 (三个实测结论叠加)**:
#   ① ★**W_MIN=0.15 (6mil)**: v57 实测 ★**救回了官方板布不出的 2 对 CSI 差分对**
#      (`CSI_D0_D0_P/N` · `CSI_D0_D2_P/N` ⇒ 官方 v37_R 是 False/False)
#      ⇒ ★**根因纯几何**: 0.4mm pitch + 0.2mm 焊盘 ⇒ 0.2mm 线余量 **0.0000mm** (卡在临界)
#      ⇒ 0.15mm ⇒ 余量 0.025mm ⇒ 可行
#   ② ★**R_SEL 挪位**: v56 实测 ★**DSI_D0_D0_P_SRC 从"完全不通"变成"P 侧通" (L=19.45mm)**
#      ⇒ ★**证明 SRC 腿缩短有效** ⇒ ★**但 v56 整体 unc 58 反而更差** ⇒ ★**原因是配套 TP 没跟着挪**
#      ⇒ ★**v56 实测: TP_DSI_D1_P/D2_N/D2_P 被自动排版挤到 y=8.80** ⇒ ★**正好堵在 BTB 焊盘排上方 0.84mm**
#      ⇒ ★★**⇒ 本臂把 R_SEL 和它的 TP 一起钉位** ⇒ ★**不堵出脚走廊**
#   ③ ★**容量实测**: J_SOM_P3 右边缘 34.8 → J_SOM_P1 左边缘 49.2 ⇒ ★**只有 14.4mm**
#      ⇒ ★**0402 每 2.4mm 一个 ⇒ 最多放 6 个** ⇒ ★**10 个 R_SEL 放不下 ⇒ 只挪"最痛的 6 个"**
#      ⇒ ★**挪哪 6 个**: ★**按 SRC 腿长度排序取最长 (最受益)** ⇒ ★**D2_N/D3_N/D2_P/D1_N/D3_P/D0_N**
#      ⇒ ★**CK 对 + D0_P/D1_P 留在右上** (★它们 SRC 腿本来就不长)
#
# ★**本臂的两个变量 (★都是本轮实证过的)**:
#   A: `PCB_W_MIN=0.15` (★env 门控, 默认 0.20 ⇒ 既有臂逐位可复现)
#   B: `PCB_PART_POS` 钉 6 个 R_SEL + 6 个配套 TP (★不动网表/不动封装)
# ★**其余 env 与官方 v37_R 逐位相同**
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

OUT=/tmp/v58_R.kicad_pcb
LOG=/tmp/v58_R.log
if [ -e "$OUT" ] || [ -e "$LOG" ]; then
  echo "  [v58 臂 R] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"
  exit 0
fi

# ★★**钉位表 (★R_SEL 的 pad1 = SRC 侧 = 焊盘中心; TP 的 pad1 同理)**
#   ★**排布**: x = 35.6, 38.0, 40.4, 42.8, 45.2, 47.6 (★间距 2.4mm, 最右 47.6 < 49.2 ✓ 不碰 J_SOM_P1)
#   ★**R_SEL 在 y=5.6 (上排) · TP 在 y=8.8 (下排) ⇒ 两排分开, TP 不挡 R_SEL**
#   ★★**但 TP 在 y=8.8 会落在 BTB 焊盘排 (7.61..8.31) 的下方 ⇒ ⇒ ★**TP 必须避开 x15.2..34.8 (J_SOM_P3) 与 x49.2..68.8 (J_SOM_P1)**
#      ⇒ 本臂的 TP 全在 x35.6..48.6 ⇒ ★**正好在两个座之间的空档 ⇒ 不挡任何 BTB 出脚** ✓
#   ★**按 SoM 脚 x 从大到小排 (最近的排最近 ⇒ SRC 腿最短)**:
#     SoM x: D0_N=23.60 D0_P=23.20 D1_N=22.40 D1_P=22.00 D2_N=20.00 D2_P=19.60 D3_N=18.80 D3_P=18.40
#   ★**挪这 6 个 (SRC 腿最长的)**: D2_N(87.7mm) D3_N(98.5mm) D2_P(92.9mm) D1_N(66.1mm) D0_N(55.4mm) D3_P(71.3mm)
#   ★**留在右上**: CK_N/CK_P · D0_P(60.5mm 但离 BTB 最近, 挪了收益小) · D1_P(71.3mm 但 TP 挪位会挤)
PP="R_SEL_D0_N:35.60,5.60;R_SEL_D1_N:38.00,5.60;R_SEL_D2_N:40.40,5.60"
PP="$PP;R_SEL_D2_P:42.80,5.60;R_SEL_D3_N:45.20,5.60;R_SEL_D3_P:47.60,5.60"
# ★**配套 TP (★lane 侧, 与 R_SEL 同网)**: 放在同一 x 列的 y=8.8 ⇒ ★**不挡 BTB 出脚**
PP="$PP;TP_DSI_D0_N:35.60,8.80;TP_DSI_D1_N:38.00,8.80;TP_DSI_D2_N:40.40,8.80"
PP="$PP;TP_DSI_D2_P:42.80,8.80;TP_DSI_D3_N:45.20,8.80;TP_DSI_D3_P:47.60,8.80"

echo "=== v58 臂 R (W_MIN=0.15 + R_SEL×6 + TP×6 一起钉位) ==="
echo "  钉位: $PP"
(
  cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
  env PCB_W_MIN=0.15 PCB_PART_POS="$PP" \
      PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
      PCB_BOARD_W=160 PCB_BOARD_H=100 \
      PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
      PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
      PCB_PAIR_EXEMPT_R=0.0 \
      PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 \
      PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
      PCB_OUT="$OUT" \
      timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$LOG" 2>&1
  echo "EXIT=$?" >> "$LOG"
) &
echo "  [v58 臂 R] PID=$! → $OUT"
echo "=== 已起 (官方板不动) ==="
