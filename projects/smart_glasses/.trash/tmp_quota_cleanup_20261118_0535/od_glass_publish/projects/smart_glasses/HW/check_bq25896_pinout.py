#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BQ25896 24 脚 pinout 机械复核 (ISS-112 (d) · 2026-10-29 · hw-lead)
================================================================================
★为什么要有这个脚本:
  ISS-112 的起因是 BQ25896 的**封装**在库里写错 (VQFN-16 3×3 → 实为 WQFN RTW 24 4×4)。
  封装一改, 就要回答一个更要命的问题: **库里的 24 脚 pinout 表和网表引用有没有错位?**
  错位 = 按表画板、按表买料, 结果 pin1 不是 VBUS ⇒ 芯片不工作 / 短路 ⇒ 2-4 周返工。

★官方真值 (逐字抄自 datasheet, 不靠记忆):
  TI BQ25896 datasheet **SLUSC76C** (2015-07, Rev. 2018-05) **§7 Pin Configuration and Functions**,
  第 5-6 页 "Pin Functions" 表 + 第 5 页 "Top View" 引脚图。
  ★datasheet 本身印的就是 **24 脚** —— 所以"24 脚"没错, 错的只是**封装名**。
  - 官方引脚图 (Top View):
      左列   VBUS 1 / PSEL 2 / PG 3 / STAT 4 / SCL 5 / SDA 6
      底行   7(INT) 8(OTG) 9(CE) 10(ILIM) 11(TS) 12(QON)
      右列   18 PGND / 17 PGND / 16 SYS / 15 SYS / 14 BAT / 13 BAT
      顶行   24 NC / 23 PMID / 22 REGN / 21 BTST / 20 SW / 19 SW
  - 官方 "Pin Functions" 表逐条: pin1 VBUS(P) / 2 PSEL(DI) / 3 PG(DO) / 4 STAT(DO) /
    5 SCL(DI) / 6 SDA(DIO) / 7 INT(DO) / 8 OTG(DI) / 9 CE(DI) / 10 ILIM(AI) / 11 TS(AI) /
    12 QON(DI) / 13,14 BAT(P) / 15,16 SYS(P) / 17,18 PGND(P) / 19,20 SW(P) / 21 BTST(P) /
    22 REGN(P) / 23 PMID(DO) / 24 NC(No Connect) / PowerPAD(P, 散热焊盘)

★本脚本查什么:
  ① **24 脚表本身**: 库内 §2.2 表 + 网表里的 "全 24 脚对照" 串, 是否与官方一致
  ② **网表引用**: netlist_v1.csv 里每一条 "U_CHG pinN" 引用, 该 pin 上挂的网是否符合官方功能
  ③ **覆盖率**: 1-24 号脚有没有被漏引用 (漏了 = 某个脚悬空没画)
  ④ **越界**: 有没有引用 pin0 / pin25 以上的脚
  ⑤ ★**附带查 J_CHG 跨铰链 pin map 三方口径是否一致** (见 §B4) —— 这条不在 ISS-112 范围内,
     但它是同一次复核里冒出来的**同等级返工风险**, 必须一并报出来

★★★2026-11-12 (ISS-136) ★★ 本脚本从"**只看网表**"改成"**规格表 + 网表真对拍**":
  ★**根因**: ⑦ 原来比的是「脚本里硬编的快照 vs 网表」—— ★**规格文件根本没参与判定**
  ⇒ 规格 §5.2 怎么漂移它都不知道 ⇒ 这就是"**一直是绿的假象**"的来源 (方法论问题, 不是单个脚本问题)。
  ⇒ 现在 ⑦ **实读** `HW/CHARGE_BOARD_SPEC.md` §5.2 的 pin map 表逐脚对拍网表 ⇒ **表一改就红**。
  ★**真源 = `HW/netlist_v1.csv`** (投板真源); 规格 §5.2 表 = 网表的镜像; 脚本内 `spec_proposal` = 已批准基线快照。

用法:
  python3 HW/check_bq25896_pinout.py
  python3 HW/check_bq25896_pinout.py --json
退出码: 0 = 全过 (或只报"待裁决项"), 1 = 有 FAIL
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
NETLIST = os.path.join(PROJ, "HW", "netlist_v1.csv")
SPEC = os.path.join(PROJ, "HW", "CHARGE_BOARD_SPEC.md")
P10JSON = os.path.join(PROJ, "state", "p10_rows.json")

# ---------------------------------------------------------------- 官方真值 [官方]
# pin -> (名称, 类型, 允许出现的网名集合, datasheet 原文关键句)
#   ★允许网集合 = 本设计里该脚"应该"接到哪个网; 网表引用落在集合外 = 错位
PINMAP: "OrderedDict[int, tuple]" = OrderedDict([
    (1,  ("VBUS",  "P",  {"VBUS_5V_CHG", "VBUS_5V_F1", "VBUS_5V", "VBUS_5V_ESD"},
          "The internal n-channel reverse block MOSFET (RBFET) is connected between VBUS and PMID ...")),
    (2,  ("PSEL",  "DI", {"PSEL"},
          "High indicates a USB host source and Low indicates an adapter source.")),
    (3,  ("PG",    "DO", {"PWR_GOOD"},
          "Open drain active low power good indicator. ... LOW indicates a good input source ...")),
    (4,  ("STAT",  "DO", {"CHG_STAT", "CHG_STAT_L"},
          "Open drain charge status output ... LOW indicates charge in progress ...")),
    (5,  ("SCL",   "DI", {"I2C_CHG_SCL"},
          "I2C Interface clock. Connect SCL to the logic rail through a 10-kOhm resistor.")),
    (6,  ("SDA",   "DIO", {"I2C_CHG_SDA"},
          "I2C Interface data. Connect SDA to the logic rail through a 10-kOhm resistor.")),
    (7,  ("INT",   "DO", {"INT", "INT_CHG", "NC"},
          "Open-drain Interrupt Output. ... The INT pin sends active low, 256-us pulse to host ...")),
    (8,  ("OTG",   "DI", {"OTG", "OTG_SET"},
          "Boost mode enable pin. The boost mode is activated when OTG_CONFIG =1, OTG pin is high ...")),
    (9,  ("CE",    "DI", {"CE", "CE_SET"},
          "Active low Charge Enable pin. ... CE pin must be pulled High or Low.")),
    (10, ("ILIM",  "AI", {"ILIM", "IINLIM"},
          "IINMAX = KILIM/RILIM ... ILIM pin sets the maximum input current limit by regulating the ILIM voltage at 0.8 V.")),
    (11, ("TS",    "AI", {"TS_BAT", "TS"},
          "Temperature qualification voltage input. ... Program temperature window with a resistor divider from REGN to TS to GND.")),
    (12, ("QON",   "DI", {"QON", "NC"},
          "BATFET enable/reset control input. ... The pin contains an internal pull-up to maintain default high logic")),
    (13, ("BAT",   "P",  {"BAT_CHG", "BAT"},
          "Battery connection point to the positive terminal of the battery pack. ... Connect a 10uF closely to the BAT pin.")),
    (14, ("BAT",   "P",  {"BAT_CHG", "BAT"},
          "Battery connection point to the positive terminal of the battery pack. ... Connect a 10uF closely to the BAT pin.")),
    (15, ("SYS",   "P",  {"SYS_CHG", "SYS"},
          "System connection point. ... Connect a 20uF closely to the SYS pin.")),
    (16, ("SYS",   "P",  {"SYS_CHG", "SYS"},
          "System connection point. ... Connect a 20uF closely to the SYS pin.")),
    (17, ("PGND",  "P",  {"PGND", "GND", "TS_RTN"},
          "Power ground connection for high-current power converter node. ... A single point connection is recommended ...")),
    (18, ("PGND",  "P",  {"PGND", "GND", "TS_RTN"},
          "Power ground connection for high-current power converter node. ... A single point connection is recommended ...")),
    (19, ("SW",    "P",  {"SW"},
          "Switching node connecting to output inductor. ... Connect the 0.047uF bootstrap capacitor from SW to BTST.")),
    (20, ("SW",    "P",  {"SW"},
          "Switching node connecting to output inductor. ... Connect the 0.047uF bootstrap capacitor from SW to BTST.")),
    (21, ("BTST",  "P",  {"BTST"},
          "PWM high side driver positive supply. ... Connect the 0.047uF bootstrap capacitor from SW to BTST.")),
    # ★★2026-11-02 02:1x 收紧: 原允许集合含 TS_BAT ⇒ 一处笔误 (RT1 的 TS 端写成 "U_CHG pin22"
    #   而不是 pin11) 被放过 ⇒ TS 与 REGN 短接 (BQ25896 内部 5V LDO 输出被短到电池 NTC 节点)。
    #   **REGN 是 LDO 输出, 只能是 REGN / REGN_5V** —— TS 归 pin11。
    (22, ("REGN",  "P",  {"REGN", "REGN_5V"},
          "PWM low side driver positive supply output. ... Connect a 4.7uF (10 V rating) ceramic capacitor from REGN to analog GND.")),
    (23, ("PMID",  "DO", {"PMID"},
          "Connected to the drain of the reverse blocking MOSFET (RBFET) and the drain of HSFET. ... put 1uF on VBUS to PGND, and the rest capacitance on PMID to PGND.")),
    (24, ("NC",    "-",  {"NC", "NC_UCHG"},
          "No Connect")),
])

# 官方 "全 24 脚对照" 串 (datasheet 引脚图读出来的标准写法)
OFFICIAL_LINE = ("1 VBUS / 2 PSEL / 3 PG / 4 STAT / 5 SCL / 6 SDA / 7 INT / 8 OTG / 9 CE / "
                 "10 ILIM / 11 TS / 12 QON / 13-14 BAT / 15-16 SYS / 17-18 PGND / 19-20 SW / "
                 "21 BTST / 22 REGN / 23 PMID / 24 NC")

PIN_RE = re.compile(r"U_CHG\s+pin\s*(\d+)(?:\s*\+\s*pin\s*(\d+))?", re.I)
JCHG_RE = re.compile(r"J_CHG\s+pin\s*(\d+)", re.I)

RESULTS = []

# ★★ISS-136 (2026-11-12) ★★ J_CHG 跨铰链 pin map 的**已批准基线快照**
#   ★**真源 = `HW/netlist_v1.csv`** (投板真源, 与 PCB/原理图/BOM 同源) ⇒ 本快照必须逐脚等于它。
#   ★历史 (为什么原来是错的):
#     - 2026-10-29 ISS-112 (d): 快照 = 规格 §5.2 **提案** (pin5=TS_BAT / pin7=PWR_GOOD / pin8=VBUS_DET
#       / pin9=I2C_SCL / pin10=I2C_SDA) ⇒ 与网表差 6 脚;
#     - 2026-11-02 03:0x: 快照被改成 "V1.8 后" 的口径 (pin5=CHG_STAT / pin7=VBUS_DET / pin10=TS_RTN)
#       ⇒ 当时与网表一致, 但网表后来又变 (见下), 快照就**过期**了;
#     - 2026-11-04: 网表 pin7 由 VBUS_DET 改 **NC** (VBUS_DET 改主板本地分压);
#     - 2026-11-03: 网表撤除跨铰链 `TS_RTN` 残留 ⇒ pin10 由 TS_RTN 改 **HINGE_RSV**;
#       ⇒ pin10 现在是 DNP 预留位, NTC 与 30.31k 分压下臂改回 PGND。
#   ★**今天 (2026-11-12) 的口径**: 规格 §5.2 表已按网表订正 (见 CHARGE_BOARD_SPEC.md §5.2 注记),
#   本快照同步为同一真源 ⇒ ⑦ (规格实读) 与 ⑦b (本快照) 都与网表一致。
SPEC_PROPOSAL = {1: "BAT_CHG", 2: "BAT_CHG", 3: "GND", 4: "GND",
                  5: "CHG_STAT", 6: "PWR_GOOD", 7: "NC", 8: "TS_BAT",
                  9: "HINGE_RSV", 10: "HINGE_RSV"}


def rec(ok: bool, name: str, detail: str = "") -> None:
    RESULTS.append({"name": name, "ok": bool(ok), "detail": detail})


def scan_netlist():
    """扫 netlist_v1.csv: U_CHG pinN 引用 -> (net, node 对端, 行号)"""
    hits = []
    with open(NETLIST, encoding="utf-8", newline="") as f:
        for i, r in enumerate(csv.DictReader(f), start=2):
            for side in ("node1", "node2"):
                nd = r.get(side) or ""
                m = PIN_RE.search(nd)
                if not m:
                    continue
                pins = [int(m.group(1))]
                if m.group(2):
                    pins.append(int(m.group(2)))
                other = r.get("node2") if side == "node1" else r.get("node1")
                hits.append({"line": i, "page": r.get("page", ""), "net": r.get("net", ""),
                             "pin_node": nd, "pins": pins, "other": other,
                             "ref": r.get("ref", ""), "note": r.get("note", ""),
                             "inventory": "[INVENTORY]" in (r.get("note") or "")})
    return hits


def scan_pin_uniqueness():
    """★扫描 **全网表** (不只 U_CHG): 同一物理脚出现在多个网 = KiCad pin conflict.
       [INVENTORY] 登记行按设计只占位不产生连接 ⇒ 不算冲突。"""
    dev_pin = defaultdict(set)      # (dev, pin) -> {net}
    where = defaultdict(list)
    with open(NETLIST, encoding="utf-8", newline="") as f:
        for i, r in enumerate(csv.DictReader(f), start=2):
            if "[INVENTORY]" in (r.get("note") or ""):
                continue
            for side in ("node1", "node2"):
                nd = (r.get(side) or "").strip()
                m = re.match(r"^([A-Za-z_0-9]+)\s+pin\s*(\d+)(?:\s*\+\s*pin\s*(\d+))?$", nd, re.I)
                if not m:
                    continue
                dev = m.group(1)
                pins = [m.group(2)] + ([m.group(3)] if m.group(3) else [])
                for p in pins:
                    dev_pin[(dev, p)].add(r.get("net", ""))
                    where[(dev, p)].append((i, r.get("page", ""), r.get("net", "")))
    conflicts = {k: sorted(v) for k, v in dev_pin.items() if len(v) > 1}
    return conflicts, where


def scan_kicad_export():
    """扫导出的 HW/netlist_v1.net: U_CHG 每个脚实际落在哪个网"""
    p = os.path.join(PROJ, "HW", "netlist_v1.net")
    if not os.path.exists(p):
        return {}
    txt = open(p, encoding="utf-8").read()
    out = {}
    for code, name, body in re.findall(r"\(net \(code \"(\d+)\"\) \(name \"([^\"]+)\"\)(.*?)\n    \)",
                                        txt, re.S):
        for ref, pin in re.findall(r'\(ref "([^"]+)"\) \(pin "([^"]+)"\)', body):
            if ref == "U_CHG":
                out.setdefault(pin, []).append(name)
    return out


def scan_spec():
    """扫 CHARGE_BOARD_SPEC.md: §2.2 表的 pin 列 + P10 csv 块 + '全 24 脚对照' 串"""
    txt = open(SPEC, encoding="utf-8").read()
    lines_found = []
    for m in re.finditer(re.escape(OFFICIAL_LINE), txt):
        lines_found.append(m.start())
    # §2.2 表: | **1** | VBUS | P | ...
    table = {}
    for m in re.finditer(r"^\|\s*\*\*(\d+)(?:,(\d+))?\*\*\s*\|\s*([A-Z_0-9]+)\s*\|", txt, re.M):
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else None
        name = m.group(3)
        table[a] = name
        if b:
            table[b] = name
    # P10 csv 块里的 U_CHG pinN
    blk = re.search(r"```csv\n(.*?)```", txt, re.S)
    p10 = []
    if blk:
        for row in csv.DictReader(blk.group(1).splitlines()):
            for side in ("node1", "node2"):
                nd = row.get(side) or ""
                m = PIN_RE.search(nd)
                if not m:
                    continue
                pins = [int(m.group(1))]
                if m.group(2):
                    pins.append(int(m.group(2)))
                p10.append({"net": row.get("net", ""), "pins": pins, "node": nd,
                            "ref": row.get("ref", ""), "board": row.get("board", "")})
    return {"official_line_count": len(lines_found), "table": table, "p10": p10}


def scan_spec_jchg_pinmap():
    """★**实读** CHARGE_BOARD_SPEC.md §5.2 的 J_CHG pin map 表 → {pin: 网名}

    ★★**为什么必须"实读" (ISS-136 · 2026-11-12)**: 检查项 ⑦ 原来比的是「脚本里硬编的快照
    vs 网表」⇒ ★**规格文件根本没有参与判定** ⇒ 规格 §5.2 改了多少它都不会红 ⇒ "一直是绿的假象"。
    ⇒ 现在规格表是判据的一部分 ⇒ 规格漂移 = 本脚本红 = 闸红。

    ★只认 §5.2 一节内的表格行 ("| pinN | `网名` | ..."), 以 '>' 开头的引用块 (ISS-112 历史快照)
      与其它章节一律不认 ⇒ 不会把历史对照表误当成现行提案。
    """
    txt = open(SPEC, encoding="utf-8").read()
    m = re.search(r"^###\s*5\.2(?![.\d]).*$", txt, re.M)
    if not m:
        return {}
    sec = txt[m.end():]
    nxt = re.search(r"^###\s", sec, re.M)
    if nxt:
        sec = sec[:nxt.start()]
    out = {}
    for line in sec.splitlines():
        if not line.startswith("|"):
            continue
        mm = re.match(r"^\|\s*\**\s*pin\s*(\d+)\s*\**\s*\|\s*\**\s*`([^`]+)`", line)
        if mm:
            out[int(mm.group(1))] = mm.group(2).strip()
    return out


def scan_p10json():
    if not os.path.exists(P10JSON):
        return None
    data = json.load(open(P10JSON, encoding="utf-8"))
    return [r for r in data if r.get("ref") == "U_CHG"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    hits = scan_netlist()
    spec = scan_spec()
    p10j = scan_p10json()

    # ---------- ① 24 脚表本身 ----------
    tbl = spec["table"]
    bad_tbl = []
    for pin, (name, typ, nets, _q) in PINMAP.items():
        got = tbl.get(pin)
        if got != name:
            bad_tbl.append(f"pin{pin}: 库内='{got}' 官方='{name}'")
    rec(not bad_tbl, "① §2.2 pinout 表 24 脚与 datasheet 一致",
        "全部 24 脚逐脚对齐" if not bad_tbl else "; ".join(bad_tbl))

    rec(spec["official_line_count"] >= 1, "①b 库内 '全 24 脚对照' 串存在且与官方一致",
        f"命中 {spec['official_line_count']} 处" if spec["official_line_count"] >= 1
        else "★库内找不到与官方一致的 '全 24 脚对照' 串")

    if p10j:
        ok_line = False
        bad_line = []
        for r in p10j:
            n = r.get("note") or ""
            if "全 24 脚对照" in n:
                ok_line = OFFICIAL_LINE in n
                if not ok_line:
                    bad_line.append(n[-160:])
        rec(ok_line, "①c 网表 P10 的 '全 24 脚对照' 串与官方一致",
            "一致" if ok_line else ("★不一致: " + (bad_line[0] if bad_line else "未找到该串")))

    # ---------- ② 网表引用逐条比对 ----------
    mismatch = []
    used = defaultdict(list)
    for h in hits:
        for p in h["pins"]:
            used[p].append(h)
            if p not in PINMAP:
                mismatch.append(f"第{h['line']}行: pin{p} 超出 1-24 范围")
                continue
            name, typ, nets, _q = PINMAP[p]
            if h["net"] not in nets:
                mismatch.append(
                    f"第{h['line']}行 [{h['page']}]: pin{p} ({name}) 挂在网 '{h['net']}' "
                    f"≠ 官方功能对应网 {sorted(nets)}")
    rec(not mismatch, "② netlist 里每条 'U_CHG pinN' 引用都符合官方功能",
        f"共核对 {len(hits)} 行 / {sum(len(h['pins']) for h in hits)} 个 pin 引用, 全对"
        if not mismatch else f"{len(mismatch)} 处错位: " + "; ".join(mismatch[:6]))

    # ---------- ③ 覆盖率 ----------
    missing = [p for p in range(1, 25) if p not in used]
    # 官方标了 NC 的脚, 不画也是合法的
    missing_real = [p for p in missing if PINMAP[p][0] != "NC"]
    rec(not missing_real, "③ 1-24 脚在网表里全部有引用 (无漏画)",
        "24 脚全部有引用" if not missing else
        f"未被网表引用: {missing} (其中官方 NC 脚可不画)")

    # ---------- ④ 越界 ----------
    oob = sorted({p for h in hits for p in h["pins"] if not (1 <= p <= 24)})
    rec(not oob, "④ 无越界引脚号 (pin0 / pin25+)", "无越界" if not oob else f"越界: {oob}")

    # ---------- ⑤ pin 唯一性 (CSV 层) ----------
    conflicts, where = scan_pin_uniqueness()
    uchg_conf = {k: v for k, v in conflicts.items() if k[0] == "U_CHG"}
    # ★★2026-11-02 03:0x 修规则: 本项目里**同一物理脚出现在多个网名是设计意图**, 不是 KiCad 冲突:
    #   pin4  (STAT) → {CHG_STAT, CHG_STAT_L}  (跨铰链主网 + 充电板本地段)
    #   pin17/18 (PGND) → {PGND, TS_RTN}        (TS 专用回流复用 PGND 脚)
    #   ⇒ 判据改成 **"落在 PINMAP 允许网集合内"**, 而不是"只能有一个网" (PINMAP 自己就写了多个允许名)。
    uchg_bad = []
    for k, nets in uchg_conf.items():
        allowed = set(PINMAP[int(k[1])][2]) if k[1].isdigit() and int(k[1]) in PINMAP else set()
        if not (allowed and set(nets) <= allowed):
            uchg_bad.append((k, nets, sorted(allowed)))
    rec(not uchg_bad, "⑤ 网表里 U_CHG 每个物理脚只出现在 PINMAP 允许的网集合内 (无 pin conflict)",
        "U_CHG 24 脚全部合规 (含设计意图的双名节点)" if not uchg_bad else
        "; ".join(f"pin{k[1]} 在 {nets} 超出允许集合 {al}" for k, nets, al in
                  sorted(uchg_bad, key=lambda x: int(x[0][1]))))

    # ---------- ⑥ 导出的 KiCad 网表里 U_CHG 脚的实际归属 ----------
    kx = scan_kicad_export()
    expect = {f"pin{p}": PINMAP[p][0] for p in range(1, 25)}
    wrong = []
    for p in range(1, 25):
        pin = f"pin{p}"
        nets = kx.get(pin, [])
        if not nets:
            wrong.append(f"{pin} ({expect[pin]}) 在导出网表里没有归属")
        elif p in (17, 18) and not ({"PGND", "TS_RTN"} & set(nets)):
            wrong.append(f"{pin} (PGND) 导出后落在 {nets} 而不是 PGND")
    rec(not wrong, "⑥ 导出的 netlist_v1.net 里 U_CHG 24 脚归属正确 (pin17/18 必须在 PGND/TS_RTN)",
        "24 脚全部正确" if not wrong else "; ".join(wrong))

    # ---------- ⑦ J_CHG 跨铰链 pin map 三方口径 ----------
    # ★★ISS-136 (2026-11-12) ★★ 这一段从"硬编快照 vs 网表"改成"**规格表实读 vs 网表**"。
    # ★**为什么**: 原来比较的是脚本里写死的 spec_proposal ⇒ 规格 §5.2 改坏了脚本也不会红
    #   ⇒ 门禁"一直是绿的假象" ⇒ 漂移被系统性放过。
    # ★**真源 = HW/netlist_v1.csv** (投板真源); 规格 §5.2 表必须是它的镜像。
    jmap = defaultdict(set)
    with open(NETLIST, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            for side in ("node1", "node2"):
                m = JCHG_RE.search(r.get(side) or "")
                if m:
                    jmap[int(m.group(1))].add(r.get("net", ""))
    # ★一个脚上挂多个网 = 真冲突 (旧代码 sorted(v)[0] 直接吞掉一个 ⇒ 又是假象)
    multi_net = {p: sorted(v) for p, v in sorted(jmap.items()) if len(v) > 1}
    rec(not multi_net, "⑦a J_CHG 每个脚只挂一个网 (无同脚多网冲突)",
        "10 脚各挂 1 个网" if not multi_net else
        "★同脚多网: " + "; ".join(f"pin{p}: {v}" for p, v in multi_net.items()))
    net_map = {p: sorted(v)[0] for p, v in sorted(jmap.items()) if v}
    # ★**规格表实读** (ISS-136: 这才是真判据 —— 以前这里根本不读规格)
    spec_tbl = scan_spec_jchg_pinmap()
    diff_spec = {p: (spec_tbl.get(p), net_map.get(p))
                 for p in sorted(set(spec_tbl) | set(net_map))
                 if spec_tbl.get(p) != net_map.get(p)}
    rec(not diff_spec, "⑦ J_CHG 跨铰链 pin map: 规格 §5.2 表 (实读) == 网表实际",
        "一致 (规格 §5.2 逐脚 = 网表)" if not diff_spec else
        "★不一致 (pin: 规格 §5.2 表 vs 网表实际) = " +
        "; ".join(f"pin{p}: {a} vs {b}" for p, (a, b) in diff_spec.items()))
    # ★脚本内快照 (spec_proposal) 与真源的同一口径校验: 快照不得比真源"更新"
    #   ⇒ 任何人改网表却不同步快照, 这里会红。
    spec_proposal = SPEC_PROPOSAL
    diff_snap = {p: (spec_proposal.get(p), net_map.get(p))
                 for p in sorted(set(spec_proposal) | set(net_map))
                 if spec_proposal.get(p) != net_map.get(p)}
    rec(not diff_snap, "⑦b J_CHG 跨铰链 pin map: 脚本内 spec_proposal 快照 == 网表实际",
        "快照与真源一致" if not diff_snap else
        "★不一致 (pin: 脚本快照 vs 网表实际) = " +
        "; ".join(f"pin{p}: {a} vs {b}" for p, (a, b) in diff_snap.items()))

    # ---------- 输出 ----------
    if args.json:
        print(json.dumps({"results": RESULTS,
                          "pin_hits": [{k: v for k, v in h.items() if k != "note"} for h in hits],
                          "j_chg_net": net_map, "j_chg_spec_proposal": spec_proposal,
                          "j_chg_spec_52_table": spec_tbl}, ensure_ascii=False, indent=2))
        return 0 if all(r["ok"] for r in RESULTS) else 1

    print("=" * 76)
    print("  BQ25896 24 脚 pinout 机械复核 (ISS-112 d)  ·  官方源: SLUSC76C §7")
    print("=" * 76)
    for r in RESULTS:
        print(f"  [{'PASS' if r['ok'] else 'FAIL'}] {r['name']}")
        if r["detail"]:
            print(f"         {r['detail']}")
    print("-" * 76)
    print(f"  网表里 U_CHG pin 引用共 {len(hits)} 行 / {sum(len(h['pins']) for h in hits)} 个 pin; "
          f"覆盖 {len(used)}/24 脚")
    if conflicts:
        print("  ── ★全网表 pin 冲突 (同一物理脚在多个网) ──")
        for (dev, p), nets in sorted(conflicts.items(), key=lambda x: (x[0][0], int(x[0][1]))):
            print(f"     {dev} pin{p}: {nets}   ← CSV 行 {','.join(str(x[0]) for x in where[(dev, p)])}")
    if kx:
        print("  ── 导出的 netlist_v1.net 里 U_CHG 脚归属 ──")
        for p in range(1, 25):
            pin = f"pin{p}"
            print(f"     {pin:>6} {expect[pin]:<5} → {kx.get(pin, ['(无归属)'])}")
    print("  ── 逐脚核对表 (官方 → 网表实际出现的网) ──")
    for p in range(1, 25):
        name, typ, nets, _q = PINMAP[p]
        got = sorted({h["net"] for h in used.get(p, [])})
        mark = "✓" if all(g in nets for g in got) else "✗"
        print(f"   {mark} pin{p:>2} {name:<5} 官方允许网 {sorted(nets)}  实际 {got if got else '—(未引用)'}")
    print("=" * 76)
    return 0 if all(r["ok"] for r in RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
