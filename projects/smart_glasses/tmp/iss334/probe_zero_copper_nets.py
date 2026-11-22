#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_zero_copper_nets.py (★ISS-334 沙盒·只读★)

★**目的**: 从【板文件】+【DRC JSON】fresh 解析出「零铜网 0 号清单」
  · 零铜定义 ★**逐字对齐 state/compare_arm_official.py 的闸定义**:
      pad_cnt[net] >= 2 且 net_seg[net] == 0 (★只数 segment, 不数 via★)
  · 端点: ref + pad号 + 坐标 + 层
  · 分类: 沿用 state/probe_unconnected_worklist.py 的三类口径
      (整网无铜 / 局部未通 / 端点缝) ⇒ **不另编分类**

★**只读**: 本脚本只 open(板, 'r') 与 open(drc, 'r') ⇒ **绝不写板**
用法:
  bash state/pcbnew_py.sh tmp/iss334/probe_zero_copper_nets.py <板> <drc.json> [--out md]
"""
import sys
import math
import json
import re
import collections
import pcbnew

MM = 1e6


def pt_seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 <= 1e-12:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def load(path):
    b = pcbnew.LoadBoard(path)
    pads, segs, vias = [], [], []
    for f in b.GetFootprints():
        for p in f.Pads():
            q = p.GetPosition()
            sz = p.GetSize()
            try:
                lay = p.GetLayerName()
            except Exception:
                lay = "?"
            pads.append(dict(ref=f.GetReference(), num=str(p.GetNumber()),
                             net=p.GetNetname(), x=q.x / MM, y=q.y / MM,
                             w=sz.x / MM, h=sz.y / MM, layer=lay))
    for t in b.GetTracks():
        s, e = t.GetStart(), t.GetEnd()
        if t.Type() == pcbnew.PCB_VIA_T:
            vias.append(dict(net=t.GetNetname(), x=s.x / MM, y=s.y / MM,
                             w=t.GetWidth(pcbnew.F_Cu) / MM))
        else:
            segs.append(dict(net=t.GetNetname(), layer=t.GetLayerName(),
                             x1=s.x / MM, y1=s.y / MM, x2=e.x / MM, y2=e.y / MM,
                             w=t.GetWidth() / MM))
    return pads, segs, vias


def nets_from_drc(path):
    d = json.load(open(path, encoding="utf-8"))
    items = d.get("unconnected_items", [])
    out = collections.OrderedDict()
    for it in items:
        s = json.dumps(it, ensure_ascii=False)
        for m in re.finditer(r"Pad\s+\S+\s+\[([^\]]+)\]", s):
            out.setdefault(m.group(1), []).append(s)
    return out, items


def main():
    a = sys.argv[1:]
    board, drc = a[0], a[1]
    outf = None
    if "--out" in a:
        i = a.index("--out")
        if len(a) > i + 1:
            outf = a[i + 1]
    pads, segs, vias = load(board)
    dn, items = nets_from_drc(drc)

    by_net_seg = collections.Counter()
    by_net_via = collections.Counter()
    net_len = collections.defaultdict(float)
    for s in segs:
        by_net_seg[s["net"]] += 1
        net_len[s["net"]] += math.hypot(s["x2"] - s["x1"], s["y2"] - s["y1"])
    for v in vias:
        by_net_via[v["net"]] += 1
    pads_by_net = collections.defaultdict(list)
    for p in pads:
        pads_by_net[p["net"]].append(p)

    lines = []
    print("═══ 板: %s ═══" % board)
    print("═══ DRC 未连接条目: %d 条 ⇒ 涉及 %d 个网 ═══" % (len(items), len(dn)))
    print("═══ 板全体: 走线 %d 段 · 过孔 %d 个 · 焊盘 %d 个 · 网名 %d 个 ═══"
          % (len(segs), len(vias), len(pads), len(pads_by_net)))
    lines.append("板全体: 走线 %d 段 · 过孔 %d 个 · 焊盘 %d 个 · 网名 %d 个"
                 % (len(segs), len(vias), len(pads), len(pads_by_net)))

    # ★零铜定义: pad>=2 且 segment==0 (对齐 compare_arm_official.py)★ ★全体网, 不只 DRC 里的网★
    zero_all = []
    for n, ps in sorted(pads_by_net.items()):
        if len(ps) >= 2 and by_net_seg.get(n, 0) == 0:
            zero_all.append(n)
    zero_in_drc = [n for n in zero_all if n in dn]
    zero_not_drc = [n for n in zero_all if n not in dn]

    print("")
    print("═══ ★零铜网 (pad≥2 且 segment=0) 全体 = %d 个 ═══" % len(zero_all))
    print("═══   其中落在 DRC 未连接网里 = %d 个 ═══" % len(zero_in_drc))
    lines.append("零铜网(pad≥2 且 segment=0) 全体 = %d 个; 落在 DRC 未连接网里 = %d 个"
                 % (len(zero_all), len(zero_in_drc)))

    hdr = "%-26s %-5s %-6s %-4s %-4s %-9s %-22s" % (
        "网名", "焊盘", "段", "孔", "长mm", "类别", "端点(ref.pad@x,y 层)")
    print(hdr)
    lines.append(hdr)
    zero_detail = []
    for n in zero_all:
        ps = pads_by_net[n]
        ns = by_net_seg.get(n, 0)
        nv = by_net_via.get(n, 0)
        L = net_len.get(n, 0.0)
        if ns == 0 and nv == 0:
            kind = "整网无铜"
        else:
            kind = "★零segment但有via"
        eps = "; ".join("%s.%s@(%.2f,%.2f %s)" % (p["ref"], p["num"], p["x"], p["y"], p["layer"])
                        for p in ps[:8])
        if len(ps) > 8:
            eps += " ...(+%d)" % (len(ps) - 8)
        row = "%-26s %-5d %-6d %-4d %-9.3f %-22s %s" % (n, len(ps), ns, nv, L, kind, eps)
        print(row)
        lines.append(row)
        zero_detail.append(dict(net=n, pads=len(ps), seg=ns, via=nv, length=L,
                                kind=kind, in_drc=(n in dn),
                                endpoints=[dict(ref=p["ref"], pad=p["num"], x=p["x"],
                                                y=p["y"], layer=p["layer"]) for p in ps]))

    print("")
    print("── 零铜网里【不在 DRC 未连接网】的 = %d 个 (★DRC 口径与几何口径不一致的样本★)" % len(zero_not_drc))
    for n in zero_not_drc:
        print("    · %s (pad=%d seg=%d via=%d)" % (n, len(pads_by_net[n]),
              by_net_seg.get(n, 0), by_net_via.get(n, 0)))
        lines.append("    · %s (pad=%d seg=%d via=%d)" % (n, len(pads_by_net[n]),
                     by_net_seg.get(n, 0), by_net_via.get(n, 0)))

    # ★零铜网的类别 (沿用 worklist 三类口径)★
    print("")
    print("── ★零铜网按 DRC 类别分布:")
    cls = collections.Counter()
    for z in zero_detail:
        n = z["net"]
        ps = pads_by_net[n]
        ns = [s for s in segs if s["net"] == n]
        nv = [v for v in vias if v["net"] == n]
        connected = 0
        for p in ps:
            d_same = 1e9
            for s in ns:
                d_same = min(d_same, max(0.0, pt_seg_dist(p["x"], p["y"], s["x1"], s["y1"],
                                                           s["x2"], s["y2"]) - s["w"] / 2.0))
            for v in nv:
                d_same = min(d_same, max(0.0, math.hypot(p["x"] - v["x"], p["y"] - v["y"]) - v["w"] / 2.0))
            if d_same <= 0.30:
                connected += 1
        if len(ns) == 0 and len(nv) == 0:
            kind = "整网无铜"
        elif connected == len(ps):
            kind = "端点缝(★口径差异★)"
        else:
            kind = "局部未通"
        z["class"] = kind
        cls[kind] += 1
    for k, v in cls.most_common():
        print("    · %-20s %d 个" % (k, v))
        lines.append("    · %-20s %d 个" % (k, v))

    # ★单边零铜的差分对 (pair_copper_table 口径)★
    PAIRS = [
        ("NET_USB_D_P_TYPEC", "NET_USB_D_N_TYPEC"), ("USB_D_P_SRC", "USB_D_N_SRC"),
        ("CSI_D0_CK_P_SRC", "CSI_D0_CK_N_SRC"), ("CSI_D0_CK_P", "CSI_D0_CK_N"),
        ("CSI_D0_D0_P_SRC", "CSI_D0_D0_N_SRC"), ("CSI_D0_D0_P", "CSI_D0_D0_N"),
        ("CSI_D0_D1_P_SRC", "CSI_D0_D1_N_SRC"), ("CSI_D0_D1_P", "CSI_D0_D1_N"),
        ("CSI_D0_D2_P_SRC", "CSI_D0_D2_N_SRC"), ("CSI_D0_D2_P", "CSI_D0_D2_N"),
        ("CSI_D0_D3_P_SRC", "CSI_D0_D3_N_SRC"), ("CSI_D0_D3_P", "CSI_D0_D3_N"),
        ("DSI_D0_CK_P_SRC", "DSI_D0_CK_N_SRC"), ("DSI_D0_CK_P", "DSI_D0_CK_N"),
        ("DSI_D0_D0_P_SRC", "DSI_D0_D0_N_SRC"), ("DSI_D0_D0_P", "DSI_D0_D0_N"),
        ("DSI_D0_D1_P_SRC", "DSI_D0_D1_N_SRC"), ("DSI_D0_D1_P", "DSI_D0_D1_N"),
        ("DSI_D0_D2_P_SRC", "DSI_D0_D2_N_SRC"), ("DSI_D0_D2_P", "DSI_D0_D2_N"),
        ("DSI_D0_D3_P_SRC", "DSI_D0_D3_N_SRC"), ("DSI_D0_D3_P", "DSI_D0_D3_N"),
    ]
    print("")
    print("── ★差分对铜长 (P / N) + 单边零铜标记:")
    pair_rows = []
    for (p_, n_) in PAIRS:
        lp, ln = net_len.get(p_, 0.0), net_len.get(n_, 0.0)
        if lp == 0.0 and ln == 0.0:
            tag = "★双边零铜"
        elif lp == 0.0:
            tag = "★P边零铜"
        elif ln == 0.0:
            tag = "★N边零铜"
        else:
            tag = "双边有铜"
        r = "%-22s|%s\tP=%.3f\tN=%.3f\t%s" % (p_, n_, lp, ln, tag)
        print("    " + r)
        lines.append("    " + r)
        pair_rows.append(dict(p=p_, n=n_, lp=lp, ln=ln, tag=tag))

    # ★差分对成员是否落在零铜网清单里★
    print("")
    print("── ★差分对腿 ⇄ 零铜网清单 对照:")
    zset = set(zero_all)
    for r in pair_rows:
        print("    · %-22s P零铜=%-5s N零铜=%-5s | %s" % (
            r["p"], r["p"] in zset, r["n"] in zset, r["tag"]))
        lines.append("    · %-22s P零铜=%-5s N零铜=%-5s | %s" % (
            r["p"], r["p"] in zset, r["n"] in zset, r["tag"]))

    if outf:
        js = dict(zero_nets=zero_detail, zero_all=zero_all, zero_in_drc=zero_in_drc,
                  zero_not_drc=zero_not_drc, classes=dict(cls), pairs=pair_rows,
                  board=dict(segs=len(segs), vias=len(vias), pads=len(pads),
                             nets=len(pads_by_net)),
                  drc_items=len(items), drc_nets=len(dn))
        with open(outf.replace(".md", ".json"), "w", encoding="utf-8") as f:
            json.dump(js, f, ensure_ascii=False, indent=1)
        with open(outf, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print("── 存证: %s (+ .json)" % outf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
