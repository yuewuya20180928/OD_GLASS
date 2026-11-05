#!/usr/bin/env bash
# board_publish_gate.sh —— ★**板级发布闸 (独立可单测)**
# 用法:
#   bash state/board_publish_gate.sh <项目目录>                        # 只判 (rc 0=准进 / 1=拦下)
#   bash state/board_publish_gate.sh <项目目录> --withdraw <发布树>     # 判 + 拦下时把板/派生产物从发布树撤下
#   bash state/board_publish_gate.sh --selftest                       # 单测 (6 个分支, 含撤下逻辑)
# ★**参数 = 项目目录本身** (不是含 projects/smart_glasses 的树根)
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
# ★★2026-11-05 09:47 新增 --withdraw (实测事故二):
#   发布脚本里包裹闸门的那句 `if [ -f "$PCB_REL" ]` 测的是**发布树**里的板路径,
#   而 rsync 早就把板从发布树排除了 ⇒ ⇒ **闸门整块从来没跑过** ⇒⇒
#   ⇒⇒ 拦下时的"板级隔离"(撤板 + 撤 Gerber/钻孔/坐标/贴片) 也从来没执行过
#   ⇒⇒ 结果: 坏板 (DRC 2) 的 32 个 Gerber 一直躺在公开仓里 (GitHub contents API 实测 32 项)
#   ⇒⇒ 修法: ① 闸门本体接 --withdraw (撤下逻辑归到**可单测**的独立脚本里)
#             ② 发布脚本的包裹条件改测**源树**的板 (`$PROJ/HW/PCB/demo_mainboard.kicad_pcb`)
#   ⇒⇒ **撤下路径必须同时覆盖两份 Gerber**: `HW/PCB/gerbers/` (顶层副本) + `HW/PCB/production/gerbers/`
set -u

PCB_REL="HW/PCB/demo_mainboard.kicad_pcb"
PUB=""

# ---- 撤下模式: 板级隔离 (板 + 派生产物 一起撤, 历史里保留) ----
# ★必须覆盖**两份** Gerber 副本 (实测: 顶层 `HW/PCB/gerbers/` 与 `HW/PCB/production/gerbers/`
#   文件名集合相同 + md5 逐个相同) —— 少撤一份 = 坏板的投产文件还留在公开仓里
withdraw_from_publish_tree() {
  local pub="$1"
  local rel_pcb="projects/smart_glasses/HW/PCB/demo_mainboard.kicad_pcb"
  ( cd "$pub" 2>/dev/null || exit 1
    git rm -q --cached --ignore-unmatch "$rel_pcb" >/dev/null 2>&1 || true
    rm -f "$rel_pcb" >/dev/null 2>&1 || true
    for _p in "projects/smart_glasses/HW/PCB/gerbers" \
              "projects/smart_glasses/HW/PCB/production/gerbers" \
              "projects/smart_glasses/HW/PCB/production/drill" \
              "projects/smart_glasses/HW/PCB/production/pos" \
              "projects/smart_glasses/HW/PCB/production/assembly"; do
      git rm -r -q --cached --ignore-unmatch "$_p" >/dev/null 2>&1 || true
      rm -rf "$_p" >/dev/null 2>&1 || true
    done
    # ★★2026-11-05 10:22 **通用规则**: 发布树里**任何** *.kicad_pcb 都撤 (除 _frame_reference)
    #   理由 (实测): 远端树里还躺着 **3 块真板** —— 逐个列路径堵不住, 得用通用规则:
    #     ① HW/PCB/demo_mainboard.stackup.kicad_pcb  (17664 段 = 坏板 v25 的副本)
    #     ② state/.lastgood/board_8L_v23_GOOD_21980seg_20261105_0702.kicad_pcb (21980 段)
    #     ③ state/.lastgood/board_prev_promote_20261105_095249.kicad_pcb (17664 段)
    #   ⇒ 违反「仓库里没有板 = 诚实状态」(AGENTS.md 铁律③)
    #   ★保留 _frame_reference.kicad_pcb: 0 段走线 = 框参考, 不是可投产的板
    for _b in $(git ls-files '*.kicad_pcb'); do
      case "$_b" in
        */_frame_reference.kicad_pcb) continue ;;
      esac
      git rm -q --cached --ignore-unmatch "$_b" >/dev/null 2>&1 || true
      rm -f "$_b" >/dev/null 2>&1 || true
    done
    # ★★3D 模型 (.step) 也是**派生产物** (从板生成的) ⇒ 一样跟着板走
    for _s in $(git ls-files '*.step' '*.stp' '*.brd' '*.dsn'); do
      git rm -q --cached --ignore-unmatch "$_s" >/dev/null 2>&1 || true
      rm -f "$_s" >/dev/null 2>&1 || true
    done
    # ★★state/.lastgood/ 整个目录 (发布树 .gitignore 本来就列了它 ——
    #   ★但那条 pattern `state/.lastgood/` 因为带斜杠 ⇒ **只匹配根目录下的** ⇒
    #   ⇒ `projects/smart_glasses/state/.lastgood/` **没被忽略** ⇒ 8 个文件全进了仓)
    git rm -r -q --cached --ignore-unmatch "projects/smart_glasses/state/.lastgood" >/dev/null 2>&1 || true
    rm -rf "projects/smart_glasses/state/.lastgood" >/dev/null 2>&1 || true
    git add -A >/dev/null 2>&1 || true
  )
  echo "WITHDRAW|板 + 任何 *.kicad_pcb + Gerber(顶层&production) + 钻孔/坐标/贴片 + 3D模型 + state/.lastgood 已从发布树撤下 (历史里保留)"
}

bad() {
  echo "BAD|$1"
  # ★撤下模式: 拦下就当场把板 + 派生产物从发布树里撤 (历史里保留)
  #   ★必须在**判据失败的那一刻**撤 —— 事后补撤会漏 (本脚本就是为了防这个)
  if [ -n "$PUB" ]; then
    withdraw_from_publish_tree "$PUB"
  fi
  exit 1
}

# ============================================================================
# --selftest: 6 个分支 (★必须覆盖"该 BAD 的场景"★, AGENTS.md 铁律六)
# ============================================================================
_selftest() {
  local pass=0 fail=0
  local ROOT; ROOT="$(mktemp -d /tmp/gate_selftest.XXXXXX)"
  mk_tree() {   # mk_tree <根> <板内容> <ok_mtime?1:0> <unconnected> <drc>
    local r="$1" seg="$2" ok="$3" u="$4" d="$5"
    mkdir -p "$r/HW/PCB" "$r/state"
    printf '%s\n' "$seg" > "$r/HW/PCB/demo_mainboard.kicad_pcb"
    echo "{\"unconnected\": $u, \"drc_violations\": $d}" > "$r/HW/PCB/.layout_done.json"
    local M; M="$(stat -c %Y "$r/HW/PCB/demo_mainboard.kicad_pcb")"
    echo "$M" > "$r/state/.verified_board_mtime"
    [ "$ok" = "1" ] && echo "$M" > "$r/state/.verified_board_ok_mtime"
    return 0
  }
  chk() {  # chk <名> <期望rc> <实际rc>
    if [ "$2" = "$3" ]; then echo "  ✅ $1 (rc=$3)"; pass=$((pass+1));
    else echo "  ❌ $1 (期望 rc=$2, 实得 rc=$3)"; fail=$((fail+1)); fi
  }
  SEG_OK='  (segment (start 0 0) (end 1 1))'

  echo "[selftest] ① 好板 (验过且通过) ⇒ 应放行"
  mk_tree "$ROOT/g1" "$SEG_OK" 1 0 0
  bash "$0" "$ROOT/g1" >/dev/null 2>&1; chk "好板放行" 0 $?

  echo "[selftest] ② 没 .verified_board_ok_mtime ⇒ 应拦下 (★就是坏板那次的场景★)"
  mk_tree "$ROOT/g2" "$SEG_OK" 0 0 0
  OUT="$(bash "$0" "$ROOT/g2" 2>&1)"; RC=$?
  chk "无 ok_mtime 拦下" 1 $RC
  if echo "$OUT" | grep -q "BAD|"; then echo "  ✅ 输出了 BAD|"; pass=$((pass+1));
  else echo "  ❌ 没输出 BAD|"; fail=$((fail+1)); fi

  echo "[selftest] ③ unconnected≠0 ⇒ 应拦下"
  mk_tree "$ROOT/g3" "$SEG_OK" 1 82 0
  bash "$0" "$ROOT/g3" >/dev/null 2>&1; chk "unconnected=82 拦下" 1 $?

  echo "[selftest] ④ DRC≠0 ⇒ 应拦下"
  mk_tree "$ROOT/g4" "$SEG_OK" 1 0 2
  bash "$0" "$ROOT/g4" >/dev/null 2>&1; chk "DRC=2 拦下" 1 $?

  echo "[selftest] ⑤ 空板 (0 段走线) ⇒ 应拦下"
  mk_tree "$ROOT/g5" "  (kicad_pcb)" 1 0 0
  bash "$0" "$ROOT/g5" >/dev/null 2>&1; chk "空板拦下" 1 $?

  echo "[selftest] ⑥ ★撤下逻辑★ (发布树里有板 + 两份 Gerber ⇒ 拦下后必须全撤)"
  PUBT="$ROOT/pub"
  mkdir -p "$PUBT/projects/smart_glasses/HW/PCB/gerbers" \
           "$PUBT/projects/smart_glasses/HW/PCB/production/gerbers" \
           "$PUBT/projects/smart_glasses/HW/PCB/production/drill" \
           "$PUBT/projects/smart_glasses/HW/PCB/production/pos" \
           "$PUBT/projects/smart_glasses/HW/PCB/production/3d" \
           "$PUBT/projects/smart_glasses/state/.lastgood"
  echo "board" > "$PUBT/projects/smart_glasses/HW/PCB/demo_mainboard.kicad_pcb"
  echo "board" > "$PUBT/projects/smart_glasses/HW/PCB/demo_mainboard.stackup.kicad_pcb"
  echo "board" > "$PUBT/projects/smart_glasses/state/.lastgood/board_prev.kicad_pcb"
  echo "step" > "$PUBT/projects/smart_glasses/HW/PCB/production/3d/demo_mainboard.step"
  echo "frame" > "$PUBT/projects/smart_glasses/HW/PCB/_frame_reference.kicad_pcb"
  for _f in "$PUBT/projects/smart_glasses/HW/PCB/gerbers/a.gbr" \
            "$PUBT/projects/smart_glasses/HW/PCB/production/gerbers/a.gbr" \
            "$PUBT/projects/smart_glasses/HW/PCB/production/drill/a.drl" \
            "$PUBT/projects/smart_glasses/HW/PCB/production/pos/a.pos"; do echo x > "$_f"; done
  ( cd "$PUBT" && git init -q -b main && git add -A \
    && git -c user.email=t@t -c user.name=t commit -qm init ) >/dev/null 2>&1
  OUT="$(bash "$0" "$ROOT/g2" --withdraw "$PUBT" 2>&1)"; RC=$?
  chk "撤下模式 rc" 1 $RC
  if echo "$OUT" | grep -q "WITHDRAW|"; then echo "  ✅ 输出了 WITHDRAW|"; pass=$((pass+1));
  else echo "  ❌ 没输出 WITHDRAW|"; fail=$((fail+1)); fi
  LEFT="$(cd "$PUBT" && git ls-files | grep -cE 'gerbers|drill|\.pos$|\.step$|demo_mainboard.*\.kicad_pcb|\.lastgood' || true)"
  if [ "$LEFT" = "0" ]; then echo "  ✅ 发布树里板+任意kicad_pcb+Gerber+钻孔+坐标+3D+.lastgood 全部撤下 (tracked 剩 $LEFT)"; pass=$((pass+1));
  else echo "  ❌ 还剩 $LEFT 个 tracked 板/派生产物"; fail=$((fail+1)); fi
  LEFT_F="$(cd "$PUBT" && git ls-files | grep -cE '_frame_reference\.kicad_pcb' || true)"
  if [ "$LEFT_F" = "1" ]; then echo "  ✅ _frame_reference.kicad_pcb (0 段框参考) 保留 (剩 $LEFT_F)"; pass=$((pass+1));
  else echo "  ❌ _frame_reference 被误撤 (剩 $LEFT_F)"; fail=$((fail+1)); fi

  echo "[selftest] ⑦ 好板 ⇒ 撤下模式**不该**撤 (误撤 = 把能投产的板也删了)"
  PUBT2="$ROOT/pub2"
  mkdir -p "$PUBT2/projects/smart_glasses/HW/PCB/gerbers"
  echo x > "$PUBT2/projects/smart_glasses/HW/PCB/gerbers/a.gbr"
  ( cd "$PUBT2" && git init -q -b main && git add -A \
    && git -c user.email=t@t -c user.name=t commit -qm init ) >/dev/null 2>&1
  OUT="$(bash "$0" "$ROOT/g1" --withdraw "$PUBT2" 2>&1)"; RC=$?
  chk "好板放行 rc" 0 $RC
  LEFT2="$(cd "$PUBT2" && git ls-files | grep -cE 'gerbers' || true)"
  if [ "$LEFT2" = "1" ]; then echo "  ✅ 好板时 Gerber 保持不动 (剩 $LEFT2)"; pass=$((pass+1));
  else echo "  ❌ 好板时 Gerber 被误撤 (剩 $LEFT2)"; fail=$((fail+1)); fi

  echo "[selftest] 结果: $pass 通过 / $fail 失败"
  rm -rf "$ROOT"
  [ "$fail" = "0" ] || exit 1
  exit 0
}

# ---- 参数 ----
if [ "${1:-}" = "--selftest" ]; then
  _selftest
  exit $?
fi
TREE="${1:?用法: board_publish_gate.sh <项目目录> [--withdraw <发布树>] | --selftest}"
if [ "${2:-}" = "--withdraw" ]; then
  PUB="${3:?--withdraw 需要发布树目录}"
fi
PCB="$TREE/$PCB_REL"

[ -f "$PCB" ] || bad "源树里没有板 ($PCB_REL)"
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
    bad "板比上次量过的板新 (mtime=$B_M > V_M) 但没有落盘时刻印 ⇒ 没法证明它是完整落盘的那块"
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
