#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SW/tools/check_load_switch_selection.py — ISS-172 负载开关选型「证据矩阵」机器门禁
=======================================================================================
目的: 机械判定 `SW/LOAD_SWITCH_SELECTION_FACTS.md` (负载开关 U_PWR_SW / U_EN_SW 选型
      证据矩阵) 是否真的把 `HW/POWER_SHUTDOWN_V3.md` §2 的 **8 条判据** 逐格填满,
      而不是只写一句 "[待选型]" —— 防止:
        ① 候选不足 3 个却当成"选完了"
        ② 八条判据有空格 / "待查" / "TBD" / 没有出处 (没查就写没查, 不许编)
        ③ 证据等级混进五级白名单之外的词 (例如把"官网"写成"[官方]"冒充官网)
        ④ RCB (反向电流阻断) 判定字段被清空 —— ★这正是 ISS-234 交卷件点名的缺口
        ⑤ 结论是"没有同封装带 RCB 的在售型号"却没有降级方案
        ⑥ 把前人 (ISS-234) 点名的 `TPS22991RAA` 悄悄删掉, 或矩阵八判据与网表 L50
           的 `[待选型]` 判据串各说各话
        ⑦ 矩阵的判据文本与 `HW/POWER_SHUTDOWN_V3.md` §2 真源漂移 (改判据不许偷偷改)

★铁律 (SOUL.md):
  1. 本脚本 **不编任何器件参数** —— 它只核对**矩阵 / 网表 / 判据真源**三者的**一致性**;
     所有参数值来自 `SW/LOAD_SWITCH_SELECTION_FACTS.md` 内的"选型证据基准块",
     本脚本只验"在位 / 不在位 / 对不对得上 / 证据等级合不合法"。
  2. **网表是只读的**: 本脚本只读 `HW/netlist_v1.csv`, 从不写它;
     反向用例只改**临时目录里的文档副本** (真盘一个字节不动)。
  3. ★**内容级, 不挂 md5**: 网表在飞 (hw-lead 并发落表) ⇒ md5 随时会漂
     ⇒ 本门禁**不锚 md5**, 一律按**位号 / 内容**判定 ⇒ 落表后仍成立。
  4. ★**不碰硬件**: 装配、DRC、器件库存一律不查 —— 本门禁只管"证据矩阵写没写全"。
  5. 退出码 0 = 全过; 1 = 有项不通过 (会点名是哪一条); 2 = 用法错误。

★读网表的一个坑 (沿用 `SW/SHUTDOWN_SEMANTICS_SPEC.md` §6.3):
  这张网表是 **"一行 = 一根导线 = 同一网上两个器件脚"**, `ref` 列只代表这条线的其中一端
  ⇒ **器件归属必须从 node 字符串反推** (`<位号> pin<N>` ⇒ 属于 `<位号>`), 不靠 `ref` 列。
  本门禁找 `U_PWR_SW` 本体行时, **同时**要求: `ref == U_PWR_SW` 且 `type == IC`
  且 node 字符串带 `U_PWR_SW pin<N>` ⇒ 不靠行号 ⇒ hw-lead 并发插行也不受影响。

用法:
    python3 SW/tools/check_load_switch_selection.py            # 核对 (rc=0 = 全过)
    python3 SW/tools/check_load_switch_selection.py --selftest  # 反向自检 (≥5/5, 每条都自证改到了目标)
    python3 SW/tools/check_load_switch_selection.py --json      # 机读输出
    python3 SW/tools/check_load_switch_selection.py --root <目录>  # 指定项目根 (自检用)
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

HERE = os.path.dirname(os.path.abspath(__file__))            # .../SW/tools
PROJ = os.path.dirname(os.path.dirname(HERE))                # .../<项目库根>

DOC_REL = os.path.join("SW", "LOAD_SWITCH_SELECTION_FACTS.md")
NETLIST_REL = os.path.join("HW", "netlist_v1.csv")
CRITERIA_REL = os.path.join("HW", "POWER_SHUTDOWN_V3.md")

BASELINE_BEGIN = "<!-- BEGIN 选型证据基准块"
BASELINE_END = "<!-- END 选型证据基准块"

# ★证据等级白名单 —— 只有这五个, 其它词一律红 (政策: 老板 2026-11-12 02:02)
EVIDENCE_OK = {"[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]"}

# ★RCB 判定三选一
RCB_VERDICTS = {"有", "无", "查不到"}

# ★判据数 (HW/POWER_SHUTDOWN_V3.md §2 表的前 8 行是负载开关判据, 第 9 行是 Q_PG 的 P-MOS 判据)
N_CRITERIA = 8

# ★ISS-234 (SW/SHUTDOWN_SEMANTICS_SPEC.md §3 Q2) 点名的候选 —— 不许把前人的候选悄悄删掉
MUST_HAVE_CANDIDATE = "TPS22991RAA"

# ★"没查" 的占位词 —— 出现在格子里 = 没查
EMPTY_TOKENS = re.compile(r"(TBD|待查|待定|待补|待填|待核|XXXX|\?\?\?)", re.IGNORECASE)

# ★降级方案必备字段
FALLBACK_FIELDS = ["change", "cost", "condition", "basis"]

# ★RCB 判定要引的官方原文 (必填)
RCB_FIELDS = ["verdict", "quote", "source", "evidence"]


# ──────────────────────────────────────────────────────────────────────────────
# 小工具
# ──────────────────────────────────────────────────────────────────────────────
def norm(s: str) -> str:
    """归一化: 去 markdown 强调符号 / ★ / 空白 / 反引号 —— 只为**比文本**, 不改判据。"""
    if s is None:
        return ""
    s = str(s)
    for ch in ("*", "★", "`", " ", "\t", "\u3000", "\u200b"):
        s = s.replace(ch, "")
    return s.strip()


def strip_fence(txt: str) -> str:
    txt = txt.strip()
    if txt.startswith("```"):
        txt = re.sub(r"^```[a-zA-Z0-9_+-]*\s*", "", txt)
        txt = re.sub(r"```\s*$", "", txt)
    return txt.strip()


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def parse_doc(text: str):
    """返回 (data_dict, prose_text)。基准块取不出来 ⇒ (None, text)。"""
    if BASELINE_BEGIN not in text or BASELINE_END not in text:
        return None, text
    i = text.index(BASELINE_BEGIN) + len(BASELINE_BEGIN)
    j = text.index(BASELINE_END)
    block = text[i:j]
    prose = text[:text.index(BASELINE_BEGIN)] + "\n" + text[j:]
    try:
        data = json.loads(strip_fence(block))
    except Exception as exc:  # noqa: BLE001
        return {"__parse_error__": str(exc)}, prose
    return data, prose


def find_netlist_rows(net_text: str, ref: str):
    """按位号 + 类型 + node 字符串找器件本体行 (不靠行号 ⇒ 并发插行安全)。"""
    rows = []
    rd = csv.reader(net_text.splitlines())
    header = next(rd, None)
    if not header:
        return rows, header
    idx = {name: i for i, name in enumerate(header)}
    for row in rd:
        if len(row) < len(header):
            continue
        if row[idx.get("ref", 0)].strip() != ref:
            continue
        if row[idx.get("type", 0)].strip().upper() != "IC":
            continue
        node = " ".join(row)
        if ("%s pin" % ref) not in node:
            continue
        rows.append({k: row[i] for k, i in idx.items()})
    return rows, header


def extract_hw_criteria(criteria_text: str):
    """从 `HW/POWER_SHUTDOWN_V3.md` §2 表里取前 8 条负载开关判据原文 (返回 list[str])。"""
    lines = criteria_text.splitlines()
    out = []
    in_sec = False
    for ln in lines:
        if ln.startswith("## §2 "):
            in_sec = True
            continue
        if in_sec and ln.startswith("## ") and not ln.startswith("## §2 "):
            break
        if not in_sec:
            continue
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        if cells[0] in ("#", "判据") or set(cells[0]) <= set("-: "):
            continue
        if not cells[0].isdigit():
            continue
        out.append(cells[1])
        if len(out) >= N_CRITERIA:
            break
    return out


# ──────────────────────────────────────────────────────────────────────────────
# 主检查: 返回 [(check_id, message), ...] —— 空列表 = 全过
# ──────────────────────────────────────────────────────────────────────────────
def run_checks(doc_text: str, net_text: str, criteria_text: str):
    fails = []

    def fail(cid, msg):
        fails.append((cid, msg))

    data, prose = parse_doc(doc_text)

    # ── 前置: 文档 / 基准块 必须能解析 ───────────────────────────────────────
    if data is None:
        fail("C0", "找不到选型证据基准块 (%s ... %s) ⇒ 矩阵的机器可读部分缺失" % (BASELINE_BEGIN, BASELINE_END))
        return fails
    if "__parse_error__" in data:
        fail("C0", "选型证据基准块不是合法 JSON: %s" % data["__parse_error__"])
        return fails

    criteria = data.get("criteria") or []
    candidates = data.get("candidates") or []
    fallbacks = data.get("fallbacks") or []
    conclusion = data.get("conclusion") or {}

    # ── C1 候选数 ≥3 (或存在"官方在售型号总数只有 N 个"的白名单说明) ─────────
    if len(candidates) < 3:
        note = str(data.get("official_total_note") or "").strip()
        if not note:
            fail("C1", "候选只有 %d 个 (<3) 且没有 `official_total_note` 白名单说明 ⇒ 证据矩阵不成立" % len(candidates))
    ids = [str(c.get("id") or "") for c in candidates]
    if len(set(ids)) != len(ids):
        fail("C1", "候选 id 有重复: %s" % ids)

    # ── C2 八条判据逐条非空 + 每条都有出处 ──────────────────────────────────
    if len(criteria) != N_CRITERIA:
        fail("C2", "判据条数 = %d (应为 %d 条)" % (len(criteria), N_CRITERIA))
    crit_ids = [int(c.get("id")) for c in criteria if str(c.get("id", "")).isdigit()]
    for n in range(1, N_CRITERIA + 1):
        if n not in crit_ids:
            fail("C2", "判据 #%d 在基准块里缺失" % n)
    for c in candidates:
        cid = c.get("id")
        cells = c.get("cells") or {}
        for n in range(1, N_CRITERIA + 1):
            cell = cells.get(str(n))
            if not isinstance(cell, dict):
                fail("C2", "候选 %s 的判据 #%d 缺格" % (cid, n))
                continue
            val = str(cell.get("value") or "").strip()
            src = str(cell.get("source") or "").strip()
            if not val:
                fail("C2", "候选 %s 的判据 #%d 值为空" % (cid, n))
            elif EMPTY_TOKENS.search(val):
                fail("C2", "候选 %s 的判据 #%d 值里含'没查'占位词: %r" % (cid, n, val))
            if not src:
                fail("C2", "候选 %s 的判据 #%d 没有出处 (source 为空)" % (cid, n))

    # ── C3 证据等级只能取五者之一 ────────────────────────────────────────────
    for c in candidates:
        cid = c.get("id")
        cells = c.get("cells") or {}
        for n in range(1, N_CRITERIA + 1):
            cell = cells.get(str(n))
            if not isinstance(cell, dict):
                continue
            ev = str(cell.get("evidence") or "").strip()
            if ev not in EVIDENCE_OK:
                fail("C3", "候选 %s 判据 #%d 的证据等级 %r 不在白名单 %s 内"
                     % (cid, n, ev, sorted(EVIDENCE_OK)))
        rcb = c.get("rcb") or {}
        ev = str(rcb.get("evidence") or "").strip()
        if ev not in EVIDENCE_OK:
            fail("C3", "候选 %s 的 RCB 证据等级 %r 不在白名单 %s 内" % (cid, ev, sorted(EVIDENCE_OK)))

    # ── C4 每个候选的 RCB 判定字段非空 (有/无/查不到 三选一) ────────────────
    for c in candidates:
        cid = c.get("id")
        rcb = c.get("rcb") or {}
        for f in RCB_FIELDS:
            if not str(rcb.get(f) or "").strip():
                fail("C4", "候选 %s 的 RCB 字段 `%s` 为空" % (cid, f))
        v = str(rcb.get("verdict") or "").strip()
        if v and v not in RCB_VERDICTS:
            fail("C4", "候选 %s 的 RCB 判定 %r 不是 有/无/查不到 三选一" % (cid, v))

    # ── C5 结论若是"没有同封装带 RCB 的在售型号" ⇒ 必须有 ≥2 条降级方案 ─────
    if conclusion.get("same_package_with_rcb_available") is False:
        if len(fallbacks) < 2:
            fail("C5", "结论 = 没有同封装带 RCB 的在售型号, 但降级方案只有 %d 条 (<2)" % len(fallbacks))
    for fb in fallbacks:
        fid = fb.get("id")
        for f in FALLBACK_FIELDS:
            if not str(fb.get(f) or "").strip():
                fail("C5", "降级方案 %s 缺字段 `%s` (改了什么/代价/适用条件/依据 一个都不能少)" % (fid, f))

    # ── C6 前人候选在册 + 网表判据串与矩阵八判据对得上 ─────────────────────
    if MUST_HAVE_CANDIDATE not in ids:
        fail("C6", "ISS-234 点名的 %s 不在候选册里 (不许把前人的候选悄悄删掉)" % MUST_HAVE_CANDIDATE)
    rows, _hdr = find_netlist_rows(net_text, "U_PWR_SW")
    if not rows:
        fail("C6", "网表里找不到 U_PWR_SW 的器件本体行 (ref=U_PWR_SW 且 type=IC)")
    else:
        live_val = rows[0].get("value", "")
        toks = re.findall(r"[≥≤><]=?\s*([\d.]+)\s*(mΩ|µA|μA|A|V)", live_val)
        toks += re.findall(r"@\s*([\d.]+)\s*V", live_val)
        crit_norm = [(int(c.get("id")), norm(str(c.get("text") or ""))) for c in criteria
                     if str(c.get("id", "")).isdigit()]
        for num, unit in toks:
            unit_n = "µA" if unit in ("µA", "μA") else unit
            hit = [i for i, t in crit_norm if (num in t and unit_n in t)]
            if not hit:
                fail("C6", "网表 U_PWR_SW 判据串里的阈值 `%s%s` 在矩阵八条判据里找不到对应条目" % (num, unit_n))
        snap = str(data.get("netlist_value_snapshot") or "").strip()
        if not snap:
            fail("C6", "基准块缺 `netlist_value_snapshot` (网表 L50 判据串的快照)")
        else:
            for num, unit in re.findall(r"[≥≤><]=?\s*([\d.]+)\s*(mΩ|µA|μA|A|V)", snap):
                unit_n = "µA" if unit in ("µA", "μA") else unit
                hit = [i for i, t in crit_norm if (num in t and unit_n in t)]
                if not hit:
                    fail("C6", "基准块快照里的阈值 `%s%s` 在矩阵八条判据里找不到对应条目" % (num, unit_n))
            if "反向阻断" in snap:
                if not any("反向阻断" in t for _i, t in crit_norm):
                    fail("C6", "基准块快照提到 '反向阻断', 但矩阵八条判据里没有对应条目")

    # ── C7 矩阵判据文本 vs `HW/POWER_SHUTDOWN_V3.md` §2 真源 (逐条对得上) ────
    hw_crit = extract_hw_criteria(criteria_text)
    if len(hw_crit) < N_CRITERIA:
        fail("C7", "从 %s §2 只解析出 %d 条判据 (应为 %d 条) —— 真源格式变了?" % (CRITERIA_REL, len(hw_crit), N_CRITERIA))
    for i in range(min(len(hw_crit), len(criteria))):
        a = norm(hw_crit[i])
        b = norm(str(criteria[i].get("text") or ""))
        if a != b:
            fail("C7", "判据 #%d 与 %s §2 不一致:\n      真源: %s\n      矩阵: %s" % (i + 1, CRITERIA_REL, a, b))

    # ── C8 正文矩阵真的存在 (每个候选 + 每条判据都要在正文出现) ─────────────
    for c in candidates:
        cid = str(c.get("id") or "")
        if not cid:
            continue
        if not re.search(r"^#{2,4}\s*%s\b" % re.escape(cid), prose, re.MULTILINE):
            fail("C8", "正文里没有候选 %s 的小节 (机器可读块有, 人读的那份没有)" % cid)
    for n in range(1, N_CRITERIA + 1):
        if not re.search(r"^\|\s*%d\s*\|" % n, prose, re.MULTILINE):
            fail("C8", "正文判据表里没有 `| %d |` 这一行" % n)

    return fails


# ──────────────────────────────────────────────────────────────────────────────
# 反向自检 (--selftest): 每条用例都必须自证「它真的改到了目标」
# ──────────────────────────────────────────────────────────────────────────────
def _mut_drop_criterion(text: str) -> str:
    """删掉判据 #5 (反向阻断那条) 的机器可读条目。"""
    m = re.search(r'"criteria"\s*:\s*\[', text)
    if not m:
        return text
    # 逐条找 "id": 5 的对象并整块删掉
    for mo in re.finditer(r'\{\s*"id"\s*:\s*5\s*,', text):
        start = mo.start()
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        else:
            continue
        return text[:start] + text[end:]
    return text


def _mut_bad_evidence(text: str) -> str:
    """把某个格子的证据等级改成非法词 "[官方]" (白名单外)。"""
    return text.replace('"evidence": "[官网]"', '"evidence": "[官方]"', 1)


def _mut_drop_candidate(text: str) -> str:
    """把候选砍到 2 个 (删掉最后一个候选对象)。"""
    m = re.search(r'"candidates"\s*:\s*\[', text)
    if not m:
        return text
    starts = [mo.start() for mo in re.finditer(r'\{\s*"id"\s*:\s*"', text[m.end():])]
    if len(starts) < 3:
        return text
    last_abs = m.end() + starts[-1]
    depth = 0
    end = None
    for i in range(last_abs, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        return text
    return text[:last_abs] + text[end:]


def _mut_drop_fallback(text: str) -> str:
    """把降级方案砍到 1 条。"""
    m = re.search(r'"fallbacks"\s*:\s*\[', text)
    if not m:
        return text
    starts = [mo.start() for mo in re.finditer(r'\{\s*"id"\s*:\s*"FB', text[m.end():])]
    if len(starts) < 2:
        return text
    last_abs = m.end() + starts[-1]
    depth = 0
    end = None
    for i in range(last_abs, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        return text
    return text[:last_abs] + text[end:]


def _mut_clear_rcb(text: str) -> str:
    """把某个候选的 RCB 判定清空。"""
    return re.sub(r'("verdict"\s*:\s*)"(有|无|查不到)"', r'\1""', text, count=1)


def _mut_drop_tps22991(text: str) -> str:
    """删掉 ISS-234 点名的 TPS22991RAA 候选。"""
    m = re.search(r'\{\s*"id"\s*:\s*"TPS22991RAA"', text)
    if not m:
        return text
    start = m.start()
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[:start] + text[i + 1:]
    return text


def _mut_clear_source(text: str) -> str:
    """把某个格子的出处清空。"""
    return re.sub(r'"source"\s*:\s*"[^"]*"', '"source": ""', text, count=1)


def _mut_drift_criteria(text: str) -> str:
    """把判据 #3 的文本改掉 (与 HW §2 真源漂移)。"""
    return re.sub(r'("id"\s*:\s*3\s*,\s*"text"\s*:\s*")[^"]*(")',
                  r'\g<1>R_on ≤ 30mΩ @3.7V\g<2>', text, count=1)


SELFTEST_CASES = [
    ("M1 删掉一条判据 (#5 反向阻断那条)", _mut_drop_criterion, "C2"),
    ("M2 证据等级写成非法词 [官方]", _mut_bad_evidence, "C3"),
    ("M3 候选砍到 2 个", _mut_drop_candidate, "C1"),
    ("M4 降级方案砍到 1 条", _mut_drop_fallback, "C5"),
    ("M5 某个候选的 RCB 判定清空", _mut_clear_rcb, "C4"),
    ("M6 删掉 ISS-234 点名的 TPS22991RAA", _mut_drop_tps22991, "C6"),
    ("M7 某个格子的出处清空", _mut_clear_source, "C2"),
    ("M8 判据文本与 HW §2 真源漂移", _mut_drift_criteria, "C7"),
]


def run_selftest(proj_root: str, doc_text: str, net_text: str, criteria_text: str):
    """返回 (passed, total, [(name, ok, detail), ...])。"""
    results = []
    base_fails = run_checks(doc_text, net_text, criteria_text)
    if base_fails:
        return 0, len(SELFTEST_CASES), [
            (name, False, "★原始文档本身就没过门禁 (%s) ⇒ 自检无意义" % base_fails[0][0])
            for name, _m, _e in SELFTEST_CASES
        ]
    tmp_root = tempfile.mkdtemp(prefix="iss172_selftest_")
    try:
        os.makedirs(os.path.join(tmp_root, "SW"), exist_ok=True)
        for name, mut, expect in SELFTEST_CASES:
            mutated = mut(doc_text)
            ok = True
            detail = ""
            if mutated == doc_text:
                ok = False
                detail = "★变异函数没有改到任何东西 (自证失败: 没改到目标)"
            else:
                fails = run_checks(mutated, net_text, criteria_text)
                got = sorted({c for c, _m in fails})
                if expect not in got:
                    ok = False
                    detail = "★期望 %s 变红, 实际红了 %s" % (expect, got or "[]")
                elif not fails:
                    ok = False
                    detail = "★变异后一条都没红"
                else:
                    detail = "%s 变红 (共 %d 条: %s)" % (expect, len(fails), ",".join(got))
                # 落盘再跑一遍 —— 证明"文档改了 ⇒ 门禁读盘后也红" (ISS-227 同款教训)
                p = os.path.join(tmp_root, "SW", "LOAD_SWITCH_SELECTION_FACTS.md")
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(mutated)
                disk_text = read_text(p)
                if disk_text != mutated:
                    ok = False
                    detail += " ★落盘回读不一致"
                else:
                    dfails = run_checks(disk_text, net_text, criteria_text)
                    if expect not in {c for c, _m in dfails}:
                        ok = False
                        detail += " ★落盘后 %s 没红" % expect
            results.append((name, ok, detail))
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
    passed = sum(1 for _n, ok, _d in results if ok)
    return passed, len(results), results


# ──────────────────────────────────────────────────────────────────────────────
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="ISS-172 负载开关选型证据矩阵门禁")
    ap.add_argument("--selftest", action="store_true", help="跑反向自检 (≥5 条)")
    ap.add_argument("--json", action="store_true", help="机读输出")
    ap.add_argument("--root", default=PROJ, help="项目根目录")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    doc_path = os.path.join(root, DOC_REL)
    net_path = os.path.join(root, NETLIST_REL)
    crit_path = os.path.join(root, CRITERIA_REL)

    for p in (doc_path, net_path, crit_path):
        if not os.path.isfile(p):
            sys.stderr.write("[check_load_switch_selection] 缺文件: %s\n" % p)
            return 2

    doc_text = read_text(doc_path)
    net_text = read_text(net_path)
    crit_text = read_text(crit_path)

    if args.selftest:
        passed, total, results = run_selftest(root, doc_text, net_text, crit_text)
        for name, ok, detail in results:
            print("%s %s — %s" % ("[PASS]" if ok else "[FAIL]", name, detail))
        print("selftest: %d/%d" % (passed, total))
        if args.json:
            print(json.dumps({"selftest_passed": passed, "selftest_total": total,
                              "cases": [{"name": n, "ok": o, "detail": d} for n, o, d in results]},
                             ensure_ascii=False, indent=2))
        return 0 if (total >= 5 and passed == total) else 1

    fails = run_checks(doc_text, net_text, crit_text)
    if args.json:
        print(json.dumps({"ok": not fails,
                          "failures": [{"check": c, "message": m} for c, m in fails]},
                         ensure_ascii=False, indent=2))
    if not fails:
        print("[check_load_switch_selection] PASS — 负载开关选型证据矩阵门禁全过")
        return 0
    print("[check_load_switch_selection] FAIL — %d 条不通过:" % len(fails))
    for cid, msg in fails:
        print("  %s: %s" % (cid, msg))
    return 1


if __name__ == "__main__":
    sys.exit(main())
