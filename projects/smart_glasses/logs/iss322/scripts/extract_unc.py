#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISS-322 · tmp 沙盒脚本 · 45 条 unconnected 逐条提取 (★机器搬·不许手抄★)

数据源: /tmp/_pcb_drc_demo_mainboard.kicad_pcb.json  (由 state/check_pcb_drc.py 生成, rc=0)
输出:   tmp/iss322/unc45.json  (★45 条·每条 8 列原始数据★)
        tmp/iss322/unc45.md    (markdown 表 · 直接抄进交卷页)
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
DRC = "/tmp/_pcb_drc_demo_mainboard.kicad_pcb.json"
PCB = os.path.join(PROJ, "HW", "PCB", "demo_mainboard.kicad_pcb")
OFF = os.path.join(PROJ, "state", "official_18092_unc.drc.json")

d = json.load(open(DRC, encoding="utf-8"))
unc = d.get("unconnected_items") or []
assert len(unc) == 45, "unconnected count != 45: %d" % len(unc)

# ---- 板面/层数实读 (★从板文件本体取, 不抄文档★) ----
txt = open(PCB, encoding="utf-8").read()
edge = [(float(a), float(b), float(c), float(d_)) for a, b, c, d_ in
        re.findall(r'\(gr_line\s*\n\s*\(start ([-\d.]+) ([-\d.]+)\)\s*\n\s*\(end ([-\d.]+) ([-\d.]+)\)', txt)]
xs = [v for e in edge for v in (e[0], e[2])]
ys = [v for e in edge for v in (e[1], e[3])]
BOARD_W, BOARD_H = max(xs) - min(xs), max(ys) - min(ys)
cu_layers = re.findall(r'\((\d+) "([^"]+)" (signal|power|user|mixed)', txt)
cu_layers = [(int(a), b) for a, b, c in cu_layers if b.endswith(".Cu")]
N_CU = len(cu_layers)

# ---- 解析 description: 'Pad 14 [NET] of REF on F.Cu' / 'Track [NET] on In2.Cu, length 0.2500 mm' ----
PAD_RE = re.compile(r'^Pad ([\w.\-]+) \[([^\]]*)\] of ([A-Za-z0-9_]+) on ([\w.]+)$')
TRK_RE = re.compile(r'^Track \[([^\]]*)\] on ([\w.]+), length ([\d.]+) mm$')
VIA_RE = re.compile(r'^Via \[([^\]]*)\] at .* on ([\w.]+)$')
ZONE_RE = re.compile(r'^Zone net \[([^\]]*)\]$')


def parse_item(it):
    dsc = it["description"]
    p = it.get("pos") or {}
    x, y = p.get("x"), p.get("y")
    m = PAD_RE.match(dsc)
    if m:
        return dict(kind="pad", pad=m.group(1), net=m.group(2), ref=m.group(3),
                    layer=m.group(4), x=x, y=y, length=None, dsc=dsc)
    m = TRK_RE.match(dsc)
    if m:
        return dict(kind="track", pad=None, net=m.group(1), ref=None,
                    layer=m.group(2), x=x, y=y, length=float(m.group(3)), dsc=dsc)
    m = VIA_RE.match(dsc)
    if m:
        return dict(kind="via", pad=None, net=m.group(1), ref=None,
                    layer=m.group(2), x=x, y=y, length=None, dsc=dsc)
    return dict(kind="other", pad=None, net=None, ref=None, layer=None,
                x=x, y=y, length=None, dsc=dsc)


def net_of(it):
    q = parse_item(it)
    if q["net"]:
        return q["net"]
    # fallback: description 里抓 [..]
    m = re.search(r'\[([^\]]+)\]', it["description"])
    return m.group(1) if m else "?"


rows = []
for idx, u in enumerate(unc, 1):
    its = u["items"]
    a = parse_item(its[0])
    b = parse_item(its[1])
    net = net_of(its[0]) or net_of(its[1])
    # 长度: 优先取 track 自带 length; 否则两点欧氏距
    L = None
    for q in (a, b):
        if q["length"] is not None:
            L = q["length"]
            break
    if L is None and a["x"] is not None and b["x"] is not None:
        L = round(math.hypot(a["x"] - b["x"], a["y"] - b["y"]), 4)
    rows.append(dict(
        idx=idx, net=net,
        a=a, b=b, length=L,
        a_dsc=a["dsc"], b_dsc=b["dsc"],
        sev=u.get("severity"),
    ))

# ---- 高速腿分类 (★口径写死在本脚本里, 交卷页必须逐字引用★) ----
HS_PREFIX = ("DSI_", "CSI_", "MIPI_")


def is_hs(net):
    return any(net.startswith(p) for p in HS_PREFIX)


for r in rows:
    r["hs"] = is_hs(r["net"])

# ---- 官方板 (18092) 对照: net-pair 集合 ----
off = json.load(open(OFF, encoding="utf-8"))
off_unc = off.get("unconnected_items") or []


def netpair(u):
    a, b = net_of(u["items"][0]), net_of(u["items"][1])
    return tuple(sorted([a, b]))


cur_pairs = {}
for r in rows:
    cur_pairs.setdefault((r["net"], r["net"]), 0)
off_pairs = {}
for u in off_unc:
    p = netpair(u)
    off_pairs[p] = off_pairs.get(p, 0) + 1

# 每条 unc 的 net pair: 两条 item 的 net 必须一致 (单网断线)
for r in rows:
    pair = tuple(sorted([net_of(r["a"] and {"description": r["a_dsc"], "pos": {"x": r["a"]["x"], "y": r["a"]["y"]}}),
                         net_of(r["b"] and {"description": r["b_dsc"], "pos": {"x": r["b"]["x"], "y": r["b"]["y"]}})]))
    r["net_pair"] = pair

cur_pair_set = set(r["net_pair"] for r in rows)
off_pair_set = set(off_pairs)

out = dict(
    board_md5_note="run md5sum separately",
    board_w=BOARD_W, board_h=BOARD_H, n_cu_layers=N_CU, cu_layers=cu_layers,
    total=len(rows),
    hs_count=sum(1 for r in rows if r["hs"]),
    hs_nets=sorted(set(r["net"] for r in rows if r["hs"])),
    hs_net_count=len(set(r["net"] for r in rows if r["hs"])),
    non_hs_count=sum(1 for r in rows if not r["hs"]),
    non_hs_nets=sorted(set(r["net"] for r in rows if not r["hs"])),
    official_total=len(off_unc),
    official_pair_in_current=len(cur_pair_set & off_pair_set),
    official_pair_only=sorted(off_pair_set - cur_pair_set),
    official_pair_current_only=sorted(cur_pair_set - off_pair_set),
    rows=rows,
)
json.dump(out, open(os.path.join(HERE, "unc45.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# ---- 摘要打印 ----
print("BOARD %gx%g mm  cu_layers=%d %s" % (BOARD_W, BOARD_H, N_CU, cu_layers))
print("TOTAL unc = %d" % len(rows))
print("HS (DSI_/CSI_/MIPI_ prefix) unc items = %d   distinct HS nets = %d"
      % (out["hs_count"], out["hs_net_count"]))
print("HS NETS:", out["hs_nets"])
print("non-HS unc items = %d   distinct nets = %d" % (out["non_hs_count"], len(out["non_hs_nets"])))
print("NON-HS NETS:", out["non_hs_nets"])
print("OFFICIAL unc = %d ; net-pairs shared with current = %d ; off-only = %s ; cur-only = %s"
      % (out["official_total"], out["official_pair_in_current"],
         out["official_pair_only"], out["official_pair_current_only"]))
print()
print("=== per-item ===")
for r in rows:
    print("%2d | %-22s | %-38s -> %-38s | L=%-8s | %s"
          % (r["idx"], r["net"], r["a_dsc"][:38], r["b_dsc"][:38], r["length"],
             "HS" if r["hs"] else ""))
