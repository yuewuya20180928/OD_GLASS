#!/usr/bin/env bash
# v76rt_arms.sh -- ★★★★**★【★未启动 ★ 等 v76rs 交卷 + 主会话批准后再开 ★】★★★★ ★★★
#
# ★★**本脚本【刻意带启动闸】: `V76RT_GO=1` 才真跑** ⇒ ★**任何误执行都不会偷偷开臂** ★★
#   ⇒ 用法: `V76RT_GO=1 V76RT_MODE=span bash state/v76rt_arms.sh`
#
# ★★★★**★【为什么要开这个臂 (★2026-11-10 00:3x 独立复算后)】★★★★** ★★★
#   ★**基线账 (★链后同口径, ★vs `baseline_v76_chain`)**: ★★★
#   | 臂 | unc | 零铜网 | 差分单边零铜 | 走线 | 死腿 | 判定 |
#   |---|---|---|---|---|---|---|
#   | 基线 | 46 | 22 | 11 | 14023 | 0 | 参照 |
#   | ★v76rr (单网预留) | 43 | 16 | 8 | 13753 | 0 | REJECT (★退铜4 + 孤岛13) |
#   | ★v76rp (成对预留+跨距排序) | ★**39** ★ | ? | ? | 14093 | 0 | REJECT (★退铜1 + 孤岛6 + DRC1) |
#   | ★v76rs (8框预留) | ★跑着★ | | | | | |
#   ★★**⇒ 唯一把 unc 打到 39 的是 `PCB_PRIO_SPAN_SORT=1` (★v76rp) ⇒ 它是【已验证有效】的杠杆** ★★
#   ★★**⇒ 而 `PCB_PRIO_RETRY=1` (★机制③: 优先阶段失败的网, ★第4阶段再试一次) 在【任何臂里都没开过】** ★★
#     ⇒ ★**源码里已实现 + env 门控 + 默认关 ⇒ 逐位不变** ⇒ ★**这是【唯一没被试过的现成杠杆】** ★★
#
# ★★★★**★【四个模式 (★单变量, ★一次只开一个)】★★★★ ★★★
#   ★**`span`**   = v76rs env 逐位相同 + `PCB_PRIO_SPAN_SORT=1` ⇒ ★**目标: 复现 v76rp 的 unc 39, ★同时保住 v76rs 的 JTAG/UART 专属道**
#     ⇒ ★**已知风险**: ★v76rp 的 DRC=1 = `ID_DETECT_0` vs `BOOT_N` 净距 0.1813 (需 0.2000) ⇒ ★**本臂要盯这一条**
#   ★**`box`**    = v76rs env 逐位相同 + 预留串【加 `CSI_D0_D3_P`】(★10 个框) ⇒ ★**目标: 补上 v76rr/v76rp 都补不上的那条退铜**
#   ★**`spanbox`**= 上面两个都开
#   ★**`retry`**  = v76rs env 逐位相同 + `PCB_PRIO_RETRY=1` ⇒ ★**目标: 机制③ (★失败优先网在第4阶段重试)**
#
# ★★★★**★【★★为什么必须有 `box` 这个模式 (★v76rs 的已知漏洞)】★★★★ ★★★
#   ★**v76rr 的 4 个退铜网 = `CSI_D0_D3_P` / `CSI_D0_D3_P_SRC` / `JTAG_TDO` / `JTAG_TMS`**
#   ★★**实测 (★只读探针 `state/_probe_pads.py`)**: ★★
#     · `CSI_D0_D3_P_SRC` 的焊盘 = `J_SOM_P4.91`(16.800,50.960) + `C_AC_CSI_D0_D3_P.1`(5.900,58.600)
#     · `CSI_D0_D3_P`     的焊盘 = `C_AC_CSI_D0_D3_P.2`(7.500,58.600) + `CONN_CAM.3`(79.900,51.400)
#     ⇒ ★**`CSI_D0_D3_P` 【不经过 J_SOM】⇒ ★**A1 那 5 个框里【没有一个是它的】⇒ ★**8 框覆盖不到它**
#   ★★**⇒ 证据链**: ★**v76rp 已经有【成对预留】(★同样 5 个框) ⇒ ★★**实测 v76rp 仍然退铜 `CSI_D0_D3_P`** ★★
#     ⇒ ★★**⇒ v76rs 大概率也会退铜 `CSI_D0_D3_P` ⇒ ★★**名单制闸还是 REJECT** ⇒ ★**必须单独给它一个框** ★★
#   ★**`box` 模式加的框** = `CSI_D0_D3_P:0,7.050,58.600,7.950,60.000` (★AC 端出脚走廊, ★净距 +0.874mm)
#     ⇒ ★**注意**: ★**AC 端另外两个焊盘 (`CSI_D0_D3_N_SRC`@10.700 / `CSI_D0_D3_N`@12.300) 不在这个框里 ⇒ 不误伤** ★★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

MODE="${V76RT_MODE:-span}"
if [ "${V76RT_GO:-0}" != "1" ]; then
  echo "🚫 ★**本臂【带启动闸】: 未启动** ★★"
  echo "   ⇒ 确认后: ★\`V76RT_GO=1 V76RT_MODE=$MODE bash state/v76rt_arms.sh\`"
  echo "   ⇒ 模式: span | box | spanbox | retry (★默认 $MODE)"
  exit 9
fi

OUT=/tmp/v76rt_R.kicad_pcb
LOG=/tmp/v76rt_R.log
DRC=/tmp/v76rt_R.drc.json

# ---- 模式 ⇒ env 增量 + 预留串增量 ----
EXTRA_ENV=""
RESERVE_NETS="JTAG_TDO,JTAG_TMS,UART_TX@J_UART.1"
case "$MODE" in
  span)   EXTRA_ENV="PCB_PRIO_SPAN_SORT=1" ;;
  box)    RESERVE_NETS="$RESERVE_NETS,CSI_D0_D3_P" ;;
  spanbox) EXTRA_ENV="PCB_PRIO_SPAN_SORT=1"; RESERVE_NETS="$RESERVE_NETS,CSI_D0_D3_P" ;;
  retry)  EXTRA_ENV="PCB_PRIO_RETRY=1" ;;
  *) echo "❌ 未知模式: $MODE (★span|box|spanbox|retry)"; exit 2 ;;
esac

echo "=== v76rt 臂: v76rs env 逐位相同 + 模式[$MODE] (★增量: $EXTRA_ENV / 预留网: $RESERVE_NETS) ==="

echo "── 算预留串 (plan_route_reserve.py) ──"
RESERVE=$(bash state/pcbnew_py.sh state/plan_route_reserve.py HW/PCB/demo_mainboard.kicad_pcb \
           --nets "$RESERVE_NETS" 2>/dev/null \
           | grep -o 'PCB_ROUTE_RESERVE="[^"]*"' | head -1 | sed 's/PCB_ROUTE_RESERVE="//; s/"$//')
if [ -z "$RESERVE" ]; then
  echo "❌ 预留串没算出来 ⇒ 收工 (★别用空串开臂)"
  exit 3
fi
echo "  ✓ 预留串 = $RESERVE"

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
      PCB_VIA_HALO_CENTER=1 \
      $EXTRA_ENV \
      PCB_ROUTE_RESERVE="$RESERVE" \
      PCB_OUT="$OUT" \
      timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$LOG" 2>&1
  echo "EXIT=$?" >> "$LOG"
) &
_PID=$!
echo "  [v76rt 臂] PID=$_PID"

while kill -0 "$_PID" 2>/dev/null; do sleep 60; done
echo "=== 第①步结束 ==="
if [ ! -f "$OUT" ]; then
  echo "❌ 没出板 ⇒ 收工 (看 $LOG)"; exit 2
fi

echo "── 板规则 min track width → 0.15 (★老板批准的规格; ★不改几何) ──"
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
bash state/replay_patch_chain.sh "$OUT" "v76rt_$MODE"
echo "  链 rc=$?"

echo "── vs 同链基线 (★不是 vs 官方板) ──"
FINAL="/tmp/chain_v76rt_$MODE/final_chain.kicad_pcb"
if [ -f "$FINAL" ]; then
  bash state/compare_arm_baseline.sh "$FINAL"
else
  echo "  ⚠️ 链没出终板 ⇒ 没法比"
fi
exit 0
