#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-354 cont2 · 交卷页引用路径在盘自检 (★MISS 必须 = 0★).

★把交卷页正文里出现的【看起来像仓库路径】的 token 抽出来, 逐个到盘上找:
  · 有斜杠且首段是仓库里的已知目录 (HW/ SW/ state/ logs/ HANDOFF/ REQ/ tmp/) ⇒ 当路径查
  · 查法: 路径本体 / 路径去掉末尾 / 路径当目录 ⇒ 命中任一即算在盘
★只读, 不写任何东西。
"""
import os
import re
import sys

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
PAGE = os.path.join(ROOT, "HANDOFF", "2026-11-23_hw-lead_ISS354_demo主板可制造性收口.md")

KNOWN = ("HW/", "SW/", "state/", "logs/", "HANDOFF/", "REQ/", "MECH/", "tmp/", "config/")
# 路径 token: 允许 . _ - / 字母数字 与 § 后缀
TOKEN = re.compile(r"(?:HW|SW|state|logs|HANDOFF|REQ|MECH|tmp|config)/[A-Za-z0-9_./\-一-鿿]+")


def norm(p: str) -> str:
    return p.rstrip("/").rstrip(".")


def exists_as(rel: str) -> bool:
    cand = [
        os.path.join(ROOT, rel),
        os.path.join(ROOT, norm(rel)),
        os.path.join(ROOT, norm(rel) + "/"),
    ]
    for c in cand:
        if os.path.exists(c):
            return True
    # 目录前缀命中 (页里写 logs/iss354/ 这种目录)
    parent = os.path.join(ROOT, norm(rel))
    if os.path.isdir(parent):
        return True
    return False


def main() -> int:
    if not os.path.exists(PAGE):
        print("✗ 交卷页不在盘:", PAGE)
        return 2
    txt = open(PAGE, encoding="utf-8").read()
    # 去掉代码块外的行内反引号包裹影响: 直接抽 token 再清洗
    seen = {}
    for m in TOKEN.finditer(txt):
        raw = m.group(0)
        # 清洗尾部标点 / 括号 / 逗号
        raw = raw.rstrip(".,;:)]}。、，；：）】")
        raw = re.sub(r"[·/]+$", "", raw)
        if len(raw) < 4:
            continue
        seen.setdefault(raw, None)
    miss = []
    for t in sorted(seen):
        if not exists_as(t):
            miss.append(t)
    print("=" * 74)
    print("ISS-354 cont2 · 交卷页引用路径在盘自检")
    print("=" * 74)
    print(f"交卷页      : {os.path.relpath(PAGE, ROOT)}  ({os.path.getsize(PAGE)} B)")
    print(f"抽出路径 token: {len(seen)} 个")
    print(f"在盘命中    : {len(seen) - len(miss)}")
    print(f"MISS        : {len(miss)}")
    for t in miss:
        print("  ✗ MISS:", t)
    if miss:
        print("★结论: 有引用路径不在盘 ⇒ 交卷页不可自证 ✘")
        return 1
    print("★结论: 全部引用路径在盘 (MISS = 0) ✔")
    return 0


if __name__ == "__main__":
    sys.exit(main())
