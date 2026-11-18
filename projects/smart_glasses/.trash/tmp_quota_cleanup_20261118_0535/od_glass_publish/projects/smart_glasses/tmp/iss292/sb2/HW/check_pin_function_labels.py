#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HW/check_pin_function_labels.py —— ★★【引脚功能名闸】★★ (ISS-239)

★★**为什么必须有这把尺子 (★一句话★)**:
  ★**`state/check_sch_pinfull.py` 的「584 = 584」抓不到引脚功能名串号** ——
  因为原理图符号脚数与脚表脚数**同源派生** (都由 `state/gen_netlist.py` 生成) ⇒ **一起错就一起过** ★
  ⇒ 而脚表 `value` 列里写的是**引脚功能名** ("EN (pin3)" / "GND (pin2)" / "散热焊盘 (pin5, EP)") ⇒
    ★**脚数对 ≠ 功能名对** ⇒ 必须另开一把【查功能名】的尺子 ★

★★**本闸的判据 (★4 类检查·缺一不可★)** ★★

  ① **TPS7A20 族逐脚对账** (`state/gen_netlist_pins.py` 产出的 `HW/netlist_v1_pins.csv`)
     · ★**脚集完整**: 7 颗 × 5 脚必须全在 ⇒ 少一脚 = 硬缺陷 (`MISSING_PIN`)
     · ★**功能名对得上官方 pinout**: 脚表 `value` 里**声明的功能名**必须等于该脚的官方功能名
       ⇒ 不等 = 硬缺陷 (`WRONG_FUNCTION` · ★串号★)
     · ★**引脚号不得串**: `value` 里出现的 `(pinN)` 的 N 必须等于本脚号 ⇒ 否则 = 硬缺陷 (`WRONG_PIN_REF`)
     · ★**"没声明功能名" 不算硬缺陷**: 脚表 `value` 是自由文本列, 器件级 value (型号 "TPS7A20-28")
       **不声明任何脚功能** ⇒ 记为 `NO_FUNCTION` 提示, **不计入 rc** (详见下面「判据口径」)

  ② **同一器件内不许两个脚共用同一个功能名** (★**限死在 IC 类**★)
     · ★**为什么必须限死 IC 类**: 无源件/连接器的 value 本来就重复 (CONN_CAM 13 个 GND /
       CONN_LIGHT 8 个 GND / J_SOM_P3 12 个 EN / J_USB_C 4 个 GND) ⇒ 不限死就是成片误报
     · ★**谁是"器件级 IC"**: 该 ref 的**任一行** `type == "IC"` ⇒ (脚表 `type` 列是**逐行**的,
       pin 级行是 "NET", 所以不能只看单行)

  ③ **官方 pinout 表不许被改软**
     · 内置 pinout 表带 **SHA256 摘要** ⇒ 改表不改摘要 = 红
     · ★**且**交叉核对仓库内两处记录 (`HW/CORE_MODULE_SELECTION.md` / `HW/POWER_RAIL_SPEC.md`) 的原文
       ⇒ 改仓库记录也会红 (出处可当场复核, 不靠本脚本自说自话)

  ④ **受保护文件 md5 未变** (网表 / 脚表 / BOM / 板 / `.kicad_pro` 五个值写死在脚本里)
     · ★**不许为了凑绿去改脚本里的基线值** ⇒ 改基线 = 改代码, 走 review
     · ★**落表批次必须同步更新这 5 个基线值** (网表/脚表 md5 会变) ⇒ 否则本闸会红 ⇒ **这是设计意图**

  ④b **md5 基线可追溯性 (★2026-11-17 补·H-1 重锚第 1 跳·★自己发现的漏★)**
     · ★**为什么必须补**: 只比【盘上 md5 == 脚本基线】的话, ★**改一下脚本里的基线值就能凑绿** ★
       (★这正是 ISS-239 任务书点名的红线★) ⇒ 补一条【台账对账】
     · ★**脚本里的基线 md5 必须能在落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里查到** ★
       ⇒ 查不到 ⇒ `MD5_BASELINE_UNTRACED` 红 ⇒ **"改基线凑绿"这条路被堵死**
     · ★**H-1 重锚链** (`MD5_ANCHOR_CHAIN` · 逐跳留痕) 的**链尾必须 == 当前基线**
       ⇒ 不一致 ⇒ `MD5_CHAIN_INCONSISTENT` 红 ⇒ **用台账里的历史旧值顶替基线也堵死**
     · ★**本闸第 1 跳 (2026-11-17)**: ISS-257 落表 (2026-11-16 21:22) 后 网表/脚表/BOM 三个基线已重锚
       ⇒ 台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18.4 L1069 / L1070 / L1071
       ⇒ **板 / `.kicad_pro` 两个基线逐字节不变 (硬保护)** ⇒ 旧值 (34132f7e… / b21b743a… / c195a117…)
       是【历史事实】, 留痕在 `MD5_ANCHOR_CHAIN` 里, **一个字没抹**

★★**官方 pinout 出处 (★[官网]·自己去 ti.com 查的★)**:
  TI **TPS7A20** datasheet **SBVS338H – MARCH 2020 – REVISED JULY 2024**,
  §4 *Pin Configuration and Functions* → 表 *Pin Functions: X2SON, SOT-23*:
  | NAME | X2SON | SOT-23 | I/O |
  |---|---|---|---|
  | **IN** | **4** | 1 | I |
  | **OUT** | **1** | 5 | O |
  | **EN** | **3** | 3 | I |
  | **GND** | **2** | 2 | — |
  | Thermal Pad | **5** | — | — |
  (N/C 只在 SOT-23 的 pin4, X2SON 无此脚)
  ⇒ ★**X2SON (DQN0004A) = 1=OUT · 2=GND · 3=EN · 4=IN · 5=散热焊盘(接 GND)** ★
  · EN 脚内部 500kΩ 下拉 ⇒ 悬空 = 关断; VEN(LOW) ≤ 0.3V 关断 / VEN(HI) ≥ 0.9V 使能
  · 仓库内两处记录一致: `HW/CORE_MODULE_SELECTION.md` L15 · `HW/POWER_RAIL_SPEC.md` L41

★★**★判据口径 (★不许自己放宽★)** ★★:
  ★**底线一**: 7 颗 LDO 的 **5 个脚必须齐全** ⇒ 少一脚 = 硬缺陷, 不许用"表里没有 IN 就当没有 IN"糊过去
  ★**底线二**: 任何**声明了功能名**的 `value` 必须与官方 pinout **逐脚**一致 ⇒ 串号 = 硬缺陷
  ★**底线三**: `value` 里出现的 `(pinN)` 必须指向本脚 ⇒ 指向别的脚 = 硬缺陷
  ★★**"一条功能名都没声明"的 value (器件级型号) 不算硬缺陷** —— 因为脚表 `value` 是自由文本列,
     器件行 (type=IC) 的 value 是型号, 不是脚功能名 ⇒ 把它算成缺陷 = 把判据放宽成"逐字相等"
     ⇒ ★**本闸记为 `NO_FUNCTION` 提示并打印, 不计入 rc** ★

★**三种运行模式 (★核心交付★)** ★★:
  · `python3 HW/check_pin_function_labels.py`            ⇒ **rc=1** (缺陷还在 ⇒ 该红) + 打印缺陷清单
    ★**首行固定写明「当前基线 = 已知缺陷 ISS-239 ⇒ rc=1 属预期, 落表后应转绿」** ★
  · `python3 HW/check_pin_function_labels.py --expect-known` ⇒ **rc=0** (实算清单与冻结快照**逐条**一致)
    ⇒ **多一条 / 少一条 / 变一条 ⇒ 红**
  · `python3 HW/check_pin_function_labels.py --selftest` ⇒ **rc=0** + **≥6 条反向用例**
    ⇒ ★**每条反向用例都必须自证「它真的改到了目标」** (ISS-227 / ISS-221 同款教训:
       「有断言」≠「断言有效」) ★

★**落表后怎么转绿 (★交 main 的操作说明·本单不落表★)** ★★:
  1. 改 `state/gen_netlist.py` / `state/gen_netlist_pins.py` (真根因改法见 `HW/PIN_FUNCTION_TABLE_CLOSEOUT.md`)
  2. 重跑生成器 ⇒ 网表/脚表 md5 变 ⇒ **同步更新本脚本里 `PROTECTED_MD5` 的 5 个基线值**
     ⇒ ★**并且在 `MD5_ANCHOR_CHAIN` 里追加一跳 (单号 / 旧 md5 / 新 md5 / 落表时刻 / 台账行号)★**
       ⇒ ★**新基线值必须能在落表台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里查到** ⇒ ④b 才不会红 ★
  3. 缺陷清零 ⇒ 更新本脚本里 `KNOWN_DEFECTS` 快照 (或直接删掉 `--expect-known` 分支)
  4. ⇒ 默认模式 rc=0 / `--expect-known` rc=0

用法:
    python3 HW/check_pin_function_labels.py
    python3 HW/check_pin_function_labels.py --expect-known
    python3 HW/check_pin_function_labels.py --selftest
    python3 HW/check_pin_function_labels.py --root /tmp/xxx     # ★指向另一棵项目树 (落表预演用)
    python3 HW/check_pin_function_labels.py --json
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))

# ─────────────────────────── 官方 pinout (★内置真源★) ───────────────────────────
# ★**出处**: TI TPS7A20 datasheet **SBVS338H (2020-03, rev 2024-07)** §4 *Pin Configuration and Functions*
#            → 表 *Pin Functions: X2SON, SOT-23* ⇒ X2SON 列: IN=4 / OUT=1 / EN=3 / GND=2 / ThermalPad=5
# ★**仓库内两处同口径记录**: HW/CORE_MODULE_SELECTION.md L15 · HW/POWER_RAIL_SPEC.md L41
# ★**摘要**: 改这张表而不改下面的摘要 ⇒ ③ 号检查变红 (⇒ pinout 不许被改软)
PINOUT_CANON_PREFIX = "TPS7A20|X2SON(DQN0004A)|"
PINOUT_SHA256 = "15fc9f622518220d8fb9eb0f39f268085b5fd68f61f389ac0f89143099c762a1"

TPS7A20_PINOUT = {
    "pin1": "OUT",
    "pin2": "GND",
    "pin3": "EN",
    "pin4": "IN",
    "pin5": "THERMAL_PAD",
}

# ★**官方功能名 → 脚表 value 里允许出现的标签前缀** (★顺序敏感: 先匹配到的算"声明"★)
OFFICIAL_LABELS = {
    "OUT": (r"^OUT\b",),
    "GND": (r"^GND\b",),
    "EN": (r"^EN\b",),
    "IN": (r"^IN\b",),
    "THERMAL_PAD": (r"^散热焊盘\b", r"^EP\b"),
}

# ★**7 颗 TPS7A20 族位号 (★自己从 HW/netlist_v1_pins.csv 复核出来的★) ★**
TPS7A20_REFS = (
    "U_LDO_S28", "U_LDO_S18B", "U_LDO_S12",
    "U_LDO_L33", "U_LDO_L18", "U_LDO_IO33", "U_LDO_IO18",
)
TPS7A20_PINS = ("pin1", "pin2", "pin3", "pin4", "pin5")

# ★**受保护文件 md5 基线 (★写在脚本里·不许为了凑绿改这里★) ★** ★★H-1 重锚 (2026-11-17 · 本闸第 1 跳): 网表/脚表/BOM 三个基线 = ★**ISS-257 落表后真盘实测值** (台账 `HW/SCHEMATIC_LANDING_V1_LANDED.md` §18.4 L1069/L1070/L1071 · 2026-11-16 21:22) ★** 旧值 (ISS-239 交卷时 = 34132f7e… / b21b743a… / c195a117…) 是历史事实, 逐跳留痕在 `MD5_ANCHOR_CHAIN`★** ★**板 / `.kicad_pro` 两个逐字节不变 (硬保护)★**
PROTECTED_MD5 = {
    "HW/netlist_v1.csv": "e06c1dd633566aa44732762c2ff99d1c",
    "HW/netlist_v1_pins.csv": "287e7861a0d1007748d92d9fbecdd490",
    "HW/BOM_v1.csv": "94642d07a69e8d60dd2af57f69b93607",
    "HW/PCB/demo_mainboard.kicad_pcb": "611b869e13518c3c023fb178f91a0075",
    "HW/PCB/demo_mainboard.kicad_pro": "3e504d2be83152e337949723e909be1b",
}

# ★**仓库内两处官方 pinout 原文 (★出处可当场复核★) ★**
REPO_PINOUT_EVIDENCE = (
    ("HW/CORE_MODULE_SELECTION.md", "1=OUT · 2=GND · 3=EN · 4=IN · 5=散热焊盘→GND"),
    ("HW/POWER_RAIL_SPEC.md", "1=OUT · 2=GND · 3=EN · 4=IN · 5=散热焊盘(→GND)"),
)

# ★**冻结的已知缺陷快照 (★ISS-239 当前基线★) ★**
# ★**键 = "位号.脚号" ⇒ 值 = 该脚应有的官方功能名** ★
KNOWN_DEFECTS = {
    "U_LDO_S28.pin3": "EN",          # ★缺脚★
    "U_LDO_S28.pin4": "IN",
    "U_LDO_S28.pin5": "THERMAL_PAD",
    "U_LDO_S18B.pin4": "IN",
    "U_LDO_S18B.pin5": "THERMAL_PAD",
    "U_LDO_S12.pin4": "IN",
    "U_LDO_S12.pin5": "THERMAL_PAD",
    "U_LDO_L33.pin4": "IN",
    "U_LDO_L33.pin5": "THERMAL_PAD",
    "U_LDO_L18.pin4": "IN",
    "U_LDO_L18.pin5": "THERMAL_PAD",
    "U_LDO_IO33.pin4": "IN",
    "U_LDO_IO33.pin5": "THERMAL_PAD",
    "U_LDO_IO18.pin4": "IN",
    "U_LDO_IO18.pin5": "THERMAL_PAD",
}

KNOWN_DEFECT_BASELINE_NOTE = "当前基线 = 已知缺陷 ISS-239 ⇒ rc=1 属预期, 落表后应转绿"


# ─────────────────────────── 基础工具 ───────────────────────────
def cell(row: dict, key: str) -> str:
    return (row.get(key) or "").strip()


def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def pinout_digest(pinout: dict) -> str:
    canon = PINOUT_CANON_PREFIX + "\n".join(
        "%s=%s" % (k, pinout[k]) for k in sorted(pinout)
    )
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def declared_function(value: str):
    """★从脚表 value 里解出【它声明的功能名】⇒ (功能名|None, 引脚号|None) ★

    ★**"声明"的判据 = value 以官方功能标签开头** —— 因为脚表 `value` 是自由文本列:
      · "EN (pin3)" / "GND (pin2)" / "散热焊盘 (pin5, EP)" / "IN (pin4)" / "OUT (pin1)" ⇒ 声明
      · "TPS7A20-28" (器件级型号) ⇒ **不声明任何脚功能** ⇒ 返回 None
      · "TPS22991RAA (负载开关: 1=VIN/2=ON/3=VOUT/4=GND, ...)" ⇒ 描述里含 GND 但**不是本脚的声明** ⇒ None
        (★若用"含关键词"判 ⇒ U_EN_SW.pin1 会被误判成 GND ⇒ 连带把 IC 限制的判据搞脏★)
    """
    v = (value or "").strip()
    func = None
    for name, pats in OFFICIAL_LABELS.items():
        for p in pats:
            if re.match(p, v):
                func = name
                break
        if func:
            break
    m = re.search(r"pin\s*(\d+)", v)
    return func, (int(m.group(1)) if m else None)


def load_pins_rows(root: str) -> list:
    path = os.path.join(root, "HW", "netlist_v1_pins.csv")
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def index_pins(rows: list) -> dict:
    out = {}
    for r in rows:
        out[(cell(r, "ref"), cell(r, "pin"))] = r
    return out


def device_types(rows: list) -> dict:
    """★ref → 该 ref 出现过的 type 集合 (★脚表 type 列是逐行的, pin 级行是 "NET"★) ★"""
    out = {}
    for r in rows:
        out.setdefault(cell(r, "ref"), set()).add(cell(r, "type"))
    return out


# ─────────────────────────── 检查 ① ② ───────────────────────────
def check1_tps7a20(rows: list) -> tuple:
    """① TPS7A20 族逐脚对账 ⇒ (defects: dict, advisories: list)"""
    idx = index_pins(rows)
    defects = {}
    advisories = []
    for ref in TPS7A20_REFS:
        for pin in TPS7A20_PINS:
            key = "%s.%s" % (ref, pin)
            official = TPS7A20_PINOUT[pin]
            row = idx.get((ref, pin))
            if row is None:
                defects[key] = {
                    "key": key, "ref": ref, "pin": pin, "kind": "MISSING_PIN",
                    "expected": official, "actual": "★脚表里没有这一脚★",
                    "reasons": ["脚表里缺少 %s ⇒ 官方 pinout 要求 %s 必须存在" % (pin, official)],
                }
                continue
            value = cell(row, "value")
            func, pnum = declared_function(value)
            reasons = []
            if func is None:
                advisories.append({
                    "key": key, "ref": ref, "pin": pin, "kind": "NO_FUNCTION",
                    "expected": official, "actual": value,
                    "reasons": ["value 未声明任何官方功能名 (器件级 value) ⇒ 本闸不判为串号"],
                })
            else:
                if func != official:
                    reasons.append("声明功能名 '%s' ≠ 官方 '%s'" % (func, official))
                if pnum is not None and ("pin%d" % pnum) != pin:
                    reasons.append("value 里的引脚号 pin%d ≠ 本脚 %s (★串号★)" % (pnum, pin))
            if reasons:
                defects[key] = {
                    "key": key, "ref": ref, "pin": pin, "kind": "WRONG_FUNCTION",
                    "expected": official, "actual": value, "reasons": reasons,
                }
    return defects, advisories


def check2_no_duplicate_function(rows: list, ic_only: bool = True,
                                 pinout: dict = None) -> dict:
    """② 同一器件内不许两个脚共用同一个功能名 (★限死 IC 类★) ⇒ defects dict"""
    pinout = pinout or TPS7A20_PINOUT
    dtypes = device_types(rows)
    byref = {}
    for r in rows:
        byref.setdefault(cell(r, "ref"), []).append(r)
    defects = {}
    for ref, rlist in sorted(byref.items()):
        if ic_only and "IC" not in dtypes.get(ref, set()):
            continue
        groups = {}
        for r in rlist:
            func, _ = declared_function(cell(r, "value"))
            if func:
                groups.setdefault(func, []).append(cell(r, "pin"))
        for func, pins in sorted(groups.items()):
            if len(pins) < 2:
                continue
            if ref in TPS7A20_REFS:
                # ★有官方 pinout ⇒ 只点名【与本脚官方功能名不符】的那个脚 (★另一个脚是对的★) ★
                culprits = [p for p in pins if pinout.get(p) != func]
                for p in sorted(culprits):
                    key = "%s.%s" % (ref, p)
                    d = defects.setdefault(key, {
                        "key": key, "ref": ref, "pin": p, "kind": "WRONG_FUNCTION",
                        "expected": pinout.get(p, "?"), "actual": "",
                        "reasons": [],
                    })
                    d["reasons"].append(
                        "同器件内功能名重复: '%s' 与 %s 共用 ⇒ 本脚官方应为 '%s'"
                        % (func, sorted(set(pins) - {p}), pinout.get(p, "?")))
            else:
                key = "%s.(重复功能名:%s)" % (ref, func)
                defects[key] = {
                    "key": key, "ref": ref, "pin": "-", "kind": "DUP_FUNCTION_NO_PINOUT",
                    "expected": "★该器件无官方 pinout 真源★",
                    "actual": "%s × %d 脚" % (func, len(pins)),
                    "reasons": ["同器件内 %d 个脚共用功能名 '%s' (%s)"
                                % (len(pins), func, sorted(pins))],
                }
    return defects


def analyze_pins(rows: list, ic_only: bool = True, pinout: dict = None) -> tuple:
    """① + ② 合并 ⇒ (defects: dict, advisories: list)"""
    d1, adv = check1_tps7a20(rows)
    d2 = check2_no_duplicate_function(rows, ic_only=ic_only, pinout=pinout)
    merged = dict(d1)
    for key, d in d2.items():
        if key in merged:
            for r in d.get("reasons", []):
                if r not in merged[key]["reasons"]:
                    merged[key]["reasons"].append(r)
            if merged[key].get("actual", "") == "":
                merged[key]["actual"] = d.get("actual", "")
        else:
            merged[key] = d
    return merged, adv


# ─────────────────────────── 检查 ③ ④ ───────────────────────────
def check3_pinout_integrity(root: str, pinout: dict = None,
                            digest: str = None) -> list:
    """③ 官方 pinout 表不许被改软 ⇒ findings list"""
    pinout = pinout or TPS7A20_PINOUT
    digest = digest or PINOUT_SHA256
    out = []
    got = pinout_digest(pinout)
    if got != digest:
        out.append({
            "key": "pinout.sha256", "kind": "PINOUT_TAMPERED",
            "expected": digest, "actual": got,
            "reasons": ["内置官方 pinout 表的 SHA256 与基线不符 ⇒ 表被改过 (★不许改软★)"],
        })
    if set(pinout) != set(TPS7A20_PINOUT):
        out.append({
            "key": "pinout.keys", "kind": "PINOUT_TAMPERED",
            "expected": sorted(TPS7A20_PINOUT), "actual": sorted(pinout),
            "reasons": ["内置 pinout 的脚集合与基线不符"],
        })
    else:
        for k in sorted(pinout):
            if pinout[k] != TPS7A20_PINOUT[k]:
                out.append({
                    "key": "pinout.%s" % k, "kind": "PINOUT_TAMPERED",
                    "expected": TPS7A20_PINOUT[k], "actual": pinout[k],
                    "reasons": ["内置 pinout 的 %s 被改软" % k],
                })
    # ★交叉核对仓库两处出处原文 ★
    for rel, needle in REPO_PINOUT_EVIDENCE:
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            out.append({
                "key": "evidence.%s" % rel, "kind": "EVIDENCE_MISSING",
                "expected": needle, "actual": "★文件不存在★",
                "reasons": ["出处文件缺失: %s" % rel],
            })
            continue
        txt = open(path, encoding="utf-8", errors="replace").read()
        if needle not in txt:
            out.append({
                "key": "evidence.%s" % rel, "kind": "EVIDENCE_SOFTENED",
                "expected": needle, "actual": "★原文里找不到★",
                "reasons": ["出处文件里的官方 pinout 原文被改软: %s" % rel],
            })
    return out


def check4_protected_md5(root: str, baseline: dict = None) -> list:
    """④ 受保护文件 md5 未变 ⇒ findings list"""
    baseline = baseline or PROTECTED_MD5
    out = []
    for rel, want in sorted(baseline.items()):
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            out.append({
                "key": "md5:%s" % rel, "kind": "MD5_FILE_MISSING",
                "expected": want, "actual": "★文件不存在★",
                "reasons": ["受保护文件缺失: %s" % rel],
            })
            continue
        got = md5_of(path)
        if got != want:
            out.append({
                "key": "md5:%s" % rel, "kind": "MD5_CHANGED",
                "expected": want, "actual": got,
                "reasons": ["受保护文件 md5 变了 ⇒ %s" % rel],
            })
    return out


def check4b_md5_ledger(root: str, baseline: dict = None, ledger_file: str = None,
                       refs: dict = None, chain: dict = None) -> list:
    """④b md5 基线可追溯性 ⇒ findings list

    ★**堵死「改脚本里的基线值来凑绿」这条路**:
      · 脚本里的基线 md5 必须能在★**落表台账**★ `HW/SCHEMATIC_LANDING_V1_LANDED.md` 里查到
        ⇒ 查不到 ⇒ `MD5_BASELINE_UNTRACED` 红
      · ★**H-1 重锚链的链尾必须 == 当前基线** ⇒ 不一致 ⇒ `MD5_CHAIN_INCONSISTENT` 红
        ⇒ ⇒【用台账里的历史旧值顶替基线】也堵死 (旧值虽在台账里, 但 ≠ 盘上现值 ⇒ ④ 先红)
    """
    baseline = baseline or PROTECTED_MD5
    ledger_file = ledger_file or MD5_LEDGER_FILE
    refs = refs if refs is not None else MD5_LEDGER_REFS
    chain = chain if chain is not None else MD5_ANCHOR_CHAIN
    out = []
    path = os.path.join(root, ledger_file)
    if not os.path.exists(path):
        out.append({
            "key": "md5ledger:%s" % ledger_file, "kind": "MD5_LEDGER_MISSING",
            "expected": ledger_file, "actual": "★文件不存在★",
            "reasons": ["落表台账不存在 ⇒ 无法证明 md5 基线可追溯 (★本闸要求落表台账在树里★)"],
        })
        return out
    txt = open(path, encoding="utf-8", errors="replace").read()
    for rel, ref in sorted(refs.items()):
        want = baseline.get(rel, "")
        if not want:
            continue
        if want not in txt:
            out.append({
                "key": "md5ledger:%s" % rel, "kind": "MD5_BASELINE_UNTRACED",
                "expected": "%s ∈ %s (%s)" % (want, ledger_file, ref),
                "actual": "★落表台账里查不到这个 md5★",
                "reasons": ["脚本里的基线 md5 在落表台账里查不到 ⇒ 疑似【改基线凑绿】 "
                            "(★台账 %s %s★)" % (ledger_file, ref)],
            })
        ch = chain.get(rel) or []
        if ch and ch[-1][2] != want:
            out.append({
                "key": "md5chain:%s" % rel, "kind": "MD5_CHAIN_INCONSISTENT",
                "expected": ch[-1][2], "actual": want,
                "reasons": ["H-1 重锚链的链尾与脚本基线不一致 (★链尾 = %s %s★)"
                            % (ch[-1][0], ch[-1][4])],
            })
    return out


# ─────────────────────────── 已知缺陷快照比对 ───────────────────────────
def compare_known(computed: dict, known: dict) -> dict:
    """★实算缺陷清单 vs 冻结快照 ⇒ (ok, 差异说明 list) ★"""
    diffs = []
    ck = set(computed)
    kk = set(known)
    for k in sorted(ck - kk):
        diffs.append("多出一条: %s (实算存在, 快照里没有)" % k)
    for k in sorted(kk - ck):
        diffs.append("少了一条: %s (快照里有, 实算没有)" % k)
    for k in sorted(ck & kk):
        if computed[k].get("expected") != known[k]:
            diffs.append("变了一条: %s 期望功能名 %s ≠ 快照 %s"
                          % (k, computed[k].get("expected"), known[k]))
    return {"ok": not diffs, "diffs": diffs}


# ─────────────────────────── 打印 ───────────────────────────
def print_audit_matrix(rows: list) -> None:
    """★35 行逐脚对账矩阵 (★7 颗 × 5 脚★) ★"""
    idx = index_pins(rows)
    print("  ── 35 行逐脚对账矩阵 (官方 pinout 出处: TI TPS7A20 SBVS338H §4) ──")
    print("     ★图例: ✔ 对 · ✘ 错(串号) · ○ value 未声明功能名(器件级·提示) · ★缺脚★ 该脚不存在")
    head = "     %-14s" % "位号"
    for p in TPS7A20_PINS:
        head += " %-22s" % ("%s(%s)" % (p, TPS7A20_PINOUT[p]))
    print(head)
    for ref in TPS7A20_REFS:
        line = "     %-14s" % ref
        for p in TPS7A20_PINS:
            r = idx.get((ref, p))
            if r is None:
                line += " %-22s" % "★缺脚★"
                continue
            v = cell(r, "value")
            func, pnum = declared_function(v)
            ok = (func == TPS7A20_PINOUT[p]) and (pnum is None or ("pin%d" % pnum) == p)
            if ok:
                mark = "✔"
            elif func is None:
                mark = "○"
            else:
                mark = "✘"
            show = v if len(v) <= 14 else v[:13] + "…"
            line += " %-22s" % ("%s %s" % (mark, show))
        print(line)


def print_defects(defects: dict) -> None:
    print("  ── 【缺陷清单 (★计入 rc·共 %d 条★)】 ──" % len(defects))
    for key in sorted(defects):
        d = defects[key]
        print("   · %-18s [%s] 官方应为 %-12s 脚表现值 %-28r"
              % (key, d["kind"], d["expected"], d.get("actual", "")))
        for r in d.get("reasons", []):
            print("       - %s" % r)


def print_advisories(adv: list) -> None:
    if not adv:
        return
    print("  ── 【提示 (★不计入 rc★·共 %d 条★)】 ──" % len(adv))
    for a in adv:
        print("   · %-18s [%s] 官方应为 %-12s 现值 %r"
              % (a["key"], a["kind"], a["expected"], a.get("actual", "")))


# ─────────────────────────── 主流程 ───────────────────────────
def run(root: str) -> dict:
    rows = load_pins_rows(root)
    defects, advisories = analyze_pins(rows)
    pinout_f = check3_pinout_integrity(root)
    md5_f = check4_protected_md5(root) + check4b_md5_ledger(root)
    all_defects = dict(defects)
    for f in pinout_f + md5_f:
        all_defects[f["key"]] = f
    return {"rows": rows, "defects": defects, "advisories": advisories,
            "pinout_findings": pinout_f, "md5_findings": md5_f,
            "all_defects": all_defects}


def main_default(root: str, as_json: bool) -> int:
    res = run(root)
    defects = res["defects"]
    pinout_f = res["pinout_findings"]
    md5_f = res["md5_findings"]
    total = len(defects) + len(pinout_f) + len(md5_f)
    if as_json:
        print(json.dumps({
            "rc": 1 if total else 0,
            "known_defect_baseline": KNOWN_DEFECT_BASELINE_NOTE,
            "defects": [defects[k] for k in sorted(defects)],
            "advisories": res["advisories"],
            "pinout_findings": pinout_f,
            "md5_findings": md5_f,
        }, ensure_ascii=False, indent=1))
        return 1 if total else 0

    # ★★首行固定写明"rc=1 属预期"★★
    print("★当前基线 = 已知缺陷 ISS-239 ⇒ rc=1 属预期, 落表后应转绿★")
    print("═══ 引脚功能名闸 (★pin_function_labels · root=%s★)" % root)
    print("  [口径] 官方 pinout = TI TPS7A20 SBVS338H §4 (X2SON: 1=OUT 2=GND 3=EN 4=IN 5=散热焊盘)")
    print("  [口径] 脚表 = HW/netlist_v1_pins.csv (%d 行 / %d 脚) · 7 颗 TPS7A20 × 5 脚 = 35 行"
          % (len(res["rows"]), len(res["rows"])))
    print()
    print_audit_matrix(res["rows"])
    print()
    print_defects(defects)
    print()
    print_advisories(res["advisories"])
    if pinout_f:
        print()
        print("  ── 【③ 官方 pinout 完整性】 ──")
        for f in pinout_f:
            print("   · %-22s [%s] 期望 %r 实得 %r" % (f["key"], f["kind"], f["expected"], f["actual"]))
    if md5_f:
        print()
        print("  ── 【④/④b 受保护文件 md5 + 基线可追溯性 (★台账对账★)】 ──")
        for f in md5_f:
            print("   · %-40s [%s] 期望 %s 实得 %s" % (f["key"], f["kind"], f["expected"], f["actual"]))
    else:
        print()
        print("  ── 【④/④b 受保护文件 md5 + 基线可追溯性】 5 个基线全部一致 + 3 个基线在落表台账里可查 ✔")
    print()
    print("  判定: %s" % ("❌ 不过 (%d 条缺陷) ⇒ ★当前是已知缺陷基线, 落表批次里修★" % total
                          if total else "✅ 过 (0 条缺陷) ⇒ 已转绿"))
    return 1 if total else 0


def main_expect_known(root: str) -> int:
    res = run(root)
    computed = res["defects"]
    cmp = compare_known(computed, KNOWN_DEFECTS)
    other = res["pinout_findings"] + res["md5_findings"]
    print("═══ 引脚功能名闸 · ★--expect-known★ 已知缺陷快照核对 ═══")
    print("  [基线] %s" % KNOWN_DEFECT_BASELINE_NOTE)
    print("  快照条数 = %d · 实算条数 = %d" % (len(KNOWN_DEFECTS), len(computed)))
    if not cmp["ok"]:
        print("  ❌ 快照与实算不一致 ⇒ 逐条差异:")
        for d in cmp["diffs"]:
            print("     · %s" % d)
    else:
        print("  ✅ 实算清单与冻结快照逐条一致 (%d/%d)" % (len(computed), len(KNOWN_DEFECTS)))
    if other:
        print("  ❌ 另有 %d 条非快照类缺陷 (③ pinout / ④ md5):" % len(other))
        for f in other:
            print("     · %-40s [%s] 期望 %s 实得 %s" % (f["key"], f["kind"], f["expected"], f["actual"]))
    rc = 0 if (cmp["ok"] and not other) else 1
    print("  判定: %s" % ("✅ 过 (rc=0) ⇒ 当前状态确为已知缺陷基线" if rc == 0 else "❌ 不过 (rc=1)"))
    return rc


# ─────────────────────────── 自测 (★≥6 条反向用例★) ───────────────────────────
def _synth_rows(overrides=None, drop=(), extra=()):
    """★造一份"全部正确"的合成脚表 (★只有 TPS7A20 7 颗·足够验 ①②★) ★"""
    base = {
        "U_LDO_S28": {"pin1": "OUT (pin1)", "pin2": "GND (pin2)", "pin3": "EN (pin3)",
                       "pin4": "IN (pin4)", "pin5": "散热焊盘 (pin5, EP)"},
        "U_LDO_S18B": {"pin1": "OUT (pin1)", "pin2": "GND (pin2)", "pin3": "EN (pin3)",
                       "pin4": "IN (pin4)", "pin5": "散热焊盘 (pin5, EP)"},
        "U_LDO_S12": {"pin1": "OUT (pin1)", "pin2": "GND (pin2)", "pin3": "EN (pin3)",
                      "pin4": "IN (pin4)", "pin5": "散热焊盘 (pin5, EP)"},
        "U_LDO_L33": {"pin1": "OUT (pin1)", "pin2": "GND (pin2)", "pin3": "EN (pin3)",
                      "pin4": "IN (pin4)", "pin5": "散热焊盘 (pin5, EP)"},
        "U_LDO_L18": {"pin1": "OUT (pin1)", "pin2": "GND (pin2)", "pin3": "EN (pin3)",
                      "pin4": "IN (pin4)", "pin5": "散热焊盘 (pin5, EP)"},
        "U_LDO_IO33": {"pin1": "OUT (pin1)", "pin2": "GND (pin2)", "pin3": "EN (pin3)",
                       "pin4": "IN (pin4)", "pin5": "散热焊盘 (pin5, EP)"},
        "U_LDO_IO18": {"pin1": "OUT (pin1)", "pin2": "GND (pin2)", "pin3": "EN (pin3)",
                       "pin4": "IN (pin4)", "pin5": "散热焊盘 (pin5, EP)"},
    }
    if overrides:
        for (ref, pin), val in overrides.items():
            base.setdefault(ref, {})[pin] = val
    rows = []
    for ref, pins in base.items():
        for pin, val in pins.items():
            if (ref, pin) in drop:
                continue
            rows.append({"ref": ref, "pin": pin, "value": val, "type": "NET"})
        rows.append({"ref": ref, "pin": "pin1", "value": base[ref]["pin1"], "type": "IC"})
    for r in extra:
        rows.append(r)
    return rows


def selftest() -> int:
    """★≥6 条反向用例 ★**每条都必须自证「它真的改到了目标」** ★"""
    fails = []
    cases = []

    # ── T1 ★把某颗的 pin4 改回 "EN (pin3)" ⇒ 仍被点名★★
    rows = _synth_rows(overrides={("U_LDO_L33", "pin4"): "EN (pin3)"})
    d, _ = analyze_pins(rows)
    hit = "U_LDO_L33.pin4" in d
    if not hit:
        fails.append("T1 失效: pin4 改回 'EN (pin3)' 竟没被点名")
    elif set(d) != {"U_LDO_L33.pin4"}:
        fails.append("T1 越界: 期望只点 %s, 实得 %s" % ("U_LDO_L33.pin4", sorted(d)))
    else:
        cases.append(("T1 串号仍被点名 (pin4 改回 'EN (pin3)')", "点-named=%s" % sorted(d)))
    # ★自证: 不改的话应当是干净的 ⇒ 证明 T1 的红确实来自这次改动★
    d_clean, _ = analyze_pins(_synth_rows())
    if d_clean:
        fails.append("T1 前提不成立: 未改动的合成样本本应 0 缺陷, 实得 %s" % sorted(d_clean))

    # ── T2 ★删掉已知清单里一条 ⇒ --expect-known 红★★
    #   ★**用【合成快照】而不是真快照** ⇒ 落表后 (快照清空) 本用例依然有效 (★fix-point 稳定★) ★
    synth_known = dict(KNOWN_DEFECTS)
    synth_known["U_LDO_IO18.pin5"] = "THERMAL_PAD"
    known = dict(synth_known)
    removed = "U_LDO_IO18.pin5"
    known.pop(removed, None)
    cmp = compare_known({k: {"expected": v} for k, v in synth_known.items()}, known)
    if cmp["ok"]:
        fails.append("T2 失效: 快照少一条竟仍判一致")
    elif not any(removed in d for d in cmp["diffs"]):
        fails.append("T2 差异信息没指出被删的那条: %s" % cmp["diffs"])
    else:
        cases.append(("T2 快照少一条 ⇒ 判红", "diff=%s" % cmp["diffs"][0]))

    # ── T3 ★篡改内置 pinout 表 ⇒ 红★★
    tampered = dict(TPS7A20_PINOUT)
    tampered["pin4"] = "EN"
    if pinout_digest(tampered) == PINOUT_SHA256:
        fails.append("T3 失效: 篡改后的 pinout 摘要没变 ⇒ 摘要没生效")
    else:
        f = check3_pinout_integrity(PROJ, pinout=tampered)
        if not f:
            fails.append("T3 失效: 篡改 pinout 后 ③ 号检查竟没报")
        else:
            cases.append(("T3 篡改 pinout 表 ⇒ 红", "报=%s" % [x["key"] for x in f]))

    # ── T4 ★把 pin4 改成 "IN (pin4)" ⇒ 该条从清单里消失 且 --expect-known 红★★
    rows = _synth_rows(overrides={("U_LDO_L33", "pin4"): "IN (pin4)"})
    d, _ = analyze_pins(rows)
    if "U_LDO_L33.pin4" in d:
        fails.append("T4 失效: pin4 改成 'IN (pin4)' 后仍在缺陷清单里")
    else:
        # ★合成快照里【有】这一条 ⇒ 实算没有 ⇒ 必须判红 ★
        sk = dict(KNOWN_DEFECTS)
        sk["U_LDO_L33.pin4"] = "IN"
        cmp = compare_known(d, sk)
        if cmp["ok"]:
            fails.append("T4 失效: 缺陷消失后 --expect-known 竟仍判一致")
        else:
            cases.append(("T4 pin4 改成 'IN (pin4)' ⇒ 该条消失且快照判红",
                          "diff 数=%d" % len(cmp["diffs"])))

    # ── T5 ★篡改受保护 md5 基线 ⇒ 红★★
    bad_base = dict(PROTECTED_MD5)
    bad_base["HW/netlist_v1.csv"] = "0" * 32
    f = check4_protected_md5(PROJ, baseline=bad_base)
    if not f:
        fails.append("T5 失效: 篡改 md5 基线竟没报")
    else:
        # ★自证: 正常基线必须是干净的 ⇒ 证明红确实来自这次篡改★
        f_ok = check4_protected_md5(PROJ)
        if f_ok:
            fails.append("T5 前提不成立: 正常基线本应干净, 实得 %s" % [x["key"] for x in f_ok])
        else:
            cases.append(("T5 篡改受保护 md5 基线 ⇒ 红", "报=%s" % [x["key"] for x in f]))

    # ── T6 ★把 IC 限制放宽到无源件 ⇒ 红 (★且证明这条限制是承重的★) ★★
    passive = [{"ref": "R_TMP", "pin": "pin1", "value": "GND (pin1)", "type": "R"},
               {"ref": "R_TMP", "pin": "pin2", "value": "GND (pin2)", "type": "R"},
               {"ref": "R_TMP", "pin": "pin3", "value": "GND (pin3)", "type": "R"}]
    d_on, _ = analyze_pins(_synth_rows(extra=passive), ic_only=True)
    d_off, _ = analyze_pins(_synth_rows(extra=passive), ic_only=False)
    if any(k.startswith("R_TMP") for k in d_on):
        fails.append("T6 失效: 限死 IC 类时仍误报了无源件 R_TMP ⇒ 判据被放宽了")
    elif not any(k.startswith("R_TMP") for k in d_off):
        fails.append("T6 失效: 放宽到无源件后竟没报错 ⇒ '限死 IC' 这条限制不是承重的")
    else:
        cases.append(("T6 放宽到无源件 ⇒ 红 (限死 IC 是承重的)",
                      "IC 限制开=%d 条 / 关=%d 条" % (len(d_on), len(d_off))))

    # ── T7 ★删掉 U_LDO_S28 的 pin3 行 ⇒ 报"缺脚"★★
    rows = _synth_rows(drop={("U_LDO_S28", "pin3")})
    d, _ = analyze_pins(rows)
    if d.get("U_LDO_S28.pin3", {}).get("kind") != "MISSING_PIN":
        fails.append("T7 失效: 删掉 U_LDO_S28.pin3 未报缺脚")
    else:
        cases.append(("T7 删掉 U_LDO_S28.pin3 ⇒ 报缺脚", "kind=%s" % d["U_LDO_S28.pin3"]["kind"]))

    # ── T8 ★把 U_LDO_S28 的 pin3 补上 ⇒ 缺脚缺陷消失 且 --expect-known 红★★
    rows = _synth_rows()
    d, _ = analyze_pins(rows)
    if "U_LDO_S28.pin3" in d:
        fails.append("T8 失效: pin3 补齐后缺脚缺陷仍在")
    else:
        sk = dict(KNOWN_DEFECTS)
        sk["U_LDO_S28.pin3"] = "EN"
        cmp = compare_known(d, sk)
        if cmp["ok"]:
            fails.append("T8 失效: 补齐后 --expect-known 竟仍判一致")
        else:
            cases.append(("T8 补上 U_LDO_S28.pin3 ⇒ 缺脚消失且快照判红",
                          "diff 数=%d" % len(cmp["diffs"])))

    # ── T9 ★真盘核对: 当前基线必须是【恰好 15 条】(14 串号 + 1 缺脚)★★
    try:
        real = load_pins_rows(PROJ)
    except Exception as exc:  # noqa: BLE001
        fails.append("T9 失败: 读不到真脚表 (%s)" % exc)
        real = []
    if real:
        d_real, adv_real = analyze_pins(real)
        cmp = compare_known(d_real, KNOWN_DEFECTS)
        if not cmp["ok"]:
            fails.append("T9 失效: 真盘实算与冻结快照不一致: %s ⇒ ★**落表批次忘了同步更新 KNOWN_DEFECTS "
                         "与它的 SHA256 (★清零后应把快照改成空★)**" % cmp["diffs"][:3])
        else:
            # ★★【快照非空时 = 当前基线】必须恰好 15 条 = 14 串号 + 1 缺脚 ★★
            #   ★**快照清空 (落表后) ⇒ 本段 vacuous ⇒ selftest 仍然是绿的** (★fix-point 稳定★)
            if KNOWN_DEFECTS:
                n_missing = sum(1 for v in d_real.values() if v["kind"] == "MISSING_PIN")
                n_wrong = sum(1 for v in d_real.values() if v["kind"] == "WRONG_FUNCTION")
                if len(d_real) != 15 or n_missing != 1 or n_wrong != 14:
                    fails.append("T9 失效: 真盘实算缺陷 = %d 条 (缺脚 %d / 串号 %d) ⇒ 期望 15 = 14 串号 + 1 缺脚"
                                 % (len(d_real), n_missing, n_wrong))
                else:
                    wrong_keys = {k for k, v in d_real.items() if v["kind"] == "WRONG_FUNCTION"}
                    expect = {"%s.pin%d" % (r, p) for r in TPS7A20_REFS for p in (4, 5)}
                    if wrong_keys != expect:
                        fails.append("T9 失效: 串号集合不是【7 颗 × {pin4,pin5}】⇒ 实得 %s" % sorted(wrong_keys))
            cases.append(("T9 真盘实算与冻结快照逐条一致 (★快照非空时=15 条: 14 串号 + 1 缺脚★)",
                          "实算 %d 条 · 提示(NO_FUNCTION)=%d 条" % (len(d_real), len(adv_real))))

    # ── T10 ★快照条目本身不许被偷改 (★KNOWN_DEFECTS 也要有摘要★) ★
    known_canon = "\n".join("%s=%s" % (k, KNOWN_DEFECTS[k]) for k in sorted(KNOWN_DEFECTS))
    known_digest = hashlib.sha256(known_canon.encode("utf-8")).hexdigest()
    if not KNOWN_SNAPSHOT_SHA256:
        fails.append("T10 失效: 快照基线摘要为空")
    elif known_digest != KNOWN_SNAPSHOT_SHA256:
        fails.append("T10 失效: 已知缺陷快照的 SHA256 与基线不符 ⇒ 快照被偷改")
    else:
        cases.append(("T10 已知缺陷快照 SHA256 一致 (快照不许偷改)", known_digest[:16] + "…"))

    # ── T11 ★把 md5 基线改成【落表台账里查不到】的任意值 ⇒ ④ 与 ④b 必须同时红 ★
    bad = dict(PROTECTED_MD5)
    bad["HW/netlist_v1.csv"] = "deadbeef" * 4
    f4 = check4_protected_md5(PROJ, baseline=bad)
    f4b = check4b_md5_ledger(PROJ, baseline=bad)
    kinds = {x["kind"] for x in f4 + f4b}
    if "MD5_CHANGED" not in kinds:
        fails.append("T11 失效: 篡改 md5 基线后 ④ 没报 MD5_CHANGED")
    elif "MD5_BASELINE_UNTRACED" not in kinds:
        fails.append("T11 失效: 篡改 md5 基线后 ④b 没报 MD5_BASELINE_UNTRACED "
                     "(★台账对账不是承重的·白写的★)")
    else:
        # ★自证: 正常基线必须是干净的 (④ + ④b) ⇒ 证明红确实来自这次篡改★
        if check4_protected_md5(PROJ) or check4b_md5_ledger(PROJ):
            fails.append("T11 前提不成立: 正常基线本应干净")
        else:
            cases.append(("T11 改基线凑绿 ⇒ ④+④b 双红 (★台账里查不到这个 md5★)",
                          "报=%s" % sorted(kinds)))

    # ── T12 ★把 md5 基线改成【落表台账里的历史旧值】⇒ 仍然红 (★用旧值顶替不算数★) ★
    old = dict(PROTECTED_MD5)
    old["HW/netlist_v1.csv"] = "34132f7e40a241e1fae1476be0eafbd5"   # ★ISS-233 之后的旧值 (台账里查得到) ★
    f = check4_protected_md5(PROJ, baseline=old) + check4b_md5_ledger(PROJ, baseline=old)
    if not f:
        fails.append("T12 失效: 用落表台账里的历史旧值顶替基线竟没报 "
                     "(★旧值 ≠ 盘上现值 ⇒ 必须红★)")
    else:
        cases.append(("T12 用落表台账里的历史旧值顶替基线 ⇒ 仍红",
                      "报=%s" % sorted({x["kind"] for x in f})))

    # ── T13 ★链尾与基线不一致 ⇒ 红 (★H-1 重锚链不是摆设★) ★
    ch = {k: list(v) for k, v in MD5_ANCHOR_CHAIN.items()}
    ch["HW/netlist_v1.csv"] = ch["HW/netlist_v1.csv"][:-1]   # ★把链尾砍掉 ⇒ 链尾 ≠ 基线 ★
    f = check4b_md5_ledger(PROJ, chain=ch)
    if not f:
        fails.append("T13 失效: 砍掉 H-1 重锚链的链尾竟没报 (★链尾检查不是承重的★)")
    else:
        cases.append(("T13 砍掉 H-1 重锚链的链尾 ⇒ ④b 红",
                      "报=%s" % [x["kind"] for x in f]))

    print("═══ 引脚功能名闸 · ★--selftest★ 反向用例自测 ═══")
    for i, (name, detail) in enumerate(cases, start=1):
        print("   [T%-2d] ✔ %s  —— %s" % (i, name, detail))
    if fails:
        for f in fails:
            print("   ❌ %s" % f)
        print("SELFTEST FAILED (%d 条失效)" % len(fails))
        return 1
    print("ALL TESTS PASS (%d/%d 条反向用例, 每条均自证改到了目标)" % (len(cases), len(cases)))
    return 0


# ★**已知缺陷快照的 SHA256 (★硬编码基线·不许与 KNOWN_DEFECTS 一起被偷改★)** ★
# ★**改 KNOWN_DEFECTS 就必须同时改这一行, 且必须在交卷单里说明为什么改 (★落表批次清零时改★)** ★
KNOWN_SNAPSHOT_SHA256 = "4b48cfee483dfd8a4931c518aa13151be869c54a90f0cd04925e9f67436deca1"


# ─────────────────── ④b 落表台账对账 (★H-1 重锚可追溯★·2026-11-17 补) ───────────────────
# ★**为什么必须补这一条 (★ISS-239 交卷后自己发现的漏★)**:
#   ④ 号检查只比【盘上 md5 == 脚本里的基线】⇒ ★**光有这一条, 谁都可以直接改脚本里的基线值来凑绿** ★
#   (★这正是 ISS-239 任务书点名的红线: 「不许改脚本里的基线值来凑绿」★)
#   ⇒ 补一条【台账对账】: ★**脚本里的基线值必须能在落表台账里查到** ★
#   ⇒ 落表台账 = `HW/SCHEMATIC_LANDING_V1_LANDED.md` (★落表批次的唯一真源登记处★)
#   ⇒ 【改基线凑绿】这条路被堵死: 台账里查不到的 md5 ⇒ ④b 红 ★
MD5_LEDGER_FILE = "HW/SCHEMATIC_LANDING_V1_LANDED.md"

# ★**哪些文件走台账对账 (★落表会变的 3 个★); 板 / `.kicad_pro` 是硬保护, 走纯 md5 比对 ★**
MD5_LEDGER_REFS = {
    "HW/netlist_v1.csv": "§18.4 L1069 (ISS-257 · 2026-11-16 21:22)",
    "HW/netlist_v1_pins.csv": "§18.4 L1070 (ISS-257 · 2026-11-16 21:22)",
    "HW/BOM_v1.csv": "§18.4 L1071 (ISS-257 · 2026-11-16 21:22)",
}

# ★**H-1 重锚链 (★追加式留痕·历史不改·逐条可回台账核★)** ★
#   ★**链尾必须 == `PROTECTED_MD5` 里的当前基线** ⇒ 不一致 ⇒ `MD5_CHAIN_INCONSISTENT` 红
MD5_ANCHOR_CHAIN = {
    "HW/netlist_v1.csv": [
        ("ISS-233", "3215020b6d4120e1b7728227effdc6d3", "34132f7e40a241e1fae1476be0eafbd5", "2026-11-16 06:48", "§15.4 L552"),
        ("ISS-243", "34132f7e40a241e1fae1476be0eafbd5", "611c3ba3db3dc7de7213063375b96d01", "2026-11-16 15:45", "§16.4 L656"),
        ("ISS-249", "611c3ba3db3dc7de7213063375b96d01", "16ac89f77c25a3f61834cc7ebcd78a7f", "2026-11-16 19:3x", "§17.5 L852"),
        ("ISS-257", "16ac89f77c25a3f61834cc7ebcd78a7f", "e06c1dd633566aa44732762c2ff99d1c", "2026-11-16 21:22", "§18.4 L1069"),
    ],
    "HW/netlist_v1_pins.csv": [
        ("ISS-233", "a600afae493f5a7a6c55f46ad35ac89c", "b21b743a7702d30729f0d653c15392df", "2026-11-16 06:48", "§15.4 L553"),
        ("ISS-243", "b21b743a7702d30729f0d653c15392df", "ef436a37412ac9b6eac3c9f41f1edca4", "2026-11-16 15:45", "§16.4 L657"),
        ("ISS-257", "ef436a37412ac9b6eac3c9f41f1edca4", "287e7861a0d1007748d92d9fbecdd490", "2026-11-16 21:22", "§18.4 L1070"),
    ],
    "HW/BOM_v1.csv": [
        ("ISS-233", "92b51580867deca9f8b04af88d925d96", "c195a117ff17490d4d1e1a5b8f1995a7", "2026-11-16 06:48", "§15.4 L554"),
        ("ISS-243", "c195a117ff17490d4d1e1a5b8f1995a7", "2a7305741134788dfee9f13f34c656b4", "2026-11-16 15:45", "§16.4 L658"),
        ("ISS-257", "2a7305741134788dfee9f13f34c656b4", "94642d07a69e8d60dd2af57f69b93607", "2026-11-16 21:22", "§18.4 L1071"),
    ],
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="引脚功能名闸 (ISS-239)")
    ap.add_argument("--expect-known", action="store_true",
                    help="实算缺陷清单必须与冻结快照逐条一致 (rc=0)")
    ap.add_argument("--selftest", action="store_true", help="跑反向用例自测 (rc=0)")
    ap.add_argument("--root", default=PROJ, help="项目根目录 (默认 = 本脚本上级)")
    ap.add_argument("--json", action="store_true", help="机器读格式")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    root = os.path.abspath(args.root)
    if args.expect_known:
        return main_expect_known(root)
    return main_default(root, args.json)


if __name__ == "__main__":
    sys.exit(main())
