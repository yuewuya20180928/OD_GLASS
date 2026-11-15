#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-211 机器门禁 —— ★**网表自身一致性 4 处缺陷的「现状守卫」** ★
================================================================================
★**它不是"检查网表对不对", 是"检查【规格页】跟【现行网表】还对不对得上"** ★

★★**它守的是三件事 (★规格页 ⇄ 本脚本 ⇄ 现行文件 三方对齐★)** ★★

  ① **判据 a (规格页 ⇄ 现行文件)**: `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` 里
     ★**逐字引用**的 4 条缺陷现状 (行号 + 关键字段) 必须与现行
     `HW/netlist_v1.csv` / `HW/netlist_v1_pins.csv` / `HW/BOM_v1.csv` /
     `HW/SCHEMATIC_V1_SPEC.json` / `HW/PCB/demo_mainboard.kicad_pcb` **完全一致**
     ⇒ 对不上 = 网表被静默改过 = **红**
  ② **判据 b (BOM 现状断言)**: `HW/BOM_v1.csv` 里 `U_EN_SW` 行的 `type` 仍是 `NET`
     (★现状断言, 让它别被悄悄"修好"而规格页不跟★)
  ③ **判据 c (不该改错的锚点仍在)**: 4 条各自的"锚"必须还在原位
     (★例: L169 note 里那句"已作废"还在 / L182 的 `dnp=DNP` 还在 / ★
     `U_EN_SW` 在表A/表B 仍然 0 条 `type!=NET` 的器件本体行 / ★
     `D_ESD_USB_D` 仍然只有 2 个焊盘且 D− 那条路仍然 0 个 ESD 位号★)

★★**rc 语义 (★重要: 现在 rc=0 不等于"网表没问题"★)** ★★
  - `rc=0` ⇒ ★**现状与规格页一致** (★即 4 条缺陷**仍在**, 这是预期状态★)
  - `rc=1` ⇒ 不一致, 并**点名**是哪一条 (哪个 key / 哪一行 / 哪个字段对不上)
  - `rc=2` ⇒ 用法/环境错误 (文件缺失等)
  - ★**门禁是【现状守卫】不是【合格证】**: 现在 4 条缺陷仍在 ⇒ 门禁应当是绿的 ⇒
    ★**等它们随"整链重出 第 1 步"那一趟落表后, 用 `--expect-resolved` 翻成
    "缺陷已消失"口径 (★翻面条件写在 `HW/NETLIST_SELF_CONSISTENCY_SPEC.md` §⑤★)★

★★**三条纪律 (★别踩★)** ★★
  - ★**只读**: 本脚本不写任何项目文件 (自检只动临时目录里的副本) ★
  - ★**不改网表 / 不改板 / 不改生成器** ⇒ 本脚本只**看**, 只**判** ★
  - ★**受保护 md5 必须逐字节不变** (网表 `c78f9912…` / 脚表 `4814617e…` / ★
    板 `611b869e…` / `.kicad_pro` `3e504d2b…`) ⇒ 本脚本**一个字节都不碰** ★

用法:
    python3 HW/check_netlist_selfconsistency.py              # 现状守卫 (现在应 rc=0)
    python3 HW/check_netlist_selfconsistency.py --verbose    # 打印逐条锚点明细
    python3 HW/check_netlist_selfconsistency.py --expect-resolved   # 翻面口径 (落表后 rc=0)
    python3 HW/check_netlist_selfconsistency.py --selftest   # 反向用例 (改临时副本 ⇒ 必须变红)
    python3 HW/check_netlist_selfconsistency.py --root DIR   # 指定工程根 (自检/复现用)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.dirname(HERE)  # HW/ 的上一级 = 工程根

REL = {
    "netlist": os.path.join("HW", "netlist_v1.csv"),
    "pins": os.path.join("HW", "netlist_v1_pins.csv"),
    "bom": os.path.join("HW", "BOM_v1.csv"),
    "spec": os.path.join("HW", "SCHEMATIC_V1_SPEC.json"),
    "board": os.path.join("HW", "PCB", "demo_mainboard.kicad_pcb"),
    "specpage": os.path.join("HW", "NETLIST_SELF_CONSISTENCY_SPEC.md"),
}

# ─────────────────────────────────────────────────────────────────────────────
# ★★ 期望值 (★唯一真源: 规格页的锚点表必须与这里逐字一致★) ★★
# ★格式: (key, file, line, check) ★
#   file : netlist | pins | bom | spec | board | specpage
#   line : 物理行号 (1-based, 表头 = 第 1 行) · 特殊: "?" = 不限行号 (按谓词找)
#   check: ★迷你判据 DSL★ ★
#     "field == value"              CSV 列值逐字相等
#     "field contains value"        CSV 列值包含子串
#     "count(<pred>) == N"          谓词命中行数 (pred 形如 "ref==X&type!=NET")
#     "footprint.<REF>.<attr> == v" 板封装属性 (value | pads | pad1.net | pad2.net | pad3.net)
#     "spec.<path> == value"        SCHEMATIC_V1_SPEC.json 里的字段 (connections[id=B-01].level)
#     "esd_on_net(<netA>,<netB>) == N"  板上带 ESD 的位号里, 焊盘挂在这两条网上的个数
# ─────────────────────────────────────────────────────────────────────────────

EXPECT: list[tuple[str, str, str, str]] = [
    # ── 第 (1) 条: I2C_A 上拉 —— NET 行说 4.7k/3.3V, 器件行说 2.2k/1.8V ──
    ("d1_a167_value", "netlist", "167", "value == 上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF)"),
    ("d1_a167_ref", "netlist", "167", "ref == NET_I2C_A_SCL"),
    ("d1_a168_value", "netlist", "168", "value == 上拉 4.7k 到 3.3V"),
    ("d1_a168_ref", "netlist", "168", "ref == NET_I2C_A_SDA"),
    ("d1_a169_value", "netlist", "169", "value == 2.2k ±1%"),
    ("d1_a169_net", "netlist", "169", "net == VDD_1V8_IO"),
    ("d1_a169_ref", "netlist", "169", "ref == R_PU_I2CA_SCL"),
    ("d1_a169_note", "netlist", "169", "note contains 已作废"),
    ("d1_a170_value", "netlist", "170", "value == 2.2k ±1%"),
    ("d1_a170_net", "netlist", "170", "net == VDD_1V8_IO"),
    ("d1_a171_value", "netlist", "171", "value contains 上拉 2.2k 到 1.8V"),
    ("d1_b367_net", "pins", "367", "net == I2C_A_SCL"),
    ("d1_b368_net", "pins", "368", "net == VDD_1V8_IO"),
    ("d1_spec_b01_level", "spec", "?", "spec.connections[id=B-01].level == 3.3V"),
    ("d1_spec_b01_imp", "spec", "?", "spec.connections[id=B-01].imp == 上拉 4.7k 到 3.3V (灌 702µA, t_r=2.38µs@100pF)"),
    ("d1_spec_b02_level", "spec", "?", "spec.connections[id=B-02].level == 3.3V"),
    ("d1_spec_b02_imp", "spec", "?", "spec.connections[id=B-02].imp == 上拉 4.7k 到 3.3V"),

    # ── 第 (2) 条: BAT_DET 分压链全 DNP, 但 SoC ADC 输入脚必装 ──
    ("d2_a181_ref", "netlist", "181", "ref == NET_BAT_DET"),
    ("d2_a181_dnp", "netlist", "181", "dnp == 必装"),
    ("d2_a182_ref", "netlist", "182", "ref == R_BAT_DET_1"),
    ("d2_a182_dnp", "netlist", "182", "dnp == DNP"),
    ("d2_a182_value", "netlist", "182", "value == 1M ±1%"),
    ("d2_a182_note", "netlist", "182", "note contains DNP: 同上"),
    ("d2_a183_ref", "netlist", "183", "ref == R_BAT_DET_2"),
    ("d2_a183_dnp", "netlist", "183", "dnp == DNP"),
    ("d2_a184_ref", "netlist", "184", "ref == C_DET_BAT"),
    ("d2_a184_dnp", "netlist", "184", "dnp == DNP"),
    ("d2_a185_ref", "netlist", "185", "ref == C_DET_BAT"),
    ("d2_a185_dnp", "netlist", "185", "dnp == DNP"),
    ("d2_a186_node1", "netlist", "186", "node1 == J_SOM_P1 pin38"),
    ("d2_a186_dnp", "netlist", "186", "dnp == 必装"),
    ("d2_a186_note", "netlist", "186", "note contains [BAT_DET] SoC ADC 输入节点"),
    ("d2_b307_dnp", "pins", "307", "dnp == DNP"),
    ("d2_b309_dnp", "pins", "309", "dnp == DNP"),
    ("d2_b100_dnp", "pins", "100", "dnp == DNP"),
    ("d2_b210_net", "pins", "210", "net == BAT_DET"),

    # ── 第 (3) 条: U_EN_SW 没有器件本体行 ⇒ BOM 把它登记成 NET 行 ──
    ("d3_a441_type", "netlist", "441", "type == NET"),
    ("d3_a441_value", "netlist", "441", "value == EN 输入 (高=放行底板)"),
    ("d3_a442_type", "netlist", "442", "type == NET"),
    ("d3_a443_type", "netlist", "443", "type == NET"),
    ("d3_a444_type", "netlist", "444", "type == NET"),
    ("d3_a_rows", "netlist", "?", "count(ref==U_EN_SW) == 4"),
    ("d3_a_body", "netlist", "?", "count(ref==U_EN_SW&type!=NET) == 0"),
    ("d3_b_rows", "pins", "?", "count(ref==U_EN_SW) == 4"),
    ("d3_b_body", "pins", "?", "count(ref==U_EN_SW&type!=NET) == 0"),
    ("d3_bom208_type", "bom", "208", "type == NET"),
    ("d3_bom208_value", "bom", "208", "value == EN 输入 (高=放行底板)"),
    ("d3_board_value", "board", "?", "footprint.U_EN_SW.value == EN 输入 (高=放行底板)"),
    ("d3_board_pads", "board", "?", "footprint.U_EN_SW.pads == 4"),
    ("d3_ctrl_a50_type", "netlist", "50", "type == IC"),

    # ── 第 (4) 条: USB D− 全程无 ESD, 而 D_ESD_USB_D 自称"双通道" ──
    ("d4_a417_value", "netlist", "417", "value == ESD 阵列 [待选型] (USB 2.0 双通道)"),
    ("d4_a417_net", "netlist", "417", "net == USB_D_P_SRC"),
    ("d4_a417_dnp", "netlist", "417", "dnp == 必装"),
    ("d4_a417_note", "netlist", "417", "note contains Forlinx 载板指引要求 ESD 紧贴接口"),
    ("d4_a418_value", "netlist", "418", "value == ESD 阵列 [待选型]"),
    ("d4_a432_net", "netlist", "432", "net == NET_USB_D_N_TYPEC"),
    ("d4_a432_ref", "netlist", "432", "ref == R_SER_USB_D_N"),
    ("d4_esd_pads", "board", "?", "footprint.D_ESD_USB_D.pads == 2"),
    ("d4_esd_value", "board", "?", "footprint.D_ESD_USB_D.value == ESD 阵列 [待选型] (USB 2.0 双通道)"),
    ("d4_esd_pad1_net", "board", "?", "footprint.D_ESD_USB_D.pad1.net == USB_D_P_SRC"),
    ("d4_esd_pad2_net", "board", "?", "footprint.D_ESD_USB_D.pad2.net == GND"),
    ("d4_esd_on_dminus", "board", "?", "esd_on_net(USB_D_N_SRC,NET_USB_D_N_TYPEC) == 0"),
    ("d4_bom62_value", "bom", "62", "value == ESD 阵列 [待选型] (USB 2.0 双通道)"),
    ("d4_bom62_fp", "bom", "62", "footprint contains 2 焊盘"),
]


class CheckError(Exception):
    """rc=2: 环境/用法错误"""


# ─────────────────────────────────────────────────────────────────────────────
# 读文件
# ─────────────────────────────────────────────────────────────────────────────

def _path(root: str, key: str) -> str:
    return os.path.join(root, REL[key])


def _read_rows(path: str) -> list[dict]:
    """带行号 (CSV 物理行号, 1-based, 表头 = 第 1 行) 的读取。"""
    if not os.path.exists(path):
        raise CheckError(f"★缺文件: {path}")
    with open(path, encoding="utf-8", newline="") as fh:
        raw = fh.read()
    rows = list(csv.reader(raw.split("\n")))
    while rows and rows[-1] == []:
        rows.pop()
    if not rows:
        raise CheckError(f"★空文件: {path}")
    head = rows[0]
    out = []
    for i, r in enumerate(rows[1:]):
        if len(r) != len(head):
            # 列数不齐的行仍然读进来, 缺的补空串 (便于报告)
            r = r + [""] * (len(head) - len(r))
        d = dict(zip(head, r))
        d["_line"] = i + 2
        out.append(d)
    return out


def _read_json(path: str):
    if not os.path.exists(path):
        raise CheckError(f"★缺文件: {path}")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _read_board(path: str) -> dict:
    """解析板文件: {ref: {"value":…, "pads":N, "padN.net":…}}。只读。"""
    if not os.path.exists(path):
        raise CheckError(f"★缺文件: {path}")
    with open(path, encoding="utf-8") as fh:
        s = fh.read()
    out: dict[str, dict] = {}
    for m in re.finditer(r"\(footprint ", s):
        i = m.start()
        depth = 0
        j = i
        while j < len(s):
            if s[j] == "(":
                depth += 1
            elif s[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        blk = s[i:j + 1]
        rm = re.search(r'\(property "Reference" "([^"]*)"', blk)
        if not rm:
            continue
        ref = rm.group(1)
        if ref in out:
            continue
        vm = re.search(r'\(property "Value" "([^"]*)"', blk)
        pads = []
        for pm in re.finditer(r'\(pad "([^"]*)"', blk):
            num = pm.group(1)
            rest = blk[pm.end():pm.end() + 1200]
            nm = re.search(r'\(net "([^"]*)"\)', rest)
            pads.append((num, nm.group(1) if nm else ""))
        info = {"value": vm.group(1) if vm else "", "pads": len(pads), "pads_list": pads}
        for idx, (_num, net) in enumerate(pads, start=1):
            info[f"pad{idx}.net"] = net
        out[ref] = info
    return out


# ─────────────────────────────────────────────────────────────────────────────
# 迷你判据 DSL 求值
# ─────────────────────────────────────────────────────────────────────────────

def _norm(s: str) -> str:
    return (s or "").strip()


def _split_call(check: str, name: str) -> tuple[str, str]:
    """把 'name(<参数>) == <期望>' 拆成 (<参数>, <期望>)。★谓词里可能含 '==', 所以按括号配平拆★"""
    idx = check.index("(")
    depth = 0
    for j in range(idx, len(check)):
        if check[j] == "(":
            depth += 1
        elif check[j] == ")":
            depth -= 1
            if depth == 0:
                break
    else:
        raise CheckError(f"★判据括号不配平: {check!r}")
    pred = check[idx + 1:j]
    rhs = check[j + 1:].strip()
    if not rhs.startswith("=="):
        raise CheckError(f"★判据缺 '==': {check!r}")
    return pred, rhs[2:].strip()


def _eval_check(ctx: dict, check: str) -> tuple[bool, str]:
    """返回 (ok, 实际值文本)。"""
    check = check.strip()

    # ★"field contains value" (★必须先判, 因为它不含 '==')
    cm = re.match(r"^(\w+)\s+contains\s+(.*)$", check)
    if cm:
        field, want = cm.group(1), cm.group(2).strip()
        got = _norm(ctx.get("row", {}).get(field, ""))
        return want in got, f"{field}={got!r}"

    # ★count(<pred>) == N  (★必须先判: 谓词里含 '==', 不能用朴素的 split★)
    if check.startswith("count("):
        pred, want = _split_call(check, "count")
        rows = ctx["rows"]
        n = 0
        for r in rows:
            ok = True
            for term in pred.split("&"):
                term = term.strip()
                if not term:
                    continue
                if "!=" in term:
                    f, v = term.split("!=", 1)
                    if _norm(r.get(f, "")) == _norm(v):
                        ok = False
                        break
                elif "==" in term:
                    f, v = term.split("==", 1)
                    if _norm(r.get(f, "")) != _norm(v):
                        ok = False
                        break
            if ok:
                n += 1
        return str(n) == want, f"count={n}"

    if "==" not in check:
        return False, f"★判据写法不认识: {check!r}"
    lhs, rhs = check.split("==", 1)
    lhs = lhs.strip()
    rhs = rhs.strip()
    want = rhs

    # count(<pred>) == N  (★已在上头单独处理, 这里不该再到★)
    if lhs.startswith("count("):
        return False, f"★count 判据解析失败: {check!r}"

    # footprint.<REF>.<attr> == v
    if lhs.startswith("footprint."):
        body = lhs[len("footprint."):]
        ref, _, attr = body.partition(".")
        fps = ctx["board"]
        if ref not in fps:
            return False, f"★板文件里没有位号 {ref!r}"
        info = fps[ref]
        if attr == "pads":
            return str(info["pads"]) == want, f"pads={info['pads']}"
        if attr == "value":
            return _norm(info["value"]) == want, f"value={info['value']!r}"
        if attr.endswith(".net"):
            got = info.get(attr, "")
            return _norm(got) == want, f"{attr}={got!r}"
        return False, f"★板属性不认识: {attr!r}"

    # spec.<path> == v
    if lhs.startswith("spec."):
        path = lhs[len("spec."):]
        obj = ctx["spec"]
        m = re.fullmatch(r"connections\[id=([^\]]+)\]\.(\w+)", path)
        if m:
            cid, field = m.group(1), m.group(2)
            hit = [c for c in obj.get("connections", []) if c.get("id") == cid]
            if not hit:
                return False, f"★SPEC.json 里没有 connections id={cid!r}"
            got = hit[0].get(field, "")
            return _norm(got) == want, f"{path}={got!r}"
        # 普通点路径
        cur = obj
        for part in path.split("."):
            if isinstance(cur, dict):
                cur = cur.get(part, "")
            else:
                return False, f"★SPEC 路径走不通: {path}"
        return _norm(cur) == want, f"{path}={cur!r}"

    # esd_on_net(<netA>,<netB>) == N
    if lhs.startswith("esd_on_net("):
        body = lhs[len("esd_on_net("):]
        body = body[:-1] if body.endswith(")") else body
        nets = {n.strip() for n in body.split(",") if n.strip()}
        fps = ctx["board"]
        n = 0
        for ref, info in fps.items():
            if "ESD" not in ref.upper():
                continue
            for _num, net in info.get("pads_list", []):
                if net in nets:
                    n += 1
                    break
        return str(n) == want, f"esd_on_net={n}"

    # 普通列比较
    field = lhs
    if field == "count":
        return False, "★count 判据要写成 count(...)"
    got = _norm(ctx.get("row", {}).get(field, ""))
    return got == want, f"{field}={got!r}"


def _parse_contains(check: str) -> tuple[str, str] | None:
    m = re.match(r"^(\w+)\s+contains\s+(.*)$", check)
    if m:
        return m.group(1), m.group(2).strip()
    return None


# ─────────────────────────────────────────────────────────────────────────────
# 规格页锚点表 (判据 a 的另一半: 规格页 ⇄ 本脚本)
# ─────────────────────────────────────────────────────────────────────────────

ANCHOR_ROW_RE = re.compile(r"^\|\s*([a-z0-9_]+)\s*\|\s*([a-z]+)\s*\|\s*(\d+|\?)\s*\|\s*(.+?)\s*\|\s*$")
ANCHOR_BEGIN = "<!-- ANCHORS:BEGIN -->"
ANCHOR_END = "<!-- ANCHORS:END -->"


def parse_spec_anchors(path: str) -> dict[str, tuple[str, str, str]]:
    if not os.path.exists(path):
        raise CheckError(f"★缺文件: {path}")
    with open(path, encoding="utf-8") as fh:
        txt = fh.read()
    if ANCHOR_BEGIN not in txt or ANCHOR_END not in txt:
        raise CheckError(f"★规格页里没有锚点表 (需要 {ANCHOR_BEGIN} … {ANCHOR_END})")
    body = txt.split(ANCHOR_BEGIN, 1)[1].split(ANCHOR_END, 1)[0]
    out: dict[str, tuple[str, str, str]] = {}
    for line in body.split("\n"):
        if not line.strip().startswith("|"):
            continue
        m = ANCHOR_ROW_RE.match(line.strip())
        if not m:
            continue
        key, f, line_no, chk = m.group(1), m.group(2), m.group(3), m.group(4)
        out[key] = (f, line_no, chk)
    return out


def emit_anchor_table() -> str:
    """把 EXPECT 渲染成规格页用的 markdown 锚点表。"""
    lines = ["| key | file | line | check |", "|---|---|---|---|"]
    for key, f, ln, chk in EXPECT:
        lines.append(f"| {key} | {f} | {ln} | {chk} |")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 主检查
# ─────────────────────────────────────────────────────────────────────────────

def _row_at(rows: list[dict], line_no: str) -> dict:
    if line_no == "?":
        return {}
    n = int(line_no)
    for r in rows:
        if r["_line"] == n:
            return r
    raise CheckError(f"★行号 {n} 不在 {len(rows)} 行里 (文件被截断?)")


def check_guard(root: str, verbose: bool) -> tuple[int, list[str]]:
    """现状守卫: 规格页 ⇄ 本脚本 ⇄ 现行文件 三方对齐。"""
    errors: list[str] = []
    report: list[str] = []

    specpage = _path(root, "specpage")
    anchors = parse_spec_anchors(specpage)

    # ---- ① 规格页锚点表 ⇄ 本脚本 EXPECT (不许漂移) ----
    exp_map = {k: (f, ln, chk) for k, f, ln, chk in EXPECT}
    for key, want in exp_map.items():
        if key not in anchors:
            errors.append(f"★规格页锚点表里**缺** {key!r} ⇒ 规格页与门禁脚本漂移了")
    for key, got in anchors.items():
        if key not in exp_map:
            errors.append(f"★规格页锚点表里**多** {key!r} (脚本里没有) ⇒ 规格页与门禁脚本漂移了")
        elif got != exp_map[key]:
            errors.append(
                f"★锚点 {key!r} 规格页={got!r} ≠ 脚本={exp_map[key]!r} ⇒ 规格页与门禁脚本漂移了")

    # ---- ② 现行文件 ⇄ EXPECT ----
    ctx_common: dict = {"spec": _read_json(_path(root, "spec")),
                         "board": _read_board(_path(root, "board"))}
    cache: dict[str, list[dict]] = {}

    def rows_of(kind: str) -> list[dict]:
        if kind not in cache:
            cache[kind] = _read_rows(_path(root, kind))
        return cache[kind]

    for key, f, ln, chk in EXPECT:
        ctx = dict(ctx_common)
        if f in ("netlist", "pins", "bom"):
            ctx["rows"] = rows_of(f)
            ctx["row"] = _row_at(ctx["rows"], ln)
        ok, actual = _eval_check(ctx, chk)
        if not ok:
            errors.append(
                f"★[{key}] {REL[f]}:{ln} 判据 {chk!r} 不成立 (实际 {actual}) "
                f"⇒ 现状与规格页不符 (网表被静默改过? 或规格页没跟)")
        if verbose:
            report.append(f"   {'OK  ' if ok else 'FAIL'} {key:<18} {REL[f]}:{ln:<5} {chk}")

    # ---- ③ 报告项 (不判红, 只打印): ESD 到 J_USB_C 的几何距离 ----
    try:
        import math
        fps = ctx_common["board"]
        if "J_USB_C" in fps and "D_ESD_USB_D" in fps:
            # 板文件里 (at x y) 是封装原点; 这里用 ref→原点坐标
            coords = _board_ref_xy(_path(root, "board"))
            if "J_USB_C" in coords and "D_ESD_USB_D" in coords:
                a = coords["J_USB_C"]
                b = coords["D_ESD_USB_D"]
                d = math.hypot(a[0] - b[0], a[1] - b[1])
                report.append(f"   [报告项] D_ESD_USB_D → J_USB_C 板面距离 = {d:.2f} mm "
                              f"(★规格页 §①(4) 引的就是这个数★)")
    except Exception as exc:  # 报告项失败不许影响 rc
        report.append(f"   [报告项] 距离计算跳过: {exc}")

    if verbose:
        report.append("── 判据 b: BOM 里 U_EN_SW 的 type 仍是 NET (现状断言) ──")
        report.append("   (见上方 d3_bom208_type / d3_bom208_value)")

    return (1 if errors else 0), errors + report


def _board_ref_xy(path: str) -> dict:
    """ref → 封装原点 (x, y)。只读。"""
    with open(path, encoding="utf-8") as fh:
        s = fh.read()
    out: dict[str, tuple[float, float]] = {}
    for m in re.finditer(r"\(footprint ", s):
        i = m.start()
        depth = 0
        j = i
        while j < len(s):
            if s[j] == "(":
                depth += 1
            elif s[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        blk = s[i:j + 1]
        rm = re.search(r'\(property "Reference" "([^"]*)"', blk)
        am = re.search(r"\(at (-?[\d.]+) (-?[\d.]+)", blk)
        if rm and am and rm.group(1) not in out:
            out[rm.group(1)] = (float(am.group(1)), float(am.group(2)))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# 翻面口径 (--expect-resolved): 4 条缺陷必须已经消失
# ─────────────────────────────────────────────────────────────────────────────

def _parse_res(s: str) -> float | None:
    """'1M' / '100k' / '220Ω' → 欧姆。"""
    s = (s or "").strip()
    m = re.search(r"([\d.]+)\s*([kKMmRrΩ]|ohm)?", s)
    if not m:
        return None
    try:
        v = float(m.group(1))
    except ValueError:
        return None
    unit = (m.group(2) or "").lower()
    if unit in ("k", "kohm", "kω"):
        v *= 1e3
    return v


def check_resolved(root: str, verbose: bool) -> tuple[int, list[str]]:
    """翻面口径: 4 条缺陷都已随整链重出落表。"""
    errors: list[str] = []
    report: list[str] = []
    net = _read_rows(_path(root, "netlist"))
    pins = _read_rows(_path(root, "pins"))
    bom = _read_rows(_path(root, "bom"))
    spec = _read_json(_path(root, "spec"))
    board = _read_board(_path(root, "board"))

    # ---- R1: I2C_A 上拉 —— NET 行必须与器件行一致 (2.2k / 1.8V) ----
    stale = [r for r in net if "4.7k 到 3.3V" in (r.get("value") or "")
             or "2.38µs" in (r.get("value") or "")]
    if stale:
        errors.append(
            f"★R1 未落表: 仍有 {len(stale)} 行写着『4.7k 到 3.3V / 2.38µs』 "
            f"(行 {[r['_line'] for r in stale]}) ⇒ L167/L168 的过期注记还在")
    for cid in ("B-01", "B-02"):
        hit = [c for c in spec.get("connections", []) if c.get("id") == cid]
        if not hit:
            errors.append(f"★R1 未落表: SPEC.json 里没有 connections id={cid}")
            continue
        c = hit[0]
        if _norm(c.get("level")) == "3.3V":
            errors.append(f"★R1 未落表: SPEC.json {cid}.level 仍是 3.3V")
        if "4.7k" in (c.get("imp") or ""):
            errors.append(f"★R1 未落表: SPEC.json {cid}.imp 仍含 4.7k")
        if "2.2k" not in (c.get("imp") or ""):
            errors.append(f"★R1 未落表: SPEC.json {cid}.imp 里没有 2.2k")
        if "1.8V" not in (c.get("imp") or "") and "1.8" not in (c.get("imp") or ""):
            errors.append(f"★R1 未落表: SPEC.json {cid}.imp 里没有 1.8V 口径")
    for r in net:
        if _norm(r.get("ref")) in ("NET_I2C_A_SCL", "NET_I2C_A_SDA"):
            v = r.get("value") or ""
            if "2.2k" not in v:
                errors.append(f"★R1 未落表: 表A 行 {r['_line']} 的 NET 行 value 还没改成 2.2k 口径")
    if verbose:
        report.append("   R1 (I2C_A 上拉注记) 检查完毕")

    # ---- R2: BAT_DET 分压链必须实装, 且分压后电压要进得了 1.8V 域 ADC ----
    for ref in ("R_BAT_DET_1", "R_BAT_DET_2", "C_DET_BAT"):
        rows = [r for r in net if _norm(r.get("ref")) == ref]
        if not rows:
            errors.append(f"★R2 未落表: 表A 里没有 {ref}")
            continue
        for r in rows:
            if _norm(r.get("dnp")) == "DNP":
                errors.append(f"★R2 未落表: {ref} 仍是 DNP (表A 行 {r['_line']})")
        rows_b = [r for r in pins if _norm(r.get("ref")) == ref]
        for r in rows_b:
            if _norm(r.get("dnp")) == "DNP":
                errors.append(f"★R2 未落表: {ref} 在脚表里仍是 DNP (行 {r['_line']})")
    top = _parse_res(next((r.get("value") or "" for r in net
                           if _norm(r.get("ref")) == "R_BAT_DET_1"), ""))
    bot = _parse_res(next((r.get("value") or "" for r in net
                           if _norm(r.get("ref")) == "R_BAT_DET_2"), ""))
    if top and bot and top > 0 and bot > 0:
        vbat_max = 4.2   # 1S 锂电满充 (HW/INTERFACE_TABLE.md C-03)
        vnode = vbat_max * bot / (top + bot)
        if vnode > 1.8:
            errors.append(
                f"★R2 未落表: 分压后 {vbat_max}V × {bot:g}/({top:g}+{bot:g}) = {vnode:.3f}V "
                f"> 1.8V 域 ADC 上限 (J_SOM_P1 pin38 = SARADC_VIN5, 1.8V 域) ⇒ 贴上去就是过压")
        if verbose:
            report.append(f"   R2 分压后 ADC 节点电压 @4.2V = {vnode:.3f} V (上限 1.8V)")
    else:
        errors.append("★R2 未落表: 解析不出 R_BAT_DET_1/2 的阻值 ⇒ 无法判定分压后电压, 人工判")
    if verbose:
        report.append("   R2 (BAT_DET 分压链) 检查完毕")

    # ---- R3: U_EN_SW 必须有器件本体行 (type=IC) ----
    body_a = [r for r in net if _norm(r.get("ref")) == "U_EN_SW" and _norm(r.get("type")) != "NET"]
    if not body_a:
        errors.append("★R3 未落表: 表A 里 U_EN_SW 仍然 0 条 type!=NET 的器件本体行")
    body_b = [r for r in pins if _norm(r.get("ref")) == "U_EN_SW" and _norm(r.get("type")) != "NET"]
    if not body_b:
        errors.append("★R3 未落表: 脚表里 U_EN_SW 仍然 0 条 type!=NET 的器件本体行")
    bom_u = [r for r in bom if _norm(r.get("ref")) == "U_EN_SW"]
    if not bom_u:
        errors.append("★R3 未落表: BOM 里没有 U_EN_SW")
    for r in bom_u:
        if _norm(r.get("type")) == "NET":
            errors.append(f"★R3 未落表: BOM 里 U_EN_SW 的 type 仍是 NET (行 {r['_line']})")
    if "U_EN_SW" in board:
        bv = _norm(board["U_EN_SW"].get("value"))
        if bv in ("EN 输入 (高=放行底板)", "5V 输入", "5V 输出 (受 CARRIER_BOARD_EN 门控)", "GND"):
            errors.append(
                f"★R3 未落表: 板封装 U_EN_SW 的 Value 属性还是脚级功能串 {bv!r} ⇒ 板文件也要同趟改")
    if verbose:
        report.append("   R3 (U_EN_SW 器件本体行) 检查完毕")

    # ---- R4: USB D− 必须有 ESD ----
    dminus = {"USB_D_N_SRC", "NET_USB_D_N_TYPEC"}
    hit = []
    for ref, info in board.items():
        if "ESD" not in ref.upper():
            continue
        for _num, net in info.get("pads_list", []):
            if net in dminus:
                hit.append((ref, net))
                break
    if not hit:
        errors.append(
            "★R4 未落表: 板上仍然没有任何 ESD 位号挂在 D− 那条网上 "
            "(USB_D_N_SRC / NET_USB_D_N_TYPEC) ⇒ D− 仍然裸奔")
    if "D_ESD_USB_D" in board:
        info = board["D_ESD_USB_D"]
        if info["pads"] < 3 and not hit:
            errors.append("★R4 未落表: D_ESD_USB_D 仍然只有 2 个焊盘 (D+ + GND) ⇒ 仍不是双通道")
    if verbose:
        report.append(f"   R4 (USB D− ESD) 检查完毕, 命中位号 = {hit}")

    return (1 if errors else 0), errors + report


# ─────────────────────────────────────────────────────────────────────────────
# 自检 (--selftest): 反向用例 —— 改坏任一锚点 ⇒ 必须变红
# ─────────────────────────────────────────────────────────────────────────────

FIXTURES = ["netlist", "pins", "bom", "spec", "board", "specpage"]


def _copy_fixture(root: str, dst: str) -> str:
    for key in FIXTURES:
        src = os.path.join(root, REL[key])
        if not os.path.exists(src):
            continue
        d = os.path.join(dst, REL[key])
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(src, d)
    return dst


def _run_case(name: str, root: str, mutate, expect_rc: int = 1) -> tuple[str, bool, str]:
    tmp = tempfile.mkdtemp(prefix="iss211_selftest_")
    try:
        _copy_fixture(root, tmp)
        mutate(tmp)
        rc, _ = check_guard(tmp, False)
        if rc != expect_rc:
            return name, False, f"rc={rc} (期望 {expect_rc})"
        return name, True, f"rc={rc} (期望 {expect_rc}) ✔"
    except Exception as exc:
        return name, False, f"异常: {exc}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _mutate_line(path: str, lineno: int, field: str, newval: str) -> None:
    with open(path, encoding="utf-8", newline="") as fh:
        raw = fh.read()
    rows = list(csv.reader(raw.split("\n")))
    while rows and rows[-1] == []:
        rows.pop()
    head = rows[0]
    idx = lineno - 1
    r = rows[idx]
    fi = head.index(field)
    r[fi] = newval
    out = "\n".join(",".join(_csv_escape(x) for x in row) for row in rows) + "\n"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(out)


def _csv_escape(v: str) -> str:
    if any(ch in v for ch in ',"\n'):
        return '"' + v.replace('"', '""') + '"'
    return v


def selftest(root: str) -> int:
    print("╔══ ISS-211 门禁自检 (反向用例: 改坏锚点 ⇒ 必须变红) ══╗")
    cases: list[tuple[str, bool, str]] = []

    # 用例 0: 基线必须是绿的 —— 否则后面的"抓到"没有意义
    tmp = tempfile.mkdtemp(prefix="iss211_selftest_")
    try:
        _copy_fixture(root, tmp)
        rc, errs = check_guard(tmp, False)
        cases.append((f"用例0 基线干净 (现状=规格页)", rc == 0, f"rc={rc} (期望 0)" + ("" if rc == 0 else f" 错误: {errs[:3]}")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    def m_net_value(tmp):
        _mutate_line(os.path.join(tmp, REL["netlist"]), 167, "value", "上拉 2.2k 到 1.8V")

    def m_net_dnp(tmp):
        _mutate_line(os.path.join(tmp, REL["netlist"]), 182, "dnp", "必装")

    def m_net_note(tmp):
        _mutate_line(os.path.join(tmp, REL["netlist"]), 169, "note", "[VDD_1V8_IO] I2C_A 上拉 (已订正)")

    def m_bom_type(tmp):
        _mutate_line(os.path.join(tmp, REL["bom"]), 208, "type", "IC")

    def m_spec_level(tmp):
        p = os.path.join(tmp, REL["spec"])
        with open(p, encoding="utf-8") as fh:
            obj = json.load(fh)
        for c in obj.get("connections", []):
            if c.get("id") == "B-01":
                c["level"] = "1.8V"
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=2)

    def m_board_value(tmp):
        p = os.path.join(tmp, REL["board"])
        with open(p, encoding="utf-8") as fh:
            s = fh.read()
        # ★板文件里 property 的 s-表达式在值后面不跟 ')' ⇒ 替换串不能带尾巴★
        s = s.replace('(property "Value" "EN 输入 (高=放行底板)"',
                      '(property "Value" "TPS22991RAA"', 1)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(s)

    def m_specpage_anchor(tmp):
        p = os.path.join(tmp, REL["specpage"])
        with open(p, encoding="utf-8") as fh:
            s = fh.read()
        s = s.replace("| d2_a182_dnp | netlist | 182 | dnp == DNP |",
                      "| d2_a182_dnp | netlist | 182 | dnp == 必装 |", 1)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(s)

    def m_net_delete_esd_note(tmp):
        _mutate_line(os.path.join(tmp, REL["netlist"]), 417, "note", "[D_ESD_USB_D] ESD")

    cases.append(_run_case("用例1 改坏 L167 的 value (4.7k→2.2k) ⇒ 必须红", root, m_net_value))
    cases.append(_run_case("用例2 改坏 L182 的 dnp (DNP→必装) ⇒ 必须红", root, m_net_dnp))
    cases.append(_run_case("用例3 改坏 L169 note (删掉『已作废』) ⇒ 必须红", root, m_net_note))
    cases.append(_run_case("用例4 改坏 BOM L208 的 type (NET→IC) ⇒ 必须红", root, m_bom_type))
    cases.append(_run_case("用例5 改坏 SPEC.json B-01.level ⇒ 必须红", root, m_spec_level))
    cases.append(_run_case("用例6 改坏板封装 U_EN_SW 的 Value ⇒ 必须红", root, m_board_value))
    cases.append(_run_case("用例7 改坏规格页锚点表 (规格页⇄脚本漂移) ⇒ 必须红", root, m_specpage_anchor))
    cases.append(_run_case("用例8 改坏 L417 的 note (删掉 Forlinx 规矩引用) ⇒ 必须红", root, m_net_delete_esd_note))

    ok = 0
    for name, good, detail in cases:
        print(f"  {'✅' if good else '❌'} {name:<52} {detail}")
        if good:
            ok += 1
    print(f"\n自检结果: {ok}/{len(cases)} 通过")
    if ok != len(cases):
        print("★★ 自检没过 ⇒ 门禁不可信, 不许交卷 ★★")
        return 1
    # 翻面口径: 现在应当是红的 (缺陷还在) ⇒ 期望 rc=1
    rc, errs = check_resolved(root, False)
    print(f"翻面口径 (--expect-resolved) 现状 rc={rc} (期望 1 = 缺陷尚未落表) "
          f"{'✔' if rc == 1 else '★★不符合预期★★'}")
    return 0 if rc == 1 else 1


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", default=DEFAULT_ROOT, help="工程根 (默认 = HW/ 的上一级)")
    ap.add_argument("--verbose", action="store_true", help="打印逐条锚点明细")
    ap.add_argument("--expect-resolved", action="store_true",
                    help="★翻面口径: 4 条缺陷必须已消失 (落表后才 rc=0) ★")
    ap.add_argument("--selftest", action="store_true", help="跑自检 (反向用例, 只动临时副本)")
    ap.add_argument("--emit-anchors", action="store_true",
                    help="打印规格页用的锚点表 (唯一真源 = 本脚本 EXPECT)")
    args = ap.parse_args(argv)

    if args.emit_anchors:
        print(emit_anchor_table())
        return 0

    root = os.path.abspath(args.root)

    if args.selftest:
        return selftest(root)

    try:
        if args.expect_resolved:
            rc, out = check_resolved(root, args.verbose)
            if rc == 0:
                print("✅ rc=0: ★4 条缺陷已全部消失★ (翻面口径通过)")
            else:
                print(f"★★ rc=1: 翻面口径未通过 ({len(out)} 条未落表) ★★")
                for line in out:
                    print(f"   {line}")
                print("★**说明**: 现在 4 条缺陷仍在 ⇒ 本口径应当是红的; ★"
                      "等它们随『整链重出 第 1 步』落表后本口径才转绿★")
            return rc
        rc, out = check_guard(root, args.verbose)
        errors = [x for x in out if x.startswith("★")]
        report = [x for x in out if not x.startswith("★")]
        for line in report:
            print(line)
        if rc == 0:
            print("✅ rc=0: ★现状与 HW/NETLIST_SELF_CONSISTENCY_SPEC.md 一致★")
            print("★**注意: 门禁是【现状守卫】不是【合格证】** ⇒ 4 条缺陷★仍在★ ⇒ "
                  "rc=0 是预期状态 ★")
            print("★**翻面条件见规格页 §⑤**; 落表后请改用 `--expect-resolved` ★")
        else:
            print(f"★★ rc=1: 现状与规格页不一致 ({len(errors)} 条) ★★")
            for line in errors:
                print(f"   {line}")
        return rc
    except CheckError as exc:
        print(f"★rc=2: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover
        print(f"★rc=2: 未预期异常: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
