#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-368 · 反证脚本: 「只改一处 ⇒ H4 红 + F4 红」.

★**三个变体** ★
  V0  三处同批落地 (★基线·期望: 全绿★)
  V1  ★只改落点① (清单页三处)★ · 落点② 没改 ⇒ 期望 H4 红 + F4 红
  V2  ★只改落点② (影响页三个数字)★ · 落点① 没改 ⇒ 期望 H4 红 + F4 红

★**跑哪两道闸** ★
  · ISS-362 闸 `SW/tools/check_sw_fp_truth_impact.py` ⇒ 看 H4 (登记 vs 实测)
  · ISS-363 闸 `SW/tools/check_fp_truth_read.py`     ⇒ 看 F4 (登记 vs 实测)

★**真件一个字节不许碰** ★: 变体全在项目盘 `tmp/iss368_sbx/` 下 · 变体里用的是【真件原文】做「回退那一处」★

用法: python3 logs/iss368/prove_partial_landing.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SBX = os.path.join(PROJ, "tmp", "iss368_sbx")
PATCHED = os.path.join(SBX, "patched")
SYNC_REL = os.path.join("SW", "BOARD_ONEPASS_SW_SYNC.md")
IMPACT_REL = os.path.join("SW", "BOARD_ONEPASS_FP_TRUTH_IMPACT.md")
GATE_IMPACT = "SW/tools/check_sw_fp_truth_impact.py"
GATE_READ = "SW/tools/check_fp_truth_read.py"


def sh(root, rel, timeout=180):
    env = dict(os.environ)
    tmpd = os.path.join(root, "tmp", "iss368_tmp")
    os.makedirs(tmpd, exist_ok=True)
    env["TMPDIR"] = tmpd
    env["TMP"] = tmpd
    env["TEMP"] = tmpd
    try:
        p = subprocess.run([sys.executable, rel], cwd=root, env=env,
                           capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "★超时★"


def red_set(out: str):
    """从闸输出里抽红集合 (★形如 `[H4] ... ⇒ ❌ 红` / `[F4] ... ⇒ ❌ 红`★)"""
    reds = []
    for line in out.split("\n"):
        s = line.strip()
        if s.startswith("[") and ("❌" in s or "红" in s.split("⇒")[-1]):
            cid = s[1:s.index("]")] if "]" in s else "?"
            if s.startswith("[H0]"):
                continue
            reds.append(cid)
    return sorted(set(reds))


def make_variant(name: str, revert_rel: str):
    dst = os.path.join(SBX, name)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(PATCHED, dst, symlinks=False)
    if revert_rel:
        shutil.copy2(os.path.join(PROJ, revert_rel), os.path.join(dst, revert_rel))
    return dst


def main() -> int:
    out_lines = []
    report = []

    def log(s=""):
        print(s)
        out_lines.append(s)

    log("=" * 96)
    log("ISS-368 · 反证: 「只改一处 ⇒ H4 红 + F4 红」")
    log("  项目根 = %s" % PROJ)
    log("=" * 96)

    variants = [
        ("V0 三处同批落地 (基线)", None),
        ("V1 只改落点① (清单页) · 落点② 没改", IMPACT_REL),
        ("V2 只改落点② (影响页) · 落点① 没改", SYNC_REL),
    ]
    for label, revert in variants:
        name = {"V0 三处同批落地 (基线)": "v0_both",
                "V1 只改落点① (清单页) · 落点② 没改": "v1_only_sync",
                "V2 只改落点② (影响页) · 落点① 没改": "v2_only_impact"}[label]
        dst = make_variant(name, revert)
        log("")
        log("-" * 96)
        log("### %s" % label)
        log("    变体 = %s" % dst)
        rc1, o1 = sh(dst, GATE_IMPACT)
        rc2, o2 = sh(dst, GATE_READ)
        r1 = red_set(o1)
        r2 = red_set(o2)
        log("    ISS-362 闸 rc=%d · 红集合 = %s" % (rc1, r1 or "无"))
        log("    ISS-363 闸 rc=%d · 红集合 = %s" % (rc2, r2 or "无"))
        for line in o1.split("\n"):
            if line.strip().startswith("[H4]"):
                log("      H4 行: %s" % line.strip())
        for line in o2.split("\n"):
            if line.strip().startswith("[F4]"):
                log("      F4 行: %s" % line.strip())
        report.append({"label": label, "sandbox": dst,
                       "iss362_rc": rc1, "iss362_red": r1,
                       "iss363_rc": rc2, "iss363_red": r2})

    log("")
    log("=" * 96)
    log("汇总")
    for r in report:
        log("  %-46s H4 红=%s · F4 红=%s"
            % (r["label"],
               ("是" if "H4" in r["iss362_red"] else "否"),
               ("是" if "F4" in r["iss363_red"] else "否")))
    v0 = report[0]
    v1 = report[1]
    v2 = report[2]
    ok = (not v0["iss362_red"] and not v0["iss363_red"]
          and "H4" in v1["iss362_red"] and "F4" in v1["iss363_red"]
          and "H4" in v2["iss362_red"] and "F4" in v2["iss363_red"])
    log("")
    log("反证成立 = %s" % ("是 ★" if ok else "否 ★"))
    log("=" * 96)

    with open(os.path.join(PROJ, "logs", "iss368", "prove_partial_landing.out"), "w",
              encoding="utf-8") as f:
        f.write("\n".join(out_lines) + "\n")
    with open(os.path.join(PROJ, "logs", "iss368", "prove_partial_landing.json"), "w",
              encoding="utf-8") as f:
        json.dump({"ok": ok, "variants": report}, f, ensure_ascii=False, indent=2)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
