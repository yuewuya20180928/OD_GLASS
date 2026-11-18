#!/usr/bin/env bash
# ISS-297 · 6 道 HW 闸的「合法改板」通道自检 —— 一键复跑 (★带 /tmp 配额兜底★)
# ---------------------------------------------------------------------------
# ★**为什么有这份脚本 (★cont4 现场实测出来的, 不是猜的★)** ★
#   2026-11-18 05:5x 本机实跑: `HW/check_onepass_preflight_coverage.py --selftest`
#   与 `HW/check_workpack_state_values.py --selftest` 崩在
#     OSError: [Errno 122] Disk quota exceeded: ... -> '/tmp/iss277_selftest_xxx/.../demo_mainboard.kicad_pcb'
#   ⇒ ★**根因 = /tmp 是带 usrquota 的 tmpfs, 并发进程一多就装不下 4.9 MB 的板副本** ★
#   ⇒ ★**不是判据的问题**: 06:0x 同一台机重跑 ⇒ 6 道闸 `--selftest` 全绿 (21/21 · 25/25 · 20/20 …) ★
#   ⇒ ★**兜底办法 (★零改动闸本体★)**: 把 TMPDIR 指到配额宽裕的盘 (家目录盘 / 项目盘) ⇒
#      `tempfile.mkdtemp()` 认 TMPDIR ⇒ 沙盒落在家目录盘 ⇒ 不再撞 /tmp 的 usrquota ★
#
# ★**用法** (★在项目根跑★):
#     bash logs/iss297/run_iss297_selftests.sh
# ★**它只做两件事**: ① 设 TMPDIR ② 逐条跑 6 道闸的 `--selftest` 并打印原样 rc ★
# ★**零写板 · 零落表**: 本脚本不写任何受保护件, 沙盒全在临时目录里且跑完即删 ★
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT" || exit 2

# ★沙盒落点: 家目录盘 (★配额宽裕·不在带 usrquota 的 /tmp 上★) ⇒
export TMPDIR="${ISS297_TMPDIR:-$HOME/.cache/iss297_sbx}"
mkdir -p "$TMPDIR" || { echo "★TMPDIR 建不出来: $TMPDIR★"; exit 2; }
echo "★TMPDIR = $TMPDIR★"

rc_all=0
for g in check_fsin_rootcause check_g1a7_selection_landed check_onepass_commit_order \
         check_onepass_preflight_coverage check_pin_function_labels check_workpack_state_values; do
    echo "################ python3 HW/$g.py --selftest ################"
    python3 "HW/$g.py" --selftest 2>&1 | tail -6
    rc=${PIPESTATUS[0]}
    echo "rc=$rc"
    [ "$rc" -ne 0 ] && rc_all=1
    echo
done

echo "################ python3 HW/board_reboard.py --selftest ################"
python3 HW/board_reboard.py --selftest 2>&1 | tail -3
rc=${PIPESTATUS[0]}
echo "rc=$rc"
[ "$rc" -ne 0 ] && rc_all=1

echo
echo "★6+1 道自检总判定: $([ "$rc_all" -eq 0 ] && echo '全绿 ✅' || echo '有红 ❌')★"
echo "★受保护 5 件 md5 (★零写板自证★):"
md5sum HW/PCB/demo_mainboard.kicad_pcb HW/PCB/demo_mainboard.kicad_pro \
       HW/netlist_v1.csv HW/netlist_v1_pins.csv HW/BOM_v1.csv
exit "$rc_all"
