#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-361 侦察 5: 精确量测候选封装 (fab/courtyard/pad 角色) + 13 件口径公式自校验"""
import os, re, csv, json, hashlib

LR = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"


def blocks(txt, name):
    """取 (name ...) 的 s-expr 内容 (括号配平)"""
    out = []
    i = 0
    while True:
        m = re.search(r"\(%s\b" % re.escape(name), txt[i:])
        if not m:
            break
        s = i + m.start()
        depth = 0
        j = s
        while j < len(txt):
            if txt[j] == "(":
                depth += 1
            elif txt[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append(txt[s:j+1])
        i = j + 1
    return out


def layer_of(blk):
    m = re.search(r'\(layer\s+"([^"]+)"\)', blk)
    return m.group(1) if m else None


def measure(path):
    txt = open(path, encoding="utf-8").read()
    res = {}
    for layer in ("F.Fab", "F.CrtYd"):
        xs, ys = [], []
        for blk in blocks(txt, "fp_line") + blocks(txt, "fp_rect"):
            if layer_of(blk) != layer:
                continue
            for tag in ("start", "end"):
                m = re.search(r"\(%s ([-\d\.]+) ([-\d\.]+)\)" % tag, blk)
                if m:
                    xs.append(float(m.group(1))); ys.append(float(m.group(2)))
        res[layer] = (max(xs)-min(xs), max(ys)-min(ys)) if xs else None
    pads = []
    for blk in blocks(txt, "pad"):
        num = re.search(r'pad\s+"([^"]*)"', blk).group(1)
        at = re.search(r"\(at ([^)]*)\)", blk).group(1)
        sz = re.search(r"\(size ([^)]*)\)", blk).group(1)
        A = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", at)]
        S = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", sz)]
        pads.append((num, A, S))
    # fp_text user (脚角色标注, 如 "K" "A")
    users = []
    for blk in blocks(txt, "fp_text"):
        if '"user"' in blk:
            m = re.search(r'fp_text user\s+"([^"]*)"', blk)
            if m:
                users.append(m.group(1))
    # desc / tags
    desc = ""
    m = re.search(r'desc\s+"([^"]*)"', txt)
    if m:
        desc = m.group(1)
    return res, pads, users, desc


CANDS = [
    ("Diode_SMD", "D_SOD-323"),
    ("Diode_SMD", "D_SOD-523"),
    ("Diode_SMD", "Nexperia_DSN0603-2_0.6x0.3mm_P0.4mm"),
    ("Package_SON", "Texas_DQX002A"),
    ("Package_SON", "Texas_DPY0002A_0.6x1mm_P0.65mm"),
    ("Inductor_SMD", "L_0805_2012Metric"),
    ("Package_TO_SOT_SMD", "SOT-23"),
    ("TestPoint", "TestPoint_Pad_D1.0mm"),
    ("Button_Switch_SMD", "SW_Push_1P1T_NO_CK_KMR2"),
    ("Diode_SMD", "D_SOT-23"),
    ("Diode_SMD", "D_SOD-123"),
]
print("=== 候选封装精确量测 ===")
for lib, name in CANDS:
    p = os.path.join(LR, "%s.pretty" % lib, "%s.kicad_mod" % name)
    if not os.path.isfile(p):
        print("\n-- %s:%s ⇒ 不在盘" % (lib, name)); continue
    md5 = hashlib.md5(open(p, "rb").read()).hexdigest()
    res, pads, users, desc = measure(p)
    print("\n-- %s:%s" % (lib, name))
    print("   md5 = %s" % md5)
    print("   desc = %s" % desc)
    print("   F.Fab   = %s" % (("%.3f x %.3f" % res["F.Fab"]) if res["F.Fab"] else "n/a"))
    print("   F.CrtYd = %s" % (("%.3f x %.3f" % res["F.CrtYd"]) if res["F.CrtYd"] else "n/a"))
    print("   pads = %d · 焊盘号 %s · user 标注 %s"
          % (len(pads), [x[0] for x in pads], users))
    xs = [x[1][0] for x in pads]; ys = [x[1][1] for x in pads]
    sw = max(x[2][0] for x in pads); sh = max(x[2][1] for x in pads)
    print("   pad 组 bbox(含焊盘尺寸) = %.3f x %.3f mm" % (
        max(xs)-min(xs)+sw, max(ys)-min(ys)+sh))
    for num, A, S in pads:
        print("      pad %-3s at=(%s) size=(%s)" % (num,
              ",".join("%.3f" % x for x in A), ",".join("%.3f" % x for x in S)))

# ---------- 13 件口径公式自校验 ----------
print("\n\n=== 13 件口径公式自校验 (从 BOM 实算) ===")
recon = json.load(open(os.path.join(ROOT, "logs/iss361/04_recon.json")))
c4 = set(recon["c4"])
bom = list(csv.DictReader(open(os.path.join(ROOT, "HW", "BOM_v1.csv"), encoding="utf-8")))
calc = []
for r in bom:
    if r["dnp"] != "必装":
        continue
    if r["type"] in ("NET", "TP"):
        continue
    if r["footprint"] == "待定":
        continue
    if r["ref"] not in c4:
        continue
    calc.append(r["ref"])
calc.sort()
print("  公式「必装 ∩ 非NET/TP ∩ footprint!='待定' ∩ 在C4」⇒ %d 件" % len(calc))
print("  名单 = %s" % calc)
print("  与 recon.gap 一致? %s" % (calc == sorted(recon["gap"])))

# 再看: 必装 ∩ 非NET/TP ∩ footprint!='待定' 但【不在 C4】的 (不在本单 13 件口径内)
out = [r["ref"] for r in bom
       if r["dnp"] == "必装" and r["type"] not in ("NET", "TP")
       and r["footprint"] != "待定" and r["ref"] not in c4]
print("  同口径但【不在 C4-158】的 (另 %d 件): %s" % (len(out), sorted(out)))
