#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KiCad 兼容 netlist 导出器 (gen_kicad_net) —— 从 netlist_v1.csv 导出 KiCad legacy .net
================================================================================
★边界说明 (重要, 别误读):
  本项目 SoC 引脚表/球位图**还没拿到** (TBD-01) → 所以这份 .net 里 **SoC 侧引脚号是临时编号**
  (U_SOC 的 pin 号按 netlist 出现顺序分配), 用途是:
    ① 让老板本地装 KiCad 后能 **import 出一张可看的原理图** (结构对不对一眼看得出)
    ② 让 netlist 进入 KiCad 生态 (ERC / 封装替换 / 出 BOM)
  ③ **它不是投板文件** —— 原厂回信后必须把 pin 号替换成真球号 (这一步在任务书里写死)

用法:
  python3 state/gen_kicad_net.py                 # 写 HW/netlist_v1.net
  python3 state/gen_kicad_net.py --csv X --out Y
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

FOOTPRINT = {  # 规格里明写的用规格值, 其余给占位 (标 待定)
    "R": "Resistor_SMD:R_0402_1005Metric",
    "C": "Capacitor_SMD:C_0402_1005Metric",
    "TP": "TestPoint:TestPoint_Pad_D1.0mm",
    "RAIL": "Regulator_Linear:",
    "NET": "",
}
VALUE_HINT = {"R": "0402", "C": "0402"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=os.path.join(PROJ, "HW", "netlist_v1.csv"))
    ap.add_argument("--out", default=os.path.join(PROJ, "HW", "netlist_v1.net"))
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

    def comp(ref: str, value: str, typ: str, page: str):
        if ref not in comps:
            fp = FOOTPRINT.get(typ, "")
            comps[ref] = {"value": value, "footprint": fp, "page": page, "pins": []}

    # 1) 收集器件 (ref 列) + 合成连接器/SoC
    for r in rows:
        ref = (r.get("ref") or "").strip()
        typ = (r.get("type") or "").strip()
        if not ref:
            continue
        val = (r.get("value") or "").strip()
        comp(ref, val, typ, r.get("page", ""))
    # 端点里的连接器/SoC 也作为器件
    for r in rows:
        for node in ((r.get("node1") or ""), (r.get("node2") or "")):
            node = node.strip()
            if node.startswith("SoC["):
                comp("U_SOC", "ARS45 (同 Die 参考版)", "IC", r.get("page", ""))
            elif node.startswith("CONN_LIGHT"):
                comp("CONN_LIGHT", "40p 光机连接器", "CONN", r.get("page", ""))
            elif node.startswith("CONN_CAM"):
                comp("CONN_CAM", "40p 摄像头连接器", "CONN", r.get("page", ""))
            elif node.startswith("J_BOOT"):
                comp("J_BOOT1", "启动存储焊盘位", "CONN", r.get("page", ""))
            elif node == "GND":
                comp("GND", "机壳地/数字地", "PWR", r.get("page", ""))

    # 2) 分配临时 pin 号
    pinno: dict[str, int] = {}

    def pin_of(ref: str) -> int:
        n = pinno.get(ref, 0) + 1
        pinno[ref] = n
        return n

    for r in rows:
        net = (r.get("net") or "").strip()
        if not net:
            continue
        for node in ((r.get("node1") or ""), (r.get("node2") or "")):
            node = node.strip()
            if not node:
                continue
            if node.startswith("SoC["):
                ref, pin = "U_SOC", pin_of("U_SOC")
            elif node.startswith("CONN_LIGHT"):
                ref, pin = "CONN_LIGHT", pin_of("CONN_LIGHT")
            elif node.startswith("CONN_CAM"):
                ref, pin = "CONN_CAM", pin_of("CONN_CAM")
            elif node.startswith("J_BOOT"):
                ref, pin = "J_BOOT1", pin_of("J_BOOT1")
            elif node == "GND":
                ref, pin = "GND", pin_of("GND")
            else:
                # 器件端: 用本行的 ref (NET_* 行时用信号名当伪器件)
                ref = (r.get("ref") or "NET").strip() or "NET"
                pin = pin_of(ref)
            nets.setdefault(net, [])
            if not any(n[0] == ref and n[1] == pin for n in nets[net]):
                nets[net].append((ref, pin))

    # 3) 输出 KiCad legacy netlist
    out = ['(export (version "E")',
           '  (design (source "ARS45_V1") (date "2026-10-26") (tool "ARS45-SCH"))',
           '  (components']
    for ref, c in comps.items():
        fp = c["footprint"] or ""
        out.append('    (comp (ref "%s") (value "%s") (footprint "%s"))' % (ref, c["value"], fp))
    out.append('  )')
    out.append('  (nets')
    code = 0
    for net, nodes in nets.items():
        code += 1
        out.append('    (net (code "%d") (name "%s")' % (code, net))
        for ref, pin in nodes:
            out.append('      (node (ref "%s") (pin "%d") (pintype "passive"))' % (ref, pin))
        out.append('    )')
    out.append('  )')
    out.append(')')
    open(args.out, "w", encoding="utf-8").write("\n".join(out) + "\n")

    print(f"✅ 已导出 {args.out}: {len(comps)} 个器件 / {len(nets)} 个 net / {code} 行 net")
    print("⚠️ SoC 侧 pin 号是**临时编号** (原厂球位图未回, TBD-01) → 这不是投板文件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
