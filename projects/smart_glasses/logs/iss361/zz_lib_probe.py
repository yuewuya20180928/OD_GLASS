#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-361 侦察 3: KiCad 官方库候选封装的 pad/尺寸实读 (只读)"""
import os, re, hashlib

LR = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"

CANDS = [
    ("Diode_SMD", "D_SOD-323"),
    ("Diode_SMD", "D_SOD-523"),
    ("Diode_SMD", "D_SOD-882"),
    ("Diode_SMD", "D_SOD-923"),
    ("Inductor_SMD", "L_0805_2012Metric"),
    ("Package_TO_SOT_SMD", "SOT-23"),
    ("TestPoint", "TestPoint_Pad_D1.0mm"),
    ("Button_Switch_SMD", "SW_Push_1P1T_NO_CK_KMR2"),
    ("Button_Switch_SMD", "SW_Push_1P1T-SH_NO_CK_KMR2xxG"),
    ("Button_Switch_SMD", "SW_SPST_CK_KMS2xxG"),
    ("Button_Switch_SMD", "SW_SPST_EVQP0"),
    ("Button_Switch_SMD", "SW_SPST_TL3342"),
]

def summarize(path):
    txt = open(path, encoding="utf-8").read()
    pads = []
    for m in re.finditer(r'\(pad\s+"([^"]*)"\s+(\w+)\s+(\w+)\s*\(at ([^)]*)\)\s*\(size ([^)]*)\)(?:[^()]|\([^()]*\))*', txt):
        num, ptype, shape, at, size = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        def nums(s):
            return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", s)]
        a = nums(at); s = nums(size)
        pads.append((num, ptype, shape, a, s))
    # fab bbox
    fab = []
    for m in re.finditer(r'\(fp_line\s*\(start ([^)]*)\)\s*\(end ([^)]*)\)', txt):
        for grp in (1, 2):
            pass
    # crude: fab layer lines
    for m in re.finditer(r'\(fp_line\s*\(start ([-\d\. ]+)\)\s*\(end ([-\d\. ]+)\)\s*\(layer "F\.Fab"\)', txt):
        p1 = [float(x) for x in m.group(1).split()]
        p2 = [float(x) for x in m.group(2).split()]
        fab.append((p1, p2))
    xs, ys = [], []
    for p1, p2 in fab:
        for p in (p1, p2):
            xs.append(p[0]); ys.append(p[1])
    fbb = (max(xs)-min(xs), max(ys)-min(ys)) if xs else (0, 0)
    # courtyard
    cy = []
    for m in re.finditer(r'\(fp_line\s*\(start ([-\d\. ]+)\)\s*\(end ([-\d\. ]+)\)\s*\(layer "F\.CrtYd"\)', txt):
        p1 = [float(x) for x in m.group(1).split()]
        p2 = [float(x) for x in m.group(2).split()]
        cy.append((p1, p2))
    cxs, cys = [], []
    for p1, p2 in cy:
        for p in (p1, p2):
            cxs.append(p[0]); cys.append(p[1])
    cbb = (max(cxs)-min(cxs), max(cys)-min(cys)) if cxs else (0, 0)
    return pads, fbb, cbb

print("=== KiCad 官方库候选封装实读 (库根 %s) ===" % LR)
for lib, name in CANDS:
    p = os.path.join(LR, "%s.pretty" % lib, "%s.kicad_mod" % name)
    if not os.path.isfile(p):
        print("\n-- %s:%s  ⇒ **不在盘**" % (lib, name))
        continue
    md5 = hashlib.md5(open(p, "rb").read()).hexdigest()
    pads, fbb, cbb = summarize(p)
    print("\n-- %s:%s" % (lib, name))
    print("   路径 = %s" % p)
    print("   md5  = %s" % md5)
    print("   pad 数 = %d · F.Fab bbox = %.3f x %.3f mm · F.CrtYd bbox = %.3f x %.3f mm"
          % (len(pads), fbb[0], fbb[1], cbb[0], cbb[1]))
    for num, ptype, shape, at, s in pads:
        print("      pad %-3s %-6s %-9s at=(%s) size=(%s)" % (num, ptype, shape,
              ",".join("%.3f" % x for x in at), ",".join("%.3f" % x for x in s)))
    # 焊盘中心距
    if len(pads) >= 2:
        c = [(sum(a[0::2])/len(a[0::2]), sum(a[1::2])/len(a[1::2])) for _,_,_,a,_ in pads]
        print("      焊盘中心 = %s" % ["(%.3f,%.3f)" % x for x in c])

# 顺便: 板面 13 件的占位 bbox / pad 间距对照 (硬编自板面实测)
print("\n=== 板面占位几何 (实测自 demo_mainboard.kicad_pcb) ===")
BOARD = {
    "CHG_GND_STAR": (1, [(99.200, 63.500)], 0.600, 0.900),
    "D_ESD_CAM":    (2, [(83.700, 56.600), (86.000, 56.600)], 0.600, 0.900),
    "D_ESD_DEMO":   (2, [(98.300, 9.600), (100.600, 9.600)], 0.600, 0.900),
    "D_ESD_USB_D":  (2, [(94.500, 21.600), (96.800, 21.600)], 0.600, 0.900),
    "FB_DEMO":      (2, [(93.000, 9.500), (93.800, 10.100)], 0.550, 0.900),
    "Q_AND":        (3, [(106.200, 63.500), (107.470, 63.500), (109.000, 67.500)], 0.600, 0.900),
    "Q_ENVC":       (3, [(113.200, 63.500), (114.470, 63.500), (116.000, 67.500)], 0.600, 0.900),
    "Q_PG":         (3, [(83.400, 27.500), (84.670, 27.500), (86.200, 31.500)], 0.600, 0.900),
    "SW_BOOT":      (2, [(115.800, 9.600), (118.000, 9.600)], 0.600, 0.900),
    "SW_KEY_PWR":   (2, [(78.900, 21.600), (81.100, 21.600)], 0.600, 0.900),
    "SW_KEY_VM":    (2, [(35.900, 62.600), (38.100, 62.600)], 0.600, 0.900),
    "SW_KEY_VP":    (2, [(65.900, 62.600), (68.100, 62.600)], 0.600, 0.900),
    "SW_RST":       (2, [(118.200, 56.600), (120.400, 56.600)], 0.600, 0.900),
}
for r, (n, pts, pw, ph) in BOARD.items():
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    print("  %-14s %d pad · pad %.3f x %.3f mm · pad 组 bbox %.3f x %.3f mm"
          % (r, n, pw, ph, max(xs)-min(xs)+pw, max(ys)-min(ys)+ph))
