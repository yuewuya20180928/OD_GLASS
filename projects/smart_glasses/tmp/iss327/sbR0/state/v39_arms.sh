#!/usr/bin/env bash
# v39_arms.sh —— ★**v39 概念: DSI 中途串阻阵 `R_SEL_D*` 归位 (摆放在反方向 ⇒ 修摆放)**
#
# ★★**为什么要有 (2026-11-05 22:0x 机器读出的根因)**:
#   - DSI lane 的路径中途有 2 脚器件 `R_SEL_D*` (pad1=SoM 侧 net `*_SRC`, pad2=连接器侧 net)
#     ⇒ lane 被拆成两个独立 2 焊盘网 (⇒ 交叉可在摆放里吸收, **不必写路由器 crossover**)
#   - ★**真根因 = 摆放方向反了**: `R_SEL_D*` 整阵被行式装箱甩到 **x=78.90…118.90** (右上角)
#     而它两端点**全在左边**:
#       · SoM `J_SOM_P3` DSI 脚  x=18.40…23.60, y=7.96
#       · `CONN_LIGHT` DSI 脚    x=26.25…34.75, y=60.15
#     ⇒ ★**单 lane 走 168mm 斜穿全板** (官方板实测 `DSI_D0_D2_P` 铜已到 x=105, **最后一跳缺 78mm**)
#   - ★**P/N 序**: SoM 侧与 CONN_LIGHT 侧**都是 P 在左** ⇒ DSI **不需要 P/N 自交**
#     (只有 CSI 的 `CONN_CAM` 侧 N 在左 ⇒ 才需要 P/N 互换 ⇒ 那是 v38 crossover 的事)
#
# ★**本臂改什么**: 只加一个 env `PCB_PART_POS` (★把 10 个 `R_SEL_D*` 钉到顶带, **按 SoM lane 顺序**)
#   ★ 顺序 = SoM P3 的 DSI 脚 x 序 (D3,D2,CK,D1,D0) ⇒ 腿 A (SoM→串阻) 零交叉
#   ★ 腿 B (串阻→CONN_LIGHT) 承担 lane 3-cycle 交叉 (D0×CK×D1) ⇒ 那里是长走廊, 有换层空间
#   ★ 其余 env 与 v36_S **逐位相同** ⇒ 单变量可比
# ★**默认关**: `PCB_PART_POS` 空 ⇒ 与 v31/v36/v37 逐位一致 (机制在 gen_pcb_netlist_board.py, env 门控)
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {   # $1=臂名
  local name="$1"
  local out="/tmp/v39_${name}.kicad_pcb"
  local log="/tmp/v39_${name}.log"
  if [ -e "$out" ] || [ -e "$log" ]; then
    echo "  [v39 臂 $name] ★已有产物/日志 ⇒ 不覆盖 (铁律: 不删别人的输出) ⇒ 跳过"
    return 0
  fi
  # ★R_SEL_D* 顶带坐标: 同 lane P/N 间距 2.45mm (铜间隙 0.25), lane 间 5.15mm (铜间隙 2.95)
  local pp="R_SEL_D3_P:5.50,3.0;R_SEL_D3_N:7.95,3.0;R_SEL_D2_P:13.10,3.0;R_SEL_D2_N:15.55,3.0"
  pp="$pp;R_SEL_CK_P:20.70,3.0;R_SEL_CK_N:23.15,3.0;R_SEL_D1_P:28.30,3.0;R_SEL_D1_N:30.75,3.0"
  pp="$pp;R_SEL_D0_P:35.90,3.0;R_SEL_D0_N:38.35,3.0"
  (
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    env PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
        PCB_BOARD_W=160 PCB_BOARD_H=100 \
        PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
        PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
        PCB_PAIR_EXEMPT_R=0.0 \
        PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 \
        PCB_PART_POS="$pp" \
        PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "$log" 2>&1
    echo "EXIT=$?" >> "$log"
  ) &
  echo "  [v39 臂 $name] PID=$! → $out"
}

echo "=== v39 臂 R (DSI 中途串阻阵归位; 只加 PCB_PART_POS) ==="
launch R
echo "=== 已起 (官方板不动) ==="
