#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 · 186 件【逐焊盘几何等价】穷举 (只读)

★判据 (写盘后铜箔零改动 ⇒ lib_id 可安全写入)★:
  E1 焊盘数相同
  E2 每个焊盘的 (相对位置 x,y) 与 (尺寸 w,h) 都在容差内
  E3 焊盘中心距一致
  ⇒ 只比【铜箔事实】, 不比 F.Fab 外框 (F.Fab 是装配图, 不参与贴片)
容差: PAD_POS_TOL=0.05mm · PAD_SIZE_TOL=0.05mm · CEN_TOL=0.10mm
"""
import json
import os
from collections import defaultdict

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
INV = json.load(open(os.path.join(ROOT, "tmp/iss369/board_inventory.json"),
                     encoding="utf-8"))["footprints"]
LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"

PAD_POS_TOL = 0.05
PAD_SIZE_TOL = 0.05
CEN_TOL = 0.10

import re


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
        out.append({"x": a[0], "y": a[1],
                    "w": float(sm.group(1)) if sm else 0.0,
                    "h": float(sm.group(2)) if sm else 0.0,
                    "num": nm.group(1) if nm else ""})
    return out


def eq(board_pads, mod):
    if len(board_pads) != len(mod):
        return None
    # 按焊盘号对齐 (数字优先, 否则按序)
    def key(p):
        d = "".join(ch for ch in p["num"] if ch.isdigit())
        return (0, int(d), p["num"]) if d else (1, 0, p["num"])
    bp = sorted(board_pads, key=key)
    mp = sorted(mod, key=key)
    for a, b in zip(bp, mp):
        if abs(a["x"] - b["x"]) > PAD_POS_TOL or abs(a["y"] - b["y"]) > PAD_POS_TOL:
            return None
        if abs(a["w"] - b["w"]) > PAD_SIZE_TOL or abs(a["h"] - b["h"]) > PAD_SIZE_TOL:
            return None
    d = 0.0
    for i in range(len(bp)):
        for j in range(i + 1, len(bp)):
            d = max(d, ((bp[i]["x"] - bp[j]["x"]) ** 2
                        + (bp[i]["y"] - bp[j]["y"]) ** 2) ** 0.5)
    md = 0.0
    for i in range(len(mp)):
        for j in range(i + 1, len(mp)):
            md = max(md, ((mp[i]["x"] - mp[j]["x"]) ** 2
                          + (mp[i]["y"] - mp[j]["y"]) ** 2) ** 0.5)
    if abs(d - md) > CEN_TOL:
        return None
    return True


# 索引库里所有 .kicad_mod 的 pad 集 (按 pad 数分桶)
buck = defaultdict(list)
for lib in sorted(os.listdir(LIBROOT)):
    if not lib.endswith(".pretty"):
        continue
    lp = os.path.join(LIBROOT, lib)
    for fn in sorted(os.listdir(lp)):
        if not fn.endswith(".kicad_mod"):
            continue
        p = os.path.join(lp, fn)
        try:
            mp = mod_pads(p)
        except Exception:
            continue
        buck[len(mp)].append(("%s:%s" % (lib[:-7], fn[:-10]), mp))

print("库按 pad 数分桶: %s" % {k: len(v) for k, v in sorted(buck.items())})

hits = {}
for f in INV:
    n = f["pad_count"]
    got = []
    for key, mp in buck.get(n, []):
        if eq(f["pads"], mp):
            got.append(key)
    hits[f["ref"]] = got

nz = {k: v for k, v in hits.items() if v}
print()
print("=== 逐焊盘几何等价的件 (%d/%d) ===" % (len(nz), len(INV)))
for ref in sorted(nz, key=lambda r: -len(nz[r])):
    print("  %-18s (%d 个候选) %s" % (ref, len(nz[ref]), nz[ref][:6]))

json.dump(hits, open(os.path.join(ROOT, "tmp/iss369/padeq186.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("-> tmp/iss369/padeq186.json")
