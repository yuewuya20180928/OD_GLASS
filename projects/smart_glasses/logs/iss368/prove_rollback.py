#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-368 · sw-lead · §4 回滚证明 (★逐字节反向补丁 + 回滚后 10 道 SW 闸复跑读数★).

★**真件一个字节不许碰** ★: 全程在项目盘 `tmp/iss368_sbx/rollback_test/` 副本上做
★**跑法** ★: `python3 logs/iss368/prove_rollback.py`
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

PROJ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SBX = os.path.join(PROJ, "tmp", "iss368_sbx")
PATCHED = os.path.join(SBX, "patched")
ROLLBACK = os.path.join(SBX, "rollback_test")
SYNC_REL = os.path.join("SW", "BOARD_ONEPASS_SW_SYNC.md")
IMPACT_REL = os.path.join("SW", "BOARD_ONEPASS_FP_TRUTH_IMPACT.md")
GATE_REL = os.path.join("SW", "tools", "check_fp_truth_read.py")
APPLY_REL = os.path.join("SW", "tools", "apply_sw09_three_place_patch.py")

SW_GATES = [
    "SW/tools/check_onepass_sw_sync.py",
    "SW/tools/check_sw_ref_reachability.py",
    "SW/tools/check_landing_trace_obligation.py",
    "SW/tools/check_demo_panel_spec.py",
    "SW/tools/check_demo_panel_spec_r6_selftest.py",
    "SW/tools/check_demo_panel_spec_r6_chainjudge_selftest.py",
    "SW/tools/check_demo_panel_spec_r6_hardprot_iss315_selftest.py",
    "SW/tools/check_shutdown_semantics.py",
    "SW/tools/check_timing_review_adc_sync.py",
    "SW/tools/timing_check.py",
]


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sh(root, rel, timeout=300):
    env = dict(os.environ)
    tmpd = os.path.join(root, "tmp", "iss368_tmp")
    os.makedirs(tmpd, exist_ok=True)
    env["TMPDIR"] = tmpd
    env["TMP"] = tmpd
    env["TEMP"] = tmpd
    t0 = time.time()
    p = subprocess.run([sys.executable, rel], cwd=root, env=env,
                       capture_output=True, text=True, timeout=timeout)
    return p.returncode, round(time.time() - t0, 2)


def main():
    out = []
    def log(s=""):
        out.append(s)
        print(s)

    log("=" * 96)
    log("ISS-368 · §4 回滚证明 (★逐字节反向补丁 + 回滚后 10 道 SW 闸复跑★)")
    log("  项目根 = %s" % PROJ)
    log("=" * 96)

    if os.path.isdir(ROLLBACK):
        shutil.rmtree(ROLLBACK)
    shutil.copytree(PATCHED, ROLLBACK, symlinks=False)

    truth = {rel: md5_of(os.path.join(PROJ, rel)) for rel in (SYNC_REL, IMPACT_REL, GATE_REL)}
    patched = {rel: md5_of(os.path.join(ROLLBACK, rel)) for rel in (SYNC_REL, IMPACT_REL, GATE_REL)}

    log("")
    log("---- 步骤 1 · 回滚前 (副本 = 已落地态) ----")
    for rel in (SYNC_REL, IMPACT_REL, GATE_REL):
        log("  %-44s 副本 %s | 真件 %s | 与真件相同=%s"
            % (rel, patched[rel], truth[rel], patched[rel] == truth[rel]))

    log("")
    log("---- 步骤 2 · 跑反向补丁 (逐字节回到落地前原文) ----")
    cmd = [sys.executable, APPLY_REL, "--root", PROJ, "--apply", "--rollback",
           "--target-root", ROLLBACK]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    log("  命令 = python3 %s --apply --rollback --target-root <项目盘 tmp/ 下的副本>" % APPLY_REL)
    log("  rc = %d" % p.returncode)
    if p.returncode != 0:
        log("  ★stdout★ %s" % p.stdout[-2000:])
        log("  ★stderr★ %s" % p.stderr[-2000:])
    for line in p.stdout.splitlines():
        if "编辑" in line or "零写入" in line or "已写" in line or "落点③" in line:
            log("  | %s" % line.strip())

    after = {rel: md5_of(os.path.join(ROLLBACK, rel)) for rel in (SYNC_REL, IMPACT_REL, GATE_REL)}
    log("")
    log("---- 步骤 3 · 回滚后逐字节比对 (★副本必须 == 真件落地前原文★) ----")
    all_same = True
    for rel in (SYNC_REL, IMPACT_REL, GATE_REL):
        same = after[rel] == truth[rel]
        all_same = all_same and same
        log("  %-44s 回滚后 %s | 真件 %s | 逐字节相同=%s" % (rel, after[rel], truth[rel], same))
    log("  ★结论: 回滚是否逐字节回到落地前原文 = %s" % ("是 ★" if all_same else "否 ★★红★★"))

    log("")
    log("---- 步骤 4 · 回滚后 10 道 SW 闸复跑 (★在回滚后的副本上逐道实跑★) ----")
    rows = []
    for rel in SW_GATES:
        rc, sec = sh(ROLLBACK, rel)
        rows.append((rel, rc, sec))
        log("    %-70s rc=%s  %ss" % (rel, rc, sec))
    nred = sum(1 for r in rows if r[1] != 0)
    log("  ★10 道闸复跑: 绿 %d / 红 %d" % (len(rows) - nred, nred))

    log("")
    log("---- 步骤 5 · 真件侧复核 (★本单全程零写真件★) ----")
    for rel in (SYNC_REL, IMPACT_REL, GATE_REL):
        log("  %-44s 真件 md5 = %s (与步骤 1 同值 = %s)"
            % (rel, md5_of(os.path.join(PROJ, rel)),
               md5_of(os.path.join(PROJ, rel)) == truth[rel]))

    log("")
    log("=" * 96)
    log("汇总: 逐字节回滚 = %s · 10 道闸复跑 绿 %d / 红 %d"
        % ("是" if all_same else "否", len(rows) - nred, nred))
    log("=" * 96)

    with open(os.path.join(PROJ, "logs", "iss368", "rollback_proof.txt"), "w",
              encoding="utf-8", newline="") as f:
        f.write("\n".join(out) + "\n")
    with open(os.path.join(PROJ, "logs", "iss368", "rollback_proof.json"), "w",
              encoding="utf-8", newline="") as f:
        json.dump({"truth": truth, "patched": patched, "after_rollback": after,
                   "byte_identical": all_same,
                   "gates": [{"rel": r[0], "rc": r[1], "sec": r[2]} for r in rows]},
                  f, ensure_ascii=False, indent=2)
    return 0 if (all_same and nred == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
