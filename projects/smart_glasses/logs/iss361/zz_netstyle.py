#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-361 侦察 6: 网表节点串风格 (bare vs 具名 pin) + 158 桶的脚数构成 + 候选封装脚数兼容性"""
import csv, os, re, json, sys

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
recon = json.load(open(os.path.join(ROOT, "logs/iss361/04_recon.json")))
c4 = recon["c4"]
ph = recon["ph_pins"]

rows = list(csv.DictReader(open(os.path.join(ROOT, "HW", "netlist_v1.csv"), encoding="utf-8")))
rows = [r for r in rows if (r.get("board") or "MAIN_PCB").strip() == "MAIN_PCB"]

G13 = ["CHG_GND_STAR", "D_ESD_CAM", "D_ESD_DEMO", "D_ESD_USB_D", "FB_DEMO", "Q_AND",
       "Q_ENVC", "Q_PG", "SW_BOOT", "SW_KEY_PWR", "SW_KEY_VM", "SW_KEY_VP", "SW_RST"]

print("=== 13 件在网表里的节点串原文 (bare ⇒ 占位脚号根因) ===")
for ref in G13:
    print("\n-- %s" % ref)
    for r in rows:
        n1 = (r.get("node1") or "").strip()
        n2 = (r.get("node2") or "").strip()
        for nm, v in (("node1", n1), ("node2", n2)):
            if v == ref or v.startswith(ref + " "):
                style = "bare(占位)" if v == ref else "具名:" + v.split(" ", 1)[1]
                print("     %-6s %-28s net=%-20s ⇒ %s" % (nm, v, r["net"], style))

print("\n\n=== 158 桶里: 占位脚号件数分布 (脚数 → 件数) ===")
from collections import Counter
cnt = Counter(ph.values())
for n in sorted(cnt):
    print("   %d 脚: %d 件" % (n, cnt[n]))
print("   合计 = %d" % sum(cnt.values()))

print("\n=== 158 桶里各 ref 的网表节点是否全 bare ===")
bym = {}
for r in rows:
    net = (r.get("net") or "").strip()
    for k in ("node1", "node2"):
        v = (r.get(k) or "").strip()
        m = re.match(r"^([A-Za-z_0-9]+)\s*(.*)$", v)
        if not m:
            continue
        comp, tail = m.group(1), m.group(2).strip()
        if comp in c4:
            bym.setdefault(comp, []).append((tail, net))
named = {c: v for c, v in bym.items() if any(t for t, _ in v)}
print("   158 桶中带【具名脚】的 ref 数 = %d" % len(named))
if named:
    for c in sorted(named)[:10]:
        print("      %-16s %s" % (c, named[c][:3]))

print("\n=== 13 件的网表脚数 (pins csv) vs 候选封装脚数 ===")
pins = list(csv.DictReader(open(os.path.join(ROOT, "HW", "netlist_v1_pins.csv"), encoding="utf-8")))
pc = Counter(p["ref"] for p in pins)
CAND = {
    "CHG_GND_STAR": ("TestPoint", "TestPoint_Pad_D1.0mm", 1),
    "D_ESD_CAM":    ("Package_SON", "Texas_DPY0002A_0.6x1mm_P0.65mm", 2),
    "D_ESD_DEMO":   ("Diode_SMD", "D_SOD-323", 2),
    "D_ESD_USB_D":  ("Package_SON", "Texas_DPY0002A_0.6x1mm_P0.65mm", 2),
    "FB_DEMO":      ("Inductor_SMD", "L_0805_2012Metric", 2),
    "Q_AND":        ("Package_TO_SOT_SMD", "SOT-23", 3),
    "Q_ENVC":       ("Package_TO_SOT_SMD", "SOT-23", 3),
    "Q_PG":         ("Package_TO_SOT_SMD", "SOT-23", 3),
    "SW_BOOT":      ("Button_Switch_SMD", "SW_SPST_CK_KXT3", 2),
    "SW_KEY_PWR":   ("Button_Switch_SMD", "SW_SPST_CK_KXT3", 2),
    "SW_KEY_VM":    ("Button_Switch_SMD", "SW_SPST_CK_KXT3", 2),
    "SW_KEY_VP":    ("Button_Switch_SMD", "SW_SPST_CK_KXT3", 2),
    "SW_RST":       ("Button_Switch_SMD", "SW_SPST_CK_KXT3", 2),
}
for ref in G13:
    c = CAND[ref]
    print("  %-14s 网表脚=%d  候选 %s:%s 脚数=%d  ⇒ %s"
          % (ref, pc.get(ref, 0), c[0], c[1], c[2],
             "一致" if pc.get(ref, 0) == c[2] else "★不一致★"))
