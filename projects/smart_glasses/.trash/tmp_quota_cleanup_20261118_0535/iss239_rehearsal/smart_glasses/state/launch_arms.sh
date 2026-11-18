#!/usr/bin/env bash
# launch_arms.sh —— ★**启动 v26 四臂 (带同网缝合基线)** (2026-11-05 08:45)
# ★★为什么要写进文件: 之前在命令行里 launch ⇒ ★★kill 循环的模式匹配到自己 ⇒ SIGTERM 把刚起的臂一起杀了
# ⇒ ⇒ **启动脚本必须是独立文件 + setsid**
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {   # $1=臂名 $2=层数 $3=额外env
  local name="$1" L="$2" extra="$3"
  local out="/tmp/v26_${name}.kicad_pcb"
  rm -f "$out" "/tmp/v26_${name}.log"
  (
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    env PCB_LAYERS="$L" PCB_ABUDGET_MULT=6 $extra PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "/tmp/v26_${name}.log" 2>&1
    echo "EXIT=$?" >> "/tmp/v26_${name}.log"
  ) &
  echo "  [臂 $name] PID=$! L=$L env='$extra' log=/tmp/v26_${name}.log"
}

echo "=== v26 四臂 (08:45, 含同网缝合基线) ==="
launch A 8  "PCB_SKIP_PAD_CELLS=1"
launch B 8  "PCB_SKIP_PAD_CELLS=0"
launch C 10 "PCB_SKIP_PAD_CELLS=1"
launch D 8  "PCB_SKIP_PAD_CELLS=1 PCB_BOARD_W=180 PCB_BOARD_H=120 PCB_AREA_BOT=5,58,70,117 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,177,117"
echo "=== 四臂已起 (官方板不动) ==="
