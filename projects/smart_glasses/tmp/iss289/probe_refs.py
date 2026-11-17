#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-289 · 只读探针: 位号 / 封装数 / DNP 口径一次测清 (★零写板 · 零落表★)

用法 (★必须走 pcbnew_py.sh★):
  bash state/pcbnew_py.sh tmp/iss289/probe_refs.py
"""
import csv
import json
import os
import sys

PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")

import pcbnew  # noqa: E402

board = pcbnew.LoadBoard(PCB)
fps = list(board.GetFootprints())
refs = [f.GetReference() for f in fps]
print("== 官方板 (真盘) ==")
print("封装数 (footprints) =", len(fps))
print("唯一位号数 =", len(set(refs)))
dups = sorted({r for r in refs if refs.count(r) > 1})
print("重复位号 =", dups if dups else "无")
suf1 = sorted(r for r in refs if r.endswith("_1"))
print("带 _1 后缀的位号 =", len(suf1), suf1)
digit_end = sorted(r for r in refs if r and r[-1].isdigit())
print("末字符是数字的位号 =", len(digit_end), digit_end)
letter_end = [r for r in refs if r and not r[-1].isdigit()]
print("末字符是字母的位号 =", len(letter_end))
dnp_marked = sorted(f.GetReference() for f in fps if f.IsDNP())
print("板上带 DNP 标记的位号 =", len(dnp_marked), dnp_marked)
print("板文件 'dnp' 出现次数 =", open(PCB, encoding='utf-8', errors='replace').read().lower().count('dnp'))
print("板框 =", board.GetBoardEdgesBoundingBox().GetWidth() / 1e6,
      "x", board.GetBoardEdgesBoundingBox().GetHeight() / 1e6, "mm")
print("铜层数 =", board.GetCopperLayerCount())

print()
print("== 网表 / BOM 口径 ==")
rows = list(csv.DictReader(open(os.path.join(PROJ, "HW", "netlist_v1.csv"), encoding="utf-8")))
print("网表行数 =", len(rows))
byboard = {}
for r in rows:
    byboard.setdefault((r.get("board") or "MAIN_PCB").strip(), set()).add(r.get("ref"))
for k in sorted(byboard):
    print("  board=%-10s 唯一 ref 数 = %d" % (k, len(byboard[k])))
main_dnp = set()
for r in rows:
    if (r.get("board") or "MAIN_PCB").strip() != "MAIN_PCB":
        continue
    if (r.get("dnp") or "").strip().upper() == "DNP":
        main_dnp.add(r.get("ref"))
print("MAIN_PCB 且 DNP 的唯一 ref 数 =", len(main_dnp))
print("  其中在官方板上的 =", len(main_dnp & set(refs)))
print("  官方板有但 MAIN_PCB∩DNP 没有的 =", sorted(set(refs) - main_dnp))

bom = list(csv.DictReader(open(os.path.join(PROJ, "HW", "BOM_v1.csv"), encoding="utf-8")))
print()
print("== BOM 口径 ==")
print("BOM 行数 =", len(bom))
bom_dnp = {b["ref"] for b in bom if (b.get("dnp") or "").strip().upper() == "DNP"}
print("BOM 里 dnp=DNP 的唯一 ref 数 =", len(bom_dnp))
bom_main = {b["ref"] for b in bom if (b.get("board") or "MAIN_PCB").strip() == "MAIN_PCB"}
print("BOM 里 board=MAIN_PCB 的唯一 ref 数 =", len(bom_main))
print("BOM ∩ 官方板 refs =", len(bom_main & set(refs)))
print("BOM(MAIN_PCB) − 官方板 =", sorted(bom_main - set(refs)))
print("官方板 − BOM(MAIN_PCB) =", sorted(set(refs) - bom_main))
print("BOM dnp 总数 (含 CHG_BOARD/HINGE) =", len(bom_dnp))

print()
print("== S1 位号改名口径 (★186 个加 _1 / 32 个数字结尾不动★) ==")
all_bom_refs = {b["ref"] for b in bom}
letter_bom = sorted(r for r in all_bom_refs if r and not r[-1].isdigit())
digit_bom = sorted(r for r in all_bom_refs if r and r[-1].isdigit())
print("BOM 218 位号里 末字符是字母 (需加 _1) =", len(letter_bom))
print("BOM 218 位号里 末字符是数字 (不动) =", len(digit_bom))
print("  其中末字符是数字的样例 =", digit_bom[:40])
print("官方板 186 个封装里 末字符是字母 (需加 _1) =", len(letter_end))
print("官方板 186 个封装里 末字符是数字 (不动) =", len(digit_end), digit_end)
new_refs = [r + "_1" for r in letter_end]
print("★改名后官方板带 _1 后缀的位号数 = %d + %d = %d"
      % (len(new_refs), len([r for r in digit_end if r.endswith('_1')]),
         len(new_refs) + len([r for r in digit_end if r.endswith('_1')])))
all_new = set(new_refs) | set(refs)
print("改名后位号唯一性 = %d / %d" % (len(all_new), len(refs)))
print("撞名 =", sorted({r for r in new_refs if r in set(refs)}) or "无")
