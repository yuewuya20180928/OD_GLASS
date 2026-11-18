#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_c1_diff.py —— ISS-311 自证探针 (hw-lead)
★**只读**: 不写板 / 不写网表 / 不写任何产物文件 (只往 stdout 打)
★**目的**: 把 chain_gate 的「C1 差 2 个」这句结论, 展开成**逐条可核证据**:
  · 板上有、网表里没有 的 (ref, pad)   —— 带板上网络名 + .kicad_pcb 行号 + 焊盘坐标
  · 网表有、板上没有 的 (ref, pad)   —— 带网表行号 + 网络名
  · 同号异网 的 (ref, pad)           —— 带网表行号 + 板上行号 + 双方网络名
★**口径单一真源**: 直接 import `state/check_pcb_nets.py` 的 `netlist_pads()` / `board_pads()`
  ⇒ **不重写一遍网表→焊盘推导逻辑** ⇒ 零漂移 (★与门禁同口径★)

用法:
  bash state/pcbnew_py.sh logs/iss311/probe_c1_diff.py
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "state"))

import check_pcb_nets as CPN  # noqa: E402

NET = os.path.join(PROJ, "HW", "netlist_v1.csv")
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")


# ---------------------------------------------------------------- 板文件原文行号索引
def build_pcb_text_index(path):
    """★把 .kicad_pcb 原文按 (ref, pad_number) 索引到 (行号, 该行原文) ★
    ★做法: 逐行扫, 遇到 `(footprint "..."` 开一个 footprint 块, 块内 `(property "Reference" "REF"`
    ⇒ 记住 ref; 块内 `(pad "NUM" ...` ⇒ 记 (ref, NUM) → 行号 ★"""
    idx = {}
    refs = {}
    cur = None
    with open(path, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            s = line.strip()
            m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', line)
            if m:
                cur = m.group(1)
                refs[cur] = ln
                continue
            m = re.match(r'\(pad\s+"([^"]*)"', s)
            if m and cur:
                idx[(cur, m.group(1))] = (ln, s)
    return idx, refs


def netlist_line_index(path, board_filter="MAIN_PCB"):
    """网表 CSV 行号索引: (ref) → [(行号, net, node1, node2, type)] ★
    ★注: 网表是「一行 = 一根连接」模型 ⇒ 同一个 ref 会出现在多行 ⇒ 取全部 ★"""
    out = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        for ln, r in enumerate(rd, 2):
            if (r.get("board") or "MAIN_PCB").strip() != board_filter:
                continue
            ref = (r.get("ref") or "").strip()
            if not ref:
                continue
            out.setdefault(ref, []).append(
                (ln, (r.get("net") or "").strip(), (r.get("node1") or "").strip(),
                 (r.get("node2") or "").strip(), (r.get("type") or "").strip()))
    return out


def main():
    print("=" * 78)
    print("ISS-311 · C1 焊盘级差异探针 (只读)")
    print("=" * 78)

    rows = list(csv.DictReader(open(NET, encoding="utf-8")))
    rows = [r for r in rows if (r.get("board") or "MAIN_PCB").strip() == CPN.BOARD_FILTER]
    per_ref, numbered, placeholder, notes = CPN.netlist_pads(rows)
    have, board_refs = CPN.board_pads(PCB)

    want = {}
    for ref, pins in per_ref.items():
        if ref.startswith(CPN.PSEUDO):
            continue
        for n, net in pins:
            want[(ref, str(n))] = net

    missing, extra, wrong = CPN.compare(want, have)
    nc_pads = {k for k, v in have.items() if not v}
    extra_real = [e for e in extra if e[0] not in nc_pads]

    pcb_idx, pcb_refs = build_pcb_text_index(PCB)
    net_idx = netlist_line_index(NET)

    print(f"\n网表推出的 (ref,pad)→网络: {len(want)} 条")
    print(f"板上带网络的 (ref,pad)→网络: {len(have) - len(nc_pads)} 条")
    print(f"板上 NC 焊盘: {len(nc_pads)} 个")
    print(f"★差集: 缺失(网表有板没有) {len(missing)} · 多余(板有网表没有) {len(extra_real)} "
          f"· 同号异网 {len(wrong)}")

    # ---------------- 板上有、网表里没有 ----------------
    print("\n" + "-" * 78)
    print("【A】★板上有、网表里没有★ (⇒ 板侧多出来的旧件 / 网表删掉的件)")
    print("-" * 78)
    if not extra_real:
        print("(无)")
    for (ref, pad), net in extra_real:
        ent = pcb_idx.get((ref, pad))
        lines = net_idx.get(ref, [])
        print(f"★ {ref} pad{pad} = {net}")
        print(f"    .kicad_pcb 行号: {ent[0] if ent else '(未在原文找到)'}")
        print(f"    .kicad_pcb 原行: {ent[1] if ent else '(未在原文找到)'}")
        print(f"    板上位号行: {pcb_refs.get(ref, '(未找到)')}")
        print(f"    网表里有没有这个位号: {'★没有 ⇒ 板侧多出来的旧件' if ref not in net_idx else '有 (见下)'}")
        for ln, n, n1, n2, ty in lines:
            print(f"    网表行 L{ln}: ref={ref} net={n} node1={n1!r} node2={n2!r} type={ty}")
        if not lines:
            # ★板上有、网表里完全没有 ⇒ 看看网表里长得很像的 (同前缀)
            pre = ref.rsplit("_", 1)[0] + "_" if "_" in ref else ref
            cands = [k for k in net_idx if k.startswith(pre) and k != ref]
            print(f"    ★网表里同前缀(`{pre}`)的器件: {sorted(cands)[:12]}")

    # ---------------- 网表有、板上没有 ----------------
    print("\n" + "-" * 78)
    print("【B】★网表有、板上没有★ (⇒ 网表新加的脚 / 板侧漏画)")
    print("-" * 78)
    if not missing:
        print("(无)")
    for (ref, pad), net in missing:
        print(f"★ {ref} pad{pad} 应为 {net}")
        for ln, n, n1, n2, ty in net_idx.get(ref, []):
            print(f"    网表行 L{ln}: net={n} node1={n1!r} node2={n2!r} type={ty}")
        print(f"    板上该位号行: {pcb_refs.get(ref, '(板上没有这个位号)')}")

    # ---------------- 同号异网 ----------------
    print("\n" + "-" * 78)
    print("【C】★同号异网★ (⇒ 脚位对调 / 网名改过 · 板上挂错网)")
    print("-" * 78)
    if not wrong:
        print("(无)")
    for (ref, pad), wantnet, havenet in wrong:
        ent = pcb_idx.get((ref, pad))
        print(f"★ {ref} pad{pad}: 网表应为 {wantnet} / 板上实际 {havenet}")
        print(f"    .kicad_pcb 行号: {ent[0] if ent else '(未在原文找到)'}")
        print(f"    .kicad_pcb 原行: {ent[1] if ent else '(未在原文找到)'}")
        for ln, n, n1, n2, ty in net_idx.get(ref, []):
            print(f"    网表行 L{ln}: net={n} node1={n1!r} node2={n2!r} type={ty}")

    # ---------------- 涉及的器件, 板上全部焊盘一览 ----------------
    print("\n" + "-" * 78)
    print("【D】涉及器件的板上全部焊盘一览 (便于人工核)")
    print("-" * 78)
    touch = sorted({k[0] for k, _ in extra_real} | {k[0] for k, _ in missing} | {k[0] for k, _, _ in wrong})
    for ref in touch:
        pads = sorted([(k[1], v) for k, v in have.items() if k[0] == ref], key=lambda t: t[0])
        print(f"· {ref}  (板上带网焊盘 {len(pads)} 个)")
        for pad, net in pads:
            ent = pcb_idx.get((ref, pad))
            w = want.get((ref, pad))
            flag = "" if w == net else f"   ★网表要求={w!r}"
            print(f"    pad{pad:<4} net={net!r:<28} L{ent[0] if ent else '?':<7}{flag}")
        if ref not in net_idx:
            print(f"    ★★网表里**完全没有** {ref} 这个位号 ★★")
        else:
            print(f"    网表里 {ref} 的行:")
            for ln, n, n1, n2, ty in net_idx[ref]:
                print(f"      L{ln}: net={n!r} node1={n1!r} node2={n2!r} type={ty!r}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
