#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-304 · 沙盒反向用例 (★真盘零写★) ★

★**5 条用例 (★全过才 rc=0★)** ★★:
    ① 生成器连跑两次 ⇒ 清单页 md5 逐字节相同 (★幂等·ISS-292 那条硬判据的延续★)
    ② 同步脚本连跑两次 ⇒ 作业包页 + sidecar md5 逐字节相同 (★幂等★)
    ③ 沙盒台账追加一条新落表链 (★模拟又一次合法落表★) ⇒ 重跑生成器 + 同步
       ⇒ 那 4 条台账口径 `fresh` 值必须跟着新链走 (★**这就是「永不再漂」★**)
    ④ 沙盒台账链断 (★删掉最新链的 §16.2★) ⇒ 生成器必须**拒写** (rc≠0) + 页一个字节没动
       (★**fail-closed·不许静默回退到硬基线★**)
    ⑤ 沙盒闸 `HW/check_workpack_state_values.py` ⇒ rc=0 (★V1~V7 全绿★)

★**跑法**: `python3 tmp/iss304/sbx_tests.py` (★本机实跑·真盘只读★) ★
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys

REAL = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
SB = os.path.join(REAL, "tmp", "iss304", "sbxT")
LEDGER_REL = "HW/SCHEMATIC_LANDING_V1_LANDED.md"
PAGE_REL = "HW/PCB/BOARD_ONEPASS_PREFLIGHT.md"
WP_REL = "HW/PCB/BOARD_ONEPASS_WORKPACKET.md"
SC_REL = "state/_iss277_preflight_appendix.md"

FAKE = {
    "HW/netlist_v1.csv": ("6aee500e60ba0732f83a9cf557ba90ab", "aaaa0000aaaa0000aaaa0000aaaa0000"),
    "HW/netlist_v1_pins.csv": ("9174309df1ec9411ac8e8d9e80ee386a", "bbbb0000bbbb0000bbbb0000bbbb0000"),
    "HW/BOM_v1.csv": ("5b9993992405904a60ac96a020b375d8", "cccc0000cccc0000cccc0000cccc0000"),
}

cases = []


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def run(cmd, env=None, cwd=None):
    e = dict(os.environ)
    e.update(env or {})
    r = subprocess.run(cmd, cwd=cwd or REAL, env=e, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=900)
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace")


def build_sandbox():
    rc, out = run(["bash", os.path.join(REAL, "tmp/iss304/mk_sandbox.sh"), SB])
    assert rc == 0, out
    # ★沙盒里再补两个文件 (★闸的探针要读★) ★
    shutil.copy(os.path.join(REAL, "HW/PCB/BOARD_FRAME_CALIBER.md"),
                os.path.join(SB, "HW/PCB/BOARD_FRAME_CALIBER.md"))


def gen():
    return run(["python3", "state/_iss277_build_preflight.py"],
               env={"PREFLIGHT_PROJ": SB}, cwd=SB)


def sync():
    return run(["python3", "state/_iss304_sync_state_baseline_md5.py"],
               env={"WORKPACKET_PROJ": SB}, cwd=SB)


def read(p):
    with open(os.path.join(SB, p), encoding="utf-8") as fh:
        return fh.read()


def case(name, ok, detail=""):
    cases.append((name, ok))
    print("  %s %s%s" % ("✔" if ok else "✘", name, (" — " + detail) if detail else ""))


def main():
    print("=== ISS-304 · 沙盒反向用例 (★真盘零写★) ===")
    build_sandbox()

    # ---------------------------------------------------------------- ①
    rc1, o1 = gen()
    p1 = md5(os.path.join(SB, PAGE_REL))
    rc2, o2 = gen()
    p2 = md5(os.path.join(SB, PAGE_REL))
    case("① 生成器连跑两次 ⇒ 清单页 md5 逐字节相同", rc1 == 0 and rc2 == 0 and p1 == p2,
         "%s / %s (rc %s/%s)" % (p1[:12], p2[:12], rc1, rc2))

    # ---------------------------------------------------------------- ②
    rc1, o1 = sync()
    w1, s1 = md5(os.path.join(SB, WP_REL)), md5(os.path.join(SB, SC_REL))
    rc2, o2 = sync()
    w2, s2 = md5(os.path.join(SB, WP_REL)), md5(os.path.join(SB, SC_REL))
    case("② 同步脚本连跑两次 ⇒ 作业包页 + sidecar md5 逐字节相同",
         rc1 == 0 and rc2 == 0 and w1 == w2 and s1 == s2,
         "wp %s/%s · sc %s/%s" % (w1[:12], w2[:12], s1[:12], s2[:12]))

    # ---------------------------------------------------------------- ③
    led = read(LEDGER_REL)
    rows = "\n".join(
        "| ★**`%s`** ★ | `%s` | `%s` | ★**是**★ |" % (rel, old, new)
        for rel, (old, new) in FAKE.items())
    newchain = ("\n## ★★20 · ★★ISS-999 落表链 (★沙盒模拟的一次新落表·★ISS-304 反向用例★) ★★\n\n"
                "### ★★16.2 · 新旧 md5 前后对照 (★沙盒模拟★) ★★\n\n"
                "| 文件 | 前 | 后 | 变了? |\n|---|---|---|---|\n%s\n" % rows)
    with open(os.path.join(SB, LEDGER_REL), "w", encoding="utf-8") as fh:
        fh.write(led + newchain)
    rcg, og = gen()
    rcs, os_ = sync()
    page = read(PAGE_REL)
    wp = read(WP_REL)
    ok3 = rcg == 0 and rcs == 0
    for rel, (_old, new) in FAKE.items():
        want = "落表台账登记 = %s" % new
        ok3 = ok3 and (want in page) and (want in wp)
    case("③ 台账链头前跳 ⇒ 4 条 fresh 跟着新链走 (★永不再漂★)", ok3,
         "清单页 %s · 作业包页 %s" % ("有" if "aaaa0000aaaa0000aaaa0000aaaa0000" in page else "无",
                                  "有" if "aaaa0000aaaa0000aaaa0000aaaa0000" in wp else "无"))

    # ---------------------------------------------------------------- ④
    before = md5(os.path.join(SB, PAGE_REL))
    led2 = read(LEDGER_REL).replace("### ★★16.2 · 新旧 md5 前后对照 (★沙盒模拟★) ★★",
                                     "### ★★16.3 · 沙盒故意把 §16.2 弄没了 (★模拟链断★) ★★")
    with open(os.path.join(SB, LEDGER_REL), "w", encoding="utf-8") as fh:
        fh.write(led2)
    rcg, og = gen()
    after = md5(os.path.join(SB, PAGE_REL))
    case("④ 台账链断 ⇒ 生成器拒写 (rc≠0) + 页一个字节没动",
         rcg != 0 and before == after, "rc=%s · md5 %s ⇒ %s" % (rcg, before[:12], after[:12]))
    print("     拒写原文: %s" % (og.strip().splitlines() or ["(空)"])[0][:160])

    # ---------------------------------------------------------------- ⑤
    build_sandbox()                       # ★重建成干净沙盒 (★把 ③④ 的破坏丢掉★)
    gen(); sync()
    rcg, og = run(["python3", "HW/check_workpack_state_values.py"], cwd=SB)
    v3 = "OK   V3" in og
    v4 = "OK   V4" in og
    case("⑤ 沙盒闸 V1~V7 全绿 (rc=0)", rcg == 0 and v3 and v4,
         "rc=%s · V3 %s · V4 %s" % (rcg, "绿" if v3 else "红", "绿" if v4 else "红"))

    print("---")
    bad = [n for n, ok in cases if not ok]
    for n, ok in cases:
        print("  %s %s" % ("通过" if ok else "失败", n))
    print("=== 汇总: %d 条全过才 rc=0 ⇒ %s ===" % (len(cases), "全过" if not bad else "有失败: %s" % bad))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
