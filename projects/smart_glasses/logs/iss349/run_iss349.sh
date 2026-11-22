#!/usr/bin/env bash
# ★ISS-349 · 一条命令复现本单全部读数 (★项目总工 2026-11-23 01:4x 派活·hw-lead★)
#
# ★**性质**: 零写板 · 零落表 · 零改既有闸判定逻辑 · 零外发 · 不代拍 ★
# ★**沙盒一律落项目盘 `tmp/iss349/` (★`/tmp` 是带 userquota 的 tmpfs 且配额已打满 ⇒ 写 /tmp 会 EDQUOT ⇒ 假读数★) ★
#
# 用法:
#   bash logs/iss349/run_iss349.sh            # 全跑
#   bash logs/iss349/run_iss349.sh --quick    # 跳过最慢的 --selftest (★含端到端真跑生成器★)
set -uo pipefail

PROJ="/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LOGDIR="$PROJ/logs/iss349"
SBDIR="$PROJ/tmp/iss349"
export TMPDIR="$SBDIR/tmpdir"          # ★绝不落 /tmp★
mkdir -p "$LOGDIR" "$SBDIR/tmpdir"

QUICK=0
[ "${1:-}" = "--quick" ] && QUICK=1

cd "$PROJ"

banner() { echo; echo "════════════════════════════════════════════════════════════════════════════════"; echo "  $*"; echo "════════════════════════════════════════════════════════════════════════════════"; }

step() {   # step <标题> <命令...>
  local title="$1"; shift
  banner "$title"
  echo "\$ $*"
  "$@" 2>&1
  local rc=$?
  echo "--- rc=$rc ---"
  return $rc
}

# ── ① 板指纹 (前后双证) ───────────────────────────────────────────────
banner "① 板指纹 (★前后双证·零写板★)"
echo "\$ md5sum HW/PCB/demo_mainboard.kicad_pcb ; stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb"
md5sum HW/PCB/demo_mainboard.kicad_pcb
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb
echo "★期望: md5 = 611b869e13518c3c023fb178f91a0075 · mtime = 2026-11-06 07:07:17.362193413"

# ── ② 清单页 id 集合核对 (表 vs JSON) ─────────────────────────────────
banner "② 清单页 §2 表 vs §7 JSON 的 id 集合 (★逐个相等·不是只比个数★)"
python3 - "$PROJ" <<'PY'
import re, json, sys, os
p = os.path.join(sys.argv[1], "HW", "PCB", "BOARD_ONEPASS_PREFLIGHT.md")
txt = open(p, encoding="utf-8").read()
m2 = re.search(r"^##\s*§2\b(.*?)^##\s*§3\b", txt, re.S | re.M)
tbl = re.findall(r"^\|\s*★\*\*`([A-Za-z0-9_]+)`\*\*\s*★\s*\|", m2.group(1) if m2 else "", re.M)
mj = re.search(r"```json\s*(\{.*?\})\s*```", txt, re.S)
js = [it["id"] for it in json.loads(mj.group(1))["items"]]
print("§2 表行数 = %d · 唯一 id = %d" % (len(tbl), len(set(tbl))))
print("§7 JSON 条数 = %d · 唯一 id = %d" % (len(js), len(set(js))))
print("两集合逐一相等 ? %s" % (set(tbl) == set(js)))
print("只在表里 = %s · 只在 JSON 里 = %s" % (sorted(set(tbl) - set(js)), sorted(set(js) - set(tbl))))
print("B33_PIN_LAND_1P27 在表里 ? %s · 在 JSON 里 ? %s"
      % ("B33_PIN_LAND_1P27" in tbl, "B33_PIN_LAND_1P27" in js))
sys.exit(0 if (set(tbl) == set(js) and len(tbl) == len(js) == 33) else 1)
PY
echo "--- rc=$? ---"

# ── ③ 新闸 + 自测 (★端到端跑真生成器★) ────────────────────────────────
if [ "$QUICK" = "0" ]; then
  step "③ 新闸自测 (★R1/R2/R3/R4 + 正例·端到端跑真生成器★)" \
       python3 -B HW/check_preflight_regen_idempotent.py --selftest
fi
step "③ 新闸主模式 (★C1 表/JSON 同源 · C2 重跑幂等 · C3 来源在册 · C4 必需项★)" \
     python3 -B HW/check_preflight_regen_idempotent.py

# ── ④ 既有闸不许被本单弄红 ────────────────────────────────────────────
step "④ 覆盖度闸 (★钉板闸⑥·本单一个字未改★)" \
     python3 -B HW/check_onepass_preflight_coverage.py
step "④ ISS-289 现状值闸 (★读同一份页·本单一个字未改★)" \
     python3 -B HW/check_workpack_state_values.py

# ── ⑤ 蒸发复现 (★生成器里没有 B33 ⇒ 重跑 ⇒ 页回到 32 条 ⇒ 闸红★) ────
banner "⑤ 蒸发复现 (★沙盒里把生成器的 B33 那条删掉 ⇒ 重跑 ⇒ 页回到 32 条 ⇒ 闸红并点名★)"
SB="$SBDIR/run_repro"
rm -rf "$SB"; mkdir -p "$SB"
python3 -B HW/check_preflight_regen_idempotent.py --makesandbox "$SB"
python3 - "$SB" <<'PY'
import re, sys, os
sb = sys.argv[1]
g = os.path.join(sb, "state", "_iss277_build_preflight.py")
lines = open(g, encoding="utf-8").read().split("\n")
i0 = next(i for i, l in enumerate(lines) if '"B33_PIN_LAND_1P27"' in l)
i1 = next(i for i in range(i0, len(lines)) if lines[i].rstrip().endswith('"[实测]"),'))
del lines[i0:i1 + 1]
open(g, "w", encoding="utf-8").write("\n".join(lines))
print("★已从沙盒生成器里删掉 B33 那条 (★真生成器零动★)")
PY
PREFLIGHT_PROJ="$SB" python3 -B "$SB/state/_iss277_build_preflight.py" 2>&1 | tail -3
echo "--- 闸判 (★对沙盒页跑·GEN_PROJ 指向沙盒⇒生成器就是那个被删掉 B33 的★) ---"
PREFLIGHT_CHECKLIST="$SB/HW/PCB/BOARD_ONEPASS_PREFLIGHT.md" \
PREFLIGHT_GEN_PROJ="$SB" \
PREFLIGHT_SANDBOX="$SBDIR/run_repro_regen" \
  python3 -B HW/check_preflight_regen_idempotent.py 2>&1 | tail -14
echo "--- 闸 rc=${PIPESTATUS[0]} (★非 0 = 判红·正是本单要的★) ---"

# ── ⑥ 落表链 (★merge + gate_check★) ──────────────────────────────────
step "⑥ state/merge.py" python3 state/merge.py
step "⑥ state/gate_check.py (★Q1 必须 18/18★)" python3 state/gate_check.py

# ── ⑦ 板指纹 (后证) ───────────────────────────────────────────────────
banner "⑦ 板指纹 (★后证·逐字节未动★)"
md5sum HW/PCB/demo_mainboard.kicad_pcb
stat -c '%y %s' HW/PCB/demo_mainboard.kicad_pcb

banner "★跑完 · 本单性质: 零写板 · 零落表 · 零改既有闸判定逻辑 · 零外发 · 不代拍 ★"
