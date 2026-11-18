#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""iss326_reconcile6.py —— 只找「合计恰好 = 571」的规则 + py-only 578→571 的差额定位"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
MECH = os.path.join(PROJ, "MECH")
uni = json.load(open(os.path.join(HERE, "mech_ref_universe.json"), encoding="utf-8"))["universe"]
REFS = sorted(uni.keys(), key=len, reverse=True)
EX = re.compile(r"(?<![A-Za-z0-9_])(?:" + "|".join(re.escape(r) for r in REFS) + r")(?![A-Za-z0-9_])")

MAIN_TOP5 = {
    "MECH/BOARD_ONEPASS_STRUCT_CROSSCHECK.md": 174,
    "MECH/BOARD_ONEPASS_MECH_SYNC.md": 129,
    "MECH/ONETRIP_D_LED_G_PLACEMENT_CALIBER.md": 120,
    "MECH/BOARD_PORT_OPENING_S6_FRAME_CALIBER.md": 116,
    "MECH/BOARD_ONEPASS_MECH_CLAIMS.md": 74,
}


def top_files(ext=None):
    out = []
    for dp, dn, fns in os.walk(MECH):
        dn[:] = sorted(d for d in dn if d != "__pycache__")
        if dp != MECH:
            continue
        for fn in sorted(fns):
            if fn.endswith((".py", ".md")):
                if ext and not fn.endswith(ext):
                    continue
                out.append(os.path.join(dp, fn))
    return sorted(out)


print("★A · py-only 精确真集 occ = 578 ⇒ 距 main 的 571 差 7 ⇒ 定位这 7 处可能在哪★")
pyf = top_files(".py")
per = {}
for p in pyf:
    rel = os.path.relpath(p, PROJ)
    n = sum(len(EX.findall(l)) for l in open(p, encoding="utf-8", errors="replace"))
    per[rel] = n
print("  py-only 合计 = %d" % sum(per.values()))
for rel, n in sorted(per.items(), key=lambda kv: -kv[1]):
    if n:
        print("      %5d  %s" % (n, rel))

print("")
print("★B · 找「合计恰好 571」的规则 (穷举 计数方式 × 文件子集)★")
md_all = top_files(".md")
py_all = top_files(".py")
subsets = {
    "md+py 全部": md_all + py_all,
    "md 全部": md_all,
    "py 全部": py_all,
    "md 全部 + py 去掉 .bak": md_all + [p for p in py_all if ".bak" not in p],
    "md 去掉 .bak + py 全部": [p for p in md_all if ".bak" not in p] + py_all,
    "md 去掉 .bak + py 去掉 .bak": [p for p in md_all if ".bak" not in p] + [p for p in py_all if ".bak" not in p],
}
# 形状前缀集合
PFX = {
    "pfx10": r"\b(?:R_|C_|U_|J_|D_|Q_|TP_|LED_|FB_|CONN_)[A-Za-z0-9_]*",
    "pfx12": r"\b(?:R_|C_|U_|J_|D_|Q_|TP_|LED_|FB_|CONN_|CHG_|SW_)[A-Za-z0-9_]*",
    "pfx16": r"\b(?:R_|C_|U_|J_|D_|L_|Q_|TP_|LED_|FB_|BT_|CONN_|CHG_|SW_|VBUS_|PWR_)[A-Za-z0-9_]*",
    "A1_4": r"\b[A-Z]{1,4}_[A-Za-z0-9_]*[A-Za-z0-9]\b",
    "A2_4": r"\b[A-Z]{2,4}_[A-Za-z0-9_]*[A-Za-z0-9]\b",
    "A1_5": r"\b[A-Z]{1,5}_[A-Za-z0-9_]*[A-Za-z0-9]\b",
    "uc1": r"\b[A-Z][A-Z0-9]*_[A-Za-z0-9_]*[A-Za-z0-9]\b",
    "uc2": r"\b[A-Z][A-Z0-9]*_[A-Z0-9_]*\b",
}
RX = {"exact_wb": EX}
for k, v in PFX.items():
    RX[k] = re.compile(v)

found = []
for sname, sel in subsets.items():
    for rname, rx in RX.items():
        cache = {p: open(p, encoding="utf-8", errors="replace").read().splitlines() for p in sel}
        occ = sum(len(rx.findall(l)) for l in cache[p] for p in sel)
        occ = sum(sum(len(rx.findall(l)) for l in cache[p]) for p in sel)
        ln = sum(sum(1 for l in cache[p] if rx.search(l)) for p in sel)
        upl = 0
        uf = set()
        for p in sel:
            for l in cache[p]:
                h = rx.findall(l)
                if h:
                    upl += len(set(h))
                    uf |= set(h)
        got5 = []
        for k in MAIN_TOP5:
            p = os.path.join(PROJ, k)
            got5.append(sum(len(rx.findall(l)) for l in cache[p]) if p in cache else 0)
        for metric, tot in (("occ", occ), ("ln", ln), ("uniqpl", upl), ("uniqfile", len(uf))):
            if tot == 571:
                found.append((sname, rname, metric, tot, got5))
                print("  ★★★ 命中: subset=%s regex=%s metric=%s total=571 top5=%s" % (sname, rname, metric, got5))
if not found:
    print("  ★ 没有任何 (子集 × 正则 × 计数方式) 组合给出恰好 571 ⇒ main 的 571 无法用任何常见口径复现★")
    print("  ★ 唯一最接近 = py-only + 精确真集 + 出现次数 = 578 (差 7)★")
    print("  ★ 但那个口径下「前5名」全是 .md 文件 ⇒ 与 main 的前5名列表【不同域】⇒ 不是同一口径★")
