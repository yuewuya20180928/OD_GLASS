#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss326_scan_mech_refs.py —— ISS-326 · MECH 侧「位号硬编码」全量机器扫描
=================================================================================
★**只读脚本** (★本脚本只写 logs/iss326/ 与 tmp/iss326/·项目真文件一个字节都不写★)

输入 (只读):
  · HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md   (§1-2 表 = 218 行改名对照·★口径单源★)
输出 (只写 logs/iss326/):
  · mech_ref_universe.json      (218 条 old→new map + 计数自证)
  · mech_ref_hits.tsv           (★全量命中逐条·机器扫·不许手抄★)
  · scan_raw.txt                (原始输出)

★扫描面 = MECH/**/*.py (递归) + MECH/**/*.md (递归)  ★不许只扫顶层★
★口径单源 = state/gen_kicad_sch.py::kicad_ref() (ISS-205 规则·与 ISS-317/ISS-321 同源)★
"""
from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))            # logs/iss326/
PROJ = os.path.dirname(os.path.dirname(HERE))                # 项目根
RENAME_MD = os.path.join(PROJ, "HW", "PCB", "ONETRIP_S1_THREE_SIDE_RENAME_LIST.md")
MECH = os.path.join(PROJ, "MECH")

OUT_JSON = os.path.join(HERE, "mech_ref_universe.json")
OUT_TSV = os.path.join(HERE, "mech_ref_hits.tsv")
OUT_RAW = os.path.join(HERE, "scan_raw.txt")


# =================================================================================================
# §口径单源 · kicad_ref (与 state/gen_kicad_sch.py 同源·逐字复刻)
# =================================================================================================
def kicad_ref(ref: str) -> str:
    r = (ref or "").strip()
    if r and r[-1].isdigit():
        return r
    return r + "_1"


# =================================================================================================
# §1 · 解析 §1-2 改名对照表 (218 行)
# =================================================================================================
def parse_rename_table(path: str):
    txt = open(path, encoding="utf-8").read()
    lines = txt.splitlines()
    rows = []
    for ln in lines:
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 8:
            continue
        num = cells[0]
        if not re.fullmatch(r"\d{1,3}", num):
            continue
        idx = int(num)
        if not (1 <= idx <= 218):
            continue
        old = cells[1]
        old_board = cells[2]
        old_sch = cells[3]
        new = cells[4]
        board = cells[6]
        move = cells[7]
        rows.append({
            "idx": idx, "old": old, "old_board": old_board, "old_sch": old_sch,
            "new": new, "board": board, "move": move,
        })
    rows.sort(key=lambda r: r["idx"])
    return rows


def build_universe(rows):
    uni = {}
    for r in rows:
        assert r["old"] not in uni, "重复 ref: %s" % r["old"]
        uni[r["old"]] = r
    # 自证: 218 行 / 改名 186 / 不动 32 / kicad_ref 口径逐条相符
    n_move = sum(1 for r in uni.values() if r["move"] == "改名")
    n_keep = sum(1 for r in uni.values() if r["move"] == "不动")
    bad = [(o, r["new"], kicad_ref(o)) for o, r in uni.items() if r["new"] != kicad_ref(o)]
    assert len(uni) == 218, "universe 不是 218: %d" % len(uni)
    assert n_move == 186, "改名不是 186: %d" % n_move
    assert n_keep == 32, "不动不是 32: %d" % n_keep
    assert not bad, "kicad_ref 口径不符: %r" % bad[:5]
    # 改名后撞名自证
    news = [r["new"] for r in uni.values()]
    assert len(set(news)) == len(news), "改名后撞名"
    return uni, n_move, n_keep


# =================================================================================================
# §2 · 文件分类 (★判据脚本 / 工具脚本 / 历史脚本 / 归档 / 文档★)
# =================================================================================================
# ★**历史落地脚本前缀** (★跑完就没了 ⇒ 硬编 ref 【不需要改】⇒ 列出来但标「历史脚本 · 不改」★)
HIST_PREFIXES = ("_apply_", "_frag_update_", "_frag_rebase_", "rebase_", "_close_",
                  "_handoff_", "_append_", "_frag_", "iss317_", "iss321_")
# ★**判据脚本 (★挂进 state/gate_check.py 的或被别闸调用的★)** ★
GATE_NAMES = {
    "check_board_frame_coords.py", "check_onepass_mech_sync.py",
    "check_onepass_struct_crosscheck.py", "check_demo_struct_truth.py",
    "board_port_opening_s6_check.py", "jd_y0_feasibility.py",
    "service_port_check.py", "check_onepass_mech_release.py",
    "board_frame_feasibility.py", "check_mech_verdict_freshness.py",
    "check_budget_caliber.py", "check_hinge_fpc_truth.py",
    "check_zoujuan_marker_consistency.py", "cross_review_check.py",
    "dfm_check.py", "display_biosafety_v2_check.py", "fit_check.py",
    "fit_check_v3_30mm.py", "hw_cross_review_check.py", "iss047_doc_check.py",
    "iss065_check.py", "iss127_h_chain_check.py", "pinset2_mech_check.py",
    "prototype_plan_check.py", "reliability_plan_check.py",
    "skeleton_section_check.py", "verify_budget.py", "board_width_15mm_check.py",
    "camera_window_check.py", "cavity_recalc_check.py", "carrier_eval.py",
    "hinge_power_calc.py", "hinge_usb_check.py",
}


def classify_file(rel: str):
    base = os.path.basename(rel)
    stem = base
    if stem.endswith(".py"):
        stem = stem[:-3]
    elif stem.endswith(".md"):
        stem = stem[:-3]
    # ★**文档 (md) ★**
    if base.endswith(".md"):
        return "文档", "★MECH 侧文档正文 · 非判据代码★"
    # ★**归档 (bak / 备份)★**
    if ".bak" in base or base.startswith("."):
        return "归档/备份", "★备份文件 · 不参与门禁 · 不用改★"
    # ★**历史落地脚本★**
    for p in HIST_PREFIXES:
        if stem.startswith(p):
            return "历史脚本", "★历史落地脚本 · 跑完就没了 · 【不需要改】★"
    # ★**判据/工具脚本★**
    if base in GATE_NAMES:
        return "判据脚本", "★判据脚本 · 门禁链成员或被门禁调用★"
    if base.startswith("check_") or base.endswith("_check.py"):
        return "判据脚本", "★判据脚本 (命名口径)★"
    if base.startswith("gen_") or base.startswith("print_") or base.startswith("verify_"):
        return "工具脚本", "★工具脚本 (生成/验证)· 不在门禁链★"
    return "其他脚本", "★未归类脚本★"


# =================================================================================================
# §3 · 注释判定 (★py 注释 vs 代码★)
# =================================================================================================
def strip_py_comment(line: str) -> str:
    """★保守判定: 一行是不是纯注释 (★引号内的 # 不算·用简单引号扫描器★)★"""
    in_s = None
    i = 0
    while i < len(line):
        ch = line[i]
        if in_s:
            if ch == "\\":
                i += 2
                continue
            if ch == in_s:
                in_s = None
        else:
            if ch in ("'", '"'):
                in_s = ch
            elif ch == "#":
                return line[:i]
        i += 1
    return line


def is_py_comment_only(line: str) -> bool:
    code = strip_py_comment(line)
    return code.strip() == "" and line.strip() != ""


# =================================================================================================
# §4 · 全量扫描
# =================================================================================================
def scan(uni):
    # ★**长 ref 优先 (避免 R_SEL_D0_N 抢在 R_SEL_D0_N_1 前面这种边界问题)★**
    refs = sorted(uni.keys(), key=len, reverse=True)
    pats = {r: re.compile(r"(?<![A-Za-z0-9_])" + re.escape(r) + r"(?![A-Za-z0-9_])") for r in refs}

    files = []
    for dirpath, dirnames, filenames in os.walk(MECH):
        dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
        for fn in sorted(filenames):
            if fn.endswith(".py") or fn.endswith(".md"):
                files.append(os.path.join(dirpath, fn))
    files.sort()

    hits = []
    per_file = {}
    per_ext = {}
    for path in files:
        rel = os.path.relpath(path, PROJ)
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                lines = fh.read().splitlines()
        except OSError as exc:
            raise SystemExit("读不了 %s: %s" % (rel, exc))
        fcls, fnote = classify_file(rel)
        n_here = 0
        for lineno, line in enumerate(lines, 1):
            for ref in refs:
                for m in pats[ref].finditer(line):
                    new = uni[ref]["new"]
                    move = uni[ref]["move"]
                    if path.endswith(".py"):
                        kind = "py-注释" if is_py_comment_only(line) else "py-代码"
                    else:
                        kind = "md-正文"
                    hits.append({
                        "rel": rel, "line": lineno, "ref": ref, "new": new,
                        "move": move, "kind": kind, "file_class": fcls,
                        "ctx": line.rstrip()[:400],
                        "col": m.start(),
                    })
                    n_here += 1
        per_file[rel] = {"file_class": fcls, "note": fnote, "hits": n_here,
                         "lines": len(lines)}
        per_ext[os.path.splitext(rel)[1]] = per_ext.get(os.path.splitext(rel)[1], 0) + n_here
    return hits, per_file, per_ext, files


def main():
    out = []
    def L(s=""):
        out.append(str(s))
        print(s)

    rows = parse_rename_table(RENAME_MD)
    uni, n_move, n_keep = build_universe(rows)
    L("=" * 78)
    L("ISS-326 · MECH 侧位号硬编码全量扫描 (★机器扫·非手抄★)")
    L("=" * 78)
    L("口径单源      : HW/PCB/ONETRIP_S1_THREE_SIDE_RENAME_LIST.md §1-2 (218 行表)")
    L("口径复刻      : state/gen_kicad_sch.py::kicad_ref() (末字符是数字⇒不动·否则⇒加 _1)")
    L("改名宇宙      : %d" % len(uni))
    L("  要改        : %d" % n_move)
    L("  不动        : %d" % n_keep)
    L("kicad_ref 口径逐条相符 : True (自证通过)")
    L("改名后撞名             : 无 (自证通过)")

    hits, per_file, per_ext, files = scan(uni)

    L("")
    L("── 扫描面 (递归 · 不许只扫顶层) ──")
    n_py = sum(1 for f in files if f.endswith(".py"))
    n_md = sum(1 for f in files if f.endswith(".md"))
    top_py = sum(1 for f in files if f.endswith(".py") and os.path.dirname(f) == MECH)
    top_md = sum(1 for f in files if f.endswith(".md") and os.path.dirname(f) == MECH)
    L("  MECH/**/*.py 递归 : %d 个文件 (顶层 %d + 子目录 %d)" % (n_py, top_py, n_py - top_py))
    L("  MECH/**/*.md 递归 : %d 个文件 (顶层 %d + 子目录 %d)" % (n_md, top_md, n_md - top_md))
    L("  子目录命中        : %s" % ", ".join(sorted(
        os.path.dirname(os.path.relpath(f, PROJ)) for f in files
        if os.path.dirname(f) != MECH)))
    L("")
    L("── 命中统计 (全量 · 精确字面量 + 词边界) ──")
    L("  总命中数          : %d" % len(hits))
    L("  按扩展名          : %s" % per_ext)
    L("  按文件类别        :")
    by_cls = {}
    for h in hits:
        by_cls[h["file_class"]] = by_cls.get(h["file_class"], 0) + 1
    for k in sorted(by_cls):
        L("      %-14s %d" % (k, by_cls[k]))
    L("  按命中性质        :")
    by_kind = {}
    for h in hits:
        by_kind[h["kind"]] = by_kind.get(h["kind"], 0) + 1
    for k in sorted(by_kind):
        L("      %-14s %d" % (k, by_kind[k]))
    L("  命中文件数        : %d / %d" % (len([f for f in per_file if per_file[f]["hits"]]), len(per_file)))

    L("")
    L("── 命中 TOP 20 文件 ──")
    for rel, info in sorted(per_file.items(), key=lambda kv: -kv[1]["hits"])[:20]:
        if info["hits"]:
            L("  %6d  %-58s [%s]" % (info["hits"], rel, info["file_class"]))

    L("")
    L("── 改名 / 不动 命中分布 ──")
    mv = {}
    for h in hits:
        mv[h["move"]] = mv.get(h["move"], 0) + 1
    for k in sorted(mv):
        L("      %-6s %d" % (k, mv[k]))

    L("")
    L("── 唯一 ref 数 (MECH 侧命中的) ──")
    uniq = sorted({h["ref"] for h in hits})
    L("  唯一 ref: %d 个" % len(uniq))
    for i in range(0, len(uniq), 6):
        L("      " + "  ".join("%-18s" % u for u in uniq[i:i + 6]))

    # ---- 写 TSV ----
    import csv
    with open(OUT_TSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["file", "line", "hit_kind", "file_class", "ref", "new_ref", "move", "context"])
        for h in hits:
            w.writerow([h["rel"], h["line"], h["kind"], h["file_class"], h["ref"], h["new"],
                        h["move"], h["ctx"].replace("\t", " ")])
    L("")
    L("TSV 写出: %s (%d 行 + 表头)" % (os.path.relpath(OUT_TSV, PROJ), len(hits)))

    # ---- 写 universe json ----
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump({"count": len(uni), "move": n_move, "keep": n_keep,
                   "universe": uni}, fh, ensure_ascii=False, indent=1, sort_keys=True)
    L("JSON 写出: %s" % os.path.relpath(OUT_JSON, PROJ))

    with open(OUT_RAW, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
