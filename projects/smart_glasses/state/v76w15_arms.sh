#!/usr/bin/env bash
# v76w15_arms.sh -- ★★★**0.15mm 臂 (★用【当前代码】重跑, ★因为 v57 那次的读数可能已过期)** ★★★
#
# ★★★**★为什么重跑 (★2026-11-09 15:5x 实测推出来的)★★★**
#   ★**MEMORY 里"单改线宽这条路判死"的依据 = v57 臂 (★11-06 跑的) ⇒ ★**那次的两个失败原因, 之后都修好了** ★★
#     · ★**① 过孔净距盲区**: ★**`_via_ok` 只查 `halo[2]` ⇒ 看不见 0.25mm 走线** ⇒ ★**已修 (`PCB_VIA_CHECK_ALL_CLS` + `patch_astar_gated.py` 换层点几何闸)**
#     · ★**② `_stub_clear` 的 need 硬编码 0.299** ⇒ ★**W_MIN=0.15 时偏严 0.024mm ⇒ 把能过的直道判死** ⇒ ★**已修 (★need 跟着 W_MIN 走)**
#   ⇒ ★★**⇒ v57 的 "unc 45→60 / 退铜 8 网" 很可能是【修复前】的读数 ⇒ ★★**必须重跑才能下结论** ★★★ ★★★
#
# ★★★**★本臂是【干净的 A/B】★★★★** ★★★
#   ★**基线臂 = `state/v76_arms.sh` (★PCB_PART_POS 换边重试版)** ⇒ ★**本臂 = 同一份 env, 只加 `PCB_W_MIN=0.15`** ⇒ ★★**逐位只差一个变量** ★★
#   · ★**而且 `PCB_W_MIN` 只用于【出脚直道】(★`gen_pcb_routing.py:2947` 追加的是 W_MIN)** ⇒ ★★**⇒ 产出的就是【混合线宽板】: 信号仍 0.25mm, 只把 BTB 出脚细到 0.15mm ⇒ ★★**这正是我们想要的那种板, 不是"全板 0.15mm"** ★★**
#
# ★**跑完的读数流程 (★与基线同一把尺子)**:
#   ① 板出来 ⇒ ② 套【已校准的官方补丁链】(`state/replay_patch_chain.sh`) ⇒ ③ vs `state/.lastgood/baseline_v76_chain.kicad_pcb`
#   ⇒ ★**用 `state/compare_arm_baseline.sh` (★不是 vs 官方板!)**
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

OUT=/tmp/v76w15_R.kicad_pcb
LOG=/tmp/v76w15_R.log
DRC=/tmp/v76w15_R.drc.json

echo "=== v76w15 臂: 官方配方 + 换边重试 + ★W_MIN=0.15★ (★只差基线臂一个变量) ==="
echo "  产出: $OUT   日志: $LOG"

(
  cd "$PROJ"
  env PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
      PCB_BOARD_W=160 PCB_BOARD_H=100 \
      PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
      PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
      PCB_PAIR_EXEMPT_R=0.0 \
      PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 \
      PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
      PCB_PART_POS="R_SEL_D3_P:5.50,3.0;R_SEL_D3_N:7.95,3.0;R_SEL_D2_P:13.10,3.0;R_SEL_D2_N:15.55,3.0;R_SEL_CK_P:20.70,3.0;R_SEL_CK_N:23.15,3.0;R_SEL_D1_P:28.30,3.0;R_SEL_D1_N:30.75,3.0;R_SEL_D0_P:35.90,3.0;R_SEL_D0_N:38.35,3.0" \
      PCB_VIA_HALO_CENTER=1 \
      PCB_W_MIN=0.15 \
      PCB_OUT="$OUT" \
      timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$LOG" 2>&1
  echo "EXIT=$?" >> "$LOG"
) &
_PID=$!
echo "  [v76w15 臂] PID=$_PID"

while kill -0 "$_PID" 2>/dev/null; do sleep 60; done
echo "=== 第①步结束 (EXIT 见 $LOG) ==="
if [ ! -f "$OUT" ]; then
  echo "❌ 没出板 ⇒ 收工 (看 $LOG)"; exit 2
fi

echo "── 板面读数 ──"
echo "  走线 = $(grep -ac '(segment' "$OUT") · 过孔 = $(grep -ac '(via' "$OUT")"
bash state/kicad.sh pcb drc --output "$DRC" --severity-error --severity-warning --format json "$OUT" >/dev/null 2>&1
python3 - "$DRC" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
print("  DRC违规 = %d · unconnected = %d" % (len(d.get("violations") or []), len(d.get("unconnected_items") or [])))
PY

echo "── 套【已校准的官方补丁链】 (★与基线同一把尺子) ──"
bash state/replay_patch_chain.sh "$OUT" v76w15
RC=$?
echo "  链 rc=$RC"

echo "── vs 同链基线 (★不是 vs 官方板) ──"
FINAL="/tmp/chain_v76w15/final_chain.kicad_pcb"
if [ -f "$FINAL" ]; then
  bash state/compare_arm_baseline.sh "$FINAL"
else
  echo "  ⚠️ 链没出终板 (rc=$RC) ⇒ 没法比"
fi
exit 0
