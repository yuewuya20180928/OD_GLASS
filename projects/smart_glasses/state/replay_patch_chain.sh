#!/usr/bin/env bash
# replay_patch_chain.sh -- ★★★**复现"官方板补丁链" (★2026-11-09 02:5x)** ★★★
#
# ★★★**为什么要有这个脚本 (★今晚最贵的教训)****
#   ★**官方板 = 路由阶段(13407 段) + 一串补丁(→18092 段, unc 45, DRC 0)** ⇒ ★**不是一次路由出来的**
#   ★⇒ ★**任何臂的候选板若只跑【最后一步补丁】, 就跟官方终板【不是同工艺】⇒ 四把尺子会刷出一堆假失败**
#   ★**今晚实测**: ★**对照臂 v76 (★根本没做任何改动) 也被闸门 REJECT (★2 对死腿 + 11 个碎裂网)** ⇒ ★**⇒ 那批失败全是基线不可比**
#
# ★**官方链 (★从 /tmp/_nostub125.log / _straight*.log / _combo*.log / _combo2,3.log / _nostub_loose.log 的头一行倒推)**:
#   ① nostub125 : patch_astar_nostub @ grid 0.125  (★输入 = 当时的官方板 = 路由产物 17426 图元 ⇒ 补上 7 条 ⇒ 17619 段)
#   ② straight1/2/3/6/7 : fix_straight_links (★★日志是空的 ⇒ ★**具体参数待校准** ⇒ 见下面的 ★自校准★)
#   ③ combo     : patch_astar_nostub @ grid 0.125  (★输入 = _straight7 ⇒ 补上 6 条 ⇒ 17585 段)
#   ④ combo2    : patch_astar_nostub @ grid 0.125  (★输入 = _combo ⇒ 补上 0 条 ⇒ 18008 图元)
#   ⑤ combo3    : patch_astar_nostub @ grid 0.125 --max-dist ? (★输入 = _combo ⇒ 补上 0 条)
#   ⑥ nostub_loose : patch_astar_nostub @ grid 0.125 margin 0.0625 (★输入 = 18008 图元 ⇒ **补上 3 条 ⇒ 18092 段 = 现在的官方板**)
#
# ★★★**自校准 (★本脚本的正确性判据 —— 不靠"我觉得对不对")****:
#   ★**用法**: `bash state/replay_patch_chain.sh <路由产物板> <标签> [--validate]`
#   ★**--validate 模式**: ★**拿【已知的官方路由产物】(`/tmp/board_last_good_v44_R.kicad_pcb`) 重放整条链**
#     ⇒ ★**如果结果与官方终板逐段数一致 (⇒ 18092 段 / unc 45 / DRC 0) ⇒ 参数对了**
#     ⇒ ★**★没复现出来之前, 这个脚本产出的板不许拿去跟官方比** (★否则又是拿苹果比橘子)
#
# ★**每步都要【该板自己的 fresh DRC】当输入** (★补丁器靠 DRC.json 里的 unconnected_items 找活)
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
cd "$PROJ" || exit 1

ROUTE="${1:?用法: replay_patch_chain.sh <路由产物板> <标签> [--validate]}"
TAG="${2:?用法: replay_patch_chain.sh <路由产物板> <标签> [--validate]}"
VALIDATE="${3:-}"

WORK=/tmp/chain_${TAG}
mkdir -p "$WORK"
LOG=$WORK/chain.log
: > "$LOG"

say() { echo "[$TAG] $*" | tee -a "$LOG"; }

# ★**fresh DRC (★给下一步当输入)**
fresh_drc() {   # $1=板 → $2=json
  bash state/kicad.sh pcb drc --output "$2" --severity-error --severity-warning \
       --format json "$1" >/dev/null 2>&1
}

step_nostub() {  # $1=输入板 $2=输出板 $3=网格 $4=margin $5=额外参数
  local in="$1" out="$2" grid="$3" margin="$4" extra="${5:-}"
  local drc="$WORK/$(basename "$out").drc.json"
  say "── nostub: $(basename "$in") → $(basename "$out") (grid=$grid margin=$margin $extra)"
  fresh_drc "$in" "$drc"
  env PCB_HALO_MARGIN="$margin" bash state/pcbnew_py.sh state/patch_astar_nostub.py \
      "$in" "$drc" --out "$out" --grid "$grid" $extra >> "$LOG" 2>&1
  say "   ⇒ $(grep -ac '(segment' "$out" 2>/dev/null) 段 · $(grep -aE '── 补上' "$LOG" | tail -1)"
}

step_straight() {  # $1=输入板 $2=输出板
  local in="$1" out="$2"
  local drc="$WORK/$(basename "$out").drc.json"
  say "── straight: $(basename "$in") → $(basename "$out")"
  fresh_drc "$in" "$drc"
  bash state/pcbnew_py.sh state/fix_straight_links.py "$in" "$drc" --out "$out" >> "$LOG" 2>&1
  say "   ⇒ $(grep -ac '(segment' "$out" 2>/dev/null) 段"
}

if [ "$VALIDATE" = "--validate" ]; then
  say "★自校准模式: 用官方【路由产物】重放整条链 ⇒ 结果必须复现官方终板 (18092 段 / unc 45 / DRC 0)"
  # ★★注意: 输入必须是【路由产物】(13407 段), **不是官方终板**(18092 段) ⇒ 否则就是拿终板重放 ⇒ 必然对不上
  IN="${ROUTE:-/tmp/board_last_good_v44_R.kicad_pcb}"
  say "   输入 = $IN ($(grep -ac '(segment' "$IN" 2>/dev/null) 段)"
else
  IN="$ROUTE"
fi

# ① nostub125
step_nostub "$IN" "$WORK/s1_nostub125.kicad_pcb" 0.125 0.125
# ② straight ×5 (★参数照官方那次: ★width 默认 0.25/0.20 扫描 + detour)
CUR="$WORK/s1_nostub125.kicad_pcb"
for i in 1 2 3 6 7; do
  step_straight "$CUR" "$WORK/s2_straight${i}.kicad_pcb"
  CUR="$WORK/s2_straight${i}.kicad_pcb"
done
# ③ combo
step_nostub "$CUR" "$WORK/s3_combo.kicad_pcb" 0.125 0.125
# ④⑤ combo2 / combo3 (★官方那次: 输入都是 _combo ⇒ 各自独立从 combo 出发)
step_nostub "$WORK/s3_combo.kicad_pcb" "$WORK/s4_combo2.kicad_pcb" 0.125 0.125
step_nostub "$WORK/s3_combo.kicad_pcb" "$WORK/s4_combo3.kicad_pcb" 0.125 0.125 --max-dist 15
# ⑥ nostub_loose (★margin 0.0625 = 网格半格 ⇒ 这才是"loose"的关键)
step_nostub "$WORK/s4_combo3.kicad_pcb" "$WORK/final_chain.kicad_pcb" 0.125 0.0625

say "★链跑完 ⇒ 终板 $WORK/final_chain.kicad_pcb"
say "   段数 = $(grep -ac '(segment' "$WORK/final_chain.kicad_pcb" 2>/dev/null) (★官方终板 = 18092)"
bash state/pcbnew_py.sh state/check_pcb_drc.py "$WORK/final_chain.kicad_pcb" 2>&1 | grep -E "C3 |C4 " | tee -a "$LOG"
