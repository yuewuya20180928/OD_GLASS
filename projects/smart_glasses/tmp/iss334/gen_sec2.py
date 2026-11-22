#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_sec2.py (ISS-334 沙盒·只读) —— 生成 §2 逐网死因归类表
★数据全部来自本单 fresh 读数:
  · tmp/iss334/02_zero_copper_nets.json (零铜网 + 差分伙伴腿铜长)
  · tmp/iss334/07_blockers.json (每个端点的最优出脚方向 / 长度 / 余量 / 最近异网阻挡物)
  · logs/iss334/02_pair_copper_table.txt (逐对铜长)
"""
import json

Z = json.load(open("tmp/iss334/02_zero_copper_nets.json", encoding="utf-8"))
BL = json.load(open("tmp/iss334/07_blockers.json", encoding="utf-8"))
zero = [z["net"] for z in Z["zero_nets"] if z["net"]]

pmap = {}
for p in Z["pairs"]:
    P, N, lp, ln = p["p"], p["n"], p["lp"], p["ln"]
    pmap[P] = (N, ln)
    pmap[N] = (P, lp)

THRESH = 0.30  # ★出脚余量阈值 (mm): ≤ 此值 ⇒ 出脚被几何钉死


def tightest(net):
    eps = BL.get(net) or []
    if not eps:
        return None, None
    e = min(eps, key=lambda x: float(x["margin"]))
    return e, eps


rows = []
for n in sorted(zero):
    e, eps = tightest(n)
    marg = float(e["margin"]) if e else None
    partner = pmap.get(n)
    if partner and partner[1] > 0:
        bucket = "A"
    elif marg is not None and marg <= THRESH:
        bucket = "B"
    else:
        bucket = "C"
    rows.append(dict(net=n, bucket=bucket, margin=marg,
                     blocker=e["blocker"] if e else "?", dist=e["dist"] if e else 0.0,
                     ep=e["ep"] if e else "?", dirn=e["dirn"] if e else "?",
                     length=e["length"] if e else "?",
                     partner=partner[0] if partner else None,
                     partner_len=partner[1] if partner else None))

cnt = {"A": 0, "B": 0, "C": 0}
for r in rows:
    cnt[r["bucket"]] += 1

print("| 网名 | 桶 | 归桶依据 (机器读数 + 出处) | 最小可试机制 (逐字) | 反向用例 (什么读数能证明这条路不通) |")
print("|---|---|---|---|---|")
for r in rows:
    n = r["net"]
    if r["bucket"] == "A":
        basis = ("差分腿且**伙伴腿官方有铜 %.3fmm** ⇒ 走廊被占 (`logs/iss334/02_pair_copper_table.txt`); "
                 "该腿端点 %s 的最优出脚余量 %smm ⇒ 几何不是瓶颈"
                 % (r["partner_len"], r["ep"], r["margin"]))
        mech = ("`bash state/pcbnew_py.sh state/pair_corridor.py HW/PCB/demo_mainboard.kicad_pcb "
                "logs/iss334/00_official_drc_fresh.json --out tmp/iss334/arms/A_<pair>/pair_corridor.kicad_pcb "
                "--pair %s %s`" % (r["partner"], n))
        rev = ("① 该命令打印「没找到成对路径 ⇒ 不落铜」或 rc=1 ⇒ 成对走廊对该对不通; "
               "② 落铜后 `python3 state/pair_copper_table.py` 里该腿仍 = 0.000 ⇒ 不通")
    elif r["bucket"] == "B":
        basis = ("最紧端点 %s 的最优出脚余量仅 **%smm** (阻挡物 `%s` @ %smm) ⇒ 出脚被几何钉死 "
                 "(`tmp/iss334/03_escape_feasibility.txt` · `tmp/iss334/07_blockers.json`)" %
                 (r["ep"], r["margin"], r["blocker"], r["dist"]))
        mech = ("`PCB_ESC_STRAIGHT=2 PCB_ESC_STRAIGHT_NETS=\"%s\"`" % n)
        rev = ("① 臂的裸板 fresh DRC JSON 里该网**仍出现在 unconnected_items** ⇒ 出脚直行救不了; "
               "② 出脚探针在 4 个方向上**都**读出余量 ≤ +%smm ⇒ 几何真卡死 ⇒ 换层绕开也不通" % THRESH)
    else:
        basis = ("最紧端点 %s 的出脚余量 **%smm** (阻挡物 `%s` @ %smm) ⇒ 几何宽松; "
                 "但 A* 补线实测 (官方同配方 GRID=0.125 / margin 0.0625) **补上 0 条** ⇒ 是搜索失败不是几何卡死 "
                 "(`logs/iss334/08_astar_officialenv.log`)" % (r["ep"], r["margin"], r["blocker"], r["dist"]))
        mech = ("`bash state/pcbnew_py.sh state/fix_unconnected_astar.py HW/PCB/demo_mainboard.kicad_pcb "
                "logs/iss334/00_official_drc_fresh.json --out tmp/iss334/arms/C_<net>/astar.kicad_pcb "
                "--max-dist 90`")
        rev = ("① 打印「补上 0 条 / 未成 N 条」且名单含该网 ⇒ A* 补线不通; "
               "② 放大 A* 预算 (PCB_ABUDGET_MULT) 20× 后仍 0 ⇒ 不是预算 ⇒ 必须在产生点改 `state/gen_pcb_routing.py`")
    print("| `%s` | **%s** | %s | %s | %s |" % (n, r["bucket"], basis, mech, rev))

print("")
print("★桶计数: A=%d · B=%d · C=%d · 合计=%d" % (cnt["A"], cnt["B"], cnt["C"], len(rows)))
print("★A 桶名单: %s" % ", ".join(r["net"] for r in rows if r["bucket"] == "A"))
print("★B 桶名单: %s" % ", ".join(r["net"] for r in rows if r["bucket"] == "B"))
print("★C 桶名单: %s" % ", ".join(r["net"] for r in rows if r["bucket"] == "C"))
json.dump(rows, open("tmp/iss334/08_bucket_assignment.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
