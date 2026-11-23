#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-369 cont1 · 逐焊盘几何等价穷举 (★含 NPTH 焊盘★·只读)

★为什么重跑这一遍★: 上一趟的 tmp/iss369/tools/padeq_rot.py 用
  `(pad "N" TYPE SHAPE\\n\\s*\\(at ...` 正则取板面焊盘 ⇒ ★把【焊盘名为空 "" 的 NPTH 固定孔】
  漏掉★ (J_USB_C 实测: 文本里 18 个 (pad 块, 上一趟只数到 16) ⇒ 它的等效件搜索用错了焊盘数桶)
⇒ 本脚本改用【括号配平切块】取焊盘 ⇒ 一个都不漏。

判据 (与 tmp/iss369/tools/padeq_rot.py 同一组容差, 不另立):
  PAD_POS_TOL  = 0.05 mm   焊盘位置
  PAD_SIZE_TOL = 0.05 mm   焊盘尺寸
  CEN_TOL      = 0.10 mm   焊盘中心距
  允许旋转 0/90/180/270

产出: logs/iss369/21_padeq_allpads.json
"""
import hashlib
import json
import os
import re
from collections import defaultdict

ROOT = "/home/yuewuya/.openclaw/workspace/projects/smart_glasses"
LIBROOT = "/home/yuewuya/kicad/AppDir/share/kicad/footprints"
BOARD = os.path.join(ROOT, "HW", "PCB", "demo_mainboard.kicad_pcb")
OUT = os.path.join(ROOT, "logs", "iss369", "21_padeq_allpads.json")
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


def pad_geom(pb):
    at = re.search(r"\(at ([^)]*)\)", pb)
    a = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", at.group(1))] if at else [0.0, 0.0]
    sm = re.search(r"\(size ([-\d\.]+) ([-\d\.]+)\)", pb)
    w = float(sm.group(1)) if sm else 0.0
    h = float(sm.group(2)) if sm else 0.0
    nm = re.search(r'\(pad\s+"([^"]*)"', pb)
    ty = re.search(r'\(pad\s+"[^"]*"\s+(\S+)', pb)
    return {"num": nm.group(1) if nm else "", "x": a[0], "y": a[1],
            "w": w, "h": h, "type": ty.group(1) if ty else ""}


def fp_blocks(text):
    out = []
    for m in re.finditer(r"^\t\(footprint ", text, re.M):
        s = m.start()
        cands = [text.find("\n\t(footprint ", s + 1), text.find("\n\t(net ", s + 1)]
        cands = [c for c in cands if c != -1]
        e = min(cands) if cands else len(text)
        blk = text[s:e]
        rm = re.search(r'\(property "Reference" "([^"]*)"', blk)
        if rm:
            out.append((rm.group(1), blk))
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


def main():
    text = open(BOARD, encoding="utf-8").read()
    board = {}
    for ref, blk in fp_blocks(text):
        board[ref] = [pad_geom(pb) for pb in blocks(blk, "pad")]
    print("[padeq] 板面封装 %d 个 · 焊盘总数 %d"
          % (len(board), sum(len(v) for v in board.values())))

    buck = defaultdict(list)
    nlib = 0
    for lib in sorted(os.listdir(LIBROOT)):
        if not lib.endswith(".pretty"):
            continue
        lp = os.path.join(LIBROOT, lib)
        if not os.path.isdir(lp):
            continue
        for fn in sorted(os.listdir(lp)):
            if not fn.endswith(".kicad_mod"):
                continue
            t = open(os.path.join(lp, fn), encoding="utf-8").read()
            mp = [pad_geom(pb) for pb in blocks(t, "pad")]
            buck[len(mp)].append(("%s:%s" % (lib[:-len(".pretty")], fn[:-len(".kicad_mod")]), mp))
            nlib += 1
    print("[padeq] 官方库 .kicad_mod 扫描 %d 个" % nlib)

    hits = {}
    for ref, bp in board.items():
        got = []
        for k, mp in buck.get(len(bp), []):
            deg = eq(bp, mp)
            if deg is not None:
                got.append([k, deg])
        hits[ref] = got
    nz = {k: v for k, v in hits.items() if v}
    print("[padeq] ★逐焊盘几何等价 (含 NPTH·允许旋转) 的件 = %d / %d" % (len(nz), len(board)))
    for ref in sorted(nz):
        print("   %-14s %d 个候选: %s" % (ref, len(nz[ref]), nz[ref]))
    json.dump({"tolerances": {"pad_pos": PAD_POS_TOL, "pad_size": PAD_SIZE_TOL,
                               "center": CEN_TOL},
               "board_footprints": len(board),
               "board_pads_total": sum(len(v) for v in board.values()),
               "lib_mods_scanned": nlib,
               "n_equivalent": len(nz),
               "equivalent": nz,
               "none_equivalent": sorted(k for k, v in hits.items() if not v)},
              open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("-> %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
