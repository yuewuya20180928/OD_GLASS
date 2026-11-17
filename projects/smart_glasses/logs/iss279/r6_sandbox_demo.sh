#!/bin/bash
# ★★ISS-279 · 沙盒正向演示: 「改板 md5 ⇒ SW 侧 R6 从绿变红」★★
# ★**真盘零写入**: 全程只在 /tmp 沙盒副本里改, 真盘的 5 件受保护文件跑前跑后逐字节不变 ★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
SB=/tmp/iss279_r6_demo
LOG="$PROJ/logs/iss279/r6_sandbox_demo.log"

mkdir -p "$(dirname "$LOG")"
exec > >(tee "$LOG") 2>&1

echo "###############################################################################"
echo "# ISS-279 · 沙盒正向演示 (★真盘零写入★)"
echo "# 时间: $(date '+%F %T %Z')"
echo "###############################################################################"
echo ""
echo "=== [0] 真盘基线 md5 (跑前) ==="
cd "$PROJ" || exit 9
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
BEFORE_BOARD=$(md5sum HW/PCB/demo_mainboard.kicad_pcb | cut -d' ' -f1)
echo ""

echo "=== [1] 建沙盒副本 (HW + SW + HANDOFF) ==="
rm -rf "$SB"
mkdir -p "$SB"
cp -a "$PROJ/HW" "$PROJ/SW" "$PROJ/HANDOFF" "$SB/" || exit 9
echo "沙盒 = $SB"
echo ""

echo "=== [2] 沙盒里改板【之前】跑 R6 (★期望 rc=0 绿★) ==="
python3 "$SB/SW/tools/check_demo_panel_spec.py" --root "$SB"
RC_BEFORE=$?
echo ">>> rc = $RC_BEFORE"
echo ""

echo "=== [3] 沙盒里改板 (★只动沙盒的板文件, 真盘一个字不许动★) ==="
python3 - "$SB" <<'PY'
import sys
sb = sys.argv[1]
p = sb + "/HW/PCB/demo_mainboard.kicad_pcb"
with open(p, "ab") as f:
    f.write(b"\n")          # ★只加一个换行字节 ⇒ md5 变, 内容语义不变 ★
import hashlib
h = hashlib.md5(open(p, "rb").read()).hexdigest()
print("沙盒板文件新 md5 =", h)
PY
echo ""

echo "=== [4] 沙盒里改板【之后】再跑 R6 (★期望 rc=1 红 + 点名「硬保护: 受保护文件 md5 变了」★) ==="
python3 "$SB/SW/tools/check_demo_panel_spec.py" --root "$SB"
RC_AFTER=$?
echo ">>> rc = $RC_AFTER"
echo ""

echo "=== [5a] 沙盒里【只】改台账 §1 锚点块里的板 md5 (★板没动★) ⇒ 期望 rc=1 (锚点被手改当场被抓) ==="
cp -a "$PROJ/HW/PCB/demo_mainboard.kicad_pcb" "$SB/HW/PCB/demo_mainboard.kicad_pcb"
cp -a "$PROJ/SW/SW_MD5_BASELINE_LEDGER.md" "$SB/SW/SW_MD5_BASELINE_LEDGER.md"
python3 - "$SB" <<'PY'
import sys
sb = sys.argv[1]
lp = sb + "/SW/SW_MD5_BASELINE_LEDGER.md"
t = open(lp, encoding="utf-8").read()
old = "611b869e13518c3c023fb178f91a0075"
new = "611b869e13518c3c023fb178f91a0076"
assert old in t, "台账里找不到板 md5 字面量"
open(lp, "w", encoding="utf-8").write(t.replace(old, new))
print("沙盒台账锚点被手改成:", new)
PY
python3 "$SB/SW/tools/check_demo_panel_spec.py" --root "$SB"
RC_ANCHOR_ONLY=$?
echo ">>> rc = $RC_ANCHOR_ONLY (期望 1)"
echo ""

echo "=== [5b] ★★沙盒里【板改了 + 台账锚点也手改成新 md5】⇒ 期望 rc=0 ★★"
echo "=== ★★这一条 = 「手改 md5 就能凑绿」这个洞【确实存在】的正面证据 = 本单 §4 存在理由★★ ==="
cp -a "$PROJ/HW/PCB/demo_mainboard.kicad_pcb" "$SB/HW/PCB/demo_mainboard.kicad_pcb"
cp -a "$PROJ/SW/SW_MD5_BASELINE_LEDGER.md" "$SB/SW/SW_MD5_BASELINE_LEDGER.md"
python3 - "$SB" <<'PY'
import sys, hashlib
sb = sys.argv[1]
p = sb + "/HW/PCB/demo_mainboard.kicad_pcb"
with open(p, "ab") as f:
    f.write(b"\n")
h = hashlib.md5(open(p, "rb").read()).hexdigest()
lp = sb + "/SW/SW_MD5_BASELINE_LEDGER.md"
t = open(lp, encoding="utf-8").read()
old = "611b869e13518c3c023fb178f91a0075"
assert old in t, "台账里找不到板 md5 字面量"
open(lp, "w", encoding="utf-8").write(t.replace(old, h))
print("沙盒板新 md5 =", h, "· 台账锚点也已手改成同一个值")
PY
python3 "$SB/SW/tools/check_demo_panel_spec.py" --root "$SB"
RC_ANCHOR=$?
echo ">>> rc = $RC_ANCHOR (期望 0 ⇒ 证明【改板 + 手改锚点 md5】就能凑绿 ⇒ 洞确实存在)"
echo ""

echo "=== [6] 真盘 md5 (跑后) —— 必须与 [0] 逐字节相同 ★"
cd "$PROJ" || exit 9
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
AFTER_BOARD=$(md5sum HW/PCB/demo_mainboard.kicad_pcb | cut -d' ' -f1)
echo ""

echo "=== [7] 结论 ==="
if [ "$BEFORE_BOARD" = "$AFTER_BOARD" ]; then
  echo "✅ 真盘板 md5 跑前跑后逐字节不变: $BEFORE_BOARD"
else
  echo "❌ 真盘板 md5 变了: $BEFORE_BOARD → $AFTER_BOARD  (★本演示失败★)"
fi
echo "沙盒 [2] 改板前 R6 rc = $RC_BEFORE (期望 0)"
echo "沙盒 [4] 改板后 R6 rc = $RC_AFTER (期望 1)"
echo "沙盒 [5a] 只手改台账锚点后 R6 rc = $RC_ANCHOR_ONLY (期望 1)"
echo "沙盒 [5b] 改板 + 手改台账锚点后 R6 rc = $RC_ANCHOR (期望 0 ⇒ 洞存在)"
rm -rf "$SB"
echo ""
echo "=== 演示结束 ==="
