#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_lane_order2.py —— ★逐 lane 判定 P/N 在**每一段**的左右序 (全焊盘, pcbnew 直读)

★★**要回答的唯一问题**: 对每个 lane, 在四个位置 (SoM端 / 中途器件SRC脚 / 中途器件后脚 / 远端)
   P 和 N 的 x 序分别是多少? ⇒ 凡是序**反转**的那一段, P/N 铜**几何上必须交换** ⇒ 必有一侧布不出来

★★**为什么必须先测这个 (教训)**:
  cron 说 "CSI 5 对缺铜 ⇒ 下 crossover 刀" ⇒ ★**缺铜 ≠ 需要交叉**
  ⇒ 审计实测 **P 侧基本通了 / N 侧基本没通** ⇒ 也可能纯拥塞
  ⇒ ★**而且**: P/N 之间夹着**两个分立的 2 脚器件** (C_AC_CSI_xx_P / _N, R_SEL_xx_P / _N)
  ⇒ ⇒ "lane" 被拆成**两条独立网** ⇒ ★**换器件摆放就能吃掉一部分交叉**
  ⇒ ⇒ ★**先测清楚再写 crossover 代码, 否则白造一个臂**
"""
import sys, re, collections
import pcbnew

PCB = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/yuewuya/.openclaw/workspace/projects/smart_glasses/HW/PCB/demo_mainboard.kicad_pcb"

b = pcbnew.LoadBoard(PCB)
nets = collections.defaultdict(list)
for f in b.GetFootprints():
    ref = f.GetReference()
    for p in f.Pads():
        pos = p.GetPosition()
        nets[p.GetNetname()].append((ref, p.GetNumber(), pos.x / 1e6, pos.y / 1e6))

SERIES = ("C_AC_CSI", "R_SEL")

def lane_of(net):
    m = re.match(r'^(CSI|DSI)_D0_(D\d|CK)_(P|N)(_SRC)?$', net)
    return (m.group(1), m.group(2), m.group(3), bool(m.group(4))) if m else None

def where(ref):
    if ref.startswith("J_SOM"): return "som"
    if ref.startswith(SERIES): return "series"
    if ref.startswith("CONN_") or ref.startswith("TP_"): return "far"
    return "other"

print("═══ 板: %s ═══" % PCB)
summary = {}
for kind in ("CSI", "DSI"):
    lanes = collections.defaultdict(lambda: {"P": [], "N": []})
    for net, pads in nets.items():
        r = lane_of(net)
        if not r or r[0] != kind:
            continue
        _, lane, pol, src = r
        for pd in pads:
            lanes[lane][pol].append((pd[0], pd[1], pd[2], pd[3], net, src))

    print("\n" + "=" * 90)
    print("═══ %s: 每 lane 的 P/N 序 (x) ═══" % kind)
    print("=" * 90)
    for lane in sorted(lanes):
        d = lanes[lane]
        # 按 (位置, SRC/后段) 分桶
        buckets = collections.defaultdict(dict)   # bucket -> pol -> x
        for pol in ("P", "N"):
            for (ref, num, x, y, net, src) in d[pol]:
                w = where(ref)
                if w == "series":
                    key = "series_src" if src else "series_post"
                elif w == "som":
                    key = "som"
                elif w == "far":
                    key = "far"
                else:
                    key = "other"
                buckets[key].setdefault(pol, []).append(x)

        print("\n──── %s_%s ────" % (kind, lane))
        orders = {}
        for key in ("som", "series_src", "series_post", "far"):
            if key not in buckets:
                continue
            P = sorted(buckets[key].get("P", []))
            N = sorted(buckets[key].get("N", []))
            if not P or not N:
                print("   %-12s : ★缺一侧 (P=%s N=%s)" % (key, P, N))
                continue
            # 用**最外侧**焊盘判序 (SoM端取最小x; 其余取平均)
            px = min(P) if key == "som" else (min(P) + max(P)) / 2.0
            nx = min(N) if key == "som" else (min(N) + max(N)) / 2.0
            order = "P在左" if px < nx else ("N在左" if nx < px else "同x")
            orders[key] = ("P" if px < nx else "N")
            print("   %-12s : P x=%-28s N x=%-28s ⇒ ★%s" % (
                key, "%.2f" % px, "%.2f" % nx, order))
        # 判定反转
        seq = [orders[k] for k in ("som", "series_src", "series_post", "far") if k in orders]
        trans = []
        for a, bb in zip(seq, seq[1:]):
            if a != bb:
                trans.append("反转")
        verdict = "★需交叉 (%d 处反转)" % len(trans) if trans else "⇒ 全程序一致, **不需交叉**"
        print("   ★★ 结论: %s" % verdict)
        summary["%s_%s" % (kind, lane)] = (len(trans), trans)

print("\n" + "=" * 90)
print("═══ 汇总 ═══")
for k in sorted(summary):
    n, tr = summary[k]
    print("  %-10s 反转次数=%d %s" % (k, n, ("(需交叉)" if n else "(不需交叉)")))
print("\n★ 需要 crossover 的 lane 数: %d / %d" % (sum(1 for v in summary.values() if v[0]), len(summary)))
