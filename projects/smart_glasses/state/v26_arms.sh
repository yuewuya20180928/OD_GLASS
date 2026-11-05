#!/usr/bin/env bash
# v26_arms.sh —— ★**v25 之后的并行实验臂** (2026-11-05 07:45)
# 目的: 一次跑 3 个臂, 用**隔离的 PCB_OUT** (★绝不动官方板), 比"布不动的脚"个数
# ★**纪律**: 一个臂一个写者 (各自 PCB_OUT) ⇒ 官方板只由"赢家轮"落盘
# 用法: bash state/v26_arms.sh
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
RUN=state/v26_runs
mkdir -p "$RUN"

launch() {   # $1=臂名 $2=层数 $3=halo $4=预算倍数 $5=额外env
  local name="$1" L="$2" halo="$3" mult="$4" extra="$5"
  local out="/tmp/v26_${name}.kicad_pcb"
  rm -f "$out" /tmp/v26_${name}.log
  ( cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses && \
    env PCB_LAYERS="$L" PCB_HALO_MARGIN="$halo" PCB_ABUDGET_MULT="$mult" $extra \
        PCB_OUT="$out" timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "/tmp/v26_${name}.log" 2>&1 ; echo "EXIT=$?" >> "/tmp/v26_${name}.log" ) &
  echo "  [臂 $name] PID=$! L=$L halo=$halo mult=$mult env='$extra' out=$out log=/tmp/v26_${name}.log"
}

echo "=== v26 并行实验臂 (08:10) ==="
# ★**共同基线** (v25 的全部修复 + ★差分对端点连接器钉回原位 + rip-up + 长网先走)
launch A 8  0.20 6 "PCB_SKIP_PAD_CELLS=1"   # ★基线臂
launch B 8  0.20 6 "PCB_SKIP_PAD_CELLS=0"   # ★单变量: 关掉"halo 不盖焊盘格" (★可能是我丢对的那个)
launch C 10 0.20 6 "PCB_SKIP_PAD_CELLS=1"   # ★单变量: 8层→10层 (★官方载板本身就是 10 层)
echo "=== 三个臂已起 (官方板不动) ==="

# ★★2026-11-05 08:22 **加第四臂: 更大的板** (★布线密度是核心矛盾 ⇒ 180×120 给路由器更多余地)
#   ⇒ 板尺寸是产品决策, 但 demo 板做大没问题; ★**面积与层数两个方向都测过** (v16 测过面积但只到 6 层)
launch() {   # $1=臂名 $2=层数 $3=halo $4=预算倍数 $5=额外env
  local name="$1" L="$2" halo="$3" mult="$4" extra="$5"
  local out="/tmp/v26_${name}.kicad_pcb"
  rm -f "$out" /tmp/v26_${name}.log
  ( cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses && \
    env PCB_LAYERS="$L" PCB_HALO_MARGIN="$halo" PCB_ABUDGET_MULT="$mult" $extra \
        PCB_OUT="$out" timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "/tmp/v26_${name}.log" 2>&1 ; echo "EXIT=$?" >> "/tmp/v26_${name}.log" ) &
  echo "  [臂 $name] PID=$! L=$L halo=$halo mult=$mult env='$extra' out=$out log=/tmp/v26_${name}.log"
}
launch D 8 0.20 6 "PCB_SKIP_PAD_CELLS=1 PCB_BOARD_W=180 PCB_BOARD_H=120 PCB_AREA_BOT=5,58,70,117 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,177,117"
echo "=== 第四臂已起 (板 180x120) ==="
