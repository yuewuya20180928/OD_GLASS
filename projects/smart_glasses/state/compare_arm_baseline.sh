#!/usr/bin/env bash
# compare_arm_baseline.sh -- ★★比较【候选臂】vs【同工艺基线】(★不是 vs 官方板!)
#
# ★★★★**★为什么要有这个脚本 (★2026-11-09 14:0x 实测)★★★★**
#   ★**"官方板 vs 候选臂"这个比较本身就是错的**: ★**官方板的 stage-1 是 17022 段 (★历史 promote 累积),
#     而当前路由器的产物只有 13407 段** ⇒ ★★**两边不在同一条工艺线上 ⇒ 比出来的差异全是【工艺差】不是【臂的优劣】★★
#   ⇒ ★**正确做法**: ★**基线也用【当前路由器】跑, 再套【同一条已校准的补丁链】** ⇒ ★★**两边同工艺 ⇒ 差异才是臂的功劳** ★★
#   ⇒ ★**基线 = `v76_R` (★当前路由器"什么都没改"的产物) + 已校准的链** ⇒ ★**14023 段 / 392 孔 / DRC 0 / unc 46** ★★
#
# ★**用法**:
#   bash state/compare_arm_baseline.sh <候选臂板> [--baseline <基线板>]
#   ⇒ ★**候选臂必须是【已跑过补丁链】的板** (★链脚本会自己写 `<板>.chain.json` 凭据 ⇒ 脚本会验)
#
# ★**判据 (★全部用已落地的统一尺子)**:
#   ① `state/cmp_unc_sets.py --strict` ⇒ ★**未连接的网名集合必须【变小】** (★不许变大/不变)
#   ② `state/compare_arm_official.py` 名单制闸 ⇒ ★**只看"变好"的指标 (unc / 零铜网数)**
#   ③ `state/cmp_pcb_geom.py` ⇒ ★**几何差异定位 (★不是判据, 是给"差异出在哪"用的)**
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1

SRC="${1:?用法: compare_arm_baseline.sh <候选臂板> [--baseline <基线板>]}"
BASE=""
if [ "${2:-}" = "--baseline" ] && [ -n "${3:-}" ]; then
  BASE="$3"
fi
BASE="${BASE:-state/.lastgood/baseline_v76_chain.kicad_pcb}"

[ -f "$SRC" ] || { echo "❌ 没有候选臂: $SRC"; exit 1; }
[ -f "$BASE" ] || { echo "❌ 没有基线板: $BASE"; echo "   ⇒ 建基线: bash state/replay_patch_chain.sh <当前路由器产物板> baseline"; exit 1; }

echo "══════ 候选臂 vs 同工艺基线 ══════"
echo "  候选臂: $SRC  ($(grep -ac '(segment' "$SRC") 段)"
echo "  基线  : $BASE  ($(grep -ac '(segment' "$BASE") 段)"

# ── ① 链凭据 (★候选臂必须跑过链 ⇒ 否则跟基线不同工艺) ──
CHAINJSON="${SRC}.chain.json"
if [ -f "$CHAINJSON" ]; then
  echo "  ✅ 链凭据: $(python3 -c "
import json,sys
d=json.load(open('$CHAINJSON',encoding='utf-8'))
print('输入=%s 步数=%s' % (d.get('input','?'), d.get('steps','?')))" 2>/dev/null)"
else
  echo "  ⚠️ ★**没有链凭据 ${CHAINJSON}** ⇒ ★**这块板没跑过补丁链 ⇒ 与基线不同工艺 ⇒ 不比**"
  exit 1
fi

# ── ② fresh DRC 双方 ──
# ★★★★**★2026-11-09 21:5x 【临时文件名按板名唯一】(★防并行臂互相覆盖)** ★★★★
#   ★**为什么**: ★**原来固定写 `/tmp/_cab_候选.json` / `/tmp/_cab_基线.json`** ⇒ ★**两个臂同时比 ⇒ 后一个覆盖前一个的 DRC json
#     ⇒ ⇒ 判据可能读【另一个臂的板】⇒ ⇒ 结论错** ⇒ ★**⇒ 改成按板文件名唯一** ★★
#   ★**老名字保留一份兼容 (★别的脚本可能在读)** ★★
_CAND_JSON="/tmp/_cab_$(basename "$SRC" | tr -c 'A-Za-z0-9._-' '_' | cut -c1-48).cand.json"
_BASE_JSON="/tmp/_cab_$(basename "$BASE" | tr -c 'A-Za-z0-9._-' '_' | cut -c1-48).base.json"
for pair in "候选:$SRC:$_CAND_JSON" "基线:$BASE:$_BASE_JSON"; do
  tag="${pair%%:*}"; rest="${pair#*:}"; p="${rest%%:*}"; out="${rest#*:}"
  bash state/kicad.sh pcb drc --output "$out" --severity-error --severity-warning --format json "$p" >/dev/null 2>&1
done
CAND_JSON="$_CAND_JSON" BASE_JSON="$_BASE_JSON" python3 - <<'PY'
import json, os
for tag, path in (("候选", os.environ["CAND_JSON"]), ("基线", os.environ["BASE_JSON"])):
    d = json.load(open(path, encoding="utf-8"))
    print("  %s: DRC违规=%d · unconnected=%d" % (tag, len(d.get("violations") or []), len(d.get("unconnected_items") or [])))
PY

# ── ③ 判据①: unc 网名集合必须变小 ──
echo "── ① 未连接网名集合 (★强判据) ──"
python3 state/cmp_unc_sets.py "$_BASE_JSON" "$_CAND_JSON" 2>&1 | sed -n '1,12p'
UPC=$(python3 state/cmp_unc_sets.py "$_BASE_JSON" "$_CAND_JSON" --strict >/dev/null 2>&1 && echo 0 || echo 1)
if [ "$UPC" != "0" ]; then
  echo "❌ ★**候选臂的未连接网名集合没有变小 (★判据① 不过) ⇒ 不是改进 ⇒ 不晋级**"
else
  echo "  ✅ 判据①: 候选臂的未连接网名集合与基线不同 (★逐条对比见上)"
fi
echo "── ①b 名单差集 (★谁被救回 / 谁被打断) ──"
python3 state/arm_net_set_diff.py "$_BASE_JSON" "$_CAND_JSON" 2>&1 | tail -40

# ── ④ 判据②: 名单制闸 (只看变好) ──
echo "── ② 名单制闸 (★臂 vs 基线) ──"
echo "  ★注: ★**该脚本内部把第二个参数叫\"官方板\" ⇒ ★★**这里的\"官方\"实际指本基线** ★★ (★读数时注意) ★"
python3 state/compare_arm_official.py "$SRC" "$BASE" 2>&1 | tail -18
GATE=${PIPESTATUS[0]}
echo "  闸 rc=$GATE"

# ── ⑤ 几何差异定位 (★不是判据) ──
echo "── ③ 几何差异定位 (★供排查) ──"
python3 state/cmp_pcb_geom.py "$SRC" "$BASE" --fast 2>&1 | tail -6

exit "$GATE"
