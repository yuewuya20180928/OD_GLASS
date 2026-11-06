#!/usr/bin/env bash
# v56_arms.sh -- ★★**v56 概念: R_SEL 串阻阵从"右上"挪到"J_SOM_P3 右侧" (2026-11-06 09:5x)**
#
# ★★★★**为什么要有这个臂 (2026-11-06 07:0x~09:4x 实测三重实证)**:
#   ① 官方板 unc 45 (18092段/433孔 · DRC 0 · md5 611b869e) ⇒ G1 要求 unc=0
#   ② ★**自研 A\*** (无 stub + halo 调优 + 拆挡路 + 承重守卫) ⇒ **最多 +3 条** (48→45)
#   ③ ★**freerouting 2.1.0 (工业级)** ⇒ 成品板上 37 轮 score 恒定 996.44 **零改善**;
#      ★**空板上** 191→89 unrouted (确实在布) ⇒ ★**但仍卡在 SoM BTB 出脚**
#      ⇒ ★★**两个完全独立的引擎撞同一堵墙 ⇒ 物理约束, 不是算法问题**
#
# ★★★**★根因 (布局级, 机器实测)**:
#   · DSI lane 拓扑 = `J_SOM_P3.x ──[SRC腿]── R_SEL_Dx_x ──[lane腿]── CONN_LIGHT.pin`
#     (★R_SEL 是串在 lane 中间的匹配电阻, ★**网表已核对**)
#   · ★**R_SEL 串阻阵现在在右上角 (x78.9..117.3, y5.5..9.5)** ⇒ ★**行式自动排版的结果**
#   · ⇒ SRC 腿 = J_SOM_P3 顶排 (x18.4..23.6, y7.96) ⇒ **横穿全板 55~98mm**
#   · ⇒ ★**且必须穿过 J_SOM_P1 座 (x49.2..68.8, y7.96..11.04) 占着的位置**
#   · ★**板顶走廊实测全满**: y0..3.5 带 1723 条 / y3.5..7.0 带 2551 条 / y7..11 带 1964 条
#     ⇒ ★**顶部没有任何可用走廊**
#
# ★★★**★修法 (本臂)**: ★**把 8 个 R_SEL 挪到 J_SOM_P3 右侧 (x36..53, y5.6)**
#   ★**为什么这样摆**: ★**串阻紧邻它服务的 SoM 出口才是正确布局** (SRC 腿才短)
#   ★**实测距离收益 (算出来的)**:
#     · SRC 腿合计  **593.1mm → 192.2mm (↓68%)**
#     · lane 腿合计  684.3mm → 456.8mm (↓33%)**
#     · 总铜长      1277mm   → 649mm   (↓49%)**
#   ★**而且 SRC 腿变成 x18..53 的局部走线** ⇒ **可以绕开 J_SOM_P1 座 (x49.2 起)**
#
# ★**本臂只改 8 个 R_SEL 的位置** (★不动网表 / 不动封装 / 不动其他器件)
#   ★**⇒ 与官方板 v37_R 的差异是单变量 ⇒ A/B 干净**
# ★**环境**: 沿用官方 v37 的 env 逐位相同 (★**不加任何开关** ⇒ 差异只来自 R_SEL 位置)
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

OUT=/tmp/v56_R.kicad_pcb
LOG=/tmp/v56_R.log
if [ -e "$OUT" ] || [ -e "$LOG" ]; then
  echo "  [v56 臂 R] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"
  exit 0
fi

# ★★**R_SEL 钉位 (★x,y = 封装原点 = pad1 位置 = SRC 侧)**
#   ★**按 SoM 脚 x 从大到小排 (最近的排最近)** ⇒ SRC 腿最短
#   ★**pad1(SRC) 朝左 (SoM 方向) · pad2(lane) 朝右** ⇒ 0402 横放, rot=0
#   ★★**实测: 8 个串阻 pad 间距 1.6mm (0.6 宽焊盘 + 1.0 间隙) ⇒ 间距取 2.4mm 够放走线**
#   · SoM 脚 x: D0_N=23.60 D0_P=23.20 D1_N=22.40 D1_P=22.00 D2_N=20.00 D2_P=19.60 D3_N=18.80 D3_P=18.40
#   · ⇒ 从右到左排: D0_N D0_P D1_N D1_P D2_N D2_P D3_N D3_P
PP="R_SEL_D0_N:36.50,5.60;R_SEL_D0_P:38.90,5.60;R_SEL_D1_N:41.30,5.60;R_SEL_D1_P:43.70,5.60"
PP="$PP;R_SEL_D2_N:46.10,5.60;R_SEL_D2_P:48.50,5.60;R_SEL_D3_N:50.90,5.60;R_SEL_D3_P:53.30,5.60"

echo "=== v56 臂 R (R_SEL 串阻阵挪到 J_SOM_P3 右侧) ==="
echo "  钉位: $PP"
(
  cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
  env PCB_PART_POS="$PP" \
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
echo "  [v56 臂 R] PID=$! → $OUT"
echo "=== 已起 (官方板不动) ==="
