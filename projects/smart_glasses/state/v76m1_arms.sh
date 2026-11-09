#!/usr/bin/env bash
# v76m1_arms.sh -- ★★第一批"挪焊盘让路"臂 (★v76 基线 + ★12 个 0.3mm 小挪) ★★
#
# ★★★**★设计 (★每一条都有依据)★★★** ★★★
#   ★**① 基线 = `state/v76_arms.sh` 的 env 逐位不变** ⇒ ★**只多一条 `PCB_PART_POS` (★合并, ★不是覆盖)**
#   ★**② 挪的 12 个器件来自 `state/plan_part_moves.py` 在【臂自己的板 `/tmp/v76_R.kicad_pcb`】上算出的清单**
#      ⇒ ★**位置一致性已校验 (★对照官方板, ★位置不同的 16 个器件已剔除)** ★
#   ★**③ 只挪 ≤2 焊盘的小器件 (★TP 单焊盘 / 电阻 2 焊盘)⇒ ★★**挪器件 ≈ 挪焊盘** ★★
#   ★**④ 位移全是 0.3mm ⇒ ★★**最小改动 ⇒ 一旦变差, 立刻能定位是"哪一挪"** ★★
#   ★★**⇒ 与 v76 臂的 env 逐位对照 = 只差 PCB_PART_POS ⇒ ★★**干净 A/B** ★★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

OUT=/tmp/v76m1_R.kicad_pcb
LOG=/tmp/v76m1_R.log
DRC=/tmp/v76m1_R.drc.json

echo "=== v76m1 臂: v76 基线 + ★12 个 0.3mm 小挪 (★挪焊盘让路) ==="
(
  cd "$PROJ"
  env PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
      PCB_BOARD_W=160 PCB_BOARD_H=100 \
      PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
      PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
      PCB_PAIR_EXEMPT_R=0.0 \
      PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 \
      PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
      PCB_PART_POS="R_SEL_D3_P:5.50,3.0;R_SEL_D3_N:7.95,3.0;R_SEL_D2_P:13.10,3.0;R_SEL_D2_N:15.55,3.0;R_SEL_CK_P:20.70,3.0;R_SEL_CK_N:23.15,3.0;R_SEL_D1_P:28.30,3.0;R_SEL_D1_N:30.75,3.0;R_SEL_D0_P:35.90,3.0;R_SEL_D0_N:38.35,3.0;C_AC_CSI_D0_D0_N:62.377,54.986;C_KEY_CAM:20.300,62.200;D_ESD_LIGHT:90.077,56.996;R_JTAG_TDI:141.300,56.506;R_LED_B:71.718,58.599;R_PG_PULL:75.920,46.001;R_PU_I2CB_SCL:11.739,70.115;R_PU_I2CB_SDA:27.692,68.795;SW_KEY_CAM:16.100,63.200;TP_FSIN:92.801,46.720;TP_I2CA_SCL:51.599,62.680;TP_I2CB_SDA:27.563,68.974" \
      PCB_VIA_HALO_CENTER=1 \
      PCB_OUT="$OUT" \
      timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$LOG" 2>&1
  echo "EXIT=$?" >> "$LOG"
) &
_PID=$!
echo "  [v76m1 臂] PID=$_PID"
while kill -0 "$_PID" 2>/dev/null; do sleep 60; done
echo "=== 第①步结束 ==="
[ -f "$OUT" ] || { echo "❌ 没出板 ⇒ 收工 (看 $LOG)"; exit 2; }
echo "── 板面读数 ──"
echo "  走线 = $(grep -ac '(segment' "$OUT") · 过孔 = $(grep -ac '(via' "$OUT")"
bash state/kicad.sh pcb drc --output "$DRC" --severity-error --severity-warning --format json "$OUT" >/dev/null 2>&1
python3 - "$DRC" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
print("  DRC违规 = %d · unconnected = %d" % (len(d.get("violations") or []), len(d.get("unconnected_items") or [])))
PY
echo "── ★挪完在【臂的板】上重跑走廊冲突探针 (★确认没占掉别人的走廊) ──"
bash state/pcbnew_py.sh state/probe_lane_conflicts.py "$OUT" "$DRC" --out /tmp/_lane_conflicts_arm_m1.txt 2>&1 | tail -3
echo "── 套【已校准的官方补丁链】 ──"
bash state/replay_patch_chain.sh "$OUT" v76m1
FINAL="/tmp/chain_v76m1/final_chain.kicad_pcb"
if [ -f "$FINAL" ]; then
  echo "── ★vs 同链基线 (★不是 vs 官方板) ──"
  bash state/compare_arm_baseline.sh "$FINAL"
fi
exit 0
