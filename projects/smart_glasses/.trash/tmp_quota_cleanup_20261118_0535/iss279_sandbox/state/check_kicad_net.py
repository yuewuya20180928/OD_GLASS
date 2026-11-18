#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KiCad 导出件门禁 (check_kicad_net) —— 2026-10-27 09:2x 新增
================================================================================
★为什么要有: hw-lead 复审 ISS-088 时发现, 旧版 .net 导出器**引脚号是按出现顺序编的**
  → 连接器/IC 的真实引脚名丢失 · 伪 ref 变成幽灵器件 · 同一物理脚发多个 pin 号
  → KiCad import 会判 pin 冲突, 甚至把分压电阻短接。
  旧版**没有任何脚本判过 .net** → 这 4 条就是补上的回归判据。

用法:  python3 state/check_kicad_net.py [--net HW/netlist_v1.net] [--csv HW/netlist_v1.csv]
退出码: 0=全过  1=有违规  2=文件缺失
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
PSEUDO_PREFIX = ("RAIL_", "NET_")
PSEUDO_EXACT = {"GND", "SYS_PCB"}   # CHG_GND_STAR 是**真实的单点汇流位**, 不是网名


def is_pseudo(ref: str) -> bool:
    return ref.startswith(PSEUDO_PREFIX) or ref in PSEUDO_EXACT


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--net", default=os.path.join(PROJ, "HW", "netlist_v1.net"))
    ap.add_argument("--csv", default=os.path.join(PROJ, "HW", "netlist_v1.csv"))
    args = ap.parse_args()
    for p in (args.net, args.csv):
        if not os.path.exists(p):
            print(f"❌ 缺文件: {p}", file=sys.stderr)
            return 2

    txt = open(args.net, encoding="utf-8").read()
    comps = re.findall(r'\(comp \(ref "([^"]+)"\)', txt)
    blocks = re.findall(r'\(net \(code "\d+"\) \(name "([^"]+)"\)(.*?)\n    \)', txt, re.S)
    nodes_by_net = OrderedDict()
    for name, body in blocks:
        nodes_by_net[name] = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]*)"\)', body)

    R = []

    def chk(name, ok, detail=""):
        R.append({"name": name, "ok": bool(ok), "detail": detail})

    # 1) 同一 (ref,pin) 不得出现在多个 net (KiCad 会判 pin 冲突)
    seen: dict[tuple, list] = {}
    for net, nodes in nodes_by_net.items():
        for ref, pin in nodes:
            seen.setdefault((ref, pin), []).append(net)
    conflict = {k: v for k, v in seen.items() if len(v) > 1}
    chk("同一 (ref,pin) 只出现在 1 个 net (无 pin 冲突)", not conflict,
        f"冲突 {list(conflict.items())[:4]}" if conflict else f"{len(seen)} 个 (ref,pin) 全唯一")

    # 2) 器件表里不得有伪 ref (网名当器件 = 幽灵器件)
    ghost = [c for c in comps if is_pseudo(c)]
    chk("器件表无幽灵器件 (RAIL_*/NET_*/GND 不是器件)", not ghost,
        f"幽灵 {ghost[:5]}" if ghost else f"{len(comps)} 个器件全合法")

    # 3) 不得有 net 同时含 GND 与非 GND 器件脚 (= 短路)
    mixed = []
    for net, nodes in nodes_by_net.items():
        refs = {r for r, _ in nodes}
        if "GND" in refs and len(refs) > 1:
            mixed.append(net)
    chk("没有 net 同时含 GND 与其他器件脚 (无隐式短路)", not mixed,
        f"混网 {mixed[:5]}" if mixed else f"{len(nodes_by_net)} 个 net 全干净")

    # 4) CSV 里每个真实器件都要在 .net 里出现 (无孤儿器件)
    rows = list(csv.DictReader(open(args.csv, encoding="utf-8")))
    want = {r["ref"].strip() for r in rows if (r.get("ref") or "").strip() and not is_pseudo(r["ref"].strip())}
    have = {r for r, _ in ((ref, pin) for net, nodes in nodes_by_net.items() for ref, pin in nodes)}
    orphan = sorted(want - have)
    chk("CSV 里每个真实器件都进了 .net (无孤儿)", not orphan,
        f"孤儿 {orphan[:6]}" if orphan else f"{len(want)} 个器件全部落网")

    # 5) ★两脚无源件在 .net 里必须**恰好 2 个脚** (A-3 的判据: 分压上端被并进同一网 →
    #    另一端悬空 → 监督器读 0V → RESET 永不释放)
    rows = list(csv.DictReader(open(args.csv, encoding="utf-8")))
    type_of = {r["ref"].strip(): (r.get("type") or "").strip()
               for r in rows if (r.get("ref") or "").strip()}
    pin_count: dict[str, int] = {}
    for net, nodes in nodes_by_net.items():
        if net == "NC":
            continue
        for ref, _pin in nodes:
            pin_count[ref] = pin_count.get(ref, 0) + 1
    two_pin = {"R", "C", "L"}
    bad_pin = {r: c for r, c in pin_count.items()
               if type_of.get(r) in two_pin and c != 2}
    # D 类 (ESD 阵列 / TVS) 是多脚件 → 3-4 脚合法 (2 路 I/O + 地)
    bad_d = {r: c for r, c in pin_count.items()
             if type_of.get(r) == "D" and c < 2}
    chk("两脚无源件 (R/C/L) 在 .net 里恰好 2 个脚 (无悬空脚/无同网并脚)", not bad_pin and not bad_d,
        f"脚数不对: {list(bad_pin.items())[:6]}" if bad_pin else
        (f"D 类多脚件脚数异常: {list(bad_d.items())[:4]}" if bad_d else f"{len(pin_count)} 个器件脚数全对"))

    # 6) 单点网 = **提示项** (不判失败)。
    #    根因: 我们的网表是"连接清单"模型 (一行 = 一根连接), 而 KiCad 网表要的是
    #    "每引脚一行" (pin-centric)。RAIL_* 别名 (如 RAIL_VBUS_5V 与 VBUS_5V 指同一个节点)
    #    与若干 1 脚连接件, 会在导出后表现为单点网 → **投板前必须做一次 pin-centric 重整**
    #    (已登记 ISS-094)。这里只报数, 不假装通过。
    thin = [n for n, nodes in nodes_by_net.items() if len(nodes) < 2]
    print(f"  ℹ️  单点网 (提示项, 不判失败): {len(thin)} 个 → {thin[:8]}")
    if thin:
        R.append({"name": "单点网清单 (投板前要 pin-centric 重整, 见 ISS-094)", "ok": True,
                  "detail": f"{len(thin)} 个"})

    # ★★6) ★★2026-11-06 新增 (实测事故回补): **CSV 里带引脚提示的节点, .net 里一个都不能缺**
    #   ★**为什么加这条**: 2026-11-06 实测发现 `.net` 导出器 (gen_kicad_net.py) 把
    #   **J_SOM_P2 / J_SOM_P4 这两个只在 node 串里出现、ref 列里没有的座** 的 23 个脚
    #   **静默丢弃**了 (.net 里 J_SOM_P2=0 节点 / J_SOM_P4=0 节点) ⇒
    #   ★而本文件原有的 5 条判据**全部通过 (rc=0)** ⇒ ★**"门禁形同虚设"**
    #   ⇒ 后果: gen_netlist_pins.py 的"SoC 引脚 >= 50" 判红 ⇒ 脚级表从 11-03 起停更。
    #   ⇒ 这条判据 = **按"CSV 说该有多少脚, .net 就得有多少脚"逐个点名**, 与 ref 列无关 ⇒
    #   ★**只要导出器再丢任何一个脚, 这条立刻报红** (而不是像这次一样静默三天)。
    #   ★口径: 只查**单脚提示** (不含 '+'); 多脚展开 (如 "J_USB_C A6+B6") 是"一脚并联多物理脚",
    #   导出后拆成多个 pin ⇒ 口径不同, 不在本判据内。
    csv_rows = list(csv.DictReader(open(args.csv, encoding="utf-8")))
    csv_labels = {(r.get("net") or "").strip() for r in csv_rows}
    have_pins = {(ref, pin) for ref, pin in
                 ((r, p) for net_, nodes in nodes_by_net.items() for r, p in nodes)}
    want_pins: set[tuple[str, str]] = set()
    for r in csv_rows:
        for k in ("node1", "node2"):
            n = (r.get(k) or "").strip()
            if " " not in n:
                continue
            head, rest = n.split(" ", 1)
            head, rest = head.strip(), rest.strip()
            if not head or "+" in rest:
                continue
            if head in csv_labels:                      # 网名不是器件
                continue
            if head.startswith(("NET_", "RAIL_")) or head in ("GND", "VSS", "VDD", "SYS_PCB"):
                continue
            want_pins.add((head, rest))
    lost = sorted(want_pins - have_pins)
    chk("CSV 里带引脚提示的脚, .net 里一个不缺 (导出器不许静默丢脚)", not lost,
        f"★丢了 {len(lost)} 个脚 ⇒ 导出器把只在 node 串里出现的器件整组丢掉了 (实测: J_SOM_P2/J_SOM_P4)"
        if lost else f"{len(want_pins)} 个带引脚提示的脚全在 .net 里")

    bad = [x for x in R if not x["ok"]]
    print("=" * 72)
    print("  KiCad 导出件门禁 · 项目总工机械验收")
    print("=" * 72)
    for x in R:
        print(f"  {'✅' if x['ok'] else '❌'} {x['name']}")
        if x["detail"]:
            print(f"       {x['detail']}")
    print()
    print(f"  {'✅ 全过 — .net 与 netlist 一致 (可给 PCB 工程师)' if not bad else f'❌ {len(bad)} 项不通过'}")
    print("=" * 72)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
