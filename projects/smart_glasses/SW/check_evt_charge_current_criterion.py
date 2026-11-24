#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-385 · EVT `PWR-05` 充电电流判据口径闸 (sw-lead · 2026-11-24)

★★★【性质】★★★ ★**只新建** ⇒ ★**零改既有闸 · 零改既有页面正文 · 零挂链** ★
  · ★**零改 `SW/EVT_TEMPLATE.md`**: 本闸只读它, 绝不碰它一个字节 (K8 运行前后 md5 自证) ★
  · ★**零挂链**: ★**本闸【不在】 `state/gate_check.py` 链里** ⇒ K7 自证 (命中数必须 = 0) ★
  · ★**不改任何既有闸的判据表**: R10/§11.2 那些判据只在【本页 + 本闸】里另写一份 ★

★★★【命门 · 判据必须按【语义】判, 不许按【子串】判】★★★
  ★**为什么**: 「充电电流 ≥ 1.5A」这句话的【语义】是【下限要求】(要求实测达到 1.5A) ⇒ ★**上限要求 (≤) 是完全不同的语义** ⇒ ★**若按子串判 ("1.5A" in cell), 把判据改写成「≤ 1.5A」或「≥ 0.01A」都仍判绿 ⇒ 口径被换掉闸看不见** ★
  ⇒ ★**本闸的做法**: ① 双向语义解析【比较符 + 数值 + 量纲】(「≥ X」与「X ≤」两种写法都认; mA 自动折算成 A) ② 把每个边界归类成【下限 / 上限】 ③ 数值按【浮点容差】比, 不比字符串 ⇒ ★**「≥1.5A」改「≤1.5A」/ 改「≥0.01A」/ 改「≥1.6A」全被抓; 而「1.50 A」「1500mA」这种同义改写【不误伤】** ★
  ⇒ ★**另外**: 「@5V/2A 适配器」里的 2A **不是判据阈值** (它前面没有比较符) ⇒ 解析器不会把它当阈值 ★

★★★【三相 (★照 ISS-381 同款先例★)】★★★
  · `--phase pre`   (默认, 裸跑): ★**基线/登记相** ⇒ ★**现行判据(1.5A) 被【如实点名】但【不判红】** (它是被登记的【既存缺陷】, 待 main 拍改法) ⇒ rc=0 ★
  · `--phase post`  (★改判据那一趟的验收相★): ★**阈值必须 ≤ 硬件真值 + 必须声明量哪个量 + 必须标注适用范围 + 读回方式必须可达** ⇒ ★**今天实跑 rc=1 且逐条点名** ★
  · `--strict`      (★把「既存缺陷」也当红★): ★**裸跑就 rc=1 并点名「永远判不过」** ⇒ ★**给 main 一个「一条命令就红」的入口** ★
  ⇒ ★**为什么默认 pre 是绿的**: ★**「1.5A 永远判不过」是【已登记的既存缺陷】, 不是本闸的新发现** ⇒ ★**闸的职责是「口径漂移即红」, 不是「把已知缺陷重复报一遍当新红」** ⇒ ★**真值被改 / 口径被换 / 适用性造假 / 挂链 / 改页面 ⇒ 任何一相都红** ★
  ⇒ ★**登记口径跟着 EVT 页走**: ★**main 在「改判据那一趟」把 EVT 页改了之后, 必须同批更新本页机器块里的 `evt_current_criterion_a` / `evt_current_criterion_max_a`** ⇒ ★**否则闸立刻报「口径被换掉」** ★

用法:
    python3 SW/check_evt_charge_current_criterion.py                  # 裸跑 (pre 相) ⇒ rc=0 + 点名既存缺陷
    python3 SW/check_evt_charge_current_criterion.py --phase post     # 改判据那一趟的验收相 ⇒ 今天 rc=1
    python3 SW/check_evt_charge_current_criterion.py --strict          # 既存缺陷也当红 ⇒ 今天 rc=1
    python3 SW/check_evt_charge_current_criterion.py --selftest       # 反向用例自测 ⇒ 末行 ALL TESTS PASS
    python3 SW/check_evt_charge_current_criterion.py --root <dir>     # 指定根目录 (沙盒用)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

GATE_NAME = "check_evt_charge_current_criterion"

EVT_TEMPLATE_REL = os.path.join("SW", "EVT_TEMPLATE.md")
CALIBER_REL = os.path.join("SW", "EVT_CHARGE_CURRENT_CRITERION_CALIBER.md")
POWER_JSON_REL = os.path.join("MECH", "hinge_power_calc.json")
NETLIST_REL = os.path.join("HW", "netlist_v1.csv")
GATE_CHECK_REL = os.path.join("state", "gate_check.py")

CHARGE_REFS = ("U_CHG", "R_ILIM")
EVIDENCE_GRADES = ("[实测]", "[推算]", "[官网]", "[媒体]", "[0数据]")

# ★**R_ILIM 未装时的故障电流**: BQ25896 REG04 复位默认 ICHG = 2048 mA [官网]
#   (见 HW/CHARGE_BOARD_SPEC.md §2.8) ⇒ ★**判据上限只要 < 2.048A 就还有鉴别力** ★
ILIM_FAULT_ICHG_A = 2.048

# ── 语义解析: 比较符 → 语义类 ────────────────────────────────────────
LOWER_OPS = ("≥", ">=", "≧", "不低于", "不小于", "至少", "大于等于", ">")
UPPER_OPS = ("≤", "<=", "≦", "不超过", "不高于", "至多", "小于等于", "<")

_NUM = r"(?P<num>\d+(?:\.\d+)?)"
_UNIT = r"(?P<unit>mA|MA|A|安培|毫安)"

#  ★**形式一**: 比较符在【前】 —— 「≥ 1.5A」 ★
BEFORE_RE = re.compile(
    r"(?P<op>≥|>=|≧|≤|<=|≦|不低于|不小于|至少|大于等于|不超过|不高于|至多|小于等于|>|<)\s*"
    + _NUM + r"\s*" + _UNIT
)
#  ★**形式二**: 比较符在【后】 —— 「0.50A ≤ ICHG ≤ 0.75A」 ★
AFTER_RE = re.compile(
    _NUM + r"\s*" + _UNIT + r"\s*(?P<op>≤|<=|≦|≥|>=|≧|不低于|不小于|至少|大于等于|不超过|不高于|至多|小于等于|>|<)"
)

#  ★**量纲口径识别**: 判据必须声明【量哪个量】(IIN 输入侧 / ICHG 电池侧) ★
QTY_PATTERNS = (
    ("ICHG", re.compile(r"ICHG|电池侧|电池(?:充电)?电流|充入电池|入电池")),
    ("IIN", re.compile(r"IIN|输入电流|适配器电流|VBUS\s*电流|输入侧")),
)


def _md5(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def _norm_unit(num: float, unit: str) -> float:
    u = (unit or "A").lower()
    if u in ("ma", "毫安"):
        return num / 1000.0
    return num


def _op_class(op: str):
    if op in LOWER_OPS:
        return "lower"
    if op in UPPER_OPS:
        return "upper"
    return None


def _same_num(a: float, b: float) -> bool:
    return abs(float(a) - float(b)) <= 1e-9 * max(1.0, abs(float(a)), abs(float(b)))


def _split_row(raw: str):
    return [c.strip() for c in raw.strip().strip("|").split("|")]


# ── 真值推导 (不写死任何数) ──────────────────────────────────────────
def derive_truth(root: str) -> dict:
    """从 MECH/hinge_power_calc.json 的 rilim_table + 网表 board 域推导硬件真值。"""
    out = {"ok": False, "errors": []}

    netlist = os.path.join(root, NETLIST_REL)
    if not os.path.isfile(netlist):
        out["errors"].append("网表不存在: %s" % NETLIST_REL)
        return out
    import csv
    with open(netlist, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    boards = {r: set() for r in CHARGE_REFS}
    dnp = {r: set() for r in CHARGE_REFS}
    ri_ohm = None
    for row in rows:
        ref = (row.get("ref") or "").strip()
        if ref not in CHARGE_REFS:
            continue
        boards[ref].add((row.get("board") or "").strip())
        dnp[ref].add((row.get("dnp") or "").strip())
        if ref == "R_ILIM" and ri_ohm is None:
            m = re.search(r"(\d+(?:\.\d+)?)\s*Ω", row.get("value") or "")
            if m:
                ri_ohm = float(m.group(1))
    out["netlist_rows"] = len(rows)
    out["boards"] = {k: sorted(v) for k, v in boards.items()}
    out["dnp"] = {k: sorted(v) for k, v in dnp.items()}
    out["ri_ohm"] = ri_ohm
    if ri_ohm is None:
        out["errors"].append("网表里读不到 R_ILIM 阻值 (value 字段无 Ω 数)")
    if not boards["U_CHG"] or not boards["R_ILIM"]:
        out["errors"].append("网表里读不到 U_CHG / R_ILIM 行")

    main_has_chain = any("MAIN_PCB" in boards.get(r, set()) for r in CHARGE_REFS)
    out["applicable_on_demo_main_pcb"] = bool(main_has_chain)

    # 充电 IC 的 I2C 是否跨铰链到 MAIN_PCB (⇒ SoC 能不能读充电 IC 寄存器)
    i2c_chg = [(row.get("board") or "").strip() for row in rows
               if "I2C_CHG" in (row.get("net") or "")]
    out["i2c_chg_boards"] = sorted(set(i2c_chg))
    out["charger_registers_reachable"] = any(b == "MAIN_PCB" for b in i2c_chg)

    pj = os.path.join(root, POWER_JSON_REL)
    if not os.path.isfile(pj):
        out["errors"].append("权威表不存在: %s" % POWER_JSON_REL)
        return out
    with open(pj, encoding="utf-8") as f:
        data = json.load(f)
    table = data.get("rilim_table") or []
    if ri_ohm is None:
        out["errors"].append("拿不到阻值 ⇒ 无法选档")
        return out
    sel = {t["tag"]: t for t in table if abs(float(t["R_ILIM"]) - ri_ohm) < 1e-9}
    if "max" not in sel:
        out["errors"].append("权威表里没有 R_ILIM=%s 档" % ri_ohm)
        return out
    out["ri_ohm"] = float(sel["max"]["R_ILIM"])
    out["iinmax_max_a"] = float(sel["max"]["IINMAX_A"])
    out["ichg_max_a"] = float(sel["max"]["ICHG_A"])
    out["per_pin_max_a"] = float(sel["max"]["per_pin_A"])
    out["iinmax_min_a"] = float(sel["min"]["IINMAX_A"]) if "min" in sel else None
    out["ichg_min_a"] = float(sel["min"]["ICHG_A"]) if "min" in sel else None
    out["ichg_typ_a"] = float(sel["typ"]["ICHG_A"]) if "typ" in sel else None
    out["ceiling_by_qty"] = {"ICHG": out["ichg_max_a"], "IIN": out["iinmax_max_a"]}
    out["floor_by_qty"] = {
        "ICHG": out["ichg_min_a"] if out["ichg_min_a"] is not None else out["ichg_max_a"],
        "IIN": out["iinmax_min_a"] if out["iinmax_min_a"] is not None else out["iinmax_max_a"],
    }
    out["ok"] = not out["errors"]
    return out


# ── 判据解析 (语义, 非子串) ──────────────────────────────────────────
def parse_criterion(text: str) -> dict:
    """把通过标准单元解析成【边界集合】: 下限 (lower) / 上限 (upper)。"""
    res = {"op": None, "raw_op": None, "num": None, "unit": None, "value_a": None,
           "kind": None, "quantity": None, "register_readback": False,
           "mentions_scope": False, "lower": [], "upper": [], "thresholds": []}

    def _add(op, num, unit, form):
        kind = _op_class(op)
        if kind is None:
            return
        val = _norm_unit(num, unit)
        rec = {"op": op, "num": num, "unit": unit, "kind": kind, "value_a": val, "form": form}
        res["thresholds"].append(rec)
        (res["lower"] if kind == "lower" else res["upper"]).append(rec)

    for m in BEFORE_RE.finditer(text):
        _add(m.group("op"), float(m.group("num")), m.group("unit"), "before")
    for m in AFTER_RE.finditer(text):
        _add(m.group("op"), float(m.group("num")), m.group("unit"), "after")

    if res["thresholds"]:
        first = res["thresholds"][0]
        res.update(op=first["op"], raw_op=first["op"], num=first["num"],
                   unit=first["unit"], value_a=first["value_a"], kind=first["kind"])

    for qty, pat in QTY_PATTERNS:
        if pat.search(text):
            res["quantity"] = qty
            break
    res["register_readback"] = bool(re.search(r"寄存器回读|寄存器\s*读|读寄存器", text))
    res["mentions_scope"] = bool(re.search(r"不适用|不适用于|整机|充电板", text))
    return res


def find_pwr05(root: str):
    path = os.path.join(root, EVT_TEMPLATE_REL)
    if not os.path.isfile(path):
        return None, []
    lines = open(path, encoding="utf-8").read().splitlines()
    # ★**必须要求 PWR-05 后面紧跟单元格分隔符 '|'** ⇒ ★**否则 "PWR-05-OLD" 这种改名也会被误当成真行** ★
    hits = [(i, ln) for i, ln in enumerate(lines, 1)
            if re.match(r"^\|\s*PWR-05\s*\|", ln.strip())]
    return (hits[0] if hits else None), hits


# ── 口径页机器块 ─────────────────────────────────────────────────────
def load_caliber_block(root: str):
    path = os.path.join(root, CALIBER_REL)
    if not os.path.isfile(path):
        return None, "口径页不存在: %s" % CALIBER_REL
    text = open(path, encoding="utf-8").read()
    m = re.search(r"```ya?ml[^\n]*\n(.*?)```", text, re.S)
    if not m:
        return None, "口径页里找不到 yaml 机器块"
    try:
        import yaml
        data = yaml.safe_load(m.group(1))
    except Exception as e:  # noqa: BLE001
        return None, "口径页机器块 yaml 解析失败: %s" % e
    blk = (data or {}).get("evt_pwr05_caliber")
    if not isinstance(blk, dict):
        return None, "口径页机器块缺 evt_pwr05_caliber 段"
    return blk, None


def check_evidence_section(root: str):
    """证据分级表必须存在、是表、每行带等级、五个等级都定义过。"""
    path = os.path.join(root, CALIBER_REL)
    if not os.path.isfile(path):
        return False, "口径页不存在"
    text = open(path, encoding="utf-8").read()
    m = re.search(r"^#{1,4}\s*.*证据分级.*$", text, re.M)
    if not m:
        return False, "口径页找不到【证据分级】章节"
    rest = text[m.end():]
    nxt = re.search(r"^#{1,4}\s", rest, re.M)
    section = rest[: nxt.start()] if nxt else rest
    rows = [l for l in section.splitlines() if l.strip().startswith("|")]
    if len(rows) < 3:
        return False, "证据分级段没有表 (至少 表头+分隔+1 行)"
    data_rows = rows[2:]
    for l in data_rows:
        if not any(g in l for g in EVIDENCE_GRADES):
            return False, "证据分级表有一行没标等级: %s" % l.strip()[:60]
    missing = [g for g in EVIDENCE_GRADES if g not in section]
    if missing:
        return False, "证据分级表缺等级定义: %s" % ",".join(missing)
    return True, "证据分级表 %d 行, 五个等级齐全, 每行都带等级" % len(data_rows)


# ── 主判据 ───────────────────────────────────────────────────────────
def run_checks(root: str, phase: str = "pre", strict: bool = False) -> dict:
    findings = []

    def add(code, ok, msg, severity="fail"):
        findings.append({"code": code, "ok": bool(ok), "msg": msg, "severity": severity})

    evt_path = os.path.join(root, EVT_TEMPLATE_REL)
    if not os.path.isfile(evt_path):
        add("K0_evt_exists", False, "%s 不存在" % EVT_TEMPLATE_REL)
        return {"phase": phase, "rc": 1, "findings": findings}
    evt_md5_before = _md5(evt_path)

    truth = derive_truth(root)
    if not truth["ok"]:
        for e in truth["errors"]:
            add("K1_truth", False, "真值推导失败: %s" % e)
        return {"phase": phase, "rc": 1, "findings": findings}

    blk, err = load_caliber_block(root)
    if blk is None:
        add("K0_caliber_exists", False, err)
        return {"phase": phase, "rc": 1, "findings": findings}

    row, hits = find_pwr05(root)
    if row is None:
        add("K2_row_found", False,
            "SW/EVT_TEMPLATE.md 里找不到 PWR-05 行 (★判据被删 ⇒ 红★)")
        return {"phase": phase, "rc": 1, "findings": findings}
    row_no, row_text = row
    cells = _split_row(row_text)
    standard = cells[2] if len(cells) > 2 else row_text
    crit = parse_criterion(standard)

    known_sev = "fail" if (phase == "post" or strict) else "known"

    # ── K1 真值一致性: 机器块登记的真值必须与权威表/网表逐字相符 ──
    k1_bad = False
    for key, tk in (("ri_ohm", "ri_ohm"), ("iinmax_max_a", "iinmax_max_a"),
                    ("ichg_max_a", "ichg_max_a"), ("per_pin_max_a", "per_pin_max_a")):
        if key not in blk:
            add("K1_truth_match", False, "口径页机器块缺字段 %s" % key)
            k1_bad = True
            continue
        try:
            got = float(blk[key])
        except (TypeError, ValueError):
            add("K1_truth_match", False, "口径页机器块 %s 非数值: %r" % (key, blk[key]))
            k1_bad = True
            continue
        exp = truth[tk]
        if not _same_num(got, exp):
            add("K1_truth_match", False,
                "口径页机器块 %s=%r 与权威真值 %r 不符 ⇒ 登记的真值被换过 ⇒ 红" % (key, got, exp))
            k1_bad = True
    if not k1_bad:
        add("K1_truth_match", True,
            "机器块真值与权威表/网表逐字相符 (R=%gΩ · IINMAX(max)=%0.4fA · ICHG(max)=%0.4fA · 单pin(max)=%0.4fA)"
            % (truth["ri_ohm"], truth["iinmax_max_a"], truth["ichg_max_a"], truth["per_pin_max_a"]))

    # ── K2 口径登记一致: 判据的【边界集合】必须与登记口径一致 (语义比, 非子串) ──
    reg_lo = blk.get("evt_current_criterion_a")
    reg_hi = blk.get("evt_current_criterion_max_a")
    if reg_lo is None:
        add("K2_registered_match", False,
            "口径页机器块缺 evt_current_criterion_a (现行判据口径未登记 ⇒ 闸无从判『口径被换掉』)")
    else:
        page_lo = [r["value_a"] for r in crit["lower"]]
        page_hi = [r["value_a"] for r in crit["upper"]]
        try:
            reg_lo_f = float(reg_lo)
            reg_hi_f = float(reg_hi) if reg_hi is not None else None
        except (TypeError, ValueError):
            reg_lo_f, reg_hi_f = None, None
        if reg_lo_f is None:
            add("K2_registered_match", False, "口径页机器块 evt_current_criterion_a 非数值: %r" % (reg_lo,))
        else:
            lo_ok = (len(page_lo) == 1 and _same_num(page_lo[0], reg_lo_f))
            hi_ok = (reg_hi_f is None and not page_hi) or (
                reg_hi_f is not None and len(page_hi) == 1 and _same_num(page_hi[0], reg_hi_f))
            if lo_ok and hi_ok:
                add("K2_registered_match", True,
                    "PWR-05 现状判据 (下限 %gA%s) 与登记口径逐字相符"
                    % (reg_lo_f, (", 上限 %gA" % reg_hi_f) if reg_hi_f is not None else ""))
            else:
                got_lo = ("下限 %gA" % page_lo[0]) if len(page_lo) == 1 else ("下限 %s" % page_lo)
                got_hi = (", 上限 %gA" % page_hi[0]) if len(page_hi) == 1 else (", 上限 %s" % page_hi)
                exp_lo = "下限 %gA" % reg_lo_f
                exp_hi = (", 上限 %gA" % reg_hi_f) if reg_hi_f is not None else ", 无上限"
                add("K2_registered_match", False,
                    "口径被换掉: PWR-05 (L%d) 现为【%s%s】, 登记口径是【%s%s】 ⇒ "
                    "不再是本文给的『硬件上限口径』 ⇒ 红 (★这正是把阈值改成 0.01A 的那类改写★)"
                    % (row_no, got_lo, got_hi, exp_lo, exp_hi))

    # ── K3 可达性: 按【语义】把每个边界与硬件真值对账 ──
    qty = crit["quantity"]
    ceil_ichg = truth["ceiling_by_qty"]["ICHG"]
    ceil_iin = truth["ceiling_by_qty"]["IIN"]
    floor_ichg = truth["floor_by_qty"]["ICHG"]
    floor_iin = truth["floor_by_qty"]["IIN"]
    for r in crit["thresholds"]:
        if r["kind"] == "lower":
            if qty == "IIN":
                cap, capname = ceil_iin, "IINMAX"
            elif qty == "ICHG":
                cap, capname = ceil_ichg, "ICHG"
            else:
                cap, capname = min(ceil_ichg, ceil_iin), "ICHG/IIN"
            if r["value_a"] > cap + 1e-12:
                add("K3_reachable", False,
                    "PWR-05 (L%d) 要求【%s %g%s】(下限要求) 而硬件真值 %s 上限只有 %0.4fA "
                    "(差 %0.2f×) ⇒ ★永远判不过★" % (row_no, r["op"], r["num"], r["unit"],
                                                    capname, cap, r["value_a"] / cap),
                    severity=known_sev)
            else:
                add("K3_reachable", True,
                    "PWR-05 下限 %gA ≤ 硬件真值上限 %0.4fA ⇒ 可达成" % (r["value_a"], cap))
        else:
            cap = max(ceil_ichg, ceil_iin)
            fl = min(floor_ichg, floor_iin)
            if r["value_a"] < fl - 1e-12:
                add("K3_reachable", False,
                    "PWR-05 (L%d) 上限 %gA 低于硬件真值下限 %0.4fA ⇒ ★永远判不过★"
                    % (row_no, r["value_a"], fl), severity=known_sev)
            elif r["value_a"] >= ILIM_FAULT_ICHG_A - 1e-12:
                add("K3_reachable", False,
                    "PWR-05 (L%d) 只给了上限 %gA 且 ≥ R_ILIM 未装时的故障电流 %0.3fA ⇒ "
                    "★该判据恒过 = 无鉴别力★" % (row_no, r["value_a"], ILIM_FAULT_ICHG_A),
                    severity=known_sev)
            else:
                add("K3_reachable", True,
                    "PWR-05 上限 %gA 落在硬件真值区间 [%0.4f, %0.4f] 内, 且 < 故障电流 %0.3fA ⇒ 有鉴别力"
                    % (r["value_a"], fl, cap, ILIM_FAULT_ICHG_A))

    # ── K4 量口径必须声明 ──
    declared = blk.get("criterion_source")
    if declared not in ("ICHG", "IIN"):
        add("K4_quantity_declared", False,
            "口径页机器块 criterion_source=%r 不是 ICHG/IIN ⇒ 本页自己没定住『量哪个量』" % (declared,))
    elif crit["quantity"] is None:
        add("K4_quantity_declared", False,
            "PWR-05 (L%d) 没声明【量哪个量】(须写明 电池侧 ICHG 或 输入侧 IIN) ⇒ 判据对象不唯一 "
            "(登记口径 = %s)" % (row_no, declared), severity=known_sev)
    elif crit["quantity"] != declared:
        add("K4_quantity_declared", False,
            "PWR-05 (L%d) 声明的量口径 = %s, 登记口径 = %s ⇒ 不一致 ⇒ 红" % (row_no, crit["quantity"], declared))
    else:
        add("K4_quantity_declared", True, "PWR-05 声明的量口径 = %s (与登记口径一致)" % crit["quantity"])

    # ── K5 适用性必须与网表 board 域一致 ──
    decl_app = blk.get("applicable_on_demo_main_pcb")
    real_app = truth["applicable_on_demo_main_pcb"]
    if decl_app is None:
        add("K5_applicable", False, "口径页机器块缺 applicable_on_demo_main_pcb")
    elif bool(decl_app) != bool(real_app):
        add("K5_applicable", False,
            "适用性登记与网表不符: 机器块写 applicable_on_demo_main_pcb=%r, 实读网表 board 域 = %r ⇒ 红"
            % (bool(decl_app), truth["boards"]))
    else:
        add("K5_applicable", True,
            "适用性一致 (网表 board 域 %s ⇒ demo 主 PCB 上有充电链 = %r)"
            % (truth["boards"], bool(real_app)))
    if not bool(real_app) and not crit["mentions_scope"]:
        add("K5b_scope_marked", False,
            "网表说充电链在 CHG_BOARD (demo 主 PCB 上不存在该链路) ⇒ PWR-05 必须标注【不适用/整机/充电板】"
            "或改判据对象", severity=known_sev)
    elif not bool(real_app):
        add("K5b_scope_marked", True, "PWR-05 已标注适用范围 (整机/充电板/不适用)")

    # ── K6 证据分级表 ──
    ok, msg = check_evidence_section(root)
    add("K6_evidence_grades", ok, "证据分级: %s" % msg)

    # ── K7 零挂链自证 ──
    gc = os.path.join(root, GATE_CHECK_REL)
    if os.path.isfile(gc):
        cnt = open(gc, encoding="utf-8").read().count(GATE_NAME)
        if cnt:
            add("K7_zero_hook", False,
                "★本闸被挂进 %s (命中 %d 处) ⇒ 零挂链被破坏 ⇒ 红" % (GATE_CHECK_REL, cnt))
        else:
            add("K7_zero_hook", True, "零挂链自证: %s 里命中 %s = 0" % (GATE_CHECK_REL, GATE_NAME))
    else:
        add("K7_zero_hook", True, "零挂链自证: %s 不存在 (沙盒) ⇒ 命中 0" % GATE_CHECK_REL)

    # ── K8 本闸没动 EVT 模板 ──
    evt_md5_after = _md5(evt_path)
    if evt_md5_before == evt_md5_after:
        add("K8_no_write", True, "本闸未改 %s (md5 %s 运行前后逐字相同)" % (EVT_TEMPLATE_REL, evt_md5_after[:8]))
    else:
        add("K8_no_write", False, "★本闸运行前后 %s 的 md5 变了 ⇒ 闸越界写页面 ⇒ 红" % EVT_TEMPLATE_REL)

    # ── K9 读回方式必须可达 (充电 IC 的 I2C 不过铰链 ⇒ SoC 读不到寄存器) ──
    if crit["register_readback"] and not truth["charger_registers_reachable"]:
        add("K9_readback_reachable", False,
            "PWR-05 (L%d) 写『寄存器回读』, 但充电 IC 的 I2C 不跨铰链 (I2C_CHG_* 的 board 域 = %s, "
            "MAIN_PCB 上 0 行) ⇒ SoC 读不到充电 IC 寄存器 ⇒ 判据的读回方式不可达"
            % (row_no, truth["i2c_chg_boards"]), severity=known_sev)
    elif crit["register_readback"]:
        add("K9_readback_reachable", True, "充电 IC 寄存器可达")
    else:
        add("K9_readback_reachable", True, "判据未要求寄存器回读 (无需可达性检查)")

    hard_fail = [f for f in findings if f["severity"] == "fail" and not f["ok"]]
    known = [f for f in findings if f["severity"] == "known" and not f["ok"]]
    rc = 1 if hard_fail else 0
    return {"phase": phase, "strict": strict, "rc": rc, "findings": findings,
            "known_defects": known, "truth": truth, "criterion": crit,
            "row_no": row_no, "standard": standard}


def report(res: dict) -> None:
    print("=" * 78)
    print("ISS-385 · EVT PWR-05 充电电流判据口径闸 · %s 相%s"
          % (res["phase"], " (+strict)" if res.get("strict") else ""))
    print("=" * 78)
    truth = res.get("truth") or {}
    if truth:
        print("硬件真值 (权威表 %s + 网表 %s):" % (POWER_JSON_REL, NETLIST_REL))
        print("  R_ILIM = %g Ω · IINMAX(min/max) = %0.4f / %0.4f A · ICHG(min/typ/max) = %0.4f / %0.4f / %0.4f A"
              % (truth["ri_ohm"], truth["iinmax_min_a"], truth["iinmax_max_a"],
                 truth["ichg_min_a"], truth["ichg_typ_a"], truth["ichg_max_a"]))
        print("  单 pin(max) = %0.4f A · 网表 board 域 %s · demo 主 PCB 上有充电链 = %r"
              % (truth["per_pin_max_a"], truth["boards"], truth["applicable_on_demo_main_pcb"]))
    crit = res.get("criterion") or {}
    if crit:
        lo = [r["value_a"] for r in crit.get("lower", [])]
        hi = [r["value_a"] for r in crit.get("upper", [])]
        print("PWR-05 (L%s) 语义解析: 下限 %s A · 上限 %s A · 量的口径=%s · 寄存器回读=%s"
              % (res.get("row_no"), lo, hi, crit.get("quantity") or "★未声明★",
                 crit.get("register_readback")))
    print("-" * 78)
    for f in res["findings"]:
        tag = "PASS" if f["ok"] else ("KNOWN" if f["severity"] == "known" else "FAIL")
        print("[%s] %-22s %s" % (tag, f["code"], f["msg"]))
    print("-" * 78)
    if res.get("known_defects"):
        print("★已登记的既存缺陷 (pre 相不判红, 但必须被点名; --strict / --phase post 会判红)★")
        for f in res["known_defects"]:
            print("  · [%s] %s" % (f["code"], f["msg"]))
    print("⇒ rc=%d (%s 相)" % (res["rc"], res["phase"]))
    if res["phase"] == "pre" and not res.get("strict"):
        print("★提示: --phase post = 改判据那一趟的验收相 (今天必红) · --strict = 既存缺陷也当红★")


# ── 反向用例自测 (沙盒, 不碰真件) ───────────────────────────────────
def _sandbox_copy(root: str, dst: str) -> str:
    for rel in (EVT_TEMPLATE_REL, CALIBER_REL, POWER_JSON_REL, NETLIST_REL, GATE_CHECK_REL):
        src = os.path.join(root, rel)
        if os.path.isfile(src):
            tgt = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(tgt), exist_ok=True)
            shutil.copy2(src, tgt)   # ★不用 cp -al (本项目吃过硬链接的亏)★
    return dst


def selftest(root: str) -> int:
    sbx_root = os.path.join(root, "tmp", "iss385_sbx", "selftest")
    os.makedirs(sbx_root, exist_ok=True)
    results = []

    def run_case(name, mutate, expect_fail, expect_token, phase="pre", strict=False) -> None:
        d = tempfile.mkdtemp(prefix="case_", dir=sbx_root)
        try:
            _sandbox_copy(root, d)
            mutate(d)
            res = run_checks(d, phase=phase, strict=strict)
            rc = res["rc"]
            blob = " ".join(f["msg"] for f in res["findings"])
            ok = (rc != 0) if expect_fail else (rc == 0)
            if expect_fail and expect_token and expect_token not in blob:
                ok = False
            results.append((name, ok))
            print("[%s] %-52s rc=%d 期望=%s" % ("PASS" if ok else "FAIL", name, rc,
                                                ("rc≠0 且点名「%s」" % expect_token) if expect_fail else "rc=0"))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def edit(path, old, new) -> None:
        t = open(path, encoding="utf-8").read()
        if old not in t:
            raise AssertionError("沙盒改写失败: 找不到 %r" % old)
        open(path, "w", encoding="utf-8").write(t.replace(old, new, 1))

    evt = os.path.join("SW", "EVT_TEMPLATE.md")
    cal = os.path.join("SW", "EVT_CHARGE_CURRENT_CRITERION_CALIBER.md")
    net = os.path.join("HW", "netlist_v1.csv")

    # 基线
    run_case("基线 · 现状 pre 相 (登记口径一致)", lambda d: None, False, "")
    run_case("基线 · 现状 post 相 (现行判据永远判不过)",
             lambda d: None, True, "永远判不过", phase="post")
    run_case("基线 · --strict (既存缺陷也判红)",
             lambda d: None, True, "永远判不过", strict=True)

    # 反向 1: 阈值改成 0.01A (口径被换掉)
    run_case("反向1 · 阈值改成 0.01A ⇒ 口径被换掉 ⇒ 红",
             lambda d: edit(os.path.join(d, evt), "充电电流 ≥ 1.5A", "充电电流 ≥ 0.01A"),
             True, "口径被换掉")
    # 反向 2: 比较符 ≥ 改成 ≤ (语义倒置)
    run_case("反向2 · ≥ 改成 ≤ ⇒ 口径被换掉 ⇒ 红",
             lambda d: edit(os.path.join(d, evt), "充电电流 ≥ 1.5A", "充电电流 ≤ 1.5A"),
             True, "口径被换掉")
    # 反向 3: 阈值改成 1.6A (仍是下限要求, 但数值被换)
    run_case("反向3 · 阈值改成 1.6A ⇒ 口径被换掉 ⇒ 红",
             lambda d: edit(os.path.join(d, evt), "充电电流 ≥ 1.5A", "充电电流 ≥ 1.6A"),
             True, "口径被换掉")
    # 反向 4: PWR-05 行被删 ⇒ 判据消失 ⇒ 红
    run_case("反向4 · PWR-05 行被删 ⇒ 红",
             lambda d: edit(os.path.join(d, evt), "| PWR-05 | 充电检测与充电电流 |",
                            "| PWR-05-OLD | 充电检测与充电电流 |"),
             True, "找不到 PWR-05")
    # 反向 5: 机器块真值被改 ⇒ 与权威表不符 ⇒ 红 (★改的是【值】, 保持 yaml 合法★)
    run_case("反向5 · 机器块 ichg_max_a 被改 ⇒ 红",
             lambda d: edit(os.path.join(d, cal), "ichg_max_a: 0.6974117647058823",
                            "ichg_max_a: 0.9"),
             True, "权威真值")
    # 反向 6: 机器块阻值档被改 ⇒ 红
    run_case("反向6 · 机器块 ri_ohm 被改 ⇒ 红",
             lambda d: edit(os.path.join(d, cal), "ri_ohm: 680", "ri_ohm: 390"),
             True, "权威真值")
    # 反向 7: 适用性造假 (网表说 CHG_BOARD, 机器块写 true)
    run_case("反向7 · 适用性写成 true ⇒ 红",
             lambda d: edit(os.path.join(d, cal), "applicable_on_demo_main_pcb: false",
                            "applicable_on_demo_main_pcb: true"),
             True, "适用性登记与网表不符")
    # 反向 8: 挂链 ⇒ 零挂链被破坏 ⇒ 红
    def hook(d):
        p = os.path.join(d, "state", "gate_check.py")
        t = open(p, encoding="utf-8").read()
        open(p, "w", encoding="utf-8").write(t + "\n# %s\n" % GATE_NAME)
    run_case("反向8 · 本闸被挂进 gate_check.py ⇒ 红", hook, True, "零挂链被破坏")
    # 反向 9: 证据分级表被删 ⇒ 红
    def del_evidence(d):
        p = os.path.join(d, cal)
        t = open(p, encoding="utf-8").read()
        t = re.sub(r"^#{1,4}\s*.*证据分级.*$", "## §5 证据说明", t, count=1, flags=re.M)
        open(p, "w", encoding="utf-8").write(t)
    run_case("反向9 · 证据分级章节被删 ⇒ 红", del_evidence, True, "证据分级")
    # 反向 10: 网表 board 域被改成 MAIN_PCB ⇒ 适用性真值变 ⇒ 与机器块不符 ⇒ 红
    def to_main(d):
        p = os.path.join(d, net)
        t = open(p, encoding="utf-8").read()
        open(p, "w", encoding="utf-8").write(t.replace(",CHG_BOARD", ",MAIN_PCB"))
    run_case("反向10 · 网表 board 域改成 MAIN_PCB ⇒ 适用性登记不符 ⇒ 红",
             to_main, True, "适用性登记与网表不符")
    # 反向 11: 口径页机器块被删 ⇒ 红
    def del_blk(d):
        p = os.path.join(d, cal)
        t = open(p, encoding="utf-8").read()
        t = re.sub(r"```ya?ml[^\n]*\n.*?```", "```\n(机器块已删)\n```", t, count=1, flags=re.S)
        open(p, "w", encoding="utf-8").write(t)
    run_case("反向11 · 口径页机器块被删 ⇒ 红", del_blk, True, "找不到 yaml 机器块")
    # 反向 12: 口径页整个被删 ⇒ 红
    def del_page(d):
        os.remove(os.path.join(d, cal))
    run_case("反向12 · 口径页被删 ⇒ 红", del_page, True, "口径页不存在")
    # 反向 13: 登记的现行口径数被改 (页面没动, 登记动了) ⇒ 红
    run_case("反向13 · 登记口径 evt_current_criterion_a 被改 ⇒ 口径漂移 ⇒ 红",
             lambda d: edit(os.path.join(d, cal), "evt_current_criterion_a: 1.5",
                            "evt_current_criterion_a: 1.2"),
             True, "口径被换掉")
    # 反向 14: 判据被改成窗口写法但登记没同批更新 ⇒ 红
    run_case("反向14 · 判据改成窗口写法 (0.50A≤ICHG≤0.75A) 而登记未同批更新 ⇒ 红",
             lambda d: edit(os.path.join(d, evt), "充电电流 ≥ 1.5A",
                            "电池侧充电电流 ICHG: 0.50A ≤ ICHG ≤ 0.75A"),
             True, "口径被换掉")
    # 不误伤: 同义改写 (数值等价) ⇒ 不红
    run_case("不误伤1 · 1.5A 写成 1500mA (数值等价) ⇒ rc=0",
             lambda d: edit(os.path.join(d, evt), "充电电流 ≥ 1.5A", "充电电流 ≥ 1500mA"), False, "")
    run_case("不误伤2 · 1.5A 写成 1.50 A (数值等价) ⇒ rc=0",
             lambda d: edit(os.path.join(d, evt), "充电电流 ≥ 1.5A", "充电电流 ≥ 1.50 A"), False, "")
    run_case("不误伤3 · 适配器规格 2A 不被误当阈值 ⇒ rc=0",
             lambda d: edit(os.path.join(d, evt), "@5V/2A 适配器", "@5V/3A 适配器"), False, "")

    npass = sum(1 for _, ok in results if ok)
    print("-" * 78)
    print("反向用例 %d/%d 通过" % (npass, len(results)))
    if npass == len(results):
        print("ALL TESTS PASS")
        return 0
    print("SELFTEST FAILED")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="ISS-385 EVT PWR-05 充电电流判据口径闸")
    ap.add_argument("--phase", choices=("pre", "post"), default="pre")
    ap.add_argument("--strict", action="store_true", help="把已登记的既存缺陷也判红")
    ap.add_argument("--root", default=PROJ)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    if args.selftest:
        return selftest(root)
    res = run_checks(root, phase=args.phase, strict=args.strict)
    report(res)
    return res["rc"]


if __name__ == "__main__":
    sys.exit(main())
