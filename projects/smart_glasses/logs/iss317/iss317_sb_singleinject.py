#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss317_sb_singleinject.py —— ISS-317 · T5-a / T7: 改名口径的【单射校验】

★ISS-314 §3-6 T5/T7 逐字设计★:
    T5 造法: 沙盒网表里放两个表侧 ref X 与 X_1
             (⇒ kicad_ref(X)=X_1, kicad_ref(X_1)=X_1 ⇒ 映射非单射)
    期望: ③ 红, 文案「★口径歧义: …」或「★单射校验失败 …」⇒ ★不许静默丢掉一个器件★
    T7: 「单射校验失败: X 与 X_1 都映到 X_1」

★本脚本是【改名清单生成器同款单射校验】的独立实现 (★口径单源 = state/gen_kicad_sch.py::kicad_ref()★)
★**只读** ⇒ 零写板 / 零落表 / 零重生成 / 零改闸 ★

用法:  python3 iss317_sb_singleinject.py <网表CSV> [<网表CSV> ...]
退出码: 0 = 单射成立 (无碰撞) · 1 = 单射不成立 (★单射校验失败★)
"""
import csv
import os
import sys

PSEUDO = ("RAIL_", "NET_")


def kicad_ref(ref):
    """★ISS-205 口径 (与 state/gen_kicad_sch.py::kicad_ref() 同源·逐字复刻★)"""
    r = (ref or "").strip()
    if r and r[-1].isdigit():
        return r
    return r + "_1"


def refs_of(net_csv):
    out = set()
    for r in csv.DictReader(open(net_csv, encoding="utf-8")):
        ref = (r.get("ref") or "").strip()
        if ref and not ref.startswith(PSEUDO):
            out.add(ref)
    return out


def check(net_csv):
    refs = refs_of(net_csv)
    fwd = {}
    rev = {}
    for r in sorted(refs):
        k = kicad_ref(r)
        fwd[r] = k
        rev.setdefault(k, []).append(r)
    collisions = {k: v for k, v in rev.items() if len(v) > 1}
    print("★单射校验 · %s" % net_csv)
    print("  表侧真实器件 ref 数        : %d" % len(refs))
    print("  改名后图上位号数 (去重后)  : %d" % len(rev))
    if not collisions:
        print("  ✅ 单射校验通过: 无碰撞 (★每个表侧 ref 映到唯一图上位号★)")
        return 0
    print("  ❌ ★单射校验失败: %d 组表侧 ref 映到同一个图上位号★" % len(collisions))
    for k, v in sorted(collisions.items()):
        print("     ★ %s  ←  %s" % (k, " 与 ".join(v)))
        for r in v:
            print("        · %s ⇒ %s" % (r, kicad_ref(r)))
    print("  ★⇒ 后果: 这 %d 个器件在【原理图侧】会被并成同一个位号 ⇒ "
          "板侧会出现同名封装 ⇒ 一个器件被静默丢掉 ★" % sum(len(v) - 1 for v in collisions.values()))
    return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    rc = 0
    for p in sys.argv[1:]:
        print()
        rc |= check(p)
    print()
    print("★总判定: %s" % ("❌ 单射校验失败" if rc else "✅ 全部单射成立"))
    sys.exit(rc)
