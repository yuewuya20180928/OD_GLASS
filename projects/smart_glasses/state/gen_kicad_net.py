#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KiCad legacy netlist 导出器 (gen_kicad_net) —— 从 HW/netlist_v1.csv 出 .net
================================================================================
★V1.4 (2026-10-27 09:2x) 重写。原因: 旧版**引脚号是按出现顺序编的**, 导致:
  ① 连接器/IC 的**真实引脚名丢失** (node 名里本来就写着 "J_CHG pin1" / "U_CHG TS" / "J_TYPE_C A6+B6")
     → 旧版把 J_TYPE_C 的 A4/A9/B4/B9 全编成 pin1/2/3/9, **电气上是错的**
  ② **伪 ref 变成幽灵器件** (RAIL_*/NET_*/GND 出现在 components 段)
  ③ 同一个器件在同一 net 里出现多次 → 旧版给同一物理脚发多个 pin 号 → KiCad 判 pin 冲突
  ④ node 名复用 (信号网名里混进 GND 端) → **分压电阻在 .net 里被短接** (hw-lead ISS-088 复审 F6)

★新版的规则 (全部可机械判, 见 state/check_kicad_net.py):
  - **引脚号来自 node 名里的引脚提示** (连接器/IC/SoC) → 稳定、可追溯
  - **裸器件名** (2 脚无源件) → 按它出现在哪些网来定 pin1/pin2 (先到先得, 但**按网定**不按行定)
  - **伪 ref** (RAIL_*/NET_*/GND/SYS_PCB) 是**网名不是器件** → 不进 components, 也不占 pin
  - 一行 = 一根连接 → 该行两端若是器件脚, 则这两个脚都在该行的 net 上
  - `SoC[TBD-01].<信号>` → 合成为器件 `SoC_TBD01`, pin = 信号名 (原厂回信后替换)

用法:  python3 state/gen_kicad_net.py
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
CSV_P = os.path.join(PROJ, "HW", "netlist_v1.csv")
OUT = os.path.join(PROJ, "HW", "netlist_v1.net")

FOOTPRINT = {
    "R": "Resistor_SMD:R_0402_1005Metric",
    "C": "Capacitor_SMD:C_0402_1005Metric",
    "L": "Inductor_SMD:L_0805_2012Metric",
    "D": "Diode_SMD:D_SOD-323",
    "IC": "TBD:IC_PLACEHOLDER",
    "CONN": "TBD:CONN_PLACEHOLDER",
    "SW": "TBD:SW_PLACEHOLDER",
    "LED": "TBD:LED_PLACEHOLDER",
    "TP": "TestPoint:TestPoint_Pad_D1.0mm",
    "NET": "TBD:NET_PLACEHOLDER",
    "RAIL": "TBD:RAIL_PLACEHOLDER",
}

# 伪 ref = 网名, 不是器件
PSEUDO_PREFIX = ("RAIL_", "NET_")
PSEUDO_EXACT = {"GND", "SYS_PCB", "CHG_GND_STAR"}


def is_pseudo(ref: str) -> bool:
    return ref.startswith(PSEUDO_PREFIX) or ref in PSEUDO_EXACT


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=CSV_P)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()
    if not os.path.exists(args.csv):
        print(f"❌ 缺 netlist: {args.csv}", file=sys.stderr)
        return 2
    rows = list(csv.DictReader(open(args.csv, encoding="utf-8")))
    if not rows:
        print("❌ netlist 是空的", file=sys.stderr)
        return 2

    comps: "OrderedDict[str, dict]" = OrderedDict()
    nets: "OrderedDict[str, list]" = OrderedDict()
    known = {r["ref"].strip() for r in rows if (r.get("ref") or "").strip()}
    known -= {x for x in known if is_pseudo(x)}

    def comp(ref: str, value: str, typ: str, page: str):
        if ref not in comps:
            comps[ref] = {"value": value, "footprint": FOOTPRINT.get(typ, "TBD:PLACEHOLDER"),
                          "page": page}

    # 1) 真实器件 (ref 列) —— 伪 ref 不进器件表
    for r in rows:
        ref = (r.get("ref") or "").strip()
        if not ref or is_pseudo(ref):
            continue
        comp(ref, (r.get("value") or "").strip(), (r.get("type") or "").strip(), r.get("page", ""))

    # 2) 节点解析 → [(ref, pin)]  (pin 可能为 None = 裸器件名, 后面按网定)
    def parse_node(node: str):
        node = (node or "").strip()
        if not node:
            return []
        if node.startswith("SoC["):
            m = re.match(r"^SoC\[TBD-01\]\.(.+)$", node)
            if m:
                comp("SoC_TBD01", "ARS45 (8x10 FCCSP, 球位图未回)", "IC", "P2")
                return [("SoC_TBD01", m.group(1))]
            return []
        if " " in node:
            head, rest = node.split(" ", 1)
            if head in known:
                # 引脚提示: "pin1" / "TS" / "A6+B6" (多物理脚用 + 连写)
                pins = [p.strip() for p in rest.split("+") if p.strip()]
                return [(head, p) for p in pins]
        if node in known:
            return [(node, None)]
        return []   # 伪 ref / 未知节点 = 网名, 不算器件脚

    # 3) 收集: 每个 (ref, net) → 引脚号
    #    裸器件名: 按它所在的**网**定 pin (同网同脚, 不同网不同脚) —— 稳定, 不按行数编
    bare_pins: dict[str, "OrderedDict[str, int]"] = {}

    def pin_for_bare(ref: str, net: str) -> int:
        m = bare_pins.setdefault(ref, OrderedDict())
        if net not in m:
            m[net] = len(m) + 1
        return m[net]

    for r in rows:
        net = (r.get("net") or "").strip()
        if not net:
            continue
        if (r.get("note") or "").startswith("[INVENTORY]"):
            continue   # 器件登记行, 不是一根连接 → 混进去会让同一物理脚落多个网
        for node in ((r.get("node1") or ""), (r.get("node2") or "")):
            for ref, pin in parse_node(node):
                if pin is None:
                    pin = pin_for_bare(ref, net)
                nets.setdefault(net, [])
                if not any(n[0] == ref and n[1] == pin for n in nets[net]):
                    nets[net].append((ref, pin))

    # 4) 输出 KiCad legacy netlist
    out = ['(export (version "E")',
           '  (design (source "ARS45_V1.4") (date "2026-10-27") (tool "ARS45-SCH"))',
           '  (components']
    for ref, c in comps.items():
        out.append('    (comp (ref "%s") (value "%s") (footprint "%s"))'
                   % (ref, c["value"].replace('"', "'"), c["footprint"]))
    out.append('  )')
    out.append('  (nets')
    code = 0
    for net, nodes in nets.items():
        code += 1
        out.append('    (net (code "%d") (name "%s")' % (code, net))
        for ref, pin in nodes:
            out.append('      (node (ref "%s") (pin "%s") (pintype "passive"))' % (ref, pin))
        out.append('    )')
    out.append('  )')
    out.append(')')
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")

    print(f"✅ 已导出 {args.out}: {len(comps)} 个器件 / {len(nets)} 个 net / {code} 行 net")
    print("⚠️ SoC 侧 pin = 信号名占位 (原厂球位图未回, TBD-01) → 这不是投板文件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
