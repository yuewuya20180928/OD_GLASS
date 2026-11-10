#!/usr/bin/env bash
# v76mq_arms.sh -- ★★★【单臂: 【三闸 + 走廊让路 (★`PCB_CORRIDOR_YIELD=1`★)】★★★】★★★
#
# ★★★★★**★为什么这条臂 (★2026-11-10 19:5x 实测决策)★★★★** ★★★
#   ★**实测 (`v76mo` 臂)**: ★**`BOOT_N` @ (63.60,11.04) 出不去 ⇒ 因为 `ID_DETECT_1` 的一根
#     (62.2,11.95)->(68.95,11.95) w=0.15 的直道【横在它的出脚口上方 0.91mm】**
#     ⇒ ★★**⇒ 而官方板那一带【一寸 F.Cu 走线都没有】⇒ ⇒ 官方板把整条走廊腾空了** ★★
#     ⇒ ★★★**★⇒ "让路"是一条【链】不是单点: ★让走 `ID_DETECT_0`, `ID_DETECT_1` 照样堵** ★★★
#     ⇒ ★★★**★⇒ 而【调优先网名单】只调"谁先走", ★管不到"这条走廊上挤着几个网" ⇒ ⇒ 那条路已实测双向关闭** ★★★
#   ★★**★⇒ 本臂的机制 (★走廊级, ★不是网级★)**: ★**出脚直道若会【站在别人的出脚口上】
#     ⇒ ⇒ 换方向/换长度 ⇒ ⇒ 把走廊让给对方** ★★
#     ⇒ ★★**⇒ 这是 `PAIR_AWARE_ROUTING_PLAN.md` "走廊优先"思路的【弱化版】(★不做成对, ★只做单走廊腾挪★)** ★★
#   ★**对照**: ★**`state/.lastgood/baseline_v76mj0_chain.kicad_pcb` (★同 env 闸关对照臂★)** ★★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

OUT0=/tmp/v76mq_R.kicad_pcb
LOG0=/tmp/v76mq_R.log
DRC0=/tmp/v76mq_R.drc.json


if [ -e "$OUT0" ] || [ -e "$LOG0" ]; then
  echo "  [v76mq 臂] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"
  exit 0
fi

echo "=== v76mq 成对臂: env = v76s8 (★连通性最好★) · 唯一变量 = PCB_MEANDER_EDGE ==="

# ---- ① 算预留串 (★两条臂共用同一个 ★防坐标过期★) ----
echo "── 算预留串 (plan_route_reserve.py) ──"
RESERVE=$(bash state/pcbnew_py.sh state/plan_route_reserve.py HW/PCB/demo_mainboard.kicad_pcb \
           --from-drc /tmp/v76rs_unc.drc.json 2>/dev/null \
           | grep -o 'PCB_ROUTE_RESERVE="[^"]*"' | head -1 | sed 's/PCB_ROUTE_RESERVE="//; s/"$//')
if [ -z "$RESERVE" ]; then
  echo "❌ 预留串没算出来 ⇒ 收工 (★别用空串开臂)"
  exit 3
fi
echo "  ✓ 预留串 = $RESERVE"
printf '%s\n' "$RESERVE" > "$PROJ/state/.lastgood/v76mq_reserve.txt"
echo "  ✓ 工具指纹 gen_pcb_routing.py sha256 = $(sha256sum state/gen_pcb_routing.py | cut -c1-16)"

# ---- ② 两条臂并行开跑 (★唯一差别 = PCB_MEANDER_EDGE★) ----
run_arm () {
  local _out="$1" _log="$2" _extra="$3"
  cd "$PROJ" || return 1
  env PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.0625 \
      PCB_BOARD_W=160 PCB_BOARD_H=100 \
      PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
      PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
      PCB_PAIR_EXEMPT_R=0.0 \
      PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 \
      PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
      PCB_PART_POS="R_SEL_D3_P:5.50,3.0;R_SEL_D3_N:7.95,3.0;R_SEL_D2_P:13.10,3.0;R_SEL_D2_N:15.55,3.0;R_SEL_CK_P:20.70,3.0;R_SEL_CK_N:23.15,3.0;R_SEL_D1_P:28.30,3.0;R_SEL_D1_N:30.75,3.0;R_SEL_D0_P:35.90,3.0;R_SEL_D0_N:38.35,3.0" \
      PCB_PAIR_BEFORE_PWR=1 PCB_PRIORITY_NETS="FSIN_OUT;LIGHT_5V;LIGHT_3V3;I2C_A_SCL;I2C_A_SDA;I2C_B_SCL;I2C_B_SDA;LED_G;LED_G_D;KEY_CAM;JTAG_TDI;SPI_SCLK_BOOT;SPI_MOSI_BOOT;SPI_MISO_BOOT;UART_RX;USB_CC2;BAT_DET;ID_DETECT_0;ID_DETECT_1;JTAG_TDO;JTAG_TMS;UART_TX;LED_B_D" PCB_W_MIN=0.15 \
      PCB_VIA_HALO_CENTER=1 PCB_MERGE_FIX=1 PCB_ESC_ROWNORM=2 \
      PCB_ROUTE_RESERVE="$RESERVE" PCB_PRIO_SPAN_SORT=1 \
      PCB_MEANDER_EDGE=1 \
      PCB_GND_ORPHAN_FIX=1 \
      PCB_CORRIDOR_YIELD=1 \
      PCB_ESC_CLR_FIX=1 \
      $_extra \
      PCB_OUT="$_out" \
      timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$_log" 2>&1
  echo "EXIT=$?" >> "$_log"
}

run_arm "$OUT0" "$LOG0" "" &
_PID0=$!
echo "  [v76mq 单臂 三个闸全开] PID=$_PID0"
echo "  ★两条臂并行 (★各自单线程 ⇒ 8 核机器扛得住★) ★"

# ---- ③ 等两条臂都跑完 (★最长 6 小时★) ----
while kill -0 "$_PID0" 2>/dev/null; do sleep 60; done
echo "=== 两条臂都跑完 ==="

for p in "$OUT0"; do
  if [ ! -f "$p" ]; then
    echo "❌ 没出板: $p ⇒ 收工 (看对应 log)"
    exit 2
  fi
done

# ---- ④ 板规则 min track width → 0.15 (★老板批准的规格; ★不改几何★) ----
fix_rule () {
  bash state/pcbnew_py.sh - "$1" <<'PY'
import pcbnew, sys
p = sys.argv[1]
b = pcbnew.LoadBoard(p)
if b is None:
    print("  ❌ 板读不出来"); raise SystemExit(1)
ds = b.GetDesignSettings()
ds.m_TrackMinWidth = int(0.15 * 1e6)
b.Save(p)
print("  ✓ 板规则 min track width → 0.15 :", p)
PY
}
echo "── 板规则 min track width → 0.15 (两条臂都做, ★保持一致★) ──"
fix_rule "$OUT0"

# ---- ⑤ fresh DRC (★两条臂都跑★) ----
echo "── fresh DRC ──"
bash state/kicad.sh pcb drc --output "$DRC0" --severity-error --severity-warning --format json "$OUT0" >/dev/null 2>&1
python3 - "$DRC0" <<'PY'
import json, sys, collections
def rep(p, tag):
    d = json.load(open(p, encoding="utf-8"))
    v = d.get("violations") or []
    kinds = collections.Counter()
    for it in v:
        kinds[it.get("type") or "?"] += 1
    unc = len(d.get("unconnected_items") or [])
    print("  %s: 走线违规=%d · unconnected=%d · %s"
          % (tag, len(v), unc, dict(kinds.most_common(8))))
    return len(v), unc, kinds.get("copper_edge_clearance", 0)
a = rep(sys.argv[1], "v76mq(三个闸全开)")
print("  ★★铜边违规 = %d (★v76mg1 是 0★)" % a[2])
PY

# ---- ⑥ 套【已校准的官方补丁链】 (★两条臂同一条链★) ----
echo "── 套已校准的官方补丁链 (臂A) ──"
bash state/replay_patch_chain.sh "$OUT0" v76mq
echo "  链 rc=$?"

FINAL0=/tmp/chain_v76mq/final_chain.kicad_pcb

# ---- ⑦ vs 同代码同 env 基线 (★臂A = 基线★) ----
if [ -f "$FINAL0" ]; then
  echo "── vs 同 env 闸关对照臂 (★baseline_v76mj0_chain★) ──"
  bash state/compare_arm_baseline.sh "$FINAL0" --baseline state/.lastgood/baseline_v76mj0_chain.kicad_pcb
  echo "  ★闸 rc=$?"
  echo "── vs 【同 env 少一个闸】的 v76mj1 (★★用来量 ESC_CLR_FIX 的净效果★★) ──"
  if [ -f /tmp/chain_v76mj1/final_chain.kicad_pcb ]; then
    bash state/compare_arm_baseline.sh "$FINAL0" --baseline /tmp/chain_v76mj1/final_chain.kicad_pcb
    echo "  ★闸 rc=$?"
  else
    echo "  ⚠️ v76mj1 终板还没出 ⇒ 跳过"
  fi
else
  echo "  ⚠️ 链没出终板 ⇒ 没法比 (查 /tmp/chain_v76mq)"
fi
echo "=== v76mq 成对臂全流程结束 $(date '+%F %T') ==="
