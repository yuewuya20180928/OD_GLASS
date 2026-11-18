#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-280 · 「板只改一次」的【提交时序守卫】机器闸
=================================================================================================
派活: state/dispatch_briefs/ISS-280_hw_commit_order_guard.md (项目总工 2026-11-17 08:3x)

★**本闸守的是【什么时候跑 / 板 md5 变了几次】, 不是板本身** ⇒ ★**零写板 · 零落表 · 零改网表/脚表/BOM** ★
★**不执行任何一步 (S1~S13 一律不许跑) —— 本闸只【读】作业包 / 台账 / 板文件 / 留证产物** ★

★**它补的是哪个洞 (★main 08:2x 实查★)**:
  · `state/chain_gate.py`         ⇒ 判「产物比板新」(★mtime 口径★) ⇒ ★**判不了「板改了几次」** ★
  · `HW/check_onepass_preflight_coverage.py` (ISS-277) ⇒ 判「板侧项有没有漏进作业包」⇒ **也不判时序** ★
  ⇒ ★**「板只改一次」这条全项目最贵的铁律, 在本闸之前是靠人记着的** ★

七条判据:
  D0 (附加) 权威页存在且含 INV-1~INV-4 锚点 + 受保护 3 件 (网表/脚表/BOM) md5 逐字节不变 (零落表)
  D1        作业包必须存在「B 类终段步 (S9/S10/S12/S13) = 最后跑」的显式表述      (★缺 ⇒ 红★)
  D2        作业包必须存在「板 md5 只允许变一次 / S4/S8 与 S1/S2/S3/S6/S7 同趟」的显式表述 (★缺 ⇒ 红★)
  D3        作业包【不得】再把 S9/S10/S11/S12/S13 列进「现在就能做完」的集合      (★仍列着 ⇒ 红★)
  D4        盘上板 md5 == 台账最后一次登记的板 md5 (变更区 0 行时 == 基线 md5)   (★不一致 ⇒ 红★)
  D5        变更台账的变更次数 ≤ 1                                             (★≥2 ⇒ 红★)
  D6        若变更次数 = 1 ⇒ 那一版必须被留证产物绑定                             (★没绑定 ⇒ 红★)

★**★D3 的机器形式 (★因为作业包只许追加, 不许删老字★)**:
  「现在就能做完」这类集合断言, 必然在盘上留下【若干行断言文本】(★§0 表那行 + ISS-268 那行 + §6.1 末行★)
  ⇒ 本闸的判法 = ★**凡含 B 类步 (S9/S10/S11/S12/S13) 的集合断言行, 必须被【后文】一条显式【撤回】订正覆盖** ★
  ⇒ ★**撤回行 = 含撤回动词 (撤回/作废/不成立/推翻/不许跑…) 且含 ISS-280 或「订正」, 且点了 B 类步的名字** ★
  ⇒ ★**没撤回 ⇒ 旧集合仍生效 ⇒ 红** ★ (★注意: 撤回行本身不算断言行 ⇒ 不会自相矛盾★)

★**★D4 的口径 (★与任务书原文的一处细化, ★在此留痕★)**:
  任务书原文 = 「盘上板 md5 == 台账登记的基线 md5」
  本闸实现   = 「盘上板 md5 == 台账【最后一次登记】的板 md5」
  ⇒ ★**变更区 0 行时二者完全一致 (== 基线 md5); 变更区 1 行时 == 那一行的【改后 md5】** ★
  理由 = ★**若死守「永远 == 基线」, 合法的那一次变更一落地 D4 就红 ⇒ 闸会逼着人【永远不许改板】★**
  ⇒ ★**⇒ 与任务书 ⑤-2「板改一次是合法的, 判据是 ≤1 次不是不许改」一致★** ★

退出码: 0 = 全过 · 1 = 有不通过项 · 2 = 用法错
用法:
  python3 HW/check_onepass_commit_order.py             # 主模式
  python3 HW/check_onepass_commit_order.py --selftest   # 反向用例 (★端到端跑真盘沙盒副本★)
  ★自检用 env 覆盖★: ONEPASS_WORKPACKET / ONEPASS_LEDGER / ONEPASS_COMMIT_ORDER /
                     ONEPASS_PCB / ONEPASS_PRO / ONEPASS_NETLIST / ONEPASS_PINS / ONEPASS_BOM
                     + --root (★相对路径的根★)
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)

# ★默认相对路径 (★相对 --root★)
REL = {
    "workpacket":   "HW/PCB/BOARD_ONEPASS_WORKPACKET.md",
    "ledger":       "HW/PCB/BOARD_ONEPASS_MD5_LEDGER.md",
    "commit_order": "HW/PCB/BOARD_ONEPASS_COMMIT_ORDER.md",
    "pcb":          "HW/PCB/demo_mainboard.kicad_pcb",
    "pro":          "HW/PCB/demo_mainboard.kicad_pro",
    "netlist":      "HW/netlist_v1.csv",
    "pins":         "HW/netlist_v1_pins.csv",
    "bom":          "HW/BOM_v1.csv",
}

# ★env 覆盖 (★--selftest 用它把闸指向沙盒副本★)
ENV = {
    "workpacket":   "ONEPASS_WORKPACKET",
    "ledger":       "ONEPASS_LEDGER",
    "commit_order": "ONEPASS_COMMIT_ORDER",
    "pcb":          "ONEPASS_PCB",
    "pro":          "ONEPASS_PRO",
    "netlist":      "ONEPASS_NETLIST",
    "pins":         "ONEPASS_PINS",
    "bom":          "ONEPASS_BOM",
}

# ★受保护件的硬基线 (★网表/脚表/BOM 按作业包 §5 全程「不变」⇒ 可硬校验; 板与 .kicad_pro 走 D4 的 change-aware 口径★)
HARD_BASELINE = {
    "netlist": "e06c1dd633566aa44732762c2ff99d1c",
    "pins":    "287e7861a0d1007748d92d9fbecdd490",
    "bom":     "94642d07a69e8d60dd2af57f69b93607",
}

# ★受保护 5 件的对外基线 (★交卷单与任务书用的那组★)
PROTECTED_5 = {
    "板":       "611b869e13518c3c023fb178f91a0075",
    ".kicad_pro": "3e504d2be83152e337949723e909be1b",
    "网表":     "e06c1dd633566aa44732762c2ff99d1c",
    "脚表":     "287e7861a0d1007748d92d9fbecdd490",
    "BOM":      "94642d07a69e8d60dd2af57f69b93607",
}

# ── 词表 (★判据的语义锚点★) ───────────────────────────────────────────────
B_CLASS = ("S9", "S10", "S11", "S12", "S13")          # ★B 类终段步 + C 类只读闸步★
B_TERMINAL = ("S9", "S10", "S12", "S13")              # ★B 类留证产物终段步★

# ★注意: 这里只收【顺序性】标记 (★"最后跑"一类★), 不收 "终段步" 这类【类别名】★
# ★—— 类别名不表达【什么时候跑】, 拿它当判据 = 判据不判事★
TERMINAL_MARKERS = ("最后跑", "最后一批", "最后才跑", "之后才跑", "跑在最后",
                     "最后才生成", "最后才做", "最后才产出")

SET_ASSERT_PHRASES = ("不用任何人就能走的", "不投板也能做完的集合",
                      "正确集合", "能做完的集合")

RETRACT_VERBS = ("撤回", "作废", "不成立", "推翻", "不许跑", "不许现在跑",
                 "现在不许跑", "禁止跑", "已废止", "不许【跑")

ONEPASS_MARKERS = ("ISS-280", "订正")

HEX32 = re.compile(r"^[0-9a-f]{32}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ── 小工具 ────────────────────────────────────────────────────────────────
def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def resolve(root: str, key: str, override: str | None) -> str:
    """★相对路径一律相对 --root; env/CLI 给的绝对路径直接用★"""
    if override:
        return os.path.abspath(override)
    env_val = os.environ.get(ENV[key])
    if env_val:
        return env_val if os.path.isabs(env_val) else os.path.join(root, env_val)
    return os.path.join(root, REL[key])


# ── 台账解析 ──────────────────────────────────────────────────────────────
def _block(text: str, name: str) -> list[str]:
    """★取 <!-- ledger:NAME BEGIN ... END --> 之间的行★"""
    m = re.search(r"<!--\s*ledger:%s\s*\n(.*?)\n?END\s*-->" % re.escape(name), text, re.S)
    if not m:
        return []
    return [ln for ln in m.group(1).splitlines()]


def _kv(text: str, name: str) -> dict:
    out = {}
    for ln in _block(text, name):
        m = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+?)\s*$", ln)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def _rows(text: str, name: str) -> list[list[str]]:
    """★取表体行 (★跳过表头与分隔行★)"""
    rows = []
    for ln in _block(text, name):
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 2:
            continue
        if set("".join(cells)) <= set("-: "):      # 分隔行
            continue
        if cells[0] in ("单号", "---"):            # 表头
            continue
        rows.append(cells)
    return rows


def parse_ledger(text: str):
    """★返回 (baseline_dict, changes[list], binding[list], errors[list])★"""
    errors = []
    baseline = _kv(text, "BASELINE")
    changes_raw = _rows(text, "CHANGES")
    binding_raw = _rows(text, "BINDING")

    if "baseline_md5" not in baseline:
        errors.append("台账 BASELINE 区缺 baseline_md5")
    else:
        if not HEX32.match(baseline["baseline_md5"]):
            errors.append("台账 baseline_md5 不是 32 位 hex: %r" % baseline["baseline_md5"])

    changes = []
    for i, c in enumerate(changes_raw):
        if len(c) < 5:
            errors.append("变更区第 %d 行字段不足 5 个 (★格式 = 单号|改前md5|改后md5|第几次变更|日期★): %r" % (i + 1, c))
            continue
        changes.append({
            "issue": c[0], "before": c[1], "after": c[2], "seq": c[3], "date": c[4],
        })

    binding = []
    for i, c in enumerate(binding_raw):
        if len(c) < 4:
            errors.append("留证绑定区第 %d 行字段不足 4 个 (★格式 = 单号|绑定md5|留证产物|产物生成时间|备注★): %r" % (i + 1, c))
            continue
        binding.append({
            "issue": c[0], "md5": c[1], "artifact": c[2], "when": c[3], "note": c[4] if len(c) > 4 else "",
        })

    return baseline, changes, binding, errors


# ── 判据实现 ──────────────────────────────────────────────────────────────
def judge_d1(lines: list[str]):
    """★D1: 作业包必须存在「B 类终段步 (S9/S10/S12/S13) = 最后跑」的显式表述★"""
    hits = []
    for i, ln in enumerate(lines):
        if all(t in ln for t in B_TERMINAL) and any(m in ln for m in TERMINAL_MARKERS):
            hits.append(i)
    if hits:
        return True, "找到 %d 处「B 类终段步 = 最后跑」表述 (★第 %d 行★)" % (len(hits), hits[0] + 1)
    return False, ("找不到一行同时点到 S9/S10/S12/S13 且含终段标记 (%s) "
                   "⇒ 作业包没写清「B 类终段步最后跑」" % "/".join(TERMINAL_MARKERS))


def judge_d2(lines: list[str]):
    """★D2: 作业包必须存在「板 md5 只允许变一次 / S4/S8 与 S1/S2/S3/S6/S7 同趟」的显式表述★"""
    for i, ln in enumerate(lines):
        once = ("只允许变一次" in ln) or ("只变一次" in ln)
        if once and ("同趟" in ln) and ("S4" in ln) and ("S8" in ln):
            return True, "找到「只允许变一次 + 同趟 + S4 + S8」表述 (★第 %d 行★)" % (i + 1)
    return False, ("找不到一行同时含「只允许变一次/只变一次」+「同趟」+「S4」+「S8」"
                   "⇒ 作业包没写清「板 md5 只允许变一次 ⇒ S4/S8 与 S1/S2/S3/S6/S7 同趟」")


def _is_retraction(ln: str) -> bool:
    """★撤回行 = ① 含撤回动词 ② 含 ISS-280 或「订正」 ③ 【必须是在撤那个集合断言】★
    ★③ 的实现 = 该行必须提到那个集合 (★引用集合断言短语, 或直接说「集合」★)
    ⇒ ★否则 §6.2 那种【泛化警告】会被当成撤回 ⇒ D3 就成了一句空话★"""
    if not any(v in ln for v in RETRACT_VERBS):
        return False
    if not any(m in ln for m in ONEPASS_MARKERS):
        return False
    if not (any(p in ln for p in SET_ASSERT_PHRASES) or ("集合" in ln)):
        return False
    return True


def judge_d3(lines: list[str]):
    """★D3: 作业包【不得】再把 S9/S10/S11/S12/S13 列进「现在就能做完」的集合★"""
    assertions, retractions = [], []
    for i, ln in enumerate(lines):
        has_set = any(p in ln for p in SET_ASSERT_PHRASES)
        has_b = any(b in ln for b in B_CLASS)
        if has_set and has_b and not _is_retraction(ln):
            assertions.append(i)
        if has_b and _is_retraction(ln):
            retractions.append(i)
    uncovered = [i for i in assertions if not any(r > i for r in retractions)]
    if not assertions:
        return False, "作业包里找不到任何「现在就能做完」集合断言行 ⇒ 集合段被整段删了 (★老字不许删★)"
    if uncovered:
        return False, ("集合断言行 (第 %s 行) 仍把 B 类步 (S9/S10/S11/S12/S13) 列在「现在就能做完」里, "
                       "且【后文没有撤回订正】" % ", ".join(str(i + 1) for i in uncovered))
    return True, ("%d 处集合断言全部被后文撤回订正覆盖 (★断言行 %s · 撤回行 %s★)"
                  % (len(assertions), ", ".join(str(i + 1) for i in assertions),
                     ", ".join(str(i + 1) for i in retractions)))


def judge_d4(root: str, paths: dict, baseline: dict, changes: list):
    """★D4: 盘上板 md5 == 台账最后一次登记的板 md5 (变更区 0 行时 == 基线 md5)★"""
    pcb = paths["pcb"]
    if not os.path.exists(pcb):
        return False, "找不到板文件 %s" % pcb
    cur = md5_of(pcb)
    if changes:
        registered = changes[-1]["after"]
        where = "变更区最后一行 (★%s · 第 %s 次变更★) 的改后 md5" % (changes[-1]["issue"], changes[-1]["seq"])
    else:
        registered = baseline.get("baseline_md5", "")
        where = "台账基线 md5 (★变更区 0 行 = 板至今没变过★)"
    if cur == registered:
        return True, "盘上板 md5 %s == %s ⇒ 盘面与台账一致" % (cur, where)
    return False, ("盘上板 md5 = %s ≠ %s = %s ⇒ 有人绕过本单改了板 (★未登记台账★)"
                   % (cur, where, registered))


def judge_d4b(root: str, paths: dict, baseline: dict):
    """★D4b: 盘上 .kicad_pro md5 == 台账基线登记的 .kicad_pro md5★"""
    pro = paths["pro"]
    if not os.path.exists(pro):
        return False, "找不到 .kicad_pro %s" % pro
    cur = md5_of(pro)
    registered = baseline.get("baseline_pro_md5", "")
    if not registered:
        return False, "台账 BASELINE 区缺 baseline_pro_md5"
    if cur == registered:
        return True, "盘上 .kicad_pro md5 %s == 台账基线登记值 ⇒ 未被绕过改动" % cur
    return False, ("盘上 .kicad_pro md5 = %s ≠ 台账基线 %s ⇒ .kicad_pro 被绕过本单改动"
                   % (cur, registered))


def judge_d5(changes: list, baseline: dict, ledger_errors: list):
    """★D5: 变更次数 ≤ 1 (★顺带查台账自身结构★)★"""
    n = len(changes)
    detail = []
    if n >= 2:
        detail.append("变更区有 %d 行 ⇒ 板 md5 变了 %d 次 ⇒ 「板只改一次」已破功" % (n, n))
    if n >= 1:
        if not HEX32.match(changes[0]["before"]):
            detail.append("第 1 行的改前 md5 不是 32 位 hex: %r" % changes[0]["before"])
        elif baseline.get("baseline_md5") and changes[0]["before"] != baseline["baseline_md5"]:
            detail.append("第 1 行的改前 md5 %s ≠ 台账基线 md5 %s" % (changes[0]["before"], baseline["baseline_md5"]))
        if not HEX32.match(changes[0]["after"]):
            detail.append("第 1 行的改后 md5 不是 32 位 hex: %r" % changes[0]["after"])
        if changes[0]["seq"].strip() != "1":
            detail.append("第 1 行的「第几次变更」= %r, 应为 1" % changes[0]["seq"])
        if not DATE_RE.match(changes[0]["date"].strip()):
            detail.append("第 1 行的日期格式错: %r (★应 YYYY-MM-DD★)" % changes[0]["date"])
    for e in ledger_errors:
        detail.append(e)
    if detail:
        return False, " · ".join(detail)
    return True, "变更区 %d 行 (★≤ 1 ⇒ 板 md5 至多变一次★)" % n


def judge_d6(root: str, paths: dict, changes: list, binding: list):
    """★D6: 变更次数 = 1 ⇒ 那一版必须被留证产物绑定★"""
    if not changes:
        return True, "变更区 0 行 ⇒ 板 md5 没变过 ⇒ 无需留证绑定 (★本单零写板★)"
    target = changes[-1]["after"]
    cands = [b for b in binding if b["md5"] == target]
    if not binding:
        return False, ("变更次数 = 1 (★改后 md5 %s★) 但留证绑定区 0 行 ⇒ 那一版没有任何留证产物钉住它 "
                       "⇒ 悬空的改板" % target)
    if not cands:
        return False, ("变更次数 = 1 (★改后 md5 %s★) 但留证绑定区没有一行绑定这个 md5 (★现有 %s★)"
                       % (target, ", ".join(b["md5"] for b in binding)))
    bad = []
    for b in cands:
        ap = b["artifact"]
        apath = ap if os.path.isabs(ap) else os.path.join(root, ap)
        if not os.path.exists(apath):
            bad.append("留证产物 %s 不在盘上" % ap)
            continue
        if os.path.getmtime(apath) < os.path.getmtime(paths["pcb"]):
            bad.append("留证产物 %s 的 mtime 比板旧 (★产物不得比板旧★)" % ap)
    if bad:
        return False, " · ".join(bad)
    return True, ("变更次数 = 1, 留证绑定 %d 行命中改后 md5 %s, 且产物在盘且不比板旧"
                  % (len(cands), target))


# ── 主评估 ────────────────────────────────────────────────────────────────
def evaluate(root: str, paths: dict, only: str | None = None):
    results = []   # (判据号, 通过?, 说明)

    wp = paths["workpacket"]
    if not os.path.exists(wp):
        return [(k, False, "找不到作业包 %s" % wp) for k in ("D0", "D1", "D2", "D3", "D4", "D5", "D6")]

    wp_lines = read_text(wp).splitlines()

    # ── D0 ──
    if only in (None, "D0"):
        co = paths["commit_order"]
        msgs, ok = [], True
        if not os.path.exists(co):
            ok = False
            msgs.append("找不到权威页 %s" % co)
        else:
            co_txt = read_text(co)
            miss = [a for a in ("INV-1", "INV-2", "INV-3", "INV-4") if a not in co_txt]
            if miss:
                ok = False
                msgs.append("权威页缺锚点 %s" % ", ".join(miss))
            else:
                msgs.append("权威页存在且 INV-1~INV-4 齐全")
        for key, label in (("netlist", "网表"), ("pins", "脚表"), ("bom", "BOM")):
            p = paths[key]
            if not os.path.exists(p):
                ok = False
                msgs.append("找不到 %s %s" % (label, p))
                continue
            cur = md5_of(p)
            if cur != HARD_BASELINE[key]:
                ok = False
                msgs.append("%s md5 = %s ≠ 基线 %s ⇒ 落表了 (零落表被破)" % (label, cur, HARD_BASELINE[key]))
            else:
                msgs.append("%s md5 未变" % label)
        results.append(("D0", ok, " · ".join(msgs)))

    # ── D1 / D2 / D3 (作业包) ──
    if only in (None, "D1"):
        ok, msg = judge_d1(wp_lines)
        results.append(("D1", ok, msg))
    if only in (None, "D2"):
        ok, msg = judge_d2(wp_lines)
        results.append(("D2", ok, msg))
    if only in (None, "D3"):
        ok, msg = judge_d3(wp_lines)
        results.append(("D3", ok, msg))

    # ── 台账 ──
    lg = paths["ledger"]
    if not os.path.exists(lg):
        for k in ("D4", "D5", "D6"):
            if only in (None, k):
                results.append((k, False, "找不到台账 %s" % lg))
        return results

    ledger_txt = read_text(lg)
    baseline, changes, binding, ledger_errors = parse_ledger(ledger_txt)

    if only in (None, "D4"):
        ok, msg = judge_d4(root, paths, baseline, changes)
        results.append(("D4", ok, msg))
        ok2, msg2 = judge_d4b(root, paths, baseline)
        results.append(("D4b", ok2, msg2))
    if only in (None, "D5"):
        ok, msg = judge_d5(changes, baseline, ledger_errors)
        results.append(("D5", ok, msg))
    if only in (None, "D6"):
        ok, msg = judge_d6(root, paths, changes, binding)
        results.append(("D6", ok, msg))

    return results


def report(results, title="主模式"):
    print("=" * 78)
    print("  ISS-280 · 「板只改一次」提交时序守卫 (★%s★)" % title)
    print("=" * 78)
    bad = 0
    for code, ok, msg in results:
        mark = "✅" if ok else "❌"
        if not ok:
            bad += 1
        print("  %s %-4s %s" % (mark, code, msg))
    print("-" * 78)
    if bad:
        print("  ❌ %d 项不通过" % bad)
    else:
        print("  ✅ 全部通过")
    return bad


# ── --selftest (★端到端跑真盘沙盒副本★) ───────────────────────────────────
def _copy_tree_for_sandbox(root: str, dst: str):
    """★把闸要读的那几个件复制成沙盒副本 (★真盘原件一个字节不动★)"""
    for key in ("workpacket", "ledger", "commit_order", "pcb", "pro", "netlist", "pins", "bom"):
        src = os.path.join(root, REL[key])
        d = os.path.join(dst, REL[key])
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(src, d)


def _run_gate(root: str):
    """★真跑本闸 (子进程) ★"""
    env = dict(os.environ)
    cmd = [sys.executable, os.path.abspath(__file__), "--root", root]
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return p.returncode, p.stdout + p.stderr


def _ledger_with(changes_rows, binding_rows, baseline_extra=None):
    """★造一份沙盒台账文本★"""
    bl = ["baseline_md5: 611b869e13518c3c023fb178f91a0075",
          "baseline_ref: HW/PCB/demo_mainboard.kicad_pcb",
          "baseline_date: 2026-11-06",
          "baseline_pro_md5: 3e504d2be83152e337949723e909be1b",
          "baseline_netlist_md5: e06c1dd633566aa44732762c2ff99d1c",
          "baseline_pins_md5: 287e7861a0d1007748d92d9fbecdd490",
          "baseline_bom_md5: 94642d07a69e8d60dd2af57f69b93607"]
    if baseline_extra:
        bl += baseline_extra
    ch = ["| 单号 | 改前 md5 | 改后 md5 | 第几次变更 | 日期 |",
          "|---|---|---|---|---|"] + changes_rows
    bd = ["| 单号 | 绑定 md5 | 留证产物 (相对路径) | 产物生成时间 | 备注 |",
          "|---|---|---|---|---|"] + binding_rows
    return ("<!-- ledger:BASELINE\n%s\n-->\n\n"
            "<!-- ledger:CHANGES\nBEGIN\n%s\nEND\n-->\n\n"
            "<!-- ledger:BINDING\nBEGIN\n%s\nEND\n-->\n"
            % ("\n".join(bl), "\n".join(ch), "\n".join(bd)))


def run_selftest(root: str):
    tmpd = tempfile.mkdtemp(prefix="iss280_selftest_")
    sb = os.path.join(tmpd, "sandbox")
    os.makedirs(sb, exist_ok=True)
    cases = []
    try:
        _copy_tree_for_sandbox(root, sb)

        wp_s = os.path.join(sb, REL["workpacket"])
        lg_s = os.path.join(sb, REL["ledger"])
        pcb_s = os.path.join(sb, REL["pcb"])
        wp_orig = read_text(wp_s)
        lg_orig = read_text(lg_s)
        pcb_orig = read_text(pcb_s)

        def restore():
            open(wp_s, "w", encoding="utf-8").write(wp_orig)
            open(lg_s, "w", encoding="utf-8").write(lg_orig)
            open(pcb_s, "w", encoding="utf-8").write(pcb_orig)

        def write_wp(txt):
            open(wp_s, "w", encoding="utf-8").write(txt)

        # ★基线: 沙盒副本必须全绿 (否则下面的红没意义) ★
        rc, out = _run_gate(sb)
        cases.append(("★基线: 沙盒副本 (真盘原样) ⇒ rc=0", rc == 0, out))

        # ① D1: 把「最后跑」改成「随时跑」⇒ D1 红
        t = wp_orig.replace("最后跑", "随时跑")
        write_wp(t)
        rc, out = _run_gate(sb)
        caught = ("D1" in out and "❌ D1" in out)
        cases.append(("① 把作业包「最后跑」改成「随时跑」⇒ D1 红", rc == 1 and caught, out))
        restore()

        # ② D2: 把「只允许变一次」改成「随便变几次」⇒ D2 红
        t = wp_orig.replace("只允许变一次", "随便变几次")
        write_wp(t)
        rc, out = _run_gate(sb)
        caught = ("❌ D2" in out)
        cases.append(("② 把作业包「只允许变一次」改成「随便变几次」⇒ D2 红", rc == 1 and caught, out))
        restore()

        # ③ D3: 把撤回订正整段抹掉 (旧集合重新生效) ⇒ D3 红
        t = wp_orig.replace("撤回", "保留原样")
        write_wp(t)
        rc, out = _run_gate(sb)
        caught = ("❌ D3" in out)
        cases.append(("③ 把作业包的「撤回」订正抹掉 ⇒ 旧集合重新生效 ⇒ D3 红", rc == 1 and caught, out))
        restore()

        # ④ D4: 沙盒里的板偷改一个字节 (不登记台账) ⇒ D4 红
        open(pcb_s, "a", encoding="utf-8").write("\n; ★selftest 注入的一行 ★\n")
        rc, out = _run_gate(sb)
        caught = ("❌ D4" in out)
        cases.append(("④ 沙盒里的板偷改一个字节 (不登记台账) ⇒ D4 红", rc == 1 and caught, out))
        restore()

        # ⑤ D5: 台账登记 2 次变更 ⇒ D5 红
        open(lg_s, "w", encoding="utf-8").write(_ledger_with(
            ["| ISS-266 | 611b869e13518c3c023fb178f91a0075 | aaaabbbbccccddddeeeeffff00001111 | 1 | 2026-11-17 |",
             "| ISS-268 | aaaabbbbccccddddeeeeffff00001111 | 11112222333344445555666677778888 | 2 | 2026-11-17 |"],
            []))
        rc, out = _run_gate(sb)
        caught = ("❌ D5" in out)
        cases.append(("⑤ 台账登记 2 次变更 ⇒ D5 红", rc == 1 and caught, out))
        restore()

        # ⑥ D6: 台账登记 1 次变更但不写留证绑定 ⇒ D6 红
        newmd5 = "aaaabbbbccccddddeeeeffff00001111"
        open(lg_s, "w", encoding="utf-8").write(_ledger_with(
            ["| ISS-266 | 611b869e13518c3c023fb178f91a0075 | %s | 1 | 2026-11-17 |" % newmd5], []))
        rc, out = _run_gate(sb)
        caught = ("❌ D6" in out)
        cases.append(("⑥ 台账登记 1 次变更但无留证绑定 ⇒ D6 红 (悬空的改板)", rc == 1 and caught, out))
        restore()

        # ⑦ D6 正向对照: 登记 1 次变更 + 沙盒板真改成那个 md5 + 留证绑定齐全 ⇒ 全绿
        open(pcb_s, "a", encoding="utf-8").write("\n; ★selftest 合法变更注入的一行 ★\n")
        real_md5 = md5_of(pcb_s)
        art_rel = "HW/PCB/production/doc/board-stats.txt"
        art = os.path.join(sb, art_rel)
        os.makedirs(os.path.dirname(art), exist_ok=True)
        open(art, "w", encoding="utf-8").write("selftest 留证产物 (★绑 md5 %s★)\n" % real_md5)
        os.utime(art, (os.path.getmtime(pcb_s) + 60, os.path.getmtime(pcb_s) + 60))
        open(lg_s, "w", encoding="utf-8").write(_ledger_with(
            ["| ISS-266 | 611b869e13518c3c023fb178f91a0075 | %s | 1 | 2026-11-17 |" % real_md5],
            ["| ISS-266 | %s | %s | 2026-11-17 09:00 | ★selftest 绑定★ |" % (real_md5, art_rel)]))
        rc, out = _run_gate(sb)
        cases.append(("⑦ 正向对照: 登记 1 次变更 + 留证绑定齐全 + 产物不比板旧 ⇒ rc=0 (★证明 D6 不是恒红★)",
                      rc == 0, out))
        restore()

        # ⑧ D0: 沙盒里的网表偷改一个字节 ⇒ D0 红 (零落表守卫)
        net_s = os.path.join(sb, REL["netlist"])
        net_orig = read_text(net_s)
        open(net_s, "a", encoding="utf-8").write("P99,GND,NET_X,GND,X,1uF,C,NO,0603,01,MAIN_PCB,,\n")
        rc, out = _run_gate(sb)
        caught = ("❌ D0" in out)
        cases.append(("⑧ 沙盒里的网表偷改一行 ⇒ D0 红 (零落表守卫)", rc == 1 and caught, out))
        open(net_s, "w", encoding="utf-8").write(net_orig)

        # ⑨ D5 断号: 第几次变更写成 2 (第 1 行) ⇒ D5 红
        open(lg_s, "w", encoding="utf-8").write(_ledger_with(
            ["| ISS-266 | 611b869e13518c3c023fb178f91a0075 | aaaabbbbccccddddeeeeffff00001111 | 2 | 2026-11-17 |"], []))
        rc, out = _run_gate(sb)
        caught = ("❌ D5" in out)
        cases.append(("⑨ 台账「第几次变更」断号 (第 1 行写成 2) ⇒ D5 红", rc == 1 and caught, out))
        restore()

        # ⑩ D4b: 沙盒里的 .kicad_pro 偷改一个字节 ⇒ D4b 红
        pro_s = os.path.join(sb, REL["pro"])
        pro_orig = read_text(pro_s)
        open(pro_s, "a", encoding="utf-8").write("\n; ★selftest 注入的一行 ★\n")
        rc, out = _run_gate(sb)
        caught = ("❌ D4b" in out)
        cases.append(("⑩ 沙盒里的 .kicad_pro 偷改一个字节 ⇒ D4b 红", rc == 1 and caught, out))
        open(pro_s, "w", encoding="utf-8").write(pro_orig)

        # ⑪ ★历史对照: 用 ISS-280 之前的作业包 (★原病灶副本★) ⇒ 闸必须红
        before = os.path.join(root, "logs", "iss280", "workpacket_BEFORE_iss280.md")
        if os.path.exists(before):
            open(wp_s, "w", encoding="utf-8").write(read_text(before))
            rc, out = _run_gate(sb)
            caught = ("❌ D1" in out) and ("❌ D3" in out)
            cases.append(("⑪ ★历史对照: 用 ISS-280 之前的作业包 (★原病灶★) ⇒ D1/D3 红 (★证明闸真能抓住原病灶★)",
                          rc == 1 and caught, out))
        else:
            cases.append(("⑪ ★历史对照: 跳过 (★找不到 logs/iss280/workpacket_BEFORE_iss280.md★)", True, ""))

    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    print("=" * 78)
    print("  ISS-280 · 反向用例 (★每条都【把判据真改坏一次】并端到端跑真闸★)")
    print("=" * 78)
    bad = 0
    for item in cases:
        name, caught = item[0], item[1]
        mark = "✔" if caught else "✘"
        if not caught:
            bad += 1
        print("  %s  %s" % (mark, name))
    print("-" * 78)
    reverse = [c for c in cases if not c[0].startswith("★基线")]
    print("  反向用例 %d 条 (★≥6★) · 抓到 %d / %d" % (len(reverse), len(reverse) - bad, len(reverse)))
    if bad:
        print("  ❌ 有反向用例没抓到 ⇒ 闸不是判据 (或用例本身写错了)")
        return 1
    print("  ✅ 反向用例全抓到 ⇒ 判据真在被读 (★不是把红灯调没★)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=PROJ)
    ap.add_argument("--workpacket", default=None)
    ap.add_argument("--ledger", default=None)
    ap.add_argument("--commit-order", dest="commit_order", default=None)
    ap.add_argument("--pcb", default=None)
    ap.add_argument("--pro", default=None)
    ap.add_argument("--netlist", default=None)
    ap.add_argument("--pins", default=None)
    ap.add_argument("--bom", default=None)
    ap.add_argument("--only", default=None, help="★只跑某一条判据 (调试用★)")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    overrides = {
        "workpacket": args.workpacket, "ledger": args.ledger, "commit_order": args.commit_order,
        "pcb": args.pcb, "pro": args.pro, "netlist": args.netlist,
        "pins": args.pins, "bom": args.bom,
    }
    paths = {k: resolve(root, k, v) for k, v in overrides.items()}

    if args.selftest:
        return run_selftest(root)

    if not os.path.exists(paths["workpacket"]):
        print("❌ 用法错: 找不到作业包 %s" % paths["workpacket"])
        return 2

    results = evaluate(root, paths, only=args.only)
    bad = report(results, "主模式 · root=%s" % root)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
