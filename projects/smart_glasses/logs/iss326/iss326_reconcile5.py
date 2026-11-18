#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iss326_reconcile5.py —— 口径大扫: (regex × 范围 × 计数方式) 矩阵, 找 main 的 571 与前5名向量"""
import os, re, itertools, json

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
MECH = os.path.join(PROJ, "MECH")
uni = json.load(open(os.path.join(HERE, "mech_ref_universe.json"), encoding="utf-8"))["universe"]
REFS = sorted(uni.keys(), key=len, reverse=True)

MAIN_TOP5 = [
    ("MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md", 174),
    ("MECH/BOARD_ONEPASS_MECH_SYNC.md", 129),
    ("MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md", 120),
    ("MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md", 116),
    ("MECH/BOARD_ONEPASS_MECH_CLAIMS.md", 74),
]
EXP5 = [v for _, v in MAIN_TOP5]
T5NAMES = [os.path.basename(k) for k, _ in MAIN_TOP5]

REGEXES = {
    "exact_wb": re.compile(r"(?<![A-Za-z0-9_])(?:" + "|".join(re.escape(r) for r in REFS) + r")(?![A-Za-z0-9_])"),
    "exact_nw": re.compile("(?:" + "|".join(re.escape(r) for r in REFS) + r")"),
    "exact_wb_move": re.compile(r"(?<![A-Za-z0-9_])(?:" + "|".join(
        re.escape(r) for r in REFS if uni[r]["move"] == "改名") + r")(?![A-Za-z0-9_])"),
    "shp_A1_4": re.compile(r"\b[A-Z]{1,4}_[A-Za-z0-9_]*[A-Za-z0-9]\b"),
    "shp_A1_3": re.compile(r"\b[A-Z]{1,3}_[A-Za-z0-9_]*[A-Za-z0-9]\b"),
    "shp_A2_4": re.compile(r"\b[A-Z]{2,4}_[A-Za-z0-9_]*[A-Za-z0-9]\b"),
    "shp_uc1": re.compile(r"\b[A-Z][A-Z0-9]*_[A-Za-z0-9_]*[A-Za-z0-9]\b"),
    "shp_uc1_3": re.compile(r"\b[A-Z][A-Z0-9]{0,3}_[A-Za-z0-9_]*[A-Za-z0-9]\b"),
    "shp_uc1_5": re.compile(r"\b[A-Z][A-Z0-9]{0,5}_[A-Za-z0-9_]*[A-Za-z0-9]\b"),
    "shp_pfx16": re.compile(r"\b(?:R_|C_|U_|J_|D_|L_|Q_|TP_|LED_|FB_|BT_|CONN_|CHG_|SW_|VBUS_|PWR_)[A-Za-z0-9_]*"),
    "shp_pfx16s": re.compile(r"\b(?:R_|C_|U_|J_|D_|L_|Q_|TP_|LED_|FB_|BT_|CONN_|CHG_|SW_|VBUS_|PWR_)[A-Za-z0-9_]*[A-Za-z0-9]\b"),
    "shp_pfx10": re.compile(r"\b(?:R_|C_|U_|J_|D_|Q_|TP_|LED_|FB_|CONN_)[A-Za-z0-9_]*"),
    "shp_pfx8": re.compile(r"\b(?:R_|C_|U_|J_|D_|TP_)[A-Za-z0-9_]*"),
    "shp_pfx4": re.compile(r"\b(?:R_|C_|U_|J_)[A-Za-z0-9_]*"),
    "shp_any": re.compile(r"\b[A-Za-z]{1,5}_[A-Za-z0-9_]*\b"),
    "shp_uc2_": re.compile(r"\b[A-Z][A-Z0-9]*_[A-Z0-9_]*\b"),
    "shp_cap_pfx": re.compile(r"\b(?:R|C|U|J|D|L|Q|TP|LED|FB|BT|CONN|CHG|SW|VBUS|PWR)_[A-Za-z0-9_]*\b"),
    "shp_designator_like": re.compile(r"(?<![A-Za-z0-9_])[A-Z][A-Za-z0-9]*_[A-Za-z0-9_]*(?![A-Za-z0-9_])"),
}


def top_files():
    out = []
    for dp, dn, fns in os.walk(MECH):
        dn[:] = sorted(d for d in dn if d != "__pycache__")
        if dp != MECH:
            continue
        for fn in sorted(fns):
            if fn.endswith((".py", ".md")):
                out.append(os.path.join(dp, fn))
    return sorted(out)


files = top_files()
cache = {p: open(p, encoding="utf-8", errors="replace").read().splitlines() for p in files}

rows = []
for rname, rx in REGEXES.items():
    for scope in ("md+py", "md", "py"):
        sel = [p for p in files if (scope == "md+py" or p.endswith("." + scope))]
        per = {}
        for p in sel:
            rel = os.path.relpath(p, PROJ)
            occ = 0
            lnset = set()
            uniqpl = 0
            uniqfile = set()
            for i, line in enumerate(cache[p], 1):
                hits = rx.findall(line)
                if hits:
                    occ += len(hits)
                    lnset.add(i)
                    uniqpl += len(set(hits))
                    uniqfile |= set(hits)
            per[rel] = {"occ": occ, "ln": len(lnset), "uniqpl": uniqpl, "uniqfile": len(uniqfile)}
        for mname in ("occ", "ln", "uniqpl", "uniqfile"):
            tot = sum(v[mname] for v in per.values())
            got5 = [per.get(k, {}).get(mname, 0) for k, _ in MAIN_TOP5]
            score = sum(abs(a - b) for a, b in zip(got5, EXP5))
            rows.append((score, abs(tot - 571), rname, scope, mname, tot, got5))

rows.sort(key=lambda r: (r[0], r[1]))
print("★按「前5名绝对差之和」排序 · 目标 前5=[174,129,120,116,74] 合计=571")
print("%-6s %-8s %-14s %-7s %-9s %8s  %s" % ("score", "d571", "regex", "scope", "metric", "total", "top5"))
for score, d571, rname, scope, mname, tot, got5 in rows[:25]:
    print("%-6d %-8d %-14s %-7s %-9s %8d  %s" % (score, d571, rname, scope, mname, tot, got5))

print("")
print("★★ 反证: main 给的「合计 571」与「前5名 174/129/120/116/74」★逻辑上不可能同时成立 ★★")
print("   前5名之和 = %d  >  571  ⇒ 若前5名是同一口径的子集 ⇒ 总量至少 %d ⇒ ★571 必错★"
      % (sum(EXP5), sum(EXP5)))
print("   ⇒ main 的这两个数【必然不同口径】或【其中一个抄错】⇒ 本单【不猜】⇒ 交两套口径的实测数 + 差量表")
