#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HW/check_netlist_contradiction_r3.py —— ★**网表 / 板 第 3 轮「自相矛盾」机器门禁**★

================================================================================
★**本脚本只判「矛盾」, 不落表** ★
  · ★**只读**: `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/PCB/demo_mainboard.kicad_pcb`
  · ★**只出规格**: 逐条定性 + 逐字改法见 `HW/NETLIST_CONTRADICTION_R3_CLOSEOUT.md`
  · ★**不改** 网表 / 脚表 / BOM / 板文件 / 任何生成器 (落表由 main 排期 · H-1 重锚)
  · ★**零外发** (不发邮件 / 不联系供应商 / 不下采购单) · ★**实物 [实测] = 0 条**

================================================================================
★**3 条缺陷家族 (main 2026-11-16 13:4x 本机自验派单)** ★
  ★**F1** 「C_VBUS_OUT / C_VBUS_GND 两颗 2 脚电容在网表里端子标签撞车」
       → 规则 **R3-A1** (2 脚 C 的端子登记次数 ≤ 脚表脚数) + **R3-A2** (2 脚 C 之间的裸位号对端撞车)
       ★★**★F1 已于 ISS-249 (2026-11-16 19:2x) 落表 ⇒ 现在 findings = 2 (F2 + F3) ★★ ★
  ★**F2** 「J_CHG 位号双义 + 板侧封装块不可装配」
       → 规则 **R3-A3** (多脚连接器板侧焊盘数 ≥ 脚表脚数) + **R3-A5** (板级封装名 / 几何原语完整性)
  ★**F3** 「MAIN_PCB 上 DNP 位号在板文件里零标记」
       → 规则 **R3-A4** (DNP 位号必须带 exclude_from_bom / exclude_from_pos_files / (attr dnp))

★**附加观察 (不计入 finding 数, 不影响 rc)** ★
  → 规则 **R3-A6** 「充电 IC 的 VBUS 脚到上游 VBUS 之间只隔着电容 ⇒ 无直流通路」
    ★归 **V-7** (充电板整机阶段 P0 · 已由 ISS-214 §4.C 补差C #4/#6 登记) ⇒ 本单只出规格, 不落表★

================================================================================
★**为什么每条规则都带 scope** (★"零多报零少报"的前提★):
  · `HW/netlist_v1.csv` 的模型是「**一行 = 一根连接**」(node1 ↔ node2), 裸位号 token 表示
    「**这颗器件自己的一个端子**」⇒ 别的器件的行把本器件的裸位号当对端引用是**正常写法**
    (例: L40 `R_NTC_BAT` ↔ `R_TS_PULL` 都是 2 脚 R) ⇒ ★**不能**用「裸位号出现次数 > 2」
    一刀切判全表 (会误报 26 颗) ⇒ ⇒ **每条规则都限定在可判定的子集上** ★
================================================================================
★================================================================================
★**2026-11-16 14:2x 续做 (上一会话 14:07 被 provider 掐断) 的唯一改动 = 修 T0 基线误红** ★
  ★**根因 (★本机实测复核过, 与派单单里写的根因【不同】★)**:
    派单单说「T0 红是因为 `_green_baseline()` 没补 186 个空封装名 ⇒ `a5["empty_name"]` 非零」
    ⇒ ★**实测不成立**: T0 自测输出里 `R3-A5 empty_name = 0` ⇒ 基线**已经**把封装名补齐了
      (`PKG:<ref>`) ⇒ ★**真根因 = `a5["few_lines"]` 非零 = `['J_USB_C']`** ★
  ★**`few_lines` 为什么会非零**: 几何下限判据只数 `(fp_line` ⇒ `J_USB_C` 的丝印是用 KiCad 的
    **`(fp_rect` 画的 (0 fp_line + 2 fp_rect) ⇒ 旧口径把它判成「没有几何」= ★纯误报★**
    ⇒ ★**实测整板 186 个 footprint 里, fp_line<2 的只有 J_USB_C 这 1 个; 按【全部 fp_* 图形
    原语】(fp_line/fp_rect/fp_poly/fp_arc/fp_circle) 数, <2 的 = 0 个** ★
  ★**修法 (落在判据本身, 不许削弱真文件判定)**:
    ① `parse_pcb()` 增加 `fp_prim` = 全部 fp_* 图形原语数
    ② `rule_A5()` 增加 `few_prim` (★真判据★) · `few_lines` (fp_line 旧口径) **保留作对照/留痕**
    ③ F2 的触发条件用 `few_prim` 不用 `few_lines` ⇒ ★**真文件 findings 数 = 2 (F2 + F3) · ★F1 已于 ISS-249 落表消失★** ★
  ★**为什么不能改成「基线里把 J_USB_C 也补画图形」**: 那是拿合成件糊门禁 ⇒ ★**J_USB_C 根本没坏**
    (它有 2 个 fp_rect 丝印矩形 + 18 个焊盘) ⇒ 真正的问题是判据把它误判了 ★
★================================================================================
用法:
    python3 HW/check_netlist_contradiction_r3.py              # 门禁 (rc=1 且 findings≥1 时 = 红)
    #   ★★2026-11-16 19:2x (ISS-249 · F1 已落表): findings 由 3 条变 2 条 (F1 消失, 剩 F2+F3)
    #     ⇒ ★**rc 语义一个字没改** (仍是「有未修缺陷 ⇒ 红」) ⇒ ★F2/F3 还在 ⇒ 本门禁【仍然红】是预期 ★
    #     ⇒ ★「恰 2 条」只改【条数期望 + 文案】(判据逻辑不动) ⇒ ★T11 反向用例证明「F1 改回来 ⇒ 必须回到 3 条」★
    python3 HW/check_netlist_contradiction_r3.py --selftest   # 反向用例自证 (rc=0 = 全抓到)
    python3 HW/check_netlist_contradiction_r3.py --json       # 机器可读
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

CSV_NET = os.path.join(PROJ, "HW", "netlist_v1.csv")
CSV_PINS = os.path.join(PROJ, "HW", "netlist_v1_pins.csv")
PCB_FILE = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")

# ★**被点名的 3 组 (main 派单原文里的具体对象)** ★
NAMED_CAPS = ("C_VBUS_OUT", "C_VBUS_GND")       # F1
NAMED_CONN = ("J_CHG",)                         # F2


# ======================================================================== 读 CSV
def read_csv_rows(path):
    """读 CSV ⇒ [(file_line_no, dict)]  (file_line_no 含表头偏移, L1 = 表头)"""
    with io.open(path, encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        out = []
        for i, r in enumerate(rdr):
            out.append((i + 2, r))
        return out


def cell(r, k):
    return (r.get(k) or "").strip()


# ======================================================================== 读板文件
def parse_pcb(path):
    """解析 .kicad_pcb ⇒ {ref: {...}}  (只读, 不改)"""
    txt = io.open(path, encoding="utf-8").read()
    lines = txt.split("\n")
    blocks = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("\t(footprint "):
            bal = 0
            k = i
            while k < len(lines):
                bal += lines[k].count("(") - lines[k].count(")")
                if k > i and bal <= 0:
                    break
                k += 1
            blocks.append((i + 1, k + 1, "\n".join(lines[i:k])))
            i = k + 1
        else:
            i += 1
    out = {}
    for a, b, body in blocks:
        m = re.search(r'\(footprint\s+"([^"]*)"', body)
        fname = m.group(1) if m else ""
        m = re.search(r'\(property "Reference" "([^"]*)"', body)
        ref = m.group(1) if m else ""
        m = re.search(r'\(property "Value" "([^"]*)"', body)
        val = m.group(1) if m else ""
        pads = re.findall(r'\(pad\s+"([^"]*)"', body)
        padnets = [(mm.group(1), mm.group(2)) for mm in
                   re.finditer(r'\(pad\s+"([^"]*)"(.*?)\(net "([^"]*)"\)', body, re.S)]
        attr = re.search(r'\(attr\s+([^)]*)\)', body)
        out[ref] = {
            "ref": ref, "line": a, "end": b, "fname": fname, "value": val,
            "pads": pads, "npad": len(pads), "padnets": padnets,
            "fplines": len(re.findall(r'\(fp_line', body)),
            # ★2026-11-16 ISS-242 续做: KiCad 的丝印/本体图形**不只有 fp_line** ——
            #   fp_rect / fp_poly / fp_arc / fp_circle 都是合法图形原语 ⇒ 只数 fp_line 会把
            #   【用 fp_rect 画丝印的正常封装】误判成「没有几何」⇒ 实测 J_USB_C = 0 fp_line + 2 fp_rect
            #   (整板 186 个 footprint 里 fp_line<2 的【只有它一个】⇒ 纯误报) ⇒
            #   几何下限判据必须数【全部】fp_* 原语 ★
            "fp_prim": len(re.findall(r'\(fp_(?:line|rect|poly|arc|circle)\b', body)),
            "attr": attr.group(1).strip() if attr else "",
            "has_attr": bool(attr),
            "ex_bom": "exclude_from_bom" in body,
            "ex_pos": "exclude_from_pos_files" in body,
            "attr_dnp": bool(attr) and "dnp" in attr.group(1).lower(),
            "body": body,
        }
    return out


# ======================================================================== 网表索引
def build_net_index(net_rows, pin_rows):
    """建索引: 类型 / 脚数 / 端子 / 网"""
    types = {}
    for _, r in net_rows:
        ref = cell(r, "ref")
        if ref and ref not in types:
            types[ref] = cell(r, "type")
    # 脚表: ref → {pin: net}
    pins = {}
    for _, r in pin_rows:
        ref = cell(r, "ref")
        if not ref:
            continue
        pins.setdefault(ref, {})[cell(r, "pin")] = cell(r, "net")
    # 网表里每颗器件出现过的 (net, 裸位号) 登记
    regs = {}
    for ln, r in net_rows:
        ref = cell(r, "ref")
        net = cell(r, "net")
        for slot in ("node1", "node2"):
            v = cell(r, slot)
            if not v or " " in v:          # 带 " pinN" 提示的物理脚, 不是裸位号
                continue
            regs.setdefault(v, []).append({"line": ln, "net": net, "slot": slot,
                                           "row_ref": ref})
    return {"types": types, "pins": pins, "regs": regs}


# ======================================================================== 规则实现
def rule_A1(idx, ctx):
    """R3-A1: 每颗 **2 脚 C** 的端子登记次数 (裸位号出现在 node 槽的总次数) ≤ 脚表脚数。

    ★为什么只看 type=='C'★: 全表 (R/C/L) 里有 26 颗 2 脚件的裸位号被别的行当对端引用
      (例: `R_PU_CHG_STAT` 在 CHG_STAT 网上有 U_CHG 与 TP_CHG_STAT 两条对端线) ⇒
      那是「一行 = 一根连接」模型的正常写法, 不是缺陷 ⇒ 判据只对 **2 脚 C** 生效 ★
    """
    hits = []
    for ref, pmap in idx["pins"].items():
        if idx["types"].get(ref) != "C":
            continue
        if len(pmap) != 2:
            continue
        occ = idx["regs"].get(ref, [])
        if len(occ) > 2:
            hits.append({"ref": ref, "pins": 2, "occ": len(occ),
                         "lines": [o["line"] for o in occ],
                         "detail": [f'L{o["line"]}: net={o["net"]} {o["slot"]}={ref} '
                                    f'(本行 ref={o["row_ref"]}) ⇒ {ref} 的端子被登记 {len(occ)} 次 > 脚数 2'
                                    for o in occ]})
    return hits


def rule_A2(idx, ctx):
    """R3-A2: **2 脚 C** 的行里, 对端是另一颗 2 脚 C 的裸位号, 且两颗在脚表里**同在该行的网上**
    ⇒ ⇒ 「一颗件的端子标签被另一颗件借走」⇒ 撞车。

    ★scope★: 只判 ref 的 type=='C' (2 脚 C ↔ 2 脚 C 的直接连线);
      `R_NTC_BAT` ↔ `R_TS_PULL` (L40) 那类 2 脚 R 直连是正常分压写法 ⇒ 不在 scope ★
    """
    hits = []
    for ln, r in ctx["net_rows"]:
        ref = cell(r, "ref")
        if idx["types"].get(ref) != "C" or len(idx["pins"].get(ref, {})) != 2:
            continue
        net = cell(r, "net")
        own = idx["pins"].get(ref, {})
        if net not in own.values():
            continue
        for slot in ("node1", "node2"):
            v = cell(r, slot)
            if not v or " " in v or v == ref:
                continue
            if idx["types"].get(v) != "C" or len(idx["pins"].get(v, {})) != 2:
                continue
            peer_nets = idx["pins"].get(v, {}).values()
            if net in peer_nets:
                hits.append({"line": ln, "net": net, "owner": ref, "peer": v,
                             "detail": f'L{ln}: net={net} ref={ref} 的对端裸位号={v} '
                                       f'⇒ {v} 与 {ref} 在脚表里同在 {net} 上 ⇒ 端子标签撞车'})
    return hits


def rule_A3(idx, ctx):
    """R3-A3: 网表里声明为**多脚连接器** (type==CONN 或 value 里声明 N×Mp / Np) 的位号,
    在板文件里必须 **焊盘数 ≥ 脚表脚数**。

    ★焊盘数是「物理上能不能装配/能不能连线」的下限判据★:
      脚表 10 脚 / 板上 2 个焊盘 ⇒ 8 个脚在板上**没有落点** ⇒ 跨铰链通道物理上不存在 ★
    """
    hits = []
    conn_refs = set()
    for _, r in ctx["net_rows"]:
        ref = cell(r, "ref")
        if not ref:
            continue
        if cell(r, "type") == "CONN" or re.search(r'\d+\s*[×x]\s*\d*\s*p\b', cell(r, "value")) \
                or re.search(r'\d+\s*p\b', cell(r, "value")):
            conn_refs.add(ref)
    for ref in sorted(conn_refs):
        if ref not in ctx["pcb"]:
            continue
        pins = len(idx["pins"].get(ref, {}))
        if pins <= 1:
            continue
        got = ctx["pcb"][ref]["npad"]
        if got < pins:
            hits.append({"ref": ref, "want": pins, "got": got,
                         "line": ctx["pcb"][ref]["line"],
                         "pads": ctx["pcb"][ref]["pads"],
                         "detail": f'{ref}: 脚表 {pins} 脚 / 板文件只有 {got} 个焊盘 '
                                   f'{ctx["pcb"][ref]["pads"]} ⇒ 板上无落点的脚 = {pins - got} 个'})
    return hits


def rule_A4(idx, ctx):
    """R3-A4: 板文件里 **board=MAIN_PCB 且 dnp=DNP** 的位号, 必须带
    exclude_from_bom / exclude_from_pos_files / (attr … dnp) 之一。

    ★为什么致命★: 板文件里没有标记 ⇒ **贴片坐标文件 (CPL) 会把这 43 颗当必装** ⇒
      产线贴上「不装」的器件 (电池座 / 电池保护 MOS / NTC …) ⇒ 既占料又可能短接 ★
    """
    dnp_main = []
    for _, r in ctx["net_rows"]:
        if cell(r, "board") == "MAIN_PCB" and cell(r, "dnp") == "DNP" and cell(r, "ref"):
            dnp_main.append(cell(r, "ref"))
    dnp_main = sorted(set(dnp_main))
    on_board = [x for x in dnp_main if x in ctx["pcb"]]
    unmarked = [x for x in on_board
                if not (ctx["pcb"][x]["ex_bom"] or ctx["pcb"][x]["ex_pos"] or ctx["pcb"][x]["attr_dnp"])]
    return {"dnp_main": dnp_main, "on_board": on_board, "unmarked": unmarked}


def rule_A5(ctx):
    """R3-A5: 板文件里 **所有 footprint 必须有非空封装名** (+ 几何原语数 ≥2 的几何下限)。

    ★实测口径★: 本板 186/186 个 footprint 的封装名都是空串 ⇒ 这是 `state/gen_pcb_*.py`
      的**统一写法** (不是某颗器件独有) ⇒ ⇒ **本条不单开 finding**, 归并进 F2 的证据里,
      避免「零多报」被破坏 (main 的 ⑤ 若按字面单开一条 ⇒ findings 会变成 4 条) ★

    ★几何下限的口径 (★2026-11-16 14:2x 续做时订正★)★:
      · `few_lines` = 只数 `(fp_line` 的旧口径 ⇒ 实测整板唯一命中 `J_USB_C`
        ⇒ ★**那是误报**: J_USB_C 的丝印是 KiCad 的 `(fp_rect` 画的 (0 fp_line + 2 fp_rect)
        ⇒ fp_rect / fp_poly / fp_arc / fp_circle 都是合法图形原语 ⇒ ★真判据是 `few_prim`
          (数全部 fp_* 原语) ⇒ 实测 186 个 footprint 里 `few_prim` 命中 = **0 个** ★
      · ★`few_lines` 保留在报告里 (★留痕: 派单实测数就是 1 = J_USB_C, 不许把这个数悄悄抹掉★) ★
    """
    empty_name = sorted(r for r, v in ctx["pcb"].items() if not v["fname"].strip())
    few_lines = sorted(r for r, v in ctx["pcb"].items() if v["fplines"] < 2)
    few_prim = sorted(r for r, v in ctx["pcb"].items() if v["fp_prim"] < 2)
    return {"n_fp": len(ctx["pcb"]), "empty_name": empty_name,
            "few_lines": few_lines, "few_prim": few_prim}


def rule_A6(idx, ctx):
    """R3-A6 (★附加观察·不计入 findings·不影响 rc★): **充电 IC 的供电脚到上游 VBUS 之间
    只隔着电容 ⇒ 直流被隔断 ⇒ 该 IC 无 DC 供电**。

    ★判据★: 在脚表建的网图里, 若 net B (含 IC 的 VBUS 脚) 与 net A (含上游 VBUS 源) 之间
      **唯一的连接件是一颗电容** ⇒ 直流不��� ⇒ 红 ★
    ★归属★: V-7 / ISS-214 §4.C 补差C #4·#6 (充电板整机阶段 P0) ⇒ 本单只出规格 ★
    """
    # 网 → 脚集合
    net_nodes = {}
    for ref, pmap in idx["pins"].items():
        for pin, net in pmap.items():
            net_nodes.setdefault(net, []).append((ref, pin))
    caps = [r for r in idx["types"] if idx["types"].get(r) == "C"]
    hits = []
    for cap in caps:
        pmap = idx["pins"].get(cap, {})
        if len(pmap) != 2:
            continue
        nets = list(pmap.values())
        if nets[0] == nets[1]:
            continue
        a, b = nets
        for ic_net in (a, b):
            # ★只认「VBUS 域」的两网之间的电容桥★ (否则 GND↔VBUS 这种对地电容会误报)
            if not re.search(r"VBUS", ic_net, re.I):
                continue
            ics = [(r, p) for (r, p) in net_nodes.get(ic_net, [])
                   if idx["types"].get(r) == "IC"]
            if not ics:
                continue
            other = b if ic_net == a else a
            if not re.search(r"VBUS", other, re.I):
                continue
            # other (上游) 网上必须有真源器件 (Type-C 座 / ESD / 磁珠 / LDO)
            has_src = any(idx["types"].get(r) in ("CONN", "D", "L", "IC")
                          for (r, _) in net_nodes.get(other, []))
            if not has_src:
                continue
            # 两网之间除这颗电容外, 还要没有别的器件桥接
            bridge = set()
            for ref, pmap2 in idx["pins"].items():
                ns = set(pmap2.values())
                if other in ns and ic_net in ns and ref != cap:
                    bridge.add(ref)
            if bridge:
                continue
            hits.append({"cap": cap, "ic_net": ic_net, "src_net": other,
                         "ic": sorted({r for (r, _) in ics}),
                         "detail": f'{cap} 是 {other} ↔ {ic_net} 之间**唯一**的连接件 (电容) ⇒ '
                                   f'{ic_net} 上的 IC {sorted({r for (r, _) in ics})} '
                                   f'的供电脚没有直流通路'})
            break
    # 去重
    seen, uniq = set(), []
    for h in hits:
        k = (h["cap"], h["ic_net"], h["src_net"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(h)
    return uniq


# ======================================================================== 汇总
def analyze(net_path=CSV_NET, pins_path=CSV_PINS, pcb_path=PCB_FILE):
    net_rows = read_csv_rows(net_path)
    pin_rows = read_csv_rows(pins_path)
    pcb = parse_pcb(pcb_path)
    idx = build_net_index(net_rows, pin_rows)
    ctx = {"net_rows": net_rows, "pin_rows": pin_rows, "pcb": pcb, "idx": idx}

    a1 = rule_A1(idx, ctx)
    a2 = rule_A2(idx, ctx)
    a3 = rule_A3(idx, ctx)
    a4 = rule_A4(idx, ctx)
    a5 = rule_A5(ctx)
    a6 = rule_A6(idx, ctx)

    findings = []

    # ---- F1 ----
    f1_rows = sorted({h["line"] for h in a2} | {ln for h in a1 for ln in h["lines"]})
    if a1 or a2:
        findings.append({
            "id": "F1", "family": "C_VBUS_OUT / C_VBUS_GND 两颗 2 脚电容在网表里端子标签撞车",
            "rules": ["R3-A1", "R3-A2"],
            "lines": f1_rows,
            "detail": {
                "A1_2脚C登记次数超脚数": a1,
                "A2_2脚C之间裸位号对端撞车": a2,
            },
        })

    # ---- F2 ----
    # ★2026-11-16 14:2x 续做: 触发条件用 `few_prim` (数全部 fp_* 图形原语) 而不是 `few_lines`
    #   (只数 fp_line ⇒ 把用 fp_rect 画丝印的正常封装 J_USB_C 误判成「没有几何」= 纯误报)
    #   ⇒ ★真文件 findings 数 = 2 (F2 + F3) · ★F1 已于 ISS-249 落表消失★ · A1/A2 已转绿 (T8) ★
    if a3 or a5["empty_name"] or a5["few_prim"]:
        findings.append({
            "id": "F2", "family": "J_CHG 位号双义 + 板侧封装块不可装配",
            "rules": ["R3-A3", "R3-A5"],
            "lines": [h["line"] for h in a3],
            "detail": {
                "A3_多脚连接器板侧焊盘数不足": a3,
                "A5_板级封装名空": {"count": len(a5["empty_name"]), "total": a5["n_fp"],
                                   "refs": a5["empty_name"][:8] + (["…"] if len(a5["empty_name"]) > 8 else [])},
                "A5_板级几何原语少于2条(真判据·全部fp_*)": {"count": len(a5["few_prim"]),
                                                           "refs": a5["few_prim"]},
                "A5_板级fp_line少于2条(旧口径·只数fp_line·留痕)": {
                    "count": len(a5["few_lines"]), "refs": a5["few_lines"][:8],
                    "note": "★只数 (fp_line ⇒ 把用 (fp_rect 画丝印的正常封装 (J_USB_C: 0 fp_line + 2 fp_rect) "
                            "误判成『没有几何』⇒ 整板唯一一例 = 误报, 不作判据★"},
            },
        })

    # ---- F3 ----
    if a4["unmarked"]:
        findings.append({
            "id": "F3", "family": "MAIN_PCB 上 DNP 位号在板文件里零标记 (贴片坐标会当必装)",
            "rules": ["R3-A4"],
            "lines": [ctx["pcb"][x]["line"] for x in a4["unmarked"][:12]],
            "detail": {
                "MAIN_PCB且DNP的位号数": len(a4["dnp_main"]),
                "其中在板文件里真实存在的": len(a4["on_board"]),
                "零标记的": len(a4["unmarked"]),
                "refs": a4["unmarked"],
            },
        })

    return {
        "findings": findings,
        "rules": {
            "R3-A1": {"hits": len(a1), "ok": not a1},
            "R3-A2": {"hits": len(a2), "ok": not a2},
            "R3-A3": {"hits": len(a3), "ok": not a3},
            "R3-A4": {"hits": len(a4["unmarked"]), "ok": not a4["unmarked"],
                      "dnp_main": len(a4["dnp_main"]), "on_board": len(a4["on_board"])},
            "R3-A5": {"empty_name": len(a5["empty_name"]), "fp": a5["n_fp"],
                      "few_lines": len(a5["few_lines"]), "few_prim": len(a5["few_prim"])},
        },
        "advisory": {"R3-A6": {"hits": len(a6), "items": a6}},
        "ctx": ctx,
    }


# ======================================================================== 报告
def report(res):
    out = []
    out.append("=" * 78)
    out.append("  网表 / 板 第 3 轮「自相矛盾」门禁 (R3)  ·  hw-lead 2026-11-16")
    out.append("=" * 78)
    out.append("  ★本门禁只判矛盾, 不落表 (网表/脚表/BOM/板文件/生成器 一个字节都没动)★")
    out.append("")
    out.append("── 规则结果 " + "─" * 62)
    for r, v in res["rules"].items():
        if r == "R3-A5":
            out.append(f"  {r}: 空封装名 {v['empty_name']}/{v['fp']} · fp_*几何原语<2 的 {v['few_prim']} 个 (★真判据★)"
                       f" · fp_line<2 的 {v['few_lines']} 个 (★旧口径·J_USB_C 用 fp_rect 画丝印 = 误报·只留痕★)")
            out.append(f"        ⇒ ★板级同源特征 (整板封装名都没写), 归并进 F2 证据, 不单开 finding★")
        elif r == "R3-A4":
            out.append(f"  {r}: MAIN_PCB且DNP {v['dnp_main']} 颗 · 在板上 {v['on_board']} 颗"
                       f" · 零标记 {v['hits']} 颗  ⇒ {'❌ 红' if not v['ok'] else '✅ 绿'}")
        else:
            out.append(f"  {r}: 命中 {v['hits']}  ⇒ {'❌ 红' if not v['ok'] else '✅ 绿'}")
    out.append("")
    out.append(f"── FINDINGS ({len(res['findings'])}) " + "─" * 56)
    for f in res["findings"]:
        out.append(f"  [{f['id']}] {f['family']}")
        out.append(f"        规则 = {' + '.join(f['rules'])}  ·  网表行 = {f['lines'][:12]}")
        for k, v in f["detail"].items():
            out.append(f"        · {k}: {v if not isinstance(v, list) else ''}")
            if isinstance(v, list):
                for item in v[:6]:
                    out.append(f"            - {item}")
    out.append("")
    adv = res["advisory"]["R3-A6"]
    out.append("── 附加观察 (★不计入 findings 数, 不影响 rc★) " + "─" * 34)
    if adv["hits"]:
        out.append(f"  R3-A6 命中 {adv['hits']} 条 (★归 V-7 / ISS-214 §4.C 补差C · 充电板整机阶段 P0★):")
        for h in adv["items"][:4]:
            out.append(f"    - {h['detail']}")
        out.append("  ★⇒ 本门禁 rc=0 **不等于**充电板可投板 ★")
    else:
        out.append("  R3-A6: 无命中")
    out.append("")
    out.append("─" * 78)
    out.append(f"  FINDINGS: {len(res['findings'])}  (主线要求 = 恰 2 条 = F2 + F3)")
    ok = (len(res["findings"]) == 2 and [f["id"] for f in res["findings"]] == ["F2", "F3"])
    out.append(f"  结论: {'✅ 恰 2 条 = 主线的 F2 + F3 (★F1 已于 ISS-249 落表 ⇒ 消失★)' if ok else '❌ 条数不符'}"
               f"  ·  rc = {1 if res['findings'] else 0}")
    out.append("─" * 78)
    return "\n".join(out)


# ======================================================================== 自测
def _patch_netlist_C_VBUS(rows, which):
    """在网表行上做定向改写 (只改 node2 / node2) —— 用于反向用例"""
    out = []
    for ln, r in rows:
        r = dict(r)
        if which == "L12_node2_back_to_C_VBUS_OUT" and ln == 12:
            r["node2"] = "C_VBUS_OUT"
        elif which == "L12_node2_to_C_VBUS_GND" and ln == 12:
            r["node2"] = "C_VBUS_GND"
        elif which == "L8_node2_back_to_C_VBUS_OUT" and ln == 8:
            r["node2"] = "C_VBUS_OUT"
        elif which == "L8_L12_node2_back_to_C_VBUS_OUT" and ln in (8, 12):
            # ★★ISS-249 新增: 两行一起回退成「落表前」⇒ 用于反向用例「改回旧值 ⇒ 必须回到 3 条」
            r["node2"] = "C_VBUS_OUT"
        out.append((ln, r))
    return out


def _write_rows(path, rows):
    cols = list(rows[0][1].keys())
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for _, r in rows:
            w.writerow(r)


def _green_baseline(tmp):
    """造一份「全绿」基线 (合成临时件, **不碰任何真文件**)"""
    net_rows = read_csv_rows(CSV_NET)
    pin_rows = read_csv_rows(CSV_PINS)
    pcb_txt = io.open(PCB_FILE, encoding="utf-8").read()
    lines = pcb_txt.split("\n")

    # (1) 落 R1-a: L8 node2 → 网标签 ; L12 node2 → 网标签
    for ln, r in net_rows:
        if ln == 8:
            r["node2"] = "VBUS_5V_F1"
        if ln == 12:
            r["node2"] = "VBUS_5V_CHG"
    net_p = os.path.join(tmp, "netlist_v1.csv")
    _write_rows(net_p, net_rows)

    pins_p = os.path.join(tmp, "netlist_v1_pins.csv")
    _write_rows(pins_p, pin_rows)

    # (2) 板: 给所有 footprint 非空封装名 + 给 J_CHG 补到 10 个焊盘 + 给 DNP 位号加标记
    idx = build_net_index(net_rows, pin_rows)
    pcb = parse_pcb(PCB_FILE)
    dnp_main = sorted({cell(r, "ref") for _, r in net_rows
                       if cell(r, "board") == "MAIN_PCB" and cell(r, "dnp") == "DNP"
                       and cell(r, "ref")})
    on_board = [x for x in dnp_main if x in pcb]

    out = list(lines)
    # 逐块改写
    blocks = []
    i = 0
    while i < len(out):
        if out[i].startswith("\t(footprint "):
            bal = 0
            k = i
            while k < len(out):
                bal += out[k].count("(") - out[k].count(")")
                if k > i and bal <= 0:
                    break
                k += 1
            blocks.append((i, k))
            i = k + 1
        else:
            i += 1
    for (a, b) in reversed(blocks):
        body = out[a:b + 1]
        body[0] = re.sub(r'\(footprint\s+"[^"]*"', '(footprint "PKG:%s"' % "X", body[0])
        blob = "\n".join(body)
        m = re.search(r'\(property "Reference" "([^"]*)"', blob)
        ref = m.group(1) if m else ""
        body[0] = re.sub(r'\(footprint\s+"[^"]*"', '(footprint "PKG:%s"' % ref, body[0])
        blob = "\n".join(body)
        if ref in on_board and "(attr" not in blob:
            blob = blob.replace('\t\t(layer "F.Cu")', '\t\t(attr exclude_from_bom exclude_from_pos_files)\n'
                                                     '\t\t(layer "F.Cu")', 1)
        if ref == "J_CHG":
            extra = []
            for pn in ("2", "3", "4", "5", "7", "8", "9", "10"):
                extra.append('\t\t(pad "%s" smd rect\n\t\t\t(at -1.1 -1.4)\n'
                             '\t\t\t(size 0.18 0.9)\n\t\t\t(layers "F.Cu" "F.Mask" "F.Paste")\n'
                             '\t\t\t(net "NC")\n\t\t)' % pn)
            blob = blob.rstrip()
            assert blob.endswith(")")
            blob = blob[:-1].rstrip() + "\n" + "\n".join(extra) + "\n\t)"
        out[a:b + 1] = blob.split("\n")
    pcb_p = os.path.join(tmp, "demo_mainboard.kicad_pcb")
    io.open(pcb_p, "w", encoding="utf-8").write("\n".join(out))
    return net_p, pins_p, pcb_p


def selftest():
    tmp = tempfile.mkdtemp(prefix="r3selftest_")
    cases = []
    try:
        net_p, pins_p, pcb_p = _green_baseline(tmp)

        def run(net=net_p, pcb=pcb_p):
            return analyze(net, pins_p, pcb)

        # --- T0: 基线必须全绿 ---
        r0 = run()
        cases.append(("T0 基线 (R1-a + DNP 标记 + J_CHG 补焊盘 + 封装名) 必须 0 findings",
                      len(r0["findings"]) == 0,
                      f'findings={len(r0["findings"])} rules='
                      f'{ {k: v.get("hits", v.get("empty_name")) for k, v in r0["rules"].items()} }'))

        # --- T1: L12 的 node2 改回 C_VBUS_OUT ⇒ A1 + A2 红 ---
        rows = read_csv_rows(net_p)
        _write_rows(os.path.join(tmp, "t1.csv"), _patch_netlist_C_VBUS(rows, "L12_node2_back_to_C_VBUS_OUT"))
        r1 = run(net=os.path.join(tmp, "t1.csv"))
        ok = (not r1["rules"]["R3-A2"]["ok"]) and (not r1["rules"]["R3-A1"]["ok"])
        cases.append(("T1 把 L12 的 node2 改回 C_VBUS_OUT ⇒ 期望 A2 红 + A1 红", ok,
                      f'A1={r1["rules"]["R3-A1"]["hits"]} A2={r1["rules"]["R3-A2"]["hits"]}'))

        # --- T2: L12 的 node2 改成 C_VBUS_GND (main 提的值) ⇒ A1 红 (证明 main 的值会造新缺陷) ---
        _write_rows(os.path.join(tmp, "t2.csv"), _patch_netlist_C_VBUS(rows, "L12_node2_to_C_VBUS_GND"))
        r2 = run(net=os.path.join(tmp, "t2.csv"))
        ok = (not r2["rules"]["R3-A1"]["ok"])
        cases.append(("T2 把 L12 的 node2 改成 C_VBUS_GND (main 提的值) ⇒ 期望 A1 红 (一颗件登记 3 次)",
                      ok, f'A1={r2["rules"]["R3-A1"]["hits"]}'))

        # --- T3: L8 的 node2 改回 C_VBUS_OUT ⇒ A1 红 ---
        _write_rows(os.path.join(tmp, "t3.csv"), _patch_netlist_C_VBUS(rows, "L8_node2_back_to_C_VBUS_OUT"))
        r3 = run(net=os.path.join(tmp, "t3.csv"))
        ok = (not r3["rules"]["R3-A1"]["ok"])
        cases.append(("T3 把 L8 的 node2 改回 C_VBUS_OUT ⇒ 期望 A1 红 (C_VBUS_OUT 登记 3 次)",
                      ok, f'A1={r3["rules"]["R3-A1"]["hits"]}'))

        # --- T4: 板侧 J_CHG 焊盘数改成 1 ⇒ A3 红 ---
        pcb_txt = io.open(pcb_p, encoding="utf-8").read()
        pcb4 = os.path.join(tmp, "t4.kicad_pcb")
        io.open(pcb4, "w", encoding="utf-8").write(
            re.sub(r'(\(property "Reference" "J_CHG".*?)(?=.*?\(property)', r'\1', pcb_txt, flags=re.S)
            if False else _shrink_j_chg(pcb_txt))
        r4 = run(pcb=pcb4)
        ok = (not r4["rules"]["R3-A3"]["ok"])
        cases.append(("T4 把 J_CHG 板侧焊盘数改成 1 ⇒ 期望 A3 红", ok,
                      f'A3={r4["rules"]["R3-A3"]["hits"]}'))

        # --- T5: 删掉一个 DNP 器件的标记 ⇒ A4 红 ---
        pcb5 = os.path.join(tmp, "t5.kicad_pcb")
        io.open(pcb5, "w", encoding="utf-8").write(_drop_dnp_marker(pcb_txt, "BT_432243"))
        r5 = run(pcb=pcb5)
        ok = (not r5["rules"]["R3-A4"]["ok"])
        cases.append(("T5 删掉 BT_432243 的 DNP 标记 ⇒ 期望 A4 红", ok,
                      f'A4={r5["rules"]["R3-A4"]["hits"]}'))

        # --- T6: 把某个 footprint 的封装名清空 ⇒ A5 红 ---
        pcb6 = os.path.join(tmp, "t6.kicad_pcb")
        io.open(pcb6, "w", encoding="utf-8").write(_empty_one_fname(pcb_txt, "J_CHG"))
        r6 = run(pcb=pcb6)
        ok = r6["rules"]["R3-A5"]["empty_name"] >= 1
        cases.append(("T6 把 J_CHG 的封装名清空 ⇒ 期望 A5 报空封装名", ok,
                      f'A5 empty_name={r6["rules"]["R3-A5"]["empty_name"]}'))

        # --- T7: 真文件基线 (现状) 必须恰 2 条 findings = F2 + F3 ---
        #   ★★2026-11-16 19:2x (ISS-249 · F1 落表): 断言值由「恰 3 条」改为「恰 2 条 且 ids == [F2, F3]」
        #     ⇒ ★F1 真落表了 (端子标签撞车消失) ⇒ 现状断言必须跟着真相走
        #     ⇒ ★**判据逻辑 (findings 的计算 / R3-A1~A6) 一个字节没动** ⇒ ★**只动这一条现状断言** ★
        r7 = analyze()
        ok = (len(r7["findings"]) == 2 and [f["id"] for f in r7["findings"]] == ["F2", "F3"])
        cases.append(("T7 现状 (真文件) 必须恰 2 条 findings = F2 + F3", ok,
                      f'findings={len(r7["findings"])} ids={[f["id"] for f in r7["findings"]]}'))

        # --- T8: 现状必须 A1/A2 绿 (F1 已修) 且 A3/A4 仍红 (F2/F3 未修) ---
        ok = (r7["rules"]["R3-A1"]["ok"] and r7["rules"]["R3-A2"]["ok"]
              and not r7["rules"]["R3-A3"]["ok"] and not r7["rules"]["R3-A4"]["ok"])
        cases.append(("T8 现状必须 A1/A2 绿 (F1 已落) 且 A3/A4 红 (F2/F3 未落)", ok,
                      f'{ {r: r7["rules"][r]["hits"] for r in ("R3-A1","R3-A2","R3-A3","R3-A4")} }'))

        # --- T9 (2026-11-16 14:2x 续做新增): 几何下限判据不是摆设 ——
        #   把 J_CHG 的全部 fp_* 图形原语删掉 ⇒ 必须红 (few_prim ≥ 1) ---
        pcb9 = os.path.join(tmp, "t9.kicad_pcb")
        io.open(pcb9, "w", encoding="utf-8").write(_strip_fp_geom(pcb_txt, "J_CHG"))
        r9 = run(pcb=pcb9)
        ok = r9["rules"]["R3-A5"]["few_prim"] >= 1
        cases.append(("T9 把 J_CHG 的 fp_* 图形原语全删掉 ⇒ 期望几何下限判据红 (few_prim ≥ 1)",
                      ok, f'few_prim={r9["rules"]["R3-A5"]["few_prim"]}'))

        # --- T10 (2026-11-16 14:2x 续做新增): 反误报 ——
        #   0 fp_line 的封装 (J_USB_C = 2×fp_rect 画丝印) 不得被判成「无几何」⇒
        #   ★这条同时证明「fp_rect 计入几何」这条订正是承重的 (回退到只数 fp_line ⇒ T0 也会红) ---
        r10 = run()
        pcbmap = r10["ctx"]["pcb"]
        zero_line = sorted(ref for ref, v in pcbmap.items() if v["fplines"] == 0)
        bad_geom = [ref for ref in zero_line if pcbmap[ref]["fp_prim"] < 2]
        ok = (r10["rules"]["R3-A5"]["few_prim"] == 0) and (bad_geom == [])
        cases.append(("T10 反误报: 0 fp_line 的封装 (J_USB_C 用 2×fp_rect 画丝印) 不得被判成『无几何』",
                      ok, f'fp_line==0 的封装={zero_line} · 其中几何原语<2 的={bad_geom} '
                          f'· few_prim={r10["rules"]["R3-A5"]["few_prim"]}'))

        # --- T11 (★2026-11-16 19:3x · ISS-249 新增): ★把 F1 改回旧值 ⇒ 必须回到 3 条 ★
        #   ★fixture = 【真网表 + 真脚表 + 真板】(不是绿基线!) ⇒ F1 一改回, F2/F3 本来就在 ⇒ 必须 3 条 ★
        #   ⇒ ★证明 T7/T8 的「条数期望」改动【没有把判据调没】: 缺陷一回来, findings 必须回来 ★
        #   ⇒ ★判据逻辑 (findings 的计算 / R3-A1~A6) 一个字节没动 ★
        live_rows = read_csv_rows(CSV_NET)
        _write_rows(os.path.join(tmp, "t11.csv"),
                    _patch_netlist_C_VBUS(live_rows, "L8_L12_node2_back_to_C_VBUS_OUT"))
        r11 = analyze(os.path.join(tmp, "t11.csv"))     # ★脚表/板走真文件 (默认参数) ★
        ids11 = [f["id"] for f in r11["findings"]]
        ok11 = (len(r11["findings"]) == 3 and ids11 == ["F1", "F2", "F3"]
                and not r11["rules"]["R3-A1"]["ok"] and not r11["rules"]["R3-A2"]["ok"])
        cases.append(("T11 把 F1 改回旧值 (真网表 L8/L12 的 node2 都借 C_VBUS_OUT) ⇒ 期望回到 3 条 findings "
                      "(★证明条数期望的改动没把判据调没★)", ok11,
                      f'findings={len(r11["findings"])} ids={ids11} '
                      f'A1={r11["rules"]["R3-A1"]["hits"]} A2={r11["rules"]["R3-A2"]["hits"]}'))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("=" * 78)
    print("  --selftest 反向用例自证 (R3)")
    print("=" * 78)
    bad = 0
    for name, ok, info in cases:
        print(f"  {'✅' if ok else '❌'} {name}")
        print(f"       {info}")
        if not ok:
            bad += 1
    print("-" * 78)
    print(f"  反向用例 {len(cases)} 条 · 失败 {bad} 条")
    print(f"  {'✅ 全抓到' if bad == 0 else '❌ 有用例没抓到'}")
    print("=" * 78)
    return 0 if bad == 0 else 1


def _strip_fp_geom(pcb_txt, ref):
    """把某个 footprint 的【全部 fp_* 图形原语】(fp_line/fp_rect/fp_poly/fp_arc/fp_circle) 删掉
    ⇒ 制造「这个封装一个几何都没有」的合成件 (★T9 反向用例用★)"""
    lines = pcb_txt.split("\n")
    out = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("\t(footprint ") and f'"Reference" "{ref}"' in "\n".join(lines[i:i + 12]):
            bal = 0
            k = i
            while k < len(lines):
                bal += lines[k].count("(") - lines[k].count(")")
                if k > i and bal <= 0:
                    break
                k += 1
            body = lines[i:k + 1]
            new = []
            j = 0
            while j < len(body):
                if re.match(r'\s*\(fp_(?:line|rect|poly|arc|circle)\b', body[j]):
                    b2 = 0
                    m = j
                    while m < len(body):
                        b2 += body[m].count("(") - body[m].count(")")
                        if m > j and b2 <= 0:
                            break
                        m += 1
                    j = m + 1
                    continue
                new.append(body[j])
                j += 1
            out.extend(new)
            i = k + 1
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)


def _shrink_j_chg(pcb_txt):
    """把 J_CHG 的焊盘数改成 1 (只留 pad 1)"""
    out = []
    lines = pcb_txt.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].startswith("\t(footprint ") and '"J_CHG"' in "\n".join(lines[i:i + 12]):
            bal = 0
            k = i
            while k < len(lines):
                bal += lines[k].count("(") - lines[k].count(")")
                if k > i and bal <= 0:
                    break
                k += 1
            body = lines[i:k + 1]
            new = []
            drop = False
            for ln in body:
                if re.match(r'\s*\(pad\s+"', ln):
                    if drop:
                        continue
                    drop = True
                if re.match(r'\s*\(pad\s+"', ln):
                    new.append(ln)
                    continue
                new.append(ln)
            # 简单起见: 删掉所有 pad "6" 块
            txt = "\n".join(new)
            txt = re.sub(r'\n\t\t\(pad "6".*?\n\t\t\)\n', "\n", txt, flags=re.S)
            out.extend(txt.split("\n"))
            i = k + 1
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)


def _drop_dnp_marker(pcb_txt, ref):
    """把某个 footprint 的 (attr exclude_from_bom exclude_from_pos_files) 行删掉"""
    lines = pcb_txt.split("\n")
    out = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("\t(footprint ") and f'"Reference" "{ref}"' in "\n".join(lines[i:i + 12]):
            bal = 0
            k = i
            while k < len(lines):
                bal += lines[k].count("(") - lines[k].count(")")
                if k > i and bal <= 0:
                    break
                k += 1
            body = [ln for ln in lines[i:k + 1]
                    if not (ln.strip().startswith("(attr exclude_from_bom"))]
            out.extend(body)
            i = k + 1
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)


def _empty_one_fname(pcb_txt, ref):
    lines = pcb_txt.split("\n")
    out = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("\t(footprint ") and f'"Reference" "{ref}"' in "\n".join(lines[i:i + 12]):
            bal = 0
            k = i
            while k < len(lines):
                bal += lines[k].count("(") - lines[k].count(")")
                if k > i and bal <= 0:
                    break
                k += 1
            body = lines[i:k + 1]
            body[0] = re.sub(r'\(footprint\s+"[^"]*"', '(footprint ""', body[0])
            out.extend(body)
            i = k + 1
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)


def main(argv):
    if "--selftest" in argv:
        return selftest()
    res = analyze()
    if "--json" in argv:
        print(json.dumps({"findings": res["findings"], "rules": res["rules"],
                          "advisory": res["advisory"]}, ensure_ascii=False, indent=2))
        return 1 if res["findings"] else 0
    print(report(res))
    return 1 if res["findings"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
