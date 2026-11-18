#!/usr/bin/env bash
# v76s7_arms.sh -- ★★★【★★单变量臂: ★相对【v76s2】只差 `PCB_MERGE_FIX=1` (★共线合并瞬移 bug 的修法★)★★★】★★ ★★★
#
# ★★**★为什么是这条 (★2026-11-10 04:4x 实测)★★** ★★★
#   ★**v76s2 实测**: ★**unc 26 (★当前最佳总数★)** · 零铜 8 · 差分单边 3 · 但 ★**DRC 13** ★
#     ⇒ ★**其中 12 条是 `copper_edge_clearance` (actual 0.0000mm) ⇒ 根因 = 共线合并的"瞬移"bug** ★
#     ⇒ ★★**⇒ 修它 ⇒ 12 条板边违规应全部消失 ⇒ unc 26 就可能过 DRC 闸** ★★
#   ★**唯一变量**: ★`PCB_MERGE_FIX=1` (★修对 `by` 的坐标错位 + 三角不等式兜底★)
#     ★**默认关 ⇒ 既有臂逐位不变** ★ · 自测 `state/_test_merge_fix.py` (★10 条断言全过★)
#
# ★★**★为什么是这条 (★2026-11-10 03:2x 三个硬证据凑齐了)★★★** ★★★
#   ★**证据① (★物理层★)**: ★**`state/probe_escape_feasibility.py` 实测 ⇒ 70 个未连接端点,
#     ★**在 W=0.20 和 W=0.15 下【全部物理可行】(★0 个不可能★) ⇒ ⇒ "等板厂"这个结论不成立** ★★
#   ★**证据② (★日志层★)**: ★**v76ru 日志: `[RIPUP] 收尾: 尝试 27 个失败网 ⇒ 重布成功 0 个`
#     ★★**且每个失败网平均只差 1~3 个脚 (★如 `I2C_B_SDA` 已布 69.7mm 只差 2 脚★) ⇒ ⇒ 全是"差一点"** ★★
#   ★★**证据③ (★代码层★)**: ★**`GRID = 0.25` mm 是写死的常量 ⇒ ⇒ 0.4mm pitch 的 BTB 区域只有 1~2 格
#     ⇒ ⇒ 密集区【没有足够细的格子可走】⇒ ⇒ ⇒ 【"密集区无路可走"是最可能的真凶】** ★★
#   ★★**⇒ halo 余量是【把可走空间还回去】的最便宜旋钮 (★现成 env, ★零代码★)** ★★
#   ★**为什么选 0.0625**: ★**MEMORY 实测: 0.0625 是下限 (★再降到 0 ⇒ 11 条 clearance 违规★)
#     ⇒ ★**⇒ 这条路有实测边界, 不是瞎试** ★★
#
# ★★**★本臂的风险 (★必须一起看★)★★** ★★★
#   ★**halo 变小 ⇒ 【更多格被判可走】⇒ ⇒ 净距可能不达标 ⇒ ⇒ 【必须看 fresh DRC】(★旧同名 json 会误报★) ★★
#   ★**⇒ 若 DRC 变红 ⇒ ⇒ 说明 0.0625 太松 ⇒ ⇒ 那就得走【更细网格】(★更贵: 4× 内存/时间★)★★
#
# ★v76s7_arms.sh -- ★★★【★★并集臂: ★v76rp env (成对预留+PRIO_SPAN_SORT) + ★--from-drc 57 框 + 板规则0.15★★★】 ★★★【成对预留 + 优先网按跨距排序 臂】: v76rr env 逐位相同 + ★2 处机制修复 ★★★
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

OUT=/tmp/v76s7_R.kicad_pcb
LOG=/tmp/v76s7_R.log
DRC=/tmp/v76s7_R.drc.json

echo "=== v76s7 臂: v76rr + ★成对预留(P+N) + ★优先网按跨距排序 ★ ==="

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
echo "  ✓ 唯一变量 = PCB_MERGE_FIX=1 (★相对 v76s2 只差这个★; --from-drc 输入与 v76ru 同 ★)"

(
  cd "$PROJ"
  env PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.0625 \
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
      PCB_OUT="$OUT" \
      timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$LOG" 2>&1
  echo "EXIT=$?" >> "$LOG"
) &
_PID=$!
echo "  [v76s7 臂] PID=$_PID"

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
bash state/replay_patch_chain.sh "$OUT" v76s7
echo "  链 rc=$?"

echo "── vs 同链基线 (★不是 vs 官方板) ──"
FINAL="/tmp/chain_v76s7/final_chain.kicad_pcb"
if [ -f "$FINAL" ]; then
  bash state/compare_arm_baseline.sh "$FINAL"
else
  echo "  ⚠️ 链没出终板 ⇒ 没法比"
fi
exit 0
