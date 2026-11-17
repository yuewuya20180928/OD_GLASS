#!/bin/bash
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
echo "=== [1] python3 MECH/check_mech_verdict_freshness.py ==="
python3 MECH/check_mech_verdict_freshness.py; echo "rc=$?"
echo "=== [2] python3 MECH/check_mech_verdict_freshness.py --selftest ==="
python3 MECH/check_mech_verdict_freshness.py --selftest; echo "rc=$?"
echo "=== [3] python3 MECH/check_onepass_mech_sync.py ==="
python3 MECH/check_onepass_mech_sync.py >/dev/null 2>&1; echo "rc=$?"
echo "=== [4] python3 MECH/check_onepass_struct_crosscheck.py ==="
python3 MECH/check_onepass_struct_crosscheck.py >/dev/null 2>&1; echo "rc=$?"
echo "=== [5] python3 state/merge.py ==="
python3 state/merge.py 2>&1 | tail -2; echo "rc=${PIPESTATUS[0]}"
echo "=== [6] python3 state/gate_check.py ==="
python3 state/gate_check.py 2>&1 | sed -n '1,10p'; echo "rc=${PIPESTATUS[0]}"
echo "=== [7] grep -c iss295 state/fragments/mech.yaml ==="
grep -c iss295 state/fragments/mech.yaml
echo "=== [8] md5sum 受保护 5 件 ==="
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
echo "=== [9] 板 mtime ==="
stat -c '%y %n' HW/PCB/demo_mainboard.kicad_pcb
echo "=== [10] 老行留痕自证 (XCHK L1~L2161 与备份逐字节相同) ==="
diff <(sed -n '1,2161p' logs/iss295/BOARD_ONEPASS_STRUCT_CROSSCHECK.md.cont2.bak) <(sed -n '1,2161p' MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md) && echo "老行区未变 rc=0"
echo "=== [11] 两页现状句逐字一致 ==="
python3 - <<'PY'
a=open("MECH/BOARD_ONEPASS_MECH_SYNC.md",encoding="utf-8").read()
b=open("MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md",encoding="utf-8").read()
C=("【现状句 · ISS-295 · 帧 `B160x100`】USB-C 边开口规格已补: 开口 `PORT_OPEN_USBC` = X 132.995..147.005 @ 板边 Y = 0 · 必须清空区 X 133.895..146.105 · h 三档 0.90/2.54/4.00 · Z 向窗口 `OPEN_Y_eff(h)` = 4.60 / 4.60 / 5.80")
print("MSYNC 含现状句:", C in a, "| XCHK 含现状句:", C in b, "| 两页逐字一致:", (C in a) and (C in b))
PY
