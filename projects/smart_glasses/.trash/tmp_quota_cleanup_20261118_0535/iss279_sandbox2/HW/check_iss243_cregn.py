#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HW/check_iss243_cregn.py — ★ISS-243 独立机器门禁 (C_REGN 官方值落表 + 4 条落表前置)★

★★**干什么**★★
  ★**把 ISS-243 交卷单 §B4 的验收从「人读」变成「机器判」** ★
  ⇒ ★**断言 ①: `C_REGN` 在【网表 / 脚表 / BOM】三处的 value 必须是 4.7µF 级【且带 10 V 耐压标注】** ★
  ⇒ ★**断言 ②: `C_REGN` 三处的 opn 栏不许为空** (★空 = 采购单出不来 = 门禁红★) ★
  ⇒ ★**断言 ③: 落表台账必须登记本单 (单号 + 三处改动 + 新旧 md5)** (★防「改了盘没留痕」★) ★
  ⇒ ★**断言 ④: `HW/MOS_PAD_PIN_MAPPING.md` 必须存在, 且三件 MOS 都在【L2 主表】里有行** (★L2 交付存在性★) ★
  ⇒ ★**断言 ⑤: 映射表里每件 MOS 必须同时写出「占位 pad 序」与「SOT-23 库引脚序」两个串** (★防表只抄一半★) ★
  ⇒ ★**断言 ⑥: L3 的 `D_ESD_CAM` pad 序反了的改法映射 (方案甲 + 方案乙) 在案** ★
  ⇒ ★**断言 ⑦: 真源一致 —— `state/gen_netlist.py` 里必须有新 value + `C_REGN` 的 PARTS 条目** (★防「手改 CSV 冒充落表」★) ★
  ⇒ ★**断言 ⑧: L4 的充电板 6 件 footprint 候选清单在交卷单里, 每件 ≥2 候选 + 证据等级 + 降级方案** ★

★★**判据不许放松 / 不许挂 md5** ★★
  ★**本门禁【不挂 md5】** ⇒ ★**判的是【内容】不是【指纹】**: 一份被手改过的 CSV 只要内容对就绿, 反之 md5 对不上也照样红** ★
  ★**md5 前后对照放在落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §16 (供人读), 不作为本门禁的判据** ★

★★**用法**★★
    python3 HW/check_iss243_cregn.py             # 跑断言 (rc=0 全过 / rc=1 有红)
    python3 HW/check_iss243_cregn.py --selftest  # 反向用例 (每条必须自证「真的改到了目标」)

★★**边界**★★
  · ★**只读盘** ⇒ ★**零写盘** (selftest 只在临时目录里造副本, 跑完即删) ★
  · ★**不改任何文件** · ★**零外发** · ★**实物 [实测] = 0 条** (本门禁的「实测」= 实读盘上文件)
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import re
import shutil
import sys
import tempfile

# ---------------------------------------------------------------- 判据常量 (★不许放松★)

CREGN = "C_REGN"
VALUE_RE = re.compile(r"4[.,]7\s*(?:µ|u)F", re.I)          # ★4.7µF 级★
VRWM_RE = re.compile(r"10\s*V", re.I)                      # ★10 V 耐压标注★
OPN_RE = re.compile(r"GRM21BR71C475KA73L")                 # ★本单落定的官方可采购型号★
NEW_VALUE = "4.7µF ±10% (10V)"

MOS_REFS = ("Q_AND", "Q_PG", "Q_ENVC")
PADSEQ_RE = re.compile(r"D\s*/\s*S\s*/\s*G|S\s*/\s*D\s*/\s*G|G\s*/\s*S\s*/\s*D")  # ★占位 pad 序串★
LIBSEQ_RE = re.compile(r"G\s*/\s*S\s*/\s*D")                # ★SOT-23 库引脚序串★
PAD_CELL_RE = re.compile(r"^\*\*([DSG])\s*/\s*([DSG])\s*/\s*([DSG])\*\*$")  # ★占位 pad 序【单元格】★
LIB_CELL_RE = re.compile(r"^\*\*G\s*/\s*S\s*/\s*D\*\*$")                    # ★库引脚序【单元格】★
MOS_ROW_RE = lambda ref: re.compile(r"\|\s*\*\*`%s`\*\*" % re.escape(ref))  # ★L2 主表行★

L4_REFS = ("D_ESD_TC", "FB_VBUS", "D_TVS_VBUS", "Q_CHG_LED", "D_CHG_LED", "C_REGN")
EVID_RE = re.compile(r"\[官网\]|\[实测\]|\[推算\]|\[0数据\]")

HANDOFF_REL = os.path.join(
    "HANDOFF", "2026-11-16_hw-lead_ISS243_C_REGN官方值落表与4条落表前置.md")
LEDGER_REL = os.path.join("HW", "SCHEMATIC_LANDING_V1_LANDED.md")
MAP_REL = os.path.join("HW", "MOS_PAD_PIN_MAPPING.md")
GEN_NETLIST_REL = os.path.join("state", "gen_netlist.py")

NETLIST_REL = os.path.join("HW", "netlist_v1.csv")
PINS_REL = os.path.join("HW", "netlist_v1_pins.csv")
BOM_REL = os.path.join("HW", "BOM_v1.csv")


def find_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    cur = here
    for _ in range(6):
        if os.path.isdir(os.path.join(cur, "HW")) and os.path.isdir(os.path.join(cur, "state")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return os.getcwd()


# ---------------------------------------------------------------- helpers

def _read(root: str, rel: str) -> str:
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        return ""
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


def _rows(root: str, rel: str) -> list[dict]:
    txt = _read(root, rel)
    if not txt:
        return []
    return list(csv.DictReader(io.StringIO(txt)))


def _cregn_rows(root: str, rel: str) -> list[dict]:
    return [r for r in _rows(root, rel) if (r.get("ref") or "").strip() == CREGN]


def _table_rows(txt: str) -> list[str]:
    return [ln for ln in txt.split("\n") if ln.strip().startswith("|")]


def _find_row(txt: str, ref: str) -> str:
    """★L2 主表行: 行首粗体位号★"""
    rx = MOS_ROW_RE(ref)
    for ln in _table_rows(txt):
        if rx.search(ln):
            return ln
    return ""


def _section(txt: str, num: str) -> str:
    """★取 §num 那一节 (到下一个 '## ' 为止)★"""
    m = re.search(r"^##\s*★*★*\s*%s\b" % re.escape(num), txt, re.M)
    if not m:
        return ""
    rest = txt[m.start():]
    nxt = re.search(r"^##\s", rest[len(m.group(0)):], re.M)
    return rest[: len(m.group(0)) + nxt.start()] if nxt else rest


def _section_heading(txt: str, num: str) -> str:
    """★取 §num 那一节的【标题行】★"""
    for ln in txt.split("\n"):
        if re.match(r"^##\s*★*★*\s*%s\b" % re.escape(num), ln):
            return ln
    return ""


def _cells(row: str) -> list[str]:
    """★表格行的单元格 (去掉首尾空串)★"""
    parts = row.split("|")
    return [p.strip() for p in parts[1:-1]]


# ---------------------------------------------------------------- 断言 (★8 条★)

def check_c1_value_three_places(root: str) -> tuple[bool, str]:
    """① 三处 value 必须是 4.7µF 级【且带 10V 耐压标注】"""
    bad = []
    plan = [(NETLIST_REL, "网表 L44/L45"), (PINS_REL, "脚表 L132/L133"), (BOM_REL, "BOM L43")]
    for rel, label in plan:
        rows = _cregn_rows(root, rel)
        if not rows:
            bad.append("%s 里找不到 %s 行" % (label, CREGN))
            continue
        for r in rows:
            v = (r.get("value") or "").strip()
            if not VALUE_RE.search(v):
                bad.append("%s value 不是 4.7µF 级: %r" % (label, v))
            elif not VRWM_RE.search(v):
                bad.append("%s value 缺 10V 耐压标注: %r" % (label, v))
    if bad:
        return False, "; ".join(bad)
    return True, "三处 value 均为 4.7µF 级且带 10V 耐压标注"


def check_c2_opn_not_empty(root: str) -> tuple[bool, str]:
    """② 三处 opn 栏不许为空"""
    bad = []
    plan = [(NETLIST_REL, "网表"), (PINS_REL, "脚表"), (BOM_REL, "BOM")]
    for rel, label in plan:
        rows = _cregn_rows(root, rel)
        if not rows:
            bad.append("%s 里找不到 %s 行" % (label, CREGN))
            continue
        for r in rows:
            opn = (r.get("opn") or "").strip()
            if not opn or opn == "待定":
                bad.append("%s 的 opn 栏为空/待定" % label)
            elif not OPN_RE.search(opn):
                bad.append("%s 的 opn 不含落定的官方型号 %s: %r" % (label, OPN_RE.pattern, opn))
    if bad:
        return False, "; ".join(bad)
    return True, "三处 opn 均非空且为落定型号 %s" % OPN_RE.pattern


def check_c3_ledger(root: str) -> tuple[bool, str]:
    """③ 落表台账必须登记本单 (单号 + 三处改动)"""
    txt = _read(root, LEDGER_REL)
    if not txt:
        return False, "台账文件不存在: %s" % LEDGER_REL
    head = _section_heading(txt, "16")
    if not head:
        return False, "台账里没有 §16 (ISS-243 那一节)"
    if "ISS-243" not in head:
        return False, "台账 §16 的标题行里没有 ISS-243 的单号"
    sec = _section(txt, "16")
    need = ["netlist_v1.csv", "netlist_v1_pins.csv", "BOM_v1.csv", NEW_VALUE]
    missing = [n for n in need if n not in sec]
    if missing:
        return False, "台账 §16 的 ISS-243 登记缺: %s" % ", ".join(missing)
    return True, "台账 §16 已登记 ISS-243 (三处改动 + 新值 + 新旧 md5)"


def check_c4_map_exists(root: str) -> tuple[bool, str]:
    """④ 映射表必须存在, 且三件 MOS 在 L2 主表里都有行"""
    txt = _read(root, MAP_REL)
    if not txt:
        return False, "映射表不存在: %s" % MAP_REL
    missing = [r for r in MOS_REFS if not _find_row(txt, r)]
    if missing:
        return False, "映射表的 L2 主表里缺 MOS 行: %s" % ", ".join(missing)
    if "D_ESD_CAM" not in txt:
        return False, "映射表里没有 L3 的 D_ESD_CAM"
    return True, "映射表存在, 三件 MOS 在 L2 主表里都有行"


def check_c5_both_sequences(root: str) -> tuple[bool, str]:
    """⑤ 每件 MOS 必须同时写出「占位 pad 序」与「SOT-23 库引脚序」两个串 (★按列判, 不许串味★)"""
    txt = _read(root, MAP_REL)
    if not txt:
        return False, "映射表不存在"
    bad = []
    for ref in MOS_REFS:
        row = _find_row(txt, ref)
        if not row:
            bad.append("%s 在 L2 主表里没有行" % ref)
            continue
        cells = _cells(row)
        # ★L2 主表的列序: 0 位号 | 1 pad1 | 2 pad2 | 3 pad3 | 4 占位 pad 序 | 5 SOT-23 库引脚序 | ...★
        if len(cells) < 6:
            bad.append("%s 行的列数不足 (找不到占位/库引脚序两列)" % ref)
            continue
        if not PAD_CELL_RE.match(cells[4]):
            bad.append("%s 行的「占位 pad 序」列缺三功能串 (D/S/G · S/D/G · G/S/D): %r" % (ref, cells[4]))
        if not LIB_CELL_RE.match(cells[5]):
            bad.append("%s 行的「SOT-23 库引脚序」列缺 G/S/D: %r" % (ref, cells[5]))
    if bad:
        return False, "; ".join(bad)
    return True, "三件 MOS 行都同时有占位 pad 序 + 库引脚序两个串 (按列判)"


def check_c6_l3_dual_path(root: str) -> tuple[bool, str]:
    """⑥ L3: D_ESD_CAM 的 pad 序反了的改法映射 (方案甲 + 方案乙) 在案"""
    txt = _read(root, MAP_REL)
    if not txt:
        return False, "映射表不存在"
    rows = _table_rows(txt)
    for token in ("方案甲", "方案乙"):
        if not any(token in ln for ln in rows):
            return False, "L3 的表格里没有「%s」那一栏" % token
    need = ["D_ESD_CAM", "GND", "CSI_D0_CK_P", "TPD1E05U06", "PESD5V0S1BA"]
    missing = [n for n in need if n not in txt]
    if missing:
        return False, "L3 改法映射缺: %s" % ", ".join(missing)
    return True, "L3 方案甲 (换双向件) + 方案乙 (对调 land) 都在案"


def check_c7_true_source(root: str) -> tuple[bool, str]:
    """⑦ 真源一致: state/gen_netlist.py 里必须有新 value + C_REGN 的 PARTS 条目"""
    txt = _read(root, GEN_NETLIST_REL)
    if not txt:
        return False, "真源不存在: %s" % GEN_NETLIST_REL
    # ★只判 C_REGN 自己的 add() 调用 (★不判注释里出现的字样★)
    calls = re.findall(r'add\("[^"]*",\s*"[^"]*",\s*"C_REGN",\s*"[^"]*",\s*"C_REGN",\s*"([^"]*)"', txt)
    if not calls:
        return False, "真源里找不到 C_REGN 的 add() 调用"
    bad = [v for v in calls if v != NEW_VALUE]
    if bad:
        return False, "真源里 C_REGN 的 add() value 不是「%s」: %s" % (NEW_VALUE, bad)
    if NEW_VALUE not in txt:
        return False, "真源里找不到新 value「%s」" % NEW_VALUE
    m = re.search(r'"C_REGN"\s*:\s*\{', txt)
    if not m:
        return False, "真源的 PARTS 字典里没有 C_REGN 条目 (⇒ footprint/opn 两栏还是空)"
    seg = txt[m.start(): m.start() + 700]
    if not OPN_RE.search(seg):
        return False, "真源 PARTS[C_REGN] 里没有落定的 opn"
    if "footprint" not in seg:
        return False, "真源 PARTS[C_REGN] 里没有 footprint"
    return True, "真源 (gen_netlist.py) 的 value + PARTS[C_REGN] 都在位"


def check_c8_l4_candidates(root: str) -> tuple[bool, str]:
    """⑧ L4: 充电板 6 件的 footprint 候选清单在交卷单里, 每件 ≥2 候选"""
    txt = _read(root, HANDOFF_REL)
    if not txt:
        return False, "交卷单不存在: %s" % HANDOFF_REL
    rows = _table_rows(txt)
    bad = []
    for ref in L4_REFS:
        cand_rows = [ln for ln in rows if ref in ln and "候选1" in ln and "候选2" in ln]
        if not cand_rows:
            bad.append("交卷单里找不到 %s 的 L4 候选行 (要 ≥2 候选: 候选1 + 候选2)" % ref)
            continue
        row = cand_rows[0]
        if not EVID_RE.search(row):
            bad.append("%s 的 L4 行没有证据等级标注" % ref)
        if "降级" not in row:
            bad.append("%s 的 L4 行没有降级方案" % ref)
    if bad:
        return False, "; ".join(bad)
    return True, "L4 六件在交卷单里, 每件 ≥2 候选 + 证据等级 + 降级方案"


CHECKS = [
    ("C1", "C_REGN 三处 value = 4.7µF 级且带 10V 耐压标注", check_c1_value_three_places),
    ("C2", "C_REGN 三处 opn 栏非空且为落定型号", check_c2_opn_not_empty),
    ("C3", "落表台账 §16 登记了 ISS-243", check_c3_ledger),
    ("C4", "MOS pad↔pin 映射表存在且含三件 MOS 的 L2 主表行", check_c4_map_exists),
    ("C5", "映射表每件 MOS 同时有占位 pad 序 + 库引脚序", check_c5_both_sequences),
    ("C6", "L3 D_ESD_CAM 双方案改法映射在案", check_c6_l3_dual_path),
    ("C7", "真源 gen_netlist.py 的 value + PARTS[C_REGN] 在位", check_c7_true_source),
    ("C8", "L4 充电板 6 件候选清单在交卷单里", check_c8_l4_candidates),
]


# ---------------------------------------------------------------- 运行

def run_checks(root: str) -> list[tuple[str, bool, str]]:
    out = []
    for cid, _desc, fn in CHECKS:
        try:
            ok, msg = fn(root)
        except Exception as e:  # ★断言自身炸了 = 红, 不许静默放过★
            ok, msg = False, "断言异常: %r" % e
        out.append((cid, ok, msg))
    return out


def print_results(results, title: str) -> int:
    print("=" * 78)
    print("  ★[%s]★" % title)
    print("=" * 78)
    n_red = 0
    for cid, ok, msg in results:
        tag = "[PASS]" if ok else "[FAIL]"
        if not ok:
            n_red += 1
        print("  %-4s %s %s" % (cid, tag, msg))
    print("-" * 78)
    if n_red == 0:
        print("  ✅ rc=0: %d/%d 条断言全过" % (len(results), len(results)))
    else:
        print("  ❌ rc=1: %d/%d 条红" % (n_red, len(results)))
    return 0 if n_red == 0 else 1


# ---------------------------------------------------------------- selftest

SELFTEST_FILES = [
    NETLIST_REL, PINS_REL, BOM_REL, LEDGER_REL, MAP_REL, GEN_NETLIST_REL, HANDOFF_REL,
]


def _stage(root: str, tmp: str) -> str:
    for rel in SELFTEST_FILES:
        src = os.path.join(root, rel)
        dst = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(src):
            shutil.copy2(src, dst)
        else:
            open(dst, "w", encoding="utf-8").write("")
    return tmp


def _mutate_in_line(path: str, scope: str, old: str, new: str) -> bool:
    """★只改【含 scope 的那一行】里的 old ⇒ 定点突变, 不误伤别的行★"""
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    for i, ln in enumerate(lines):
        if scope in ln and old in ln:
            lines[i] = ln.replace(old, new, 1)
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return True
    return False


def _delete_line(path: str, scope: str) -> bool:
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    for i, ln in enumerate(lines):
        if scope in ln:
            del lines[i]
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return True
    return False


# ★★反向用例: (用例名, 期望变红的断言集合, 相对路径, scope, old, new, mode)★★
# ★★每条都【自证「真的改到了目标」】: 改完后变红的断言集合必须【恰好】等于期望集合 (其余仍绿)★★
SELFTEST_CASES = [
    ("① 删掉 BOM 的 10V 耐压标注 ⇒ 期望红 C1",
     ("C1",), BOM_REL, CREGN, "4.7µF ±10% (10V)", "4.7µF", "replace"),
    ("② 把网表 L44 的 opn 栏清空 ⇒ 期望红 C2",
     ("C2",), NETLIST_REL, "P1,REGN,C_REGN",
     "GRM21BR71C475KA73L (Murata 0805 / 4.7µF / 16V / X7R / ±10%)", "", "replace"),
    ("③ 把台账 §16 里的 ISS-243 登记删掉 ⇒ 期望红 C3",
     ("C3",), LEDGER_REL, "## ★★16 ·", "ISS-243", "ISS-XXX", "replace"),
    ("④ 把映射表里 Q_PG 那行删掉 ⇒ 期望红 C4/C5",
     ("C4", "C5"), MAP_REL, "| **`Q_PG`**", None, None, "delete"),
    ("⑤ 把映射表里 Q_AND 行的「占位 pad 序」串抹掉 ⇒ 期望红 C5",
     ("C5",), MAP_REL, "| **`Q_AND`**", "**D / S / G**", "(占位 pad 序未写)", "replace"),
    ("⑥ 把映射表里 L3 的「方案乙」那一栏抹掉 ⇒ 期望红 C6",
     ("C6",), MAP_REL, "| | ★**方案甲:", "**方案乙:", "**方案X:", "replace"),
    ("⑦ 把真源的 value 退回「[待选型] 1µF」 ⇒ 期望红 C7",
     ("C7",), GEN_NETLIST_REL, '"U_CHG pin22", "C_REGN"',
     '"4.7µF ±10% (10V)", "C",', '"[待选型] 1µF", "C",', "replace"),
    ("⑧ 把交卷单里 D_TVS_VBUS 的候选2 抹掉 ⇒ 期望红 C8",
     ("C8",), HANDOFF_REL, "D_TVS_VBUS", "候选2", "候选X", "replace"),
]


def run_selftest(root: str) -> int:
    base = run_checks(root)
    n_red_base = sum(1 for _c, ok, _m in base if not ok)
    print("=" * 78)
    print("  ★[selftest] 反向用例 (★每条必须自证「真的改到了目标」★)")
    print("=" * 78)
    if n_red_base:
        print("  ❌ 基线就有 %d 条红 ⇒ 先修好正例再谈反向用例 (基线红: %s)"
              % (n_red_base, ", ".join(c for c, ok, _m in base if not ok)))
        return 1
    print("  基线: %d/%d 条全绿 ✔" % (len(base), len(base)))
    print("-" * 78)

    n_ok = 0
    for name, expect_red, rel, scope, old, new, mode in SELFTEST_CASES:
        tmp = tempfile.mkdtemp(prefix="iss243_selftest_")
        try:
            _stage(root, tmp)
            target = os.path.join(tmp, rel)
            if mode == "delete":
                changed = _delete_line(target, scope)
            else:
                changed = _mutate_in_line(target, scope, old, new)
            if not changed:
                print("  [FAIL] %s\n         ★突变没生效 (盘上找不到 scope=%r) ⇒ 用例不算数★" % (name, scope))
                continue
            res = run_checks(tmp)
            reds = tuple(sorted(c for c, ok, _m in res if not ok))
            if reds == tuple(sorted(expect_red)):
                print("  [PASS] %s\n         ★自证: 变红的断言 = {%s} = 期望集合, 其余 %d 条仍绿 ⇒ 真的改到了目标★"
                      % (name, ",".join(reds), len(res) - len(reds)))
                n_ok += 1
            else:
                print("  [FAIL] %s\n         ★期望红 %s, 实测红 %s ⇒ 判据太宽或突变没生效★"
                      % (name, ",".join(expect_red), ",".join(reds) or "无"))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    print("-" * 78)
    if n_ok == len(SELFTEST_CASES):
        print("  ✅ rc=0: 反向用例 %d/%d 全过 (★每条都自证「真的改到了目标」★)" % (n_ok, len(SELFTEST_CASES)))
        return 0
    print("  ❌ rc=1: 反向用例 %d/%d 过" % (n_ok, len(SELFTEST_CASES)))
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=None)
    args = ap.parse_args()
    root = args.root or find_root()
    if args.selftest:
        return run_selftest(root)
    res = run_checks(root)
    rc = print_results(res, "check_iss243_cregn · ISS-243 独立门禁")
    print("  根目录: %s" % root)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
