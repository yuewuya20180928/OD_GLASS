#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 · 186 件【逐焊盘几何等价 · 允许旋转】穷举 (只读)

★判据 (写库名后铜箔零改动 ⇒ lib_id 可安全写入)★:
  E1 焊盘数相同
  E2 绕 footprint 原点旋转 0/90/180/270 后, 每个焊盘的 (x,y) 与 (w,h) 在容差内
  E3 焊盘中心距一致
容差: PAD_POS_TOL=0.05mm · PAD_SIZE_TOL=0.05mm · CEN_TOL=0.10mm
"""
import json
import os
import re
from collections import defaultdict

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
INV = json.load(open(os.path.join(ROOT, "tmp/iss369/board_inventory.json"),
                     encoding="utf-8"))["footprints"]
LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
PAD_POS_TOL = 0.05
PAD_SIZE_TOL = 0.05
CEN_TOL = 0.10


def blocks(text, name):
    out = []
    i = 0
    while True:
        m = re.search(r"\(%s\b" % re.escape(name), text[i:])
        if not m:
            break
        s = i + m.start()
        depth = 0
        j = s
        while j < len(text):
            if text[j] == "(":
                depth += 1
            elif text[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append(text[s:j + 1])
        i = j + 1
    return out


def mod_pads(path):
    t = open(path, encoding="utf-8").read()
    out = []
    for pb in blocks(t, "pad"):
        at = re.search(r"\(at ([^)]*)\)", pb)
        a = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", at.group(1))] if at else [0, 0]
        sm = re.search(r"\(size ([-\d\.]+) ([-\d\.]+)\)", pb)
        nm = re.search(r'pad "([^"]*)"', pb)
        rot = re.search(r'\(at ([-\d\.]+) ([-\d\.]+) ([-\d\.]+)\)', pb)
        out.append({"x": a[0], "y": a[1], "rot": float(rot.group(3)) if rot else 0.0,
                    "w": float(sm.group(1)) if sm else 0.0,
                    "h": float(sm.group(2)) if sm else 0.0,
                    "num": nm.group(1) if nm else ""})
    return out


def rot(p, deg):
    x, y = p["x"], p["y"]
    if deg == 0:
        return x, y, p["w"], p["h"]
    if deg == 90:
        return -y, x, p["h"], p["w"]
    if deg == 180:
        return -x, -y, p["w"], p["h"]
    return y, -x, p["h"], p["w"]


def key(p):
    d = "".join(ch for ch in p["num"] if ch.isdigit())
    return (0, int(d), p["num"]) if d else (1, 0, p["num"])


def maxdist(ps):
    d = 0.0
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            d = max(d, ((ps[i][0] - ps[j][0]) ** 2 + (ps[i][1] - ps[j][1]) ** 2) ** 0.5)
    return d


def eq(board_pads, mod):
    if len(board_pads) != len(mod):
        return None
    bp = sorted(board_pads, key=key)
    for deg in (0, 90, 180, 270):
        mp = sorted([{"num": p["num"], "x": rot(p, deg)[0], "y": rot(p, deg)[1],
                      "w": rot(p, deg)[2], "h": rot(p, deg)[3]} for p in mod], key=key)
        ok = True
        for a, b in zip(bp, mp):
            if abs(a["x"] - b["x"]) > PAD_POS_TOL or abs(a["y"] - b["y"]) > PAD_POS_TOL:
                ok = False
                break
            if abs(a["w"] - b["w"]) > PAD_SIZE_TOL or abs(a["h"] - b["h"]) > PAD_SIZE_TOL:
                ok = False
                break
        if not ok:
            continue
        bpts = [(p["x"], p["y"]) for p in bp]
        mpts = [(p["x"], p["y"]) for p in mp]
        if abs(maxdist(bpts) - maxdist(mpts)) > CEN_TOL:
            continue
        return deg
    return None


buck = defaultdict(list)
for lib in sorted(os.listdir(LIBROOT)):
    if not lib.endswith(".pretty"):
        continue
    lp = os.path.join(LIBROOT, lib)
    for fn in sorted(os.listdir(lp)):
        if not fn.endswith(".kicad_mod"):
            continue
        try:
            mp = mod_pads(os.path.join(lp, fn))
        except Exception:
            continue
        buck[len(mp)].append(("%s:%s" % (lib[:-7], fn[:-10]), mp))

hits = {}
for f in INV:
    got = []
    for key_, mp in buck.get(f["pad_count"], []):
        deg = eq(f["pads"], mp)
        if deg is not None:
            got.append((key_, deg))
    hits[f["ref"]] = got

nz = {k: v for k, v in hits.items() if v}
print("=== 逐焊盘几何等价 (允许旋转) 的件: %d/%d ===" % (len(nz), len(INV)))
for ref in sorted(nz, key=lambda r: -len(nz[r])):
    print("  %-18s %d 个候选: %s" % (ref, len(nz[ref]), nz[ref][:8]))
json.dump({k: v for k, v in hits.items()},
          open(os.path.join(ROOT, "tmp/iss369/padeq186_rot.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("-> tmp/iss369/padeq186_rot.json")
