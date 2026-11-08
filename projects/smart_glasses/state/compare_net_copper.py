#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""compare_net_copper.py -- ★★★**两块板"逐网铜长"对照 (★2026-11-09 01:0x 新增)** ★★★

★★**为什么要有这个 (★v74 实测踩出来的坑)****
  ★**"差分对逐对对照"只覆盖 22 对差分对** ⇒ ★**普通信号网掉了, 它看不见**
  ★**v74 实测**: ★**`RESET_N` 整条丢了 (官方 ok=True L=144.5mm ⇒ v74 ok=False 失败脚=5)**
    ⇒ ★**这是关键电源/复位线, 不是边角** ⇒ ★**只看差分对会漏掉这类回归**
  ⇒ ★**⇒ 必须有"逐网"这一层**: ★**谁多了铜、谁少了铜、谁从"有"变成"没有"**

★★**用法**: `python3 state/compare_net_copper.py <板A> <板B>` (★A=候选 · B=基线)
★★**★阶段必须对齐 (★踩过的坑)****: ★**拿"中间阶段的板"去比"最终板"会刷出一堆假"丢铜"**
  ★**实测**: ★**v74 的【MIPI 阶段中间板】(段数 9735) vs 官方【最终板】(段数 17092) ⇒ 报"丢铜 38 个网"**
    ⇒ ★**那 38 个里有大半是【其余网还没布】造成的 ⇒ 不是回归** ⇒ ★**⇒ 必须同阶段比 (★要么都用最终板, 要么都用同一次阶段性落盘)**
★**输出**: ★**按"变化量绝对值"降序排的逐网表** ⇒ ★**最上面几行就是这次臂改动最大的网**
★**判据**: ★**"丢网" = 基线有铜(>0) 而候选零铜 ⇒ 标记 ★丢铜 (最严重)**
"""
import math
import re
import sys


def net_lengths(pcb):
    out = {}
    inseg = False
    net = None
    x1 = y1 = x2 = y2 = None
    with open(pcb, encoding="utf-8", errors="ignore") as f:
        for ln in f:
            s = ln.strip()
            if s == "(segment":
                inseg = True
                net = None
                x1 = y1 = x2 = y2 = None
                continue
            if inseg:
                m = re.match(r"\(start ([-\d.]+) ([-\d.]+)\)", s)
                if m:
                    x1, y1 = float(m.group(1)), float(m.group(2))
                m = re.match(r"\(end ([-\d.]+) ([-\d.]+)\)", s)
                if m:
                    x2, y2 = float(m.group(1)), float(m.group(2))
                m = re.match(r'\(net "([^"]+)"\)', s)
                if m:
                    net = m.group(1)
                if s == ")":
                    inseg = False
                    if net is not None and x1 is not None and x2 is not None:
                        out[net] = out.get(net, 0.0) + math.hypot(x2 - x1, y2 - y1)
    return out


def main():
    a = net_lengths(sys.argv[1])
    b = net_lengths(sys.argv[2])
    keys = sorted(set(a) | set(b), key=lambda k: -abs(a.get(k, 0.0) - b.get(k, 0.0)))
    print("════ A(候选): %s" % sys.argv[1])
    print("════ B(基线): %s" % sys.argv[2])
    print()
    print("%-26s %12s %12s %12s  %s" % ("网名", "A(候选)", "B(基线)", "Δ", "判定"))
    lost = gained = 0
    for k in keys:
        av = a.get(k, 0.0)
        bv = b.get(k, 0.0)
        d = av - bv
        if bv > 0.0 and av <= 0.0:
            v = "★★丢铜 (基线有 ⇒ 候选零铜)"
            lost += 1
        elif av > 0.0 and bv <= 0.0:
            v = "★新增铜"
            gained += 1
        elif abs(d) < 0.05:
            v = "持平"
        else:
            v = "长度变化"
        print("%-26s %12.3f %12.3f %+12.3f  %s" % (k, av, bv, d, v))
    print()
    print("★合计: 丢铜 %d 个网 · 新增铜 %d 个网 · 涉及 %d 个网"
          % (lost, gained, len([k for k in keys
                                if abs(a.get(k, 0.0) - b.get(k, 0.0)) > 0.05])))


if __name__ == "__main__":
    main()
