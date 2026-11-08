#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cmp_pcb_geom.py —— ★★比较两块 PCB 的【几何等价性】(★判"复现没复现"的正确工具)

★★★**★为什么必须有这个脚本 (★2026-11-09 夜里踩出来的)★★★**
  ★**md5 不能用来判"复现"** ⇒ ★**KiCad 每次存盘都重新生成 uuid ⇒ ⇒ md5 天生不可能逐位相同**
  ⇒ ★★**本项目因此判错 3 次 (★每一次都差点把一条正确的路线判死)** ★★
    ① "margin=0.20 跑出 17585 段但 md5 不同 ⇒ 配方差最后一步" ⇒ ★**几何集合 17473 条全同 ⇒ 配方命中**
    ② "复现链只到 17695 ⇒ 此路线判死" ⇒ ★**换对 margin ⇒ 18092 全同**
    ③ "final_chain 17731 段 ⇒ 复现成功" ⇒ ★**段数差 361 ⇒ 根本没复现**
  ⇒ ★★★**⇒ 判复现必须比【几何集合】(★忽略 uuid/tstamp) ⇒ ★本脚本就是那个判据** ★★★

★★★★**★用法** ★★★★
  python3 state/cmp_pcb_geom.py <板A.kicad_pcb> <板B.kicad_pcb>
    ⇒ 打印 ① 段数 ② 几何集合是否相同 ③ 只差在哪
    ⇒ rc=0 ⇒ 两板【几何等价】(★可当复现成功的凭据)
    ⇒ rc=1 ⇒ 【不等价】(★并打印差集样例 ⇒ 便于定位)

  --fast   ★只比段数+几何集合 (★默认, 已是快的)
  --vias   ★额外比过孔 (★默认也比, ★只是多几行)
  --zones  ★额外比铜皮区数

★★★★**★它比什么 (★逐项都有出处)** ★★★★
  · 走线 (segment): 起点 / 终点 / 线宽 / 层 / 网名   ← ★**几何等价的核心**
  · 过孔 (via): 位置 / 尺寸 / 钻孔 / 层 / 网名
  · 铜皮 (zone): 数量

★**不比什么 (★刻意不比)**: ★**uuid / tstamp** ⇒ ★**因为它们每次存盘都变 ⇒ 比了必然不等**
"""
import argparse
import os
import re
import sys

SEG = re.compile(
    r"\(segment\s*\n\s*\(start ([-\d.]+) ([-\d.]+)\)\s*\n\s*"
    r"\(end ([-\d.]+) ([-\d.]+)\)\s*\n\s*\(width ([\d.]+)\)\s*\n\s*"
    r'\(layer "([^"]+)"\)\s*\n\s*\(net "([^"]+)"\)'
)
VIA = re.compile(
    r"\(via\s*\n\s*\(at ([-\d.]+) ([-\d.]+)\)\s*\n\s*\(size ([\d.]+)\)\s*\n\s*"
    r"\(drill ([\d.]+)\)\s*\n\s*\(layers ([^)]+)\)\s*\n\s*"
    r'\(net "([^"]+)"\)'
)
ZONE = re.compile(r"\(zone\b")


def parse(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        t = f.read()
    return (
        set(m.groups() for m in SEG.finditer(t)),
        set(m.groups() for m in VIA.finditer(t)),
        len(ZONE.findall(t)),
    )


def show_diff(name, only_a, only_b, limit=5):
    print(f"  ── {name}: 仅A {len(only_a)} · 仅B {len(only_b)}")
    for x in sorted(only_a)[:limit]:
        print(f"     仅A: {x}")
    for x in sorted(only_b)[:limit]:
        print(f"     仅B: {x}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--vias", action="store_true")
    ap.add_argument("--zones", action="store_true")
    args = ap.parse_args()

    for p in (args.a, args.b):
        if not os.path.isfile(p):
            print(f"❌ 板不存在: {p}")
            return 2

    sa, va, za = parse(args.a)
    sb, vb, zb = parse(args.b)

    print(f"板A: {os.path.basename(args.a)}")
    print(f"  走线 {len(sa)} 条 · 过孔 {len(va)} 个 · 铜皮 {za} 区")
    print(f"板B: {os.path.basename(args.b)}")
    print(f"  走线 {len(sb)} 条 · 过孔 {len(vb)} 个 · 铜皮 {zb} 区")
    print()

    ok = True

    print("── ① 走线几何集合 (★起点/终点/线宽/层/网名, ★忽略 uuid) ──")
    if sa == sb:
        print(f"  ✅ 完全相同 ({len(sa)} 条)")
    else:
        ok = False
        print(f"  ❌ 不同 ⇒ ★**不是同一块铜**")
        show_diff("走线", sa - sb, sb - sa)

    if not args.fast:
        print()
        print("── ② 过孔 (★位置/尺寸/钻孔/层/网名) ──")
        if va == vb:
            print(f"  ✅ 完全相同 ({len(va)} 个)")
        else:
            ok = False
            print(f"  ❌ 不同")
            show_diff("过孔", va - vb, vb - va)

    if args.zones:
        print()
        print("── ③ 铜皮区数 ──")
        if za == zb:
            print(f"  ✅ 相同 ({za} 区)")
        else:
            ok = False
            print(f"  ❌ 不同: A={za} B={zb}")

    print()
    if ok:
        print("★★★ 结论: 两板【几何等价】⇒ ★**复现成功** (★md5 不同只是 uuid 随机, ★不是问题)")
        return 0
    print("★★★ 结论: 两板【不等价】⇒ ★**复现未成功** ⇒ ★别拿去跟官方板比")
    return 1


if __name__ == "__main__":
    sys.exit(main())
