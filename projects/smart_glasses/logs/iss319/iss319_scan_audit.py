#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-319 · mech-lead · 电芯型号订正影响面 —— 全量扫描 + 脚本常量归属核对 (★脚本自算, 非手抄★)

产出:
  §1  全量扫描 (47 行 / N 文件)  —— 排除 tmp/ .trash/ .bak_
  §2  逐行: 文件 + 行号 + 逐字原文 + 机器自动分类 (口径行 / 对照留证行 / 脚本行)
  §3  九个命中脚本的常量归属核对 (哪个常量是哪个型号的 · 哪些一个字不许动)
  §4  零写板双证 (md5 + mtime)

纪律: 本脚本**只读**, 不写任何被保护文件, 不跑任何生成器。
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OLD = "ICP582035PR-01"
NEW = "ICP422339PR"
SCAN_DIRS = ["MECH", "HW", "SW"]
EXCL = ("/tmp/", ".trash/", ".bak_")

# ---------------------------------------------------------------- 留证行人工判定
# 机器可判的两类:
#   (a) 同一行里两个型号名并置  ⇒ 语义是「对照」, 改名即毁 ⇒ 留证/对照行
#   (b) 带日期的更正记录 / 已跑过的一次性结案脚本 ⇒ 历史留证行
# 下面这张表是**人工判定**的部分 (机器判不了「这段话记的是哪天的结论」)。
KEEP_AS_IS = {
    ("MECH/MECH_BUDGET.md", 867): "历史留证行 (2026-10-26 ISS-072 电池行按新电芯重算的更正记录) ⇒ ISS-316 §5-2 已点名不许动",
    ("MECH/_close_iss065.py", 66): "历史留证行 (ISS-065 结案脚本里的一次性结案说明) ⇒ 改它就是改结案记录",
    ("MECH/iss065_check.py", 486): "历史留证行 (ISS-065 复算的 D-9 条发现记录) ⇒ 记录的是当时 §1.3 缺 315 档的事实",
    ("MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md", 280): "对照行 (差集条目里两型号并置)",
    ("MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md", 321): "对照行 (两型号规格并置)",
    ("MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md", 323): "历史留证行 (ISS-316 当时实读的行号清单)",
    ("MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md", 324): "历史留证行 (ISS-316 当时的逐字改法提案)",
    ("MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md", 326): "对照行 (照旧型号买会怎样)",
    ("MECH/BOARD_FRAME_FREEZE_DECISION_PACK.md", 368): "对照行 (官网读数两型号并置)",
    ("MECH/MECH_NEEDS_TRIAGE.md", 163): "对照行 (官网实读两型号并置)",
    ("MECH/MECH_NEEDS_TRIAGE.md", 362): "对照行 (官网规格表两型号并置)",
}

# 每个命中脚本的常量归属 (★本单的核心核对项★)
SCRIPT_CONST = {
    "MECH/service_port_check.py": {
        51: ("BASE[\"cell_thk\"]", 4.60, "ICP422339PR 的厚度", "受保护闸 · 只许改注释里的型号名 · 4.60 一个字不许动"),
        52: ("BASE[\"cell_v\"]", 23.50, "ICP422339PR 的高", "受保护闸 · 23.50 一个字不许动"),
        53: ("BASE[\"cell_l\"]", 40.50, "ICP422339PR 的长", "受保护闸 · 40.50 一个字不许动"),
    },
    "MECH/fit_check.py": {
        69: ("BASE[\"cell_thk\"]", 4.60, "ICP422339PR 的厚度", "注释里改型号名 · 4.60 不许动"),
        70: ("BASE[\"cell_v\"]", 23.50, "ICP422339PR 的高", "注释 · 23.50 不许动"),
        71: ("BASE[\"cell_l\"]", 40.50, "ICP422339PR 的长", "注释 · 40.50 不许动"),
        256: ("print(...) 文案", None, "「改: 电芯 ICP422339PR (4.60 厚) → 丰江 432243」", "只是打印出来的字 · 无逻辑 · 可改"),
    },
    "MECH/fit_check_v3_30mm.py": {
        55: ("BASE[\"cell_thk\"]", 4.60, "ICP422339PR 的厚度", "注释里改型号名 · 4.60 不许动"),
        56: ("BASE[\"cell_v\"]", 23.50, "ICP422339PR 的高", "注释 · 23.50 不许动"),
        57: ("BASE[\"cell_l\"]", 40.50, "ICP422339PR 的长", "注释 · 40.50 不许动"),
    },
    "MECH/print/gen_print_pack_revb.py": {
        99: ("P[\"batt_thk\"]", 4.60, "ICP422339PR 的厚度", "第 3 元是「出处文案」(会被打进打印包尺寸来源表) · 第 1 元 4.60 不许动"),
        100: ("P[\"batt_v\"]", 23.50, "ICP422339PR 的高", "第 3 元是「同上 高」· 无型号名 · 23.50 不许动"),
        101: ("P[\"batt_l\"]", 40.50, "ICP422339PR 的长", "第 3 元是「同上 长」· 无型号名 · 40.50 不许动"),
    },
    "MECH/verify_budget.py": {
        126: ("注释", None, "「340mAh 用 ICP422339PR [官网] 4.6×23.5×40.5」", "纯注释 · 不改逻辑"),
        141: ("注释", None, "「340mAh: ICP422339PR 4.6×23.5×40.5 [官网]」", "纯注释 · 不改逻辑"),
    },
    "MECH/iss065_check.py": {
        71: ("CELLS[\"315\"][\"name\"]", None, "显示用名字字段 (t/v/l/g 才是逻辑量)", "name 字段全脚本无引用 ⇒ 纯显示 · 可改"),
        486: ("发现文案 D-9", None, "历史留证 ⇒ 不改", "留证行"),
    },
    "MECH/carrier_eval.py": {
        55: ("P[\"cell_l\"] 第 2 元", 40.50, "ICP422339PR 的长 (第 2 元是出处文案)", "第 1 元 40.50 不许动"),
        56: ("P[\"cell_thk\"] 第 2 元", 4.60, "同电芯 厚 (文案无型号名)", "第 1 元 4.60 不许动"),
    },
    "MECH/board_width_15mm_check.py": {
        47: ("注释", None, "「电芯 (解 A: ICP422339PR 340mAh 4.60 厚)」", "纯注释 · 不改逻辑"),
    },
    "MECH/_close_iss065.py": {
        66: ("结案说明字符串", None, "历史留证 ⇒ 不改", "一次性结案脚本"),
    },
}


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def scan():
    """全量扫描: 排除 tmp/ .trash/ .bak_"""
    hits = []
    for d in SCAN_DIRS:
        for dp, dns, fns in os.walk(os.path.join(ROOT, d)):
            dns[:] = [x for x in dns if x not in ("__pycache__",)]
            for fn in fns:
                if not (fn.endswith(".py") or fn.endswith(".md")):
                    continue
                fp = os.path.join(dp, fn)
                rel = os.path.relpath(fp, ROOT)
                if any(e in ("/" + rel) for e in EXCL) or ".bak_" in rel:
                    continue
                try:
                    with open(fp, encoding="utf-8", errors="replace") as f:
                        for i, line in enumerate(f, 1):
                            if OLD in line:
                                hits.append((rel, i, line.rstrip("\n")))
                except OSError:
                    pass
    hits.sort(key=lambda t: (t[0], t[1]))
    return hits


def classify(rel, ln, line):
    if (rel, ln) in KEEP_AS_IS:
        return "留证/对照行", KEEP_AS_IS[(rel, ln)]
    if rel.endswith(".py"):
        return "脚本行", "脚本命中 ⇒ 只许改型号名 (注释/显示串), 逻辑与常量一个字不许动"
    return "口径行", "会被后人当现状读 ⇒ 要改 (只换型号名)"


def main():
    out = []
    P = out.append
    P("=" * 100)
    P("ISS-319 · mech-lead · 电芯型号订正影响面 —— 全量扫描 + 脚本常量归属核对")
    P("扫描根 = %s" % ROOT)
    P("扫描范围 = %s/  --include=*.py --include=*.md  排除 /tmp/ .trash/ .bak_" % "/".join(SCAN_DIRS))
    P("=" * 100)

    hits = scan()
    files = sorted({h[0] for h in hits})
    n_py = sum(1 for f in files if f.endswith(".py"))
    n_md = len(files) - n_py
    n_py_lines = sum(1 for h in hits if h[0].endswith(".py"))
    n_md_lines = len(hits) - n_py_lines

    P("")
    P("§1 · 全量扫描汇总")
    P("-" * 100)
    P("命中行数   = %d" % len(hits))
    P("命中文件数 = %d" % len(files))
    P("  其中 .md  = %d 个文件 / %d 行" % (n_md, n_md_lines))
    P("  其中 .py  = %d 个文件 / %d 行   ★脚本命中不是 main 记的 3 个, 实测 %d 个★" % (n_py, n_py_lines, n_py))
    P("")
    P("逐文件命中行数 (降序):")
    for f in sorted(files, key=lambda x: (-sum(1 for h in hits if h[0] == x), x)):
        c = sum(1 for h in hits if h[0] == f)
        P("  %3d  %s" % (c, f))

    P("")
    P("§2 · 逐行: 文件 + 行号 + 逐字原文 + 机器分类")
    P("-" * 100)
    P("(分类规则: ① 人工留证表命中 ⇒ 留证/对照行; ② .py ⇒ 脚本行; ③ 其余 ⇒ 口径行)")
    P("")
    n_kj = n_jz = n_gx = 0
    for rel, ln, line in hits:
        kind, why = classify(rel, ln, line)
        if kind.startswith("留证"):
            n_kj += 1
        elif kind == "脚本行":
            n_gx += 1
        else:
            n_jz += 1
        P("[%s] %s : %d" % (kind, rel, ln))
        P("    原文: %s" % line.strip())
        P("    判定: %s" % why)
        P("")
    P("分类合计: 口径行 %d 行 / 脚本行 %d 行 / 留证·对照行 %d 行  = %d 行" % (n_jz, n_gx, n_kj, len(hits)))

    P("")
    P("§3 · 九个命中脚本的常量归属核对 (★哪个常量是哪个型号的 · 为什么不能动★)")
    P("-" * 100)
    for rel, consts in SCRIPT_CONST.items():
        P("── %s" % rel)
        for ln in sorted(consts):
            name, val, owner, rule = consts[ln]
            try:
                with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
                    src = f.readlines()[ln - 1].rstrip("\n")
            except (OSError, IndexError):
                src = "<读取失败>"
            P("   L%-4d %-26s 值=%-8s 归属=%s" % (ln, name, val, owner))
            P("        现行原文: %s" % src.strip())
            P("        改法纪律: %s" % rule)
        P("")

    P("")
    P("§4 · 零写板双证")
    P("-" * 100)
    for p in ["HW/PCB/demo_mainboard.kicad_pcb", "MECH/service_port_check.py", "MECH/fit_check.py",
              "MECH/fit_check_v3_30mm.py", "MECH/print/gen_print_pack_revb.py", "MECH/MECH_BUDGET.md",
              "HW/netlist_v1.csv", "HW/BOM_v1.csv"]:
        fp = os.path.join(ROOT, p)
        st = os.stat(fp)
        P("  %s  %s  mtime=%s" % (md5(fp), p, st.st_mtime))
    P("")
    P("  板 mtime (人读) = %s" % subprocess.run(
        ["stat", "-c", "%y", os.path.join(ROOT, "HW/PCB/demo_mainboard.kicad_pcb")],
        capture_output=True, text=True).stdout.strip())

    txt = "\n".join(out)
    sys.stdout.write(txt + "\n")
    with open(os.path.join(ROOT, "logs/iss319/scan_audit_raw.txt"), "w", encoding="utf-8") as f:
        f.write(txt + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
