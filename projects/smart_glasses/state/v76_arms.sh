#!/usr/bin/env bash
# v76_arms.sh -- ★**对照组: 不带任何换边开关** ⇒ 用来测【换边到底有没有效果】(★v76 vs v74 = 中途换边; v76 vs v77 = 末尾换边)
#
# ★★**这个臂是什么** ****
#   ★**env = 官方板【路由阶段】的真 env (★v44_R: ★PCB_PART_POS 钉位 10 个 R_SEL + PCB_VIA_HALO_CENTER=1)
#     ⇒ ★**之前 v74/v75 用的是 v37_R env (★没有钉位、没有 VIA_HALO_CENTER) ⇒ 与官方板不可比
#     ⇒ ★**v74/v75 连 RESET_N 都保不住 (官方 ok=True L=144.5mm ⇒ v74/v75 ok=False 失败脚=5)
#        ⇒ ★**那是 env 差异, 不是换边造成的 ⇒ ★**换边的真实效果还没测过**
#   ★**★**对照组: 不带任何换边开关** ⇒ 用来测【换边到底有没有效果】(★v76 vs v74 = 中途换边; v76 vs v77 = 末尾换边)**
# ★**纪律**: 官方板只读 / 不覆盖既有产物 / 板文件与日志分开命名 / 存盘回读校验 / 四把尺子自动跑
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

OUT1=/tmp/v76_R.kicad_pcb          # ★第 ① 步: 整板重布产物
LOG1=/tmp/v76_R.log                # ★第 ① 步日志
OUT2=/tmp/v76_R2.kicad_pcb         # ★第 ② 步: 补段后产物
LOG2=/tmp/v76_R2.log
DRC2=/tmp/_v76_drc.json
PROV=$PROJ/state/arm_logs/v76_R.provenance.txt

if [ -e "$OUT1" ] || [ -e "$LOG1" ] || [ -e "$OUT2" ] || [ -e "$LOG2" ]; then
  echo "  [v76 臂] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"
  exit 0
fi

echo "=== v76 臂: 官方配方 + 换边重试 (唯一变量 ) ==="
echo "  第①步 整板重布 → $OUT1 (日志 $LOG1)"

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
      PCB_VIA_HALO_CENTER=1 \
      PCB_OUT="$OUT1" \
      timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$LOG1" 2>&1
  echo "EXIT=$?" >> "$LOG1"
) &
_PID=$!
echo "  [v76 臂] PID=$_PID"

# ★**等第 ① 步跑完 (最长 6 小时)** ⇒ 轮询产物
while kill -0 "$_PID" 2>/dev/null; do sleep 60; done

echo "=== 第①步结束 (EXIT 见 $LOG1) ⇒ 存盘回读校验 ==="
if [ ! -f "$OUT1" ]; then
  echo "❌ 第①步没出板 ⇒ 收工"
  exit 2
fi
bash state/pcbnew_py.sh -c "
import pcbnew
b = pcbnew.LoadBoard('$OUT1')
if b is None:
    print('❌ 存盘回读失败 (板文件无效) ⇒ 收工')
    raise SystemExit(3)
seg = sum(1 for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T)
via = sum(1 for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T)
print('  ✓ 存盘回读 OK: 走线 %d 段 / 过孔 %d 个' % (seg, via))
" 2>&1 | grep -v "Debug:" | tee /tmp/_v76_readback.txt
if ! grep -q "存盘回读 OK" /tmp/_v76_readback.txt; then
  echo "❌ 回读失败 ⇒ 收工 (不往下走)"
  exit 3
fi

echo "=== 第②步: fresh DRC (取 v76 自己的未连接表) ==="
bash state/kicad.sh pcb drc --output "$DRC2" --severity-error --severity-warning \
     --format json "$OUT1" >/dev/null 2>&1
python3 - <<PY
import json
d = json.load(open("$DRC2", encoding="utf-8"))
print("  v76 fresh DRC: violations=%d unconnected=%d"
      % (len(d.get("violations") or []), len(d.get("unconnected_items") or [])))
PY

echo "=== 第②步: 补段补丁 (grid 0.125 · margin 0.0625 · 与官方板同配方) ==="
env PCB_HALO_MARGIN=0.0625 bash state/pcbnew_py.sh state/patch_astar_nostub.py \
    "$OUT1" "$DRC2" --out "$OUT2" --grid 0.125 \
    > "$LOG2" 2>&1
echo "  补段 rc=$? → $OUT2"

cat > "$PROV" <<EOF
★★**v76 臂溯源 (2026-11-08 23:5x 起)**★
★**配方**: ★**官方板两步配方 + 唯一变量 **
  · 第①步 整板重布: 官方 v37_R env (★PCB_HALO_MARGIN=0.20 · LAYERS=8 · KEEPOUT=24.0,56.1,35.6,59.6 …)
  · 第②步 补段: patch_astar_nostub @ grid 0.125 · PCB_HALO_MARGIN=0.0625 (★官方板同配方)
★**第①步产物**: $OUT1 · 日志 $LOG1
★**第②步产物**: $OUT2 · 日志 $LOG2 · DRC JSON $DRC2
★**机制依据**: state/PAIR_AWARE_ROUTING_PLAN.md §3.2 ("P 通 N 不通"是顺序依赖)
★**自测**: state/test_pair_swap_retry.py (★两档 ALL TESTS PASS)
★**官方板全程只读** (md5 611b869e)
EOF

echo "=== 四把尺子 (fresh DRC / 名单制闸 / 闸自测 / 差分对审计) ==="
bash state/verify_candidate.sh "$OUT2" 2>&1 | tee /tmp/_v76_verify.txt
echo "=== v76 全流程结束 $(date '+%F %T') ==="
