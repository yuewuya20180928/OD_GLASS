#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/display_biosafety_v2_check.py
================================================================================
显示口径收口 (ISS-134 遗留 need `iss134_mech_close_legacy_zoujuan_refs`) +
光生物安全眼盒约束落位 (ISS-208) 的**机器门禁**。

判据真源 (只引用, 不许改一个字):
  * MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md   (md5 96239070dc7c0ec00edb1b758a698769)
  * MECH/JBD_ROLE_NARROWING.md              (md5 bda4a29464336bc1452c913602ce3f46)

检查项 (rc=0 = 全过; 任一条不过 ⇒ rc=1 并点名是哪一条):
  [C1] 5 份旧文档里的「走鹃」命中: **活动口径必须 = 0**; 历史沿革允许保留
       (每处历史沿革必须带「已作废 (2026-11-15, ISS-134 V2)」标注)
  [C2] 眼盒约束条目是否已落在**结构侧真源** (MECH/MECH_BUDGET.md): 关键词 + 数值 62 都要命中
  [C3] V2 判据 6 条的关键量是否被结构侧**引用** (引用即可, 不许复制改写判据原文)
  [C4] 交卷件 MECH/DISPLAY_LEGACY_V2_CLOSEOUT.md 的 33 处逐处定性表自洽 (33 行 + 分布对得上)
  [C5] 判据文件与角色收窄记录 md5 未变 (证明本单没改判据)

用法:
  python3 MECH/display_biosafety_v2_check.py             # 跑门禁
  python3 MECH/display_biosafety_v2_check.py --selftest   # 跑自测 (5 个用例, 全在临时目录里做)
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ---------------------------------------------------------------- 常量 (单一真源)
MARKER = "已作废 (2026-11-15, ISS-134 V2)"

# 5 份旧文档: 收口前的「走鹃」命中数 (ISS-134 交卷时 main 实测 21/6/3/2/1 = 33)
LEGACY_DOCS = [
    ("MECH/MECH_BUDGET.md", 21),
    ("MECH/PROTOTYPE_PLAN.md", 6),
    ("MECH/SOC_CARRIER_EVAL.md", 3),
    ("MECH/STRUCT_REVIEW_ISS065.md", 2),
    ("MECH/CLEARANCE_FIX.md", 1),
]
LEGACY_TOTAL = 33

STRUCT_TRUTH = "MECH/MECH_BUDGET.md"          # 结构侧真源 (空间/厚度/散热主表)
CLOSEOUT = "MECH/DISPLAY_LEGACY_V2_CLOSEOUT.md"
V2_DOC = "MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md"
JN_DOC = "MECH/JBD_ROLE_NARROWING.md"
CRITERIA_MD5 = {
    V2_DOC: "96239070dc7c0ec00edb1b758a698769",
    JN_DOC: "bda4a29464336bc1452c913602ce3f46",
}

# 眼盒约束条目的关键词 (结构真源里必须全中)
EYEBOX_KEYS = [
    "X-1", "X-2", "X-3", "X-4", "X-5", "X-6",   # 条目号 (下一单直接引)
    "眼盒",                                        # 主题词
    "62 mm²",                                      # ★数值
    "A_e",                                         # 公式符号
    "镜框上沿",                                     # 它夹住的厚度
    "鼻梁",                                         # 它夹住的空间
    "DISPLAY_BIOSAFETY_CRITERIA_V2.md",             # 判据引用
]

# V2 判据 6 条 → 结构侧必须引用的关键量 (引用即可, 不许复制改写判据原文)
V2_SIX = [
    ("① 出光面辐亮度", ["1500 cd/m²", "4000 cd/m²"]),
    ("② 光谱与蓝光占比", ["460 nm", "25%"]),
    ("③ 全温区亮度/腔体热", ["50 °C", "60 °C"]),
    ("④ IEC 62471 条款", ["62471-7", "100 W/(m²·sr)"]),
    ("⑤ 观察距离与视场角", ["15–20 mm", "0.011 rad"]),
    ("⑥ 波导后等效辐亮度折算", ["0.1234", "62 mm²"]),
]


# ---------------------------------------------------------------- 小工具
def _read(root: str, rel: str) -> str:
    with open(os.path.join(root, rel), "r", encoding="utf-8") as f:
        return f.read()


def _md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- [C1] 走鹃收口
def check_c1(root: str):
    total_active = 0
    total_hist = 0
    per_file = []
    offenders = []
    for rel, _expect in LEGACY_DOCS:
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            return False, "文件缺失: %s" % rel
        act, hist = 0, 0
        for i, line in enumerate(_read(root, rel).split("\n"), 1):
            if "走鹃" not in line:
                continue
            if MARKER in line:
                hist += 1
            else:
                act += 1
                offenders.append("%s:%d" % (rel, i))
        total_active += act
        total_hist += hist
        per_file.append("%s %d/%d" % (rel.split("/")[-1], act, hist))
    ok = total_active == 0
    detail = "活动口径 = %d (必须 0) ; 历史沿革 = %d ; 逐文件(活动/历史): %s" % (
        total_active, total_hist, " · ".join(per_file))
    if offenders:
        detail += " ; 违规行: " + ", ".join(offenders[:8])
    return ok, detail


# ---------------------------------------------------------------- [C2] 眼盒条目落位
def check_c2(root: str):
    path = os.path.join(root, STRUCT_TRUTH)
    if not os.path.exists(path):
        return False, "结构侧真源缺失: %s" % STRUCT_TRUTH
    text = _read(root, STRUCT_TRUTH)
    missing = [k for k in EYEBOX_KEYS if k not in text]
    ok = not missing
    detail = "结构真源 %s 命中 %d/%d 关键词" % (STRUCT_TRUTH, len(EYEBOX_KEYS) - len(missing), len(EYEBOX_KEYS))
    if missing:
        detail += " ; 缺: " + ", ".join(missing)
    else:
        detail += " (含数值 62 mm² + 眼盒 + 镜框上沿 + 鼻梁)"
    return ok, detail


# ---------------------------------------------------------------- [C3] V2 六条关键量被引用
def check_c3(root: str):
    path = os.path.join(root, STRUCT_TRUTH)
    if not os.path.exists(path):
        return False, "结构侧真源缺失: %s" % STRUCT_TRUTH
    text = _read(root, STRUCT_TRUTH)
    missing = []
    for name, toks in V2_SIX:
        for t in toks:
            if t not in text:
                missing.append("%s[%s]" % (name, t))
    ok = not missing
    detail = "V2 判据 6 条关键量: 命中 %d/%d" % (
        sum(1 for _n, ts in V2_SIX for t in ts if t in text),
        sum(len(ts) for _n, ts in V2_SIX))
    if missing:
        detail += " ; 未引用: " + ", ".join(missing)
    return ok, detail


# ---------------------------------------------------------------- [C4] 交卷件 33 行定性表自洽
_ROW_RE = re.compile(r"^\|\s*\*\*L-(\d\d)\*\*\s*\|\s*`([^`]+)`\s*\|")


def check_c4(root: str):
    path = os.path.join(root, CLOSEOUT)
    if not os.path.exists(path):
        return False, "交卷件缺失: %s" % CLOSEOUT
    rows = []
    bad = []
    for line in _read(root, CLOSEOUT).split("\n"):
        m = _ROW_RE.match(line)
        if not m:
            continue
        rid, fpath = m.group(1), m.group(2)
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        # 列序: # | 文件 | 原行号 | 原句摘要 | 类别 | 处置 | 机器分类
        klass = cells[4].replace("**", "") if len(cells) > 4 else ""
        action = cells[5] if len(cells) > 5 else ""
        rows.append((rid, fpath, klass))
        if klass not in ("活动", "历史"):
            bad.append("%s 类别缺 (%s)" % (rid, klass))
        if not action or action in ("-", "—"):
            bad.append("%s 处置缺" % rid)
    ok = True
    detail = ""
    if len(rows) != LEGACY_TOTAL:
        ok = False
        detail = "定性表行数 = %d (必须 %d) ; " % (len(rows), LEGACY_TOTAL)
    dist = {}
    for _rid, fpath, _k in rows:
        dist[fpath] = dist.get(fpath, 0) + 1
    for rel, expect in LEGACY_DOCS:
        got = dist.get(rel, 0)
        if got != expect:
            ok = False
            detail += "%s 行数 %d≠%d ; " % (rel, got, expect)
    if bad:
        ok = False
        detail += "行内容缺陷: " + ", ".join(bad[:5]) + " ; "
    if ok:
        detail = "定性表 %d 行, 分布 %s 与收口前一致 (21/6/3/2/1)" % (
            len(rows), "/".join(str(dist.get(rel, 0)) for rel, _e in LEGACY_DOCS))
    return ok, detail


# ---------------------------------------------------------------- [C5] 判据文件 md5 未变
def check_c5(root: str):
    bad = []
    for rel, expect in CRITERIA_MD5.items():
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            bad.append("%s 缺失" % rel)
            continue
        got = _md5(p)
        if got != expect:
            bad.append("%s md5 %s≠%s" % (rel, got, expect))
    ok = not bad
    return ok, ("判据文件未改动 (md5 一致): " + ", ".join(CRITERIA_MD5) if ok
                else "判据文件被改: " + ", ".join(bad))


CHECKS = [
    ("C1", "走鹃旧口径收口 (5 份旧文档)", check_c1),
    ("C2", "眼盒约束条目落在结构侧真源", check_c2),
    ("C3", "V2 判据 6 条关键量被结构侧引用", check_c3),
    ("C4", "交卷件 33 处逐处定性表自洽", check_c4),
    ("C5", "判据文件 (V2 / JN) 未被改动", check_c5),
]


def run_checks(root: str):
    results = []
    for cid, name, fn in CHECKS:
        try:
            ok, detail = fn(root)
        except Exception as exc:  # noqa: BLE001 — 门禁不能因异常假绿
            ok, detail = False, "检查异常: %r" % (exc,)
        results.append((cid, name, ok, detail))
    return results


# ---------------------------------------------------------------- 自测
def _copy_fixture(tmp: str):
    files = set(rel for rel, _ in LEGACY_DOCS) | {
        STRUCT_TRUTH, CLOSEOUT, V2_DOC, JN_DOC}
    for rel in files:
        src = os.path.join(ROOT, rel)
        dst = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)


def _mutate(root: str, rel: str, fn):
    path = os.path.join(root, rel)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    with open(path, "w", encoding="utf-8") as f:
        f.write(fn(text))


def selftest() -> int:
    cases = []

    with tempfile.TemporaryDirectory(prefix="dbv2_selftest_") as tmp:
        # ST-1 基线: 未改 ⇒ 全过
        _copy_fixture(tmp)
        res = run_checks(tmp)
        cases.append(("ST-1 基线 (未改) ⇒ 期望全过 rc=0",
                      all(r[2] for r in res), [r[0] for r in res if not r[2]]))

    with tempfile.TemporaryDirectory(prefix="dbv2_selftest_") as tmp:
        # ST-2 故意塞一条活动口径 (无作废标注) ⇒ 必须被抓
        _copy_fixture(tmp)
        _mutate(tmp, STRUCT_TRUTH,
                lambda t: t + "\n| 走鹃Ⅱ 光机 仍在本方案里 | 是 | 是 |\n")
        res = run_checks(tmp)
        failed = [r[0] for r in res if not r[2]]
        cases.append(("ST-2 塞一条活动口径 ⇒ 必须被 C1 抓",
                      "C1" in failed and not all(r[2] for r in res), failed))

    with tempfile.TemporaryDirectory(prefix="dbv2_selftest_") as tmp:
        # ST-3 删掉眼盒约束数值 62 mm² ⇒ 必须被 C2 抓
        _copy_fixture(tmp)
        _mutate(tmp, STRUCT_TRUTH, lambda t: t.replace("62 mm²", "XX mm²"))
        res = run_checks(tmp)
        failed = [r[0] for r in res if not r[2]]
        cases.append(("ST-3 删掉眼盒数值 62 ⇒ 必须被 C2 抓",
                      "C2" in failed and not all(r[2] for r in res), failed))

    with tempfile.TemporaryDirectory(prefix="dbv2_selftest_") as tmp:
        # ST-4 删掉 V2 判据 ⑥ 的关键量 0.1234 ⇒ 必须被 C3 抓
        _copy_fixture(tmp)
        _mutate(tmp, STRUCT_TRUTH, lambda t: t.replace("0.1234", "X.XXXX"))
        res = run_checks(tmp)
        failed = [r[0] for r in res if not r[2]]
        cases.append(("ST-4 删掉判据关键量 0.1234 ⇒ 必须被 C3 抓",
                      "C3" in failed and not all(r[2] for r in res), failed))

    with tempfile.TemporaryDirectory(prefix="dbv2_selftest_") as tmp:
        # ST-5 破坏交卷件定性表 (删两行) ⇒ 必须被 C4 抓
        _copy_fixture(tmp)
        _mutate(tmp, CLOSEOUT, lambda t: "\n".join(
            ln for ln in t.split("\n") if not ln.startswith("| **L-3")))
        res = run_checks(tmp)
        failed = [r[0] for r in res if not r[2]]
        cases.append(("ST-5 破坏 33 行定性表 ⇒ 必须被 C4 抓",
                      "C4" in failed and not all(r[2] for r in res), failed))

    with tempfile.TemporaryDirectory(prefix="dbv2_selftest_") as tmp:
        # ST-6 篡改判据文件一个字节 ⇒ 必须被 C5 抓
        _copy_fixture(tmp)
        _mutate(tmp, V2_DOC, lambda t: t + "\n<!-- touched -->\n")
        res = run_checks(tmp)
        failed = [r[0] for r in res if not r[2]]
        cases.append(("ST-6 篡改判据文件 ⇒ 必须被 C5 抓",
                      "C5" in failed and not all(r[2] for r in res), failed))

    print("=== MECH/display_biosafety_v2_check.py --selftest (ISS-208) ===")
    bad = 0
    for name, ok, failed in cases:
        print("  %-4s %-44s %s" % (name.split(" ")[0], name.split(" ", 1)[1],
                                  "PASS" if ok else "FAIL (抓到: %s)" % (failed,)))
        if not ok:
            bad += 1
    print("自测: %d/%d 用例通过" % (len(cases) - bad, len(cases)))
    return 0 if bad == 0 else 1


# ---------------------------------------------------------------- main
def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    print("=== MECH/display_biosafety_v2_check.py (ISS-208) ===")
    results = run_checks(ROOT)
    nbad = 0
    for cid, name, ok, detail in results:
        print("  [%s] %-30s %s" % (cid, name, "PASS" if ok else "FAIL"))
        print("        %s" % detail)
        if not ok:
            nbad += 1
    print("结论: %d/%d 项通过" % (len(results) - nbad, len(results)))
    if nbad:
        print("✗ 门禁不通过: %s" % ", ".join(c for c, _n, ok, _d in results if not ok))
        return 1
    print("✓ 门禁通过 (rc=0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
