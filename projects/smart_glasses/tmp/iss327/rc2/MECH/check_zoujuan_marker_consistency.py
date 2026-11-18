#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MECH/check_zoujuan_marker_consistency.py
================================================================================
ISS-238 新机器门禁: 「走鹃旧口径已收口」这句话的**机器背书**。

★为什么要有这个门禁 (背景)★:
  · `MECH/display_biosafety_v2_check.py` 的 [C1] 只认**单一字符串**
    `已作废 (2026-11-15, ISS-134 V2)` ⇒ **作废标注每多一种写法, 门禁就再打一次红**
    (ISS-222 形态已经打过一次: 2026-11-16 实跑 rc=1 · 活动口径 = 5 ⇒ 4 处假阳性 + 1 处真漏标)
  · ★**这个脚本不在 `state/daily_check.py` 链上** ⇒ 巡检看不见 ⇒ 「已收口」没有机器背书
  · ⇒ 本门禁**不依赖受保护脚本** (只**只读**它的 md5 与 MARKER 常量做交叉核对),
    自己把「活动口径 = 0」+「形态清单对得上」+「受保护文件没被动」三件事钉住。

判据 (rc=0 = 全过; 任一条不过 ⇒ rc=1 并**点名是哪一条**):
  [K1] 5 份旧文档里含「走鹃」的行必须**全部**带 canonical MARKER (活动口径 = 0) ⇒ 逐行点名
  [K2] canonical MARKER 串本身必须存在 (走鹃行上 / 提案文件里 / 与受保护脚本 MARKER 常量一致)
       —— 否则**门禁自己失效了都没人知道**
  [K3] `MECH/MECH_BUDGET.md` 里不许出现【**无标注的裸走鹃命中**】 (L880 这类 = 真漏标)
  [K4] 作废标注形态清单: **盘上实际形态集合 == 提案 §5 登记形态集合** (双向)
       + 提案清单 ⊆ 门禁白名单 (不许清单自我膨胀成「什么都认」)
  [K5] 受保护文件 md5 未变 (4 个)

用法:
  python3 MECH/check_zoujuan_marker_consistency.py            # 跑门禁
  python3 MECH/check_zoujuan_marker_consistency.py --selftest   # 跑自测 (8 条反向用例 + 1 基线)
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
# canonical 标注串: 与受保护脚本 MECH/display_biosafety_v2_check.py 的 MARKER 常量一致
CANON = "已作废 (2026-11-15, ISS-134 V2)"

# 5 份旧文档 (与 display_biosafety_v2_check.py 的 LEGACY_DOCS 同源)
LEGACY_DOCS = [
    "MECH/MECH_BUDGET.md",
    "MECH/PROTOTYPE_PLAN.md",
    "MECH/SOC_CARRIER_EVAL.md",
    "MECH/STRUCT_REVIEW_ISS065.md",
    "MECH/CLEARANCE_FIX.md",
]

STRUCT_TRUTH = "MECH/MECH_BUDGET.md"          # 结构侧真源 (K3 专查它)
PROPOSAL = "MECH/DISPLAY_BIOSAFETY_V2_MARKER_POLICY_PROPOSAL.md"   # 形态清单唯一登记处 (K4 比对对象)
GUARDED_SCRIPT = "MECH/display_biosafety_v2_check.py"              # 受保护脚本 (只读, 不改)

# 受保护文件 md5 (交卷前逐字节不变)
GUARDED = {
    "MECH/display_biosafety_v2_check.py": "29c77fc3fc823048b1d96c9500d28dd7",
    "MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md": "96239070dc7c0ec00edb1b758a698769",
    "MECH/JBD_ROLE_NARROWING.md": "bda4a29464336bc1452c913602ce3f46",
    "MECH/check_demo_struct_truth.py": "fa9b59e593a13408ad9505d986276f63",
}

# 作废标注形态登记表 (★门禁自己的白名单★) —— 与提案 §5 的登记块一一对应
#   F1 = canonical (ISS-134 V2) / F2·F3 = ISS-222 两种写法 / F4 = 裸「已作废」
KNOWN_PAREN = [
    ("F1", "已作废 (2026-11-15, ISS-134 V2)"),
    ("F2", "已作废 (ISS-222 · 2026-11-16, C-6 落地)"),
    ("F3", "已作废 (ISS-222 · C-6 落地)"),
]
BARE_ID, BARE = "F4", "已作废"
WHITELIST = set(s for _fid, s in KNOWN_PAREN) | {BARE}

# 提案 §5 登记块的一行: "F1 | 形态串 | 次数 | 说明"
FORM_LINE_RE = re.compile(r"^F(\d+)\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|", re.MULTILINE)

# 行内任一作废标注片段 (用于反向用例把标注整段抹掉)
MARKER_SEG_RE = re.compile(r"(?:\*\*)?已作废(?:\s*\([^)]*\))?(?:\*\*)?")
CANON_SEG_RE = re.compile(r"(?:\*\*)?" + re.escape(CANON) + r"(?:\*\*)?")


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


def classify_forms(text: str):
    """普查文本里「走鹃」行上的作废标注形态。

    返回 (counts, unknown):
      counts  = {形态串: 出现次数}
      unknown = [(行号, 片段)] —— 「已作废 (…」但括号内容不在白名单里 ⇒ **清单外的新形态**
    """
    counts = {}
    unknown = []
    for i, line in enumerate(text.split("\n"), 1):
        if "走鹃" not in line:
            continue
        for m in re.finditer("已作废", line):
            pos = m.start()
            hit = None
            for _fid, s in KNOWN_PAREN:
                if line.startswith(s, pos):
                    hit = s
                    break
            if hit is None:
                if line[pos + 3:].lstrip().startswith("("):
                    frag = line[pos:].split(")")[0] + ")"
                    unknown.append((i, frag))
                    continue
                hit = BARE
            counts[hit] = counts.get(hit, 0) + 1
    return counts, unknown


# ---------------------------------------------------------------- [K1] 走鹃行必须全部带 canonical
def check_k1(root: str):
    offenders = []
    total = 0
    marked = 0
    per = []
    for rel in LEGACY_DOCS:
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            return False, "文件缺失: %s" % rel
        act = hist = 0
        for i, line in enumerate(_read(root, rel).split("\n"), 1):
            if "走鹃" not in line:
                continue
            total += 1
            if CANON in line:
                hist += 1
                marked += 1
            else:
                act += 1
                offenders.append("%s:%d" % (rel, i))
        per.append("%s %d/%d" % (rel.split("/")[-1], act, hist))
    ok = not offenders
    detail = "走鹃命中 %d 行 ; 带 canonical %d 行 ; 活动口径 = %d (必须 0) ; 逐文件(活动/带标注): %s" % (
        total, marked, len(offenders), " · ".join(per))
    if offenders:
        detail += " ; 违规行: " + ", ".join(offenders[:12])
    return ok, detail


# ---------------------------------------------------------------- [K2] canonical 串本身必须在位
def check_k2(root: str):
    bad = []
    on_zj = 0
    for rel in LEGACY_DOCS:
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            bad.append("%s 缺失" % rel)
            continue
        for line in _read(root, rel).split("\n"):
            if "走鹃" in line and CANON in line:
                on_zj += 1
    if on_zj == 0:
        bad.append("5 份旧文档里没有任何一行带 canonical 标注 ⇒ 门禁自身已失效")
    pp = os.path.join(root, PROPOSAL)
    if not os.path.exists(pp):
        bad.append("提案文件缺失: %s" % PROPOSAL)
    elif CANON not in _read(root, PROPOSAL):
        bad.append("提案文件里查不到 canonical 标注串")
    gp = os.path.join(root, GUARDED_SCRIPT)
    if not os.path.exists(gp):
        bad.append("受保护脚本缺失: %s" % GUARDED_SCRIPT)
    else:
        m = re.search(r'MARKER\s*=\s*"([^"]*)"', _read(root, GUARDED_SCRIPT))
        if not m:
            bad.append("受保护脚本里找不到 MARKER 常量")
        elif m.group(1) != CANON:
            bad.append("受保护脚本 MARKER = %r ≠ %r" % (m.group(1), CANON))
    ok = not bad
    detail = ("canonical 标注串在位: 走鹃行 %d 处 + 提案文件 + 受保护脚本 MARKER 常量一致" % on_zj
              if ok else "canonical 标注串失效: " + " ; ".join(bad))
    return ok, detail


# ---------------------------------------------------------------- [K3] 结构侧真源不许有裸走鹃命中
def check_k3(root: str):
    p = os.path.join(root, STRUCT_TRUTH)
    if not os.path.exists(p):
        return False, "结构侧真源缺失: %s" % STRUCT_TRUTH
    offenders = []
    total = 0
    for i, line in enumerate(_read(root, STRUCT_TRUTH).split("\n"), 1):
        if "走鹃" not in line:
            continue
        total += 1
        if "已作废" not in line:
            offenders.append("%s:%d" % (STRUCT_TRUTH, i))
    ok = not offenders
    detail = "%s 走鹃命中 %d 行 ; 无标注裸命中 = %d (必须 0)" % (STRUCT_TRUTH, total, len(offenders))
    if offenders:
        detail += " ; 违规行: " + ", ".join(offenders[:12])
    return ok, detail


# ---------------------------------------------------------------- [K4] 形态清单 ↔ 盘面对得上
def _parse_proposal_forms(text: str):
    out = []
    for m in FORM_LINE_RE.finditer(text):
        out.append((m.group(1), m.group(2)))
    return out


def check_k4(root: str):
    pp = os.path.join(root, PROPOSAL)
    if not os.path.exists(pp):
        return False, "提案文件缺失: %s (形态清单没法比)" % PROPOSAL
    pforms = _parse_proposal_forms(_read(root, pp))
    if not pforms:
        return False, "提案文件里解析不到形态登记行 (格式: F1 | 形态串 | 次数 | 说明)"
    pset = set(s for _fid, s in pforms)
    bad = []
    disk = {}
    unknown = []
    for rel in LEGACY_DOCS:
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            bad.append("%s 缺失" % rel)
            continue
        counts, unk = classify_forms(_read(root, rel))
        for k, v in counts.items():
            disk[k] = disk.get(k, 0) + v
        for i, frag in unk:
            unknown.append("%s:%d (%s)" % (rel, i, frag))
    dset = set(disk.keys())
    if unknown:
        bad.append("盘上出现清单外的新形态 %d 处: %s" % (len(unknown), ", ".join(unknown[:5])))
    only_disk = dset - pset
    only_prop = pset - dset
    if only_disk:
        bad.append("盘上有、提案清单没登记的形态: " + " | ".join(sorted(only_disk)))
    if only_prop:
        bad.append("提案清单有、盘上不存在的形态: " + " | ".join(sorted(only_prop)))
    bogus = pset - WHITELIST
    if bogus:
        bad.append("提案清单里的形态不在门禁白名单内: " + " | ".join(sorted(bogus)))
    ok = not bad
    detail = ("作废标注形态 %d 种, 盘上出现次数 %s ; 与提案 §5 登记清单双向一致 (白名单 %d 种)"
              % (len(dset), "/".join("%s=%d" % (k, disk[k]) for k in sorted(disk)), len(WHITELIST))
              if ok else "形态清单对不上: " + " ; ".join(bad))
    return ok, detail


# ---------------------------------------------------------------- [K5] 受保护文件 md5 未变
def check_k5(root: str):
    bad = []
    for rel, want in sorted(GUARDED.items()):
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            bad.append("%s 缺失" % rel)
            continue
        got = _md5(p)
        if got != want:
            bad.append("%s md5 %s≠%s" % (rel, got, want))
    ok = not bad
    detail = ("受保护文件 md5 逐字节未变 (%d 个): %s"
              % (len(GUARDED), ", ".join("%s=%s…" % (r.split("/")[-1], v[:8]) for r, v in sorted(GUARDED.items())))
              if ok else "受保护文件被改: " + " ; ".join(bad))
    return ok, detail


CHECKS = [
    ("K1", "走鹃行必须全部带 canonical 标注 (活动口径 = 0)", check_k1),
    ("K2", "canonical 标注串自身在位 (门禁不许自我失效)", check_k2),
    ("K3", "结构侧真源不许有裸走鹃命中 (真漏标)", check_k3),
    ("K4", "作废标注形态清单 ↔ 盘面双向一致", check_k4),
    ("K5", "受保护文件 md5 未变", check_k5),
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


# ---------------------------------------------------------------- 自测 (反向用例)
FIXTURE_FILES = list(LEGACY_DOCS) + [PROPOSAL] + sorted(GUARDED.keys())


def _copy_fixture(tmp: str):
    for rel in FIXTURE_FILES:
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


def _patch_line(text: str, anchor: str, fn):
    """在含 anchor 的那一行上做替换; 返回 (新文本, 是否真改到了)"""
    ls = text.split("\n")
    hit = None
    for i, l in enumerate(ls):
        if anchor in l:
            hit = i
            break
    if hit is None:
        return text, False
    old = ls[hit]
    new = fn(old)
    ls[hit] = new
    return "\n".join(ls), (new != old)


def _strip_all_markers(line: str) -> str:
    return MARKER_SEG_RE.sub("", line)


def selftest() -> int:
    cases = []

    # ---- ST-0 基线: 未改 ⇒ 全过 ----
    with tempfile.TemporaryDirectory(prefix="zjmc_selftest_") as tmp:
        _copy_fixture(tmp)
        res = run_checks(tmp)
        failed = [r[0] for r in res if not r[2]]
        cases.append(("ST-0 基线 (未改) ⇒ 期望全过 rc=0",
                      not failed, failed, "基线全绿" if not failed else "基线就红"))

    # ---- RT-1 真漏标复现: 抹掉 L880 行的全部作废标注 ⇒ K1 + K3 必须红 ----
    with tempfile.TemporaryDirectory(prefix="zjmc_selftest_") as tmp:
        _copy_fixture(tmp)
        anchor = "为什么这不是「预扣」"
        landed = {}

        def _m(text):
            new, ok = _patch_line(text, anchor, _strip_all_markers)
            landed["ok"] = ok
            return new

        _mutate(tmp, STRUCT_TRUTH, _m)
        # ★自证: 抹完以后该行仍含「走鹃」但一个「已作废」都不剩 ⇒ 证明真的改到了目标
        tgt = [l for l in _read(tmp, STRUCT_TRUTH).split("\n") if anchor in l]
        selfproof = (bool(tgt) and "走鹃" in tgt[0] and "已作废" not in tgt[0])
        res = run_checks(tmp)
        failed = [r[0] for r in res if not r[2]]
        cases.append(("RT-1 抹掉 L880 全部作废标注 ⇒ 必须被 K1+K3 抓",
                      selfproof and "K1" in failed and "K3" in failed, failed,
                      "自证=%s" % ("过" if selfproof else "★没改到目标★")))

    # ---- RT-2 只抹 canonical (其它形态还在) ⇒ K1 红, K3 必须仍绿 (证明 K3 精度) ----
    with tempfile.TemporaryDirectory(prefix="zjmc_selftest_") as tmp:
        _copy_fixture(tmp)
        anchor = "现行光束口径 = **8.8849 mm**"
        landed = {}

        def _m(text):
            new, ok = _patch_line(text, anchor, lambda l: CANON_SEG_RE.sub("", l))
            landed["ok"] = ok
            return new

        _mutate(tmp, STRUCT_TRUTH, _m)
        tgt = [l for l in _read(tmp, STRUCT_TRUTH).split("\n") if anchor in l]
        selfproof = (bool(tgt) and CANON not in tgt[0] and "已作废 (ISS-222" in tgt[0])
        res = run_checks(tmp)
        failed = [r[0] for r in res if not r[2]]
        cases.append(("RT-2 抹掉某行 canonical (留 ISS-222 形态) ⇒ K1 红、K3 仍绿",
                      selfproof and "K1" in failed and "K3" not in failed, failed,
                      "自证=%s" % ("过" if selfproof else "★没改到目标★")))

    # ---- RT-3 把 5 份旧文档的 canonical 全洗掉 ⇒ K2 必须红 (门禁自身失效自检) ----
    with tempfile.TemporaryDirectory(prefix="zjmc_selftest_") as tmp:
        _copy_fixture(tmp)
        for rel in LEGACY_DOCS:
            _mutate(tmp, rel, lambda t: CANON_SEG_RE.sub("", t))
        left = 0
        for rel in LEGACY_DOCS:
            for l in _read(tmp, rel).split("\n"):
                if "走鹃" in l and CANON in l:
                    left += 1
        selfproof = (left == 0)
        res = run_checks(tmp)
        failed = [r[0] for r in res if not r[2]]
        cases.append(("RT-3 洗掉全部 canonical ⇒ K2 必须红 (门禁失效自检)",
                      selfproof and "K2" in failed, failed,
                      "自证=%s (残留 %d 处)" % ("过" if selfproof else "★没改到目标★", left)))

    # ---- RT-4a 篡改提案清单 (删掉一种形态) ⇒ K4 必须红 ----
    with tempfile.TemporaryDirectory(prefix="zjmc_selftest_") as tmp:
        _copy_fixture(tmp)

        def _m(text):
            ls = text.split("\n")
            keep = [l for l in ls if not re.match(r"^F2\s*\|", l)]
            return "\n".join(keep)

        _mutate(tmp, PROPOSAL, _m)
        after = _read(tmp, PROPOSAL)
        selfproof = ("F2 |" not in after) and ("F1 |" in after)
        res = run_checks(tmp)
        failed = [r[0] for r in res if not r[2]]
        cases.append(("RT-4a 提案清单删掉一种形态 ⇒ K4 必须红",
                      selfproof and "K4" in failed, failed,
                      "自证=%s" % ("过" if selfproof else "★没改到目标★")))

    # ---- RT-4b 篡改提案清单 (塞一种盘上不存在的假形态) ⇒ K4 必须红 ----
    with tempfile.TemporaryDirectory(prefix="zjmc_selftest_") as tmp:
        _copy_fixture(tmp)
        fake = "F9 | 已作废 (2020-01-01, FAKE-ISS) | 0 | 假形态 (自证用: 盘上不存在)"
        _mutate(tmp, PROPOSAL, lambda t: t + "\n" + fake + "\n")
        after = _read(tmp, PROPOSAL)
        selfproof = fake in after
        res = run_checks(tmp)
        failed = [r[0] for r in res if not r[2]]
        cases.append(("RT-4b 提案清单塞进盘上没有的假形态 ⇒ K4 必须红",
                      selfproof and "K4" in failed, failed,
                      "自证=%s" % ("过" if selfproof else "★没改到目标★")))

    # ---- RT-5 篡改判据文件一个字节 ⇒ K5 必须红 ----
    with tempfile.TemporaryDirectory(prefix="zjmc_selftest_") as tmp:
        _copy_fixture(tmp)
        rel = "MECH/DISPLAY_BIOSAFETY_CRITERIA_V2.md"
        before = _md5(os.path.join(tmp, rel))
        _mutate(tmp, rel, lambda t: t + "\n<!-- touched by ISS-238 selftest -->\n")
        after = _md5(os.path.join(tmp, rel))
        selfproof = (before != after)
        res = run_checks(tmp)
        failed = [r[0] for r in res if not r[2]]
        cases.append(("RT-5 篡改判据文件一个字节 ⇒ K5 必须红",
                      selfproof and "K5" in failed, failed,
                      "自证=%s" % ("过" if selfproof else "★没改到目标★")))

    # ---- RT-6 塞一条裸走鹃命中 (一个标注都不带) ⇒ K1 + K3 必须红 (底线) ----
    with tempfile.TemporaryDirectory(prefix="zjmc_selftest_") as tmp:
        _copy_fixture(tmp)
        bare = "| 走鹃Ⅱ 光机 仍在本方案内 | 是 | 是 |"
        _mutate(tmp, STRUCT_TRUTH, lambda t: t + "\n" + bare + "\n")
        after = _read(tmp, STRUCT_TRUTH)
        selfproof = (bare in after) and ("已作废" not in bare)
        res = run_checks(tmp)
        failed = [r[0] for r in res if not r[2]]
        cases.append(("RT-6 塞一条无标注裸走鹃命中 ⇒ K1+K3 必须红 (底线)",
                      selfproof and "K1" in failed and "K3" in failed, failed,
                      "自证=%s" % ("过" if selfproof else "★没改到目标★")))

    # ---- RT-7 把某行 canonical 换成 ISS-222 形态 ⇒ 当前口径 (P3) 下 K1 必须红 ----
    with tempfile.TemporaryDirectory(prefix="zjmc_selftest_") as tmp:
        _copy_fixture(tmp)
        anchor = "现行光束口径 = **8.8849 mm**"
        _mutate(tmp, STRUCT_TRUTH,
                lambda t: _patch_line(t, anchor, lambda l: l.replace(CANON, "已作废 (ISS-222 · 2026-11-16, C-6 落地)"))[0])
        tgt = [l for l in _read(tmp, STRUCT_TRUTH).split("\n") if anchor in l]
        selfproof = (bool(tgt) and CANON not in tgt[0] and "已作废 (ISS-222 · 2026-11-16, C-6 落地)" in tgt[0])
        res = run_checks(tmp)
        failed = [r[0] for r in res if not r[2]]
        cases.append(("RT-7 canonical 换成 ISS-222 形态 ⇒ 当前口径下 K1 必须红",
                      selfproof and "K1" in failed, failed,
                      "自证=%s" % ("过" if selfproof else "★没改到目标★")))

    print("=== MECH/check_zoujuan_marker_consistency.py --selftest (ISS-238) ===")
    bad = 0
    for name, ok, failed, note in cases:
        print("  %-6s %-48s %s" % (name.split(" ")[0], name.split(" ", 1)[1],
                                   "PASS" if ok else "FAIL (抓到: %s / %s)" % (failed, note)))
        if not ok:
            bad += 1
    print("自测: %d/%d 用例通过" % (len(cases) - bad, len(cases)))
    return 0 if bad == 0 else 1


# ---------------------------------------------------------------- main
def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    print("=== MECH/check_zoujuan_marker_consistency.py (ISS-238) ===")
    results = run_checks(ROOT)
    nbad = 0
    for cid, name, ok, detail in results:
        print("  [%s] %-34s %s" % (cid, name, "PASS" if ok else "FAIL"))
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
