#!/usr/bin/env bash
# v74_arms.sh -- ★★**"换边重试"上真板 (★2026-11-08 23:5x)★★
#
# ★★**这个臂是什么 (★单变量 A/B, 其余与官方板逐位相同)****
#   ★**官方板的配方 (★11-06 实测倒推出来的, 不是猜)**:
#     ① 整板重布 (臂 v37_R env · PCB_HALO_MARGIN=0.20) ⇒ unc 48 (18008 个铜图元)
#     ② ★**补段补丁**: `patch_astar_nostub.py` @ grid 0.125mm · PCB_HALO_MARGIN=0.0625 (★网格半格)
#        ⇒ ★**补上 3 条 (CSI_D0_D0_P / PWR_GOOD / VDD_3V3_IO) ⇒ unc 45** ⇒ ★**这就是现在的官方板**
#        (★出处: /tmp/_nostub_loose.log)
#   ★**⇒ v74 = 同两步, 只在第 ① 步多一个 `PCB_PAIR_SWAP_RETRY=1` ⇒ 唯一的差别就是换边重试**
#
# ★★**为什么值得跑这个臂 (★机制依据是实测)****
#   ★`state/PAIR_AWARE_ROUTING_PLAN.md` §3.2 ⇒ ★**"P 通 N 不通"是【顺序依赖】**: 先布的腿占走廊 ⇒ 后布的腿出不来
#   ★官方板 11 个差分对是"单边零铜" (★整条腿一根铜都没有) ⇒ ★**其中 9 条是 SRC 腿 ⇒ 出脚就卡死**
#   ★⇒ ★**换边重试: 跟腿没布出来时, 摘掉主腿的铜, 换边重跑整对 ⇒ 只有两条腿都通才采纳**
#   ★⇒ ★**这正是 §4.1 "pair-aware 成对走廊" 的可落地版本 (★联合 A* 4.1M² 格不可行)**
#
# ★**自测已过**: `bash state/pcbnew_py.sh state/test_pair_swap_retry.py --on` ⇒ SELFTEST ALL TESTS PASS
#   (★默认档也过了 ⇒ 既有臂逐位不变)
#
# ★**纪律**:
#   ★**① 官方板只读** (本臂只写 /tmp)
#   ★**② 不覆盖既有产物** (铁律)
#   ★**③ 板文件与日志分开命名** (★v69 翻车根因: 板文件叫 .log ⇒ LoadBoard 读不回来 ⇒ 6 小时白跑)
#   ★**④ 跑完做存盘回读校验** (能 LoadBoard 回来 + 段数/过孔数打印)
#   ★**⑤ 四把尺子自动跑** (fresh DRC / 名单制闸 / 闸自测 / 差分对审计)
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

OUT1=/tmp/v74_R.kicad_pcb          # ★第 ① 步: 整板重布产物
LOG1=/tmp/v74_R.log                # ★第 ① 步日志
OUT2=/tmp/v74_R2.kicad_pcb         # ★第 ② 步: 补段后产物
LOG2=/tmp/v74_R2.log
DRC2=/tmp/_v74_drc.json
PROV=$PROJ/state/arm_logs/v74_R.provenance.txt

if [ -e "$OUT1" ] || [ -e "$LOG1" ] || [ -e "$OUT2" ] || [ -e "$LOG2" ]; then
  echo "  [v74 臂] ★已有产物/日志 ⇒ 不覆盖 (铁律) ⇒ 跳过"
  exit 0
fi

echo "=== v74 臂: 官方配方 + 换边重试 (唯一变量 PCB_PAIR_SWAP_RETRY=1) ==="
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
      PCB_PAIR_SWAP_RETRY=1 \
      PCB_OUT="$OUT1" \
      timeout 21600 bash state/pcbnew_py.sh state/gen_pcb_netlist_board.py \
      > "$LOG1" 2>&1
  echo "EXIT=$?" >> "$LOG1"
) &
_PID=$!
echo "  [v74 臂] PID=$_PID"

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
" 2>&1 | grep -v "Debug:" | tee /tmp/_v74_readback.txt
if ! grep -q "存盘回读 OK" /tmp/_v74_readback.txt; then
  echo "❌ 回读失败 ⇒ 收工 (不往下走)"
  exit 3
fi

echo "=== 第②步: fresh DRC (取 v74 自己的未连接表) ==="
bash state/kicad.sh pcb drc --output "$DRC2" --severity-error --severity-warning \
     --format json "$OUT1" >/dev/null 2>&1
python3 - <<PY
import json
d = json.load(open("$DRC2", encoding="utf-8"))
print("  v74 fresh DRC: violations=%d unconnected=%d"
      % (len(d.get("violations") or []), len(d.get("unconnected_items") or [])))
PY

echo "=== 第②步: 补段补丁 (grid 0.125 · margin 0.0625 · 与官方板同配方) ==="
env PCB_HALO_MARGIN=0.0625 bash state/pcbnew_py.sh state/patch_astar_nostub.py \
    "$OUT1" "$DRC2" --out "$OUT2" --grid 0.125 \
    > "$LOG2" 2>&1
echo "  补段 rc=$? → $OUT2"

cat > "$PROV" <<EOF
★★**v74 臂溯源 (2026-11-08 23:5x 起)**★
★**配方**: ★**官方板两步配方 + 唯一变量 PCB_PAIR_SWAP_RETRY=1**
  · 第①步 整板重布: 官方 v37_R env (★PCB_HALO_MARGIN=0.20 · LAYERS=8 · KEEPOUT=24.0,56.1,35.6,59.6 …)
  · 第②步 补段: patch_astar_nostub @ grid 0.125 · PCB_HALO_MARGIN=0.0625 (★官方板同配方)
★**第①步产物**: $OUT1 · 日志 $LOG1
★**第②步产物**: $OUT2 · 日志 $LOG2 · DRC JSON $DRC2
★**机制依据**: state/PAIR_AWARE_ROUTING_PLAN.md §3.2 ("P 通 N 不通"是顺序依赖)
★**自测**: state/test_pair_swap_retry.py (★两档 ALL TESTS PASS)
★**官方板全程只读** (md5 611b869e)
EOF

echo "=== 四把尺子 (fresh DRC / 名单制闸 / 闸自测 / 差分对审计) ==="
bash state/verify_candidate.sh "$OUT2" 2>&1 | tee /tmp/_v74_verify.txt
echo "=== v74 全流程结束 $(date '+%F %T') ==="
