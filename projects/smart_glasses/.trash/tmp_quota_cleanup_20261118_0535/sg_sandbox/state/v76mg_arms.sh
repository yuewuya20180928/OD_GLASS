#!/usr/bin/env bash
# v76mg_arms.sh -- ★★★【成对臂: 【蛇形配平不许出板】闸 (`PCB_MEANDER_EDGE`) 在【连通性最好的 env】上的复验】★★★
#
# ★★★★★**★为什么要这条臂 (★2026-11-10 12:2x 实测决策)★★★★★ ★★★
#   ★**实测 (★v76me 成对臂已跑完, ★12:10★)**:
#     · 闸 **确实有效**: ★**铜边违规 4 → 0 · 总违规 6 → 2 · unconnected 51 → 51 (★零信号代价★)**
#     · ★**但臂的 env 是【连通性最差的那一档】** (★v76b1 系: unc 35 条 / 33 网名★)
#   ★★**⇒ 闸已证明有效 ⇒ 下一步不是【再证明一次】, 而是【把闸装到【最好的 env】上】★★** ★★
#     ★**连通性最好的 env = `v76s8`** (★HALO_MARGIN=0.0625 + ESC_ROWNORM=2★):
#       ★★**unc 25 条 / 23 个网名 (★全项目最好★)** ⇒ ★**比基线 46 条 / 42 网名好一大截** ★★
#       ★★**但 DRC 29 (★25 条铜边 + 4 条擦边净距★) ⇒ ⇒ 闸装上去 ⇒ 期望 DRC 29 → 4** ★★
#   ★★**⇒ 本臂 = 【同 env 成对】, 唯一变量 = `PCB_MEANDER_EDGE` (★A 关 / B 开★)**
#     ★★**⇒ 臂 A 顺带就是【同代码同 env 的新基线】(★老基线作废 ⇒ 必须重建, ★MEMORY 铁律★)** ★★
#
# ★**判据 (★全部用已落地的统一尺子★)**:
#   ① **头号指标**: `copper_edge_clearance` 违规数 ⇒ ★**闸开 ⇒ 必须 0 (★v76me 已实测闸关 4 → 闸开 0★)★**
#   ② **不许拿信号换地**: unc 网名集合不许变大 · GND 未连接不许变多
#   ③ **名单制闸**: `state/compare_arm_official.py` (★退铜名单 / 差分死腿 / 逐网孤岛不许变多★)
#   ④ **官方板全程只读** (md5 611b869e / mtime 11-06 07:07:17)
#
# ★**env 来源**: ★**`v76s8_arms.sh` 逐位相同** (★只多一个 `PCB_MEANDER_EDGE=1`★)
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

OUT0=/tmp/v76mg0_R.kicad_pcb
LOG0=/tmp/v76mg0_R.log
OUT1=/tmp/v76mg1_R.kicad_pcb
LOG1=/tmp/v76mg1_R.log
DRC0=/tmp/v76mg0_R.drc.json
DRC1=/tmp/v76mg1_R.drc.json

if [ -e "$OUT0" ] || [ -e "$LOG0" ] || [ -e "$OUT1" ] || [ -e "$LOG1" ]; then
  echo "  [v76mg 臂] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"
  exit 0
fi

echo "=== v76mg 成对臂: env = v76s8 (★连通性最好★) · 唯一变量 = PCB_MEANDER_EDGE ==="

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
printf '%s\n' "$RESERVE" > "$PROJ/state/.lastgood/v76mg_reserve.txt"
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
      $_extra \
      PCB_OUT="$_out" \
      timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$_log" 2>&1
  echo "EXIT=$?" >> "$_log"
}

run_arm "$OUT0" "$LOG0" "" &
_PID0=$!
run_arm "$OUT1" "$LOG1" "PCB_MEANDER_EDGE=1" &
_PID1=$!
echo "  [臂A 对照 闸关] PID=$_PID0   [臂B 候选 闸开] PID=$_PID1"
echo "  ★两条臂并行 (★各自单线程 ⇒ 8 核机器扛得住★) ★"

# ---- ③ 等两条臂都跑完 (★最长 6 小时★) ----
while kill -0 "$_PID0" 2>/dev/null || kill -0 "$_PID1" 2>/dev/null; do sleep 60; done
echo "=== 两条臂都跑完 ==="

for p in "$OUT0" "$OUT1"; do
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
fix_rule "$OUT1"

# ---- ⑤ fresh DRC (★两条臂都跑★) ----
echo "── fresh DRC ──"
bash state/kicad.sh pcb drc --output "$DRC0" --severity-error --severity-warning --format json "$OUT0" >/dev/null 2>&1
bash state/kicad.sh pcb drc --output "$DRC1" --severity-error --severity-warning --format json "$OUT1" >/dev/null 2>&1
python3 - "$DRC0" "$DRC1" <<'PY'
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
a = rep(sys.argv[1], "臂A(闸关)")
b = rep(sys.argv[2], "臂B(闸开)")
print("  ★★头号指标 (copper_edge_clearance): 闸关 %d → 闸开 %d ⇒ %s"
      % (a[2], b[2], ("✅ 降了 %d 条" % (a[2]-b[2])) if b[2] < a[2] else ("❌ 没降 (还多了)" if b[2] > a[2] else "➖ 持平")))
print("  ★总违规: 闸关 %d → 闸开 %d · unconnected: %d → %d" % (a[0], b[0], a[1], b[1]))
PY

# ---- ⑥ 套【已校准的官方补丁链】 (★两条臂同一条链★) ----
echo "── 套已校准的官方补丁链 (臂A) ──"
bash state/replay_patch_chain.sh "$OUT0" v76mg0
echo "  链A rc=$?"
echo "── 套已校准的官方补丁链 (臂B) ──"
bash state/replay_patch_chain.sh "$OUT1" v76mg1
echo "  链B rc=$?"

FINAL0=/tmp/chain_v76mg0/final_chain.kicad_pcb
FINAL1=/tmp/chain_v76mg1/final_chain.kicad_pcb

# ---- ⑦ vs 同代码同 env 基线 (★臂A = 基线★) ----
if [ -f "$FINAL0" ] && [ -f "$FINAL1" ]; then
  echo "── vs 同代码同 env 基线 (★臂A 对照 = 基线★) ──"
  bash state/compare_arm_baseline.sh "$FINAL1" --baseline "$FINAL0"
  echo "  ★闸 rc=$?"
  echo "── 归档基线 (★给后面的臂用★) ──"
  # ★★★★★★2026-11-10 15:0x 【★归档必须连【.kicad_pro】一起拷★】★★★★★★
  #   ★**实测踩到的坑 (★不是猜★)**: ★**只拷 .kicad_pcb ⇒ 归档基线的旁边没有 .kicad_pro**
  #     ⇒ ★**KiCad 读不到 min_track_width=0.15 ⇒ 回落到默认 0.20 ⇒ ⇒ fresh DRC 多出 132 条假 `track_width`**
  #     ⇒ ★★**⇒ 归档基线的 DRC 读数变成 161 (★真值是 29★) ⇒ ⇒ 闸门拿一个【假基线】在比 ★★**
  #     ⇒ ★★**⇒ 这就是"读数纪律"要防的东西: ★【同一块板 md5 相同, DRC 读数却差 132 条】★★**
  #   ★**修法**: ★**连 .kicad_pro / .kicad_prl 一起拷** ⇒ ⇒ 归档基线与原始终板【读数逐位一致】★
  cp -f "$FINAL0" "$PROJ/state/.lastgood/baseline_v76mg0_chain.kicad_pcb" 2>/dev/null && \
    cp -f "${FINAL0%.kicad_pcb}.kicad_pro" "$PROJ/state/.lastgood/baseline_v76mg0_chain.kicad_pro" 2>/dev/null && \
    cp -f "${FINAL0%.kicad_pcb}.kicad_prl" "$PROJ/state/.lastgood/baseline_v76mg0_chain.kicad_prl" 2>/dev/null && \
    echo "  ✓ 已归档 state/.lastgood/baseline_v76mg0_chain.kicad_pcb (+ .kicad_pro/.kicad_prl)"
else
  echo "  ⚠️ 链没出终板 ⇒ 没法比 (查 /tmp/chain_v76mg0 / /tmp/chain_v76mg1)"
fi
echo "=== v76mg 成对臂全流程结束 $(date '+%F %T') ==="
