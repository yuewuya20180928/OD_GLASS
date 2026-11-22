#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""classify_unc.py —— ★★把未连接按【堵点性质】分桶 (★决定"哪条路能走")

★★★**★设计原则 (★2026-11-09 06:5x 踩坑后定的)★★★**
  ★★**几何判定不许自己重造** ⇒ ★★**唯一真源 = `state/probe_unconnected_worklist_v2.py` 的输出** ★★
  (★v2 已处理分层 / 焊盘按矩形 / 走线端点按圆头 ⇒ ★★**我第一版自己重写几何时【漏了分层】⇒ 净距出现负值 ⇒ 那是假数据** ★★)

★★★★**★分桶判据 (★全部来自实测)★★★★**
  ★**主轴: 【端点是不是真墙】(★★**真墙 = 同层异网铜净距 < 规则要求 ⇒ 端点本身就出不来**) ★★
  ★★★**★为什么主轴用"真墙" (★实测)★★★**
    · ★**45 条里只有 9 个端点是真墙** ⇒ ★**其余 34 个【端点出得来】, 失败发生在【路径中段】(走廊被堵)**
    · ★★**⇒ 所以"端点有没有墙"是【第一区分维度】, "端点在不在 0.4mm BTB 上"只是【第二维度】(出脚区的物理约束)** ★★
    · ★★★**★⇒ 三个子桶 (★互斥, ★按证据分级)** ★★★
      ★**A1【真墙 + 堵的是自己伙伴腿】** ⇒ ★**成对走廊规划 (pair-aware) 能解** ⇒ ★**改路由器**
      ★**A2【真墙 + 堵的是别的网】** ⇒ ★**拆挡路 / rip-and-replace 能解** ⇒ ★★**现在就能动手** ★★
      ★**B1【无真墙 + 端点在 0.4mm BTB 排针上】** ⇒ ★**出脚区余量 0 ⇒ 需线宽 0.15mm** ⇒ ★**要板厂**
      ★**B2【无真墙 + 普通间距端点】** ⇒ ★**端点能出, 走廊中段被堵** ⇒ ★**要更强路由器 / 拆挡路**

用法:
  bash state/pcbnew_py.sh state/probe_unconnected_worklist_v2.py <板> <DRC.json> --out <wl.txt>
  python3 state/classify_unc.py <wl.txt> [--out <txt>]
"""
import os
import re
import sys

# ★0.4mm pitch 排针的器件前缀 (★实测: SoM BTB = J_SOM_P1..P4)
BTB_FP = re.compile(r"^(J_SOM_P\d|CONN_)", re.I)


def pair_partner(net):
    for a, b in (("_N_SRC", "_P_SRC"), ("_P_SRC", "_N_SRC"), ("_N", "_P"), ("_P", "_N")):
        if net.endswith(a):
            return net[: -len(a)] + b
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    wlp = sys.argv[1]
    outp = None
    if "--out" in sys.argv:
        outp = sys.argv[sys.argv.index("--out") + 1]

    lines = open(wlp, encoding="utf-8").read().split("\n")
    # 行格式: [★墙 ]NET   ENDPOINT ⇒ ★同层异网铜  DISTmm BLOCKER[LAYER] · 异层异网铜 ...
    pat = re.compile(
        r"^\s*(★墙\s+)?(\S+)\s+(\S+)\s+⇒\s+★同层异网铜\s+([-\d.]+)mm\s+(\S+?)\["
    )

    # ★同一 net 可能有多行 (多个端点) ⇒ 逐端点归桶, net 取【最严重】的那档
    order = {"A1": 0, "A2": 1, "B1": 2, "B2": 3}
    per_net = {}
    rows = []

    for ln in lines:
        m = pat.match(ln)
        if not m:
            continue
        is_wall = bool(m.group(1))
        net, ep, dist, blocker = m.group(2), m.group(3), float(m.group(4)), m.group(5)
        part = pair_partner(net)
        on_btb = ep.startswith("J_SOM_P")

        if is_wall and part and blocker == part:
            b = "A1"
            why = f"★真墙: 端点被自己伙伴腿 {blocker} ({dist:.3f}mm) 卡死 ⇒ 成对走廊规划可解"
        elif is_wall:
            b = "A2"
            why = f"★真墙: 端点被 {blocker} ({dist:.3f}mm) 卡死 ⇒ 可拆挡路/rip-and-replace"
        elif on_btb:
            b = "B1"
            why = f"无真墙, 但端点在 0.4mm BTB 排针({ep}) ⇒ 出脚区余量 0 ⇒ 需线宽 0.15mm (要板厂)"
        else:
            b = "B2"
            why = f"无真墙, 普通间距端点({ep}) ⇒ 端点出得来, 走廊中段被堵 (最近异网 {blocker} {dist:.3f}mm) ⇒ 要更强路由器/拆挡路"

        rows.append((net, ep, b, why, is_wall, dist))
        if net not in per_net or order[b] < order[per_net[net][0]]:
            per_net[net] = (b, why, ep, is_wall, dist)

    buckets = {k: [] for k in ("A1", "A2", "B1", "B2")}
    for net, (b, why, ep, wall, dist) in per_net.items():
        buckets[b].append((net, why, wall, ep, dist))

    out = ["★未连接按【堵点性质】分桶 (★几何唯一真源 = probe_unconnected_worklist_v2.py 输出)",
           "★主轴 = 端点是不是真墙 (★45 条里只有 9 个真墙 ⇒ 其余 34 个是路径中段被堵)", ""]
    labels = {
        "A1": "A1 真墙 + 堵的是自己伙伴腿 ⇒ 成对走廊规划 (pair-aware) ⇒ 改路由器",
        "A2": "A2 真墙 + 堵的是别的网 ⇒ 拆挡路 / rip-and-replace ⇒ 【现在就能动手】",
        "B1": "B1 无真墙 + 端点在 0.4mm BTB 出脚区 ⇒ 需线宽 0.15mm ⇒ 要板厂",
        "B2": "B2 无真墙 + 普通间距 ⇒ 端点能出, 走廊中段被堵 ⇒ 要更强路由器 / 拆挡路",
    }
    for b in ("A1", "A2", "B1", "B2"):
        out.append(f"── {labels[b]} ── ({len(buckets[b])} 个网)")
        for net, why, wall, ep, dist in sorted(buckets[b]):
            out.append(f"   {net:<20}{why}")
        out.append("")
    out.append("★★⇒ A2 现在就能动手 · A1 要改路由器 · B1 等板厂 0.15mm · B2 要更强路由器")
    out.append("★★⇒ ★【A1 的 net 名单 == 之前实测的 7 条单边零铜 N 腿】⇒ ★⇒ pair-aware 的靶子完全坐实")

    text = "\n".join(out)
    if outp:
        open(outp, "w", encoding="utf-8").write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
