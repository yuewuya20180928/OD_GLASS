#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ISS-367 · `LED_G_D` 网两端 (换 land 前后) 实算 · 只读"""
import os, sys, json, math, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(PROJ, "MECH"))
spec = importlib.util.spec_from_file_location("G", os.path.join(PROJ, "MECH", "check_onepass_s10_led_spec_sync.py"))
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
root = PROJ
cfc = G.load_cfc(root); fp_gate = G.load_fp_gate(root)
board = cfc.read_board(root); comp = cfc.compute(root)
rots = G.board_footprint_rots(root); tmap = G.target_map(root, fp_gate)
patched, used = G.swap_set(board, G.S10_MECH_REFS, tmap, rots)

def ends(bd, tag):
    out = {}
    for ref in ("R_LED_G", "D_LED_G"):
        fp = bd["fps"][ref]
        pads = fp.get("pads") or []
        ps = []
        for p in pads:
            ps.append((p.get("num"), round(p.get("x"), 6), round(p.get("y"), 6)))
        ps.sort()
        out[ref] = {"at": [round(fp["at"][0], 6), round(fp["at"][1], 6)], "pads": ps}
    a = out["R_LED_G"]["pads"][-1]      # R_LED_G.2
    b = out["D_LED_G"]["pads"][0]       # D_LED_G.1
    dx = b[1] - a[1]; dy = b[2] - a[2]
    ln = math.hypot(dx, dy)
    out["net"] = {"r2": [a[1], a[2]], "d1": [b[1], b[2]], "dx": round(dx, 6),
                  "dy": round(dy, 6), "len": round(ln, 6)}
    out["tag"] = tag
    return out

r = {"before": ends(board, "BEFORE"), "after": ends(patched, "AFTER")}
r["after"]["net"]["delta_len"] = round(r["after"]["net"]["len"] - r["before"]["net"]["len"], 6)
print(json.dumps(r, ensure_ascii=False, indent=1))
