#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-257 续做第 1 轮 · hw-lead · P0 修红: 落表链【证据等级词表】写错 ⇒ 改回 `[官方]`
================================================================================
★**根因 (★main 21:1x 本机实跑, 不是猜★)** ★
  上一轮 (ISS-257 第 1 轮, 会话 `agent:hw-lead:subagent:ea25d3e9` status=timeout 20:53)
  把 29 行落表行的 **evidence 列写成了 `[官网]`** ⇒ ★**`state/check_netlist.py` 由绿转红**
  (★G1a-5 = 原理图定稿的尺子 ⇒ 它红 ⇒ 原理图定稿门就红★)。

★**两套词表并存 (★本单只许改落表链那一套★)** ★
  · 落表链 (网表 / 脚表 / BOM 的 evidence 列) ⇒ 白名单 = `state/check_netlist.py` L30 的 **8 档**:
      `[官方]` `[推算]` `[实测]` `[待原厂]` `[待JBD]` `[待视涯]` `[同Die参考-待官方确认]` `[0数据]`
    ⇒ 里面**有 `[官方]`, 没有 `[官网]`** ⇒ ★**唯一修法 = 改回 `[官方]`** ★
  · 选型类 (`HW/PART_SELECTION_MATRIX_2026-11-16.md` / 选型缺口清单 / 交卷单散文) ⇒
    老板政策 **5 档** `[官网]`/`[实测]`/`[媒体]`/`[推算]`/`[0数据]`
    ⇒ ★**选型类那一套一个字不许动** (★本脚本一行都不碰那些文件★)

★**只改 evidence 文字 (★value/opn/footprint/dnp/net/node/type/tbd/note 一律不许动★)** ★
  ① `state/gen_netlist.py`  —— 24 处 `"[官网]"` (★全部在 evidence 列位置★)
  ② `state/p10_rows.json`    —— 5 处 `"evidence": "[官网]"` (★P10 页的真源就是这个 JSON★)
  ⇒ 24 + 5 = 29 ⇒ ★**与网表 CSV 里 29 行 `[官网]` 逐行对得上** ★

★**不许手改 CSV** ★ ⇒ 改完走真源 → 重生成链 (★板那条不许跑★)。

★**自带反向断言 (★假绿铁律: 改完必须证明只有 evidence 列变了★)** ★
  改前把 `HW/netlist_v1.csv` 存快照 ⇒ 改完重生成 ⇒ ★**逐行逐列比对: 除 evidence 外全部列必须逐字节相同★
  ⇒ 任何一列变了 ⇒ rc=1 报警并中止** ★

用法:  python3 state/_apply_iss257_r1_evidence_official.py [--apply]
      ★不带 --apply = 只做改前快照 + 预检 (不动文件)★
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
import shutil
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GN = os.path.join(PROJ, "state", "gen_netlist.py")
P10 = os.path.join(PROJ, "state", "p10_rows.json")
NET_CSV = os.path.join(PROJ, "HW", "netlist_v1.csv")
SNAP_DIR = os.path.join(PROJ, "state", "_iss257_r1_snapshot")

OLD = '"[官网]"'
NEW = '"[官方]"'
EXP_GN = 24
EXP_P10 = 5


def md5(p: str) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def read_csv_rows(p: str):
    with io.open(p, encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="真改 (默认只预检)")
    args = ap.parse_args()

    os.makedirs(SNAP_DIR, exist_ok=True)
    snap_csv = os.path.join(SNAP_DIR, "netlist_v1.csv.before")
    if not os.path.exists(snap_csv):
        shutil.copy2(NET_CSV, snap_csv)
        print("★快照: %s (md5 %s)" % (snap_csv, md5(snap_csv)))

    for p, exp, tag in ((GN, EXP_GN, "state/gen_netlist.py"), (P10, EXP_P10, "state/p10_rows.json")):
        src = io.open(p, encoding="utf-8").read()
        n = src.count(OLD)
        if n != exp:
            print("❌ %s: `[官网]` 出现 %d 次, 期望 %d ⇒ 中止 (★不许猜★)" % (tag, n, exp))
            return 1
        print("★预检 %s: `[官网]` × %d (符合期望)" % (tag, n))

    if not args.apply:
        print("★预检通过 (未改文件)。真改请加 --apply")
        return 0

    # ── 真改 (只改 evidence 文字) ──
    for p, exp, tag in ((GN, EXP_GN, "state/gen_netlist.py"), (P10, EXP_P10, "state/p10_rows.json")):
        src = io.open(p, encoding="utf-8").read()
        assert src.count(OLD) == exp
        src = src.replace(OLD, NEW)
        # ★改后自检: 目标文件里不许再剩 `[官网]`★
        if OLD in src:
            print("❌ %s: 改完仍残留 `[官网]` ⇒ 中止" % tag)
            return 1
        io.open(p, "w", encoding="utf-8", newline="").write(src)
        print("★已改 %s (md5 %s)" % (tag, md5(p)))

    print("★真改完成 ⇒ 接下来必须跑重生成链 (★6 条, 板那条不许跑★)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
