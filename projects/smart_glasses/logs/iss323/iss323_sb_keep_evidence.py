#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iss323_sb_keep_evidence.py —— ISS-323 · 第 7 件的【留证排除】选项的闸读数实测

★★问题 ★★:
    第 7 件的机器化改名会把 SW/*.md 里所有「要改」的位号字面量一起改掉。
    ★但【体检报告类文档】(★ISS-321 的 SW/ONETRIP_SW_RENAME_SAFETY.md · 本单的
    SW/ONETRIP_SW_SAMEBATCH_RENAME_LIST.md★) 记录的【就是改名前的位号】⇒
    ★把它们改掉 ⇒ 历史体检记录被改写 ⇒ 证据链失真★ ★
    ★把它们留下 ⇒ 闸会怎么判? ★★ ← ★本脚本回答这个★

★★做法 ★★:
    · 场景 K = S2 (板/表已改名 + SW 文档已同步改名) 的副本
    · 但把【留证文档】恢复成【改名前的原文】
    · 跑 ISS-318 的闸 ⇒ 读 DESIGNATOR_MISSING / DESIGNATOR_DRIFT

★★只写 tmp/ + logs/iss323/★ ⇒ ★项目真件一个字节都不动★ ★
"""
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
SB = os.path.join(PROJ, "tmp", "iss321_sandbox")
S2 = os.path.join(SB, "rootS2")
K = os.path.join(SB, "rootS2_keep_evidence")
LOG = os.path.join(PROJ, "logs", "iss323", "15_sb_keep_evidence.txt")

# ★留证文档清单 (★按文件名·★SW/ 下★) ★
KEEP = [
    "ONETRIP_SW_RENAME_SAFETY.md",
    "ONETRIP_SW_SAMEBATCH_RENAME_LIST.md",
]

OUT = []


def A(s):
    OUT.append(s)
    print(s)


def main():
    if os.path.isdir(K):
        shutil.rmtree(K)
    shutil.copytree(S2, K, symlinks=True)
    os.makedirs(os.path.join(K, "tmp"), exist_ok=True)

    A("=" * 96)
    A("ISS-323 · 第 7 件 · 「留证文档不改」选项的闸读数实测 (★场景 K★)")
    A("=" * 96)
    A("  ★场景 K = S2 (板/表已改名 + SW 文档已同步改名) 的副本")
    A("  ★但把【留证文档】恢复成【改名前的原文】 ⇒ 模拟「历史体检记录保真」")
    A("")

    restored = []
    for name in KEEP:
        src = os.path.join(PROJ, "SW", name)
        dst = os.path.join(K, "SW", name)
        if not os.path.isfile(src):
            A("  ★跳过 (真件里还没有): SW/%s" % name)
            continue
        if os.path.lexists(dst):
            os.remove(dst)
        shutil.copy2(src, dst)
        restored.append(name)
        A("  ★恢复成改名前原文: SW/%s" % name)

    A("")
    A("── 跑 ISS-318 闸 (★场景 K★) ──")
    p = subprocess.run([sys.executable, "SW/tools/check_sw_ref_reachability.py"],
                       cwd=K, capture_output=True, text=True, timeout=900)
    out = (p.stdout or "") + (p.stderr or "")
    A("  rc=%s" % p.returncode)
    for ln in out.splitlines():
        if re.search(r"DESIGNATOR_(OK|DRIFT|MISSING)|基线|扫描文档|抽出 token", ln):
            A("    %s" % ln[:140])

    drift = m = None
    for ln in out.splitlines():
        mm = re.search(r"DESIGNATOR_DRIFT\s+(\d+)", ln)
        if mm:
            drift = mm.group(1)
        mm = re.search(r"DESIGNATOR_MISSING\s+(\d+)", ln)
        if mm:
            m = mm.group(1)
    A("")
    A("  ★★场景 K 读数: DESIGNATOR_DRIFT = %s · DESIGNATOR_MISSING = %s (★基线上限 = 3★)"
      % (drift, m))
    A("  ★★对照 S2 (全改): DESIGNATOR_DRIFT = 0 · DESIGNATOR_MISSING = 3 (★= 基线·绿★)")
    A("  ★⇒ 若 MISSING > 3 ⇒ ★留证文档不改 ⇒ 闸红 (新增真隐患) ★")
    A("")
    A("★★真闸 SW/tools/*.py 一个字节都没改 ★★")
    A("=" * 96)

    open(LOG, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n★写出: logs/iss323/15_sb_keep_evidence.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
