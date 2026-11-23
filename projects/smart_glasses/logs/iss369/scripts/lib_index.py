#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 · 本机 KiCad 官方库全量几何索引 (只读, 建索引)
产出 tmp/iss369/lib_index.json: 每个 .kicad_mod 的
  lib, name, path, md5, pads_n, fab_w, fab_h, center, pad_sizes(list), courtyard(有/无)
"""
import hashlib
import json
import os
import re
import sys

LIBROOT = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
OUT = sys.argv[2] if len(sys.argv) > 2 else "tmp/iss369/lib_index.json"


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


def parse(p):
    text = open(p, encoding="utf-8").read()
    pads = []
    for pb in blocks(text, "pad"):
        at = re.search(r"\(at ([^)]*)\)", pb)
        a = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", at.group(1))] if at else [0, 0]
        sm = re.search(r"\(size ([-\d\.]+) ([-\d\.]+)\)", pb)
        sw = float(sm.group(1)) if sm else 0.0
        sh = float(sm.group(2)) if sm else 0.0
        ty = re.search(r'\(pad "([^"]*)" (\S+)', pb)
        pads.append({"x": a[0], "y": a[1], "w": sw, "h": sh,
                     "type": ty.group(2) if ty else ""})
    d = 0.0
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            d = max(d, ((pads[i]["x"] - pads[j]["x"]) ** 2
                        + (pads[i]["y"] - pads[j]["y"]) ** 2) ** 0.5)
    xs, ys = [], []
    for tag in ("fp_line", "fp_rect"):
        for b in blocks(text, tag):
            lm = re.search(r'\(layer "([^"]*)"\)', b)
            if not lm or lm.group(1) != "F.Fab":
                continue
            for grp in ("start", "end"):
                m = re.search(r"\(%s ([-\d\.]+) ([-\d\.]+)\)" % grp, b)
                if m:
                    xs.append(float(m.group(1)))
                    ys.append(float(m.group(2)))
    fab_w = round(max(xs) - min(xs), 3) if xs else 0.0
    fab_h = round(max(ys) - min(ys), 3) if ys else 0.0
    return {"pads_n": len(pads),
            "fab_w": fab_w, "fab_h": fab_h,
            "center": round(d, 3),
            "pad_sizes": sorted({"%.3fx%.3f" % (q["w"], q["h"]) for q in pads}),
            "pad_types": sorted({q["type"] for q in pads}),
            "has_courtyard": any(".CrtYd" in b for b in blocks(text, "fp_line"))
            or any(".CrtYd" in b for b in blocks(text, "fp_rect"))}


idx = {}
n = 0
for lib in sorted(os.listdir(LIBROOT)):
    if not lib.endswith(".pretty"):
        continue
    lp = os.path.join(LIBROOT, lib)
    if not os.path.isdir(lp):
        continue
    for fn in sorted(os.listdir(lp)):
        if not fn.endswith(".kicad_mod"):
            continue
        p = os.path.join(lp, fn)
        name = fn[:-len(".kicad_mod")]
        key = "%s:%s" % (lib[:-len(".pretty")], name)
        d = parse(p)
        d["md5"] = hashlib.md5(open(p, "rb").read()).hexdigest()
        d["path"] = "%s/%s" % (lib, fn)
        idx[key] = d
        n += 1

json.dump({"libroot": LIBROOT, "count": n, "mods": idx},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("indexed %d .kicad_mod -> %s" % (n, OUT))
