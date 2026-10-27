#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KiCad legacy netlist 导出器 (gen_kicad_net) —— 从 HW/netlist_v1.csv 出 .net
================================================================================
★V1.6 (2026-10-27 18:5x) 第三次重写。起因: hw-lead 复审 ISS-088 报出的 A-3/A-5 + B-4/B-5/B-7。

★网表模型的正确解读 (前两版都错在这):
  我们的 CSV 是"**一行 = 一根连接**"(node1 ↔ node2, ref = 这根连接上经过的器件),
  但**一行 ≠ 一个引脚归属的节点**。一个 2 脚器件 (如分压电阻) 必然出现在**两行**里:
    行 1: net=SENSE,  node1=分压上端, node2=R_DIV1      ← R_DIV1 的这一脚在 SENSE 上
    行 2: net=SENSE,  node1=R_DIV1,    node2=分压下端    ← R_DIV1 的另一脚也在 SENSE 上?
  → 只有当**一行里恰好有一个器件端 + 一个"网别名"端**时, 才能判定该器件脚挂在**别名**那一侧;
    这就是 A-3 (R_SUPV_DIV1 的 V_SOC_IO 端被当成"同一网" → 导出后悬空 → U_SUPV.IN≈0V → RESET 永不释放) 的成因。

★本版的判定规则:
  1) **别名规范化**: `RAIL_X` → `X` (电源轨与网名同指一个节点) · `NET_X` → `X` ·
     少数特例走显式表 (`NET_BAT_PROT`→`BAT_CHG`, `NET_SYS_3V3`→`SYS`)
  2) **一行里 2 个器件端** → 这两个脚都在该行的 net 上 (一根线)
  3) **一行里 1 个器件端 + 1 个别名端** → 该器件脚挂在**别名**那一侧, 该行 net 是它的**另一侧**
  4) **一行里 1 个器件端 + 1 个自引用端** (node == net) → 该器件脚挂在该行 net 上
  5) 每个器件的脚 = 它出现过的各个 net (按首次出现顺序编号) ⇒ 一个器件跨两个网 = 它在两者之间
  6) `[INVENTORY]` 登记行 → 只用来占位 (那些脚进 NC 网, 让 PCB 工程师看见"这个脚故意不接"),
     本身不产生连接 (B-5)
  7) 节点名带引脚提示 (`J_CHG pin1` / `U_CHG TS` / `SoC[TBD-01].<信号>`) → **真实物理脚**, 直接用
  8) 裸器件名 (2 脚无源件) → 脚号按"它出现在哪个网"顺序推定 (B-4: 幻影脚号只出现在多脚 IC 上,
     那种器件必须用带提示的节点名 —— 见本文末尾的约定)

用法:  python3 state/gen_kicad_net.py
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import OrderedDict, defaultdict

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

# 别名 → 规范网名
ALIAS_MAP = {
    "NET_BAT_PROT": "BAT_CHG",
    "NET_SYS_3V3": "SYS",
    "RAIL_SYS_PCB": "SYS",
    "RAIL_GND": "GND",
}


def canon(node: str) -> str:
    """别名规范化: RAIL_X / NET_X → X (特例走表)"""
    node = (node or "").strip()
    if node in ALIAS_MAP:
        return ALIAS_MAP[node]
    if node.startswith("RAIL_"):
        return node[5:]
    if node.startswith("NET_"):
        return node[4:]
    return node


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

    known = {r["ref"].strip() for r in rows if (r.get("ref") or "").strip()}
    # 网名集合 (行标签) —— 用来判断某个节点是不是"网别名"
    net_labels = {r["net"].strip() for r in rows if (r.get("net") or "").strip()}
    # 真实器件 (ref 列, 排除纯网名伪 ref)
    netlike = {n for n in known if n.startswith("RAIL_") or n.startswith("NET_") or n == "GND"}
    devices = known - netlike

    comps: "OrderedDict[str, dict]" = OrderedDict()

    def comp(ref: str, value: str, typ: str, page: str):
        if ref not in comps:
            comps[ref] = {"value": value, "footprint": FOOTPRINT.get(typ, "TBD:PLACEHOLDER")}

    # 器件表: 从 ref 列取; 连接器的 value/footprint 优先取"带声明格式"的那一行 (B-7)
    for r in rows:
        ref = (r.get("ref") or "").strip()
        if not ref or ref not in devices:
            continue
        val = (r.get("value") or "").strip()
        typ = (r.get("type") or "").strip()
        cur = comps.get(ref)
        if cur is None:
            comp(ref, val, typ, r.get("page", ""))
            continue
        # 声明式 value (含 Np / N×Mp) 更权威 → 覆盖
        if re.search(r"\d+\s*[×x]?\s*\d*\s*p\b", val) and not re.search(r"\d+\s*[×x]?\s*\d*\s*p\b", cur["value"]):
            cur["value"] = val

    def parse_node(node: str):
        """节点 → [(ref, pin_hint or None)]"""
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
            if head in devices:
                pins = [p.strip() for p in rest.split("+") if p.strip()]
                return [(head, p) for p in pins]
        if node in devices:
            return [(node, None)]
        return []

    def is_alias(node: str) -> bool:
        node = (node or "").strip()
        if node in devices:
            return False
        return canon(node) in net_labels or node in net_labels

    # ---- 收集: 器件脚 → 网 ----
    # ★核心规则 (V1.6): **一个器件跨的网 = 它出现过的所有"行网" + 同行出现的"别名网"**
    #   例: 行 (net=KEY_PWR, node1=C_KEY_PWR, node2=GND) → 电容跨 {KEY_PWR, GND} (两个脚)
    #       行 (net=SUPV_SENSE, node1=RAIL_V_SOC_IO, node2=R_SUPV_DIV1) → 电阻跨 {SUPV_SENSE, V_SOC_IO}
    #   前一版只记了别名那一侧 → 器件只剩 1 个脚 → 导出后悬空 (就是复审报的 A-3)。
    pin_net: dict[tuple, str] = {}          # (ref, pin) → net
    dev_nets: dict[str, list] = defaultdict(list)   # ref → 依次遇到的网 (裸器件用来定脚号)
    hinted_pins: dict[str, list] = defaultdict(list)  # ref → 明确点名的脚
    nc_pins: list[tuple] = []               # INVENTORY 声明但没连的脚 → NC

    def dev_of(node: str):
        return parse_node(node)

    for r in rows:
        net = (r.get("net") or "").strip()
        if not net:
            continue
        inv = (r.get("note") or "").startswith("[INVENTORY]")
        n1, n2 = (r.get("node1") or "").strip(), (r.get("node2") or "").strip()
        d1, d2 = dev_of(n1), dev_of(n2)
        a1, a2 = is_alias(n1), is_alias(n2)
        alias_net = canon(n2 if a2 else (n1 if a1 else ""))
        if inv:
            for ref, pin in d1 + d2:
                if pin is not None and (ref, pin) not in pin_net:
                    nc_pins.append((ref, pin))
            continue
        devs = d1 + d2
        # 行 ref 也是这根连接上的器件 (裸名时它就是这根线的中继点)
        rowref = (r.get("ref") or "").strip()
        if rowref in devices and rowref not in {x[0] for x in devs}:
            devs = devs + [(rowref, None)]
        for ref, pin in devs:
            if net and net not in dev_nets[ref]:
                dev_nets[ref].append(net)
            if alias_net and alias_net not in dev_nets[ref]:
                dev_nets[ref].append(alias_net)
            if pin is not None:
                hinted_pins[ref].append(pin)
                # 明确点名的脚: 挂在**行网**上; 若同行有别名且别名≠行网, 该脚在别名侧
                target = alias_net if (alias_net and alias_net != net) else net
                pin_net.setdefault((ref, pin), target)

    # 裸器件: 脚号按"它跨了哪些网"顺序推定 (2 脚件 → pin1/pin2)
    for ref, nets in dev_nets.items():
        if hinted_pins.get(ref):
            continue
        for i, net in enumerate(nets, start=1):
            pin_net.setdefault((ref, str(i)), net)

    # 组网
    nets_out: "OrderedDict[str, list]" = OrderedDict()
    for (ref, pin), net in pin_net.items():
        nets_out.setdefault(net, [])
        if not any(x[0] == ref and x[1] == pin for x in nets_out[net]):
            nets_out[net].append((ref, pin))
    for ref, pin in nc_pins:
        if (ref, pin) in pin_net:
            continue
        nets_out.setdefault("NC", [])
        if not any(x[0] == ref and x[1] == pin for x in nets_out["NC"]):
            nets_out["NC"].append((ref, pin))

    # 组件清单: 所有真实器件都要有 (即使没进网)
    for r in rows:
        ref = (r.get("ref") or "").strip()
        if ref and ref in devices:
            comp(ref, (r.get("value") or "").strip(), (r.get("type") or "").strip(), r.get("page", ""))

    out = ['(export (version "E")',
           '  (design (source "ARS45_V1.6") (date "2026-10-27") (tool "ARS45-SCH"))',
           '  (components']
    for ref, c in comps.items():
        out.append('    (comp (ref "%s") (value "%s") (footprint "%s"))'
                   % (ref, c["value"].replace('"', "'"), c["footprint"]))
    out.append('  )')
    out.append('  (nets')
    code = 0
    for net, nodes in nets_out.items():
        code += 1
        out.append('    (net (code "%d") (name "%s")' % (code, net))
        for ref, pin in nodes:
            out.append('      (node (ref "%s") (pin "%s") (pintype "passive"))' % (ref, pin))
        out.append('    )')
    out.append('  )')
    out.append(')')
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")

    print(f"✅ 已导出 {args.out}: {len(comps)} 个器件 / {len(nets_out)} 个 net / {code} 行 net")
    print("⚠️ SoC 侧 pin = 信号名占位 (原厂球位图未回, TBD-01) → 这不是投板文件")
    print("★约定: **多脚器件 (IC/连接器) 的节点名必须带引脚提示** (如 'U_CHG TS' / 'J_CHG pin1'), "
          "否则导出的脚号是按网序推的幻影脚号 (B-4)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
