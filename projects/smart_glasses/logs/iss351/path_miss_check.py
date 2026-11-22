#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-351 · hw-lead · 交卷页引用路径 MISS 自检 (★沿用 ISS-349 cont1 的做法·白名单扩到 SW/MECH/REF★)

用法:
    python3 logs/iss351/path_miss_check.py \
        [--page HANDOFF/2026-11-23_hw-lead_ISS351_存储轴旧口径清账.md] \
        [--out logs/iss351/10_path_miss_final.txt]

做法:
  1) 从交卷页全文里抽出所有"看起来像仓内路径"的 token (反引号包裹 / 纯文本)
  2) 逐个 stat 在盘
  3) MISS 行数 = 0 ⇒ PASS; 否则 rc=1
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys

PROJ = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
TOPDIRS = ("HW", "SW", "state", "logs", "tmp", "HANDOFF", "MECH", "REF", "PRINT", "config", "deploy", "docs")

PATH_RE = re.compile(
    r"(?<![\w./~-])((?:%s)/[A-Za-z0-9_.*/一-鿿\-]*\.[A-Za-z0-9_]+|%s/[A-Za-z0-9_.*/一-鿿\-]*)"
    % ("|".join(TOPDIRS), "|".join(TOPDIRS))
)

# 顶层单文件 (不在 TOPDIRS 下的仓根文件)
ROOTFILES = (
    "DECISION_ONE_PAGER_2026-11-22.md",
    "DECISION_INDEX_2026-11-18.md",
    "DECISIONS.md",
    "PROGRESS_SNAPSHOT.md",
    "STATUS_SUMMARY.md",
    "PROJECT_TRACKER.md",
    "TODO.md",
    "TASK_BOARD.md",
    "AGENTS.md",
)
ROOT_RE = re.compile(r"(?<![\w./~-])(%s)" % "|".join(ROOTFILES))


def extract(txt: str) -> list[str]:
    out = []
    for m in PATH_RE.finditer(txt):
        p = m.group(1).rstrip(".,;:)")
        # 去掉 #锚点 与 :行号
        p = p.split("#", 1)[0]
        if p.count(":") == 1:
            p = p.split(":", 1)[0]
        if p and p not in out:
            out.append(p)
    for m in ROOT_RE.finditer(txt):
        p = m.group(1).rstrip(".,;:)")
        if p not in out:
            out.append(p)
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", default="HANDOFF/2026-11-23_hw-lead_ISS351_存储轴旧口径清账.md")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    page = os.path.join(PROJ, args.page)
    txt = open(page, encoding="utf-8").read()
    paths = extract(txt)

    lines = []
    lines.append("★ISS-351 · hw-lead · 交卷页引用路径 MISS 自检 (★任务书 §3「页内引用路径逐个在盘·MISS = 0」★)")
    lines.append("  被检页 = %s" % args.page)
    lines.append("  被检路径数 = %d" % len(paths))
    miss = 0
    for p in paths:
        ap_ = os.path.join(PROJ, p)
        if os.path.exists(ap_):
            lines.append("  OK   %s" % p)
        elif "*" in p:
            hits = sorted(glob.glob(ap_))
            if hits:
                lines.append("  OK   %s  (★glob 命中 %d 个: %s★)"
                             % (p, len(hits), ", ".join(os.path.basename(h) for h in hits)))
            else:
                miss += 1
                lines.append("  MISS %s  (★glob 命中 0 个★)" % p)
        else:
            miss += 1
            lines.append("  MISS %s" % p)
    lines.append("  ★MISS 行数 = %d" % miss)
    lines.append("  --- rc=%d ---" % (0 if miss == 0 else 1))

    text = "\n".join(lines) + "\n"
    print(text, end="")
    if args.out:
        outp = os.path.join(PROJ, args.out)
        os.makedirs(os.path.dirname(outp), exist_ok=True)
        with open(outp, "w", encoding="utf-8") as f:
            f.write(text)
    return 0 if miss == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
