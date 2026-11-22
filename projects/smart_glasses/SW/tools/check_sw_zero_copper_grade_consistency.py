#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_sw_zero_copper_grade_consistency.py
==========================================================================
★★【SW 侧「零铜单端网分级」与「板侧真值」不许再分叉闸】★★
  ★ISS-344 · sw-lead · 2026-11-23 · ★零写板 · 零落表 · 零改固件本体 · 零改板侧判据 ★

★★**这把闸是干什么的 (★一句话★)** ★★
  ★**ISS-344 的病根**: `SW/ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md` 的 §3 表
  把 6 条网判成「NC (不连)」, 而 main 2026-11-22 20:5x 已逐条改判【必需】⇒
  ★**这 6 条会带着「板侧不许标 NC」的矛盾进板那一趟** ★
  ⇒ ★**本闸把「板侧真值」钉成唯一尺子, 让 SW 页一旦再写出与它冲突的分级就立刻判红并点名** ★

★★**真值源 (★只读·一个字都不许动★)** ★★
  ★**`HW/check_s8_target_list.py`** 的 `REQUIRED_SINGLE` / `FLOAT_OK` / `EXPECT_*`
  ⇒ ★**板那一趟的唯一机器判据** ⇒ ★**本闸用 AST 静态解析它 (不执行它的代码)★** ★

★★**方向纪律 (★本项目铁律★)** ★★
  ★**只许【加严】不许【放宽】** ★ ⇒ ★**本闸绝不写 `HW/check_s8_target_list.py`**
  ⇒ ★**它只读它** ★

★★**判据 (★逐条可单测★)** ★★
  C0  ★**跨节一致**: §3/§3-1 表里的「建议的板侧标记」必须与 §7 订正表的「新说法」判出同一档
  C1  ★**凡判 NC 的网, 必须在 `FLOAT_OK` 里** ⇒ 否则判红并点名
  C2  ★**凡在 `REQUIRED_SINGLE` 里的网, 判 NC 就判红并点名** ★
  C3  ★**`REQUIRED_SINGLE` 的每一条都必须在 SW 页里被判成【必需】** (漏判/降级都红)
  C4  ★**`FLOAT_OK` 的网不得被 SW 页判成【必需】** (防止把可悬空误升成必需)
  C5  ★**`REQUIRED_SINGLE` 的网, 其「固件侧要改哪一行」清单必须标「作废」** (不留降级声明尾巴)
  C6  ★**待定档必须为空** (终裁: 待定 0 条) ⇒ SW 页出现「待定」就红
  C7  ★**板侧名单 (REQUIRED_SINGLE ∪ FLOAT_OK) 之外的网, 不许被 SW 页判成 NC 或必需** ⇒ 红
  C8  ★**标记类别认不出来** ⇒ 红 (不许糊过去)

★★**分类器怎么读「建议的板侧标记」那一格 (★顺序敏感·写死·可复现★)** ★★
  ① 含「不许标 NC / 不许标 no-connect」 ⇒ 【必需】
  ② 含「板那一趟 / 现在只定口径 / 不落 NC / 条件」 ⇒ 【可悬空·条件式】 (★**FSIN_OUT 走这条★)
  ③ 含「NC (不连) / no-connect / 标 NC」 ⇒ 【断言 NC】
  ④ 含「必需 / 必须救回 / 布铜」 ⇒ 【必需】
  ⑤ 含「可悬空」 ⇒ 【可悬空】
  ⑥ 含「待定 / TBD」 ⇒ 【待定】
  ⑦ 其它 ⇒ 【认不出】 ⇒ 红
  ★**先剥掉「」『』引号段与 `反引号` 段再判** ⇒ ★**旧说法的字串不会污染判定** ★

★★**用法** ★★
    python3 SW/tools/check_sw_zero_copper_grade_consistency.py
    python3 SW/tools/check_sw_zero_copper_grade_consistency.py --doc <另一份副本> --json
  ★**rc = 0 全绿 / 1 判红 / 2 用法错** ★
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))

TRUTH_SRC = os.path.join(PROJ, "HW", "check_s8_target_list.py")
DOC_REL = os.path.join("SW", "ONETRIP_ZERO_COPPER_SINGLE_END_FW_USAGE.md")

# ★★标记类别 ★★
REQUIRED = "REQUIRED"       # 必需 (进 S8 布线目标 · 板侧不许标 NC)
FLOAT = "FLOAT"             # 可悬空 (含条件式)
NC = "NC"                   # 断言 NC (板侧现在就标不连)
TBD = "TBD"                 # 待定
UNKNOWN = "UNKNOWN"         # 认不出

# ★★订正小节的哨兵 (★本单加进 SW 页的追加式订正块★) ★★
CORR_TABLE_KEY = "新说法"


# ═══════════════════════════════════════════════════════════════════════
# 板侧真值 (★AST 静态解析·不执行被读脚本的任何代码★)
# ═══════════════════════════════════════════════════════════════════════
def load_truth(path: str) -> dict:
    if not os.path.isfile(path):
        raise SystemExit("❌ 板侧判据脚本不存在: %s" % path)
    with open(path, encoding="utf-8", errors="ignore") as f:
        src = f.read()
    tree = ast.parse(src, filename=path)
    want = ("REQUIRED_SINGLE", "FLOAT_OK",
            "EXPECT_REQUIRED", "EXPECT_FLOAT", "EXPECT_TBD")
    out = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id in want and t.id not in out:
                try:
                    out[t.id] = ast.literal_eval(node.value)
                except Exception:
                    pass
    missing = [k for k in want if k not in out]
    if missing:
        raise SystemExit("❌ 板侧判据里读不到这些名字: %s" % missing)
    return out


# ═══════════════════════════════════════════════════════════════════════
# Markdown 表解析 (★按未转义的 | 切·处理 \\| ★)
# ═══════════════════════════════════════════════════════════════════════
def split_row(line: str):
    s = line.strip()
    if not s.startswith("|"):
        return None
    s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def norm_head(c: str) -> str:
    c = c.replace("★", "")
    c = c.replace("**", "")
    c = c.replace("`", "")
    return re.sub(r"\s+", "", c)


def find_tables(lines):
    """→ [{'start':行号(1基), 'end':行号, 'header':[...], 'rows':[(行号, cells)]}]"""
    out = []
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].strip().startswith("|"):
            j = i
            while j < n and lines[j].strip().startswith("|"):
                j += 1
            hdr = split_row(lines[i]) or []
            rows = []
            for k in range(i + 1, j):
                cells = split_row(lines[k])
                if cells is None:
                    continue
                if all(set(c) <= set("-: ") for c in cells):
                    continue          # ★分隔行★·
                rows.append((k + 1, cells))
            out.append({"start": i + 1, "end": j,
                        "header": [norm_head(c) for c in hdr], "rows": rows})
            i = j
        else:
            i += 1
    return out


def net_of(cell: str):
    m = re.search(r"`([^`]+)`", cell)
    if m:
        return m.group(1).strip()
    m = re.search(r"\b([A-Z][A-Z0-9_]{2,})\b", cell)
    return m.group(1) if m else None


# ═══════════════════════════════════════════════════════════════════════
# 标记分类 (★顺序敏感·写死·可复现★)
# ═══════════════════════════════════════════════════════════════════════
def strip_noise(t: str) -> str:
    t = re.sub(r"[「『][^」』]*[」』]", "", t)     # ★去掉被引号包住的旧说法★
    t = re.sub(r"`[^`]*`", "", t)                 # ★去掉代码片段★
    return t


def classify_mark(t: str) -> str:
    s = strip_noise(t or "")
    if re.search(r"不许标\s*(NC|no-?connect)", s, re.I):
        return REQUIRED
    if re.search(r"(板那一趟|现在只定口径|不落\s*NC|条件)", s):
        return FLOAT
    if re.search(r"(NC\s*\(不连\)|no-?connect|标\s*NC)", s, re.I):
        return NC
    if re.search(r"(必需|必须救回|布铜)", s):
        return REQUIRED
    if re.search(r"(可悬空|浮空)", s):
        return FLOAT
    if re.search(r"(待定|TBD)", s, re.I):
        return TBD
    return UNKNOWN


def family(cat: str) -> str:
    """归并档位 (★跨节一致比对用★)"""
    if cat in (REQUIRED,):
        return REQUIRED
    if cat in (FLOAT,):
        return FLOAT
    if cat in (NC,):
        return NC
    if cat in (TBD,):
        return TBD
    return UNKNOWN


# ═══════════════════════════════════════════════════════════════════════
# 文档解析
# ═══════════════════════════════════════════════════════════════════════
def parse_doc(path: str) -> dict:
    with open(path, encoding="utf-8", errors="ignore") as f:
        text = f.read()
    lines = text.split("\n")
    tables = find_tables(lines)

    marks = {}        # net -> {"mark": str, "fw": str, "line": int, "tbl": "3"/"3-1"}
    corrs = {}        # net -> {"corr": str, "fw": str, "line": int}
    seen_grades = {}  # §2 表的「分级」列
    sec2_grade_col = None

    for t in tables:
        h = t["header"]
        joined = "|".join(h)
        is_main = ("建议的板侧标记" in joined) or ("建议板侧标记" in joined)
        is_corr = (CORR_TABLE_KEY in joined) and ("旧说法" in joined)
        is_sec2 = ("分级" in h) and ("引用形态" in joined) and ("证据" in joined)

        if is_main:
            # §3 (4 列) 与 §3-1 (4 列) 结构一致 ⇒ 最后一列 = 建议的板侧标记
            # ★★ 只有 §3 表有「悬空后固件侧要不要改」这一列 ⇒ §3-1 表没有 ⇒ C5 不适用 ★★
            has_fw = ("悬空后固件侧要不要改" in joined)
            for ln, cells in t["rows"]:
                if not cells:
                    continue
                net = net_of(cells[0])
                if not net:
                    continue
                mark = cells[-1]
                fw = cells[2] if len(cells) >= 4 else ""
                if net in marks:
                    continue
                marks[net] = {"mark": mark, "fw": fw, "line": ln,
                              "has_fw": has_fw}
        elif is_corr:
            for ln, cells in t["rows"]:
                if not cells:
                    continue
                net = net_of(cells[0])
                if not net:
                    continue
                corr = cells[2] if len(cells) >= 3 else ""
                fw = cells[-1] if len(cells) >= 4 else ""
                if net in corrs:
                    continue
                corrs[net] = {"corr": corr, "fw": fw, "line": ln}
        elif is_sec2:
            try:
                sec2_grade_col = h.index("分级")
            except ValueError:
                sec2_grade_col = None
            for ln, cells in t["rows"]:
                if sec2_grade_col is None or len(cells) <= sec2_grade_col:
                    continue
                net = net_of(cells[0])
                if not net:
                    continue
                seen_grades[net] = {"grade": cells[sec2_grade_col], "line": ln}

    return {"text": text, "lines": lines, "marks": marks,
            "corrs": corrs, "sec2": seen_grades}


# ═══════════════════════════════════════════════════════════════════════
# 主判定
# ═══════════════════════════════════════════════════════════════════════
def run(doc_path: str) -> dict:
    truth = load_truth(TRUTH_SRC)
    req = list(truth["REQUIRED_SINGLE"])
    flt = list(truth["FLOAT_OK"])
    known = set(req) | set(flt)

    doc = parse_doc(doc_path)
    marks = doc["marks"]
    corrs = doc["corrs"]
    sec2 = doc["sec2"]

    violations = []      # [{code, net, msg}]
    checks = []          # [(code, desc, ok, detail)]

    def viol(code, net, msg):
        violations.append({"code": code, "net": net, "msg": msg})

    # ── 覆盖度: 板侧名单里的每一条都要在 SW 页里有分级 ──
    missing_req = [n for n in req if n not in marks]
    missing_flt = [n for n in flt if n not in marks]
    for n in missing_req:
        viol("C3", n, "板侧必需名单里的 %s 在 SW 页 §3/§3-1 表里根本没有出现 (漏判)" % n)
    for n in missing_flt:
        viol("C4", n, "板侧可悬空名单里的 %s 在 SW 页 §3/§3-1 表里根本没有出现 (漏判)" % n)
    checks.append(("C3", "REQUIRED_SINGLE 每条都在 SW 页且被判【必需】",
                   not missing_req and all(
                       family(classify_mark(marks[n]["mark"])) == REQUIRED
                       for n in req if n in marks),
                   "缺 %d 条 · 非必需 %d 条" % (
                       len(missing_req),
                       sum(1 for n in req if n in marks
                           and family(classify_mark(marks[n]["mark"])) != REQUIRED))))

    # ── C2 / C1 / C3 分级本体 ──
    nc_nets, req_nets = [], []
    for net, info in sorted(marks.items()):
        cat = classify_mark(info["mark"])
        fam = family(cat)
        if fam == NC:
            nc_nets.append(net)
            if net not in flt:
                viol("C1", net, "%s 判了「NC (不连)」但不在板侧可悬空名单 FLOAT_OK 里" % net)
            if net in req:
                viol("C2", net, "%s 在板侧【必需】名单 REQUIRED_SINGLE 里, 却被 SW 页判成 NC" % net)
        if net in req and fam != REQUIRED:
            req_nets.append(net)
            viol("C3", net, "%s 在板侧【必需】名单里, 但 SW 页把它判成 %s" % (net, cat))
        if net in flt and fam == REQUIRED:
            viol("C4", net, "%s 在板侧【可悬空】名单里, 但 SW 页把它判成【必需】" % net)
        if net not in known and fam in (NC, REQUIRED):
            viol("C7", net, "%s 不在板侧名单 (REQUIRED_SINGLE ∪ FLOAT_OK) 里, 却被 SW 页判成 %s"
                 % (net, cat))
        if fam == TBD:
            viol("C6", net, "%s 在 SW 页仍是【待定】⇒ 终裁口径是待定 0 条" % net)
        if fam == UNKNOWN:
            viol("C8", net, "%s 的「建议的板侧标记」这一格认不出类别 (原文: %s)"
                 % (net, info["mark"][:80]))

    checks.append(("C1", "凡判 NC 的网必须在 FLOAT_OK 里",
                   not [v for v in violations if v["code"] == "C1"],
                   "断言 NC 的网 = %s" % (", ".join(nc_nets) if nc_nets else "(无)")))
    checks.append(("C2", "凡在 REQUIRED_SINGLE 里的网判 NC 就判红并点名",
                   not [v for v in violations if v["code"] == "C2"],
                   "被判 NC 的必需网 = %s" % (
                       ", ".join(v["net"] for v in violations if v["code"] == "C2") or "(无)")))

    # ── C0 跨节一致 (SW §3/§3-1 的标记 vs §7 订正表的「新说法」) ──
    for net in sorted(set(marks) & set(corrs)):
        a = family(classify_mark(marks[net]["mark"]))
        b = family(classify_mark(corrs[net]["corr"]))
        if a != b:
            viol("C0", net, "%s 的 §3 标记判成 %s, 但 §7 订正表判成 %s ⇒ 两处分叉"
                 % (net, a, b))
    checks.append(("C0", "§3/§3-1 标记与 §7 订正表「新说法」同档",
                   not [v for v in violations if v["code"] == "C0"],
                   "比对 %d 条" % len(set(marks) & set(corrs))))

    # ── C5 必需网的固件侧「要改哪一行」清单必须标作废 ──
    for net in req:
        if net not in marks:
            continue
        if not marks[net].get("has_fw"):
            continue        # ★§3-1 表没有「固件侧要不要改」这一列 ⇒ C5 不适用★
        fw = marks[net].get("fw") or ""
        if "作废" not in fw:
            viol("C5", net, "%s 已改判【必需】, 但 §3 表「固件侧要不要改」这一列还没标「作废」"
                 % net)
    checks.append(("C5", "必需网的固件侧改动清单已标「作废」",
                   not [v for v in violations if v["code"] == "C5"],
                   "未标作废 = %d 条" % len([v for v in violations if v["code"] == "C5"])))

    # ── 附带: §2 表「分级」列与 §3 标记同档 (加分项·缺 §2 表时跳过) ──
    for net, g in sorted(sec2.items()):
        if net not in marks:
            continue
        a = family(classify_mark(g["grade"]))
        b = family(classify_mark(marks[net]["mark"]))
        # ★§2 的「分级」列写的是 必需/可悬空候选/待定; §3 的标记写的是 板侧动作 ⇒
        #   「可悬空候选」与「可悬空 (条件)」同档 ⇒ FLOAT
        if a != b and not (a == FLOAT and b == FLOAT):
            viol("C9", net, "§2 表「分级」列 (%s · 行 %d) 与 §3 标记 (%s) 不同档"
                 % (net, g["line"], a))
    checks.append(("C9", "§2 表「分级」列与 §3 标记同档 (加分项)",
                   not [v for v in violations if v["code"] == "C9"],
                   "比对 %d 条" % len(sec2)))

    return {
        "doc": doc_path,
        "truth_src": TRUTH_SRC,
        "required_single": req,
        "float_ok": flt,
        "expect": {"required": truth["EXPECT_REQUIRED"],
                   "float": truth["EXPECT_FLOAT"],
                   "tbd": truth["EXPECT_TBD"]},
        "marks": {k: {"line": v["line"], "cat": classify_mark(v["mark"]),
                      "fam": family(classify_mark(v["mark"]))}
                  for k, v in sorted(marks.items())},
        "corrs": {k: {"line": v["line"], "cat": classify_mark(v["corr"]),
                      "fam": family(classify_mark(v["corr"]))}
                  for k, v in sorted(corrs.items())},
        "checks": [{"code": c, "desc": d, "ok": bool(o), "detail": det}
                   for c, d, o, det in checks],
        "violations": violations,
        "rc": 1 if violations else 0,
    }


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", default=os.path.join(PROJ, DOC_REL),
                    help="★被检的 SW 页 (★默认真件; 反向用例请指向 tmp/ 副本★)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    if not os.path.isfile(a.doc):
        print("❌ 被检文件不存在: %s" % a.doc)
        return 2

    r = run(a.doc)

    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return r["rc"]

    print("═══ SW 侧零铜网分级 ↔ 板侧真值 一致性闸 (★ISS-344·sw-lead·零写板★) ═══")
    print("  被检文档 : %s" % a.doc)
    print("  真值源   : %s (★只读·AST 静态解析·未执行其代码★)" % TRUTH_SRC)
    print("  板侧真值 : REQUIRED_SINGLE(%d) = %s" % (len(r["required_single"]),
          ", ".join(r["required_single"])))
    print("             FLOAT_OK(%d) = %s" % (len(r["float_ok"]), ", ".join(r["float_ok"])))
    print("             EXPECT_* = 必需 %d / 可悬空 %d / 待定 %d"
          % (r["expect"]["required"], r["expect"]["float"], r["expect"]["tbd"]))

    print("\n── SW 页 §3/§3-1 表读出的「建议的板侧标记」 ──")
    if r["marks"]:
        for n, v in r["marks"].items():
            print("  %-18s 行 %-5s ⇒ %-9s %s" % (n, v["line"], v["cat"], v["fam"]))
    else:
        print("  (没读到 §3/§3-1 表的行)")

    if r["corrs"]:
        print("\n── SW 页订正表的「新说法」 ──")
        for n, v in r["corrs"].items():
            print("  %-18s 行 %-5s ⇒ %-9s %s" % (n, v["line"], v["cat"], v["fam"]))

    print("\n── 判据逐条 ──")
    for c in r["checks"]:
        print("  %s %-46s %s" % (c["code"], c["desc"], "✔ 通过" if c["ok"] else "✘ 判红"))
        if c["detail"]:
            print("       └─ %s" % c["detail"])

    if r["violations"]:
        print("\n── ★★判红明细 (★逐条点名★) ──")
        for v in r["violations"]:
            print("  ✘ [%s] %s" % (v["code"], v["msg"]))
        print("\n★★结论: ★**判红 %d 条** ★ ⇒ SW 侧分级与板侧真值【分叉】了 ★" % len(r["violations"]))
    else:
        print("\n★★结论: ★**全绿** ★ ⇒ SW 侧分级与板侧真值【一致】★")

    return r["rc"]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
