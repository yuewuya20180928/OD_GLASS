#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_only_additions.py —— 「追加式订正·老字一字未删」机器自证 (★ISS-344★)
================================================================================
★**为什么不能用 `diff | grep -c '^<'`**: ★**§3 表里有 14 行是【行内插入】(在单元格中间插字)
  ⇒ 行级 diff 会把这 14 行同时打成 `<` 和 `>` ⇒ 行级 diff 看不出「只增不删」** ★
  ⇒ ★**本脚本按【字符级子序列】证明: 老内容逐字符都还在, 且顺序不变 ⇒ 只可能是插入** ★

★**判据 (★三条全过才算过★)** ★★
  ① **逐行**: 老文件每一行 (非空) 必须【逐字出现在新文件里】, 或【是某个新行的字符子序列】
     (★后者 = 该行被行内插入了字, 但老字符一个没少、顺序没变★)
  ② **全文**: 老文件全文必须是新文件全文的【字符子序列】(★⇒ 全局一个字符都没被删★)
  ③ **反向**: 新文件里新增的行数 ≥ 老文件行数 (★只增不减★)

★**用法**: python3 logs/iss344/check_only_additions.py <老文件> <新文件>
"""
import hashlib
import sys


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def is_subseq(short, long_):
    it = iter(long_)
    return all(ch in it for ch in short)


def main():
    if len(sys.argv) < 3:
        print("用法: python3 check_only_additions.py <老文件> <新文件>")
        return 2
    old_p, new_p = sys.argv[1], sys.argv[2]
    old = open(old_p, encoding="utf-8").read()
    new = open(new_p, encoding="utf-8").read()
    old_l = old.split("\n")
    new_l = new.split("\n")

    print("═══ 追加式订正 · 只增不删 机器自证 (★ISS-344★) ═══")
    print("  老文件 : %s" % old_p)
    print("          md5 %s · %d 行 · %d 字符" % (md5(old_p), len(old_l), len(old)))
    print("  新文件 : %s" % new_p)
    print("          md5 %s · %d 行 · %d 字符" % (md5(new_p), len(new_l), len(new)))

    # ① 逐行
    verbatim = 0
    inserted = 0
    fail = []
    new_set = set(new_l)
    for i, l in enumerate(old_l, 1):
        if not l.strip():
            continue
        if l in new_set:
            verbatim += 1
            continue
        if any(is_subseq(l, n) for n in new_l):
            inserted += 1
            continue
        fail.append((i, l))
    print("\n  ① 逐行判据")
    print("     老行逐字原样仍在      : %d 行" % verbatim)
    print("     老行被【行内插入】     : %d 行 (★老字符一个没少·顺序没变★)" % inserted)
    print("     判据不通过            : %d 行" % len(fail))
    for i, l in fail[:10]:
        print("       ✘ 老文件第 %d 行: %s" % (i, l[:120]))

    # ② 全文
    glob = is_subseq(old, new)
    print("\n  ② 全文判据: 老文件全文是新文件全文的字符子序列 ⇒ %s"
          % ("✔ 一个字符都没被删" % () if glob else "✘ 有字符被删"))

    # ③ 行数
    print("\n  ③ 行数判据: %d ⇒ %d (%+d) ⇒ %s"
          % (len(old_l), len(new_l), len(new_l) - len(old_l),
             "只增不减 ✔" if len(new_l) >= len(old_l) else "✘ 行数少了"))

    ok = (not fail) and glob and len(new_l) >= len(old_l)
    print("\n★★结论: ★**%s** ★" % ("只增不删 ✔ 自证通过" if ok else "★自证不通过★"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
