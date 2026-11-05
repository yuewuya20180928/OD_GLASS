#!/usr/bin/env bash
# v31_arms.sh —— ★**v31 轮: 治 v30_P 剩下唯一那条 `hole_to_hole`** (2026-11-05 14:05)
# ★**v30_P 实测 (机器读数)**: DRC **1** / unconnected **64** (EXIT=0) ⇒ ★**两刀只打中一条**
#   ⇒ 剩下的 = `hole_to_hole`: 两个 **GND** 孔 @24.45 / 24.95, y=60.2 ⇒ **中心距 0.50mm, 净距 0.2000mm**
# ★**真根因 (不是"判据各查各的"这么简单)**: `_via_exact_ok()` 的第 ③ 条判据
#   "孔心到已有过孔 ≥ 0.60mm" 写了 ★**`if vn == net: continue`** ⇒ ★**同网的孔直接豁免**
#   ⇒ ⇒ 这两个孔**都是 GND** ⇒ 第二个就这么落在 0.50mm 上
#   ⇒ ⇒ ★**孔到孔是制造规则 (钻孔/电镀), 跟网一点关系都没有** ⇒ ★**同网异网一律卡 0.60mm**
# ★**三刀**:
#   ① `_via_exact_ok` ③/④ 删掉"同网不算" (★**真根因**)
#   ② `cleanup_geometry` 加"孔中心距兜底" (删后落的那个) ⇒ ★**任何路径漏网的都被它兜住**
#   ③ 焊盘内过孔补登 `via_hash` (★之前只有 `self.vias`, A* 的 `_via_too_close` 看不见它)
# ★**单测 `state/_test_cleanup.py` = PASS** (含"同网两孔 0.50mm ⇒ 判不合格"新用例)
# ★**代价预期**: GND 落孔可能少几个 ⇒ unconnected 64 → 64~67 ⇒ ★**宁可 unconnected 多几条, 也要 DRC=0**
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

launch() {   # $1=臂名 $2=层数 $3=额外env
  local name="$1" layers="$2" extra="$3"
  local out="/tmp/v31_${name}.kicad_pcb"
  rm -f "$out" "/tmp/v31_${name}.log"
  (
    cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
    env PCB_LAYERS="$layers" PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
        PCB_BOARD_W=160 PCB_BOARD_H=100 \
        PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
        PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
        PCB_PAIR_EXEMPT_R=0.0 \
        $extra PCB_OUT="$out" \
        timeout 14400 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "/tmp/v31_${name}.log" 2>&1
    echo "EXIT=$?" >> "/tmp/v31_${name}.log"
  ) &
  echo "  [v31 臂 $name] PID=$! L=$layers env='$extra' → $out"
}

echo "=== v31 (治 v29_N 剩的 6 条 DRC: 孔中心距 + 悬空段不动点) ==="
launch Q 8 "PCB_GND_FIRST=1"               # ★与 v29_O 同参 (只多两刀) ⇒ 可直接对比
echo "=== v31 单臂已起 (官方板不动; 自动晋级守候器随后挂上) ==="
