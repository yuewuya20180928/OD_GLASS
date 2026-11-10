#!/usr/bin/env bash
# v76ml_arms.sh -- ★★★【单臂: 【三个闸全开】(★板边闸 + GND 孤儿铜闸 + 出脚离网格净距闸★)★】★★★
#
# ★★★★★**★为什么这条臂 (★2026-11-10 15:4x 实测决策)★★★★** ★★★
#   ★**三个闸各自的实测凭证 (★都是真臂/真跑, 不是推断★)**:
#     ① `PCB_MEANDER_EDGE=1` (★蛇形板边闸★): ★**v76mg 成对臂 ⇒ 板边违规 25→0, 总 DRC 29→6, unc 零代价** ★★
#     ② `PCB_GND_ORPHAN_FIX=1` (★GND 孤儿铜闸★): ★**端到端 ⇒ 重复直道 316→0 条, GND 有铜 94/94 一致** ★★
#        ★**且实测它把 unc 从 48 拉回 43 (★-5★) ⇒ ⇒ 孤儿铜确实在堵路** ★★
#     ③ `PCB_ESC_CLR_FIX=1` (★出脚离网格净距闸★): ★**15:3x 实测 ⇒ v76mg1 终板那 6 条 clearance
#        【全部是离网格的 45° 出脚斜线】(★扫出的网对完全覆盖 DRC 报的每一个网对★) ⇒ ⇒ 这个闸专治它们** ★★
#   ★★**⇒ 本臂 = 三个闸叠加, ★目标是 DRC 6 → 0, 且 unc 保持 25 条/23 网名 (★v76mg1 那一档★)** ★★
#   ★**对照**: ★**`state/.lastgood/baseline_v76mj0_chain.kicad_pcb` (★同 env 闸关对照臂★)** ★★
#   ★★**★注意 (★2026-11-10 15:4x 记录★)**: ★★**本臂的 `gen_pcb_routing.py` 指纹与 `v76mj` 那两条不同**
#     (★v76mj 起跑时还没加 `PCB_ESC_CLR_FIX`★) ⇒ ★**但那个闸默认关 ⇒ 行为逐位不变 ⇒ 不影响可比性** ★★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

OUT0=/tmp/v76ml_R.kicad_pcb
LOG0=/tmp/v76ml_R.log
DRC0=/tmp/v76ml_R.drc.json


if [ -e "$OUT0" ] || [ -e "$LOG0" ]; then
  echo "  [v76ml 臂] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"
  exit 0
fi

echo "=== v76ml 成对臂: env = v76s8 (★连通性最好★) · 唯一变量 = PCB_MEANDER_EDGE ==="

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
printf '%s\n' "$RESERVE" > "$PROJ/state/.lastgood/v76ml_reserve.txt"
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
      PCB_ESC_CLR_FIX=1 \
      $_extra \
      PCB_OUT="$_out" \
      timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$_log" 2>&1
  echo "EXIT=$?" >> "$_log"
}

run_arm "$OUT0" "$LOG0" "" &
_PID0=$!
echo "  [v76ml 单臂 三个闸全开] PID=$_PID0"
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

# ★★★★★★【★铁律: 要跑 DRC 的板, 同目录【必须】有 .kicad_pro ★★★★★★】★★★★★★
#   ★**2026-11-11 00:2x 实测踩到 (★不是猜★)**: ★**臂A 的裸板旁没有 .kicad_pro ⇒
#   KiCad 退回【默认 min_width 0.20mm】⇒ 0.15mm 走线全成【假 track_width 违规】(实测 87 条)★**
#   ⇒ ★**⇒ 缺 .kicad_pro 的 DRC 读数一律作废** ⇒ ⇒ 【每条臂的裸板/终板, 同目录都必须放工程文件★】
#   ★★**且它会伪装成"臂变差了"(★我一度据此误判"默认关⇒逐位不变"失效★)⇒ ★★必须先补齐再读数★**
ensure_pro () {
  local p="$1"
  local pro="${p%.kicad_pcb}.kicad_pro"
  if [ ! -f "$pro" ]; then
    cp -f "$PROJ/HW/PCB/demo_mainboard.kicad_pro" "$pro" 2>/dev/null || \
    cp -f "$PROJ/state/.lastgood/baseline_v76me0_chain.kicad_pro" "$pro" 2>/dev/null || true
    echo "  ✓ 已补 .kicad_pro (★规则同源·否则 DRC 假违规★): $pro"
  fi
}
ensure_pro "$OUT0"

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
a = rep(sys.argv[1], "v76ml(三个闸全开)")
print("  ★★铜边违规 = %d (★v76mg1 是 0★)" % a[2])
PY

# ---- ⑥ 套【已校准的官方补丁链】 (★两条臂同一条链★) ----
echo "── 套已校准的官方补丁链 (臂A) ──"
bash state/replay_patch_chain.sh "$OUT0" v76ml
echo "  链 rc=$?"

FINAL0=/tmp/chain_v76ml/final_chain.kicad_pcb

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
  echo "  ⚠️ 链没出终板 ⇒ 没法比 (查 /tmp/chain_v76ml)"
fi
echo "=== v76ml 成对臂全流程结束 $(date '+%F %T') ==="
