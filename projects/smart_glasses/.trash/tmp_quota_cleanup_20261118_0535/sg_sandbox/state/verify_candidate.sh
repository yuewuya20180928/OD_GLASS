#!/usr/bin/env bash
# verify_candidate.sh -- ★★★**候选板四把尺子一次跑完 (★2026-11-08 21:5x 新增)** ★★★
#
# ★**为什么要有这个脚本 (★实测事故链)**:
#   ★**v69 臂**: 跑了 6 小时 ⇒ rc=1 ⇒ 结论"产物不可用" ⇒ 但板文件其实完好 (只是后缀错)
#     ⇒ ★**⇒ "跑完到底行不行"这件事, 之前是散在几个脚本里、每次只记得跑其中一个**
#     ⇒ ★**⇒ 结论下早了 (★"不可用"这个判断是在没量板的情况下下的)**
#   ★**⇒ 正解: 验收必须【一个入口、一次跑完四把尺子】⇒ 不许凭印象下结论**
#
# ★**四把尺子 (★缺一不可)**:
#   ① fresh DRC + unconnected: `state/check_pcb_drc.py <板>` ⇒ ★**DRC 必须 0 · unc 必须比官方板低**
#   ② 名单制闸: `state/compare_arm_official.py <候选> <官方板>` ⇒ ★**必须 ACCEPT**
#      (★硬指标: DRC=0 · 退铜名单空 · 差分死腿空 · 逐网孤岛不变多 · 至少一项变好)
#   ③ 闸自测: `state/compare_arm_official.py --self-test` ⇒ ★**ALL TESTS PASS (★否则第②步不可信)**
#   ④ 差分对审计: `tools/diff_pair_audit.py <板>` ⇒ ★**单边零铜对数 / Δ超差对数 ⇒ 与官方板逐条比**
#
# ★**用法**: `bash state/verify_candidate.sh <候选板> [官方板]`
# ★**注意**: ★**tools/diff_pair_audit.py 在【工作区根目录】不在项目里** ⇒ ★**本脚本自己 cd 到工作区根跑它**
set -u
PROJ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS="$(cd "$PROJ/../.." && pwd)"
CAND="${1:?用法: verify_candidate.sh <候选板> [官方板]}"
OFF="${2:-$PROJ/HW/PCB/demo_mainboard.kicad_pcb}"

echo "══════ ① fresh DRC + unconnected ══════"
bash "$PROJ/state/pcbnew_py.sh" "$PROJ/state/check_pcb_drc.py" "$CAND" 2>&1 | grep -vE "^$|Debug:" | tail -25

echo
echo "══════ ② 名单制闸 (候选 vs 官方) ══════"
python3 "$PROJ/state/compare_arm_official.py" "$CAND" "$OFF" 2>&1 | tail -22

echo
echo "══════ ③ 闸自测 ══════"
python3 "$PROJ/state/compare_arm_official.py" --self-test 2>&1 | tail -8

echo
echo "══════ ④ 差分对审计 (候选) ══════"
( cd "$WS" && python3 tools/diff_pair_audit.py "$CAND" 2>&1 | grep -E "单边零铜|Δ>0.13|segment 总数|^   [A-Z]" | head -30 )

echo
echo "══════ ④b 差分对审计 (官方板基线) ══════"
( cd "$WS" && python3 tools/diff_pair_audit.py "$OFF" 2>&1 | grep -E "单边零铜|Δ>0.13|segment 总数|^   [A-Z]" | head -30 )
