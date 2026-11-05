#!/usr/bin/env bash
# finish_line.sh —— ★**终点线: 选赢家 → 晋级官方板 → 重出投产包 → 全门禁 → 写证据**
# 用法: bash state/finish_line.sh <A|B|C|D>
# ★★为什么要有这条: 赢家落盘后还有 4 步 (晋级/投产包/门禁/证据) ⇒ 手做容易漏 ⇒ 一条跑完
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses || exit 1
ARM="${1:?用法: finish_line.sh <A|B|C|D>}"
# ★2026-11-05 10:35 支持前缀 (v26 / v27 / v28)
PREFIX="${PREFIX:-v26}"
PCB=HW/PCB/demo_mainboard.kicad_pcb
LOG="/tmp/${PREFIX}_${ARM}.log"

echo "════════ ① 臂对比 ════════"
PREFIX="$PREFIX" bash state/cmp_arms.sh

echo "════════ ② 晋级 臂 $ARM 到官方板 ════════"
bash state/promote_arm.sh "$ARM" 2>&1 | tail -35; _rc=${PIPESTATUS[0]}
if [ "$_rc" -ne 0 ]; then
  echo "  ❌ 晋级失败 (rc=$_rc) ⇒ ★**中止终点线** (不许拿半成品继续)"
  exit 1
fi

echo "════════ ②b 大电流网加铜皮 (★RAIL_DEMO_5V 实测 151mm×0.25mm ⇒ 扛不住 SoM 输入) ════════"
if [ -f state/add_power_pour.py ]; then
  bash state/pcbnew_py.sh state/add_power_pour.py "$PCB" RAIL_DEMO_5V 2>&1 | tail -4
  # ★★加铜皮会改板文件 (mtime 变) ⇒ ★**落盘印要跟着更新** ⇒ 不然"落盘时刻闸"会说"板被中途改过 ⇒ 不许量"
  python3 - "$PCB" <<'PY'
import json, os, sys, time
p = sys.argv[1]
seg = via = 0
for l in open(p, encoding="utf-8", errors="ignore"):
    s = l.lstrip()
    if s.startswith("(segment"): seg += 1
    elif s.startswith("(via"): via += 1
land = {"at": int(os.stat(p).st_mtime), "tracks": seg, "vias": via,
        "pcb": os.path.basename(p), "landed_at": int(time.time()),
        "note": "after power pour"}
json.dump(land, open(os.path.join(os.path.dirname(p), ".layout_landed.json"), "w",
                     encoding="utf-8"), ensure_ascii=False)
print("  落盘印(加铜皮后):", json.dumps(land, ensure_ascii=False))
PY
fi

echo "════════ ③ 重出投产资料包 (★Gerber/钻孔/贴片/BOM 都要跟着新板) ════════"
timeout 3600 bash state/gen_production_pack.sh > /tmp/prod_pack.log 2>&1
echo "  gen_production_pack rc=$?"
tail -6 /tmp/prod_pack.log

echo "════════ ④ 全门禁自验 (verify_and_release) ════════"
timeout 3600 bash state/verify_and_release.sh > /tmp/verify_final.log 2>&1
RC=$?
echo "  verify_and_release rc=$RC"
grep -E "unconnected items|DRC violations|check_pcb_nets rc|check_pcb_drc|chain_gate rc|stage_gate rc|G1|放行" /tmp/verify_final.log | head -14

echo "════════ ⑤ 放行章状态 ════════"
if [ -f state/.auto_release_done ]; then
  echo "  ✅ 放行章存在: $(cat state/.auto_release_done)"
else
  echo "  ★ 放行章不存在 ⇒ 未放行 (★只有 unconnected=0 + DRC=0 + 全门禁 rc=0 才盖章)"
fi
echo "════════ ⑥ 最终证据 ════════"
bash state/board_report.sh "$PCB" "$LOG" 2>&1 | head -12
date '+%H:%M:%S 完成'
