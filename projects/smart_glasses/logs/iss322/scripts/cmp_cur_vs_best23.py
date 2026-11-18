#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-322 · tmp 沙盒脚本 · ★★"我们的 45 条" vs "盘上最好的板" 逐网集合比对★★
★回答: 我们这 45 条里, 有多少条【别的板已经布通过】⇒ ⇒ 是不是"几何不可能"★"""
import json, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
CUR = "/tmp/_pcb_drc_demo_mainboard.kicad_pcb.json"
BEST = "state/.lastgood/best_unc23_clrfix.kicad_pcb.drc.json"


def nets(path):
    d = json.load(open(path, encoding="utf-8"))
    c = collections.Counter()
    for u in d.get("unconnected_items") or []:
        for it in u["items"]:
            m = re.search(r"\[([^\]]+)\]", it["description"])
            if m:
                c[m.group(1)] += 1
                break
    return c, len(d.get("unconnected_items") or [])


cur, cur_n = nets(CUR)
bst, bst_n = nets(BEST)
print("现役板 : unc 条目 %d · 网名 %d" % (cur_n, len(cur)))
print("best_unc23 板 : unc 条目 %d · 网名 %d" % (bst_n, len(bst)))
print()

HS = lambda n: n.startswith(("DSI_", "CSI_"))

cur_s, bst_s = set(cur), set(bst)
routed_by_best = sorted(cur_s - bst_s)          # ★我们的 unc, 但 best_unc23 布通了★
still_unc_in_best = sorted(cur_s & bst_s)        # ★两边都没布通★
only_in_best = sorted(bst_s - cur_s)             # ★best_unc23 自己新欠的债★

print("★我们这 43 个未连通网名里:")
print("  ├─ 【best_unc23 板已经布通】 = %d 个  ⇒ ⇒ 这些【不是几何不可能】" % len(routed_by_best))
print("  └─ 【best_unc23 板也没布通】 = %d 个  ⇒ ⇒ 这些是【真·硬骨头】" % len(still_unc_in_best))
print()
for tag, lst in (("已布通", routed_by_best), ("两边都未通", still_unc_in_best)):
    h = [n for n in lst if HS(n)]
    o = [n for n in lst if not HS(n)]
    print("── %s (高速 %d / 非高速 %d) ──" % (tag, len(h), len(o)))
    print("   高速:", h)
    print("   非高速:", o)
print()
print("── best_unc23 板自己新欠的债 (%d) ──" % len(only_in_best))
print("  ", only_in_best)
print()
n_hs_routed = sum(1 for n in routed_by_best if HS(n))
n_nhs_routed = sum(1 for n in routed_by_best if not HS(n))
out = dict(cur_unc_items=cur_n, cur_nets=len(cur), best_unc_items=bst_n, best_nets=len(bst),
           routed_by_best=routed_by_best, still_unc_in_best=still_unc_in_best,
           only_in_best=only_in_best,
           n_routed_by_best=len(routed_by_best), n_still=len(still_unc_in_best),
           n_hs_routed_by_best=n_hs_routed, n_nhs_routed_by_best=n_nhs_routed)
json.dump(out, open(os.path.join(HERE, "cur_vs_best23.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("⇒ 量化: 我们 43 个未连通网名中 %d 个已被别的板布通 (高速 %d / 非高速 %d); %d 个两边都没通"
      % (len(routed_by_best), n_hs_routed, n_nhs_routed, len(still_unc_in_best)))
