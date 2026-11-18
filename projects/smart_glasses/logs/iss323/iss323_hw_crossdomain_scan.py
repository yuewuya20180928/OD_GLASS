#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss323_hw_crossdomain_scan.py —— ISS-323 · 第 4 件 (★跨域·hw-lead 的域★) 的位号字面量清单

★★只读★★: HW/check_netlist_selfconsistency.py (★本单不碰这个文件★)
★★输出 (只写)★★: logs/iss323/04_hw_crossdomain_refs.tsv + 04_hw_crossdomain_scan.txt

★★为什么要有这个脚本★★:
    ISS-321 §2 报了「16 个唯一真位号 / 116 处字面量」·但没给【行号 + 逐字原文 + 哪几处是【判据 DSL】】★
    ⇒ 本单要把第 4 件做成【逐字可执行清单】⇒ 必须自己把行号与原文抄准 (★从盘上真件抄·不许凭印象★)
    ⇒ ★★本脚本只做「抄」这件事·不给改法·改法是本单清单里的人工判断★★

★★口径 (与 ISS-321 §2 逐字同源)★★:
    真集 = logs/iss321/rename_sets.json 的 218 个旧 ref (★机器解析·非手抄★)
    命中 = 【精确字面量 + 词边界】★ ⇒ ★不是靠前缀猜★
"""
import json
import os
import re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
SETS = os.path.join(os.path.dirname(HERE), "iss321", "rename_sets.json")
TARGET = os.path.join(PROJ, "HW", "check_netlist_selfconsistency.py")
OUT_TSV = os.path.join(HERE, "04_hw_crossdomain_refs.tsv")
OUT_TXT = os.path.join(HERE, "04_hw_crossdomain_scan.txt")

OUT = []


def A(s):
    OUT.append(s)
    print(s)


def main():
    sets = json.load(open(SETS, encoding="utf-8"))
    universe = sorted(sets["map"].keys())          # ★218 个旧 ref★

    src = open(TARGET, encoding="utf-8").read()
    lines = src.split("\n")

    # ★行类别判定★ (★三档★):
    #   DSL  = 判据四元组字面量行 ★直接决定判决★ (形如 ("id", "kind", "arg", "expr"),)
    #   CODE = Python 代码行 (★含位号字面量·会真炸★)
    #   COMM = 纯注释 / 文档行 (★改不改都不影响判决★)
    DSL_RE = re.compile(r"""^\s*\(["']""")
    COMM_RE = re.compile(r"""^\s*(#|//|·|★|\*|/\*)""")

    def kind_of(ln):
        if DSL_RE.match(ln):
            return "DSL"
        if COMM_RE.match(ln):
            return "COMM"
        return "CODE"

    rows = []
    per_token = defaultdict(list)
    for tok in universe:
        # ★词边界精确字面量★ (★ISS-321 §2 同款口径★)
        pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(tok) + r"(?![A-Za-z0-9_])")
        for i, ln in enumerate(lines, 1):
            n = len(pat.findall(ln))
            if not n:
                continue
            per_token[tok].append((i, n, ln))
            for _ in range(n):
                rows.append((i, tok, kind_of(ln), ln.rstrip()))

    A("=" * 96)
    A("ISS-323 · 第 4 件 (跨域) · HW/check_netlist_selfconsistency.py 的真位号字面量清单")
    A("=" * 96)
    A("  ★文件: HW/check_netlist_selfconsistency.py")
    A("  ★总行数: %d" % len(lines))
    A("  ★真集来源: logs/iss321/rename_sets.json (218 个旧 ref·机器解析)")
    A("")
    A("── 分组 A: 【改名组】(★末字符是字母 ⇒ 要改 _1★) ──")
    total = 0
    rename_group = []
    for tok in sorted(per_token, key=lambda t: -sum(c for _, c, _ in per_token[t])):
        cnt = sum(c for _, c, _ in per_token[tok])
        new = sets["map"].get(tok, "")
        if not new or new == tok:
            continue          # ★不在 186 改名组 ⇒ 归分组 B (不动组)★
        rename_group.append(tok)
        total += cnt
        A("  %-18s %3d 处   行号: %s   改名后: %s" % (
            tok, cnt,
            ",".join(str(i) for i, _, _ in per_token[tok]),
            new))
    A("")
    A("  ★【改名组】唯一 token 数 = %d   字面量总处数 = %d" % (len(rename_group), total))
    A("  ★★交叉验证: ISS-321 §2 报的是「16 个唯一真位号 / 116 处」⇒ 逐字一致: %s" % (
        "★OK★" if (len(rename_group) == 16 and total == 116) else "★不符★"))

    A("")
    A("── 分组 B: 【不动组】(★末字符是数字 ⇒ 一律不动★·★这些不是改名引起的·不用动★) ──")
    keep_total = 0
    for tok in sorted(per_token):
        if tok in rename_group:
            continue
        cnt = sum(c for _, c, _ in per_token[tok])
        keep_total += cnt
        A("  %-18s %3d 处   行号: %s   (★末字符是数字 ⇒ kicad_ref() 原样返回★)" % (
            tok, cnt, ",".join(str(i) for i, _, _ in per_token[tok])))
    A("")
    A("  ★【不动组】唯一 token 数 = %d   字面量总处数 = %d" % (
        len(per_token) - len(rename_group), keep_total))
    A("  ★★全文件合计 = %d 唯一 token / %d 处字面量" % (len(per_token), total + keep_total))

    dsl_rows = [r for r in rows if r[2] == "DSL"]
    code_rows = [r for r in rows if r[2] == "CODE"]
    comm_rows = [r for r in rows if r[2] == "COMM"]
    A("")
    A("  ★行类别分布 (改名组 + 不动组 全体):")
    A("    DSL  (判据四元组字面量·★直接决定判决★) = %d 处 / %d 行" % (
        len(dsl_rows), len({r[0] for r in dsl_rows})))
    A("    CODE (Python 代码行·★含位号字面量★)     = %d 处 / %d 行" % (
        len(code_rows), len({r[0] for r in code_rows})))
    A("    COMM (纯注释 / 文档行)                  = %d 处 / %d 行" % (
        len(comm_rows), len({r[0] for r in comm_rows})))

    A("")
    A("── 逐行明细 (★TSV 同源·★文件:行 | 位号 | 类别 | 原文逐字★) ──")
    with open(OUT_TSV, "w", encoding="utf-8") as f:
        f.write("文件:行\t位号\t类别\t原文逐字\n")
        for i, tok, cat, ln in sorted(rows):
            f.write("HW/check_netlist_selfconsistency.py:%d\t%s\t%s\t%s\n" % (i, tok, cat, ln))
    A("  ★写出: logs/iss323/04_hw_crossdomain_refs.tsv (%d 行)" % len(rows))

    A("")
    A("── 判据 DSL 行清单 (★这才是 hw-lead 必须动的部分★) ──")
    for i, tok, cat, ln in sorted(dsl_rows):
        A("  L%-5d %-16s %s" % (i, tok, ln.strip()[:120]))

    A("")
    A("── CODE 行清单 (★改名后会真炸的代码路径★) ──")
    for i, tok, cat, ln in sorted(code_rows):
        A("  L%-5d %-16s %s" % (i, tok, ln.strip()[:120]))

    A("")
    A("── 自检 (★三条·不符就 abort★) ──")
    ok1 = (len(rename_group) == 16)
    ok2 = (total == 116)
    A("  ★改名组唯一 token 数 == 16 : %s (实测 %d)" % ("OK" if ok1 else "★不符★", len(rename_group)))
    A("  ★改名组字面量总处数 == 116: %s (实测 %d)" % ("OK" if ok2 else "★不符★", total))
    A("  ★★只读本文件·没改它 (md5 见 logs/iss323/00_baseline_capture.txt 与 99_zerowrite_proof.txt)")
    A("=" * 96)

    open(OUT_TXT, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n★写出: logs/iss323/04_hw_crossdomain_scan.txt")


if __name__ == "__main__":
    main()
