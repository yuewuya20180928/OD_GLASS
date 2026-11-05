#!/usr/bin/env bash
# board_publish_gate.sh —— ★**板级发布闸 (独立可单测)**
# 用法: bash state/board_publish_gate.sh <项目目录>   ★**参数 = 项目目录本身** (不是含 projects/smart_glasses 的树根)
# 退出码: 0 = 板准进仓库 · 1 = 拦下 (并打印原因)
# ★★判据 (三层, 全过才算):
#   ① 板不是空板 (段数 ≥ 1)
#   ② 板不比"上次量过的板"新 (除非有落盘时刻印交叉校验)
#   ③ ★**板验过且通过**: `.verified_board_ok_mtime` 存在且 == 板 mtime
#      且 `.layout_done.json` 的 unconnected == 0 且 drc_violations == 0
# ★★2026-11-05 09:20 新增③的原因 (实测事故):
#   v25 板 (焊盘短路 / DRC 2 / unconnected 82) 的自验 rc=1, 但脚本**无条件**写了
#   `.verified_board_mtime` ⇒ 发布闸把"mtime ≤ 量过的板"当**通过** ⇒⇒
#   ⇒⇒ 带短路的板 + 它出的 30 个 Gerber 被推进了 GitHub (commit f31814b)
set -u
TREE="${1:?用法: board_publish_gate.sh <项目目录>}"
PCB_REL="HW/PCB/demo_mainboard.kicad_pcb"
PCB="$TREE/$PCB_REL"
say() { echo "$1"; }
bad() { echo "BAD|$1"; exit 1; }

[ -f "$PCB" ] || bad "发布树里没有板"
SEG_C="$(grep -c '(segment' "$PCB" 2>/dev/null | head -1)"; SEG_C="${SEG_C:-0}"
[ "${SEG_C:-0}" -ge 1 ] || bad "官方板只有 $SEG_C 段走线 ⇒ 骨架/空板"

B_M="$(stat -c %Y "$PCB" 2>/dev/null | head -1)"; B_M="${B_M:-0}"
V_M="$(cat "$TREE/state/.verified_board_mtime" 2>/dev/null | head -1)"; V_M="${V_M:-0}"

if [ "${B_M:-0}" -gt "${V_M:-0}" ]; then
  LAND_REL="$TREE/HW/PCB/.layout_landed.json"
  L_AT="$(python3 -c "import json;print(int(json.load(open('$LAND_REL')).get('at',0)))" 2>/dev/null || echo 0)"
  L_TR="$(python3 -c "import json;print(int(json.load(open('$LAND_REL')).get('tracks',0)))" 2>/dev/null || echo 0)"
  if [ "${L_AT:-0}" -gt 0 ]; then
    D=$(( B_M > L_AT ? B_M - L_AT : L_AT - B_M ))
    if [ "$D" -gt 10 ] || [ "${SEG_C:-0}" -ne "${L_TR:-0}" ]; then
      bad "板 mtime=$B_M vs 落盘 at=$L_AT (差 ${D}s) · 板段数=$SEG_C vs 落盘段数=$L_TR ⇒ 板被中途存盘改过"
    fi
  else
    bad "板比上次量过的板新 (mtime=$B_M > $V_M) 但没有落盘时刻印 ⇒ 没法证明它是完整落盘的那块"
  fi
fi

# ---- 判据③: 验过且通过 ----
O_M="$(cat "$TREE/state/.verified_board_ok_mtime" 2>/dev/null | head -1)"; O_M="${O_M:-0}"
[ "${O_M:-0}" -gt 0 ] || bad "★没有 .verified_board_ok_mtime ⇒ 这块板**没通过自验** (⇒ 不可投产 ⇒ 不许进仓库)"
[ "$B_M" = "${O_M:-0}" ] || bad "★板 mtime=$B_M ≠ 验过通过的板 $O_M ⇒ 这块板自验后被改过"
LD_REL="$TREE/HW/PCB/.layout_done.json"
LD_U="$(python3 -c "import json;print(int(json.load(open('$LD_REL')).get('unconnected',-1)))" 2>/dev/null || echo -1)"
LD_D="$(python3 -c "import json;print(int(json.load(open('$LD_REL')).get('drc_violations',-1)))" 2>/dev/null || echo -1)"
[ "${LD_U:-1}" = "0" ] || bad "★自验记录 unconnected=$LD_U (必须 0)"
[ "${LD_D:-1}" = "0" ] || bad "★自验记录 DRC=$LD_D (必须 0)"

echo "OK|seg=$SEG_C mtime=$B_M unconnected=$LD_U DRC=$LD_D"
exit 0
