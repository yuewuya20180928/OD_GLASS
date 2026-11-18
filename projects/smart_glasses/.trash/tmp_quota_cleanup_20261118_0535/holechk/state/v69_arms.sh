#!/usr/bin/env bash
# v69_arms.sh —— ★★**"钉位清单按当前板重排"臂 (★2026-11-07 02:3x 兄弟实测 + 我独立复算)**
#
# ★★★★**★为什么起这个臂 (★根因是"清单过期", ★不是"当时的判断错")**:
#   ★**v58 臂的钉位清单是 2026-11-06 10:2x 的判断, 依据是【当时】官方板的 unc 清单** ⇒ ★**板子后来变了 (★官方板现为 unc 45 / md5 611b869e / mtime 2026-11-06 07:07:17) ⇒ ★**⇒ 清单过期 ⇒ ⇒ ★**要改的是【清单】不是【结论】****
#   ★**★⇒ 这正是"判断会因依据被修掉而半过期"的板面应用 (★结论仍对, 推理链断了)****
#
# ★★★★**★判据 (★本次用的唯一准绳, ★干净可复现)**:
#   ★**① 数据源**: ★**`/tmp/_drc45.json` (★mtime 2026-11-06 07:10:50, ★与官方板 mtime 07:07:17 吻合 ⇒ 对应官方板) 的 45 条 `unconnected_items`**
#   ★**② 逐 net 铜段数**: ★**从 `HW/PCB/demo_mainboard.kicad_pcb` 逐段统计每个 net 的 `(segment` 数 ⇒ ★**铜段 = 0 ⇒ 整网无铜 ⇒ 才是真痛点****
#   ★**③ 零铜 SRC 腿 = 9 条 (★兄弟与我独立复算逐条一致)**: ★**`DSI_D0_D3_N_SRC` 98.53mm · `DSI_D0_D2_N_SRC` 87.73mm · `DSI_D0_D1_P_SRC` 71.34mm · `DSI_D0_D1_N_SRC` 66.14mm · `DSI_D0_D0_P_SRC` 60.55mm · `DSI_D0_D0_N_SRC` 55.35mm · `CSI_D0_D0_N_SRC` 42.20mm · `CSI_D0_D1_N_SRC` 33.97mm · `CSI_D0_D3_N_SRC` 10.03mm****
#   ★**④ R_SEL → SRC net 映射 (★板文件实况)**: ★**`R_SEL_D0_N`⇒`DSI_D0_D0_N_SRC` · `R_SEL_D0_P`⇒`DSI_D0_D0_P_SRC` · `R_SEL_D1_N`⇒`DSI_D0_D1_N_SRC` · `R_SEL_D1_P`⇒`DSI_D0_D1_P_SRC` · `R_SEL_D2_N`⇒`DSI_D0_D2_N_SRC` · `R_SEL_D2_P`⇒`DSI_D0_D2_P_SRC` · `R_SEL_D3_N`⇒`DSI_D0_D3_N_SRC` · `R_SEL_D3_P`⇒`DSI_D0_D3_P_SRC`****
#
# ★★★★**★⇒ v58 钉的 6 个里, 有 2 个是白挪 (★它的 SRC net 已有铜 ⇒ 已通)**:
#   ★**`R_SEL_D2_P` ⇒ `DSI_D0_D2_P_SRC` 铜段 **372** ⇒ 不在 unc ⇒ 已通 ⇒ 白挪 ✗**
#   ★**`R_SEL_D3_P` ⇒ `DSI_D0_D3_P_SRC` 铜段 **250** ⇒ 不在 unc ⇒ 已通 ⇒ 白挪 ✗**
# ★★★★**★⇒ 同时漏了 2 个真痛点 (★铜段 = 0 ⇒ 在 unc)**: ★**`R_SEL_D1_P` ⇒ `DSI_D0_D1_P_SRC` 71.34mm · `R_SEL_D0_P` ⇒ `DSI_D0_D0_P_SRC` 60.55mm**
#   ⇒ ★**⇒ 本臂把 `R_SEL_D2_P`/`R_SEL_D3_P` 换成 `R_SEL_D1_P`/`R_SEL_D0_P` ★**(★数值旁证: 71.34mm 恰是我曾记成 "D3_P 71.3mm" 的那根 ⇒ ★**当时记的其实是 D1_P**)****
#
# ★★★★**★⇒ 本臂清单 (★6 个: 4 个 N 侧 + 2 个 P 侧)**: ★**`R_SEL_D0_N` · `R_SEL_D1_N` · `R_SEL_D2_N` · `R_SEL_D3_N` · `R_SEL_D1_P` · `R_SEL_D0_P`****
#
# ★★★★**★★CSI 侧为何不动 (★两条腿要分开打)**: ★**9 条零铜 SRC 腿里有 3 条是 `CSI_*` (★42.20 / 33.97 / 10.03mm) ⇒ ★**而板文件里 10 个 R_SEL 全是 `DSI_D0_*` 系列 ⇒ ★**⇒ CSI 的 SRC 腿【没有 R_SEL 可挪】⇒ ⇒ CSI 的痛点只能靠【成对走廊规划 / 0.15mm 臂】⇒ ★**⇒ DSI 侧可用"挪串阻"打开, CSI 侧只能靠线宽/走廊 ⇒ 两路不混****
#
# ★**★单变量纪律**: ★**本臂相对 v58 只改【钉位清单】(★D2_P→D1_P, D3_P→D0_P); ★**其余 env 与 v58 逐位相同 ⇒ A/B 干净****
# ★**配套 TP (★与 R_SEL 同网, ★放同一 x 列的 y=8.8 ⇒ 不挡 BTB 出脚)**: ★**TP 必须在 x35.6..48.6 (★J_SOM_P3 占 x15.2..34.8, J_SOM_P1 占 x49.2..68.8 ⇒ 中间空档)****

OUT=/tmp/v69_R.log
PP="R_SEL_D0_N:35.60,5.60;R_SEL_D1_N:38.00,5.60;R_SEL_D2_N:40.40,5.60;R_SEL_D3_N:45.20,5.60"
PP="$PP;R_SEL_D1_P:42.80,5.60;R_SEL_D0_P:47.60,5.60"
PP="$PP;TP_DSI_D0_N:35.60,8.80;TP_DSI_D1_N:38.00,8.80;TP_DSI_D2_N:40.40,8.80"
PP="$PP;TP_DSI_D3_N:45.20,8.80;TP_DSI_D1_P:42.80,8.80;TP_DSI_D0_P:47.60,8.80"

echo "=== v69 臂 (★钉位清单按当前板重排: D2_P→D1_P, D3_P→D0_P) ==="
echo "  钉位: $PP"
(
  cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
  env PCB_W_MIN=0.15 PCB_PART_POS="$PP" \
      PCB_LAYERS=8 PCB_ABUDGET_MULT=6 PCB_HALO_MARGIN=0.20 \
      PCB_BOARD_W=160 PCB_BOARD_H=100 \
      PCB_AREA_BOT=5,58,70,97 PCB_AREA_TOP=78,5,120,36 PCB_AREA_RES=78,38,157,97 \
      PCB_PIN_CONN_CAM=1 PCB_SKIP_PAD_CELLS=1 PCB_PAIR_ESCAPE_EXEMPT=1 \
      PCB_PAIR_EXEMPT_R=0.0 \
      PCB_GND_FIRST=1 PCB_VIA_HALO_MARGIN=0.0 PCB_CONN_GND_ESCAPE=CONN_CAM:4.0 \
      PCB_KEEPOUT=24.0,56.1,35.6,59.6 \
      PCB_OUT="$OUT" \
      timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
        > /tmp/_v69_launch.log 2>&1
  echo "  rc=$? (★日志 $OUT)"
)
