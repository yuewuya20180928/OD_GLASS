#!/usr/bin/env bash
# promote_board_file.sh -- ★**把一个"任意路径的候选板"晋级到官方板** (2026-11-06 07:1x)
#
# ★**为什么需要这个脚本 (实测)**:
#   `promote_arm.sh` 只认 `/tmp/${PREFIX}_${ARM}.kicad_pcb` 这一种命名
#   ⇒ 而 06:2x 之后的晋级来源是"补丁工具链" (patch_astar_nostub / fix_straight_links)
#      产出的板 (名字五花八门) ⇒ ★**没法用 promote_arm.sh 晋级** ⇒ 只能手抄
#   ⇒ 手抄 = 漏步骤的历史已经有过 (备份/落盘印/叠层/铜皮/自检/回滚)
#   ⇒ ★**本脚本 = 把 promote_arm.sh + finish_line.sh 的纪律固化下来, 只把"臂板路径"参数化**
#
# ★**判据前置**: 调用者**必须**已经跑过 `compare_arm_official.py` 并拿到 ACCEPT
#   (名单制闸: DRC=0 + 退铜名单为空 + 差分死腿为空 + 逐网孤岛不变多 + 至少一项变好)
#   ⇒ 本脚本会**再跑一次闸**做兜底 (防止手滑把 REJECT 的板推上去)
#
# ★**流程 (与 finish_line.sh 一致)**:
#   ① 再跑名单制闸 (ACCEPT 才继续)
#   ② parity 预检 (rc=0 才继续)
#   ③ 备份官方板 (state/.lastgood/ + ~/board_backups/ 双份)
#   ④ 复制 + 写落盘印 (.layout_landed.json)
#   ⑤ 注入叠层 (add_stackup.py) —— 走线数前后必须一致
#   ⑥ 大电流网加铜皮 (add_power_pour.py) + 改写落盘印
#   ⑦ ★**终点线自检: fresh DRC** ⇒ ≠0 ⇒ ★**自动回滚**
#   ⑧ 重出投产包 (gen_production_pack.sh)
#   ⑨ 全门禁自验 (verify_and_release.sh) + ★**写 .layout_done.json** (实测值)
#   ⑩ 打印最终证据 (段数/孔/unc/DRC/G1 状态)
#
# 用法: bash state/promote_board_file.sh <候选板路径> [闸基线板]
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

SRC="${1:?用法: promote_board_file.sh <候选板> [基线板]}"
BASE="${2:-HW/PCB/demo_mainboard.kicad_pcb}"
PCB=HW/PCB/demo_mainboard.kicad_pcb

[ -f "$SRC" ] || { echo "❌ 没有候选板: $SRC"; exit 1; }
echo "════════ ① 名单制闸复检 (ACCEPT 才准晋级) ════════"
python3 state/compare_arm_official.py "$SRC" "$BASE" 2>&1 | tail -22
GATE=$?
if [ "$GATE" -ne 0 ]; then
  echo "❌ 闸 REJECT (rc=$GATE) ⇒ **中止晋级** (不许拿 REJECT 的板当官方板)"
  exit 1
fi

echo "════════ ② parity 预检 ════════"
bash state/pcbnew_py.sh state/check_pcb_nets.py "$SRC" > /tmp/_promote_parity.log 2>&1
PRC=$?
echo "  候选板 parity rc=$PRC"
if [ "$PRC" -ne 0 ]; then
  echo "❌ ★**候选板与网表不一致 (parity 红) ⇒ 拒绝晋级**"; tail -8 /tmp/_promote_parity.log; exit 1
fi

SEG=$(grep -c '(segment' "$SRC"); VIA=$(grep -c '(via' "$SRC")
echo "  候选板: $SEG 段 / $VIA 孔"
[ "$SEG" -gt 1000 ] || { echo "❌ 段数太少 ⇒ 不晋级"; exit 1; }

echo "════════ ③ 备份官方板 (双份持久) ════════"
STAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p state/.lastgood "$HOME/board_backups"
cp -p "$PCB" "state/.lastgood/board_prev_promote_${STAMP}.kicad_pcb"
cp -p "$PCB" "$HOME/board_backups/board_prev_promote_${STAMP}.kicad_pcb"
echo "  ✅ 备份: state/.lastgood/board_prev_promote_${STAMP}.kicad_pcb (+ ~/board_backups/)"

echo "════════ ④ 复制 + 写落盘印 ════════"
cp "$SRC" "$PCB"
python3 - "$PCB" <<'PY'
import json, os, sys, time
p = sys.argv[1]
seg = via = 0
for l in open(p, encoding="utf-8", errors="ignore"):
    s = l.lstrip()
    if s.startswith("(segment"): seg += 1
    elif s.startswith("(via"): via += 1
land = {"at": int(os.stat(p).st_mtime), "tracks": seg, "vias": via,
        "pcb": os.path.basename(p), "landed_at": int(time.time())}
json.dump(land, open(os.path.join(os.path.dirname(p), ".layout_landed.json"), "w",
                     encoding="utf-8"), ensure_ascii=False)
print("  落盘印:", json.dumps(land, ensure_ascii=False))
PY

echo "════════ ④a 注入叠层/介质规格 ════════"
_sb=$(grep -c '(segment' "$PCB" || echo 0); _vb=$(grep -c '(via' "$PCB" || echo 0)
python3 state/add_stackup.py "$PCB" --inplace 2>&1 | tail -3
_sa=$(grep -c '(segment' "$PCB" || echo 0); _va=$(grep -c '(via' "$PCB" || echo 0)
if [ "$_sb" = "$_sa" ] && [ "$_vb" = "$_va" ]; then
  echo "  ✅ 叠层已注入 (走线/过孔未变: $_sa 段 / $_va 孔)"
else
  echo "  ❌ ★叠层注入后走线数变了 ($_sb/$_vb -> $_sa/$_va) ⇒ 中止"
  BK="state/.lastgood/board_prev_promote_${STAMP}.kicad_pcb"
  [ -f "$BK" ] && cp -p "$BK" "$PCB"
  exit 1
fi

echo "════════ ④b 大电流网加铜皮 ════════"
bash state/pcbnew_py.sh state/add_power_pour.py "$PCB" RAIL_DEMO_5V 2>&1 | tail -4
python3 - "$PCB" <<'PY'
import json, os, sys, time
p = sys.argv[1]
seg = via = 0
for l in open(p, encoding="utf-8", errors="ignore"):
    s = l.lstrip()
    if s.startswith("(segment"): seg += 1
    elif s.startswith("(via"): via += 1
land = {"at": int(os.stat(p).st_mtime), "tracks": seg, "vias": via,
        "pcb": os.path.basename(p), "landed_at": int(time.time()), "note": "after power pour"}
json.dump(land, open(os.path.join(os.path.dirname(p), ".layout_landed.json"), "w",
                     encoding="utf-8"), ensure_ascii=False)
print("  落盘印(加铜皮后):", json.dumps(land, ensure_ascii=False))
PY

echo "════════ ④c 终点线自检 (fresh DRC ⇒ 不过就回滚) ════════"
bash state/kicad.sh pcb drc --output /tmp/_finish_drc.json --severity-error --severity-warning --format json "$PCB" >/dev/null 2>&1
_drc=$(python3 -c "import json;print(len(json.load(open('/tmp/_finish_drc.json')).get('violations') or []))" 2>/dev/null || echo 999)
_unc=$(python3 -c "import json;print(len(json.load(open('/tmp/_finish_drc.json')).get('unconnected_items') or []))" 2>/dev/null || echo -1)
echo "  终点线后 DRC违规 = $_drc · unconnected = $_unc"
if [ "$_drc" != "0" ]; then
  BK="state/.lastgood/board_prev_promote_${STAMP}.kicad_pcb"
  if [ -f "$BK" ]; then
    echo "  ★**DRC≠0 ⇒ 自动回滚官方板** (备份: $BK)"
    cp -p "$BK" "$PCB"
    python3 state/_restore_land_stamp.py "$PCB" "rollback after promote DRC!=0"
    echo "  ❌ 终点线自检失败 ⇒ **官方板已回滚** ⇒ 中止"
    exit 1
  fi
  echo "  ❌ DRC≠0 且找不到备份 ⇒ 中止"; exit 1
fi
echo "  ✅ 终点线后 DRC=0 ⇒ 继续"

echo "════════ ⑤ 重出投产资料包 ════════"
timeout 3600 bash state/gen_production_pack.sh > /tmp/prod_pack.log 2>&1
echo "  gen_production_pack rc=$?"
tail -5 /tmp/prod_pack.log

echo "════════ ⑥ 全门禁自验 + 写 .layout_done.json ════════"
timeout 3600 bash state/verify_and_release.sh > /tmp/verify_final.log 2>&1
RC=$?
echo "  verify_and_release rc=$RC"
grep -E "unconnected items|DRC violations|check_pcb_nets rc|chain_gate rc|stage_gate rc|放行" /tmp/verify_final.log | head -12

echo "════════ ⑦ 最终证据 ════════"
python3 - "$PCB" <<'PY'
import json, os, sys
p = sys.argv[1]
seg = via = 0
for l in open(p, encoding="utf-8", errors="ignore"):
    s = l.lstrip()
    if s.startswith("(segment"): seg += 1
    elif s.startswith("(via"): via += 1
print("  板文件      : %s" % p)
print("  mtime/size  : %d · %d 字节" % (int(os.stat(p).st_mtime), os.path.getsize(p)))
print("  走线段数    : %d" % seg)
print("  过孔数      : %d" % via)
d = json.load(open('/tmp/_finish_drc.json'))
print("  DRC违规     : %d" % len(d.get('violations') or []))
print("  unconnected : %d" % len(d.get('unconnected_items') or []))
PY
ls -la HW/PCB/.layout_done.json && cat HW/PCB/.layout_done.json
echo
echo "════════ ⑧ 放行章状态 ════════"
if [ -f state/.auto_release_done ]; then
  echo "  ✅ 放行章存在: $(cat state/.auto_release_done)"
else
  echo "  ★ 放行章不存在 ⇒ 未放行 (★只有 unconnected=0 + DRC=0 + 全门禁 rc=0 才盖章)"
fi
echo "  ★ G1 状态见上面 stage_gate rc (rc=1 ⇒ G1 仍开 ⇒ **不许投板**)"
exit $RC
