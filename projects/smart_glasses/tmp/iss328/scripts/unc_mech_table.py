#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-325 · unc_mech_table.py -- ★★「离 0 还差几条 + 每条卡在什么上」机制级读数★★
★口径 (★照 ISS-322 §2-6 的「板上零铜 vs 长了一半」机制★):
    · 板上零铜 (★一根铜都没长出来★) ⇒ 路由器【没布出来】⇒ 换层/让路这些增量手段对它无效
    · 有铜但仍未连通 (★长了一半★)   ⇒ 路由器【布歪了】⇒ 增量手段对它有效
用法: bash state/pcbnew_py.sh logs/iss325/scripts/unc_mech_table.py <板> <板.drc.json> [<板2> <板2.drc.json> ...]
"""
import collections
import json
import re
import sys

import pcbnew

MM = 1e6


def unc_nets_from_drc(drcpath):
    d = json.load(open(drcpath, encoding="utf-8"))
    nets = collections.Counter()
    for it in (d.get("unconnected_items") or []):
        s = json.dumps(it, ensure_ascii=False)
        for n in set(re.findall(r"\[([A-Za-z0-9_]+)\]", s)):
            nets[n] += 1
    return nets


def copper_by_net(b):
    seg_len = collections.defaultdict(float)
    seg_cnt = collections.Counter()
    via_cnt = collections.Counter()
    for t in b.GetTracks():
        n = t.GetNetname()
        if t.Type() == pcbnew.PCB_VIA_T:
            via_cnt[n] += 1
            continue
        s, e = t.GetStart(), t.GetEnd()
        seg_len[n] += ((s.x - e.x) ** 2 + (s.y - e.y) ** 2) ** 0.5 / MM
        seg_cnt[n] += 1
    return seg_len, seg_cnt, via_cnt


def main():
    args = sys.argv[1:]
    pairs = [(args[i], args[i + 1]) for i in range(0, len(args) - 1, 2)]
    data = {}
    for bd, dj in pairs:
        b = pcbnew.LoadBoard(bd)
        nets = unc_nets_from_drc(dj)
        sl, sc, vc = copper_by_net(b)
        data[bd] = (nets, sl, sc, vc)
        print("★板 %s (%s): 未连接网名 %d 个 · 未连接条目 %d 条"
              % (bd, dj.split("/")[-1], len(nets), sum(nets.values())))

    print()
    print("═══ 逐网机制表 (★零铜 = 路由器没布出来 / 有铜 = 布歪了★) ═══")
    w = 36
    hdr = "%-24s" % "net"
    for bd, _ in pairs:
        hdr += " | %-*s" % (w, bd.split("/")[-1][:w])
    print(hdr)
    print("-" * len(hdr))
    allnets = set()
    for bd, _ in pairs:
        allnets |= set(data[bd][0].keys())

    def key(n):
        return (0 if n.startswith(("DSI_", "CSI_")) else 1, n)

    for n in sorted(allnets, key=key):
        row = "%-24s" % n
        for bd, _ in pairs:
            nets, sl, sc, vc = data[bd]
            if n in nets:
                L = sl.get(n, 0.0)
                if L < 1e-9 and vc.get(n, 0) == 0:
                    cell = "★零铜★"
                else:
                    cell = "铜%.1fmm/%d段/%d孔" % (L, sc.get(n, 0), vc.get(n, 0))
                row += " | %-*s" % (w, "未连:" + cell)
            else:
                row += " | %-*s" % (w, "通")
        print(row)


if __name__ == "__main__":
    main()
