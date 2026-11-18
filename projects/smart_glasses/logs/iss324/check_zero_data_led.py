#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-324 · mech-lead · §2 [0数据] 查证脚本 (只读)

问题: 结构侧 (MECH 域 / 打印包 / 整机件) 对 D_LED_G / D_LED_R / D_LED_B 的【位置】有没有规定?
本脚本逐条 grep 并把【命中清单 + 出处行号】落盘, 不下结论 (结论写在交付页 §2)。
零写板: 只读 + 只写 stdout (由 shell 重定向到 logs/iss324/)。
"""
import os
import re
import subprocess
import sys

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"

PATTERNS = [
    ("位号 D_LED_G", r"D_LED_G"),
    ("位号 D_LED_R", r"D_LED_R"),
    ("位号 D_LED_B", r"D_LED_B"),
    ("中文 指示灯", r"指示灯"),
    ("中文 状态灯", r"状态灯"),
    ("中文 电源灯", r"电源灯"),
    ("中文 电量灯", r"电量灯"),
    ("中文 导光柱", r"导光柱"),
    ("中文 导光窗", r"导光窗"),
    ("中文 光孔", r"光孔"),
    ("中文 出光孔", r"出光孔"),
    ("英文 light pipe", r"(?i)light\s*pipe"),
    ("英文 light guide", r"(?i)light\s*guide"),
    ("英文 light hole", r"(?i)light\s*hole"),
    ("英文 window/led", r"(?i)(led[_\- ]?window|window[_\- ]?led)"),
]

SCAN_ROOTS = [
    ("MECH/ (结构域)", "MECH"),
    ("PRINT/ (打印包)", "PRINT"),
    ("MECH/print/ (打印包 Rev B 素材)", "MECH/print"),
    ("REF/ (参考件)", "REF"),
    ("REQ/ (需求)", "REQ"),
    ("docs/ (文档)", "docs"),
    ("FRAMEWORK/ (框架)", "FRAMEWORK"),
    ("config/ (配置)", "config"),
]
SKIP_DIRS = {"__pycache__", ".git", ".openclaw", ".trash"}
SKIP_SUFFIX = (".bak", ".log", ".pyc", ".onnx", ".stl", ".3mf", ".zip")


def iter_files(rel_root):
    base = os.path.join(ROOT, rel_root)
    if not os.path.isdir(base):
        return
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(SKIP_SUFFIX):
                continue
            p = os.path.join(dirpath, fn)
            yield os.path.relpath(p, ROOT)


def main():
    print("=" * 80)
    print("ISS-324 §2 [0数据] 查证 · 扫描根: " + ", ".join(r for _, r in SCAN_ROOTS))
    print("=" * 80)
    total = 0
    for label, rel_root in SCAN_ROOTS:
        files = list(iter_files(rel_root))
        print("\n### 扫描根 %s  (%s) · 文件数 %d" % (rel_root, label, len(files)))
        if not files:
            print("  ★该根不存在或为空")
            continue
        for plabel, pat in PATTERNS:
            hits = []
            for rel in files:
                path = os.path.join(ROOT, rel)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                        for i, line in enumerate(fh, 1):
                            if re.search(pat, line):
                                hits.append((rel, i, line.strip()[:180]))
                except Exception:
                    continue
            total += len(hits)
            shown = hits if len(hits) <= 12 else hits[:12]
            print("  [%s] 命中 %d" % (plabel, len(hits)))
            for rel, i, txt in shown:
                print("      %s:%d  %s" % (rel, i, txt))
            if len(hits) > 12:
                print("      ... (余 %d 条见下表)" % (len(hits) - 12))
                for rel, i, txt in hits[12:]:
                    print("      %s:%d  %s" % (rel, i, txt))
    print("\n### 合计命中行 = %d (含本脚本自身与交付页的引述行)" % total)

    print("\n### 附: 打印包二进制件 (STL/3MF) 是否含 LED/导光特征 —— 只能做文件名/字符串级判据")
    for rel in ("PRINT/ars45_print_pack.3mf", "MECH/print/fit_coupon_revb.stl",
                "MECH/print/temple_cage_revb.stl", "MECH/print/frame_typec_coupon_revb.stl",
                "MECH/print/optical_cage_TEMPLATE.stl"):
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            print("  %-46s ★不存在" % rel)
            continue
        with open(path, "rb") as fh:
            blob = fh.read()
        low = blob.lower()
        tags = [t for t in (b"led", b"light_pipe", b"lightpipe", b"light_guide", b"window")
                if t in low]
        print("  %-46s %8d B · 字符串级命中: %s"
              % (rel, len(blob), [t.decode() for t in tags] if tags else "无 (⇒ 该件不含 LED/导光命名特征)"))

    print("\n[END] [0数据] 查证扫描完 · 只读")


if __name__ == "__main__":
    sys.exit(main())
