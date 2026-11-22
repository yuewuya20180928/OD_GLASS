#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-349 cont1 · 交卷页引用路径 MISS 自检 (★任务书 §5⑤·最近三轮全栽在这条上★)

用法:
    python3 logs/iss349/cont1/path_miss_check.py \
        [--page HANDOFF/2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md] \
        [--out logs/iss349/cont1/04_path_miss_final.txt]

做法:
  1) 从交卷页全文里抽出所有"看起来像仓内路径"的 token
     (反引号包裹 / 纯文本 · 顶层目录限定在 HW / state / logs / tmp / HANDOFF)
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
TOPDIRS = ("HW", "state", "logs", "tmp", "HANDOFF")

# 形如 HW/PCB/xxx.py / state/fragments/hw.yaml / logs/iss349/x.log / tmp/iss349/sb_base
PATH_RE = re.compile(
    r"(?<![\w./~-])((?:%s)/[A-Za-z0-9_.*/一-鿿\-]*\.[A-Za-z0-9_]+|%s/[A-Za-z0-9_.*/一-鿿\-]*)"
    % ("|".join(TOPDIRS), "|".join(TOPDIRS))
)


def extract(txt: str) -> list[str]:
    out = []
    for m in PATH_RE.finditer(txt):
        p = m.group(1).rstrip(".,;:)")
        # 去掉行内代码里的尾缀标点 / 括号
        p = p.split(":")[0] if p.count(":") == 1 and not p.startswith("http") else p
        if p not in out:
            out.append(p)
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", default="HANDOFF/2026-11-23_hw-lead_ISS349_板侧项全集生成器回归修复.md")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    page = os.path.join(PROJ, args.page)
    txt = open(page, encoding="utf-8").read()
    paths = extract(txt)

    lines = []
    lines.append("★ISS-349 cont1 · 交卷页引用路径 MISS 自检 (★任务书 §5⑤·最近三轮全栽在这条上★)")
    lines.append("  被检页 = %s" % args.page)
    lines.append("  被检路径数 = %d" % len(paths))
    miss = 0
    for p in paths:
        ap_ = os.path.join(PROJ, p)
        if os.path.exists(ap_):
            lines.append("  OK   %s" % p)
        elif "*" in p:
            # ★glob 模式 (★页里写了 "HANDOFF/xxx_*.md" 这类·不能当字面路径判 MISS★)
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
