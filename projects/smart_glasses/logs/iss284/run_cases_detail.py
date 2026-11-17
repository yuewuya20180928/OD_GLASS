#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-284 · 六条反向/正向用例的【原样 rc + 期望红组 vs 实际红组】逐条打印。

★在临时树上跑 (★真盘一个字节都不碰★) ⇒ 每条用例跑完临时树即销毁★
"""
import importlib.util
import os
import shutil
import sys
import tempfile

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
GATE = os.path.join(ROOT, "SW", "tools", "check_demo_panel_spec.py")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


EXPECT = {
    "REV-16": "期望红组 = {R6 硬保护: 保护基线 md5 在落表台账里查不到 ⇒ 锚点被单独改了}",
    "REV-17": "期望红组 = {R6 硬保护: 锚点里有合法改板记录 (reboard) 但落表台账里查不到任何变更行}",
    "REV-18": "期望红组 = {R6 硬保护: 台账最新记录取不准 (链头不唯一)}",
    "REV-19": "期望红组 = {R6 硬保护: reboard 改前 md5 与台账链头那一行的改前不一致 (链断)}",
    "REV-20": "期望红组 = {R6 硬保护: .kicad_pro 没有被同一次合法改板覆盖 (记录只来一条)}",
    "REV-21": "期望红组 = {} (★正向: 四项齐全 ⇒ 必须绿★)",
}


def main() -> int:
    mod = load(GATE, "iss284_gate")
    bad = 0
    with tempfile.TemporaryDirectory(prefix="iss284_cases_") as tmp:
        for idx, (name, expect_green, fmut) in enumerate(mod.R6_REBOARD_CASES):
            work = mod._build_r6_tree(tmp, ROOT, "case_%02d" % idx)
            fmut(os.path.join(work, mod.BOARD_REL))
            fails = mod.run_all(work, skip_md5=False)
            hit = [f for f in fails if f.startswith("R6")]
            key = name.split(" ")[0]
            print("=" * 100)
            print("### %s" % name)
            print("--- 期望红组: %s" % EXPECT.get(key, "?"))
            print("--- 实际红组 (R6 全部失败项, %d 条):" % len(hit))
            for f in hit:
                print("    %s" % f)
            if expect_green:
                rc = 0 if not hit else 1
                verdict = "PASS (期望绿 ⇒ 实际绿)" if not hit else "FAIL (期望绿却红了)"
            else:
                rc = 1 if hit else 0
                verdict = "PASS (期望红 ⇒ 实际红)" if hit else "FAIL (期望红却绿了)"
            print("--- rc=%d  %s" % (rc, verdict))
            if verdict.startswith("FAIL"):
                bad += 1
    print("=" * 100)
    print("六条用例: %d/6 与期望一致" % (6 - bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
