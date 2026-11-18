#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss323_rename_sw_docs.py —— ISS-323 · 第 7 件的【机器化改法】(★SW 侧 md 文档位号同步★)

★★这是清单里第 7 件的「逐字可执行」本体 ★★
    ★本单【不执行它】(★零改既有文档正文★) ⇒ ★默认 --dry-run★ ★

★★算法 (★与 ISS-321 沙盒造场逐字同源★) ★★:
    · 真集 = logs/iss321/rename_sets.json 的 186 条「要改」映射 (★机器解析·非手抄★)
    · 替换 = 【词边界精确字面量】⇒ ★不是靠前缀猜★
    · 顺序 = 【长的名字先替换】⇒ ★避免短名先替掉长名★ ★
    · 只动 `SW/*.md` (★41 份★) ⇒ ★`SW/tools/*.py` 归第 1/2/3 件管·本脚本不碰★ ★

★★三个开关 ★★:
    --dry-run          (★默认★) 只报计划, 不写任何文件
    --apply            真写 (★必须同时给 --out ★ ⇒ 永远写到项目外的一个副本目录★)
    --exclude A,B      ★留证文件白名单 (★不改·★见清单第 7 件「哪些是留证不能改」★) ★
    --out DIR          输出目录 (★--apply 时必给★)

★★退出码 ★★: 0 = 计划已出 (或 apply 成功) · 2 = 输入读不到 (★fail-closed★)
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
SETS = os.path.join(os.path.dirname(HERE), "iss321", "rename_sets.json")
SW_DIR = os.path.join(PROJ, "SW")


def load_map():
    d = json.load(open(SETS, encoding="utf-8"))
    m = d["map"]
    ren = {k: v for k, v in m.items() if k != v}
    return ren, d.get("selfcheck", {})


def main():
    ap = argparse.ArgumentParser(description="ISS-323 · SW 侧 md 文档位号同步 (★默认 dry-run★)")
    ap.add_argument("--dry-run", action="store_true", help="只报计划 (★默认行为★)")
    ap.add_argument("--apply", action="store_true", help="★真写 (★必须配 --out★)")
    ap.add_argument("--out", default="", help="输出目录 (★--apply 时必给★)")
    ap.add_argument("--exclude", default="",
                    help="★留证文件白名单 (逗号分隔·文件名)· 这些文件一个字都不改★")
    args = ap.parse_args()

    if args.apply and not args.out:
        print("[FAIL] --apply 必须同时给 --out (★不许直接改项目真件★)")
        return 2
    if not os.path.isfile(SETS):
        print("[FAIL] fail-closed: 真集文件读不到: %s" % SETS)
        return 2

    ren, selfcheck = load_map()
    excl = {x.strip() for x in args.exclude.split(",") if x.strip()}
    keys = sorted(ren.keys(), key=len, reverse=True)

    print("=" * 96)
    print("ISS-323 · 第 7 件 · SW 侧 md 文档位号同步 (★%s★)"
          % ("DRY-RUN (★不写任何文件★)" if not args.apply else "APPLY → %s" % args.out))
    print("=" * 96)
    print("  ★真集来源 : logs/iss321/rename_sets.json (186 条要改·机器解析)")
    print("  ★映射条数 : %d" % len(ren))
    print("  ★扫描范围 : SW/*.md (★不含 SW/tools/*.py★)")
    print("  ★替换算法 : 词边界精确字面量 + 长名优先")
    print("  ★留证排除 : %s" % (", ".join(sorted(excl)) if excl else "★无★"))
    print("")

    total_hits = 0
    total_files = 0
    plan = []
    for name in sorted(os.listdir(SW_DIR)):
        if not name.endswith(".md"):
            continue
        if name in excl:
            print("  ★跳过 (留证): SW/%s" % name)
            continue
        src = os.path.join(SW_DIR, name)
        txt = open(src, encoding="utf-8", errors="replace").read()
        hits = 0
        per_tok = {}
        for old in keys:
            new = ren[old]
            pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(old) + r"(?![A-Za-z0-9_])")
            txt, c = pat.subn(new, txt)
            if c:
                per_tok[old] = c
                hits += c
        if hits:
            total_hits += hits
            total_files += 1
            plan.append((name, hits, per_tok))
            print("  ★SW/%-46s %4d 处 · %2d 个位号" % (name, hits, len(per_tok)))
        else:
            print("  ·SW/%-46s %4d 处" % (name, 0))

    print("")
    print("  ★★合计: %d 份文件 · %d 处字面量替换 ★★" % (total_files, total_hits))
    print("  ★★对照 ISS-321 沙盒实测: 41 份 / 671 处 (★本单在 SW/ONETRIP_SW_RENAME_SAFETY.md 与")
    print("     SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md 建好之后跑 ⇒ 数字会更大·★属正常★) ★★")

    if not args.apply:
        print("")
        print("  ★DRY-RUN 结束 (★一个字节都没写★)")
        return 0

    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    for name in sorted(os.listdir(SW_DIR)):
        if not name.endswith(".md") or name in excl:
            continue
        src = os.path.join(SW_DIR, name)
        txt = open(src, encoding="utf-8", errors="replace").read()
        for old in keys:
            pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(old) + r"(?![A-Za-z0-9_])")
            txt = pat.sub(ren[old], txt)
        open(os.path.join(out, name), "w", encoding="utf-8", errors="replace").write(txt)
    print("")
    print("  ★APPLY 完成 ⇒ 副本落 %s (★项目真件一个字节都没动★)" % out)
    print("  ★★下一步 (★逐字★):")
    print("     1) 把副本逐份覆盖回 SW/  (★这一步才真改项目真件·★归 board-trip 那一趟★)")
    print("     2) python3 SW/tools/check_sw_ref_reachability.py  ⇒ 期望 rc=0 · DESIGNATOR_DRIFT = 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
