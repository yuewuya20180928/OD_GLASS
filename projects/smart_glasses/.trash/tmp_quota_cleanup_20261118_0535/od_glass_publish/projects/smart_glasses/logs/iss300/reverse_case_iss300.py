#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reverse_case_iss300.py —— ISS-300 反向用例【独立复现脚本】(★沙盒副本上跑, 真盘一个字节不许动★)

干什么:
  在 MECH/ + HW/ 的【真拷贝沙盒】里, 把 1 个开口坐标常量篡改成越界值
  ⇒ ★**汇总闸必须红 + 必须点名是哪一道红了** ★
  ⇒ 恢复 ⇒ ★**必须回绿** ★
  ⇒ 最后打印【真盘 6 件受保护文件的 md5 前后对照】⇒ ★**证明真盘一个字节不许动** ★

跑法:
    python3 logs/iss300/reverse_case_iss300.py          # rc=0 = 反向用例全抓到
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
GATE = os.path.join(PROJ, "MECH", "check_onepass_mech_release.py")

spec = importlib.util.spec_from_file_location("release_gate_iss300", GATE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

PROTECTED = (
    "HW/PCB/demo_mainboard.kicad_pcb",
    "HW/PCB/demo_mainboard.kicad_pro",
    "HW/netlist_v1.csv",
    "HW/netlist_v1_pins.csv",
    "HW/BOM_v1.csv",
    "HW/SCHEMATIC_LANDING_V1_LANDED.md",
)
CALIB = os.path.join("MECH", "BOARD_PORT_OPENING_S6_FRAME_CALIBER.md")
TARGET = "MECH/check_board_frame_coords.py"


def md5(p):
    return mod.md5_of(p)


def show(title):
    print("")
    print("=" * 96)
    print(title)
    print("=" * 96)


def run_and_report(root, tag):
    res = mod.run_all(root, mod.GATES, mod.GATE_TIMEOUT)
    for i, r in enumerate(res, 1):
        mark = "✅ 绿" if r["ok"] else "❌ 红"
        rc = "None" if r["rc"] is None else str(r["rc"])
        print("  [%d/6] %-42s rc=%-5s %s" % (i, r["rel"], rc, mark))
        if not r["ok"]:
            print("        ★点名详情: %s" % r["detail"][:400])
    reds = [r for r in res if not r["ok"]]
    print("  ⇒ 汇总: 绿 %d / 红 %d" % (len(res) - len(reds), len(reds)))
    return res


def main():
    ok = True
    show("【0】真盘 6 件受保护文件 · 篡改【前】基线")
    before = {rel: md5(os.path.join(PROJ, rel)) for rel in PROTECTED}
    for rel, m in before.items():
        print("  %s  %s" % (m, rel))
    mt = os.stat(os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")).st_mtime_ns
    print("  板 mtime(ns) = %d" % mt)

    sb = mod.make_sandbox(PROJ, "iss300_reverse_case")
    print("")
    print("  沙盒 = %s" % sb)
    print("  ★沙盒里 MECH/ 与 HW/ 是【真拷贝】⇒ 沙盒里改的绝不会碰到真件★")

    show("【1】沙盒基线 (★6 道闸应当全绿★)")
    base = run_and_report(sb, "baseline")
    if any(not r["ok"] for r in base):
        print("  ✗ 基线就红 ⇒ 反向用例无意义")
        return 2

    show("【2】★篡改 1 个开口坐标常量★ (port_open_uart_bench.y0 66.300 ⇒ 52.000)")
    p_sb = os.path.join(sb, CALIB)
    orig = open(p_sb, encoding="utf-8").read()
    sb_before = md5(p_sb)
    changed = mod._mutate_calib_rect(sb, "port_open_uart_bench", "y0", "66.300", "52.000")
    sb_after = md5(p_sb)
    print("  真改了 = %s   md5 %s ⇒ %s" % (changed, sb_before[:12], sb_after[:12]))
    print("  ★这个矩形挪进 SoM P3/P4 的 Y 带 ⇒ 该闸 C2「窗口不得压 SoM 座」必红★")
    if not changed or sb_before == sb_after:
        print("  ✗ 没能真改到目标")
        return 2

    show("【3】★篡改后跑汇总闸 ⇒ 必须红 + 必须点名★")
    red = run_and_report(sb, "mutated")
    reds = [r for r in red if not r["ok"]]
    named = [r for r in reds if r["rel"] == TARGET]
    others = [r for r in red if r["rel"] != TARGET]
    print("  ★红的道 = %s" % [r["rel"] for r in reds])
    print("  ★点名的道 = %s" % [r["rel"] for r in named])
    print("  ★其余 5 道仍绿 = %s" % all(r["ok"] for r in others))
    if not (len(reds) == 1 and named and all(r["ok"] for r in others)):
        print("  ✗ 反向用例没达到「汇总红 + 点名 + 其余仍绿」")
        ok = False

    show("【4】★被点名那道闸的原始输出 (★原样贴, 供人工看它到底判了什么红★)")
    raw = subprocess.run([sys.executable, os.path.join(sb, TARGET)], cwd=sb,
                         capture_output=True, text=True, timeout=300)
    print("  (原始 rc = %d)" % raw.returncode)
    print(raw.stdout[-4000:])
    if raw.stderr.strip():
        print("  --- stderr ---")
        print(raw.stderr[-1500:])

    show("【5】★恢复 ⇒ 必须回绿★")
    open(p_sb, "w", encoding="utf-8").write(orig)
    print("  恢复后沙盒副本 md5 = %s (篡改前 = %s) ⇒ 相同 = %s"
          % (md5(p_sb)[:12], sb_before[:12], md5(p_sb) == sb_before))
    green = run_and_report(sb, "restored")
    if any(not r["ok"] for r in green):
        print("  ✗ 恢复后没有回绿")
        ok = False

    show("【6】★真盘 6 件受保护文件 · 篡改【后】对照 ⇒ 真盘一个字节不许动★")
    after = {rel: md5(os.path.join(PROJ, rel)) for rel in PROTECTED}
    for rel in PROTECTED:
        same = before[rel] == after[rel]
        print("  %s  %-42s 与前面相同 = %s" % (after[rel], rel, same))
        if not same:
            ok = False
    mt2 = os.stat(os.path.join(PROJ, "HW/PCB/demo_mainboard.kicad_pcb")).st_mtime_ns
    print("  板 mtime(ns) = %d  ⇒ 与前面相同 = %s" % (mt2, mt == mt2))
    if mt != mt2:
        ok = False

    import shutil
    shutil.rmtree(sb, ignore_errors=True)

    show("【结论】")
    print("  %s" % ("✅ 反向用例全抓到 (汇总红 + 点名 + 恢复回绿 + 真盘零变化)"
                    if ok else "❌ 有项没达到"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
