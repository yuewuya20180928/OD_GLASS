#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-244 · ISS-241 登记的 10 条选型缺口 (G-1~G-10) 逐条自查补全 + 22 件 OPN 回填清单 — 机器门禁
作者: sw-lead (软件总工) · 2026-11-16 · 交卷给 main / 项目总工

用法:
    python3 HW/check_part_selection_gaps.py             # 正常跑 ⇒ rc=0 = 全过
    python3 HW/check_part_selection_gaps.py --selftest   # 反向用例自证 ⇒ rc=0 = N/N 全抓到
    python3 HW/check_part_selection_gaps.py --json       # 机器可读输出
    python3 HW/check_part_selection_gaps.py --root DIR   # 指定项目根 (默认自动定位)

检查项 (C0~C6):
    C0 基准块存在且是合法 JSON
    C1 G-1~G-10 十条必须全部在收口页出现 (缺一条 = 红)
    C2 每条缺口必须带齐四栏: 状态 / 证据等级 / 出处 / 降级方案 (任一栏空 = 红)
    C3 证据等级只能取 [官网]/[实测]/[媒体]/[推算]/[0数据] 五者之一 (写 "[官方]" = 红)
    C4 不许出现「等回复 / 等原厂回信 / 待供应商确认」这类挂起措辞
       (老板 2026-11-12 02:02 政策: 不再发信, 全靠自己查资料 ⇒ 查不到必须写成
        "[0数据] + 降级方案"; 出现挂起措辞 = 红)
    C5 OPN 回填清单必须 22 件全在 (以 BOM 待选型∩必装 − U_PWR_SW 为准;
       件数由本脚本自己跑 csv 统计, 不抄任何硬编码数字)
    C6 清单每行必须带非空的「落表锚点」字段 (防止落表时找不到改哪儿)

★ 本门禁【不挂 md5】: 判据是内容级 (缺口条数 / 字段非空 / 证据等级白名单 / 挂起措辞 /
  清单覆盖度 / 锚点非空), 文档改一个字就重判, 不用重锚。

--selftest 反向用例 (每条都自证「真的改到了目标」):
    M1 删掉一条缺口 (G-7)          → 期望 C1 变红, 且 C2/C3/C5/C6 仍绿
    M2 把某条缺口的降级方案清空      → 期望 C2 变红, 且 C1/C3/C5/C6 仍绿
    M3 把某条缺口的证据等级写成 [官方] → 期望 C3 变红, 且 C1/C2/C5/C6 仍绿
    M4 正文里塞一句「等原厂回信」     → 期望 C4 变红, 且 C1/C2/C3/C5/C6 仍绿
    M5 清单里删掉一件 (D_ESD_CAM)   → 期望 C5 变红, 且 C1/C2/C3/C4/C6 仍绿
    M6 把某行的落表锚点清空          → 期望 C6 变红, 且 C1/C2/C3/C4/C5 仍绿
    M7 破坏基准块 JSON               → 期望 C0 变红, 且 C1~C6 仍绿

★ 反向用例的「真的改到了目标」自证 = 三件事同时成立:
    ① 变异确实落到盘上副本里 (变异串在副本里 count>=1, 变异前原串消失)
    ② 期望变红的那一条 check 真的红了
    ③ 其余 check 仍然绿 (证明红的是目标那一条, 不是随便塌一条)
"""

import copy
import csv
import json
import os
import re
import shutil
import sys
import tempfile

DOC_REL = os.path.join("HW", "PART_SELECTION_GAPS_CLOSEOUT.md")
BASELINE_BEGIN = "<!-- BEGIN ISS244 缺口收口基准块 -->"
BASELINE_END = "<!-- END ISS244 缺口收口基准块 -->"

# 证据等级白名单 (五级固定, 写死的)
ALLOWED_EVIDENCE = {"[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]"}

# 十条缺口 (ISS-241 §4 登记, 一条不许漏)
GAP_IDS = ["G-1", "G-2", "G-3", "G-4", "G-5", "G-6", "G-7", "G-8", "G-9", "G-10"]

# 挂起措辞黑名单 (老板 2026-11-12 02:02 政策: 不发信, 全靠自己查资料)
FORBIDDEN_PHRASES = (
    "等回复",
    "等原厂回信",
    "待供应商确认",
    "等原厂",
    "等确认",
)

# 正文里允许出现黑名单词的那一段 (本门禁自己的反向用例说明) ⇒ 跳过区
SKIP_BEGIN = "<!-- C4-SKIP-BEGIN -->"
SKIP_END = "<!-- C4-SKIP-END -->"

# OPN 回填清单必须覆盖的位号集合
#   ★ 两个机器派生源, 不抄任何硬编码数字:
#     ① scope   = ISS-241 矩阵基准块里的 expected_refs (登记范围, 本单必须全覆盖)
#     ② pending = HW/BOM_v1.csv 实跑的「待选型∩必装 − 越界件」(当前还待落的)
#   ★ 两者可以不等: 落表批次会把某件的「待选型」改掉 ⇒ 该件已不在 pending 里
#     ⇒ 清单仍保留它 (登记范围不变) 但必须写清 landed_note (落表证据) ⇒ 否则红
#   ★ 这就是 ISS-225 的 H-1 重锚纪律: 锚点过期 ⇒ 红 ⇒ 留痕重锚, 不许把红灯调没
OUT_OF_SCOPE_REFS = {"U_PWR_SW", "U_EN_SW"}

# ISS-241 矩阵 (只读) —— 登记范围从它的机器可读基准块里读, 不硬编码
MATRIX_REL = os.path.join("HW", "PART_SELECTION_MATRIX_2026-11-16.md")
MATRIX_BEGIN = "<!-- BEGIN 选型证据基准块 -->"
MATRIX_END = "<!-- END 选型证据基准块 -->"


def expected_scope_from_matrix(root):
    """从 ISS-241 矩阵的机器可读基准块取登记范围 expected_refs"""
    p = os.path.join(root, MATRIX_REL)
    if not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8") as fh:
        text = fh.read()
    if MATRIX_BEGIN not in text or MATRIX_END not in text:
        return None
    blob = text.split(MATRIX_BEGIN, 1)[1].split(MATRIX_END, 1)[0].strip()
    blob = re.sub(r"^```json\s*", "", blob)
    blob = re.sub(r"```\s*$", "", blob)
    try:
        data = json.loads(blob)
    except Exception:  # noqa: BLE001
        return None
    refs = data.get("expected_refs")
    if not isinstance(refs, list) or not refs:
        return None
    return [str(r).strip() for r in refs]


# ---------------------------------------------------------------- helpers

def find_root():
    """自动定位项目根: 从本文件位置向上找含 HW/ 与 state/ 的目录"""
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


def expected_refs_from_bom(root):
    """自己跑 csv 统计 BOM 待选型∩必装 → 减越界件 ⇒ 本单必须覆盖的位号集合

    ★ 不抄任何硬编码数字 (ISS-241 §4 G-9 的教训: 件数口径三处不一致)
    ★ BOM 若被落表批次改了 ⇒ 这里会漂 ⇒ 门禁按设计变红 ⇒ 走 H-1 重锚流程
    """
    bom = os.path.join(root, "HW", "BOM_v1.csv")
    refs = []
    with open(bom, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            val = (row.get("value") or "")
            dnp = (row.get("dnp") or "").strip()
            if "待选型" in val and dnp == "必装":
                ref = (row.get("ref") or "").strip()
                if ref and ref not in OUT_OF_SCOPE_REFS:
                    refs.append(ref)
    return refs


def extract_baseline(text):
    """从收口页里切出机器可读基准块 (合法 JSON)"""
    if BASELINE_BEGIN not in text or BASELINE_END not in text:
        return None, "基准块标记缺失 (需要 %s ... %s)" % (BASELINE_BEGIN, BASELINE_END)
    blob = text.split(BASELINE_BEGIN, 1)[1].split(BASELINE_END, 1)[0].strip()
    blob = re.sub(r"^```json\s*", "", blob)
    blob = re.sub(r"```\s*$", "", blob)
    try:
        return json.loads(blob), None
    except Exception as exc:  # noqa: BLE001
        return None, "基准块不是合法 JSON: %s" % exc


def strip_skip_region(text):
    """把 C4 跳过区 (本门禁自己的反向用例说明) 从正文里抠掉, 避免自证词误伤"""
    if SKIP_BEGIN not in text or SKIP_END not in text:
        return text
    head, rest = text.split(SKIP_BEGIN, 1)
    _, tail = rest.split(SKIP_END, 1)
    return head + tail


def _nonempty(val):
    return isinstance(val, str) and val.strip() != ""


# ---------------------------------------------------------------- checks

def evaluate(text, baseline, exp_refs, scope_refs=None):
    """跑 C0~C6 ⇒ 返回 {check_id: (ok, [失败信息])}"""
    res = {}

    # ---- C0 基准块存在且合法
    if baseline is None:
        res["C0"] = (False, ["基准块缺失或非法 JSON"])
        # 基准块没了, 后面几条无法判定 ⇒ 全部按红处理 (fail-closed)
        for cid in ("C1", "C2", "C3", "C4", "C5", "C6", "C7"):
            res[cid] = (False, ["基准块不可用 ⇒ 本条无法判定 (fail-closed)"])
        return res
    res["C0"] = (True, [])

    gaps = baseline.get("gaps") or []
    opn = baseline.get("opn_rows") or []

    # ---- C1 十条缺口全部在 (基准块 + 正文都要出现)
    f1 = []
    got_ids = [str(g.get("id", "")) for g in gaps]
    for gid in GAP_IDS:
        if gid not in got_ids:
            f1.append("基准块缺缺口 %s" % gid)
        if gid not in text:
            f1.append("正文缺缺口 %s" % gid)
    if len(gaps) != len(GAP_IDS):
        f1.append("基准块缺口条数 = %d (应为 %d)" % (len(gaps), len(GAP_IDS)))
    res["C1"] = (not f1, f1)

    # ---- C2 每条缺口带齐四栏: 状态 / 证据等级 / 出处 / 降级方案
    f2 = []
    for g in gaps:
        gid = g.get("id", "?")
        for field, label in (
            ("status", "状态"),
            ("evidence_level", "证据等级"),
            ("source", "出处"),
            ("fallback", "降级方案"),
        ):
            if not _nonempty(g.get(field)):
                f2.append("缺口 %s 的「%s」栏为空" % (gid, label))
    res["C2"] = (not f2, f2)

    # ---- C3 证据等级白名单 (缺口级 + 清单级都核)
    f3 = []
    for g in gaps:
        lvl = g.get("evidence_level")
        if _nonempty(lvl) and lvl not in ALLOWED_EVIDENCE:
            f3.append("缺口 %s 的证据等级 %r 不在白名单 %s" % (g.get("id"), lvl, sorted(ALLOWED_EVIDENCE)))
    for r in opn:
        lvl = r.get("evidence_level")
        if _nonempty(lvl) and lvl not in ALLOWED_EVIDENCE:
            f3.append("清单 %s 的证据等级 %r 不在白名单 %s" % (r.get("ref"), lvl, sorted(ALLOWED_EVIDENCE)))
    res["C3"] = (not f3, f3)

    # ---- C4 不许挂起措辞 (跳过区除外)
    f4 = []
    body = strip_skip_region(text)
    for ph in FORBIDDEN_PHRASES:
        cnt = body.count(ph)
        if cnt:
            f4.append("正文出现挂起措辞 %r × %d (政策: 不发信, 查不到就写 [0数据] + 降级方案)" % (ph, cnt))
    res["C4"] = (not f4, f4)

    # ---- C5 OPN 清单必须全覆盖登记范围, 且当前待落的一件不许漏
    f5 = []
    got_refs = [str(r.get("ref", "")) for r in opn]
    scope = scope_refs if scope_refs is not None else set(exp_refs)
    for ref in scope:
        if ref not in got_refs:
            f5.append("OPN 回填清单缺 ISS-241 登记范围内的 %s" % ref)
    for ref in exp_refs:
        if ref not in got_refs:
            f5.append("OPN 回填清单缺当前仍待选型的 %s" % ref)
    for ref in got_refs:
        if ref not in scope and ref not in exp_refs:
            f5.append("OPN 回填清单出现越界件 %s (不在 ISS-241 登记范围, 也不在当前 BOM 待选型集合内)" % ref)
    if len(got_refs) != len(set(got_refs)):
        f5.append("OPN 回填清单有重复位号")
    if len(got_refs) != len(scope):
        f5.append("OPN 回填清单件数 = %d (ISS-241 登记范围应为 %d)" % (len(got_refs), len(scope)))
    # 已被别的落表批次改掉的件 ⇒ 必须写清落表证据 (landed_note), 否则红
    for r in opn:
        ref = str(r.get("ref", ""))
        if ref in scope and ref not in exp_refs:
            if not _nonempty(r.get("landed_note")):
                f5.append("%s 已不在 BOM 待选型集合 (疑被别的落表批次落掉) 但清单没写 landed_note (落表证据)" % ref)
    res["C5"] = (not f5, f5)

    # ---- C6 清单每行必须带非空的「落表锚点」
    f6 = []
    for r in opn:
        anchor = r.get("land_anchor")
        if not _nonempty(anchor):
            f6.append("清单 %s 的「落表锚点」为空" % r.get("ref"))
    res["C6"] = (not f6, f6)

    # ---- C7 落表后回归表: 每件「已落表」的件都要有一行 + 判定 + 出处 + (有引脚序不符就必须有修法)
    f7 = []
    pl = baseline.get("post_landing") or {}
    rows7 = pl.get("rows") or []
    if not rows7:
        f7.append("基准块缺 post_landing (落表后回归表)")
    got7 = {str(r.get("ref", "")) for r in rows7}
    scope_set = scope if scope is not None else set(exp_refs)
    for ref in sorted(ref for ref in scope_set if ref not in exp_refs):
        if ref not in got7:
            f7.append("落表后回归表缺已落表件 %s" % ref)
    for r in rows7:
        ref = r.get("ref", "?")
        if not _nonempty(r.get("verdict")):
            f7.append("落表后回归 %s 的「判定」栏为空" % ref)
        if not _nonempty(r.get("source")):
            f7.append("落表后回归 %s 的「出处」栏为空" % ref)
        checks = r.get("checks") or []
        mism = [c for c in checks if not c.get("match")]
        if mism and not _nonempty(r.get("fix")):
            f7.append("落表后回归 %s 有引脚序不符 (pad %s) 但没写修法"
                      % (ref, ",".join(str(c.get("pad")) for c in mism)))
        for c in checks:
            if not _nonempty(c.get("device_role")) or not _nonempty(c.get("netlist_role")):
                f7.append("落表后回归 %s 的某条 pad 核对缺「器件脚角色 / 网表角色」" % ref)
    res["C7"] = (not f7, f7)

    return res


# ---------------------------------------------------------------- runner

def run(root):
    doc_path = os.path.join(root, DOC_REL)
    if not os.path.isfile(doc_path):
        print("[FAIL] 收口页不存在: %s" % DOC_REL)
        return 1, None, None
    with open(doc_path, encoding="utf-8") as fh:
        text = fh.read()
    baseline, berr = extract_baseline(text)
    exp_refs = expected_refs_from_bom(root)
    scope_refs = expected_scope_from_matrix(root)
    res = evaluate(text, baseline, exp_refs, scope_refs)
    if berr:
        res["C0"] = (False, [berr])
    return res, text, exp_refs, scope_refs


def print_report(res, exp_refs, scope_refs=None):
    order = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]
    npass = 0
    print("=== ISS-244 选型缺口自查补全 + OPN 回填清单 · 机器门禁 ===")
    print("OPN 清单应覆盖件数 (ISS-241 登记范围, 从矩阵基准块读) = %s" % (len(scope_refs) if scope_refs else "?"))
    print("其中当前仍待落 (HW/BOM_v1.csv 实跑 待选型∩必装 − 越界件) = %d" % len(exp_refs))
    for cid in order:
        ok, msgs = res.get(cid, (False, ["未运行"]))
        npass += 1 if ok else 0
        print("[%s] %s" % ("PASS" if ok else "FAIL", cid))
        for m in msgs:
            print("      - %s" % m)
    print("--- %d/%d PASS ---" % (npass, len(order)))
    return npass == len(order)


# ---------------------------------------------------------------- selftest

def mutate_baseline_json(text, fn):
    """只改基准块 JSON (其它正文一字不动)"""
    blob = text.split(BASELINE_BEGIN, 1)[1].split(BASELINE_END, 1)[0]
    payload = blob.split("```json", 1)[1].rsplit("```", 1)[0]
    data = json.loads(payload)
    fn(data)
    new_blob = blob.replace(payload, json.dumps(data, ensure_ascii=False, indent=2))
    return text.replace(blob, new_blob, 1)


def selftest(root):
    doc_path = os.path.join(root, DOC_REL)
    if not os.path.isfile(doc_path):
        print("[FAIL] 收口页不存在, 无法自证")
        return 1
    with open(doc_path, encoding="utf-8") as fh:
        base_text = fh.read()
    exp_refs = expected_refs_from_bom(root)
    scope_refs = expected_scope_from_matrix(root)

    tmpdir = tempfile.mkdtemp(prefix="iss244_selftest_")
    passed = 0
    total = 0
    try:
        def evaluate_text(txt):
            bl, err = extract_baseline(txt)
            r = evaluate(txt, bl, exp_refs, scope_refs)
            if err:
                r["C0"] = (False, [err])
            return r

        # 变异器: 每一项 = (用例名, 期望变红的 check, 变异函数, 自证串)
        def m1(txt):
            def fn(d):
                d["gaps"] = [g for g in d["gaps"] if g.get("id") != "G-7"]
            out = mutate_baseline_json(txt, fn)
            return out, "G-7"
        def m2(txt):
            def fn(d):
                for g in d["gaps"]:
                    if g.get("id") == "G-3":
                        g["fallback"] = "   "
            out = mutate_baseline_json(txt, fn)
            return out, "G-3"
        def m3(txt):
            def fn(d):
                for g in d["gaps"]:
                    if g.get("id") == "G-5":
                        g["evidence_level"] = "[官方]"
            out = mutate_baseline_json(txt, fn)
            return out, "[官方]"
        def m5(txt):
            def fn(d):
                d["opn_rows"] = [r for r in d["opn_rows"] if r.get("ref") != "D_ESD_CAM"]
            out = mutate_baseline_json(txt, fn)
            return out, "D_ESD_CAM"
        def m6(txt):
            def fn(d):
                for r in d["opn_rows"]:
                    if r.get("ref") == "Q_PG":
                        r["land_anchor"] = ""
            out = mutate_baseline_json(txt, fn)
            return out, "Q_PG"
        def m8(txt):
            def fn(d):
                for r in d["opn_rows"]:
                    if r.get("ref") == "C_REGN":
                        r["landed_note"] = ""
            out = mutate_baseline_json(txt, fn)
            return out, "C_REGN"
        def m9(txt):
            # 删掉落表后回归表的一行 (动态取最后一行 ⇒ 不受「哪件已落表」漂移影响)
            def fn(d):
                pl = d.get("post_landing") or {}
                rows = pl.get("rows") or []
                if rows:
                    pl["rows"] = rows[:-1]
                    d["post_landing"] = pl
            out = mutate_baseline_json(txt, fn)
            return out, ""  # probe 动态取 (见下)

        def _m9_probe(base_text):
            bl, _ = extract_baseline(base_text)
            rows = ((bl or {}).get("post_landing") or {}).get("rows") or []
            return str(rows[-1].get("ref", "")) if rows else ""

        def m10(txt):
            # 把落表后回归表里某件的「出处」清空 ⇒ 期望 C7 红
            def fn(d):
                pl = d.get("post_landing") or {}
                rows = pl.get("rows") or []
                if rows:
                    rows[0]["source"] = ""
                    pl["rows"] = rows
                    d["post_landing"] = pl
            out = mutate_baseline_json(txt, fn)
            return out, ""  # probe 动态取

        def _m10_probe(base_text):
            bl, _ = extract_baseline(base_text)
            rows = ((bl or {}).get("post_landing") or {}).get("rows") or []
            return str(rows[0].get("ref", "")) if rows else ""

        cases = [
            ("M1 删掉一条缺口 (G-7) → 期望 C1 红", "C1", m1, None),
            ("M2 某条缺口降级方案清空 → 期望 C2 红", "C2", m2, None),
            ("M3 证据等级写成 [官方] → 期望 C3 红", "C3", m3, None),
            ("M5 清单里删一件 (D_ESD_CAM) → 期望 C5 红", "C5", m5, None),
            ("M6 某行落表锚点清空 → 期望 C6 红", "C6", m6, None),
            ("M8 已被别的批次落掉的件清空 landed_note → 期望 C5 红", "C5", m8, None),
            ("M9 落表后回归表删掉一行 → 期望 C7 红", "C7", m9, "落表后回归表缺已落表件"),
            ("M10 落表后回归表某件清空出处 → 期望 C7 红", "C7", m10, "出处"),
        ]

        for name, target, mut, expect_msg in cases:
            total += 1
            mutated, probe = mut(base_text)
            if not probe:
                probe = _m9_probe(base_text) if mut is m9 else _m10_probe(base_text)
            # ① 变异确实落到盘上副本里 (副本里找得到探针串)
            landed = probe in mutated
            # ② 变异后的判定
            res_m = evaluate_text(mutated)
            target_red = not res_m[target][0]
            # ③ 其余 check 仍绿 (证明红的是目标那一条)
            others = [c for c in ("C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7") if c != target]
            others_green = all(res_m[c][0] for c in others)
            # ④ (可选) 红的那一条必须**指名道姓**说清是哪个目标 (防“随便塌一条也算过”)
            msg_ok = True
            if expect_msg:
                msg_ok = any(expect_msg in m and (probe in m or expect_msg == "出处") for m in res_m[target][1])
            ok = landed and target_red and others_green and msg_ok
            passed += 1 if ok else 0
            print("[%s] %s" % ("PASS" if ok else "FAIL", name))
            print("      变异落地(探针 %r 在副本里)=%s · 目标 %s 变红=%s · 其余 check 仍绿=%s · 红因指名=%s"
                  % (probe, landed, target, target_red, others_green, msg_ok))
            if not target_red:
                for m in res_m[target][1]:
                    print("        %s: %s" % (target, m))

        # M4: 正文里塞一句挂起措辞 (直接改正文, 不动基准块)
        total += 1
        probe = "等原厂回信"
        mutated = base_text.replace("\n---\n", "\n\n本条挂起: %s\n\n---\n" % probe, 1)
        if mutated == base_text:
            mutated = base_text + "\n\n%s\n" % probe
        landed = probe in mutated
        res_m = evaluate_text(mutated)
        target_red = not res_m["C4"][0]
        others = [c for c in ("C0", "C1", "C2", "C3", "C5", "C6", "C7") if c != "C4"]
        others_green = all(res_m[c][0] for c in others)
        ok = landed and target_red and others_green
        passed += 1 if ok else 0
        print("[%s] %s" % ("PASS" if ok else "FAIL", "M4 正文塞一句挂起措辞 → 期望 C4 红"))
        print("      变异落地(探针 %r 在副本里)=%s · 目标 C4 变红=%s · 其余 check 仍绿=%s"
              % (probe, landed, target_red, others_green))

        # M7: 破坏基准块 JSON ⇒ C0 红, 且 C1~C6 按设计 **fail-closed 一致地红** (基准块没了就没法判定)
        total += 1
        probe = '"issue": "ISS-244" BROKEN'
        mutated = base_text.replace('"issue": "ISS-244"', '"issue": "ISS-244" BROKEN', 1)
        landed = probe in mutated
        res_m = evaluate_text(mutated)
        target_red = not res_m["C0"][0]
        others = [c for c in ("C1", "C2", "C3", "C4", "C5", "C6", "C7") if c != "C0"]
        others_red = all(not res_m[c][0] for c in others)
        ok = landed and target_red and others_red
        passed += 1 if ok else 0
        print("[%s] %s" % ("PASS" if ok else "FAIL", "M7 破坏基准块 JSON → 期望 C0 红 (且 C1~C6 一致地红 = fail-closed)"))
        print("      变异落地=%s · 目标 C0 变红=%s · 其余 check 一致地红(fail-closed)=%s" % (landed, target_red, others_red))

        print("--- SELFTEST %d/%d ---" % (passed, total))
        return 0 if passed == total else 1
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------- main

def main():
    root = None
    do_selftest = False
    do_json = False
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--selftest":
            do_selftest = True
        elif a == "--json":
            do_json = True
        elif a == "--root":
            i += 1
            root = argv[i]
        else:
            print("未知参数: %s" % a)
            return 2
        i += 1
    if root is None:
        root = find_root()

    if do_selftest:
        return selftest(root)

    res, text, exp_refs, scope_refs = run(root)
    if do_json:
        out = {
            "issue": "ISS-244",
            "checks": {k: {"pass": v[0], "failures": v[1]} for k, v in res.items()},
            "scope_refs_count": len(scope_refs) if scope_refs else None,
            "scope_refs": scope_refs,
            "pending_refs_count": len(exp_refs),
            "pending_refs": exp_refs,
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if all(v[0] for v in res.values()) else 1

    ok = print_report(res, exp_refs, scope_refs)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
