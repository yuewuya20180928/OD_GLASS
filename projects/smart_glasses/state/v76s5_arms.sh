#!/usr/bin/env bash
# v76s5_arms.sh -- ★★★【★★单变量臂: ★v76ru env 逐位相同 + ★唯一变量 = `PCB_ESC_STRAIGHT=2` (★2026-11-10 04:2x 新机制★)★★★】★★ ★★★
#
# ★★**★唯一变量 (★2026-11-10 04:2x 实测几何推导, ★不是猜★)★★** ★★★
#   ★**机制: "出脚后必须先直行" (★env 门控 `PCB_ESC_STRAIGHT`, ★默认 0 = 关 ⇒ 逐位不变★)**
#   ★★**实测根因 (★v76ru 终板上量到的坐标, ★不是理论★)★★**:
#     · `CSI_D0_D0_P_SRC` 出脚直道 (21.600,50.960)->(21.600,52.160) w=0.15
#     · 紧接着 (21.600,52.160)->(21.950,52.450) w=0.25  ★**出脚后立刻 45° 斜切**★
#     · ⇒ 该斜线与邻居 `CSI_D0_D0_N_SRC` 出脚道 (x=22.000 竖线, 顶端 52.160) 的**垂距 = 0.255mm**
#       而 [邻居半宽 0.075 + 自己半宽 0.125 + 净距 0.20 + 余量 0.025] = **0.425mm** ⇒ **差 0.17mm**
#     · ⇒ ★★**N 的唯一出脚方向被判死 ⇒ N 腿 L=0.00 (连出脚都没成功)** ★★
#   ★**解法 (纯几何)**: ★**出脚后先沿出脚方向直行** ⇒ 垂距 = 0.255 + 0.77×h
#     ⇒ h=0.5mm (0.25 网格 2 格) ⇒ 0.64mm ⇒ ★解封★
#   ★**兜底**: ★约束下 A* 无路 ⇒ 自动回退无约束重试 ⇒ ★保证不比现状更差★
#   ★**自测**: ★`state/_test_esc_straight.py` (★14 条断言全过★)
#
# ★★**★唯一变量 (★2026-11-10 02:4x)★★** ★★★
#   ★**机制③ (★11-09 21:5x 就实现了, ★env 门控 `PCB_PRIO_RETRY`, ★默认关 ⇒ 逐位不变★)**: ★★★
#     ★**`route_net()` 失败也会 `self.routed.add(net)` ⇒ 第4阶段"其余网络"按 `n not in r.routed` 跳过**
#     ★**⇒ 该网彻底没铜 (0 段) ⇒ 再也没被试过** ⇒ ★★**实测受害者: `JTAG_TDO`/`JTAG_TMS`/`UART_RX`/`I2C_B_SCL`/`I2C_B_SDA`★★**
#     ★**⇒ 修法: 优先阶段失败 ⇒ `routed.discard(net)` ⇒ 第4阶段用更大的预算再试一次** ★★
#   ★**⇒ 本臂 env 与 v76ru 逐位相同, ★只多这一个开关 ⇒ 干净 A/B** ★★
#   ★**⇒ `--from-drc` 输入仍是 `/tmp/v76rs_unc.drc.json` (★与 v76ru 同 ⇒ 目标清单一致 ★) ★★
#
# ★v76s5_arms.sh -- ★★★【★★并集臂: ★v76rp env (成对预留+PRIO_SPAN_SORT) + ★--from-drc 57 框 + 板规则0.15★★★】 ★★★【成对预留 + 优先网按跨距排序 臂】: v76rr env 逐位相同 + ★2 处机制修复 ★★★
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

OUT=/tmp/v76s5_R.kicad_pcb
LOG=/tmp/v76s5_R.log
DRC=/tmp/v76s5_R.drc.json

echo "=== v76s5 臂: v76rr + ★成对预留(P+N) + ★优先网按跨距排序 ★ ==="

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
echo "  ✓ 唯一变量 = PCB_ESC_STRAIGHT=2 (★--from-drc 输入 /tmp/v76rs_unc.drc.json 与 v76ru 同 ★)"

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
      PCB_VIA_HALO_CENTER=1 PCB_ESC_STRAIGHT=2 \
      PCB_ROUTE_RESERVE="$RESERVE" PCB_PRIO_SPAN_SORT=1 \
      PCB_OUT="$OUT" \
      timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$LOG" 2>&1
  echo "EXIT=$?" >> "$LOG"
) &
_PID=$!
echo "  [v76s5 臂] PID=$_PID"

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
bash state/replay_patch_chain.sh "$OUT" v76s5
echo "  链 rc=$?"

echo "── vs 同链基线 (★不是 vs 官方板) ──"
FINAL="/tmp/chain_v76s5/final_chain.kicad_pcb"
if [ -f "$FINAL" ]; then
  bash state/compare_arm_baseline.sh "$FINAL"
else
  echo "  ⚠️ 链没出终板 ⇒ 没法比"
fi
exit 0
