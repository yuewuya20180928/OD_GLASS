#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
★ISS-369 独立复核脚本 (v3)★ —— ★自己解析页里的两张表·自己找库·自己 test -f + 重算 md5★
★不调用本单新建的闸·不读上一趟的 JSON ⇒ 独立判定★
校验:
  ① §3.1 表行数 == §3.2 表行数 == 90 / 96
  ② §3.1 + §3.2 的 ref 集合 == 板面 186 个 ref (不多不少)
  ③ 每个标了要写库名的行: lib:name 解析出来 → 指向的 .kicad_mod 逐个 test -f 在盘 + md5 重算 == 页里写的 md5
  ④ 库根下的 .pretty 目录数 / .kicad_mod 总数 (复核 main 给的 155 / 15468)
用法: python3 logs/iss369/scripts/v3_indep_targets_verify.py
"""
import hashlib
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PAGE = os.path.join(ROOT, "HW", "PCB", "FP_LIBID_TRUTH_WORKPACKET.md")
LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
BOARD = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def slice_section(text, start_marker, end_marker):
    i = text.index(start_marker)
    j = text.index(end_marker, i)
    return text[i:j]


def parse_rows(block):
    rows = []
    for ln in block.splitlines():
        ln = ln.strip()
        if not ln.startswith("| `"):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        rows.append(cells)
    return rows


def main():
    with open(PAGE, encoding="utf-8") as f:
        text = f.read()

    tA = parse_rows(slice_section(text, "### §3.1", "### §3.2"))
    tB = parse_rows(slice_section(text, "### §3.2", "### §3.3"))
    print("§3.1 行数 = %d (期望 90)" % len(tA))
    print("§3.2 行数 = %d (期望 96)" % len(tB))

    refsA = [r[0].strip("`") for r in tA]
    refsB = [r[0].strip("`") for r in tB]
    print("§3.1 ref 唯一 = %d · §3.2 ref 唯一 = %d · 两表交集 = %d"
          % (len(set(refsA)), len(set(refsB)), len(set(refsA) & set(refsB))))

    # 板面 ref (纯文本, 不依赖 pcbnew)
    with open(BOARD, encoding="utf-8", errors="replace") as f:
        bt = f.read()
    board_refs = set(re.findall(r'\(property "Reference" "([^"]*)"', bt))
    if not board_refs:
        board_refs = set(re.findall(r'\(fp_text reference "([^"]*)"', bt))
    page_refs = set(refsA) | set(refsB)
    print("板面 ref 数 = %d · 页内两表 ref 数 = %d · 缺 = %s · 多 = %s"
          % (len(board_refs), len(page_refs),
             sorted(board_refs - page_refs)[:8], sorted(page_refs - board_refs)[:8]))

    # ---- 每个「写」行的 .kicad_mod 在盘 + md5 ----
    n_write = 0
    n_ok = 0
    bad = []
    seen_mod = set()
    for tag, rows, i_target, i_path in (("A", tA, 3, 4), ("B", tB, 3, 4)):
        for r in rows:
            if len(r) <= i_path:
                continue
            target = r[i_target].strip("` ")
            if "写" not in target and "不写" not in target:
                pass
            if target.startswith("**不写") or "不需要写" in target:
                continue
            if ":" not in target:
                continue
            n_write += 1
            mm = re.search(r"([A-Za-z0-9_]+\.pretty/[A-Za-z0-9_.+-]+\.kicad_mod)`?\s*md5\s*`?([0-9a-f]{32})`?",
                           r[i_path])
            if not mm:
                bad.append((tag, r[0], "★页里没解析出 path/md5★: %r" % r[i_path][:80]))
                continue
            rel, page_md5 = mm.group(1), mm.group(2)
            seen_mod.add(rel)
            p = os.path.join(LIBROOT, rel)
            if not os.path.isfile(p):
                bad.append((tag, r[0], "★不在盘★ %s" % p))
                continue
            real = md5(p)
            if real != page_md5:
                bad.append((tag, r[0], "★md5 不符★ 页=%s 实=%s %s" % (page_md5, real, rel)))
                continue
            # 目标 lib:name 必须与 .kicad_mod 路径自洽
            lib, nm = target.split(":", 1)
            exp_rel = "%s.pretty/%s.kicad_mod" % (lib, nm)
            if exp_rel != rel:
                bad.append((tag, r[0], "★lib:name 与路径不自洽★ %s vs %s" % (target, rel)))
                continue
            n_ok += 1

    print("\n要写库名的行数 = %d · 逐个 test -f + md5 对得上 = %d · 不过 = %d"
          % (n_write, n_ok, len(bad)))
    for b in bad[:20]:
        print("   ✗ %s %s :: %s" % (b[0], b[1], b[2]))

    # 库根规模复核
    dirs = [d for d in os.listdir(LIBROOT) if d.endswith(".pretty")]
    nmod = 0
    for d in dirs:
        nmod += len([f for f in os.listdir(os.path.join(LIBROOT, d)) if f.endswith(".kicad_mod")])
    print("\n库根 %s · .pretty 目录 = %d · .kicad_mod 文件 = %d (main 给的 155 / 15468)"
          % (LIBROOT, len(dirs), nmod))
    print("页里引用的去重 .kicad_mod = %d 个" % len(seen_mod))
    return 0 if (not bad and len(tA) == 90 and len(tB) == 96 and page_refs == board_refs) else 1


if __name__ == "__main__":
    sys.exit(main())
