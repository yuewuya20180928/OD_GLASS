#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-361 侦察 4: 候选封装 fab/courtyard 实存尺寸 + 13 件网表脚↔net 逐脚 + FP_TRUTH 命中复查"""
import os, re, hashlib, csv, sys

LR = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"

def outline(path, layer):
    txt = open(path, encoding="utf-8").read()
    xs, ys = [], []
    # fp_rect
    for m in re.finditer(r'\(fp_rect\s*\(start ([-\d\. ]+)\)\s*\(end ([-\d\. ]+)\)\s*\(layer "%s"\)' % re.escape(layer), txt):
        for grp in (1, 2):
            v = [float(x) for x in m.group(grp).split()]
            xs.append(v[0]); ys.append(v[1])
    for m in re.finditer(r'\(fp_line\s*\(start ([-\d\. ]+)\)\s*\(end ([-\d\. ]+)\)\s*\(layer "%s"\)' % re.escape(layer), txt):
        for grp in (1, 2):
            v = [float(x) for x in m.group(grp).split()]
            xs.append(v[0]); ys.append(v[1])
    if not xs:
        return None
    return (max(xs)-min(xs), max(ys)-min(ys))

def pads_of(path):
    txt = open(path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r'\(pad\s+"([^"]*)"\s+(\w+)\s+(\w+)\s*\(at ([^)]*)\)\s*\(size ([^)]*)\)', txt):
        at = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", m.group(4))]
        sz = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", m.group(5))]
        out.append((m.group(1), m.group(2), m.group(3), at, sz))
    return out

CANDS = [
    ("Diode_SMD", "D_SOD-323"),
    ("Package_SON", "Texas_DQX002A"),
    ("Package_SON", "Texas_DPY0002A_0.6x1mm_P0.65mm"),
    ("Diode_SMD", "Nexperia_DSN0603-2_0.6x0.3mm_P0.4mm"),
    ("Inductor_SMD", "L_0805_2012Metric"),
    ("Package_TO_SOT_SMD", "SOT-23"),
    ("TestPoint", "TestPoint_Pad_D1.0mm"),
    ("Button_Switch_SMD", "SW_Push_1P1T_NO_CK_KMR2"),
]
print("=== 候选封装 fab/courtyard/pad 实读 ===")
for lib, name in CANDS:
    p = os.path.join(LR, "%s.pretty" % lib, "%s.kicad_mod" % name)
    if not os.path.isfile(p):
        print("\n-- %s:%s  ⇒ **不在盘**" % (lib, name)); continue
    md5 = hashlib.md5(open(p, "rb").read()).hexdigest()
    fab = outline(p, "F.Fab"); cy = outline(p, "F.CrtYd")
    ps = pads_of(p)
    print("\n-- %s:%s" % (lib, name))
    print("   路径 = %s" % p)
    print("   md5  = %s" % md5)
    print("   pad 数 = %d (焊盘号 %s)" % (len(ps), [x[0] for x in ps]))
    print("   F.Fab   bbox = %s" % (("%.3f x %.3f mm" % fab) if fab else "n/a"))
    print("   F.CrtYd bbox = %s" % (("%.3f x %.3f mm" % cy) if cy else "n/a"))
    for num, pt, sh, at, sz in ps:
        print("      pad %-3s %-6s %-9s at=(%s) size=(%s)" % (num, pt, sh,
              ",".join("%.3f" % x for x in at), ",".join("%.3f" % x for x in sz)))

# ---- 13 件网表逐脚
print("\n\n=== 13 件网表逐脚 (netlist_v1_pins.csv) ===")
G13 = ["CHG_GND_STAR", "D_ESD_CAM", "D_ESD_DEMO", "D_ESD_USB_D", "FB_DEMO", "Q_AND",
       "Q_ENVC", "Q_PG", "SW_BOOT", "SW_KEY_PWR", "SW_KEY_VM", "SW_KEY_VP", "SW_RST"]
rows = list(csv.DictReader(open(os.path.join(ROOT, "HW", "netlist_v1_pins.csv"), encoding="utf-8")))
for r in G13:
    pr = [x for x in rows if x["ref"] == r]
    print("  %-14s (%d 脚): %s" % (r, len(pr),
          " · ".join("%s=%s" % (x["pin"], x["net"]) for x in pr)))

# ---- FP_TRUTH 命中复查 (修正正则: lib:name 允许 . - 等)
print("\n=== 13 件在 FP_TRUTH_BASELINE.md 里的 lib:name 命中 (修正正则) ===")
fp = open(os.path.join(ROOT, "HW", "FP_TRUTH_BASELINE.md"), encoding="utf-8").read()
LIBNAME = re.compile(r"`([A-Za-z0-9_\-\.]+:[A-Za-z0-9_\-\.\+]+)`")
for r in G13:
    found = set()
    for line in fp.splitlines():
        if re.search(r"\b%s\b" % re.escape(r), line):
            for h in LIBNAME.findall(line):
                found.add(h)
    print("  %-14s ⇒ %s" % (r, sorted(found) or "★无★"))

# ---- SW_KEY_CAM 在哪
print("\n=== SW_KEY_CAM / 其它按键归属 ===")
bom = {x["ref"]: x for x in csv.DictReader(open(os.path.join(ROOT, "HW", "BOM_v1.csv"), encoding="utf-8"))}
import json
recon = json.load(open(os.path.join(ROOT, "logs/iss361/04_recon.json")))
c4 = set(recon["c4"]); iss = set(recon["iss356"]); diff = set(recon["diff"])
for r in ["SW_KEY_CAM", "D_ESD_LIGHT", "SW_BOOT", "SW_RST", "SW_KEY_PWR", "SW_KEY_VM", "SW_KEY_VP"]:
    br = bom.get(r, {})
    where = "C4∩ISS356靶内" if (r in c4 and r in iss) else ("C4差集" if r in diff else ("不在C4" if r not in c4 else "?"))
    print("  %-12s dnp=%-4s type=%-4s ⇒ %s" % (r, br.get("dnp"), br.get("type"), where))
