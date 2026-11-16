#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-241 附录 · 落表批次回填核对 + pad↔pin 序一致性机检 (只读, 零外发, 不落表)
=====================================================================
作者: sw-lead (软件总工) · 2026-11-17 · 交卷给 main / 项目总工

为什么有这张脚本:
    ISS-241 只出选型证据, 不落表。 但 2026-11-16 22:25 hw-lead 的落表批次把
    大部分 OPN 回填进了 BOM / 网表 / 脚表 ⇒ 本脚本把「矩阵推荐项 vs 板上已落
    值」逐件对齐, 并把最容易翻车的那一类 (占位 pad 序 vs 器件引脚序) 机检出来
    —— ★**D_ESD_CAM 落表后是反的** (pad1=GND/pad2=CSI, 而落表器件 pin1=I/O/
    pin2=GND) ⇒ 不重画 land 直接投板 ⇒ CSI lane 上没有 ESD。

★**本脚本只读**: 只读 HW/PART_SELECTION_MATRIX_2026-11-16.md / HW/BOM_v1.csv /
HW/netlist_v1_pins.csv / HW/PCB/demo_mainboard.kicad_pcb ⇒ **一个字节都不写**
(自测在 tempfile 沙盒里改副本, 不碰真源)。

用法:
    python3 HW/check_part_selection_landed_crosscheck.py            # 正常跑 ⇒ rc=0 (发现以 ★ 列出)
    python3 HW/check_part_selection_landed_crosscheck.py --strict   # 有 ★PAD-序 缺陷 ⇒ rc=1
    python3 HW/check_part_selection_landed_crosscheck.py --selftest # 反向用例自证 ⇒ rc=0 (N/N)
    python3 HW/check_part_selection_landed_crosscheck.py --bom F --pins F --pcb F --matrix F

检查项 (C0~C5):
    C0 矩阵基准块可解析 + 22 个在册位号一个不缺
    C1 矩阵 22 个位号在 BOM_v1.csv 里都存在 (落表后行不能被删掉)
    C2 落表三分统计: HIT(落表值=矩阵推荐) / DEVIATION(落了但≠推荐) / OPEN(仍待选型) —— 打印逐件明细
    C3 OPEN 件在矩阵里必须仍有 ≥2 候选 + 非空降级方案 (证据没烂 ⇒ 可直接回填)
    C4 ★PAD-序一致性: 板上占位 pad 序 vs 落表器件引脚序 (逐件逐 pad 核; 不一致 ⇒ ★缺陷)
    C5 焊盘数 vs 器件脚数 (板上有占位的逐件核; 充电板件无占位 ⇒ 报「需落板批次定 N 焊盘 land」)

--selftest 反向用例 (每条自证「真的改到了目标」):
    M1 从 BOM 副本删掉一个位号        → 期望 C1 变红
    M2 从矩阵副本删掉一个位号          → 期望 C0 变红
    M3 把 OPEN 件 (D_LED_G) 的候选清空  → 期望 C3 变红
    M4 把 D_ESD_CAM 的 pad 网络对调成正确序 → 期望 C4 对该件不再报 ★ (反向: 证明 C4 真在核)
    M5 把 Q_ENVC 的 pad2 网络改成非 GND  → 期望 C4 对 Q_ENVC 报 ★ (正向: 证明 C4 会抓)
"""

import argparse
import csv
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

DOC_REL = os.path.join("HW", "PART_SELECTION_MATRIX_2026-11-16.md")
BOM_REL = os.path.join("HW", "BOM_v1.csv")
PINS_REL = os.path.join("HW", "netlist_v1_pins.csv")
PCB_REL = os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb")

BASELINE_BEGIN = "<!-- BEGIN 选型证据基准块 -->"
BASELINE_END = "<!-- END 选型证据基准块 -->"

# ---------------------------------------------------------------- 器件引脚序表
# ★**每条都来自器件官方数据手册 (ISS-241 矩阵里已带链接)**, 不是猜的。
DEVICE_PIN_ORDER = {
    # TI DPY X1SON 2 脚: 1=I/O 2=GND  (TI TPD1E05U06 数据手册 pinout)
    "TPD1E05U06DPYR": {"1": "I/O", "2": "GND"},
    # Nexperia SOD-323 2 脚: 1=K1 2=K2 双向 ⇒ 无极性 ⇒ pad 序无所谓
    "PESD5V0S1BA": {"1": "K1", "2": "K2", "bidirectional": True},
    # AOS SOT-23 3 脚: 1=G 2=S 3=D  (AO3400A / AO3407A 数据手册 pinout)
    "AO3400A": {"1": "G", "2": "S", "3": "D"},
    # Diodes Inc SOT-23 3 脚: 1=G 2=S 3=D  (DMP3098L 数据手册 pinout)
    "DMP3098L": {"1": "G", "2": "S", "3": "D"},
    # Microchip/onsemi SOT-23 3 脚: 1=G 2=S 3=D  (2N7002 数据手册 pinout)
    "2N7002": {"1": "G", "2": "S", "3": "D"},
}

# ---------------------------------------------------- 每个网络应当接到器件的哪个角色
# ★**来源 = 网表 note / ISS-241 矩阵 criteria** (逐件引用见 ISS-241 §3)。
# "?" = 角色待裁决 (缺口 G-1: Q_PG 源漏措辞与 P-MOS 高边拓扑相反) ⇒ 不判, 只报。
NET_ROLE_EXPECT = {
    "D_ESD_CAM": {"CSI_D0_CK_P": "I/O", "GND": "GND"},
    "D_ESD_DEMO": {"RAIL_DEMO_5V": "I/O", "GND": "GND"},
    "D_ESD_USB_D": {"USB_D_P_SRC": "I/O", "GND": "GND"},
    "Q_AND": {"RESET_N": "D", "GND": "S", "PG_AND": "G"},
    "Q_ENVC": {"PG_AND": "G", "GND": "S", "EN_VCORE": "D"},
    "Q_PG": {"PWR_ON": "?", "BAT_SW": "?", "PWR_GOOD": "?"},
}

# 已知「pad 序 ≠ 器件引脚序」但板文件还没重画 land 的件 (占位 pad 序 = 网表顺序)
PAD_ORDER_EXPECT_NOTE = {
    "D_ESD_CAM": "占位 pad 序 = GND/信号, 器件 DPY 引脚序 = I/O/GND ⇒ 必须重画 land (或改用双向件 PESD5V0S1BA)",
    "Q_AND": "占位 pad 序 = D/S/G, SOT-23 库引脚序 = G/S/D ⇒ 必须重画 land",
    "Q_PG": "占位 pad 序 = S/D/G, SOT-23 库引脚序 = G/S/D ⇒ 必须重画 land (且角色待 G-1 裁决)",
}


def load_matrix(path):
    txt = open(path, encoding="utf-8").read()
    if BASELINE_BEGIN not in txt or BASELINE_END not in txt:
        raise ValueError("矩阵基准块缺失")
    blk = txt.split(BASELINE_BEGIN)[1].split(BASELINE_END)[0]
    blk = blk.split("```json")[1].split("```")[0]
    return json.loads(blk)


def load_bom(path):
    with open(path, newline="", encoding="utf-8") as f:
        return {r["ref"]: r for r in csv.DictReader(f)}


def load_pins(path):
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.setdefault(r["ref"], {})[r["pin"].strip()] = r["net"].strip()
    return out


def load_pcb_pads(path):
    """读 KiCad 板文件: ref -> {pad_number: net_name}"""
    lines = open(path, encoding="utf-8").read().split("\n")
    starts = [i for i, l in enumerate(lines) if l.strip().startswith("(footprint ")]

    def block(i):
        depth, out = 0, []
        for j in range(i, len(lines)):
            l = lines[j]
            depth += l.count("(") - l.count(")")
            out.append(l)
            if depth == 0:
                return out
        return out

    pads = {}
    for i in starts:
        s = "\n".join(block(i))
        m = re.search(r'\(property "Reference" "([^"]+)"', s)
        if not m:
            continue
        ref = m.group(1)
        d = {}
        for pm in re.finditer(r'\(pad "([^"]+)"(.*?)\n\t\t\)', s, re.S):
            nm = re.search(r'\(net (?:\d+ )?"([^"]*)"\)', pm.group(2))
            d[pm.group(1)] = nm.group(1) if nm else ""
        if d:
            pads.setdefault(ref, {}).update(d)
    return pads


def _pcb_footprint_span(lines, ref):
    """返回 (start, end) 该 ref 的 footprint 块行号区间 (按括号深度切块, 不用缩进猜)"""
    for i, l in enumerate(lines):
        if not l.strip().startswith("(footprint "):
            continue
        depth, end = 0, None
        for j in range(i, len(lines)):
            depth += lines[j].count("(") - lines[j].count(")")
            if depth == 0:
                end = j + 1
                break
        if end is None:
            continue
        if f'"Reference" "{ref}"' in "\n".join(lines[i:end]):
            return i, end
    return None, None


def pcb_swap_pad_nets(lines, ref, net_a, net_b):
    """把该 ref 块内 net_a / net_b 的 pad 网络对调 (自测用)"""
    s, e = _pcb_footprint_span(lines, ref)
    if s is None:
        return False
    ia = ib = None
    for k in range(s, e):
        if ia is None and f'(net "{net_a}")' in lines[k]:
            ia = k
        if ib is None and f'(net "{net_b}")' in lines[k]:
            ib = k
    if ia is None or ib is None or ia == ib:
        return False
    lines[ia] = lines[ia].replace(f'(net "{net_a}")', f'(net "@@TMP@@")')
    lines[ib] = lines[ib].replace(f'(net "{net_b}")', f'(net "{net_a}")')
    lines[ia] = lines[ia].replace('(net "@@TMP@@")', f'(net "{net_b}")')
    return True


def pcb_set_pad_net(lines, ref, net_old, net_new):
    """把该 ref 块内第一个 net_old 改成 net_new (自测用)"""
    s, e = _pcb_footprint_span(lines, ref)
    if s is None:
        return False
    for k in range(s, e):
        if f'(net "{net_old}")' in lines[k]:
            lines[k] = lines[k].replace(f'(net "{net_old}")', f'(net "{net_new}")')
            return True
    return False


def part_of(row):
    """取落表 OPN 型号 (opn 栏优先, 退回 value 栏; '[0数据]' 视为未落表)"""
    opn = (row.get("opn") or "").strip()
    if opn and opn != "[0数据]":
        m = re.match(r"^([A-Za-z0-9\-\+\.\_]+)", opn)
        if m:
            return m.group(1)
    val = (row.get("value") or "").strip()
    if val and "待选型" not in val:
        m = re.match(r"^([A-Za-z0-9\-\+\.\_]+)", val)
        if m:
            return m.group(1)
    return ""


def run_checks(matrix_path, bom_path, pins_path, pcb_path):
    """返回 (results, details)"""
    res = []
    details = []

    def add(cid, ok, msg):
        res.append((cid, ok, msg))

    # ---- C0 矩阵基准块
    try:
        mtx = load_matrix(matrix_path)
        refs = list(mtx.get("expected_refs", []))
        items = {it["ref"]: it for it in mtx.get("items", [])}
        add("C0", len(refs) > 0 and len(items) == len(refs),
            f"矩阵基准块解析通过 · 在册位号 {len(refs)} · 条目 {len(items)}")
    except Exception as e:  # noqa: BLE001
        add("C0", False, f"矩阵基准块解析失败: {e}")
        return res, details

    bom = load_bom(bom_path)
    pins = load_pins(pins_path)
    pads = load_pcb_pads(pcb_path)

    # ---- C1 位号还在不在 BOM
    missing = [r for r in refs if r not in bom]
    add("C1", not missing, f"矩阵 {len(refs)} 个位号在 BOM 里全在" if not missing
        else f"BOM 缺位号: {missing}")

    # ---- C2 落表三分统计
    hit, dev, open_ = [], [], []
    for r in refs:
        row = bom.get(r, {})
        pn = part_of(row)
        if not pn:
            open_.append((r, "opn 仍空/[0数据]", "", ""))
            continue
        it = items.get(r, {})
        pick = (it.get("recommendation") or {}).get("pick", "")
        cands = [c.get("pn", "") for c in it.get("candidates", [])]
        if pn == pick:
            hit.append((r, pn))
        elif pn in cands:
            dev.append((r, pn, pick, "落表=矩阵候选2 (非推荐项)"))
        else:
            dev.append((r, pn, pick, "★落表值不在矩阵候选里 (新选型)"))
    add("C2", True, f"落表三分: HIT={len(hit)} (落表值=矩阵推荐) · "
                    f"DEVIATION={len(dev)} · OPEN={len(open_)} (仍待选型)")
    details.append("HIT (落表值 = ISS-241 推荐项):")
    details += [f"    ✔ {r:<14} {p}" for r, p in hit]
    details.append("DEVIATION (落了但 ≠ ISS-241 推荐项):")
    details += [f"    ▲ {r:<14} 落表={p} | 矩阵推荐={pk} | {why}" for r, p, pk, why in dev] \
        or ["    (无)"]
    details.append("OPEN (BOM 里 value/opn 仍待选型):")
    details += [f"    ○ {r:<14} {note}" for r, note, _, _ in open_] or ["    (无)"]

    # ---- C3 OPEN 件的证据还在不在 (可回填性)
    bad_open = []
    for r, note, _, _ in open_:
        it = items.get(r, {})
        cands = [c for c in it.get("candidates", []) if (c.get("pn") or "").strip()]
        fb = (it.get("fallback") or "").strip()
        if len(cands) < 2 or not fb:
            bad_open.append(r)
    add("C3", not bad_open,
        f"OPEN 件在矩阵里证据完整 (≥2 候选 + 非空降级方案)" if not bad_open
        else f"OPEN 件证据缺失: {bad_open}")
    details.append("OPEN 件可直接回填的 ISS-241 推荐项:")
    for r, note, _, _ in open_:
        it = items.get(r, {})
        pick = (it.get("recommendation") or {}).get("pick", "")
        cands = ", ".join(c.get("pn", "") for c in it.get("candidates", []))
        details.append(f"    ○ {r:<14} 推荐={pick or '(无)'} | 候选= {cands}")

    # ---- C4 ★PAD-序一致性
    defects = []
    for r, expect in NET_ROLE_EXPECT.items():
        row = bom.get(r, {})
        pn = part_of(row)
        order = DEVICE_PIN_ORDER.get(pn)
        if not order:
            continue
        if order.get("bidirectional"):
            details.append(f"    ⓘ {r:<14} {pn} 双向件 ⇒ pad 序无极性要求 (跳过 C4 判)")
            continue
        pcb_pad = pads.get(r, {})
        if not pcb_pad:
            details.append(f"    ⓘ {r:<14} 板文件无占位 (充电板件) ⇒ 跳过 C4 判")
            continue
        for pad_no, net in sorted(pcb_pad.items()):
            role_dev = order.get(pad_no)
            role_exp = expect.get(net)
            if role_dev is None or role_exp is None or role_exp == "?":
                continue
            if role_dev != role_exp:
                defects.append((r, pn, pad_no, net, role_exp, role_dev))
    add("C4", not defects,
        "PAD-序一致性: 板文件占位 pad 序 与 落表器件引脚序 全部对上" if not defects
        else f"★PAD-序缺陷 {len(defects)} 处 (不重画 land 直接投板 ⇒ 器件脚接错)")
    details.append("C4 逐 pad 判定:")
    for r, pn, pad_no, net, role_exp, role_dev in defects:
        note = PAD_ORDER_EXPECT_NOTE.get(r, "")
        details.append(
            f"    ★ {r:<14} {pn} pad{pad_no}(net={net}) 期望角色={role_exp} "
            f"实际器件脚={role_dev} ⇒ 接错 {note}")
    for r, expect in NET_ROLE_EXPECT.items():
        if r in [d[0] for d in defects]:
            continue
        if any(v == "?" for v in expect.values()):
            details.append(f"    ⓘ {r:<14} pad 序与器件引脚序比对【待裁决】(角色归属由缺口 G-1 定) ⇒ 不判对错")
        else:
            details.append(f"    ✔ {r:<14} pad 序与器件引脚序一致")

    # ---- C5 焊盘数 vs 器件脚数
    bad5 = []
    for r in refs:
        row = bom.get(r, {})
        pn = part_of(row)
        if not pn:
            continue
        order = DEVICE_PIN_ORDER.get(pn)
        if not order:
            continue
        n_dev = len([k for k in order if k != "bidirectional"])
        pcb_pad = pads.get(r, {})
        if pcb_pad:
            if len(pcb_pad) != n_dev:
                bad5.append((r, pn, len(pcb_pad), n_dev))
        else:
            details.append(f"    ⓘ {r:<14} {pn} 器件 {n_dev} 脚 · 板文件无占位 "
                            f"⇒ 充电板落板批次须定 {n_dev} 焊盘 land")
    add("C5", not bad5,
        "焊盘数 vs 器件脚数: 逐件对上" if not bad5
        else f"★焊盘数不符: {bad5}")

    return res, details


def print_report(res, details, strict):
    for cid, ok, msg in res:
        print(f"  [{'PASS' if ok else 'FAIL'}] {cid} — {msg}")
    print()
    for d in details:
        print(d)
    n_fail = sum(1 for _, ok, _ in res if not ok)
    star_defect = any(not ok and cid == "C4" for cid, ok, _ in res)
    if strict and n_fail:
        print(f"\n[check_part_selection_landed_crosscheck] STRICT — {n_fail} 项 FAIL ⇒ rc=1")
        return 1
    if n_fail:
        print(f"\n[check_part_selection_landed_crosscheck] 完成 — ★{n_fail} 项 FAIL (缺陷见上, "
              f"本脚本只报告不修); rc=0 (加 --strict ⇒ rc=1)")
        return 0
    print("\n[check_part_selection_landed_crosscheck] PASS — 全过 (rc=0)")
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    cases = []

    def sandbox():
        d = tempfile.mkdtemp(prefix="iss241_cc_")
        for rel in (DOC_REL, BOM_REL, PINS_REL, PCB_REL):
            src = os.path.join(ROOT, rel)
            dst = os.path.join(d, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
        return d

    def run(d):
        return run_checks(os.path.join(d, DOC_REL), os.path.join(d, BOM_REL),
                          os.path.join(d, PINS_REL), os.path.join(d, PCB_REL))

    # M1 从 BOM 副本删掉一个位号 → C1 红
    d = sandbox()
    p = os.path.join(d, BOM_REL)
    lines = open(p, encoding="utf-8").read().split("\n")
    out = [l for l in lines if not l.startswith("SW_RST,")]
    open(p, "w", encoding="utf-8").write("\n".join(out))
    res, _ = run(d)
    cases.append(("M1 删 BOM 里的 SW_RST → C1 红", ("C1", False) in [(c, o) for c, o, _ in res]))
    shutil.rmtree(d, ignore_errors=True)

    # M2 从矩阵副本删掉一个位号 → C0 红
    d = sandbox()
    p = os.path.join(d, DOC_REL)
    t = open(p, encoding="utf-8").read()
    t = t.replace('"SW_BOOT",\n', "", 1)
    open(p, "w", encoding="utf-8").write(t)
    res, _ = run(d)
    cases.append(("M2 删矩阵里的 SW_BOOT → C0 红", ("C0", False) in [(c, o) for c, o, _ in res]))
    shutil.rmtree(d, ignore_errors=True)

    # M3 把 OPEN 件 (D_LED_G) 的候选清空 → C3 红
    d = sandbox()
    p = os.path.join(d, DOC_REL)
    t = open(p, encoding="utf-8").read()
    t = t.replace('"pn": "KP-2012SGC"', '"pn": ""', 1)
    open(p, "w", encoding="utf-8").write(t)
    res, _ = run(d)
    cases.append(("M3 清空 D_LED_G 候选 → C3 红", ("C3", False) in [(c, o) for c, o, _ in res]))
    shutil.rmtree(d, ignore_errors=True)

    # M4 把 D_ESD_CAM 的 pad 网络对调成正确序 → C4 对该件不再报 ★ (证明 C4 真在核 pad 序)
    d0 = sandbox()
    res0, det0 = run(d0)
    base_flags_cam = any("D_ESD_CAM" in x for x in det0 if x.strip().startswith("★"))
    shutil.rmtree(d0, ignore_errors=True)

    d = sandbox()
    p = os.path.join(d, PCB_REL)
    lines = open(p, encoding="utf-8").read().split("\n")
    swapped = pcb_swap_pad_nets(lines, "D_ESD_CAM", "GND", "CSI_D0_CK_P")
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    res, details = run(d)
    still_flags_cam = any("D_ESD_CAM" in x for x in details if x.strip().startswith("★"))
    cases.append(("M4 D_ESD_CAM: 基线报 ★ → 把 pad 序改对后不再报 ★",
                   base_flags_cam and swapped and not still_flags_cam))
    shutil.rmtree(d, ignore_errors=True)

    # M5 把 Q_ENVC 的 pad2 网络改成非 GND → C4 对 Q_ENVC 报 ★ (证明 C4 会抓)
    d = sandbox()
    p = os.path.join(d, PCB_REL)
    lines = open(p, encoding="utf-8").read().split("\n")
    changed = pcb_set_pad_net(lines, "Q_ENVC", "GND", "PG_AND")
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    res, details = run(d)
    c4_ok = [ok for cid, ok, _ in res if cid == "C4"][0]
    hits_qenvc = any("Q_ENVC" in x for x in details if x.strip().startswith("★"))
    cases.append(("M5 改坏 Q_ENVC pad 网络 → C4 报 ★ 且点名 Q_ENVC",
                   changed and (not c4_ok) and hits_qenvc))
    shutil.rmtree(d, ignore_errors=True)

    print("[check_part_selection_landed_crosscheck] selftest:")
    n_ok = 0
    for name, ok in cases:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        n_ok += 1 if ok else 0
    print(f"selftest: {n_ok}/{len(cases)}")
    return 0 if n_ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--bom")
    ap.add_argument("--pins")
    ap.add_argument("--pcb")
    ap.add_argument("--matrix")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    matrix_path = args.matrix or os.path.join(ROOT, DOC_REL)
    bom_path = args.bom or os.path.join(ROOT, BOM_REL)
    pins_path = args.pins or os.path.join(ROOT, PINS_REL)
    pcb_path = args.pcb or os.path.join(ROOT, PCB_REL)

    print("[check_part_selection_landed_crosscheck] 落表回填核对 + PAD 序机检 (只读)")
    res, details = run_checks(matrix_path, bom_path, pins_path, pcb_path)
    return print_report(res, details, args.strict)


if __name__ == "__main__":
    sys.exit(main())
