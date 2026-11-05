#!/usr/bin/env bash
# v43_arms.sh -- ★**v43 概念: CSI 差分对交叉靠"摆放吃掉" (N 侧 AC 电容 rot=180 + 移到第二行)**
#
# ★★**机制 (机器读出的根因)**:
#   每条 CSI lane 的 P/N 之间夹着**两个分立的 2 脚器件** (C_AC_CSI_D0_xx_P / _N)
#   ⇒ P 网和 N 网是**两条完全独立的网** ⇒ "lane 必须交叉" **不是硬约束**
#   ⇒ ★**交叉可以在器件摆放 + 旋转里吃掉** ⇒ **不必写 crossover 代码**
#
# ★**几何 (探针 state/probe_lane_fix.py 实测)**:
#   段1 (SoM→器件pad1): SoM 端 P 在左 ⇒ 要求 **P.pad1 < N.pad1**
#   段2 (器件pad2→连接器): 连接器端 N 在左 ⇒ 要求 **N.pad2 < P.pad2**
#   N 侧电容 rot=180 ⇒ pad1 在右 / pad2 在左 ⇒ **px < ox < px+3.2** 即可两段都成立
#   ⇒ ★**官方板 5 条 CSI lane 的反转全在 POST 段 ⇒ 这刀正好切在病根上**
#
# ★**为什么 N 侧要移到第二行 (y=57.0) 而不是同一行**:
#   同一行时 P.pad1 / N.pad2 / P.pad2 / N.pad1 会交错 ⇒ 焊盘边缘净距只剩 0.20mm (零裕量)
#   ⇒ 改放到 y=57.0 行 (AC 电容行 y=58.6 与 TP 行 y=55.2 之间) ⇒ 上下各留 0.80/0.90mm
#
# ★**★P/N 必须一起钉死** (探针教训: 只钉 N 侧 ⇒ 排版重排把 P 侧电容从 x=39.5 挤到 x=15.5)
# ★**★TP 也必须钉** (TP 走"贴伙伴件"逻辑; 不钉 ⇒ TP 的 x 序会把 POST 段重新变成反序)
#   ⇒ ★**为此给 PCB_PART_POS 补了 TP 支持** (默认关 ⇒ 与其它臂逐位一致)
#
# ★**基线 = v42 臂 env (官方板 env + keepout + 串阻归位 + PCB_VIA_HALO_EXACT=1)**
#   ⇒ ★**相对 v42 只多一个变量: CSI 镜像摆放**
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {
  local name="$1"
  local out="/tmp/v43_${name}.kicad_pcb"
  local log="/tmp/v43_${name}.log"
  if [ -e "$out" ] || [ -e "$log" ]; then
    echo "  [v43 臂 $name] ★已有产物/日志 ⇒ 不覆盖 ⇒ 跳过"; return 0
  fi
  # ★TP 焊盘中心 = 原点 +0.2 ⇒ 要落 pad@39.70 就写原点 39.50
  local CSI="C_AC_CSI_D0_D3_P:5.90,58.50;C_AC_CSI_D0_D3_N:7.50,57.00,180;\
C_AC_CSI_D0_D2_P:15.50,58.50;C_AC_CSI_D0_D2_N:17.10,57.00,180;\
C_AC_CSI_D0_CK_P:39.50,58.50;C_AC_CSI_D0_CK_N:41.10,57.00,180;\
TP_CSI_CK_P:39.50,55.30;TP_CSI_CK_N:38.30,55.30;\
C_AC_CSI_D0_D1_P:49.10,58.50;C_AC_CSI_D0_D1_N:50.70,57.00,180;\
C_AC_CSI_D0_D0_P:58.70,58.50;C_AC_CSI_D0_D0_N:60.30,57.00,180;\
TP_CSI_D0_P:58.70,55.30;TP_CSI_D0_N:57.30,55.30"
  local DSI="R_SEL_D3_P:5.50,3.0;R_SEL_D3_N:7.95,3.0;R_SEL_D2_P:13.10,3.0;R_SEL_D2_N:15.55,3.0;\
R_SEL_CK_P:20.70,3.0;R_SEL_CK_N:23.15,3.0;R_SEL_D1_P:28.30,3.0;R_SEL_D1_N:30.75,3.0;\
R_SEL_D0_P:35.90,3.0;R_SEL_D0_N:38.35,3.0"
  (
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    env PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
        PCB_BOARD_W=160 PCB_BOARD_H=100 \
        PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
        PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 PCB_PAIR_EXEMPT_R=0.0 \
        PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 \
        PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
        PCB_PART_POS="$DSI;$CSI" \
        PCB_VIA_HALO_EXACT=1 \
        PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "$log" 2>&1
    echo "EXIT=$?" >> "$log"
  ) &
  echo "  [v43 臂 $name] PID=$! → $out"
}
echo "=== v43 臂 R (CSI 镜像摆放; 基线=v42 env) ==="
launch R
echo "=== 已起 (官方板不动) ==="
