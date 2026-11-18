#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-322 · tmp 沙盒脚本 · ★★高速腿 (DSI/CSI) 几何可布性判定 ★★
------------------------------------------------------------------
输入 (全部现役探针 + 板本体, ★不许抄文档★):
  · /tmp/_pcb_drc_demo_mainboard.kicad_pcb.json   ← state/check_pcb_drc.py
  · tmp/iss322/escape_feas_current.txt            ← state/probe_escape_feasibility.py
  · tmp/iss322/lane_conflicts_current.txt         ← state/probe_lane_conflicts.py
  · tmp/iss322/unc_worklist_current.txt           ← state/probe_unconnected_worklist_v2.py
输出:
  · tmp/iss322/hs_geometry.json  (机读)
  · tmp/iss322/hs_geometry.md    (交卷页直接用)
"""
import json, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))

DRC = "/tmp/_pcb_drc_demo_mainboard.kicad_pcb.json"
d = json.load(open(DRC, encoding="utf-8"))
unc = d.get("unconnected_items") or []
assert len(unc) == 45


def net_of(it):
    m = re.search(r"\[([^\]]+)\]", it["description"])
    return m.group(1) if m else "?"


HS = [u for u in unc if net_of(u["items"][0]).startswith(("DSI_", "CSI_"))]
assert len(HS) == 23, len(HS)

# ── 1. 高速腿逐条: 网名 / 两端 / 类型 ──
hs_rows = []
for u in HS:
    a, b = u["items"]
    hs_rows.append(dict(
        net=net_of(a),
        a_ref=(re.search(r"of (\S+) on", a["description"]) or [None, None])[1],
        a_pad=(re.search(r"^Pad (\S+) ", a["description"]) or [None, None])[1],
        a_x=a["pos"]["x"], a_y=a["pos"]["y"], a_dsc=a["description"],
        b_ref=(re.search(r"of (\S+) on", b["description"]) or [None, None])[1],
        b_pad=(re.search(r"^Pad (\S+) ", b["description"]) or [None, None])[1],
        b_x=b["pos"]["x"], b_y=b["pos"]["y"], b_dsc=b["description"],
    ))

# ── 2. escape feasibility: 逐端点读数 ──
esc = open(os.path.join(HERE, "escape_feas_current.txt"), encoding="utf-8").read()
esc_feas = re.findall(r"W=([\d.]+) ⇒ 物理可行 (\d+) / 物理不可能 (\d+)", esc)
esc_summary = [dict(w=float(w), feas=int(a), imposs=int(b)) for w, a, b in esc_feas]
# 逐端点: 记录最优方向 + 余量
ep_margin = collections.defaultdict(dict)
for m in re.finditer(
        r"── (\S+) @ (\S+) \(([-\d.]+), ([-\d.]+)\).*?\n"
        r"\s+★W=0\.20 ([^=]+?) ⇒ 余量 ([-+]?[\d.]+)mm.*?\n"
        r"\s+★W=0\.15 ([^=]+?) ⇒ 余量 ([-+]?[\d.]+)mm",
        esc):
    ep_margin[m.group(1)][m.group(2)] = dict(
        x=float(m.group(3)), y=float(m.group(4)),
        w20_dir=m.group(5).strip(), w20_margin=float(m.group(6)),
        w15_dir=m.group(7).strip(), w15_margin=float(m.group(8)))

# ── 3. lane conflicts: 走廊横穿表 ──
lc = open(os.path.join(HERE, "lane_conflicts_current.txt"), encoding="utf-8").read()
lane = []
for ln in lc.splitlines():
    m = re.match(r"^(\S+)\s+(\S+)\s+(\S+)\s+([\d.]+)\s+(.+?)\s+(★挪 3mm 内无解|[\d.]+mm .)$", ln)
    if m:
        lane.append(dict(net=m.group(1), pa=m.group(2), pb=m.group(3),
                         length=float(m.group(4)), crossers=m.group(5).strip(),
                         fix=m.group(6).strip()))
lane_by_net = collections.defaultdict(list)
for r in lane:
    lane_by_net[r["net"]].append(r)

# ── 4. 每条高速腿的走廊横穿者, 分类: 是不是【同族差分腿】互掐 ──
HS_FAMILY = set()


def family(net):
    """DSI_D0_D1_P → DSI_D0_D1 ; CSI_D0_D2_N_SRC → CSI_D0_D2"""
    for suf in ("_P_SRC", "_N_SRC", "_P", "_N"):
        if net.endswith(suf):
            return net[: -len(suf)]
    return net


for r in hs_rows:
    r["family"] = family(r["net"])
    HS_FAMILY.add(r["family"])

for r in hs_rows:
    crossers = set()
    for L in lane_by_net.get(r["net"], []):
        for c in L["crossers"].split(","):
            c = c.strip()
            if c:
                crossers.add(c)
    r["corridor_crossers"] = sorted(crossers)
    r["crossers_same_family"] = sorted(c for c in crossers if family(c) == r["family"])
    r["crossers_other_hs"] = sorted(c for c in crossers
                                    if c.startswith(("DSI_", "CSI_")) and family(c) != r["family"])
    r["crossers_non_hs"] = sorted(c for c in crossers
                                  if not c.startswith(("DSI_", "CSI_")))
    r["lane_nosolution"] = [L["fix"] for L in lane_by_net.get(r["net"], [])
                            if "无解" in L["fix"]]

# ── 5. 出脚余量汇总 (按端点) ──
worst20 = []
for r in hs_rows:
    for side in ("a", "b"):
        ref = r[side + "_ref"]
        pad = r[side + "_pad"]
        key = "%s.%s" % (ref, pad) if pad else None
        e = ep_margin.get(r["net"], {}).get(key)
        if e is None:
            # 走线端 / 过孔端: 用最近的同网条目近似
            continue
        worst20.append((e["w20_margin"], r["net"], key, e["w20_dir"], e["w15_margin"]))
worst20.sort()

# ── 6. 结论 ──
hs_families = sorted(HS_FAMILY)
n_same = sum(1 for r in hs_rows if r["crossers_same_family"])
n_other_hs = sum(1 for r in hs_rows if r["crossers_other_hs"])
n_nonhs = sum(1 for r in hs_rows if r["crossers_non_hs"])
n_lane_nosol = sum(1 for r in hs_rows if r["lane_nosolution"])

out = dict(
    n_hs_items=len(hs_rows),
    n_hs_nets=len(set(r["net"] for r in hs_rows)),
    n_hs_families=len(hs_families),
    hs_families=hs_families,
    dsi_nets=sorted(set(r["net"] for r in hs_rows if r["net"].startswith("DSI_"))),
    csi_nets=sorted(set(r["net"] for r in hs_rows if r["net"].startswith("CSI_"))),
    escape_summary=esc_summary,
    n_endpoints_total=len(ep_margin),
    hs_items_blocked_by_same_family=n_same,
    hs_items_blocked_by_other_hs=n_other_hs,
    hs_items_blocked_by_non_hs=n_nonhs,
    hs_items_with_lane_nosolution=n_lane_nosol,
    worst_escape_margins=[dict(margin=m, net=n, ep=k, dir=d, w15=w15)
                          for m, n, k, d, w15 in worst20[:12]],
    rows=hs_rows,
)
json.dump(out, open(os.path.join(HERE, "hs_geometry.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("高速腿 unc 条目 = %d  (DSI/CSI 合计)" % len(hs_rows))
print("  高速网名 = %d  · 差分族(family) = %d" % (out["n_hs_nets"], out["n_hs_families"]))
print("  DSI_ 网名数 = %d   CSI_ 网名数 = %d"
      % (len(out["dsi_nets"]), len(out["csi_nets"])))
print()
print("── 出脚可行性 (probe_escape_feasibility, 88 端点) ──")
for s in esc_summary:
    print("  W=%s ⇒ 可行 %s / 不可能 %s" % (s["w"], s["feas"], s["imposs"]))
print()
print("── 走廊横穿 (probe_lane_conflicts) ──")
print("  被同族差分腿横穿的高速腿条数 = %d" % n_same)
print("  被异族高速腿横穿的高速腿条数 = %d" % n_other_hs)
print("  被非高速网横穿的高速腿条数   = %d" % n_nonhs)
print("  直走廊 3mm 内挪不动的条数    = %d" % n_lane_nosol)
print()
print("── 高速腿出脚余量最紧的 12 个端点 ──")
for m, n, k, dd, w15 in worst20[:12]:
    print("   %+7.3fmm  W0.15 %+7.3fmm  %-18s %-22s %s" % (m, w15, n, k, dd))
print()
print("── 逐条 ──")
for r in hs_rows:
    print("%-18s fam=%-14s 同族横穿=%-2d 异族HS=%-2d 非HS=%-2d 无解走廊=%d"
          % (r["net"], r["family"], len(r["crossers_same_family"]),
             len(r["crossers_other_hs"]), len(r["crossers_non_hs"]),
             len(r["lane_nosolution"])))
    if r["crossers_same_family"]:
        print("      同族横穿者:", r["crossers_same_family"])
    if r["crossers_other_hs"]:
        print("      异族HS横穿者:", r["crossers_other_hs"])
    if r["crossers_non_hs"]:
        print("      非HS横穿者:", r["crossers_non_hs"])
