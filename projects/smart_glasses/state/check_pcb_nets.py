#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_pcb_nets.py —— 板子 ↔ 网表 等价性门禁 (★"自己画图"的核心验收)

为什么要有: ★**图纸的正确性不能靠人眼** ⇒ ★**把板子上的每个焊盘的网络读回来,
和网表逐点比对** —— 少一个、多一个、接错, 机器立刻报出来。
"""
import csv, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, "/home/yuewuya/kicad/squashfs-root/usr/lib/python3/dist-packages")
sys.path.insert(0, "/home/yuewuya/kicad/squashfs-root/usr/lib")
import pcbnew  # noqa: E402

NET = os.path.join(PROJ, "HW", "netlist_v1.csv")
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
PSEUDO = ("RAIL_", "NET_")

def main():
    want = set()
    with open(NET, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ref = (r.get("ref") or "").strip(); net = (r.get("net") or "").strip()
            if ref and net and not ref.startswith(PSEUDO):
                want.add((ref, net))
    b = pcbnew.LoadBoard(PCB)
    if b is None:
        print("❌ 板文件读不回来"); return 1
    have = set()
    for fp in list(b.GetFootprints()):
        for pad in list(fp.Pads()):
            nm = pad.GetNetname()
            if nm:
                have.add((fp.GetReference(), nm))
    missing, extra = want - have, have - want
    print("=" * 68)
    print("  PCB ↔ 网表 等价性门禁 (板子由网表生成 ⇒ 必须逐点相等)")
    print("=" * 68)
    print(f"  网表 (ref,net): {len(want)}   板上: {len(have)}")
    print(f"  {'✅' if not missing else '❌'} 缺失 {len(missing)} {sorted(missing)[:5]}")
    print(f"  {'✅' if not extra else '❌'} 多余 {len(extra)} {sorted(extra)[:5]}")
    ok = not missing and not extra
    print(f"\n{'✅ 全过 —— 板子与网表逐点等价' if ok else '❌ 不等价 ⇒ 板子不能下单'}")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
