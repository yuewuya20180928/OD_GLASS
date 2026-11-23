#!/usr/bin/env bash
# ★★【ISS-365】沙盒重判实测驱动: 换 land 前 / 后 各跑四道 MECH 闸, 输出并排留证 ★★
set -u
PROJ=/home/yuewuya/.openclaw/workspace/projects/smart_glasses
SBX="$PROJ/tmp/iss365_sbx"
LOG="$PROJ/logs/iss365"
GATES="check_onepass_struct_crosscheck check_onepass_mech_sync check_board_frame_coords check_demo_struct_truth"

cd "$SBX" || exit 9

# ★★先把板副本恢复成原板 (★否则重跑时 BEFORE 会在【已换过】的板上跑 ⇒ BEFORE/AFTER 对比无效★) ★★
if [ -f HW/PCB/demo_mainboard_ORIG.kicad_pcb ]; then
  cp HW/PCB/demo_mainboard_ORIG.kicad_pcb HW/PCB/demo_mainboard.kicad_pcb
  echo "=== [RESTORE] 板副本已恢复成原板 (md5 $(md5sum HW/PCB/demo_mainboard.kicad_pcb | cut -c1-32)) ==="
fi

echo "=== [BEFORE] 板副本 = 原板 (md5 $(md5sum HW/PCB/demo_mainboard.kicad_pcb | cut -c1-32)) ==="
for g in $GATES; do
  timeout 110 python3 "MECH/$g.py" > "$LOG/sbx_before_${g}.txt" 2>&1
  echo "  $g rc=$?"
done

echo "=== [SWAP] 把 §1 的 25 件换成官方 land ==="
cp "$LOG/sbx_before_board_md5.txt" /dev/null 2>/dev/null || true
md5sum HW/PCB/demo_mainboard.kicad_pcb > "$LOG/sbx_before_board_md5.txt"
cd "$PROJ" || exit 9
timeout 110 bash state/pcbnew_py.sh logs/iss365/swap_iss365_sbx.py --sbx "$SBX" --mode swap 2>"$LOG/sbx_swap_stderr.txt" >"$LOG/sbx_swap_raw.txt"
python3 - <<'PY'
import json
t=open('/home/yuewuya/.openclaw/workspace/projects/smart_glasses/logs/iss365/sbx_swap_raw.txt',encoding='utf-8',errors='replace').read()
i=t.find('\n}\n')
d=json.loads(t[:i+3])
json.dump(d,open('/home/yuewuya/.openclaw/workspace/projects/smart_glasses/logs/iss365/sbx_swap_log.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print("  swapped %d 件" % len([x for x in d['log'] if x.get('status')=='SWAPPED']))
PY

cd "$SBX" || exit 9
echo "=== [AFTER] 板副本 = 换完 land (md5 $(md5sum HW/PCB/demo_mainboard.kicad_pcb | cut -c1-32)) ==="
for g in $GATES; do
  timeout 110 python3 "MECH/$g.py" > "$LOG/sbx_after_${g}.txt" 2>&1
  echo "  $g rc=$?"
done
md5sum HW/PCB/demo_mainboard.kicad_pcb > "$LOG/sbx_after_board_md5.txt"

echo "=== 真板复核 (必须逐字节不变) ==="
cd "$PROJ" && md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
  HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv | tee "$LOG/real_board_md5_after_sbx.txt"
