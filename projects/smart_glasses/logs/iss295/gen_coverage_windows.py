#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-295 辅助: 从两页里抓「过期字样」出现点 + 逐字窗口 (★给订正节做覆盖锚点用★)

★窗口必须【逐字包含匹配串】+ 【页内唯一】+ 【≥14 字】⇒ 改写老行 ⇒ 窗口对不上 ⇒ 闸必红★
"""
import re
import sys

PATS = [
    ("缺…边开口规格", r"缺[^。；;、)\n]{0,10}边开口规格"),
    ("边开口规格…缺", r"边开口规格[^。；;、)\n]{0,12}缺"),
    ("登记为缺口", r"登记为缺口"),
    ("缺口…待登记", r"缺口[^。；;、)\n]{0,8}待登记"),
    ("规格…没有…边开口",
     r"(?:现有\s*MECH\s*规格|现有规格|MECH\s*规格)[^。；;、)\n]{0,34}没有[^。；;、)\n]{0,16}边开口"),
    ("没有…边开口", r"没有[^。；;、)\n]{0,16}边开口"),
    ("未补/没补/仍缺…边开口",
     r"(?:未补|没补|尚未补|未登记|没登记|尚缺|仍缺|缺一条结构)[^。；;、)\n]{0,12}边开口"),
    ("缺口…不改板", r"缺口[^。；;、)\n]{0,10}不改板"),
]

PAGES = ["MECH/BOARD_ONEPASS_MECH_SYNC.md", "MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md"]


def heading_of(lines, idx):
    for j in range(idx, -1, -1):
        m = re.match(r"^(#{1,6})\s*(.*)$", lines[j])
        if m:
            return j + 1, m.group(2)
    return 0, ""


def pick_window(lines, i, start, end, page_text):
    line = lines[i]
    cands = []
    for pad in range(4, 120):
        lo = max(0, start - pad)
        hi = min(len(line), end + pad)
        w = line[lo:hi]
        if len(w.strip()) < 14:
            continue
        cands.append(w.strip())
        if page_text.count(w.strip()) == 1:
            return w.strip()
    # 兜底: 取最长候选
    return max(cands, key=len) if cands else line.strip()


def main():
    for p in PAGES:
        text = open(p, encoding="utf-8").read()
        lines = text.splitlines()
        print("=" * 110)
        print(p)
        for i, line in enumerate(lines):
            for name, pat in PATS:
                m = re.search(pat, line)
                if not m:
                    continue
                hl, htxt = heading_of(lines, i)
                w = pick_window(lines, i, m.start(), m.end(), text)
                ok = (m.group(0) in w) and (text.count(w) == 1)
                print("L%-5d [%s] head=L%d %s" % (i + 1, name, hl, htxt[:56]))
                print("      matched=%r" % m.group(0))
                print("      window =%r   (contains=%s unique=%s)"
                      % (w, m.group(0) in w, text.count(w) == 1))
                break


if __name__ == "__main__":
    sys.exit(main())
