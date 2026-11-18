#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sb01_rename_board_refs.py —— ISS-314 沙盒: 给【板副本】的 156 个板上位号加 `_1` 后缀

★只写沙盒目录 (tmp/iss314_sandbox/) ★ · ★项目板文件一个字节不许动 ★
★规则 = ISS-205 规则 (与 state/gen_kicad_sch.py::kicad_ref() 同口径):
    末字符是数字 ⇒ 不动; 否则加 `_1`
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "demo_mainboard.kicad_pcb")        # ★沙盒副本 (由 cp 复制而来)
OUT = os.path.join(HERE, "board_ref1.kicad_pcb")            # ★改完名的新副本

import pcbnew  # noqa: E402

b = pcbnew.LoadBoard(SRC)
if b is None:
    print("❌ 沙盒板读不回来")
    sys.exit(1)

renamed, kept = [], []
for fp in list(b.GetFootprints()):
    ref = fp.GetReference()
    if not ref:
        continue
    if ref[-1].isdigit():
        kept.append(ref)
        continue
    new = ref + "_1"
    fp.SetReference(new)
    renamed.append((ref, new))

pcbnew.SaveBoard(OUT, b)
print("★沙盒: 改名 %d 个 (末字符数字 ⇒ 不动 %d 个)" % (len(renamed), len(kept)))
print("★样例 (前 8): " + ", ".join("%s→%s" % x for x in renamed[:8]))
print("★不动 (前 8): " + ", ".join(kept[:8]))
print("★输出: %s" % OUT)

# ★自检: 重新读回来确认改名真的落盘了
b2 = pcbnew.LoadBoard(OUT)
refs = [f.GetReference() for f in b2.GetFootprints()]
print("★复读校验: 封装 %d 个 · 带 _1 的 %d 个 · 末字符数字的 %d 个"
      % (len(refs), len([r for r in refs if r.endswith("_1")]),
         len([r for r in refs if r and r[-1].isdigit()])))
print("★未加后缀的样例: " + ", ".join([r for r in refs if not r.endswith("_1")][:6]))
