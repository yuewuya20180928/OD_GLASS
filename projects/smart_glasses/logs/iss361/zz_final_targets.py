#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-361 侦察 9: 13 件目标封装候选的最终实存核验 (md5 + 焊盘数 + fab/courtyd)"""
import os, re, hashlib

LR = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"

CHOSEN = [
    ("CHG_GND_STAR", "TestPoint", "TestPoint_Pad_D1.0mm", 1),
    ("D_ESD_CAM",    "Package_SON", "Texas_DPY0002A_0.6x1mm_P0.65mm", 2),
    ("D_ESD_DEMO",   "Diode_SMD", "D_SOD-323", 2),
    ("FB_DEMO",      "Inductor_SMD", "L_0805_2012Metric", 2),
    ("Q_AND",        "Package_TO_SOT_SMD", "SOT-23", 3),
    ("Q_ENVC",       "Package_TO_SOT_SMD", "SOT-23", 3),
    ("Q_PG",         "Package_TO_SOT_SMD", "SOT-23", 3),
    ("SW_BOOT",      "Button_Switch_SMD", "SW_Push_1P1T_NO_CK_KMR2", 4),
    ("SW_KEY_PWR",   "Button_Switch_SMD", "SW_Push_1P1T_NO_CK_KMR2", 4),
    ("SW_KEY_VM",    "Button_Switch_SMD", "SW_SPST_B3U-1000P", 2),
    ("SW_KEY_VP",    "Button_Switch_SMD", "SW_SPST_B3U-1000P", 2),
    ("SW_RST",       "Button_Switch_SMD", "SW_Push_1P1T_NO_CK_KMR2", 4),
]
ALT = [
    ("Button_Switch_SMD", "SW_SPST_CK_KXT3"),
    ("Button_Switch_SMD", "SW_SPST_CK_KMS2xxG"),
    ("Button_Switch_SMD", "SW_SPST_EVQP0"),
    ("Button_Switch_SMD", "SW_SPST_TL3342"),
    ("Package_TO_SOT_SMD", "SOT-23-3"),
]


def blocks(t, name):
    out = []
    i = 0
    while True:
        m = re.search(r"\(%s\b" % re.escape(name), t[i:])
        if not m:
            break
        s = i + m.start()
        d = 0
        j = s
        while j < len(t):
            if t[j] == "(":
                d += 1
            elif t[j] == ")":
                d -= 1
                if d == 0:
                    break
            j += 1
        out.append(t[s:j + 1])
        i = j + 1
    return out


def layer_bbox(blk, layer):
    xs, ys = [], []
    for tag in ("fp_line", "fp_rect"):
        for b in blocks(blk, tag):
            lm = re.search(r'\(layer "([^"]*)"\)', b)
            if not lm or lm.group(1) != layer:
                continue
            for g in ("start", "end"):
                m = re.search(r"\(%s ([-\d\.]+) ([-\d\.]+)\)" % g, b)
                if m:
                    xs.append(float(m.group(1))); ys.append(float(m.group(2)))
    return (max(xs) - min(xs), max(ys) - min(ys)) if xs else None


def report(lib, name):
    p = os.path.join(LR, "%s.pretty" % lib, "%s.kicad_mod" % name)
    if not os.path.isfile(p):
        print("   ★不在盘★ %s:%s" % (lib, name)); return
    t = open(p, encoding="utf-8").read()
    md5 = hashlib.md5(open(p, "rb").read()).hexdigest()
    pads = []
    for b in blocks(t, "pad"):
        num = re.search(r'pad\s+"([^"]*)"', b).group(1)
        at = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", re.search(r"\(at ([^)]*)\)", b).group(1))]
        sz = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", re.search(r"\(size ([^)]*)\)", b).group(1))]
        pads.append((num, at, sz))
    descr = re.search(r'descr "([^"]*)"', t)
    print("   %s:%s" % (lib, name))
    print("      path = %s.pretty/%s.kicad_mod" % (lib, name))
    print("      md5  = %s" % md5)
    print("      pads = %d  焊盘号=%s" % (len(pads), [x[0] for x in pads]))
    print("      F.Fab = %s · F.CrtYd = %s"
          % (("%.3f x %.3f" % layer_bbox(t, "F.Fab")) if layer_bbox(t, "F.Fab") else "n/a",
             ("%.3f x %.3f" % layer_bbox(t, "F.CrtYd")) if layer_bbox(t, "F.CrtYd") else "n/a"))
    if descr:
        print("      descr = %s" % descr.group(1)[:130])
    for n, a, s in pads:
        print("         pad %-3s at=(%s) size=(%s)" % (n, ",".join("%.3f" % x for x in a), ",".join("%.3f" % x for x in s)))


print("=== 13 件目标封装候选 (逐件实存核验) ===")
for ref, lib, name, npad in CHOSEN:
    print("\n-- %s  (期望焊盘数 %d)" % (ref, npad))
    report(lib, name)

print("\n\n=== 备选封装 (降级方案用) ===")
for lib, name in ALT:
    print()
    report(lib, name)
