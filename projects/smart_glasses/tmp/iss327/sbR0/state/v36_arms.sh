#!/usr/bin/env bash
# v36_arms.sh —— ★**v36 轮: 治"窄焊盘边缘落孔"** (2026-11-05 21:45)
# ★**根因 (机器读数, 非推测)**:
#   v35_R 落盘: DRC 2 (两条 clearance, 其实是**同一颗孔**) / unconnected 62 / EXIT=0
#   ⇒ KiCad 按线段各报一次, 两条都指向 ★**同一颗 GND 孔 @ (62.700, 64.450) Ø0.5**
#   ⇒ 该孔压住 `U_TEMP.1` (I2C_B_SCL) 的逃逸短桩 (62.895,63.850)->(62.700,63.950)
#     ⇒ 孔到桩 0.50mm ⇒ ★**净距 0.125mm < 0.20mm** ⇒ DRC clearance ×2
#   ★**它为什么会落在那儿**:
#     ① `U_TEMP.2` 的焊盘**短边 < 0.55mm** (窄焊盘)
#     ② 第一遍"焊盘内直接落孔"分支取**环格** (r=0.8mm ⇒ 网格最近格 0.15mm)
#        ⇒ 孔心离焊盘中心仅 **0.201mm** ⇒ ★**孔探出焊盘铜**
#     ③ ★**第三遍有 `_short<0.55` 的尺寸门槛, 第一遍漏了** ⇒ 窄焊盘被塞了个边缘孔
#     ④ ★而这个焊盘本来就被第四遍"沿长轴引出"正确接好 (0.9mm 线 + Ø0.6 孔 @63.795,64.500)
#        ⇒ 那颗孔 **100% 多余**
# ★**单变量**: 只加三处判据 (路由器其余逻辑一行没动) ⇒ **env 与 v35_R 完全相同**
#   ① in-pad 分支: 焊盘短边 ≥ 孔径+0.10 ⇒ 窄焊盘交给第四遍
#   ② 三遍成功都登记 `done_pads` ⇒ ★**同一焊盘绝不落两个孔**
#   ③ 第三遍门槛 0.55 → 0.60 (孔径+0.10)
# ★**预期**: ★**DRC 0 + unconnected 62** ⇒ 若成立 ⇒ Pareto 过闸 (基线 v31_Q = DRC 0 / 64)
# ★**代价预期**: 窄焊盘的 GND 下拉从"in-pad 孔"变成"长轴引出" ⇒ 可能慢一点/多几个未通 ⇒ 以实测为准
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {   # $1=臂名 $2=层数 $3=额外env
  local name="$1" layers="$2" extra="$3"
  local out="/tmp/v36_${name}.kicad_pcb"
  local log="/tmp/v36_${name}.log"
  if [ -e "$out" ] || [ -e "$log" ]; then
    echo "  [v36 臂 $name] ★已有产物/日志 ⇒ 不覆盖 (铁律: 不删别人的输出) ⇒ 跳过"
    return 0
  fi
  (
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    env PCB_LAYERS="$layers" PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
        PCB_BOARD_W=160 PCB_BOARD_H=100 \
        PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
        PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
        PCB_PAIR_EXEMPT_R=0.0 \
        $extra PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "$log" 2>&1
    echo "EXIT=$?" >> "$log"
  ) &
  echo "  [v36 臂 $name] PID=$! L=$layers env='$extra' → $out"
}

echo "=== v36 (治窄焊盘边缘落孔 ⇒ v35_R 那两条 clearance 的根因) ==="
launch R 8 "PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0"   # ★env 与 v35_R 完全相同 (单变量 = 代码补丁)
echo "=== v36 单臂已起 (官方板不动; 自动晋级守候器随后挂上) ==="
