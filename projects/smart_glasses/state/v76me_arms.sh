#!/usr/bin/env bash
# v76me_arms.sh -- ★★★【成对臂: 【蛇形配平不许出板】闸 (`PCB_MEANDER_EDGE`) 的【单变量】实测】★★★
#
# ★★★★**★为什么要成对 (★2026-11-10 11:1x 实测决定)★★★★**
#   ★**实测**: `state/gen_pcb_routing.py` 的 mtime = **11-10 10:04** ⇒ ★**比今天 06:50 跑完的 v76b1 臂新**
#     ⇒ ★★**v76b1 那块板不能当本臂的基线** (★代码已变 ⇒ 不是单变量 ⇒ 差异全是"代码差"不是"闸的功劳")★★
#   ★★**⇒ 本脚本同代码同 env 跑两条臂: 唯一差别 = `PCB_MEANDER_EDGE` 开/关 ⇒ 差异才是闸的功劳** ★★
#   ★★**臂 A (`v76me0`) = 对照组 (闸关) · 臂 B (`v76me1`) = 候选 (闸开) ★★
#
# ★**env 来源**: ★**v76b1_arms.sh 逐位相同** (★`PCB_W_MIN=0.15` + ★`PCB_MERGE_FIX=1` + ★成对预留 + ★PRIO_SPAN_SORT ★)
#   ⇒ ★**两条臂的 env 完全一致, 只差 `PCB_MEANDER_EDGE=1` 一项** ★★
#
# ★**判据 (★全部用已落地的统一尺子★)**:
#   ① **头号指标**: `copper_edge_clearance` 违规数 ⇒ ★**闸开 ⇒ 必须显著下降** (★v76b1 实测 4~29 条全来自蛇形凸起★)
#   ② **不许拿信号换地**: unc 网名集合不许变大 · GND 未连接不许变多 (★`compare_arm_baseline.sh` 里的 ①/①b/①c★)
#   ③ **名单制闸**: `state/compare_arm_official.py` (★只看"变好"的指标: unc / 零铜网数★)
#   ④ **差分死腿不许新增** + **单边零铜对不许新增**
#   ⑤ **官方板全程只读** (md5 611b869e / mtime 11-06 07:07:17)
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

OUT0=/tmp/v76me0_R.kicad_pcb
LOG0=/tmp/v76me0_R.log
OUT1=/tmp/v76me1_R.kicad_pcb
LOG1=/tmp/v76me1_R.log
DRC0=/tmp/v76me0_R.drc.json
DRC1=/tmp/v76me1_R.drc.json
ARMS_LOG=/tmp/v76me_arms.log

if [ -e "$OUT0" ] || [ -e "$LOG0" ] || [ -e "$OUT1" ] || [ -e "$LOG1" ]; then
  echo "  [v76me 臂] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"
  exit 0
fi

echo "=== v76me 成对臂: 唯一变量 = PCB_MEANDER_EDGE (A 关 / B 开) ==="
echo "  A(对照) → $OUT0   B(候选) → $OUT1"

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
echo "  ✓ 预留串 ⇒ 落盘 $PROJ/state/.lastgood/v76me_reserve.txt"
printf '%s\n' "$RESERVE" > "$PROJ/state/.lastgood/v76me_reserve.txt"

# ---- ② 两条臂并行开跑 (★唯一差别 = PCB_MEANDER_EDGE★) ----
run_arm () {
  local _out="$1" _log="$2" _extra="$3"
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
        PCB_PAIR_BEFORE_PWR=1 PCB_PRIORITY_NETS="FSIN_OUT;LIGHT_5V;LIGHT_3V3;I2C_A_SCL;I2C_A_SDA;I2C_B_SCL;I2C_B_SDA;LED_G;LED_G_D;KEY_CAM;JTAG_TDI;SPI_SCLK_BOOT;SPI_MOSI_BOOT;SPI_MISO_BOOT;UART_RX;USB_CC2;BAT_DET;ID_DETECT_0;ID_DETECT_1;JTAG_TDO;JTAG_TMS;UART_TX;LED_B_D" PCB_W_MIN=0.15 \
        PCB_VIA_HALO_CENTER=1 PCB_MERGE_FIX=1 \
        PCB_ROUTE_RESERVE="$RESERVE" PCB_PRIO_SPAN_SORT=1 \
        $_extra \
        PCB_OUT="$_out" \
        timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > "$_log" 2>&1
    echo "EXIT=$?" >> "$_log"
  ) &
  echo $!
}

_PID0=$(run_arm "$OUT0" "$LOG0" "")
_PID1=$(run_arm "$OUT1" "$LOG1" "PCB_MEANDER_EDGE=1")
echo "  [臂A 对照] PID=$_PID0   [臂B 候选] PID=$_PID1"
echo "  ★两条臂并行 (★各自单线程 ⇒ 8 核机器扛得住) ★"

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

# ---- ⑤ fresh DRC (★两条臂都跑, ★顺带数【蛇形板边违规】条数★) ----
echo "── fresh DRC ──"
bash state/kicad.sh pcb drc --output "$DRC0" --severity-error --severity-warning --format json "$OUT0" >/dev/null 2>&1
bash state/kicad.sh pcb drc --output "$DRC1" --severity-error --severity-warning --format json "$OUT1" >/dev/null 2>&1
python3 - "$DRC0" "$DRC1" <<'PY'
import json, sys, collections
def rep(p, tag):
    d = json.load(open(p, encoding="utf-8"))
    v = d.get("violations") or []
    kinds = collections.Counter()
    edge = []
    for it in v:
        t = it.get("type") or "?"
        kinds[t] += 1
        if "edge" in str(t).lower() or "edge" in str(it.get("description", "")).lower():
            edge.append(it)
    unc = len(d.get("unconnected_items") or [])
    print("  %s: 走线违规=%d · unconnected=%d · copper_edge_clearance=%d"
          % (tag, len(v), unc, kinds.get("copper_edge_clearance", 0)))
    print("      违规类型分布: %s" % dict(kinds.most_common(8)))
    return len(v), unc, kinds.get("copper_edge_clearance", 0)
a = rep(sys.argv[1], "臂A(闸关)")
b = rep(sys.argv[2], "臂B(闸开)")
print("  ★★头号指标 (copper_edge_clearance): 闸关 %d → 闸开 %d ⇒ %s"
      % (a[2], b[2], ("✅ 降了 %d 条" % (a[2]-b[2])) if b[2] < a[2] else ("❌ 没降 (还多了)" if b[2] > a[2] else "➖ 持平")))
print("  ★总违规: 闸关 %d → 闸开 %d · unconnected: %d → %d" % (a[0], b[0], a[1], b[1]))
PY

# ---- ⑥ 套【已校准的官方补丁链】 (★两条臂同一条链★) ----
echo "── 套已校准的官方补丁链 (臂A) ──"
bash state/replay_patch_chain.sh "$OUT0" v76me0
echo "  链A rc=$?"
echo "── 套已校准的官方补丁链 (臂B) ──"
bash state/replay_patch_chain.sh "$OUT1" v76me1
echo "  链B rc=$?"

FINAL0=/tmp/chain_v76me0/final_chain.kicad_pcb
FINAL1=/tmp/chain_v76me1/final_chain.kicad_pcb

# ---- ⑦ vs 同代码同 env 基线 (★臂A = 基线★) ----
if [ -f "$FINAL0" ] && [ -f "$FINAL1" ]; then
  echo "── vs 同代码同 env 基线 (★臂A 对照 = 基线★) ──"
  bash state/compare_arm_baseline.sh "$FINAL1" --baseline "$FINAL0"
  echo "  ★闸 rc=$?"
  echo "── 归档基线 (★给后面的臂用★) ──"
  cp -f "$FINAL0" "$PROJ/state/.lastgood/baseline_v76me0_chain.kicad_pcb" 2>/dev/null && \
    echo "  ✓ 已归档 state/.lastgood/baseline_v76me0_chain.kicad_pcb"
else
  echo "  ⚠️ 链没出终板 ⇒ 没法比 (查 /tmp/chain_v76me0 / /tmp/chain_v76me1)"
fi
echo "=== v76me 成对臂全流程结束 $(date '+%F %T') ==="
