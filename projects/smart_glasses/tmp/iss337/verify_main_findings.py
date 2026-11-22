#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""★ISS-337 cont1 · main 两条独立复算发现的【本机复核】★

只读: 只解析 .kicad_pcb 文本, 不写任何板/闸/表。
★零铜网口径 = 与 state/compare_arm_official.py:113-115 逐字一致:
    pad_cnt[n] >= 2 且 net_seg[n] == 0
★逐网铜长「相符」口径 = main 2026-11-19 01:2x 的口径:
    |a-b| <= max(0.02 * max(a,b), 1.0mm)
"""
import re
import sys
import math
import collections


def parse(path):
    segs = []
    pad_cnt = collections.Counter()
    cur = {}
    x1 = y1 = x2 = y2 = w = layer = net = None
    in_pad = False
    with open(path, encoding="utf-8", errors="ignore") as f:
        for ln in f:
            s = ln.strip()
            if s == "(segment":
                cur = {"k": "seg"}
                x1 = y1 = x2 = y2 = w = layer = net = None
            elif s.startswith("(pad ") or s == "(pad":
                in_pad = True
                cur = {"k": "pad"}
                net = None
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
                if in_pad and net is not None:
                    pad_cnt[net] += 1
            elif s == ")":
                if cur.get("k") == "seg" and None not in (x1, y1, x2, y2):
                    segs.append((x1, y1, x2, y2, w or 0.25, layer, net))
                if cur.get("k") == "pad":
                    in_pad = False
                cur = {}
    net_seg = collections.Counter(s[6] for s in segs if s[6])
    net_cu = collections.defaultdict(float)
    for s in segs:
        if s[6]:
            net_cu[s[6]] += math.hypot(s[2] - s[0], s[3] - s[1])
    zero = sorted(n for n, np_ in pad_cnt.items() if np_ >= 2 and net_seg[n] == 0)
    return {
        "path": path,
        "segs": len(segs),
        "nets_on_pads": len(pad_cnt),
        "nets_with_cu": len(net_cu),
        "zero": zero,
        "net_cu": dict(net_cu),
        "net_seg": dict(net_seg),
    }


def main():
    proj = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
    boards = {
        "官方板 611b869e": proj + "/HW/PCB/demo_mainboard.kicad_pcb",
        "现役链终板 v76mg1": "/tmp/chain_v76mg1/final_chain.kicad_pcb",
        "现役链终板 v76mz": "/tmp/chain_v76mz/final_chain.kicad_pcb",
        "现役 best_unc23_clrfix": proj + "/state/.lastgood/best_unc23_clrfix.kicad_pcb",
    }
    M = {}
    print("=" * 92)
    print("★ISS-337 cont1 · main 两条独立复算发现的本机复核 (★只读·证据 [实测]★)")
    print("=" * 92)
    print("\n── 发现 ①: 零铜网 (pad>=2 且板上零 segment) 三板对照 ──")
    print("%-28s %10s %10s %12s" % ("板", "焊盘网名", "有铜网", "零铜网(pad>=2)"))
    for k, p in boards.items():
        M[k] = parse(p)
        m = M[k]
        print("%-28s %10d %10d %12d"
              % (k, m["nets_on_pads"], m["nets_with_cu"], len(m["zero"])))

    off = M["官方板 611b869e"]
    cur = M["现役链终板 v76mg1"]
    zoff, zcur = set(off["zero"]), set(cur["zero"])
    both_zero = sorted(zoff & zcur)
    print("\n  ★官方板零铜网 = %d 条; 其中在现役链终板 v76mg1 上【已有铜】= %d 条"
          % (len(zoff), len(zoff - zcur)))
    print("  ★两边都零铜 = %d 条: %s" % (len(both_zero), ", ".join(both_zero)))
    zv76mz = set(M["现役链终板 v76mz"]["zero"])
    print("  ★现役链终板 v76mz 零铜网 = %d 条" % len(zv76mz))

    print("\n── 发现 ②: 逐网铜长 (官方板 vs state/.lastgood/best_unc23_clrfix) ──")
    b = M["现役 best_unc23_clrfix"]
    both = sorted(set(off["net_cu"]) & set(b["net_cu"]))
    match, mismatch = [], []
    for n in both:
        a, c = off["net_cu"][n], b["net_cu"][n]
        tol = max(0.02 * max(a, c), 1.0)
        (match if abs(a - c) <= tol else mismatch).append((n, a, c))
    print("  两板都有铜的网 = %d 条" % len(both))
    print("  ★铜长相符 (±2%% 或 1mm 内) = %d 条" % len(match))
    print("  ★对不上 = %d 条" % len(mismatch))
    print("  ★差异最大 8 条 (官方 - best_unc23):")
    for n, a, c in sorted(mismatch, key=lambda t: t[1] - t[2])[:8]:
        print("    %-24s 官方=%8.1fmm  best_unc23=%8.1fmm  Δ=%+8.1fmm" % (n, a, c, a - c))
    return 0


if __name__ == "__main__":
    sys.exit(main())
