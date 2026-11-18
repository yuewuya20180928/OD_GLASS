#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-241 · BOM 待选型件 OPN 选型证据矩阵 — 机器门禁
作者: sw-lead (软件总工) · 2026-11-16 · 交卷给 main / 项目总工

用法:
    python3 HW/check_part_selection_matrix.py             # 正常跑 ⇒ rc=0 = 全过
    python3 HW/check_part_selection_matrix.py --selftest   # 反向用例自证 ⇒ rc=0 = N/N 全抓到
    python3 HW/check_part_selection_matrix.py --json       # 机器可读输出
    python3 HW/check_part_selection_matrix.py --root DIR   # 指定项目根 (默认自动定位)

检查项 (C0~C7):
    C0 基准块存在且是合法 JSON
    C1 覆盖: 矩阵含全部 22 个位号 (21 个在册 + R_SUPV_DIV1/R_SUPV_DIV2 这一对) 一个不缺
    C2 每件 ≥2 个候选 + 候选栏 (型号/链接/参数/封装/证据等级) 全部非空
    C3 每件都有 封装兼容性结论 (兼容/条件兼容/不兼容/落N焊盘…) + 理由 + pads_required
    C4 每件都有 证据等级 + 降级方案 (降级方案不许留空) + 推荐项 (含 why/cost/disclaimer)
    C5 证据等级只能取 [官网]/[实测]/[媒体]/[推算]/[0数据] 五者之一 (候选级与件级都核)
    C6 不许出现「已定型」式空话 / 空候选型号栏 (候选型号栏不许为空)
    C7 矩阵位号不许超出本单范围 (expected_refs 之外的一律红)

--selftest 反向用例 (每条都自证「真的改到了目标」):
    M1 删掉一个位号        → 期望 C1 变红
    M2 把某件候选清空      → 期望 C2 变红
    M3 把某件降级方案删掉  → 期望 C4 变红
    M4 塞一个越界位号      → 期望 C7 变红
    M5 把证据等级写成非法词 → 期望 C5 变红
    M6 删掉封装兼容性结论  → 期望 C3 变红
    M7 把推荐项清空        → 期望 C4 变红
    M8 把 baseline JSON 破坏 → 期望 C0 变红
    M9 把某件候选降到 1 个  → 期望 C2 变红
"""

import json
import os
import re
import shutil
import sys
import tempfile

DOC_REL = os.path.join("HW", "PART_SELECTION_MATRIX_2026-11-16.md")
BASELINE_BEGIN = "<!-- BEGIN 选型证据基准块 -->"
BASELINE_END = "<!-- END 选型证据基准块 -->"

# 证据等级白名单 (五级固定, 写死的)
ALLOWED_EVIDENCE = {"[官网]", "[实测]", "[媒体]", "[推算]", "[0数据]"}

# 封装兼容性结论允许的取值形态 (前 4 个是本板 MAIN_PCB 判定形态, 后 2 个是充电板占位待定形态)
ALLOWED_VERDICTS = (
    "兼容",
    "条件兼容",
    "不兼容",
    "落2焊盘+充电板侧封装另行定",
    "落3焊盘+充电板侧封装另行定",
)

# 空话黑名单: 出现在候选型号栏/参数栏里的这些词 ⇒ 判为空话 (C6)
EMPTY_TALK = ("已定型", "待定", "待查", "待选型", "TBD", "待补", "待填", "???")

# 越界位号 (ISS-172 在办, 本单不许越界)
OUT_OF_SCOPE = {"U_PWR_SW", "U_EN_SW"}


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


def extract_baseline(text):
    """从 markdown 里切出基准块并解 JSON; 失败抛 ValueError"""
    if BASELINE_BEGIN not in text or BASELINE_END not in text:
        raise ValueError("基准块标记缺失 (BEGIN/END)")
    seg = text.split(BASELINE_BEGIN, 1)[1].split(BASELINE_END, 1)[0]
    if "```json" not in seg:
        raise ValueError("基准块里没有 ```json 围栏")
    body = seg.split("```json", 1)[1]
    body = body.rsplit("```", 1)[0]
    return json.loads(body)


def _nonempty(s):
    return isinstance(s, str) and s.strip() != ""


# ---------------------------------------------------------------- checks
# 每个 check 返回 (name, ok, message)

def run_checks(doc_text):
    """返回 [(check_id, ok, msg), ...]"""
    results = []

    # C0 基准块可解析
    try:
        data = extract_baseline(doc_text)
        results.append(("C0", True, "基准块 JSON 解析通过"))
    except Exception as e:
        results.append(("C0", False, "基准块不是合法 JSON: %s" % e))
        return results

    expected = list(data.get("expected_refs", []))
    brief_enum = list(data.get("brief_enumerated_refs", []))
    out_of_scope = set(data.get("out_of_scope_refs", [])) | OUT_OF_SCOPE
    items = data.get("items", [])
    by_ref = {it.get("ref"): it for it in items}

    # C1 覆盖: 一个不缺
    missing = [r for r in expected if r not in by_ref]
    missing_brief = [r for r in brief_enum if r not in by_ref]
    if missing or missing_brief:
        results.append(("C1", False, "缺位号: expected=%s brief枚举=%s" % (missing, missing_brief)))
    else:
        results.append(("C1", True, "覆盖 %d/%d 位号 (含任务书枚举的 %d 个全齐)"
                        % (len(by_ref), len(expected), len(brief_enum))))

    # C2/C3/C4/C5/C6 逐件核
    c2_bad, c3_bad, c4_bad, c5_bad, c6_bad = [], [], [], [], []
    for ref, it in sorted(by_ref.items()):
        cands = it.get("candidates") or []
        # C2 ≥2 候选 + 候选栏非空
        if len(cands) < 2:
            c2_bad.append("%s 只有 %d 个候选" % (ref, len(cands)))
        else:
            for i, c in enumerate(cands):
                for field in ("pn", "mfr", "url", "params", "package"):
                    if not _nonempty(c.get(field)):
                        c2_bad.append("%s 候选%d 字段 %s 为空" % (ref, i + 1, field))
                if not _nonempty(c.get("evidence")):
                    c2_bad.append("%s 候选%d 缺证据等级" % (ref, i + 1))
                if not isinstance(c.get("pads"), int) or c.get("pads") < 2:
                    c2_bad.append("%s 候选%d 缺 pads 字段" % (ref, i + 1))

        # C3 封装兼容性结论
        pc = it.get("package_compat") or {}
        verdict = pc.get("verdict")
        if not _nonempty(verdict) or not _nonempty(pc.get("reason")):
            c3_bad.append("%s 封装兼容性结论或理由为空" % ref)
        elif not any(v in verdict for v in ALLOWED_VERDICTS):
            c3_bad.append("%s 封装兼容性结论取值非法: %r" % (ref, verdict))
        if not isinstance(pc.get("pads_required"), int) or pc.get("pads_required") < 2:
            c3_bad.append("%s 缺 pads_required" % ref)

        # C4 证据等级 / 降级方案 / 推荐项
        if not _nonempty(it.get("evidence")):
            c4_bad.append("%s 件级证据等级为空" % ref)
        if not _nonempty(it.get("fallback")):
            c4_bad.append("%s 降级方案为空" % ref)
        rec = it.get("recommendation") or {}
        for field in ("pick", "why", "cost", "disclaimer"):
            if not _nonempty(rec.get(field)):
                c4_bad.append("%s 推荐项缺 %s" % (ref, field))

        # C5 证据等级白名单 (件级 + 候选级)
        if it.get("evidence") not in ALLOWED_EVIDENCE:
            c5_bad.append("%s 件级证据等级非法: %r" % (ref, it.get("evidence")))
        for i, c in enumerate(cands):
            ev = c.get("evidence")
            if ev not in ALLOWED_EVIDENCE:
                c5_bad.append("%s 候选%d 证据等级非法: %r" % (ref, i + 1, ev))

        # C6 空话: 候选型号栏不许空/不许「已定型」式空话
        for i, c in enumerate(cands):
            pn = c.get("pn") or ""
            if not _nonempty(pn):
                c6_bad.append("%s 候选%d 型号栏为空" % (ref, i + 1))
            else:
                for word in EMPTY_TALK:
                    if word in pn:
                        c6_bad.append("%s 候选%d 型号栏含空话 %r" % (ref, i + 1, word))
            if not _nonempty(c.get("params")):
                c6_bad.append("%s 候选%d 参数栏为空" % (ref, i + 1))

    results.append(("C2", not c2_bad, "候选完整性: %s" % ("; ".join(c2_bad) if c2_bad else "每件 ≥2 候选且各栏非空")))
    results.append(("C3", not c3_bad, "封装兼容性: %s" % ("; ".join(c3_bad) if c3_bad else "每件有结论+理由+pads_required")))
    results.append(("C4", not c4_bad, "证据/降级/推荐: %s" % ("; ".join(c4_bad) if c4_bad else "每件齐全")))
    results.append(("C5", not c5_bad, "证据等级白名单: %s" % ("; ".join(c5_bad) if c5_bad else "全部合法")))
    results.append(("C6", not c6_bad, "空话检查: %s" % ("; ".join(c6_bad) if c6_bad else "无空候选/无已定型式空话")))

    # C7 不许越界
    stray = sorted(set(by_ref) - set(expected))
    stray += sorted(set(by_ref) & out_of_scope)
    if stray:
        results.append(("C7", False, "越界位号: %s" % stray))
    else:
        results.append(("C7", True, "无越界位号 (OUT_OF_SCOPE %s 全部不在册)" % sorted(out_of_scope)))

    return results


# ---------------------------------------------------------------- selftest

def _mutate_drop_ref(text):
    """M1: 删掉一个位号 (把 Q_PG 的 ref 改成不在册的位号 ⇒ 该位号从册上消失)"""
    return text.replace('"ref": "Q_PG",', '"ref": "Q_PG_DELETED_FOR_SELFTEST",', 1)


def _mutate_empty_cand(text):
    """M2: 把某件候选清空"""
    return text.replace('"pn": "AO3400A",', '"pn": "",', 1)


def _mutate_drop_fallback(text):
    """M3: 把某件降级方案删掉"""
    return re.sub(r'"fallback": "若不许重画 land, 改选 2 脚且厂商 land 间距约 2\.30mm 的器件[^"]*"',
                  '"fallback": ""', text, count=1)


def _mutate_stray_ref(text):
    """M4: 塞一个越界位号"""
    return text.replace('"ref": "Q_PG",', '"ref": "U_PWR_SW",', 1)


def _mutate_bad_evidence(text):
    """M5: 证据等级写成非法词"""
    return text.replace('"evidence": "[官网]",\n        "url": "https://www.aosmd.com/pdfs/datasheet/AO3407A.pdf"',
                        '"evidence": "[官方]",\n        "url": "https://www.aosmd.com/pdfs/datasheet/AO3407A.pdf"', 1)


def _mutate_drop_compat(text):
    """M6: 删掉封装兼容性结论"""
    return re.sub(r'"verdict": "条件兼容",\n      "reason": "焊盘数 3=3 OK; 焊盘网络 pad1=PG_AND',
                  '"verdict": "",\n      "reason": "焊盘数 3=3 OK; 焊盘网络 pad1=PG_AND', text, count=1)


def _mutate_drop_rec(text):
    """M7: 把推荐项清空"""
    return text.replace('"why": "命中 \'关断漏电 nA 级\' 硬判据', '"why": "", "x": "命中 \'关断漏电 nA 级\' 硬判据', 1)


def _mutate_break_json(text):
    """M8: 破坏 baseline JSON"""
    return text.replace('"issue": "ISS-241",', '"issue": "ISS-241",,', 1)


def _mutate_one_cand(text):
    """M9: 把某件候选降到 1 个"""
    # 删掉 AO3400A 候选块 (Q_AND 的第一个候选)
    pat = re.compile(
        r'\{\n\s*"pn": "AO3400A",\n\s*"mfr": "Alpha & Omega Semiconductor",\n\s*"evidence": "\[官网\]",\n'
        r'\s*"url": "https://www\.aosmd\.com/pdfs/datasheet/AO3400A\.pdf",\n'
        r'\s*"params": "30V N-ch SOT23; VGS\(th\) 0\.65/1\.05/1\.45V; RDS\(on\) 26\.5mOhm@10V.*?\n\s*"pads": 3\n\s*\},',
        re.S)
    return pat.sub("", text, count=1)


MUTATIONS = [
    ("M1", "删掉一个位号 (Q_PG)", _mutate_drop_ref, "C1"),
    ("M2", "把某件候选清空 (AO3400A 的 pn)", _mutate_empty_cand, "C2"),
    ("M3", "把某件降级方案删空 (D_ESD_USB_D)", _mutate_drop_fallback, "C4"),
    ("M4", "塞一个越界位号 (U_PWR_SW)", _mutate_stray_ref, "C7"),
    ("M5", "证据等级写成非法词 [官方]", _mutate_bad_evidence, "C5"),
    ("M6", "删掉封装兼容性结论 (Q_ENVC)", _mutate_drop_compat, "C3"),
    ("M7", "把推荐项 why 清空 (Q_PG)", _mutate_drop_rec, "C4"),
    ("M8", "破坏 baseline JSON", _mutate_break_json, "C0"),
    ("M9", "把某件候选降到 1 个 (Q_AND)", _mutate_one_cand, "C2"),
]


def run_selftest(doc_text):
    """返回 (ok, lines)"""
    lines = []
    all_ok = True
    base_red = {cid for cid, ok, _ in run_checks(doc_text) if not ok}
    if base_red:
        lines.append("[FAIL] 基线本身就不绿 (C%s 红) — selftest 无法进行" % ",".join(sorted(base_red)))
        return False, lines

    for mid, desc, fn, expect in MUTATIONS:
        mutated = fn(doc_text)
        if mutated == doc_text:
            lines.append("[FAIL] %s %s — 变异没改到东西 (自证失败)" % (mid, desc))
            all_ok = False
            continue
        res = run_checks(mutated)
        red = sorted({cid for cid, ok, _ in res if not ok})
        # 落盘回读再跑一遍 (ISS-227 同款教训: 证明"文档改了 ⇒ 门禁读盘后也红")
        tmp = tempfile.mkdtemp(prefix="iss241_selftest_")
        try:
            p = os.path.join(tmp, "mut.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write(mutated)
            with open(p, "r", encoding="utf-8") as f:
                reread = f.read()
            res2 = run_checks(reread)
            red2 = sorted({cid for cid, ok, _ in res2 if not ok})
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        if expect in red and expect in red2:
            lines.append("[PASS] %s %s — %s 变红 (共 %d 条: %s) [落盘回读复核同红]"
                         % (mid, desc, expect, len(red), ",".join(red)))
        else:
            lines.append("[FAIL] %s %s — 期望 %s 变红, 实际 %s / 回读 %s"
                         % (mid, desc, expect, red or "无", red2 or "无"))
            all_ok = False
    return all_ok, lines


# ---------------------------------------------------------------- main

def main(argv):
    root = find_root()
    as_json = "--json" in argv
    do_selftest = "--selftest" in argv
    if "--root" in argv:
        root = argv[argv.index("--root") + 1]

    doc_path = os.path.join(root, DOC_REL)
    if not os.path.isfile(doc_path):
        print("[check_part_selection_matrix] FAIL — 找不到矩阵文档: %s" % doc_path)
        return 1

    with open(doc_path, "r", encoding="utf-8") as f:
        doc_text = f.read()

    if do_selftest:
        ok, lines = run_selftest(doc_text)
        for ln in lines:
            print(ln)
        n_pass = sum(1 for ln in lines if ln.startswith("[PASS]"))
        n_total = len(MUTATIONS)
        print("selftest: %d/%d" % (n_pass, n_total))
        if not ok or n_pass != n_total:
            print("[check_part_selection_matrix] SELFTEST FAIL")
            return 1
        print("[check_part_selection_matrix] PASS — 反向用例 %d/%d 全抓到" % (n_pass, n_total))
        return 0

    results = run_checks(doc_text)
    if as_json:
        print(json.dumps({
            "doc": doc_path,
            "checks": [{"id": cid, "ok": ok, "msg": msg} for cid, ok, msg in results],
            "all_pass": all(ok for _, ok, _ in results),
        }, ensure_ascii=False, indent=2))
    else:
        print("[check_part_selection_matrix] 门禁检查: %s" % DOC_REL)
        for cid, ok, msg in results:
            print("  [%s] %s — %s" % ("PASS" if ok else "FAIL", cid, msg))
        n_ok = sum(1 for _, ok, _ in results if ok)
        if n_ok == len(results):
            print("[check_part_selection_matrix] PASS — 选型证据矩阵门禁全过 (%d/%d)" % (n_ok, len(results)))
            return 0
        print("[check_part_selection_matrix] FAIL — %d/%d 条红" % (len(results) - n_ok, len(results)))
        return 1
    return 0 if all(ok for _, ok, _ in results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
