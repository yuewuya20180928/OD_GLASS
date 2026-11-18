#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iss326_reconcile4.py —— 规则大扫: 找 main 的前5名向量 [174,129,120,116,74] 和合计 571 对应的口径"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
MECH = os.path.join(PROJ, "MECH")

uni = json.load(open(os.path.join(HERE, "mech_ref_universe.json"), encoding="utf-8"))["universe"]
REFS = sorted(uni.keys(), key=len, reverse=True)
EXACT = re.compile(r"(?<![A-Za-z0-9_])(?:" + "|".join(re.escape(r) for r in REFS) + r")(?![A-Za-z0-9_])")
EXACT_NOB = re.compile("(?:" + "|".join(re.escape(r) for r in REFS) + r")")
MOVE_SET = {r for r in REFS if uni[r]["move"] == "改名"}

CANDIDATES = {
    "C1_exact_wordboundary": EXACT,
    "C2_exact_noboundary": EXACT_NOB,
    "C3_shape_[A-Z]{1,4}_": re.compile(r"\b[A-Z]{1,4}_[A-Za-z0-9_]*[A-Za-z0-9]\b"),
    "C4_shape_[A-Z]{2,4}_": re.compile(r"\b[A-Z]{2,4}_[A-Za-z0-9_]*[A-Za-z0-9]\b"),
    "C5_shape_[A-Z]{1,4}_[A-Z0-9_]": re.compile(r"\b[A-Z]{1,4}_[A-Z0-9_]*[A-Z0-9]\b"),
    "C6_shape_prefix16": re.compile(r"\b(?:R_|C_|U_|J_|D_|L_|Q_|TP_|LED_|FB_|BT_|CONN_|CHG_|SW_|VBUS_|PWR_)[A-Za-z0-9_]*"),
    "C7_shape_prefix16_strict": re.compile(r"\b(?:R_|C_|U_|J_|D_|L_|Q_|TP_|LED_|FB_|BT_|CONN_|CHG_|SW_|VBUS_|PWR_)[A-Za-z0-9_]*[A-Za-z0-9]\b"),
    "C8_shape_anyCamel_": re.compile(r"\b[A-Za-z]{1,5}_[A-Za-z0-9_]*\b"),
    "C9_exact_moveonly": re.compile(r"(?<![A-Za-z0-9_])(?:" + "|".join(
        re.escape(r) for r in REFS if r in MOVE_SET) + r")(?![A-Za-z0-9_])"),
    "C10_shape_uc_only": re.compile(r"\b[A-Z][A-Z0-9]*_[A-Z0-9_]*[A-Z0-9]\b"),
    "C11_shape_uc_1to5": re.compile(r"\b[A-Z][A-Z0-9]{0,4}_[A-Za-z0-9_]*\b"),
}

MAIN_TOP5 = [
    ("MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md", 174),
    ("MECH/BOARD_ONEPASS_MECH_SYNC.md", 129),
    ("MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md", 120),
    ("MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md", 116),
    ("MECH/BOARD_ONEPASS_MECH_CLAIMS.md", 74),
]


def top_files(sub):
    out = []
    for dp, dn, fns in os.walk(MECH):
        dn[:] = sorted(d for d in dn if d != "__pycache__")
        if not sub and dp != MECH:
            continue
        for fn in sorted(fns):
            if fn.endswith((".py", ".md")):
                out.append(os.path.join(dp, fn))
    return sorted(out)


for sub, label in ((False, "顶层"), (True, "递归")):
    files = top_files(sub)
    # 缓存行
    cache = {p: open(p, encoding="utf-8", errors="replace").read().splitlines() for p in files}
    print("=" * 96)
    print("扫描面: %s   文件数=%d" % (label, len(files)))
    for cname, rx in CANDIDATES.items():
        per = {}
        tot = 0
        totln = 0
        for p in files:
            n = sum(len(rx.findall(l)) for l in cache[p])
            per[os.path.relpath(p, PROJ)] = n
            tot += n
            totln += sum(1 for l in cache[p] if rx.search(l))
        got5 = [per[k] for k, _ in MAIN_TOP5]
        exp5 = [v for _, v in MAIN_TOP5]
        ok = got5 == exp5
        print("  %-30s 合计=%6d 命中行=%6d 前5=%s %s" % (
            cname, tot, totln, got5, "★★完全对上★★" if ok else ""))
    print("  ★main 目标: 合计=571  前5=%s" % [v for _, v in MAIN_TOP5])
    print("  ★main 前5名合计 = %d  ⇒ ★若它同时是「总量」的子集 ⇒ 总量≥%d ⇒ 571 与前5名【自相矛盾】★"
          % (sum(v for _, v in MAIN_TOP5), sum(v for _, v in MAIN_TOP5)))
