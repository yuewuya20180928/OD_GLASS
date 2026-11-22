#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★ISS-337 cont1 · 归一化实现差异定位 (★只读·纯解析·不改任何真件★)

★目的: main 2026-11-19 01:2x 独立复算得 官方板 2288 / v76mg1 2421,
      本单脚本得 2649 / 2582 ⇒ 同一概念两个数。
★本脚本: 把【合并规则】拆成几个可独立开关的旋钮, 逐个测 ⇒ 定位差异来源。
★结论用于交卷页「归一化段数的唯一定义」一节。

旋钮:
  group_width : True=按 (层,网,宽) 分组 / False=按 (层,网) 分组
  need_deg2   : True=共享端点在该组内度数必须恰为 2 / False=不检查度数
  allow_over  : True=允许【共线重叠】(不只是首尾相接) 的段合并
"""
import re
import sys
import math
import collections


def segs_of(path):
    out = []
    cur = {}
    x1 = y1 = x2 = y2 = w = layer = net = None
    with open(path, encoding="utf-8", errors="ignore") as f:
        for ln in f:
            s = ln.strip()
            if s == "(segment":
                cur = {"k": "seg"}
                x1 = y1 = x2 = y2 = w = layer = net = None
            elif s.startswith("(start "):
                m = re.match(r"\(start\s+([-\d.]+)\s+([-\d.]+)\)", s)
                if m:
                    x1, y1 = float(m.group(1)), float(m.group(2))
            elif s.startswith("(end "):
                m = re.match(r"\(end\s+([-\d.]+)\s+([-\d.]+)\)", s)
                if m:
                    x2, y2 = float(m.group(1)), float(m.group(2))
            elif s.startswith("(width "):
                m = re.match(r"\(width\s+([-\d.]+)\)", s)
                if m:
                    w = float(m.group(1))
            elif s.startswith("(layer "):
                layer = s.split('"')[1] if '"' in s else None
            elif s.startswith("(net "):
                m = re.search(r'\(net\s+(?:\d+\s+)?"([^"]*)"', s)
                net = m.group(1) if m else None
            elif s == ")":
                if cur.get("k") == "seg" and None not in (x1, y1, x2, y2):
                    out.append((x1, y1, x2, y2, w or 0.25, layer, net))
                cur = {}
    return out


def merge(segs, group_width=True, need_deg2=True, allow_over=False, tol=1e-6):
    by = collections.defaultdict(list)
    for i, (x1, y1, x2, y2, w, l, n) in enumerate(segs):
        key = (l, n, round(w, 4)) if group_width else (l, n)
        by[key].append(i)
    alive = [True] * len(segs)
    segs = list(segs)
    changed = True
    rounds = 0
    while changed:
        changed = False
        rounds += 1
        for key, idxs in by.items():
            ep = collections.defaultdict(list)
            for i in idxs:
                if not alive[i]:
                    continue
                x1, y1, x2, y2, w, l, n = segs[i]
                ep[(round(x1, 4), round(y1, 4))].append((i, (x2, y2)))
                ep[(round(x2, 4), round(y2, 4))].append((i, (x1, y1)))
            for pt, lst in ep.items():
                if len(lst) < 2:
                    continue
                if need_deg2 and len(lst) != 2:
                    continue
                # 两两尝试 (need_deg2=False 时 lst 可能 >2)
                done = False
                for a in range(len(lst)):
                    for b in range(a + 1, len(lst)):
                        i, _ = lst[a]
                        j, _ = lst[b]
                        if i == j or not alive[i] or not alive[j]:
                            continue
                        x1, y1, x2, y2, w, l, n = segs[i]
                        x3, y3, x4, y4, _w2, _l2, _n2 = segs[j]
                        d1 = (x2 - x1, y2 - y1)
                        d2 = (x4 - x3, y4 - y3)
                        nd1 = math.hypot(*d1)
                        nd2 = math.hypot(*d2)
                        if nd1 < tol or nd2 < tol:
                            continue
                        cross = abs(d1[0] * d2[1] - d1[1] * d2[0]) / (nd1 * nd2)
                        if cross > 1e-6:
                            continue
                        dot = (d1[0] * d2[0] + d1[1] * d2[1]) / (nd1 * nd2)
                        if abs(dot) < 1.0 - 1e-9:
                            continue
                        pts = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
                        ends = []
                        for p in pts:
                            if p not in ends:
                                ends.append(p)
                        if len(ends) == 3:
                            common = [p for p in ends
                                      if p in ((x1, y1), (x2, y2)) and p in ((x3, y3), (x4, y4))]
                            if len(common) != 1:
                                continue
                            c = common[0]
                            o1 = (x2, y2) if (x1, y1) == c else (x1, y1)
                            o2 = (x4, y4) if (x3, y3) == c else (x3, y3)
                            ends = [o1, o2]
                        if len(ends) != 2:
                            continue
                        segs[i] = (ends[0][0], ends[0][1], ends[1][0], ends[1][1], w, l, n)
                        alive[j] = False
                        changed = True
                        done = True
                        break
                    if done:
                        break
                if changed:
                    break
            if changed:
                break
    return [segs[i] for i in range(len(segs)) if alive[i]]


VARIANTS = [
    ("V1 本单基线 (层,网,宽 + 度数=2)", dict(group_width=True, need_deg2=True)),
    ("V2 不按线宽分组 (层,网 + 度数=2)", dict(group_width=False, need_deg2=True)),
    ("V3 不查度数 (层,网,宽 · 任意度数)", dict(group_width=True, need_deg2=False)),
    ("V4 不查度数 + 不按线宽分组 (层,网 · 任意度数)", dict(group_width=False, need_deg2=False)),
]


def main():
    boards = [
        ("官方板 611b869e", "/home/yuewuya/.openclaw/workspace/projects/smart_glasses/HW/PCB/demo_mainboard.kicad_pcb"),
        ("现役链终板 v76mg1", "/tmp/chain_v76mg1/final_chain.kicad_pcb"),
    ]
    for label, path in boards:
        segs = segs_of(path)
        print("=" * 92)
        print("★%s  raw=%d" % (label, len(segs)))
        print("=" * 92)
        for vname, kw in VARIANTS:
            out = merge(list(segs), **kw)
            print("  %-46s ⇒ norm=%d" % (vname, len(out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
