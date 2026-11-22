#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HW/check_iss247_f1_landed.py —— ★**ISS-247 · 「F1 是否已落表」语义门禁**★

★★**干什么**★★
  判 ★**ISS-242 的 F1 (网表自相矛盾第 1 条: 两颗 2 脚电容 C_VBUS_OUT / C_VBUS_GND
  在网表里端子标签撞车) 是否已经落到 `HW/netlist_v1.csv` 里** ★
  ⇒ ★**判据全部挂在【语义】上 (端子归属 / 网名绑定 / 端子登记台账), 一个 md5 都不碰** ★
  ⇒ 因为 md5 会随别的批次 (ISS-245 SW 重锚 / ISS-246 MECH 重锚 / V-2~V-4 落表) 一起变,
    ★**挂 md5 的门禁必然一换批次就过期 ⇒ 本门禁坚决不挂** ★

★★**病灶 (F1) 一句话**★★
  `HW/netlist_v1.csv` 里一颗 **2 脚**器件 (C_VBUS_OUT) 的裸位号被登记了 **4 次**
  (脚表只有 2 个脚) ⇒ ★**导出后一脚悬空 / 串联对地混在一颗上** ★
  ★★**★现状 (2026-11-16 19:2x · ISS-249): ★F1 已落表★ ⇒ 两颗 2 脚电容的端子登记各回到 2 次
  (= 脚表脚数) ⇒ ★**默认模式现在 rc=0 (已落)★** ⇒ ★**下面「病灶」段保留作历史对照 (改法与判据没变)** ★ ★

★★**落表真源 (★不是手改 CSV★)**★★
  `state/gen_netlist.py` 的 `add(page, net, node1, node2, ref, ...)` 第 4 个参数 (node2) 槽:
    · L381  `add("P1", "VBUS_5V_F1", "FB_VBUS", <node2>, "FB_VBUS", ...)`   ← FB_VBUS 后级行
    · L393  `add("P1", "VBUS_5V_CHG", "C_VBUS_GND", <node2>, "C_VBUS_GND", ...)` ← C_VBUS_GND 信号端行
  ★**两个 node2 槽都写了 `C_VBUS_OUT`** ⇒ ★**"node2 槽" 混用了两种绑定约定** ★
    约定甲 (器件↔器件直连): node2 = 对方的裸位号 (合法写法, 例: L40 `R_NTC_BAT` ↔ `R_TS_PULL`)
    约定乙 (器件↔网):        node2 = 网名 (如 `VBUS_5V_F1` / `GND`)
  ★**F1 的两行误用了约定甲, 而且借的那颗 (C_VBUS_OUT) 是【2 脚 C】⇒ 端子台账被登记爆** ★

★★**本门禁的 6 条判据 (★S1/S3 是定向 · S4/S5 是通用 · S6 是反误报护栏★)**★★
  **S1** `C_VBUS_GND` 的信号端行 (ref=C_VBUS_GND 且 net=脚表里它那根**非 GND** 脚所属的网)
       的 **node2 必须等于它自己的网名** (⇒ `VBUS_5V_CHG`) ⇒ ★**不许借别人的裸位号** ★
  **S2** `C_VBUS_OUT` 的串联端行 (ref=C_VBUS_OUT 且 net=脚表里它第 2 脚所属的网) 的 node2
       必须是**带 pin 提示的物理脚** (如 `U_CHG pin1`) 或**自己的网名** ⇒ 不许借 2 脚 C 的裸位号
  **S3** `FB_VBUS` 的后级行 (ref=FB_VBUS 且 net=脚表里它第 2 脚所属的网 = `VBUS_5V_F1`) 的
       **node2 必须等于它自己的网名** (⇒ `VBUS_5V_F1`) ⇒ ★**不许借别人的裸位号** ★
  **S4** (通用·等价 R3-A1) ★**每颗 2 脚 C 的裸位号在 node1/node2 槽出现的总次数 ≤ 它在脚表里的脚数** ★
  **S5** (通用·等价 R3-A2) ★**任一行 (ref 是 2 脚 C) 的 node2 若是另一颗 2 脚 C 的裸位号,
       且两颗在脚表里同在该行的 net ⇒ 端子标签撞车** ★
  **S6** (反误报护栏) ★**器件↔器件直连里对方是 2 脚 R/L/D 的, 不得判红**
       (例: L184 `C_DET_BAT` ↔ `R_BAT_DET_2` = 合法分压/检测写法) ★

★★**用法**★★
    python3 HW/check_iss247_f1_landed.py                 # ★**判定模式**: rc=0 ⇔ F1 已落表
    python3 HW/check_iss247_f1_landed.py --expect-landed    # 同上 (显式)
    python3 HW/check_iss247_f1_landed.py --expect-not-landed # ★**【已过期·停用】** ★ISS-249 落表后恒 rc=1
                                                      #   ⇒ 不许再当守卫跑 (★活文件的现状由默认模式守★)
    python3 HW/check_iss247_f1_landed.py --selftest         # ★**反向用例自证** (rc=0 = 全抓到)
                                                      #   ★**11 条 · fixture 与活文件状态无关 (T0/T4/T5 先显式回退成落表前)★ ★
    python3 HW/check_iss247_f1_landed.py --json              # 机器可读
    python3 HW/check_iss247_f1_landed.py --csv <path> --pins <path>   # 换盘 (自测用)

★★**只读**: 本脚本 **只读** `HW/netlist_v1.csv` + `HW/netlist_v1_pins.csv`, ★**一个字节都不写** ★
★★**零外发** (不发邮件 / 不联系供应商 / 不下采购单) · ★**实物 [实测] = 0 条** ★
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

CSV_NET = os.path.join(PROJ, "HW", "netlist_v1.csv")
CSV_PINS = os.path.join(PROJ, "HW", "netlist_v1_pins.csv")

# ★**F1 病灶点名的两颗 2 脚电容 + 那一对信号网** ★
CAP_SERIES = "C_VBUS_OUT"          # 串联电容 (VBUS_5V_F1 ↔ VBUS_5V_CHG)
CAP_SHUNT = "C_VBUS_GND"           # 对地电容 (VBUS_5V_CHG ↔ GND)
BEAD = "FB_VBUS"                   # π 滤波磁珠 (它的后级行也借了 C_VBUS_OUT 的裸位号)
GND_NET = "GND"

# ★**2 脚无源件类型 (★S6 的 scope★)** ★
PASSIVE_2P = ("C", "R", "L", "D")


# ═══════════════════════════════════════════════════════════════════════════
# 0 · 读盘
# ═══════════════════════════════════════════════════════════════════════════
def read_rows(path):
    """读 CSV ⇒ [(file_line_no, dict)]  (file_line_no 含表头偏移, L1 = 表头)"""
    with io.open(path, encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        return [(i + 2, r) for i, r in enumerate(rdr)]


def cell(r, k):
    return (r.get(k) or "").strip()


def build_index(net_rows, pin_rows):
    """⇒ {types, pins, regs}  (types: ref→type · pins: ref→{pin: net} · regs: 裸位号→登记列表)"""
    types = {}
    pins = {}
    for _ln, r in pin_rows:
        ref = cell(r, "ref")
        types.setdefault(ref, cell(r, "type"))
        pins.setdefault(ref, {})[cell(r, "pin")] = cell(r, "net")
    regs = {}
    for ln, r in net_rows:
        ref = cell(r, "ref")
        net = cell(r, "net")
        for slot in ("node1", "node2"):
            v = cell(r, slot)
            if not v or " " in v:        # 带 " pinN" 提示的物理脚, 不是裸位号
                continue
            regs.setdefault(v, []).append({"line": ln, "net": net, "slot": slot, "row_ref": ref})
    return {"types": types, "pins": pins, "regs": regs}


def is_2pin_cap(idx, ref):
    return idx["types"].get(ref) == "C" and len(idx["pins"].get(ref, {})) == 2


def is_2pin_passive(idx, ref):
    return idx["types"].get(ref) in PASSIVE_2P and len(idx["pins"].get(ref, {})) == 2


def bare(v):
    """裸位号 (无空格) ⇒ True"""
    return bool(v) and " " not in v


# ═══════════════════════════════════════════════════════════════════════════
# 1 · 6 条判据
# ═══════════════════════════════════════════════════════════════════════════
def crit_S1(idx, net_rows):
    """S1: C_VBUS_GND 的信号端行, node2 必须等于它自己的网名 (不许借别人的裸位号)"""
    hits = []
    pmap = idx["pins"].get(CAP_SHUNT, {})
    sig_nets = [n for n in pmap.values() if n != GND_NET]
    if not sig_nets:
        return {"ok": False, "hits": [{"detail": f"脚表里 {CAP_SHUNT} 没有非 {GND_NET} 的信号脚"
                                        f" ⇒ 脚表本身缺一根 (⇒ F1 判定前提不成立)"}]}
    target_net = sorted(sig_nets)[0]
    rows = [(ln, r) for ln, r in net_rows
            if cell(r, "ref") == CAP_SHUNT and cell(r, "net") == target_net]
    if not rows:
        return {"ok": False, "hits": [{"detail": f"网表里找不到 {CAP_SHUNT} 在 {target_net} 上的行"}]}
    for ln, r in rows:
        n2 = cell(r, "node2")
        if n2 != target_net:
            hits.append({"line": ln, "net": target_net, "node2": n2,
                         "detail": f"L{ln}: {CAP_SHUNT} 在 {target_net} 上的行, node2={n2!r} "
                                   f"⇒ 必须等于它自己的网名 {target_net!r} (借了别的器件的裸位号)"})
    return {"ok": not hits, "hits": hits}


def crit_S2(idx, net_rows):
    """S2: C_VBUS_OUT 的串联端行, node2 必须是带 pin 提示的物理脚或自己的网名 (不许借 2 脚 C 的裸位号)"""
    hits = []
    pmap = idx["pins"].get(CAP_SERIES, {})
    target_nets = sorted({n for n in pmap.values() if n != GND_NET})
    rows = [(ln, r) for ln, r in net_rows
            if cell(r, "ref") == CAP_SERIES and cell(r, "net") in target_nets]
    if not rows:
        return {"ok": False, "hits": [{"detail": f"网表里找不到 {CAP_SERIES} 的信号端行"}]}
    for ln, r in rows:
        n2 = cell(r, "node2")
        if n2 and " " in n2:
            continue                      # 带 " pinN" ⇒ 物理脚, 合规
        if n2 == cell(r, "net"):
            continue                      # 自己的网名 ⇒ 合规
        if bare(n2) and n2 == cell(r, "ref"):
            continue                      # 本器件自己的端子标签 (合法写法)
        if bare(n2) and is_2pin_cap(idx, n2):
            hits.append({"line": ln, "net": cell(r, "net"), "node2": n2,
                         "detail": f"L{ln}: {CAP_SERIES} 的行 node2 借了 2 脚电容 {n2} 的裸位号"})
        elif bare(n2):
            hits.append({"line": ln, "net": cell(r, "net"), "node2": n2,
                         "detail": f"L{ln}: {CAP_SERIES} 的行 node2={n2!r} 既不是物理脚也不是自己的网名"})
    return {"ok": not hits, "hits": hits}


def crit_S3(idx, net_rows):
    """S3: FB_VBUS 的后级行 (第 2 脚所在网), node2 必须等于它自己的网名"""
    hits = []
    pmap = idx["pins"].get(BEAD, {})
    target_net = sorted({n for n in pmap.values()})[-1] if pmap else ""
    rows = [(ln, r) for ln, r in net_rows
            if cell(r, "ref") == BEAD and cell(r, "net") == target_net]
    if not rows:
        return {"ok": False, "hits": [{"detail": f"网表里找不到 {BEAD} 在 {target_net} 上的行"}]}
    for ln, r in rows:
        n2 = cell(r, "node2")
        if n2 != target_net:
            hits.append({"line": ln, "net": target_net, "node2": n2,
                         "detail": f"L{ln}: {BEAD} 在 {target_net} 上的行, node2={n2!r} "
                                   f"⇒ 必须等于它自己的网名 {target_net!r} (借了别的器件的裸位号)"})
    return {"ok": not hits, "hits": hits}


def crit_S4(idx, net_rows):
    """S4 (通用·等价 R3-A1): 每颗 2 脚 C 的裸位号登记次数 ≤ 脚表脚数"""
    hits = []
    for ref, pmap in idx["pins"].items():
        if not is_2pin_cap(idx, ref):
            continue
        occ = idx["regs"].get(ref, [])
        if len(occ) > len(pmap):
            hits.append({"ref": ref, "pins": len(pmap), "occ": len(occ),
                         "lines": [o["line"] for o in occ],
                         "detail": [f'L{o["line"]}: net={o["net"]} {o["slot"]}={ref} '
                                    f'(本行 ref={o["row_ref"]}) ⇒ {ref} 的端子被登记 {len(occ)} 次 '
                                    f'> 脚数 {len(pmap)}' for o in occ]})
    return {"ok": not hits, "hits": hits}


def crit_S5(idx, net_rows):
    """S5 (通用·等价 R3-A2): 2 脚 C 的行里, 对端是另一颗 2 脚 C 的裸位号且两颗同网 ⇒ 撞车"""
    hits = []
    for ln, r in net_rows:
        ref = cell(r, "ref")
        if not is_2pin_cap(idx, ref):
            continue
        net = cell(r, "net")
        own = idx["pins"].get(ref, {})
        if net not in own.values():
            continue
        for slot in ("node1", "node2"):
            v = cell(r, slot)
            if not bare(v) or v == ref:
                continue
            if not is_2pin_cap(idx, v):
                continue
            if net in idx["pins"].get(v, {}).values():
                hits.append({"line": ln, "net": net, "owner": ref, "peer": v,
                             "detail": f'L{ln}: net={net} ref={ref} 的对端裸位号={v} '
                                       f'⇒ {v} 与 {ref} 在脚表里同在 {net} 上 ⇒ 端子标签撞车'})
    return {"ok": not hits, "hits": hits}


def crit_S6(idx, net_rows):
    """S6 (反误报护栏): 器件↔器件直连里对方是 2 脚 R/L/D 的, 不得判红 (只回报, 不判红)"""
    legit = []
    for ln, r in net_rows:
        ref = cell(r, "ref")
        if not is_2pin_cap(idx, ref):
            continue
        for slot in ("node1", "node2"):
            v = cell(r, slot)
            if not bare(v) or v == ref:
                continue
            if is_2pin_passive(idx, v) and idx["types"].get(v) != "C":
                legit.append({"line": ln, "owner": ref, "peer": v,
                              "detail": f'L{ln}: {ref} ↔ {v} (2脚 {idx["types"].get(v)}) '
                                        f'= 合法器件↔器件直连 ⇒ 不得判红'})
    return {"ok": True, "hits": [], "legit": legit}


CRITERIA = [
    ("S1", "C_VBUS_GND 信号端行的 node2 == 它自己的网名", crit_S1),
    ("S2", "C_VBUS_OUT 串联端行的 node2 是物理脚或自己的网名", crit_S2),
    ("S3", "FB_VBUS 后级行的 node2 == 它自己的网名", crit_S3),
    ("S4", "通用: 每颗 2 脚 C 的端子登记次数 ≤ 脚表脚数 (等价 R3-A1)", crit_S4),
    ("S5", "通用: 2 脚 C 之间的裸位号对端撞车 (等价 R3-A2)", crit_S5),
    ("S6", "反误报护栏: 2 脚 R/L/D 直连不判红", crit_S6),
]


def analyze(csv_path=CSV_NET, pins_path=CSV_PINS):
    net_rows = read_rows(csv_path)
    pin_rows = read_rows(pins_path)
    idx = build_index(net_rows, pin_rows)
    res = {}
    for code, desc, fn in CRITERIA:
        r = fn(idx, net_rows)
        res[code] = {"desc": desc, "ok": bool(r.get("ok")),
                     "hits": r.get("hits", []), "legit": r.get("legit", [])}
    landed = all(res[c]["ok"] for c, _, _ in CRITERIA)
    return {"landed": landed, "criteria": res,
            "csv": csv_path, "pins": pins_path}


# ═══════════════════════════════════════════════════════════════════════════
# 2 · 文本级原地改写 (★自测用 · ★保证除目标字段外逐字节不变★)
# ═══════════════════════════════════════════════════════════════════════════
def _field_spans(line):
    """把一行 CSV 拆成 [(start, end)] 字段区间 (★尊重引号★)"""
    spans = []
    i = 0
    n = len(line)
    in_q = False
    start = 0
    while i < n:
        ch = line[i]
        if in_q:
            if ch == '"':
                if i + 1 < n and line[i + 1] == '"':
                    i += 2
                    continue
                in_q = False
        else:
            if ch == '"' and i == start:
                in_q = True
            elif ch == ",":
                spans.append((start, i))
                start = i + 1
        i += 1
    spans.append((start, n))
    return spans


def _split_line(line):
    """⇒ (fields, spans)"""
    spans = _field_spans(line)
    fields = []
    for a, b in spans:
        v = line[a:b]
        if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
            v = v[1:-1].replace('""', '"')
        fields.append(v)
    return fields, spans


def find_row(net_rows, ref, net):
    """⇒ [(line_no, row)]  (ref + net 精确定位, ★不依赖行号★)"""
    return [(ln, r) for ln, r in net_rows if cell(r, "ref") == ref and cell(r, "net") == net]


def patch_csv_col(src, dst, col, ref, net, new_value, expect_count=1):
    """把 CSV 里 `ref` 在 `net` 上的那一行的某一列 (col) 改成 `new_value`。

    ★**逐字节安全**: 只替换该字段的原始字节区间, 其余字符原样拷贝 ⇒ 别的列一个字节都不动 ★
    ★返回 (命中的行号列表, 实际替换次数) ★
    """
    with io.open(src, encoding="utf-8") as f:
        lines = f.read().split("\n")
    header = _split_line(lines[0])[0]
    try:
        i_ref = header.index("ref")
        i_net = header.index("net")
        i_col = header.index(col)
    except ValueError as exc:
        raise RuntimeError(f"CSV 缺列: {exc}")
    out = list(lines)
    hits = []
    count = 0
    for idx_ln in range(1, len(lines)):
        raw = lines[idx_ln]
        if not raw.strip():
            continue
        fields, spans = _split_line(raw)
        if len(fields) != len(header):
            continue
        if fields[i_ref].strip() != ref or fields[i_net].strip() != net:
            continue
        a, b = spans[i_col]
        out[idx_ln] = raw[:a] + new_value + raw[b:]
        hits.append(idx_ln + 1)
        count += 1
    if count != expect_count:
        raise RuntimeError(f"patch_csv_col: 期望命中 {expect_count} 行, 实际 {count} 行 "
                           f"(ref={ref} net={net} col={col}) ⇒ 判据行号变了, 拒绝落")
    with io.open(dst, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    return hits, count


def patch_csv_node2(src, dst, ref, net, new_value, expect_count=1):
    """★`node2` 列的特化版 (★F1 病灶就落在这个槽★)★"""
    return patch_csv_col(src, dst, "node2", ref, net, new_value, expect_count)


def copy_file(src, dst):
    shutil.copyfile(src, dst)
    return dst


# ═══════════════════════════════════════════════════════════════════════════
# 3 · 报告
# ═══════════════════════════════════════════════════════════════════════════
def render(res):
    o = []
    o.append("=" * 78)
    o.append("  ISS-247 · F1 落表判定门禁 (★语义判据 · 一个 md5 都不碰★)")
    o.append("=" * 78)
    o.append(f"  网表: {res['csv']}")
    o.append(f"  脚表: {res['pins']}")
    o.append("")
    for code, desc, _ in CRITERIA:
        c = res["criteria"][code]
        o.append(f"  {'✅' if c['ok'] else '❌'} {code}  {desc}")
        for h in c["hits"]:
            d = h.get("detail")
            if isinstance(d, list):
                for x in d[:8]:
                    o.append(f"        · {x}")
            elif d:
                o.append(f"        · {d}")
        if code == "S6" and c.get("legit"):
            o.append(f"        · (合法直连 {len(c['legit'])} 处, 不得判红)")
    o.append("")
    o.append("─" * 78)
    verdict = "✅ F1 已落表 (两颗 2 脚电容的端子标签不再撞车)" if res["landed"] \
        else "❌ F1 未落表 (★网表里 node2 槽仍借用了别的器件裸位号★)"
    o.append(f"  判定: {verdict}")
    o.append(f"  rc   = {0 if res['landed'] else 1}")
    o.append("─" * 78)
    return "\n".join(o)


# ═══════════════════════════════════════════════════════════════════════════
# 4 · 自测 (★≥5 条反向用例 · ★每条自证「真的改到了目标」★)
# ═══════════════════════════════════════════════════════════════════════════
def _mutate_l12(src, dst, node2_new):
    """把 C_VBUS_GND@VBUS_5V_CHG 行的 node2 改成 node2_new (src ⇒ dst)"""
    return patch_csv_node2(src, dst, CAP_SHUNT, "VBUS_5V_CHG", node2_new)


def _mutate_l8(src, dst, node2_new):
    """把 FB_VBUS@VBUS_5V_F1 行的 node2 改成 node2_new (src ⇒ dst)"""
    return patch_csv_node2(src, dst, BEAD, "VBUS_5V_F1", node2_new)


def _mutate_both_to_old(src, dst):
    """★把【两处病灶行】的 node2 一起改回旧值 (借来的裸位号 C_VBUS_OUT) ⇒ 复现「F1 未落表」基线★

    ★★2026-11-16 19:2x (ISS-249 · F1 已落表): 新增 ★
    ★**用途: 让 --selftest 的用例【不依赖盘上现状】** ⇒ 落表前跑 / 落表后跑 = 同一套断言 ★
    ★**原来的 T0 / T4 / T5 直接拿真文件当前状态当基线** ⇒ F1 一落表这三条就必红
      (T0 断言「现状必须红」· T4/T5 断言「只修一行 ⇒ 另一行仍红」但真文件已经修好了)
      ⇒ ★**这不是判据坏了, 是自证用例把【现状】写死了** ⇒ 本次改成「先显式复现旧基线, 再改」
      ⇒ ★**判据逻辑 (S1~S6) 一个字节没动** ★
    """
    tmp1 = dst + ".tmp1"
    h1, n1 = patch_csv_node2(src, tmp1, BEAD, "VBUS_5V_F1", "C_VBUS_OUT")
    h2, n2 = patch_csv_node2(tmp1, dst, CAP_SHUNT, "VBUS_5V_CHG", "C_VBUS_OUT")
    os.unlink(tmp1)
    return (h1, h2), (n1, n2)


def selftest():
    cases = []
    tmp = tempfile.mkdtemp(prefix="iss247_f1_")
    try:
        # ---------- T0 反向: ★fixture 显式回退成「落表前」⇒ 必须红 (★fixture 与活文件状态无关★) ----------
        #   ★★2026-11-16 19:2x (ISS-249 · main 19:3x 口径): 原 T0 断言「现状真文件必须红 (F1 未落表)」
        #     ⇒ F1 一落表, 活文件变绿 ⇒ 这条必红 (★fixture 起点被写死在「未落表」★)
        #   ★**改法 (main 口径): 把 fixture 显式回退成落表前的样子 (L8 的 VBUS_5V_F1 → C_VBUS_OUT
        #     · L12 的 VBUS_5V_CHG → C_VBUS_OUT), 再在回退后的副本上判红** ★
        #   ★**活文件的现状由【主模式】守 (默认模式 rc=0 ⇔ F1 已落表)** ⇒ 本条只管「坏态必红」 ★
        #   ⇒ ★**判据 (S1~S6) 一个字节没动** ⇒ ★**没有删任何断言, 只是把 fixture 起点改成状态无关** ★
        c0 = os.path.join(tmp, "t0.csv")
        b0, n0 = _mutate_both_to_old(CSV_NET, c0)
        r0 = analyze(c0, CSV_PINS)
        red0 = [code for code in ("S1", "S3", "S4", "S5") if not r0["criteria"][code]["ok"]]
        ok0 = (not r0["landed"]) and len(red0) == 4
        cases.append(("T0 fixture 回退成落表前 (L8/L12 都借 C_VBUS_OUT) ⇒ 期望红 (S1+S3+S4+S5 全红)",
                      ok0, f'回退行 L{b0[0]}/L{b0[1]} · 红判据={red0} · landed={r0["landed"]}', "反"))

        # ---------- T1 反向: L12 node2 改回 C_VBUS_OUT ----------
        c1 = os.path.join(tmp, "t1.csv")
        h1, n1 = _mutate_l12(CSV_NET, c1, "C_VBUS_OUT")
        r1 = analyze(c1, CSV_PINS)
        ok1 = (not r1["landed"]) and not r1["criteria"]["S5"]["ok"] \
            and not r1["criteria"]["S4"]["ok"]
        cases.append(("T1 把 C_VBUS_GND@VBUS_5V_CHG 的 node2 改回 C_VBUS_OUT ⇒ 期望红 (撞车+登记超脚数)",
                      ok1, f'改了 L{h1} (命中{n1}行) · landed={r1["landed"]} '
                            f'S4红={not r1["criteria"]["S4"]["ok"]} S5红={not r1["criteria"]["S5"]["ok"]}', "反"))

        # ---------- T2 反向: L12 node2 改成 C_VBUS_GND (★上一轮派单给的错值★) ----------
        c2 = os.path.join(tmp, "t2.csv")
        h2, n2 = _mutate_l12(CSV_NET, c2, "C_VBUS_GND")
        r2 = analyze(c2, CSV_PINS)
        s4_refs = [x.get("ref") for x in r2["criteria"]["S4"]["hits"]]
        ok2 = (not r2["landed"]) and (CAP_SHUNT in s4_refs)
        cases.append(("T2 把 node2 改成 C_VBUS_GND (★上一轮派单给的错值★) ⇒ 期望红 (一颗件登记 3 次)",
                      ok2, f'改了 L{h2} · S4 命中 ref={s4_refs} · landed={r2["landed"]}', "反"))

        # ---------- T3 反向: L8 node2 改回 C_VBUS_OUT ----------
        c3 = os.path.join(tmp, "t3.csv")
        h3, n3 = _mutate_l8(CSV_NET, c3, "C_VBUS_OUT")
        r3 = analyze(c3, CSV_PINS)
        s4_refs3 = [x.get("ref") for x in r3["criteria"]["S4"]["hits"]]
        ok3 = (not r3["landed"]) and (CAP_SERIES in s4_refs3) and not r3["criteria"]["S3"]["ok"]
        cases.append(("T3 把 FB_VBUS@VBUS_5V_F1 的 node2 改回 C_VBUS_OUT ⇒ 期望红 (登记 3 次)",
                      ok3, f'改了 L{h3} · S4 命中 ref={s4_refs3} · S3红={not r3["criteria"]["S3"]["ok"]}', "反"))

        # ---------- T4 反向: 先复现旧基线 (两行都借 C_VBUS_OUT), 再只修 L12 ⇒ S3 仍红 ----------
        c4 = os.path.join(tmp, "t4.csv")
        b4, n4 = _mutate_both_to_old(CSV_NET, c4)
        h4, _ = _mutate_l12(c4, os.path.join(tmp, "t4b.csv"), "VBUS_5V_CHG")
        r4 = analyze(os.path.join(tmp, "t4b.csv"), CSV_PINS)
        ok4 = (not r4["landed"]) and not r4["criteria"]["S3"]["ok"]
        cases.append(("T4 先复现旧基线再只修 L12 (L8 仍借 C_VBUS_OUT) ⇒ 期望红 (S3 仍红)",
                      ok4, f'旧基线行 L{b4[0]}/L{b4[1]} · 只改 L{h4} · S3红={not r4["criteria"]["S3"]["ok"]} · landed={r4["landed"]}', "反"))

        # ---------- T5 反向: 先复现旧基线 (两行都借 C_VBUS_OUT), 再只修 L8 ⇒ S1 仍红 ----------
        c5 = os.path.join(tmp, "t5.csv")
        b5, n5 = _mutate_both_to_old(CSV_NET, c5)
        h5, _ = _mutate_l8(c5, os.path.join(tmp, "t5b.csv"), "VBUS_5V_F1")
        r5 = analyze(os.path.join(tmp, "t5b.csv"), CSV_PINS)
        ok5 = (not r5["landed"]) and not r5["criteria"]["S1"]["ok"]
        cases.append(("T5 先复现旧基线再只修 L8 (L12 仍借 C_VBUS_OUT) ⇒ 期望红 (S1 仍红)",
                      ok5, f'旧基线行 L{b5[0]}/L{b5[1]} · 只改 L{h5} · S1红={not r5["criteria"]["S1"]["ok"]} · landed={r5["landed"]}', "反"))

        # ---------- T6 正向: 两行都按作业包改 ⇒ 必须绿 (★两种起点都测: 回退态 + 活文件态★) ----------
        #   ★★ISS-249 (main 口径「两种都测」): ① 回退态 + 两行都改对 ⇒ 绿  ② 活文件 (已落表) ⇒ 绿 ★
        c6 = os.path.join(tmp, "t6a.csv")
        b6, _ = _mutate_both_to_old(CSV_NET, c6)
        c6b = os.path.join(tmp, "t6b.csv")
        h6a, _ = _mutate_l12(c6, c6b, "VBUS_5V_CHG")
        c6c = os.path.join(tmp, "t6c.csv")
        h6b, _ = _mutate_l8(c6b, c6c, "VBUS_5V_F1")
        r6a = analyze(c6c, CSV_PINS)          # 起点①: 回退态 + 两行都改对
        r6b = analyze(CSV_NET, CSV_PINS)       # 起点②: 活文件 (F1 已落表)
        ok6 = r6a["landed"] and r6b["landed"]
        cases.append(("T6 ★正向: 两行都按作业包改 (L8→VBUS_5V_F1 · L12→VBUS_5V_CHG) ⇒ 期望绿 "
                      "(★两种起点都测: 回退态 + 活文件态★)",
                      ok6, f'回退态改对 L{h6a}+L{h6b} landed={r6a["landed"]} · 活文件态 landed={r6b["landed"]}', "正"))

        # ---------- T7 反向: 改一颗【无关】的 2 脚 C ⇒ 通用判据仍须抓到 ----------
        c7 = os.path.join(tmp, "t7.csv")
        h7, n7 = patch_csv_node2(CSV_NET, c7, "C_BULK_V_CORE", "V_CORE", "C_HF_V_CORE")
        r7 = analyze(c7, CSV_PINS)
        s4_refs7 = [x.get("ref") for x in r7["criteria"]["S4"]["hits"]]
        ok7 = (not r7["landed"]) and ("C_HF_V_CORE" in s4_refs7)
        cases.append(("T7 把【无关】的 C_BULK_V_CORE@V_CORE 的 node2 改成另一颗 2 脚 C ⇒ 期望红 "
                      "(证明判据是通用的, 不是只认两颗点名电容)",
                      ok7, f'改了 L{h7} · S4 命中 ref={s4_refs7} · landed={r7["landed"]}', "反"))

        # ---------- T8 反向: 改脚表 (C_VBUS_GND 的信号脚被抹掉) ⇒ 必须红 ----------
        c8 = os.path.join(tmp, "t8_pins.csv")
        h8, n8 = patch_csv_col(CSV_PINS, c8, "net", CAP_SHUNT, "VBUS_5V_CHG", "GND")
        r8 = analyze(CSV_NET, c8)
        ok8 = (not r8["landed"]) and not r8["criteria"]["S1"]["ok"]
        cases.append(("T8 把脚表里 C_VBUS_GND 的信号脚改成 GND ⇒ 期望红 (S1: 脚表缺一根信号脚)",
                      ok8, f'改了脚表 L{h8} · S1红={not r8["criteria"]["S1"]["ok"]} · landed={r8["landed"]}', "反"))

        # ---------- T9 反误报: 合法器件↔器件直连 (2 脚 R) 不得判红 ----------
        c9 = os.path.join(tmp, "t9a.csv")
        c9b = os.path.join(tmp, "t9b.csv")
        h9a, _ = _mutate_l12(CSV_NET, c9, "VBUS_5V_CHG")
        h9b, _ = _mutate_l8(c9, c9b, "VBUS_5V_F1")
        r9 = analyze(c9b, CSV_PINS)
        legit9 = r9["criteria"]["S6"]["legit"]
        ok9 = r9["landed"] and len(legit9) >= 1
        cases.append(("T9 反误报: 已修好的副本里, 合法器件↔器件直连 (2脚R) 存在且**不**判红",
                      ok9, f'改了 L{h9a}+L{h9b} · S6 记下合法直连 {len(legit9)} 处 · landed={r9["landed"]}', "正"))

        # ---------- T10 反向: C_VBUS_OUT 的串联端行 node2 借 2 脚 C 裸位号 ⇒ 必须红 ----------
        c10 = os.path.join(tmp, "t10.csv")
        h10, _ = patch_csv_node2(CSV_NET, c10, CAP_SERIES, "VBUS_5V_CHG", CAP_SHUNT)
        r10 = analyze(c10, CSV_PINS)
        ok10 = (not r10["landed"]) and not r10["criteria"]["S2"]["ok"]
        cases.append(("T10 把 C_VBUS_OUT@VBUS_5V_CHG 的 node2 改成 C_VBUS_GND ⇒ 期望红 (S2 撞车)",
                      ok10, f'改了 L{h10} · S2红={not r10["criteria"]["S2"]["ok"]} · landed={r10["landed"]}', "反"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    out = []
    out.append("=" * 78)
    out.append("  --selftest 反向用例自证 (ISS-247 · F1 落表判定)")
    out.append("=" * 78)
    npass = 0
    for name, ok, det, kind in cases:
        out.append(f"  {'✅' if ok else '❌'} {name}")
        out.append(f"       {det}")
        if ok:
            npass += 1
    nrev = len([c for c in cases if c[3] == "反"])   # 反向用例 (必须抓到红)
    npos = len([c for c in cases if c[3] == "正"])   # 正向用例 (必须绿)
    out.append("-" * 78)
    out.append(f"  用例 {len(cases)} 条 · 通过 {npass} 条 · 失败 {len(cases) - npass} 条")
    out.append(f"  ★其中反向用例 (必须抓到红) {nrev} 条 ★ 正向用例 {npos} 条 (改对 ⇒ 绿 + 反误报 ⇒ 绿)")
    out.append("  ★**fixture 与活文件状态无关** (T0/T4/T5 先显式回退成落表前) ⇒ 落表前跑 / 落表后跑 = 同一套断言 ★")
    out.append(f"  结论: {'✅ 全抓到' if npass == len(cases) else '❌ 有用例没抓到'}"
               f"  ·  rc = {0 if npass == len(cases) else 1}")
    out.append("=" * 78)
    return "\n".join(out), npass == len(cases)


# ═══════════════════════════════════════════════════════════════════════════
# 5 · main
# ═══════════════════════════════════════════════════════════════════════════
def main(argv=None):
    ap = argparse.ArgumentParser(description="ISS-247 · F1 落表判定门禁 (语义判据)")
    ap.add_argument("--csv", default=CSV_NET)
    ap.add_argument("--pins", default=CSV_PINS)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--expect-landed", action="store_true",
                    help="rc=0 ⇔ F1 已落表 (默认模式)")
    ap.add_argument("--expect-not-landed", action="store_true",
                    help="rc=0 ⇔ F1 还没落表 (现状守卫)")
    a = ap.parse_args(argv)

    if a.selftest:
        txt, ok = selftest()
        print(txt)
        return 0 if ok else 1

    res = analyze(a.csv, a.pins)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(render(res))
    if a.expect_not_landed:
        return 0 if not res["landed"] else 1
    return 0 if res["landed"] else 1


if __name__ == "__main__":
    sys.exit(main())
