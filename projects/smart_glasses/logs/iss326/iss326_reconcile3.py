#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iss326_reconcile3.py —— 口径对账 (修正版 walk) + 规则扫描: 找 main 的 571 / 174 / 129 / 120 / 116 / 74"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
MECH = os.path.join(PROJ, "MECH")

uni = json.load(open(os.path.join(HERE, "mech_ref_universe.json"), encoding="utf-8"))["universe"]
REFS = sorted(uni.keys(), key=len, reverse=True)
PATS = {r: re.compile(r"(?<![A-Za-z0-9_])" + re.escape(r) + r"(?![A-Za-z0-9_])") for r in REFS}
PATS_SUB = {r: re.compile(re.escape(r)) for r in REFS}          # 无词边界
MOVE_REFS = [r for r in REFS if uni[r]["move"] == "改名"]
KEEP_REFS = [r for r in REFS if uni[r]["move"] == "不动"]
PATS_MOVE = {r: PATS[r] for r in MOVE_REFS}
PATS_KEEP = {r: PATS[r] for r in KEEP_REFS}
PATS_MOVE_SUB = {r: PATS_SUB[r] for r in MOVE_REFS}

SHAPE_PFX = re.compile(r"\b(?:R_|C_|U_|J_|D_|L_|Q_|TP_|LED_|FB_|BT_|CONN_|CHG_|SW_|VBUS_|PWR_)[A-Za-z0-9_]*")


def walk(sub):
    out = []
    if sub:
        for dp, dn, fns in os.walk(MECH):
            dn[:] = sorted(d for d in dn if d != "__pycache__")
            for fn in sorted(fns):
                if fn.endswith((".py", ".md")):
                    out.append(os.path.join(dp, fn))
    else:
        for fn in sorted(os.listdir(MECH)):
            p = os.path.join(MECH, fn)
            if os.path.isfile(p) and fn.endswith((".py", ".md")):
                out.append(p)
    return sorted(out)


def count_rule(lines, pats, sub_mode=False):
    occ = 0
    ln = set()
    uniqpl = 0
    for i, line in enumerate(lines, 1):
        c = 0
        for r, p in pats.items():
            n = len(p.findall(line))
            if n:
                c += n
        if c:
            occ += c
            ln.add(i)
            uniqpl += sum(1 for r in pats if pats[r].search(line))
    return occ, len(ln), uniqpl


MAIN_TOP5 = {
    "MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md": 174,
    "MECH/BOARD_ONEPASS_MECH_SYNC.md": 129,
    "MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md": 120,
    "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md": 116,
    "MECH/BOARD_ONEPASS_MECH_CLAIMS.md": 74,
}

RULES = [
    ("R1_精确真集_有词边界_出现次数", PATS, False),
    ("R2_精确真集_有词边界_命中行数", PATS, None),
    ("R3_精确真集_仅改名186_有词边界_次数", PATS_MOVE, False),
    ("R4_精确真集_仅改名186_有词边界_行数", PATS_MOVE, None),
    ("R5_精确真集_仅不动32_有词边界_次数", PATS_KEEP, False),
    ("R6_前缀形状正则_次数", None, False),
]

print("=" * 96)
print("★对账目标 (main 2026-11-18 14:0x 本机实读): 顶层 MECH/*.md + MECH/*.py 合计 571 处")
print("  main 前5名: " + " / ".join("%s=%d" % (os.path.basename(k), v) for k, v in MAIN_TOP5.items()))
print("=" * 96)

for sub, label in ((False, "顶层 (MECH/*.md + MECH/*.py)"), (True, "递归 (MECH/**/*.md + MECH/**/*.py)")):
    files = walk(sub)
    npy = sum(1 for f in files if f.endswith(".py"))
    nmd = len(files) - npy
    print("")
    print("■ 扫描面 %s   py=%d md=%d 合计=%d" % (label, npy, nmd, len(files)))
    store = {}
    for name, pats, mode in RULES:
        tot_occ = tot_ln = 0
        per = {}
        for p in files:
            rel = os.path.relpath(p, PROJ)
            lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
            if name.startswith("R6"):
                occ = sum(len(SHAPE_PFX.findall(l)) for l in lines)
                ln = sum(1 for l in lines if SHAPE_PFX.search(l))
                up = 0
            else:
                occ, ln, up = count_rule(lines, pats)
            per[rel] = (occ, ln, up)
            tot_occ += occ
            tot_ln += ln
        store[name] = (per, tot_occ, tot_ln)
        # 命中 main 前5名?
        got5 = [per[k][0] for k in MAIN_TOP5]
        exp5 = list(MAIN_TOP5.values())
        match = "★完全对上★" if got5 == exp5 else ("部分接近" if all(abs(a - b) <= 12 for a, b in zip(got5, exp5)) else "")
        print("  %-38s 出现次数合计=%6d  命中行数合计=%6d" % (name, tot_occ, tot_ln))
        print("        前5名实测 = %s   main = %s   %s" % (got5, exp5, match))

# ★子目录单独数字
print("")
print("■ 子目录 (MECH/print/) 单独读数")
for p in walk(True):
    rel = os.path.relpath(p, PROJ)
    if not rel.startswith("MECH/print/"):
        continue
    lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
    occ, ln, up = count_rule(lines, PATS)
    shape = sum(len(SHAPE_PFX.findall(l)) for l in lines)
    print("  %-42s 精确真集=%3d 行=%3d 形状=%4d" % (rel, occ, ln, shape))
