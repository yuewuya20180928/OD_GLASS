#!/bin/bash
# ★★【ISS-367 · mech-lead · 一键回滚】★★
# ★把「两处定点改写」逐字节还原成 2026-11-23 18:30 的原文 (★改前备份 = logs/iss367/10_pre_*.md★) ★
# ★用法: bash logs/iss367/12_ROLLBACK.sh          → 回滚两页 + 回滚规格页 ★
# ★      bash logs/iss367/12_ROLLBACK.sh --only-gates → 只回滚两页 (规格页保留) ★
# ★★回滚后请重跑: python3 MECH/check_onepass_s10_led_spec_sync.py  (预期 rc=1 · L3 红 · 那是【回到改前口径】的正常表现) ★★
set -u
cd /home/yuewuya/.openclaw/workspace/projects/smart_glasses
LOGD=logs/iss367

echo "=== 回滚前 md5 ==="
md5sum MECH/BOARD_ONEPASS_MECH_SYNC.md MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md

echo "=== ① 回滚两处定点改写 (★改前原文逐字节还原★) ==="
cp -f "$LOGD/10_pre_MECH_SYNC.md" MECH/BOARD_ONEPASS_MECH_SYNC.md
cp -f "$LOGD/10_pre_S6_CALIBER.md" MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md

if [ "${1:-}" != "--only-gates" ]; then
  echo "=== ② 回滚规格页 (★改前原文逐字节还原★) ==="
  cp -f "$LOGD/10_pre_SPEC_PAGE.md" MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md
fi

echo "=== 回滚后 md5 (★应等于 05_baseline_pre_CONT1.md 里的改前基线★) ==="
md5sum MECH/BOARD_ONEPASS_MECH_SYNC.md MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md MECH/BOARD_ONEPASS_S10_LED_SPEC_SYNC.md
echo "=== 改前基线 (对照) ==="
grep -A2 "待改两页 md5" "$LOGD/05_baseline_pre_CONT1.md"
grep "BOARD_ONEPASS_S10_LED_SPEC_SYNC.md" "$LOGD/05_baseline_pre_CONT1.md"

echo "=== 板/表 双证 (★回滚不许碰板★) ==="
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
stat -c '%y' HW/PCB/demo_mainboard.kicad_pcb
