#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-288 cont1 · sw-lead · 「改前」基线【自己重跑一遍】(★不抄上趟日志★)

目的: §5 回归对照表里的【改前】那一行, 必须由本趟自己跑出来 (brief §2-③
      「把交卷单里引用的每条命令都自己再跑一遍, 把原样输出贴进去」)。

做法 (★全部在沙盒里, 真盘一个字节不许动★):
  ① 用 verify_iss288_land.py 的 MIN_FILES 清单造一个最小镜像沙盒
     (网表 / 脚表 / BOM / 落表台账 / 板 / .kicad_pro / timing_check.py /
      check_demo_panel_spec.py / SW 台账 / 3 份 spec md)
  ② 把沙盒里的 SW/tools/timing_check.py 换成【改前快照】
     (logs/iss288/timing_check.py.BEFORE, md5 4cba20b1d0249b671632878c964b4bd7
      ≡ state/.bak_iss285_sw_alignment/timing_check.py.bak_20261117-143616)
  ③ 在沙盒里跑 python3 SW/tools/timing_check.py ⇒ 期望 rc=1 · 68/71 · 3 条红

★沙盒是 copies ⇒ 真盘 HW/ SW/ 一个字节都不受影响 (跑完再核 md5)★
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))          # projects/smart_glasses
sys.path.insert(0, os.path.join(PROJ, "SW", "patches", "ISS-288_timing_check_land"))
import verify_iss288_land as V                            # noqa: E402

BEFORE = os.path.join(HERE, "timing_check.py.BEFORE")
SBX = os.path.join(HERE, "sbx_before")


def md5_of(p: str) -> str:
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def main() -> int:
    if os.path.isdir(SBX):
        shutil.rmtree(SBX)
    os.makedirs(SBX)
    V.copy_min(PROJ, SBX)
    # ② 换回改前快照
    shutil.copy2(BEFORE, os.path.join(SBX, V.TIMING_REL))
    print("[沙盒] 改前 timing_check.py md5 = %s" % md5_of(os.path.join(SBX, V.TIMING_REL)))
    print("[沙盒] 改前 check_demo_panel_spec.py md5 = %s"
          % md5_of(os.path.join(SBX, V.DPS_REL)))
    # ③ 跑
    p = subprocess.run([sys.executable, os.path.join(SBX, V.TIMING_REL)],
                       cwd=SBX, capture_output=True, text=True, timeout=600)
    out = (p.stdout or "") + (p.stderr or "")
    log = os.path.join(HERE, "20_REPRO_BEFORE_timing_check.log")
    with open(log, "w", encoding="utf-8") as f:
        f.write(out)
        f.write("\nrc=%d\n" % p.returncode)
    print("---- 沙盒改前 SELFTEST 末行 ----")
    for ln in out.splitlines():
        if ln.startswith("SELFTEST") or "rc=" in ln:
            print(ln)
    print("---- 沙盒改前 FAIL 组 ----")
    for ln in out.splitlines():
        if "  [FAIL] " in ln:
            print(ln.strip())
    print("[沙盒] rc=%d ⇒ 日志 %s" % (p.returncode, log))
    return 0


if __name__ == "__main__":
    sys.exit(main())
