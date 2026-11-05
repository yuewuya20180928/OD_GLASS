#!/usr/bin/env bash
# v47_arms.sh -- ★**v47 概念: GND 同排相邻焊盘"合并下拉"** (★不是挪孔, 是少落孔)
#
# ★★★**为什么 (2026-11-06 01:5x 机器读)**:
#   · CONN_LIGHT 有 **8 个 GND 焊盘**, 其中 `.21/.20` 相距仅 **0.50mm** (同排 0.5mm pitch)
#   · 而过孔中心距下限 = **0.58mm** ⇒ ★**同排相邻两个焊盘放不下各自的孔**
#   · ⇒ 每个焊盘被迫往外扩 ⇒ 扩成 **0.75mm 间距的一排** ⇒ ★**"栅栏"成形**
#   · ⇒ 实测该带 **15 个孔** = 9 个"走一段线再落孔"(栅栏本体) + 6 个同网缝合链
#   · ⇒ ★**62/62 条失败段都在这排栅栏 1.2mm 内**
#
# ★★**为什么"改落位规则"治不了 (★实测两条臂都失败)**:
#   · v45 (对称 MIN=2.0) ⇒ `CSI_D0_CK_P` ok=True ⇒ **ok=False** (打地鼠)
#   · v46 (DOWN 方向 1.5) ⇒ `CSI_D0_CK_P` 同样 **ok=False** (打地鼠)
#   · ⇒ ★**落位自由度只有 1 格 ⇒ 任何扰动都重排全局 ⇒ 必打坏某对**
#
# ★**本臂的修法 (代码机制, env 门控默认关)**: `PCB_GND_SHARE_ROW=1`
#   ⇒ ★**先把同排相邻的 GND 焊盘短接成链, 只在链端落一个孔**
#   ⇒ 单测 (`state/_test_gnd_share.py` 全过): CONN_LIGHT **8 个焊盘 ⇒ 2 个落孔点**
#   ⇒ ★**不是挪孔, 是少落孔** ⇒ ★**不会打地鼠** ⇒ ★**栅栏从根上消失**
#   ⇒ 缝合链每步 ≤1.5mm ⇒ ★**远低于第二遍 6mm 硬闸** ⇒ 不产生新未连接
#
# ★**单变量 (vs v44 臂)**: env 完全相同, 只多 `PCB_GND_SHARE_ROW=1`
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {
  local name="$1"
  local out="/tmp/v47_${name}.kicad_pcb"
  local log="/tmp/v47_${name}.log"
  if [ -e "$out" ] || [ -e "$log" ]; then
    echo "  [v47 臂 $name] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"; return 0
  fi
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
        PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 \
        PCB_CONN_GND_ESCAPE="CONN_CAM:4.0" \
        PCB_GND_SHARE_ROW=1 \
        PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
        PCB_PART_POS="$pp" \
        PCB_VIA_HALO_CENTER=1 \
        PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "$log" 2>&1
    echo "EXIT=$?" >> "$log"
  ) &
  echo "  [v47 臂 $name] PID=$! → $out"
}
echo "=== v47 臂 R (v44 env + PCB_GND_SHARE_ROW=1: GND 同排合并下拉) ==="
launch R
echo "=== 已起 (官方板不动) ==="
