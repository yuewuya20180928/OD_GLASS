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
