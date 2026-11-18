#!/usr/bin/env bash
# ★arm_ledger.sh —— 【臂总账汇总】★ 把所有臂的同口径读数排成一张表
#
# ★★**为什么要有 (★2026-11-10 04:5x)★★
#   ★**臂一多, 读数散在各处, 口径还容易混 (★"unconnected 条目数" vs "网名签名数"★)**
#   ★**⇒ 一张表, 同一口径, 全部 fresh DRC ★★
#
# ★★★2026-11-10 16:4x 修掉三个"汇总表说谎"的 bug (★实测: 28 行臂读数全部现形)★★
#   ① ★**"差单" 列 28 行全是 ?** —— 抽取用的标签是 "差分单边", ★**而 compare_arm_baseline.sh
#      实际打印的是 "★差分对死腿: N"** ⇒ grep 永远抓不到 ⇒ **该列恒为空**
#      ⇒ ★这正是 MEMORY 铁律里点名的病: "★闸脚本自己也会有 bug: 差分对清单路径少退一级
#        ⇒ 指标恒为 0 ⇒ 闸门形同虚设" ⇒ ★**同一个坑出现在汇总表层**。
#   ② ★**"零铜" 列名不副实** —— 它 grep 的是任何含 "零铜" 的行 ⇒ 命中的是
#      "★退铜名单 (官方板有铜⇒候选零铜): N" ⇒ **这一列其实是"退铜名单数"**;
#      ★**当退铜名单为空时** (那一行没有数字) ⇒ head -1 继续往下落到
#      "(参考) 救回零铜的网: 15" ⇒ ★**同一列在两种臂上表示两个完全不同的量** (实测 v76mj1 = 3 / v76mh = 15)。
#   ③ ★**"退铜" 列与"零铜" 列同源** ⇒ 两个列显示同一个数。
#   ⇒ ★**修法**: 列口径改成 **退铜 / 死腿 / 孤岛 / 救回** (全部对齐 compare_arm_baseline.sh 的真实标签),
#     ★**列数与列宽一字未改** (10 列), 只换名字与取值。
#   ⇒ ★**同时加"抽取失败必须响亮"守卫**: 标签抓不到 (而不是抓到 0) 时,
#     ★**不许静默打 ?** ⇒ 该行打 "抽取失败" + 整张表 rc=1
#     (★沿用铁律: 恒为 0 / 恒为空 的指标比没有指标更危险)。
#
# 用法:
#   bash state/arm_ledger.sh [基线板]
#   ⇒ 默认基线 = state/.lastgood/baseline_v76_chain.kicad_pcb
#   ⇒ 扫 /tmp/chain_v76*/final_chain.kicad_pcb
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
BASE="${1:-state/.lastgood/baseline_v76_chain.kicad_pcb}"

# ★**抽取: 按标签取数** —— ★标签在但没数字 ⇒ 0 (空名单是合法的好结果);
#   ★标签不在 ⇒ "MISS" (⇒ 守卫会响亮报错, 不许静默变 ?)***
extract() {  # extract <输出> <标签正则> [1=取末字段(计数行) 2=取倒数第2字段(指标表候选值)]
  local out="$1" re="$2" mode="${3:-1}" line n
  line=$(echo "$out" | grep -E "$re" | head -1)
  if [ -z "$line" ]; then echo "MISS"; return; fi
  if [ "$mode" = "2" ]; then
    n=$(echo "$line" | awk '{print $(NF-1)}')
  else
    n=$(echo "$line" | awk '{print $NF}')
  fi
  echo "${n:-0}"
}

printf '%-14s %7s %7s %6s %6s %6s %6s %6s %6s %6s %6s %6s\n' \
  "臂" "段数" "DRC" "unc条" "unc网" "零铜网" "差半" "退铜" "死腿" "孤岛" "救回" "闸"
printf '%.0s─' {1..96}; echo

# ★**基线自己先算一遍**
BASE_ROW=$(python3 - "$BASE" <<'PY'
import json, os, sys
sys.path.insert(0, "state")
p = sys.argv[1]
if not os.path.exists(p):
    print("  (基线缺失)"); raise SystemExit
d = json.load(open(p, encoding="utf-8", errors="ignore")) if p.endswith(".json") else None
segs = sum(1 for l in open(p, encoding="utf-8", errors="ignore") if l.lstrip().startswith("(segment"))
print("BASE\t%d\t-\t-\t-\t-\t-\t-\t-\t-" % segs)
PY
)
echo "$BASE_ROW" | awk -F'\t' '{printf "%-14s %7s %7s %6s %6s %6s %6s %6s %6s %6s %6s %6s\n", "★基线", $2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12}'

for d in $(ls -d /tmp/chain_v76* 2>/dev/null | sort); do
  B="$d/final_chain.kicad_pcb"
  [ -f "$B" ] || continue
  TAG=$(basename "$d" | sed 's/^chain_//')
  SEG=$(grep -ac '(segment' "$B")
  OUT=$(timeout 900 bash state/arm_fresh_readings.sh "$B" --baseline "$BASE" 2>/dev/null)
  DRC=$(echo "$OUT" | grep -oE "DRC违规: [0-9]+" | head -1 | grep -oE "[0-9]+")
  UNC=$(echo "$OUT" | grep -oE "unc   : [0-9]+ 条 / [0-9]+ 个网名" | grep -oE "[0-9]+" | head -1)
  UNCN=$(echo "$OUT" | grep -oE "unc   : [0-9]+ 条 / [0-9]+ 个网名" | grep -oE "[0-9]+" | tail -1)
  # ★★列口径 = compare_arm_baseline.sh / compare_arm_official.py 的**真实标签** (★不要臆造标签名) ★★
  # ★★"零铜网" 与 "差半" 取自指标表 (compare_arm_official.py 打的
  #     "零铜网(≥2焊盘)  <候选>  <基线>" / "差分单边零铜  <候选>  <基线>")
  #     ⇒ ★**取倒数第 2 个字段 = 候选值** (★★且不能取"首个数字" —— 标签里的 "≥2" 是 2 不是读数★) ★★
  ZC=$(extract "$OUT" "零铜网\(≥2焊盘\)" 2)   # ★零铜网数 (计数类, 只作参考)
  DH=$(extract "$OUT" "差分单边零铜" 2)        # ★差分单边零铜对数 (计数类, 只作参考)
  RC=$(extract "$OUT" "退铜名单" 1)          # ★退铜名单 (官方有铜⇒候选零铜) —— 硬判据② 必须为空
  DP=$(extract "$OUT" "差分对死腿" 1)        # ★差分对死腿 (官方双边有铜⇒候选单边零铜) —— 硬判据③ 必须为空
  ISL=$(extract "$OUT" "逐网孤岛变多" 1)     # ★逐网孤岛变多 —— 硬判据④ 必须为空
  RSQ=$(extract "$OUT" "救回零铜的网" 1)     # ★(参考) 救回零铜的网 —— 正向信号
  GATE=$(echo "$OUT" | grep -oE "闸 rc=[0-9]+" | tail -1 | grep -oE "[0-9]+$")
  # ★★守卫: 任一列抽不到 (MISS) ⇒ 该行打"抽取失败" + 整表 rc=1 (★不许静默 "?") ★★
  if [ "$RC" = "MISS" ] || [ "$DP" = "MISS" ] || [ "$ISL" = "MISS" ] || [ -z "$GATE" ] \
     || [ "$ZC" = "MISS" ] || [ "$DH" = "MISS" ]; then
    printf '%-14s %7s %7s %6s %6s %6s %6s %6s %6s %6s %6s %6s\n' \
      "$TAG" "$SEG" "${DRC:-?}" "${UNC:-?}" "${UNCN:-?}" "失败" "失败" "失败" "失败" "失败" "失败" "?"
    echo "  ❌ $TAG 抽取失败: 零铜=$ZC 差半=$DH 退铜=$RC 死腿=$DP 孤岛=$ISL 闸=${GATE:-MISS} (★标签抓不到 ⇒ 闸门会形同虚设★)" >&2
    FAIL=1
    continue
  fi
  printf '%-14s %7s %7s %6s %6s %6s %6s %6s %6s %6s %6s %6s\n' \
    "$TAG" "$SEG" "${DRC:-?}" "${UNC:-?}" "${UNCN:-?}" "$ZC" "$DH" "$RC" "$DP" "$ISL" "$RSQ" "$GATE"
done
echo
echo "★口径: unc条 = unconnected_items 条目数 · unc网 = 网名签名数"
echo "★★硬判据三列 (★必须为空才是好结果★): 退铜 = 退铜名单数 · 死腿 = 差分对死腿数 · 孤岛 = 逐网孤岛变多数"
echo "★计数类两列 (★只作参考, ★不许当\"变好\"证据★): 零铜网 = 零铜网(≥2焊盘) 数 · 差半 = 差分单边零铜 对数"
echo "★救回 = (参考) 救回零铜的网数 (正向信号) · 闸 = 名单制闸 rc (0=ACCEPT)"
echo "★全部读数来自 fresh DRC (★不用 chain 目录里的同名 json★)"
echo "★列口径 2026-11-10 16:4x 修正 (旧版 '差单' 恒为 ? / '零铜' 名不副实 ⇒ 见文件头注释)"
[ "${FAIL:-0}" = "1" ] && { echo "❌ 有臂的读数抽取失败 —— 这张表不可信 (★已响亮报错, 不许当绿表用★)" >&2; exit 1; }
exit 0
