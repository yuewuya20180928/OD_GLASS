#!/usr/bin/env bash
# v76s1_arms.sh -- ★★★【★★单变量臂: ★v76ru env 逐位相同 + ★唯一变量 = `PCB_GND_ESC_FIX=1` (★修 GND 下拉孔绕过逃逸走廊的 bug)★★★】★★ ★★★
#
# ★★**★唯一变量 (★2026-11-10 03:0x 实测出来的)★★** ★★★
#   ★**实测根因**: ★**GND 下拉孔【不落焊盘周围的环格】, 而是落 `escape_stub()` 出脚直道的末端 (anchor)**
#     ⇒ ⇒ 而 `escape_stub` 只查 `_stub_clear`/`_stub_vs_routed` ⇒ ⇒ ★**不查 `_gnd_drop_esc_ok`**
#     ⇒ ⇒ ★**"连接器差分脚逃逸走廊"规则只在环格路径上生效 ⇒ ⇒ 最常见的路径绕过了它** ★★
#   ★**实测代价 (v76ru 终板)**: ★**7 个 CONN_CAM 的 GND 下拉孔违反 [Δy ≥ 4.0mm] (★实际 0.9 / 1.2mm★)**
#     ⇒ ★**其中 4 个直接卡死 A2 那 5 条的端点**: ★`CONN_CAM.13`→`CSI_D0_D1_P`/`CSI_D0_D0_N`
#       · `CONN_CAM.16`→`CSI_D0_CK_N` · `CONN_CAM.19`→`CSI_MCLK` · `CONN_CAM.21`→`I2C_A_SCL` ★★
#   ★**修法**: ★**anchor 违规 ⇒ 改走"长出脚" (★沿垂直方向走到 |Δy| ≥ MIN★) ⇒ 不行就落回环格路径** ★★
#   ★**⇒ env 门控 `PCB_GND_ESC_FIX` (★默认关 ⇒ 逐位不变★) · 自测 `state/_test_gnd_esc_fix.py` 8 条断言全过★**
#
# ★★**★判据风险 (★必须一起看, ★否则会把"救回信号"看成"净负"★)★★** ★★★
#   ★**这个修法可能让某些 GND 焊盘【失去下拉孔】(★长出脚找不到合规落点 ⇒ 落回环格 ⇒ 也可能失败★)**
#   ★⇒ ⇒ ★**必须同时看【GND 类未连接数有没有变多】⇒ 变多 ⇒ 就是拿信号换地 ⇒ 不算赢** ★★
#
# ★v76s1_arms.sh -- ★★★【★★并集臂: ★v76rp env (成对预留+PRIO_SPAN_SORT) + ★--from-drc 57 框 + 板规则0.15★★★】 ★★★【成对预留 + 优先网按跨距排序 臂】: v76rr env 逐位相同 + ★2 处机制修复 ★★★
#
# ★★★★**★为什么是这条 (★2026-11-09 19:4x 老板批准 0.15mm 之后)★★★★** ★★★
#   ★**老板批准**: ★**"按常规的硬件电路图的线宽来做, demo 板指标不用卡得太死"** ⇒ ★**0.15mm (6mil) 已定为设计线宽** ★★★
#   ★**① 本臂 = v76fam env 逐位相同 + 只多 `PCB_ROUTE_RESERVE`** ⇒ ★**干净 A/B** ★★
#   ★**② 板规则 min track width 0.20 ⇒ 0.15** (★老板批的规格; ★**对官方板零影响, ★它没有 0.15mm 走线**)
#      ⇒ ★★**否则这臂会带 176~182 条 track_width 假违规** (★板规则说 0.2, ★臂画了 0.15) ⇒ ★★**改完 ⇒ 几何零违规** ★★
#   ★**③ `PCB_ROUTE_RESERVE`**: ★**给 A1 那 5 条 N 腿留出脚走廊** (★实测: 它们的反向道都被别的网占着)
#      ⇒ ★★**关键: 预留框在 `__init__` 末尾就生效 ⇒ ★P 铺铜时就被挡开 ⇒ ★P 自动走另一侧
#      ⇒ ★★**⇒ 而 N 侧本来就有 `esc_avoid = P 用过的方向` ⇒ ⇒ 两条机制自动配合 ⇒ ⇒ 不用改 `route_diff_pair`** ★★
#   ★**④ 预留串不硬编码** ⇒ ★**启动时用 `state/plan_route_reserve.py` 按当前板实测算出** (★防坐标过期)
#
# ★★★★★**★本臂两处机制修复 (★全部实测依据, ★不是拍脑袋)★★★★** ★★★
#   ★**① 成对预留 (★`PCB_ROUTE_RESERVE` 支持 `N+P` 语法)**: ★**v76rr 实测** ⇒ 预留框 0.9mm 宽
#     ⇒ 必盖住 0.4mm pitch 的伙伴焊盘 ⇒ ★**单网预留把伙伴腿打死** (★`CSI_D0_D3_P_SRC` 46 段⇒0 段)
#     ⇒ ★**⇒ 一个框同时留给 P+N** ★★
#   ★**② 优先网按跨距排序 (★`PCB_PRIO_SPAN_SORT=1`)**: ★**v76rr 实测** ⇒ `JTAG_TDO` 被 `JTAG_TDI` 的铜挡 0.213mm
#     ⇒ ★**同族内部谁先布谁赢** ⇒ 而优先名单是人写的顺序 ⇒ 等于抽签
#     ⇒ ★**⇒ 优先网内部按跨距降序 (★与第 4 阶段同口径) ⇒ 复现基线里已验证的好顺序** ★★
#
# ★**读数与判据**: ★**出臂 → fresh DRC → 套已校准的官方补丁链 → vs `state/.lastgood/baseline_v76_chain.kicad_pcb`**
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

OUT=/tmp/v76s1_R.kicad_pcb
LOG=/tmp/v76s1_R.log
DRC=/tmp/v76s1_R.drc.json

echo "=== v76s1 臂: v76rr + ★成对预留(P+N) + ★优先网按跨距排序 ★ ==="

# ---- ① 算预留串 (★按官方板实测 ⇒ 坐标不硬编码) ----
echo "── 算预留串 (plan_route_reserve.py) ──"
RESERVE=$(bash state/pcbnew_py.sh state/plan_route_reserve.py HW/PCB/demo_mainboard.kicad_pcb \
           --from-drc /tmp/v76rs_unc.drc.json 2>/dev/null \
           | grep -o 'PCB_ROUTE_RESERVE="[^"]*"' | head -1 | sed 's/PCB_ROUTE_RESERVE="//; s/"$//')
if [ -z "$RESERVE" ]; then
  echo "❌ 预留串没算出来 ⇒ 收工 (★别用空串开臂)"
  exit 3
fi
echo "  ✓ 预留串 = $RESERVE"
echo "  ✓ 工具指纹 plan_route_reserve.py sha256 = $(sha256sum state/plan_route_reserve.py | cut -c1-16)"
echo "  ✓ 工具指纹 gen_pcb_routing.py    sha256 = $(sha256sum state/gen_pcb_routing.py  | cut -c1-16)"
echo "  ✓ 唯一变量 = PCB_GND_ESC_FIX=1 (★--from-drc 输入 /tmp/v76rs_unc.drc.json 与 v76ru 同 ★)"

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
      PCB_VIA_HALO_CENTER=1 PCB_GND_ESC_FIX=1 \
      PCB_ROUTE_RESERVE="$RESERVE" PCB_PRIO_SPAN_SORT=1 \
      PCB_OUT="$OUT" \
      timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$LOG" 2>&1
  echo "EXIT=$?" >> "$LOG"
) &
_PID=$!
echo "  [v76s1 臂] PID=$_PID"

while kill -0 "$_PID" 2>/dev/null; do sleep 60; done
echo "=== 第①步结束 ==="
if [ ! -f "$OUT" ]; then
  echo "❌ 没出板 ⇒ 收工 (看 $LOG)"; exit 2
fi

# ---- ② 板规则 min track width 0.20 ⇒ 0.15 (★老板批准的规格; ★不改几何, ★只让 0.15mm 走线合法) ----
echo "── 板规则 min track width → 0.15 (★老板批准的规格) ──"
bash state/pcbnew_py.sh - "$OUT" <<'PY'
import pcbnew, sys
p = sys.argv[1]
b = pcbnew.LoadBoard(p)
if b is None:
    print("  ❌ 板读不出来"); raise SystemExit(1)
ds = b.GetDesignSettings()
print("  改前 m_TrackMinWidth =", ds.m_TrackMinWidth / 1e6, "mm")
ds.m_TrackMinWidth = int(0.15 * 1e6)
b.Save(p)
print("  ✓ 改为 0.15 ⇒", p)
PY

echo "── 板规则 min track width → 0.15 (★老板批准的规格; ★否则 0.15mm 走线全是假违规) ──"
bash state/pcbnew_py.sh - "$OUT" <<'PY'
import pcbnew, sys
p = sys.argv[1]
b = pcbnew.LoadBoard(p)
if b is None:
    print("  ❌ 板读不出来"); raise SystemExit(1)
ds = b.GetDesignSettings()
print("  改前 m_TrackMinWidth =", ds.m_TrackMinWidth / 1e6, "mm")
ds.m_TrackMinWidth = int(0.15 * 1e6)
b.Save(p)
print("  ✓ 改为 0.15 ⇒", p)
PY

echo "── 裸板读数 ──"
echo "  走线 = $(grep -ac '(segment' "$OUT") · 过孔 = $(grep -ac '(via' "$OUT")"
bash state/kicad.sh pcb drc --output "$DRC" --severity-error --severity-warning --format json "$OUT" >/dev/null 2>&1
python3 - "$DRC" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
print("  DRC违规 = %d · unconnected = %d" % (len(d.get("violations") or []), len(d.get("unconnected_items") or [])))
PY

echo "── 套【已校准的官方补丁链】 ──"
bash state/replay_patch_chain.sh "$OUT" v76s1
echo "  链 rc=$?"

echo "── vs 同链基线 (★不是 vs 官方板) ──"
FINAL="/tmp/chain_v76s1/final_chain.kicad_pcb"
if [ -f "$FINAL" ]; then
  bash state/compare_arm_baseline.sh "$FINAL"
else
  echo "  ⚠️ 链没出终板 ⇒ 没法比"
fi
exit 0
