#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cmp_unc_sets.py —— ★★比较两张板的"未连接集合" (★判"是否同工艺"的辅助判据)

★**为什么需要它 (★2026-11-09 05:5x)**: ★**"unc 数量相同"太弱** (★官方 45 / 复现 45 可能是完全不同的 45 条)
⇒ ★**必须比【集合】, 而且要比对【正确的层级】** ⇒ ★★**这三条判据的强弱依次是** ★★:
  ① ★**网名集合** (★最强, ★最稳) ⇒ 官方 43 vs 复现 43 ⇒ **交集 43 / 仅官方 0 / 仅复现 0** ⇒ ★**逐条坐实**
  ② ★**端点归属集合** (★器件+焊盘+层) ⇒ ★**会有少量出入** ⇒ 原因见下
  ③ ★**精确端点坐标** (★最严, ★★**但不可用作判据**)

★★★**★为什么 ②③ 会差几条 (★实测, ★不是 bug)** ★★★
  ★**同一条未连接, 两端的"具体落点"会不一样**:
  ★**官方板**: ★`(Pad 16 [LIGHT_3V3] of CONN_LIGHT) ↔ (Pad 1 [LIGHT_3V3] of C_BULK_LIGHT_3V3)` (★焊盘↔焊盘)
  ★**我复现的**: ★`(Pad 16 [LIGHT_3V3] of CONN_LIGHT) ↔ (Track [LIGHT_3V3] on F.Cu)` (★焊盘↔铜)
  ⇒ ★**同一张网, 一个端点接在焊盘上、另一个接在哪段铜上** ⇒ ★**A* 补段时选的起点不同 ⇒ 表述就不同**
  ⇒ ★★★**⇒ 判"同工艺"必须看【网名集合】(①) + 【几何集合】(在 replay_patch_chain.sh 的自校准闸里) ⇒ ★★**别拿坐标集合当判据** ★★★

用法:
  python3 state/cmp_unc_sets.py <板A.drc.json> <板B.drc.json>
  python3 state/cmp_unc_sets.py <板A.drc.json> <板B.drc.json> --strict
    ★--strict: 网名集合不完全相同 ⇒ rc=1 (★用作闸门)
"""
import json
import re
import sys


def load(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return d.get("unconnected_items") or []


def nets_of(it):
    """这条未连接涉及的所有网名 (★排序, ★去重)"""
    s = json.dumps(it, ensure_ascii=False)
    return tuple(sorted(set(re.findall(r"\[([A-Za-z0-9_]+)\]", s))))


def sides_of(it):
    """两端归属: (类型, 网名, 器件/层)"""
    out = []
    for x in (it.get("items") or []):
        d = x.get("description", "")
        m = re.match(r"Pad \d+ \[([^\]]+)\] of (\S+) on", d)
        if m:
            out.append(("PAD", m.group(1), m.group(2)))
            continue
        m = re.match(r"Track \[([^\]]+)\] on (\S+)", d)
        if m:
            out.append(("TRK", m.group(1), m.group(2)))
            continue
        out.append(("OTHER", "", ""))
    return tuple(sorted(out))


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    strict = "--strict" in sys.argv
    a = load(sys.argv[1])
    b = load(sys.argv[2])

    na = {nets_of(i) for i in a if nets_of(i)}
    nb = {nets_of(i) for i in b if nets_of(i)}
    sa = {sides_of(i) for i in a}
    sb = {sides_of(i) for i in b}

    print(f"板A: {len(a)} 条 unc · {len(na)} 个网名签名 · {len(sa)} 个端点归属")
    print(f"板B: {len(b)} 条 unc · {len(nb)} 个网名签名 · {len(sb)} 个端点归属")
    print()
    print("── ① 网名集合 (★强判据) ──")
    print(f"  交集 {len(na & nb)} · 仅A {len(na - nb)} · 仅B {len(nb - na)}")
    same_nets = na == nb
    print(f"  ★完全相同 = {same_nets}")
    print()
    print("── ② 端点归属集合 (★辅助: 会有少量出入, ★因为同一条未连接的铜侧落点可不同) ──")
    print(f"  交集 {len(sa & sb)} · 仅A {len(sa - sb)} · 仅B {len(sb - sa)}")
    print(f"  ★完全相同 = {sa == sb}")
    for x in sorted(sa - sb)[:3]:
        print(f"    仅A: {x}")
    for x in sorted(sb - sa)[:3]:
        print(f"    仅B: {x}")

    if strict and not same_nets:
        print()
        print("❌ --strict: 网名集合不完全相同 ⇒ rc=1")
        return 1
    print()
    print("★判据: ① 网名集合完全相同 ⇒ 两板【同一批未连接】⇒ 同工艺 (★②③ 有出入是正常的, ★别当失败)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
