#!/usr/bin/env bash
# v30_arms.sh —— ★**v30 轮: 治 v29_N 剩下的 6 条 DRC** (2026-11-05 13:40)
# ★**背景 (实测 v29_N, 板已落盘, 机器读数)**: DRC **6** (v28 的 147 → 6 ✔ 两个根因修复有效) · unconnected **74**
#   ★**剩下的 6 条全是"记账/几何判据"问题, 不是布线失败**:
#   ① 3 × `hole_to_hole` (GND 下拉过孔间距不够: 净距 0.0000 / 0.2000 / 0.0536mm, 板限 0.25mm)
#      ★**根因**: `_via_exists` 只查**同点** ⇒ ★**中心只差 0.25mm 的两个孔也能各落一个**
#      ⇒ ★**修法**: 新增 `_via_center_ok()` ⇒ 孔中心距 ≥ MIN_VIA_CENTER (0.58mm) ⇒ 同网异网都算
#   ② 3 × `track_dangling` (GND 短铜 0.25mm, 端点悬空)
#      ★**根因 A**: `cleanup_geometry` 的"落在过孔上"判据**不带网** ⇒ ★**别网的过孔也算接上**
#      ★**根因 B**: 顺序是"先删悬空段 → 再删孤立过孔" ⇒ ★**孔删了, 挂在它上的短铜变成悬空, 没人再查**
#      ⇒ ★**修法**: 按网记过孔点 + 端点/计数全部按网 + ★**删孔↔删悬空段循环到不动点**
# ★**单变量**: v30 = v29_O 的全部 env (8层 + GND_FIRST) + 上面两刀 ⇒ 其它一律不动
# ★**目标**: DRC 1 (v29_O) → **0**, unconnected 64 (v29_O) → ≤64
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {   # $1=臂名 $2=层数 $3=额外env
  local name="$1" layers="$2" extra="$3"
  local out="/tmp/v30_${name}.kicad_pcb"
  rm -f "$out" "/tmp/v30_${name}.log"
  (
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    env PCB_LAYERS="$layers" PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
        PCB_BOARD_W=160 PCB_BOARD_H=100 \
        PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
        PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
        PCB_PAIR_EXEMPT_R=0.0 \
        $extra PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "/tmp/v30_${name}.log" 2>&1
    echo "EXIT=$?" >> "/tmp/v30_${name}.log"
  ) &
  echo "  [v30 臂 $name] PID=$! L=$layers env='$extra' → $out"
}

echo "=== v30 (治 v29_N 剩的 6 条 DRC: 孔中心距 + 悬空段不动点) ==="
launch P 8 "PCB_GND_FIRST=1"               # ★与 v29_O 同参 (只多两刀) ⇒ 可直接对比
echo "=== v30 单臂已起 (官方板不动; 自动晋级守候器随后挂上) ==="
